---
lesson: AI Evals & Quality Scoring
module: 04 — AI & ML Systems
tags: tech
difficulty: working
prereqs:
  - 04.01 — How LLMs Work: LLMs generate text by prediction — understanding this is necessary before you can evaluate whether predictions are good
  - 04.02 — Prompt Engineering Basics: Prompts define expected behavior — evals measure whether that behavior is actually happening
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/pqs-architecture-project-document.md
  - technical-architecture/student-lifecycle/first-connect-pqs-review.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The grader who never agreed

### The Problem: Broken Measurement

In 2022, a tutoring platform had a critical issue:

| Aspect | Situation |
|--------|-----------|
| **Scale** | 200 teachers across 12 countries |
| **Task** | Grading students on "lesson quality" |
| **Consistency** | None |
| **Example** | One teacher: 8/10 for a student's smile<br>Another teacher: 4/10 for same session (student didn't repeat vocabulary) |
| **Result** | Parent complaint; operations manager disagreed with both grades |

**Core issue:** No rulebook. No consistency. No way to measure if quality was actually improving or declining.

---

### The Same Problem Today

This pattern repeats at every company shipping AI-powered features:

**The Scenario:**
- A chatbot answers a customer question
- Team member A: "Good"
- Team member B: "It's hallucinating"
- Team member C: "Too robotic"

**What's happening:** Each person is measuring something different. None can prove whether the next model update made things better or worse.

---

### The Solution

> **AI Evaluations (evals):** Systematic methods to consistently measure AI output quality across multiple dimensions and stakeholders.

## F2. What it is — definition and analogy

> **AI evals:** A structured system for measuring whether an AI feature is doing what you want it to do. They replace "does it feel right?" with specific, repeatable tests that produce a number or a pass/fail result.

> **Key concept:** An eval answers one question — "Is the AI's output good enough, and is it getting better or worse over time?" Without evals, you can't safely make any changes to your AI system.

### The analogy: a school exam

Imagine a school deciding whether students understand fractions. They could ask teachers to "just feel it out" — but that's what the tutoring platform above was doing. Instead, they write a standardized test: 20 questions, each testing a specific skill, with a rubric defining what a correct answer looks like.

**Result:** They can measure every student consistently, compare classes, and tell if a new teaching method helped.

**AI evals work the same way.**

| Component | School Exam | AI Evals |
|-----------|------------|----------|
| **What questions to ask** | 20 standardized test questions | Specific test inputs for the AI |
| **What a good answer looks like** | Rubric defining correct answers | Rubric defining acceptable AI outputs |
| **How to measure the gap** | Scoring method (% correct) | Scoring method (pass/fail, numeric score) |

Once you have those three things, you can run the same test before and after every change to your AI system — and know with confidence whether things improved or broke.

## F3. When you'll encounter this as a PM

| Scenario | What Happens | Why It Matters |
|----------|--------------|----------------|
| **Shipping an AI feature** | Chatbots, summarization tools, recommendation engines, text generation, predictions go live | Without evals, you're flying blind on every model update, prompt change, or infrastructure swap |
| **Something breaks and you can't prove it** | Customer reports incorrect output → Support escalates → Engineering says "looks fine in testing" | No eval data means you can't distinguish one-off errors from widespread regressions. With evals, you pull score history and get answers in minutes |
| **Upgrading your model** | AI provider releases new version → Engineering wants to migrate | You need proof the new model is better *for your use case*, not just general benchmarks. Evals compare both models on your real user inputs |
| **Defining "done" for an AI sprint** | Team asks "how do we know this is ready to ship?" | Evals turn "vibes" into measurable acceptance criteria: ship when eval scores meet your quality threshold |

---

⚠️ **The Risk:** The PM who doesn't own evals is the PM whose AI features regress silently, ship broken, and never improve systematically.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation (or existing PM context)
# ═══════════════════════════════════

## W1. How evals actually work

There are three components to any eval system. You need all three.

---

### 1. The eval dataset (golden set)

> **Golden set:** A curated collection of inputs where you already know what a good output looks like. These are your test cases.

