# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## Implemented Features

### Signal Strength Summary (NEW - Mar 2026)
- Displays detected behavioral signals grouped by strength: Strong (>=55%), Moderate (25-55%), Weak (<25%)
- Composite intensity from: signals dict + selected change categories + core answer detection
- Each signal shows: name, intensity bar (animated), percentage, description
- Color-coded: Red (strong), Amber (moderate), Green (weak)
- Non-accusatory: "patterns observed in responses, not conclusions"
- Located at Stage 6 of the progressive reveal in ResultsDashboard

### Conversation Coach (Enhanced - Mar 2026)
- AI-powered guidance personalized from full analysis context
- Sections: Conversation Framing, 2-3 Opening Lines, 3-5 Questions, Emotional Preparation, Things to Avoid, What to Observe
- Uses detected signals, suspicion score, changes, timeline, Mirror Mode gaps

### Dual Perspective Analysis / Mirror Mode (Mar 2026)
- Partner A creates invite -> Partner B completes independent analysis -> Both consent -> Dual Report
- Comparison: side-by-side scores, 5-dimension perception gaps, AI narrative
- Auto-polling (15s) on waiting page
- Privacy: report only after BOTH partners explicitly consent

### Hybrid Adaptive Question Engine (Mar 2026)
- Stage 1: 5 core deterministic questions -> Stage 2: up to 3 AI follow-ups (only when strong signals)

### Other Features
- AI-Powered Narrative Analysis, Pattern Comparison with Demographic Filtering
- Relationship Case Database (300 cases), Calibrated Suspicion Score
- 12-stage progressive reveal, Relationship Pulse, Share Report, PDF Export

## Prioritized Backlog
### P2 - Future
- [ ] Optional User Accounts
- [ ] Enhanced Demographic Filtering (Phase 2 & 3)
- [ ] Global Pattern Engine
- [ ] PDF Export for Conversation Coach guidance

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /answer, /pulse, /conversation-coach
- GET /api/analysis/{id}/question, /results (includes signal_strength_summary)
- POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
