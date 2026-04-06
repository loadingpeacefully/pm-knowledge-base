---
title: "The Geeta-AI Hybrid Content Operations Platform"
category: product-prd
subcategory: ai-content-factory
source_id: 25ce869f-88d6-452d-9020-40d9992d9bb5
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# The Geeta-AI Hybrid Content Operations Platform

## Overview

A full-stack Content Operations Platform that evolved from a simple generation script into a WYSIWYG review system. Solves the "Sheet vs. Screen" disparity — the critical UX failure where spreadsheet-approved content displays incorrectly in the actual student app.

---

## The Core Problem: "Sheet vs. Screen" Disparity

### The Two Failure Modes

**The Layout Trap:**
- A 50-word question looks fine in a spreadsheet cell
- On a student's tablet, the same question pushes the input box off-screen

**The Input Ambiguity:**
- `3x + 2` looks correct in a cell
- A spreadsheet reviewer cannot test whether the input box accepts spaces
- Does the system require a specific math keyboard? Only testing in the actual UI reveals this

### The Conclusion
Traditional spreadsheet-based review is fundamentally broken for UI-rendered content. A WYSIWYG interface is required.

---

## New Architecture: Two Coupled Pipelines

### Phase A: Creation Pipeline (Geeta-AI)
| Property | Value |
|----------|-------|
| Role | Raw Manufacturing |
| Input | Curriculum Metadata |
| Engine | Python (FastAPI) + OpenAI |
| Output | Rows in Google Sheet |
| Limitation | Creates raw material; cannot verify usability |

### Phase B: Review Pipeline (Stage Viewer)
| Property | Value |
|----------|-------|
| Role | Quality Assurance & UX Testing |
| Interface | Custom React/Node.js web application |
| Data Sync | Bi-directional sync with Google Sheet |

---

## Stage Viewer Deep Dive

### A. The Rendering Engine
- Parses proprietary tags: `[blank1:num]`, `[fraction:blank1]`, `[break]`
- Renders **actual React components** used in the student app (not text representations)
- Reviewer can type into input boxes to test validation logic in real time

### B. Bi-Directional Edit ("Write-Back" System)
- **Read:** Stage Viewer pulls latest JSON from Google Sheet
- **Edit:** Reviewer clicks "Edit" on the rendered screen; makes changes in-place
- **Sync:** "Save" → API call updates specific cells in Master Sheet
- **Result:** Google Sheet = Single Source of Truth; work happens in rich UI

### C. Approval State Machine

| Action | Effect |
|--------|--------|
| Approve | Sets `Review Status = "Approved"` in Sheet |
| Reject | Opens comment modal → updates `Review Status` + `Additional Comment` |
| Upload Image | Direct asset upload for `Image_Required` flagged items |

---

## Automation & Deployment: The Cron Loop

### The Sweeper
- Node.js script runs periodically
- Condition: `Review Status == "Approved"` AND `Sync_Status != "Synced"`

### The Fork
- **Approved path:** `insertWorksheetQuestions` → transforms JSON → Production MySQL Database → live for students
- **Rejected path:** Skill Codes re-queued → creation pipeline re-triggered to regenerate variations

---

## Interview Summary

"I architected a Hybrid Content Operations Platform. We used Geeta-AI (Python/LLM) for high-volume creation, but for quality control, we built a Stage Viewer (React/Node). This allowed reviewers to validate content in a WYSIWYG environment — testing actual input mechanics (like `3x+2` spacing) and layout responsiveness — while maintaining a bi-directional sync with our Google Sheets database. Finally, a Cron-based orchestrator automatically promoted approved content to production and routed rejected content back for regeneration."

---

## Why This Architecture Works

| Design Decision | Rationale |
|----------------|-----------|
| Google Sheets as primary DB | Non-tech staff already know how to use it; no new tools to learn |
| Bi-directional sync | Sheet stays as source of truth; rich UI handles human editing |
| Cron-based promotion | Fully automated deployment without manual steps |
| Stage Viewer as React mirror | Content reviewers test the exact same component the student sees |

## Relevance Tags
- `geeta-ai` `content-factory` `stage-viewer` `wysiwyg` `hybrid-platform` `brightchamps` `architecture`
