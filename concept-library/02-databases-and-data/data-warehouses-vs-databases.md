---
lesson: Data Warehouses vs Databases
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 02.01 — SQL vs NoSQL: databases covered here are the OLTP systems that feed data warehouses
  - 02.04 — Caching (Redis): caching and warehousing both solve read performance — but for different query types and time horizons
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/etl-and-async-jobs/etl-pipeline-inventory.md
  - technical-architecture/etl-and-async-jobs/marketing-etl.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-07
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The dashboard that could never be trusted

The executive team at the edtech platform held a weekly business review. Every Monday morning, the same ritual: open Metabase, pull up the key metrics dashboard, discuss the numbers.

**But the numbers were never entirely fresh:**

| Data Source | Freshness |
|---|---|
| Payment data | 2 hours old |
| Teacher performance | 1 day old |
| Demo attendance | This morning |
| Student balances | This morning |

Every screenshot required annotation: "Payment numbers as of 9am, teacher data as of last night."

**The compound data problem:**

When someone asked, "Did the campaign we ran Thursday convert to paid classes by Friday?" — the answer required:
1. Marketing spend table
2. Demo bookings table
3. Payment records table
4. Class completion table

The analyst had to pull data from three microservice databases, join them manually, clean duplicates, and present results in a spreadsheet — **two days after the question was asked**.

---

### Why this is a structural problem, not a reporting one

Production databases (where students book classes, payments are recorded, teachers log attendance) are built for one job: **handling individual operations fast**. They're optimized for:
- Thousands of small writes per second
- One student booking one class
- One payment confirmation
- One teacher feedback submission

**They are not built for analytical questions** like "what was our CAC by vertical and channel last month across all regions?"

#### The cost of running analytics against production:

⚠️ **Row locking:** A multi-minute analytical query locks database rows while it runs — slowing down students trying to book classes in real-time.

⚠️ **Fragmentation:** Data lives across eight microservice schemas that weren't designed to be joined together.

---

### The solution: separate systems for separate jobs

> **Data warehouse:** A separate database system built specifically for analytical questions. It holds a copy of production data, transformed and organized for reading. It never handles live user transactions. It exists entirely to answer questions.

> **ETL (Extract, Transform, Load):** A scheduled job that copies data from one database, transforms it (cleaning, restructuring, joining), and loads the result into another. The mechanism that keeps the data warehouse populated with fresh data from production.

> **Microservice:** A software design approach where each function of an application (payments, student profiles, class scheduling) runs as a separate, independent service with its own database. The platform has 8+ microservices — Payment-Structure, Eklavya (students), Paathshala (classes), etc. — each with a separate PostgreSQL database. The warehouse consolidates their data.

**The platform's architecture:**
- 12 ETL pipelines copy data from production databases
- Data is transformed and loaded into a separate analytics PostgreSQL
- Metabase reads from the analytics PostgreSQL, **not from production**

**Why:** Running analytical queries against production disrupts the users actively using the system. The data warehouse absorbs that load instead.

## F2. What it is — the filing office and the archive room

Imagine a busy hospital.

**The Emergency Room = Production Database**

The **emergency room** is the production database. Doctors and nurses are constantly creating records: new patients admitted, diagnoses entered, medications prescribed, vital signs logged. Everything happens fast. The ER is optimized for writing quickly and finding one patient's records immediately. 

*Nobody stops to analyze "how many appendectomies did we perform last quarter by age group and season."*

**The Medical Records Archive = Data Warehouse**

The **medical records archive** is the data warehouse. Every night, staff copy that day's ER records to the archive room, organized by date, diagnosis, procedure type, and outcome. Medical researchers come to the archive to run studies: "What's the mortality rate for appendectomies in patients over 60?" They can scan every record from the last 10 years without disturbing the ER at all.

⚠️ **Critical timing trade-off:** The archive isn't updated in real time. It's always slightly behind — the morning archive has yesterday's records. That's fine for research. But it would be catastrophic for the ER to use the archive to find a patient who came in an hour ago.

---

### Two Database Types

> **OLTP (Online Transaction Processing):** The production database. Handles individual operations: one payment, one booking, one student record. Optimized for fast reads and writes of specific rows. The application database.

> **OLAP (Online Analytical Processing):** The data warehouse. Handles analytical queries: aggregate 10 million rows, group by region, calculate conversion rates over 90 days. Optimized for reading large amounts of data across many columns.

> **Data warehouse:** An OLAP system. A database designed and built specifically for analytical queries. Holds historical data copied from production. Used by analysts, data teams, and business intelligence tools (Metabase, Looker, Tableau).

---

### Why Can't One Database Do Both?

