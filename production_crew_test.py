#!/usr/bin/env python3
"""
Production Backend Test for Crew Member Date Serialization
==========================================================

Test the crew member creation against the production backend to ensure consistency.
"""

import requests
import json
import os

# Production backend URL
PRODUCTION_URL = "https://tm3014-tm-app-production.up.railway.app/api"

def test_production_crew_creation():
    """Test crew member creation against production backend"""
    print("🚀 Testing Crew Member Creation Against Production Backend")
    print(f"🔗 Production URL: {PRODUCTION_URL}")
    print("=" * 80)
    
    # Test data from user's screenshot
    test_data = {
        "name": "Production Test Installer",
        "cost_rate": 33,
        "hire_date": "2025-09-30",
        "phone": "(555) 123-4567",
        "email": "production@example.com"
    }
    
    try:
        print("📤 Sending request to production backend...")
        response = requests.post(f"{PRODUCTION_URL}/installers", json=test_data, timeout=10)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            installer_data = response.json()
            print("✅ SUCCESS: Production backend successfully created installer with hire_date")
            print(f"   Installer ID: {installer_data.get('id')}")
            print(f"   Name: {installer_data.get('name')}")
            print(f"   Cost Rate: ${installer_data.get('cost_rate')}/hr")
            print(f"   Hire Date: {installer_data.get('hire_date')}")
            print(f"   Phone: {installer_data.get('phone')}")
            print(f"   Email: {installer_data.get('email')}")
            
            # Verify all expected fields are present
            expected_fields = ['id', 'name', 'cost_rate', 'hire_date', 'phone', 'email']
            missing_fields = [field for field in expected_fields if field not in installer_data]
            
            if not missing_fields:
                print("✅ All expected fields present in response")
                return True
            else:
                print(f"⚠️  Missing fields: {missing_fields}")
                return False
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT: Production backend did not respond within 10 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 CONNECTION ERROR: Could not connect to production backend")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_production_get_installers():
    """Test getting installers from production backend"""
    print("\n🔍 Testing GET /api/installers on production...")
    
    try:
        response = requests.get(f"{PRODUCTION_URL}/installers", timeout=10)
        
        if response.status_code == 200:
            installers = response.json()
            print(f"✅ SUCCESS: Retrieved {len(installers)} installers from production")
            
            # Check if any installers have hire_date
            installers_with_dates = [i for i in installers if i.get('hire_date')]
            print(f"   Installers with hire_date: {len(installers_with_dates)}")
            
            if installers_with_dates:
                print("   Sample installer with hire_date:")
                sample = installers_with_dates[0]
                print(f"     Name: {sample.get('name')}")
                print(f"     Hire Date: {sample.get('hire_date')}")
            
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 PRODUCTION BACKEND CONSISTENCY TEST")
    print("=" * 80)
    
    # Test creation
    creation_success = test_production_crew_creation()
    
    # Test retrieval
    retrieval_success = test_production_get_installers()
    
    print("\n" + "=" * 80)
    print("📊 PRODUCTION TEST SUMMARY")
    print("=" * 80)
    
    if creation_success and retrieval_success:
        print("🎉 PRODUCTION BACKEND: FULLY COMPATIBLE")
        print("   ✅ Crew member creation with hire_date works")
        print("   ✅ Date serialization is consistent")
        print("   ✅ No HTTP 500 errors")
    elif creation_success:
        print("⚠️  PRODUCTION BACKEND: PARTIALLY COMPATIBLE")
        print("   ✅ Creation works")
        print("   ❌ Retrieval has issues")
    else:
        print("❌ PRODUCTION BACKEND: COMPATIBILITY ISSUES")
        print("   ❌ Date serialization may not be fixed in production")
        print("   ❌ May still have HTTP 500 errors")
    
    print("\n💡 NOTE: If production tests fail, the fix may not be deployed to production yet.")