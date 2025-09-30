"""
Rhino Platform Data Models
Based on specification for single-domain auth/routing + project-based T&M rates + cashflow
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date as Date, datetime as DateTime
import uuid
from decimal import Decimal

# =============================================================================
# CORE DATA MODELS
# =============================================================================

class Installer(BaseModel):
    """Installer model - stores COST ONLY, no GC billing fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Full name of installer")
    cost_rate: float = Field(..., description="Hourly cost rate (company cost, not billing rate)")
    position: Optional[str] = Field(None, description="Job position/title")
    active: bool = Field(True, description="Whether installer is active")
    hire_date: Optional[Date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: DateTime = Field(default_factory=DateTime.now)

class InstallerCreate(BaseModel):
    name: str
    cost_rate: float
    position: Optional[str] = None
    active: bool = True
    hire_date: Optional[Date] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class InstallerUpdate(BaseModel):
    name: Optional[str] = None
    cost_rate: Optional[float] = None
    position: Optional[str] = None
    active: Optional[bool] = None
    hire_date: Optional[Date] = None
    phone: Optional[str] = None
    email: Optional[str] = None

# =============================================================================

class Project(BaseModel):
    """Project model with billing type and T&M rate"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Unique project name")
    billing_type: Literal["TM", "SOV", "Fixed", "Bid"] = Field(..., description="Project billing type")
    tm_bill_rate: Optional[float] = Field(None, description="T&M hourly billing rate (required if billing_type=TM)")
    description: Optional[str] = None
    client_company: Optional[str] = None
    project_manager: Optional[str] = None
    address: Optional[str] = None
    status: str = Field("active", description="Project status")
    start_date: Optional[Date] = None
    estimated_completion: Optional[Date] = None
    contract_amount: Optional[float] = None
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

class ProjectCreate(BaseModel):
    name: str
    billing_type: Literal["TM", "SOV", "Fixed", "Bid"]
    tm_bill_rate: Optional[float] = None
    description: Optional[str] = None
    client_company: Optional[str] = None
    project_manager: Optional[str] = None
    address: Optional[str] = None
    status: str = "active"
    start_date: Optional[Date] = None
    estimated_completion: Optional[Date] = None
    contract_amount: Optional[float] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    billing_type: Optional[Literal["TM", "SOV", "Fixed", "Bid"]] = None
    tm_bill_rate: Optional[float] = None
    description: Optional[str] = None
    client_company: Optional[str] = None
    project_manager: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    estimated_completion: Optional[date] = None
    contract_amount: Optional[float] = None

# =============================================================================

class TimeLog(BaseModel):
    """Time log entry - uses project's T&M rate for billing calculations"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date = Field(..., description="Work date")
    installer_id: str = Field(..., description="Installer UUID")
    project_id: str = Field(..., description="Project UUID")
    hours: float = Field(..., ge=0, le=16, description="Hours worked (0-16)")
    bill_rate_override: Optional[float] = Field(None, description="Optional override for billing rate")
    notes: Optional[str] = None
    created_by: Optional[str] = None  # User who created the entry
    created_at: datetime = Field(default_factory=datetime.now)

class TimeLogCreate(BaseModel):
    date: date
    installer_id: str
    project_id: str
    hours: float = Field(..., ge=0, le=16)
    bill_rate_override: Optional[float] = None
    notes: Optional[str] = None

class TimeLogUpdate(BaseModel):
    date: Optional[date] = None
    installer_id: Optional[str] = None
    project_id: Optional[str] = None
    hours: Optional[float] = None
    bill_rate_override: Optional[float] = None
    notes: Optional[str] = None

# =============================================================================

class PerDiemHotel(BaseModel):
    """Per diem and hotel expense tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date = Field(..., description="Expense date")
    project_id: str = Field(..., description="Project UUID")
    workers: int = Field(..., ge=1, description="Number of workers")
    per_diem_per_worker: float = Field(40.0, description="Per diem amount per worker")
    days: int = Field(..., ge=1, description="Number of days")
    nights: int = Field(..., ge=0, description="Number of nights")
    rooms: int = Field(..., ge=1, description="Number of hotel rooms")
    hotel_rate: float = Field(125.0, description="Hotel rate per room per night")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class PerDiemHotelCreate(BaseModel):
    date: date
    project_id: str
    workers: int = Field(..., ge=1)
    per_diem_per_worker: float = 40.0
    days: int = Field(..., ge=1)
    nights: int = Field(..., ge=0)
    rooms: int = Field(..., ge=1)
    hotel_rate: float = 125.0
    notes: Optional[str] = None

# =============================================================================

class Cashflow(BaseModel):
    """Cashflow entry for running balance tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date = Field(..., description="Transaction date")
    type: Literal["inflow", "outflow"] = Field(..., description="Transaction type")
    category: Literal["Deposit", "Labor", "Per Diem", "Hotels", "Material", "Other"] = Field(..., description="Transaction category")
    project_id: Optional[str] = Field(None, description="Optional project association")
    amount: float = Field(..., description="Transaction amount (positive value)")
    reference: Optional[str] = Field(None, description="Reference number or description")
    created_at: datetime = Field(default_factory=datetime.now)

class CashflowCreate(BaseModel):
    date: date
    type: Literal["inflow", "outflow"]
    category: Literal["Deposit", "Labor", "Per Diem", "Hotels", "Material", "Other"]
    project_id: Optional[str] = None
    amount: float
    reference: Optional[str] = None

# =============================================================================

class Settings(BaseModel):
    """System settings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    starting_balance: float = Field(34000.0, description="Starting cash balance")

# =============================================================================
# CALCULATED/VIEW MODELS
# =============================================================================

class TimeLogEffective(BaseModel):
    """Time log with calculated effective rates and totals"""
    id: str
    date: date
    hours: float
    installer_id: str
    project_id: str
    installer_name: str
    project_name: str
    billing_type: str
    eff_cost_rate: float  # From installer.cost_rate
    eff_bill_rate: Optional[float]  # From project.tm_bill_rate or override
    labor_cost: float  # hours * eff_cost_rate
    billable: Optional[float]  # hours * eff_bill_rate (only for T&M projects)
    profit: Optional[float]  # billable - labor_cost (only for T&M projects)

class ProjectTMTotals(BaseModel):
    """T&M project totals"""
    project: str
    project_id: str
    hours: float
    labor_cost: float
    billable: Optional[float]
    profit: Optional[float]

class CashBalance(BaseModel):
    """Current cash balance"""
    current_balance: float
    starting_balance: float
    total_inflows: float
    total_outflows: float

# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_project_tm_rate(project: ProjectCreate) -> bool:
    """Validate that T&M projects have tm_bill_rate"""
    if project.billing_type == "TM" and project.tm_bill_rate is None:
        return False
    return True

def validate_timelog_project_compatibility(project_billing_type: str, project_tm_rate: Optional[float]) -> bool:
    """Validate time log can be created for project"""
    if project_billing_type == "TM" and project_tm_rate is None:
        return False
    return True