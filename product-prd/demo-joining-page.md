---
title: "Demo Joining Page"
category: product-prd
subcategory: demo-experience
source_id: c5354271-f388-4db6-8f44-3bbf384f3664
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Demo Joining Page

## Overview

The Demo Joining Page is a critical touchpoint in the BrightCHAMPS conversion funnel — it is the screen students and parents land on immediately before entering a demo class. It must reduce friction, build confidence, and ensure technical readiness before the live session begins.

## Problem Statement

### Pre-Launch Issues
- Students and parents arrived at demo classes unprepared (poor internet, unfamiliar interface)
- High drop-off rate at the "Join" step due to technical anxiety
- No pre-class context: students didn't know what the class was about or what to expect
- Ops team received excessive "Where is my link?" support queries

## Design Objectives

1. **Technical readiness check** — audio/video test before entering the class
2. **Engagement primer** — give the student something interesting to interact with while waiting
3. **Context setting** — brief overview of what the demo class will cover
4. **Anxiety reduction** — warm, friendly design language; reassuring copy
5. **Parent handover** — ensure parent is aware the class is starting

## Key Design Decisions

### Pre-Join Experience
- **System check:** Automatic test of camera, microphone, and internet connection with clear pass/fail indicators
- **Device preparation tips:** Simple checklist (headphones plugged in, quiet room, tablet charged)
- **Countdown timer:** Visual countdown to class start time reduces "waiting anxiety"

### Engagement While Waiting
- **Pre-Demo Engagement Game:** A lightweight interactive activity (e.g., a simple puzzle or question) that keeps students engaged during the 3–5 minute pre-class window
  - Serves a secondary purpose: surfaces personality data to the teacher before class starts
  - Teacher sees student's pre-class interaction summary in their prep view

### Class Context
- **Teacher introduction card:** Photo, name, brief bio, star rating (from past demo reviews)
- **Lesson teaser:** 1–2 sentences about what the class will cover (creates curiosity)
- **Course overview:** Brief description of the full course the demo is introducing

### Join Flow
1. Parent receives class link (via email/WhatsApp)
2. Opens Demo Joining Page on browser/app
3. System check runs automatically
4. Student completes pre-demo game (optional but encouraged)
5. At T-1 minute: "Join Now" button activates
6. Student enters Zoom/classroom with teacher already in session

## Technical Details

### Integration Points
- Pulls teacher profile data from Teacher Profile service
- Pre-demo game results stored against student profile for teacher view
- Join button triggers Zoom SDK launch (or redirects to Zoom link)
- Real-time slot validation: confirms demo hasn't been cancelled or rescheduled

### Edge Cases
- **Demo cancelled:** Page shows rescheduling options with a friendly message
- **Student joins early:** Waiting room experience with countdown and game
- **Tech failure:** Direct link to support chat if system check fails

## Impact
- Reduction in "Where is my link?" ops queries (quantified via ops ticket volume)
- Higher demo attendance rate (less no-show due to anxiety/confusion)
- Better demo experience quality (students arrive prepared and engaged)
- Teacher NPS uplift (students show up prepared, reducing teacher frustration)

## Relevance Tags
- `demo-experience` `joining-flow` `conversion-funnel` `pre-class-engagement` `brightchamps` `ux`
