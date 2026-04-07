# PM Knowledge Base — System Audit
Generated: 2026-04-07
Auditor: Claude Code (claude-sonnet-4-6)

---

## Executive summary

The PM Knowledge Base is a functioning two-part system: a 219-file read-only KB sourced from BrightChamps production systems, and a 26-lesson concept library curriculum (all v2 format, all status: ready). Two Python scripts (pm_swarm.py, pm_format.py) handle automated QA and formatting; the lesson reader dashboard (dashboard/index.html) is fully working with level selector, AI notes, and all markdown components. The mission control dashboard is entirely unbuilt — no control/ directory, no data pipeline, no UI. The primary gap between the current system and a working mission control dashboard is three missing files: control/data.py, control/data.json, and control/index.html.

---

## What exists — complete inventory

### Knowledge base (KB)

- **218 files** across 4 categories + assets
- All files read-only — never modified by Claude Code (enforced by settings.json deny rules)

| Category | Files | Description |
|---|---|---|
| technical-architecture/ | 133 | API specs, architecture docs, CRM flows, ETL jobs, infra, payments, student lifecycle, teacher management |
| product-prd/ | 64 | PRDs, portfolio docs, feature specs, AI worksheets, gamification |
| research-competitive/ | 18 | LingoAce competitive intel, adaptive learning, reddit research |
| performance-reviews/ | 3 | Apr24-Mar25, Mar23-Apr24 performance reviews |
| assets/ | 1 | _index.md |

Key KB subdirectories (technical-architecture):
- api-specifications/ (14 files) — API endpoint docs
- architecture/ (3 files) — architecture-overview.md, auth flows, DB design
- crm-and-sales/ (14 files) — Zoho CRM, lead flows, sales pipelines
- etl-and-async-jobs/ (4 files) — ETL inventory, feed ETL, marketing ETL
- infrastructure/ (12 files) — infra-monitoring, web app optimization, server docs
- payments/ (15 files) — 7 payment gateways, payment flows
- student-lifecycle/ (30 files) — booking, demos, onboarding, post-class
- teacher-management/ (5 files) — onboarding, payout, teacher change

---

### Concept library (curriculum)

- **26 lessons** written, all v2 format (6 level markers each), all status: ready
- **62 lessons** remaining across 6 modules (88 total planned)
- All 26 lessons have passed the 11-agent swarm QA + pm_format.py pipeline
- **26 lessons** have FEEDBACK reports (all lessons now covered)

| Module | Total planned | Written | Remaining |
|---|---|---|---|
| 01 — APIs & Integration | 10 | 10 (complete) | 0 |
| 02 — Databases & Data | 10 | 10 (complete) | 0 |
| 03 — Infrastructure & DevOps | 10 | 3 (03.01, 03.02, 03.04) | 7 |
| 04 — AI & ML Systems | 9 | 0 | 9 |
| 05 — Product Fundamentals | 9 | 0 | 9 |
| 06 — Metrics & Analytics | 6 | 1 (06.01) | 5 |
| 07 — Business & Monetization | 7 | 1 (07.01) | 6 |
| 08 — GTM & Growth | 8 | 1 (08.01) | 7 |
| 09 — Security & Scale | 9 | 0 | 9 |
| **Total** | **88** | **26** | **62** |

Module 03 remaining: 03.03 Kubernetes, 03.05 Infrastructure as Code, 03.06 Queues & Message Brokers, 03.07 CDN & Edge Caching, 03.08 Load Balancing, 03.09 Monitoring & Alerting, 03.10 Feature Flags

---

### Scripts

| Script | Purpose | Input | Output | Lines | Status |
|---|---|---|---|---|---|
| pm_swarm.py | 11-agent PM feedback swarm | lesson .md path | FEEDBACK_lesson.md | 837 | WORKING |
| pm_format.py | Section-by-section markdown formatter | lesson .md + optional FEEDBACK report | formatted .md + .bak backup | 172 | WORKING |
| _debug_synth{1-4}.py | Synthesizer debugging artifacts | — | — | — | DELETE — run `rm _debug_synth*.py` |

