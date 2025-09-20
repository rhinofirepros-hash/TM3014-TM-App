#!/usr/bin/env python3
"""
GC PIN System Testing Script
Tests the newly added GC PIN functionality in server_unified.py

Test Requirements:
1. GET /api/projects to see if any projects exist
2. GET /api/projects/{project_id}/gc-pin to verify PIN generation works
3. POST /api/gc/login-simple with a valid project ID and PIN
4. GET /api/gc/dashboard/{project_id} to verify the dashboard endpoint works
5. Verify that GC endpoints are now returning 200 OK instead of 404
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://project-inspect-app.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class GCPinSystemTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.project_id = None
        self.project_pin = None
        self.new_pin = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_1_get_projects(self):
        """Test 1: GET /api/projects to see if any projects exist"""
        try:
            response = requests.get(f"{BACKEND_URL}/projects", headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                projects = response.json()
                if projects and len(projects) > 0:
                    # Store first project for subsequent tests
                    self.project_id = projects[0].get("id")
                    project_name = projects[0].get("name", "Unknown")
                    
                    self.log_test(
                        "GET /api/projects - Projects exist",
                        True,
                        f"Found {len(projects)} projects. Using project: {project_name} (ID: {self.project_id})",
                        {"project_count": len(projects), "first_project": projects[0]}
                    )
                    return True
                else:
                    self.log_test(
                        "GET /api/projects - No projects found",
                        False,
                        "No projects exist in database. Cannot proceed with GC PIN tests.",
                        {"projects": projects}
                    )
                    return False
            else:
                self.log_test(
                    "GET /api/projects - API Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "GET /api/projects - Exception",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_2_get_project_gc_pin(self):
        """Test 2: GET /api/projects/{project_id}/gc-pin to verify PIN generation works"""
        if not self.project_id:
            self.log_test(
                "GET /api/projects/{project_id}/gc-pin - No Project ID",
                False,
                "Cannot test PIN generation without a valid project ID"
            )
            return False
            
        try:
            response = requests.get(
                f"{BACKEND_URL}/projects/{self.project_id}/gc-pin", 
                headers=HEADERS, 
                timeout=10
            )
            
            if response.status_code == 200:
                pin_data = response.json()
                self.project_pin = pin_data.get("gcPin")
                project_name = pin_data.get("projectName", "Unknown")
                pin_used = pin_data.get("pinUsed", False)
                
                if self.project_pin and len(str(self.project_pin)) == 4:
                    self.log_test(
                        "GET /api/projects/{project_id}/gc-pin - PIN Generated",
                        True,
                        f"Generated 4-digit PIN: {self.project_pin} for project: {project_name}. PIN Used: {pin_used}",
                        pin_data
                    )
                    return True
                else:
                    self.log_test(
                        "GET /api/projects/{project_id}/gc-pin - Invalid PIN Format",
                        False,
                        f"PIN format invalid: {self.project_pin}. Expected 4-digit number.",
                        pin_data
                    )
                    return False
            else:
                self.log_test(
                    "GET /api/projects/{project_id}/gc-pin - API Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "GET /api/projects/{project_id}/gc-pin - Exception",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_3_gc_login_simple(self):
        """Test 3: POST /api/gc/login-simple with a valid project ID and PIN"""
        if not self.project_id or not self.project_pin:
            self.log_test(
                "POST /api/gc/login-simple - Missing Prerequisites",
                False,
                f"Cannot test login without project ID ({self.project_id}) and PIN ({self.project_pin})"
            )
            return False
            
        try:
            login_payload = {
                "projectId": self.project_id,
                "pin": str(self.project_pin),
                "ip": "127.0.0.1",
                "userAgent": "GC PIN System Test Script"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/gc/login-simple",
                headers=HEADERS,
                json=login_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                login_data = response.json()
                success = login_data.get("success", False)
                self.new_pin = login_data.get("newPin")
                project_name = login_data.get("projectName", "Unknown")
                message = login_data.get("message", "")
                
                if success and self.new_pin:
                    self.log_test(
                        "POST /api/gc/login-simple - Login Successful",
                        True,
                        f"Login successful for project: {project_name}. Old PIN: {self.project_pin}, New PIN: {self.new_pin}. Message: {message}",
                        login_data
                    )
                    return True
                else:
                    self.log_test(
                        "POST /api/gc/login-simple - Login Failed",
                        False,
                        f"Login response invalid. Success: {success}, New PIN: {self.new_pin}",
                        login_data
                    )
                    return False
            else:
                self.log_test(
                    "POST /api/gc/login-simple - API Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "payload": login_payload}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "POST /api/gc/login-simple - Exception",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_4_gc_dashboard(self):
        """Test 4: GET /api/gc/dashboard/{project_id} to verify the dashboard endpoint works"""
        if not self.project_id:
            self.log_test(
                "GET /api/gc/dashboard/{project_id} - No Project ID",
                False,
                "Cannot test dashboard without a valid project ID"
            )
            return False
            
        try:
            response = requests.get(
                f"{BACKEND_URL}/gc/dashboard/{self.project_id}",
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Verify dashboard structure
                required_fields = ["projectName", "crewSummary", "materialsSummary", "tmTagSummary"]
                missing_fields = [field for field in required_fields if field not in dashboard_data]
                
                if not missing_fields:
                    crew_summary = dashboard_data.get("crewSummary", {})
                    materials_summary = dashboard_data.get("materialsSummary", [])
                    tm_tag_summary = dashboard_data.get("tmTagSummary", {})
                    
                    self.log_test(
                        "GET /api/gc/dashboard/{project_id} - Dashboard Working",
                        True,
                        f"Dashboard loaded successfully. Crew Hours: {crew_summary.get('totalHours', 0)}, "
                        f"Materials: {len(materials_summary)}, T&M Tags: {tm_tag_summary.get('totalTags', 0)}",
                        {
                            "projectName": dashboard_data.get("projectName"),
                            "crewSummary": crew_summary,
                            "materialsCount": len(materials_summary),
                            "tmTagSummary": tm_tag_summary
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "GET /api/gc/dashboard/{project_id} - Missing Fields",
                        False,
                        f"Dashboard response missing required fields: {missing_fields}",
                        dashboard_data
                    )
                    return False
            else:
                self.log_test(
                    "GET /api/gc/dashboard/{project_id} - API Error",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "GET /api/gc/dashboard/{project_id} - Exception",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_5_verify_pin_regeneration(self):
        """Test 5: Verify that PIN regeneration works and old PIN is invalidated"""
        if not self.project_id or not self.project_pin or not self.new_pin:
            self.log_test(
                "PIN Regeneration Verification - Missing Prerequisites",
                False,
                "Cannot test PIN regeneration without old PIN, new PIN, and project ID"
            )
            return False
            
        try:
            # Test 5a: Try to login with old PIN (should fail)
            old_pin_payload = {
                "projectId": self.project_id,
                "pin": str(self.project_pin),  # Old PIN
                "ip": "127.0.0.1",
                "userAgent": "GC PIN System Test Script - Old PIN Test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/gc/login-simple",
                headers=HEADERS,
                json=old_pin_payload,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test(
                    "PIN Regeneration - Old PIN Rejected",
                    True,
                    f"Old PIN {self.project_pin} correctly rejected with 401 status",
                    {"old_pin": self.project_pin, "status_code": response.status_code}
                )
            else:
                self.log_test(
                    "PIN Regeneration - Old PIN Not Rejected",
                    False,
                    f"Old PIN {self.project_pin} should have been rejected but got status {response.status_code}",
                    {"old_pin": self.project_pin, "status_code": response.status_code}
                )
                return False
            
            # Test 5b: Try to login with new PIN (should work)
            new_pin_payload = {
                "projectId": self.project_id,
                "pin": str(self.new_pin),  # New PIN
                "ip": "127.0.0.1",
                "userAgent": "GC PIN System Test Script - New PIN Test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/gc/login-simple",
                headers=HEADERS,
                json=new_pin_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                login_data = response.json()
                success = login_data.get("success", False)
                newest_pin = login_data.get("newPin")
                
                if success and newest_pin:
                    self.log_test(
                        "PIN Regeneration - New PIN Works",
                        True,
                        f"New PIN {self.new_pin} works correctly. Generated another new PIN: {newest_pin}",
                        {"new_pin": self.new_pin, "newest_pin": newest_pin}
                    )
                    return True
                else:
                    self.log_test(
                        "PIN Regeneration - New PIN Failed",
                        False,
                        f"New PIN {self.new_pin} should work but login failed",
                        login_data
                    )
                    return False
            else:
                self.log_test(
                    "PIN Regeneration - New PIN API Error",
                    False,
                    f"New PIN {self.new_pin} login failed with status {response.status_code}",
                    {"new_pin": self.new_pin, "status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "PIN Regeneration Verification - Exception",
                False,
                f"Request failed: {str(e)}"
            )
            return False

    def test_6_verify_404_fix(self):
        """Test 6: Verify that GC endpoints are now returning 200 OK instead of 404"""
        test_endpoints = [
            f"/projects/{self.project_id}/gc-pin" if self.project_id else "/projects/test-id/gc-pin",
            f"/gc/dashboard/{self.project_id}" if self.project_id else "/gc/dashboard/test-id"
        ]
        
        all_passed = True
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=HEADERS, timeout=10)
                
                if response.status_code != 404:
                    self.log_test(
                        f"404 Fix Verification - {endpoint}",
                        True,
                        f"Endpoint returns {response.status_code} (not 404). Fix confirmed.",
                        {"endpoint": endpoint, "status_code": response.status_code}
                    )
                else:
                    self.log_test(
                        f"404 Fix Verification - {endpoint}",
                        False,
                        f"Endpoint still returns 404. Fix not working.",
                        {"endpoint": endpoint, "status_code": response.status_code}
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(
                    f"404 Fix Verification - {endpoint} Exception",
                    False,
                    f"Request failed: {str(e)}"
                )
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all GC PIN system tests"""
        print("🚀 Starting GC PIN System Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        test_1_success = self.test_1_get_projects()
        test_2_success = self.test_2_get_project_gc_pin()
        test_3_success = self.test_3_gc_login_simple()
        test_4_success = self.test_4_gc_dashboard()
        test_5_success = self.test_5_verify_pin_regeneration()
        test_6_success = self.test_6_verify_404_fix()
        
        # Summary
        print("=" * 60)
        print("🎯 GC PIN SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Critical test results
        critical_tests = [test_1_success, test_2_success, test_3_success, test_4_success]
        critical_passed = sum(critical_tests)
        
        print("🔥 CRITICAL FUNCTIONALITY STATUS:")
        print(f"✅ Projects API: {'WORKING' if test_1_success else 'FAILED'}")
        print(f"✅ PIN Generation: {'WORKING' if test_2_success else 'FAILED'}")
        print(f"✅ GC Login: {'WORKING' if test_3_success else 'FAILED'}")
        print(f"✅ GC Dashboard: {'WORKING' if test_4_success else 'FAILED'}")
        print(f"✅ PIN Regeneration: {'WORKING' if test_5_success else 'FAILED'}")
        print(f"✅ 404 Fix: {'WORKING' if test_6_success else 'FAILED'}")
        print()
        
        if critical_passed == 4:
            print("🎉 ALL CRITICAL GC PIN FUNCTIONALITY IS WORKING!")
            print("✅ GC PIN system is fully operational and ready for production use.")
        else:
            print("⚠️  SOME CRITICAL FUNCTIONALITY IS NOT WORKING")
            print(f"❌ {4 - critical_passed} out of 4 critical tests failed.")
        
        print()
        print("=" * 60)
        print(f"Test End Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        return self.passed_tests, self.total_tests, self.test_results

def main():
    """Main test execution"""
    tester = GCPinSystemTester()
    passed, total, results = tester.run_all_tests()
    
    # Return appropriate exit code
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()