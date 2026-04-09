---
lesson: Data Quality & Pipelines
module: 06 — metrics and analytics
tags: product
difficulty: working
prereqs:
  - 06.07 — Dashboards & BI Tools: dashboards are only as accurate as the pipelines feeding them
  - 02.06 — ETL Pipelines: technical foundation for how data moves from production to analytics
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/etl-and-async-jobs/etl-pipeline-inventory.md
  - technical-architecture/infrastructure/infra-monitoring.md
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

At some point in every PM's career, they get the same uncomfortable moment. You're in a leadership review presenting metrics — a chart showing user growth or conversion improvement. Someone from the data team raises their hand: "Wait, that dashboard hasn't been updated since Tuesday. The pipeline broke two days ago."

Every data point you just presented was stale. The product decision you were about to recommend was based on numbers that didn't reflect what was actually happening.

This happens constantly. Dashboards show last week's numbers labeled as "today." A key metric looks flat for three days, then jumps — not because users changed their behavior, but because a broken pipeline backfilled three days of missing data all at once. A feature looks like it's failing, so the PM asks for it to be rolled back, but the metrics were just wrong: the tracking code had a bug.

Bad data doesn't announce itself. It looks exactly like good data. A dashboard with stale numbers displays the same chart as one with fresh numbers. A metric calculated with a buggy formula looks identical to one calculated correctly — until someone checks.

The discipline that prevents this is called data quality management. It's not glamorous. It doesn't ship features. But every metric you report, every decision you make from a dashboard, and every A/B test you evaluate depends on data quality being maintained. A PM who doesn't understand how their data gets from production systems to dashboards is navigating with a map that might be wrong — and doesn't know it.

> **Why this is a PM responsibility, not just engineering:** Data engineers build and maintain pipelines. But PMs are the primary consumers of the data — and the ones who present metrics to leadership. If you don't understand how your data was produced, you can't tell when it's wrong. You can't ask the right questions. You can't catch the moment when a great-looking metric is actually a pipeline artifact. Understanding data quality is not optional for a PM who makes decisions from data.

## F2 — What it is, and a way to think about it

> **ETL (Extract, Transform, Load):** The three-step process that powers every data pipeline.

| Step | Action | Purpose |
|---|---|---|
| **Extract** | Pull data from production systems | Source the raw data |
| **Transform** | Apply business logic (calculations, joins, cleaning) | Prepare data for analysis |
| **Load** | Write results to the analytics database | Make data queryable by dashboards |

⚠️ **Risk:** When any step fails, your dashboard shows old or wrong data.

> **Data pipeline:** The automated, scheduled process that runs ETL on a set schedule — hourly, daily, every few hours — to keep your analytics database current. When someone says "the pipeline broke," they mean the ETL job failed to complete one or more of its steps.

> **Data quality:** The degree to which data is accurate, complete, fresh, and consistent enough to make reliable decisions. Data quality is not binary — it degrades in specific, detectable ways.

### A way to think about it: The water supply analogy

A city's water supply flows from reservoir → pipes → tap. At any point, something breaks:
- A pipe ruptures
- A filter clogs  
- A valve closes

When you turn on the tap, water looks fine — but it could be from a different source, stale, or contaminated mid-journey.

**Data pipelines work identically.**

Data flows: production databases → ETL jobs → data warehouse → Metabase dashboard

At any point, something breaks. The dashboard number looks fine — but it could be stale, incomplete, or calculated from a broken formula.

**The job of data quality management is to:**
1. Know when the water stopped flowing
2. Know what caused it
3. Know how to fix it before anyone drinks the bad water

### The five dimensions of data quality

| Dimension | What it means | What breaks it |
|---|---|---|
| **Freshness** | Is the data current? Does it reflect today's reality? | Pipeline failed overnight; data is from yesterday |
| **Completeness** | Is all the data there? Are there missing rows or events? | Tracking code bug; ETL missed a time window |
| **Accuracy** | Does the number reflect what it's supposed to measure? | Formula bug; wrong join condition; double-counting |
| **Consistency** | Does the same metric show the same number everywhere? | Two pipelines calculate a metric differently |
| **Lineage** | Can you trace where a number came from? | No documentation; no audit trail when something looks wrong |

