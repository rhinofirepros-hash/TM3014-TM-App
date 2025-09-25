"""
Enhanced FastAPI server with unified schema support
Supports both legacy and new unified schema for gradual migration
"""

from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import asyncio
import random
import secrets
import bcrypt

# Import both legacy and unified models
from models_unified import (
    Project, ProjectCreate, ProjectUpdate,
    CrewMember, CrewMemberCreate, CrewMemberUpdate,
    CrewLog, CrewLogCreate,
    Material, MaterialCreate,
    Expense, ExpenseCreate,
    TmTag, TmTagCreate,
    Invoice, InvoiceCreate,
    Payable, PayableCreate,
    WeeklyForecast, CompanyForecast, CashRunway,
    ProjectAnalytics, CompanyAnalytics,
    ContractType, InvoiceSchedule, ProjectStatus,
    convert_legacy_tm_tag_to_unified, LegacyTMTag
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

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Enhanced T&M Management API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Collection names - using new unified schema collections
COLLECTIONS = {
    "projects": "projects_new",
    "crew_members": "crew_members", 
    "crew_logs": "crew_logs_new",
    "tm_tags": "tm_tags_new",
    "materials": "materials_new",
    "expenses": "expenses",
    "invoices": "invoices",
    "payables": "payables",
    "weekly_forecasts": "weekly_forecasts",
    "company_forecasts": "company_forecasts",
    "cash_runway": "cash_runway"
}

# GC Dashboard collections
gc_keys_collection = db["gc_keys"]
gc_access_logs_collection = db["gc_access_logs"]
project_phases_collection = db["project_phases"]
inspection_status_collection = db["inspection_status"]
gc_narratives_collection = db["gc_narratives"]

# Helper functions
async def get_collection(name: str):
    """Get collection with fallback to legacy if unified doesn't exist"""
    collection_name = COLLECTIONS.get(name, name)
    collection = db[collection_name]
    
    # Check if collection exists and has data
    count = await collection.count_documents({})
    if count == 0 and name in ["projects", "crew_logs", "tm_tags", "materials"]:
        # Fallback to legacy collection names
        legacy_names = {
            "projects": "projects",
            "crew_logs": "crew_logs", 
            "tm_tags": "tm_tags",
            "materials": "materials"
        }
        if name in legacy_names:
            logger.info(f"Falling back to legacy collection: {legacy_names[name]}")
            return db[legacy_names[name]]
    
    return collection

def serialize_doc(doc: dict) -> dict:
    """Remove MongoDB ObjectId and ensure serialization"""
    if "_id" in doc:
        # Use _id as the id field if no id field exists
        if "id" not in doc:
            doc["id"] = str(doc["_id"])
        del doc["_id"]
    
    # Convert any ObjectId fields to strings
    for key, value in doc.items():
        if hasattr(value, '__class__') and value.__class__.__name__ == 'ObjectId':
            doc[key] = str(value)
    
    return doc

# Project Management Endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    """Create a new project with unified schema"""
    try:
        collection = await get_collection("projects")
        project_dict = project.dict()
        project_obj = Project(**project_dict)
        
        result = await collection.insert_one(project_obj.dict())
        logger.info(f"Created project: {project_obj.name} (ID: {project_obj.id})")
        
        return project_obj
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects", response_model=List[Project])
async def get_projects(status: Optional[ProjectStatus] = None):
    """Get all projects with optional status filter"""
    try:
        collection = await get_collection("projects")
        query = {}
        if status:
            query["status"] = status.value
        
        projects = await collection.find(query).to_list(1000)
        
        # Handle both unified and legacy schema
        result = []
        for project in projects:
            project = serialize_doc(project)
            
            # Convert legacy schema if needed
            if "client_company" in project:  # Legacy schema
                project["client"] = project.get("client_company", project.get("client", ""))
                project["contractType"] = "T&M" if project.get("project_type") == "tm_only" else "Fixed"
                project["invoiceSchedule"] = "monthly"
                project["billingDay"] = 20
                project["openingBalance"] = 0
                project["gcRate"] = project.get("labor_rate", 95)
                
            result.append(Project(**project))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get project by ID"""
    try:
        collection = await get_collection("projects")
        project = await collection.find_one({"id": project_id})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = serialize_doc(project)
        
        # Convert legacy schema if needed
        if "client_company" in project:
            project["client"] = project.get("client_company", project.get("client", ""))
            project["contractType"] = "T&M" if project.get("project_type") == "tm_only" else "Fixed"
            project["invoiceSchedule"] = "monthly"
            project["billingDay"] = 20
            project["openingBalance"] = 0
            project["gcRate"] = project.get("labor_rate", 95)
        
        return Project(**project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    """Update project"""
    try:
        collection = await get_collection("projects")
        update_dict = {k: v for k, v in project_update.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"id": project_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return await get_project(project_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project"""
    try:
        collection = await get_collection("projects")
        result = await collection.delete_one({"id": project_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"message": "Project deleted successfully", "id": project_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Crew Member Management Endpoints
@api_router.post("/crew-members", response_model=CrewMember)
async def create_crew_member(crew_member: CrewMemberCreate):
    """Create a new crew member"""
    try:
        collection = await get_collection("crew_members")
        crew_member_dict = crew_member.dict()
        crew_member_obj = CrewMember(**crew_member_dict)
        
        result = await collection.insert_one(crew_member_obj.dict())
        logger.info(f"Created crew member: {crew_member_obj.name}")
        
        return crew_member_obj
    except Exception as e:
        logger.error(f"Error creating crew member: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/crew-members", response_model=List[CrewMember])
async def get_crew_members(status: Optional[str] = "active"):
    """Get all crew members"""
    try:
        collection = await get_collection("crew_members")
        query = {}
        if status:
            query["status"] = status
        
        crew_members = await collection.find(query).to_list(1000)
        
        # Handle fallback to employees collection
        if not crew_members:
            employees_collection = db["employees"]
            employees = await employees_collection.find({"status": "active"}).to_list(1000)
            
            crew_members = []
            for emp in employees:
                emp = serialize_doc(emp)
                crew_member_dict = {
                    "id": emp.get("id", str(uuid.uuid4())),
                    "name": emp.get("name", "Unknown"),
                    "position": emp.get("position", ""),
                    "hourlyRate": emp.get("hourly_rate", 40),
                    "gcBillRate": emp.get("gc_billing_rate", 95),
                    "hireDate": emp.get("hire_date"),
                    "status": "active" if emp.get("status") == "active" else "inactive",
                    "created_at": emp.get("created_at", datetime.utcnow())
                }
                crew_members.append(crew_member_dict)
        else:
            crew_members = [serialize_doc(cm) for cm in crew_members]
        
        return [CrewMember(**cm) for cm in crew_members]
    except Exception as e:
        logger.error(f"Error fetching crew members: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Material Management Endpoints
@api_router.post("/materials", response_model=Material)
async def create_material(material: MaterialCreate):
    """Create a new material entry"""
    try:
        collection = await get_collection("materials")
        material_dict = material.dict()
        material_obj = Material(**material_dict)
        
        result = await collection.insert_one(material_obj.dict())
        logger.info(f"Created material: {material_obj.description}")
        
        return material_obj
    except Exception as e:
        logger.error(f"Error creating material: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/materials", response_model=List[Material])
async def get_materials(project_id: Optional[str] = None):
    """Get materials with optional project filter"""
    try:
        collection = await get_collection("materials")
        query = {}
        if project_id:
            query["projectId"] = project_id
        
        materials = await collection.find(query).to_list(1000)
        
        # Handle legacy schema conversion
        result = []
        for material in materials:
            material = serialize_doc(material)
            
            # Convert legacy schema if needed
            if "project_id" in material:  # Legacy schema
                material["projectId"] = material.get("project_id", "")
                material["vendor"] = material.get("vendor", "Unknown")
                material["date"] = material.get("purchase_date", datetime.utcnow())
                material["description"] = material.get("material_name", "Material")
                material["quantity"] = material.get("quantity", 1)
                material["unitCost"] = material.get("unit_cost", 0)  
                material["total"] = material.get("total_cost", 0)
                material["markupPercent"] = 20  # Default markup
                material["confirmed"] = True
                material["tmTagId"] = None
                
            result.append(Material(**material))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Expense Management Endpoints
@api_router.post("/expenses", response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    """Create a new expense entry"""
    try:
        collection = await get_collection("expenses")
        expense_dict = expense.dict()
        expense_obj = Expense(**expense_dict)
        
        result = await collection.insert_one(expense_obj.dict())
        logger.info(f"Created expense: {expense_obj.description}")
        
        return expense_obj
    except Exception as e:
        logger.error(f"Error creating expense: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/expenses", response_model=List[Expense])
async def get_expenses(project_id: Optional[str] = None):
    """Get expenses with optional project filter"""
    try:
        collection = await get_collection("expenses")
        query = {}
        if project_id:
            query["projectId"] = project_id
        
        expenses = await collection.find(query).to_list(1000)
        return [Expense(**serialize_doc(expense)) for expense in expenses]
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# T&M Tag Management (Enhanced)
@api_router.post("/tm-tags", response_model=TmTag)
async def create_tm_tag(tm_tag: TmTagCreate):
    """Create a new T&M tag with unified schema"""
    try:
        collection = await get_collection("tm_tags")
        
        # Calculate totals based on linked crew logs, materials, expenses
        total_labor_cost = 0
        total_labor_bill = 0
        total_material_cost = 0
        total_material_bill = 0
        total_expense = 0
        
        # Calculate labor totals from crew logs
        if tm_tag.crewLogs:
            crew_logs_collection = await get_collection("crew_logs")
            for log_id in tm_tag.crewLogs:
                log = await crew_logs_collection.find_one({"id": log_id})
                if log:
                    hours = log.get("hours", 0)
                    cost_rate = log.get("costRate", 40)
                    bill_rate = log.get("billRate", 95)
                    total_labor_cost += hours * cost_rate
                    total_labor_bill += hours * bill_rate
        
        # Calculate material totals
        if tm_tag.materials:
            materials_collection = await get_collection("materials")
            for material_id in tm_tag.materials:
                material = await materials_collection.find_one({"id": material_id})
                if material:
                    cost = material.get("total", 0)
                    markup = material.get("markupPercent", 20) / 100
                    total_material_cost += cost
                    total_material_bill += cost * (1 + markup)
        
        # Calculate expense totals
        if tm_tag.expenses:
            expenses_collection = await get_collection("expenses")
            for expense_id in tm_tag.expenses:
                expense = await expenses_collection.find_one({"id": expense_id})
                if expense:
                    total_expense += expense.get("amount", 0)
        
        tm_tag_dict = tm_tag.dict()
        
        # Fix timezone handling for date field
        if isinstance(tm_tag_dict['date'], str):
            # Parse the date string and ensure it's in the correct timezone
            from datetime import datetime, timezone
            parsed_date = datetime.fromisoformat(tm_tag_dict['date'].replace('Z', '+00:00'))
            # Convert to local timezone if needed and store as UTC
            tm_tag_dict['date'] = parsed_date.replace(tzinfo=timezone.utc)
        
        tm_tag_dict.update({
            "totalLaborCost": total_labor_cost,
            "totalLaborBill": total_labor_bill,
            "totalMaterialCost": total_material_cost,
            "totalMaterialBill": total_material_bill,
            "totalExpense": total_expense,
            "totalBill": total_labor_bill + total_material_bill + total_expense
        })
        
        tm_tag_obj = TmTag(**tm_tag_dict)
        result = await collection.insert_one(tm_tag_obj.dict())
        
        logger.info(f"Created T&M tag for project {tm_tag_obj.projectId} with date {tm_tag_obj.date}")
        return tm_tag_obj
    except Exception as e:
        logger.error(f"Error creating T&M tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tm-tags", response_model=List[TmTag])
async def get_tm_tags(project_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    """Get T&M tags with optional project filter"""
    try:
        collection = await get_collection("tm_tags")
        query = {}
        if project_id:
            query["projectId"] = project_id
        
        tm_tags = await collection.find(query).skip(skip).limit(limit).to_list(limit)
        
        # Handle legacy schema conversion
        result = []
        for tag in tm_tags:
            tag = serialize_doc(tag)
            
            # Convert legacy T&M tags if needed
            if "date_of_work" in tag:  # Legacy schema
                try:
                    legacy_tag = LegacyTMTag(**tag)
                    unified_tag = convert_legacy_tm_tag_to_unified(legacy_tag)
                    result.append(unified_tag)
                except Exception as e:
                    logger.warning(f"Failed to convert legacy T&M tag {tag.get('id')}: {e}")
                    continue
            else:
                result.append(TmTag(**tag))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching T&M tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Invoice Management Endpoints
@api_router.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate):
    """Create a new invoice"""
    try:
        collection = await get_collection("invoices")
        invoice_dict = invoice.dict()
        invoice_obj = Invoice(**invoice_dict)
        
        result = await collection.insert_one(invoice_obj.dict())
        logger.info(f"Created invoice: {invoice_obj.invoiceNumber}")
        
        return invoice_obj
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/invoices", response_model=List[Invoice])
async def get_invoices(project_id: Optional[str] = None):
    """Get invoices with optional project filter"""
    try:
        collection = await get_collection("invoices")
        query = {}
        if project_id:
            query["projectId"] = project_id
        
        invoices = await collection.find(query).to_list(1000)
        return [Invoice(**serialize_doc(invoice)) for invoice in invoices]
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Payable Management Endpoints
@api_router.post("/payables", response_model=Payable)
async def create_payable(payable: PayableCreate):
    """Create a new payable"""
    try:
        collection = await get_collection("payables")
        payable_dict = payable.dict()
        payable_obj = Payable(**payable_dict)
        
        result = await collection.insert_one(payable_obj.dict())
        logger.info(f"Created payable: {payable_obj.description}")
        
        return payable_obj
    except Exception as e:
        logger.error(f"Error creating payable: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/payables", response_model=List[Payable])
async def get_payables(project_id: Optional[str] = None):
    """Get payables with optional project filter"""
    try:
        collection = await get_collection("payables")
        query = {}
        if project_id:
            query["projectId"] = project_id
        
        payables = await collection.find(query).to_list(1000)
        return [Payable(**serialize_doc(payable)) for payable in payables]
    except Exception as e:
        logger.error(f"Error fetching payables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Forecast Engine Endpoints
@api_router.get("/projects/{project_id}/weekly-forecast", response_model=List[WeeklyForecast])
async def get_weekly_forecast(project_id: str, weeks: int = 12):
    """Calculate weekly cashflow forecast for a project"""
    try:
        # Get project details
        project = await get_project(project_id)
        
        # Get invoices and payables for the project
        invoices = await get_invoices(project_id)
        payables = await get_payables(project_id)
        
        forecasts = []
        current_date = datetime.utcnow()
        
        for week in range(weeks):
            week_start = current_date + timedelta(weeks=week)
            week_end = week_start + timedelta(days=7)
            
            # Calculate inflows (invoices due)
            inflow = sum(
                invoice.total for invoice in invoices 
                if week_start <= invoice.dueDate <= week_end
            )
            
            # Calculate outflows (payables due)
            outflow = sum(
                payable.amount for payable in payables
                if week_start <= payable.dueDate <= week_end and payable.status.value == "open"
            )
            
            net = inflow - outflow
            alert = "Low cash flow" if net < 0 else None
            
            forecast = WeeklyForecast(
                projectId=project_id,
                weekOf=week_start,
                inflow=inflow,
                outflow=outflow,
                net=net,
                alert=alert,
                forecastNarrative=f"Week {week+1}: ${inflow:,.2f} inflow, ${outflow:,.2f} outflow, net ${net:,.2f}"
            )
            forecasts.append(forecast)
        
        return forecasts
    except Exception as e:
        logger.error(f"Error calculating weekly forecast for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/company/forecast", response_model=CompanyForecast)
async def get_company_forecast(weeks: int = 12):
    """Calculate company-wide forecast"""
    try:
        projects = await get_projects()
        active_projects = [p for p in projects if p.status == ProjectStatus.ACTIVE]
        project_ids = [p.id for p in active_projects]
        
        current_date = datetime.utcnow()
        total_inflow = 0
        total_outflow = 0
        successful_forecasts = 0
        
        # Aggregate from all project forecasts
        for project_id in project_ids:
            try:
                project_forecast = await get_weekly_forecast(project_id, 1)  # Just this week
                if project_forecast:
                    total_inflow += project_forecast[0].inflow
                    total_outflow += project_forecast[0].outflow
                    successful_forecasts += 1
            except Exception as e:
                logger.warning(f"Skipping forecast for project {project_id}: {e}")
                continue  # Skip projects with forecast errors
        
        net = total_inflow - total_outflow
        
        company_forecast = CompanyForecast(
            weekOf=current_date,
            totalInflow=total_inflow,
            totalOutflow=total_outflow,
            net=net,
            projects=project_ids,
            rollupNarrative=f"Company-wide: ${total_inflow:,.2f} expected inflow, ${total_outflow:,.2f} outflow, net ${net:,.2f} (based on {successful_forecasts} projects)"
        )
        
        return company_forecast
    except Exception as e:
        logger.error(f"Error calculating company forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/company/cash-runway", response_model=CashRunway)
async def get_cash_runway():
    """Calculate cash runway analysis"""
    try:
        company_forecast = await get_company_forecast(52)  # 1 year
        
        # Simple runway calculation
        weekly_burn = []
        cumulative_balance = []
        current_balance = 50000  # Starting balance (should come from settings)
        
        for week in range(52):
            # Simulate weekly burn
            weekly_expense = abs(company_forecast.totalOutflow) / 52 if company_forecast.totalOutflow < 0 else 1000
            weekly_income = company_forecast.totalInflow / 52 if company_forecast.totalInflow > 0 else 0
            
            net_burn = weekly_expense - weekly_income
            current_balance -= net_burn
            
            weekly_burn.append(net_burn)
            cumulative_balance.append(current_balance)
            
            if current_balance <= 0:
                break
        
        runway_weeks = len([b for b in cumulative_balance if b > 0])
        alert = "Critical: Less than 8 weeks runway" if runway_weeks < 8 else None
        
        next_invoice_date = datetime.utcnow() + timedelta(days=20)  # Based on billing day
        
        runway = CashRunway(
            nextInvoiceDate=next_invoice_date,
            weeklyBurn=weekly_burn[:12],  # Show 12 weeks
            cumulativeBalance=cumulative_balance[:12],
            runwayWeeks=runway_weeks,
            alert=alert,
            runwayNarrative=f"Cash runway: {runway_weeks} weeks based on current burn rate"
        )
        
        return runway
    except Exception as e:
        logger.error(f"Error calculating cash runway: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Analytics Endpoint
@api_router.get("/projects/{project_id}/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(project_id: str):
    """Get comprehensive project analytics with forecasting"""
    try:
        project = await get_project(project_id)
        tm_tags = await get_tm_tags(project_id)
        materials = await get_materials(project_id)
        expenses = await get_expenses(project_id)
        weekly_forecasts = await get_weekly_forecast(project_id, 12)
        
        # Calculate totals
        total_labor_cost = sum(tag.totalLaborCost for tag in tm_tags)
        total_labor_bill = sum(tag.totalLaborBill for tag in tm_tags)
        total_material_cost = sum(tag.totalMaterialCost for tag in tm_tags)
        total_material_bill = sum(tag.totalMaterialBill for tag in tm_tags)
        total_expense = sum(tag.totalExpense for tag in tm_tags)
        total_bill = sum(tag.totalBill for tag in tm_tags)
        
        profit_margin = ((total_bill - (total_labor_cost + total_material_cost + total_expense)) / total_bill * 100) if total_bill > 0 else 0
        
        analytics = ProjectAnalytics(
            projectId=project_id,
            contractType=project.contractType,
            totalLaborCost=total_labor_cost,
            totalLaborBill=total_labor_bill,
            totalMaterialCost=total_material_cost,
            totalMaterialBill=total_material_bill,
            totalExpense=total_expense,
            totalBill=total_bill,
            profitMargin=profit_margin,
            weeklyForecasts=weekly_forecasts,
            forecastNarrative=f"Project analytics: ${total_bill:,.2f} total billing, {profit_margin:.1f}% margin"
        )
        
        return analytics
    except Exception as e:
        logger.error(f"Error calculating project analytics for {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/company/analytics", response_model=CompanyAnalytics)
async def get_company_analytics():
    """Get company-wide analytics"""
    try:
        projects = await get_projects()
        active_projects = [p for p in projects if p.status == ProjectStatus.ACTIVE]
        
        # Calculate company totals
        total_revenue = 0
        total_costs = 0
        successful_analytics = 0
        
        for project in active_projects:
            try:
                project_analytics = await get_project_analytics(project.id)
                total_revenue += project_analytics.totalBill
                total_costs += project_analytics.totalLaborCost + project_analytics.totalMaterialCost + project_analytics.totalExpense
                successful_analytics += 1
            except Exception as e:
                logger.warning(f"Skipping analytics for project {project.id}: {e}")
                continue  # Skip projects with errors
        
        net_profit = total_revenue - total_costs
        
        # Get company forecast and cash runway with error handling
        try:
            company_forecast = await get_company_forecast()
        except Exception as e:
            logger.warning(f"Company forecast failed: {e}")
            # Create a default forecast
            company_forecast = CompanyForecast(
                weekOf=datetime.utcnow(),
                totalInflow=0,
                totalOutflow=0,
                net=0,
                projects=[],
                rollupNarrative="Company forecast unavailable"
            )
        
        try:
            cash_runway = await get_cash_runway()
        except Exception as e:
            logger.warning(f"Cash runway failed: {e}")
            # Create a default runway
            cash_runway = CashRunway(
                nextInvoiceDate=datetime.utcnow() + timedelta(days=20),
                weeklyBurn=[],
                cumulativeBalance=[],
                runwayWeeks=0,
                runwayNarrative="Cash runway analysis unavailable"
            )
        
        analytics = CompanyAnalytics(
            totalProjects=len(projects),
            activeProjects=len(active_projects),
            totalRevenue=total_revenue,
            totalCosts=total_costs,
            netProfit=net_profit,
            weeklyForecast=company_forecast,
            cashRunway=cash_runway,
            rollupNarrative=f"Company performance: {len(active_projects)} active projects, ${total_revenue:,.2f} revenue, ${net_profit:,.2f} profit (based on {successful_analytics} projects with complete data)"
        )
        
        return analytics
    except Exception as e:
        logger.error(f"Error calculating company analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "collections": COLLECTIONS,
        "timestamp": datetime.utcnow()
    }

# GC PIN SYSTEM FUNCTIONS

def generate_project_pin():
    """Generate a unique 4-digit PIN for project access"""
    return f"{random.randint(1000, 9999)}"

async def ensure_project_has_pin(project_id: str):
    """Ensure project has a GC access PIN, generate if missing"""
    try:
        projects_collection = await get_collection("projects")
        
        # Try to find project by id field first, then by _id field
        project = await projects_collection.find_one({"id": project_id})
        if not project:
            # Try finding by _id field (for unified schema)
            try:
                from bson import ObjectId
                if ObjectId.is_valid(project_id):
                    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
                else:
                    project = await projects_collection.find_one({"_id": project_id})
            except:
                pass
        
        if not project:
            return None
            
        # Check if project has a PIN
        if not project.get("gc_pin"):
            # Generate new PIN
            new_pin = generate_project_pin()
            
            # Make sure PIN is unique across all projects
            while await projects_collection.find_one({"gc_pin": new_pin}):
                new_pin = generate_project_pin()
            
            # Update project with new PIN
            update_query = {"id": project_id} if "id" in project else {"_id": project.get("_id")}
            await projects_collection.update_one(
                update_query,
                {"$set": {"gc_pin": new_pin, "gc_pin_used": False}}
            )
            
            logger.info(f"Generated new PIN for project {project_id}: {new_pin}")
            return new_pin
        
        return project.get("gc_pin")
        
    except Exception as e:
        logger.error(f"Error ensuring project PIN: {e}")
        return None

# GC DASHBOARD API ROUTES - SIMPLIFIED PIN SYSTEM

@api_router.get("/projects/{project_id}/gc-pin")
async def get_project_gc_pin(project_id: str):
    """Admin: Get current GC PIN for project"""
    try:
        projects_collection = await get_collection("projects")
        
        # Try to find project by id field first, then by _id field
        project = await projects_collection.find_one({"id": project_id})
        if not project:
            # Try finding by _id field (for unified schema)
            try:
                from bson import ObjectId
                if ObjectId.is_valid(project_id):
                    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
                else:
                    project = await projects_collection.find_one({"_id": project_id})
            except:
                pass
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # ALWAYS generate a new PIN for admin access (not just when missing)
        pin = generate_project_pin()
        
        # Make sure PIN is unique across all projects
        while await projects_collection.find_one({"gc_pin": pin}):
            pin = generate_project_pin()
        
        # Update project with new PIN using the same criteria we used to find it
        if project.get("id") == project_id:
            # Found by id field
            update_result = await projects_collection.update_one(
                {"id": project_id},
                {"$set": {"gc_pin": pin, "gc_pin_used": False}}
            )
        else:
            # Found by _id field  
            update_result = await projects_collection.update_one(
                {"_id": project["_id"]},
                {"$set": {"gc_pin": pin, "gc_pin_used": False}}
            )
        
        logger.info(f"Generated NEW PIN for project {project_id}: {pin} (Updated {update_result.modified_count} documents)")
        
        return {
            "projectId": project_id,
            "projectName": project.get("name", "Unknown Project"),
            "gcPin": pin,
            "pinUsed": False  # Always false since we just generated it
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project GC PIN: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/gc/login-simple")
async def gc_login_simple(login_data: dict):
    """GC: Simple login with project ID and PIN"""
    try:
        # Handle both dict and request body formats
        if hasattr(login_data, 'dict'):
            data = login_data.dict()
        else:
            data = login_data
            
        project_id = data.get("projectId")
        pin = data.get("pin")  
        ip = data.get("ip", "unknown")
        
        logger.info(f"GC login attempt: projectId={project_id}, pin={pin}")
        
        if not project_id or not pin:
            logger.error("Missing projectId or pin in request")
            raise HTTPException(status_code=400, detail="Project ID and PIN required")
        
        # Find project with matching PIN
        projects_collection = await get_collection("projects")
        
        # Try to find project by id field first, then by _id field
        project = await projects_collection.find_one({
            "id": project_id,
            "gc_pin": pin,
            "gc_pin_used": False
        })
        
        if not project:
            # Try finding by _id field (for unified schema)
            try:
                from bson import ObjectId
                if ObjectId.is_valid(project_id):
                    project = await projects_collection.find_one({
                        "_id": ObjectId(project_id),
                        "gc_pin": pin,
                        "gc_pin_used": False
                    })
                else:
                    project = await projects_collection.find_one({
                        "_id": project_id,
                        "gc_pin": pin,
                        "gc_pin_used": False
                    })
            except:
                pass
        
        if not project:
            # Log failed access
            await gc_access_logs_collection.insert_one({
                "id": str(uuid.uuid4()),
                "projectId": project_id,
                "timestamp": datetime.now(),
                "ip": ip,
                "status": "failed",
                "userAgent": login_data.get("userAgent", ""),
                "failureReason": "Invalid PIN or PIN already used"
            })
            raise HTTPException(status_code=401, detail="Invalid PIN or PIN already used")
        
        # Mark PIN as used and generate new one
        new_pin = generate_project_pin()
        
        # Ensure new PIN is unique
        while await projects_collection.find_one({"gc_pin": new_pin}):
            new_pin = generate_project_pin()
        
        # Update project with new PIN
        update_query = {"id": project_id} if "id" in project else {"_id": project.get("_id")}
        await projects_collection.update_one(
            update_query,
            {"$set": {
                "gc_pin": new_pin,
                "gc_pin_used": False,
                "gc_last_access": datetime.now(),
                "gc_last_ip": ip
            }}
        )
        
        # Log successful access
        await gc_access_logs_collection.insert_one({
            "id": str(uuid.uuid4()),
            "projectId": project_id,
            "timestamp": datetime.now(),
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

@api_router.post("/gc/validate-pin")
async def gc_validate_pin_only(pin_data: dict):
    """GC: Secure PIN validation without exposing project data"""
    try:
        pin = pin_data.get("pin")
        ip = pin_data.get("ip", "unknown")
        
        if not pin or len(pin) != 4:
            raise HTTPException(status_code=400, detail="4-digit PIN required")
        
        logger.info(f"GC PIN validation attempt from {ip}")
        
        # Find project with matching PIN (without exposing all project data)
        projects_collection = await get_collection("projects")
        
        project = await projects_collection.find_one({
            "gc_pin": pin,
            "gc_pin_used": False
        })
        
        if not project:
            # Log failed attempt
            await gc_access_logs_collection.insert_one({
                "id": str(uuid.uuid4()),
                "projectId": "unknown",
                "timestamp": datetime.now(),
                "ip": ip,
                "status": "failed",
                "usedPin": pin
            })
            raise HTTPException(status_code=401, detail="Invalid PIN or PIN already used")
        
        # Generate new PIN for security
        new_pin = str(random.randint(1000, 9999))
        
        # Update project with new PIN and mark old one as used
        await projects_collection.update_one(
            {"id": project.get("id") or project.get("_id")},
            {"$set": {
                "gc_pin": new_pin,
                "gc_pin_used": False,
                "gc_last_access": datetime.now(),
                "gc_last_ip": ip
            }}
        )
        
        # Log successful validation
        await gc_access_logs_collection.insert_one({
            "id": str(uuid.uuid4()),
            "projectId": project.get("id") or str(project.get("_id")),
            "timestamp": datetime.now(),
            "ip": ip,
            "status": "success",
            "usedPin": pin,
            "newPin": new_pin
        })
        
        logger.info(f"GC PIN validation successful. Old PIN: {pin}, New PIN: {new_pin}")
        
        return {
            "success": True,
            "projectId": project.get("id") or str(project.get("_id")),
            "projectName": project.get("name", "Unknown Project"),
            "message": "PIN validated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during PIN validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gc/dashboard/{project_id}", response_model=GcProjectDashboard)
async def get_gc_dashboard(project_id: str):
    """GC: Get project dashboard (no financial data)"""
    try:
        projects_collection = await get_collection("projects")
        
        # Try to find project by id field first, then by _id field
        project = await projects_collection.find_one({"id": project_id})
        if not project:
            # Try finding by _id field (for unified schema)
            try:
                from bson import ObjectId
                if ObjectId.is_valid(project_id):
                    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
                else:
                    project = await projects_collection.find_one({"_id": project_id})
            except:
                pass
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get crew logs for this project
        crew_logs_collection = await get_collection("crew_logs")
        crew_logs = await crew_logs_collection.find({"project_id": project_id}).to_list(length=None)
        
        # Calculate crew summary (hours/days only, no financial data)
        total_hours = 0
        total_days = len(set(log.get("date", "") for log in crew_logs if log.get("date")))
        active_crew_members = len(set(member.get("name", "") for log in crew_logs for member in log.get("crew", [])))
        recent_descriptions = []
        
        for log in crew_logs:
            # Sum up all crew member hours
            for member in log.get("crew", []):
                total_hours += member.get("straight_time", 0)
                total_hours += member.get("overtime", 0)
                total_hours += member.get("double_time", 0)
                total_hours += member.get("premium_overtime", 0)
            
            # Collect recent work descriptions
            if log.get("work_description"):
                recent_descriptions.append(log["work_description"])
        
        crew_summary = GcCrewSummary(
            totalHours=total_hours,
            totalDays=total_days,
            activeCrewMembers=active_crew_members,
            recentDescriptions=recent_descriptions[-5:]  # Last 5 descriptions
        )
        
        # Get materials for this project (quantities only)
        materials_collection = await get_collection("materials")
        materials = await materials_collection.find({"project_id": project_id}).to_list(length=None)
        
        materials_summary = []
        for material in materials:
            materials_summary.append({
                "item": material.get("item", "Unknown Item"),
                "vendor": material.get("vendor", "Unknown Vendor"),
                "quantity": material.get("quantity", "N/A"),
                "date": material.get("date", "")
            })
        
        # Get T&M tags for this project (counts/hours only)
        tm_tags_collection = await get_collection("tm_tags")
        tm_tags = await tm_tags_collection.find({"project_id": project_id}).to_list(length=None)
        
        total_tm_hours = 0
        approved_tags = 0
        submitted_tags = 0
        recent_tag_titles = []
        
        for tag in tm_tags:
            # Count hours from labor entries
            for entry in tag.get("entries", []):
                if entry.get("category") == "Labor":
                    total_tm_hours += entry.get("hours", 0)
            
            # Count status
            status = tag.get("status", "")
            if status.lower() in ["approved", "submitted"]:
                approved_tags += 1
            if status.lower() == "submitted":
                submitted_tags += 1
            
            # Collect recent tag titles
            if tag.get("tm_tag_title") or tag.get("title"):
                recent_tag_titles.append(tag.get("tm_tag_title") or tag.get("title"))
        
        tm_tag_summary = GcTmTagSummary(
            totalTags=len(tm_tags),
            approvedTags=approved_tags,
            submittedTags=submitted_tags,
            totalHours=total_tm_hours,
            recentTagTitles=recent_tag_titles[-5:]  # Last 5 tag titles
        )
        
        # Get project phases (mock data for now)
        phases = [
            ProjectPhaseModel(
                id=str(uuid.uuid4()),
                projectId=project_id,
                phase="design",
                percentComplete=100,
                plannedDate=datetime.now(),
                actualDate=datetime.now()
            ),
            ProjectPhaseModel(
                id=str(uuid.uuid4()),
                projectId=project_id,
                phase="installation",
                percentComplete=75,
                plannedDate=datetime.now() + timedelta(days=30),
                actualDate=None
            )
        ]
        
        # Get inspection data from project
        inspections = {
            "rough_inspection_status": project.get("rough_inspection_status", "pending"),
            "rough_inspection_date": project.get("rough_inspection_date"),
            "rough_inspection_notes": project.get("rough_inspection_notes"),
            "final_inspection_status": project.get("final_inspection_status", "pending"),
            "final_inspection_date": project.get("final_inspection_date"),
            "final_inspection_notes": project.get("final_inspection_notes")
        }
        
        # Build dashboard response
        dashboard = GcProjectDashboard(
            projectId=project_id,
            projectName=project.get("name", "Unknown Project"),
            projectLocation=project.get("address", ""),
            projectStatus=project.get("status", "active"),
            overallProgress=75.0,  # Mock calculation
            lastUpdated=datetime.now(),
            crewSummary=crew_summary,
            materials=materials_summary,
            tmTagSummary=tm_tag_summary,
            phases=phases,
            inspections=inspections,
            narrative=f"Project {project.get('name', 'Unknown')} is progressing well with {total_hours:.1f} hours logged across {total_days} work days."
        )
        
        return dashboard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching GC dashboard for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function for admin endpoints
async def get_project_by_id(project_id: str):
    """Get project by ID from the appropriate collection"""
    try:
        # Try projects_new collection first (unified schema)
        projects_collection = await get_collection("projects_new")
        project = await projects_collection.find_one({"id": project_id})
        
        if not project:
            # Fallback to projects collection
            projects_collection = await get_collection("projects")
            project = await projects_collection.find_one({"id": project_id})
        
        return project
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        return None

# GC ADMIN ENDPOINTS
@api_router.get("/gc/keys/admin", response_model=List[GcKeyAdmin])
async def get_gc_keys_admin():
    """Admin: Get all GC keys for management"""
    try:
        keys = await gc_keys_collection.find({}).sort("createdAt", -1).to_list(1000)
        admin_keys = []
        
        for key in keys:
            # Get project info
            project = await get_project_by_id(key["projectId"])
            project_name = project.get("name", "Unknown Project") if project else "Unknown Project"
            
            admin_key = GcKeyAdmin(
                id=key["id"],
                projectName=project_name,
                keyLastFour=key["key"][-4:],
                expiresAt=key["expiresAt"],
                active=key.get("active", True),
                used=key.get("used", False),
                usedAt=key.get("usedAt")
            )
            admin_keys.append(admin_key)
        
        return admin_keys
    except Exception as e:
        logger.error(f"Error fetching admin GC keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/gc/access-logs/admin", response_model=List[GcAccessLogAdmin])
async def get_gc_access_logs_admin():
    """Admin: Get all GC access logs"""
    try:
        logs = await gc_access_logs_collection.find({}).sort("timestamp", -1).to_list(1000)
        admin_logs = []
        
        for log in logs:
            # Get project info
            project_id = log.get("projectId", "unknown")
            if project_id != "unknown":
                project = await get_project_by_id(project_id)
                project_name = project.get("name", "Unknown Project") if project else "Unknown Project"
            else:
                project_name = "Unknown Project"
            
            # For access logs, we don't have gcKeyId, so we'll use the PIN info
            key_last_four = log.get("usedPin", "****")[-4:] if log.get("usedPin") else "****"
            
            admin_log = GcAccessLogAdmin(
                id=log["id"],
                projectName=project_name,
                keyLastFour=key_last_four,
                timestamp=log["timestamp"],
                ip=log.get("ip", "unknown"),
                status=log["status"],
                userAgent=log.get("userAgent")
            )
            admin_logs.append(admin_log)
        
        return admin_logs
    except Exception as e:
        logger.error(f"Error fetching admin access logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router in app (after all routes are defined)
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)