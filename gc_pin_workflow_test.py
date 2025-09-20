#!/usr/bin/env python3
"""
CRITICAL END-TO-END GC PIN SYSTEM TEST
Production Readiness Test for tm.rhinofirepro.com

This test performs comprehensive validation of the complete GC PIN workflow:
1. Generate Fresh PIN: Create new 4-digit PIN for a project
2. Verify PIN Storage: Confirm PIN is stored in database with gc_pin_used: false  
3. Test PIN Validation: Use /api/gc/validate-pin endpoint with the fresh PIN
4. Verify PIN Regeneration: Confirm old PIN becomes invalid after successful login
5. Test GC Dashboard Access: Verify /api/gc/dashboard/{project_id} returns data
"""

import requests
import json
from datetime import datetime
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://tm.rhinofirepro.com/api"

class GCPinWorkflowTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "pin_generation": {"passed": 0, "failed": 0, "errors": []},
            "pin_validation": {"passed": 0, "failed": 0, "errors": []},
            "pin_regeneration": {"passed": 0, "failed": 0, "errors": []},
            "dashboard_access": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        self.fresh_pins = []  # Store fresh PINs for manual frontend testing
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True, "API is accessible")
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def get_existing_projects(self):
        """Get existing projects to test with"""
        print("\n=== Getting Existing Projects ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    self.log_result("general", "Get existing projects", True, f"Found {len(projects)} projects")
                    return projects
                else:
                    self.log_result("general", "Get existing projects", False, "No projects found in system")
                    return []
            else:
                self.log_result("general", "Get existing projects", False, f"HTTP {response.status_code}", response)
                return []
        except Exception as e:
            self.log_result("general", "Get existing projects", False, str(e))
            return []
    
    def test_fresh_pin_generation(self, project_id):
        """Test Step 1: Generate Fresh PIN for a project"""
        print(f"\n=== STEP 1: Generate Fresh PIN for Project {project_id} ===")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                
                # Verify response structure
                required_fields = ["projectId", "projectName", "gcPin", "pinUsed"]
                missing_fields = [field for field in required_fields if field not in pin_data]
                
                if not missing_fields:
                    pin = pin_data["gcPin"]
                    project_name = pin_data["projectName"]
                    pin_used = pin_data["pinUsed"]
                    
                    # Verify PIN format (4-digit)
                    if len(pin) == 4 and pin.isdigit():
                        # Verify PIN is fresh (not used)
                        if pin_used == False:
                            self.log_result("pin_generation", "Fresh PIN generation", True, 
                                          f"Generated fresh PIN '{pin}' for project '{project_name}'")
                            
                            # Store for manual testing
                            self.fresh_pins.append({
                                "project_id": project_id,
                                "project_name": project_name,
                                "pin": pin,
                                "pin_used": pin_used
                            })
                            
                            return pin_data
                        else:
                            self.log_result("pin_generation", "Fresh PIN generation", False, 
                                          f"PIN '{pin}' is already used (pinUsed: {pin_used})")
                    else:
                        self.log_result("pin_generation", "Fresh PIN generation", False, 
                                      f"Invalid PIN format: '{pin}' (should be 4 digits)")
                else:
                    self.log_result("pin_generation", "Fresh PIN generation", False, 
                                  f"Missing required fields: {missing_fields}", response)
            else:
                self.log_result("pin_generation", "Fresh PIN generation", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_generation", "Fresh PIN generation", False, str(e))
        
        return None
    
    def test_pin_storage_verification(self, project_id, expected_pin):
        """Test Step 2: Verify PIN is stored in database with gc_pin_used: false"""
        print(f"\n=== STEP 2: Verify PIN Storage for Project {project_id} ===")
        try:
            # Get project data to verify PIN storage
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                target_project = None
                
                for project in projects:
                    if project.get("id") == project_id:
                        target_project = project
                        break
                
                if target_project:
                    stored_pin = target_project.get("gc_pin")
                    pin_used = target_project.get("gc_pin_used")
                    
                    if stored_pin == expected_pin:
                        if pin_used == False:
                            self.log_result("pin_generation", "PIN storage verification", True, 
                                          f"PIN '{stored_pin}' correctly stored with gc_pin_used: false")
                            return True
                        else:
                            self.log_result("pin_generation", "PIN storage verification", False, 
                                          f"PIN stored but gc_pin_used is {pin_used} (should be false)")
                    else:
                        self.log_result("pin_generation", "PIN storage verification", False, 
                                      f"PIN mismatch - expected '{expected_pin}', stored '{stored_pin}'")
                else:
                    self.log_result("pin_generation", "PIN storage verification", False, 
                                  f"Project {project_id} not found in projects list")
            else:
                self.log_result("pin_generation", "PIN storage verification", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_generation", "PIN storage verification", False, str(e))
        
        return False
    
    def test_pin_validation_endpoint(self, pin):
        """Test Step 3: Test PIN Validation using /api/gc/validate-pin endpoint"""
        print(f"\n=== STEP 3: Test PIN Validation with PIN '{pin}' ===")
        try:
            validation_data = {"pin": pin}
            
            response = self.session.post(
                f"{self.base_url}/gc/validate-pin",
                json=validation_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                validation_result = response.json()
                
                # Verify response structure
                required_fields = ["success", "projectId", "projectName"]
                missing_fields = [field for field in required_fields if field not in validation_result]
                
                if not missing_fields:
                    if validation_result.get("success") == True:
                        project_id = validation_result["projectId"]
                        project_name = validation_result["projectName"]
                        
                        self.log_result("pin_validation", "PIN validation endpoint", True, 
                                      f"PIN '{pin}' successfully validated for project '{project_name}' (ID: {project_id})")
                        
                        return validation_result
                    else:
                        self.log_result("pin_validation", "PIN validation endpoint", False, 
                                      f"Validation failed for PIN '{pin}' - success: false")
                else:
                    self.log_result("pin_validation", "PIN validation endpoint", False, 
                                  f"Missing required fields in response: {missing_fields}", response)
            elif response.status_code == 401:
                self.log_result("pin_validation", "PIN validation endpoint", False, 
                              f"PIN '{pin}' rejected with 401 Unauthorized", response)
            else:
                self.log_result("pin_validation", "PIN validation endpoint", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_validation", "PIN validation endpoint", False, str(e))
        
        return None
    
    def test_pin_regeneration(self, project_id, old_pin):
        """Test Step 4: Verify PIN Regeneration - old PIN becomes invalid after successful login"""
        print(f"\n=== STEP 4: Test PIN Regeneration for Project {project_id} ===")
        
        # First, get the new PIN after validation
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                new_pin = pin_data["gcPin"]
                
                if new_pin != old_pin:
                    self.log_result("pin_regeneration", "PIN regeneration", True, 
                                  f"PIN successfully regenerated from '{old_pin}' to '{new_pin}'")
                    
                    # Test that old PIN is now invalid
                    old_pin_validation = {"pin": old_pin}
                    
                    old_pin_response = self.session.post(
                        f"{self.base_url}/gc/validate-pin",
                        json=old_pin_validation,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if old_pin_response.status_code == 401:
                        self.log_result("pin_regeneration", "Old PIN invalidation", True, 
                                      f"Old PIN '{old_pin}' correctly rejected with 401")
                    else:
                        self.log_result("pin_regeneration", "Old PIN invalidation", False, 
                                      f"Old PIN '{old_pin}' should be rejected but got status {old_pin_response.status_code}")
                    
                    # Test that new PIN works
                    new_pin_validation = {"pin": new_pin}
                    
                    new_pin_response = self.session.post(
                        f"{self.base_url}/gc/validate-pin",
                        json=new_pin_validation,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if new_pin_response.status_code == 200:
                        self.log_result("pin_regeneration", "New PIN validation", True, 
                                      f"New PIN '{new_pin}' works correctly")
                        return new_pin
                    else:
                        self.log_result("pin_regeneration", "New PIN validation", False, 
                                      f"New PIN '{new_pin}' failed validation with status {new_pin_response.status_code}")
                else:
                    self.log_result("pin_regeneration", "PIN regeneration", False, 
                                  f"PIN not regenerated - still '{old_pin}'")
            else:
                self.log_result("pin_regeneration", "PIN regeneration", False, 
                              f"Could not get new PIN - HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_regeneration", "PIN regeneration", False, str(e))
        
        return None
    
    def test_gc_dashboard_access(self, project_id):
        """Test Step 5: Test GC Dashboard Access - verify /api/gc/dashboard/{project_id} returns data"""
        print(f"\n=== STEP 5: Test GC Dashboard Access for Project {project_id} ===")
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Verify essential dashboard fields
                required_fields = ["projectId", "projectName", "crewSummary", "tmTagSummary"]
                missing_fields = [field for field in required_fields if field not in dashboard_data]
                
                if not missing_fields:
                    project_name = dashboard_data["projectName"]
                    crew_summary = dashboard_data["crewSummary"]
                    tm_tag_summary = dashboard_data["tmTagSummary"]
                    
                    # Verify data structure
                    crew_hours = crew_summary.get("totalHours", 0)
                    crew_days = crew_summary.get("totalDays", 0)
                    tm_tags_count = tm_tag_summary.get("totalTags", 0)
                    tm_hours = tm_tag_summary.get("totalHours", 0)
                    
                    self.log_result("dashboard_access", "GC dashboard access", True, 
                                  f"Dashboard accessible for '{project_name}' - Crew Hours: {crew_hours}, T&M Tags: {tm_tags_count}")
                    
                    # Verify additional dashboard components
                    if "phases" in dashboard_data and "inspections" in dashboard_data:
                        phases = dashboard_data["phases"]
                        inspections = dashboard_data["inspections"]
                        
                        self.log_result("dashboard_access", "Dashboard completeness", True, 
                                      f"Complete dashboard data - Phases: {len(phases)}, Inspections available")
                    else:
                        self.log_result("dashboard_access", "Dashboard completeness", False, 
                                      "Missing phases or inspections data")
                    
                    return dashboard_data
                else:
                    self.log_result("dashboard_access", "GC dashboard access", False, 
                                  f"Missing required dashboard fields: {missing_fields}", response)
            elif response.status_code == 404:
                self.log_result("dashboard_access", "GC dashboard access", False, 
                              f"Dashboard not found for project {project_id} - 404", response)
            else:
                self.log_result("dashboard_access", "GC dashboard access", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("dashboard_access", "GC dashboard access", False, str(e))
        
        return None
    
    def run_complete_workflow_test(self, project_id):
        """Run the complete GC PIN workflow test for a single project"""
        print(f"\n🎯 STARTING COMPLETE GC PIN WORKFLOW TEST FOR PROJECT: {project_id}")
        print("=" * 80)
        
        # Step 1: Generate Fresh PIN
        pin_data = self.test_fresh_pin_generation(project_id)
        if not pin_data:
            print(f"❌ WORKFLOW FAILED: Could not generate fresh PIN for project {project_id}")
            return False
        
        fresh_pin = pin_data["gcPin"]
        
        # Step 2: Verify PIN Storage
        if not self.test_pin_storage_verification(project_id, fresh_pin):
            print(f"❌ WORKFLOW FAILED: PIN storage verification failed for project {project_id}")
            return False
        
        # Step 3: Test PIN Validation
        validation_result = self.test_pin_validation_endpoint(fresh_pin)
        if not validation_result:
            print(f"❌ WORKFLOW FAILED: PIN validation failed for project {project_id}")
            return False
        
        # Step 4: Verify PIN Regeneration
        new_pin = self.test_pin_regeneration(project_id, fresh_pin)
        if not new_pin:
            print(f"❌ WORKFLOW FAILED: PIN regeneration failed for project {project_id}")
            return False
        
        # Step 5: Test GC Dashboard Access
        dashboard_data = self.test_gc_dashboard_access(project_id)
        if not dashboard_data:
            print(f"❌ WORKFLOW FAILED: GC dashboard access failed for project {project_id}")
            return False
        
        print(f"✅ COMPLETE WORKFLOW SUCCESS FOR PROJECT: {project_id}")
        print(f"   - Fresh PIN Generated: {fresh_pin}")
        print(f"   - PIN Regenerated To: {new_pin}")
        print(f"   - Dashboard Accessible: ✅")
        
        return True
    
    def run_all_tests(self):
        """Run comprehensive GC PIN workflow tests"""
        print("🎯 CRITICAL END-TO-END GC PIN SYSTEM TEST")
        print("Production Readiness Test for tm.rhinofirepro.com")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ CRITICAL FAILURE: Cannot connect to backend API")
            return False
        
        # Get existing projects
        projects = self.get_existing_projects()
        if not projects:
            print("❌ CRITICAL FAILURE: No projects found to test with")
            return False
        
        # Test with first few projects (limit to avoid overwhelming)
        test_projects = projects[:3]  # Test with first 3 projects
        successful_workflows = 0
        
        for project in test_projects:
            project_id = project.get("id")
            project_name = project.get("name", "Unknown")
            
            print(f"\n📋 Testing Project: {project_name} (ID: {project_id})")
            
            if self.run_complete_workflow_test(project_id):
                successful_workflows += 1
        
        # Print final results
        self.print_final_results(successful_workflows, len(test_projects))
        
        return successful_workflows == len(test_projects)
    
    def print_final_results(self, successful_workflows, total_projects):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎯 FINAL TEST RESULTS - GC PIN WORKFLOW")
        print("=" * 80)
        
        total_passed = sum(category["passed"] for category in self.test_results.values())
        total_failed = sum(category["failed"] for category in self.test_results.values())
        total_tests = total_passed + total_failed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   - Total Tests: {total_tests}")
        print(f"   - Passed: {total_passed}")
        print(f"   - Failed: {total_failed}")
        print(f"   - Success Rate: {success_rate:.1f}%")
        print(f"   - Successful Workflows: {successful_workflows}/{total_projects}")
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, results in self.test_results.items():
            if results["passed"] > 0 or results["failed"] > 0:
                category_total = results["passed"] + results["failed"]
                category_rate = (results["passed"] / category_total * 100) if category_total > 0 else 0
                print(f"   - {category.replace('_', ' ').title()}: {results['passed']}/{category_total} ({category_rate:.1f}%)")
        
        # Print fresh PINs for manual testing
        if self.fresh_pins:
            print(f"\n🔑 FRESH PINS FOR MANUAL FRONTEND TESTING:")
            for pin_info in self.fresh_pins:
                print(f"   - Project: {pin_info['project_name']}")
                print(f"     PIN: {pin_info['pin']}")
                print(f"     Project ID: {pin_info['project_id']}")
                print(f"     Status: Fresh (unused)")
                print()
        
        # Print any errors
        if total_failed > 0:
            print(f"\n❌ ERRORS ENCOUNTERED:")
            for category, results in self.test_results.items():
                if results["errors"]:
                    print(f"   {category.replace('_', ' ').title()}:")
                    for error in results["errors"]:
                        print(f"     - {error}")
        
        # Production readiness assessment
        print(f"\n🏭 PRODUCTION READINESS ASSESSMENT:")
        if successful_workflows == total_projects and total_failed == 0:
            print("   ✅ SYSTEM IS PRODUCTION READY")
            print("   ✅ All GC PIN workflows operational")
            print("   ✅ Backend endpoints fully functional")
            print("   ✅ Ready for deployment on tm.rhinofirepro.com")
        else:
            print("   ❌ SYSTEM NOT READY FOR PRODUCTION")
            print(f"   ❌ {total_failed} test failures detected")
            print("   ❌ Critical issues must be resolved before deployment")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = GCPinWorkflowTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()