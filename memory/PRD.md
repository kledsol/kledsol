# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF), passlib + python-jose (JWT auth)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions, users, signal_snapshots)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## Implemented Features (All Tested & Working)

### Core Analysis
- Full multi-step deep analysis: baseline → changes → timeline → adaptive questions → results
- Hybrid Adaptive Question Engine: 5 core deterministic + up to 3 AI follow-ups
- Calibrated Suspicion Score with pattern comparison (300+ case database)
- AI Narrative Analysis (Claude Sonnet 4.5)
- Perception Consistency Check
- Signal Strength Summary (Strong/Moderate/Weak grouping)
- Relationship Pulse (quick 3-5 question check-up)

### Mirror Mode (Dual Perspective)
- Two partners independently complete analyses
- Consent-driven comparison report with perception gap analysis
- Auto-polling (15s) on waiting page

### Conversation Coach
- AI-guided conversation preparation with full analysis context
- Sections: Framing, Opening Lines, Questions, Emotional Preparation, Avoid, Observe
- **PDF Export** — Download coaching guidance as PDF

### User Accounts & Tracking
- Optional JWT-based auth (email/password), anonymous by default
- Save analysis to account, link post-analysis
- **Enhanced My Analyses Dashboard** — Score comparison, signal bars with deltas, score evolution chart, dominant pattern display, changes detected badges

### Landing Page
- Centered hero: "Is my partner cheating?" headline, emotional narrative
- Pink CTA (#ff2e8b) "Start Relationship Analysis"
- Desktop side margins with credibility text
- Trust○Lens logo with circular lens icon
- "Why TrustLens Exists" section: 2x2 card grid on solid dark background
- "How It Works" 3-step section, Privacy section, Footer
- Full mobile responsiveness

### Reports & Sharing
- Anonymous shareable link generation
- PDF export with full analysis data
- Shared report viewer

## System Check (Feb 2026) — ALL PASSING
- Backend: 17/17 tests passed (100%)
- Frontend: All Playwright tests passed (100%)
- All core APIs operational
- Application confirmed ready for launch

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /pulse
- POST /api/analysis/conversation-coach, /conversation-coach/pdf
- GET /api/analysis/{id}/question, /results, /status
- POST /api/auth/register, /login, /link-analysis
- GET /api/auth/me, /my-analyses, /signal-trends/{id}
- POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf

## Remaining Backlog
### P3 - Future
- [ ] Enhanced Demographic Filtering (cohabitation status, age range)
- [ ] Global Pattern Engine (anonymous case contributions)
