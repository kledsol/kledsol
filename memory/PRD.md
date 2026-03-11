# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an AI-powered relationship intelligence platform designed to help users understand behavioral changes and trust dynamics. The goal is not to spy or accuse, but to provide clarity through behavioral pattern analysis, psychological insight, and structured questioning.

## Architecture Overview
- **Frontend**: React 19 with Tailwind CSS, Framer Motion animations, Fraunces/Manrope fonts
- **Backend**: FastAPI with Python
- **Database**: MongoDB (score_timeline collection for timeline history, analysis_sessions for sessions)
- **AI Integration**: Claude Sonnet 4.5 via emergentintegrations library (with hardcoded fallbacks)

## Core Requirements
1. Landing Page with cinematic hero slideshow, CTAs, "Why TrustLens" section
2. Clarity Moment - Emotional checkpoint before analysis
3. Deep Analysis 6-step wizard (Baseline, Changes, Timeline, AI Investigation, Pattern Detection, Report)
4. Dramatic Analysis Sequence (4 animated steps before results reveal)
5. Suspicion Score (0-100) with animated circular gauge and color-coded labels
6. Pattern Comparison with "compared with thousands" copy and disclaimer
7. Perception Consistency Check detecting micro-contradictions
8. Relationship Timeline tracking suspicion scores over time with line chart
9. Mirror Mode & Conversation Coach
10. Privacy-first, anonymous, session-based design

## Design System
- Primary: Deep Blue #0B132B
- Accent: Electric Turquoise #3DD9C5
- Emotional: Coral Red #FF4D6D
- Positive: Soft Mint #6EE7B7
- Warning: Amber #FCA311
- Typography: Fraunces (headings), Manrope (body), JetBrains Mono (data)

## What's Been Implemented

### Feb 2026 - Core Analytical Experience
- 4-step dramatic analysis sequence with animated progress
- Enhanced Pattern Comparison with "thousands of patterns" copy and disclaimer
- Perception Consistency Check detecting contradictory answers
- Relationship Timeline with score history and line chart visualization
- Timeline history stored in MongoDB (score_timeline collection)

### Feb 2026 - Suspicion Score
- Scoring engine based on changes, signals, hypotheses, timeline, baseline
- Circular progress ring with animated counter (1.2s ease-out)
- Color-coded: green (0-30), yellow (31-60), orange (61-80), red (81-100)

### Feb 2026 - Cinematic Hero Redesign
- Rotating slideshow with 2 custom hero images (6s crossfade)
- Gradient overlay, custom TrustLens logo, responsive clamp() typography
- "Why TrustLens" section with 4 clarity blocks

### Jan 2026 - Full MVP Build
- Backend API endpoints, frontend pages, AI adaptive questioning (with fallbacks)
- Results Dashboard with Trust Disruption Index, progressive reveal sequence

## Prioritized Backlog

### P1 (Important) - Upcoming
- [ ] Relationship Pulse quick flow refinement
- [ ] Export report as PDF
- [ ] Evidence signals module (expanded)

### P2 (Nice to Have) - Future
- [ ] User accounts (optional authentication)
- [ ] Replace hardcoded AI fallbacks with real-time Claude Sonnet 4.5 analysis
- [ ] Global Pattern Engine with real anonymized data
- [ ] Mobile app version

## Key API Endpoints
- POST /api/analysis/start - Initialize session
- POST /api/analysis/baseline - Submit baseline data
- POST /api/analysis/changes - Submit change categories
- POST /api/analysis/timeline - Submit timeline data
- GET /api/analysis/{session_id}/results - Full results (suspicion_score, perception_consistency, pattern_comparison_pct, etc.)
- GET /api/timeline-history - Get stored suspicion scores over time
- POST /api/timeline-history - Save a score entry
- GET /api/analysis/{session_id}/question - Adaptive AI question
- POST /api/analysis/answer - Submit answer
- POST /api/analysis/mirror - Mirror mode
- POST /api/analysis/conversation-coach - Conversation guidance
