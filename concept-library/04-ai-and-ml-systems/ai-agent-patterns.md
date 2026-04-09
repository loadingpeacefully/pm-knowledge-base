---
lesson: AI Agent Patterns
module: 04 — AI & ML Systems
tags: tech
difficulty: working
prereqs:
  - 04.01 — How LLMs Work: Agents use LLMs as their reasoning core — understanding token prediction and context windows is required before understanding how agents plan and act
  - 04.02 — Prompt Engineering Basics: Agent behavior is defined by system prompts — the same prompt engineering principles govern agent scope, persona, and guardrails
  - 04.06 — AI Evals & Quality Scoring: Agents are harder to eval than static LLMs — multi-step failures compound; understanding evals is a prerequisite for understanding agentic quality assurance
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/trialbuddy-ai-powered-chatbot.md
  - technical-architecture/student-lifecycle/welcome-call-through-ai-calling.md
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

## F1. The difference between answering a question and doing a job

### The Evolution: Chatbot → Agent

| Interaction | Chatbot | Agent |
|---|---|---|
| **Pattern** | User asks → AI responds with text | User sets goal → AI takes actions |
| **User role** | Does all the work | Defines the objective |
| **AI role** | Answers questions, generates text | Executes tasks across multiple steps |
| **Example** | "What's the capital of France?" → "Paris" (user copies/pastes) | "Reschedule my meeting" → AI rebooks the meeting |

---

### What Changed in 2023

**Traditional chatbot workflow:**
- You type a message
- AI responds with text
- You copy and paste
- You do the rest

**New agent workflow:**
- AI calls APIs to check flight status
- AI writes and executes code
- AI searches the web
- AI fills forms
- AI sends emails on your behalf
- AI completes the full task

---

> **Agent:** An AI system that takes actions in the world — not just generates text. It can use tools, interact with other systems, make decisions across multiple steps, and complete tasks that require more than one action to finish.

The key difference: **agency**. The human defines the goal. The agent figures out the steps.

---

### Why This Matters (2024–2026)

This shift from chatbot to agent is one of the most significant changes in how software products are being built. Every major AI platform is racing to build agents. Every product team working with AI needs to understand:
- What agents can do
- Where they fail
- How to design for them

## F2. What it is — definition and analogy

> **AI Agent:** An AI system that can perceive its environment, reason about what to do, take actions using tools, observe the results, and repeat — until it completes a goal or reaches a point where it needs human input.

### The Core Difference: Feedback Loop

The defining property of an agent is the **feedback loop**:

observe → reason → act → observe again

A chatbot generates text once and stops. An agent keeps going until the job is done.

### The Analogy: Consultant vs. Employee

| Consultant | New Employee |
|---|---|
| Gives you a report | Joins your team with a goal |
| Answers questions, produces document | Asks clarifying questions |
| Hands it to you and is done | Takes actions: accesses CRM, drafts emails, schedules calls, updates tracking |
| One interaction | Iterates until goal is complete or needs escalation |

**Takeaway:** The consultant is a chatbot. The new employee is an agent. The difference isn't intelligence — it's autonomy and the ability to use tools to take action.

### Three Things That Make Something an Agent

1. **Tools** — the agent can call external systems (APIs, databases, search engines, other AI models)
2. **Multi-step reasoning** — the agent can plan a sequence of actions to complete a goal, not just respond once
3. **Feedback loop** — the agent observes the result of each action and adjusts its next step accordingly

## F3. When you'll encounter this as a PM

| **Scenario** | **What's Happening** | **Why It Matters** |
|---|---|---|
| Team proposes "automating" a multi-step process with AI | Process involves: access system → make decision → take action → respond to result | You're designing an agent, whether labeled as such or not |
| Chatbot needs to "do things," not just "say things" | Chatbot answers questions (passive) vs. Agent accesses systems, processes requests, sends confirmations, updates records (active) | Tool access = you've crossed from chatbot to agent |
| AI-powered customer support, sales automation, or onboarding | Workflows span multiple steps across multiple systems | Multi-system + tool access = agent architecture required |
| "AI features" that sound simple but hide complexity | Example: "Handle rescheduling" requires: check availability → check preferences → propose options → confirm → update calendar → notify parties → handle failures | Scoping agents requires surfacing hidden sequential steps |
| AI feature fails in unexpected ways | Chatbot gives wrong answer (information failure) vs. Agent takes wrong action (operational failure) | Agent failures are more consequential; PM owns guardrail design |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation (or existing PM context)
# ═══════════════════════════════════

