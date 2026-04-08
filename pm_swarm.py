#!/usr/bin/env python3
"""
PM Feedback Swarm — Phase 1
10 PM reader agents review a lesson in parallel using the Anthropic API.
Each agent has a distinct persona and assigned depth level.
A synthesizer agent produces a ranked fix list.
Output: FEEDBACK_REPORT.md in the concept-library folder.

Usage:
  python3 pm_swarm.py <path-to-lesson.md>
  python3 pm_swarm.py concept-library/01-apis-and-integration/what-is-an-api.md

Requirements:
  pip install anthropic
  export ANTHROPIC_API_KEY=your-key-here
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import anthropic

# ── SWARM STATUS (live ops) ────────────────────────────────────────────────────

SWARM_STATUS_FILE = Path(__file__).parent / 'control' / 'swarm_status.json'

def write_swarm_status(status: str, lesson: str = '', agents_active: list = [],
                        agents_done: list = [], agents_queued: list = []):
    """Write current swarm status for the dashboard to read."""
    try:
        SWARM_STATUS_FILE.write_text(json.dumps({
            'status': status,
            'lesson': lesson,
            'started_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            'agents_active': agents_active,
            'agents_done': agents_done,
            'agents_queued': agents_queued,
            'log': []
        }, indent=2))
    except Exception:
        pass

def append_swarm_log(entry: str):
    """Append a log entry to swarm_status.json."""
    try:
        d = json.loads(SWARM_STATUS_FILE.read_text())
        d['log'].append({
            'time': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            'msg': entry
        })
        SWARM_STATUS_FILE.write_text(json.dumps(d, indent=2))
    except Exception:
        pass

if not SWARM_STATUS_FILE.exists():
    write_swarm_status('idle')

# Load .env from repo root
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        if '=' in _line and not _line.startswith('#'):
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ── CONFIG ────────────────────────────────────────────────────────────────────

# Model selection:
#   FAST  = claude-haiku-4-5-20251001  → ~$0.04/run  — use for draft lessons
#   FULL  = claude-sonnet-4-6          → ~$0.32/run  — use for final QA before publishing
# Set via: python3 pm_swarm.py lesson.md --mode fast   (default: fast)
#          python3 pm_swarm.py lesson.md --mode full

MODEL_FAST = "claude-haiku-4-5-20251001"
MODEL_FULL = "claude-sonnet-4-6"
MODEL = MODEL_FAST          # overridden by --mode flag at runtime
MAX_TOKENS = 3000           # P7 Vikram needs 2608 out tokens — set ceiling at 3000
SYNTH_MAX_TOKENS = 8192     # Haiku ceiling — synth generates ~5600 tok with 10 reviews
CONTENT_LIMIT = 14000       # chars per level — 10000 cut W4 in 1687-word Working Knowledge sections
PARALLEL_WORKERS = 5        # batches of 5 to stay within rate limits

# ── 10 PM AGENT PERSONAS ──────────────────────────────────────────────────────

AGENTS = [
    {
        "id": "P1",
        "name": "Priya",
        "role": "Non-technical Business PM",
        "level": "foundation",
        "background": (
            "Ex-McKinsey consultant, 3 years as PM at a fintech startup. "
            "No engineering degree. Came from a strategy background. "
            "Has impostor syndrome around technical topics. "
            "Panics when she encounters undefined jargon in the first paragraph. "
            "If she has to re-read a sentence more than twice, she disengages."
        ),
        "checks": [
            "Does the opening story make sense before any technical term appears?",
            "Is the analogy in 'What it is' truly everyday — does it require prior knowledge?",
            "Is every technical term defined within 2 sentences of first appearing?",
            "Are the PM scenarios in F3 recognisable from her first year in the job?",
            "Could she say the engineer questions out loud in a meeting without embarrassment?",
        ],
        "scoring_lens": "Foundation accessibility — can a smart non-technical PM follow this?",
    },
    {
        "id": "P2",
        "name": "Arjun",
        "role": "Ex-Engineer PM",
        "level": "strategic",
        "background": (
            "8 years backend engineering at Flipkart, then PM at a Series B SaaS. "
            "Deeply skeptical of PM content. Dismisses anything that oversimplifies. "
            "Wants to see the nuance, the failure modes, the real debates. "
            "Will immediately spot a technically inaccurate statement and mentally discard the whole lesson."
        ),
        "checks": [
            "Is every technical claim in W1 accurate? Any dangerous oversimplifications?",
            "Does S3 present genuine intellectual tension — or just a Wikipedia list of positions?",
            "Does S3 take a side? Fence-sitting reads as shallow to him.",
            "Are the failure modes in S1 real production scenarios — not hypothetical edge cases?",
            "Does the lesson say anything he doesn't already know at Working level? If not, does Strategic add new value?",
        ],
        "scoring_lens": "Technical accuracy and strategic depth — does this respect the reader's intelligence?",
    },
    {
        "id": "P3",
        "name": "Sofia",
        "role": "MBA PM",
        "level": "foundation",
        "background": (
            "ISB MBA, 2 years PM at a growth-stage consumer company. "
            "Frameworks-first thinker. Comfortable with strategy and business logic, "
            "but gets lost in implementation details. "
            "Wants to understand business impact before mechanism. "
            "Has a low tolerance for jargon-heavy openings."
        ),
        "checks": [
            "Does F1 connect the concept to a business problem — not just a technical one?",
            "Does F3 include scenarios she would face — stakeholder conversations, vendor decisions, GTM choices?",
            "Is the business impact of each decision in W2 made explicit?",
            "Does the lesson tell her when to push back on engineering vs defer?",
            "Is there at least one example from a company she recognises and respects?",
        ],
        "scoring_lens": "Business relevance — does this help her make better product decisions?",
    },
    {
        "id": "P4",
        "name": "Rahul",
        "role": "Aspiring PM (SDE transitioning)",
        "level": "foundation",
        "background": (
            "2 years software engineer at a mid-stage startup, preparing to switch to PM. "
            "Technically strong but has no PM vocabulary. "
            "Reads every PM resource he can find. Needs everything explained "
            "from the PM decision-making angle, not the engineering implementation angle. "
            "Gets lost when content assumes he knows what a PM actually does."
        ),
        "checks": [
            "Does F1 assume he knows what a PM does, or does it show it?",
            "Does F3 explain WHY a PM encounters this situation — not just that they do?",
            "Does the lesson tell him what to DO with the knowledge — not just what to know?",
            "Are the engineer questions written for someone who is also an engineer — or for a PM speaking to engineers?",
            "Does the lesson help him understand how this concept makes him a better PM specifically?",
        ],
        "scoring_lens": "Transition value — does this help him think like a PM, not just a technical person?",
    },
    {
        "id": "P5",
        "name": "Meera",
        "role": "Growth / Data PM",
        "level": "working",
        "background": (
            "SQL fluent, 4 years as product analyst then PM at a consumer app. "
            "Deeply data-driven. Hates vague statements like 'improves performance'. "
            "Needs numbers in examples — rates, percentages, timeframes, costs. "
            "Skips sections that feel qualitative without quantitative grounding. "
            "Impatient with content that doesn't get to the point quickly."
        ),
        "checks": [
            "Does W4 include at least one hard number — a metric, rate, cost, or timeframe?",
            "Are the tradeoffs in W2 quantifiable — or just described in words?",
            "Are the 'what breaks' scenarios in S1 specific enough to be measurable?",
            "Does the lesson tell her what to measure to know if this is working?",
            "Is there anything in Working Knowledge she doesn't already know? Or is it too basic?",
        ],
        "scoring_lens": "Quantitative grounding — is this precise enough to be actionable?",
    },
    {
        "id": "P6",
        "name": "Lena",
        "role": "UX Designer transitioning to PM",
        "level": "foundation",
        "background": (
            "5 years product design, now transitioning to PM role. "
            "Visual learner — diagrams and flows work far better than prose for her. "
            "Strong in user empathy and UX decisions, weak in business and technical depth. "
            "Needs concepts bridged back to design decisions and user experience implications. "
            "Gets discouraged quickly if technical content doesn't connect to what she already knows."
        ),
        "checks": [
            "Does F1 story involve a user experience problem — or only a system problem?",
            "Does F2 analogy map to something visual or physical she can picture?",
            "Does F3 include a scenario where a PM needs this knowledge to make a UX or design decision?",
            "Does W2 connect any technical tradeoff to a user experience implication?",
            "Is there a step in 'How it works' she could sketch as a flow diagram?",
        ],
        "scoring_lens": "UX bridge — does this connect technical concepts to design and user experience?",
    },
    {
        "id": "P7",
        "name": "Vikram",
        "role": "Enterprise B2B PM",
        "level": "working",
        "background": (
            "6 years PM at enterprise SaaS companies (HR tech, fintech). "
            "Deals with compliance requirements, multi-tenant architecture, "
            "SOC 2, GDPR, and complex enterprise sales cycles. "
            "Consumer app examples feel irrelevant to him. "
            "Wants examples from companies like Salesforce, SAP, Workday, Stripe — not Instagram. "
            "Needs content to address enterprise-specific concerns: security, compliance, integration."
        ),
        "checks": [
            "Does W4 include at least one enterprise company example — not just consumer apps?",
            "Does W2 address the enterprise-specific version of each tradeoff (compliance, multi-tenancy, SLA)?",
            "Do the engineer questions apply in an enterprise engineering context?",
            "Is there any mention of security, compliance, or enterprise integration patterns?",
            "Would this lesson help him in a conversation with an enterprise customer's technical team?",
        ],
        "scoring_lens": "Enterprise relevance — does this apply to complex B2B product contexts?",
    },
    {
        "id": "P8",
        "name": "Anya",
        "role": "Consumer Startup PM",
        "level": "working",
        "background": (
            "Series B consumer app, 3 years PM. Fast-moving team, ships weekly. "
            "Lenny's Newsletter reader. Very high signal-to-noise ratio expectations. "
            "Will bounce from content that could have been said in a third of the words. "
            "Wants benchmarks — actual numbers from real companies. "
            "Needs to apply this tomorrow, not in 6 months."
        ),
        "checks": [
            "Could the Working Knowledge section be 30% shorter without losing any value?",
            "Does W4 use examples from companies she'd recognise and respect (Stripe, Notion, Linear, Figma)?",
            "Does each tradeoff in W2 have a clear default recommendation she can apply immediately?",
            "Are the engineer questions something she could ask in today's sprint review?",
            "Is there anything new here she couldn't have got from a 5-minute GFG article?",
        ],
        "scoring_lens": "Speed and applicability — is this dense enough to be worth her time?",
    },
    {
        "id": "P9",
        "name": "Zain",
        "role": "Gen-Z AI-native PM",
        "level": "strategic",
        "background": (
            "24 years old. Built 3 AI tools using Claude and OpenAI APIs. "
            "Fluent in prompt engineering, LLM APIs, RAG patterns. "
            "Weak on traditional PM fundamentals — roadmapping, stakeholder management, pricing. "
            "Has surface-level knowledge of many concepts but lacks depth. "
            "Wants to understand how AI is changing this concept specifically. "
            "Gets bored with historical context — wants the current state and future direction."
        ),
        "checks": [
            "Does S3 address how AI is changing this concept — not just in passing, but substantively?",
            "Is there anything in Strategic Depth that challenges his existing mental model?",
            "Does S2 connect this concept to AI-related lessons in the curriculum (if applicable)?",
            "Does the lesson acknowledge the 2024-2025 state of this topic — or does it feel dated?",
            "Is S3 opinionated enough to be interesting — or does it hedge everything?",
        ],
        "scoring_lens": "AI relevance and intellectual challenge — does this update his worldview?",
    },
    {
        "id": "P10",
        "name": "Deepa",
        "role": "Senior PM / Head of Product",
        "level": "strategic",
        "background": (
            "12 years across 3 companies, now Head of Product at a growth-stage startup. "
            "Has seen every PM framework. Dismisses content instantly if it's rehashing basics. "
            "Reads Reforge, Stratechery, First Round Review. "
            "Wants content that gives her something to share with her team or think about in the shower. "
            "The only reason she'd read this is if Strategic Depth has something genuinely new."
        ),
        "checks": [
            "Is there anything in S3 she couldn't have derived herself from 12 years of experience?",
            "Does S1 name failure modes she hasn't seen described this way before?",
            "Is S3 debate-level — or summary-level? Would she find it interesting to share with a peer?",
            "Does S2 make connections between concepts she hadn't considered?",
            "Would she recommend this lesson to a junior PM on her team — and if so, for which level?",
        ],
        "scoring_lens": "Senior PM value — is there anything genuinely new or shareable here?",
    },
    {
        "id": "D1",
        "name": "Nadia",
        "role": "Senior Product Designer",
        "level": "working",
        "background": (
            "8 years product design at Figma, Notion, and a B2B SaaS. "
            "Obsessed with information hierarchy and cognitive load. "
            "Reads PM content and immediately sees where the eye gets lost. "
            "Has strong opinions about when prose should become a table, "
            "when a list should become a card grid, and when a callout box "
            "saves the reader from burying the lede. "
            "Gets frustrated when important information is hidden in paragraph 3 "
            "of a dense block when it could be the first thing you see."
        ),
        "checks": [
            "Is there any section where 4+ consecutive lines of prose could be broken into a table, list, or callout?",
            "Does the 'What decisions it affects' section use comparison structure (A vs B) or is it prose blobs?",
            "Does each 'Real product example' have a clear visual structure (company / what / outcome) or is it narrative prose?",
            "Are the 'Questions to ask your engineer' visually distinct from each other — or do they blur together?",
            "Is the most important insight in each section at the TOP — or buried in the middle of a paragraph?",
            "Does the lesson use any callout boxes, warning blocks, or highlighted key terms?",
            "Could any section benefit from a quick-reference summary box at the top?",
            "Is the reading flow clear — does the eye know where to go next after each section?",
            "Are there any walls of text (4+ dense paragraphs with no visual break)?",
            "Could any comparison ('REST vs GraphQL', 'public vs internal') be a side-by-side table?",
        ],
        "scoring_lens": (
            "Visual scannability and information hierarchy — "
            "can a reader find what they need in 30 seconds without reading every word?"
        ),
    },
]

# ── LESSON PARSER ─────────────────────────────────────────────────────────────

def parse_lesson(path: Path) -> dict:
    """Parse lesson file into frontmatter + three levels."""
    text = path.read_text(encoding="utf-8")

    # Strip frontmatter
    fm = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm_block = text[3:end]
            for line in fm_block.split("\n"):
                m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
                if m:
                    fm[m.group(1)] = m.group(2).strip()
            body = text[end + 4:]

    # Detect v1 vs v2
    levels = {}
    markers = {
        "foundation": r"#\s*FOUNDATION",
        "working": r"#\s*WORKING KNOWLEDGE",
        "strategic": r"#\s*STRATEGIC DEPTH",
    }

    for level, pattern in markers.items():
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            levels[level] = True

    is_v2 = len(levels) > 0

    if is_v2:
        # Split into level blocks
        chunks = re.split(r"\n#\s*═+\s*\n", body)
        level_content = {}
        current = None
        for chunk in chunks:
            if re.match(r"#\s*FOUNDATION", chunk.strip(), re.IGNORECASE):
                current = "foundation"
                level_content[current] = re.sub(
                    r"^#\s*(FOUNDATION|For:|Assumes:|Prereq:|This level|Skip).*$",
                    "", chunk, flags=re.MULTILINE | re.IGNORECASE
                ).strip()
            elif re.match(r"#\s*WORKING KNOWLEDGE", chunk.strip(), re.IGNORECASE):
                current = "working"
                level_content[current] = re.sub(
                    r"^#\s*(WORKING KNOWLEDGE|For:|Assumes:|Prereq:|This level|Skip).*$",
                    "", chunk, flags=re.MULTILINE | re.IGNORECASE
                ).strip()
            elif re.match(r"#\s*STRATEGIC DEPTH", chunk.strip(), re.IGNORECASE):
                current = "strategic"
                level_content[current] = re.sub(
                    r"^#\s*(STRATEGIC DEPTH|For:|Assumes:|Prereq:|This level|Skip).*$",
                    "", chunk, flags=re.MULTILINE | re.IGNORECASE
                ).strip()
            elif current:
                level_content[current] = level_content.get(current, "") + "\n" + chunk
    else:
        # v1: treat entire body as foundation
        level_content = {"foundation": body, "working": body, "strategic": body}

    word_counts = {
        lvl: len(content.split())
        for lvl, content in level_content.items()
    }

    return {
        "title": fm.get("lesson", path.stem),
        "module": fm.get("module", ""),
        "tags": fm.get("tags", ""),
        "status": fm.get("status", ""),
        "is_v2": is_v2,
        "level_content": level_content,
        "word_counts": word_counts,
        "full_text": text,
    }


# ── AGENT REVIEW ──────────────────────────────────────────────────────────────

def build_agent_prompt(agent: dict, lesson: dict) -> str:
    level = agent["level"]
    content = lesson["level_content"].get(level, lesson["full_text"])
    word_count = lesson["word_counts"].get(level, 0)
    checks = "\n".join(f"  - {c}" for c in agent["checks"])

    return f"""You are {agent['name']}, a {agent['role']}.

