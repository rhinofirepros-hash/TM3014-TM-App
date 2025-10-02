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

def test_result(test_name, success, details=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if success:
        passed_tests += 1
        print(f"✅ {test_name}")
    else:
        failed_tests += 1
        print(f"❌ {test_name}")
    if details:
        print(f"   {details}")

def test_tm_tag_creation_exact_form_data():
    """Test POST /api/tm-tags with exact T&M tag data structure from form"""
    print("\n🎯 TESTING T&M TAG CREATION - EXACT FORM FAILURE ANALYSIS")
    print("=" * 70)
    
    # Exact T&M tag data structure as provided in the review request
    tm_tag_data = {
        "id": "tm_1727901234567",
        "project_id": "test_project_id", 
        "project_name": "Test Project",
        "cost_code": "001",
        "date_of_work": "2025-10-02T17:30:00.000Z",
        "company_name": "Rhino Fire Pro", 
        "tm_tag_title": "Test T&M Tag",
        "description_of_work": "Test work description",
        "labor_entries": [
            {
                "id": 1727901234567,
                "workerName": "Test Worker",
                "quantity": 1,
                "st_hours": 8,
                "ot_hours": 0,
                "dt_hours": 0,
                "pot_hours": 0,
                "total": 8,
                "dateOfWork": "10/2/2025"
            }
        ],
        "material_entries": [],
        "equipment_entries": [], 
        "other_entries": [],
        "gc_email": "",
        "signature": "",
        "foreman_name": "Test Foreman",
        "status": "completed",
        "created_at": "2025-10-02T17:30:00.000Z",
        "total_cost": 800
    }
    
    print(f"📡 Testing POST {API_BASE}/tm-tags")
    print(f"📋 Data Structure: T&M tag with 1 labor entry (8 hours)")
    
    try:
        # Test the exact POST request that the frontend makes
        response = requests.post(
            f"{API_BASE}/tm-tags",
            json=tm_tag_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            test_result("T&M Tag Creation", True, "Successfully created T&M tag")
            try:
                response_data = response.json()
                print(f"📄 Response Data: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"📄 Response Text: {response.text}")
            return True
        else:
            test_result("T&M Tag Creation", False, f"Status {response.status_code} - This explains 'offline mode' fallback!")
            
            try:
                error_data = response.json()
                print(f"📄 Error Response: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"📄 Error Text: {response.text}")
            
            return False
            
    except requests.exceptions.ConnectionError as e:
        test_result("T&M Tag Creation", False, f"CONNECTION ERROR: Cannot reach backend - {e}")
        print("🔍 This explains the 'offline mode' fallback!")
        return False
    except requests.exceptions.Timeout as e:
        test_result("T&M Tag Creation", False, f"TIMEOUT ERROR: Backend not responding - {e}")
        return False
    except Exception as e:
        test_result("T&M Tag Creation", False, f"UNEXPECTED ERROR: {e}")
        return False

def test_backend_connectivity():
    """Test basic backend connectivity"""
    print("\n🌐 TESTING BACKEND CONNECTIVITY")
    print("=" * 50)
    
    endpoints_to_test = [
        "/api/health",
        "/api/projects", 
        "/api/tm-tags",
        "/api/workers"
    ]
    
    connectivity_results = {}
    
    for endpoint in endpoints_to_test:
        url = f"{BACKEND_URL}{endpoint}"
        print(f"📡 Testing GET {url}")
        
        try:
            response = requests.get(url, timeout=10)
            connectivity_results[endpoint] = {
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "response_time": response.elapsed.total_seconds()
            }
            
            if response.status_code < 400:
                test_result(f"GET {endpoint}", True, f"{response.status_code} ({response.elapsed.total_seconds():.2f}s)")
            else:
                test_result(f"GET {endpoint}", False, f"{response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                
        except requests.exceptions.ConnectionError:
            test_result(f"GET {endpoint}", False, "CONNECTION ERROR")
            connectivity_results[endpoint] = {"success": False, "error": "connection_error"}
        except requests.exceptions.Timeout:
            test_result(f"GET {endpoint}", False, "TIMEOUT")
            connectivity_results[endpoint] = {"success": False, "error": "timeout"}
        except Exception as e:
            test_result(f"GET {endpoint}", False, f"ERROR - {e}")
            connectivity_results[endpoint] = {"success": False, "error": str(e)}
    
    return connectivity_results

def test_working_endpoints_comparison():
    """Test other endpoints to see if they work vs tm-tags"""
    print("\n🔄 COMPARING WITH WORKING ENDPOINTS")
    print("=" * 50)
    
    # Test GET endpoints first
    get_endpoints = [
        "/api/projects",
        "/api/tm-tags", 
        "/api/workers",
        "/api/employees"
    ]
    
    working_gets = []
    failing_gets = []
    
    for endpoint in get_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            if response.status_code < 400:
                working_gets.append(endpoint)
                test_result(f"GET {endpoint}", True, f"{response.status_code}")
            else:
                failing_gets.append(endpoint)
                test_result(f"GET {endpoint}", False, f"{response.status_code}")
        except Exception as e:
            failing_gets.append(endpoint)
            test_result(f"GET {endpoint}", False, f"ERROR - {e}")
    
    print(f"\n📊 Working GET endpoints: {len(working_gets)}")
    print(f"📊 Failing GET endpoints: {len(failing_gets)}")
    
    # Now test POST endpoints with minimal data
    post_tests = [
        {
            "endpoint": "/api/projects",
            "data": {
                "name": "Test Project",
                "client_company": "Test Company",
                "gc_email": "test@test.com",
                "start_date": "2025-01-01T00:00:00.000Z"
            }
        },
        {
            "endpoint": "/api/workers",
            "data": {
                "name": "Test Worker",
                "rate": 95.0
            }
        }
    ]
    
    print(f"\n🧪 Testing POST endpoints for comparison:")
    
    for test in post_tests:
        try:
            response = requests.post(
                f"{BACKEND_URL}{test['endpoint']}",
                json=test["data"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            test_result(f"POST {test['endpoint']}", response.status_code < 400, f"{response.status_code}")
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
        except Exception as e:
            test_result(f"POST {test['endpoint']}", False, f"ERROR - {e}")

def main():
    """Main test execution"""
    print("🚨 T&M TAG CREATION ENDPOINT - EXACT FORM FAILURE ANALYSIS")
    print("🎯 CRITICAL ISSUE: 'SAVED OFFLINE' MESSAGE IN T&M FORM")
    print("=" * 80)
    
    # Test 1: Exact T&M tag creation that's failing
    tm_creation_success = test_tm_tag_creation_exact_form_data()
    
    # Test 2: Backend connectivity
    connectivity_results = test_backend_connectivity()
    
    # Test 3: Compare with working endpoints
    test_working_endpoints_comparison()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 ANALYSIS SUMMARY")
    print("=" * 80)
    
    if tm_creation_success:
        test_result("OVERALL T&M Tag Creation", True, "Issue may be frontend-related")
    else:
        test_result("OVERALL T&M Tag Creation", False, "This explains 'offline mode'")
    
    working_endpoints = sum(1 for result in connectivity_results.values() if result.get("success", False))
    total_endpoints = len(connectivity_results)
    
    print(f"📊 Backend Connectivity: {working_endpoints}/{total_endpoints} endpoints working")
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}%)")
    
    if working_endpoints == 0:
        print("🔍 ROOT CAUSE: Complete backend connectivity failure")
    elif not tm_creation_success and working_endpoints > 0:
        print("🔍 ROOT CAUSE: Specific issue with T&M tag creation endpoint")
    elif tm_creation_success:
        print("🔍 ROOT CAUSE: Issue likely in frontend T&M form or data format")
    
    print("\n🎯 NEXT STEPS:")
    if not tm_creation_success:
        print("1. Fix T&M tag creation endpoint issues identified above")
        print("2. Verify data model compatibility between frontend and backend")
        print("3. Check for missing required fields or validation errors")
    else:
        print("1. Check frontend T&M form data formatting")
        print("2. Verify frontend is using correct backend URL")
        print("3. Check for JavaScript errors in browser console")

if __name__ == "__main__":
    main()

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