---
title: First Connect with Customer and PQS Review Task
category: technical-architecture
subcategory: student-lifecycle
source_id: 2237955b
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# First Connect with Customer and PQS Review Task

## Overview
This document covers two interconnected Zoho CRM automation workflows: the First Connect Task (ensures sales agents initiate timely outreach to new leads) and the PQS (Pitch Quality Score) Review Task (provisions TL review tasks when a sales agent's AI-evaluated pitch score is at or below 6). Both use AI-driven scheduling, shift-awareness, and strict closure rules.

## API Contract

### Zoho CRM Internal Automation APIs
All operations use Zoho Deluge script functions:

- **`zoho.crm.createRecord("Tasks", payload)`** — Creates task in Zoho CRM
- **`automation.STL_Pitch_Quality_Score_Review_Task(Int leadId)`** — PQS review task automation entry point

## Logic Flow

### Controller Layer
Zoho CRM automations triggered by:
- Lead creation → `ST Create Task on Lead Creation`
- Lead updated to trial booked stage → same automation
- Neo Lead updated + `Sales_Pitch_Audit_Score <= 6` → `STL_Pitch_Quality_Score_Review_Task`
- TL sets `Audit_Status = Completed` → `STL Pitch Quality Score Review Task Close`

### Service/Facade Layer

**PQS Review Task Creation:**
1. Automation `STL_Pitch_Quality_Score_Review_Task(leadId)` triggered when:
   - Layout = "Standard"
   - Neo Lead Owner is not empty or "Zoho Developer"
   - `Sales_Pitch_Audit_Score <= 6`
   - Lead Stage is in: Parent Contacted, Pitching Done, Closed Won, Closed Lost
2. Query `Neo_Lead_Eligibilities` module using Owner's User ID → fetch `Shift_Start_IST`, `Shift_End_IST`, `Week_Off`, `Manager`
3. If shift or manager details missing → halt execution
4. Generate random task time within agent's shift window → **snap to 30-min interval** (e.g., 10:17 → 10:30)
5. Check for existing open PQS Review tasks for this lead (TaskType = "ST - Pitch Quality Score Review (TL)", Status in [Empty, Not Started, In Progress]) → if found, skip (duplicate prevention)
6. Create Zoho task: `zoho.crm.createRecord("Tasks", payload)` assigned to Manager with 2-day completion window

**PQS Task Closure:**
1. TL changes `Audit_Status` to "Completed"
2. Query all tasks related to the lead; filter for open PQS Review tasks
3. Update `Status` and `Main_Status` to "Completed"
4. Task auto-expires 2 days after Start_Time if not completed

**First Connect Task Creation:**
1. Trigger: lead created OR lead updated to trial booked stage
2. Validate lead has valid owner via `Lead_v2` module
3. Base task time = `Lead Created Time + 2 hours`, rounded to nearest 30-minute slot
4. Apply time restrictions:
   - Must be within agent's active shift (via `Neo_Lead_Eligibilities`)
   - At least 1 hour after current time
   - Must occur before `Trial_Time - 1 hour`
5. If task falls on week-off or agent unavailable → shift to next active working day
6. Regional override: if Business Region starts with "vietnam" → assign to `Co_Owner1` (if available), else default to Lead Owner

**First Connect Task Closure:**
1. `ST Close Pre Demo Tasks` automation monitors `Activity_Tracking` subform
2. Runs only if latest activity created/updated within strict 1-hour execution window
3. If `Activity_Disposition = "Picked"` + `Mode = "Call"` → update `Lead.Last_Connected_Date_Time`
4. Strict closure: to mark Completed, activities must be executed by task owner within ~4 hours:
   - **ALL of the following required:** Call AND Email AND at least one of (SMS, WhatsApp, Zalo)
5. On satisfaction → update `Task_Outcome` to match `Activity_Status`
6. Auto-expires 4 hours after Start_Time if unfulfilled

**AI Scoring (PQS):**
- Transcripts evaluated via 10-dimensional rubric with 17 distinct event types
- 0–2 scoring per dimension
- Timestamped, speaker-labelled event ledger as "ground truth" (~91% dispute-free at ~500 sessions/day)

### High-Level Design (HLD)
- Both workflows are Zoho CRM-native automations (Deluge scripting)
- `Neo_Lead_Eligibilities` module acts as the scheduling/routing database for all agents
- `Activity_Tracking` subform on Lead module is the source of truth for outbound communication
- PQS scoring computed via external AI pipeline → stored as `Sales_Pitch_Audit_Score` on `Lead_v2`

## External Integrations
- **AI Pipeline (PQS Scoring):** Transforms class transcripts into structured event logs; evaluates pitch against 10-dimensional rubric
- **Zoho CRM:** All task creation, update, and closure operations

## Internal Service Dependencies
- `Lead_v2` (Zoho module): Lead demographic data, Lead Stage, `Sales_Pitch_Audit_Score`, `Last_Connected_Date_Time`
- `Neo_Lead_Eligibilities` (Zoho module): SM/agent shift times, manager hierarchy, week-off status
- `Tasks` (Zoho module): Task state machine
- `Activity_Tracking` (Zoho subform on Lead): Communication action ledger

## Database Operations

### Tables Accessed (Zoho CRM Modules)

**`Lead_v2`:**
| Field | Notes |
|-------|-------|
| Layout | Must be "Standard" for PQS trigger |
| Neo_Lead_Owner | Must be non-empty |
| Sales_Pitch_Audit_Score | Triggers PQS if <= 6 |
| Lead_Stage | Parent Contacted, Pitching Done, Closed Won, Closed Lost |
| Last_Connected_Date_Time | Updated when call picked |
| Business_Region | Vietnam check for Co_Owner1 assignment |

**`Neo_Lead_Eligibilities`:**
| Field | Notes |
|-------|-------|
| Shift_Start_IST | Agent shift start |
| Shift_End_IST | Agent shift end |
| Week_Off | Days off |
| Manager | TL/manager for PQS task assignment |

**`Tasks`:**
| Field | Notes |
|-------|-------|
| TaskType | ST - Join Trial Class / ST - Pitch Quality Score Review (TL) |
| Status | Empty, Not Started, In Progress, Completed, Expired |
| Main_Status | Mirrors Status |
| Task_Outcome | Set on closure |
| Start_Time, End_Time | Scheduling |

**`Activity_Tracking`** (Subform on Lead):
| Field | Notes |
|-------|-------|
| Activity_Disposition | e.g., Picked |
| Mode | Call, Email, SMS, WhatsApp, Zalo |

### SQL / ORM Queries
N/A — All operations use Zoho CRM Deluge API functions.

### Transactions
N/A — Zoho CRM manages atomicity internally.

## Performance Analysis

### Good Practices
- 30-minute interval snapping ensures task times align with practical shift scheduling
- Duplicate prevention check before task creation prevents CRM task spam
- Multi-channel closure requirement (Call + Email + one of SMS/WhatsApp/Zalo) ensures quality first-contact standard

### Performance Concerns
- AI pipeline for PQS scoring operates externally — latency in score availability could delay PQS task creation
- `Neo_Lead_Eligibilities` lookup on every task creation adds a CRM query overhead

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Vietnam region hard-coded as special case for Co_Owner1 assignment — should use a config-driven region override table |
| Low | 1-hour execution window for `ST Close Pre Demo Tasks` automation could miss activity updates in edge timing scenarios |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Cache `Neo_Lead_Eligibilities` data per agent with 1-hour TTL to reduce CRM lookup frequency
- Replace Vietnam region hard-code with a configurable `Region_Assignment_Rules` module

### Month 1 (Architectural)
- Pre-compute daily shift windows for all agents at midnight to avoid real-time lookups
- Build a monitoring dashboard for PQS score distribution and task creation/closure rates

## Test Scenarios

### Functional Tests
- PQS score = 6 → review task created for TL within shift hours
- PQS score = 7 → no task created
- Duplicate PQS review task for same lead → second creation skipped
- TL sets Audit_Status = Completed → task closed
- New lead created → first connect task scheduled at correct time
- Lead in Vietnam region → task assigned to Co_Owner1
- Agent on week-off → task shifted to next active working day
- Agent performs Call + Email + WhatsApp within 4 hours → first connect task closed

### Performance & Security Tests
- Verify only Lead Owner and Manager can view/update their respective tasks
- Simulate 500 concurrent lead creations and verify first connect tasks are created without CRM throttling

### Edge Cases
- Shift times missing in `Neo_Lead_Eligibilities` → PQS automation halts gracefully
- `Trial_Time - 1 hour` is before `Lead Created Time + 2 hours` (impossible scheduling window)
- Agent has no working days in the next 7 days (shift + week-off overlap)

## Async Jobs & Automation
- **`STL_Pitch_Quality_Score_Review_Task` Automation:** Triggered by Neo Lead update when `Sales_Pitch_Audit_Score <= 6`; creates TL review task
- **`STL Pitch Quality Score Review Task Close` Automation:** Triggered by `Audit_Status = Completed`; closes all related open PQS tasks
- **`ST Create Task on Lead Creation` Automation:** Triggered by lead creation or trial booked update; creates first connect task
- **`ST Close Pre Demo Tasks` Automation:** Monitors `Activity_Tracking` for qualifying Call + Email + SMS/WA/Zalo combination; closes first connect task
- **PQS AI Scoring Pipeline:** External async pipeline that scores pitch recordings on 10-dimensional rubric and writes `Sales_Pitch_Audit_Score` to `Lead_v2`
