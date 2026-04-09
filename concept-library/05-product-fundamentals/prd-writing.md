---
lesson: PRD Writing
module: 05 — Product Fundamentals
tags: product
difficulty: working
prereqs: []
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - product-prd/unified-migration-prd.md
  - technical-architecture/student-lifecycle/unified-demo-paid-experience-student.md
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

In the early days of software development, products were built through informal communication. The founder had an idea, sat down with an engineer, and explained it verbally. The engineer built it. If the result was wrong, they talked again.

This worked when teams were two or three people. It stopped working the moment the team had five engineers, a designer, a QA tester, and stakeholders in three different time zones. Suddenly, the founder's verbal explanation became six different things in six people's heads. The engineer built what they heard. The designer designed what they imagined. The QA tester tested against their own interpretation. The result: a product no one had actually intended to build, discovered only after weeks of work.

Product Requirements Documents — PRDs — emerged as the solution. Not as bureaucratic paperwork, but as a shared source of truth. A single artifact everyone could reference, disagree with, mark up, and align on before any code was written.

The best PRDs are not long. They are precise. They answer the questions that would otherwise be asked in a hundred side conversations: What problem are we solving? Who is it for? What does success look like? What are we explicitly not building? What are the edge cases engineering will hit at 2am on a Friday?

A well-written PRD doesn't prevent all miscommunication. But it shifts the miscommunication from happening in production — when it costs weeks of rework — to happening in a document comment thread, where it costs an hour of revision.

---

## F2 — What it is — definition + analogy

> **PRD (Product Requirements Document):** A written document that defines the problem a product feature or initiative is solving, who it is solving it for, what the solution must do, and how we'll know it worked.

### The Architect-to-Contractor Analogy

Think of a PRD like the brief an architect hands to a building contractor before construction begins.

**The brief does:**
- Specify the building site and client's need (e.g., a 4-bedroom home with a north-facing garden)
- State non-negotiables (must pass fire safety code)
- List constraints (budget and timeline)
- Clarify what is explicitly *not* needed (e.g., a garage)

**The brief does NOT:**
- Prescribe which hammer to use
- Dictate the order to lay bricks

**What happens without it:**
The contractor makes reasonable assumptions—some wrong. Client arrives on move-in day, sees the unwanted garage, and asks why it exists. Six weeks and $40,000 of work must be demolished.

**The mapping:**
- PRD = the brief
- Engineer = the contractor
- PM = the architect

### What a PRD Is Not

| Document Type | Purpose | Who Owns It |
|---|---|---|
| **PRD** | *What* and *why* | PM |
| Technical design document | *How* to build it | Engineer |
| Project management plan | *When* and workflow | Jira/Linear |
| Design specification | Visual/interaction details | Designer |
| Strategy document | Product direction | Leadership |

Each serves a different purpose. The PRD focuses exclusively on *what* and *why*.

## F3 — When you'll encounter this as a PM

| Situation | Why it matters | PM action |
|-----------|----------------|-----------|
| **Before every feature sprint** | Engineering teams expect a PRD before building. Spec review meetings surface questions that would cost 10× more to fix during coding. | Have PRD ready for spec review |
| **When a feature goes sideways** | Post-mortems start with "What did the PRD say?" Vague or missing PRDs leave no accountability. PRDs create protection for the PM. | Document decisions explicitly to establish accountability |
| **When stakeholder asks "can we just add X?"** | Scope creep happens when requirements are soft. A written "Out of Scope" section gives you a boundary to defend. | Point to PRD's scope section; add requests to backlog |
| **When you join a new team** | Existing PRDs show product evolution, problems solved, and conscious vs. accidental decisions faster than reading code. | Read PRDs before the codebase for better context |
| **When you're new to PM** | Writing early PRDs feels uncomfortable—you'll face questions without answers. That discomfort is the job. PRDs force you to confront unknowns before they become engineering waste. | Embrace discomfort as part of learning the role |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level, or equivalent PM experience
# ═══════════════════════════════════

## W1 — How it actually works

A PRD has standard sections, and each section has a job. Understanding what job each section does — and what happens when it's missing — is the difference between a PRD that engineers use and one that gets ignored.

### The core PRD structure

