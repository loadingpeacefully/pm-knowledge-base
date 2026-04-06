---
title: "Content Factory 02 – Automated Bug Resolution System"
category: product-prd
subcategory: ai-content-factory
source_id: 81d54c1f-11b5-4ca9-8bb7-e8e037811ca2
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Content Factory 02: The Automated Bug Resolution System ("Self-Healing" Layer)

## Overview

The Automated Bug Resolution System transforms the Content Factory from a linear production line into a **Closed-Loop Feedback System**. Every student bug report becomes a structured data event that triggers either automated code execution or a targeted manual workflow.

## Architecture: Event-Driven Feedback Loop

### Phase A: Ingestion & Routing (The "Nervous System")

When a student reports a bug, the frontend triggers two synchronous actions:

**1. Slack Webhook (Visibility)**
- Sends real-time alert to `#content-bugs` channel
- Payload: `Student_ID`, `Worksheet_ID`, `Bug_Type`, `System_Info` (OS/Browser)

**2. Database Write (Persistence)**
- Appends unique row to "Master Bug Tracker" (Google Sheet)
- Smart Routing applied immediately to `Bug_Type` column:
  - `Content/Accuracy` → **Owner: AI**
  - `UI/Layout` → **Owner: Design Team**
  - `Other` → **Owner: Review Team**

## The AI Auto-Resolver (The "Self-Healing" Engine)

For content bugs, a Cron-based Agent handles resolution autonomously:

### The Logic
1. Daily Cron job (Node.js) queries Bug Sheet for: `Owner == "AI"` AND `Status == "Pending"`
2. **Context Retrieval:** Extracts `Worksheet_ID` (Skill Code) and `Question_ID` (QID)
3. **Correction Execution:** AI processes "Bug Context" (e.g., "hint implies addition but symbol is subtraction") → generates targeted patch for specific JSON field
4. **Diff Generation:** Compares existing JSON vs. new fix → creates Diff Log (New Value vs. Old Value)
5. **Auto-Deployment:** Executes `insertWorksheetQuestions` → fix pushed directly to Production
6. **Notification:** Bot replies to original Slack thread: "Resolved. Changed '4+4' to '4-4' in Problem Statement."

## Manual Workflow: Reusing the Stage Viewer

For UI/Layout bugs requiring human judgment:

### The Deep Link System
- Bug Sheet generates a "Preview Link" for every reported row: `domain.com/verification/v1?skillCode=XYZ&qid=123&mode=debug`

### The Workflow
1. Reviewer/Designer clicks the generated link
2. Stage Viewer renders the question exactly as the student saw it (same React components, debug mode)
3. Designer fixes content or layout directly in the panel
4. "Save Changes" pushes update to Master Sheet (Development) → sync script triggers Production update
5. Bug Sheet status automatically updated to `Resolved`

## Performance Impact

| Metric | Before | After |
|--------|--------|-------|
| Bug Turnaround Time | Days | Hours |
| Manual content fixes | 100% of content bugs | 0% (AI-handled) |
| Layout bug resolution | Slack + ticket system | Direct Stage Viewer deep link |
| Slack visibility | None | Real-time thread with Diff Log |

## Interview Summary (The Full Cycle)

"To handle maintenance at scale, I built an Automated Bug Resolution Pipeline. Ingestion: We routed user reports into a central data store (Sheets) and communication layer (Slack) with auto-tagging based on bug type. Self-Healing: For content errors, I wrote a Cron job that acted as an autonomous agent — it read the bug report, regenerated the specific question segment using Geeta-AI, pushed the code to production, and posted a 'Diff Log' to Slack without human intervention. Manual Efficiency: For UI bugs, we integrated deep links to our Stage Viewer, allowing designers to fix layout issues in a WYSIWYG environment that synced directly to production. This reduced our bug turnaround time from days to hours."

## Relevance Tags
- `content-factory` `bug-resolution` `self-healing` `cron-automation` `slack-webhook` `brightchamps` `ai-pipeline`
