# Skill: Lesson Formatter

## Purpose
Transform structurally correct lesson content into visually scannable markdown.
Run AFTER content QA passes. Does NOT change meaning — only restructures presentation.
Triggered by: /format-lesson command OR automatically when pm_swarm.py sets run_formatter: true.

## Markdown components available (dashboard renders all of these)

### Callout boxes
```
> **Key concept:** Definition here.
> Supporting detail on second line.
```
Use for: definitions in F2, key insights, the "bottom line" of a decision.

### Warning callouts
```
> ⚠️ **Watch out:** Risk or common mistake here.
```
Use for: security gaps, common PM mistakes, "never do this without asking."

### Tip callouts
```
> 💡 **PM tip:** Actionable advice here.
```
Use for: the single most important thing a PM should do with this knowledge.

### Comparison tables (W2 decisions)
```
| | Option A | Option B |
|---|---|---|
| Best for | ... | ... |
| Risk | ... | ... |
| **Default** | **Use this** | Only when... |
```
Use for: any tradeoff section with 2+ named options.

### Company example cards (W4)
```
### Company Name — one-line headline

**What they did:** ...
**Why it worked:** ...
**PM takeaway:** ...
```
Use for: every real product example.

### Quick reference box (top of Working Knowledge)
```
> **Quick reference — [lesson title]**
> **What:** One sentence definition
> **When:** The 2 most common PM moments
> **Default:** The recommendation for most situations
```

### Engineer question format (W3)
```
**Question:** [The question to ask]
*What the answer reveals: [one line on what good vs bad answers look like]*
```

### Section summary (bottom of each level)
```
---
**Level summary:** One sentence on what this level covered and what to read next.
```

## Formatting rules by section

| Section | If you see | Transform to |
|---|---|---|
| F2 (What it is) | Dense definition paragraph | Callout box |
| F2 (What it is) | Multiple variants listed inline | Bullet list with one-line each |
| F3 (PM encounters) | Bold label + long paragraph | Bold label on own line + short para |
| W1 (How it works) | Numbered steps >20 words each | Bold action word + detail line |
| W2 (Decisions) | Bold paragraph blocks per option | Comparison table + recommendation callout |
| W3 (Questions) | Numbered questions only | Question bold + italic "reveals" line |
| W4 (Examples) | Bold company + prose | Company card format |
| S1 (What breaks) | Prose failure modes | Bold failure name + indented mechanism |
| S3 (Debate) | Position A and B in same paragraph | Separate labeled blocks + synthesis |

## What NOT to format
- F1 (The world before) — keep as narrative prose. It's a story.
- S2 (System connections) — keep as → link format. Already scannable.
- Do not add tables where a list is cleaner.
- Do not add callouts to every paragraph — max 2 callouts per level.
- Do not reorder sections or change headings.
