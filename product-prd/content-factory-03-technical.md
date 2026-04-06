---
title: "Content Factory 03 – Technical Deep Dive (Geeta-AI ETL Pipeline)"
category: product-prd
subcategory: ai-content-factory
source_id: 26b47625-999b-432a-916b-da9d0ad595f8
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Content Factory 03: Technical Deep Dive – Geeta-AI ETL Pipeline

## Architecture Stack

| Layer | Technology |
|-------|-----------|
| Backend Logic | Python (FastAPI + Uvicorn), port 8001 |
| Frontend/Interface | Google Sheets (powered by Google Apps Script) |
| Database Injection | Node.js with Sequelize (ORM) → MySQL |
| AI Model | OpenAI API (strict prompt engineering) |
| Communication | Server-Sent Events (SSE) for streaming generation status |

## The Core Workflow: RAG-Lite Generation

### Step A: Metadata Extraction & Context Building

When generation is triggered (`generate-v1/{skill_code}`):
1. **Fetch Metadata:** Python backend calls Google Apps Script endpoint to fetch "Master Skill Curriculum Sheet"
2. **Context Construction:** Retrieves: `Lesson Name`, `Objectives`, `Problem Characteristics`, `Context Distribution`
3. **Skill Classification:** Classifier determines skill type:
   - Pure Numeric
   - Word Problem
   - Mixed
4. **Context Distribution Logic:** For Mixed: 4 questions on Money, 4 on Sports, 4 on Science

### Step B: The Prompt Engineering Layer

**Sample Matching Protocol:**
- Prompt forces AI to analyze "Sample Questions" from curriculum
- If samples are simple arithmetic (`3.5 + 2.8`): word problems are forbidden

**The Tag System (Syntax Enforcement):**
| Tag | Renders As |
|-----|-----------|
| `[blank1:num]` | Numeric input box |
| `[fraction:blank1]` | Fraction input widget |
| `[break]` | Line break |

**Output Constraint:**
- LLM must output pure JSON with keys: `QID`, `Problem Statement`, `Expected Answer` (format: `key1: ans1`), `Hint`, `Misconception`

### Step C: Generation & Streaming

- Python backend uses `AsyncGenerator` with `text/event-stream` for streaming
- Batch generation: 20 questions per skill (8 Easy, 6 Medium, 6 Hard)

## The Validation Layer (The "Police")

Raw AI output is never trusted. Node.js middleware enforces:

1. **Tag-to-Answer Matching:** Parses `Problem Statement` for tags (e.g., `[blank1]`, `[blank2]`); checks `Expected Answer` keys match exactly (`key1`, `key2`)
2. **Structure Check:** Verifies all 12 mandatory columns are populated
3. **Image Detection:** Scans for keywords "draw," "graph," "plot" → auto-flags `Image_Required = True`

## The Data Pipeline (The "Muscle")

`insertWorksheetQuestions` Node.js script:
1. Checks if `Worksheet` exists → creates if not (using Skill Code)
2. Maps Worksheet to Curriculum via `WorksheetCurriculumMapping`
3. Creates `WorksheetQuestion` rows with atomic transactions
4. Parses AI string answers into JSON format (`getAnswer(input)`) for programmatic grading
5. Idempotency check: verifies no duplicate by `sequence` + `variant`

## Technical "Wins" Summary

| Achievement | Technical Mechanism |
|-------------|---------------------|
| Decoupled architecture | Google Sheets as CMS — non-tech SMEs review in familiar UI |
| Structured hallucination control | `[tag]` system + `key:value` answer format converts text generation to structured code generation |
| Hybrid validation | Regex scripts mathematically prove question structure matches answer key |
| Scale | 10 → 150 worksheets/week |
| Quality | 0% syntax error rate in production |

## Relevance Tags
- `content-factory` `geeta-ai` `fastapi` `rag-lite` `etl-pipeline` `prompt-engineering` `brightchamps` `technical`
