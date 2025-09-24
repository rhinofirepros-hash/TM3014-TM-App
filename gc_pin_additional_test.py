#!/usr/bin/env python3
"""
Additional GC PIN System Testing
Test with multiple projects to ensure consistency
"""

import requests
import json
from datetime import datetime
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://rhino-ui-sync.preview.emergentagent.com/api"

class GCPinAdditionalTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message
        }
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code})"
            print(f"❌ {error_msg}")
    
    def test_multiple_projects_pin_workflow(self):
        """Test PIN workflow with multiple projects"""
        print("\n=== Testing Multiple Projects PIN Workflow ===")
        
        try:
            # Get all projects
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code != 200:
                self.log_result("Get projects list", False, f"HTTP {response.status_code}", response)
                return False
            
            projects = response.json()
            if len(projects) < 2:
                self.log_result("Multiple projects test", False, "Need at least 2 projects for testing")
                return False
            
            # Test first 3 projects (or all if less than 3)
            test_projects = projects[:min(3, len(projects))]
            successful_tests = 0
            
            for i, project in enumerate(test_projects):
                project_id = project.get("id")
                project_name = project.get("name", f"Project {i+1}")
                
                print(f"\n--- Testing Project {i+1}: {project_name} ---")
                
                # Step 1: Generate PIN
                pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                if pin_response.status_code != 200:
                    self.log_result(f"Project {i+1} PIN generation", False, f"HTTP {pin_response.status_code}")
                    continue
                
                pin_data = pin_response.json()
                pin = str(pin_data.get("gcPin", ""))
                
                if len(pin) != 4 or not pin.isdigit():
                    self.log_result(f"Project {i+1} PIN format", False, f"Invalid PIN: {pin}")
                    continue
                
                self.log_result(f"Project {i+1} PIN generation", True, f"Generated PIN: {pin}")
                
                # Step 2: Test login
                login_data = {
                    "projectId": project_id,
                    "pin": pin
                }
                
                login_response = self.session.post(
                    f"{self.base_url}/gc/login-simple",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code != 200:
                    self.log_result(f"Project {i+1} login", False, f"HTTP {login_response.status_code}")
                    continue
                
                login_result = login_response.json()
                if not login_result.get("success"):
                    self.log_result(f"Project {i+1} login", False, "Login not successful")
                    continue
                
                new_pin = str(login_result.get("newPin", ""))
                self.log_result(f"Project {i+1} login", True, f"Login successful, new PIN: {new_pin}")
                
                # Step 3: Test dashboard access
                dashboard_response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    if "projectId" in dashboard_data and "projectName" in dashboard_data:
                        self.log_result(f"Project {i+1} dashboard", True, "Dashboard accessible")
                        successful_tests += 1
                    else:
                        self.log_result(f"Project {i+1} dashboard", False, "Invalid dashboard data")
                else:
                    self.log_result(f"Project {i+1} dashboard", False, f"HTTP {dashboard_response.status_code}")
            
            # Overall assessment
            if successful_tests == len(test_projects):
                self.log_result("Multiple projects workflow", True, f"All {successful_tests} projects tested successfully")
                return True
            else:
                self.log_result("Multiple projects workflow", False, f"Only {successful_tests}/{len(test_projects)} projects successful")
                return False
                
        except Exception as e:
            self.log_result("Multiple projects workflow", False, str(e))
            return False
    
    def test_pin_uniqueness(self):
        """Test that all projects have unique PINs"""
        print("\n=== Testing PIN Uniqueness Across Projects ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code != 200:
                self.log_result("PIN uniqueness test", False, f"HTTP {response.status_code}", response)
                return False
            
            projects = response.json()
            pins = []
            
            for project in projects:
                pin = project.get("gc_pin")
                if pin:
                    pins.append(str(pin))
            
            unique_pins = set(pins)
            
            if len(pins) == len(unique_pins):
                self.log_result("PIN uniqueness test", True, f"All {len(pins)} PINs are unique")
                return True
            else:
                duplicates = len(pins) - len(unique_pins)
                self.log_result("PIN uniqueness test", False, f"Found {duplicates} duplicate PINs")
                return False
                
        except Exception as e:
            self.log_result("PIN uniqueness test", False, str(e))
            return False
    
    def test_used_pin_rejection(self):
        """Test that used PINs are properly rejected"""
        print("\n=== Testing Used PIN Rejection ===")
        
        try:
            # Get a project
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code != 200:
                self.log_result("Used PIN test setup", False, f"HTTP {response.status_code}", response)
                return False
            
            projects = response.json()
            if not projects:
                self.log_result("Used PIN test setup", False, "No projects available")
                return False
            
            project = projects[0]
            project_id = project.get("id")
            
            # Get current PIN
            pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            if pin_response.status_code != 200:
                self.log_result("Used PIN test - get PIN", False, f"HTTP {pin_response.status_code}")
                return False
            
            pin_data = pin_response.json()
            current_pin = str(pin_data.get("gcPin", ""))
            
            # Use the PIN (this should work)
            login_data = {
                "projectId": project_id,
                "pin": current_pin
            }
            
            first_login = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if first_login.status_code != 200:
                self.log_result("Used PIN test - first login", False, f"HTTP {first_login.status_code}")
                return False
            
            self.log_result("Used PIN test - first login", True, "First login successful")
            
            # Try to use the same PIN again (this should fail)
            second_login = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if second_login.status_code == 401:
                error_data = second_login.json()
                if "Invalid PIN or PIN already used" in error_data.get("detail", ""):
                    self.log_result("Used PIN test - second login rejection", True, "Used PIN correctly rejected")
                    return True
                else:
                    self.log_result("Used PIN test - second login rejection", False, f"Wrong error message: {error_data.get('detail')}")
                    return False
            else:
                self.log_result("Used PIN test - second login rejection", False, f"Expected 401, got {second_login.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Used PIN test", False, str(e))
            return False
    
    def run_additional_tests(self):
        """Run additional comprehensive tests"""
        print("🔍 STARTING ADDITIONAL GC PIN SYSTEM TESTING")
        print("=" * 60)
        
        self.test_multiple_projects_pin_workflow()
        self.test_pin_uniqueness()
        self.test_used_pin_rejection()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🔍 ADDITIONAL GC PIN SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"\n📊 RESULTS:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📈 Success Rate: {(passed / len(self.test_results) * 100):.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  {i}. {result['test']}: {status}")
            if result["message"]:
                print(f"     {result['message']}")
        
        return failed == 0

def main():
    """Main test execution"""
    tester = GCPinAdditionalTester()
    
    try:
        tester.run_additional_tests()
        success = tester.print_summary()
        
        if success:
            print("\n🎉 ADDITIONAL GC PIN SYSTEM TESTING COMPLETED SUCCESSFULLY!")
            return 0
        else:
            print("\n❌ ADDITIONAL GC PIN SYSTEM TESTING FOUND ISSUES!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)