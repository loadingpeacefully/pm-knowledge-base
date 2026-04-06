---
title: "Phase 2 - Post-Class Quiz Experience"
category: product-prd
subcategory: post-class-experience
source_id: b955cec3-d43a-4b43-a24f-be32480de191
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Phase 2 - Post-Class Quiz Experience

## Overview

Phase 2 enhancements to the Post-Class Quiz (Quiz Galaxy) experience. Focuses on richer start screen animations, immersive quiz icon design system, and improved visual/interaction language to increase engagement and return rates.

## Problem Statement

Phase 1 Quiz Galaxy provides functional quiz access but the UX lacks the polish and immersion needed to build a consistent post-class habit among Grade 4-10 students. Phase 2 adds animations, richer visual states, and accessibility features.

## Goals & Success Metrics

- Increase quiz attempt rate from Phase 1 baseline by a further 10 percentage points
- Increase quiz completion rate (started → finished) to 90%
- Improve student-reported enjoyment score for Quiz Galaxy (target: 4.5/5)
- Reduce "started but abandoned" quiz rate

## User Stories / Jobs-to-Be-Done

- As a student, I want the start screen to feel exciting and not like homework
- As a student, I want the transition from flashcards to quiz to feel seamless
- As a student with slower reading speed, I want a read-aloud option for quiz questions
- As a teacher, I want to grant extra time to specific students who need more support

## Feature Scope

**In Scope:**
- Start screen: character-by-character title animation with sound effects
- Dynamic text reveal with sequential word fade-in for quiz info
- "Review Flashcards" button: hover effect + flashcard slide animation + sound
- "Start Quiz" button: pulsing CTA with animated treasure chest (locked → unlocked on click)
- Loading animation: progress bar + educational tips + motivational background music
- Thematic quiz icons: digital key/orb (available), locked orb with gear (locked), glowing trophy/checkmark (completed)
- Hover tooltips on locked orbs showing prerequisites needed
- Smooth state transitions (locked → unlocked, available → completed) with CSS animations
- Phase 2 accommodations: extra time (once per quiz), sound effects toggle, read-aloud toggle

**Out of Scope:**
- New question types (Phase 1 MCQ format retained)
- Real-time quiz multiplayer

## Key Design Decisions

- All animations use SVG + CSS (not canvas) for cross-device responsiveness
- Sound effects and animations can be disabled in settings for accessibility compliance
- Hover/click animations include tactile feedback (vibration + sound) toggleable in settings
- Orb icon states driven by the same quiz state machine as Phase 1 (no new state logic)

## Open Questions / Risks

- Does adding animation/sound increase load time and hurt performance on low-end devices?
- Risk: Students may spend too long on start screen animations before attempting quiz
- Dependency: Phase 1 must be stable before Phase 2 features are layered on
- Open: Should "read-aloud" use TTS (text-to-speech) or pre-recorded audio?
