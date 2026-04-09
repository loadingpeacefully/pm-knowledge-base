---
lesson: Discovery vs Delivery
module: 05 — product-fundamentals
tags: product
difficulty: working
prereqs:
  - 05.05 — Roadmapping depends on discovery status to determine roadmap placement
  - 05.02 — Jobs to Be Done is the primary discovery lens for understanding user motivation
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/auxo-prediction.md
  - product-prd/pre-demo-engagement-game-v01.md
profiles:
  foundation: aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: senior PM, head of product, ex-engineer PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

Here's a scene that plays out in product teams constantly: the engineering team ships a feature. Users don't adopt it. Post-launch, someone goes back to do user interviews and discovers that users didn't want what was built — they wanted something slightly but fundamentally different. The feature is rearchitected. Or shelved. Six weeks of engineering work, gone.

Why did this happen? The team went straight to building without understanding the problem deeply enough. They were doing what product people call "delivery" — building the solution — before completing "discovery" — understanding the problem.

Now the reverse: a different team has been doing interviews, sketching concepts, running surveys, and mapping user journeys for four months. But nothing has shipped. They keep finding new insights that suggest they should revisit the approach. Meanwhile, the market window is narrowing, competitors are shipping, and the CEO is asking why the team isn't making progress.

Both scenarios describe a failure mode. The first team confuses motion with understanding. The second team confuses understanding with action.

Discovery is the work of understanding what problem to solve and whether your solution hypothesis is valid. Delivery is the work of actually building and shipping that solution. Every product team needs both, and the question of which to do, when, and in what proportion is one of the most important operating decisions a PM makes.

---

## F2 — What it is — definition + analogy

> **Discovery:** The phase where a PM and team figure out whether a problem is real, who has it, how much it matters, and whether a given solution approach is likely to work.
> 
> *Tools: user interviews, prototype testing, data analysis, competitive research, surveys*

> **Delivery:** The phase where the team builds and ships a solution that's already been validated well enough to commit engineering time to.
> 
> *Tools: sprints, user stories, engineering, QA, release management*

### The Restaurant Analogy

**Before Opening (Discovery):**
- Taste your menu
- Test recipes with focus groups
- Learn what the neighborhood wants to eat
- Understand price sensitivity
- Verify kitchen layout supports the menu

*All of this generates understanding before you've committed the full cost.*

**Opening Day Forward (Delivery):**
- Kitchen is staffed
- Space is leased
- Menu is printed
- Serving real customers weekly
- Learning and adjusting *while* paying full rent and payroll

### The Trap

Teams often act like every problem should go straight to delivery—opening the restaurant without testing whether the neighborhood wants the food. Or they stay forever in the discovery kitchen, tasting and adjusting, never serving a single customer.

### The Insight

| Question | Phase | Focus |
|----------|-------|-------|
| Should we build this, and in what form? | Discovery | Learning |
| How do we build this well and get it to users? | Delivery | Execution |

**Conflating them wastes either learning or execution.** Separating them clearly is how product teams work efficiently without building the wrong thing.

## F3 — When you'll encounter this as a PM

| Situation | What's Happening | Your Move |
|-----------|------------------|-----------|
| **Every new feature** | Deciding how much discovery is warranted | Small UI copy = 20 min thinking. New product category = months of research. |
| **Engineering asks "what are we building?"** | You don't have a clear answer | This signals you're not ready for delivery. Proceeding means building on a shaky foundation. |
| **Pressure to ship before understanding** | Stakeholders want progress; visibility matters more than clarity | Protect enough discovery to avoid expensive delivery mistakes. This is your core job. |
| **Shipped feature isn't being used** | Post-mortem shows adoption failure | Discovery was incomplete. Adoption problems are rarely execution issues—they're discovery gaps. |
| **Roadmap item keeps delaying** | Team seems stuck on delivery | Check if this is execution friction *or* a discovery gap masquerading as a delivery problem. |

### The Core Signal

The most common PM dilemma: **Discovery feels slow because nothing visible is shipping.** But discovery prevents the expensive mistakes that happen when you build without understanding the problem.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The dual-track model

The most widely used framework for managing discovery and delivery simultaneously is the dual-track model. Two tracks run in parallel:

| Track | Who does it | Time horizon | Output |
|---|---|---|---|
| **Discovery track** | PM + designer + 1 engineer | 2–4 weeks ahead of delivery | Validated problem + solution hypothesis ready to build |
| **Delivery track** | Engineering + PM + QA | Current sprint | Shipped, working features |

