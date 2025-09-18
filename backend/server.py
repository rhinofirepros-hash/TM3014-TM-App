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

@api_router.get("/tm-tags/{tm_tag_id}", response_model=TMTag)
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
