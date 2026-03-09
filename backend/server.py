from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============= Models =============

class AnalysisSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    analysis_type: str = "pulse"  # pulse or deep
    current_step: str = "baseline"
    baseline_data: Optional[Dict[str, Any]] = None
    changes_data: Optional[List[str]] = None
    timeline_data: Optional[Dict[str, Any]] = None
    evidence_signals: List[Dict[str, Any]] = []
    qa_history: List[Dict[str, Any]] = []
    mirror_mode_data: Optional[Dict[str, Any]] = None
    hypotheses: Dict[str, float] = {
        "emotional_distance": 0.0,
        "communication_breakdown": 0.0,
        "external_stress": 0.0,
        "trust_erosion": 0.0,
        "lifestyle_divergence": 0.0,
        "unresolved_conflict": 0.0,
        "intimacy_decline": 0.0
    }
    signals: Dict[str, float] = {
        "routine_changes": 0.0,
        "communication_changes": 0.0,
        "emotional_indicators": 0.0,
        "digital_behavior": 0.0,
        "social_behavior": 0.0,
        "financial_signals": 0.0
    }
    trust_disruption_index: float = 0.0
    stability_hearts: int = 4
    narrative_consistency: float = 100.0
    confidence_level: str = "low"
    dominant_pattern: str = ""
    context_estimation: List[str] = []

class PulseInput(BaseModel):
    session_id: str
    emotional_connection: int  # 1-5
    communication_quality: int  # 1-5
    perceived_tension: int  # 1-5

class BaselineInput(BaseModel):
    session_id: str
    relationship_duration: str
    prior_satisfaction: int
    communication_habits: str
    emotional_closeness: int
    transparency_level: int

class ChangesInput(BaseModel):
    session_id: str
    categories: List[str]

class TimelineInput(BaseModel):
    session_id: str
    when_started: str
    gradual_or_sudden: str
    multiple_at_once: bool

class EvidenceInput(BaseModel):
    session_id: str
    signal_type: str
    description: str

class AnswerInput(BaseModel):
    session_id: str
    question_id: str
    question_text: str
    answer: str
    category: str

class MirrorModeInput(BaseModel):
    session_id: str
    partner_emotional: int
    partner_communication: int
    partner_trust: int

class ConversationCoachInput(BaseModel):
    session_id: str
    tone: str
    topic: str

# ============= AI Engine =============

SYSTEM_PROMPT = """You are TrustLens, an empathetic relationship intelligence assistant. Your role is to help users understand behavioral changes in their relationships through careful, non-judgmental analysis.

CORE PRINCIPLES:
1. Never accuse or make definitive statements
2. Focus on behavioral patterns, not conclusions
3. Be empathetic and supportive
4. Provide psychological insights
5. Help users gain clarity, not anxiety

ANALYSIS CATEGORIES:
- Emotional distance patterns
- Communication breakdown indicators
- External stress factors
- Trust erosion signals
- Lifestyle divergence
- Unresolved conflict patterns
- Intimacy decline indicators

When generating questions or insights, always be:
- Calm and measured
- Psychologically informed
- Non-accusatory
- Supportive of the user's emotional state"""

