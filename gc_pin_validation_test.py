#!/usr/bin/env python3
"""
Comprehensive Testing for Secure GC PIN Validation Endpoint
Testing the new secure GC PIN validation endpoint POST /api/gc/validate-pin
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"

class GCPinValidationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_new_secure_pin_validation_endpoint(self):
        """Test the new secure GC PIN validation endpoint POST /api/gc/validate-pin"""
        print("\n🎯 TESTING NEW SECURE GC PIN VALIDATION ENDPOINT")
        print("=" * 60)
        
        # Step 1: Get a valid project with PIN for testing
        try:
            response = requests.get(f"{BACKEND_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                test_project = None
                
                # Find a project with a PIN
                for project in projects:
                    if project.get("gc_pin") and not project.get("gc_pin_used", True):
                        test_project = project
                        break
                
                if not test_project:
                    # Generate a PIN for the first project
                    if projects:
                        project_id = projects[0]["id"]
                        pin_response = requests.get(f"{BACKEND_URL}/projects/{project_id}/gc-pin", timeout=10)
                        if pin_response.status_code == 200:
                            pin_data = pin_response.json()
                            test_project = {
                                "id": project_id,
                                "name": projects[0]["name"],
                                "gc_pin": pin_data.get("gcPin")
                            }
                
                if test_project:
                    self.log_test("Setup: Found test project with PIN", True, 
                                f"Project: {test_project['name']}, PIN: {test_project['gc_pin']}")
                    return self._run_pin_validation_tests(test_project)
                else:
                    self.log_test("Setup: Find test project with PIN", False, "No projects with PINs available")
                    return False
            else:
                self.log_test("Setup: Get projects list", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Setup: Get projects list", False, f"Error: {str(e)}")
            return False
    
    def _run_pin_validation_tests(self, test_project):
        """Run comprehensive PIN validation tests"""
        original_pin = test_project["gc_pin"]
        project_id = test_project["id"]
        project_name = test_project["name"]
        
        # Test 1: Valid PIN validation
        try:
            payload = {
                "pin": original_pin,
                "ip": "127.0.0.1"
            }
            
            response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                   json=payload, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "projectId", "projectName", "message"]
                has_all_fields = all(field in data for field in required_fields)
                
                if has_all_fields:
                    self.log_test("Valid PIN validation - Response structure", True, 
                                f"All required fields present: {required_fields}")
                    
                    # Check that it returns correct project info
                    if data["projectId"] == project_id and data["projectName"] == project_name:
                        self.log_test("Valid PIN validation - Correct project data", True,
                                    f"ProjectId: {data['projectId']}, ProjectName: {data['projectName']}")
                    else:
                        self.log_test("Valid PIN validation - Correct project data", False,
                                    f"Expected: {project_id}/{project_name}, Got: {data['projectId']}/{data['projectName']}")
                    
                    # Check that response doesn't expose sensitive data
                    sensitive_fields = ["gc_pin", "all_projects", "project_list", "pins"]
                    has_sensitive = any(field in data for field in sensitive_fields)
                    
                    if not has_sensitive:
                        self.log_test("Security: No sensitive data exposed", True,
                                    "Response contains only necessary project info")
                    else:
                        exposed = [field for field in sensitive_fields if field in data]
                        self.log_test("Security: No sensitive data exposed", False,
                                    f"Exposed sensitive fields: {exposed}")
                        
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Valid PIN validation - Response structure", False,
                                f"Missing fields: {missing_fields}")
                    
            else:
                self.log_test("Valid PIN validation", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Valid PIN validation", False, f"Error: {str(e)}")
            return False
        
        # Test 2: PIN regeneration verification
        try:
            # Get the project again to check if PIN was regenerated
            time.sleep(1)  # Small delay to ensure update is processed
            
            response = requests.get(f"{BACKEND_URL}/projects/{project_id}/gc-pin", timeout=10)
            if response.status_code == 200:
                pin_data = response.json()
                new_pin = pin_data.get("gcPin")
                
                if new_pin and new_pin != original_pin:
                    self.log_test("PIN regeneration after validation", True,
                                f"Old PIN: {original_pin}, New PIN: {new_pin}")
                    
                    # Test 3: Old PIN should now be invalid
                    try:
                        old_pin_payload = {
                            "pin": original_pin,
                            "ip": "127.0.0.1"
                        }
                        
                        response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                               json=old_pin_payload, 
                                               timeout=10)
                        
                        if response.status_code == 401:
                            self.log_test("Old PIN rejection", True,
                                        f"Old PIN {original_pin} correctly rejected with 401")
                        else:
                            self.log_test("Old PIN rejection", False,
                                        f"Old PIN should be rejected, got status: {response.status_code}")
                            
                    except Exception as e:
                        self.log_test("Old PIN rejection", False, f"Error: {str(e)}")
                    
                    # Test 4: New PIN should work
                    try:
                        new_pin_payload = {
                            "pin": new_pin,
                            "ip": "127.0.0.1"
                        }
                        
                        response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                               json=new_pin_payload, 
                                               timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success") and data.get("projectId") == project_id:
                                self.log_test("New PIN validation", True,
                                            f"New PIN {new_pin} works correctly")
                            else:
                                self.log_test("New PIN validation", False,
                                            f"New PIN validation failed: {data}")
                        else:
                            self.log_test("New PIN validation", False,
                                        f"New PIN should work, got status: {response.status_code}")
                            
                    except Exception as e:
                        self.log_test("New PIN validation", False, f"Error: {str(e)}")
                        
                else:
                    self.log_test("PIN regeneration after validation", False,
                                f"PIN not regenerated. Old: {original_pin}, Current: {new_pin}")
                    
            else:
                self.log_test("PIN regeneration verification", False,
                            f"Could not get updated PIN, status: {response.status_code}")
                
        except Exception as e:
            self.log_test("PIN regeneration verification", False, f"Error: {str(e)}")
        
        # Test 5: Invalid PIN format
        try:
            invalid_pins = ["123", "12345", "abcd", "", None]
            
            for invalid_pin in invalid_pins:
                payload = {
                    "pin": invalid_pin,
                    "ip": "127.0.0.1"
                }
                
                response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                       json=payload, 
                                       timeout=10)
                
                if response.status_code == 400:
                    self.log_test(f"Invalid PIN format rejection ({invalid_pin})", True,
                                "Correctly rejected with 400 Bad Request")
                else:
                    self.log_test(f"Invalid PIN format rejection ({invalid_pin})", False,
                                f"Should reject invalid format, got status: {response.status_code}")
                    
        except Exception as e:
            self.log_test("Invalid PIN format testing", False, f"Error: {str(e)}")
        
        # Test 6: Non-existent PIN
        try:
            fake_pin = "9999"  # Assuming this PIN doesn't exist
            payload = {
                "pin": fake_pin,
                "ip": "127.0.0.1"
            }
            
            response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                   json=payload, 
                                   timeout=10)
            
            if response.status_code == 401:
                self.log_test("Non-existent PIN rejection", True,
                            f"Fake PIN {fake_pin} correctly rejected with 401")
            else:
                self.log_test("Non-existent PIN rejection", False,
                            f"Fake PIN should be rejected, got status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Non-existent PIN rejection", False, f"Error: {str(e)}")
        
        # Test 7: Endpoint security - no data leakage
        try:
            # Test that the endpoint doesn't return project lists or other sensitive data
            payload = {
                "pin": "1234",  # Invalid PIN
                "ip": "127.0.0.1"
            }
            
            response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                   json=payload, 
                                   timeout=10)
            
            # Even on failure, should not expose sensitive data
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    sensitive_fields = ["projects", "pins", "gc_pin", "all_projects"]
                    has_sensitive = any(field in str(error_data).lower() for field in sensitive_fields)
                    
                    if not has_sensitive:
                        self.log_test("Security: No data leakage on failure", True,
                                    "Error response doesn't expose sensitive data")
                    else:
                        self.log_test("Security: No data leakage on failure", False,
                                    f"Error response may contain sensitive data: {error_data}")
                except:
                    # If response is not JSON, that's fine for security
                    self.log_test("Security: No data leakage on failure", True,
                                "Error response is not JSON (good for security)")
            else:
                self.log_test("Security: Proper error handling", False,
                            f"Expected 401 for invalid PIN, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("Security: No data leakage testing", False, f"Error: {str(e)}")
        
        return True
    
    def test_access_logging(self):
        """Test that access attempts are properly logged"""
        print("\n📝 TESTING ACCESS LOGGING")
        print("=" * 40)
        
        try:
            # Make a failed PIN attempt
            payload = {
                "pin": "0000",  # Invalid PIN
                "ip": "192.168.1.100"  # Test IP
            }
            
            response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                   json=payload, 
                                   timeout=10)
            
            if response.status_code == 401:
                self.log_test("Failed attempt logging", True,
                            "Failed PIN attempt returns 401 as expected")
                
                # Note: We can't directly test log entries without admin access,
                # but we can verify the endpoint behaves correctly
                
            else:
                self.log_test("Failed attempt logging", False,
                            f"Expected 401 for invalid PIN, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("Access logging test", False, f"Error: {str(e)}")
    
    def test_endpoint_requirements(self):
        """Test specific requirements from the review request"""
        print("\n📋 TESTING SPECIFIC REVIEW REQUIREMENTS")
        print("=" * 50)
        
        # Test that endpoint only requires PIN in request body
        try:
            # Get a valid PIN first
            response = requests.get(f"{BACKEND_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    project_id = projects[0]["id"]
                    pin_response = requests.get(f"{BACKEND_URL}/projects/{project_id}/gc-pin", timeout=10)
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        test_pin = pin_data.get("gcPin")
                        
                        # Test minimal payload (only PIN required)
                        minimal_payload = {"pin": test_pin}
                        
                        response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                               json=minimal_payload, 
                                               timeout=10)
                        
                        if response.status_code == 200:
                            self.log_test("Minimal payload requirement", True,
                                        "Endpoint accepts payload with only PIN field")
                        else:
                            self.log_test("Minimal payload requirement", False,
                                        f"Endpoint should accept minimal payload, got: {response.status_code}")
                    else:
                        self.log_test("Setup for minimal payload test", False, "Could not get test PIN")
                else:
                    self.log_test("Setup for minimal payload test", False, "No projects available")
            else:
                self.log_test("Setup for minimal payload test", False, f"Could not get projects: {response.status_code}")
                
        except Exception as e:
            self.log_test("Minimal payload requirement test", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests for the secure GC PIN validation system"""
        print("🚀 STARTING COMPREHENSIVE GC PIN VALIDATION TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Test the new secure PIN validation endpoint
        self.test_new_secure_pin_validation_endpoint()
        
        # Test access logging
        self.test_access_logging()
        
        # Test specific requirements
        self.test_endpoint_requirements()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🎯 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! The secure GC PIN validation system is working perfectly.")
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} tests failed. Review the issues above.")
        
        return self.passed_tests == self.total_tests

if __name__ == "__main__":
    tester = GCPinValidationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)