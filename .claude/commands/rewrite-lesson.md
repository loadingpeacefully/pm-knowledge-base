Rewrite an existing v1 lesson to v2 three-level architecture.

File: $ARGUMENTS

PHASE 1 — READ AND EXTRACT
1. Read the existing v1 lesson file fully
2. Extract all valuable content:
   - The story/problem framing (maps to F1)
   - The definition and analogy (maps to F2)
   - PM encounter scenarios (maps to F3)
   - How it works content (maps to W1)
   - Decisions/tradeoffs (maps to W2)
   - Engineer questions (maps to W3)
   - Real product examples (maps to W4)
   - Note: v1 has no S1/S2/S3 — these must be written from scratch
3. Read the v2 reference lesson: concept-library/01-apis-and-integration/what-is-an-api.md
4. Load writer-personas.md — activate the correct writer persona
5. Load kb-reader.md — find relevant KB sources

PHASE 2 — REWRITE TO V2
6. Write all 3 levels using v2 architecture (see CLAUDE.md and lesson-writer.md)
7. Preserve and expand good content from v1
8. Write S1, S2, S3 fresh — v1 has no equivalent
9. Update frontmatter to v2 schema

PHASE 3 — QA AND SAVE
10. Run full QA (lesson-qa.md)
11. Fix Critical and High flags
12. Save, update _CONCEPT_INDEX.md, update tasks.md
13. Output: "Rewritten [lesson] to v2 — [path] — status: [ready/draft] — [N] flags"
