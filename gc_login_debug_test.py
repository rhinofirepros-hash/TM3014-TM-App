#!/usr/bin/env python3
"""
GC Login Connection Debug Test
Specifically tests the exact endpoints the frontend is calling to debug the "unable to connect to server" issue
"""

import requests
import json
from datetime import datetime
import uuid
import sys
import time

# Get backend URL from frontend .env file
BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

class GCLoginDebugTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "projects_endpoint": {"passed": 0, "failed": 0, "errors": []},
            "cors_check": {"passed": 0, "failed": 0, "errors": []},
            "pin_flow": {"passed": 0, "failed": 0, "errors": []},
            "gc_login": {"passed": 0, "failed": 0, "errors": []}
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
                    error_msg += f" Response: {response.text[:500]}"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_projects_endpoint(self):
        """Test Projects Endpoint (what frontend calls first) - GET /api/projects"""
        print("\n=== STEP 1: Testing Projects Endpoint (Frontend's First Call) ===")
        print("This is where 'unable to connect to server' error occurs")
        
        try:
            # Test basic connectivity first
            print(f"Testing connectivity to: {self.base_url}/projects")
            
            # Add headers that frontend would typically send
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (compatible; GC-Dashboard-Test)',
                'Origin': 'https://gc-sprinkler-app.preview.emergentagent.com',
                'Referer': 'https://gc-sprinkler-app.preview.emergentagent.com/'
            }
            
            response = self.session.get(f"{self.base_url}/projects", headers=headers, timeout=30)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Response Data Type: {type(response_data)}")
                print(f"Number of projects returned: {len(response_data) if isinstance(response_data, list) else 'Not a list'}")
                
                if isinstance(response_data, list):
                    self.log_result("projects_endpoint", "GET /api/projects", True, f"Retrieved {len(response_data)} projects successfully")
                    self.projects_data = response_data
                    
                    # Show sample project data structure
                    if response_data:
                        sample_project = response_data[0]
                        print(f"Sample project structure: {list(sample_project.keys())}")
                        if 'gc_pin' in sample_project:
                            print(f"Sample project has gc_pin: {sample_project.get('gc_pin')}")
                        else:
                            print("⚠️  Sample project missing gc_pin field")
                    
                    return True
                else:
                    self.log_result("projects_endpoint", "GET /api/projects", False, "Response is not a list", response)
            elif response.status_code == 404:
                self.log_result("projects_endpoint", "GET /api/projects", False, "Endpoint not found - API routing issue", response)
            elif response.status_code == 500:
                self.log_result("projects_endpoint", "GET /api/projects", False, "Internal server error", response)
            elif response.status_code == 502:
                self.log_result("projects_endpoint", "GET /api/projects", False, "Bad Gateway - Backend not responding", response)
            elif response.status_code == 503:
                self.log_result("projects_endpoint", "GET /api/projects", False, "Service Unavailable", response)
            else:
                self.log_result("projects_endpoint", "GET /api/projects", False, f"Unexpected status code: {response.status_code}", response)
                
        except requests.exceptions.ConnectionError as e:
            self.log_result("projects_endpoint", "GET /api/projects", False, f"Connection Error: {str(e)}")
        except requests.exceptions.Timeout as e:
            self.log_result("projects_endpoint", "GET /api/projects", False, f"Timeout Error: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.log_result("projects_endpoint", "GET /api/projects", False, f"Request Error: {str(e)}")
        except Exception as e:
            self.log_result("projects_endpoint", "GET /api/projects", False, f"Unexpected Error: {str(e)}")
        
        return False
    
    def test_cors_configuration(self):
        """Check CORS Configuration - Verify backend accepts requests from frontend domain"""
        print("\n=== STEP 2: Testing CORS Configuration ===")
        print("Checking if backend accepts requests from frontend domain")
        
        try:
            # Test preflight OPTIONS request
            headers = {
                'Origin': 'https://gc-sprinkler-app.preview.emergentagent.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            print("Testing preflight OPTIONS request...")
            options_response = self.session.options(f"{self.base_url}/projects", headers=headers, timeout=10)
            
            print(f"OPTIONS Response Status: {options_response.status_code}")
            print(f"OPTIONS Response Headers: {dict(options_response.headers)}")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': options_response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': options_response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': options_response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': options_response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print(f"CORS Headers: {cors_headers}")
            
            # Test actual GET request with CORS headers
            print("Testing actual GET request with CORS headers...")
            get_headers = {
                'Origin': 'https://gc-sprinkler-app.preview.emergentagent.com',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            get_response = self.session.get(f"{self.base_url}/projects", headers=get_headers, timeout=10)
            
            print(f"GET Response Status: {get_response.status_code}")
            cors_origin = get_response.headers.get('Access-Control-Allow-Origin')
            print(f"GET Response CORS Origin: {cors_origin}")
            
            if get_response.status_code == 200:
                if cors_origin == '*' or cors_origin == 'https://gc-sprinkler-app.preview.emergentagent.com':
                    self.log_result("cors_check", "CORS Configuration", True, f"CORS properly configured - Origin: {cors_origin}")
                else:
                    self.log_result("cors_check", "CORS Configuration", False, f"CORS origin mismatch - Expected: https://gc-sprinkler-app.preview.emergentagent.com, Got: {cors_origin}")
            else:
                self.log_result("cors_check", "CORS Configuration", False, f"GET request failed with status: {get_response.status_code}")
                
        except Exception as e:
            self.log_result("cors_check", "CORS Configuration", False, f"CORS test error: {str(e)}")
    
    def test_complete_pin_flow(self):
        """Test a complete PIN flow as requested"""
        print("\n=== STEP 3: Testing Complete PIN Flow ===")
        
        # First, get projects to find one with a PIN
        if not hasattr(self, 'projects_data'):
            print("No projects data available, attempting to fetch...")
            if not self.test_projects_endpoint():
                self.log_result("pin_flow", "PIN Flow Setup", False, "Could not fetch projects data")
                return False
        
        if not self.projects_data:
            self.log_result("pin_flow", "PIN Flow Setup", False, "No projects available for PIN testing")
            return False
        
        # Find a project with a PIN or use the first project
        test_project = None
        for project in self.projects_data:
            if project.get('gc_pin'):
                test_project = project
                break
        
        if not test_project:
            test_project = self.projects_data[0]
        
        project_id = test_project.get('id')
        if not project_id:
            self.log_result("pin_flow", "PIN Flow Setup", False, "No valid project ID found")
            return False
        
        print(f"Using project: {test_project.get('name', 'Unknown')} (ID: {project_id})")
        
        # Step 3a: Generate a PIN
        print(f"\n--- Step 3a: Generate PIN for project {project_id} ---")
        try:
            pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin", timeout=10)
            
            print(f"PIN Generation Status: {pin_response.status_code}")
            
            if pin_response.status_code == 200:
                pin_data = pin_response.json()
                print(f"PIN Response: {pin_data}")
                
                if 'gcPin' in pin_data:
                    generated_pin = pin_data['gcPin']
                    project_name = pin_data.get('projectName', 'Unknown')
                    self.log_result("pin_flow", "PIN Generation", True, f"Generated PIN '{generated_pin}' for project '{project_name}'")
                    
                    # Step 3b: Verify PIN appears in projects list
                    print(f"\n--- Step 3b: Verify PIN '{generated_pin}' appears in projects list ---")
                    projects_response = self.session.get(f"{self.base_url}/projects", timeout=10)
                    
                    if projects_response.status_code == 200:
                        updated_projects = projects_response.json()
                        pin_found = False
                        
                        for proj in updated_projects:
                            if proj.get('id') == project_id and proj.get('gc_pin') == generated_pin:
                                pin_found = True
                                break
                        
                        if pin_found:
                            self.log_result("pin_flow", "PIN in Projects List", True, f"PIN '{generated_pin}' found in projects list")
                        else:
                            self.log_result("pin_flow", "PIN in Projects List", False, f"PIN '{generated_pin}' not found in projects list")
                    else:
                        self.log_result("pin_flow", "PIN in Projects List", False, f"Could not fetch projects list: {projects_response.status_code}")
                    
                    # Step 3c: Test GC login with that PIN
                    print(f"\n--- Step 3c: Test GC login with PIN '{generated_pin}' ---")
                    self.test_gc_login_with_pin(project_id, generated_pin)
                    
                else:
                    self.log_result("pin_flow", "PIN Generation", False, "No 'gcPin' field in response", pin_response)
            else:
                self.log_result("pin_flow", "PIN Generation", False, f"PIN generation failed with status: {pin_response.status_code}", pin_response)
                
        except Exception as e:
            self.log_result("pin_flow", "PIN Generation", False, f"PIN generation error: {str(e)}")
    
    def test_gc_login_with_pin(self, project_id, pin):
        """Test GC login with specific PIN - POST /api/gc/login-simple"""
        print(f"\n=== Testing GC Login with PIN '{pin}' ===")
        
        try:
            # Test the exact login payload format
            login_data = {
                "projectId": project_id,  # Using camelCase as expected by backend
                "pin": pin
            }
            
            print(f"Login payload: {login_data}")
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'https://gc-sprinkler-app.preview.emergentagent.com'
            }
            
            login_response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers=headers,
                timeout=10
            )
            
            print(f"Login Response Status: {login_response.status_code}")
            print(f"Login Response Headers: {dict(login_response.headers)}")
            
            if login_response.status_code == 200:
                response_data = login_response.json()
                print(f"Login Response Data: {response_data}")
                
                if response_data.get('success'):
                    self.log_result("gc_login", "GC Login Success", True, f"Successfully logged in with PIN '{pin}'")
                    
                    # Test accessing dashboard after login
                    dashboard_response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}", timeout=10)
                    
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        self.log_result("gc_login", "Dashboard Access", True, f"Dashboard accessible after login")
                        print(f"Dashboard data keys: {list(dashboard_data.keys()) if isinstance(dashboard_data, dict) else 'Not a dict'}")
                    else:
                        self.log_result("gc_login", "Dashboard Access", False, f"Dashboard not accessible: {dashboard_response.status_code}")
                else:
                    self.log_result("gc_login", "GC Login Success", False, f"Login response indicates failure: {response_data}")
                    
            elif login_response.status_code == 400:
                self.log_result("gc_login", "GC Login Success", False, "Bad Request - Check payload format", login_response)
            elif login_response.status_code == 401:
                response_data = login_response.json() if login_response.text else {}
                self.log_result("gc_login", "GC Login Success", False, f"Unauthorized - {response_data.get('detail', 'Invalid PIN or PIN already used')}", login_response)
            elif login_response.status_code == 404:
                self.log_result("gc_login", "GC Login Success", False, "Login endpoint not found", login_response)
            else:
                self.log_result("gc_login", "GC Login Success", False, f"Unexpected status: {login_response.status_code}", login_response)
                
        except requests.exceptions.ConnectionError as e:
            self.log_result("gc_login", "GC Login Success", False, f"Connection Error during login: {str(e)}")
        except Exception as e:
            self.log_result("gc_login", "GC Login Success", False, f"Login error: {str(e)}")
    
    def test_specific_project_pins(self):
        """Test specific project IDs mentioned in test_result.md"""
        print("\n=== Testing Specific Project IDs from test_result.md ===")
        
        # These are the project IDs mentioned in the test results
        specific_project_ids = [
            "68cc802f8d44fcd8015b39b8",  # 3rd Ave project
            "68cc802f8d44fcd8015b39b9"   # Full Contract Project Test
        ]
        
        for project_id in specific_project_ids:
            print(f"\n--- Testing Project ID: {project_id} ---")
            
            try:
                # Try to generate PIN for this specific project
                pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin", timeout=10)
                
                if pin_response.status_code == 200:
                    pin_data = pin_response.json()
                    if 'gcPin' in pin_data:
                        pin = pin_data['gcPin']
                        project_name = pin_data.get('projectName', 'Unknown')
                        print(f"✅ Project '{project_name}' (ID: {project_id}) has PIN: {pin}")
                        
                        # Test login with this PIN
                        self.test_gc_login_with_pin(project_id, pin)
                    else:
                        print(f"❌ Project {project_id} PIN response missing 'gcPin' field: {pin_data}")
                else:
                    print(f"❌ Project {project_id} PIN generation failed: {pin_response.status_code}")
                    if pin_response.text:
                        print(f"   Response: {pin_response.text[:200]}")
                        
            except Exception as e:
                print(f"❌ Error testing project {project_id}: {str(e)}")
    
    def run_comprehensive_debug(self):
        """Run comprehensive debug test for GC login connection issue"""
        print("🔍 GC LOGIN CONNECTION DEBUG TEST")
        print("=" * 60)
        print("Testing the exact endpoints the frontend is calling to debug")
        print("the 'unable to connect to server' error on GC login page")
        print("=" * 60)
        
        # Step 1: Test Projects Endpoint (what frontend calls first)
        self.test_projects_endpoint()
        
        # Step 2: Check CORS Configuration
        self.test_cors_configuration()
        
        # Step 3: Test complete PIN flow
        self.test_complete_pin_flow()
        
        # Step 4: Test specific project IDs
        self.test_specific_project_pins()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🔍 GC LOGIN DEBUG TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{status} {category.upper()}: {passed} passed, {failed} failed")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"   ❌ {error}")
        
        print(f"\n📊 OVERALL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED - GC Login system is working correctly!")
            print("   If user is still getting 'unable to connect to server',")
            print("   the issue may be on the frontend side or with specific PIN usage.")
        else:
            print("⚠️  ISSUES FOUND - See failed tests above for details")
            print("   These issues may be causing the 'unable to connect to server' error")
        
        print("=" * 60)

def main():
    """Main function to run the debug test"""
    tester = GCLoginDebugTester()
    tester.run_comprehensive_debug()

if __name__ == "__main__":
    main()