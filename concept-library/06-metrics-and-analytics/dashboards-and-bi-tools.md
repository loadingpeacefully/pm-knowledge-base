---
lesson: Dashboards & BI Tools
module: 06 — metrics and analytics
tags: product
difficulty: working
prereqs:
  - 06.05 — Event Tracking & Instrumentation: events feed the pipelines that feed dashboards
  - 02.06 — ETL Pipelines: the transform layer between raw data and dashboards
writer: senior-pm
qa_panel: Senior PM, CFO/Finance Lead, Junior PM Reader
kb_sources:
  - technical-architecture/etl-and-async-jobs/marketing-etl.md
  - technical-architecture/etl-and-async-jobs/etl-pipeline-inventory.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, head of product, AI-native PM
status: ready
last_qa: 2026-04-09
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

Before dashboards, reporting meant waiting. Every week, an analyst would pull data from the database, write SQL queries, paste numbers into a spreadsheet, format a table, and email it to the executive team. If a number looked wrong, you'd send a Slack message, wait for the analyst to recheck, and hope the corrected version arrived before the meeting.

This wasn't just slow — it was limiting. By the time a report reached the people who needed it, the window for action had often closed. A spike in signup failures on Tuesday might not appear in anyone's report until Friday's weekly meeting. A campaign that was burning through budget with no conversions might run for three more days before anyone stopped it.

The insight that changed everything: data stored in databases could be connected directly to visualization tools that anyone could query, in near real-time, without requiring an analyst to manually build every report. The concept of a "dashboard" — a live, automatically-updated view of the metrics you care about — turned data from a weekly report into a real-time operational resource.

## F2 — What it is, and a way to think about it

> **Business Intelligence (BI) tool:** Software that connects to data sources (databases, warehouses, ETL outputs) and allows users to query, visualize, and monitor business metrics without writing code — or with minimal SQL.

> **Dashboard:** A collection of metrics, charts, and tables displayed together for a specific audience or use case, refreshing automatically as underlying data updates.

> **ETL pipeline:** The process (Extract, Transform, Load) that moves raw data from production systems into the analytics database that BI tools query. Dashboards are only as fresh as their ETL pipeline.

> **Data freshness:** How current the data in a dashboard is. A dashboard that queries an ETL output running every 3 hours shows data that may be up to 3 hours old. Understanding freshness is essential for using dashboards correctly.

### A concrete way to think about it: The water supply analogy

| Water system | BI system equivalent |
|---|---|
| Water source (reservoir, river) | Production databases (user actions, transactions, events) |
| Treatment and purification plant | ETL pipelines (cleaning, transforming, aggregating raw data) |
| Distribution pipes | Analytics database (cleaned, queryable data) |
| Taps in your house | Dashboard and BI tool (where you actually access the data) |

You don't go to the reservoir to get water — you turn on the tap. But if the treatment plant is offline, the tap runs dry or runs dirty. If the pipes have a leak, you get less than you expect.

⚠️ **Most dashboard problems are actually ETL problems.** The visualization layer is usually fine — the issue is upstream: data missing, delayed, or incorrectly transformed before it ever reaches the dashboard.

## F3 — When you'll encounter this as a PM

| Context | What happens | Why it matters |
|---|---|---|
| **Weekly metrics reviews** | Leadership reviews dashboards showing acquisition, activation, revenue | You need to understand what each metric means, what data feeds it, and when it updates |
| **Campaign monitoring** | Marketing team tracks spend vs. conversions in real-time | Dashboard freshness determines how quickly you can stop a bleeding campaign |
| **Feature launch checks** | You want to see if the new feature is driving its success metric | Knowing which dashboard and which pipeline shows that metric determines when you'll have evidence |
| **Data discrepancy investigations** | Two dashboards show different numbers for the same metric | Understanding the data pipeline explains why — different sources, different transformation logic, different freshness |
| **Self-serve analysis** | You have a product question and want to pull the data yourself | BI tools like Metabase let you build queries without engineering support |

### BrightChamps — How it works in practice

**What:** BrightChamps uses Metabase at `analytics.brightchamps.com` as the primary BI layer, backed by 12 ETL pipelines running on AWS Glue.

