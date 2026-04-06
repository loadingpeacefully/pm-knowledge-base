# Memory — PM Knowledge Base

_Long-term patterns, bugs, things that worked, things that broke. Claude reads this._

---

## Lesson quality patterns

- The "Questions to ask your engineer" section is the hardest to write well. Generic questions ("How does this scale?") fail. Good questions assume the PM has read the lesson and probe specific decisions ("Why did you choose cursor-based pagination over offset here? What breaks at scale with offset?")
- "The problem it solves" works best as a mini story — 3-4 sentences describing a world without this concept, then the punchline of what changed.
- Analogies land best when they're physical and everyday (a restaurant menu = an API contract; a post office = a message queue).

## KB patterns

- `_REGISTRY.md` is the fastest way to find relevant files. Search it before reading individual files.
- `technical-architecture/payments/` has the richest real-world monetization examples.
- `technical-architecture/infrastructure/` has strong lessons for Modules 01–03 (APIs, infra, DevOps).
- `research-competitive/lingoace-*` files are useful for GTM and competitive benchmarking lessons.
- `product-prd/` files are best for Module 05 (Product Fundamentals) examples.

## Warnings

- Do NOT read all 214 files in one pass — context overload. Use _REGISTRY.md to sample.
- Do NOT write lessons from memory — always cite a KB file or a named real-world product.
- Lessons with `status: draft` are incomplete. Do not link to them from other lessons until they are `status: ready`.

## Architecture v2 patterns — 2026-04-06

**F1 most common failure:** Starting with a definition instead of a story.
"Before APIs existed, developers had to..." is wrong.
Right: Name the company, name the problem, show the pain. Then: "APIs solved this."

**W2 most common failure:** Tradeoffs that describe options without recommending one.
Every W2 tradeoff must end: "Default to X unless [specific condition Y], in which case Z."

**W3 best practice:** Each question includes "(this reveals: [what the answer shows])" in parentheses.
This turns questions into interrogation guides, not just conversation starters.

**S3 best practice:** Take a side in the debate. State your position, acknowledge the other,
explain why the tension is genuine. Don't just list positions and say "smart PMs disagree."

**Level selector default:** Set `difficulty: foundation` for all tech-tagged lessons.
Set `difficulty: working` for product-tagged lessons.
Set `difficulty: working` for business-tagged lessons.

**QA panel rule:** Always read qa_panel from _CONCEPT_INDEX.md, not from tags alone.
The cross-pairing rules (engineer writer → junior PM reader in panel) matter.

**Level markers:** The exact format required by the dashboard parser:
```
# ═══════════════════════════════════
# FOUNDATION
# ═══════════════════════════════════
```
Do not vary this format. The parser splits on `# ═══` lines.
