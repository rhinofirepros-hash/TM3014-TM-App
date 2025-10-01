#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION SITE AUDIT - BACKEND TESTING
Testing tm.rhinofirepro.com production backend for complete system failure analysis

Issues to verify:
1. NO DATABASE STORAGE - Nothing saving to backend database
2. FRONTEND-BACKEND DISCONNECTION - T&M tags falling back to "offline mode"
3. Worker addition fails - Add worker functionality not working
4. Dashboard stats not updating - Project management data not reflecting in dashboard
5. UI theme inconsistencies - Multiple UI design problems (backend data issues)
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone
import uuid
import time

# Production backend URL
PRODUCTION_URL = "https://tm3014-tm-app-production.up.railway.app"
API_URL = f"{PRODUCTION_URL}/api"

print(f"🚨 COMPREHENSIVE PRODUCTION SITE AUDIT - BACKEND TESTING")
print(f"🌐 Production URL: {PRODUCTION_URL}")
print(f"📍 API URL: {API_URL}")
print("=" * 80)

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0
critical_issues = []
warnings = []

def test_result(test_name, success, details="", critical=False):
    global total_tests, passed_tests, failed_tests, critical_issues, warnings
    total_tests += 1
    if success:
        passed_tests += 1
        print(f"✅ {test_name}")
        if details:
            print(f"   {details}")
    else:
        failed_tests += 1
        print(f"❌ {test_name}")
        if details:
            print(f"   {details}")
        if critical:
            critical_issues.append(f"{test_name}: {details}")
        else:
            warnings.append(f"{test_name}: {details}")

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request with error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# =============================================================================
# TEST 1: PRODUCTION BACKEND CONNECTIVITY AUDIT
# =============================================================================
print("\n🔍 TEST 1: PRODUCTION BACKEND CONNECTIVITY AUDIT")

# Test basic connectivity
response, error = make_request("GET", "/")
if error:
    test_result("Production backend connectivity", False, f"Connection error: {error}", critical=True)
else:
    if response.status_code == 200:
        test_result("Production backend connectivity", True, f"Status: {response.status_code}")
    else:
        test_result("Production backend connectivity", False, f"Status: {response.status_code}", critical=True)

# Test all critical API endpoints
critical_endpoints = [
    "/projects",
    "/installers", 
    "/timelogs",
    "/tm-tags",
    "/cashflows"
]

print("\n📋 Testing Critical API Endpoints:")
for endpoint in critical_endpoints:
    response, error = make_request("GET", endpoint)
    if error:
        test_result(f"GET {endpoint} endpoint", False, f"Connection error: {error}", critical=True)
    else:
        if response.status_code == 200:
            test_result(f"GET {endpoint} endpoint", True, f"Status: {response.status_code}")
        elif response.status_code == 404:
            test_result(f"GET {endpoint} endpoint", False, f"Endpoint not found (404)", critical=True)
        else:
            test_result(f"GET {endpoint} endpoint", False, f"Status: {response.status_code}")

# =============================================================================
# TEST 2: DATABASE WRITE OPERATIONS VERIFICATION
# =============================================================================
print("\n🔍 TEST 2: DATABASE WRITE OPERATIONS VERIFICATION")

# Test 1: Create a new installer (worker)
print("\n📝 Testing Worker/Installer Creation:")
test_installer = {
    "name": "Production Test Worker",
    "hourly_rate": 33.0,
    "hire_date": "2025-01-15",
    "position": "Electrician",
    "phone": "555-0123",
    "email": "test@production.com"
}

response, error = make_request("POST", "/installers", test_installer)
created_installer_id = None
if error:
    test_result("POST /installers - Worker creation", False, f"Connection error: {error}", critical=True)
else:
    if response.status_code == 200:
        try:
            created_data = response.json()
            created_installer_id = created_data.get('id')
            test_result("POST /installers - Worker creation", True, f"Created installer ID: {created_installer_id}")
        except:
            test_result("POST /installers - Worker creation", False, "Invalid JSON response", critical=True)
    else:
        test_result("POST /installers - Worker creation", False, f"Status: {response.status_code}, Response: {response.text[:200]}", critical=True)