## F3 — When you'll encounter this as a PM

### Quick reference: Pipeline failure scenarios

| Context | Risk | First move |
|---|---|---|
| Dashboard metric looks wrong | Stale data vs. real behavior | Check last-updated timestamp |
| A/B test results arrive | Invalid results if tracking failed | Verify no pipeline failures during experiment window |
| Feature launch monitoring | Can't detect early impact with lag | Check pipeline frequency vs. launch timing |
| OKR / quarterly review | Reporting on corrupted numbers | Request pipeline health log before review |
| Stakeholder questions | Defending wrong numbers | Say "Let me verify the pipeline was running" |

---

### Dashboard metric looks wrong
**What happens:** A number changes dramatically overnight or flatlines for days.

**What you need to know:** Could be real user behavior *or* pipeline failure — these look identical in the dashboard.

**What to do:** 
1. Check the last-updated timestamp
2. If stale, ask data team: "Which pipeline feeds this metric and when did it last run?"

---

### A/B test results arrive
**What happens:** Experiment shows a winner with high confidence.

**What you need to know:** Results are only valid if tracking was working correctly for the full experiment window.

**What to do:** Before declaring a winner, ask: *"Were there any pipeline failures during the experiment window?"*

---

### Feature launch monitoring
**What happens:** You're watching metrics post-launch.

**What you need to know:** Is the metric reflecting the launch, or is there a 3-hour lag in the pipeline? A 3-hour-lag pipeline can't tell you what happened in the first 2 hours.

**What to do:** Check pipeline frequency for your launch metrics before launch day.

---

### OKR / quarterly review
**What happens:** You're reporting on metric performance.

**What you need to know:** Were there any pipeline failures this quarter that affected the numbers you're reporting?

**What to do:** Ask data team for a pipeline health log *before* your review. Flag any known gaps when presenting.

---

### Stakeholder question
**What happens:** "This number looks off."

**What you need to know:** Can you answer confidently, or do you have to say "I'll check with the data team"?

**What to do:** Say *"Let me verify the pipeline was running correctly for that period"* — this is the right first move, not defending the number.

---

### BrightChamps — Data pipeline infrastructure at scale

**What:** 12 ETL pipelines running continuously across 5 production database schemas (tryouts, eklavya, paathshala, dronacharya, payments). Data moves through AWS Glue into an analytics database surfaced via Metabase. The BAU pipeline (most business-critical, feeding the exec dashboard) runs hourly.

**Why:** When any pipeline breaks, every dashboard and metric downstream goes stale until recovery.

**Takeaway:** A PM reviewing BrightChamps metrics needs to know:
- Which pipeline feeds which metric
- How frequently each runs
- Where to check when a number looks suspicious
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

> **PM framing for this section:** You don't need to write ETL code. You need to understand the mechanics well enough to ask good questions, interpret pipeline failures correctly, and diagnose whether a metric problem is a product problem or a data problem. The rest of this section explains what you need to know — and why.

---

### The ETL pipeline mechanics

Data pipelines follow a three-step process:

> **Extract:** Pull data from source systems (production databases, event tracking, third-party APIs). This step must be read-only — ETL jobs that write back to production databases can corrupt live systems.

> **Transform:** Apply business logic to the raw data. This is where calculations happen: join tables, apply CASE statements to derive categories, aggregate by dimensions, handle null values with COALESCE, clean inconsistencies. This is also where most bugs live.

> **Load:** Write the transformed data to the analytics database or data warehouse. This step can be incremental (only new/changed rows) or full (overwrite the entire table). Incremental is faster and better for large tables (less data moved, less risk of table lock). Full load is simpler and always produces a consistent known state — but expensive at scale and slower to recover if something goes wrong mid-run.

---

### How pipelines fail (and what each failure looks like)

