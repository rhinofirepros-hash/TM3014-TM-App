#!/usr/bin/env python3
"""
GC Login Edge Case Testing
Test edge cases that might cause "unable to connect to server" errors
"""

import requests
import json
from datetime import datetime
import uuid
import sys
import time

# Get backend URL from frontend .env file
BACKEND_URL = "https://fireprotect-app.preview.emergentagent.com/api"

class GCEdgeCaseTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        
    def test_invalid_project_id(self):
        """Test login with invalid project ID"""
        print("\n=== Testing Invalid Project ID ===")
        
        invalid_project_id = "invalid-project-id-12345"
        fake_pin = "1234"
        
        login_data = {
            "projectId": invalid_project_id,
            "pin": fake_pin
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("✅ Correctly rejects invalid project ID with 401")
            else:
                print(f"❌ Unexpected response for invalid project ID: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing invalid project ID: {str(e)}")
    
    def test_used_pin(self):
        """Test login with already used PIN"""
        print("\n=== Testing Already Used PIN ===")
        
        # First, get a valid project and generate a PIN
        try:
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code == 200:
                projects = projects_response.json()
                if projects:
                    project = projects[0]
                    project_id = project['id']
                    
                    # Generate a PIN
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        pin = pin_data['gcPin']
                        
                        print(f"Generated PIN: {pin} for project: {project_id}")
                        
                        # Use the PIN once (should succeed)
                        login_data = {"projectId": project_id, "pin": pin}
                        first_login = self.session.post(
                            f"{self.base_url}/gc/login-simple",
                            json=login_data,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        print(f"First login status: {first_login.status_code}")
                        
                        if first_login.status_code == 200:
                            print("✅ First login successful")
                            
                            # Try to use the same PIN again (should fail)
                            second_login = self.session.post(
                                f"{self.base_url}/gc/login-simple",
                                json=login_data,
                                headers={'Content-Type': 'application/json'}
                            )
                            
                            print(f"Second login status: {second_login.status_code}")
                            print(f"Second login response: {second_login.text}")
                            
                            if second_login.status_code == 401:
                                print("✅ Correctly rejects used PIN with 401")
                            else:
                                print(f"❌ Should reject used PIN, got: {second_login.status_code}")
                        else:
                            print(f"❌ First login failed: {first_login.status_code}")
                            
        except Exception as e:
            print(f"❌ Error testing used PIN: {str(e)}")
    
    def test_malformed_requests(self):
        """Test malformed request payloads"""
        print("\n=== Testing Malformed Requests ===")
        
        test_cases = [
            # Missing projectId
            {"pin": "1234"},
            # Missing pin
            {"projectId": "68cc802f8d44fcd8015b39b8"},
            # Wrong field names (snake_case instead of camelCase)
            {"project_id": "68cc802f8d44fcd8015b39b8", "pin": "1234"},
            # Empty values
            {"projectId": "", "pin": "1234"},
            {"projectId": "68cc802f8d44fcd8015b39b8", "pin": ""},
            # Null values
            {"projectId": None, "pin": "1234"},
            {"projectId": "68cc802f8d44fcd8015b39b8", "pin": None},
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest case {i+1}: {test_case}")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/gc/login-simple",
                    json=test_case,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code in [400, 422]:  # Bad Request or Unprocessable Entity
                    print("✅ Correctly rejects malformed request")
                else:
                    print(f"⚠️  Unexpected status for malformed request: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error with test case {i+1}: {str(e)}")
    
    def test_network_timeout_simulation(self):
        """Test with very short timeout to simulate network issues"""
        print("\n=== Testing Network Timeout Simulation ===")
        
        try:
            # Use a very short timeout to simulate network issues
            response = self.session.get(
                f"{self.base_url}/projects",
                timeout=0.001  # 1ms timeout - should fail
            )
            print(f"❌ Request should have timed out but got: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("✅ Timeout correctly simulated - this could cause 'unable to connect to server'")
        except Exception as e:
            print(f"⚠️  Other network error: {str(e)}")
    
    def test_content_type_issues(self):
        """Test requests with wrong content types"""
        print("\n=== Testing Content Type Issues ===")
        
        # Get a valid project and PIN first
        try:
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code == 200:
                projects = projects_response.json()
                if projects:
                    project = projects[0]
                    project_id = project['id']
                    
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        pin = pin_data['gcPin']
                        
                        login_data = {"projectId": project_id, "pin": pin}
                        
                        # Test with wrong content type
                        print("Testing with text/plain content type...")
                        response = self.session.post(
                            f"{self.base_url}/gc/login-simple",
                            data=json.dumps(login_data),  # Send as string, not JSON
                            headers={'Content-Type': 'text/plain'},
                            timeout=10
                        )
                        
                        print(f"Status: {response.status_code}")
                        print(f"Response: {response.text[:200]}")
                        
                        if response.status_code in [400, 415, 422]:
                            print("✅ Correctly rejects wrong content type")
                        else:
                            print(f"⚠️  Unexpected response for wrong content type: {response.status_code}")
                            
        except Exception as e:
            print(f"❌ Error testing content type: {str(e)}")
    
    def test_cors_preflight_failure(self):
        """Test CORS preflight with wrong origin"""
        print("\n=== Testing CORS Preflight with Wrong Origin ===")
        
        try:
            # Test with wrong origin
            headers = {
                'Origin': 'https://malicious-site.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(f"{self.base_url}/gc/login-simple", headers=headers)
            
            print(f"OPTIONS Status: {response.status_code}")
            print(f"CORS Origin: {response.headers.get('Access-Control-Allow-Origin')}")
            
            # The backend allows all origins (*), so this should still work
            if response.status_code == 200:
                print("✅ CORS allows all origins (backend configured with '*')")
            else:
                print(f"⚠️  CORS preflight failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing CORS: {str(e)}")
    
    def run_edge_case_tests(self):
        """Run all edge case tests"""
        print("🧪 GC LOGIN EDGE CASE TESTING")
        print("=" * 50)
        print("Testing edge cases that might cause connection issues")
        print("=" * 50)
        
        self.test_invalid_project_id()
        self.test_used_pin()
        self.test_malformed_requests()
        self.test_network_timeout_simulation()
        self.test_content_type_issues()
        self.test_cors_preflight_failure()
        
        print("\n" + "=" * 50)
        print("🧪 EDGE CASE TESTING COMPLETE")
        print("=" * 50)

def main():
    """Main function to run edge case tests"""
    tester = GCEdgeCaseTester()
    tester.run_edge_case_tests()

if __name__ == "__main__":
    main()