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

## 2026-04-06 — Design Agent added to swarm

**Decision:** Added D1 Nadia (Senior Product Designer) as 11th agent in pm_swarm.py. Created pm_format.py formatter script and upgraded dashboard renderer.

**Why:** Lessons were passing content QA but remained walls of text. The swarm had no visual scannability reviewer — dense prose was passing where tables, callouts, and cards would serve readers better.

**What changed:**
- D1 Nadia reads Working Knowledge level for visual hierarchy, comparison structure, callout usage, and information density
- Synthesizer now flags formatting issues and sets `run_formatter: true` when 2+ visual flags found
- pm_format.py applies Claude Haiku formatting transforms section-by-section (non-destructive, creates .bak)
- dashboard/index.html renders all new components: blockquote variants (warning/tip/info), quick-ref box, table rec rows, → arrows, markdown links

**Tradeoff:** Adds one more swarm agent (11 total, still fits in parallel budget). Formatter is optional — only runs when flagged.

## 2026-04-09 — v2 template review (post-88-lesson audit)

**Decision:** Refined v2 template rules based on patterns across 88 completed lessons.

**Score distribution observed:**
- Tech modules (01–04): avg 6.8–7.1 — concrete mechanisms, rich KB source material
- Product/business/GTM/security (05–09): avg 5.85–6.30 — more conceptual, fewer hard numbers

**Why the gap is expected (and acceptable):** Lower scores in product/business reflect the swarm
wanting more quantitative specificity in concepts where context-dependence is real. The gap is
not a template failure — it reflects honest domain differences. Threshold for "good" remains 5.0+.

**Changes made to CLAUDE.md:**
1. W1 rule: If > ~400 words, must include at least one table or summary box (D1's #1 critique)
2. W2 rule: Recommendations must include specific threshold/number/condition — "it depends" = fail
3. W4 rule: Explicit Company | What | Hard metric format; at least 3/5 examples need a number
4. S3 rule: Must include at least one reference to a shift in the last 2 years
5. Section naming: Standardized to em-dash style `## F1 — [Title]`
6. Known tech debt: 5 v1-style lessons documented (correct markers, bare section names)

**Structural anomaly fixed in record:** `api-versioning.md` has duplicate F3 headings
(analogy given its own F3 instead of living in F2). Not worth fixing in the file — it renders
correctly in dashboard. But the template now explicitly says: analogy belongs inside F2.
