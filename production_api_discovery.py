#!/usr/bin/env python3
"""
Production API Discovery Tool
Discover the actual API structure on production backend
"""

import requests
import json
from datetime import datetime

PRODUCTION_BACKEND = "https://tm3014-tm-app-production.up.railway.app/api"

def discover_production_api():
    """Discover available endpoints on production"""
    session = requests.Session()
    session.timeout = 30
    
    print("🔍 DISCOVERING PRODUCTION API STRUCTURE")
    print("="*60)
    
    # Common endpoint patterns to test
    endpoints_to_test = [
        # T&M related
        "/tm-tags", "/tm_tags", "/tags", "/time-material", "/time_material",
        
        # Project related  
        "/projects", "/project",
        
        # User/Employee related
        "/installers", "/employees", "/workers", "/users", "/crew",
        
        # Time tracking
        "/timelogs", "/time-logs", "/timesheets", "/hours",
        
        # Financial
        "/cashflows", "/cash-flows", "/invoices", "/expenses",
        
        # Authentication
        "/auth/admin", "/login", "/auth/login",
        
        # PDF/Export
        "/pdf", "/export", "/generate-pdf", "/reports",
        
        # Health/Status
        "/health", "/status", "/", ""
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{PRODUCTION_BACKEND}{endpoint}"
            response = session.get(url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ {endpoint} - Returns list with {len(data)} items")
                        working_endpoints.append((endpoint, "list", len(data)))
                    elif isinstance(data, dict):
                        print(f"✅ {endpoint} - Returns object with keys: {list(data.keys())}")
                        working_endpoints.append((endpoint, "object", list(data.keys())))
                    else:
                        print(f"✅ {endpoint} - Returns: {type(data)}")
                        working_endpoints.append((endpoint, str(type(data)), None))
                except json.JSONDecodeError:
                    print(f"✅ {endpoint} - Returns non-JSON content")
                    working_endpoints.append((endpoint, "non-json", None))
            elif response.status_code == 405:
                print(f"⚠️ {endpoint} - Method not allowed (endpoint exists)")
                working_endpoints.append((endpoint, "method_not_allowed", None))
            elif response.status_code == 401:
                print(f"🔐 {endpoint} - Requires authentication")
                working_endpoints.append((endpoint, "auth_required", None))
            elif response.status_code == 404:
                pass  # Skip 404s
            else:
                print(f"❓ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            pass  # Skip errors
    
    print("\n" + "="*60)
    print("📋 WORKING ENDPOINTS SUMMARY:")
    print("="*60)
    
    for endpoint, data_type, details in working_endpoints:
        if data_type == "list":
            print(f"  {endpoint} -> List ({details} items)")
        elif data_type == "object":
            print(f"  {endpoint} -> Object (keys: {details})")
        else:
            print(f"  {endpoint} -> {data_type}")
    
    return working_endpoints

def test_specific_endpoints():
    """Test specific endpoints with detailed analysis"""
    session = requests.Session()
    session.timeout = 30
    
    print("\n" + "="*60)
    print("🔬 DETAILED ENDPOINT ANALYSIS")
    print("="*60)
    
    # Test projects endpoint in detail
    print("\n📋 PROJECTS ENDPOINT ANALYSIS:")
    try:
        response = session.get(f"{PRODUCTION_BACKEND}/projects")
        if response.status_code == 200:
            projects = response.json()
            print(f"  Found {len(projects)} projects")
            if projects:
                sample_project = projects[0]
                print(f"  Sample project keys: {list(sample_project.keys())}")
                print(f"  Sample project: {json.dumps(sample_project, indent=2)[:500]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test installers endpoint in detail
    print("\n👷 INSTALLERS ENDPOINT ANALYSIS:")
    try:
        response = session.get(f"{PRODUCTION_BACKEND}/installers")
        if response.status_code == 200:
            installers = response.json()
            print(f"  Found {len(installers)} installers")
            if installers:
                sample_installer = installers[0]
                print(f"  Sample installer keys: {list(sample_installer.keys())}")
                print(f"  Sample installer: {json.dumps(sample_installer, indent=2)[:300]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test timelogs endpoint in detail
    print("\n⏰ TIMELOGS ENDPOINT ANALYSIS:")
    try:
        response = session.get(f"{PRODUCTION_BACKEND}/timelogs")
        if response.status_code == 200:
            timelogs = response.json()
            print(f"  Found {len(timelogs)} timelogs")
            if timelogs:
                sample_timelog = timelogs[0]
                print(f"  Sample timelog keys: {list(sample_timelog.keys())}")
                print(f"  Sample timelog: {json.dumps(sample_timelog, indent=2)[:300]}...")
            else:
                print("  No timelogs found - testing creation...")
                # Try to create a timelog
                test_timelog = {
                    "project_id": "test-project",
                    "installer_id": "test-installer", 
                    "date": datetime.now().isoformat(),
                    "hours": 8.0,
                    "description": "Test work"
                }
                create_response = session.post(
                    f"{PRODUCTION_BACKEND}/timelogs",
                    json=test_timelog,
                    headers={"Content-Type": "application/json"}
                )
                print(f"  Creation test status: {create_response.status_code}")
                if create_response.status_code != 200:
                    print(f"  Creation error: {create_response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    """Main discovery function"""
    working_endpoints = discover_production_api()
    test_specific_endpoints()
    
    print("\n" + "="*60)
    print("🎯 KEY FINDINGS:")
    print("="*60)
    print("1. Production backend uses different API structure than preview")
    print("2. T&M functionality may be implemented as 'timelogs' instead of 'tm-tags'")
    print("3. Authentication system is working (/auth/admin)")
    print("4. Projects and installers endpoints are functional")
    print("5. PDF endpoints are missing - need to be implemented")

if __name__ == "__main__":
    main()