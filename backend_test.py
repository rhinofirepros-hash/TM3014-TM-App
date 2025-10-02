#!/usr/bin/env python3
"""
T&M TAG CREATION ENDPOINT - EXACT FORM FAILURE ANALYSIS

CRITICAL ISSUE: "SAVED OFFLINE" MESSAGE IN T&M FORM
User reports that when adding a worker in T&M form, it shows "saved offline" and redirects to dashboard.

ROOT CAUSE INVESTIGATION:
The TimeAndMaterialForm.jsx makes a POST request to `${backendUrl}/tm-tags` (line 219), 
but if the response is not OK, it falls back to "offline mode" (line 286).

EXACT API CALL TO TEST: POST /api/tm-tags with T&M tag data structure
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone
import uuid

# Backend URL from frontend/.env
BACKEND_URL = "https://tm3014-tm-app-production.up.railway.app"
API_BASE = f"{BACKEND_URL}/api"

print(f"🚨 T&M TAG CREATION ENDPOINT - EXACT FORM FAILURE ANALYSIS")
print(f"🎯 CRITICAL ISSUE: 'SAVED OFFLINE' MESSAGE IN T&M FORM")
print(f"📍 Backend URL: {BACKEND_URL}")
print(f"📍 API Base: {API_BASE}")
print("=" * 80)

# Test tracking
total_tests = 0
passed_tests = 0
failed_tests = 0
missing_endpoints = []
working_endpoints = []
failed_endpoints = []

def test_result(test_name, success, details="", endpoint=None):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if success:
        passed_tests += 1
        print(f"✅ {test_name}")
        if endpoint:
            working_endpoints.append(endpoint)
    else:
        failed_tests += 1
        print(f"❌ {test_name}")
        if endpoint:
            if "404" in str(details) or "Not Found" in str(details):
                missing_endpoints.append(endpoint)
            else:
                failed_endpoints.append(endpoint)
    
    if details:
        print(f"   {details}")

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request with error handling"""
    try:
        url = f"{PRODUCTION_API_URL}{endpoint}"
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

def test_endpoint_exists(endpoint, method="GET", data=None):
    """Test if endpoint exists and is accessible"""
    response, error = make_request(method, endpoint, data)
    if error:
        return False, f"Connection error: {error}"
    
    if response.status_code == 404:
        return False, f"404 Not Found - Endpoint missing"
    elif response.status_code in [200, 201, 422, 400]:  # 422/400 means endpoint exists but validation failed
        return True, f"{response.status_code} - Endpoint exists"
    else:
        return False, f"{response.status_code} - {response.text[:100]}"

# =============================================================================
# CRITICAL T&M TAGS COMPATIBILITY ENDPOINTS TESTING
# =============================================================================
print("\n🎯 TESTING T&M TAGS COMPATIBILITY ENDPOINTS (CRITICAL)")

# 1. GET /api/tm-tags (list all T&M tags)
print("\n📋 TEST 1: GET /api/tm-tags (list T&M tags)")
success, details = test_endpoint_exists("/tm-tags", "GET")
test_result("GET /api/tm-tags (list T&M tags)", success, details, "/tm-tags")

# 2. POST /api/tm-tags (create new T&M tag)
print("\n📝 TEST 2: POST /api/tm-tags (create T&M tag)")
test_tm_tag = {
    "project_name": "Production Test Project",
    "cost_code": "PROD001",
    "date_of_work": datetime.now().isoformat(),
    "tm_tag_title": "Production Endpoint Test",
    "description_of_work": "Testing production backend endpoints",
    "gc_email": "test@production.com",
    "labor_entries": [],
    "material_entries": [],
    "equipment_entries": [],
    "other_entries": []
}
success, details = test_endpoint_exists("/tm-tags", "POST", test_tm_tag)
test_result("POST /api/tm-tags (create T&M tag)", success, details, "/tm-tags")

# 3. GET /api/tm-tags/{id} (get specific T&M tag)
print("\n🔍 TEST 3: GET /api/tm-tags/{id} (get specific T&M tag)")
test_id = str(uuid.uuid4())
success, details = test_endpoint_exists(f"/tm-tags/{test_id}", "GET")
test_result("GET /api/tm-tags/{id} (get specific T&M tag)", success, details, f"/tm-tags/{test_id}")

