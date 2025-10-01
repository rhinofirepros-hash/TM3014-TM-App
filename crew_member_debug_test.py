#!/usr/bin/env python3
"""
Crew Member Creation Debug Test
Specifically testing the POST /api/installers endpoint for the production issue
"""

import requests
import json
from datetime import datetime, date
import uuid
import sys

# Production backend URL from the review request
BACKEND_URL = "https://tm3014-tm-app-production.up.railway.app/api"

class CrewMemberDebugTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code})"
                try:
                    error_msg += f" Response: {response.text[:500]}"
                except:
                    error_msg += " (Could not read response)"
            self.test_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.log_result("Basic connectivity", True, f"Connected to {self.base_url}")
                return True
            else:
                self.log_result("Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Basic connectivity", False, str(e))
            return False
    
    def test_crew_member_creation_from_screenshot(self):
        """Test crew member creation with exact data from screenshot"""
        print("\n=== Testing Crew Member Creation with Screenshot Data ===")
        
        # Data from the screenshot in the review request
        crew_member_data = {
            "name": "Test Installer",
            "cost_rate": 33,
            "hire_date": "2025-09-30",
            "phone": "(555) 123-4567",
            "email": "john@example.com",
            "emergency_contact": "Jane Smith - (555) 987-6543"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=crew_member_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Request URL: {self.base_url}/installers")
            print(f"Request Data: {json.dumps(crew_member_data, indent=2)}")
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
                self.log_result("Screenshot data creation", True, f"Crew member created successfully")
                return response_data
            else:
                print(f"Response Text: {response.text}")
                self.log_result("Screenshot data creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Screenshot data creation", False, str(e))
        
        return None
    
    def test_minimal_data_creation(self):
        """Test crew member creation with minimal required data"""
        print("\n=== Testing Minimal Data Creation ===")
        
        # Test with just name and cost_rate
        minimal_data = {
            "name": "Minimal Test Installer",
            "cost_rate": 35
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=minimal_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Request Data: {json.dumps(minimal_data, indent=2)}")
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
                self.log_result("Minimal data creation", True, f"Crew member created with minimal data")
                return response_data
            else:
                print(f"Response Text: {response.text}")
                self.log_result("Minimal data creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Minimal data creation", False, str(e))
        
        return None
    
    def test_field_validation(self):
        """Test individual field validation"""
        print("\n=== Testing Field Validation ===")
        
        # Test 1: Missing name
        test_cases = [
            {
                "name": "Missing name test",
                "data": {
                    "cost_rate": 33,
                    "hire_date": "2025-09-30"
                },
                "expected_error": "name field required"
            },
            {
                "name": "Missing cost_rate test", 
                "data": {
                    "name": "Test Installer",
                    "hire_date": "2025-09-30"
                },
                "expected_error": "cost_rate field required"
            },
            {
                "name": "Invalid cost_rate type test",
                "data": {
                    "name": "Test Installer",
                    "cost_rate": "invalid",
                    "hire_date": "2025-09-30"
                },
                "expected_error": "cost_rate must be numeric"
            },
            {
                "name": "Invalid date format test",
                "data": {
                    "name": "Test Installer",
                    "cost_rate": 33,
                    "hire_date": "invalid-date"
                },
                "expected_error": "invalid date format"
            },
            {
                "name": "Invalid email format test",
                "data": {
                    "name": "Test Installer",
                    "cost_rate": 33,
                    "email": "invalid-email"
                },
                "expected_error": "invalid email format"
            }
        ]
        
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{self.base_url}/installers",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"\nTest: {test_case['name']}")
                print(f"Data: {json.dumps(test_case['data'], indent=2)}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code >= 400:
                    self.log_result(f"Validation - {test_case['name']}", True, f"Correctly rejected invalid data")
                else:
                    self.log_result(f"Validation - {test_case['name']}", False, f"Should have rejected invalid data", response)
                    
            except Exception as e:
                self.log_result(f"Validation - {test_case['name']}", False, str(e))
    
    def test_different_data_combinations(self):
        """Test different combinations of data"""
        print("\n=== Testing Different Data Combinations ===")
        
        test_combinations = [
            {
                "name": "Full data set",
                "data": {
                    "name": "Full Data Installer",
                    "cost_rate": 40.50,
                    "hire_date": "2024-01-15",
                    "phone": "(555) 111-2222",
                    "email": "full@example.com",
                    "emergency_contact": "Emergency Contact - (555) 333-4444"
                }
            },
            {
                "name": "No optional fields",
                "data": {
                    "name": "Basic Installer",
                    "cost_rate": 30
                }
            },
            {
                "name": "With phone only",
                "data": {
                    "name": "Phone Only Installer",
                    "cost_rate": 35,
                    "phone": "(555) 555-5555"
                }
            },
            {
                "name": "With email only",
                "data": {
                    "name": "Email Only Installer", 
                    "cost_rate": 38,
                    "email": "email@example.com"
                }
            },
            {
                "name": "Future hire date",
                "data": {
                    "name": "Future Hire Installer",
                    "cost_rate": 42,
                    "hire_date": "2025-12-31"
                }
            }
        ]
        
        for combination in test_combinations:
            try:
                response = self.session.post(
                    f"{self.base_url}/installers",
                    json=combination["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"\nTest: {combination['name']}")
                print(f"Data: {json.dumps(combination['data'], indent=2)}")
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200 or response.status_code == 201:
                    response_data = response.json()
                    print(f"Success: {json.dumps(response_data, indent=2)}")
                    self.log_result(f"Combination - {combination['name']}", True, f"Created successfully")
                else:
                    print(f"Error: {response.text}")
                    self.log_result(f"Combination - {combination['name']}", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result(f"Combination - {combination['name']}", False, str(e))
    
    def test_endpoint_existence(self):
        """Test if the /api/installers endpoint exists"""
        print("\n=== Testing Endpoint Existence ===")
        
        # Test GET endpoint first
        try:
            response = self.session.get(f"{self.base_url}/installers")
            print(f"GET {self.base_url}/installers")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                self.log_result("GET /api/installers exists", True, f"Endpoint exists and returns data")
            elif response.status_code == 404:
                self.log_result("GET /api/installers exists", False, f"Endpoint not found - may not be implemented")
            else:
                self.log_result("GET /api/installers exists", True, f"Endpoint exists (status {response.status_code})")
                
        except Exception as e:
            self.log_result("GET /api/installers exists", False, str(e))
        
        # Test POST with OPTIONS to check allowed methods
        try:
            response = self.session.options(f"{self.base_url}/installers")
            print(f"\nOPTIONS {self.base_url}/installers")
            print(f"Status: {response.status_code}")
            print(f"Allowed methods: {response.headers.get('Allow', 'Not specified')}")
            
            if 'POST' in response.headers.get('Allow', ''):
                self.log_result("POST method allowed", True, f"POST method is allowed")
            else:
                self.log_result("POST method allowed", False, f"POST method may not be allowed")
                
        except Exception as e:
            self.log_result("POST method check", False, str(e))
    
    def test_alternative_endpoints(self):
        """Test alternative endpoints that might handle crew member creation"""
        print("\n=== Testing Alternative Endpoints ===")
        
        alternative_endpoints = [
            "/api/workers",
            "/api/employees", 
            "/api/crew-members",
            "/api/crew",
            "/api/staff"
        ]
        
        test_data = {
            "name": "Alternative Test Installer",
            "cost_rate": 33,
            "hire_date": "2025-09-30",
            "phone": "(555) 123-4567",
            "email": "john@example.com",
            "emergency_contact": "Jane Smith - (555) 987-6543"
        }
        
        for endpoint in alternative_endpoints:
            try:
                # First check if endpoint exists with GET
                get_response = self.session.get(f"{self.base_url}{endpoint}")
                print(f"\nTesting {endpoint}")
                print(f"GET Status: {get_response.status_code}")
                
                if get_response.status_code != 404:
                    # Try POST if GET doesn't return 404
                    post_response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=test_data,
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"POST Status: {post_response.status_code}")
                    print(f"POST Response: {post_response.text[:200]}")
                    
                    if post_response.status_code == 200 or post_response.status_code == 201:
                        self.log_result(f"Alternative endpoint {endpoint}", True, f"Successfully created via {endpoint}")
                    else:
                        self.log_result(f"Alternative endpoint {endpoint}", False, f"Failed via {endpoint} - HTTP {post_response.status_code}")
                else:
                    print(f"Endpoint {endpoint} not found")
                    
            except Exception as e:
                print(f"Error testing {endpoint}: {str(e)}")
    
    def run_comprehensive_debug(self):
        """Run comprehensive debugging tests"""
        print("🔍 CREW MEMBER CREATION DEBUG TEST")
        print("=" * 50)
        print(f"Testing production backend: {self.base_url}")
        print("=" * 50)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Cannot connect to backend. Stopping tests.")
            return
        
        # Test endpoint existence
        self.test_endpoint_existence()
        
        # Test the exact data from screenshot
        self.test_crew_member_creation_from_screenshot()
        
        # Test minimal data
        self.test_minimal_data_creation()
        
        # Test field validation
        self.test_field_validation()
        
        # Test different data combinations
        self.test_different_data_combinations()
        
        # Test alternative endpoints
        self.test_alternative_endpoints()
        
        # Print summary
        print("\n" + "=" * 50)
        print("🔍 DEBUG TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n🚨 ERRORS FOUND:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    tester = CrewMemberDebugTester()
    tester.run_comprehensive_debug()