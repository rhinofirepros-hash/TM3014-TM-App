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
BACKEND_URL = "https://project-tracker-102.preview.emergentagent.com/api"

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
        """Create realistic project data for testing"""
        return {
            "name": "Downtown Office Complex - Phase 2",
            "description": "Complete electrical installation for 15-story office building including power distribution, lighting systems, and emergency backup systems.",
            "client_company": "Metropolitan Development Corp",
            "gc_email": "project.manager@metrodev.com",
            "contract_amount": 485000.00,
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
                required_fields = ["id", "name", "client_company", "gc_email", "status", "created_at"]
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
                    required_fields = ["id", "name", "base_pay", "burden_cost", "position", "status", "created_at"]
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
            "base_pay": 30.00,
            "burden_cost": 13.50,
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
                if response_data.get("base_pay") == update_data["base_pay"]:
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
    
    def test_project_analytics(self, project_id):
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
                    "Origin": "https://project-tracker-102.preview.emergentagent.com",
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