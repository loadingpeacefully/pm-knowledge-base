---
title: "Geeta-AI Content Factory – Technical Architecture"
category: product-prd
subcategory: ai-content-factory
source_id: 6685498d-33a6-4d40-9640-0b65057ba454
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Geeta-AI Content Factory: Technical Architecture

## Overview

The Geeta-AI Content Factory is a multi-stage ETL (Extract, Transform, Load) pipeline — not a simple ChatGPT wrapper. It uses Python for logic, Google Sheets for the UI/interface, and Node.js for database injection.

## Architecture Stack

- **Backend:** Python (FastAPI + Uvicorn), port 8001
- **Interface:** Google Sheets (Google Apps Script)
- **Database:** Node.js + Sequelize → MySQL
- **AI Model:** OpenAI API with strict prompt engineering
- **Streaming:** Server-Sent Events (SSE)

## Core Workflow (RAG-Lite Pattern)

### Step A: Metadata Extraction
- Triggered by: `generate-v1/{skill_code}`
- Fetches curriculum context from Google Apps Script endpoint
- Retrieves: Lesson Name, Objectives, Problem Characteristics, Context Distribution
- Classifier determines: Pure Numeric / Word Problem / Mixed

### Step B: Prompt Engineering

**Sample Matching Protocol:**
- Forces AI to match difficulty/format of existing curriculum samples
- Prevents hallucination of inappropriate content types

**Tag System (Syntax Enforcement):**
- `[blank1:num]` → numeric input
- `[fraction:blank1]` → fraction widget
- `[break]` → line break

**Output Constraint:**
- Pure JSON: `{QID, Problem Statement, Expected Answer (key:value), Hint, Misconception}`

### Step C: Generation & Streaming
- AsyncGenerator for SSE streaming
- Batches: 20 questions (8 Easy, 6 Medium, 6 Hard)

## Validation Layer

Raw AI output is validated by Node.js/Apps Script middleware:
- Tag-to-Answer key matching (`blank1` → `key1`)
- All 12 mandatory columns present
- Data type enforcement
- Auto-flag keywords triggering image requirements

## Data Pipeline

`insertWorksheetQuestions` script:
1. Creates/validates Worksheet record by Skill Code
2. Maps to Curriculum via `WorksheetCurriculumMapping`
3. Creates `WorksheetQuestion` rows atomically
4. Parses answers into JSON format for programmatic grading
5. Idempotency: no duplicates by `sequence` + `variant`

## Technical Wins

| Win | Mechanism |
|-----|-----------|
| Decoupled architecture | Google Sheets as CMS (familiar UI for non-tech staff) |
| Hallucination control | Proprietary `[tag]` system converts text generation to structured code generation |
| Hybrid validation | Regex scripts verify structural integrity without trusting AI |

## Scale
- **10 → 150 worksheets/week** (15x scale)
- **0% syntax error rate** in production
- **~90% cost reduction** in content operations

## Relevance Tags
- `geeta-ai` `content-factory` `fastapi` `rag-lite` `prompt-engineering` `technical-architecture` `brightchamps`
