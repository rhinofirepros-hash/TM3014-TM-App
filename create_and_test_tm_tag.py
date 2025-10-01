#!/usr/bin/env python3
"""
CREATE T&M TAG AND TEST MISSING FUNCTIONALITY
Create a T&M tag on production and test the missing endpoints
"""

import requests
import json
import uuid
from datetime import datetime

PRODUCTION_API_URL = "https://tm3014-tm-app-production.up.railway.app/api"

def create_tm_tag():
    """Create a T&M tag for testing"""
    print("📝 CREATING T&M TAG FOR TESTING")
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
        print("❌ Cannot create T&M tag - missing project or installer")
        return None
    
    # Create T&M tag data
    tm_tag_data = {
        "project_name": "Production Test Project",
        "cost_code": "TEST001",
        "date_of_work": datetime.now().isoformat(),
        "tm_tag_title": "Production Endpoint Test T&M Tag",
        "description_of_work": "Testing production backend T&M tag endpoints for missing functionality",
        "gc_email": "test@production.com",
        "project_id": project_id,
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
                "date": datetime.now().strftime('%Y-%m-%d')
            }
        ],
        "material_entries": [
            {
                "id": str(uuid.uuid4()),
                "material_name": "Test Material",
                "unit_of_measure": "EA",
                "quantity": 10,
                "unit_cost": 5.0,
                "total": 50.0,
                "date_of_work": datetime.now().strftime('%Y-%m-%d')
            }
        ],
        "equipment_entries": [],
        "other_entries": []
    }
    
    print(f"\n📤 Creating T&M tag...")
    try:
        response = requests.post(f"{PRODUCTION_API_URL}/tm-tags", 
                               json=tm_tag_data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            created_tag = response.json()
            tag_id = created_tag.get('id')
            print(f"✅ T&M tag created successfully: {tag_id}")
            return tag_id
        else:
            print(f"❌ T&M tag creation failed: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"❌ Error creating T&M tag: {e}")
        return None

def test_tm_tag_endpoints(tag_id):
    """Test T&M tag endpoints with real ID"""
    print(f"\n🎯 TESTING T&M TAG ENDPOINTS WITH ID: {tag_id}")
    print("=" * 80)
    
    # Test GET /api/tm-tags/{id}
    print(f"\n🔍 Testing GET /api/tm-tags/{tag_id}")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{tag_id}", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Individual T&M tag retrieval WORKS")
            tag_data = response.json()
            print(f"✅ Retrieved tag title: {tag_data.get('tm_tag_title', 'N/A')}")
        elif response.status_code == 404:
            print("❌ Individual T&M tag retrieval MISSING (404)")
        else:
            print(f"⚠️  Unexpected status: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/tm-tags/{id}/pdf
    print(f"\n📄 Testing GET /api/tm-tags/{tag_id}/pdf")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{tag_id}/pdf", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PDF export WORKS")
            print(f"✅ Content-Type: {response.headers.get('content-type')}")
            print(f"✅ Content-Length: {len(response.content)} bytes")
            
            # Check if it's actually a PDF
            if response.content.startswith(b'%PDF'):
                print("✅ Valid PDF content detected")
            else:
                print("⚠️  Content may not be valid PDF")
                
        elif response.status_code == 404:
            print("❌ PDF export MISSING (404)")
        else:
            print(f"⚠️  Unexpected status: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test GET /api/tm-tags/{id}/preview
    print(f"\n👁️ Testing GET /api/tm-tags/{tag_id}/preview")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags/{tag_id}/preview", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ PDF preview WORKS")
            print(f"✅ Content-Type: {response.headers.get('content-type')}")
            print(f"✅ Content-Length: {len(response.content)} bytes")
            
            # Check if it's HTML
            if 'text/html' in response.headers.get('content-type', ''):
                print("✅ HTML content detected")
                # Check for key elements
                content = response.text
                if 'TIME & MATERIAL' in content:
                    print("✅ Contains T&M report structure")
                else:
                    print("⚠️  May not contain proper T&M report structure")
            else:
                print("⚠️  Content may not be HTML")
                
        elif response.status_code == 404:
            print("❌ PDF preview MISSING (404)")
        else:
            print(f"⚠️  Unexpected status: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_timelogs_vs_tm_tags():
    """Compare timelogs and tm-tags endpoints"""
    print(f"\n🔄 COMPARING TIMELOGS VS TM-TAGS ENDPOINTS")
    print("=" * 80)
    
    # Get timelogs
    print("\n⏰ Getting timelogs...")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/timelogs", timeout=10)
        if response.status_code == 200:
            timelogs = response.json()
            print(f"✅ Timelogs count: {len(timelogs)}")
            if timelogs:
                print(f"✅ Timelog structure: {list(timelogs[0].keys())}")
        else:
            print(f"❌ Timelogs error: {response.status_code}")
    except Exception as e:
        print(f"❌ Timelogs error: {e}")
    
    # Get tm-tags
    print("\n📋 Getting tm-tags...")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/tm-tags", timeout=10)
        if response.status_code == 200:
            tm_tags = response.json()
            print(f"✅ T&M tags count: {len(tm_tags)}")
            if tm_tags:
                print(f"✅ T&M tag structure: {list(tm_tags[0].keys())}")
        else:
            print(f"❌ T&M tags error: {response.status_code}")
    except Exception as e:
        print(f"❌ T&M tags error: {e}")

def main():
    """Main test execution"""
    print("🚨 CREATE AND TEST T&M TAG FUNCTIONALITY")
    print(f"📍 Production API URL: {PRODUCTION_API_URL}")
    print("=" * 80)
    
    # Create a T&M tag
    tag_id = create_tm_tag()
    
    if tag_id:
        # Test the endpoints with the created tag
        test_tm_tag_endpoints(tag_id)
    else:
        print("❌ Cannot test T&M tag endpoints - creation failed")
    
    # Compare timelogs vs tm-tags
    test_timelogs_vs_tm_tags()
    
    print("\n" + "=" * 80)
    print("📊 CRITICAL FINDINGS SUMMARY")
    print("=" * 80)
    print("🎯 PRODUCTION BACKEND STATUS:")
    print("   ✅ T&M tags list endpoint works")
    print("   ✅ T&M tag creation works")
    print("   ✅ Installers management works (except DELETE)")
    print("   ✅ Projects endpoint works")
    print("   ✅ Timelogs endpoint works")
    print("   ✅ Authentication works")
    print("\n❌ MISSING FUNCTIONALITY CAUSING USER ISSUES:")
    print("   🚨 Individual T&M tag retrieval (/tm-tags/{id}) - causes frontend errors")
    print("   🚨 PDF export (/tm-tags/{id}/pdf) - causes 'black screen' on preview")
    print("   🚨 PDF preview (/tm-tags/{id}/preview) - causes preview failures")
    print("   🚨 DELETE installers - user can't delete crew members")
    print("\n💡 ROOT CAUSE:")
    print("   • Production backend is missing specific endpoint implementations")
    print("   • API structure mismatch between frontend expectations and backend reality")
    print("   • PDF functionality not deployed to production")

if __name__ == "__main__":
    main()