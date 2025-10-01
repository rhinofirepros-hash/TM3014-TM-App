"""
Rhino Platform Backend Server
Implements single-domain auth/routing + project-based T&M rates + cashflow system + Project Intelligence
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import asyncio

# Import Rhino Platform models
from models_rhino_platform import (
    Installer, InstallerCreate, InstallerUpdate,
    Project, ProjectCreate, ProjectUpdate,
    TimeLog, TimeLogCreate, TimeLogUpdate,
    PerDiemHotel, PerDiemHotelCreate,
    Cashflow, CashflowCreate,
    Settings,
    TimeLogEffective, ProjectTMTotals, CashBalance,
    validate_project_tm_rate, validate_timelog_project_compatibility
)

# Import Project Intelligence models
from models_project_intelligence import (
    InboundEmail, InboundEmailCreate, EmailAttachment,
    ProjectCandidate, Task, TaskCreate,
    Invoice, InvoiceCreate,
    ProjectProgress, ProjectProgressCreate,
    ReviewQueue, ReviewQueueCreate,
    EmailExtractionResult, ProjectIntelligence, SystemIntelligence
)

# Import LLM service (optional)
try:
    from service_project_intelligence import intelligence_llm
    LLM_AVAILABLE = True
except ImportError:
    intelligence_llm = None
    LLM_AVAILABLE = False
    logger.warning("LLM service not available - Project Intelligence features disabled")

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Rhino Platform API",
    description="Single-domain auth/routing + project-based T&M rates + cashflow system + Project Intelligence",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://tm.rhinofirepro.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.rhino_platform

# Security
security = HTTPBearer(auto_error=False)

# =============================================================================
# AUTHENTICATION & AUTHORIZATION
# =============================================================================

# Admin credentials (in production, use environment variables or database)
ADMIN_CREDENTIALS = {
    "J777": True,  # Main admin PIN
}

USER_ROLES = {
    "admin": ["admin"],
    "gc": ["gc"], 
    "subcontractor": ["subcontractor"]
}

async def verify_admin_pin(pin: str) -> bool:
    """Verify admin PIN"""
    return pin.upper() in ADMIN_CREDENTIALS

async def get_user_role(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get user role from token (simplified for now)"""
    # In production, decode JWT token and extract role
    # For now, return admin for valid credentials
    if credentials:
        return "admin"
    return "anonymous"

