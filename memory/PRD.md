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

## All Implemented Features

### Core Analysis
- Full multi-step deep analysis with hybrid adaptive question engine
- Calibrated Suspicion Score with pattern comparison (300+ case database)
- AI Narrative Analysis (Claude Sonnet 4.5) with graduated score-based tone system
- Relationship Pulse (quick 3-5 question check-up)

### Advanced Features
- Mirror Mode (Dual Perspective Analysis)
- Conversation Coach with PDF Export
- Optional JWT-based User Accounts
- Enhanced My Analyses Dashboard with signal evolution
- Global Pattern Engine (anonymous contribution)

### Landing Page (March 15, 2026 — Major Visual Overhaul)
- **Hero**: 3-act cinematic slideshow (Woman → Gay couple → Mixed couple) with synchronized text and optimized rhythm (5s/8s/7s)
- **Why TrustLens Exists**: 4 custom AI-generated images representing diversity (hetero, gay, lesbian, mixed-race couples)
- **How It Works**: Minimalist icon cards (MessageCircle, Brain, Sun)
- **Scanner Logo SVG**: Concentric circles with tick marks matching original brand design
- Full-screen images, lighter overlay, cinematic transitions

### Reports & Sharing
- Anonymous shareable link generation
- PDF export with full analysis data

## Deployment — COMPLETE
- Backend: Docker on Render.com (Web Service, Frankfurt)
- Frontend: Static Site on Render.com (Global CDN)
- Database: MongoDB Atlas (M0 Free, Paris region)

## Backlog
- Google Analytics integration (awaiting Measurement ID)
- Custom domain setup
- OpenGraph meta tags for social sharing
- Marketing launch (TikTok/Instagram)

## Changelog
- **March 15, 2026 (Evening)**: Major visual overhaul — 3-act hero, 4 new Why section images, How It Works icons, scanner logo SVG
- **March 15, 2026**: Successfully deployed to Render.com + MongoDB Atlas
- **Feb 2026**: All features implemented and tested (100% pass rate)
