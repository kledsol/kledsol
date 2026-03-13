"""
Test suite for TrustLens new features (iteration 16):
1. POST /api/analysis/conversation-coach/pdf - PDF export of conversation guidance
2. GET /api/auth/my-analyses - Enhanced dashboard with full score/signal data

Also includes regression tests for core analysis flow.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCoreAPIHealth:
    """Basic health check and core endpoints"""
    
    def test_api_root(self):
        """API root should return active status"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        print("PASS: API root returns active status")
    
    def test_analysis_start_deep(self):
        """POST /api/analysis/start should return session_id for deep analysis"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data.get("type") == "deep"
        print(f"PASS: Deep analysis start returns session_id: {data['session_id'][:8]}...")
        return data["session_id"]


class TestAnalysisFlow:
    """Full analysis flow tests - needed for coach PDF and my-analyses"""
    
    @pytest.fixture(scope="class")
    def analysis_session(self):
        """Create a complete analysis session for testing"""
        # Start deep analysis
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        print(f"Created session: {session_id[:8]}...")
        
        # Submit baseline
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 7,
            "communication_habits": "Daily talks",
            "emotional_closeness": 4,
            "transparency_level": 3
        }
        response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        assert response.status_code == 200
        print("Baseline submitted")
        
        # Submit changes
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance", "schedule_changes"]
        }
        response = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        assert response.status_code == 200
        print("Changes submitted")
        
        # Submit timeline
        timeline_data = {
            "session_id": session_id,
            "when_started": "2-4 weeks ago",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": True
        }
        response = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        assert response.status_code == 200
        print("Timeline submitted")
        
        # Answer a few questions
        for i in range(3):
            q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            if q_response.status_code == 200:
                q = q_response.json()
                if q.get("question_id") == "complete":
                    break
                answer_data = {
                    "session_id": session_id,
                    "question_id": q.get("question_id"),
                    "question_text": q.get("question_text", ""),
                    "answer": q.get("options", ["Option 1"])[0] if q.get("options") else "Yes",
                    "category": q.get("category", "general")
                }
                requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        
        print("Questions answered")
        return session_id
    
    def test_get_question(self, analysis_session):
        """GET /api/analysis/{session_id}/question should return question"""
        response = requests.get(f"{BASE_URL}/api/analysis/{analysis_session}/question")
        assert response.status_code == 200
        data = response.json()
        assert "question_id" in data or "question_text" in data
        print(f"PASS: Question retrieved - {data.get('question_id', 'complete')}")
    
    def test_get_results(self, analysis_session):
        """GET /api/analysis/{session_id}/results should return full results"""
        response = requests.get(f"{BASE_URL}/api/analysis/{analysis_session}/results")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "suspicion_score" in data
        assert "suspicion_label" in data
        assert "signals" in data
        assert "pattern_statistics" in data
        assert "dominant_pattern" in data
        
        print(f"PASS: Results retrieved - score: {data['suspicion_score']}, label: {data['suspicion_label']}")
        return data


class TestConversationCoach:
    """Test conversation coach feature"""
    
    @pytest.fixture(scope="class")
    def session_with_data(self):
        """Create a session with analysis data for coach testing"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        # Submit baseline
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "3-5 years",
            "prior_satisfaction": 6,
            "communication_habits": "Regular",
            "emotional_closeness": 3,
            "transparency_level": 3
        })
        
        # Submit changes
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["communication", "emotional_distance"]
        })
        
        return session_id
    
    def test_conversation_coach_guidance(self, session_with_data):
        """POST /api/analysis/conversation-coach should return guidance"""
        response = requests.post(
            f"{BASE_URL}/api/analysis/conversation-coach",
            json={
                "session_id": session_with_data,
                "tone": "gentle",
                "topic": "recent_changes"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected structure
        assert "openings" in data or "opening" in data
        assert "questions" in data
        assert "avoid" in data
        
        print(f"PASS: Conversation guidance returned with {len(data.get('questions', []))} questions")
    
    def test_conversation_coach_pdf_export(self, session_with_data):
        """NEW: POST /api/analysis/conversation-coach/pdf should return PDF file"""
        response = requests.post(
            f"{BASE_URL}/api/analysis/conversation-coach/pdf",
            json={
                "session_id": session_with_data,
                "tone": "direct",
                "topic": "trust"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        # Verify content-type is PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        
        # Verify it's actual PDF content (starts with %PDF)
        content = response.content
        assert len(content) > 1000, "PDF content too small"
        assert content[:4] == b'%PDF', "Content doesn't start with PDF header"
        
        print(f"PASS: PDF export successful - {len(content)} bytes, content-type: {content_type}")
    
    def test_conversation_coach_pdf_invalid_session(self):
        """POST /api/analysis/conversation-coach/pdf with invalid session should return 404"""
        response = requests.post(
            f"{BASE_URL}/api/analysis/conversation-coach/pdf",
            json={
                "session_id": "invalid-session-id-12345",
                "tone": "gentle",
                "topic": "feelings"
            }
        )
        assert response.status_code == 404
        print("PASS: Invalid session returns 404 for PDF export")


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_valid_credentials(self):
        """POST /api/auth/login should return token for valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "syscheck@test.com", "password": "test1234"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"PASS: Login successful, token received")
        return data["token"]
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login should return 401 for invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpass"}
        )
        assert response.status_code == 401
        print("PASS: Invalid credentials return 401")
    
    def test_register_new_user(self):
        """POST /api/auth/register should create new user"""
        unique_email = f"TEST_user_{int(time.time())}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": unique_email, "password": "test1234"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"PASS: Registration successful for {unique_email}")
        return data["token"]


class TestMyAnalyses:
    """NEW: Test enhanced my-analyses dashboard endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for testing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "syscheck@test.com", "password": "test1234"}
        )
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_my_analyses_requires_auth(self):
        """GET /api/auth/my-analyses without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/auth/my-analyses")
        assert response.status_code == 401
        print("PASS: my-analyses endpoint requires authentication")
    
    def test_my_analyses_with_auth(self, auth_headers):
        """NEW: GET /api/auth/my-analyses with auth should return analyses with full data"""
        response = requests.get(
            f"{BASE_URL}/api/auth/my-analyses",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "analyses" in data
        assert "total" in data
        
        print(f"PASS: my-analyses returned {data['total']} analyses")
        
        # If there are analyses, verify they have the new fields
        if data["analyses"]:
            analysis = data["analyses"][0]
            # Check for new enhanced fields
            required_fields = ["session_id", "analysis_type", "created_at", "suspicion_score", "suspicion_label"]
            for field in required_fields:
                assert field in analysis, f"Missing field: {field}"
            
            print(f"PASS: Analysis has required fields - score: {analysis.get('suspicion_score')}, label: {analysis.get('suspicion_label')}")
            
            # Check for enhanced fields (new feature)
            if "dominant_pattern" in analysis:
                print(f"PASS: Analysis includes dominant_pattern: {analysis.get('dominant_pattern')}")
            
            if "top_signals" in analysis:
                print(f"PASS: Analysis includes top_signals: {len(analysis.get('top_signals', []))} signals")
        
        return data
    
    def test_link_analysis_and_retrieve(self, auth_headers):
        """Test linking an analysis to user and retrieving it in my-analyses"""
        # Create a new analysis session
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        # Submit minimal data
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 5,
            "communication_habits": "Daily",
            "emotional_closeness": 3,
            "transparency_level": 3
        })
        
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["emotional_distance"]
        })
        
        # Link to user
        link_response = requests.post(
            f"{BASE_URL}/api/auth/link-analysis",
            headers=auth_headers,
            json={"session_id": session_id}
        )
        assert link_response.status_code == 200
        print(f"PASS: Analysis {session_id[:8]}... linked to user")
        
        # Verify it appears in my-analyses
        analyses_response = requests.get(
            f"{BASE_URL}/api/auth/my-analyses",
            headers=auth_headers
        )
        data = analyses_response.json()
        session_ids = [a["session_id"] for a in data["analyses"]]
        assert session_id in session_ids, "Linked session not found in my-analyses"
        
        print("PASS: Linked analysis appears in my-analyses")


class TestSharedReport:
    """Test shared report endpoints"""
    
    def test_create_shared_report(self):
        """POST /api/reports/share should create shared report"""
        # First create a session
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        # Create shared report
        report_response = requests.post(
            f"{BASE_URL}/api/reports/share",
            json={
                "session_id": session_id,
                "suspicion_score": 45,
                "suspicion_label": "Moderate Signal",
                "signals": {"emotional_indicators": 0.5},
                "summary": "Test report",
                "created_by": "test_user"
            }
        )
        assert report_response.status_code == 200
        data = report_response.json()
        assert "report_id" in data
        print(f"PASS: Shared report created - {data['report_id'][:8]}...")
        return data["report_id"]
    
    def test_get_shared_report(self):
        """GET /api/reports/{report_id} should return shared report"""
        # Create report first
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        report_response = requests.post(
            f"{BASE_URL}/api/reports/share",
            json={
                "session_id": session_id,
                "suspicion_score": 35,
                "suspicion_label": "Low Signal",
                "signals": {},
                "summary": "Test"
            }
        )
        report_id = report_response.json()["report_id"]
        
        # Get report
        get_response = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert "suspicion_score" in data
        print(f"PASS: Retrieved shared report with score {data['suspicion_score']}")
    
    def test_get_report_pdf(self):
        """GET /api/reports/{report_id}/pdf should return PDF"""
        # Create report first
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        report_response = requests.post(
            f"{BASE_URL}/api/reports/share",
            json={
                "session_id": session_id,
                "suspicion_score": 50,
                "suspicion_label": "Moderate Signal",
                "signals": {"routine_changes": 0.4},
                "summary": "PDF test report"
            }
        )
        report_id = report_response.json()["report_id"]
        
        # Get PDF
        pdf_response = requests.get(f"{BASE_URL}/api/reports/{report_id}/pdf")
        assert pdf_response.status_code == 200
        assert "application/pdf" in pdf_response.headers.get("content-type", "")
        assert pdf_response.content[:4] == b'%PDF'
        print(f"PASS: Report PDF generated - {len(pdf_response.content)} bytes")


class TestMirrorMode:
    """Test mirror/dual perspective mode"""
    
    def test_create_mirror_session(self):
        """POST /api/mirror/create should return mirror_id"""
        # Create analysis first
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        mirror_response = requests.post(
            f"{BASE_URL}/api/mirror/create",
            json={"session_id": session_id}
        )
        assert mirror_response.status_code == 200
        data = mirror_response.json()
        assert "mirror_id" in data
        print(f"PASS: Mirror session created - {data['mirror_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
