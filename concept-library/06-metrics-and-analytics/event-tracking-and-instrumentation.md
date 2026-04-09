---
lesson: Event Tracking & Instrumentation
module: 06 — metrics and analytics
tags: product
difficulty: working
prereqs:
  - 06.01 — North Star Metric: understanding what you're trying to measure before deciding how
  - 05.07 — Experimentation & A/B Testing: events are the raw material for experiment analysis
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/paid-joining-flow.md
  - technical-architecture/student-lifecycle/student-feed.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, head of product, AI-native PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

In the early days of digital products, product managers measured success by counting. How many people signed up. How many pages were loaded. How many orders were placed. These numbers came from server logs — raw records of HTTP requests — and from databases that stored transactions.

The problem was that server logs told you *what happened*, not *what the user did*. You could see that a page was loaded 10,000 times. You couldn't see that 7,000 of those loads resulted in the user bouncing immediately, 2,000 led to a scroll halfway down, and only 1,000 led to the button click you cared about. The user's journey through your product was invisible.

When Netflix launched in 1997, they had no way to know which movies users started but didn't finish, or which genres drove repeat visits. When early e-commerce sites lost half their users on checkout page 3, they couldn't see *where* the dropout happened — only that orders didn't complete. Product teams were flying blind, optimizing guesses rather than observed behavior.

The solution was event tracking: deliberately instrumenting every meaningful user action, giving each action a name and a set of properties, and collecting that data so you could replay and understand what users actually did.

## F2 — What it is, and a way to think about it

> **Event tracking:** The practice of recording specific user actions in a digital product as discrete, named data points, each with associated properties that describe the context of the action.

> **Instrumentation:** The act of adding tracking code to a product so that events are captured when users perform actions.

> **Event:** A single recorded user action — a click, a view, a form submission, a video play — with a timestamp, a user identifier, and a set of properties describing what happened.

### A concrete way to think about it

Think of your product as a bank. A bank keeps a transaction ledger: every deposit, withdrawal, and transfer is recorded with the amount, the account, the time, and the counterparty. You can reconstruct any account's history from that ledger.

Event tracking is the same idea applied to user behavior. Every meaningful action a user takes is recorded as a "transaction" in a behavioral ledger:

| **Bank ledger** | **Event tracking equivalent** |
|---|---|
| Transaction type (deposit/withdrawal) | Event name (`button_clicked` / `class_joined` / `payment_completed`) |
| Account ID | User ID |
| Amount and currency | Event properties (`amount: 500`, `currency: INR`) |
| Timestamp | When the action occurred |
| Branch and teller | Platform and feature context |

**The key difference from server logs:** these records are **intentionally designed**, not incidental. Each event has a name a human chose, properties a product team specified, and a schema that other systems depend on.

> **Event schema:** The agreed-upon structure of an event — its name, which properties are required, and what format each property uses. Schemas are how teams ensure events are consistent and queryable.

## F3 — When you'll encounter this as a PM

| Context | What happens | Why it matters |
|---|---|---|
| **Feature spec writing** | Engineers need to know what to track before they build | Events not specced at build time require retroactive instrumentation — costly and often incomplete |
| **Experiment setup** | Every A/B test requires events to measure success | Without the right events firing, you can't know which variant won |
| **Analytics request** | BI team asks "what does this number mean?" | Inconsistent event naming or missing properties cause analysis to be wrong or impossible |
| **Bug investigation** | "Users are dropping at checkout" needs event data to diagnose | Without granular events, you can identify that there's a problem but not where |
| **Metrics reviews** | Dashboard shows a metric spike or drop | You need to trace the change to a specific event or event change to understand it |

### Company — BrightChamps

**Student Feed PRD**

**What:** Engagement signals (likes per session, replies per session, return visits) instrumented as events to prove habit formation.

**Why:** Without those events, the PM would know the feature launched but not whether it worked.

**Takeaway:** Engagement metrics must be defined and instrumented *before* launch to measure feature success.

---

**Paid Joining Flow**

**What:** Events tracking teacher preparation steps — 10-second review window completion, pre-class to-do visibility, join button clicks.

**Why:** Creates closed-loop accountability for whether the feature improves teacher preparedness.

**Takeaway:** Without granular event data, you can't prove whether a feature achieved its intended outcome.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The anatomy of an event

Every event has four required components and a variable set of properties:

