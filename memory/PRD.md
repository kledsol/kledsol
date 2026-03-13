# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF), passlib + python-jose (JWT auth)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions, users, signal_snapshots)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## All Implemented Features (Tested & Working)

### Core Analysis
- Full multi-step deep analysis: baseline → changes → timeline → adaptive questions → results
- Hybrid Adaptive Question Engine: 5 core deterministic + up to 3 AI follow-ups
- Calibrated Suspicion Score with pattern comparison (300+ case database)
- AI Narrative Analysis (Claude Sonnet 4.5)
- Perception Consistency Check
- Signal Strength Summary (Strong/Moderate/Weak grouping)
- Relationship Pulse (quick 3-5 question check-up)

### Enhanced Demographic Filtering
- Optional age_range (18-25, 25-35, 35-45, 45-55, 55+) and cohabitation_status (living_together, living_apart, part_time) fields in baseline
- Multi-dimensional filtering: duration + cohabitation + age_range with graceful fallback (min 8 samples)
- Frontend selectors in baseline form

### Global Pattern Engine
- POST /api/cases/contribute-from-session — auto-extracts anonymized data from completed sessions
- GET /api/cases/stats — returns total/contributed/seeded counts
- Frontend "Help Others Gain Clarity" prompt in ResultsDashboard after stage 12
- Outcome selection: confirmed_infidelity, emotional_disengagement, misunderstanding, personal_crisis, unresolved_conflict
- Duplicate contribution detection

### Mirror Mode (Dual Perspective)
- Two partners independently complete analyses
- Consent-driven comparison report with perception gap analysis
- Auto-polling (15s) on waiting page

### Conversation Coach
- AI-guided conversation preparation with full analysis context
- Sections: Framing, Opening Lines, Questions, Emotional Preparation, Avoid, Observe
- PDF Export — Download coaching guidance as PDF

### User Accounts & Tracking
- Optional JWT-based auth (email/password), anonymous by default
- Save analysis to account, link post-analysis
- Enhanced My Analyses Dashboard — Score comparison, signal bars with deltas, score evolution chart, dominant pattern, changes badges

### Landing Page
- Centered hero: "Is my partner cheating?" headline, emotional narrative
- Pink CTA (#ff2e8b) "Start Relationship Analysis"
- Desktop side margins with credibility text
- Trust○Lens logo with circular lens icon
- "Why TrustLens Exists" section: 2x2 card grid on solid dark background
- "How It Works" 3-step section, Privacy section, Footer

### Reports & Sharing
- Anonymous shareable link generation
- PDF export with full analysis data
- Shared report viewer

## System Check (Feb 2026) — ALL PASSING
- Backend: 100% (16/16 tests passed)
- Frontend: 100% (all Playwright tests passed)
- Application fully operational and ready for launch

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /pulse
- POST /api/analysis/conversation-coach, /conversation-coach/pdf
- GET /api/analysis/{id}/question, /results, /status
- POST /api/auth/register, /login, /link-analysis
- GET /api/auth/me, /my-analyses, /signal-trends/{id}
- POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
- POST /api/cases/contribute-from-session, GET /api/cases/stats

## Backlog — EMPTY
All planned features have been implemented and tested.
