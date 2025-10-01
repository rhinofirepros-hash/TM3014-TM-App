#!/usr/bin/env python3
"""
DELETE INSTALLER ENDPOINT TESTING - CRITICAL FIX VERIFICATION

This test verifies the newly added DELETE /api/installers/{id} endpoint
to fix the user's "Cannot delete crew members" issue.

Testing against production backend: https://tm3014-tm-app-production.up.railway.app
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone
import uuid
import time

# Production backend URL from review request
BACKEND_URL = "https://tm3014-tm-app-production.up.railway.app"
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 DELETE INSTALLER ENDPOINT TESTING - CRITICAL FIX VERIFICATION")
print(f"📍 Backend URL: {BACKEND_URL}")
print(f"📍 API URL: {API_URL}")
print("=" * 80)

# Test tracking
total_tests = 0
passed_tests = 0
failed_tests = 0
test_results = []

def test_result(test_name, success, details="", critical=False):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    status = "✅ PASS" if success else "❌ FAIL"
    priority = "🚨 CRITICAL" if critical else "📋 STANDARD"
    
    if success:
        passed_tests += 1
    else:
        failed_tests += 1
    
    result = {
        "test": test_name,
        "success": success,
        "details": details,
        "critical": critical,
        "status": status,
        "priority": priority
    }
    test_results.append(result)
    
    print(f"{status} {priority} {test_name}")
    if details:
        print(f"   📝 {details}")

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
# TEST 1: VERIFY DELETE ENDPOINT EXISTS AND RETURNS 200 (NOT 405)
# =============================================================================
print("\n🔍 TEST 1: DELETE ENDPOINT EXISTENCE AND METHOD SUPPORT")

# First, let's get existing installers to find a valid ID
print("\n📋 Getting existing installers...")
response, error = make_request("GET", "/installers")
if error:
    test_result("GET /api/installers (prerequisite)", False, f"Connection error: {error}", critical=True)
    sys.exit(1)

if response.status_code != 200:
    test_result("GET /api/installers (prerequisite)", False, f"Status: {response.status_code}", critical=True)
    sys.exit(1)

try:
    installers = response.json()
    test_result("GET /api/installers (prerequisite)", True, f"Found {len(installers)} installers")
except:
    test_result("GET /api/installers (prerequisite)", False, "Invalid JSON response", critical=True)
    sys.exit(1)

# =============================================================================
# TEST 2: CREATE TEST INSTALLER FOR DELETION
# =============================================================================
print("\n📝 TEST 2: CREATE TEST INSTALLER FOR DELETION")

test_installer = {
    "name": "DELETE TEST INSTALLER",
    "cost_rate": 45.0,
    "position": "Test Electrician",
    "phone": "555-DELETE",
    "email": "delete.test@example.com",
    "hire_date": datetime.now().date().isoformat()
}

response, error = make_request("POST", "/installers", test_installer)
if error:
    test_result("POST /api/installers (create test installer)", False, f"Connection error: {error}", critical=True)
    sys.exit(1)

if response.status_code in [200, 201]:
    try:
        created_installer = response.json()
        test_installer_id = created_installer.get("id")
        test_result("POST /api/installers (create test installer)", True, f"Created installer ID: {test_installer_id}")
    except:
        test_result("POST /api/installers (create test installer)", False, "Invalid JSON response", critical=True)
        sys.exit(1)
else:
    test_result("POST /api/installers (create test installer)", False, f"Status: {response.status_code} - {response.text[:200]}", critical=True)
    sys.exit(1)

# =============================================================================
# TEST 3: TEST DELETE ENDPOINT - CRITICAL TEST
# =============================================================================
print("\n🗑️ TEST 3: DELETE INSTALLER ENDPOINT - CRITICAL TEST")

response, error = make_request("DELETE", f"/installers/{test_installer_id}")
if error:
    test_result("DELETE /api/installers/{id} (method support)", False, f"Connection error: {error}", critical=True)
else:
    if response.status_code == 405:
        test_result("DELETE /api/installers/{id} (method support)", False, "405 Method Not Allowed - DELETE endpoint missing!", critical=True)
    elif response.status_code == 200:
        test_result("DELETE /api/installers/{id} (method support)", True, "200 OK - DELETE endpoint working correctly", critical=False)
        
        # Verify response content
        try:
            delete_response = response.json()
            if "message" in delete_response and "installer_id" in delete_response:
                test_result("DELETE response format", True, f"Proper response format: {delete_response}")
            else:
                test_result("DELETE response format", False, f"Unexpected response format: {delete_response}")
        except:
            test_result("DELETE response format", False, "Invalid JSON response")
            
    elif response.status_code == 404:
        test_result("DELETE /api/installers/{id} (method support)", False, "404 Not Found - Installer not found", critical=True)
    elif response.status_code == 400:
        # This might be the business logic protection
        try:
            error_response = response.json()
            if "time logs" in error_response.get("detail", "").lower():
                test_result("DELETE /api/installers/{id} (business logic protection)", True, f"Protected deletion: {error_response.get('detail')}")
            else:
                test_result("DELETE /api/installers/{id} (method support)", False, f"400 Bad Request: {error_response.get('detail', 'Unknown error')}")
        except:
            test_result("DELETE /api/installers/{id} (method support)", False, f"400 Bad Request: {response.text[:200]}")
    else:
        test_result("DELETE /api/installers/{id} (method support)", False, f"Status: {response.status_code} - {response.text[:200]}", critical=True)

# =============================================================================
# TEST 4: VERIFY INSTALLER IS ACTUALLY REMOVED FROM DATABASE
# =============================================================================
print("\n🔍 TEST 4: VERIFY INSTALLER REMOVAL FROM DATABASE")

# Try to get the deleted installer
response, error = make_request("GET", f"/installers/{test_installer_id}")
if error:
    test_result("Verify installer deletion (database removal)", False, f"Connection error: {error}")
else:
    if response.status_code == 404:
        test_result("Verify installer deletion (database removal)", True, "404 Not Found - Installer successfully removed from database")
    elif response.status_code == 200:
        test_result("Verify installer deletion (database removal)", False, "200 OK - Installer still exists in database!", critical=True)
    else:
        test_result("Verify installer deletion (database removal)", False, f"Unexpected status: {response.status_code}")

# =============================================================================
# TEST 5: TEST ERROR HANDLING - 404 FOR NON-EXISTENT INSTALLER
# =============================================================================
print("\n❌ TEST 5: ERROR HANDLING - NON-EXISTENT INSTALLER")

fake_installer_id = str(uuid.uuid4())
response, error = make_request("DELETE", f"/installers/{fake_installer_id}")
if error:
    test_result("DELETE non-existent installer (404 handling)", False, f"Connection error: {error}")
else:
    if response.status_code == 404:
        test_result("DELETE non-existent installer (404 handling)", True, "404 Not Found - Proper error handling for non-existent installer")
    else:
        test_result("DELETE non-existent installer (404 handling)", False, f"Expected 404, got {response.status_code}")

# =============================================================================
# TEST 6: TEST BUSINESS LOGIC - PROTECTION AGAINST DELETING INSTALLERS WITH TIME LOGS
# =============================================================================
print("\n🛡️ TEST 6: BUSINESS LOGIC - PROTECTION AGAINST DELETING INSTALLERS WITH TIME LOGS")

# Create another test installer
test_installer_2 = {
    "name": "PROTECTED TEST INSTALLER",
    "cost_rate": 50.0,
    "position": "Protected Electrician",
    "phone": "555-PROTECT",
    "email": "protect.test@example.com",
    "hire_date": datetime.now().date().isoformat()
}

response, error = make_request("POST", "/installers", test_installer_2)
if response and response.status_code in [200, 201]:
    try:
        protected_installer = response.json()
        protected_installer_id = protected_installer.get("id")
        
        # Try to create a time log for this installer (if time log endpoint exists)
        test_timelog = {
            "installer_id": protected_installer_id,
            "project_id": "test-project-id",
            "date": datetime.now().date().isoformat(),
            "hours": 8.0,
            "description": "Test work for protection testing"
        }
        
        # Try to create time log
        timelog_response, timelog_error = make_request("POST", "/timelogs", test_timelog)
        if timelog_response and timelog_response.status_code in [200, 201]:
            print("   📝 Created test time log for protection testing")
            
            # Now try to delete the installer - should be protected
            delete_response, delete_error = make_request("DELETE", f"/installers/{protected_installer_id}")
            if delete_response:
                if delete_response.status_code == 400:
                    try:
                        error_data = delete_response.json()
                        if "time logs" in error_data.get("detail", "").lower():
                            test_result("Business logic protection (time logs)", True, f"Protected: {error_data.get('detail')}")
                        else:
                            test_result("Business logic protection (time logs)", False, f"Wrong error message: {error_data.get('detail')}")
                    except:
                        test_result("Business logic protection (time logs)", False, "Invalid error response format")
                else:
                    test_result("Business logic protection (time logs)", False, f"Expected 400, got {delete_response.status_code}")
            else:
                test_result("Business logic protection (time logs)", False, f"Connection error: {delete_error}")
        else:
            print("   ⚠️ Could not create time log for protection testing - testing deletion anyway")
            # Try to delete without time logs
            delete_response, delete_error = make_request("DELETE", f"/installers/{protected_installer_id}")
            if delete_response and delete_response.status_code == 200:
                test_result("Business logic protection (fallback test)", True, "Installer deleted successfully when no time logs exist")
            else:
                test_result("Business logic protection (fallback test)", False, f"Unexpected result: {delete_response.status_code if delete_response else delete_error}")
                
    except Exception as e:
        test_result("Business logic protection setup", False, f"Setup error: {str(e)}")
else:
    test_result("Business logic protection setup", False, "Could not create protected installer for testing")

# =============================================================================
# TEST 7: VERIFY NO REGRESSION - OTHER INSTALLER ENDPOINTS STILL WORK
# =============================================================================
print("\n🔄 TEST 7: REGRESSION TESTING - OTHER INSTALLER ENDPOINTS")

# Test GET /api/installers
response, error = make_request("GET", "/installers")
if response and response.status_code == 200:
    test_result("GET /api/installers (regression test)", True, f"Status: {response.status_code}")
else:
    test_result("GET /api/installers (regression test)", False, f"Status: {response.status_code if response else 'Connection error'}")

# Test POST /api/installers
regression_installer = {
    "name": "REGRESSION TEST INSTALLER",
    "cost_rate": 40.0,
    "position": "Regression Tester",
    "phone": "555-REGRESS",
    "email": "regression@example.com",
    "hire_date": datetime.now().isoformat()
}

response, error = make_request("POST", "/installers", regression_installer)
if response and response.status_code in [200, 201]:
    test_result("POST /api/installers (regression test)", True, f"Status: {response.status_code}")
    
    # Get the created installer ID for PUT test
    try:
        regression_installer_data = response.json()
        regression_installer_id = regression_installer_data.get("id")
        
        # Test PUT /api/installers/{id}
        update_data = {"cost_rate": 42.0}
        put_response, put_error = make_request("PUT", f"/installers/{regression_installer_id}", update_data)
        if put_response and put_response.status_code == 200:
            test_result("PUT /api/installers/{id} (regression test)", True, f"Status: {put_response.status_code}")
        else:
            test_result("PUT /api/installers/{id} (regression test)", False, f"Status: {put_response.status_code if put_response else 'Connection error'}")
            
        # Clean up - delete the regression test installer
        cleanup_response, cleanup_error = make_request("DELETE", f"/installers/{regression_installer_id}")
        if cleanup_response and cleanup_response.status_code == 200:
            print("   🧹 Cleaned up regression test installer")
            
    except Exception as e:
        test_result("POST /api/installers response parsing", False, f"JSON parsing error: {str(e)}")
else:
    test_result("POST /api/installers (regression test)", False, f"Status: {response.status_code if response else 'Connection error'}")

# =============================================================================
# TEST 8: T&M TAG API STRUCTURE VERIFICATION
# =============================================================================
print("\n📊 TEST 8: T&M TAG API STRUCTURE VERIFICATION")

# Test T&M tag endpoints to identify structure mismatches
tm_endpoints = [
    ("/tm-tags", "GET", "T&M Tags List"),
    ("/timelogs", "GET", "Time Logs List (Alternative)"),
]

for endpoint, method, description in tm_endpoints:
    response, error = make_request(method, endpoint)
    if response:
        if response.status_code == 200:
            test_result(f"{description} endpoint", True, f"Status: {response.status_code}")
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    sample_item = data[0]
                    print(f"   📋 Sample structure: {list(sample_item.keys())[:5]}...")
            except:
                pass
        else:
            test_result(f"{description} endpoint", False, f"Status: {response.status_code}")
    else:
        test_result(f"{description} endpoint", False, f"Connection error: {error}")

# =============================================================================
# COMPREHENSIVE SUMMARY REPORT
# =============================================================================
def generate_summary_report():
    """Generate comprehensive summary report"""
    print("\n" + "=" * 80)
    print("📊 DELETE INSTALLER ENDPOINT TESTING SUMMARY")
    print("=" * 80)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Critical issues
    critical_failures = [r for r in test_results if not r["success"] and r["critical"]]
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
        for failure in critical_failures:
            print(f"   • {failure['test']}: {failure['details']}")
    else:
        print(f"\n✅ NO CRITICAL FAILURES DETECTED")
    
    # All test results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in test_results:
        print(f"   {result['status']} {result['test']}")
        if result['details']:
            print(f"      📝 {result['details']}")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT:")
    if success_rate >= 90:
        print("   ✅ DELETE INSTALLER ENDPOINT FIX IS WORKING CORRECTLY")
        print("   ✅ User's 'Cannot delete crew members' issue should be RESOLVED")
    elif success_rate >= 70:
        print("   ⚠️  DELETE INSTALLER ENDPOINT PARTIALLY WORKING")
        print("   ⚠️  Some issues remain that may affect user experience")
    else:
        print("   🚨 DELETE INSTALLER ENDPOINT FIX IS NOT WORKING")
        print("   🚨 User's 'Cannot delete crew members' issue is NOT RESOLVED")
    
    return success_rate >= 70

print("\n" + "=" * 80)
generate_summary_report()

# =============================================================================
# FINAL RESULTS AND EXIT
# =============================================================================
print(f"\n🔗 Backend URL: {BACKEND_URL}")
print(f"📅 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Check if the critical DELETE functionality is working
delete_tests = [r for r in test_results if "DELETE" in r["test"] and "method support" in r["test"]]
if delete_tests and delete_tests[0]["success"]:
    print(f"\n✅ CRITICAL SUCCESS: DELETE /api/installers/{{id}} endpoint is working")
    print("   💡 User's 'Cannot delete crew members' issue should be RESOLVED")
    sys.exit(0)
else:
    print(f"\n🚨 CRITICAL FAILURE: DELETE /api/installers/{{id}} endpoint is NOT working")
    print("   💡 User's 'Cannot delete crew members' issue is NOT RESOLVED")
    sys.exit(1)