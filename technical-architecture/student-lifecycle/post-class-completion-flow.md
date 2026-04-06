---
title: Post Class Completion Flow
category: technical-architecture
subcategory: student-lifecycle
source_id: 4c649e6f
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Post Class Completion Flow

## Overview
The Post Class Completion Flow handles all downstream actions after a demo or paid class ends, including CRM deal creation, sales manager allocation, student credit deduction, and social feed generation. Demo classes trigger CRM lead-to-deal conversion and hotlead routing; paid classes trigger balance updates and completion reason logging via Lambda.

## API Contract

### POST /paathshala/api/v1/class/paid/feedback/v2
- **Auth:** Teacher JWT
- **Purpose:** Submit paid class feedback; triggers `update-paid-class-status` SQS message
- **Status Codes:** 200 OK, 400 Bad Request

### PATCH /eklavya/v2/student-class-balance
- **Auth:** Internal (Lambda to Eklavya)
- **Purpose:** Update `total_class_paid` and `credits_consumed` after paid class completion

### POST /hotlead (Tryouts Service)
- **Auth:** Teacher JWT
- **Request Body:** `{ "classId": int }`
- **Purpose:** Mark a student as a hotlead; notify Slack channel for sales claim

### POST /webhook (Hotlead claim)
- **Auth:** Slack signature verification
- **Purpose:** Sales Manager claims hotlead via Slack button; assigns SM and sends meeting link

## Logic Flow

### Controller Layer
- Demo feedback → SNS publish → `prabandhan` SQS → Lambda `prabandhan-class-completion-flow`
- Paid feedback → `update-paid-class-status` SQS → Lambda
- Hotlead → Tryouts `/hotlead` API → Slack notification → SM claims via `/webhook`

### Service/Facade Layer
**Demo Class Completion Flow:**
1. Teacher submits demo feedback and marks class as "Successful"
2. Publish `{ classId, status }` to SNS topic
3. `prabandhan` SQS queue (filters for "Successful") → triggers Lambda `prabandhan-class-completion-flow`
4. Lambda fetches: `demo_classes` → `bookingId` + `teacherConfirmationId` → teacher details → student/booking details
5. Call `createDBCRMDeal()`:
   - Search Zoho CRM for existing Lead by booking details
   - Convert Lead → Deal; update with current data
   - Fetch class feedback → append to deal as notes
6. Separate SQS consumer: allocate Sales Manager to deal in round-robin:
   - Check sales group mapping
   - Find SM where `deals_alloted < max_deals`
   - Update deal owner in CRM
7. On error: log to logger + alert Slack channel with function name

**HotLead Flow:**
1. Teacher marks student as hotlead → `POST /hotlead` with `classId`
2. Fetch student and teacher details
3. Push rich notification to Slack channel mapped to course/language/region
4. SM clicks "Claim" in Slack → triggers `POST /webhook` callback
5. Fetch SM email using Slack User ID → assign hotlead → send meeting link as DM

**Paid Class Completion Flow:**
1. Teacher submits paid class feedback → `POST /paathshala/api/v1/class/paid/feedback/v2`
2. Push message to `update-paid-class-status` SQS queue
3. Lambda evaluates completion reason:
   - `common_duration >= required` → "Met the criterion"
   - `student_duration` met but not `teacher_duration` → "teacher duration not satisfied"
   - `teacher_duration` met but not `student_duration` → "student duration not satisfied"
   - Default → "Met the criterion"
4. Update `paid_classes.paid_class_status_id`
5. Upsert `paid_class_metrics(metric_key='class-completion-reason', value=reason)`
6. If `status = completed`: call `PATCH /eklavya/v2/student-class-balance`
   - Update `student_class_balances.total_class_paid`
   - Increment `student_profiles.credits_consumed`
   - Log to `student_class_balance_audit_trails`

### High-Level Design (HLD)
- Demo completion: Paathshala SNS → Prabandhan SQS → CRM Lambda chain
- Paid completion: SQS → Lambda → Eklavya API (cross-service)
- Hotlead: Tryouts → Slack → Webhook claim flow
- CRM is Zoho; deal allocation uses round-robin with capacity cap per SM

