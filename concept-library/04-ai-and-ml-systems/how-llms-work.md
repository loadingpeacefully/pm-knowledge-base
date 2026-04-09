---
lesson: How LLMs Work
module: 04 — AI & ML Systems
tags: tech
difficulty: working
prereqs:
  - 01.01 — What is an API: LLMs are accessed via API; understanding request/response structure gives context for how prompts and outputs flow
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

## F1. The class evaluation that invented events that never happened

The PQS system at BrightChamps was built to evaluate class quality automatically. Every completed class — a teacher, a student, 45 minutes of instruction — produces a transcript. PQS reads that transcript, scores it against a 10-point pedagogical rubric, and generates a parent-facing report showing how much the child participated, which concepts were covered, and what to reinforce at home.

### The Problem: Confident Fabrication

When the team first built the evaluation engine, they gave the LLM a class transcript and asked it to identify pedagogical events: `HOMEWORK_CHECK`, `EXPLANATION`, `GUIDED_PRACTICE`, and others.

**What the team observed:**
- Output looked good, confident, and structured
- LLM produced statements like: "EXPLANATION event at 12:34 — teacher demonstrated multiplication with apples example"
- LLM produced: "HOMEWORK_CHECK at 4:15 — teacher reviewed last session's assignment"

**What QA reviewers found when checking against actual transcripts:**
- At 12:34: the student was talking, not the teacher
- At 4:15: homework was never mentioned

> **Hallucination:** The model producing confident, structured, grammatically correct output that is factually wrong.

The LLM wasn't reading the transcript and finding those events. It was predicting what a good class evaluation would look like — and generating plausible-sounding events, complete with timestamps, that it invented.

### The Solution: Anchor to Evidence

The fix was implemented in the PQS spec. The Forensic Ledger — the structured output the LLM produces — now requires:

| Requirement | Purpose |
|---|---|
| Exact evidence quotes from the actual transcript | Force direct citation of source material |
| Mathematical score justification for every event tagged | Anchor scoring to measurable data |
| Rejection of any event without verbatim transcript quote | Eliminate invented details |

Requiring the model to cite its source forced it to stay tethered to real evidence instead of predicting what a good evaluation would contain.

---

**What this reveals about LLMs:** They don't read and reason. They predict text. Given a context, an LLM produces the text that is most likely to follow. When you give it a task without anchoring it to specific evidence, it predicts what a confident, correct answer would look like — even when that means inventing the evidence.

This is the most important thing a PM building AI products needs to understand. Every decision that follows — how to design prompts, what information to provide, when to trust the output — flows from this.

## F2. What it is — the world's most sophisticated autocomplete

An LLM (Large Language Model) is a statistical prediction engine. It has read an enormous amount of text — the internet, books, code, scientific papers — and learned patterns: which words follow which words, which ideas follow which ideas, which sentence structures go where.

When you give it a prompt, it predicts the most likely text to come next. Then it predicts the next word after that. Then the next. One token at a time, until the response is complete.

> **Token:** The basic unit an LLM reads and writes. Roughly 3/4 of a word in English. "BrightChamps" is 3–4 tokens. A 45-minute class transcript might be 50,000 tokens. Tokens matter because they determine cost (you pay per token), speed (more tokens = slower response), and what the model can process at once.

**The phone keyboard analogy:**
When you type "Happy birth" and your phone suggests "day", "birthday", or "days" — that's the same mechanism, just scaled by a factor of a billion. The LLM has seen so much text that its predictions are coherent, nuanced, and often indistinguishable from human writing.

### What it means that LLMs predict text

| Implication | Details |
|---|---|
| **Knowledge is pattern-based** | They don't "know" things the way a database knows things. They know patterns — what text tends to follow what other text. |
| **Confident but fallible** | They can produce confident, well-formatted, grammatically perfect output that is completely wrong — because wrong text can be statistically plausible given the context. |
| **No real-time access** | They can't look up current information (unless given a tool to do so). An LLM's knowledge is frozen at its training cutoff. BrightChamps class schedules for next Tuesday don't exist in any training data. |
| **Prompt-sensitive** | They respond to how you frame a question. The same underlying question, asked differently, can produce very different outputs — because different framings predict different continuations. |

### Three terms every PM needs