**Why:** Different pipelines refresh at different cadences (hourly to daily) depending on time sensitivity.

**Takeaway:** A PM asking "why are my demo numbers different from what ops reported?" often traces back to one report using the BAU ETL (hourly) and another using the DEMO ETL (every 3 hours). Know which pipeline feeds your dashboard.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The BI stack from source to screen

Data flows through several layers before appearing on a dashboard. Each layer has its own latency and failure modes:

| Layer | What it is | BrightChamps example | Typical latency |
|---|---|---|---|
| **Production database** | Operational data generated by product actions | PostgreSQL schemas: tryouts, eklavya, paathshala, payments | Real-time |
| **ETL pipeline** | Scheduled jobs that extract, clean, and transform raw data | 12 AWS Glue jobs; BAU ETL uses Lambda | 1 hour to 1 day |
| **Analytics database** | Transformed, query-optimized data store | Analytics PostgreSQL at BrightChamps | Matches ETL freshness |
| **BI tool / dashboard** | Query and visualization layer | Metabase at analytics.brightchamps.com | Matches analytics DB |

#### The freshness implication — key principle

> **Data freshness ceiling:** A dashboard is only as fresh as its most recent ETL pipeline run. A booking at 9:00 AM won't appear in Metabase until the pipeline next runs. If the pipeline runs every 3 hours, the maximum data age at any moment is 3 hours.

#### What happens when a pipeline fails

1. **6:00 AM** — Pipeline runs successfully; data current as of 6:00 AM
2. **9:00 AM** — Run fails silently
3. **9:00 AM–12:00 PM** — Dashboard continues showing 6:00 AM data while appearing current
4. **12:00 PM** — Run succeeds; gap filled, but team made 3-hour-old decisions for 3 hours

⚠️ **Risk:** If you're using the demo bookings dashboard to decide whether to run a same-day campaign, you need to know that numbers may be up to 3 hours behind. A booking campaign launched at 10:00 AM might not show results until 1:00 PM — not because the campaign isn't working, but because the pipeline hasn't run yet.

---

### The major BI tool categories

Different tools occupy different positions in the stack:

| Category | Tools | What they do | Who uses them |
|---|---|---|---|
| **Self-serve BI** | Metabase, Looker, Mode | Query data warehouse, build charts/reports, share dashboards | Product, ops, finance, marketing |
| **Product analytics** | Amplitude, Mixpanel, Heap | Analyze user behavior from event streams; funnels, retention, cohorts | Product team, growth |
| **Marketing analytics** | Google Analytics, Segment | Web traffic, acquisition attribution, campaign performance | Marketing, growth |
| **Executive dashboards** | Tableau, Power BI, Looker | Executive-facing operational metrics, financial KPIs | Leadership, finance |
| **Real-time streaming** | Grafana, Datadog | Infrastructure metrics, latency, error rates — monitoring-grade freshness | Engineering, DevOps |

#### Key distinction for PMs

> **Product analytics vs. self-serve BI:** Product analytics tools (Amplitude, Mixpanel) operate on the event stream directly — designed for behavioral analysis and A/B testing. Self-serve BI tools (Metabase, Looker) operate on the data warehouse — designed for operational reporting and ad hoc analysis. They often show similar metrics but from different data sources, which is why they sometimes disagree.

---

### How BrightChamps's ETL system feeds its dashboards

BrightChamps runs 12 pipelines, grouped by business domain and refresh frequency:

#### Revenue-critical (every 3 hours)
- **DEMO ETL** — student bookings with course, vertical, region data
- **PAYMENT ETL** — sales and payment data
- **STUDENT ETL** — unified student records
- **PAID CLASS ETL** — paid classes, PTMs, groups

#### Operational (daily)
- **TEACHER ETL** — employment, contacts, preferences
- **MARKETING ETL** — Facebook + Google spend aggregated by course/region
- **STUDENT TEACHER CLASS METRICS ETL** — attendance, assignments, assessments

#### Executive (hourly)
- **BAU ETL** — business-as-usual: marketing + demo + payment metrics for exec reporting

#### Why different cadences