## W1. How AI agents actually work

### The agentic loop

Every AI agent — regardless of complexity — operates on a loop:

```
1. OBSERVE   — receive input (user message, tool result, system event)
2. REASON    — use the LLM to decide what to do next
3. ACT       — call a tool, generate a response, or do both
4. OBSERVE   — receive the result of the action
5. REPEAT    — until the goal is achieved or a stopping condition is met
```

**What distinguishes an agent from a single LLM call:**
- **Chatbot:** One cycle of steps 1–3, then stops
- **Agent:** Loops dozens of times to complete complex tasks

### Tools — the agent's hands

> **Tool:** A function the agent can call to interact with an external system. The LLM decides when to call a tool, what arguments to pass, and what to do with the result.

An agent without tools is just a chatbot with delusions of agency. Tools are what allow an agent to actually affect the world.

| Tool type | What it does | Example |
|---|---|---|
| **Search** | Query a knowledge base or the web | Find the parent's booking details |
| **API call** | Interact with an external service | Fetch available slots from the scheduling API |
| **Database read/write** | Query or update a data store | Update the lead's qualification score in the CRM |
| **Code execution** | Run code and return the result | Calculate the amortization schedule for this loan |
| **Send message** | Send an email, SMS, or notification | Confirm the appointment and send a WhatsApp message |
| **Call another AI** | Route to a specialized model | Pass this legal document to the contract analysis agent |

**PM's role with tools:**
Define which tools the agent can access, what each tool is allowed to do, and under what conditions it should be used. Tool scope is a product decision — the agent's capabilities and risks are defined by the tools you give it.

### The system prompt — the agent's job description

The system prompt is the PM's primary control surface for agent behavior.

| Dimension | What it controls | PM decision |
|---|---|---|
| **Persona** | How the agent presents itself — name, voice, tone, warmth level | Sets user trust and brand consistency; wrong persona creates cognitive dissonance |
| **Scope** | What topics the agent may address and what actions it may take | Prevents scope creep; every topic or action NOT listed here requires explicit addition |
| **Grounding** | Which sources of truth the agent must use, and whether it may use its own training knowledge | Without this, the agent will invent answers; with it, the agent stays factual but limited |
| **Escalation criteria** | The exact conditions that force a handoff to a human | Too narrow = agent fails silently; too broad = agent escalates everything, defeating automation |
| **Knowledge base** | The documents or data the agent can retrieve from | Determines the factual boundary of what the agent knows — content quality directly determines answer quality |

**Key insight:** A well-designed system prompt is the difference between an agent that stays on-task and one that hallucinates, goes off-script, or takes unauthorized actions.

### Company — BrightChamps (Niki TrialBuddy)

**What:** An AI agent that books demo sessions with a constrained system prompt across five dimensions

**Why:** 
- **Persona** (friendly, knowledgeable BrightChamps rep) → controls tone and trust
- **Scope** (demo booking only — not pricing, curriculum, or post-enrollment) → prevents scope creep
- **Grounding** (knowledge base only — not general LLM knowledge) → prevents hallucinations
- **Escalation** (trigger handoff if: out of scope, negative sentiment, or 2+ unresolved clarifications) → balances automation with safety
- **Knowledge base** (curated FAQ covering demo logistics only) → bounds the factual boundary

**Takeaway:** Each dimension of the system prompt is a distinct PM control lever. The system prompt itself defines the agent's capabilities and constraints.

## W2. The decisions this forces

### Decision 1: What pattern fits your use case?

Agents aren't one thing — there are several distinct patterns, each suited to different use cases.

