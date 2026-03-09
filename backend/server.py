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

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= Models =============

class AnalysisSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "started"
    current_step: str = "baseline"
    baseline_data: Optional[Dict[str, Any]] = None
    changes_data: Optional[List[str]] = None
    timeline_data: Optional[Dict[str, Any]] = None
    qa_history: List[Dict[str, Any]] = []
    hypotheses: Dict[str, float] = {
        "emotional_disengagement": 0.0,
        "workplace_proximity": 0.0,
        "digital_emotional_affair": 0.0,
        "stress_related_changes": 0.0,
        "hidden_personal_crisis": 0.0,
        "opportunity_based_infidelity": 0.0,
        "gradual_relationship_withdrawal": 0.0
    }
    signals: Dict[str, float] = {
        "routine_changes": 0.0,
        "communication_changes": 0.0,
        "emotional_indicators": 0.0,
        "digital_behavior": 0.0,
        "social_behavior": 0.0,
        "financial_signals": 0.0
    }
    narrative_consistency: float = 100.0
    trust_disruption_index: float = 0.0
    confidence_level: str = "low"
    uncertainty_level: str = "high"
    context_estimation: List[str] = []
    reactions: List[Dict[str, Any]] = []

class BaselineInput(BaseModel):
    session_id: str
    relationship_duration: str
    perceived_quality: int  # 1-10
    communication_frequency: str
    emotional_connection: int  # 1-10
    transparency_level: int  # 1-10
    shared_routines: str

class ChangesInput(BaseModel):
    session_id: str
    categories: List[str]

class TimelineInput(BaseModel):
    session_id: str
    when_started: str
    gradual_or_sudden: str
    multiple_at_once: bool

class AnswerInput(BaseModel):
    session_id: str
    question_id: str
    question_text: str
    answer: str
    category: str

class ReactionInput(BaseModel):
    session_id: str
    reaction_type: str
    notes: Optional[str] = None

class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    category: str
    options: Optional[List[str]] = None

class AnalysisResult(BaseModel):
    session_id: str
    trust_disruption_index: float
    confidence_level: str
    uncertainty_level: str
    hypotheses: Dict[str, float]
    signals: Dict[str, float]
    narrative_consistency: float
    context_estimation: List[str]
    clarity_actions: List[str]
    timeline_events: List[Dict[str, Any]]
    pattern_clusters: List[str]

# ============= AI Engine =============

SYSTEM_PROMPT = """You are TrustLens, an intelligent relationship analysis engine. Your role is to help users understand behavioral changes in their relationships through careful, non-judgmental analysis.

IMPORTANT GUIDELINES:
1. Never accuse or make definitive statements about infidelity
2. Focus on behavioral patterns, not conclusions
3. Ask one targeted question at a time
4. Track multiple competing hypotheses
5. Be empathetic but analytical
6. Consider stress, work changes, and personal issues as valid explanations

HYPOTHESES TO TRACK:
- Emotional disengagement
- Workplace proximity pattern
- Digital emotional affair
- Stress-related behavioral changes
- Hidden personal crisis
- Opportunity-based infidelity
- Gradual relationship withdrawal

SIGNAL CATEGORIES:
- Routine changes
- Communication changes
- Emotional indicators
- Digital behavior
- Social behavior
- Financial signals

When generating questions, target the hypothesis or signal category with the highest information value based on current data."""

async def get_ai_response(session_id: str, prompt: str, system_override: str = None) -> str:
    """Get AI response using emergentintegrations"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"trustlens-{session_id}",
            system_message=system_override or SYSTEM_PROMPT
        )
        chat.with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logger.error(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

async def generate_next_question(session: dict) -> dict:
    """Generate the next adaptive question based on session state"""
    changes = session.get('changes_data', [])
    qa_history = session.get('qa_history', [])
    hypotheses = session.get('hypotheses', {})
    
    # Build context for AI
    context = f"""
Current session state:
- Detected change categories: {', '.join(changes) if changes else 'None specified'}
- Questions asked so far: {len(qa_history)}
- Current hypothesis probabilities: {hypotheses}

Previous Q&A:
"""
    for qa in qa_history[-5:]:  # Last 5 QAs for context
        context += f"\nQ: {qa.get('question_text', 'N/A')}\nA: {qa.get('answer', 'N/A')}\n"

    prompt = f"""{context}