| Cadence | Rationale |
|---|---|
| **Hourly** | Leadership reviews BAU metrics during the day for operational decisions |
| **Every 3 hours** | Payment and demo data must be fresh enough for ops teams to act on same-day issues |
| **Daily** | Teacher data changes less frequently; daily refresh is sufficient |

---

### Metabase alerts: the data quality safeguard

⚠️ **Why alerts matter:** ETL failures are silent — the dashboard shows data, but it's wrong or stale. Without alerts, a team might make campaign decisions based on marketing spend data that's 3 days old because the Marketing ETL failed quietly.

| Pipeline | Alert | What it catches |
|---|---|---|
| DEMO ETL | `/question/4275-bookings-vs-etl-alert` | Discrepancy between source bookings and ETL output |
| MARKETING ETL | `/question/2622-marketing-alert` | Marketing spend data not matching source |
| PAYMENT ETL | `/question/2624-regular-collection-mismatch-` | Payment records not reconciling |
| BAU ETL | Three separate alerts | Demo/completed/lead count discrepancies vs. source |

---

### ETL architecture: why BrightChamps uses AWS Glue

BrightChamps's pipelines extract from production PostgreSQL schemas (tryouts, eklavya, paathshala, dronacharya, payments), transform with AWS Glue (SQL-based CASE statements, joins, aggregations), and load into an analytics PostgreSQL that Metabase queries.

#### The Marketing ETL example

**Flow:**
1. Join two source tables (Google Ads and Facebook/Meta spend)
2. Derive geographic and product dimensions via CASE statements
3. Aggregate by those dimensions
4. Output clean `FINAL_OUTPUT` table
5. Metabase queries that table — never touches production `tryouts` schema directly

#### Why this separation matters

> **Analytics isolation principle:** Analytical queries (aggregations, full-table scans, complex joins) are expensive and slow when run on production databases. They compete with user-facing transactions for database resources. The ETL layer copies data to a separate analytics database optimized for reads, ensuring analytical queries don't degrade product performance.

## W2 — The decisions this forces

### Decision 1: Which BI tool is your team's source of truth?

Most companies end up with multiple BI tools serving different needs. The problem: they often show different numbers for the same metric, creating confusion and eroding trust.

| Scenario | Why numbers differ | Consequence |
|---|---|---|
| Amplitude DAU vs. Metabase DAU | Different "active" definitions, different event sources | Team debates which number is right instead of acting |
| Marketing ETL Metabase vs. Google Ads native dashboard | ETL transformation logic applies filters; native dashboard shows raw | Spend looks different depending on where you look |
| BAU ETL vs. DEMO ETL | Different transformation logic; different refresh frequencies | Exec report shows different demo numbers than ops report |

**→ Recommendation:** Establish one source of truth per metric and document it explicitly. Which dashboard shows the "official" demo booking count? Which shows the revenue number? This is a PM and data team decision that requires alignment, not a technical configuration.

---

### Decision 2: Build vs. buy for the BI layer

When product teams outgrow spreadsheet reporting, they face a tool choice:

| Option | Examples | Strengths | Weaknesses |
|---|---|---|---|
| **Self-serve BI (SQL-based)** | Metabase, Looker, Mode | Full flexibility, lower cost | SQL required, needs data team setup |
| **Product analytics platform** | Amplitude, Mixpanel | Fast insights, no SQL needed | Expensive at scale, opaque data models |
| **Custom internal dashboards** | React + Recharts over data API | Full control | Highest engineering cost, ongoing maintenance |
| **Spreadsheet + manual exports** | Google Sheets, Excel | Cheapest entry point | Non-scalable, error-prone, no automation |

### Company — BrightChamps

**What:** Uses Metabase (self-serve BI) as primary tool

**Why:** Pragmatic for a company with dedicated data engineers who can write underlying queries and transformations

**Takeaway:** Teams with lower data engineering capacity often default to product analytics platforms (Amplitude) because they require no ETL setup.

---

### Decision 3: Who owns the dashboard?

Three common ownership models, each with distinct failure modes:

| Model | How it works | Failure mode |
|---|---|---|
| **Engineering-owned** | Data team builds and maintains all dashboards | Dashboard backlog grows; PMs can't get metrics quickly |
| **PM-owned** | Product team builds dashboards in self-serve tools | PMs build on unreliable data; no schema governance |
| **Shared model** ✓ | Data team owns ETL/schema; PMs own visualization layer | Requires discipline on both sides, but works best |

