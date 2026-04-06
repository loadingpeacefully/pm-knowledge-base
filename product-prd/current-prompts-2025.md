---
title: "CURRENT PROMPTS – AI Prompt Library (July 2025)"
category: product-prd
subcategory: ai-content-factory
source_id: ca6f2149-45be-49a7-895e-9a793dfe0059
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# CURRENT PROMPTS – AI Prompt Library (July 2025)

## Overview

This document is the canonical library of production AI prompts used in BrightCHAMPS' AI Content Factory (Geeta-AI). It contains all prompt templates used for generating math worksheets, question variations, hint/explanation content, and curriculum-grounded quiz content as of July 23, 2025.

> Note: Source file is 87,325 characters. This document captures the structural overview and key prompt engineering principles. For full prompt text, reference the original source (source_id: ca6f2149-45be-49a7-895e-9a793dfe0059).

## Prompt Engineering Architecture

### Core Design Philosophy
- Prompts are **context-aware** — each generation request includes curriculum metadata (lesson name, objectives, sample questions) to ground the LLM output
- **Tag enforcement** — prompts mandate the use of proprietary UI tags (`[blank1:num]`, `[fraction:blank1]`, `[break]`) in output, ensuring generated content is directly renderable in the student app without post-processing
- **Structured output** — all prompts require JSON output with defined keys: QID, Problem Statement, Expected Answer (key:value format), Hint, Misconception, Difficulty
- **Sample matching** — prompts force the AI to analyze existing sample questions; if samples are simple arithmetic, word problems are prohibited

### Prompt Types

| Prompt Category | Purpose |
|----------------|---------|
| **Worksheet Generation v1** | Generate a batch of 20 questions (8 Easy, 6 Medium, 6 Hard) for a given skill code |
| **Worksheet Generation v2** | Refined version with improved difficulty calibration and context distribution logic |
| **Hint Generation** | Generate pedagogically useful hints for existing questions (not just the answer, but the reasoning step) |
| **Misconception Tagging** | Identify and document common student errors for a given question type |
| **Question Variation** | Generate N variations of an existing question (change numbers/names, preserve structure) |
| **Explanation Generation** | Generate step-by-step worked solution for a question |
| **Context Distribution** | Classify skill as Pure Numeric / Word Problem / Mixed; assign context themes (Money, Sports, Science) |

### Skill Classification Logic
The system runs a pre-generation classifier:
1. **Pure Numeric**: `3.5 + 2.8` → purely computational, no context
2. **Word Problem**: "Rahul has 5 apples..." → real-world narrative required
3. **Mixed**: Some questions are numeric, others are contextual

Context Distribution example for a Mixed skill:
- 4 questions: Money context
- 4 questions: Sports context
- 4 questions: Science context
- 8 questions: Pure numeric

### Tag System Specification

| Tag | Renders As |
|-----|-----------|
| `[blank1:num]` | Numeric input box |
| `[blank2:num]` | Second numeric input box |
| `[fraction:blank1]` | Fraction input widget (numerator + denominator) |
| `[break]` | Line break in problem statement |
| `[blank1:text]` | Text input field |

### Output Validation Checks (Run After Generation)
1. All mandatory columns present (QID, Problem Statement, Expected Answer, Hint, Difficulty)
2. Tags in Problem Statement match keys in Expected Answer (`blank1` → `key1`)
3. Data type consistency (`[blank1:num]` → answer must be numeric)
4. No keywords triggering image requirement ("draw", "graph", "plot") without Image_Required flag

## Prompt Quality Standards

### What Good Prompts Ensure
- Minimal hallucination through explicit constraints ("Do NOT generate word problems if samples are arithmetic")
- Structural integrity through tag mandates
- Pedagogical alignment through curriculum context injection
- Output consistency through JSON format enforcement

### Iteration History
Prompts have been iterated through multiple versions (v1 → v2) to address:
- Inconsistent difficulty calibration in v1
- Tag omission in edge cases (very long problem statements)
- Context repetition (same Money context for all word problems)
- Answer key mismatch (blank1 in statement, key2 in answer)

## Integration with Geeta-AI Pipeline
- Prompts are stored as code templates in the Python (FastAPI) backend
- Curriculum metadata injected at runtime from Google Sheets API
- Generation streamed to frontend via Server-Sent Events (SSE)
- Output written to Google Sheets; validated by middleware before human review

## Relevance Tags
- `ai-prompts` `geeta-ai` `content-factory` `prompt-engineering` `worksheet-generation` `brightchamps` `llm`
