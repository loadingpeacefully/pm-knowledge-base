---
lesson: CRM Fundamentals
module: 08 — gtm and growth
tags: product
difficulty: foundation
prereqs:
  - 08.07 — Paid Acquisition Fundamentals: leads from paid acquisition enter the CRM pipeline; fundamentals assume you understand where leads originate
writer: gtm-lead
qa_panel: GTM Lead, Junior PM Reader, Staff Engineer
kb_sources:
  - technical-architecture/crm-and-sales/sales-flow.md
  - technical-architecture/crm-and-sales/renewal-crm.md
profiles:
  foundation:
    - Non-technical Business PM
    - Aspiring PM
    - Designer PM
    - MBA PM
  working:
    - Growth PM
    - Consumer Startup PM
    - B2B Enterprise PM
status: draft
last_qa: 2026-04-11
split: lesson_a
continues_in: 08.12 — Sales Pipeline Integration
---
# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

Before CRM software, sales teams tracked their prospects in spreadsheets, notebooks, and their own memory. A salesperson knew their pipeline — who they were talking to, where each conversation was, who was close to buying — but that knowledge lived entirely in their head and their notes. When the salesperson left the company, the pipeline left with them.

This created two persistent problems. First, the company had no visibility into the sales process: a manager couldn't see how many deals were in the pipeline, which stage they were at, or which salesperson was going to hit their number. Second, when deals fell through or salespeople left, the institutional knowledge about those relationships was lost. The next person starting a conversation with a prospect would often be starting from scratch, unaware that a colleague had already built a relationship and made progress.

CRM (Customer Relationship Management) software was designed to solve both problems. A CRM is a system that records and tracks every interaction between a company and its potential or existing customers. Every email, every call, every meeting, every step in the sales process — it's all logged. The pipeline becomes visible to the whole team, not just the individual salesperson.

For product managers, the CRM can seem like a sales team's tool — not product's problem. This is a costly misconception. PMs design the product events that feed the CRM (demo completion, payment, class attendance), and PMs are accountable for product changes that affect conversion rates tracked in the CRM. If a PM changes the demo experience and demo-to-paid conversion drops from 25% to 18%, the CRM data will reveal it — but only if the PM ensured the pipeline stages and events were properly instrumented in the first place. The CRM is not invisible to PMs. It's the system that makes revenue impact of product decisions visible.

## F2 — What it is, and a way to think about it

> **CRM (Customer Relationship Management):** A software system that records and tracks customer interactions, relationships, and status through a defined sales or service process.
>
> *Examples: Zoho CRM (used by BrightChamps), Salesforce, HubSpot*

> **Sales pipeline:** The set of stages that a potential customer moves through from first contact to purchase. Each stage represents where the customer is in their decision-making process.

> **Lead:** A potential customer who has shown initial interest but hasn't been fully qualified or engaged in a sales conversation.
>
> *Example: A parent who books a demo class at BrightChamps is a lead — they've expressed interest but haven't yet paid.*

> **Qualification:** The process of confirming a lead is worth pursuing — the sales team has verified the prospect has a genuine need, real budget, and decision-making authority. Unqualified leads waste sales capacity; over-qualifying loses real buyers.

> **Deal (or Opportunity):** A potential sale from a lead who has been qualified and is actively being worked by a sales representative.
>
> *Example: After a demo is completed at BrightChamps, the lead is converted to a deal — the sales manager now works to close it.*

> **Pipeline stages:** The named steps through which deals progress.

### BrightChamps Pipeline Examples

| Pipeline | Stages |
|----------|--------|
| **New Acquisition** | Lead Not Contacted → Demo Completed → [Hot Lead → SM Assigned] → Payment Initiated → Closed Won |
| **Renewal** | Renewal Pending → Parent Contacted → Appointment Scheduled → Pitching Done → On Hold → Interested → Closed Won / Closed Lost |

> **Pipeline velocity:** How quickly deals move through the pipeline from first stage to close.
>
> *A deal that takes 2 days to close vs. one that takes 45 days have very different implications for revenue forecasting and sales team capacity.*

### Mental Model: CRM Pipeline as an Airport Security Queue

