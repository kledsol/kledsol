# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## Implemented Features

### Dual Perspective Analysis / Mirror Mode (NEW - Mar 2026)
- **Flow**: Partner A completes analysis -> generates private invite link -> Partner B opens link, completes independent analysis -> both explicitly consent -> Dual Perspective Report generated
- **Backend**: 6 new endpoints: POST /api/mirror/create, GET /mirror/{id}/join, GET /mirror/{id}/status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- **New collection**: `mirror_sessions` (mirror_id, partner_a/b_session_id, partner_a/b_consented, status, report)
- **Comparison Report**: Side-by-side suspicion scores, perception gaps (5 dimensions: emotional_distance, communication_quality, trust_level, behavioral_changes, intimacy), AI narrative
- **AI Narrative**: Claude Sonnet 4.5 generates empathetic, non-accusatory perception gap explanation with fallback
- **Privacy**: Report only generated after BOTH partners explicitly consent. Invite link never exposes Partner A's results. Each analysis remains private until consent given
- **Frontend**: /mirror-invite/{mirrorId} (Partner B welcome page), /dual-report/{mirrorId} (comparison report), ResultsDashboard updated with mirror invite section
- **Solo mode remains default** — mirror is fully optional

### Hybrid Adaptive Question Engine (Mar 2026)
- **Stage 1 — Core Deterministic Questions**: 5 fixed questions (core_1 to core_5) served in order, feeding the scoring model
- **Stage 2 — AI-Generated Follow-ups**: Up to 3 contextual follow-up questions by Claude Sonnet 4.5
- **Signal Detection**: Strong signals detected from core answers (options 3/4 = concerning)
- **Trigger Map**: core_1->emotional_distance, core_2->schedule_changes, core_3->defensive_behavior, core_4->phone_secrecy, core_5->intimacy_changes
- **Constraints**: Max 3 follow-ups, only when strong signals detected; LLM generates question text only, does not influence scoring
- **UX**: Stage transition with amber "Adaptive Investigation" banner, AI FOLLOW-UP X/3 badge

### AI-Powered Narrative Analysis
- Real-time LLM generation via Claude Sonnet 4.5 (Emergent LLM Key)
- Suspicion Score and Pattern Comparison remain fully deterministic
- Template fallback if LLM unavailable

### Pattern Comparison with Demographic Filtering
- Compares user signals against 300+ cases with >=30% similarity threshold
- **Phase 1 (current, ~300 cases)**: Filters by relationship duration when sample >= 8
- **Phase 2 (planned, ~500+ cases)**: Add cohabitation status filtering
- **Phase 3 (planned, ~1000+ cases)**: Add age range filtering

### Other Features
- Relationship Case Database (300 synthetic cases)
- Suspicion Score (calibrated, 5-factor)
- Dramatic Analysis Sequence (11-stage progressive reveal)
- Perception Consistency Check, Pattern Comparison
- Relationship Timeline (score history + line chart)
- Relationship Pulse (5-question quick check)
- Share Anonymized Report (unique URL)
- PDF Export (reportlab)
- Cinematic hero slideshow, dark theme

## Prioritized Backlog
### P2 - Upcoming
- [ ] "Conversation Coach" enhancement
### P2 - Future
- [ ] User accounts, Global Pattern Engine
- [ ] Enhanced Demographic Filtering (Phase 2 & 3)

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /evidence, /answer, /pulse
- GET /api/analysis/{id}/question (hybrid: core + adaptive stages)
- GET /api/analysis/{id}/results
- POST /api/mirror/create, GET /api/mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- GET /api/cases/stats, POST /api/cases/contribute
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
- GET/POST /api/timeline-history
