#!/usr/bin/env python3
"""
Comprehensive Backend System Validation
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
BACKEND_URL = "https://firepro-auth-hub.preview.emergentagent.com/api"

class ComprehensiveBackendTester:
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
        
        # Test T&M Tag CRUD operations
        print("\n--- T&M Tag CRUD Operations ---")
        tm_tag_data = {
            "project_name": "Backend Test Project",
            "cost_code": "TEST-001",
            "date_of_work": datetime.now().isoformat(),
            "tm_tag_title": "Backend API Test",
            "description_of_work": "Testing T&M tag CRUD operations",
            "labor_entries": [{
                "id": str(uuid.uuid4()),
                "worker_name": "Test Worker",
                "quantity": 1,
                "st_hours": 8.0,
                "ot_hours": 0.0,
                "dt_hours": 0.0,
                "pot_hours": 0.0,
                "total_hours": 8.0,
                "date": datetime.now().strftime("%Y-%m-%d")
            }],
            "material_entries": [],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "test@backend.com"
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
                tags = response.json()
                self.log_result("core_apis", "GET /api/tm-tags", True, f"Retrieved {len(tags)} tags")
            else:
                self.log_result("core_apis", "GET /api/tm-tags", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/tm-tags", False, str(e))
        
        # PUT T&M Tag (if created)
        if 'tm_tag_id' in self.created_resources:
            try:
                update_data = {"tm_tag_title": "Updated Backend Test"}
                response = self.session.put(f"{self.base_url}/tm-tags/{self.created_resources['tm_tag_id']}", json=update_data)
                if response.status_code == 200:
                    self.log_result("core_apis", "PUT /api/tm-tags", True, "T&M tag updated")
                else:
                    self.log_result("core_apis", "PUT /api/tm-tags", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "PUT /api/tm-tags", False, str(e))
        
        # DELETE T&M Tag (if created)
        if 'tm_tag_id' in self.created_resources:
            try:
                response = self.session.delete(f"{self.base_url}/tm-tags/{self.created_resources['tm_tag_id']}")
                if response.status_code == 200:
                    self.log_result("core_apis", "DELETE /api/tm-tags", True, "T&M tag deleted")
                else:
                    self.log_result("core_apis", "DELETE /api/tm-tags", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "DELETE /api/tm-tags", False, str(e))
        
        # Test Project Management endpoints
        print("\n--- Project Management CRUD Operations ---")
        project_data = {
            "name": "Backend Test Project",
            "description": "Testing project management APIs",
            "client_company": "Test Client",
            "gc_email": "gc@test.com",
            "contract_amount": 50000.0,
            "labor_rate": 95.0,
            "start_date": datetime.now().isoformat(),
            "address": "Test Address"
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
        
        # Test Employee Management endpoints
        print("\n--- Employee Management CRUD Operations ---")
        employee_data = {
            "name": "Test Employee",
            "hourly_rate": 45.0,
            "gc_billing_rate": 95.0,
            "position": "Test Electrician",
            "hire_date": datetime.now().isoformat(),
            "phone": "(555) 123-4567",
            "email": "test@employee.com"
        }
        
        # POST Employee
        try:
            response = self.session.post(f"{self.base_url}/employees", json=employee_data)
            if response.status_code == 200:
                employee = response.json()
                self.created_resources['employee_id'] = employee['id']
                self.log_result("core_apis", "POST /api/employees", True, f"Created employee {employee['id']}")
            else:
                self.log_result("core_apis", "POST /api/employees", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "POST /api/employees", False, str(e))
        
        # GET Employees
        try:
            response = self.session.get(f"{self.base_url}/employees")
            if response.status_code == 200:
                employees = response.json()
                self.log_result("core_apis", "GET /api/employees", True, f"Retrieved {len(employees)} employees")
            else:
                self.log_result("core_apis", "GET /api/employees", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/employees", False, str(e))
        
        # Test Crew Log endpoints
        print("\n--- Crew Log CRUD Operations ---")
        if 'project_id' in self.created_resources:
            crew_log_data = {
                "project_id": self.created_resources['project_id'],
                "date": datetime.now().isoformat(),
                "crew_members": [{"name": "Test Worker", "st_hours": 8.0, "total_hours": 8.0}],
                "work_description": "Backend test work",
                "weather_conditions": "clear"
            }
            
            # POST Crew Log
            try:
                response = self.session.post(f"{self.base_url}/crew-logs", json=crew_log_data)
                if response.status_code == 200:
                    crew_log = response.json()
                    self.created_resources['crew_log_id'] = crew_log['id']
                    self.log_result("core_apis", "POST /api/crew-logs", True, f"Created crew log {crew_log['id']}")
                else:
                    self.log_result("core_apis", "POST /api/crew-logs", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("core_apis", "POST /api/crew-logs", False, str(e))
        
        # GET Crew Logs
        try:
            response = self.session.get(f"{self.base_url}/crew-logs")
            if response.status_code == 200:
                crew_logs = response.json()
                self.log_result("core_apis", "GET /api/crew-logs", True, f"Retrieved {len(crew_logs)} crew logs")
            else:
                self.log_result("core_apis", "GET /api/crew-logs", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("core_apis", "GET /api/crew-logs", False, str(e))
        
        # Test Material endpoints
        print("\n--- Material Management CRUD Operations ---")
        if 'project_id' in self.created_resources:
            material_data = {
                "project_id": self.created_resources['project_id'],
                "project_name": "Backend Test Project",
                "purchase_date": datetime.now().isoformat(),
                "vendor": "Test Vendor",
                "material_name": "Test Material",
                "quantity": 10.0,
                "unit_cost": 5.0,
                "total_cost": 50.0,
                "invoice_number": "TEST-001"
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
            "description": "Testing database persistence",
            "client_company": "DB Test Client",
            "gc_email": "db@test.com",
            "contract_amount": 25000.0,
            "start_date": datetime.now().isoformat(),
            "address": "DB Test Address"
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
                update_data = {"name": "DB Test Project Updated"}
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
    
    def test_sync_functionality(self):
        """Test bidirectional sync functionality"""
        print("\n🔄 TESTING SYNC FUNCTIONALITY")
        print("=" * 50)
        
        if 'project_id' not in self.created_resources:
            # Create a project for sync testing
            project_data = {
                "name": "Sync Test Project",
                "description": "Testing sync functionality",
                "client_company": "Sync Test Client",
                "gc_email": "sync@test.com",
                "contract_amount": 30000.0,
                "start_date": datetime.now().isoformat(),
                "address": "Sync Test Address"
            }
            
            try:
                response = self.session.post(f"{self.base_url}/projects", json=project_data)
                if response.status_code == 200:
                    project = response.json()
                    self.created_resources['sync_project_id'] = project['id']
                else:
                    self.log_result("sync", "Sync test setup", False, "Could not create project for sync test")
                    return
            except Exception as e:
                self.log_result("sync", "Sync test setup", False, str(e))
                return
        
        project_id = self.created_resources.get('sync_project_id', self.created_resources.get('project_id'))
        
        # Test crew log creation and sync
        print("\n--- Crew Log to T&M Sync Testing ---")
        crew_log_data = {
            "project_id": project_id,
            "date": datetime.now().isoformat(),
            "crew_members": [{
                "name": "Sync Test Worker",
                "st_hours": 8.0,
                "ot_hours": 0.0,
                "dt_hours": 0.0,
                "pot_hours": 0.0,
                "total_hours": 8.0
            }],
            "work_description": "Testing sync functionality",
            "weather_conditions": "clear"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/crew-logs", json=crew_log_data)
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log['id']
                self.log_result("sync", "Crew log creation", True, f"Created crew log {crew_log_id}")
                
                # Wait for sync to complete
                time.sleep(2)
                
                # Check if T&M tag was auto-created
                tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
                if tm_tags_response.status_code == 200:
                    tm_tags = tm_tags_response.json()
                    auto_tm_tag = None
                    for tag in tm_tags:
                        if (tag.get("project_id") == project_id and 
                            "Auto-generated from Crew Log" in tag.get("tm_tag_title", "")):
                            auto_tm_tag = tag
                            break
                    
                    if auto_tm_tag:
                        self.log_result("sync", "Crew log → T&M sync", True, f"Auto-generated T&M tag: {auto_tm_tag['id']}")
                    else:
                        self.log_result("sync", "Crew log → T&M sync", False, "No auto-generated T&M tag found")
                else:
                    self.log_result("sync", "Crew log → T&M sync", False, "Could not verify T&M tag creation")
                
                # Test manual sync endpoint
                try:
                    sync_response = self.session.post(f"{self.base_url}/crew-logs/{crew_log_id}/sync")
                    if sync_response.status_code == 200:
                        self.log_result("sync", "Manual sync endpoint", True, "Manual sync successful")
                    else:
                        self.log_result("sync", "Manual sync endpoint", False, f"HTTP {sync_response.status_code}", sync_response)
                except Exception as e:
                    self.log_result("sync", "Manual sync endpoint", False, str(e))
            else:
                self.log_result("sync", "Crew log creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("sync", "Crew log creation", False, str(e))
    
    def test_financial_system(self):
        """Test financial management system integration"""
        print("\n💰 TESTING FINANCIAL SYSTEM INTEGRATION")
        print("=" * 50)
        
        if 'project_id' not in self.created_resources:
            self.log_result("financial", "Financial test setup", False, "No project available for financial testing")
            return
        
        project_id = self.created_resources['project_id']
        
        # Test Invoice endpoints
        print("\n--- Invoice Management Testing ---")
        invoice_data = {
            "project_id": project_id,
            "invoice_number": "TEST-INV-001",
            "client_name": "Test Client",
            "amount": 5000.0,
            "status": "draft",
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "line_items": [
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
        
        # Test Payable endpoints
        print("\n--- Payable Management Testing ---")
        payable_data = {
            "project_id": project_id,
            "vendor_name": "Test Vendor",
            "amount": 2000.0,
            "status": "pending",
            "due_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "po_number": "PO-TEST-001",
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
        
        # Test Cashflow Forecast endpoints
        print("\n--- Cashflow Forecast Testing ---")
        cashflow_data = {
            "project_id": project_id,
            "week_starting": datetime.now().isoformat(),
            "projected_inflow": 5000.0,
            "projected_outflow": 2000.0,
            "net_cashflow": 3000.0,
            "running_balance": 3000.0
        }
        
        try:
            response = self.session.post(f"{self.base_url}/cashflow-forecasts", json=cashflow_data)
            if response.status_code == 200:
                cashflow = response.json()
                self.created_resources['cashflow_id'] = cashflow['id']
                self.log_result("financial", "Cashflow forecast creation", True, f"Created cashflow forecast {cashflow['id']}")
            else:
                self.log_result("financial", "Cashflow forecast creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Cashflow forecast creation", False, str(e))
        
        # Test Profitability endpoints
        print("\n--- Profitability Analysis Testing ---")
        profitability_data = {
            "project_id": project_id,
            "period": "monthly",
            "revenue": 5000.0,
            "direct_costs": 2000.0,
            "indirect_costs": 500.0,
            "gross_profit": 2500.0,
            "profit_margin": 50.0,
            "alert_status": "healthy"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/profitability", json=profitability_data)
            if response.status_code == 200:
                profitability = response.json()
                self.created_resources['profitability_id'] = profitability['id']
                self.log_result("financial", "Profitability analysis creation", True, f"Created profitability analysis {profitability['id']}")
            else:
                self.log_result("financial", "Profitability analysis creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("financial", "Profitability analysis creation", False, str(e))
        
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
                            else:
                                self.log_result("gc_dashboard", "Dashboard data structure", False, f"Missing fields: {missing_fields}")
                        else:
                            self.log_result("gc_dashboard", "Dashboard data retrieval", False, f"HTTP {dashboard_response.status_code}", dashboard_response)
                    except Exception as e:
                        self.log_result("gc_dashboard", "Dashboard data retrieval", False, str(e))
                    
                    # Test Project Phases Management
                    print("\n--- Project Phases Management Testing ---")
                    phase_data = {
                        "projectId": project_id,
                        "phaseName": "Test Phase",
                        "progress": 50.0,
                        "status": "in_progress"
                    }
                    
                    try:
                        phase_response = self.session.post(f"{self.base_url}/project-phases", json=phase_data)
                        if phase_response.status_code == 200:
                            phase = phase_response.json()
                            self.log_result("gc_dashboard", "Project phase creation", True, f"Created phase {phase['id']}")
                            
                            # Test phase retrieval
                            get_phases_response = self.session.get(f"{self.base_url}/project-phases/{project_id}")
                            if get_phases_response.status_code == 200:
                                phases = get_phases_response.json()
                                self.log_result("gc_dashboard", "Project phases retrieval", True, f"Retrieved {len(phases)} phases")
                            else:
                                self.log_result("gc_dashboard", "Project phases retrieval", False, f"HTTP {get_phases_response.status_code}", get_phases_response)
                        else:
                            self.log_result("gc_dashboard", "Project phase creation", False, f"HTTP {phase_response.status_code}", phase_response)
                    except Exception as e:
                        self.log_result("gc_dashboard", "Project phase creation", False, str(e))
                    
                    # Test GC Narratives
                    print("\n--- GC Narratives Testing ---")
                    narrative_data = {
                        "projectId": project_id,
                        "narrative": "Test narrative for project progress",
                        "author": "Test System"
                    }
                    
                    try:
                        narrative_response = self.session.post(f"{self.base_url}/gc-narratives", json=narrative_data)
                        if narrative_response.status_code == 200:
                            narrative = narrative_response.json()
                            self.log_result("gc_dashboard", "GC narrative creation", True, f"Created narrative {narrative['id']}")
                            
                            # Test narrative retrieval
                            get_narrative_response = self.session.get(f"{self.base_url}/gc-narratives/{project_id}")
                            if get_narrative_response.status_code == 200:
                                latest_narrative = get_narrative_response.json()
                                self.log_result("gc_dashboard", "GC narrative retrieval", True, "Retrieved latest narrative")
                            else:
                                self.log_result("gc_dashboard", "GC narrative retrieval", False, f"HTTP {get_narrative_response.status_code}", get_narrative_response)
                        else:
                            self.log_result("gc_dashboard", "GC narrative creation", False, f"HTTP {narrative_response.status_code}", narrative_response)
                    except Exception as e:
                        self.log_result("gc_dashboard", "GC narrative creation", False, str(e))
                else:
                    self.log_result("gc_dashboard", "GC dashboard setup", False, "No projects available for dashboard testing")
            else:
                self.log_result("gc_dashboard", "GC dashboard setup", False, "Could not retrieve projects for dashboard testing")
        except Exception as e:
            self.log_result("gc_dashboard", "GC dashboard setup", False, str(e))
    
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
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        self.log_result("error_handling", "Non-existent resource handling", True, "Returns error message")
                    else:
                        self.log_result("error_handling", "Non-existent resource handling", False, "No error message for non-existent resource")
                else:
                    self.log_result("error_handling", "Non-existent resource handling", True, "Correctly returns 404")
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
            ("/employees", "Employees list"),
            ("/tm-tags", "T&M tags list"),
            ("/crew-logs", "Crew logs list"),
            ("/materials", "Materials list")
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
        print("🚀 STARTING COMPREHENSIVE BACKEND SYSTEM VALIDATION")
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
        self.test_sync_functionality()
        self.test_financial_system()
        self.test_gc_dashboard_system()
        self.test_error_handling()
        self.test_performance_optimization()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
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
            print("🎉 ALL TESTS PASSED! Backend system is fully operational.")
        else:
            print("⚠️ Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    tester.run_comprehensive_tests()