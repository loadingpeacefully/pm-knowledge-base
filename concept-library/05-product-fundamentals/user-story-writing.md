---
lesson: User Story Writing
module: 05 — product-fundamentals
tags: product
difficulty: working
prereqs:
  - 05.01 — PRD Writing explains the document user stories live inside
  - 05.02 — Jobs to Be Done provides the "why" that user stories need to express
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/paid-joining-flow.md
  - technical-architecture/student-lifecycle/unified-demo-paid-experience-student.md
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

Imagine you're building a house and the only instructions you give the contractor are: "Build a nice kitchen."

What counts as nice? How many cabinets? Where does the stove go? Who decides if the countertop material changes halfway through? The contractor does their best, but six weeks later you walk in and find something technically functional but completely wrong for how you actually cook.

This is what product development looked like before user stories became standard practice. Engineers received requirement documents full of system behaviors: "The application shall display a countdown timer. The timer shall decrement by one second per interval. The button shall become enabled upon timer expiration." Perfectly precise — and completely disconnected from the person those features were supposed to serve.

When requirements were written in system language rather than human language, a few things reliably went wrong. Engineers built exactly what was specified, even when what was specified didn't match what users needed. Scope crept invisibly — one "small" addition looked like a trivial change in a requirements doc but turned out to be two weeks of engineering work. And no one knew when they were done, because "done" meant "shipped," not "working for the user."

User stories changed the starting point. Instead of describing what the system should do, they describe what a user needs to accomplish and why. Everything flows from there.

---

## F2 — What it is — definition + analogy

> **User Story:** A short description of a feature written from the perspective of the person who will use it.

**Classic format:**
```
As a [type of user],
I want to [do something],
so that [I get some benefit].
```

This three-part structure forces you to name:
- **Who** you're building for
- **What** they're trying to do
- **Why** it matters to them

Those three things are surprisingly hard to hold together—which is why the format exists.

---

### The Restaurant Order Analogy

| Element | User Story | Restaurant Order |
|---------|-----------|------------------|
| **Who requests** | User | Customer |
| **What they want** | Action/feature | Specific dish |
| **Why they want it** | Benefit | They're hungry for it |
| **Who fulfills it** | Engineering team | Kitchen |
| **What they receive** | User story | Order slip |

The kitchen figures out *how* to make it—you don't write the recipe. But the slip has to be specific enough that they don't bring out something completely different.

**Acceptance criteria** are like saying "No mayo"—not the whole recipe, but a condition the kitchen needs to know to prevent misunderstandings.

---

### The Three Parts, in Plain Terms

| Part | What It Does | Why It Matters |
|------|-------------|-----------------|
| **"As a…"** | Names the user—a specific type of person, not "the system" or "the app" | Keeps you focused on real humans, not abstract entities |
| **"I want to…"** | Describes the goal, not the feature itself | Separates what users need from how you might build it |
| **"So that…"** | Explains the benefit—where the value lives | If you can't answer this, you probably don't understand why you're building it |

## F3 — When you'll encounter this as a PM

User stories show up wherever features get planned and built. Here are the specific situations where you'll use them:

| **Context** | **What happens** | **Your role** |
|---|---|---|
| **Sprint planning and backlog grooming** | Engineering team organizes work in two-week sprint cycles. The backlog is written as user stories. | Read stories aloud or prepare them for the team to estimate and commit to. |
| **Handoff from strategy to execution** | Moving from "we should build this" to "here's what we need." | Write user stories as the bridge between product decision and engineering task. |
| **Stakeholder alignment** | Disagreements about feature priorities or scope. | Write the story together with stakeholders to reveal different assumptions about *who* the user is and *why* they need it. |
| **Defining "done"** | Team needs clarity on completion. | Write acceptance criteria that serve as the checklist for QA and the contract between PM and engineering. |

### Your daily responsibilities with user stories

- **Write** user stories to translate product decisions into work
- **Review** stories to catch unclear language or missing context
- **Push back** when stories lack detail or clarity
- **Explain** stories to stakeholders and the broader team
- **Scope** work by counting stories ("that's three stories, not one")
- **Prioritize** by communicating what matters most about each feature