**pm_swarm.py detail:**
- 11 agents: P1 Priya (non-tech biz PM), P2 Arjun (ex-engineer PM), P3 Sofia (MBA PM), P4 Rahul (aspiring PM), P5 Meera (growth/data PM), P6 Lena (UX designer PM), P7 Vikram (enterprise B2B PM), P8 Anya (consumer startup PM), P9 Zain (AI-native PM), P10 Deepa (senior PM / HoP), D1 Nadia (senior product designer)
- Fast mode: claude-haiku-4-5-20251001 (~$0.04/lesson)
- Full mode: claude-sonnet-4-6 (~$0.40/lesson)
- Parallel workers: 5 (rate-limit safe)
- Output schema: health, avg_score, level_scores, ranked fixes (CRITICAL/HIGH/MEDIUM), formatting_flags, run_formatter

**pm_format.py detail:**
- Model: claude-haiku-4-5-20251001
- Splits lesson by `## ` section headers, reformats each independently
- `--from-report`: reads formatting_flags from FEEDBACK report to target specific sections
- Known behavior: always injects AI response artifact between `---` and first `# ═══` marker — must be stripped manually after every run
- Backup: always saves .bak before overwriting

---

### Dashboards

| Dashboard | Path | Purpose | Lines | Status |
|---|---|---|---|---|
| Lesson reader | dashboard/index.html | Read lessons, 3 levels, AI notes, search | 1208 | WORKING |
| Mission control | control/index.html | Agent + content health + learner view | — | NOT BUILT |

**Lesson reader dashboard features:**
- Level selector (Foundation / Working Knowledge / Strategic Depth) — persisted per lesson in localStorage
- v2 lesson parsing: splits on `# ═══` markers, extracts profile lists from frontmatter
- AI notes: text selection → "Ask AI" button → streams from Anthropic API (key from config.js or localStorage)
- Manual notes: per-lesson, stored in localStorage
- Search: filters sidebar by lesson title in real-time
- Collapsible module sidebar with status dots (ready/draft/—)
- Markdown renderer (renderMd): headings, blockquotes (4 variants: default/warning/tip/info), tables (with rec row tinting), ordered/unordered lists, code, inline bold/italic, links, → arrows, quick-ref boxes
- ANTHROPIC_KEY: loaded from dashboard/config.js (placeholder `YOUR_KEY_HERE`) or localStorage fallback — not hardcoded

**Known limitation:** config.js is currently a placeholder. First-time users must enter key via the settings modal (⚙ icon) — stored in localStorage. Key is never committed to git.

---

### Claude Code infrastructure

| File | Purpose | Lines | Status |
|---|---|---|---|
| CLAUDE.md | Project memory, v2 architecture spec, writer personas, folder structure | 183 | CURRENT |
| .claude/skills/lesson-writer.md | Quality bars per level, section requirements | 138 | CURRENT |
| .claude/skills/lesson-qa.md | 12-guardrail QA panel, cross-pairing rules | 222 | CURRENT |
| .claude/skills/lesson-formatter.md | Formatting transforms, callout patterns | 88 | CURRENT |
| .claude/skills/kb-reader.md | KB abstraction rules, read-only constraints | 20 | CURRENT |
| .claude/skills/writer-personas.md | 4 writer personas (staff-eng PM, senior PM, CFO, GTM lead) | 86 | CURRENT |
| .claude/commands/new-lesson.md | 7-phase lesson write + QA pipeline | 57 | CURRENT |
| .claude/commands/rewrite-lesson.md | v1→v2 migration command | 30 | CURRENT |
| .claude/commands/qa-lesson.md | QA panel run | 14 | CURRENT |
| .claude/commands/review-lesson.md | Fix criticals + re-QA | 32 | CURRENT |
| .claude/commands/daily-start.md | Session start — read tasks.md + _CONCEPT_INDEX | 21 | CURRENT |
| .claude/commands/status.md | Project status summary | 19 | CURRENT |
| .claude/commands/kb-search.md | KB search command | 11 | CURRENT |
| .claude/commands/module-plan.md | Module planning command | 12 | CURRENT |
| .claude/settings.json | Auto-allow/deny rules for tools | — | CURRENT |