| Dimension | OLTP (Production) | OLAP (Warehouse) |
|-----------|-------------------|------------------|
| **Storage organization** | Row by row — all of a student's fields together in one block | Column by column — all students' `country_code` values together, all `created_at` values together |
| **Storage benefit** | Fast writes and individual row lookups | Fast aggregation queries; skips irrelevant columns (e.g., reading only `created_at` and `age` to find Q1 joiners) |
| **Query example** | "Find student ID 12345's current credit balance" | "What's the average credit balance of students who completed 3+ classes in the last 90 days, by vertical?" |
| **Query scale** | One row, instant | Millions of rows, minutes |
| **Optimization priority** | Write throughput + millisecond reads of individual rows | Reading and aggregating large datasets |

**The fundamental problem:** OLTP and OLAP requirements pull database design in opposite directions — indexes, locks, query planners all work differently for the two use cases.

## F3. When you'll encounter this as a PM

### Dashboard lag

**Situation:** Data team says the dashboard is "lagging."

Every data warehouse has a freshness window — the delay between when something happens in production and when it appears in the analytics dashboard. The platform's payment ETL runs every 3 hours. If a payment was made 2 hours and 50 minutes ago, it's not in the dashboard yet.

**PM question:** "What's the maximum lag for this metric, and does that lag affect any decision that needs to be fast?"

---

### Production database queries

**Situation:** Someone asks "why can't we just query the production database directly?"

⚠️ **Risk:** Analytical queries against a production database lock rows and consume server resources needed for live users. A 5-minute analytics query running against the production student database during peak booking hours is a latency incident.

**What the PM needs to know:** Analytics belongs in the warehouse, not production. You don't need to understand the query planner — but you need to enforce this boundary.

---

### Cross-system metrics

**Situation:** A new metric requires data from multiple systems.

Example: "Show me demo completion rate, payment conversion, and class attendance together on one dashboard."

| System | Data lives in |
|---|---|
| Demo completion | tryouts database |
| Payment conversion | payments database |
| Class attendance | paathshala database |

**Options to combine them:**
1. **New ETL pipeline** — joins data in the warehouse (preferred)
2. **Cross-database query** — slow, engineering won't permit against production

**PM question:** "Is this data already in the warehouse? If not, how long to add an ETL pipeline for it?"

---

### Data-driven features

**Situation:** Planning a feature that requires aggregated historical data.

Examples: personalized recommendations, cohort analysis, churn prediction, retention dashboards.

This work happens in the warehouse.

**PM questions:**
- "Is the data we need for this feature already being ETL'd to the warehouse?"
- "What's the freshness window?"

---

### PM ownership and decision matrix

| Situation | Your role | Approve or push back? | What to require |
|---|---|---|---|
| **Data team asks for new ETL pipeline** | Validate business need — is this metric worth engineering time? | ✅ Approve if it drives a decision<br/>❌ Push back if "nice to have" reporting | Define freshness SLA: "This metric needs to refresh every X hours because it drives Y decision" |
| **Dashboard shows stale numbers before business review** | Own the escalation — this is a product quality issue, not just infra | ✅ Require root cause and fix timeline | Document acceptable lag per metric; set monitoring alert |
| **New product vertical or feature launches** | Add "update ETL mappings" to launch checklist | ❌ Push back if missing — metric drift is silent and dangerous | Confirm ETL is updated and re-validated before launch |
| **Engineer says "analytical queries are slow"** | Understand: warehouse-sizing problem or query design problem? | ❌ Don't approve migration without trying indexes and optimization first | Time-box optimization; if still slow after indexing, approve migration planning |
| **Team proposes moving to BigQuery/Snowflake** | Validate business case — performance or engineering preference? | ✅ Approve if query times degrade analyst productivity<br/>❌ Push back if premature | Require migration plan with data validation before decommissioning old system |

---

### Managed warehouse services

**Situation:** Someone mentions "BigQuery," "Redshift," or "Snowflake."

> **Managed service:** A cloud product where the vendor handles infrastructure (hardware, software updates, backups, scaling). Your team focuses on using it, not running it. BigQuery (Google Cloud), Redshift (AWS), and Snowflake are managed data warehouses — as opposed to self-hosting PostgreSQL, where your team manages the server.

> **Denormalized:** Data where information is deliberately duplicated across a table for query speed. A denormalized analytics table might repeat the student's country_name in every row instead of storing it once in a separate student table and joining. Slower to write, faster to read — the right tradeoff for analytics.

**Why teams migrate:** If the engineering team is proposing one of these, it's because the analytics PostgreSQL is hitting its limits:
- Query times are growing
- System can't scale storage independently of compute
- Analysts are competing for resources
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that a data warehouse is a separate system for analytical queries, holding copied production data; knows OLTP vs OLAP, ETL, and data freshness.
# ═══════════════════════════════════

## W1. How data warehouses actually work — the mechanics that matter for PMs