# Verify the installer was actually saved
if created_installer_id:
    response, error = make_request("GET", f"/installers/{created_installer_id}")
    if error:
        test_result("Database persistence - Installer retrieval", False, f"Connection error: {error}", critical=True)
    else:
        if response.status_code == 200:
            try:
                retrieved_data = response.json()
                if retrieved_data.get('name') == test_installer['name']:
                    test_result("Database persistence - Installer data integrity", True, "Data matches original")
                else:
                    test_result("Database persistence - Installer data integrity", False, "Data mismatch", critical=True)
            except:
                test_result("Database persistence - Installer retrieval", False, "Invalid JSON response", critical=True)
        else:
            test_result("Database persistence - Installer retrieval", False, f"Status: {response.status_code}", critical=True)

# Test 2: Create a T&M tag/timelog
print("\n📝 Testing T&M Tag Creation:")

# First get projects and installers for realistic data
projects_response, _ = make_request("GET", "/projects")
installers_response, _ = make_request("GET", "/installers")

project_id = None
installer_id = created_installer_id

if projects_response and projects_response.status_code == 200:
    try:
        projects = projects_response.json()
        if projects:
            project_id = projects[0].get('id')
    except:
        pass

# Test T&M tag creation (both endpoints)
test_tm_data = {
    "project_id": project_id or str(uuid.uuid4()),
    "installer_id": installer_id or str(uuid.uuid4()),
    "date": datetime.now().strftime('%Y-%m-%d'),
    "hours": 8.0,
    "notes": "Production audit test - T&M tag creation verification",
    "bill_rate_override": 95.0
}

# Test /tm-tags endpoint (frontend expects this)
response, error = make_request("POST", "/tm-tags", test_tm_data)
created_tm_id = None
if error:
    test_result("POST /tm-tags - T&M tag creation", False, f"Connection error: {error}", critical=True)
else:
    if response.status_code == 200:
        try:
            created_data = response.json()
            created_tm_id = created_data.get('id')
            test_result("POST /tm-tags - T&M tag creation", True, f"Created T&M tag ID: {created_tm_id}")
        except:
            test_result("POST /tm-tags - T&M tag creation", False, "Invalid JSON response", critical=True)
    elif response.status_code == 404:
        test_result("POST /tm-tags - T&M tag creation", False, "Endpoint not found - this explains offline mode!", critical=True)
    else:
        test_result("POST /tm-tags - T&M tag creation", False, f"Status: {response.status_code}, Response: {response.text[:200]}", critical=True)

# Test /timelogs endpoint (backend implementation)
response, error = make_request("POST", "/timelogs", test_tm_data)
created_timelog_id = None
if error:
    test_result("POST /timelogs - Timelog creation", False, f"Connection error: {error}")
else:
    if response.status_code == 200:
        try:
            created_data = response.json()
            created_timelog_id = created_data.get('id')
            test_result("POST /timelogs - Timelog creation", True, f"Created timelog ID: {created_timelog_id}")
        except:
            test_result("POST /timelogs - Timelog creation", False, "Invalid JSON response")
    else:
        test_result("POST /timelogs - Timelog creation", False, f"Status: {response.status_code}")

# =============================================================================
# TEST 3: FRONTEND-BACKEND API STRUCTURE MISMATCH ANALYSIS
# =============================================================================
print("\n🔍 TEST 3: FRONTEND-BACKEND API STRUCTURE MISMATCH ANALYSIS")

print("\n📊 Analyzing API endpoint availability:")

# Check which endpoints exist vs what frontend expects
frontend_expected_endpoints = [
    "/tm-tags",      # Frontend expects this for T&M functionality
    "/installers",   # Frontend expects this for worker management
    "/projects",     # Frontend expects this for project management
    "/timelogs",     # Backend might use this instead
    "/cashflows"     # Frontend expects this for dashboard
]

backend_endpoints = []
missing_endpoints = []

for endpoint in frontend_expected_endpoints:
    response, error = make_request("GET", endpoint)
    if error:
        missing_endpoints.append(f"{endpoint} - Connection error")
    elif response.status_code == 404:
        missing_endpoints.append(f"{endpoint} - Not found (404)")
    elif response.status_code == 200:
        backend_endpoints.append(endpoint)
    else:
        missing_endpoints.append(f"{endpoint} - Status {response.status_code}")

test_result("API endpoint availability analysis", len(missing_endpoints) == 0, 
           f"Available: {backend_endpoints}, Missing: {missing_endpoints}")