**The key insight:** By the time engineering finishes building this sprint, the PM has already validated what the next sprint's problem and solution should be. Discovery is always running ahead of delivery, feeding it validated work.

> **The anti-pattern:** Discovery happening in parallel with delivery on the same items creates mid-sprint pivots.

**The dependency:** 
- ✅ Delivery can only build things that discovery has prepared
- ✅ Discovery should never be trying to catch up with delivery
- ⚠️ If engineering is waiting for PM to tell them what to build, discovery is behind

---

### How much discovery is enough?

Discovery is not binary — it's a dial. More discovery reduces the risk of building the wrong thing, but delays the learning that only comes from real users using real code.

**Adjust the dial based on these four factors:**

| Factor | Light Discovery | Heavy Discovery |
|---|---|---|
| **Reversibility** | Button label change | New pricing model |
| **Novelty** | Solved before by your team | New user type, market, or technology |
| **Cost of being wrong** | 2-day build | 3-month build |
| **Signal quality** | Strong behavioral data | Single interview mention |

---

### Discovery in practice: BrightChamps pre-demo engagement game

**What:** An interactive game shown to students between booking and attending their demo class.

**Why:** Students arrived "cold" with no platform context. Demo attendance and conversion rates were below target.

**Discovery work included:**
- Identifying the behavioral gap: dead time between booking and demo
- Defining success metrics: 5pp attendance lift, 3pp conversion lift, 70% completion rate
- Validating direction: Would a 3–5 minute game create engagement?
- Answering constraints: Mobile-first, no login required, completable in booking window

**Open questions documented explicitly:**
- What game length maximizes completion without overwhelming?
- Should completion affect the teacher's demo script?

**Takeaway:** Even small features benefit from explicit discovery framing—problem definition, success metrics, constraints, and open questions before engineering begins.

---

### Discovery in practice: Auxo prediction system

**What:** Automated teacher availability prediction system for demo slot scheduling.

**Why:** Need accurate staffing forecasts to prevent class shortfalls without over-staffing.

**Discovery phase questions:**
- How many teachers needed per slot?
- What's the right prediction window?
- What safety buffer prevents shortfalls?
- How much historical data is required?

**Delivery phase solution:**
- Weighted 4-week historical average (recent weeks: 32.5 → 15 for oldest)
- 30% safety buffer on predictions
- Cron-based automation at defined intervals

**Takeaway:** Discovery produced a testable algorithmic hypothesis. Delivery implemented it. The separation matters—jumping to delivery without validating weights means shipping a system with potentially wrong logic already in production, making fixes much costlier than adjustments during discovery.

---

### The four types of discovery

> **Problem discovery:** Does this problem actually exist and does it matter?
> - Methods: User interviews, support ticket analysis, behavioral data, NPS verbatim analysis
> - Output: Problem statement with evidence

> **Solution discovery:** Given the problem, which approach is most likely to work?
> - Methods: Prototype testing, A/B testing, design sprints, concept validation interviews
> - Output: Solution hypothesis with confidence level

> **Technical discovery (spike):** Is this technically feasible as imagined?
> - Methods: Engineering exploration of unknowns before committing
> - Output: Technical approach clarity and rough effort estimate

> **Market discovery:** Is timing right? Problem growing or shrinking? Competitor activity?
> - Methods: Continuous background research
> - Output: Prioritization context

**Not every item needs all four:**
- Problem discovery → almost always needed
- Solution discovery → depends on novelty
- Technical discovery → triggered by engineering unknowns
- Market discovery → useful but often runs continuously

## W2 — The decisions this forces

### Decision 1: How long should discovery run before we commit to delivery?

> **Discovery Readiness:** You're ready for delivery when you can describe the problem specifically, identify the user clearly, describe success metrics precisely, and explain why your solution beats alternatives. If you can't do all four, you're not ready.

| Feature Type | Duration | Discovery Activities | Bandwidth |
|---|---|---|---|
| New feature | 1–2 weeks | 5–10 interviews, behavioral data review, one design sprint | Minimal PM overhead |
| New product category | 4–8 weeks | Extended user research, competitive analysis, multiple design iterations | High PM + design investment |

**Recommendation:** Set a "discovery exit criteria" before starting—what specific questions need answers before moving to delivery?

---

### Decision 2: When should discovery and delivery run in parallel vs. sequentially?

| Approach | Timeline | Best For | Trade-off |
|---|---|---|---|
| **Sequential** | Discovery → Delivery | High-stakes, high-cost, hard-to-reverse features | Reduces risk; slower time-to-delivery |
| **Parallel (Dual-track)** | Discovery & Delivery on different items (discovery 2–4 sprints ahead) | Mature product teams with sufficient PM bandwidth | Faster; requires discipline |

