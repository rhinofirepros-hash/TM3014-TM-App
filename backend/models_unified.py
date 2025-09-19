"""
Unified Schema Models for Enhanced T&M and Cashflow Forecasting System
Supports the new schema with enhanced project management, cashflow forecasting, 
invoice management, and AI-powered narratives.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid

# Enums for type safety
class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class PlanSubmittalStatus(str, Enum):
    """Plan submittal status enumeration"""
    IN_DESIGN = "in_design"
    SUBMITTED = "submitted"
    CORRECTIONS = "corrections"  
    APPROVED = "approved"

class ContractType(str, Enum):
    TM = "T&M"
    FIXED = "Fixed"

class InvoiceSchedule(str, Enum):
    MONTHLY = "monthly"
    MILESTONES = "milestones"
    WEEKLY = "weekly"

class CrewMemberStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class TMTagStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"

class PayableStatus(str, Enum):
    OPEN = "open"
    PAID = "paid"

class ExpenseType(str, Enum):
    HOTEL = "hotel"
    PER_DIEM = "per diem"
    RENTAL = "rental"
    MISC = "misc"

# Core Models
class Project(BaseModel):
    """Enhanced Project model with billing and forecasting capabilities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    client: str
    contractType: ContractType = ContractType.TM
    invoiceSchedule: InvoiceSchedule = InvoiceSchedule.MONTHLY
    billingDay: int = 20
    openingBalance: float = 0
    gcRate: float  # Billing rate to GC
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    notes: Optional[str] = None
    # GC PIN fields for dashboard access
    gc_pin: Optional[str] = None
    gc_pin_used: Optional[bool] = False
    # Plan submittal tracking
    plan_submittal_status: PlanSubmittalStatus = PlanSubmittalStatus.APPROVED  # T&M projects default to approved
    plan_submittal_date: Optional[datetime] = None
    plan_submittal_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    client: str
    contractType: Optional[ContractType] = ContractType.TM
    invoiceSchedule: Optional[InvoiceSchedule] = InvoiceSchedule.MONTHLY
    billingDay: Optional[int] = 20
    openingBalance: Optional[float] = 0
    gcRate: float
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    notes: Optional[str] = None

class CrewMember(BaseModel):
    """Enhanced crew member model with separate cost and billing rates"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    position: Optional[str] = None
    hourlyRate: float  # True cost rate
    gcBillRate: float  # Rate billed to GC
    hireDate: Optional[datetime] = None
    status: CrewMemberStatus = CrewMemberStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CrewMemberCreate(BaseModel):
    name: str
    position: Optional[str] = None
    hourlyRate: float
    gcBillRate: float
    hireDate: Optional[datetime] = None

class CrewLog(BaseModel):
    """Enhanced crew log with rates and sync tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    crewMemberId: Optional[str] = None  # Reference to CrewMember
    date: datetime
    hours: float
    description: Optional[str] = None
    weather: Optional[str] = None
    syncedToTmTag: bool = False
    tmTagId: Optional[str] = None  # Reference to TmTag
    costRate: Optional[float] = None  # Hourly cost rate
    billRate: Optional[float] = None  # Hourly billing rate
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CrewLogCreate(BaseModel):
    projectId: str
    crewMemberId: Optional[str] = None
    date: datetime
    hours: float
    description: Optional[str] = None
    weather: Optional[str] = None
    costRate: Optional[float] = None
    billRate: Optional[float] = None

class Material(BaseModel):
    """Enhanced material tracking with markup"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    vendor: str
    date: datetime
    description: str
    quantity: float
    unitCost: float
    total: float
    markupPercent: float = 0
    confirmed: bool = False
    tmTagId: Optional[str] = None  # Reference to TmTag
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MaterialCreate(BaseModel):
    projectId: str
    vendor: str
    date: datetime
    description: str
    quantity: float
    unitCost: float
    total: float
    markupPercent: Optional[float] = 0
    confirmed: Optional[bool] = False
    tmTagId: Optional[str] = None

class Expense(BaseModel):
    """New expense tracking model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    type: ExpenseType
    description: str
    date: datetime
    amount: float
    tmTagId: Optional[str] = None  # Reference to TmTag
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExpenseCreate(BaseModel):
    projectId: str
    type: ExpenseType
    description: str
    date: datetime
    amount: float
    tmTagId: Optional[str] = None

class TmTag(BaseModel):
    """Enhanced T&M tag with calculated totals"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    date: datetime
    gcEmail: Optional[str] = None
    foreman: Optional[str] = None
    crewLogs: List[str] = []  # References to CrewLog IDs
    materials: List[str] = []  # References to Material IDs
    expenses: List[str] = []  # References to Expense IDs
    totalLaborCost: float
    totalLaborBill: float
    totalMaterialCost: float
    totalMaterialBill: float
    totalExpense: float
    totalBill: float
    pdfUrl: Optional[str] = None
    status: TMTagStatus = TMTagStatus.DRAFT
    tmTagNarrative: Optional[str] = None  # AI-generated summary
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TmTagCreate(BaseModel):
    projectId: str
    date: datetime
    gcEmail: Optional[str] = None
    foreman: Optional[str] = None
    crewLogs: Optional[List[str]] = []
    materials: Optional[List[str]] = []
    expenses: Optional[List[str]] = []
    tmTagNarrative: Optional[str] = None

class LineItem(BaseModel):
    """Invoice line item"""
    description: str
    amount: float

class Invoice(BaseModel):
    """New invoice management model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    invoiceNumber: str
    dateIssued: datetime
    dueDate: datetime
    periodStart: datetime
    periodEnd: datetime
    lineItems: List[LineItem]
    total: float
    status: InvoiceStatus = InvoiceStatus.DRAFT
    invoiceNarrative: Optional[str] = None  # AI-generated description
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvoiceCreate(BaseModel):
    projectId: str
    invoiceNumber: str
    dateIssued: datetime
    dueDate: datetime
    periodStart: datetime
    periodEnd: datetime
    lineItems: List[LineItem]
    total: float
    invoiceNarrative: Optional[str] = None

