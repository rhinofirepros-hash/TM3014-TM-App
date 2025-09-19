#!/usr/bin/env python3
"""
Debug which collection projects are stored in
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def debug_project_collections():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    project_id = "68cc802f8d44fcd8015b39b8"
    
    print(f"Looking for project {project_id} in different collections...")
    
    # Check all possible project collections
    collections_to_check = ["projects", "projects_new", "projects_unified"]
    
    for collection_name in collections_to_check:
        collection = db[collection_name]
        count = await collection.count_documents({})
        project = await collection.find_one({"id": project_id})
        
        print(f"{collection_name}: {count} total documents, project found: {project is not None}")
        if project:
            print(f"  Project name: {project.get('name', 'No name')}")
    
    # Also check what collections exist
    collections = await db.list_collection_names()
    project_collections = [c for c in collections if 'project' in c.lower()]
    print(f"\nAll project-related collections: {project_collections}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_project_collections())