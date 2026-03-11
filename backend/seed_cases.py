"""Seed script to generate 300 relationship cases for the TrustLens case database."""
import random
import uuid

SIGNALS = [
    "phone_secrecy", "emotional_distance", "schedule_inconsistency",
    "defensive_reactions", "reduced_intimacy", "late_night_messaging",
    "unexplained_absences", "financial_secrecy", "social_withdrawal",
    "appearance_changes", "communication_decline", "mood_swings",
    "guilt_behavior", "privacy_increase", "routine_disruption",
]

OUTCOMES = [
    "confirmed_infidelity",
    "emotional_disengagement",
    "misunderstanding",
    "personal_crisis",
    "unresolved_conflict",
]

# Outcome weights by severity profile
OUTCOME_PROFILES = {
    "high": {"confirmed_infidelity": 0.40, "emotional_disengagement": 0.25, "unresolved_conflict": 0.20, "personal_crisis": 0.10, "misunderstanding": 0.05},
    "moderate": {"confirmed_infidelity": 0.15, "emotional_disengagement": 0.30, "unresolved_conflict": 0.25, "personal_crisis": 0.18, "misunderstanding": 0.12},
    "low": {"confirmed_infidelity": 0.05, "emotional_disengagement": 0.15, "unresolved_conflict": 0.20, "personal_crisis": 0.25, "misunderstanding": 0.35},
}

RELATIONSHIP_TYPES = ["married", "cohabiting", "dating", "long_distance", "engaged"]
DURATIONS = ["0-1 years", "1-3 years", "3-5 years", "5-10 years", "10+ years"]
AGE_RANGES = ["18-25", "25-35", "35-45", "45-55", "55+"]
COHABITATION = [True, False]
TIMELINES = ["sudden", "gradual", "progressive"]
CONFIDENCE_LEVELS = ["low", "moderate", "high"]


def weighted_choice(weights: dict) -> str:
    items = list(weights.keys())
    probs = list(weights.values())
    return random.choices(items, weights=probs, k=1)[0]


def generate_case(case_num: int) -> dict:
    # Determine signal count (1-7) with bell curve
    signal_count = min(7, max(1, int(random.gauss(3.5, 1.5))))
    primary_count = min(signal_count, random.randint(1, 3))
    secondary_count = signal_count - primary_count

    all_signals = random.sample(SIGNALS, signal_count)
    primary = all_signals[:primary_count]
    secondary = all_signals[primary_count:]

    # Determine severity from signals
    high_severity_signals = {"phone_secrecy", "late_night_messaging", "unexplained_absences", "financial_secrecy", "guilt_behavior"}
    high_count = sum(1 for s in all_signals if s in high_severity_signals)

    if high_count >= 3 or signal_count >= 5:
        severity = "high"
    elif high_count >= 1 or signal_count >= 3:
        severity = "moderate"
    else:
        severity = "low"

    outcome = weighted_choice(OUTCOME_PROFILES[severity])

    # Micro-contradictions more likely in moderate/high severity
    contradiction_prob = {"high": 0.55, "moderate": 0.35, "low": 0.15}
    has_contradictions = random.random() < contradiction_prob[severity]

    # Confidence correlates with signal count
    if signal_count >= 5:
        confidence = random.choices(CONFIDENCE_LEVELS, weights=[0.1, 0.3, 0.6], k=1)[0]
    elif signal_count >= 3:
        confidence = random.choices(CONFIDENCE_LEVELS, weights=[0.2, 0.5, 0.3], k=1)[0]
    else:
        confidence = random.choices(CONFIDENCE_LEVELS, weights=[0.5, 0.4, 0.1], k=1)[0]

    return {
        "case_id": f"TL-{case_num:04d}",
        "relationship_type": random.choice(RELATIONSHIP_TYPES),
        "relationship_duration": random.choice(DURATIONS),
        "age_range": random.choice(AGE_RANGES),
        "cohabitation": random.choice(COHABITATION),
        "primary_signals": primary,
        "secondary_signals": secondary,
        "timeline": random.choice(TIMELINES),
        "micro_contradictions_present": has_contradictions,
        "outcome": outcome,
        "confidence_level": confidence,
    }


def generate_all_cases(count: int = 300) -> list:
    random.seed(42)  # Reproducible dataset
    return [generate_case(i + 1) for i in range(count)]