⚠️ **Critical detail:** A user story without acceptance criteria is incomplete. "Done" means every acceptance criterion passes — not just that code was written.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The anatomy of a good user story

The three-part format is a starting point, not the destination. A complete, workable user story has several components:

**1. The story statement**
The standard format: "As a… I want to… so that…"

**2. Acceptance criteria**
The conditions that define when the story is done. Should be specific, testable, and written in plain language.

| ✅ Good | ❌ Bad |
|---|---|
| "When the teacher clicks Join Now before the 10-second countdown completes, the button is visually disabled and unclickable. After 10 seconds, the button becomes fully enabled. If the countdown is interrupted by a network error, a retry option appears." | "The button works correctly." |

**3. Out-of-scope notes**
Explicit callouts of what this story does NOT cover. If you don't write them, engineers (reasonably) interpret silence as inclusion.

**4. Dependencies**
Anything this story requires from another team or component to be complete. If the student dashboard requires a backend API from the data team, that's a dependency that needs naming.

---

### The INVEST criteria

| Criteria | What it means |
|---|---|
| **Independent** | Can be built and tested without requiring another story to be complete first |
| **Negotiable** | The story is a conversation, not a contract — details can change as you learn more |
| **Valuable** | Delivers something the user actually cares about |
| **Estimable** | The team can roughly size it (if they can't, it's probably too vague) |
| **Small** | Fits in a sprint — if it's too big, split it |
| **Testable** | Has acceptance criteria that can be verified |

> ⚠️ **Most common failure: Size.** PMs write epics thinking they're writing stories. "As a student, I want to complete my homework, so that I can practice what I learned in class" — that's an epic. It could take months to build, covers dozens of sub-features, and no team can estimate it. Break it into the smallest thing that delivers real value: "As a student, I want to see my pending homework assignments on my dashboard, so that I know what to do after class."

---

### Story hierarchy: from epic to task

| Level | Definition | Example |
|---|---|---|
| **Epic** | A large body of work covering a full capability area | "Student Dashboard" |
| **Feature** | A distinct capability within the epic | "Homework tracking" |
| **User story** | A single deliverable from the user's perspective | "View pending homework" |
| **Task** | A technical sub-step within the story | "Build GET /homework/pending API endpoint" |

**Your operating zone:** Features and stories  
**Engineers' zone:** Tasks  
**Executive zone:** Epics

> **Story splitting:** The transition from epic to story is a skill — you're looking for vertical slices (each slice delivers end-to-end value, even if limited) rather than horizontal slices (build the frontend, then the backend, then the database — nothing works until all three are done).

#### Vertical slice example: BrightChamps

**What:** Redesigning the teacher dashboard to improve class-start behavior.

**Instead of:** "Build the entire pre-class experience" (an epic)

**Split into:**

1. As a teacher, I want to see a Join Now button 10 minutes before my class starts, so that I can open the class without hunting for a link.
2. As a teacher, I want the Join Now button to have a 10-second countdown before it activates, so that I don't accidentally join before I'm ready.
3. As a teacher, I want to see a pre-class task list (maximum 3 items) prioritized by urgency, so that I know exactly what to do in the minutes before class.

**Why this works:** Each story delivers real value independently. Story 1 ships, teachers immediately benefit. Story 2 adds behavioral refinement. Story 3 adds the task-list capability. They can be sequenced, prioritized, or even cut — without breaking each other.

---

### Writing acceptance criteria that engineers can use

Good acceptance criteria anticipate edge cases before they become engineering debates. The discipline of writing them forces PM-engineer alignment before a single line of code is written.

#### Criterion template

| Component | What to do |
|---|---|
| **State** | Describe the initial condition ("When the teacher is in the 10-minute window before class start") |
| **Trigger** | What happens ("and clicks the Join Now button before the countdown completes") |
| **Expected behavior** | What the system does ("the button is disabled and shows remaining seconds") |
| **Edge case** | What happens when things go wrong ("if the class ID is not passed via the URL, the joining section is not shown at all") |

