---
lesson: Sales Pipeline Integration
module: 08 — gtm and growth
tags: product
difficulty: working
prereqs:
  - 08.11 — CRM Fundamentals: this lesson assumes you understand how CRM data flows and how records are structured; read CRM Fundamentals first
  - 08.07 — Paid Acquisition Fundamentals: pipeline decisions depend on where leads come from and their unit economics
  - 06.02 — Funnel Analysis: a sales pipeline is a structured funnel; funnel analysis techniques apply to stage conversion rates
  - 02.03 — Transactions & ACID: event-driven sale flow (SQS, webhooks, atomic payment callbacks) requires distributed transaction grounding
writer: gtm-lead
qa_panel: GTM Lead, CFO/Finance Lead, Senior PM
kb_sources:
  - technical-architecture/crm-and-sales/sales-flow.md
  - technical-architecture/crm-and-sales/renewal-crm.md
profiles:
  foundation:
    - (see 08.11 CRM Fundamentals for Foundation-level content)
  working:
    - Growth PM
    - Consumer Startup PM
    - B2B Enterprise PM
  strategic:
    - Ex-Engineer PM
    - Senior PM
    - Head of Product
status: draft
last_qa: 2026-04-11
split: lesson_b
continues_from: 08.11 — CRM Fundamentals
---
# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — See 08.11 CRM Fundamentals

This lesson is the second half of a split. For the world before CRM existed, how sales tracking worked without it, and why PMs must care about the system, read [08.11 CRM Fundamentals](crm-fundamentals.md) first — it covers the Foundation-level context this lesson assumes.

## F2 — What it is

CRM (Customer Relationship Management) software records every interaction between a company and its customers, and a sales pipeline is the set of stages customers move through from first contact to purchase. Full definitions (lead, deal, qualification, pipeline velocity, hot lead) are in [08.11 CRM Fundamentals](crm-fundamentals.md).

## F3 — When you'll encounter this as a PM

08.11 CRM Fundamentals covers the four encounter points: building product events that feed the CRM, analyzing conversion problems, designing renewal flows, and prioritizing backlog against sales requests. This lesson (08.12) covers what the PM must decide and build once CRM is running — the pipeline integration layer that sits on top of those fundamentals.

# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

> **Before this lesson:** This is the second half of CRM & Sales Pipeline. It covers the decisions, engineering questions, and real examples that assume you already understand the mechanism. If you haven't read [08.11 CRM Fundamentals](crm-fundamentals.md), start there — it covers how CRM data flows, which the decisions below assume.

## W2 — The decisions this forces

### Decision 1: Pipeline stage granularity

More pipeline stages = more visibility into where deals are stuck. Fewer stages = simpler operations for the sales team.

| Approach | Benefit | Risk |
|----------|---------|------|
| **Too many stages** | Maximum visibility | Sales managers spend time updating CRM instead of selling; stage transitions become admin overhead that gets skipped; pipeline data becomes stale |
| **Too few stages** | Simpler operations | Can't identify where deals get stuck; broad categories obscure bottlenecks (e.g., "In Progress" masks whether payment conversation happened) |

### Company — BrightChamps renewal pipeline

**What:** 7-stage pipeline (Renewal Pending → Parent Contacted → Appointment Scheduled → Pitching Done → On Hold → Interested → Closed Won/Lost) with 14–30 day sales process.

**Why:** Each stage has distinct action requirements; PM can identify exactly where conversion breaks.

**Takeaway:** Pipeline stages should be defined by observable actions, not time passage or judgment calls.

> **Design principle:** Define pipeline stages based on the actions they require, not the passage of time. "Parent Contacted" requires first contact; "Appointment Scheduled" requires a time commitment. Stage transitions should be triggered by observable actions, not SM judgment about relationship status.

---

### Decision 2: Automation vs. human judgment in pipeline management

