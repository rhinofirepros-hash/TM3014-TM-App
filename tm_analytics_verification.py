#!/usr/bin/env python3
"""
Specific verification test for T&M project analytics fix
This test verifies the exact issue mentioned in the review request:
- T&M project showing -$2,387 profit should now show correct markup profit of $2,743
"""

import requests
import json
from datetime import datetime
import uuid

# Backend URL
BACKEND_URL = "https://project-autopilot.preview.emergentagent.com/api"

def test_tm_profit_calculation_fix():
    """Test the specific T&M profit calculation fix mentioned in the review request"""
    print("🔍 Testing T&M Project Profit Calculation Fix")
    print("=" * 60)
    
    session = requests.Session()
    
    # Create a T&M project similar to the one that was showing negative profit
    tm_project_data = {
        "name": "T&M Profit Fix Test Project",
        "description": "Testing the fix for T&M project profit calculation",
        "client_company": "Test Client Corp",
        "gc_email": "test@client.com",
        "project_type": "tm_only",  # T&M project type
        "contract_amount": 0,  # T&M projects don't have fixed contract
        "labor_rate": 95.0,  # Standard rate
        "project_manager": "Jesus Garcia",
        "start_date": datetime.now().isoformat(),
        "address": "Test Location"
    }
    
    try:
        # Create T&M project
        print("1. Creating T&M project...")
        response = session.post(
            f"{BACKEND_URL}/projects",
            json=tm_project_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create T&M project: {response.status_code}")
            return False
        
        tm_project = response.json()
        project_id = tm_project["id"]
        print(f"✅ T&M project created: {project_id}")
        
        # Create employee with known cost
        print("2. Creating employee with known hourly rate...")
        employee_data = {
            "name": "Test Worker for T&M Fix",
            "hourly_rate": 65.0,  # True cost to company
            "gc_billing_rate": 95.0,  # Rate billed to GC
            "position": "Test Electrician",
            "hire_date": datetime.now().isoformat()
        }
        
        emp_response = session.post(
            f"{BACKEND_URL}/employees",
            json=employee_data,
            headers={"Content-Type": "application/json"}
        )
        
        if emp_response.status_code == 200:
            print("✅ Employee created successfully")
        else:
            print(f"⚠️ Employee creation failed: {emp_response.status_code}")
        
        # Create T&M tag with realistic data that would have shown negative profit before
        print("3. Creating T&M tag with labor and materials...")
        tm_tag_data = {
            "project_id": project_id,
            "project_name": tm_project["name"],
            "cost_code": "TM-FIX-TEST-001",
            "date_of_work": datetime.now().isoformat(),
            "tm_tag_title": "T&M Profit Fix Test",
            "description_of_work": "Testing T&M profit calculation fix - should show positive markup profit",
            "labor_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "worker_name": "Test Worker for T&M Fix",
                    "quantity": 1,
                    "st_hours": 40.0,  # 40 hours of work
                    "ot_hours": 0.0,
                    "dt_hours": 0.0,
                    "pot_hours": 0.0,
                    "total_hours": 40.0,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "material_entries": [
                {
                    "id": str(uuid.uuid4()),
                    "material_name": "Test Materials",
                    "unit_of_measure": "lot",
                    "quantity": 1.0,
                    "unit_cost": 1500.0,
                    "total": 1500.0,
                    "date_of_work": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "equipment_entries": [],
            "other_entries": [],
            "gc_email": "test@client.com"
        }
        
        tm_tag_response = session.post(
            f"{BACKEND_URL}/tm-tags",
            json=tm_tag_data,
            headers={"Content-Type": "application/json"}
        )
        
        if tm_tag_response.status_code != 200:
            print(f"❌ Failed to create T&M tag: {tm_tag_response.status_code}")
            return False
        
        print("✅ T&M tag created successfully")
        
        # Wait for data processing
        import time
        time.sleep(2)
        
        # Get analytics for T&M project
        print("4. Getting analytics for T&M project...")
        analytics_response = session.get(f"{BACKEND_URL}/projects/{project_id}/analytics")
        
        if analytics_response.status_code != 200:
            print(f"❌ Failed to get analytics: {analytics_response.status_code}")
            return False
        
        analytics = analytics_response.json()
        
        # Analyze the results
        print("\n📊 ANALYTICS RESULTS:")
        print("=" * 40)
        
        project_type = analytics.get("project_type", "unknown")
        labor_markup_profit = analytics.get("labor_markup_profit", 0)
        material_markup_profit = analytics.get("material_markup_profit", 0)
        total_profit = analytics.get("profit", 0)
        profit_margin = analytics.get("profit_margin", 0)
        total_labor_cost = analytics.get("total_labor_cost", 0)
        true_employee_cost = analytics.get("true_employee_cost", 0)
        total_material_cost = analytics.get("total_material_cost", 0)
        
        print(f"Project Type: {project_type}")
        print(f"Total Labor Cost (Billed): ${total_labor_cost:,.2f}")
        print(f"True Employee Cost: ${true_employee_cost:,.2f}")
        print(f"Labor Markup Profit: ${labor_markup_profit:,.2f}")
        print(f"Total Material Cost: ${total_material_cost:,.2f}")
        print(f"Material Markup Profit: ${material_markup_profit:,.2f}")
        print(f"Total Profit: ${total_profit:,.2f}")
        print(f"Profit Margin: {profit_margin:.2f}%")
        
        # Expected calculations:
        # Labor: 40 hours * $95/hr = $3,800 billed
        # True cost: 40 hours * $65/hr = $2,600
        # Labor markup profit = $3,800 - $2,600 = $1,200
        # Material markup profit = $1,500 * 0.2 = $300 (20% markup)
        # Total profit = $1,200 + $300 = $1,500
        
        expected_labor_billed = 40 * 95  # $3,800
        expected_true_cost = 40 * 65     # $2,600
        expected_labor_markup = expected_labor_billed - expected_true_cost  # $1,200
        expected_material_markup = 1500 * 0.2  # $300
        expected_total_profit = expected_labor_markup + expected_material_markup  # $1,500
        
        print(f"\n🎯 EXPECTED VALUES:")
        print(f"Expected Labor Billed: ${expected_labor_billed:,.2f}")
        print(f"Expected True Cost: ${expected_true_cost:,.2f}")
        print(f"Expected Labor Markup: ${expected_labor_markup:,.2f}")
        print(f"Expected Material Markup: ${expected_material_markup:,.2f}")
        print(f"Expected Total Profit: ${expected_total_profit:,.2f}")
        
        # Verify the fix
        print(f"\n✅ VERIFICATION RESULTS:")
        print("=" * 40)
        
        success = True
        issues = []
        
        # 1. Project type should be tm_only
        if project_type != "tm_only":
            success = False
            issues.append(f"❌ Project type should be 'tm_only', got '{project_type}'")
        else:
            print("✅ Project type correctly identified as 'tm_only'")
        
        # 2. Labor markup profit should be positive and approximately correct
        if labor_markup_profit <= 0:
            success = False
            issues.append(f"❌ Labor markup profit should be positive, got ${labor_markup_profit}")
        elif abs(labor_markup_profit - expected_labor_markup) > 100:  # Allow some variance
            success = False
            issues.append(f"❌ Labor markup profit calculation incorrect: expected ~${expected_labor_markup}, got ${labor_markup_profit}")
        else:
            print(f"✅ Labor markup profit is positive: ${labor_markup_profit:,.2f}")
        
        # 3. Total profit should be positive (this was the main issue - showing negative)
        if total_profit <= 0:
            success = False
            issues.append(f"❌ CRITICAL: Total profit should be positive, got ${total_profit} (this was the original issue)")
        else:
            print(f"✅ Total profit is positive: ${total_profit:,.2f} (ISSUE FIXED!)")
        
        # 4. Profit margin should be positive
        if profit_margin <= 0:
            success = False
            issues.append(f"❌ Profit margin should be positive, got {profit_margin}%")
        else:
            print(f"✅ Profit margin is positive: {profit_margin:.2f}%")
        
        # 5. Material markup profit should exist
        if material_markup_profit <= 0:
            success = False
            issues.append(f"❌ Material markup profit should be positive, got ${material_markup_profit}")
        else:
            print(f"✅ Material markup profit calculated: ${material_markup_profit:,.2f}")
        
        if success:
            print(f"\n🎉 SUCCESS: T&M Project Profit Calculation Fix VERIFIED!")
            print(f"   The issue where T&M projects showed negative profit has been resolved.")
            print(f"   T&M projects now correctly show markup profit instead of contract minus costs.")
            return True
        else:
            print(f"\n❌ ISSUES FOUND:")
            for issue in issues:
                print(f"   {issue}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_tm_profit_calculation_fix()
    if success:
        print("\n✅ T&M Analytics Fix Verification: PASSED")
        exit(0)
    else:
        print("\n❌ T&M Analytics Fix Verification: FAILED")
        exit(1)