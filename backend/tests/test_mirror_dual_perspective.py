"""
Test Mirror / Dual Perspective Analysis Feature
Tests the complete flow:
1. Partner A creates a session and completes analysis
2. Partner A creates a mirror invite
3. Partner B joins via invite link
4. Partner B completes their analysis
5. Both partners consent
6. Dual perspective report is generated
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# =============================================================================
# Helper Functions
# =============================================================================

def create_session_and_complete_analysis(session=None):
    """Helper to create a session and complete baseline, changes, timeline, and 5 core questions."""
    if not session:
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
    
    # Start a deep analysis session
    resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    
    # Submit baseline
    baseline_data = {
        "session_id": session_id,
        "relationship_duration": "3-5 years",
        "prior_satisfaction": 3,
        "communication_habits": "weekly",
        "emotional_closeness": 3,
        "transparency_level": 3
    }
    resp = session.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
    assert resp.status_code == 200
    
    # Submit changes
    changes_data = {
        "session_id": session_id,
        "categories": ["emotional_distance", "communication", "phone_secrecy"]
    }
    resp = session.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
    assert resp.status_code == 200
    
    # Submit timeline
    timeline_data = {
        "session_id": session_id,
        "when_started": "1-3 months ago",
        "gradual_or_sudden": "gradual",
        "multiple_at_once": True
    }
    resp = session.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
    assert resp.status_code == 200
    
    # Answer 5 core questions with concerning answers to generate some signals
    for i in range(5):
        resp = session.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        assert resp.status_code == 200
        q = resp.json()
        if q.get("question_id") == "complete":
            break
        
        # Choose option 2 or 3 (mildly concerning)
        answer_choice = q["options"][2] if len(q["options"]) > 2 else q["options"][1]
        answer_data = {
            "session_id": session_id,
            "question_id": q["question_id"],
            "question_text": q["question_text"],
            "answer": answer_choice,
            "category": q["category"]
        }
        resp = session.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        assert resp.status_code == 200
    
    return session_id


# =============================================================================
# Test: POST /api/mirror/create creates a mirror session
# =============================================================================
class TestMirrorCreate:
    """Tests for POST /api/mirror/create endpoint"""
    
    def test_create_mirror_session_success(self):
        """POST /api/mirror/create creates a mirror session and returns mirror_id"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # First create an analysis session
        session_id = create_session_and_complete_analysis(session)
        
        # Create mirror session
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify response structure
        assert "mirror_id" in data
        assert len(data["mirror_id"]) > 0
        print(f"✓ Mirror session created: mirror_id={data['mirror_id']}")
    
    def test_create_mirror_session_invalid_session(self):
        """POST /api/mirror/create returns 404 for invalid session_id"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": "invalid-session-id-123"})
        assert resp.status_code == 404
        print("✓ Mirror create correctly returns 404 for invalid session")


# =============================================================================
# Test: GET /api/mirror/{mirror_id}/join
# =============================================================================
class TestMirrorJoin:
    """Tests for GET /api/mirror/{mirror_id}/join endpoint"""
    
    def test_join_mirror_session_creates_partner_b_session(self):
        """GET /api/mirror/{mirror_id}/join creates a new session for Partner B"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner B joins
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify response structure
        assert "session_id" in data
        assert "mirror_id" in data
        assert data["mirror_id"] == mirror_id
        assert "already_joined" not in data or data["already_joined"] == False
        print(f"✓ Partner B joined: session_id={data['session_id']}")
    
    def test_join_mirror_session_already_joined_returns_flag(self):
        """GET /api/mirror/{mirror_id}/join returns already_joined=true if called again"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner B joins first time
        resp1 = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        assert resp1.status_code == 200
        first_session_id = resp1.json()["session_id"]
        
        # Partner B tries to join again
        resp2 = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        assert resp2.status_code == 200
        data = resp2.json()
        
        # Should return already_joined flag
        assert data["already_joined"] == True
        assert data["session_id"] == first_session_id  # Same session
        print("✓ Already joined flag returned correctly")
    
    def test_join_invalid_mirror_returns_404(self):
        """GET /api/mirror/{mirror_id}/join returns 404 for invalid mirror_id"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        resp = session.get(f"{BASE_URL}/api/mirror/invalid-mirror-123/join")
        assert resp.status_code == 404
        print("✓ Join correctly returns 404 for invalid mirror_id")