YOUR BACKGROUND:
{agent['background']}

YOUR SCORING LENS:
{agent['scoring_lens']}

You are reviewing the {level.upper()} level of a PM curriculum lesson titled:
"{lesson['title']}" (Module: {lesson['module']}, Tags: {lesson['tags']})

This level has {word_count} words.

LESSON CONTENT TO REVIEW:
---
{content[:CONTENT_LIMIT]}
---

YOUR SPECIFIC CHECKS FOR THIS LEVEL:
{checks}

Review the lesson from your persona's perspective. Be honest and specific.
Do not be generous — real learning gaps matter.

Respond in this EXACT JSON format:
{{
  "agent_id": "{agent['id']}",
  "agent_name": "{agent['name']}",
  "role": "{agent['role']}",
  "level_reviewed": "{level}",
  "overall_score": <integer 1-10>,
  "verdict": "<one of: EXCELLENT | GOOD | NEEDS_WORK | POOR>",
  "what_works": [
    "<specific thing that works well — quote the lesson if possible>",
    "<another thing>"
  ],
  "flags": [
    {{
      "severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
      "section": "<which section: F1/F2/F3/W1/W2/W3/W4/S1/S2/S3 or general>",
      "issue": "<specific problem — be precise, quote the lesson text where relevant>",
      "why_it_matters": "<why this is a problem for your persona specifically>",
      "suggested_fix": "<concrete suggestion — what should it say instead>"
    }}
  ],
  "missing_content": [
    "<something important that is completely absent — not just weak, but missing>"
  ],
  "one_line_summary": "<your honest overall take in one sentence, from your persona's voice>"
}}