### Quick reference
| Concept | Key takeaway |
|---|---|
| **OLTP vs OLAP** | Production DBs optimize for single rows; warehouses optimize for columns across millions of rows |
| **Columnar storage** | Reads only needed columns = 50× faster than row storage for analytics |
| **ETL pipeline** | Extract → Transform → Load; introduces freshness lag between production and warehouse |
| **Data freshness** | Your dashboards show old data; fastest ETL runs hourly, slowest daily |
| **Warehouse schema** | Denormalized flat tables designed for speed, not normalization |

---

### 1. OLTP vs OLAP — the fundamental design difference

The same data query runs in completely different time on OLTP vs OLAP systems:

| | OLTP (Production DB) | OLAP (Data Warehouse) |
|---|---|---|
| **Optimized for** | Fast reads/writes of individual rows | Fast reads of large column ranges |
| **Typical query** | "Get student ID 12345's current balance" | "What's the average balance of all students by country, last 90 days?" |
| **Row scan for analytics** | Reads every column to find matching rows | Reads only the columns needed (columnar storage) |
| **Query time (10M rows)** | Minutes — wrong tool | Seconds — correct tool |
| **Write pattern** | Constant, high-frequency | Batch writes from ETL (not from live users) |
| **Concurrent users** | Thousands (application users) | Dozens (analysts, BI tools) |
| **Indexes** | Many, on frequently queried columns | Few — full scans are common and fast |
| **Lock behavior** | Row-level locks during transactions | No transactional locks — read-only |

---

### 2. Row storage vs columnar storage — why it matters for query speed

> **Row-oriented database:** Stores complete rows together (PostgreSQL, MySQL). To find "average age of Q1 joiners," must read every column including name, email, address, phone — only to extract 2 columns.

> **Column-oriented database:** Stores one column's values together (BigQuery, Redshift, Snowflake). To find "average age of Q1 joiners," reads only `joined_at` and `age` columns.

**The math:**
- Row storage: 100 columns × 10M rows = **1 billion field reads**
- Columnar storage: 2 columns × 10M rows = **20 million field reads**
- **Result: 50× faster on columnar**

This is why analytical queries taking minutes on PostgreSQL run in seconds on BigQuery.

**Current state:** The platform uses PostgreSQL as its analytics database (not purpose-built columnar). This works at startup scale. As data volume grows, columnar warehouses like BigQuery or Snowflake become necessary.

---

### 3. The ETL pipeline — how data gets from production to warehouse

> **ETL:** Extract, Transform, Load — the three-step process moving data from production to warehouse.

#### Extract
Copy data from one or more production databases.

The platform's ETL extracts from six microservice schemas:
- tryouts
- eklavya
- paathshala
- dronacharya
- payments
- platform

#### Transform
Clean, enrich, and restructure the data.

**Marketing ETL example:**
- Normalizes country codes ('BC' → 'Vietnam')
- Maps numeric vertical IDs (1 → 'Codechamps')
- Standardizes UTM channels ('google_display' → 'Google-Display')
- Aggregates spend by date × country × vertical × channel

#### Load
Write transformed data to the analytics database. The `FINAL_OUTPUT` table holds pre-aggregated marketing performance ready for Metabase queries.

**Infrastructure & schedule:**
Runs on AWS Glue (managed ETL service). 12 pipelines with different frequencies:

| Frequency | Pipelines | Use |
|---|---|---|
| Every 1 hour | BAU ETL | Exec-level dashboard (highest priority) |
| Every 3 hours | Payment, Demo, Student, Addons, Paid Class ETL | Core metrics |
| Daily | Teacher, Marketing, Student Metrics, Refund ETL | Low-priority or batch-friendly metrics |

---

### 4. Data freshness — the PM's most important warehouse concept

> **Data freshness:** The lag between when something happens in production and when it appears in the warehouse. Every ETL introduces this gap.

Every analytical question has a freshness limit:

| Metric | ETL frequency | Max lag |
|---|---|---|
| Payments, Revenue | Every 3 hours | Up to 3 hours |
| Demo bookings | Every 3 hours | Up to 3 hours |
| Exec dashboard (BAU) | Every 1 hour | Up to 1 hour |
| Teacher performance | Daily | Up to 24 hours |
| Refunds | Daily | Up to 24 hours |
| Marketing spend | Daily | Up to 24 hours |

**What this means:** 
- Campaign launched at 2pm? Can't answer "did it convert by 5pm?" from warehouse
- If Marketing ETL runs at midnight, today's campaign performance appears tomorrow morning
- Any decision needing data fresher than ETL frequency must use production DB, cache, or real-time stream

---

### 5. Warehouse schemas — the analytics layer design

Data warehouses use denormalized schemas optimized for analytics queries — opposite of normalized production schemas.

#### Star schema
One central "fact" table (e.g., payments) surrounded by dimension tables (student, teacher, course, date). Every query joins fact to dimensions. Simple, fast for analytics.

