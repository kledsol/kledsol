# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform providing clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Framer Motion, Fraunces/Manrope fonts
- **Backend**: FastAPI (Python), reportlab (PDF)
- **Database**: MongoDB (analysis_sessions, score_timeline, shared_reports, relationship_cases, mirror_sessions)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (with deterministic fallbacks)

## Implemented Features

### Conversation Coach (Enhanced - Mar 2026)
- **AI-powered guidance** personalized from full analysis context: detected signals, suspicion score, changes, timeline, QA history, and Mirror Mode perception gaps
- **Sections**: Conversation Framing (approach, tone guidance, timing), 2-3 Suggested Opening Lines, 3-5 Thoughtful Questions, Things to Avoid (3-4), Emotional Preparation (before/during/if_difficult), What to Observe
- **Tone options**: gentle, direct, curious, supportive
- **Topic options**: recent changes, feelings, communication, future, trust
- **Non-accusatory**: all guidance focuses on understanding, never confrontation
- **Rich fallback**: signal-specific questions when LLM unavailable

### Dual Perspective Analysis / Mirror Mode (Mar 2026)
- **Flow**: Partner A completes analysis -> generates private invite link -> Partner B opens link, completes independent analysis -> both explicitly consent -> Dual Perspective Report generated
- **Endpoints**: POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- **Comparison Report**: Side-by-side suspicion scores, 5-dimension perception gaps, AI narrative
- **Auto-polling**: 15s interval on waiting page, stops when report ready
- **Privacy**: Report only after BOTH partners explicitly consent

### Hybrid Adaptive Question Engine (Mar 2026)
- Stage 1: 5 core deterministic questions -> Stage 2: up to 3 AI follow-ups (only when strong signals detected)
- LLM generates question text only, does not influence scoring

### Other Features
- AI-Powered Narrative Analysis (Claude Sonnet 4.5)
- Pattern Comparison with Demographic Filtering (Phase 1: duration)
- Relationship Case Database (300 synthetic cases)
- Calibrated Suspicion Score (5-factor)
- Dramatic Analysis Sequence (11-stage reveal)
- Relationship Pulse (5-question quick check)
- Share Anonymized Report, PDF Export
- Cinematic hero slideshow, dark theme

## Prioritized Backlog
### P2 - Future
- [ ] Optional User Accounts (save history across sessions)
- [ ] Enhanced Demographic Filtering (Phase 2: cohabitation at ~500 cases, Phase 3: age at ~1000 cases)
- [ ] Global Pattern Engine (anonymous user contributions)

## Key API Endpoints
- POST /api/analysis/start, /baseline, /changes, /timeline, /evidence, /answer, /pulse
- GET /api/analysis/{id}/question, GET /api/analysis/{id}/results
- POST /api/analysis/conversation-coach (enhanced)
- POST /api/mirror/create, GET /mirror/{id}/join, /status, POST /mirror/{id}/consent, GET /mirror/{id}/report
- POST /api/reports/share, GET /api/reports/{id}, GET /api/reports/{id}/pdf
- GET/POST /api/timeline-history