| Pattern | How it works | Best for | Watch out for |
|---|---|---|---|
| **Single agent + tools** | One LLM with access to multiple tools. Plans and executes sequentially. | Customer support bots, onboarding assistants, scheduling agents | Context window limits — long tasks can exceed what the agent can hold in memory |
| **Multi-agent orchestration** | A "manager" agent breaks a task into subtasks and delegates to specialized sub-agents | Complex workflows requiring specialization (research + writing + verification) | Coordination overhead; failures in sub-agents can cascade to the manager |
| **Human-in-the-loop** | Agent executes steps autonomously, but certain actions require human approval before proceeding | High-stakes actions (payments, account changes, legal documents) | Adds friction; defeats the purpose of automation if the human approves everything |
| **Agentic pipeline (no LLM loop)** | Fixed sequence of LLM calls and tool calls, no dynamic replanning | Predictable structured workflows (extract → validate → transform → write) | Less flexible than a true agent; breaks on unexpected inputs |

**PM recommendation:** Start with the simplest pattern. A single agent with tools solves most use cases. Multi-agent adds coordination complexity that creates new failure modes. Default to human-in-the-loop for any action that is difficult or impossible to reverse.

---

### Decision 2: What actions are reversible — and what guardrails do irreversible actions need?

⚠️ **This is the most important architectural PM decision in agentic product design.**

> **Reversible action:** The agent sends a draft email → PM can review before sending. Cost of error: low.

> **Irreversible action:** The agent sends the email. Cost of error: potentially very high.

**The autonomy dial for each action type:**

| Action reversibility | Agent autonomy level | Guardrail design |
|---|---|---|
| **Fully reversible** (read-only, drafts, previews) | Full autonomy — no human confirmation needed | Log all actions; allow easy undo |
| **Partially reversible** (bookings, account updates) | Confirm-before-execute — agent proposes, human approves | Approval step with clear action summary before execution |
| **Irreversible** (payments, sent emails, deletions) | Always human-in-the-loop or double-confirmation | Hard gate — never auto-execute without explicit approval |

**Rule of thumb:** If you'd be embarrassed if the agent took the action without asking, add a confirmation gate.

### Company — BrightChamps, Niki voice agent (AI calling)

**What:** The AI reschedules demo bookings in real time during calls with verbal confirmation.

**Why:** Partially reversible action (a rescheduled booking can be changed again, but requires additional effort). The AI must verbally confirm the new slot and wait for the parent to say "yes" before calling the Prashashak Reschedule API.

**Takeaway:** The confirmation step is the human-in-the-loop gate built into the conversational flow itself.

---

### Decision 3: What are the escalation criteria — and what happens when the agent can't handle something?

Every agent needs a clearly defined escalation path. The agent's job is to handle what it can handle. The escalation path's job is to handle everything else gracefully.

**Well-designed escalation triggers:**

| Trigger | What it means | PM action |
|---|---|---|
| **Query outside scope** | User asks something the agent isn't designed to answer | Agent says "let me connect you with a specialist" and hands off with context |
| **Negative sentiment detected** | User is frustrated, upset, or aggressive | Auto-escalate to human — do not let the agent continue in this state |
| **Confidence below threshold** | Agent is uncertain about an answer or action | Prompt for clarification or escalate rather than hallucinate |
| **Action requires data the agent doesn't have** | Agent can't complete the task with available tools | Ask for what's needed or escalate if the information can't be obtained |
| **Maximum turn limit reached** | After N turns without resolution, the problem is intractable | Escalate with full conversation context |

### Company — BrightChamps, Niki AI calling escalation

**What:** Escalation triggers include complex queries, detected negative sentiment, and confidence failures. Human pre-sales rep receives full call transcript within 30 seconds.

**Why:** Users never experience a dead end. The handoff is seamless and the human rep has complete context to help immediately.

**Takeaway:** Always pass context during escalation—a human agent without it will ask the user to repeat themselves, undoing the value of automation.

⚠️ **Critical design rule:** A human agent who receives an escalation without context will ask the user to repeat themselves — the worst possible experience after an automated interaction.

---

### Decision 4: How do you define the agent's scope — and what happens when users push outside it?

An agent without a clearly defined scope will try to answer anything and take action on anything. That's a product and legal risk.