| Section | Purpose | Red flag |
|---------|---------|----------|
| **1. Overview / What this is** | Enable quick triage by busy engineers | Takes >90 seconds to read |
| **2. Problem statement** | Establish *why* this work matters | Focuses on solution ("users want X") instead of pain ("users experience Y, causing Z") |
| **3. User stories** | Define desired behavior without prescribing implementation | Written as acceptance criteria or implementation details |
| **4. Feature scope** | Prevent scope creep and anticipate "why didn't we..." questions | Missing Out of Scope section |
| **5. Functional requirements** | Provide testable specifications for engineering | Vague language ("users should see") instead of precise, measurable statements |
| **6. Success metrics** | Establish before-the-fact evaluation criteria | Metrics defined *after* launch |
| **7. Edge cases & error handling** | Prevent 2am P0 incidents | Undocumented edge case behavior |
| **8. Dependencies** | Identify blockers before sprint execution | Missing cross-team dependencies |

---

#### 1. Overview / What this is

One paragraph. The busiest engineer on your team should be able to read this and know whether they need to keep reading.

**Required:** initiative name, user served, expected outcome  
**Length limit:** 90 seconds

---

#### 2. Problem statement

> **Problem Statement:** A description of user pain, its consequences, and quantified evidence that the problem matters enough to solve.

The most important section of the PRD.

**Weak:** "Users want X"  
**Strong:** "Users experience Y pain point → causes Z behavior → costs us A (quantified). Evidence: B (research, data, support tickets)."

**Example:**  
*"BrightCHAMPS's pre-demo attendance and in-demo engagement are lower than target. Parents surveyed (n ~6,000) cited three primary unmet needs: timely reminders, interactive content, and clear communication."*

This problem statement has a quantified signal. It makes why the work matters obvious.

---

#### 3. User stories

> **User Story:** "As a [user type], I want to [action], so that [benefit]."

User stories describe desired behavior *without prescribing implementation*. They are **not** acceptance criteria — they provide context for why functional requirements exist.

---

#### 4. Feature scope

**Two sections — both equally important:**

| In Scope | Out of Scope |
|----------|--------------|
| Define what *must* be built | Record conscious decisions about what *not* to build |
| Answers: "What are we committing to?" | Answers: "Why didn't we just...?" (6 months later) |
| | Prevents scope creep |
| | Documents deferred work for future roadmaps |

**Example:**  
*Unified Demo & Paid PRD explicitly scoped out:*
- Arena tab ("deferred to a future scope")
- Project Tags in Global Feed
- Course Explorer detail pages

*Impact:* Three sentences prevented weeks of sidebar conversations with engineers asking "Should we build the Arena flow too?"

---

#### 5. Functional requirements

> **Functional Requirement:** A precise, testable specification of what the feature must do.

**Not acceptable:** "Users should see their homework" (too vague to test)  
**Acceptable:** "The system must display all pending assignments" (testable)  
**Better:** "The Missed Class Card must appear in My Feed within 1 hour of the missed class window" (testable with embedded acceptance criteria)

Each requirement should be:
- ✓ Testable by QA
- ✓ Precise enough for engineering to write acceptance criteria
- ✓ Quantified where applicable (timing, thresholds, limits)

---

#### 6. Success metrics

> **Success Metric:** A before-the-fact measurement that determines whether the feature achieved its goal.

⚠️ **Critical:** Metrics defined *after* launch will unconsciously reflect what the data *shows* — not what you committed to. You will always be able to claim success.

Define metrics *before* launch. This forces honest evaluation.

**Example:**  
*Unified Demo & Paid PRD:* "Lead to Completion % (USA) from 36–39% baseline to 60% target"  
- Specific ✓
- Measurable ✓
- Before-the-fact commitment ✓

---

#### 7. Edge cases and error handling

The scenarios that will:
- Break your feature at 2am
- Generate a P0 incident
- Require post-launch fixes if not documented

⚠️ **When engineers see edge cases in the PRD:** They follow documented behavior. When they don't: They make judgment calls in code — inconsistently.

Enumerate edge cases explicitly. Example cases to always include:
- Network timeouts / offline scenarios
- Rate limits and capacity thresholds
- Partial data or missing fields
- Concurrent user actions
- Stale cache states

---

#### 8. Dependencies

> **Dependency:** Anything that must exist before the feature can be built or launched.

Cross-team dependencies are the #1 reason features slip timelines.

**Common dependencies:**
- API availability / backend infrastructure
- Data migrations
- Third-party integrations
- Design system updates
- Other team's feature completions

A PRD without enumerated dependencies will surprise you in week 3 of the sprint.

## [Feature Name] — PRD

### Overview
One paragraph: what this initiative is, who it's for, and the expected business outcome.

