# PM Knowledge Base

An autonomous content intelligence system. Structured knowledge content that reviews itself, scores itself, and improves itself — using a swarm of specialized AI agents.

Built by one person with a Python script and an Anthropic API key.

---

## What it does

Most content gets written once and left to degrade. This system runs a continuous improvement loop:

```
Write → Review → Score → Fix → Measure → Repeat
```

**Write.** Lessons are written in a structured v2 format with three depth levels (Foundation, Working Knowledge, Strategic Depth) and persona-driven quality bars baked in from the start.

**Review.** A swarm of 11 specialized AI agents reads each lesson simultaneously — each from a distinct human lens. Not a single generic reviewer. Eleven: a non-technical biz PM, an ex-engineer PM, an MBA PM, a growth PM, a designer-turned-PM, an enterprise PM, a senior PM, a Gen-Z AI-native PM, and others. Each flags issues specific to how *they* would read the content.

**Score.** A synthesizer agent aggregates all 11 reviews into a ranked flag list (Critical / High / Medium) with per-level scores (Foundation / Working / Strategic) and an overall health rating.

**Fix.** A formatter agent applies targeted transforms to flagged sections — not the whole lesson. W2 missing a comparison table? Added. Foundation section too dense? Restructured. Score re-measured after fix.

**Measure.** Every run produces a FEEDBACK report. The mission control dashboard shows improvement deltas over time.

---

## The numbers

| Metric | Value |
|---|---|
| Lessons written | 32 |
| Lessons scored | 32 |
| Average quality score | 6.9 / 10 |
| Highest score | 7.4 / 10 (Error Codes & Response Design) |
| Lowest score | 6.6 / 10 |
| Total planned lessons | 88 across 9 modules |
| Agents in the swarm | 13 (11 PM personas + synthesizer + formatter) |
| Cost per review run | ~$0.04 (Haiku fast mode) |
| Total API cost to date | ~$1.28 |

---

## The system

```
pm_swarm.py          11-agent review swarm
pm_format.py         Section-by-section formatter
control/data.py      Parses FEEDBACK reports → data.json
control/index.html   Mission control dashboard (live ops)
dashboard/index.html Lesson reader (3 levels, AI notes, search)
```

**After every swarm run**, `control/data.json` updates automatically. The mission control dashboard reflects the change within 15 seconds — no manual step.

---

## Dashboards

**Lesson reader** — read any lesson at three depth levels. Select text and ask Claude for context. Notes persist per lesson.

**Mission control** — live ops view. Agent swarm panel shows which agents are active/queued/done with animated status. Content health panel shows all lesson scores with sparklines, sortable by score or module. Score delta flash when data updates. Lesson rows are clickable — full score breakdown, flags, and metadata slide in from the right.

---

## What's coming next

**Layer 4 — Spy agent.** An agent that watches how real humans consume content — where they slow down, what they highlight, what they skip, where they leave — and feeds that behavioral signal back into the improvement loop. Content improves based on real reader behavior, not just agent opinions.

The friction signals already exist in the lesson reader dashboard (localStorage). The spy agent is the bridge between that raw behavioral data and the swarm.

---

## Run it yourself

You need Python 3.9+, an Anthropic API key, and your own markdown content.

```bash
git clone https://github.com/loadingpeacefully/pm-knowledge-base
cd pm-knowledge-base

# Set your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the swarm on any lesson
python3 pm_swarm.py concept-library/01-apis-and-integration/what-is-an-api.md --mode fast

# View the FEEDBACK report
cat concept-library/01-apis-and-integration/FEEDBACK_what-is-an-api.md

# Update the mission control dashboard
python3 control/data.py

# Start the dashboards
python3 -m http.server 8080   # lesson reader → localhost:8080/dashboard/
python3 -m http.server 8081   # mission control → localhost:8081/control/
```

**To run on your own content:**
- Drop your markdown files into `concept-library/`
- Update `_CONCEPT_INDEX.md` with your lesson IDs and titles
- Run `pm_swarm.py` on any file
- The rest is automatic

---

## The curriculum

A PM knowledge base covering the technical and strategic concepts product managers encounter but rarely learned formally.

| Module | Topic | Status |
|---|---|---|
| 01 | APIs & System Integration | 10/10 complete |
| 02 | Databases & Data | 10/10 complete |
| 03 | Infrastructure & DevOps | 6/10 complete |
| 04 | AI & ML Systems | 0/9 — next |
| 05 | Product Fundamentals | 0/9 |
| 06 | Metrics & Analytics | 1/6 |
| 07 | Business & Monetization | 1/7 |
| 08 | GTM & Growth | 1/8 |
| 09 | Security & Scale | 0/8 |

Each lesson has three depth levels so different PMs can read the same content at the right altitude — Foundation for context, Working Knowledge for day-to-day application, Strategic Depth for senior decision-making.

---

## Why this exists

Documentation and training content goes stale the moment it's written. Humans can't review everything continuously. AI agents can.

The system treats content quality as an engineering problem — observable, measurable, improvable. Every lesson has a score. Every score can go up. The loop runs autonomously.

The PM curriculum is the proof of concept. The loop works on any structured knowledge content.

---

## What's not in this repo

The Anthropic API key (`.env` — gitignored).
The FEEDBACK reports (`FEEDBACK_*.md` — gitignored, generated artifacts).
The swarm runtime log (`control/swarm_status.json` — gitignored, ephemeral).

---

*Built with Claude Sonnet and Haiku via the Anthropic API.*
*Lesson reader and mission control run as static HTML — no backend required.*