async def get_ai_response(session_id: str, prompt: str, system_override: str = None) -> str:
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"trustlens-{session_id}",
            system_message=system_override or SYSTEM_PROMPT
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logger.error(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

async def generate_adaptive_question(session: dict) -> dict:
    changes = session.get('changes_data', [])
    qa_history = session.get('qa_history', [])
    hypotheses = session.get('hypotheses', {})
    
    context = f"""
Session context:
- Changed areas: {', '.join(changes) if changes else 'Not specified'}
- Questions asked: {len(qa_history)}
- Current hypothesis weights: {hypotheses}

Recent Q&A:
"""
    for qa in qa_history[-3:]:
        context += f"\nQ: {qa.get('question_text', 'N/A')}\nA: {qa.get('answer', 'N/A')}\n"

    prompt = f"""{context}

Generate ONE targeted, empathetic question that would provide the most insight into the relationship dynamics.
Focus on the area with highest uncertainty.

Respond in JSON format:
{{"question_id": "q_{len(qa_history)+1}", "question_text": "Your empathetic question?", "category": "emotional_indicators|communication_changes|routine_changes|digital_behavior|social_behavior|financial_signals", "options": ["Option 1", "Option 2", "Option 3", "Option 4"] or null}}

Only output JSON."""

    try:
        response = await get_ai_response(session['id'], prompt)
        import json
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception as e:
        logger.error(f"Question generation error: {e}")
    
    return {
        "question_id": f"q_{len(qa_history)+1}",
        "question_text": "How would you describe the emotional atmosphere at home recently?",
        "category": "emotional_indicators",
        "options": ["Warm and connected", "Slightly distant", "Noticeably tense", "Cold or uncomfortable"]
    }

async def analyze_and_update(session: dict, answer_data: dict) -> dict:
    hypotheses = session.get('hypotheses', {})
    signals = session.get('signals', {})
    
    prompt = f"""
Analyze this response in the context of relationship dynamics:

Question: {answer_data.get('question_text')}
Answer: {answer_data.get('answer')}
Category: {answer_data.get('category')}

Current state:
- Hypotheses: {hypotheses}
- Signals: {signals}

Based on this answer, update the probabilities (0.0-1.0).

Respond in JSON:
{{
    "hypotheses": {{"emotional_distance": 0.0-1.0, "communication_breakdown": 0.0-1.0, "external_stress": 0.0-1.0, "trust_erosion": 0.0-1.0, "lifestyle_divergence": 0.0-1.0, "unresolved_conflict": 0.0-1.0, "intimacy_decline": 0.0-1.0}},
    "signals": {{"routine_changes": 0.0-1.0, "communication_changes": 0.0-1.0, "emotional_indicators": 0.0-1.0, "digital_behavior": 0.0-1.0, "social_behavior": 0.0-1.0, "financial_signals": 0.0-1.0}},
    "narrative_consistency": 0-100,
    "insight": "Brief psychological insight"
}}

Only JSON."""

    try:
        response = await get_ai_response(session['id'], prompt)
        import json
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception as e:
        logger.error(f"Analysis error: {e}")
    
    return {}

async def generate_conversation_guidance(session: dict, tone: str, topic: str) -> dict:
    prompt = f"""
Generate conversation guidance for someone wanting to discuss relationship concerns with their partner.

Tone requested: {tone}
Topic to discuss: {topic}

Current relationship state:
- Trust Disruption Index: {session.get('trust_disruption_index', 0)}
- Dominant patterns: {session.get('dominant_pattern', 'Not determined')}

Provide:
1. Opening statement suggestion
2. 3-4 questions to ask
3. Things to avoid saying
4. What to observe during conversation

Respond in JSON:
{{
    "opening": "Suggested opening statement",
    "questions": ["Question 1", "Question 2", "Question 3"],
    "avoid": ["Thing to avoid 1", "Thing to avoid 2"],
    "observe": ["What to watch for 1", "What to watch for 2"]
}}

Only JSON."""

    try:
        response = await get_ai_response(session['id'], prompt)
        import json
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception as e:
        logger.error(f"Conversation coach error: {e}")
    
    return {
        "opening": "I've been feeling like we should talk about how things have been between us lately.",
        "questions": [
            "How have you been feeling about us recently?",
            "Is there anything on your mind you'd like to share?",
            "What do you think we could do to feel more connected?"
        ],
        "avoid": ["Accusations", "Bringing up past issues", "Ultimatums"],
        "observe": ["Body language", "Willingness to engage", "Emotional responses"]
    }

def calculate_trust_index(hypotheses: dict, signals: dict) -> float:
    h_weights = {"emotional_distance": 0.18, "communication_breakdown": 0.16, "external_stress": 0.08, "trust_erosion": 0.22, "lifestyle_divergence": 0.12, "unresolved_conflict": 0.14, "intimacy_decline": 0.10}
    s_weights = {"routine_changes": 0.12, "communication_changes": 0.20, "emotional_indicators": 0.22, "digital_behavior": 0.18, "social_behavior": 0.15, "financial_signals": 0.13}
    
    h_score = sum(hypotheses.get(h, 0) * w * 100 for h, w in h_weights.items())
    s_score = sum(signals.get(s, 0) * w * 100 for s, w in s_weights.items())
    
    return min(100, (h_score * 0.6 + s_score * 0.4))

def calculate_stability_hearts(trust_index: float) -> int:
    if trust_index < 20:
        return 4
    if trust_index < 40:
        return 3
    if trust_index < 60:
        return 2
    if trust_index < 80:
        return 1
    return 0

def get_dominant_pattern(hypotheses: dict) -> str:
    if not hypotheses:
        return "Insufficient data"
    return max(hypotheses.items(), key=lambda x: x[1])[0].replace('_', ' ').title()

def get_pattern_statistics(hypotheses: dict) -> dict:
    """Simulated global pattern comparison statistics"""
    trust_erosion = hypotheses.get('trust_erosion', 0)
    emotional_distance = hypotheses.get('emotional_distance', 0)
    
    # Simulated realistic statistics based on pattern severity
    avg_severity = (trust_erosion + emotional_distance) / 2
    
    if avg_severity > 0.6:
        return {"confirmed_issues": 67, "relationship_conflict": 21, "resolved_positively": 12}
    elif avg_severity > 0.4:
        return {"confirmed_issues": 42, "relationship_conflict": 35, "resolved_positively": 23}
    elif avg_severity > 0.2:
        return {"confirmed_issues": 23, "relationship_conflict": 38, "resolved_positively": 39}
    else:
        return {"confirmed_issues": 8, "relationship_conflict": 27, "resolved_positively": 65}

def generate_clarity_actions(hypotheses: dict, signals: dict) -> List[str]:
    actions = ["Have an open, non-accusatory conversation about your feelings"]
    
    if signals.get('communication_changes', 0) > 0.4:
        actions.append("Discuss communication patterns and preferences calmly")
    if signals.get('emotional_indicators', 0) > 0.4:
        actions.append("Express your emotional needs and ask about theirs")
    if hypotheses.get('external_stress', 0) > 0.3:
        actions.append("Explore if external stressors are affecting the relationship")
    if signals.get('routine_changes', 0) > 0.4:
        actions.append("Discuss recent schedule changes openly")
    
    actions.append("Consider professional relationship counseling")
    actions.append("Focus on rebuilding emotional connection through quality time")
    
    return actions[:6]

# ============= API Routes =============

@api_router.get("/")
async def root():
    return {"message": "TrustLens API", "status": "active"}

@api_router.post("/analysis/start")
async def start_analysis(analysis_type: str = "pulse"):
    session = AnalysisSession(analysis_type=analysis_type)
    session_dict = session.model_dump()
    await db.analysis_sessions.insert_one(session_dict)
    return {"session_id": session.id, "type": analysis_type}

@api_router.post("/analysis/pulse")
async def submit_pulse(data: PulseInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate pulse score (higher = more strain)
    avg_score = (data.emotional_connection + data.communication_quality + (6 - data.perceived_tension)) / 3
    stability_hearts = min(4, max(0, int(avg_score)))
    trust_index = max(0, min(100, (5 - avg_score) * 25))
    
    pulse_data = {
        "emotional_connection": data.emotional_connection,
        "communication_quality": data.communication_quality,
        "perceived_tension": data.perceived_tension,
        "stability_hearts": stability_hearts,
        "trust_disruption_index": trust_index
    }
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {
            "baseline_data": pulse_data,
            "stability_hearts": stability_hearts,
            "trust_disruption_index": trust_index,
            "current_step": "pulse_complete"
        }}
    )
    
    return {
        "stability_hearts": stability_hearts,
        "trust_disruption_index": trust_index,
        "interpretation": "Stable" if stability_hearts >= 3 else "Moderate strain" if stability_hearts >= 2 else "Significant stress"
    }

