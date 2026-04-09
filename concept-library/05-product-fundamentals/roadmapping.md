---
lesson: Roadmapping
module: 05 — product-fundamentals
tags: product
difficulty: working
prereqs:
  - 05.01 — PRD Writing defines the problems a roadmap is trying to solve
  - 05.03 — Prioritization Frameworks explains how roadmap items get ranked
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - performance-reviews/apr24-mar25-performance-review.md
  - product-prd/unified-migration-prd.md
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

Imagine a startup team of twelve people. The engineering team is building a recommendation engine. The design team is wireframing a new onboarding flow. Sales just promised a customer an export feature that nobody has heard of. And the founder is telling investors the company is focused on enterprise features — none of which exist.

Everyone is busy. Nobody is building the same product.

This is what product development looks like without a roadmap: a collection of smart people working hard toward different destinations. The problems compound quickly. Engineering finishes the recommendation engine but it can't ship because the infrastructure to support it was never prioritized. The new onboarding flow is half-done when the sales promise forces a pivot to the export feature. And the investor deck is already outdated.

A roadmap is the answer to a deceptively simple question: what are we building next, and why?

It's not a project plan. It's not a promise. It's not a list of features. A roadmap is the artifact that tells every team — engineering, design, sales, marketing, leadership — where the product is going, in what sequence, and based on what reasoning. The sequence is the strategy made visible.

What changed when product teams adopted roadmaps: coordination became possible. Engineering could plan infrastructure in advance of features. Design could start work before engineering needed it. Sales could make promises based on actual intentions, not wishes. And leadership could have a conversation about tradeoffs — what to cut — rather than just adding more.

---

## F2 — What it is — definition + analogy

> **Roadmap:** A prioritized, time-horizon view of what a product team intends to build and why — organized to communicate direction to different audiences.

### The Road Trip Analogy

Imagine planning a long road trip to the Pacific Coast:

