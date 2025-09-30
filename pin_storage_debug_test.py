#!/usr/bin/env python3
"""
PIN Storage Debug Test - Comprehensive Step-by-Step Analysis
Tests the exact issue with PIN storage and retrieval mismatch
"""

import requests
import json
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://firepro-auth-hub.preview.emergentagent.com/api"

class PINStorageDebugger:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_step(self, step_num, step_name, success, message="", data=None):
        """Log each step with detailed information"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {step_name}")
        print(f"Status: {status}")
        print(f"Message: {message}")
        if data:
            print(f"Data: {json.dumps(data, indent=2, default=str)}")
        print(f"{'='*60}")
        
        self.test_results.append({
            "step": step_num,
            "name": step_name,
            "success": success,
            "message": message,
            "data": data
        })
        
    def step_1_before_pin_generation(self, project_id):
        """STEP 1 - Before PIN generation: GET /api/projects/{project_id} and show current gc_pin value"""
        print(f"\n🔍 STEP 1: Checking project {project_id} BEFORE PIN generation")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}")
            
            if response.status_code == 200:
                project_data = response.json()
                current_gc_pin = project_data.get("gc_pin", "NOT_SET")
                gc_pin_used = project_data.get("gc_pin_used", "NOT_SET")
                
                self.log_step(
                    1, 
                    "Before PIN Generation - Check Current State",
                    True,
                    f"Project found. Current gc_pin: {current_gc_pin}, gc_pin_used: {gc_pin_used}",
                    {
                        "project_id": project_id,
                        "project_name": project_data.get("name", "Unknown"),
                        "gc_pin": current_gc_pin,
                        "gc_pin_used": gc_pin_used,
                        "full_project_data": project_data
                    }
                )
                return project_data
            else:
                self.log_step(
                    1,
                    "Before PIN Generation - Check Current State", 
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"project_id": project_id, "status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_step(1, "Before PIN Generation - Check Current State", False, str(e))
            return None
    
    def step_2_generate_pin(self, project_id):
        """STEP 2 - Generate PIN: GET /api/projects/{project_id}/gc-pin and note the PIN returned"""
        print(f"\n🔧 STEP 2: Generating PIN for project {project_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/gc-pin")
            
            if response.status_code == 200:
                pin_data = response.json()
                generated_pin = pin_data.get("gcPin", "NOT_FOUND")
                
                self.log_step(
                    2,
                    "Generate PIN",
                    True,
                    f"PIN generated successfully: {generated_pin}",
                    {
                        "project_id": project_id,
                        "generated_pin": generated_pin,
                        "full_response": pin_data
                    }
                )
                return generated_pin
            else:
                self.log_step(
                    2,
                    "Generate PIN",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"project_id": project_id, "status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_step(2, "Generate PIN", False, str(e))
            return None
    
    def step_3_check_pin_storage(self, project_id, expected_pin):
        """STEP 3 - Immediately after PIN generation: GET /api/projects/{project_id} and check if gc_pin field matches"""
        print(f"\n🔍 STEP 3: Checking if PIN {expected_pin} was stored correctly in project {project_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}")
            
            if response.status_code == 200:
                project_data = response.json()
                stored_gc_pin = project_data.get("gc_pin", "NOT_FOUND")
                gc_pin_used = project_data.get("gc_pin_used", "NOT_FOUND")
                
                pin_matches = str(stored_gc_pin) == str(expected_pin)
                
                self.log_step(
                    3,
                    "Check PIN Storage",
                    pin_matches,
                    f"Expected PIN: {expected_pin}, Stored PIN: {stored_gc_pin}, Match: {pin_matches}, Used: {gc_pin_used}",
                    {
                        "project_id": project_id,
                        "expected_pin": expected_pin,
                        "stored_pin": stored_gc_pin,
                        "pin_matches": pin_matches,
                        "gc_pin_used": gc_pin_used,
                        "full_project_data": project_data
                    }
                )
                return project_data
            else:
                self.log_step(
                    3,
                    "Check PIN Storage",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"project_id": project_id, "status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_step(3, "Check PIN Storage", False, str(e))
            return None
    
    def step_4_test_login_with_pin(self, project_id, pin):
        """STEP 4 - Try login with the fresh PIN: POST /api/gc/login-simple with projectId and PIN"""
        print(f"\n🔐 STEP 4: Testing login with project {project_id} and PIN {pin}")
        
        try:
            login_data = {
                "projectId": project_id,
                "pin": str(pin)
            }
            
            response = self.session.post(
                f"{self.base_url}/gc/login-simple",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                login_result = response.json()
                
                self.log_step(
                    4,
                    "Test Login with Fresh PIN",
                    True,
                    f"Login successful with PIN {pin}",
                    {
                        "project_id": project_id,
                        "pin_used": pin,
                        "login_response": login_result
                    }
                )
                return login_result
            else:
                error_message = response.text
                try:
                    error_json = response.json()
                    error_message = error_json.get("detail", error_message)
                except:
                    pass
                
                self.log_step(
                    4,
                    "Test Login with Fresh PIN",
                    False,
                    f"Login failed with PIN {pin}. HTTP {response.status_code}: {error_message}",
                    {
                        "project_id": project_id,
                        "pin_used": pin,
                        "status_code": response.status_code,
                        "error_message": error_message
                    }
                )
                return None
                
        except Exception as e:
            self.log_step(4, "Test Login with Fresh PIN", False, str(e))
            return None
    
    def step_5_debug_gc_login_query(self, project_id, pin):
        """STEP 5 - Debug the GC login query: Show exactly what query the GC login is running"""
        print(f"\n🔍 STEP 5: Debugging GC login query for project {project_id} with PIN {pin}")
        
        try:
            # First, let's check what's in the projects collection
            print("5a. Checking projects collection...")
            projects_response = self.session.get(f"{self.base_url}/projects")
            
            if projects_response.status_code == 200:
                projects = projects_response.json()
                target_project = None
                
                for project in projects:
                    if project.get("id") == project_id:
                        target_project = project
                        break
                
                if target_project:
                    self.log_step(
                        "5a",
                        "Debug - Check Projects Collection",
                        True,
                        f"Project found in collection with gc_pin: {target_project.get('gc_pin', 'NOT_SET')}",
                        {
                            "project_in_collection": True,
                            "project_data": target_project,
                            "gc_pin_in_collection": target_project.get("gc_pin"),
                            "gc_pin_used_in_collection": target_project.get("gc_pin_used")
                        }
                    )
                else:
                    self.log_step(
                        "5a",
                        "Debug - Check Projects Collection",
                        False,
                        f"Project {project_id} NOT found in projects collection",
                        {
                            "project_in_collection": False,
                            "total_projects": len(projects),
                            "project_ids_in_collection": [p.get("id") for p in projects]
                        }
                    )
            
            # Now let's check the specific project endpoint
            print("5b. Checking specific project endpoint...")
            project_response = self.session.get(f"{self.base_url}/projects/{project_id}")
            
            if project_response.status_code == 200:
                project_data = project_response.json()
                self.log_step(
                    "5b",
                    "Debug - Check Specific Project Endpoint",
                    True,
                    f"Project accessible via direct endpoint with gc_pin: {project_data.get('gc_pin', 'NOT_SET')}",
                    {
                        "project_accessible": True,
                        "project_data": project_data,
                        "gc_pin_direct": project_data.get("gc_pin"),
                        "gc_pin_used_direct": project_data.get("gc_pin_used")
                    }
                )
            else:
                self.log_step(
                    "5b",
                    "Debug - Check Specific Project Endpoint",
                    False,
                    f"Project NOT accessible via direct endpoint. HTTP {project_response.status_code}",
                    {
                        "project_accessible": False,
                        "status_code": project_response.status_code,
                        "error": project_response.text
                    }
                )
            
            # Now let's simulate what the GC login query should be doing
            print("5c. Simulating GC login query logic...")
            
            # The login should be looking for a project with matching ID and PIN
            login_query_simulation = {
                "expected_query": f"Find project where id='{project_id}' AND gc_pin='{pin}' AND gc_pin_used=false",
                "actual_project_data": target_project if target_project else "PROJECT_NOT_FOUND",
                "pin_match": target_project.get("gc_pin") == str(pin) if target_project else False,
                "pin_used_status": target_project.get("gc_pin_used") if target_project else "UNKNOWN"
            }
            
            query_would_succeed = (
                target_project is not None and 
                str(target_project.get("gc_pin", "")) == str(pin) and 
                target_project.get("gc_pin_used", True) == False
            )
            
            self.log_step(
                "5c",
                "Debug - Simulate GC Login Query",
                query_would_succeed,
                f"Query simulation: {'WOULD SUCCEED' if query_would_succeed else 'WOULD FAIL'}",
                login_query_simulation
            )
            
            return login_query_simulation
            
        except Exception as e:
            self.log_step("5", "Debug GC Login Query", False, str(e))
            return None
    
    def run_comprehensive_pin_debug(self, project_id):
        """Run the complete 5-step PIN storage debug process"""
        print(f"\n🚀 STARTING COMPREHENSIVE PIN STORAGE DEBUG FOR PROJECT: {project_id}")
        print(f"Backend URL: {self.base_url}")
        print(f"Timestamp: {datetime.now()}")
        
        # Step 1: Check current state before PIN generation
        step1_result = self.step_1_before_pin_generation(project_id)
        if not step1_result:
            print("❌ CRITICAL: Cannot proceed - project not found")
            return False
        
        # Step 2: Generate PIN
        generated_pin = self.step_2_generate_pin(project_id)
        if not generated_pin:
            print("❌ CRITICAL: Cannot proceed - PIN generation failed")
            return False
        
        # Step 3: Check if PIN was stored correctly
        step3_result = self.step_3_check_pin_storage(project_id, generated_pin)
        if not step3_result:
            print("❌ CRITICAL: Cannot proceed - cannot verify PIN storage")
            return False
        
        # Step 4: Test login with the fresh PIN
        login_result = self.step_4_test_login_with_pin(project_id, generated_pin)
        
        # Step 5: Debug the GC login query (regardless of step 4 result)
        debug_result = self.step_5_debug_gc_login_query(project_id, generated_pin)
        
        # Generate comprehensive summary
        self.generate_debug_summary(project_id, generated_pin, login_result is not None)
        
        return True
    
    def generate_debug_summary(self, project_id, pin, login_successful):
        """Generate a comprehensive summary of the debug results"""
        print(f"\n{'='*80}")
        print("🎯 COMPREHENSIVE PIN STORAGE DEBUG SUMMARY")
        print(f"{'='*80}")
        
        print(f"Project ID: {project_id}")
        print(f"Generated PIN: {pin}")
        print(f"Login Successful: {'✅ YES' if login_successful else '❌ NO'}")
        
        print(f"\n📊 STEP-BY-STEP RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"  {status} Step {result['step']}: {result['name']}")
            if not result["success"]:
                print(f"      ⚠️  {result['message']}")
        
        # Analyze the root cause
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Check if PIN generation worked
        pin_generation_worked = any(r["success"] and r["step"] == 2 for r in self.test_results)
        pin_storage_worked = any(r["success"] and r["step"] == 3 for r in self.test_results)
        
        if not pin_generation_worked:
            print("❌ ISSUE: PIN generation endpoint is not working")
        elif not pin_storage_worked:
            print("❌ ISSUE: PIN is generated but not stored correctly in the database")
        elif not login_successful:
            print("❌ ISSUE: PIN is generated and stored correctly, but GC login is not finding it")
            print("   This suggests a query mismatch in the login endpoint")
        else:
            print("✅ ALL SYSTEMS WORKING: PIN generation, storage, and login are all functional")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not login_successful:
            print("1. Check the GC login endpoint query logic")
            print("2. Verify the database collection and field names match")
            print("3. Ensure the login endpoint is looking in the correct collection")
            print("4. Check for data type mismatches (string vs number)")
            print("5. Verify the gc_pin_used flag is being checked correctly")
        else:
            print("✅ System is working correctly - no issues found")
        
        print(f"\n{'='*80}")
        
        # Return summary for further processing
        return {
            "project_id": project_id,
            "generated_pin": pin,
            "login_successful": login_successful,
            "steps_passed": sum(1 for r in self.test_results if r["success"]),
            "total_steps": len(self.test_results),
            "success_rate": f"{sum(1 for r in self.test_results if r['success'])}/{len(self.test_results)}"
        }

def main():
    """Main function to run the PIN storage debug test"""
    debugger = PINStorageDebugger()
    
    # Test with the specific project ID mentioned in the request
    project_id = "68cc802f8d44fcd8015b39b8"
    
    print("🔧 PIN STORAGE DEBUG TEST - COMPREHENSIVE ANALYSIS")
    print("=" * 60)
    print("This test will trace the PIN storage issue step by step:")
    print("1. Check project state before PIN generation")
    print("2. Generate a fresh PIN")
    print("3. Verify PIN is stored correctly")
    print("4. Test login with the fresh PIN")
    print("5. Debug the GC login query logic")
    print("=" * 60)
    
    success = debugger.run_comprehensive_pin_debug(project_id)
    
    if success:
        print("\n✅ DEBUG TEST COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ DEBUG TEST ENCOUNTERED CRITICAL ERRORS")
    
    return success

if __name__ == "__main__":
    main()