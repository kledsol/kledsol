"""
Test suite for TrustLens Structural Upgrade Features
Tests:
- Suspicion score calibration (5 factors: signal intensity, pattern matches, contradictions, timeline, baseline)
- Enhanced Relationship Pulse (5 questions, pulse_suspicion, recommendation)
- PDF Export (/api/reports/{id}/pdf)
- Dataset Evolution (POST /api/cases/contribute)
- Case stats with contributed cases
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSuspicionScoreCalibration:
    """Test suspicion score uses all 5 factors and proper calibration"""
    
    def test_high_risk_signals_score_70_95(self):
        """Score with phone_secrecy+emotional_distance+schedule_changes+defensive_behavior+sudden+multiple should be 70-95"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert start_resp.status_code == 200
        session_id = start_resp.json()["session_id"]
        
        # Submit baseline with low transparency/closeness to trigger baseline modifier
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "occasional",
            "emotional_closeness": 2,  # LOW - adds baseline modifier
            "transparency_level": 2    # LOW - adds baseline modifier
        }
        resp = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        assert resp.status_code == 200
        
        # Submit high-risk change categories
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance", "schedule_changes", "defensive_behavior"]
        }
        resp = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        assert resp.status_code == 200
        
        # Submit timeline with sudden + multiple_at_once
        timeline_data = {
            "session_id": session_id,
            "when_started": "2 weeks ago",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": True
        }
        resp = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        assert resp.status_code == 200
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        suspicion_score = data["suspicion_score"]
        print(f"Suspicion score with high-risk signals: {suspicion_score}")
        
        # Score should be in 70-95 range
        assert 70 <= suspicion_score <= 95, f"Expected score 70-95, got {suspicion_score}"
        print(f"✓ High-risk suspicion score {suspicion_score} is in expected range 70-95")
    
    def test_score_components_signal_intensity(self):
        """Test signal intensity component contributes to score"""
        # Create session with only high-signal changes, no timeline/baseline modifiers
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Neutral baseline
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "regular",
            "emotional_closeness": 3,
            "transparency_level": 3
        })
        
        # High-intensity signals: phone_secrecy(12) + defensive_behavior(10) + emotional_distance(10) = 32 pts signal
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["phone_secrecy", "defensive_behavior", "emotional_distance"]
        })
        
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        # Should have a meaningful score just from signal intensity
        assert data["suspicion_score"] >= 30, f"Expected score >= 30 from signal intensity, got {data['suspicion_score']}"
        print(f"✓ Signal intensity contributes to score: {data['suspicion_score']}")
    
    def test_score_components_pattern_matches(self):
        """Test pattern match count from case DB contributes to score"""
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit changes that should match cases
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance"]
        })
        
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        # Case comparison should show similar cases
        assert "case_comparison" in data
        similar_count = data["case_comparison"]["similar_case_count"]
        print(f"✓ Pattern matches from case DB: {similar_count} similar cases found")
        
        # If we have matches, score should reflect it
        if similar_count > 0:
            assert data["suspicion_score"] > 0


