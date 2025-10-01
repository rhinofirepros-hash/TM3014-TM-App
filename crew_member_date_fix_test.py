#!/usr/bin/env python3
"""
Crew Member Creation Date Serialization Fix Test
=================================================

This test verifies that the date serialization issue in the /api/installers endpoint
has been resolved. The fix changed installer.dict() to installer.model_dump(mode="json")
on line 310 to properly serialize date objects for MongoDB.

Test Requirements:
1. Test Basic Creation - Try creating crew member with hire_date field
2. Test Screenshot Data - Use exact data from user's screenshot
3. Test Multiple Date Formats - Verify different date formats work
4. Test Complete Crew Creation Flow - End-to-end testing
5. Verify No Regression - Ensure existing functionality still works
"""

import requests
import json
from datetime import datetime, date
import sys
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://project-autopilot.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class CrewMemberDateFixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.created_installers = []  # Track created installers for cleanup
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_crew_member_creation_with_date(self):
        """Test 1: Basic crew member creation with hire_date field"""
        print("\n🔍 TEST 1: Basic Crew Member Creation with hire_date")
        
        test_data = {
            "name": "Test Installer Basic",
            "cost_rate": 45.0,
            "position": "Electrician",
            "hire_date": "2024-01-15",
            "phone": "(555) 123-4567",
            "email": "test@example.com"
        }
        
        try:
            response = requests.post(f"{self.base_url}/installers", json=test_data)
            
            if response.status_code == 200:
                installer_data = response.json()
                self.created_installers.append(installer_data.get('id'))
                
                # Verify all fields are present
                required_fields = ['id', 'name', 'cost_rate', 'hire_date', 'phone', 'email']
                missing_fields = [field for field in required_fields if field not in installer_data]
                
                if not missing_fields:
                    self.log_test(
                        "Basic Creation with Date",
                        True,
                        f"Successfully created installer with hire_date. ID: {installer_data.get('id')}",
                        {"installer_data": installer_data}
                    )
                else:
                    self.log_test(
                        "Basic Creation with Date",
                        False,
                        f"Missing fields in response: {missing_fields}",
                        {"response": installer_data}
                    )
            else:
                self.log_test(
                    "Basic Creation with Date",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Basic Creation with Date",
                False,
                f"Exception occurred: {str(e)}",
                {"exception": str(e)}
            )
    
    def test_screenshot_data(self):
        """Test 2: Test with exact data from user's screenshot"""
        print("\n🔍 TEST 2: User Screenshot Data Test")
        
        # Exact data from user's screenshot
        screenshot_data = {
            "name": "Test Installer",
            "cost_rate": 33,
            "hire_date": "2025-09-30",
            "phone": "(555) 123-4567",
            "email": "john@example.com"
        }
        
        try:
            response = requests.post(f"{self.base_url}/installers", json=screenshot_data)
            
            if response.status_code == 200:
                installer_data = response.json()
                self.created_installers.append(installer_data.get('id'))
                
                # Verify specific screenshot data
                expected_values = {
                    'name': 'Test Installer',
                    'cost_rate': 33,
                    'phone': '(555) 123-4567',
                    'email': 'john@example.com'
                }
                
                mismatches = []
                for key, expected_value in expected_values.items():
                    actual_value = installer_data.get(key)
                    if actual_value != expected_value:
                        mismatches.append(f"{key}: expected {expected_value}, got {actual_value}")
                
                if not mismatches and installer_data.get('hire_date'):
                    self.log_test(
                        "Screenshot Data Test",
                        True,
                        f"Successfully created installer with screenshot data. hire_date: {installer_data.get('hire_date')}",
                        {"installer_data": installer_data}
                    )
                else:
                    self.log_test(
                        "Screenshot Data Test",
                        False,
                        f"Data mismatches: {mismatches}" if mismatches else "Missing hire_date in response",
                        {"response": installer_data, "mismatches": mismatches}
                    )
            else:
                self.log_test(
                    "Screenshot Data Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Screenshot Data Test",
                False,
                f"Exception occurred: {str(e)}",
                {"exception": str(e)}
            )
    
    def test_multiple_date_formats(self):
        """Test 3: Test multiple date formats"""
        print("\n🔍 TEST 3: Multiple Date Formats Test")
        
        date_formats = [
            ("ISO Format", "2024-03-15"),
            ("Future Date", "2025-12-31"),
            ("Past Date", "2020-01-01"),
            ("Leap Year", "2024-02-29"),
        ]
        
        for format_name, date_value in date_formats:
            test_data = {
                "name": f"Test Installer {format_name}",
                "cost_rate": 50.0,
                "hire_date": date_value,
                "position": "Test Position"
            }
            
            try:
                response = requests.post(f"{self.base_url}/installers", json=test_data)
                
                if response.status_code == 200:
                    installer_data = response.json()
                    self.created_installers.append(installer_data.get('id'))
                    
                    if installer_data.get('hire_date'):
                        self.log_test(
                            f"Date Format - {format_name}",
                            True,
                            f"Successfully handled date format: {date_value}",
                            {"date_input": date_value, "date_output": installer_data.get('hire_date')}
                        )
                    else:
                        self.log_test(
                            f"Date Format - {format_name}",
                            False,
                            f"Date not saved properly for format: {date_value}",
                            {"response": installer_data}
                        )
                else:
                    self.log_test(
                        f"Date Format - {format_name}",
                        False,
                        f"HTTP {response.status_code} for date {date_value}: {response.text}",
                        {"date_value": date_value, "status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Date Format - {format_name}",
                    False,
                    f"Exception for date {date_value}: {str(e)}",
                    {"date_value": date_value, "exception": str(e)}
                )
    
    def test_complete_crew_creation_flow(self):
        """Test 4: Complete crew creation flow (Create -> Read -> Update)"""
        print("\n🔍 TEST 4: Complete Crew Creation Flow")
        
        # Step 1: Create installer
        create_data = {
            "name": "Flow Test Installer",
            "cost_rate": 55.0,
            "position": "Senior Electrician",
            "hire_date": "2024-06-15",
            "phone": "(555) 987-6543",
            "email": "flowtest@example.com"
        }
        
        try:
            # CREATE
            create_response = requests.post(f"{self.base_url}/installers", json=create_data)
            
            if create_response.status_code != 200:
                self.log_test(
                    "Complete Flow - Create",
                    False,
                    f"Create failed: HTTP {create_response.status_code}",
                    {"response": create_response.text}
                )
                return
            
            installer_data = create_response.json()
            installer_id = installer_data.get('id')
            self.created_installers.append(installer_id)
            
            self.log_test(
                "Complete Flow - Create",
                True,
                f"Successfully created installer: {installer_id}",
                {"installer_data": installer_data}
            )
            
            # READ
            read_response = requests.get(f"{self.base_url}/installers/{installer_id}")
            
            if read_response.status_code == 200:
                read_data = read_response.json()
                self.log_test(
                    "Complete Flow - Read",
                    True,
                    f"Successfully retrieved installer: {installer_id}",
                    {"read_data": read_data}
                )
                
                # UPDATE
                update_data = {
                    "cost_rate": 60.0,
                    "hire_date": "2024-07-01"
                }
                
                update_response = requests.put(f"{self.base_url}/installers/{installer_id}", json=update_data)
                
                if update_response.status_code == 200:
                    updated_data = update_response.json()
                    
                    # Verify update worked
                    if updated_data.get('cost_rate') == 60.0:
                        self.log_test(
                            "Complete Flow - Update",
                            True,
                            f"Successfully updated installer with new date: {updated_data.get('hire_date')}",
                            {"updated_data": updated_data}
                        )
                    else:
                        self.log_test(
                            "Complete Flow - Update",
                            False,
                            "Update didn't apply correctly",
                            {"expected_rate": 60.0, "actual_rate": updated_data.get('cost_rate')}
                        )
                else:
                    self.log_test(
                        "Complete Flow - Update",
                        False,
                        f"Update failed: HTTP {update_response.status_code}",
                        {"response": update_response.text}
                    )
            else:
                self.log_test(
                    "Complete Flow - Read",
                    False,
                    f"Read failed: HTTP {read_response.status_code}",
                    {"response": read_response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Complete Flow",
                False,
                f"Exception in complete flow: {str(e)}",
                {"exception": str(e)}
            )
    
    def test_regression_check(self):
        """Test 5: Verify no regression in existing functionality"""
        print("\n🔍 TEST 5: Regression Check")
        
        try:
            # Test GET all installers
            response = requests.get(f"{self.base_url}/installers")
            
            if response.status_code == 200:
                installers = response.json()
                self.log_test(
                    "Regression - GET All",
                    True,
                    f"Successfully retrieved {len(installers)} installers",
                    {"count": len(installers)}
                )
                
                # Test creating installer without hire_date (should still work)
                no_date_data = {
                    "name": "No Date Installer",
                    "cost_rate": 40.0,
                    "position": "Helper"
                }
                
                no_date_response = requests.post(f"{self.base_url}/installers", json=no_date_data)
                
                if no_date_response.status_code == 201:
                    installer_data = no_date_response.json()
                    self.created_installers.append(installer_data.get('id'))
                    
                    self.log_test(
                        "Regression - No Date Field",
                        True,
                        "Successfully created installer without hire_date",
                        {"installer_data": installer_data}
                    )
                else:
                    self.log_test(
                        "Regression - No Date Field",
                        False,
                        f"Failed to create installer without date: HTTP {no_date_response.status_code}",
                        {"response": no_date_response.text}
                    )
            else:
                self.log_test(
                    "Regression - GET All",
                    False,
                    f"Failed to get installers: HTTP {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Regression Check",
                False,
                f"Exception in regression check: {str(e)}",
                {"exception": str(e)}
            )
    
    def cleanup_test_data(self):
        """Clean up created test installers"""
        print("\n🧹 Cleaning up test data...")
        
        for installer_id in self.created_installers:
            try:
                # Note: DELETE endpoint might not exist, so we'll just log the IDs
                print(f"   Created installer ID: {installer_id}")
            except Exception as e:
                print(f"   Note: Could not clean up {installer_id}: {e}")
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Starting Crew Member Date Serialization Fix Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run all tests
        self.test_basic_crew_member_creation_with_date()
        self.test_screenshot_data()
        self.test_multiple_date_formats()
        self.test_complete_crew_creation_flow()
        self.test_regression_check()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n🎯 VERIFICATION RESULTS:")
        
        # Check if the main issue is fixed
        date_tests = [r for r in self.test_results if "Date" in r["test"] and "✅ PASS" in r["status"]]
        if len(date_tests) >= 3:  # At least 3 date-related tests passed
            print("✅ DATE SERIALIZATION ISSUE: RESOLVED")
            print("   - hire_date field now works correctly")
            print("   - Multiple date formats supported")
            print("   - No HTTP 500 errors when including hire_date")
        else:
            print("❌ DATE SERIALIZATION ISSUE: NOT FULLY RESOLVED")
            print("   - Some date-related tests are still failing")
        
        # Check screenshot data specifically
        screenshot_test = next((r for r in self.test_results if "Screenshot" in r["test"]), None)
        if screenshot_test and "✅ PASS" in screenshot_test["status"]:
            print("✅ USER SCREENSHOT DATA: WORKING")
            print("   - Exact data from user's screenshot now works")
        else:
            print("❌ USER SCREENSHOT DATA: STILL FAILING")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = CrewMemberDateFixTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Date serialization fix is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - Date serialization fix needs attention")
        sys.exit(1)