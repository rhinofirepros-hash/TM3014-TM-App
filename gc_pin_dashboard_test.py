#!/usr/bin/env python3
"""
GC PIN System and Dashboard Testing
Tests the simplified GC PIN system and GC Dashboard endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-inspect-app.preview.emergentagent.com/api"

class GCPinDashboardTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "gc_pin": {"passed": 0, "failed": 0, "errors": []},
            "gc_dashboard": {"passed": 0, "failed": 0, "errors": []},
            "projects": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        self.test_project_id = None
        self.test_project_pin = None
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            # Test with a known working endpoint instead of root
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True, "API is accessible via /projects")
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def test_projects_have_gc_pin_field(self):
        """Test GET /api/projects to check if projects have gc_pin field"""
        print("\n=== Testing Projects Have GC PIN Field ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                if isinstance(projects, list) and len(projects) > 0:
                    # Check if projects have gc_pin field
                    projects_with_pin = 0
                    projects_without_pin = 0
                    
                    for project in projects:
                        if "gc_pin" in project and project["gc_pin"]:
                            projects_with_pin += 1
                            # Store first project for testing
                            if not self.test_project_id:
                                self.test_project_id = project["id"]
                                self.test_project_pin = project["gc_pin"]
                        else:
                            projects_without_pin += 1
                    
                    if projects_with_pin > 0:
                        self.log_result("projects", "Projects have GC PIN field", True, 
                                      f"Found {projects_with_pin} projects with GC PINs, {projects_without_pin} without")
                        return True
                    else:
                        self.log_result("projects", "Projects have GC PIN field", False, 
                                      "No projects found with gc_pin field")
                        return False
                else:
                    self.log_result("projects", "Projects have GC PIN field", False, 
                                  "No projects found in database")
                    return False
            else:
                self.log_result("projects", "Projects have GC PIN field", False, 
                              f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("projects", "Projects have GC PIN field", False, str(e))
            return False
    
    def test_gc_pin_generation_for_project(self):
        """Test that projects get auto-generated GC PINs"""
        print("\n=== Testing GC PIN Auto-Generation ===")
        
        # Create a new project to test PIN generation
        project_data = {
            "name": "GC PIN Test Project",
            "description": "Testing GC PIN auto-generation",
            "client_company": "Test GC Company",
            "gc_email": "test@gc.com",
            "contract_amount": 100000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "123 Test Street"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                
                # Check if project has gc_pin and gc_pin_used fields
                if "gc_pin" in project and project["gc_pin"]:
                    pin = project["gc_pin"]
                    # Verify PIN is 4 digits
                    if len(pin) == 4 and pin.isdigit():
                        self.log_result("gc_pin", "GC PIN auto-generation", True, 
                                      f"Project created with 4-digit PIN: {pin}")
                        
                        # Store for later tests
                        self.test_project_id = project["id"]
                        self.test_project_pin = pin
                        
                        # Check gc_pin_used field
                        if "gc_pin_used" in project and project["gc_pin_used"] == False:
                            self.log_result("gc_pin", "GC PIN unused status", True, 
                                          "PIN correctly marked as unused")
                        else:
                            self.log_result("gc_pin", "GC PIN unused status", False, 
                                          "PIN not properly marked as unused")
                        
                        return True
                    else:
                        self.log_result("gc_pin", "GC PIN auto-generation", False, 
                                      f"PIN format invalid: {pin} (should be 4 digits)")
                        return False
                else:
                    self.log_result("gc_pin", "GC PIN auto-generation", False, 
                                  "Project created without gc_pin field")
                    return False
            else:
                self.log_result("gc_pin", "GC PIN auto-generation", False, 
                              f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_pin", "GC PIN auto-generation", False, str(e))
            return False
    
    def test_gc_login_with_valid_pin(self):
        """Test simplified GC login with valid project ID and PIN"""
        print("\n=== Testing GC Login with Valid PIN ===")
        
        if not self.test_project_id or not self.test_project_pin:
            self.log_result("gc_pin", "GC login with valid PIN", False, 
                          "No test project/PIN available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.test_project_pin
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                
                # Check for successful login response
                if "access_token" in login_result or "success" in login_result:
                    self.log_result("gc_pin", "GC login with valid PIN", True, 
                                  f"Successfully logged in with PIN {self.test_project_pin}")
                    
                    # Store new PIN if regenerated
                    if "new_pin" in login_result:
                        old_pin = self.test_project_pin
                        self.test_project_pin = login_result["new_pin"]
                        self.log_result("gc_pin", "PIN regeneration after login", True, 
                                      f"PIN regenerated from {old_pin} to {self.test_project_pin}")
                    
                    return True
                else:
                    self.log_result("gc_pin", "GC login with valid PIN", False, 
                                  "Login response missing expected fields", response)
                    return False
            else:
                self.log_result("gc_pin", "GC login with valid PIN", False, 
                              f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_pin", "GC login with valid PIN", False, str(e))
            return False
    
    def test_gc_login_with_invalid_project_id(self):
        """Test GC login with invalid project ID"""
        print("\n=== Testing GC Login with Invalid Project ID ===")
        
        login_data = {
            "projectId": str(uuid.uuid4()),  # Random UUID
            "pin": "1234"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_result("gc_pin", "GC login with invalid project ID", True, 
                              "Correctly rejected invalid project ID with 401")
                return True
            elif response.status_code == 200:
                result = response.json()
                if "error" in result:
                    self.log_result("gc_pin", "GC login with invalid project ID", True, 
                                  f"Correctly rejected with error: {result['error']}")
                    return True
                else:
                    self.log_result("gc_pin", "GC login with invalid project ID", False, 
                                  "Should have rejected invalid project ID", response)
                    return False
            else:
                self.log_result("gc_pin", "GC login with invalid project ID", False, 
                              f"Unexpected status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_pin", "GC login with invalid project ID", False, str(e))
            return False
    
    def test_gc_login_with_wrong_pin(self):
        """Test GC login with wrong PIN"""
        print("\n=== Testing GC Login with Wrong PIN ===")
        
        if not self.test_project_id:
            self.log_result("gc_pin", "GC login with wrong PIN", False, 
                          "No test project available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": "9999"  # Wrong PIN
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_result("gc_pin", "GC login with wrong PIN", True, 
                              "Correctly rejected wrong PIN with 401")
                return True
            elif response.status_code == 200:
                result = response.json()
                if "error" in result and "Invalid PIN" in result["error"]:
                    self.log_result("gc_pin", "GC login with wrong PIN", True, 
                                  f"Correctly rejected with error: {result['error']}")
                    return True
                else:
                    self.log_result("gc_pin", "GC login with wrong PIN", False, 
                                  "Should have rejected wrong PIN", response)
                    return False
            else:
                self.log_result("gc_pin", "GC login with wrong PIN", False, 
                              f"Unexpected status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_pin", "GC login with wrong PIN", False, str(e))
            return False
    
    def test_gc_dashboard_endpoint(self):
        """Test GET /api/gc/dashboard/{project_id} endpoint"""
        print("\n=== Testing GC Dashboard Endpoint ===")
        
        if not self.test_project_id:
            self.log_result("gc_dashboard", "GC dashboard endpoint", False, 
                          "No test project available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{self.test_project_id}")
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Verify dashboard structure
                expected_fields = ["project_info", "crew_summary", "materials_summary", "tm_tags_summary"]
                missing_fields = [field for field in expected_fields if field not in dashboard_data]
                
                if not missing_fields:
                    self.log_result("gc_dashboard", "GC dashboard endpoint", True, 
                                  "Dashboard data structure is correct")
                    
                    # Verify no financial information is exposed
                    financial_fields = ["cost", "rate", "profit", "billing", "hourly_rate", "total_cost"]
                    financial_exposed = []
                    
                    def check_financial_data(data, path=""):
                        if isinstance(data, dict):
                            for key, value in data.items():
                                current_path = f"{path}.{key}" if path else key
                                if any(fin_field in key.lower() for fin_field in financial_fields):
                                    financial_exposed.append(current_path)
                                check_financial_data(value, current_path)
                        elif isinstance(data, list):
                            for i, item in enumerate(data):
                                check_financial_data(item, f"{path}[{i}]")
                    
                    check_financial_data(dashboard_data)
                    
                    if not financial_exposed:
                        self.log_result("gc_dashboard", "No financial data exposed", True, 
                                      "Dashboard correctly excludes financial information")
                    else:
                        self.log_result("gc_dashboard", "No financial data exposed", False, 
                                      f"Financial data exposed: {financial_exposed}")
                    
                    return True
                else:
                    self.log_result("gc_dashboard", "GC dashboard endpoint", False, 
                                  f"Missing required fields: {missing_fields}", response)
                    return False
            else:
                self.log_result("gc_dashboard", "GC dashboard endpoint", False, 
                              f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_dashboard", "GC dashboard endpoint", False, str(e))
            return False
    
    def test_project_data_completeness(self):
        """Test GET /api/projects/{project_id} to verify project data is complete"""
        print("\n=== Testing Project Data Completeness ===")
        
        if not self.test_project_id:
            self.log_result("projects", "Project data completeness", False, 
                          "No test project available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                project_data = response.json()
                
                # Check for essential project fields
                essential_fields = [
                    "id", "name", "client_company", "gc_email", "project_manager",
                    "start_date", "status", "created_at", "gc_pin", "gc_pin_used"
                ]
                
                missing_fields = [field for field in essential_fields if field not in project_data]
                
                if not missing_fields:
                    self.log_result("projects", "Project data completeness", True, 
                                  "All essential project fields present")
                    
                    # Verify GC PIN is present and valid
                    gc_pin = project_data.get("gc_pin")
                    if gc_pin and len(gc_pin) == 4 and gc_pin.isdigit():
                        self.log_result("projects", "Project GC PIN validity", True, 
                                      f"GC PIN is valid: {gc_pin}")
                    else:
                        self.log_result("projects", "Project GC PIN validity", False, 
                                      f"GC PIN is invalid: {gc_pin}")
                    
                    return True
                else:
                    self.log_result("projects", "Project data completeness", False, 
                                  f"Missing essential fields: {missing_fields}", response)
                    return False
            else:
                self.log_result("projects", "Project data completeness", False, 
                              f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("projects", "Project data completeness", False, str(e))
            return False
    
    def test_pin_regeneration_after_login(self):
        """Test that PIN is regenerated after successful login"""
        print("\n=== Testing PIN Regeneration After Login ===")
        
        if not self.test_project_id or not self.test_project_pin:
            self.log_result("gc_pin", "PIN regeneration after login", False, 
                          "No test project/PIN available")
            return False
        
        # Store original PIN
        original_pin = self.test_project_pin
        
        # Login with current PIN
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.test_project_pin
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Check project to see if PIN was regenerated
                project_response = self.session.get(f"{self.base_url}/projects/{self.test_project_id}")
                
                if project_response.status_code == 200:
                    project_data = project_response.json()
                    new_pin = project_data.get("gc_pin")
                    
                    if new_pin and new_pin != original_pin:
                        self.log_result("gc_pin", "PIN regeneration after login", True, 
                                      f"PIN regenerated from {original_pin} to {new_pin}")
                        
                        # Test that old PIN no longer works
                        old_pin_login = {
                            "projectId": self.test_project_id,
                            "pin": original_pin
                        }
                        
                        old_pin_response = self.session.post(
                            f"{self.base_url}/gc/login-simple",
                            json=old_pin_login,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if old_pin_response.status_code == 401:
                            self.log_result("gc_pin", "Old PIN rejection", True, 
                                          "Old PIN correctly rejected after regeneration")
                        else:
                            self.log_result("gc_pin", "Old PIN rejection", False, 
                                          "Old PIN should be rejected after regeneration")
                        
                        # Update stored PIN
                        self.test_project_pin = new_pin
                        return True
                    else:
                        self.log_result("gc_pin", "PIN regeneration after login", False, 
                                      f"PIN not regenerated (still {original_pin})")
                        return False
                else:
                    self.log_result("gc_pin", "PIN regeneration after login", False, 
                                  "Could not retrieve project after login")
                    return False
            else:
                self.log_result("gc_pin", "PIN regeneration after login", False, 
                              f"Login failed: HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_pin", "PIN regeneration after login", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all GC PIN and Dashboard tests"""
        print("🚀 Starting GC PIN System and Dashboard Testing")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Test GC PIN System
        print("\n🔐 TESTING GC PIN SYSTEM")
        print("-" * 40)
        
        self.test_projects_have_gc_pin_field()
        self.test_gc_pin_generation_for_project()
        self.test_gc_login_with_valid_pin()
        self.test_gc_login_with_invalid_project_id()
        self.test_gc_login_with_wrong_pin()
        self.test_pin_regeneration_after_login()
        
        # Test GC Dashboard
        print("\n📊 TESTING GC DASHBOARD")
        print("-" * 40)
        
        self.test_gc_dashboard_endpoint()
        
        # Test Project Management
        print("\n📋 TESTING PROJECT MANAGEMENT")
        print("-" * 40)
        
        self.test_project_data_completeness()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            if passed + failed > 0:
                success_rate = (passed / (passed + failed)) * 100
                print(f"{category.upper()}: {passed} passed, {failed} failed ({success_rate:.1f}% success)")
                
                if results["errors"]:
                    print(f"  Errors:")
                    for error in results["errors"]:
                        print(f"    - {error}")
        
        overall_success_rate = (total_passed / (total_passed + total_failed)) * 100 if (total_passed + total_failed) > 0 else 0
        
        print(f"\nOVERALL: {total_passed} passed, {total_failed} failed ({overall_success_rate:.1f}% success)")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total_failed} TESTS FAILED")

def main():
    """Main function to run the tests"""
    tester = GCPinDashboardTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()