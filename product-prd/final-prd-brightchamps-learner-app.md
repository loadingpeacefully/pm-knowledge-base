---
title: "Final PRD BrightCHAMPS Learner App"
category: product-prd
subcategory: learner-experience
source_id: 929cd1cc-86bf-4152-bc98-569965718729
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Final PRD BrightCHAMPS Learner App

## Overview

Comprehensive product requirements document for the BrightCHAMPS Learner App — the primary student-facing product covering dashboard, class experience, Nano Skills, post-class activities, progress tracking, and gamification.

## Problem Statement

Students across BrightCHAMPS courses experienced fragmented dashboards, inconsistent UX between demo and paid modes, and low post-class engagement. Parents lacked visibility into learning progress. The learner app consolidates all student touchpoints into a unified, engaging experience.

## Goals & Success Metrics

- Increase class attendance rate by 10%
- Increase post-class quiz completion to 60%
- Increase Nano Skills diamond consumption to 35,000/month
- Improve NPS by 10 points
- Reduce post-enrollment churn in first 30 days

## User Stories / Jobs-to-Be-Done

- As a student, I want to join my class easily and see what I'll learn before it starts
- As a student, I want to complete quizzes after class to reinforce learning
- As a parent, I want to see my child's progress against the curriculum
- As a student, I want to explore and enroll in Nano Skills to learn beyond my class
- As a parent, I want to receive updates on my child's achievements

## Feature Scope

**In Scope:**
- Unified login and profile selection (single/multi-student households)
- Upcoming class cards with join flow
- Post-class summary with assignments and quizzes
- Course progress view (My Course Progress)
- Nano Skills discovery, enrollment, and completion
- Student feed with milestone cards
- Progress report (per 10 lessons completed)
- Certificate display and download
- Gamification: XP system, badges, showcase

**Out of Scope:**
- Teacher-facing features
- Admin/ops dashboard
- Real-time in-class experience (separate product)

## Key Design Decisions

- Single dashboard codebase with mode flag (demo vs paid) from enrollment service
- Post-class quiz activated by lesson completion event (not time-based)
- Nano Skills discovery uses locale-aware tray ordering
- Progress report generated every 10 unique lessons covered (not 10 classes)

## Open Questions / Risks

- How to handle non-linear learning paths in progress reporting?
- What is the fallback if quiz content is not available for a newly launched lesson?
- Risk: Parent notification fatigue if too many updates are sent
- Dependency on teacher feedback form completion for progress report accuracy
