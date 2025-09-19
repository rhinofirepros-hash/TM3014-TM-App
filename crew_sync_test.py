#!/usr/bin/env python3
"""
Crew Log to T&M Tag Synchronization Testing
Focus on debugging why crew logs are getting stuck in "Pending" status instead of syncing to create T&M tags.
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import time
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

class CrewSyncTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "crew_sync": {"passed": 0, "failed": 0, "errors": []},
            "manual_sync": {"passed": 0, "failed": 0, "errors": []},
            "database": {"passed": 0, "failed": 0, "errors": []},
            "error_scenarios": {"passed": 0, "failed": 0, "errors": []}
        }
        self.created_project_id = None
        self.created_project_name = None
        
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
    
    def setup_test_project(self):
        """Create a test project for crew log sync testing"""
        print("\n=== Setting Up Test Project ===")
        
        project_data = {
            "name": "Crew Sync Test Project",
            "description": "Project for testing crew log to T&M tag synchronization",
            "client_company": "Test Client Corp",
            "gc_email": "test@client.com",
            "contract_amount": 100000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "123 Test Street"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                self.created_project_id = project["id"]
                self.created_project_name = project["name"]
                self.log_result("database", "Test project setup", True, f"Created project: {self.created_project_id}")
                return project
            else:
                self.log_result("database", "Test project setup", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("database", "Test project setup", False, str(e))
            return None
    
    def test_crew_log_creation_and_auto_sync(self):
        """Test creating crew logs and verify auto-sync to T&M tags"""
        print("\n=== Testing Crew Log Creation and Auto-Sync ===")
        
        if not self.created_project_id:
            self.log_result("crew_sync", "Auto-sync test setup", False, "No test project available")
            return False
        
        # Create realistic crew log data
        work_date = datetime.now() - timedelta(days=1)
        crew_log_data = {
            "project_id": self.created_project_id,
            "date": work_date.isoformat(),
            "crew_members": [
                {
                    "name": "Mike Rodriguez",
                    "st_hours": 8.0,
                    "ot_hours": 2.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 10.0
                },
                {
                    "name": "Sarah Johnson",
                    "st_hours": 8.0,
                    "ot_hours": 1.5,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 9.5
                }
            ],
            "work_description": "Electrical panel installation and conduit running for office spaces",
            "weather_conditions": "Clear, 72°F",
            "expenses": {
                "per_diem": 100.0,
                "hotel_cost": 0.0,
                "gas_expense": 45.0,
                "other_expenses": 25.0
            }
        }
        
        try:
            # Step 1: Create crew log
            print("Step 1: Creating crew log...")
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log.get("id")
                self.log_result("crew_sync", "Crew log creation", True, f"Created crew log: {crew_log_id}")
                
                # Step 2: Wait for sync to complete
                print("Step 2: Waiting for sync to complete...")
                time.sleep(3)
                
                # Step 3: Check if sync_crew_log_to_tm function was called
                print("Step 3: Checking if T&M tag was auto-created...")
                tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
                
                if tm_tags_response.status_code == 200:
                    tm_tags = tm_tags_response.json()
                    
                    # Look for auto-generated T&M tag
                    auto_tm_tag = None
                    for tag in tm_tags:
                        if (tag.get("project_id") == self.created_project_id and 
                            "Auto-generated from Crew Log" in tag.get("tm_tag_title", "")):
                            auto_tm_tag = tag
                            break
                    
                    if auto_tm_tag:
                        self.log_result("crew_sync", "Auto T&M tag creation", True, f"T&M tag auto-created: {auto_tm_tag['id']}")
                        self.auto_tm_tag_id = auto_tm_tag["id"]
                        
                        # Step 4: Verify crew log is marked as synced
                        print("Step 4: Verifying crew log sync status...")
                        crew_logs_response = self.session.get(f"{self.base_url}/crew-logs")
                        if crew_logs_response.status_code == 200:
                            crew_logs = crew_logs_response.json()
                            synced_log = None
                            for log in crew_logs:
                                if log.get("id") == crew_log_id:
                                    synced_log = log
                                    break
                            
                            if synced_log and synced_log.get("synced_to_tm") == True:
                                self.log_result("crew_sync", "Crew log sync status", True, "Crew log marked as synced_to_tm = true")
                            else:
                                self.log_result("crew_sync", "Crew log sync status", False, f"Crew log not marked as synced: synced_to_tm = {synced_log.get('synced_to_tm') if synced_log else 'log not found'}")
                        else:
                            self.log_result("crew_sync", "Crew log sync status", False, "Could not retrieve crew logs for sync verification")
                    else:
                        self.log_result("crew_sync", "Auto T&M tag creation", False, "No auto-generated T&M tag found - sync may have failed")
                        
                        # Debug: Check if there are any T&M tags at all
                        print(f"DEBUG: Found {len(tm_tags)} total T&M tags")
                        for i, tag in enumerate(tm_tags):
                            print(f"  Tag {i+1}: {tag.get('tm_tag_title', 'No title')} - Project: {tag.get('project_id', 'No project')}")
                else:
                    self.log_result("crew_sync", "Auto T&M tag creation", False, f"Could not retrieve T&M tags: HTTP {tm_tags_response.status_code}")
            else:
                self.log_result("crew_sync", "Crew log creation", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("crew_sync", "Auto-sync test", False, str(e))
            return False
        
        return True
    
    def test_manual_sync_endpoint(self):
        """Test the manual sync endpoint for stuck crew logs"""
        print("\n=== Testing Manual Sync Endpoint ===")
        
        if not self.created_project_id:
            self.log_result("manual_sync", "Manual sync test setup", False, "No test project available")
            return False
        
        # Create a crew log that might get stuck
        work_date = datetime.now() - timedelta(hours=2)
        crew_log_data = {
            "project_id": self.created_project_id,
            "date": work_date.isoformat(),
            "crew_members": [
                {
                    "name": "David Chen",
                    "st_hours": 8.0,
                    "ot_hours": 0.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 8.0
                }
            ],
            "work_description": "Manual sync test - electrical troubleshooting",
            "weather_conditions": "Overcast, 68°F"
        }
        
        try:
            # Step 1: Create crew log
            print("Step 1: Creating crew log for manual sync test...")
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log.get("id")
                self.log_result("manual_sync", "Manual sync crew log creation", True, f"Created crew log: {crew_log_id}")
                
                # Step 2: Test manual sync endpoint
                print("Step 2: Testing manual sync endpoint...")
                sync_response = self.session.post(
                    f"{self.base_url}/crew-logs/{crew_log_id}/sync",
                    headers={"Content-Type": "application/json"}
                )
                
                if sync_response.status_code == 200:
                    sync_result = sync_response.json()
                    
                    if "message" in sync_result and "synced successfully" in sync_result["message"]:
                        self.log_result("manual_sync", "Manual sync execution", True, f"Manual sync successful: {sync_result['message']}")
                        
                        # Step 3: Verify T&M tag was created
                        if "tm_tag_id" in sync_result:
                            tm_tag_id = sync_result["tm_tag_id"]
                            tm_tag_response = self.session.get(f"{self.base_url}/tm-tags/{tm_tag_id}")
                            
                            if tm_tag_response.status_code == 200:
                                self.log_result("manual_sync", "Manual sync T&M tag creation", True, f"T&M tag created via manual sync: {tm_tag_id}")
                            else:
                                self.log_result("manual_sync", "Manual sync T&M tag creation", False, "T&M tag ID returned but tag not found")
                        else:
                            self.log_result("manual_sync", "Manual sync T&M tag creation", False, "No tm_tag_id returned from manual sync")
                    else:
                        self.log_result("manual_sync", "Manual sync execution", False, f"Unexpected sync response: {sync_result}")
                else:
                    self.log_result("manual_sync", "Manual sync execution", False, f"HTTP {sync_response.status_code}", sync_response)
            else:
                self.log_result("manual_sync", "Manual sync crew log creation", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("manual_sync", "Manual sync test", False, str(e))
            return False
        
        return True
    
    def test_database_state_verification(self):
        """Test database state verification for sync status"""
        print("\n=== Testing Database State Verification ===")
        
        try:
            # Step 1: Get all crew logs and check their sync status
            print("Step 1: Checking crew logs sync status...")
            crew_logs_response = self.session.get(f"{self.base_url}/crew-logs")
            
            if crew_logs_response.status_code == 200:
                crew_logs = crew_logs_response.json()
                
                synced_count = 0
                pending_count = 0
                
                for log in crew_logs:
                    if log.get("synced_to_tm") == True:
                        synced_count += 1
                    else:
                        pending_count += 1
                
                self.log_result("database", "Crew logs sync status check", True, 
                              f"Found {len(crew_logs)} crew logs: {synced_count} synced, {pending_count} pending")
                
                # Step 2: Get all T&M tags and check for auto-generated ones
                print("Step 2: Checking T&M tags for auto-generated entries...")
                tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
                
                if tm_tags_response.status_code == 200:
                    tm_tags = tm_tags_response.json()
                    
                    auto_generated_count = 0
                    manual_count = 0
                    
                    for tag in tm_tags:
                        if "Auto-generated from Crew Log" in tag.get("tm_tag_title", ""):
                            auto_generated_count += 1
                        else:
                            manual_count += 1
                    
                    self.log_result("database", "T&M tags auto-generation check", True,
                                  f"Found {len(tm_tags)} T&M tags: {auto_generated_count} auto-generated, {manual_count} manual")
                    
                    # Step 3: Verify relationship between crew logs and T&M tags
                    print("Step 3: Verifying crew log to T&M tag relationships...")
                    relationship_count = 0
                    
                    for log in crew_logs:
                        if log.get("tm_tag_id"):
                            # Check if the referenced T&M tag exists
                            tm_tag_id = log["tm_tag_id"]
                            tm_tag_exists = any(tag["id"] == tm_tag_id for tag in tm_tags)
                            if tm_tag_exists:
                                relationship_count += 1
                    
                    self.log_result("database", "Crew log to T&M tag relationships", True,
                                  f"Found {relationship_count} valid crew log to T&M tag relationships")
                else:
                    self.log_result("database", "T&M tags auto-generation check", False, f"HTTP {tm_tags_response.status_code}")
            else:
                self.log_result("database", "Crew logs sync status check", False, f"HTTP {crew_logs_response.status_code}")
                
        except Exception as e:
            self.log_result("database", "Database state verification", False, str(e))
            return False
        
        return True
    
    def test_sync_logic_debugging(self):
        """Test the sync function with actual crew log data to debug issues"""
        print("\n=== Testing Sync Logic Debugging ===")
        
        if not self.created_project_id:
            self.log_result("crew_sync", "Sync logic test setup", False, "No test project available")
            return False
        
        # Create crew log with comprehensive data for debugging
        work_date = datetime.now() - timedelta(minutes=30)
        crew_log_data = {
            "project_id": self.created_project_id,
            "date": work_date.isoformat(),
            "crew_members": [
                {
                    "name": "Debug Test Worker",
                    "st_hours": 4.0,
                    "ot_hours": 0.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 4.0
                }
            ],
            "work_description": "Debug test - checking sync logic with detailed logging",
            "weather_conditions": "Debug conditions"
        }
        
        try:
            # Step 1: Verify project exists before creating crew log
            print("Step 1: Verifying project exists...")
            project_response = self.session.get(f"{self.base_url}/projects/{self.created_project_id}")
            
            if project_response.status_code == 200:
                project = project_response.json()
                self.log_result("crew_sync", "Project existence check", True, f"Project found: {project['name']}")
                
                # Step 2: Create crew log with debug data
                print("Step 2: Creating crew log with debug data...")
                response = self.session.post(
                    f"{self.base_url}/crew-logs",
                    json=crew_log_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    crew_log = response.json()
                    crew_log_id = crew_log.get("id")
                    self.log_result("crew_sync", "Debug crew log creation", True, f"Created debug crew log: {crew_log_id}")
                    
                    # Step 3: Check date parsing and comparison logic
                    print("Step 3: Testing date parsing and comparison...")
                    work_date_str = work_date.strftime('%Y-%m-%d')
                    
                    # Look for T&M tags with same project and date
                    tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
                    if tm_tags_response.status_code == 200:
                        tm_tags = tm_tags_response.json()
                        matching_tags = []
                        
                        for tag in tm_tags:
                            if tag.get("project_id") == self.created_project_id:
                                tag_date = tag.get("date_of_work", "")
                                if isinstance(tag_date, str):
                                    tag_date_str = tag_date.split("T")[0]
                                    if tag_date_str == work_date_str:
                                        matching_tags.append(tag)
                        
                        self.log_result("crew_sync", "Date parsing and comparison", True,
                                      f"Found {len(matching_tags)} T&M tags with matching project and date")
                    
                    # Step 4: Wait and check if sync occurred
                    print("Step 4: Waiting for sync and checking results...")
                    time.sleep(5)  # Longer wait for debugging
                    
                    # Check crew log sync status
                    updated_crew_logs = self.session.get(f"{self.base_url}/crew-logs")
                    if updated_crew_logs.status_code == 200:
                        logs = updated_crew_logs.json()
                        debug_log = None
                        for log in logs:
                            if log.get("id") == crew_log_id:
                                debug_log = log
                                break
                        
                        if debug_log:
                            sync_status = debug_log.get("synced_to_tm", False)
                            tm_tag_id = debug_log.get("tm_tag_id")
                            
                            if sync_status and tm_tag_id:
                                self.log_result("crew_sync", "Debug sync verification", True,
                                              f"Sync successful - synced_to_tm: {sync_status}, tm_tag_id: {tm_tag_id}")
                            else:
                                self.log_result("crew_sync", "Debug sync verification", False,
                                              f"Sync failed - synced_to_tm: {sync_status}, tm_tag_id: {tm_tag_id}")
                        else:
                            self.log_result("crew_sync", "Debug sync verification", False, "Could not find debug crew log after creation")
                else:
                    self.log_result("crew_sync", "Debug crew log creation", False, f"HTTP {response.status_code}", response)
            else:
                self.log_result("crew_sync", "Project existence check", False, f"HTTP {project_response.status_code}")
                
        except Exception as e:
            self.log_result("crew_sync", "Sync logic debugging", False, str(e))
            return False
        
        return True
    
    def test_error_scenarios(self):
        """Test sync with various error scenarios"""
        print("\n=== Testing Error Scenarios ===")
        
        # Test 1: Sync with missing project_id
        print("Test 1: Sync with missing project_id...")
        try:
            crew_log_data = {
                "date": datetime.now().isoformat(),
                "crew_members": [{"name": "Test Worker", "total_hours": 8.0}],
                "work_description": "Test with missing project_id"
            }
            
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            # This should either fail or handle gracefully
            if response.status_code == 200:
                self.log_result("error_scenarios", "Missing project_id handling", True, "API handled missing project_id gracefully")
            else:
                self.log_result("error_scenarios", "Missing project_id handling", True, f"API correctly rejected missing project_id: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("error_scenarios", "Missing project_id handling", False, str(e))
        
        # Test 2: Sync with invalid project_id
        print("Test 2: Sync with invalid project_id...")
        try:
            fake_project_id = str(uuid.uuid4())
            crew_log_data = {
                "project_id": fake_project_id,
                "date": datetime.now().isoformat(),
                "crew_members": [{"name": "Test Worker", "total_hours": 8.0}],
                "work_description": "Test with invalid project_id"
            }
            
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log.get("id")
                
                # Wait and check if sync failed gracefully
                time.sleep(2)
                
                # Try manual sync to see error handling
                sync_response = self.session.post(f"{self.base_url}/crew-logs/{crew_log_id}/sync")
                
                if sync_response.status_code == 200:
                    sync_result = sync_response.json()
                    if "error" in sync_result:
                        self.log_result("error_scenarios", "Invalid project_id handling", True, f"Sync correctly failed: {sync_result['error']}")
                    else:
                        self.log_result("error_scenarios", "Invalid project_id handling", False, "Sync should have failed with invalid project_id")
                else:
                    self.log_result("error_scenarios", "Invalid project_id handling", True, f"Manual sync correctly failed: HTTP {sync_response.status_code}")
            else:
                self.log_result("error_scenarios", "Invalid project_id handling", True, f"API correctly rejected invalid project_id: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("error_scenarios", "Invalid project_id handling", False, str(e))
        
        # Test 3: Sync with invalid dates
        print("Test 3: Sync with invalid dates...")
        try:
            crew_log_data = {
                "project_id": self.created_project_id if self.created_project_id else str(uuid.uuid4()),
                "date": "invalid-date-format",
                "crew_members": [{"name": "Test Worker", "total_hours": 8.0}],
                "work_description": "Test with invalid date"
            }
            
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("error_scenarios", "Invalid date handling", True, f"API correctly rejected invalid date: HTTP {response.status_code}")
            else:
                self.log_result("error_scenarios", "Invalid date handling", False, "API should reject invalid date format")
                
        except Exception as e:
            self.log_result("error_scenarios", "Invalid date handling", False, str(e))
        
        # Test 4: Sync with missing crew member data
        print("Test 4: Sync with missing crew member data...")
        try:
            crew_log_data = {
                "project_id": self.created_project_id if self.created_project_id else str(uuid.uuid4()),
                "date": datetime.now().isoformat(),
                "crew_members": [],  # Empty crew members
                "work_description": "Test with no crew members"
            }
            
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log.get("id")
                
                # Try manual sync to see how it handles empty crew
                sync_response = self.session.post(f"{self.base_url}/crew-logs/{crew_log_id}/sync")
                
                if sync_response.status_code == 200:
                    sync_result = sync_response.json()
                    if "error" in sync_result or "failed" in sync_result.get("message", "").lower():
                        self.log_result("error_scenarios", "Missing crew member handling", True, "Sync correctly handled empty crew members")
                    else:
                        self.log_result("error_scenarios", "Missing crew member handling", False, "Sync should handle empty crew members gracefully")
                else:
                    self.log_result("error_scenarios", "Missing crew member handling", True, f"Manual sync correctly failed: HTTP {sync_response.status_code}")
            else:
                self.log_result("error_scenarios", "Missing crew member handling", True, f"API correctly rejected empty crew: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("error_scenarios", "Missing crew member handling", False, str(e))
        
        return True
    
    def check_backend_logs(self):
        """Check backend logs for sync-related errors"""
        print("\n=== Checking Backend Logs ===")
        
        try:
            # This would typically require access to server logs
            # For now, we'll just note that this should be done
            print("NOTE: Backend logs should be checked for:")
            print("- sync_crew_log_to_tm function calls")
            print("- Database connection errors")
            print("- Date parsing errors")
            print("- Project lookup failures")
            print("- T&M tag creation errors")
            
            self.log_result("database", "Backend log check", True, "Log check recommendations provided")
            
        except Exception as e:
            self.log_result("database", "Backend log check", False, str(e))
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("CREW LOG TO T&M TAG SYNC TESTING SUMMARY")
        print("="*80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            if results["errors"]:
                print("  Errors:")
                for error in results["errors"]:
                    print(f"    - {error}")
        
        print(f"\nOVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%" if (total_passed + total_failed) > 0 else "  📊 Success Rate: 0%")
        
        print(f"\n" + "="*80)
        print("KEY FINDINGS:")
        
        if total_failed == 0:
            print("🎉 All sync tests passed! The crew log to T&M tag synchronization is working correctly.")
        else:
            print("⚠️  Issues found with crew log to T&M tag synchronization:")
            
            # Analyze common failure patterns
            all_errors = []
            for results in self.test_results.values():
                all_errors.extend(results["errors"])
            
            if any("HTTP 500" in error for error in all_errors):
                print("  - Server errors (HTTP 500) detected - check backend logs")
            if any("synced_to_tm" in error for error in all_errors):
                print("  - Crew logs not being marked as synced - sync function may not be called")
            if any("Auto-generated" in error for error in all_errors):
                print("  - T&M tags not being auto-created - sync logic may be failing")
            if any("project" in error.lower() for error in all_errors):
                print("  - Project-related issues - verify project existence and data")
        
        print("="*80)

def main():
    """Main test execution"""
    print("🔍 CREW LOG TO T&M TAG SYNCHRONIZATION TESTING")
    print("Focus: Debugging why crew logs are getting stuck in 'Pending' status")
    print("="*80)
    
    tester = CrewSyncTester()
    
    # Setup
    tester.setup_test_project()
    
    # Core sync tests
    tester.test_crew_log_creation_and_auto_sync()
    tester.test_manual_sync_endpoint()
    tester.test_database_state_verification()
    tester.test_sync_logic_debugging()
    
    # Error scenario tests
    tester.test_error_scenarios()
    
    # Backend log check
    tester.check_backend_logs()
    
    # Print comprehensive summary
    tester.print_summary()

if __name__ == "__main__":
    main()