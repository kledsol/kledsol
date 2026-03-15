# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF), passlib + python-jose (JWT auth)
- **Database**: MongoDB Atlas (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions, users, signal_snapshots)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)
- **Deployment**: Render.com (Backend Web Service + Frontend Static Site) + MongoDB Atlas

## Production URLs
- **Frontend**: https://trustlens-axq5.onrender.com
- **Backend API**: https://trustlens-api-hawl.onrender.com

## All Implemented Features (Tested & Working)

### Core Analysis
- Full multi-step deep analysis: baseline → changes → timeline → adaptive questions → results
- Hybrid Adaptive Question Engine: 5 core deterministic + up to 3 AI follow-ups
- Calibrated Suspicion Score with pattern comparison (300+ case database)
- AI Narrative Analysis (Claude Sonnet 4.5) with graduated score-based tone system
- Perception Consistency Check
- Signal Strength Summary (Strong/Moderate/Weak grouping)
- Relationship Pulse (quick 3-5 question check-up)

### Enhanced Demographic Filtering
- Optional age_range and cohabitation_status fields in baseline
- Multi-dimensional filtering with graceful fallback (min 8 samples)

### Global Pattern Engine
- POST /api/cases/contribute-from-session — anonymized data contribution
- GET /api/cases/stats — total/contributed/seeded counts
- Frontend contribution prompt in ResultsDashboard

### Mirror Mode (Dual Perspective)
- Two partners independently complete analyses
- Consent-driven comparison report with perception gap analysis

### Conversation Coach
- AI-guided conversation preparation with full analysis context
- PDF Export capability

### User Accounts & Tracking
- Optional JWT-based auth, anonymous by default
- Enhanced My Analyses Dashboard with score comparison and signal evolution

### Landing Page
- Cinematic dark theme with emotional narrative
- 2x2 card grid "Why TrustLens" section
- Trust○Lens logo with circular lens icon

### Reports & Sharing
- Anonymous shareable link generation
- PDF export with full analysis data

## Deployment (March 15, 2026) — COMPLETE
- Backend: Docker on Render.com (Web Service, Free tier, Frankfurt)
- Frontend: Static Site on Render.com (Global CDN)
- Database: MongoDB Atlas (M0 Free, Paris region)
- All deployment files: Dockerfile, render.yaml, .env.example, .gitignore, DEPLOYMENT_GUIDE.md (with custom domain instructions)
- Rewrite rule configured for SPA routing

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /pulse
- POST /api/analysis/conversation-coach, /conversation-coach/pdf
- GET /api/analysis/{id}/question, /results, /status
- GET /api/health (health check)
- POST /api/auth/register, /login, /link-analysis
- GET /api/auth/me, /my-analyses, /signal-trends/{id}
- POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
- POST /api/cases/contribute-from-session, GET /api/cases/stats

## Backlog — EMPTY
All planned features have been implemented, tested, and deployed to production.

## Changelog
- **March 15, 2026**: Successfully deployed to Render.com + MongoDB Atlas. App is live!
- **Feb 2026**: All features implemented and tested (100% pass rate)