| Decision Point | Automate | Require Human Judgment |
|---|---|---|
| **Lead/deal creation** | ✓ Lambda-triggered on technical events | — |
| **Stage transitions** | ✓ Payment received, class completed | ✓ Renewal pitch, objection handling, interest qualification |
| **Timing of payment ask** | — | ✓ Context-dependent |
| **Pipeline closure** | ✓ Technical events | ✓ Complex stalled deals |

**Automation benefits:** Reduces manual work, prevents delays from follow-up latency.

⚠️ **Risk of over-automation:**
BrightChamps's renewal trigger fires when credits ≤ 6. For online 1:1 classes, 6 credits is meaningful runway. But for a 30-class package with slow consumption (1 class/week), 6 credits = 6 weeks remaining — plenty of time for outreach. The automation doesn't differentiate by consumption rate.

**PM decision needed:** Should the renewal trigger be time-based (subscription ending in N days) rather than credit-based alone?

---

### Decision 3: How to instrument CRM for product decisions

The CRM is a data source for product decisions only if the right events are captured.

**What's captured vs. what's missing:**

| What's captured | What's missing |
|---|---|
| SM knows how to reach parent | Demo satisfaction scores |
| — | Specific features student engaged with during class |
| — | Trial attendance rate |

**The insight:** If the PM captured demo satisfaction and feature engagement, the sales team could segment outreach ("parents whose child completed all 3 demo tasks have 40% higher conversion").

> **PM framework:** Every conversion event in the sales pipeline has a product-side trigger. Map those triggers to CRM fields and test whether high-value product behaviors correlate with higher pipeline conversion rates. If yes: that's a sales enablement tool AND a product signal that the feature drives revenue.

---

### Decision 4: Renewal timing — when to trigger outreach

The renewal trigger timing is one of the highest-leverage PM decisions in the retention stack.

| Trigger timing | Problem |
|---|---|
| Too early (30+ days before end) | Parent doesn't feel urgency |
| Too late (3 days before end) | Insufficient time for sales conversation to conclude |

**BrightChamps uses two triggers:**

1. **Credits ≤ 6:** Immediate renewal lead when balance drops
   - Time-independent
   - Fires when student has used most credits

2. **Subscription ending in 30 days:** Fires regardless of credit balance
   - Catches students with unused credits on vacation or poor attendance

> **Testable hypothesis:** The 30-day subscription window directly affects renewal rate. A/B test different windows (45 days vs. 30 days vs. 21 days) to measure Closed Won rate impact. Does earlier triggering help because SMs get more time? Or does later triggering work better because parents feel urgency?

