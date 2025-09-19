from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import asyncio
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64

# Import financial models
from models_financial import (
    Invoice, InvoiceCreate, InvoiceUpdate,
    Payable, PayableCreate, PayableUpdate,
    CashflowForecast, CashflowForecastCreate, CashflowForecastUpdate,
    Profitability, ProfitabilityCreate, ProfitabilityUpdate,
    Inspection, InspectionCreate, InspectionUpdate
)

# Import GC Dashboard models
from models_gc_dashboard import (
    GcKey, GcKeyCreate, GcAccessLog, GcAccessLogCreate,
    ProjectPhaseModel, ProjectPhaseCreate, ProjectPhaseUpdate,
    InspectionStatusModel, InspectionStatusCreate, InspectionStatusUpdate,
    GcNarrative, GcNarrativeCreate,
    GcProjectDashboard, GcCrewSummary, GcMaterialSummary, GcTmTagSummary,
    GcKeyAdmin, GcAccessLogAdmin
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Financial collections
invoices_collection = db["invoices"]
payables_collection = db["payables"]
cashflow_forecasts_collection = db["cashflow_forecasts"]
profitability_collection = db["profitability"]
inspections_collection = db["inspections"]

# GC Dashboard collections
gc_keys_collection = db["gc_keys"]
gc_access_logs_collection = db["gc_access_logs"]
project_phases_collection = db["project_phases"]
inspection_status_collection = db["inspection_status"]
gc_narratives_collection = db["gc_narratives"]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# T&M Tag Models
class LaborEntry(BaseModel):
    id: str
    worker_name: str
    quantity: float
    st_hours: float
    ot_hours: float
    dt_hours: float
    pot_hours: float
    total_hours: float
    date: str

class MaterialEntry(BaseModel):
    id: str
    material_name: str
    unit_of_measure: str
    quantity: float
    unit_cost: Optional[float] = 0
    total: float
    date_of_work: str

class EquipmentEntry(BaseModel):
    id: str
    equipment_name: str
    pieces_of_equipment: int
    unit_of_measure: str
    quantity: float
    total: float
    date_of_work: str

class OtherEntry(BaseModel):
    id: str
    other_name: str
    quantity_of_other: int
    unit_of_measure: str
    quantity_of_unit: float
    total: float
    date_of_work: str

class TMTag(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None  # Link to project
    project_name: str
    cost_code: str
    date_of_work: datetime
    company_name: Optional[str] = ""
    tm_tag_title: str
    description_of_work: str
    labor_entries: List[LaborEntry] = []
    material_entries: List[MaterialEntry] = []
    equipment_entries: List[EquipmentEntry] = []
    other_entries: List[OtherEntry] = []
    gc_email: str
    signature: Optional[str] = None
    foreman_name: str = "Jesus Garcia"
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None

class TMTagCreate(BaseModel):
    project_id: Optional[str] = None  # Link to project
    project_name: str
    cost_code: str
    date_of_work: datetime
    company_name: Optional[str] = ""
    tm_tag_title: str
    description_of_work: str
    labor_entries: List[LaborEntry] = []
    material_entries: List[MaterialEntry] = []
    equipment_entries: List[EquipmentEntry] = []
    other_entries: List[OtherEntry] = []
    gc_email: str
    signature: Optional[str] = None

class EmailRequest(BaseModel):
    to_email: str
    cc_email: Optional[str] = ""
    subject: str
    message: str
    pdf_data: str  # base64 encoded PDF
    tm_tag_id: str

class Worker(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    rate: float = 95.0
    position: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Enhanced AI Super Tracking Models
class Phase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = ""
    estimated_hours: Optional[float] = 0
    estimated_cost: Optional[float] = 0
    actual_hours: Optional[float] = 0
    actual_cost: Optional[float] = 0
    status: str = "pending"  # pending, in-progress, completed, on-hold
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PhaseCreate(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = ""
    estimated_hours: Optional[float] = 0
    estimated_cost: Optional[float] = 0
    status: Optional[str] = "pending"
    start_date: Optional[datetime] = None

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    phase_id: Optional[str] = None
    name: str
    description: Optional[str] = ""
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = 0
    actual_hours: Optional[float] = 0
    status: str = "open"  # open, in-progress, completed, blocked
    priority: str = "medium"  # low, medium, high, urgent
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(BaseModel):
    project_id: str
    phase_id: Optional[str] = None
    name: str
    description: Optional[str] = ""
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = 0
    status: Optional[str] = "open"
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    source: str  # email, portal, manual, ai-generated
    source_id: Optional[str] = None  # Original email ID or portal reference
    update_type: str  # inspection, financial, material, delay, change-order, communication
    title: str
    summary: str
    full_content: Optional[str] = ""
    ai_confidence: Optional[float] = 0.0  # 0-1 confidence score from AI
    requires_review: bool = True  # Always true for AI-generated updates
    tags: List[str] = []
    extracted_data: Optional[dict] = {}  # Structured data extracted by AI
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

class ProjectUpdateCreate(BaseModel):
    project_id: str
    source: str
    source_id: Optional[str] = None
    update_type: str
    title: str
    summary: str
    full_content: Optional[str] = ""
    ai_confidence: Optional[float] = 0.0
    requires_review: Optional[bool] = True
    tags: Optional[List[str]] = []
    extracted_data: Optional[dict] = {}

class TMTicket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    task_id: Optional[str] = None
    tm_tag_id: Optional[str] = None  # Link to existing T&M tags
    employee_name: str
    date: datetime
    ticket_type: str  # labor, material, equipment, other
    hours: Optional[float] = 0
    rate: Optional[float] = 95  # Default GC rate
    cost: Optional[float] = 0
    description: Optional[str] = ""
    approved: bool = False
    approved_by: Optional[str] = None  
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TMTicketCreate(BaseModel):
    project_id: str
    task_id: Optional[str] = None
    tm_tag_id: Optional[str] = None
    employee_name: str
    date: datetime
    ticket_type: str
    hours: Optional[float] = 0
    rate: Optional[float] = 95
    cost: Optional[float] = 0
    description: Optional[str] = ""

# Project Management Models (extend existing)
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    client_company: str
    gc_email: str
    project_type: str = "full_project"  # full_project or tm_only
    contract_amount: Optional[float] = 0
    labor_rate: Optional[float] = 95.0  # Hourly rate billed to this client
    project_manager: str = "Jesus Garcia"
    status: str = "active"  # active, completed, on_hold, cancelled
    start_date: datetime
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    # Forecasted schedule fields
    estimated_hours: Optional[float] = 0  # Forecasted total hours
    estimated_labor_cost: Optional[float] = 0  # Forecasted labor cost
    estimated_material_cost: Optional[float] = 0  # Forecasted material cost
    estimated_profit: Optional[float] = 0  # Expected profit
    address: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    client_company: str
    gc_email: str
    project_type: Optional[str] = "full_project"  # full_project or tm_only
    contract_amount: Optional[float] = 0
    labor_rate: Optional[float] = 95.0  # Default to $95/hr, but customizable
    project_manager: Optional[str] = "Jesus Garcia"
    start_date: datetime
    estimated_completion: Optional[datetime] = None
    # Forecasted schedule fields
    estimated_hours: Optional[float] = 0  # Forecasted total hours
    estimated_labor_cost: Optional[float] = 0  # Forecasted labor cost
    estimated_material_cost: Optional[float] = 0  # Forecasted material cost
    estimated_profit: Optional[float] = 0  # Expected profit
    address: Optional[str] = ""

class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hourly_rate: float  # True hourly cost for calculations
    gc_billing_rate: float = 95.0  # Rate billed to GC
    position: str
    hire_date: datetime
    status: str = "active"  # active, inactive, terminated
    phone: Optional[str] = ""
    email: Optional[str] = ""
    emergency_contact: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmployeeCreate(BaseModel):
    name: str
    hourly_rate: float  # True hourly cost
    gc_billing_rate: Optional[float] = 95.0  # Default GC billing rate
    position: str
    hire_date: datetime
    phone: Optional[str] = ""
    email: Optional[str] = ""
    emergency_contact: Optional[str] = ""

class CrewLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    project_name: str
    date: datetime
    crew_members: List[str]  # List of employee names/IDs
    work_description: str
    hours_worked: float
    per_diem: Optional[float] = 0
    hotel_cost: Optional[float] = 0
    gas_expense: Optional[float] = 0
    other_expenses: Optional[float] = 0
    expense_notes: Optional[str] = ""
    weather_conditions: Optional[str] = ""
    logged_by: str = "Jesus Garcia"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CrewLogCreate(BaseModel):
    project_id: str
    project_name: str
    date: datetime
    crew_members: List[str]
    work_description: str
    hours_worked: float
    per_diem: Optional[float] = 0
    hotel_cost: Optional[float] = 0
    gas_expense: Optional[float] = 0
    other_expenses: Optional[float] = 0
    expense_notes: Optional[str] = ""
    weather_conditions: Optional[str] = ""

class MaterialPurchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    project_name: str
    purchase_date: datetime
    vendor: str
    material_name: str
    quantity: float
    unit_cost: float
    total_cost: float
    invoice_number: Optional[str] = ""
    receipt_image: Optional[str] = ""  # Base64 encoded image
    category: str = "general"  # pipe, fittings, equipment, etc.
    purchased_by: str = "Jesus Garcia"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MaterialPurchaseCreate(BaseModel):
    project_id: str
    project_name: str
    purchase_date: datetime
    vendor: str
    material_name: str
    quantity: float
    unit_cost: float
    total_cost: float
    invoice_number: Optional[str] = ""
    receipt_image: Optional[str] = ""
    category: Optional[str] = "general"

class WorkerCreate(BaseModel):
    name: str
    rate: Optional[float] = 95.0
    position: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# T&M Tag Endpoints
# Enhanced T&M Tag Creation with Crew Log Sync
@api_router.post("/tm-tags", response_model=TMTag)
async def create_tm_tag(tm_tag: TMTagCreate):
    tm_tag_dict = tm_tag.dict()
    tm_tag_obj = TMTag(**tm_tag_dict)
    tm_tag_obj.submitted_at = datetime.utcnow()
    
    # Insert into database
    result = await db.tm_tags.insert_one(tm_tag_obj.dict())
    
    # Sync to crew logs
    await sync_tm_to_crew_log(tm_tag_obj.dict())
    
    return tm_tag_obj

@api_router.get("/tm-tags", response_model=List[TMTag])
async def get_tm_tags(skip: int = 0, limit: int = 100):
    tm_tags = await db.tm_tags.find().skip(skip).limit(limit).to_list(limit)
    return [TMTag(**tm_tag) for tm_tag in tm_tags]

@api_router.get("/tm-tags/{tm_tag_id}")
async def get_tm_tag(tm_tag_id: str):
    tm_tag = await db.tm_tags.find_one({"id": tm_tag_id})
    if tm_tag:
        return TMTag(**tm_tag)
    return {"error": "T&M Tag not found"}

@api_router.delete("/tm-tags/{tm_tag_id}")
async def delete_tm_tag(tm_tag_id: str):
    result = await db.tm_tags.delete_one({"id": tm_tag_id})
    if result.deleted_count == 1:
        return {"message": "T&M Tag deleted successfully", "id": tm_tag_id}
    return {"error": "T&M Tag not found"}

@api_router.put("/tm-tags/{tm_tag_id}")
async def update_tm_tag(tm_tag_id: str, update_data: dict):
    """Update T&M tag with new data"""
    try:
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.tm_tags.update_one(
            {"id": tm_tag_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            updated_tag = await db.tm_tags.find_one({"id": tm_tag_id})
            return TMTag(**updated_tag)
        return {"error": "T&M Tag not found"}
        
    except Exception as e:
        return {"error": str(e)}

# Worker Management Endpoints
@api_router.post("/workers", response_model=Worker)
async def create_worker(worker: WorkerCreate):
    worker_dict = worker.dict()
    worker_obj = Worker(**worker_dict)
    
    # Insert into database
    result = await db.workers.insert_one(worker_obj.dict())
    
    return worker_obj

@api_router.get("/workers", response_model=List[Worker])
async def get_workers():
    workers = await db.workers.find({"active": True}).to_list(1000)
    return [Worker(**worker) for worker in workers]

@api_router.delete("/workers/{worker_id}")
async def delete_worker(worker_id: str):
    result = await db.workers.delete_one({"id": worker_id})
    if result.deleted_count == 1:
        return {"message": "Worker deleted successfully", "id": worker_id}
    return {"error": "Worker not found"}

# Project Management Endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    project_dict = project.dict()
    project_obj = Project(**project_dict)
    
    # Insert into database
    result = await db.projects.insert_one(project_obj.dict())
    
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    
    projects = await db.projects.find(query).to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if project:
        return Project(**project)
    return {"error": "Project not found"}

@api_router.put("/projects/{project_id}")
async def update_project(project_id: str, project_update: ProjectCreate):
    update_dict = project_update.dict()
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.projects.update_one(
        {"id": project_id}, 
        {"$set": update_dict}
    )
    
    if result.modified_count == 1:
        updated_project = await db.projects.find_one({"id": project_id})
        return Project(**updated_project)
    return {"error": "Project not found"}

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 1:
        return {"message": "Project deleted successfully", "id": project_id}
    return {"error": "Project not found"}

# Employee Management Endpoints
@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate):
    employee_dict = employee.dict()
    employee_obj = Employee(**employee_dict)
    
    # Insert into database
    result = await db.employees.insert_one(employee_obj.dict())
    
    return employee_obj

@api_router.get("/employees", response_model=List[Employee])
async def get_employees(status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    else:
        query["status"] = "active"  # Default to active employees
    
    employees = await db.employees.find(query).to_list(1000)
    
    # Handle schema migration - convert old schema to new schema
    processed_employees = []
    for employee in employees:
        if "_id" in employee:
            del employee["_id"]  # Remove MongoDB ObjectId
        
        # Convert old schema to new schema if needed
        if "base_pay" in employee and "burden_cost" in employee:
            # Old schema: convert to new schema
            total_cost = float(employee.get("base_pay", 0)) + float(employee.get("burden_cost", 0))
            employee["hourly_rate"] = total_cost
            employee["gc_billing_rate"] = employee.get("gc_billing_rate", 95.0)
            
            # Remove old fields
            employee.pop("base_pay", None)
            employee.pop("burden_cost", None)
            
            # Update in database to new schema
            await db.employees.update_one(
                {"id": employee["id"]},
                {"$set": {
                    "hourly_rate": total_cost,
                    "gc_billing_rate": 95.0
                }, "$unset": {
                    "base_pay": "",
                    "burden_cost": ""
                }}
            )
        
        # Ensure required fields exist
        if "hourly_rate" not in employee:
            employee["hourly_rate"] = 40.0  # Default value
        if "gc_billing_rate" not in employee:
            employee["gc_billing_rate"] = 95.0  # Default value
            
        processed_employees.append(employee)
    
    return [Employee(**employee) for employee in processed_employees]

@api_router.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    employee = await db.employees.find_one({"id": employee_id})
    if employee:
        return Employee(**employee)
    return {"error": "Employee not found"}

@api_router.put("/employees/{employee_id}")
async def update_employee(employee_id: str, employee_update: EmployeeCreate):
    update_dict = employee_update.dict()
    
    result = await db.employees.update_one(
        {"id": employee_id}, 
        {"$set": update_dict}
    )
    
    if result.modified_count == 1:
        updated_employee = await db.employees.find_one({"id": employee_id})
        return Employee(**updated_employee)
    return {"error": "Employee not found"}

@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    result = await db.employees.delete_one({"id": employee_id})
    if result.deleted_count == 1:
        return {"message": "Employee deleted successfully", "id": employee_id}
    return {"error": "Employee not found"}

# Crew Logging Endpoints with T&M Integration
@api_router.post("/crew-logs")
async def create_crew_log(crew_log_data: dict):
    """Create crew log and automatically sync with T&M data"""
    try:
        # Create crew log entry
        crew_log = {
            "id": str(uuid.uuid4()),
            "project_id": crew_log_data.get("project_id"),
            "date": crew_log_data.get("date"),
            "crew_members": crew_log_data.get("crew_members", []),
            "work_description": crew_log_data.get("work_description", ""),
            "weather_conditions": crew_log_data.get("weather_conditions", "clear"),
            "expenses": crew_log_data.get("expenses", {}),
            "created_at": datetime.utcnow(),
            "synced_to_tm": False
        }
        
        # Insert crew log
        await db.crew_logs.insert_one(crew_log)
        
        # Auto-sync to T&M if project has active T&M tag for same date
        await sync_crew_log_to_tm(crew_log)
        
        return {"message": "Crew log created successfully", "id": crew_log["id"]}
        
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/crew-logs")
async def get_crew_logs(project_id: Optional[str] = None, date: Optional[str] = None):
    """Get crew logs with optional filtering"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    if date:
        query["date"] = date
        
    crew_logs = await db.crew_logs.find(query).to_list(1000)
    
    # Convert to serializable format
    serializable_logs = []
    for log in crew_logs:
        if "_id" in log:
            del log["_id"]  # Remove MongoDB ObjectId
        serializable_logs.append(log)
    
    return serializable_logs

@api_router.put("/crew-logs/{log_id}")
async def update_crew_log(log_id: str, crew_log_data: dict):
    """Update crew log and sync changes to T&M if linked"""
    try:
        crew_log_data["updated_at"] = datetime.utcnow()
        
        result = await db.crew_logs.update_one(
            {"id": log_id},
            {"$set": crew_log_data}
        )
        
        if result.modified_count == 1:
            # Re-sync to T&M tags
            updated_log = await db.crew_logs.find_one({"id": log_id})
            await sync_crew_log_to_tm(updated_log)
            
            return {"message": "Crew log updated successfully"}
        return {"error": "Crew log not found"}
        
    except Exception as e:
        return {"error": str(e)}

@api_router.delete("/crew-logs/{log_id}")
async def delete_crew_log(log_id: str):
    """Delete crew log"""
    try:
        result = await db.crew_logs.delete_one({"id": log_id})
        
        if result.deleted_count == 1:
            return {"message": "Crew log deleted successfully"}
        return {"error": "Crew log not found"}
        
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/crew-logs/{log_id}/sync")
async def manual_sync_crew_log(log_id: str):
    """Manually sync a crew log to T&M tag"""
    try:
        # Get the crew log
        crew_log = await db.crew_logs.find_one({"id": log_id})
        if not crew_log:
            raise HTTPException(status_code=404, detail="Crew log not found")
        
        # Attempt to sync
        await sync_crew_log_to_tm(crew_log)
        
        # Check if sync was successful
        updated_log = await db.crew_logs.find_one({"id": log_id})
        if updated_log and updated_log.get("synced_to_tm"):
            return {"message": "Crew log synced successfully", "tm_tag_id": updated_log.get("tm_tag_id")}
        else:
            return {"error": "Sync failed - please check if project exists and crew log has valid data"}
        
    except Exception as e:
        logger.error(f"Manual sync error for log {log_id}: {e}")
        return {"error": str(e)}

async def sync_crew_log_to_tm(crew_log):
    """Sync crew log data to T&M tags - create if doesn't exist"""
    try:
        project_id = crew_log.get("project_id")
        log_date = crew_log.get("date")
        
        logger.info(f"Starting sync for crew log {crew_log.get('id')} - Project: {project_id}, Date: {log_date}")
        
        if not project_id or not log_date:
            logger.error(f"Missing required data - project_id: {project_id}, log_date: {log_date}")
            return
            
        # Get date string for comparison
        if hasattr(log_date, 'strftime'):
            date_str = log_date.strftime('%Y-%m-%d')
        else:
            date_str = log_date.split("T")[0] if isinstance(log_date, str) else str(log_date)
            
        logger.info(f"Looking for T&M tag with project_id: {project_id}, date: {date_str}")
            
        # Check if T&M tag exists for same project and date
        # Use a safer approach that handles both string and date formats
        # First try to find by string match (most common case)
        tm_tag = await db.tm_tags.find_one({
            "project_id": project_id,
            "date_of_work": {"$regex": f"^{date_str}"}
        })
        
        # If not found, try to find by date conversion (only if no string matches exist)
        if not tm_tag:
            try:
                tm_tag = await db.tm_tags.find_one({
                    "project_id": project_id,
                    "$expr": {
                        "$eq": [
                            {"$dateToString": {"format": "%Y-%m-%d", "date": "$date_of_work"}},
                            date_str
                        ]
                    }
                })
            except Exception as date_query_error:
                logger.warning(f"Date query failed (expected for string dates): {date_query_error}")
                # This is expected when date_of_work is stored as string
        
        if tm_tag:
            logger.info(f"Found existing T&M tag: {tm_tag.get('id')}, updating with crew log data")
            # Update existing T&M tag with crew log data
            labor_entries = []
            for crew_member in crew_log.get("crew_members", []):
                labor_entry = {
                    "id": str(uuid.uuid4()),
                    "worker_name": crew_member.get("name"),
                    "quantity": 1,
                    "st_hours": float(crew_member.get("st_hours", 0)),
                    "ot_hours": float(crew_member.get("ot_hours", 0)),
                    "dt_hours": float(crew_member.get("dt_hours", 0)),
                    "pot_hours": float(crew_member.get("pot_hours", 0)),
                    "total_hours": float(crew_member.get("total_hours", 0)),
                    "date": log_date
                }
                labor_entries.append(labor_entry)
            
            # Update T&M tag with crew data
            await db.tm_tags.update_one(
                {"id": tm_tag["id"]},
                {"$set": {
                    "labor_entries": labor_entries,
                    "description_of_work": crew_log.get("work_description", tm_tag.get("description_of_work", "")),
                    "crew_log_synced": True,
                    "status": "approved"  # Auto-approve when synced from crew log
                }}
            )
            
            # Mark crew log as synced
            await db.crew_logs.update_one(
                {"id": crew_log["id"]},
                {"$set": {"synced_to_tm": True, "tm_tag_id": tm_tag["id"]}}
            )
            logger.info(f"Successfully updated existing T&M tag and marked crew log as synced")
        else:
            logger.info(f"No existing T&M tag found, creating new one")
            # Create new T&M tag from crew log data
            # Get project details for T&M tag
            project = await db.projects.find_one({"id": project_id})
            if not project:
                logger.error(f"Project not found for ID: {project_id}")
                return
                
            logger.info(f"Found project: {project.get('name')}")
            
            labor_entries = []
            for crew_member in crew_log.get("crew_members", []):
                labor_entry = {
                    "id": str(uuid.uuid4()),
                    "worker_name": crew_member.get("name"),
                    "quantity": 1,
                    "st_hours": float(crew_member.get("st_hours", 0)),
                    "ot_hours": float(crew_member.get("ot_hours", 0)),
                    "dt_hours": float(crew_member.get("dt_hours", 0)),
                    "pot_hours": float(crew_member.get("pot_hours", 0)),
                    "total_hours": float(crew_member.get("total_hours", 0)),
                    "date": log_date
                }
                labor_entries.append(labor_entry)
            
            new_tm_tag = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "project_name": project.get("name", ""),
                "cost_code": "",
                "date_of_work": log_date,
                "company_name": project.get("client_company", ""),
                "tm_tag_title": f"Auto-generated from Crew Log - {date_str}",
                "description_of_work": crew_log.get("work_description", ""),
                "labor_entries": labor_entries,
                "material_entries": [],
                "equipment_entries": [],
                "other_entries": [],
                "gc_email": project.get("gc_email", ""),
                "signature": None,
                "foreman_name": crew_log.get("crew_members", [{}])[0].get("name", "Unknown") if crew_log.get("crew_members") else "Unknown",
                "status": "pending_review",  # Needs review since auto-generated
                "created_at": datetime.now(timezone.utc),
                "submitted_at": datetime.now(timezone.utc),
                "crew_log_synced": True
            }
            
            await db.tm_tags.insert_one(new_tm_tag)
            logger.info(f"Created new T&M tag: {new_tm_tag['id']}")
            
            # Mark crew log as synced
            await db.crew_logs.update_one(
                {"id": crew_log["id"]},
                {"$set": {"synced_to_tm": True, "tm_tag_id": new_tm_tag["id"]}}
            )
            logger.info(f"Marked crew log {crew_log['id']} as synced")
            
    except Exception as e:
        logger.error(f"Error syncing crew log to T&M: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

async def sync_tm_to_crew_log(tm_tag):
    """Sync T&M tag labor data to crew logs - create if doesn't exist"""
    try:
        project_id = tm_tag.get("project_id")
        work_date = tm_tag.get("date_of_work")
        
        if not project_id or not work_date:
            return
            
        # Get date string for comparison
        if hasattr(work_date, 'strftime'):
            date_str = work_date.strftime('%Y-%m-%d')
        else:
            date_str = work_date.split("T")[0] if isinstance(work_date, str) else str(work_date)
            
        # Check if crew log exists for same project and date
        # Use a safer approach that handles both string and date formats
        # First try to find by string match (most common case)
        crew_log = await db.crew_logs.find_one({
            "project_id": project_id,
            "date": {"$regex": f"^{date_str}"}
        })
        
        # If not found, try to find by date conversion (only if no string matches exist)
        if not crew_log:
            try:
                crew_log = await db.crew_logs.find_one({
                    "project_id": project_id,
                    "$expr": {
                        "$eq": [
                            {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                            date_str
                        ]
                    }
                })
            except Exception as date_query_error:
                logger.warning(f"Date query failed (expected for string dates): {date_query_error}")
                # This is expected when date is stored as string
        
        if not crew_log:
            # Create new crew log from T&M data
            crew_members = []
            for labor_entry in tm_tag.get("labor_entries", []):
                crew_member = {
                    "name": labor_entry.get("worker_name"),
                    "st_hours": labor_entry.get("st_hours", 0),
                    "ot_hours": labor_entry.get("ot_hours", 0),
                    "dt_hours": labor_entry.get("dt_hours", 0),
                    "pot_hours": labor_entry.get("pot_hours", 0),
                    "total_hours": labor_entry.get("total_hours", 0)
                }
                crew_members.append(crew_member)
            
            new_crew_log = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "date": work_date,
                "crew_members": crew_members,
                "work_description": tm_tag.get("description_of_work", ""),
                "weather_conditions": "clear",
                "expenses": {},
                "created_at": datetime.utcnow(),
                "synced_from_tm": True,
                "tm_tag_id": tm_tag["id"],
                "synced_to_tm": True,  # Already synced since it came from T&M
                "status": "pending_review"  # Needs review since auto-generated
            }
            
            await db.crew_logs.insert_one(new_crew_log)
            
    except Exception as e:
        print(f"Error syncing T&M to crew log: {e}")

# Material Purchase Endpoints
@api_router.post("/materials", response_model=MaterialPurchase)
async def create_material_purchase(material: MaterialPurchaseCreate):
    material_dict = material.dict()
    material_obj = MaterialPurchase(**material_dict)
    
    # Insert into database
    result = await db.materials.insert_one(material_obj.dict())
    
    return material_obj

@api_router.get("/materials", response_model=List[MaterialPurchase])
async def get_materials(project_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if project_id:
        query["project_id"] = project_id
    
    materials = await db.materials.find(query).skip(skip).limit(limit).to_list(limit)
    return [MaterialPurchase(**material) for material in materials]

@api_router.get("/materials/{material_id}")
async def get_material(material_id: str):
    material = await db.materials.find_one({"id": material_id})
    if material:
        return MaterialPurchase(**material)
    return {"error": "Material purchase not found"}

@api_router.delete("/materials/{material_id}")
async def delete_material(material_id: str):
    result = await db.materials.delete_one({"id": material_id})
    if result.deleted_count == 1:
        return {"message": "Material purchase deleted successfully", "id": material_id}
    return {"error": "Material purchase not found"}

# Enhanced AI Super Tracking Endpoints

# Phase Management
@api_router.post("/phases", response_model=Phase)
async def create_phase(phase: PhaseCreate):
    phase_dict = phase.dict()
    phase_obj = Phase(**phase_dict)
    result = await db.phases.insert_one(phase_obj.dict())
    return phase_obj

@api_router.get("/phases", response_model=List[Phase])
async def get_phases(project_id: Optional[str] = None):
    query = {}
    if project_id:
        query["project_id"] = project_id
    phases = await db.phases.find(query).to_list(1000)
    return [Phase(**phase) for phase in phases]

@api_router.delete("/phases/{phase_id}")
async def delete_phase(phase_id: str):
    result = await db.phases.delete_one({"id": phase_id})
    if result.deleted_count == 1:
        return {"message": "Phase deleted successfully", "id": phase_id}
    return {"error": "Phase not found"}

# Task Management
@api_router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    task_dict = task.dict()
    task_obj = Task(**task_dict)
    result = await db.tasks.insert_one(task_obj.dict())
    return task_obj

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(project_id: Optional[str] = None, phase_id: Optional[str] = None, assigned_to: Optional[str] = None):
    query = {}
    if project_id:
        query["project_id"] = project_id
    if phase_id:
        query["phase_id"] = phase_id
    if assigned_to:
        query["assigned_to"] = assigned_to
    tasks = await db.tasks.find(query).to_list(1000)
    return [Task(**task) for task in tasks]

@api_router.put("/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskCreate):
    update_dict = task_update.dict()
    update_dict["updated_at"] = datetime.utcnow()
    result = await db.tasks.update_one({"id": task_id}, {"$set": update_dict})
    if result.modified_count == 1:
        updated_task = await db.tasks.find_one({"id": task_id})
        return Task(**updated_task)
    return {"error": "Task not found"}

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 1:
        return {"message": "Task deleted successfully", "id": task_id}
    return {"error": "Task not found"}

# Project Updates (AI-Parsed Content)
@api_router.post("/project-updates", response_model=ProjectUpdate)
async def create_project_update(update: ProjectUpdateCreate):
    update_dict = update.dict()
    update_obj = ProjectUpdate(**update_dict)
    result = await db.project_updates.insert_one(update_obj.dict())
    return update_obj

@api_router.get("/project-updates", response_model=List[ProjectUpdate])
async def get_project_updates(
    project_id: Optional[str] = None, 
    update_type: Optional[str] = None,
    requires_review: Optional[bool] = None,
    skip: int = 0, 
    limit: int = 100
):
    query = {}
    if project_id:
        query["project_id"] = project_id
    if update_type:
        query["update_type"] = update_type
    if requires_review is not None:
        query["requires_review"] = requires_review
    
    updates = await db.project_updates.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
    return [ProjectUpdate(**update) for update in updates]

@api_router.put("/project-updates/{update_id}/review")
async def review_project_update(update_id: str, reviewer: str, approved: bool = True):
    update_data = {
        "requires_review": False,
        "reviewed_at": datetime.utcnow(),
        "reviewed_by": reviewer
    }
    
    result = await db.project_updates.update_one({"id": update_id}, {"$set": update_data})
    if result.modified_count == 1:
        updated_update = await db.project_updates.find_one({"id": update_id})
        return ProjectUpdate(**updated_update)
    return {"error": "Project update not found"}

@api_router.delete("/project-updates/{update_id}")
async def delete_project_update(update_id: str):
    result = await db.project_updates.delete_one({"id": update_id})
    if result.deleted_count == 1:
        return {"message": "Project update deleted successfully", "id": update_id}
    return {"error": "Project update not found"}

# T&M Tickets (Enhanced)
@api_router.post("/tm-tickets", response_model=TMTicket)
async def create_tm_ticket(ticket: TMTicketCreate):
    ticket_dict = ticket.dict()
    # Auto-calculate cost if not provided
    if not ticket_dict.get('cost') and ticket_dict.get('hours') and ticket_dict.get('rate'):
        ticket_dict['cost'] = ticket_dict['hours'] * ticket_dict['rate']
    
    ticket_obj = TMTicket(**ticket_dict)
    result = await db.tm_tickets.insert_one(ticket_obj.dict())
    return ticket_obj

@api_router.get("/tm-tickets", response_model=List[TMTicket])
async def get_tm_tickets(
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    employee_name: Optional[str] = None,
    approved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if project_id:
        query["project_id"] = project_id
    if task_id:
        query["task_id"] = task_id
    if employee_name:
        query["employee_name"] = employee_name
    if approved is not None:
        query["approved"] = approved
    
    tickets = await db.tm_tickets.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
    return [TMTicket(**ticket) for ticket in tickets]

@api_router.put("/tm-tickets/{ticket_id}/approve")
async def approve_tm_ticket(ticket_id: str, approver: str):
    update_data = {
        "approved": True,
        "approved_by": approver,
        "approved_at": datetime.utcnow()
    }
    
    result = await db.tm_tickets.update_one({"id": ticket_id}, {"$set": update_data})
    if result.modified_count == 1:
        updated_ticket = await db.tm_tickets.find_one({"id": ticket_id})
        return TMTicket(**updated_ticket)
    return {"error": "T&M ticket not found"}

# Project Analytics with Consolidated Data
@api_router.get("/projects/{project_id}/analytics")
async def get_project_analytics(project_id: str):
    """Get comprehensive project analytics including crew logs and T&M data"""
    try:
        # Get all T&M tags for project
        tm_tags = await db.tm_tags.find({"project_id": project_id}).to_list(1000)
        
        # Get all crew logs for project
        crew_logs = await db.crew_logs.find({"project_id": project_id}).to_list(1000)
        
        # Consolidate analytics
        total_hours = 0
        total_labor_cost = 0
        total_material_cost = 0
        total_other_cost = 0
        unique_crew_members = set()
        work_days = set()
        
        # Get project details for labor rate
        project = await db.projects.find_one({"id": project_id})
        contract_amount = project.get("contract_amount", 0) if project else 0
        project_labor_rate = project.get("labor_rate", 95.0) if project else 95.0  # Use project-specific rate
        
        # Get employee data for accurate cost calculations
        employees = await db.employees.find({"status": "active"}).to_list(1000)
        employee_rates = {emp["name"]: emp.get("hourly_rate", 40) for emp in employees}  # Default to $40
        
        # Process T&M tags
        total_true_cost = 0  # True employee cost
        total_gc_billing = 0  # Amount billed to GC
        
        for tag in tm_tags:
            for labor_entry in tag.get("labor_entries", []):
                hours = float(labor_entry.get("total_hours", 0))
                worker_name = labor_entry.get("worker_name", "")
                
                total_hours += hours
                
                # Calculate true cost using employee's hourly rate
                hourly_rate = employee_rates.get(worker_name, 40)  # Default $40
                
                total_true_cost += hours * hourly_rate
                total_gc_billing += hours * project_labor_rate  # Use project-specific rate
                
                unique_crew_members.add(worker_name)
            
            for material_entry in tag.get("material_entries", []):
                total_material_cost += float(material_entry.get("total", 0))
                
            for other_entry in tag.get("other_entries", []):
                total_other_cost += float(other_entry.get("total", 0))
                
            # Handle date properly - check if it's already a string or datetime object
            work_date = tag.get("date_of_work", "")
            if hasattr(work_date, 'strftime'):  # It's a datetime object
                work_days.add(work_date.strftime('%Y-%m-%d'))
            elif isinstance(work_date, str) and work_date:
                work_days.add(work_date.split("T")[0])
        
        # Process crew logs - count ALL crew logs for comprehensive analytics
        crew_log_hours = 0
        crew_log_true_cost = 0
        crew_log_gc_billing = 0
        
        for log in crew_logs:
            crew_members = log.get("crew_members", [])
            
            # Handle different crew member formats
            if isinstance(crew_members, list):
                for crew_member in crew_members:
                    if isinstance(crew_member, dict):
                        # New format with detailed hours
                        member_hours = float(crew_member.get("total_hours", 0))
                        worker_name = crew_member.get("name", "Unknown")
                        
                        hourly_rate = employee_rates.get(worker_name, 40)  # Default $40
                        
                        crew_log_hours += member_hours
                        crew_log_true_cost += member_hours * hourly_rate
                        crew_log_gc_billing += member_hours * project_labor_rate  # Use project-specific rate
                        unique_crew_members.add(worker_name)
                    elif isinstance(crew_member, str):
                        # Old format - just names, use hours_worked from log level
                        log_hours = float(log.get("hours_worked", 0)) / len(crew_members) if crew_members else 0
                        hourly_rate = employee_rates.get(crew_member, 40)  # Default $40
                        
                        crew_log_hours += log_hours
                        crew_log_true_cost += log_hours * hourly_rate
                        crew_log_gc_billing += log_hours * project_labor_rate  # Use project-specific rate
                        unique_crew_members.add(crew_member)
            
            # Handle date properly - check if it's already a string or datetime object
            log_date = log.get("date", "")
            if hasattr(log_date, 'strftime'):  # It's a datetime object
                work_days.add(log_date.strftime('%Y-%m-%d'))
            elif isinstance(log_date, str) and log_date:
                work_days.add(log_date.split("T")[0])
        
        # Use the higher values to avoid underestimating
        total_hours = max(total_hours, crew_log_hours)
        final_true_cost = max(total_true_cost, crew_log_true_cost)
        final_gc_billing = max(total_gc_billing, crew_log_gc_billing)
        
        # Get project details
        project = await db.projects.find_one({"id": project_id})
        contract_amount = project.get("contract_amount", 0) if project else 0
        project_type = project.get("project_type", "full_project") if project else "full_project"
        
        # Get material purchases for project and add to T&M tag materials
        materials = await db.materials.find({"project_id": project_id}).to_list(1000)
        material_purchases_cost = sum(float(material.get("total_cost", 0)) for material in materials)
        total_material_cost += material_purchases_cost  # Add to existing T&M tag materials
        
        # Calculate profit based on project type
        total_project_cost = final_true_cost + total_material_cost + total_other_cost
        labor_markup_profit = final_gc_billing - final_true_cost  # Labor markup profit
        material_markup_profit = total_material_cost * 0.2  # Assume 20% markup on materials
        
        if project_type == "tm_only":
            # For T&M projects, profit is the markup profit
            total_profit = labor_markup_profit + material_markup_profit
            total_revenue = final_gc_billing + total_material_cost + total_other_cost
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        else:
            # For full projects, profit is contract amount minus true costs
            total_profit = contract_amount - total_project_cost
            profit_margin = (total_profit / contract_amount * 100) if contract_amount > 0 else 0
        
        # Get forecasted values for comparison
        estimated_hours = project.get("estimated_hours", 0) if project else 0
        estimated_labor_cost = project.get("estimated_labor_cost", 0) if project else 0
        estimated_material_cost = project.get("estimated_material_cost", 0) if project else 0
        estimated_profit = project.get("estimated_profit", 0) if project else 0
        
        return {
            "project_id": project_id,
            "project_type": project_type,
            "total_hours": total_hours,
            "total_labor_cost": final_gc_billing,  # Amount billed to GC
            "total_labor_cost_gc": final_gc_billing,
            "true_employee_cost": final_true_cost,  # Actual cost of labor
            "labor_markup_profit": labor_markup_profit,  # Profit from labor markup
            "material_markup_profit": material_markup_profit,  # Profit from material markup
            "total_material_cost": total_material_cost,
            "total_other_cost": total_other_cost,
            "total_cost": final_gc_billing + total_material_cost + total_other_cost,
            "contract_amount": contract_amount,
            "total_crew_expenses": total_other_cost,
            "profit": total_profit,
            "profit_margin": profit_margin,
            # Forecasted vs Actual comparisons
            "estimated_hours": estimated_hours,
            "estimated_labor_cost": estimated_labor_cost,
            "estimated_material_cost": estimated_material_cost,
            "estimated_profit": estimated_profit,
            "hours_variance": total_hours - estimated_hours if estimated_hours > 0 else 0,
            "labor_cost_variance": final_gc_billing - estimated_labor_cost if estimated_labor_cost > 0 else 0,
            "material_cost_variance": total_material_cost - estimated_material_cost if estimated_material_cost > 0 else 0,
            "profit_variance": total_profit - estimated_profit if estimated_profit != 0 else 0,
            # Other metrics
            "unique_crew_members": len(unique_crew_members),
            "work_days": len(work_days),
            "crew_members_list": list(unique_crew_members),
            "tm_tags_count": len(tm_tags),
            "tm_tag_count": len(tm_tags),
            "crew_logs_count": len(crew_logs),
            "crew_log_count": len(crew_logs),
            "material_purchase_count": len(materials)
        }
        
    except Exception as e:
        return {"error": str(e)}

# Endpoint to get daily crew data for auto-population
@api_router.get("/daily-crew-data")
async def get_daily_crew_data(project_id: str, date: str):
    """Get existing crew data for a specific project and date for auto-population"""
    try:
        # Check crew logs first
        crew_log = await db.crew_logs.find_one({
            "project_id": project_id,
            "date": {"$regex": date}
        })
        
        if crew_log:
            return {
                "source": "crew_log",
                "data": crew_log,
                "crew_members": crew_log.get("crew_members", []),
                "work_description": crew_log.get("work_description", "")
            }
        
        # Check T&M tags
        tm_tag = await db.tm_tags.find_one({
            "project_id": project_id,
            "date_of_work": {"$regex": date}
        })
        
        if tm_tag:
            # Convert labor entries to crew member format
            crew_members = []
            for labor_entry in tm_tag.get("labor_entries", []):
                crew_member = {
                    "name": labor_entry.get("worker_name"),
                    "st_hours": labor_entry.get("st_hours", 0),
                    "ot_hours": labor_entry.get("ot_hours", 0),
                    "dt_hours": labor_entry.get("dt_hours", 0),
                    "pot_hours": labor_entry.get("pot_hours", 0),
                    "total_hours": labor_entry.get("total_hours", 0)
                }
                crew_members.append(crew_member)
            
            return {
                "source": "tm_tag",
                "data": tm_tag,
                "crew_members": crew_members,
                "work_description": tm_tag.get("description_of_work", "")
            }
        
        return {"source": None, "data": None, "crew_members": [], "work_description": ""}
        
    except Exception as e:
        return {"error": str(e)}

# AI Email Parsing Endpoint (will be called by n8n or direct integration)
@api_router.post("/ai/parse-email")
async def parse_email_content(
    email_subject: str,
    email_body: str,
    sender_email: str,
    email_id: Optional[str] = None,
    project_hint: Optional[str] = None
):
    """
    AI-powered email parsing endpoint
    This will be called by n8n workflows or direct email integration
    """
    try:
        # This is where we'll integrate with LLM for parsing
        # For now, return a placeholder structure
        
        parsed_data = {
            "project_id": project_hint or "unknown",
            "update_type": "communication",
            "title": email_subject,
            "summary": f"Email from {sender_email}: {email_subject}",
            "full_content": email_body,
            "ai_confidence": 0.8,
            "requires_review": True,
            "tags": ["email", "communication"],
            "extracted_data": {
                "sender": sender_email,
                "subject": email_subject,
                "detected_project": project_hint or "unknown"
            }
        }
        
        # Create project update from parsed email
        update = ProjectUpdateCreate(**parsed_data)
        result = await create_project_update(update)
        
        return {
            "success": True,
            "message": "Email parsed and project update created",
            "update_id": result.id,
            "requires_review": result.requires_review
        }
        
    except Exception as e:
        logger.error(f"Error parsing email: {str(e)}")
        return {"success": False, "error": str(e)}

# Email Endpoint
@api_router.post("/send-email")
async def send_email(email_request: EmailRequest):
    try:
        # Get email configuration from environment
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        
        if not smtp_username or not smtp_password:
            return {"error": "Email configuration not set up"}
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_request.to_email
        if email_request.cc_email:
            msg['Cc'] = email_request.cc_email
        msg['Subject'] = email_request.subject
        
        # Add body
        msg.attach(MIMEText(email_request.message, 'plain'))
        
        # Add PDF attachment
        if email_request.pdf_data:
            # Decode base64 PDF
            pdf_data = base64.b64decode(email_request.pdf_data.split(',')[1] if ',' in email_request.pdf_data else email_request.pdf_data)
            
            # Create attachment
            pdf_attachment = MIMEBase('application', 'octet-stream')
            pdf_attachment.set_payload(pdf_data)
            encoders.encode_base64(pdf_attachment)
            
            # Generate filename
            tm_tag = await db.tm_tags.find_one({"id": email_request.tm_tag_id})
            date_str = tm_tag['date_of_work'][:10] if tm_tag else datetime.utcnow().strftime('%Y-%m-%d')
            filename = f"TM_Tag_{date_str}.pdf"
            
            pdf_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(pdf_attachment)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        recipients = [email_request.to_email]
        if email_request.cc_email:
            recipients.append(email_request.cc_email)
            
        server.sendmail(smtp_username, recipients, msg.as_string())
        server.quit()
        
        # Log the email
        email_log = {
            "id": str(uuid.uuid4()),
            "to_email": email_request.to_email,
            "cc_email": email_request.cc_email,
            "subject": email_request.subject,
            "tm_tag_id": email_request.tm_tag_id,
            "sent_at": datetime.utcnow(),
            "status": "sent"
        }
        await db.email_logs.insert_one(email_log)
        
        return {"message": "Email sent successfully", "status": "sent"}
        
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return {"error": f"Failed to send email: {str(e)}"}

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    """Convert MongoDB document to serializable format"""
    if doc is None:
        return None
    if "_id" in doc:
        del doc["_id"]
    return doc

def generate_project_pin():
    """Generate a unique 4-digit PIN for project access"""
    return f"{random.randint(1000, 9999)}"

async def ensure_project_has_pin(project_id: str):
    """Ensure project has a GC access PIN, generate if missing"""
    try:
        project = await db.projects.find_one({"id": project_id})
        if not project:
            return None
            
        # Check if project has a PIN
        if not project.get("gc_pin"):
            # Generate new PIN
            new_pin = generate_project_pin()
            
            # Make sure PIN is unique across all projects
            while await db.projects.find_one({"gc_pin": new_pin}):
                new_pin = generate_project_pin()
            
            # Update project with new PIN
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {"gc_pin": new_pin, "gc_pin_used": False}}
            )
            
            logger.info(f"Generated new PIN for project {project_id}: {new_pin}")
            return new_pin
        
        return project.get("gc_pin")
        
    except Exception as e:
        logger.error(f"Error ensuring project PIN: {e}")
        return None

# FINANCIAL MANAGEMENT ENDPOINTS

# INVOICES API ROUTES
@api_router.get("/invoices/{project_id}", response_model=List[Invoice])
async def get_invoices_by_project(project_id: str):
    """Fetch all invoices for a project"""
    try:
        invoices = await invoices_collection.find({"project_id": project_id}).to_list(1000)
        return [Invoice(**serialize_doc(invoice)) for invoice in invoices]
    except Exception as e:
        logger.error(f"Error fetching invoices for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate):
    """Create new invoice"""
    try:
        invoice_dict = invoice.dict()
        invoice_obj = Invoice(**invoice_dict)
        
        result = await invoices_collection.insert_one(invoice_obj.dict())
        logger.info(f"Created invoice: {invoice_obj.invoice_number}")
        
        return invoice_obj
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_invoice(invoice_id: str, invoice_update: InvoiceUpdate):
    """Update invoice"""
    try:
        update_dict = {k: v for k, v in invoice_update.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await invoices_collection.update_one(
            {"id": invoice_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        updated_invoice = await invoices_collection.find_one({"id": invoice_id})
        return Invoice(**serialize_doc(updated_invoice))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    """Delete invoice"""
    try:
        result = await invoices_collection.delete_one({"id": invoice_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {"message": "Invoice deleted successfully", "id": invoice_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PAYABLES API ROUTES
@api_router.get("/payables/{project_id}", response_model=List[Payable])
async def get_payables_by_project(project_id: str):
    """Fetch all payables for a project"""
    try:
        payables = await payables_collection.find({"project_id": project_id}).to_list(1000)
        return [Payable(**serialize_doc(payable)) for payable in payables]
    except Exception as e:
        logger.error(f"Error fetching payables for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/payables", response_model=Payable)
async def create_payable(payable: PayableCreate):
    """Create payable"""
    try:
        payable_dict = payable.dict()
        payable_obj = Payable(**payable_dict)
        
        result = await payables_collection.insert_one(payable_obj.dict())
        logger.info(f"Created payable: {payable_obj.description}")
        
        return payable_obj
    except Exception as e:
        logger.error(f"Error creating payable: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/payables/{payable_id}", response_model=Payable)
async def update_payable(payable_id: str, payable_update: PayableUpdate):
    """Update payable"""
    try:
        update_dict = {k: v for k, v in payable_update.dict().items() if v is not None}
        
        result = await payables_collection.update_one(
            {"id": payable_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Payable not found")
        
        updated_payable = await payables_collection.find_one({"id": payable_id})
        return Payable(**serialize_doc(updated_payable))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payable {payable_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/payables/{payable_id}")
async def delete_payable(payable_id: str):
    """Delete payable"""
    try:
        result = await payables_collection.delete_one({"id": payable_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Payable not found")
        
        return {"message": "Payable deleted successfully", "id": payable_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting payable {payable_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CASHFLOW API ROUTES
@api_router.get("/cashflow/{project_id}", response_model=List[CashflowForecast])
async def get_cashflow_by_project(project_id: str):
    """Fetch cashflow forecast for a project"""
    try:
        forecasts = await cashflow_forecasts_collection.find({"project_id": project_id}).to_list(1000)
        return [CashflowForecast(**serialize_doc(forecast)) for forecast in forecasts]
    except Exception as e:
        logger.error(f"Error fetching cashflow for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/cashflow", response_model=CashflowForecast)
async def create_cashflow_forecast(forecast: CashflowForecastCreate):
    """Create forecast entry"""
    try:
        forecast_dict = forecast.dict()
        forecast_obj = CashflowForecast(**forecast_dict)
        
        result = await cashflow_forecasts_collection.insert_one(forecast_obj.dict())
        logger.info(f"Created cashflow forecast for project {forecast_obj.project_id}")
        
        return forecast_obj
    except Exception as e:
        logger.error(f"Error creating cashflow forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/cashflow/{forecast_id}", response_model=CashflowForecast)
async def update_cashflow_forecast(forecast_id: str, forecast_update: CashflowForecastUpdate):
    """Update forecast"""
    try:
        update_dict = {k: v for k, v in forecast_update.dict().items() if v is not None}
        
        result = await cashflow_forecasts_collection.update_one(
            {"id": forecast_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        updated_forecast = await cashflow_forecasts_collection.find_one({"id": forecast_id})
        return CashflowForecast(**serialize_doc(updated_forecast))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating forecast {forecast_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/cashflow/{forecast_id}")
async def delete_cashflow_forecast(forecast_id: str):
    """Delete forecast"""
    try:
        result = await cashflow_forecasts_collection.delete_one({"id": forecast_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        return {"message": "Forecast deleted successfully", "id": forecast_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting forecast {forecast_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PROFITABILITY API ROUTES
@api_router.get("/profitability/{project_id}", response_model=List[Profitability])
async def get_profitability_by_project(project_id: str):
    """Fetch profitability data for a project"""
    try:
        profitability_data = await profitability_collection.find({"project_id": project_id}).to_list(1000)
        return [Profitability(**serialize_doc(data)) for data in profitability_data]
    except Exception as e:
        logger.error(f"Error fetching profitability for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/profitability", response_model=Profitability)
async def create_profitability_entry(profitability: ProfitabilityCreate):
    """Create profitability entry"""
    try:
        profitability_dict = profitability.dict()
        profitability_obj = Profitability(**profitability_dict)
        
        result = await profitability_collection.insert_one(profitability_obj.dict())
        logger.info(f"Created profitability entry for project {profitability_obj.project_id}")
        
        return profitability_obj
    except Exception as e:
        logger.error(f"Error creating profitability entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/profitability/{profitability_id}", response_model=Profitability)
async def update_profitability_entry(profitability_id: str, profitability_update: ProfitabilityUpdate):
    """Update profitability"""
    try:
        update_dict = {k: v for k, v in profitability_update.dict().items() if v is not None}
        
        result = await profitability_collection.update_one(
            {"id": profitability_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Profitability entry not found")
        
        updated_profitability = await profitability_collection.find_one({"id": profitability_id})
        return Profitability(**serialize_doc(updated_profitability))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profitability {profitability_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/profitability/{profitability_id}")
async def delete_profitability_entry(profitability_id: str):
    """Delete profitability"""
    try:
        result = await profitability_collection.delete_one({"id": profitability_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Profitability entry not found")
        
        return {"message": "Profitability entry deleted successfully", "id": profitability_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profitability {profitability_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# INSPECTIONS API ROUTES
@api_router.get("/inspections/{project_id}", response_model=List[Inspection])
async def get_inspections_by_project(project_id: str):
    """Fetch all inspections for a project"""
    try:
        inspections = await inspections_collection.find({"project_id": project_id}).to_list(1000)
        return [Inspection(**serialize_doc(inspection)) for inspection in inspections]
    except Exception as e:
        logger.error(f"Error fetching inspections for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/inspections", response_model=Inspection)
async def create_inspection(inspection: InspectionCreate):
    """Add a new inspection record"""
    try:
        inspection_dict = inspection.dict()
        inspection_obj = Inspection(**inspection_dict)
        
        result = await inspections_collection.insert_one(inspection_obj.dict())
        logger.info(f"Created inspection: {inspection_obj.inspection_type} for project {inspection_obj.project_id}")
        
        return inspection_obj
    except Exception as e:
        logger.error(f"Error creating inspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/inspections/{inspection_id}", response_model=Inspection)
async def update_inspection(inspection_id: str, inspection_update: InspectionUpdate):
    """Update inspection (status/notes/date)"""
    try:
        update_dict = {k: v for k, v in inspection_update.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await inspections_collection.update_one(
            {"id": inspection_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Inspection not found")
        
        updated_inspection = await inspections_collection.find_one({"id": inspection_id})
        return Inspection(**serialize_doc(updated_inspection))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating inspection {inspection_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/inspections/{inspection_id}")
async def delete_inspection(inspection_id: str):
    """Delete inspection"""
    try:
        result = await inspections_collection.delete_one({"id": inspection_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Inspection not found")
        
        return {"message": "Inspection deleted successfully", "id": inspection_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting inspection {inspection_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GC DASHBOARD API ROUTES - SIMPLIFIED PIN SYSTEM

@api_router.get("/projects/{project_id}/gc-pin")
async def get_project_gc_pin(project_id: str):
    """Admin: Get current GC PIN for project"""
    try:
        pin = await ensure_project_has_pin(project_id)
        if pin:
            project = await db.projects.find_one({"id": project_id})
            return {
                "projectId": project_id,
                "projectName": project.get("name", "Unknown Project"),
                "gcPin": pin,
                "pinUsed": project.get("gc_pin_used", False)
            }
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project GC PIN: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/gc/login-simple")
async def gc_login_simple(login_data: dict):
    """GC: Simple login with project ID and PIN"""
    try:
        project_id = login_data.get("projectId")
        pin = login_data.get("pin")
        ip = login_data.get("ip", "unknown")
        
        if not project_id or not pin:
            raise HTTPException(status_code=400, detail="Project ID and PIN required")
        
        # Find project with matching PIN
        project = await db.projects.find_one({
            "id": project_id,
            "gc_pin": pin,
            "gc_pin_used": False
        })
        
        if not project:
            # Log failed access
            await gc_access_logs_collection.insert_one({
                "id": str(uuid.uuid4()),
                "projectId": project_id,
                "timestamp": datetime.now(timezone.utc),
                "ip": ip,
                "status": "failed",
                "userAgent": login_data.get("userAgent", ""),
                "failureReason": "Invalid PIN or PIN already used"
            })
            raise HTTPException(status_code=401, detail="Invalid PIN or PIN already used")
        
        # Mark PIN as used and generate new one
        new_pin = generate_project_pin()
        
        # Ensure new PIN is unique
        while await db.projects.find_one({"gc_pin": new_pin}):
            new_pin = generate_project_pin()
        
        # Update project with new PIN
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "gc_pin": new_pin,
                "gc_pin_used": False,
                "gc_last_access": datetime.now(timezone.utc),
                "gc_last_ip": ip
            }}
        )
        
        # Log successful access
        await gc_access_logs_collection.insert_one({
            "id": str(uuid.uuid4()),
            "projectId": project_id,
            "timestamp": datetime.now(timezone.utc),
            "ip": ip,
            "status": "success",
            "userAgent": login_data.get("userAgent", ""),
            "usedPin": pin,
            "newPin": new_pin
        })
        
        logger.info(f"GC login successful for project {project_id}. Old PIN: {pin}, New PIN: {new_pin}")
        
        return {
            "success": True,
            "projectId": project_id,
            "projectName": project.get("name", "Unknown Project"),
            "message": "Login successful",
            "newPin": new_pin  # Admin can see the new PIN
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during GC login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gc/dashboard/{project_id}", response_model=GcProjectDashboard)
async def get_gc_dashboard(project_id: str):
    """GC: Get project dashboard (no financial data)"""
    try:
        # Get project info
        project = await db.projects.find_one({"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get project phases
        phases = await project_phases_collection.find({"projectId": project_id}).to_list(100)
        phase_models = [ProjectPhaseModel(**serialize_doc(phase)) for phase in phases]
        
        # Calculate overall progress
        total_progress = sum(phase.get("percentComplete", 0) for phase in phases)
        overall_progress = total_progress / len(phases) if phases else 0
        
        # Get crew summary (hours and days only, no costs)
        crew_logs = await db.crew_logs.find({"project_id": project_id}).to_list(1000)
        total_hours = sum(log.get("hours_worked", 0) for log in crew_logs)
        unique_dates = set(log.get("date", "").split("T")[0] for log in crew_logs if log.get("date"))
        total_days = len(unique_dates)
        recent_descriptions = [log.get("work_description", "") for log in crew_logs[-5:] if log.get("work_description")]
        
        # Get unique crew members
        all_crew_members = []
        for log in crew_logs:
            if log.get("crew_members"):
                all_crew_members.extend([member.get("name") for member in log["crew_members"] if member.get("name")])
        active_crew_members = len(set(all_crew_members))
        
        crew_summary = GcCrewSummary(
            totalHours=total_hours,
            totalDays=total_days,
            recentDescriptions=recent_descriptions,
            activeCrewMembers=active_crew_members
        )
        
        # Get materials summary (quantities only, no costs)
        materials = await db.materials.find({"project_id": project_id}).to_list(1000)
        material_summaries = [
            GcMaterialSummary(
                date=material.get("purchase_date", datetime.now(timezone.utc)),
                vendor=material.get("vendor", "Unknown"),
                item=material.get("material_name", "Material"),
                quantity=material.get("quantity", 0),
                description=material.get("description")
            )
            for material in materials
        ]
        
        # Get T&M tag summary (counts and hours only, no dollars)
        tm_tags = await db.tm_tags.find({"project_id": project_id}).to_list(1000)
        total_tags = len(tm_tags)
        submitted_tags = len([tag for tag in tm_tags if tag.get("status") in ["submitted", "approved"]])
        approved_tags = len([tag for tag in tm_tags if tag.get("status") == "approved"])
        
        # Calculate total hours from T&M tags
        tm_total_hours = 0
        for tag in tm_tags:
            labor_entries = tag.get("labor_entries", [])
            for entry in labor_entries:
                tm_total_hours += entry.get("total_hours", 0)
        
        recent_tag_titles = [tag.get("tm_tag_title", "") for tag in tm_tags[-5:] if tag.get("tm_tag_title")]
        
        tm_tag_summary = GcTmTagSummary(
            totalTags=total_tags,
            submittedTags=submitted_tags,
            approvedTags=approved_tags,
            totalHours=tm_total_hours,
            recentTagTitles=recent_tag_titles
        )
        
        # Get inspections
        inspections = await inspection_status_collection.find({"projectId": project_id}).to_list(100)
        inspection_models = [InspectionStatusModel(**serialize_doc(inspection)) for inspection in inspections]
        
        # Get narrative
        latest_narrative = await gc_narratives_collection.find_one(
            {"projectId": project_id},
            sort=[("generatedAt", -1)]
        )
        narrative_text = latest_narrative.get("narrative") if latest_narrative else None
        
        dashboard = GcProjectDashboard(
            projectId=project_id,
            projectName=project.get("name", "Unknown Project"),
            projectLocation=project.get("address"),
            projectStatus=project.get("status", "active"),
            overallProgress=overall_progress,
            phases=phase_models,
            crewSummary=crew_summary,
            materials=material_summaries,
            tmTagSummary=tm_tag_summary,
            inspections=inspection_models,
            narrative=narrative_text,
            lastUpdated=datetime.now(timezone.utc)
        )
        
        return dashboard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching GC dashboard for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gc/access-logs/admin", response_model=List[GcAccessLogAdmin])
async def get_gc_access_logs_admin():
    """Admin: Get all GC access logs"""
    try:
        logs = await gc_access_logs_collection.find({}).sort("timestamp", -1).to_list(1000)
        admin_logs = []
        
        for log in logs:
            # Get project and key info
            project = await db.projects.find_one({"id": log["projectId"]})
            project_name = project.get("name", "Unknown Project") if project else "Unknown Project"
            
            gc_key = await gc_keys_collection.find_one({"id": log["gcKeyId"]})
            key_last_four = gc_key["key"][-4:] if gc_key else "****"
            
            admin_log = GcAccessLogAdmin(
                id=log["id"],
                projectName=project_name,
                keyLastFour=key_last_four,
                timestamp=log["timestamp"],
                ip=log["ip"],
                status=log["status"],
                userAgent=log.get("userAgent")
            )
            admin_logs.append(admin_log)
        
        return admin_logs
    except Exception as e:
        logger.error(f"Error fetching admin access logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PROJECT PHASES API ROUTES
@api_router.post("/project-phases", response_model=ProjectPhaseModel)
async def create_project_phase(phase: ProjectPhaseCreate):
    """Create project phase"""
    try:
        phase_dict = phase.dict()
        phase_obj = ProjectPhaseModel(**phase_dict)
        
        result = await project_phases_collection.insert_one(phase_obj.dict())
        logger.info(f"Created project phase: {phase_obj.phase} for project {phase_obj.projectId}")
        
        return phase_obj
    except Exception as e:
        logger.error(f"Error creating project phase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/project-phases/{project_id}", response_model=List[ProjectPhaseModel])
async def get_project_phases(project_id: str):
    """Get project phases"""
    try:
        phases = await project_phases_collection.find({"projectId": project_id}).to_list(100)
        return [ProjectPhaseModel(**serialize_doc(phase)) for phase in phases]
    except Exception as e:
        logger.error(f"Error fetching project phases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/project-phases/{phase_id}", response_model=ProjectPhaseModel)
async def update_project_phase(phase_id: str, phase_update: ProjectPhaseUpdate):
    """Update project phase"""
    try:
        update_dict = {k: v for k, v in phase_update.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await project_phases_collection.update_one(
            {"id": phase_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Project phase not found")
        
        updated_phase = await project_phases_collection.find_one({"id": phase_id})
        return ProjectPhaseModel(**serialize_doc(updated_phase))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project phase {phase_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GC NARRATIVES API ROUTES
@api_router.post("/gc-narratives", response_model=GcNarrative)
async def create_gc_narrative(narrative: GcNarrativeCreate):
    """Create GC narrative"""
    try:
        narrative_dict = narrative.dict()
        narrative_obj = GcNarrative(**narrative_dict)
        
        result = await gc_narratives_collection.insert_one(narrative_obj.dict())
        logger.info(f"Created GC narrative for project {narrative_obj.projectId}")
        
        return narrative_obj
    except Exception as e:
        logger.error(f"Error creating GC narrative: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gc-narratives/{project_id}")
async def get_latest_gc_narrative(project_id: str):
    """Get latest GC narrative for project"""
    try:
        narrative = await gc_narratives_collection.find_one(
            {"projectId": project_id},
            sort=[("generatedAt", -1)]
        )
        
        if not narrative:
            return {"projectId": project_id, "narrative": None}
        
        return GcNarrative(**serialize_doc(narrative))
    except Exception as e:
        logger.error(f"Error fetching GC narrative: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Include the router in the main app (MUST be after all endpoints are defined)
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
