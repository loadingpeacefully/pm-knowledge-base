---
lesson: AI Cost & Latency Tradeoffs
module: 04 — AI & ML Systems
tags: tech
difficulty: working
prereqs:
  - 04.01 — How LLMs Work: Cost is driven by token count and model size — understanding how LLMs generate tokens is required before understanding why bigger models cost more
  - 04.02 — Prompt Engineering Basics: Prompt length directly impacts token spend — poorly structured prompts are a hidden cost driver
  - 04.03 — RAG (Retrieval-Augmented Generation): Retrieval adds latency to the AI pipeline — understanding RAG is prerequisite to understanding full-stack AI latency
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/pqs-architecture-project-document.md
  - technical-architecture/student-lifecycle/trialbuddy-ai-powered-chatbot.md
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

## F1 — The world before this existed

When software ran on servers, cost was mostly fixed: you paid for machines that ran 24 hours a day whether anyone used the product or not. A thousand users hitting your app in a minute cost almost nothing extra — the server was already on.

AI changed this completely. Every time a user sends a message to an AI feature, the model does real computational work. That work costs money. Specifically: it costs money proportional to how many words it reads and how many words it writes back. Ship a bad AI feature — one that writes rambling five-paragraph responses when one sentence would do — and you've built a machine that charges you more the worse it performs.

Before product managers understood this, AI features were spec'd the same way as database queries: describe the behavior you want, hand it to engineering, and let infrastructure worry about cost. That worked until the bills arrived. Teams that shipped AI features in 2023 and 2024 frequently discovered their per-user AI cost was five to twenty times higher than projected because nobody had done the math at the feature level.

The second problem is latency. Traditional software can respond in milliseconds because it's mostly lookup — find a record, return it. AI models generate responses token by token, one word at a time. A 300-word response from a large model might take 8–12 seconds to complete. That's not a bug. It's physics. Users who waited 3 seconds for a web page to load in 2010 will not wait 10 seconds for an AI chatbot response in 2025 — unless the product makes that wait feel worth it.

Cost and latency are now first-class product problems, not infrastructure afterthoughts. The PM who can't reason about them will ship features that either don't get funded or don't get used.

---

## F2 — What it is — definition + analogy

> **AI cost and latency tradeoffs:** The set of decisions about how much to spend on AI inference and how fast that response needs to arrive — and the relationship between those two variables.

### The Kitchen Analogy

| Aspect | Fast-Food Kitchen | Michelin-Star Kitchen |
|--------|-------------------|----------------------|
| **Model Type** | Small, cheap | Large, expensive |
| **Speed** | Hundreds per hour | 30 minutes per dish |
| **Cost** | Low per unit | 20× higher per plate |
| **Quality** | Consistent, predictable | Bespoke, adaptive |
| **Capability** | Cannot improvise | Handles any request |
| **Best For** | School cafeteria | One-off special orders |

**What this reveals:** Most AI products need *both* approaches—not everything routes through the expensive option just because output quality is higher.

---

### Key Terms

> **Token:** The unit AI models use to measure text. Roughly 1 token ≈ 0.75 words in English. "Hello, how can I help you?" is about 8 tokens. AI models charge per token, separately for tokens they read (input) and tokens they write (output).

> **Inference:** The act of running a model to produce a response. Every AI feature call = one inference. Cost and latency are properties of inference.

> **Model size:** Measured in parameters (billions of numbers the model learned during training). More parameters = better reasoning ability, higher cost per token, slower response.

---

### The PM's Core Responsibility

Assign each task to the right kitchen — not to route everything through the expensive one because it produces better output.

**Example tasks:**
- **Simple, repetitive** → Fast kitchen: "What's my class schedule?"
- **Complex, high-value** → Fine dining: Personalized post-class analysis for parents

## F3 — When you'll encounter this as a PM

| Scenario | What You'll Need |
|----------|-----------------|
| **Writing the spec for a new AI feature** | Cost estimate: tokens per prompt × response length × daily active users = monthly projection. Engineers will ask. You need the answer ready. |
| **Engineering says "the model is too slow"** | A choice between three paths: faster/cheaper model (tradeoff in quality), streaming UI (same time, better perception), or background processing (unblocks user). |
| **Budget conversations with leadership** | Cost translated to business metrics: cost per user, cost per feature interaction, scaling dynamics—not "we spend $X on OpenAI" but "$0.04 per report, 10,000/month = $400/month." |
| **After a cost spike** | Root cause identification (usage growth? longer prompts? new feature rollout?) and immediate fix proposal. Understanding drivers beats waiting a week for engineering. |
| **When a cheaper model launches** | Decision framework: Can we switch? Model pricing drops 40–60% every 12–18 months; smaller models regularly match larger ones from 12 months prior. |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level, or equivalent PM experience
# ═══════════════════════════════════