| Failure type | What causes it | What you see | How to detect |
|---|---|---|---|
| **Complete stop** | Pipeline crashes, Glue job errors out | Metric flatlines; dashboard shows old data | Last-updated timestamp stops changing |
| **Partial failure** | One table in a multi-table pipeline fails | Metric present but some dimensions missing | Row count lower than expected; filter shows incomplete data |
| **Silent staleness** | Pipeline runs but source data isn't refreshing | Numbers look plausible but are old | Cross-check with another data source for same metric |
| **Backfill spike** | Pipeline was broken, then fixed | Metric jumps suddenly after flat period | Sudden change in metric coincides with pipeline fix |
| **Formula bug** | Transform logic miscalculates a metric | Number consistently wrong, not missing | Metric diverges from expected based on related metrics |
| **Schema drift** | Production database changes a column name or type | Pipeline fails on next run | Transform step throws error; data stops loading |

---

### BrightChamps pipeline architecture

```
Production databases (PostgreSQL)
├── tryouts schema        → DEMO ETL (3h), DEMO CLASS ETL (3h), MARKETING ETL (daily)
├── eklavya schema        → STUDENT ETL (3h), STUDENT CLASS BALANCE ETL (daily), REFUND ETL (daily)
├── paathshala schema     → PAID CLASS ETL (3h), STUDENT TEACHER CLASS METRICS ETL (daily)
├── dronacharya schema    → TEACHER ETL (daily)
├── payments schema       → PAYMENT ETL (3h), ADDONS ETL (3h)
└── all schemas           → BAU ETL (hourly, via Lambda)
                                    ↓
                          Analytics PostgreSQL
                                    ↓
                    Metabase (analytics.brightchamps.com)
```

#### Pipeline lag by priority

| Pipeline | Frequency | Maximum lag | Business impact of failure |
|---|---|---|---|
| BAU ETL | Hourly | 1–2 hours | Exec dashboard stale; revenue reporting delayed |
| PAYMENT ETL | Every 3 hours | 3–6 hours | Payment reconciliation delayed |
| STUDENT ETL | Every 3 hours | 3–6 hours | Student onboarding metrics delayed |
| DEMO ETL | Every 3 hours | 3–6 hours | Sales funnel metrics delayed |
| TEACHER ETL | Daily | 24 hours | Teacher supply metrics 1 day stale |
| STUDENT CLASS METRICS | Daily | 24 hours | Attendance and learning metrics 1 day stale |

---

### How data quality monitoring works

BrightChamps monitors pipeline health through Metabase alert queries. Each alert compares what the ETL produced against an independent reference count:

| Alert | What it monitors |
|---|---|
| `DEMO ETL: bookings vs ETL` | Raw booking count in source DB vs. ETL output — detects missed rows |
| `MARKETING ETL: marketing alert` | Marketing spend in source vs. ETL — detects missing campaign data |
| `PAYMENT ETL: collection mismatch` | Payment amounts in source vs. ETL — detects revenue calculation errors |
| `ADDONS ETL: addon mismatch` | Add-on transactions source vs. ETL — detects missing add-on data |
| `STUDENT ETL: missing students` | Students in source DB not present in analytics — detects gap in student data |
| `BAU ETL: demo/class/leads differences` | Three separate checks: joined demos, completed classes, total leads |

⚠️ **Alert blindness risk:** A pipeline alert fires when the data looks wrong — when the ETL output doesn't match what the source database shows. But alerts only catch what they're designed to catch. A formula bug that miscalculates a metric consistently won't fire a row-count alert, because the right number of rows are present — just calculated incorrectly.

## W2 — The decisions this forces

### Decision 1: How fresh does this metric need to be?

Not all metrics have the same freshness requirement. Setting freshness requirements upfront determines which pipeline failures are critical (stop everything) vs. acceptable (fix by morning).

**Framework for freshness requirements:**

| Decision type | Required freshness | Rationale |
|---|---|---|
| Real-time operational decisions (teacher dispatch, payment confirmation) | <5 minutes | Delays cause immediate user harm |
| Daily business decisions (campaigns, pricing changes) | Same-day (hourly) | Decisions made by EOD need today's data |
| Weekly product reviews | 24 hours | Day-old data still surfaces meaningful trends |
| Quarterly/OKR reporting | 48 hours | Slight staleness acceptable; trends matter more than point-in-time accuracy |
| Historical analysis | Any | Freshness is irrelevant for analysis of completed periods |

**What this means for BrightChamps:**

The BAU ETL runs hourly and is calibrated for daily business decisions.
- **9am failure → 11am impact:** 2 hours stale — acceptable
- **Still broken at 5pm:** Entire day's metrics unreliable for EOD decisions

