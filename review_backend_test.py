#!/usr/bin/env python3
"""
Review Request Backend Testing
Tests the specific fixes mentioned in the review request:
1. Date Sync Issue - crew log to T&M tag sync dates
2. GC Access Management - PINs and access logs
3. Enhanced GC Dashboard - inspection data
4. Project Management with Inspections - inspection fields
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

class ReviewBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "date_sync": {"passed": 0, "failed": 0, "errors": []},
            "gc_access": {"passed": 0, "failed": 0, "errors": []},
            "gc_dashboard": {"passed": 0, "failed": 0, "errors": []},
            "project_inspections": {"passed": 0, "failed": 0, "errors": []}
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
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                print("✅ Backend connectivity: PASSED")
                return True
            else:
                print(f"❌ Backend connectivity: FAILED - Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connectivity: FAILED - {str(e)}")
            return False
    
    def test_date_sync_issue(self):
        """Test 1: Date Sync Issue - crew log to T&M tag sync dates consistency"""
        print("\n=== Testing Date Sync Issue Fix ===")
        
        # First, get or create a project
        try:
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code != 200:
                self.log_result("date_sync", "Get projects for sync test", False, f"HTTP {projects_response.status_code}", projects_response)
                return False
            
            projects = projects_response.json()
            if not projects:
                # Create a test project
                project_data = {
                    "name": "Date Sync Test Project",
                    "description": "Testing date sync between crew logs and T&M tags",
                    "client_company": "Test Company",
                    "gc_email": "test@company.com",
                    "contract_amount": 50000.00,
                    "labor_rate": 95.0,
                    "project_manager": "Jesus Garcia",
                    "start_date": datetime.now().isoformat(),
                    "address": "Test Address"
                }
                
                create_response = self.session.post(
                    f"{self.base_url}/projects",
                    json=project_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if create_response.status_code != 200:
                    self.log_result("date_sync", "Create project for sync test", False, f"HTTP {create_response.status_code}", create_response)
                    return False
                
                project = create_response.json()
                project_id = project["id"]
                self.log_result("date_sync", "Create project for sync test", True, f"Created project {project_id}")
            else:
                project = projects[0]
                project_id = project["id"]
                self.log_result("date_sync", "Get existing project for sync test", True, f"Using project {project_id}")
            
            # Create crew log with today's date
            today = datetime.now()
            crew_log_data = {
                "project_id": project_id,
                "date": today.isoformat(),
                "crew_members": [
                    {
                        "name": "Test Worker",
                        "st_hours": 8.0,
                        "ot_hours": 0.0,
                        "dt_hours": 0.0,
                        "pot_hours": 0.0,
                        "total_hours": 8.0
                    }
                ],
                "work_description": "Date sync test - crew log created today",
                "weather_conditions": "clear"
            }
            
            crew_log_response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if crew_log_response.status_code != 200:
                self.log_result("date_sync", "Create crew log with today's date", False, f"HTTP {crew_log_response.status_code}", crew_log_response)
                return False
            
            crew_log = crew_log_response.json()
            crew_log_id = crew_log["id"]
            self.log_result("date_sync", "Create crew log with today's date", True, f"Created crew log {crew_log_id} with date {today.strftime('%Y-%m-%d')}")
            
            # Wait for sync to complete
            import time
            time.sleep(3)
            
            # Check if T&M tag was created with correct date
            tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
            if tm_tags_response.status_code != 200:
                self.log_result("date_sync", "Get T&M tags for date verification", False, f"HTTP {tm_tags_response.status_code}", tm_tags_response)
                return False
            
            tm_tags = tm_tags_response.json()
            synced_tag = None
            
            for tag in tm_tags:
                if (tag.get("project_id") == project_id and 
                    "Auto-generated from Crew Log" in tag.get("tm_tag_title", "")):
                    synced_tag = tag
                    break
            
            if synced_tag:
                # Check if the date matches (not 1 day behind)
                tag_date = synced_tag.get("date_of_work", "")
                if isinstance(tag_date, str):
                    tag_date_str = tag_date.split("T")[0]
                else:
                    tag_date_str = str(tag_date)
                
                today_str = today.strftime('%Y-%m-%d')
                
                if tag_date_str == today_str:
                    self.log_result("date_sync", "T&M tag date consistency", True, f"T&M tag date {tag_date_str} matches crew log date {today_str}")
                else:
                    self.log_result("date_sync", "T&M tag date consistency", False, f"T&M tag date {tag_date_str} does not match crew log date {today_str}")
            else:
                self.log_result("date_sync", "T&M tag auto-generation", False, "No auto-generated T&M tag found")
            
            # Test manual sync endpoint
            sync_response = self.session.post(f"{self.base_url}/crew-logs/{crew_log_id}/sync")
            if sync_response.status_code == 200:
                self.log_result("date_sync", "Manual sync endpoint", True, "Manual sync endpoint working")
            else:
                self.log_result("date_sync", "Manual sync endpoint", False, f"HTTP {sync_response.status_code}", sync_response)
            
        except Exception as e:
            self.log_result("date_sync", "Date sync test", False, str(e))
        
        return True
    
    def test_gc_access_management(self):
        """Test 2: GC Access Management - PINs and access logs"""
        print("\n=== Testing GC Access Management Fix ===")
        
        try:
            # Test GET /api/gc/keys/admin - should show PINs correctly
            keys_response = self.session.get(f"{self.base_url}/gc/keys/admin")
            if keys_response.status_code == 200:
                keys_data = keys_response.json()
                if isinstance(keys_data, list):
                    self.log_result("gc_access", "GET /api/gc/keys/admin", True, f"Retrieved {len(keys_data)} GC keys")
                else:
                    self.log_result("gc_access", "GET /api/gc/keys/admin", False, "Response is not a list")
            else:
                self.log_result("gc_access", "GET /api/gc/keys/admin", False, f"HTTP {keys_response.status_code}", keys_response)
            
            # Test GET /api/gc/access-logs/admin - should show access logs
            logs_response = self.session.get(f"{self.base_url}/gc/access-logs/admin")
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                if isinstance(logs_data, list):
                    self.log_result("gc_access", "GET /api/gc/access-logs/admin", True, f"Retrieved {len(logs_data)} access logs")
                else:
                    self.log_result("gc_access", "GET /api/gc/access-logs/admin", False, "Response is not a list")
            else:
                self.log_result("gc_access", "GET /api/gc/access-logs/admin", False, f"HTTP {logs_response.status_code}", logs_response)
            
            # Test GC PIN generation for projects
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code == 200:
                projects = projects_response.json()
                if projects:
                    project = projects[0]
                    project_id = project["id"]
                    
                    # Test PIN generation endpoint
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        if "gcPin" in pin_data and len(pin_data["gcPin"]) == 4:
                            self.log_result("gc_access", "GC PIN generation", True, f"Generated 4-digit PIN: {pin_data['gcPin']}")
                            
                            # Test GC login with the PIN
                            login_data = {
                                "projectId": project_id,
                                "pin": pin_data["gcPin"]
                            }
                            
                            login_response = self.session.post(
                                f"{self.base_url}/gc/login-simple",
                                json=login_data,
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if login_response.status_code == 200:
                                self.log_result("gc_access", "GC PIN login", True, "GC login with PIN successful")
                            else:
                                self.log_result("gc_access", "GC PIN login", False, f"HTTP {login_response.status_code}", login_response)
                        else:
                            self.log_result("gc_access", "GC PIN generation", False, "Invalid PIN format")
                    else:
                        self.log_result("gc_access", "GC PIN generation", False, f"HTTP {pin_response.status_code}", pin_response)
                else:
                    self.log_result("gc_access", "Get projects for PIN test", False, "No projects found")
            else:
                self.log_result("gc_access", "Get projects for PIN test", False, f"HTTP {projects_response.status_code}", projects_response)
        
        except Exception as e:
            self.log_result("gc_access", "GC access management test", False, str(e))
        
        return True
    
    def test_enhanced_gc_dashboard(self):
        """Test 3: Enhanced GC Dashboard with inspection data"""
        print("\n=== Testing Enhanced GC Dashboard Fix ===")
        
        try:
            # Get a project to test dashboard
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code != 200:
                self.log_result("gc_dashboard", "Get projects for dashboard test", False, f"HTTP {projects_response.status_code}", projects_response)
                return False
            
            projects = projects_response.json()
            if not projects:
                self.log_result("gc_dashboard", "Get projects for dashboard test", False, "No projects found")
                return False
            
            project = projects[0]
            project_id = project["id"]
            
            # Test GET /api/gc/dashboard/{project_id} with inspection data
            dashboard_response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                
                # Verify required dashboard fields are present
                required_fields = ["projectId", "projectName", "crewSummary", "tmTagSummary", "phases", "inspections"]
                missing_fields = [field for field in required_fields if field not in dashboard_data]
                
                if not missing_fields:
                    self.log_result("gc_dashboard", "Dashboard structure", True, "All required dashboard fields present")
                    
                    # Check inspection data specifically
                    inspections = dashboard_data.get("inspections", {})
                    if isinstance(inspections, dict):
                        self.log_result("gc_dashboard", "Inspection data structure", True, "Inspection data properly structured")
                        
                        # Check if inspection status and dates are included
                        if "status" in inspections or "rough_inspection_status" in inspections:
                            self.log_result("gc_dashboard", "Inspection status included", True, "Inspection status fields present")
                        else:
                            self.log_result("gc_dashboard", "Inspection status included", False, "No inspection status fields found")
                    else:
                        self.log_result("gc_dashboard", "Inspection data structure", False, "Inspection data not properly structured")
                    
                    # Check crew summaries
                    crew_summary = dashboard_data.get("crewSummary", {})
                    if "totalHours" in crew_summary and "totalDays" in crew_summary:
                        self.log_result("gc_dashboard", "Crew summary populated", True, f"Crew summary: {crew_summary.get('totalHours', 0)} hours, {crew_summary.get('totalDays', 0)} days")
                    else:
                        self.log_result("gc_dashboard", "Crew summary populated", False, "Crew summary missing required fields")
                    
                    # Check recent work descriptions
                    tm_tag_summary = dashboard_data.get("tmTagSummary", {})
                    if "recentTagTitles" in tm_tag_summary:
                        recent_titles = tm_tag_summary["recentTagTitles"]
                        self.log_result("gc_dashboard", "Recent work descriptions", True, f"Found {len(recent_titles)} recent work descriptions")
                    else:
                        self.log_result("gc_dashboard", "Recent work descriptions", False, "No recent work descriptions found")
                
                else:
                    self.log_result("gc_dashboard", "Dashboard structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("gc_dashboard", "GET /api/gc/dashboard/{project_id}", False, f"HTTP {dashboard_response.status_code}", dashboard_response)
        
        except Exception as e:
            self.log_result("gc_dashboard", "Enhanced GC dashboard test", False, str(e))
        
        return True
    
    def test_project_inspections(self):
        """Test 4: Project Management with Inspections"""
        print("\n=== Testing Project Management with Inspections Fix ===")
        
        try:
            # Get or create a project to test inspection fields
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code != 200:
                self.log_result("project_inspections", "Get projects for inspection test", False, f"HTTP {projects_response.status_code}", projects_response)
                return False
            
            projects = projects_response.json()
            if projects:
                project = projects[0]
                project_id = project["id"]
                self.log_result("project_inspections", "Get existing project", True, f"Using project {project_id}")
            else:
                # Create a test project with inspection fields
                project_data = {
                    "name": "Inspection Test Project",
                    "description": "Testing inspection field functionality",
                    "client_company": "Inspection Test Company",
                    "gc_email": "inspection@test.com",
                    "contract_amount": 75000.00,
                    "labor_rate": 95.0,
                    "project_manager": "Jesus Garcia",
                    "start_date": datetime.now().isoformat(),
                    "address": "Inspection Test Address",
                    "rough_inspection_status": "pending",
                    "final_inspection_status": "not_started",
                    "rough_inspection_date": (datetime.now() + timedelta(days=30)).isoformat(),
                    "final_inspection_date": (datetime.now() + timedelta(days=60)).isoformat()
                }
                
                create_response = self.session.post(
                    f"{self.base_url}/projects",
                    json=project_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if create_response.status_code != 200:
                    self.log_result("project_inspections", "Create project with inspection fields", False, f"HTTP {create_response.status_code}", create_response)
                    return False
                
                project = create_response.json()
                project_id = project["id"]
                self.log_result("project_inspections", "Create project with inspection fields", True, f"Created project {project_id}")
            
            # Test updating project with inspection fields
            update_data = {
                "name": project.get("name", "Test Project"),
                "description": project.get("description", ""),
                "client_company": project.get("client_company", ""),
                "gc_email": project.get("gc_email", ""),
                "contract_amount": project.get("contract_amount", 0),
                "labor_rate": project.get("labor_rate", 95.0),
                "project_manager": project.get("project_manager", "Jesus Garcia"),
                "start_date": project.get("start_date", datetime.now().isoformat()),
                "address": project.get("address", ""),
                "rough_inspection_status": "completed",
                "final_inspection_status": "scheduled",
                "rough_inspection_date": datetime.now().isoformat(),
                "final_inspection_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "inspection_notes": "Updated inspection notes - rough inspection completed successfully"
            }
            
            update_response = self.session.put(
                f"{self.base_url}/projects/{project_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code == 200:
                updated_project = update_response.json()
                
                # Verify inspection fields are working
                inspection_fields_working = True
                inspection_fields = ["rough_inspection_status", "final_inspection_status"]
                
                for field in inspection_fields:
                    if updated_project.get(field) != update_data[field]:
                        inspection_fields_working = False
                        break
                
                if inspection_fields_working:
                    self.log_result("project_inspections", "Inspection status fields", True, f"Rough: {updated_project.get('rough_inspection_status')}, Final: {updated_project.get('final_inspection_status')}")
                else:
                    self.log_result("project_inspections", "Inspection status fields", False, "Inspection status fields not updated correctly")
                
                # Test date handling for inspection_date fields
                rough_date = updated_project.get("rough_inspection_date")
                final_date = updated_project.get("final_inspection_date")
                
                if rough_date and final_date:
                    self.log_result("project_inspections", "Inspection date handling", True, f"Dates properly stored: rough={rough_date[:10]}, final={final_date[:10]}")
                else:
                    self.log_result("project_inspections", "Inspection date handling", False, "Inspection dates not properly stored")
                
                # Test inspection notes
                if updated_project.get("inspection_notes") == update_data["inspection_notes"]:
                    self.log_result("project_inspections", "Inspection notes", True, "Inspection notes properly stored")
                else:
                    self.log_result("project_inspections", "Inspection notes", False, "Inspection notes not properly stored")
            
            else:
                self.log_result("project_inspections", "Update project with inspection fields", False, f"HTTP {update_response.status_code}", update_response)
        
        except Exception as e:
            self.log_result("project_inspections", "Project inspections test", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """Run all review request tests"""
        print("🚀 Starting Review Request Backend Testing")
        print("=" * 60)
        
        if not self.test_basic_connectivity():
            print("❌ Cannot proceed - backend not accessible")
            return False
        
        # Run all specific tests
        self.test_date_sync_issue()
        self.test_gc_access_management()
        self.test_enhanced_gc_dashboard()
        self.test_project_inspections()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REVIEW REQUEST TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASSED" if failed == 0 else "❌ FAILED"
            print(f"{category.upper().replace('_', ' ')}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  - {error}")
        
        print(f"\nOVERALL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL REVIEW REQUEST TESTS PASSED!")
        else:
            print(f"⚠️  {total_failed} TESTS FAILED - REVIEW NEEDED")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = ReviewBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)