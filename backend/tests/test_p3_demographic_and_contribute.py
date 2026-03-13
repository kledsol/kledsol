"""
P3 Features Testing - TrustLens
1. Enhanced Demographic Filtering - age_range and cohabitation_status in baseline
2. Global Pattern Engine - contribute-from-session endpoint and case stats

Test file created for iteration 17.
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEnhancedDemographicFiltering:
    """Tests for age_range and cohabitation_status optional fields in baseline"""
    
    @pytest.fixture
    def session_id(self):
        """Create a fresh deep analysis session"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        return data["session_id"]
    
    def test_baseline_accepts_age_range_and_cohabitation(self, session_id):
        """Test that POST /api/analysis/baseline accepts optional age_range and cohabitation_status"""
        payload = {
            "session_id": session_id,
            "relationship_duration": "3_to_5",
            "prior_satisfaction": 7,
            "communication_habits": "We communicate daily via text and calls",
            "emotional_closeness": 8,
            "transparency_level": 7,
            "age_range": "25-35",
            "cohabitation_status": "living_together"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "baseline_recorded"
        assert data["next_step"] == "changes"
        print(f"SUCCESS: Baseline accepted with age_range={payload['age_range']}, cohabitation_status={payload['cohabitation_status']}")
    
    def test_baseline_works_without_optional_fields(self, session_id):
        """Test backward compatibility - baseline works WITHOUT age_range and cohabitation_status"""
        payload = {
            "session_id": session_id,
            "relationship_duration": "1_to_3",
            "prior_satisfaction": 6,
            "communication_habits": "We talk in person mostly",
            "emotional_closeness": 7,
            "transparency_level": 6
            # No age_range or cohabitation_status
        }
        response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "baseline_recorded"
        print("SUCCESS: Baseline works without optional demographic fields (backward compatible)")
    
    def test_baseline_with_all_age_ranges(self, session_id):
        """Test baseline with various age_range values"""
        age_ranges = ["18-25", "25-35", "35-45", "45-55", "55+"]
        for age in age_ranges:
            # Create fresh session for each
            resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
            sid = resp.json()["session_id"]
            
            payload = {
                "session_id": sid,
                "relationship_duration": "1_to_3",
                "prior_satisfaction": 7,
                "communication_habits": "Daily conversations",
                "emotional_closeness": 7,
                "transparency_level": 7,
                "age_range": age
            }
            response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=payload)
            assert response.status_code == 200
            print(f"  - age_range={age} accepted")
        print("SUCCESS: All age_range values accepted")
    
    def test_baseline_with_all_cohabitation_statuses(self, session_id):
        """Test baseline with various cohabitation_status values"""
        statuses = ["living_together", "living_apart", "part_time"]
        for status in statuses:
            resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
            sid = resp.json()["session_id"]
            
            payload = {
                "session_id": sid,
                "relationship_duration": "3_to_5",
                "prior_satisfaction": 7,
                "communication_habits": "Regular communication",
                "emotional_closeness": 7,
                "transparency_level": 7,
                "cohabitation_status": status
            }
            response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=payload)
            assert response.status_code == 200
            print(f"  - cohabitation_status={status} accepted")
        print("SUCCESS: All cohabitation_status values accepted")