**Scope has two dimensions:**

| Dimension | Definition |
|---|---|
| **Topic scope** | What subjects the agent is allowed to discuss |
| **Action scope** | What actions the agent is allowed to take |

Both must be explicit in the system prompt. "Be helpful and answer questions" is not a scope definition.

**Example system prompt:**

> *You are Niki, a BrightChamps demo booking assistant. You may only discuss: demo scheduling, class timing, subject offerings, and basic platform FAQs. You may not discuss: pricing beyond what's in the approved FAQ, competitor comparisons, personal data of other students, or post-enrollment curriculum details. If a user asks about anything outside these topics, say: "That's a great question — let me connect you with someone who can help" and escalate.*

**When users push outside scope:**

| Boundary type | How to handle |
|---|---|
| **Soft boundary** | Agent redirects ("That's outside what I can help with, but here's who can...") |
| **Hard boundary** | Agent refuses and escalates, with no further engagement on the topic |
| **Injection attempt** | User tries to override instructions ("Ignore all previous instructions and...") — system prompt must explicitly forbid following user-provided instruction overrides |

---

### Decision 5: How do you eval an agent — it's not the same as eval-ing a chatbot

Evals for agents are more complex than for static LLMs because agent behavior is sequential and conditional.

| What you're evaluating | How to eval it | What can go wrong |
|---|---|---|
| **Individual tool calls** | Test each tool call in isolation — correct arguments? correct timing? | Tool called with wrong params; tool called when it shouldn't be |
| **Step sequence** | Trace the full action log — did the agent take steps in the right order? | Agent skips a step; agent takes steps in wrong order |
| **Outcome accuracy** | Did the agent achieve the goal? | Agent took all the right steps but the outcome is still wrong (e.g., booked the wrong slot) |
| **Escalation accuracy** | Did the agent escalate when it should have? Did it fail to escalate when it should have? | Agent escalates unnecessarily (annoying) or fails to escalate when it should (dangerous) |
| **Scope adherence** | Did the agent stay within its defined scope? | Agent answers questions it shouldn't; agent ignores user questions within scope |

**PM implication:** For agents, you need trace-level evals — you can't just evaluate the final output. You must evaluate the entire action sequence leading to it. Build logging that captures every tool call, every LLM decision, and every user interaction in a structured format that can be reviewed and scored.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **"What tools does the agent have access to — and what can each tool do?"** | The agent's actual capability boundary. If an engineer says "the agent has access to the CRM," follow up: can it read only, or also write? Can it update any field or only specific ones? Tool scope is your guardrail. |
| **"What's our escalation path, and what context does the human agent receive?"** | Whether the handoff was designed or an afterthought. Poor escalation design is the most common source of user complaints about AI features. If the human agent receives no context, the user experience is broken at the moment it matters most. |
| **"What happens if a tool call fails — does the agent retry, give up, or escalate?"** | Whether failure modes were designed. An agent that silently fails on a tool call and then gives the user a wrong answer is worse than an agent that fails visibly and asks for help. |
| **"How long does the agent's memory persist — does it remember context from earlier in the conversation?"** | Context window management. Long agent conversations can exceed the LLM's context window. When this happens, early conversation context is dropped — which can cause the agent to "forget" the user's original goal and take conflicting actions. |
| **"What does a trace log for a complete agent interaction look like — can I see a real example?"** | Whether the team has observability for agent behavior. Without trace logs, debugging agent failures is guesswork. You should be able to replay any agent interaction step-by-step. |
| ⚠️ **"How do we prevent prompt injection — what happens if a user tries to override the agent's instructions?"** | Whether the system prompt has been hardened against adversarial inputs. Prompt injection (getting an agent to ignore its instructions by embedding instructions in user input) is the most common security vulnerability in agentic systems. |
| **"What's our test suite for agent behavior — how do we know it works before we ship?"** | Whether the team has built agent-specific evals (trace-level testing, not just output testing) and whether they've covered the escalation triggers and edge cases in the test plan. |

## W4. Real product examples

### BrightChamps — Niki AI voice agent (outbound welcome calls)

