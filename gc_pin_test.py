#!/usr/bin/env python3
"""
GC PIN System Testing - Comprehensive Test Suite
Tests the new simplified GC PIN system that automatically generates PINs for projects
and allows one-time access that regenerates new PINs.
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import time
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

class GCPinTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "pin_generation": {"passed": 0, "failed": 0, "errors": []},
            "gc_login": {"passed": 0, "failed": 0, "errors": []},
            "pin_regeneration": {"passed": 0, "failed": 0, "errors": []},
            "access_logging": {"passed": 0, "failed": 0, "errors": []},
            "data_security": {"passed": 0, "failed": 0, "errors": []},
            "pin_uniqueness": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        self.created_projects = []
        
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
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True)
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def create_test_project(self, name_suffix=""):
        """Create a test project for PIN testing"""
        project_data = {
            "name": f"GC PIN Test Project {name_suffix}",
            "description": "Test project for GC PIN system validation",
            "client_company": "Test GC Company",
            "gc_email": "test.gc@example.com",
            "contract_amount": 100000.00,
            "labor_rate": 95.0,
            "project_manager": "Test Manager",
            "start_date": datetime.now().isoformat(),
            "address": "123 Test Street, Test City, TS 12345"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                self.created_projects.append(project)
                return project
            else:
                print(f"Failed to create test project: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating test project: {e}")
            return None
    
    def test_automatic_pin_generation_new_project(self):
        """Test 1: Automatic PIN Generation for New Projects"""
        print("\n=== Test 1: Automatic PIN Generation for New Projects ===")
        
        # Create a new project and verify it gets a PIN
        project = self.create_test_project("AutoPIN")
        
        if not project:
            self.log_result("pin_generation", "New project PIN generation", False, "Could not create test project")
            return False
        
        # Check if project has gc_pin in response
        if "gc_pin" in project and project["gc_pin"]:
            pin = project["gc_pin"]
            if len(str(pin)) == 4 and str(pin).isdigit():
                self.log_result("pin_generation", "New project PIN generation", True, f"Project created with 4-digit PIN: {pin}")
                self.test_project_id = project["id"]
                self.test_project_pin = pin
                return True
            else:
                self.log_result("pin_generation", "New project PIN generation", False, f"Invalid PIN format: {pin}")
        else:
            self.log_result("pin_generation", "New project PIN generation", False, "No gc_pin in project response")
        
        return False
    
    def test_automatic_pin_generation_existing_projects(self):
        """Test 2: Verify existing projects get PINs via GET /api/projects"""
        print("\n=== Test 2: Automatic PIN Generation for Existing Projects ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                
                if not projects:
                    self.log_result("pin_generation", "Existing projects PIN generation", False, "No projects found")
                    return False
                
                projects_with_pins = 0
                valid_pins = 0
                
                for project in projects:
                    if project.get("gc_pin"):
                        projects_with_pins += 1
                        pin = str(project["gc_pin"])
                        if len(pin) == 4 and pin.isdigit():
                            valid_pins += 1
                
                if projects_with_pins == len(projects) and valid_pins == projects_with_pins:
                    self.log_result("pin_generation", "Existing projects PIN generation", True, 
                                  f"All {len(projects)} projects have valid 4-digit PINs")
                    return True
                else:
                    self.log_result("pin_generation", "Existing projects PIN generation", False, 
                                  f"Only {projects_with_pins}/{len(projects)} projects have PINs, {valid_pins} valid")
            else:
                self.log_result("pin_generation", "Existing projects PIN generation", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_generation", "Existing projects PIN generation", False, str(e))
        
        return False
    
    def test_get_project_gc_pin_endpoint(self):
        """Test 3: GET /api/projects/{project_id}/gc-pin endpoint"""
        print("\n=== Test 3: Get Project GC PIN Endpoint ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("pin_generation", "Get project GC PIN endpoint", False, "No test project available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{self.test_project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                required_fields = ["projectId", "projectName", "gcPin", "pinUsed"]
                
                missing_fields = [field for field in required_fields if field not in pin_data]
                if not missing_fields:
                    if pin_data["projectId"] == self.test_project_id and len(str(pin_data["gcPin"])) == 4:
                        self.log_result("pin_generation", "Get project GC PIN endpoint", True, 
                                      f"Retrieved PIN: {pin_data['gcPin']}, Used: {pin_data['pinUsed']}")
                        return True
                    else:
                        self.log_result("pin_generation", "Get project GC PIN endpoint", False, 
                                      "Invalid project ID or PIN format")
                else:
                    self.log_result("pin_generation", "Get project GC PIN endpoint", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("pin_generation", "Get project GC PIN endpoint", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_generation", "Get project GC PIN endpoint", False, str(e))
        
        return False
    
    def test_gc_login_valid_pin(self):
        """Test 4: GC Login with Valid PIN"""
        print("\n=== Test 4: GC Login with Valid PIN ===")
        
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'test_project_pin'):
            self.log_result("gc_login", "Valid PIN login", False, "No test project or PIN available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.test_project_pin,
            "ip": "192.168.1.100",
            "userAgent": "GC PIN Test Suite"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                required_fields = ["success", "projectId", "projectName", "message", "newPin"]
                
                missing_fields = [field for field in required_fields if field not in login_result]
                if not missing_fields:
                    if (login_result["success"] and 
                        login_result["projectId"] == self.test_project_id and
                        len(str(login_result["newPin"])) == 4):
                        
                        self.log_result("gc_login", "Valid PIN login", True, 
                                      f"Login successful, new PIN: {login_result['newPin']}")
                        self.new_pin = login_result["newPin"]
                        return True
                    else:
                        self.log_result("gc_login", "Valid PIN login", False, "Invalid login response data")
                else:
                    self.log_result("gc_login", "Valid PIN login", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("gc_login", "Valid PIN login", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Valid PIN login", False, str(e))
        
        return False
    
    def test_gc_login_used_pin(self):
        """Test 5: GC Login with Already Used PIN (should fail)"""
        print("\n=== Test 5: GC Login with Already Used PIN ===")
        
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'test_project_pin'):
            self.log_result("gc_login", "Used PIN login failure", False, "No test project or PIN available")
            return False
        
        # Try to use the old PIN again (should fail)
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.test_project_pin,  # Old PIN that was already used
            "ip": "192.168.1.101",
            "userAgent": "GC PIN Test Suite - Used PIN Test"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                error_data = response.json()
                if "Invalid PIN or PIN already used" in error_data.get("detail", ""):
                    self.log_result("gc_login", "Used PIN login failure", True, 
                                  "Correctly rejected already used PIN")
                    return True
                else:
                    self.log_result("gc_login", "Used PIN login failure", False, 
                                  f"Wrong error message: {error_data.get('detail')}")
            else:
                self.log_result("gc_login", "Used PIN login failure", False, 
                              f"Expected 401, got {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Used PIN login failure", False, str(e))
        
        return False
    
    def test_gc_login_invalid_project(self):
        """Test 6: GC Login with Invalid Project ID"""
        print("\n=== Test 6: GC Login with Invalid Project ID ===")
        
        fake_project_id = str(uuid.uuid4())
        login_data = {
            "projectId": fake_project_id,
            "pin": "1234",
            "ip": "192.168.1.102",
            "userAgent": "GC PIN Test Suite - Invalid Project Test"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                error_data = response.json()
                if "Invalid PIN or PIN already used" in error_data.get("detail", ""):
                    self.log_result("gc_login", "Invalid project login failure", True, 
                                  "Correctly rejected invalid project ID")
                    return True
                else:
                    self.log_result("gc_login", "Invalid project login failure", False, 
                                  f"Wrong error message: {error_data.get('detail')}")
            else:
                self.log_result("gc_login", "Invalid project login failure", False, 
                              f"Expected 401, got {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Invalid project login failure", False, str(e))
        
        return False
    
    def test_gc_login_wrong_pin(self):
        """Test 7: GC Login with Wrong PIN"""
        print("\n=== Test 7: GC Login with Wrong PIN ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("gc_login", "Wrong PIN login failure", False, "No test project available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": "9999",  # Wrong PIN
            "ip": "192.168.1.103",
            "userAgent": "GC PIN Test Suite - Wrong PIN Test"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                error_data = response.json()
                if "Invalid PIN or PIN already used" in error_data.get("detail", ""):
                    self.log_result("gc_login", "Wrong PIN login failure", True, 
                                  "Correctly rejected wrong PIN")
                    return True
                else:
                    self.log_result("gc_login", "Wrong PIN login failure", False, 
                                  f"Wrong error message: {error_data.get('detail')}")
            else:
                self.log_result("gc_login", "Wrong PIN login failure", False, 
                              f"Expected 401, got {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Wrong PIN login failure", False, str(e))
        
        return False
    
    def test_pin_regeneration_after_login(self):
        """Test 8: PIN Regeneration After Successful Login"""
        print("\n=== Test 8: PIN Regeneration After Successful Login ===")
        
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'new_pin'):
            self.log_result("pin_regeneration", "PIN regeneration verification", False, 
                          "No test project or new PIN available")
            return False
        
        # Verify the old PIN is marked as used and new PIN is different
        try:
            response = self.session.get(f"{self.base_url}/projects/{self.test_project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                current_pin = pin_data.get("gcPin")
                
                if current_pin == self.new_pin and current_pin != self.test_project_pin:
                    self.log_result("pin_regeneration", "PIN regeneration verification", True, 
                                  f"PIN successfully regenerated from {self.test_project_pin} to {current_pin}")
                    return True
                else:
                    self.log_result("pin_regeneration", "PIN regeneration verification", False, 
                                  f"PIN not properly regenerated. Old: {self.test_project_pin}, Current: {current_pin}, Expected: {self.new_pin}")
            else:
                self.log_result("pin_regeneration", "PIN regeneration verification", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_regeneration", "PIN regeneration verification", False, str(e))
        
        return False
    
    def test_new_pin_works_for_next_login(self):
        """Test 9: New PIN Works for Next Login"""
        print("\n=== Test 9: New PIN Works for Next Login ===")
        
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'new_pin'):
            self.log_result("pin_regeneration", "New PIN login test", False, 
                          "No test project or new PIN available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.new_pin,
            "ip": "192.168.1.104",
            "userAgent": "GC PIN Test Suite - New PIN Test"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                if (login_result.get("success") and 
                    login_result.get("projectId") == self.test_project_id and
                    login_result.get("newPin") != self.new_pin):
                    
                    self.log_result("pin_regeneration", "New PIN login test", True, 
                                  f"New PIN login successful, next PIN: {login_result['newPin']}")
                    self.latest_pin = login_result["newPin"]
                    return True
                else:
                    self.log_result("pin_regeneration", "New PIN login test", False, 
                                  "Invalid login response")
            else:
                self.log_result("pin_regeneration", "New PIN login test", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_regeneration", "New PIN login test", False, str(e))
        
        return False
    
    def test_access_logging_successful_login(self):
        """Test 10: Access Logging for Successful Login"""
        print("\n=== Test 10: Access Logging for Successful Login ===")
        
        # Note: This test assumes we have admin access to logs
        # In a real scenario, this might require admin authentication
        try:
            response = self.session.get(f"{self.base_url}/gc/access-logs/admin")
            
            if response.status_code == 200:
                logs = response.json()
                
                # Look for our test project logs
                test_logs = [log for log in logs if log.get("projectId") == getattr(self, 'test_project_id', '')]
                successful_logs = [log for log in test_logs if log.get("status") == "success"]
                
                if successful_logs:
                    latest_log = successful_logs[0]  # Should be sorted by timestamp desc
                    required_fields = ["projectId", "timestamp", "ip", "status", "userAgent", "usedPin", "newPin"]
                    
                    missing_fields = [field for field in required_fields if field not in latest_log]
                    if not missing_fields:
                        self.log_result("access_logging", "Successful login logging", True, 
                                      f"Login logged with IP: {latest_log['ip']}, Status: {latest_log['status']}")
                        return True
                    else:
                        self.log_result("access_logging", "Successful login logging", False, 
                                      f"Missing log fields: {missing_fields}")
                else:
                    self.log_result("access_logging", "Successful login logging", False, 
                                  "No successful login logs found for test project")
            else:
                self.log_result("access_logging", "Successful login logging", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("access_logging", "Successful login logging", False, str(e))
        
        return False
    
    def test_access_logging_failed_login(self):
        """Test 11: Access Logging for Failed Login"""
        print("\n=== Test 11: Access Logging for Failed Login ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/access-logs/admin")
            
            if response.status_code == 200:
                logs = response.json()
                
                # Look for our test project logs
                test_logs = [log for log in logs if log.get("projectId") == getattr(self, 'test_project_id', '')]
                failed_logs = [log for log in test_logs if log.get("status") == "failed"]
                
                if failed_logs:
                    latest_failed_log = failed_logs[0]  # Should be sorted by timestamp desc
                    required_fields = ["projectId", "timestamp", "ip", "status", "userAgent", "failureReason"]
                    
                    missing_fields = [field for field in required_fields if field not in latest_failed_log]
                    if not missing_fields:
                        self.log_result("access_logging", "Failed login logging", True, 
                                      f"Failed login logged: {latest_failed_log['failureReason']}")
                        return True
                    else:
                        self.log_result("access_logging", "Failed login logging", False, 
                                      f"Missing log fields: {missing_fields}")
                else:
                    self.log_result("access_logging", "Failed login logging", False, 
                                  "No failed login logs found for test project")
            else:
                self.log_result("access_logging", "Failed login logging", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("access_logging", "Failed login logging", False, str(e))
        
        return False
    
    def test_gc_dashboard_data_security(self):
        """Test 12: GC Dashboard Data Security (No Financial Data)"""
        print("\n=== Test 12: GC Dashboard Data Security ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("data_security", "Dashboard data security", False, "No test project available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{self.test_project_id}")
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Check that financial data is NOT present
                financial_fields = ["cost", "price", "rate", "profit", "revenue", "billing", "payment"]
                dashboard_str = json.dumps(dashboard_data).lower()
                
                financial_data_found = []
                for field in financial_fields:
                    if field in dashboard_str:
                        financial_data_found.append(field)
                
                # Check required non-financial fields ARE present
                required_fields = ["projectId", "projectName", "crewSummary", "materials", "tmTagSummary"]
                missing_required = [field for field in required_fields if field not in dashboard_data]
                
                if not financial_data_found and not missing_required:
                    self.log_result("data_security", "Dashboard data security", True, 
                                  "Dashboard contains no financial data and has required fields")
                    return True
                else:
                    issues = []
                    if financial_data_found:
                        issues.append(f"Financial data found: {financial_data_found}")
                    if missing_required:
                        issues.append(f"Missing required fields: {missing_required}")
                    
                    self.log_result("data_security", "Dashboard data security", False, 
                                  "; ".join(issues))
            else:
                self.log_result("data_security", "Dashboard data security", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("data_security", "Dashboard data security", False, str(e))
        
        return False
    
    def test_pin_uniqueness_across_projects(self):
        """Test 13: PIN Uniqueness Across All Projects"""
        print("\n=== Test 13: PIN Uniqueness Across All Projects ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                
                if len(projects) < 2:
                    # Create additional projects to test uniqueness
                    for i in range(3):
                        self.create_test_project(f"Uniqueness-{i}")
                    
                    # Re-fetch projects
                    response = self.session.get(f"{self.base_url}/projects")
                    if response.status_code == 200:
                        projects = response.json()
                
                # Collect all PINs
                pins = []
                for project in projects:
                    if project.get("gc_pin"):
                        pins.append(str(project["gc_pin"]))
                
                # Check for duplicates
                unique_pins = set(pins)
                
                if len(pins) == len(unique_pins) and len(pins) > 0:
                    self.log_result("pin_uniqueness", "PIN uniqueness verification", True, 
                                  f"All {len(pins)} PINs are unique")
                    return True
                else:
                    duplicates = len(pins) - len(unique_pins)
                    self.log_result("pin_uniqueness", "PIN uniqueness verification", False, 
                                  f"Found {duplicates} duplicate PINs out of {len(pins)} total")
            else:
                self.log_result("pin_uniqueness", "PIN uniqueness verification", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_uniqueness", "PIN uniqueness verification", False, str(e))
        
        return False
    
    def test_pin_collision_handling(self):
        """Test 14: PIN Collision Handling (Regeneration if Duplicate)"""
        print("\n=== Test 14: PIN Collision Handling ===")
        
        # This test is more theoretical since we can't easily force a collision
        # But we can verify the system handles it by creating many projects
        
        initial_project_count = len(self.created_projects)
        
        # Create multiple projects rapidly to increase chance of collision handling
        for i in range(5):
            project = self.create_test_project(f"Collision-{i}")
            if project:
                time.sleep(0.1)  # Small delay to avoid overwhelming the system
        
        final_project_count = len(self.created_projects)
        new_projects = final_project_count - initial_project_count
        
        if new_projects >= 3:  # At least some projects were created
            # Verify all new projects have unique PINs
            new_project_pins = []
            for project in self.created_projects[initial_project_count:]:
                if project.get("gc_pin"):
                    new_project_pins.append(str(project["gc_pin"]))
            
            unique_new_pins = set(new_project_pins)
            
            if len(new_project_pins) == len(unique_new_pins):
                self.log_result("pin_uniqueness", "PIN collision handling", True, 
                              f"Created {new_projects} projects with unique PINs")
                return True
            else:
                self.log_result("pin_uniqueness", "PIN collision handling", False, 
                              "Duplicate PINs found in newly created projects")
        else:
            self.log_result("pin_uniqueness", "PIN collision handling", False, 
                          "Could not create enough projects to test collision handling")
        
        return False
    
    def run_complete_workflow_test(self):
        """Test 15: Complete PIN Workflow End-to-End"""
        print("\n=== Test 15: Complete PIN Workflow End-to-End ===")
        
        # Create a fresh project for complete workflow test
        workflow_project = self.create_test_project("Workflow")
        
        if not workflow_project:
            self.log_result("general", "Complete workflow test", False, "Could not create workflow test project")
            return False
        
        project_id = workflow_project["id"]
        original_pin = workflow_project.get("gc_pin")
        
        if not original_pin:
            self.log_result("general", "Complete workflow test", False, "Project created without PIN")
            return False
        
        # Step 1: Use PIN to login
        login_data = {
            "projectId": project_id,
            "pin": original_pin,
            "ip": "192.168.1.200",
            "userAgent": "GC PIN Workflow Test"
        }
        
        try:
            login_response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code != 200:
                self.log_result("general", "Complete workflow test", False, 
                              f"Login failed: {login_response.status_code}")
                return False
            
            login_result = login_response.json()
            new_pin = login_result.get("newPin")
            
            # Step 2: Verify old PIN no longer works
            old_pin_login = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json={**login_data, "pin": original_pin},
                headers={"Content-Type": "application/json"}
            )
            
            if old_pin_login.status_code != 401:
                self.log_result("general", "Complete workflow test", False, 
                              "Old PIN still works after use")
                return False
            
            # Step 3: Verify new PIN works
            new_pin_login = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json={**login_data, "pin": new_pin},
                headers={"Content-Type": "application/json"}
            )
            
            if new_pin_login.status_code != 200:
                self.log_result("general", "Complete workflow test", False, 
                              "New PIN doesn't work")
                return False
            
            # Step 4: Access dashboard
            dashboard_response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
            
            if dashboard_response.status_code != 200:
                self.log_result("general", "Complete workflow test", False, 
                              "Dashboard access failed")
                return False
            
            self.log_result("general", "Complete workflow test", True, 
                          "Complete workflow successful: create → login → regenerate → verify → dashboard")
            return True
            
        except Exception as e:
            self.log_result("general", "Complete workflow test", False, str(e))
        
        return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("GC PIN SYSTEM TEST SUMMARY")
        print("="*80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            if passed + failed > 0:
                success_rate = (passed / (passed + failed)) * 100
                print(f"\n{category.upper().replace('_', ' ')}:")
                print(f"  ✅ Passed: {passed}")
                print(f"  ❌ Failed: {failed}")
                print(f"  📊 Success Rate: {success_rate:.1f}%")
                
                if results["errors"]:
                    print(f"  🔍 Errors:")
                    for error in results["errors"]:
                        print(f"    - {error}")
        
        overall_success_rate = (total_passed / (total_passed + total_failed)) * 100 if (total_passed + total_failed) > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS:")
        print(f"✅ Total Passed: {total_passed}")
        print(f"❌ Total Failed: {total_failed}")
        print(f"📊 Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"{'='*80}")
        
        # Determine overall status
        if overall_success_rate >= 90:
            print("🎉 GC PIN SYSTEM: EXCELLENT - Ready for production!")
        elif overall_success_rate >= 75:
            print("✅ GC PIN SYSTEM: GOOD - Minor issues to address")
        elif overall_success_rate >= 50:
            print("⚠️  GC PIN SYSTEM: NEEDS WORK - Several issues found")
        else:
            print("❌ GC PIN SYSTEM: CRITICAL ISSUES - Major problems detected")
        
        return overall_success_rate
    
    def run_all_tests(self):
        """Run all GC PIN system tests"""
        print("🚀 Starting Comprehensive GC PIN System Testing")
        print("="*80)
        
        # Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return False
        
        # Test 1-3: Automatic PIN Generation
        self.test_automatic_pin_generation_new_project()
        self.test_automatic_pin_generation_existing_projects()
        self.test_get_project_gc_pin_endpoint()
        
        # Test 4-7: GC Login Tests
        self.test_gc_login_valid_pin()
        self.test_gc_login_used_pin()
        self.test_gc_login_invalid_project()
        self.test_gc_login_wrong_pin()
        
        # Test 8-9: PIN Regeneration
        self.test_pin_regeneration_after_login()
        self.test_new_pin_works_for_next_login()
        
        # Test 10-11: Access Logging
        self.test_access_logging_successful_login()
        self.test_access_logging_failed_login()
        
        # Test 12: Data Security
        self.test_gc_dashboard_data_security()
        
        # Test 13-14: PIN Uniqueness
        self.test_pin_uniqueness_across_projects()
        self.test_pin_collision_handling()
        
        # Test 15: Complete Workflow
        self.run_complete_workflow_test()
        
        # Print summary
        success_rate = self.print_summary()
        
        return success_rate >= 75  # Consider 75%+ as passing

def main():
    """Main test execution"""
    tester = GCPinTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 GC PIN SYSTEM TESTING COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print("\n❌ GC PIN SYSTEM TESTING COMPLETED WITH ISSUES!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()