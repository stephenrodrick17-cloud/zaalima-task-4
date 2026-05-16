"""
Connection Tester - Verify Frontend & Backend Communication
This script tests all critical connection points between frontend and backend
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Tuple

class ConnectionTester:
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
    
    def print_test(self, status: str, test_name: str, details: str = ""):
        """Print test result"""
        symbols = {"✅": "PASS", "❌": "FAIL", "⚠️": "WARN"}
        color_code = {"✅": "\033[92m", "❌": "\033[91m", "⚠️": "\033[93m", "\033[0m": ""}
        
        status_symbol = status
        output = f"  {status_symbol} {test_name}"
        if details:
            output += f"\n     └─ {details}"
        
        print(output)
        
        if status == "✅":
            self.results["passed"].append(test_name)
        elif status == "❌":
            self.results["failed"].append(test_name)
        elif status == "⚠️":
            self.results["warnings"].append(test_name)
    
    def test_backend_health(self) -> bool:
        """Test if backend is running and healthy"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.print_test("✅", "Backend Service Running", 
                               f"Status: {data.get('status')}, Version: {data.get('version')}")
                return True
            else:
                self.print_test("❌", "Backend Health Check", 
                               f"Status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("❌", "Backend Service Running", 
                           f"Cannot connect to {self.backend_url}")
            return False
        except Exception as e:
            self.print_test("❌", "Backend Service Running", str(e))
            return False
    
    def test_backend_cors(self) -> bool:
        """Test CORS configuration"""
        try:
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "POST"
            }
            response = requests.options(f"{self.backend_url}/api/detection/detect", headers=headers, timeout=2)
            
            allow_origin = response.headers.get("Access-Control-Allow-Origin")
            if allow_origin:
                self.print_test("✅", "CORS Configuration", 
                               f"Allow-Origin: {allow_origin}")
                return True
            else:
                self.print_test("⚠️", "CORS Configuration", 
                               "No CORS headers in response")
                return False
        except Exception as e:
            self.print_test("⚠️", "CORS Configuration", str(e))
            return False
    
    def test_api_endpoints(self):
        """Test all critical API endpoints"""
        endpoints = [
            ("/api", "API Root"),
            ("/api/detection/reports/recent", "Recent Reports"),
            ("/api/dashboard/overview", "Dashboard Overview"),
            ("/api/dashboard/statistics", "Statistics"),
            ("/docs", "API Documentation"),
            ("/redoc", "ReDoc Documentation"),
        ]
        
        for endpoint, label in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=2)
                if response.status_code == 200:
                    self.print_test("✅", f"Endpoint: {label}", endpoint)
                else:
                    self.print_test("⚠️", f"Endpoint: {label}", 
                                   f"Status {response.status_code}")
            except Exception as e:
                self.print_test("❌", f"Endpoint: {label}", str(e)[:50])
    
    def test_database(self) -> bool:
        """Test database connectivity via API"""
        try:
            response = requests.get(f"{self.backend_url}/api/detection/reports/recent?limit=1", 
                                   timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.print_test("✅", "Database Connection", 
                               f"Successfully queried reports")
                return True
            else:
                self.print_test("⚠️", "Database Connection", 
                               f"API returned {response.status_code}")
                return False
        except Exception as e:
            self.print_test("⚠️", "Database Connection", str(e)[:50])
            return False
    
    def test_frontend_accessibility(self) -> bool:
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=3)
            if response.status_code == 200:
                self.print_test("✅", "Frontend Service Running", 
                               f"Status: {response.status_code}")
                return True
            else:
                self.print_test("⚠️", "Frontend Service Running", 
                               f"Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_test("❌", "Frontend Service Running", 
                           f"Cannot connect to {self.frontend_url}")
            return False
        except Exception as e:
            self.print_test("⚠️", "Frontend Service Running", str(e)[:50])
            return False
    
    def test_frontend_api_config(self) -> bool:
        """Check frontend .env configuration"""
        env_path = Path("frontend/.env")
        
        if not env_path.exists():
            self.print_test("❌", "Frontend .env Configuration", 
                           "frontend/.env not found")
            return False
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if "REACT_APP_API_URL" in content:
                    self.print_test("✅", "Frontend .env Configuration", 
                                   "REACT_APP_API_URL configured")
                    return True
                else:
                    self.print_test("⚠️", "Frontend .env Configuration", 
                                   "REACT_APP_API_URL not set")
                    return False
        except Exception as e:
            self.print_test("⚠️", "Frontend .env Configuration", str(e)[:50])
            return False
    
    def test_backend_env_config(self) -> bool:
        """Check backend .env configuration"""
        env_path = Path(".env")
        
        if not env_path.exists():
            self.print_test("⚠️", "Backend .env Configuration", 
                           ".env not found (using defaults)")
            return True
        
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                checks = {
                    "ALLOWED_ORIGINS": "CORS Origins",
                    "DATABASE_URL": "Database URL",
                    "GEMINI_API_KEY": "AI Chat API (Gemini)"
                }
                
                all_ok = True
                for key, label in checks.items():
                    if key in content:
                        self.print_test("✅", f"Backend .env: {label}", 
                                       f"{key} configured")
                    else:
                        self.print_test("⚠️", f"Backend .env: {label}", 
                                       f"{key} not configured")
                        all_ok = False
                
                return all_ok
        except Exception as e:
            self.print_test("⚠️", "Backend .env Configuration", str(e)[:50])
            return False
    
    def run_all_tests(self):
        """Run all connection tests"""
        self.print_header("Infrastructure Damage Detection - Connection Test Suite")
        
        print("\n📡 BACKEND TESTS:")
        self.test_backend_health()
        self.test_backend_cors()
        self.test_api_endpoints()
        self.test_database()
        
        print("\n🌐 FRONTEND TESTS:")
        self.test_frontend_accessibility()
        
        print("\n⚙️  CONFIGURATION TESTS:")
        self.test_backend_env_config()
        self.test_frontend_api_config()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        self.print_header("Test Results Summary")
        
        total_passed = len(self.results["passed"])
        total_failed = len(self.results["failed"])
        total_warnings = len(self.results["warnings"])
        total_tests = total_passed + total_failed + total_warnings
        
        print(f"\n  Total Tests: {total_tests}")
        print(f"  ✅ Passed:   {total_passed}")
        print(f"  ❌ Failed:   {total_failed}")
        print(f"  ⚠️  Warnings: {total_warnings}")
        
        if total_failed == 0:
            print(f"\n  🎉 All critical tests passed!")
            print(f"\n  Next steps:")
            print(f"     1. Open http://localhost:3000 in your browser")
            print(f"     2. Navigate to Detection page")
            print(f"     3. Upload a test image to verify end-to-end connection")
            print(f"     4. View Reports page to confirm data is saved")
        else:
            print(f"\n  ⚠️  Some tests failed. Please review the errors above.")
            print(f"\n  Troubleshooting:")
            print(f"     • Check backend is running: python -m uvicorn backend.main:app --reload")
            print(f"     • Check frontend is running: npm start")
            print(f"     • Verify .env files in both frontend and backend directories")
            print(f"     • Check ALLOWED_ORIGINS in backend .env includes http://localhost:3000")


def main():
    import sys
    
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    frontend_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000"
    
    tester = ConnectionTester(backend_url, frontend_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
