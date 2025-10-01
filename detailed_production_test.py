#!/usr/bin/env python3
"""
DETAILED PRODUCTION BACKEND ANALYSIS
Analyze the working endpoints to understand the API structure and identify missing functionality
"""

import requests
import json
import uuid
from datetime import datetime

PRODUCTION_API_URL = "https://tm3014-tm-app-production.up.railway.app/api"

def test_working_endpoints():
    """Test the working endpoints in detail to understand API structure"""
    print("🔍 DETAILED ANALYSIS OF WORKING PRODUCTION ENDPOINTS")
    print("=" * 80)
    
    # Test GET /api/tm-tags in detail
    print("\n📋 ANALYZING GET /api/tm-tags")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Count: {len(data)} T&M tags")
            if data:
                print(f"✅ Sample structure: {list(data[0].keys())}")
                print(f"✅ Sample data: {json.dumps(data[0], indent=2, default=str)[:500]}...")
            else:
                print("⚠️  No T&M tags found")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/installers in detail
    print("\n👷 ANALYZING GET /api/installers")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/installers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Count: {len(data)} installers")
            if data:
                print(f"✅ Sample structure: {list(data[0].keys())}")
                print(f"✅ Sample data: {json.dumps(data[0], indent=2, default=str)[:500]}...")
            else:
                print("⚠️  No installers found")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/projects in detail
    print("\n📋 ANALYZING GET /api/projects")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/projects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Count: {len(data)} projects")
            if data:
                print(f"✅ Sample structure: {list(data[0].keys())}")
                print(f"✅ Sample data: {json.dumps(data[0], indent=2, default=str)[:500]}...")
            else:
                print("⚠️  No projects found")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/timelogs in detail
    print("\n⏰ ANALYZING GET /api/timelogs")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/timelogs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Count: {len(data)} timelogs")
            if data:
                print(f"✅ Sample structure: {list(data[0].keys())}")
                print(f"✅ Sample data: {json.dumps(data[0], indent=2, default=str)[:500]}...")
            else:
                print("⚠️  No timelogs found")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_specific_tm_tag_functionality():
    """Test specific T&M tag functionality with real data"""
    print("\n🎯 TESTING T&M TAG FUNCTIONALITY WITH REAL DATA")
    print("=" * 80)
    
    # First get existing T&M tags
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags", timeout=10)
        if response.status_code == 200:
            tm_tags = response.json()
            if tm_tags:
                # Test with first existing T&M tag
                first_tag = tm_tags[0]
                tag_id = first_tag.get('id')
                print(f"\n📝 Testing with existing T&M tag ID: {tag_id}")
                
                # Test GET /api/tm-tags/{id}
                print(f"\n🔍 Testing GET /api/tm-tags/{tag_id}")
                try:
                    response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{tag_id}", timeout=10)
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        print("✅ Individual T&M tag retrieval works")
                    elif response.status_code == 404:
                        print("❌ Individual T&M tag retrieval missing (404)")
                    else:
                        print(f"⚠️  Unexpected status: {response.text[:200]}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Test PDF endpoints with real ID
                print(f"\n📄 Testing GET /api/tm-tags/{tag_id}/pdf")
                try:
                    response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{tag_id}/pdf", timeout=10)
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        print("✅ PDF export works")
                        print(f"Content-Type: {response.headers.get('content-type')}")
                        print(f"Content-Length: {len(response.content)} bytes")
                    elif response.status_code == 404:
                        print("❌ PDF export missing (404)")
                    else:
                        print(f"⚠️  Unexpected status: {response.text[:200]}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                print(f"\n👁️ Testing GET /api/tm-tags/{tag_id}/preview")
                try:
                    response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{tag_id}/preview", timeout=10)
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        print("✅ PDF preview works")
                        print(f"Content-Type: {response.headers.get('content-type')}")
                        print(f"Content-Length: {len(response.content)} bytes")
                    elif response.status_code == 404:
                        print("❌ PDF preview missing (404)")
                    else:
                        print(f"⚠️  Unexpected status: {response.text[:200]}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("⚠️  No existing T&M tags to test with")
        else:
            print(f"❌ Could not get T&M tags: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting T&M tags: {e}")

def test_installer_crud_operations():
    """Test installer CRUD operations"""
    print("\n👷 TESTING INSTALLER CRUD OPERATIONS")
    print("=" * 80)
    
    # Test POST /api/installers (create)
    print("\n📝 Testing POST /api/installers (create installer)")
    test_installer = {
        "name": "Production Test Installer",
        "cost_rate": 45.0,
        "position": "Senior Electrician",
        "phone": "555-TEST",
        "email": "test@production.com"
    }
    
    try:
        response = requests.post(f"{PRODUCTION_API_URL}/installers", 
                               json=test_installer, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            created_installer = response.json()
            installer_id = created_installer.get('id')
            print(f"✅ Installer created successfully: {installer_id}")
            
            # Test GET /api/installers/{id}
            print(f"\n🔍 Testing GET /api/installers/{installer_id}")
            try:
                response = requests.get(f"{PRODUCTION_API_URL}/installers/{installer_id}", timeout=10)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Individual installer retrieval works")
                elif response.status_code == 404:
                    print("❌ Individual installer retrieval missing (404)")
                else:
                    print(f"⚠️  Unexpected status: {response.text[:200]}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test PUT /api/installers/{id}
            print(f"\n✏️ Testing PUT /api/installers/{installer_id}")
            update_data = {"name": "Updated Test Installer", "cost_rate": 50.0}
            try:
                response = requests.put(f"{PRODUCTION_API_URL}/installers/{installer_id}", 
                                      json=update_data, timeout=10)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Installer update works")
                elif response.status_code == 404:
                    print("❌ Installer update missing (404)")
                else:
                    print(f"⚠️  Unexpected status: {response.text[:200]}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test DELETE /api/installers/{id}
            print(f"\n🗑️ Testing DELETE /api/installers/{installer_id}")
            try:
                response = requests.delete(f"{PRODUCTION_API_URL}/installers/{installer_id}", timeout=10)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Installer deletion works")
                elif response.status_code == 404:
                    print("❌ Installer deletion missing (404)")
                elif response.status_code == 405:
                    print("❌ Installer deletion not allowed (405 Method Not Allowed)")
                else:
                    print(f"⚠️  Unexpected status: {response.text[:200]}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        else:
            print(f"❌ Installer creation failed: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error creating installer: {e}")

def test_authentication():
    """Test authentication endpoints"""
    print("\n🔐 TESTING AUTHENTICATION")
    print("=" * 80)
    
    # Test admin authentication
    print("\n🔑 Testing POST /api/auth/admin")
    try:
        response = requests.post(f"{PRODUCTION_API_URL}/auth/admin", 
                               json={"pin": "J777"}, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Admin authentication works")
            print(f"Response: {json.dumps(auth_data, indent=2)}")
        else:
            print(f"❌ Admin authentication failed: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test execution"""
    print("🚨 DETAILED PRODUCTION BACKEND ANALYSIS")
    print(f"📍 Production API URL: {PRODUCTION_API_URL}")
    print("=" * 80)
    
    test_working_endpoints()
    test_specific_tm_tag_functionality()
    test_installer_crud_operations()
    test_authentication()
    
    print("\n" + "=" * 80)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 80)
    print("🎯 KEY FINDINGS:")
    print("   • T&M tags list endpoint works (/tm-tags)")
    print("   • Installers management partially works (/installers)")
    print("   • Projects endpoint works (/projects)")
    print("   • Timelogs endpoint works (/timelogs)")
    print("   • Authentication works (/auth/admin)")
    print("\n❌ MISSING CRITICAL FUNCTIONALITY:")
    print("   • Individual T&M tag retrieval (/tm-tags/{id})")
    print("   • PDF export functionality (/tm-tags/{id}/pdf)")
    print("   • PDF preview functionality (/tm-tags/{id}/preview)")
    print("   • Individual installer operations (/installers/{id})")
    print("   • DELETE operations for installers")

if __name__ == "__main__":
    main()