---

### Decision 2: What is the response protocol when a pipeline fails?

A pipeline failure without a defined response protocol leads to two bad outcomes:
1. Nobody notices until a stakeholder asks why the dashboard looks wrong
2. Everyone panics and starts making assumptions about what the data might show

**Standard response protocol for pipeline failures:**

| Step | Who owns it | What it looks like | SLA |
|------|-------------|-------------------|-----|
| **1. Detect** | Engineer (via alert) or PM (via unusual metric) | Alert fires in Slack; PM notices stale last-updated timestamp | Immediate |
| **2. Assess severity** | PM (business impact) + Engineer (technical scope) | PM asks: which metrics affected, who depends on them, what decisions blocked? Engineer diagnoses root cause | Within 30 min of detection |
| **3. Communicate** | PM | "The PAYMENT ETL has been down since 6am. Payment reports are 9 hours stale. ETA to fix: 3 hours. Do not make pricing decisions from today's dashboard." | Before any stakeholder is caught by surprise |
| **4. Isolate** | PM | Block product decisions based on affected metrics until pipeline recovers and backfills. Flag any meeting where stale data is relevant | Until pipeline restored |
| **5. Restore** | Engineer | Fix root cause, trigger backfill, verify row counts match source | Per pipeline SLA |
| **6. Post-mortem** | PM + Engineer | Is this the third failure of this type? If yes, escalate as reliability risk, not just incident | Within 48 hours of restore |

> ⚠️ **PM accountability:** Engineers own fixing the pipeline. PMs own communicating the impact and blocking bad decisions during outage. Both are required — engineering alone is not enough.

> ⚠️ **The worst response to a pipeline failure:** Presenting stale data in a stakeholder meeting without flagging it's stale. If you notice the dashboard shows no updates for 12 hours, say so before the meeting — don't discover it during the presentation.

---

### Decision 3: What data quality audits should a PM own?

Data quality is not just an engineering responsibility. PMs who rely on data need to understand what questions to ask and when to challenge a number.

**PM-owned data quality checks:**

| Check | When to run | How to do it |
|---|---|---|
| **Freshness check** | Before every important review | Look at "last updated" or filter for today's date — is data from today present? |
| **Sanity check** | Any time a metric looks unusual | Compare against a related metric. If DAU is down 40% but conversions flat, something is wrong with one of them |
| **Cross-source check** | When a metric diverges from expectation | Check the same metric in two different dashboards. If they disagree, there's a calculation inconsistency |
| **Baseline check** | After A/B experiment ends | Were there pipeline failures during the experiment window? Failures invalidate results |
| **Definition check** | When a new metric appears | How exactly is this metric calculated? What's included and excluded? |

---

### Decision 4: Build vs. buy for data quality tooling

As a PM, you'll often advocate for data quality investments. The decision is usually: keep monitoring manually (current state) vs. invest in dedicated data quality tooling.

| Approach | What it looks like | When it's right |
|---|---|---|
| **Manual monitoring + Metabase alerts** | Engineers write alert queries; team checks Slack | Early-stage; low data volume; small data team |
| **Dedicated data observability tool** (Monte Carlo, Soda, Great Expectations) | Automated anomaly detection, lineage tracking, schema drift alerts | Data is critical to core product decisions; multiple pipelines; >3 data consumers |
| **Embedded data quality in pipeline** | Validation checks run as part of each ETL job | High-reliability requirement; compliance context |

**BrightChamps current state:**
- Manual monitoring via 9 Metabase alert queries across 6 pipelines
- Managed by 3 engineers
- ⚠️ **Bus factor risk:** If all three engineers unavailable simultaneously, monitoring breaks down

---

### Decision 5: How to communicate data uncertainty to stakeholders

A PM who always reports numbers as definitive facts loses credibility the first time a number turns out to be wrong. A PM who communicates data quality context earns trust — and makes better decisions.

