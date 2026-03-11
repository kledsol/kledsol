"""
Test suite for TrustLens New Features (Iteration 4)
Tests: 
- Perception consistency detection
- Pattern comparison percentage
- Timeline history endpoints (GET/POST)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPerceptionConsistency:
    """Tests for detect_perception_inconsistencies functionality"""
    
    def test_perception_consistency_in_results(self):
        """Test results endpoint returns perception_consistency object"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert start_resp.status_code == 200
        session_id = start_resp.json()["session_id"]
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        # Validate perception_consistency structure
        assert "perception_consistency" in data
        pc = data["perception_consistency"]
        assert "has_inconsistencies" in pc
        assert "inconsistencies" in pc
        assert "insight" in pc
        assert isinstance(pc["has_inconsistencies"], bool)
        assert isinstance(pc["inconsistencies"], list)
        assert isinstance(pc["insight"], str)
        
        print(f"✓ perception_consistency object present with has_inconsistencies={pc['has_inconsistencies']}")
    
    def test_high_satisfaction_many_changes_inconsistency(self):
        """Test: High satisfaction (4+) + many changes (4+) triggers inconsistency"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit baseline with high satisfaction (4)
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 4,  # HIGH
            "communication_habits": "Regular",
            "emotional_closeness": 3,
            "transparency_level": 3
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit 4+ changes
        changes_data = {
            "session_id": session_id,
            "categories": ["communication", "emotional_distance", "phone_secrecy", "schedule_changes"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        pc = data["perception_consistency"]
        assert pc["has_inconsistencies"] == True
        assert any("high prior satisfaction" in inc.lower() or "multiple categories" in inc.lower() 
                   for inc in pc["inconsistencies"])
        
        print(f"✓ High satisfaction + many changes detected: {pc['inconsistencies']}")
    
    def test_high_transparency_phone_secrecy_inconsistency(self):
        """Test: High transparency (4+) + phone_secrecy change triggers inconsistency"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit baseline with high transparency (4)
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "Regular",
            "emotional_closeness": 3,
            "transparency_level": 4  # HIGH
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit phone_secrecy as change
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        pc = data["perception_consistency"]
        assert pc["has_inconsistencies"] == True
        assert any("transparency" in inc.lower() and "phone" in inc.lower() 
                   for inc in pc["inconsistencies"])
        
        print(f"✓ High transparency + phone secrecy detected: {pc['inconsistencies']}")
    
    def test_high_closeness_emotional_distance_inconsistency(self):
        """Test: High closeness (4+) + emotional_distance change triggers inconsistency"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit baseline with high closeness (4)
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,
            "communication_habits": "Regular",
            "emotional_closeness": 4,  # HIGH
            "transparency_level": 3
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit emotional_distance as change
        changes_data = {
            "session_id": session_id,
            "categories": ["emotional_distance"]
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        pc = data["perception_consistency"]
        assert pc["has_inconsistencies"] == True
        assert any("closeness" in inc.lower() and "emotional distance" in inc.lower() 
                   for inc in pc["inconsistencies"])
        
        print(f"✓ High closeness + emotional distance detected: {pc['inconsistencies']}")
    
    def test_no_inconsistencies_consistent_answers(self):
        """Test: Consistent answers return has_inconsistencies=False"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Submit baseline with moderate levels (no triggers)
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 3,  # Not high (not >=4)
            "communication_habits": "occasional",  # Not 'daily' or 'frequent'
            "emotional_closeness": 3,  # Not high
            "transparency_level": 3   # Not high
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        
        # Submit few changes (not triggering satisfaction+many changes rule)
        changes_data = {
            "session_id": session_id,
            "categories": ["schedule_changes"]  # Not phone_secrecy or emotional_distance
        }
        requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        
        # Submit timeline with consistent choices
        timeline_data = {
            "session_id": session_id,
            "when_started": "1 week ago",
            "gradual_or_sudden": "sudden",  # If gradual with multiple_at_once would be inconsistent
            "multiple_at_once": False
        }
        requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        pc = data["perception_consistency"]
        # Should be consistent (no inconsistencies)
        assert pc["has_inconsistencies"] == False
        assert len(pc["inconsistencies"]) == 0
        assert "consistency" in pc["insight"].lower()
        
        print(f"✓ Consistent answers detected correctly")