```markdown
## W3 — Questions to ask your engineering team

### Quick Reference: Critical Questions by Risk Area

| Area | Question | Why It Matters |
|------|----------|----------------|
| **Data Coverage** | Q1: Event triggers | Silent churn from incomplete automation |
| **Reliability** | Q2: API failures & retries | Deal stage stuck indefinitely |
| **Concurrency** | Q3: Lead claiming conflicts | Revenue impact from ownership disputes |
| **Deduplication** | Q4: Renewal lead logic | Risk of duplicate lead flooding |
| **Latency** | Q5: Demo → deal timing | SM ability to act on hot leads |
| **Testing** | Q6: Test coverage & status | Fragility of revenue-critical paths |
| **Multi-course** | Q7: Lead per course handling | SM workflow clarity for multi-course parents |
| **Rate limits** | Q8: API throttling at scale | Peak processing bottlenecks |

---

### Q1: Event trigger coverage

**The Question**  
"What events trigger CRM lead and deal creation — and are there any product events that don't trigger a CRM update?"

*What this reveals:* Whether the CRM automation has gaps (new class types not covered, edge case class completions not handled).

**Why this matters**  
Missing event coverage means silent churn — students or leads falling out of the pipeline without the sales team knowing.

---

### Q2: API failure handling

**The Question**  
"What happens when a Zoho CRM API call fails — is there a retry mechanism, and do we alert on failures?"

*What this reveals:* The reliability of the sales pipeline data.

⚠️ **Known Issue**
BrightChamps's technical debt includes no documented retry on Zoho upsert failure. A failed CRM update means the deal is stuck at the wrong stage indefinitely.

---

### Q3: Concurrent lead claiming

**The Question**  
"How does the hot lead routing system handle concurrent claims — can two SMs claim the same lead simultaneously?"

*What this reveals:* Whether concurrency protection is correctly implemented.

**Why this matters**  
Concurrency issues in sales systems create deal ownership conflicts with direct revenue impact.

> **Test case validation:** BrightChamps documentation mentions "two SMs claim simultaneously — only first succeeds." Confirm this is implemented correctly as a product quality issue.

---

### Q4: Renewal lead deduplication

**The Question**  
"What is the deduplication logic for renewal leads — and what happens when a student triggers multiple renewal conditions simultaneously (credits ≤ 6 AND subscription ending in 30 days)?"

*What this reveals:* Whether duplicate lead flooding is a risk.

> **Deduplication Key:** Student × Course × Class Type × Cycle Count

**Expected behavior:** If both triggers fire for the same student in the same cycle, only one renewal lead should be created.

---

### Q5: Demo-to-deal latency

**The Question**  
"What is the current latency between a demo completing and the CRM deal being created — and what's the P95 latency?"

*What this reveals:* Tail latency — occasionally slow updates that affect outreach timing.

**Why this matters**

| Impact | Detail |
|--------|--------|
| **High latency (> 5 min)** | SMs can't act on hot leads immediately |
| **Latency path** | Teacher feedback → SNS → Prabandhan SQS → Lambda → Zoho upsert |
| **P95 metric** | Captures the slowest 5% of updates, revealing real-world impact |

---

### Q6: Sales pipeline test coverage

**The Question**  
"Are there automated tests for the sales pipeline event chain — and when did the tests last pass?"

*What this reveals:* The fragility of this critical revenue path.

⚠️ **Risk**
Complex async event chains (SNS → SQS → Lambda → CRM) are easy to break with infrastructure changes. A Lambda timeout or Zoho API schema change could silently break deal creation for days.

---

### Q7: Multi-course renewal leads

**The Question**  
"How does the renewal CRM handle a student with multiple active courses — and does each course get its own renewal lead?"

*What this reveals:* Whether SMs understand their lead structure for complex accounts.

> **Design Pattern:** Renewal CRM uses "Student × Course" as part of the unique key → separate renewal leads per course

**Implication:** An SM working a multi-course student may have 3 renewal leads for the same parent. This is correct for tracking but requires the SM to understand they're managing the same parent across multiple leads.

---

### Q8: Zoho API rate limits at scale

**The Question**  
"What is our Zoho CRM API rate limit — and what happens during peak renewal processing (end-of-month bulk triggers)?"

*What this reveals:* Bottlenecks during peak processing that delay lead distribution.

⚠️ **Known Bottleneck: Thundering Herd**

| Factor | Detail |
|--------|--------|
| **Trigger time** | Renewal cron runs at 07:50 UTC |
| **Batch size** | Processes all students with subscriptions ending in 30 days simultaneously |
| **Example volume** | 500 students trigger at once = 500 Zoho API calls |
| **Rate limit constraint** | If Zoho rate limit is 100 calls/minute, batch takes 5 minutes minimum |
| **Result** | SMs don't receive renewal leads until the queue clears |
```

## W4 — Real product examples

### BrightChamps — event-driven sales pipeline

**What:** Sales pipeline driven by product events rather than manual data entry, with automated triggers across acquisition and renewal flows.

**Architecture overview:**

