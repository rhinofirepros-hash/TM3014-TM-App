#!/usr/bin/env python3
"""
Debug project name resolution in access logs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def debug_project_names():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check access logs
    gc_access_logs_collection = db["gc_access_logs"]
    
    print("Debugging project name resolution...")
    
    # Get a recent successful log
    recent_log = await gc_access_logs_collection.find_one(
        {"status": "success", "projectId": {"$ne": "unknown"}},
        sort=[("timestamp", -1)]
    )
    
    if recent_log:
        project_id = recent_log.get("projectId")
        print(f"Recent log project ID: {project_id}")
        
        # Check both project collections
        projects_collection = db["projects"]
        projects_new_collection = db["projects_new"]
        
        project_old = await projects_collection.find_one({"id": project_id})
        project_new = await projects_new_collection.find_one({"id": project_id})
        
        print(f"Project in 'projects' collection: {project_old is not None}")
        if project_old:
            print(f"  Name: {project_old.get('name', 'No name')}")
        
        print(f"Project in 'projects_new' collection: {project_new is not None}")
        if project_new:
            print(f"  Name: {project_new.get('name', 'No name')}")
    else:
        print("No recent successful logs found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_project_names())