| Situation | How to communicate |
|---|---|
| Data is fresh and validated | "Conversion is 4.2% this week, up from 3.8% last week" |
| Data might be stale | "The dashboard shows 4.2% as of yesterday morning — pipeline was down overnight, recovering now" |
| Metric definition is ambiguous | "This is active users by our standard definition (any session ≥30s in 7 days), not total logins" |
| Data from a period with known quality issues | "Note: we had a tracking bug affecting events from March 10–14; these numbers exclude that window" |
| Two dashboards disagree | "There's a discrepancy between Metabase and the Google Sheet model — I'm investigating before drawing conclusions" |

## W3 — Questions to ask your team

### Quick Reference
| Question | Reveals | Risk Level |
|----------|---------|-----------|
| Pipeline source & last run | Data lineage documentation | 🔴 High |
| Alert ownership | Incident response process | 🔴 High |
| Pipeline failures during experiment | Data integrity during tests | 🔴 High |
| Metric SQL formula | Understanding vs. inheritance | 🟡 Medium |
| Backfill behavior | Analysis rigor | 🟡 Medium |
| Known data quality issues | Team communication health | 🟡 Medium |
| Pipeline ownership redundancy | Bus factor risk | 🟠 Medium-High |
| Double-count validation | Data validation testing | 🔴 High |

---

### **1. "Which pipeline feeds this metric, and when did it last run successfully?"**

Every metric on a dashboard comes from a pipeline. You should be able to trace any number to its source — which pipeline produces it, how often it runs, when it last succeeded.

*What this reveals:* Whether the data team has documented lineage, or whether metrics are black boxes. Undocumented lineage is a red flag for data quality risk.

---

### **2. "What does this alert mean, and who responds when it fires?"**

> **Alert Theater:** A monitoring alert that fires and sits unread in a Slack channel — not actionable monitoring, just noise.

Monitoring alerts are only useful if someone acts on them.

*What this reveals:* Whether the data team has an on-call rotation or incident response process for data quality failures.

---

### **3. "Has there been any pipeline failure during this experiment window?"**

A/B test results are invalid if tracking broke during the test. This question should be asked before shipping any experiment result.

*What this reveals:* Whether the data team routinely checks for pipeline health before declaring experiment winners.

---

### **4. "How is this metric calculated — show me the SQL?"**

If you can't get a plain-language explanation of how a metric is computed, you can't trust it.

**Common red flags in metric formulas:**
- Incorrect join condition
- Missing filter
- Wrong aggregation logic

These produce numbers that *look* fine but measure the wrong thing.

*What this reveals:* Whether anyone on the team fully understands the metric, or whether it's been inherited from a previous analyst and nobody has reviewed it.

---

### **5. "What happens to this metric when the pipeline backfills after a failure?"**

When a pipeline recovers from a multi-day failure, it often backfills missing data all at once. This creates a sudden jump in cumulative metrics (total conversions, total revenue) that *looks* like a spike when it's actually a catch-up.

*What this reveals:* Whether the team distinguishes real trend changes from backfill artifacts in their analysis.

---

### **6. "Are there any known data quality issues we should be aware of for this period?"**

Before any major review, ask this question. The data team often knows about issues that haven't been communicated upstream.

*What this reveals:* The health of communication between data engineering and product. If you never hear about data quality issues, it's not because there are none.

---

### **7. "Who owns this pipeline when [primary owner] is unavailable?"**

⚠️ **Bus Factor Risk:** If one engineer owns 8 pipelines and is on vacation, what happens when one breaks?

*What this reveals:* Whether the data infrastructure has redundant ownership or is a single-point-of-failure operation.

---

### **8. "How would we know if this metric were being double-counted?"**

⚠️ **Double-Counting Bug:** A row appears twice in a join, so a count metric is inflated 2x. The metric looks plausible; it's just wrong by a factor of two.

*What this reveals:* Whether the team has data validation tests that would catch this, or whether they rely on intuition.

## W4 — Real product examples

### BrightChamps — 12 pipelines, 3 owners, and the reliability question

**What:** BrightChamps runs 12 ETL pipelines processing all core business data — demos, payments, students, teachers, classes, marketing spend, refunds, and add-ons. Every number that appears in any Metabase dashboard flows through one or more of these pipelines.

**Pipeline inventory:**

