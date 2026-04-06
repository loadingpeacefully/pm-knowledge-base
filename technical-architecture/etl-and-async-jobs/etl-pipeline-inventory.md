---
title: ETL Pipeline Inventory & Metadata Catalog
category: technical-architecture
subcategory: etl-and-async-jobs
source_id: 991c8087-5207-470f-88f3-b76fb8251d45
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# ETL Pipeline Inventory & Metadata Catalog

## Overview
This document is the master catalog of all BrightCHAMPS ETL pipelines, covering 12 pipelines that process demo, class, teacher, marketing, payment, student, and business analytics data. All pipelines run on AWS Glue with PostgreSQL as both source and target, and are owned by two engineers (Kadambi Kashyap and Ishan Sarkar), with Ankitha Bhaskara owning the Paid Class ETL.

## API Contract
N/A — ETL pipeline inventory document.

## Logic Flow
### Controller Layer
N/A — ETL pipelines are batch/scheduled jobs, not HTTP APIs.

### Service/Facade Layer
**Complete Pipeline Inventory:**

| # | Pipeline | Description | Owner | Platform | Source → Target | Frequency | Status | Incremental |
|---|----------|-------------|-------|----------|-----------------|-----------|--------|-------------|
| 1 | DEMO ETL | Student bookings with course, vertical, region, and country data | Kadambi Kashyap | AWS Glue | PostgreSQL → PostgreSQL | Every 3 hours | Healthy | Yes |
| 2 | DEMO CLASS ETL | Student + teacher demo class details: durations, feedback, join/leave timestamps | Kadambi Kashyap | AWS Glue | PostgreSQL → PostgreSQL | Every 3 hours | Healthy | Yes |
| 3 | TEACHER ETL | Unified teacher dataset: employment, contacts, teaching preferences, metadata | Kadambi Kashyap | AWS Glue | PostgreSQL → PostgreSQL | Daily | Healthy | Yes |
| 4 | MARKETING ETL | Performance marketing spend from Facebook + Google with course/vertical/region data | Kadambi Kashyap | AWS Glue | PostgreSQL → PostgreSQL | Daily | Healthy | Yes |
| 5 | STUDENT TEACHER CLASS METRICS ETL | Attendance, assignments, assessments, certificates — operational + strategic metrics | Kadambi Kashyap | AWS Glue | PostgreSQL → PostgreSQL | Daily | Healthy | Yes |
| 6 | PAYMENT ETL | Sales and payment data: package sales, payments, associated entities | Ishan Sarkar | AWS Glue | PostgreSQL → PostgreSQL | Every 3 hours | Healthy | Yes |
| 7 | STUDENT CLASS BALANCE ETL | Class balance data: bookings, completed classes, penalties, other metrics | Ishan Sarkar | AWS Glue | PostgreSQL → PostgreSQL | Daily | Healthy | Yes |
| 8 | ADDONS ETL | Add-on purchase transactions: payment details, timing, contextual attributes | Ishan Sarkar | AWS Glue | PostgreSQL → PostgreSQL | Every 3 hours | Healthy | Yes |
| 9 | REFUND ETL | Unified refund view: reasons, students, courses, verticals, financial metrics | Ishan Sarkar | AWS Glue | PostgreSQL → PostgreSQL | Daily | Healthy | Yes |
| 10 | STUDENT ETL | Unified student records: standardized, cleaned, enriched with country/language | Ishan Sarkar | AWS Glue | PostgreSQL → PostgreSQL | Every 3 hours | Healthy | Yes |
| 11 | PAID CLASS ETL | Paid classes, PTMs, and groups — unified class view for operational decisions | Ankitha Bhaskara | AWS Glue | PostgreSQL → PostgreSQL | Every 3 hours | Healthy | Yes |
| 12 | BAU ETL | Business-as-usual dashboard: marketing + demo + payment metrics for exec reporting | Ishan Sarkar | SQL + Python + AWS Lambda | PostgreSQL → PostgreSQL | Every hour | Healthy | Yes |

### High-Level Design (HLD)
```
Production Microservice DBs (PostgreSQL)
├── tryouts schema → DEMO ETL, DEMO CLASS ETL, MARKETING ETL
├── eklavya schema → STUDENT ETL, STUDENT CLASS BALANCE ETL, REFUND ETL
├── paathshala schema → PAID CLASS ETL, STUDENT TEACHER CLASS METRICS ETL
├── dronacharya schema → TEACHER ETL
├── payments schema → PAYMENT ETL, ADDONS ETL
└── All schemas → BAU ETL (consolidated)
        │
        ▼ (AWS Glue / Lambda — scheduled transforms)
        │
        ▼
Analytics PostgreSQL (data warehouse)
        │
        ▼
Metabase (analytics.brightchamps.com)
```

## External Integrations
- **AWS Glue** — Primary ETL execution platform for all pipelines except BAU
- **AWS Lambda** — Used for BAU ETL (combined with SQL + Python)
- **Metabase** — Alerting and dashboard platform at `analytics.brightchamps.com`

