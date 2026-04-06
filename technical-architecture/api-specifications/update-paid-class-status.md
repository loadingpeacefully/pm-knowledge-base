---
title: Update Paid Class Status
category: technical-architecture
subcategory: api-specifications
source_id: eddd4b55-8141-41d5-b8b8-f3e22f37c70a
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Update Paid Class Status

## Overview
This flow updates the `paid_class_status_id` in the `paid_classes` table of Paathshala, inserts or updates the `class-completion-reason` metric key in `paid_class_metrics`, and then calls the Eklavya service to update `total_class_paid` in `student_class_balances` and `credits_consumed` in `student_profiles`. It is triggered either from a Lambda function or from the `POST /paathshala/api/v1/class/paid/feedback/v2` API when a teacher submits a feedback form.

## API Contract

| Property | Value |
|----------|-------|
| Method | POST |
| Path | `/paathshala/api/v1/class/paid/feedback/v2` |
| Auth | Internal/JWT (teacher-facing) |
| Content-Type | application/json |

**Trigger via SQS (Lambda Path):**
```json
{
  "classId": 9,
  "paidClassDetails": {
    "id": 748,
    "studentId": 195,
    "studentClassBalanceId": 2,
    "teacherId": 1,
    "batchId": "BT_TEST_1",
    "startAt": "2023-05-23T14:30:00.000Z",
    "durationId": 2,
    "referenceId": null,
    "paidClassStatusId": 17,
    "schedulingSource": "sd_bulk_schedule_web",
    "meetingId": null,
    "courseId": 3,
    "scheduledBy": "195",
    "cancelledAt": "2023-05-05T12:28:45.000Z",
    "cancelledBy": "195",
    "cancellingSource": "sd_cancel_web"
  },
  "studentDetails": {
    "id": 195,
    "grade": 2,
    "parentId": 18,
    "name": "Student Name",
    "StudentProfile": {},
    "StudentLanguageMappings": []
  },
  "paidClassMetrics": {
    "feedback": 1,
    "teacher_joined": "2023-05-23T14:41:00.000Z",
    "teacher_joined_zm": "2023-05-23T14:41:00.000Z",
    "teacher_left": "2023-05-23T15:30:00.000Z",
    "student_joined": "2023-05-23T14:36:00.000Z",
    "student_joined_zm": "2023-05-23T14:37:00.000Z",
    "student_left": "2023-05-23T15:30:00.000Z",
    "teacher_duration": 2000,
    "student_duration": 3400,
    "common_duration": 1900
  }
}
```

**Downstream call to Eklavya:**
```
PATCH /eklavya/v2/student-class-balance
```
Updates `total_class_paid` in `student_class_balances` and `credits_consumed` in `student_profiles`.

## Logic Flow

### Controller Layer
- `POST /paathshala/api/v1/class/paid/feedback/v2` — Teacher submits feedback → message pushed into `update-paid-class-status` SQS queue.

### Service/Facade Layer
1. **EventBridge** triggers `publish-paid-class-status-update` Lambda every 30 minutes (at :15 and :45 of each hour).
2. **`publish-paid-class-status-update` Lambda** formats data in a `-5 to -1 hour` window of current time and pushes each class object into the `update-paid-class-status` SQS queue.
3. **`update-paid-class-status` SQS** receives messages (from Lambda or feedback API) and invokes the `update-paid-class-status` Lambda.
4. **`update-paid-class-status` Lambda** performs:
   - Updates `paid_class_status_id` in `paid_classes`.
   - Creates or updates the `class-completion-reason` metric in `paid_class_metrics`.
   - Calls Eklavya `PATCH /eklavya/v2/student-class-balance` to update class balance and credits.

### High-Level Design (HLD)
- Dual trigger path: scheduled EventBridge cron (every 30 min) AND real-time teacher feedback API.
- Both paths converge on the same SQS queue → Lambda processing.
- Cross-service update: Paathshala updates class status; Eklavya updates student credit/balance.
- A low-level flowchart exists in source documenting all conditional branches (student left early, teacher left early, minimum duration completion, etc.).

## External Integrations
- **AWS EventBridge** — Cron-based triggering of `publish-paid-class-status-update` Lambda.
- **AWS SQS** — `update-paid-class-status` queue (stage and prod variants).
- **AWS Lambda** — `publish-paid-class-status-update`, `update-paid-class-status`.

## Internal Service Dependencies
- **Eklavya** — `PATCH /eklavya/v2/student-class-balance` for updating `total_class_paid` and `credits_consumed`.
- **Paathshala** — Source of class and metric data.

## Database Operations

### Tables Accessed
**Paathshala:**
- `paid_classes` — Updated: `paid_class_status_id`
- `paid_class_metrics` — Inserted/updated: `class-completion-reason` metric key

**Eklavya:**
- `student_class_balances` — Updated: `total_class_paid`
- `student_profiles` — Updated: `credits_consumed`
- `student_class_balance_audit_trails` — Audit log for balance changes

### SQL / ORM Queries
- `UPDATE paid_classes SET paid_class_status_id = ? WHERE id = ?`
- `INSERT INTO paid_class_metrics (metric_key, ...) VALUES ('class-completion-reason', ...) ON DUPLICATE KEY UPDATE ...`

### Transactions
- The Lambda processes one class at a time from SQS; Eklavya update is a separate API call (not wrapped in a distributed transaction).

## Performance Analysis

### Good Practices
- Dual trigger strategy (cron + real-time) ensures both batch processing and low-latency updates for active teacher submissions.
- SQS decouples the feedback API from synchronous processing.
- EventBridge cron uses a `-5 to -1 hour` window to avoid processing in-progress classes.

### Performance Concerns
- No distributed transaction between Paathshala DB update and Eklavya API call — partial failures are possible (class status updated but credit not decremented).
- Cron runs every 30 minutes; classes completed in between rely on the real-time feedback API path.

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No distributed transaction across Paathshala and Eklavya — a failure mid-flow leaves data inconsistent between services. |
| Medium | SQS retry behavior on Lambda errors needs explicit dead-letter queue (DLQ) configuration. |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Confirm DLQ is configured on `update-paid-class-status` SQS for failed message handling.
- Add structured logging per Lambda invocation with `classId` for traceability.

### Month 1 (Architectural)
- Implement idempotency key on Lambda to prevent double-processing of the same classId.
- Add saga/compensation pattern for Eklavya credit update failure — revert Paathshala status update if Eklavya call fails.

## Test Scenarios

### Functional Tests
- Teacher submits feedback → verify `paid_class_status_id` updated in `paid_classes`.
- Verify `class-completion-reason` metric is created/updated in `paid_class_metrics`.
- Verify Eklavya balance updated after Lambda processes message.

### Performance & Security Tests
- Simulate 1000 concurrent feedback submissions; verify no message loss in SQS.
- Verify EventBridge cron does not reprocess already-processed classes.

### Edge Cases
- Student left early — verify correct status ID applied.
- Teacher left early — verify minimum duration logic applied correctly.
- Missing `bookingId` or `teacherConfirmationId` — verify graceful Lambda failure with Slack alert.
- Eklavya API call fails after Paathshala update — verify current error handling behavior.

## Async Jobs & Automation
- **EventBridge Cron:** `rate(30 minutes)` at :15 and :45 each hour → triggers `publish-paid-class-status-update` Lambda.
- **`publish-paid-class-status-update` Lambda:** Batches classes in the `-5 to -1 hour` window and pushes to SQS.
- **`update-paid-class-status` SQS:** Decouples feedback API and cron from Lambda processing.
- **`update-paid-class-status` Lambda:** Core processor — updates both Paathshala and Eklavya.
