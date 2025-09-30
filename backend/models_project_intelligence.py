"""
Project Intelligence System Models
Enhanced models for comprehensive project management with LLM integration
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import date as Date, datetime as DateTime
import uuid

# =============================================================================
# EMAIL & DOCUMENT PROCESSING MODELS
# =============================================================================

class InboundEmail(BaseModel):
    """Email received for processing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = Field("outlook", description="Email provider")
    provider_id: str = Field(..., description="Graph message id")
    internet_message_id: str = Field(..., description="RFC822 id (stable for dedupe)")
    from_addr: str = Field(..., description="Sender email address")
    to_addr: List[str] = Field(default_factory=list, description="Recipient email addresses")
    subject: str = Field(..., description="Email subject")
    snippet: str = Field(..., description="Email preview text")
    body: str = Field(..., description="Full email body")
    received_at: DateTime = Field(..., description="When email was received")
    web_link: Optional[str] = Field(None, description="Outlook web link")
    classified_as: Optional[str] = Field(None, description="LLM classification")
    confidence: Optional[float] = Field(None, description="Classification confidence")
    raw_ref: Dict[str, Any] = Field(default_factory=dict, description="Raw email data")
    processed: bool = Field(False, description="Whether email has been processed")
    created_at: DateTime = Field(default_factory=DateTime.now)

class InboundEmailCreate(BaseModel):
    subject: str
    body: str
    from_addr: str = "unknown@example.com"
    to_addr: List[str] = []
    snippet: Optional[str] = None
    provider_id: Optional[str] = None
    internet_message_id: Optional[str] = None
    received_at: Optional[DateTime] = None
    web_link: Optional[str] = None

class EmailAttachment(BaseModel):
    """Email attachment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email_id: str = Field(..., description="Parent email ID")
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    storage_url: Optional[str] = Field(None, description="Storage location")
    text_ocr: Optional[str] = Field(None, description="OCR extracted text")
    created_at: DateTime = Field(default_factory=DateTime.now)

# =============================================================================
# PROJECT INTELLIGENCE MODELS
# =============================================================================

class ProjectCandidate(BaseModel):
    """Potential project extracted from email"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email_id: str = Field(..., description="Source email ID")
    name: str = Field(..., description="Project name")
    billing_type: Literal["TM", "SOV", "Fixed", "Bid"] = Field(..., description="Project billing type")
    tm_bill_rate: Optional[float] = Field(None, description="T&M billing rate if applicable")
    description: Optional[str] = Field(None, description="Project description")
    client_company: Optional[str] = Field(None, description="Client company name")
    project_manager: Optional[str] = Field(None, description="Project manager")
    address: Optional[str] = Field(None, description="Full project address")
    city: Optional[str] = Field(None, description="Project city")
    state: Optional[str] = Field(None, description="Project state")
    zip_code: Optional[str] = Field(None, description="Project ZIP code")
    ahj: Optional[str] = Field(None, description="Authority Having Jurisdiction")
    links: List[str] = Field(default_factory=list, description="Related links")
    due_date: Optional[Date] = Field(None, description="Project due date")
    confidence: float = Field(..., description="Extraction confidence")
    status: str = Field("pending_review", description="Candidate status")
    created_at: DateTime = Field(default_factory=DateTime.now)

class Task(BaseModel):
    """Project task/action item"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = Field(..., description="Associated project ID")
    type: str = Field(..., description="Task type (submittals, permits, inspection, etc.)")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field("open", description="Task status")
    priority: Literal["low", "medium", "high", "urgent"] = Field("medium", description="Task priority")
    due_date: Optional[Date] = Field(None, description="Task due date")
    assigned_to: Optional[str] = Field(None, description="Assigned person/role")
    source_email_id: Optional[str] = Field(None, description="Originating email ID")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")
    created_at: DateTime = Field(default_factory=DateTime.now)
    completed_at: Optional[DateTime] = Field(None, description="Task completion timestamp")

class TaskCreate(BaseModel):
    project_id: str
    type: str
    title: str
    description: Optional[str] = None
    status: str = "open"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    due_date: Optional[Date] = None
    assigned_to: Optional[str] = None
    source_email_id: Optional[str] = None
    meta: Dict[str, Any] = {}

# =============================================================================
# INVOICE & PAYMENT TRACKING
# =============================================================================

class Invoice(BaseModel):
    """Invoice tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = Field(..., description="Associated project ID")
    invoice_number: str = Field(..., description="Invoice number")
    invoice_date: Date = Field(..., description="Invoice date")
    due_date: Optional[Date] = Field(None, description="Payment due date")
    amount: float = Field(..., description="Invoice amount")
    description: Optional[str] = Field(None, description="Invoice description")
    status: Literal["draft", "sent", "paid", "overdue", "disputed"] = Field("draft", description="Invoice status")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    client_po_number: Optional[str] = Field(None, description="Client PO number")
    source_email_id: Optional[str] = Field(None, description="Source email if auto-created")
    paid_date: Optional[Date] = Field(None, description="Date payment was received")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: DateTime = Field(default_factory=DateTime.now)

class InvoiceCreate(BaseModel):
    project_id: str
    invoice_number: str
    invoice_date: Date
    amount: float
    due_date: Optional[Date] = None
    description: Optional[str] = None
    status: Literal["draft", "sent", "paid", "overdue", "disputed"] = "draft"
    payment_terms: Optional[str] = None
    client_po_number: Optional[str] = None
    source_email_id: Optional[str] = None
    notes: Optional[str] = None

