"""
Test suite for the Hybrid Adaptive Question Engine (Stage 1: Core + Stage 2: AI Follow-ups)
Tests:
- POST /api/analysis/start creates session
- POST /api/analysis/baseline, /changes, /timeline record data
- GET /api/analysis/{session_id}/question returns core questions first (5 questions)
- After 5 core questions with concerning answers, AI follow-ups are triggered
- Max 3 follow-up questions enforced
- When all 5 core questions answered with mild answers, stage='complete' returned immediately
- POST /api/analysis/answer processes answers correctly
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Core question IDs
CORE_QUESTION_IDS = ["core_1", "core_2", "core_3", "core_4", "core_5"]

# Concerning answers (option 3 or 4) that trigger strong signals
CONCERNING_ANSWERS = {
    "core_1": "Noticeably tense",  # option 3
    "core_2": "Significant unexplained changes",  # option 3
    "core_3": "Vague or deflecting",  # option 3
    "core_4": "Noticeably guarded",  # option 3
    "core_5": "Noticeably reduced",  # option 3
}

# Mild answers (option 1) that do NOT trigger signals
MILD_ANSWERS = {
    "core_1": "Warm and connected",
    "core_2": "No noticeable changes",
    "core_3": "Open and detailed",
    "core_4": "No changes",
    "core_5": "Same or improved",
}


@pytest.fixture(scope="function")
def session_with_baseline():
    """Create a fresh session with baseline, changes, and timeline data."""
    # Start session
    response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
    assert response.status_code == 200, f"Failed to start session: {response.text}"
    session_id = response.json()["session_id"]
    
    # Submit baseline
    baseline_data = {
        "session_id": session_id,
        "relationship_duration": "3-5 years",
        "prior_satisfaction": 7,
        "communication_habits": "We talk daily about our days and plans",
        "emotional_closeness": 7,
        "transparency_level": 7
    }
    response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
    assert response.status_code == 200, f"Baseline failed: {response.text}"
    
    # Submit changes (select categories that may trigger signals)
    changes_data = {
        "session_id": session_id,
        "categories": ["digital_behavior", "emotional_distance", "communication_changes"]
    }
    response = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
    assert response.status_code == 200, f"Changes failed: {response.text}"
    
    # Submit timeline
    timeline_data = {
        "session_id": session_id,
        "when_started": "3_months",
        "gradual_or_sudden": "gradual",
        "multiple_at_once": False
    }
    response = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
    assert response.status_code == 200, f"Timeline failed: {response.text}"
    
    return session_id


class TestSessionCreation:
    """Test session creation and data recording APIs"""
    
    def test_start_analysis_creates_session(self):
        """POST /api/analysis/start creates session successfully"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["type"] == "deep"
        assert len(data["session_id"]) > 10  # UUID format
        print(f"✓ Session created: {data['session_id']}")
    
    def test_baseline_records_data(self):
        """POST /api/analysis/baseline records data"""
        # Create session first
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        baseline_data = {
            "session_id": session_id,
            "relationship_duration": "1_to_3",
            "prior_satisfaction": 6,
            "communication_habits": "Regular daily check-ins",
            "emotional_closeness": 8,
            "transparency_level": 7
        }
        response = requests.post(f"{BASE_URL}/api/analysis/baseline", json=baseline_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "baseline_recorded"
        assert data["next_step"] == "changes"
        print("✓ Baseline data recorded")
    
    def test_changes_records_categories(self):
        """POST /api/analysis/changes records change categories"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        # Submit baseline first
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "1_to_3",
            "prior_satisfaction": 7,
            "communication_habits": "Daily",
            "emotional_closeness": 7,
            "transparency_level": 7
        })
        
        changes_data = {
            "session_id": session_id,
            "categories": ["routine_changes", "communication_changes", "digital_behavior"]
        }
        response = requests.post(f"{BASE_URL}/api/analysis/changes", json=changes_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "changes_recorded"
        assert data["next_step"] == "timeline"
        print("✓ Changes data recorded")
    
    def test_timeline_records_data(self):
        """POST /api/analysis/timeline records timeline data"""
        response = requests.post(f"{BASE_URL}/api/analysis/start?analysis_type=deep")
        session_id = response.json()["session_id"]
        
        # Setup baseline and changes
        requests.post(f"{BASE_URL}/api/analysis/baseline", json={
            "session_id": session_id,
            "relationship_duration": "1_to_3",
            "prior_satisfaction": 7,
            "communication_habits": "Daily",
            "emotional_closeness": 7,
            "transparency_level": 7
        })
        requests.post(f"{BASE_URL}/api/analysis/changes", json={
            "session_id": session_id,
            "categories": ["routine_changes"]
        })
        
        timeline_data = {
            "session_id": session_id,
            "when_started": "1_month",
            "gradual_or_sudden": "sudden",
            "multiple_at_once": True
        }
        response = requests.post(f"{BASE_URL}/api/analysis/timeline", json=timeline_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "timeline_recorded"
        assert data["next_step"] == "investigation"
        print("✓ Timeline data recorded")


class TestCoreQuestions:
    """Test that core questions are returned in Stage 1"""
    
    def test_first_question_is_core(self, session_with_baseline):
        """First question returned is a core question (stage='core')"""
        session_id = session_with_baseline
        response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        assert response.status_code == 200
        data = response.json()
        
        assert data["stage"] == "core", f"Expected stage='core', got '{data.get('stage')}'"
        assert data["type"] == "core", f"Expected type='core', got '{data.get('type')}'"
        assert data["question_id"] == "core_1", f"First question should be core_1, got '{data.get('question_id')}'"
        assert "total_core" in data, "Response should include total_core field"
        assert data["total_core"] == 5, f"total_core should be 5, got {data.get('total_core')}"
        print(f"✓ First question is core: {data['question_id']} - {data['question_text'][:50]}...")
    
    def test_all_five_core_questions_returned_sequentially(self, session_with_baseline):
        """Core questions core_1 through core_5 are returned in order"""
        session_id = session_with_baseline
        
        for i, expected_id in enumerate(CORE_QUESTION_IDS, 1):
            # Get question
            response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            assert response.status_code == 200
            data = response.json()
            
            assert data["question_id"] == expected_id, f"Expected {expected_id}, got {data.get('question_id')}"
            assert data["stage"] == "core"
            assert data["type"] == "core"
            print(f"✓ Core question {i}: {expected_id} - {data['question_text'][:40]}...")
            
            # Answer with mild answer (no signal trigger)
            answer_data = {
                "session_id": session_id,
                "question_id": expected_id,
                "question_text": data["question_text"],
                "answer": MILD_ANSWERS[expected_id],
                "category": data["category"]
            }
            answer_response = requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
            assert answer_response.status_code == 200
            print(f"  ↳ Answered: {MILD_ANSWERS[expected_id][:30]}...")
        
        print("✓ All 5 core questions served correctly")


class TestMildAnswersNoFollowups:
    """Test that mild answers (option 1) result in no follow-ups"""
    
    def test_mild_answers_trigger_immediate_complete(self, session_with_baseline):
        """When all 5 core questions answered with mild answers, next question is stage='complete'"""
        session_id = session_with_baseline
        
        # Answer all 5 core questions with mild answers
        for q_id in CORE_QUESTION_IDS:
            q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            q_data = q_response.json()
            
            # Verify it's a core question
            if q_data.get("stage") == "complete":
                pytest.fail(f"Unexpected complete stage before answering all core questions")
            
            answer_data = {
                "session_id": session_id,
                "question_id": q_data["question_id"],
                "question_text": q_data["question_text"],
                "answer": MILD_ANSWERS.get(q_data["question_id"], q_data["options"][0] if q_data.get("options") else "OK"),
                "category": q_data["category"]
            }
            requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        
        # Next question should be complete (no follow-ups needed)
        final_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        final_data = final_response.json()
        
        assert final_data["stage"] == "complete", f"Expected stage='complete' after mild answers, got '{final_data.get('stage')}'"
        assert final_data["question_id"] == "complete"
        assert final_data["type"] == "complete"
        print("✓ Mild answers result in immediate completion (no follow-ups)")


class TestConcerningAnswersAdaptiveFollowups:
    """Test that concerning answers (options 3/4) trigger adaptive AI follow-ups"""
    
    def test_concerning_answers_trigger_adaptive_stage(self, session_with_baseline):
        """When core questions answered with concerning answers, adaptive stage triggered"""
        session_id = session_with_baseline
        
        # Answer all 5 core questions with CONCERNING answers
        for q_id in CORE_QUESTION_IDS:
            q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            q_data = q_response.json()
            
            if q_data.get("stage") == "complete":
                pytest.fail("Unexpected complete before all core questions")
            
            answer_data = {
                "session_id": session_id,
                "question_id": q_data["question_id"],
                "question_text": q_data["question_text"],
                "answer": CONCERNING_ANSWERS.get(q_data["question_id"], q_data["options"][2] if q_data.get("options") else "Concerning"),
                "category": q_data["category"]
            }
            response = requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
            assert response.status_code == 200
            print(f"  Answered {q_data['question_id']} with: {answer_data['answer'][:30]}...")
        
        # Next question should be adaptive follow-up
        followup_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        followup_data = followup_response.json()
        
        assert followup_data["stage"] == "adaptive", f"Expected stage='adaptive', got '{followup_data.get('stage')}'"
        assert followup_data["type"] == "ai_followup", f"Expected type='ai_followup', got '{followup_data.get('type')}'"
        assert "followup_number" in followup_data, "Should have followup_number"
        assert followup_data["followup_number"] == 1, f"First followup should be number 1"
        assert "max_followups" in followup_data, "Should have max_followups"
        assert followup_data["max_followups"] == 3, f"max_followups should be 3"
        print(f"✓ Adaptive follow-up triggered: {followup_data['question_text'][:50]}...")
    
    def test_first_followup_has_transition_message(self, session_with_baseline):
        """First AI follow-up includes transition_message field"""
        session_id = session_with_baseline
        
        # Answer all core questions with concerning answers
        for q_id in CORE_QUESTION_IDS:
            q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            q_data = q_response.json()
            
            answer_data = {
                "session_id": session_id,
                "question_id": q_data["question_id"],
                "question_text": q_data["question_text"],
                "answer": CONCERNING_ANSWERS.get(q_data["question_id"], "Concerning"),
                "category": q_data["category"]
            }
            requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        
        # Get first follow-up
        followup_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        followup_data = followup_response.json()
        
        assert "transition_message" in followup_data, "First follow-up should have transition_message"
        assert len(followup_data["transition_message"]) > 10, "transition_message should be meaningful"
        print(f"✓ Transition message: {followup_data['transition_message']}")


class TestMaxFollowupsEnforced:
    """Test that max 3 follow-up questions are enforced"""
    
    def test_max_three_followups_enforced(self, session_with_baseline):
        """After 3 AI follow-ups, stage='complete' is returned"""
        session_id = session_with_baseline
        
        # Answer all core questions with concerning answers
        for q_id in CORE_QUESTION_IDS:
            q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            q_data = q_response.json()
            
            answer_data = {
                "session_id": session_id,
                "question_id": q_data["question_id"],
                "question_text": q_data["question_text"],
                "answer": CONCERNING_ANSWERS.get(q_data["question_id"], "Concerning"),
                "category": q_data["category"]
            }
            requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        
        # Now answer up to 3 follow-up questions
        followup_count = 0
        for i in range(4):  # Try 4 times, should only get 3 follow-ups
            time.sleep(0.5)  # AI generation may take time
            
            q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
            q_data = q_response.json()
            
            if q_data.get("stage") == "complete":
                print(f"✓ Stage complete after {followup_count} follow-ups")
                break
            
            if q_data.get("stage") == "adaptive":
                followup_count += 1
                assert q_data["followup_number"] == followup_count, f"Expected followup #{followup_count}"
                print(f"  Follow-up {followup_count}: {q_data['question_text'][:40]}...")
                
                # Answer the follow-up (with concerning option if available)
                answer_choice = q_data["options"][2] if q_data.get("options") and len(q_data["options"]) > 2 else "Frequently"
                answer_data = {
                    "session_id": session_id,
                    "question_id": q_data["question_id"],
                    "question_text": q_data["question_text"],
                    "answer": answer_choice,
                    "category": q_data["category"]
                }
                requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        
        # After loop, check that we got exactly 3 follow-ups
        assert followup_count <= 3, f"Should have max 3 follow-ups, got {followup_count}"
        
        # Final check - should be complete now
        final_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        final_data = final_response.json()
        assert final_data["stage"] == "complete", "Should be complete after 3 follow-ups"
        print(f"✓ Max 3 follow-ups enforced ({followup_count} delivered)")


class TestAnswerProcessing:
    """Test POST /api/analysis/answer response format"""
    
    def test_answer_returns_expected_fields(self, session_with_baseline):
        """POST /api/analysis/answer returns questions_answered, trust_disruption_index, stability_hearts, confidence_level"""
        session_id = session_with_baseline
        
        # Get first question
        q_response = requests.get(f"{BASE_URL}/api/analysis/{session_id}/question")
        q_data = q_response.json()
        
        answer_data = {
            "session_id": session_id,
            "question_id": q_data["question_id"],
            "question_text": q_data["question_text"],
            "answer": q_data["options"][0] if q_data.get("options") else "OK",
            "category": q_data["category"]
        }
        response = requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert "questions_answered" in data, "Should have questions_answered"
        assert data["questions_answered"] == 1, "Should be 1 after first answer"
        
        assert "trust_disruption_index" in data, "Should have trust_disruption_index"
        assert isinstance(data["trust_disruption_index"], (int, float)), "trust_disruption_index should be numeric"
        
        assert "stability_hearts" in data, "Should have stability_hearts"
        assert isinstance(data["stability_hearts"], int), "stability_hearts should be int"
        assert 0 <= data["stability_hearts"] <= 4, "stability_hearts should be 0-4"
        
        assert "confidence_level" in data, "Should have confidence_level"
        assert data["confidence_level"] in ["low", "moderate", "high"], "confidence_level should be low/moderate/high"
        
        print(f"✓ Answer response: answered={data['questions_answered']}, trust_index={data['trust_disruption_index']:.1f}, hearts={data['stability_hearts']}, confidence={data['confidence_level']}")


class TestInvalidSession:
    """Test error handling for invalid sessions"""
    
    def test_question_for_invalid_session_returns_404(self):
        """GET /api/analysis/{invalid_id}/question returns 404"""
        response = requests.get(f"{BASE_URL}/api/analysis/invalid-session-id/question")
        assert response.status_code == 404
        print("✓ Invalid session returns 404 for question endpoint")
    
    def test_answer_for_invalid_session_returns_404(self):
        """POST /api/analysis/answer with invalid session returns 404"""
        answer_data = {
            "session_id": "invalid-session-id",
            "question_id": "core_1",
            "question_text": "Test",
            "answer": "Test",
            "category": "test"
        }
        response = requests.post(f"{BASE_URL}/api/analysis/answer", json=answer_data)
        assert response.status_code == 404
        print("✓ Invalid session returns 404 for answer endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
