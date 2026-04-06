# Skill: Lesson Writer — v2

Load this skill when writing any concept lesson.

## Architecture reminder

Every lesson has THREE levels. Each level is self-contained.
Read CLAUDE.md for full level specs before writing.

Foundation → Working Knowledge → Strategic Depth

Never blend levels. Write each level completely before moving to the next.

## Quality bar — Foundation

Pass conditions:
- 600–900 words
- All 3 sections present: F1, F2, F3
- F1 is a story with a protagonist and a problem. Not "before X, people did Y." Show it.
- F2 has exactly one physical everyday analogy BEFORE any mechanism
- F2 defines every technical term on first use
- F3 has 4–6 PM scenarios each 2–3 sentences long with real stakes
- Zero jargon undefined. Zero shortcuts. Zero assumed context.
- Read it aloud: could a smart sales manager follow this? If not, rewrite.

## Quality bar — Working Knowledge

Pass conditions:
- 1200–2000 words (no cap — as long as the concept needs)
- All 4 sections present: W1, W2, W3, W4
- W1: numbered steps, enough depth to build a real mental model
- W2: 3–5 tradeoffs, each ending with a recommendation. "It depends" alone = fail.
- W3: 6–8 questions, each with what the answer reveals
- W4: 3–5 named companies, at least one hard number
- W4: every company example uses the ### card format (never prose narrative)
- W2: every comparison with 2+ named options uses a comparison table (never parallel paragraphs)
- No BrightChamps product names (use abstracted versions: see kb-reader.md)

## Quality bar — Strategic Depth

Pass conditions:
- 600–1000 words
- All 3 sections present: S1, S2, S3
- S1: failure modes with mechanism + PM prevention role. Not "X is important."
- S2: explicit links to 3+ other curriculum lessons. How this concept compounds.
- S3: genuine intellectual tension. What changed recently. What AI is doing to this space.
- No hand-holding. No definitions. Debates only.
- Read it: would a Head of Product find something new here? If not, deepen it.

## Tone per level

Foundation: warm, clear, story-driven. Like explaining to a smart colleague who's new to tech.
Working: direct, opinionated, precise. Like a smart senior PM briefing you before a hard meeting.
Strategic: peer-level. No explaining. Just debating the hard questions.

## Level markers (exact format required)

Use these exact headers to delimit levels. The dashboard parser splits on them.

```
# ═══════════════════════════════════
# FOUNDATION
# For: [profiles]
# Assumes: [prereqs or "nothing"]
# ═══════════════════════════════════
```

```
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: [profiles]
# Assumes: Foundation. [one line prereq note]
# ═══════════════════════════════════
```

```
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: [profiles]
# Assumes: Working Knowledge. [one line]
# This level debates, doesn't explain.
# ═══════════════════════════════════
```

## Process

1. Read CLAUDE.md — confirm architecture and active rules
2. Load writer-personas.md — activate the correct persona for this lesson
3. Load kb-reader.md — find and read the KB source files from _CONCEPT_INDEX.md
4. Write Foundation completely. Check word count. Check all pass conditions.
5. Write Working Knowledge completely. Check word count. Check all pass conditions.
6. Write Strategic Depth completely. Check word count. Check all pass conditions.
7. Run lesson-qa.md — full QA before saving.
8. Save to correct path. Update _CONCEPT_INDEX.md. Update tasks.md.

## Anti-patterns to eliminate

- Starting F1 with a definition ("X is a concept that...")
- F2 analogy that requires technical knowledge to understand the analogy
- W2 tradeoffs that end with "it depends" without specifying what it depends on
- W3 questions that could be asked by someone who hasn't read the lesson
- W4 examples without a number or a named outcome
- S3 that summarizes positions without taking a side or naming the real tension
- Any level that bleeds vocabulary from a higher level into a lower one

**Anti-pattern: Company examples written as prose narrative**
W4 (Real product examples) must NEVER be written as bold-company + flowing paragraph.
Every company example must use this exact card structure:

### [Company Name] — [one-line headline describing the specific thing they did]

**What they did:** One sentence. Specific feature or decision, not "they built X."
**Why it worked:** One sentence. The mechanism — what made it effective.
**PM takeaway:** One sentence. What a PM should do or ask differently because of this.

No narrative prose. No "Stripe is the canonical example of..." openers.
If you find yourself writing a paragraph about a company, stop and use the card format.

---

**Anti-pattern: Comparison sections written as parallel prose paragraphs**
Any W2 decision with 2+ named options (REST vs GraphQL, polling vs webhooks,
URL versioning vs header versioning, sync vs async) must NEVER be written as
bold-label + paragraph + bold-label + paragraph.

Use a comparison table instead:

| | Option A | Option B |
|---|---|---|
| Best for | ... | ... |
| Cost/risk | ... | ... |
| **Default** | **Use this** | Only when [specific condition] |

Rules for the table:
- Last row must be **Default** — bold in first cell, recommendation in both option columns
- Max 4 rows — if you need more, you're comparing too many dimensions
- "Best for" is always row 1
- After the table: one callout box with the PM recommendation (> **PM default:** ...)
