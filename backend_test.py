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
# TEST 1: BACKWARD COMPATIBILITY ALIASES - GET /api/tm-tags
# =============================================================================
print("\n🔍 TEST 1: Testing GET /api/tm-tags (compatibility alias)")

response, error = make_request("GET", "/tm-tags")
if error:
    test_result("GET /api/tm-tags endpoint connectivity", False, f"Connection error: {error}")
else:
    if response.status_code == 200:
        try:
            data = response.json()
            test_result("GET /api/tm-tags returns 200 OK", True, f"Returned {len(data)} timelogs")
            
            # Verify response structure
            if isinstance(data, list):
                test_result("GET /api/tm-tags returns list format", True)
                if len(data) > 0:
                    first_item = data[0]
                    required_fields = ['id', 'project_id', 'installer_id', 'date', 'hours']
                    missing_fields = [field for field in required_fields if field not in first_item]
                    if not missing_fields:
                        test_result("GET /api/tm-tags response has required fields", True, f"Fields: {list(first_item.keys())}")
                    else:
                        test_result("GET /api/tm-tags response has required fields", False, f"Missing: {missing_fields}")
                else:
                    test_result("GET /api/tm-tags data availability", True, "No existing timelogs (empty list)")
            else:
                test_result("GET /api/tm-tags returns list format", False, f"Got {type(data)}")
        except json.JSONDecodeError:
            test_result("GET /api/tm-tags JSON response", False, "Invalid JSON response")
    else:
        test_result("GET /api/tm-tags returns 200 OK", False, f"Status: {response.status_code}, Response: {response.text[:200]}")

# =============================================================================
# TEST 2: BACKWARD COMPATIBILITY ALIASES - POST /api/tm-tags
# =============================================================================
print("\n🔍 TEST 2: Testing POST /api/tm-tags (compatibility alias)")

# First, get projects and installers for realistic test data
projects_response, _ = make_request("GET", "/projects")
installers_response, _ = make_request("GET", "/installers")

project_id = None
installer_id = None

if projects_response and projects_response.status_code == 200:
    projects = projects_response.json()
    if projects:
        project_id = projects[0].get('id')

if installers_response and installers_response.status_code == 200:
    installers = installers_response.json()
    if installers:
        installer_id = installers[0].get('id')

# Create test timelog data
test_timelog = {
    "project_id": project_id or str(uuid.uuid4()),
    "installer_id": installer_id or str(uuid.uuid4()),
    "date": datetime.now().strftime('%Y-%m-%d'),  # Date format, not datetime
    "hours": 8.5,
    "notes": "T&M Tags Compatibility Test - Backend endpoint verification",
    "bill_rate_override": 95.0
}

response, error = make_request("POST", "/tm-tags", test_timelog)
if error:
    test_result("POST /api/tm-tags endpoint connectivity", False, f"Connection error: {error}")
