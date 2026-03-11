"""
Test Signal Strength Summary Feature
- Tests GET /api/analysis/{session_id}/results endpoint for signal_strength_summary field
- Validates signal categorization (strong >= 0.55, moderate 0.25-0.55, weak < 0.25)
- Validates each signal has required fields: key, name, desc, intensity, strength, explanation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Pre-existing session with full analysis data
TEST_SESSION_ID = "74389d33-3604-422f-af6f-9240b5df74fe"


class TestSignalStrengthSummaryBackend:
    """Backend tests for Signal Strength Summary feature"""

    def test_results_endpoint_includes_signal_strength_summary(self):
        """Test that GET /api/analysis/{session_id}/results includes signal_strength_summary field"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "signal_strength_summary" in data, "Response should include signal_strength_summary field"
        
    def test_signal_strength_summary_structure(self):
        """Test that signal_strength_summary contains strong, moderate, weak arrays and total_signals"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        ss = data.get("signal_strength_summary", {})
        
        # Check required keys
        assert "strong" in ss, "signal_strength_summary should have 'strong' array"
        assert "moderate" in ss, "signal_strength_summary should have 'moderate' array"
        assert "weak" in ss, "signal_strength_summary should have 'weak' array"
        assert "total_signals" in ss, "signal_strength_summary should have 'total_signals' count"
        
        # Check types
        assert isinstance(ss["strong"], list), "'strong' should be a list"
        assert isinstance(ss["moderate"], list), "'moderate' should be a list"
        assert isinstance(ss["weak"], list), "'weak' should be a list"
        assert isinstance(ss["total_signals"], int), "'total_signals' should be an int"
        
    def test_signal_item_fields(self):
        """Test that each signal item has required fields: key, name, desc, intensity, strength, explanation"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        ss = data.get("signal_strength_summary", {})
        
        required_fields = ["key", "name", "desc", "intensity", "strength", "explanation"]
        
        all_signals = ss.get("strong", []) + ss.get("moderate", []) + ss.get("weak", [])
        assert len(all_signals) > 0, "Should have at least one signal"
        
        for signal in all_signals:
            for field in required_fields:
                assert field in signal, f"Signal '{signal.get('key', 'unknown')}' missing field '{field}'"
                
            # Validate intensity is a float between 0 and 1
            assert isinstance(signal["intensity"], (int, float)), f"Intensity should be numeric for {signal['key']}"
            assert 0 <= signal["intensity"] <= 1, f"Intensity should be 0-1, got {signal['intensity']} for {signal['key']}"
            
    def test_strong_signals_categorization(self):
        """Test that strong signals have intensity >= 0.55"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        strong_signals = data.get("signal_strength_summary", {}).get("strong", [])
        
        for signal in strong_signals:
            assert signal["intensity"] >= 0.55, f"Strong signal '{signal['key']}' has intensity {signal['intensity']} < 0.55"
            assert signal["strength"] == "strong", f"Strong signal '{signal['key']}' has wrong strength label"
            
    def test_moderate_signals_categorization(self):
        """Test that moderate signals have intensity between 0.25 and 0.55"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        moderate_signals = data.get("signal_strength_summary", {}).get("moderate", [])
        
        for signal in moderate_signals:
            assert 0.25 <= signal["intensity"] < 0.55, f"Moderate signal '{signal['key']}' has intensity {signal['intensity']} outside 0.25-0.55 range"
            assert signal["strength"] == "moderate", f"Moderate signal '{signal['key']}' has wrong strength label"
            
    def test_weak_signals_categorization(self):
        """Test that weak signals have intensity < 0.25"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        weak_signals = data.get("signal_strength_summary", {}).get("weak", [])
        
        for signal in weak_signals:
            assert signal["intensity"] < 0.25, f"Weak signal '{signal['key']}' has intensity {signal['intensity']} >= 0.25"
            assert signal["strength"] == "weak", f"Weak signal '{signal['key']}' has wrong strength label"
            
    def test_total_signals_count_matches(self):
        """Test that total_signals equals sum of strong + moderate + weak"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        ss = data.get("signal_strength_summary", {})
        
        total = len(ss.get("strong", [])) + len(ss.get("moderate", [])) + len(ss.get("weak", []))
        assert ss.get("total_signals") == total, f"total_signals {ss.get('total_signals')} != sum of arrays {total}"
        
    def test_signal_descriptions_are_non_accusatory(self):
        """Test that signal descriptions don't accuse the partner - should describe patterns/observations"""
        response = requests.get(f"{BASE_URL}/api/analysis/{TEST_SESSION_ID}/results")
        assert response.status_code == 200
        
        data = response.json()
        ss = data.get("signal_strength_summary", {})
        
        accusatory_phrases = ["cheating", "infidelity", "affair", "lying", "deceiving", "guilty"]
        pattern_phrases = ["observed", "detected", "noted", "identified", "reflected", "patterns"]
        
        all_signals = ss.get("strong", []) + ss.get("moderate", []) + ss.get("weak", [])
        
        for signal in all_signals:
            desc = signal.get("desc", "").lower()
            
            # Should NOT contain accusatory language
            for phrase in accusatory_phrases:
                assert phrase not in desc, f"Signal '{signal['key']}' description contains accusatory phrase '{phrase}'"
                
            # Should contain pattern-based language
            has_pattern_language = any(phrase in desc for phrase in pattern_phrases)
            assert has_pattern_language, f"Signal '{signal['key']}' description should use pattern-based language"
            
    def test_signal_strength_for_session_without_data(self):
        """Test signal strength summary for a new session without analysis data"""
        # Create new session
        create_response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=pulse")
        assert create_response.status_code == 200
        
        new_session_id = create_response.json().get("session_id")
        
        # Get results for new session (should have empty or minimal signals)
        results_response = requests.get(f"{BASE_URL}/api/analysis/{new_session_id}/results")
        assert results_response.status_code == 200
        
        data = results_response.json()
        assert "signal_strength_summary" in data
        
        ss = data.get("signal_strength_summary", {})
        # New session should have empty arrays or zero total
        assert ss.get("total_signals", 0) >= 0  # Can be 0 for new session
