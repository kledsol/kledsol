"""
Test Suite for TrustLens Auth & Signal Trend Tracking Features
Tests: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me,
       POST /api/auth/link-analysis, GET /api/auth/my-analyses, 
       GET /api/auth/signal-trends/{session_id}
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable is required")


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ============= Registration Tests =============

class TestAuthRegister:
    """Tests for POST /api/auth/register endpoint"""
    
    def test_register_creates_account_and_returns_token(self, api_client):
        """POST /api/auth/register creates account and returns user_id, email, token"""
        unique_email = f"TEST_newuser_{uuid.uuid4().hex[:8]}@trustlens.com"
        payload = {
            "email": unique_email,
            "password": "secure123"
        }
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "user_id" in data, "Response should contain user_id"
        assert "email" in data, "Response should contain email"
        assert "token" in data, "Response should contain token"
        
        # Validate values
        assert data["email"] == unique_email.lower()
        assert len(data["user_id"]) > 0
        assert len(data["token"]) > 0  # JWT token should exist
        print(f"✓ Registration successful - user_id: {data['user_id']}, token length: {len(data['token'])}")
    
    def test_register_returns_409_for_duplicate_email(self, api_client):
        """POST /api/auth/register returns 409 for duplicate email"""
        # Use the existing test account
        payload = {
            "email": "test@trustlens.com",
            "password": "secure123"
        }
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 409, f"Expected 409 for duplicate email, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower() or "already" in data["detail"].lower()
        print(f"✓ Duplicate email correctly rejected with 409")
    
    def test_register_returns_400_for_short_password(self, api_client):
        """POST /api/auth/register returns 400 for password < 6 chars"""
        payload = {
            "email": f"TEST_shortpwd_{uuid.uuid4().hex[:8]}@trustlens.com",
            "password": "12345"  # Only 5 chars
        }
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        
        assert response.status_code == 400, f"Expected 400 for short password, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "6" in data["detail"] or "min" in data["detail"].lower()
        print(f"✓ Short password correctly rejected with 400")


# ============= Login Tests =============

class TestAuthLogin:
    """Tests for POST /api/auth/login endpoint"""
    
    def test_login_returns_token_for_valid_credentials(self, api_client):
        """POST /api/auth/login returns token for valid credentials"""
        payload = {
            "email": "test@trustlens.com",
            "password": "secure123"
        }
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "user_id" in data, "Response should contain user_id"
        assert "email" in data, "Response should contain email"
        assert "token" in data, "Response should contain token"
        
        # Validate values
        assert data["email"] == "test@trustlens.com"
        assert len(data["token"]) > 0
        print(f"✓ Login successful - token length: {len(data['token'])}")
    
    def test_login_returns_401_for_invalid_credentials(self, api_client):
        """POST /api/auth/login returns 401 for invalid credentials"""
        payload = {
            "email": "test@trustlens.com",
            "password": "wrongpassword"
        }
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401, f"Expected 401 for invalid credentials, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Invalid credentials correctly rejected with 401")
    
    def test_login_returns_401_for_nonexistent_email(self, api_client):
        """POST /api/auth/login returns 401 for non-existent email"""
        payload = {
            "email": f"nonexistent_{uuid.uuid4().hex[:8]}@trustlens.com",
            "password": "secure123"
        }
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401, f"Expected 401 for non-existent email, got {response.status_code}"
        print(f"✓ Non-existent email correctly rejected with 401")


# ============= Auth Me Tests =============

class TestAuthMe:
    """Tests for GET /api/auth/me endpoint"""
    
    def test_me_returns_user_profile_with_valid_token(self, api_client):
        """GET /api/auth/me returns user profile with valid token"""
        # First login to get token
        login_response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@trustlens.com", "password": "secure123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Now call /me endpoint
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response contains user info
        assert "user_id" in data, "Response should contain user_id"
        assert "email" in data, "Response should contain email"
        assert data["email"] == "test@trustlens.com"
        assert "password_hash" not in data, "Password hash should not be returned"
        print(f"✓ /me endpoint returned user profile - email: {data['email']}")
    
    def test_me_returns_401_without_token(self, api_client):
        """GET /api/auth/me returns 401 without token"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401, f"Expected 401 without token, got {response.status_code}"
        print(f"✓ /me without token correctly returns 401")
    
    def test_me_returns_401_with_invalid_token(self, api_client):
        """GET /api/auth/me returns 401 with invalid token"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401, f"Expected 401 with invalid token, got {response.status_code}"
        print(f"✓ /me with invalid token correctly returns 401")


# ============= Link Analysis Tests =============

class TestLinkAnalysis:
    """Tests for POST /api/auth/link-analysis endpoint"""
    
    def test_link_analysis_creates_signal_snapshot(self, api_client):
        """POST /api/auth/link-analysis links session to user and creates signal snapshot"""
        # First login
        login_response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@trustlens.com", "password": "secure123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Create a new analysis session
        session_response = api_client.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # Submit some data to populate the session
        api_client.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 7,
            "communication_habits": "daily",
            "emotional_closeness": 6,
            "transparency_level": 5
        })
        
        api_client.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance"]
        })
        
        # Now link the analysis
        response = api_client.post(
            f"{BASE_URL}/api/auth/link-analysis",
            json={"session_id": session_id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["status"] == "linked"
        assert data["session_id"] == session_id
        print(f"✓ Analysis linked successfully - session_id: {session_id}")
    
    def test_link_analysis_returns_401_without_auth(self, api_client):
        """POST /api/auth/link-analysis returns 401 without authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/link-analysis",
            json={"session_id": "some-session-id"}
        )
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ Link analysis without auth correctly returns 401")