Flags should be real issues. Do not fabricate problems. If the lesson is good, say so.
Return only valid JSON. No markdown, no preamble."""


def run_agent(client: anthropic.Anthropic, agent: dict, lesson: dict) -> dict:
    """Run a single agent review. Returns parsed JSON result."""
    prompt = build_agent_prompt(agent, lesson)
    last_err = None
    for attempt in range(3):
        try:
            if attempt > 0:
                import time; time.sleep(5 * attempt)  # 5s, 10s backoff
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)
        except json.JSONDecodeError as e:
            return {
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "role": agent["role"],
                "level_reviewed": agent["level"],
                "overall_score": 0,
                "verdict": "ERROR",
                "what_works": [],
                "flags": [],
                "missing_content": [],
                "one_line_summary": f"Parse error: {str(e)[:100]}",
                "_raw": raw[:500]
            }
        except Exception as e:
            last_err = e
            if "rate_limit" not in str(e).lower() and "529" not in str(e) and "overloaded" not in str(e).lower():
                break  # non-retryable error
    return {
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "role": agent["role"],
        "level_reviewed": agent["level"],
        "overall_score": 0,
        "verdict": "ERROR",
        "flags": [],
        "what_works": [],
        "missing_content": [],
        "one_line_summary": f"API error: {str(last_err)[:100]}",
    }


# ── SYNTHESIZER ───────────────────────────────────────────────────────────────

def synthesize(client: anthropic.Anthropic, reviews: list, lesson: dict) -> dict:
    """Synthesizer agent: reads all 10 reviews and produces ranked fix list."""
    # Build condensed view: drop what_works verbosity, keep all flags + summaries.
    # Full reviews_json is ~70k chars — this keeps it under 20k while preserving all signal.
    condensed = []
    for r in reviews:
        if r.get("verdict") == "ERROR":
            continue
        # Strip why_it_matters and suggested_fix from flags — synthesizer only needs
        # severity/section/issue to detect cross-agent patterns. Cuts input by ~60%.
        slim_flags = [
            {"severity": f.get("severity"), "section": f.get("section"), "issue": f.get("issue", "")[:200]}
            for f in r.get("flags", [])
        ]
        condensed.append({
            "agent_id": r.get("agent_id"),
            "role": r.get("role"),
            "level": r.get("level_reviewed"),
            "score": r.get("overall_score"),
            "verdict": r.get("verdict"),
            "flags": slim_flags,
            "missing_content": [m[:150] for m in r.get("missing_content", [])],
            "summary": r.get("one_line_summary", "")[:200],
        })
    reviews_json = json.dumps(condensed, indent=2, ensure_ascii=False)

    prompt = f"""You are the Synthesis Agent for a PM curriculum quality system.