| Property | What it means |
|---|---|
| **Input** | The prompt or query the AI will receive |
| **Expected output** | The "right" answer — or the criteria a right answer must meet |
| **Label** | Pass/fail, a score, or a category (e.g., factual, hallucination, off-topic) |
| **Coverage** | Your golden set must cover edge cases, not just the happy path |

**What a good golden set includes:**
- Questions the AI answers well
- Questions it tends to get wrong
- Edge cases from real tickets
- Adversarial inputs users have tried

**Scale guidance:** Start with 20–50 examples → Ship with 100+ → Re-add any real user case that caused a bug.

---

### 2. The scoring method

How you decide whether an output is good. Three approaches — each with different tradeoffs:

| Method | How it works | Best for | Weakness |
|---|---|---|---|
| **Deterministic** | Exact string match, keyword check, regex | Structured outputs (JSON format, yes/no classification, specific phrases required) | Brittle — misses semantically correct answers that use different words |
| **LLM-as-judge** | A second LLM reads the output and scores it against a rubric | Open-ended text (chatbots, summaries, explanations) | Can be inconsistent; needs a good rubric; costs money to run |
| **Human eval** | A person scores the output | High-stakes decisions, rubric calibration, final QA sign-off | Slow, expensive — not scalable for regression testing |

**In practice:** You use all three. Deterministic checks for structure → LLM-as-judge for quality → Human eval for threshold calibration.

---

### 3. The rubric

> **Rubric:** The definition of *what good looks like* for your specific use case. This is the most important thing a PM owns in an eval system.

**Why generic rubrics fail:**
- "Is the answer helpful?" is not a rubric — it's a feeling.
- A real rubric is specific, measurable, grounded, and versioned.

**Example: PQS Pedagogical Rubric (BrightChamps)**
- **10 dimensions**, each scored 0–2
- Includes: Concept Clarity, Worked Examples, Guided Practice, Homework Check (+ 6 others)
- **Pass threshold:** ≥ 1 on at least 8 dimensions
- **Evidence requirement:** Each score backed by a timestamped quote from transcript — no score without a quote