#### Denormalized flat tables
All dimension data copied directly into the fact table (student_name, student_country, course_name all columns in payments table). No joins at query time. Fastest for analytics. Most storage.

**Current implementation:**
Marketing ETL output (`FINAL_OUTPUT`) is a denormalized flat table with:
- date
- country_name
- vertical_name
- course_name
- utm_updated
- All metric columns

No joins needed — Metabase reads one table directly.

---

### 6. The warehouse stack — what systems are used at scale

| System | Type | Pricing | Indicative cost | Best for |
|---|---|---|---|---|
| **PostgreSQL (analytics)** | Row-based DB used as warehouse | Fixed server (EC2/RDS) | $50–500/month | Startups, <50M rows per table |
| **Amazon Redshift** | Columnar, managed | Node-based (always-on) | $180–2,000+/month per node | AWS shops, predictable workloads |
| **Google BigQuery** | Columnar, serverless | Per TB scanned ($5/TB) + storage | $0–500/month at startup; can spike $5,000+/month unoptimized | Ad-hoc queries, unpredictable load, GCP shops |
| **Snowflake** | Columnar, multi-cloud | Compute credits (pause when idle) | $200–10,000+/month; ~$2–4/credit | Enterprise, multi-team, workload isolation |
| **Databricks** | Lakehouse (lake + warehouse) | Compute-based (DBU units) | $500–5,000+/month | Data science-heavy orgs, ML pipelines |

⚠️ **BigQuery cost trap:** Pay-per-TB scanned seems cheap until someone runs `SELECT * FROM billion_row_table` with no filter — scanning 500GB = $2.50 per scan. With 20 analysts, this adds up fast.

**Mitigation:**
- Set per-user query cost limits
- Require WHERE clauses on large tables
- Monitor scan volumes weekly

**Current state:** Platform uses PostgreSQL as analytics target — pragmatic at current scale, but columnar migration is on the horizon as query volumes grow.

---

### 7. What the warehouse can't do — the limits PMs need to know

Data warehouses are **read-only copies**. They cannot:

- ❌ Drive real-time application features (data is hours old)
- ❌ Replace the production database for user-facing reads
- ❌ Run transactional operations (no ACID, no row-level locking)
- ❌ Surface events from the last few minutes (ETL lag blocks this)

> **Rule:** Any feature requiring data fresher than ETL frequency must read from production database, cache, or real-time streaming pipeline — NOT the warehouse.

## W2. The decisions a data warehouse forces

### Decision 1: Analytics PostgreSQL now vs columnar warehouse later — when to migrate?

> **PM default:** Stay on analytics PostgreSQL until query times on the analytics DB exceed 30–60 seconds for critical business metrics, or until data volume requires independent storage/compute scaling. Migration to BigQuery/Snowflake is a 3–6 month project; do it before you're in pain, not during.

| | Analytics PostgreSQL | Columnar warehouse (BigQuery/Snowflake) |
|---|---|---|
| Setup cost | Low — extend existing infrastructure | High — migration effort, new tooling, team learning |
| Query performance (small data) | Adequate for <100M rows | No benefit over PostgreSQL at small scale |
| Query performance (large data) | Degrades significantly beyond ~100M rows per table | Consistent sub-30s even at billions of rows |
| Storage/compute scaling | Coupled — scale both together | Independent — store cheaply, scale compute for big queries |
| Cost at low volume | Low fixed cost | Low (pay per query on BigQuery) to medium (node cost on Redshift) |
| Cost at high volume | Expensive to scale server | More predictable; BigQuery's per-TB model can spike unexpectedly |
| **When to use** | **Startup/growth stage** | **When analytics PostgreSQL becomes the bottleneck** |

---

### Decision 2: ETL frequency — how fresh does each metric need to be?

> **PM default:** Match ETL frequency to the decision cycle for that metric. Revenue and demo conversion data drives daily sales team decisions — 3-hour lag is acceptable, but 24-hour is too slow. Teacher quality data drives weekly performance reviews — daily lag is fine.

| Metric type | Decision cycle | Acceptable lag | ETL frequency |
|---|---|---|---|
| Revenue, payments, conversions | Daily sales team decisions | ≤3 hours | Every 3 hours |
| Exec summary metrics | Weekly business review | ≤1 hour (for live session data) | Hourly |
| Marketing spend vs conversion | Daily campaign optimization | ≤24 hours | Daily |
| Teacher performance, quality | Weekly performance reviews | ≤24 hours | Daily |
| Student retention, cohort analysis | Monthly product reviews | ≤24 hours | Daily |
| Real-time product feature (inventory, seat count) | Instant user action | 0 lag | Not a warehouse use case — use production DB |

---

### Decision 3: Which data belongs in the warehouse vs the production database?

