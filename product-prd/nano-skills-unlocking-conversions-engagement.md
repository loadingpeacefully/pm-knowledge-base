---
title: "Nano Skills Unlocking Conversions & Engagement"
category: product-prd
subcategory: nano-skills
source_id: 8a894ff0-2161-4454-b13d-e64a44666edf
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Nano Skills Unlocking Conversions & Engagement

## Overview

Sprint 2 initiative targeting Nano Skills engagement and diamond consumption growth. Focuses on three levers: localized discovery, friction removal at enrollment, and post-enrollment activation — with supporting nudges across students, parents, and teachers.

## Problem Statement

Despite existing Nano Skills infrastructure, three critical gaps block conversion:
1. 68.4% of enrolled students haven't started their first lesson
2. No in-product path to top up diamonds when balance is low (0% conversion from blocked intent)
3. Vietnamese students (holding ~70% of diamonds) are not shown relevant content first

## Goals & Success Metrics

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| % Purchased Diamonds Consumed | 19.2% (AMJ avg) | ≥30% | 30 Sept 2025 |
| Nano Course Diamonds Consumed | 24,113/mo | ≥35,000/mo | 30 Sept 2025 |
| Diamond Top-Up Conversion | 0% | 2–3% click-to-purchase | 30 Sept 2025 |

## User Stories / Jobs-to-Be-Done

- As a student with low diamonds, I want to be shown how to buy more without leaving the Nano Skills page
- As a Vietnamese student, I want to see Vietnamese courses first so I can find relevant content quickly
- As a student who enrolled in a course, I want a clear push to start my first lesson
- As a teacher, I want to recommend Nano Skills to students directly from my dashboard
- As a parent, I want to receive a summary of which skills my child completed

## Feature Scope

**In Scope:**
- Dynamic diamond top-up banner (visible to users with < 15 diamonds)
- Animated diamond count button (animated for users with < 80 diamonds)
- Language-sensitive tray (Vietnamese or Most Popular, based on locale)
- Newly Launched Courses tray (top 4 by launch date)
- Self-Paced Course hero tray with progress carousel
- Category tabs on Nano Skills homepage
- Dynamic course ordering (by enrollment count, past 30 days)
- Discount banner and feed post for incomplete diamond purchase (48-hour offer)
- Teacher Nano Skills recommendation tools (Phase 2)
- Parent progress email (Phase 2)

**Out of Scope:**
- New course content creation
- Teacher-assigned Nano Skills (V2)
- Leaderboard for Nano Skills

## Key Design Decisions

- Diamond top-up banner only shown to < 15 diamond users; animated button to < 80 diamond users
- Language-sensitive tray: Vietnamese tray for `vi` locale; Most Popular tray for all others
- Newly launched course gets 15-day priority placement before switching to enrollment-count ordering
- If enrolled in all displayed courses, replace with enrolled-state cards (updated CTAs)
- Discount offer (20% off) triggered if payment not completed within 48 hours of diamond modal shown

## Open Questions / Risks

- How to reliably detect Vietnamese locale (system language vs. IP vs. profile)?
- Risk: Discount offer may train students to wait for discounts
- Dependency: Diamond purchase flow must reuse existing parent hub payment flow with no backend changes
- Open: Should teachers be notified when students enroll in recommended skills?