⚠️ **Failure Mode:** Discovery and delivery run on the *same item* in the same sprint. PM is still figuring out the problem while engineering builds the solution. Results: mid-sprint pivots and wasted work.

**Recommendation:** Default to parallel tracks. Discovery must be at least one sprint ahead of delivery commitment. Never combine discovery and delivery on the same item *unless* you've explicitly chosen "build to learn."

---

### Decision 3: What do you do with discovery that contradicts a delivery commitment?

You've committed to delivery, engineering has started, and new discovery evidence suggests the wrong direction. Choose one:

| Option | When to Use | Outcome |
|---|---|---|
| Continue delivery as planned | Late in sprint (e.g., day 12 of 14) | Deliver committed feature; apply insights next sprint |
| Pause delivery, address gap, restart | Early discovery contradiction; high mistake cost | Course correction; lost sprint |
| Adjust scope without stopping | Mid-sprint; partial misalignment | Balanced iteration; some rework |

⚠️ **Critical Risk:** Ignoring discovery evidence because "we already started" is how teams ship features they already know are wrong.

**Recommendation:** Timing matters. Day 1 of sprint → stop and fix. Day 12 of 14-day sprint → finish, iterate next sprint.

---

### Decision 4: Who owns discovery?

> **Discovery Ownership Model:** Joint PM + Design leadership, with Engineering consulting. Each role owns a distinct question.

| Role | Owns This Question | Responsibilities |
|---|---|---|
| **PM** | Is this the right problem? Does this solution direction make sense? | Problem framing, business context, validation |
| **Design** | What does the right solution look and feel like for the user? | User research execution, solution concepts |
| **Engineering** | Is this technically feasible and at what cost? | Technical assumption validation, effort estimation |

**Recommendation:** All three must participate in discovery. None can do it alone.

---

### Decision 5: When is "build to learn" better than extended discovery?

> **Build to Learn:** A small, quick, reversible delivery built for discovery purposes—not to ship a polished feature.

**Use when:**
- The question can *only* be answered by real behavioral data (not surveys or interviews)
- The build is small and reversible (feature flag, beta, limited rollout)
- Alternative discovery methods have been tried without resolution

**Don't use as:**
- An excuse to skip discovery entirely
- A shortcut for questions answerable through interviews or existing data

**Recommendation:** Before choosing build to learn, ask:
- Could we answer this in a week of interviews?
- Could we answer it with existing data?

If **yes** to either → do that first. Build to learn is appropriate only when the question is genuinely unanswerable without real user behavior data.

## W3 — Questions to ask your engineer

| Question | What this reveals |
|----------|------------------|
| **"What would you want to know before we start building this?"** | Technical unknowns you haven't considered. Engineers often see structural problems in a solution approach that PMs miss — dependency issues, performance risks, architectural conflicts. Their discovery concerns are often different from yours and equally important. |
| **"Is there a quick prototype or spike we could build to resolve the biggest technical unknown?"** | Whether a small technical discovery investment can significantly reduce delivery risk. A 2-day spike that answers "can we actually do real-time matching with the existing infrastructure?" is often worth 2 weeks of false starts in delivery. |
| **"What happens if we're wrong about [core assumption] after we've built this?"** | The reversibility and cost of your largest assumption. If being wrong means rearchitecting, you need stronger discovery. If being wrong means tweaking an algorithm, you can carry more uncertainty. |
| **"Have we solved anything like this before? What did we learn?"** | Whether there's institutional knowledge that should inform discovery. Previous feature patterns, database behavior, performance precedents — if engineering has done this before, that's de facto discovery that already exists. |
| **"Is there any technical spike work you'd want to do before sprint commitment?"** | Whether engineering is comfortable with the delivery scoping. A "yes" here is an important signal — it means there are open technical questions that should be answered before the team starts the clock on the sprint. |
| **"What's the minimum build that would tell us whether this solution actually works for users?"** | The boundary between build-to-learn and full delivery. Engineers often have sharp intuitions about what's "enough" to validate versus what's "done" for production. |

## W4 — Real product examples

### BrightChamps — Pre-demo engagement game: discovery ahead of delivery

**What:** Built an interactive game to engage cold-start students before live demos, running discovery work in parallel with engineering delivery.

**Why:** Student attendance was dropping and conversion suffered because they arrived unprepared. Rather than block delivery on all unknowns, the team separated what was known from what was still being explored.

