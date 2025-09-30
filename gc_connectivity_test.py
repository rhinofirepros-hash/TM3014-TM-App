#!/usr/bin/env python3
"""
GC Login Connectivity and CORS Testing
Tests backend connectivity and CORS for the GC login functionality
"""

import requests
import json
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"
FRONTEND_URL = "https://project-autopilot.preview.emergentagent.com"

class GCConnectivityTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.frontend_url = FRONTEND_URL
        self.session = requests.Session()
        self.test_results = {
            "projects": {"passed": 0, "failed": 0, "errors": []},
            "cors": {"passed": 0, "failed": 0, "errors": []},
            "gc_login": {"passed": 0, "failed": 0, "errors": []},
            "connectivity": {"passed": 0, "failed": 0, "errors": []}
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
                error_msg += f" (Status: {response.status_code})"
                if hasattr(response, 'text'):
                    error_msg += f" Response: {response.text[:300]}"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Backend Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects", timeout=10)
            if response.status_code == 200:
                self.log_result("connectivity", "Basic backend connectivity", True, f"Backend responding at {self.base_url}")
                return True
            else:
                self.log_result("connectivity", "Basic backend connectivity", False, f"Backend returned status {response.status_code}", response)
                return False
        except requests.exceptions.ConnectionError as e:
            self.log_result("connectivity", "Basic backend connectivity", False, f"Connection error: {str(e)}")
            return False
        except requests.exceptions.Timeout as e:
            self.log_result("connectivity", "Basic backend connectivity", False, f"Timeout error: {str(e)}")
            return False
        except Exception as e:
            self.log_result("connectivity", "Basic backend connectivity", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_projects_endpoint_with_gc_pins(self):
        """Test Projects Endpoint - Verify returns project data with gc_pin fields"""
        print("\n=== Testing Projects Endpoint with GC PIN Fields ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects", timeout=10)
            
            if response.status_code == 200:
                projects = response.json()
                
                if isinstance(projects, list):
                    self.log_result("projects", "Projects endpoint response format", True, f"Retrieved {len(projects)} projects")
                    
                    if len(projects) > 0:
                        # Check if projects have gc_pin fields
                        projects_with_pins = 0
                        sample_project = None
                        
                        for project in projects:
                            if "gc_pin" in project and project["gc_pin"]:
                                projects_with_pins += 1
                                if not sample_project:
                                    sample_project = project
                        
                        if projects_with_pins > 0:
                            self.log_result("projects", "GC PIN fields present", True, 
                                          f"{projects_with_pins}/{len(projects)} projects have GC PINs")
                            
                            # Verify PIN format (should be 4-digit string)
                            if sample_project and len(str(sample_project["gc_pin"])) == 4:
                                self.log_result("projects", "GC PIN format validation", True, 
                                              f"Sample PIN: {sample_project['gc_pin']} (4-digit format)")
                                
                                # Store a valid project ID and PIN for login testing
                                self.test_project_id = sample_project.get("id")
                                self.test_project_pin = sample_project.get("gc_pin")
                                self.test_project_name = sample_project.get("name", "Unknown Project")
                                
                                return sample_project
                            else:
                                self.log_result("projects", "GC PIN format validation", False, 
                                              f"Invalid PIN format: {sample_project.get('gc_pin') if sample_project else 'None'}")
                        else:
                            self.log_result("projects", "GC PIN fields present", False, 
                                          "No projects have GC PIN fields populated")
                    else:
                        self.log_result("projects", "Projects data availability", False, 
                                      "No projects found in system")
                else:
                    self.log_result("projects", "Projects endpoint response format", False, 
                                  f"Expected list, got {type(projects)}", response)
            else:
                self.log_result("projects", "Projects endpoint accessibility", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Projects endpoint accessibility", False, str(e))
        
        return None
    
    def test_cors_configuration(self):
        """Test CORS Configuration - Check if backend accepts requests from frontend domain"""
        print("\n=== Testing CORS Configuration ===")
        
        # Test 1: Check CORS headers in response
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            # Test preflight request
            response = self.session.options(f"{self.base_url}/projects", headers=headers, timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print(f"CORS Headers received: {cors_headers}")
            
            # Check if CORS allows our frontend origin
            allow_origin = cors_headers.get('Access-Control-Allow-Origin')
            if allow_origin == '*' or allow_origin == self.frontend_url:
                self.log_result("cors", "CORS origin policy", True, 
                              f"Origin allowed: {allow_origin}")
            else:
                self.log_result("cors", "CORS origin policy", False, 
                              f"Origin not allowed. Expected: {self.frontend_url}, Got: {allow_origin}")
            
            # Check if required methods are allowed
            allow_methods = cors_headers.get('Access-Control-Allow-Methods', '')
            required_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
            missing_methods = [method for method in required_methods if method not in allow_methods]
            
            if not missing_methods:
                self.log_result("cors", "CORS methods policy", True, 
                              f"All required methods allowed: {allow_methods}")
            else:
                self.log_result("cors", "CORS methods policy", False, 
                              f"Missing methods: {missing_methods}. Allowed: {allow_methods}")
            
            # Check if Content-Type header is allowed
            allow_headers = cors_headers.get('Access-Control-Allow-Headers', '')
            if 'Content-Type' in allow_headers or '*' in allow_headers:
                self.log_result("cors", "CORS headers policy", True, 
                              f"Content-Type header allowed: {allow_headers}")
            else:
                self.log_result("cors", "CORS headers policy", False, 
                              f"Content-Type header not allowed: {allow_headers}")
                
        except Exception as e:
            self.log_result("cors", "CORS preflight request", False, str(e))
        
        # Test 2: Actual request with Origin header
        try:
            headers = {
                'Origin': self.frontend_url,
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(f"{self.base_url}/projects", headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Check if CORS headers are present in actual response
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                if cors_origin:
                    self.log_result("cors", "CORS actual request", True, 
                                  f"Actual request successful with CORS origin: {cors_origin}")
                else:
                    self.log_result("cors", "CORS actual request", False, 
                                  "Actual request successful but no CORS origin header")
            else:
                self.log_result("cors", "CORS actual request", False, 
                              f"Actual request failed: HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("cors", "CORS actual request", False, str(e))
    
    def test_gc_login_endpoint(self):
        """Test GC Login Endpoint - POST /api/gc/login-simple with valid PIN"""
        print("\n=== Testing GC Login Endpoint ===")
        
        # First, ensure we have a valid project and PIN from the projects test
        if not hasattr(self, 'test_project_id') or not hasattr(self, 'test_project_pin'):
            print("Getting fresh project data for login test...")
            project = self.test_projects_endpoint_with_gc_pins()
            if not project:
                self.log_result("gc_login", "GC login setup", False, 
                              "No valid project with PIN found for login test")
                return False
        
        project_id = self.test_project_id
        project_pin = self.test_project_pin
        project_name = self.test_project_name
        
        print(f"Testing login with Project: {project_name} (ID: {project_id}, PIN: {project_pin})")
        
        # Test 1: Valid login attempt
        try:
            login_data = {
                "project_id": project_id,
                "pin": project_pin
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Origin': self.frontend_url
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers=headers,
                timeout=10
            )
            
            print(f"Login response status: {response.status_code}")
            print(f"Login response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Login response data: {response_data}")
                
                # Check if login was successful
                if "success" in response_data and response_data["success"]:
                    self.log_result("gc_login", "Valid PIN login", True, 
                                  f"Login successful for project {project_name}")
                    
                    # Check if new PIN was generated (security feature)
                    if "new_pin" in response_data:
                        new_pin = response_data["new_pin"]
                        self.log_result("gc_login", "PIN regeneration", True, 
                                      f"New PIN generated: {new_pin}")
                        
                        # Update our test PIN for subsequent tests
                        self.test_project_pin = new_pin
                    else:
                        self.log_result("gc_login", "PIN regeneration", False, 
                                      "No new PIN in response")
                else:
                    self.log_result("gc_login", "Valid PIN login", False, 
                                  f"Login failed: {response_data.get('message', 'Unknown error')}", response)
            elif response.status_code == 401:
                # This might be expected if PIN was already used
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if "already used" in response_data.get("message", "").lower():
                    self.log_result("gc_login", "Used PIN rejection", True, 
                                  "Correctly rejected already used PIN")
                    
                    # Try to get a fresh PIN
                    print("Getting fresh PIN for login test...")
                    fresh_pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if fresh_pin_response.status_code == 200:
                        fresh_pin_data = fresh_pin_response.json()
                        fresh_pin = fresh_pin_data.get("gcPin")
                        
                        if fresh_pin:
                            print(f"Got fresh PIN: {fresh_pin}, retrying login...")
                            # Retry with fresh PIN
                            login_data["pin"] = fresh_pin
                            retry_response = self.session.post(
                                f"{self.base_url}/gc/login-simple",
                                json=login_data,
                                headers=headers,
                                timeout=10
                            )
                            
                            if retry_response.status_code == 200:
                                retry_data = retry_response.json()
                                if retry_data.get("success"):
                                    self.log_result("gc_login", "Fresh PIN login", True, 
                                                  f"Login successful with fresh PIN: {fresh_pin}")
                                else:
                                    self.log_result("gc_login", "Fresh PIN login", False, 
                                                  f"Fresh PIN login failed: {retry_data.get('message')}")
                            else:
                                self.log_result("gc_login", "Fresh PIN login", False, 
                                              f"Fresh PIN login HTTP {retry_response.status_code}", retry_response)
                        else:
                            self.log_result("gc_login", "Fresh PIN generation", False, 
                                          "Could not get fresh PIN")
                    else:
                        self.log_result("gc_login", "Fresh PIN generation", False, 
                                      f"Fresh PIN request failed: HTTP {fresh_pin_response.status_code}")
                else:
                    self.log_result("gc_login", "Valid PIN login", False, 
                                  f"Login failed with 401: {response_data.get('message', 'Unknown error')}", response)
            else:
                self.log_result("gc_login", "Valid PIN login", False, 
                              f"Unexpected status code: {response.status_code}", response)
                
        except requests.exceptions.ConnectionError as e:
            self.log_result("gc_login", "GC login connectivity", False, 
                          f"Connection error - this is the main issue: {str(e)}")
        except requests.exceptions.Timeout as e:
            self.log_result("gc_login", "GC login connectivity", False, 
                          f"Timeout error: {str(e)}")
        except Exception as e:
            self.log_result("gc_login", "Valid PIN login", False, str(e))
        
        # Test 2: Invalid project ID
        try:
            invalid_login_data = {
                "project_id": "invalid-project-id",
                "pin": "1234"
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=invalid_login_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_result("gc_login", "Invalid project ID rejection", True, 
                              "Correctly rejected invalid project ID")
            else:
                self.log_result("gc_login", "Invalid project ID rejection", False, 
                              f"Expected 401, got {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Invalid project ID rejection", False, str(e))
        
        # Test 3: Invalid PIN
        try:
            invalid_pin_data = {
                "project_id": project_id,
                "pin": "0000"  # Invalid PIN
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=invalid_pin_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_result("gc_login", "Invalid PIN rejection", True, 
                              "Correctly rejected invalid PIN")
            else:
                self.log_result("gc_login", "Invalid PIN rejection", False, 
                              f"Expected 401, got {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Invalid PIN rejection", False, str(e))
    
    def test_gc_dashboard_access(self):
        """Test GC Dashboard access after successful login"""
        print("\n=== Testing GC Dashboard Access ===")
        
        if not hasattr(self, 'test_project_id'):
            self.log_result("gc_login", "Dashboard access setup", False, 
                          "No project ID available for dashboard test")
            return
        
        project_id = self.test_project_id
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}", timeout=10)
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Check if dashboard has expected structure
                expected_fields = ["projectId", "projectName", "crewSummary", "tmTagSummary"]
                missing_fields = [field for field in expected_fields if field not in dashboard_data]
                
                if not missing_fields:
                    self.log_result("gc_login", "Dashboard data structure", True, 
                                  f"Dashboard data complete for project {dashboard_data.get('projectName', 'Unknown')}")
                else:
                    self.log_result("gc_login", "Dashboard data structure", False, 
                                  f"Missing dashboard fields: {missing_fields}")
            else:
                self.log_result("gc_login", "Dashboard accessibility", False, 
                              f"Dashboard request failed: HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Dashboard accessibility", False, str(e))
    
    def run_all_tests(self):
        """Run all connectivity and CORS tests"""
        print("🔥 FIREPROTECT GC LOGIN CONNECTIVITY & CORS TESTING")
        print("=" * 60)
        
        # Test 1: Basic connectivity
        connectivity_ok = self.test_basic_connectivity()
        
        if not connectivity_ok:
            print("\n❌ CRITICAL: Basic connectivity failed. Cannot proceed with other tests.")
            self.print_summary()
            return False
        
        # Test 2: Projects endpoint with GC PINs
        self.test_projects_endpoint_with_gc_pins()
        
        # Test 3: CORS configuration
        self.test_cors_configuration()
        
        # Test 4: GC login endpoint
        self.test_gc_login_endpoint()
        
        # Test 5: GC dashboard access
        self.test_gc_dashboard_access()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🔥 GC LOGIN CONNECTIVITY TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper()}: {status} ({passed} passed, {failed} failed)")
            
            # Print errors for failed tests
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print("\n" + "=" * 60)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {overall_status} ({total_passed} passed, {total_failed} failed)")
        
        if total_failed > 0:
            print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
            print("The user is experiencing 'unable to connect to server' errors.")
            print("Based on test results, the main issues are likely:")
            
            connectivity_failed = self.test_results["connectivity"]["failed"] > 0
            cors_failed = self.test_results["cors"]["failed"] > 0
            gc_login_failed = self.test_results["gc_login"]["failed"] > 0
            
            if connectivity_failed:
                print("1. ❌ BACKEND CONNECTIVITY: Backend server is not responding")
            if cors_failed:
                print("2. ❌ CORS CONFIGURATION: CORS headers not properly configured")
            if gc_login_failed:
                print("3. ❌ GC LOGIN ENDPOINT: Login endpoint not working correctly")
        else:
            print("\n✅ All systems operational! GC login should work correctly.")
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = GCConnectivityTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()