# =============================================================================
# Test: GET /api/mirror/{mirror_id}/status
# =============================================================================
class TestMirrorStatus:
    """Tests for GET /api/mirror/{mirror_id}/status endpoint"""
    
    def test_status_before_partner_b_joins(self):
        """GET /api/mirror/{mirror_id}/status shows partner_b_joined=false initially"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Check status
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/status")
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["partner_b_joined"] == False
        assert data["partner_a_consented"] == False
        assert data["partner_b_consented"] == False
        assert data["report_ready"] == False
        print("✓ Status correct before Partner B joins")
    
    def test_status_after_partner_b_joins(self):
        """GET /api/mirror/{mirror_id}/status shows partner_b_joined=true after join"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner B joins
        session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        
        # Check status
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/status")
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["partner_b_joined"] == True
        assert data["partner_b_complete"] == False  # Not completed analysis yet
        print("✓ Status correct after Partner B joins")
    
    def test_status_invalid_mirror_returns_404(self):
        """GET /api/mirror/{mirror_id}/status returns 404 for invalid mirror_id"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        resp = session.get(f"{BASE_URL}/api/mirror/invalid-mirror-456/status")
        assert resp.status_code == 404
        print("✓ Status correctly returns 404 for invalid mirror_id")


# =============================================================================
# Test: POST /api/mirror/{mirror_id}/consent
# =============================================================================
class TestMirrorConsent:
    """Tests for POST /api/mirror/{mirror_id}/consent endpoint"""
    
    def test_partner_a_consent(self):
        """POST /api/mirror/{mirror_id}/consent sets consent for Partner A"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner A consents
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_a_id})
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["consented"] == True
        assert data["role"] == "a"
        assert data["both_consented"] == False  # Partner B hasn't consented yet
        print("✓ Partner A consent recorded correctly")
    
    def test_partner_b_consent(self):
        """POST /api/mirror/{mirror_id}/consent sets consent for Partner B"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner B joins
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        session_b_id = resp.json()["session_id"]
        
        # Partner B consents
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_b_id})
        assert resp.status_code == 200
        data = resp.json()
        
        assert data["consented"] == True
        assert data["role"] == "b"
        print("✓ Partner B consent recorded correctly")
    
    def test_consent_invalid_session_returns_403(self):
        """POST /api/mirror/{mirror_id}/consent returns 403 for invalid session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Try to consent with invalid session
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": "invalid-session-xyz"})
        assert resp.status_code == 403
        print("✓ Consent correctly returns 403 for invalid session")


# =============================================================================
# Test: GET /api/mirror/{mirror_id}/report - 403 when not both consented
# =============================================================================
class TestMirrorReportGuard:
    """Tests for GET /api/mirror/{mirror_id}/report access control"""
    
    def test_report_returns_403_when_no_consent(self):
        """GET /api/mirror/{mirror_id}/report returns 403 if neither partner consented"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Try to get report without consent
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/report")
        assert resp.status_code == 403
        print("✓ Report returns 403 when no consent")
    
    def test_report_returns_403_when_only_one_consented(self):
        """GET /api/mirror/{mirror_id}/report returns 403 if only one partner consented"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Partner A creates session and mirror
        session_a_id = create_session_and_complete_analysis(session)
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Only Partner A consents
        session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_a_id})
        
        # Try to get report
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/report")
        assert resp.status_code == 403
        print("✓ Report returns 403 when only Partner A consented")


