---
title: "Math Worksheet Flow"
category: product-prd
subcategory: content-tools
source_id: d9a2ddce-6e80-4d23-baab-edb74fa9cbe4
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Math Worksheet Flow

## Overview

End-to-end process flow for math worksheet creation — from skill intake through AI generation, validation, human review, staging upload, and production release. Documents each step, actor, system, and decision gate.

## Problem Statement

The math worksheet generation process was undocumented, relying on tribal knowledge across developers, reviewers, and content leads. Without a clear documented flow, onboarding new team members was slow, errors crept in at handoff points, and the process was not repeatable at scale.

## Goals & Success Metrics

- All team members can execute the full workflow independently using this document
- Reduce average time from skill intake to production upload by 30%
- Zero production errors caused by unclear handoff procedures
- Process handles 120 skill codes per grade without bottlenecks

## User Stories / Jobs-to-Be-Done

- As a new developer, I want a step-by-step process to follow when processing a new skill code
- As a reviewer, I want to know exactly what I need to check and in what order
- As a content lead, I want to see the full pipeline at a glance to identify where bottlenecks occur
- As a developer, I want clear inputs and outputs for each step so I know when to proceed

## Feature Scope

**In Scope:**
- Step 0 — Intake & Readiness: confirm skill readiness, assign developer + reviewer, record Skill Code
- Step 1 — Metadata & Type Setup: fetch skill metadata, classify skill type (word problem / numeric / mixed)
- Step 2 — Sample Generation: build sample prompt, generate 3 sample questions, auto-flag image needs, manual review
- Step 3 — Final Prompt & Generation: build final prompt, generate 20 questions, distribution check (8E/8M/4H)
- Step 4 — Validation: run validateProblemStatementsAndAnswers(), check Final Review flags
- Step 5 — Human Review: reviewer approves/rejects per question, flags Image_Required
- Step 6 — Staging Upload: run insertWorksheetQuestions() Node.js script
- Step 7 — Final Review: check Approved Skills New Master Data sheet for red cells
- Step 8 — Production Upload: run Paathshala Node.js script with approved skill codes

**Out of Scope:**
- Image generation workflow (separate process)
- Post-production question editing process
- Cross-subject content flows

## Key Design Decisions

- Sample review is a hard gate — cannot proceed to final generation without sample approval
- Distribution check (8E/8M/4H + MCQ balance) is automated before human review
- "New Master Data" sheet is the single source of truth for production-ready questions
- Red cells in New Master Data = do not upload; only clean rows proceed to production
- Process loops are defined: sample rejection → edit metadata → regenerate sample (not escalate)

## Open Questions / Risks

- What is the SLA for reviewer turnaround on 3 sample questions? On 20 final questions?
- Risk: Bottleneck at Step 5 (human review) if reviewer capacity is limited
- Dependency: geeta-AI service (FastAPI) must be running and accessible during generation steps
- Open: Is there a tracking sheet to monitor pipeline status per skill code across all grades?
