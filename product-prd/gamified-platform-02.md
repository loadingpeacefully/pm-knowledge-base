---
title: "Gamified Platform 02 – CMS Training & Low-Code Workflow"
category: product-prd
subcategory: content-authoring-engine
source_id: f621f36a-7329-4b44-97d5-7f177459cd7c
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Gamified Platform 02: How Content Creators Were Trained (Low-Code/No-Code Workflow)

## Overview

Content creators (teachers and subject matter experts) were NOT trained to write traditional code. They were trained on a **Low-Code/No-Code Operational Workflow** using the Adhyayan CMS, focused on three pillars: **Configuration, Visualization, and Constraints**.

## 1. The "Split-Screen" CMS Workflow

The interface was designed to provide immediate visual feedback, removing the abstract nature of coding.

### The Editor (Input)
- Left side: JSON Editor
- Creators didn't write schema from scratch — they filled in values for pre-defined keys (e.g., changing `"text": "Hello"` to `"text": "Welcome"`)

### The Stage Viewer (Output)
- Right side: Stage Viewer renders the game in **real-time**
- Instant visualization of how a JSON change (e.g., `multiFlipsAllowed: false`) affects gameplay behavior
- No engineering deployment needed to preview changes

## 2. The "Template Guide" (The Rulebook)

The comprehensive Template Guide acted as an operational manual for content creators.

### Selection Logic
- "If you want a memory game, use T1 - Card Flip"
- "If you want an assessment, use T8 - Multiple Choice"

### Strict Constraints (Enforced by Training)
- For T8 (MCQ): Keep questions <15 words and answers <3 words
- For T10 (Re-arranging): Keep card text under 6 letters
- Constraints prevent UI breakage due to text overflow or layout issues

## 3. Logic Configuration (Low-Code Features)

Creators were taught to control complex game logic using simple Boolean Flags and configuration objects.

### Gamification Control
- `selectUntilCorrect: true` → switches a task from Pass/Fail to a "Mastery Loop" (try again until right)
- `multiFlipsAllowed: false` → enforces mutex state in card flip games

### Asset Management
- Creators input Lottie JSON file paths into the `animation` field
- Ensures performance optimization handled at content entry level (not post-production)

## 4. Quality Assurance: Self-Serve Validation

The "Zero-Code Deployment" model trained creators to:
1. **Write** the JSON configuration
2. **Preview** in the Stage Viewer (check for layout overflows, text going off-screen)
3. **Publish** directly to the student app, bypassing the engineering deployment cycle

### Benefits
- No engineering tickets for content creation
- Immediate feedback loop on content quality
- Creators become "logic designers" without being engineers

## Interview Summary

"We didn't just hand them a text editor. We built a no-code studio. We trained creators to treat JSON as a configuration form, using a split-screen CMS to instantly visualize their changes. By providing a strict Template Guide with asset constraints (e.g., character limits), we empowered non-technical staff to build and deploy 2,000+ interactive lessons without a single engineering ticket."

## Relevance Tags
- `adhyayan` `cms-training` `low-code` `no-code` `content-authoring` `json-workflow` `brightchamps`
