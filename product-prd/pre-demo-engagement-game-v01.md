---
title: "Pre-Demo Engagement Game Version 0.1"
category: product-prd
subcategory: demo-experience
source_id: 87f14ecf-184c-4586-98af-082bfa16a7ad
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Pre-Demo Engagement Game Version 0.1

## Overview

Pre-Demo Engagement Game is a short, interactive mini-game shown to students before their demo class. It warms up the student, introduces BrightCHAMPS concepts, and increases demo attendance and engagement rates.

## Problem Statement

Students (and parents) who book a demo class often arrive cold — they haven't interacted with the platform before the session. Demo attendance drops when there's no engagement between booking and class time. A pre-demo game creates a hook that increases show rates.

## Goals & Success Metrics

- Increase demo attendance rate by 5 percentage points
- Increase demo-to-paid conversion rate by 3 percentage points
- Achieve 70% completion rate for students who start the pre-demo game
- Positive qualitative feedback from teachers on student preparedness

## User Stories / Jobs-to-Be-Done

- As a student booked for a demo, I want something fun to do before my class starts
- As a parent, I want my child to be excited and prepared before the demo
- As a teacher, I want the student to arrive with some context about what we'll do together
- As a student, I want to feel accomplished before the class even starts

## Feature Scope

**In Scope:**
- 3-5 minute mini-game (course-appropriate: coding puzzle / math game / quiz)
- Accessible via demo confirmation link (no login required)
- Completion reward: in-class mention or small virtual reward
- Completion data visible to teacher before demo starts

**Out of Scope:**
- Full curriculum content pre-demo (just a teaser)
- Persistent account creation from game completion
- Real-time multiplayer game

## Key Design Decisions

- Game is course-specific (coding demo → block coding puzzle; math demo → number game)
- No login required — accessed via unique token in demo confirmation link
- Game completion signal sent to teacher dashboard (shows "Student completed pre-demo game")
- Game designed to be completable on mobile without installation

## Open Questions / Risks

- What is the right game length to maximize completion without overwhelming?
- Risk: Technical barriers (mobile compatibility, slow connection) may reduce completion
- Dependency: Demo confirmation email/WhatsApp must include game link prominently
- Open: Should game completion affect teacher's demo script/approach?