@api_router.post("/analysis/baseline")
async def submit_baseline(data: BaselineInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    baseline_data = {
        "relationship_duration": data.relationship_duration,
        "prior_satisfaction": data.prior_satisfaction,
        "communication_habits": data.communication_habits,
        "emotional_closeness": data.emotional_closeness,
        "transparency_level": data.transparency_level
    }
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {"baseline_data": baseline_data, "current_step": "changes"}}
    )
    
    return {"status": "baseline_recorded", "next_step": "changes"}

@api_router.post("/analysis/changes")
async def submit_changes(data: ChangesInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {"changes_data": data.categories, "current_step": "timeline"}}
    )
    
    return {"status": "changes_recorded", "next_step": "timeline"}

@api_router.post("/analysis/timeline")
async def submit_timeline(data: TimelineInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    timeline_data = {
        "when_started": data.when_started,
        "gradual_or_sudden": data.gradual_or_sudden,
        "multiple_at_once": data.multiple_at_once
    }
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {"timeline_data": timeline_data, "current_step": "investigation"}}
    )
    
    return {"status": "timeline_recorded", "next_step": "investigation"}

@api_router.post("/analysis/evidence")
async def submit_evidence(data: EvidenceInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    evidence = {
        "type": data.signal_type,
        "description": data.description,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$push": {"evidence_signals": evidence}}
    )
    
    return {"status": "evidence_recorded"}

@api_router.get("/analysis/{session_id}/question")
async def get_next_question(session_id: str):
    session = await db.analysis_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = await generate_adaptive_question(session)
    return question

@api_router.post("/analysis/answer")
async def submit_answer(data: AnswerInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    qa_entry = {
        "question_id": data.question_id,
        "question_text": data.question_text,
        "answer": data.answer,
        "category": data.category,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    updates = await analyze_and_update(session, qa_entry)
    
    hypotheses = session.get('hypotheses', {})
    signals = session.get('signals', {})
    
    if updates.get('hypotheses'):
        for k, v in updates['hypotheses'].items():
            if k in hypotheses:
                hypotheses[k] = v
    
    if updates.get('signals'):
        for k, v in updates['signals'].items():
            if k in signals:
                signals[k] = v
    
    narrative = updates.get('narrative_consistency', session.get('narrative_consistency', 100))
    qa_history = session.get('qa_history', [])
    qa_history.append(qa_entry)
    
    trust_index = calculate_trust_index(hypotheses, signals)
    hearts = calculate_stability_hearts(trust_index)
    confidence = "high" if len(qa_history) >= 8 else "moderate" if len(qa_history) >= 5 else "low"
    dominant = get_dominant_pattern(hypotheses)
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {
            "qa_history": qa_history,
            "hypotheses": hypotheses,
            "signals": signals,
            "narrative_consistency": narrative,
            "trust_disruption_index": trust_index,
            "stability_hearts": hearts,
            "confidence_level": confidence,
            "dominant_pattern": dominant
        }}
    )
    
    return {
        "questions_answered": len(qa_history),
        "trust_disruption_index": trust_index,
        "stability_hearts": hearts,
        "confidence_level": confidence,
        "insight": updates.get('insight', '')
    }

@api_router.post("/analysis/mirror")
async def submit_mirror_mode(data: MirrorModeInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    baseline = session.get('baseline_data', {})
    user_emotional = baseline.get('emotional_closeness', 3)
    user_communication = baseline.get('prior_satisfaction', 3)
    user_trust = baseline.get('transparency_level', 3)
    
    perception_gap = {
        "emotional": abs(user_emotional - data.partner_emotional),
        "communication": abs(user_communication - data.partner_communication),
        "trust": abs(user_trust - data.partner_trust),
        "user_view": {"emotional": user_emotional, "communication": user_communication, "trust": user_trust},
        "partner_view": {"emotional": data.partner_emotional, "communication": data.partner_communication, "trust": data.partner_trust}
    }
    
    total_gap = sum([perception_gap['emotional'], perception_gap['communication'], perception_gap['trust']])
    has_mismatch = total_gap > 4
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {"mirror_mode_data": perception_gap}}
    )
    
    return {
        "perception_gap": perception_gap,
        "has_significant_mismatch": has_mismatch,
        "insight": "Potential perception mismatch detected. Consider discussing how you each view the relationship." if has_mismatch else "Your perceptions appear relatively aligned."
    }