class TestPatternComparisonPct:
    """Tests for pattern_comparison_pct field"""
    
    def test_pattern_comparison_pct_in_results(self):
        """Test results endpoint returns pattern_comparison_pct number between 12-62"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        assert response.status_code == 200
        data = response.json()
        
        # Validate pattern_comparison_pct exists and is in range
        assert "pattern_comparison_pct" in data
        pct = data["pattern_comparison_pct"]
        assert isinstance(pct, int)
        assert 12 <= pct <= 62, f"Expected pattern_comparison_pct between 12-62, got {pct}"
        
        print(f"✓ pattern_comparison_pct={pct} (in range 12-62)")
    
    def test_pattern_comparison_increases_with_score(self):
        """Test pattern_comparison_pct increases with suspicion score"""
        # Session 1: Low risk
        start1 = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        sid1 = start1.json()["session_id"]
        
        # Minimal data for low score
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": sid1,
            "relationship_duration": "3+ years",
            "prior_satisfaction": 5,
            "communication_habits": "daily",
            "emotional_closeness": 5,
            "transparency_level": 5
        })
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": sid1,
            "categories": []
        })
        
        r1 = requests.get(f"{BASE_URL}/api/analysis/{sid1}/results")
        low_data = r1.json()
        
        # Session 2: High risk
        start2 = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        sid2 = start2.json()["session_id"]
        
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": sid2,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 2,
            "communication_habits": "minimal",
            "emotional_closeness": 2,
            "transparency_level": 2
        })
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": sid2,
            "categories": ["phone_secrecy", "emotional_distance", "defensive_behavior", "schedule_changes"]
        })
        requests.post(f"{BASE_URL}/api/analysis/timeline", json={
            "session_id": sid2,
            "when_started": "1 week ago",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": True
        })
        
        r2 = requests.get(f"{BASE_URL}/api/analysis/{sid2}/results")
        high_data = r2.json()
        
        # High-risk should have higher pattern_comparison_pct
        assert high_data["pattern_comparison_pct"] >= low_data["pattern_comparison_pct"]
        
        print(f"✓ Low score ({low_data['suspicion_score']}) -> pct={low_data['pattern_comparison_pct']}")
        print(f"✓ High score ({high_data['suspicion_score']}) -> pct={high_data['pattern_comparison_pct']}")


class TestTimelineHistory:
    """Tests for timeline-history endpoints (GET/POST)"""
    
    def test_get_timeline_history_returns_entries(self):
        """Test GET /api/timeline-history returns entries array"""
        response = requests.get(f"{BASE_URL}/api/timeline-history")
        assert response.status_code == 200
        data = response.json()
        
        assert "entries" in data
        assert isinstance(data["entries"], list)
        
        print(f"✓ GET /api/timeline-history returns {len(data['entries'])} entries")
    
    def test_post_timeline_history_saves_entry(self):
        """Test POST /api/timeline-history saves a score entry"""
        # Get initial count
        initial_resp = requests.get(f"{BASE_URL}/api/timeline-history")
        initial_count = len(initial_resp.json()["entries"])
        
        # POST new entry
        test_score = 42
        test_label = "Test Signal"
        post_resp = requests.post(f"{BASE_URL}/api/timeline-history", json={
            "score": test_score,
            "label": test_label
        })
        assert post_resp.status_code == 200
        assert post_resp.json().get("status") == "saved"
        
        # Verify entry was saved
        verify_resp = requests.get(f"{BASE_URL}/api/timeline-history")
        entries = verify_resp.json()["entries"]
        
        assert len(entries) > initial_count
        
        # Find our entry (should be the last one)
        latest = entries[-1]
        assert latest["score"] == test_score
        assert latest["label"] == test_label
        assert "created_at" in latest
        assert "date_display" in latest
        
        print(f"✓ POST /api/timeline-history saved entry with score={test_score}")
    
    def test_timeline_history_entry_structure(self):
        """Test timeline entry has required fields"""
        # POST an entry
        requests.post(f"{BASE_URL}/api/timeline-history", json={
            "score": 55,
            "label": "Moderate Signal"
        })
        
        # GET and verify structure
        response = requests.get(f"{BASE_URL}/api/timeline-history")
        entries = response.json()["entries"]
        
        assert len(entries) > 0
        entry = entries[-1]
        
        required_fields = ["score", "label", "created_at", "date_display"]
        for field in required_fields:
            assert field in entry, f"Missing field: {field}"
        
        print(f"✓ Timeline entry has all required fields: {required_fields}")
    
    def test_timeline_history_max_50_entries(self):
        """Test GET /api/timeline-history returns max 50 entries"""
        response = requests.get(f"{BASE_URL}/api/timeline-history")
        entries = response.json()["entries"]
        
        assert len(entries) <= 50
        
        print(f"✓ Timeline history respects limit (entries={len(entries)})")


class TestResultsAllNewFields:
    """Test results endpoint contains all new fields"""
    
    def test_results_has_all_new_fields(self):
        """Verify results endpoint includes perception_consistency and pattern_comparison_pct"""
        # Create session
        start_resp = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = start_resp.json()["session_id"]
        
        # Get results
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/results")
        data = response.json()
        
        # Verify new fields
        assert "perception_consistency" in data
        assert "pattern_comparison_pct" in data
        
        # Verify perception_consistency structure
        pc = data["perception_consistency"]
        assert "has_inconsistencies" in pc
        assert "inconsistencies" in pc
        assert "insight" in pc
        
        print("✓ Results endpoint contains all new fields")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