| Pipeline | Trigger | Flow |
|----------|---------|------|
| **Acquisition** | Demo booking | Tryouts INSERT → SQS → Eklavya → Prabandhan → Zoho Lead (Not Contacted) |
| | Demo feedback | SNS → Prabandhan SQS → Lambda → Zoho Deal (Demo Completed) |
| | Hot lead API | Prabandhan → Slack → SM claim → Deal owner updated |
| | Payment callback | Eklavya → SQS → Prabandhan → Zoho Deal (Closed Won) |
| **Renewal** | Credit threshold | FIFO SQS queue (ordered, non-duplicated processing) |

**PM-owned design decisions:**

| Decision | BrightChamps Choice | Rationale |
|----------|-------------------|-----------|
| Renewal trigger threshold | ≤ 6 credits | (not ≤ 3 or ≤ 10) |
| Subscription window | 30 days before end | (not 14 or 45) |
| Hot lead routing | First-claim in Slack | (not skill-based routing) |
| Deduplication | Composite key prevents duplicates | Renewal lead integrity |

**Technical debt with revenue impact:**

⚠️ **Missing retry logic on Zoho upsert failure** — Failed CRM updates mean missing pipeline data and incomplete revenue visibility.

⚠️ **No distributed tracing across multi-service sales flow** — Pipeline diagnosis requires significant engineering investigation when systems break.

*What this reveals:* Infrastructure quality directly impacts pipeline data integrity. The PM should prioritize these as revenue-impacting investments, not infrastructure-only work.

---

### Salesforce — the CRM that became a platform

**What:** Cloud-based CRM (launched 1999) that evolved from sales pipeline tool into $35B revenue platform spanning CRM, marketing automation, analytics, and AI.

> **The PM lesson:** CRM data is the foundation for a platform, not just a sales tool.

When every customer interaction is structured and queryable, you unlock:

- **Automated workflows** — triggered by pipeline stage changes
- **Analytics & forecasting** — pipeline velocity, win rates
- **AI recommendations** — lead prioritization, messaging
- **Business integrations** — every downstream tool

**Revenue intelligence questions enabled:**

- Which course vertical has the highest Closed Won rate?
- Which SM has the highest conversion rate for hot leads?
- Which renewal window produces the highest Closed Won rate?

*What this reveals:* CRM design is not a sales-only problem — it's the data substrate for all revenue product decisions.

---

### HubSpot — CRM designed for product-led sales

**What:** CRM built for inbound, product-led motion where free users' product behavior automatically feeds lead scoring.

**The product-usage-in-CRM design:**

| User Action | Trigger | CRM Signal |
|-------------|---------|-----------|
| Creates 5th contact | Automatic | Lead score increases |
| Builds first email campaign | Automatic | Lead score increases |
| Engages with feature X | Product behavior | Sales notification |

> **Product-qualified lead (PQL):** Automatic lead scoring based on product engagement signals rather than demographics. Sales teams see signal-based engagement, not just demographic data.

**BrightChamps parallel:**

**Current state:** Teacher manually flags hot leads based on classroom engagement judgment.

**Opportunity:** Automatic lead scoring from student engagement data:
- Attendance rate
- Homework completion  
- Quiz scores
- Showcase creation

High-engagement students become hot leads automatically. Human judgment stays but scales through data.

*What this reveals:* The most scalable sales engines replace manual judgment with product behavior signals.

---

### Renewal CRM failure: the silent churn problem

**What:** Renewal trigger fires → lead created in CRM → no SM claims it → lead sits at "Renewal Pending" → subscription expires → student churns silently.

> **The mechanism:** Renewal leads compete for SM attention with acquisition leads (treated as higher priority). Constrained capacity = unclaimed renewal leads = system generates data but process fails to convert it to action.

**Detection signal:**

⚠️ **Monitor:** "Renewal Pending" age — leads at this stage for > N days with zero activity (no call, note, or stage update).

**Key metric to track:** Median days-in-stage per pipeline stage with alert thresholds.

**PM prevention approaches:**