> **PM default:** If a human reads it to make a decision (dashboard, report, analysis) — it belongs in the warehouse. If the application reads it to serve a user (booking confirmation, credit balance, class availability) — it belongs in production. Never blur this line.

| Data type | Where it lives | Why |
|---|---|---|
| Live user session data (current credit balance) | Production DB | Requires real-time accuracy for gating decisions |
| Historical payment records (revenue by month) | Warehouse | Aggregated for reporting; freshness lag acceptable |
| Real-time inventory count | Production DB + Cache | User-facing, time-critical |
| Marketing spend by campaign (daily reporting) | Warehouse | Batch analysis, not time-critical |
| Student cohort retention rates | Warehouse | Computed from historical data, multi-table join |
| Active class booking (live scheduling) | Production DB | Transactional, real-time |

## W3. Questions to ask your engineer

### Quick Reference
| Question | Reveals | Key Signal |
|----------|---------|-----------|
| Warehouse or production database? | Freshness lag | ETL frequency determines latency |
| Maximum data lag? | Currency for decisions | Lag must match decision cadence |
| ETL pipeline failure? | Monitoring & recovery | Alert coverage and SLA documentation |
| Cross-pipeline dependencies? | Partial staleness risk | Explicit dependency mapping needed |
| Missing ETL pipelines? | Engineering investment required | Schema compatibility before launch |
| Query performance? | Analytics limits | 2–3 min queries signal undersizing |
| Hardcoded business rules? | Silent metric drift | Reference tables vs. SQL CASE statements |

---

**1. Is this metric coming from the warehouse or the production database?**

*What this reveals:* Whether the metric has a freshness lag. If it's from the warehouse via an ETL pipeline, it has a lag equal to the ETL frequency. A "daily active users" metric sourced from a daily ETL job reports yesterday's actives as today's number. The PM's decision-making should account for that gap.

---

**2. What's the maximum data lag for this dashboard?**

*What this reveals:* Whether the dashboard's numbers are current enough for the decisions being made from them. 

**Example scenario:** The platform's payment ETL runs every 3 hours, meaning a payment made 2 hours 55 minutes ago is not reflected. If the exec team is making hourly decisions based on revenue numbers, 3-hour lag matters.

**What to ask for:** "ETL runs every X hours. Max lag is X hours. The dashboard timestamp shows last refresh time."

---

**3. What happens if an ETL pipeline fails?**

*What this reveals:* Whether there's monitoring, alerting, and a recovery path.

⚠️ **Risk:** The platform has Metabase alerts for 7 of its 12 pipelines to detect data discrepancies. But there's no documented SLA or recovery procedure for pipeline failures. If the Payment ETL fails at 9am, does the dashboard show stale payment numbers until someone notices at 3pm — or does an alert fire at 9:03am?

**What to ask for:**
- Who gets alerted?
- How fast do they get notified?
- What's the documented recovery procedure?

---

**4. Which ETL pipelines does this new dashboard depend on?**

*What this reveals:* Whether the dashboard has cross-pipeline freshness dependencies.

**Example scenario:** The BAU exec dashboard depends on Demo ETL, Payment ETL, and Marketing ETL all being fresh. If one is delayed, the dashboard is partially stale without obvious indication.

**What to ask for:** "This dashboard shows the combination of these N pipelines. All must be fresh for the numbers to be consistent."

---

**5. Is any data in this warehouse report missing an ETL pipeline?**

*What this reveals:* Whether the new metric requires an engineering investment before the dashboard can exist.

**Example scenario:** "Show me teacher attendance correlated with student renewal rates" requires Student ETL and Teacher ETL data to be joinable in the warehouse with compatible keys. If the Teacher ETL doesn't include a `student_id` field that joins to the Student ETL, the query is impossible without an ETL schema change.

**Why this matters:** The PM should know this before promising a dashboard delivery date.

---

**6. How long does the most expensive query on this dashboard take?**

*What this reveals:* Whether the analytics PostgreSQL is hitting its limits.

**Warning signal:** A query that takes 2–3 minutes indicates the analytics PostgreSQL is undersized or that the warehouse needs schema optimization (partitioning, materialized views).

**Failure scenario:** If Metabase times out on a dashboard query, the business review becomes a broken dashboard incident.

---

**7. Are there any hardcoded business rules in the ETL transformations?**

*What this reveals:* Whether a metric definition can drift silently.

**Example scenario:** The Marketing ETL hardcodes:
- Country mappings (`'BC'` → `'Vietnam'`)
- Vertical names (`1` → `'Codechamps'`)
- Channel standardizations (`'google_display'` → `'Google-Display'`)

All in SQL CASE statements.

**The problem:** When the business adds a new vertical or a new channel, someone must update the ETL SQL — or the new data appears with a null `vertical_name` in all reports.

**What to ask for:** "Business logic mappings are stored in reference tables, not hardcoded in ETL SQL."

