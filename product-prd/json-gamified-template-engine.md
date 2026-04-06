---
title: "The JSON-Driven Gamified Template Engine Architecture"
category: product-prd
subcategory: content-authoring-engine
source_id: f4ff9895-cdc4-4b32-bdda-da2968263263
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# The JSON-Driven Gamified Template Engine Architecture

## Overview

Technical deep dive into the Gamified Template Engine built for BrightCHAMPS' Adhyayan platform. Architecture designed to demonstrate Systems Architecture and Frontend Logic capabilities in interviews.

## 1. Core Architecture: JSON-Driven UI

A **Declarative Rendering Engine** — the frontend acts as a "player" that consumes a JSON configuration file to render the appropriate React component.

### The "Task" Object
- Root entity; `templateTypes` field determines which React component to mount
- Polymorphism: single `Task` object might contain a `cardFlip` config OR a `crossword` config
- Database schema remains flexible without strict migrations for new game types

---

## 2. Key Gamification Mechanics

### A. Card Flip Engine (Memory & Discovery)

**Core Object:** `TaskCardFlip` with `frontSections` + `backSections`

**State Management:**
- `TaskFlipMultipleCards` with `multiFlipsAllowed` boolean
- `false` → mutex state: flipping Card B auto-closes Card A
- Matching game variant: randomizes `TemplateCard` array; tracks if clicked pair IDs match → reveal or auto-close after timeout

### B. Drag & Drop Engine (Categorization)

**Data Structure:** `question` array (draggable items) + `categories` array (drop zones)

**Validation:**
- Maps `options` to specific `categories`
- Drop Item A into Bucket B → frontend checks if Item A's ID exists in Bucket B's valid `options` array
- `variant: "assessment"` → suppresses immediate validation until "Submit"

### C. Hotspot Engine (Spatial Mechanics)

**Coordinate Mapping:**
- `MapArea` objects: `shape` (circle/polygon) + `coords` (number array)
- Invisible SVG overlay on rendered image
- Click events calculate if cursor X/Y falls within defined polygon coordinates

**Multi-Select State:**
- `selectUntilCorrect` flag → Mastery Loop until all valid coordinates clicked

### D. Crossword & Jumble Engine (Grid Mechanics)

**Grid Rendering:**
- `JumbledPuzzleGrid` defines `rows` and `columns` → CSS Grid rendered from these integers

**Data Binding:**
- `CrosswordLabel` objects bind clues to specific grid coordinates (`row`, `col`)
- Validation by intersection: changing a letter in 1-Down updates state for 3-Across

---

## 3. Advanced State & Logic Features

### A. "Select Until Correct" Loop
- `selectUntilCorrect: true` → "Next" button disabled
- State locking: once a correct option is selected, that UI element is frozen (cannot be deselected)
- Forces user to focus only on remaining incorrect items

### B. The "Feedback" Payload
- Every option includes a `feedback` object: `{ text, url, data }`
- On submission: payload pushed to **Chatbot Window** (Greenline/Ray bot)
- Connects static activity to conversational AI layer — wrong answers get character-delivered explanations

### C. Subjective vs. Evaluative Logic
- If `isCorrect` field is omitted: engine applies **Purple Highlight** (neutral) on selection
- vs. Green (correct) or Red (wrong)
- Enables opinion-based questions without breaking scoring logic

---

## 4. Visual & Asset Optimization

### Lottie Animation Integration
- `type: "json"` for animations → renders Lottie (.json) vector animations
- vs. MP4: vector-based, tiny file size, instant load on low-bandwidth connections
- High-quality character movements, confetti effects — lightweight

### Dynamic "Rich Text"
- `RichText` array: mixes strings with objects like `{ type: "link" }` or `{ type: "prompt" }`
- Renderer injects interactive React components (modal triggers) directly into paragraph text

---

## Interview Summary

"I architected a JSON-schema driven frontend that decoupled content creation from engineering. By defining 38+ interactive templates (Hotspots, Drag-and-Drop, Card Flips) in a strict schema, content teams built complex gamified logic — like 'Select Until Correct' loops or Spatial Coordinate Mapping — without writing a single line of code. This system used polymorphic rendering, where a single `Task` component dynamically loaded the correct game engine based on the JSON configuration."

## Relevance Tags
- `json-engine` `gamified-templates` `react` `polymorphism` `card-flip` `drag-drop` `hotspot` `crossword` `brightchamps`
