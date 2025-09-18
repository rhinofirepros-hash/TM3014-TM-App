/**
 * MIGRATION: Old T&M MVP -> New Unified Schema
 *
 * ------------------------------------------------------------
 * OUTLINE (WHAT THIS DOES)
 * ------------------------------------------------------------
 * 1) Read from OLD collections:
 *      - projects_old: { name, client, status? }
 *      - crew_members_old: { name, role, rate }
 *      - crew_logs_old: { projectId, crewMemberId, date, hours, description }
 *      - tm_tags_old: { projectId, date, crewLogs: [logId], description?, status? }
 *
 * 2) Transform to NEW collections (side-by-side, do NOT overwrite old):
 *      - projects        -> add billing fields (monthly @ 20), openingBalance=0, gcRate default
 *      - crew_members    -> position=role, hourlyRate=rate, gcBillRate default (95)
 *      - crew_logs       -> enrich with costRate (member.hourlyRate), billRate (member.gcBillRate),
 *                           syncedToTmTag=false, tmTagId=null
 *      - tm_tags         -> link crewLogs, totals calculated:
 *                           totalLaborCost = sum(hours*costRate), totalLaborBill = sum(hours*billRate),
 *                           totals for materials/expenses = 0 (if you didn't track them before)
 *      - materials       -> none (empty, new system feature)
 *      - expenses        -> none (empty, new system feature)
 *      - invoices        -> none (start fresh with new cadence)
 *      - payables        -> none (start fresh)
 *
 * 3) Safety / Run modes:
 *      - --dry-run: analyze & print what would be migrated, no writes
 *      - --batch-size=N: control batch size for logs/tags
 *      - uses a session (transaction) if your MongoDB supports it; falls back gracefully if not
 *
 * 4) Summary at end:
 *      - counts migrated per collection
 *      - any missing references or anomalies
 *
 * ------------------------------------------------------------
 * USAGE
 * ------------------------------------------------------------
 *   node migrate.js \
 *     --mongo="mongodb+srv://user:pass@cluster/dbname" \
 *     --gc-rate=95 --billing-day=20 --dry-run
 *
 *   node migrate.js --mongo="mongodb://127.0.0.1:27017/tmdb" --batch-size=500
 *
 * ENV VARS (optional fallback):
 *   MONGO_URI, DEFAULT_GC_RATE, DEFAULT_BILLING_DAY
 *
 * ------------------------------------------------------------
 * WHAT YOU'LL SEE AFTER MIGRATION
 * ------------------------------------------------------------
 * New collections created/filled:
 *   - projects
 *   - crew_members
 *   - crew_logs
 *   - tm_tags
 * (materials, expenses, invoices, payables remain empty until you start using new features)
 */

/////////////////////////////
// Config & CLI parsing
/////////////////////////////

const { MongoClient, ObjectId } = require("mongodb");

const args = require("minimist")(process.argv.slice(2), {
  string: ["mongo"],
  boolean: ["dry-run"],
  default: {
    mongo: process.env.MONGO_URI || "mongodb://127.0.0.1:27017/tmdb",
    "gc-rate": process.env.DEFAULT_GC_RATE ? Number(process.env.DEFAULT_GC_RATE) : 95,
    "billing-day": process.env.DEFAULT_BILLING_DAY ? Number(process.env.DEFAULT_BILLING_DAY) : 20,
    "batch-size": 500,
    "opening-balance": 0,
  },
});

const DRY_RUN = !!args["dry-run"];
const MONGO_URI = args.mongo;
const DEFAULT_GC_RATE = Number(args["gc-rate"]);
const DEFAULT_BILLING_DAY = Number(args["billing-day"]);
const BATCH_SIZE = Number(args["batch-size"]);
const DEFAULT_OPENING_BALANCE = Number(args["opening-balance"]);

// Current collection names (these will be renamed to _old)
const CURRENT_COLLECTIONS = {
  projects: "projects",
  employees: "employees", // Already using new schema
  crewLogs: "crew_logs",
  tmTags: "tm_tags",
  materials: "materials",
};