class TestEnhancedRelationshipPulse:
    """Test pulse endpoint with 5 fields and mini suspicion indicator"""
    
    def test_pulse_accepts_5_fields(self):
        """Test POST /api/analysis/pulse accepts all 5 fields"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=pulse")
        assert start_resp.status_code == 200
        session_id = start_resp.json()["session_id"]
        
        # Submit pulse with all 5 fields
        pulse_data = {
            "session_id": session_id,
            "emotional_connection": 2,
            "communication_quality": 2,
            "perceived_tension": 4,
            "behavioral_changes": 4,  # New field
            "trust_feeling": 2       # New field
        }
        response = requests.post(f"{BASE_URL}/api/analysis/pulse", json=pulse_data)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response contains pulse_suspicion and recommendation
        assert "pulse_suspicion" in data, "Missing pulse_suspicion in response"
        assert "recommendation" in data, "Missing recommendation in response"
        assert "stability_hearts" in data
        assert "trust_disruption_index" in data
        
        print(f"✓ Pulse accepts 5 fields, returns pulse_suspicion={data['pulse_suspicion']}")
    
    def test_low_trust_high_tension_pulse_suspicion_50_plus(self):
        """Test pulse with low trust/connection + high tension/changes returns pulse_suspicion >= 50"""
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=pulse")
        session_id = start_resp.json()["session_id"]
        
        # Low trust (1), low connection (1), high tension (5), high changes (5)
        pulse_data = {
            "session_id": session_id,
            "emotional_connection": 1,  # LOW
            "communication_quality": 1, # LOW
            "perceived_tension": 5,     # HIGH
            "behavioral_changes": 5,    # HIGH changes noticed
            "trust_feeling": 1          # LOW trust
        }
        response = requests.post(f"{BASE_URL}/api/analysis/pulse", json=pulse_data)
        assert response.status_code == 200
        data = response.json()
        
        pulse_suspicion = data["pulse_suspicion"]
        print(f"Pulse suspicion with high-strain inputs: {pulse_suspicion}")
        
        assert pulse_suspicion >= 50, f"Expected pulse_suspicion >= 50, got {pulse_suspicion}"
        print(f"✓ High-strain pulse returns pulse_suspicion={pulse_suspicion} (>= 50)")
    
    def test_high_strain_recommendation_mentions_deep_analysis(self):
        """Test high-strain pulse recommendation mentions deep analysis"""
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=pulse")
        session_id = start_resp.json()["session_id"]
        
        pulse_data = {
            "session_id": session_id,
            "emotional_connection": 1,
            "communication_quality": 1,
            "perceived_tension": 5,
            "behavioral_changes": 5,
            "trust_feeling": 1
        }
        response = requests.post(f"{BASE_URL}/api/analysis/pulse", json=pulse_data)
        data = response.json()
        
        recommendation = data["recommendation"].lower()
        assert "deep analysis" in recommendation, f"Expected 'deep analysis' in recommendation, got: {data['recommendation']}"
        print(f"✓ High-strain recommendation: {data['recommendation'][:80]}...")
    
    def test_healthy_pulse_returns_low_suspicion(self):
        """Test healthy pulse inputs return low pulse_suspicion"""
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=pulse")
        session_id = start_resp.json()["session_id"]
        
        # High connection, high communication, low tension, no changes, high trust
        pulse_data = {
            "session_id": session_id,
            "emotional_connection": 5,
            "communication_quality": 5,
            "perceived_tension": 1,
            "behavioral_changes": 1,
            "trust_feeling": 5
        }
        response = requests.post(f"{BASE_URL}/api/analysis/pulse", json=pulse_data)
        data = response.json()
        
        pulse_suspicion = data["pulse_suspicion"]
        assert pulse_suspicion < 25, f"Expected pulse_suspicion < 25 for healthy inputs, got {pulse_suspicion}"
        print(f"✓ Healthy pulse returns low pulse_suspicion={pulse_suspicion}")


class TestPDFExport:
    """Test PDF export endpoint"""
    
    def test_pdf_export_returns_200_with_pdf(self):
        """Test GET /api/reports/{id}/pdf returns 200 with content-type application/pdf"""
        # First create a shared report
        report_data = {
            "suspicion_score": 65,
            "suspicion_label": "Moderate Signal",
            "pattern_comparison_pct": 45,
            "pattern_statistics": {
                "confirmed_issues": 30,
                "relationship_conflict": 35,
                "resolved_positively": 35
            },
            "perception_consistency": {
                "has_inconsistencies": False,
                "inconsistencies": [],
                "insight": "Your description shows internal consistency."
            },
            "clarity_actions": ["Have an open conversation", "Consider counseling"],
            "dominant_pattern": "Communication Breakdown",
            "trustlens_perspective": "Your relationship shows some signs of strain."
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/reports/share", json=report_data)
        assert create_resp.status_code == 200
        report_id = create_resp.json()["report_id"]
        print(f"Created shared report: {report_id}")
        
        # Now request PDF
        pdf_resp = requests.get(f"{BASE_URL}/api/reports/{report_id}/pdf")
        
        assert pdf_resp.status_code == 200, f"Expected 200, got {pdf_resp.status_code}"
        assert "application/pdf" in pdf_resp.headers.get("content-type", ""), \
            f"Expected application/pdf, got {pdf_resp.headers.get('content-type')}"
        
        # Verify it's actually PDF content (starts with %PDF)
        assert pdf_resp.content[:4] == b'%PDF', "Response does not appear to be PDF"
        
        print(f"✓ PDF export returns 200 with application/pdf content-type")
    
    def test_pdf_export_404_for_nonexistent_report(self):
        """Test PDF export returns 404 for non-existent report"""
        response = requests.get(f"{BASE_URL}/api/reports/nonexistent123/pdf")
        assert response.status_code == 404
        print("✓ PDF export returns 404 for non-existent report")


class TestCaseContribution:
    """Test dataset evolution endpoint POST /api/cases/contribute"""
    
    def test_contribute_case_success(self):
        """Test POST /api/cases/contribute accepts valid case and returns TL-U case_id"""
        case_data = {
            "primary_signals": ["phone_secrecy", "emotional_distance"],
            "outcome": "confirmed_infidelity",
            "relationship_type": "married",
            "relationship_duration": "5+ years",
            "timeline": "3 months"
        }
        
        response = requests.post(f"{BASE_URL}/api/cases/contribute", json=case_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["status"] == "accepted"
        assert "case_id" in data
        assert data["case_id"].startswith("TL-U"), f"Expected case_id starting with TL-U, got {data['case_id']}"
        
        print(f"✓ Case contribution accepted with case_id={data['case_id']}")
    
    def test_contribute_case_invalid_outcome_400(self):
        """Test POST /api/cases/contribute rejects invalid outcome with 400"""
        case_data = {
            "primary_signals": ["phone_secrecy"],
            "outcome": "invalid_outcome_type"  # Invalid
        }
        
        response = requests.post(f"{BASE_URL}/api/cases/contribute", json=case_data)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        print("✓ Invalid outcome rejected with 400")
    
    def test_contribute_case_missing_required_fields_400(self):
        """Test POST /api/cases/contribute rejects missing required fields"""
        # Missing primary_signals
        response = requests.post(f"{BASE_URL}/api/cases/contribute", json={"outcome": "misunderstanding"})
        assert response.status_code == 400
        
        # Missing outcome
        response = requests.post(f"{BASE_URL}/api/cases/contribute", json={"primary_signals": ["phone_secrecy"]})
        assert response.status_code == 400
        
        print("✓ Missing required fields rejected with 400")
    
    def test_contribute_case_all_valid_outcomes(self):
        """Test all 5 valid outcomes are accepted"""
        valid_outcomes = ["confirmed_infidelity", "emotional_disengagement", "misunderstanding", "personal_crisis", "unresolved_conflict"]
        
        for outcome in valid_outcomes:
            case_data = {
                "primary_signals": ["communication_decline"],
                "outcome": outcome
            }
            response = requests.post(f"{BASE_URL}/api/cases/contribute", json=case_data)
            assert response.status_code == 200, f"Outcome '{outcome}' should be accepted, got {response.status_code}"
        
        print(f"✓ All 5 valid outcomes accepted")


class TestCaseStatsWithContributions:
    """Test case stats includes contributed cases"""
    
    def test_case_stats_shows_301_plus_cases(self):
        """Test GET /api/cases/stats shows 301+ cases after contribution"""
        # First contribute a case to ensure > 300
        case_data = {
            "primary_signals": ["test_signal"],
            "outcome": "misunderstanding"
        }
        requests.post(f"{BASE_URL}/api/cases/contribute", json=case_data)
        
        # Get stats
        response = requests.get(f"{BASE_URL}/api/cases/stats")
        assert response.status_code == 200
        data = response.json()
        
        total_cases = data["total_cases"]
        print(f"Total cases in database: {total_cases}")
        
        # Should be > 300 (300 seeded + contributed)
        assert total_cases >= 300, f"Expected at least 300 cases, got {total_cases}"
        print(f"✓ Case stats shows {total_cases} cases (>= 300)")
    
    def test_case_stats_outcome_distribution(self):
        """Test case stats returns outcome distribution"""
        response = requests.get(f"{BASE_URL}/api/cases/stats")
        data = response.json()
        
        assert "outcome_distribution" in data
        outcomes = data["outcome_distribution"]
        
        # Should have all 5 outcome types
        expected_outcomes = ["confirmed_infidelity", "emotional_disengagement", "misunderstanding", "personal_crisis", "unresolved_conflict"]
        for outcome in expected_outcomes:
            assert outcome in outcomes, f"Missing outcome: {outcome}"
        
        print(f"✓ Outcome distribution: {outcomes}")


class TestResultsCaseComparisonInsights:
    """Test results endpoint case_comparison.insights contain dynamic text"""
    
    def test_case_comparison_insights_dynamic(self):
        """Test case_comparison.insights contain dynamic text from case matching"""
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit changes that should match many cases
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance", "defensive_behavior"]
        })
        
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        case_comparison = data["case_comparison"]
        insights = case_comparison["insights"]
        
        print(f"Case comparison insights: {insights}")
        
        # If there are similar cases, insights should contain dynamic text
        if case_comparison["similar_case_count"] > 0:
            assert len(insights) > 0, "Expected insights when similar cases found"
            # Check for dynamic content patterns
            insight_text = " ".join(insights).lower()
            assert any(word in insight_text for word in ["pattern", "case", "similar", "situation"]), \
                "Insights should contain dynamic matching text"
            print(f"✓ Insights contain dynamic text from {case_comparison['similar_case_count']} similar cases")
        else:
            print("✓ No similar cases found (empty insights expected)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
