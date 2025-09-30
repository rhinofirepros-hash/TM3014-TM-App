#!/usr/bin/env python3
"""
GC Dashboard API Focused Testing - Specific test for the review request
Testing GET /api/gc/dashboard/68cc802f8d44fcd8015b39b8 as requested
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://firepro-auth-hub.preview.emergentagent.com/api"

class GCDashboardFocusedTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "gc_dashboard": {"passed": 0, "failed": 0, "errors": []}
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
                error_msg += f" (Status: {response.status_code})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_specific_gc_dashboard_endpoint(self):
        """Test the specific GC Dashboard API endpoint as requested in the review"""
        print("\n=== Testing Specific GC Dashboard API Endpoint ===")
        print("Review Request: Test GET /api/gc/dashboard/68cc802f8d44fcd8015b39b8")
        
        project_id = "68cc802f8d44fcd8015b39b8"
        endpoint = f"{self.base_url}/gc/dashboard/{project_id}"
        
        print(f"Testing endpoint: {endpoint}")
        
        try:
            # Record start time for response time measurement
            start_time = time.time()
            
            # Make the API request
            response = self.session.get(endpoint)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            print(f"Response received in: {response_time:.3f} seconds")
            
            # Test 1: Check if API returns 200 OK
            if response.status_code == 200:
                self.log_result("gc_dashboard", "API Response Status", True, f"200 OK received")
                
                # Test 2: Check response time (should be under 2-3 seconds)
                if response_time <= 3.0:
                    if response_time <= 2.0:
                        self.log_result("gc_dashboard", "Response Time (Excellent)", True, f"{response_time:.3f}s (under 2s - excellent performance)")
                    else:
                        self.log_result("gc_dashboard", "Response Time (Good)", True, f"{response_time:.3f}s (under 3s - good performance)")
                else:
                    self.log_result("gc_dashboard", "Response Time", False, f"{response_time:.3f}s (exceeds 3s limit)")
                
                # Test 3: Verify response is valid JSON
                try:
                    response_data = response.json()
                    self.log_result("gc_dashboard", "JSON Response Format", True, "Valid JSON response received")
                    
                    # Test 4: Check for required dashboard fields
                    required_fields = [
                        "projectId", "projectName", "crewSummary", "tmTagSummary", 
                        "phases", "inspections", "narrative", "lastUpdated"
                    ]
                    
                    missing_fields = []
                    present_fields = []
                    for field in required_fields:
                        if field in response_data:
                            present_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        self.log_result("gc_dashboard", "Required Fields Present", True, f"All {len(required_fields)} required fields present")
                        
                        # Test 5: Verify data structure and content
                        self.verify_dashboard_data_structure(response_data)
                        
                        # Test 6: Print dashboard summary for verification
                        self.print_dashboard_summary(response_data)
                        
                        # Test 7: Check for data formatting issues
                        self.check_data_formatting(response_data)
                        
                    else:
                        self.log_result("gc_dashboard", "Required Fields Present", False, f"Missing fields: {missing_fields}")
                        print(f"Present fields: {present_fields}")
                        
                except json.JSONDecodeError as e:
                    self.log_result("gc_dashboard", "JSON Response Format", False, f"Invalid JSON: {str(e)}")
                    print(f"Raw response: {response.text[:500]}")
                    
            elif response.status_code == 404:
                self.log_result("gc_dashboard", "API Response Status", False, f"Project not found (404) - Project ID {project_id} may not exist")
            elif response.status_code == 500:
                self.log_result("gc_dashboard", "API Response Status", False, f"Internal Server Error (500) - Backend issue")
                print(f"Error response: {response.text[:500]}")
            else:
                self.log_result("gc_dashboard", "API Response Status", False, f"Unexpected status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
        except requests.exceptions.Timeout:
            self.log_result("gc_dashboard", "API Response Status", False, "Request timeout - API not responding within timeout period")
        except requests.exceptions.ConnectionError:
            self.log_result("gc_dashboard", "API Response Status", False, "Connection error - Cannot reach API server")
        except Exception as e:
            self.log_result("gc_dashboard", "API Response Status", False, f"Unexpected error: {str(e)}")
    
    def verify_dashboard_data_structure(self, data):
        """Verify the structure and content of dashboard data"""
        print("\n--- Verifying Dashboard Data Structure ---")
        
        # Check project basic info
        project_id = data.get("projectId")
        project_name = data.get("projectName")
        if project_id and project_name:
            self.log_result("gc_dashboard", "Project Info", True, f"Project ID: {project_id}, Name: {project_name}")
        else:
            self.log_result("gc_dashboard", "Project Info", False, "Missing project ID or name")
        
        # Check crew summary structure
        crew_summary = data.get("crewSummary", {})
        if isinstance(crew_summary, dict):
            crew_fields = ["totalHours", "totalDays"]
            crew_present = [f for f in crew_fields if f in crew_summary]
            if len(crew_present) >= 2:
                self.log_result("gc_dashboard", "Crew Summary Structure", True, f"Crew fields present: {crew_present}")
            else:
                self.log_result("gc_dashboard", "Crew Summary Structure", False, f"Missing crew fields. Present: {crew_present}")
        else:
            self.log_result("gc_dashboard", "Crew Summary Structure", False, "crewSummary is not a dictionary")
        
        # Check T&M tag summary structure
        tm_summary = data.get("tmTagSummary", {})
        if isinstance(tm_summary, dict):
            tm_fields = ["totalTags", "totalHours"]
            tm_present = [f for f in tm_fields if f in tm_summary]
            if len(tm_present) >= 2:
                self.log_result("gc_dashboard", "T&M Summary Structure", True, f"T&M fields present: {tm_present}")
            else:
                self.log_result("gc_dashboard", "T&M Summary Structure", False, f"Missing T&M fields. Present: {tm_present}")
        else:
            self.log_result("gc_dashboard", "T&M Summary Structure", False, "tmTagSummary is not a dictionary")
        
        # Check phases structure
        phases = data.get("phases", [])
        if isinstance(phases, list):
            self.log_result("gc_dashboard", "Phases Structure", True, f"Phases is a list with {len(phases)} items")
            if len(phases) > 0:
                # Check first phase structure
                first_phase = phases[0]
                phase_fields = ["id", "projectId", "phase", "percentComplete"]
                phase_present = [f for f in phase_fields if f in first_phase]
                if len(phase_present) >= 3:
                    self.log_result("gc_dashboard", "Phase Data Structure", True, f"Phase fields present: {phase_present}")
                else:
                    self.log_result("gc_dashboard", "Phase Data Structure", False, f"Missing phase fields. Present: {phase_present}")
        else:
            self.log_result("gc_dashboard", "Phases Structure", False, "phases is not a list")
        
        # Check inspections structure
        inspections = data.get("inspections", [])
        if isinstance(inspections, list):
            self.log_result("gc_dashboard", "Inspections Structure", True, f"Inspections is a list with {len(inspections)} items")
        else:
            self.log_result("gc_dashboard", "Inspections Structure", False, "inspections is not a list")
    
    def check_data_formatting(self, data):
        """Check for data formatting problems"""
        print("\n--- Checking Data Formatting ---")
        
        # Check for null/undefined values in critical fields
        critical_fields = ["projectId", "projectName", "crewSummary", "tmTagSummary"]
        formatting_issues = []
        
        for field in critical_fields:
            value = data.get(field)
            if value is None:
                formatting_issues.append(f"{field} is null")
            elif isinstance(value, str) and value.strip() == "":
                formatting_issues.append(f"{field} is empty string")
        
        # Check numeric fields for proper formatting
        crew_summary = data.get("crewSummary", {})
        if isinstance(crew_summary, dict):
            total_hours = crew_summary.get("totalHours")
            total_days = crew_summary.get("totalDays")
            
            if not isinstance(total_hours, (int, float)):
                formatting_issues.append(f"crewSummary.totalHours is not numeric: {type(total_hours)}")
            if not isinstance(total_days, (int, float)):
                formatting_issues.append(f"crewSummary.totalDays is not numeric: {type(total_days)}")
        
        tm_summary = data.get("tmTagSummary", {})
        if isinstance(tm_summary, dict):
            total_tags = tm_summary.get("totalTags")
            total_hours = tm_summary.get("totalHours")
            
            if not isinstance(total_tags, (int, float)):
                formatting_issues.append(f"tmTagSummary.totalTags is not numeric: {type(total_tags)}")
            if not isinstance(total_hours, (int, float)):
                formatting_issues.append(f"tmTagSummary.totalHours is not numeric: {type(total_hours)}")
        
        if not formatting_issues:
            self.log_result("gc_dashboard", "Data Formatting", True, "No data formatting issues found")
        else:
            self.log_result("gc_dashboard", "Data Formatting", False, f"Formatting issues: {formatting_issues}")
    
    def print_dashboard_summary(self, data):
        """Print a summary of the dashboard data for verification"""
        print("\n--- Dashboard Data Summary ---")
        print(f"Project ID: {data.get('projectId', 'N/A')}")
        print(f"Project Name: {data.get('projectName', 'N/A')}")
        print(f"Project Status: {data.get('projectStatus', 'N/A')}")
        print(f"Overall Progress: {data.get('overallProgress', 'N/A')}%")
        
        crew_summary = data.get("crewSummary", {})
        print(f"\nCrew Summary:")
        print(f"  - Total Hours: {crew_summary.get('totalHours', 'N/A')}")
        print(f"  - Total Days: {crew_summary.get('totalDays', 'N/A')}")
        print(f"  - Active Crew Members: {crew_summary.get('activeCrewMembers', 'N/A')}")
        
        tm_summary = data.get("tmTagSummary", {})
        print(f"\nT&M Tag Summary:")
        print(f"  - Total Tags: {tm_summary.get('totalTags', 'N/A')}")
        print(f"  - Submitted Tags: {tm_summary.get('submittedTags', 'N/A')}")
        print(f"  - Approved Tags: {tm_summary.get('approvedTags', 'N/A')}")
        print(f"  - Total Hours: {tm_summary.get('totalHours', 'N/A')}")
        
        phases = data.get("phases", [])
        print(f"\nPhases: {len(phases)} items")
        for i, phase in enumerate(phases[:3]):  # Show first 3 phases
            print(f"  - Phase {i+1}: {phase.get('phase', 'N/A')} ({phase.get('percentComplete', 'N/A')}% complete)")
        
        inspections = data.get("inspections", [])
        print(f"\nInspections: {len(inspections)} items")
        for i, inspection in enumerate(inspections[:3]):  # Show first 3 inspections
            print(f"  - Inspection {i+1}: {inspection.get('inspectionType', 'N/A')} ({inspection.get('result', 'N/A')})")
        
        materials = data.get("materials", [])
        print(f"\nMaterials: {len(materials)} items")
        
        narrative = data.get("narrative", "")
        print(f"\nNarrative: {narrative[:100]}{'...' if len(narrative) > 100 else ''}")
        
        last_updated = data.get("lastUpdated", "N/A")
        print(f"Last Updated: {last_updated}")
    
    def run_focused_test(self):
        """Run the focused GC Dashboard test"""
        print("🎯 GC DASHBOARD API FOCUSED TESTING")
        print("="*50)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Review Request: Verify GC Dashboard API responds correctly")
        
        # Test the specific endpoint requested
        self.test_specific_gc_dashboard_endpoint()
        
        # Print final results
        self.print_final_results()
    
    def print_final_results(self):
        """Print final test results summary"""
        print("\n" + "="*60)
        print("🎯 GC DASHBOARD API TEST RESULTS")
        print("="*60)
        
        total_passed = sum(category["passed"] for category in self.test_results.values())
        total_failed = sum(category["failed"] for category in self.test_results.values())
        total_tests = total_passed + total_failed
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"📊 Overall Results: {total_passed}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        else:
            print("📊 No tests were executed")
        
        for category, results in self.test_results.items():
            if results["passed"] > 0 or results["failed"] > 0:
                print(f"\n{category.upper()}:")
                print(f"  ✅ Passed: {results['passed']}")
                print(f"  ❌ Failed: {results['failed']}")
                
                if results["errors"]:
                    print("  🔍 Errors:")
                    for error in results["errors"]:
                        print(f"    - {error}")
        
        print("\n" + "="*60)
        
        # Provide specific feedback for the review request
        if total_failed == 0:
            print("🎉 SUCCESS: GC Dashboard API is responding correctly!")
            print("✅ The API returns 200 OK with proper dashboard data")
            print("✅ Response time is within acceptable limits (under 2-3 seconds)")
            print("✅ All required fields are present in the response")
            print("✅ No data formatting problems detected")
            print("\n💡 CONCLUSION: The frontend 'Loading project dashboard...' issue")
            print("   is NOT caused by backend API problems. The API is working perfectly.")
            print("   The issue may be in the frontend code or network connectivity.")
        else:
            print("⚠️  ISSUES FOUND: GC Dashboard API has problems")
            print("❌ The frontend 'Loading project dashboard...' issue may be due to:")
            for category, results in self.test_results.items():
                for error in results["errors"]:
                    print(f"   - {error}")

if __name__ == "__main__":
    tester = GCDashboardFocusedTester()
    tester.run_focused_test()