## W1 — How it actually works

### The token pricing model

> **Token:** A unit of text that the model processes. Input tokens are what you send; output tokens are what the model generates back.

AI APIs charge per token, with separate rates for input and output. Output tokens typically cost **3–5× more** than input tokens because generating each output token requires a full model forward pass, while input tokens are processed in parallel.

**Typical pricing structure** (Anthropic, early 2025 — check your provider's current rates):

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Use case |
|---|---|---|---|
| claude-haiku-4-5 | $0.25 | $1.25 | Classification, retrieval |
| claude-sonnet-4-6 | $3.00 | $15.00 | Balanced tasks |
| claude-opus-4-6 | $15.00 | $75.00 | Complex reasoning |

**Key insight:** The 60× ratio between small and large models is the most important number in AI product economics.

**What drives token count:**

| Component | Impact | Example |
|---|---|---|
| System prompt | Static cost per call | 500-token system × 100k daily calls = 50M tokens/day |
| User input | Variable by interaction | Varies by user message length |
| Conversation history | Multiplies with depth | 10-turn chat resends all 10 turns each time |
| Retrieved content (RAG) | Per document chunk | Each vector store result adds tokens |
| Output length | Scales response cost | 100-word response ≈ 3× cost of 30-word response |

---

### The two latency numbers that matter

> **Time to First Token (TTFT):** How long before the user sees the first word. This determines perceived responsiveness.

> **Time to Complete (TTC):** Full response time = TTFT + (output tokens ÷ generation rate).

**Which metric matters depends on context:**

| Context | Critical metric | Why |
|---|---|---|
| Chat, inline suggestions | TTFT | Users judge responsiveness by initial response |
| Background reports, summaries | TTC | Response arrives after event; latency is invisible |

**Streaming** is a perception hack: instead of waiting for the full response, tokens arrive as they're generated. A 6-second response feels instant (like fast typing) rather than a 6-second blank screen.

**Example:** TrialBuddy's <2 second response target was achieved through streaming + small model selection, not raw speed.

---

### Three cost levers PMs control

#### 1. Model selection per task

Not every task needs maximum capability. Use a **model cascade**: route simple tasks to small models, complex tasks to large models.

| Task | Model size | Reasoning |
|---|---|---|
| Intent classification ("reschedule vs. complaint?") | Small | Binary output, pattern matching |
| FAQ answer retrieval | Small | Templated responses, low reasoning |
| Personalized narrative (post-class report) | Large | Synthesis, nuance, personalization required |
| Debugging edge cases | Large | Multi-step reasoning needed |

**Example:** PQS routes non-English sessions out via deterministic language detection (cheap) before expensive LLM evaluation, avoiding full model cost upfront.

#### 2. Prompt caching

> **Prompt caching:** When the same prefix (system prompt, knowledge base, instructions) is sent repeatedly, the provider caches it at ~10% of normal input token cost after the first call.

**Cost comparison** (2,000-token system prompt, 1M calls/month):

| Approach | Cost | Savings |
|---|---|---|
| Without caching | $30,000/month | — |
| With caching | $3,000/month | 90% reduction |

⚠️ **Note:** This requires zero product changes—only engineering configuration.

#### 3. Batch vs. real-time processing

> **Batch processing:** AI calls processed asynchronously (within minutes/hours) instead of in real time. Batch API pricing is **50% of normal** with up to 24-hour turnaround.

**When to batch:**
- User triggers event (class ends, form submitted, report requested)
- Response delivered asynchronously
- No real-time latency pressure

**Example:** PQS evaluates transcripts after class ends (not during), delivers reports 30–60 minutes later, qualifies for full batch discount.

## W2 — The decisions this forces

### Quick Reference
| Decision | Question | Default Recommendation |
|---|---|---|
| Real-time vs. async | Does user wait for response? | Default async; real-time only for conversation |
| Model selection | Same model for all tasks? | Cascade if 70%+ of queries route to cheaper model |
| Token budgets | Enforce length limits? | Yes—set max_tokens on every call |
| Prompt caching | Static vs. dynamic content? | Implement if static prefix > 1,000 tokens |
| Streaming | Show response arriving live? | Yes for conversation; no for structured decisions |

---

### Decision 1: Real-time vs. asynchronous processing

> Do users need the AI response immediately, or can it be delivered after a delay?

| Real-time | Asynchronous |
|---|---|
| User is waiting, watching, cannot proceed | AI runs in background after trigger event |
| Examples: chat interface, inline autocomplete, code suggestion in IDE | Examples: post-class report, email digest, bulk document analysis |
| Must optimize for TTFT | Can batch at 50% cost with no UX penalty |

> **Recommendation:** Default to async for any AI feature that produces a deliverable (report, summary, analysis). Reserve real-time for conversational interfaces and features where the user is actively waiting. Async cuts cost in half and removes latency pressure from the critical path.

---

### Decision 2: Which model for which task

> Should every AI call in the product use the same model?

**Single model approach:**
- Simple to build and maintain
- Expensive and often overkill (routing "what's my class link?" through a frontier model)

**Model cascade approach:**
- Requires engineering effort (prompt compatibility, output format consistency, routing logic)
- Math: if 70% of queries route to small model at 60× price ratio
  - Average cost = (0.7 × 1 + 0.3 × 60) ÷ 60 ≈ **31% of pure large-model cost**
  - **~80% reduction** (matches teams building cascades consistently)

> **Recommendation:** Run a sample of production queries through a cheaper model and measure quality degradation. If the cheaper model handles 70%+ of queries acceptably, implement the cascade. Defer the cascade for v1 if engineering bandwidth is the constraint — launch on one model, then optimize.

---

### Decision 3: Token budget guardrails

> Should prompts and responses have enforced length limits?

**Without guardrails:**
- Prompts grow over time (more context, edge case handling, conversation history)
- Each addition feels small but compounds into significantly higher costs
- Response length drifts upward when models lack explicit constraints
- "Be helpful and thorough" → longer outputs than "respond in 2-3 sentences unless asked"

**Cost impact example:**
- 1,000 tokens added to system prompt
- 100K daily calls
- **+$45/day in input cost** at frontier model prices

> **Recommendation:** Set explicit max_tokens limits on every API call. Define a target response length in the system prompt. Audit system prompt length quarterly — it will drift upward without active management.

---

### Decision 4: Prompt caching eligibility

> Which parts of the prompt are static vs. dynamic?

> **Prompt caching:** Only applies to the static prefix — the portion that doesn't change between calls.

**Static examples:** system prompt, knowledge base injection
**Dynamic examples:** user's name, current time, real-time data, user message, conversation history

**Best practice:**
- Keep static portion at the top
- Keep dynamic portion at the bottom
- Maximizes cacheable prefix length

> **Recommendation:** Audit prompt structure before shipping any high-volume AI feature. Identify the boundary between static and dynamic content. If the static prefix is longer than 1,000 tokens, implement prompt caching before launch — it pays for the engineering time in the first week of production traffic.

---

### Decision 5: Streaming vs. synchronous delivery

> Should the UI show the response arriving in real time, or wait for the full response?

| Streaming | Synchronous |
|---|---|
| Total compute cost: identical to synchronous | Total compute cost: identical to streaming |
| Perceived latency drops 60–80% | Preferred for structured outputs |
| Engineering complexity: moderate, well-supported by all APIs | Prevents confusing partial states |
| Best for: conversational features | Best for: yes/no decisions, classifications, data outputs |

**Example of synchronous win:** A yes/no decision that streams live as "Yes... actually, wait, I need to reconsider... No" is worse than showing final "No" after 3-second wait.

> **Recommendation:** Use streaming by default for all conversational features. Use synchronous delivery for features where the response is a structured decision, a classification, or a data output that users will act on.

---

## Worked example: estimating AI cost from a feature spec

> **Feature:** Post-class summary report — auto-generated narrative summarizing what the student learned, sent to the parent 20 minutes after class ends.

### Step 1 — Estimate token counts per call

| Component | Tokens | Notes |
|---|---|---|
| System prompt (rubric instructions, persona) | 1,500 | Static — cacheable |
| Class transcript (30-min class) | 3,000 | Dynamic per call |
| Output (structured report narrative) | 800 | PM-controlled via max_tokens |
| **Total input + output** | **5,300 + 800** | |

### Step 2 — Calculate cost per call at two model tiers

| Model | Input cost | Output cost | **Total per call** |
|---|---|---|---|
| claude-opus (large): `(5,300 × $15/1M) + (800 × $75/1M)` | $0.0795 | $0.060 | **$0.14** |
| claude-haiku (small): `(5,300 × $0.25/1M) + (800 × $1.25/1M)` | $0.0013 | $0.001 | **$0.0023** |
| **Price ratio on this call** | | | **~60×** |

### Step 3 — Project monthly cost at scale

| Monthly volume | Opus (large) | Haiku (small) | Savings |
|---|---|---|---|
| 10,000 reports | $1,400 | $23 | $1,377 |
| 100,000 reports | $14,000 | $230 | $13,770 |
| 1,000,000 reports | $140,000 | $2,300 | $137,700 |

### Step 4 — Apply prompt caching to the large model

The 1,500-token system prompt is static — enable caching (cost drops to 10% on that prefix):
- System prompt uncached: $0.0225/call
- System prompt cached: $0.00225/call
- **Total cost with caching: $0.12 per report** (~15% savings vs. uncached opus)

### Step 5 — Decision framework

**Run 200 transcript evals** comparing haiku vs. opus output quality on rubric scoring:

- **If correlation ≥ 0.90:** Switch to haiku — the $137K/month savings at scale justifies full regression
- **If correlation < 0.85:** Use mid-tier sonnet ($3/M input) and recalculate:
  - ~$21 per 1,000 calls vs. $140 (large) or $2.30 (small)

**PM takeaway:** The cost decision is not "expensive vs. cheap." It's "what quality threshold is required at what volume?" Run the numbers from the spec before your first engineering sprint, not after your first invoice.

## W3 — Questions to ask your engineer

### Quick Reference
| Question Focus | Cost Signal | Latency Signal | Scale Signal |
|---|---|---|---|
| Unit economics & caching | ✓ | | |
| API performance | | ✓ | |
| Async opportunities | ✓ | | |
| Volume scaling | | | ✓ |
| Model optimization | ✓ | | |
| Prompt management | ✓ | | |
| Conversation depth | ✓ | | ✓ |

---

**"What's our current cost per AI call, broken out by input tokens, output tokens, and which model?"**

*What this reveals:* Whether anyone has measured the unit economics. If they say they don't know, that's a critical gap. If they can answer precisely, they're managing AI cost actively.

---

**"Do we have prompt caching enabled? What percentage of our input tokens are cached vs. uncached?"**

*What this reveals:* Whether a potentially 80–90% cost reduction is sitting on the table untouched. Many teams ship without enabling caching because it's not on by default.

---

**"What's the p95 latency on AI API calls — TTFT and time to complete?"**

*What this reveals:* Whether latency issues will surface as user complaints post-launch. p50 latency (median) is often misleading — what matters is p95 (the 95th percentile user's experience).

---

**"Are any of our AI features running real-time that could run asynchronously?"**

*What this reveals:* Whether the batch discount is being captured where applicable. Engineers default to real-time unless the PM explicitly designs for async.

---

**"How does our AI cost scale at 2× and 10× current volume?"**

*What this reveals:* Whether cost is linear (most common — scales with usage) or super-linear (conversation history accumulation can cause this). Super-linear cost curves break unit economics at scale.

---

**"Is there a model cascade, or do all AI calls hit the same model?"**

*What this reveals:* Whether there's optimization work already done or a clear opportunity. Also surfaces whether engineering has experimented with smaller models on subsets of queries.

---

**"What's in our system prompt, and how long is it?"**

*What this reveals:* System prompts grow silently. If no one has audited recently, it's likely longer than it should be — and every extra token is being charged on every API call.

---

**"What happens to our AI cost if the average conversation length doubles?"**

*What this reveals:* Whether conversation history accumulation is understood as a cost driver. In multi-turn chat products, conversation context re-sent on every turn means cost grows quadratically with session depth unless there's a truncation strategy.

## W4 — Real product examples

### BrightChamps PQS — batch processing as cost architecture

**What:** PQS evaluates class transcripts against a 10-point pedagogical rubric to generate post-class parent reports. At 70% of all one-to-one class volume, this means thousands of LLM calls per day.

**Architecture:** Transcripts ingested after class ends → asynchronous engine processing → parents receive reports 30–60 minutes later.

**Why this matters:** This isn't just a latency choice—it's a cost strategy.

| Decision | Real-time evaluation | Batch async processing |
|----------|---------------------|------------------------|
| API pricing | Standard rate | 50% discount |
| Cost multiplier | 2× | 1× (baseline) |
| Infrastructure | Real-time systems required | Standard async infra |
| User benefit | None (no live parent viewing) | 30–60 min latency acceptable |

**Takeaway:** The batch architecture qualifies for 50% API pricing discounts with zero user experience degradation.

⚠️ **PM failure mode:** The Google Meet audio pipeline cost architecture was "still being finalized" at document time, flagged as a blocker for full coverage. Shipping a feature without a clear cost model for major data sources is a critical oversight.

---

### BrightChamps TrialBuddy — latency SLAs as product requirements

**What:** Conversational bot handling class enrollment, troubleshooting, and escalations.

**PM-defined latency requirements (from PRD):**

| Requirement | Target | Design implication |
|-------------|--------|-------------------|
| Bot response time | <2 seconds per turn | Model selection constraint |
| Slot availability query | <500ms | Caching requirement (explicit) |
| Escalation handoff | <30 seconds | Queue/routing SLA |

**Model selection logic:**
- Frontier model generating 200-token responses = 4–6 seconds (violates 2s SLA)
- Solution: smaller, faster model for routine intents (joining link resend, troubleshooting)
- Only escalate to capable reasoning for ambiguous decisions

**Unit economics basis:**
- Estimated revenue impact: INR 18,00,000
- Resolution rate: 70% without human intervention
- **Critical equation:** (resolution rate × queries/month) × (cost per query) = ROI
  
> **Key principle:** The PM who cannot state this equation cannot defend the AI budget.

**Takeaway:** Latency isn't a soft preference—it's a product constraint that drives architectural and model decisions.

---

### OpenAI — model cascade in production

**Pattern:** Use small models for high-volume, low-complexity tasks. Use large models only for complex reasoning.

| Task category | Model | Volume % | Cost impact |
|---------------|-------|----------|------------|
| Intent classification | GPT-4o-mini | 70–80% | Low |
| Slot filling | GPT-4o-mini | — | Low |
| FAQ responses | GPT-4o-mini | — | Low |
| Complex reasoning | GPT-4o | 20–30% | High |
| Code generation | GPT-4o | — | High |
| Nuanced synthesis | GPT-4o | — | High |

**Cost math:** At 60× price ratio between small and large models, a 70/30 split reduces average cost per query by **~80%** compared to routing everything through the large model.

**Takeaway:** Cascade architecture is table stakes for LLM cost management at scale.

---

### Anthropic Claude API — prompt caching impact

> **Prompt caching:** First use charges full rate; subsequent reads within 5-minute window charge ~10% of input token cost.

**Ideal use case:** Products with large, stable system prompts (knowledge bases, persona definitions, instruction sets).

**Cost example:**
- Volume: 1 million calls/day
- System prompt: 2,000 tokens
- Pricing: claude-opus
- **Monthly savings from caching: ~$27,000**

⚠️ **Silent cost leak:** Teams that disable caching inadvertently (by appending timestamps or session IDs to the static prompt portion) lose this discount without realizing it.

**Takeaway:** Caching is only effective if the prompt structure remains stable. Audit for hidden timestamp/session logic that breaks cache validity.

---

### Vercel AI SDK — streaming as table stakes

> **Streaming:** Sending response tokens as they generate, rather than waiting for full completion.

**Perception vs. reality:**

| Delivery method | Total time | Perceived speed | User experience |
|-----------------|-----------|-----------------|-----------------|
| Synchronous | 6 seconds | Slow (broken product) | Full response appears at once |
| Streaming | 6 seconds | Fast | Word-by-word arrival feels interactive |

**Research finding:** Streaming reduces *perceived* response time by 60–80% in user studies despite identical total generation time.

**Product implication:** Vercel made streaming the default for all AI SDK hooks—an implicit acknowledgment that synchronous delivery is no longer acceptable for interactive AI features.

**Takeaway:** For user-facing AI, streaming isn't optional. It's table stakes.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM, Ex-Engineer PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1 — What breaks and why

### System prompt bloat compounds silently

System prompts grow by accretion: a new edge case gets appended in a hotfix, a new product feature requires new instructions, a new safety requirement adds another paragraph. No individual change seems costly. Accumulated over 12 months, a system prompt that started at 200 tokens reaches 3,000 tokens, adding $135/day in input cost on a 1M-call-per-day product at frontier model prices — without anyone noticing.

**PM prevention — operational thresholds that should be in every AI feature spec:**

| Guardrail | Threshold | Action when crossed |
|---|---|---|
| System prompt length | >1,500 tokens | Requires PM + tech lead approval; audit for removal opportunities |
| Response max_tokens | Set per feature (e.g., 400 for chat, 800 for reports) | Hard API cap; PM owns definition |
| Conversation history depth | >8 turns included in context | Trigger summarization or truncation |
| Monthly AI cost vs. budget | >80% of budget by day 20 | Alert; PM reviews cascade or batching options |
| Cost per feature interaction | >$0.10 per call for commodity task | Trigger model evaluation; haiku-class should handle <$0.01 |

**Cost monitoring infrastructure:** Track input token count, output token count, model used, feature name, and cost per call as structured log events. Route them to a cost dashboard (Datadog, Grafana, or provider-native usage explorer). 

> **Without per-feature cost attribution, you cannot tell which feature caused a cost spike.**

---

### Conversation history creates super-linear cost curves

In multi-turn chat, the full conversation history re-sent on every turn means token cost grows with the square of conversation depth: turn 10 sends 10× the tokens of turn 1. A product that works economically at 5-turn average sessions breaks at 20-turn sessions. 

**The failure mode:** Teams discover this when a cohort of power users — who have long conversations — generates 10× the AI cost of typical users.

**PM prevention:** Define a conversation history truncation strategy before launch.

| Approach | How it works |
|---|---|
| Summarization | Compress old turns into a condensed summary |
| Context capping | Limit context window to N most recent turns |
| Retrieval layer | Move older context to persistent storage, retrieve as needed |

---

### Cheap model quality regression surfaces as user churn, not error rates

When you switch from a large to a small model to cut costs, the failure mode isn't a hard error — it's subtly worse responses that users tolerate for a while, then stop using the feature.

**What you'll observe:**
- Error rate dashboards: no change
- Usage metrics: drift down
- Time to diagnosis: 3–4 weeks (after lost behavior data)

**PM prevention:** Run A/B tests on model changes, not just internal quality evals. Track these as quality signals:
- Feature engagement rate
- Session depth
- Task completion rate
- LLM-specific evals

---

### Batch discounts are lost when async features get forced real-time

An async feature designed to run in batch gets a "nice to have" latency improvement requested — "can we show the report faster?" Engineering makes it real-time to satisfy the request.

**What happens:**
- Batch discount disappears
- Cost doubles
- 10-minute latency reduction doesn't show up in any metric as valuable

**PM prevention:** Make the cost implication of real-time vs. async explicit in design reviews.

> **Decision framing:** "Making this real-time removes the 50% batch discount, adding $X/month. What's the user value of the latency improvement?" is a **decision**, not an implementation detail.

## S2 — How this connects to the bigger system

### Evals and cost are the same conversation

Running evals (04.06) at scale is itself an AI cost problem: LLM-as-judge evals hit the model API on every test case. A robust eval suite running 10,000 test cases daily costs real money if run against frontier models.

| Approach | Cost Impact | Quality Signal | Risk |
|----------|------------|----------------|------|
| Skip evals to save cost | ✓ Lower eval costs | ✗ No regression detection | Undetected quality drops |
| Run expensive evals on every deployment | ✗ Eval pipeline > production cost | ✓ Complete visibility | Budget overrun |
| **Tiered eval strategy** | ✓ Optimized | ✓ Full coverage | Minimal |

**Tiered strategy:** fast, cheap evals on every commit → comprehensive, expensive evals on releases.

---

### RAG retrieval latency compounds with model latency

RAG (04.03) adds a retrieval step before inference:

1. Embed the query
2. Search the vector database
3. Retrieve top-k documents
4. Inject them into the prompt

Each step adds latency. Vector search typically adds **50–200ms**; document injection adds tokens (cost) and TTFT (latency).

**For RAG-powered features with TTFT requirements:** retrieval must be optimized alongside model selection.

**Retrieval-side latency levers** (no model changes required):
- Precomputing embeddings
- Caching frequent query results
- Using approximate nearest neighbor search

---

### Fine-tuning as a cost reduction strategy

Fine-tuning (04.05) is often framed as a quality improvement tool. Its second use is **cost reduction:** a fine-tuned small model can match the quality of a larger general model on a specific task, at a fraction of the inference cost.

**When to evaluate fine-tuning:**
- Task is high-volume, repetitive, and well-defined
- Typical candidates: intent classification, slot filling, rubric evaluation
- Monthly cost on large model exceeds $3,000
- Task definition has been stable for 3+ months

#### ROI calculation

```
Fine-tuning ROI breakeven (months) =
  Fine-tuning cost ($) /
  (Monthly cost on large model − Monthly cost on fine-tuned small model)
```

**Example:**
- Fine-tuning cost: $5,000 (engineering + API)
- Large model cost: $14,000/month on this task
- Fine-tuned small model cost: $230/month
- Monthly savings: $13,770
- **Breakeven: 0.36 months (< 2 weeks)**

At that breakeven, fine-tuning is obviously correct.

**⚠️ ROI reverses** when:
- Task volume is low
- Task definition changes frequently (fine-tune maintenance eats savings)

---

### AI agent costs are non-deterministic and hard to cap

Agents (04.09) run multiple model calls per task: planning, tool invocation, reflection, replanning.

> **Agent cost distribution:** Cost per agent run is a distribution, not a fixed number. A task taking 3 tool calls in happy path may take 8 in failure/retry scenarios.

**Cost guardrails required:**
- Explicit step limits (max tool calls per run)
- Output length controls
- Fallback escalation to human (rather than indefinite retries)

⚠️ **Risk:** Products built on agents without cost guardrails regularly produce surprise invoices when a task class hits the long tail of the step distribution.

## S3 — What senior PMs debate

### Position A vs. Position B: Cost optimization timing

| **Position A** | **Position B** |
|---|---|
| **Optimize cost aggressively from day one** | **Ship on the best model and optimize later** |
| Build model cascade, enable prompt caching, design for async batch before launch | Launch on frontier model, get to product-market fit, then optimize |
| Unit economics that fail at 10K users fail at 1M—fix now | Quality delta between frontier and cheaper models is real during early development |
| Every month unoptimized = compounding cost burn at scale | Cost of frontier model at small scale (~$1K/month) < engineering effort to optimize |
| Teams that defer refactor themselves into expensive, risky corner | Optimize when you have volume data to guide cascade design |

> **The genuine tension:** Both positions are correct—for different stages. Position B wins at pre-PMF scale (<10K active users, <$2K/month costs). Position A wins post-PMF when cost scales with growth. **The mistake:** applying Position B logic at scale—exactly what happens when teams don't revisit cost architecture after their first major growth milestone.

---

### The latency arms race and its limits

**What's changing:** Model providers are consistently reducing latency. TTFT on frontier models in 2025 is 2–4× faster than 2023.

**What this reveals:** One of the core arguments for model cascades—"smaller models are faster"—is eroding. As frontier models get faster, the latency advantage of small models shrinks, and the quality gap becomes the dominant tradeoff.

⚠️ **Senior PMs who locked in cascade logic based on 2023 latency data may be over-optimizing for a problem that's being solved by infrastructure improvement.**

---

### AI infrastructure: Moat or liability?

| **The moat argument** | **The liability argument** |
|---|---|
| Proprietary cost optimization (custom caching, fine-tuned routing, negotiated pricing) = 12–18 months to replicate | AI model pricing deflates 40–60% per year; model quality improves faster than products can tune |
| Durable competitive advantage | Infrastructure built around one provider's pricing model is a liability when competitor offers 50% better price-performance |

> **Status as of 2025:** Whether to invest deeply in AI cost infrastructure versus staying modular and provider-portable is genuinely unresolved. The answer will likely differ by company scale.

---

### What AI is doing to this concept

> **The cost-quality tradeoff is collapsing from below.** Models that were frontier quality 18 months ago are now available at small-model prices. GPT-4-class capability (2023) = Haiku-class pricing (2025).

**Implication for your product:** Every product built on cost-quality analysis from 18+ months ago should be re-evaluated.

- The "good enough" model for commodity tasks is now substantially better
- The "best quality" task bar keeps shifting to the newest frontier

**Proactive PM move:** Re-run model selection decisions every 6–12 months rather than waiting for engineering to flag a quality issue.