> **Context window:** The maximum amount of text an LLM can process in a single interaction — its "working memory." Measured in tokens. GPT-4 Turbo: 128,000 tokens (~100,000 words). A 45-minute class transcript might be 50,000 tokens — fits comfortably. A full week of classes would not. When content exceeds the context window, you must chunk, summarize, or use a larger model.

> **Temperature:** A setting that controls how predictable vs. creative the output is. Low temperature (0.0–0.3): the model always picks the highest-probability next token — consistent, predictable, conservative. High temperature (0.7–1.0): the model sometimes picks lower-probability tokens — more varied, creative, less predictable. TrialBuddy's persona spec ("Spartan sentences, no filler, no robotic language") is partly implemented as a low-temperature setting with a personality prompt.

> **Hallucination:** When the model produces confident, plausible-sounding output that is factually incorrect. Not a bug — a predictable consequence of text prediction. The model predicts what a correct answer would look like; when it lacks grounding evidence, it invents one.

## F3. When you'll encounter this as a PM

### Scoping an AI feature — "what can the LLM do?"

PMs regularly receive requests like "can we use AI to summarize student progress?" or "can the bot handle parent complaints?" The honest answer depends on what information the model has access to, not just what it's capable of in principle.

**PM question:** "What information will the model have access to when it generates this response?"

| Scenario | Access | Outcome |
|----------|--------|---------|
| Nothing beyond training data | ❌ Limited | Expect hallucination on product-specific details |
| Student's last 10 classes via context | ✅ Grounded | Output is anchored to real data |

*What this reveals:* Grounding (access to real information) matters more than raw capability.

---

### Reviewing AI output quality — "why is it wrong?"

The PQS hallucination problem was discovered in QA. When an AI feature produces wrong outputs, the first diagnostic question is: **did the model have the information it needed, or did it invent?**

| Root Cause | Definition | Fix Type |
|-----------|-----------|----------|
| **No grounding** | Model had no access to needed information | Add data access/context |
| **Reasoning failure** | Model had information but misused it | Improve prompt/model capability |

**PM action:** In AI feature reviews, ask engineering to show you cases where the model had all the right information and still failed — those reveal model capability limits. Cases where it was missing information are grounding problems, not capability problems.

---

### Setting quality thresholds — "how accurate is good enough?"

PQS targets 91% accuracy on completed paid classes. That number was set by the team based on what parents would tolerate and what the business needed.

> **The reality:** 100% is impossible with current LLM technology. 70% might destroy parent trust. 91% is the operating point.

**PM action:** Before any AI feature launches, define:
- The acceptable error rate
- What "error" means in your context

An LLM wrong 9% of the time on class evaluation may be acceptable. An LLM wrong 9% of the time on payment-related queries is not.

---

### When the team says "the model is confident but wrong"

⚠️ **Confidence in LLM output means nothing.** The model doesn't know when it's wrong — it has no internal error signal. It produces the most likely text regardless of whether that text is true. A model can be 99% confident in a hallucinated fact.

**PM action:** For any AI feature where errors have real consequences (medical, financial, legal, safety), design the system to:
- Cite sources
- Require human review
- Treat confidence scores as unreliable signals

---

### Selecting a model — "which one should we use?"

Model selection is a PM tradeoff, not purely an engineering call.

| Model Class | Examples | Strengths | Tradeoffs |
|-------------|----------|-----------|-----------|
| **Large/Capable** | GPT-4, Claude Opus | High capability, complex reasoning | Higher cost, higher latency |
| **Small/Fast** | GPT-4o-mini, Claude Haiku | Lower cost, faster response | Less capable on complex tasks |

**Examples:**
- **TrialBuddy troubleshooting flows:** Smaller model likely sufficient
- **PQS rubric evaluation:** Complex pedagogical transcripts require higher capability

**PM action:** Ask "what's the minimum model capability we need, and what does the wrong call cost?"
- Too small → poor quality, user trust damage
- Too large → unnecessary cost and latency
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that LLMs predict text, what tokens/context window/temperature/hallucination mean.
# ═══════════════════════════════════

## W1. How LLMs actually work — the mechanics that matter for PM decisions

### Quick reference

| Concept | Why it matters for PM |
|---|---|
| **Prediction loop** | Every token costs time + money; responses stream; errors compound |
| **Context window** | Your hard constraint on what the model can see; manages cost & latency |
| **Temperature** | Controls consistency vs. creativity; production use requires low temps |
| **Training vs. inference** | Model knowledge is frozen; current data must go in context every time |

