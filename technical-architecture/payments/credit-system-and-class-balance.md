---
title: Credit System and Class Balance
category: technical-architecture
subcategory: payments
source_id: 8f67bf1c
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Credit System and Class Balance

## Overview
The credit system separates a student's attendance entitlement (`total_credits` in `student_profile`) from their scheduling capacity (`total_booked_class` in `student_class_balance`). Credits are topped up after successful payments and deducted after completed classes. Multiple APIs expose credit progress, bulk lookups, and cross-student/course credit transfers.

## API Contract
**GET `/v1/student-class-balance/progress`**
- Retrieves class progress for a student
- Query: `studentId`
- Response: progress metrics from `student_class_balance`

**GET `/v1/student-class-balance`**
- Retrieves detailed class balance records
- Query: `studentId` or `id` (balance ID)
- Optional: include student, parent, and teacher mapping data
- Response: `StudentClassBalance` record(s)

**POST `/v1/student/bulk-student-class-balances`**
- Retrieves multiple student class balance records in bulk
- Request Body: `{ "studentIds": ["id1", "id2", ...] }`
- Response: Array of `StudentClassBalance` records

**PATCH `/eklavya/v2/student-class-balance`**
- Called after a class is completed
- Updates `total_class_paid` in `student_class_balances`
- Increments `credits_consumed` in `student_profiles`

**POST `/v1/student-credit-transfer/request`**
- Creates a credit transfer request between courses or students
- Request Body: `{ "type": "class|diamonds|gems", "sourceStudentId": "...", "destStudentId": "...", "sourceCourseId": "...", "destCourseId": "...", "quantity": number }`
- Response: Transfer request record

**POST `/payment-callback`** (credit top-up trigger — not a direct credit API)

## Logic Flow

### Controller Layer
- Progress endpoint: accepts `studentId`, delegates to class balance service, returns progress metrics
- Bulk endpoint: accepts array of `studentIds`, returns batched results
- Credit transfer: validates transfer type, source/destination, quantity

### Service/Facade Layer
**Credit Top-Up (post-payment):**
1. `/payment-callback` webhook triggers
2. UPDATE `student_profile.total_credits += classesInPackage`
3. SELECT `package_module_mapping` to resolve module → total classes
4. UPDATE `student_class_balance.total_booked_class += moduleClasses`

**Credit Deduction (post-class):**
1. Teacher submits feedback → Lambda triggers `PATCH /eklavya/v2/student-class-balance`
2. UPDATE `student_class_balances.total_class_paid += 1`
3. UPDATE `student_profiles.credits_consumed += 1`

**Key Distinction:**
- `total_credits` = classes the student may ATTEND (attendance gate)
- `total_booked_class` = classes the student may SCHEDULE (scheduling gate)
- Example: 30 credits (attend limit) vs. 181 total_booked_class (can schedule 181 slots)

### High-Level Design (HLD)
```
Payment Webhook → /payment-callback
  → UPDATE student_profile.total_credits
  → SELECT package_module_mapping
  → UPDATE student_class_balance.total_booked_class

Class Completion → Teacher Feedback → Lambda
  → PATCH /eklavya/v2/student-class-balance
      → UPDATE student_class_balances.total_class_paid
      → UPDATE student_profiles.credits_consumed

GET /v1/student-class-balance/progress
  → SELECT student_class_balance WHERE studentId = ?
  → Return progress (total_booked_class, total_class_paid, credits_consumed)
```

## External Integrations
- No direct external integrations — all internal Eklavya service operations

## Internal Service Dependencies
- **Eklavya:** Owns all credit/balance tables
- **Paathshala:** Triggers post-class credit deduction via teacher feedback → SNS/Lambda chain
- **Payment-Structure / onboard-flow Lambda:** Triggers credit top-up via `/payment-callback`

## Database Operations

### Tables Accessed
- `student_profile` — `total_credits`, `credits_consumed`
- `student_class_balance` / `student_class_balances` — `total_booked_class`, `total_class_paid`
- `package_module_mapping` — Maps package to module total classes
- `student_credit_transfers` — Transfer request history

### SQL / ORM Queries
- UPDATE `student_profile` SET `total_credits = ?` WHERE `student_id = ?`
- UPDATE `student_class_balance` SET `total_booked_class = ?` WHERE `student_id = ? AND course_id = ?`
- UPDATE `student_class_balances` SET `total_class_paid = total_class_paid + 1`
- UPDATE `student_profiles` SET `credits_consumed = credits_consumed + 1`
- SELECT from `package_module_mapping` WHERE `package_id = ?`
- SELECT from `student_credit_transfers` WHERE `source_student_id = ? OR dest_student_id = ?`

### Transactions
- Post-payment credit top-up (student_profile + student_class_balance) is wrapped in atomic transaction within `/payment-callback`

## Performance Analysis

### Good Practices
- Separation of scheduling capacity from attendance entitlement prevents scheduling system from being blocked by credit balance issues
- Bulk endpoint avoids N+1 queries for multi-student dashboard views
- `student_credit_transfers` table maintains full audit history of credit movements

### Performance Concerns
- Post-class credit deduction is triggered via Lambda chain (teacher feedback → SNS → Lambda → PATCH) — latency in deduction could cause brief credit over-scheduling
- No caching on `GET /v1/student-class-balance/progress` — high-frequency polling from dashboards could create DB load

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No real-time credit balance caching — dashboard could show stale data under load |
| Medium | `total_booked_class` vs `total_credits` discrepancy by design is non-intuitive and could confuse integrators |
| Low | `student_credit_transfers` table requires manual audit to reconcile cross-student transfers |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add Redis cache for `student_class_balance/progress` with 60-second TTL
- Add index on `student_class_balance(student_id, course_id)` if not present

### Month 1 (Architectural)
- Event-driven credit ledger: replace direct UPDATE with INSERT-only ledger table for full credit history
- Expose credit history API endpoint based on ledger

## Test Scenarios

### Functional Tests
- Payment → correct `total_credits` increment in `student_profile`
- Payment → correct `total_booked_class` increment matching `package_module_mapping` class count
- Class completion → `credits_consumed` incremented, `total_class_paid` incremented
- `GET /progress` returns accurate metrics post-payment and post-class

### Performance & Security Tests
- Bulk endpoint with 100 `studentIds` — response time benchmark
- Concurrent payment webhooks for same student — verify no double credit addition

### Edge Cases
- Credit transfer: source student has insufficient credits → validation error
- Transfer type `gems` vs `diamonds` vs `class` — distinct handling paths
- `package_module_mapping` missing for a package — fallback behavior