# =============================================================================
# PROJECT PROGRESS TRACKING
# =============================================================================

class ProjectProgress(BaseModel):
    """Project progress tracking entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = Field(..., description="Associated project ID")
    milestone: str = Field(..., description="Milestone/phase name")
    status: Literal["not_started", "in_progress", "completed", "on_hold", "cancelled"] = Field("not_started")
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Completion percentage")
    start_date: Optional[Date] = Field(None, description="Milestone start date")
    target_date: Optional[Date] = Field(None, description="Target completion date")
    actual_date: Optional[Date] = Field(None, description="Actual completion date")
    notes: Optional[str] = Field(None, description="Progress notes")
    source_email_id: Optional[str] = Field(None, description="Email that triggered update")
    updated_by: Optional[str] = Field(None, description="Who updated the progress")
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

class ProjectProgressCreate(BaseModel):
    project_id: str
    milestone: str
    status: Literal["not_started", "in_progress", "completed", "on_hold", "cancelled"] = "not_started"
    progress_percentage: float = 0.0
    start_date: Optional[Date] = None
    target_date: Optional[Date] = None
    actual_date: Optional[Date] = None
    notes: Optional[str] = None
    source_email_id: Optional[str] = None
    updated_by: Optional[str] = None

# =============================================================================
# REVIEW QUEUE SYSTEM
# =============================================================================

class ReviewQueue(BaseModel):
    """Items requiring human review"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity: Literal["project_candidate", "invoice", "task", "progress_update", "classification"] = Field(..., description="Type of item")
    payload: Dict[str, Any] = Field(..., description="Item data")
    reason: str = Field(..., description="Why it needs review")
    confidence: Optional[float] = Field(None, description="AI confidence score")
    priority: Literal["low", "medium", "high", "urgent"] = Field("medium", description="Review priority")
    source_email_id: Optional[str] = Field(None, description="Originating email")
    created_at: DateTime = Field(default_factory=DateTime.now)
    resolved: bool = Field(False, description="Whether item has been resolved")
    resolved_by: Optional[str] = Field(None, description="Who resolved the item")
    resolved_at: Optional[DateTime] = Field(None, description="When item was resolved")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")

class ReviewQueueCreate(BaseModel):
    entity: Literal["project_candidate", "invoice", "task", "progress_update", "classification"]
    payload: Dict[str, Any]
    reason: str
    confidence: Optional[float] = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    source_email_id: Optional[str] = None

# =============================================================================
# LLM PROCESSING MODELS
# =============================================================================

class EmailClassification(BaseModel):
    """LLM email classification result"""
    label: Literal[
        "lead_rfp", "addendum", "award", "notice_to_proceed", "change_order",
        "inspection", "permit_portal_msg", "pay_app_or_remittance",
        "shipment_or_quote", "schedule_update", "invoice", "payment_confirmation",
        "general_correspondence", "progress_update"
    ]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None

class ProjectExtraction(BaseModel):
    """Extracted project data from email"""
    name: Optional[str] = None
    billing_type: Optional[Literal["TM", "SOV", "Fixed", "Bid"]] = None
    tm_bill_rate: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    ahj: Optional[str] = None
    client_company: Optional[str] = None
    project_manager: Optional[str] = None
    description: Optional[str] = None

class ContactInfo(BaseModel):
    """Extracted contact information"""
    name: str
    email: str
    company: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None

class FinancialInfo(BaseModel):
    """Extracted financial information"""
    amount: Optional[float] = None
    pay_app_number: Optional[str] = None
    invoice_number: Optional[str] = None
    remittance: Optional[float] = None
    payment_terms: Optional[str] = None

class DateInfo(BaseModel):
    """Extracted date information"""
    due_date: Optional[Date] = None
    inspection_date: Optional[Date] = None
    start_date: Optional[Date] = None
    completion_date: Optional[Date] = None

class EmailExtractionResult(BaseModel):
    """Complete email extraction result"""
    classification: EmailClassification
    project: Optional[ProjectExtraction] = None
    contacts: List[ContactInfo] = []
    financial: Optional[FinancialInfo] = None
    dates: Optional[DateInfo] = None
    links: List[str] = []
    tasks: List[str] = []  # Suggested tasks
    action_items: List[str] = []  # Items requiring attention
    progress_updates: List[str] = []  # Progress/milestone updates

# =============================================================================
# DASHBOARD & ANALYTICS MODELS
# =============================================================================

class ProjectIntelligence(BaseModel):
    """Complete project intelligence summary"""
    project_id: str
    project_name: str
    current_status: str
    progress_percentage: float
    recent_activities: List[str]
    pending_tasks: int
    overdue_tasks: int
    recent_emails: int
    total_invoices: int
    outstanding_amount: float
    next_milestone: Optional[str] = None
    next_due_date: Optional[Date] = None
    risk_factors: List[str] = []
    last_updated: DateTime

class SystemIntelligence(BaseModel):
    """System-wide intelligence summary"""
    total_projects: int
    active_projects: int
    pending_reviews: int
    overdue_tasks: int
    recent_emails: int
    total_outstanding: float
    high_priority_items: int
    last_updated: DateTime