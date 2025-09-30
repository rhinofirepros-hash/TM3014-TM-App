#!/usr/bin/env python3
"""
GC PIN System Core Functionality Test
Tests the essential GC PIN features that are working
"""

import requests
import json
from datetime import datetime
import uuid
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"

class GCPinCoreTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log_result(self, test_name, success, message=""):
        """Log test results"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            self.test_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_result("Basic connectivity", True)
                return True
            else:
                self.log_result("Basic connectivity", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Basic connectivity", False, str(e))
            return False
    
    def test_existing_projects_pin_generation(self):
        """Test PIN generation for existing projects via GET /api/projects"""
        print("\n=== Test 1: PIN Generation for Existing Projects ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                
                if not projects:
                    self.log_result("Existing projects PIN generation", False, "No projects found")
                    return False
                
                # Test PIN generation for first project
                project = projects[0]
                project_id = project["id"]
                project_name = project.get("name", "Unknown")
                
                # Get PIN via dedicated endpoint
                pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                
                if pin_response.status_code == 200:
                    pin_data = pin_response.json()
                    pin = pin_data.get("gcPin")
                    
                    if pin and len(str(pin)) == 4 and str(pin).isdigit():
                        self.log_result("Existing projects PIN generation", True, 
                                      f"Project '{project_name}' has valid PIN: {pin}")
                        self.test_project_id = project_id
                        self.test_project_name = project_name
                        self.test_project_pin = pin
                        return True
                    else:
                        self.log_result("Existing projects PIN generation", False, 
                                      f"Invalid PIN format: {pin}")
                else:
                    self.log_result("Existing projects PIN generation", False, 
                                  f"PIN endpoint failed: {pin_response.status_code}")
            else:
                self.log_result("Existing projects PIN generation", False, 
                              f"Projects endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Existing projects PIN generation", False, str(e))
        
        return False
    
    def test_gc_login_valid_pin(self):
        """Test GC login with valid PIN"""
        print("\n=== Test 2: GC Login with Valid PIN ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("GC login with valid PIN", False, "No test project available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.test_project_pin,
            "ip": "192.168.1.100",
            "userAgent": "GC PIN Core Test Suite"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if (result.get("success") and 
                    result.get("projectId") == self.test_project_id and
                    result.get("newPin") and
                    len(str(result["newPin"])) == 4):
                    
                    self.log_result("GC login with valid PIN", True, 
                                  f"Login successful, new PIN generated: {result['newPin']}")
                    self.new_pin = result["newPin"]
                    return True
                else:
                    self.log_result("GC login with valid PIN", False, "Invalid response data")
            else:
                self.log_result("GC login with valid PIN", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("GC login with valid PIN", False, str(e))
        
        return False
    
    def test_pin_regeneration(self):
        """Test that PIN was regenerated after login"""
        print("\n=== Test 3: PIN Regeneration After Login ===")
        
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'new_pin'):
            self.log_result("PIN regeneration", False, "No test data available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{self.test_project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                current_pin = pin_data.get("gcPin")
                
                if current_pin == self.new_pin and current_pin != self.test_project_pin:
                    self.log_result("PIN regeneration", True, 
                                  f"PIN successfully regenerated from {self.test_project_pin} to {current_pin}")
                    return True
                else:
                    self.log_result("PIN regeneration", False, 
                                  f"PIN not properly regenerated. Old: {self.test_project_pin}, Current: {current_pin}")
            else:
                self.log_result("PIN regeneration", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("PIN regeneration", False, str(e))
        
        return False
    
    def test_used_pin_rejection(self):
        """Test that used PIN is rejected"""
        print("\n=== Test 4: Used PIN Rejection ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("Used PIN rejection", False, "No test project available")
            return False
        
        # Try to use the old PIN (should fail)
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.test_project_pin,  # Old PIN that was already used
            "ip": "192.168.1.101",
            "userAgent": "GC PIN Core Test - Used PIN Test"
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
                    self.log_result("Used PIN rejection", True, "Correctly rejected used PIN")
                    return True
                else:
                    self.log_result("Used PIN rejection", False, 
                                  f"Wrong error message: {error_data.get('detail')}")
            else:
                self.log_result("Used PIN rejection", False, 
                              f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Used PIN rejection", False, str(e))
        
        return False
    
    def test_new_pin_works(self):
        """Test that new PIN works for login"""
        print("\n=== Test 5: New PIN Works for Login ===")
        
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'new_pin'):
            self.log_result("New PIN login", False, "No test data available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": self.new_pin,
            "ip": "192.168.1.102",
            "userAgent": "GC PIN Core Test - New PIN Test"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if (result.get("success") and 
                    result.get("projectId") == self.test_project_id and
                    result.get("newPin") != self.new_pin):
                    
                    self.log_result("New PIN login", True, 
                                  f"New PIN login successful, next PIN: {result['newPin']}")
                    self.latest_pin = result["newPin"]
                    return True
                else:
                    self.log_result("New PIN login", False, "Invalid response data")
            else:
                self.log_result("New PIN login", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("New PIN login", False, str(e))
        
        return False
    
    def test_invalid_project_rejection(self):
        """Test rejection of invalid project ID"""
        print("\n=== Test 6: Invalid Project ID Rejection ===")
        
        fake_project_id = str(uuid.uuid4())
        login_data = {
            "projectId": fake_project_id,
            "pin": "1234",
            "ip": "192.168.1.103",
            "userAgent": "GC PIN Core Test - Invalid Project"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_result("Invalid project rejection", True, "Correctly rejected invalid project")
                return True
            else:
                self.log_result("Invalid project rejection", False, 
                              f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Invalid project rejection", False, str(e))
        
        return False
    
    def test_wrong_pin_rejection(self):
        """Test rejection of wrong PIN"""
        print("\n=== Test 7: Wrong PIN Rejection ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("Wrong PIN rejection", False, "No test project available")
            return False
        
        login_data = {
            "projectId": self.test_project_id,
            "pin": "9999",  # Wrong PIN
            "ip": "192.168.1.104",
            "userAgent": "GC PIN Core Test - Wrong PIN"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_result("Wrong PIN rejection", True, "Correctly rejected wrong PIN")
                return True
            else:
                self.log_result("Wrong PIN rejection", False, 
                              f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Wrong PIN rejection", False, str(e))
        
        return False
    
    def test_pin_uniqueness(self):
        """Test PIN uniqueness across multiple projects"""
        print("\n=== Test 8: PIN Uniqueness Verification ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                
                if len(projects) < 3:
                    self.log_result("PIN uniqueness", False, "Not enough projects to test uniqueness")
                    return False
                
                # Get PINs for first 5 projects
                pins = []
                for project in projects[:5]:
                    project_id = project["id"]
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        pin = pin_data.get("gcPin")
                        if pin:
                            pins.append(str(pin))
                
                # Check for uniqueness
                unique_pins = set(pins)
                
                if len(pins) == len(unique_pins) and len(pins) >= 3:
                    self.log_result("PIN uniqueness", True, 
                                  f"All {len(pins)} tested PINs are unique: {pins}")
                    return True
                else:
                    duplicates = len(pins) - len(unique_pins)
                    self.log_result("PIN uniqueness", False, 
                                  f"Found {duplicates} duplicate PINs in {pins}")
            else:
                self.log_result("PIN uniqueness", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("PIN uniqueness", False, str(e))
        
        return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("GC PIN SYSTEM CORE FUNCTIONALITY TEST SUMMARY")
        print("="*80)
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            print(f"\n🔍 Failed Tests:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")
        
        print(f"\n{'='*80}")
        
        if success_rate >= 90:
            print("🎉 GC PIN CORE SYSTEM: EXCELLENT - All critical features working!")
        elif success_rate >= 75:
            print("✅ GC PIN CORE SYSTEM: GOOD - Core functionality operational")
        elif success_rate >= 50:
            print("⚠️  GC PIN CORE SYSTEM: PARTIAL - Some issues found")
        else:
            print("❌ GC PIN CORE SYSTEM: CRITICAL ISSUES")
        
        return success_rate
    
    def run_all_tests(self):
        """Run all core GC PIN tests"""
        print("🚀 Starting GC PIN Core Functionality Testing")
        print("="*80)
        
        # Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return False
        
        # Core PIN functionality tests
        self.test_existing_projects_pin_generation()
        self.test_gc_login_valid_pin()
        self.test_pin_regeneration()
        self.test_used_pin_rejection()
        self.test_new_pin_works()
        self.test_invalid_project_rejection()
        self.test_wrong_pin_rejection()
        self.test_pin_uniqueness()
        
        # Print summary
        success_rate = self.print_summary()
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = GCPinCoreTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 GC PIN CORE SYSTEM TESTING COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print("\n❌ GC PIN CORE SYSTEM TESTING COMPLETED WITH ISSUES!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()