---
title: "Post-Class Experience PRD"
category: product-prd
subcategory: post-class-experience
source_id: 85fe3e8a-cb9e-4e79-8949-8e7e11bb5370
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
version: full
source_notebook: NB5
---

# Post-Class Experience PRD

## Overview

Full PRD for the Post-Class Experience module covering two components: (1) Post-Class Revision Quiz (Quiz Galaxy), and (2) Home Activity. Both are designed to reinforce and extend learning beyond the classroom for Financial Literacy and Coding students.

## Problem Statement

Students complete their class and then have no structured, engaging way to practice what they learned. Homework completion rates are low because the experience is passive. Parents don't see tangible learning outputs. Teachers have no aggregate view of student understanding post-class.

## Goals & Success Metrics

- Increase post-class quiz attempt rate (target: 60%)
- Increase home activity submission rate (target: 40%)
- Improve quiz scores over time (indicate learning retention)
- Increase parent-reported satisfaction with learning visibility

## User Stories / Jobs-to-Be-Done

- As a student, I want to access flashcard review before my quiz so I can refresh key concepts
- As a student, I want to know when a quiz becomes available after my class
- As a parent, I want to receive a detailed quiz report to monitor my child's progress
- As a parent, I want to be involved in my child's home activity (real-world FinLit discussion)
- As a teacher, I want aggregate quiz data to identify where students struggle

## Feature Scope

**In Scope (Phase 1):**
- Quiz Galaxy entry point on student home screen (single icon)
- Orb-based quiz status (Locked, New/Active, Completed, Not Attempted)
- Commander Nova introduction states (all locked, first unlock)
- Start screen with quiz info and revision flashcards
- 10-question quiz (6E, 2M, 2H), 3 minutes, multiple choice
- Scoring (-1 for wrong), up to 3 attempts, best score reported
- Home Activity: activated after all modules in a topic completed
- Home Activity: real-world tasks (family discussion, data table entry, reflection questions)
- Parental involvement prompts in activity instructions
- Activity submission with data input, optional video upload

**In Scope (Phase 2):**
- New start screen animations
- Loading screen with educational tips
- Accommodations: extra time, sound effects, read-aloud
- Best attempt report shared with parents
- Leaderboard, badges/certifications for quiz categories

**Out of Scope:**
- Real-time quiz (teacher-led)
- Peer collaboration on quizzes

## Key Design Decisions

- Quiz auto-enabled after student completes all 3 modules for a class session
- Active window: 1 week; after that, banner removed but quiz still accessible (not "missed")
- Quiz questions: 10 questions for 3 modules (covering all 3 module concepts)
- Home Activity: capstone activity per topic (not per class/lesson)
- Teacher reviews activity submissions for comprehension quality

## Open Questions / Risks

- What happens if lesson quiz content is not yet created for a newly launched lesson?
- Risk: 3-minute timer may feel rushed for younger students in FinLit
- Dependency: Teacher must mark class as "completed" for quiz unlock trigger to fire
- Open: Should home activity be graded or just reviewed for participation?