| Component | What it is | Example |
|---|---|---|
| **Event name** | A string identifying the action | `class_joined`, `feed_post_liked`, `todo_shown` |
| **User ID** | Identifier linking the action to a user | `user_id: "u_98234"` |
| **Timestamp** | When the action occurred (UTC) | `2026-04-08T14:23:07Z` |
| **Session ID** | Links events within a single usage session | `session_id: "s_abc123"` |
| **Properties** | Additional context about the action | `class_id: "c_7781"`, `todo_type: "renewal"`, `platform: "web"` |

> **Properties:** Additional key-value pairs that give context to an event. Without them, you only know *that* an action happened. With them, you can answer *how*, *when*, *where*, and *why*.

**Why properties matter:** An event named `class_joined` without properties tells you a class join happened. With properties — `class_id`, `teacher_id`, `scheduled_time`, `join_latency_ms`, `todo_items_shown: 3` — you can answer:
- Did teachers join on time?
- Which to-do types were most common?
- Was there a join latency issue on mobile?

### Where tracking happens: client vs server

Events can be captured in two places, with different tradeoffs:

| Location | Mechanism | Strengths | Weaknesses |
|---|---|---|---|
| **Client-side** | JavaScript or SDK running in the user's browser or app | Captures UI interactions (clicks, scrolls, hovers), user experience context | Delivery rate varies significantly by product, platform, and user base (ad blockers, JS errors, network failures); not suitable as sole source for business-critical metrics |
| **Server-side** | Backend emits event when action completes | Authoritative (can't be blocked or faked), reliable for transactional events | No UI context; doesn't capture failed or partial user attempts |

**The hybrid approach most products use:** Server-side events for high-stakes business actions (payment_completed, class_booking_confirmed), client-side events for behavioral signals (scroll_depth_50, button_hover, session_time).

### Company — BrightChamps

**What:** Paid joining flow uses server-side events for the class join itself (authoritative) but benefits from client-side tracking for the 10-second cooldown interaction.

**Why:** Server-side alone can't answer whether the teacher actually read the to-do items or just waited.

**Takeaway:** Hybrid tracking captures both transactional certainty and behavioral intent.

### The instrumentation pipeline

Events travel through a pipeline before becoming queryable:

1. **Capture** — SDK or server code fires the event when action occurs
2. **Queue** — Events are buffered locally to avoid blocking the UI
3. **Transport** — Events sent to collection endpoint (Segment, Amplitude, Mixpanel, or custom)
4. **Validation** — Events checked against schema (correct format, required fields present)
5. **Enrichment** — Additional properties appended server-side (user segment, account tier, A/B variant)
6. **Storage** — Events land in data warehouse (BigQuery, Snowflake, Redshift) or analytics platform
7. **Query** — Product, data, and engineering teams query events for analysis

⚠️ **Where events break:** Steps 4 (invalid schema) and 5 (missing enrichment) are the most common failure points in growing companies. Silent failures here mean broken dashboards downstream.

### Event naming conventions

Inconsistent event names are one of the biggest sources of analytics debt. Standard conventions:

| Convention | Example | Reasoning |
|---|---|---|
| `object_action` format | `class_joined`, `feed_post_liked` | Consistent prefix groups related events in queries |
| snake_case | `payment_completed` not `PaymentCompleted` | Consistency across team naming |
| Past tense for completed actions | `class_joined` not `join_class` | Confirms the action happened, not that it was attempted |
| Present tense for states | `page_viewed`, `modal_opened` | Describes what the user experienced |

⚠️ **The naming debt trap:** If one team calls it `class_joined` and another calls it `ClassJoin` and a third calls it `join_class`, you now have three event names for the same action. Queries break. Dashboards diverge. Analysis requires manual deduplication. Prevent this from day one with a naming standard document enforced at code review.

## W2 — The decisions this forces

### Decision 1: Client-side vs server-side tracking as your default

The choice affects data reliability, coverage, and engineering effort. Neither is universally right.

| Factor | Client-side default | Server-side default |
|---|---|---|
| **Use case** | User experience analytics, feature adoption | Transactional metrics, billing, compliance |
| **Reliability** | Variable — ad blockers, JS errors, and network issues cause drops; consumer products in high-ad-blocker markets (desktop Europe) can see 20–40% event loss | ~99.9% (server controls emission) |
| **UI context** | Rich (button text, scroll position, viewport) | None (only what the backend knows) |
| **PM effort** | Higher: PM must spec every UI interaction | Lower: backend events often exist already |
| **Trust for decisions** | Good for behavioral questions | Required for business/financial questions |

**Recommendation:** Use server-side as the authoritative source for anything that touches money, compliance, or business reporting. Use client-side for behavioral signals, UX optimization, and feature adoption. Don't use client-side-only for metrics that will be presented to investors or executives.

---

### Decision 2: What to track vs what to skip

The instinct is to track everything. The result is an event explosion that becomes unqueryable.

**Framework for what's worth tracking:**

| Track this | Skip this |
|---|---|
| Actions that represent value delivery (class completed, goal reached, subscription renewed) | Passive exposures that don't represent intent (every page scroll, every mouse movement) |
| Steps in a critical funnel where drop-off matters | Mid-session ephemeral states (scroll position mid-read) |
| Actions that feed A/B test success metrics | Redundant events that duplicate server-side data |
| Error and failure states at key steps | Low-stakes UI interactions with no decision value |

**Recommendation:** For every proposed event, ask: "What decision will we make differently if this event fires 10% more or less often?" If the answer is "none," skip the event.

**Company — BrightChamps**
- **What:** Disciplined event scoping in the paid joining flow
- **Why:** Tracks meaningful decision points (teacher saw to-do items, 10-second timer completed, join button clicked) while skipping noise (pixel scrolls on profile page)
- **Takeaway:** Value lives in intentional action events, not passive exposure

---

### Decision 3: How granular should event properties be?

Event properties are where the real analytical value lives — but over-engineering them creates schema complexity.

| Property level | Approach | Risk |
|---|---|---|
| **Too sparse** | `event: class_joined` with no properties | Can't slice by class type, teacher, time-to-join, or platform |
| **Right density** | Core business context in 5–10 properties | Queryable for most decisions; manageable schema |
| **Too dense** | 40+ properties per event | Schema maintenance burden; most properties never queried |

**Standard properties to always include:**
- `user_id`
- `session_id`
- `timestamp`
- `platform` (web/iOS/Android)
- `feature_version` (which release the user is on)
- `A/B variant` (if enrolled in an experiment)

**Context properties to add per event:**

Properties that answer "what were the specific conditions of this action?" 

*Example from BrightChamps's `todo_shown` event:*
- `todo_count` — how many were shown
- `todo_types[]` — which types appeared
- `class_time_to_start_min` — how far away was the class

---

### Decision 4: When to spec events — build time vs retroactive

This is the decision that separates high-functioning PM teams from everyone else.

| Approach | What it means | Cost |
|---|---|---|
| **Build-time spec** | PM includes event spec in the PRD/ticket before engineering builds | Zero extra cost; events are natural part of implementation |
| **Retroactive instrumentation** | Events added after the feature is live | 2–4x engineering time; may require rebuilding UI flows; backfill of historical data rarely possible |

**Why retroactive is so expensive:**
- The engineer who built the feature has moved on
- The UI components may not expose the properties needed
- Server-side enrichment might not be available for past events
- You'll have a permanent gap in historical data that limits cohort analysis on early adopters

**Recommendation:** Every PRD or ticket that ships user-facing code should include an **"Event spec"** section containing:
- Event name
- Trigger condition
- Required properties
- What success metric or analysis it enables

This is PM responsibility — not analytics, not engineering.

---

### Decision 5: Privacy and consent for user-level tracking

⚠️ Events that contain user-identifying information require explicit handling.

| Data type | Requirement | PM responsibility |
|---|---|---|
| Device fingerprints | GDPR: requires consent in EU | Ensure consent framework includes tracking consent |
| User behavior on logged-in paths | Generally permissible with ToS | Verify ToS covers behavioral analytics |
| Health or financial behavior | Special category under GDPR/CCPA | Requires explicit opt-in; data minimization required |
| Children's usage (COPPA) | Strict limits on data collection for under-13 | For edtech: verify age gates and COPPA compliance apply |

**Company — BrightChamps**
- **What:** Student (child) behavior tracking: class attendance, homework completion, feed engagement
- **Why:** Falls under COPPA in the US and equivalent laws globally
- **Takeaway:** Design events to aggregate at the parent-account level for advertising purposes; avoid individually identifiable child behavioral data beyond what the product requires

## W3 — Questions to ask your engineer

| Question | Why Ask | What This Reveals |
|----------|---------|-------------------|
| **"What events are currently firing on [feature X], and can you show me a sample event payload?"** | Forces confirmation that tracking exists and lets you verify properties match your needs. Half the time, events exist but have missing or wrong properties. | Whether your instrumentation is actually capturing what you think it is. A sample payload is worth more than any verbal confirmation. |
| **"What's the event delivery rate? How often do events fail to reach the pipeline?"** | Client-side events are not 100% reliable. Ad blockers, network failures, and JS errors cause drops. | Whether your analytics are based on complete data or a systematically filtered sample. A 20% event drop rate on mobile means every mobile funnel analysis is off by 20%. |
| **"How long does it take from a user action to that event appearing in the data warehouse?"** | Latency affects how quickly you can act on data during experiments or incidents. Some pipelines process in minutes; others run nightly batch jobs with 24-hour latency. | Whether you can use event data for real-time decisions (experiment monitoring, incident response) or only for retrospective analysis. |
| **"Do we have a schema registry? How do we manage event versioning when properties change?"** | When properties are renamed, removed, or restructured, old queries break. A schema registry and versioning protocol prevent analytics from silently breaking. | Schema maturity. Teams without a schema registry often have divergent event definitions across mobile, web, and backend — which surfaces as inconsistent metrics across dashboards. |
| **"How are PII fields handled in events? Are user emails, names, or IDs hashed or masked?"** | Events containing raw PII create compliance liability when stored in data warehouses or sent to third-party analytics tools. | Whether your event data is safe to share with external analytics vendors. This is particularly important for edtech handling minor students' data. |
| **"Can we backfill events for past user actions if we discover we're missing something?"** | If you realize a critical event was never instrumented, can you reconstruct past occurrences from server logs or database records? For transactional events often yes; for UI interactions almost never. | Your recovery options when you discover a tracking gap. If backfill isn't possible, every day without the event is data permanently lost. |
| **"Are events being enriched with A/B variant information automatically?"** | For experiment analysis, every event needs to carry which variant the user was in. If this enrichment happens inconsistently, experiment results will be mixed and uninterpretable. | Experiment infrastructure maturity. Teams without automatic variant enrichment have to manually join experiment assignment tables to event tables — which works but is fragile. |
| **"What analytics tooling do we have, and what's the difference between our real-time dashboard and our warehouse-based analysis?"** | Most companies have two tiers: a fast dashboard (Mixpanel, Amplitude, Segment) for day-to-day metrics, and a slower warehouse (BigQuery + Looker/Metabase) for deep analysis. They often show different numbers due to different event sources. | Which source to trust for which question, and why the CEO's Amplitude dashboard might differ from the data team's SQL query. |

⚠️ **PII Handling Risk:** Raw PII in event properties (names, emails, unencrypted user IDs) creates compliance liability under GDPR, CCPA, FERPA, and other regulations. Always verify that sensitive fields are hashed or masked before events leave your system.

## W4 — Real product examples

### BrightChamps — Paid Joining Flow: building accountability through events

**What:** The Paid Joining Flow intercepts teachers before they enter Zoom classrooms, redirecting them to a student profile with pre-class to-do items (renewals, attendance issues, refund discussions). A 10-second cooldown timer enforces a minimum review window.

**The event spec challenge:** Without explicit events, the product team can track whether teachers clicked "Join" — but not whether they actually reviewed the pre-class context. The feature's core hypothesis (teacher preparedness improves outcomes) requires finer instrumentation:

| Event | Properties | What it proves |
|---|---|---|
| `pre_class_review_started` | `class_id`, `teacher_id`, `todo_count`, `todo_types[]` | Teacher arrived at the student profile page |
| `todo_timer_completed` | `class_id`, `time_spent_sec` | Teacher waited through the 10-second window (vs. switching tabs immediately) |
| `class_joined` | `class_id`, `join_latency_from_timer_ms`, `todos_visible` | Teacher actually entered the classroom |

**Why this matters:** Without `todo_timer_completed`, you can't distinguish teachers who completed the forced review from those who opened the page in one tab and immediately switched to another. The event is what makes the feature measurable.

**Outcome:** These events enable closed-loop analysis — comparing renewal rates, attendance rates, and class ratings for teachers who completed the review vs. those who didn't.

---

### BrightChamps — Student Feed: instrumenting engagement signals

**What:** The Student Feed (auto-generated class cards, achievement posts, homework reminders) was designed to increase daily return visits beyond class attendance. The PRD explicitly defines the events needed to prove it works.

**Defined engagement signals:**
- Likes per session
- Replies per session
- Return visits to feed page

**Why this is strong PM practice:** The engagement signals were defined *in the PRD*, not after launch. This means:
- Engineering had a clear spec
- Analytics had a schema expectation
- PM had a pre-committed success criterion (not retroactively finding metrics that looked good)

**What it enabled:**
- A/B testing the feed (enabled vs. control) with clear success criteria
- Session-level analysis of which content types drove the most engagement
- Detection of students who returned to the feed but didn't engage (passive scroll vs. active like/reply)

---

### Segment — the event pipeline infrastructure layer

**What:** Segment is a Customer Data Platform (CDP) that acts as a single event ingestion layer, routing events to downstream tools (Amplitude for product analytics, Salesforce for CRM, BigQuery for warehousing).

**Why it matters for PMs:** Instead of engineering wiring events to 5 different tools separately, they fire events once into Segment, and Segment handles the routing.

**PM implications:**
- Adding a new analytics tool doesn't require re-instrumentation
- Event naming conventions become critical (they affect every downstream system simultaneously)
- Schema changes in Segment propagate everywhere — including breaking dashboards

**The instrumentation model it enables:** PMs can add new downstream tools (a new A/B testing platform, a new CRM) without asking engineering to re-instrument anything.

⚠️ **The tradeoff:** Segment becomes a single point of failure and a cost center proportional to event volume.

---

### Amplitude — session replay for instrumentation gaps

**What:** Session replay tools (Amplitude, FullStory, Hotjar) record actual user sessions as video-like replays — every click, scroll, and UI state.

**Why it matters:** When events haven't been instrumented for a UI interaction, session replay can provide qualitative evidence while you wait for proper instrumentation. A PM who sees 40% of users hovering over a disabled button has evidence that the button's state is confusing, even without a formal `button_hover_on_disabled` event.

**The limitation:** Session replay is retrospective and qualitative. It can identify problems but can't produce statistical measurements. It's a bridge to proper instrumentation, not a replacement for it.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### Schema rot

Events are designed once and accumulate over years without cleanup. The result is schema rot: a data warehouse filled with hundreds of event types, many of which have been renamed, abandoned, or duplicated by different teams.

**The failure pattern:**

| Version | Event Name | Team | Problem |
|---------|-----------|------|---------|
| v1 | `class_started` | Core | Original event |
| v1.5 (6mo) | `class_joined` | Mobile | Same action, new name |
| v2 (1yr) | `ClassBegin` | Contractor | Duplicates previous events |

**Result:** All three events coexist. Which one is canonical? Answer depends on which team you ask.

> **Schema rot:** A data warehouse filled with hundreds of event types, many renamed, abandoned, or duplicated by different teams—making analysis unreliable without tribal knowledge.

**Downstream damage:**
- New team members make wrong decisions (no canonical source)
- Dashboards built on one event break when usage shifts to another
- Analysis requires undocumented institutional knowledge

**PM prevention role:**
- Establish a naming authority and event registry **before the team exceeds 5 engineers**
- Enforce naming conventions in the PRD process
- Rule: If an event name isn't in the registry, it doesn't ship

---

### Instrumentation debt compounding

Every feature shipped without a proper event spec creates technical debt that compounds. Each untracked user action becomes a permanent blind spot. Retroactive instrumentation is expensive, historically incomplete, and often technically impossible for UI-level events.

**The compounding mechanism:**

A product with 50 features, each 80% instrumented:
- 10 features where behavior is essentially invisible
- Gaps prevent cohort analysis across feature boundaries
- Gaps prevent funnel analysis spanning multiple features
- Attribution of behavioral changes to releases becomes impossible

> **Instrumentation debt:** Untracked user actions that become permanent blind spots, impossible to retroactively instrument for UI-level events.

---

### The "event explosion" anti-pattern

The opposite of instrumentation debt: teams that track everything produce petabytes of undifferentiated data that nobody queries.

**Event explosions occur when:**
- Tracking is added without business questions attached
- Frontend SDKs are configured to autocapture all DOM interactions
- Teams add tracking "just in case" without schema governance

**Cost of explosion:**

| Impact | Cost |
|--------|------|
| Data warehouse storage | $50K+/month |
| Dashboard load time | 4+ minutes |
| Signal-to-noise ratio | Analysts cannot find actionable insights |

⚠️ **Risk:** Ungovernance data collection produces cost and complexity without analytical value.

## S2 — How this connects to the bigger system

| Concept | Dependency | How events enable it |
|---|---|---|
| **Funnel Analysis (06.02)** | Funnels require step-by-step events to calculate conversion | No events at each step = no funnel; wrong events = wrong conversion rates |
| **Cohort Analysis (06.03)** | Cohorts are built from first-occurrence events (first_class_completed, first_payment) | Cohort definition depends entirely on event accuracy and completeness |
| **Experimentation & A/B Testing (05.07)** | Every experiment needs a success metric — which is an event count or rate | Poorly designed events make experiment results uninterpretable |
| **Feature Flags (03.10)** | Feature flag systems emit events when users are assigned variants | Variant attribution must be appended to all downstream events automatically |
| **North Star Metric (06.01)** | North star metrics are typically aggregations of core events | If the north star event is wrong or inconsistently defined, the metric is wrong |
| **Data Quality & Pipelines (06.10)** | Events flow through ETL pipelines before landing in warehouses | Pipeline failures cause event loss; schema mismatches cause silent corruption |

### The dependency that breaks everything: retroactive analysis

⚠️ **Critical risk:** Senior PMs discover this when they want to understand behavior before a new feature launched — to compare pre/post, or to understand the baseline. If events weren't instrumented before launch, there's no pre-period data. The A/B test or feature analysis starts from zero.

**Why this matters:** By the time you want the data, it's too late to instrument it retroactively. Event specs in the PRD aren't optional — they're your only chance to capture the baseline.

## S3 — What senior PMs debate

### "Is event tracking PM responsibility or data engineering responsibility?"

The debate is real and consequential. Three camps:

| **Ownership Model** | **How It Works** | **Core Problem** |
|---|---|---|
| **Data engineering owns tracking** | Engineers spec and implement events based on technical needs. PMs query what exists. | Events designed for technical completeness, not business questions. PMs get data that doesn't map to their hypotheses. |
| **Analytics owns tracking** | Analytics/BI team designs the schema after features ship. | Retroactive instrumentation is expensive and incomplete. The team that knows business questions isn't involved until it's too late to do it cheaply. |
| **PM owns the event spec** | PM includes event specification in every PRD and ticket. Engineering implements the spec. Analytics validates. | Requires PMs to develop schema design skills and tracking discipline that most PM curricula don't teach. |

**Current industry consensus:** PM ownership of the event spec with data engineering governance of the schema registry. The PM defines *what* needs to be measured; the data team defines *how* it must be structured.

---

### "Real-time analytics vs warehouse-based analysis — which should PMs design for?"

| **Approach** | **Tools** | **Strengths** | **Constraints** |
|---|---|---|---|
| **Real-time analytics** | Amplitude, Mixpanel, Segment | Fast, visual, no SQL required | Expensive at scale; can't do complex joins; opaque data models |
| **Warehouse-based analysis** | BigQuery + Looker | Authoritative, cheap at scale, answers any question | Slower, requires SQL or BI tools |

**The tension:** Real-time tools require events designed for their data model (e.g., Amplitude's user/event schema). Warehouse-first approaches require events designed for SQL queryability. These constraints sometimes produce incompatible event designs.

> **What AI is changing:** AI-assisted SQL and natural language query interfaces (embedded in Amplitude and Looker in 2024–2025) are collapsing this distinction. PMs who previously needed real-time tools for low-SQL-fluency are increasingly able to query warehouses with natural language. This makes warehouse-first event design more viable for non-technical PMs — which has significant implications for how event schemas should be designed going forward.

---

### "What does LLM-native product instrumentation look like?"

Traditional event tracking assumes discrete user actions: clicks, form submissions, page views. **LLM-powered products are fundamentally different** — the "action" is a conversation, and the value is often in what the AI returned, not just what the user clicked.

**New instrumentation categories most products haven't standardized yet:**

- > **Response quality events:** Was the AI's answer rated helpful or unhelpful?

- > **Conversation abandonment:** Did the user stop mid-conversation? At what turn?

- > **Regeneration events:** Did the user ask the AI to regenerate — a proxy for dissatisfaction?

- > **Downstream conversion:** Did the conversation lead to the business outcome?

**Example — BrightChamps edtech AI tutoring:**

### BrightChamps — Capturing conversation value, not just presence

**What:** AI tutoring features (TrialBuddy, Bright Buddy) require instrumentation that captures conversation-level value, not session presence.

**Why:** A student who asked the AI 5 questions and received 5 wrong answers registers as "engaged" by traditional DAU metrics but experienced negative value.

**Takeaway:** Events must capture the quality dimension, not just the presence dimension.