from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
    contract_amount: Optional[float] = 0
    project_manager: str = "Jesus Garcia"
    status: str = "active"  # active, completed, on_hold, cancelled
    start_date: datetime
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    address: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    client_company: str
    gc_email: str
    contract_amount: Optional[float] = 0
    project_manager: Optional[str] = "Jesus Garcia"
    start_date: datetime
    estimated_completion: Optional[datetime] = None
    address: Optional[str] = ""

class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    base_pay: float  # Base hourly rate
    burden_cost: float  # Additional costs (benefits, taxes, etc.)
    position: str
    hire_date: datetime
    status: str = "active"  # active, inactive, terminated
    phone: Optional[str] = ""
    email: Optional[str] = ""
    emergency_contact: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmployeeCreate(BaseModel):
    name: str
    base_pay: float
    burden_cost: float
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
@api_router.post("/tm-tags", response_model=TMTag)
async def create_tm_tag(tm_tag: TMTagCreate):
    tm_tag_dict = tm_tag.dict()
    tm_tag_obj = TMTag(**tm_tag_dict)
    tm_tag_obj.submitted_at = datetime.utcnow()
    
    # Insert into database
    result = await db.tm_tags.insert_one(tm_tag_obj.dict())
    
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
    return [Employee(**employee) for employee in employees]

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

# Crew Log Endpoints
@api_router.post("/crew-logs", response_model=CrewLog)
async def create_crew_log(crew_log: CrewLogCreate):
    crew_log_dict = crew_log.dict()
    crew_log_obj = CrewLog(**crew_log_dict)
    
    # Insert into database
    result = await db.crew_logs.insert_one(crew_log_obj.dict())
    
    return crew_log_obj

@api_router.get("/crew-logs", response_model=List[CrewLog])
async def get_crew_logs(project_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if project_id:
        query["project_id"] = project_id
    
    crew_logs = await db.crew_logs.find(query).skip(skip).limit(limit).to_list(limit)
    return [CrewLog(**crew_log) for crew_log in crew_logs]

@api_router.get("/crew-logs/{log_id}")
async def get_crew_log(log_id: str):
    crew_log = await db.crew_logs.find_one({"id": log_id})
    if crew_log:
        return CrewLog(**crew_log)
    return {"error": "Crew log not found"}

@api_router.delete("/crew-logs/{log_id}")
async def delete_crew_log(log_id: str):
    result = await db.crew_logs.delete_one({"id": log_id})
    if result.deleted_count == 1:
        return {"message": "Crew log deleted successfully", "id": log_id}
    return {"error": "Crew log not found"}

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

# Project Analytics Endpoints
@api_router.get("/projects/{project_id}/analytics")
async def get_project_analytics(project_id: str):
    try:
        # Get project details
        project = await db.projects.find_one({"id": project_id})
        if not project:
            return {"error": "Project not found"}
        
        # Get T&M tags for this project
        tm_tags = await db.tm_tags.find({"project_name": project["name"]}).to_list(1000)
        
        # Get crew logs for this project
        crew_logs = await db.crew_logs.find({"project_id": project_id}).to_list(1000)
        
        # Get materials for this project
        materials = await db.materials.find({"project_id": project_id}).to_list(1000)
        
        # Get employees for cost calculations
        employees = await db.employees.find({"status": "active"}).to_list(1000)
        
        # Calculate analytics
        total_hours = sum(
            sum(entry.get("total_hours", 0) for entry in tag.get("labor_entries", []))
            for tag in tm_tags
        )
        
        total_labor_cost_gc = total_hours * 95  # GC rate
        
        total_material_cost = sum(material.get("total_cost", 0) for material in materials)
        
        total_crew_expenses = sum(
            log.get("per_diem", 0) + log.get("hotel_cost", 0) + 
            log.get("gas_expense", 0) + log.get("other_expenses", 0)
            for log in crew_logs
        )
        
        # Calculate true employee costs
        employee_dict = {emp["name"]: emp for emp in employees}
        true_employee_cost = 0
        
        for tag in tm_tags:
            for entry in tag.get("labor_entries", []):
                worker_name = entry.get("worker_name", "")
                hours = entry.get("total_hours", 0)
                
                if worker_name in employee_dict:
                    emp = employee_dict[worker_name]
                    true_cost_per_hour = emp.get("base_pay", 50) + emp.get("burden_cost", 20)
                    true_employee_cost += hours * true_cost_per_hour
                else:
                    # Default cost if employee not found
                    true_employee_cost += hours * 70
        
        # Calculate profit
        total_revenue = total_labor_cost_gc + (total_material_cost * 1.2)  # 20% material markup assumed
        total_costs = true_employee_cost + total_material_cost + total_crew_expenses
        profit = total_revenue - total_costs
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "project_id": project_id,
            "project_name": project["name"],
            "total_hours": total_hours,
            "total_labor_cost_gc": total_labor_cost_gc,
            "total_material_cost": total_material_cost,
            "total_crew_expenses": total_crew_expenses,
            "true_employee_cost": true_employee_cost,
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "profit": profit,
            "profit_margin": profit_margin,
            "contract_amount": project.get("contract_amount", 0),
            "tm_tag_count": len(tm_tags),
            "crew_log_count": len(crew_logs),
            "material_purchase_count": len(materials)
        }
        
    except Exception as e:
        logger.error(f"Error calculating project analytics: {str(e)}")
        return {"error": f"Failed to calculate analytics: {str(e)}"}

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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
