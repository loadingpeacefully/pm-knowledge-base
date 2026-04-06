---
title: Teacher Payout
category: technical-architecture
subcategory: teacher-management
source_id: ec36908c
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Teacher Payout

## Overview
The Teacher Payout system manages teacher earnings and penalties through a structured policy-and-pricing database model in the Dronacharya service. It supports both teacher-specific pricing and policy-based pricing, and calculates final payout using the formula: `total = teacher_earnings - teacher_earning_penalties`.

## API Contract
N/A — Specific API endpoints and request/response schemas are not documented in the source. A frontend route exists at `/teacher/teacher-extra-payouts` (restricted access) in the Prashashak admin dashboard for extra payout management, but no backend API contract is documented.

## Logic Flow

### Controller Layer
Admin dashboard route: `/teacher/teacher-extra-payouts` → restricted payout management UI (Prashashak)

### Service/Facade Layer
**Payout Calculation Formula:**
```
total_payout = SUM(teacher_earnings.amount) - SUM(teacher_earning_penalties.amount)
```

**Policy Resolution:**
1. Check if teacher has an entry in `teacher_payout_policies` (mapping to a `policy_version_id`)
2. If policy exists, fetch amounts from `policy_prices` using the `policy_version_id`
3. If no policy, fall back to `teacher_prices` for teacher-specific amounts
4. Apply `payout_line_items` thresholds to determine eligibility per line item

### High-Level Design (HLD)
- Dronacharya (Teacher Service) owns all payout tables
- Two pricing tiers: individual teacher prices (`teacher_prices`) and policy-based prices (`policy_prices`)
- Earnings and penalties are recorded per event (class, leave, extra payout, YAR penalty)
- Policy versioning allows rolling out new pay structures without breaking historical records

## External Integrations
N/A — Not documented in source.

## Internal Service Dependencies
- Paathshala (Class Service): Class completion events trigger earnings records
- Dronacharya (Teacher Service): All payout tables reside here

## Database Operations

### Tables Accessed

**`payout_line_items`:**
| Column | Notes |
|--------|-------|
| id | PK |
| line_item_category | e.g., Paid, Demo, Arrears |
| line_item | e.g., Single_Full, Single_Half |
| context | e.g., Class, Leave, Extra_Payout, YAR_Penalty |
| type | Earning or Penalty |
| threshold | Minimum count required to apply this line item |
| global_amount | Default amount |
| description | Text |

**`payout_policies`:**
| Column | Notes |
|--------|-------|
| id | PK |
| course_id | |
| name | |
| description | |
| version_number | |
| effective_date | |
| expiry_date | |

**`teacher_prices`:**
| Column | Notes |
|--------|-------|
| id | PK |
| payout_line_item_id | FK |
| teacher_id | |
| course_id | |
| country_id | |
| student_business_region_id | |
| teacher_business_region_id | |
| payout_business_region_id | |
| amount | |

**`policy_prices`:**
| Column | Notes |
|--------|-------|
| id | PK |
| policy_version_id | FK → payout_policies |
| payout_line_item_id | FK |
| country_id | |
| student_business_region_id | |
| teacher_business_region_id | |
| payout_business_region_id | |
| amount | |
| created_at, updated_at | |

**`teacher_payout_policies`:**
| Column |
|--------|
| id, teacher_id, policy_version_id |

**`teacher_penalties`:**
| Column | Notes |
|--------|-------|
| id | PK |
| teacher_id | |
| payout_line_item_id | FK |
| policy_version_id | FK |
| reference_id | Event reference |
| amount | |
| exempt | boolean |
| manual_update | boolean |
| updated_by, created_at | |

**`teacher_earnings`:**
| Column | Notes |
|--------|-------|
| id | PK |
| teacher_id | |
| date | |
| payout_line_item_id | FK |
| policy_version_id | FK |
| reference_id | Event reference |
| amount | |
| manual_update | boolean |
| updated_by, created_at | |

**`teacher_earning_penalties`:**
| Column |
|--------|
| id, teacher_id, date, payout_line_item_id, policy_version_id, amount, penaltyCount, created_at |

### SQL / ORM Queries
- SUM aggregation on `teacher_earnings` grouped by teacher and date range
- SUM aggregation on `teacher_earning_penalties` grouped by teacher and date range
- JOIN `teacher_payout_policies` → `policy_prices` for policy-based amounts
- Fallback SELECT from `teacher_prices` if no policy mapping exists
- Threshold check on `payout_line_items.threshold` before applying line item

### Transactions
N/A — Not documented in source.

## Performance Analysis

### Good Practices
- Policy versioning with effective/expiry dates allows safe pay structure migrations
- Separation of `teacher_earnings` and `teacher_earning_penalties` provides a clean audit ledger
- `exempt` flag on penalties allows admin overrides without deleting records

### Performance Concerns
- Payout calculation requires multi-table aggregation across earnings, penalties, and policy joins — could be slow at scale without proper indexing

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No API endpoints documented for payout retrieval, generation, or status — entire backend contract is undocumented |
| Medium | No cron jobs documented for automated payout period processing or disbursement scheduling |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add composite indexes on `teacher_earnings(teacher_id, date)` and `teacher_earning_penalties(teacher_id, date)`
- Document the payout generation API contract

### Month 1 (Architectural)
- Implement a scheduled payout processing job (e.g., monthly cron to aggregate earnings and initiate disbursement)
- Add a payout status table to track disbursement states (pending, processed, paid)

## Test Scenarios

### Functional Tests
- Teacher with policy mapping: verify `policy_prices` amounts are used over `teacher_prices`
- Teacher without policy: verify fallback to `teacher_prices`
- Threshold check: earning should not apply if class count is below `payout_line_items.threshold`
- Verify `total = earnings - penalties` calculation is correct

### Performance & Security Tests
- Only the teacher (or admin) should access their own payout records
- Benchmark payout calculation query time for teachers with 1000+ class records

### Edge Cases
- Teacher has no entries in `teacher_payout_policies` (must use `teacher_prices`)
- Penalty marked as `exempt = true` (must not reduce total)
- Policy version expired before payout period ends (fallback behavior)

## Async Jobs & Automation
N/A — Not documented in source. Payout disbursement scheduling and automated aggregation jobs are not described.