Based on this information, generate the SINGLE most informative question to ask next.
Focus on the category or hypothesis with the highest uncertainty.

Respond in this exact JSON format:
{{"question_id": "q_{len(qa_history)+1}", "question_text": "Your question here?", "category": "one of: routine_changes, communication_changes, emotional_indicators, digital_behavior, social_behavior, financial_signals", "options": ["Option 1", "Option 2", "Option 3", "Option 4"] or null for open text}}

Only output the JSON, nothing else."""

    try:
        response = await get_ai_response(session['id'], prompt)
        # Parse JSON from response
        import json
        # Clean response - find JSON in response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except Exception as e:
        logger.error(f"Question generation error: {e}")
    
    # Fallback question
    return {
        "question_id": f"q_{len(qa_history)+1}",
        "question_text": "Have you noticed any changes in how your partner communicates with you recently?",
        "category": "communication_changes",
        "options": ["Much less communication", "Slightly less", "About the same", "More communication"]
    }

async def update_analysis(session: dict, answer_data: dict) -> dict:
    """Update hypotheses and signals based on new answer"""
    qa_history = session.get('qa_history', [])
    hypotheses = session.get('hypotheses', {})
    signals = session.get('signals', {})
    
    # Build analysis prompt
    prompt = f"""
Analyze this Q&A in the context of relationship behavioral analysis:

Question: {answer_data.get('question_text')}
Answer: {answer_data.get('answer')}
Category: {answer_data.get('category')}

Current hypothesis probabilities: {hypotheses}
Current signal intensities: {signals}

Previous Q&A history (last 5):
"""
    for qa in qa_history[-5:]:
        prompt += f"\nQ: {qa.get('question_text', 'N/A')}\nA: {qa.get('answer', 'N/A')}"

    prompt += """

Based on this answer, update the probabilities. Consider:
1. Does this answer support or contradict any hypothesis?
2. What signal category does this affect?
3. Are there any narrative inconsistencies?

Respond in this exact JSON format:
{
    "hypotheses": {"emotional_disengagement": 0.0-1.0, "workplace_proximity": 0.0-1.0, "digital_emotional_affair": 0.0-1.0, "stress_related_changes": 0.0-1.0, "hidden_personal_crisis": 0.0-1.0, "opportunity_based_infidelity": 0.0-1.0, "gradual_relationship_withdrawal": 0.0-1.0},
    "signals": {"routine_changes": 0.0-1.0, "communication_changes": 0.0-1.0, "emotional_indicators": 0.0-1.0, "digital_behavior": 0.0-1.0, "social_behavior": 0.0-1.0, "financial_signals": 0.0-1.0},
    "narrative_consistency": 0-100,
    "context_estimation": ["context1", "context2"]
}

