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
1. Landing Page with cinematic hero section, rotating background slideshow, CTAs
2. Clarity Moment - Emotional checkpoint before analysis
3. Relationship Pulse - Quick 30-second check with heart stability indicators
4. Deep Analysis 6-step wizard (Baseline, Change Detection, Timeline, Adaptive AI Investigation, Pattern Detection, Diagnostic Report)
5. Results Dashboard with Suspicion Score (0-100) and Trust Disruption Index gauge
6. Mirror Mode - Perception gap analysis
7. Conversation Coach - Guided conversation preparation
8. Privacy-first design (anonymous mode only)

## Design System
- Primary: Deep Blue #0B132B
- Accent: Electric Turquoise #3DD9C5
- Emotional: Coral Red #FF4D6D
- Positive: Soft Mint #6EE7B7
- Warning: Amber #FCA311
- Neutral: Light Silver #E6EDF3
- Typography: Fraunces (headings), Manrope (body), JetBrains Mono (data)
- Style: Cinematic, emotional, elegant analytical dashboard

## What's Been Implemented

### Feb 2026 - Suspicion Score Feature
- Added calculate_suspicion_score() to backend based on changes, signals, hypotheses, timeline, baseline
- Score labels: Low Signal (0-30), Moderate Signal (31-60), Elevated Pattern Risk (61-80), High Pattern Risk (81-100)
- Circular progress ring UI with animated counter (1.2s ease-out)
- Color-coded gradient: green → yellow → orange → red
- Disclaimer text: "This score reflects patterns detected in your answers"
- Integrated as Stage 2 in the progressive reveal sequence on ResultsDashboard

### Feb 2026 - Cinematic Hero Redesign
- Rotating slideshow with 2 custom hero images (6s per image, smooth crossfade)
- Gradient overlay: linear-gradient(rgba(10,15,25,0.55), rgba(10,15,25,0.35))
- Custom TrustLens logo (trustlens-logo.png) in navbar and footer
- Responsive typography with clamp() (headline 38-64px, subheadline 18-22px)
- New copy: "Millions of people question..." / "Sometimes it's..." / "TrustLens helps you interpret the signals"
- "Why TrustLens" section redesigned with 4 blocks: Reality of Infidelity, Why People Miss Signs, What TrustLens Does, Not Accusations Only Clarity

### Jan 2026 - Full MVP Build
- Backend API endpoints (start, pulse, baseline, changes, timeline, evidence, question, answer, mirror, conversation-coach, results, status)
- Frontend pages: LandingPage, ClarityMoment, RelationshipPulse, DeepAnalysis, ResultsDashboard, MirrorMode, ConversationCoach
- AI-powered adaptive questioning (Claude Sonnet 4.5 - MOCKED with fallbacks)
- Results Dashboard with Trust Disruption Index gauge, bento grid visualizations

## Prioritized Backlog

### P0 (Critical) - Completed
- [x] Cinematic hero section with rotating slideshow
- [x] Suspicion Score (0-100) with animated reveal
- [x] Deep Analysis wizard flow
- [x] Results Dashboard with progressive reveal
- [x] Mirror Mode & Conversation Coach

### P1 (Important) - Upcoming
- [ ] Relationship Pulse quick flow refinement
- [ ] Export report as PDF
- [ ] Evidence signals module (expanded)

### P2 (Nice to Have) - Future
- [ ] User accounts (optional authentication)
- [ ] Replace MOCKED AI with real Claude Sonnet 4.5 LLM calls
- [ ] Global Pattern Engine with real anonymized data
- [ ] Mobile app version

## Key API Endpoints
- POST /api/analysis/start - Initialize session
- POST /api/analysis/baseline - Submit baseline data
- POST /api/analysis/changes - Submit change categories
- POST /api/analysis/timeline - Submit timeline data
- GET /api/analysis/{session_id}/results - Full results with suspicion_score and suspicion_label
- GET /api/analysis/{session_id}/question - Get adaptive AI question
- POST /api/analysis/answer - Submit answer
- POST /api/analysis/mirror - Mirror mode
- POST /api/analysis/conversation-coach - Conversation guidance

## Technical Notes
- EMERGENT_LLM_KEY used for Claude Sonnet 4.5
- No user data stored permanently (privacy-first)
- All API routes prefixed with /api
- AI analysis responses have hardcoded fallbacks
- Suspicion score is deterministic based on user inputs (not AI-generated)