#### Real example: BrightChamps paid joining flow

> **Story:** As a teacher, I want to see a countdown before the Join Now button activates, so that I don't join prematurely.

**Acceptance criteria:**

- Timer begins counting down 10 seconds when the teacher enters the pre-class view
- Timer is visually displayed (countdown visible on screen)
- Join Now button is disabled and non-interactive until timer reaches 0
- At 0 seconds, button becomes fully enabled with full opacity and click interaction
- If the class start time has passed (teacher is late), timer is skipped and button is immediately enabled
- Timer state is local — refreshing the page restarts the countdown

## W2 — The decisions this forces

### Decision 1: How big should this story be?

The most frequent judgment call.

| Problem | Impact |
|---------|--------|
| Stories too big | Can't be estimated, won't fit in sprint, often ship incomplete |
| Stories too small | Create ceremony overhead with dozens of trivial tracking items |

**Calibration guide:**
- **More than one sprint (2 weeks)** → Almost certainly an epic
- **Within one sprint:** Depends on team size and context
  - 4-person startup, high shared context: 5–7 engineering days reasonable
  - 20-person team, parallel workstreams: 1–3 days needed for flow

> **The real signal:** One engineer can take the story from start to "demo-able" without pulling in others or waiting on external dependencies.

**Common trap:** If you can't get a rough estimate ("I have no idea how long that would take"), the story is almost certainly **too vague—not too big**.

**Recommendation:** When uncertain, split. 
- You can always combine two small stories in a sprint if related
- You can't easily split a story mid-sprint without renegotiating scope
- **Split test:** Can you write a passing acceptance criterion checklist for each half independently? If yes, they're separate stories.

---

### Decision 2: Who is the user in "As a user"?

> **The problem:** Generic users ("As a user…") are almost always wrong.

Your product has multiple user types with different goals and constraints:
- A teacher ≠ a student ≠ a parent
- Each has different motivations and constraints

Naming the right user type forces precision and often reveals you're trying to serve two different users with one story—a design problem, not a writing problem.

**Recommendation:** Always use the specific persona.
- ✓ "As a teacher..."
- ✓ "As a first-time trial student..."
- ✓ "As a parent reviewing their child's progress..."
- ✗ "As a user..."

If you can't decide which user the story is for, that's a product decision you haven't made yet.

---

### Decision 3: Should the acceptance criteria define the UI or just the behavior?

| Approach | Benefit | Risk |
|----------|---------|------|
| Specify UI details ("button turns gray, shows disabled cursor") | Clarity on exact look | Constrains designer unnecessarily |
| Specify only behavior ("button is unclickable before countdown") | Designer freedom | Engineers guess at appearance |

**Recommendation:** Define behavior, not visual appearance—unless the visual is load-bearing for UX.

> Use: "The button is visually disabled and non-interactive"

Exact color, opacity, and animation style belong in the design spec, not acceptance criteria.

---

### Decision 4: When do you write the story vs. when do you let engineering write it?

Both approaches work. What matters: **the PM reviews and approves before sprint entry**.

| Scenario | Who should write | Why |
|----------|-----------------|-----|
| High-stakes outcome | PM | You understand the "why" better |
| Complex user motivation | PM | You understand the "why" better |
| Technically complex work | Engineering | They understand the "how" better |
| Clear PM brief, known goal | Engineering | They understand the "how" better |

**Recommendation:** Always review before sprint commitment, regardless of who wrote it.

---

### Decision 5: What belongs in scope vs. out-of-scope?

Every story creates implicit scope questions.

**Example:** "As a teacher, I want to see a pre-class task list"

Unspecified scope includes:
- Ability to complete tasks from the list?
- Mark them done?
- Filter by type?
- Remove them?

⚠️ **If you don't answer these, engineers will answer them in code—and often choose wrong.** The fix takes more time than writing the out-of-scope note.

**Recommendation:** Write three to five explicit out-of-scope bullets for any story touching a complex feature area.
- Not comprehensive—just the things most likely to be assumed in scope
- Prevents rework and scope creep mid-sprint