| Approach | Mechanism |
|----------|-----------|
| **SLA-based alerts** | If renewal lead > 3 business days unclaimed → automated alert fires |
| **Auto-escalation** | Unclaimed leads escalate to team lead after N days |
| **Ownership clarity** | Renewal CRM only produces revenue if leads are worked, not just tracked |

*What this reveals:* Pipeline health is not about data generation — it's about process execution. The PM owns ensuring leads convert to action, not just data.

---

### Conversion benchmarks — what good looks like

| Stage transition | B2C edtech / consumer | B2B SaaS | What moves it |
|---|---|---|---|
| **Lead → Demo (or first meeting)** | 20–40% | 10–25% | Outreach speed, lead quality, messaging fit |
| **Demo → Paid (or closed won)** | 15–30% | 15–30% | Demo quality, objection handling, payment friction |
| **Lead → Closed Won (end-to-end)** | 5–12% | 3–10% | Product-market fit, sales execution, pricing |
| **Renewal rate** | 60–80% (consumer) | 80–95% (B2B) | Product value, relationship quality, renewal outreach timing |

> **PM calibration:** If your demo-to-paid conversion is below 15% in a B2C flow, the product experience during the demo is the most likely culprit — not the sales team. If renewal rate is below 60% in a consumer product, retention mechanics need investigation before investing in more renewal leads.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The pipeline stage inflation problem

Sales teams discover that pipeline stage advancement affects their visibility with management. A deal that sits at "Demo Completed" for two weeks looks stale. Moving it to "Appointment Scheduled" looks like progress — even if no appointment was actually scheduled. Pipeline stages become aspirational rather than factual.

**The mechanism:**

| Problem | Root Cause | Impact |
|---------|-----------|--------|
| Stage data depends on SM self-reporting | No automated stage transitions | SMs incentivized to report optimistic stages |
| Pipeline inflation | Weak visibility controls | Forecast misses surprise management |
| 30-day stale deals marked "Interested" fail to close | Aspirational rather than factual stages | Deal quality assessment breaks |

> **Pipeline Stage Inflation:** The practice of advancing deals to later stages without observable business events occurring, driven by structural incentives to show progress to management.

**The PM's design response:**

- **Automate every stage transition that can be automated.** For BrightChamps: payment link sent → "Payment Requested" (automated when SM clicks "Send Payment Link"). Payment confirmed → "Closed Won" (automated via payment callback). These stages can't be manually inflated because they're triggered by product actions, not SM input.

- **Add activity requirements for judgment-based stages.** For stages that require human judgment (Parent Contacted, Pitching Done), require logged activities before stage advancement is allowed. A "Pitching Done" stage should require at least one logged call in the CRM before the transition is permitted. This prevents rubber-stamping.

---

### The Zoho API fragility under load

BrightChamps's renewal CRM processes all 30-day-ending subscriptions in a single daily batch at 07:50 UTC. If 500 students trigger simultaneously, the SQS queue fills with 500 messages.

**Current bottleneck:**

The `processRenewalCrmLead` consumer makes five sequential external API calls per message:
- Eklavya
- Paathshala
- Dronacharya
- Currency conversion
- Zoho upsert

At 500 leads: **2,500 API calls in a short burst.** Zoho CRM has rate limits. If calls exceed the limit, they fail or queue. FIFO SQS ensures ordering, but slow processing means SMs don't receive their renewal leads until the queue clears — potentially hours after the 07:50 cron fires.

**PM design options (prioritized by impact):**

| Option | Implementation | Impact | Risk |
|--------|---|--------|------|
| **Parallelize API calls** | Call Eklavya, Paathshala, Dronacharya simultaneously instead of sequentially | Reduces per-message processing time by ~2/3 | Low — calls are independent |
| **Spread the cron trigger** | Distribute processing across 4-hour window (7:50 AM–11:50 AM UTC) | Reduces peak SQS message volume | Medium — requires scheduling logic |
| **Cache currency conversion rates** | 24-hour TTL on Platform currency conversion | Eliminates one expensive API call per lead | Low — rates don't change meaningfully within 24h |

