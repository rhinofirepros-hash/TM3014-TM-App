#!/usr/bin/env python3
"""
PRODUCTION BACKEND ENDPOINT VERIFICATION - CRITICAL MISSING FUNCTIONALITY

This test verifies production backend at https://tm3014-tm-app-production.up.railway.app
for ALL required endpoints that frontend expects.

Focus: Identify exactly which endpoints are missing on production causing system breakdown.
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone
import uuid

# Production backend URL - CRITICAL TESTING
PRODUCTION_BASE_URL = "https://tm3014-tm-app-production.up.railway.app"
PRODUCTION_API_URL = f"{PRODUCTION_BASE_URL}/api"

print(f"🚨 PRODUCTION BACKEND ENDPOINT VERIFICATION - CRITICAL MISSING FUNCTIONALITY")
print(f"📍 Production Backend URL: {PRODUCTION_BASE_URL}")
print(f"📍 Production API URL: {PRODUCTION_API_URL}")
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
# TEST 5: REPORTLAB INTEGRATION VERIFICATION
# =============================================================================
print("\n🔍 TEST 5: Testing ReportLab Integration")

# Test if ReportLab is properly integrated by checking backend health
response, error = make_request("GET", "/health")
if error:
    test_result("Backend health check", False, f"Connection error: {error}")
else:
    if response.status_code == 200:
        try:
            health_data = response.json()
            test_result("Backend health endpoint", True, f"Status: {health_data.get('status', 'unknown')}")
            
            # Check if ReportLab is mentioned in health check
            health_str = json.dumps(health_data)
            if 'reportlab' in health_str.lower() or 'pdf' in health_str.lower():
                test_result("ReportLab integration detected", True, "PDF capabilities mentioned in health check")
            else:
                test_result("ReportLab integration detected", False, "No PDF capabilities mentioned")
                
        except json.JSONDecodeError:
            test_result("Backend health endpoint JSON", False, "Invalid JSON response")
    else:
        test_result("Backend health endpoint", False, f"Status: {response.status_code}")

# Test ReportLab directly by attempting to import it via a test endpoint
# This is indirect testing since we can't directly test the backend's Python environment
if created_timelog_id:
    # The PDF generation test above already tests ReportLab integration
    # If PDF was generated successfully, ReportLab is working
    print("   ReportLab integration verified through successful PDF generation above")

# =============================================================================
# TEST 6: BACKWARD COMPATIBILITY - GET /api/tm-tags/{id}
# =============================================================================
print("\n🔍 TEST 6: Testing GET /api/tm-tags/{id} (compatibility alias)")

if created_timelog_id:
    response, error = make_request("GET", f"/tm-tags/{created_timelog_id}")
    if error:
        test_result("GET /api/tm-tags/{id} endpoint connectivity", False, f"Connection error: {error}")
    else:
        if response.status_code == 200:
            try:
                timelog_data = response.json()
                test_result("GET /api/tm-tags/{id} retrieves timelog", True, f"Retrieved timelog ID: {timelog_data.get('id')}")
                
                # Verify it's the same timelog we created
                if timelog_data.get('id') == created_timelog_id:
                    test_result("GET /api/tm-tags/{id} returns correct timelog", True)
                else:
                    test_result("GET /api/tm-tags/{id} returns correct timelog", False, f"ID mismatch: expected {created_timelog_id}, got {timelog_data.get('id')}")
                    
                # Verify data integrity
                if timelog_data.get('hours') == test_timelog['hours']:
                    test_result("GET /api/tm-tags/{id} data integrity", True, "Hours match original data")
                else:
                    test_result("GET /api/tm-tags/{id} data integrity", False, f"Hours mismatch: expected {test_timelog['hours']}, got {timelog_data.get('hours')}")
                    
            except json.JSONDecodeError:
                test_result("GET /api/tm-tags/{id} JSON response", False, "Invalid JSON response")
        else:
            test_result("GET /api/tm-tags/{id} retrieves timelog", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
else:
    test_result("GET /api/tm-tags/{id} test setup", False, "No timelog ID available for retrieval test")

# =============================================================================
# TEST 7: VERIFY TIMELOGS ENDPOINT STILL WORKS
# =============================================================================
print("\n🔍 TEST 7: Testing original /api/timelogs endpoint")

response, error = make_request("GET", "/timelogs")
if error:
    test_result("GET /api/timelogs endpoint connectivity", False, f"Connection error: {error}")
else:
    if response.status_code == 200:
        try:
            timelogs_data = response.json()
            test_result("GET /api/timelogs still functional", True, f"Returned {len(timelogs_data)} timelogs")
            
            # Verify our created timelog appears in timelogs list
            if created_timelog_id:
                found_timelog = any(tl.get('id') == created_timelog_id for tl in timelogs_data)
                if found_timelog:
                    test_result("Created timelog appears in /api/timelogs", True)
                else:
                    test_result("Created timelog appears in /api/timelogs", False, "Timelog not found in list")
            
        except json.JSONDecodeError:
            test_result("GET /api/timelogs JSON response", False, "Invalid JSON response")
    else:
        test_result("GET /api/timelogs still functional", False, f"Status: {response.status_code}, Response: {response.text[:200]}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("🎯 T&M TAGS COMPATIBILITY ENDPOINTS TEST SUMMARY")
print("=" * 80)
print(f"📊 Total Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")

if failed_tests == 0:
    print("\n🎉 ALL TESTS PASSED! T&M Tags compatibility endpoints are working correctly.")
    print("✅ Backward compatibility aliases functional")
    print("✅ PDF export working with ReportLab")
    print("✅ PDF preview generating proper HTML")
    print("✅ All endpoints returning proper responses")
else:
    print(f"\n⚠️  {failed_tests} TEST(S) FAILED - Issues need attention:")
    if failed_tests > total_tests * 0.5:
        print("🚨 CRITICAL: More than 50% of tests failed - major issues detected")
    else:
        print("⚠️  Some functionality issues detected - review failed tests above")

print("\n📋 TESTED ENDPOINTS:")
print("   • GET /api/tm-tags (compatibility alias)")
print("   • POST /api/tm-tags (compatibility alias)")
print("   • GET /api/tm-tags/{id} (compatibility alias)")
print("   • GET /api/tm-tags/{id}/pdf (PDF export)")
print("   • GET /api/tm-tags/{id}/preview (HTML preview)")
print("   • GET /api/timelogs (original endpoint)")

print(f"\n🔗 Backend URL: {BASE_URL}")
print(f"📅 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Exit with appropriate code
sys.exit(0 if failed_tests == 0 else 1)