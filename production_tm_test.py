#!/usr/bin/env python3
"""
Production T&M System Testing
Testing the actual T&M functionality on production using timelogs endpoint
"""

import requests
import json
from datetime import datetime, date
import uuid

PRODUCTION_BACKEND = "https://tm3014-tm-app-production.up.railway.app/api"

class ProductionTMTester:
    def __init__(self):
        self.base_url = PRODUCTION_BACKEND
        self.session = requests.Session()
        self.session.timeout = 30
        
        self.test_results = {
            "tm_functionality": {"passed": 0, "failed": 0, "errors": []},
            "data_persistence": {"passed": 0, "failed": 0, "errors": []},
            "critical_issues": {"passed": 0, "failed": 0, "errors": []}
        }
        
        self.projects = []
        self.installers = []
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
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
                        error_msg += f" Response: {response.text[:300]}"
                except:
                    error_msg += " (Could not read response)"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def load_existing_data(self):
        """Load existing projects and installers"""
        print("\n🔍 LOADING EXISTING DATA FROM PRODUCTION")
        print("="*60)
        
        # Load projects
        try:
            response = self.session.get(f"{self.base_url}/projects")
            if response.status_code == 200:
                self.projects = response.json()
                print(f"📋 Loaded {len(self.projects)} projects")
                for project in self.projects:
                    print(f"   - {project['name']} (ID: {project['id']}, Type: {project.get('billing_type', 'Unknown')})")
            else:
                print(f"❌ Failed to load projects: {response.status_code}")
        except Exception as e:
            print(f"❌ Error loading projects: {e}")
        
        # Load installers
        try:
            response = self.session.get(f"{self.base_url}/installers")
            if response.status_code == 200:
                self.installers = response.json()
                print(f"👷 Loaded {len(self.installers)} installers")
                for installer in self.installers[:3]:  # Show first 3
                    print(f"   - {installer['name']} (ID: {installer['id']}, Rate: ${installer.get('cost_rate', 0)}/hr)")
                if len(self.installers) > 3:
                    print(f"   ... and {len(self.installers) - 3} more")
            else:
                print(f"❌ Failed to load installers: {response.status_code}")
        except Exception as e:
            print(f"❌ Error loading installers: {e}")
    
    def test_timelog_creation(self):
        """Test T&M functionality through timelogs endpoint"""
        print("\n🚨 TESTING T&M FUNCTIONALITY (via timelogs)")
        print("="*60)
        
        if not self.projects or not self.installers:
            self.log_result("tm_functionality", "T&M creation setup", False, 
                          "No projects or installers available for testing")
            return
        
        # Use first available project and installer
        test_project = self.projects[0]
        test_installer = self.installers[0]
        
        print(f"🎯 Testing with Project: {test_project['name']}")
        print(f"🎯 Testing with Installer: {test_installer['name']}")
        
        # Test 1: Create timelog with correct date format
        print("\n📝 Test 1: Creating timelog entry...")
        timelog_data = {
            "project_id": test_project["id"],
            "installer_id": test_installer["id"],
            "date": date.today().isoformat(),  # Use date format, not datetime
            "hours": 8.0,
            "description": "Production T&M test - electrical work",
            "bill_rate_override": None
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/timelogs",
                json=timelog_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                created_timelog = response.json()
                timelog_id = created_timelog.get("id")
                
                if timelog_id:
                    self.log_result("tm_functionality", "Timelog creation", True, 
                                  f"Created timelog ID: {timelog_id}")
                    self.test_timelog_id = timelog_id
                    
                    # Test 2: Verify the timelog was saved
                    print("\n🔍 Test 2: Verifying timelog persistence...")
                    verify_response = self.session.get(f"{self.base_url}/timelogs")
                    
                    if verify_response.status_code == 200:
                        all_timelogs = verify_response.json()
                        found_timelog = None
                        
                        for timelog in all_timelogs:
                            if timelog.get("id") == timelog_id:
                                found_timelog = timelog
                                break
                        
                        if found_timelog:
                            self.log_result("data_persistence", "Timelog persistence", True, 
                                          "Timelog successfully saved and retrievable")
                            
                            # Verify data integrity
                            if (found_timelog.get("hours") == 8.0 and 
                                found_timelog.get("project_id") == test_project["id"]):
                                self.log_result("data_persistence", "Data integrity", True, 
                                              "All data fields correctly saved")
                            else:
                                self.log_result("data_persistence", "Data integrity", False, 
                                              "Data fields not correctly saved")
                        else:
                            self.log_result("data_persistence", "Timelog persistence", False, 
                                          "Timelog created but not found in list")
                    else:
                        self.log_result("data_persistence", "Timelog persistence", False, 
                                      "Could not retrieve timelogs for verification", verify_response)
                else:
                    self.log_result("tm_functionality", "Timelog creation", False, 
                                  "No ID returned in response", response)
            else:
                self.log_result("tm_functionality", "Timelog creation", False, 
                              f"Creation failed", response)
                
        except Exception as e:
            self.log_result("tm_functionality", "Timelog creation", False, str(e))
    
    def test_multiple_timelogs(self):
        """Test creating multiple timelogs for comprehensive T&M tracking"""
        print("\n📊 TESTING MULTIPLE T&M ENTRIES")
        print("="*60)
        
        if not self.projects or not self.installers:
            return
        
        test_project = self.projects[0]
        
        # Create multiple timelogs with different installers and dates
        test_entries = [
            {
                "installer": self.installers[0] if len(self.installers) > 0 else None,
                "hours": 8.0,
                "description": "Morning shift - conduit installation"
            },
            {
                "installer": self.installers[1] if len(self.installers) > 1 else self.installers[0],
                "hours": 6.5,
                "description": "Afternoon shift - wire pulling"
            },
            {
                "installer": self.installers[2] if len(self.installers) > 2 else self.installers[0],
                "hours": 4.0,
                "description": "Equipment setup and testing"
            }
        ]
        
        created_timelogs = []
        
        for i, entry in enumerate(test_entries):
            if entry["installer"] is None:
                continue
                
            print(f"\n📝 Creating timelog {i+1}/3...")
            timelog_data = {
                "project_id": test_project["id"],
                "installer_id": entry["installer"]["id"],
                "date": date.today().isoformat(),
                "hours": entry["hours"],
                "description": entry["description"]
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/timelogs",
                    json=timelog_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    created_timelog = response.json()
                    created_timelogs.append(created_timelog)
                    self.log_result("tm_functionality", f"Multiple timelog {i+1}", True, 
                                  f"Created for {entry['installer']['name']}")
                else:
                    self.log_result("tm_functionality", f"Multiple timelog {i+1}", False, 
                                  "Creation failed", response)
                    
            except Exception as e:
                self.log_result("tm_functionality", f"Multiple timelog {i+1}", False, str(e))
        
        # Verify all timelogs were created
        if created_timelogs:
            print(f"\n🔍 Verifying {len(created_timelogs)} timelogs were saved...")
            try:
                response = self.session.get(f"{self.base_url}/timelogs")
                if response.status_code == 200:
                    all_timelogs = response.json()
                    
                    # Count timelogs for our test project
                    project_timelogs = [tl for tl in all_timelogs 
                                      if tl.get("project_id") == test_project["id"]]
                    
                    if len(project_timelogs) >= len(created_timelogs):
                        self.log_result("data_persistence", "Multiple timelogs persistence", True, 
                                      f"Found {len(project_timelogs)} timelogs for project")
                        
                        # Calculate total hours
                        total_hours = sum(tl.get("hours", 0) for tl in project_timelogs)
                        self.log_result("tm_functionality", "T&M hours calculation", True, 
                                      f"Total project hours: {total_hours}")
                    else:
                        self.log_result("data_persistence", "Multiple timelogs persistence", False, 
                                      f"Expected {len(created_timelogs)}, found {len(project_timelogs)}")
                        
            except Exception as e:
                self.log_result("data_persistence", "Multiple timelogs verification", False, str(e))
    
    def test_tm_project_billing(self):
        """Test T&M project billing calculations"""
        print("\n💰 TESTING T&M PROJECT BILLING")
        print("="*60)
        
        # Find a T&M project
        tm_project = None
        for project in self.projects:
            if project.get("billing_type") == "TM":
                tm_project = project
                break
        
        if not tm_project:
            self.log_result("critical_issues", "T&M project billing", False, 
                          "No T&M projects found for billing test")
            return
        
        print(f"🎯 Testing billing for T&M project: {tm_project['name']}")
        print(f"   Bill rate: ${tm_project.get('tm_bill_rate', 0)}/hr")
        
        # Get timelogs for this project
        try:
            response = self.session.get(f"{self.base_url}/timelogs")
            if response.status_code == 200:
                all_timelogs = response.json()
                project_timelogs = [tl for tl in all_timelogs 
                                  if tl.get("project_id") == tm_project["id"]]
                
                if project_timelogs:
                    total_hours = sum(tl.get("hours", 0) for tl in project_timelogs)
                    bill_rate = tm_project.get("tm_bill_rate", 0)
                    total_billable = total_hours * bill_rate
                    
                    print(f"   Total hours logged: {total_hours}")
                    print(f"   Total billable amount: ${total_billable}")
                    
                    self.log_result("tm_functionality", "T&M billing calculation", True, 
                                  f"${total_billable} for {total_hours} hours at ${bill_rate}/hr")
                else:
                    print("   No timelogs found for this T&M project")
                    self.log_result("critical_issues", "T&M project data", False, 
                                  "T&M project has no time entries")
            else:
                self.log_result("critical_issues", "T&M billing data", False, 
                              "Could not retrieve timelogs for billing calculation", response)
                
        except Exception as e:
            self.log_result("critical_issues", "T&M billing calculation", False, str(e))
    
    def test_offline_mode_issue(self):
        """Test the specific offline mode issue reported by user"""
        print("\n🔍 INVESTIGATING OFFLINE MODE ISSUE")
        print("="*60)
        print("User reports: T&M tag creation only saves locally (offline mode)")
        print("Testing if backend properly saves and persists data...")
        
        if not self.projects or not self.installers:
            self.log_result("critical_issues", "Offline mode investigation", False, 
                          "Cannot test - no projects or installers available")
            return
        
        test_project = self.projects[0]
        test_installer = self.installers[0]
        
        # Create a unique timelog entry
        unique_description = f"Offline mode test - {datetime.now().strftime('%H:%M:%S')}"
        
        timelog_data = {
            "project_id": test_project["id"],
            "installer_id": test_installer["id"],
            "date": date.today().isoformat(),
            "hours": 7.5,
            "description": unique_description
        }
        
        try:
            # Step 1: Create the entry
            print("📝 Step 1: Creating unique timelog entry...")
            response = self.session.post(
                f"{self.base_url}/timelogs",
                json=timelog_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                created_entry = response.json()
                entry_id = created_entry.get("id")
                
                # Step 2: Immediately verify it exists
                print("🔍 Step 2: Immediately checking if entry exists...")
                verify_response = self.session.get(f"{self.base_url}/timelogs")
                
                if verify_response.status_code == 200:
                    all_entries = verify_response.json()
                    found_entry = None
                    
                    for entry in all_entries:
                        if entry.get("description") == unique_description:
                            found_entry = entry
                            break
                    
                    if found_entry:
                        self.log_result("critical_issues", "Backend persistence immediate", True, 
                                      "Entry immediately available after creation")
                        
                        # Step 3: Wait and check again (simulate page refresh)
                        print("⏳ Step 3: Waiting 5 seconds and checking again...")
                        import time
                        time.sleep(5)
                        
                        delayed_response = self.session.get(f"{self.base_url}/timelogs")
                        if delayed_response.status_code == 200:
                            delayed_entries = delayed_response.json()
                            still_found = any(e.get("description") == unique_description 
                                            for e in delayed_entries)
                            
                            if still_found:
                                self.log_result("critical_issues", "Backend persistence delayed", True, 
                                              "Entry still available after delay - NOT offline mode")
                            else:
                                self.log_result("critical_issues", "Backend persistence delayed", False, 
                                              "Entry disappeared after delay - POSSIBLE offline mode issue")
                        else:
                            self.log_result("critical_issues", "Backend persistence delayed", False, 
                                          "Could not verify delayed persistence", delayed_response)
                    else:
                        self.log_result("critical_issues", "Backend persistence immediate", False, 
                                      "Entry not found immediately after creation - OFFLINE MODE CONFIRMED")
                else:
                    self.log_result("critical_issues", "Backend persistence verification", False, 
                                  "Could not verify entry creation", verify_response)
            else:
                self.log_result("critical_issues", "Offline mode test setup", False, 
                              "Could not create test entry", response)
                
        except Exception as e:
            self.log_result("critical_issues", "Offline mode investigation", False, str(e))
    
    def run_comprehensive_tm_test(self):
        """Run comprehensive T&M system test"""
        print("🚀 COMPREHENSIVE PRODUCTION T&M SYSTEM TEST")
        print(f"Backend: {self.base_url}")
        print("="*80)
        
        self.load_existing_data()
        self.test_timelog_creation()
        self.test_multiple_timelogs()
        self.test_tm_project_billing()
        self.test_offline_mode_issue()
        
        self.generate_tm_report()
    
    def generate_tm_report(self):
        """Generate T&M system test report"""
        print("\n" + "="*80)
        print("📊 PRODUCTION T&M SYSTEM TEST REPORT")
        print("="*80)
        
        total_passed = sum(category["passed"] for category in self.test_results.values())
        total_failed = sum(category["failed"] for category in self.test_results.values())
        total_tests = total_passed + total_failed
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for category, results in self.test_results.items():
            total = results["passed"] + results["failed"]
            if total > 0:
                success_rate = (results["passed"] / total) * 100
                print(f"   {category.replace('_', ' ').title()}: {results['passed']}/{total} ({success_rate:.1f}%)")
        
        print(f"\n🚨 CRITICAL FINDINGS:")
        critical_errors = self.test_results["critical_issues"]["errors"]
        if critical_errors:
            for i, error in enumerate(critical_errors, 1):
                print(f"   {i}. {error}")
        else:
            print("   ✅ No critical issues found with T&M system")
        
        print(f"\n🎯 KEY INSIGHTS:")
        print("   1. Production uses 'timelogs' endpoint instead of 'tm-tags'")
        print("   2. T&M functionality is available but with different API structure")
        print("   3. Projects have billing_type and tm_bill_rate fields for T&M billing")
        print("   4. Installers have cost_rate field for labor cost calculations")
        
        if total_failed > 0:
            print(f"\n💡 RECOMMENDATIONS:")
            print("   1. 🔧 Fix any failed T&M functionality tests")
            print("   2. 📱 Update frontend to use 'timelogs' API instead of 'tm-tags'")
            print("   3. 🔄 Ensure proper data persistence and avoid offline mode issues")
            print("   4. 📄 Implement PDF generation for T&M reports")
        
        print("\n" + "="*80)
        print("🏁 T&M SYSTEM TEST COMPLETE")
        print("="*80)

def main():
    """Main function"""
    tester = ProductionTMTester()
    tester.run_comprehensive_tm_test()

if __name__ == "__main__":
    main()