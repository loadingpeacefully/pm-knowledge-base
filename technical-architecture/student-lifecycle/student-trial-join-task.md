---
title: Student Trial Join Task
category: technical-architecture
subcategory: student-lifecycle
source_id: 95b31b58
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Student Trial Join Task

## Overview
The Student Trial Join Task system automates the creation, assignment, and escalation of Zoho CRM tasks when students and sales employees join Zoom trial/demo classes. It uses an event-driven SQS architecture with a priority-bucketing algorithm for intelligent Sales Manager (SM) reassignment across up to 5 attempts.

## API Contract

### Internal Trigger Endpoint
- **URL:** `https://api-services.brightchamps.com/prabandhan/v1/neo-tasks/trigger`
- **Auth:** Internal service-to-service
- **Purpose:** Trigger CRM task creation for join events

### Workflow API (Zoho CRM)
- **`zoho.crm.createRecord("Tasks", payload)`:** Creates a task in Zoho CRM
- Called by the `processUserTrialJoinTask` function in the Prabandhan service

## Logic Flow

### Controller Layer
Zoom meeting event → `processMeetingEvents` consumer (Paathshala) → `processJoinEvents()` → SQS → Prabandhan consumer

### Service/Facade Layer

**Student Join Flow:**
1. Student joins Zoom → `processJoinEvents()` detects trial class student join
2. Push message to SQS: `https://sqs.ap-southeast-1.amazonaws.com/271378155896/prabandhan-crm-notifications`
3. `processNeoLeadNotification` consumer in Prabandhan picks up message
4. `processUserTrialJoinTask()` checks for existing active task for `object_id`
5. If task exists → skip (idempotency)
6. If no task → create CRM task with:
   - Subject: `ST - Join Trial Class ({studentId} - {courseName})`
   - Status: `Not Started`
   - Priority: `Very High`
   - Description: `Meeting link with EmployeeID-Employee Name`
   - TaskType: `ST - Join Trial Class`
   - Task_Attempt: `1`
   - Remind_At: Current time + 1 min
   - Start_Time: Current time
   - End_Time: `Max(Current time + 5 min, Trial Time + 5 min)`
   - Owner: Neo lead Owner

**Employee Join Flow:**
1. Employee joins Zoom → message pushed to same SQS queue
2. `processUserTrialJoinTask()` fetches existing task for `object_id`
3. If task owner matches employee who joined → update task status to `Completed`
4. If task owner differs from lead owner → update lead owner to current task owner

**Task Reassignment & Escalation (Up to 5 Attempts):**
1. Task reaches `End_Time` while still "Not Started" → Zoho workflow fires API call:
   ```json
   { "type": "TASKS", "payload": { "taskType": "owner-not-joined", "payload": { "taskRecordId": taskID } } }
   ```
2. Message pushed to `prabandhan-crm-notifications` SQS
3. `processOwnerNotJoinedTask()` fetches task + lead data → marks task as expired → generates next attempt

**SM Assignment Logic per Attempt:**
| Attempt | Assignment |
|---------|-----------|
| 1, 3, 5 | Default to Neo Lead Owner |
| 2, 4 | Priority bucketing algorithm |

**Priority Buckets (Attempts 2 and 4):**
1. Current Slot 0 Task & Last Slot 0 Task (highest priority)
2. Current Slot 0 Task & Last Slot 0 Completed
3. Current Slot 0 Completed & Last Slot 0 Completed
4. Current Slot 0 Task & Last Slot Any Completed
5. Current Slot Any Task & Last Slot Any Completed (lowest priority)

`getEligibleSmsWithAllocations()` finds eligible SMs; random selection from highest available bucket. If no eligible SM found → no new task created.

**Task Timing Rules:**
| Attempt | End Time |
|---------|---------|
| 1, 2, 4, 5 | Max(Start Time + 5 min, Trial Time + 5 min) |
| 3 | Max(Start Time + 5 min, Trial Time + 40 min) |
| Max attempts | 5 attempts OR Trial Time + 60 min |

### High-Level Design (HLD)
- Paathshala detects Zoom join events and routes to Prabandhan via SQS
- Prabandhan orchestrates all CRM task management
- Zoho CRM is the task database and workflow trigger
- Escalation up to 5 attempts with alternating owner strategies

## External Integrations
- **Zoom Webhooks:** `meeting.participant_joined` events processed by Paathshala
- **Zoho CRM:** Task creation, update, and expiry via `zoho.crm.createRecord`
- **AWS SQS (`prabandhan-crm-notifications`):** Message queue for join events and escalation triggers

## Internal Service Dependencies
- Paathshala: `processMeetingEvents` consumer for Zoom event handling
- Prabandhan: `processNeoLeadNotification` consumer, task management logic
- `Neo_Lead_Eligibilities` CRM module: SM shift/availability data

## Database Operations

### Tables Accessed (Zoho CRM Modules)

**`Tasks` (Zoho CRM):**
| Field | Notes |
|-------|-------|
| Subject | Task name |
| Status | Not Started, In Progress, Completed, Expired |
| Priority | Very High |
| TaskType | ST - Join Trial Class |
| Task_Attempt | 1–5 |
| Remind_At, Start_Time, End_Time | datetime |
| Owner | SM user ID |

**`Neo_Lead_Eligibilities` (Zoho CRM):** SM shift data used for bucket-based assignment

### SQL / ORM Queries
N/A — CRM operations use Zoho CRM API (`zoho.crm.createRecord`, `zoho.crm.updateRecord`).

### Transactions
N/A — CRM is the source of truth; no relational DB transactions documented.

## Performance Analysis

### Good Practices
- Idempotency check (skip if active task exists for `object_id`) prevents duplicate task spam
- 5-attempt cap with `Trial Time + 60 min` ceiling prevents indefinite escalation
- Priority bucketing ensures SMs with the least recent workload get new assignments

### Performance Concerns
- Priority bucket calculation fetches all "ST - Join Trial Task" records for current and past slots — could be slow at high concurrency
- Each attempt requires a Zoho API round-trip — external API latency affects assignment speed

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | `getEligibleSmsWithAllocations()` bucket scan is potentially unbounded — needs pagination or Redis caching |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Cache SM eligibility and current task counts in Redis with short TTL (1–2 min)
- Add DLQ for `prabandhan-crm-notifications` SQS to capture failed task creations

### Month 1 (Architectural)
- Pre-compute priority buckets every 5 minutes via a background job rather than on-demand
- Add monitoring dashboard for task creation success rate and escalation frequency

## Test Scenarios

### Functional Tests
- Student joins → CRM task created with correct subject, priority, and owner
- Same student joins twice → second join is a no-op (idempotency)
- Employee joins with matching owner → task marked Completed
- Task expires (Not Started at End_Time) → escalation triggered, new attempt created
- 5 attempts exhausted without join → no new task created

### Performance & Security Tests
- Verify SQS message processing is idempotent (duplicate SQS message delivery)
- Benchmark bucket priority query at 500 concurrent active trial slots

### Edge Cases
- No eligible SM found in any priority bucket (attempt not created)
- `Trial Time + 60 min` ceiling reached before attempt 5 (stop creating tasks)
- Employee joins but `object_id` has no active task (graceful no-op)

## Async Jobs & Automation
- **`processNeoLeadNotification` SQS Consumer (Prabandhan):** Processes join events and escalation triggers; creates/updates/expires CRM tasks
- **Zoho CRM Workflow Timer:** Fires at task `End_Time` if task is still "Not Started"; triggers escalation via API call to `prabandhan-crm-notifications` SQS