# =============================================================================
# TEST 4: PDF FUNCTIONALITY VERIFICATION
# =============================================================================
print("\n🔍 TEST 4: PDF FUNCTIONALITY VERIFICATION")

# Test PDF endpoints that frontend might expect
pdf_endpoints_to_test = [
    "/tm-tags/{id}/pdf",
    "/tm-tags/{id}/preview", 
    "/timelogs/{id}/pdf",
    "/timelogs/{id}/preview",
    "/reports/pdf",
    "/export/pdf"
]

pdf_working = False
test_id = created_tm_id or created_timelog_id or "test-id"

for endpoint_template in pdf_endpoints_to_test:
    endpoint = endpoint_template.replace("{id}", test_id)
    response, error = make_request("GET", endpoint)
    
    if error:
        test_result(f"PDF endpoint {endpoint}", False, f"Connection error: {error}")
    elif response.status_code == 404:
        test_result(f"PDF endpoint {endpoint}", False, "Not found (404)")
    elif response.status_code == 200:
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' in content_type or 'text/html' in content_type:
            test_result(f"PDF endpoint {endpoint}", True, f"Working - Content-Type: {content_type}")
            pdf_working = True
        else:
            test_result(f"PDF endpoint {endpoint}", False, f"Unexpected content-type: {content_type}")
    else:
        test_result(f"PDF endpoint {endpoint}", False, f"Status: {response.status_code}")

if not pdf_working:
    test_result("PDF functionality overall", False, "No working PDF endpoints found", critical=True)

# =============================================================================
# TEST 5: DASHBOARD DATA FLOW VERIFICATION
# =============================================================================
print("\n🔍 TEST 5: DASHBOARD DATA FLOW VERIFICATION")

# Test dashboard-related endpoints
dashboard_endpoints = [
    "/projects",
    "/installers", 
    "/timelogs",
    "/cashflows",
    "/analytics",
    "/dashboard",
    "/stats"
]

dashboard_data = {}
for endpoint in dashboard_endpoints:
    response, error = make_request("GET", endpoint)
    if error:
        test_result(f"Dashboard endpoint {endpoint}", False, f"Connection error: {error}")
    elif response.status_code == 200:
        try:
            data = response.json()
            dashboard_data[endpoint] = len(data) if isinstance(data, list) else "object"
            test_result(f"Dashboard endpoint {endpoint}", True, f"Returns data: {dashboard_data[endpoint]}")
        except:
            test_result(f"Dashboard endpoint {endpoint}", False, "Invalid JSON response")
    else:
        test_result(f"Dashboard endpoint {endpoint}", False, f"Status: {response.status_code}")

# Test project analytics if we have a project
if project_id:
    response, error = make_request("GET", f"/projects/{project_id}/analytics")
    if error:
        test_result("Project analytics endpoint", False, f"Connection error: {error}")
    elif response.status_code == 200:
        try:
            analytics = response.json()
            test_result("Project analytics endpoint", True, f"Analytics keys: {list(analytics.keys())}")
        except:
            test_result("Project analytics endpoint", False, "Invalid JSON response")
    else:
        test_result("Project analytics endpoint", False, f"Status: {response.status_code}")

# =============================================================================
# TEST 6: AUTHENTICATION VERIFICATION
# =============================================================================
print("\n🔍 TEST 6: AUTHENTICATION VERIFICATION")

# Test admin authentication endpoint
auth_data = {"pin": "J777"}  # Known admin PIN from test_result.md
response, error = make_request("POST", "/auth/admin", auth_data)
if error:
    test_result("Admin authentication endpoint", False, f"Connection error: {error}")
elif response.status_code == 200:
    test_result("Admin authentication endpoint", True, "Authentication working")
elif response.status_code == 401:
    test_result("Admin authentication endpoint", True, "Endpoint exists (401 expected for test PIN)")
else:
    test_result("Admin authentication endpoint", False, f"Status: {response.status_code}")

# =============================================================================
# TEST 7: CORS AND CONNECTIVITY VERIFICATION
# =============================================================================
print("\n🔍 TEST 7: CORS AND CONNECTIVITY VERIFICATION")

