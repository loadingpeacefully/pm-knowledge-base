---
title: Sales Tasks
category: technical-architecture
subcategory: crm-and-sales
source_id: 3bdd664f
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Sales Tasks

## Overview
Sales Tasks are automated CRM workflow actions in Zoho CRM that prompt Sales Managers or Team Leads to perform specific actions (calls, audits, trial class joins) at scheduled times. Tasks are created, assigned, completed, and expired based on automated triggers across lead creation, class completion, and audit scoring events.

## API Contract
**`POST /v1/neo-tasks/trigger`** (Prabandhan)
- Triggers task-related operations and reassignments
- Used for `ST - Join Trial Class` reassignment flow

**SQS Queue:** `https://sqs.ap-southeast-1.amazonaws.com/271378155896/prabandhan-crm-notifications`
- Receives webhook payloads and triggers task creation

N/A for primary task creation — tasks are created programmatically via `zoho.crm.createRecord("Tasks", payload)`.

## Logic Flow

### Controller Layer
- SQS consumer processes incoming webhook payloads
- Prabandhan Lambda functions execute task creation/completion logic
- `/v1/neo-tasks/trigger` endpoint handles reassignment triggers

### Service/Facade Layer

**Task Type 1: ST - First Connect with Customer**
- **Trigger:** New lead created or lead moved to "trial booked" stage
- **Scheduling:** 2 hours after lead creation, snapped to nearest 30-minute slot
- **Assignment:** Lead Owner (or Co-Owner for Vietnam region)
- **Completion:** SM logs Call + Email + (SMS or WhatsApp or Zalo) within 4 hours
- **Expiry:** 4 hours after task start
- **Checks:** Employee shift window, week-offs, availability; moved to next active day if unavailable

**Task Type 2: ST - Pitch Quality Score Review (TL)**
- **Trigger:** Lead receives Sales Pitch Audit Score ≤ 6
- **Assignment:** Team Lead (manager) of the SM
- **Scheduling:** Random 30-minute slot within manager's shift window
- **Completion:** TL modifies lead `Audit_Status` to "Completed"
- **Expiry:** 2 days after task start time
- **Guards:** Checks for existing open tasks of same type (deduplication)

**Task Type 3: ST - Join Trial Class**
- **Trigger:** Student or employee joins Zoom trial meeting (`processMeetingEvents` consumer)
- **Assignment:** Neo Lead Owner
- **Scheduling:** Start time = current time
- **Completion:** SM joins trial class and their ID matches task owner
- **Reassignment:** If owner does not join:
  - System waits configured time
  - Re-triggers via `POST /v1/neo-tasks/trigger`
  - Routes to other eligible SMs in priority buckets (up to 5 attempts)

**Task Type 4: ST - First Task Creation**
- **Trigger:** Lead stage changes to "trial completed"
- **Post-trial follow-up task for SM**

**Zoho CRM Task Payload:**
```json
{
  "Subject": "string",
  "TaskType": "string",
  "Status": "open|completed|expired",
  "Priority": "string",
  "Due_Date": "datetime",
  "Owner": "zoho_user_id"
}
```

### High-Level Design (HLD)
```
Lead Created / Trial Booked
  → SQS: prabandhan-crm-notifications
      → Task: ST - First Connect (scheduled +2hrs, snapped to 30min)
          → SM completes Call + Email + (SMS/WA/Zalo) within 4hrs → auto-closed
          → OR: expires after 4hrs

Pitch Audit Score ≤ 6
  → SQS → Task: ST - PQS Review (TL) (random slot within TL shift)
      → TL sets Audit_Status = Completed → auto-closed
      → OR: expires after 2 days

Student joins Zoom
  → processMeetingEvents → SQS → Task: ST - Join Trial Class
      → SM joins → completed
      → SM does not join → /v1/neo-tasks/trigger → reassign (up to 5 attempts)
```

## External Integrations
- **Zoho CRM:** `zoho.crm.createRecord("Tasks", payload)` — primary task storage and tracking
- **Slack:** Task-related alerts on failure/expiry (via existing Prabandhan Slack integration)
- **Zoom:** Meeting join events via `processMeetingEvents` consumer

## Internal Service Dependencies
- **Prabandhan:** Task orchestration microservice
- **Zoho CRM Modules:** `Lead_v2`, `Tasks`, `Neo_Lead_Eligibilities`, `Activity_Tracking`

## Database Operations

### Tables Accessed
- **Zoho CRM (via API):**
  - `Lead_v2` — Lead validation and owner lookup
  - `Tasks` — Task creation, update, closure
  - `Neo_Lead_Eligibilities` — Shift timings, week-offs, manager assignments
  - `Activity_Tracking` subform — Call/email/WhatsApp log for First Connect closure

### SQL / ORM Queries
- `zoho.crm.searchRecords("Lead_v2", ...)` — fetch lead details
- `zoho.crm.createRecord("Tasks", payload)` — create task
- `zoho.crm.updateRecord("Tasks", taskId, { Status: "Completed" })` — close task
- SELECT `Neo_Lead_Eligibilities` for shift window and week-off data

### Transactions
- Task deduplication check (query for existing open tasks) must be atomic with task creation to prevent race conditions

## Performance Analysis

### Good Practices
- Automated task scheduling removes manual SM calendar management
- Deduplication guard on PQS Review prevents multiple audit tasks per lead
- Reassignment with priority buckets ensures trial class tasks are always covered

### Performance Concerns
- SQS-based task creation introduces latency between trigger event and task visibility in CRM
- Shift-based scheduling requires `Neo_Lead_Eligibilities` lookup per task — adds DB query overhead
- Zoom join event processing via `processMeetingEvents` must handle rapid consecutive joins efficiently

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Task deduplication check + creation is not atomic — race condition possible |
| Medium | Trial class reassignment (5 attempts) could spam multiple SMs if timing overlap |
| Low | `Activity_Tracking` subform closure logic relies on specific combination of activities — edge cases possible |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add distributed lock on PQS task creation to prevent duplicate tasks
- Add DLQ for `prabandhan-crm-notifications` SQS queue

### Month 1 (Architectural)
- Replace per-task shift-window DB lookup with a precomputed schedule cache (refreshed nightly)
- Implement exponential backoff on trial class reassignment (instead of fixed interval)

## Test Scenarios

### Functional Tests
- New lead created → First Connect task scheduled 2 hours later
- SM logs Call + Email + WhatsApp → First Connect task auto-closed
- Pitch audit score = 6 → PQS Review task created for TL
- Student joins Zoom → Join Trial Class task created for SM owner
- SM does not join → task reassigned (up to 5 SMs attempted)

### Performance & Security Tests
- 200 simultaneous lead creations → First Connect tasks all scheduled correctly
- Zoom join event flood — processMeetingEvents handles burst

### Edge Cases
- SM is on week-off when First Connect task is due → moved to next active day
- PQS task already exists for this lead (score re-scored ≤6) → deduplication prevents second task
- All 5 reassignment SMs unavailable for trial class → task expires without completion
