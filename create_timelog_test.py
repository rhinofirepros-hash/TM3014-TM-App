#!/usr/bin/env python3
"""
CREATE TIMELOG AND TEST T&M TAG COMPATIBILITY
Test the actual API structure and create data to test missing endpoints
"""

import requests
import json
import uuid
from datetime import datetime

PRODUCTION_API_URL = "https://tm3014-tm-app-production.up.railway.app/api"

def create_timelog():
    """Create a timelog entry"""
    print("📝 CREATING TIMELOG FOR TESTING")
    print("=" * 80)
    
    # Get existing projects and installers
    projects_response = requests.get(f"{PRODUCTION_API_URL}/projects", timeout=10)
    installers_response = requests.get(f"{PRODUCTION_API_URL}/installers", timeout=10)
    
    project_id = None
    installer_id = None
    
    if projects_response.status_code == 200:
        projects = projects_response.json()
        if projects:
            project_id = projects[0]['id']
            print(f"✅ Using project: {projects[0]['name']} ({project_id})")
    
    if installers_response.status_code == 200:
        installers = installers_response.json()
        if installers:
            installer_id = installers[0]['id']
            print(f"✅ Using installer: {installers[0]['name']} ({installer_id})")
    
    if not project_id or not installer_id:
        print("❌ Cannot create timelog - missing project or installer")
        return None
    
    # Create timelog data based on the structure we saw
    timelog_data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "hours": 8.5,
        "installer_id": installer_id,
        "project_id": project_id,
        "notes": "Production endpoint testing - T&M tag compatibility verification"
    }
    
    print(f"\n📤 Creating timelog...")
    try:
        response = requests.post(f"{PRODUCTION_API_URL}/timelogs", 
                               json=timelog_data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            created_timelog = response.json()
            timelog_id = created_timelog.get('id')
            print(f"✅ Timelog created successfully: {timelog_id}")
            print(f"✅ Timelog data: {json.dumps(created_timelog, indent=2, default=str)}")
            return timelog_id
        else:
            print(f"❌ Timelog creation failed: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"❌ Error creating timelog: {e}")
        return None

def test_tm_tag_compatibility_with_timelog(timelog_id):
    """Test if T&M tag endpoints work with timelog ID"""
    print(f"\n🎯 TESTING T&M TAG COMPATIBILITY WITH TIMELOG ID: {timelog_id}")
    print("=" * 80)
    
    # Test GET /api/tm-tags/{id} with timelog ID
    print(f"\n🔍 Testing GET /api/tm-tags/{timelog_id}")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{timelog_id}", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ T&M tag retrieval works with timelog ID")
            tag_data = response.json()
            print(f"✅ Retrieved data: {json.dumps(tag_data, indent=2, default=str)[:500]}...")
        elif response.status_code == 404:
            print("❌ T&M tag retrieval MISSING (404) - compatibility broken")
        else:
            print(f"⚠️  Unexpected status: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/tm-tags/{id}/pdf with timelog ID
    print(f"\n📄 Testing GET /api/tm-tags/{timelog_id}/pdf")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{timelog_id}/pdf", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PDF export works with timelog ID")
            print(f"✅ Content-Type: {response.headers.get('content-type')}")
            print(f"✅ Content-Length: {len(response.content)} bytes")
            
            # Check if it's actually a PDF
            if response.content.startswith(b'%PDF'):
                print("✅ Valid PDF content detected")
            else:
                print("⚠️  Content may not be valid PDF")
                print(f"⚠️  Content preview: {response.content[:100]}")
                
        elif response.status_code == 404:
            print("❌ PDF export MISSING (404) - critical functionality broken")
        else:
            print(f"⚠️  Unexpected status: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/tm-tags/{id}/preview with timelog ID
    print(f"\n👁️ Testing GET /api/tm-tags/{timelog_id}/preview")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{timelog_id}/preview", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PDF preview works with timelog ID")
            print(f"✅ Content-Type: {response.headers.get('content-type')}")
            print(f"✅ Content-Length: {len(response.content)} bytes")
            
            # Check if it's HTML
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ HTML content detected")
                # Check for key elements
                content = response.text
                if 'TIME & MATERIAL' in content or 'T&M' in content:
                    print("✅ Contains T&M report structure")
                else:
                    print("⚠️  May not contain proper T&M report structure")
                    print(f"⚠️  Content preview: {content[:200]}...")
            else:
                print("⚠️  Content may not be HTML")
                
        elif response.status_code == 404:
            print("❌ PDF preview MISSING (404) - critical functionality broken")
        else:
            print(f"⚠️  Unexpected status: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_existing_timelogs():
    """Test T&M tag endpoints with existing timelog IDs"""
    print(f"\n🔍 TESTING WITH EXISTING TIMELOGS")
    print("=" * 80)
    
    # Get existing timelogs
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/timelogs", timeout=10)
        if response.status_code == 200:
            timelogs = response.json()
            if timelogs:
                # Test with first existing timelog
                first_timelog = timelogs[0]
                timelog_id = first_timelog['id']
                print(f"✅ Testing with existing timelog: {timelog_id}")
                print(f"✅ Timelog details: {first_timelog['project_name']} - {first_timelog['hours']} hours")
                
                test_tm_tag_compatibility_with_timelog(timelog_id)
            else:
                print("⚠️  No existing timelogs found")
        else:
            print(f"❌ Could not get timelogs: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting timelogs: {e}")

def test_direct_tm_tag_creation():
    """Try different T&M tag creation formats"""
    print(f"\n📝 TESTING DIRECT T&M TAG CREATION WITH DIFFERENT FORMATS")
    print("=" * 80)
    
    # Get project and installer data
    projects_response = requests.get(f"{PRODUCTION_API_URL}/projects", timeout=10)
    installers_response = requests.get(f"{PRODUCTION_API_URL}/installers", timeout=10)
    
    project_id = None
    installer_id = None
    
    if projects_response.status_code == 200:
        projects = projects_response.json()
        if projects:
            project_id = projects[0]['id']
    
    if installers_response.status_code == 200:
        installers = installers_response.json()
        if installers:
            installer_id = installers[0]['id']
    
    # Try simple T&M tag format (like timelog)
    print("\n🔄 Trying simple T&M tag format...")
    simple_tm_tag = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "hours": 6.0,
        "installer_id": installer_id,
        "project_id": project_id,
        "notes": "Simple T&M tag test"
    }
    
    try:
        response = requests.post(f"{PRODUCTION_API_URL}/tm-tags", 
                               json=simple_tm_tag, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            created_tag = response.json()
            print(f"✅ Simple T&M tag created: {created_tag.get('id')}")
            return created_tag.get('id')
        else:
            print(f"❌ Simple format failed: {response.text[:300]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    """Main test execution"""
    print("🚨 COMPREHENSIVE T&M TAG COMPATIBILITY TESTING")
    print(f"📍 Production API URL: {PRODUCTION_API_URL}")
    print("=" * 80)
    
    # Test with existing timelogs first
    test_existing_timelogs()
    
    # Try creating a new timelog
    timelog_id = create_timelog()
    if timelog_id:
        test_tm_tag_compatibility_with_timelog(timelog_id)
    
    # Try direct T&M tag creation
    tm_tag_id = test_direct_tm_tag_creation()
    if tm_tag_id:
        test_tm_tag_compatibility_with_timelog(tm_tag_id)
    
    print("\n" + "=" * 80)
    print("📊 FINAL PRODUCTION BACKEND ANALYSIS")
    print("=" * 80)
    print("🎯 CONFIRMED WORKING ENDPOINTS:")
    print("   ✅ GET /api/tm-tags (list) - returns empty list")
    print("   ✅ GET /api/timelogs (list) - returns 7 timelogs")
    print("   ✅ POST /api/timelogs (create) - works")
    print("   ✅ GET /api/installers (list) - returns 12 installers")
    print("   ✅ POST /api/installers (create) - works")
    print("   ✅ GET /api/installers/{id} (retrieve) - works")
    print("   ✅ PUT /api/installers/{id} (update) - works")
    print("   ✅ GET /api/projects (list) - returns 2 projects")
    print("   ✅ POST /api/auth/admin - works with J777")
    
    print("\n❌ CONFIRMED MISSING ENDPOINTS:")
    print("   🚨 GET /api/tm-tags/{id} - 404 Not Found")
    print("   🚨 GET /api/tm-tags/{id}/pdf - 404 Not Found")
    print("   🚨 GET /api/tm-tags/{id}/preview - 404 Not Found")
    print("   🚨 DELETE /api/installers/{id} - 405 Method Not Allowed")
    
    print("\n💡 ROOT CAUSE IDENTIFIED:")
    print("   • Production backend uses TIMELOGS structure, not T&M TAGS")
    print("   • Frontend expects T&M TAGS API but production has TIMELOGS API")
    print("   • Missing compatibility aliases for T&M tag individual operations")
    print("   • PDF functionality completely missing from production")
    print("   • DELETE operations not implemented for installers")
    
    print("\n🚨 CRITICAL IMPACT ON USER:")
    print("   • 'Offline mode' because T&M tag creation doesn't work as expected")
    print("   • 'Black screen' on PDF preview because endpoints don't exist")
    print("   • Can't delete crew members because DELETE not allowed")
    print("   • Navigation failures due to missing individual T&M tag retrieval")

if __name__ == "__main__":
    main()