Niki is an AI voice agent that calls parents immediately after they book a demo class. The interaction is fully automated and covers: welcome and demo confirmation, slot pitch (same-day or next-day upgrade), lead qualification, FAQ handling, and real-time rescheduling if requested.

**Pattern:** Single agent + tools (Retell AI voice platform, Prashashak Reschedule API, Zoho CRM write), with human-in-the-loop escalation.

#### Tools & Integrations

| Tool | Purpose |
|------|---------|
| Prashashak Reschedule API | Fetch available slots, confirm new booking in real time |
| Zoho CRM write | Update call outcome, transcript, qualification data, UTM attribution |

#### Scope Definition

| Category | Details |
|----------|---------|
| **In scope** | Demo confirmation, slot upgrade pitch, qualification questions, FAQ (pricing, structure), reschedule |
| **Out of scope** | Post-enrollment support, curriculum details, competitor comparisons |
| **Escalation triggers** | Complex query, negative sentiment, AI confidence failure |

> **Human-in-the-loop gate:** The AI must receive explicit verbal "yes" from the parent before calling the Reschedule API. This prevents accidental booking changes.

⚠️ **Exclusion rules as guardrails:** The agent does not call if:
- Lead has already been rescheduled
- Lead was generated by an AI calling campaign (loop prevention)
- CRM already shows a human rep made contact

*These exclusions prevent the agent from taking actions it shouldn't.*

#### Metrics & Operational Benchmarks

| Metric | Target |
|--------|--------|
| Demo Joining % | 25% → 30% |
| Demo Completion % | 80% → 85% |
| Call triggered | Within 60 seconds of form submission |
| Reschedule API response | Under 3 seconds (conversational flow) |
| Human escalation notification | Within 30 seconds of trigger |
| CRM update | Within 60 seconds of call end |
| Max retry attempts | 5 per lead → human queue |

**Why the metrics matter for PM:** The 5% joining improvement (25%→30%) is the business case for the agent. If AI escalation rate climbs above ~15%, the automation is not delivering — too many conversations require human intervention, meaning the scope or script design is failing. Tracking escalation rate separately from conversion rate is essential: a high conversion rate with a high escalation rate means humans are driving the conversion, not the agent.

---

### BrightChamps — TrialBuddy (Niki chatbot)

The TrialBuddy chatbot uses the same Niki persona in a text-based interface. The system prompt defines constrained agentic behavior: a knowledge-base-grounded assistant that handles demo logistics questions and escalates anything outside scope.

**Pattern:** Single agent with knowledge base tool (document retrieval), no write actions — read-only.

> **Key design decision — why no write access:** The chatbot version of Niki has no CRM write access and no scheduling API access. This is a deliberate scope constraint: the chatbot is for answering questions only. Any action (booking, rescheduling, escalation) goes to a human. The voice agent (above) has broader tool access because it operates in a supervised, recorded context with clearer confirmation checkpoints.

*What this reveals:* Tool access decisions should vary by channel and context. The same underlying AI persona can have different capability sets depending on where and how it operates — text chat gets read-only, voice call gets read-write with confirmation gates.

---

### Anthropic Claude — computer use (autonomous browser agent)

In October 2024, Anthropic released Claude's computer use API — an agent pattern where the LLM can observe a computer screen (via screenshots), reason about what to do, and take actions (click, type, scroll) to complete tasks on a web browser or desktop application.

This is the most expansive tool set in a commercial agent: the tool is literally "any UI on a computer." The agent can fill in forms, navigate websites, extract data, and interact with any software that has a visual interface.

#### What this means for PM

⚠️ The action scope is nearly unlimited — which makes guardrail design more critical, not less

- Human-in-the-loop is strongly recommended for any irreversible action (form submissions, purchases, account changes)
- The audit log must capture screenshots, not just text — visual trace logging is required for this pattern
- Use cases are strongest where there is no API available (legacy systems, third-party websites without integrations)

---

### Cursor / GitHub Copilot — agentic code assistants

Modern AI coding tools have moved well beyond autocomplete. Cursor's "Agent mode" can: read the entire codebase, write code across multiple files, run the code, read the error output, fix the error, and repeat — until the feature is built or the tests pass.

