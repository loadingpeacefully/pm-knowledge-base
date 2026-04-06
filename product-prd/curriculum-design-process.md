---
title: "Curriculum Design Process"
category: product-prd
subcategory: curriculum-design
source_id: 1fdab4a9-5808-44b2-861f-b2fdb98dcbaf
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Curriculum Design Process

## Overview

This document describes the curriculum design framework used at BrightCHAMPS for creating structured, scalable learning content across verticals (Math, Coding, Financial Literacy, Robotics, Nano Skills).

## Design Philosophy

### Student-Led Learning
- The curriculum is designed to maximize **student agency** — students feel ownership over their progress
- Static lecture-style content (Google Slides) replaced with interactive, gamified modules
- Each lesson broken into modular segments to prevent cognitive fatigue and maintain engagement

### Layered Skill Framework (for Math)
1. **Milestones** — top-level learning goals (e.g., "Master Operations with Fractions")
2. **Skills** — specific capabilities under each milestone (e.g., "Add fractions with unlike denominators")
3. **Sub-skills** — atomic knowledge units (e.g., "Find LCM of two numbers")
4. **Activities** — individual interactive tasks that build sub-skill mastery

### Curriculum Alignment Standards
- **Math:** US Common Core; International Baccalaureate (IB) for global markets
- **Coding:** CSTA K-12 CS Framework
- **FinLit:** Custom framework based on real-world financial concepts (budgeting, investing, borrowing)

## Lesson Template: Recap → Spotlight → Practice

Each BrightCHAMPS lesson follows a standardized three-part structure:

| Phase | Duration | Purpose |
|-------|----------|---------|
| **Recap** | 5–10 min | Reinforce prior lesson concepts; combat the forgetting curve |
| **Spotlight** | 15–20 min | Introduce new concept with worked examples and teacher modeling |
| **Practice** | 20–25 min | Student-driven practice with gamified templates; teacher facilitates |

## Content Production Pipeline

### Step 1: Scope Definition
- Product/curriculum team defines learning objectives per sub-skill
- Benchmarking against competitors (Kumon, IXL, SplashLearn, Koobits) to identify gaps

### Step 2: Template Selection
- For each learning objective, select from the 40+ gamified templates (Card Flip, MCQ, Drag & Drop, Hotspot, etc.)
- Template guide defines character limits, asset constraints, and pedagogical use cases

### Step 3: JSON Authoring
- Content creators fill in pre-defined JSON schema via the Adhyayan CMS
- Stage Viewer provides real-time preview to validate layout and interaction logic
- Review cycle: Content creator → Reviewer (Stage Viewer) → Approved → Live

### Step 4: AI-Assisted Authoring (Geeta-AI)
- For worksheet/practice content: Geeta-AI generates question variations from curriculum metadata
- Validation middleware ensures structural integrity before human review

## Quality Standards
- All modules rated by students (1–5 stars) with required audio confirmation for feedback
- Target: 4.5+ rating across all modules
- Bug reporting system routes issues to the correct team (content/design/tech)

## Key Metrics
- Module engagement rate: quiz completion, time-on-task
- Learning outcomes: quiz scores, retry rates, mastery achievement
- Teacher satisfaction: rating of curriculum quality, ease of delivery

## Relevance Tags
- `curriculum-design` `lesson-template` `content-pipeline` `math-vertical` `brightchamps` `adhyayan`
