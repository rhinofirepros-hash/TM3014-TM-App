#!/usr/bin/env python3
"""
PIN Authentication Investigation Script
Investigating the PIN "2024" authentication issue reported in frontend testing
"""

import requests
import json
from datetime import datetime
import uuid
import sys

# Get backend URL from frontend .env file
BACKEND_URL = "https://fireprotect-app.preview.emergentagent.com/api"

class PINInvestigator:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.found_pins = []
        self.projects = []
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            print(f"✅ {test_name}: {message}")
        else:
            error_msg = f"❌ {test_name}: {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            print(error_msg)
    
    def investigate_current_projects_and_pins(self):
        """Step 1: Check current projects and their PINs"""
        print("\n=== STEP 1: Investigating Current Projects and PINs ===")
        
        try:
            # Get all projects
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                self.projects = response.json()
                self.log_result("Get Projects", True, f"Retrieved {len(self.projects)} projects")
                
                # Display project information
                print(f"\nFound {len(self.projects)} projects:")
                for i, project in enumerate(self.projects[:10], 1):  # Show first 10 projects
                    print(f"  {i}. {project.get('name', 'Unnamed')} (ID: {project.get('id', 'No ID')})")
                    print(f"     Client: {project.get('client_company', 'No client')}")
                    print(f"     Status: {project.get('status', 'No status')}")
                    if 'gc_pin' in project:
                        print(f"     GC PIN: {project.get('gc_pin', 'No PIN')}")
                    print()
                
                return True
            else:
                self.log_result("Get Projects", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Get Projects", False, str(e))
            return False
    
    def check_project_pins_detailed(self):
        """Step 2: Check detailed PIN information for first few projects"""
        print("\n=== STEP 2: Checking Detailed PIN Information ===")
        
        if not self.projects:
            print("❌ No projects available to check PINs")
            return False
        
        # Check first 5 projects for their PINs
        projects_to_check = self.projects[:5]
        
        for i, project in enumerate(projects_to_check, 1):
            project_id = project.get('id')
            project_name = project.get('name', 'Unnamed')
            
            print(f"\n--- Checking Project {i}: {project_name} ---")
            
            try:
                # Check if project has gc-pin endpoint
                response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
                
                if response.status_code == 200:
                    pin_data = response.json()
                    pin = pin_data.get('gc_pin', 'No PIN found')
                    pin_used = pin_data.get('gc_pin_used', 'Unknown')
                    
                    self.found_pins.append({
                        'project_id': project_id,
                        'project_name': project_name,
                        'pin': pin,
                        'pin_used': pin_used
                    })
                    
                    self.log_result(f"Project {i} PIN", True, f"PIN: {pin}, Used: {pin_used}")
                    
                    # Special check for PIN "2024"
                    if pin == "2024":
                        print(f"🎯 FOUND PIN '2024' in project: {project_name} (ID: {project_id})")
                        
                else:
                    # Try to get PIN from project data directly
                    pin = project.get('gc_pin', 'No PIN in project data')
                    pin_used = project.get('gc_pin_used', 'Unknown')
                    
                    if pin != 'No PIN in project data':
                        self.found_pins.append({
                            'project_id': project_id,
                            'project_name': project_name,
                            'pin': pin,
                            'pin_used': pin_used
                        })
                        
                        self.log_result(f"Project {i} PIN (from project data)", True, f"PIN: {pin}, Used: {pin_used}")
                        
                        # Special check for PIN "2024"
                        if pin == "2024":
                            print(f"🎯 FOUND PIN '2024' in project: {project_name} (ID: {project_id})")
                    else:
                        self.log_result(f"Project {i} PIN", False, f"No PIN endpoint and no PIN in project data", response)
                        
            except Exception as e:
                self.log_result(f"Project {i} PIN", False, str(e))
        
        # Summary of found PINs
        print(f"\n=== PIN SUMMARY ===")
        print(f"Found {len(self.found_pins)} projects with PINs:")
        for pin_info in self.found_pins:
            status = "🔴 USED" if pin_info['pin_used'] else "🟢 AVAILABLE"
            print(f"  PIN: {pin_info['pin']} - {pin_info['project_name']} ({status})")
        
        return len(self.found_pins) > 0
    
    def test_pin_authentication(self):
        """Step 3: Test PIN authentication with found PINs"""
        print("\n=== STEP 3: Testing PIN Authentication ===")
        
        if not self.found_pins:
            print("❌ No PINs available to test")
            return False
        
        # Test authentication with each found PIN
        for pin_info in self.found_pins:
            project_id = pin_info['project_id']
            pin = pin_info['pin']
            project_name = pin_info['project_name']
            pin_used = pin_info['pin_used']
            
            print(f"\n--- Testing PIN: {pin} for project: {project_name} ---")
            
            if pin_used:
                print(f"⚠️  PIN {pin} is marked as USED - testing anyway")
            
            try:
                # Test the simplified GC login endpoint
                login_data = {
                    "projectId": project_id,  # Use camelCase as expected by backend
                    "pin": pin
                }
                
                response = self.session.post(
                    f"{self.base_url}/gc/login-simple",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    login_result = response.json()
                    self.log_result(f"PIN {pin} Authentication", True, f"Login successful: {login_result}")
                    
                    # If this was PIN "2024", we found the issue
                    if pin == "2024":
                        print(f"🎯 PIN '2024' AUTHENTICATION SUCCESSFUL!")
                        print(f"   Project: {project_name}")
                        print(f"   Project ID: {project_id}")
                        print(f"   Response: {login_result}")
                        
                elif response.status_code == 401:
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get('detail', 'Authentication failed')
                    self.log_result(f"PIN {pin} Authentication", False, f"401 Unauthorized: {error_message}")
                    
                    # If this was PIN "2024", we found why it's failing
                    if pin == "2024":
                        print(f"🎯 PIN '2024' AUTHENTICATION FAILED!")
                        print(f"   Project: {project_name}")
                        print(f"   Project ID: {project_id}")
                        print(f"   Error: {error_message}")
                        print(f"   PIN Used Status: {pin_used}")
                        
                else:
                    self.log_result(f"PIN {pin} Authentication", False, f"HTTP {response.status_code}", response)
                    
            except Exception as e:
                self.log_result(f"PIN {pin} Authentication", False, str(e))
        
        return True
    
    def search_for_pin_2024(self):
        """Step 4: Specifically search for PIN "2024" """
        print("\n=== STEP 4: Searching Specifically for PIN '2024' ===")
        
        found_2024 = False
        
        # Check all projects for PIN "2024"
        for project in self.projects:
            project_id = project.get('id')
            project_name = project.get('name', 'Unnamed')
            pin = project.get('gc_pin')
            
            if pin == "2024":
                found_2024 = True
                pin_used = project.get('gc_pin_used', False)
                
                print(f"🎯 FOUND PIN '2024'!")
                print(f"   Project: {project_name}")
                print(f"   Project ID: {project_id}")
                print(f"   PIN Used: {pin_used}")
                print(f"   Client: {project.get('client_company', 'No client')}")
                print(f"   Status: {project.get('status', 'No status')}")
                
                # Test authentication with this PIN
                print(f"\n--- Testing PIN '2024' Authentication ---")
                try:
                    login_data = {
                        "projectId": project_id,  # Use camelCase as expected by backend
                        "pin": "2024"
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/gc/login-simple",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        login_result = response.json()
                        print(f"✅ PIN '2024' authentication SUCCESSFUL!")
                        print(f"   Response: {login_result}")
                    else:
                        error_data = response.json() if response.text else {}
                        error_message = error_data.get('detail', 'Authentication failed')
                        print(f"❌ PIN '2024' authentication FAILED!")
                        print(f"   Status: {response.status_code}")
                        print(f"   Error: {error_message}")
                        
                        # If PIN is used, suggest regenerating it
                        if "already used" in error_message.lower():
                            print(f"💡 SOLUTION: PIN '2024' has been used. Need to regenerate or use a fresh PIN.")
                        
                except Exception as e:
                    print(f"❌ Error testing PIN '2024': {e}")
        
        if not found_2024:
            print(f"❌ PIN '2024' NOT FOUND in any project")
            print(f"💡 SOLUTION: Need to create a project with PIN '2024' or update an existing project")
            
            # Suggest creating a project with PIN "2024"
            self.suggest_create_project_with_pin_2024()
        
        return found_2024
    
    def suggest_create_project_with_pin_2024(self):
        """Step 5: Suggest creating a project with PIN '2024' """
        print("\n=== STEP 5: Creating Project with PIN '2024' ===")
        
        # Create a test project
        project_data = {
            "name": "PIN 2024 Test Project",
            "description": "Test project created for PIN 2024 authentication testing",
            "client_company": "Test Client for PIN 2024",
            "gc_email": "test@pin2024.com",
            "project_type": "full_project",
            "contract_amount": 100000.00,
            "labor_rate": 95.0,
            "project_manager": "Jesus Garcia",
            "start_date": datetime.now().isoformat(),
            "address": "Test Address for PIN 2024"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                project_id = project.get('id')
                auto_pin = project.get('gc_pin', 'No PIN generated')
                
                print(f"✅ Created test project: {project.get('name')}")
                print(f"   Project ID: {project_id}")
                print(f"   Auto-generated PIN: {auto_pin}")
                
                # Now try to update the project to have PIN "2024"
                # Note: This might require direct database access or a special endpoint
                print(f"\n💡 RECOMMENDATION:")
                print(f"   The system auto-generates unique PINs (got: {auto_pin})")
                print(f"   To use PIN '2024', you would need to:")
                print(f"   1. Update the project directly in MongoDB to set gc_pin='2024'")
                print(f"   2. Or modify the PIN generation logic to allow specific PINs")
                print(f"   3. Or use the auto-generated PIN '{auto_pin}' for testing instead")
                
                # Test with the auto-generated PIN
                print(f"\n--- Testing with auto-generated PIN '{auto_pin}' ---")
                login_data = {
                    "project_id": project_id,
                    "pin": auto_pin
                }
                
                auth_response = self.session.post(
                    f"{self.base_url}/gc/login-simple",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if auth_response.status_code == 200:
                    print(f"✅ Auto-generated PIN '{auto_pin}' works for authentication!")
                    print(f"   Use this PIN for frontend testing instead of '2024'")
                else:
                    print(f"❌ Auto-generated PIN '{auto_pin}' failed authentication")
                
                return project_id, auto_pin
                
            else:
                self.log_result("Create test project", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Create test project", False, str(e))
        
        return None, None
    
    def run_full_investigation(self):
        """Run the complete PIN investigation"""
        print("🔍 Starting PIN Authentication Investigation")
        print("=" * 60)
        
        # Step 1: Get current projects
        if not self.investigate_current_projects_and_pins():
            print("❌ Failed to get projects. Cannot continue investigation.")
            return False
        
        # Step 2: Check detailed PIN information
        if not self.check_project_pins_detailed():
            print("❌ Failed to get PIN information. Cannot continue investigation.")
            return False
        
        # Step 3: Test PIN authentication
        self.test_pin_authentication()
        
        # Step 4: Search specifically for PIN "2024"
        found_2024 = self.search_for_pin_2024()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🔍 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        print(f"📊 Total projects found: {len(self.projects)}")
        print(f"📊 Projects with PINs: {len(self.found_pins)}")
        
        if self.found_pins:
            print(f"\n📋 Available PINs for testing:")
            for pin_info in self.found_pins:
                status = "🔴 USED" if pin_info['pin_used'] else "🟢 AVAILABLE"
                print(f"   PIN: {pin_info['pin']} - {pin_info['project_name']} ({status})")
        
        if found_2024:
            print(f"\n🎯 PIN '2024' STATUS: FOUND")
        else:
            print(f"\n🎯 PIN '2024' STATUS: NOT FOUND")
            print(f"💡 RECOMMENDATION: Use one of the available PINs above for frontend testing")
        
        print(f"\n🔧 NEXT STEPS:")
        if found_2024:
            print(f"   1. Check if PIN '2024' is marked as used")
            print(f"   2. If used, regenerate the PIN or use a different project")
            print(f"   3. Test frontend with the correct project ID and PIN combination")
        else:
            print(f"   1. Use one of the available PINs listed above")
            print(f"   2. Update frontend test to use an existing PIN")
            print(f"   3. Or create a new project and use its auto-generated PIN")
        
        return True

def main():
    """Main function to run the PIN investigation"""
    investigator = PINInvestigator()
    
    try:
        investigator.run_full_investigation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Investigation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Investigation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()