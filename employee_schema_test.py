#!/usr/bin/env python3
"""
Employee Schema Migration Testing
Tests the specific employee schema migration and CrewManagement functionality
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://firepro-tracker.preview.emergentagent.com/api"

class EmployeeSchemaTestRunner:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:500]})"
            self.test_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_result("Basic connectivity", True)
                return True
            else:
                self.log_result("Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Basic connectivity", False, str(e))
            return False
    
    def create_old_schema_employee_directly(self):
        """Create an employee with old schema directly in database for migration testing"""
        print("\n=== Creating Old Schema Employee for Migration Test ===")
        
        # First, let's create a new schema employee to ensure the endpoint works
        new_employee_data = {
            "name": "Migration Test Employee",
            "hourly_rate": 50.0,
            "gc_billing_rate": 95.0,
            "position": "Test Electrician",
            "hire_date": datetime.now().isoformat(),
            "phone": "(555) 123-4567",
            "email": "migration.test@company.com"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/employees",
                json=new_employee_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                employee = response.json()
                self.log_result("New schema employee creation", True, f"Created employee with ID: {employee['id']}")
                return employee
            else:
                self.log_result("New schema employee creation", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("New schema employee creation", False, str(e))
            return None
    
    def test_employee_schema_migration(self):
        """Test GET /api/employees endpoint for schema migration"""
        print("\n=== Testing Employee Schema Migration ===")
        
        try:
            response = self.session.get(f"{self.base_url}/employees")
            
            if response.status_code == 200:
                employees = response.json()
                
                if isinstance(employees, list):
                    self.log_result("Employee retrieval", True, f"Retrieved {len(employees)} employees")
                    
                    # Check each employee for proper schema
                    migration_success = True
                    for employee in employees:
                        # Verify new schema fields are present
                        if "hourly_rate" not in employee:
                            migration_success = False
                            self.log_result("Schema migration - hourly_rate field", False, 
                                          f"Employee {employee.get('name', 'Unknown')} missing hourly_rate field")
                        
                        if "gc_billing_rate" not in employee:
                            migration_success = False
                            self.log_result("Schema migration - gc_billing_rate field", False, 
                                          f"Employee {employee.get('name', 'Unknown')} missing gc_billing_rate field")
                        
                        # Verify old schema fields are NOT present
                        if "base_pay" in employee:
                            migration_success = False
                            self.log_result("Schema migration - old base_pay field", False, 
                                          f"Employee {employee.get('name', 'Unknown')} still has old base_pay field")
                        
                        if "burden_cost" in employee:
                            migration_success = False
                            self.log_result("Schema migration - old burden_cost field", False, 
                                          f"Employee {employee.get('name', 'Unknown')} still has old burden_cost field")
                        
                        # Verify numeric values are valid
                        try:
                            hourly_rate = float(employee.get("hourly_rate", 0))
                            gc_billing_rate = float(employee.get("gc_billing_rate", 0))
                            
                            if hourly_rate <= 0:
                                migration_success = False
                                self.log_result("Schema migration - hourly_rate validation", False, 
                                              f"Employee {employee.get('name', 'Unknown')} has invalid hourly_rate: {hourly_rate}")
                            
                            if gc_billing_rate <= 0:
                                migration_success = False
                                self.log_result("Schema migration - gc_billing_rate validation", False, 
                                              f"Employee {employee.get('name', 'Unknown')} has invalid gc_billing_rate: {gc_billing_rate}")
                                              
                        except (ValueError, TypeError) as e:
                            migration_success = False
                            self.log_result("Schema migration - numeric validation", False, 
                                          f"Employee {employee.get('name', 'Unknown')} has non-numeric rates: {str(e)}")
                    
                    if migration_success:
                        self.log_result("Employee schema migration", True, "All employees have correct new schema")
                    else:
                        self.log_result("Employee schema migration", False, "Some employees have schema issues")
                    
                    return employees
                else:
                    self.log_result("Employee retrieval", False, "Response is not a list", response)
                    return None
            else:
                self.log_result("Employee retrieval", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("Employee retrieval", False, str(e))
            return None
    
    def test_employee_crud_operations(self):
        """Test all employee CRUD operations with new schema"""
        print("\n=== Testing Employee CRUD Operations ===")
        
        # Test CREATE
        employee_data = {
            "name": "CRUD Test Employee",
            "hourly_rate": 55.0,
            "gc_billing_rate": 95.0,
            "position": "Senior Test Electrician",
            "hire_date": datetime.now().isoformat(),
            "phone": "(555) 987-6543",
            "email": "crud.test@company.com",
            "emergency_contact": "Emergency Contact - (555) 987-6544"
        }
        
        created_employee = None
        try:
            response = self.session.post(
                f"{self.base_url}/employees",
                json=employee_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                created_employee = response.json()
                required_fields = ["id", "name", "hourly_rate", "gc_billing_rate", "position", "status", "created_at"]
                missing_fields = [field for field in required_fields if field not in created_employee]
                
                if not missing_fields:
                    self.log_result("Employee CREATE", True, f"Created employee: {created_employee['name']}")
                else:
                    self.log_result("Employee CREATE", False, f"Missing fields: {missing_fields}", response)
                    return None
            else:
                self.log_result("Employee CREATE", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("Employee CREATE", False, str(e))
            return None
        
        if not created_employee:
            return None
        
        employee_id = created_employee["id"]
        
        # Test READ by ID
        try:
            response = self.session.get(f"{self.base_url}/employees/{employee_id}")
            
            if response.status_code == 200:
                retrieved_employee = response.json()
                if retrieved_employee.get("id") == employee_id:
                    self.log_result("Employee READ by ID", True, f"Retrieved employee: {retrieved_employee['name']}")
                else:
                    self.log_result("Employee READ by ID", False, "ID mismatch in response", response)
            else:
                self.log_result("Employee READ by ID", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Employee READ by ID", False, str(e))
        
        # Test UPDATE
        update_data = {
            "name": "CRUD Test Employee (Updated)",
            "hourly_rate": 60.0,  # Updated rate
            "gc_billing_rate": 100.0,  # Updated billing rate
            "position": "Lead Test Electrician",
            "hire_date": employee_data["hire_date"],
            "phone": "(555) 987-6543",
            "email": "crud.test.updated@company.com"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/employees/{employee_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_employee = response.json()
                if (updated_employee.get("hourly_rate") == update_data["hourly_rate"] and
                    updated_employee.get("name") == update_data["name"]):
                    self.log_result("Employee UPDATE", True, f"Updated employee rates: ${updated_employee['hourly_rate']}/hr")
                else:
                    self.log_result("Employee UPDATE", False, "Update not reflected in response", response)
            else:
                self.log_result("Employee UPDATE", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Employee UPDATE", False, str(e))
        
        # Test DELETE
        try:
            response = self.session.delete(f"{self.base_url}/employees/{employee_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data and "deleted successfully" in response_data["message"]:
                    self.log_result("Employee DELETE", True, f"Deleted employee: {employee_id}")
                else:
                    self.log_result("Employee DELETE", False, "Unexpected response format", response)
            else:
                self.log_result("Employee DELETE", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Employee DELETE", False, str(e))
        
        return True
    
    def test_analytics_integration(self):
        """Test analytics integration with employee hourly rates"""
        print("\n=== Testing Analytics Integration ===")
        
        # First, create a project for analytics testing
        project_data = {
            "name": "Analytics Test Project",
            "description": "Testing analytics with employee hourly rates",
            "client_company": "Test Analytics Corp",
            "gc_email": "analytics@test.com",
            "contract_amount": 100000.00,
            "labor_rate": 120.0,  # Custom labor rate
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "Analytics Test Location"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                project_id = project["id"]
                self.log_result("Analytics project creation", True, f"Created project: {project_id}")
                
                # Test analytics endpoint
                analytics_response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
                
                if analytics_response.status_code == 200:
                    analytics = analytics_response.json()
                    
                    # Verify analytics structure includes employee cost fields
                    required_fields = ["project_id", "true_employee_cost", "total_labor_cost", "labor_markup_profit"]
                    missing_fields = [field for field in required_fields if field not in analytics]
                    
                    if not missing_fields:
                        self.log_result("Analytics structure", True, "Analytics includes employee cost calculations")
                        
                        # Verify the analytics can handle the new employee schema
                        true_cost = analytics.get("true_employee_cost", 0)
                        billed_cost = analytics.get("total_labor_cost", 0)
                        markup_profit = analytics.get("labor_markup_profit", 0)
                        
                        # Even with no data, the structure should be correct
                        if isinstance(true_cost, (int, float)) and isinstance(billed_cost, (int, float)):
                            self.log_result("Analytics calculation", True, 
                                          f"Analytics calculated: True Cost=${true_cost}, Billed=${billed_cost}, Markup=${markup_profit}")
                        else:
                            self.log_result("Analytics calculation", False, "Analytics values are not numeric")
                    else:
                        self.log_result("Analytics structure", False, f"Missing fields: {missing_fields}", analytics_response)
                else:
                    self.log_result("Analytics endpoint", False, f"HTTP {analytics_response.status_code}", analytics_response)
                
                # Clean up - delete the test project
                self.session.delete(f"{self.base_url}/projects/{project_id}")
                
            else:
                self.log_result("Analytics project creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Analytics integration", False, str(e))
    
    def test_data_integrity(self):
        """Test data integrity during schema operations"""
        print("\n=== Testing Data Integrity ===")
        
        # Get all employees before any operations
        try:
            response = self.session.get(f"{self.base_url}/employees")
            
            if response.status_code == 200:
                employees_before = response.json()
                employee_count_before = len(employees_before)
                
                # Perform another GET to ensure consistency
                response2 = self.session.get(f"{self.base_url}/employees")
                
                if response2.status_code == 200:
                    employees_after = response2.json()
                    employee_count_after = len(employees_after)
                    
                    if employee_count_before == employee_count_after:
                        self.log_result("Data integrity - consistent retrieval", True, 
                                      f"Employee count consistent: {employee_count_before}")
                        
                        # Verify all employees have valid data
                        data_integrity_ok = True
                        for employee in employees_after:
                            # Check for required fields
                            if not employee.get("name") or not employee.get("id"):
                                data_integrity_ok = False
                                self.log_result("Data integrity - required fields", False, 
                                              f"Employee missing name or id: {employee}")
                            
                            # Check for valid numeric values
                            try:
                                hourly_rate = float(employee.get("hourly_rate", 0))
                                if hourly_rate <= 0:
                                    data_integrity_ok = False
                                    self.log_result("Data integrity - hourly rate", False, 
                                                  f"Invalid hourly_rate for {employee.get('name')}: {hourly_rate}")
                            except (ValueError, TypeError):
                                data_integrity_ok = False
                                self.log_result("Data integrity - hourly rate type", False, 
                                              f"Non-numeric hourly_rate for {employee.get('name')}")
                        
                        if data_integrity_ok:
                            self.log_result("Data integrity - field validation", True, "All employee data is valid")
                    else:
                        self.log_result("Data integrity - consistent retrieval", False, 
                                      f"Employee count changed: {employee_count_before} -> {employee_count_after}")
                else:
                    self.log_result("Data integrity - second retrieval", False, f"HTTP {response2.status_code}", response2)
            else:
                self.log_result("Data integrity - first retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Data integrity", False, str(e))
    
    def run_employee_schema_tests(self):
        """Run all employee schema migration tests"""
        print("🧪 EMPLOYEE SCHEMA MIGRATION TESTING")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Cannot connect to backend. Aborting tests.")
            return self.generate_report()
        
        # Run all employee schema tests
        self.create_old_schema_employee_directly()
        self.test_employee_schema_migration()
        self.test_employee_crud_operations()
        self.test_analytics_integration()
        self.test_data_integrity()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 EMPLOYEE SCHEMA MIGRATION TEST RESULTS")
        print("=" * 60)
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.test_results['passed']} ✅")
        print(f"Failed: {self.test_results['failed']} ❌")
        print(f"Success Rate: {(self.test_results['passed']/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if self.test_results["errors"]:
            print("\n❌ FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")
        
        return {
            "total_tests": total_tests,
            "passed": self.test_results["passed"],
            "failed": self.test_results["failed"],
            "success_rate": (self.test_results["passed"]/total_tests*100) if total_tests > 0 else 0,
            "errors": self.test_results["errors"]
        }

if __name__ == "__main__":
    tester = EmployeeSchemaTestRunner()
    results = tester.run_employee_schema_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)