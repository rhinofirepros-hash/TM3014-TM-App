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

# Import LLM service
from service_project_intelligence import intelligence_llm

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
    await db.installers.insert_one(installer.dict())
    
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
    
    update_data = installer_data.dict(exclude_unset=True)
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
# HEALTH CHECK
# =============================================================================

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Rhino Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)