**Recommendation:** Prioritize option 1 (parallel API calls) as the highest-leverage improvement with low implementation risk.

---

### The multi-CRM fragmentation problem

BrightChamps uses Zoho CRM via Prabandhan microservice, with activity tracking from four different dialer integrations:
- Call Hippo
- Air Call
- Maqsam
- Knowlarity

Each dialer has its own integration for auto-syncing call activities to the CRM. When a new dialer is added or an existing integration breaks, call activities may not sync — leaving CRM activity history incomplete.

⚠️ **Data integrity risk:** An SM who completed 10 calls to a parent may have only 3 logged in Zoho if their dialer integration was broken during the other 7 calls. This breaks:
- Management metrics on call activity
- Coaching based on CRM activity logs (incomplete data)
- Attribution of relationship-building to the SM before Closed Won

> **Multi-CRM Fragmentation:** Loss of data completeness across systems when integrations between multiple dialers and a CRM become unsynced or partially functional.

**The PM's structural response:**

Implement **quarterly audits** of dialer integration completeness. The BrightChamps technical debt note flags: "Activity sync for Maqsam/Knowlarity may not be uniformly implemented across all dialer integrations."

**Audit process:**
- Sample SMs across all dialer systems
- Compare call count from dialer system logs vs. Zoho CRM
- Systematic discrepancy indicates integration failure
- Trigger investigation and remediation

## S2 — How this connects to the bigger system

### System connections at a glance

| Concept | Connection |
|---|---|
| **Paid Acquisition Fundamentals (08.07)** | Paid acquisition generates leads that enter the sales pipeline. Pipeline conversion rates (lead-to-demo, demo-to-paid) translate ad spend into revenue. Improving pipeline conversion is functionally equivalent to reducing CAC. |
| **Funnel Analysis (06.02)** | A CRM pipeline is a structured sales funnel. Funnel analysis techniques (stage-by-stage conversion rates, drop-off diagnosis, cohort comparison) apply directly. The PM uses funnel analysis on pipeline data to identify where conversion is breaking. |
| **Churn & Retention Economics (07.07)** | The renewal pipeline is the operational layer of retention. Renewal CRM lead creation, SM outreach velocity, and Closed Won rates directly determine renewal rate. Poor renewal CRM operations are a churn driver. |
| **Queues & Message Brokers (03.06)** | BrightChamps's sales pipeline is event-driven via SQS/SNS. Understanding queue semantics (FIFO ordering, dead-letter queues, visibility timeouts) is required to design reliable CRM automation. |
| **Transactions & ACID (02.03)** | Payment callbacks that update both the product database (credits) and the CRM (deal stage) in an atomic sequence require understanding distributed transaction patterns. If one update succeeds and the other fails, the product and CRM are inconsistent. |
| **ETL Pipelines (02.06)** | The Marketing ETL and the CRM data can be joined to answer the full acquisition question: which channel → which lead → which SM → which deal → which Closed Won. This cross-dataset join enables true channel-to-revenue attribution. |

### CRM as the P&L bridge

> **P&L Bridge:** The CRM connects marketing metrics (impressions, clicks, CPL) to revenue metrics (deals, ARR, LTV), making it the system where product impact becomes measurable as revenue impact.

**Why this matters for growth PMs:**

For a PM working on growth, the CRM is the system that makes the question **"did this product change increase revenue?"** answerable. Without it, revenue impact of product investments is invisible.

### Real-world scenario: Demo experience improvement

**The investment:** BrightChamps ships a new demo experience (richer teacher tools, more engaging student content).

**The measurable outcome in CRM data:**
- Demo-to-paid conversion: 20% → 25%
- Ratio of "Closed Won" deals to "Demo Completed" leads improves