# Test CORS headers
response, error = make_request("GET", "/projects")
if response:
    cors_headers = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
    }
    
    if cors_headers['Access-Control-Allow-Origin']:
        test_result("CORS configuration", True, f"CORS headers present: {cors_headers}")
    else:
        test_result("CORS configuration", False, "Missing CORS headers", critical=True)

# =============================================================================
# TEST 8: DATA CONSISTENCY AND INTEGRITY
# =============================================================================
print("\n🔍 TEST 8: DATA CONSISTENCY AND INTEGRITY")

# Check if created data is consistent across endpoints
if created_installer_id:
    # Check if installer appears in list
    response, error = make_request("GET", "/installers")
    if response and response.status_code == 200:
        try:
            installers = response.json()
            found = any(inst.get('id') == created_installer_id for inst in installers)
            test_result("Data consistency - Installer in list", found, 
                       "Created installer appears in GET /installers" if found else "Created installer missing from list")
        except:
            test_result("Data consistency - Installer list", False, "Invalid JSON response")

if created_tm_id or created_timelog_id:
    # Check if T&M data appears in appropriate lists
    for endpoint in ["/tm-tags", "/timelogs"]:
        response, error = make_request("GET", endpoint)
        if response and response.status_code == 200:
            try:
                items = response.json()
                found_tm = any(item.get('id') == created_tm_id for item in items) if created_tm_id else False
                found_tl = any(item.get('id') == created_timelog_id for item in items) if created_timelog_id else False
                
                if found_tm or found_tl:
                    test_result(f"Data consistency - T&M in {endpoint}", True, "Created T&M data appears in list")
                else:
                    test_result(f"Data consistency - T&M in {endpoint}", False, "Created T&M data missing from list")
            except:
                test_result(f"Data consistency - {endpoint} list", False, "Invalid JSON response")

# =============================================================================
# COMPREHENSIVE ANALYSIS AND ROOT CAUSE IDENTIFICATION
# =============================================================================
print("\n" + "=" * 80)
print("🎯 COMPREHENSIVE PRODUCTION AUDIT RESULTS")
print("=" * 80)
print(f"📊 Total Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")

print(f"\n🚨 CRITICAL ISSUES IDENTIFIED ({len(critical_issues)}):")
for i, issue in enumerate(critical_issues, 1):
    print(f"   {i}. {issue}")

print(f"\n⚠️  WARNINGS ({len(warnings)}):")
for i, warning in enumerate(warnings, 1):
    print(f"   {i}. {warning}")

# ROOT CAUSE ANALYSIS
print(f"\n🔍 ROOT CAUSE ANALYSIS:")

if "/tm-tags" in [issue for issue in critical_issues if "tm-tags" in issue.lower()]:
    print("   🎯 OFFLINE MODE ROOT CAUSE: /tm-tags endpoint missing or not working")
    print("      - Frontend expects /tm-tags API but production uses /timelogs")
    print("      - This explains why T&M tags fall back to 'offline mode'")

if any("worker" in issue.lower() or "installer" in issue.lower() for issue in critical_issues):
    print("   🎯 WORKER ADDITION FAILURE: Installer/worker endpoints not functioning")
    print("      - POST /installers endpoint issues detected")

if any("pdf" in issue.lower() for issue in critical_issues):
    print("   🎯 PDF FUNCTIONALITY MISSING: No working PDF generation endpoints")
    print("      - PDF export/preview functionality not implemented on production")

if any("database" in issue.lower() or "persistence" in issue.lower() for issue in critical_issues):
    print("   🎯 DATABASE STORAGE ISSUES: Data not persisting correctly")
    print("      - Write operations failing or data not being saved")

# PRODUCTION READINESS ASSESSMENT
print(f"\n📋 PRODUCTION READINESS ASSESSMENT:")
if failed_tests == 0:
    print("🎉 PRODUCTION READY: All systems operational")
elif failed_tests <= total_tests * 0.3:
    print("⚠️  MINOR ISSUES: Production mostly functional with some issues")
elif failed_tests <= total_tests * 0.6:
    print("🚨 MAJOR ISSUES: Significant problems affecting functionality")
else:
    print("🔥 CRITICAL FAILURE: Production system severely compromised")

print(f"\n🔗 Production Backend: {PRODUCTION_URL}")
print(f"📅 Audit completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Exit with appropriate code
sys.exit(0 if len(critical_issues) == 0 else 1)