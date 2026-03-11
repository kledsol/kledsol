"""
Quick API tests for Mirror / Dual Perspective feature
Tests the mirror endpoints independently, without completing full analysis flow
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestMirrorAPIQuick:
    """Quick API tests for Mirror feature without LLM calls"""
    
    def test_create_mirror_basic(self):
        """Test basic mirror session creation"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create a minimal session
        resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]
        print(f"✓ Created session: {session_id}")
        
        # Create mirror from this session
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "mirror_id" in data
        print(f"✓ Created mirror: {data['mirror_id']}")
    
    def test_mirror_status_endpoint(self):
        """Test mirror status endpoint"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create session and mirror
        resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Check status
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/status")
        assert resp.status_code == 200
        status = resp.json()
        
        assert "mirror_id" in status
        assert "status" in status
        assert "partner_b_joined" in status
        assert "partner_a_consented" in status
        assert "partner_b_consented" in status
        assert "report_ready" in status
        assert not status["partner_b_joined"]
        assert not status["partner_a_consented"]
        assert not status["partner_b_consented"]
        print(f"✓ Status response correct: {status['status']}")
    
    def test_mirror_join_endpoint(self):
        """Test partner B join endpoint"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create session and mirror
        resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner B joins
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "session_id" in data
        assert data["mirror_id"] == mirror_id
        session_b_id = data["session_id"]
        print(f"✓ Partner B joined with session: {session_b_id}")
        
        # Partner B joins again (should return already_joined)
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        assert resp.status_code == 200
        assert resp.json()["already_joined"]
        print("✓ Already joined flag works")
    
    def test_mirror_consent_endpoint(self):
        """Test consent endpoint for both partners"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create session A and mirror
        resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_a_id = resp.json()["session_id"]
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_a_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Partner B joins
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/join")
        session_b_id = resp.json()["session_id"]
        
        # Partner A consents
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_a_id})
        assert resp.status_code == 200
        assert resp.json()["consented"]
        assert resp.json()["role"] == "a"
        assert not resp.json()["both_consented"]
        print("✓ Partner A consent recorded")
        
        # Partner B consents
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": session_b_id})
        assert resp.status_code == 200
        assert resp.json()["consented"]
        assert resp.json()["role"] == "b"
        assert resp.json()["both_consented"]
        print("✓ Partner B consent recorded, both_consented=True")
    
    def test_mirror_report_guard(self):
        """Test report endpoint returns 403 without consent"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create session and mirror
        resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Try to get report without consent
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/report")
        assert resp.status_code == 403
        print("✓ Report returns 403 without consent")
    
    def test_invalid_mirror_id_404(self):
        """Test invalid mirror_id returns 404"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        resp = session.get(f"{BASE_URL}/api/mirror/invalid-id-xyz/status")
        assert resp.status_code == 404
        
        resp = session.get(f"{BASE_URL}/api/mirror/invalid-id-xyz/join")
        assert resp.status_code == 404
        
        resp = session.get(f"{BASE_URL}/api/mirror/invalid-id-xyz/report")
        assert resp.status_code == 404
        
        print("✓ Invalid mirror_id returns 404 correctly")
    
    def test_invalid_session_consent_403(self):
        """Test consent with invalid session returns 403"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create session and mirror
        resp = session.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = resp.json()["session_id"]
        resp = session.post(f"{BASE_URL}/api/mirror/create", json={"session_id": session_id})
        mirror_id = resp.json()["mirror_id"]
        
        # Try to consent with invalid session
        resp = session.post(f"{BASE_URL}/api/mirror/{mirror_id}/consent", json={"session_id": "invalid-xyz"})
        assert resp.status_code == 403
        print("✓ Consent with invalid session returns 403")


class TestMirrorReportWithExisting:
    """Test with pre-existing mirror session from main agent context"""
    
    def test_existing_mirror_report(self):
        """Test report generation with existing mirror session"""
        # Use mirror session created during curl tests
        mirror_id = "0091ea17-7dd"
        
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Get report (both partners consented from curl tests)
        resp = session.get(f"{BASE_URL}/api/mirror/{mirror_id}/report")
        if resp.status_code == 404:
            pytest.skip("Pre-existing mirror not found")
        
        if resp.status_code == 403:
            pytest.skip("Pre-existing mirror not yet consented")
        
        assert resp.status_code == 200
        report = resp.json()
        
        # Validate report structure
        assert "mirror_id" in report
        assert "partner_a" in report
        assert "partner_b" in report
        assert "perception_gaps" in report
        assert "average_gap" in report
        assert "gap_level" in report
        assert "narrative" in report
        
        # Validate partner data
        for partner_key in ["partner_a", "partner_b"]:
            partner = report[partner_key]
            assert "suspicion_score" in partner
            assert "suspicion_label" in partner
            assert "signals_detected" in partner
            assert "dominant_pattern" in partner
        
        # Validate perception gaps dimensions
        expected_dims = ["emotional_distance", "communication_quality", "trust_level", "behavioral_changes", "intimacy"]
        for dim in expected_dims:
            assert dim in report["perception_gaps"], f"Missing dimension: {dim}"
            gap = report["perception_gaps"][dim]
            assert "partner_a" in gap
            assert "partner_b" in gap
            assert "gap" in gap
        
        # Validate gap level
        assert report["gap_level"] in ["aligned", "moderate", "significant"]
        
        # Validate narrative exists
        assert len(report["narrative"]) > 20
        
        print(f"✓ Report structure validated")
        print(f"  Partner A: {report['partner_a']['suspicion_score']}/100 ({report['partner_a']['suspicion_label']})")
        print(f"  Partner B: {report['partner_b']['suspicion_score']}/100 ({report['partner_b']['suspicion_label']})")
        print(f"  Average Gap: {report['average_gap']}%")
        print(f"  Gap Level: {report['gap_level']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
