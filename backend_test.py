#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

class TrustLensAPITester:
    def __init__(self, base_url="https://clarity-analysis.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, name, success, details=""):
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        if details and success:
            print(f"   {details}")

    def test_root_endpoint(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else {}
            
            details = f"Status: {response.status_code}"
            if success:
                details += f", Message: {data.get('message', 'N/A')}"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_start_analysis(self):
        """Test starting a new analysis session"""
        try:
            response = requests.post(f"{self.api_url}/analysis/start", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.session_id = data.get('session_id')
                details = f"Session ID: {self.session_id[:8]}..."
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Start Analysis Session", success, details)
            return success
        except Exception as e:
            self.log_test("Start Analysis Session", False, f"Exception: {str(e)}")
            return False

    def test_submit_baseline(self):
        """Test submitting baseline data"""
        if not self.session_id:
            self.log_test("Submit Baseline", False, "No session ID")
            return False
            
        baseline_data = {
            "session_id": self.session_id,
            "relationship_duration": "3_to_5_years",
            "perceived_quality": 8,
            "communication_frequency": "once_daily",
            "emotional_connection": 7,
            "transparency_level": 6,
            "shared_routines": "We usually have dinner together and watch movies on weekends"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/analysis/baseline", 
                json=baseline_data,
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Next: {data.get('next_step')}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Submit Baseline", success, details)
            return success
        except Exception as e:
            self.log_test("Submit Baseline", False, f"Exception: {str(e)}")
            return False

    def test_submit_changes(self):
        """Test submitting change detection data"""
        if not self.session_id:
            self.log_test("Submit Changes", False, "No session ID")
            return False
            
        changes_data = {
            "session_id": self.session_id,
            "categories": ["communication_patterns", "digital_behavior", "emotional_connection"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/analysis/changes", 
                json=changes_data,
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Next: {data.get('next_step')}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Submit Changes", success, details)
            return success
        except Exception as e:
            self.log_test("Submit Changes", False, f"Exception: {str(e)}")
            return False

    def test_submit_timeline(self):
        """Test submitting timeline data"""
        if not self.session_id:
            self.log_test("Submit Timeline", False, "No session ID")
            return False
            
        timeline_data = {
            "session_id": self.session_id,
            "when_started": "3_months",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": True
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/analysis/timeline", 
                json=timeline_data,
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Next: {data.get('next_step')}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Submit Timeline", success, details)
            return success
        except Exception as e:
            self.log_test("Submit Timeline", False, f"Exception: {str(e)}")
            return False

    def test_get_next_question(self):
        """Test getting next adaptive question"""
        if not self.session_id:
            self.log_test("Get Next Question", False, "No session ID")
            return False, None
            
        try:
            response = requests.get(
                f"{self.api_url}/analysis/{self.session_id}/question",
                timeout=15  # AI calls might take longer
            )
            success = response.status_code == 200
            
            question_data = None
            if success:
                question_data = response.json()
                details = f"Question ID: {question_data.get('question_id')}, Category: {question_data.get('category')}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Get Next Question (AI)", success, details)
            return success, question_data
        except Exception as e:
            self.log_test("Get Next Question (AI)", False, f"Exception: {str(e)}")
            return False, None

    def test_submit_answer(self, question_data):
        """Test submitting an answer"""
        if not self.session_id or not question_data:
            self.log_test("Submit Answer", False, "Missing session ID or question data")
            return False
            
        answer_data = {
            "session_id": self.session_id,
            "question_id": question_data.get("question_id"),
            "question_text": question_data.get("question_text"),
            "answer": "Yes, I have noticed some changes in communication patterns recently",
            "category": question_data.get("category")
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/analysis/answer", 
                json=answer_data,
                timeout=15  # AI analysis might take time
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Questions answered: {data.get('questions_answered')}, Trust Index: {data.get('trust_disruption_index', 0):.1f}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Submit Answer (AI Analysis)", success, details)
            return success
        except Exception as e:
            self.log_test("Submit Answer (AI Analysis)", False, f"Exception: {str(e)}")
            return False

    def test_submit_reaction(self):
        """Test submitting reaction data"""
        if not self.session_id:
            self.log_test("Submit Reaction", False, "No session ID")
            return False
            
        reaction_data = {
            "session_id": self.session_id,
            "reaction_type": "open_discussion",
            "notes": "Had a good conversation about recent changes"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/analysis/reaction", 
                json=reaction_data,
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Submit Reaction", success, details)
            return success
        except Exception as e:
            self.log_test("Submit Reaction", False, f"Exception: {str(e)}")
            return False

    def test_get_results(self):
        """Test getting analysis results"""
        if not self.session_id:
            self.log_test("Get Results", False, "No session ID")
            return False
            
        try:
            response = requests.get(
                f"{self.api_url}/analysis/{self.session_id}/results",
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                trust_index = data.get('trust_disruption_index', 0)
                confidence = data.get('confidence_level', 'unknown')
                details = f"Trust Index: {trust_index:.1f}, Confidence: {confidence}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Get Results", success, details)
            return success
        except Exception as e:
            self.log_test("Get Results", False, f"Exception: {str(e)}")
            return False

    def test_session_status(self):
        """Test getting session status"""
        if not self.session_id:
            self.log_test("Get Session Status", False, "No session ID")
            return False
            
        try:
            response = requests.get(
                f"{self.api_url}/analysis/{self.session_id}/status",
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                step = data.get('current_step', 'unknown')
                questions = data.get('questions_answered', 0)
                details = f"Step: {step}, Questions: {questions}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
                
            self.log_test("Get Session Status", success, details)
            return success
        except Exception as e:
            self.log_test("Get Session Status", False, f"Exception: {str(e)}")
            return False

    def run_complete_test_suite(self):
        """Run all tests in sequence"""
        print(f"🔍 Testing TrustLens API at {self.base_url}")
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Test basic endpoints
        if not self.test_root_endpoint():
            print("⚠️  Root endpoint failed - API might be down")
            return self.get_summary()
        
        # Test analysis flow
        if not self.test_start_analysis():
            print("⚠️  Cannot start analysis - stopping tests")
            return self.get_summary()
        
        # Continue with full flow
        self.test_submit_baseline()
        self.test_submit_changes()
        self.test_submit_timeline()
        
        # Test AI-powered features (might take longer)
        print("\n🤖 Testing AI Integration...")
        success, question_data = self.test_get_next_question()
        if success and question_data:
            self.test_submit_answer(question_data)
        
        # Test additional features
        self.test_submit_reaction()
        self.test_get_results()
        self.test_session_status()
        
        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        if success_rate >= 90:
            print(f"🎉 Excellent! {success_rate:.1f}% success rate")
            status = "PASS"
        elif success_rate >= 70:
            print(f"⚠️  Good but needs attention: {success_rate:.1f}% success rate")
            status = "WARNING"
        else:
            print(f"❌ Critical issues found: {success_rate:.1f}% success rate")
            status = "FAIL"
            
        print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "status": status,
            "success_rate": success_rate,
            "tests_passed": self.tests_passed,
            "tests_run": self.tests_run,
            "session_id": self.session_id
        }

def main():
    tester = TrustLensAPITester()
    results = tester.run_complete_test_suite()
    
    # Return appropriate exit code
    if results["success_rate"] >= 70:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())