| Frequency | Count | Domains | Owner(s) |
|-----------|-------|---------|----------|
| Every 3 hours | 6 | Payments, demos, students (revenue-critical) | Kashyap, Sarkar |
| Every 24 hours | 5 | Teachers, class metrics, refunds (operational) | Kashyap, Sarkar, Bhaskara |
| Every hour | 1 | Executive reporting dashboard (BAU) | Bhaskara |

**Ownership distribution:**
- Kadambi Kashyap: 4 pipelines
- Ishan Sarkar: 7 pipelines
- Ankitha Bhaskara: 1 pipeline

**Monitoring:**
- 9 Metabase alert queries monitor row count discrepancies across 6 critical pipelines

**The data quality gap:**

⚠️ **No documented SLA** for acceptable pipeline lag per business domain  
⚠️ **No documented recovery procedure** if a pipeline falls behind  
⚠️ **No backup ownership** when primary owners are unavailable  

When a pipeline breaks, recovery time depends entirely on the primary owner being reachable — not on a defined process.

**What a PM should ask:**

> "What's the last time each of these pipelines failed, and how long was the outage?"

*What this reveals:* If the answer is unknown, the team doesn't have sufficient visibility into pipeline reliability. If recent failures are known, ask whether the root causes were addressed.

---

### BrightChamps — the BAU ETL: when the exec dashboard is wrong

**What:** The BAU ETL runs every hour via AWS Lambda, consolidating demo, payment, and student data into the exec-facing dashboard. It's the pipeline that most leadership-level decisions depend on.

**The architecture concern:** 

The BAU ETL uses a different stack (SQL + Python + Lambda) than the 11 AWS Glue-based pipelines:

| Dimension | BAU ETL | Other Pipelines |
|-----------|---------|-----------------|
| Stack | SQL + Python + Lambda | AWS Glue (11 pipelines) |
| Failure modes | Lambda-specific | Glue-specific |
| Debugging paths | Differs | Differs |
| Monitoring instrumentation | Differs | Differs |

⚠️ This inconsistency means the BAU ETL has different failure modes and debugging paths than the rest of the pipeline fleet. The ETL pipeline inventory document flags this as a consistency issue.

**The data quality risk:**

Three separate Metabase alert queries monitor BAU ETL health:
- Demo-joined difference alert
- Total-completed difference alert
- Total-leads difference alert

**Alert firing patterns:**

| Scenario | Signal |
|----------|--------|
| All three fire simultaneously | BAU ETL has failed across all dimensions |
| One fires | A specific data category has a discrepancy while others appear correct |

**PM action:** Before any exec review, confirm the BAU ETL has completed successfully within the last two hours. If any of the three BAU alert queries are showing discrepancies, treat the dashboard numbers as unreliable until resolved.

---

### Metabase alert architecture: what monitoring catches (and doesn't)

**What:** BrightChamps uses 9 Metabase alert queries to detect pipeline failures. Each alert is a SQL query that compares the ETL output against the raw source data.

**What monitoring catches:**

✓ Complete pipeline failure (no rows loaded in the expected window)  
✓ Missing records (students/payments in source not appearing in analytics)  
✓ Revenue calculation mismatches (payment ETL output differs from source total)

**What monitoring doesn't catch:**

✗ Formula bugs that produce consistently wrong calculations (row count is correct; values are wrong)  
✗ Schema drift issues where columns are renamed but the transform logic still runs (queries against old column name may silently return nulls)  
✗ Semantic changes where a business definition changes but the SQL formula doesn't update

**The implication for PMs:**

> **Row-count alerts:** A first line of defense, not a complete guarantee of data quality.

When a metric looks wrong but the alerts aren't firing, the bug is likely in the transform logic — which requires someone to read the actual SQL.

---

### Meta — the data quality incident that affected reported MAU

**What:** In Q4 2021, Meta disclosed that its reported monthly active user counts included duplicate accounts and accounts belonging to banned users — populations that inflated the headline MAU number. Meta's stock dropped ~26% in after-hours trading following the earnings disclosure, erasing over $200B in market cap in a single session.

**The data quality failure:**

The definition of "active user" in the reporting pipeline did not match the business intent:

| Population | Issue | Impact on MAU |
|-----------|-------|----------------|
| Duplicate accounts | User counted once for Facebook + once for Instagram | Counted as 2 users instead of 1 |
| Banned users with new accounts | Re-created accounts counted again | Phantom growth in reported MAU |