**Settings.json rules:**
- Auto-allow: Read(**), Edit(concept-library/**), Edit(dashboard/index.html), Edit(tasks.md), Edit(decisions.md), Edit(memory.md), Edit(CLAUDE.md), Edit(.claude/**), Bash(find/grep/ls/wc/mkdir/cat/cp)
- Auto-deny: Edit(_REGISTRY.md), Edit(technical-architecture/**), Edit(product-prd/**), Edit(research-competitive/**), Edit(performance-reviews/**), Bash(rm/**), Bash(mv/**), Bash(curl/**)
- Requires approval: Bash(python3:*), Bash(head:*), Write(**), and anything not in allow/deny lists

---

## Data flow map

```
_CONCEPT_INDEX.md (concept-library/_CONCEPT_INDEX.md)
  → READ BY: pm_swarm.py — gets lesson file path from ID
  → READ BY: dashboard/index.html — builds sidebar module/lesson list
  → WRITTEN BY: Claude Code (new-lesson command) — updates status column

concept-library/[module]/[lesson].md
  → READ BY: pm_swarm.py — lesson content for all 11 agents
  → READ BY: pm_format.py — content to reformat section by section
  → READ BY: dashboard/index.html — fetch() on lesson select
  → WRITTEN BY: Claude Code — initial lesson write
  → WRITTEN BY: pm_format.py — saves formatted version (also creates .bak)

concept-library/[module]/FEEDBACK_[lesson].md
  → WRITTEN BY: pm_swarm.py — after each swarm run
  → READ BY: pm_format.py — extracts formatting_flags when --from-report used
  → READ BY: control/data.py — DOES NOT EXIST YET

.env (repo root)
  → READ BY: pm_swarm.py — ANTHROPIC_API_KEY
  → READ BY: pm_format.py — ANTHROPIC_API_KEY

dashboard/config.js
  → READ BY: dashboard/index.html — PM_CONFIG.ANTHROPIC_API_KEY for AI notes

control/data.json — DOES NOT EXIST
  → WOULD BE WRITTEN BY: control/data.py
  → WOULD BE READ BY: control/index.html

control/data.py — DOES NOT EXIST
  → WOULD READ: FEEDBACK_*.md (all 24+ reports), _CONCEPT_INDEX.md
  → WOULD WRITE: control/data.json

control/index.html — DOES NOT EXIST
  → WOULD READ: control/data.json
  → WOULD READ: pm_swarm.py (AGENTS list — agent definitions)
```

---

## Lesson health table

| ID | Title | Module | Words | Score | F / W / S | Flags (C/H/M) | Feedback report |
|---|---|---|---|---|---|---|---|
| 01.01 | What is an API | 01 | 4488 | 7.0 | 7.2/7.0/7.0 | 3/22/46 | YES |
| 01.02 | API Authentication | 01 | 4073 | 6.9 | 7.2/6.5/7.0 | 4/24/38 | YES |
| 01.03 | Webhooks vs Polling | 01 | 4226 | 7.2 | 7.4/7.0/7.3 | 6/30/45 | YES |
| 01.04 | Rate Limiting & Throttling | 01 | 3704 | 6.9 | 6.7/7.0/7.0 | 4/24/35 | YES |
| 01.05 | Idempotency | 01 | 4501 | 7.1 | 7.2/6.3/7.3 | 5/29/47 | YES |
| 01.06 | API Versioning | 01 | 4028 | 7.0 | 7.2/7.0/7.0 | 8/27/44 | YES |
| 01.07 | Pagination | 01 | 4195 | 6.9 | 7.2/7.0/6.7 | 5/22/41 | YES |
| 01.08 | API Gateway | 01 | 4782 | 6.9 | 7.2/6.7/7.0 | 5/28/44 | YES |
| 01.09 | Error Codes & Response Design | 01 | 4953 | 7.4 | 7.5/7.2/7.3 | 4/19/52 | YES |
| 01.10 | Third-Party Integration Patterns | 01 | 5262 | 7.1 | 7.3/6.5/7.3 | 3/25/38 | YES |
| 02.01 | SQL vs NoSQL | 02 | 5067 | 6.7 | 7.2/5.0/7.0 | 5/22/41 | YES |
| 02.02 | Indexing | 02 | 5319 | 6.9 | 7.3/6.8/6.7 | 5/26/44 | YES |
| 02.03 | Transactions & ACID | 02 | 6153 | 6.7 | 7.2/6.3/7.0 | 11/27/50 | YES |
| 02.04 | Caching (Redis) | 02 | 6246 | 7.0 | 7.2/7.0/7.0 | 2/24/42 | YES |
| 02.05 | Data Warehouses vs Databases | 02 | 6664 | 7.1 | 7.2/7.0/7.0 | 4/20/37 | YES |
| 02.06 | ETL Pipelines | 02 | 6654 | 6.9 | 7.3/7.0/6.3 | 4/21/39 | YES |
| 02.07 | Schema Design Basics | 02 | 6617 | 6.9 | 7.3/6.7/6.5 | 4/28/52 | YES |
| 02.08 | Soft Delete vs Hard Delete | 02 | 6162 | 7.1 | 7.2/7.0/7.3 | 4/29/50 | YES |
| 02.09 | PII & Data Privacy | 02 | 7058 | 6.8 | 6.8/6.5/7.0 | 6/31/46 | YES |
| 02.10 | Data Replication & Backups | 02 | 6886 | 6.9 | 7.0/6.7/7.0 | 7/26/46 | YES |
| 03.01 | Cloud Infrastructure Basics | 03 | 7040 | 6.7 | 6.5/7.0/6.3 | 5/21/48 | YES |
| 03.02 | Containers & Docker | 03 | 6236 | 6.8 | 6.8/6.6/7.0 | 7/27/48 | YES |
| 03.04 | CI/CD Pipelines | 03 | 4009 | 6.7 | 7.3/6.5/7.0 | 10/28/44 | YES |
| 06.01 | North Star Metric | 06 | 4178 | 7.3 | 7.6/7.0/7.3 | 3/23/44 | YES |
| 07.01 | Unit Economics | 07 | 4635 | 7.3 | 7.3/7.0/7.3 | 4/22/41 | YES |
| 08.01 | Go-To-Market Strategy | 08 | 4867 | 7.0 | 7.2/7.0/7.0 | 4/26/45 | YES |

**Aggregate stats:**
- Average score (26 lessons): **7.0 / 10**
- Highest score: 01.09 Error Codes & Response Design (7.4)
- Lowest score: 02.01 SQL vs NoSQL (6.7), 02.03 Transactions & ACID (6.7), 03.04 CI/CD Pipelines (6.7), 03.01 Cloud Infrastructure Basics (6.7)
- Average word count: ~5,480 words/lesson
- Lessons without feedback: 0 (all 26 now have reports)

---

## What the mission control dashboard needs

For the dashboard to show real data, these inputs must exist:

| Dashboard panel | Data needed | Source | Exists? |
|---|---|---|---|
| Content health — lesson list | All lessons + status + module | _CONCEPT_INDEX.md | YES — parseable |
| Content health — scores | Per-lesson avg score, F/W/S breakdown | FEEDBACK_*.md | YES — 24 reports |
| Content health — flags | Critical/high/medium counts per lesson | FEEDBACK_*.md | YES — 24 reports |
| Content health — score trend | Score change across re-runs | Multiple FEEDBACK runs | PARTIAL — single run per lesson |
| Content health — formatter status | Which lessons need formatting | run_formatter field in FEEDBACK | YES — parseable |
| Agent swarm — agent definitions | 11 agent names, roles, scoring lens | pm_swarm.py AGENTS list | YES — parseable |
| Agent swarm — live activity | Running process, which agent is active | pm_swarm.py stdout | NO — no log file |
| Agent swarm — run history | When each lesson was last scored | FEEDBACK file timestamps | YES — file mtime |
| Lesson writer — word counts | Word count per level per lesson | Lesson .md files | YES — parseable |
| Learner pulse — reading progress | Who read which lessons, which level | Not built | NO |
| Learner pulse — drop-offs | Where readers exit each lesson | Not built | NO |
| Learner pulse — notes | AI notes / manual notes content | localStorage (client-side only) | NO — not persisted server-side |
| Module completion — % done | Lessons ready / total per module | _CONCEPT_INDEX.md | YES — parseable |

---

## Gaps — what needs to be built for mission control

**Gap 1 — control/data.py** *(HIGH priority, ~2 hours)*
Parse all FEEDBACK_*.md reports + _CONCEPT_INDEX.md and output control/data.json.
Data fields needed: lesson_id, title, module, status, word_count, score_avg, score_foundation, score_working, score_strategic, flag_counts (C/H/M), health, run_formatter, last_qa_date, feedback_file_path.
Agent definitions can be extracted from pm_swarm.py (AGENTS list is a Python literal — parseable with ast).

**Gap 2 — control/data.json** *(blocks everything)*
Does not exist. Output of Gap 1. Required before any dashboard UI can show real data.

**Gap 3 — control/index.html** *(HIGH priority, ~4 hours)*
The mission control UI itself. Three panels:
- Content health: lesson table with scores, flags, health badges, module completion progress bars
- Swarm agent grid: 11 agent cards (id, name, role, scoring_lens)
- Pipeline status: modules, lesson counts, avg scores, next lesson to write

**Gap 4 — Swarm live-run log** *(MEDIUM priority, ~1 hour)*
pm_swarm.py currently writes only the final FEEDBACK report. Real-time agent activity requires stdout capture to a log file (e.g., `swarm_run.log`), or a `--log` flag. Mission control "live activity" panel depends on this.

**Gap 5 — Learner analytics** *(LOW priority — different system entirely)*
Notes are localStorage-only and never leave the browser. Progress, drop-offs, and reading time cannot be tracked without a backend. Out of scope for local-first tools.

**Gap 6 — control/data.py auto-refresh** *(MEDIUM priority)*
data.json is a point-in-time snapshot. For mission control to stay current, data.py should be runnable on demand (button in UI) or on a file-watcher schedule (watchdog is not installed — would need install).

---

## Recommended build order

1. **control/data.py** — parse FEEDBACK reports + index → data.json. No UI dependency. Can build and test in isolation.
2. **control/data.json** — generated by running data.py once. Verifies the parser works.
3. **control/index.html** — the dashboard UI. Read from data.json. Three panels: content health table, agent grid, module progress.
4. **Refresh button** — add a "Refresh data" call in control/index.html that re-runs data.py via a local server or manual CLI step.
5. **Swarm log** — add `--log swarm_run.log` flag to pm_swarm.py if live activity panel is a priority.
6. **Learner analytics** — future work. Requires backend or at minimum a server-side notes sync.

The minimum viable mission control (Gaps 1–3) requires roughly one focused session.

---

## Raw data

### Feedback scores by lesson (sorted by score)

| Score | Lesson |
|---|---|
| 7.4 | Error Codes & Response Design (01.09) |
| 7.3 | North Star Metric (06.01) |
| 7.3 | Unit Economics (07.01) |
| 7.2 | Webhooks vs Polling (01.03) |
| 7.1 | Third-Party Integration Patterns (01.10) |
| 7.1 | Data Warehouses vs Databases (02.05) |
| 7.1 | Soft Delete vs Hard Delete (02.08) |
| 7.0 | What is an API (01.01) |
| 7.0 | API Versioning (01.06) |
| 7.0 | Caching (Redis) (02.04) |
| 7.0 | Go-To-Market Strategy (08.01) |
| 6.9 | API Authentication (01.02) |
| 6.9 | Pagination (01.07) |
| 6.9 | API Gateway (01.08) |
| 6.9 | Indexing (02.02) |
| 6.9 | ETL Pipelines (02.06) |
| 6.9 | Schema Design Basics (02.07) |
| 6.9 | Rate Limiting & Throttling (01.04) |
| 6.9 | Data Replication & Backups (02.10) |
| 6.8 | PII & Data Privacy (02.09) |
| 6.8 | Containers & Docker (03.02) |
| 6.7 | SQL vs NoSQL (02.01) |
| 6.7 | Transactions & ACID (02.03) |
| 6.7 | CI/CD Pipelines (03.04) |
| 6.7 | Cloud Infrastructure Basics (03.01) |

### Dependency check

```
anthropic:  0.40.0  ✓
Python:     3.9.6   ✓
Node.js:    24.13.0 ✓ (available for future tooling)
watchdog:   NOT INSTALLED (needed for auto-refresh if required)
.env:       ANTHROPIC_API_KEY present (sk-ant-api03-...)
```
