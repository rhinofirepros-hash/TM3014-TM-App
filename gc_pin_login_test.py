#!/usr/bin/env python3
"""
GC PIN Login System Testing
Tests the fixed GC login endpoint as requested in the review
"""

import requests
import json
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://fireprotect-app.preview.emergentagent.com/api"

class GCPinLoginTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "pin_generation": {"passed": 0, "failed": 0, "errors": []},
            "gc_login": {"passed": 0, "failed": 0, "errors": []},
            "end_to_end": {"passed": 0, "failed": 0, "errors": []}
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
    
    def test_fresh_pin_generation(self, project_id):
        """Test generating a fresh PIN for the specified project"""
        print(f"\n=== Step 1: Generate Fresh PIN for Project {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if response has the expected structure
                if "gcPin" in response_data and "projectId" in response_data:
                    pin = response_data["gcPin"]
                    project_name = response_data.get("projectName", "Unknown")
                    pin_used = response_data.get("pinUsed", False)
                    
                    if pin and len(pin) == 4 and pin.isdigit():
                        self.log_result("pin_generation", "Fresh PIN generation", True, 
                                      f"Generated PIN '{pin}' for project '{project_name}' (Used: {pin_used})")
                        return pin, project_name
                    else:
                        self.log_result("pin_generation", "Fresh PIN generation", False, 
                                      f"Invalid PIN format: '{pin}'", response)
                else:
                    self.log_result("pin_generation", "Fresh PIN generation", False, 
                                  f"Missing required fields in response: {list(response_data.keys())}", response)
            else:
                self.log_result("pin_generation", "Fresh PIN generation", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_generation", "Fresh PIN generation", False, str(e))
        
        return None, None
    
    def test_gc_login_simple(self, project_id, pin):
        """Test the fixed GC login endpoint with the fresh PIN"""
        print(f"\n=== Step 2: Test GC Login with PIN '{pin}' ===")
        
        login_data = {
            "projectId": project_id,
            "pin": pin
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check for successful login response
                if "success" in response_data and response_data["success"]:
                    dashboard_url = response_data.get("dashboard_url", "")
                    new_pin = response_data.get("new_pin", "")
                    
                    self.log_result("gc_login", "GC login with fresh PIN", True, 
                                  f"Login successful! Dashboard URL: {dashboard_url}, New PIN: {new_pin}")
                    return True, new_pin
                else:
                    self.log_result("gc_login", "GC login with fresh PIN", False, 
                                  f"Login failed: {response_data.get('message', 'Unknown error')}", response)
            elif response.status_code == 401:
                response_data = response.json()
                self.log_result("gc_login", "GC login with fresh PIN", False, 
                              f"Authentication failed: {response_data.get('detail', 'Invalid credentials')}", response)
            else:
                self.log_result("gc_login", "GC login with fresh PIN", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "GC login with fresh PIN", False, str(e))
        
        return False, None
    
    def test_old_pin_rejection(self, project_id, old_pin):
        """Test that the old PIN is properly rejected after use"""
        print(f"\n=== Step 3: Verify Old PIN '{old_pin}' is Rejected ===")
        
        login_data = {
            "projectId": project_id,
            "pin": old_pin
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                response_data = response.json()
                error_message = response_data.get("detail", "")
                
                if "already used" in error_message.lower() or "invalid pin" in error_message.lower():
                    self.log_result("gc_login", "Old PIN rejection", True, 
                                  f"Old PIN correctly rejected: {error_message}")
                    return True
                else:
                    self.log_result("gc_login", "Old PIN rejection", False, 
                                  f"Unexpected error message: {error_message}", response)
            elif response.status_code == 200:
                self.log_result("gc_login", "Old PIN rejection", False, 
                              "Old PIN should be rejected but login succeeded", response)
            else:
                self.log_result("gc_login", "Old PIN rejection", False, 
                              f"Unexpected HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", "Old PIN rejection", False, str(e))
        
        return False
    
    def test_complete_flow(self, project_id):
        """Test the complete PIN generation → Login → PIN regeneration flow"""
        print(f"\n🎯 TESTING COMPLETE GC PIN LOGIN FLOW FOR PROJECT {project_id}")
        print("=" * 80)
        
        # Step 1: Generate fresh PIN
        pin, project_name = self.test_fresh_pin_generation(project_id)
        if not pin:
            self.log_result("end_to_end", "Complete flow", False, "Failed to generate fresh PIN")
            return False
        
        # Step 2: Test login with fresh PIN
        login_success, new_pin = self.test_gc_login_simple(project_id, pin)
        if not login_success:
            self.log_result("end_to_end", "Complete flow", False, "Failed to login with fresh PIN")
            return False
        
        # Step 3: Verify old PIN is rejected
        if new_pin and new_pin != pin:
            old_pin_rejected = self.test_old_pin_rejection(project_id, pin)
            if not old_pin_rejected:
                self.log_result("end_to_end", "Complete flow", False, "Old PIN was not properly rejected")
                return False
        
        # Step 4: Verify new PIN works
        if new_pin:
            print(f"\n=== Step 4: Verify New PIN '{new_pin}' Works ===")
            new_login_success, _ = self.test_gc_login_simple(project_id, new_pin)
            if not new_login_success:
                self.log_result("end_to_end", "Complete flow", False, "New PIN does not work")
                return False
        
        self.log_result("end_to_end", "Complete flow", True, 
                      f"Full workflow successful: PIN {pin} → Login → New PIN {new_pin}")
        return True
    
    def test_connectivity(self):
        """Test basic connectivity to the backend"""
        print("\n=== Testing Backend Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                print(f"✅ Backend connectivity: PASSED - Found {len(projects)} projects")
                return True
            else:
                print(f"❌ Backend connectivity: FAILED - HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connectivity: FAILED - {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 GC PIN LOGIN TEST SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASSED" if failed == 0 else "❌ FAILED"
            print(f"{category.upper()}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print("-" * 80)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"OVERALL: {overall_status} ({total_passed}/{total_passed + total_failed} tests, {success_rate:.1f}% success rate)")
        
        if total_failed == 0:
            print("\n🎉 GC PIN LOGIN SYSTEM IS WORKING PERFECTLY!")
            print("✅ Fresh PIN generation works")
            print("✅ GC login endpoint works without 400 errors")
            print("✅ Complete PIN workflow is functional")
            print("✅ User's 'unable to connect to server' issue should be resolved")
        else:
            print(f"\n⚠️  {total_failed} issues found that need attention")

def main():
    """Main test execution"""
    print("🚀 Starting GC PIN Login System Testing")
    print("Testing the fixed GC login endpoint as requested in review")
    print("=" * 80)
    
    tester = GCPinLoginTester()
    
    # Test connectivity first
    if not tester.test_connectivity():
        print("❌ Cannot connect to backend. Exiting.")
        return
    
    # Test the specific project ID mentioned in the review request
    project_id = "68cc802f8d44fcd8015b39b8"
    
    print(f"\n🎯 Testing GC PIN Login for Project ID: {project_id}")
    print("This is the project mentioned in the review request")
    
    # Run the complete flow test
    success = tester.test_complete_flow(project_id)
    
    # Print summary
    tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()