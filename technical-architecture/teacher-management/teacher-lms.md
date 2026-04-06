---
title: Teacher LMS (Leave Management System)
category: technical-architecture
subcategory: teacher-management
source_id: 069b15bc
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Teacher LMS (Leave Management System)

## Overview
The Teacher LMS — which stands for Leave Management System — handles teacher leave applications, tracks leave balances, and automatically manages downstream impacts on scheduled paid and demo classes. It uses an event-driven architecture (SNS/SQS) to asynchronously cancel affected classes and send notifications, with cron jobs managing status lifecycle transitions.

## API Contract

### POST /apply-leave
- **Auth:** JWT Bearer token (Teacher)
- **Purpose:** Submit a leave application
- **Notes:** Documentation indicates the endpoint may need modification if leave is applied directly from the calendar view
- **Request Body:** Leave details including `reason_id`, `start_time`, `end_time`, optional `document` and `comment`
- **Status Codes:**
  - 200: Leave application created
  - 400: Validation error

## Logic Flow

### Controller Layer
`POST /apply-leave` → `LeaveController.applyLeave()`

### Service/Facade Layer
**Application and Approval Flow:**
1. Receive leave application payload
2. Fetch `teacher_leave_reasons` row using `leave_reason_id`
3. Determine leave type: `regular` or `long_leave`
4. If `long_leave`, forward data to Zoho CRM
5. Insert record into `teacher_applied_leave`
6. Upon approval, push leave details to SNS topic

**Asynchronous Event Processing (Post-Approval):**
1. SNS topic fans out to multiple SQS queues:
   - Queue for canceling affected paid classes
   - Queue for canceling demo classes
   - Queue for sending notification emails
   - Queue for updating the calendar
2. Each queue handler processes its task independently

### High-Level Design (HLD)
- Dronacharya (Teacher Service) owns the LMS domain
- SNS/SQS fan-out pattern ensures isolation between cancellation, notification, and calendar update concerns
- Three cron jobs manage the leave status lifecycle

## External Integrations
- **Zoho CRM:** Receives leave data for long-leave type applications
- **Email Provider (via SQS queue):** Sends notification emails on leave approval
- **Calendar Service:** Updated via SQS-triggered handler when leave is approved

## Internal Service Dependencies
- Paathshala (Class Service): Provides paid class and demo class records for cancellation
- `teacher_leave_balance` is updated when paid/demo leaves are consumed

## Database Operations

### Tables Accessed

**`teacher_applied_leave`:**
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| teacher_id | int | |
| start_time | datetime | |
| end_time | datetime | |
| approved | tinyint | |
| approved_by | varchar | |
| is_active | tinyint | |
| status | ENUM | e.g., pending, processed, on_leave, completed |
| leave_reason_id | int | FK → teacher_leave_reasons |
| ticket_id | varchar | |
| document | varchar | |
| comment | varchar | |
| affected_paid_classes | int | |
| affected_demo_classes | int | |
| paid_cancellation_status | boolean | |
| demo_cancellation_status | boolean | |

**`teacher_leave_reasons`:**
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| reason | varchar | |
| type | ENUM | 'regular', 'long_leave' |

**`teacher_leave_balance`:**
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| teacher_id | int | |
| month | datetime | |
| demo_leaves_credit | int | |
| paid_leaves_credit | int | |
| demo_leaves_used | int | |
| paid_leaves_used | int | |

### SQL / ORM Queries
- SELECT leave reason type to determine routing logic
- INSERT leave record into `teacher_applied_leave`
- UPDATE `paid_cancellation_status` and `demo_cancellation_status` upon SQS processing
- UPDATE leave status to `processed`, `on_leave`, or `completed` via cron

### Transactions
- Leave application creation is a single atomic insert

## Performance Analysis

### Good Practices
- Fan-out via SNS/SQS ensures class cancellations do not block the leave approval response
- Isolated SQS queues allow independent retry logic per concern (paid cancel, demo cancel, email, calendar)

### Performance Concerns
- Multiple SQS queues increase operational overhead for monitoring and dead-letter queue management
- Leave Status Updater Cron must poll leave records periodically — could be slow for large leave backlogs

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | `/apply-leave` endpoint may need modification if leave is applied via calendar UI — noted in docs as unresolved |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add composite index on `teacher_applied_leave(teacher_id, status, start_time)` for cron efficiency
- Implement dead-letter queues for each SQS handler with alerting

### Month 1 (Architectural)
- Unify leave status updates into a single event-sourced state machine instead of polling crons
- Build an ops dashboard for real-time visibility into leave cancellation pipeline status

## Test Scenarios

### Functional Tests
- Apply regular leave: verify paid and demo classes are cancelled asynchronously
- Apply long leave: verify Zoho CRM is notified with leave data
- Approve leave: verify SNS fan-out triggers all 4 SQS queues
- Leave Status Updater Cron transitions status to `on_leave` during leave window

### Performance & Security Tests
- Verify only the teacher's own leave records are accessible via JWT
- Simulate SQS handler failure and verify retry/DLQ behavior

### Edge Cases
- Leave applied when teacher has zero upcoming classes (graceful no-op)
- Leave cancelled before approval (status must not propagate to SQS)
- Leave window spans midnight UTC (timezone edge case)

## Async Jobs & Automation
- **Leave Status Updater Cron:** Checks completion of paid/demo cancellations; transitions `teacher_applied_leave.status` to `processed` → `on_leave` → `completed` based on timing
- **Paid Schedule Window Expiry Cron (Paathshala):** Finds paid classes with `status_id = 18` scheduled within the next 2 hours; cancels them, stores cancellation in paid class metrics, pushes SQS message to increment `affected_paid_classes` count on the leave record
- **SNS → SQS fan-out:** Post-approval asynchronous pipeline for: paid class cancellation, demo class cancellation, notification email, calendar update