## W4. Real product examples

### Live class platform — 12-pipeline ETL architecture

**What:** 12 ETL pipelines on AWS Glue copy and transform data from six production microservice schemas (tryouts, eklavya, paathshala, dronacharya, payments, platform) into a single analytics PostgreSQL. Metabase serves all business dashboards and reports on top.

**Why:** 
- Running analytical queries directly against production databases would slow cross-schema joins and violate microservice isolation
- Complex aggregations during peak hours would consume database CPU needed for live transactions
- The analytics PostgreSQL is tuned exclusively for analytics access patterns

**The freshness tradeoff:**

| Data | Refresh Frequency | Priority | Risk |
|------|-------------------|----------|------|
| Payment & demo | Every 3 hours | Highest (exec decisions) | Pipeline failure = stale data for hours |
| Teacher & refund | Daily | Standard | — |

*Roadmap:* Document acceptable lag SLAs per pipeline; assign active primary + backup owners to all Metabase alerts.

**PM takeaway:** The ETL catalog is a PM artifact. Every metric has an ETL source, freshness lag, and failure mode. Understanding your data's ETL provenance lets you answer "when will this dashboard be accurate?" without filing an engineering ticket.

---

### Marketing ETL — from raw ad spend to dashboard-ready dimensions

**What:** Daily AWS Glue pipeline ingests Google Ads and Facebook/Meta data, applies business logic transformations, outputs unified table:
- **Columns:** date, country_name, vertical_name, course_name, utm_updated, spend, impressions, clicks

**The transformation layer:** Raw data contains numeric vertical IDs (1, 2, 3) and country codes ('BC', 'IN', 'US'). SQL CASE statements map these to human-readable dimensions:
- `vertical_id=1` → `'Codechamps'`
- `country_code='BC'` → `'Vietnam'`

**Result:** Metabase queries join no tables at read time — just `SELECT from FINAL_OUTPUT where date between X and Y`.

**⚠️ Tech debt alert:**

| Issue | Impact | Solution |
|-------|--------|----------|
| Business logic hardcoded in SQL CASE statements | New vertical (e.g., 'Artchamps') requires code change; silent failures if missed | Move mappings to reference tables |
| NULL vertical_name silently appears in reports | Wrong data reported, no error signal | Add validation & monitoring |

*What this reveals:* Any new product vertical or marketing channel requires an ETL update as part of launch checklist.

**PM takeaway:** ETL transformations encode business definitions. "What counts as a click?" "Which vertical does this campaign belong to?" "What's the correct region?" These are product decisions that end up hardcoded in SQL. PMs own the definition; ETL must reflect it. When definitions change, ETL must change — or dashboards silently report wrong numbers.

---

### Airbnb — BigQuery migration for host analytics

**What:** Migrated from self-managed Hadoop to Google BigQuery. Production databases (MySQL, PostgreSQL) handle live bookings; BigQuery holds 10+ years of historical data optimized for analytical queries on host behavior, pricing, and demand.

**Why BigQuery over PostgreSQL at scale:**

| Factor | PostgreSQL analytics DB | BigQuery |
|--------|-------------------------|----------|
| Cost model | Fixed server cost (always-on) | Pay per TB scanned (~$5/TB) |
| Query on 1TB data | Requires massive server | Completes in <30 seconds |
| 50-analyst workload | Resource contention | Cheap & scalable |
| Ideal for | Small to mid-scale data | Petabyte-scale analytics |

**PM takeaway:** Moving from analytics PostgreSQL to columnar warehouse (BigQuery/Redshift/Snowflake) is a growth-stage decision. It happens when:
- Analytical query times degrade
- Analysts compete for resources
- Storage costs become significant

**Timeline:** 3–6 month migration project. PM's job: forecast when current system becomes a bottleneck and plan migration before performance impacts data team's ability to answer questions quickly.

---

### Snowflake — enterprise multi-tenant analytics isolation

**What:** Enterprise SaaS companies (Workday, ServiceNow, B2B platforms) use Snowflake's virtual warehouses: each team/workload gets its own compute cluster that scales independently and pauses when unused.

**Why it matters for enterprise B2B:**

> **Virtual warehouse:** Dedicated compute cluster per team or workload; scales independently; pauses/resumes in seconds with no idle cost.

Enterprise customers require data isolation at both storage (separate schemas per customer) and compute (dedicated query resources). Snowflake's architecture supports this naturally. SOC 2 audits routinely inspect warehouse tenant isolation as security requirement.

**⚠️ Compliance consideration:** For enterprise B2B SaaS, the data warehouse is part of security and compliance posture—not just a reporting tool. Enterprise procurement teams ask:
- Where does customer data live in analytics?
- How is it isolated from other tenants?
- Who has access?

