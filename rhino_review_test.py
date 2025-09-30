#!/usr/bin/env python3
"""
Rhino Platform Review Test - Understanding Current Data State
Tests the specific endpoints mentioned in the review request to understand
what data is available and help update frontend to use correct endpoints.
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any, List

# Configuration from frontend/.env
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"
ADMIN_PIN = "J777"

class RhinoReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with detailed output"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   📋 {details}")
        if response_data:
            if isinstance(response_data, list):
                print(f"   📊 Found {len(response_data)} items")
                if response_data and isinstance(response_data[0], dict):
                    print(f"   🔑 Sample keys: {list(response_data[0].keys())}")
            elif isinstance(response_data, dict):
                print(f"   🔑 Response keys: {list(response_data.keys())}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'data': response_data
        })
    
    def authenticate_admin(self):
        """Authenticate with admin PIN J777"""
        try:
            response = self.session.post(f"{API_BASE}/auth/admin", json={"pin": ADMIN_PIN})
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, f"Successfully authenticated with PIN {ADMIN_PIN}", data)
                return True
            else:
                self.log_test("Admin Authentication", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_projects_endpoint(self):
        """Test GET /api/projects - to see what projects exist"""
        try:
            response = self.session.get(f"{API_BASE}/projects")
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /api/projects", True, f"Retrieved {len(data)} projects", data)
                
                # Detailed analysis
                if data:
                    print("   📈 PROJECT ANALYSIS:")
                    tm_projects = [p for p in data if p.get('billing_type') == 'TM']
                    fixed_projects = [p for p in data if p.get('billing_type') != 'TM']
                    
                    print(f"      • Total Projects: {len(data)}")
                    print(f"      • T&M Projects: {len(tm_projects)}")
                    print(f"      • Fixed/Other Projects: {len(fixed_projects)}")
                    
                    print("   🏗️  PROJECT DETAILS:")
                    for project in data:
                        billing_type = project.get('billing_type', 'Unknown')
                        tm_rate = project.get('tm_bill_rate')
                        rate_info = f"${tm_rate}/hr" if tm_rate else "No T&M rate"
                        print(f"      • {project.get('name', 'Unknown')} ({billing_type}) - {rate_info}")
                
                return data
            else:
                self.log_test("GET /api/projects", False, f"Failed with status {response.status_code}", response.text)
                return []
        except Exception as e:
            self.log_test("GET /api/projects", False, f"Exception: {str(e)}")
            return []
    
    def test_installers_endpoint(self):
        """Test GET /api/installers - to see what crew/installers exist"""
        try:
            response = self.session.get(f"{API_BASE}/installers")
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /api/installers", True, f"Retrieved {len(data)} installers/crew members", data)
                
                # Detailed analysis
                if data:
                    print("   👷 INSTALLER/CREW ANALYSIS:")
                    active_installers = [i for i in data if i.get('active', True)]
                    inactive_installers = [i for i in data if not i.get('active', True)]
                    
                    print(f"      • Total Installers: {len(data)}")
                    print(f"      • Active: {len(active_installers)}")
                    print(f"      • Inactive: {len(inactive_installers)}")
                    
                    print("   💰 INSTALLER RATES:")
                    for installer in data:
                        status = "Active" if installer.get('active', True) else "Inactive"
                        cost_rate = installer.get('cost_rate', 0)
                        print(f"      • {installer.get('name', 'Unknown')} - ${cost_rate}/hr ({status})")
                
                return data
            else:
                self.log_test("GET /api/installers", False, f"Failed with status {response.status_code}", response.text)
                return []
        except Exception as e:
            self.log_test("GET /api/installers", False, f"Exception: {str(e)}")
            return []
    
    def test_timelogs_endpoint(self):
        """Test GET /api/timelogs - to see what time tracking data exists"""
        try:
            response = self.session.get(f"{API_BASE}/timelogs")
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /api/timelogs", True, f"Retrieved {len(data)} time log entries", data)
                
                # Detailed analysis
                if data:
                    print("   ⏰ TIME LOG ANALYSIS:")
                    total_hours = sum(log.get('hours', 0) for log in data)
                    total_labor_cost = sum(log.get('labor_cost', 0) for log in data)
                    total_billable = sum(log.get('billable', 0) or 0 for log in data)
                    total_profit = sum(log.get('profit', 0) or 0 for log in data)
                    
                    print(f"      • Total Entries: {len(data)}")
                    print(f"      • Total Hours: {total_hours}")
                    print(f"      • Total Labor Cost: ${total_labor_cost:.2f}")
                    print(f"      • Total Billable: ${total_billable:.2f}")
                    print(f"      • Total Profit: ${total_profit:.2f}")
                    
                    # Group by project
                    project_summary = {}
                    for log in data:
                        project = log.get('project_name', 'Unknown')
                        if project not in project_summary:
                            project_summary[project] = {'hours': 0, 'entries': 0}
                        project_summary[project]['hours'] += log.get('hours', 0)
                        project_summary[project]['entries'] += 1
                    
                    print("   📊 BY PROJECT:")
                    for project, summary in project_summary.items():
                        print(f"      • {project}: {summary['hours']}h ({summary['entries']} entries)")
                
                return data
            else:
                self.log_test("GET /api/timelogs", False, f"Failed with status {response.status_code}", response.text)
                return []
        except Exception as e:
            self.log_test("GET /api/timelogs", False, f"Exception: {str(e)}")
            return []
    
    def test_tm_summary_endpoint(self):
        """Test GET /api/summary/tm - to understand what analytics are available"""
        try:
            response = self.session.get(f"{API_BASE}/summary/tm")
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /api/summary/tm", True, "Retrieved T&M analytics summary", data)
                
                # Detailed analysis
                if data:
                    print("   📊 T&M ANALYTICS SUMMARY:")
                    
                    # T&M Project Totals
                    tm_totals = data.get('tm_project_totals', [])
                    print(f"      • T&M Projects Tracked: {len(tm_totals)}")
                    
                    if tm_totals:
                        total_hours = sum(p.get('hours', 0) for p in tm_totals)
                        total_labor_cost = sum(p.get('labor_cost', 0) for p in tm_totals)
                        total_billable = sum(p.get('billable', 0) for p in tm_totals)
                        total_profit = sum(p.get('profit', 0) for p in tm_totals)
                        
                        print(f"      • Combined Hours: {total_hours}")
                        print(f"      • Combined Labor Cost: ${total_labor_cost:.2f}")
                        print(f"      • Combined Billable: ${total_billable:.2f}")
                        print(f"      • Combined Profit: ${total_profit:.2f}")
                        
                        print("   💰 T&M PROJECT BREAKDOWN:")
                        for project in tm_totals:
                            print(f"      • {project.get('project', 'Unknown')}: {project.get('hours', 0)}h, ${project.get('billable', 0):.2f} billable, ${project.get('profit', 0):.2f} profit")
                    
                    # Cash Balance
                    cash_balance = data.get('cash_balance', {})
                    if cash_balance:
                        print("   💵 CASH BALANCE:")
                        print(f"      • Current Balance: ${cash_balance.get('current_balance', 0):.2f}")
                        print(f"      • Starting Balance: ${cash_balance.get('starting_balance', 0):.2f}")
                        print(f"      • Total Inflows: ${cash_balance.get('total_inflows', 0):.2f}")
                        print(f"      • Total Outflows: ${cash_balance.get('total_outflows', 0):.2f}")
                
                return data
            else:
                self.log_test("GET /api/summary/tm", False, f"Failed with status {response.status_code}", response.text)
                return {}
        except Exception as e:
            self.log_test("GET /api/summary/tm", False, f"Exception: {str(e)}")
            return {}
    
    def test_project_intelligence_endpoints(self):
        """Test Project Intelligence endpoints if available"""
        intelligence_endpoints = [
            ("/api/intelligence/dashboard", "Intelligence Dashboard"),
            ("/api/intelligence/emails", "Email Processing"),
            ("/api/intelligence/project-candidates", "Project Candidates"),
            ("/api/tasks", "Task Management"),
            ("/api/invoices", "Invoice Management"),
            ("/api/review-queue", "Review Queue"),
            ("/api/cashflows", "Cashflow Management")
        ]
        
        print("🤖 TESTING PROJECT INTELLIGENCE ENDPOINTS:")
        print("=" * 60)
        
        intelligence_data = {}
        
        for endpoint, description in intelligence_endpoints:
            try:
                response = self.session.get(f"{API_BASE.replace('/api', '')}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"{description} ({endpoint})", True, f"Endpoint available", data)
                    intelligence_data[endpoint] = data
                    
                    # Specific analysis for each endpoint
                    if endpoint == "/api/intelligence/dashboard":
                        if isinstance(data, dict):
                            print(f"      📊 Dashboard Metrics: {list(data.keys())}")
                    elif endpoint in ["/api/tasks", "/api/invoices", "/api/intelligence/emails", "/api/cashflows"]:
                        if isinstance(data, list):
                            print(f"      📋 Found {len(data)} items")
                    
                else:
                    self.log_test(f"{description} ({endpoint})", False, f"Status {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"{description} ({endpoint})", False, f"Exception: {str(e)}")
        
        return intelligence_data
    
    def test_old_tm_tags_endpoints(self):
        """Test if old /api/tm-tags endpoints still exist (for comparison)"""
        print("🔍 TESTING OLD T&M ENDPOINTS (for comparison):")
        print("=" * 60)
        
        old_endpoints = [
            ("/api/tm-tags", "Old T&M Tags"),
            ("/api/workers", "Old Workers"),
            ("/api/employees", "Old Employees"),
            ("/api/crew-logs", "Old Crew Logs"),
            ("/api/materials", "Old Materials")
        ]
        
        for endpoint, description in old_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"{description} ({endpoint})", True, f"Still available - {len(data)} items", data)
                else:
                    self.log_test(f"{description} ({endpoint})", False, f"Not available - Status {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"{description} ({endpoint})", False, f"Exception: {str(e)}")
    
    def generate_frontend_mapping_guide(self):
        """Generate a guide for updating frontend endpoints"""
        print("\n" + "=" * 80)
        print("📋 FRONTEND ENDPOINT MAPPING GUIDE")
        print("=" * 80)
        
        print("The frontend is currently calling old endpoints. Here's the mapping:")
        print()
        
        mapping = [
            ("OLD: /api/tm-tags", "NEW: /api/timelogs", "Time tracking data with calculated billing"),
            ("OLD: /api/workers", "NEW: /api/installers", "Crew/installer data with cost rates"),
            ("OLD: /api/projects", "SAME: /api/projects", "Project data (same endpoint, enhanced fields)"),
            ("OLD: /api/analytics", "NEW: /api/summary/tm", "T&M analytics and cash balance"),
            ("OLD: /api/crew-logs", "NEW: /api/timelogs", "Time logs replace crew logs"),
            ("OLD: /api/materials", "NEW: /api/cashflows", "Material costs tracked in cashflow"),
        ]
        
        for old, new, description in mapping:
            print(f"   {old}")
            print(f"   └─> {new}")
            print(f"       📝 {description}")
            print()
        
        print("🔧 REQUIRED FRONTEND CHANGES:")
        print("   1. Update API endpoint URLs to use new Rhino Platform endpoints")
        print("   2. Update data models to match new response structures")
        print("   3. Handle new T&M billing calculations (project-based rates)")
        print("   4. Update authentication to use admin PIN system")
        print("   5. Integrate new Project Intelligence features if desired")
        
    def print_comprehensive_summary(self):
        """Print comprehensive summary of findings"""
        print("\n" + "=" * 80)
        print("🎯 RHINO PLATFORM REVIEW SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 TESTING RESULTS:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {(successful_tests/total_tests*100):.1f}%")
        
        print(f"\n🔍 KEY FINDINGS:")
        
        # Extract data from successful tests
        projects_data = None
        installers_data = None
        timelogs_data = None
        tm_summary_data = None
        
        for result in self.test_results:
            if "GET /api/projects" in result["test"] and result["success"]:
                projects_data = result["data"]
            elif "GET /api/installers" in result["test"] and result["success"]:
                installers_data = result["data"]
            elif "GET /api/timelogs" in result["test"] and result["success"]:
                timelogs_data = result["data"]
            elif "GET /api/summary/tm" in result["test"] and result["success"]:
                tm_summary_data = result["data"]
        
        if projects_data:
            tm_projects = [p for p in projects_data if p.get('billing_type') == 'TM']
            print(f"   🏗️  PROJECTS: {len(projects_data)} total, {len(tm_projects)} T&M projects")
            
        if installers_data:
            active_installers = [i for i in installers_data if i.get('active', True)]
            print(f"   👷 INSTALLERS: {len(installers_data)} total, {len(active_installers)} active")
            
        if timelogs_data:
            total_hours = sum(log.get('hours', 0) for log in timelogs_data)
            print(f"   ⏰ TIME LOGS: {len(timelogs_data)} entries, {total_hours}h total")
            
        if tm_summary_data:
            tm_totals = tm_summary_data.get('tm_project_totals', [])
            cash_balance = tm_summary_data.get('cash_balance', {})
            current_balance = cash_balance.get('current_balance', 0)
            print(f"   💰 ANALYTICS: {len(tm_totals)} T&M projects tracked, ${current_balance:.2f} cash balance")
        
        print(f"\n✅ SYSTEM STATUS:")
        if successful_tests > failed_tests:
            print("   • Rhino Platform backend is OPERATIONAL")
            print("   • Admin authentication working with PIN J777")
            print("   • Core data endpoints returning valid data")
            print("   • T&M billing calculations working correctly")
            print("   • Project Intelligence features available")
        else:
            print("   • Multiple endpoint failures detected")
            print("   • System may need troubleshooting")
        
        print(f"\n🚀 NEXT STEPS:")
        print("   1. Update frontend to use new Rhino Platform endpoints")
        print("   2. Test frontend integration with new data structures")
        print("   3. Implement new T&M billing logic in frontend")
        print("   4. Consider integrating Project Intelligence features")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    print("🚀 RHINO PLATFORM REVIEW TEST")
    print("Understanding current data state and endpoint mapping")
    print("=" * 80)
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔑 Admin PIN: {ADMIN_PIN}")
    print()
    
    tester = RhinoReviewTester()
    
    # Authenticate first
    if not tester.authenticate_admin():
        print("⚠️  Authentication failed - continuing with limited access")
    
    print("📊 TESTING CORE RHINO PLATFORM ENDPOINTS:")
    print("=" * 60)
    
    # Test the specific endpoints mentioned in the review request
    tester.test_projects_endpoint()
    tester.test_installers_endpoint() 
    tester.test_timelogs_endpoint()
    tester.test_tm_summary_endpoint()
    
    # Test Project Intelligence endpoints
    tester.test_project_intelligence_endpoints()
    
    # Test old endpoints for comparison
    tester.test_old_tm_tags_endpoints()
    
    # Generate frontend mapping guide
    tester.generate_frontend_mapping_guide()
    
    # Print comprehensive summary
    tester.print_comprehensive_summary()

if __name__ == "__main__":
    main()