Write a new v2 concept lesson for the PM curriculum.

Lesson: $ARGUMENTS
(If $ARGUMENTS is "next" — read _CONCEPT_INDEX.md, find first row where status = —, use that lesson)

PHASE 1 — LOAD
1. Read CLAUDE.md fully — confirm v2 architecture and active rules
2. Read _CONCEPT_INDEX.md — find the target lesson row
3. Load .claude/skills/writer-personas.md — activate the `writer` column persona
4. Load .claude/skills/kb-reader.md
5. Load .claude/skills/lesson-writer.md
6. Read the 2 KB files from the `kb_sources` column of the manifest row

PHASE 2 — WRITE FOUNDATION (F1, F2, F3)
7. Write F1: A story. Protagonist with a real problem. Show the pain, then the resolution.
   Do NOT start with a definition or "before X existed."
8. Write F2: 2–3 sentence definition, zero jargon. One physical everyday analogy.
   If there are variants (REST/GraphQL), name them with one line each — no depth yet.
9. Write F3: 4–6 real PM moments. Each 2–3 sentences. Real stakes, real consequences.
10. Count Foundation words. Target 600–900.

PHASE 3 — WRITE WORKING KNOWLEDGE (W1, W2, W3, W4)
11. Write W1: Numbered steps. Full mechanism. As detailed as the concept requires.
    No artificial length limit — build a real mental model.
12. Write W2: 3–5 real tradeoffs. Each ends with a recommendation.
    "It depends on X — if X, do A; if Y, do B" is acceptable. Pure "it depends" is not.
13. Write W3: 6–8 specific questions. Each includes what the answer reveals.
    Every question assumes the PM has read Foundation and W1.
14. Write W4: 3–5 named companies. Specific product, specific feature, specific outcome.
    At least one must include a hard number.
15. Count Working Knowledge words. Target 1200–2000.

PHASE 4 — WRITE STRATEGIC DEPTH (S1, S2, S3)
16. Write S1: Real failure modes. Each: what it looks like, why it happens, PM's prevention role.
    Not "X is important to get right." Show the wreckage.
17. Write S2: How this concept interacts with 3+ other lessons in the curriculum.
    Name the specific lesson IDs. Explain the compounding relationship.
18. Write S3: The unresolved debates. What smart PMs disagree on.
    What's changed in the last 2 years. What AI is doing to this concept.
    Take a side. Don't just list positions.
19. Count Strategic words. Target 600–1000.

PHASE 5 — QA (mandatory)
20. Load .claude/skills/lesson-qa.md
21. Assemble panel from `qa_panel` column in _CONCEPT_INDEX.md (not from tags alone)
22. Run full QA — output complete report

PHASE 6 — SAVE DECISION
23. READY TO SHIP → save with status: ready, last_qa: [today]
24. FIX CRITICALS → fix inline, re-run QA, then save
25. AUTHOR CALL → save with status: draft, log High flags in tasks.md

PHASE 7 — UPDATE
26. Save to: concept-library/[module-folder]/[kebab-case-title].md
27. Update _CONCEPT_INDEX.md: status → ready or draft
28. Update tasks.md: mark done, note verdict and open flags
29. Output: "[Lesson] → [path] — [status] — [N] flags open"
