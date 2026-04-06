---
title: "Content Factory Summary – Geeta-AI Numon Pipeline (Executive Overview)"
category: product-prd
subcategory: ai-content-factory
source_id: f891ed02-3d66-4eab-8174-f6d3a7964f2a
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Content Factory Summary: Geeta-AI (Numon Pipeline)

## Executive Summary

The Geeta-AI Content Factory is a hybrid **Content Operations Platform** designed to scale the production of math practice content (Worksheets) for the Numon product. It transformed a manual, bottlenecked process into an automated, self-healing ecosystem.

**By decoupling Creation (LLM), Validation (Code), and Review (Human), the system scaled production from 10 worksheets/week to 150+ worksheets/week (15x scale) while reducing operational costs by 90%.**

---

## The Problem Space

### The Velocity Bottleneck
- Cap: Manual creation capped at ~10 worksheets per week
- Cost: Highly paid SMEs spent 80% of time on JSON formatting, not pedagogical design
- Error Rate: Manual data entry caused frequent syntax errors (missing keys, invalid JSON) that crashed the app

### The "Sheet vs. Screen" Disparity
- Blind Review: Reviewers approved content in Google Sheets (text), but the Student App renders React Components (UI)
- The "3x+2" Problem: Correct in a spreadsheet cell; reviewer couldn't verify input box accepted spaces
- Layout Overflow: Long questions pushed input boxes off mobile screens — invisible during spreadsheet review

---

## System Architecture: The "Triad" Pipeline

| Phase | Component | Tech Stack | Role |
|-------|-----------|-----------|------|
| 1. Generation | Geeta-AI Engine | Python (FastAPI), OpenAI | Raw Manufacturing |
| 2. Validation | Regex Middleware | Node.js, Google Apps Script | Quality Control (Syntax Police) |
| 3. Review | Stage Viewer | React, Node.js | User Acceptance Testing (WYSIWYG) |

---

## Phase 1: Creation Engine (Geeta-AI)

### Metadata Extraction & RAG-Lite
- Reads from Master Skill Curriculum Sheet
- Injects "Sample Questions" to ground LLM output
- If sample is simple arithmetic: word problems explicitly forbidden

### Prompt Engineering (The "Tag" System)
- `[blank1:num]` → Numeric input box
- `[fraction:blank1]` → Fraction widget
- `[break]` → New line

### Streaming Generation
- Server-Sent Events (SSE) for real-time status
- Balanced batches: 8 Easy, 6 Medium, 6 Hard per skill

---

## Phase 2: Validation Layer

The `validateProblemStatementsAndAnswers` script enforces:
- **Structure Check:** All 12 mandatory columns present
- **Tag-Key Matching:** `blank1` in statement → `key1` in answer
- **Data Type Enforcement:** `[blank1:num]` accepts only numeric answers
- **Auto-Flagging:** "draw"/"graph"/"plot" keywords → `Image_Required = True`

---

## Phase 3: Review Ecosystem (Stage Viewer)

### Bi-Directional Sync
- **View:** Renders raw JSON into actual React components used in student app
- **Edit:** Reviewers edit text/LaTeX directly on screen → "Save" writes back to Google Sheet
- **Outcome:** Google Sheet is Single Source of Truth; work happens in rich UI

### Deployment (The "Sweeper" Cron)
Once marked Approved:
1. Node.js Cron scans for approved rows
2. Executes `insertWorksheetQuestions`
3. Transforms JSON → pushes to Production MySQL Database

---

## End State: Automated Bug Resolution (Self-Healing)

### Event-Driven Ingestion
- Student reports bug → Slack alert to `#content-bugs` + row in Master Bug Sheet
- Smart Routing: Content/Accuracy → AI; UI/Layout → Design Team

### Self-Healing AI Agent
1. Daily Cron detects pending AI bugs
2. Calls Geeta-AI to regenerate only the specific field (e.g., new Hint for QID 123)
3. Pushes fix to Production
4. Reports Diff Log to Slack thread

---

## Summary of Impact

| Metric | Result |
|--------|--------|
| Production scale | 10 → 150 worksheets/week (15x) |
| Quality | 0% syntax error rate |
| Bug TAT | Days → Hours |
| Cost reduction | ~90% of content operations costs |
| Manual dependency | Removed for content/accuracy bug fixes |

## Relevance Tags
- `content-factory` `geeta-ai` `numon` `executive-summary` `ai-pipeline` `brightchamps` `scale`