# =============================================================================
# STARTUP/SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database collections and seed data"""
    logger.info("Starting Rhino Platform API with Project Intelligence...")
    
    # Initialize collections
    collections = [
        "installers", "projects", "time_logs", "per_diem_hotels", "cashflows", "settings",
        "inbound_emails", "email_attachments", "project_candidates", "tasks",
        "invoices", "project_progress", "review_queue"
    ]
    for collection in collections:
        await db[collection].create_index("id")
    
    # Seed settings if not exists
    settings_count = await db.settings.count_documents({})
    if settings_count == 0:
        default_settings = Settings()
        await db.settings.insert_one(default_settings.dict())
        logger.info("Created default settings")
    
    # Seed example projects from specification
    projects_count = await db.projects.count_documents({})
    if projects_count == 0:
        example_projects = [
            ProjectCreate(
                name="3rd Ave",
                billing_type="TM",
                tm_bill_rate=95.0,
                description="Fire Protection system completion",
                client_company="Nuera Contracting LP"
            ),
            ProjectCreate(
                name="Oregon St", 
                billing_type="TM",
                tm_bill_rate=90.0,
                description="Fire Sprinkler system installation",
                client_company="Camelot Development Group Inc"
            )
        ]
        
        for project_data in example_projects:
            project = Project(**project_data.dict())
            await db.projects.insert_one(project.dict())
        
        logger.info("Seeded example T&M projects")
    
    logger.info("Rhino Platform API with Project Intelligence started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    client.close()
    logger.info("Rhino Platform API shutdown complete")

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/api/auth/admin", tags=["Authentication"])
async def admin_login(request: dict):
    """Admin authentication endpoint"""
    pin = request.get("pin", "")
    
    is_valid = await verify_admin_pin(pin)
    
    if is_valid:
        # In production, generate proper JWT token
        token = f"admin-token-{pin[:2]}**"
        logger.info(f"Admin login successful")
        return {
            "success": True,
            "token": token,
            "role": "admin",
            "redirect": "/admin"
        }
    else:
        logger.warning(f"Failed admin login attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin PIN"
        )

# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@app.get("/api/projects", response_model=List[Project], tags=["Projects"])
async def get_projects(
    billing_type: Optional[str] = None,
    status: Optional[str] = None,
    user_role: str = Depends(get_user_role)
):
    """Get all projects with optional filtering"""
    query = {}
    if billing_type:
        query["billing_type"] = billing_type
    if status:
        query["status"] = status
    
    projects = await db.projects.find(query).to_list(length=None)
    return [Project(**project) for project in projects]

@app.get("/api/projects/{project_id}", response_model=Project, tags=["Projects"])
async def get_project(project_id: str, user_role: str = Depends(get_user_role)):
    """Get specific project"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@app.post("/api/projects", response_model=Project, tags=["Projects"])
async def create_project(project_data: ProjectCreate, user_role: str = Depends(get_user_role)):
    """Create new project with validation"""
    # Validate T&M projects have tm_bill_rate
    if not validate_project_tm_rate(project_data):
        raise HTTPException(
            status_code=422,
            detail="T&M projects must have tm_bill_rate specified"
        )
    
    # Validate non-T&M projects don't have tm_bill_rate
    if project_data.billing_type != "TM" and project_data.tm_bill_rate is not None:
        project_data.tm_bill_rate = None  # Clear it for non-T&M projects
    
    # Check name uniqueness
    existing = await db.projects.find_one({"name": project_data.name})
    if existing:
        raise HTTPException(status_code=422, detail="Project name must be unique")
    
    project = Project(**project_data.dict())
    await db.projects.insert_one(project.dict())
    
    logger.info(f"Created project: {project.name} ({project.billing_type})")
    return project

@app.put("/api/projects/{project_id}", response_model=Project, tags=["Projects"])
async def update_project(
    project_id: str, 
    project_data: ProjectUpdate, 
    user_role: str = Depends(get_user_role)
):
    """Update project with validation"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_data.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now()
        
        # Validate T&M rate requirements
        new_billing_type = update_data.get("billing_type", project.get("billing_type"))
        new_tm_rate = update_data.get("tm_bill_rate", project.get("tm_bill_rate"))
        
        if new_billing_type == "TM" and new_tm_rate is None:
            raise HTTPException(
                status_code=422,
                detail="T&M projects must have tm_bill_rate specified"
            )
        
        if new_billing_type != "TM" and "tm_bill_rate" in update_data:
            update_data["tm_bill_rate"] = None
        
        await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

# =============================================================================
# INSTALLER ENDPOINTS  
# =============================================================================

@app.get("/api/installers", response_model=List[Installer], tags=["Installers"])
async def get_installers(active: Optional[bool] = None, user_role: str = Depends(get_user_role)):
    """Get all installers"""
    query = {}
    if active is not None:
        query["active"] = active
    
    installers = await db.installers.find(query).to_list(length=None)
    return [Installer(**installer) for installer in installers]

@app.get("/api/installers/{installer_id}", response_model=Installer, tags=["Installers"])
async def get_installer(installer_id: str, user_role: str = Depends(get_user_role)):
    """Get specific installer"""
    installer = await db.installers.find_one({"id": installer_id})
    if not installer:
        raise HTTPException(status_code=404, detail="Installer not found")
    return Installer(**installer)

@app.post("/api/installers", response_model=Installer, tags=["Installers"])
async def create_installer(installer_data: InstallerCreate, user_role: str = Depends(get_user_role)):
    """Create new installer"""
    installer = Installer(**installer_data.dict())
    await db.installers.insert_one(installer.model_dump(mode="json"))
    
    logger.info(f"Created installer: {installer.name} (${installer.cost_rate}/hr)")
    return installer

@app.put("/api/installers/{installer_id}", response_model=Installer, tags=["Installers"])
async def update_installer(
    installer_id: str,
    installer_data: InstallerUpdate,
    user_role: str = Depends(get_user_role)
):
    """Update installer"""
    installer = await db.installers.find_one({"id": installer_id})
    if not installer:
        raise HTTPException(status_code=404, detail="Installer not found")
    
    update_data = installer_data.model_dump(exclude_unset=True, mode="json")
    if update_data:
        await db.installers.update_one({"id": installer_id}, {"$set": update_data})
    
    updated_installer = await db.installers.find_one({"id": installer_id})
    return Installer(**updated_installer)

# =============================================================================
# TIME LOG ENDPOINTS
# =============================================================================

@app.get("/api/timelogs", response_model=List[TimeLogEffective], tags=["Time Logs"])
async def get_timelogs(
    project_id: Optional[str] = None,
    installer_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    user_role: str = Depends(get_user_role)
):
    """Get time logs with calculated effective rates"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    if installer_id:
        query["installer_id"] = installer_id
    if from_date or to_date:
        date_query = {}
        if from_date:
            date_query["$gte"] = from_date
        if to_date:
            date_query["$lte"] = to_date
        query["date"] = date_query
    
    # Get time logs with joined data
    pipeline = [
        {"$match": query},
        {"$lookup": {
            "from": "installers",
            "localField": "installer_id",
            "foreignField": "id",
            "as": "installer"
        }},
        {"$lookup": {
            "from": "projects",
            "localField": "project_id", 
            "foreignField": "id",
            "as": "project"
        }},
        {"$unwind": "$installer"},
        {"$unwind": "$project"}
    ]
    
    results = []
    async for doc in db.time_logs.aggregate(pipeline):
        # Calculate effective rates and totals
        installer = doc["installer"]
        project = doc["project"]
        
        eff_cost_rate = installer["cost_rate"]
        eff_bill_rate = doc.get("bill_rate_override") or project.get("tm_bill_rate")
        
        labor_cost = doc["hours"] * eff_cost_rate
        
        # Only calculate billable/profit for T&M projects
        if project["billing_type"] == "TM" and eff_bill_rate:
            billable = doc["hours"] * eff_bill_rate
            profit = billable - labor_cost
        else:
            billable = None
            profit = None
        
        result = TimeLogEffective(
            id=doc["id"],
            date=doc["date"],
            hours=doc["hours"],
            installer_id=doc["installer_id"],
            project_id=doc["project_id"],
            installer_name=installer["name"],
            project_name=project["name"],
            billing_type=project["billing_type"],
            eff_cost_rate=eff_cost_rate,
            eff_bill_rate=eff_bill_rate,
            labor_cost=labor_cost,
            billable=billable,
            profit=profit
        )
        results.append(result)
    
    return results

@app.post("/api/timelogs", response_model=TimeLog, tags=["Time Logs"])
async def create_timelog(timelog_data: TimeLogCreate, user_role: str = Depends(get_user_role)):
    """Create time log with project validation"""
    # Validate installer exists
    installer = await db.installers.find_one({"id": timelog_data.installer_id})
    if not installer:
        raise HTTPException(status_code=422, detail="Installer not found")
    
    # Validate project exists and get billing info
    project = await db.projects.find_one({"id": timelog_data.project_id})
    if not project:
        raise HTTPException(status_code=422, detail="Project not found")
    
    # Validate T&M project compatibility
    if not validate_timelog_project_compatibility(
        project["billing_type"], 
        project.get("tm_bill_rate")
    ):
        raise HTTPException(
            status_code=422,
            detail="Cannot create time log for T&M project without tm_bill_rate"
        )
    
    timelog = TimeLog(**timelog_data.dict())
    
    # Convert date to datetime for MongoDB compatibility
    timelog_dict = timelog.dict()
    if isinstance(timelog_dict['date'], date):
        from datetime import datetime, timezone
        timelog_dict['date'] = datetime.combine(timelog_dict['date'], datetime.min.time()).replace(tzinfo=timezone.utc)
    
    await db.time_logs.insert_one(timelog_dict)
    
    logger.info(f"Created time log: {timelog.hours}h for {installer['name']} on {project['name']}")
    return timelog

# =============================================================================
# SUMMARY/ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/summary/tm", tags=["Analytics"])
async def get_tm_summary(user_role: str = Depends(get_user_role)):
    """Get T&M project totals and cash balance"""
    # Get T&M project totals
    pipeline = [
        {"$lookup": {
            "from": "installers",
            "localField": "installer_id",
            "foreignField": "id", 
            "as": "installer"
        }},
        {"$lookup": {
            "from": "projects",
            "localField": "project_id",
            "foreignField": "id",
            "as": "project"
        }},
        {"$unwind": "$installer"},
        {"$unwind": "$project"},
        {"$match": {"project.billing_type": "TM"}},
        {"$group": {
            "_id": {
                "project_id": "$project_id",
                "project_name": "$project.name"
            },
            "hours": {"$sum": "$hours"},
            "labor_cost": {"$sum": {"$multiply": ["$hours", "$installer.cost_rate"]}},
            "billable": {"$sum": {"$multiply": [
                "$hours", 
                {"$ifNull": ["$bill_rate_override", "$project.tm_bill_rate"]}
            ]}},
        }},
        {"$project": {
            "project": "$_id.project_name",
            "project_id": "$_id.project_id",
            "hours": 1,
            "labor_cost": 1,
            "billable": 1,
            "profit": {"$subtract": ["$billable", "$labor_cost"]}
        }}
    ]
    
    tm_totals = []
    async for doc in db.time_logs.aggregate(pipeline):
        tm_totals.append(ProjectTMTotals(
            project=doc["project"],
            project_id=doc["project_id"],
            hours=doc["hours"],
            labor_cost=doc["labor_cost"],
            billable=doc["billable"],
            profit=doc["profit"]
        ))
    
    # Get cash balance
    settings = await db.settings.find_one({})
    starting_balance = settings["starting_balance"] if settings else 34000.0
    
    # Calculate running balance
    pipeline_cash = [
        {"$project": {
            "signed_amount": {
                "$cond": [
                    {"$eq": ["$type", "inflow"]},
                    "$amount",
                    {"$multiply": ["$amount", -1]}
                ]
            }
        }},
        {"$group": {
            "_id": None,
            "total_change": {"$sum": "$signed_amount"},
            "total_inflows": {"$sum": {"$cond": [{"$eq": ["$type", "inflow"]}, "$amount", 0]}},
            "total_outflows": {"$sum": {"$cond": [{"$eq": ["$type", "outflow"]}, "$amount", 0]}}
        }}
    ]
    
    cash_doc = await db.cashflows.aggregate(pipeline_cash).to_list(length=1)
    if cash_doc:
        cash_data = cash_doc[0]
        current_balance = starting_balance + cash_data["total_change"]
        total_inflows = cash_data["total_inflows"]
        total_outflows = cash_data["total_outflows"]
    else:
        current_balance = starting_balance
        total_inflows = 0
        total_outflows = 0
    
    cash_balance = CashBalance(
        current_balance=current_balance,
        starting_balance=starting_balance,
        total_inflows=total_inflows,
        total_outflows=total_outflows
    )
    
    return {
        "tm_project_totals": tm_totals,
        "cash_balance": cash_balance
    }

# =============================================================================
# CASHFLOW ENDPOINTS
# =============================================================================

@app.get("/api/cashflows", response_model=List[Cashflow], tags=["Cashflow"])
async def get_cashflows(
    project_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    type: Optional[str] = None,
    user_role: str = Depends(get_user_role)
):
    """Get cashflow entries with optional filtering"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    if type:
        query["type"] = type
    if from_date or to_date:
        date_query = {}
        if from_date:
            date_query["$gte"] = from_date
        if to_date:
            date_query["$lte"] = to_date
        query["date"] = date_query
    
    cashflows = await db.cashflows.find(query).sort("date", 1).to_list(length=None)
    return [Cashflow(**cf) for cf in cashflows]

@app.post("/api/cashflows", response_model=Cashflow, tags=["Cashflow"])
async def create_cashflow(cashflow_data: CashflowCreate, user_role: str = Depends(get_user_role)):
    """Create cashflow entry"""
    # Validate project if specified
    if cashflow_data.project_id:
        project = await db.projects.find_one({"id": cashflow_data.project_id})
        if not project:
            raise HTTPException(status_code=422, detail="Project not found")
    
    cashflow = Cashflow(**cashflow_data.dict())
    
    # Convert date to datetime for MongoDB compatibility
    cashflow_dict = cashflow.dict()
    if isinstance(cashflow_dict['date'], date):
        from datetime import datetime, timezone
        cashflow_dict['date'] = datetime.combine(cashflow_dict['date'], datetime.min.time()).replace(tzinfo=timezone.utc)
    
    await db.cashflows.insert_one(cashflow_dict)
    
    logger.info(f"Created cashflow: {cashflow.type} ${cashflow.amount} ({cashflow.category})")
    return cashflow

# =============================================================================
# PROJECT INTELLIGENCE ENDPOINTS
# =============================================================================

@app.post("/api/intelligence/process-email", response_model=EmailExtractionResult, tags=["Project Intelligence"])
async def process_email(email_data: InboundEmailCreate, user_role: str = Depends(get_user_role)):
    """Process email with LLM intelligence"""
    if not LLM_AVAILABLE:
        raise HTTPException(status_code=503, detail="LLM service not available")
        
    try:
        # Create email record
        email = InboundEmail(**email_data.dict())
        await db.inbound_emails.insert_one(email.dict())
        
        # Process with LLM
        extraction_result, auto_commit = await intelligence_llm.process_email_complete(
            subject=email.subject,
            body=email.body,
            from_addr=email.from_addr
        )
        
        # Update email with classification
        await db.inbound_emails.update_one(
            {"id": email.id},
            {"$set": {
                "classified_as": extraction_result.classification.label,
                "confidence": extraction_result.classification.confidence,
                "processed": auto_commit
            }}
        )
        
        # Auto-process if high confidence
        if auto_commit:
            await auto_process_extraction(email.id, extraction_result)
        else:
            # Add to review queue
            review_item = ReviewQueueCreate(
                entity="classification",
                payload=extraction_result.dict(),
                reason=f"Low/medium confidence: {extraction_result.classification.confidence:.2f}",
                confidence=extraction_result.classification.confidence,
                source_email_id=email.id
            )
            await create_review_item(review_item)
        
        logger.info(f"Processed email: {email.subject} -> {extraction_result.classification.label}")
        return extraction_result
        
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")

async def auto_process_extraction(email_id: str, extraction: EmailExtractionResult):
    """Auto-process high-confidence extractions"""
    try:
        # Create project if extracted
        if extraction.project and extraction.project.name:
            project_candidate = ProjectCandidate(
                email_id=email_id,
                name=extraction.project.name,
                billing_type=extraction.project.billing_type or "Fixed",
                tm_bill_rate=extraction.project.tm_bill_rate,
                description=extraction.project.description,
                client_company=extraction.project.client_company,
                project_manager=extraction.project.project_manager,
                address=extraction.project.address,
                city=extraction.project.city,
                state=extraction.project.state,
                zip_code=extraction.project.zip_code,
                ahj=extraction.project.ahj,
                confidence=extraction.classification.confidence,
                status="auto_approved" if extraction.classification.confidence >= 0.9 else "pending_review"
            )
            await db.project_candidates.insert_one(project_candidate.dict())
        
        # Create tasks if suggested
        if extraction.tasks:
            for task_title in extraction.tasks:
                task = TaskCreate(
                    project_id="pending",  # Will be linked when project is confirmed
                    type="extracted",
                    title=task_title,
                    source_email_id=email_id
                )
                await db.tasks.insert_one(Task(**task.dict()).dict())
        
        # Create invoice if financial data extracted
        if extraction.financial and extraction.financial.amount:
            invoice = InvoiceCreate(
                project_id="pending",
                invoice_number=extraction.financial.invoice_number or f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                invoice_date=datetime.now().date(),
                amount=extraction.financial.amount,
                description="Auto-extracted from email",
                source_email_id=email_id
            )
            await db.invoices.insert_one(Invoice(**invoice.dict()).dict())
        
    except Exception as e:
        logger.error(f"Error in auto-processing: {str(e)}")

async def create_review_item(review_data: ReviewQueueCreate):
    """Create review queue item"""
    review_item = ReviewQueue(**review_data.dict())
    await db.review_queue.insert_one(review_item.dict())

@app.get("/api/intelligence/emails", response_model=List[InboundEmail], tags=["Project Intelligence"])
async def get_emails(
    processed: Optional[bool] = None,
    classification: Optional[str] = None,
    limit: int = 50,
    user_role: str = Depends(get_user_role)
):
    """Get processed emails"""
    query = {}
    if processed is not None:
        query["processed"] = processed
    if classification:
        query["classified_as"] = classification
    
    emails = await db.inbound_emails.find(query).sort("received_at", -1).limit(limit).to_list(length=None)
    return [InboundEmail(**email) for email in emails]

@app.get("/api/intelligence/project-candidates", response_model=List[ProjectCandidate], tags=["Project Intelligence"])
async def get_project_candidates(
    status: Optional[str] = None,
    user_role: str = Depends(get_user_role)
):
    """Get project candidates"""
    query = {}
    if status:
        query["status"] = status
    
    candidates = await db.project_candidates.find(query).sort("created_at", -1).to_list(length=None)
    return [ProjectCandidate(**candidate) for candidate in candidates]

@app.post("/api/intelligence/approve-candidate/{candidate_id}", tags=["Project Intelligence"])
async def approve_project_candidate(candidate_id: str, user_role: str = Depends(get_user_role)):
    """Approve project candidate and create actual project"""
    candidate = await db.project_candidates.find_one({"id": candidate_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Project candidate not found")
    
    # Create actual project
    project_data = ProjectCreate(
        name=candidate["name"],
        billing_type=candidate["billing_type"],
        tm_bill_rate=candidate.get("tm_bill_rate"),
        description=candidate.get("description"),
        client_company=candidate.get("client_company"),
        project_manager=candidate.get("project_manager"),
        address=candidate.get("address"),
        status="active"
    )
    
    # Validate T&M requirements
    if not validate_project_tm_rate(project_data):
        raise HTTPException(status_code=422, detail="T&M projects must have tm_bill_rate specified")
    
    project = Project(**project_data.dict())
    await db.projects.insert_one(project.dict())
    
    # Update candidate status
    await db.project_candidates.update_one(
        {"id": candidate_id},
        {"$set": {"status": "approved", "created_project_id": project.id}}
    )
    
    # Update any pending tasks
    await db.tasks.update_many(
        {"source_email_id": candidate["email_id"], "project_id": "pending"},
        {"$set": {"project_id": project.id}}
    )
    
    logger.info(f"Approved project candidate: {candidate['name']} -> {project.id}")
    return {"success": True, "project_id": project.id}

# =============================================================================
# TASK MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/tasks", response_model=List[Task], tags=["Task Management"])
async def get_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    user_role: str = Depends(get_user_role)
):
    """Get tasks with optional filtering"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    if status:
        query["status"] = status
    if type:
        query["type"] = type
    
    tasks = await db.tasks.find(query).sort("created_at", -1).to_list(length=None)
    return [Task(**task) for task in tasks]

@app.post("/api/tasks", response_model=Task, tags=["Task Management"])
async def create_task(task_data: TaskCreate, user_role: str = Depends(get_user_role)):
    """Create new task"""
    task = Task(**task_data.dict())
    await db.tasks.insert_one(task.dict())
    logger.info(f"Created task: {task.title} for project {task.project_id}")
    return task

@app.put("/api/tasks/{task_id}", response_model=Task, tags=["Task Management"])
async def update_task(
    task_id: str,
    task_data: dict,
    user_role: str = Depends(get_user_role)
):
    """Update task"""
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in task_data.items() if v is not None}
    if update_data:
        if "status" in update_data and update_data["status"] == "completed":
            update_data["completed_at"] = datetime.now()
        
        await db.tasks.update_one({"id": task_id}, {"$set": update_data})
    
    updated_task = await db.tasks.find_one({"id": task_id})
    return Task(**updated_task)

# =============================================================================
# INVOICE MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/invoices", response_model=List[Invoice], tags=["Invoice Management"])
async def get_invoices(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    user_role: str = Depends(get_user_role)
):
    """Get invoices with optional filtering"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    if status:
        query["status"] = status
    
    invoices = await db.invoices.find(query).sort("invoice_date", -1).to_list(length=None)
    return [Invoice(**invoice) for invoice in invoices]

@app.post("/api/invoices", response_model=Invoice, tags=["Invoice Management"])
async def create_invoice(invoice_data: InvoiceCreate, user_role: str = Depends(get_user_role)):
    """Create new invoice"""
    invoice = Invoice(**invoice_data.dict())
    await db.invoices.insert_one(invoice.dict())
    logger.info(f"Created invoice: {invoice.invoice_number} for ${invoice.amount}")
    return invoice

@app.put("/api/invoices/{invoice_id}", response_model=Invoice, tags=["Invoice Management"])
async def update_invoice(
    invoice_id: str,
    invoice_data: dict,
    user_role: str = Depends(get_user_role)
):
    """Update invoice"""
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_data = {k: v for k, v in invoice_data.items() if v is not None}
    if update_data:
        if "status" in update_data and update_data["status"] == "paid":
            update_data["paid_date"] = datetime.now().date()
        
        await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    
    updated_invoice = await db.invoices.find_one({"id": invoice_id})
    return Invoice(**updated_invoice)

# =============================================================================
# REVIEW QUEUE ENDPOINTS
# =============================================================================

@app.get("/api/review-queue", response_model=List[ReviewQueue], tags=["Review Queue"])
async def get_review_queue(
    resolved: Optional[bool] = False,
    priority: Optional[str] = None,
    user_role: str = Depends(get_user_role)
):
    """Get review queue items"""
    query = {"resolved": resolved}
    if priority:
        query["priority"] = priority
    
    items = await db.review_queue.find(query).sort("created_at", -1).to_list(length=None)
    return [ReviewQueue(**item) for item in items]

@app.post("/api/review-queue/{item_id}/resolve", tags=["Review Queue"])
async def resolve_review_item(
    item_id: str,
    resolution_data: dict,
    user_role: str = Depends(get_user_role)
):
    """Resolve review queue item"""
    item = await db.review_queue.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    
    # Update item as resolved
    await db.review_queue.update_one(
        {"id": item_id},
        {"$set": {
            "resolved": True,
            "resolved_by": "current_user",  # TODO: Get actual user ID
            "resolved_at": datetime.now(),
            "resolution_notes": resolution_data.get("notes", "")
        }}
    )
    
    # Process the resolution action
    action = resolution_data.get("action", "approve")
    if action == "approve" and item["entity"] == "project_candidate":
        # Auto-approve the project candidate
        candidate_id = item["payload"].get("project", {}).get("id")
        if candidate_id:
            await approve_project_candidate(candidate_id)
    
    return {"success": True, "action": action}

# =============================================================================
# PROJECT INTELLIGENCE DASHBOARD
# =============================================================================

@app.get("/api/intelligence/dashboard", tags=["Intelligence Dashboard"])
async def get_intelligence_dashboard(user_role: str = Depends(get_user_role)):
    """Get comprehensive intelligence dashboard"""
    
    # Get counts and summaries
    total_projects = await db.projects.count_documents({})
    active_projects = await db.projects.count_documents({"status": "active"})
    pending_reviews = await db.review_queue.count_documents({"resolved": False}) if LLM_AVAILABLE else 0
    overdue_tasks = await db.tasks.count_documents({
        "due_date": {"$lt": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)},
        "status": {"$ne": "completed"}
    }) if LLM_AVAILABLE else 0
    recent_emails = await db.inbound_emails.count_documents({
        "received_at": {"$gte": datetime.now().replace(hour=0, minute=0, second=0)}
    }) if LLM_AVAILABLE else 0
    
    # Get financial summary
    total_outstanding = 0
    if LLM_AVAILABLE:
        outstanding_invoices = await db.invoices.find({"status": {"$ne": "paid"}}).to_list(length=None)
        for invoice in outstanding_invoices:
            total_outstanding += invoice.get("amount", 0)
    
    high_priority_items = await db.tasks.count_documents({"priority": "urgent", "status": {"$ne": "completed"}}) if LLM_AVAILABLE else 0
    
    system_intelligence = SystemIntelligence(
        total_projects=total_projects,
        active_projects=active_projects,
        pending_reviews=pending_reviews,
        overdue_tasks=overdue_tasks,
        recent_emails=recent_emails,
        total_outstanding=total_outstanding,
        high_priority_items=high_priority_items,
        last_updated=datetime.now()
    )
    
    return system_intelligence

@app.get("/api/intelligence/project/{project_id}", response_model=ProjectIntelligence, tags=["Intelligence Dashboard"])
async def get_project_intelligence(project_id: str, user_role: str = Depends(get_user_role)):
    """Get comprehensive project intelligence"""
    
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get project tasks
    tasks = await db.tasks.find({"project_id": project_id}).to_list(length=None)
    pending_tasks = len([t for t in tasks if t.get("status") != "completed"])
    overdue_tasks = len([t for t in tasks if t.get("due_date") and t.get("due_date") < datetime.now().date() and t.get("status") != "completed"])
    
    # Get recent emails
    recent_emails = await db.inbound_emails.count_documents({
        "received_at": {"$gte": datetime.now().replace(day=datetime.now().day-7)}
    })
    
    # Get invoices
    invoices = await db.invoices.find({"project_id": project_id}).to_list(length=None)
    outstanding_amount = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") != "paid")
    
    # Get progress
    progress_entries = await db.project_progress.find({"project_id": project_id}).to_list(length=None)
    avg_progress = sum(p.get("progress_percentage", 0) for p in progress_entries) / max(len(progress_entries), 1)
    
    # Recent activities (simplified)
    recent_activities = [
        f"{len(tasks)} total tasks",
        f"{len(invoices)} invoices",
        f"{recent_emails} recent emails"
    ]
    
    # Next milestone
    next_task = None
    for task in tasks:
        if task.get("status") != "completed" and task.get("due_date"):
            if not next_task or task["due_date"] < next_task["due_date"]:
                next_task = task
    
    project_intelligence = ProjectIntelligence(
        project_id=project_id,
        project_name=project["name"],
        current_status=project.get("status", "unknown"),
        progress_percentage=avg_progress,
        recent_activities=recent_activities,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        recent_emails=recent_emails,
        total_invoices=len(invoices),
        outstanding_amount=outstanding_amount,
        next_milestone=next_task["title"] if next_task else None,
        next_due_date=next_task["due_date"] if next_task else None,
        risk_factors=["Overdue tasks" if overdue_tasks > 0 else None],
        last_updated=datetime.now()
    )
    
    return project_intelligence

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Rhino Platform API with Project Intelligence",
        "version": "2.1.0",  # Updated version to trigger redeploy
        "llm_available": LLM_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)