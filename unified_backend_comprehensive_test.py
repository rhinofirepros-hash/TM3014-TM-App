#!/usr/bin/env python3
"""
Comprehensive Backend System Validation for Unified Server
Tests all critical backend systems as requested in the review
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import time
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://rhino-ui-sync.preview.emergentagent.com/api"

class UnifiedBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "core_apis": {"passed": 0, "failed": 0, "errors": []},
            "authentication": {"passed": 0, "failed": 0, "errors": []},
            "database": {"passed": 0, "failed": 0, "errors": []},
            "sync": {"passed": 0, "failed": 0, "errors": []},
            "financial": {"passed": 0, "failed": 0, "errors": []},
            "gc_dashboard": {"passed": 0, "failed": 0, "errors": []},
            "error_handling": {"passed": 0, "failed": 0, "errors": []},
            "performance": {"passed": 0, "failed": 0, "errors": []}
        }
        self.created_resources = {}
        
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
        print("\n🔗 TESTING BASIC CONNECTIVITY")
        print("=" * 50)
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.log_result("database", "Basic connectivity", True, "API accessible")
                return True
            else:
                self.log_result("database", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("database", "Basic connectivity", False, str(e))
            return False
    
    def test_core_api_endpoints(self):
        """Test all core API endpoints validation"""
        print("\n🎯 TESTING CORE API ENDPOINTS")
        print("=" * 50)
        
        # Test Project Management endpoints (unified schema)
        print("\n--- Project Management CRUD Operations ---")
        project_data = {
            "name": "Backend Test Project",
            "client": "Test Client Corp",
            "contractType": "full_contract",
            "invoiceSchedule": "monthly",
            "billingDay": 15,
            "openingBalance": 0.0,
            "gcRate": 95.0,
            "startDate": datetime.now().isoformat(),
            "endDate": (datetime.now() + timedelta(days=90)).isoformat(),
            "status": "active",
            "notes": "Backend testing project"
        }
        
        # POST Project
        try:
            response = self.session.post(f"{self.base_url}/projects", json=project_data)
            if response.status_code == 200:
                project = response.json()
                self.created_resources['project_id'] = project['id']
                self.log_result("core_apis", "POST /api/projects", True, f"Created project {project['id']}")
            else:
                self.log_result("core_apis", "POST /api/projects", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "POST /api/projects", False, str(e))
        
        # GET Projects
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                self.log_result("core_apis", "GET /api/projects", True, f"Retrieved {len(projects)} projects")
            else:
                self.log_result("core_apis", "GET /api/projects", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/projects", False, str(e))
        
        # PUT Project (if created)
        if 'project_id' in self.created_resources:
            try:
                update_data = {"name": "Updated Backend Test Project", "notes": "Updated via API test"}
                response = self.session.put(f"{self.base_url}/projects/{self.created_resources['project_id']}", json=update_data)
                if response.status_code == 200:
                    self.log_result("core_apis", "PUT /api/projects", True, "Project updated")
                else:
                    self.log_result("core_apis", "PUT /api/projects", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "PUT /api/projects", False, str(e))
        
        # Test Crew Member Management endpoints
        print("\n--- Crew Member Management CRUD Operations ---")
        crew_member_data = {
            "name": "Test Crew Member",
            "hourlyRate": 45.0,
            "position": "Test Electrician",
            "phone": "(555) 123-4567",
            "email": "test@crew.com",
            "hireDate": datetime.now().isoformat(),
            "status": "active"
        }
        
        # POST Crew Member
        try:
            response = self.session.post(f"{self.base_url}/crew-members", json=crew_member_data)
            if response.status_code == 200:
                crew_member = response.json()
                self.created_resources['crew_member_id'] = crew_member['id']
                self.log_result("core_apis", "POST /api/crew-members", True, f"Created crew member {crew_member['id']}")
            else:
                self.log_result("core_apis", "POST /api/crew-members", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "POST /api/crew-members", False, str(e))
        
        # GET Crew Members
        try:
            response = self.session.get(f"{self.base_url}/crew-members")
            if response.status_code == 200:
                crew_members = response.json()
                self.log_result("core_apis", "GET /api/crew-members", True, f"Retrieved {len(crew_members)} crew members")
            else:
                self.log_result("core_apis", "GET /api/crew-members", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/crew-members", False, str(e))
        
        # Test T&M Tag endpoints (unified schema)
        print("\n--- T&M Tag CRUD Operations ---")
        if 'project_id' in self.created_resources:
            tm_tag_data = {
                "projectId": self.created_resources['project_id'],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": "Backend Test T&M Tag",
                "description": "Testing T&M tag creation via API",
                "laborEntries": [{
                    "crewMemberId": self.created_resources.get('crew_member_id', 'test-id'),
                    "hours": 8.0,
                    "rate": 95.0,
                    "total": 760.0
                }],
                "materialEntries": [],
                "status": "pending"
            }
            
            # POST T&M Tag
            try:
                response = self.session.post(f"{self.base_url}/tm-tags", json=tm_tag_data)
                if response.status_code == 200:
                    tm_tag = response.json()
                    self.created_resources['tm_tag_id'] = tm_tag['id']
                    self.log_result("core_apis", "POST /api/tm-tags", True, f"Created T&M tag {tm_tag['id']}")
                else:
                    self.log_result("core_apis", "POST /api/tm-tags", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "POST /api/tm-tags", False, str(e))
        
        # GET T&M Tags
        try:
            response = self.session.get(f"{self.base_url}/tm-tags")
            if response.status_code == 200:
                tm_tags = response.json()
                self.log_result("core_apis", "GET /api/tm-tags", True, f"Retrieved {len(tm_tags)} T&M tags")
            else:
                self.log_result("core_apis", "GET /api/tm-tags", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/tm-tags", False, str(e))
        
        # Test Material Management endpoints
        print("\n--- Material Management CRUD Operations ---")
        if 'project_id' in self.created_resources:
            material_data = {
                "projectId": self.created_resources['project_id'],
                "name": "Test Material",
                "vendor": "Test Vendor",
                "quantity": 10.0,
                "unitCost": 5.0,
                "totalCost": 50.0,
                "purchaseDate": datetime.now().isoformat(),
                "category": "electrical"
            }
            
            # POST Material
            try:
                response = self.session.post(f"{self.base_url}/materials", json=material_data)
                if response.status_code == 200:
                    material = response.json()
                    self.created_resources['material_id'] = material['id']
                    self.log_result("core_apis", "POST /api/materials", True, f"Created material {material['id']}")
                else:
                    self.log_result("core_apis", "POST /api/materials", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "POST /api/materials", False, str(e))
        
        # GET Materials
        try:
            response = self.session.get(f"{self.base_url}/materials")
            if response.status_code == 200:
                materials = response.json()
                self.log_result("core_apis", "GET /api/materials", True, f"Retrieved {len(materials)} materials")
            else:
                self.log_result("core_apis", "GET /api/materials", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/materials", False, str(e))
        
        # Test Expense Management endpoints
        print("\n--- Expense Management CRUD Operations ---")
        if 'project_id' in self.created_resources:
            expense_data = {
                "projectId": self.created_resources['project_id'],
                "type": "travel",
                "amount": 100.0,
                "description": "Test expense",
                "date": datetime.now().isoformat(),
                "receipt": None
            }
            
            # POST Expense
            try:
                response = self.session.post(f"{self.base_url}/expenses", json=expense_data)
                if response.status_code == 200:
                    expense = response.json()
                    self.created_resources['expense_id'] = expense['id']
                    self.log_result("core_apis", "POST /api/expenses", True, f"Created expense {expense['id']}")
                else:
                    self.log_result("core_apis", "POST /api/expenses", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "POST /api/expenses", False, str(e))
        
        # GET Expenses
        try:
            response = self.session.get(f"{self.base_url}/expenses")
            if response.status_code == 200:
                expenses = response.json()
                self.log_result("core_apis", "GET /api/expenses", True, f"Retrieved {len(expenses)} expenses")
            else:
                self.log_result("core_apis", "GET /api/expenses", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/expenses", False, str(e))
    
    def test_authentication_system(self):
        """Test authentication system including Admin PIN and GC PIN"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        # Test GC PIN generation
        print("\n--- GC PIN System Testing ---")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    test_project = projects[0]
                    project_id = test_project['id']
                    
                    # Test PIN generation
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        if 'gcPin' in pin_data:
                            generated_pin = pin_data['gcPin']
                            self.log_result("authentication", "GC PIN generation", True, f"Generated PIN: {generated_pin}")
                            
                            # Test PIN validation
                            validate_data = {"pin": generated_pin}
                            validate_response = self.session.post(f"{self.base_url}/gc/validate-pin", json=validate_data)
                            if validate_response.status_code == 200:
                                self.log_result("authentication", "GC PIN validation", True, "PIN validated successfully")
                            else:
                                self.log_result("authentication", "GC PIN validation", False, f"HTTP {validate_response.status_code}", validate_response)
                        else:
                            self.log_result("authentication", "GC PIN generation", False, "No PIN in response", pin_response)
                    else:
                        self.log_result("authentication", "GC PIN generation", False, f"HTTP {pin_response.status_code}", pin_response)
                else:
                    self.log_result("authentication", "GC PIN generation", False, "No projects available for testing")
            else:
                self.log_result("authentication", "GC PIN generation", False, "Could not retrieve projects", response)
        except Exception as e:
            self.log_result("authentication", "GC PIN generation", False, str(e))
        
        # Test GC login simple endpoint
        print("\n--- GC Login Simple Testing ---")
        try:
            # Get a fresh PIN first
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    test_project = projects[0]
                    project_id = test_project['id']
                    
                    # Generate fresh PIN
                    pin_response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        if 'gcPin' in pin_data:
                            fresh_pin = pin_data['gcPin']
                            
                            # Test login with PIN
                            login_data = {"projectId": project_id, "pin": fresh_pin}
                            login_response = self.session.post(f"{self.base_url}/gc/login-simple", json=login_data)
                            if login_response.status_code == 200:
                                self.log_result("authentication", "GC login simple", True, "Login successful")
                            else:
                                self.log_result("authentication", "GC login simple", False, f"HTTP {login_response.status_code}", login_response)
                        else:
                            self.log_result("authentication", "GC login simple", False, "No PIN available for login test")
                    else:
                        self.log_result("authentication", "GC login simple", False, "Could not generate PIN for login test")
                else:
                    self.log_result("authentication", "GC login simple", False, "No projects for login test")
            else:
                self.log_result("authentication", "GC login simple", False, "Could not retrieve projects for login test")
        except Exception as e:
            self.log_result("authentication", "GC login simple", False, str(e))
    
    def test_database_connectivity(self):
        """Test database connectivity and performance"""
        print("\n🗄️ TESTING DATABASE CONNECTIVITY & PERFORMANCE")
        print("=" * 50)
        
        # Test data persistence
        print("\n--- Data Persistence Testing ---")
        test_data = {
            "name": "DB Test Project",
            "client": "DB Test Client",
            "contractType": "full_contract",
            "invoiceSchedule": "monthly",
            "billingDay": 15,
            "openingBalance": 0.0,
            "gcRate": 95.0,
            "startDate": datetime.now().isoformat(),
            "status": "active",
            "notes": "Database persistence test"
        }
        
        try:
            # Create record
            start_time = time.time()
            create_response = self.session.post(f"{self.base_url}/projects", json=test_data)
            create_time = time.time() - start_time
            
            if create_response.status_code == 200:
                project = create_response.json()
                project_id = project['id']
                self.log_result("database", "Data persistence - CREATE", True, f"Created in {create_time:.3f}s")
                
                # Retrieve record
                start_time = time.time()
                get_response = self.session.get(f"{self.base_url}/projects/{project_id}")
                get_time = time.time() - start_time
                
                if get_response.status_code == 200:
                    retrieved_project = get_response.json()
                    if retrieved_project['name'] == test_data['name']:
                        self.log_result("database", "Data persistence - READ", True, f"Retrieved in {get_time:.3f}s")
                    else:
                        self.log_result("database", "Data persistence - READ", False, "Data mismatch")
                else:
                    self.log_result("database", "Data persistence - READ", False, f"HTTP {get_response.status_code}", get_response)
                
                # Update record
                update_data = {"name": "DB Test Project Updated", "notes": "Updated via persistence test"}
                start_time = time.time()
                update_response = self.session.put(f"{self.base_url}/projects/{project_id}", json=update_data)
                update_time = time.time() - start_time
                
                if update_response.status_code == 200:
                    self.log_result("database", "Data persistence - UPDATE", True, f"Updated in {update_time:.3f}s")
                else:
                    self.log_result("database", "Data persistence - UPDATE", False, f"HTTP {update_response.status_code}", update_response)
                
                # Delete record
                start_time = time.time()
                delete_response = self.session.delete(f"{self.base_url}/projects/{project_id}")
                delete_time = time.time() - start_time
                
                if delete_response.status_code == 200:
                    self.log_result("database", "Data persistence - DELETE", True, f"Deleted in {delete_time:.3f}s")
                else:
                    self.log_result("database", "Data persistence - DELETE", False, f"HTTP {delete_response.status_code}", delete_response)
            else:
                self.log_result("database", "Data persistence - CREATE", False, f"HTTP {create_response.status_code}", create_response)
        except Exception as e:
            self.log_result("database", "Data persistence", False, str(e))
        
        # Test query performance
        print("\n--- Query Performance Testing ---")
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/projects")
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                projects = response.json()
                if query_time < 2.0:  # Should respond within 2 seconds
                    self.log_result("performance", "Query performance", True, f"Retrieved {len(projects)} projects in {query_time:.3f}s")
                else:
                    self.log_result("performance", "Query performance", False, f"Slow query: {query_time:.3f}s")
            else:
                self.log_result("performance", "Query performance", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("performance", "Query performance", False, str(e))
    
    def test_financial_system(self):
        """Test financial management system integration"""
        print("\n💰 TESTING FINANCIAL SYSTEM INTEGRATION")
        print("=" * 50)
        
        if 'project_id' not in self.created_resources:
            # Create a project for financial testing
            project_data = {
                "name": "Financial Test Project",
                "client": "Financial Test Client",
                "contractType": "full_contract",
                "invoiceSchedule": "monthly",
                "billingDay": 15,
                "openingBalance": 0.0,
                "gcRate": 95.0,
                "startDate": datetime.now().isoformat(),
                "status": "active",
                "notes": "Financial system testing"
            }
            
            try:
                response = self.session.post(f"{self.base_url}/projects", json=project_data)
                if response.status_code == 200:
                    project = response.json()
                    self.created_resources['financial_project_id'] = project['id']
                else:
                    self.log_result("financial", "Financial test setup", False, "Could not create project for financial test")
                    return
            except Exception as e:
                self.log_result("financial", "Financial test setup", False, str(e))
                return
        
        project_id = self.created_resources.get('financial_project_id', self.created_resources.get('project_id'))
        
        # Test Invoice endpoints
        print("\n--- Invoice Management Testing ---")
        invoice_data = {
            "projectId": project_id,
            "invoiceNumber": "TEST-INV-001",
            "amount": 5000.0,
            "dueDate": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "draft",
            "lineItems": [
                {"description": "Test Service", "quantity": 1, "rate": 5000.0, "amount": 5000.0}
            ]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/invoices", json=invoice_data)
            if response.status_code == 200:
                invoice = response.json()
                self.created_resources['invoice_id'] = invoice['id']
                self.log_result("financial", "Invoice creation", True, f"Created invoice {invoice['id']}")
            else:
                self.log_result("financial", "Invoice creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Invoice creation", False, str(e))
        
        # GET Invoices
        try:
            response = self.session.get(f"{self.base_url}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                self.log_result("financial", "Invoice retrieval", True, f"Retrieved {len(invoices)} invoices")
            else:
                self.log_result("financial", "Invoice retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Invoice retrieval", False, str(e))
        
        # Test Payable endpoints
        print("\n--- Payable Management Testing ---")
        payable_data = {
            "projectId": project_id,
            "vendor": "Test Vendor",
            "amount": 2000.0,
            "dueDate": (datetime.now() + timedelta(days=15)).isoformat(),
            "status": "pending",
            "description": "Test payable"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/payables", json=payable_data)
            if response.status_code == 200:
                payable = response.json()
                self.created_resources['payable_id'] = payable['id']
                self.log_result("financial", "Payable creation", True, f"Created payable {payable['id']}")
            else:
                self.log_result("financial", "Payable creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Payable creation", False, str(e))
        
        # GET Payables
        try:
            response = self.session.get(f"{self.base_url}/payables")
            if response.status_code == 200:
                payables = response.json()
                self.log_result("financial", "Payable retrieval", True, f"Retrieved {len(payables)} payables")
            else:
                self.log_result("financial", "Payable retrieval", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Payable retrieval", False, str(e))
        
        # Test Weekly Forecast endpoint
        print("\n--- Weekly Forecast Testing ---")
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/weekly-forecast")
            if response.status_code == 200:
                forecast = response.json()
                self.log_result("financial", "Weekly forecast", True, f"Retrieved forecast with {len(forecast)} weeks")
            else:
                self.log_result("financial", "Weekly forecast", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Weekly forecast", False, str(e))
        
        # Test Company Forecast endpoint
        print("\n--- Company Forecast Testing ---")
        try:
            response = self.session.get(f"{self.base_url}/company/forecast")
            if response.status_code == 200:
                company_forecast = response.json()
                self.log_result("financial", "Company forecast", True, "Retrieved company forecast")
            else:
                self.log_result("financial", "Company forecast", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Company forecast", False, str(e))
        
        # Test Cash Runway endpoint
        print("\n--- Cash Runway Testing ---")
        try:
            response = self.session.get(f"{self.base_url}/company/cash-runway")
            if response.status_code == 200:
                cash_runway = response.json()
                self.log_result("financial", "Cash runway", True, f"Cash runway: {cash_runway.get('runwayDays', 'N/A')} days")
            else:
                self.log_result("financial", "Cash runway", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Cash runway", False, str(e))
        
        # Test Health Check endpoint
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("financial", "Health check endpoint", True, f"System status: {health_data.get('status', 'unknown')}")
            else:
                self.log_result("financial", "Health check endpoint", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Health check endpoint", False, str(e))
    
    def test_gc_dashboard_system(self):
        """Test GC Dashboard system"""
        print("\n📊 TESTING GC DASHBOARD SYSTEM")
        print("=" * 50)
        
        # Get a project for dashboard testing
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    test_project = projects[0]
                    project_id = test_project['id']
                    
                    # Test GC Dashboard data endpoint
                    print("\n--- GC Dashboard Data Testing ---")
                    try:
                        dashboard_response = self.session.get(f"{self.base_url}/gc/dashboard/{project_id}")
                        if dashboard_response.status_code == 200:
                            dashboard_data = dashboard_response.json()
                            required_fields = ['projectId', 'projectName', 'crewSummary', 'tmTagSummary']
                            missing_fields = [field for field in required_fields if field not in dashboard_data]
                            
                            if not missing_fields:
                                self.log_result("gc_dashboard", "Dashboard data structure", True, "All required fields present")
                                
                                # Test specific dashboard components
                                crew_summary = dashboard_data.get('crewSummary', {})
                                tm_summary = dashboard_data.get('tmTagSummary', {})
                                
                                self.log_result("gc_dashboard", "Crew summary data", True, 
                                              f"Hours: {crew_summary.get('totalHours', 0)}, Days: {crew_summary.get('totalDays', 0)}")
                                self.log_result("gc_dashboard", "T&M summary data", True, 
                                              f"Tags: {tm_summary.get('totalTags', 0)}, Hours: {tm_summary.get('totalHours', 0)}")
                            else:
                                self.log_result("gc_dashboard", "Dashboard data structure", False, f"Missing fields: {missing_fields}")
                        else:
                            self.log_result("gc_dashboard", "Dashboard data retrieval", False, f"HTTP {dashboard_response.status_code}", dashboard_response)
                    except Exception as e:
                        self.log_result("gc_dashboard", "Dashboard data retrieval", False, str(e))
                    
                    # Test GC Keys Admin endpoint
                    print("\n--- GC Keys Admin Testing ---")
                    try:
                        keys_response = self.session.get(f"{self.base_url}/gc/keys/admin")
                        if keys_response.status_code == 200:
                            keys = keys_response.json()
                            self.log_result("gc_dashboard", "GC keys admin", True, f"Retrieved {len(keys)} keys")
                        else:
                            self.log_result("gc_dashboard", "GC keys admin", False, f"HTTP {keys_response.status_code}", keys_response)
                    except Exception as e:
                        self.log_result("gc_dashboard", "GC keys admin", False, str(e))
                    
                    # Test GC Access Logs Admin endpoint
                    print("\n--- GC Access Logs Admin Testing ---")
                    try:
                        logs_response = self.session.get(f"{self.base_url}/gc/access-logs/admin")
                        if logs_response.status_code == 200:
                            logs = logs_response.json()
                            self.log_result("gc_dashboard", "GC access logs admin", True, f"Retrieved {len(logs)} access logs")
                        else:
                            self.log_result("gc_dashboard", "GC access logs admin", False, f"HTTP {logs_response.status_code}", logs_response)
                    except Exception as e:
                        self.log_result("gc_dashboard", "GC access logs admin", False, str(e))
                else:
                    self.log_result("gc_dashboard", "GC dashboard setup", False, "No projects available for dashboard testing")
            else:
                self.log_result("gc_dashboard", "GC dashboard setup", False, "Could not retrieve projects for dashboard testing")
        except Exception as e:
            self.log_result("gc_dashboard", "GC dashboard setup", False, str(e))
    
    def test_analytics_system(self):
        """Test analytics system"""
        print("\n📈 TESTING ANALYTICS SYSTEM")
        print("=" * 50)
        
        # Test Project Analytics
        if 'project_id' in self.created_resources:
            project_id = self.created_resources['project_id']
            
            try:
                response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
                if response.status_code == 200:
                    analytics = response.json()
                    self.log_result("core_apis", "Project analytics", True, f"Retrieved analytics for project {project_id}")
                else:
                    self.log_result("core_apis", "Project analytics", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "Project analytics", False, str(e))
        
        # Test Company Analytics
        try:
            response = self.session.get(f"{self.base_url}/company/analytics")
            if response.status_code == 200:
                company_analytics = response.json()
                self.log_result("core_apis", "Company analytics", True, "Retrieved company analytics")
            else:
                self.log_result("core_apis", "Company analytics", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "Company analytics", False, str(e))
    
    def test_error_handling(self):
        """Test error handling and logging"""
        print("\n⚠️ TESTING ERROR HANDLING & LOGGING")
        print("=" * 50)
        
        # Test invalid endpoint
        print("\n--- Invalid Endpoint Testing ---")
        try:
            response = self.session.get(f"{self.base_url}/invalid-endpoint")
            if response.status_code == 404:
                self.log_result("error_handling", "Invalid endpoint handling", True, "Correctly returns 404")
            else:
                self.log_result("error_handling", "Invalid endpoint handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Invalid endpoint handling", False, str(e))
        
        # Test invalid data
        print("\n--- Invalid Data Handling Testing ---")
        try:
            invalid_data = {"invalid": "data"}
            response = self.session.post(f"{self.base_url}/projects", json=invalid_data)
            if response.status_code in [400, 422]:  # Bad Request or Unprocessable Entity
                self.log_result("error_handling", "Invalid data handling", True, f"Correctly returns {response.status_code}")
            else:
                self.log_result("error_handling", "Invalid data handling", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Invalid data handling", False, str(e))
        
        # Test non-existent resource
        print("\n--- Non-existent Resource Testing ---")
        try:
            fake_id = str(uuid.uuid4())
            response = self.session.get(f"{self.base_url}/projects/{fake_id}")
            if response.status_code in [404, 200]:  # Some APIs return 200 with error message
                if response.status_code == 404:
                    self.log_result("error_handling", "Non-existent resource handling", True, "Correctly returns 404")
                else:
                    # Check if it returns an error message
                    try:
                        data = response.json()
                        if "error" in str(data).lower() or "not found" in str(data).lower():
                            self.log_result("error_handling", "Non-existent resource handling", True, "Returns appropriate error message")
                        else:
                            self.log_result("error_handling", "Non-existent resource handling", False, "No error indication for non-existent resource")
                    except:
                        self.log_result("error_handling", "Non-existent resource handling", False, "Invalid JSON response")
            else:
                self.log_result("error_handling", "Non-existent resource handling", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Non-existent resource handling", False, str(e))
    
    def test_performance_optimization(self):
        """Test performance optimization"""
        print("\n⚡ TESTING PERFORMANCE OPTIMIZATION")
        print("=" * 50)
        
        # Test response times for various endpoints
        endpoints_to_test = [
            ("/projects", "Projects list"),
            ("/crew-members", "Crew members list"),
            ("/tm-tags", "T&M tags list"),
            ("/materials", "Materials list"),
            ("/expenses", "Expenses list"),
            ("/invoices", "Invoices list"),
            ("/payables", "Payables list")
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    if response_time < 2.0:  # Should respond within 2 seconds
                        self.log_result("performance", f"{description} response time", True, f"{response_time:.3f}s")
                    else:
                        self.log_result("performance", f"{description} response time", False, f"Slow response: {response_time:.3f}s")
                else:
                    self.log_result("performance", f"{description} response time", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result("performance", f"{description} response time", False, str(e))
        
        # Test concurrent requests
        print("\n--- Concurrent Request Testing ---")
        import threading
        import queue
        
        def make_request(url, result_queue):
            try:
                start_time = time.time()
                response = requests.get(url)
                response_time = time.time() - start_time
                result_queue.put((response.status_code, response_time))
            except Exception as e:
                result_queue.put((0, str(e)))
        
        try:
            result_queue = queue.Queue()
            threads = []
            num_concurrent = 5
            
            # Start concurrent requests
            for i in range(num_concurrent):
                thread = threading.Thread(target=make_request, args=(f"{self.base_url}/projects", result_queue))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            successful_requests = 0
            total_time = 0
            
            while not result_queue.empty():
                status_code, response_time = result_queue.get()
                if status_code == 200:
                    successful_requests += 1
                    if isinstance(response_time, (int, float)):
                        total_time += response_time
            
            if successful_requests == num_concurrent:
                avg_time = total_time / successful_requests
                self.log_result("performance", "Concurrent requests", True, f"{successful_requests}/{num_concurrent} successful, avg: {avg_time:.3f}s")
            else:
                self.log_result("performance", "Concurrent requests", False, f"Only {successful_requests}/{num_concurrent} successful")
        except Exception as e:
            self.log_result("performance", "Concurrent requests", False, str(e))
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 STARTING COMPREHENSIVE UNIFIED BACKEND SYSTEM VALIDATION")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return
        
        # Run all test suites
        self.test_core_api_endpoints()
        self.test_authentication_system()
        self.test_database_connectivity()
        self.test_financial_system()
        self.test_gc_dashboard_system()
        self.test_analytics_system()
        self.test_error_handling()
        self.test_performance_optimization()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE UNIFIED BACKEND TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            category_name = category.replace("_", " ").title()
            print(f"\n{category_name.upper()}:")
            print(f"  Passed: {passed} ✅")
            print(f"  Failed: {failed} ❌")
            
            if results["errors"]:
                print(f"  Errors:")
                for error in results["errors"]:
                    print(f"    - {error}")
        
        total_tests = total_passed + total_failed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} ✅")
        print(f"Failed: {total_failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"{'='*80}")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! Unified backend system is fully operational.")
        elif success_rate >= 80:
            print("✅ SYSTEM MOSTLY OPERATIONAL! Minor issues detected.")
        else:
            print("⚠️ SIGNIFICANT ISSUES DETECTED! Please review the errors above.")

if __name__ == "__main__":
    tester = UnifiedBackendTester()
    tester.run_comprehensive_tests()