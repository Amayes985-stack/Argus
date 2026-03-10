#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Sentinels Monitoring Platform
Tests all API endpoints for functionality, data integrity, and AI integration
"""

import requests
import sys
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('/app/frontend/.env')

class SentinelsAPITester:
    def __init__(self, base_url=None):
        # Use localhost for testing since external URL is not accessible from test environment
        self.base_url = base_url or 'http://localhost:8001'
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def run_test(self, name, method, endpoint, expected_status=200, data=None, timeout=30):
        """Run a single API test with comprehensive error handling"""
        url = f"{self.base_url}{endpoint}"
        self.tests_run += 1
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            elif method == 'PATCH':
                response = self.session.patch(url, json=data, timeout=timeout)
            else:
                print(f"❌ Unsupported method: {method}")
                self.failed_tests.append(f"{name}: Unsupported method {method}")
                return False, {}

            print(f"   Status: {response.status_code}")
            
            # Check if response is successful
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    json_response = response.json()
                    return True, json_response
                except json.JSONDecodeError:
                    print(f"   Warning: Non-JSON response")
                    return True, {"text": response.text}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout after {timeout}s")
            self.failed_tests.append(f"{name}: Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED - Connection error")
            self.failed_tests.append(f"{name}: Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "/api/health")

    def test_dashboard_overview(self):
        """Test dashboard overview endpoint"""
        success, data = self.run_test("Dashboard Overview", "GET", "/api/dashboard/overview")
        if success and data:
            # Validate expected fields
            required_fields = ['services_health', 'total_services', 'active_anomalies', 'active_predictions', 'active_alerts']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   Warning: Missing fields: {missing_fields}")
        return success, data

    def test_infrastructure_servers(self):
        """Test infrastructure servers endpoint"""
        success, data = self.run_test("Infrastructure Servers", "GET", "/api/infrastructure/servers")
        if success and data:
            servers = data.get('servers', [])
            if servers:
                print(f"   Found {len(servers)} servers")
                # Validate server data structure
                first_server = servers[0]
                required_fields = ['host', 'status', 'cpu', 'memory', 'disk']
                missing_fields = [field for field in required_fields if field not in first_server]
                if missing_fields:
                    print(f"   Warning: Missing server fields: {missing_fields}")
        return success, data

    def test_application_services(self):
        """Test application services endpoint"""
        success, data = self.run_test("Application Services", "GET", "/api/applications/services")
        if success and data:
            services = data.get('services', [])
            if services:
                print(f"   Found {len(services)} services")
                # Validate service data structure
                first_service = services[0]
                required_fields = ['service', 'status', 'latency_p50', 'error_rate']
                missing_fields = [field for field in required_fields if field not in first_service]
                if missing_fields:
                    print(f"   Warning: Missing service fields: {missing_fields}")
        return success, data

    def test_alerts(self):
        """Test alerts endpoint"""
        success, data = self.run_test("Get Alerts", "GET", "/api/alerts")
        if success and data:
            alerts = data.get('alerts', [])
            print(f"   Found {len(alerts)} alerts")
            if alerts:
                # Validate alert structure
                first_alert = alerts[0]
                required_fields = ['alert_id', 'service', 'severity', 'status', 'message']
                missing_fields = [field for field in required_fields if field not in first_alert]
                if missing_fields:
                    print(f"   Warning: Missing alert fields: {missing_fields}")
        return success, data

    def test_predictions(self):
        """Test predictions endpoint"""
        success, data = self.run_test("Get Predictions", "GET", "/api/predictions")
        if success and data:
            predictions = data.get('predictions', [])
            print(f"   Found {len(predictions)} predictions")
            if predictions:
                # Validate prediction structure
                first_pred = predictions[0]
                required_fields = ['prediction_id', 'service', 'metric_type', 'current_value', 'predicted_value']
                missing_fields = [field for field in required_fields if field not in first_pred]
                if missing_fields:
                    print(f"   Warning: Missing prediction fields: {missing_fields}")
        return success, data

    def test_anomalies(self):
        """Test anomalies endpoint"""
        success, data = self.run_test("Get Anomalies", "GET", "/api/anomalies")
        if success and data:
            anomalies = data.get('anomalies', [])
            print(f"   Found {len(anomalies)} anomalies")
            if anomalies:
                # Validate anomaly structure
                first_anomaly = anomalies[0]
                required_fields = ['service', 'metric_type', 'value', 'severity']
                missing_fields = [field for field in required_fields if field not in first_anomaly]
                if missing_fields:
                    print(f"   Warning: Missing anomaly fields: {missing_fields}")
        return success, data

    def test_incidents(self):
        """Test incidents endpoint"""
        success, data = self.run_test("Get Incidents", "GET", "/api/incidents")
        if success and data:
            incidents = data.get('incidents', [])
            print(f"   Found {len(incidents)} incidents")
            if incidents:
                # Validate incident structure
                first_incident = incidents[0]
                required_fields = ['incident_id', 'title', 'service', 'severity', 'status']
                missing_fields = [field for field in required_fields if field not in first_incident]
                if missing_fields:
                    print(f"   Warning: Missing incident fields: {missing_fields}")
        return success, data

    def test_logs(self):
        """Test logs endpoint with different filters"""
        success, data = self.run_test("Get Logs", "GET", "/api/logs")
        if success and data:
            logs = data.get('logs', [])
            print(f"   Found {len(logs)} log entries")
            
            # Test with service filter
            success2, data2 = self.run_test("Get Logs with Filter", "GET", "/api/logs?service=api-gateway&level=error")
            if success2:
                filtered_logs = data2.get('logs', [])
                print(f"   Found {len(filtered_logs)} filtered logs")
        return success, data

    def test_metrics_endpoints(self):
        """Test metrics-related endpoints"""
        # Get basic metrics
        success1, data1 = self.run_test("Get Metrics", "GET", "/api/metrics")
        
        # Get timeseries data
        success2, data2 = self.run_test("Get Timeseries", "GET", "/api/metrics/timeseries?service=api-gateway&metric_type=latency")
        
        return success1 and success2, data1

    def test_ai_explanation_alert(self):
        """Test AI explanation for alerts"""
        print(f"\n🧠 Testing AI Explanation (Alert)...")
        
        # Create sample anomaly data for AI explanation
        sample_anomaly = {
            "service": "api-gateway",
            "metric_type": "cpu",
            "value": 92.5,
            "severity": "critical",
            "detection_method": "threshold"
        }
        
        success, data = self.run_test("AI Alert Explanation", "POST", "/api/anomalies/explain", 200, sample_anomaly, timeout=45)
        
        if success and data:
            explanation = data.get('explanation', {})
            if explanation:
                print(f"   AI Root Cause: {explanation.get('root_cause', 'N/A')[:100]}...")
                print(f"   AI Action: {explanation.get('immediate_action', 'N/A')[:100]}...")
            else:
                print(f"   Warning: No explanation content received")
        
        return success, data

    def test_ai_explanation_prediction(self):
        """Test AI explanation for predictions"""
        print(f"\n🧠 Testing AI Explanation (Prediction)...")
        
        # Create sample prediction data
        sample_prediction = {
            "service": "payment-service",
            "metric_type": "memory",
            "current_value": 78.5,
            "predicted_value": 95.2,
            "threshold": 90,
            "hours_until_breach": 4.2,
            "confidence": 87.3,
            "trend": "increasing"
        }
        
        success, data = self.run_test("AI Prediction Explanation", "POST", "/api/predictions/explain", 200, sample_prediction, timeout=45)
        
        if success and data:
            explanation = data.get('explanation', {})
            if explanation:
                print(f"   AI Impact: {explanation.get('impact_prediction', 'N/A')[:100]}...")
                print(f"   AI Prevention: {explanation.get('prevention_steps', 'N/A')}")
            else:
                print(f"   Warning: No explanation content received")
        
        return success, data

    def test_system_status(self):
        """Test system status endpoint"""
        return self.run_test("System Status", "GET", "/api/system/status")

    def run_comprehensive_test_suite(self):
        """Run all tests and generate comprehensive report"""
        print("🚀 Starting Comprehensive Sentinels API Testing")
        print(f"📡 Testing API at: {self.base_url}")
        print("=" * 80)
        
        # Core API Tests
        tests = [
            ("Health Check", self.test_health_check),
            ("Dashboard Overview", self.test_dashboard_overview),
            ("Infrastructure Servers", self.test_infrastructure_servers),
            ("Application Services", self.test_application_services),
            ("Alerts", self.test_alerts),
            ("Predictions", self.test_predictions),
            ("Anomalies", self.test_anomalies),
            ("Incidents", self.test_incidents),
            ("Logs", self.test_logs),
            ("Metrics", self.test_metrics_endpoints),
            ("System Status", self.test_system_status),
        ]
        
        # AI Integration Tests (slower, run separately)
        ai_tests = [
            ("AI Alert Explanation", self.test_ai_explanation_alert),
            ("AI Prediction Explanation", self.test_ai_explanation_prediction),
        ]
        
        # Run core tests
        core_results = []
        for test_name, test_func in tests:
            try:
                success, data = test_func()
                core_results.append((test_name, success, data))
            except Exception as e:
                print(f"❌ {test_name} - Exception: {str(e)}")
                core_results.append((test_name, False, {}))
                self.failed_tests.append(f"{test_name}: Exception - {str(e)}")
        
        # Run AI tests
        ai_results = []
        for test_name, test_func in ai_tests:
            try:
                success, data = test_func()
                ai_results.append((test_name, success, data))
            except Exception as e:
                print(f"❌ {test_name} - Exception: {str(e)}")
                ai_results.append((test_name, False, {}))
                self.failed_tests.append(f"{test_name}: Exception - {str(e)}")
        
        # Generate Report
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for failure in self.failed_tests:
                print(f"   • {failure}")
        
        # Categorize results
        backend_issues = []
        critical_failures = []
        
        for test_name, success, data in core_results + ai_results:
            if not success:
                issue = {
                    "endpoint": test_name,
                    "issue": f"Test failed - check logs above",
                    "impact": "API endpoint not responding correctly",
                    "fix_priority": "HIGH" if "Health" in test_name or "Dashboard" in test_name else "MEDIUM"
                }
                backend_issues.append(issue)
                
                if "Health" in test_name or "AI" in test_name:
                    critical_failures.append(test_name)
        
        # Determine if environment is ready
        env_success = len(critical_failures) == 0 and success_rate >= 70
        
        return {
            "success_rate": success_rate,
            "backend_issues": backend_issues,
            "critical_failures": critical_failures,
            "env_success": env_success,
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed
        }

def main():
    """Main test execution function"""
    print("Starting Sentinels Monitoring Platform Backend Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize tester
    tester = SentinelsAPITester()
    
    # Run comprehensive test suite
    results = tester.run_comprehensive_test_suite()
    
    # Print final summary
    print(f"\n🏁 Final Result: {'✅ PASS' if results['env_success'] else '❌ FAIL'}")
    print(f"📈 Success Rate: {results['success_rate']:.1f}%")
    
    # Return appropriate exit code
    return 0 if results['env_success'] else 1

if __name__ == "__main__":
    sys.exit(main())