## W3 — Questions to ask your engineer

**"What's the smallest version of this that you could ship and we'd learn something real from?"**

*What this reveals:* Whether there's a quicker path to validation. Engineers often see natural seams in the work that PMs miss.

---

**"Is there anything in the acceptance criteria that's ambiguous or contradictory?"**

*What this reveals:* Gaps in your own clarity. An engineer saying "I'm not sure what you mean by disabled" before building is far better than after.

---

**"What are the edge cases I haven't named?"**

*What this reveals:* Engineers spend most of their time on edge cases, not the happy path. Surfacing them before writing code lets you decide upfront whether they're in or out of scope for this story.

---

**"Does this story have any hidden dependencies I should know about?"**

*What this reveals:* Whether this story can actually be started in the next sprint. Sometimes a story that looks self-contained actually depends on an API that doesn't exist yet, a third-party service, or work another team is doing in parallel.

---

**"How would you test this?"**

*What this reveals:* The weakest links in how you've defined "done." If the engineer struggles to answer, the acceptance criteria are probably too vague.

---

**"Does this story overlap with anything else in the backlog?"**

*What this reveals:* Technical debt in your backlog and alignment gaps between team members. In large backlogs, duplicate or conflicting stories accumulate.

---

**"If we had to ship half this story, which half would you ship?"**

*What this reveals:* Whether the story has a natural vertical split. If the engineer can name a coherent half, you have an option to descope without wasting work if the sprint runs long.

## W4 — Real product examples

### BrightChamps — Teacher dashboard pre-class flow

**What:** Redesigned the teacher join experience from 3 screens to single-click join from a dashboard widget.

**Why:** Reduce missed-class incidents.

**Key structural decisions:**

| Element | Design | Why it matters |
|---------|--------|----------------|
| Join action | Single-click from widget | Reduced friction |
| Anti-accident protection | 10-second countdown | Prevents accidental joins |
| Task list scope | Capped at 3 items | Cognitive load management |
| Join window | T-10 to T+10 | Clear temporal boundary |

**Task priority ordering:**
1. Refund Retained
2. First Class
3. Attendance
4. Happy Moments
5. PTM
6. Installment/Renewals
7. Average Class Count
8. Homework/Assessments

**Takeaway:** Task list ordering encoded business policy (refund retention = highest financial value). Encoding this in acceptance criteria—not leaving it implicit—meant the priority logic survived beyond the original PM who specified it.

---

### BrightChamps — Student dashboard My Feed

**What:** Five card types in My Feed (class reminder, homework, completion, missed class, course explorer) as separate user stories.

**Why:** Modular scope allows parallel work and design independence.

**Critical scoping decision:**

> **Acceptance criteria scope:** What cards appear and in what order only. Visual styling explicitly out of scope.

Example of properly scoped criterion:
- ✓ "The class reminder card appears when there is a class scheduled within the next 24 hours"
- ✗ NOT "the card appears with a blue border and countdown timer"

Visual specifications lived in design files, not stories.

**Takeaway:** This separation freed frontend engineers to build data models and rendering logic without waiting for final designs.

---

### Atlassian Jira — Story writing for a tool used to write stories

**What:** Jira's team uses a "definition of ready" gate before sprint entry.

**Required before sprint:**
- [ ] User persona named
- [ ] Acceptance criteria written
- [ ] Out-of-scope list attached
- [ ] Design mockup linked (if UI-facing)

Stories failing the gate return to backlog.

**Result:**

| Responsibility | Clarity gained |
|---|---|
| Engineering | Meaningful commitment—only build what's specified |
| PM | Accountability for completeness before sprint start |
| Both | Scope disputes dropped significantly |

**Takeaway:** Out-of-scope lists made implicit assumptions explicit.

---

### Linear — Minimal story format for fast-moving teams

**What:** Compressed format = title + description + checklist (no formal "As a… I want… so that…" structure).

**When this works:**
- Small team with shared PM-engineering context
- PM can explain "why" verbally
- Stories are granular enough that benefit is obvious

