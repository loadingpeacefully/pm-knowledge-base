# PM Knowledge Base — CLAUDE.md
# Project memory. Read this at the start of every session.
# Last updated: 2026-04-06 — Architecture v2 migration

---

## What this project is

Two parts:

1. **KB (Knowledge Base)** — 214 enriched markdown files from BrightChamps production systems.
   Source of truth for technical architecture, PRDs, competitive research, performance reviews.
   Lives in: technical-architecture/, product-prd/, research-competitive/, performance-reviews/
   Rule: NEVER modify KB files. Read-only reference only.

2. **Concept Library** — A PM learning curriculum. 9 modules, 88 lessons.
   Each lesson covers ONE universal concept. Written for 10 distinct PM profile types.
   Lives in: concept-library/
   Architecture: v2 (3-level depth system — see below)

---

## Curriculum architecture — v2

Every lesson has THREE self-contained depth levels.
The dashboard shows one level at a time. Reader selects their level.

### Level 1: Foundation
- Who: non-technical business PM, aspiring PM, designer PM, MBA PM (tech modules)
- Assumes: nothing. No prereqs.
- Sections: F1 (world before), F2 (what it is + analogy), F3 (when PM encounters this)
- Length: 600–900 words
- Rules:
  - Every technical term defined on first use. No exceptions.
  - Exactly one physical everyday analogy before any mechanism.
  - Story first. Business impact before technical detail.
  - No jargon, no shortcuts.

### Level 2: Working Knowledge
- Who: growth PM, consumer startup PM, B2B enterprise PM, 2+ years experience
- Assumes: Foundation (or existing PM context)
- Sections: W1 (how it works), W2 (decisions it forces), W3 (engineer questions), W4 (real examples)
- Length: 1200–2000 words (no cap — as long as the concept requires)
- Rules:
  - W1: numbered steps, mechanism first. As detailed as needed to build a real mental model.
  - W2: 3–5 real tradeoffs. Each must end with a recommendation. "It depends" without guidance = fail.
  - W3: 6–8 specific questions. Each includes what the answer reveals.
  - W4: 3–5 named companies. At least one hard number (metric, percentage, price, timeframe).

### Level 3: Strategic Depth
- Who: ex-engineer PM, senior PM, head of product, AI-native PM
- Assumes: Working Knowledge
- Sections: S1 (what breaks), S2 (system connections), S3 (what senior PMs debate)
- Length: 600–1000 words
- Rules:
  - No hand-holding. Debates, not definitions.
  - S1: failure modes with mechanism and PM prevention role.
  - S2: explicit links to other curriculum concepts, how understanding compounds.
  - S3: genuine intellectual tension. What changed in last 2 years. What AI is doing to this concept.

---

## Frontmatter schema — v2

Every lesson must use this exact frontmatter:

```yaml
---
lesson: [Concept Name]
module: [number — name]
tags: [tech | product | business]
difficulty: [foundation | working | strategic]  # default starting level
prereqs:
  - [lesson-id] — [one line why]
writer: [staff-engineer-pm | senior-pm | cfo-finance | gtm-lead]
qa_panel: [comma-separated personas]
kb_sources:
  - [path/to/kb/file.md]
profiles:
  foundation: [list of PM profiles]
  working: [list of PM profiles]
  strategic: [list of PM profiles]
status: draft | ready
last_qa: [YYYY-MM-DD]
---
```

---

## Writer personas

| persona | modules | voice |
|---|---|---|
| staff-engineer-pm | 01, 02, 03, 04, 09 | Direct. Gives opinions. Names failure modes before happy path. |
| senior-pm | 05, 06 | Conversational. Story-driven. Opinionated frameworks. |
| cfo-finance | 07 | Precise numbers. Mechanism before metric. Connects to P&L. |
| gtm-lead | 08 | User-first. Distribution-first. Opinionated on sequencing. |

Full persona definitions: `.claude/skills/writer-personas.md`

---

## QA panel assignment

QA panel comes from _CONCEPT_INDEX.md `qa_panel` column — not from tags alone.

Cross-pairing rule (always enforced):
- staff-engineer-pm writer → Junior PM Reader always in panel
- senior-pm writer → Staff Engineer always in panel (keeps tech claims honest)
- cfo-finance writer → GTM Lead always in panel (catches when finance ignores distribution)
- gtm-lead writer → CFO/Finance Lead always in panel (catches when growth ignores margin)

Full QA rules: `.claude/skills/lesson-qa.md`

---

## Lesson section reference

| ID | Name | Level | Required |
|---|---|---|---|
| F1 | The world before this existed | Foundation | Yes |
| F2 | What it is — definition + analogy | Foundation | Yes |
| F3 | When you'll encounter this as a PM | Foundation | Yes |
| W1 | How it actually works | Working | Yes |
| W2 | The decisions this forces | Working | Yes |
| W3 | Questions to ask your engineer | Working | Yes |
| W4 | Real product examples | Working | Yes |
| S1 | What breaks and why | Strategic | Yes |
| S2 | How this connects to the bigger system | Strategic | Yes |
| S3 | What senior PMs debate | Strategic | Yes |

---

## Folder structure

```
pm-knowledge-base/
├── CLAUDE.md                 ← you are here
├── _REGISTRY.md              ← KB index (read-only)
├── tasks.md                  ← update every session
├── decisions.md              ← architectural decisions log
├── memory.md                 ← long-term patterns
│
├── technical-architecture/   ← KB (READ ONLY)
├── product-prd/              ← KB (READ ONLY)
├── research-competitive/     ← KB (READ ONLY)
├── performance-reviews/      ← KB (READ ONLY)
├── assets/                   ← KB (READ ONLY)
│
├── concept-library/
│   ├── _CONCEPT_INDEX.md     ← lesson manifest (pipeline controller)
│   ├── 01-apis-and-integration/
│   ├── 02-databases-and-data/
│   ├── 03-infrastructure-and-devops/
│   ├── 04-ai-and-ml-systems/
│   ├── 05-product-fundamentals/
│   ├── 06-metrics-and-analytics/
│   ├── 07-business-and-monetization/
│   ├── 08-gtm-and-growth/
│   └── 09-security-and-scale/
│
└── dashboard/
    └── index.html            ← local study dashboard
```

---

## Active rules

- Never modify files outside concept-library/, dashboard/, tasks.md, decisions.md, memory.md, CLAUDE.md, .claude/
- Never delete any KB file or _REGISTRY.md
- Always update tasks.md at the end of every session
- When writing lessons: pull real examples from KB files, never invent
- All lessons must follow v2 architecture. No v1 lessons (8 sections, no levels) are acceptable.
- QA is mandatory before any lesson is marked ready
- _CONCEPT_INDEX.md is the pipeline controller — it drives all lesson writes

---

## KB notebook IDs (for MCP calls)

NB1: 2c11acfe-fafc-4bb8-8381-c92ca2cb4353
NB5: 256e3b28-eea5-40b6-aebb-dd4833c8b870

---

## Owner

Suneet Jagdev — Senior PM, BrightChamps, Bengaluru