**Read time: 90 seconds max.**

---

### Problem statement

**What pain exists today?**
- User signal (research, support tickets, surveys)
- Data (quantified if possible)
- Business impact of not solving it

---

### Success metrics

| Metric | Baseline | Target | How measured |
|---|---|---|---|
| [Primary metric] | [current] | [goal] | [source/tool] |
| [Secondary metric] | [current] | [goal] | [source/tool] |

> **Critical:** Metrics defined before feature ships—not "we'll figure it out after."

---

### User stories

As a [user type], I want to [action], so that [benefit].

**Coverage:** 2–5 stories covering primary user flows

---

### Scope

#### In scope
- [Feature 1 — one line]
- [Feature 2 — one line]

#### Out of scope
- [Explicitly deferred thing] — **why:** [brief reason / when to revisit]
- [Explicitly deferred thing] — **why:** [brief reason / when to revisit]

---

### Functional requirements

| Requirement | Acceptance criteria |
|---|---|
| [Requirement] | [Testable condition] |
| [Requirement] | [Testable condition] |

---

### Edge cases and error handling

| Scenario | Expected behavior |
|---|---|
| [Edge case] | [What the system must do] |
| [Edge case] | [What the system must do] |

---

### Dependencies

| Team / System | What's needed | By when | Owner | Fallback if delayed |
|---|---|---|---|---|
| [Team] | [Specific output] | [Date] | [Name] | [Plan B] |
| [Team] | [Specific output] | [Date] | [Name] | [Plan B] |

## W2 — The decisions this forces

### Decision 1: How much detail to include

**Question:** How long should a PRD be?

| Approach | Problem | Outcome |
|----------|---------|---------|
| **Too short** | Three bullet points ("Build a post-class report feature") | Engineers write their own spec based on interpretation; may differ from your intent |
| **Too long** | 40 pages with pixel dimensions and feed-ranking algorithms | Engineers ignore it—or follow it blindly and miss the intent behind solvable problems |
| **Right length** | As short as possible while answering every engineer question before work starts | One page for small features; ten pages for complex migrations like BrightChamps Unified Migration (100+ use cases) |

> **Recommendation:** Write for the most skeptical engineer on your team, not the most trusting. If that engineer would read this and still have a question, the PRD is incomplete.

---

### Decision 2: Problem statement depth

**Question:** Should the PRD explain the "why" or just the "what"?

> **Answer:** Always the why.

**Why this matters:**
- Engineers who understand the problem make better tradeoff decisions than those following specs blindly
- Example: "Users need to see class link prominently because 15% of trial users miss class due to difficulty finding it" → engineer makes different UI decisions than "show the class link"
- Data-rooted problem statements are defensible when stakeholders push back on scope or engineers suggest alternatives

> **Recommendation:** Write the problem statement first, before any requirements. If you can't write a clear problem statement, the feature isn't ready to spec.

---

### Decision 3: Acceptance criteria ownership

**Question:** Who writes the acceptance criteria — PM or QA?

> **Standard division:** PMs write functional requirements; QA translates them into acceptance criteria. But this creates a risk.

**The problem with full QA ownership:**
- PMs abdicate a critical decision: what does "done" mean for this feature?
- Ambiguous acceptance criteria become end-of-sprint negotiations
- Negotiations under time pressure resolve toward "shipping fast," not "shipping right"

**What PMs must own:**
- Behavioral acceptance criteria with time, quantity, or condition constraints
- Example: "Card must appear within 1 hour," "all required fields must be present"
- QA can write detailed test cases; PM defines the definition of done

> **Recommendation:** For every functional requirement with a time, quantity, or behavior condition, write the acceptance criterion in the PRD before review. "Verified end-to-end with QA sign-off" is not an acceptance criterion.

---

### Decision 4: Out of scope as a scope-creep defense

**Question:** Should you explicitly list what you're not building?

> **Answer:** Yes. Always.

**Why explicit lists matter:**
- Every unbuilt feature will be asked for (by sales, engineers, designers, stakeholders)
- Absence from the Out of Scope list = absence of a decision
- Explicit listing = this was considered and deferred, not forgotten

> **Recommendation:** Write the Out of Scope section in your first PRD draft—*before* you write the In Scope section. Articulating what you're not building often clarifies what you actually are building.

---

### Decision 5: When to update vs. lock the PRD

**Question:** Should the PRD change once development starts?