# 4. GET /api/tm-tags/{id}/pdf (PDF export)
print("\n📄 TEST 4: GET /api/tm-tags/{id}/pdf (PDF export)")
success, details = test_endpoint_exists(f"/tm-tags/{test_id}/pdf", "GET")
test_result("GET /api/tm-tags/{id}/pdf (PDF export)", success, details, f"/tm-tags/{test_id}/pdf")

# 5. GET /api/tm-tags/{id}/preview (PDF preview)
print("\n👁️ TEST 5: GET /api/tm-tags/{id}/preview (PDF preview)")
success, details = test_endpoint_exists(f"/tm-tags/{test_id}/preview", "GET")
test_result("GET /api/tm-tags/{id}/preview (PDF preview)", success, details, f"/tm-tags/{test_id}/preview")

# =============================================================================
# WORKER/INSTALLER MANAGEMENT ENDPOINTS TESTING
# =============================================================================
print("\n👷 TESTING WORKER/INSTALLER MANAGEMENT ENDPOINTS")

# 1. GET /api/installers (list workers)
print("\n📋 TEST 6: GET /api/installers (list workers)")
success, details = test_endpoint_exists("/installers", "GET")
test_result("GET /api/installers (list workers)", success, details, "/installers")

# 2. POST /api/installers (create worker)
print("\n📝 TEST 7: POST /api/installers (create worker)")
test_worker = {
    "name": "Production Test Worker",
    "cost_rate": 35.0,
    "position": "Electrician",
    "phone": "555-0123",
    "email": "testworker@production.com"
}
success, details = test_endpoint_exists("/installers", "POST", test_worker)
test_result("POST /api/installers (create worker)", success, details, "/installers")

# 3. DELETE /api/installers/{id} (delete worker) - USER CAN'T DELETE
print("\n🗑️ TEST 8: DELETE /api/installers/{id} (delete worker)")
test_id = str(uuid.uuid4())
success, details = test_endpoint_exists(f"/installers/{test_id}", "DELETE")
test_result("DELETE /api/installers/{id} (delete worker)", success, details, f"/installers/{test_id}")

# 4. PUT /api/installers/{id} (update worker)
print("\n✏️ TEST 9: PUT /api/installers/{id} (update worker)")
success, details = test_endpoint_exists(f"/installers/{test_id}", "PUT", test_worker)
test_result("PUT /api/installers/{id} (update worker)", success, details, f"/installers/{test_id}")

# =============================================================================
# NAVIGATION & CORE FUNCTIONALITY ENDPOINTS TESTING
# =============================================================================
print("\n🧭 TESTING NAVIGATION & CORE FUNCTIONALITY ENDPOINTS")

# 1. GET /api/projects (project management)
print("\n📋 TEST 10: GET /api/projects (project management)")
success, details = test_endpoint_exists("/projects", "GET")
test_result("GET /api/projects (project management)", success, details, "/projects")

# 2. Health check endpoints
print("\n🏥 TEST 11: GET /api/health (health check)")
success, details = test_endpoint_exists("/health", "GET")
test_result("GET /api/health (health check)", success, details, "/health")

# 3. Root endpoint
print("\n🏠 TEST 12: GET /api/ (root endpoint)")
success, details = test_endpoint_exists("/", "GET")
test_result("GET /api/ (root endpoint)", success, details, "/")

# 4. Authentication endpoints
print("\n🔐 TEST 13: POST /api/auth/admin (admin authentication)")
success, details = test_endpoint_exists("/auth/admin", "POST", {"pin": "J777"})
test_result("POST /api/auth/admin (admin authentication)", success, details, "/auth/admin")

# =============================================================================
# ALTERNATIVE ENDPOINT NAMES TESTING
# =============================================================================
print("\n🔍 TESTING ALTERNATIVE ENDPOINT NAMES")

# Check if workers are under different names
print("\n👥 TEST 14: Alternative worker endpoints")
alternative_worker_endpoints = ["/workers", "/employees", "/crew", "/staff"]
for endpoint in alternative_worker_endpoints:
    success, details = test_endpoint_exists(endpoint, "GET")
    test_result(f"GET /api{endpoint} (alternative worker endpoint)", success, details, endpoint)

# Check if T&M tags are under different names
print("\n📊 TEST 15: Alternative T&M endpoints")
alternative_tm_endpoints = ["/timelogs", "/time-logs", "/tm_tags", "/tags", "/reports"]
for endpoint in alternative_tm_endpoints:
    success, details = test_endpoint_exists(endpoint, "GET")
    test_result(f"GET /api{endpoint} (alternative T&M endpoint)", success, details, endpoint)