class Payable(BaseModel):
    """New payables tracking model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    vendor: str
    description: str
    dueDate: datetime
    amount: float
    status: PayableStatus = PayableStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PayableCreate(BaseModel):
    projectId: str
    vendor: str
    description: str
    dueDate: datetime
    amount: float

# New Forecast Models
class WeeklyForecast(BaseModel):
    """Weekly cashflow forecast"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str
    weekOf: datetime  # Start of week
    inflow: float
    outflow: float
    net: float
    alert: Optional[str] = None
    forecastNarrative: Optional[str] = None  # AI-generated explanation
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CompanyForecast(BaseModel):
    """Company-wide rollup forecast"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    weekOf: datetime
    totalInflow: float
    totalOutflow: float
    net: float
    projects: List[str] = []  # Project IDs included
    rollupNarrative: Optional[str] = None  # AI-generated summary
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CashRunway(BaseModel):
    """Cash runway analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nextInvoiceDate: datetime
    weeklyBurn: List[float] = []
    cumulativeBalance: List[float] = []
    runwayWeeks: int
    alert: Optional[str] = None
    runwayNarrative: Optional[str] = None  # AI-generated explanation
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Response Models for Analytics
class ProjectAnalytics(BaseModel):
    """Comprehensive project analytics response"""
    projectId: str
    contractType: ContractType
    totalLaborCost: float
    totalLaborBill: float
    totalMaterialCost: float
    totalMaterialBill: float
    totalExpense: float
    totalBill: float
    profitMargin: float
    weeklyForecasts: List[WeeklyForecast] = []
    forecastNarrative: Optional[str] = None

class CompanyAnalytics(BaseModel):
    """Company-wide analytics response"""
    totalProjects: int
    activeProjects: int
    totalRevenue: float
    totalCosts: float
    netProfit: float
    weeklyForecast: CompanyForecast
    cashRunway: CashRunway
    rollupNarrative: Optional[str] = None

# Update/Edit Models
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    contractType: Optional[ContractType] = None
    invoiceSchedule: Optional[InvoiceSchedule] = None
    billingDay: Optional[int] = None
    openingBalance: Optional[float] = None
    gcRate: Optional[float] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    notes: Optional[str] = None

class CrewMemberUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    hourlyRate: Optional[float] = None
    gcBillRate: Optional[float] = None
    hireDate: Optional[datetime] = None
    status: Optional[CrewMemberStatus] = None

# Legacy compatibility models (for migration)
class LegacyTMTag(BaseModel):
    """Legacy T&M tag structure for backward compatibility"""
    id: str
    project_id: Optional[str] = None
    project_name: str
    cost_code: str
    date_of_work: datetime
    company_name: Optional[str] = ""
    tm_tag_title: str
    description_of_work: str
    labor_entries: List[Dict[str, Any]] = []
    material_entries: List[Dict[str, Any]] = []
    equipment_entries: List[Dict[str, Any]] = []
    other_entries: List[Dict[str, Any]] = []
    gc_email: str
    signature: Optional[str] = None
    foreman_name: str = "Jesus Garcia"
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None

# Helper functions for conversions
def convert_legacy_tm_tag_to_unified(legacy_tag: LegacyTMTag) -> TmTag:
    """Convert legacy T&M tag to unified schema"""
    # Calculate totals from legacy entries
    total_labor_cost = 0
    total_labor_bill = 0
    
    for entry in legacy_tag.labor_entries:
        hours = float(entry.get("total_hours", 0))
        total_labor_cost += hours * 40  # Default cost rate
        total_labor_bill += hours * 95  # Default bill rate
    
    total_material_cost = sum(float(entry.get("total", 0)) for entry in legacy_tag.material_entries)
    total_expense = sum(float(entry.get("total", 0)) for entry in legacy_tag.other_entries)
    
    return TmTag(
        id=legacy_tag.id,
        projectId=legacy_tag.project_id or "",
        date=legacy_tag.date_of_work,
        gcEmail=legacy_tag.gc_email,
        foreman=legacy_tag.foreman_name,
        crewLogs=[],
        materials=[],
        expenses=[],
        totalLaborCost=total_labor_cost,
        totalLaborBill=total_labor_bill,
        totalMaterialCost=total_material_cost,
        totalMaterialBill=total_material_cost * 1.2,  # 20% markup
        totalExpense=total_expense,
        totalBill=total_labor_bill + (total_material_cost * 1.2) + total_expense,
        pdfUrl=None,
        status=TMTagStatus.SUBMITTED if legacy_tag.status == "completed" else TMTagStatus.DRAFT,
        tmTagNarrative=legacy_tag.description_of_work,
        created_at=legacy_tag.created_at
    )