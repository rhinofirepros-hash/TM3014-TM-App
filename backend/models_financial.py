"""
Financial Management Models - Invoices, Payables, Cashflow, Profitability
Implements the exact schema specification provided by the user
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from enum import Enum
import uuid

# Enums
class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"

class PayableStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"

class AlertType(str, Enum):
    LOW_MARGIN = "low_margin"
    OVER_BUDGET = "over_budget"

class InspectionType(str, Enum):
    ROUGH = "rough"
    PARTIAL_ROUGH = "partial_rough"
    FINAL = "final"
    PARTIAL_FINAL = "partial_final"
    UNDERGROUND = "underground"
    OTHER = "other"

class InspectionStatus(str, Enum):
    SCHEDULED = "scheduled"
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"

# Core Models
class LineItem(BaseModel):
    """Invoice line item"""
    description: str
    qty: float
    unit_cost: float
    total: float

class Invoice(BaseModel):
    """Invoice model matching exact specification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    invoice_number: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    line_items: List[LineItem] = []
    subtotal: float
    tax: float
    total: float
    due_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InvoiceCreate(BaseModel):
    project_id: str
    invoice_number: str
    line_items: List[LineItem]
    subtotal: float
    tax: float
    total: float
    due_date: datetime

class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    line_items: Optional[List[LineItem]] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    due_date: Optional[datetime] = None

class Payable(BaseModel):
    """Payable model matching exact specification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vendor_id: str
    project_id: str
    po_number: Optional[str] = None
    description: str
    amount: float
    status: PayableStatus = PayableStatus.PENDING
    due_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PayableCreate(BaseModel):
    vendor_id: str
    project_id: str
    po_number: Optional[str] = None
    description: str
    amount: float
    due_date: datetime

class PayableUpdate(BaseModel):
    vendor_id: Optional[str] = None
    po_number: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[PayableStatus] = None
    due_date: Optional[datetime] = None

class CashflowForecast(BaseModel):
    """Cashflow forecast model matching exact specification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    week_start: datetime
    inflow: float
    outflow: float
    net: float
    runway_weeks: int
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CashflowForecastCreate(BaseModel):
    project_id: str
    week_start: datetime
    inflow: float
    outflow: float
    net: float
    runway_weeks: int
    notes: Optional[str] = None

class CashflowForecastUpdate(BaseModel):
    week_start: Optional[datetime] = None
    inflow: Optional[float] = None
    outflow: Optional[float] = None
    net: Optional[float] = None
    runway_weeks: Optional[int] = None
    notes: Optional[str] = None

class Alert(BaseModel):
    """Profitability alert"""
    type: AlertType
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Profitability(BaseModel):
    """Profitability model matching exact specification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    revenue: float
    labor_cost: float
    material_cost: float
    overhead_cost: float
    profit_margin: float
    alerts: List[Alert] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProfitabilityCreate(BaseModel):
    project_id: str
    revenue: float
    labor_cost: float
    material_cost: float
    overhead_cost: float
    profit_margin: float
    alerts: Optional[List[Alert]] = []

class ProfitabilityUpdate(BaseModel):
    revenue: Optional[float] = None
    labor_cost: Optional[float] = None
    material_cost: Optional[float] = None
    overhead_cost: Optional[float] = None
    profit_margin: Optional[float] = None
    alerts: Optional[List[Alert]] = None

class Inspection(BaseModel):
    """Inspection model matching exact specification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    inspection_type: InspectionType
    status: InspectionStatus = InspectionStatus.PENDING
    date: datetime
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InspectionCreate(BaseModel):
    project_id: str
    inspection_type: InspectionType
    status: Optional[InspectionStatus] = InspectionStatus.PENDING
    date: datetime
    notes: Optional[str] = None

class InspectionUpdate(BaseModel):
    inspection_type: Optional[InspectionType] = None
    status: Optional[InspectionStatus] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None