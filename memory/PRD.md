# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform designed to help users understand behavioral changes and trust dynamics through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture Overview
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases)
- **AI Integration**: Claude Sonnet 4.5 via emergentintegrations (with hardcoded fallbacks)

## What's Been Implemented

### Feb 2026 - Relationship Case Database
- 300 generated cases in `relationship_cases` collection (seeded on startup)
- Each case: case_id, relationship_type, duration, age_range, cohabitation, primary/secondary signals, timeline, contradictions, outcome, confidence
- 5 outcomes: confirmed_infidelity, emotional_disengagement, misunderstanding, personal_crisis, unresolved_conflict
- `compare_with_case_database()` matches user signals against cases with >=30% similarity
- Pattern statistics now computed from real case data (not hardcoded)
- Frontend shows dynamic insights: "Your situation resembles patterns found in X% of documented cases"
- GET /api/cases/stats endpoint for database statistics

### Feb 2026 - Share Anonymized Report
- POST /api/reports/share stores anonymized snapshot, GET /api/reports/{id} retrieves it
- SharedReport.jsx page with score ring, pattern comparison, perception, actions, disclaimer

### Feb 2026 - Core Analytical Experience
- 4-step dramatic analysis sequence, perception consistency check, relationship timeline
- Suspicion Score (0-100) with circular gauge, animated counter, color-coded labels
- Cinematic hero slideshow, custom logo, responsive typography, "Why TrustLens" section

### Jan 2026 - Full MVP
- All API endpoints, frontend pages, AI adaptive questioning with fallbacks
- Results Dashboard with progressive 11-stage reveal
- Mirror Mode, Conversation Coach, Relationship Pulse

## Prioritized Backlog

### P1 - Upcoming
- [ ] Relationship Pulse quick flow refinement
- [ ] Export report as PDF
- [ ] Evidence signals module expansion

### P2 - Future
- [ ] User accounts (optional auth)
- [ ] Replace AI fallbacks with real-time Claude Sonnet 4.5
- [ ] Add real anonymized user stories to case database
- [ ] Global Pattern Engine

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /mirror, /conversation-coach
- GET /api/analysis/{session_id}/results (includes case_comparison), /question, /status
- GET /api/cases/stats - Case database statistics
- POST /api/reports/share, GET /api/reports/{id}
- GET/POST /api/timeline-history
