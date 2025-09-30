#!/usr/bin/env python3
"""
GC PIN System Final Verification Test
Tests the PIN system to confirm it's working as requested:
1. Generate a fresh PIN for project 68cc802f8d44fcd8015b39b8
2. Immediately test login with that PIN
3. Show that old PINs don't work (try to login again with same PIN)
4. Generate another fresh PIN to confirm it generates different PINs
"""

import requests
import json
import sys
import time

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"

class PINSystemTester:
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
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:500]})"
            self.test_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_pin_system_comprehensive(self):
        """Comprehensive PIN system test as requested"""
        print("\n🎯 GC PIN SYSTEM FINAL VERIFICATION TEST")
        print("=" * 60)
        
        project_id = "68cc802f8d44fcd8015b39b8"
        
        # Step 1: Generate a fresh PIN for the specific project
        print(f"\n📍 Step 1: Generate fresh PIN for project {project_id}")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                fresh_pin = pin_data.get("gcPin")
                project_name = pin_data.get("projectName", "Unknown")
                
                if fresh_pin:
                    self.log_result("Fresh PIN Generation", True, f"Generated PIN '{fresh_pin}' for project '{project_name}'")
                    print(f"   🔑 Fresh PIN: {fresh_pin}")
                    print(f"   📋 Project: {project_name}")
                else:
                    self.log_result("Fresh PIN Generation", False, "No PIN returned in response", response)
                    return False
            else:
                self.log_result("Fresh PIN Generation", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Fresh PIN Generation", False, str(e))
            return False
        
        # Step 2: Immediately test login with that fresh PIN
        print(f"\n🔐 Step 2: Test login with fresh PIN '{fresh_pin}'")
        try:
            login_data = {
                "projectId": project_id,
                "pin": fresh_pin
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                if login_result.get("success"):
                    self.log_result("Fresh PIN Login", True, f"Successfully logged in with PIN '{fresh_pin}'")
                    print(f"   ✅ Login successful!")
                    print(f"   📊 Dashboard access granted")
                    
                    # Check if PIN was regenerated after successful login
                    new_pin = login_result.get("new_pin")
                    if new_pin:
                        print(f"   🔄 New PIN generated: {new_pin}")
                        self.regenerated_pin = new_pin
                    else:
                        print(f"   ⚠️  No new PIN in response")
                else:
                    self.log_result("Fresh PIN Login", False, f"Login failed: {login_result.get('message', 'Unknown error')}", response)
                    return False
            else:
                # Show detailed error response for debugging
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "No detail provided")
                    print(f"   🔍 Error details: {error_detail}")
                    self.log_result("Fresh PIN Login", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("Fresh PIN Login", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
                return False
                
        except Exception as e:
            self.log_result("Fresh PIN Login", False, str(e))
            return False
        
        # Step 3: Show that old PINs don't work (try to login again with same PIN)
        print(f"\n🚫 Step 3: Test that old PIN '{fresh_pin}' no longer works")
        try:
            login_data = {
                "projectId": project_id,
                "pin": fresh_pin  # Using the same PIN that was just used
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                # This is expected - old PIN should be rejected
                error_data = response.json()
                error_message = error_data.get("detail", "")
                if "Invalid PIN or PIN already used" in error_message:
                    self.log_result("Old PIN Rejection", True, f"Old PIN '{fresh_pin}' correctly rejected with message: '{error_message}'")
                    print(f"   ✅ Old PIN correctly rejected!")
                    print(f"   📝 Error message: {error_message}")
                else:
                    self.log_result("Old PIN Rejection", False, f"Unexpected error message: {error_message}", response)
            elif response.status_code == 200:
                # This would be a problem - old PIN should not work
                self.log_result("Old PIN Rejection", False, "Old PIN still works - this is incorrect behavior", response)
                return False
            else:
                self.log_result("Old PIN Rejection", False, f"Unexpected HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Old PIN Rejection", False, str(e))
            return False
        
        # Step 4: Generate another fresh PIN to confirm it generates different PINs
        print(f"\n🔄 Step 4: Generate another fresh PIN to confirm uniqueness")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                second_fresh_pin = pin_data.get("gcPin")
                
                if second_fresh_pin:
                    if second_fresh_pin != fresh_pin:
                        self.log_result("PIN Uniqueness", True, f"New PIN '{second_fresh_pin}' is different from previous PIN '{fresh_pin}'")
                        print(f"   🔑 New PIN: {second_fresh_pin}")
                        print(f"   🔑 Previous PIN: {fresh_pin}")
                        print(f"   ✅ PINs are unique!")
                        
                        # Bonus: Test that the new PIN works
                        print(f"\n🎯 Bonus: Test that new PIN '{second_fresh_pin}' works")
                        login_data = {
                            "projectId": project_id,
                            "pin": second_fresh_pin
                        }
                        
                        login_response = self.session.post(
                            f"{self.base_url}/gc/login-simple",
                            json=login_data,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if login_response.status_code == 200:
                            login_result = login_response.json()
                            if login_result.get("success"):
                                self.log_result("New PIN Login", True, f"New PIN '{second_fresh_pin}' works correctly")
                                print(f"   ✅ New PIN login successful!")
                            else:
                                self.log_result("New PIN Login", False, f"New PIN login failed: {login_result.get('message', 'Unknown error')}")
                        else:
                            self.log_result("New PIN Login", False, f"New PIN login HTTP {login_response.status_code}", login_response)
                        
                    else:
                        self.log_result("PIN Uniqueness", False, f"New PIN '{second_fresh_pin}' is the same as previous PIN '{fresh_pin}' - PINs should be unique")
                        return False
                else:
                    self.log_result("PIN Uniqueness", False, "No PIN returned in second generation", response)
                    return False
            else:
                self.log_result("PIN Uniqueness", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("PIN Uniqueness", False, str(e))
            return False
        
        return True
    
    def test_additional_project_verification(self):
        """Test the second project ID mentioned in the review"""
        print("\n🔍 Additional Project Verification")
        print("=" * 40)
        
        project_id = "68cc802f8d44fcd8015b39b9"
        
        print(f"\n📍 Testing project {project_id}")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                pin = pin_data.get("gcPin")
                project_name = pin_data.get("projectName", "Unknown")
                
                if pin:
                    self.log_result("Additional Project PIN", True, f"Project '{project_name}' has PIN '{pin}'")
                    print(f"   🔑 PIN: {pin}")
                    print(f"   📋 Project: {project_name}")
                    
                    # Test login with this PIN too
                    login_data = {
                        "projectId": project_id,
                        "pin": pin
                    }
                    
                    login_response = self.session.post(
                        f"{self.base_url}/gc/login-simple",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        if login_result.get("success"):
                            self.log_result("Additional Project Login", True, f"Login successful for project '{project_name}'")
                        else:
                            self.log_result("Additional Project Login", False, f"Login failed: {login_result.get('message', 'Unknown error')}")
                    else:
                        self.log_result("Additional Project Login", False, f"Login HTTP {login_response.status_code}", login_response)
                else:
                    self.log_result("Additional Project PIN", False, "No PIN returned", response)
            else:
                self.log_result("Additional Project PIN", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Additional Project PIN", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 GC PIN SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            print(f"\n❌ FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"   • {error}")
        
        if success_rate == 100:
            print(f"\n🎉 ALL TESTS PASSED! The PIN system is working perfectly!")
            print(f"✅ Users can generate fresh PINs and use them immediately")
            print(f"✅ Old PINs are properly invalidated after use")
            print(f"✅ Each PIN generation creates unique PINs")
            print(f"✅ The system provides proper security with single-use PINs")
        else:
            print(f"\n⚠️  Some tests failed. Please review the errors above.")
        
        return success_rate == 100

def main():
    """Main test execution"""
    print("🚀 Starting GC PIN System Final Verification Test")
    print("This test will prove the PIN system works correctly for users")
    
    tester = PINSystemTester()
    
    # Run the comprehensive PIN system test
    success = tester.test_pin_system_comprehensive()
    
    # Test additional project for completeness
    tester.test_additional_project_verification()
    
    # Print summary
    all_passed = tester.print_summary()
    
    if all_passed:
        print(f"\n✅ CONCLUSION: The PIN system is fully operational!")
        print(f"Users just need to use fresh PINs immediately after generation.")
        sys.exit(0)
    else:
        print(f"\n❌ CONCLUSION: Issues found in PIN system.")
        sys.exit(1)

if __name__ == "__main__":
    main()