Think of a CRM pipeline like an airport security queue:

| Queue Element | CRM Equivalent |
|---------------|---|
| Passengers entering at check-in | Leads (first contact) |
| Moving through security | Qualification and demo |
| Reaching boarding | Payment |
| Boarding the plane | Closed Won |
| Missing their flight | Closed Lost |

**What the airport monitors:**
- How many passengers at each stage
- How quickly they're moving
- Where the bottlenecks are

**How this works in practice:**

When the security line backs up (demo-to-payment conversion is slow), the airport can:
- Add lanes (hire more sales managers)
- Change the process (redesign payment flow)

**The key insight:** The CRM is the system that makes the queue visible.

## F3 — When you'll encounter this as a PM

### Building product events that feed the CRM

Every key product moment — a teacher submitting demo feedback, a parent completing payment, a student finishing a class — can automatically update the CRM. Behind the scenes, the product system sends a **signal** (an automated data message triggered by a user action) to the CRM when these moments happen. The PM who designs what happens at demo completion or payment is indirectly deciding what data enters the CRM.

> **Signal:** An automated data message triggered by a user action that flows from the product system to the CRM.

#### BrightChamps — Automatic deal creation from product events

**What:** When a teacher submits demo class feedback, the product system automatically creates a deal in the CRM — no manual entry needed.

**Why:** Real-time, automatic deal creation keeps the sales pipeline synchronized with what's actually happening in the product.

**Takeaway:** If you add a new class type without updating the deal creation logic, new-class demos won't create deals — the CRM goes silent and you've created a sales data gap. The PM who designs a new product flow is also responsible for the CRM update that flow must trigger.

### Analyzing conversion problems

If demo-to-paid conversion drops, the PM and sales team both need to diagnose whether the problem is product-side or sales-side:

| Problem Origin | Signal | Data Source |
|---|---|---|
| **Product-side** | Poor demo quality, weak product experience | Product analytics |
| **Sales-side** | Slow follow-up, weak messaging | CRM pipeline data |

**Key insight:** Combining both data sources tells the full story.

### Designing renewal flows

#### BrightChamps — Renewal leads from product triggers

**What:** Automatic renewal lead creation in Zoho CRM when a student's class balance drops to ≤ 6 credits.

**Why:** Product-driven trigger ensures no renewal opportunity is missed.

**Takeaway:** As the PM designing the renewal trigger, lead creation logic, and stage definitions, you're directly designing the renewal sales team's workflow.

### Prioritizing backlog against sales requests

Sales teams routinely request product changes to improve conversion rates — better demo follow-up tools, automated reminders, improved payment flows.

| Request Type | Example | Evaluation Lens |
|---|---|---|
| **Product-adjacent with clear ROI** | Add in-product payment link to demo class chat | +5% demo-to-paid conversion = revenue-driving investment |

**Your role:** Evaluate these requests against product metrics and prioritize them like any other revenue-driving product investment.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Pipeline stages and why they matter

> **Pipeline stage:** A specific state of the customer relationship that triggers specific actions by the sales team.

A well-defined pipeline ensures stages are:

| Characteristic | What it means |
|---|---|
| **Mutually exclusive** | A deal is in exactly one stage at a time |
| **Sequentially ordered** | Deals advance forward (occasionally backward) through defined transitions |
| **Action-linked** | Each stage transition triggers specific follow-up actions (call, email, payment request) |
| **Conversion-tracked** | The percentage of deals that advance from each stage is the conversion rate for that transition |

#### BrightChamps new-acquisition pipeline

| Stage | Trigger | Action required | Success condition |
|---|---|---|---|
| Lead: Not Contacted | Demo booked | Initial outreach (WhatsApp + email from Hermes) | Demo completed |
| Deal: Demo Completed | Teacher submits feedback via SNS | Teacher flags hot/warm/cold; SM claims hot lead | SM qualifies and initiates payment conversation |
| Hot Lead claimed | Teacher marks hotlead; SM claims via Slack | SM begins active sales conversation | Payment initiated |
| Payment initiated | SM sends payment link | Parent processes payment via aggregator | Payment callback received |
| Deal: Closed Won | Payment callback → CRM closure | Welcome onboarding, curriculum provisioning | Student starts classes |