You have just received {len(condensed)} independent reviews of the lesson "{lesson['title']}"
from PM reader agents with different backgrounds and assigned depth levels.

THE REVIEWS:
{reviews_json}

Your job:
1. Identify patterns across reviews — issues raised by multiple agents = more important
2. Distinguish real content gaps from persona-specific preferences
3. Produce a ranked fix list
4. Identify any new case studies or examples multiple agents wanted
5. Assess the overall curriculum health of this lesson

FORMATTING FLAGS (separate from content flags):
Check if D1 Nadia or any agent flagged scannability issues:
- wall of text or dense paragraphs or no visual breaks
- needs comparison table or should be a table
- buried or hidden in paragraph or lede buried
- no callout or missing highlight or no visual hierarchy
If 2+ formatting flags found across all agents (including D1): set run_formatter: true.

Rules for ranking:
- CRITICAL: Same issue flagged by 3+ agents, OR any single Critical flag from any agent
- HIGH: Same issue flagged by 2 agents in same level, OR single High flag touching core structure
- MEDIUM: Issue from 1 agent only, not touching core structure
- LOW: Stylistic preference from 1 agent

Respond in this EXACT JSON format:
{{
  "lesson_title": "{lesson['title']}",
  "review_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "overall_health": "<EXCELLENT|GOOD|NEEDS_WORK|POOR>",
  "average_score": <float 1-10, mean of all agent scores>,
  "scores_by_level": {{
    "foundation": <average of foundation-assigned agents>,
    "working": <average of working-assigned agents>,
    "strategic": <average of strategic-assigned agents>
  }},
  "ranked_fixes": [
    {{
      "rank": 1,
      "severity": "CRITICAL",
      "section": "<F1/F2/etc>",
      "issue": "<max 100 chars, no inner quotes, plain text only>",
      "raised_by": ["P1", "P3"],
      "suggested_fix": "<max 150 chars, no inner quotes, plain text only>",
      "apply_automatically": <true if safe to auto-apply, false if needs human judgment>
    }}
  ],
  "new_content_suggestions": [
    {{
      "type": "<case_study|example|section|debate>",
      "description": "<max 120 chars, no inner quotes>",
      "requested_by": ["P5", "P7"],
      "priority": "<HIGH|MEDIUM|LOW>"
    }}
  ],
  "what_is_working": [
    "<max 80 chars per item>"
  ],
  "summary_for_author": "<2-3 sentences max, no inner quotes>",
  "formatting_flags": [
    {{
      "section": "<which section>",
      "issue": "<max 80 chars, what the design agent flagged>",
      "transform": "<table|callout|card|list|warning|highlight|summary-box>"
    }}
  ],
  "run_formatter": <true|false>
}}

