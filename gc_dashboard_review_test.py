#!/usr/bin/env python3
"""
GC Dashboard Review Test - Comprehensive Testing
Tests the complete GC dashboard workflow as requested in the review:
1. Generate fresh PIN and return it for manual frontend testing
2. Test GC login with secure PIN validation endpoint
3. Test GC dashboard with proper data structure
4. Verify inspection data is returned as dictionary (not list)
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://rhino-ui-sync.preview.emergentagent.com/api"

class GCDashboardReviewTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "pin_generation": {"passed": 0, "failed": 0, "errors": []},
            "gc_login": {"passed": 0, "failed": 0, "errors": []},
            "gc_dashboard": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        self.fresh_pins = []  # Store fresh PINs for manual testing
        
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
    
    def generate_fresh_pin_for_project(self, project_id):
        """Generate a fresh PIN for a specific project"""
        print(f"\n=== Generating Fresh PIN for Project {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                
                # Verify response structure
                required_fields = ["projectId", "projectName", "gcPin", "pinUsed"]
                missing_fields = [field for field in required_fields if field not in pin_data]
                
                if not missing_fields:
                    pin = pin_data['gcPin']
                    project_name = pin_data['projectName']
                    pin_used = pin_data['pinUsed']
                    
                    # Verify PIN format (4 digits)
                    if isinstance(pin, str) and len(pin) == 4 and pin.isdigit():
                        self.log_result("pin_generation", f"Fresh PIN generation - {project_id}", True, 
                                      f"Generated PIN: {pin} for project '{project_name}' (Used: {pin_used})")
                        
                        # Store for manual testing
                        self.fresh_pins.append({
                            "project_id": project_id,
                            "project_name": project_name,
                            "pin": pin,
                            "pin_used": pin_used
                        })
                        
                        return pin_data
                    else:
                        self.log_result("pin_generation", f"Fresh PIN generation - {project_id}", False, 
                                      f"Invalid PIN format: {pin} (expected 4-digit string)")
                else:
                    self.log_result("pin_generation", f"Fresh PIN generation - {project_id}", False, 
                                  f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("pin_generation", f"Fresh PIN generation - {project_id}", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("pin_generation", f"Fresh PIN generation - {project_id}", False, str(e))
        
        return None
    
    def test_secure_gc_login(self, pin):
        """Test the secure GC PIN validation endpoint"""
        print(f"\n=== Testing Secure GC Login with PIN: {pin} ===")
        
        try:
            # Test the new secure PIN validation endpoint
            login_data = {"pin": pin}
            
            response = self.session.post(
                f"{self.base_url}/gc/validate-pin",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                
                # Verify response structure
                expected_fields = ["success", "projectId", "projectName", "message"]
                missing_fields = [field for field in expected_fields if field not in login_result]
                
                if not missing_fields and login_result.get("success"):
                    project_id = login_result["projectId"]
                    project_name = login_result["projectName"]
                    
                    self.log_result("gc_login", f"Secure PIN validation - {pin}", True, 
                                  f"Login successful for project '{project_name}' (ID: {project_id})")
                    
                    # Verify PIN regeneration (old PIN should now be invalid)
                    self.test_pin_regeneration(pin, project_id)
                    
                    return login_result
                else:
                    self.log_result("gc_login", f"Secure PIN validation - {pin}", False, 
                                  f"Login failed or missing fields: {missing_fields}", response)
            elif response.status_code == 401:
                # This might be expected if PIN was already used
                self.log_result("gc_login", f"Secure PIN validation - {pin}", False, 
                              "PIN invalid or already used (401)", response)
            else:
                self.log_result("gc_login", f"Secure PIN validation - {pin}", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", f"Secure PIN validation - {pin}", False, str(e))
        
        return None
    
    def test_pin_regeneration(self, old_pin, project_id):
        """Test that PIN regeneration works after successful login"""
        print(f"\n=== Testing PIN Regeneration for Project {project_id} ===")
        
        try:
            # Get the new PIN after login
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                new_pin = pin_data.get('gcPin')
                
                if new_pin and new_pin != old_pin:
                    self.log_result("gc_login", f"PIN regeneration - {project_id}", True, 
                                  f"PIN successfully regenerated: {old_pin} → {new_pin}")
                    
                    # Test that old PIN is now invalid
                    old_pin_test = self.session.post(
                        f"{self.base_url}/gc/validate-pin",
                        json={"pin": old_pin},
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if old_pin_test.status_code == 401:
                        self.log_result("gc_login", f"Old PIN rejection - {old_pin}", True, 
                                      "Old PIN correctly rejected after regeneration")
                    else:
                        self.log_result("gc_login", f"Old PIN rejection - {old_pin}", False, 
                                      "Old PIN should be rejected but wasn't", old_pin_test)
                    
                    return new_pin
                else:
                    self.log_result("gc_login", f"PIN regeneration - {project_id}", False, 
                                  f"PIN not regenerated: old={old_pin}, new={new_pin}")
            else:
                self.log_result("gc_login", f"PIN regeneration - {project_id}", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_login", f"PIN regeneration - {project_id}", False, str(e))
        
        return None
    
    def test_gc_dashboard_data(self, project_id):
        """Test the GC dashboard endpoint with comprehensive data verification"""
        print(f"\n=== Testing GC Dashboard Data for Project {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Verify main dashboard structure
                expected_main_fields = [
                    "projectId", "projectName", "crewSummary", "tmTagSummary", 
                    "phases", "inspections", "narrative", "overallProgress", "lastUpdated"
                ]
                missing_main_fields = [field for field in expected_main_fields if field not in dashboard_data]
                
                if not missing_main_fields:
                    self.log_result("gc_dashboard", f"Dashboard structure - {project_id}", True, 
                                  "All main dashboard fields present")
                    
                    # Test crew summary structure
                    self.test_crew_summary_structure(dashboard_data.get("crewSummary", {}), project_id)
                    
                    # Test T&M tag summary structure
                    self.test_tm_tag_summary_structure(dashboard_data.get("tmTagSummary", {}), project_id)
                    
                    # Test inspection status structure (CRITICAL: must be dictionary, not list)
                    self.test_inspection_status_structure(dashboard_data.get("inspections", {}), project_id)
                    
                    # Test project phases structure
                    self.test_project_phases_structure(dashboard_data.get("phases", {}), project_id)
                    
                    # Test narrative structure
                    self.test_narrative_structure(dashboard_data.get("narrative", {}), project_id)
                    
                    return dashboard_data
                else:
                    self.log_result("gc_dashboard", f"Dashboard structure - {project_id}", False, 
                                  f"Missing main fields: {missing_main_fields}", response)
            elif response.status_code == 404:
                self.log_result("gc_dashboard", f"Dashboard data - {project_id}", False, 
                              "Project not found (404)", response)
            else:
                self.log_result("gc_dashboard", f"Dashboard data - {project_id}", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_dashboard", f"Dashboard data - {project_id}", False, str(e))
        
        return None
    
    def test_crew_summary_structure(self, crew_summary, project_id):
        """Test crew activity summary structure"""
        print(f"  → Testing Crew Summary Structure for Project {project_id}")
        
        expected_fields = ["totalHours", "totalDays", "activeCrewMembers"]
        missing_fields = [field for field in expected_fields if field not in crew_summary]
        
        if not missing_fields:
            total_hours = crew_summary.get("totalHours", 0)
            total_days = crew_summary.get("totalDays", 0)
            active_crew = crew_summary.get("activeCrewMembers", 0)
            
            self.log_result("gc_dashboard", f"Crew summary structure - {project_id}", True, 
                          f"Hours: {total_hours}, Days: {total_days}, Active Crew: {active_crew}")
        else:
            self.log_result("gc_dashboard", f"Crew summary structure - {project_id}", False, 
                          f"Missing crew summary fields: {missing_fields}")
    
    def test_tm_tag_summary_structure(self, tm_tag_summary, project_id):
        """Test T&M tag summary structure"""
        print(f"  → Testing T&M Tag Summary Structure for Project {project_id}")
        
        expected_fields = ["totalTags", "totalHours", "recentTagTitles"]
        missing_fields = [field for field in expected_fields if field not in tm_tag_summary]
        
        if not missing_fields:
            total_tags = tm_tag_summary.get("totalTags", 0)
            total_hours = tm_tag_summary.get("totalHours", 0)
            recent_titles = tm_tag_summary.get("recentTagTitles", [])
            
            self.log_result("gc_dashboard", f"T&M tag summary structure - {project_id}", True, 
                          f"Tags: {total_tags}, Hours: {total_hours}, Recent: {len(recent_titles)} titles")
        else:
            self.log_result("gc_dashboard", f"T&M tag summary structure - {project_id}", False, 
                          f"Missing T&M tag summary fields: {missing_fields}")
    
    def test_inspection_status_structure(self, inspections, project_id):
        """Test inspection status structure - CRITICAL: Must be dictionary, not list"""
        print(f"  → Testing Inspection Status Structure for Project {project_id}")
        
        # CRITICAL CHECK: Verify inspections is a dictionary, not a list
        if isinstance(inspections, dict):
            self.log_result("gc_dashboard", f"Inspection data type - {project_id}", True, 
                          "Inspection data correctly returned as dictionary")
            
            # Check for actual API response structure
            expected_fields = ["rough_inspection_status", "final_inspection_status"]
            missing_fields = [field for field in expected_fields if field not in inspections]
            
            if not missing_fields:
                rough_status = inspections.get("rough_inspection_status", "unknown")
                final_status = inspections.get("final_inspection_status", "unknown")
                rough_date = inspections.get("rough_inspection_date")
                final_date = inspections.get("final_inspection_date")
                
                self.log_result("gc_dashboard", f"Inspection status structure - {project_id}", True, 
                              f"Rough: {rough_status} ({rough_date or 'No date'}), Final: {final_status} ({final_date or 'No date'})")
            else:
                self.log_result("gc_dashboard", f"Inspection status structure - {project_id}", False, 
                              f"Missing main inspection fields: {missing_fields}")
        else:
            # CRITICAL FAILURE: Inspection data is not a dictionary
            data_type = type(inspections).__name__
            self.log_result("gc_dashboard", f"Inspection data type - {project_id}", False, 
                          f"CRITICAL: Inspection data returned as {data_type}, expected dictionary")
    
    def test_project_phases_structure(self, phases, project_id):
        """Test project phases structure"""
        print(f"  → Testing Project Phases Structure for Project {project_id}")
        
        # Check if phases is a list (actual API response) or dict
        if isinstance(phases, list):
            if phases:
                phase_info = []
                for phase in phases:
                    if isinstance(phase, dict):
                        phase_name = phase.get("phase", "unknown")
                        percent_complete = phase.get("percentComplete", 0)
                        phase_info.append(f"{phase_name}: {percent_complete}%")
                
                self.log_result("gc_dashboard", f"Project phases structure - {project_id}", True, 
                              f"Phases: {', '.join(phase_info)}")
            else:
                self.log_result("gc_dashboard", f"Project phases structure - {project_id}", True, 
                              "No phases defined for project")
        elif isinstance(phases, dict):
            # Handle dict format if API changes
            phase_statuses = []
            for phase_name, phase_data in phases.items():
                if isinstance(phase_data, dict) and "status" in phase_data:
                    phase_statuses.append(f"{phase_name}: {phase_data['status']}")
            
            self.log_result("gc_dashboard", f"Project phases structure - {project_id}", True, 
                          f"Phases: {', '.join(phase_statuses)}")
        else:
            self.log_result("gc_dashboard", f"Project phases structure - {project_id}", False, 
                          f"Unexpected phases data type: {type(phases).__name__}")
    
    def test_narrative_structure(self, narrative, project_id):
        """Test narrative structure"""
        print(f"  → Testing Narrative Structure for Project {project_id}")
        
        # Check if narrative is a string (actual API response) or dict
        if isinstance(narrative, str):
            content_length = len(narrative)
            self.log_result("gc_dashboard", f"Narrative structure - {project_id}", True, 
                          f"Narrative content: {content_length} chars - '{narrative[:50]}{'...' if len(narrative) > 50 else ''}'")
        elif isinstance(narrative, dict):
            # Handle dict format if API changes
            expected_fields = ["lastUpdated", "content", "author"]
            missing_fields = [field for field in expected_fields if field not in narrative]
            
            if not missing_fields:
                last_updated = narrative.get("lastUpdated", "unknown")
                content_length = len(narrative.get("content", ""))
                author = narrative.get("author", "unknown")
                
                self.log_result("gc_dashboard", f"Narrative structure - {project_id}", True, 
                              f"Author: {author}, Content: {content_length} chars, Updated: {last_updated}")
            else:
                self.log_result("gc_dashboard", f"Narrative structure - {project_id}", False, 
                              f"Missing narrative fields: {missing_fields}")
        else:
            self.log_result("gc_dashboard", f"Narrative structure - {project_id}", False, 
                          f"Unexpected narrative data type: {type(narrative).__name__}")
    
    def run_comprehensive_gc_dashboard_test(self):
        """Run the complete GC dashboard workflow test as requested in review"""
        print("🎯 STARTING COMPREHENSIVE GC DASHBOARD REVIEW TEST")
        print("=" * 60)
        
        # Step 1: Test basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting test.")
            return False
        
        # Step 2: Get available projects
        print("\n=== Getting Available Projects ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if not projects:
                    print("❌ No projects found in system. Cannot test GC dashboard.")
                    return False
                
                print(f"✅ Found {len(projects)} projects in system")
                
                # Show first few projects for reference
                print("Available projects:")
                for i, project in enumerate(projects[:5]):
                    print(f"  {i+1}. ID: {project.get('id')}, Name: {project.get('name', 'Unknown')}")
                
                # Use specific project IDs from review request if available
                test_project_ids = ["68cc802f8d44fcd8015b39b8", "68cc802f8d44fcd8015b39b9"]
                available_project_ids = [p.get('id') for p in projects]
                
                # Find which test project IDs exist
                existing_test_projects = [pid for pid in test_project_ids if pid in available_project_ids]
                
                if existing_test_projects:
                    test_projects = existing_test_projects
                    print(f"✅ Using specific review request project IDs: {test_projects}")
                else:
                    # Use first available project
                    test_projects = [projects[0]['id']]
                    print(f"⚠️  Review request project IDs not found. Using first available: {test_projects}")
                
            else:
                print(f"❌ Failed to get projects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return False
        
        # Step 3: Generate fresh PINs and test complete workflow
        for project_id in test_projects:
            print(f"\n{'='*60}")
            print(f"🎯 TESTING PROJECT: {project_id}")
            print(f"{'='*60}")
            
            # Step 3a: Generate fresh PIN
            pin_data = self.generate_fresh_pin_for_project(project_id)
            if not pin_data:
                print(f"❌ Failed to generate PIN for project {project_id}")
                continue
            
            fresh_pin = pin_data['gcPin']
            
            # Step 3b: Test secure GC login with fresh PIN
            login_result = self.test_secure_gc_login(fresh_pin)
            if not login_result:
                print(f"❌ Failed to login with PIN {fresh_pin} for project {project_id}")
                continue
            
            # Step 3c: Test GC dashboard data
            dashboard_data = self.test_gc_dashboard_data(project_id)
            if not dashboard_data:
                print(f"❌ Failed to get dashboard data for project {project_id}")
                continue
            
            print(f"✅ Complete workflow test successful for project {project_id}")
        
        # Step 4: Display fresh PINs for manual frontend testing
        self.display_fresh_pins_for_manual_testing()
        
        # Step 5: Display test summary
        self.display_test_summary()
        
        return True
    
    def display_fresh_pins_for_manual_testing(self):
        """Display fresh PINs for manual frontend testing"""
        print(f"\n{'='*60}")
        print("🎯 FRESH PINS FOR MANUAL FRONTEND TESTING")
        print(f"{'='*60}")
        
        if self.fresh_pins:
            print("The following fresh PINs are ready for manual frontend testing:")
            print()
            for i, pin_info in enumerate(self.fresh_pins, 1):
                print(f"{i}. PROJECT: {pin_info['project_name']}")
                print(f"   ID: {pin_info['project_id']}")
                print(f"   PIN: {pin_info['pin']}")
                print(f"   STATUS: {'Used' if pin_info['pin_used'] else 'Fresh'}")
                print()
            
            # Highlight the first fresh PIN for immediate use
            if self.fresh_pins:
                first_pin = self.fresh_pins[0]
                print("🎯 RECOMMENDED FOR IMMEDIATE TESTING:")
                print(f"   Project: {first_pin['project_name']}")
                print(f"   PIN: {first_pin['pin']}")
                print(f"   Project ID: {first_pin['project_id']}")
        else:
            print("❌ No fresh PINs were generated successfully.")
    
    def display_test_summary(self):
        """Display comprehensive test summary"""
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*60}")
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅" if failed == 0 else "❌"
            print(f"{status} {category.upper()}: {passed} passed, {failed} failed")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"    ❌ {error}")
        
        print(f"\n{'='*60}")
        total_tests = total_passed + total_failed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! GC Dashboard system is fully operational.")
        else:
            print(f"⚠️  {total_failed} tests failed. Review errors above.")
        
        print(f"{'='*60}")

def main():
    """Main test execution"""
    print("🚀 GC Dashboard Review Test - Starting Comprehensive Testing")
    print("This test covers the complete GC dashboard workflow as requested in the review.")
    
    tester = GCDashboardReviewTester()
    success = tester.run_comprehensive_gc_dashboard_test()
    
    if success:
        print("\n🎉 GC Dashboard Review Test completed successfully!")
    else:
        print("\n❌ GC Dashboard Review Test encountered critical errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()