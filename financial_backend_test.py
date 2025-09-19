#!/usr/bin/env python3
"""
Financial Management System API Testing
Tests the newly implemented financial management endpoints according to user specification
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"

class FinancialAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = {
            "invoices": {"passed": 0, "failed": 0, "errors": []},
            "payables": {"passed": 0, "failed": 0, "errors": []},
            "cashflow": {"passed": 0, "failed": 0, "errors": []},
            "profitability": {"passed": 0, "failed": 0, "errors": []},
            "health": {"passed": 0, "failed": 0, "errors": []},
            "general": {"passed": 0, "failed": 0, "errors": []}
        }
        self.created_project_id = None
        self.created_invoice_id = None
        self.created_payable_id = None
        self.created_forecast_id = None
        self.created_profitability_id = None
        
    def log_result(self, category, test_name, success, message="", response=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED")
            if message:
                print(f"   {message}")
        else:
            self.test_results[category]["failed"] += 1
            error_msg = f"{test_name}: FAILED - {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.test_results[category]["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check Endpoint ===")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_result("health", "Health check endpoint", True, "Health endpoint accessible")
                return True
            else:
                self.log_result("health", "Health check endpoint", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("health", "Health check endpoint", False, str(e))
            return False
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing Basic Connectivity ===")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_result("general", "Basic connectivity", True)
                return True
            else:
                self.log_result("general", "Basic connectivity", False, f"Status code: {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("general", "Basic connectivity", False, str(e))
            return False
    
    def setup_test_project(self):
        """Create a test project for financial testing"""
        print("\n=== Setting Up Test Project ===")
        project_data = {
            "name": "Financial Test Project",
            "description": "Project for testing financial management endpoints",
            "client_company": "Test Financial Corp",
            "gc_email": "finance@testcorp.com",
            "contract_amount": 100000.00,
            "labor_rate": 95.0,
            "project_manager": "Test Manager",
            "start_date": datetime.now().isoformat(),
            "address": "123 Financial Test St"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                project = response.json()
                self.created_project_id = project["id"]
                self.log_result("general", "Test project setup", True, f"Project ID: {self.created_project_id}")
                return project
            else:
                self.log_result("general", "Test project setup", False, f"HTTP {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_result("general", "Test project setup", False, str(e))
            return None
    
    def create_realistic_invoice_data(self, project_id):
        """Create realistic invoice data for testing"""
        return {
            "project_id": project_id,
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-001",
            "line_items": [
                {
                    "description": "Electrical Installation - Phase 1",
                    "qty": 40.0,
                    "unit_cost": 95.0,
                    "total": 3800.0
                },
                {
                    "description": "Materials and Supplies",
                    "qty": 1.0,
                    "unit_cost": 1500.0,
                    "total": 1500.0
                }
            ],
            "subtotal": 5300.0,
            "tax": 424.0,  # 8% tax
            "total": 5724.0,
            "due_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    def test_invoice_creation(self):
        """Test invoice creation endpoint"""
        print("\n=== Testing Invoice Creation ===")
        
        if not self.created_project_id:
            self.log_result("invoices", "Invoice creation", False, "No test project available")
            return None
        
        invoice_data = self.create_realistic_invoice_data(self.created_project_id)
        
        try:
            response = self.session.post(
                f"{self.base_url}/invoices",
                json=invoice_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                invoice = response.json()
                required_fields = ["id", "project_id", "invoice_number", "status", "line_items", "subtotal", "tax", "total", "due_date", "created_at"]
                missing_fields = [field for field in required_fields if field not in invoice]
                
                if not missing_fields:
                    self.created_invoice_id = invoice["id"]
                    # Verify status enum
                    if invoice["status"] in ["draft", "sent", "paid", "overdue"]:
                        self.log_result("invoices", "Invoice creation", True, f"Invoice {invoice['invoice_number']} created with status: {invoice['status']}")
                        return invoice
                    else:
                        self.log_result("invoices", "Invoice creation", False, f"Invalid status enum: {invoice['status']}")
                else:
                    self.log_result("invoices", "Invoice creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("invoices", "Invoice creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("invoices", "Invoice creation", False, str(e))
        
        return None
    
    def test_invoice_retrieval_by_project(self):
        """Test invoice retrieval by project ID"""
        print("\n=== Testing Invoice Retrieval by Project ===")
        
        if not self.created_project_id:
            self.log_result("invoices", "Invoice retrieval by project", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/invoices/{self.created_project_id}")
            
            if response.status_code == 200:
                invoices = response.json()
                if isinstance(invoices, list):
                    self.log_result("invoices", "Invoice retrieval by project", True, f"Retrieved {len(invoices)} invoices")
                    return invoices
                else:
                    self.log_result("invoices", "Invoice retrieval by project", False, "Response is not a list", response)
            else:
                self.log_result("invoices", "Invoice retrieval by project", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("invoices", "Invoice retrieval by project", False, str(e))
        
        return None
    
    def test_invoice_update(self):
        """Test invoice update endpoint"""
        print("\n=== Testing Invoice Update ===")
        
        if not self.created_invoice_id:
            self.log_result("invoices", "Invoice update", False, "No invoice available for update")
            return None
        
        update_data = {
            "status": "sent",
            "subtotal": 5500.0,
            "tax": 440.0,
            "total": 5940.0
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/invoices/{self.created_invoice_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_invoice = response.json()
                if (updated_invoice.get("status") == "sent" and 
                    updated_invoice.get("total") == 5940.0):
                    self.log_result("invoices", "Invoice update", True, f"Invoice updated to status: {updated_invoice['status']}")
                    return updated_invoice
                else:
                    self.log_result("invoices", "Invoice update", False, "Update not reflected in response", response)
            else:
                self.log_result("invoices", "Invoice update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("invoices", "Invoice update", False, str(e))
        
        return None
    
    def test_invoice_deletion(self):
        """Test invoice deletion endpoint"""
        print("\n=== Testing Invoice Deletion ===")
        
        if not self.created_invoice_id:
            self.log_result("invoices", "Invoice deletion", False, "No invoice available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/invoices/{self.created_invoice_id}")
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "deleted successfully" in result["message"]:
                    self.log_result("invoices", "Invoice deletion", True, f"Invoice {self.created_invoice_id} deleted")
                    return True
                else:
                    self.log_result("invoices", "Invoice deletion", False, "Unexpected response format", response)
            else:
                self.log_result("invoices", "Invoice deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("invoices", "Invoice deletion", False, str(e))
        
        return False
    
    def create_realistic_payable_data(self, project_id):
        """Create realistic payable data for testing"""
        return {
            "vendor_id": f"VENDOR-{str(uuid.uuid4())[:8]}",
            "project_id": project_id,
            "po_number": f"PO-{datetime.now().strftime('%Y%m%d')}-001",
            "description": "Electrical supplies and materials",
            "amount": 2500.00,
            "due_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    def test_payable_creation(self):
        """Test payable creation endpoint"""
        print("\n=== Testing Payable Creation ===")
        
        if not self.created_project_id:
            self.log_result("payables", "Payable creation", False, "No test project available")
            return None
        
        payable_data = self.create_realistic_payable_data(self.created_project_id)
        
        try:
            response = self.session.post(
                f"{self.base_url}/payables",
                json=payable_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                payable = response.json()
                required_fields = ["id", "vendor_id", "project_id", "description", "amount", "status", "due_date", "created_at"]
                missing_fields = [field for field in required_fields if field not in payable]
                
                if not missing_fields:
                    self.created_payable_id = payable["id"]
                    # Verify status enum
                    if payable["status"] in ["pending", "paid", "overdue"]:
                        self.log_result("payables", "Payable creation", True, f"Payable created with amount: ${payable['amount']}, status: {payable['status']}")
                        return payable
                    else:
                        self.log_result("payables", "Payable creation", False, f"Invalid status enum: {payable['status']}")
                else:
                    self.log_result("payables", "Payable creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("payables", "Payable creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("payables", "Payable creation", False, str(e))
        
        return None
    
    def test_payable_retrieval_by_project(self):
        """Test payable retrieval by project ID"""
        print("\n=== Testing Payable Retrieval by Project ===")
        
        if not self.created_project_id:
            self.log_result("payables", "Payable retrieval by project", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/payables/{self.created_project_id}")
            
            if response.status_code == 200:
                payables = response.json()
                if isinstance(payables, list):
                    self.log_result("payables", "Payable retrieval by project", True, f"Retrieved {len(payables)} payables")
                    return payables
                else:
                    self.log_result("payables", "Payable retrieval by project", False, "Response is not a list", response)
            else:
                self.log_result("payables", "Payable retrieval by project", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("payables", "Payable retrieval by project", False, str(e))
        
        return None
    
    def test_payable_update(self):
        """Test payable update endpoint"""
        print("\n=== Testing Payable Update ===")
        
        if not self.created_payable_id:
            self.log_result("payables", "Payable update", False, "No payable available for update")
            return None
        
        update_data = {
            "status": "paid",
            "amount": 2750.00,
            "description": "Updated electrical supplies and materials"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/payables/{self.created_payable_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_payable = response.json()
                if (updated_payable.get("status") == "paid" and 
                    updated_payable.get("amount") == 2750.00):
                    self.log_result("payables", "Payable update", True, f"Payable updated to status: {updated_payable['status']}")
                    return updated_payable
                else:
                    self.log_result("payables", "Payable update", False, "Update not reflected in response", response)
            else:
                self.log_result("payables", "Payable update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("payables", "Payable update", False, str(e))
        
        return None
    
    def test_payable_deletion(self):
        """Test payable deletion endpoint"""
        print("\n=== Testing Payable Deletion ===")
        
        if not self.created_payable_id:
            self.log_result("payables", "Payable deletion", False, "No payable available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/payables/{self.created_payable_id}")
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "deleted successfully" in result["message"]:
                    self.log_result("payables", "Payable deletion", True, f"Payable {self.created_payable_id} deleted")
                    return True
                else:
                    self.log_result("payables", "Payable deletion", False, "Unexpected response format", response)
            else:
                self.log_result("payables", "Payable deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("payables", "Payable deletion", False, str(e))
        
        return False
    
    def create_realistic_cashflow_data(self, project_id):
        """Create realistic cashflow forecast data for testing"""
        return {
            "project_id": project_id,
            "week_start": datetime.now().isoformat(),
            "inflow": 15000.0,
            "outflow": 8500.0,
            "net": 6500.0,
            "runway_weeks": 12,
            "notes": "Positive cashflow expected due to milestone payment"
        }
    
    def test_cashflow_creation(self):
        """Test cashflow forecast creation endpoint"""
        print("\n=== Testing Cashflow Forecast Creation ===")
        
        if not self.created_project_id:
            self.log_result("cashflow", "Cashflow creation", False, "No test project available")
            return None
        
        forecast_data = self.create_realistic_cashflow_data(self.created_project_id)
        
        try:
            response = self.session.post(
                f"{self.base_url}/cashflow",
                json=forecast_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                forecast = response.json()
                required_fields = ["id", "project_id", "week_start", "inflow", "outflow", "net", "runway_weeks", "created_at"]
                missing_fields = [field for field in required_fields if field not in forecast]
                
                if not missing_fields:
                    self.created_forecast_id = forecast["id"]
                    self.log_result("cashflow", "Cashflow creation", True, f"Forecast created with net: ${forecast['net']}, runway: {forecast['runway_weeks']} weeks")
                    return forecast
                else:
                    self.log_result("cashflow", "Cashflow creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("cashflow", "Cashflow creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("cashflow", "Cashflow creation", False, str(e))
        
        return None
    
    def test_cashflow_retrieval_by_project(self):
        """Test cashflow forecast retrieval by project ID"""
        print("\n=== Testing Cashflow Forecast Retrieval by Project ===")
        
        if not self.created_project_id:
            self.log_result("cashflow", "Cashflow retrieval by project", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/cashflow/{self.created_project_id}")
            
            if response.status_code == 200:
                forecasts = response.json()
                if isinstance(forecasts, list):
                    self.log_result("cashflow", "Cashflow retrieval by project", True, f"Retrieved {len(forecasts)} forecasts")
                    return forecasts
                else:
                    self.log_result("cashflow", "Cashflow retrieval by project", False, "Response is not a list", response)
            else:
                self.log_result("cashflow", "Cashflow retrieval by project", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("cashflow", "Cashflow retrieval by project", False, str(e))
        
        return None
    
    def test_cashflow_update(self):
        """Test cashflow forecast update endpoint"""
        print("\n=== Testing Cashflow Forecast Update ===")
        
        if not self.created_forecast_id:
            self.log_result("cashflow", "Cashflow update", False, "No forecast available for update")
            return None
        
        update_data = {
            "inflow": 18000.0,
            "outflow": 9000.0,
            "net": 9000.0,
            "runway_weeks": 15,
            "notes": "Updated forecast with revised milestone payments"
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/cashflow/{self.created_forecast_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_forecast = response.json()
                if (updated_forecast.get("net") == 9000.0 and 
                    updated_forecast.get("runway_weeks") == 15):
                    self.log_result("cashflow", "Cashflow update", True, f"Forecast updated with net: ${updated_forecast['net']}")
                    return updated_forecast
                else:
                    self.log_result("cashflow", "Cashflow update", False, "Update not reflected in response", response)
            else:
                self.log_result("cashflow", "Cashflow update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("cashflow", "Cashflow update", False, str(e))
        
        return None
    
    def test_cashflow_deletion(self):
        """Test cashflow forecast deletion endpoint"""
        print("\n=== Testing Cashflow Forecast Deletion ===")
        
        if not self.created_forecast_id:
            self.log_result("cashflow", "Cashflow deletion", False, "No forecast available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/cashflow/{self.created_forecast_id}")
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "deleted successfully" in result["message"]:
                    self.log_result("cashflow", "Cashflow deletion", True, f"Forecast {self.created_forecast_id} deleted")
                    return True
                else:
                    self.log_result("cashflow", "Cashflow deletion", False, "Unexpected response format", response)
            else:
                self.log_result("cashflow", "Cashflow deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("cashflow", "Cashflow deletion", False, str(e))
        
        return False
    
    def create_realistic_profitability_data(self, project_id):
        """Create realistic profitability data for testing"""
        return {
            "project_id": project_id,
            "revenue": 50000.0,
            "labor_cost": 25000.0,
            "material_cost": 12000.0,
            "overhead_cost": 5000.0,
            "profit_margin": 16.0,  # 16% margin
            "alerts": [
                {
                    "type": "low_margin",
                    "message": "Profit margin below target threshold",
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
    
    def test_profitability_creation(self):
        """Test profitability entry creation endpoint"""
        print("\n=== Testing Profitability Entry Creation ===")
        
        if not self.created_project_id:
            self.log_result("profitability", "Profitability creation", False, "No test project available")
            return None
        
        profitability_data = self.create_realistic_profitability_data(self.created_project_id)
        
        try:
            response = self.session.post(
                f"{self.base_url}/profitability",
                json=profitability_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                profitability = response.json()
                required_fields = ["id", "project_id", "revenue", "labor_cost", "material_cost", "overhead_cost", "profit_margin", "alerts", "created_at"]
                missing_fields = [field for field in required_fields if field not in profitability]
                
                if not missing_fields:
                    self.created_profitability_id = profitability["id"]
                    # Verify alert types
                    valid_alert_types = ["low_margin", "over_budget"]
                    alerts_valid = all(alert.get("type") in valid_alert_types for alert in profitability.get("alerts", []))
                    
                    if alerts_valid:
                        self.log_result("profitability", "Profitability creation", True, f"Profitability entry created with margin: {profitability['profit_margin']}%")
                        return profitability
                    else:
                        self.log_result("profitability", "Profitability creation", False, "Invalid alert types found")
                else:
                    self.log_result("profitability", "Profitability creation", False, f"Missing fields: {missing_fields}", response)
            else:
                self.log_result("profitability", "Profitability creation", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("profitability", "Profitability creation", False, str(e))
        
        return None
    
    def test_profitability_retrieval_by_project(self):
        """Test profitability data retrieval by project ID"""
        print("\n=== Testing Profitability Data Retrieval by Project ===")
        
        if not self.created_project_id:
            self.log_result("profitability", "Profitability retrieval by project", False, "No test project available")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/profitability/{self.created_project_id}")
            
            if response.status_code == 200:
                profitability_data = response.json()
                if isinstance(profitability_data, list):
                    self.log_result("profitability", "Profitability retrieval by project", True, f"Retrieved {len(profitability_data)} profitability entries")
                    return profitability_data
                else:
                    self.log_result("profitability", "Profitability retrieval by project", False, "Response is not a list", response)
            else:
                self.log_result("profitability", "Profitability retrieval by project", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("profitability", "Profitability retrieval by project", False, str(e))
        
        return None
    
    def test_profitability_update(self):
        """Test profitability entry update endpoint"""
        print("\n=== Testing Profitability Entry Update ===")
        
        if not self.created_profitability_id:
            self.log_result("profitability", "Profitability update", False, "No profitability entry available for update")
            return None
        
        update_data = {
            "revenue": 55000.0,
            "labor_cost": 26000.0,
            "material_cost": 13000.0,
            "overhead_cost": 5500.0,
            "profit_margin": 19.1,  # Improved margin
            "alerts": [
                {
                    "type": "over_budget",
                    "message": "Material costs exceeding budget",
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/profitability/{self.created_profitability_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_profitability = response.json()
                if (updated_profitability.get("profit_margin") == 19.1 and 
                    updated_profitability.get("revenue") == 55000.0):
                    self.log_result("profitability", "Profitability update", True, f"Profitability updated with margin: {updated_profitability['profit_margin']}%")
                    return updated_profitability
                else:
                    self.log_result("profitability", "Profitability update", False, "Update not reflected in response", response)
            else:
                self.log_result("profitability", "Profitability update", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("profitability", "Profitability update", False, str(e))
        
        return None
    
    def test_profitability_deletion(self):
        """Test profitability entry deletion endpoint"""
        print("\n=== Testing Profitability Entry Deletion ===")
        
        if not self.created_profitability_id:
            self.log_result("profitability", "Profitability deletion", False, "No profitability entry available for deletion")
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/profitability/{self.created_profitability_id}")
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "deleted successfully" in result["message"]:
                    self.log_result("profitability", "Profitability deletion", True, f"Profitability entry {self.created_profitability_id} deleted")
                    return True
                else:
                    self.log_result("profitability", "Profitability deletion", False, "Unexpected response format", response)
            else:
                self.log_result("profitability", "Profitability deletion", False, f"HTTP {response.status_code}", response)
                
        except Exception as e:
            self.log_result("profitability", "Profitability deletion", False, str(e))
        
        return False
    
    def test_data_validation(self):
        """Test data validation for all endpoints"""
        print("\n=== Testing Data Validation ===")
        
        # Test invalid invoice status
        try:
            invalid_invoice = {
                "project_id": self.created_project_id or str(uuid.uuid4()),
                "invoice_number": "TEST-INVALID",
                "line_items": [],
                "subtotal": 100.0,
                "tax": 8.0,
                "total": 108.0,
                "due_date": datetime.now().isoformat(),
                "status": "invalid_status"  # Invalid enum value
            }
            
            response = self.session.post(
                f"{self.base_url}/invoices",
                json=invalid_invoice,
                headers={"Content-Type": "application/json"}
            )
            
            # Should either reject with 422 or default to valid status
            if response.status_code in [422, 400]:
                self.log_result("general", "Invoice status validation", True, "Invalid status rejected")
            elif response.status_code == 200:
                invoice = response.json()
                if invoice.get("status") in ["draft", "sent", "paid", "overdue"]:
                    self.log_result("general", "Invoice status validation", True, "Invalid status defaulted to valid value")
                else:
                    self.log_result("general", "Invoice status validation", False, "Invalid status accepted")
            else:
                self.log_result("general", "Invoice status validation", False, f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_result("general", "Invoice status validation", False, str(e))
        
        # Test invalid payable status
        try:
            invalid_payable = {
                "vendor_id": "TEST-VENDOR",
                "project_id": self.created_project_id or str(uuid.uuid4()),
                "description": "Test payable",
                "amount": 100.0,
                "due_date": datetime.now().isoformat(),
                "status": "invalid_payable_status"  # Invalid enum value
            }
            
            response = self.session.post(
                f"{self.base_url}/payables",
                json=invalid_payable,
                headers={"Content-Type": "application/json"}
            )
            
            # Should either reject with 422 or default to valid status
            if response.status_code in [422, 400]:
                self.log_result("general", "Payable status validation", True, "Invalid status rejected")
            elif response.status_code == 200:
                payable = response.json()
                if payable.get("status") in ["pending", "paid", "overdue"]:
                    self.log_result("general", "Payable status validation", True, "Invalid status defaulted to valid value")
                else:
                    self.log_result("general", "Payable status validation", False, "Invalid status accepted")
            else:
                self.log_result("general", "Payable status validation", False, f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_result("general", "Payable status validation", False, str(e))
    
    def test_database_integration(self):
        """Test database integration and data persistence"""
        print("\n=== Testing Database Integration ===")
        
        # Test that data persists across requests
        if self.created_project_id:
            try:
                # Create an invoice
                invoice_data = self.create_realistic_invoice_data(self.created_project_id)
                create_response = self.session.post(
                    f"{self.base_url}/invoices",
                    json=invoice_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if create_response.status_code == 200:
                    invoice = create_response.json()
                    invoice_id = invoice["id"]
                    
                    # Retrieve the same invoice
                    get_response = self.session.get(f"{self.base_url}/invoices/{self.created_project_id}")
                    
                    if get_response.status_code == 200:
                        invoices = get_response.json()
                        found_invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
                        
                        if found_invoice:
                            self.log_result("general", "Database persistence", True, "Data persisted correctly in MongoDB")
                        else:
                            self.log_result("general", "Database persistence", False, "Created invoice not found in retrieval")
                    else:
                        self.log_result("general", "Database persistence", False, "Could not retrieve invoices for verification")
                else:
                    self.log_result("general", "Database persistence", False, "Could not create invoice for persistence test")
                    
            except Exception as e:
                self.log_result("general", "Database persistence", False, str(e))
    
    def run_comprehensive_tests(self):
        """Run all financial management system tests"""
        print("🚀 Starting Comprehensive Financial Management System API Testing")
        print("=" * 80)
        
        # Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Aborting tests.")
            return False
        
        # Health check
        self.test_health_endpoint()
        
        # Setup test project
        if not self.setup_test_project():
            print("❌ Could not set up test project. Some tests may fail.")
        
        # Invoice tests
        print("\n" + "="*50)
        print("TESTING INVOICE ENDPOINTS")
        print("="*50)
        self.test_invoice_creation()
        self.test_invoice_retrieval_by_project()
        self.test_invoice_update()
        self.test_invoice_deletion()
        
        # Payable tests
        print("\n" + "="*50)
        print("TESTING PAYABLE ENDPOINTS")
        print("="*50)
        self.test_payable_creation()
        self.test_payable_retrieval_by_project()
        self.test_payable_update()
        self.test_payable_deletion()
        
        # Cashflow tests
        print("\n" + "="*50)
        print("TESTING CASHFLOW ENDPOINTS")
        print("="*50)
        self.test_cashflow_creation()
        self.test_cashflow_retrieval_by_project()
        self.test_cashflow_update()
        self.test_cashflow_deletion()
        
        # Profitability tests
        print("\n" + "="*50)
        print("TESTING PROFITABILITY ENDPOINTS")
        print("="*50)
        self.test_profitability_creation()
        self.test_profitability_retrieval_by_project()
        self.test_profitability_update()
        self.test_profitability_deletion()
        
        # Data validation tests
        print("\n" + "="*50)
        print("TESTING DATA VALIDATION")
        print("="*50)
        self.test_data_validation()
        
        # Database integration tests
        print("\n" + "="*50)
        print("TESTING DATABASE INTEGRATION")
        print("="*50)
        self.test_database_integration()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 FINANCIAL MANAGEMENT SYSTEM API TEST SUMMARY")
        print("="*80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper():20} | {status} | Passed: {passed:2d} | Failed: {failed:2d}")
            
            # Print errors if any
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print("-" * 80)
        success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"OVERALL RESULT: {total_passed} passed, {total_failed} failed ({success_rate:.1f}% success rate)")
        
        if total_failed == 0:
            print("🎉 ALL FINANCIAL MANAGEMENT ENDPOINTS ARE WORKING PERFECTLY!")
        else:
            print(f"⚠️  {total_failed} issues found that need attention")
        
        print("="*80)

def main():
    """Main function to run financial API tests"""
    tester = FinancialAPITester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n✅ Financial Management System API testing completed successfully!")
    else:
        print("\n❌ Financial Management System API testing encountered issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()