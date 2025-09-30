"""
Migration Script: TM3014 → Rhino Platform
Migrates existing data to new schema with project-based T&M rates and cashflow system
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def migrate_data():
    """Main migration function"""
    client = AsyncIOMotorClient(MONGO_URL)
    
    # Old database (TM3014)
    old_db = client.tm_tracker
    
    # New database (Rhino Platform) 
    new_db = client.rhino_platform
    
    logger.info("Starting migration: TM3014 → Rhino Platform")
    
    try:
        # 1. Migrate Installers (remove GC billing fields, keep cost only)
        await migrate_installers(old_db, new_db)
        
        # 2. Migrate Projects (add billing_type and tm_bill_rate)
        await migrate_projects(old_db, new_db)
        
        # 3. Migrate Time Logs (adapt to new project-based billing)
        await migrate_time_logs(old_db, new_db)
        
        # 4. Create Settings collection
        await create_settings(new_db)
        
        # 5. Generate sample cashflow data
        await generate_sample_cashflow(new_db)
        
        # 6. Migration validation
        await validate_migration(old_db, new_db)
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        client.close()

async def migrate_installers(old_db, new_db):
    """Migrate employees/workers to installers (cost only, no GC billing)"""
    logger.info("Migrating installers...")
    
    # Get old employees/crew members
    old_employees = await old_db.employees.find({}).to_list(length=None)
    old_crew = await old_db.crew_members.find({}).to_list(length=None) if 'crew_members' in await old_db.list_collection_names() else []
    
    migrated_count = 0
    
    # Migrate employees
    for emp in old_employees:
        installer = {
            "id": emp.get("id") or emp.get("_id", str(emp["_id"])),
            "name": emp.get("name", "Unknown"),
            "cost_rate": emp.get("hourly_rate", emp.get("base_pay", 65.0)),  # Use true cost, not billing rate
            "position": emp.get("position", "Installer"),
            "active": emp.get("status", "active") == "active",
            "hire_date": emp.get("hire_date"),
            "phone": emp.get("phone"),
            "email": emp.get("email"),
            "created_at": emp.get("created_at", datetime.now())
        }
        
        await new_db.installers.update_one(
            {"id": installer["id"]},
            {"$set": installer},
            upsert=True
        )
        migrated_count += 1
    
    # Migrate crew members (if different collection)
    for crew in old_crew:
        if crew.get("id") not in [emp.get("id") for emp in old_employees]:
            installer = {
                "id": crew.get("id") or str(crew["_id"]),
                "name": crew.get("name", "Unknown"),
                "cost_rate": crew.get("hourly_rate", 65.0),
                "position": "Crew Member",
                "active": True,
                "created_at": crew.get("created_at", datetime.now())
            }
            
            await new_db.installers.update_one(
                {"id": installer["id"]},
                {"$set": installer},
                upsert=True
            )
            migrated_count += 1
    
    logger.info(f"Migrated {migrated_count} installers")

async def migrate_projects(old_db, new_db):
    """Migrate projects with new billing_type and tm_bill_rate fields"""
    logger.info("Migrating projects...")
    
    old_projects = await old_db.projects_new.find({}).to_list(length=None)
    if not old_projects:
        old_projects = await old_db.projects.find({}).to_list(length=None)
    
    migrated_count = 0
    
    for proj in old_projects:
        # Determine billing type based on project data
        project_type = proj.get("project_type", proj.get("type", "tm_only"))
        
        if "tm" in project_type.lower():
            billing_type = "TM"
            tm_bill_rate = proj.get("labor_rate", 95.0)  # Use existing labor rate
        else:
            billing_type = "Fixed"  # Default non-T&M to Fixed
            tm_bill_rate = None
        
        project = {
            "id": proj.get("id") or str(proj["_id"]),
            "name": proj.get("name", "Untitled Project"),
            "billing_type": billing_type,
            "tm_bill_rate": tm_bill_rate,
            "description": proj.get("description"),
            "client_company": proj.get("client_company"),
            "project_manager": proj.get("project_manager"),
            "address": proj.get("address"),
            "status": proj.get("status", "active"),
            "start_date": proj.get("start_date"),
            "estimated_completion": proj.get("estimated_completion"),
            "contract_amount": proj.get("contract_amount"),
            "created_at": proj.get("created_at", datetime.now()),
            "updated_at": datetime.now()
        }
        
        await new_db.projects.update_one(
            {"id": project["id"]},
            {"$set": project},
            upsert=True
        )
        migrated_count += 1
    
    logger.info(f"Migrated {migrated_count} projects")

async def migrate_time_logs(old_db, new_db):
    """Migrate crew logs/time entries to new time_logs"""
    logger.info("Migrating time logs...")
    
    # Get old time entries from various possible collections
    old_entries = []
    
    collections_to_check = ["crew_logs", "tm_tags", "time_entries", "crew_entries"]
    for collection_name in collections_to_check:
        if collection_name in await old_db.list_collection_names():
            entries = await old_db[collection_name].find({}).to_list(length=None)
            old_entries.extend(entries)
    
    migrated_count = 0
    
    for entry in old_entries:
        # Extract time data from different possible formats
        hours = 0
        if "hours" in entry:
            hours = entry["hours"]
        elif "crew_members" in entry:
            # Sum hours from crew members
            for member in entry["crew_members"]:
                hours += member.get("straight_time", 0)
                hours += member.get("overtime", 0) * 1.5  # Convert OT to regular hours equivalent
                hours += member.get("double_time", 0) * 2
        elif "entries" in entry:
            # Sum from labor entries
            for labor_entry in entry.get("entries", {}).get("labor", []):
                hours += labor_entry.get("hours", 0)
        
        if hours > 0:  # Only migrate entries with actual hours
            time_log = {
                "id": entry.get("id") or str(entry["_id"]),
                "date": entry.get("date_of_work", entry.get("date", date.today())),
                "installer_id": entry.get("employee_id", entry.get("installer_id", "unknown")),
                "project_id": entry.get("project_id", "unknown"),
                "hours": round(hours, 2),
                "bill_rate_override": entry.get("bill_rate_override"),
                "notes": entry.get("work_description", entry.get("description")),
                "created_at": entry.get("created_at", datetime.now())
            }
            
            await new_db.time_logs.update_one(
                {"id": time_log["id"]},
                {"$set": time_log},
                upsert=True
            )
            migrated_count += 1
    
    logger.info(f"Migrated {migrated_count} time log entries")

async def create_settings(new_db):
    """Create settings collection with default values"""
    logger.info("Creating settings...")
    
    settings = {
        "id": "default-settings",
        "starting_balance": 34000.0  # As specified in requirements
    }
    
    await new_db.settings.update_one(
        {"id": "default-settings"},
        {"$set": settings},
        upsert=True
    )
    
    logger.info("Created default settings")

async def generate_sample_cashflow(new_db):
    """Generate sample cashflow entries for testing"""
    logger.info("Generating sample cashflow data...")
    
    sample_entries = [
        {
            "id": "cf-1",
            "date": date(2025, 9, 1),
            "type": "inflow",
            "category": "Deposit",
            "amount": 50000.0,
            "reference": "Initial project deposit",
            "created_at": datetime.now()
        },
        {
            "id": "cf-2", 
            "date": date(2025, 9, 15),
            "type": "outflow",
            "category": "Labor",
            "amount": 8500.0,
            "reference": "Payroll - Week 38",
            "created_at": datetime.now()
        },
        {
            "id": "cf-3",
            "date": date(2025, 9, 20),
            "type": "outflow",
            "category": "Material",
            "amount": 12000.0,
            "reference": "Sprinkler heads and fittings",
            "created_at": datetime.now()
        }
    ]
    
    for entry in sample_entries:
        await new_db.cashflows.update_one(
            {"id": entry["id"]},
            {"$set": entry},
            upsert=True
        )
    
    logger.info("Generated sample cashflow data")

async def validate_migration(old_db, new_db):
    """Validate migration results"""
    logger.info("Validating migration...")
    
    # Count records in new collections
    installers_count = await new_db.installers.count_documents({})
    projects_count = await new_db.projects.count_documents({})
    time_logs_count = await new_db.time_logs.count_documents({})
    cashflows_count = await new_db.cashflows.count_documents({})
    settings_count = await new_db.settings.count_documents({})
    
    logger.info(f"Migration validation:")
    logger.info(f"  - Installers: {installers_count}")
    logger.info(f"  - Projects: {projects_count}")
    logger.info(f"  - Time Logs: {time_logs_count}")
    logger.info(f"  - Cashflows: {cashflows_count}")
    logger.info(f"  - Settings: {settings_count}")
    
    # Validate T&M projects have tm_bill_rate
    tm_projects = await new_db.projects.find({"billing_type": "TM"}).to_list(length=None)
    invalid_tm = [p for p in tm_projects if p.get("tm_bill_rate") is None]
    
    if invalid_tm:
        logger.warning(f"Found {len(invalid_tm)} T&M projects without tm_bill_rate")
        for proj in invalid_tm:
            logger.warning(f"  - {proj['name']} (ID: {proj['id']})")
    
    logger.info("Migration validation complete")

if __name__ == "__main__":
    asyncio.run(migrate_data())