class TestGlobalPatternEngine:
    """Tests for contribute-from-session endpoint and case stats"""
    
    @pytest.fixture
    def completed_session(self):
        """Create a completed analysis session with changes and signals"""
        # Start session
        resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        
        # Submit baseline with demographics
        baseline = {
            "session_id": session_id,
            "relationship_duration": "3_to_5",
            "prior_satisfaction": 6,
            "communication_habits": "We used to talk daily",
            "emotional_closeness": 5,
            "transparency_level": 4,
            "age_range": "25-35",
            "cohabitation_status": "living_together"
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline)
        
        # Submit changes
        changes = {
            "session_id": session_id,
            "categories": ["routine_changes", "communication_changes", "emotional_distance"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes)
        
        # Submit timeline
        timeline = {
            "session_id": session_id,
            "when_started": "3_months",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": True
        }
        requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline)
        
        return session_id
    
    def test_get_case_stats(self):
        """Test GET /api/cases/stats returns total_cases, user_contributed, seeded counts"""
        response = requests.get(f"{BASE_URL}/api/cases/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_cases" in data
        assert "user_contributed" in data
        assert "seeded" in data
        assert isinstance(data["total_cases"], int)
        assert isinstance(data["user_contributed"], int)
        assert isinstance(data["seeded"], int)
        assert data["total_cases"] >= 300  # Should have seeded data
        print(f"SUCCESS: Case stats - Total: {data['total_cases']}, User contributed: {data['user_contributed']}, Seeded: {data['seeded']}")
    
    def test_contribute_from_session_valid_outcome(self, completed_session):
        """Test POST /api/cases/contribute-from-session with valid outcome"""
        session_id = completed_session
        
        valid_outcomes = [
            "confirmed_infidelity",
            "emotional_disengagement",
            "misunderstanding",
            "personal_crisis",
            "unresolved_conflict"
        ]
        
        # Test with one valid outcome
        payload = {
            "session_id": session_id,
            "outcome": "misunderstanding"
        }
        response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # First contribution should return accepted
        assert data["status"] in ["accepted", "already_contributed"]
        if data["status"] == "accepted":
            assert "case_id" in data
            assert data["case_id"].startswith("TL-U")
            assert "new_total_cases" in data
        print(f"SUCCESS: Contribution accepted with outcome='misunderstanding', case_id={data.get('case_id')}")
    
    def test_contribute_from_session_invalid_outcome(self, completed_session):
        """Test POST /api/cases/contribute-from-session rejects invalid outcome"""
        # Create fresh session to avoid already_contributed
        resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        
        # Submit minimal baseline
        baseline = {
            "session_id": session_id,
            "relationship_duration": "1_to_3",
            "prior_satisfaction": 7,
            "communication_habits": "Normal",
            "emotional_closeness": 7,
            "transparency_level": 7
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline)
        
        payload = {
            "session_id": session_id,
            "outcome": "invalid_outcome_value"
        }
        response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "outcome must be one of" in data["detail"]
        print(f"SUCCESS: Invalid outcome rejected with error: {data['detail']}")
    
    def test_contribute_from_session_duplicate_returns_already_contributed(self, completed_session):
        """Test POST /api/cases/contribute-from-session returns already_contributed on duplicate"""
        session_id = completed_session
        
        # First contribution
        payload = {
            "session_id": session_id,
            "outcome": "emotional_disengagement"
        }
        first_response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json=payload)
        assert first_response.status_code == 200
        
        # Second attempt (duplicate)
        second_response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json=payload)
        assert second_response.status_code == 200
        data = second_response.json()
        assert data["status"] == "already_contributed"
        assert "case_id" in data
        print(f"SUCCESS: Duplicate contribution returns already_contributed with case_id={data['case_id']}")
    
    def test_contribute_from_session_missing_fields(self):
        """Test POST /api/cases/contribute-from-session with missing required fields"""
        # Missing session_id
        response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json={"outcome": "misunderstanding"})
        assert response.status_code == 400
        
        # Missing outcome
        resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        sid = resp.json()["session_id"]
        response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json={"session_id": sid})
        assert response.status_code == 400
        print("SUCCESS: Missing fields properly rejected with 400")
    
    def test_contribute_from_session_invalid_session(self):
        """Test POST /api/cases/contribute-from-session with non-existent session"""
        payload = {
            "session_id": "non-existent-session-id-12345",
            "outcome": "misunderstanding"
        }
        response = requests.post(f"{BASE_URL}/api/cases/contribute-from-session", json=payload)
        assert response.status_code == 404
        print("SUCCESS: Non-existent session returns 404")