**Why it matters:** Without clean CRM instrumentation, this signal is lost entirely.

### The PM case for instrumentation

Every significant product investment should have a measurable CRM outcome hypothesis.

**Example hypothesis:**
> *"We expect this feature to improve demo-to-paid conversion by 5 percentage points, which at current demo volume generates X additional Closed Won deals per month."*

Without CRM data, this hypothesis cannot be tested or proven.

## S3 — What senior PMs debate

### Build vs. buy for CRM infrastructure

| Dimension | Build (Custom Middleware) | Buy (Native CRM Tools) |
|-----------|---------------------------|----------------------|
| **Example** | BrightChamps' Prabandhan (custom microservice on Zoho) | Zoho Flow/Deluge scripting or integration platforms (Zapier, Make, Workato) |
| **Flexibility** | High — custom pipeline stages, product event integration | Medium — limited to CRM's native capabilities |
| **Engineering cost** | High upfront + ongoing maintenance burden | Low — outsourced to vendor |
| **Scalability challenge** | Maintenance cost grows with scale | Maintenance cost stays flat |

**When to build:**
- Workflow is deeply product-specific (acquisition stages triggered by product events, not standard lead stages)
- Custom service bridging product event language + CRM API is more maintainable than complex native scripting
- Team has engineers comfortable in the chosen CRM's scripting language (e.g., Zoho Deluge)
- Strategic direction aligns with event-driven architecture (Prabandhan becomes a natural fit)

**When to buy:**
- Native CRM automation can handle 80%+ of workflow
- Engineering hours are better spent on product than on CRM middleware maintenance
- Team lacks specialized CRM scripting expertise

> **The senior PM's judgment:** depends on three variables — team composition, workflow complexity (e.g., async SQS chains), and strategic direction (event-driven product architecture).

---

### AI and the future of sales pipeline management

**Two ways AI is transforming CRM:**

1. **Operational efficiency** — automatically summarize calls, suggest next actions, draft follow-ups (reduces manual CRM overhead)
2. **Predictive accuracy** — AI-driven lead scoring and close probability outperforms rule-based systems

#### EdTech example

### EdTech — AI engagement scoring

**What:** AI listens to demo class recordings and automatically scores parent engagement (sentiment analysis, questions asked, voice enthusiasm) → replaces/augments teacher's manual "hot lead" flag

**Why:** Removes subjective judgment → improves lead prioritization

**Takeaway:** Automation handles volume while improving consistency

---

**The emerging debate:**

| Task Type | Best Handled By | Why |
|-----------|-----------------|-----|
| Tier-1 outreach (automated messages, scheduling, objection responses) | AI | Scales efficiently |
| Complex conversations (renewal objections, progress concerns) | Humans | Requires genuine engagement |
| Highest-trust conversations ("Is this program working for my child?") | Humans | Automation degrades relationship |

⚠️ **EdTech risk:** Automating high-trust conversations erodes parent confidence and increases churn.

---

### Renewal rate as a product metric vs. a sales metric

**The common disagreement:**

*If a student churns, whose fault is it?*

- **Product view:** Product didn't deliver enough value → product failure
- **Sales view:** Sales didn't work the renewal lead effectively → sales execution failure

> **The reality:** Both drive renewal. The measurement should reflect this.

**Product-driven renewal factors:**
- Class quality
- Teacher consistency
- Student engagement
- Perceived learning outcomes

**Sales-driven renewal factors:**
- Renewal lead response time
- Sales manager pitch quality
- Objection handling
- Payment friction

**How to instrument both:**

For each churned renewal, track in parallel:

| Data Source | Metrics to Track |
|-------------|------------------|
| **Product engagement** | Class attendance (last 30 days), showcase creation, homework completion |
| **CRM sales activity** | Days between renewal lead creation + first contact, call volume, stage stall time |

*What this reveals:* The pattern shows which side of the renewal equation is the primary driver — directing investment accordingly.