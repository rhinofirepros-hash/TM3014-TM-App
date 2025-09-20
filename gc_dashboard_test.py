#!/usr/bin/env python3
"""
GC Dashboard Backend API Testing
Tests the complete General Contractor access system with secure authentication and progress-only dashboards.
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os
import time

# Get backend URL from frontend .env file
BACKEND_URL = "https://project-inspect-app.preview.emergentagent.com/api"

class GCDashboardTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "gc_keys": {"passed": 0, "failed": 0, "errors": []},
            "gc_auth": {"passed": 0, "failed": 0, "errors": []},
            "gc_dashboard": {"passed": 0, "failed": 0, "errors": []},
            "project_phases": {"passed": 0, "failed": 0, "errors": []},
            "gc_access_logs": {"passed": 0, "failed": 0, "errors": []},
            "gc_narratives": {"passed": 0, "failed": 0, "errors": []},
            "security": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        self.created_project_id = None
        self.created_gc_key = None
        self.used_gc_key = None
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED")
            if message:
                print(f"   {message}")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True)
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def setup_test_project(self):
        """Create a test project for GC Dashboard testing"""
        print("\n=== Setting Up Test Project ===")
        
        project_data = {
            "name": "GC Dashboard Test Project",
            "description": "Test project for GC Dashboard functionality",
            "client_company": "Test GC Company",
            "gc_email": "gc@testcompany.com",
            "project_type": "full_project",
            "contract_amount": 200000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=90)).isoformat(),
            "address": "123 Test Street, Test City, TS 12345"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                self.created_project_id = project["id"]
                self.log_result("general", "Test project setup", True, f"Project ID: {self.created_project_id}")
                return project
            else:
                self.log_result("general", "Test project setup", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("general", "Test project setup", False, str(e))
            return None
    
    def test_gc_key_creation(self):
        """Test GC key creation endpoint"""
        print("\n=== Testing GC Key Creation ===")
        
        if not self.created_project_id:
            self.log_result("gc_keys", "GC key creation", False, "No test project available")
            return None
        
        # Generate unique 4-digit key
        unique_key = f"{uuid.uuid4().hex[:4].upper()}"
        
        gc_key_data = {
            "projectId": self.created_project_id,
            "key": unique_key,
            "expiresAt": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/keys",
                json=gc_key_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                gc_key = response.json()
                required_fields = ["id", "projectId", "key", "expiresAt", "active", "used", "created_at"]
                missing_fields = [field for field in required_fields if field not in gc_key]
                
                if not missing_fields:
                    self.created_gc_key = gc_key
                    self.log_result("gc_keys", "GC key creation", True, f"Key: {unique_key}, ID: {gc_key['id']}")
                    return gc_key
                else:
                    self.log_result("gc_keys", "GC key creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("gc_keys", "GC key creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_keys", "GC key creation", False, str(e))
        
        return None
    
    def test_gc_key_uniqueness(self):
        """Test GC key uniqueness validation"""
        print("\n=== Testing GC Key Uniqueness Validation ===")
        
        if not self.created_gc_key:
            self.log_result("gc_keys", "Key uniqueness validation", False, "No GC key available for testing")
            return False
        
        # Try to create another key with the same key value
        duplicate_key_data = {
            "projectId": self.created_project_id,
            "key": self.created_gc_key["key"],  # Same key
            "expiresAt": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/keys",
                json=duplicate_key_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should fail with 400 or similar error
            if response.status_code == 400:
                self.log_result("gc_keys", "Key uniqueness validation", True, "Duplicate key correctly rejected")
                return True
            elif response.status_code == 200:
                self.log_result("gc_keys", "Key uniqueness validation", False, "Duplicate key was accepted (should be rejected)")
                return False
            else:
                self.log_result("gc_keys", "Key uniqueness validation", False, f"Unexpected status: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("gc_keys", "Key uniqueness validation", False, str(e))
            return False
    
    def test_gc_keys_admin_view(self):
        """Test GC keys admin endpoint"""
        print("\n=== Testing GC Keys Admin View ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/keys/admin")
            
            if response.status_code == 200:
                admin_keys = response.json()
                if isinstance(admin_keys, list):
                    # Check if our created key is in the list
                    found_key = False
                    for key in admin_keys:
                        if key.get("id") == self.created_gc_key.get("id"):
                            found_key = True
                            # Verify admin view fields
                            required_fields = ["id", "projectName", "keyLastFour", "expiresAt", "active", "used"]
                            missing_fields = [field for field in required_fields if field not in key]
                            if not missing_fields:
                                self.log_result("gc_keys", "Admin view structure", True, f"Found key with proper admin fields")
                            else:
                                self.log_result("gc_keys", "Admin view structure", False, f"Missing admin fields: {missing_fields}")
                            break
                    
                    if found_key:
                        self.log_result("gc_keys", "Admin keys retrieval", True, f"Retrieved {len(admin_keys)} keys")
                    else:
                        self.log_result("gc_keys", "Admin keys retrieval", False, "Created key not found in admin view")
                    return admin_keys
                else:
                    self.log_result("gc_keys", "Admin keys retrieval", False, "Response is not a list", response)
            else:
                self.log_result("gc_keys", "Admin keys retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_keys", "Admin keys retrieval", False, str(e))
        
        return None
    
    def test_gc_login_valid_key(self):
        """Test GC login with valid key"""
        print("\n=== Testing GC Login with Valid Key ===")
        
        if not self.created_gc_key:
            self.log_result("gc_auth", "Valid key login", False, "No GC key available for testing")
            return False
        
        login_data = {
            "projectId": self.created_project_id,
            "key": self.created_gc_key["key"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                if login_result.get("success") == True:
                    self.used_gc_key = self.created_gc_key
                    self.log_result("gc_auth", "Valid key login", True, f"Login successful for project {self.created_project_id}")
                    return True
                else:
                    self.log_result("gc_auth", "Valid key login", False, "Login failed despite valid key", response)
            else:
                self.log_result("gc_auth", "Valid key login", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_auth", "Valid key login", False, str(e))
        
        return False
    
    def test_gc_login_invalid_key(self):
        """Test GC login with invalid key"""
        print("\n=== Testing GC Login with Invalid Key ===")
        
        login_data = {
            "projectId": self.created_project_id,
            "key": "INVALID_KEY_9999"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should fail with 401 or 400
            if response.status_code in [400, 401]:
                self.log_result("gc_auth", "Invalid key login", True, "Invalid key correctly rejected")
                return True
            elif response.status_code == 200:
                login_result = response.json()
                if login_result.get("success") == False:
                    self.log_result("gc_auth", "Invalid key login", True, "Invalid key correctly rejected (200 with success=false)")
                    return True
                else:
                    self.log_result("gc_auth", "Invalid key login", False, "Invalid key was accepted")
                    return False
            else:
                self.log_result("gc_auth", "Invalid key login", False, f"Unexpected status: {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_auth", "Invalid key login", False, str(e))
        
        return False
    
    def test_single_use_key_consumption(self):
        """Test that keys are marked as used after login"""
        print("\n=== Testing Single-Use Key Consumption ===")
        
        if not self.used_gc_key:
            self.log_result("gc_auth", "Single-use key consumption", False, "No used key available for testing")
            return False
        
        # Try to use the same key again
        login_data = {
            "projectId": self.created_project_id,
            "key": self.used_gc_key["key"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should fail because key is already used
            if response.status_code in [400, 401]:
                self.log_result("gc_auth", "Single-use key consumption", True, "Used key correctly rejected")
                return True
            elif response.status_code == 200:
                login_result = response.json()
                if login_result.get("success") == False:
                    self.log_result("gc_auth", "Single-use key consumption", True, "Used key correctly rejected (200 with success=false)")
                    return True
                else:
                    self.log_result("gc_auth", "Single-use key consumption", False, "Used key was accepted again (should be single-use)")
                    return False
            else:
                self.log_result("gc_auth", "Single-use key consumption", False, f"Unexpected status: {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_auth", "Single-use key consumption", False, str(e))
        
        return False
    
    def test_expired_key_rejection(self):
        """Test expired key rejection"""
        print("\n=== Testing Expired Key Rejection ===")
        
        # Create an expired key
        expired_key = f"{uuid.uuid4().hex[:4].upper()}"
        expired_key_data = {
            "projectId": self.created_project_id,
            "key": expired_key,
            "expiresAt": (datetime.now() - timedelta(days=1)).isoformat()  # Expired yesterday
        }
        
        try:
            # Create expired key
            create_response = self.session.post(
                f"{self.base_url}/gc/keys",
                json=expired_key_data,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code != 200:
                self.log_result("gc_auth", "Expired key rejection", False, "Could not create expired key for testing", create_response)
                return False
            
            # Try to login with expired key
            login_data = {
                "projectId": self.created_project_id,
                "key": expired_key
            }
            
            login_response = self.session.post(
                f"{self.base_url}/gc/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should fail because key is expired
            if login_response.status_code in [400, 401]:
                self.log_result("gc_auth", "Expired key rejection", True, "Expired key correctly rejected")
                return True
            elif login_response.status_code == 200:
                login_result = login_response.json()
                if login_result.get("success") == False:
                    self.log_result("gc_auth", "Expired key rejection", True, "Expired key correctly rejected (200 with success=false)")
                    return True
                else:
                    self.log_result("gc_auth", "Expired key rejection", False, "Expired key was accepted")
                    return False
            else:
                self.log_result("gc_auth", "Expired key rejection", False, f"Unexpected status: {login_response.status_code}", login_response)
                
        except Exception as e:
            self.log_result("gc_auth", "Expired key rejection", False, str(e))
        
        return False
    
    def setup_test_data_for_dashboard(self):
        """Setup test data (crew logs, materials, T&M tags) for dashboard testing"""
        print("\n=== Setting Up Test Data for Dashboard ===")
        
        if not self.created_project_id:
            return False
        
        # Create test crew logs
        crew_log_data = {
            "project_id": self.created_project_id,
            "date": datetime.now().isoformat(),
            "crew_members": [
                {
                    "name": "John Smith",
                    "st_hours": 8.0,
                    "ot_hours": 2.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 10.0
                },
                {
                    "name": "Mike Johnson",
                    "st_hours": 8.0,
                    "ot_hours": 1.5,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 9.5
                }
            ],
            "work_description": "Electrical panel installation and conduit running",
            "weather_conditions": "Clear, 75°F"
        }
        
        try:
            crew_response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if crew_response.status_code == 200:
                self.log_result("general", "Test crew log setup", True)
            else:
                self.log_result("general", "Test crew log setup", False, f"HTTP {crew_response.status_code}", crew_response)
        except Exception as e:
            self.log_result("general", "Test crew log setup", False, str(e))
        
        # Create test materials
        material_data = {
            "project_id": self.created_project_id,
            "project_name": "GC Dashboard Test Project",
            "purchase_date": datetime.now().isoformat(),
            "vendor": "Test Electrical Supply",
            "material_name": "12 AWG Wire",
            "quantity": 500.0,
            "unit_cost": 0.85,
            "total_cost": 425.0,
            "invoice_number": "TEST-001",
            "category": "wire"
        }
        
        try:
            material_response = self.session.post(
                f"{self.base_url}/materials",
                json=material_data,
                headers={"Content-Type": "application/json"}
            )
            
            if material_response.status_code == 200:
                self.log_result("general", "Test material setup", True)
            else:
                self.log_result("general", "Test material setup", False, f"HTTP {material_response.status_code}", material_response)
        except Exception as e:
            self.log_result("general", "Test material setup", False, str(e))
        
        # Create test T&M tag
        tm_tag_data = {
            "project_id": self.created_project_id,
            "project_name": "GC Dashboard Test Project",
            "cost_code": "TEST-001",
            "date_of_work": datetime.now().isoformat(),
            "tm_tag_title": "Test T&M Tag for GC Dashboard",
            "description_of_work": "Test work for GC dashboard validation",
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
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "gc@testcompany.com"
        }
        
        try:
            tm_response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if tm_response.status_code == 200:
                self.log_result("general", "Test T&M tag setup", True)
            else:
                self.log_result("general", "Test T&M tag setup", False, f"HTTP {tm_response.status_code}", tm_response)
        except Exception as e:
            self.log_result("general", "Test T&M tag setup", False, str(e))
        
        return True
    
    def test_gc_dashboard_data(self):
        """Test GC dashboard data endpoint"""
        print("\n=== Testing GC Dashboard Data ===")
        
        if not self.created_project_id:
            self.log_result("gc_dashboard", "Dashboard data retrieval", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/gc/dashboard/{self.created_project_id}")
            
            if response.status_code == 200:
                dashboard = response.json()
                
                # Verify required dashboard fields
                required_fields = [
                    "projectId", "projectName", "projectStatus", "overallProgress",
                    "phases", "crewSummary", "materials", "tmTagSummary", 
                    "inspections", "lastUpdated"
                ]
                missing_fields = [field for field in required_fields if field not in dashboard]
                
                if not missing_fields:
                    self.log_result("gc_dashboard", "Dashboard structure", True, "All required fields present")
                    
                    # Test crew summary (no financial data)
                    crew_summary = dashboard.get("crewSummary", {})
                    crew_fields = ["totalHours", "totalDays", "activeCrewMembers"]
                    crew_missing = [field for field in crew_fields if field not in crew_summary]
                    
                    if not crew_missing:
                        self.log_result("gc_dashboard", "Crew summary structure", True, f"Hours: {crew_summary.get('totalHours')}, Days: {crew_summary.get('totalDays')}")
                    else:
                        self.log_result("gc_dashboard", "Crew summary structure", False, f"Missing crew fields: {crew_missing}")
                    
                    # Test T&M tag summary (no financial data)
                    tm_summary = dashboard.get("tmTagSummary", {})
                    tm_fields = ["totalTags", "submittedTags", "totalHours"]
                    tm_missing = [field for field in tm_fields if field not in tm_summary]
                    
                    if not tm_missing:
                        self.log_result("gc_dashboard", "T&M summary structure", True, f"Tags: {tm_summary.get('totalTags')}, Hours: {tm_summary.get('totalHours')}")
                    else:
                        self.log_result("gc_dashboard", "T&M summary structure", False, f"Missing T&M fields: {tm_missing}")
                    
                    # Test materials summary (quantities only, no costs)
                    materials = dashboard.get("materials", [])
                    if materials:
                        material = materials[0]
                        if "quantity" in material and "cost" not in material and "total_cost" not in material:
                            self.log_result("security", "Materials no financial data", True, "Materials contain quantities only, no costs")
                        else:
                            self.log_result("security", "Materials no financial data", False, "Materials may contain financial data")
                    
                    return dashboard
                else:
                    self.log_result("gc_dashboard", "Dashboard structure", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("gc_dashboard", "Dashboard data retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_dashboard", "Dashboard data retrieval", False, str(e))
        
        return None
    
    def test_gc_dashboard_api_fix(self):
        """Test the specific GC Dashboard API fix for confirmed project IDs"""
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
                    expected_fields = ["project_id", "project_name", "crew_summary", "materials_summary", "tm_tags_summary"]
                    missing_fields = [field for field in expected_fields if field not in response_data]
                    
                    if not missing_fields:
                        self.log_result("gc_dashboard", f"GC Dashboard API Fix - Project {project_id}", True, 
                                      f"Returns 200 OK with complete dashboard data. Project: {response_data.get('project_name', 'Unknown')}")
                        
                        # Log some key metrics from the response
                        crew_summary = response_data.get("crew_summary", {})
                        materials_summary = response_data.get("materials_summary", {})
                        tm_tags_summary = response_data.get("tm_tags_summary", {})
                        
                        print(f"   📊 Dashboard Data Summary:")
                        print(f"   - Project Name: {response_data.get('project_name', 'N/A')}")
                        print(f"   - Total Hours: {crew_summary.get('total_hours', 0)}")
                        print(f"   - Work Days: {crew_summary.get('total_days', 0)}")
                        print(f"   - Materials Count: {materials_summary.get('total_items', 0)}")
                        print(f"   - T&M Tags Count: {tm_tags_summary.get('total_tags', 0)}")
                        
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
    
    def test_financial_data_exclusion(self):
        """Test that no financial data is exposed in GC dashboard"""
        print("\n=== Testing Financial Data Exclusion ===")
        
        dashboard = self.test_gc_dashboard_data()
        if not dashboard:
            self.log_result("security", "Financial data exclusion", False, "Could not retrieve dashboard for testing")
            return False
        
        # Check for financial fields that should NOT be present
        financial_fields = [
            "contract_amount", "total_cost", "labor_cost", "material_cost", 
            "profit", "profit_margin", "hourly_rate", "billing_rate", 
            "unit_cost", "cost", "amount"
        ]
        
        dashboard_str = json.dumps(dashboard).lower()
        found_financial_fields = []
        
        for field in financial_fields:
            # Use word boundaries to avoid false positives like "generated" containing "rate"
            if f'"{field}"' in dashboard_str or f"'{field}'" in dashboard_str:
                found_financial_fields.append(field)
        
        if not found_financial_fields:
            self.log_result("security", "Financial data exclusion", True, "No financial data found in dashboard")
            return True
        else:
            self.log_result("security", "Financial data exclusion", False, f"Found financial fields: {found_financial_fields}")
            return False
    
    def test_project_phases_creation(self):
        """Test project phases creation"""
        print("\n=== Testing Project Phases Creation ===")
        
        if not self.created_project_id:
            self.log_result("project_phases", "Phase creation", False, "No test project available")
            return None
        
        phase_data = {
            "projectId": self.created_project_id,
            "phase": "installation",
            "percentComplete": 25.0,
            "plannedDate": (datetime.now() + timedelta(days=30)).isoformat(),
            "notes": "Installation phase for GC dashboard testing"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/project-phases",
                json=phase_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                phase = response.json()
                required_fields = ["id", "projectId", "phase", "percentComplete", "created_at"]
                missing_fields = [field for field in required_fields if field not in phase]
                
                if not missing_fields:
                    self.created_phase_id = phase["id"]
                    self.log_result("project_phases", "Phase creation", True, f"Phase: {phase['phase']}, Progress: {phase['percentComplete']}%")
                    return phase
                else:
                    self.log_result("project_phases", "Phase creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("project_phases", "Phase creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("project_phases", "Phase creation", False, str(e))
        
        return None
    
    def test_project_phases_retrieval(self):
        """Test project phases retrieval"""
        print("\n=== Testing Project Phases Retrieval ===")
        
        if not self.created_project_id:
            self.log_result("project_phases", "Phase retrieval", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/project-phases/{self.created_project_id}")
            
            if response.status_code == 200:
                phases = response.json()
                if isinstance(phases, list):
                    self.log_result("project_phases", "Phase retrieval", True, f"Retrieved {len(phases)} phases")
                    return phases
                else:
                    self.log_result("project_phases", "Phase retrieval", False, "Response is not a list", response)
            else:
                self.log_result("project_phases", "Phase retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("project_phases", "Phase retrieval", False, str(e))
        
        return None
    
    def test_project_phase_update(self):
        """Test project phase update"""
        print("\n=== Testing Project Phase Update ===")
        
        if not hasattr(self, 'created_phase_id'):
            self.log_result("project_phases", "Phase update", False, "No phase available for testing")
            return False
        
        update_data = {
            "percentComplete": 50.0,
            "notes": "Updated progress for GC dashboard testing"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/project-phases/{self.created_phase_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_phase = response.json()
                if updated_phase.get("percentComplete") == 50.0:
                    self.log_result("project_phases", "Phase update", True, f"Progress updated to {updated_phase['percentComplete']}%")
                    return True
                else:
                    self.log_result("project_phases", "Phase update", False, "Update not reflected", response)
            else:
                self.log_result("project_phases", "Phase update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("project_phases", "Phase update", False, str(e))
        
        return False
    
    def test_gc_access_logs(self):
        """Test GC access logs admin endpoint"""
        print("\n=== Testing GC Access Logs ===")
        
        try:
            response = self.session.get(f"{self.base_url}/gc/access-logs/admin")
            
            if response.status_code == 200:
                logs = response.json()
                if isinstance(logs, list):
                    # Look for our login attempt
                    found_log = False
                    for log in logs:
                        if log.get("projectName") == "GC Dashboard Test Project":
                            found_log = True
                            # Verify log structure
                            required_fields = ["id", "projectName", "timestamp", "ip", "status"]
                            missing_fields = [field for field in required_fields if field not in log]
                            if not missing_fields:
                                self.log_result("gc_access_logs", "Access log structure", True, f"Status: {log['status']}, IP: {log['ip']}")
                            else:
                                self.log_result("gc_access_logs", "Access log structure", False, f"Missing fields: {missing_fields}")
                            break
                    
                    if found_log:
                        self.log_result("gc_access_logs", "Access logs retrieval", True, f"Retrieved {len(logs)} access logs")
                    else:
                        self.log_result("gc_access_logs", "Access logs retrieval", True, f"Retrieved {len(logs)} access logs (test login may not be logged yet)")
                    return logs
                else:
                    self.log_result("gc_access_logs", "Access logs retrieval", False, "Response is not a list", response)
            else:
                self.log_result("gc_access_logs", "Access logs retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_access_logs", "Access logs retrieval", False, str(e))
        
        return None
    
    def test_gc_narratives_creation(self):
        """Test GC narratives creation"""
        print("\n=== Testing GC Narratives Creation ===")
        
        if not self.created_project_id:
            self.log_result("gc_narratives", "Narrative creation", False, "No test project available")
            return None
        
        narrative_data = {
            "projectId": self.created_project_id,
            "narrative": "Project is progressing well. Installation phase is 25% complete with electrical panel work underway. Crew of 2 electricians working 19.5 total hours. Weather conditions are favorable for continued work."
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/gc-narratives",
                json=narrative_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                narrative = response.json()
                required_fields = ["id", "projectId", "narrative", "generatedAt"]
                missing_fields = [field for field in required_fields if field not in narrative]
                
                if not missing_fields:
                    self.created_narrative_id = narrative["id"]
                    self.log_result("gc_narratives", "Narrative creation", True, f"Narrative ID: {narrative['id']}")
                    return narrative
                else:
                    self.log_result("gc_narratives", "Narrative creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("gc_narratives", "Narrative creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_narratives", "Narrative creation", False, str(e))
        
        return None
    
    def test_gc_narratives_retrieval(self):
        """Test GC narratives retrieval"""
        print("\n=== Testing GC Narratives Retrieval ===")
        
        if not self.created_project_id:
            self.log_result("gc_narratives", "Narrative retrieval", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/gc-narratives/{self.created_project_id}")
            
            if response.status_code == 200:
                narrative = response.json()
                if narrative and "narrative" in narrative:
                    self.log_result("gc_narratives", "Narrative retrieval", True, f"Retrieved narrative: {narrative['narrative'][:50]}...")
                    return narrative
                else:
                    self.log_result("gc_narratives", "Narrative retrieval", False, "No narrative found or invalid structure", response)
            else:
                self.log_result("gc_narratives", "Narrative retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("gc_narratives", "Narrative retrieval", False, str(e))
        
        return None
    
    def test_data_integration(self):
        """Test that GC dashboard pulls from existing collections"""
        print("\n=== Testing Data Integration ===")
        
        dashboard = self.test_gc_dashboard_data()
        if not dashboard:
            self.log_result("gc_dashboard", "Data integration", False, "Could not retrieve dashboard")
            return False
        
        # Verify data comes from existing collections
        crew_summary = dashboard.get("crewSummary", {})
        tm_summary = dashboard.get("tmTagSummary", {})
        materials = dashboard.get("materials", [])
        
        integration_tests = []
        
        # Test crew data integration
        if crew_summary.get("totalHours", 0) > 0:
            integration_tests.append("crew_logs")
            self.log_result("gc_dashboard", "Crew data integration", True, f"Total hours: {crew_summary['totalHours']}")
        
        # Test T&M data integration
        if tm_summary.get("totalTags", 0) > 0:
            integration_tests.append("tm_tags")
            self.log_result("gc_dashboard", "T&M data integration", True, f"Total tags: {tm_summary['totalTags']}")
        
        # Test materials data integration
        if len(materials) > 0:
            integration_tests.append("materials")
            self.log_result("gc_dashboard", "Materials data integration", True, f"Materials count: {len(materials)}")
        
        if len(integration_tests) >= 2:
            self.log_result("gc_dashboard", "Overall data integration", True, f"Integrated data from: {', '.join(integration_tests)}")
            return True
        else:
            self.log_result("gc_dashboard", "Overall data integration", False, f"Limited integration: {integration_tests}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("GC DASHBOARD BACKEND TESTING SUMMARY")
        print("="*80)
        
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
                
                if results["errors"]:
                    for error in results["errors"]:
                        print(f"   ❌ {error}")
        
        print("-" * 80)
        overall_success_rate = (total_passed / (total_passed + total_failed)) * 100 if (total_passed + total_failed) > 0 else 0
        print(f"OVERALL: {total_passed}/{total_passed + total_failed} tests passed ({overall_success_rate:.1f}%)")
        
        if overall_success_rate >= 90:
            print("🎉 EXCELLENT: GC Dashboard system is fully functional!")
        elif overall_success_rate >= 70:
            print("✅ GOOD: GC Dashboard system is mostly functional with minor issues")
        else:
            print("❌ NEEDS WORK: GC Dashboard system has significant issues")
        
        print("="*80)
    
    def run_all_tests(self):
        """Run all GC Dashboard tests"""
        print("🚀 Starting GC Dashboard Backend Testing...")
        print("Testing comprehensive General Contractor access system")
        
        # Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Cannot connect to backend. Stopping tests.")
            return
        
        # PRIORITY: Test the specific GC Dashboard API fix first
        print("\n🎯 PRIORITY TEST: GC Dashboard API Fix")
        self.test_gc_dashboard_api_fix()
        
        # Setup
        if not self.setup_test_project():
            print("❌ Cannot create test project. Stopping tests.")
            return
        
        # GC Key Management Tests
        self.test_gc_key_creation()
        self.test_gc_key_uniqueness()
        self.test_gc_keys_admin_view()
        
        # GC Authentication Tests
        self.test_gc_login_valid_key()
        self.test_gc_login_invalid_key()
        self.test_single_use_key_consumption()
        self.test_expired_key_rejection()
        
        # Setup test data for dashboard
        self.setup_test_data_for_dashboard()
        
        # GC Dashboard Tests
        self.test_gc_dashboard_data()
        self.test_financial_data_exclusion()
        self.test_data_integration()
        
        # Project Phases Tests
        self.test_project_phases_creation()
        self.test_project_phases_retrieval()
        self.test_project_phase_update()
        
        # GC Access Logs Tests
        self.test_gc_access_logs()
        
        # GC Narratives Tests
        self.test_gc_narratives_creation()
        self.test_gc_narratives_retrieval()
        
        # Print final summary
        self.print_summary()

if __name__ == "__main__":
    tester = GCDashboardTester()
    tester.run_all_tests()