| Element | Road Trip | Product Roadmap |
|---------|-----------|-----------------|
| **Destination** | North America Pacific Coast (clear and fixed) | Outcome: the north star user problem or business result |
| **Route** | Logical sequence (can't skip cities between start and end) | Sequence: reflects dependencies and priorities |
| **Schedule** | Flexible daily details (stay longer somewhere interesting, reroute around traffic, discover unplanned stops) | Time horizons (near, next, later): acknowledges increasing uncertainty further out |
| **Value** | Makes the trip legible to everyone on it; prevents misaligned assumptions about sleep, arrival, activities | Makes product direction clear; prevents each person from assuming different priorities |

Without the itinerary, everyone on the road trip makes different assumptions. Without the roadmap, the product team does the same.

### What a Roadmap is NOT

| ❌ NOT a Feature List | ❌ NOT a Commitment |
|---|---|
| "We will build X" | Fixed contract; treating it as immutable creates liability |
| Lacks the "why" and timing context | Plans change when understanding changes — and it always does |
| **Instead:** "We will solve Y by building X, and here's why Y matters now" | **Instead:** A living plan that evolves with new information |

## F3 — When you'll encounter this as a PM

| Context | Why the roadmap matters |
|---------|------------------------|
| **Team planning** | Roadmaps drive sprint and quarterly planning. When engineering asks "what are we building this quarter?" the roadmap is the answer. Without one, every planning meeting becomes a negotiation from scratch. |
| **Stakeholder conversations** | Every stakeholder — your manager, your CEO, your sales team, your enterprise customers — wants to know what's coming. A roadmap gives you a structured, defensible answer that you can share without revealing competitive details or making binding commitments. |
| **Cross-functional alignment** | Design needs to know what's coming two months from now to start work. Marketing needs the release schedule to plan campaigns. Customer success needs it to set expectations with churning accounts. The roadmap is the shared reference that lets each function plan. |
| **When priorities conflict** | "Can we add this feature?" is a question you'll hear constantly. A roadmap gives you a principled way to answer it: here's where we are, here's the current queue, here's how we'd evaluate adding this. Without a roadmap, every request becomes a negotiation based on who asks loudest. |
| **Your own career** | PMs who can build and defend a clear roadmap — explaining not just what's on it but why, and why other things are not — are operating at a senior level. The roadmap is visible evidence of your product thinking. |
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Now / Next / Later: the most useful roadmap format

The format that works for most product teams is a three-horizon view:

| Horizon | Timeframe | Confidence | What goes here |
|---|---|---|---|
| **Now** | 0–4 weeks | High | Actively being built; features are specified, stories exist |
| **Next** | 1–3 months | Medium | Directionally committed; research done, not fully specified |
| **Later** | 3+ months | Low | Strategic intent; problems identified, solutions not decided |

The horizon format is honest about uncertainty by design. Specificity decreases as you move right:
- **Now** items have engineering estimates and designs
- **Next** items are problems and goals, not features
- **Later** items are directional bets based on strategy

#### Why not dates?

Date-based roadmaps fail predictably:
- Near-term: often accurate
- Medium-term: usually wrong
- Long-term: fiction

Teams treat all three columns with equal confidence. When the Q3 date slips, trust collapses — both in the roadmap and in the PM.

**Now/Next/Later sidesteps this by being explicit about confidence level.**

⚠️ **Exception:** Enterprise sales and launch marketing require dates. Solution: put dates only on **Now** items where you have high confidence, and use horizon language for everything else.

---

### Outcome-based vs. feature-based roadmaps

The most important distinction in roadmap design:

| Dimension | Feature-based | Outcome-based |
|---|---|---|
| **What's specified** | Output | Problem |
| **Definition of success** | Feature shipped | Problem solved |
| **Example** | Q2: Build bulk export. Q3: Build dashboard v2. Q4: Build API integrations. | Q2: Reduce enterprise onboarding from 14 days to 5 days. Q3: Enable self-serve reporting for power users. Q4: Support multi-team workflows. |
| **Ease** | Easy to write and understand | Harder to write, much more valuable |
| **Team behavior** | Optimize for shipping features | Optimize for solving problems |
| **Evaluation** | Done = shipped | Done = measurable improvement |

**Key dysfunction of feature-based roadmaps:**
When the bulk export ships but nobody uses it, a feature-based roadmap says "done." An outcome-based roadmap asks "did enterprise onboarding time drop?"

> **Outcome-based roadmap:** Forces alignment on the problem before committing to a solution. Gives engineering flexibility to find better approaches. Makes it possible to answer "did this work?" after shipping.

---

### Building a roadmap: the four inputs

| Input | What it provides | When it overrides others |
|---|---|---|
| **Strategy and goals** | The "why" — what company bets you're making | Always: if an item doesn't connect to a current goal, it doesn't belong on the roadmap |
| **User research and discovery** | The problems worth solving — what users actually struggle with | When the strategy is vague; discovery makes it specific |
| **Engineering constraints** | The sequence — what's technically feasible and what unlocks later capabilities | When two equally important items conflict; the one with lower technical risk goes first |
| **Competitive and market signals** | The timing — when "good enough" is no longer defensible | When a competitor ships; timeline pressure overrides ideal sequencing |

**Conflict resolution rule:** When inputs conflict — strategy says X, engineering says Y can't ship for 3 months — don't pick one. Ask: **what's the minimum version of X that delivers value before Y becomes available?** Almost every constraint has a partial path forward.

---

### Outcome-based roadmap template

The discipline of writing outcomes rather than features:

```
Horizon: Now
Outcome: [Problem we're solving + measurable definition of success]
  Why now: [What's forcing this to the top — data, business pressure, dependency]
  Key stories: [3–5 user stories that are the primary mechanism]
  Success metric: [Specific, measurable, time-bounded]

Horizon: Next
Outcome: [Problem we intend to solve]
  Why this: [Evidence this is the right problem]
  Hypothesis: [Likely approach — not committed]
  Discovery needed: [What we still need to learn before committing]

Horizon: Later
Outcome: [Problem area we're tracking]
  Signal to promote: [What would move this to Next]
```

#### Example: BrightChamps teacher dashboard

```
Now: Reduce missed class incidents caused by teacher join friction
  Why now: 12% of classes in Jan had teacher-side join delays > 5 min
  Key stories: Single-click join, 10-sec countdown, pre-class task list (max 3)
  Success metric: Teacher join delays < 2 min in 95% of classes by March

Next: Improve post-class teacher compliance rates
  Why this: Happy Moments and attendance fill rates < 60% — ops team impact
  Hypothesis: In-class reminder at T+45 reduces post-class forgetting
  Discovery needed: Teacher interviews on what prevents compliance

Later: Enable async parent communication from teacher dashboard
  Signal to promote: Parent satisfaction drops below 70% in any cohort
```

---

### BrightChamps unified migration roadmap as a case study

**The challenge:** 13-month platform migration (Feb 2023 – Mar 2024) requiring:
- 30+ engineers
- 7 legacy systems
- Hundreds of use cases

How do you sequence a migration that is simultaneously a **business risk** (breaking the student experience) and a **business necessity** (scaling to new courses is impossible without it)?

#### Sequencing strategy

1. **Start with low-risk verticals** (Robotics, Financial Literacy) to test stability before high-stakes migrations
2. **Route new students into unified flow first** (smaller blast radius for bugs)
3. **Batch migrate paid students in phases** (never migrate everyone at once)
4. **Keep parallel systems active during migration** as a safety net

#### What this reveals

This is outcome-based roadmapping in practice: the outcome was **"migrate all 7 courses with zero critical outages and minimal student churn."** The feature sequence was the means to that outcome.

Every sequencing decision was made by asking:
- Does this reduce risk or increase it?
- Does this build toward the outcome or away from it?

---

### What goes on a roadmap and what doesn't

Not every idea belongs on a roadmap. The roadmap represents your bets — things you believe are worth doing now given what you know. The rest goes in the backlog.

**Practical filter:** Does this item connect to a current company or product goal?
- ✅ **Yes** → Roadmap-eligible
- ❌ **No** → Parking lot for later review

#### Tech debt and maintenance work

⚠️ **Common mistake:** Including maintenance and tech debt on the same roadmap as new features.

Technical work that doesn't have a user-facing outcome is real and important, but mixing it into a customer-facing roadmap confuses both audiences.

**Better approach:**
- Maintain a separate technical roadmap, OR
- Allocate a percentage of capacity (e.g., 20% of sprint capacity for technical health)

This avoids treating tech debt as a feature.

## W2 — The decisions this forces

| **Decision** | **The Tension** | **Recommendation** |
|---|---|---|
| How far out should the roadmap extend? | 12 months is expected, but uncertainty makes commitments misleading beyond 6 months | Build at the detail level you can commit to, then extend with decreasing specificity. 3 months of real commitments beats 12 months of wishful thinking. |
| Feature-based or outcome-based? | Outcomes are more valuable but harder to communicate; stakeholders want specific features | Write an internal outcome-based roadmap and simplified feature-based summary for external audiences. Features are your hypothesis for achieving the outcome. |
| How much specificity in "Later"? | Too little looks unorganized; too much creates false commitment | "Later" items should be problems, not features. One sentence per item. "Reduce manual ops work in student onboarding" ✓ — "Build automated email sequencing" ✗ |
| Who sees the roadmap, and what do they need? | Engineering, leadership, sales, and customers all need different things from one document | Maintain one authoritative internal roadmap. Create derivatives for specific audiences: executive summary, sales enablement, customer-facing statement. |
| How do you handle urgent requests that disrupt the roadmap? | Urgent requests arrive constantly; without a process, the roadmap becomes irrelevant within weeks | Treat urgent requests as priority-override candidates. When something arrives, explicitly name what gets pushed out or cut. Adding without removing creates a 18-month roadmap in a 6-month box. |

### Deeper look at each decision

#### Decision 1: How far out should the roadmap extend?

> **Standard practice:** 12 months is the standard answer, but the meaningful part of most roadmaps is 3–6 months.

The honest answer depends on *what you're using the roadmap for*:

- **Internal team alignment:** 3 months of "now + next" and directional "later" is usually enough
- **Enterprise sales & investor communication:** 12-month view is expected — but explicitly frame as directional, not committed

---

#### Decision 2: Feature-based or outcome-based?

| **Approach** | **Strength** | **Weakness** |
|---|---|---|
| **Outcome-based** | More valuable; expresses strategy clearly | Harder to communicate to stakeholders wanting exact features |
| **Feature-based** | Sales can promise; marketing can plan launches; engineering knows what to build | Obscures the problem you're solving; locks in solutions prematurely |

**The solution:** Write an internal outcome-based roadmap (your strategy) and a simplified feature-based summary for external audiences (your communication artifact). The two should be derivable from each other.

---

#### Decision 3: How much specificity in the "Later" column?

**What to avoid:**
- Too little specificity → "Later" looks like an unorganized backlog
- Too much specificity → Creates false commitment you'll need to walk back

**Right level of specificity:**
- ✓ **Problem statement:** "Reduce manual ops work in student onboarding"
- ✗ **Solution statement:** "Build automated email sequencing for trial-to-paid conversion"

Format: One sentence per item, clearly framed as a *problem* you intend to solve rather than a *feature* you intend to build.

---

#### Decision 4: Who sees the roadmap, and what do they need from it?

| **Audience** | **Primary Need** |
|---|---|
| Engineering | Specificity and sequencing |
| Leadership | Outcomes and timing |
| Sales | Commitments and dates (or honest lack of them) |
| Customers | Confidence that their problems are being addressed |

**Key insight:** One roadmap format cannot serve all audiences well. Don't try.

**Better approach:**
1. Maintain one authoritative internal roadmap with full context
2. Create derivatives for specific audiences:
   - Executive summary for leadership
   - "What's coming" slide for sales enablement
   - Customer-facing statement for enterprise accounts

Each derivative is a *subset* of the authoritative version.

---

#### Decision 5: How do you handle urgent requests that disrupt the roadmap?

⚠️ **Risk:** Without a process for handling urgent requests, your roadmap becomes irrelevant within weeks of publication.

**What happens every quarter:**
- A competitor ships a feature
- A big customer threatens to churn
- A critical bug turns into a product gap

**Treatment:** Urgent requests are priority-override *candidates*, not automatic additions.

**Process for each urgent request:**
1. Evaluate explicitly
2. Name what gets pushed out or cut
3. Communicate the trade-off

⚠️ **Common mistake:** Adding without removing. This is how roadmaps become 18 months of work packed into a 6-month box.

## W3 — Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **"What are the technical dependencies I'm not seeing in this sequence?"** | Hidden constraints in the roadmap order. Some features can't ship before others because of architecture dependencies — the engineer often knows these before the PM does. Missing them means scheduling conflicts mid-quarter. |
| **"If we had to cut one item from 'Next' to protect the 'Now' commitment, which one would you cut first and why?"** | Where the team's confidence is weakest. Engineers often have a hierarchy of risk that they don't volunteer unless asked. This question surfaces it. |
| **"Is there anything in the 'Later' column that would fundamentally change the technical approach we're taking Now, if we knew it was coming?"** | Whether current architecture decisions are creating technical debt. If a future roadmap item requires rearchitecting something you're building today, it may be worth a short conversation now before it becomes expensive later. |
| **"What's the blast radius if this 'Now' item slips two weeks?"** | How tightly coupled the roadmap is. If one slip cascades into three downstream delays, the roadmap is too tightly sequenced. Buffer needs to exist somewhere. |
| **"Which of these Now items has the most unknowns?"** | Where the roadmap is most fragile. Items with high uncertainty deserve earlier investigation, not just earlier priority. A discovery spike on an unknown item in "Now" is often better than committing to a specification that turns out to be wrong. |
| **"What's the minimum viable version of this that we'd be comfortable shipping?"** | Whether the scoping on roadmap items is realistic. Engineers often have strong opinions about what "shippable" means that PMs underestimate. |
| **"Are there any 'Next' items that would be dramatically easier if we changed the order?"** | Whether there's a better sequence than the one you've chosen. Engineering efficiency is a legitimate input to roadmap sequencing — if item B takes 2 weeks when item A ships first, and 6 weeks if we ship item C first instead, that's worth knowing. |

## W4 — Real product examples

### BrightChamps — Platform migration sequencing as roadmap strategy

**What:** Sequenced 7 course migrations over 13 months by choosing low-risk verticals first (Robotics, Financial Literacy) rather than highest-revenue ones.

**Why:** Low-risk-first sequence validated the migration playbook at small scale before applying it to higher-stakes verticals. Problems (data normalization issues, Redis cache inconsistencies, teacher schedule conflicts) appeared with small blast radius.

**Key principle:** Sequencing for learning — early roadmap items should generate confidence and knowledge, not just output.

**Takeaway:** 7 courses migrated across 14 months with no critical outages and maintained service continuity.

---

### Linear — Roadmaps that evolve by design

**What:** Public roadmap with three explicit states: "In Progress" (committed), "Up Next" (planned), "Considering" (exploring, no delivery date).

**Why:** 
- "Considering" items signal strategic interest without locking in promises
- Customers evaluate fit without sales gatekeeping
- Team stays accountable for in-progress work without speculative overcommitment

**Key design decision:** Linear publicly moves items from "Considering" back to nothing — making curation visible builds trust rather than eroding it.

**Takeaway:** Roadmap versioning and transparent curation reduce both customer confusion and internal commitment creep.

---

### Figma — Outcome-based roadmap driving platform strategy

**What:** 2020–2022 roadmap organized around outcomes (problem statements) rather than features:

| Outcome | Generated Features |
|---------|-------------------|
| Make collaborative design real-time | Multiplayer cursors |
| Enable developers to build from design without re-speccing | Dev Mode |
| Make design systems maintainable at scale | Variables and Tokens |

**Why:** 
- Prioritization debates resolve with "does this serve the outcome?" instead of feature-by-feature negotiation
- Engineering gets latitude to find best technical approach
- Team can rearchitect without creating "roadmap misses" (Dev Mode took longer than planned due to performance rework, but outcome commitment remained solid)

**Takeaway:** Outcome-based roadmaps survive technical uncertainty better than feature-based ones.

---

### Spotify — The 20% ring and the honest roadmap

**What:** Explicitly allocates 20% of engineering capacity to "tech health" (infrastructure, debt reduction, architecture). This capacity doesn't appear on the product roadmap but directly enables shipping velocity on everything else.

**Why:** 
- Teams without explicit technical investment see velocity decline 10–15% per quarter as debt accumulates
- 20% allocation maintains constant velocity
- Outcome-based roadmaps become feasible only with honest capacity visibility

**PM implication:** Roadmaps that don't account for technical investment overestimate capacity and underdeliver consistently.

**Takeaway:** An honest roadmap starts with honest capacity — the technical health allocation conversation must happen before committing to new outcomes.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The roadmap becomes a commitment document instead of a direction document

**The problem:** Stakeholders—especially sales—treat roadmap items as promises. PMs respond by sandbagging: removing anything they're not 100% certain about. The roadmap stops reflecting strategy and starts reflecting only safe bets.

**Result:** Team executes on lowest-risk work, not highest-impact work.

**The fix:** Add explicit confidence levels to the roadmap itself.

| Confidence Level | Meaning | Accountability |
|---|---|---|
| High confidence | We're building it | Commit to timeline |
| Medium confidence | We intend to, still validating | Update status regularly |
| Low confidence | Considering it, no commitment yet | Revisit quarterly |

---

### Outcome-based roadmaps drift back to feature roadmaps under pressure

**The problem:** Outcome-based roadmaps work in planning sessions. But when sales asks "is feature X on the roadmap?" the path of least resistance is to translate outcomes into features for the conversation—then forget to translate back.

**Result:** Internal roadmap gradually becomes feature-based because that's how it was communicated externally.

**The fix:** Maintain two separate views.

| View | Purpose | Authority |
|---|---|---|
| Outcome-based (internal) | Reflects actual strategy | Authoritative |
| Feature-based (external) | Answers stakeholder questions | Derived on request only |

Never let the external view drive changes to the internal one.

---

### Long-horizon roadmaps create credibility debt

**The problem:** Every item in "Q3" that doesn't ship erodes trust. Engineering loses faith that planning predicts reality. Stakeholders stop relying on the roadmap. Leadership treats it as fiction.

**Result:** Roadmaps stop generating coordination benefits—the entire point of having them.

**The fix:** Use tiered time horizons with matching confidence and accountability.

| Horizon | Time | Commitment | Use |
|---|---|---|---|
| Committed | 8 weeks | High accountability | "Now" items |
| Directional | 6 months | Medium accountability | "Next" items |
| Orientational | 12 months | Low accountability | Strategic direction only |

---

### Roadmap misses cascade when dependencies are hidden

**The problem:** Item A slips two weeks. Item B depends on A. Item C depends on B. The slip propagates and Q2 looks nothing like the plan.

**Why it happens:** PMs skip dependency mapping because it takes time and requires engineering input.

**Result:** Roadmaps look coherent on paper but collapse when one item runs late.

**The fix:** Before sprint commitment, explicitly map "what has to be true for this to ship" for every Now item.

⚠️ **Hidden dependencies are a primary cause of roadmap failure.** Block time for dependency discovery before you commit to timelines.

---

### The roadmap becomes a constraint that prevents better decisions

**The problem:** The roadmap isn't wrong, but it stops the team from adapting when reality changes. A team committed publicly to a 12-month plan discovers a better approach in month 3.

**The dilemma:**
- Change course → "miss" roadmap items → lose stakeholder trust
- Keep the plan → ship the wrong thing

**The fix:** Build in explicit checkpoint moments—typically quarterly—where the roadmap is formally reviewed and revision is expected, not exceptional.

> **Roadmap revision isn't failure.** It's evidence-based planning working correctly.

## S2 — How this connects to the bigger system

> **Roadmap:** The operational translation of company strategy into a sequenced set of deliverables that shows engineering what to build and when.

**Roadmaps are the link between company strategy and engineering execution.** A company strategy without a roadmap is a vision document. A roadmap without a company strategy is a backlog. The roadmap makes strategy operational — it takes "we will become the leading enterprise collaboration tool" and translates it into "here's what we're building in the next six months and why that sequence gets us there."

| **Without roadmap** | **Roadmap** | **Without strategy** |
|---|---|---|
| Strategy = vision only | Strategy + roadmap = operational plan | Roadmap = backlog only |

### Prioritization frameworks ← → Roadmaps

**Prioritization frameworks (05.03) populate the roadmap.**

| **Tool** | **Answers** | **Output** |
|---|---|---|
| RICE, opportunity scoring, cost-of-delay | "What should we build?" | Ranked list |
| Roadmap | "In what sequence and within what timeframe?" | Temporal shape to the list |

*These are complementary:* prioritization gives you a ranked list; roadmapping gives that list a shape in time.

### User stories: The atomic unit

**User stories (05.04) are the atomic unit below the roadmap.** A roadmap item like "enable enterprise SSO" is too large to build directly. It decomposes into features, which decompose into stories.

- **Roadmap level:** Legible to executives and stakeholders
- **Story backlog level:** Legible to engineering

Good PMs maintain both and can translate fluently between them.

### Discovery status → Roadmap placement

**Discovery vs. Delivery (05.06) determines roadmap confidence.**

| **Roadmap timeframe** | **Discovery status** | **What you know** |
|---|---|---|
| **Now** | ✅ Completed | Problem understood, solution validated, definition of done clear |
| **Next** | 🔄 In-progress | Problem known, approach still being validated |
| **Later** | 🔶 Initial only | Problem hypothesis, no validated solution yet |

⚠️ **Risk:** A roadmap that places items in "Now" without completed discovery will trigger mid-sprint pivots and broken commitments.

### North Star Metric: The tiebreaker

> **North Star Metric (06.01):** A single measurement that makes roadmap tradeoff decisions resolvable by impact rather than by seniority or persuasiveness.

**North Star Metric (06.01) makes roadmap tradeoffs resolvable.** When two roadmap items compete for capacity, the north star metric provides the decision rule: which one moves the metric more? Without a north star, roadmap prioritization debates are often resolved by seniority or persuasiveness rather than impact. The north star is the neutral arbiter.

## S3 — What senior PMs debate

### Should roadmaps be public?

| Argument FOR | Argument AGAINST |
|---|---|
| Builds customer trust | Competitors see your strategy |
| Creates accountability | Customer expectations lock in prematurely |
| Community feedback improves roadmap | Legal/contractual exposure for enterprise |

**The shift:** B2B SaaS companies increasingly publish directional roadmaps that signal intent without timeline commitments. The language has evolved from "X ships in Q3" to "we're working on X."

*What this reveals:* The debate isn't about transparency vs. secrecy anymore—it's about managing commitment risk while maintaining trust.

---

### Is the now/next/later format becoming a crutch?

**The critique:**
- Avoids hard sequencing work by deferring everything ambiguous to "later"
- "Later" becomes a graveyard for ideas nobody has courage to cut
- Lets teams avoid real evaluation of *when* and *whether* items ship

**The defense:**
- Dates without confidence intervals are fiction that erode trust faster
- Honest ambiguity is healthier than false precision
- The format works if "later" is actively pruned (every 3+ quarters without progress = cut or archive)

> **Healthy now/next/later:** Regular reevaluation of the "later" column. If items don't advance in 3+ quarters, they get explicitly cut or archived—not abandoned indefinitely.

---

### How is AI changing roadmapping?

**Two effects compressing roadmap cycles:**

1. **Engineering velocity increases**
   - Features: 6 weeks → 2 weeks
   - Effect: "Now" horizon shrinks; weekly refinement replaces quarterly review

2. **Discovery accelerates**
   - User research: 3 weeks → days (AI-augmented feedback analysis, support ticket clustering, behavioral pattern detection)
   - Effect: Items move from "later" (hypothesis) → "next" (validated) much faster

**The strategic implication:**

Roadmapping skill is shifting from *format mastery* to *judgment calls*:
- What to build vs. skip
- What validation level is sufficient
- When to commit vs. when to keep exploring

⚠️ **AI accelerates execution, not decision-making.** The fundamentals of what makes a roadmap decision *good* remain unchanged.