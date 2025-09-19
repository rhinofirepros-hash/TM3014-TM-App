#!/usr/bin/env python3
"""
Check if access logs are being created in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def check_access_logs():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check access logs collection
    gc_access_logs_collection = db["gc_access_logs"]
    
    print("Checking GC Access Logs in database...")
    
    # Count total logs
    total_logs = await gc_access_logs_collection.count_documents({})
    print(f"Total access logs in database: {total_logs}")
    
    if total_logs > 0:
        # Get recent logs
        recent_logs = await gc_access_logs_collection.find({}).sort("timestamp", -1).limit(10).to_list(10)
        
        print("\nRecent access logs:")
        for i, log in enumerate(recent_logs, 1):
            timestamp = log.get("timestamp", "Unknown")
            project_id = log.get("projectId", "Unknown")
            status = log.get("status", "Unknown")
            ip = log.get("ip", "Unknown")
            print(f"{i}. {timestamp} - Project: {project_id} - Status: {status} - IP: {ip}")
    else:
        print("No access logs found in database")
    
    # Check GC keys collection
    gc_keys_collection = db["gc_keys"]
    total_keys = await gc_keys_collection.count_documents({})
    print(f"\nTotal GC keys in database: {total_keys}")
    
    if total_keys > 0:
        keys = await gc_keys_collection.find({}).limit(5).to_list(5)
        print("\nSample GC keys:")
        for i, key in enumerate(keys, 1):
            key_id = key.get("id", "Unknown")
            project_id = key.get("projectId", "Unknown")
            key_value = key.get("key", "Unknown")
            print(f"{i}. Key ID: {key_id} - Project: {project_id} - Key: {key_value[:4]}****")
    else:
        print("No GC keys found in database")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_access_logs())