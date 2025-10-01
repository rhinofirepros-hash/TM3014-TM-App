#!/usr/bin/env python3
"""
T&M TAG API STRUCTURE VERIFICATION

This test compares the T&M tag API structure between what the frontend expects
and what the backend provides to identify the "offline mode" issue.
"""

import requests
import json
import sys
from datetime import datetime

# Production backend URL
BACKEND_URL = "https://tm3014-tm-app-production.up.railway.app"
API_URL = f"{BACKEND_URL}/api"

print(f"📊 T&M TAG API STRUCTURE VERIFICATION")
print(f"📍 Backend URL: {BACKEND_URL}")
print("=" * 80)

def make_request(method, endpoint, data=None):
    """Make HTTP request with error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def analyze_api_structure(endpoint_name, endpoint_path, method="GET", sample_data=None):
    """Analyze API structure and response format"""
    print(f"\n🔍 ANALYZING: {endpoint_name}")
    print(f"   📍 Endpoint: {method} {endpoint_path}")
    
    response, error = make_request(method, endpoint_path, sample_data)
    
    if error:
        print(f"   ❌ Connection Error: {error}")
        return None
    
    print(f"   📊 Status Code: {response.status_code}")
    
    if response.status_code == 404:
        print(f"   ❌ Endpoint Not Found")
        return None
    elif response.status_code == 405:
        print(f"   ❌ Method Not Allowed")
        return None
    elif response.status_code not in [200, 201, 422]:
        print(f"   ❌ Error Response: {response.text[:200]}")
        return None
    
    try:
        data = response.json()
        print(f"   ✅ Valid JSON Response")
        
        if isinstance(data, list):
            print(f"   📋 Response Type: Array with {len(data)} items")
            if len(data) > 0:
                sample_item = data[0]
                print(f"   🔑 Sample Item Keys: {list(sample_item.keys())}")
                return {"type": "array", "sample": sample_item, "count": len(data)}
        elif isinstance(data, dict):
            print(f"   📋 Response Type: Object")
            print(f"   🔑 Object Keys: {list(data.keys())}")
            return {"type": "object", "data": data}
        else:
            print(f"   📋 Response Type: {type(data)}")
            return {"type": str(type(data)), "data": data}
            
    except json.JSONDecodeError:
        print(f"   ❌ Invalid JSON Response")
        print(f"   📝 Raw Response: {response.text[:200]}")
        return None

# =============================================================================
# ANALYZE T&M TAG ENDPOINTS
# =============================================================================
print("\n🎯 T&M TAG ENDPOINTS ANALYSIS")

# Test /api/tm-tags endpoint
tm_tags_result = analyze_api_structure("T&M Tags (Frontend Expected)", "/tm-tags", "GET")

# Test /api/timelogs endpoint (alternative)
timelogs_result = analyze_api_structure("Time Logs (Backend Alternative)", "/timelogs", "GET")

# =============================================================================
# COMPARE API STRUCTURES
# =============================================================================
print("\n📊 API STRUCTURE COMPARISON")

if tm_tags_result and timelogs_result:
    print("✅ Both endpoints exist - comparing structures...")
    
    tm_sample = tm_tags_result.get("sample", {})
    timelog_sample = timelogs_result.get("sample", {})
    
    tm_keys = set(tm_sample.keys()) if tm_sample else set()
    timelog_keys = set(timelog_sample.keys()) if timelog_sample else set()
    
    print(f"\n🔑 T&M Tags Keys: {sorted(tm_keys)}")
    print(f"🔑 Time Logs Keys: {sorted(timelog_keys)}")
    
    common_keys = tm_keys.intersection(timelog_keys)
    tm_only_keys = tm_keys - timelog_keys
    timelog_only_keys = timelog_keys - tm_keys
    
    print(f"\n✅ Common Keys ({len(common_keys)}): {sorted(common_keys)}")
    if tm_only_keys:
        print(f"📋 T&M Tags Only ({len(tm_only_keys)}): {sorted(tm_only_keys)}")
    if timelog_only_keys:
        print(f"📋 Time Logs Only ({len(timelog_only_keys)}): {sorted(timelog_only_keys)}")
    
    # Check for critical fields
    critical_fields = ["id", "project_id", "date", "hours", "description"]
    missing_in_tm = [field for field in critical_fields if field not in tm_keys]
    missing_in_timelog = [field for field in critical_fields if field not in timelog_keys]
    
    if missing_in_tm:
        print(f"⚠️  Missing in T&M Tags: {missing_in_tm}")
    if missing_in_timelog:
        print(f"⚠️  Missing in Time Logs: {missing_in_timelog}")

elif tm_tags_result and not timelogs_result:
    print("✅ T&M Tags endpoint exists, Time Logs endpoint missing")
    print("💡 Frontend should use /api/tm-tags")
    
elif not tm_tags_result and timelogs_result:
    print("❌ T&M Tags endpoint missing, Time Logs endpoint exists")
    print("🚨 CRITICAL: Frontend expects /api/tm-tags but backend only has /api/timelogs")
    print("💡 This explains the 'offline mode' issue!")
    
else:
    print("❌ Both endpoints missing or inaccessible")
    print("🚨 CRITICAL: No T&M functionality available")

# =============================================================================
# TEST T&M TAG CREATION STRUCTURE
# =============================================================================
print("\n📝 T&M TAG CREATION STRUCTURE TESTING")

# Sample T&M tag data that frontend might send
frontend_tm_tag = {
    "project_name": "API Structure Test Project",
    "cost_code": "TEST001",
    "date_of_work": datetime.now().date().isoformat(),
    "tm_tag_title": "API Structure Test",
    "description_of_work": "Testing API structure compatibility",
    "gc_email": "test@structure.com",
    "labor_entries": [
        {
            "id": "test-labor-1",
            "worker_name": "Test Worker",
            "quantity": 1,
            "st_hours": 8.0,
            "ot_hours": 0.0,
            "dt_hours": 0.0,
            "pot_hours": 0.0,
            "total_hours": 8.0,
            "date": datetime.now().date().isoformat()
        }
    ],
    "material_entries": [],
    "equipment_entries": [],
    "other_entries": []
}

# Test T&M tag creation
print("\n🔍 Testing T&M Tag Creation (Frontend Format)")
tm_create_result = analyze_api_structure("T&M Tag Creation", "/tm-tags", "POST", frontend_tm_tag)

# Test alternative time log creation format
backend_timelog = {
    "project_id": "test-project-id",
    "installer_id": "test-installer-id",
    "date": datetime.now().date().isoformat(),
    "hours": 8.0,
    "description": "Testing timelog creation"
}

print("\n🔍 Testing Time Log Creation (Backend Format)")
timelog_create_result = analyze_api_structure("Time Log Creation", "/timelogs", "POST", backend_timelog)

# =============================================================================
# FINAL ANALYSIS AND RECOMMENDATIONS
# =============================================================================
print("\n" + "=" * 80)
print("📊 FINAL API STRUCTURE ANALYSIS")
print("=" * 80)

print("\n🎯 KEY FINDINGS:")

if not tm_tags_result and timelogs_result:
    print("🚨 CRITICAL ISSUE IDENTIFIED:")
    print("   • Frontend expects /api/tm-tags endpoints")
    print("   • Backend only provides /api/timelogs endpoints")
    print("   • This mismatch causes 'offline mode' fallback behavior")
    print("\n💡 SOLUTIONS:")
    print("   1. Add /api/tm-tags compatibility endpoints that map to /api/timelogs")
    print("   2. Update frontend to use /api/timelogs instead of /api/tm-tags")
    print("   3. Implement both endpoints with proper data transformation")

elif tm_tags_result and timelogs_result:
    print("✅ BOTH ENDPOINTS AVAILABLE:")
    print("   • Frontend can use preferred /api/tm-tags endpoints")
    print("   • Backend provides both /api/tm-tags and /api/timelogs")
    print("   • API structure compatibility confirmed")

elif tm_tags_result and not timelogs_result:
    print("✅ T&M TAGS ENDPOINT AVAILABLE:")
    print("   • Frontend /api/tm-tags expectations met")
    print("   • Backend provides expected T&M tag functionality")

else:
    print("🚨 CRITICAL FAILURE:")
    print("   • No T&M tag functionality available")
    print("   • Both /api/tm-tags and /api/timelogs endpoints missing or broken")

print(f"\n📅 Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")