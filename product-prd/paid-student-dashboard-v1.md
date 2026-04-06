---
title: "Paid Student Dashboard v1"
category: product-prd
subcategory: learner-experience
source_id: dacd6f61-d114-4ea9-acd2-e43ce20088fb
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Paid Student Dashboard v1

## Overview

V1 of the unified paid student dashboard — consolidates all courses into one platform, replacing fragmented per-course dashboards. Supports multi-profile households, upcoming class management, class summaries, course progress, and certificates.

## Problem Statement

BrightCHAMPS had multiple separate student dashboards per course with different UIs and navigation patterns. This fragmented experience confused students and parents, made cross-course management difficult, and limited the platform's ability to cross-sell. A unified dashboard solves all three issues.

## Goals & Success Metrics

- Reduce student support tickets related to dashboard navigation by 30%
- Increase cross-course enrollment rate for students who see unified progress view
- Improve parent satisfaction score for dashboard experience (NPS target: +15 points)
- Achieve 90%+ successful class-join rate via new join flow

## User Stories / Jobs-to-Be-Done

- As a parent with multiple children, I want to switch between profiles without logging out
- As a student, I want to see my next 3 upcoming classes with their timing and a join button
- As a student, I want to review my last class summary including assignments and quizzes
- As a parent, I want to see my child's course progress and certificates from one place
- As a student, I want to reschedule a class without calling support

## Feature Scope

**In Scope (V1):**
- Multi-profile login: single vs. multi-student profile selection post-login
- Dashboard Home: Banner, Upcoming Classes (3 cards), Class Summary section
- Class cards: topic image, module name, class no. & name, timing, teacher, join button with T-24h timer
- Reschedule: reason capture → date/time selection (next 7 days, available teacher slots only)
- Cancel: reason capture → type "CANCEL" confirmation (2-step friction)
- Class Summary page: all completed classes, sort by newest/oldest
- Certificates page: all earned certificates with course name, certificate name, award date
- Profile & Progress section: student details, learning progress, course enrollment CTA

**Out of Scope (V1):**
- Edit profile (V2)
- Demo dashboard (separate product)
- Assessment and results (V2)
- In-app certificate download (mobile app only in V1)

## Key Design Decisions

- Sidebar: collapsed by default, expands on hover; 3 pages: Home, Class Summary, Certificates
- Join button disabled at T > 24h; timer shown at T < 24h; join active at T-5min
- Cancellation requires typing "CANCEL" to add friction and reduce accidental cancellations
- Profile section shows: student name, grade, school, country, avatar/photo
- Help & Support details only shown in expanded sidebar state

## Open Questions / Risks

- What teacher slots are shown in reschedule flow — only original teacher or all available teachers?
- Risk: Multiple-user households may have profile confusion if avatars look similar
- Dependency: Teacher availability service must expose slots reliably for reschedule flow
- Open: Timeline for adding notification bar (planned for V2)?
