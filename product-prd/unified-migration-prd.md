---
title: "Unified Migration – Platform Migration Project Document"
category: product-prd
subcategory: platform-infrastructure
source_id: e61fae52-c556-46f4-8291-dec589052e47
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Unified Platform Migration

## Project Overview

| Field | Detail |
|-------|--------|
| **Company** | BrightChamps (EdTech, K–12, 30+ countries) |
| **Timeline** | Feb 2023 – Mar 2024 |
| **Involvement** | Feb 2023 – Aug 2023 (7 months, Lead PM for rollout) |
| **Team Size** | ~30–35 Engineers (21–22 backend, rest frontend) + 2 Designers + 4–6 Ops/QA |
| **Objective** | Unify all legacy and acquired platforms into one scalable system covering students, teachers, and ops |

---

## Context

### Legacy & Acquired Platforms
- **BrightChamps Legacy:** Coding, Robotics
- **Education10x:** Financial Literacy
- **Scola:** Public Speaking, Presentation Skills, Kids Academic English (Cambridge), IELTS, Senior Communication

**Total: 7 courses to migrate**

### Problems Before Migration
- Multiple disjointed dashboards for students, teachers, and ops
- ~20 Ops staff needed for manual demo scheduling, calling, and reconciliation
- Teachers wasted hours in empty classes (payout inefficiencies)
- Tracking scattered in Google Sheets → poor auditability
- Scalability bottleneck: onboarding a new course = rebuilding flow from scratch

---

## Role & Responsibility

- **Lead PM for Demo & Class Flows**
- Owned: Demo Flow unification, Paid Student Experience, Teacher Dashboard, Admin demo cases
- **Documented 100+ use cases**, created phased rollout plan, coordinated with ~30 engineers
- Stakeholder interviews: Ops, Teachers, Sales, acquired company leads
- Handover: After Aug 2023, other PMs scaled the remaining features and existing student migrations

---

## Execution Strategy

### Rollout Approach
1. Start with low-risk verticals (Robotics, Financial Literacy)
2. Route all new students into UnifiedFlow → test stability
3. Gradual batch migration of paid students → minimize disruption
4. Parallel systems active during early rollout (safety net)

### ETL & Data Migration
- **Sources:** MySQL, Redis, Mongo, Google Sheets
- **Pipeline:** SQL + Python scripts → unified schema in MySQL (Redis caching)
- **Steps:** Extract → Transform (normalize IDs, clean duplicates, standardize teacher schedules) → Load
- **Reliability:** Phased rollout, automated integrity checks, rollback scripts
- **Scheduler:** Cron initially → later Airflow/dbt

### System Architecture (Simplified)
```
[Legacy: BrightChamps / Education10x / Scola]
↓ Extract (SQL, Python, Sheets API)
[ETL Layer] — Clean, Normalize, Map IDs
↓ Load
[Unified MySQL + Redis Cache]
↓
[Backend APIs — Node.js/Python]
↓
[Frontends: React + Vite]
→ Student Dashboard
→ Teacher Dashboard
→ Admin Dashboard
```

---

## Key Deliverables

### Student Dashboard
- Gamified Gems Referral Program (rewarded attendance/referrals)
- Redesigned class cards → lesson info + progress
- Quizzes page with live tracking
- Certificates page (previously email-only)
- Calendar view for upcoming classes
- Course progress view across modules

### Teacher Dashboard
- Google Calendar-style weekly view → manage demos/paid slots
- Slot enablement toggle for demo & paid classes
- Animated class cards with lesson booklet links
- One-click live issue reporting → alerts to Ops dashboard
- Salary dashboard with per-class credits + downloadable payslips

### Admin Dashboard (Demo Ops)
- Centralized monitoring of demo flows
- Real-time alerts (student no-show, teacher escalation)
- **Ops workload cut 80%** → ~20 → 3–4 staff
- Unified logs for audit & payouts

---

## Outcomes

- Migrated **100% of 7 courses** into UnifiedFlow
- **Ops efficiency:** Demo ops headcount reduced from ~20 → 3–4
- **Teacher efficiency:** Eliminated payout waste by confirming only joined demos
- **Data integrity:** Centralized tracking; removed Google Sheets dependence
- **Scalability:** New courses onboarded in weeks (vs. months earlier)

---

## Challenges & Resolutions

| Challenge | Resolution |
|-----------|-----------|
| Bandwidth gaps | ~3-month delay in rollout; addressed with phased approach |
| Legacy data quality | Normalization scripts + manual audits |
| Balancing disruption | Phased rollout + dual systems reduced confusion |
| Stakeholder alignment | Early cross-functional interviews co-created demo policy with teachers/ops |

---

## Learnings

1. Importance of early stakeholder alignment — demo policy co-created with teachers and ops led to faster adoption
2. Phased migration > hard cutover for large systems — reduces risk and allows real-world testing
3. UX parity across student/teacher/ops dashboards simplifies adoption across all user types
4. Data-first migration strategy prevents rework — clean data from the start saves months downstream

## Relevance Tags
- `unified-migration` `platform-infrastructure` `etl` `data-migration` `brightchamps` `m-and-a` `product-prd`
