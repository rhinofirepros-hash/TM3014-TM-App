#!/usr/bin/env python3
"""
Test to verify the date serialization issue
"""

from datetime import date, datetime
import json
from pydantic import BaseModel, Field
from typing import Optional

class TestInstaller(BaseModel):
    name: str
    cost_rate: float
    hire_date: Optional[date] = None

# Test the issue
print("Testing date serialization issue...")

# Create installer with date
installer_data = {
    "name": "Test Installer",
    "cost_rate": 33.0,
    "hire_date": "2025-09-30"
}

print(f"Input data: {installer_data}")

# Create Pydantic model
installer = TestInstaller(**installer_data)
print(f"Pydantic model: {installer}")
print(f"hire_date type: {type(installer.hire_date)}")

# Try to convert to dict (this should work)
installer_dict = installer.dict()
print(f"Model dict: {installer_dict}")
print(f"hire_date in dict type: {type(installer_dict['hire_date'])}")

# Try to JSON serialize (this might fail)
try:
    json_str = json.dumps(installer_dict)
    print(f"JSON serialization: SUCCESS")
    print(f"JSON: {json_str}")
except Exception as e:
    print(f"JSON serialization: FAILED - {e}")

# Try to JSON serialize with default handler
try:
    json_str = json.dumps(installer_dict, default=str)
    print(f"JSON with default=str: SUCCESS")
    print(f"JSON: {json_str}")
except Exception as e:
    print(f"JSON with default=str: FAILED - {e}")