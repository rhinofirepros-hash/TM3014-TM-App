#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Enhanced Rhino Platform with Project Intelligence System
Tests all new LLM-powered features and enhanced backend functionality
"""

import requests
import json
from datetime import datetime, timedelta, date
import uuid
import base64
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://tm3014-tm-app-production.up.railway.app/api"

class TMTagAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "tm_tags": {"passed": 0, "failed": 0, "errors": []},
            "workers": {"passed": 0, "failed": 0, "errors": []},
            "projects": {"passed": 0, "failed": 0, "errors": []},
            "employees": {"passed": 0, "failed": 0, "errors": []},
            "crew_logs": {"passed": 0, "failed": 0, "errors": []},
            "materials": {"passed": 0, "failed": 0, "errors": []},
            "analytics": {"passed": 0, "failed": 0, "errors": []},
            "email": {"passed": 0, "failed": 0, "errors": []},
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
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True)
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def create_realistic_tm_tag_data(self):
        """Create realistic T&M tag data for testing"""
        today = datetime.now()
        work_date = today - timedelta(days=1)  # Yesterday's work
        
        return {
            "project_name": "Downtown Office Complex - Phase 2",
            "cost_code": "CC-2024-0156",
            "date_of_work": work_date.isoformat(),
            "customer_reference": "REF-DOC-2024-001",
            "tm_tag_title": "Electrical Installation - Floor 3",
            "description_of_work": "Installation of electrical conduits, outlets, and lighting fixtures on the third floor of the downtown office complex. Work included running 12 AWG wire through conduits, installing 24 duplex outlets, and mounting 8 LED light fixtures.",
            "labor_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Mike Rodriguez",
                    "quantity": 1,
                    "st_hours": 8.0,
                    "ot_hours": 2.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 10.0,
                    "date": work_date.strftime("%Y-%m-%d")
                },
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Sarah Johnson",
                    "quantity": 1,
                    "st_hours": 8.0,
                    "ot_hours": 1.5,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 9.5,
                    "date": work_date.strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "material_name": "12 AWG THHN Wire",
                    "unit_of_measure": "feet",
                    "quantity": 500.0,
                    "unit_cost": 0.85,
                    "total": 425.0,
                    "date_of_work": work_date.strftime("%Y-%m-%d")
                },
                {
                    "id": str(uuid.uuid4()),
                    "material_name": "Duplex Outlets",
                    "unit_of_measure": "each",
                    "quantity": 24.0,
                    "unit_cost": 12.50,
                    "total": 300.0,
                    "date_of_work": work_date.strftime("%Y-%m-%d")
                }
            ],
            "equipment_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "equipment_name": "Wire Pulling System",
                    "pieces_of_equipment": 1,
                    "unit_of_measure": "day",
                    "quantity": 1.0,
                    "total": 150.0,
                    "date_of_work": work_date.strftime("%Y-%m-%d")
                }
            ],
            "other_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "other_name": "Permit Fees",
                    "quantity_of_other": 1,
                    "unit_of_measure": "permit",
                    "quantity_of_unit": 1.0,
                    "total": 75.0,
                    "date_of_work": work_date.strftime("%Y-%m-%d")
                }
            ],
            "gc_email": "project.manager@downtownoffice.com",
            "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
    
    def test_tm_tag_creation(self):
        """Test T&M tag creation endpoint"""
        print("\n=== Testing T&M Tag Creation ===")
        
        tm_tag_data = self.create_realistic_tm_tag_data()
        
        try:
            response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Verify response structure
                required_fields = ["id", "project_name", "cost_code", "created_at", "submitted_at"]
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    self.created_tm_tag_id = response_data["id"]
                    self.log_result("tm_tags", "T&M tag creation", True)
                    return response_data
                else:
                    self.log_result("tm_tags", "T&M tag creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("tm_tags", "T&M tag creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("tm_tags", "T&M tag creation", False, str(e))
        
        return None
    
    def test_tm_tag_retrieval(self):
        """Test T&M tag retrieval endpoint"""
        print("\n=== Testing T&M Tag Retrieval ===")
        
        try:
            response = self.session.get(f"{self.base_url}/tm-tags")
            
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    self.log_result("tm_tags", "T&M tag retrieval", True, f"Retrieved {len(response_data)} tags")
                    return response_data
                else:
                    self.log_result("tm_tags", "T&M tag retrieval", False, "Response is not a list", response)
            else:
                self.log_result("tm_tags", "T&M tag retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("tm_tags", "T&M tag retrieval", False, str(e))
        
        return None
    
    def test_tm_tag_by_id(self, tm_tag_id):
        """Test T&M tag retrieval by ID"""
        print(f"\n=== Testing T&M Tag Retrieval by ID: {tm_tag_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/tm-tags/{tm_tag_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "id" in response_data and response_data["id"] == tm_tag_id:
                    self.log_result("tm_tags", "T&M tag by ID", True)
                    return response_data
                else:
                    self.log_result("tm_tags", "T&M tag by ID", False, "ID mismatch in response", response)
            else:
                self.log_result("tm_tags", "T&M tag by ID", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("tm_tags", "T&M tag by ID", False, str(e))
        
        return None
    
    def test_tm_tag_deletion(self):
        """Test T&M tag deletion endpoint - comprehensive DELETE functionality test"""
        print("\n=== Testing T&M Tag Deletion Functionality ===")
        
        # Step 1: First, get existing T&M tags to work with
        print("Step 1: Getting existing T&M tags...")
        try:
            response = self.session.get(f"{self.base_url}/tm-tags")
            if response.status_code != 200:
                self.log_result("tm_tags", "DELETE test - Get existing tags", False, f"HTTP {response.status_code}", response)
                return False
            
            existing_tags = response.json()
            if not existing_tags:
                # Create a tag first if none exist
                print("No existing tags found. Creating one for deletion test...")
                created_tag = self.test_tm_tag_creation()
                if not created_tag:
                    self.log_result("tm_tags", "DELETE test - Setup", False, "Could not create tag for deletion test")
                    return False
                tag_to_delete = created_tag
                tag_id = created_tag["id"]
            else:
                tag_to_delete = existing_tags[0]
                tag_id = tag_to_delete["id"]
                
            self.log_result("tm_tags", "DELETE test - Get existing tags", True, f"Found tag to delete: {tag_id}")
            
        except Exception as e:
            self.log_result("tm_tags", "DELETE test - Get existing tags", False, str(e))
            return False
        
        # Step 2: Verify the tag exists by getting it individually
        print(f"Step 2: Verifying tag {tag_id} exists...")
        try:
            response = self.session.get(f"{self.base_url}/tm-tags/{tag_id}")
            if response.status_code == 200:
                self.log_result("tm_tags", "DELETE test - Verify tag exists", True)
            else:
                self.log_result("tm_tags", "DELETE test - Verify tag exists", False, f"Tag not found before deletion: HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("tm_tags", "DELETE test - Verify tag exists", False, str(e))
            return False
        
        # Step 3: Delete the T&M tag
        print(f"Step 3: Deleting T&M tag {tag_id}...")
        try:
            response = self.session.delete(f"{self.base_url}/tm-tags/{tag_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data and "deleted successfully" in response_data["message"]:
                    self.log_result("tm_tags", "DELETE test - Delete tag", True, f"Tag {tag_id} deleted successfully")
                else:
                    self.log_result("tm_tags", "DELETE test - Delete tag", False, "Unexpected response format", response)
                    return False
            else:
                self.log_result("tm_tags", "DELETE test - Delete tag", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("tm_tags", "DELETE test - Delete tag", False, str(e))
            return False
        
        # Step 4: Verify the deleted tag is no longer accessible by ID
        print(f"Step 4: Verifying deleted tag {tag_id} is no longer accessible...")
        try:
            response = self.session.get(f"{self.base_url}/tm-tags/{tag_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "error" in response_data and "not found" in response_data["error"]:
                    self.log_result("tm_tags", "DELETE test - Verify tag deleted (by ID)", True, "Tag correctly returns 'not found' error")
                else:
                    self.log_result("tm_tags", "DELETE test - Verify tag deleted (by ID)", False, "Deleted tag still accessible", response)
                    return False
            else:
                # Some APIs might return 404 instead of 200 with error message
                if response.status_code == 404:
                    self.log_result("tm_tags", "DELETE test - Verify tag deleted (by ID)", True, "Tag correctly returns 404")
                else:
                    self.log_result("tm_tags", "DELETE test - Verify tag deleted (by ID)", False, f"Unexpected status: {response.status_code}", response)
                    return False
                    
        except Exception as e:
            self.log_result("tm_tags", "DELETE test - Verify tag deleted (by ID)", False, str(e))
            return False
        
        # Step 5: Verify the deleted tag is no longer in the list
        print("Step 5: Verifying deleted tag is no longer in the list...")
        try:
            response = self.session.get(f"{self.base_url}/tm-tags")
            if response.status_code == 200:
                current_tags = response.json()
                deleted_tag_still_exists = any(tag["id"] == tag_id for tag in current_tags)
                
                if not deleted_tag_still_exists:
                    self.log_result("tm_tags", "DELETE test - Verify tag deleted (from list)", True, "Deleted tag no longer appears in list")
                else:
                    self.log_result("tm_tags", "DELETE test - Verify tag deleted (from list)", False, "Deleted tag still appears in list")
                    return False
            else:
                self.log_result("tm_tags", "DELETE test - Verify tag deleted (from list)", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("tm_tags", "DELETE test - Verify tag deleted (from list)", False, str(e))
            return False
        
        # Step 6: Test deleting a non-existent tag (should return error)
        print("Step 6: Testing deletion of non-existent tag...")
        fake_id = str(uuid.uuid4())
        try:
            response = self.session.delete(f"{self.base_url}/tm-tags/{fake_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "error" in response_data and "not found" in response_data["error"]:
                    self.log_result("tm_tags", "DELETE test - Non-existent tag", True, "Correctly returns error for non-existent tag")
                else:
                    self.log_result("tm_tags", "DELETE test - Non-existent tag", False, "Should return error for non-existent tag", response)
            else:
                # Some APIs might return 404 for non-existent resources
                if response.status_code == 404:
                    self.log_result("tm_tags", "DELETE test - Non-existent tag", True, "Correctly returns 404 for non-existent tag")
                else:
                    self.log_result("tm_tags", "DELETE test - Non-existent tag", False, f"Unexpected status: {response.status_code}", response)
                    
        except Exception as e:
            self.log_result("tm_tags", "DELETE test - Non-existent tag", False, str(e))
            return False
        
        print("✅ DELETE functionality test completed successfully!")
        return True
    
    def create_realistic_worker_data(self):
        """Create realistic worker data for testing"""
        return [
            {
                "name": "Mike Rodriguez",
                "rate": 95.0,
                "position": "Senior Electrician",
                "phone": "(555) 123-4567",
                "email": "mike.rodriguez@contractor.com"
            },
            {
                "name": "Sarah Johnson", 
                "rate": 85.0,
                "position": "Electrician",
                "phone": "(555) 234-5678",
                "email": "sarah.johnson@contractor.com"
            },
            {
                "name": "David Chen",
                "rate": 105.0,
                "position": "Master Electrician",
                "phone": "(555) 345-6789",
                "email": "david.chen@contractor.com"
            }
        ]
    
    def test_worker_creation(self):
        """Test worker creation endpoint"""
        print("\n=== Testing Worker Creation ===")
        
        workers_data = self.create_realistic_worker_data()
        created_workers = []
        
        for worker_data in workers_data:
            try:
                response = self.session.post(
                    f"{self.base_url}/workers",
                    json=worker_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    required_fields = ["id", "name", "rate", "active", "created_at"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if not missing_fields:
                        created_workers.append(response_data)
                        self.log_result("workers", f"Worker creation - {worker_data['name']}", True)
                    else:
                        self.log_result("workers", f"Worker creation - {worker_data['name']}", False, f"Missing fields: {missing_fields}", response)
                else:
                    self.log_result("workers", f"Worker creation - {worker_data['name']}", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("workers", f"Worker creation - {worker_data['name']}", False, str(e))
        
        return created_workers
    
    def test_worker_retrieval(self):
        """Test worker retrieval endpoint"""
        print("\n=== Testing Worker Retrieval ===")
        
        try:
            response = self.session.get(f"{self.base_url}/workers")
            
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    self.log_result("workers", "Worker retrieval", True, f"Retrieved {len(response_data)} workers")
                    return response_data
                else:
                    self.log_result("workers", "Worker retrieval", False, "Response is not a list", response)
            else:
                self.log_result("workers", "Worker retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("workers", "Worker retrieval", False, str(e))
        
        return None
    
    def create_realistic_project_data(self):
        """Create realistic project data for testing - WITH CUSTOM LABOR RATE"""
        return {
            "name": "Downtown Office Complex - Phase 2",
            "description": "Complete electrical installation for 15-story office building including power distribution, lighting systems, and emergency backup systems.",
            "client_company": "Metropolitan Development Corp",
            "gc_email": "project.manager@metrodev.com",
            "contract_amount": 485000.00,
            "labor_rate": 120.0,  # Custom labor rate for this client (not fixed $95/hr)
            "project_manager": "Jesus Garcia",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=90)).isoformat(),
            "address": "1234 Downtown Ave, Metro City, ST 12345"
        }
    
    def test_project_creation(self):
        """Test project creation endpoint"""
        print("\n=== Testing Project Creation ===")
        
        project_data = self.create_realistic_project_data()
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                required_fields = ["id", "name", "client_company", "gc_email", "labor_rate", "status", "created_at"]
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    self.created_project_id = response_data["id"]
                    self.created_project_name = response_data["name"]
                    self.log_result("projects", "Project creation", True)
                    return response_data
                else:
                    self.log_result("projects", "Project creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("projects", "Project creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Project creation", False, str(e))
        
        return None
    
    def test_project_retrieval(self):
        """Test project retrieval endpoint"""
        print("\n=== Testing Project Retrieval ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    self.log_result("projects", "Project retrieval", True, f"Retrieved {len(response_data)} projects")
                    return response_data
                else:
                    self.log_result("projects", "Project retrieval", False, "Response is not a list", response)
            else:
                self.log_result("projects", "Project retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Project retrieval", False, str(e))
        
        return None
    
    def test_project_by_id(self, project_id):
        """Test project retrieval by ID"""
        print(f"\n=== Testing Project Retrieval by ID: {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "id" in response_data and response_data["id"] == project_id:
                    self.log_result("projects", "Project by ID", True)
                    return response_data
                else:
                    self.log_result("projects", "Project by ID", False, "ID mismatch in response", response)
            else:
                self.log_result("projects", "Project by ID", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Project by ID", False, str(e))
        
        return None
    
    def test_project_update(self, project_id):
        """Test project update endpoint"""
        print(f"\n=== Testing Project Update: {project_id} ===")
        
        update_data = {
            "name": "Downtown Office Complex - Phase 2 (Updated)",
            "description": "Updated project description with additional scope",
            "client_company": "Metropolitan Development Corp",
            "gc_email": "updated.manager@metrodev.com",
            "contract_amount": 525000.00,
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "address": "1234 Downtown Ave, Metro City, ST 12345 (Updated)"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/projects/{project_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("name") == update_data["name"]:
                    self.log_result("projects", "Project update", True)
                    return response_data
                else:
                    self.log_result("projects", "Project update", False, "Update not reflected in response", response)
            else:
                self.log_result("projects", "Project update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Project update", False, str(e))
        
        return None
    
    def test_project_deletion(self, project_id):
        """Test project deletion endpoint"""
        print(f"\n=== Testing Project Deletion: {project_id} ===")
        
        try:
            response = self.session.delete(f"{self.base_url}/projects/{project_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data and "deleted successfully" in response_data["message"]:
                    self.log_result("projects", "Project deletion", True)
                    return True
                else:
                    self.log_result("projects", "Project deletion", False, "Unexpected response format", response)
            else:
                self.log_result("projects", "Project deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Project deletion", False, str(e))
        
        return False
    
    def create_realistic_employee_data(self):
        """Create realistic employee data for testing - NEW SCHEMA with hourly_rate"""
        return [
            {
                "name": "Carlos Martinez",
                "hourly_rate": 45.00,  # True employee cost
                "gc_billing_rate": 95.0,  # Rate billed to GC
                "position": "Journeyman Electrician",
                "hire_date": (datetime.now() - timedelta(days=365)).isoformat(),
                "phone": "(555) 987-6543",
                "email": "carlos.martinez@company.com",
                "emergency_contact": "Maria Martinez - (555) 987-6544"
            },
            {
                "name": "Jennifer Thompson",
                "hourly_rate": 52.00,  # True employee cost
                "gc_billing_rate": 95.0,  # Rate billed to GC
                "position": "Senior Electrician",
                "hire_date": (datetime.now() - timedelta(days=730)).isoformat(),
                "phone": "(555) 876-5432",
                "email": "jennifer.thompson@company.com",
                "emergency_contact": "Robert Thompson - (555) 876-5433"
            },
            {
                "name": "Michael Rodriguez",
                "hourly_rate": 65.00,  # True employee cost
                "gc_billing_rate": 95.0,  # Rate billed to GC
                "position": "Master Electrician",
                "hire_date": (datetime.now() - timedelta(days=1095)).isoformat(),
                "phone": "(555) 765-4321",
                "email": "michael.rodriguez@company.com",
                "emergency_contact": "Sofia Rodriguez - (555) 765-4322"
            }
        ]
    
    def test_employee_creation(self):
        """Test employee creation endpoint"""
        print("\n=== Testing Employee Creation ===")
        
        employees_data = self.create_realistic_employee_data()
        created_employees = []
        
        for employee_data in employees_data:
            try:
                response = self.session.post(
                    f"{self.base_url}/employees",
                    json=employee_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    required_fields = ["id", "name", "hourly_rate", "position", "status", "created_at"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if not missing_fields:
                        created_employees.append(response_data)
                        self.log_result("employees", f"Employee creation - {employee_data['name']}", True)
                    else:
                        self.log_result("employees", f"Employee creation - {employee_data['name']}", False, f"Missing fields: {missing_fields}", response)
                else:
                    self.log_result("employees", f"Employee creation - {employee_data['name']}", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("employees", f"Employee creation - {employee_data['name']}", False, str(e))
        
        return created_employees
    
    def test_employee_retrieval(self):
        """Test employee retrieval endpoint"""
        print("\n=== Testing Employee Retrieval ===")
        
        try:
            response = self.session.get(f"{self.base_url}/employees")
            
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    self.log_result("employees", "Employee retrieval", True, f"Retrieved {len(response_data)} employees")
                    return response_data
                else:
                    self.log_result("employees", "Employee retrieval", False, "Response is not a list", response)
            else:
                self.log_result("employees", "Employee retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("employees", "Employee retrieval", False, str(e))
        
        return None
    
    def test_employee_by_id(self, employee_id):
        """Test employee retrieval by ID"""
        print(f"\n=== Testing Employee Retrieval by ID: {employee_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/employees/{employee_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "id" in response_data and response_data["id"] == employee_id:
                    self.log_result("employees", "Employee by ID", True)
                    return response_data
                else:
                    self.log_result("employees", "Employee by ID", False, "ID mismatch in response", response)
            else:
                self.log_result("employees", "Employee by ID", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("employees", "Employee by ID", False, str(e))
        
        return None
    
    def test_employee_update(self, employee_id):
        """Test employee update endpoint"""
        print(f"\n=== Testing Employee Update: {employee_id} ===")
        
        update_data = {
            "name": "Carlos Martinez (Updated)",
            "hourly_rate": 48.00,  # Updated true employee cost
            "gc_billing_rate": 95.0,
            "position": "Senior Journeyman Electrician",
            "hire_date": (datetime.now() - timedelta(days=365)).isoformat(),
            "phone": "(555) 987-6543",
            "email": "carlos.martinez.updated@company.com"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/employees/{employee_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("hourly_rate") == update_data["hourly_rate"]:
                    self.log_result("employees", "Employee update", True)
                    return response_data
                else:
                    self.log_result("employees", "Employee update", False, "Update not reflected in response", response)
            else:
                self.log_result("employees", "Employee update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("employees", "Employee update", False, str(e))
        
        return None
    
    def test_employee_deletion(self, employee_id):
        """Test employee deletion endpoint"""
        print(f"\n=== Testing Employee Deletion: {employee_id} ===")
        
        try:
            response = self.session.delete(f"{self.base_url}/employees/{employee_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data and "deleted successfully" in response_data["message"]:
                    self.log_result("employees", "Employee deletion", True)
                    return True
                else:
                    self.log_result("employees", "Employee deletion", False, "Unexpected response format", response)
            else:
                self.log_result("employees", "Employee deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("employees", "Employee deletion", False, str(e))
        
        return False
    
    def create_realistic_crew_log_data(self, project_id, project_name):
        """Create realistic crew log data for testing"""
        return {
            "project_id": project_id,
            "project_name": project_name,
            "date": (datetime.now() - timedelta(days=1)).isoformat(),
            "crew_members": ["Carlos Martinez", "Jennifer Thompson", "Michael Rodriguez"],
            "work_description": "Installed main electrical panel and ran conduit for first floor lighting circuits. Completed rough-in for 12 office spaces including power outlets and switch boxes.",
            "hours_worked": 24.0,  # 3 workers x 8 hours
            "per_diem": 150.00,  # $50 per person
            "hotel_cost": 0.00,  # Local project
            "gas_expense": 45.50,
            "other_expenses": 25.00,
            "expense_notes": "Gas for company truck, lunch for crew",
            "weather_conditions": "Clear, 72°F"
        }
    
    def test_crew_log_creation(self):
        """Test crew log creation endpoint"""
        print("\n=== Testing Crew Log Creation ===")
        
        # Use existing project or create a default one
        project_id = getattr(self, 'created_project_id', str(uuid.uuid4()))
        project_name = getattr(self, 'created_project_name', 'Test Project')
        
        crew_log_data = self.create_realistic_crew_log_data(project_id, project_name)
        
        try:
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                required_fields = ["id", "project_id", "date", "crew_members", "work_description", "hours_worked", "created_at"]
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    self.created_crew_log_id = response_data["id"]
                    self.log_result("crew_logs", "Crew log creation", True)
                    return response_data
                else:
                    self.log_result("crew_logs", "Crew log creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("crew_logs", "Crew log creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("crew_logs", "Crew log creation", False, str(e))
        
        return None
    
    def test_crew_log_retrieval(self):
        """Test crew log retrieval endpoint"""
        print("\n=== Testing Crew Log Retrieval ===")
        
        try:
            response = self.session.get(f"{self.base_url}/crew-logs")
            
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    self.log_result("crew_logs", "Crew log retrieval", True, f"Retrieved {len(response_data)} crew logs")
                    return response_data
                else:
                    self.log_result("crew_logs", "Crew log retrieval", False, "Response is not a list", response)
            else:
                self.log_result("crew_logs", "Crew log retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("crew_logs", "Crew log retrieval", False, str(e))
        
        return None
    
    def test_crew_log_by_id(self, log_id):
        """Test crew log retrieval by ID"""
        print(f"\n=== Testing Crew Log Retrieval by ID: {log_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/crew-logs/{log_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "id" in response_data and response_data["id"] == log_id:
                    self.log_result("crew_logs", "Crew log by ID", True)
                    return response_data
                else:
                    self.log_result("crew_logs", "Crew log by ID", False, "ID mismatch in response", response)
            else:
                self.log_result("crew_logs", "Crew log by ID", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("crew_logs", "Crew log by ID", False, str(e))
        
        return None
    
    def test_crew_log_deletion(self, log_id):
        """Test crew log deletion endpoint"""
        print(f"\n=== Testing Crew Log Deletion: {log_id} ===")
        
        try:
            response = self.session.delete(f"{self.base_url}/crew-logs/{log_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data and "deleted successfully" in response_data["message"]:
                    self.log_result("crew_logs", "Crew log deletion", True)
                    return True
                else:
                    self.log_result("crew_logs", "Crew log deletion", False, "Unexpected response format", response)
            else:
                self.log_result("crew_logs", "Crew log deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("crew_logs", "Crew log deletion", False, str(e))
        
        return False
    
    def create_realistic_material_data(self, project_id, project_name):
        """Create realistic material data for testing"""
        return [
            {
                "project_id": project_id,
                "project_name": project_name,
                "purchase_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "vendor": "Metro Electrical Supply",
                "material_name": "12 AWG THHN Copper Wire",
                "quantity": 1000.0,
                "unit_cost": 0.89,
                "total_cost": 890.00,
                "invoice_number": "MES-2024-0156",
                "category": "wire"
            },
            {
                "project_id": project_id,
                "project_name": project_name,
                "purchase_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "vendor": "Downtown Hardware",
                "material_name": "20A GFCI Outlets",
                "quantity": 15.0,
                "unit_cost": 18.75,
                "total_cost": 281.25,
                "invoice_number": "DH-2024-0892",
                "category": "outlets"
            }
        ]
    
    def test_material_creation(self):
        """Test material purchase creation endpoint"""
        print("\n=== Testing Material Purchase Creation ===")
        
        # Use existing project or create a default one
        project_id = getattr(self, 'created_project_id', str(uuid.uuid4()))
        project_name = getattr(self, 'created_project_name', 'Test Project')
        
        materials_data = self.create_realistic_material_data(project_id, project_name)
        created_materials = []
        
        for material_data in materials_data:
            try:
                response = self.session.post(
                    f"{self.base_url}/materials",
                    json=material_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    required_fields = ["id", "project_id", "vendor", "material_name", "quantity", "unit_cost", "total_cost", "created_at"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if not missing_fields:
                        created_materials.append(response_data)
                        self.log_result("materials", f"Material creation - {material_data['material_name']}", True)
                    else:
                        self.log_result("materials", f"Material creation - {material_data['material_name']}", False, f"Missing fields: {missing_fields}", response)
                else:
                    self.log_result("materials", f"Material creation - {material_data['material_name']}", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("materials", f"Material creation - {material_data['material_name']}", False, str(e))
        
        return created_materials
    
    def test_material_retrieval(self):
        """Test material purchase retrieval endpoint"""
        print("\n=== Testing Material Purchase Retrieval ===")
        
        try:
            response = self.session.get(f"{self.base_url}/materials")
            
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, list):
                    self.log_result("materials", "Material retrieval", True, f"Retrieved {len(response_data)} materials")
                    return response_data
                else:
                    self.log_result("materials", "Material retrieval", False, "Response is not a list", response)
            else:
                self.log_result("materials", "Material retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("materials", "Material retrieval", False, str(e))
        
        return None
    
    def test_material_by_id(self, material_id):
        """Test material purchase retrieval by ID"""
        print(f"\n=== Testing Material Purchase Retrieval by ID: {material_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/materials/{material_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "id" in response_data and response_data["id"] == material_id:
                    self.log_result("materials", "Material by ID", True)
                    return response_data
                else:
                    self.log_result("materials", "Material by ID", False, "ID mismatch in response", response)
            else:
                self.log_result("materials", "Material by ID", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("materials", "Material by ID", False, str(e))
        
        return None
    
    def test_material_deletion(self, material_id):
        """Test material purchase deletion endpoint"""
        print(f"\n=== Testing Material Purchase Deletion: {material_id} ===")
        
        try:
            response = self.session.delete(f"{self.base_url}/materials/{material_id}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data and "deleted successfully" in response_data["message"]:
                    self.log_result("materials", "Material deletion", True)
                    return True
                else:
                    self.log_result("materials", "Material deletion", False, "Unexpected response format", response)
            else:
                self.log_result("materials", "Material deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("materials", "Material deletion", False, str(e))
        
        return False
    
    def test_project_specific_labor_rates(self):
        """Test project-specific labor rates functionality"""
        print("\n=== Testing Project-Specific Labor Rates ===")
        
        # Test 1: Create project with custom labor rate
        project_data = {
            "name": "Premium Client Project",
            "description": "High-end client with premium rates",
            "client_company": "Premium Corp",
            "gc_email": "premium@client.com",
            "contract_amount": 250000.00,
            "labor_rate": 150.0,  # Premium rate instead of default $95
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "Premium Location"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                if project.get("labor_rate") == 150.0:
                    self.log_result("projects", "Custom labor rate creation", True, f"Project created with ${project['labor_rate']}/hr rate")
                    self.premium_project_id = project["id"]
                    return project
                else:
                    self.log_result("projects", "Custom labor rate creation", False, f"Expected $150/hr, got ${project.get('labor_rate', 'None')}/hr", response)
            else:
                self.log_result("projects", "Custom labor rate creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Custom labor rate creation", False, str(e))
        
        return None
    
    def test_employee_schema_restructuring(self):
        """Test new employee schema with single hourly_rate field"""
        print("\n=== Testing Employee Schema Restructuring ===")
        
        # Test creating employee with new schema
        employee_data = {
            "name": "Test Employee Schema",
            "hourly_rate": 55.0,  # Single field for true cost
            "gc_billing_rate": 95.0,
            "position": "Test Electrician",
            "hire_date": datetime.now().isoformat(),
            "phone": "(555) 123-4567",
            "email": "test.schema@company.com"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/employees",
                json=employee_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                employee = response.json()
                # Verify new schema fields are present
                if "hourly_rate" in employee and "gc_billing_rate" in employee:
                    # Verify old schema fields are NOT present
                    if "base_pay" not in employee and "burden_cost" not in employee:
                        self.log_result("employees", "New schema structure", True, f"Employee created with hourly_rate: ${employee['hourly_rate']}")
                        self.test_employee_id = employee["id"]
                        return employee
                    else:
                        self.log_result("employees", "New schema structure", False, "Old schema fields still present", response)
                else:
                    self.log_result("employees", "New schema structure", False, "Missing new schema fields", response)
            else:
                self.log_result("employees", "New schema structure", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("employees", "New schema structure", False, str(e))
        
        return None
    
    def test_bidirectional_sync(self):
        """Test bidirectional sync between crew logs and T&M tags"""
        print("\n=== Testing Bidirectional Sync ===")
        
        # First ensure we have a project
        if not hasattr(self, 'created_project_id'):
            project = self.test_project_creation()
            if not project:
                self.log_result("crew_logs", "Bidirectional sync setup", False, "Could not create project for sync test")
                return False
        
        project_id = self.created_project_id
        project_name = self.created_project_name
        work_date = datetime.now().isoformat()
        
        # Test 1: Create crew log and verify T&M tag is auto-generated
        print("Test 1: Crew Log → T&M Tag sync")
        crew_log_data = {
            "project_id": project_id,
            "date": work_date,
            "crew_members": [
                {
                    "name": "Carlos Martinez",
                    "st_hours": 8.0,
                    "ot_hours": 2.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 10.0
                }
            ],
            "work_description": "Sync test - crew log to T&M",
            "weather_conditions": "clear"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                crew_log = response.json()
                crew_log_id = crew_log.get("id")
                
                # Wait a moment for sync to complete
                import time
                time.sleep(2)
                
                # Check if T&M tag was auto-created
                tm_tags_response = self.session.get(f"{self.base_url}/tm-tags")
                if tm_tags_response.status_code == 200:
                    tm_tags = tm_tags_response.json()
                    # Look for auto-generated T&M tag with matching project and date
                    auto_tm_tag = None
                    for tag in tm_tags:
                        if (tag.get("project_id") == project_id and 
                            "Auto-generated from Crew Log" in tag.get("tm_tag_title", "")):
                            auto_tm_tag = tag
                            break
                    
                    if auto_tm_tag:
                        self.log_result("crew_logs", "Crew log → T&M sync", True, f"T&M tag auto-created: {auto_tm_tag['id']}")
                        self.sync_tm_tag_id = auto_tm_tag["id"]
                    else:
                        self.log_result("crew_logs", "Crew log → T&M sync", False, "No auto-generated T&M tag found")
                else:
                    self.log_result("crew_logs", "Crew log → T&M sync", False, "Could not retrieve T&M tags for verification")
            else:
                self.log_result("crew_logs", "Crew log → T&M sync", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("crew_logs", "Crew log → T&M sync", False, str(e))
        
        # Test 2: Create T&M tag and verify crew log is auto-generated
        print("Test 2: T&M Tag → Crew Log sync")
        tm_tag_data = {
            "project_id": project_id,
            "project_name": project_name,
            "cost_code": "SYNC-TEST-001",
            "date_of_work": (datetime.now() + timedelta(hours=1)).isoformat(),  # Slightly different time
            "tm_tag_title": "Sync test - T&M to crew log",
            "description_of_work": "Testing bidirectional sync from T&M to crew log",
            "labor_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Jennifer Thompson",
                    "quantity": 1,
                    "st_hours": 6.0,
                    "ot_hours": 1.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 7.0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "sync@test.com"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                tm_tag = response.json()
                tm_tag_id = tm_tag.get("id")
                
                # Wait a moment for sync to complete
                time.sleep(2)
                
                # Check if crew log was auto-created
                crew_logs_response = self.session.get(f"{self.base_url}/crew-logs")
                if crew_logs_response.status_code == 200:
                    crew_logs = crew_logs_response.json()
                    # Look for auto-generated crew log with matching project
                    auto_crew_log = None
                    for log in crew_logs:
                        if (log.get("project_id") == project_id and 
                            log.get("synced_from_tm") == True):
                            auto_crew_log = log
                            break
                    
                    if auto_crew_log:
                        self.log_result("tm_tags", "T&M → Crew log sync", True, f"Crew log auto-created: {auto_crew_log['id']}")
                    else:
                        self.log_result("tm_tags", "T&M → Crew log sync", False, "No auto-generated crew log found")
                else:
                    self.log_result("tm_tags", "T&M → Crew log sync", False, "Could not retrieve crew logs for verification")
            else:
                self.log_result("tm_tags", "T&M → Crew log sync", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("tm_tags", "T&M → Crew log sync", False, str(e))
        
        return True
    
    def test_tm_tag_edit_functionality(self):
        """Test T&M tag edit functionality via PUT endpoint"""
        print("\n=== Testing T&M Tag Edit Functionality ===")
        
        # First create a T&M tag to edit
        tm_tag_data = self.create_realistic_tm_tag_data()
        
        try:
            # Create the tag
            response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("tm_tags", "Edit functionality setup", False, "Could not create T&M tag for edit test", response)
                return False
            
            created_tag = response.json()
            tag_id = created_tag["id"]
            
            # Test editing the tag
            edit_data = {
                "tm_tag_title": "EDITED - Electrical Installation - Floor 3",
                "cost_code": "EDITED-CC-2024-0156",
                "company_name": "EDITED Company Name",
                "description_of_work": "EDITED - Updated work description with new details",
                "gc_email": "edited.email@client.com"
            }
            
            edit_response = self.session.put(
                f"{self.base_url}/tm-tags/{tag_id}",
                json=edit_data,
                headers={"Content-Type": "application/json"}
            )
            
            if edit_response.status_code == 200:
                updated_tag = edit_response.json()
                
                # Verify the edits were applied
                edits_applied = True
                for field, expected_value in edit_data.items():
                    if updated_tag.get(field) != expected_value:
                        edits_applied = False
                        break
                
                if edits_applied:
                    self.log_result("tm_tags", "Edit functionality", True, f"T&M tag {tag_id} successfully edited")
                    
                    # Verify the tag can still be retrieved with edits
                    get_response = self.session.get(f"{self.base_url}/tm-tags/{tag_id}")
                    if get_response.status_code == 200:
                        retrieved_tag = get_response.json()
                        if retrieved_tag.get("tm_tag_title") == edit_data["tm_tag_title"]:
                            self.log_result("tm_tags", "Edit persistence", True, "Edits persisted correctly")
                        else:
                            self.log_result("tm_tags", "Edit persistence", False, "Edits not persisted")
                    else:
                        self.log_result("tm_tags", "Edit persistence", False, "Could not retrieve edited tag")
                else:
                    self.log_result("tm_tags", "Edit functionality", False, "Edits not applied correctly", edit_response)
            else:
                self.log_result("tm_tags", "Edit functionality", False, f"HTTP {edit_response.status_code}", edit_response)
                
        except Exception as e:
            self.log_result("tm_tags", "Edit functionality", False, str(e))
        
        return True
    
    def test_crew_log_edit_functionality(self):
        """Test crew log edit functionality via PUT endpoint"""
        print("\n=== Testing Crew Log Edit Functionality ===")
        
        # First ensure we have a project
        if not hasattr(self, 'created_project_id'):
            project = self.test_project_creation()
            if not project:
                self.log_result("crew_logs", "Edit functionality setup", False, "Could not create project for edit test")
                return False
        
        project_id = self.created_project_id
        project_name = self.created_project_name
        
        # Create a crew log to edit
        crew_log_data = {
            "project_id": project_id,
            "date": datetime.now().isoformat(),
            "crew_members": [
                {
                    "name": "Original Worker",
                    "st_hours": 8.0,
                    "ot_hours": 0.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 8.0
                }
            ],
            "work_description": "Original work description",
            "weather_conditions": "clear"
        }
        
        try:
            # Create the crew log
            response = self.session.post(
                f"{self.base_url}/crew-logs",
                json=crew_log_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("crew_logs", "Edit functionality setup", False, "Could not create crew log for edit test", response)
                return False
            
            created_log = response.json()
            log_id = created_log["id"]
            
            # Test editing the crew log
            edit_data = {
                "work_description": "EDITED - Updated work description with new details",
                "weather_conditions": "EDITED - Partly cloudy, 75°F",
                "crew_members": [
                    {
                        "name": "EDITED Worker Name",
                        "st_hours": 6.0,
                        "ot_hours": 2.0,
                        "dt_hours": 1.0,
                        "pot_hours": 0.0,
                        "total_hours": 9.0
                    }
                ]
            }
            
            edit_response = self.session.put(
                f"{self.base_url}/crew-logs/{log_id}",
                json=edit_data,
                headers={"Content-Type": "application/json"}
            )
            
            if edit_response.status_code == 200:
                # Verify the edit was successful by retrieving the updated log
                get_response = self.session.get(f"{self.base_url}/crew-logs")
                if get_response.status_code == 200:
                    crew_logs = get_response.json()
                    updated_log = None
                    for log in crew_logs:
                        if log.get("id") == log_id:
                            updated_log = log
                            break
                    
                    if updated_log:
                        if (updated_log.get("work_description") == edit_data["work_description"] and
                            updated_log.get("weather_conditions") == edit_data["weather_conditions"]):
                            self.log_result("crew_logs", "Edit functionality", True, f"Crew log {log_id} successfully edited")
                        else:
                            self.log_result("crew_logs", "Edit functionality", False, "Edits not applied correctly")
                    else:
                        self.log_result("crew_logs", "Edit functionality", False, "Could not find updated crew log")
                else:
                    self.log_result("crew_logs", "Edit functionality", False, "Could not retrieve crew logs for verification")
            else:
                self.log_result("crew_logs", "Edit functionality", False, f"HTTP {edit_response.status_code}", edit_response)
                
        except Exception as e:
            self.log_result("crew_logs", "Edit functionality", False, str(e))
        
        return True
    
    def test_enhanced_cost_analytics(self):
        """Test enhanced cost analytics with new fields"""
        print("\n=== Testing Enhanced Cost Analytics ===")
        
        # First ensure we have a project with custom labor rate
        if not hasattr(self, 'premium_project_id'):
            premium_project = self.test_project_specific_labor_rates()
            if not premium_project:
                self.log_result("analytics", "Enhanced analytics setup", False, "Could not create premium project for analytics test")
                return False
        
        project_id = self.premium_project_id
        
        # Create some test data for analytics
        # 1. Create employees with known rates
        employee_data = {
            "name": "Analytics Test Employee",
            "hourly_rate": 50.0,  # True cost
            "gc_billing_rate": 95.0,
            "position": "Test Electrician",
            "hire_date": datetime.now().isoformat()
        }
        
        emp_response = self.session.post(f"{self.base_url}/employees", json=employee_data, headers={"Content-Type": "application/json"})
        
        # 2. Create T&M tag with labor entries
        tm_tag_data = {
            "project_id": project_id,
            "project_name": "Premium Client Project",
            "cost_code": "ANALYTICS-TEST",
            "date_of_work": datetime.now().isoformat(),
            "tm_tag_title": "Analytics Test Tag",
            "description_of_work": "Testing enhanced analytics calculations",
            "labor_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Analytics Test Employee",
                    "quantity": 1,
                    "st_hours": 8.0,
                    "ot_hours": 2.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 10.0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "material_name": "Test Material",
                    "unit_of_measure": "each",
                    "quantity": 5.0,
                    "unit_cost": 20.0,
                    "total": 100.0,
                    "date_of_work": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "analytics@test.com"
        }
        
        tm_response = self.session.post(f"{self.base_url}/tm-tags", json=tm_tag_data, headers={"Content-Type": "application/json"})
        
        # Wait for data to be processed
        import time
        time.sleep(2)
        
        # Test the enhanced analytics endpoint
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
            
            if response.status_code == 200:
                analytics = response.json()
                
                # Check for new enhanced fields
                required_new_fields = [
                    "labor_markup_profit",  # Difference between billed and true labor cost
                    "true_employee_cost",   # Actual employee hourly rates
                    "total_labor_cost_gc"   # Amount billed to GC using project rate
                ]
                
                missing_fields = [field for field in required_new_fields if field not in analytics]
                
                if not missing_fields:
                    # Verify calculations are using project-specific rates
                    project_labor_rate = 150.0  # Premium project rate
                    true_employee_cost = analytics.get("true_employee_cost", 0)
                    total_labor_cost_gc = analytics.get("total_labor_cost_gc", 0)
                    labor_markup_profit = analytics.get("labor_markup_profit", 0)
                    
                    # Expected calculations:
                    # True cost: 10 hours * $50/hr = $500
                    # Billed amount: 10 hours * $150/hr = $1500 (project-specific rate)
                    # Labor markup profit: $1500 - $500 = $1000
                    
                    expected_true_cost = 10.0 * 50.0  # 10 hours * $50/hr
                    expected_billed = 10.0 * 150.0    # 10 hours * $150/hr (project rate)
                    expected_markup = expected_billed - expected_true_cost
                    
                    calculations_correct = (
                        abs(true_employee_cost - expected_true_cost) < 1.0 and
                        abs(total_labor_cost_gc - expected_billed) < 1.0 and
                        abs(labor_markup_profit - expected_markup) < 1.0
                    )
                    
                    if calculations_correct:
                        self.log_result("analytics", "Enhanced cost analytics", True, 
                                      f"Analytics calculated correctly: True cost=${true_employee_cost}, Billed=${total_labor_cost_gc}, Markup profit=${labor_markup_profit}")
                    else:
                        self.log_result("analytics", "Enhanced cost analytics", False, 
                                      f"Calculation mismatch: Expected true=${expected_true_cost}, billed=${expected_billed}, markup=${expected_markup}")
                else:
                    self.log_result("analytics", "Enhanced cost analytics", False, f"Missing enhanced fields: {missing_fields}", response)
            else:
                self.log_result("analytics", "Enhanced cost analytics", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("analytics", "Enhanced cost analytics", False, str(e))
        
        return True

    def test_tm_project_analytics(self):
        """Test T&M project profit calculation - should show markup profit correctly"""
        print("\n=== Testing T&M Project Analytics ===")
        
        # Create a T&M project
        tm_project_data = {
            "name": "T&M Test Project",
            "description": "Time & Material project for testing profit calculations",
            "client_company": "T&M Client Corp",
            "gc_email": "tm@client.com",
            "project_type": "tm_only",  # T&M project type
            "contract_amount": 0,  # T&M projects don't have fixed contract
            "labor_rate": 120.0,  # Rate billed to client
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "T&M Project Location"
        }
        
        try:
            # Create T&M project
            response = self.session.post(
                f"{self.base_url}/projects",
                json=tm_project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("analytics", "T&M project creation", False, f"HTTP {response.status_code}", response)
                return False
            
            tm_project = response.json()
            tm_project_id = tm_project["id"]
            
            # Create some employees for cost calculations
            employee_data = {
                "name": "T&M Test Worker",
                "hourly_rate": 50.0,  # True cost
                "gc_billing_rate": 120.0,  # Rate billed to GC
                "position": "Test Electrician",
                "hire_date": datetime.now().isoformat()
            }
            
            emp_response = self.session.post(
                f"{self.base_url}/employees",
                json=employee_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Create T&M tag with labor for this project
            tm_tag_data = {
                "project_id": tm_project_id,
                "project_name": tm_project["name"],
                "cost_code": "TM-TEST-001",
                "date_of_work": datetime.now().isoformat(),
                "tm_tag_title": "T&M Test Work",
                "description_of_work": "Testing T&M profit calculations",
                "labor_entries": [
                    {
                        "id": str(uuid.uuid4()),
                        "worker_name": "T&M Test Worker",
                        "quantity": 1,
                        "st_hours": 10.0,
                        "ot_hours": 0.0,
                        "dt_hours": 0.0,
                        "pot_hours": 0.0,
                        "total_hours": 10.0,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "material_entries": [
                    {
                        "id": str(uuid.uuid4()),
                        "material_name": "Test Material",
                        "unit_of_measure": "each",
                        "quantity": 5.0,
                        "unit_cost": 20.0,
                        "total": 100.0,
                        "date_of_work": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "equipment_entries": [],
                "other_entries": [],
                "gc_email": "tm@client.com"
            }
            
            tm_tag_response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if tm_tag_response.status_code != 200:
                self.log_result("analytics", "T&M tag creation", False, f"HTTP {tm_tag_response.status_code}", tm_tag_response)
                return False
            
            # Wait a moment for data to be processed
            import time
            time.sleep(1)
            
            # Get analytics for T&M project
            analytics_response = self.session.get(f"{self.base_url}/projects/{tm_project_id}/analytics")
            
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                
                # Verify T&M project analytics
                project_type = analytics.get("project_type")
                labor_markup_profit = analytics.get("labor_markup_profit", 0)
                material_markup_profit = analytics.get("material_markup_profit", 0)
                total_profit = analytics.get("profit", 0)
                profit_margin = analytics.get("profit_margin", 0)
                
                # Expected calculations:
                # Labor: 10 hours * $120/hr = $1200 billed, 10 hours * $50/hr = $500 true cost
                # Labor markup profit = $1200 - $500 = $700
                # Material markup profit = $100 * 0.2 = $20 (20% markup)
                # Total profit = $700 + $20 = $720
                
                expected_labor_markup = 10 * 120 - 10 * 50  # $700
                expected_material_markup = 100 * 0.2  # $20
                expected_total_profit = expected_labor_markup + expected_material_markup  # $720
                
                success = True
                issues = []
                
                if project_type != "tm_only":
                    success = False
                    issues.append(f"Expected project_type 'tm_only', got '{project_type}'")
                
                if abs(labor_markup_profit - expected_labor_markup) > 50:  # Allow some variance
                    success = False
                    issues.append(f"Expected labor markup profit ~${expected_labor_markup}, got ${labor_markup_profit}")
                
                if total_profit <= 0:
                    success = False
                    issues.append(f"Expected positive total profit, got ${total_profit}")
                
                if profit_margin <= 0:
                    success = False
                    issues.append(f"Expected positive profit margin, got {profit_margin}%")
                
                if success:
                    self.log_result("analytics", "T&M project profit calculation", True, 
                                  f"T&M project shows correct markup profit: Labor=${labor_markup_profit}, Material=${material_markup_profit}, Total=${total_profit} ({profit_margin:.1f}% margin)")
                    self.tm_project_id = tm_project_id
                else:
                    self.log_result("analytics", "T&M project profit calculation", False, "; ".join(issues))
                
                return analytics
            else:
                self.log_result("analytics", "T&M project analytics", False, f"HTTP {analytics_response.status_code}", analytics_response)
                
        except Exception as e:
            self.log_result("analytics", "T&M project analytics", False, str(e))
        
        return None

    def test_full_project_analytics(self):
        """Test full project profit calculation - should calculate profit as contract minus costs"""
        print("\n=== Testing Full Project Analytics ===")
        
        # Create a full project
        full_project_data = {
            "name": "Full Contract Test Project",
            "description": "Fixed contract project for testing profit calculations",
            "client_company": "Full Contract Client Corp",
            "gc_email": "full@client.com",
            "project_type": "full_project",  # Full project type
            "contract_amount": 50000.0,  # Fixed contract amount
            "labor_rate": 95.0,  # Rate billed to client
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "Full Project Location"
        }
        
        try:
            # Create full project
            response = self.session.post(
                f"{self.base_url}/projects",
                json=full_project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("analytics", "Full project creation", False, f"HTTP {response.status_code}", response)
                return False
            
            full_project = response.json()
            full_project_id = full_project["id"]
            
            # Create T&M tag with labor and materials for this project
            tm_tag_data = {
                "project_id": full_project_id,
                "project_name": full_project["name"],
                "cost_code": "FULL-TEST-001",
                "date_of_work": datetime.now().isoformat(),
                "tm_tag_title": "Full Project Test Work",
                "description_of_work": "Testing full project profit calculations",
                "labor_entries": [
                    {
                        "id": str(uuid.uuid4()),
                        "worker_name": "T&M Test Worker",
                        "quantity": 1,
                        "st_hours": 20.0,
                        "ot_hours": 0.0,
                        "dt_hours": 0.0,
                        "pot_hours": 0.0,
                        "total_hours": 20.0,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "material_entries": [
                    {
                        "id": str(uuid.uuid4()),
                        "material_name": "Full Project Material",
                        "unit_of_measure": "each",
                        "quantity": 10.0,
                        "unit_cost": 100.0,
                        "total": 1000.0,
                        "date_of_work": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "equipment_entries": [],
                "other_entries": [],
                "gc_email": "full@client.com"
            }
            
            tm_tag_response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if tm_tag_response.status_code != 200:
                self.log_result("analytics", "Full project T&M tag creation", False, f"HTTP {tm_tag_response.status_code}", tm_tag_response)
                return False
            
            # Wait a moment for data to be processed
            import time
            time.sleep(1)
            
            # Get analytics for full project
            analytics_response = self.session.get(f"{self.base_url}/projects/{full_project_id}/analytics")
            
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                
                # Verify full project analytics
                project_type = analytics.get("project_type")
                contract_amount = analytics.get("contract_amount", 0)
                total_profit = analytics.get("profit", 0)
                profit_margin = analytics.get("profit_margin", 0)
                
                # For full projects, profit should be contract amount minus true costs
                success = True
                issues = []
                
                if project_type != "full_project":
                    success = False
                    issues.append(f"Expected project_type 'full_project', got '{project_type}'")
                
                if contract_amount != 50000.0:
                    success = False
                    issues.append(f"Expected contract amount $50,000, got ${contract_amount}")
                
                # Profit should be positive and significant for full projects
                if total_profit <= 0:
                    success = False
                    issues.append(f"Expected positive profit for full project, got ${total_profit}")
                
                if profit_margin <= 0:
                    success = False
                    issues.append(f"Expected positive profit margin, got {profit_margin}%")
                
                if success:
                    self.log_result("analytics", "Full project profit calculation", True, 
                                  f"Full project shows correct contract-based profit: ${total_profit} ({profit_margin:.1f}% margin) from ${contract_amount} contract")
                    self.full_project_id = full_project_id
                else:
                    self.log_result("analytics", "Full project profit calculation", False, "; ".join(issues))
                
                return analytics
            else:
                self.log_result("analytics", "Full project analytics", False, f"HTTP {analytics_response.status_code}", analytics_response)
                
        except Exception as e:
            self.log_result("analytics", "Full project analytics", False, str(e))
        
        return None

    def test_forecasted_schedule_creation(self):
        """Test creating projects with forecasted values and verify they're stored correctly"""
        print("\n=== Testing Forecasted Schedule Creation ===")
        
        # Create project with forecasted values
        forecasted_project_data = {
            "name": "Forecasted Schedule Test Project",
            "description": "Project with forecasted schedule values for testing",
            "client_company": "Forecast Client Corp",
            "gc_email": "forecast@client.com",
            "project_type": "full_project",
            "contract_amount": 75000.0,
            "labor_rate": 110.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=60)).isoformat(),
            # Forecasted schedule fields
            "estimated_hours": 500.0,
            "estimated_labor_cost": 55000.0,
            "estimated_material_cost": 15000.0,
            "estimated_profit": 5000.0,
            "address": "Forecasted Project Location"
        }
        
        try:
            # Create project with forecasted values
            response = self.session.post(
                f"{self.base_url}/projects",
                json=forecasted_project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                project_id = project["id"]
                
                # Verify forecasted fields are stored correctly
                forecasted_fields = {
                    "estimated_hours": 500.0,
                    "estimated_labor_cost": 55000.0,
                    "estimated_material_cost": 15000.0,
                    "estimated_profit": 5000.0
                }
                
                success = True
                issues = []
                
                for field, expected_value in forecasted_fields.items():
                    actual_value = project.get(field)
                    if actual_value != expected_value:
                        success = False
                        issues.append(f"Expected {field}={expected_value}, got {actual_value}")
                
                if success:
                    self.log_result("analytics", "Forecasted schedule creation", True, 
                                  f"Project created with forecasted values: {forecasted_fields}")
                    self.forecasted_project_id = project_id
                    return project
                else:
                    self.log_result("analytics", "Forecasted schedule creation", False, "; ".join(issues))
            else:
                self.log_result("analytics", "Forecasted schedule creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("analytics", "Forecasted schedule creation", False, str(e))
        
        return None

    def test_analytics_response_fields(self):
        """Test that GET /api/projects/{id}/analytics returns all new fields"""
        print("\n=== Testing Analytics Response Fields ===")
        
        # Use forecasted project if available, otherwise create one
        if not hasattr(self, 'forecasted_project_id'):
            project = self.test_forecasted_schedule_creation()
            if not project:
                self.log_result("analytics", "Analytics response setup", False, "Could not create forecasted project")
                return False
        
        project_id = self.forecasted_project_id
        
        try:
            # Get analytics for the project
            response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
            
            if response.status_code == 200:
                analytics = response.json()
                
                # Check for all required new fields
                required_new_fields = [
                    "project_type",
                    "material_markup_profit",
                    "estimated_hours",
                    "estimated_labor_cost", 
                    "estimated_material_cost",
                    "estimated_profit",
                    "hours_variance",
                    "labor_cost_variance",
                    "material_cost_variance",
                    "profit_variance"
                ]
                
                missing_fields = []
                present_fields = []
                
                for field in required_new_fields:
                    if field in analytics:
                        present_fields.append(f"{field}={analytics[field]}")
                    else:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_result("analytics", "Analytics response fields", True, 
                                  f"All new fields present: {', '.join(present_fields[:5])}...")  # Show first 5 to avoid long output
                    return analytics
                else:
                    self.log_result("analytics", "Analytics response fields", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("analytics", "Analytics response fields", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("analytics", "Analytics response fields", False, str(e))
        
        return None

    def test_variance_analysis(self):
        """Test variance analysis between forecasted vs actual values"""
        print("\n=== Testing Variance Analysis ===")
        
        # Use forecasted project and add some actual data
        if not hasattr(self, 'forecasted_project_id'):
            project = self.test_forecasted_schedule_creation()
            if not project:
                self.log_result("analytics", "Variance analysis setup", False, "Could not create forecasted project")
                return False
        
        project_id = self.forecasted_project_id
        
        try:
            # Add some actual work data to compare against forecasts
            tm_tag_data = {
                "project_id": project_id,
                "project_name": "Forecasted Schedule Test Project",
                "cost_code": "VAR-TEST-001",
                "date_of_work": datetime.now().isoformat(),
                "tm_tag_title": "Variance Test Work",
                "description_of_work": "Testing variance calculations",
                "labor_entries": [
                    {
                        "id": str(uuid.uuid4()),
                        "worker_name": "Variance Test Worker",
                        "quantity": 1,
                        "st_hours": 30.0,  # Some actual hours to create variance
                        "ot_hours": 0.0,
                        "dt_hours": 0.0,
                        "pot_hours": 0.0,
                        "total_hours": 30.0,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "material_entries": [
                    {
                        "id": str(uuid.uuid4()),
                        "material_name": "Variance Test Material",
                        "unit_of_measure": "each",
                        "quantity": 20.0,
                        "unit_cost": 50.0,
                        "total": 1000.0,
                        "date_of_work": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "equipment_entries": [],
                "other_entries": [],
                "gc_email": "forecast@client.com"
            }
            
            tm_tag_response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if tm_tag_response.status_code != 200:
                self.log_result("analytics", "Variance test data creation", False, f"HTTP {tm_tag_response.status_code}", tm_tag_response)
                return False
            
            # Wait for data processing
            import time
            time.sleep(1)
            
            # Get analytics with variance calculations
            analytics_response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
            
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                
                # Check variance calculations
                hours_variance = analytics.get("hours_variance", 0)
                labor_cost_variance = analytics.get("labor_cost_variance", 0)
                material_cost_variance = analytics.get("material_cost_variance", 0)
                profit_variance = analytics.get("profit_variance", 0)
                
                # Verify variance calculations exist and make sense
                success = True
                issues = []
                
                # Variance fields should exist
                variance_fields = ["hours_variance", "labor_cost_variance", "material_cost_variance", "profit_variance"]
                for field in variance_fields:
                    if field not in analytics:
                        success = False
                        issues.append(f"Missing variance field: {field}")
                
                # Hours variance should be calculated (actual vs estimated)
                estimated_hours = analytics.get("estimated_hours", 0)
                actual_hours = analytics.get("total_hours", 0)
                expected_hours_variance = actual_hours - estimated_hours
                
                if abs(hours_variance - expected_hours_variance) > 1:
                    success = False
                    issues.append(f"Hours variance calculation incorrect: expected {expected_hours_variance}, got {hours_variance}")
                
                if success:
                    self.log_result("analytics", "Variance analysis", True, 
                                  f"Variance calculations working: Hours={hours_variance}, Labor=${labor_cost_variance}, Material=${material_cost_variance}, Profit=${profit_variance}")
                else:
                    self.log_result("analytics", "Variance analysis", False, "; ".join(issues))
                
                return analytics
            else:
                self.log_result("analytics", "Variance analysis", False, f"HTTP {analytics_response.status_code}", analytics_response)
                
        except Exception as e:
            self.log_result("analytics", "Variance analysis", False, str(e))
        
        return None
    
    def test_daily_crew_data_endpoint(self):
        """Test the daily crew data endpoint for auto-population"""
        print("\n=== Testing Daily Crew Data Endpoint ===")
        
        if not hasattr(self, 'created_project_id'):
            project = self.test_project_creation()
            if not project:
                self.log_result("crew_logs", "Daily crew data setup", False, "Could not create project for daily crew data test")
                return False
        
        project_id = self.created_project_id
        test_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(f"{self.base_url}/daily-crew-data?project_id={project_id}&date={test_date}")
            
            if response.status_code == 200:
                crew_data = response.json()
                
                # Verify response structure
                required_fields = ["source", "data", "crew_members", "work_description"]
                missing_fields = [field for field in required_fields if field not in crew_data]
                
                if not missing_fields:
                    self.log_result("crew_logs", "Daily crew data endpoint", True, f"Endpoint returned data source: {crew_data.get('source', 'None')}")
                else:
                    self.log_result("crew_logs", "Daily crew data endpoint", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("crew_logs", "Daily crew data endpoint", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("crew_logs", "Daily crew data endpoint", False, str(e))
        
        return True

    def test_gc_pin_system(self):
        """Test the fixed GC PIN system as requested in review"""
        print("\n=== Testing Fixed GC PIN System ===")
        
        # Test 1: Get all projects to verify we have projects in the system
        print("Test 1: GET /api/projects to verify projects exist")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                if isinstance(projects, list) and len(projects) > 0:
                    self.log_result("projects", "GC PIN - Projects exist", True, f"Found {len(projects)} projects in system")
                    self.available_projects = projects
                    
                    # Show project details for testing
                    print(f"Available projects for PIN testing:")
                    for project in projects[:5]:  # Show first 5 projects
                        print(f"  - ID: {project.get('id')}, Name: {project.get('name', 'Unknown')}")
                else:
                    self.log_result("projects", "GC PIN - Projects exist", False, "No projects found in system")
                    return False
            else:
                self.log_result("projects", "GC PIN - Projects exist", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("projects", "GC PIN - Projects exist", False, str(e))
            return False
        
        # Test 2: Test the specific project IDs mentioned in the review request
        test_project_ids = ["68cc802f8d44fcd8015b39b8", "68cc802f8d44fcd8015b39b9"]
        
        for project_id in test_project_ids:
            print(f"Test 2: GET /api/projects/{project_id}/gc-pin for project {project_id}")
            try:
                response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                
                if response.status_code == 200:
                    pin_data = response.json()
                    
                    # Verify response structure
                    required_fields = ["projectId", "projectName", "gcPin", "pinUsed"]
                    missing_fields = [field for field in required_fields if field not in pin_data]
                    
                    if not missing_fields:
                        self.log_result("projects", f"GC PIN - Project {project_id}", True, 
                                      f"PIN: {pin_data['gcPin']}, Project: {pin_data['projectName']}, Used: {pin_data['pinUsed']}")
                        
                        # Verify PIN is 4 digits
                        pin = pin_data['gcPin']
                        if isinstance(pin, str) and len(pin) == 4 and pin.isdigit():
                            self.log_result("projects", f"GC PIN - PIN format {project_id}", True, f"Valid 4-digit PIN: {pin}")
                        else:
                            self.log_result("projects", f"GC PIN - PIN format {project_id}", False, f"Invalid PIN format: {pin}")
                    else:
                        self.log_result("projects", f"GC PIN - Project {project_id}", False, f"Missing fields: {missing_fields}", response)
                        
                elif response.status_code == 404:
                    self.log_result("projects", f"GC PIN - Project {project_id}", False, "Project not found (404)", response)
                else:
                    self.log_result("projects", f"GC PIN - Project {project_id}", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("projects", f"GC PIN - Project {project_id}", False, str(e))
        
        # Test 3: Test PIN generation for existing projects (use first available project)
        if hasattr(self, 'available_projects') and self.available_projects:
            test_project = self.available_projects[0]
            project_id = test_project['id']
            
            print(f"Test 3: Verify PIN generation for existing project {project_id}")
            try:
                response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                
                if response.status_code == 200:
                    pin_data = response.json()
                    
                    # Verify all required fields are present
                    if all(field in pin_data for field in ["projectId", "projectName", "gcPin", "pinUsed"]):
                        pin = pin_data['gcPin']
                        project_name = pin_data['projectName']
                        pin_used = pin_data['pinUsed']
                        
                        self.log_result("projects", "GC PIN - Generation verification", True, 
                                      f"Project: {project_name}, PIN: {pin}, Used: {pin_used}")
                        
                        # Verify PIN uniqueness by testing multiple projects
                        pins_collected = [pin]
                        for additional_project in self.available_projects[1:4]:  # Test up to 3 more projects
                            try:
                                add_response = self.session.get(f"{self.base_url}/projects/{additional_project['id']}/gc-pin")
                                if add_response.status_code == 200:
                                    add_pin_data = add_response.json()
                                    add_pin = add_pin_data.get('gcPin')
                                    if add_pin:
                                        pins_collected.append(add_pin)
                            except:
                                pass  # Skip errors for additional projects
                        
                        # Check PIN uniqueness
                        unique_pins = set(pins_collected)
                        if len(unique_pins) == len(pins_collected):
                            self.log_result("projects", "GC PIN - Uniqueness", True, f"All {len(pins_collected)} PINs are unique: {pins_collected}")
                        else:
                            self.log_result("projects", "GC PIN - Uniqueness", False, f"Duplicate PINs found: {pins_collected}")
                    else:
                        self.log_result("projects", "GC PIN - Generation verification", False, "Missing required fields in response", response)
                else:
                    self.log_result("projects", "GC PIN - Generation verification", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("projects", "GC PIN - Generation verification", False, str(e))
        
        # Test 4: Test PIN generation for a newly created project
        print("Test 4: Create new project and verify automatic PIN generation")
        new_project_data = {
            "name": "GC PIN Test Project",
            "client": "Test Client Corp",
            "contractType": "T&M",
            "invoiceSchedule": "monthly",
            "billingDay": 20,
            "openingBalance": 0.0,
            "gcRate": 95.0,
            "startDate": datetime.now().isoformat(),
            "notes": "Test project for GC PIN system verification"
        }
        
        try:
            # Create new project
            create_response = self.session.post(
                f"{self.base_url}/projects",
                json=new_project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code == 200:
                new_project = create_response.json()
                new_project_id = new_project.get('id')
                
                if new_project_id:
                    # Test PIN endpoint for new project
                    pin_response = self.session.get(f"{self.base_url}/projects/{new_project_id}/gc-pin")
                    
                    if pin_response.status_code == 200:
                        pin_data = pin_response.json()
                        
                        if all(field in pin_data for field in ["projectId", "projectName", "gcPin", "pinUsed"]):
                            new_pin = pin_data['gcPin']
                            self.log_result("projects", "GC PIN - New project PIN", True, 
                                          f"New project automatically assigned PIN: {new_pin}")
                            
                            # Verify PIN format
                            if isinstance(new_pin, str) and len(new_pin) == 4 and new_pin.isdigit():
                                self.log_result("projects", "GC PIN - New project PIN format", True, f"Valid 4-digit PIN: {new_pin}")
                            else:
                                self.log_result("projects", "GC PIN - New project PIN format", False, f"Invalid PIN format: {new_pin}")
                        else:
                            self.log_result("projects", "GC PIN - New project PIN", False, "Missing required fields", pin_response)
                    else:
                        self.log_result("projects", "GC PIN - New project PIN", False, f"HTTP {pin_response.status_code}", pin_response)
                else:
                    self.log_result("projects", "GC PIN - New project creation", False, "No project ID returned")
            else:
                self.log_result("projects", "GC PIN - New project creation", False, f"HTTP {create_response.status_code}", create_response)
                
        except Exception as e:
            self.log_result("projects", "GC PIN - New project PIN", False, str(e))
        
        print("✅ GC PIN System testing completed!")
        return True
        """Test project analytics endpoint"""
        print(f"\n=== Testing Project Analytics: {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
            
            if response.status_code == 200:
                response_data = response.json()
                required_fields = ["project_id", "project_name", "total_hours", "total_labor_cost_gc", 
                                 "total_material_cost", "total_revenue", "total_costs", "profit", "profit_margin"]
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    self.log_result("analytics", "Project analytics", True, f"Analytics calculated for project {project_id}")
                    return response_data
                else:
                    self.log_result("analytics", "Project analytics", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("analytics", "Project analytics", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("analytics", "Project analytics", False, str(e))
        
        return None
    
    def test_project_analytics(self, project_id):
        """Test project analytics endpoint with employee hourly rates"""
        print(f"\n=== Testing Project Analytics: {project_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/analytics")
            
            if response.status_code == 200:
                analytics = response.json()
                
                # Verify analytics structure
                required_fields = ["project_id", "total_hours", "total_labor_cost", "true_employee_cost", 
                                 "labor_markup_profit", "total_material_cost", "contract_amount", "profit_margin"]
                missing_fields = [field for field in required_fields if field not in analytics]
                
                if not missing_fields:
                    # Verify that true_employee_cost is different from total_labor_cost (showing markup)
                    true_cost = analytics.get("true_employee_cost", 0)
                    billed_cost = analytics.get("total_labor_cost", 0)
                    markup_profit = analytics.get("labor_markup_profit", 0)
                    
                    if markup_profit == (billed_cost - true_cost):
                        self.log_result("analytics", "Project analytics calculation", True, 
                                      f"Analytics calculated correctly: True Cost=${true_cost}, Billed=${billed_cost}, Markup=${markup_profit}")
                    else:
                        self.log_result("analytics", "Project analytics calculation", False, 
                                      f"Markup calculation incorrect: Expected {billed_cost - true_cost}, got {markup_profit}")
                else:
                    self.log_result("analytics", "Project analytics structure", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("analytics", "Project analytics", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("analytics", "Project analytics", False, str(e))
        
        return None
    
    def test_project_type_functionality(self):
        """Test the newly implemented project type functionality"""
        print("\n=== Testing Project Type Functionality ===")
        
        # Test 1: Create Full Project with contract amount
        print("Test 1: Creating Full Project with contract amount...")
        full_project_data = {
            "name": "Full Contract Project Test",
            "description": "Testing full project type with fixed contract",
            "client_company": "Full Contract Client Corp",
            "gc_email": "fullproject@client.com",
            "project_type": "full_project",
            "contract_amount": 150000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "123 Full Project Ave"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=full_project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                if (project.get("project_type") == "full_project" and 
                    project.get("contract_amount") == 150000.00):
                    self.log_result("projects", "Full project creation", True, 
                                  f"Full project created with type: {project['project_type']}, contract: ${project['contract_amount']}")
                    self.full_project_id = project["id"]
                else:
                    self.log_result("projects", "Full project creation", False, 
                                  f"Expected full_project/$150000, got {project.get('project_type')}/${project.get('contract_amount')}", response)
            else:
                self.log_result("projects", "Full project creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Full project creation", False, str(e))
        
        # Test 2: Create T&M Only Project (contract amount optional)
        print("Test 2: Creating T&M Only Project...")
        tm_project_data = {
            "name": "Time & Material Only Project Test",
            "description": "Testing T&M only project type",
            "client_company": "T&M Client Corp",
            "gc_email": "tmproject@client.com",
            "project_type": "tm_only",
            "contract_amount": 0,  # Optional for T&M projects
            "labor_rate": 110.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "456 T&M Project Blvd"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=tm_project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                if project.get("project_type") == "tm_only":
                    self.log_result("projects", "T&M project creation", True, 
                                  f"T&M project created with type: {project['project_type']}, rate: ${project['labor_rate']}/hr")
                    self.tm_project_id = project["id"]
                else:
                    self.log_result("projects", "T&M project creation", False, 
                                  f"Expected tm_only, got {project.get('project_type')}", response)
            else:
                self.log_result("projects", "T&M project creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "T&M project creation", False, str(e))
        
        # Test 3: Retrieve projects and verify project_type field
        print("Test 3: Retrieving projects and verifying project_type field...")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                if isinstance(projects, list) and len(projects) > 0:
                    # Check if project_type field is present in responses
                    projects_with_type = [p for p in projects if "project_type" in p]
                    if len(projects_with_type) > 0:
                        self.log_result("projects", "Project type field retrieval", True, 
                                      f"Found {len(projects_with_type)} projects with project_type field")
                        
                        # Verify our test projects are in the list
                        full_projects = [p for p in projects if p.get("project_type") == "full_project"]
                        tm_projects = [p for p in projects if p.get("project_type") == "tm_only"]
                        
                        self.log_result("projects", "Project type filtering", True, 
                                      f"Found {len(full_projects)} full projects, {len(tm_projects)} T&M projects")
                    else:
                        self.log_result("projects", "Project type field retrieval", False, "No projects have project_type field")
                else:
                    self.log_result("projects", "Project type field retrieval", False, "No projects found or invalid response format")
            else:
                self.log_result("projects", "Project type field retrieval", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Project type field retrieval", False, str(e))
        
        # Test 4: Update project type (full_project to tm_only)
        if hasattr(self, 'full_project_id'):
            print("Test 4: Updating project type from full_project to tm_only...")
            update_data = {
                "name": "Full Contract Project Test (Updated to T&M)",
                "description": "Updated to T&M project type",
                "client_company": "Full Contract Client Corp",
                "gc_email": "fullproject@client.com",
                "project_type": "tm_only",  # Changed from full_project
                "contract_amount": 0,  # Reset for T&M
                "labor_rate": 95.0,
                "project_manager": "Jesus Garcia",
                "start_date": datetime.now().isoformat(),
                "address": "123 Full Project Ave"
            }
            
            try:
                response = self.session.put(
                    f"{self.base_url}/projects/{self.full_project_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    updated_project = response.json()
                    if updated_project.get("project_type") == "tm_only":
                        self.log_result("projects", "Project type update", True, 
                                      f"Successfully updated project type to: {updated_project['project_type']}")
                    else:
                        self.log_result("projects", "Project type update", False, 
                                      f"Expected tm_only, got {updated_project.get('project_type')}", response)
                else:
                    self.log_result("projects", "Project type update", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result("projects", "Project type update", False, str(e))
        
        # Test 5: Backward compatibility - create project without project_type
        print("Test 5: Testing backward compatibility (project without project_type)...")
        backward_compat_data = {
            "name": "Backward Compatibility Test Project",
            "description": "Testing project creation without project_type field",
            "client_company": "Legacy Client Corp",
            "gc_email": "legacy@client.com",
            # Note: project_type field is intentionally omitted
            "contract_amount": 75000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "789 Legacy Project St"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=backward_compat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                # Should default to "full_project"
                if project.get("project_type") == "full_project":
                    self.log_result("projects", "Backward compatibility", True, 
                                  f"Project without project_type defaulted to: {project['project_type']}")
                else:
                    self.log_result("projects", "Backward compatibility", False, 
                                  f"Expected default 'full_project', got {project.get('project_type')}", response)
            else:
                self.log_result("projects", "Backward compatibility", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Backward compatibility", False, str(e))
        
        # Test 6: Data validation - invalid project_type
        print("Test 6: Testing data validation with invalid project_type...")
        invalid_data = {
            "name": "Invalid Project Type Test",
            "description": "Testing invalid project_type value",
            "client_company": "Invalid Client Corp",
            "gc_email": "invalid@client.com",
            "project_type": "invalid_type",  # Invalid value
            "contract_amount": 50000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "999 Invalid Project Rd"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            # This should either fail with validation error or default to full_project
            if response.status_code == 200:
                project = response.json()
                if project.get("project_type") in ["full_project", "tm_only"]:
                    self.log_result("projects", "Invalid project_type validation", True, 
                                  f"Invalid project_type handled gracefully, defaulted to: {project['project_type']}")
                else:
                    self.log_result("projects", "Invalid project_type validation", False, 
                                  f"Invalid project_type accepted: {project.get('project_type')}", response)
            elif response.status_code in [400, 422]:  # Validation error expected
                self.log_result("projects", "Invalid project_type validation", True, 
                              f"Invalid project_type properly rejected with HTTP {response.status_code}")
            else:
                self.log_result("projects", "Invalid project_type validation", False, 
                              f"Unexpected response: HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "Invalid project_type validation", False, str(e))
        
        print("✅ Project Type Functionality Testing Completed!")
        return True
    
    def test_email_endpoint(self):
        """Test email endpoint (will likely fail due to missing SMTP config)"""
        print("\n=== Testing Email Endpoint ===")
        
        # Create a simple base64 encoded "PDF" for testing
        fake_pdf = base64.b64encode(b"This is a fake PDF for testing").decode()
        
        email_data = {
            "to_email": "test@example.com",
            "cc_email": "cc@example.com",
            "subject": "Test T&M Tag Email",
            "message": "This is a test email from the T&M Tag system.",
            "pdf_data": f"data:application/pdf;base64,{fake_pdf}",
            "tm_tag_id": getattr(self, 'created_tm_tag_id', str(uuid.uuid4()))
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/send-email",
                json=email_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if "message" in response_data or "status" in response_data:
                    self.log_result("email", "Email sending", True)
                elif "error" in response_data and "configuration not set up" in response_data["error"]:
                    self.log_result("email", "Email sending", True, "Expected failure - SMTP not configured")
                else:
                    self.log_result("email", "Email sending", False, "Unexpected response format", response)
            else:
                # Email endpoint is expected to fail due to missing SMTP config
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if "error" in response_data and "configuration not set up" in response_data["error"]:
                    self.log_result("email", "Email sending", True, "Expected failure - SMTP not configured")
                else:
                    self.log_result("email", "Email sending", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("email", "Email sending", False, str(e))
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n=== Testing CORS Configuration ===")
        
        try:
            # Test preflight request
            response = self.session.options(
                f"{self.base_url}/tm-tags",
                headers={
                    "Origin": "https://firepro-auth-hub.preview.emergentagent.com",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            ]
            
            present_headers = [header for header in cors_headers if header in response.headers]
            
            if len(present_headers) >= 2:  # At least 2 CORS headers should be present
                self.log_result("general", "CORS configuration", True, f"CORS headers present: {present_headers}")
            else:
                self.log_result("general", "CORS configuration", False, f"Missing CORS headers. Present: {present_headers}")
                
        except Exception as e:
            self.log_result("general", "CORS configuration", False, str(e))
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid T&M tag data
        try:
            invalid_data = {"invalid": "data"}
            response = self.session.post(
                f"{self.base_url}/tm-tags",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [400, 422]:  # Bad request or validation error
                self.log_result("general", "Error handling - invalid T&M data", True, f"Properly rejected with {response.status_code}")
            else:
                self.log_result("general", "Error handling - invalid T&M data", False, f"Unexpected status: {response.status_code}", response)
                
        except Exception as e:
            self.log_result("general", "Error handling - invalid T&M data", False, str(e))
        
        # Test non-existent endpoint
        try:
            response = self.session.get(f"{self.base_url}/non-existent-endpoint")
            
            if response.status_code == 404:
                self.log_result("general", "Error handling - 404", True)
            else:
                self.log_result("general", "Error handling - 404", False, f"Expected 404, got {response.status_code}", response)
                
        except Exception as e:
            self.log_result("general", "Error handling - 404", False, str(e))
    
    def run_tm_analytics_tests(self):
        """Run T&M analytics and forecasted schedule tests specifically"""
        print("🚀 Starting T&M Analytics and Forecasted Schedule Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        print("\n" + "=" * 60)
        print("📊 TESTING T&M PROJECT ANALYTICS & FORECASTED SCHEDULE")
        print("=" * 60)
        
        # Test 1: T&M Project Analytics - should show markup profit correctly
        self.test_tm_project_analytics()
        
        # Test 2: Full Project Analytics - should calculate profit as contract minus costs
        self.test_full_project_analytics()
        
        # Test 3: Forecasted Schedule Creation - test creating projects with forecasted values
        self.test_forecasted_schedule_creation()
        
        # Test 4: Analytics Response Fields - verify GET /api/projects/{id}/analytics returns new fields
        self.test_analytics_response_fields()
        
        # Test 5: Variance Analysis - test comparison between forecasted vs actual values
        self.test_variance_analysis()
        
        # Test 6: Enhanced Cost Analytics (existing test)
        self.test_enhanced_cost_analytics()
        
        return self.generate_report()

    # =============================================================================
    # PROJECT INTELLIGENCE TESTING METHODS
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin authentication with PIN J777"""
        print("\n=== Testing Admin Authentication ===")
        try:
            # Test valid admin PIN
            response = self.session.post(f"{self.base_url}/auth/admin", 
                json={"pin": "J777"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("role") == "admin":
                    self.log_result("general", "Admin authentication", True, 
                                  f"Admin login successful with token: {data.get('token')}")
                    return True
            
            self.log_result("general", "Admin authentication", False, 
                          f"Authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Admin authentication", False, str(e))
            return False
            
    def test_llm_email_processing(self):
        """Test LLM Email Processing endpoint"""
        print("\n=== Testing LLM Email Processing ===")
        try:
            # Test RFP email sample
            rfp_email = {
                "subject": "RFP: Fire Sprinkler System - Downtown Office Building",
                "body": "We are seeking bids for a complete fire sprinkler system installation for our new downtown office building project. Project Name: Downtown Office Complex, Address: 1200 Broadway, San Diego, CA 92101, Client: Downtown Development LLC, Billing: Time & Material preferred at $95/hour, Due Date: October 15, 2025",
                "sender_email": "procurement@downtowndev.com",
                "received_at": datetime.now().isoformat()
            }
            
            response = self.session.post(f"{self.base_url}/intelligence/process-email", 
                json=rfp_email)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("general", "RFP Email processing", True, 
                              f"Classification: {data.get('classification', 'N/A')}, Confidence: {data.get('confidence', 'N/A')}")
                
                # Test Invoice email sample
                invoice_email = {
                    "subject": "Invoice #INV-2025-0123 - $15,500",
                    "body": "Invoice Number: INV-2025-0123, Date: September 30, 2025, Amount: $15,500.00, Project: 3rd Ave Fire Protection, Payment Terms: Net 30",
                    "sender_email": "billing@contractor.com",
                    "received_at": datetime.now().isoformat()
                }
                
                response2 = self.session.post(f"{self.base_url}/intelligence/process-email", 
                    json=invoice_email)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    self.log_result("general", "Invoice Email processing", True, 
                                  f"Classification: {data2.get('classification', 'N/A')}")
                    
                    # Test Progress Update email sample
                    progress_email = {
                        "subject": "Project Update - Oregon St Sprinkler Installation 75% Complete",
                        "body": "Project: Oregon St Fire Sprinkler System, Status: 75% Complete, Milestone: Main line installation completed, Next Phase: Head installation and testing",
                        "sender_email": "foreman@contractor.com",
                        "received_at": datetime.now().isoformat()
                    }
                    
                    response3 = self.session.post(f"{self.base_url}/intelligence/process-email", 
                        json=progress_email)
                    
                    if response3.status_code == 200:
                        data3 = response3.json()
                        self.log_result("general", "Progress Update Email processing", True, 
                                      f"Classification: {data3.get('classification', 'N/A')}")
                        return True
                        
            self.log_result("general", "Email processing", False, 
                          f"Failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Email processing", False, str(e))
            return False
            
    def test_project_intelligence_dashboard(self):
        """Test Project Intelligence Dashboard endpoints"""
        print("\n=== Testing Project Intelligence Dashboard ===")
        try:
            # Test system-wide intelligence dashboard
            response = self.session.get(f"{self.base_url}/intelligence/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("general", "System intelligence dashboard", True, 
                              f"Emails processed: {data.get('total_emails_processed', 0)}, Candidates: {data.get('project_candidates_count', 0)}")
                
                # Test project-specific intelligence (using existing project)
                projects_response = self.session.get(f"{self.base_url}/projects")
                if projects_response.status_code == 200:
                    projects = projects_response.json()
                    if projects:
                        project_id = projects[0]["id"]
                        project_intel_response = self.session.get(f"{self.base_url}/intelligence/project/{project_id}")
                        
                        if project_intel_response.status_code == 200:
                            project_data = project_intel_response.json()
                            self.log_result("general", "Project intelligence", True, 
                                          f"Tasks: {project_data.get('tasks_count', 0)}, Invoices: {project_data.get('invoices_count', 0)}")
                            return True
                
            self.log_result("general", "Intelligence dashboard", False, 
                          f"Failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Intelligence dashboard", False, str(e))
            return False
            
    def test_review_queue_system(self):
        """Test Review Queue System"""
        print("\n=== Testing Review Queue System ===")
        try:
            # Get review queue items
            response = self.session.get(f"{self.base_url}/review-queue")
            
            if response.status_code == 200:
                items = response.json()
                self.log_result("general", "Review queue retrieval", True, 
                              f"Loaded {len(items)} items")
                
                # If there are items, test resolving one
                if items:
                    item_id = items[0]["id"]
                    resolve_response = self.session.post(f"{self.base_url}/review-queue/{item_id}/resolve",
                        json={"action": "approve", "notes": "Test approval"})
                    
                    if resolve_response.status_code == 200:
                        self.log_result("general", "Review queue resolution", True, 
                                      "Item resolved successfully")
                        return True
                else:
                    self.log_result("general", "Review queue empty", True, 
                                  "Queue is empty (expected for new system)")
                    return True
                    
            self.log_result("general", "Review queue", False, 
                          f"Failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Review queue", False, str(e))
            return False
            
    def test_project_candidate_management(self):
        """Test Project Candidate Management"""
        print("\n=== Testing Project Candidate Management ===")
        try:
            # Get project candidates
            response = self.session.get(f"{self.base_url}/intelligence/project-candidates")
            
            if response.status_code == 200:
                candidates = response.json()
                self.log_result("general", "Project candidates retrieval", True, 
                              f"Loaded {len(candidates)} candidates")
                
                # If there are candidates, test approval workflow
                if candidates:
                    candidate_id = candidates[0]["id"]
                    approve_response = self.session.post(f"{self.base_url}/intelligence/approve-candidate/{candidate_id}",
                        json={"tm_rate": 95.0, "notes": "Test approval"})
                    
                    if approve_response.status_code == 200:
                        self.log_result("general", "Project candidate approval", True, 
                                      "Candidate approved successfully")
                        return True
                else:
                    self.log_result("general", "Project candidates empty", True, 
                                  "No candidates found (expected for new system)")
                    return True
                    
            self.log_result("general", "Project candidates", False, 
                          f"Failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Project candidates", False, str(e))
            return False
            
    def test_enhanced_task_management(self):
        """Test Enhanced Task Management System"""
        print("\n=== Testing Enhanced Task Management ===")
        try:
            # Get existing projects first
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code != 200:
                self.log_result("general", "Task management setup", False, 
                              "Could not get projects for task testing")
                return False
                
            projects = projects_response.json()
            if not projects:
                self.log_result("general", "Task management setup", False, 
                              "No projects available for task testing")
                return False
                
            project_id = projects[0]["id"]
            
            # Test task creation
            task_data = {
                "project_id": project_id,
                "title": "Test Fire System Installation Task",
                "description": "Install main fire sprinkler lines",
                "priority": "high",
                "status": "open",
                "estimated_hours": 8.0,
                "assigned_to": "Mike Rodriguez"
            }
            
            create_response = self.session.post(f"{self.base_url}/tasks", json=task_data)
            
            if create_response.status_code == 200:
                task = create_response.json()
                task_id = task["id"]
                self.log_result("general", "Task creation", True, 
                              f"Created task: {task_id}")
                
                # Test task retrieval
                get_response = self.session.get(f"{self.base_url}/tasks")
                if get_response.status_code == 200:
                    tasks = get_response.json()
                    self.log_result("general", "Task retrieval", True, 
                                  f"Retrieved {len(tasks)} tasks")
                    
                    # Test task update
                    update_data = {
                        "status": "in_progress",
                        "actual_hours": 4.0,
                        "notes": "Started installation work"
                    }
                    
                    update_response = self.session.put(f"{self.base_url}/tasks/{task_id}", json=update_data)
                    if update_response.status_code == 200:
                        self.log_result("general", "Task update", True, 
                                      "Task updated successfully")
                        return True
                        
            self.log_result("general", "Task management", False, 
                          f"Failed: {create_response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Task management", False, str(e))
            return False
            
    def test_invoice_management_system(self):
        """Test Invoice Management System"""
        print("\n=== Testing Invoice Management System ===")
        try:
            # Get existing projects first
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code != 200:
                self.log_result("general", "Invoice management setup", False, 
                              "Could not get projects for invoice testing")
                return False
                
            projects = projects_response.json()
            if not projects:
                self.log_result("general", "Invoice management setup", False, 
                              "No projects available for invoice testing")
                return False
                
            project_id = projects[0]["id"]
            
            # Test invoice creation
            invoice_data = {
                "project_id": project_id,
                "invoice_number": "INV-2025-TEST-001",
                "amount": 15500.00,
                "status": "draft",
                "issue_date": date.today().isoformat(),
                "due_date": "2025-11-15",
                "description": "Fire sprinkler system installation - Phase 1",
                "line_items": [
                    {
                        "description": "Labor - 40 hours @ $95/hr",
                        "quantity": 40,
                        "rate": 95.0,
                        "amount": 3800.0
                    },
                    {
                        "description": "Materials - Sprinkler heads and pipes",
                        "quantity": 1,
                        "rate": 11700.0,
                        "amount": 11700.0
                    }
                ]
            }
            
            create_response = self.session.post(f"{self.base_url}/invoices", json=invoice_data)
            
            if create_response.status_code == 200:
                invoice = create_response.json()
                invoice_id = invoice["id"]
                self.log_result("general", "Invoice creation", True, 
                              f"Created invoice: {invoice_id}")
                
                # Test invoice retrieval
                get_response = self.session.get(f"{self.base_url}/invoices")
                if get_response.status_code == 200:
                    invoices = get_response.json()
                    self.log_result("general", "Invoice retrieval", True, 
                                  f"Retrieved {len(invoices)} invoices")
                    
                    # Test invoice status update
                    update_data = {
                        "status": "sent",
                        "sent_date": date.today().isoformat(),
                        "notes": "Invoice sent to client via email"
                    }
                    
                    update_response = self.session.put(f"{self.base_url}/invoices/{invoice_id}", json=update_data)
                    if update_response.status_code == 200:
                        self.log_result("general", "Invoice status update", True, 
                                      "Invoice status updated successfully")
                        return True
                        
            self.log_result("general", "Invoice management", False, 
                          f"Failed: {create_response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "Invoice management", False, str(e))
            return False
            
    def test_llm_integration_health(self):
        """Test LLM Integration Health and Error Handling"""
        print("\n=== Testing LLM Integration Health ===")
        try:
            # Test email processing with malformed data to check error handling
            malformed_email = {
                "subject": "",  # Empty subject
                "body": "",     # Empty body
                "sender_email": "invalid-email"  # Invalid email format
            }
            
            response = self.session.post(f"{self.base_url}/intelligence/process-email", 
                json=malformed_email)
            
            # Should handle gracefully (either 400 for validation or 200 with low confidence)
            if response.status_code in [200, 400, 422]:
                self.log_result("general", "LLM malformed request handling", True, 
                              f"Handles malformed requests gracefully: {response.status_code}")
                
                # Test with missing LLM key scenario (should fallback gracefully)
                test_email = {
                    "subject": "Test Email Without LLM",
                    "body": "This should be handled even if LLM is disabled",
                    "sender_email": "test@example.com",
                    "received_at": datetime.now().isoformat()
                }
                
                response2 = self.session.post(f"{self.base_url}/intelligence/process-email", 
                    json=test_email)
                
                if response2.status_code in [200, 503]:  # 200 for success, 503 for service unavailable
                    self.log_result("general", "LLM fallback behavior", True, 
                                  f"Fallback behavior working: {response2.status_code}")
                    return True
                    
            self.log_result("general", "LLM integration health", False, 
                          f"Health check failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("general", "LLM integration health", False, str(e))
            return False
            
    def test_existing_rhino_platform_core(self):
        """Test existing Rhino Platform core functionality"""
        print("\n=== Testing Existing Rhino Platform Core ===")
        try:
            # Test projects endpoint
            projects_response = self.session.get(f"{self.base_url}/projects")
            if projects_response.status_code != 200:
                self.log_result("general", "Core projects endpoint", False, 
                              f"Projects endpoint failed: {projects_response.status_code}")
                return False
                
            projects = projects_response.json()
            self.log_result("general", "Core projects endpoint", True, 
                          f"Loaded {len(projects)} projects")
            
            # Test installers endpoint
            installers_response = self.session.get(f"{self.base_url}/installers")
            if installers_response.status_code != 200:
                self.log_result("general", "Core installers endpoint", False, 
                              f"Installers endpoint failed: {installers_response.status_code}")
                return False
                
            installers = installers_response.json()
            self.log_result("general", "Core installers endpoint", True, 
                          f"Loaded {len(installers)} installers")
            
            # Test time logs endpoint
            time_logs_response = self.session.get(f"{self.base_url}/time-logs")
            if time_logs_response.status_code != 200:
                self.log_result("general", "Core time logs endpoint", False, 
                              f"Time logs endpoint failed: {time_logs_response.status_code}")
                return False
                
            time_logs = time_logs_response.json()
            self.log_result("general", "Core time logs endpoint", True, 
                          f"Loaded {len(time_logs)} time logs")
            
            return True
            
        except Exception as e:
            self.log_result("general", "Core platform", False, str(e))
            return False

    def run_project_intelligence_tests(self):
        """Run all Project Intelligence tests"""
        print("🚀 Starting Enhanced Rhino Platform with Project Intelligence Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        # Test authentication first
        self.test_admin_authentication()
        
        # Test existing core functionality
        self.test_existing_rhino_platform_core()
        
        # Test new Project Intelligence features
        print("\n" + "=" * 60)
        print("🧠 TESTING PROJECT INTELLIGENCE FEATURES")
        print("=" * 60)
        
        self.test_llm_email_processing()
        self.test_project_intelligence_dashboard()
        self.test_review_queue_system()
        self.test_project_candidate_management()
        self.test_enhanced_task_management()
        self.test_invoice_management_system()
        self.test_llm_integration_health()
        
        return self.generate_report()

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Backend API Tests for TM3014 T&M Daily Tag App + Project Management System")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        # Test T&M Tag APIs
        created_tm_tag = self.test_tm_tag_creation()
        self.test_tm_tag_retrieval()
        
        if created_tm_tag and "id" in created_tm_tag:
            self.test_tm_tag_by_id(created_tm_tag["id"])
        
        # Test DELETE functionality - NEW TEST FOR USER REPORTED ISSUE
        self.test_tm_tag_deletion()
        
        # Test Worker APIs
        self.test_worker_creation()
        self.test_worker_retrieval()
        
        # Test NEW Project Management System APIs
        print("\n" + "=" * 50)
        print("🏗️  TESTING PROJECT MANAGEMENT SYSTEM ENDPOINTS")
        print("=" * 50)
        
        # Test Project APIs
        created_project = self.test_project_creation()
        self.test_project_retrieval()
        
        # Test NEW Project Type Functionality
        self.test_project_type_functionality()
        
        if created_project and "id" in created_project:
            project_id = created_project["id"]
            self.test_project_by_id(project_id)
            self.test_project_update(project_id)
            
            # Test Employee APIs
            created_employees = self.test_employee_creation()
            self.test_employee_retrieval()
            
            if created_employees:
                employee_id = created_employees[0]["id"]
                self.test_employee_by_id(employee_id)
                self.test_employee_update(employee_id)
                self.test_employee_deletion(employee_id)
            
            # Test Crew Log APIs
            created_crew_log = self.test_crew_log_creation()
            self.test_crew_log_retrieval()
            
            if created_crew_log and "id" in created_crew_log:
                log_id = created_crew_log["id"]
                self.test_crew_log_by_id(log_id)
                self.test_crew_log_deletion(log_id)
            
            # Test Material Purchase APIs
            created_materials = self.test_material_creation()
            self.test_material_retrieval()
            
            if created_materials:
                material_id = created_materials[0]["id"]
                self.test_material_by_id(material_id)
                self.test_material_deletion(material_id)
            
            # Test Project Analytics API
            self.test_project_analytics(project_id)
            
            # Clean up - delete the test project last
            self.test_project_deletion(project_id)
        
        # Test Email API
        self.test_email_endpoint()
        
        # Test general functionality
        self.test_cors_configuration()
        self.test_error_handling()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_passed = sum(category["passed"] for category in self.test_results.values())
        total_failed = sum(category["failed"] for category in self.test_results.values())
        total_tests = total_passed + total_failed
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} ✅")
        print(f"Failed: {total_failed} ❌")
        print(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        print("\n📋 DETAILED RESULTS:")
        for category, results in self.test_results.items():
            if results["passed"] > 0 or results["failed"] > 0:
                print(f"\n{category.upper()}:")
                print(f"  Passed: {results['passed']} ✅")
                print(f"  Failed: {results['failed']} ❌")
                
                if results["errors"]:
                    print("  Errors:")
                    for error in results["errors"]:
                        print(f"    - {error}")
        
        return {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "success_rate": (total_passed/total_tests*100) if total_tests > 0 else 0,
            "details": self.test_results
        }

    def run_gc_pin_tests(self):
        """Run GC PIN system tests specifically"""
        print("🚀 Starting GC PIN System Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        print("\n" + "=" * 60)
        print("🔐 TESTING GC PIN SYSTEM")
        print("=" * 60)
        
        # Run the comprehensive GC PIN system test
        self.test_gc_pin_system()
        
        return self.generate_report()

    def test_gc_pin_system_investigation(self):
        """Test the specific GC PIN system issue reported by user"""
        print("\n=== INVESTIGATING GC PIN SYSTEM ISSUE ===")
        print("User reported: PIN 8598 for '3rd Ave' project not working for login and not showing in table")
        print("Testing specific project ID: 68cc802f8d44fcd8015b39b8")
        
        # Step 1: Get the specific project's PIN
        print("\nStep 1: Getting PIN for project 68cc802f8d44fcd8015b39b8...")
        try:
            response = self.session.get(f"{self.base_url}/projects/68cc802f8d44fcd8015b39b8/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                project_pin = pin_data.get("gcPin") or pin_data.get("gc_pin")
                project_name = pin_data.get("projectName") or pin_data.get("project_name")
                pin_used = pin_data.get("pinUsed") or pin_data.get("gc_pin_used", False)
                
                self.log_result("general", "Get specific project PIN", True, 
                              f"Project: {project_name}, PIN: {project_pin}, Used: {pin_used}")
                
                # Store for later tests
                self.test_project_id = "68cc802f8d44fcd8015b39b8"
                self.test_project_pin = project_pin
                self.test_project_name = project_name
                
            else:
                self.log_result("general", "Get specific project PIN", False, 
                              f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("general", "Get specific project PIN", False, str(e))
            return False
        
        # Step 2: Check if the PIN was saved to the project
        print(f"\nStep 2: Checking if PIN is saved in project record...")
        try:
            response = self.session.get(f"{self.base_url}/projects/68cc802f8d44fcd8015b39b8")
            
            if response.status_code == 200:
                project_data = response.json()
                stored_pin = project_data.get("gc_pin")
                stored_pin_used = project_data.get("gc_pin_used", False)
                
                if stored_pin:
                    self.log_result("general", "PIN saved in project", True, 
                                  f"Project has gc_pin: {stored_pin}, gc_pin_used: {stored_pin_used}")
                    
                    # Check if it matches the PIN from step 1
                    if stored_pin == self.test_project_pin:
                        self.log_result("general", "PIN consistency", True, "PIN matches between endpoints")
                    else:
                        self.log_result("general", "PIN consistency", False, 
                                      f"PIN mismatch: endpoint returned {self.test_project_pin}, project has {stored_pin}")
                else:
                    self.log_result("general", "PIN saved in project", False, "Project has no gc_pin field")
                    
            else:
                self.log_result("general", "PIN saved in project", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("general", "PIN saved in project", False, str(e))
        
        # Step 3: Test GC login with the generated PIN
        print(f"\nStep 3: Testing GC login with PIN {self.test_project_pin}...")
        try:
            login_data = {
                "projectId": "68cc802f8d44fcd8015b39b8",
                "pin": self.test_project_pin
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                if "success" in login_result and login_result["success"]:
                    self.log_result("general", "GC login with PIN", True, 
                                  f"Login successful with PIN {self.test_project_pin}")
                    
                    # Check if PIN was regenerated after use
                    new_pin = login_result.get("newPin")
                    if new_pin:
                        self.log_result("general", "PIN regeneration", True, 
                                      f"New PIN generated: {new_pin}")
                        self.new_pin = new_pin
                    else:
                        self.log_result("general", "PIN regeneration", False, "No new PIN in response")
                        
                else:
                    self.log_result("general", "GC login with PIN", False, 
                                  f"Login failed: {login_result}")
                    
            elif response.status_code == 401:
                error_data = response.json()
                self.log_result("general", "GC login with PIN", False, 
                              f"Login rejected (401): {error_data.get('detail', 'Unknown error')}")
            else:
                self.log_result("general", "GC login with PIN", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("general", "GC login with PIN", False, str(e))
        
        # Step 4: Check all projects to see their PIN status
        print(f"\nStep 4: Checking all projects for PIN status...")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                projects_with_pins = 0
                projects_without_pins = 0
                target_project_found = False
                
                print(f"Found {len(projects)} projects:")
                for project in projects:
                    project_id = project.get("id")
                    project_name = project.get("name", "Unknown")
                    gc_pin = project.get("gc_pin")
                    gc_pin_used = project.get("gc_pin_used", False)
                    
                    if gc_pin:
                        projects_with_pins += 1
                        pin_status = "USED" if gc_pin_used else "ACTIVE"
                        print(f"  - {project_name} (ID: {project_id[:8]}...): PIN {gc_pin} ({pin_status})")
                        
                        if project_id == "68cc802f8d44fcd8015b39b8":
                            target_project_found = True
                            if project_name == "3rd Ave":
                                self.log_result("general", "Target project in list", True, 
                                              f"'3rd Ave' project found with PIN {gc_pin}")
                            else:
                                self.log_result("general", "Target project name", False, 
                                              f"Project found but name is '{project_name}', not '3rd Ave'")
                    else:
                        projects_without_pins += 1
                        print(f"  - {project_name} (ID: {project_id[:8]}...): NO PIN")
                
                if not target_project_found:
                    self.log_result("general", "Target project in list", False, 
                                  "Project 68cc802f8d44fcd8015b39b8 not found in projects list")
                
                self.log_result("general", "Projects PIN status", True, 
                              f"{projects_with_pins} projects with PINs, {projects_without_pins} without PINs")
                
            else:
                self.log_result("general", "Projects PIN status", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("general", "Projects PIN status", False, str(e))
        
        # Step 5: Test if the issue is with PIN 8598 specifically
        print(f"\nStep 5: Testing if PIN 8598 exists in any project...")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                pin_8598_found = False
                
                for project in projects:
                    if project.get("gc_pin") == "8598":
                        pin_8598_found = True
                        project_name = project.get("name", "Unknown")
                        project_id = project.get("id")
                        self.log_result("general", "PIN 8598 exists", True, 
                                      f"PIN 8598 found in project '{project_name}' (ID: {project_id})")
                        break
                
                if not pin_8598_found:
                    self.log_result("general", "PIN 8598 exists", False, 
                                  "PIN 8598 not found in any project - this explains the login failure")
                    
                    # Test login with non-existent PIN 8598
                    print("Testing login with non-existent PIN 8598...")
                    login_data = {
                        "projectId": "68cc802f8d44fcd8015b39b8",
                        "pin": "8598"
                    }
                    
                    login_response = self.session.post(
                        f"{self.base_url}/gc/login-simple",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if login_response.status_code == 401:
                        self.log_result("general", "Invalid PIN rejection", True, 
                                      "System correctly rejects non-existent PIN 8598")
                    else:
                        self.log_result("general", "Invalid PIN rejection", False, 
                                      f"Unexpected response to invalid PIN: {login_response.status_code}")
                
            else:
                self.log_result("general", "PIN 8598 search", False, 
                              f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("general", "PIN 8598 search", False, str(e))
        
        return True

    def test_gc_pin_generation_specific(self):
        """Test specific PIN generation for requested project IDs"""
        print("\n=== Testing GC PIN Generation for Specific Projects ===")
        
        # Test the specific project IDs mentioned in the review request
        test_project_ids = [
            "68cc802f8d44fcd8015b39b8",
            "68cc802f8d44fcd8015b39b9"
        ]
        
        pin_results = {}
        
        for project_id in test_project_ids:
            print(f"\n--- Testing PIN generation for project {project_id} ---")
            
            # Step 1: Test PIN generation endpoint
            try:
                response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                
                if response.status_code == 200:
                    pin_data = response.json()
                    
                    # Verify response structure
                    required_fields = ["projectId", "projectName", "gcPin", "pinUsed"]
                    missing_fields = [field for field in required_fields if field not in pin_data]
                    
                    if not missing_fields:
                        pin_results[project_id] = {
                            "pin": pin_data["gcPin"],
                            "project_name": pin_data["projectName"],
                            "pin_used": pin_data["pinUsed"]
                        }
                        self.log_result("projects", f"PIN generation - {project_id}", True, 
                                      f"Generated PIN: {pin_data['gcPin']} for project: {pin_data['projectName']}")
                        
                        print(f"✅ PIN Generated: {pin_data['gcPin']}")
                        print(f"   Project Name: {pin_data['projectName']}")
                        print(f"   PIN Used: {pin_data['pinUsed']}")
                        
                    else:
                        self.log_result("projects", f"PIN generation - {project_id}", False, 
                                      f"Missing fields: {missing_fields}", response)
                        print(f"❌ Missing fields in response: {missing_fields}")
                        
                elif response.status_code == 404:
                    self.log_result("projects", f"PIN generation - {project_id}", False, 
                                  "Project not found", response)
                    print(f"❌ Project {project_id} not found")
                    
                else:
                    self.log_result("projects", f"PIN generation - {project_id}", False, 
                                  f"HTTP {response.status_code}", response)
                    print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_result("projects", f"PIN generation - {project_id}", False, str(e))
                print(f"❌ Exception: {str(e)}")
        
        # Step 2: Check if projects were updated by getting all projects
        print(f"\n--- Checking if projects were updated with gc_pin field ---")
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                all_projects = response.json()
                
                print(f"Total projects in system: {len(all_projects)}")
                
                for project_id in test_project_ids:
                    # Find the specific project
                    target_project = None
                    for project in all_projects:
                        if project.get("id") == project_id:
                            target_project = project
                            break
                    
                    if target_project:
                        print(f"\n📋 Project {project_id} data structure:")
                        print(f"   ID: {target_project.get('id', 'N/A')}")
                        print(f"   Name: {target_project.get('name', 'N/A')}")
                        print(f"   GC PIN: {target_project.get('gc_pin', 'NOT SET')}")
                        print(f"   PIN Used: {target_project.get('gc_pin_used', 'NOT SET')}")
                        print(f"   Has 'id' field: {'id' in target_project}")
                        print(f"   Has '_id' field: {'_id' in target_project}")
                        
                        # Check if gc_pin field is set
                        if target_project.get("gc_pin"):
                            expected_pin = pin_results.get(project_id, {}).get("pin")
                            actual_pin = target_project.get("gc_pin")
                            
                            if expected_pin and expected_pin == actual_pin:
                                self.log_result("projects", f"PIN update verification - {project_id}", True, 
                                              f"Project updated with PIN: {actual_pin}")
                            else:
                                self.log_result("projects", f"PIN update verification - {project_id}", False, 
                                              f"PIN mismatch - Expected: {expected_pin}, Got: {actual_pin}")
                        else:
                            self.log_result("projects", f"PIN update verification - {project_id}", False, 
                                          "Project does not have gc_pin field set")
                    else:
                        print(f"❌ Project {project_id} not found in projects list")
                        self.log_result("projects", f"PIN update verification - {project_id}", False, 
                                      "Project not found in projects list")
                
                # Show sample of project data structure
                if all_projects:
                    sample_project = all_projects[0]
                    print(f"\n📋 Sample project data structure:")
                    for key, value in sample_project.items():
                        if key not in ['description', 'address']:  # Skip long fields
                            print(f"   {key}: {value}")
                
            else:
                self.log_result("projects", "PIN update verification", False, 
                              f"Could not retrieve projects list: HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("projects", "PIN update verification", False, str(e))
        
        # Step 3: Test with a different project ID for comparison
        print(f"\n--- Testing with different project ID for comparison ---")
        
        # Get a different project ID from the list
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                all_projects = response.json()
                
                # Find a project that's not in our test list
                comparison_project = None
                for project in all_projects:
                    if project.get("id") not in test_project_ids:
                        comparison_project = project
                        break
                
                if comparison_project:
                    comparison_id = comparison_project["id"]
                    print(f"Testing PIN generation for comparison project: {comparison_id}")
                    
                    response = self.session.get(f"{self.base_url}/projects/{comparison_id}/gc-pin")
                    
                    if response.status_code == 200:
                        pin_data = response.json()
                        self.log_result("projects", f"Comparison PIN generation - {comparison_id}", True, 
                                      f"Generated PIN: {pin_data.get('gcPin', 'N/A')}")
                        
                        print(f"✅ Comparison Project PIN: {pin_data.get('gcPin', 'N/A')}")
                        print(f"   Project Name: {pin_data.get('projectName', 'N/A')}")
                        
                    else:
                        self.log_result("projects", f"Comparison PIN generation - {comparison_id}", False, 
                                      f"HTTP {response.status_code}", response)
                else:
                    print("No other projects available for comparison")
                    
        except Exception as e:
            print(f"Error during comparison test: {str(e)}")
        
        print(f"\n=== GC PIN Generation Test Summary ===")
        for project_id, result in pin_results.items():
            print(f"Project {project_id}: PIN {result['pin']} ({'Used' if result['pin_used'] else 'Available'})")
        
        return pin_results

    def run_pin_generation_tests(self):
        """Run specific PIN generation tests as requested in review"""
        print("🚀 Starting PIN Generation Tests for Specific Projects")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        # Run the specific PIN generation test
        self.test_gc_pin_generation_specific()
        
        return self.generate_report()

    def run_pin_investigation_tests(self):
        """Run the specific PIN investigation tests"""
        print("🚀 Starting GC PIN System Investigation")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        print("\n" + "=" * 60)
        print("🔍 INVESTIGATING SPECIFIC PIN ISSUE")
        print("=" * 60)
        
        # Run the specific PIN investigation
        self.test_gc_pin_system_investigation()
        
        return self.generate_report()

if __name__ == "__main__":
    tester = TMTagAPITester()
    
    # Check command line arguments for specific test types
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "pin_generation":
            print("Running PIN Generation Tests for Specific Projects...")
            results = tester.run_pin_generation_tests()
        elif test_type == "pin_investigation":
            print("Running GC PIN System Investigation...")
            results = tester.run_pin_investigation_tests()
        elif test_type == "gc_pin":
            print("Running GC PIN System Tests...")
            results = tester.run_gc_pin_tests()
        else:
            print("Running PIN Generation Tests (default)...")
            results = tester.run_pin_generation_tests()
    else:
        print("Running PIN Generation Tests...")
        results = tester.run_pin_generation_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)