| Phase | Status | Rule |
|-------|--------|------|
| **Writing & review** | Living document | Changes expected |
| **Active development** | Locked | Changes require full-team agreement |
| **Mid-sprint changes** | High cost | Engineers redo completed work |

**How to manage changes:**
- Log each change with date and reason
- Communicate to full team—don't just update the document

⚠️ **Warning:** If requirements change frequently after kickoff, the root cause is usually a problem statement that wasn't validated before writing. Stop, revalidate, then proceed.

> **Recommendation:** Treat the PRD as locked after sprint kickoff, except for explicit scope changes that the full team agrees to.

## W3 — Questions to ask your engineer

**"What's the first thing in this PRD you'd need more detail on before starting?"**

*What this reveals:* The spec review meeting is structured around this question. Engineers read PRDs looking for ambiguities. Getting the ambiguities surfaced before sprint planning means they get resolved before they become blockers.

---

**"Are there any edge cases in this spec that you'd handle differently than described?"**

*What this reveals:* Engineers have deep domain knowledge about failure modes. An engineer who says "the way you've described handling the missing metadata case would cause a cascade failure in X scenario" is saving you a P0 incident. This question invites that input.

---

**"What are the dependencies that aren't in this PRD?"**

*What this reveals:* Cross-team dependencies live in the knowledge of people who've tried to build similar things. Engineers know which other teams they'll need to coordinate with. This question surfaces hidden dependencies before they become schedule surprises.

---

**"Is anything in this PRD prescribing implementation rather than behavior?"**

*What this reveals:* PMs sometimes accidentally write technical design into PRDs — specifying database schemas, API structures, or algorithms when they should be specifying behavior. Engineers will tell you when this happens, and when they do, it usually means the requirement can be stated more simply.

---

**"Given this spec, how would you build the acceptance criteria for each requirement?"**

*What this reveals:* This is the fastest way to test whether your requirements are testable. If an engineer can't write a test case from a requirement, the requirement is too vague. Do this exercise before the sprint, not during QA.

---

**"Which requirements are most likely to change based on what we learn in the first week?"**

*What this reveals:* Engineers have pattern recognition from past projects about which requirements tend to be wrong the first time. This question surfaces the hypotheses baked into the PRD and lets you flag them for early validation rather than late discovery.

## W4 — Real product examples

### BrightChamps — Unified Platform Migration

**Headline:** PRD as navigation for a 30-engineer project

**What:** Consolidated 7 courses across 3 legacy platforms (BrightChamps Legacy: Coding & Robotics | Education10x: Financial Literacy | Scola: Public Speaking, Cambridge English, IELTS, and others) into a single platform in under 14 months. PM documented 100+ use cases across student, teacher, and admin flows.

**Why:** Without a written document encoding sequencing decisions, 30 engineers would have made 30 different priority calls. The PRD anchored execution strategy:
1. Start with low-risk verticals (Robotics, Financial Literacy)
2. Route new students into unified flow first
3. Migrate existing paid students in batches

**Outcomes:**
- Ops headcount: 20 → 3–4 people (80% reduction)
- New course onboarding: months → weeks
- 7 courses migrated successfully

**Takeaway:** The PM who could not articulate a written rollout plan would have been overwhelmed by the coordination surface area.

---

### BrightChamps — Unified Demo & Paid Dashboard

**Headline:** Edge cases and dependencies working as designed

**What:** PRD documents 7 edge cases with explicit handling behaviors:

| Edge Case | Market Context | Handling Rule |
|-----------|----------------|---------------|
| Teacher names < 3 characters | Common in Southeast Asia (e.g., "Jo," "Li") | Use full name if first name is < 3 characters |
| Multiple assignments pending | — | [Documented] |
| Missing curriculum metadata | — | [Documented] |
| Failed video loads | — | [Documented] |
| Arena tab clicks | — | [Documented] |
| Missing class link | — | [Documented] |
| Missed class card timing | — | [Documented] |

**Why:** Without the PRD rule, engineers would have shipped a display rule showing a single character as teacher name in class reminder card. Edge cases aren't hypothetical—they're real customer pain points waiting to happen.

**Dependencies tracked:** 6 cross-team dependencies with named owners

| Dependency | Owner |
|------------|-------|
| Gurukul Middle Layer Initiative | [Named] |
| Curriculum Backend Metadata API | [Named] |
| Event Schema | [Named] |
| Figma finalization | [Named] |
| QA sign-off | Vidurbh Raj Srivastava |
| Business metric alignment | [Named] |

