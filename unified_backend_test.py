#!/usr/bin/env python3
"""
Unified Backend API Testing for Enhanced T&M Management System
Tests the new unified schema with forecasting capabilities
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

class UnifiedBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "schema_migration": {"passed": 0, "failed": 0, "errors": []},
            "projects": {"passed": 0, "failed": 0, "errors": []},
            "crew_members": {"passed": 0, "failed": 0, "errors": []},
            "materials": {"passed": 0, "failed": 0, "errors": []},
            "expenses": {"passed": 0, "failed": 0, "errors": []},
            "tm_tags": {"passed": 0, "failed": 0, "errors": []},
            "invoices": {"passed": 0, "failed": 0, "errors": []},
            "payables": {"passed": 0, "failed": 0, "errors": []},
            "forecasting": {"passed": 0, "failed": 0, "errors": []},
            "analytics": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_health_check(self):
        """Test unified server health check"""
        print("\n=== Testing Unified Server Health Check ===")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy" and health_data.get("version") == "2.0.0":
                    self.log_result("general", "Health check", True, f"Version: {health_data.get('version')}")
                    return health_data
                else:
                    self.log_result("general", "Health check", False, "Invalid health response", response)
            else:
                self.log_result("general", "Health check", False, f"Status code: {response.status_code}", response)
        except Exception as e:
            self.log_result("general", "Health check", False, str(e))
        return None
    
    def test_schema_migration_validation(self):
        """Test that schema migration was successful with expected counts"""
        print("\n=== Testing Schema Migration Validation ===")
        
        # Test projects_new collection (should have 15 projects)
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if len(projects) == 15:
                    self.log_result("schema_migration", "Projects migration (15 projects)", True)
                    
                    # Validate enhanced fields
                    sample_project = projects[0]
                    required_fields = ["id", "name", "client", "contractType", "invoiceSchedule", "billingDay", "openingBalance", "gcRate"]
                    missing_fields = [field for field in required_fields if field not in sample_project]
                    
                    if not missing_fields:
                        self.log_result("schema_migration", "Project enhanced schema fields", True)
                    else:
                        self.log_result("schema_migration", "Project enhanced schema fields", False, f"Missing: {missing_fields}")
                else:
                    self.log_result("schema_migration", "Projects migration (15 projects)", False, f"Expected 15, got {len(projects)}")
            else:
                self.log_result("schema_migration", "Projects migration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Projects migration", False, str(e))
        
        # Test crew_members collection (should have 38 members)
        try:
            response = self.session.get(f"{self.base_url}/crew-members")
            if response.status_code == 200:
                crew_members = response.json()
                if len(crew_members) == 38:
                    self.log_result("schema_migration", "Crew members migration (38 members)", True)
                    
                    # Validate enhanced fields
                    sample_member = crew_members[0]
                    required_fields = ["id", "name", "hourlyRate", "gcBillRate", "status"]
                    missing_fields = [field for field in required_fields if field not in sample_member]
                    
                    if not missing_fields:
                        self.log_result("schema_migration", "Crew member enhanced schema fields", True)
                    else:
                        self.log_result("schema_migration", "Crew member enhanced schema fields", False, f"Missing: {missing_fields}")
                else:
                    self.log_result("schema_migration", "Crew members migration (38 members)", False, f"Expected 38, got {len(crew_members)}")
            else:
                self.log_result("schema_migration", "Crew members migration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Crew members migration", False, str(e))
        
        # Test materials_new collection (should have 6 materials)
        try:
            response = self.session.get(f"{self.base_url}/materials")
            if response.status_code == 200:
                materials = response.json()
                if len(materials) == 6:
                    self.log_result("schema_migration", "Materials migration (6 materials)", True)
                    
                    # Validate enhanced fields
                    sample_material = materials[0]
                    required_fields = ["id", "projectId", "vendor", "description", "quantity", "unitCost", "total", "markupPercent"]
                    missing_fields = [field for field in required_fields if field not in sample_material]
                    
                    if not missing_fields:
                        self.log_result("schema_migration", "Material enhanced schema fields", True)
                    else:
                        self.log_result("schema_migration", "Material enhanced schema fields", False, f"Missing: {missing_fields}")
                else:
                    self.log_result("schema_migration", "Materials migration (6 materials)", False, f"Expected 6, got {len(materials)}")
            else:
                self.log_result("schema_migration", "Materials migration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Materials migration", False, str(e))
        
        # Test tm_tags_new collection (should have 10 tags)
        try:
            response = self.session.get(f"{self.base_url}/tm-tags")
            if response.status_code == 200:
                tm_tags = response.json()
                if len(tm_tags) == 10:
                    self.log_result("schema_migration", "T&M tags migration (10 tags)", True)
                    
                    # Validate enhanced fields
                    sample_tag = tm_tags[0]
                    required_fields = ["id", "projectId", "totalLaborCost", "totalLaborBill", "totalMaterialCost", "totalMaterialBill", "totalExpense", "totalBill"]
                    missing_fields = [field for field in required_fields if field not in sample_tag]
                    
                    if not missing_fields:
                        self.log_result("schema_migration", "T&M tag enhanced schema fields", True)
                    else:
                        self.log_result("schema_migration", "T&M tag enhanced schema fields", False, f"Missing: {missing_fields}")
                else:
                    self.log_result("schema_migration", "T&M tags migration (10 tags)", False, f"Expected 10, got {len(tm_tags)}")
            else:
                self.log_result("schema_migration", "T&M tags migration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "T&M tags migration", False, str(e))
    
    def test_new_collections_initialization(self):
        """Test that new collections are properly initialized"""
        print("\n=== Testing New Collections Initialization ===")
        
        # Test expenses collection
        try:
            response = self.session.get(f"{self.base_url}/expenses")
            if response.status_code == 200:
                expenses = response.json()
                self.log_result("schema_migration", "Expenses collection initialized", True, f"Found {len(expenses)} expenses")
            else:
                self.log_result("schema_migration", "Expenses collection initialized", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Expenses collection initialized", False, str(e))
        
        # Test invoices collection
        try:
            response = self.session.get(f"{self.base_url}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                self.log_result("schema_migration", "Invoices collection initialized", True, f"Found {len(invoices)} invoices")
            else:
                self.log_result("schema_migration", "Invoices collection initialized", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Invoices collection initialized", False, str(e))
        
        # Test payables collection
        try:
            response = self.session.get(f"{self.base_url}/payables")
            if response.status_code == 200:
                payables = response.json()
                self.log_result("schema_migration", "Payables collection initialized", True, f"Found {len(payables)} payables")
            else:
                self.log_result("schema_migration", "Payables collection initialized", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Payables collection initialized", False, str(e))
    
    def test_enhanced_project_endpoints(self):
        """Test enhanced project management endpoints"""
        print("\n=== Testing Enhanced Project Endpoints ===")
        
        # Test project creation with unified schema
        project_data = {
            "name": "Test Unified Project",
            "client": "Unified Test Client",
            "contractType": "T&M",
            "invoiceSchedule": "monthly",
            "billingDay": 15,
            "openingBalance": 5000.0,
            "gcRate": 110.0,
            "startDate": datetime.utcnow().isoformat(),
            "notes": "Testing unified schema project creation"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                required_fields = ["id", "name", "client", "contractType", "invoiceSchedule", "billingDay", "openingBalance", "gcRate"]
                missing_fields = [field for field in required_fields if field not in project]
                
                if not missing_fields:
                    self.created_project_id = project["id"]
                    self.log_result("projects", "Enhanced project creation", True)
                else:
                    self.log_result("projects", "Enhanced project creation", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("projects", "Enhanced project creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("projects", "Enhanced project creation", False, str(e))
        
        # Test project retrieval with unified schema
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if len(projects) >= 15:  # Should have at least the migrated projects
                    self.log_result("projects", "Enhanced project retrieval", True, f"Retrieved {len(projects)} projects")
                else:
                    self.log_result("projects", "Enhanced project retrieval", False, f"Expected >= 15, got {len(projects)}")
            else:
                self.log_result("projects", "Enhanced project retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("projects", "Enhanced project retrieval", False, str(e))
    
    def test_crew_member_endpoints(self):
        """Test crew member management endpoints"""
        print("\n=== Testing Crew Member Endpoints ===")
        
        # Test crew member creation
        crew_member_data = {
            "name": "Test Unified Crew Member",
            "position": "Test Electrician",
            "hourlyRate": 55.0,
            "gcBillRate": 105.0,
            "hireDate": datetime.utcnow().isoformat()
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/crew-members",
                json=crew_member_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_member = response.json()
                required_fields = ["id", "name", "position", "hourlyRate", "gcBillRate", "status"]
                missing_fields = [field for field in required_fields if field not in crew_member]
                
                if not missing_fields:
                    self.created_crew_member_id = crew_member["id"]
                    self.log_result("crew_members", "Crew member creation", True)
                else:
                    self.log_result("crew_members", "Crew member creation", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("crew_members", "Crew member creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("crew_members", "Crew member creation", False, str(e))
        
        # Test crew member retrieval
        try:
            response = self.session.get(f"{self.base_url}/crew-members")
            if response.status_code == 200:
                crew_members = response.json()
                if len(crew_members) >= 38:  # Should have at least the migrated members
                    self.log_result("crew_members", "Crew member retrieval", True, f"Retrieved {len(crew_members)} crew members")
                else:
                    self.log_result("crew_members", "Crew member retrieval", False, f"Expected >= 38, got {len(crew_members)}")
            else:
                self.log_result("crew_members", "Crew member retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("crew_members", "Crew member retrieval", False, str(e))
    
    def test_material_endpoints(self):
        """Test enhanced material management endpoints"""
        print("\n=== Testing Enhanced Material Endpoints ===")
        
        # Test material creation with markup
        if not hasattr(self, 'created_project_id'):
            # Use first project from migration
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code == 200:
                projects = projects_response.json()
                if projects:
                    self.created_project_id = projects[0]["id"]
        
        if hasattr(self, 'created_project_id'):
            material_data = {
                "projectId": self.created_project_id,
                "vendor": "Test Unified Vendor",
                "date": datetime.utcnow().isoformat(),
                "description": "Test Unified Material",
                "quantity": 10.0,
                "unitCost": 25.0,
                "total": 250.0,
                "markupPercent": 25.0,
                "confirmed": True
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/materials",
                    json=material_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    material = response.json()
                    required_fields = ["id", "projectId", "vendor", "description", "quantity", "unitCost", "total", "markupPercent"]
                    missing_fields = [field for field in required_fields if field not in material]
                    
                    if not missing_fields:
                        self.log_result("materials", "Enhanced material creation", True)
                    else:
                        self.log_result("materials", "Enhanced material creation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("materials", "Enhanced material creation", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("materials", "Enhanced material creation", False, str(e))
        
        # Test material retrieval
        try:
            response = self.session.get(f"{self.base_url}/materials")
            if response.status_code == 200:
                materials = response.json()
                if len(materials) >= 6:  # Should have at least the migrated materials
                    self.log_result("materials", "Enhanced material retrieval", True, f"Retrieved {len(materials)} materials")
                else:
                    self.log_result("materials", "Enhanced material retrieval", False, f"Expected >= 6, got {len(materials)}")
            else:
                self.log_result("materials", "Enhanced material retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("materials", "Enhanced material retrieval", False, str(e))
    
    def test_expense_endpoints(self):
        """Test new expense management endpoints"""
        print("\n=== Testing New Expense Endpoints ===")
        
        if hasattr(self, 'created_project_id'):
            expense_data = {
                "projectId": self.created_project_id,
                "type": "hotel",
                "description": "Test Hotel Expense",
                "date": datetime.utcnow().isoformat(),
                "amount": 150.0
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/expenses",
                    json=expense_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    expense = response.json()
                    required_fields = ["id", "projectId", "type", "description", "date", "amount"]
                    missing_fields = [field for field in required_fields if field not in expense]
                    
                    if not missing_fields:
                        self.log_result("expenses", "Expense creation", True)
                    else:
                        self.log_result("expenses", "Expense creation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("expenses", "Expense creation", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("expenses", "Expense creation", False, str(e))
        
        # Test expense retrieval
        try:
            response = self.session.get(f"{self.base_url}/expenses")
            if response.status_code == 200:
                expenses = response.json()
                self.log_result("expenses", "Expense retrieval", True, f"Retrieved {len(expenses)} expenses")
            else:
                self.log_result("expenses", "Expense retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("expenses", "Expense retrieval", False, str(e))
    
    def test_invoice_endpoints(self):
        """Test new invoice management endpoints"""
        print("\n=== Testing New Invoice Endpoints ===")
        
        if hasattr(self, 'created_project_id'):
            invoice_data = {
                "projectId": self.created_project_id,
                "invoiceNumber": "INV-TEST-001",
                "dateIssued": datetime.utcnow().isoformat(),
                "dueDate": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "periodStart": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "periodEnd": datetime.utcnow().isoformat(),
                "lineItems": [
                    {"description": "Labor - Week 1", "amount": 5000.0},
                    {"description": "Materials", "amount": 1500.0}
                ],
                "total": 6500.0,
                "invoiceNarrative": "Test invoice for unified system"
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/invoices",
                    json=invoice_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    invoice = response.json()
                    required_fields = ["id", "projectId", "invoiceNumber", "dateIssued", "dueDate", "total", "status"]
                    missing_fields = [field for field in required_fields if field not in invoice]
                    
                    if not missing_fields:
                        self.log_result("invoices", "Invoice creation", True)
                    else:
                        self.log_result("invoices", "Invoice creation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("invoices", "Invoice creation", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("invoices", "Invoice creation", False, str(e))
        
        # Test invoice retrieval
        try:
            response = self.session.get(f"{self.base_url}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                self.log_result("invoices", "Invoice retrieval", True, f"Retrieved {len(invoices)} invoices")
            else:
                self.log_result("invoices", "Invoice retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("invoices", "Invoice retrieval", False, str(e))
    
    def test_payable_endpoints(self):
        """Test new payable management endpoints"""
        print("\n=== Testing New Payable Endpoints ===")
        
        if hasattr(self, 'created_project_id'):
            payable_data = {
                "projectId": self.created_project_id,
                "vendor": "Test Vendor Inc",
                "description": "Test Payable for Materials",
                "dueDate": (datetime.utcnow() + timedelta(days=15)).isoformat(),
                "amount": 2500.0
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/payables",
                    json=payable_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    payable = response.json()
                    required_fields = ["id", "projectId", "vendor", "description", "dueDate", "amount", "status"]
                    missing_fields = [field for field in required_fields if field not in payable]
                    
                    if not missing_fields:
                        self.log_result("payables", "Payable creation", True)
                    else:
                        self.log_result("payables", "Payable creation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("payables", "Payable creation", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("payables", "Payable creation", False, str(e))
        
        # Test payable retrieval
        try:
            response = self.session.get(f"{self.base_url}/payables")
            if response.status_code == 200:
                payables = response.json()
                self.log_result("payables", "Payable retrieval", True, f"Retrieved {len(payables)} payables")
            else:
                self.log_result("payables", "Payable retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("payables", "Payable retrieval", False, str(e))
    
    def test_forecasting_endpoints(self):
        """Test new forecasting capabilities"""
        print("\n=== Testing Forecasting Endpoints ===")
        
        if hasattr(self, 'created_project_id'):
            # Test weekly forecast
            try:
                response = self.session.get(f"{self.base_url}/projects/{self.created_project_id}/weekly-forecast?weeks=8")
                if response.status_code == 200:
                    forecasts = response.json()
                    if len(forecasts) == 8:
                        # Validate forecast structure
                        sample_forecast = forecasts[0]
                        required_fields = ["projectId", "weekOf", "inflow", "outflow", "net", "forecastNarrative"]
                        missing_fields = [field for field in required_fields if field not in sample_forecast]
                        
                        if not missing_fields:
                            self.log_result("forecasting", "Weekly project forecast", True, f"Generated {len(forecasts)} weeks")
                        else:
                            self.log_result("forecasting", "Weekly project forecast", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("forecasting", "Weekly project forecast", False, f"Expected 8 weeks, got {len(forecasts)}")
                else:
                    self.log_result("forecasting", "Weekly project forecast", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("forecasting", "Weekly project forecast", False, str(e))
        
        # Test company forecast
        try:
            response = self.session.get(f"{self.base_url}/company/forecast")
            if response.status_code == 200:
                company_forecast = response.json()
                required_fields = ["weekOf", "totalInflow", "totalOutflow", "net", "projects", "rollupNarrative"]
                missing_fields = [field for field in required_fields if field not in company_forecast]
                
                if not missing_fields:
                    self.log_result("forecasting", "Company forecast", True)
                else:
                    self.log_result("forecasting", "Company forecast", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("forecasting", "Company forecast", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("forecasting", "Company forecast", False, str(e))
        
        # Test cash runway
        try:
            response = self.session.get(f"{self.base_url}/company/cash-runway")
            if response.status_code == 200:
                cash_runway = response.json()
                required_fields = ["nextInvoiceDate", "weeklyBurn", "cumulativeBalance", "runwayWeeks", "runwayNarrative"]
                missing_fields = [field for field in required_fields if field not in cash_runway]
                
                if not missing_fields:
                    self.log_result("forecasting", "Cash runway analysis", True, f"Runway: {cash_runway.get('runwayWeeks')} weeks")
                else:
                    self.log_result("forecasting", "Cash runway analysis", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("forecasting", "Cash runway analysis", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("forecasting", "Cash runway analysis", False, str(e))
    
    def test_enhanced_analytics_endpoints(self):
        """Test enhanced analytics with forecasting"""
        print("\n=== Testing Enhanced Analytics Endpoints ===")
        
        if hasattr(self, 'created_project_id'):
            # Test project analytics
            try:
                response = self.session.get(f"{self.base_url}/projects/{self.created_project_id}/analytics")
                if response.status_code == 200:
                    analytics = response.json()
                    required_fields = ["projectId", "contractType", "totalLaborCost", "totalLaborBill", "totalMaterialCost", "totalMaterialBill", "totalExpense", "totalBill", "profitMargin", "weeklyForecasts"]
                    missing_fields = [field for field in required_fields if field not in analytics]
                    
                    if not missing_fields:
                        self.log_result("analytics", "Enhanced project analytics", True, f"Profit margin: {analytics.get('profitMargin', 0):.1f}%")
                    else:
                        self.log_result("analytics", "Enhanced project analytics", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("analytics", "Enhanced project analytics", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("analytics", "Enhanced project analytics", False, str(e))
        
        # Test company analytics
        try:
            response = self.session.get(f"{self.base_url}/company/analytics")
            if response.status_code == 200:
                analytics = response.json()
                required_fields = ["totalProjects", "activeProjects", "totalRevenue", "totalCosts", "netProfit", "weeklyForecast", "cashRunway", "rollupNarrative"]
                missing_fields = [field for field in required_fields if field not in analytics]
                
                if not missing_fields:
                    self.log_result("analytics", "Company analytics", True, f"Active projects: {analytics.get('activeProjects')}")
                else:
                    self.log_result("analytics", "Company analytics", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("analytics", "Company analytics", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("analytics", "Company analytics", False, str(e))
    
    def test_legacy_compatibility(self):
        """Test legacy schema compatibility"""
        print("\n=== Testing Legacy Compatibility ===")
        
        # Test that legacy T&M tags are converted properly
        try:
            response = self.session.get(f"{self.base_url}/tm-tags")
            if response.status_code == 200:
                tm_tags = response.json()
                if tm_tags:
                    # Check if legacy tags have been converted to unified schema
                    sample_tag = tm_tags[0]
                    unified_fields = ["totalLaborCost", "totalLaborBill", "totalMaterialCost", "totalMaterialBill", "totalExpense", "totalBill"]
                    has_unified_fields = all(field in sample_tag for field in unified_fields)
                    
                    if has_unified_fields:
                        self.log_result("schema_migration", "Legacy T&M tag conversion", True)
                    else:
                        self.log_result("schema_migration", "Legacy T&M tag conversion", False, "Missing unified fields")
                else:
                    self.log_result("schema_migration", "Legacy T&M tag conversion", False, "No T&M tags found")
            else:
                self.log_result("schema_migration", "Legacy T&M tag conversion", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("schema_migration", "Legacy T&M tag conversion", False, str(e))
    
    def run_all_tests(self):
        """Run all unified backend tests"""
        print("🚀 Starting Unified Backend API Testing")
        print("=" * 60)
        
        # Basic connectivity
        health_data = self.test_health_check()
        if not health_data:
            print("❌ Health check failed - aborting tests")
            return
        
        # Schema migration validation
        self.test_schema_migration_validation()
        self.test_new_collections_initialization()
        self.test_legacy_compatibility()
        
        # Enhanced endpoints
        self.test_enhanced_project_endpoints()
        self.test_crew_member_endpoints()
        self.test_material_endpoints()
        self.test_expense_endpoints()
        self.test_invoice_endpoints()
        self.test_payable_endpoints()
        
        # New forecasting capabilities
        self.test_forecasting_endpoints()
        self.test_enhanced_analytics_endpoints()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 UNIFIED BACKEND TEST SUMMARY")
        print("=" * 60)
        
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
                    print(f"   ❌ {error}")
        
        print("\n" + "=" * 60)
        success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"🎯 OVERALL: {total_passed} passed, {total_failed} failed ({success_rate:.1f}% success rate)")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! Unified backend is fully functional.")
        else:
            print(f"⚠️  {total_failed} tests failed. Review errors above.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = UnifiedBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)