The pipeline was calculating exactly what it was told to calculate — the formula was just wrong relative to what the metric was supposed to measure.

**What PMs can apply:**

> **Metric drift:** Metric definitions change over time. A metric that was accurate 18 months ago may no longer reflect the business reality it was designed to measure.

**Defense:** Conduct annual definition audits — asking "is the SQL formula still measuring what we think it's measuring?" — to catch silent metric drift before it surfaces publicly.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The bus factor failure

**BrightChamps's situation:**
- 3 engineers own the entire pipeline fleet
- 8 of 12 pipelines lack documented backup owners
- Primary pipeline engineer is a single point of failure

**Typical failure sequence when owner is unavailable:**

| Time | Event | Impact |
|------|-------|--------|
| 2:00 AM | Pipeline silently fails | No immediate detection |
| 2:00–9:00 AM | No alert reaches available staff | 7-hour gap |
| 9:00 AM | Stakeholders notice incorrect data in standup | Problem surfaces |
| 9:00–12:00 PM | 3 hours diagnosing while locating owner | Business decisions delayed |
| 12:00–2:00 PM | 2 hours fixing and backfilling | Data remains stale |
| **Result** | Data is 8+ hours old | Business impact |

**The misconception:** More engineers solve this.

**The actual fix:**
- Backup ownership documentation for every pipeline
- Runbooks for common failure modes
- Alert routing to secondary owners

> **Key insight:** Three engineers *can* own 12 pipelines with appropriate documentation; they *cannot* own 12 pipelines without it.

---

### The compounding error problem

**How errors cascade:**

BrightChamps's BAU ETL aggregates data from multiple source pipelines. When the DEMO ETL produces incorrect data (backfill artifact, formula bug), the BAU ETL incorporates it faithfully into the exec dashboard.

| Stage | Problem | Time cost |
|------|---------|-----------|
| Error occurs in DEMO ETL | Bad data enters system | — |
| BAU ETL runs 3–4 times before error detected | Bad data cached in Metabase multiple times | Hours |
| Fix source pipeline | DEMO ETL corrected | ~1 hour |
| Rerun affected time windows | Regenerate correct data | ~1 hour |
| Refresh all downstream pipelines | Propagate corrections | ~1 hour |
| Invalidate Metabase cache | Clear stale results | ~30 min |
| **Total recovery time** | Often exceeds original failure duration | **3–5 hours** |

> **Compounding effect:** Each downstream pipeline that incorporated bad data becomes a point that must be corrected, multiplying recovery effort.

---

### Schema drift as a silent killer

> **Schema drift:** Untracked changes to production database structure (column renames, type changes, table additions, field deprecations) that break or silently corrupt ETL pipelines.

**Two failure modes:**

| Mode | Scenario | Detection |
|------|----------|-----------|
| **Loud failure** | Column is deleted | ETL errors immediately; alerts fire |
| **Silent corruption** | Column renamed (e.g., `booking_date` → `created_at`) | ETL finds *a* column named `booking_date` (perhaps from legacy view or different join path) and runs successfully with wrong data |

**Why silent corruption is dangerous:**

- Row counts look correct
- No alerts fire
- All data appears valid
- Date dimension in all downstream reports is now systematically wrong
- Error may go undetected for days or weeks

⚠️ **Risk:** Silent schema drift corrupts entire reporting layers without triggering any technical alerts. Detection relies on stakeholders noticing incorrect business logic.

**Why it persists:**

Schema drift has no automatic fix. Someone must:
1. Review all ETL transform logic
2. Compare against current production schema definitions
3. Repeat whenever production schemas change

This requires communication between production engineering and data engineering teams — communication that often doesn't happen.

## S2 — How this connects to the bigger system

