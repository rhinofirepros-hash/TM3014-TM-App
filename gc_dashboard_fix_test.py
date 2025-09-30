#!/usr/bin/env python3
"""
GC Dashboard API Fix Testing - Focused Test
Tests the specific fix for database schema compatibility issue
"""

import requests
import json
from datetime import datetime
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"

class GCDashboardFixTester:
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
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:500]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_gc_dashboard_api_fix(self):
        """Test the GC Dashboard API fix for confirmed project IDs"""
        print("\n=== Testing GC Dashboard API Fix ===")
        print("Testing database schema compatibility fix where unified server was only looking for 'id' field but projects use '_id' field")
        
        # Confirmed project IDs from the review request
        project_ids = [
            "68cc802f8d44fcd8015b39b8",  # Primary test ID
            "68cc802f8d44fcd8015b39b9",  # Additional test ID
            "68cc802f8d44fcd8015b39ba"   # Additional test ID
        ]
        
        for project_id in project_ids:
            print(f"\n--- Testing Project ID: {project_id} ---")
            
            try:
                # Test the GC Dashboard endpoint
                response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
                
                if response.status_code == 200:
                    # Success! The fix worked
                    response_data = response.json()
                    
                    # Verify the response structure
                    expected_fields = ["projectId", "projectName", "crewSummary", "tmTagSummary"]
                    missing_fields = [field for field in expected_fields if field not in response_data]
                    
                    if not missing_fields:
                        self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", True, 
                                      f"Returns 200 OK with complete dashboard data. Project: {response_data.get('projectName', 'Unknown')}")
                        
                        # Log some key metrics from the response
                        crew_summary = response_data.get("crewSummary", {})
                        tm_tag_summary = response_data.get("tmTagSummary", {})
                        materials = response_data.get("materials", [])
                        
                        print(f"   📊 Dashboard Data Summary:")
                        print(f"   - Project Name: {response_data.get('projectName', 'N/A')}")
                        print(f"   - Total Hours: {crew_summary.get('totalHours', 0)}")
                        print(f"   - Work Days: {crew_summary.get('totalDays', 0)}")
                        print(f"   - Materials Count: {len(materials)}")
                        print(f"   - T&M Tags Count: {tm_tag_summary.get('totalTags', 0)}")
                        
                    else:
                        self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", False, 
                                      f"Missing expected fields: {missing_fields}", response)
                        
                elif response.status_code == 404:
                    # This was the original problem - should now be fixed
                    self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", False, 
                                  "Still returns 404 - fix may not be working", response)
                    
                elif response.status_code == 500:
                    # Server error - might indicate database issues
                    self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", False, 
                                  "Server error - possible database schema issue", response)
                    
                else:
                    # Other unexpected status codes
                    self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", False, 
                                  f"Unexpected status code: {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", False, str(e))
    
    def test_gc_dashboard_error_handling(self):
        """Test GC Dashboard API error handling with invalid project ID"""
        print("\n=== Testing GC Dashboard Error Handling ===")
        
        # Test with invalid project ID
        invalid_project_id = "invalid-project-id-12345"
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{invalid_project_id}")
            
            if response.status_code == 404:
                self.log_result("gc_dashboard", "Invalid Project ID handling", True, 
                              "Correctly returns 404 for invalid project ID")
            elif response.status_code == 400:
                self.log_result("gc_dashboard", "Invalid Project ID handling", True, 
                              "Correctly returns 400 for invalid project ID")
            else:
                self.log_result("gc_dashboard", "Invalid Project ID handling", False, 
                              f"Unexpected status for invalid ID: {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_dashboard", "Invalid Project ID handling", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("GC DASHBOARD API FIX TEST SUMMARY")
        print("="*60)
        
        total_passed = sum(results["passed"] for results in self.test_results.values())
        total_failed = sum(results["failed"] for results in self.test_results.values())
        total_tests = total_passed + total_failed
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Print detailed results
        for category, results in self.test_results.items():
            if results["failed"] > 0:
                print(f"\n❌ {category.upper()} FAILURES:")
                for error in results["errors"]:
                    print(f"   - {error}")
        
        if total_failed == 0:
            print("\n🎉 ALL TESTS PASSED! GC Dashboard API fix is working correctly.")
        else:
            print(f"\n⚠️  {total_failed} test(s) failed. Please review the issues above.")
        
        return total_failed == 0

def main():
    """Main test execution"""
    print("GC Dashboard API Fix Testing")
    print("="*60)
    print("Testing the fix for database schema compatibility issue")
    print("where unified server was only looking for 'id' field but projects use '_id' field")
    print("="*60)
    
    tester = GCDashboardFixTester()
    
    # Run the specific tests for the fix
    tester.test_gc_dashboard_api_fix()
    tester.test_gc_dashboard_error_handling()
    
    # Print summary
    success = tester.print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)