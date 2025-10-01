#!/usr/bin/env python3
"""
PRODUCTION API STRUCTURE ANALYSIS
Testing exact API structure differences between preview and production
"""

import requests
import json
import sys
from datetime import datetime
import uuid

PRODUCTION_URL = "https://tm3014-tm-app-production.up.railway.app"
API_URL = f"{PRODUCTION_URL}/api"

print(f"🔍 PRODUCTION API STRUCTURE ANALYSIS")
print(f"🌐 Production URL: {PRODUCTION_URL}")
print("=" * 80)

def make_request(method, endpoint, data=None):
    try:
        url = f"{API_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# =============================================================================
# TEST 1: INSTALLER API STRUCTURE
# =============================================================================
print("\n🔍 TEST 1: INSTALLER API STRUCTURE ANALYSIS")

# Get existing installer structure
response, error = make_request("GET", "/installers")
if response and response.status_code == 200:
    installers = response.json()
    if installers:
        print("✅ Existing installer structure:")
        print(json.dumps(installers[0], indent=2))
        
        # Test with correct structure
        test_installer = {
            "name": "Production API Test Worker",
            "cost_rate": 33.0,  # Using cost_rate instead of hourly_rate
            "position": "Electrician",
            "phone": "555-0123",
            "email": "test@production.com"
        }
        
        print(f"\n📝 Testing installer creation with correct structure:")
        response, error = make_request("POST", "/installers", test_installer)
        if error:
            print(f"❌ Connection error: {error}")
        else:
            print(f"✅ Status: {response.status_code}")
            if response.status_code == 200:
                created = response.json()
                print(f"✅ Created installer: {created.get('id')}")
                print(json.dumps(created, indent=2))
            else:
                print(f"❌ Response: {response.text}")

# =============================================================================
# TEST 2: T&M TAGS API STRUCTURE
# =============================================================================
print("\n🔍 TEST 2: T&M TAGS API STRUCTURE ANALYSIS")

# Get existing T&M tag structure
response, error = make_request("GET", "/tm-tags")
if response and response.status_code == 200:
    tm_tags = response.json()
    if tm_tags:
        print("✅ Existing T&M tag structure:")
        print(json.dumps(tm_tags[0], indent=2))
    else:
        print("⚠️  No existing T&M tags found")

# Get projects and installers for test
projects_response, _ = make_request("GET", "/projects")
installers_response, _ = make_request("GET", "/installers")

project_id = None
installer_id = None

if projects_response and projects_response.status_code == 200:
    projects = projects_response.json()
    if projects:
        project_id = projects[0].get('id')
        print(f"✅ Using project ID: {project_id}")

if installers_response and installers_response.status_code == 200:
    installers = installers_response.json()
    if installers:
        installer_id = installers[0].get('id')
        print(f"✅ Using installer ID: {installer_id}")

if project_id and installer_id:
    # Test T&M tag creation with correct structure
    test_tm_tag = {
        "project_id": project_id,
        "installer_id": installer_id,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "hours": 8.0,
        "notes": "Production API structure test",
        "bill_rate_override": 95.0
    }
    
    print(f"\n📝 Testing T&M tag creation:")
    response, error = make_request("POST", "/tm-tags", test_tm_tag)
    if error:
        print(f"❌ Connection error: {error}")
    else:
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            created = response.json()
            print(f"✅ Created T&M tag: {created.get('id')}")
            print(json.dumps(created, indent=2))
            
            # Test PDF functionality with real ID
            tm_id = created.get('id')
            if tm_id:
                print(f"\n📄 Testing PDF functionality with ID: {tm_id}")
                
                # Test PDF export
                response, error = make_request("GET", f"/tm-tags/{tm_id}/pdf")
                if response:
                    print(f"PDF export status: {response.status_code}")
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        print(f"✅ PDF export working - Content-Type: {content_type}")
                    else:
                        print(f"❌ PDF export failed: {response.text[:200]}")
                
                # Test PDF preview
                response, error = make_request("GET", f"/tm-tags/{tm_id}/preview")
                if response:
                    print(f"PDF preview status: {response.status_code}")
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        print(f"✅ PDF preview working - Content-Type: {content_type}")
                    else:
                        print(f"❌ PDF preview failed: {response.text[:200]}")
        else:
            print(f"❌ Response: {response.text}")

# =============================================================================
# TEST 3: TIMELOGS API STRUCTURE
# =============================================================================
print("\n🔍 TEST 3: TIMELOGS API STRUCTURE ANALYSIS")

response, error = make_request("GET", "/timelogs")
if response and response.status_code == 200:
    timelogs = response.json()
    if timelogs:
        print("✅ Existing timelog structure:")
        print(json.dumps(timelogs[0], indent=2))
    else:
        print("⚠️  No existing timelogs found")

# =============================================================================
# TEST 4: PROJECT ANALYTICS STRUCTURE
# =============================================================================
print("\n🔍 TEST 4: PROJECT ANALYTICS STRUCTURE")

if project_id:
    response, error = make_request("GET", f"/projects/{project_id}/analytics")
    if response:
        print(f"Project analytics status: {response.status_code}")
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Project analytics structure:")
            print(json.dumps(analytics, indent=2))
        else:
            print(f"❌ Analytics failed: {response.text[:200]}")

# =============================================================================
# TEST 5: CASHFLOW STRUCTURE
# =============================================================================
print("\n🔍 TEST 5: CASHFLOW STRUCTURE ANALYSIS")

response, error = make_request("GET", "/cashflows")
if response and response.status_code == 200:
    cashflows = response.json()
    print(f"✅ Cashflows endpoint working - {len(cashflows)} items")
    if cashflows:
        print("✅ Cashflow structure:")
        print(json.dumps(cashflows[0], indent=2))
    else:
        print("⚠️  No existing cashflows found")

print(f"\n📅 Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")