**PM takeaway:** PMs building enterprise products must understand the warehouse's data governance model, not just query performance. Data warehouse architecture is a security and compliance differentiator.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands OLTP vs OLAP distinction, ETL pipelines, data freshness, star schemas, and columnar storage.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### The pipeline that silently drifted

**What happens:** The platform's Marketing ETL hardcodes business logic in SQL CASE statements. When a new vertical launches, the ETL doesn't know about it — new vertical IDs appear with NULL vertical_name in the FINAL_OUTPUT. No error. No alert. The marketing dashboard just shows a growing "NULL" row in the vertical breakdown.

**The risk:** A product manager who doesn't cross-check ETL provenance might build a roadmap on numbers that exclude 10% of the business because a new vertical was never added to the CASE statement.

⚠️ **Silent metric drift is worse than a broken dashboard — at least a broken dashboard prompts investigation.**

**PM prevention role:**

- Every product launch that adds a new categorical dimension (new course, new region, new channel) must have an ETL update as a launch blocker
- "Update the ETL CASE statements" belongs on the launch checklist with the same priority as "update the marketing copy"

---

### The bus factor on the ETL

**What happens:** The platform's 12 ETL pipelines are owned by three engineers. 

| Risk scenario | Impact |
|---|---|
| One engineer leaves | Team loses 33% of ETL knowledge |
| Two engineers leave | Exec team loses ability to maintain or debug pipelines that generate every business metric reviewed weekly |

**Why this matters:** ETL pipelines accumulate technical debt, undocumented business logic, and implicit dependencies faster than product features do. Example: the STUDENT TEACHER CLASS METRICS ETL joins data from three schemas; if the schema changes in paathshala and nobody tells the ETL owner, the pipeline fails silently or produces wrong counts.

**PM prevention role:**

- Treat ETL ownership as a product reliability conversation, not an engineering resourcing one
- Ask in sprint reviews: "Who is the backup owner for the Payment ETL? When was the pipeline last documented?"
- Roadmap the optimization: "Add a pipeline health dashboard showing last_run time, row counts, and status for all 12 pipelines"

---

### The "good enough" analytics PostgreSQL that became the bottleneck

**What happens:** The platform uses PostgreSQL for analytics — a row-oriented transactional database being asked to do columnar analytical work. At current data volumes, this works.

**The degradation curve:**
1. Data volumes grow (more students, classes, transactions, historical data)
2. Data team adds more indexes
3. Query times fall, then grow again
4. Eventually a business review query times out on Metabase
5. Exec team has no numbers for their Monday morning discussion
6. Migration to columnar warehouse happens under pressure, with data team scrambling

**PM prevention role:**

- Track analytics query p95 latency as a product health metric
- **Trigger point:** When the slowest 5% of Metabase queries exceed 60 seconds, start columnar warehouse migration planning
- Don't wait for the timeout incident

## S2. How this connects to the bigger system

### ETL Pipelines (02.06)
**The relationship:** Data warehouses are the destination; ETL pipelines are the transport mechanism.

| Aspect | Detail |
|--------|--------|
| **Core function** | Every warehouse relies on ETL (or modern ELT variant) to populate it |
| **What you need to understand** | Incremental loads, failure modes, data quality checks |
| **Platform reality** | 12 pipelines = operational infrastructure that makes warehouse useful |
| **Critical principle** | A warehouse without reliable ETL is a large, empty room |

---

### Caching (02.04)
**The relationship:** Caching and warehousing solve adjacent but different problems.

| Problem | Solution | Example |
|---------|----------|---------|
| **Caching** | Reduce latency for user-facing reads of fresh data | Feed loads in 50ms instead of 300ms |
| **Warehousing** | Enable complex analytical queries over historical data | Last quarter's revenue by region |

⚠️ **Common mistake:** Teams cache warehouse query results for dashboards (Metabase can cache for 15 minutes), but this doesn't make underlying data fresher.

**Remember:** Cache for read latency; warehouse for analytical depth.

---

### Schema Design (02.07)

| Context | Schema approach | Why | Example |
|---------|-----------------|-----|---------|
| **Production databases** | Normalized | Avoid duplication, maintain consistency | Standard relational design |
| **Data warehouses** | Denormalized | Optimize for read speed | country_name, vertical_name, course_name all as columns in single table |

**The key insight:** The Marketing ETL output (FINAL_OUTPUT) duplicates data across thousands of rows because join-free reads are faster than normalized joins at analytical scale.

⚠️ **Critical:** Schema decisions in warehouses are often *opposite* to schema decisions in production.

---

### Indexing (02.02)

| Context | Indexing strategy | Performance trade-off |
|---------|-------------------|----------------------|
| **Production databases** | Many indexes | Accelerate specific row lookups |
| **Data warehouses** | Few or no traditional indexes | Use columnar storage, partitioning, clustering instead |