**Discovery outputs (locked before coding):**
- Problem statement: cold arrival → low attendance → low conversion
- Success metrics: 5pp attendance increase, 70% game completion
- Hard constraints: mobile-first, no login required, pre-demo window completion

**Open questions (explored in parallel):**
- What game length maximizes completion without overwhelming?

**Takeaway:** Engineering unblocked immediately on game shell and tokenized access while discovery continued. Deliverables weren't held hostage to unknowns; open questions were surfaced and tracked separately.

---

### BrightChamps — Auxo prediction: technical discovery as a prerequisite

**What:** Built a weighted prediction algorithm for teacher joining behavior by making technical discovery the prerequisite for delivery specification.

**Why:** The weighting model couldn't be specified without first answering: *How much historical data is needed for accuracy? How do you balance recency against volume?*

**Discovery phase output:**
- Analysis of 4+ weeks of demo booking and joining data
- Finding: recency matters more than naive averages suggest

**Delivery phase output:**
- Weighted 4-week average: 32.5/30/22.5/15 (most recent week weighted heaviest)
- 30% safety buffer calibrated to observed variance in teacher behavior

**Takeaway:** Skipping technical discovery would have shipped a worse model (equal weights across 4 weeks). The buffer wasn't arbitrary; it was discovery-derived and tied to real data variance.

---

### Intercom — Discovery and delivery as explicitly separate roles

**What:** Created a dual-track accountability system where PMs owned both discovery ("product thinking") and delivery ("product execution") but were measured separately.

**Measurement shift:**
| Traditional | Intercom's Model |
|---|---|
| PM success = features shipped | PM success = *quality* of discovery *and* execution |
| Discovery = overhead cost | Discovery output = value generated |
| Deciding not to build = failure | Deciding not to build = win |

**Cultural implication:**
Teams that discovered an item *shouldn't* be built were celebrated for saving engineering time—not punished for "not shipping."

**Takeaway:** Organizations sustain healthy discovery discipline only when discovery output is credited as value, not treated as pre-work friction.

---

### Airbnb — Discovery preventing delivery of the wrong thing

**What:** Validated a professional photography hypothesis with a small, deliberate experiment before investing in platform scale.

**The discovery experiment:**
- Airbnb sent photographers to a handful of NYC listings at its own expense
- Measured booking lift on photographed listings vs. control
- Result: significant increase in bookings

**Why this mattered:**
Without this validation, Airbnb would have built a full photography service and operations pipeline before confirming it would work.

**Takeaway:** Cheap discovery (photographers + small experiment) de-risked expensive delivery (platform-scale photography program). The sequence reversed what "normal" shipping pressure would have demanded.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### Discovery becomes a delay tactic, not a learning method

**The problem:** Discovery is used to delay decisions rather than improve them—one more interview, another survey, waiting for more data—not because questions are genuinely unresolved, but because committing is uncomfortable.

**The tell:** Discovery output that doesn't change what gets built.

**The fix:** Pre-define what would change your delivery plan *before* starting discovery. If no reasonable discovery outcome would shift the plan, you're ready to ship—you don't need more discovery.

---

### Delivery pressure systematically outcompetes discovery

| Dimension | Discovery | Delivery |
|-----------|-----------|----------|
| Visibility | Invisible | Highly visible |
| Speed | Slow | Fast |
| Measurement | Hard to track | Clear metrics (velocity, dates, shipped features) |
| Leadership question | "What did you learn?" | "What did you ship?" |
| Organizational incentive | Often deprioritized | Always prioritized |

**The result:** Teams ship fast and learn slowly—high output, low signal.

**The fix:** Make discovery measurable—track validated problems documented, assumptions invalidated, and discovery-informed delivery decisions as a leading indicator of future delivery quality.

---

### Technical debt accumulates in the discovery-delivery gap

**The problem:** Discovery generates insights about user needs that conflict with what delivery has already built. The longer delivery runs ahead of updated discovery, the more architectural debt accumulates.

**The consequence:** Products that technically work but are architecturally wrong for actual user needs. Rewriting is expensive.

**The fix:** Run regular discovery reviews of existing delivered features—ask: does what we built 6 months ago still match what we now understand about the problem?

---

### "Discovery" and "spikes" become synonymous, missing the user dimension

| Discovery Type | Questions | Focus |
|---|---|---|
| **Technical spikes** (well-executed) | Can we build this? | Architecture, feasibility |
| **User discovery** (often skipped) | Should we build this? Does this solve the right problem? | User needs, problem validation |

**The gap:** When teams say "we did discovery" meaning only technical exploration, they've answered one question while skipping the other.

> **Discovery completeness:** Both user discovery and technical discovery are required; neither is sufficient alone.