**Takeaway:** Naming the owner of each dependency creates accountability that "the curriculum team" does not.

---

### Notion — The PRD that launched a $10B product

**Headline:** Behavior-first requirements age better than implementation-first

**What:** Early internal PRDs for the block editor defined "everything is a block" as a *behavioral* requirement before it was an architectural decision.

**Behavioral requirement (from PRD):** Users should be able to treat text, images, databases, and embeds identically — drag, reorder, nest.

**Implementation choice (by engineers):** Unified block model to satisfy that requirement.

**Why:** This inverts the typical order. The PM defined user behavior; the engineer chose the architecture. When Notion later expanded to databases, calendars, and AI blocks, the original PRD's behavioral definition ("everything is a block") made the extension obvious.

**Takeaway:** Requirements written around *behavior* rather than *implementation* tend to age better.

---

### Stripe — PRD rigor as a moat against complexity

**Headline:** Detailed narrative prevents edge-case disasters in high-stakes payments

**What:** Stripe treats PRDs as the primary artifact of product development. Every significant product decision requires a written narrative: problem, options considered, recommended approach, tradeoffs accepted.

**Case: Stripe Connect** (marketplace payments infrastructure)

| Dimension | Detail |
|-----------|--------|
| Complexity | Edge cases in money flow between platforms, connected accounts, end users |
| PRD length | ~40+ pages |
| Success metric | Became infrastructure for Lyft, DoorDash, Shopify payments |
| Why it worked | Edge cases handled correctly the first time—not discovered and patched in production |

**Takeaway:** PRD rigor prevents expensive post-launch fixes and makes your product the reliable choice for downstream customers.

---

### Atlassian Jira — Enterprise PRD structure

**Headline:** Enterprise B2B requires additional sections consumer PRDs omit

**Context:** Jira Cloud migration tool (moving customers from Jira Server → Cloud)

**Three enterprise-specific sections:**

#### 1. Security and compliance review

> **Requirement:** Features touching data residency, audit logging, and user permissions require security team sign-off *before* engineering begins.

**PRD includes:** Which security requirements apply and when the security review is scheduled.

#### 2. Customer implementation complexity

> **Requirement:** Enterprise features often require customers to configure, migrate, or train teams.

**PRD includes:** Estimated customer effort and support model definition.

**Example paths:**
- **Guided migration:** CSM-assisted, specific documentation requirements
- **Self-service:** Different documentation requirements

#### 3. SLA and incident scope

> **Requirement:** Enterprise contracts include uptime commitments. Any feature touching SLA-covered systems must define incident handling.

**PRD includes:** Incident severity levels, escalation paths for the new feature.

⚠️ **Risk:** Omitting these sections creates contractual and operational gaps that surface in the worst moments—during enterprise customer renewal conversations or high-severity incidents.

**Takeaway:** Consumer PRDs and enterprise PRDs are structurally different documents. One size does not fit all.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM, Ex-Engineer PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1 — What breaks and why

### Problem 1: PRD completeness creates false confidence

**The pattern:**
A detailed PRD signals thoroughness, but documentation completeness ≠ correctness of assumptions. Engineers ship a feature that meets every requirement but doesn't solve the actual user problem.

| What happens | Why it fails |
|---|---|
| PM writes detailed, complete PRD | Feels rigorous and thorough |
| Engineers build exactly what's specified | 6 weeks of work on validated requirements |
| Feature launches | ...but doesn't solve the real user problem |

**Prevention:**
- Treat the problem statement as a hypothesis until validated
- Add a **"Validation evidence"** field to every PRD
- Document: research, data, or customer conversations that justify this problem as real and important

---

### Problem 2: Dependencies undocumented are dependencies guaranteed to block

**The pattern:**
Cross-team dependencies discovered in the worst moment — usually the sprint before launch.

| Timeline | Discovery | Consequence |
|---|---|---|
| Week 1–4 | PRD written; engineering builds | No visibility into blockers |
| Week 5 | Data pipeline dependency emerges as unready | Launch slips; rework required |
| Root cause | PRD said "Data team will provide feed" with no owner, deadline, or fallback | Unmanaged risk |

**Prevention:**
For every dependency in the PRD, require three things:
1. **Owner:** Name of the team or person responsible
2. **Deadline:** Date the dependency is needed by
3. **Fallback plan:** What happens if it's delayed

---

### Problem 3: Out of scope sections that aren't enforced create technical debt

