"""
GC Dashboard Models - General Contractor Access System
Provides secure one-time login keys and read-only dashboards with project progress.
Excludes all financial information for security.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

# Enums
class AccessStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class ProjectPhase(str, Enum):
    DESIGN = "design"
    APPROVAL = "approval"
    MOBILIZATION = "mobilization"
    INSTALLATION = "installation"
    INSPECTION = "inspection"
    CLOSEOUT = "closeout"

class InspectionResult(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"

# Core Models
class GcKey(BaseModel):
    """GC Key model for secure one-time access"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    key: str  # 4-digit unique key
    expiresAt: datetime
    active: bool = True
    used: bool = False
    usedAt: Optional[datetime] = None
    usedByIp: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GcKeyCreate(BaseModel):
    projectId: str
    key: str
    expiresAt: datetime

class GcAccessLog(BaseModel):
    """GC Access Log for admin visibility"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gcKeyId: str  # Reference to GcKey
    projectId: str  # Reference to Project
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip: str
    status: AccessStatus = AccessStatus.SUCCESS
    userAgent: Optional[str] = None

class GcAccessLogCreate(BaseModel):
    gcKeyId: str
    projectId: str
    ip: str
    status: AccessStatus = AccessStatus.SUCCESS
    userAgent: Optional[str] = None

class ProjectPhaseModel(BaseModel):
    """Project Phase for GC progress tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    phase: ProjectPhase
    percentComplete: float = 0.0
    plannedDate: Optional[datetime] = None
    actualDate: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectPhaseCreate(BaseModel):
    projectId: str
    phase: ProjectPhase
    percentComplete: Optional[float] = 0.0
    plannedDate: Optional[datetime] = None
    actualDate: Optional[datetime] = None
    notes: Optional[str] = None

class ProjectPhaseUpdate(BaseModel):
    phase: Optional[ProjectPhase] = None
    percentComplete: Optional[float] = None
    plannedDate: Optional[datetime] = None
    actualDate: Optional[datetime] = None
    notes: Optional[str] = None

class InspectionStatusModel(BaseModel):
    """Inspection Status for GC visibility"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    inspectionType: str
    scheduledDate: Optional[datetime] = None
    result: InspectionResult = InspectionResult.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InspectionStatusCreate(BaseModel):
    projectId: str
    inspectionType: str
    scheduledDate: Optional[datetime] = None
    result: Optional[InspectionResult] = InspectionResult.PENDING
    notes: Optional[str] = None

class InspectionStatusUpdate(BaseModel):
    inspectionType: Optional[str] = None
    scheduledDate: Optional[datetime] = None
    result: Optional[InspectionResult] = None
    notes: Optional[str] = None

class GcNarrative(BaseModel):
    """GC Narrative for plain English progress summary"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str  # Reference to Project
    narrative: str
    generatedAt: datetime = Field(default_factory=datetime.utcnow)

class GcNarrativeCreate(BaseModel):
    projectId: str
    narrative: str

# Response Models for GC Dashboard (No Financial Data)
class GcCrewSummary(BaseModel):
    """Crew summary for GC (hours and days only, no costs)"""
    totalHours: float
    totalDays: int
    recentDescriptions: List[str]
    activeCrewMembers: int

class GcMaterialSummary(BaseModel):
    """Material summary for GC (quantities only, no costs)"""
    date: datetime
    vendor: str
    item: str
    quantity: float
    description: Optional[str] = None

class GcTmTagSummary(BaseModel):
    """T&M Tag summary for GC (counts and hours only, no dollars)"""
    totalTags: int
    submittedTags: int
    approvedTags: int
    totalHours: float
    recentTagTitles: List[str]

class GcProjectDashboard(BaseModel):
    """Complete GC Dashboard response (no financial data)"""
    projectId: str
    projectName: str
    projectLocation: Optional[str] = None
    projectStatus: str
    overallProgress: float  # Overall completion percentage
    phases: List[ProjectPhaseModel]
    crewSummary: GcCrewSummary
    materials: List[GcMaterialSummary]
    tmTagSummary: GcTmTagSummary
    inspections: List[InspectionStatusModel]
    narrative: Optional[str] = None
    lastUpdated: datetime

# Admin Models
class GcKeyAdmin(BaseModel):
    """Admin view of GC Key with limited info"""
    id: str
    projectName: str
    keyLastFour: str  # Only show last 4 digits for security
    expiresAt: datetime
    active: bool
    used: bool
    usedAt: Optional[datetime] = None

class GcAccessLogAdmin(BaseModel):
    """Admin view of access logs"""
    id: str
    projectName: str
    keyLastFour: str
    timestamp: datetime
    ip: str
    status: AccessStatus
    userAgent: Optional[str] = None