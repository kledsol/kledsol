# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform designed to help users understand behavioral changes and trust dynamics. The goal is not to spy or accuse, but to provide clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture Overview
- **Frontend**: React 19 with Tailwind CSS, Framer Motion animations, Fraunces/Manrope fonts
- **Backend**: FastAPI with Python
- **Database**: MongoDB (single-session, privacy-focused)
- **AI Integration**: Claude Sonnet 4.5 via emergentintegrations library (currently MOCKED)

## User Personas
1. **Primary User**: Adults experiencing relationship uncertainty seeking clarity through analytical, psychology-driven insights without accusations
2. **Use Case**: Users who notice behavioral changes in their partner and want to understand potential causes through empathetic analysis

## Core Requirements (Static)
1. Landing Page with TrustLens logo, cinematic hero section, CTAs
2. Clarity Moment - Emotional checkpoint before analysis
3. Relationship Pulse - Quick 30-second check with heart stability indicators
4. Deep Analysis 6-step wizard:
   - Baseline (duration, satisfaction, communication, emotional closeness, transparency)
   - Change Detection (7 categories)
   - Timeline Reconstruction
   - Adaptive AI Investigation
   - Pattern Detection
   - Diagnostic Report
5. Results Dashboard with Trust Disruption Index 0-100 gauge
6. Mirror Mode - Perception gap analysis
7. Conversation Coach - Guided conversation preparation
8. Privacy-first design (anonymous mode only)

## Design System
- Primary: Deep Blue #14213D / #0B132B
- Accent: Electric Turquoise #3DD9C5
- Emotional: Coral Red #FF4D6D
- Positive: Soft Mint #7BD389
- Neutral: Light Silver #F5F7FA
- Typography: Fraunces (headings), Manrope (body), JetBrains Mono (data)
- Style: Cinematic, emotional, elegant analytical dashboard

## What's Been Implemented

### Feb 2026 - Cinematic Hero Section
- Rotating background slideshow with 2 custom images (8s per image, crossfade)
- Dark overlay (#0B132B at 65% opacity)
- Custom TrustLens logo (trustlens-logo.png) in navbar and footer
- Improved mobile typography (responsive text sizes)
- Left-aligned, vertically centered text block

### Jan 2026 - Full MVP Build
- Backend API endpoints (start, pulse, baseline, changes, timeline, evidence, question, answer, mirror, conversation-coach, results, status)
- Frontend pages: LandingPage, ClarityMoment, RelationshipPulse, DeepAnalysis, ResultsDashboard, MirrorMode, ConversationCoach
- AI-powered adaptive questioning (Claude Sonnet 4.5 - MOCKED)
- Results Dashboard with Trust Disruption Index gauge, bento grid visualizations

## Prioritized Backlog

### P0 (Critical) - Completed
- [x] Landing page with cinematic hero section and design system
- [x] Clarity Moment emotional checkpoint
- [x] Relationship Pulse with heart indicators
- [x] Deep Analysis wizard flow
- [x] AI-powered adaptive questioning (MOCKED)
- [x] Results Dashboard with Trust Index gauge
- [x] Mirror Mode perception analysis
- [x] Conversation Coach

### P1 (Important) - Upcoming
- [ ] Implement real "Relationship Pulse" quick flow refinement
- [ ] Long-term relationship timeline tracking
- [ ] Evidence signals module (expanded)
- [ ] Post-conversation feedback analysis
- [ ] Export report as PDF

### P2 (Nice to Have) - Future
- [ ] User accounts (optional authentication)
- [ ] Analysis history tracking
- [ ] Replace MOCKED AI with real Claude Sonnet 4.5 LLM calls
- [ ] Global Pattern Engine with real anonymized data
- [ ] Mobile app version

## Key API Endpoints
- POST /api/analysis/start - Initialize session (pulse or deep)
- POST /api/analysis/pulse - Quick pulse check
- POST /api/analysis/baseline - Submit baseline data
- POST /api/analysis/changes - Submit change categories
- POST /api/analysis/timeline - Submit timeline data
- POST /api/analysis/evidence - Submit evidence signals
- GET /api/analysis/{session_id}/question - Get adaptive AI question
- POST /api/analysis/answer - Submit answer with AI analysis
- POST /api/analysis/mirror - Mirror mode perception analysis
- POST /api/analysis/conversation-coach - Get conversation guidance
- GET /api/analysis/{session_id}/results - Full analysis results
- GET /api/analysis/{session_id}/status - Session status

## Technical Notes
- EMERGENT_LLM_KEY used for Claude Sonnet 4.5
- No user data stored permanently (privacy-first)
- All API routes prefixed with /api
- Pattern statistics simulated for MVP
- AI analysis responses are currently MOCKED in server.py