**Pattern:** Single agent with multiple tools (file read/write, terminal execution, test runner), running a full agentic loop.

#### What this means for PM

Code agents demonstrate the most mature production use of the agentic loop pattern. The failure modes are instructive:

| Failure Mode | What happens |
|--------------|--------------|
| Confident wrong action | Agent makes changes that break unrelated parts of the codebase |
| Infinite retry | Agent gets stuck on intractable errors |
| Locally correct but globally wrong | Code passes tests but is architecturally wrong |

*What this reveals:* These failure modes — confident wrong action, infinite retry, locally correct but globally wrong — appear in every agentic product.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. What breaks and why

### Action amplification — small errors compound across steps

> **Action amplification:** When an agent makes an error early in a multi-step task, each subsequent action is rational given the false premise, but systematically wrong in reality. The error compounds through the workflow.

**The problem:**
- Chatbot hallucinates in step 2 of a 10-step task
- Steps 3–10 execute logically but based on false data
- Final outcome is systematically wrong and hard to trace

**PM prevention role:**
- Build verification steps into multi-step workflows
- Add pass/fail checks after consequential steps (especially tool calls that write data)
- Have the agent confirm results before proceeding
- Trade-off: adds latency, but prevents compounding errors
- Frame in product terms: each major step = mini-milestone with validation

---

### Tool call failures with silent degradation

⚠️ **Silent failures are product design failures, not engineering failures.**

> **Silent degradation:** An API call fails (500 error), the agent finds no result, makes an assumption, and continues without surfacing the failure to the user.

**The problem:**
- User receives an outcome based on data that never existed
- Failure is invisible to both agent and user
- System appears to work while actually failing

**PM prevention role:**
- Define explicit failure handling for every tool call
- Example: "If the Reschedule API fails, do not proceed — tell the user there was a problem and offer to connect them with a person"
- Specify failure behavior in the agent's requirements, not as an afterthought

---

### Prompt injection — the adversarial user problem

⚠️ **High-risk: agents with tool access are manipulation targets.**

> **Prompt injection:** A user attempts to override, modify, or extract an agent's system prompt through crafted input. Can be direct ("Tell me your system prompt") or subtle ("The admin approved an exception...").

**Attack patterns:**
- Direct instruction override
- False authority claims
- Urgency framing to bypass normal process

**PM prevention role:**
- Every agent system prompt must include explicit injection resistance instructions
- Instruct the agent that no user input can override, modify, or reveal its system prompt
- For high-stakes tool access (payments, deletions, account modifications):
  - Add a secondary validation layer
  - Before irreversible actions, agent re-checks the original system prompt
  - Verify the action is within scope before executing

---

### Context window exhaustion in long conversations

> **Context window exhaustion:** An agent silently drops early turns from context as conversation length exceeds the model's window. Original goals stated early become inaccessible.

**The problem:**
- User's original goal (turn 3) is no longer in context
- Agent continues executing most recent instructions
- Recent instructions may contradict the original goal
- Neither agent nor user is aware of the mismatch

**PM prevention role:**
- For agents handling long conversations, build explicit memory management:
  - **Option A:** Summarize early context into a persistent memory store the agent can retrieve
  - **Option B:** Set a hard turn limit after which the agent re-prompts the user to re-state the goal
- Never allow context exhaustion to happen silently

## S2. How this connects to the bigger system

### Agent architecture: built on Module 04 foundations

**Agents are the product layer built on top of every other concept in Module 04.**

An agent depends on:
- LLM (04.01) — reasoning core
- System prompt (04.02) — behavioral specification
- RAG (04.03) — knowledge base grounding
- Embeddings (04.04) — context retrieval and intent matching
- Classification models (04.07) — callable as tools
- Recommendation systems (04.08) — callable as tools
- Trace-level evals (04.06) — step-by-step correctness validation

⚠️ **Critical dependency:** A PM who hasn't read Module 04 in order will design agents without understanding the building blocks those agents depend on.

---

### Multi-agent systems: the frontier (and genuinely hard)

