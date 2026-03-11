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
from seed_cases import generate_all_cases

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

# ============= Startup: Seed Case Database =============

@app.on_event("startup")
async def seed_case_database():
    count = await db.relationship_cases.count_documents({})
    if count < 300:
        logger.info("Seeding relationship case database...")
        await db.relationship_cases.delete_many({})
        cases = generate_all_cases(300)
        await db.relationship_cases.insert_many(cases)
        await db.relationship_cases.create_index("primary_signals")
        await db.relationship_cases.create_index("outcome")
        logger.info(f"Seeded {len(cases)} relationship cases")
    else:
        logger.info(f"Case database already seeded ({count} cases)")

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
    behavioral_changes: int = 3  # 1-5 (noticed behavioral changes)
    trust_feeling: int = 3  # 1-5 (how much you trust partner right now)

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

def calculate_suspicion_score(session: dict, case_match_count: int = 0) -> int:
    """Calculate suspicion score 0-100 using signal intensity, pattern matches,
    micro-contradictions, and timeline consistency."""
    score = 0.0
    
    # 1. Signal intensity from selected change categories (max ~45 pts)
    change_scores = {
        "communication": 8, "emotional_distance": 10, "schedule_changes": 7,
        "phone_secrecy": 12, "intimacy_changes": 8, "financial_changes": 6,
        "social_behavior": 7, "defensive_behavior": 10,
        "late_night_messaging": 8, "unexplained_absences": 10,
    }
    changes = session.get('changes_data') or []
    signal_pts = 0
    for change in changes:
        for key, pts in change_scores.items():
            if key in change.lower().replace(' ', '_'):
                signal_pts += pts
    # Normalize signal intensity to 0-45 range
    score += min(45, signal_pts)
    
    # 2. Pattern match factor from case database (max 20 pts)
    if case_match_count > 0:
        match_factor = min(20, case_match_count * 0.6)
        score += match_factor
    
    # 3. Micro-contradictions detected (max 10 pts)
    baseline = session.get('baseline_data') or {}
    contradictions = 0
    satisfaction = baseline.get('prior_satisfaction', 3)
    transparency = baseline.get('transparency_level', 3)
    closeness = baseline.get('emotional_closeness', 3)
    
    if satisfaction >= 4 and len(changes) >= 4:
        contradictions += 1
    if transparency >= 4 and 'phone_secrecy' in changes:
        contradictions += 1
    if closeness >= 4 and 'emotional_distance' in changes:
        contradictions += 1
    
    timeline = session.get('timeline_data') or {}
    if timeline.get('gradual_or_sudden') == 'gradual' and timeline.get('multiple_at_once'):
        contradictions += 1
    
    score += min(10, contradictions * 3)
    
    # 4. Timeline consistency factor (max 15 pts)
    timeline_pts = 0
    if timeline.get('gradual_or_sudden') == 'sudden':
        timeline_pts += 8
    if timeline.get('multiple_at_once'):
        timeline_pts += 4
    if len(changes) >= 3 and timeline.get('when_started'):
        timeline_pts += 3
    score += min(15, timeline_pts)
    
    # 5. Baseline context modifier (max 10 pts)
    if transparency <= 2:
        score += 5
    if closeness <= 2:
        score += 5
    
    return max(0, min(100, int(round(score))))

def get_suspicion_label(score: int) -> str:
    if score <= 30:
        return "Low Signal"
    if score <= 60:
        return "Moderate Signal"
    if score <= 80:
        return "Elevated Pattern Risk"
    return "High Pattern Risk"

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
    """Fallback simulated statistics (used when DB comparison not available)"""
    trust_erosion = hypotheses.get('trust_erosion', 0)
    emotional_distance = hypotheses.get('emotional_distance', 0)
    avg_severity = (trust_erosion + emotional_distance) / 2
    
    if avg_severity > 0.6:
        return {"confirmed_issues": 67, "relationship_conflict": 21, "resolved_positively": 12}
    elif avg_severity > 0.4:
        return {"confirmed_issues": 42, "relationship_conflict": 35, "resolved_positively": 23}
    elif avg_severity > 0.2:
        return {"confirmed_issues": 23, "relationship_conflict": 38, "resolved_positively": 39}
    else:
        return {"confirmed_issues": 8, "relationship_conflict": 27, "resolved_positively": 65}

