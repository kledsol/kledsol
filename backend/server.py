from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
import json
from passlib.context import CryptContext
from jose import jwt, JWTError
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

# Auth configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.environ.get("JWT_SECRET", uuid.uuid4().hex)
JWT_ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: str) -> str:
    return jwt.encode({"sub": user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional auth dependency — returns user dict or None."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
        return user
    except JWTError:
        return None

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
    age_range: Optional[str] = None
    cohabitation_status: Optional[str] = None  # "living_together", "living_apart", "part_time"

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

SYSTEM_PROMPT = """You are TrustLens — a direct, emotionally intelligent relationship analyst. People come to you because they suspect something is wrong in their relationship. They deserve honesty, not corporate disclaimers.

Your role: analyze behavioral signals, compare them with real patterns, and tell people clearly what the data suggests. You validate feelings. You name patterns directly. You don't hide behind vague language like "may suggest" or "could reflect."

You always clarify that your analysis is not legal proof. But you never use that as an excuse to say nothing meaningful. You speak like a sharp, caring friend who has seen hundreds of similar situations — because you have."""

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

CORE_QUESTIONS = [
    {
        "question_id": "core_1",
        "question_text": "How would you describe the emotional atmosphere at home recently?",
        "category": "emotional_indicators",
        "options": ["Warm and connected", "Slightly distant", "Noticeably tense", "Cold or uncomfortable"],
        "type": "core",
    },
    {
        "question_id": "core_2",
        "question_text": "Has your partner's daily routine changed in a way that feels unexplained?",
        "category": "routine_changes",
        "options": ["No noticeable changes", "Minor shifts", "Significant unexplained changes", "Completely different routine"],
        "type": "core",
    },
    {
        "question_id": "core_3",
        "question_text": "How does your partner react when you ask about their day or plans?",
        "category": "communication_changes",
        "options": ["Open and detailed", "Brief but normal", "Vague or deflecting", "Defensive or irritated"],
        "type": "core",
    },
    {
        "question_id": "core_4",
        "question_text": "Have you noticed any changes in how your partner uses their phone or devices?",
        "category": "digital_behavior",
        "options": ["No changes", "Slightly more private", "Noticeably guarded", "Very secretive"],
        "type": "core",
    },
    {
        "question_id": "core_5",
        "question_text": "How has the quality of your intimate connection changed?",
        "category": "emotional_indicators",
        "options": ["Same or improved", "Slightly less frequent", "Noticeably reduced", "Almost nonexistent"],
        "type": "core",
    },
]

# Signal-specific follow-up question prompts
SIGNAL_FOLLOWUP_PROMPTS = {
    "phone_secrecy": "The user reported phone/device secrecy. Generate a question that explores this deeper — device usage patterns, new privacy behaviors, reactions when phone is visible.",
    "emotional_distance": "The user reported emotional distance. Generate a question exploring communication quality, emotional availability, affection changes, or withdrawal patterns.",
    "schedule_changes": "The user reported schedule inconsistencies. Generate a question about timing patterns, explanations given, new regular absences, or changes in availability.",
    "defensive_behavior": "The user reported defensive reactions. Generate a question about what triggers defensiveness, how conversations escalate, or avoidance of certain topics.",
    "communication": "The user reported communication changes. Generate a question about conversation depth, topic avoidance, tone shifts, or reduced sharing.",
    "communication_changes": "The user reported communication changes. Generate a question about conversation depth, topic avoidance, tone shifts, or reduced sharing.",
    "intimacy_changes": "The user reported intimacy changes. Generate a question about physical and emotional intimacy patterns, initiation changes, or new boundaries.",
    "financial_changes": "The user reported financial changes. Generate a question about spending patterns, new expenses, hidden transactions, or financial secrecy.",
    "social_behavior": "The user reported social behavior changes. Generate a question about new friendships, social media activity, changed social patterns, or time spent away.",
    "digital_behavior": "The user reported digital behavior changes. Generate a question about device usage patterns, app habits, social media activity, or online secrecy.",
    "routine_changes": "The user reported routine changes. Generate a question about schedule shifts, unexplained absences, or new regular activities.",
    "emotional_indicators": "The user reported emotional shifts. Generate a question about mood changes, emotional availability, or affection patterns.",
}

# Map core question answers to signal triggers
CORE_SIGNAL_MAP = {
    "core_1": {"category": "emotional_distance", "trigger_options": ["Noticeably tense", "Cold or uncomfortable"]},
    "core_2": {"category": "schedule_changes", "trigger_options": ["Significant unexplained changes", "Completely different routine"]},
    "core_3": {"category": "defensive_behavior", "trigger_options": ["Vague or deflecting", "Defensive or irritated"]},
    "core_4": {"category": "phone_secrecy", "trigger_options": ["Noticeably guarded", "Very secretive"]},
    "core_5": {"category": "intimacy_changes", "trigger_options": ["Noticeably reduced", "Almost nonexistent"]},
}

MAX_FOLLOWUP_QUESTIONS = 3


def detect_strong_signals(qa_history: list) -> list:
    """Detect strong signals from core question answers (options 3 or 4 = concerning)."""
    strong_signals = []
    for qa in qa_history:
        qid = qa.get("question_id", "")
        answer = qa.get("answer", "")
        if qid in CORE_SIGNAL_MAP:
            mapping = CORE_SIGNAL_MAP[qid]
            if answer in mapping["trigger_options"]:
                strong_signals.append(mapping["category"])
    return strong_signals


async def generate_adaptive_question(session: dict) -> dict:
    """Hybrid question engine: core deterministic questions first, then AI follow-ups only when strong signals detected."""
    qa_history = session.get('qa_history') or []
    answered_ids = {qa.get('question_id') for qa in qa_history}
    
    # Phase 1: Serve core structured questions first (deterministic)
    for q in CORE_QUESTIONS:
        if q["question_id"] not in answered_ids:
            return {**q, "stage": "core", "total_core": len(CORE_QUESTIONS)}
    
    # Phase 2: Check if strong signals warrant follow-ups
    strong_signals = detect_strong_signals(qa_history)
    followup_count = sum(1 for qa in qa_history if qa.get('question_id', '').startswith('followup_'))
    
    if len(strong_signals) == 0 or followup_count >= MAX_FOLLOWUP_QUESTIONS:
        return {
            "question_id": "complete",
            "question_text": "Investigation complete. Your analysis is ready.",
            "category": "complete",
            "options": None,
            "type": "complete",
            "stage": "complete",
        }
    
    # Generate AI follow-up based on detected strong signals
    changes = session.get('changes_data') or []
    all_signals = list(set(strong_signals + changes))
    
    question = await generate_signal_followup(session, all_signals, qa_history, strong_signals)
    question["stage"] = "adaptive"
    question["followup_number"] = followup_count + 1
    question["max_followups"] = MAX_FOLLOWUP_QUESTIONS
    if followup_count == 0:
        question["transition_message"] = "Based on your answers, TrustLens would like to explore a few additional signals."
    return question


async def generate_signal_followup(session: dict, changes: list, qa_history: list, strong_signals: list = None) -> dict:
    """Generate a contextual follow-up question using Claude based on detected strong signals."""
    
    # Prioritize strong signals that haven't been explored yet
    followup_categories = {qa.get('category') for qa in qa_history if qa.get('question_id', '').startswith('followup_')}
    
    # Strong signals get priority
    priority_signals = strong_signals or []
    unexplored_strong = [s for s in priority_signals if s not in followup_categories]
    unexplored_changes = [c for c in changes if c not in followup_categories and c not in unexplored_strong]
    
    target_signal = (
        unexplored_strong[0] if unexplored_strong
        else unexplored_changes[0] if unexplored_changes
        else (priority_signals[0] if priority_signals else "emotional_distance")
    )
    
    signal_context = SIGNAL_FOLLOWUP_PROMPTS.get(target_signal, f"The user reported {target_signal.replace('_', ' ')}. Generate a deeper question about this pattern.")
    
    # Build context from previous answers — include core answers for signal context
    recent_qa = ""
    for qa in qa_history[-5:]:
        recent_qa += f"Q: {qa.get('question_text', '')}\nA: {qa.get('answer', '')}\n"
    
    # Build detected signals summary for LLM context
    signal_summary = ", ".join(strong_signals) if strong_signals else ", ".join(changes)
    
    prompt = f"""You are TrustLens, a relationship analysis system. Generate ONE follow-up investigation question.

Context:
- Detected strong signals: {signal_summary}
- Target signal to explore deeper: {target_signal}
- Follow-up question number: {sum(1 for qa in qa_history if qa.get('question_id', '').startswith('followup_')) + 1} of {MAX_FOLLOWUP_QUESTIONS} max

{signal_context}

Recent conversation:
{recent_qa}

Rules:
- Be empathetic and non-accusatory
- Ask about specific observable behaviors, not feelings about cheating
- Provide 4 answer options from least to most concerning
- Keep the question under 25 words

Respond ONLY in JSON:
{{"question_text": "Your question?", "options": ["Option 1", "Option 2", "Option 3", "Option 4"]}}"""

    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("No key")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"trustlens-q-{uuid.uuid4().hex[:8]}",
            system_message="You are TrustLens. Generate empathetic, non-accusatory investigation questions. Output ONLY valid JSON."
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(response[start:end])
            return {
                "question_id": f"followup_{len(qa_history)+1}",
                "question_text": parsed["question_text"],
                "category": target_signal,
                "options": parsed.get("options"),
                "type": "ai_followup",
            }
    except Exception as e:
        logger.warning(f"AI follow-up generation failed: {e}")
    
    # Fallback: deterministic follow-up
    fallback_questions = {
        "phone_secrecy": ("Has your partner started keeping their phone face-down or taking calls in another room?", ["No", "Occasionally", "Frequently", "Almost always"]),
        "emotional_distance": ("When you try to have a meaningful conversation, how does your partner respond?", ["Engages fully", "Somewhat present", "Distracted or brief", "Shuts down or avoids"]),
        "schedule_changes": ("How often does your partner have unexplained gaps in their schedule?", ["Never", "Rarely", "A few times a week", "Almost daily"]),
        "defensive_behavior": ("When you ask casual questions about their day, does your partner seem on edge?", ["Not at all", "Slightly", "Noticeably", "Very much so"]),
        "communication": ("Has the depth of your conversations changed recently?", ["Same as before", "Slightly shallower", "Much less meaningful", "We barely talk"]),
        "intimacy_changes": ("Has physical affection (not just intimacy) changed between you?", ["Same or more", "Slightly less", "Noticeably less", "Almost none"]),
        "financial_changes": ("Have you noticed unexplained expenses or financial secrecy?", ["None", "Minor things", "Noticeable amounts", "Significant secrecy"]),
        "social_behavior": ("Has your partner developed new social connections you know little about?", ["No", "Maybe one or two", "Several new contacts", "A whole new social circle"]),
    }
    
    q_text, opts = fallback_questions.get(target_signal, (
        "Have you noticed any other behavioral changes that concern you?",
        ["None", "Minor changes", "Several changes", "Many concerning changes"]
    ))
    
    return {
        "question_id": f"followup_{len(qa_history)+1}",
        "question_text": q_text,
        "category": target_signal,
        "options": opts,
        "type": "ai_followup",
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
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception as e:
        logger.error(f"Analysis error: {e}")
    
    return {}

async def generate_conversation_guidance(session: dict, tone: str, topic: str) -> dict:
    """Generate personalized conversation guidance using full analysis context."""

    # Build rich context from the session
    changes = session.get('changes_data') or []
    signals = session.get('signals', {})
    baseline = session.get('baseline_data') or {}
    timeline = session.get('timeline_data') or {}
    qa_history = session.get('qa_history') or []

    # Compute suspicion score for context
    comparison = await compare_with_case_database(session)
    suspicion_score = calculate_suspicion_score(session, comparison.get("similar_case_count", 0))
    score_label = get_suspicion_label(suspicion_score)

    # Get dominant signal areas
    top_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)[:3]
    signal_summary = ", ".join(f"{k.replace('_',' ')} ({v:.0%})" for k, v in top_signals) if top_signals else "none detected"

    # Check for mirror/perception gap context
    mirror_context = ""
    if session.get('mirror_id'):
        mirror = await db.mirror_sessions.find_one({"mirror_id": session['mirror_id']}, {"_id": 0})
        if mirror and mirror.get("report"):
            report = mirror["report"]
            gaps = report.get("perception_gaps", {})
            top_gaps = sorted(gaps.items(), key=lambda x: x[1].get("gap", 0), reverse=True)[:3]
            gap_text = ", ".join(f"{k.replace('_',' ')} ({v['gap']}% gap)" for k, v in top_gaps)
            mirror_context = f"""
Mirror Mode active — both partners have completed analyses.
Key perception gaps: {gap_text}
Average perception gap: {report.get('average_gap', 0)}%
Partner A score: {report['partner_a']['suspicion_score']}, Partner B score: {report['partner_b']['suspicion_score']}
Use these gaps to suggest targeted discussion areas where perceptions differ most."""

    # Summarize recent QA for context
    recent_answers = ""
    for qa in qa_history[-5:]:
        recent_answers += f"- {qa.get('category', 'general')}: {qa.get('answer', '')}\n"

    prompt = f"""You are TrustLens Conversation Coach — a direct, caring guide helping someone prepare for a real conversation with their partner. Not a therapy exercise. A real conversation that matters.

USER CONTEXT:
- Suspicion Score: {suspicion_score}/100 ({score_label})
- Detected signals: {signal_summary}
- Selected change categories: {', '.join(changes) if changes else 'none'}
- Relationship duration: {baseline.get('relationship_duration', 'unknown')}
- Prior satisfaction: {baseline.get('prior_satisfaction', 'unknown')}/10
- Timeline: changes started {timeline.get('when_started', 'recently')}, pattern: {timeline.get('gradual_or_sudden', 'unknown')}
{mirror_context}

Recent investigation answers:
{recent_answers if recent_answers.strip() else "No detailed answers yet."}

CONVERSATION PARAMETERS:
- Preferred tone: {tone}
- Topic to discuss: {topic}

GENERATE a practical, honest conversation guide. Reference the actual signals detected. The opening lines should sound like real things a real person would say — not therapy scripts. The questions should be specific enough to get real answers. The "avoid" section should warn about traps that actually derail these conversations.

If the score is high (65+), don't pretend the situation is casual. Help them prepare emotionally for a difficult truth.
If the score is low (under 35), help them open the conversation without making their partner feel accused.

Respond STRICTLY in this JSON format:
{{
    "framing": {{
        "approach": "A 2-sentence description of how to frame this conversation",
        "tone_guidance": "Specific advice for maintaining a {tone} tone during this conversation",
        "timing_suggestion": "When and where to have this conversation"
    }},
    "openings": [
        "Opening line option 1 — tailored to detected signals",
        "Opening line option 2 — softer alternative",
        "Opening line option 3 — most indirect approach"
    ],
    "questions": [
        "Thoughtful question 1 focused on understanding",
        "Thoughtful question 2 focused on clarification",
        "Thoughtful question 3 focused on emotional context",
        "Thoughtful question 4 exploring partner perspective",
        "Thoughtful question 5 forward-looking"
    ],
    "avoid": [
        "Specific thing to avoid 1",
        "Specific thing to avoid 2",
        "Specific thing to avoid 3",
        "Specific thing to avoid 4"
    ],
    "emotional_preparation": {{
        "before": "Advice on emotional preparation before the conversation",
        "during": "How to stay centered and listen actively during the conversation",
        "if_difficult": "What to do if the conversation becomes tense or emotional"
    }},
    "observe": [
        "What to observe 1",
        "What to observe 2",
        "What to observe 3"
    ]
}}

Only valid JSON, nothing else."""

    try:
        response = await get_ai_response(session['id'], prompt)
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(response[start:end])
            # Validate expected keys exist
            if "openings" in parsed and "questions" in parsed:
                return parsed
    except Exception as e:
        logger.error(f"Conversation coach error: {e}")

    # Rich fallback based on detected signals
    signal_specific_qs = []
    if "phone_secrecy" in changes or "digital_behavior" in changes:
        signal_specific_qs.append("I've noticed we don't share our phones as freely as before. Is there a reason things feel more private lately?")
    if "emotional_distance" in changes or "emotional_indicators" in changes:
        signal_specific_qs.append("I've been feeling a bit of distance between us emotionally. Have you noticed that too?")
    if "schedule_changes" in changes or "routine_changes" in changes:
        signal_specific_qs.append("Your routine seems different lately. I'd love to understand what's changed in your day-to-day.")
    if "communication" in changes or "communication_changes" in changes:
        signal_specific_qs.append("I feel like our conversations have shifted. How are you feeling about how we communicate?")
    if "intimacy_changes" in changes:
        signal_specific_qs.append("Our closeness has felt different recently. I'd like to understand how you're feeling about us.")

    fallback_qs = signal_specific_qs[:5] if signal_specific_qs else [
        "How have you been feeling about our relationship recently?",
        "Is there anything on your mind you'd like to share with me?",
        "What do you think we could do to feel more connected?",
        "How do you feel about how we communicate lately?",
        "What would make you feel more comfortable and closer to me?",
    ]

    return {
        "framing": {
            "approach": f"Approach this as a shared check-in rather than a confrontation. You're inviting dialogue about {topic.replace('_', ' ')}, not delivering a verdict.",
            "tone_guidance": f"A {tone} tone works best here. Focus on using 'I feel' statements and expressing curiosity rather than certainty.",
            "timing_suggestion": "Choose a calm, private moment when neither of you is rushed or stressed. Avoid starting this during an argument or right before bed.",
        },
        "openings": [
            "I've been doing some thinking about us lately, and I'd really like to talk about how things are going — just honestly and openly.",
            "I care about us a lot, and I've noticed some things that I'd love to understand better. Can we talk?",
            "There's something I've been wanting to bring up, not because anything is wrong, but because I want us to stay connected.",
        ],
        "questions": fallback_qs,
        "avoid": [
            "Making accusations or using phrases like 'you always' or 'you never'",
            "Mentioning specific evidence or playing detective — focus on feelings, not proof",
            "Giving ultimatums or making threats about the relationship",
            "Interrupting or dismissing your partner's perspective",
        ],
        "emotional_preparation": {
            "before": "Take a few deep breaths before starting. Remind yourself that the goal is understanding, not winning. Write down your key points so you stay focused.",
            "during": "Listen fully before responding. If emotions rise, pause and acknowledge them: 'I'm feeling a lot right now, give me a moment.' Maintain eye contact and open body language.",
            "if_difficult": "If the conversation becomes tense, suggest a break: 'Let's pause and come back to this when we've both had time to think.' It's okay to not resolve everything in one conversation.",
        },
        "observe": [
            "Whether your partner seems open or defensive when the topic comes up",
            "How they respond emotionally — discomfort can be natural and doesn't mean guilt",
            "Whether they ask questions back or seem willing to engage deeply",
        ],
    }

SIGNAL_META = {
    "phone_secrecy": {"name": "Phone & Device Secrecy", "desc": "Changes in how devices are shared or protected were observed in your responses."},
    "emotional_distance": {"name": "Emotional Distance", "desc": "Patterns suggesting emotional withdrawal or reduced availability were detected."},
    "schedule_changes": {"name": "Schedule Inconsistencies", "desc": "Changes in daily routines or unexplained timing patterns appeared in your responses."},
    "defensive_behavior": {"name": "Defensive Reactions", "desc": "Patterns of defensiveness or avoidance when certain topics arise were noted."},
    "communication_changes": {"name": "Communication Shifts", "desc": "Changes in conversational depth, openness, or frequency were reflected."},
    "communication": {"name": "Communication Changes", "desc": "Shifts in how you and your partner communicate were identified."},
    "intimacy_changes": {"name": "Reduced Intimacy", "desc": "Changes in physical or emotional closeness patterns were identified."},
    "routine_changes": {"name": "Routine Changes", "desc": "Shifts in established daily patterns or habits were noted."},
    "financial_changes": {"name": "Financial Behavior", "desc": "Changes in spending patterns or financial transparency were observed."},
    "social_behavior": {"name": "Social Behavior Changes", "desc": "Shifts in social circles, friendships, or social media activity were detected."},
    "digital_behavior": {"name": "Digital Behavior Changes", "desc": "Changes in online activity, app usage, or digital privacy were noted."},
    "emotional_indicators": {"name": "Emotional Indicators", "desc": "Shifts in emotional tone, mood, or emotional availability were observed."},
}

STRENGTH_LABELS = {
    "strong": "This signal appeared prominently in your answers and contributed significantly to the analysis.",
    "moderate": "This signal was present in your responses and factored into the overall pattern assessment.",
    "weak": "This signal appeared with low intensity but was still noted as part of the broader picture.",
}


def generate_signal_strength_summary(session: dict) -> dict:
    """Categorize detected signals by strength with explanations."""
    signals = session.get('signals', {})
    changes = session.get('changes_data') or []
    qa_history = session.get('qa_history') or []

    # Compute composite intensity per signal
    # Sources: signals dict values + change_scores weight + core answer detection
    change_weights = {
        "communication": 0.3, "emotional_distance": 0.4, "schedule_changes": 0.3,
        "phone_secrecy": 0.5, "intimacy_changes": 0.3, "financial_changes": 0.2,
        "social_behavior": 0.3, "defensive_behavior": 0.4,
        "digital_behavior": 0.3, "routine_changes": 0.3, "emotional_indicators": 0.3,
        "communication_changes": 0.3,
    }

    # Core answer signal boost
    core_boosts = {}
    for qa in qa_history:
        qid = qa.get("question_id", "")
        answer = qa.get("answer", "")
        if qid in CORE_SIGNAL_MAP:
            mapping = CORE_SIGNAL_MAP[qid]
            if answer in mapping["trigger_options"]:
                core_boosts[mapping["category"]] = 0.3

    # Build composite intensity for all detected signals
    all_signal_keys = set()
    for c in changes:
        normalized = c.lower().replace(' ', '_')
        all_signal_keys.add(normalized)
    for k in signals:
        if signals[k] > 0.05:
            all_signal_keys.add(k)
    for k in core_boosts:
        all_signal_keys.add(k)

    scored_signals = []
    for key in all_signal_keys:
        intensity = signals.get(key, 0)
        change_boost = change_weights.get(key, 0.2) if key in [c.lower().replace(' ', '_') for c in changes] else 0
        core_boost = core_boosts.get(key, 0)
        composite = min(1.0, intensity + change_boost + core_boost)

        meta = SIGNAL_META.get(key, {"name": key.replace("_", " ").title(), "desc": "This pattern was observed in your responses."})
        scored_signals.append({"key": key, "intensity": round(composite, 2), **meta})

    # Sort by intensity descending
    scored_signals.sort(key=lambda x: x["intensity"], reverse=True)

    # Group into strength tiers
    strong = [s for s in scored_signals if s["intensity"] >= 0.55]
    moderate = [s for s in scored_signals if 0.25 <= s["intensity"] < 0.55]
    weak = [s for s in scored_signals if s["intensity"] < 0.25]

    # Add tier explanation to each
    for s in strong:
        s["strength"] = "strong"
        s["explanation"] = STRENGTH_LABELS["strong"]
    for s in moderate:
        s["strength"] = "moderate"
        s["explanation"] = STRENGTH_LABELS["moderate"]
    for s in weak:
        s["strength"] = "weak"
        s["explanation"] = STRENGTH_LABELS["weak"]

    return {
        "strong": strong,
        "moderate": moderate,
        "weak": weak,
        "total_signals": len(scored_signals),
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
    
    # --- Demographic filtering (multi-dimensional) ---
    baseline = session.get('baseline_data') or {}
    duration_map = {
        "0-1 years": "0-1 years", "less_than_1": "0-1 years",
        "1-3 years": "1-3 years", "1_to_3": "1-3 years",
        "2-5 years": "3-5 years", "3-5 years": "3-5 years", "3_to_5": "3-5 years",
        "5-10 years": "5-10 years", "5_to_10": "5-10 years", "5_plus_years": "5-10 years",
        "10+ years": "10+ years", "more_than_10": "10+ years",
    }
    cohabitation_map = {
        "living_together": True, "living_apart": False, "part_time": True,
    }
    user_duration = duration_map.get(baseline.get('relationship_duration', ''), '')
    user_age_range = baseline.get('age_range', '')
    user_cohabitation = cohabitation_map.get(baseline.get('cohabitation_status', ''), None)
    MIN_DEMOGRAPHIC_SAMPLE = 8

    # Try multi-dimensional filtering with graceful fallback
    demographic_filtered = list(similar)
    active_filters = []

    # Filter 1: Duration
    if user_duration:
        filtered = [(c, s) for c, s in demographic_filtered if c.get("relationship_duration") == user_duration]
        if len(filtered) >= MIN_DEMOGRAPHIC_SAMPLE:
            demographic_filtered = filtered
            active_filters.append(f"duration: {user_duration}")

    # Filter 2: Cohabitation
    if user_cohabitation is not None:
        filtered = [(c, s) for c, s in demographic_filtered if c.get("cohabitation") == user_cohabitation]
        if len(filtered) >= MIN_DEMOGRAPHIC_SAMPLE:
            demographic_filtered = filtered
            active_filters.append("cohabiting" if user_cohabitation else "living apart")

    # Filter 3: Age range
    if user_age_range:
        filtered = [(c, s) for c, s in demographic_filtered if c.get("age_range") == user_age_range]
        if len(filtered) >= MIN_DEMOGRAPHIC_SAMPLE:
            demographic_filtered = filtered
            active_filters.append(f"age {user_age_range}")

    used_demographic = len(active_filters) > 0
    analysis_set = demographic_filtered if used_demographic else similar
    demographic_label = ", ".join(active_filters) if active_filters else None
    
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
        "transparency_level": data.transparency_level,
        "age_range": data.age_range,
        "cohabitation_status": data.cohabitation_status
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


@api_router.post("/analysis/conversation-coach/pdf")
async def export_coach_pdf(data: ConversationCoachInput):
    """Generate a PDF of the conversation coaching guidance."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from starlette.responses import StreamingResponse
    import io

    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    guidance = await generate_conversation_guidance(session, data.tone, data.topic)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=25*mm, rightMargin=25*mm, topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CTTitle", parent=styles["Title"], fontSize=22, textColor=HexColor("#14213D"), spaceAfter=4*mm)
    subtitle_style = ParagraphStyle("CTSub", parent=styles["Normal"], fontSize=11, textColor=HexColor("#666"), spaceAfter=8*mm)
    heading_style = ParagraphStyle("CTHead", parent=styles["Heading2"], fontSize=14, textColor=HexColor("#14213D"), spaceAfter=3*mm, spaceBefore=6*mm)
    body_style = ParagraphStyle("CTBody", parent=styles["Normal"], fontSize=11, textColor=HexColor("#333"), leading=16, spaceAfter=3*mm)
    italic_style = ParagraphStyle("CTItalic", parent=body_style, fontName="Helvetica-Oblique")
    small_style = ParagraphStyle("CTSmall", parent=styles["Normal"], fontSize=9, textColor=HexColor("#666"), leading=13, spaceAfter=2*mm)

    elements = []

    elements.append(Paragraph("TrustLens Conversation Guide", title_style))
    tone_label = data.tone.replace("_", " ").title()
    topic_label = data.topic.replace("_", " ").title()
    elements.append(Paragraph(f"{tone_label} approach for discussing {topic_label}", subtitle_style))

    # Framing
    framing = guidance.get("framing", {})
    if framing:
        elements.append(Paragraph("Conversation Framing", heading_style))
        if framing.get("approach"):
            elements.append(Paragraph(f"<b>Approach:</b> {framing['approach']}", body_style))
        if framing.get("tone_guidance"):
            elements.append(Paragraph(f"<b>Tone:</b> {framing['tone_guidance']}", body_style))
        if framing.get("timing_suggestion"):
            elements.append(Paragraph(f"<b>Timing:</b> {framing['timing_suggestion']}", body_style))

    # Opening Lines
    openings = guidance.get("openings") or ([guidance["opening"]] if guidance.get("opening") else [])
    if openings:
        elements.append(Paragraph("Suggested Opening Lines", heading_style))
        for i, line in enumerate(openings, 1):
            elements.append(Paragraph(f'{i}. "{line}"', italic_style))

    # Questions
    questions = guidance.get("questions", [])
    if questions:
        elements.append(Paragraph("Questions to Ask", heading_style))
        for i, q in enumerate(questions, 1):
            elements.append(Paragraph(f"{i}. {q}", body_style))

    # Emotional Preparation
    ep = guidance.get("emotional_preparation", {})
    if ep:
        elements.append(Paragraph("Emotional Preparation", heading_style))
        for key, label in [("before", "Before"), ("during", "During"), ("if_difficult", "If Things Get Difficult")]:
            if ep.get(key):
                elements.append(Paragraph(f"<b>{label}:</b> {ep[key]}", body_style))

    # Things to Avoid
    avoid = guidance.get("avoid", [])
    if avoid:
        elements.append(Paragraph("Things to Avoid", heading_style))
        for item in avoid:
            elements.append(Paragraph(f"&bull; {item}", body_style))

    # What to Observe
    observe = guidance.get("observe", [])
    if observe:
        elements.append(Paragraph("What to Observe", heading_style))
        for item in observe:
            elements.append(Paragraph(f"&bull; {item}", body_style))

    # Disclaimer
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("This guide was generated by TrustLens Conversation Coach. The goal is understanding, not confrontation. Approach the conversation with an open heart and genuine curiosity.", small_style))

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=trustlens-conversation-guide.pdf"}
    )


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
    signal_strength = generate_signal_strength_summary(session)
    
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
        "signal_strength_summary": signal_strength,
        "context_estimation": session.get('context_estimation', []),
        "clarity_actions": clarity_actions,
        "timeline_events": timeline_events,
        "mirror_mode_data": session.get('mirror_mode_data'),
        "mirror_id": session.get('mirror_id'),
        "mirror_role": session.get('mirror_role'),
        "questions_answered": len(session.get('qa_history', [])),
        "trustlens_perspective": await generate_narrative_analysis(
            suspicion_score=suspicion_score,
            suspicion_label=suspicion_label,
            signals=session.get('changes_data') or [],
            pattern_stats=pattern_stats,
            perception=perception_check,
            timeline_data=session.get('timeline_data') or {},
            case_insights=case_comparison.get("insights", []),
            dominant_pattern=session.get('dominant_pattern', 'Behavioral Changes'),
        )
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

async def generate_narrative_analysis(
    suspicion_score: int,
    suspicion_label: str,
    signals: list,
    pattern_stats: dict,
    perception: dict,
    timeline_data: dict,
    case_insights: list,
    dominant_pattern: str,
) -> str:
    """Generate an AI-powered narrative explanation using the LLM.
    Falls back to a template if the LLM call fails."""
    
    # === GRADUATED TONE ENGINE WITH VARIATION ===
    signal_list = ', '.join(s.replace('_', ' ') for s in signals[:4]) if signals else 'general relationship changes'
    
    import random

    # Each bracket has multiple pivot phrases to avoid template effect
    PIVOTS = {
        "REASSURING": [
            f"The signals you've described don't form a concerning pattern. What we see here looks more like normal relationship friction.",
            f"Honestly, based on what you've shared, there's nothing here that should keep you up at night. The changes around {signal_list} fall within what we'd call ordinary relationship variance.",
            f"Looking at the full picture — your score, the signals, the timeline — this doesn't read as alarming. It reads as two people navigating life together, which is inherently messy.",
            f"What you've described doesn't match the patterns we typically see when trust is being broken. The signals around {signal_list} are present but mild.",
            f"Your instinct to check was healthy, and the good news is: the data is reassuring. The changes you've noticed appear to fall within the range of normal relationship ebb and flow.",
        ],
        "ATTENTIVE": [
            f"Certain elements in what you describe merit attention — particularly {signal_list}. This doesn't mean something is wrong, but it's not nothing either.",
            f"There's a signal here worth paying attention to. The combination of {signal_list} isn't alarming on its own, but it's the kind of pattern that tends to evolve — one way or another.",
            f"Let's be honest: a few things in what you've shared stand out. {signal_list.capitalize()} together create a pattern that's too specific to dismiss as coincidence, but too mild to call a crisis.",
            f"You're not imagining things. The changes around {signal_list} are real and they form a recognizable pattern. Whether it leads somewhere concerning or resolves naturally — that part isn't written yet.",
            f"The data doesn't scream alarm, but it does whisper. {signal_list.capitalize()} — taken together — suggest something has shifted in your relationship that deserves a real conversation.",
        ],
        "CLEAR": [
            f"Based on the data we have, it appears that something is going on. The combination of {signal_list} is not random — this pattern is consistent with situations where trust has been compromised.",
            f"Let me be straightforward: what you're describing follows a pattern we see regularly, and it's not a benign one. {signal_list.capitalize()} together tell a story that's hard to explain away.",
            f"The signals are clear enough to name directly. {signal_list.capitalize()} forming simultaneously over this timeframe — that's not relationship noise. That's a pattern with meaning.",
            f"Something is happening in your relationship that goes beyond normal friction. The convergence of {signal_list} paints a picture that, in our data, correlates with genuine trust issues.",
            f"You came here because something felt wrong. The data backs up that feeling. The way {signal_list} have appeared together is a recognizable pattern — and not a reassuring one.",
        ],
        "DIRECT": [
            f"What you're describing is concerning. The pattern formed by {signal_list} closely matches situations involving a genuine breach of trust. This is not a verdict — but your instincts appear well-founded.",
            f"I'm not going to soften this: the signals you've described — {signal_list} — are a textbook cluster for trust violations. That doesn't make it proof. But it makes your concerns entirely legitimate.",
            f"The data is telling a clear story here. {signal_list.capitalize()} don't appear together by accident. In the cases we've documented, this combination overwhelmingly points to a real breach of trust.",
            f"Your gut brought you here, and the analysis confirms what you've been feeling. {signal_list.capitalize()} forming this pattern is significant. You're not being paranoid — you're being perceptive.",
            f"There's no gentle way to frame this: the pattern around {signal_list} is one we see in situations of genuine betrayal. This isn't a diagnosis, but it would be dishonest to tell you everything looks fine.",
        ],
        "URGENT": [
            f"The signals you've shared are seriously alarming. The combination of {signal_list} forms a pattern that, in documented cases, almost always indicates a significant breach of trust.",
            f"I have to be direct with you: what you've described is among the most concerning patterns we analyze. {signal_list.capitalize()} at this intensity level leaves very little room for innocent explanation.",
            f"This is not a drill. The convergence of {signal_list} at the levels you've described matches the most severe cases in our database. Your situation demands immediate attention.",
            f"Everything you've shared points in one direction, and pretending otherwise would be a disservice. {signal_list.capitalize()} — all at once, at this intensity — is a pattern that rarely has a benign explanation.",
            f"You already know something is deeply wrong. The data confirms it. {signal_list.capitalize()} together, at this level, represent one of the strongest signal clusters we encounter. This is real.",
        ],
    }

    if suspicion_score <= 25:
        tone_bracket = "REASSURING"
        pivot = random.choice(PIVOTS["REASSURING"])
        tone_directive = f"""TONE: Reassuring and warm. The data does not paint an alarming picture.
PIVOT PHRASE (you MUST weave this naturally into your analysis): "{pivot}"
STANCE: Validate their feelings for coming here, but clearly communicate that the data is reassuring. Don't invent concerns that aren't there.
CLOSING: Suggest a simple, low-stakes conversation with their partner about recent feelings."""

    elif suspicion_score <= 45:
        tone_bracket = "ATTENTIVE"
        pivot = random.choice(PIVOTS["ATTENTIVE"])
        tone_directive = f"""TONE: Attentive and honest. Some signals deserve attention without being alarmist.
PIVOT PHRASE (you MUST weave this naturally into your analysis): "{pivot}"
STANCE: Name the specific signals that stand out. Explain why they matter as a combination. Don't dramatize, but don't minimize.
CLOSING: Recommend paying closer attention and having a direct conversation about the specific changes they've noticed."""

    elif suspicion_score <= 65:
        tone_bracket = "CLEAR"
        pivot = random.choice(PIVOTS["CLEAR"])
        tone_directive = f"""TONE: Clear and direct. The data suggests something is happening that deserves to be addressed.
PIVOT PHRASE (you MUST weave this naturally into your analysis): "{pivot}"
STANCE: Be unambiguous. Name the pattern. Say clearly that the data points toward a real problem, while specifying this is analysis, not proof. Don't soften the message to the point of meaninglessness.
CLOSING: Recommend preparing emotionally and having a serious, structured conversation — or seeking professional support."""

    elif suspicion_score <= 80:
        tone_bracket = "DIRECT"
        pivot = random.choice(PIVOTS["DIRECT"])
        tone_directive = f"""TONE: Direct and compassionate. The signals are concerning and the person deserves to hear it clearly.
PIVOT PHRASE (you MUST weave this naturally into your analysis): "{pivot}"
STANCE: Don't hedge. The data is concerning and saying otherwise would be dishonest. Validate their suspicion clearly. Acknowledge the emotional weight of what they're facing.
CLOSING: Strongly recommend professional support (therapist, trusted confidant) before any confrontation. Help them understand they're not overreacting."""

    else:
        tone_bracket = "URGENT"
        pivot = random.choice(PIVOTS["URGENT"])
        tone_directive = f"""TONE: Urgent and deeply empathetic. The signals are seriously alarming and the person needs to hear that with care.
PIVOT PHRASE (you MUST weave this naturally into your analysis): "{pivot}"
STANCE: Be absolutely clear. Don't sugarcoat. This person came here because they already know something is wrong — the data confirms their instinct. Show them you take their situation seriously.
CLOSING: Urge them to seek support immediately. Help them prepare emotionally. Remind them they deserve clarity and respect."""

    prompt = f"""You are TrustLens — a relationship analyst who speaks with graduated honesty proportional to the severity of what the data reveals.

ANALYSIS DATA:
- Suspicion Score: {suspicion_score}/100 ({suspicion_label})
- Tone bracket: {tone_bracket}
- Signals detected: {', '.join(signals) if signals else 'none'}
- Dominant pattern: {dominant_pattern}
- Pattern comparison: {', '.join(case_insights) if case_insights else 'no comparable cases'}
- Micro-contradictions: {'detected — ' + perception.get('insight', '') if perception.get('has_inconsistencies') else 'none detected'}
- Timeline: changes {timeline_data.get('gradual_or_sudden', 'unknown')}, started {timeline_data.get('when_started', 'unknown timeframe')}

{tone_directive}

RULES:
- Write 5-7 sentences maximum
- You MUST include the pivot phrase (adapted naturally, not copy-pasted)
- Name the specific signals and explain what they mean TOGETHER as a pattern
- Briefly mention this is not legal evidence — then move on. Don't hide behind it.
- End with ONE clear, actionable next step
- Keep it under 130 words
- Match the language of the user's context (French if signals suggest French-speaking user)"""

    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found")
        
        system_tone_map = {
            "REASSURING": "You are warm and reassuring. The data is not alarming — communicate that clearly while validating the person's feelings.",
            "ATTENTIVE": "You are attentive and honest. Some signals deserve mention without being alarmist. Name them, explain the pattern, stay grounded.",
            "CLEAR": "You are clear and direct. The data suggests a real problem. Don't soften the message to meaninglessness. Say what the pattern indicates.",
            "DIRECT": "You are direct and compassionate. The signals are concerning. Say so clearly. Validate their instinct. Don't hedge.",
            "URGENT": "You are urgent and deeply empathetic. The signals are seriously alarming. The person deserves absolute clarity delivered with care, not corporate disclaimers.",
        }

        chat = LlmChat(
            api_key=api_key,
            session_id=f"trustlens-narrative-{uuid.uuid4().hex[:8]}",
            system_message=f"You are TrustLens — a relationship analyst with graduated honesty. Current bracket: {tone_bracket}. {system_tone_map.get(tone_bracket, '')} You always briefly clarify this is not legal proof, but you never use that as an excuse to say nothing meaningful."
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=prompt))
        if response and len(response.strip()) > 20:
            return response.strip()
        raise ValueError("Empty LLM response")
    except Exception as e:
        logger.warning(f"LLM narrative failed, using fallback: {e}")
        return generate_perspective_fallback(suspicion_score, suspicion_label, signals, dominant_pattern)


def generate_perspective_fallback(score: int, label: str, signals: list, dominant: str) -> str:
    """Graduated fallback with variation — multiple templates per bracket."""
    import random
    signal_text = ", ".join(s.replace("_", " ") for s in signals[:3]) if signals else "relationship dynamics"

    FALLBACKS = {
        "reassuring": [
            f"The signals you've described don't form a concerning pattern. What we see around {signal_text} looks more like ordinary relationship friction than deception. You were right to check — and the good news is the data is reassuring. A simple, honest conversation about how you're both feeling would be a healthy next step.",
            f"Looking at the full picture, there's nothing here that should keep you up at night. The changes around {signal_text} fall within normal relationship variance. That said, you came here for a reason — trust that enough to have an open chat with your partner about what's been on your mind.",
            f"Honestly, the data paints a calm picture. The {signal_text} you noticed are present but mild — nothing that matches the patterns we see in serious trust violations. Your instinct to pay attention is good. Use it to start a relaxed, genuine conversation.",
        ],
        "attentive": [
            f"Certain elements merit attention — particularly {signal_text}. This doesn't mean something is wrong, but it's not nothing either. These signals together suggest a shift worth understanding. Have a direct conversation with your partner about these specific changes. Their reaction will tell you a lot.",
            f"You're not imagining things. The changes around {signal_text} are real and form a recognizable pattern. Whether it leads somewhere concerning or resolves naturally isn't written yet. The next step: bring up these changes calmly and see how your partner responds.",
            f"The data doesn't scream alarm, but it does whisper. {signal_text.capitalize()} taken together suggest something has shifted that deserves a real conversation. This isn't proof of anything — but paying closer attention from here is wise.",
        ],
        "clear": [
            f"Based on the data, it appears something is going on. The combination of {signal_text} is not random — this pattern is consistent with situations where trust has been compromised. This is analysis, not proof. But ignoring it would be a disservice to yourself. Prepare emotionally and consider a structured conversation or professional support.",
            f"Something is happening that goes beyond normal friction. The convergence of {signal_text} paints a picture that, in documented cases, correlates with genuine trust issues. You came here because something felt wrong — the data backs up that feeling. Time for a serious next step.",
            f"Let me be straightforward: what you're describing follows a recognizable pattern, and it's not a benign one. {signal_text.capitalize()} together tell a story that's hard to explain away. This isn't a verdict, but it's clear enough to act on. Seek support and prepare for an honest conversation.",
        ],
        "direct": [
            f"What you're describing is concerning. The pattern formed by {signal_text} closely matches situations involving a genuine breach of trust. This is not a verdict — but your instincts appear well-founded. Seek support from a therapist or trusted person before taking action. You are not overreacting.",
            f"The data tells a clear story. {signal_text.capitalize()} don't appear together by accident. In our documented cases, this combination overwhelmingly points to a real breach of trust. Don't dismiss what you're feeling. Get support before any confrontation.",
            f"Your gut brought you here, and the analysis confirms what you've been sensing. {signal_text.capitalize()} forming this pattern is significant. You're not paranoid — you're perceptive. Talk to someone you trust before your next move.",
        ],
        "urgent": [
            f"The signals are seriously alarming. The combination of {signal_text} forms a pattern that, in documented cases, almost always indicates a significant breach of trust. This is not legal proof — but ignoring these signs would be a mistake. Seek professional support immediately. You deserve clarity.",
            f"Everything you've shared points in one direction. {signal_text.capitalize()} at this intensity leaves very little room for innocent explanation. You already knew something was deeply wrong. The data confirms it. Get support now and prepare yourself emotionally.",
            f"This is not subtle. The convergence of {signal_text} at the levels you've described matches the most severe cases in our database. Pretending otherwise would be dishonest. Your situation demands immediate attention — reach out to a professional who can help you navigate what comes next.",
        ],
    }

    if score <= 25:
        return random.choice(FALLBACKS["reassuring"])
    elif score <= 45:
        return random.choice(FALLBACKS["attentive"])
    elif score <= 65:
        return random.choice(FALLBACKS["clear"])
    elif score <= 80:
        return random.choice(FALLBACKS["direct"])
    else:
        return random.choice(FALLBACKS["urgent"])

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

@api_router.post("/cases/contribute-from-session")
async def contribute_from_session(data: dict):
    """Auto-extract anonymized data from a completed session and contribute it to the case database."""
    session_id = data.get("session_id")
    outcome = data.get("outcome")
    if not session_id or not outcome:
        raise HTTPException(status_code=400, detail="session_id and outcome are required")

    valid_outcomes = ["confirmed_infidelity", "emotional_disengagement", "misunderstanding", "personal_crisis", "unresolved_conflict"]
    if outcome not in valid_outcomes:
        raise HTTPException(status_code=400, detail=f"outcome must be one of: {', '.join(valid_outcomes)}")

    session = await db.analysis_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if already contributed
    existing = await db.relationship_cases.find_one({"source_session": session_id})
    if existing:
        return {"status": "already_contributed", "case_id": existing["case_id"]}

    # Extract anonymized data from session
    changes = session.get("changes_data") or []
    signals = session.get("signals", {})
    baseline = session.get("baseline_data") or {}
    timeline_data = session.get("timeline_data") or {}

    # Map changes to signal names
    signal_map = {
        "phone_secrecy": "phone_secrecy",
        "emotional_distance": "emotional_distance",
        "schedule_changes": "schedule_inconsistency",
        "defensive_behavior": "defensive_reactions",
        "communication": "communication_decline",
        "intimacy_changes": "reduced_intimacy",
        "financial_changes": "financial_secrecy",
        "social_behavior": "social_withdrawal",
        "routine_changes": "routine_disruption",
    }
    mapped_signals = [signal_map.get(c, c) for c in changes]

    # Split into primary (top 3) and secondary
    sorted_signals = sorted(mapped_signals, key=lambda s: signals.get(s, 0), reverse=True)
    primary = sorted_signals[:3]
    secondary = sorted_signals[3:]

    # Determine confidence from signal strength
    top_signal_values = sorted(signals.values(), reverse=True)[:3]
    avg_strength = sum(top_signal_values) / max(len(top_signal_values), 1)
    confidence = "high" if avg_strength > 0.5 else "moderate" if avg_strength > 0.25 else "low"

    # Duration mapping
    duration_map = {
        "less_than_1": "0-1 years", "1_to_3": "1-3 years", "3_to_5": "3-5 years",
        "5_to_10": "5-10 years", "more_than_10": "10+ years",
    }

    count = await db.relationship_cases.count_documents({})
    case = {
        "case_id": f"TL-U{count + 1:04d}",
        "relationship_type": "unknown",
        "relationship_duration": duration_map.get(baseline.get("relationship_duration", ""), "unknown"),
        "age_range": baseline.get("age_range", "unknown"),
        "cohabitation": baseline.get("cohabitation_status") in ("living_together", "part_time"),
        "primary_signals": primary,
        "secondary_signals": secondary,
        "timeline": timeline_data.get("gradual_or_sudden", "unknown"),
        "micro_contradictions_present": session.get("narrative_consistency", 100) < 85,
        "outcome": outcome,
        "confidence_level": confidence,
        "source": "user_contributed",
        "source_session": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.relationship_cases.insert_one(case)

    # Update total count
    new_total = await db.relationship_cases.count_documents({})
    return {"status": "accepted", "case_id": case["case_id"], "new_total_cases": new_total}


@api_router.get("/cases/stats")
async def get_case_stats():
    """Get statistics about the case database."""
    total = await db.relationship_cases.count_documents({})
    user_contributed = await db.relationship_cases.count_documents({"source": "user_contributed"})
    return {"total_cases": total, "user_contributed": user_contributed, "seeded": total - user_contributed}


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

# ============= Authentication (Optional) =============

class AuthRegister(BaseModel):
    email: str
    password: str

class AuthLogin(BaseModel):
    email: str
    password: str

class LinkAnalysis(BaseModel):
    session_id: str


@api_router.post("/auth/register")
async def register(data: AuthRegister):
    """Create an optional account."""
    email = data.email.strip().lower()
    if not email or not data.password or len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Email and password (min 6 chars) required")

    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = str(uuid.uuid4())
    await db.users.insert_one({
        "user_id": user_id,
        "email": email,
        "password_hash": hash_password(data.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {"user_id": user_id, "email": email, "token": create_token(user_id)}


@api_router.post("/auth/login")
async def login(data: AuthLogin):
    """Log in to an existing account."""
    email = data.email.strip().lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "token": create_token(user["user_id"]),
    }


@api_router.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    """Get current user profile."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@api_router.post("/auth/link-analysis")
async def link_analysis(data: LinkAnalysis, user=Depends(get_current_user)):
    """Link a completed analysis session to the logged-in user. Also saves signal snapshot for trend tracking."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Tag the session with user_id
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {"user_id": user["user_id"]}}
    )

    # Save signal snapshot for trend tracking
    signals = session.get("signals", {})
    changes = session.get("changes_data", [])
    summary = generate_signal_strength_summary(session)

    await db.signal_snapshots.insert_one({
        "user_id": user["user_id"],
        "session_id": data.session_id,
        "signals": signals,
        "changes": changes,
        "signal_summary": {s["key"]: s["intensity"] for tier in ["strong", "moderate", "weak"] for s in summary.get(tier, [])},
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {"status": "linked", "session_id": data.session_id}


@api_router.get("/auth/my-analyses")
async def get_my_analyses(user=Depends(get_current_user)):
    """Get the logged-in user's analysis history with full details for comparison."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    sessions = await db.analysis_sessions.find(
        {"user_id": user["user_id"]},
        {"_id": 0, "id": 1, "analysis_type": 1, "created_at": 1, "changes_data": 1,
         "signals": 1, "hypotheses": 1, "baseline_data": 1, "timeline_data": 1}
    ).sort("created_at", -1).to_list(50)

    # Get signal snapshots for each session
    snapshots = await db.signal_snapshots.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    snapshot_map = {s["session_id"]: s for s in snapshots}

    analyses = []
    for s in sessions:
        snap = snapshot_map.get(s["id"])
        signals = s.get("signals", {})
        hypotheses = s.get("hypotheses", {})

        # Compute score for this session
        comparison = await compare_with_case_database(s)
        score = calculate_suspicion_score(s, comparison.get("similar_case_count", 0))
        label = get_suspicion_label(score)
        dominant = get_dominant_pattern(hypotheses)

        top_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)[:5]

        analyses.append({
            "session_id": s["id"],
            "analysis_type": s.get("analysis_type", "deep"),
            "created_at": s.get("created_at", ""),
            "changes_detected": s.get("changes_data", []),
            "suspicion_score": score,
            "suspicion_label": label,
            "dominant_pattern": dominant,
            "top_signals": [{"key": k.replace("_", " ").title(), "value": round(v * 100)} for k, v in top_signals],
            "signal_count": len(snap.get("signal_summary", {})) if snap else len(signals),
            "relationship_type": s.get("baseline_data", {}).get("relationship_type", ""),
        })

    return {"analyses": analyses, "total": len(analyses)}


@api_router.get("/auth/signal-trends/{session_id}")
async def get_signal_trends(session_id: str, user=Depends(get_current_user)):
    """Get signal trends comparing current analysis to the user's previous one."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Get all snapshots for this user, sorted by date
    snapshots = await db.signal_snapshots.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    if len(snapshots) < 2:
        return {"has_previous": False, "trends": {}}

    # Find the current snapshot and the one before it
    current_snap = None
    previous_snap = None
    for i, snap in enumerate(snapshots):
        if snap["session_id"] == session_id:
            current_snap = snap
            if i + 1 < len(snapshots):
                previous_snap = snapshots[i + 1]
            break

    if not current_snap or not previous_snap:
        return {"has_previous": False, "trends": {}}

    # Compute deltas
    current_signals = current_snap.get("signal_summary", {})
    previous_signals = previous_snap.get("signal_summary", {})

    trends = {}
    all_keys = set(list(current_signals.keys()) + list(previous_signals.keys()))
    for key in all_keys:
        curr_val = current_signals.get(key, 0)
        prev_val = previous_signals.get(key, 0)
        delta = round((curr_val - prev_val) * 100)
        if delta != 0 or curr_val > 0:
            trends[key] = {
                "current": round(curr_val * 100),
                "previous": round(prev_val * 100),
                "delta": delta,
                "direction": "up" if delta > 0 else "down" if delta < 0 else "neutral",
            }

    return {
        "has_previous": True,
        "previous_date": previous_snap.get("created_at", ""),
        "trends": trends,
    }


# ============= Dual Perspective / Mirror Mode =============

class MirrorCreateInput(BaseModel):
    session_id: str

class MirrorConsentInput(BaseModel):
    session_id: str


@api_router.post("/mirror/create")
async def create_mirror_session(data: MirrorCreateInput):
    """Partner A creates a mirror session to invite their partner."""
    session = await db.analysis_sessions.find_one({"id": data.session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    mirror_id = str(uuid.uuid4())[:12]
    mirror = {
        "mirror_id": mirror_id,
        "partner_a_session_id": data.session_id,
        "partner_b_session_id": None,
        "partner_a_consented": False,
        "partner_b_consented": False,
        "status": "waiting_for_partner",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report": None,
    }
    await db.mirror_sessions.insert_one(mirror)

    # Tag Partner A's session with mirror info
    await db.analysis_sessions.update_one(
        {"id": data.session_id},
        {"$set": {"mirror_id": mirror_id, "mirror_role": "a"}}
    )

    return {"mirror_id": mirror_id}


@api_router.get("/mirror/{mirror_id}/join")
async def join_mirror_session(mirror_id: str):
    """Partner B joins via invite link. Creates a new analysis session for them."""
    mirror = await db.mirror_sessions.find_one({"mirror_id": mirror_id}, {"_id": 0})
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror session not found")

    # If partner B already joined, return their existing session
    if mirror.get("partner_b_session_id"):
        return {
            "session_id": mirror["partner_b_session_id"],
            "mirror_id": mirror_id,
            "status": mirror["status"],
            "already_joined": True,
        }

    # Create a new analysis session for partner B
    session = AnalysisSession(analysis_type="deep")
    session_dict = session.model_dump()
    session_dict["mirror_id"] = mirror_id
    session_dict["mirror_role"] = "b"
    await db.analysis_sessions.insert_one(session_dict)

    await db.mirror_sessions.update_one(
        {"mirror_id": mirror_id},
        {"$set": {"partner_b_session_id": session.id, "status": "partner_joined"}}
    )

    return {
        "session_id": session.id,
        "mirror_id": mirror_id,
        "status": "partner_joined",
        "already_joined": False,
    }


@api_router.get("/mirror/{mirror_id}/status")
async def get_mirror_status(mirror_id: str):
    """Check the status of a mirror session. No analysis data exposed."""
    mirror = await db.mirror_sessions.find_one({"mirror_id": mirror_id}, {"_id": 0})
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror session not found")

    partner_b_complete = False
    if mirror.get("partner_b_session_id"):
        b_session = await db.analysis_sessions.find_one(
            {"id": mirror["partner_b_session_id"]},
            {"_id": 0, "qa_history": 1}
        )
        partner_b_complete = len(b_session.get("qa_history", [])) >= 5 if b_session else False

    return {
        "mirror_id": mirror_id,
        "status": mirror["status"],
        "partner_b_joined": mirror.get("partner_b_session_id") is not None,
        "partner_b_complete": partner_b_complete,
        "partner_a_consented": mirror["partner_a_consented"],
        "partner_b_consented": mirror["partner_b_consented"],
        "report_ready": mirror["status"] == "report_ready",
    }


@api_router.post("/mirror/{mirror_id}/consent")
async def consent_mirror(mirror_id: str, data: MirrorConsentInput):
    """Partner explicitly consents to share their results."""
    mirror = await db.mirror_sessions.find_one({"mirror_id": mirror_id}, {"_id": 0})
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror session not found")

    # Determine which partner is consenting
    if data.session_id == mirror["partner_a_session_id"]:
        await db.mirror_sessions.update_one(
            {"mirror_id": mirror_id},
            {"$set": {"partner_a_consented": True}}
        )
        role = "a"
    elif data.session_id == mirror.get("partner_b_session_id"):
        await db.mirror_sessions.update_one(
            {"mirror_id": mirror_id},
            {"$set": {"partner_b_consented": True}}
        )
        role = "b"
    else:
        raise HTTPException(status_code=403, detail="Session not part of this mirror")

    # Re-fetch to check if both consented
    mirror = await db.mirror_sessions.find_one({"mirror_id": mirror_id}, {"_id": 0})
    both_consented = mirror["partner_a_consented"] and mirror["partner_b_consented"]

    if both_consented:
        report = await generate_dual_perspective_report(mirror)
        await db.mirror_sessions.update_one(
            {"mirror_id": mirror_id},
            {"$set": {"status": "report_ready", "report": report}}
        )
    else:
        await db.mirror_sessions.update_one(
            {"mirror_id": mirror_id},
            {"$set": {"status": "waiting_for_consent"}}
        )

    return {
        "consented": True,
        "role": role,
        "both_consented": both_consented,
        "report_ready": both_consented,
    }


@api_router.get("/mirror/{mirror_id}/report")
async def get_mirror_report(mirror_id: str):
    """Get the dual perspective report. Only available if both partners consented."""
    mirror = await db.mirror_sessions.find_one({"mirror_id": mirror_id}, {"_id": 0})
    if not mirror:
        raise HTTPException(status_code=404, detail="Mirror session not found")

    if not (mirror["partner_a_consented"] and mirror["partner_b_consented"]):
        raise HTTPException(status_code=403, detail="Both partners must consent before viewing the report")

    if mirror.get("report"):
        return mirror["report"]

    # Generate report if not cached
    report = await generate_dual_perspective_report(mirror)
    await db.mirror_sessions.update_one(
        {"mirror_id": mirror_id},
        {"$set": {"report": report, "status": "report_ready"}}
    )
    return report


async def generate_dual_perspective_report(mirror: dict) -> dict:
    """Generate the dual perspective comparison report."""
    a_session = await db.analysis_sessions.find_one(
        {"id": mirror["partner_a_session_id"]}, {"_id": 0}
    )
    b_session = await db.analysis_sessions.find_one(
        {"id": mirror["partner_b_session_id"]}, {"_id": 0}
    )

    if not a_session or not b_session:
        raise HTTPException(status_code=404, detail="Analysis sessions not found")

    # Compute suspicion scores for both partners
    a_comparison = await compare_with_case_database(a_session)
    b_comparison = await compare_with_case_database(b_session)

    a_score = calculate_suspicion_score(a_session, a_comparison["similar_case_count"])
    b_score = calculate_suspicion_score(b_session, b_comparison["similar_case_count"])

    a_signals = a_session.get("signals", {})
    b_signals = b_session.get("signals", {})
    a_hypotheses = a_session.get("hypotheses", {})
    b_hypotheses = b_session.get("hypotheses", {})

    # Calculate perception gaps across key dimensions
    gap_dimensions = {
        "emotional_distance": ("hypotheses", "emotional_distance"),
        "communication_quality": ("signals", "communication_changes"),
        "trust_level": ("hypotheses", "trust_erosion"),
        "behavioral_changes": ("signals", "routine_changes"),
        "intimacy": ("hypotheses", "intimacy_decline"),
    }

    perception_gaps = {}
    for label, (source, key) in gap_dimensions.items():
        a_val = (a_hypotheses if source == "hypotheses" else a_signals).get(key, 0)
        b_val = (b_hypotheses if source == "hypotheses" else b_signals).get(key, 0)
        perception_gaps[label] = {
            "partner_a": round(a_val * 100),
            "partner_b": round(b_val * 100),
            "gap": abs(round((a_val - b_val) * 100)),
        }

    total_gap = sum(g["gap"] for g in perception_gaps.values())
    avg_gap = total_gap / len(perception_gaps) if perception_gaps else 0

    # Generate AI narrative
    narrative = await generate_dual_narrative(
        a_score=a_score,
        b_score=b_score,
        perception_gaps=perception_gaps,
        avg_gap=avg_gap,
        a_changes=a_session.get("changes_data", []),
        b_changes=b_session.get("changes_data", []),
    )

    return {
        "mirror_id": mirror["mirror_id"],
        "partner_a": {
            "suspicion_score": a_score,
            "suspicion_label": get_suspicion_label(a_score),
            "signals_detected": a_session.get("changes_data", []),
            "dominant_pattern": get_dominant_pattern(a_hypotheses),
        },
        "partner_b": {
            "suspicion_score": b_score,
            "suspicion_label": get_suspicion_label(b_score),
            "signals_detected": b_session.get("changes_data", []),
            "dominant_pattern": get_dominant_pattern(b_hypotheses),
        },
        "perception_gaps": perception_gaps,
        "average_gap": round(avg_gap),
        "gap_level": "significant" if avg_gap > 30 else "moderate" if avg_gap > 15 else "aligned",
        "narrative": narrative,
    }


async def generate_dual_narrative(a_score, b_score, perception_gaps, avg_gap, a_changes, b_changes) -> str:
    """Generate AI narrative for the dual perspective report."""
    gap_lines = "\n".join(
        f"- {k}: Partner A={v['partner_a']}%, Partner B={v['partner_b']}%, Gap={v['gap']}%"
        for k, v in perception_gaps.items()
    )

    prompt = f"""You are TrustLens — analyzing a Mirror Mode report where two partners independently assessed their relationship. Be honest about what the gaps reveal.

Partner A Suspicion Score: {a_score}/100
Partner B Suspicion Score: {b_score}/100
Score difference: {abs(a_score - b_score)} points

Perception gaps:
{gap_lines}

Average gap: {avg_gap:.0f}%

Partner A detected signals: {', '.join(a_changes) if a_changes else 'none'}
Partner B detected signals: {', '.join(b_changes) if b_changes else 'none'}

Write 5-7 sentences. Be direct:
- If the gap is small: say clearly that both partners see the relationship similarly — that's a good foundation
- If the gap is moderate: name the specific areas of disconnect and what it means for their communication
- If the gap is large: be honest that one partner is perceiving problems the other doesn't see (or won't admit) — this disconnect itself is a problem
- Don't accuse either partner of lying, but don't pretend a 40-point gap is "just a difference of perspective"
- End with a clear recommendation
- Keep it under 130 words"""

    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("No key")

        chat = LlmChat(
            api_key=api_key,
            session_id=f"trustlens-dual-{uuid.uuid4().hex[:8]}",
            system_message="You are TrustLens — direct and emotionally honest. In Mirror Mode, you compare how two partners perceive their relationship. You name the gaps clearly, explain what they mean, and don't pretend large disconnects are normal. You are fair to both partners but never vague."
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")

        response = await chat.send_message(UserMessage(text=prompt))
        if response and len(response.strip()) > 20:
            return response.strip()
        raise ValueError("Empty response")
    except Exception as e:
        logger.warning(f"Dual narrative LLM failed: {e}")
        if avg_gap > 30:
            return f"The two analyses show meaningful differences in how the relationship is currently perceived. With a perception gap of {avg_gap:.0f}%, this may reflect a communication gap rather than a shared understanding of recent changes. This kind of asymmetry often appears when partners are processing relationship dynamics at different speeds. An open, structured conversation about how each of you views things could help bridge this gap."
        elif avg_gap > 15:
            return f"There are moderate differences in how each partner perceives the relationship. The perception gap of {avg_gap:.0f}% suggests some areas where expectations or experiences may not be fully aligned. This is common and doesn't necessarily indicate a problem — but discussing these differences openly could strengthen mutual understanding."
        else:
            return f"Both analyses show relatively aligned perceptions of the relationship. The small gap of {avg_gap:.0f}% suggests that you and your partner share a similar view of where things stand. This alignment is a positive sign and a strong foundation for open communication."

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