# =============================================================================
# Test: Full dual perspective flow with report generation
# =============================================================================
class TestMirrorFullFlow:
    """End-to-end test of the complete Mirror/Dual Perspective flow"""
    
    def test_full_dual_perspective_flow_with_report(self):
        """Full flow: both partners complete, consent, and report is generated"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        print("\n--- Step 1: Partner A completes analysis ---")
        session_a_id = create_session_and_complete_analysis(session)
        print(f"Partner A session: {session_a_id}")
        
        print("\n--- Step 2: Partner A creates mirror invite ---")
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        assert resp.status_code == 200
        mirror_id = resp.json()["mirror_id"]
        print(f"Mirror ID: {mirror_id}")
        
        print("\n--- Step 3: Partner B joins via invite ---")
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        assert resp.status_code == 200
        session_b_id = resp.json()["session_id"]
        print(f"Partner B session: {session_b_id}")
        
        print("\n--- Step 4: Partner B completes their analysis ---")
        # Submit baseline for Partner B
        baseline_data = {
            "session_id": session_b_id,
            "relationship_duration": "3-5 years",
            "prior_satisfaction": 4,
            "communication_habits": "daily",
            "emotional_closeness": 4,
            "transparency_level": 4
        }
        resp = session.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        assert resp.status_code == 200
        
        # Submit changes for Partner B (different from A)
        changes_data = {
            "session_id": session_b_id,
            "categories": ["schedule_changes", "social_behavior"]
        }
        resp = session.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        assert resp.status_code == 200
        
        # Submit timeline for Partner B
        timeline_data = {
            "session_id": session_b_id,
            "when_started": "less than 1 month ago",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": False
        }
        resp = session.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        assert resp.status_code == 200
        
        # Answer 5 core questions for Partner B
        for i in range(5):
            resp = session.get(f"{BASE_URL}/api/analysis/{session_b_id}/question")
            assert resp.status_code == 200
            q = resp.json()
            if q.get("question_id") == "complete":
                break
            
            answer_choice = q["options"][1]  # Mild answers
            answer_data = {
                "session_id": session_b_id,
                "question_id": q["question_id"],
                "question_text": q["question_text"],
                "answer": answer_choice,
                "category": q["category"]
            }
            resp = session.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
            assert resp.status_code == 200
        
        print("Partner B analysis complete")
        
        print("\n--- Step 5: Check status - both should show as complete ---")
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/status")
        assert resp.status_code == 200
        status = resp.json()
        assert status["partner_b_joined"] == True
        print(f"Status: partner_b_joined={status['partner_b_joined']}, partner_b_complete={status['partner_b_complete']}")
        
        print("\n--- Step 6: Partner A consents ---")
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_a_id})
        assert resp.status_code == 200
        assert resp.json()["consented"] == True
        assert resp.json()["both_consented"] == False  # B hasn't consented yet
        print("Partner A consented")
        
        print("\n--- Step 7: Partner B consents ---")
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_b_id})
        assert resp.status_code == 200
        consent_resp = resp.json()
        assert consent_resp["consented"] == True
        assert consent_resp["both_consented"] == True
        assert consent_resp["report_ready"] == True
        print("Partner B consented, report is ready!")
        
        print("\n--- Step 8: Fetch dual perspective report ---")
        # Give LLM a moment to generate narrative
        time.sleep(2)
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/report")
        assert resp.status_code == 200
        report = resp.json()
        
        # Verify report structure
        assert "partner_a" in report
        assert "partner_b" in report
        assert "perception_gaps" in report
        assert "average_gap" in report
        assert "gap_level" in report
        assert "narrative" in report
        
        # Verify partner_a structure
        assert "suspicion_score" in report["partner_a"]
        assert "suspicion_label" in report["partner_a"]
        assert "signals_detected" in report["partner_a"]
        assert "dominant_pattern" in report["partner_a"]
        
        # Verify partner_b structure
        assert "suspicion_score" in report["partner_b"]
        assert "suspicion_label" in report["partner_b"]
        assert "signals_detected" in report["partner_b"]
        assert "dominant_pattern" in report["partner_b"]
        
        # Verify perception_gaps has 5 dimensions
        expected_dimensions = ["emotional_distance", "communication_quality", "trust_level", "behavioral_changes", "intimacy"]
        for dim in expected_dimensions:
            assert dim in report["perception_gaps"], f"Missing dimension: {dim}"
            gap_data = report["perception_gaps"][dim]
            assert "partner_a" in gap_data
            assert "partner_b" in gap_data
            assert "gap" in gap_data
        
        # Verify gap level
        assert report["gap_level"] in ["aligned", "moderate", "significant"]
        
        # Verify narrative exists
        assert len(report["narrative"]) > 20
        
        print(f"\n✓ FULL DUAL PERSPECTIVE REPORT GENERATED")
        print(f"  Partner A Score: {report['partner_a']['suspicion_score']} ({report['partner_a']['suspicion_label']})")
        print(f"  Partner B Score: {report['partner_b']['suspicion_score']} ({report['partner_b']['suspicion_label']})")
        print(f"  Average Gap: {report['average_gap']}%")
        print(f"  Gap Level: {report['gap_level']}")
        print(f"  Narrative: {report['narrative'][:100]}...")


# =============================================================================
# Test using pre-existing mirror session (from main agent context)
# =============================================================================
class TestPreExistingMirrorSession:
    """Test with pre-existing mirror session if available"""
    
    def test_pre_existing_mirror_report(self):
        """Use pre-existing mirror session to verify report endpoint"""
        # Pre-existing session from agent context:
        # mirror_id=0350920e-571, session_a=behavioral-intel-2, 
        # session_b=behavioral-intel-2 (both consented, report ready)
        pre_existing_mirror_id = "0350920e-571"
        
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Check status first
        resp = session.get(f"{BASE_URL}/api/mirror/{pre_existing_mirror_id}/status")
        if resp.status_code == 404:
            pytest.skip("Pre-existing mirror session not found, skipping")
        
        assert resp.status_code == 200
        status = resp.json()
        
        if not status.get("report_ready"):
            pytest.skip("Pre-existing mirror report not ready, skipping")
        
        # Fetch report
        resp = session.get(f"{BASE_URL}/api/mirror/{pre_existing_mirror_id}/report")
        assert resp.status_code == 200
        report = resp.json()
        
        assert "partner_a" in report
        assert "partner_b" in report
        assert "perception_gaps" in report
        assert "narrative" in report
        
        print(f"✓ Pre-existing mirror report retrieved successfully")
        print(f"  Partner A: {report['partner_a']['suspicion_score']}/100")
        print(f"  Partner B: {report['partner_b']['suspicion_score']}/100")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
