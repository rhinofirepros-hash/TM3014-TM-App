#!/usr/bin/env python3
"""
Production PDF Functionality Test
Testing PDF export and preview functionality on production backend
"""

import requests
import json
from datetime import datetime, date
import uuid

PRODUCTION_BACKEND = "https://tm3014-tm-app-production.up.railway.app/api"

class ProductionPDFTester:
    def __init__(self):
        self.base_url = PRODUCTION_BACKEND
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_pdf_endpoints(self):
        """Test various PDF-related endpoints"""
        print("🔍 TESTING PDF FUNCTIONALITY ON PRODUCTION")
        print("="*60)
        
        # Comprehensive list of possible PDF endpoints
        pdf_endpoints = [
            # Direct PDF endpoints
            "/pdf", "/pdf/generate", "/pdf/export", "/pdf/preview",
            "/generate-pdf", "/export-pdf", "/create-pdf",
            
            # T&M/Timelog PDF endpoints
            "/timelogs/pdf", "/timelogs/export", "/timelogs/generate-pdf",
            "/tm-tags/pdf", "/tm-tags/export",
            
            # Report endpoints
            "/reports", "/reports/pdf", "/reports/generate",
            "/export", "/export/timelogs", "/export/reports",
            
            # Project-specific PDF
            "/projects/pdf", "/projects/export", "/projects/reports",
            
            # Summary/Invoice PDF
            "/summary/pdf", "/invoices/pdf", "/billing/pdf"
        ]
        
        working_pdf_endpoints = []
        
        for endpoint in pdf_endpoints:
            try:
                print(f"📋 Testing {endpoint}...")
                
                # Test GET request
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    print(f"   ✅ GET {endpoint} - Working (200)")
                    working_pdf_endpoints.append((endpoint, "GET", 200))
                elif response.status_code == 405:
                    print(f"   ⚠️ GET {endpoint} - Method not allowed (405) - trying POST")
                    
                    # Try POST with sample data
                    sample_data = {
                        "project_id": "test-project",
                        "timelog_id": "test-timelog",
                        "format": "pdf"
                    }
                    
                    post_response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=sample_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if post_response.status_code == 200:
                        print(f"   ✅ POST {endpoint} - Working (200)")
                        working_pdf_endpoints.append((endpoint, "POST", 200))
                    elif post_response.status_code == 422:
                        print(f"   ⚠️ POST {endpoint} - Validation error (422) - endpoint exists")
                        working_pdf_endpoints.append((endpoint, "POST", 422))
                    else:
                        print(f"   ❌ POST {endpoint} - Failed ({post_response.status_code})")
                        
                elif response.status_code == 404:
                    pass  # Skip 404s
                else:
                    print(f"   ❓ GET {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                pass  # Skip errors
        
        print(f"\n📊 PDF ENDPOINTS SUMMARY:")
        if working_pdf_endpoints:
            print("   Found working PDF endpoints:")
            for endpoint, method, status in working_pdf_endpoints:
                print(f"   ✅ {method} {endpoint} (Status: {status})")
        else:
            print("   ❌ No working PDF endpoints found")
            
        return working_pdf_endpoints
    
    def test_pdf_generation_with_real_data(self):
        """Test PDF generation with real timelog data"""
        print(f"\n📄 TESTING PDF GENERATION WITH REAL DATA")
        print("="*60)
        
        # Get real timelogs first
        try:
            response = self.session.get(f"{self.base_url}/timelogs")
            if response.status_code == 200:
                timelogs = response.json()
                
                if timelogs:
                    test_timelog = timelogs[0]
                    print(f"🎯 Using timelog: {test_timelog.get('id')} for PDF test")
                    
                    # Test various PDF generation approaches
                    pdf_test_data = [
                        {
                            "endpoint": "/pdf/generate",
                            "data": {"timelog_id": test_timelog.get("id")}
                        },
                        {
                            "endpoint": "/timelogs/pdf",
                            "data": {"id": test_timelog.get("id")}
                        },
                        {
                            "endpoint": "/export/pdf",
                            "data": {
                                "type": "timelog",
                                "id": test_timelog.get("id")
                            }
                        },
                        {
                            "endpoint": "/reports/generate",
                            "data": {
                                "report_type": "timelog",
                                "timelog_id": test_timelog.get("id"),
                                "format": "pdf"
                            }
                        }
                    ]
                    
                    for test in pdf_test_data:
                        try:
                            print(f"📋 Testing PDF generation: {test['endpoint']}")
                            
                            response = self.session.post(
                                f"{self.base_url}{test['endpoint']}",
                                json=test['data'],
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if response.status_code == 200:
                                # Check if response is PDF
                                content_type = response.headers.get('content-type', '')
                                if 'pdf' in content_type.lower():
                                    print(f"   ✅ PDF generated successfully (Content-Type: {content_type})")
                                    print(f"   📏 PDF size: {len(response.content)} bytes")
                                else:
                                    print(f"   ⚠️ Response received but not PDF (Content-Type: {content_type})")
                            elif response.status_code == 404:
                                print(f"   ❌ Endpoint not found")
                            else:
                                print(f"   ❌ Failed (Status: {response.status_code})")
                                if response.text:
                                    print(f"   📝 Error: {response.text[:200]}")
                                    
                        except Exception as e:
                            print(f"   ❌ Error: {e}")
                else:
                    print("❌ No timelogs available for PDF testing")
            else:
                print(f"❌ Could not retrieve timelogs: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting timelogs: {e}")
    
    def test_pdf_preview_functionality(self):
        """Test PDF preview functionality"""
        print(f"\n👁️ TESTING PDF PREVIEW FUNCTIONALITY")
        print("="*60)
        
        preview_endpoints = [
            "/pdf/preview",
            "/timelogs/preview", 
            "/reports/preview",
            "/preview/pdf",
            "/preview/timelog"
        ]
        
        # Get a real timelog for testing
        try:
            response = self.session.get(f"{self.base_url}/timelogs")
            if response.status_code == 200:
                timelogs = response.json()
                
                if timelogs:
                    test_timelog = timelogs[0]
                    
                    for endpoint in preview_endpoints:
                        try:
                            print(f"👁️ Testing preview: {endpoint}")
                            
                            preview_data = {
                                "timelog_id": test_timelog.get("id"),
                                "format": "preview"
                            }
                            
                            response = self.session.post(
                                f"{self.base_url}{endpoint}",
                                json=preview_data,
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if response.status_code == 200:
                                content_type = response.headers.get('content-type', '')
                                print(f"   ✅ Preview working (Content-Type: {content_type})")
                                
                                # Check if it's HTML preview or image
                                if 'html' in content_type.lower():
                                    print(f"   📄 HTML preview ({len(response.content)} bytes)")
                                elif 'image' in content_type.lower():
                                    print(f"   🖼️ Image preview ({len(response.content)} bytes)")
                                else:
                                    print(f"   📄 Preview content ({len(response.content)} bytes)")
                            elif response.status_code == 404:
                                pass  # Skip 404s
                            else:
                                print(f"   ❌ Failed (Status: {response.status_code})")
                                
                        except Exception as e:
                            pass  # Skip errors
                else:
                    print("❌ No timelogs available for preview testing")
            else:
                print(f"❌ Could not retrieve timelogs for preview testing")
                
        except Exception as e:
            print(f"❌ Error in preview testing: {e}")
    
    def investigate_pdf_libraries(self):
        """Check if PDF generation libraries are available on the backend"""
        print(f"\n🔍 INVESTIGATING PDF CAPABILITIES")
        print("="*60)
        
        # Test health endpoint for PDF capabilities
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"📊 Backend health info:")
                for key, value in health_data.items():
                    print(f"   {key}: {value}")
                
                # Check if there are any PDF-related capabilities mentioned
                health_str = json.dumps(health_data).lower()
                pdf_indicators = ['pdf', 'reportlab', 'weasyprint', 'wkhtmltopdf', 'puppeteer']
                
                found_pdf_libs = [lib for lib in pdf_indicators if lib in health_str]
                if found_pdf_libs:
                    print(f"   🎯 PDF libraries detected: {found_pdf_libs}")
                else:
                    print(f"   ❌ No PDF libraries detected in health info")
            else:
                print(f"❌ Could not get health info: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking health: {e}")
    
    def run_comprehensive_pdf_test(self):
        """Run comprehensive PDF functionality test"""
        print("🚀 COMPREHENSIVE PRODUCTION PDF FUNCTIONALITY TEST")
        print(f"Backend: {self.base_url}")
        print("="*80)
        
        working_endpoints = self.test_pdf_endpoints()
        self.test_pdf_generation_with_real_data()
        self.test_pdf_preview_functionality()
        self.investigate_pdf_libraries()
        
        self.generate_pdf_report(working_endpoints)
    
    def generate_pdf_report(self, working_endpoints):
        """Generate PDF functionality report"""
        print("\n" + "="*80)
        print("📊 PRODUCTION PDF FUNCTIONALITY REPORT")
        print("="*80)
        
        print(f"\n🔍 PDF ENDPOINTS ANALYSIS:")
        if working_endpoints:
            print(f"   ✅ Found {len(working_endpoints)} potentially working PDF endpoints")
            for endpoint, method, status in working_endpoints:
                print(f"      {method} {endpoint} (Status: {status})")
        else:
            print(f"   ❌ No PDF endpoints found")
        
        print(f"\n🚨 CRITICAL FINDINGS:")
        if not working_endpoints:
            print("   1. ❌ NO PDF ENDPOINTS FOUND - PDF functionality not implemented")
            print("   2. ❌ PDF export feature is completely missing from production")
            print("   3. ❌ PDF preview feature is completely missing from production")
        else:
            print("   1. ⚠️ Some PDF endpoints exist but may not be fully functional")
            print("   2. 🔍 Further testing needed to verify PDF generation quality")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("   1. 📄 Implement PDF generation endpoints for timelogs")
        print("   2. 👁️ Implement PDF preview functionality")
        print("   3. 📚 Add PDF generation library (ReportLab, WeasyPrint, or similar)")
        print("   4. 🔗 Create endpoints like:")
        print("      - POST /api/timelogs/{id}/pdf (generate PDF)")
        print("      - POST /api/timelogs/{id}/preview (preview PDF)")
        print("      - POST /api/projects/{id}/report (project summary PDF)")
        
        print("\n" + "="*80)
        print("🏁 PDF FUNCTIONALITY TEST COMPLETE")
        print("="*80)

def main():
    """Main function"""
    tester = ProductionPDFTester()
    tester.run_comprehensive_pdf_test()

if __name__ == "__main__":
    main()