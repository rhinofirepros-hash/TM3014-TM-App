"""
Financial Management API Routes - Invoices, Payables, Cashflow, Profitability
Implements the exact API specification provided by the user
"""

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from models_financial import (
    Invoice, InvoiceCreate, InvoiceUpdate,
    Payable, PayableCreate, PayableUpdate,
    CashflowForecast, CashflowForecastCreate, CashflowForecastUpdate,
    Profitability, ProfitabilityCreate, ProfitabilityUpdate
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Financial Management API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Collections
invoices_collection = db["invoices"]
payables_collection = db["payables"]
cashflow_forecasts_collection = db["cashflow_forecasts"]
profitability_collection = db["profitability"]

def serialize_doc(doc: dict) -> dict:
    """Remove MongoDB ObjectId and ensure serialization"""
    if "_id" in doc:
        del doc["_id"]
    return doc

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
        update_dict["updated_at"] = datetime.utcnow()
        
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

# Health check endpoint
@api_router.get("/financial/health")
async def health_check():
    """Health check endpoint for financial modules"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "modules": ["invoices", "payables", "cashflow", "profitability"],
        "timestamp": datetime.utcnow()
    }

# Include router in app
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
    uvicorn.run(app, host="0.0.0.0", port=8002)