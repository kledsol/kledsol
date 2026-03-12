# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF), passlib + python-jose (JWT auth)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions, users, signal_snapshots)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## Implemented Features

### Landing Page Hero Redesign (Feb 2026)
- Centered headline: "Is my partner cheating?"
- Narrative text with emotional pacing (subtle signs, late nights, locked phone, etc.)
- Pink CTA button (#ff2e8b) "Start Relationship Analysis"
- Reassurance lines: "3-minute analysis" + "Private - Anonymous - No account required"
- Desktop side margins: credibility text ("300+ documented cases") and privacy text
- Hero and content sections fully separated (hero has own relative container)

### "Why TrustLens" Section (Feb 2026)
- Horizontal glass cards (image left, text right on desktop, stacked on mobile)
- 4 blocks: Reality of Infidelity, Why People Miss Signs, What TrustLens Does, Not Accusations Only Clarity
- Solid dark background (#0B132B), no hero image bleed
- Max-width 6xl, centered layout

### User Accounts & Signal Trend Tracking (Mar 2026)
- Optional JWT auth: email + password registration/login, stays anonymous by default
- Endpoints: POST /api/auth/register, /login, GET /me, POST /link-analysis, GET /my-analyses, GET /signal-trends/{session_id}
- Collections: users (user_id, email, password_hash, created_at), signal_snapshots
- Trend tracking: Compares current analysis against previous saved analysis
- My Analyses page at /my-analyses

### Signal Strength Summary (Mar 2026)
- Displays signals grouped by strength: Strong (>=55%), Moderate (25-55%), Weak (<25%)
- Includes trend deltas for logged-in users with previous analyses

### Conversation Coach (Enhanced - Mar 2026)
- AI-powered guidance personalized from full analysis context
- Sections: Framing, Openings, Questions, Emotional Preparation, Avoid, Observe

### Dual Perspective / Mirror Mode (Mar 2026)
- Two partners independently complete analyses, consent to share, get comparison report
- Auto-polling (15s) on waiting page

### Hybrid Adaptive Question Engine (Mar 2026)
- 5 core deterministic questions -> up to 3 AI follow-ups when strong signals detected

### Other Features
- AI Narrative (Claude Sonnet), Pattern Comparison with Demographic Filtering
- 300-case database, Calibrated Suspicion Score, 12-stage progressive reveal
- Relationship Pulse, Share Report, PDF Export

## Prioritized Backlog
### P2 - Future
- [ ] PDF Export for Conversation Coach guidance
- [ ] Enhance "My Analyses" Dashboard
- [ ] Enhanced Demographic Filtering (Phase 2 & 3)
- [ ] Global Pattern Engine (anonymous contributions)

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /pulse, /conversation-coach
- GET /api/analysis/{id}/question, /results (includes signal_strength_summary)
- POST /api/auth/register, /login, /link-analysis, GET /me, /my-analyses, /signal-trends/{id}
- POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf

## System Check Status (Feb 2026)
- Backend: 100% (11/11 tests passed)
- Frontend: 100% (all Playwright tests passed)
- All core APIs operational
- Application confirmed ready for launch
