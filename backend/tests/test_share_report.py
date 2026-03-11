"""
Test suite for TrustLens Share Anonymized Report Feature
Tests:
- POST /api/reports/share - Create anonymized shareable report
- GET /api/reports/{report_id} - Retrieve stored report
- Validates report contains only anonymized data (no personal info)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCreateSharedReport:
    """Tests for POST /api/reports/share endpoint"""
    
    def test_create_shared_report_returns_report_id(self):
        """Test POST /api/reports/share creates a report and returns report_id"""
        report_data = {
            "suspicion_score": 45,
            "suspicion_label": "Moderate Signal",
            "pattern_comparison_pct": 32,
            "pattern_statistics": {
                "confirmed_issues": 42,
                "relationship_conflict": 35,
                "resolved_positively": 23
            },
            "perception_consistency": {
                "has_inconsistencies": True,
                "inconsistencies": ["Test inconsistency"],
                "insight": "Test insight"
            },
            "clarity_actions": [
                "Have an open conversation",
                "Discuss communication patterns",
                "Consider counseling"
            ],
            "dominant_pattern": "Communication Breakdown",
            "trustlens_perspective": "Your relationship shows some signs of strain."
        }
        
        response = requests.post(f"{BASE_URL}/api/reports/share", json=report_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "report_id" in data
        assert len(data["report_id"]) == 12  # UUID[:12]
        
        print(f"✓ Created shared report with ID: {data['report_id']}")
    
    def test_create_shared_report_with_minimal_data(self):
        """Test report creation works with minimal data"""
        report_data = {
            "suspicion_score": 20,
            "suspicion_label": "Low Signal"
        }
        
        response = requests.post(f"{BASE_URL}/api/reports/share", json=report_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "report_id" in data
        print(f"✓ Created minimal report with ID: {data['report_id']}")
    
    def test_create_shared_report_with_empty_body(self):
        """Test report creation works with empty body (defaults applied)"""
        response = requests.post(f"{BASE_URL}/api/reports/share", json={})
        assert response.status_code == 200
        data = response.json()
        
        assert "report_id" in data
        print(f"✓ Created empty report with ID: {data['report_id']}")


class TestGetSharedReport:
    """Tests for GET /api/reports/{report_id} endpoint"""
    
    def test_get_shared_report_returns_stored_data(self):
        """Test GET /api/reports/{report_id} returns the stored report data"""
        # Create a report first
        original_data = {
            "suspicion_score": 65,
            "suspicion_label": "Elevated Pattern Risk",
            "pattern_comparison_pct": 45,
            "pattern_statistics": {
                "confirmed_issues": 50,
                "relationship_conflict": 30,
                "resolved_positively": 20
            },
            "perception_consistency": {
                "has_inconsistencies": False,
                "inconsistencies": [],
                "insight": "Your description shows consistency."
            },
            "clarity_actions": [
                "Action 1",
                "Action 2",
                "Action 3",
                "Action 4"
            ],
            "dominant_pattern": "Trust Erosion",
            "trustlens_perspective": "Significant changes detected."
        }
        
        create_response = requests.post(f"{BASE_URL}/api/reports/share", json=original_data)
        report_id = create_response.json()["report_id"]
        
        # GET the report
        get_response = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        assert get_response.status_code == 200
        report = get_response.json()
        
        # Verify stored data matches
        assert report["suspicion_score"] == 65
        assert report["suspicion_label"] == "Elevated Pattern Risk"
        assert report["pattern_comparison_pct"] == 45
        assert report["pattern_statistics"] == original_data["pattern_statistics"]
        assert report["perception_consistency"] == original_data["perception_consistency"]
        assert report["dominant_pattern"] == "Trust Erosion"
        assert report["trustlens_perspective"] == "Significant changes detected."
        assert len(report["clarity_actions"]) == 4  # Max 4 actions stored
        
        print(f"✓ Retrieved report {report_id} with correct data")
    
    def test_get_invalid_report_returns_404(self):
        """Test GET /api/reports/invalid-id returns 404"""
        response = requests.get(f"{BASE_URL}/api/reports/invalid-id-123")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        
        print("✓ Invalid report ID returns 404")
    
    def test_get_nonexistent_report_returns_404(self):
        """Test GET with random UUID returns 404"""
        random_id = str(uuid.uuid4())[:12]
        response = requests.get(f"{BASE_URL}/api/reports/{random_id}")
        assert response.status_code == 404
        
        print(f"✓ Nonexistent report {random_id} returns 404")


class TestReportDataAnonymization:
    """Tests verifying shared reports contain only anonymized data"""
    
    def test_report_does_not_store_session_id(self):
        """Verify report does not include session_id field"""
        # Create report (session_id not in allowed fields)
        report_data = {
            "session_id": "should-not-be-stored",  # This should be ignored
            "suspicion_score": 30,
            "suspicion_label": "Low Signal"
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/reports/share", json=report_data)
        report_id = create_resp.json()["report_id"]
        
        # Retrieve and verify session_id is not present
        get_resp = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        report = get_resp.json()
        
        assert "session_id" not in report
        print("✓ session_id is not stored in shared report")
    
    def test_report_contains_required_anonymized_fields(self):
        """Verify report contains all required anonymized fields"""
        report_data = {
            "suspicion_score": 50,
            "suspicion_label": "Moderate Signal",
            "pattern_comparison_pct": 35,
            "pattern_statistics": {
                "confirmed_issues": 40,
                "relationship_conflict": 30,
                "resolved_positively": 30
            },
            "perception_consistency": {
                "has_inconsistencies": True,
                "inconsistencies": ["Test"],
                "insight": "Test insight"
            },
            "clarity_actions": ["Action 1", "Action 2"],
            "dominant_pattern": "Emotional Distance",
            "trustlens_perspective": "Analysis complete."
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/reports/share", json=report_data)
        report_id = create_resp.json()["report_id"]
        
        get_resp = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        report = get_resp.json()
        
        # Required fields for shared report
        required_fields = [
            "report_id",
            "created_at",
            "suspicion_score",
            "suspicion_label",
            "pattern_comparison_pct",
            "pattern_statistics",
            "perception_consistency",
            "clarity_actions",
            "dominant_pattern",
            "trustlens_perspective"
        ]
        
        for field in required_fields:
            assert field in report, f"Missing required field: {field}"
        
        print(f"✓ Report contains all required anonymized fields: {required_fields}")
    
    def test_report_limits_clarity_actions_to_four(self):
        """Verify only first 4 clarity actions are stored"""
        report_data = {
            "suspicion_score": 40,
            "suspicion_label": "Moderate Signal",
            "clarity_actions": [
                "Action 1",
                "Action 2",
                "Action 3",
                "Action 4",
                "Action 5",
                "Action 6"
            ]
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/reports/share", json=report_data)
        report_id = create_resp.json()["report_id"]
        
        get_resp = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        report = get_resp.json()
        
        assert len(report["clarity_actions"]) == 4
        assert report["clarity_actions"] == ["Action 1", "Action 2", "Action 3", "Action 4"]
        
        print("✓ clarity_actions correctly limited to first 4 items")


class TestExistingSharedReport:
    """Test the existing shared report from development"""
    
    def test_existing_report_loads(self):
        """Test the existing report mentioned in test context loads correctly"""
        # Try the known existing report
        response = requests.get(f"{BASE_URL}/api/reports/4dd0790e-642")
        
        if response.status_code == 200:
            report = response.json()
            assert "suspicion_score" in report
            assert "suspicion_label" in report
            print(f"✓ Existing report 4dd0790e-642 loads with score={report['suspicion_score']}")
        else:
            # Report may have been deleted or doesn't exist
            print(f"⚠ Existing report 4dd0790e-642 not found (status={response.status_code})")
            # This is not a failure - report may not exist


class TestReportIntegrationWithResults:
    """Tests verifying share report flow works with real results data"""
    
    def test_create_report_from_real_results(self):
        """Create a full analysis session and share its results"""
        # Create analysis session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit baseline
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "regular",
            "emotional_closeness": 3,
            "transparency_level": 3
        })
        
        # Submit changes
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["communication", "emotional_distance"]
        })
        
        # Get results
        results_resp = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        results = results_resp.json()
        
        # Create shared report from results
        share_data = {
            "suspicion_score": results["suspicion_score"],
            "suspicion_label": results["suspicion_label"],
            "pattern_comparison_pct": results["pattern_comparison_pct"],
            "pattern_statistics": results["pattern_statistics"],
            "perception_consistency": results["perception_consistency"],
            "clarity_actions": results["clarity_actions"],
            "dominant_pattern": results["dominant_pattern"],
            "trustlens_perspective": results["trustlens_perspective"]
        }
        
        share_resp = requests.post(f"{BASE_URL}/api/reports/share", json=share_data)
        assert share_resp.status_code == 200
        report_id = share_resp.json()["report_id"]
        
        # Verify we can retrieve it
        get_resp = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        assert get_resp.status_code == 200
        report = get_resp.json()
        
        # Verify the data matches
        assert report["suspicion_score"] == results["suspicion_score"]
        assert report["suspicion_label"] == results["suspicion_label"]
        
        print(f"✓ Created shared report from real analysis: {report_id}")
        print(f"  Score: {report['suspicion_score']} ({report['suspicion_label']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
