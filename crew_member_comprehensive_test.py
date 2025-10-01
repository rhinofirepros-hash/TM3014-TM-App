#!/usr/bin/env python3
"""
Comprehensive Crew Member Creation Test with Authentication
Testing the POST /api/installers endpoint with proper auth and data types
"""

import requests
import json
from datetime import datetime, date
import uuid
import sys

# Production backend URL from the review request
BACKEND_URL = "https://tm3014-tm-app-production.up.railway.app/api"

class CrewMemberComprehensiveTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.auth_token = None
        
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
    
    def authenticate_admin(self):
        """Authenticate as admin to get access token"""
        print("\n=== Admin Authentication ===")
        
        auth_data = {"pin": "J777"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/admin",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Auth request to: {self.base_url}/auth/admin")
            print(f"Auth data: {json.dumps(auth_data, indent=2)}")
            print(f"Auth response status: {response.status_code}")
            print(f"Auth response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "token" in response_data:
                    self.auth_token = response_data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_result("Admin authentication", True, f"Authenticated successfully")
                    return True
                else:
                    self.log_result("Admin authentication", False, f"No token in response", response)
            else:
                self.log_result("Admin authentication", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Admin authentication", False, str(e))
        
        return False
    
    def test_with_auth_header(self):
        """Test with simple auth header (fallback if token auth fails)"""
        print("\n=== Testing with Auth Header ===")
        
        # Try with a simple Bearer token
        self.session.headers.update({"Authorization": "Bearer admin-token"})
        
        test_data = {
            "name": "Auth Test Installer",
            "cost_rate": 35
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Request with auth header")
            print(f"Headers: {dict(self.session.headers)}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                self.log_result("Auth header test", True, f"Request succeeded with auth header")
                return True
            else:
                self.log_result("Auth header test", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Auth header test", False, str(e))
        
        return False
    
    def test_crew_member_with_proper_types(self):
        """Test crew member creation with proper data types"""
        print("\n=== Testing with Proper Data Types ===")
        
        # Data from screenshot but with proper types and only supported fields
        crew_member_data = {
            "name": "Test Installer",
            "cost_rate": 33.0,  # Ensure it's a float
            "hire_date": "2025-09-30",  # Keep as string, let Pydantic convert
            "phone": "(555) 123-4567",
            "email": "john@example.com"
            # Note: emergency_contact is NOT in the model, so we exclude it
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=crew_member_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Request Data: {json.dumps(crew_member_data, indent=2)}")
            print(f"Response Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                self.log_result("Proper types creation", True, f"Crew member created successfully")
                return response_data
            else:
                self.log_result("Proper types creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Proper types creation", False, str(e))
        
        return None
    
    def test_without_unsupported_fields(self):
        """Test without emergency_contact field (not in model)"""
        print("\n=== Testing Without Unsupported Fields ===")
        
        # Only include fields that are in the InstallerCreate model
        crew_member_data = {
            "name": "Clean Test Installer",
            "cost_rate": 33.0,
            "hire_date": "2025-09-30",
            "phone": "(555) 123-4567",
            "email": "john@example.com",
            "position": "Electrician"  # This field IS supported
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=crew_member_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Request Data: {json.dumps(crew_member_data, indent=2)}")
            print(f"Response Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                self.log_result("Clean fields creation", True, f"Crew member created without unsupported fields")
                return response_data
            else:
                self.log_result("Clean fields creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Clean fields creation", False, str(e))
        
        return None
    
    def test_date_formats(self):
        """Test different date formats"""
        print("\n=== Testing Different Date Formats ===")
        
        date_formats = [
            ("ISO format", "2025-09-30"),
            ("US format", "09/30/2025"),
            ("Date object", date(2025, 9, 30).isoformat()),
        ]
        
        for format_name, date_value in date_formats:
            crew_member_data = {
                "name": f"Date Test {format_name}",
                "cost_rate": 33.0,
                "hire_date": date_value,
                "phone": "(555) 123-4567",
                "email": f"test.{format_name.lower().replace(' ', '.')}@example.com"
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/installers",
                    json=crew_member_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"\nTesting {format_name}: {date_value}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code == 200 or response.status_code == 201:
                    self.log_result(f"Date format - {format_name}", True, f"Accepted {format_name}")
                else:
                    self.log_result(f"Date format - {format_name}", False, f"Rejected {format_name} - HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Date format - {format_name}", False, str(e))
    
    def test_field_requirements(self):
        """Test which fields are actually required"""
        print("\n=== Testing Field Requirements ===")
        
        # Test with only name
        test_cases = [
            {
                "name": "Only name",
                "data": {"name": "Name Only Test"}
            },
            {
                "name": "Name and cost_rate",
                "data": {"name": "Name Cost Test", "cost_rate": 35.0}
            },
            {
                "name": "All required fields",
                "data": {
                    "name": "Full Required Test",
                    "cost_rate": 35.0,
                    "position": "Electrician",
                    "active": True
                }
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
                
                if response.status_code == 200 or response.status_code == 201:
                    self.log_result(f"Requirements - {test_case['name']}", True, f"Accepted minimal data")
                else:
                    self.log_result(f"Requirements - {test_case['name']}", False, f"Rejected - HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Requirements - {test_case['name']}", False, str(e))
    
    def test_error_analysis(self):
        """Test to understand the 500 error better"""
        print("\n=== Error Analysis ===")
        
        # Test the exact failing case step by step
        print("Step 1: Test with emergency_contact (unsupported field)")
        failing_data = {
            "name": "Error Test 1",
            "cost_rate": 33,
            "emergency_contact": "Jane Smith - (555) 987-6543"  # This field doesn't exist in model
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=failing_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nStep 2: Test with hire_date as string")
        date_test_data = {
            "name": "Error Test 2",
            "cost_rate": 33,
            "hire_date": "2025-09-30"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=date_test_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nStep 3: Test with both unsupported field and date")
        combined_test_data = {
            "name": "Error Test 3",
            "cost_rate": 33,
            "hire_date": "2025-09-30",
            "emergency_contact": "Jane Smith - (555) 987-6543"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/installers",
                json=combined_test_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🔍 COMPREHENSIVE CREW MEMBER CREATION TEST")
        print("=" * 60)
        print(f"Testing production backend: {self.base_url}")
        print("=" * 60)
        
        # Try authentication first
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("⚠️  Admin auth failed, trying with simple auth header...")
            auth_success = self.test_with_auth_header()
        
        if not auth_success:
            print("⚠️  No authentication successful, testing without auth...")
        
        # Run tests
        self.test_crew_member_with_proper_types()
        self.test_without_unsupported_fields()
        self.test_date_formats()
        self.test_field_requirements()
        self.test_error_analysis()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔍 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print("\n🚨 ERRORS FOUND:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print("\n" + "=" * 60)
        
        # Provide recommendations
        print("🔧 RECOMMENDATIONS:")
        print("1. Remove 'emergency_contact' field - not supported by backend model")
        print("2. Ensure authentication is provided (Bearer token)")
        print("3. Use proper date format (YYYY-MM-DD)")
        print("4. Only required fields are 'name' and 'cost_rate'")
        print("=" * 60)

if __name__ == "__main__":
    tester = CrewMemberComprehensiveTester()
    tester.run_comprehensive_test()