## Internal Service Dependencies
- DEMO ETL → `tryouts` schema (demo bookings)
- DEMO CLASS ETL → `tryouts`/`paathshala` schemas (class + booking data)
- TEACHER ETL → `dronacharya` schema (teacher data)
- MARKETING ETL → `tryouts` schema (marketing spend data)
- STUDENT TEACHER CLASS METRICS ETL → `paathshala`/`eklavya`/`dronacharya` schemas
- PAYMENT ETL → `payments` schema
- STUDENT CLASS BALANCE ETL → `eklavya`/data warehouse schemas
- ADDONS ETL → `payments` schema (add-on transactions)
- REFUND ETL → `eklavya`/`platform` schemas
- STUDENT ETL → `eklavya` schema + country/language references
- PAID CLASS ETL → `paathshala` schema (paid_classes, PTMs, groups)
- BAU ETL → aggregates from multiple schemas

## Database Operations
### Tables Accessed
All pipelines read from production microservice schemas and write to the analytics/data warehouse PostgreSQL.

Key source schemas:
- `tryouts.*` — Demo and marketing data
- `eklavya.*` — Student data and class balances
- `paathshala.*` — Class and paid class data
- `dronacharya.*` — Teacher data
- `payments.*` — Sales, payments, addons, refunds
- `platform.*` — Cross-service data (refund ETL)

### SQL / ORM Queries
Not detailed per pipeline in this catalog — see individual pipeline documentation.

### Transactions
N/A — Batch ETL jobs; incremental load patterns used throughout.

## Performance Analysis
### Good Practices
- All 12 pipelines report Healthy status
- All pipelines use incremental loading — no full table scans on every run
- High-frequency pipelines (every 3 hours) for revenue-critical data (Payments, Students, Demo)
- Metabase alerts configured for critical pipelines to detect data discrepancies

### Performance Concerns
- BAU ETL runs every hour via Lambda — highest frequency job; should have strict SLA monitoring
- All pipelines owned by only 3 engineers — bus factor risk
- No documented recovery procedure if a pipeline falls behind (no SLA documentation)

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | All pipelines owned by only 3 people — no documented backup owner or on-call rotation |
| Medium | No SLA documentation for acceptable pipeline lag per business domain |
| Low | BAU ETL uses SQL + Python + Lambda (mixed stack) — inconsistent with Glue-based approach of other pipelines |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Document acceptable lag SLAs per pipeline (e.g., Payment ETL: max 3 hours, Teacher ETL: max 24 hours)
- Ensure all Metabase alerts are actively monitored with a primary + backup owner

### Month 1 (Architectural)
- Standardize BAU ETL onto AWS Glue to reduce infrastructure heterogeneity
- Add a pipeline health dashboard showing last_run time, row counts, and status for all 12 pipelines
- Document cross-pipeline dependencies (e.g., BAU ETL depends on DEMO ETL and PAYMENT ETL being fresh)

## Test Scenarios
### Functional Tests
- DEMO ETL row count matches source `tryouts.bookings` within acceptable delta
- PAYMENT ETL row count matches source `payments.*` tables within acceptable delta
- STUDENT ETL correctly enriches records with country/language data

### Performance & Security Tests
- BAU ETL completes within 30 minutes to ensure hourly freshness
- DEMO ETL and PAYMENT ETL complete within 2 hours for every-3-hour refresh cycle
- Verify analytics PostgreSQL is not directly accessible from production microservice network

### Edge Cases
- Source microservice DB is under heavy load during ETL window — does Glue job wait, fail, or degrade?
- Incremental load misses a batch due to clock skew — gap detection and backfill mechanism?

## Async Jobs & ETL
All 12 pipelines are ETL jobs. Summary of schedules:

**Every Hour:**
- BAU ETL (SQL + Python + AWS Lambda)

**Every 3 Hours:**
- DEMO ETL, DEMO CLASS ETL, PAYMENT ETL, ADDONS ETL, STUDENT ETL, PAID CLASS ETL

**Daily:**
- TEACHER ETL, MARKETING ETL, STUDENT TEACHER CLASS METRICS ETL, STUDENT CLASS BALANCE ETL, REFUND ETL

**Alerts (Metabase):**
- DEMO ETL: `/question/4275-bookings-vs-etl-alert`
- MARKETING ETL: `/question/2622-marketing-alert`
- PAYMENT ETL: `/question/2624-regular-collection-mismatch-`
- ADDONS ETL: `/question/4713-addon-collection-mismatch-raw-vs-etl`
- STUDENT ETL: `/question/4715-missing-students`
- BAU ETL: `/question/4589-demo-joined-difference-bau-vs-etl`, `/question/4590-total-completed-difference-bau-vs-etl`, `/question/4586-total-leads-difference-bau-vs-etl`
