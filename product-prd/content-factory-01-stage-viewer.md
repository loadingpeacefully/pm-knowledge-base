---
title: "Content Factory 01 – Stage Viewer & Pipeline Architecture"
category: product-prd
subcategory: ai-content-factory
source_id: bf74b82e-7563-4375-a1f2-154db54265cb
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Content Factory 01: The Stage Viewer & New Pipeline Architecture

## Core Problem: "Sheet vs. Screen" Disparity

### The Trigger
Verifying content in a spreadsheet is technically valid but experientially flawed:
- **Layout Trap:** A 50-word question looks fine in a cell but might push the input box off-screen on a student's tablet
- **Input Ambiguity:** A reviewer cannot test if `3x + 2` input validation accepts spaces or requires a specific math keyboard
- **Solution Required:** A WYSIWYG (What You See Is What You Get) interface for reviewers

## New Pipeline Architecture: Two Coupled Pipelines

### Phase A: The Creation Pipeline (Geeta-AI)
- **Role:** Raw Manufacturing
- **Input:** Curriculum Metadata
- **Engine:** Python (FastAPI) + OpenAI
- **Output:** Rows in a Google Sheet
- Creates "Raw Material" — does not verify usability

### Phase B: The Review Pipeline (Stage Viewer)
- **Role:** Quality Assurance & UX Testing
- **Interface:** Custom web-based React/Node.js application
- **Data Sync:** Bi-directional sync with the Google Sheet

## Deep Dive: The Stage Viewer Tech

### A. The Rendering Engine
- Parses proprietary tags (`[blank1:num]`, `[fraction:blank1]`) and renders the **actual React components** used in the student app
- Reviewers don't just read "3x + 2" — they see the input box and can test spacing validation

### B. Bi-Directional Editing (The "Write-Back" System)
- **Read:** Stage Viewer pulls latest JSON from Google Sheet
- **Edit:** Reviewer clicks "Edit" directly on the rendered screen
- **Sync:** "Save" triggers API call to update the specific cell in the Master Sheet
- Google Sheet remains the **Single Source of Truth**, even though work happens in the UI

### C. The Approval State Machine
Three actions per question:
- **Approve:** Marks `Review Status = "Approved"` in Sheet
- **Reject:** Opens comment modal (e.g., "Incorrect Image," "Layout Overflow") → updates `Review Status` + `Additional Comment` columns
- **Upload Image:** Direct asset upload if `Image_Required` was flagged

## Automation & Deployment: The Cron Loop

### The Sweeper (Cron)
- Node.js script runs periodically (hourly or nightly)
- Scans Master Sheet for: `Review Status == "Approved"` AND `Sync_Status != "Synced"`

### The Fork
- **Path A (Approved):** Executes `insertWorksheetQuestions` → transforms JSON → inserts into Production MySQL Database → live for students
- **Path B (Rejected):** Assigns back to QA/Content queue → creation pipeline re-triggered for those Skill Codes

## Interview Summary

"I architected a Hybrid Content Operations Platform. We used Geeta-AI (Python/LLM) for high-volume creation, but for quality control, we built a Stage Viewer (React/Node). This allowed reviewers to validate content in a WYSIWYG environment—testing actual input mechanics (like `3x+2` spacing) and layout responsiveness—while maintaining a bi-directional sync with our Google Sheets database. Finally, a Cron-based orchestrator automatically promoted approved content to production and routed rejected content back for regeneration."

## Relevance Tags
- `content-factory` `stage-viewer` `geeta-ai` `wysiwyg` `bi-directional-sync` `brightchamps` `ai-pipeline`