IMPORTANT: Keep all string values short (see char limits above). Do not use apostrophes or
quotes inside string values — rephrase instead. This ensures valid JSON output.
Return only valid JSON. No markdown fences."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=SYNTH_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e), "lesson_title": lesson["title"]}


# ── REPORT WRITER ─────────────────────────────────────────────────────────────

def write_report(lesson_path: Path, reviews: list, synthesis: dict) -> Path:
    """Write the FEEDBACK_REPORT.md to the same folder as the lesson."""
    lesson_dir = lesson_path.parent
    lesson_stem = lesson_path.stem
    report_path = lesson_dir / f"FEEDBACK_{lesson_stem}.md"

    lines = []
    lines.append(f"# Feedback Report — {synthesis.get('lesson_title', lesson_stem)}")
    lines.append(f"Generated: {synthesis.get('review_date', datetime.now().strftime('%Y-%m-%d'))}")
    lines.append(f"Agents: {len(AGENTS)} | Model: {MODEL}")
    lines.append("")

    # Summary box
    health = synthesis.get("overall_health", "—")
    avg = synthesis.get("average_score", 0)
    lines.append("## Executive summary")
    lines.append(f"**Overall health:** {health}  |  **Average score:** {avg:.1f}/10")
    lines.append("")
    scores = synthesis.get("scores_by_level", {})
    lines.append(f"| Level | Avg score |")
    lines.append(f"|---|---|")
    for lvl in ["foundation", "working", "strategic"]:
        s = scores.get(lvl, "—")
        lines.append(f"| {lvl.title()} | {s if s == '—' else f'{s:.1f}'} |")
    lines.append("")
    summary = synthesis.get("summary_for_author", "")
    if summary:
        lines.append(f"> {summary}")
        lines.append("")

    # Ranked fix list
    fixes = synthesis.get("ranked_fixes", [])
    if fixes:
        lines.append("## Ranked fix list")
        lines.append("")
        for fix in fixes:
            auto = "✓ auto-apply" if fix.get("apply_automatically") else "✎ human review"
            raised = ", ".join(fix.get("raised_by", []))
            lines.append(f"### [{fix.get('severity')}] #{fix.get('rank')} — {fix.get('section', '')}")
            lines.append(f"**Raised by:** {raised}  |  {auto}")
            lines.append(f"**Issue:** {fix.get('issue', '')}")
            lines.append(f"**Fix:** {fix.get('suggested_fix', '')}")
            lines.append("")

    # New content suggestions
    suggestions = synthesis.get("new_content_suggestions", [])
    if suggestions:
        lines.append("## New content suggestions")
        lines.append("")
        for s in suggestions:
            by = ", ".join(s.get("requested_by", []))
            lines.append(f"- **[{s.get('priority')}] {s.get('type', '').title()}** (requested by {by}): {s.get('description', '')}")
        lines.append("")

    # What's working
    working = synthesis.get("what_is_working", [])
    if working:
        lines.append("## What is working")
        lines.append("")
        for w in working:
            lines.append(f"- {w}")
        lines.append("")

    # Individual agent verdicts
    lines.append("## Individual agent verdicts")
    lines.append("")
    lines.append("| Agent | Role | Level | Score | Verdict |")
    lines.append("|---|---|---|---|---|")
    for r in reviews:
        if r.get("verdict") != "ERROR":
            lines.append(
                f"| {r.get('agent_id')} {r.get('agent_name')} "
                f"| {r.get('role')} "
                f"| {r.get('level_reviewed', '').title()} "
                f"| {r.get('overall_score', '—')}/10 "
                f"| {r.get('verdict', '—')} |"
            )
    lines.append("")

    # Full agent reports
    lines.append("## Full agent reports")
    lines.append("")
    for r in reviews:
        if r.get("verdict") == "ERROR":
            continue
        lines.append(f"### {r.get('agent_id')} — {r.get('agent_name')} ({r.get('role')})")
        lines.append(f"*Level: {r.get('level_reviewed', '').title()} | Score: {r.get('overall_score')}/10 | {r.get('verdict')}*")
        lines.append("")
        lines.append(f"**Summary:** {r.get('one_line_summary', '')}")
        lines.append("")

        what_works = r.get("what_works", [])
        if what_works:
            lines.append("**What works:**")
            for w in what_works:
                lines.append(f"- {w}")
            lines.append("")

        flags = r.get("flags", [])
        if flags:
            lines.append("**Flags:**")
            for f in flags:
                lines.append(f"- [{f.get('severity')}] **{f.get('section')}**: {f.get('issue')}")
                lines.append(f"  - *Why it matters:* {f.get('why_it_matters', '')}")
                lines.append(f"  - *Fix:* {f.get('suggested_fix', '')}")
            lines.append("")

        missing = r.get("missing_content", [])
        if missing:
            lines.append("**Missing content:**")
            for m in missing:
                lines.append(f"- {m}")
            lines.append("")

    # Formatting flags section (used by pm_format.py)
    fmt_flags = synthesis.get("formatting_flags", [])
    run_fmt = synthesis.get("run_formatter", False)
    lines.append("## Formatting flags")
    lines.append(f"run_formatter: {str(run_fmt).lower()}")
    lines.append("")
    if fmt_flags:
        for ff in fmt_flags:
            lines.append(f"- [{ff.get('transform', '')}] {ff.get('section', '')}: {ff.get('issue', '')}")
        lines.append("")
    else:
        lines.append("- No formatting flags raised.")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    # Auto-update mission control data after each swarm run
    _ctrl = Path(__file__).parent / 'control' / 'data.py'
    if _ctrl.exists():
        import subprocess
        result = subprocess.run(['python3', str(_ctrl)], capture_output=True)
        if result.returncode == 0:
            print("  ✓ Mission control data updated.")

    return report_path


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pm_swarm.py <path-to-lesson.md> [--mode fast|full]")
        print("  --mode fast  Use Haiku (~$0.04/run) — good for draft lessons (default)")
        print("  --mode full  Use Sonnet (~$0.32/run) — use before publishing")
        sys.exit(1)

    # Parse --mode flag
    global MODEL
    args = sys.argv[1:]
    mode = "fast"
    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 < len(args):
            mode = args[idx + 1].lower()
            args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]
    MODEL = MODEL_FULL if mode == "full" else MODEL_FAST

    lesson_path = Path(args[0])
    if not lesson_path.exists():
        print(f"Error: File not found: {lesson_path}")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Run: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    lesson = parse_lesson(lesson_path)

    print(f"\n{'='*60}")
    print(f"PM Feedback Swarm")
    print(f"Lesson: {lesson['title']}")
    print(f"Format: {'v2 (3 levels)' if lesson['is_v2'] else 'v1 (single level)'}")
    print(f"Word counts: {lesson['word_counts']}")
    print(f"Model: {MODEL} (--mode {mode})")
    print(f"Cost estimate: {'~$0.04' if mode == 'fast' else '~$0.32'}")
    print(f"Agents: {len(AGENTS)} | Parallel workers: {PARALLEL_WORKERS}")
    print(f"{'='*60}\n")

    # Write initial running status
    write_swarm_status(
        'running',
        lesson['title'],
        agents_queued=[a['id'] for a in AGENTS]
    )

    # Run agents in parallel batches
    reviews = []
    done_ids = []
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        futures = {
            executor.submit(run_agent, client, agent, lesson): agent
            for agent in AGENTS
        }
        for i, future in enumerate(as_completed(futures)):
            agent = futures[future]
            result = future.result()
            reviews.append(result)
            score = result.get("overall_score", "ERR")
            verdict = result.get("verdict", "ERROR")
            flags = len(result.get("flags", []))
            print(f"  [{i+1:2d}/{len(AGENTS)}] {agent['id']} {agent['name']:8s} ({agent['role'][:30]:30s}) → {score}/10 {verdict} | {flags} flags")
            done_ids.append(agent['id'])
            remaining_ids = [a['id'] for a in AGENTS if a['id'] not in done_ids]
            append_swarm_log(f"{agent['id']} {agent['name']} → {score}/10")
            write_swarm_status(
                'running',
                lesson['title'],
                agents_done=list(done_ids),
                agents_queued=remaining_ids
            )

    # Sort reviews by agent ID for consistent output
    reviews.sort(key=lambda r: r.get("agent_id", "P0"))

    # Synthesize
    print(f"\n  Synthesizing findings across all {len(AGENTS)} agents...")
    synthesis = synthesize(client, reviews, lesson)

    # Write report
    report_path = write_report(lesson_path, reviews, synthesis)

    print(f"\n{'='*60}")
    print(f"SWARM COMPLETE")
    print(f"{'='*60}")
    print(f"Overall health : {synthesis.get('overall_health', '—')}")
    print(f"Average score  : {synthesis.get('average_score', 0):.1f}/10")
    fixes = synthesis.get("ranked_fixes", [])
    criticals = [f for f in fixes if f.get("severity") == "CRITICAL"]
    highs = [f for f in fixes if f.get("severity") == "HIGH"]
    print(f"Critical fixes : {len(criticals)}")
    print(f"High fixes     : {len(highs)}")
    print(f"Total fixes    : {len(fixes)}")
    print(f"Report written : {report_path}")
    print(f"{'='*60}\n")

    if criticals:
        print("CRITICAL FIXES (apply first):")
        for fix in criticals:
            print(f"  → [{fix.get('section')}] {fix.get('issue', '')[:80]}")
        print()

    write_swarm_status('done', lesson['title'], agents_done=[a['id'] for a in AGENTS])
    write_swarm_status('idle')


if __name__ == "__main__":
    main()