---

### 1. The prediction loop — what happens when you send a prompt

> **The core insight:** An LLM doesn't "think through" a response and then output it. It generates one token at a time, each token conditioned on everything before it — the prompt and every token already generated.

This has real PM implications. A response is not computed upfront and delivered; it streams. If you've ever watched a ChatGPT response appear word by word, that's the prediction loop made visible. The model doesn't "know" the complete response when it starts — it's discovering it one token at a time.

**The loop:**
1. Input tokens (your prompt + conversation history) are processed by the model
2. Model outputs a probability distribution over the entire vocabulary (~50,000 possible next tokens)
3. A token is selected based on that distribution (temperature controls how this selection works)
4. That token is appended to the context
5. Repeat from step 1 until an end-of-sequence token is generated or token limit is reached

**What this means for product design:**
- Long responses cost more and take longer — every extra token is one more loop iteration
- Responses can degrade over very long outputs — each new token is conditioned on prior tokens, and errors can compound
- Streaming is native — responses can be shown progressively; no need to wait for completion

---

### 2. The context window — your product's most important constraint

> **Context window:** The working memory of the model. Everything the model can "see" to generate a response must fit within it.

**What goes in the context:**

| Element | Examples |
|---|---|
| System prompt | "You are Niki, a friendly support bot for BrightChamps" |
| Conversation history | All prior turns in this session |
| Retrieved documents | Knowledge base articles, student records, class transcripts |
| Current user message | "What time is my child's class?" |
| Output buffer | Space for the model's response |

**PQS context window constraint:**

A 45-minute class produces roughly 8,000–15,000 tokens of transcript. A 128k context window can hold that comfortably — plus the system prompt and rubric instructions. But PQS processes classes continuously; if the system accidentally accumulated multiple class transcripts in the same context, it would overflow. The architecture deliberately processes one transcript per inference call.

**TrialBuddy session persistence constraint:**

TrialBuddy maintains a 3-day session window. If a parent's full 3-day conversation history is included in every new message's context, long sessions become expensive. Most production chatbots use a sliding window (last N turns) or summarization to manage conversation length.

**Context window sizes and practical limits:**

| Context window size | Practical limit | Typical use case |
|---|---|---|
| 8K tokens | ~6,000 words | Short chatbot turns, single documents |
| 128K tokens | ~100,000 words | Long documents, extended conversations, full transcripts |
| 1M tokens | ~750,000 words | Full codebases, book-length content (Gemini 1.5 Pro) |

**The PM tradeoff:** Larger context = higher cost per call and higher latency. Always ask: "What do we actually need to include, vs. what are we including out of convenience?"

---

### 3. Temperature and sampling — controlling output behavior

> **Temperature:** A parameter that controls the randomness of token selection. Lower = more deterministic; higher = more creative and variable.

**Behavior by temperature setting:**

| Temperature | Behavior | When to use |
|---|---|---|
| 0.0 | Always picks highest-probability token. Same input = same output every time. | Classification, structured data extraction, factual Q&A |
| 0.3–0.5 | Mostly predictable with some variation. | Customer support (consistent but not robotic) |
| 0.7–0.9 | Notable variation between runs. Feels more creative. | Marketing copy, brainstorming, creative writing |
| 1.0+ | High randomness. Can be incoherent. | Rarely appropriate in production |

**TrialBuddy's temperature implication:**

The persona spec says "Spartan sentences, no filler, no robotic language." This is implemented through a combination of a low temperature setting (consistent responses) and a system prompt that defines the persona and style. The style instruction is in the prompt; temperature controls how rigidly the model follows it.

**PQS temperature implication:**

The rubric evaluation engine should run at temperature 0.0 or close to it. The goal is consistent, reproducible evaluation — not creative variation. If the same class transcript produced different scores each time it was evaluated, the rubric would be useless for QA purposes. Deterministic evaluation requires low temperature.

---

### 4. Training vs. inference — two entirely different concepts

| Aspect | Training | Inference |
|---|---|---|
| **What it is** | Teaching the model by adjusting weights on billions of examples | Running the trained model to generate a response |
| **When it happens** | Months before you use the model | Every time a user sends a message |
| **Who does it** | OpenAI, Anthropic, Google — not you | Your product, via API |
| **Cost** | Hundreds of millions of dollars (for foundation models) | Fractions of a cent to cents per call |
| **Knowledge cutoff** | Fixed at training completion | Can see new information if provided in context |