**When the classic format scales better:**
- Team size exceeds ~15 people
- Onboarding engineers need written context
- External stakeholders must prioritize stories

**Takeaway:** Ceremony cost vs. clarity benefit shifts with team scale and async communication needs.

---

### Salesforce — Enterprise stories with compliance and integration acceptance criteria

**What:** B2B products require acceptance criteria categories rarely surfaced in consumer products.

⚠️ **Compliance acceptance criteria are non-negotiable.** They are contractual requirements negotiated during procurement, not nice-to-haves.

**Example: Bulk-export feature story**

| Criterion type | Example |
|---|---|
| Audit logging | "Export operation logged with user ID, timestamp, record count" |
| Permission enforcement | "Missing export permission hides button entirely—not disabled" |
| Compliance gates | "Exports containing PII trigger compliance review gate before download" |

**Takeaway:** Enterprise stories shipped without compliance criteria fail security reviews, not just miss features. Include compliance requirements from day one, not as afterthoughts during deals.

---

### GitHub Copilot — Writing user stories for AI features

**What:** AI features require acceptance criteria that specify quality thresholds and fallback behaviors, not deterministic pass/fail criteria.

⚠️ **"The suggestion is correct" is not testable.** AI acceptance criteria must define observable signals instead.

**Example: Code suggestion feature story**

| Criterion type | Example |
|---|---|
| Quality threshold | "In 500-Python-function benchmark, suggestions accepted ≥30% of the time (measured 2 weeks post-launch)" |
| Degradation path | "When confidence below threshold, no suggestion shown rather than low-confidence guess" |
| Performance gate | "Latency keystroke→suggestion <300ms at p95" |

**What this reveals:** Story-writing for AI requires an evaluation framework as the acceptance criteria, not a checklist.

**Takeaway:** AI feature "done" criteria shift from deterministic behavior to observable quality signals and acceptable degradation paths.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The "so that" clause is where value lives

**Problem:** Stories without "so that" ship features nobody wanted.

When teams skip the "so that" clause, they're writing technical tasks with a thin user wrapper. Consider this story:

> **Before:** "As a teacher, I want to see a task list on the dashboard"

The team optimizes for completeness. The user needed something different.

> **After:** "As a teacher, I want to see a task list on the dashboard, **so that I know exactly what to do in the 10 minutes before class**"

The "so that" is what makes the distinction actionable and reveals the actual need: prioritized clarity about immediate next steps.

**The cost:** PMs who let "so that" slide trade short-term writing speed for long-term direction drift.

---

### Acceptance criteria that are too strict prevent good engineering

| ❌ Overly Prescriptive | ✅ Behavior-Focused |
|---|---|
| "The button becomes enabled after exactly 10,000 milliseconds measured from page load" | "After 10 seconds visible to the user, the button is enabled" |
| Eliminates engineering judgment | Leaves room for better technical decisions |
| Engineer has no path to client-side timer, server-side event, or polling optimization | Engineer can choose the best approach |

> **Principle:** Describe observable user behavior, not implementation constraints.

PM's job: define the observable outcome  
Engineering's job: decide how to produce it

---

### Stories written in isolation create technical debt

**Pattern:** PM writes story → throws it over the wall → engineering builds exactly what was specified

**What this reveals:** Teams lack the dialogue loop that catches constraints early.

| Stage | Who | Action | Time |
|---|---|---|---|
| 1 | PM | Write draft story | 5 min |
| 2 | Engineer | Challenge assumptions; surface constraints | 7 min |
| 3 | PM + Engineer | Refine story together | 3 min |
| **Total** | — | — | **15 min** |

This 15-minute loop saves days of rework. Stories aren't mandates — they're hypotheses about what to build and why. The INVEST criteria include "negotiable" for this reason.

---

### Epic-level stories collapse sprints

**Signal:** Story commits to something that turns out to be an epic, ending the sprint half-shipped.

**Recognition signals (any one is a red flag):**
- Requires multiple design mockups
- Has more than 8 acceptance criteria  
- Multiple engineers need to touch it simultaneously

