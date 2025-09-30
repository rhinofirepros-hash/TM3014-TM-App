"""
Seed Rhino Platform with Sample Data
Creates initial installers, projects, and time logs based on specification
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def seed_rhino_platform():
    """Seed the Rhino Platform with initial data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.rhino_platform
    
    logger.info("Seeding Rhino Platform with sample data...")
    
    try:
        # 1. Create Installers (cost-only, no GC billing rates)
        await seed_installers(db)
        
        # 2. Create Projects with T&M rates
        await seed_projects(db)
        
        # 3. Create sample time logs
        await seed_time_logs(db)
        
        # 4. Create per diem/hotel entries
        await seed_per_diem_hotels(db)
        
        # 5. Verify data
        await verify_seed_data(db)
        
        logger.info("Seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        raise
    finally:
        client.close()

async def seed_installers(db):
    """Create sample installers with cost rates only"""
    logger.info("Seeding installers...")
    
    installers = [
        {
            "id": "inst-001",
            "name": "Mike Rodriguez",
            "cost_rate": 65.00,  # Company cost, not billing rate
            "position": "Senior Sprinkler Technician",
            "active": True,
            "hire_date": "2024-03-15",
            "phone": "(619) 555-0101",
            "email": "mike.rodriguez@rhinofirepro.com",
            "created_at": datetime.now()
        },
        {
            "id": "inst-002", 
            "name": "Sarah Johnson",
            "cost_rate": 58.00,
            "position": "Sprinkler Installer", 
            "active": True,
            "hire_date": "2024-06-01",
            "phone": "(619) 555-0102",
            "email": "sarah.johnson@rhinofirepro.com",
            "created_at": datetime.now()
        },
        {
            "id": "inst-003",
            "name": "David Chen",
            "cost_rate": 72.00,
            "position": "Master Electrician",
            "active": True,
            "hire_date": "2023-11-20",
            "phone": "(619) 555-0103", 
            "email": "david.chen@rhinofirepro.com",
            "created_at": datetime.now()
        },
        {
            "id": "inst-004",
            "name": "Jesus Garcia",
            "cost_rate": 68.00,
            "position": "Project Supervisor",
            "active": True,
            "hire_date": "2023-08-10",
            "phone": "(619) 555-0104",
            "email": "jesus.garcia@rhinofirepro.com",
            "created_at": datetime.now()
        },
        {
            "id": "inst-005",
            "name": "Maria Gonzalez",
            "cost_rate": 55.00,
            "position": "Apprentice Installer",
            "active": True,
            "hire_date": "2025-01-15",
            "phone": "(619) 555-0105",
            "email": "maria.gonzalez@rhinofirepro.com",
            "created_at": datetime.now()
        }
    ]
    
    for installer in installers:
        await db.installers.update_one(
            {"id": installer["id"]},
            {"$set": installer},
            upsert=True
        )
    
    logger.info(f"Seeded {len(installers)} installers")

async def seed_projects(db):
    """Create sample projects with proper billing types and T&M rates"""
    logger.info("Seeding projects...")
    
    projects = [
        {
            "id": "proj-3rd-ave",
            "name": "3rd Ave",
            "billing_type": "TM",
            "tm_bill_rate": 95.00,  # T&M projects MUST have billing rate
            "description": "Fire Protection system completion. T&M Project",
            "client_company": "Nuera Contracting LP",
            "project_manager": "Jesus Garcia", 
            "address": "3104 Third Ave, San Diego, CA",
            "status": "active",
            "start_date": "2025-09-17",
            "contract_amount": None,  # T&M projects don't have fixed contract amounts
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": "proj-oregon-st",
            "name": "Oregon St",
            "billing_type": "TM", 
            "tm_bill_rate": 90.00,  # Different T&M rate per project
            "description": "Fire Sprinkler system installation to complete project",
            "client_company": "Camelot Development Group Inc",
            "project_manager": "Jesus Garcia",
            "address": "4060 N Oregon St, San Diego, CA 92104", 
            "status": "active",
            "start_date": "2025-09-22",
            "contract_amount": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": "proj-downtown-fixed",
            "name": "Downtown Office Complex",
            "billing_type": "Fixed",
            "tm_bill_rate": None,  # Fixed projects don't have T&M rates
            "description": "Complete fire suppression system - fixed bid project",
            "client_company": "Downtown Development LLC",
            "project_manager": "Jesus Garcia",
            "address": "1200 Broadway, San Diego, CA",
            "status": "active", 
            "start_date": "2025-08-01",
            "contract_amount": 125000.00,  # Fixed contract amount
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": "proj-hospital-sov",
            "name": "Hospital Addition SOV",
            "billing_type": "SOV",
            "tm_bill_rate": None,  # SOV projects don't use T&M rates
            "description": "Schedule of Values project for hospital fire systems",
            "client_company": "Medical Center Construction",
            "project_manager": "David Chen", 
            "address": "5500 Hospital Way, San Diego, CA",
            "status": "active",
            "start_date": "2025-07-15",
            "contract_amount": 200000.00,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    for project in projects:
        await db.projects.update_one(
            {"id": project["id"]},
            {"$set": project},
            upsert=True
        )
    
    logger.info(f"Seeded {len(projects)} projects")

async def seed_time_logs(db):
    """Create sample time logs demonstrating T&M vs non-T&M calculations"""
    logger.info("Seeding time logs...")
    
    time_logs = [
        # T&M Project: 3rd Ave - uses project's T&M rate of $95/hr
        {
            "id": "tl-001",
            "date": "2025-09-25",
            "installer_id": "inst-001",  # Mike Rodriguez ($65/hr cost)
            "project_id": "proj-3rd-ave",  # T&M at $95/hr
            "hours": 8.0,
            "bill_rate_override": None,  # Use project rate
            "notes": "Installed main sprinkler lines",
            "created_at": datetime.now()
        },
        {
            "id": "tl-002", 
            "date": "2025-09-25",
            "installer_id": "inst-002",  # Sarah Johnson ($58/hr cost)
            "project_id": "proj-3rd-ave",  # T&M at $95/hr
            "hours": 7.5,
            "bill_rate_override": None,
            "notes": "Assisted with main line installation",
            "created_at": datetime.now()
        },
        # T&M Project: Oregon St - uses different T&M rate of $90/hr
        {
            "id": "tl-003",
            "date": "2025-09-26",
            "installer_id": "inst-003",  # David Chen ($72/hr cost)
            "project_id": "proj-oregon-st",  # T&M at $90/hr
            "hours": 6.0,
            "bill_rate_override": None,
            "notes": "Electrical connections for sprinkler system",
            "created_at": datetime.now()
        },
        # T&M with override rate
        {
            "id": "tl-004",
            "date": "2025-09-26", 
            "installer_id": "inst-004",  # Jesus Garcia ($68/hr cost)
            "project_id": "proj-3rd-ave",  # T&M at $95/hr normally
            "hours": 4.0,
            "bill_rate_override": 110.00,  # Special rate for supervision
            "notes": "Project supervision and quality control",
            "created_at": datetime.now()
        },
        # Fixed Project - no T&M billing calculations
        {
            "id": "tl-005",
            "date": "2025-09-27",
            "installer_id": "inst-001",  # Mike Rodriguez ($65/hr cost)  
            "project_id": "proj-downtown-fixed",  # Fixed project
            "hours": 8.0,
            "bill_rate_override": None,
            "notes": "Downtown office complex work",
            "created_at": datetime.now()
        },
        # SOV Project - no T&M billing calculations
        {
            "id": "tl-006",
            "date": "2025-09-27",
            "installer_id": "inst-005",  # Maria Gonzalez ($55/hr cost)
            "project_id": "proj-hospital-sov",  # SOV project
            "hours": 6.5,
            "bill_rate_override": None,
            "notes": "Hospital addition prep work",
            "created_at": datetime.now()
        }
    ]
    
    for log in time_logs:
        await db.time_logs.update_one(
            {"id": log["id"]},
            {"$set": log},
            upsert=True
        )
    
    logger.info(f"Seeded {len(time_logs)} time log entries")

async def seed_per_diem_hotels(db):
    """Create sample per diem and hotel entries"""
    logger.info("Seeding per diem/hotel entries...")
    
    entries = [
        {
            "id": "pdh-001",
            "date": "2025-09-25",
            "project_id": "proj-3rd-ave",
            "workers": 2,
            "per_diem_per_worker": 40.00,
            "days": 1,
            "nights": 1, 
            "rooms": 1,
            "hotel_rate": 125.00,
            "notes": "Overnight work for 3rd Ave project",
            "created_at": datetime.now()
        },
        {
            "id": "pdh-002",
            "date": "2025-09-28",
            "project_id": "proj-downtown-fixed",
            "workers": 3,
            "per_diem_per_worker": 45.00,  # Higher rate for downtown
            "days": 2,
            "nights": 1,
            "rooms": 2,
            "hotel_rate": 150.00,
            "notes": "Multi-day downtown project work",
            "created_at": datetime.now()
        }
    ]
    
    for entry in entries:
        await db.per_diem_hotels.update_one(
            {"id": entry["id"]},
            {"$set": entry},
            upsert=True
        )
    
    logger.info(f"Seeded {len(entries)} per diem/hotel entries")

async def verify_seed_data(db):
    """Verify seeded data and show T&M calculations"""
    logger.info("Verifying seeded data...")
    
    # Count records
    installers_count = await db.installers.count_documents({})
    projects_count = await db.projects.count_documents({})
    time_logs_count = await db.time_logs.count_documents({})
    tm_projects_count = await db.projects.count_documents({"billing_type": "TM"})
    
    logger.info(f"Verification results:")
    logger.info(f"  - Installers: {installers_count}")
    logger.info(f"  - Projects: {projects_count} (T&M: {tm_projects_count})")
    logger.info(f"  - Time Logs: {time_logs_count}")
    
    # Show sample T&M calculations
    logger.info(f"Sample T&M calculations:")
    
    # Example: Mike Rodriguez on 3rd Ave project
    # Cost: $65/hr, Bill Rate: $95/hr, Hours: 8.0
    # Labor Cost: $65 * 8 = $520
    # Billable: $95 * 8 = $760  
    # Profit: $760 - $520 = $240
    logger.info(f"  Mike on 3rd Ave: 8h * $65 cost = $520 labor cost, 8h * $95 bill = $760 billable, $240 profit")
    
    # Example: David Chen on Oregon St project
    # Cost: $72/hr, Bill Rate: $90/hr, Hours: 6.0
    # Labor Cost: $72 * 6 = $432
    # Billable: $90 * 6 = $540
    # Profit: $540 - $432 = $108  
    logger.info(f"  David on Oregon St: 6h * $72 cost = $432 labor cost, 6h * $90 bill = $540 billable, $108 profit")
    
    logger.info("Data verification complete")

if __name__ == "__main__":
    asyncio.run(seed_rhino_platform())