@api_router.post("/analysis/conversation-coach")
async def get_conversation_guidance(data: ConversationCoachInput):
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    guidance = await generate_conversation_guidance(session, data.tone, data.topic)
    return guidance

@api_router.get("/analysis/{session_id}/results")
async def get_results(session_id: str):
    session = await db.analysis_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    hypotheses = session.get('hypotheses', {})
    signals = session.get('signals', {})
    
    clarity_actions = generate_clarity_actions(hypotheses, signals)
    pattern_stats = get_pattern_statistics(hypotheses)
    
    timeline_events = []
    timeline_data = session.get('timeline_data', {})
    if timeline_data.get('when_started'):
        timeline_events.append({"period": timeline_data['when_started'], "event": "Changes began", "type": "start"})
    
    changes = session.get('changes_data', [])
    for i, change in enumerate(changes[:3]):
        timeline_events.append({"period": f"Phase {i+1}", "event": f"{change.replace('_', ' ').title()}", "type": "development"})
    
    return {
        "session_id": session_id,
        "trust_disruption_index": session.get('trust_disruption_index', 0),
        "stability_hearts": session.get('stability_hearts', 4),
        "dominant_pattern": session.get('dominant_pattern', 'Insufficient data'),
        "confidence_level": session.get('confidence_level', 'low'),
        "narrative_consistency": session.get('narrative_consistency', 100),
        "hypotheses": hypotheses,
        "signals": signals,
        "pattern_statistics": pattern_stats,
        "context_estimation": session.get('context_estimation', []),
        "clarity_actions": clarity_actions,
        "timeline_events": timeline_events,
        "mirror_mode_data": session.get('mirror_mode_data'),
        "questions_answered": len(session.get('qa_history', [])),
        "trustlens_perspective": generate_perspective(session)
    }

