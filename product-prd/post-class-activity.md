---
title: "Post-Class Activity"
category: product-prd
subcategory: post-class-experience
source_id: f7201c5c-649a-4916-83b7-bcaea5c4f2df
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Post-Class Activity

## Overview

Post-Class Activity covers the dynamic class summary and course progress experience on the unified student dashboard. Teachers update lesson status post-class; this drives real-time changes to student dashboard cards, quiz/assignment activation, and assessment triggering.

## Problem Statement

Students progress at different speeds — one student may complete a lesson in a single class while another takes 2-3 classes. The dashboard must reflect live learning pace and dynamically activate or deactivate assignments and quizzes based on actual progress, not a fixed schedule.

## Goals & Success Metrics

- Achieve 95% accuracy in dashboard card state vs. actual lesson status
- Increase assignment submission rate by 20%
- Reduce support tickets for "missing quiz" or "wrong class card" errors
- All assessment triggers fire correctly per curriculum mapping

## User Stories / Jobs-to-Be-Done

- As a teacher, I want to update lesson status immediately after class so the student dashboard reflects the real outcome
- As a student, I want to see the correct quiz and assignment on my dashboard after each class
- As a student, I want to receive a notification when a new quiz or assignment is activated for me
- As a parent, I want to track my child's course progress module by module

## Feature Scope

**In Scope:**
- Class status update: Completed Normally, Missed, Interrupted
- Lesson status: Skipped Completely, Skipped a Lot, Skipped a Bit, Covered Everything
- Dynamic upcoming class card state based on lesson status
- Quiz/Assignment activation: triggered by "Skipped a Bit" or "Covered Everything"
- 1-week quiz/assignment active window; auto-deactivated to "missed" after 7 days
- Assessment activation: based on curriculum mapping (specific class numbers); active for 1 week
- Assessment re-attempt for failed students (within same 1-week window)
- My Course Progress page: module-level progress view (5 states: Not Started, In Progress, Completed, Skipped, Paused)
- Certificate trigger: all lessons + all assessments for a module completed
- "Participation" certificate if classes exhausted without full completion

**Out of Scope:**
- Assessment creation (curriculum team manages question bank)
- Student-editable lesson status

## Key Design Decisions

- Quiz/Assignment active only for Skipped a Bit or Covered Everything (not for Skipped Completely or Skipped a Lot)
- If student completes 2 lessons in one class — 2 separate class summary cards with same class time/date
- Rating for class is given once per session, shared across both lesson cards if 2 completed
- Certificate: "Achievement" requires all lessons + passed assessments; "Participation" if credits exhausted without completion

## Open Questions / Risks

- What is the real-time mechanism for teacher feedback → dashboard update? (webhook vs. polling)
- Risk: Teacher may submit feedback hours after class — should dashboard update retroactively or wait?
- Dependency: Curriculum mapping sheet must accurately mark assessment trigger class numbers
- Open: How to handle courses with no assessments in the certificate trigger logic?