**The PM implication of the training/inference split:**

The model's learned knowledge is frozen at training. What the model "knows" about BrightChamps, current schedules, enrolled students, and this parent's specific situation — none of that exists in the model's weights. It must be provided in the context (inference time) or the model will fabricate plausible answers.

⚠️ **Hallucination risk:** Without a knowledge base, the model will confidently generate false information. TrialBuddy requires a knowledge base because Niki would otherwise invent class times, fabricate troubleshooting steps, or give wrong joining link formats — because it has no access to current operational data.

---

### 5. How the BrightChamps systems use LLMs — two patterns

#### PQS: LLM as structured extractor

**What:**
1. Input: raw class transcript (15,000 tokens)
2. System prompt: "You are a pedagogical evaluator. Identify events from this rubric. For each event, quote the exact text as evidence."
3. Output: structured JSON with event tags, timestamps, evidence quotes, scores

**Why:** Temperature ~0. Goal: consistent, reproducible, grounded output.

**Takeaway:** Exact quote requirement forces the model to cite from the provided text, protecting against hallucination.

---

#### TrialBuddy: LLM as conversational router

**What:**
1. Input: parent message + conversation history + knowledge base articles
2. System prompt: "You are Niki, a support bot for BrightChamps. Answer questions using only the provided knowledge base. After 3 unresolved interactions, offer human escalation."
3. Output: a response + a structured intent signal (join, troubleshoot, reschedule, escalate)

**Why:** Temperature ~0.3. Goal: consistent persona, some naturalness.

**Takeaway:** "Use only the provided knowledge base" instruction constrains the model to retrieved content, preventing out-of-context fabrication.

## W2. The decisions LLM architecture forces

### Decision 1: What goes in the context?

Every token in the context costs money and adds latency. The PM decides what information the model actually needs:

| Always include | Include selectively | Rarely include |
|---|---|---|
| System prompt (defines behavior) | Recent conversation history (last 5–10 turns) | Full conversation history (use summarization instead) |
| The user's current message | Relevant knowledge base articles (retrieved, not all) | Entire knowledge base |
| Any data the model needs to answer correctly | Student/account context if relevant | All historical student data |

> **Context window principle:** Start with minimal context and add what's needed. Adding context is easy; removing it when the bill arrives is harder.

---

### Decision 2: What accuracy threshold is acceptable?

LLMs are probabilistic. 100% accuracy is not a design target — it's not achievable with current technology. The PM sets the operating threshold based on consequences:

| Use case | Error consequence | Acceptable error rate | Design response |
|---|---|---|---|
| PQS rubric scoring | Parent sees inaccurate class evaluation | ~9% missed / miscategorized events | Require evidence quotes; human QA sampling |
| TrialBuddy joining link | Parent misses class, can't find link | Near-zero | API lookup (not LLM generation) for the actual link |
| TrialBuddy troubleshooting | Parent gets wrong fix, still can't join | ~5–10% | Human escalation after 3 failed turns as safety net |
| Payment-related queries | Wrong charge information | <1% | Do not use LLM; use deterministic system |

> **The principle:** Don't use LLM generation for outputs that must be exactly correct. Use API lookups, database queries, or deterministic logic for facts — LLMs for synthesis, explanation, and conversation.

⚠️ **High-stakes outputs:** Payment information, account access, and critical facts should never rely solely on LLM generation. Combine with deterministic systems or human review.

---

### Decision 3: Model size vs. cost vs. quality

| Model tier | Example | Cost per 1M tokens | Best for |
|---|---|---|---|
| Large (frontier) | GPT-4o, Claude Sonnet | $3–15 | Complex reasoning, nuanced evaluation, long documents |
| Mid-tier | GPT-4o-mini, Claude Haiku | $0.10–0.60 | Chatbots, classification, simple Q&A, high-volume |
| Small / local | Llama 3, Mistral | Infrastructure cost | Privacy-sensitive, high-volume, offline use cases |

**For BrightChamps — model selection by use case:**

- **PQS transcript evaluation:** Mid-to-large tier — long context, pedagogical nuance required
- **TrialBuddy troubleshooting:** Mid-tier sufficient — responses are templated, knowledge base grounds the output
- **Parent-facing narrative generation (Actionable Next Steps):** Large tier — needs to feel personal and high quality

