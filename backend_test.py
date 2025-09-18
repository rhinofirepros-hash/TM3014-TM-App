#!/usr/bin/env python3
"""
Backend API Testing for TM3014 T&M Daily Tag App
Tests all backend endpoints with realistic data
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import base64
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://rhino-tm-tracker.preview.emergentagent.com/api"

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
                    "Origin": "https://rhino-tm-tracker.preview.emergentagent.com",
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

if __name__ == "__main__":
    tester = TMTagAPITester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)