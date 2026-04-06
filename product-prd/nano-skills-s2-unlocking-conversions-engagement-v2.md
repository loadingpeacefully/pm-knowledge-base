---
title: "S2 - Nano Skills: Unlocking Conversions & Engagement (Sprint 2)"
category: product-prd
subcategory: nano-skills
source_id: 5db3460b-4ff2-4eea-b31b-830edd1e05d3
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# S2 - Nano Skills: Unlocking Conversions & Engagement (Sprint 2)

## Overview

Sprint 2 detailed spec for Nano Skills engagement improvements. Covers the full Nano Skills homepage redesign including diamond top-up banner, self-paced course tray with progress carousel, language-sensitive course trays, newly launched courses tray, teacher-led courses section, Harvard Courses placement, and category tabs.

## Problem Statement

Core mechanics for Nano Skills exist but are underutilized:
- Diamond hoarders (30%+ with > 100 diamonds) not converting to enrollment
- 68.4% of enrolled students haven't started their first lesson
- Vietnamese students (70% of diamond balance) not shown Vietnamese content first
- No in-product diamond top-up path — 0% conversion from low-balance state

## Goals & Success Metrics

| Metric | Baseline | Target | Confidence |
|--------|----------|--------|-----------|
| % Purchased Diamonds Consumed | 19.2% | ≥30% | 60% |
| Nano Course Diamonds Consumed | 24,113/mo | ≥35,000/mo | 80% |
| Diamond Top-Up Conversion | 0% | 2–3% | 60% |

## User Stories / Jobs-to-Be-Done

- As a student with < 15 diamonds, I want a clear prompt to buy more so I can enroll in a course
- As a Vietnamese student, I want to see Popular Vietnamese Courses in my language at the top
- As a student who enrolled but never started, I want a compelling nudge to begin my first lesson
- As a student exploring Nano Skills, I want to filter courses by category easily
- As a teacher, I want to see the progress of my students in Nano Skills (Phase 2)

## Feature Scope

**In Scope:**
- Add Diamond banner (< 15 diamond threshold, with payment modal)
- Diamond count animated button (< 80 diamond threshold)
- Self-Paced Course hero tray / progress carousel
- Language-Sensitive Tray (Vietnamese vs. Most Popular based on locale)
- Newly Launched Courses tray (top 4 by launch date, 15-day priority window)
- Teacher-Led Courses (live group sessions)
- Harvard Courses (placement below teacher-led)
- Category tabs (All, Creativity & Digital Skills, Financial Literacy, Math & Science, Personal Growth)
- Dynamic course ordering (enrollment count, last 30 days)
- 20% discount offer banner + feed post (48-hour window for abandoned diamond purchase)

**Out of Scope:**
- Teacher Nano Skills recommendation dashboard
- Parent progress email for Nano Skills
- Nano Skills leaderboard

## Key Design Decisions

- Only ONE language-sensitive tray shown per student (Vietnamese OR Most Popular)
- Newly Launched Courses tray always shown regardless of locale
- Courses where student is already enrolled are replaced with next-eligible course in tray
- Discount offer triggered only if no top-up completed within 48 hours of modal shown; CTA disabled after 48h

## Open Questions / Risks

- How to determine "system language" reliably across Android/iOS/web?
- Risk: Discount offer may create adverse incentive (wait for discount before buying)
- Dependency: Payment flow reuses parent hub — no backend payment changes needed
- Open: Should teacher-led session availability be real-time or batch-updated?
