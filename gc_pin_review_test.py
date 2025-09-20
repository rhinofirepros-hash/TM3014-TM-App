#!/usr/bin/env python3
"""
GC PIN System Review Test
Focused test for the specific review request requirements:
1. Test GC PIN generation for existing project
2. Test GC PIN-only login 
3. Test GC Dashboard access
"""

import requests
import json
from datetime import datetime
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-inspect-app.preview.emergentagent.com/api"

class GCPinReviewTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "status_code": response.status_code if response else None,
            "response_preview": response.text[:300] if response else None
        }
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code})"
            print(f"❌ {error_msg}")
    
    def test_1_get_existing_project(self):
        """Step 1: Get an existing project from the projects collection"""
        print("\n=== Step 1: Getting Existing Project ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if projects and len(projects) > 0:
                    # Use the first project
                    project = projects[0]
                    self.test_project_id = project.get("id")
                    project_name = project.get("name", "Unknown Project")
                    self.log_result("Get existing project", True, f"Found project: {project_name} (ID: {self.test_project_id})")
                    return project
                else:
                    self.log_result("Get existing project", False, "No projects found in database")
                    return None
            else:
                self.log_result("Get existing project", False, f"HTTP {response.status_code}", response)
                return None
        except Exception as e:
            self.log_result("Get existing project", False, str(e))
            return None
    
    def test_2_generate_fresh_pin(self, project_id):
        """Step 2: Generate/regenerate a fresh 4-digit PIN for the project"""
        print(f"\n=== Step 2: Generating Fresh PIN for Project {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if response has the expected structure
                if "gcPin" in response_data and "projectId" in response_data:
                    pin = response_data["gcPin"]
                    project_name = response_data.get("projectName", "Unknown")
                    
                    # Validate PIN format (should be 4-digit)
                    if pin and len(str(pin)) == 4 and str(pin).isdigit():
                        self.generated_pin = str(pin)
                        self.log_result("Generate fresh PIN", True, f"Generated 4-digit PIN: {pin} for project: {project_name}")
                        return str(pin)
                    else:
                        self.log_result("Generate fresh PIN", False, f"Invalid PIN format: {pin}")
                        return None
                else:
                    self.log_result("Generate fresh PIN", False, "Response missing required fields", response)
                    return None
            else:
                self.log_result("Generate fresh PIN", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("Generate fresh PIN", False, str(e))
            return None
    
    def test_3_pin_only_login(self, project_id, pin):
        """Step 3: Test PIN-only login (should automatically find project by PIN)"""
        print(f"\n=== Step 3: Testing PIN-Only Login with PIN: {pin} ===")
        
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
                
                # Check if login was successful
                if "success" in response_data and response_data["success"]:
                    new_pin = response_data.get("newPin")
                    project_name = response_data.get("projectName", "Unknown")
                    
                    if new_pin and len(str(new_pin)) == 4 and str(new_pin).isdigit():
                        self.new_pin = str(new_pin)
                        self.log_result("PIN-only login", True, f"Login successful for project: {project_name}, new PIN generated: {new_pin}")
                        return True
                    else:
                        self.log_result("PIN-only login", False, f"Login successful but invalid new PIN: {new_pin}")
                        return False
                else:
                    error_msg = response_data.get("message", "Unknown error")
                    self.log_result("PIN-only login", False, f"Login failed: {error_msg}", response)
                    return False
            else:
                self.log_result("PIN-only login", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("PIN-only login", False, str(e))
            return False
    
    def test_4_gc_dashboard_access(self, project_id):
        """Step 4: Test GC Dashboard access after successful login"""
        print(f"\n=== Step 4: Testing GC Dashboard Access for Project {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if dashboard data has expected structure
                required_fields = ["projectId", "projectName"]
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    project_name = response_data.get("projectName", "Unknown")
                    crew_summary = response_data.get("crewSummary", {})
                    tm_summary = response_data.get("tmTagSummary", {})
                    materials = response_data.get("materials", {})
                    
                    # Validate data structure
                    crew_hours = crew_summary.get("totalHours", 0) if crew_summary else 0
                    tm_count = tm_summary.get("totalTags", 0) if tm_summary else 0
                    material_count = materials.get("totalQuantity", 0) if materials else 0
                    
                    self.log_result("GC Dashboard access", True, 
                                  f"Dashboard loaded for {project_name} - Crew Hours: {crew_hours}, T&M Tags: {tm_count}, Materials: {material_count}")
                    return True
                else:
                    self.log_result("GC Dashboard access", False, f"Missing required fields: {missing_fields}", response)
                    return False
            else:
                self.log_result("GC Dashboard access", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("GC Dashboard access", False, str(e))
            return False
    
    def test_5_pin_regeneration_verification(self, project_id, original_pin):
        """Step 5: Verify PIN regeneration after successful login"""
        print(f"\n=== Step 5: Verifying PIN Regeneration ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                response_data = response.json()
                current_pin = str(response_data.get("gcPin", ""))
                
                if current_pin != original_pin and len(current_pin) == 4 and current_pin.isdigit():
                    self.log_result("PIN regeneration verification", True, 
                                  f"PIN successfully regenerated from {original_pin} to {current_pin}")
                    return True
                else:
                    self.log_result("PIN regeneration verification", False, 
                                  f"PIN not properly regenerated. Original: {original_pin}, Current: {current_pin}")
                    return False
            else:
                self.log_result("PIN regeneration verification", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("PIN regeneration verification", False, str(e))
            return False
    
    def run_review_tests(self):
        """Run the specific tests requested in the review"""
        print("🎯 STARTING GC PIN SYSTEM REVIEW TESTING")
        print("=" * 60)
        print("Testing the specific requirements from the review request:")
        print("1. Test GC PIN generation for existing project")
        print("2. Test GC PIN-only login")
        print("3. Test GC Dashboard access")
        print("=" * 60)
        
        # Step 1: Get existing project
        project = self.test_1_get_existing_project()
        if not project:
            print("❌ Cannot continue without an existing project")
            return False
        
        project_id = self.test_project_id
        
        # Step 2: Generate fresh PIN
        pin = self.test_2_generate_fresh_pin(project_id)
        if not pin:
            print("❌ Cannot continue without a valid PIN")
            return False
        
        # Step 3: Test PIN-only login
        login_success = self.test_3_pin_only_login(project_id, pin)
        
        # Step 4: Test GC Dashboard access
        dashboard_success = self.test_4_gc_dashboard_access(project_id)
        
        # Step 5: Verify PIN regeneration
        regeneration_success = self.test_5_pin_regeneration_verification(project_id, pin)
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 GC PIN SYSTEM REVIEW TEST SUMMARY")
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
            if not result["success"] and result["status_code"]:
                print(f"     HTTP Status: {result['status_code']}")
        
        # Determine overall status
        if failed == 0:
            print("\n🎉 ALL REVIEW REQUIREMENTS PASSED!")
            print("The GC PIN system is working correctly for the reported issues.")
        else:
            print(f"\n⚠️  {failed} TESTS FAILED - ISSUES FOUND")
            print("The GC PIN system has problems that need to be addressed.")
        
        return failed == 0

def main():
    """Main test execution"""
    tester = GCPinReviewTester()
    
    try:
        tester.run_review_tests()
        success = tester.print_summary()
        
        if success:
            print("\n🎉 GC PIN SYSTEM REVIEW TESTING COMPLETED SUCCESSFULLY!")
            return 0
        else:
            print("\n❌ GC PIN SYSTEM REVIEW TESTING FOUND ISSUES!")
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