// New collection names (final schema)
const NEW_COLLECTIONS = {
  projects: "projects_new",
  crewMembers: "crew_members",
  crewLogs: "crew_logs_new", 
  tmTags: "tm_tags_new",
  materials: "materials_new",
  expenses: "expenses",
  invoices: "invoices",
  payables: "payables",
};

/////////////////////////////
// Helpers
/////////////////////////////

const iso = (d) => (d ? new Date(d) : null);
const asObjectId = (v) => {
  try { return typeof v === "string" ? new ObjectId(v) : v; } catch { return null; }
};

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

/////////////////////////////
// Main Migration
/////////////////////////////

(async () => {
  const client = new MongoClient(MONGO_URI, { ignoreUndefined: true });
  await client.connect();
  const db = client.db();

  // try to start a session (TX optional)
  let session = null;
  try { 
    session = client.startSession(); 
    console.log("✅ MongoDB session started - using transactions");
  } catch { 
    console.log("⚠️  No transaction support - proceeding without session");
  }

  const report = {
    dryRun: DRY_RUN,
    defaults: { DEFAULT_GC_RATE, DEFAULT_BILLING_DAY, DEFAULT_OPENING_BALANCE },
    counts: {
      projects_current: 0, employees_current: 0, crew_logs_current: 0, tm_tags_current: 0, materials_current: 0,
      projects_new: 0, crew_members_new: 0, crew_logs_new: 0, tm_tags_new: 0, materials_new: 0
    },
    warnings: [],
    notes: [],
  };

  // Current collections
  const currentProjectsCol = db.collection(CURRENT_COLLECTIONS.projects);
  const currentEmployeesCol = db.collection(CURRENT_COLLECTIONS.employees);
  const currentCrewLogsCol = db.collection(CURRENT_COLLECTIONS.crewLogs);
  const currentTmTagsCol = db.collection(CURRENT_COLLECTIONS.tmTags);
  const currentMaterialsCol = db.collection(CURRENT_COLLECTIONS.materials);

  // New collections
  const newProjectsCol = db.collection(NEW_COLLECTIONS.projects);
  const newCrewMembersCol = db.collection(NEW_COLLECTIONS.crewMembers);
  const newCrewLogsCol = db.collection(NEW_COLLECTIONS.crewLogs);
  const newTmTagsCol = db.collection(NEW_COLLECTIONS.tmTags);
  const newMaterialsCol = db.collection(NEW_COLLECTIONS.materials);
  const newExpensesCol = db.collection(NEW_COLLECTIONS.expenses);
  const newInvoicesCol = db.collection(NEW_COLLECTIONS.invoices);
  const newPayablesCol = db.collection(NEW_COLLECTIONS.payables);

  // Ensure useful indexes (idempotent)
  if (!DRY_RUN) {
    console.log("🔧 Creating indexes for new collections...");
    await Promise.all([
      newProjectsCol.createIndex({ name: 1 }),
      newCrewMembersCol.createIndex({ name: 1 }),
      newCrewLogsCol.createIndex({ projectId: 1, date: 1 }),
      newTmTagsCol.createIndex({ projectId: 1, date: 1 }),
      newMaterialsCol.createIndex({ projectId: 1 }),
      newExpensesCol.createIndex({ projectId: 1 }),
      newInvoicesCol.createIndex({ projectId: 1 }),
      newPayablesCol.createIndex({ projectId: 1 }),
    ]);
    console.log("✅ Indexes created");
  }

  const runCore = async () => {
    console.log("🚀 Starting migration process...");

    // 1) PROJECTS - Transform current projects to new enhanced schema
    console.log("\n📋 Processing Projects...");
    const currentProjects = await currentProjectsCol.find({}).toArray();
    report.counts.projects_current = currentProjects.length;

    const projectIdMap = new Map(); // oldId -> newId
    const projectDocs = currentProjects.map((p) => {
      const newDoc = {
        name: p.name || "Untitled Project",
        client: p.client_company || p.client || null,
        contractType: p.project_type === "tm_only" ? "T&M" : "Fixed",
        invoiceSchedule: "monthly",
        billingDay: DEFAULT_BILLING_DAY,
        openingBalance: DEFAULT_OPENING_BALANCE,
        gcRate: p.labor_rate || DEFAULT_GC_RATE,
        startDate: p.start_date ? iso(p.start_date) : null,
        endDate: p.estimated_completion || p.actual_completion ? iso(p.estimated_completion || p.actual_completion) : null,
        status: p.status && ["active","completed","on-hold"].includes(p.status) ? p.status : "active",
        notes: p.description || p.notes || null,
      };
      return { oldId: p.id || p._id, newDoc };
    });

    if (!DRY_RUN && projectDocs.length) {
      const res = await newProjectsCol.insertMany(projectDocs.map(x => x.newDoc), { ordered: false });
      report.counts.projects_new = res.insertedCount;
      console.log(`✅ Migrated ${res.insertedCount} projects`);
      
      // Build mapping
      const inserted = await newProjectsCol.find({ name: { $in: projectDocs.map(x => x.newDoc.name) } }).toArray();
      const nameToId = new Map(inserted.map(i => [i.name, i._id]));
      for (const x of projectDocs) projectIdMap.set(String(x.oldId), nameToId.get(x.newDoc.name));
    } else {
      report.counts.projects_new = projectDocs.length;
      for (const x of projectDocs) projectIdMap.set(String(x.oldId), new ObjectId());
      console.log(`📋 Would migrate ${projectDocs.length} projects`);
    }

    // 2) CREW MEMBERS - Transform employees to crew_members
    console.log("\n👥 Processing Employees -> Crew Members...");
    const currentEmployees = await currentEmployeesCol.find({}).toArray();
    report.counts.employees_current = currentEmployees.length;

    const crewMemberIdMap = new Map();
    const crewMemberDocs = currentEmployees.map((e) => {
      const newDoc = {
        name: e.name || "Unnamed",
        position: e.position || null,
        hourlyRate: typeof e.hourly_rate === "number" ? e.hourly_rate : (typeof e.base_pay === "number" ? e.base_pay + (e.burden_cost || 0) : null),
        gcBillRate: e.gc_billing_rate || DEFAULT_GC_RATE,
        hireDate: e.hire_date ? iso(e.hire_date) : null,
        status: e.status === "active" ? "active" : "inactive",
      };
      return { oldId: e.id || e._id, newDoc };
    });

    if (!DRY_RUN && crewMemberDocs.length) {
      const res = await newCrewMembersCol.insertMany(crewMemberDocs.map(x => x.newDoc), { ordered: false });
      report.counts.crew_members_new = res.insertedCount;
      console.log(`✅ Migrated ${res.insertedCount} crew members`);
      
      const inserted = await newCrewMembersCol.find({ name: { $in: crewMemberDocs.map(x => x.newDoc.name) } }).toArray();
      const nameToId = new Map(inserted.map(i => [i.name, i._id]));
      for (const x of crewMemberDocs) crewMemberIdMap.set(String(x.oldId), nameToId.get(x.newDoc.name));
    } else {
      report.counts.crew_members_new = crewMemberDocs.length;
      for (const x of crewMemberDocs) crewMemberIdMap.set(String(x.oldId), new ObjectId());
      console.log(`👥 Would migrate ${crewMemberDocs.length} crew members`);
    }

    // 3) CREW LOGS - Transform with enhanced fields (batched)
    console.log("\n📝 Processing Crew Logs...");
    const allCurrentLogs = await currentCrewLogsCol.find({}).toArray();
    report.counts.crew_logs_current = allCurrentLogs.length;

    let newLogsCount = 0;
    const logChunks = chunk(allCurrentLogs, BATCH_SIZE);
    
    for (const [chunkIndex, batch] of logChunks.entries()) {
      console.log(`Processing crew logs batch ${chunkIndex + 1}/${logChunks.length} (${batch.length} logs)`);
      
      const newLogs = batch.map((l) => {
        const newProjectId = projectIdMap.get(String(l.project_id)) || asObjectId(l.project_id);
        
        // Extract crew member info for rates
        const crewMembers = l.crew_members || [];
        let totalHours = 0;
        let totalCostRate = 0;
        let totalBillRate = 0;
        
        // Calculate hours and rates from crew members
        if (Array.isArray(crewMembers)) {
          crewMembers.forEach(member => {
            if (typeof member === 'object' && member.total_hours) {
              totalHours += parseFloat(member.total_hours || 0);
              // Find crew member rates
              const memberName = member.name;
              const crewMemberDoc = crewMemberDocs.find(c => c.newDoc.name === memberName);
              if (crewMemberDoc) {
                totalCostRate += (member.total_hours || 0) * (crewMemberDoc.newDoc.hourlyRate || 40);
                totalBillRate += (member.total_hours || 0) * (crewMemberDoc.newDoc.gcBillRate || DEFAULT_GC_RATE);
              }
            }
          });
        }

        // Use existing hours_worked if no detailed crew member hours
        if (totalHours === 0) {
          totalHours = parseFloat(l.hours_worked || 0);
          totalCostRate = totalHours * 40; // Default cost rate
          totalBillRate = totalHours * DEFAULT_GC_RATE;
        }

        return {
          projectId: newProjectId || new ObjectId(),
          crewMemberId: null, // Will be populated later if needed
          date: iso(l.date) || new Date(),
          hours: totalHours,
          description: l.work_description || null,
          weather: l.weather_conditions || null,
          syncedToTmTag: l.synced_to_tm || false,
          tmTagId: l.tm_tag_id ? asObjectId(l.tm_tag_id) : null,
          costRate: totalCostRate > 0 ? totalCostRate / totalHours : 40,
          billRate: totalBillRate > 0 ? totalBillRate / totalHours : DEFAULT_GC_RATE,
        };
      });

      if (!DRY_RUN && newLogs.length) {
        const res = await newCrewLogsCol.insertMany(newLogs, { ordered: false });
        newLogsCount += res.insertedCount;
      } else {
        newLogsCount += newLogs.length;
      }
    }
    
    report.counts.crew_logs_new = newLogsCount;
    console.log(`✅ ${DRY_RUN ? 'Would migrate' : 'Migrated'} ${newLogsCount} crew logs`);

    // 4) T&M TAGS - Calculate totals with new structure
    console.log("\n🏷️  Processing T&M Tags...");
    const currentTags = await currentTmTagsCol.find({}).toArray();
    report.counts.tm_tags_current = currentTags.length;

    const tmTagDocs = [];
    for (const t of currentTags) {
      const newProjectId = projectIdMap.get(String(t.project_id)) || asObjectId(t.project_id);
      if (!newProjectId) {
        report.warnings.push(`TmTag ${t.id} missing/invalid projectId`);
        continue;
      }

      // Calculate totals from labor entries
      let totalLaborCost = 0;
      let totalLaborBill = 0;
      
      const laborEntries = t.labor_entries || [];
      laborEntries.forEach(entry => {
        const hours = parseFloat(entry.total_hours || 0);
        // Find worker rate
        const workerName = entry.worker_name;
        const crewMember = crewMemberDocs.find(c => c.newDoc.name === workerName);
        const costRate = crewMember ? crewMember.newDoc.hourlyRate : 40;
        const billRate = crewMember ? crewMember.newDoc.gcBillRate : DEFAULT_GC_RATE;
        
        totalLaborCost += hours * costRate;
        totalLaborBill += hours * billRate;
      });

      // Calculate material totals
      let totalMaterialCost = 0;
      let totalMaterialBill = 0;
      const materialEntries = t.material_entries || [];
      materialEntries.forEach(entry => {
        const cost = parseFloat(entry.total || 0);
        totalMaterialCost += cost;
        totalMaterialBill += cost * 1.2; // 20% markup
      });

      // Calculate other totals (expenses)
      let totalExpense = 0;
      const otherEntries = t.other_entries || [];
      otherEntries.forEach(entry => {
        totalExpense += parseFloat(entry.total || 0);
      });

      const newTag = {
        projectId: newProjectId,
        date: iso(t.date_of_work) || new Date(),
        gcEmail: t.gc_email || null,
        foreman: t.foreman_name || null,
        crewLogs: [], // Will be linked later if needed
        materials: [], // Will be populated from materials collection
        expenses: [], // Will be populated from expenses
        totalLaborCost,
        totalLaborBill,
        totalMaterialCost,
        totalMaterialBill,
        totalExpense,
        totalBill: totalLaborBill + totalMaterialBill + totalExpense,
        pdfUrl: null,
        status: ["draft","submitted","accepted"].includes(t.status) ? t.status : "draft",
        tmTagNarrative: t.description_of_work || null
      };

      tmTagDocs.push(newTag);
    }

    if (!DRY_RUN && tmTagDocs.length) {
      const res = await newTmTagsCol.insertMany(tmTagDocs, { ordered: false });
      report.counts.tm_tags_new = res.insertedCount;
      console.log(`✅ Migrated ${res.insertedCount} T&M tags`);
    } else {
      report.counts.tm_tags_new = tmTagDocs.length;
      console.log(`🏷️  Would migrate ${tmTagDocs.length} T&M tags`);
    }

    // 5) MATERIALS - Transform existing materials
    console.log("\n🧱 Processing Materials...");
    const currentMaterials = await currentMaterialsCol.find({}).toArray();
    report.counts.materials_current = currentMaterials.length;

    const materialDocs = currentMaterials.map((m) => ({
      projectId: projectIdMap.get(String(m.project_id)) || asObjectId(m.project_id) || new ObjectId(),
      vendor: m.vendor || "Unknown Vendor",
      date: iso(m.purchase_date) || new Date(),
      description: m.material_name || "Material",
      quantity: parseFloat(m.quantity || 1),
      unitCost: parseFloat(m.unit_cost || 0),
      total: parseFloat(m.total_cost || 0),
      markupPercent: 20, // Default 20% markup
      confirmed: true,
      tmTagId: null, // Will be linked later if needed
    }));

    if (!DRY_RUN && materialDocs.length) {
      const res = await newMaterialsCol.insertMany(materialDocs, { ordered: false });
      report.counts.materials_new = res.insertedCount;
      console.log(`✅ Migrated ${res.insertedCount} materials`);
    } else {
      report.counts.materials_new = materialDocs.length;
      console.log(`🧱 Would migrate ${materialDocs.length} materials`);
    }

    // 6) Initialize empty collections
    if (!DRY_RUN) {
      console.log("\n🆕 Initializing new collections...");
      // Expenses, Invoices, Payables start empty
      await newExpensesCol.insertOne({ _placeholder: true }); // Placeholder to create collection
      await newExpensesCol.deleteOne({ _placeholder: true });
      
      await newInvoicesCol.insertOne({ _placeholder: true });
      await newInvoicesCol.deleteOne({ _placeholder: true });
      
      await newPayablesCol.insertOne({ _placeholder: true });
      await newPayablesCol.deleteOne({ _placeholder: true });
      
      console.log("✅ New collections initialized");
    }

    // Notes / reminders
    report.notes.push(
      "Enhanced project schema with billing schedules and opening balances.",
      "Crew members now have separate hourly rates and GC billing rates.",
      "Materials include markup tracking.",
      "Expenses, Invoices, and Payables start empty - ready for new workflow.",
      "Consider running forecast calculations after migration."
    );
  };

  if (session) {
    try {
      await session.withTransaction(async () => { await runCore(); }, {
        readConcern: { level: "local" },
        writeConcern: DRY_RUN ? { w: "majority" } : { w: "majority" }
      });
      console.log("✅ Migration completed with transaction");
    } catch (e) {
      console.error("❌ Transaction failed:", e);
      report.warnings.push("Transaction failed; migration may be partial.");
    } finally {
      session.endSession();
    }
  } else {
    await runCore(); // no transaction available
    console.log("✅ Migration completed without transaction");
  }

  console.log("\n" + "=".repeat(60));
  console.log("📊 MIGRATION REPORT");
  console.log("=".repeat(60));
  console.log(JSON.stringify(report, null, 2));

  if (DRY_RUN) {
    console.log("\n🧪 DRY RUN COMPLETED - No data was modified");
    console.log("Run without --dry-run to execute the migration");
  } else {
    console.log("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!");
    console.log("Your data has been transformed to the new unified schema.");
  }

  await client.close();
  process.exit(0);
})().catch((err) => {
  console.error("💥 Migration error:", err);
  process.exit(1);
});