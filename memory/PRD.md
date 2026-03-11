# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with hardcoded fallbacks)

## Implemented Features

### AI-Powered Narrative Analysis
- Real-time LLM generation via Claude Sonnet 4.5 (Emergent LLM Key)
- LLM receives: suspicion score, signals, pattern stats, contradictions, timeline, case insights
- Generates contextual 4-6 sentence analysis with empathetic, non-accusatory tone
- Template fallback if LLM unavailable (generate_perspective_fallback)
- Suspicion Score and Pattern Comparison remain fully deterministic
- Response time: ~5-7 seconds for narrative generation

### Pattern Comparison with Demographic Filtering
- Compares user signals against 300+ cases with >=30% similarity threshold
- **Phase 1 (current, ~300 cases)**: Filters by relationship duration when sample >= 8
- **Phase 2 (planned, ~500+ cases)**: Add cohabitation status filtering
- **Phase 3 (planned, ~1000+ cases)**: Add age range filtering
- Falls back to full dataset when demographic subset too small (safety rule)
- Generates contextual insights: "Among couples together for 1-3 years, 42% experienced..."

### Relationship Case Database
- 300 synthetic cases seeded on startup (seed=42)
- POST /api/cases/contribute for dataset evolution (user-contributed cases)
- 5 outcomes weighted by severity profile

### Suspicion Score (Calibrated)
- 5-factor calculation: signal intensity (45), pattern matches (20), contradictions (10), timeline (15), baseline (10)
- Circular gauge with animated counter, color-coded labels

### Analysis Experience
- 4-step dramatic analysis sequence, 11-stage progressive reveal
- Perception Consistency Check, Pattern Comparison with case insights + disclaimer
- Relationship Timeline (score history + line chart)

### Relationship Pulse
- 5 questions with mini suspicion indicator (0-100)
- Dynamic recommendation encouraging Deep Analysis

### Share & Export
- Anonymized shareable reports with unique URL
- PDF export via reportlab (GET /api/reports/{id}/pdf)

### UI
- Cinematic hero slideshow, custom logo, responsive typography
- "Why TrustLens" section, dark theme, glass morphism cards

## Prioritized Backlog
### P1 - Upcoming
- [ ] Evidence signals module expansion
- [ ] Post-conversation feedback analysis
### P2 - Future
- [ ] User accounts, real-time LLM, Global Pattern Engine

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /evidence, /answer, /pulse, /mirror, /conversation-coach
- GET /api/analysis/{id}/results (includes case_comparison with demographic_filtered, demographic_label)
- GET /api/cases/stats, POST /api/cases/contribute
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
- GET/POST /api/timeline-history
