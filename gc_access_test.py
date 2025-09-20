#!/usr/bin/env python3
"""
GC Access Management Testing Script
Tests the GC Access Management endpoints to debug why PINs aren't showing and access logs are empty
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-inspect-app.preview.emergentagent.com/api"

class GCAccessTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "projects": {"passed": 0, "failed": 0, "errors": []},
            "gc_keys": {"passed": 0, "failed": 0, "errors": []},
            "gc_access_logs": {"passed": 0, "failed": 0, "errors": []},
            "pin_workflow": {"passed": 0, "failed": 0, "errors": []},
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
    
    def test_projects_endpoint(self):
        """Test Projects Endpoint: GET /api/projects - Verify projects have gc_pin and gc_pin_used fields"""
        print("\n=== Testing Projects Endpoint for GC PIN Fields ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                
                if not isinstance(projects, list):
                    self.log_result("projects", "Projects endpoint structure", False, "Response is not a list", response)
                    return None
                
                self.log_result("projects", "Projects endpoint access", True, f"Retrieved {len(projects)} projects")
                
                # Check if projects have gc_pin and gc_pin_used fields
                projects_with_pins = 0
                projects_without_pins = 0
                sample_project = None
                
                for project in projects:
                    if "gc_pin" in project and "gc_pin_used" in project:
                        projects_with_pins += 1
                        if sample_project is None:
                            sample_project = project
                    else:
                        projects_without_pins += 1
                
                if projects_with_pins > 0:
                    self.log_result("projects", "GC PIN fields present", True, 
                                  f"{projects_with_pins}/{len(projects)} projects have gc_pin fields")
                    
                    # Show sample project PIN data
                    if sample_project:
                        pin_value = sample_project.get("gc_pin", "None")
                        pin_used = sample_project.get("gc_pin_used", "None")
                        project_name = sample_project.get("name", "Unknown")
                        self.log_result("projects", "Sample PIN data", True, 
                                      f"Project '{project_name}': PIN={pin_value}, Used={pin_used}")
                else:
                    self.log_result("projects", "GC PIN fields present", False, 
                                  f"No projects have gc_pin fields. Missing from {len(projects)} projects")
                
                if projects_without_pins > 0:
                    self.log_result("projects", "Missing PIN fields", False, 
                                  f"{projects_without_pins} projects missing gc_pin fields")
                
                return projects
            else:
                self.log_result("projects", "Projects endpoint access", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("projects", "Projects endpoint access", False, str(e))
            return None
    
    def test_gc_keys_admin_endpoint(self):
        """Test GC Keys Admin Endpoint: GET /api/gc/keys/admin"""
        print("\n=== Testing GC Keys Admin Endpoint ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/keys/admin")
            
            if response.status_code == 200:
                keys_data = response.json()
                self.log_result("gc_keys", "GC keys admin endpoint access", True, 
                              f"Endpoint exists and returned data: {type(keys_data)}")
                
                if isinstance(keys_data, list):
                    self.log_result("gc_keys", "GC keys data structure", True, 
                                  f"Retrieved {len(keys_data)} GC keys")
                    
                    # Show sample key data if available
                    if keys_data:
                        sample_key = keys_data[0]
                        key_fields = list(sample_key.keys())
                        self.log_result("gc_keys", "GC key fields", True, 
                                      f"Sample key fields: {key_fields}")
                    else:
                        self.log_result("gc_keys", "GC keys data", False, "No GC keys found in system")
                else:
                    self.log_result("gc_keys", "GC keys data structure", False, 
                                  f"Expected list, got {type(keys_data)}", response)
                
                return keys_data
            elif response.status_code == 404:
                self.log_result("gc_keys", "GC keys admin endpoint access", False, 
                              "Endpoint does not exist (404)", response)
                return None
            else:
                self.log_result("gc_keys", "GC keys admin endpoint access", False, 
                              f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("gc_keys", "GC keys admin endpoint access", False, str(e))
            return None
    
    def test_gc_access_logs_admin_endpoint(self):
        """Test GC Access Logs Admin Endpoint: GET /api/gc/access-logs/admin"""
        print("\n=== Testing GC Access Logs Admin Endpoint ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/access-logs/admin")
            
            if response.status_code == 200:
                logs_data = response.json()
                self.log_result("gc_access_logs", "GC access logs admin endpoint access", True, 
                              f"Endpoint exists and returned data: {type(logs_data)}")
                
                if isinstance(logs_data, list):
                    self.log_result("gc_access_logs", "GC access logs data structure", True, 
                                  f"Retrieved {len(logs_data)} access logs")
                    
                    # Show sample log data if available
                    if logs_data:
                        sample_log = logs_data[0]
                        log_fields = list(sample_log.keys())
                        self.log_result("gc_access_logs", "GC access log fields", True, 
                                      f"Sample log fields: {log_fields}")
                        
                        # Check for expected fields
                        expected_fields = ["id", "projectName", "timestamp", "ip", "status"]
                        missing_fields = [field for field in expected_fields if field not in sample_log]
                        if not missing_fields:
                            self.log_result("gc_access_logs", "Access log structure validation", True, 
                                          "All expected fields present")
                        else:
                            self.log_result("gc_access_logs", "Access log structure validation", False, 
                                          f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("gc_access_logs", "GC access logs data", False, 
                                      "No access logs found in system - this explains why admin interface is empty")
                else:
                    self.log_result("gc_access_logs", "GC access logs data structure", False, 
                                  f"Expected list, got {type(logs_data)}", response)
                
                return logs_data
            elif response.status_code == 404:
                self.log_result("gc_access_logs", "GC access logs admin endpoint access", False, 
                              "Endpoint does not exist (404)", response)
                return None
            else:
                self.log_result("gc_access_logs", "GC access logs admin endpoint access", False, 
                              f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("gc_access_logs", "GC access logs admin endpoint access", False, str(e))
            return None
    
    def test_pin_generation_endpoint(self, project_id):
        """Test PIN generation for a specific project"""
        print(f"\n=== Testing PIN Generation for Project {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                self.log_result("pin_workflow", "PIN generation endpoint", True, 
                              f"PIN endpoint accessible for project {project_id}")
                
                # Check PIN data structure
                expected_fields = ["projectId", "projectName", "gcPin", "pinUsed"]
                missing_fields = [field for field in expected_fields if field not in pin_data]
                
                if not missing_fields:
                    pin_value = pin_data.get("gcPin")
                    pin_used = pin_data.get("pinUsed")
                    project_name = pin_data.get("projectName")
                    
                    self.log_result("pin_workflow", "PIN data structure", True, 
                                  f"Project: {project_name}, PIN: {pin_value}, Used: {pin_used}")
                    
                    # Validate PIN format (should be 4-digit)
                    if pin_value and len(str(pin_value)) == 4 and str(pin_value).isdigit():
                        self.log_result("pin_workflow", "PIN format validation", True, 
                                      f"PIN {pin_value} is valid 4-digit format")
                    else:
                        self.log_result("pin_workflow", "PIN format validation", False, 
                                      f"PIN {pin_value} is not valid 4-digit format")
                    
                    return pin_data
                else:
                    self.log_result("pin_workflow", "PIN data structure", False, 
                                  f"Missing fields: {missing_fields}", response)
                    return None
            else:
                self.log_result("pin_workflow", "PIN generation endpoint", False, 
                              f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("pin_workflow", "PIN generation endpoint", False, str(e))
            return None
    
    def test_secure_pin_validation(self, pin):
        """Test the new secure PIN validation endpoint"""
        print(f"\n=== Testing Secure PIN Validation with PIN {pin} ===")
        
        try:
            # Test the secure PIN validation endpoint
            validation_data = {"pin": pin}
            response = self.session.post(
                f"{self.base_url}/gc/validate-pin",
                json=validation_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                validation_result = response.json()
                self.log_result("pin_workflow", "Secure PIN validation success", True, 
                              f"PIN {pin} validated successfully")
                
                # Check validation response structure
                expected_fields = ["success", "projectId", "projectName"]
                missing_fields = [field for field in expected_fields if field not in validation_result]
                
                if not missing_fields:
                    project_id = validation_result.get("projectId")
                    project_name = validation_result.get("projectName")
                    self.log_result("pin_workflow", "PIN validation response structure", True, 
                                  f"Project: {project_name} (ID: {project_id})")
                    return validation_result
                else:
                    self.log_result("pin_workflow", "PIN validation response structure", False, 
                                  f"Missing fields: {missing_fields}", response)
                    return None
            elif response.status_code == 401:
                self.log_result("pin_workflow", "Secure PIN validation rejection", True, 
                              f"PIN {pin} correctly rejected (401 - Invalid or used PIN)")
                return None
            elif response.status_code == 404:
                self.log_result("pin_workflow", "Secure PIN validation endpoint", False, 
                              "Secure PIN validation endpoint does not exist (404)", response)
                return None
            else:
                self.log_result("pin_workflow", "Secure PIN validation", False, 
                              f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("pin_workflow", "Secure PIN validation", False, str(e))
            return None
    
    def test_gc_login_simple(self, project_id, pin):
        """Test the simple GC login endpoint"""
        print(f"\n=== Testing GC Login Simple with Project {project_id} and PIN {pin} ===")
        
        try:
            login_data = {"projectId": project_id, "pin": pin}
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                self.log_result("pin_workflow", "GC login simple success", True, 
                              f"Login successful for project {project_id}")
                
                # Check if new PIN was generated
                new_pin = login_result.get("newPin")
                if new_pin:
                    self.log_result("pin_workflow", "PIN regeneration after login", True, 
                                  f"New PIN generated: {new_pin} (old PIN: {pin})")
                    return login_result
                else:
                    self.log_result("pin_workflow", "PIN regeneration after login", False, 
                                  "No new PIN generated after login", response)
                    return login_result
            elif response.status_code == 401:
                self.log_result("pin_workflow", "GC login simple rejection", True, 
                              f"Login correctly rejected for invalid/used PIN {pin}")
                return None
            else:
                self.log_result("pin_workflow", "GC login simple", False, 
                              f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("pin_workflow", "GC login simple", False, str(e))
            return None
    
    def test_full_pin_workflow(self):
        """Test the complete PIN workflow: Generate → Validate → Login → Check Logs"""
        print("\n=== Testing Full PIN Workflow ===")
        
        # Step 1: Get projects to work with
        projects = self.test_projects_endpoint()
        if not projects:
            self.log_result("pin_workflow", "Full workflow setup", False, "No projects available for testing")
            return False
        
        # Find a project with a PIN
        test_project = None
        for project in projects:
            if project.get("gc_pin"):
                test_project = project
                break
        
        if not test_project:
            self.log_result("pin_workflow", "Full workflow setup", False, "No projects with PINs found")
            return False
        
        project_id = test_project["id"]
        project_name = test_project.get("name", "Unknown")
        
        self.log_result("pin_workflow", "Full workflow setup", True, 
                      f"Using project: {project_name} (ID: {project_id})")
        
        # Step 2: Generate fresh PIN
        pin_data = self.test_pin_generation_endpoint(project_id)
        if not pin_data:
            self.log_result("pin_workflow", "Full workflow PIN generation", False, 
                          "Could not generate PIN for workflow test")
            return False
        
        fresh_pin = pin_data.get("gcPin")
        
        # Step 3: Test secure PIN validation
        validation_result = self.test_secure_pin_validation(fresh_pin)
        
        # Step 4: Test GC login
        login_result = self.test_gc_login_simple(project_id, fresh_pin)
        
        # Step 5: Check if access logs were created
        print("\n--- Checking if access logs were created during PIN workflow ---")
        access_logs = self.test_gc_access_logs_admin_endpoint()
        
        if access_logs and len(access_logs) > 0:
            # Look for recent logs related to our test project
            recent_logs = []
            for log in access_logs:
                if log.get("projectName") == project_name:
                    recent_logs.append(log)
            
            if recent_logs:
                self.log_result("pin_workflow", "Access log creation", True, 
                              f"Found {len(recent_logs)} access logs for test project")
            else:
                self.log_result("pin_workflow", "Access log creation", False, 
                              "No access logs found for test project despite PIN usage")
        else:
            self.log_result("pin_workflow", "Access log creation", False, 
                          "No access logs found in system - logs not being created")
        
        # Step 6: Verify PIN regeneration by checking project data
        print("\n--- Verifying PIN regeneration ---")
        updated_pin_data = self.test_pin_generation_endpoint(project_id)
        if updated_pin_data:
            updated_pin = updated_pin_data.get("gcPin")
            if updated_pin != fresh_pin:
                self.log_result("pin_workflow", "PIN regeneration verification", True, 
                              f"PIN successfully regenerated: {fresh_pin} → {updated_pin}")
            else:
                self.log_result("pin_workflow", "PIN regeneration verification", False, 
                              f"PIN not regenerated, still: {fresh_pin}")
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("GC ACCESS MANAGEMENT TESTING SUMMARY")
        print("="*80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper()}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print(f"\nOVERALL: {total_passed} passed, {total_failed} failed")
        
        # Specific findings for the review request
        print("\n" + "="*80)
        print("SPECIFIC FINDINGS FOR REVIEW REQUEST")
        print("="*80)
        
        print("\n1. PROJECTS ENDPOINT (GET /api/projects):")
        if self.test_results["projects"]["failed"] == 0:
            print("   ✅ Projects endpoint working correctly")
            print("   ✅ Projects have gc_pin and gc_pin_used fields")
        else:
            print("   ❌ Issues found with projects endpoint or PIN fields")
        
        print("\n2. GC KEYS ADMIN ENDPOINT (GET /api/gc/keys/admin):")
        if any("does not exist" in error for error in self.test_results["gc_keys"]["errors"]):
            print("   ❌ CRITICAL: GC Keys Admin endpoint does not exist")
            print("   📝 RECOMMENDATION: Implement GET /api/gc/keys/admin endpoint")
        elif self.test_results["gc_keys"]["failed"] == 0:
            print("   ✅ GC Keys Admin endpoint working correctly")
        else:
            print("   ❌ Issues found with GC Keys Admin endpoint")
        
        print("\n3. GC ACCESS LOGS ADMIN ENDPOINT (GET /api/gc/access-logs/admin):")
        if any("does not exist" in error for error in self.test_results["gc_access_logs"]["errors"]):
            print("   ❌ CRITICAL: GC Access Logs Admin endpoint does not exist")
            print("   📝 RECOMMENDATION: Implement GET /api/gc/access-logs/admin endpoint")
        elif any("No access logs found" in error for error in self.test_results["gc_access_logs"]["errors"]):
            print("   ⚠️  Endpoint exists but no access logs found")
            print("   📝 RECOMMENDATION: Check if access logging is working during PIN validation")
        elif self.test_results["gc_access_logs"]["failed"] == 0:
            print("   ✅ GC Access Logs Admin endpoint working correctly")
        else:
            print("   ❌ Issues found with GC Access Logs Admin endpoint")
        
        print("\n4. FULL PIN WORKFLOW:")
        if self.test_results["pin_workflow"]["failed"] == 0:
            print("   ✅ PIN workflow working correctly")
        else:
            print("   ❌ Issues found in PIN workflow")
            print("   📝 Check PIN generation, validation, and access logging")
        
        success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"\nSUCCESS RATE: {success_rate:.1f}%")
        
        return success_rate >= 80

def main():
    """Main testing function"""
    print("GC Access Management Testing Script")
    print("="*50)
    
    tester = GCAccessTester()
    
    # Test basic connectivity first
    if not tester.test_basic_connectivity():
        print("❌ Basic connectivity failed. Exiting.")
        return False
    
    # Run all tests as specified in the review request
    print("\n🔍 TESTING AS PER REVIEW REQUEST:")
    print("1. Test Projects Endpoint for GC PIN fields")
    print("2. Test GC Keys Admin Endpoint")
    print("3. Test GC Access Logs Admin Endpoint") 
    print("4. Test Full PIN Workflow")
    
    # Execute tests
    tester.test_projects_endpoint()
    tester.test_gc_keys_admin_endpoint()
    tester.test_gc_access_logs_admin_endpoint()
    tester.test_full_pin_workflow()
    
    # Print comprehensive summary
    success = tester.print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)