---

### Decision 4: When to add grounding vs. fine-tuning vs. prompting

| Technique | What it does | When to use | Cost |
|---|---|---|---|
| **Prompting** | Instructions in the system prompt | Default starting point | Low — just text |
| **Grounding (RAG)** | Retrieve relevant documents and include in context | When the model needs current or proprietary data it wasn't trained on | Medium — retrieval infrastructure |
| **Fine-tuning** | Re-train model on your specific data and style | When prompting consistently fails; when you need a distinct persona or domain knowledge baked in | High — labeled data, compute, ongoing |

**What BrightChamps chose:**

- **PQS:** Grounding — the transcript is the grounding document
- **TrialBuddy:** Grounding — the knowledge base is retrieved and included in context
- **Neither team needed fine-tuning** — prompting + grounding achieved the required quality

## W3. Questions to ask your engineer

| Question | What this reveals |
|---|---|
| **1. What's in the context window for every call?** | Whether the system is including unnecessary tokens (full conversation history, full knowledge base) vs. only what's needed. *What this reveals:* Cost and latency exposure. |
| **2. What's our token cost per user interaction?** | The unit economics of the AI feature. A PQS evaluation call at 50,000 tokens costs very differently than a TrialBuddy chatbot turn at 2,000 tokens. *What this reveals:* True scalability when extrapolated to monthly volume. |
| **3. What temperature are we running at?** | Whether the team has thought about consistency. *What this reveals:* Temperature 0 for evaluation. Temperature 0.3 for support. Temperature 0.8 for creative features. "We haven't set it" means you're at the default, which may not match the use case. |
| **4. What happens when the model hallucinates?** | Whether there are grounding mechanisms, output validation, or human review in place. *What this reveals:* "We catch it in QA" is not a production answer for a customer-facing feature. ⚠️ |
| **5. What's our context window utilization — how close to the limit are we?** | Whether there's headroom or whether long conversations / long documents will start truncating. *What this reveals:* Truncation typically drops the beginning — which is often the system prompt. That destroys behavior. |
| **6. How is the system prompt versioned?** | Prompts are code. They should be version-controlled, reviewed before changes, and rollback-able. *What this reveals:* "We just update it" means a prompt change can break production with no rollback path. ⚠️ |
| **7. What's the model's knowledge cutoff, and does anything we're asking depend on post-cutoff knowledge?** | Whether the model will confidently hallucinate on current events, recent product changes, or new features. *What this reveals:* If yes: grounding (context injection or retrieval) is required. |
| **8. How do we measure quality — what's our eval pipeline?** | Whether there is a structured quality measurement process (see 04.06 AI Evals). *What this reveals:* Shipping an LLM feature without an eval pipeline means you're measuring quality via user complaints. ⚠️ |

## W4. Real product examples

### BrightChamps PQS — LLM as pedagogical evaluator

**What:** Every completed class transcript (Zoom or Google Meet, 45–60 minutes) is passed to an LLM evaluation engine. The engine maps the transcript to a 10-point pedagogical rubric, produces a structured JSON Forensic Ledger with event tags, timestamps, and evidence quotes, and generates the parent-facing post-class report.

**LLM architecture decision:**

| Component | Specification |
|---|---|
| Input | Full transcript (~10,000–50,000 tokens) |
| Prompt design | Rubric-based evaluation with required evidence quoting |
| Output | Structured JSON (Forensic Ledger) with event tags, exact evidence quotes, score justifications |
| Temperature | Low (deterministic scoring required) |
| Grounding mechanism | Exact evidence quote requirement forces model to cite from the transcript |

**Scale:** Processes 70% of all OTO platform volume. Achieves 91% accuracy on scored classes. 9% missed due to non-English language detection (multi-lingual prompts are future phase).

**The hallucination fix:**

> **Grounding through citation:** Requiring exact evidence quotes in the output structure means the model must quote specific text from the transcript for every event it tags. If no supporting text exists, the model cannot fabricate it without the quote being verifiably absent from the input. This transforms a "predict a good evaluation" task into a "locate and extract evidence" task.

**Takeaway:** When you need LLM outputs to be factually reliable, anchor them to a specific evidence document and require the model to cite it. The quality of the prompt design — not the model's inherent capability — determines whether the output is trustworthy.

---

### BrightChamps TrialBuddy — LLM as support conversation engine

