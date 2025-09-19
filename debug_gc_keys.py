#!/usr/bin/env python3
"""
Debug GC keys data structure
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def debug_gc_keys():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check GC keys collection
    gc_keys_collection = db["gc_keys"]
    
    print("Debugging GC Keys data structure...")
    
    # Get one sample key
    sample_key = await gc_keys_collection.find_one({})
    
    if sample_key:
        print("Sample GC key structure:")
        for field, value in sample_key.items():
            print(f"  {field}: {value} ({type(value).__name__})")
    else:
        print("No GC keys found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_gc_keys())