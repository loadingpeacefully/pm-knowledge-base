# Decisions Log — PM Knowledge Base

_Every architectural or product decision for this project. For humans only — not fed to Claude._

---

## 2026-04-06 — Curriculum scope

**Decision:** Cover Tech + Product + Business (3 domains, 9 modules, ~88 lessons)
**Why:** Target is PMs at any level as a shareable reference. Tech-only is too narrow for senior PMs; business layer differentiates from GFG.
**Tradeoff:** More lessons to write, but more durable as a resource.

## 2026-04-06 — Lesson format

**Decision:** Hybrid GFG structure + PM-specific decision prompts. 8 sections. 600–900 words.
**Why:** GFG is scannable and concept-first. PM layer (decisions, engineer questions) is the differentiator.
**Tradeoff:** More opinionated format — harder to contribute to, but higher quality floor.

## 2026-04-06 — KB source policy

**Decision:** KB files are read-only reference. Concept library is the writable layer.
**Why:** KB is ground truth for real systems. Mixing curriculum writes with KB risks corrupting source data.
**Tradeoff:** Two separate mental models to maintain.

## 2026-04-06 — Abstraction rule

**Decision:** All BrightChamps-specific names must be abstracted in lessons. KB evidence is used for grounding, not direct quotation.
**Why:** Curriculum is shareable publicly. Company-specific names reduce generalizability and may be sensitive.

## 2026-04-06 — Architecture v2 migration

**Decision:** Migrate all lessons from v1 (8 sections, single voice, 900-word cap) to v2 (3 depth levels, 10 sections, no word cap, profile-targeted).

**Why:** 10-profile PM audience analysis revealed:
1. The 900-word cap created thin content serving no profile well
2. Single voice and single entry point excluded 8 of 10 profiles
3. No learning hierarchy — no prereqs, no sequencing, no difficulty signal
4. The most underserved gap in PM education is technical fluency at the PM level with proper sequencing — exactly what v2 is designed to deliver.

**Reference implementation:** concept-library/01-apis-and-integration/what-is-an-api.md

**Tradeoff:** More words per lesson, more work per lesson.
Value: each lesson now serves the full PM spectrum, not just the technical PM.

**Files changed:** CLAUDE.md, lesson-writer.md, lesson-qa.md, new-lesson.md, review-lesson.md, qa-lesson.md, daily-start.md, status.md, rewrite-lesson.md (new), settings.json, _CONCEPT_INDEX.md, dashboard/index.html, 4 existing lessons rewritten to v2.
