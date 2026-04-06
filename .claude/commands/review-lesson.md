Review and fix an existing lesson based on QA flags. Re-run QA to confirm.

File: $ARGUMENTS

PHASE 1 — READ AND ASSESS
1. Read the lesson file completely
2. Check if it is v1 (8 sections, no levels) or v2 (10 sections, 3 levels)
   - If v1: this requires a full rewrite to v2 architecture, not a review.
     Output: "This is a v1 lesson. Run /rewrite-lesson [filename] instead."
     Stop here.
   - If v2: continue.
3. Load .claude/skills/lesson-qa.md
4. Run full QA — output complete report
5. Read tasks.md for any previously logged open flags on this lesson

PHASE 2 — FIX
6. Fix all Critical flags (mandatory — do not skip)
7. Fix all High flags (apply unless two fixes conflict — note conflicts)
8. Fix Medium flags that don't change meaning or structure
9. Do NOT apply Low flags
10. Re-count words per level after fixes — confirm still in range

PHASE 3 — RE-RUN QA
11. Run full QA on revised lesson
12. Output new QA report

PHASE 4 — SAVE
13. If READY TO SHIP: update status to ready, update last_qa date, save
14. If still issues: list remaining, do not mark ready
15. Update _CONCEPT_INDEX.md status
16. Update tasks.md: close fixed flags, note remaining
17. Output: "Review complete — [N] fixed, [N] remaining. Status: [ready/draft]"
