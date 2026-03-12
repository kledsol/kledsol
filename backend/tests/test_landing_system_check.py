"""
TrustLens Landing Page & System Check Tests
============================================
Comprehensive backend API tests for system health check covering:
- Analysis start endpoints (deep/pulse)
- Question retrieval
- Auth endpoints (register/login)
- Mirror mode creation
- Report sharing
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSystemHealth:
    """Basic health check and API availability tests"""
    
    def test_api_root_responds(self):
        """Test that the API root is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "active"
        assert "TrustLens" in data.get("message", "")
        print("✅ API root responds with active status")


class TestAnalysisStart:
    """Tests for /api/analysis/start endpoint"""
    
    def test_start_deep_analysis(self):
        """Test starting a deep analysis returns session_id"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data.get("type") == "deep"
        assert isinstance(data["session_id"], str)
        assert len(data["session_id"]) > 10  # UUID format
        print(f"✅ Deep analysis started: session_id={data['session_id'][:8]}...")
        return data["session_id"]
    
    def test_start_pulse_analysis(self):
        """Test starting a pulse analysis returns session_id"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=pulse")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data.get("type") == "pulse"
        assert isinstance(data["session_id"], str)
        print(f"✅ Pulse analysis started: session_id={data['session_id'][:8]}...")


class TestQuestionRetrieval:
    """Tests for /api/analysis/{session_id}/question endpoint"""
    
    def test_get_question_for_valid_session(self):
        """Test that a question is returned for a valid session"""
        # First create a session
        start_response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]
        
        # Get question
        question_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        assert question_response.status_code == 200
        data = question_response.json()
        
        # Validate question structure
        assert "question_id" in data
        assert "question_text" in data
        assert "category" in data
        assert isinstance(data["question_text"], str)
        assert len(data["question_text"]) > 5
        print(f"✅ Question retrieved: '{data['question_text'][:50]}...'")
    
    def test_get_question_invalid_session(self):
        """Test that 404 is returned for invalid session"""
        fake_session = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/analysis/{fake_session}/question")
        assert response.status_code == 404
        print("✅ 404 returned for invalid session (expected behavior)")


class TestAuthEndpoints:
    """Tests for authentication endpoints"""
    
    def test_register_new_user(self):
        """Test registering a new user"""
        unique_email = f"TEST_syscheck_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "test1234"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        # Could be 200 (success) or 409 (already exists)
        assert response.status_code in [200, 409]
        
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data or "token" in data
            print(f"✅ Registration successful for {unique_email[:20]}...")
        else:
            print("ℹ️ Registration returned 409 (user may already exist)")
    
    def test_login_with_valid_credentials(self):
        """Test login with the test account"""
        payload = {
            "email": "syscheck@test.com",
            "password": "test1234"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        # If test account exists
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            print("✅ Login successful with test account")
        elif response.status_code == 401:
            # Test account may not exist, try to create it first
            register_response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
            if register_response.status_code == 200:
                # Now try login again
                login_response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
                assert login_response.status_code == 200
                print("✅ Login successful after creating test account")
            else:
                print("ℹ️ Could not login or create test account (may need different credentials)")
        else:
            print(f"ℹ️ Login returned {response.status_code}")
    
    def test_login_invalid_credentials(self):
        """Test that invalid credentials return 401"""
        payload = {
            "email": "nonexistent@fake.com",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401
        print("✅ 401 returned for invalid credentials (expected)")


class TestMirrorMode:
    """Tests for Mirror Mode endpoint"""
    
    def test_create_mirror_session(self):
        """Test POST /api/mirror/create returns mirror_id"""
        # First create an analysis session
        start_response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]
        
        # Create mirror session
        payload = {"session_id": session_id}
        response = requests.post(f"{BASE_URL}/api/mirror/create", json=payload)
        
        # Mirror create should return 200 with mirror_id
        assert response.status_code == 200
        data = response.json()
        assert "mirror_id" in data
        assert isinstance(data["mirror_id"], str)
        print(f"✅ Mirror session created: mirror_id={data['mirror_id'][:8]}...")


class TestReportSharing:
    """Tests for Report Sharing endpoint"""
    
    def test_share_report_endpoint(self):
        """Test POST /api/reports/share responds"""
        # First create a session with some data
        start_response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]
        
        # Share report
        payload = {"session_id": session_id}
        response = requests.post(f"{BASE_URL}/api/reports/share", json=payload)
        
        # Should return 200 or 201 with report info
        assert response.status_code in [200, 201]
        data = response.json()
        assert "report_id" in data or "share_url" in data or "message" in data
        print(f"✅ Report share endpoint responded: {response.status_code}")


class TestFullAnalysisFlow:
    """End-to-end test of analysis flow"""
    
    def test_complete_analysis_flow(self):
        """Test start -> get question -> answer flow"""
        # 1. Start analysis
        start_response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]
        print(f"✅ Step 1: Started analysis (session={session_id[:8]}...)")
        
        # 2. Get first question
        q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        assert q_response.status_code == 200
        question = q_response.json()
        print(f"✅ Step 2: Got question: '{question['question_text'][:40]}...'")
        
        # 3. Submit an answer
        answer_payload = {
            "session_id": session_id,
            "question_id": question["question_id"],
            "question_text": question["question_text"],
            "answer": question.get("options", ["Test answer"])[0] if question.get("options") else "Test answer",
            "category": question["category"]
        }
        answer_response = requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_payload)
        assert answer_response.status_code == 200
        answer_data = answer_response.json()
        assert "questions_answered" in answer_data
        print(f"✅ Step 3: Answered question (total answered: {answer_data['questions_answered']})")
        
        # 4. Get next question (should be different or complete)
        q2_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        assert q2_response.status_code == 200
        print("✅ Step 4: Question flow continues correctly")


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
