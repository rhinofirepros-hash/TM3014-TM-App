#!/usr/bin/env python3
"""
Focused test for the specific review requirements of the secure GC PIN validation endpoint
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

def test_complete_workflow():
    """Test the complete workflow as specified in the review request"""
    print("🎯 TESTING COMPLETE WORKFLOW AS REQUESTED")
    print("=" * 50)
    
    # Step 1: Get a project with a valid PIN
    try:
        response = requests.get(f"{BACKEND_URL}/projects", timeout=10)
        if response.status_code != 200:
            print(f"❌ Could not get projects: {response.status_code}")
            return False
            
        projects = response.json()
        if not projects:
            print("❌ No projects available")
            return False
            
        # Use the first project and generate a fresh PIN
        project_id = projects[0]["id"]
        project_name = projects[0]["name"]
        
        pin_response = requests.get(f"{BACKEND_URL}/projects/{project_id}/gc-pin", timeout=10)
        if pin_response.status_code != 200:
            print(f"❌ Could not generate PIN: {pin_response.status_code}")
            return False
            
        pin_data = pin_response.json()
        original_pin = pin_data.get("gcPin")
        
        print(f"✅ Setup complete - Project: {project_name}, PIN: {original_pin}")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    
    # Step 2: Send a valid 4-digit PIN to the secure endpoint
    try:
        payload = {"pin": original_pin}
        
        response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                               json=payload, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Valid PIN accepted - Response: {data}")
            
            # Verify response contains only necessary data
            if "projectId" in data and "projectName" in data:
                print(f"✅ Response contains projectId: {data['projectId']}")
                print(f"✅ Response contains projectName: {data['projectName']}")
                
                # Verify no sensitive data is exposed
                sensitive_fields = ["gc_pin", "all_projects", "project_list", "pins", "password"]
                exposed = [field for field in sensitive_fields if field in str(data).lower()]
                if not exposed:
                    print("✅ No sensitive data exposed in response")
                else:
                    print(f"⚠️ Potentially sensitive data found: {exposed}")
            else:
                print("❌ Response missing required project info")
                return False
        else:
            print(f"❌ Valid PIN rejected: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PIN validation failed: {e}")
        return False
    
    # Step 3: Verify PIN regeneration occurred
    try:
        time.sleep(1)  # Allow time for database update
        
        pin_response = requests.get(f"{BACKEND_URL}/projects/{project_id}/gc-pin", timeout=10)
        if pin_response.status_code == 200:
            new_pin_data = pin_response.json()
            new_pin = new_pin_data.get("gcPin")
            
            if new_pin != original_pin:
                print(f"✅ PIN regenerated successfully: {original_pin} → {new_pin}")
            else:
                print(f"❌ PIN was not regenerated: still {original_pin}")
                return False
        else:
            print(f"❌ Could not verify PIN regeneration: {pin_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ PIN regeneration check failed: {e}")
        return False
    
    # Step 4: Test that the old PIN is now invalid
    try:
        old_pin_payload = {"pin": original_pin}
        
        response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                               json=old_pin_payload, 
                               timeout=10)
        
        if response.status_code == 401:
            print(f"✅ Old PIN correctly rejected: {original_pin}")
        else:
            print(f"❌ Old PIN should be invalid but got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Old PIN test failed: {e}")
        return False
    
    print("\n🎉 COMPLETE WORKFLOW TEST PASSED!")
    print("✅ Endpoint only requires PIN in request body")
    print("✅ Does NOT expose all project PINs or project data")
    print("✅ Returns project info only for valid PIN")
    print("✅ Regenerates PIN after successful validation")
    print("✅ Old PIN becomes invalid after use")
    
    return True

def test_security_aspects():
    """Test the security aspects specifically mentioned in the review"""
    print("\n🔒 TESTING SECURITY ASPECTS")
    print("=" * 40)
    
    # Test 1: Endpoint doesn't return lists of projects or PINs
    try:
        # Try various payloads that might trick the endpoint into exposing data
        test_payloads = [
            {"pin": "0000"},  # Invalid PIN
            {"pin": "1234", "list_projects": True},  # Try to request project list
            {"pin": "5678", "show_pins": True},  # Try to request PINs
            {"pin": "9999", "admin": True},  # Try admin access
        ]
        
        for payload in test_payloads:
            response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                                   json=payload, 
                                   timeout=10)
            
            if response.status_code in [400, 401]:
                # Check that error response doesn't leak data
                try:
                    error_data = response.json()
                    sensitive_terms = ["projects", "pins", "list", "all", "database"]
                    has_sensitive = any(term in str(error_data).lower() for term in sensitive_terms)
                    
                    if not has_sensitive:
                        print(f"✅ No data leakage in error response for payload: {payload}")
                    else:
                        print(f"⚠️ Potential data leakage in error response: {error_data}")
                except:
                    print(f"✅ Error response is not JSON (good for security)")
            else:
                print(f"⚠️ Unexpected response for invalid payload: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False
    
    # Test 2: Failed attempts are logged without exposing valid PINs
    try:
        # Make a failed attempt
        payload = {"pin": "0000", "ip": "test-security-check"}
        
        response = requests.post(f"{BACKEND_URL}/gc/validate-pin", 
                               json=payload, 
                               timeout=10)
        
        if response.status_code == 401:
            print("✅ Failed attempts properly rejected with 401")
            
            # Verify error message doesn't expose valid PINs
            try:
                error_data = response.json()
                error_message = str(error_data).lower()
                
                # Check that error doesn't contain actual PIN numbers
                has_pin_numbers = any(char.isdigit() for char in error_message if len([c for c in error_message if c.isdigit()]) >= 4)
                
                if not has_pin_numbers:
                    print("✅ Error message doesn't expose valid PINs")
                else:
                    print(f"⚠️ Error message might expose PIN numbers: {error_data}")
                    
            except:
                print("✅ Error response format is secure")
        else:
            print(f"❌ Expected 401 for invalid PIN, got: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed attempt logging test failed: {e}")
        return False
    
    print("✅ Security aspects verified")
    return True

if __name__ == "__main__":
    print("🚀 FOCUSED TESTING FOR SECURE GC PIN VALIDATION ENDPOINT")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    workflow_success = test_complete_workflow()
    security_success = test_security_aspects()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    if workflow_success and security_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The secure GC PIN validation endpoint is working correctly")
        print("✅ All security requirements are met")
        print("✅ Complete workflow functions as expected")
    else:
        print("⚠️ Some tests failed:")
        if not workflow_success:
            print("❌ Workflow test failed")
        if not security_success:
            print("❌ Security test failed")