**The BrightChamps model uses the shared approach:**
- Data engineers (Kadambi Kashyap, Ishan Sarkar) own ETL pipelines and alerts
- Analytics PostgreSQL and Metabase setup maintained by data team
- PMs build their own Metabase questions on reliable tables

---

### Decision 4: Data freshness requirements per use case

Not every metric needs to be real-time. Getting freshness wrong in either direction creates problems:

| Use case | Required freshness | If too stale | If too fresh (over-engineered) |
|---|---|---|---|
| Executive weekly review | Daily | Decisions on old numbers | Waste of resources |
| Active campaign monitoring | Hourly or better | Can't stop failing campaign in time | Waste of resources |
| Same-day ops (class cancellations, payment failures) | < 3 hours | Ops misses time-sensitive cases | Pipeline cost increases |
| Monthly cohort analysis | 24 hours | Nothing meaningful | Waste of resources |
| Infrastructure incident response | < 5 minutes | Incident runs longer | Waste of resources |

**→ Cost principle:** Fresher data = more pipeline runs = higher compute cost. A 5-minute refresh for a daily-decision metric is a waste of engineering and cloud spend. Align pipeline frequency to actual decision frequency.

---

### Decision 5: Treating dashboard numbers as inputs, not answers

⚠️ **Common PM mistake:** Treating a number on a screen as fact without understanding what it represents.

> **Dashboard number lifecycle:** Every metric has four components that determine whether it's trustworthy

Every metric on a dashboard has:

1. **Definition** — What counts as "active," "revenue," what time zone for timestamps
2. **Source** — Which ETL, schema, and table
3. **Freshness** — Last updated when
4. **Transformation** — What filters, aggregations, or CASE logic was applied

**A drop in demo bookings could signal:**
- ✓ Actual decline in bookings
- ✗ ETL pipeline failed overnight
- ✗ Timezone handling changed in recent deploy
- ✗ New marketing campaign excluded a country in the CASE logic

**→ Always ask:** Did something change in the *data layer* before concluding something changed in the *business*.

## W3 — Questions to ask your data team

### Quick Reference
| Question | Reveals |
|----------|---------|
| Which ETL pipeline feeds this metric? | Current vs. stale data |
| What's the official definition? | Whether metric matches your decision |
| Are there Metabase alerts configured? | Data quality monitoring gaps |
| Why do Amplitude and Metabase differ? | Team's data stack understanding |
| Can I build queries myself? | Data democratization level |
| What's the latency? | Same-day vs. historical analysis capability |
| Is the data reliable at this granularity? | Filtering safety at narrow slices |
| Who owns each pipeline? | Bus factor risk in infrastructure |

---

### 1. "Which ETL pipeline feeds this metric, and when did it last run?"

The most important question when a number looks wrong. The answer tells you whether you're looking at a data problem or a business problem.

*What this reveals:* Whether the dashboard is showing current data or stale data from a failed pipeline run.

---

### 2. "What's the official definition of [metric] in this dashboard — what counts and what doesn't?"

Dashboards rarely show raw database counts. Every metric has a definition applied during transformation.

| Scenario | Impact |
|----------|--------|
| Finance dashboard (includes trial discounts) | Higher revenue number |
| Product dashboard (excludes trial discounts) | Lower revenue number |
| Same metric, different definitions | Different decisions made |

*What this reveals:* Whether the metric you're using matches the decision you're making. "Revenue" means different things to finance and product.

---

### 3. "Are there Metabase alerts configured for this pipeline? When did they last trigger?"

Alerts on data pipelines catch silent failures before you act on bad data. Without alerts, a pipeline can fail quietly for days.

⚠️ **Risk:** Absence of alerts is a red flag — it means problems are discovered only when someone notices a wrong number.

*What this reveals:* How the data team monitors data quality.

---

### 4. "Why does the Amplitude metric differ from the Metabase metric for the same thing?"

This question almost always has an answer — it's usually about different definitions, different event sources, or different time windows. The answer tells you which source to trust for which use case.

