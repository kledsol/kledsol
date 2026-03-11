"""
Test suite for TrustLens Suspicion Score feature
Tests: POST /api/analysis/start, baseline, changes, timeline
       GET /api/analysis/{session_id}/results (suspicion_score, suspicion_label)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSuspicionScoreFeature:
    """Test suspicion score calculation and API responses"""
    
    # Store session IDs for cleanup
    created_sessions = []
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test - verify BASE_URL is set"""
        assert BASE_URL, "REACT_APP_BACKEND_URL environment variable must be set"
        yield
    
    def test_api_health(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "active"
        print("✓ API health check passed")
    
    def test_start_analysis_creates_session(self):
        """Test POST /api/analysis/start creates session with session_id"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data.get("type") == "deep"
        assert len(data["session_id"]) > 0  # UUID should be non-empty
        self.created_sessions.append(data["session_id"])
        print(f"✓ Session created: {data['session_id'][:8]}...")
    
    def test_submit_baseline_accepts_data(self):
        """Test POST /api/analysis/baseline accepts baseline data"""
        # First create a session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Submit baseline data
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 4,
            "communication_habits": "Regular daily communication",
            "emotional_closeness": 4,
            "transparency_level": 4
        }
        response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "baseline_recorded"
        assert data.get("next_step") == "changes"
        print("✓ Baseline data accepted")
    
    def test_submit_changes_accepts_categories(self):
        """Test POST /api/analysis/changes accepts change categories"""
        # Create session and submit baseline first
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 4,
            "communication_habits": "Regular",
            "emotional_closeness": 4,
            "transparency_level": 4
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit changes
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance", "schedule_changes"]
        }
        response = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "changes_recorded"
        assert data.get("next_step") == "timeline"
        print("✓ Changes data accepted")
    
    def test_submit_timeline_accepts_data(self):
        """Test POST /api/analysis/timeline accepts timeline data"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Submit baseline
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 4,
            "communication_habits": "Regular",
            "emotional_closeness": 4,
            "transparency_level": 4
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit changes
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Submit timeline
        timeline_data = {
            "session_id": session_id,
            "when_started": "2-4 weeks ago",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": True
        }
        response = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "timeline_recorded"
        assert data.get("next_step") == "investigation"
        print("✓ Timeline data accepted")
    
    def test_results_returns_suspicion_score_and_label(self):
        """Test GET /api/analysis/{session_id}/results returns suspicion_score and suspicion_label"""
        # Create session with full data
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Submit baseline
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "Occasional",
            "emotional_closeness": 3,
            "transparency_level": 3
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit changes
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Submit timeline
        timeline_data = {
            "session_id": session_id,
            "when_started": "1 week ago",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": False
        }
        requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        # Validate suspicion score structure
        assert "suspicion_score" in data
        assert "suspicion_label" in data
        assert isinstance(data["suspicion_score"], int)
        assert data["suspicion_score"] >= 0
        assert data["suspicion_score"] <= 100
        assert isinstance(data["suspicion_label"], str)
        assert data["suspicion_label"] in ["Low Signal", "Moderate Signal", "Elevated Pattern Risk", "High Pattern Risk"]
        
        print(f"✓ Results endpoint returns suspicion_score: {data['suspicion_score']}, label: {data['suspicion_label']}")
    
    def test_high_risk_scenario_suspicion_score(self):
        """
        Test high-risk scenario with phone_secrecy+emotional_distance+schedule_changes+defensive_behavior
        plus sudden+multiple_at_once and low transparency/closeness should give ~81 (High Pattern Risk)
        """
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Submit baseline with LOW transparency and closeness (<=2 adds +8 and +5)
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 2,
            "communication_habits": "Minimal",
            "emotional_closeness": 2,  # Low closeness (+5)
            "transparency_level": 2    # Low transparency (+8)
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit high-risk changes:
        # phone_secrecy: +15
        # emotional_distance: +15
        # schedule_changes: +10
        # defensive_behavior: +15
        # Total from changes: 55
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance", "schedule_changes", "defensive_behavior"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Submit timeline with sudden (+8) and multiple_at_once (+5)
        # Total from timeline: 13
        timeline_data = {
            "session_id": session_id,
            "when_started": "1 week ago",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": True
        }
        requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        
        # Get results
        # Expected: changes(55) + timeline(13) + baseline(8+5=13) = 81
        # But signals and hypotheses may contribute additional points
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        suspicion_score = data["suspicion_score"]
        suspicion_label = data["suspicion_label"]
        
        # Based on calculation: phone_secrecy(15)+emotional_distance(15)+schedule_changes(10)+defensive_behavior(15)=55
        # + sudden(8) + multiple_at_once(5) = 13
        # + low_transparency(8) + low_closeness(5) = 13
        # Total minimum: 55+13+13 = 81
        # Label should be "High Pattern Risk" (81-100)
        
        assert suspicion_score >= 75, f"Expected score >= 75 for high-risk scenario, got {suspicion_score}"
        assert suspicion_label in ["Elevated Pattern Risk", "High Pattern Risk"], f"Expected elevated/high risk, got {suspicion_label}"
        
        print(f"✓ High-risk scenario: score={suspicion_score}, label={suspicion_label}")
    
    def test_empty_session_returns_zero_score(self):
        """Test empty session with no changes should return suspicion_score of 0 (Low Signal)"""
        # Create session but don't submit any data
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Get results without submitting any data
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        suspicion_score = data["suspicion_score"]
        suspicion_label = data["suspicion_label"]
        
        # Empty session should have 0 score
        assert suspicion_score == 0, f"Expected score 0 for empty session, got {suspicion_score}"
        assert suspicion_label == "Low Signal", f"Expected 'Low Signal' label, got {suspicion_label}"
        
        print(f"✓ Empty session: score={suspicion_score}, label={suspicion_label}")
    
    def test_low_risk_scenario(self):
        """Test low-risk scenario should return Low Signal (0-30)"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Submit baseline with HIGH transparency and closeness
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "3+ years",
            "prior_satisfaction": 5,
            "communication_habits": "Very frequent",
            "emotional_closeness": 5,  # High closeness (no bonus)
            "transparency_level": 5    # High transparency (no bonus)
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit minimal change category (only communication - 12 pts)
        changes_data = {
            "session_id": session_id,
            "categories": ["communication"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Submit timeline with gradual changes
        timeline_data = {
            "session_id": session_id,
            "when_started": "3+ months ago",
            "gradual_or_sudden": "gradual",  # No bonus
            "multiple_at_once": False  # No bonus
        }
        requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        suspicion_score = data["suspicion_score"]
        suspicion_label = data["suspicion_label"]
        
        # Low risk should be in Low Signal range (0-30)
        assert suspicion_score <= 30, f"Expected score <= 30 for low-risk scenario, got {suspicion_score}"
        assert suspicion_label == "Low Signal", f"Expected 'Low Signal' label, got {suspicion_label}"
        
        print(f"✓ Low-risk scenario: score={suspicion_score}, label={suspicion_label}")
    
    def test_moderate_risk_scenario(self):
        """Test moderate-risk scenario should return Moderate Signal (31-60)"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Submit baseline with moderate levels
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "Regular",
            "emotional_closeness": 3,
            "transparency_level": 3
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit moderate changes (communication 12 + schedule_changes 10 + intimacy_changes 12 = 34)
        changes_data = {
            "session_id": session_id,
            "categories": ["communication", "schedule_changes", "intimacy_changes"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Submit timeline with gradual changes
        timeline_data = {
            "session_id": session_id,
            "when_started": "1 month ago",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": False
        }
        requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        suspicion_score = data["suspicion_score"]
        suspicion_label = data["suspicion_label"]
        
        # Moderate risk should be 31-60
        assert suspicion_score >= 31 and suspicion_score <= 60, f"Expected 31-60 for moderate-risk, got {suspicion_score}"
        assert suspicion_label == "Moderate Signal", f"Expected 'Moderate Signal' label, got {suspicion_label}"
        
        print(f"✓ Moderate-risk scenario: score={suspicion_score}, label={suspicion_label}")
    
    def test_results_contains_all_required_fields(self):
        """Test results endpoint returns all required fields"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        self.created_sessions.append(session_id)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields exist
        required_fields = [
            "session_id",
            "suspicion_score",
            "suspicion_label",
            "trust_disruption_index",
            "stability_hearts",
            "dominant_pattern",
            "confidence_level",
            "narrative_consistency",
            "hypotheses",
            "signals",
            "pattern_statistics",
            "clarity_actions",
            "timeline_events",
            "trustlens_perspective"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print("✓ Results endpoint contains all required fields")
    
    def test_invalid_session_returns_404(self):
        """Test GET results for non-existent session returns 404"""
        fake_session_id = "non-existent-session-id-12345"
        response = requests.get(f"{BASE_URL}/api/analysis/{fake_session_id}/results")
        assert response.status_code == 404
        print("✓ Invalid session returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
