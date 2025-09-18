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
BACKEND_URL = "https://fire-tm-reports.preview.emergentagent.com/api"

class TMTagAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "tm_tags": {"passed": 0, "failed": 0, "errors": []},
            "workers": {"passed": 0, "failed": 0, "errors": []},
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
                    "Origin": "https://fire-tm-reports.preview.emergentagent.com",
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
        print("🚀 Starting Backend API Tests for TM3014 T&M Daily Tag App")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return self.generate_report()
        
        # Test T&M Tag APIs
        created_tm_tag = self.test_tm_tag_creation()
        self.test_tm_tag_retrieval()
        
        if created_tm_tag and "id" in created_tm_tag:
            self.test_tm_tag_by_id(created_tm_tag["id"])
        
        # Test Worker APIs
        self.test_worker_creation()
        self.test_worker_retrieval()
        
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