| Common Reasons | What to Check |
|----------------|---------------|
| Different event source | Which system-of-record applies? |
| Different definitions | What counts as a user action? |
| Different time windows | UTC vs. local time? Daily vs. hourly? |

*What this reveals:* The team's understanding of their own data stack. If they don't know why the numbers differ, neither source can be trusted fully.

---

### 5. "Can I build a Metabase question myself, or do I need to submit a ticket?"

Self-serve BI is only self-serve if PMs can access and query the analytics database. Access controls, table documentation, and SQL knowledge all determine whether PMs can genuinely be self-sufficient.

| Access Level | Outcome |
|--------------|---------|
| PMs can query directly | Data-democratized; no bottleneck |
| PMs must submit tickets | Data team becomes blocker |
| Tables undocumented | Even access doesn't help |

*What this reveals:* How data-democratized your organization is. If PMs can't build their own queries, they're bottlenecked by data team capacity.

---

### 6. "What's the latency between a user action and when it appears in this dashboard?"

For operational decisions (is this feature working?), you need to know how long you have to wait for evidence. The answer is the sum of pipeline latency plus any downstream processing.

*What this reveals:* Whether you can use the dashboard for same-day decisions or only for backward-looking analysis.

---

### 7. "If I filter this metric by [country/course/teacher segment], is the underlying data reliable at that granularity?"

ETL pipelines often have data quality issues at low-cardinality slices. A marketing spend dashboard might be reliable at the country level but unreliable at the city level because city data has mapping gaps.

⚠️ **Risk:** Filtering a dashboard to a narrow slice can produce numbers that look precise but are based on incomplete data.

*What this reveals:* Granularity reliability.

---

### 8. "Who owns each pipeline, and what's the escalation path if a pipeline fails?"

With only a few engineers owning all pipelines (the BrightChamps pattern), a pipeline failure during an engineer's vacation or sick leave can leave critical dashboards stale for days.

> **Bus Factor:** The number of team members who must be hit by a bus before the project stalls. Single-owner pipelines have a bus factor of 1.

⚠️ **Risk:** Single-owner pipelines are a fragility point for any organization that depends on daily data.

*What this reveals:* Bus factor risk in the data infrastructure.

## W4 — Real product examples

### BrightChamps — 12-pipeline ETL feeding Metabase

**What:** BrightChamps's data stack has 12 AWS Glue pipelines extracting from 5 microservice PostgreSQL schemas (tryouts, eklavya, paathshala, dronacharya, payments) and loading into a single analytics PostgreSQL queried by Metabase.

**Refresh architecture by business criticality:**

| Pipeline | Sources | Refresh cadence | Rationale |
|---|---|---|---|
| Payment, Demo, Student, Paid Class | Revenue tables | Every 3 hours | Revenue-critical decisions |
| Teacher, Marketing, Attendance | Operational tables | Daily | Operational rhythm |
| BAU Dashboard | Executive queries | Hourly | Real-time decision-making |

**The PM implication:** A PM reviewing marketing spend-to-demo conversion at 10 AM is looking at:
- Demo bookings from up to 3 hours ago
- Marketing spend from up to 24 hours ago

Comparing spend to bookings with different freshness windows can show apparent inefficiency that doesn't actually exist — the bookings just haven't been processed yet.

**What BrightChamps does right:** Metabase alerts for every critical pipeline. If the DEMO ETL produces results that don't match source bookings, an alert fires. This means data discrepancies are caught by the data team before a PM makes a wrong decision.

---

### Metabase — self-serve BI for operational teams

**What:** Metabase is an open-source BI tool that allows non-technical users to build queries through a point-and-click interface or directly write SQL. BrightChamps hosts it at `analytics.brightchamps.com`.

**PM workflow at BrightChamps:**

1. Access Metabase
2. Browse available tables in the analytics PostgreSQL
3. Build a "question" (either graphical or SQL-based)
4. Save to a collection for sharing with ops, marketing, or leadership
5. Set up scheduled email delivery for recurring reports

**What this enables:** A PM can ask "how many students from Vietnam completed at least one paid class in the last 30 days?" without waiting for an analyst to build the query — if the data is in the analytics database and the PM has Metabase access.