def generate_perspective(session: dict) -> str:
    trust_index = session.get('trust_disruption_index', 0)
    dominant = session.get('dominant_pattern', '')
    
    if trust_index < 25:
        return "Based on the signals you described, your relationship appears to be in a relatively stable state. The changes you've noticed may be normal variations in relationship dynamics."
    elif trust_index < 50:
        return f"Your relationship shows some signs of {dominant.lower()}. While this doesn't indicate a crisis, addressing these patterns through open communication could strengthen your bond."
    elif trust_index < 75:
        return f"Based on the signals you described, your relationship shows significant changes in trust dynamics, particularly around {dominant.lower()}. Your concerns appear understandable. Consider having an open conversation or seeking professional guidance."
    else:
        return f"The patterns you've described suggest substantial changes in your relationship, centered around {dominant.lower()}. This doesn't confirm any specific conclusion, but your feelings of concern are validated by the signals present. Professional support may be beneficial."

@api_router.get("/analysis/{session_id}/status")
async def get_session_status(session_id: str):
    session = await db.analysis_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "analysis_type": session.get('analysis_type', 'pulse'),
        "current_step": session.get('current_step', 'baseline'),
        "questions_answered": len(session.get('qa_history', [])),
        "trust_disruption_index": session.get('trust_disruption_index', 0)
    }

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