# ============= My Analyses Tests =============

class TestMyAnalyses:
    """Tests for GET /api/auth/my-analyses endpoint"""
    
    def test_my_analyses_returns_list(self, api_client):
        """GET /api/auth/my-analyses returns list of user's linked analyses"""
        # Login
        login_response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@trustlens.com", "password": "secure123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        response = api_client.get(
            f"{BASE_URL}/api/auth/my-analyses",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "analyses" in data
        assert "total" in data
        assert isinstance(data["analyses"], list)
        assert data["total"] >= 0
        
        # If there are analyses, validate structure
        if len(data["analyses"]) > 0:
            analysis = data["analyses"][0]
            assert "session_id" in analysis
            assert "analysis_type" in analysis
            assert "created_at" in analysis
            print(f"✓ My analyses returned {len(data['analyses'])} analyses")
        else:
            print(f"✓ My analyses returned empty list (new user)")
    
    def test_my_analyses_returns_401_without_auth(self, api_client):
        """GET /api/auth/my-analyses returns 401 without authentication"""
        response = api_client.get(f"{BASE_URL}/api/auth/my-analyses")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ My analyses without auth correctly returns 401")


# ============= Signal Trends Tests =============

class TestSignalTrends:
    """Tests for GET /api/auth/signal-trends/{session_id} endpoint"""
    
    @pytest.fixture
    def auth_token(self, api_client):
        """Get authentication token"""
        login_response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@trustlens.com", "password": "secure123"}
        )
        assert login_response.status_code == 200
        return login_response.json()["token"]
    
    def test_signal_trends_returns_has_previous_false_for_first_analysis(self, api_client, auth_token):
        """GET /api/auth/signal-trends/{session_id} returns has_previous=false for first analysis (of a new user)"""
        # Create a new user to test first analysis
        unique_email = f"TEST_firstanalysis_{uuid.uuid4().hex[:8]}@trustlens.com"
        register_response = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": unique_email, "password": "secure123"}
        )
        assert register_response.status_code == 200
        new_token = register_response.json()["token"]
        
        # Create an analysis session
        session_response = api_client.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # Link the analysis
        link_response = api_client.post(
            f"{BASE_URL}/api/auth/link-analysis",
            json={"session_id": session_id},
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert link_response.status_code == 200
        
        # Get signal trends
        response = api_client.get(
            f"{BASE_URL}/api/auth/signal-trends/{session_id}",
            headers={"Authorization": f"Bearer {new_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "has_previous" in data
        assert data["has_previous"] == False, "First analysis should have has_previous=False"
        assert "trends" in data
        assert data["trends"] == {}
        print(f"✓ Signal trends for first analysis correctly returns has_previous=False")
    
    def test_signal_trends_returns_deltas_for_second_analysis(self, api_client):
        """GET /api/auth/signal-trends/{session_id} returns trends with delta values for second+ analysis"""
        # Create a dedicated user for this test
        unique_email = f"TEST_secondanalysis_{uuid.uuid4().hex[:8]}@trustlens.com"
        register_response = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": unique_email, "password": "secure123"}
        )
        assert register_response.status_code == 200
        test_token = register_response.json()["token"]
        
        # Create first analysis session with changes
        session1_response = api_client.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert session1_response.status_code == 200
        session1_id = session1_response.json()["session_id"]
        
        api_client.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session1_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 7,
            "communication_habits": "daily",
            "emotional_closeness": 6,
            "transparency_level": 5
        })
        
        api_client.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session1_id,
            "categories": ["phone_secrecy", "emotional_distance"]
        })
        
        # Link first analysis
        api_client.post(
            f"{BASE_URL}/api/auth/link-analysis",
            json={"session_id": session1_id},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Create second analysis session with different changes
        session2_response = api_client.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert session2_response.status_code == 200
        session2_id = session2_response.json()["session_id"]
        
        api_client.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session2_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 5,
            "communication_habits": "weekly",
            "emotional_closeness": 4,
            "transparency_level": 3
        })
        
        api_client.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session2_id,
            "categories": ["phone_secrecy", "emotional_distance", "schedule_changes"]
        })
        
        # Link second analysis
        api_client.post(
            f"{BASE_URL}/api/auth/link-analysis",
            json={"session_id": session2_id},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        # Get signal trends for second analysis
        response = api_client.get(
            f"{BASE_URL}/api/auth/signal-trends/{session2_id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "has_previous" in data
        assert data["has_previous"] == True, "Second analysis should have has_previous=True"
        assert "trends" in data
        assert isinstance(data["trends"], dict)
        
        # Check structure of trends
        if len(data["trends"]) > 0:
            first_key = list(data["trends"].keys())[0]
            trend = data["trends"][first_key]
            assert "current" in trend or "delta" in trend
            print(f"✓ Signal trends for second analysis correctly returns has_previous=True with {len(data['trends'])} trend keys")
        else:
            print(f"✓ Signal trends returned has_previous=True (trends may be empty if signals identical)")
    
    def test_signal_trends_returns_401_without_auth(self, api_client):
        """GET /api/auth/signal-trends/{session_id} returns 401 without authentication"""
        response = api_client.get(f"{BASE_URL}/api/auth/signal-trends/some-session-id")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ Signal trends without auth correctly returns 401")


# ============= Test Existing Test Account =============

class TestExistingTestAccount:
    """Tests using the pre-existing test account mentioned in requirements"""
    
    def test_existing_test_account_works(self, api_client):
        """Verify the existing test account (test@trustlens.com/secure123) works"""
        payload = {
            "email": "test@trustlens.com",
            "password": "secure123"
        }
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "token" in data
        assert data["email"] == "test@trustlens.com"
        print(f"✓ Existing test account test@trustlens.com works correctly")
    
    def test_existing_test_account_has_linked_analyses(self, api_client):
        """Verify the existing test account has linked analyses (as per requirements: 2 linked)"""
        # Login
        login_response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@trustlens.com", "password": "secure123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Get analyses
        response = api_client.get(
            f"{BASE_URL}/api/auth/my-analyses",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # According to requirements, this account has 2 linked analyses
        assert len(data["analyses"]) >= 2, f"Expected at least 2 analyses, got {len(data['analyses'])}"
        print(f"✓ Test account has {len(data['analyses'])} linked analyses (expected >= 2)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
