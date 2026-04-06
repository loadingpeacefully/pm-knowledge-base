---
title: "Gamification Badges"
category: product-prd
subcategory: learner-experience
source_id: 29f5812e-4287-4f4d-9179-df43bfd6244e
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Gamification Badges

## Overview

Gamification Badges recognize and reward student achievements — class attendance streaks, quiz completions, Nano Skills enrollments, and milestones. Badges displayed on student profile and shared in feed.

## Problem Statement

Students lack visible recognition for their efforts beyond certificates. Without a continuous reward loop, engagement drops between major milestones. Badges provide a lightweight, frequent recognition mechanism.

## Goals & Success Metrics

- Increase daily active users (DAU) by 10%
- Increase 7-day retention post-enrollment
- Increase Nano Skills completion rate
- Increase quiz attempt rate (target: 60% completion)

## User Stories / Jobs-to-Be-Done

- As a student, I want to earn badges for consistent attendance so I feel rewarded for showing up
- As a student, I want to show my badges to friends and family
- As a parent, I want to see what my child has earned to understand their progress
- As a student, I want to know what I need to do to earn the next badge

## Feature Scope

**In Scope:**
- Badge types: Attendance streak, Quiz ace, Nano Skills completion, First class, Course completion
- Badge display on student profile
- Feed card on badge earned
- Badge unlock criteria visible in app
- Badge count on parent progress view

**Out of Scope:**
- Badge trading or social gifting
- Physical badge/merchandise (future scope)
- Teacher badges

## Key Design Decisions

- Badges are awarded automatically by event triggers (no manual award)
- Streak badges reset if student misses the trigger condition (e.g., attendance streak)
- Nano Skills completion badge requires completing all lessons, not just enrollment

## Open Questions / Risks

- What is the right badge density? Too many badges devalue them
- Risk: Badge criteria need to be clearly communicated to avoid confusion
- Dependency: Feed service must support badge card type