#### BrightChamps renewal pipeline

| Stage | Meaning | Trigger | Action |
|---|---|---|---|
| Renewal Pending | Lead auto-created; not yet contacted | Credits ≤ 6 or subscription ending in 30 days | SM contacts parent |
| Parent Contacted | First contact made | SM call/WhatsApp | Schedule appointment |
| Appointment Scheduled | Call/meeting booked | SM books time slot | Conduct renewal pitch |
| Pitching Done | Renewal conversation had | SM updates after call | Follow up on objections |
| On Hold | Parent undecided | SM updates | Re-engage in X days |
| Interested | Parent expressed intent to renew | SM updates | Send payment link |
| Closed Won | Payment received | Payment callback | Invoice, curriculum extension |
| Closed Lost | Parent decided not to renew | SM updates | Churn analysis, win-back later |

**Why the difference?** The renewal pipeline is more complex than the acquisition pipeline because renewal requires active selling — the parent isn't coming in fresh with curiosity, they're making a deliberate decision to reinvest. The stages reflect the multi-touch outbound process.

---

### CRM automation and event-driven triggers

> **Event-driven trigger:** An observable product event (demo completed, payment received, class started) that automatically updates CRM stage, not manual human entry.

In any product, automatic CRM updates require a set of internal systems with clear ownership over specific product events. When a demo is completed, some system must be responsible for telling the CRM. When a payment is processed, another system must close the deal. Every stage transition should be triggered by a product event, not by a sales manager remembering to update a field.

#### BrightChamps system ownership map

| System | Responsibility |
|---|---|
| **Eklavya** | Student bookings and class management |
| **Prabandhan** | Lead and CRM management (bridge between product events and Zoho) |
| **Paathshala** | Class content and session data |
| **Dronacharya** | Teacher management |
| **Hermes** | Outbound messaging (WhatsApp, email) |

In Salesforce or HubSpot, the equivalent is your backend application calling the CRM API directly (or via a middleware like Zapier, Workato, or a custom integration). The names differ; the pattern is identical: product event → API call → CRM record updated.

> **What to map in your system:** For each key product event (account created, purchase completed, class attended, subscription renewed), ask: Does this event create or update a CRM record? Which service owns that handoff? What happens if that service fails silently?

#### Acquisition flow

```
Demo booked → Tryouts bookings table INSERT
  → SQS → Eklavya mapStudenWithBooking Lambda
  → Prabandhan: POST /lead/create-db-crm-lead
  → Zoho: Lead created (Not Contacted)
  → Hermes: WhatsApp + Email confirmations

Teacher submits feedback → SNS published
  → Prabandhan SQS → Lambda
  → Zoho: Lead converted to Deal (Demo Completed)
  → Optional: Teacher marks hotlead → Slack → SM claims deal

Payment webhook → Eklavya /payment-callback
  → sale_payments = 'paid', credits updated
  → SQS → Invoice generation
  → SQS → Onboard flow → CRM: Closed Won
```

#### Renewal flow

```
Credits ≤ 6 → updateClassBalanceV2 → SQS queue
       OR
Daily cron at 07:50 UTC (subscription ending in 30 days) → SQS queue

→ processRenewalCrmLead consumer:
   → Fetch student data (Eklavya)
   → Fetch class data (Paathshala)
   → Fetch teacher data (Dronacharya)
   → Currency conversion (Platform service)
   → Zoho upsert: Renewal lead (Renewal Pending) OR Closed Won (fresh payment)
```

#### What this reveals for PMs

**Every step is a PM decision.** The choice to trigger renewal leads at ≤ 6 credits (not ≤ 10 or ≤ 3) is a PM decision. The choice to use a daily cron at 07:50 UTC vs. a real-time trigger for subscription-ending is a product architecture decision with implications for renewal outreach timeliness (batch daily vs. immediate). When the PM changes the subscription model, the renewal trigger conditions must be updated.

---

### CRM data quality — what the PM owns

