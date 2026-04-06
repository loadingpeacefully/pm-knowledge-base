---
title: "AI Worksheet Generator"
category: product-prd
subcategory: content-tools
source_id: cf808d7c-ef4f-4933-a72d-67a9e64ad2fd
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# AI Worksheet Generator

## Overview

AI-powered system (geeta-AI) that generates math worksheet questions for the BrightCHAMPS platform. Takes skill codes from the Master Curriculum Sheet, generates sample questions via LLM, passes through human review, and uploads validated questions to production.

## Problem Statement

Manual math worksheet creation is time-consuming, inconsistent, and does not scale across the K-10 curriculum. Creating 120 lessons per grade across 10 grades (1,200 total) manually would require 20 SMEs over 26 weeks at significant cost. AI generation can reduce this to 4 reviewers handling the same volume.

## Goals & Success Metrics

- Generate and review 1,200 lessons across Grades 1-10 within 26 weeks
- Reduce cost per lesson from 1,500 INR (manual) to 500 INR (AI-generated + reviewed)
- Achieve > 95% validation pass rate (Final Review = True) for generated questions
- Zero production errors from incorrectly formatted questions

## User Stories / Jobs-to-Be-Done

- As a content developer, I want to generate 20 validated questions for a skill code in < 30 minutes
- As a reviewer, I want to see AI-generated questions in a structured sheet and approve/reject each one
- As a developer, I want to upload approved questions to staging and production with a simple script
- As a teacher, I want worksheet questions to match the correct difficulty distribution (8 Easy, 8 Medium, 4 Hard)

## Feature Scope

**In Scope:**
- Skill metadata fetch from Master Curriculum Sheet (Google Sheets App Script)
- AI question generation via geeta-AI (LLM-based, FastAPI service)
- 3 sample questions → human review → 20 final questions generation
- Validation: tag format, blank-key correspondence, answer type checking
- Staging upload: Node.js script (insertWorksheetQuestions)
- Production upload: Node.js Paathshala script
- Image detection: auto-flag questions requiring diagrams

**Out of Scope:**
- Student-facing question selection logic
- Real-time question generation during class
- Non-math subjects in V1

## Key Design Decisions

- Difficulty distribution enforced: 8 Easy, 8 Medium, 4 Hard per skill
- Word-problem ratio capped at 50% (unless skill is word-problem only)
- Questions use structured tags: [break], [options:single], blank1:num, key1: value
- Image_Required flag auto-detected from problem statement keywords ("draw", "number line")
- Approved Skills sheet acts as single source of truth before prod upload

## Open Questions / Risks

- What is the process for updating questions post-production if errors found?
- Risk: LLM hallucination on specific math concepts — reviewer must catch
- Dependency: Google Sheets App Script for metadata and question management (single point of failure)
- Open: How to handle skill codes where Curriculum Sheet data is incomplete?