**What:** Niki is the AI persona of TrialBuddy — a support chatbot deployed on WhatsApp, Zalo, the trial dashboard, and blog pages. It handles joining link retrieval, Zoom troubleshooting, rescheduling, re-trial booking, and escalation.

**LLM architecture decision:**

| Component | Specification |
|---|---|
| Input | Parent message + last N conversation turns + retrieved knowledge base articles |
| System prompt | Persona definition ("Niki — friendly, supportive, Spartan sentences"), scope constraints ("use only the provided knowledge base"), escalation rules ("after 3 unresolved turns, offer human escalation") |
| Output | Conversational response + implicit intent classification (which flow to invoke) |
| Knowledge base | Company info, courses, schedules, troubleshooting steps — critical for grounding |

**The scope boundary:**

> **Narrow scope principle:** TrialBuddy handles pre-trial and trial-day queries only. Post-enrollment, payments, and billing are explicitly out of scope. This is a PM decision: keep the model's scope narrow enough that the knowledge base can fully cover it. A chatbot that tries to answer everything has a large hallucination surface. One that handles 5 well-defined flows can be fully grounded.

**Estimated business impact:** INR 18,00,000 (~$22,000 USD) from trial-to-enrollment lift and support cost reduction.

**Takeaway:** Chatbots succeed when the problem domain is narrow and the knowledge base is complete. The temptation is to expand scope ("can it also handle billing?"). The LLM capability is there — but the grounding for billing queries may not be, and one bad billing answer destroys parent trust more than a hundred correct troubleshooting answers build it.

---

### OpenAI — the context window arms race

**What:** Between GPT-3.5 (4K context) and GPT-4 Turbo (128K context), the practical applications of LLMs changed entirely. At 4K tokens, you could handle short conversations. At 128K, you could process entire books, codebases, or full class transcripts in a single call.

| Model | Context window | What became possible |
|---|---|---|
| GPT-3.5 (2022) | 4,096 tokens | Short chatbot turns, document summaries |
| GPT-4 (2023) | 8,192 tokens | Moderate documents, multi-turn conversations |
| GPT-4 Turbo (2023) | 128,000 tokens | Full books, full transcripts, full codebases |
| Gemini 1.5 Pro (2024) | 1,000,000 tokens | Full audio/video files, multi-document analysis |

**Takeaway:** Context window size is a product capability multiplier. Features that required chunking and summarization pipelines at 4K become trivial at 128K. When you hear "we can't fit the whole transcript" — check whether the model generation you're using is the actual constraint, or whether a more recent model generation removes the problem entirely.

---

### Anthropic / Claude — Constitutional AI and output behavior

**What:** Anthropic uses a technique called "Constitutional AI" in training Claude — the model is trained to follow a set of principles that shape its output behavior. This produces reliable refusals on harmful content, consistent politeness, and predictable behavior on edge cases.

**Why it matters for PMs:** Different foundation models have different trained behaviors, not just different capabilities. Claude tends to refuse edge cases more conservatively than GPT-4o. GPT-4o tends to be more willing to follow unusual instructions. These differences are training artifacts, not prompting artifacts — you can't fully override them with a system prompt.

**Takeaway:** Model selection is a behavior decision, not just a capability decision. The model you choose brings its training biases, safety behaviors, and style tendencies to your product. Test on your specific edge cases before committing to a model provider.

---

### Stripe — Enterprise LLM with compliance, audit logging, and multi-tenancy

**What:** Stripe uses LLMs across their developer documentation assistant, fraud signal summarization, and support routing. Their enterprise integration with platforms like Salesforce, SAP, and Workday surfaces as AI-assisted reconciliation and dispute explanation features.

**Enterprise architecture constraints:**

| Constraint | What it means for LLM architecture |
|---|---|
| Data residency | Enterprise customers in EU require inference to stay within EU data boundaries — model selection is now a geography decision |
| Audit logging | Every LLM call must log input hash, model version, output hash, timestamp — for SOC 2 and financial audit trails |
| Multi-tenancy isolation | One enterprise customer's data must never appear in another's context — retrieval pipelines enforce tenant boundaries before any token enters the context |
| PII handling | Payment-related queries contain card data, account numbers, transaction IDs — LLM pipelines must strip or mask PII before inference |
| Model version pinning | Enterprise SLAs require reproducible outputs — Stripe pins model versions so behavior doesn't drift when the provider updates |

