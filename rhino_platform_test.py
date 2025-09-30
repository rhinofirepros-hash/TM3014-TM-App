#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Rhino Platform API System
Tests the new Rhino Platform backend server that implements:
1. Project-based T&M billing (not per-person rates)
2. Single-domain authentication  
3. Cashflow management system
4. New data models and business logic
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any, List
import uuid

# Configuration
BACKEND_URL = "http://localhost:8002"
API_BASE = f"{BACKEND_URL}/api"

class RhinoPlatformTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.created_resources = {
            'projects': [],
            'installers': [],
            'timelogs': [],
            'cashflows': []
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response': response_data
        })
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Service: {data.get('service', 'Unknown')}, Status: {data.get('status', 'Unknown')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test admin authentication with PIN J777"""
        try:
            # Test valid admin PIN
            response = self.session.post(f"{API_BASE}/auth/admin", json={"pin": "J777"})
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('role') == 'admin':
                    self.admin_token = data.get('token')
                    self.log_test("Admin Authentication - Valid PIN J777", True, f"Token received: {self.admin_token[:20]}...")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                    
                    # Test invalid PIN
                    invalid_response = self.session.post(f"{API_BASE}/auth/admin", json={"pin": "INVALID"})
                    if invalid_response.status_code == 401:
                        self.log_test("Admin Authentication - Invalid PIN Rejection", True, "Invalid PIN correctly rejected")
                        return True
                    else:
                        self.log_test("Admin Authentication - Invalid PIN Rejection", False, f"Expected 401, got {invalid_response.status_code}")
                        return False
                else:
                    self.log_test("Admin Authentication - Valid PIN J777", False, "Invalid response structure", data)
                    return False
            else:
                self.log_test("Admin Authentication - Valid PIN J777", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_installer_management(self):
        """Test installer CRUD operations"""
        try:
            # Test GET installers (empty initially)
            response = self.session.get(f"{API_BASE}/installers")
            if response.status_code == 200:
                installers = response.json()
                self.log_test("Get Installers - Initial", True, f"Found {len(installers)} installers")
            else:
                self.log_test("Get Installers - Initial", False, f"Status code: {response.status_code}")
                return False
            
            # Test CREATE installer
            installer_data = {
                "name": "Mike Rodriguez",
                "cost_rate": 65.0,
                "position": "Senior Fire Protection Installer",
                "active": True,
                "phone": "555-0123",
                "email": "mike.rodriguez@rhinofire.com"
            }
            
            response = self.session.post(f"{API_BASE}/installers", json=installer_data)
            if response.status_code == 200:
                installer = response.json()
                installer_id = installer['id']
                self.created_resources['installers'].append(installer_id)
                self.log_test("Create Installer", True, f"Created installer: {installer['name']} at ${installer['cost_rate']}/hr")
                
                # Test GET specific installer
                response = self.session.get(f"{API_BASE}/installers/{installer_id}")
                if response.status_code == 200:
                    retrieved_installer = response.json()
                    if retrieved_installer['name'] == installer_data['name']:
                        self.log_test("Get Specific Installer", True, f"Retrieved installer: {retrieved_installer['name']}")
                    else:
                        self.log_test("Get Specific Installer", False, "Data mismatch")
                        return False
                else:
                    self.log_test("Get Specific Installer", False, f"Status code: {response.status_code}")
                    return False
                
                # Test UPDATE installer
                update_data = {"cost_rate": 70.0, "position": "Lead Fire Protection Installer"}
                response = self.session.put(f"{API_BASE}/installers/{installer_id}", json=update_data)
                if response.status_code == 200:
                    updated_installer = response.json()
                    if updated_installer['cost_rate'] == 70.0:
                        self.log_test("Update Installer", True, f"Updated cost rate to ${updated_installer['cost_rate']}/hr")
                    else:
                        self.log_test("Update Installer", False, "Update not reflected")
                        return False
                else:
                    self.log_test("Update Installer", False, f"Status code: {response.status_code}")
                    return False
                
                # Create second installer for testing
                installer2_data = {
                    "name": "Sarah Johnson",
                    "cost_rate": 60.0,
                    "position": "Fire Protection Installer",
                    "active": True
                }
                
                response = self.session.post(f"{API_BASE}/installers", json=installer2_data)
                if response.status_code == 200:
                    installer2 = response.json()
                    self.created_resources['installers'].append(installer2['id'])
                    self.log_test("Create Second Installer", True, f"Created installer: {installer2['name']}")
                else:
                    self.log_test("Create Second Installer", False, f"Status code: {response.status_code}")
                    return False
                
                return True
            else:
                self.log_test("Create Installer", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Installer Management", False, f"Exception: {str(e)}")
            return False
    
    def test_project_management(self):
        """Test project CRUD operations with T&M billing validation"""
        try:
            # Test GET projects (empty initially)
            response = self.session.get(f"{API_BASE}/projects")
            if response.status_code == 200:
                projects = response.json()
                self.log_test("Get Projects - Initial", True, f"Found {len(projects)} projects")
            else:
                self.log_test("Get Projects - Initial", False, f"Status code: {response.status_code}")
                return False
            
            # Test CREATE T&M project (should require tm_bill_rate)
            import time
            timestamp = int(time.time())
            tm_project_data = {
                "name": f"3rd Ave Fire Protection {timestamp}",
                "billing_type": "TM",
                "tm_bill_rate": 95.0,
                "description": "Fire Protection system completion",
                "client_company": "Nuera Contracting LP",
                "project_manager": "Jesus Garcia",
                "address": "123 3rd Ave, Seattle, WA"
            }
            
            response = self.session.post(f"{API_BASE}/projects", json=tm_project_data)
            if response.status_code == 200:
                tm_project = response.json()
                tm_project_id = tm_project['id']
                self.created_resources['projects'].append(tm_project_id)
                self.log_test("Create T&M Project", True, f"Created T&M project: {tm_project['name']} at ${tm_project['tm_bill_rate']}/hr")
                
                # Test CREATE Fixed project (should NOT have tm_bill_rate)
                fixed_project_data = {
                    "name": f"Oregon St Fixed Contract {timestamp}",
                    "billing_type": "Fixed",
                    "description": "Fixed price fire sprinkler installation",
                    "client_company": "Camelot Development Group Inc",
                    "contract_amount": 50000.0
                }
                
                response = self.session.post(f"{API_BASE}/projects", json=fixed_project_data)
                if response.status_code == 200:
                    fixed_project = response.json()
                    fixed_project_id = fixed_project['id']
                    self.created_resources['projects'].append(fixed_project_id)
                    
                    # Verify tm_bill_rate is null for non-T&M project
                    if fixed_project.get('tm_bill_rate') is None:
                        self.log_test("Create Fixed Project", True, f"Created Fixed project: {fixed_project['name']} (tm_bill_rate correctly null)")
                    else:
                        self.log_test("Create Fixed Project", False, f"tm_bill_rate should be null for Fixed projects, got: {fixed_project.get('tm_bill_rate')}")
                        return False
                else:
                    self.log_test("Create Fixed Project", False, f"Status code: {response.status_code}")
                    return False
                
                # Test validation: T&M project without tm_bill_rate should fail
                invalid_tm_project = {
                    "name": f"Invalid T&M Project {timestamp}",
                    "billing_type": "TM",
                    "description": "This should fail validation"
                }
                
                response = self.session.post(f"{API_BASE}/projects", json=invalid_tm_project)
                if response.status_code == 422:
                    self.log_test("T&M Project Validation", True, "T&M project without tm_bill_rate correctly rejected")
                else:
                    self.log_test("T&M Project Validation", False, f"Expected 422, got {response.status_code}")
                    return False
                
                # Test GET specific project
                response = self.session.get(f"{API_BASE}/projects/{tm_project_id}")
                if response.status_code == 200:
                    retrieved_project = response.json()
                    if retrieved_project['name'] == tm_project_data['name']:
                        self.log_test("Get Specific Project", True, f"Retrieved project: {retrieved_project['name']}")
                    else:
                        self.log_test("Get Specific Project", False, "Data mismatch")
                        return False
                else:
                    self.log_test("Get Specific Project", False, f"Status code: {response.status_code}")
                    return False
                
                # Test UPDATE project
                update_data = {"tm_bill_rate": 100.0, "description": "Updated fire protection system"}
                response = self.session.put(f"{API_BASE}/projects/{tm_project_id}", json=update_data)
                if response.status_code == 200:
                    updated_project = response.json()
                    if updated_project['tm_bill_rate'] == 100.0:
                        self.log_test("Update Project", True, f"Updated T&M rate to ${updated_project['tm_bill_rate']}/hr")
                    else:
                        self.log_test("Update Project", False, "Update not reflected")
                        return False
                else:
                    self.log_test("Update Project", False, f"Status code: {response.status_code}")
                    return False
                
                return True
            else:
                self.log_test("Create T&M Project", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Project Management", False, f"Exception: {str(e)}")
            return False
    
    def test_time_log_management(self):
        """Test time log creation with T&M calculations"""
        try:
            # Ensure we have installers and projects
            if not self.created_resources['installers'] or not self.created_resources['projects']:
                self.log_test("Time Log Prerequisites", False, "Need installers and projects first")
                return False
            
            installer_id = self.created_resources['installers'][0]
            tm_project_id = self.created_resources['projects'][0]  # Should be T&M project
            
            # Test CREATE time log
            timelog_data = {
                "date": "2024-01-15",
                "installer_id": installer_id,
                "project_id": tm_project_id,
                "hours": 8.0,
                "notes": "Fire protection system installation work"
            }
            
            response = self.session.post(f"{API_BASE}/timelogs", json=timelog_data)
            if response.status_code == 200:
                timelog = response.json()
                timelog_id = timelog['id']
                self.created_resources['timelogs'].append(timelog_id)
                self.log_test("Create Time Log", True, f"Created time log: {timelog['hours']} hours")
                
                # Test GET time logs with calculations
                response = self.session.get(f"{API_BASE}/timelogs")
                if response.status_code == 200:
                    timelogs = response.json()
                    if len(timelogs) > 0:
                        effective_log = timelogs[0]
                        
                        # Verify T&M calculations
                        if effective_log.get('billable') is not None and effective_log.get('profit') is not None:
                            expected_billable = effective_log['hours'] * effective_log['eff_bill_rate']
                            expected_profit = expected_billable - effective_log['labor_cost']
                            
                            if abs(effective_log['billable'] - expected_billable) < 0.01:
                                self.log_test("T&M Billing Calculation", True, 
                                    f"Billable: ${effective_log['billable']:.2f} = {effective_log['hours']}h × ${effective_log['eff_bill_rate']}/hr")
                            else:
                                self.log_test("T&M Billing Calculation", False, 
                                    f"Expected ${expected_billable:.2f}, got ${effective_log['billable']:.2f}")
                                return False
                            
                            if abs(effective_log['profit'] - expected_profit) < 0.01:
                                self.log_test("T&M Profit Calculation", True, 
                                    f"Profit: ${effective_log['profit']:.2f} = ${effective_log['billable']:.2f} - ${effective_log['labor_cost']:.2f}")
                            else:
                                self.log_test("T&M Profit Calculation", False, 
                                    f"Expected ${expected_profit:.2f}, got ${effective_log['profit']:.2f}")
                                return False
                        else:
                            self.log_test("T&M Calculations", False, "Missing billable or profit calculations")
                            return False
                    else:
                        self.log_test("Get Time Logs", False, "No time logs returned")
                        return False
                else:
                    self.log_test("Get Time Logs", False, f"Status code: {response.status_code}")
                    return False
                
                # Test bill_rate_override functionality
                override_timelog_data = {
                    "date": "2024-01-16",
                    "installer_id": installer_id,
                    "project_id": tm_project_id,
                    "hours": 4.0,
                    "bill_rate_override": 110.0,
                    "notes": "Premium rate work"
                }
                
                response = self.session.post(f"{API_BASE}/timelogs", json=override_timelog_data)
                if response.status_code == 200:
                    override_log = response.json()
                    self.created_resources['timelogs'].append(override_log['id'])
                    self.log_test("Create Time Log with Override", True, f"Created time log with override rate: $110/hr")
                    
                    # Verify override is used in calculations
                    response = self.session.get(f"{API_BASE}/timelogs")
                    if response.status_code == 200:
                        all_logs = response.json()
                        override_effective = next((log for log in all_logs if log['id'] == override_log['id']), None)
                        
                        if override_effective and override_effective.get('eff_bill_rate') == 110.0:
                            self.log_test("Bill Rate Override", True, f"Override rate correctly applied: ${override_effective['eff_bill_rate']}/hr")
                        else:
                            self.log_test("Bill Rate Override", False, "Override rate not applied correctly")
                            return False
                    else:
                        self.log_test("Verify Override Rate", False, f"Status code: {response.status_code}")
                        return False
                else:
                    self.log_test("Create Time Log with Override", False, f"Status code: {response.status_code}")
                    return False
                
                # Test time log for non-T&M project (should have billable = null)
                if len(self.created_resources['projects']) > 1:
                    fixed_project_id = self.created_resources['projects'][1]  # Should be Fixed project
                    
                    fixed_timelog_data = {
                        "date": "2024-01-17",
                        "installer_id": installer_id,
                        "project_id": fixed_project_id,
                        "hours": 6.0,
                        "notes": "Fixed contract work"
                    }
                    
                    response = self.session.post(f"{API_BASE}/timelogs", json=fixed_timelog_data)
                    if response.status_code == 200:
                        fixed_log = response.json()
                        self.created_resources['timelogs'].append(fixed_log['id'])
                        
                        # Verify non-T&M project has no hourly billing
                        response = self.session.get(f"{API_BASE}/timelogs")
                        if response.status_code == 200:
                            all_logs = response.json()
                            fixed_effective = next((log for log in all_logs if log['id'] == fixed_log['id']), None)
                            
                            if fixed_effective and fixed_effective.get('billable') is None:
                                self.log_test("Non-T&M Project Billing", True, "Fixed project correctly has billable = null")
                            else:
                                self.log_test("Non-T&M Project Billing", False, f"Fixed project should have billable = null, got: {fixed_effective.get('billable')}")
                                return False
                        else:
                            self.log_test("Verify Non-T&M Billing", False, f"Status code: {response.status_code}")
                            return False
                    else:
                        self.log_test("Create Fixed Project Time Log", False, f"Status code: {response.status_code}")
                        return False
                
                return True
            else:
                self.log_test("Create Time Log", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Time Log Management", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_summary(self):
        """Test /api/summary/tm endpoint for T&M project totals"""
        try:
            response = self.session.get(f"{API_BASE}/summary/tm")
            if response.status_code == 200:
                summary = response.json()
                
                # Verify structure
                if 'tm_project_totals' in summary and 'cash_balance' in summary:
                    tm_totals = summary['tm_project_totals']
                    cash_balance = summary['cash_balance']
                    
                    self.log_test("T&M Summary Structure", True, f"Found {len(tm_totals)} T&M projects")
                    
                    # Verify T&M project calculations
                    if len(tm_totals) > 0:
                        project_total = tm_totals[0]
                        required_fields = ['project', 'project_id', 'hours', 'labor_cost', 'billable', 'profit']
                        
                        if all(field in project_total for field in required_fields):
                            # Verify profit calculation
                            expected_profit = project_total['billable'] - project_total['labor_cost']
                            if abs(project_total['profit'] - expected_profit) < 0.01:
                                self.log_test("T&M Profit Calculation", True, 
                                    f"Project: {project_total['project']}, Profit: ${project_total['profit']:.2f}")
                            else:
                                self.log_test("T&M Profit Calculation", False, 
                                    f"Expected ${expected_profit:.2f}, got ${project_total['profit']:.2f}")
                                return False
                        else:
                            missing_fields = [f for f in required_fields if f not in project_total]
                            self.log_test("T&M Project Fields", False, f"Missing fields: {missing_fields}")
                            return False
                    
                    # Verify cash balance structure
                    balance_fields = ['current_balance', 'starting_balance', 'total_inflows', 'total_outflows']
                    if all(field in cash_balance for field in balance_fields):
                        self.log_test("Cash Balance Structure", True, 
                            f"Current balance: ${cash_balance['current_balance']:.2f}")
                    else:
                        missing_fields = [f for f in balance_fields if f not in cash_balance]
                        self.log_test("Cash Balance Structure", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    return True
                else:
                    self.log_test("T&M Summary Structure", False, "Missing tm_project_totals or cash_balance")
                    return False
            else:
                self.log_test("Get T&M Summary", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Analytics Summary", False, f"Exception: {str(e)}")
            return False
    
    def test_cashflow_management(self):
        """Test cashflow CRUD operations and balance calculations"""
        try:
            # Test GET cashflows (empty initially)
            response = self.session.get(f"{API_BASE}/cashflows")
            if response.status_code == 200:
                cashflows = response.json()
                self.log_test("Get Cashflows - Initial", True, f"Found {len(cashflows)} cashflow entries")
            else:
                self.log_test("Get Cashflows - Initial", False, f"Status code: {response.status_code}")
                return False
            
            # Test CREATE inflow
            inflow_data = {
                "date": "2024-01-15",
                "type": "inflow",
                "category": "Deposit",
                "amount": 25000.0,
                "reference": "Client payment - 3rd Ave project"
            }
            
            if self.created_resources['projects']:
                inflow_data["project_id"] = self.created_resources['projects'][0]
            
            response = self.session.post(f"{API_BASE}/cashflows", json=inflow_data)
            if response.status_code == 200:
                inflow = response.json()
                self.created_resources['cashflows'].append(inflow['id'])
                self.log_test("Create Cashflow Inflow", True, f"Created inflow: ${inflow['amount']} ({inflow['category']})")
                
                # Test CREATE outflow
                outflow_data = {
                    "date": "2024-01-16",
                    "type": "outflow",
                    "category": "Labor",
                    "amount": 5600.0,
                    "reference": "Weekly payroll"
                }
                
                response = self.session.post(f"{API_BASE}/cashflows", json=outflow_data)
                if response.status_code == 200:
                    outflow = response.json()
                    self.created_resources['cashflows'].append(outflow['id'])
                    self.log_test("Create Cashflow Outflow", True, f"Created outflow: ${outflow['amount']} ({outflow['category']})")
                    
                    # Test balance calculation
                    response = self.session.get(f"{API_BASE}/summary/tm")
                    if response.status_code == 200:
                        summary = response.json()
                        cash_balance = summary['cash_balance']
                        
                        # Verify balance calculation
                        expected_balance = cash_balance['starting_balance'] + cash_balance['total_inflows'] - cash_balance['total_outflows']
                        if abs(cash_balance['current_balance'] - expected_balance) < 0.01:
                            self.log_test("Cashflow Balance Calculation", True, 
                                f"Balance: ${cash_balance['current_balance']:.2f} = ${cash_balance['starting_balance']:.2f} + ${cash_balance['total_inflows']:.2f} - ${cash_balance['total_outflows']:.2f}")
                        else:
                            self.log_test("Cashflow Balance Calculation", False, 
                                f"Expected ${expected_balance:.2f}, got ${cash_balance['current_balance']:.2f}")
                            return False
                    else:
                        self.log_test("Verify Balance Calculation", False, f"Status code: {response.status_code}")
                        return False
                    
                    # Test different transaction types and categories
                    test_transactions = [
                        {"type": "outflow", "category": "Per Diem", "amount": 320.0, "reference": "Per diem expenses"},
                        {"type": "outflow", "category": "Hotels", "amount": 750.0, "reference": "Hotel accommodations"},
                        {"type": "outflow", "category": "Material", "amount": 2500.0, "reference": "Fire protection materials"},
                        {"type": "inflow", "category": "Deposit", "amount": 15000.0, "reference": "Progress payment"}
                    ]
                    
                    for i, transaction in enumerate(test_transactions):
                        transaction["date"] = f"2024-01-{17+i}"
                        response = self.session.post(f"{API_BASE}/cashflows", json=transaction)
                        if response.status_code == 200:
                            created_transaction = response.json()
                            self.created_resources['cashflows'].append(created_transaction['id'])
                        else:
                            self.log_test(f"Create {transaction['category']} Transaction", False, f"Status code: {response.status_code}")
                            return False
                    
                    self.log_test("Multiple Transaction Types", True, f"Created {len(test_transactions)} different transaction types")
                    
                    return True
                else:
                    self.log_test("Create Cashflow Outflow", False, f"Status code: {response.status_code}")
                    return False
            else:
                self.log_test("Create Cashflow Inflow", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Cashflow Management", False, f"Exception: {str(e)}")
            return False
    
    def test_business_logic_validation(self):
        """Test business logic and data model compliance"""
        try:
            # Test project-specific T&M rates (3rd Ave = $95/hr, Oregon St = $90/hr)
            oregon_project_data = {
                "name": "Oregon St T&M Project",
                "billing_type": "TM",
                "tm_bill_rate": 90.0,
                "description": "Fire Sprinkler system installation",
                "client_company": "Camelot Development Group Inc"
            }
            
            response = self.session.post(f"{API_BASE}/projects", json=oregon_project_data)
            if response.status_code == 200:
                oregon_project = response.json()
                oregon_project_id = oregon_project['id']
                self.created_resources['projects'].append(oregon_project_id)
                
                if oregon_project['tm_bill_rate'] == 90.0:
                    self.log_test("Project-Specific T&M Rate", True, f"Oregon St project: ${oregon_project['tm_bill_rate']}/hr")
                else:
                    self.log_test("Project-Specific T&M Rate", False, f"Expected $90/hr, got ${oregon_project['tm_bill_rate']}/hr")
                    return False
            else:
                self.log_test("Create Oregon St Project", False, f"Status code: {response.status_code}")
                return False
            
            # Test enum validations
            invalid_billing_type = {
                "name": "Invalid Billing Type Project",
                "billing_type": "INVALID",
                "description": "This should fail"
            }
            
            response = self.session.post(f"{API_BASE}/projects", json=invalid_billing_type)
            if response.status_code == 422:
                self.log_test("Billing Type Enum Validation", True, "Invalid billing type correctly rejected")
            else:
                self.log_test("Billing Type Enum Validation", False, f"Expected 422, got {response.status_code}")
                return False
            
            # Test field constraints (hours 0-16)
            if self.created_resources['installers'] and self.created_resources['projects']:
                invalid_hours_data = {
                    "date": "2024-01-20",
                    "installer_id": self.created_resources['installers'][0],
                    "project_id": self.created_resources['projects'][0],
                    "hours": 20.0,  # Invalid: > 16
                    "notes": "This should fail validation"
                }
                
                response = self.session.post(f"{API_BASE}/timelogs", json=invalid_hours_data)
                if response.status_code == 422:
                    self.log_test("Hours Constraint Validation", True, "Hours > 16 correctly rejected")
                else:
                    self.log_test("Hours Constraint Validation", False, f"Expected 422, got {response.status_code}")
                    return False
            
            # Test that installers only store cost_rate (no GC billing fields)
            response = self.session.get(f"{API_BASE}/installers")
            if response.status_code == 200:
                installers = response.json()
                if len(installers) > 0:
                    installer = installers[0]
                    
                    # Verify installer has cost_rate but no billing fields
                    if 'cost_rate' in installer and 'gc_billing_rate' not in installer and 'bill_rate' not in installer:
                        self.log_test("Installer Data Structure", True, "Installers correctly store only cost_rate")
                    else:
                        self.log_test("Installer Data Structure", False, "Installers should only have cost_rate, not billing fields")
                        return False
            
            return True
            
        except Exception as e:
            self.log_test("Business Logic Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Rhino Platform Backend Testing")
        print("=" * 60)
        
        # Test sequence
        test_suites = [
            ("Health Check", self.test_health_check),
            ("Admin Authentication", self.test_admin_authentication),
            ("Installer Management", self.test_installer_management),
            ("Project Management", self.test_project_management),
            ("Time Log Management", self.test_time_log_management),
            ("Analytics & Summary", self.test_analytics_summary),
            ("Cashflow Management", self.test_cashflow_management),
            ("Business Logic Validation", self.test_business_logic_validation)
        ]
        
        passed = 0
        total = len(test_suites)
        
        for suite_name, test_func in test_suites:
            print(f"\n📋 Testing {suite_name}")
            print("-" * 40)
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
            except Exception as e:
                print(f"❌ {suite_name} - EXCEPTION: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Test Suites Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        # Detailed results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        test_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Individual Tests: {passed_tests}/{total_tests} ({test_success_rate:.1f}%)")
        
        # Failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Created resources summary
        print(f"\n📊 CREATED RESOURCES:")
        for resource_type, resources in self.created_resources.items():
            print(f"   • {resource_type}: {len(resources)}")
        
        print("\n🏁 Testing Complete!")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

def main():
    """Main test execution"""
    tester = RhinoPlatformTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()