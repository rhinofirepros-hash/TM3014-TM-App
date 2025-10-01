#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION SITE FUNCTIONALITY AUDIT
Testing tm.rhinofirepro.com backend functionality

CRITICAL ISSUES TO INVESTIGATE:
1. T&M tag creation doesn't save to backend (only saves locally/offline mode)
2. PDF export doesn't work 
3. PDF preview doesn't work
4. Many application features non-functional on production

Production Backend: https://tm3014-tm-app-production.up.railway.app
Preview Backend: https://project-autopilot.preview.emergentagent.com
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Production and Preview Backend URLs for comparison
PRODUCTION_BACKEND = "https://tm3014-tm-app-production.up.railway.app/api"
PREVIEW_BACKEND = "https://project-autopilot.preview.emergentagent.com/api"

class ProductionAuditTester:
    def __init__(self):
        self.production_url = PRODUCTION_BACKEND
        self.preview_url = PREVIEW_BACKEND
        self.session = requests.Session()
        self.session.timeout = 30  # 30 second timeout
        
        self.test_results = {
            "production_connectivity": {"passed": 0, "failed": 0, "errors": []},
            "tm_tags_production": {"passed": 0, "failed": 0, "errors": []},
            "projects_production": {"passed": 0, "failed": 0, "errors": []},
            "installers_production": {"passed": 0, "failed": 0, "errors": []},
            "authentication_production": {"passed": 0, "failed": 0, "errors": []},
            "api_comparison": {"passed": 0, "failed": 0, "errors": []},
            "critical_issues": {"passed": 0, "failed": 0, "errors": []}
        }
        
        self.production_issues = []
        self.api_differences = []
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results with detailed error information"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                try:
                    error_msg += f" (Status: {response.status_code})"
                    if response.text:
                        error_msg += f" Response: {response.text[:500]}"
                except:
                    error_msg += " (Could not read response)"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            
            # Track critical production issues
            if "production" in category:
                self.production_issues.append(error_msg)
    
    def test_production_connectivity(self):
        """Test basic connectivity to production backend"""
        print("\n" + "="*80)
        print("🔍 TESTING PRODUCTION BACKEND CONNECTIVITY")
        print("="*80)
        
        endpoints_to_test = [
            "/projects",
            "/tm-tags", 
            "/installers",
            "/timelogs",
            "/cashflows"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                print(f"\n🌐 Testing {self.production_url}{endpoint}")
                response = self.session.get(f"{self.production_url}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            self.log_result("production_connectivity", f"GET {endpoint}", True, 
                                          f"Retrieved {len(data)} items")
                        else:
                            self.log_result("production_connectivity", f"GET {endpoint}", True, 
                                          "Valid JSON response")
                    except json.JSONDecodeError:
                        self.log_result("production_connectivity", f"GET {endpoint}", False, 
                                      "Invalid JSON response", response)
                elif response.status_code == 404:
                    self.log_result("production_connectivity", f"GET {endpoint}", False, 
                                  "Endpoint not found - API structure may be different", response)
                elif response.status_code == 500:
                    self.log_result("production_connectivity", f"GET {endpoint}", False, 
                                  "Internal server error - backend issue", response)
                else:
                    self.log_result("production_connectivity", f"GET {endpoint}", False, 
                                  f"Unexpected status code", response)
                    
            except requests.exceptions.Timeout:
                self.log_result("production_connectivity", f"GET {endpoint}", False, 
                              "Request timeout - server may be down")
            except requests.exceptions.ConnectionError:
                self.log_result("production_connectivity", f"GET {endpoint}", False, 
                              "Connection error - server unreachable")
            except Exception as e:
                self.log_result("production_connectivity", f"GET {endpoint}", False, str(e))
    
    def test_tm_tag_creation_production(self):
        """Test T&M tag creation on production - CRITICAL ISSUE #1"""
        print("\n" + "="*80)
        print("🚨 TESTING T&M TAG CREATION - CRITICAL ISSUE #1")
        print("User reports: T&M tag creation doesn't save to backend (only saves locally)")
        print("="*80)
        
        # Create realistic T&M tag data
        tm_tag_data = {
            "project_name": "Production Test Project",
            "cost_code": "PROD-TEST-001",
            "date_of_work": datetime.now().isoformat(),
            "company_name": "Test Company",
            "tm_tag_title": "Production Backend Test",
            "description_of_work": "Testing T&M tag creation on production backend",
            "labor_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Test Worker",
                    "quantity": 1,
                    "st_hours": 8.0,
                    "ot_hours": 0.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 8.0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "test@production.com"
        }
        
        try:
            print(f"🔄 Attempting to create T&M tag on production...")
            response = self.session.post(
                f"{self.production_url}/tm-tags",
                json=tm_tag_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                try:
                    created_tag = response.json()
                    tag_id = created_tag.get("id")
                    
                    if tag_id:
                        self.log_result("tm_tags_production", "T&M tag creation", True, 
                                      f"Tag created with ID: {tag_id}")
                        
                        # Verify the tag was actually saved by retrieving it
                        print(f"🔍 Verifying T&M tag was saved...")
                        verify_response = self.session.get(f"{self.production_url}/tm-tags/{tag_id}")
                        
                        if verify_response.status_code == 200:
                            self.log_result("tm_tags_production", "T&M tag persistence", True, 
                                          "Tag successfully saved and retrievable")
                        else:
                            self.log_result("tm_tags_production", "T&M tag persistence", False, 
                                          "Tag created but not retrievable - data not persisted", verify_response)
                    else:
                        self.log_result("tm_tags_production", "T&M tag creation", False, 
                                      "No ID returned in response", response)
                        
                except json.JSONDecodeError:
                    self.log_result("tm_tags_production", "T&M tag creation", False, 
                                  "Invalid JSON response", response)
            elif response.status_code == 404:
                self.log_result("tm_tags_production", "T&M tag creation", False, 
                              "T&M tags endpoint not found - API structure different", response)
            elif response.status_code == 500:
                self.log_result("tm_tags_production", "T&M tag creation", False, 
                              "Internal server error - backend issue", response)
            else:
                self.log_result("tm_tags_production", "T&M tag creation", False, 
                              f"Creation failed", response)
                
        except Exception as e:
            self.log_result("tm_tags_production", "T&M tag creation", False, str(e))
    
    def test_project_management_production(self):
        """Test project management endpoints on production"""
        print("\n" + "="*80)
        print("🏗️ TESTING PROJECT MANAGEMENT ON PRODUCTION")
        print("="*80)
        
        # Test project listing
        try:
            print(f"📋 Testing project listing...")
            response = self.session.get(f"{self.production_url}/projects")
            
            if response.status_code == 200:
                try:
                    projects = response.json()
                    if isinstance(projects, list):
                        self.log_result("projects_production", "Project listing", True, 
                                      f"Retrieved {len(projects)} projects")
                        
                        # Test project creation
                        print(f"➕ Testing project creation...")
                        project_data = {
                            "name": "Production Test Project",
                            "description": "Testing project creation on production",
                            "client_company": "Test Client",
                            "gc_email": "test@client.com",
                            "contract_amount": 50000.0,
                            "labor_rate": 95.0,
                            "start_date": datetime.now().isoformat(),
                            "address": "Test Address"
                        }
                        
                        create_response = self.session.post(
                            f"{self.production_url}/projects",
                            json=project_data,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if create_response.status_code == 200:
                            try:
                                created_project = create_response.json()
                                project_id = created_project.get("id")
                                
                                if project_id:
                                    self.log_result("projects_production", "Project creation", True, 
                                                  f"Project created with ID: {project_id}")
                                else:
                                    self.log_result("projects_production", "Project creation", False, 
                                                  "No ID returned", create_response)
                            except json.JSONDecodeError:
                                self.log_result("projects_production", "Project creation", False, 
                                              "Invalid JSON response", create_response)
                        else:
                            self.log_result("projects_production", "Project creation", False, 
                                          "Creation failed", create_response)
                    else:
                        self.log_result("projects_production", "Project listing", False, 
                                      "Response is not a list", response)
                except json.JSONDecodeError:
                    self.log_result("projects_production", "Project listing", False, 
                                  "Invalid JSON response", response)
            else:
                self.log_result("projects_production", "Project listing", False, 
                              "Failed to retrieve projects", response)
                
        except Exception as e:
            self.log_result("projects_production", "Project management", False, str(e))
    
    def test_installer_management_production(self):
        """Test installer/crew management on production"""
        print("\n" + "="*80)
        print("👷 TESTING INSTALLER/CREW MANAGEMENT ON PRODUCTION")
        print("="*80)
        
        # Test different possible endpoints for crew/installer management
        endpoints_to_test = [
            "/installers",
            "/crew",
            "/employees",
            "/workers"
        ]
        
        working_endpoint = None
        
        for endpoint in endpoints_to_test:
            try:
                print(f"🔍 Testing {endpoint} endpoint...")
                response = self.session.get(f"{self.production_url}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            self.log_result("installers_production", f"GET {endpoint}", True, 
                                          f"Retrieved {len(data)} items")
                            working_endpoint = endpoint
                            break
                    except json.JSONDecodeError:
                        self.log_result("installers_production", f"GET {endpoint}", False, 
                                      "Invalid JSON response", response)
                elif response.status_code == 404:
                    print(f"   ⚠️ {endpoint} not found")
                else:
                    self.log_result("installers_production", f"GET {endpoint}", False, 
                                  f"Unexpected status", response)
                    
            except Exception as e:
                self.log_result("installers_production", f"GET {endpoint}", False, str(e))
        
        if working_endpoint:
            # Test creation on the working endpoint
            print(f"➕ Testing creation on {working_endpoint}...")
            installer_data = {
                "name": "Test Installer",
                "cost_rate": 45.0,
                "hire_date": datetime.now().isoformat(),
                "phone": "(555) 123-4567",
                "email": "test@installer.com"
            }
            
            try:
                create_response = self.session.post(
                    f"{self.production_url}{working_endpoint}",
                    json=installer_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if create_response.status_code == 200:
                    self.log_result("installers_production", f"POST {working_endpoint}", True, 
                                  "Installer created successfully")
                else:
                    self.log_result("installers_production", f"POST {working_endpoint}", False, 
                                  "Creation failed", create_response)
                    
            except Exception as e:
                self.log_result("installers_production", f"POST {working_endpoint}", False, str(e))
        else:
            self.log_result("installers_production", "Installer endpoints", False, 
                          "No working installer/crew endpoint found")
    
    def test_authentication_production(self):
        """Test authentication system on production"""
        print("\n" + "="*80)
        print("🔐 TESTING AUTHENTICATION ON PRODUCTION")
        print("="*80)
        
        # Test admin PIN authentication (J777)
        auth_endpoints = [
            "/auth/admin",
            "/admin/login",
            "/login",
            "/auth/login"
        ]
        
        for endpoint in auth_endpoints:
            try:
                print(f"🔑 Testing authentication at {endpoint}...")
                auth_data = {"pin": "J777"}
                
                response = self.session.post(
                    f"{self.production_url}{endpoint}",
                    json=auth_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    self.log_result("authentication_production", f"Admin auth {endpoint}", True, 
                                  "Authentication successful")
                    break
                elif response.status_code == 404:
                    print(f"   ⚠️ {endpoint} not found")
                else:
                    self.log_result("authentication_production", f"Admin auth {endpoint}", False, 
                                  "Authentication failed", response)
                    
            except Exception as e:
                self.log_result("authentication_production", f"Admin auth {endpoint}", False, str(e))
    
    def compare_api_structures(self):
        """Compare API structures between production and preview"""
        print("\n" + "="*80)
        print("🔄 COMPARING PRODUCTION VS PREVIEW API STRUCTURES")
        print("="*80)
        
        endpoints_to_compare = [
            "/projects",
            "/tm-tags",
            "/installers",
            "/employees",
            "/workers"
        ]
        
        for endpoint in endpoints_to_compare:
            print(f"\n🔍 Comparing {endpoint}...")
            
            # Test production
            prod_status = None
            prod_data = None
            try:
                prod_response = self.session.get(f"{self.production_url}{endpoint}")
                prod_status = prod_response.status_code
                if prod_status == 200:
                    prod_data = prod_response.json()
            except Exception as e:
                prod_status = f"Error: {str(e)}"
            
            # Test preview
            preview_status = None
            preview_data = None
            try:
                preview_response = self.session.get(f"{self.preview_url}{endpoint}")
                preview_status = preview_response.status_code
                if preview_status == 200:
                    preview_data = preview_response.json()
            except Exception as e:
                preview_status = f"Error: {str(e)}"
            
            # Compare results
            if prod_status == 200 and preview_status == 200:
                if isinstance(prod_data, list) and isinstance(preview_data, list):
                    self.log_result("api_comparison", f"{endpoint} structure", True, 
                                  f"Both return lists - Prod: {len(prod_data)} items, Preview: {len(preview_data)} items")
                else:
                    self.log_result("api_comparison", f"{endpoint} structure", True, 
                                  "Both endpoints working but different data types")
            elif prod_status == 404 and preview_status == 200:
                self.log_result("api_comparison", f"{endpoint} availability", False, 
                              f"Endpoint missing in production but exists in preview")
                self.api_differences.append(f"{endpoint}: Missing in production")
            elif prod_status == 200 and preview_status == 404:
                self.log_result("api_comparison", f"{endpoint} availability", True, 
                              f"Endpoint exists in production but not in preview")
            elif prod_status != 200 and preview_status == 200:
                self.log_result("api_comparison", f"{endpoint} functionality", False, 
                              f"Endpoint broken in production (Status: {prod_status}) but working in preview")
                self.api_differences.append(f"{endpoint}: Broken in production ({prod_status})")
            else:
                print(f"   ℹ️ Both endpoints have issues - Prod: {prod_status}, Preview: {preview_status}")
    
    def test_pdf_functionality(self):
        """Test PDF-related functionality - CRITICAL ISSUES #2 & #3"""
        print("\n" + "="*80)
        print("📄 TESTING PDF FUNCTIONALITY - CRITICAL ISSUES #2 & #3")
        print("User reports: PDF export doesn't work, PDF preview doesn't work")
        print("="*80)
        
        # Test PDF-related endpoints
        pdf_endpoints = [
            "/pdf/generate",
            "/pdf/export",
            "/tm-tags/pdf",
            "/export/pdf",
            "/generate-pdf"
        ]
        
        for endpoint in pdf_endpoints:
            try:
                print(f"📋 Testing PDF endpoint: {endpoint}")
                
                # Test GET request first
                response = self.session.get(f"{self.production_url}{endpoint}")
                
                if response.status_code == 200:
                    self.log_result("critical_issues", f"PDF endpoint {endpoint}", True, 
                                  "Endpoint accessible")
                elif response.status_code == 404:
                    print(f"   ⚠️ {endpoint} not found")
                elif response.status_code == 405:
                    print(f"   ℹ️ {endpoint} exists but requires POST")
                    # Try POST with sample data
                    pdf_data = {
                        "tm_tag_id": "sample-id",
                        "format": "pdf"
                    }
                    post_response = self.session.post(
                        f"{self.production_url}{endpoint}",
                        json=pdf_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if post_response.status_code == 200:
                        self.log_result("critical_issues", f"PDF generation {endpoint}", True, 
                                      "PDF generation endpoint working")
                    else:
                        self.log_result("critical_issues", f"PDF generation {endpoint}", False, 
                                      "PDF generation failed", post_response)
                else:
                    self.log_result("critical_issues", f"PDF endpoint {endpoint}", False, 
                                  "Endpoint error", response)
                    
            except Exception as e:
                self.log_result("critical_issues", f"PDF endpoint {endpoint}", False, str(e))
    
    def run_comprehensive_audit(self):
        """Run the complete production audit"""
        print("🚀 STARTING COMPREHENSIVE PRODUCTION SITE FUNCTIONALITY AUDIT")
        print(f"Production Backend: {self.production_url}")
        print(f"Preview Backend: {self.preview_url}")
        print("="*80)
        
        # Run all tests
        self.test_production_connectivity()
        self.test_tm_tag_creation_production()
        self.test_project_management_production()
        self.test_installer_management_production()
        self.test_authentication_production()
        self.test_pdf_functionality()
        self.compare_api_structures()
        
        # Generate comprehensive report
        self.generate_audit_report()
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE PRODUCTION AUDIT REPORT")
        print("="*80)
        
        total_passed = sum(category["passed"] for category in self.test_results.values())
        total_failed = sum(category["failed"] for category in self.test_results.values())
        total_tests = total_passed + total_failed
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
        
        print(f"\n🔍 DETAILED RESULTS BY CATEGORY:")
        for category, results in self.test_results.items():
            total = results["passed"] + results["failed"]
            if total > 0:
                success_rate = (results["passed"] / total) * 100
                print(f"   {category.replace('_', ' ').title()}: {results['passed']}/{total} ({success_rate:.1f}%)")
        
        print(f"\n🚨 CRITICAL PRODUCTION ISSUES IDENTIFIED:")
        if self.production_issues:
            for i, issue in enumerate(self.production_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   ✅ No critical issues identified")
        
        print(f"\n🔄 API STRUCTURE DIFFERENCES:")
        if self.api_differences:
            for i, diff in enumerate(self.api_differences, 1):
                print(f"   {i}. {diff}")
        else:
            print("   ✅ No major API differences found")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if total_failed > 0:
            print("   1. 🔧 Fix failed endpoints on production backend")
            print("   2. 🔄 Ensure production backend matches preview functionality")
            print("   3. 📋 Verify database connectivity and data persistence")
            print("   4. 🔐 Check authentication system configuration")
            print("   5. 📄 Implement or fix PDF generation functionality")
        else:
            print("   ✅ Production backend appears to be functioning correctly")
        
        print("\n" + "="*80)
        print("🏁 AUDIT COMPLETE")
        print("="*80)

def main():
    """Main function to run the production audit"""
    print("🔍 COMPREHENSIVE PRODUCTION SITE FUNCTIONALITY AUDIT")
    print("Testing tm.rhinofirepro.com backend functionality")
    print("="*80)
    
    tester = ProductionAuditTester()
    tester.run_comprehensive_audit()

if __name__ == "__main__":
    main()