**Fix:** Split first, commit later.

## S2 — How this connects to the bigger system

> **User stories:** The atomic unit where product strategy becomes engineering commitment. The bridge between abstract roadmap items and specific buildable things.

### The JTBD–User Story Pair

| Element | Source | Function |
|---------|--------|----------|
| **Why** the user wants something | JTBD (05.02) | Functional, emotional, and social motivations |
| **What** to build | User story | Feature-level decision |

**The "so that" clause is where JTBD lives.** A JTBD lens prevents purely feature-based stories ("As a teacher, I want a countdown timer") by exposing the real motivation ("so that I don't accidentally join before I'm ready, which I've done three times and it embarrasses me in front of students").

### Prioritization: Stories → Estimates → Rankings

**Prioritization frameworks (RICE, ICE, opportunity scoring — 05.03) only work if stories are well-specified.**

```
Better stories 
  → Better estimates 
    → More accurate prioritization 
      → More reliable roadmaps
```

Vague stories produce garbage prioritization scores. This is a feedback loop with direct consequences for roadmap reliability.

### PRD vs. User Stories: Different Jobs

| Document | Answers | Use |
|-----------|---------|-----|
| **PRD** (05.01) | "Why are we building this?" | Strategy document: problem, audience, success metrics |
| **User story** | "What exactly should I build?" | Execution artifact: sprint tasks and acceptance criteria |

PRDs don't replace stories — they inform them.

### Acceptance Criteria → Technical Debt

**Ambiguous acceptance criteria force engineers to guess.** Stories with vague criteria lead to:
- Engineers making judgment calls with insufficient product context
- Code that passes QA but doesn't actually serve the user
- Rework and downstream technical debt

Precise acceptance criteria directly reduce the cost of engineering decisions made in the dark.

### Story Splitting → Release Velocity → Feedback Speed

| Story Type | Ship Frequency | Learning Cycle |
|------------|---|---|
| Epics disguised as stories | Quarterly | Slow feedback, high risk |
| Well-split vertical slices | Weekly | Fast feedback, learning-driven |

Smaller stories shipped faster means faster learning about what's actually working for users. This isn't just productivity — it's a feedback loop question.

## S3 — What senior PMs debate

### User stories: formal requirement or thinking tool?

| **Position** | **Argument** | **When it applies** |
|---|---|---|
| **Skip formal stories** | Ceremony overhead; one-paragraph briefs + conversation deliver the same outcome | 5-person startups with high PM-engineer trust and fast shipping |
| **Write formal stories** | Discipline of acceptance criteria forces edge-case thinking; format scaffolds your reasoning | Large teams, context gaps, compliance/audit requirements |

> **Senior PM consensus:** The format is a scaffold for thinking, not a bureaucratic requirement. Use it when it helps; compress it when it doesn't.

---

### Should acceptance criteria include "won't do" items?

| **Approach** | **Benefit** | **Cost** |
|---|---|---|
| **Explicit out-of-scope list** | Prevents scope creep; enables autonomous execution | Requires ongoing maintenance; stale lists create confusion |
| **Lightweight spec + async dialogue** | Faster to write; adapts to technical reality | Requires accessible PM; depends on communication tools working |

**Recent trend:** Toward lighter specs with richer verbal context. The formal out-of-scope list is giving way to "leave a comment in Linear and I'll answer within 24 hours."

---

### How AI is reshaping user stories

**Story quality becomes higher stakes**

AI coding tools (GitHub Copilot, Cursor) can generate working code from well-specified stories. Better stories → better AI output. PM precision is now a bottleneck on shipping speed.

**But stories are also becoming less pre-requisite**

Engineers with AI assistance can iterate rapidly without full upfront specification. Validation loop (try → show → refine) replaces some specification work.

**Forward-looking pattern emerging:**

1. PM writes story + acceptance criteria
2. AI generates first-pass implementation
3. PM evaluates output against criteria
4. Engineer refines

The story format doesn't disappear—it becomes the prompt.