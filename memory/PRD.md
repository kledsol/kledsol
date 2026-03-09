# TrustLens - Product Requirements Document

## Original Problem Statement
TrustLens is an intelligent relationship analysis platform designed to help users understand behavioral changes and trust dynamics in their relationship. The system analyzes behavioral signals, narrative consistency, contextual factors, and timeline evolution through an adaptive diagnostic engine.

## Architecture Overview
- **Frontend**: React 19 with Tailwind CSS, Framer Motion animations
- **Backend**: FastAPI with Python
- **Database**: MongoDB (single-session, privacy-focused)
- **AI Integration**: OpenAI GPT-5.2 via emergentintegrations library

## User Personas
1. **Primary User**: Adults seeking clarity about relationship dynamics through analytical, non-judgmental behavioral pattern analysis
2. **Use Case**: Users who notice behavioral changes in their partner and want to understand potential causes without accusations

## Core Requirements (Static)
1. Welcome/Landing Page with analysis CTA
2. Relationship Baseline Assessment (duration, quality, communication, emotional connection, transparency, routines)
3. Change Detection (8 categories: routine, communication, emotional, digital, social, intimacy, financial, other)
4. Timeline Reconstruction (when started, gradual/sudden, multiple changes)
5. Adaptive AI Investigation (dynamic questions, hypothesis updates)
6. Results Dashboard (Trust Disruption Index, hypotheses, signals, clarity actions)
7. Dark/Light theme toggle
8. Privacy-first design (no auth, no persistence)

## What's Been Implemented (January 2026)
### Backend API Endpoints
- POST /api/analysis/start - Initialize new session
- POST /api/analysis/baseline - Submit baseline data
- POST /api/analysis/changes - Submit detected changes
- POST /api/analysis/timeline - Submit timeline data
- GET /api/analysis/{session_id}/question - Get next AI question
- POST /api/analysis/answer - Submit answer with AI analysis
- POST /api/analysis/reaction - Track partner reactions
- GET /api/analysis/{session_id}/results - Get full results
- GET /api/analysis/{session_id}/status - Get session status

### Frontend Pages
- WelcomePage.jsx - Hero with features and CTA
- BaselineAssessment.jsx - Multi-field form with sliders
- ChangeDetection.jsx - Interactive category grid
- TimelineReconstruction.jsx - Timeline selection with preview
- AdaptiveInvestigation.jsx - AI questions with answer options
- ResultsDashboard.jsx - Bento grid with visualizations

### AI Features
- GPT-5.2 powered adaptive question generation
- Real-time hypothesis probability updates
- Signal intensity tracking
- Narrative consistency analysis
- Context estimation

## Design System
- Theme: Dark default (#1E2A38), Light available
- Accent: Soft Turquoise (#3AA6A6)
- Typography: Manrope (headings), Inter (body)
- Components: Shadcn/UI + custom cards
- Animations: Framer Motion

## Prioritized Backlog

### P0 (Critical) - Completed ✅
- [x] Core analysis flow (Welcome → Baseline → Changes → Timeline → Investigation → Results)
- [x] AI-powered adaptive questioning
- [x] Trust Disruption Index calculation
- [x] Hypothesis and signal visualization

### P1 (Important)
- [ ] Improve question diversity and depth
- [ ] Add more granular signal tracking
- [ ] Enhanced pattern cluster detection
- [ ] Export analysis report as PDF

### P2 (Nice to Have)
- [ ] Mobile-responsive improvements
- [ ] Accessibility enhancements (ARIA labels)
- [ ] Animation refinements
- [ ] Additional visualization types

## Next Tasks
1. Test complete user flow end-to-end
2. Consider adding more question categories
3. Optional: Add anonymous pattern intelligence network
4. Optional: Long-term relationship tracking with auth

## Technical Notes
- EMERGENT_LLM_KEY used for AI (universal key)
- No user data stored permanently (privacy-first)
- Single session analysis only
- All API routes prefixed with /api
