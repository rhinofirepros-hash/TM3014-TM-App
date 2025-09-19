#!/usr/bin/env python3
"""
GC PIN System Debug Test
Specifically testing the issues reported in the review request:
1. Test GC login with PIN 5249 for project "68cc802f8d44fcd8015b39b8"
2. Debug the GC login query to understand what it's searching for
3. Test PIN generation for project "68cc802f8d44fcd8015b39b8"
4. Check project data consistency
"""

import requests
import json
from datetime import datetime
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://fireprotect-app.preview.emergentagent.com/api"

class GCPinDebugTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "gc_pin_tests": {"passed": 0, "failed": 0, "errors": []},
            "project_tests": {"passed": 0, "failed": 0, "errors": []},
            "login_tests": {"passed": 0, "failed": 0, "errors": []}
        }
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:500]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_specific_project_existence(self):
        """Test if the specific project 68cc802f8d44fcd8015b39b8 exists"""
        print("\n=== Testing Specific Project Existence ===")
        project_id = "68cc802f8d44fcd8015b39b8"
        
        try:
            # Test 1: Check if project exists in projects list
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                target_project = None
                for project in projects:
                    if project.get("id") == project_id:
                        target_project = project
                        break
                
                if target_project:
                    self.log_result("project_tests", "Project exists in list", True, 
                                  f"Found project: {target_project.get('name', 'Unknown')} with ID {project_id}")
                    print(f"   Project details: {json.dumps(target_project, indent=2)}")
                    return target_project
                else:
                    self.log_result("project_tests", "Project exists in list", False, 
                                  f"Project {project_id} not found in projects list")
            else:
                self.log_result("project_tests", "Project exists in list", False, 
                              f"Could not retrieve projects list", response)
            
            # Test 2: Try to get project directly by ID
            response = self.session.get(f"{self.base_url}/projects/{project_id}")
            if response.status_code == 200:
                project = response.json()
                self.log_result("project_tests", "Project exists by ID", True, 
                              f"Found project: {project.get('name', 'Unknown')}")
                print(f"   Direct project details: {json.dumps(project, indent=2)}")
                return project
            else:
                self.log_result("project_tests", "Project exists by ID", False, 
                              f"Project {project_id} not found by direct ID lookup", response)
                
        except Exception as e:
            self.log_result("project_tests", "Project existence check", False, str(e))
        
        return None
    
    def test_pin_generation_for_specific_project(self):
        """Test PIN generation for the specific project"""
        print("\n=== Testing PIN Generation for Specific Project ===")
        project_id = "68cc802f8d44fcd8015b39b8"
        
        try:
            # Test the PIN generation endpoint
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                self.log_result("gc_pin_tests", "PIN generation endpoint", True, 
                              f"PIN endpoint returned: {json.dumps(pin_data, indent=2)}")
                
                # Check if PIN is present and valid
                if "gcPin" in pin_data or "gc_pin" in pin_data:
                    pin = pin_data.get("gcPin") or pin_data.get("gc_pin")
                    if pin and len(str(pin)) == 4:
                        self.log_result("gc_pin_tests", "PIN format validation", True, 
                                      f"Valid 4-digit PIN: {pin}")
                        return pin_data
                    else:
                        self.log_result("gc_pin_tests", "PIN format validation", False, 
                                      f"Invalid PIN format: {pin}")
                else:
                    self.log_result("gc_pin_tests", "PIN presence check", False, 
                                  "No PIN field found in response")
            else:
                self.log_result("gc_pin_tests", "PIN generation endpoint", False, 
                              f"PIN generation failed", response)
                
        except Exception as e:
            self.log_result("gc_pin_tests", "PIN generation test", False, str(e))
        
        return None
    
    def test_gc_login_with_specific_pin(self):
        """Test GC login with the specific PIN 5249 mentioned in the review"""
        print("\n=== Testing GC Login with PIN 5249 ===")
        project_id = "68cc802f8d44fcd8015b39b8"
        pin = "5249"
        
        try:
            # Test the GC login endpoint
            login_data = {
                "projectId": project_id,
                "pin": pin
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Login attempt with PIN {pin} for project {project_id}")
            print(f"   Response status: {response.status_code}")
            print(f"   Response body: {response.text}")
            
            if response.status_code == 200:
                login_result = response.json()
                self.log_result("login_tests", "GC login with PIN 5249", True, 
                              f"Login successful: {json.dumps(login_result, indent=2)}")
                return login_result
            elif response.status_code == 401:
                error_data = response.json() if response.text else {}
                self.log_result("login_tests", "GC login with PIN 5249", False, 
                              f"Login failed with 401: {error_data.get('detail', 'Unknown error')}")
            else:
                self.log_result("login_tests", "GC login with PIN 5249", False, 
                              f"Unexpected status code", response)
                
        except Exception as e:
            self.log_result("login_tests", "GC login with PIN 5249", False, str(e))
        
        return None
    
    def test_all_project_pins(self):
        """Get all projects and their current PINs to understand the system state"""
        print("\n=== Testing All Project PINs ===")
        
        try:
            # Get all projects
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code != 200:
                self.log_result("project_tests", "Get all projects", False, 
                              "Could not retrieve projects", response)
                return
            
            projects = response.json()
            self.log_result("project_tests", "Get all projects", True, 
                          f"Retrieved {len(projects)} projects")
            
            print(f"\n   === PROJECT PIN SUMMARY ===")
            pin_project_map = {}
            
            for project in projects:
                project_id = project.get("id")
                project_name = project.get("name", "Unknown")
                
                # Try to get PIN for each project
                try:
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        pin = pin_data.get("gcPin") or pin_data.get("gc_pin")
                        pin_used = pin_data.get("pinUsed") or pin_data.get("gc_pin_used", False)
                        
                        print(f"   Project: {project_name[:30]:<30} | ID: {project_id} | PIN: {pin} | Used: {pin_used}")
                        
                        if pin:
                            pin_project_map[pin] = {
                                "project_id": project_id,
                                "project_name": project_name,
                                "pin_used": pin_used
                            }
                    else:
                        print(f"   Project: {project_name[:30]:<30} | ID: {project_id} | PIN: ERROR ({pin_response.status_code})")
                        
                except Exception as e:
                    print(f"   Project: {project_name[:30]:<30} | ID: {project_id} | PIN: EXCEPTION ({str(e)})")
            
            # Check if PIN 5249 exists
            if "5249" in pin_project_map:
                pin_info = pin_project_map["5249"]
                self.log_result("gc_pin_tests", "PIN 5249 exists", True, 
                              f"PIN 5249 belongs to project: {pin_info['project_name']} ({pin_info['project_id']})")
                
                # Test login with this PIN
                if pin_info["project_id"] == "68cc802f8d44fcd8015b39b8":
                    self.log_result("gc_pin_tests", "PIN 5249 project match", True, 
                                  "PIN 5249 correctly belongs to the target project")
                else:
                    self.log_result("gc_pin_tests", "PIN 5249 project match", False, 
                                  f"PIN 5249 belongs to different project: {pin_info['project_id']}")
            else:
                self.log_result("gc_pin_tests", "PIN 5249 exists", False, 
                              "PIN 5249 not found in any project")
            
            return pin_project_map
            
        except Exception as e:
            self.log_result("project_tests", "All project PINs test", False, str(e))
        
        return {}
    
    def test_gc_login_debug(self):
        """Debug the GC login process to understand what's happening"""
        print("\n=== Debugging GC Login Process ===")
        
        # First, get the current PIN for the target project
        project_id = "68cc802f8d44fcd8015b39b8"
        
        try:
            # Get current PIN
            pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            if pin_response.status_code == 200:
                pin_data = pin_response.json()
                current_pin = pin_data.get("gcPin") or pin_data.get("gc_pin")
                pin_used = pin_data.get("pinUsed") or pin_data.get("gc_pin_used", False)
                
                print(f"   Current PIN for project {project_id}: {current_pin}")
                print(f"   PIN used status: {pin_used}")
                
                if current_pin:
                    # Test login with current PIN
                    login_data = {
                        "projectId": project_id,
                        "pin": current_pin
                    }
                    
                    login_response = self.session.post(
                        f"{self.base_url}/gc/login-simple",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"   Login test with current PIN {current_pin}:")
                    print(f"   Status: {login_response.status_code}")
                    print(f"   Response: {login_response.text}")
                    
                    if login_response.status_code == 200:
                        self.log_result("login_tests", "Login with current PIN", True, 
                                      f"Successfully logged in with PIN {current_pin}")
                        
                        # Check if PIN was regenerated
                        new_pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                        if new_pin_response.status_code == 200:
                            new_pin_data = new_pin_response.json()
                            new_pin = new_pin_data.get("gcPin") or new_pin_data.get("gc_pin")
                            print(f"   PIN after login: {new_pin}")
                            
                            if new_pin != current_pin:
                                self.log_result("gc_pin_tests", "PIN regeneration", True, 
                                              f"PIN regenerated from {current_pin} to {new_pin}")
                            else:
                                self.log_result("gc_pin_tests", "PIN regeneration", False, 
                                              "PIN was not regenerated after login")
                    else:
                        self.log_result("login_tests", "Login with current PIN", False, 
                                      f"Login failed with current PIN {current_pin}", login_response)
                else:
                    self.log_result("gc_pin_tests", "Current PIN retrieval", False, 
                                  "No current PIN found for project")
            else:
                self.log_result("gc_pin_tests", "Current PIN retrieval", False, 
                              "Could not retrieve current PIN", pin_response)
                
        except Exception as e:
            self.log_result("login_tests", "GC login debug", False, str(e))
    
    def test_database_consistency(self):
        """Check database consistency for the specific project"""
        print("\n=== Testing Database Consistency ===")
        project_id = "68cc802f8d44fcd8015b39b8"
        
        try:
            # Test 1: Get project data
            project_response = self.session.get(f"{self.base_url}/projects/{project_id}")
            if project_response.status_code == 200:
                project_data = project_response.json()
                self.log_result("project_tests", "Project data retrieval", True, 
                              f"Project data retrieved successfully")
                
                # Check for GC PIN fields in project data
                has_gc_pin = "gc_pin" in project_data
                has_gc_pin_used = "gc_pin_used" in project_data
                
                print(f"   Project has gc_pin field: {has_gc_pin}")
                print(f"   Project has gc_pin_used field: {has_gc_pin_used}")
                
                if has_gc_pin:
                    print(f"   gc_pin value: {project_data.get('gc_pin')}")
                if has_gc_pin_used:
                    print(f"   gc_pin_used value: {project_data.get('gc_pin_used')}")
                
                self.log_result("project_tests", "GC PIN fields in project", 
                              has_gc_pin and has_gc_pin_used, 
                              f"gc_pin: {has_gc_pin}, gc_pin_used: {has_gc_pin_used}")
            else:
                self.log_result("project_tests", "Project data retrieval", False, 
                              "Could not retrieve project data", project_response)
            
            # Test 2: Compare PIN endpoint vs project data
            pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            if pin_response.status_code == 200 and project_response.status_code == 200:
                pin_data = pin_response.json()
                project_data = project_response.json()
                
                pin_endpoint_pin = pin_data.get("gcPin") or pin_data.get("gc_pin")
                project_data_pin = project_data.get("gc_pin")
                
                if pin_endpoint_pin == project_data_pin:
                    self.log_result("project_tests", "PIN data consistency", True, 
                                  f"PIN consistent across endpoints: {pin_endpoint_pin}")
                else:
                    self.log_result("project_tests", "PIN data consistency", False, 
                                  f"PIN mismatch - endpoint: {pin_endpoint_pin}, project: {project_data_pin}")
                
        except Exception as e:
            self.log_result("project_tests", "Database consistency check", False, str(e))
    
    def run_comprehensive_debug(self):
        """Run all debug tests"""
        print("🔍 Starting GC PIN System Debug Tests")
        print("=" * 60)
        
        # Test 1: Check if the specific project exists
        project = self.test_specific_project_existence()
        
        # Test 2: Test PIN generation for the specific project
        pin_data = self.test_pin_generation_for_specific_project()
        
        # Test 3: Test login with the specific PIN mentioned in the review
        self.test_gc_login_with_specific_pin()
        
        # Test 4: Get all project PINs to understand the system state
        pin_map = self.test_all_project_pins()
        
        # Test 5: Debug the login process
        self.test_gc_login_debug()
        
        # Test 6: Check database consistency
        self.test_database_consistency()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 GC PIN DEBUG TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            if results["errors"]:
                print(f"  🔍 Errors:")
                for error in results["errors"]:
                    print(f"    - {error}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📈 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%" if (total_passed + total_failed) > 0 else "N/A")
        
        if total_failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! GC PIN system is working correctly.")
        else:
            print(f"\n⚠️  ISSUES FOUND: {total_failed} test(s) failed. Review the errors above.")

if __name__ == "__main__":
    tester = GCPinDebugTester()
    tester.run_comprehensive_debug()