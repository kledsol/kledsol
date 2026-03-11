# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform designed to help users understand behavioral changes and trust dynamics. The goal is not to spy or accuse, but to provide clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture Overview
- **Frontend**: React 19 with Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI with Python
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports)
- **AI Integration**: Claude Sonnet 4.5 via emergentintegrations (with hardcoded fallbacks)

## What's Been Implemented

### Feb 2026 - Share Anonymized Report
- POST /api/reports/share stores anonymized report snapshot (no personal data)
- GET /api/reports/{report_id} retrieves shared report
- SharedReport.jsx page at /report/:reportId with score ring, pattern comparison, perception consistency, clarity actions, perspective, disclaimer
- Share button on results page (Stage 11) generates unique URL + copies to clipboard
- Mobile-optimized layout, 404 handling for invalid links

### Feb 2026 - Core Analytical Experience
- 4-step dramatic analysis sequence (animated icons + progress bar, ~5s total)
- Enhanced Pattern Comparison ("compared with thousands" copy + disclaimer)
- Perception Consistency Check (micro-contradiction detection)
- Relationship Timeline (score history in MongoDB + line chart)

### Feb 2026 - Suspicion Score & Hero
- Suspicion Score 0-100 with circular gauge, animated counter, color-coded labels
- Cinematic hero slideshow (2 custom images, 6s crossfade, gradient overlay)
- Custom TrustLens logo, responsive clamp() typography
- "Why TrustLens" section with 4 clarity blocks

### Jan 2026 - Full MVP
- All API endpoints, frontend pages, AI adaptive questioning with fallbacks
- Results Dashboard with progressive reveal (11 stages)
- Mirror Mode, Conversation Coach, Relationship Pulse

## Prioritized Backlog

### P1 - Upcoming
- [ ] Relationship Pulse quick flow refinement
- [ ] Export report as PDF
- [ ] Evidence signals module (expanded)

### P2 - Future
- [ ] User accounts (optional auth)
- [ ] Replace AI fallbacks with real-time Claude Sonnet 4.5
- [ ] Global Pattern Engine with real anonymized data

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /mirror, /conversation-coach
- GET /api/analysis/{session_id}/results, /question, /status
- POST /api/reports/share → returns report_id
- GET /api/reports/{report_id} → anonymized report
- GET/POST /api/timeline-history → score tracking
