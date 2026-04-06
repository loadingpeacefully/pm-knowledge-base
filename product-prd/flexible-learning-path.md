---
title: "Flexible Learning Path"
category: product-prd
subcategory: learner-experience
source_id: fd410cb1-8e77-466b-ad64-8e0e4f555f44
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Flexible Learning Path

## Overview

Flexible Learning Path allows students to progress through the curriculum at their own pace rather than being locked to a fixed class schedule. Students can accelerate, slow down, or revisit lessons based on their performance and preference.

## Problem Statement

The existing curriculum follows a rigid, teacher-determined pace. Students who learn faster are under-stimulated, while students who need more time feel rushed. This rigidity contributes to disengagement and early churn.

## Goals & Success Metrics

- Increase lesson completion rate by 15%
- Reduce "lesson skipped" events by 20%
- Improve student satisfaction score (NPS) for curriculum pace
- Increase re-enrollment rate for students who complete their package

## User Stories / Jobs-to-Be-Done

- As a student, I want to move to the next lesson when I'm ready, not just when the teacher decides
- As a parent, I want to see what my child has completed and what's coming next
- As a teacher, I want to know which students are ahead or behind so I can personalize instruction
- As a student, I want the option to revisit a lesson I didn't fully understand

## Feature Scope

**In Scope:**
- Student-driven lesson unlock (post-quiz/assignment completion)
- Progress-based next-lesson recommendation
- Lesson status states: Not Started, In Progress, Completed, Skipped
- Teacher visibility into student's self-paced progress
- Parent progress view with flexible path context

**Out of Scope:**
- Fully asynchronous learning (no teacher-led classes)
- AI-driven adaptive lesson generation (future scope)

## Key Design Decisions

- Lesson unlock triggered by quiz completion (not just attendance)
- Teacher retains ability to override and mark lessons manually
- Non-linear paths are tracked but progress report uses "lessons covered" not lesson sequence

## Open Questions / Risks

- How to handle curriculum gaps when student skips ahead?
- Risk: Students gaming the system (completing quizzes without learning)
- Dependency: Quiz system must have reliable content per lesson to enable unlock