**The pattern:**
When engineers see "Arena tab — Coming Soon state only, full functionality out of scope," they architect around a stub. If a PM un-scopes mid-sprint without updating architecture, engineers retrofit their work.

⚠️ **Risk:** PRD out-of-scope commitments have downstream technical consequences. Adding something back into scope is never free.

**Prevention:**
- Treat out-of-scope decisions as architecture-level constraints
- Require PM approval + engineering sign-off before un-scoping
- Document the technical implications of each out-of-scope boundary

## S2 — How this connects to the bigger system

> **PRDs and user stories (05.04):** Different levels of abstraction. PRDs *contain* user stories but are not user stories.

| **User Stories** | **PRD Functional Requirements** |
|---|---|
| User perspective behavior | System behavior enabling that story |
| Example: "as a student, I want to see my upcoming class" | "Upcoming Class Reminder Card must display class number, lesson title, and Join button; appear at top of My Feed when class within 24 hours" |
| **When to use:** Capturing intent | **When to use:** Defining implementation |

**→ Understanding when to write at each level is a maturity marker in PM craft.**

---

> **PRD success metrics and North Star Metrics (06.01):** The same question asked at different granularity.

| **North Star Metric** | **PRD Success Metrics** |
|---|---|
| One metric capturing overall value delivery | Feature-level version of North Star question |
| Product-wide signal | Individual spec benchmark |

**The risk:** When PRD metrics don't connect upward to the North Star, you get features that hit their own targets but don't move the business.
- Features that increase click-through rate while reducing conversion
- Features that improve DAU while reducing revenue per user

**→ The best PMs trace every PRD metric to the next level up in the metric tree.**

---

> **Roadmapping (05.05) depends on PRD discipline.**

| **Pre-PRD Backlog** | **Specced Backlog** |
|---|---|
| Ideas without specs | PRDs written and reviewed |
| Planning cannot be confident | Planning accuracy improves dramatically |

**Reality check:** A roadmap without PRDs is a list of wishes. When engineering asks "how long will it take?", the only way to answer with confidence is to have a spec. Teams that maintain this two-tier backlog find that planning accuracy improves—not because estimation got better, but because the features being estimated are actually *defined*.

## S3 — What senior PMs debate

### Position A vs. Position B

| **Position A: Comprehensive PRDs First** | **Position B: PRDs Delay Learning** |
|---|---|
| Write full spec before any work begins | Ship with minimal spec, validate by building |
| Validate with engineers, designers, stakeholders | Requirements emerge through iteration |
| Rationale: Unclear requirements cause rework | Rationale: Specs lock in wrong assumptions |
| Claim: 1 hour on PRD saves 3 hours of rework | Claim: Shipping reveals if problem is right |
| | Examples: Notion, Figma, Slack shipped this way |

### The Genuine Tension

Both positions are describing **the same phenomenon at different stages of product maturity.**

- **Pre-product-market fit:** Comprehensive PRDs lock in wrong assumptions and slow iteration → Position B applies
- **Post-product-market fit:** Skimping on specs creates coordination failures at scale → Position A applies

**Senior PM behavior:** Apply Position B judgment early and Position A discipline late, and know which stage you're in.

---

### PRDs in AI-Native Product Development

> **AI-native feature property:** Not deterministic. Same input → different outputs across users.

**The problem with traditional PRDs:**
- Acceptance criterion designed for deterministic features: "the card must appear within 1 hour"
- Doesn't map to AI features: "the AI summary must be accurate"

**The solution:** Eval-based acceptance criteria
- Feature ships when it passes defined quality threshold on defined test set
- PRDs reference eval frameworks (04.06) as the mechanism for defining "done"

⚠️ **Senior PM risk:** Using a PRD template designed for traditional features on AI products is using a tool from a different era.

---

### The PRD-Less Culture as Management Failure

> **The function migration:** When teams stop writing PRDs formally, the PRD's function doesn't disappear — it moves into Slack conversations, verbal briefings, and unrecorded design reviews.

**The true cost:**
| **Formal PRD** | **"PRD-less" (actual costs)** |
|---|---|
| One document | PM re-explains requirements multiple times |
| Single source of truth | Across multiple channels |
| | Unrecorded conversations |
| | Higher total communication cost |

**What this reveals:** "We don't write PRDs" almost always means "we don't write PRDs formally" — not that requirements don't exist. Pushing toward documented requirements isn't bureaucracy; it's **multiplying force.**