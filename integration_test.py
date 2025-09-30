#!/usr/bin/env python3
"""
Integration Testing for Project Overview System
Tests end-to-end workflows and cross-system relationships
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"

class IntegrationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {"passed": 0, "failed": 0, "errors": []}
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASSED")
        else:
            self.test_results["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 TESTING END-TO-END WORKFLOW")
        print("=" * 50)
        
        # Step 1: Create a project
        print("Step 1: Creating project...")
        project_data = {
            "name": "Integration Test Project - Office Building",
            "description": "Complete electrical installation for office building",
            "client_company": "Test Construction Corp",
            "gc_email": "pm@testcorp.com",
            "contract_amount": 750000.00,
            "project_manager": "Jesus Garcia",
            "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=30)).isoformat(),
            "address": "123 Test Street, Test City, TS 12345"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                project_id = project["id"]
                project_name = project["name"]
                self.log_result("Project creation", True)
            else:
                self.log_result("Project creation", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Project creation", False, str(e))
            return False
        
        # Step 2: Create employees
        print("Step 2: Creating employees...")
        employees_data = [
            {
                "name": "John Smith",
                "base_pay": 35.00,
                "burden_cost": 15.50,
                "position": "Master Electrician",
                "hire_date": (datetime.now() - timedelta(days=1000)).isoformat(),
                "phone": "(555) 111-2222",
                "email": "john.smith@company.com"
            },
            {
                "name": "Maria Garcia",
                "base_pay": 28.75,
                "burden_cost": 12.25,
                "position": "Journeyman Electrician",
                "hire_date": (datetime.now() - timedelta(days=500)).isoformat(),
                "phone": "(555) 333-4444",
                "email": "maria.garcia@company.com"
            }
        ]
        
        created_employees = []
        for emp_data in employees_data:
            try:
                response = self.session.post(f"{self.base_url}/employees", json=emp_data)
                if response.status_code == 200:
                    created_employees.append(response.json())
                    self.log_result(f"Employee creation - {emp_data['name']}", True)
                else:
                    self.log_result(f"Employee creation - {emp_data['name']}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Employee creation - {emp_data['name']}", False, str(e))
        
        if len(created_employees) != 2:
            print("❌ Failed to create required employees")
            return False
        
        # Step 3: Create crew logs
        print("Step 3: Creating crew logs...")
        crew_log_data = {
            "project_id": project_id,
            "project_name": project_name,
            "date": (datetime.now() - timedelta(days=5)).isoformat(),
            "crew_members": ["John Smith", "Maria Garcia"],
            "work_description": "Installed main electrical panel and distribution boards",
            "hours_worked": 16.0,  # 2 workers x 8 hours
            "per_diem": 100.00,
            "hotel_cost": 0.00,
            "gas_expense": 65.50,
            "other_expenses": 35.00,
            "expense_notes": "Fuel and lunch expenses",
            "weather_conditions": "Clear, 75°F"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/crew-logs", json=crew_log_data)
            if response.status_code == 200:
                crew_log = response.json()
                self.log_result("Crew log creation", True)
            else:
                self.log_result("Crew log creation", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Crew log creation", False, str(e))
            return False
        
        # Step 4: Create material purchases
        print("Step 4: Creating material purchases...")
        materials_data = [
            {
                "project_id": project_id,
                "project_name": project_name,
                "purchase_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "vendor": "Electrical Supply Co",
                "material_name": "200A Main Panel",
                "quantity": 1.0,
                "unit_cost": 850.00,
                "total_cost": 850.00,
                "invoice_number": "ESC-2024-001",
                "category": "panels"
            },
            {
                "project_id": project_id,
                "project_name": project_name,
                "purchase_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "vendor": "Wire & Cable Inc",
                "material_name": "14 AWG THHN Wire",
                "quantity": 2500.0,
                "unit_cost": 0.95,
                "total_cost": 2375.00,
                "invoice_number": "WCI-2024-045",
                "category": "wire"
            }
        ]
        
        created_materials = []
        for mat_data in materials_data:
            try:
                response = self.session.post(f"{self.base_url}/materials", json=mat_data)
                if response.status_code == 200:
                    created_materials.append(response.json())
                    self.log_result(f"Material creation - {mat_data['material_name']}", True)
                else:
                    self.log_result(f"Material creation - {mat_data['material_name']}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Material creation - {mat_data['material_name']}", False, str(e))
        
        if len(created_materials) != 2:
            print("❌ Failed to create required materials")
            return False
        
        # Step 5: Create T&M tags with project reference
        print("Step 5: Creating T&M tags...")
        tm_tag_data = {
            "project_name": project_name,
            "cost_code": "CC-INT-TEST-001",
            "date_of_work": (datetime.now() - timedelta(days=1)).isoformat(),
            "company_name": "Test Construction Corp",
            "tm_tag_title": "Panel Installation and Wiring",
            "description_of_work": "Installation of main electrical panel and rough wiring for office spaces",
            "labor_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "John Smith",
                    "quantity": 1,
                    "st_hours": 8.0,
                    "ot_hours": 2.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 10.0,
                    "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                },
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Maria Garcia",
                    "quantity": 1,
                    "st_hours": 8.0,
                    "ot_hours": 1.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 9.0,
                    "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "material_name": "Conduit and Fittings",
                    "unit_of_measure": "feet",
                    "quantity": 150.0,
                    "unit_cost": 2.50,
                    "total": 375.0,
                    "date_of_work": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            ],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "pm@testcorp.com"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/tm-tags", json=tm_tag_data)
            if response.status_code == 200:
                tm_tag = response.json()
                self.log_result("T&M tag creation", True)
            else:
                self.log_result("T&M tag creation", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("T&M tag creation", False, str(e))
            return False
        
        # Step 6: Get comprehensive analytics
        print("Step 6: Testing analytics calculations...")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
            if response.status_code == 200:
                analytics = response.json()
                
                # Verify analytics structure
                required_fields = [
                    "project_id", "project_name", "total_hours", "total_labor_cost_gc",
                    "total_material_cost", "total_crew_expenses", "true_employee_cost",
                    "total_revenue", "total_costs", "profit", "profit_margin"
                ]
                
                missing_fields = [field for field in required_fields if field not in analytics]
                if missing_fields:
                    self.log_result("Analytics structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify calculations make sense
                expected_material_cost = 850.00 + 2375.00  # From material purchases
                expected_crew_expenses = 100.00 + 65.50 + 35.00  # From crew log
                expected_hours = 19.0  # From T&M tag labor entries (10 + 9)
                
                if abs(analytics["total_material_cost"] - expected_material_cost) < 0.01:
                    self.log_result("Analytics - Material cost calculation", True)
                else:
                    self.log_result("Analytics - Material cost calculation", False, 
                                  f"Expected {expected_material_cost}, got {analytics['total_material_cost']}")
                
                if abs(analytics["total_crew_expenses"] - expected_crew_expenses) < 0.01:
                    self.log_result("Analytics - Crew expenses calculation", True)
                else:
                    self.log_result("Analytics - Crew expenses calculation", False,
                                  f"Expected {expected_crew_expenses}, got {analytics['total_crew_expenses']}")
                
                if abs(analytics["total_hours"] - expected_hours) < 0.01:
                    self.log_result("Analytics - Hours calculation", True)
                else:
                    self.log_result("Analytics - Hours calculation", False,
                                  f"Expected {expected_hours}, got {analytics['total_hours']}")
                
                # Verify profit calculation logic
                if analytics["total_revenue"] > 0 and analytics["total_costs"] > 0:
                    calculated_profit = analytics["total_revenue"] - analytics["total_costs"]
                    if abs(analytics["profit"] - calculated_profit) < 0.01:
                        self.log_result("Analytics - Profit calculation", True)
                    else:
                        self.log_result("Analytics - Profit calculation", False,
                                      f"Profit calculation mismatch: {analytics['profit']} vs {calculated_profit}")
                else:
                    self.log_result("Analytics - Revenue/Cost validation", False, "Revenue or costs are zero")
                
                print(f"📊 Analytics Summary:")
                print(f"   Total Hours: {analytics['total_hours']}")
                print(f"   Material Cost: ${analytics['total_material_cost']:,.2f}")
                print(f"   Crew Expenses: ${analytics['total_crew_expenses']:,.2f}")
                print(f"   Total Revenue: ${analytics['total_revenue']:,.2f}")
                print(f"   Total Costs: ${analytics['total_costs']:,.2f}")
                print(f"   Profit: ${analytics['profit']:,.2f}")
                print(f"   Profit Margin: {analytics['profit_margin']:.1f}%")
                
            else:
                self.log_result("Analytics retrieval", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Analytics retrieval", False, str(e))
            return False
        
        # Step 7: Test filtering by project
        print("Step 7: Testing project filtering...")
        
        # Test crew logs filtering
        try:
            response = self.session.get(f"{self.base_url}/crew-logs?project_id={project_id}")
            if response.status_code == 200:
                filtered_logs = response.json()
                if len(filtered_logs) > 0 and all(log["project_id"] == project_id for log in filtered_logs):
                    self.log_result("Crew logs filtering", True, f"Found {len(filtered_logs)} logs for project")
                else:
                    self.log_result("Crew logs filtering", False, "No logs found or incorrect filtering")
            else:
                self.log_result("Crew logs filtering", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Crew logs filtering", False, str(e))
        
        # Test materials filtering
        try:
            response = self.session.get(f"{self.base_url}/materials?project_id={project_id}")
            if response.status_code == 200:
                filtered_materials = response.json()
                if len(filtered_materials) > 0 and all(mat["project_id"] == project_id for mat in filtered_materials):
                    self.log_result("Materials filtering", True, f"Found {len(filtered_materials)} materials for project")
                else:
                    self.log_result("Materials filtering", False, "No materials found or incorrect filtering")
            else:
                self.log_result("Materials filtering", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Materials filtering", False, str(e))
        
        # Step 8: Cleanup - Delete test data
        print("Step 8: Cleaning up test data...")
        
        # Delete T&M tag
        try:
            response = self.session.delete(f"{self.base_url}/tm-tags/{tm_tag['id']}")
            if response.status_code == 200:
                self.log_result("T&M tag cleanup", True)
            else:
                self.log_result("T&M tag cleanup", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("T&M tag cleanup", False, str(e))
        
        # Delete materials
        for material in created_materials:
            try:
                response = self.session.delete(f"{self.base_url}/materials/{material['id']}")
                if response.status_code == 200:
                    self.log_result(f"Material cleanup - {material['material_name']}", True)
                else:
                    self.log_result(f"Material cleanup - {material['material_name']}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"Material cleanup - {material['material_name']}", False, str(e))
        
        # Delete crew log
        try:
            response = self.session.delete(f"{self.base_url}/crew-logs/{crew_log['id']}")
            if response.status_code == 200:
                self.log_result("Crew log cleanup", True)
            else:
                self.log_result("Crew log cleanup", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Crew log cleanup", False, str(e))
        
        # Delete employees
        for employee in created_employees:
            try:
                response = self.session.delete(f"{self.base_url}/employees/{employee['id']}")
                if response.status_code == 200:
                    self.log_result(f"Employee cleanup - {employee['name']}", True)
                else:
                    self.log_result(f"Employee cleanup - {employee['name']}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"Employee cleanup - {employee['name']}", False, str(e))
        
        # Delete project
        try:
            response = self.session.delete(f"{self.base_url}/projects/{project_id}")
            if response.status_code == 200:
                self.log_result("Project cleanup", True)
            else:
                self.log_result("Project cleanup", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Project cleanup", False, str(e))
        
        return True
    
    def run_integration_tests(self):
        """Run all integration tests"""
        print("🔗 Starting Integration Tests for Project Overview System")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Run end-to-end workflow test
        self.test_end_to_end_workflow()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS SUMMARY")
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
    tester = IntegrationTester()
    results = tester.run_integration_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)