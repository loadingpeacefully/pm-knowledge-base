---
title: "Introducing Post-Class Quiz Galaxy"
category: product-prd
subcategory: post-class-experience
source_id: a592a4d1-4136-4e3a-92f7-5785c5300e55
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
version: quiz-galaxy-spec
source_notebook: NB5
---

# Introducing Post-Class Quiz Galaxy

## Overview

Quiz Galaxy is the gamified post-class quiz experience for BrightCHAMPS students. Students navigate a space-themed galaxy of quiz orbs, each representing a quiz unlocked by class completion. Commander Nova (AI character) guides students through the experience.

## Problem Statement

Post-class quiz completion rates are low when quizzes are presented as plain homework tasks. Students aged 7-13 need an engaging, game-like wrapper around quiz content to build the habit of post-class practice.

## Goals & Success Metrics

- Increase post-class quiz attempt rate to 60%
- Increase quiz completion rate (started → finished) to 85%
- Increase 7-day return rate for students who complete their first Quiz Galaxy quiz
- Track DAU impact of Quiz Galaxy vs. non-Quiz Galaxy students

## User Stories / Jobs-to-Be-Done

- As a student, I want to feel like I'm on a mission when I take my quiz after class
- As a student, I want to know which quizzes I've unlocked and which are still locked
- As a parent, I want to know my child completed their quiz and what score they got
- As a student, I want to be able to review flashcards before I start the quiz

## Feature Scope

**In Scope:**
- Quiz Galaxy screen: grid of orbs (locked, active/new, completed)
- Commander Nova character with contextual messages
- Orb states: Locked (lock icon), New/Active (spinning with "New" banner), Completed (flag — green for perfect, standard otherwise), Not Attempted (banner removed after 1 week, still accessible)
- Start screen: dynamic welcome, quiz info (topics, question count, duration)
- Revision flashcards (pre-quiz review option)
- Quiz: 10 questions (6 Easy, 2 Medium, 2 Hard), 3 minutes total, multiple choice
- Scoring: 100 total, -1 per wrong answer, up to 3 attempts, best score reported
- Loading screen with educational tips and animated progress bar
- Special accommodations (Phase 2): extra time, sound effects, read-aloud

**Out of Scope:**
- Multiplayer/real-time quiz battles (future scope)
- Quiz leaderboard (future scope)
- Custom quiz difficulty (teacher-assigned)

## Key Design Decisions

- Quiz auto-unlocked after student completes all modules in a class session (3 modules/class)
- Active quiz window: 1 week from unlock; after 1 week, banner removed but still accessible (not missed)
- New students (≤ 5 classes completed): all quizzes unlocked as "New" for 1 week with welcoming Commander message
- Best attempt (not latest) is the score shared with parents
- Quiz timer is fixed at 3 minutes for all students (Phase 1)

## Open Questions / Risks

- How to prevent students from rushing through flashcards (just to get to quiz faster)?
- Risk: Timer pressure may stress younger students — should timer be optional?
- Dependency: Quiz questions must be available per lesson before quiz is activated
- Open: Should Commander Nova be voiced (audio) or text-only?