| Concept | Connection | Key Interaction |
|---|---|---|
| **Dashboards & BI Tools (06.07)** | Front end of the data pipeline | Metabase accuracy depends on most recent successful ETL run |
| **ETL Pipelines (02.06)** | Technical foundation for data movement | Data quality = pipeline reliability output measure |
| **Monitoring & Alerting (03.09)** | Shared architecture for infrastructure & data monitoring | New Relic (service health) + Metabase (data health) both required |
| **Experimentation & A/B Testing (05.07)** | Experiment validity depends on data quality | Pipeline failure during experiment window = invalidated results |
| **Counter Metrics (06.09)** | Data quality issues disguise as product metric changes | Pipeline failure metric drop ≈ real product problem (indistinguishable) |
| **North Star Metric (06.01)** | North star reliability = pipeline calculation reliability | North star degradation from pipeline bug ≠ product problem |

### The product-data team relationship

> **Joint Responsibility:** Data engineers own pipeline reliability; PMs own metric definitions and escalation when numbers look wrong.

#### The failure mode

- Data engineers assume PMs will flag suspicious numbers
- PMs assume data engineers will proactively communicate pipeline failures
- **Result:** Nobody communicates; stale data reported as fact

#### The fix — defined protocol

1. **Data engineers** communicate pipeline health status proactively before important reviews
2. **PMs** perform basic sanity checks before presenting metrics
3. **Both sides** post pipeline incidents immediately to shared Slack channel

## S3 — What senior PMs debate

### "Should we move to real-time pipelines for core business metrics?"

The appeal is obvious: real-time data means decisions aren't delayed by pipeline lag. Payments visible in 5 seconds, demo bookings reflected instantly, no more "the pipeline hasn't run yet" explanations.

The cost is less obvious:

| Consideration | Batch ETL | Real-time / streaming |
|---|---|---|
| **Infrastructure cost** | Lower — Glue and Lambda are relatively cheap | Higher — Kafka, Flink, or Kinesis add significant cost and operational complexity |
| **Engineering complexity** | Moderate — SQL transforms are readable and debuggable | High — streaming logic is harder to test, debug, and monitor |
| **Data quality control** | Transforms can be reviewed and tested before each run | Errors propagate in real-time — catching and fixing a streaming bug is harder |
| **Appropriate for** | Business metrics (daily/hourly decisions), historical analysis | Operational triggers (payment confirmation, notification dispatch), sub-minute decisions |

**Current consensus:** Real-time is right for operational triggers (did this payment go through? dispatch a teacher now). Batch ETL is right for business metrics (how did this cohort perform this week?). Most companies use both, with the separation determined by latency requirement and consequence of error.

---

### "Who really owns data quality — engineering or product?"

The answer differs by function:

| Layer | Owner | Responsibility |
|---|---|---|
| Pipeline reliability | Data engineering | Pipeline runs on schedule; row counts match source; alerts fire when they should |
| Metric definitions | Product | "Active user" means sessions ≥30s, not logins; conversion includes first payment only |
| Metric interpretation | Product + Analytics | What does a 5% drop in this metric actually mean for the business? |
| Data quality culture | Everyone | PMs check before presenting; engineers communicate failures; analysts flag anomalies |

**The resolution is always the same:** Define ownership upfront, not after the incident. The debate is usually triggered when a metric turns out to be wrong and two teams point at each other.

---

### "What does AI do to data quality requirements?"

AI/ML models that power product features (recommendation systems, prediction models, content ranking) have a harder relationship with data quality than dashboards do:

**Stale data impact**
- A dashboard with stale data shows old numbers
- A model trained on stale data makes wrong decisions — often without any visible indication of the error

**Formula bugs**
- A dashboard with a formula bug shows a wrong number
- A model trained on a formula-bug-corrupted feature set learns the wrong relationship — and continues making wrong predictions after the bug is fixed, until the model is retrained

**Distributional stability**
Data quality for ML requires not just freshness and accuracy but distributional stability — has the distribution of values in this feature changed significantly from when the model was trained?

> **Distributional drift:** When the statistical properties of input data change from the distribution on which a model was trained, causing silent prediction errors.

⚠️ **Silent failures:** Models trained on corrupted or stale data often degrade invisibly. Unlike dashboards, there's no clear signal that something is wrong until business metrics deteriorate.

---

**For PMs building AI features:**

Every model in production is a pipeline with data quality requirements. "The model is making weird recommendations" is often a data quality problem (feature distribution drift, stale training data, missing records) masquerading as a model performance problem. Senior PMs who understand this can direct debugging toward data quality issues rather than model retraining — which saves weeks.