class TestFullAnalysisFlowWithDemographics:
    """Test full analysis flow with demographic filtering applied"""
    
    def test_full_flow_produces_results_with_demographic_filtering(self):
        """Run complete analysis with demographics and verify pattern comparison includes filtering"""
        # Start session
        resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]
        
        # Submit baseline with demographics
        baseline = {
            "session_id": session_id,
            "relationship_duration": "3_to_5",
            "prior_satisfaction": 5,
            "communication_habits": "We used to talk openly",
            "emotional_closeness": 4,
            "transparency_level": 3,
            "age_range": "25-35",
            "cohabitation_status": "living_together"
        }
        resp = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline)
        assert resp.status_code == 200
        
        # Submit changes
        changes = {
            "session_id": session_id,
            "categories": ["routine_changes", "communication_changes", "emotional_distance", "digital_behavior"]
        }
        resp = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes)
        assert resp.status_code == 200
        
        # Submit timeline
        timeline = {
            "session_id": session_id,
            "when_started": "1_month",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": True
        }
        resp = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline)
        assert resp.status_code == 200
        
        # Answer core questions
        for i in range(5):
            q_resp = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            assert q_resp.status_code == 200
            question = q_resp.json()
            
            if question.get("question_id") == "complete":
                break
            
            answer = {
                "session_id": session_id,
                "question_id": question["question_id"],
                "question_text": question["question_text"],
                "answer": question["options"][2] if question.get("options") else "Noticeable changes",
                "category": question["category"]
            }
            a_resp = requests.post(f"{BASE_URL}/api/analysis/answer", json=answer)
            assert a_resp.status_code == 200
        
        # Get results
        results_resp = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert results_resp.status_code == 200
        results = results_resp.json()
        
        # Verify results structure
        assert "suspicion_score" in results
        assert "case_comparison" in results
        assert "pattern_statistics" in results
        
        # Check demographic filtering in case_comparison
        case_comparison = results["case_comparison"]
        assert "demographic_filtered" in case_comparison
        assert "total_cases" in case_comparison
        
        print(f"SUCCESS: Full analysis completed")
        print(f"  - Suspicion score: {results['suspicion_score']}")
        print(f"  - Demographic filtered: {case_comparison.get('demographic_filtered')}")
        print(f"  - Demographic label: {case_comparison.get('demographic_label')}")
        print(f"  - Similar cases found: {case_comparison.get('similar_case_count')}")


class TestAuthAndMyAnalyses:
    """Tests for authentication and my-analyses endpoint"""
    
    def test_auth_login(self):
        """Test POST /api/auth/login works correctly"""
        payload = {"email": "syscheck@test.com", "password": "test1234"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print("SUCCESS: Login returns token")
    
    def test_auth_register(self):
        """Test POST /api/auth/register creates new user"""
        unique_email = f"TEST_p3_{uuid.uuid4().hex[:8]}@test.com"
        payload = {"email": unique_email, "password": "testpass123"}
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"SUCCESS: Registered new user {unique_email}")
    
    def test_my_analyses_returns_enhanced_data(self):
        """Test GET /api/auth/my-analyses returns suspicion_score, top_signals, dominant_pattern"""
        # Login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "syscheck@test.com", "password": "test1234"})
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/my-analyses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "analyses" in data
        assert "total" in data
        print(f"SUCCESS: my-analyses returns {data['total']} analyses")
        
        # If there are analyses, verify enhanced fields
        if data["analyses"]:
            analysis = data["analyses"][0]
            expected_fields = ["session_id", "analysis_type", "created_at"]
            for field in expected_fields:
                assert field in analysis, f"Missing field: {field}"
            
            # Check for enhanced fields (may be None for old analyses)
            enhanced_fields = ["suspicion_score", "dominant_pattern", "top_signals"]
            for field in enhanced_fields:
                if field in analysis:
                    print(f"  - {field}: {analysis[field]}")


class TestLandingAndConversationCoach:
    """Tests for landing page and conversation coach endpoints"""
    
    def test_landing_api_health(self):
        """Test GET /api/ returns active status"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        print("SUCCESS: API health check passed")
    
    def test_conversation_coach_pdf(self):
        """Test POST /api/analysis/conversation-coach/pdf returns valid PDF"""
        # Create session and get guidance first
        resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        
        # Submit minimal baseline
        baseline = {
            "session_id": session_id,
            "relationship_duration": "1_to_3",
            "prior_satisfaction": 7,
            "communication_habits": "Normal",
            "emotional_closeness": 7,
            "transparency_level": 7
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline)
        
        # Request PDF
        payload = {
            "session_id": session_id,
            "tone": "gentle",
            "topic": "recent_changes"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach/pdf", json=payload)
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content[:4] == b"%PDF"
        print("SUCCESS: Conversation coach PDF export works")


# Run pytest with verbose output
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
