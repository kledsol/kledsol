# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab for PDF generation
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with hardcoded fallbacks)

## Implemented Features

### Relationship Case Database
- 300 synthetic cases seeded on startup (seed=42, reproducible)
- Fields: case_id, relationship_type, duration, age_range, cohabitation, primary/secondary signals, timeline, contradictions, outcome, confidence
- 5 outcomes weighted by severity: confirmed_infidelity, emotional_disengagement, misunderstanding, personal_crisis, unresolved_conflict
- compare_with_case_database() matches user signals with >=30% similarity threshold
- Pattern statistics now computed from real case data
- POST /api/cases/contribute for anonymized user story submission (dataset evolution)

### Suspicion Score (Calibrated)
- 5-factor weighted calculation (max 100): signal intensity (45), pattern matches (20), contradictions (10), timeline (15), baseline (10)
- Circular gauge with animated counter, color-coded labels (green/yellow/orange/red)

### Analysis Experience
- 4-step dramatic analysis sequence before results reveal
- 11-stage progressive reveal on ResultsDashboard
- Perception Consistency Check (micro-contradiction detection)
- Pattern Comparison with case database insights and disclaimer
- Relationship Timeline (score history + line chart)

### Relationship Pulse (Enhanced)
- 5 quick questions: emotional connection, communication, tension, behavioral changes, trust
- Mini suspicion indicator (0-100) with recommendation
- CTA to start Deep Analysis

### Share & Export
- POST /api/reports/share creates anonymized snapshot
- SharedReport.jsx page with score ring, patterns, perception, actions
- GET /api/reports/{id}/pdf generates downloadable PDF via reportlab

### Cinematic Hero
- Rotating slideshow (2 custom images, 6s crossfade, gradient overlay)
- Custom TrustLens logo, responsive clamp() typography
- "Why TrustLens" section with 4 clarity blocks

### Core
- Deep Analysis 6-step wizard, Mirror Mode, Conversation Coach
- AI adaptive questioning (Claude Sonnet 4.5 with hardcoded fallbacks)

## Prioritized Backlog

### P1 - Upcoming
- [ ] Evidence signals module expansion
- [ ] Post-conversation feedback analysis

### P2 - Future
- [ ] User accounts (optional auth)
- [ ] Replace AI fallbacks with real-time Claude Sonnet 4.5
- [ ] Add real anonymized user stories to case database
- [ ] Global Pattern Engine
- [ ] Mobile app version

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /evidence, /answer, /pulse, /mirror, /conversation-coach
- GET /api/analysis/{id}/results, /question, /status
- GET /api/cases/stats, POST /api/cases/contribute
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
- GET/POST /api/timeline-history