**Why this matters for B2B PMs:**

⚠️ Enterprise contracts with LLM features require security review before signing. The questions: "Where does inference happen?", "Who can see the prompts?", "What's logged, and for how long?" are not engineering concerns — they're deal blockers. A B2B PM who can't answer these loses enterprise deals to competitors who can.

**The audit log requirement in practice:**

> **Compliance-ready logging:** Most LLM APIs don't provide audit-ready logs by default. Stripe's engineering team built a middleware layer that captures: request ID, tenant ID, model ID + version, token counts (input/output), latency, and a SHA-256 hash of the prompt and response. This log is immutable, retained for 7 years per financial compliance requirements, and queryable by compliance teams without exposing raw prompt content.

**Multi-tenancy isolation patterns for B2B SaaS with LLMs:**

| Pattern | How it works | When to use |
|---|---|---|
| Context-level isolation | Each tenant's documents are retrieved and injected into context only for that tenant's requests | Most B2B SaaS — simplest, achieves isolation without separate infrastructure |
| Namespace-level isolation | Each tenant has a dedicated vector store namespace; retrieval is scoped by namespace at query time | When tenants have large, distinct knowledge bases (e.g., different product catalogs) |
| Inference-level isolation | Each enterprise tenant gets a dedicated model endpoint | Regulated industries (financial services, healthcare) with strict data separation requirements |

**Takeaway:** Enterprise LLM products require a compliance-first architecture review before they ship. The technical capability is table stakes. The questions that win or lose deals are: data residency, audit trails, PII handling, tenant isolation, and model version control. A PM building for enterprise needs to design these requirements into the system from day one — retrofitting compliance architecture is 3× more expensive than building it in.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands token economics, context window, grounding, temperature, training vs. inference.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Grounding failure — the confident wrong answer

**The pattern:**
A knowledge base is built for an AI feature. The knowledge base is complete at launch. Six months later, prices change, courses are added, policies are updated. Nobody updates the knowledge base. The chatbot confidently cites outdated pricing. A parent books a trial expecting a price that no longer applies. Support ticket. Trust damage.

**Why it compounds:** 
LLM outputs don't degrade gradually. A chatbot with a stale knowledge base is indistinguishable from a correct one until someone hits an outdated fact — at which point the entire product's trustworthiness is questioned.

**PM prevention role:**

| Prevention mechanism | Action |
|---|---|
| Knowledge base ownership | Assign a living product owner; treat as code, not static files |
| Deployment requirement | Add KB update as definition of done for every pricing change, policy update, product change |
| Analytics monitoring | Flag "hallucination signals": unusual escalation spikes, low-confidence outputs, clustered negative feedback by topic |

---

### Prompt drift — the behavior that changed with no deploy

**The pattern:**
The system prompt is updated to "improve tone." The model behaves slightly differently. Nobody notices until a week later when conversion in the chatbot drops 8%. The A/B test infrastructure for the chatbot was never built. There's no clear rollback. There's no record of what the old prompt said.

**Why it happens:** 
Teams treat prompts as configuration rather than code. They're edited directly in a dashboard with no version control, no review process, and no change log.

**PM prevention role:**

| Prevention mechanism | Action |
|---|---|
| Version control | Treat prompts as code; require code review for every change |
| Deployment strategy | Use feature flags for significant prompt changes |
| Validation requirement | A/B test new prompt against old before full rollout |

⚠️ **Risk:** A prompt that has never been A/B tested has never been validated — it's shipped on vibes.

---

### Context overflow — the system prompt that disappeared

**The pattern:**
A chatbot starts with a tight 800-token system prompt. Over months, engineers add exception handling, edge case instructions, persona details, and knowledge base content directly into the system prompt. The prompt grows to 12,000 tokens. Long conversations approach the 128K limit. When the context window fills, the model silently truncates the beginning — which is the system prompt. The bot loses its persona, ignores its constraints, and behaves unpredictably.

**Why it's hard to detect:** 
The failure mode is silent. The model doesn't throw an error — it just ignores the instructions that no longer fit. The degradation is gradual as conversations get longer.

**PM prevention role:**

| Prevention mechanism | Rationale |
|---|---|
| Monitor context utilization | Track as operational metric, not just cost metric |
| System prompt size governance | Every instruction added = tradeoff against context headroom for conversation history and retrieved documents |
| Alert threshold | Flag sessions exceeding 80% context window utilization for human review |