---

### Amplitude — product analytics for behavioral questions

**What:** Amplitude (or tools like it — Mixpanel, Heap, PostHog) sits on the event stream rather than the ETL pipeline. It captures every user action in real-time and makes behavioral analysis immediately available: retention curves, funnel completion, user paths, A/B test results.

**When to use Amplitude vs. Metabase:**

| Question | Right tool | Why |
|---|---|---|
| What % of users completed the onboarding flow? | Amplitude | User behavior, step-by-step funnel from events |
| What was last month's total revenue? | Metabase / data warehouse | Financial data from payments table |
| Which A/B variant drove more completions? | Amplitude | Event-level experiment tracking |
| How many classes did a specific teacher complete last quarter? | Metabase | Operational record query |

> **Key distinction:** Amplitude shows you what users *did*. Metabase shows you what *happened* in the business. Both are necessary; treating one as a substitute for the other produces wrong analysis.

---

### Looker (Google) — data modeling as the BI standard at scale

**What:** Looker (now Google Looker) adds a data modeling layer between the database and the dashboard using a language called LookML. Instead of every analyst writing their own SQL definition of "monthly active users," the definition is written once in LookML and reused across all queries.

**Why this matters for PM:**

- Metrics are defined once, consistently, for the entire organization
- Changing a metric definition in LookML propagates to all dashboards automatically
- PMs can explore data without knowing SQL because Looker abstracts the queries

**The tradeoff:** Looker requires a significant upfront investment in data modeling. It's powerful for companies with 50+ metrics and multiple teams querying the same definitions. For early-stage companies (like BrightChamps at its current scale), Metabase + well-documented ETL tables achieves similar consistency with less infrastructure overhead.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The semantic layer gap

Data warehouse tables are optimized for storage and query performance. Business metrics are optimized for human comprehension. The translation between them is often missing or scattered.

> **Semantic Layer:** A centralized, documented definition layer that maps business metrics to their underlying database queries and logic.

**The failure pattern:**

| Step | What happens | Result |
|------|--------------|--------|
| 1 | Engineer creates `student_class_balance` table with column `total_class_paid` | Schema exists |
| 2 | PM A builds Metabase query: `SUM(total_class_paid)` → "Total Paid Classes" | One metric definition |
| 3 | PM B builds Metabase query: `COUNT(class_id WHERE status = 'completed')` → "Total Paid Classes" | Conflicting definition |
| 4 | Leadership sees two different numbers in two reports | Confusion |
| 5 | No documented definition exists | Nobody knows which is correct |

**What this reveals:** The absence of a single, authoritative, documented definition for each metric is one of the most common sources of organizational dysfunction in companies with 20+ people and more than 5 dashboards.

---

### Dashboard proliferation and the "graveyard" problem

Dashboards are easy to create and nearly impossible to retire. Every team that gets BI tool access builds dashboards for their needs.

**What breaks:**

| Scenario | Timeline | Risk |
|----------|----------|------|
| Company with 50 employees | Within 2 years | 300 Metabase questions + 80 dashboards |
| Many dashboards contain | Unknown | Stale schemas, deprecated tables, outdated ETL logic |
| A new PM discovers an existing dashboard | Day 1 | Trusts it, makes decisions |
| Decision is based on | 18 months old | Logic that no longer reflects current data model |

> **The Graveyard Problem:** Dashboards that appear functional but display incorrect data because the underlying ETL was refactored and the dashboard query was never updated.

⚠️ **Without governance:** Every dashboard is a potential minefield for decision-making.

---

### ETL pipeline dependencies: the hidden cascade failure

Pipelines depend on each other. A failure in one triggers downstream failures that propagate silently.

**Example cascade:**

```
Schema change in tryouts database
        ↓
DEMO ETL fails silently
        ↓
BAU ETL runs on stale DEMO data
        ↓
BAU numbers become incorrect
        ↓
Leadership reviews wrong numbers
        ↓
PM makes campaign decision based on bad data
```

**The prevention pattern:**

- Document cross-pipeline dependencies explicitly
- Monitor source tables for schema changes
- Design ETL pipelines to **fail loudly** (error state, not silent failure) when inputs don't match expectations

