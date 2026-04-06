Run full QA panel review on an existing lesson. Read-only — does not modify files.

File: $ARGUMENTS

1. Read the lesson file
2. Load .claude/skills/lesson-qa.md
3. Detect lesson version:
   - Count level headers (# FOUNDATION, # WORKING KNOWLEDGE, # STRATEGIC DEPTH)
   - If 3 levels found: v2 lesson — run full v2 QA
   - If not found: v1 lesson — flag as "v1 architecture detected. Needs full rewrite."
4. Run full QA — assemble panel from frontmatter `qa_panel` field
5. Output complete QA report in the exact format defined in lesson-qa.md
6. Do NOT modify any file
7. Do NOT change status field