⚠️ **Risk:** Silent failure mode. No errors thrown — model simply ignores instructions that no longer fit in available context.

## S2. How this connects to the bigger system

| System | Role | Key Connection |
|---|---|---|
| **Prompt Engineering (04.02)** | Controls model behavior | Tokens and temperature are the foundation for every prompt design decision |
| **RAG (04.03)** | Grounding mechanism | Context window constraints make RAG necessary — you can't fit all knowledge in a single prompt |
| **AI Evals (04.06)** | Quality measurement | Hallucination prevention requires an eval pipeline to measure accuracy (e.g., PQS's 91% figure) |
| **AI Cost & Latency (04.10)** | Token economics | Cost and latency decisions map directly to token counts and model tier selection |
| **Feature Flags (03.10)** | Prompt deployment safety | Prompt changes need staged rollout and rollback like code changes do |

### The PM's expanding role in AI systems

**In traditional software:** PMs define requirements → engineers implement them → code determines behavior.

**In LLM-based systems:** Behavior is determined by multiple factors working together:

- Foundation model (PM/engineering choice)
- System prompt (written by PM, engineers, or AI team)
- Knowledge base (curated by PM or content team)
- Temperature and inference parameters (set by engineering)
- Grounding documents per call (determined by retrieval architecture)

> **The implication:** PMs are direct contributors to AI system quality—not just requirement-setters. A poor system prompt ships a poor product. An unmaintained knowledge base ships a product that confidently lies to customers.

⚠️ **This is a new PM responsibility with no analogue in traditional software development. The stakes are higher: your decisions directly affect model behavior and customer experience.**

## S3. What senior PMs debate

### The reliability question: can LLMs be trusted in production?

| Position | Argument | Example |
|----------|----------|---------|
| **"Yes, with guardrails"** | Production systems prove reliability at scale with measurable outcomes | PQS: 91% accuracy; TrialBuddy: resolves majority of support queries without escalation |
| **"Failure modes unacceptable"** | Error rates unacceptable by human standards; at scale = thousands of errors monthly | PQS 9% error rate = ~1 in 10 parents receives incorrectly tagged report; at 70% coverage = thousands/month |

**The resolution:** 

> **Comparison class:** Evaluate LLM reliability against the process being *replaced*, not against a perfect human standard.

Before PQS, quality evaluation was manual, inconsistent, and reached 20% of classes. The comparison:
- **91% accuracy at 70% coverage** (LLM) vs. 
- **80% accurate at 20% coverage** (human baseline)

LLM reliability is a *product decision* about acceptable outcomes relative to the alternative.

---

### The commoditization question: does model choice still matter?

**Context:** By late 2024, GPT-4-level capability available at 1/10th the cost. Capability gap between frontier and mid-tier models compressing.

| Position | Case | Trade-off |
|----------|------|-----------|
| **Switch to cheaper models** | GPT-4o-mini: 88% accuracy vs. GPT-4o: 91% at 1/15th cost on PQS eval | 3% quality delta may justify $X thousand/month savings |
| **Stay with current model** | Model switching requires re-tuning prompts, re-evaluating behavior, re-QA | Switching costs often exceed short-term savings; "just as good" fails on edge cases |

**Emerging best practice: Multi-provider routing**

Route requests by complexity, not by product:
- **Simple, high-volume** → Haiku
- **Complex, high-stakes evaluation** → Sonnet or Opus

> **Model selection:** Becomes a per-request decision, not a per-product decision.

---

### The autonomy question: how much should the LLM decide?

**Current guardrails:**
- TrialBuddy: escalates to human after 3 failed interactions
- PQS: requires evidence quotes with all outputs

> **Autonomy expansion risk:** Each guardrail removal expands the blast radius of failure.

**Action type determines autonomy threshold:**

| Action Type | Failure Cost | Appropriate Autonomy |
|-------------|--------------|----------------------|
| Read-only (chatting, summarizing, scoring) | Low | Higher autonomy acceptable |
| Write actions (booking, cancelling, charging) | High | Requires human oversight |

**PM judgment call:**

Autonomy expansion should be proportional to:
1. **Eval pipeline maturity** — How well can you detect failures?
2. **Action reversibility** — Can the error be undone?

A wrong API call is not the same as wrong advice.