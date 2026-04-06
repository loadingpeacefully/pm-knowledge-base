# Skill: Lesson QA — v2 Adaptive Panel Review

Load this skill after every lesson is written, before saving.

---

## Step 0 — Pre-flight checks (run before assembling panel)

Read the lesson file. Extract:
- lesson, module, tags, difficulty, prereqs, writer, qa_panel, status
- Run: wc -w on the file (total)
- Count words in each level separately (Foundation, Working, Strategic)
- List all 10 section headers — confirm all 10 exist (F1-F3, W1-W4, S1-S3)

### Universal guardrails — flag any violation before personas run

G1: Foundation 600–900 words. Under 400 = too thin. Over 1000 = too dense.
G2: Working Knowledge 1200–2000 words. Under 800 = too thin.
G3: Strategic Depth 600–1000 words. Under 400 = too thin.
G4: All 10 sections present (F1, F2, F3, W1, W2, W3, W4, S1, S2, S3).
G5: F2 contains exactly one physical everyday analogy before any mechanism.
G6: Every technical term in Foundation is defined on first use.
G7: Every W2 tradeoff ends with a recommendation — not "it depends" alone.
G8: W4 contains at least one hard number (metric, %, price, timeframe).
G9: Concept coherence — every concept named in F2 or W1 is either:
    (a) explained within its level,
    (b) explicitly deferred with "→ covered in [lesson]", or
    (c) used as a known analogy only.
    Orphaned concepts = High flag.
G10: No BrightChamps product names anywhere (Quiz Galaxy, Adhyayan, PQS, TeacherBot,
     Paathshala, Eklavya, Doordarshan, Chowkidar, Prabandhan, Hermes, Tryouts, Auxo, Geeta).
G11: Frontmatter complete — all fields present (lesson, module, tags, difficulty, prereqs,
     writer, qa_panel, kb_sources, profiles, status, last_qa).
G12: Related lessons section exists and separates prereqs / companions / next.

---

## Step 1 — Assemble adaptive panel

Use the `qa_panel` field from frontmatter (not tags alone).
Always include Junior PM Reader regardless of panel.

Available personas: Staff Engineer, Senior PM, CFO/Finance Lead, GTM Lead, Junior PM Reader

State the panel before reviewing:
"Panel for [lesson] ([tags]): → [persona 1], → [persona 2], → [persona 3]"

---

## Step 2 — Persona reviews

Each persona reads ALL THREE levels and flags issues from their lens.

Flag format:
[PERSONA] [LEVEL] [SECTION] — Issue description — Severity: Critical | High | Medium | Low

Severity:
- Critical: wrong, misleading, or creates false understanding. Blocks ready status.
- High: key section weak, generic, or missing depth. Author must decide before marking ready.
- Medium: polish — tone, structure, missed example. Fix recommended.
- Low: minor tightening. Author discretion.

---

### Staff Engineer persona

Background: 8+ years building distributed systems. Moved into PM. Hates false confidence.
Holistic read: After section checks, read the whole lesson top to bottom.
Does every concept introduced in F2 or W1 get resolved by the end of that level?

Checks:
- F1: Is this a real story or a textbook preamble?
- F2: Is the definition technically accurate? Does the analogy distort the concept?
- W1: Is the mechanism correct? Any dangerous oversimplifications?
- W1: Are variants (REST/GraphQL, SQL/NoSQL, etc.) handled correctly?
- W2: Are the tradeoffs real architectural decisions, not generic comparisons?
- W2: Does each recommendation reflect what a good engineer would actually do?
- W3: Are the questions ones a PM could ask after reading this lesson?
- W3: Does each question reveal something specific about the system?
- S1: Are the failure modes real? Do they name the mechanism, not just the symptom?
- S3: Does the debate section reflect what senior engineers and PMs actually argue about?
- Coherence: any concept introduced and then orphaned?

Standard: "After reading Foundation, could a PM ask one intelligent question in an arch review?"

---

### Senior PM persona

Background: 7 years product, 3 companies. Deep skepticism of PM theory without application.

Checks:
- F1: Does this story have stakes? Does it make the reader care?
- F3: Are these real PM moments with real consequences — not abstract scenarios?
- W2: Is the PM's actual decision named — or just options listed neutrally?
- W2: Does each tradeoff tell the PM when to push back vs. defer?
- W3: Could these questions be asked in a real meeting under time pressure?
- S3: Is there a genuine product management perspective in the debate — or just engineering views?
- All levels: Is the PM the protagonist — or just an observer?