> **CRM data quality:** A product quality problem. The data is only as good as the events that feed it.

#### Missing trigger coverage

If BrightChamps adds a new class type (e.g., group online classes) and the renewal trigger logic only handles `online` and `online-group` class balances, group class students won't generate renewal leads. The sales team doesn't know these students are churning — the CRM is silent.

#### Duplicate lead creation

If the same parent books two demos (for two children), or books and cancels and re-books, the lead deduplication logic must handle these cases. BrightChamps's renewal CRM uses a composite key (`Student * Course * Class Type * Cycle Count`) to prevent duplicate leads per renewal cycle. Poor deduplication floods the CRM with duplicate leads, overwhelming sales managers.

#### Stage transition logic errors

⚠️ **Silent Zoho upsert failures:** If a Zoho API call fails (rate limit, network timeout), the deal stays at the wrong stage indefinitely. The sales manager sees "Demo Completed" but the deal should be "Hot Lead." BrightChamps's technical debt includes: "No documented retry on Zoho upsert failure."

**PM-owned improvement:** Add a dead-letter queue and alert for failed CRM updates.

#### Hardcoded mapping problems

The Marketing ETL uses hardcoded CASE statements for channel classification. A similar problem exists in the renewal CRM: if a new course vertical is added but the renewal trigger query doesn't include it, students in that vertical won't get renewal leads.

**PM audit required:** New product additions must be reflected in CRM automation logic.

#### PM ownership — 3 non-negotiable CRM data quality checks

1. **New feature audit:** Every time you ship a feature that creates a new product event or flow, verify CRM automation explicitly covers it before launch.
2. **Monthly sample audit:** Pull 20 closed deals and check that stage progressions match expected triggers. Systematic gaps indicate broken automations.
3. **Conversion drop hypothesis:** When conversion metrics drop unexpectedly, CRM data quality is always a hypothesis — ask: Are leads being created? Are stages advancing? Is a webhook silently failing?

---

### Hot lead mechanics — PM-designed prioritization

> **Hot lead system:** A product-designed prioritization mechanism where teachers flag demo outcomes and sales managers race to claim high-intent leads.

After a demo, the teacher submits feedback indicating whether the lead is "hot" (high purchase intent), "warm," or "cold." A hot lead is posted via API, routed to a Slack channel, and the first sales manager who claims it gets the deal.

#### Conversion implications of this design

| Design element | Impact | Consideration |
|---|---|---|
| **Teacher judgment quality** | How well-calibrated are teachers at identifying hot vs. warm leads? | A teacher who marks every lead as hot floods the channel; one who marks too few leaves high-intent parents unworked. |
| **SM response time** | The first SM to claim a hot lead gets it. | Creates speed incentives (good) but also gaming risk (SMs gaming the queue rather than focusing on existing deals). |
| **Routing fairness** | Experienced SMs who respond faster acquire more hot leads. | Creates imbalance in workload and earnings across the sales team. |

#### The PM design question

**Is the hot lead routing optimized for conversion or for speed?**

If the best SM (highest close rate) is busy and can't claim the hot lead quickly, a less skilled SM may claim it instead. 

**Alternative design:** Route hot leads to the SM with the highest recent close rate, not the fastest to respond. This is a product architecture decision that affects revenue.

#### PM audit for hot lead ROI — 3 questions before redesigning

1. **Claim speed:** What % of hot leads are claimed within 5 minutes of posting? If < 60%, speed routing isn't even working as intended.
2. **Skill bias:** Do the 3 SMs with the highest close rates get significantly more hot leads? If yes, the fastest responders already correlate with skill — routing is working. If no, consider skill-based routing.
3. **Conversion lift:** Is hot lead conversion rate meaningfully higher than warm lead conversion? If the difference is < 5 percentage points, the routing complexity may not justify its maintenance cost.


> **Next step:** You've covered the mechanism — how CRM data flows, how records move through stages, and the engineering building blocks. For the PM decisions this forces (build vs. buy, data quality ownership, hot lead routing, conversion benchmarks) and how it connects to the broader revenue stack, continue to [08.12 Sales Pipeline Integration](sales-pipeline-integration.md).
