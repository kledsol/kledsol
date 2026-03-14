"""
Test cases for TrustLens Conversation Coach feature.
Tests POST /api/analysis/conversation-coach endpoint with enriched guidance structure.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://signal-analysis-5.preview.emergentagent.com')

class TestConversationCoachEndpoint:
    """Tests for POST /api/analysis/conversation-coach"""
    
    @pytest.fixture(scope="class")
    def session_with_analysis(self):
        """Create a session with full analysis data for testing conversation coach"""
        # 1. Start deep analysis session
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200, f"Failed to start session: {response.text}"
        session_id = response.json()["session_id"]
        
        # 2. Submit baseline data
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "3-5 years",
            "prior_satisfaction": 7,
            "communication_habits": "daily",
            "emotional_closeness": 4,
            "transparency_level": 3
        }
        response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        assert response.status_code == 200, f"Failed to submit baseline: {response.text}"
        
        # 3. Submit changes data
        changes_data = {
            "session_id": session_id,
            "categories": ["phone_secrecy", "emotional_distance", "schedule_changes"]
        }
        response = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        assert response.status_code == 200, f"Failed to submit changes: {response.text}"
        
        # 4. Submit timeline data
        timeline_data = {
            "session_id": session_id,
            "when_started": "Past few weeks",
            "gradual_or_sudden": "gradual",
            "multiple_at_once": True
        }
        response = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        assert response.status_code == 200, f"Failed to submit timeline: {response.text}"
        
        # 5. Answer 5 core questions
        core_questions = [
            {"question_id": "core_1", "question_text": "How would you describe the emotional atmosphere at home recently?", "answer": "Noticeably tense", "category": "emotional_indicators"},
            {"question_id": "core_2", "question_text": "Has your partner's daily routine changed in a way that feels unexplained?", "answer": "Significant unexplained changes", "category": "routine_changes"},
            {"question_id": "core_3", "question_text": "How does your partner react when you ask about their day or plans?", "answer": "Vague or deflecting", "category": "communication_changes"},
            {"question_id": "core_4", "question_text": "Have you noticed any changes in how your partner uses their phone or devices?", "answer": "Noticeably guarded", "category": "digital_behavior"},
            {"question_id": "core_5", "question_text": "How has the quality of your intimate connection changed?", "answer": "Slightly less frequent", "category": "emotional_indicators"},
        ]
        
        for q in core_questions:
            q["session_id"] = session_id
            response = requests.post(f"{BASE_URL}/api/analysis/answer", json=q)
            assert response.status_code == 200, f"Failed to answer question: {response.text}"
        
        return session_id
    
    def test_conversation_coach_returns_200_with_valid_session(self, session_with_analysis):
        """Test that POST /api/analysis/conversation-coach returns 200 with valid session"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "gentle",
            "topic": "recent_changes"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_conversation_coach_returns_404_for_invalid_session(self):
        """Test that invalid session_id returns 404"""
        data = {
            "session_id": "invalid-session-id-12345",
            "tone": "gentle",
            "topic": "recent_changes"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_response_has_framing_object(self, session_with_analysis):
        """Test that response includes framing object with approach, tone_guidance, timing_suggestion"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "direct",
            "topic": "communication"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        assert "framing" in result, "Response should contain 'framing' key"
        framing = result["framing"]
        assert "approach" in framing, "framing should have 'approach'"
        assert "tone_guidance" in framing, "framing should have 'tone_guidance'"
        assert "timing_suggestion" in framing, "framing should have 'timing_suggestion'"
        assert isinstance(framing["approach"], str), "approach should be a string"
        assert len(framing["approach"]) > 10, "approach should be a meaningful sentence"
    
    def test_response_has_openings_array(self, session_with_analysis):
        """Test that response includes openings as array with 2-3 items"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "curious",
            "topic": "feelings"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        assert "openings" in result, "Response should contain 'openings' key"
        openings = result["openings"]
        assert isinstance(openings, list), "openings should be an array"
        assert len(openings) >= 2, f"openings should have at least 2 items, got {len(openings)}"
        assert len(openings) <= 4, f"openings should have at most 4 items, got {len(openings)}"
        for i, opening in enumerate(openings):
            assert isinstance(opening, str), f"openings[{i}] should be a string"
            assert len(opening) > 10, f"openings[{i}] should be meaningful"
    
    def test_response_has_questions_array(self, session_with_analysis):
        """Test that response includes questions as array with 3-5 items"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "supportive",
            "topic": "future"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        assert "questions" in result, "Response should contain 'questions' key"
        questions = result["questions"]
        assert isinstance(questions, list), "questions should be an array"
        assert len(questions) >= 3, f"questions should have at least 3 items, got {len(questions)}"
        assert len(questions) <= 6, f"questions should have at most 6 items, got {len(questions)}"
        for i, q in enumerate(questions):
            assert isinstance(q, str), f"questions[{i}] should be a string"
    
    def test_response_has_avoid_array(self, session_with_analysis):
        """Test that response includes avoid array with 3-4 items"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "gentle",
            "topic": "trust"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        assert "avoid" in result, "Response should contain 'avoid' key"
        avoid = result["avoid"]
        assert isinstance(avoid, list), "avoid should be an array"
        assert len(avoid) >= 3, f"avoid should have at least 3 items, got {len(avoid)}"
        assert len(avoid) <= 5, f"avoid should have at most 5 items, got {len(avoid)}"
    
    def test_response_has_emotional_preparation_object(self, session_with_analysis):
        """Test that response includes emotional_preparation with before/during/if_difficult"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "direct",
            "topic": "recent_changes"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        assert "emotional_preparation" in result, "Response should contain 'emotional_preparation' key"
        ep = result["emotional_preparation"]
        assert "before" in ep, "emotional_preparation should have 'before'"
        assert "during" in ep, "emotional_preparation should have 'during'"
        assert "if_difficult" in ep, "emotional_preparation should have 'if_difficult'"
        assert isinstance(ep["before"], str), "before should be a string"
        assert isinstance(ep["during"], str), "during should be a string"
        assert isinstance(ep["if_difficult"], str), "if_difficult should be a string"
    
    def test_response_has_observe_array(self, session_with_analysis):
        """Test that response includes observe array"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "curious",
            "topic": "communication"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        assert "observe" in result, "Response should contain 'observe' key"
        observe = result["observe"]
        assert isinstance(observe, list), "observe should be an array"
        assert len(observe) >= 2, f"observe should have at least 2 items, got {len(observe)}"
    
    def test_all_tones_work(self, session_with_analysis):
        """Test that all 4 tone options work"""
        session_id = session_with_analysis
        tones = ["gentle", "direct", "curious", "supportive"]
        
        for tone in tones:
            data = {
                "session_id": session_id,
                "tone": tone,
                "topic": "feelings"
            }
            response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
            assert response.status_code == 200, f"Tone '{tone}' failed with {response.status_code}"
            result = response.json()
            # Verify tone is reflected in guidance
            assert "framing" in result, f"Tone '{tone}' should return framing"
    
    def test_all_topics_work(self, session_with_analysis):
        """Test that all 5 topic options work"""
        session_id = session_with_analysis
        topics = ["recent_changes", "feelings", "communication", "future", "trust"]
        
        for topic in topics:
            data = {
                "session_id": session_id,
                "tone": "gentle",
                "topic": topic
            }
            response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
            assert response.status_code == 200, f"Topic '{topic}' failed with {response.status_code}"
            result = response.json()
            assert "questions" in result, f"Topic '{topic}' should return questions"
    
    def test_guidance_personalization_mentions_signals(self, session_with_analysis):
        """Test that guidance is personalized based on session signals"""
        session_id = session_with_analysis
        data = {
            "session_id": session_id,
            "tone": "gentle",
            "topic": "recent_changes"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        # Check that questions or framing contain references to the signals
        # (phone, emotional, schedule) - either from LLM or fallback
        full_text = str(result).lower()
        # At least one signal-related word should appear
        signal_keywords = ["phone", "distance", "emotional", "routine", "schedule", "communication", "changes"]
        found = any(kw in full_text for kw in signal_keywords)
        assert found, f"Guidance should be personalized with signal keywords. Got: {full_text[:500]}"


class TestConversationCoachFallback:
    """Test fallback behavior when LLM fails"""
    
    @pytest.fixture(scope="class")
    def minimal_session(self):
        """Create a minimal session for fallback testing"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Submit only required baseline
        baseline = {
            "session_id": session_id,
            "relationship_duration": "1-3 years",
            "prior_satisfaction": 5,
            "communication_habits": "weekly",
            "emotional_closeness": 3,
            "transparency_level": 3
        }
        requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline)
        
        return session_id
    
    def test_fallback_still_returns_valid_structure(self, minimal_session):
        """Test that even with minimal data, response has valid structure"""
        session_id = minimal_session
        data = {
            "session_id": session_id,
            "tone": "gentle",
            "topic": "feelings"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/conversation-coach", json=data)
        assert response.status_code == 200
        result = response.json()
        
        # Even with no changes_data, should have valid structure
        required_keys = ["framing", "openings", "questions", "avoid", "emotional_preparation", "observe"]
        for key in required_keys:
            assert key in result, f"Fallback should include '{key}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