## S2 — How this connects to the bigger system

| Concept | Connection | Critical Interaction |
|---|---|---|
| **ETL Pipelines (02.06)** | Dashboards query ETL outputs; understanding pipelines explains freshness and quality | Pipeline failures and schema changes are the most common cause of wrong dashboard metrics |
| **Event Tracking (06.05)** | Product analytics dashboards (Amplitude, Mixpanel) are built on event streams | Bad event schemas produce wrong funnel and retention metrics in product dashboards |
| **Data Quality & Pipelines (06.10)** | Data quality issues manifest as dashboard anomalies | A number that looks wrong usually traces to a quality issue upstream |
| **North Star Metric (06.01)** | The north star lives in a dashboard; knowing the pipeline and definition is what makes it trustworthy | Teams that don't know how their north star is calculated often debate wrong numbers instead of acting |
| **Counter Metrics (06.09)** | Guardrail metrics live on dashboards; their freshness determines how quickly teams can respond to degradation | A counter metric that updates daily can't protect against a same-day regression |

### The organizational tension

**The paradox:** The more dashboards a team has, the less any single one is trusted. At scale, organizations stop trusting their data because every meeting surfaces a different number from a different report.

**The resolution:**

> **Data Governance:** A small set of "official" metrics with documented definitions, single sources, and an owner who maintains them. Everything else is clearly labeled as unofficial or exploratory.

**The PM role:** Senior PMs often have to champion this governance even when it means killing dashboards they built.

## S3 — What senior PMs debate

### "Should PMs own their metrics, or should there be a dedicated analytics function?"

Two dominant models emerge as organizations scale:

| Model | How it works | Strengths | Tradeoffs |
|-------|-------------|----------|----------|
| **Embedded analytics** | Every PM directly accesses data warehouse, builds queries, owns metrics end-to-end | Fast, empowering, self-sufficient | Semantic fragmentation, inconsistent definitions across teams |
| **Centralized analytics** | Dedicated data team owns definitions, ETL, dashboard governance; PMs consume pre-built metrics | Consistent, authoritative, governed | Bottlenecks when PMs need non-standard metrics |

**What's emerging (2024–2025):** AI-assisted query tools are collapsing this debate. Natural language interfaces to data warehouses (ChatGPT-like interfaces embedded in Metabase, Looker, Tableau) allow PMs without SQL fluency to get accurate answers from well-governed data models without waiting for analysts.

> **The shift:** The bottleneck moves from "can the PM write SQL?" to "is the data model accurate and well-documented?" — a semantic layer problem, not a skills problem.

---

### "Metrics in the warehouse vs. metrics in the product analytics platform — which wins?"

The tension is real and unresolved in most organizations.

| System | Best for | Key capabilities |
|--------|----------|------------------|
| **Warehouse** (Metabase, Looker) | Investor reporting, financial metrics, compliance | Consistency, historical depth, joins any business data |
| **Product analytics** (Amplitude, Mixpanel) | Feature adoption, retention curves, experiment analysis | Real-time behavioral data, funnel visualization, A/B test integration |

**The practical answer:** For everything else, it depends on which your team trusts more — often a cultural question, not a technical one.

**What changes with AI:** LLM-powered query interfaces are starting to sit above both layers and translate natural language into appropriate queries for each system. Soon, "show me MAU broken down by course" will route automatically to the most appropriate source without the PM knowing whether the answer comes from Amplitude or BigQuery.

---

### "What metrics should a PM be able to pull themselves, and what should they delegate?"

> **The uncomfortable truth:** A PM who can't answer basic product health questions from the data directly is operationally dependent on others in a way that slows down good decisions.

But the answer isn't "learn SQL." Instead:

1. **Know which dashboards show which things** and whether they're reliable
2. **Know who to ask for new queries** and how to frame the request clearly
3. **Know enough to evaluate whether an answer looks right** (sanity-check outputs)

A PM who masters these three skills is as effective as a SQL-fluent PM, without the overhead of maintaining SQL competency.

> **Right division of responsibility:**
> - **Data engineers** own the pipeline
> - **Analytics team** owns the model
> - **PM** owns the question — knowing exactly what business question needs answering and what the answer needs to do