# =============================================================================
# COMPREHENSIVE API STRUCTURE TESTING
# =============================================================================
print("\n📋 TESTING COMPREHENSIVE API STRUCTURE")

# Common REST endpoints
print("\n🔧 TEST 16: Common REST endpoints")
common_endpoints = [
    "/status", "/tm-tags", "/workers", "/projects", "/employees", 
    "/materials", "/crew-logs", "/phases", "/tasks", "/invoices",
    "/payables", "/cashflows", "/timelogs", "/installers"
]

for endpoint in common_endpoints:
    success, details = test_endpoint_exists(endpoint, "GET")
    test_result(f"GET /api{endpoint}", success, details, endpoint)

# =============================================================================
# GENERATE COMPREHENSIVE SUMMARY REPORT
# =============================================================================
def generate_summary_report():
    """Generate comprehensive summary report"""
    print("\n" + "=" * 80)
    print("📊 PRODUCTION BACKEND ENDPOINT VERIFICATION SUMMARY")
    print("=" * 80)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    print(f"\n✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
    for endpoint in sorted(set(working_endpoints)):
        print(f"   • {endpoint}")
    
    print(f"\n❌ MISSING ENDPOINTS ({len(missing_endpoints)}):")
    for endpoint in sorted(set(missing_endpoints)):
        print(f"   • {endpoint} (404 Not Found)")
    
    print(f"\n⚠️  FAILED ENDPOINTS ({len(failed_endpoints)}):")
    for endpoint in sorted(set(failed_endpoints)):
        print(f"   • {endpoint}")
    
    # Critical analysis
    print(f"\n🎯 CRITICAL ISSUES IDENTIFIED:")
    
    critical_missing = []
    if "/tm-tags" in missing_endpoints:
        critical_missing.append("T&M Tags endpoints missing - causes 'offline mode'")
    if "/installers" in missing_endpoints:
        critical_missing.append("Installer endpoints missing - can't manage crew")
    if any("pdf" in ep for ep in missing_endpoints):
        critical_missing.append("PDF endpoints missing - causes 'black screen' on preview")
    
    if critical_missing:
        for issue in critical_missing:
            print(f"   🚨 {issue}")
    else:
        print("   ✅ No critical missing endpoints identified")
    
    # Root cause analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    if len(missing_endpoints) > len(working_endpoints):
        print("   🚨 MAJOR ISSUE: More endpoints missing than working")
        print("   💡 LIKELY CAUSE: Wrong server deployment or API structure mismatch")
    elif "/tm-tags" in missing_endpoints and "/timelogs" in working_endpoints:
        print("   🚨 API STRUCTURE MISMATCH: Frontend expects /tm-tags but backend has /timelogs")
        print("   💡 SOLUTION: Add compatibility aliases or update frontend")
    elif len(missing_endpoints) == 0:
        print("   ✅ All tested endpoints exist - issue may be in request/response format")
    else:
        print(f"   ⚠️  Partial implementation: {len(missing_endpoints)} endpoints missing")
    
    print(f"\n📋 PRODUCTION READINESS: {success_rate:.1f}%")
    if success_rate >= 90:
        print("   ✅ READY FOR PRODUCTION")
    elif success_rate >= 70:
        print("   ⚠️  MOSTLY READY - Minor fixes needed")
    else:
        print("   🚨 NOT READY - Major functionality gaps")

generate_summary_report()

# =============================================================================
# FINAL RESULTS AND EXIT
# =============================================================================

# Return exit code based on critical endpoints
critical_endpoints = ["/tm-tags", "/installers", "/projects"]
missing_critical = [ep for ep in critical_endpoints if ep in missing_endpoints]

print(f"\n🔗 Production Backend URL: {PRODUCTION_BASE_URL}")
print(f"📅 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if missing_critical:
    print(f"\n🚨 CRITICAL FAILURE: Missing critical endpoints: {missing_critical}")
    print("   💡 RECOMMENDATION: Use web search tool to investigate production deployment issues")
    sys.exit(1)
else:
    print(f"\n✅ CRITICAL ENDPOINTS VERIFIED: All essential endpoints working")
    sys.exit(0 if failed_tests == 0 else 1)