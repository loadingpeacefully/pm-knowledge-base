---
title: Zoom Demo Class Report 1 — Real-time Class Monitoring
category: technical-architecture
subcategory: infrastructure
source_id: d493c8a7-c933-411e-bb34-f8721db5444a
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Zoom Demo Class Report 1 — Real-time Class Monitoring

## Overview
This document describes the real-time demo class monitoring system that tracks teacher and student join times, attendance durations, class errors, and Zoom meeting details. It powers a "Current Running Classes" dashboard and uses the `class/demo/class-by-time` API to aggregate class data within a specified time window.

## API Contract
**Primary API:**
- Method: `GET`
- Path: `/class/demo/class-by-time`
- Required Params: `startTime`, `endTime`
- Description: Fetches all demo classes within a time window, aggregating meeting details, teacher profiles, class metrics, and errors

**Supporting Data Fetches (per class):**
- Fetch meeting joiner data using `vendor_meeting_id`
- Fetch class errors from `paathshala.class_errors` table using `classId`
- Fetch class metrics (`student-join-time`, `teacher-join-time`) from `demo_class_metrics` using `classId`

**Auth:** Standard internal Bearer token.

## Logic Flow
### Controller Layer
1. Dashboard calls `/class/demo/class-by-time` with `startTime` and `endTime`
2. System retrieves all bookings and teacher-demo-confirmations within the window
3. `demo_classes` table filtered for classes with `bookingId`, `teacherConfirmationId`, or both
4. For each class, a `classDetails` object is built containing: meeting details, teacher profile, class metrics, class errors
5. Meeting joiner data fetched per class using `vendor_meeting_id`
6. Dashboard renders "Current Running Classes" with real-time join statuses

### Service/Facade Layer
**Attendance Tracking Logic:**
- System listens for `meeting.participant_joined` and `meeting.participant_left` Zoom webhook events
- Captures: user name, join time, leave time
- `joinStatus` flag: `1` = currently in meeting, `0` = has left
- Duration formula: `duration = duration + (end_time - lastJoin)` (cumulative, handles re-joins)
- Re-join handling: finds existing participant entry by index and updates instead of creating a new entry

**Class Metrics Tracked:**
- `student-join-time` — when student entered the Zoom meeting
- `teacher-join-time` — when teacher entered the Zoom meeting
- Total participation duration per participant

### High-Level Design (HLD)
```
Dashboard Request (startTime, endTime)
        │
        ▼
/class/demo/class-by-time API
        │
        ├── Query demo_classes (bookingId + teacherConfirmationId filter)
        ├── Query demo_class_metrics (student/teacher join times)
        ├── Query class_errors table (per classId)
        └── Fetch meeting joiner data (via vendor_meeting_id)
                │
                ▼
classDetails object aggregated per class
        │
        ▼
Dashboard: "Current Running Classes"
(teacher name, student name, contacts, join statuses, meeting links, durations)
```

**Zoom Webhook Flow (Async):**
```
Zoom Event (participant_joined / participant_left)
        │
        ▼
Webhook handler
        │
        ├── Update joinStatus flag in classDetails
        ├── Calculate duration = duration + (end_time - lastJoin)
        └── Store in demo_class_metrics
```

## External Integrations
- **Zoom** — Meeting provider; `vendor_meeting_id` used as the key for fetching joiner data. Events: `meeting.participant_joined`, `meeting.participant_left`
- **Zoom Webhook** — Async event feed for real-time attendance tracking

## Internal Service Dependencies
- Zoom Demo Class Report → Paathshala (class data, class errors)
- Zoom Demo Class Report → Doordarshan (meeting configuration, host/participant links)
- Zoom Demo Class Report → Tryouts (demo booking data, teacher confirmations)

## Database Operations
### Tables Accessed

**demo_class_metrics**
| Column | Description |
|--------|-------------|
| classId | FK to demo class |
| student-join-time | Timestamp of student join |
| teacher-join-time | Timestamp of teacher join |

**demo_classes**
| Column | Description |
|--------|-------------|
| id | Class identifier |
| bookingId | FK to booking |
| teacherConfirmationId | FK to teacher confirmation |

**class_errors (paathshala DB)**
| Column | Description |
|--------|-------------|
| classId | FK to class |
| error details | Error type and data |

**meetings (Doordarshan)**
| Column | Description |
|--------|-------------|
| vendor_meeting_id | Zoom meeting identifier |
| licence_id | Zoom license used |
| host_link | Authenticated host URL |
| participant_link | Encrypted participant URL |
| fallback_link | Backup joining URL |
| status | Meeting status (SCHEDULED, LIVE, etc.) |
| start_at / end_at / created_at / updated_at | Timestamps |

### SQL / ORM Queries
- Fetch classes in window: `SELECT * FROM demo_classes WHERE (bookingId IS NOT NULL OR teacherConfirmationId IS NOT NULL) AND start_at BETWEEN :startTime AND :endTime`
- Fetch class metrics: `SELECT student_join_time, teacher_join_time FROM demo_class_metrics WHERE classId = :classId`
- Fetch class errors: `SELECT * FROM class_errors WHERE classId = :classId`

### Transactions
N/A — Read-heavy reporting queries; no transactional writes in the monitoring flow.

## Performance Analysis
### Good Practices
- `classDetails` central object aggregates all data for a class cleanly
- `joinStatus` flag provides O(1) current presence check
- Duration formula handles re-joins without data duplication
- Deduplicated participant list prevents double-counting

### Performance Concerns
- **Individual API calls per class** — fetching meeting joiner data per class in a loop (N+1 problem)
- Single bulk API call recommended as future improvement but not yet implemented
- Unnecessary data in JSON responses identified (suggested for removal)

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Loop of individual API calls for meeting/joiner data — N+1 performance problem |
| Medium | Unnecessary data included in JSON responses — increases payload size |
| Low | No caching layer for `class_errors` or `demo_class_metrics` during active monitoring sessions |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Remove unnecessary fields from JSON responses for meeting and joiner data
- Add index on `demo_class_metrics.classId` and `class_errors.classId`

### Month 1 (Architectural)
- Replace the per-class API call loop with a single bulk API call to fetch all meeting and joiner details for all active classes in the time window simultaneously
- Add Redis cache for active class metrics during the class window to reduce DB reads on every dashboard refresh

## Test Scenarios
### Functional Tests
- `/class/demo/class-by-time` returns all classes within the time window
- Student join time correctly captured when `meeting.participant_joined` event fires
- Duration correctly accumulates when student leaves and rejoins the same meeting
- Class errors fetched and mapped to correct classes

### Performance & Security Tests
- Load test with 50 simultaneous active demo classes — verify response time under 2 seconds
- Verify host_link (with auth tokens) is not exposed to student-facing APIs

### Edge Cases
- Class with `bookingId` but no `teacherConfirmationId` — should still appear in dashboard
- Student with no Zoom events — `joinStatus = 0`, duration = 0
- Zoom webhook delivery failure — missing join/leave events — how is data reconciled?

## Async Jobs & ETL
- **Zoom Webhook** — Async event listener for `meeting.participant_joined` and `meeting.participant_left` events; updates real-time attendance data
- `demo_class_metrics` is written asynchronously by the webhook handler