async def compare_with_case_database(session: dict) -> dict:
    """Compare user signals against the relationship case database with demographic filtering."""
    changes = session.get('changes_data') or []
    if not changes:
        return {
            "total_cases": 300,
            "matching_cases": 0,
            "match_pct": 0,
            "outcome_breakdown": {},
            "insights": [],
            "similar_case_count": 0,
            "demographic_filtered": False,
        }
    
    # Normalize user signals to match case signal names
    signal_map = {
        "phone_secrecy": "phone_secrecy",
        "emotional_distance": "emotional_distance",
        "schedule_changes": "schedule_inconsistency",
        "defensive_behavior": "defensive_reactions",
        "communication": "communication_decline",
        "intimacy_changes": "reduced_intimacy",
        "financial_changes": "financial_secrecy",
        "social_behavior": "social_withdrawal",
    }
    user_signals = set()
    for c in changes:
        mapped = signal_map.get(c, c)
        user_signals.add(mapped)
    
    # Query cases that share at least one signal
    signal_list = list(user_signals)
    query = {"$or": [
        {"primary_signals": {"$in": signal_list}},
        {"secondary_signals": {"$in": signal_list}},
    ]}
    matching_cases = await db.relationship_cases.find(query, {"_id": 0}).to_list(300)
    
    if not matching_cases:
        return {
            "total_cases": 300,
            "matching_cases": 0,
            "match_pct": 0,
            "outcome_breakdown": {},
            "insights": [],
            "similar_case_count": 0,
            "demographic_filtered": False,
        }
    
    # Score each case by signal overlap
    scored = []
    for case in matching_cases:
        case_signals = set(case.get("primary_signals", []) + case.get("secondary_signals", []))
        overlap = len(user_signals & case_signals)
        total = max(len(user_signals | case_signals), 1)
        similarity = overlap / total
        scored.append((case, similarity))
    
    # Filter to cases with meaningful similarity (>= 30%)
    similar = [(c, s) for c, s in scored if s >= 0.3]
    similar.sort(key=lambda x: x[1], reverse=True)
    
    # --- Demographic filtering ---
    baseline = session.get('baseline_data') or {}
    duration_map = {
        "0-1 years": "0-1 years", "1-3 years": "1-3 years",
        "2-5 years": "3-5 years", "3-5 years": "3-5 years",
        "5-10 years": "5-10 years", "10+ years": "10+ years",
    }
    user_duration = duration_map.get(baseline.get('relationship_duration', ''), '')
    MIN_DEMOGRAPHIC_SAMPLE = 8
    
    demographic_filtered = []
    if user_duration:
        demographic_filtered = [
            (c, s) for c, s in similar
            if c.get("relationship_duration") == user_duration
        ]
    
    used_demographic = len(demographic_filtered) >= MIN_DEMOGRAPHIC_SAMPLE
    analysis_set = demographic_filtered if used_demographic else similar
    demographic_label = f"couples together for {user_duration}" if used_demographic and user_duration else None
    
    # --- Compute outcomes from chosen set ---
    total_similar = len(analysis_set)
    outcome_counts = {}
    for case, _ in analysis_set:
        o = case["outcome"]
        outcome_counts[o] = outcome_counts.get(o, 0) + 1
    
    outcome_pcts = {}
    for o, count in outcome_counts.items():
        outcome_pcts[o] = round(count / total_similar * 100) if total_similar else 0
    
    total_cases_count = await db.relationship_cases.count_documents({})
    
    # --- Generate insights ---
    insights = []
    match_pct = round(len(similar) / max(total_cases_count, 1) * 100)
    outcome_labels = {
        "confirmed_infidelity": "trust was later broken",
        "emotional_disengagement": "emotional disengagement was the root cause",
        "misunderstanding": "the situation was resolved as a misunderstanding",
        "personal_crisis": "a personal crisis was the underlying cause",
        "unresolved_conflict": "ongoing unresolved conflict was identified",
    }
    
    if total_similar > 0:
        top_outcome = max(outcome_counts, key=outcome_counts.get)
        top_pct = outcome_pcts[top_outcome]
        
        if used_demographic and demographic_label:
            insights.append(f"Among {demographic_label}, {top_pct}% of similar cases ended where {outcome_labels.get(top_outcome, top_outcome)}.")
        else:
            insights.append(f"Your situation resembles patterns found in {match_pct}% of documented cases.")
            insights.append(f"In similar cases, {top_pct}% ended with a situation where {outcome_labels.get(top_outcome, top_outcome)}.")
        
        positive_pct = outcome_pcts.get("misunderstanding", 0) + outcome_pcts.get("personal_crisis", 0)
        if positive_pct > 30:
            prefix = f"Among {demographic_label}" if used_demographic and demographic_label else "Notably"
            insights.append(f"{prefix}, {positive_pct}% of similar patterns were later explained by non-infidelity causes.")
    
    # --- Pattern statistics ---
    pattern_stats = {
        "confirmed_issues": outcome_pcts.get("confirmed_infidelity", 0) + outcome_pcts.get("emotional_disengagement", 0),
        "relationship_conflict": outcome_pcts.get("unresolved_conflict", 0),
        "resolved_positively": outcome_pcts.get("misunderstanding", 0) + outcome_pcts.get("personal_crisis", 0),
    }
    total_stats = sum(pattern_stats.values())
    if total_stats > 0 and total_stats != 100:
        for k in pattern_stats:
            pattern_stats[k] = round(pattern_stats[k] / total_stats * 100)
    
    return {
        "total_cases": total_cases_count,
        "matching_cases": len(matching_cases),
        "similar_case_count": len(similar),
        "demographic_sample_size": len(demographic_filtered) if user_duration else 0,
        "demographic_filtered": used_demographic,
        "demographic_label": demographic_label,
        "match_pct": match_pct,
        "outcome_breakdown": outcome_pcts,
        "insights": insights,
        "pattern_statistics": pattern_stats,
    }

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
    
    # Mini suspicion indicator from all 5 questions
    strain_score = (
        (5 - data.emotional_connection) * 6 +
        (5 - data.communication_quality) * 5 +
        data.perceived_tension * 5 +
        data.behavioral_changes * 6 +
        (5 - data.trust_feeling) * 8
    )
    pulse_suspicion = max(0, min(100, int(strain_score * 0.67)))
    
    pulse_data = {
        "emotional_connection": data.emotional_connection,
        "communication_quality": data.communication_quality,
        "perceived_tension": data.perceived_tension,
        "behavioral_changes": data.behavioral_changes,
        "trust_feeling": data.trust_feeling,
        "stability_hearts": stability_hearts,
        "trust_disruption_index": trust_index,
        "pulse_suspicion": pulse_suspicion,
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
    
    # Determine recommendation
    if pulse_suspicion >= 50:
        recommendation = "Your pulse suggests notable relationship strain. We recommend running a full Deep Analysis for a detailed pattern assessment."
    elif pulse_suspicion >= 25:
        recommendation = "Some signals of tension detected. A Deep Analysis could provide more clarity on what might be happening."
    else:
        recommendation = "Your relationship pulse appears healthy. Continue nurturing your bond through open communication."
    
    return {
        "stability_hearts": stability_hearts,
        "trust_disruption_index": trust_index,
        "pulse_suspicion": pulse_suspicion,
        "recommendation": recommendation,
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
    fallback_stats = get_pattern_statistics(hypotheses)
    
    timeline_events = []
    timeline_data = session.get('timeline_data') or {}
    if timeline_data.get('when_started'):
        timeline_events.append({"period": timeline_data['when_started'], "event": "Changes began", "type": "start"})
    
    changes = session.get('changes_data') or []
    for i, change in enumerate(changes[:3]):
        timeline_events.append({"period": f"Phase {i+1}", "event": f"{change.replace('_', ' ').title()}", "type": "development"})
    
    # Compare with relationship case database
    case_comparison = await compare_with_case_database(session)
    
    # Calibrated suspicion score using pattern matches
    suspicion_score = calculate_suspicion_score(session, case_comparison["similar_case_count"])
    suspicion_label = get_suspicion_label(suspicion_score)
    perception_check = detect_perception_inconsistencies(session)
    
    # Use DB-driven stats if available, otherwise fallback
    if case_comparison["similar_case_count"] > 0:
        pattern_stats = case_comparison.get("pattern_statistics", fallback_stats)
        comparison_pct = case_comparison["match_pct"]
    else:
        pattern_stats = fallback_stats
        comparison_pct = min(62, max(12, int(suspicion_score * 0.65 + 5)))
    
    return {
        "session_id": session_id,
        "suspicion_score": suspicion_score,
        "suspicion_label": suspicion_label,
        "trust_disruption_index": session.get('trust_disruption_index', 0),
        "stability_hearts": session.get('stability_hearts', 4),
        "dominant_pattern": session.get('dominant_pattern', 'Insufficient data'),
        "confidence_level": session.get('confidence_level', 'low'),
        "narrative_consistency": session.get('narrative_consistency', 100),
        "hypotheses": hypotheses,
        "signals": signals,
        "pattern_statistics": pattern_stats,
        "pattern_comparison_pct": comparison_pct,
        "case_comparison": {
            "total_cases": case_comparison["total_cases"],
            "similar_case_count": case_comparison["similar_case_count"],
            "demographic_filtered": case_comparison["demographic_filtered"],
            "demographic_label": case_comparison.get("demographic_label"),
            "demographic_sample_size": case_comparison.get("demographic_sample_size", 0),
            "outcome_breakdown": case_comparison["outcome_breakdown"],
            "insights": case_comparison["insights"],
        },
        "perception_consistency": perception_check,
        "context_estimation": session.get('context_estimation', []),
        "clarity_actions": clarity_actions,
        "timeline_events": timeline_events,
        "mirror_mode_data": session.get('mirror_mode_data'),
        "questions_answered": len(session.get('qa_history', [])),
        "trustlens_perspective": generate_perspective(session)
    }

def detect_perception_inconsistencies(session: dict) -> dict:
    """Detect contradictions in user's answers to add analytical depth."""
    inconsistencies = []
    
    baseline = session.get('baseline_data') or {}
    changes = session.get('changes_data') or []
    timeline = session.get('timeline_data') or {}
    
    # High satisfaction but many change categories
    satisfaction = baseline.get('prior_satisfaction', 3)
    if satisfaction >= 4 and len(changes) >= 4:
        inconsistencies.append("You described high prior satisfaction but reported changes across multiple categories.")
    
    # High transparency but phone secrecy selected
    transparency = baseline.get('transparency_level', 3)
    if transparency >= 4 and 'phone_secrecy' in changes:
        inconsistencies.append("You indicated a high level of transparency, yet noted phone secrecy as a recent change.")
    
    # High emotional closeness but emotional distance selected
    closeness = baseline.get('emotional_closeness', 3)
    if closeness >= 4 and 'emotional_distance' in changes:
        inconsistencies.append("You reported strong emotional closeness while also observing emotional distance.")
    
    # Gradual changes but multiple simultaneous categories
    if timeline.get('gradual_or_sudden') == 'gradual' and timeline.get('multiple_at_once'):
        inconsistencies.append("You described the changes as gradual, yet indicated they appeared simultaneously.")
    
    # Good communication but communication changes detected
    comm_habits = baseline.get('communication_habits', '')
    if comm_habits in ['daily', 'frequent'] and 'communication' in changes:
        inconsistencies.append("You described frequent communication habits while noting significant communication changes.")
    
    has_inconsistencies = len(inconsistencies) > 0
    return {
        "has_inconsistencies": has_inconsistencies,
        "inconsistencies": inconsistencies[:3],
        "insight": "We detected inconsistencies in how the situation is described. This often happens when people try to interpret emotionally complex situations." if has_inconsistencies else "Your description of the situation shows internal consistency."
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

@api_router.get("/timeline-history")
async def get_timeline_history():
    """Get stored suspicion scores over time for the relationship timeline."""
    entries = await db.score_timeline.find({}, {"_id": 0}).sort("created_at", 1).to_list(50)
    return {"entries": entries}

@api_router.post("/timeline-history")
async def save_timeline_entry(data: dict):
    """Save a suspicion score entry to the timeline."""
    entry = {
        "score": data.get("score", 0),
        "label": data.get("label", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "date_display": datetime.now(timezone.utc).strftime("%b %d"),
    }
    await db.score_timeline.insert_one(entry)
    return {"status": "saved"}

@api_router.get("/cases/stats")
async def get_case_stats():
    """Get statistics about the relationship case database."""
    total = await db.relationship_cases.count_documents({})
    pipeline = [{"$group": {"_id": "$outcome", "count": {"$sum": 1}}}]
    outcome_agg = await db.relationship_cases.aggregate(pipeline).to_list(10)
    outcomes = {r["_id"]: r["count"] for r in outcome_agg}
    return {"total_cases": total, "outcome_distribution": outcomes}

@api_router.post("/cases/contribute")
async def contribute_anonymized_case(data: dict):
    """Accept an anonymized user story to enrich the case database."""
    required = ["primary_signals", "outcome"]
    if not all(k in data for k in required):
        raise HTTPException(status_code=400, detail="primary_signals and outcome are required")
    
    valid_outcomes = ["confirmed_infidelity", "emotional_disengagement", "misunderstanding", "personal_crisis", "unresolved_conflict"]
    if data["outcome"] not in valid_outcomes:
        raise HTTPException(status_code=400, detail=f"outcome must be one of: {', '.join(valid_outcomes)}")
    
    count = await db.relationship_cases.count_documents({})
    case = {
        "case_id": f"TL-U{count + 1:04d}",
        "relationship_type": data.get("relationship_type", "unknown"),
        "relationship_duration": data.get("relationship_duration", "unknown"),
        "age_range": data.get("age_range", "unknown"),
        "cohabitation": data.get("cohabitation", False),
        "primary_signals": data["primary_signals"],
        "secondary_signals": data.get("secondary_signals", []),
        "timeline": data.get("timeline", "unknown"),
        "micro_contradictions_present": data.get("micro_contradictions_present", False),
        "outcome": data["outcome"],
        "confidence_level": data.get("confidence_level", "moderate"),
        "source": "user_contributed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.relationship_cases.insert_one(case)
    return {"status": "accepted", "case_id": case["case_id"]}

@api_router.get("/reports/{report_id}/pdf")
async def export_report_pdf(report_id: str):
    """Generate a PDF export of a shared report."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import io
    
    report = await db.shared_reports.find_one({"report_id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=25*mm, rightMargin=25*mm, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TLTitle", parent=styles["Title"], fontSize=22, textColor=HexColor("#14213D"), spaceAfter=6*mm)
    heading_style = ParagraphStyle("TLHeading", parent=styles["Heading2"], fontSize=14, textColor=HexColor("#14213D"), spaceAfter=3*mm, spaceBefore=6*mm)
    body_style = ParagraphStyle("TLBody", parent=styles["Normal"], fontSize=11, textColor=HexColor("#333"), leading=16, spaceAfter=3*mm)
    small_style = ParagraphStyle("TLSmall", parent=styles["Normal"], fontSize=9, textColor=HexColor("#666"), leading=13, spaceAfter=2*mm)
    
    elements = []
    
    elements.append(Paragraph("TrustLens Analysis Report", title_style))
    elements.append(Paragraph("Anonymized Relationship Pattern Analysis", small_style))
    elements.append(Spacer(1, 8*mm))
    
    # Suspicion Score
    elements.append(Paragraph("Suspicion Score", heading_style))
    score = report.get("suspicion_score", 0)
    label = report.get("suspicion_label", "")
    elements.append(Paragraph(f"<b>{score}/100</b> — {label}", body_style))
    
    # Dominant Pattern
    pattern = report.get("dominant_pattern", "")
    if pattern and pattern != "Insufficient data":
        elements.append(Paragraph(f"Dominant pattern: {pattern}", body_style))
    
    # Pattern Comparison
    stats = report.get("pattern_statistics")
    pct = report.get("pattern_comparison_pct", 0)
    if stats:
        elements.append(Paragraph("Pattern Comparison", heading_style))
        elements.append(Paragraph(f"Your answers were compared with documented relationship cases. Similar patterns found in {pct}% of cases.", body_style))
        table_data = [
            ["Confirmed Issues", "Unresolved Conflict", "Resolved Positively"],
            [f"{stats.get('confirmed_issues', 0)}%", f"{stats.get('relationship_conflict', 0)}%", f"{stats.get('resolved_positively', 0)}%"],
        ]
        t = Table(table_data, colWidths=[55*mm, 55*mm, 55*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0B132B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 4*mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4*mm),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 3*mm))
    
    # Perception Consistency
    pc = report.get("perception_consistency")
    if pc:
        elements.append(Paragraph("Perception Consistency", heading_style))
        elements.append(Paragraph(pc.get("insight", ""), body_style))
        if pc.get("has_inconsistencies"):
            for inc in pc.get("inconsistencies", []):
                elements.append(Paragraph(f"• {inc}", small_style))
    
    # Clarity Actions
    actions = report.get("clarity_actions", [])
    if actions:
        elements.append(Paragraph("Recommended Actions", heading_style))
        for i, action in enumerate(actions, 1):
            elements.append(Paragraph(f"{i}. {action}", body_style))
    
    # Perspective
    perspective = report.get("trustlens_perspective", "")
    if perspective:
        elements.append(Paragraph("TrustLens Perspective", heading_style))
        elements.append(Paragraph(f"<i>{perspective}</i>", body_style))
    
    # Disclaimer
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("This report was generated using TrustLens relationship pattern analysis. It highlights behavioral patterns and similarities with known relationship situations. It does not prove or confirm infidelity.", small_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    from starlette.responses import StreamingResponse
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=trustlens-report-{report_id}.pdf"}
    )

@api_router.post("/reports/share")
async def create_shared_report(data: dict):
    """Create an anonymized shareable report snapshot."""
    report_id = str(uuid.uuid4())[:12]
    report = {
        "report_id": report_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "suspicion_score": data.get("suspicion_score", 0),
        "suspicion_label": data.get("suspicion_label", ""),
        "pattern_comparison_pct": data.get("pattern_comparison_pct", 0),
        "pattern_statistics": data.get("pattern_statistics"),
        "perception_consistency": data.get("perception_consistency"),
        "clarity_actions": data.get("clarity_actions", [])[:4],
        "dominant_pattern": data.get("dominant_pattern", ""),
        "trustlens_perspective": data.get("trustlens_perspective", ""),
    }
    await db.shared_reports.insert_one(report)
    return {"report_id": report_id}

@api_router.get("/reports/{report_id}")
async def get_shared_report(report_id: str):
    """Fetch a shared anonymized report."""
    report = await db.shared_reports.find_one({"report_id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

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