**The fix:** Treat user discovery and technical discovery as distinct tracks with distinct questions and distinct outputs.

## S2 — How this connects to the bigger system

> **Discovery-to-Delivery Cycle:** Discovery feeds the roadmap; the roadmap determines discovery scope. Managing discovery ahead of delivery is what makes confidence levels real rather than nominal.

| Roadmap Horizon | Discovery Status | Confidence Level |
|---|---|---|
| **Now** (05.05) | Completed discovery | High |
| **Later** | Initial discovery only | Lower |

---

### Discovery Framework: Jobs to Be Done

> **Jobs to Be Done (JTBD):** A structured lens for discovery that asks: what functional, emotional, and social jobs is this user hiring a product to do?

**Why structure matters:** Without JTBD, discovery interviews drift toward feature requests ("I wish I could do X") rather than problem understanding ("here's what I'm really trying to accomplish and what stands in the way"). Discovery quality depends directly on having a structured theory of the user's motivation.

---

### User Stories as Discovery Signals

**Shallow discovery → Feature descriptions**
> "As a user, I want a button that does X."

**Deep discovery → Actual user motivation**
> "As a teacher preparing for class, I want to see my most urgent pre-class tasks so that I can act on them in the 10 minutes I have before students join."

The "so that" clause — where the story's value lives — comes directly from discovery quality.

---

### Prioritization Requires Complete Discovery

> **Prerequisite relationship:** Prioritization frameworks (05.03) only have valid inputs when discovery is complete.

- **RICE (05.03)** needs accurate reach and impact estimates
- **Impact estimates** are discovery outputs — you can only know how much a feature will move a metric if you understand the problem it's solving
- **Risk:** Teams that run RICE scoring on items with incomplete discovery get precise-looking but fundamentally unreliable prioritization

⚠️ Precise numbers from incomplete discovery create false confidence.

---

### Post-Launch Discovery: Experimentation

> **Delivery-phase discovery:** Experimentation and A/B testing (05.07) closes the learning loop.

**The cycle:**
1. Discovered the problem
2. Built a solution  
3. Running post-delivery testing to confirm the solution actually works as hypothesized

The clean separation of pre-delivery discovery and post-delivery testing is what gives the full learning cycle its integrity.

## S3 — What senior PMs debate

### Should discovery have a "done" state?

| Perspective | Position |
|---|---|
| **"Discovery is never done"** | You always have incomplete information. The PM's job is making good decisions under uncertainty—not waiting for certainty. Waiting for "complete" discovery causes slow organizational velocity. |
| **"Discovery needs bounded exit"** | Without a "done" state, discovery becomes infinite (one more interview, dataset, prototype test). Teams use explicit **discovery exit criteria**—pre-defined questions that, when answered, trigger commitment to delivery. |
| **Senior PM consensus** | Discovery is done when highest-priority unanswered questions are addressed and remaining uncertainty is acceptable for your delivery bet. "Acceptable uncertainty" varies by reversibility and cost—a button and a pricing model have different discovery standards. |

---

### Is the dual-track model overrated for small teams?

| Model | Best for | Trade-off |
|---|---|---|
| **Continuous dual-track** (discovery + delivery in parallel) | Teams with PM bandwidth to sustain both tracks | Higher coordination overhead for small teams |
| **Sequential sprints** (discovery sprint → delivery sprint) | Solo PMs, 4-person teams | Simpler execution; risk of building without discovery habits |
| **Early dual-track discipline** | All teams, regardless of size | Builds scalable discovery-delivery habits before growth pressures hit |

**The habit argument:** If you get accustomed to building without discovery in a small team, that pattern scales poorly as you grow.

---

### How is AI changing the discovery-delivery boundary?

**On the discovery side:**
- AI-assisted synthesis of interview transcripts
- Behavioral pattern clustering (automated)
- Support ticket analysis (automated)
- Generative prototyping (prompt → clickable prototype in minutes)

*Result:* Discovery cycle times compress from weeks to days. New bottleneck: interpreting data correctly (not gathering it).

**On the delivery side:**
- AI coding tools reduce implementation time
- **Build to learn** threshold shifts: 2-hour prototype vs. 2-week prototype changes the calculus
- Some research questions now answer faster through cheap prototyping than research

**The skill pivot:**
> **What remains valuable:** Interpretive skills—recognizing which discoveries matter, knowing when insight is strong enough to act on, connecting user behavior to product strategy for durable competitive advantage.
>
> **What becomes commoditized:** Process skills (running surveys, conducting interviews) are increasingly automated.