## External Integrations
- **Zoho CRM:** Lead-to-deal conversion, deal owner allocation
- **Slack:** HotLead notifications + SM claim interaction
- **AWS SNS/SQS:** Demo class feedback fan-out; paid class update queue
- **Social Feed Service (`eklavya.posts`):** Class completion events trigger post creation

## Internal Service Dependencies
- Paathshala: `demo_classes`, `paid_classes`, `paid_class_metrics`
- Eklavya: `student_class_balances`, `student_profiles`, `student_class_balance_audit_trails`, `posts`
- Prabandhan: CRM integration service

## Database Operations

### Tables Accessed

**`paathshala.demo_classes`:** `booking_id`, `teacher_confirmation_id`

**`paathshala.paid_classes`:** `paid_class_status_id`

**`paathshala.paid_class_metrics`:**
| Column | Notes |
|--------|-------|
| metric_key | e.g., 'class-completion-reason' |
| value | Reason string |

**`eklavya.student_class_balances`:** `total_class_paid`

**`eklavya.student_profiles`:** `credits_consumed`

**`eklavya.student_class_balance_audit_trails`:** Audit log of balance changes

**`eklavya.posts`:** Social feed posts generated on class completion

### SQL / ORM Queries
- SELECT `demo_classes` WHERE `demoClassId` → `bookingId`, `teacherConfirmationId`
- UPDATE `paid_classes.paid_class_status_id`
- UPSERT `paid_class_metrics` WHERE `metric_key = 'class-completion-reason'`
- UPDATE `student_class_balances.total_class_paid`
- UPDATE `student_profiles.credits_consumed`
- INSERT into `student_class_balance_audit_trails`

### Transactions
- Paid class balance update (Eklavya `PATCH`) is atomic: `student_class_balances` + `student_profiles` + audit trail

## Performance Analysis

### Good Practices
- SNS fan-out separates CRM deal creation from SM allocation, allowing independent retry
- Error handling with Slack alerting prevents silent failures in the CRM pipeline
- Audit trail in `student_class_balance_audit_trails` provides full balance history

### Performance Concerns
- CRM deal creation Lambda makes sequential API calls to Zoho (fetch → convert → update → notes) — multiple round trips add latency
- Round-robin SM allocation requires reading all `deals_alloted` counts — could be slow under high load

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | SM allocation round-robin reads all SMs on each allocation — needs caching or atomic counter |
| Low | Social feed generation via class completion is loosely documented — integration details unclear |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Cache SM allocation state in Redis to avoid full DB scan per deal
- Add DLQ for `prabandhan` SQS to capture failed CRM conversion events

### Month 1 (Architectural)
- Batch Zoho API calls in the CRM Lambda to reduce round trips
- Implement idempotency check on paid class status update Lambda (avoid double-processing)

## Test Scenarios

### Functional Tests
- Demo class marked "Successful" → CRM Lead converted to Deal with correct data
- SM allocated in round-robin and deal owner updated
- Teacher marks hotlead → Slack notification sent → SM claims → meeting link received
- Paid class completed → completion reason logged, `credits_consumed` incremented
- Error in CRM Lambda → Slack alert sent

### Performance & Security Tests
- Verify SM claim webhook validates Slack signature before processing
- Simulate 100 concurrent paid class completions and verify no double credit deductions

### Edge Cases
- Demo class feedback submitted but `bookingId` missing in `demo_classes` → error + Slack alert
- SM pool exhausted (all SMs at `max_deals`) → no new deal owner assigned
- Paid class `common_duration` equals exactly `required_duration` (boundary condition)

## Async Jobs & Automation
- **`prabandhan-class-completion-flow` Lambda:** Triggered by `prabandhan` SQS on "Successful" demo feedback; handles CRM Lead-to-Deal conversion
- **SM Allocation Lambda:** Separate SQS consumer on same SNS topic; round-robin SM assignment to deals
- **`update-paid-class-status` Lambda:** Triggered by SQS; updates `paid_classes`, `paid_class_metrics`, calls Eklavya balance API
- **Zoho CRM Balance Sync Cron (Daily):** Aggregates class balances for students who completed/missed classes yesterday; batches to Zoho CRM
- **Social Feed Domain Service:** Triggered by class completion events; creates posts in `eklavya.posts`
