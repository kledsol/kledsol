#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class TrustLensAPITester:
    def __init__(self, base_url="https://trustlens-preview-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"🔍 Testing {test_name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {test_name} - Status: {response.status_code}")
                try:
                    return success, response.json() if response.text else {}
                except json.JSONDecodeError:
                    return success, {"raw": response.text}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                self.log(f"❌ {test_name} - {error_msg}", "ERROR")
                self.failed_tests.append({
                    "test": test_name,
                    "endpoint": endpoint,
                    "method": method,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200] if response.text else ""
                })
                try:
                    return False, response.json() if response.text else {}
                except:
                    return False, {"error": response.text}

        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            self.log(f"❌ {test_name} - {error_msg}", "ERROR")
            self.failed_tests.append({
                "test": test_name,
                "endpoint": endpoint,
                "method": method,
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_start_analysis_pulse(self):
        """Test starting a pulse analysis"""
        success, response = self.run_test(
            "Start Pulse Analysis", 
            "POST", 
            "analysis/start?analysis_type=pulse", 
            200
        )
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            self.log(f"✅ Got session ID: {self.session_id}")
            return True
        return False

    def test_start_analysis_deep(self):
        """Test starting a deep analysis"""
        success, response = self.run_test(
            "Start Deep Analysis", 
            "POST", 
            "analysis/start?analysis_type=deep", 
            200
        )
        if success and 'session_id' in response:
            # Use this session for subsequent tests
            if not self.session_id:
                self.session_id = response['session_id']
            return True
        return False

    def test_submit_pulse(self):
        """Test submitting pulse data"""
        if not self.session_id:
            self.log("❌ No session ID available for pulse test", "ERROR")
            return False
            
        pulse_data = {
            "session_id": self.session_id,
            "emotional_connection": 3,
            "communication_quality": 4,
            "perceived_tension": 2
        }
        
        success, response = self.run_test(
            "Submit Pulse Data",
            "POST", 
            "analysis/pulse", 
            200,
            data=pulse_data
        )
        
        if success:
            expected_fields = ['stability_hearts', 'trust_disruption_index', 'interpretation']
            for field in expected_fields:
                if field not in response:
                    self.log(f"⚠️  Missing field in pulse response: {field}", "WARN")
        
        return success

    def test_submit_baseline(self):
        """Test submitting baseline data"""
        if not self.session_id:
            self.log("❌ No session ID available for baseline test", "ERROR")
            return False
            
        baseline_data = {
            "session_id": self.session_id,
            "relationship_duration": "3_to_5",
            "prior_satisfaction": 8,
            "communication_habits": "We talk daily about work and personal matters, usually in the evening.",
            "emotional_closeness": 7,
            "transparency_level": 8
        }
        
        return self.run_test(
            "Submit Baseline Data",
            "POST", 
            "analysis/baseline", 
            200,
            data=baseline_data
        )[0]

    def test_submit_changes(self):
        """Test submitting changes data"""
        if not self.session_id:
            self.log("❌ No session ID available for changes test", "ERROR")
            return False
            
        changes_data = {
            "session_id": self.session_id,
            "categories": ["communication_changes", "emotional_distance", "routine_changes"]
        }
        
        return self.run_test(
            "Submit Changes Data",
            "POST", 
            "analysis/changes", 
            200,
            data=changes_data
        )[0]

    def test_submit_timeline(self):
        """Test submitting timeline data"""
        if not self.session_id:
            self.log("❌ No session ID available for timeline test", "ERROR")
            return False
            
        timeline_data = {
            "session_id": self.session_id,
            "when_started": "1_month",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": False
        }
        
        return self.run_test(
            "Submit Timeline Data",
            "POST", 
            "analysis/timeline", 
            200,
            data=timeline_data
        )[0]

    def test_get_next_question(self):
        """Test getting next question for investigation"""
        if not self.session_id:
            self.log("❌ No session ID available for question test", "ERROR")
            return False
            
        success, response = self.run_test(
            "Get Next Question",
            "GET", 
            f"analysis/{self.session_id}/question", 
            200
        )
        
        if success:
            expected_fields = ['question_id', 'question_text', 'category']
            for field in expected_fields:
                if field not in response:
                    self.log(f"⚠️  Missing field in question response: {field}", "WARN")
                    
        return success, response if success else None

    def test_submit_answer(self):
        """Test submitting answer to investigation question"""
        if not self.session_id:
            self.log("❌ No session ID available for answer test", "ERROR")
            return False
            
        # First get a question
        question_success, question_data = self.test_get_next_question()
        if not question_success:
            return False
            
        # Wait a moment for AI processing
        time.sleep(2)
        
        answer_data = {
            "session_id": self.session_id,
            "question_id": question_data.get("question_id", "q_1"),
            "question_text": question_data.get("question_text", "Test question"),
            "answer": "Things have been feeling different lately, more distant.",
            "category": question_data.get("category", "emotional_indicators")
        }
        
        success, response = self.run_test(
            "Submit Answer",
            "POST", 
            "analysis/answer", 
            200,
            data=answer_data
        )
        
        if success:
            expected_fields = ['questions_answered', 'trust_disruption_index', 'stability_hearts']
            for field in expected_fields:
                if field not in response:
                    self.log(f"⚠️  Missing field in answer response: {field}", "WARN")
                    
        return success

    def test_mirror_mode(self):
        """Test mirror mode perception gap analysis"""
        if not self.session_id:
            self.log("❌ No session ID available for mirror mode test", "ERROR")
            return False
            
        mirror_data = {
            "session_id": self.session_id,
            "partner_emotional": 6,
            "partner_communication": 7,
            "partner_trust": 8
        }
        
        success, response = self.run_test(
            "Mirror Mode Analysis",
            "POST", 
            "analysis/mirror", 
            200,
            data=mirror_data
        )
        
        if success:
            expected_fields = ['perception_gap', 'has_significant_mismatch', 'insight']
            for field in expected_fields:
                if field not in response:
                    self.log(f"⚠️  Missing field in mirror response: {field}", "WARN")
                    
        return success

    def test_conversation_coach(self):
        """Test conversation coach guidance"""
        if not self.session_id:
            self.log("❌ No session ID available for coach test", "ERROR")
            return False
            
        coach_data = {
            "session_id": self.session_id,
            "tone": "gentle",
            "topic": "recent_changes"
        }
        
        # Wait a moment for AI processing
        time.sleep(2)
        
        success, response = self.run_test(
            "Conversation Coach",
            "POST", 
            "analysis/conversation-coach", 
            200,
            data=coach_data
        )
        
        if success:
            expected_fields = ['opening', 'questions', 'avoid', 'observe']
            for field in expected_fields:
                if field not in response:
                    self.log(f"⚠️  Missing field in coach response: {field}", "WARN")
                    
        return success

    def test_get_results(self):
        """Test getting final analysis results"""
        if not self.session_id:
            self.log("❌ No session ID available for results test", "ERROR")
            return False
            
        success, response = self.run_test(
            "Get Analysis Results",
            "GET", 
            f"analysis/{self.session_id}/results", 
            200
        )
        
        if success:
            expected_fields = ['trust_disruption_index', 'stability_hearts', 'hypotheses', 'signals', 'clarity_actions']
            for field in expected_fields:
                if field not in response:
                    self.log(f"⚠️  Missing field in results response: {field}", "WARN")
                    
        return success

    def test_session_status(self):
        """Test getting session status"""
        if not self.session_id:
            self.log("❌ No session ID available for status test", "ERROR")
            return False
            
        return self.run_test(
            "Get Session Status",
            "GET", 
            f"analysis/{self.session_id}/status", 
            200
        )[0]

    def run_full_test_suite(self):
        """Run all backend API tests"""
        self.log("🚀 Starting TrustLens API Test Suite")
        self.log(f"🔗 Testing backend: {self.base_url}")
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            self.log("❌ Basic connectivity failed, stopping tests", "ERROR")
            return False
            
        # Test analysis startup
        if not self.test_start_analysis_deep():
            self.log("❌ Failed to start analysis session", "ERROR")
            return False
            
        # Test the complete flow
        tests = [
            ("Baseline Submission", self.test_submit_baseline),
            ("Changes Submission", self.test_submit_changes), 
            ("Timeline Submission", self.test_submit_timeline),
            ("Answer Submission", self.test_submit_answer),
            ("Mirror Mode", self.test_mirror_mode),
            ("Conversation Coach", self.test_conversation_coach),
            ("Get Results", self.test_get_results),
            ("Session Status", self.test_session_status),
        ]
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                if not success:
                    self.log(f"⚠️  {test_name} failed but continuing tests", "WARN")
            except Exception as e:
                self.log(f"❌ {test_name} threw exception: {str(e)}", "ERROR")
                
        # Test pulse flow separately
        self.log("🔄 Testing Pulse Flow...")
        if self.test_start_analysis_pulse():
            self.test_submit_pulse()
            
        # Print summary
        self.print_summary()
        
        return self.tests_passed > 0 and len(self.failed_tests) < 5

    def print_summary(self):
        """Print test results summary"""
        self.log(f"\n📊 Test Results Summary:")
        self.log(f"✅ Tests passed: {self.tests_passed}/{self.tests_run}")
        self.log(f"❌ Tests failed: {len(self.failed_tests)}")
        
        if self.failed_tests:
            self.log("\n🔍 Failed Tests Details:")
            for failure in self.failed_tests:
                error_msg = failure.get('error', f'Status {failure.get("actual", "unknown")}')
                self.log(f"  ❌ {failure['test']}: {error_msg}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            self.log("🎉 Backend API tests mostly successful!", "SUCCESS")
        elif success_rate >= 60:
            self.log("⚠️  Backend API has some issues but is functional", "WARN")
        else:
            self.log("❌ Backend API has significant issues", "ERROR")

def main():
    """Main test execution"""
    tester = TrustLensAPITester()
    success = tester.run_full_test_suite()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())