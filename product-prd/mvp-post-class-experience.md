---
title: "MVP Post-Class Experience"
category: product-prd
subcategory: post-class-experience
source_id: 14477142-8fae-431a-a462-2753f1defad8
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# MVP Post-Class Experience

## Overview

MVP for a gamified post-class experience targeting the Financial Literacy course on BrightEdge Platform. Introduces XP System, project-level quizzes, weekly invite-a-friend collaborative challenges, and a progress dashboard to improve engagement and expand user base.

## Problem Statement

Financial Literacy students have low post-class engagement — they complete the class but don't practice or apply what they learned. Without a compelling post-class experience, quiz completion rates are low and parent-perceived value drops, reducing renewal rates.

## Goals & Success Metrics

- Increase quiz completion rate (target: 60% of students completing homework quizzes)
- Grow user base via invite-a-friend challenge conversion
- Improve student engagement (session duration, frequency of logins)
- Increase renewal/upgrade rate among parents who engage with progress features

## User Stories / Jobs-to-Be-Done

- As a student (Grade 4-6), I want to earn XP for completing quizzes and modules to feel rewarded
- As a student, I want to invite a friend to join a weekly challenge and win rewards together
- As a parent, I want to see a clear progress dashboard showing what my child has learned
- As a teacher, I want to see aggregate quiz data to adjust how I teach
- As a student, I want to work collaboratively on real-world financial projects with my friends

## Feature Scope

**In Scope:**
- XP (Experience Points) system: earn XP for module completion, quiz participation
- Project-level quizzes: end-of-project comprehensive quiz covering all modules in a project
- Weekly collaborative challenges: invite-a-friend, both parties receive rewards on completion
- Collaborative learning projects: teamwork-based problem solving
- Progress dashboard: XP level, recent scores, project quiz progress, challenge status
- Enhanced parental engagement tools: digital newsletters, personalized consultation prompts

**Out of Scope:**
- Real-time multiplayer gameplay
- Physical rewards (badges, merchandise)
- Cross-subject challenges (FinLit only in MVP)

## Key Design Decisions

- Invite-a-friend challenge requires both inviter and invitee to participate to unlock rewards
- Challenges are not real-time (can be completed at any time within the week)
- Progress dashboard is visible to both student and parent
- MVP development timeline: 2 weeks development + 1 week integration/testing
- Team: 1 designer, 3 FE developers, 1 BE developer

## Open Questions / Risks

- How to handle timezone differences for weekly challenges (challenge "week" definition)?
- Risk: Low friend invite acceptance rate if onboarding is complex
- Risk: XP inflation if too many actions award XP (needs careful calibration)
- Dependency: Parent dashboard must show XP and challenge progress for engagement tools to work
- Open: How to get parental consent for invited friends who are new users?