**Performance reality:**
- Same query in PostgreSQL with index: **10ms**
- Same query in BigQuery without index: **5 seconds**
- Verdict: 5 seconds is acceptable for a dashboard refreshing once per day

⚠️ **Wrong answer:** Adding an index to a data warehouse

✓ **Right answer:** Partition by date instead

## S3. What senior PMs debate

### ETL vs ELT: should transformation happen before or after loading?

> **ETL (Extract-Transform-Load):** Transform data before loading into the warehouse. Traditional pattern optimized for expensive storage and limited compute.

> **ELT (Extract-Load-Transform):** Load raw data directly into the warehouse, then transform using warehouse-native tools like SQL and dbt. Modern pattern optimized for cheap storage and powerful compute.

| Aspect | ETL | ELT |
|---|---|---|
| **When it made sense** | Storage expensive, warehouse compute limited | Storage cheap (columnar), warehouse compute powerful |
| **Tools** | AWS Glue, custom pipelines | Snowflake, BigQuery, dbt |
| **Data in warehouse** | Cleaned, compact, transformed | Raw, full-fidelity, unfiltered |
| **Key advantage** | Small footprint, no raw data exposure | Retroactive transformation fixes without backfill |
| **Key risk** | Brittle transforms, hard to fix mistakes | PII/sensitive data in shared warehouse, compliance violations |

**The governance trap:** For platforms with GDPR obligations or student data, storing raw payment and student data in a shared analytics warehouse with broad analyst access isn't just a performance question—it's a data governance blocker.

⚠️ **Decision:** ETL vs ELT is a data governance decision *masquerading* as a technical one. Choose based on compliance requirements first, performance second.

---

### Real-time warehousing: does the concept make sense?

**Historical distinction:** Warehouses = batch systems. Production databases = real-time systems.

**Current reality:** Apache Kafka, Flink, and real-time OLAP systems (Druid, ClickHouse, Pinot) have collapsed this boundary. A payment event can now travel: Kafka → streaming job (sub-second) → dashboard (near-real-time).

| Business Need | Data Freshness Required | Typical ETL Latency | Match? | Example |
|---|---|---|---|---|
| Product analytics (trend spotting) | ~1 hour acceptable | Hourly batch | ✅ Yes | "How many users started the course today?" |
| Executive dashboards | ~1 hour acceptable | Hourly batch | ✅ Yes | "Revenue by cohort this month" |
| Marketing spend optimization (live campaign) | Real-time required | Hourly batch | ❌ No | "Conversion rate 5 minutes after campaign launch" |
| Campaign performance tracking | ~15 min acceptable | Hourly batch | ⚠️ Marginal | "Which ad variant is winning right now?" |

**The PM's actual question:** Does the *business decision* require real-time data, or just "fresh enough" data?

⚠️ **Cost warning:** Real-time analytical pipelines are significantly more complex and expensive than batch ETL. Most decisions that *feel* urgent work fine with 1-hour latency. Marketing spend optimization during live campaigns is the rare exception.

---

### AI needs a different data layer — and PMs need to understand why

LLM-powered features read from data layers that traditional warehouses don't serve well.

#### Data layer requirements by AI feature type

| Feature | Data Needed | Source Layer | Freshness | Right System |
|---|---|---|---|---|
| **Semantic search** ("find lessons like this one") | Content embeddings (vector representations) | Not in warehouse — computed separately | On index update | Vector database (Pinecone, pgvector, Weaviate) |
| **Personalized recommendations** ("classes for this student") | Historical engagement + behavioral patterns | Data warehouse (historical) | Daily | Warehouse → ML model → production cache |
| **Churn prediction** ("will student cancel?") | Historical usage, payment history, engagement scores | Data warehouse | Weekly | Warehouse → batch ML inference |
| **Real-time next-action suggestion** (mid-session) | Current session state + profile | Production database | Sub-second | Production DB + Redis, *not* warehouse |
| **LLM chatbot over curriculum** | Curriculum content, lesson structure | Vector store (indexed from content system) | On content update | RAG pipeline over vector store |

#### The three-layer architecture

AI features require up to three data layers running in parallel:

1. **Production database** — real-time transactional facts (current session, live state)
2. **Data warehouse** — historical analytical context (cohort patterns, retention signals, engagement history)
3. **Vector store** — semantic retrieval layer (embeddings of content, student behavior, past interactions)

#### The PM scoping question at design time

Ask: *"Which layer does this feature read from, how fresh must the data be, and is that layer already built?"*

**Example 1:** Churn model reading from warehouse (exists) = 2-week integration
**Example 2:** Semantic search requiring new vector pipeline (doesn't exist) = 3-month infrastructure project

⚠️ **Most common mistake:** Assuming the data warehouse can serve inference directly. It can't. Warehouses train and fine-tune pipelines; they don't power live feature inference.