| Aspect | Single Agent | Multi-Agent Network |
|--------|--------------|-------------------|
| **Architecture** | One reasoning loop | Manager agent + specialized agents (researcher, writer, verifier, formatter) |
| **Scaling** | Limited by context window | Decomposition enables unbounded task complexity |
| **Specialization** | Generalist approach | Each agent optimized for its domain |
| **Failure modes** | Isolated hallucination | Coordination failures, inter-agent hallucination, cascading errors |
| **Debugging** | Straightforward | Exponentially complex |

**Status (2025–2026):** The most capable AI systems are not single agents but networks of specialized agents.

> **The PM challenge:** Multi-agent systems represent the hardest class of AI product problems that exist today.

---

### The PM-engineering interface is shifting

In traditional software, the division is clear:
- PM writes requirements
- Engineers build them

In agentic products, the boundary dissolves:
- PM writes the **system prompt** (behavioral spec)
- PM writes the **tool specifications** (interface spec)
- PM writes the **escalation criteria** (failure handling spec)

These are simultaneously requirements *and* implementation.

> **Capability shift:** The PM who can't write a precise system prompt is giving up control over a core part of the product.

This transition is underway at most AI-native companies in 2025–2026.

## S3. What senior PMs debate

### Debate 1: How much autonomy is the right amount?

| Dimension | "AI drafts, human reviews" | "AI executes, human reviews after" |
|-----------|----------------------------|-------------------------------------|
| **Where industry settles** | ✓ Current production standard | Emerging frontier practice |
| **Driver** | Trust + regulatory caution | Automation value proposition |
| **Risk profile** | Lower | Higher |

> **The autonomy spectrum:** ranges from full human review before any action to fully autonomous execution with human review only after the fact.

**Why the gap exists:**
- Not a capability problem — models often make correct decisions without review
- Trust problem — users, businesses, regulators don't yet trust autonomous irreversible actions
- Scale problem — errors compound across thousands of agents

**The emerging resolution — autonomy earned through data:**

Teams at the frontier measure false positive rates by action class:
- Bookings with 99.5% accuracy? → Remove confirmation gate
- Refunds with 92% accuracy? → Keep the gate

Autonomy expansion is **demonstrated**, not assumed.

---

### Debate 2: Who owns the system prompt?

| Owner | Optimizes For | Blind Spots | Current Status |
|-------|---------------|-------------|-----------------|
| **Engineer** | Capability (what model can do) | User journeys, edge cases, brand voice | ✗ Early-stage default |
| **PM** | Behavior spec | Technical feasibility | Emerging standard |
| **Product ops** | Production alignment | Design intent | Emerging standard |

**The three-party ownership model (emerging at AI-native companies):**

- **PM:** behavior specification (what agent should do in each scenario, escalation criteria, scope)
- **AI engineer:** technical prompt implementation (how to express behaviors in prompt form)
- **Product ops / Trust & Safety:** ongoing monitoring and refinement (what's the agent actually doing that diverges from spec?)

⚠️ **Risk:** The PM who says "the system prompt is an engineering artifact" cedes control of core product definition to people who don't own the user experience.

---

### Debate 3: Are agents fundamentally different software risks?

**Traditional software failure modes:**
- Predictable
- Enumerable and testable
- Examples: database errors, form validation failures, API timeouts

**Agent failure modes:**
- **Emergent** — arise from LLM + tools + user input interaction in unanticipated ways
- **Context-dependent** — same agent behaves differently in different conversational contexts
- **Hard to reproduce** — semantically similar questions trigger completely different agent behaviors

⚠️ **The QA gap:** Standard playbook (write tests → run tests → ship) is **insufficient** for agentic products.

**Current industry position (2026):**
The industry does not yet have a mature playbook for agentic QA. Production agents ship with more uncertainty than equivalent-stakes traditional software.

| Responsible PM | Negligent PM |
|---|---|
| Acknowledges novel risk category | Treats agent like deterministic feature |
| Designs conservative guardrails | Skips trace logging |
| Builds robust escalation paths | Deploys without escalation design |
| Implements ongoing monitoring | Ships without monitoring |