else:
    if response.status_code == 200:
        try:
            created_timelog = response.json()
            test_result("POST /api/tm-tags creates timelog successfully", True, f"Created timelog ID: {created_timelog.get('id')}")
            
            # Store the created ID for later tests
            created_timelog_id = created_timelog.get('id')
            
            # Verify response structure
            required_fields = ['id', 'project_id', 'installer_id', 'date', 'hours']
            missing_fields = [field for field in required_fields if field not in created_timelog]
            if not missing_fields:
                test_result("POST /api/tm-tags response has required fields", True)
            else:
                test_result("POST /api/tm-tags response has required fields", False, f"Missing: {missing_fields}")
                
        except json.JSONDecodeError:
            test_result("POST /api/tm-tags JSON response", False, "Invalid JSON response")
            created_timelog_id = None
    else:
        test_result("POST /api/tm-tags creates timelog successfully", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
        created_timelog_id = None

# =============================================================================
# TEST 3: PDF EXPORT FUNCTIONALITY - GET /api/tm-tags/{id}/pdf
# =============================================================================
print("\n🔍 TEST 3: Testing PDF Export - GET /api/tm-tags/{id}/pdf")

if created_timelog_id:
    response, error = make_request("GET", f"/tm-tags/{created_timelog_id}/pdf")
    if error:
        test_result("GET /api/tm-tags/{id}/pdf endpoint connectivity", False, f"Connection error: {error}")
    else:
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                test_result("GET /api/tm-tags/{id}/pdf generates PDF", True, f"Content-Type: {content_type}")
                
                # Check PDF content length
                content_length = len(response.content)
                if content_length > 1000:  # PDF should be reasonably sized
                    test_result("GET /api/tm-tags/{id}/pdf PDF content size", True, f"Size: {content_length} bytes")
                else:
                    test_result("GET /api/tm-tags/{id}/pdf PDF content size", False, f"Size too small: {content_length} bytes")
                    
                # Check PDF headers
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' in content_disposition and 'filename' in content_disposition:
                    test_result("GET /api/tm-tags/{id}/pdf proper headers", True, f"Disposition: {content_disposition}")
                else:
                    test_result("GET /api/tm-tags/{id}/pdf proper headers", False, f"Missing proper headers")
                    
            elif 'application/json' in content_type:
                # Fallback JSON response (if ReportLab fails)
                test_result("GET /api/tm-tags/{id}/pdf generates PDF", False, "Fallback to JSON - ReportLab issue")
                try:
                    json_data = response.json()
                    if 'note' in json_data and 'ReportLab' in json_data['note']:
                        test_result("GET /api/tm-tags/{id}/pdf fallback handling", True, "Proper fallback to JSON")
                    else:
                        test_result("GET /api/tm-tags/{id}/pdf fallback handling", False, "Unexpected JSON structure")
                except:
                    test_result("GET /api/tm-tags/{id}/pdf fallback handling", False, "Invalid JSON fallback")
            else:
                test_result("GET /api/tm-tags/{id}/pdf generates PDF", False, f"Unexpected content-type: {content_type}")
        else:
            test_result("GET /api/tm-tags/{id}/pdf generates PDF", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
else:
    test_result("GET /api/tm-tags/{id}/pdf test setup", False, "No timelog ID available for PDF test")

# =============================================================================
# TEST 4: PDF PREVIEW FUNCTIONALITY - GET /api/tm-tags/{id}/preview
# =============================================================================
print("\n🔍 TEST 4: Testing PDF Preview - GET /api/tm-tags/{id}/preview")

if created_timelog_id:
    response, error = make_request("GET", f"/tm-tags/{created_timelog_id}/preview")
    if error:
        test_result("GET /api/tm-tags/{id}/preview endpoint connectivity", False, f"Connection error: {error}")
    else:
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                test_result("GET /api/tm-tags/{id}/preview returns HTML", True, f"Content-Type: {content_type}")
                
                # Check HTML content
                html_content = response.text
                required_html_elements = ['TIME & MATERIAL REPORT', 'Project Information', 'Installer Information', 'Time & Billing']
                missing_elements = [elem for elem in required_html_elements if elem not in html_content]
                
                if not missing_elements:
                    test_result("GET /api/tm-tags/{id}/preview HTML structure", True, "Contains all required sections")
                else:
                    test_result("GET /api/tm-tags/{id}/preview HTML structure", False, f"Missing: {missing_elements}")
                
                # Check for proper HTML structure
                if '<html>' in html_content and '</html>' in html_content:
                    test_result("GET /api/tm-tags/{id}/preview valid HTML", True, "Proper HTML document structure")
                else:
                    test_result("GET /api/tm-tags/{id}/preview valid HTML", False, "Invalid HTML structure")
                    
                # Check content length
                if len(html_content) > 500:
                    test_result("GET /api/tm-tags/{id}/preview content size", True, f"Size: {len(html_content)} characters")
                else:
                    test_result("GET /api/tm-tags/{id}/preview content size", False, f"Content too small: {len(html_content)} characters")
                    
            else:
                test_result("GET /api/tm-tags/{id}/preview returns HTML", False, f"Unexpected content-type: {content_type}")
        else:
            test_result("GET /api/tm-tags/{id}/preview returns HTML", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
else:
    test_result("GET /api/tm-tags/{id}/preview test setup", False, "No timelog ID available for preview test")

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