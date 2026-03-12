# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF), passlib + python-jose (JWT auth)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions, users, signal_snapshots)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## Implemented Features

### User Accounts & Signal Trend Tracking (NEW - Mar 2026)
- **Optional JWT auth**: email + password registration/login, stays anonymous by default
- **Endpoints**: POST /api/auth/register, /login, GET /me, POST /link-analysis, GET /my-analyses, GET /signal-trends/{session_id}
- **Collections**: `users` (user_id, email, password_hash, created_at), `signal_snapshots` (signal intensity snapshots per analysis)
- **Trend tracking**: Compares current analysis signal intensities against immediately previous saved analysis
- **Deltas displayed**: TrendingUp (red) for increases, TrendingDown (green) for decreases
- **UX**: Soft save prompt appears only after all results revealed (stage 12). Privacy text: "Optional. Your analysis can still be used anonymously."
- **My Analyses page** at /my-analyses: lists saved analyses with dates, signal counts, and detected changes
- **Landing page**: "My Analyses" nav link appears for logged-in users

### Signal Strength Summary (Mar 2026)
- Displays signals grouped by strength: Strong (>=55%), Moderate (25-55%), Weak (<25%)
- Composite intensity from signals + change categories + core answer detection
- Now includes trend deltas for logged-in users with previous analyses

### Conversation Coach (Enhanced - Mar 2026)
- AI-powered guidance personalized from full analysis context
- Sections: Framing, 2-3 Openings, 3-5 Questions, Emotional Preparation, Avoid, Observe

### Dual Perspective / Mirror Mode (Mar 2026)
- Two partners independently complete analyses, consent to share, get comparison report
- Auto-polling (15s) on waiting page

### Hybrid Adaptive Question Engine (Mar 2026)
- 5 core deterministic questions -> up to 3 AI follow-ups when strong signals detected

### Other Features
- AI Narrative (Claude Sonnet), Pattern Comparison with Demographic Filtering
- 300-case database, Calibrated Suspicion Score, 12-stage progressive reveal
- Relationship Pulse, Share Report, PDF Export

## Recent Changes
### "Why TrustLens" Section Restored (Feb 2026)
- Reverted broken image-based template back to stable 2-column icon+text grid
- Fixed data/template mismatch (rendering expected fields that didn't exist)

## Prioritized Backlog
### P0 - Next
- [ ] Redesign "Why TrustLens" section with new structure, copy, and images (awaiting user direction)

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