Standard: "Could I paste Foundation into APM onboarding and have them be meaningfully better in week 1?"

---

### CFO / Finance Lead persona (activate only for business-tagged lessons)

Background: Runs FP&A at Series B. Has killed features over unit economics.

Checks:
- W4: Are real financial numbers present (rates, margins, payback periods)?
- W2: Does each tradeoff name the P&L or unit economics implication?
- S3: Is the business model evolution in this space addressed?
- All: Does the lesson help a PM understand when a business decision is a finance decision?

Standard: "After reading this, would a PM understand why the CFO said no — and know how to reframe?"

---

### GTM Lead persona (activate only for business-tagged lessons)

Background: Runs growth at B2C startup. Thinks distribution before product.

Checks:
- F3: Are launch, channel, and activation moments in the PM encounters list?
- W4: Do the real product examples show the GTM motion, not just the product feature?
- S2: Does the system connections section address distribution and growth implications?
- S3: Does the debate address how this concept affects user adoption and retention?

Standard: "Does this lesson help a PM understand why users adopt, stick, or leave?"

---

### Junior PM Reader (always active)

Background: 1 year in product. Business background. Smart but has no technical context.

Checks:
- F1: Does the story pull them in before asking them to learn anything?
- F2: Is the analogy truly everyday — or does it require prior knowledge?
- F2: Is the first jargon term defined within 2 sentences of appearing?
- F3: Are these scenarios recognizable from their first 6 months on the job?
- Foundation word count: 600–900? Outside this = immediate flag.
- W1: Could they follow the numbered steps with zero technical background?
- W3: Could they say these questions out loud in a meeting without embarrassment?
- Related lessons: does the lesson leave them with clear next steps?

Standard: "Could this PM read Foundation in 5 minutes and confidently use the vocabulary in their next meeting?"

---

## Step 3 — Output the QA Report

Use this exact format:

```
═══════════════════════════════════════════════════
LESSON QA REPORT — v2
Lesson: [name]
Module: [module]
Tags: [tags]
Panel: [personas]

WORD COUNT
Foundation   : [N] words — [PASS / FAIL — target 600–900]
Working      : [N] words — [PASS / FAIL — target 1200–2000]
Strategic    : [N] words — [PASS / FAIL — target 600–1000]

SECTION CHECK
[✓/✗] F1 — The world before this existed
[✓/✗] F2 — What it is + analogy
[✓/✗] F3 — When PM encounters this
[✓/✗] W1 — How it actually works
[✓/✗] W2 — The decisions this forces
[✓/✗] W3 — Questions to ask your engineer ([N] questions)
[✓/✗] W4 — Real product examples ([N] companies, [has/lacks] hard number)
[✓/✗] S1 — What breaks and why
[✓/✗] S2 — System connections ([N] lesson links)
[✓/✗] S3 — What senior PMs debate

GUARDRAIL CHECK
[✓/✗] G1-G3: Word counts
[✓/✗] G4: All 10 sections present
[✓/✗] G5: F2 analogy before mechanism
[✓/✗] G6: Foundation terms defined
[✓/✗] G7: W2 recommendations present
[✓/✗] G8: W4 hard number present
[✓/✗] G9: Concept coherence
[✓/✗] G10: Brand safety — [CLEAN / terms found: list]
[✓/✗] G11: Frontmatter complete
[✓/✗] G12: Related lessons structured

FLAG LIST
[If no flags]: No flags raised. Lesson is clean.

[STAFF ENGINEER] [LEVEL] [SECTION] — issue — Severity
...

[SENIOR PM] [LEVEL] [SECTION] — issue — Severity
...

[JUNIOR PM READER] [LEVEL] [SECTION] — issue — Severity
...

SUMMARY
Critical : [N]
High     : [N]
Medium   : [N]
Low      : [N]

Verdict:
→ READY TO SHIP        (0 Critical, 0 High)
→ FIX CRITICALS FIRST  (any Critical)
→ AUTHOR CALL          (High flags, no Critical)
═══════════════════════════════════════════════════
```

---

## Step 4 — Do NOT auto-fix

This skill produces a report only.
To apply fixes: run /review-lesson [filename]
