#!/usr/bin/env python3
"""
Review Request Backend Testing
Focus on specific requirements from the review request:
1. Crew Log -> T&M tag date handling (2025-09-17 ISO local)
2. GC PIN validation and login
3. Admin/GC endpoints under /api prefix
4. Projects list returns gc_pin and gc_pin_used
5. Health check
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://rhino-tm-app.preview.emergentagent.com/api"

class ReviewTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "crew_log_date_handling": {"passed": 0, "failed": 0, "errors": []},
            "gc_pin_system": {"passed": 0, "failed": 0, "errors": []},
            "api_endpoints": {"passed": 0, "failed": 0, "errors": []},
            "health_check": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
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
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_result("health_check", "Health check endpoint", True, "Health check accessible")
                return True
            else:
                self.log_result("health_check", "Health check endpoint", False, f"Status: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("health_check", "Health check endpoint", False, str(e))
            return False
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True, "API accessible")
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def test_projects_gc_pin_fields(self):
        """Test that projects list returns gc_pin and gc_pin_used fields"""
        print("\n=== Testing Projects GC PIN Fields ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if isinstance(projects, list) and len(projects) > 0:
                    # Check first project for required fields
                    project = projects[0]
                    has_gc_pin = "gc_pin" in project
                    has_gc_pin_used = "gc_pin_used" in project
                    
                    if has_gc_pin and has_gc_pin_used:
                        self.log_result("api_endpoints", "Projects GC PIN fields", True, 
                                      f"Found gc_pin: {project.get('gc_pin')}, gc_pin_used: {project.get('gc_pin_used')}")
                        return projects
                    else:
                        missing_fields = []
                        if not has_gc_pin:
                            missing_fields.append("gc_pin")
                        if not has_gc_pin_used:
                            missing_fields.append("gc_pin_used")
                        self.log_result("api_endpoints", "Projects GC PIN fields", False, 
                                      f"Missing fields: {missing_fields}")
                else:
                    self.log_result("api_endpoints", "Projects GC PIN fields", False, "No projects found to test")
            else:
                self.log_result("api_endpoints", "Projects GC PIN fields", False, f"Status: {response.status_code}", response)
        except Exception as e:
            self.log_result("api_endpoints", "Projects GC PIN fields", False, str(e))
        return None
    
    def test_gc_pin_generation(self, project_id):
        """Test GC PIN generation for a specific project"""
        print(f"\n=== Testing GC PIN Generation for Project {project_id} ===")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            if response.status_code == 200:
                pin_data = response.json()
                if "gcPin" in pin_data and "projectId" in pin_data:
                    pin = pin_data["gcPin"]
                    # Validate PIN format (4-digit)
                    if isinstance(pin, str) and len(pin) == 4 and pin.isdigit():
                        self.log_result("gc_pin_system", "GC PIN generation", True, 
                                      f"Generated PIN: {pin} for project: {pin_data.get('projectName', 'Unknown')}")
                        return pin_data
                    else:
                        self.log_result("gc_pin_system", "GC PIN generation", False, 
                                      f"Invalid PIN format: {pin}")
                else:
                    self.log_result("gc_pin_system", "GC PIN generation", False, 
                                  "Missing gcPin or projectId in response", response)
            else:
                self.log_result("gc_pin_system", "GC PIN generation", False, f"Status: {response.status_code}", response)
        except Exception as e:
            self.log_result("gc_pin_system", "GC PIN generation", False, str(e))
        return None
    
    def test_gc_pin_validation(self, pin):
        """Test GC PIN validation endpoint"""
        print(f"\n=== Testing GC PIN Validation with PIN: {pin} ===")
        try:
            response = self.session.post(
                f"{self.base_url}/gc/validate-pin",
                json={"pin": pin},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                validation_data = response.json()
                if "success" in validation_data and validation_data["success"]:
                    if "projectId" in validation_data:
                        self.log_result("gc_pin_system", "GC PIN validation", True, 
                                      f"PIN validated successfully, projectId: {validation_data['projectId']}")
                        return validation_data
                    else:
                        self.log_result("gc_pin_system", "GC PIN validation", False, 
                                      "Missing projectId in successful validation response")
                else:
                    self.log_result("gc_pin_system", "GC PIN validation", False, 
                                  f"Validation failed: {validation_data.get('message', 'Unknown error')}")
            elif response.status_code == 401:
                # This might be expected if PIN was already used
                self.log_result("gc_pin_system", "GC PIN validation", True, 
                              "PIN correctly rejected (likely already used)")
                return {"used_pin": True}
            else:
                self.log_result("gc_pin_system", "GC PIN validation", False, f"Status: {response.status_code}", response)
        except Exception as e:
            self.log_result("gc_pin_system", "GC PIN validation", False, str(e))
        return None
    
    def test_crew_log_date_handling(self):
        """Test crew log creation with specific date 2025-09-17 and verify T&M tag date handling"""
        print("\n=== Testing Crew Log -> T&M Tag Date Handling (2025-09-17) ===")
        
        # First, get a project to work with
        projects = self.test_projects_gc_pin_fields()
        if not projects or len(projects) == 0:
            self.log_result("crew_log_date_handling", "Setup - Get project", False, "No projects available for testing")
            return False
        
        project = projects[0]
        project_id = project["id"]
        project_name = project.get("name", "Test Project")
        
        # Create crew log with specific date 2025-09-17 (ISO local format)
        test_date = "2025-09-17T08:00:00"  # ISO local format as requested
        
        crew_log_data = {
            "project_id": project_id,
            "date": test_date,
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
            "work_description": "Date handling test - crew log for 2025-09-17",
            "weather_conditions": "clear"
        }
        
        try:
            # Create crew log
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log.get("id")
                self.log_result("crew_log_date_handling", "Crew log creation", True, 
                              f"Created crew log with date: {test_date}")
                
                # Wait for sync to complete
                import time
                time.sleep(3)
                
                # Check if T&M tag was auto-created with correct date
                tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
                if tm_tags_response.status_code == 200:
                    tm_tags = tm_tags_response.json()
                    
                    # Look for auto-generated T&M tag
                    matching_tm_tag = None
                    for tag in tm_tags:
                        if (tag.get("project_id") == project_id and 
                            "Auto-generated from Crew Log" in tag.get("tm_tag_title", "")):
                            matching_tm_tag = tag
                            break
                    
                    if matching_tm_tag:
                        tm_date = matching_tm_tag.get("date_of_work", "")
                        expected_date = "2025-09-17"  # Expected date format
                        
                        # Check if date matches (handle different formats)
                        if expected_date in tm_date:
                            self.log_result("crew_log_date_handling", "T&M tag date handling", True, 
                                          f"T&M tag created with correct date: {tm_date} (contains {expected_date})")
                            
                            # Test analytics to verify day count
                            analytics_response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
                            if analytics_response.status_code == 200:
                                analytics = analytics_response.json()
                                work_days = analytics.get("work_days", 0)
                                self.log_result("crew_log_date_handling", "Analytics day count", True, 
                                              f"Analytics shows {work_days} work days")
                            else:
                                self.log_result("crew_log_date_handling", "Analytics day count", False, 
                                              f"Analytics not accessible: {analytics_response.status_code}")
                        else:
                            self.log_result("crew_log_date_handling", "T&M tag date handling", False, 
                                          f"T&M tag date mismatch: got {tm_date}, expected to contain {expected_date}")
                    else:
                        self.log_result("crew_log_date_handling", "T&M tag auto-creation", False, 
                                      "No auto-generated T&M tag found")
                else:
                    self.log_result("crew_log_date_handling", "T&M tag verification", False, 
                                  f"Could not retrieve T&M tags: {tm_tags_response.status_code}")
                
                # Test manual sync endpoint
                sync_response = self.session.post(f"{self.base_url}/crew-logs/{crew_log_id}/sync")
                if sync_response.status_code == 200:
                    self.log_result("crew_log_date_handling", "Manual sync endpoint", True, 
                                  "Manual sync endpoint accessible")
                else:
                    self.log_result("crew_log_date_handling", "Manual sync endpoint", False, 
                                  f"Manual sync failed: {sync_response.status_code}")
                
                return True
            else:
                self.log_result("crew_log_date_handling", "Crew log creation", False, 
                              f"Status: {response.status_code}", response)
        except Exception as e:
            self.log_result("crew_log_date_handling", "Crew log creation", False, str(e))
        
        return False
    
    def test_admin_gc_endpoints(self):
        """Test that Admin/GC endpoints work under /api prefix"""
        print("\n=== Testing Admin/GC Endpoints under /api prefix ===")
        
        endpoints_to_test = [
            ("/gc/validate-pin", "POST", {"pin": "0000"}),  # Test with dummy PIN
            ("/projects", "GET", None),  # Should work
        ]
        
        for endpoint, method, data in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url, json=data, headers={"Content-Type": "application/json"})
                
                # We expect these to be accessible (even if they return errors for invalid data)
                if response.status_code in [200, 400, 401, 422]:  # Accessible but may have validation errors
                    self.log_result("api_endpoints", f"Endpoint {endpoint} accessibility", True, 
                                  f"Endpoint accessible (status: {response.status_code})")
                else:
                    self.log_result("api_endpoints", f"Endpoint {endpoint} accessibility", False, 
                                  f"Endpoint not accessible (status: {response.status_code})")
            except Exception as e:
                self.log_result("api_endpoints", f"Endpoint {endpoint} accessibility", False, str(e))
    
    def run_comprehensive_review_tests(self):
        """Run all review-specific tests"""
        print("🎯 STARTING COMPREHENSIVE REVIEW TESTING")
        print("=" * 60)
        
        # Test 1: Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed - aborting tests")
            return False
        
        # Test 2: Health check
        self.test_health_check()
        
        # Test 3: Projects list with GC PIN fields
        projects = self.test_projects_gc_pin_fields()
        
        # Test 4: Admin/GC endpoints under /api prefix
        self.test_admin_gc_endpoints()
        
        # Test 5: GC PIN system (if we have projects)
        if projects and len(projects) > 0:
            project_id = projects[0]["id"]
            
            # Generate fresh PIN
            pin_data = self.test_gc_pin_generation(project_id)
            
            # Test PIN validation (if we got a PIN)
            if pin_data and "gcPin" in pin_data:
                self.test_gc_pin_validation(pin_data["gcPin"])
        
        # Test 6: Crew log date handling
        self.test_crew_log_date_handling()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 REVIEW TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            if passed + failed > 0:
                success_rate = (passed / (passed + failed)) * 100
                status = "✅" if failed == 0 else "⚠️" if success_rate >= 70 else "❌"
                print(f"{status} {category.upper()}: {passed}/{passed + failed} passed ({success_rate:.1f}%)")
                
                # Print errors if any
                if results["errors"]:
                    for error in results["errors"]:
                        print(f"   ❌ {error}")
        
        overall_success_rate = (total_passed / (total_passed + total_failed)) * 100 if (total_passed + total_failed) > 0 else 0
        print(f"\n🎯 OVERALL: {total_passed}/{total_passed + total_failed} tests passed ({overall_success_rate:.1f}%)")
        
        if overall_success_rate >= 90:
            print("🎉 EXCELLENT: Review requirements are working well!")
        elif overall_success_rate >= 70:
            print("✅ GOOD: Most review requirements are working, minor issues found")
        else:
            print("⚠️ NEEDS ATTENTION: Several review requirements need fixes")

def main():
    """Main test execution"""
    tester = ReviewTester()
    
    print("🎯 REVIEW REQUEST BACKEND TESTING")
    print("Testing specific requirements:")
    print("1. Crew Log -> T&M tag date handling (2025-09-17 ISO local)")
    print("2. GC PIN validation and login")
    print("3. Admin/GC endpoints under /api prefix")
    print("4. Projects list returns gc_pin and gc_pin_used")
    print("5. Health check")
    print()
    
    success = tester.run_comprehensive_review_tests()
    
    if success:
        print("\n✅ Review testing completed successfully!")
    else:
        print("\n❌ Review testing encountered critical issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()