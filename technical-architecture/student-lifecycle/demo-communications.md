---
title: Demo Communications
category: technical-architecture
subcategory: student-lifecycle
source_id: aad8bfe5
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Demo Communications

## Overview
The Demo Communications system manages all notifications sent to students, teachers, and sales managers during the lead-to-trial lifecycle. Booking reminders and cancellation messages are orchestrated via the Tryouts service using an event-driven SNS/SQS architecture, with the centralized Hermes service handling actual message dispatch over Email and WhatsApp.

## API Contract

### POST /communications/demo-cancel (Tryouts Service)
- **Auth:** Internal
- **Purpose:** Trigger cancellation communications when a class is cancelled
- **Request Body:** `{ "objectId": "string" }`

### DELETE /communications (Tryouts Service)
- **Auth:** Internal
- **Purpose:** Delete previously scheduled communication messages
- **Use Cases:** Booking cancelled, rescheduled, or marked unqualified
- **Request Body:** `{ "objectId": "string" }`

## Logic Flow

### Controller Layer
- Booking creation/update triggers SNS event with `objectId` and `isDateTimeModified` boolean
- `booking_comms` SQS queue filters for `isDateTimeModified = true`

### Service/Facade Layer
**Booking Reminders Flow:**
1. Booking created or updated → push `{ objectId, isDateTimeModified }` to SNS topic
2. `booking_comms` SQS queue receives message
3. Only process if `isDateTimeModified = true`
4. Delete any existing scheduled messages for that `objectId` (prevents sending stale reminders after reschedule)
5. Schedule new messages across all configured mediums based on `scheduleType` and `schedule` offset
6. A/B test: generate random weight; send message only if `calculatedWeight < sumTemplatesWeight`

**Reschedule Reminders (Missed Class):**
- Not triggered by SNS/SQS events
- Polling Lambda runs every 30 minutes to find students who have not joined their scheduled classes
- Dispatches reschedule reminder messages for those students

### High-Level Design (HLD)
- Tryouts service owns booking communication scheduling logic
- Hermes service is the centralized dispatcher for all message types
- Templates defined in `constants/communication-templates.js`, organized by course and medium
- Two mediums: Email and WhatsApp
- A/B testing supported via weighted template selection

## External Integrations
- **Hermes (Communications Service):** All messages are scheduled and dispatched through Hermes
- **AWS SNS:** Booking creation/modification publishes events to SNS topic
- **AWS SQS:** `booking_comms` queue subscribes to SNS topic
- **WhatsApp Provider:** Active communication medium
- **Email Provider:** Active communication medium
- **Mo-engage (Proposed):** Future integration for promotional and re-engagement messaging

## Internal Service Dependencies
- Tryouts (Demo Booking Service): Owns booking state, communication triggers
- Hermes: `hermes.communication_requests` table tracks request and message status
- `tryouts.communication_logs` tracks sent communication history

## Database Operations

### Tables Accessed

**`tryouts.communication_logs`:**
| Column | Notes |
|--------|-------|
| type | Communication type |
| referenceId | objectId reference |

**`hermes.communication_requests`:**
| Column | Notes |
|--------|-------|
| (various) | Logs communication requests and message delivery statuses |

### SQL / ORM Queries
- SELECT existing scheduled messages for `objectId` before creating new ones
- DELETE scheduled messages for `objectId` on reschedule/cancel
- INSERT new communication schedule entries after booking update

### Transactions
- Delete-then-insert of communication schedule treated as a logical transaction to prevent orphaned messages

## Performance Analysis

### Good Practices
- Deleting stale schedules before inserting new ones prevents duplicate notifications on reschedule
- SNS/SQS decouples booking service from communication dispatching
- A/B testing baked into the template selection layer without requiring code changes

### Performance Concerns
- Reschedule reminders use polling (Lambda every 30 min) rather than event-driven triggers — slight latency in detecting missed joins

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | Mo-engage integration is proposed but not yet implemented — promotional messaging is currently not separated from transactional |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add dead-letter queue for `booking_comms` SQS to capture failed message processing
- Monitor A/B test weight distributions to ensure statistical validity

### Month 1 (Architectural)
- Migrate reschedule reminder detection from polling to event-driven (Zoom join event → SNS → SQS)
- Implement Mo-engage integration to handle promotional communications separately

## Test Scenarios

### Functional Tests
- Booking created → verify booking reminder is scheduled in Hermes
- Booking rescheduled → verify old reminders deleted and new ones scheduled
- Booking cancelled → verify `/communications/demo-cancel` sends cancellation message
- Booking unqualified → verify `DELETE /communications` removes all scheduled messages
- Reschedule reminder Lambda fires for student who did not join

### Performance & Security Tests
- Simulate 1000 concurrent booking creations and verify SNS/SQS handles fan-out without message loss
- Verify `objectId` lookup for message deletion is indexed for performance

### Edge Cases
- Reschedule immediately before class time (window < schedule offset)
- Same booking rescheduled twice in rapid succession (race condition on delete-then-insert)
- A/B weight sum = 0 (no messages sent — should be handled gracefully)

## Async Jobs & Automation
- **Reschedule Reminder Lambda (`cron(0,30 * * * ? *)`):** Runs at every 0th and 30th minute; detects students who have not joined; dispatches reschedule reminder messages
- **`booking_comms` SQS Consumer:** Processes booking creation/modification events to schedule or delete communication messages via Hermes
