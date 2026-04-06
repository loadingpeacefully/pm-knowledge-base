---
title: "V1 Generation Prompt - Math Worksheet"
category: product-prd
subcategory: content-tools
source_id: 4afd2754-0d43-44cc-a6bc-f094227a1b66
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# V1 Generation Prompt - Math Worksheet

## Overview

Reference document containing the V1 LLM prompt templates used by geeta-AI to generate math worksheet questions. Covers prompt structure, difficulty distribution, context distribution, formatting rules, and solution requirements for K-10 math skill codes.

## Problem Statement

Ad-hoc or poorly structured LLM prompts produce inconsistent question quality, wrong difficulty distributions, and formatting issues that require manual correction. A standardized, versioned prompt template ensures reproducible, reviewable question generation.

## Goals & Success Metrics

- Achieve > 95% Final Review = True rate using V1 prompts
- Maintain correct difficulty distribution (8 Easy, 8 Medium, 4 Hard per skill code)
- Zero formatting errors (malformed tags, LaTeX, HTML) in generated questions
- Reviewer approval rate > 90% on sample questions before full generation

## User Stories / Jobs-to-Be-Done

- As a content developer, I want a standard prompt template so I get consistent question formats every time
- As a reviewer, I want questions in the correct format so I don't have to spend time on structural fixes
- As a developer, I want prompts to enforce difficulty distribution automatically so I don't count manually
- As a content lead, I want to version prompts so I can track quality improvements over iterations

## Feature Scope

**In Scope:**
- Grade-level prompt context (Grade, Module, Topic, Skill, Standard, Lesson)
- Learning objective injection into prompt
- Difficulty distribution enforcement (8E/8M/4H)
- Context distribution (Money, Measurement, Sports, Science, Everyday Life — 4 each)
- Decimal operation requirements (specific to decimal skills)
- Solution requirements: step-by-step with formula, answer verification
- Formatting rules: [break] tags, no LaTeX/HTML, sequential blank numbering
- Problem characteristics by difficulty level (Easy: single-step, numbers 0.1-10; Medium: 2-3 decimal places; Hard: multi-step, 0.001-100)

**Out of Scope:**
- Non-math prompts
- Image-based question generation prompts (separate image workflow)
- Student-facing prompt customization

## Key Design Decisions

- Prompts are versioned (prompt_version field) to enable quality tracking across iterations
- Approved sample questions from previous runs are injected into the final prompt for style matching
- Word-problem ratio capped at 50% unless skill type is word-problem only
- Context distribution is fixed per skill code type (not dynamically varied)
- Each question generated individually in missing QID mode (not batch) to avoid repetition

## Open Questions / Risks

- How often should prompt versions be updated? Who owns versioning decisions?
- Risk: Injecting previous approved questions for style matching may cause over-fitting (similar questions generated)
- Dependency: Metadata API (metadata_script_path) must return clean skillData for prompt injection
- Open: Should prompts be stored in the system (DB) or in code (hardcoded)? Currently appears to be in code