**What makes this rubric strong:**
- ✓ Specific (named dimensions)
- ✓ Measurable (0–2 scale, not "good/bad")
- ✓ Grounded (evidence quotes, not impressions)
- ✓ Versioned (rubric changes don't silently invalidate past scores)

---

### Concrete eval row — end to end

**Good output:**

| Field | Example value |
|---|---|
| **Input** | "Why does my API keep returning 429 errors?" |
| **AI output** | "A 429 means you're hitting a rate limit. Try adding exponential backoff in your retry logic." |
| **Rubric dimension** | Factual accuracy |
| **Score** | 2/2 — factually correct, specific fix given |
| **Rubric dimension** | Tone (customer support) |
| **Score** | 2/2 — direct, not condescending, actionable |
| **Rubric dimension** | Hallucination check |
| **Score** | 2/2 — no invented claims, no made-up library names |
| **Overall pass/fail** | **PASS** (6/6) |

**Bad output (same input):**

| Field | Example value |
|---|---|
| **Input** | "Why does my API keep returning 429 errors?" |
| **AI output** | "429 is a server error. Contact our enterprise support team for a resolution." |
| **Rubric dimension** | Factual accuracy |
| **Score** | 0/2 — 429 is a *client* error, not server error. Wrong. |
| **Rubric dimension** | Resolution provided |
| **Score** | 0/2 — deflects to support, gives no fix |
| **Overall pass/fail** | **FAIL** (2/6) |

*What this reveals:* An eval system produces per-dimension breakdowns for every output, with specific failure modes identified — not a vague "quality score."

---

### The eval pipeline

Once you have dataset + scoring method + rubric, the pipeline runs automatically:

```
Input from golden set
    → AI generates output
        → Scoring method evaluates output against rubric
            → Score written to eval log
                → Dashboard shows pass rate, trend, regressions
```

**Deployment gate:** A healthy team runs this pipeline on every pull request. A score drop below threshold blocks the deploy.

## W2. The decisions this forces

### Decision 1: What type of eval do you need?

Not all AI features need the same eval approach.

| Feature type | Right eval type | Example |
|---|---|---|
| Classification | Deterministic (accuracy, F1) | Spam detection, intent routing |
| Structured generation | Deterministic (schema validation + field checks) | Extracting data into JSON, filling forms |
| Open-ended generation | LLM-as-judge + human calibration | Chatbot responses, summaries, explanations |
| Ranking/recommendation | Offline: precision@k, NDCG. Online: CTR, conversion | Search results, feed ranking |

**PM recommendation:** Start with the simplest eval type that covers your failure modes. A classification system scored with F1 is far more trustworthy than a chatbot scored with a vague "helpfulness" rubric.

### Decision 2: What's your quality threshold?

Your eval system needs a number that means "good enough to ship." This is a PM decision, not an engineering decision — because it's a product quality bar.

**Consider:**
- **Safety cost of being wrong** — A medical chatbot that hallucinates 5% of the time is categorically different from a recipe suggester that does the same
- **Current baseline** — If your system is at 72% today, shipping at 73% is progress; shipping at 68% is regression
- **Comparative baseline** — Does your AI need to beat human performance, match it, or just be "good enough"?

> **PQS threshold example:** BrightChamps requires 91% accuracy on completed paid classes. Below that, the parent report isn't surfaced — it's held pending manual review. The 91% target was set by product based on the parent trust threshold (what percent accuracy would parents stop trusting the score?), not by what the model could achieve.

**Set your threshold before you see the score.** If you wait until after, you'll rationalize whatever number comes out as "good enough."

### Decision 3: Offline vs. online evals

These are not the same thing — you need both.

> **Offline evals:** Run against your golden set before shipping. Catch regressions before users see them.

> **Online evals:** Monitor real production outputs after shipping. Catch distribution shifts, novel failure modes, and cases your golden set didn't cover.

**The failure mode:** Teams that only do offline evals ship something that passes their test set perfectly — because the test set doesn't represent what users actually ask.

Online monitoring is your early warning system. When the real-world pass rate drifts below offline pass rate by more than a few percentage points, your golden set is stale and your model is encountering inputs it wasn't tested on.

### Decision 4: Who owns the rubric?

The rubric definition is a product decision. Engineering owns the pipeline that runs it. **PM owns what "good" means.**

This is the most commonly dropped ball in AI product work. Engineers set up an eval pipeline with a generic rubric pulled from a paper or a framework. It runs. It produces numbers. Nobody on the product side understands what the numbers mean or trusts them. The eval system becomes theater.

> **How to avoid it:** PM writes the rubric in plain language first. Engineering translates it into a scoring prompt. A sample of outputs is scored by both the rubric and by humans — and the two are compared. If they diverge by more than 15%, the rubric is wrong and needs rework before you trust the numbers.

### Decision 5: How often do you run evals?

| Cadence | When to use |
|---|---|
| On every PR/deploy | Regression testing — catches breaks before they ship |
| Nightly batch | Track trends without blocking dev velocity |
| On model/prompt changes | Before/after comparison for any change to the AI layer |
| On rubric changes | Full re-score of historical data to maintain score continuity |
| On data drift alerts | When production inputs start diverging from your golden set |

**PM recommendation:** Block deploys on critical regressions. Alert (don't block) on medium drops. Weekly review of trend charts is a PM responsibility — not just an engineering metric.

### Decision 6: Who owns what — and what does it cost?

Ownership confusion is why eval systems fail.

**Clean ownership split:**

| Component | PM owns | Engineering owns |
|---|---|---|
| **Rubric** | Writes it in plain language. Approves final scoring criteria. | Translates into a scoring prompt or rule. Maintains the pipeline. |
| **Golden set** | Defines what cases must be covered. Reviews new cases from production failures. | Builds the tooling to add cases. Runs the set automatically. |
| **Threshold** | Sets the pass/fail bar. Decides when a score drop blocks a deploy. | Implements the gate. Alerts PM when threshold is crossed. |
| **Human eval** | Sponsors the effort. Allocates time for calibration. | Coordinates annotation tooling and inter-rater scoring. |
| **Trend review** | Reviews quality charts weekly. Flags divergences for investigation. | Builds the dashboard. Runs the nightly batch. |

**Honest cost breakdown:**

| Resource | What you're spending |
|---|---|
| **PM time** | 2–4 hours to write an initial rubric. 30 min/week reviewing trends. 1 hour/sprint reviewing golden set additions. |
| **Human annotation** | $0.05–$2.00 per scored output depending on complexity and annotator source (internal vs. vendor). A 200-case golden set costs $20–$400 to label once. |
| **LLM-as-judge API cost** | $0.002–$0.02 per output eval at current model pricing. A 100-case eval suite costs $0.20–$2.00 per run. Daily regression testing costs $5–$50/month. |
| **Engineering setup** | 2–5 days to build the eval pipeline from scratch. 1 day to add a new eval dimension. Ongoing: low if automated, high if manual. |

⚠️ **The common trap:** Teams skip evals because they "don't have bandwidth." The actual cost of skipping: one silent regression that ships to users, causes support tickets, and requires a hotfix. That incident costs more than a month of eval infrastructure. Build it before you need it.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **"What's our current eval pass rate, and what was it three months ago?"** | Whether the team is tracking quality over time at all. No answer = no eval system. A number without a trend = vanity metric. |
| **"What's in our golden set, and when was it last updated?"** | Whether your test cases reflect real user inputs. A golden set that hasn't been updated since launch is likely missing the failure modes users have actually encountered. |
| **"How do we score open-ended outputs — LLM-as-judge, human, or something else?"** | Whether the team has thought through the quality measurement method, or just wired up the first thing that worked. LLM-as-judge with no rubric calibration produces noisy scores. |
| **"What's our threshold for blocking a deploy?"** | Whether quality has teeth. If there's no threshold, evals are observational, not protective. |
| **"Do we have online monitoring, or only offline evals?"** | Whether the team knows the difference. Offline-only means production failures are invisible until a user reports them. |
| **"What does a regression look like in our system — how would we know if the AI got worse this week?"** | Whether the alerting loop is closed. Many teams can produce a score but have no process for what happens when it drops. |
| **"How does our rubric handle edge cases — ambiguous inputs, adversarial queries, refusals?"** | Whether the rubric has been stress-tested. A rubric written for the happy path will score adversarial outputs incorrectly. |
| **"If we switch to a new model version, what's our migration eval process?"** | Whether model upgrades are treated as engineering events or product quality events. The answer should be: run the full eval suite against both versions, compare scores, make a decision. |

## W4. Real product examples

### BrightChamps — PQS Forensic Ledger

**What:** A 10-dimensional pedagogical rubric (0–2 per dimension) that evaluates every class transcript with timestamped evidence quotes from the transcript for each score.

**Why:** No score without a quote. Parents and QA teams can challenge scores by pointing to exact evidence. Creates a disputable, auditable evaluation artifact.

**Key implementation details:**

| Aspect | Decision |
|--------|----------|
| Rubric authorship | Curriculum + Product (not engineering) |
| Accuracy target | 91% (set against parent trust requirements) |
| Rubric changes | Full re-score of historical data (no silent resets) |
| Product output | Drives three parent-facing surfaces: Class Energy, Learning Journey, Actionable Next Steps |

**Scale:** 91% accuracy on completed paid classes | ~500 sessions/day | 17 distinct event types in scoring engine

**Takeaway:** The evaluation artifact *is* the product output—not a backend signal.

---

### BrightChamps — Sales Pitch Quality Score

**What:** AI pipeline scores sales agent calls (10-dimensional rubric) against a `Sales_Pitch_Audit_Score`. Scores ≤ 6/10 trigger automated task assignment to the agent's team lead for human review within the agent's working shift.

**Why:** Eval-to-action workflow. AI scores continuously; human review only triggers below threshold. Result: ~91% of scores accepted without dispute. TLs only involved in bottom 9%.

**Takeaway:** The threshold (≤ 6) is a **product decision**, not a technical parameter. It determines TL time allocation between review and coaching. Set too low = review everything. Set too high = bad pitches ship. Threshold was calibrated against trial conversion rates.

---

### Notion — AI output quality gates

**What:** Automated evals on every change to Notion AI's prompting layer test against golden set of real user documents: summary quality, answer faithfulness, hallucination rate. Regressions block production deployment.

**Why:** Consistency compounds. Catching regressions over six months produced 40% hallucination rate drop—not from model improvement, but from the eval gate itself.

**Takeaway:** Evals work through iteration, not breakthroughs. One regression caught today prevents it from becoming six months of drift.

---

### Stripe — Structured output validation

**What:** Deterministic evals (not LLM-as-judge) on AI data extraction from documents. Rule engine validates schema: required fields present, data types match, values in expected ranges. Runs in milliseconds. 0% false-negative rate for schema violations.

**Why:** Structured outputs don't need LLM judgment. A regex is faster, cheaper, and more reliable than a language model.

**Takeaway:** Match eval type to output type. Deterministic evals beat LLM-as-judge on speed, cost, and reliability for structured data.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. What breaks and why

### The Goodhart problem in rubric design

> **Goodhart's Law:** When a measure becomes a target, it ceases to be a good measure.

AI systems optimized on a rubric will find ways to score well on the rubric without achieving the underlying goal.

| Problem | Example | Signal |
|---------|---------|--------|
| Metric gaming | Chatbot rubric rewards "uses the user's name" | Output uses names excessively |
| False optimization | Pedagogical rubric rewards "uses examples" | Output stuffed with irrelevant examples |

**PM prevention role:** 
- Audit your rubric quarterly against a sample of real outputs
- Look for the gap between "scores well" and "is actually good"
- Treat the rubric as a living document requiring adversarial review
- Note: The gap widens over time as prompts and models are tuned to the eval

---

### Eval set staleness

A golden set built in Q1 represents Q1 user behavior. By Q4, your users, their vocabulary, and their failure modes have all shifted. An eval that passes at 94% on a stale golden set may be passing 94% of easy cases while failing on new hard cases that didn't exist when the golden set was built.

**PM prevention role:**
- Add a minimum of 5 new cases from real production failures to the golden set every sprint
- Gate any prompt or model change on *both* the existing golden set *and* the new cases from that sprint

---

### LLM-as-judge bias

When you use an LLM to score another LLM, you're measuring alignment between two models, not alignment with human intent.

| Scenario | Result | Why |
|----------|--------|-----|
| Using GPT-4 to judge GPT-4 outputs | Artificially high scores | Models share failure modes |
| Using verbose-biased model as judge | Verbose outputs score higher | Judge preference, not accuracy |

**PM prevention role:**
- Calibrate your LLM judge against human scores *before* trusting it
- Run 50–100 outputs through both judge and human evaluators
- ⚠️ **If inter-rater agreement (judge vs. human) is below 80%, your judge is not measuring what you think it's measuring**

---

### The "passing evals but failing users" failure

Your eval suite passes at 89%. Users report the AI "sounds wrong." Both are true. The gap exists because your golden set tests what users ask, but not how they interpret what they get back.

| What Happened | Eval Score | User Experience | Root Cause |
|---------------|-----------|-----------------|-----------|
| Factually accurate answer | 100% accuracy | 0% trust | Condescending tone |

**PM prevention role:**
- Track qualitative signals alongside quantitative eval scores:
  - Support tickets
  - User feedback tags
  - NPS for AI features
- ⚠️ **Treat a divergence between qualitative and quantitative signals as an urgent indicator that your rubric is measuring the wrong thing**

## S2. How this connects to the bigger system

> **Evals:** The feedback loop for the entire AI stack. Every artifact produced by other Module 04 decisions is measured through evals.

### Evals measure every other decision in the AI stack

| Decision | What evals measure | Risk without evals |
|----------|-------------------|-------------------|
| **Fine-tuning vs prompting (04.05)** | Whether fine-tuning improved quality; whether prompt changes regressed behavior | Decisions based on intuition rather than data |
| **RAG (04.03)** | Whether better retrieval produces better outputs; whether retrieval failures degrade quality | Unable to distinguish retrieval failures from generation failures |
| **Embeddings (04.04)** | Whether embedding model changes broke retrieval quality downstream | Silent quality regressions that cascade through the system |

### Evals as competitive advantage

**Evals become a product moat.** A proprietary golden set of real user inputs—annotated with product-specific rubric criteria—cannot be replicated by competitors. This is institutional knowledge:
- What your users actually ask
- What your domain actually requires  
- What your quality bar actually is

**Compounding advantage:** Companies investing in evals early move faster on model changes because they have the safety net.

### Evals require data infrastructure

⚠️ **Evals are not a standalone feature.** They depend on:
- **Logging:** Every production output must be capturable
- **Storage:** The eval log is a time series of quality scores
- **Dashboard:** Trends, regressions, per-category breakdowns

Treat evals as infrastructure, not a sprint task.

## S3. What senior PMs debate

### Debate 1: Does LLM-as-judge actually work — or are we all just telling ourselves it does?

| Position | Stance | Typical Context |
|----------|--------|-----------------|
| **Mainstream** | LLM-as-judge is good enough for most regression detection, calibrated against human eval initially, re-calibrated when rubric changes | Anthropic, OpenAI, AI-native startups |
| **Counter** | LLM-as-judge has unknown failure modes that correlate with the exact failure modes you're trying to catch | Regulated industries, high-stakes domains (medical, legal) |

**The core friction point:**

What inter-rater agreement between LLM judge and human rater is "good enough" to trust?

- **Industry baseline:** 80% is commonly cited
- **High-stakes threshold:** Medical/legal AI typically requires 90%+
- **The real disagreement:** Not about the number itself, but whether you can ever fully trust a judge you can't fully inspect

**Where senior PMs split:**

- Some have stopped trusting LLM-as-judge for rubric dimensions where the judge model has no domain expertise (clinical accuracy, legal precision, financial instrument definitions) — *regardless of calibration scores*
- Others argue that imperfect automated evals are better than no evals
- Both positions are defensible

⚠️ **Critical assumption to reject:** LLM-as-judge calibration scores transfer across domains. They don't.

---

### Debate 2: Eval-driven development vs. ship-and-observe — and who's actually willing to block a deploy?

**Theory vs. Practice:**

| What's Clean | What's Messy |
|--------------|--------------|
| Set a threshold, block if score drops | Product team with weekly deploys and VP pressure won't block for 82% → 79% drop |

**The validation prerequisite that makes eval gates credible:**

Senior PM teams that successfully implemented eval gates share one common element: **the rubric was validated against real business outcomes before being used as a gate.**

> **Example evidence statement:** "We correlated eval score with CSAT/support rate/retention and showed that a 5% drop in eval score predicts a 12% increase in support tickets"

**What happens without this validation:**

Teams that skip correlation analysis build eval gates that get ignored or bypassed under pressure.

**The timing question:**

- **Early stage consensus:** Most senior PMs say skip the validation overhead — ship and observe until you have enough data to correlate
- **Risk of skipping:** Defers the problem to a production incident

---

### Debate 3: Does eval ownership belong to PM, ML engineering, or does it need to be its own role?

**The PM-ownership model breaks when:**

PM lacks sufficient context to write a rubric capturing real failure modes in a technical domain.

**The problem in regulated/expert domains:**

A PM writing a rubric for legal contract analysis, medical diagnostics, or code generation can describe *symptoms* but not *mechanisms*. The rubric ends up measuring surface features (tone, length, format) rather than domain correctness.

**Current solutions by company size:**

| Company Stage | Solution | Trade-offs |
|---------------|----------|-----------|
| **Larger (2024–2025 trend)** | Create "eval engineer" or "AI QA" hybrid role — domain expertise + evaluation methodology | Requires new headcount |
| **Smaller** | Require PM to shadow users intensively before writing rubric | High time investment from PM |

**The unresolved tension:**

If PM doesn't own the rubric deeply, the eval system reflects engineering's definition of quality — which may or may not align with what users experience.

> **Historical pattern:** Several high-profile AI product failures in 2024 were attributed post-mortem to eval systems that scored high on dimensions engineers understood and *missed the dimensions users cared about*.

---

### What AI is doing to all three debates

**The new capability:** Synthetic eval generation now lets LLMs generate hundreds of golden set examples from a rubric description in minutes.

**What this solves:**
- Reduces the cost barrier to building evals

**What this inverts:**
- The bottleneck shifts from golden set volume → rubric quality
- A high-volume eval suite built from a bad rubric produces confident, wrong signal

⚠️ **The meta-eval frontier:** How do you know your eval is measuring what matters? No one has a clean answer yet.