Only output the JSON, nothing else."""

    try:
        response = await get_ai_response(session['id'], prompt)
        import json
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            updates = json.loads(json_str)
            return updates
    except Exception as e:
        logger.error(f"Analysis update error: {e}")
    
    return {}

def calculate_trust_disruption_index(hypotheses: dict, signals: dict) -> float:
    """Calculate the Trust Disruption Index (0-100)"""
    # Weight hypotheses
    hypothesis_weights = {
        "emotional_disengagement": 0.15,
        "workplace_proximity": 0.12,
        "digital_emotional_affair": 0.18,
        "stress_related_changes": 0.08,
        "hidden_personal_crisis": 0.10,
        "opportunity_based_infidelity": 0.22,
        "gradual_relationship_withdrawal": 0.15
    }
    
    hypothesis_score = sum(
        hypotheses.get(h, 0) * w * 100 
        for h, w in hypothesis_weights.items()
    )
    
    # Weight signals
    signal_weights = {
        "routine_changes": 0.12,
        "communication_changes": 0.18,
        "emotional_indicators": 0.20,
        "digital_behavior": 0.22,
        "social_behavior": 0.15,
        "financial_signals": 0.13
    }
    
    signal_score = sum(
        signals.get(s, 0) * w * 100 
        for s, w in signal_weights.items()
    )
    
    # Combined score
    return min(100, (hypothesis_score * 0.6 + signal_score * 0.4))

def determine_confidence_level(qa_count: int, signal_consistency: float) -> str:
    """Determine diagnostic confidence level"""
    if qa_count >= 10 and signal_consistency > 0.7:
        return "high"
    elif qa_count >= 5 and signal_consistency > 0.4:
        return "moderate"
    return "low"

def determine_uncertainty_level(hypotheses: dict) -> str:
    """Determine uncertainty based on hypothesis spread"""
    values = list(hypotheses.values())
    if not values:
        return "high"
    
    max_val = max(values)
    spread = max_val - (sum(values) / len(values))
    
    if spread > 0.3 and max_val > 0.6:
        return "low"
    elif spread > 0.15 or max_val > 0.4:
        return "moderate"
    return "high"

def generate_clarity_actions(hypotheses: dict, signals: dict) -> List[str]:
    """Generate recommended clarity actions"""
    actions = []
    
    # Base actions
    actions.append("Initiate an open, non-accusatory conversation about recent changes")
    
    if signals.get('communication_changes', 0) > 0.5:
        actions.append("Ask calmly about communication preferences and any stressors")
    
    if signals.get('routine_changes', 0) > 0.5:
        actions.append("Discuss schedule changes and work demands openly")
    
    if signals.get('emotional_indicators', 0) > 0.5:
        actions.append("Express your feelings and ask about emotional state")
    
    if signals.get('digital_behavior', 0) > 0.5:
        actions.append("Discuss transparency expectations around digital privacy")
    
    if hypotheses.get('stress_related_changes', 0) > 0.4:
        actions.append("Explore potential external stressors (work, family, health)")
    
    if hypotheses.get('hidden_personal_crisis', 0) > 0.4:
        actions.append("Create safe space for sharing difficult personal matters")
    
    actions.append("Observe response patterns during conversations")
    actions.append("Consider professional relationship counseling for guidance")
    
    return actions[:6]  # Return top 6 actions

# ============= API Routes =============

@api_router.get("/")
async def root():
    return {"message": "TrustLens API", "status": "active"}

@api_router.post("/analysis/start")
async def start_analysis():
    """Initialize a new analysis session"""
    session = AnalysisSession()
    session_dict = session.model_dump()
    await db.analysis_sessions.insert_one(session_dict)
    return {"session_id": session.id, "status": "started"}

@api_router.post("/analysis/baseline")
async def submit_baseline(data: BaselineInput):
    """Submit baseline relationship data"""
    session = await db.analysis_sessions.find_one(
        {"id": data.session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    baseline_data = {
        "relationship_duration": data.relationship_duration,
        "perceived_quality": data.perceived_quality,
        "communication_frequency": data.communication_frequency,
        "emotional_connection": data.emotional_connection,
        "transparency_level": data.transparency_level,
        "shared_routines": data.shared_routines
    }
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {
            "baseline_data": baseline_data,
            "current_step": "changes"
        }}
    )
    
    return {"status": "baseline_recorded", "next_step": "changes"}

@api_router.post("/analysis/changes")
async def submit_changes(data: ChangesInput):
    """Submit detected change categories"""
    session = await db.analysis_sessions.find_one(
        {"id": data.session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {
            "changes_data": data.categories,
            "current_step": "timeline"
        }}
    )
    
    return {"status": "changes_recorded", "next_step": "timeline"}

@api_router.post("/analysis/timeline")
async def submit_timeline(data: TimelineInput):
    """Submit timeline reconstruction data"""
    session = await db.analysis_sessions.find_one(
        {"id": data.session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    timeline_data = {
        "when_started": data.when_started,
        "gradual_or_sudden": data.gradual_or_sudden,
        "multiple_at_once": data.multiple_at_once
    }
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {
            "timeline_data": timeline_data,
            "current_step": "investigation"
        }}
    )
    
    return {"status": "timeline_recorded", "next_step": "investigation"}

@api_router.get("/analysis/{session_id}/question")
async def get_next_question(session_id: str):
    """Get the next adaptive question"""
    session = await db.analysis_sessions.find_one(
        {"id": session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = await generate_next_question(session)
    return question

@api_router.post("/analysis/answer")
async def submit_answer(data: AnswerInput):
    """Submit answer and get updated analysis"""
    session = await db.analysis_sessions.find_one(
        {"id": data.session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Record the answer
    qa_entry = {
        "question_id": data.question_id,
        "question_text": data.question_text,
        "answer": data.answer,
        "category": data.category,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Update analysis with AI
    updates = await update_analysis(session, qa_entry)
    
    # Merge updates
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
    
    narrative_consistency = updates.get('narrative_consistency', session.get('narrative_consistency', 100))
    context_estimation = updates.get('context_estimation', session.get('context_estimation', []))
    
    # Calculate derived metrics
    qa_history = session.get('qa_history', [])
    qa_history.append(qa_entry)
    
    trust_index = calculate_trust_disruption_index(hypotheses, signals)
    confidence = determine_confidence_level(len(qa_history), narrative_consistency / 100)
    uncertainty = determine_uncertainty_level(hypotheses)
    
    # Update session
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {
            "qa_history": qa_history,
            "hypotheses": hypotheses,
            "signals": signals,
            "narrative_consistency": narrative_consistency,
            "trust_disruption_index": trust_index,
            "confidence_level": confidence,
            "uncertainty_level": uncertainty,
            "context_estimation": context_estimation
        }}
    )
    
    return {
        "status": "answer_recorded",
        "questions_answered": len(qa_history),
        "trust_disruption_index": trust_index,
        "confidence_level": confidence
    }

@api_router.post("/analysis/reaction")
async def submit_reaction(data: ReactionInput):
    """Submit reaction tracking data"""
    session = await db.analysis_sessions.find_one(
        {"id": data.session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    reaction = {
        "type": data.reaction_type,
        "notes": data.notes,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    reactions = session.get('reactions', [])
    reactions.append(reaction)
    
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$push": {"reactions": reaction}}
    )
    
    return {"status": "reaction_recorded"}

@api_router.get("/analysis/{session_id}/results")
async def get_results(session_id: str):
    """Get full analysis results"""
    session = await db.analysis_sessions.find_one(
        {"id": session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Generate clarity actions
    clarity_actions = generate_clarity_actions(
        session.get('hypotheses', {}),
        session.get('signals', {})
    )
    
    # Build timeline events
    timeline_events = []
    timeline_data = session.get('timeline_data', {})
    changes_data = session.get('changes_data', [])
    
    if timeline_data.get('when_started'):
        timeline_events.append({
            "period": timeline_data['when_started'],
            "event": "Initial behavioral changes detected",
            "type": "start"
        })
    
    for i, change in enumerate(changes_data[:4]):
        timeline_events.append({
            "period": f"Phase {i+1}",
            "event": f"{change.replace('_', ' ').title()} changes observed",
            "type": "development"
        })
    
    # Identify pattern clusters
    signals = session.get('signals', {})
    pattern_clusters = []
    
    if signals.get('digital_behavior', 0) > 0.4 and signals.get('communication_changes', 0) > 0.4:
        pattern_clusters.append("secrecy_escalation")
    if signals.get('emotional_indicators', 0) > 0.5:
        pattern_clusters.append("emotional_disengagement")
    if signals.get('routine_changes', 0) > 0.4 and signals.get('social_behavior', 0) > 0.4:
        pattern_clusters.append("lifestyle_reinvention")
    if signals.get('communication_changes', 0) > 0.3:
        pattern_clusters.append("communication_withdrawal")
    
    return {
        "session_id": session_id,
        "trust_disruption_index": session.get('trust_disruption_index', 0),
        "confidence_level": session.get('confidence_level', 'low'),
        "uncertainty_level": session.get('uncertainty_level', 'high'),
        "hypotheses": session.get('hypotheses', {}),
        "signals": session.get('signals', {}),
        "narrative_consistency": session.get('narrative_consistency', 100),
        "context_estimation": session.get('context_estimation', []),
        "clarity_actions": clarity_actions,
        "timeline_events": timeline_events,
        "pattern_clusters": pattern_clusters,
        "questions_answered": len(session.get('qa_history', []))
    }

@api_router.get("/analysis/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current session status"""
    session = await db.analysis_sessions.find_one(
        {"id": session_id}, {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "current_step": session.get('current_step', 'baseline'),
        "questions_answered": len(session.get('qa_history', [])),
        "trust_disruption_index": session.get('trust_disruption_index', 0)
    }

# Include the router in the main app
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
