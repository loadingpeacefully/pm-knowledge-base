---
title: "TEMPLATES.pdf – Adhyayan Gamified Template Engine Schema"
category: product-prd
subcategory: content-authoring-engine
source_id: 59cb8139-bb89-4697-8970-e0a57315088d
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Adhyayan Gamified Template Engine Schema (TEMPLATES.pdf)

## Overview

The TEMPLATES document is the canonical technical specification for BrightCHAMPS' JSON-Driven Gamified Template Engine — the core architecture underlying the Adhyayan platform. It defines the full schema for 40+ interactive learning templates, including data structures, field definitions, validation constraints, and usage guidelines for content creators.

## Architecture: JSON-Driven Declarative UI

The engine uses a **Declarative Rendering** model: instead of hard-coding UI for each activity, the frontend acts as a generic "Player" that reads a JSON configuration file and renders the appropriate React component.

### Core Entity: Task Object
- Root entity in the schema
- `templateTypes` field determines which component to mount
- Supports **polymorphism**: a single Task object can be a memory game, crossword, MCQ, or video based on its configuration

## Template Types (TemplateTypes)

### Read-Only Content Templates
| Template | Use Case |
|----------|----------|
| `readonly` | Text, image, video in any layout (vertical/horizontal) |
| `activity-conversation` | Interactive character dialogue (AI mentor "Greenline") |
| `activity-table` | Tabular data presentation |

### Selection & Input Templates
| Template | Use Case |
|----------|----------|
| `activity-mcq` | Standard multiple-choice questions |
| `activity-mcq-tiles` | MCQ in tile/grid format |
| `activity-input` | List of text input fields |
| `activity-subjective` | Open-ended paragraph answer |
| `activity-rating` | Rating-based tasks (1–5 scale) |
| `activity-grid-select` | Grid-based selection (not MCQ — sets context for following tasks) |

### Drag & Drop / Spatial Templates
| Template | Use Case |
|----------|----------|
| `activity-match-the-following` | Drag-and-drop matching |
| `activity-bucketing` | Categorization/bucketing tasks |
| `activity-reorder` | Rearrange items in correct sequence |
| `activity-hotspot` | Click the correct area on an image (coordinate-based) |
| `activity-labelling` | Label areas within an image |

### Game Templates
| Template | Use Case |
|----------|----------|
| `activity-card-flip` | Read-only content on front and back of card |
| `activity-card-flip-game` | Memory game — match pairs of cards in a grid |
| `activity-crossword` | Crossword puzzle with intersecting letter inputs |
| `activity-fill-blanks` | Fill-in-the-blank with text inputs |

## Key Schema Features

### Polymorphic Configuration Objects
- `TaskCardFlip`: `frontSections` + `backSections` (for card flip)
- `TaskDragDrop`: `question` array + `categories` array (for drag & drop)
- `JumbledPuzzleGrid`: `rows` + `columns` (for crossword/grid)
- `MapArea`: `shape` + `coords` array (for hotspot coordinate mapping)

### Behavioral Flags
| Flag | Effect |
|------|--------|
| `multiFlipsAllowed: false` | Mutex state — flipping card B auto-closes card A |
| `selectUntilCorrect: true` | Mastery loop — student must stay until all correct answers selected |
| `variant: "assessment"` | Suppresses immediate validation until "Submit" pressed |
| `isCorrect: null` | Purple highlight (neutral) instead of green/red — for opinion-based questions |

### Feedback Payload
- Every option can include a `feedback` object: `{ text, url, data }`
- On answer submission, feedback is pushed to the Chatbot Window (Greenline/Ray)
- Connects static activity to conversational AI layer

### Asset Optimization
- `type: "json"` for animations → Lottie (vector JSON) instead of MP4
- Ensures high-quality animations load fast even in low-bandwidth regions
- `RichText` array: mixes strings with interactive components (links, modal triggers)

## Content Creator Constraints (Template Guide)

### Character Limits (Examples)
- MCQ (T8): Questions <15 words; answers <3 words
- Reorder (T10): Card text under 6 letters
- Input (T14): Response field max 50 characters

### Template Selection Logic
- "Memory game" → Card Flip Game
- "Multiple choice assessment" → MCQ or MCQ Tiles
- "Visual identification" → Hotspot
- "Sorting/categorizing" → Bucketing or Drag & Drop
- "Opinion/feeling check" → Rating or Subjective

## CMS Workflow
1. Content creator opens Adhyayan CMS
2. Selects template type from dropdown
3. Fills JSON configuration values in the left-side Editor
4. Stage Viewer (right side) renders the game in real time
5. Publishes directly to student app — no engineering deployment needed

## Scale Achieved
- 40+ template types operational
- 2,000+ interactive lessons authored using this system
- 3 verticals: Coding, Financial Literacy, Robotics (now Math added)
- Zero engineering tickets for content creation post-system launch

## Relevance Tags
- `adhyayan` `gamified-templates` `json-schema` `cms` `content-authoring` `brightchamps` `technical-spec`
