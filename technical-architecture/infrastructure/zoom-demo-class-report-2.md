---
title: Zoom Demo Class Report 2 — Demo Class Operations API
category: technical-architecture
subcategory: infrastructure
source_id: 36905878-b130-44f9-a65f-8a1b1fe15ccf
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Zoom Demo Class Report 2 — Demo Class Operations API

## Overview
This document specifies the backend API for dynamically managing participants in active demo classes — specifically adding or removing students (bookings) and teachers to handle real-time edge cases where one participant is present but the other is not. It operates on the `demo_classes` table in the Paathshala service.

## API Contract
All endpoints are in the Paathshala service under `/v1/demo/operations/`.

**1. GET `/v1/demo/operations/eligible-bookings`**
- Uses a teacher's `confirmationId` to fetch their availability and details
- Retrieves all course/language combinations the teacher is eligible to teach
- Filters available bookings to return eligible students
- Response: List of eligible student bookings for the teacher

**2. POST `/v1/demo/operations/add/student`**
- Operation: `student_addition`
- Body: `{ classId, bookingId }`
- Action: Inserts `bookingId` into the `demo_classes` table for the given `classId`

**3. POST `/v1/demo/operations/remove/student`**
- Operation: `student_removal`
- Body: `{ classId }`
- Action: Sets `booking_id = NULL` in `demo_classes` for the given `classId`

**4. GET `/v1/demo/operations/eligible-teachers`**
- Param: `classId`
- Uses `classId` to find the associated `bookingId` and course/language combination
- Fetches available teachers from `teacher_demo_availabilities` table
- Response: List of eligible available teachers

**5. POST `/v1/demo/operations/add/teacher`**
- Operation: `teacher_addition`
- Body: `{ classId, availabilityId }`
- Action: Looks up the availability ID, creates a new confirmation if none exists, updates `teacher_confirmation_id` in `demo_classes`

**6. POST `/v1/demo/operations/remove/teacher`**
- Operation: `teacher_removal`
- Body: `{ classId }`
- Action: Sets `teacher_confirmation_id = NULL` in `demo_classes`

**Auth:** Standard internal Bearer token.

## Logic Flow
### Controller Layer
This API is used by operations teams during live demo classes to resolve two scenarios:
1. Teacher is in the class but no student is present
2. Student is in the class but no teacher is present

### Service/Facade Layer
**Scenario 1 — Student Missing (Teacher Present):**
1. Call `GET /eligible-teachers` with `classId`
2. System looks up `bookingId` from `classId`, finds the course/language combination
3. Fetches available teachers from `teacher_demo_availabilities`
4. Ops confirms a new teacher selection
5. Call `POST /add/teacher` — system creates confirmation if needed, updates `teacher_confirmation_id`

**Scenario 2 — Teacher Missing (Student Present):**
1. Call `GET /eligible-bookings` with teacher's `confirmationId`
2. System fetches teacher availability, finds combinations they can teach
3. Filters bookings for eligible students
4. Ops confirms a new student selection
5. Call `POST /add/student` — system inserts `bookingId` into `demo_classes`

**Key Definitions:**
- **Demo class** = mapping of a `bookingId` + `teacherConfirmationId` in `demo_classes`
- **Booking** = student request containing: start time, duration, course, language

### High-Level Design (HLD)
```
Active Demo Class
        │
        ├── Teacher present, Student missing?
        │         │
        │         ▼
        │   GET /eligible-bookings (using teacherConfirmationId)
        │         │
        │         ▼
        │   POST /add/student (insert bookingId into demo_classes)
        │
        └── Student present, Teacher missing?
                  │
                  ▼
          GET /eligible-teachers (using classId)
                  │
                  ▼
          POST /add/teacher (create confirmation if needed, update demo_classes)
```

## External Integrations
N/A — Internal Paathshala service operations. No third-party integrations.

## Internal Service Dependencies
- Demo Operations API → Paathshala DB (`demo_classes`, `teacher_demo_availabilities` tables)
- Demo Operations API → Tryouts (for booking data and teacher eligibility/combination logic)
- Demo Operations API → Dronacharya (teacher profile data)

## Database Operations
### Tables Accessed

**demo_classes**
| Column | Description |
|--------|-------------|
| id | Class identifier |
| booking_id | FK to booking (student) — nullable |
| teacher_confirmation_id | FK to teacher confirmation — nullable |

**teacher_demo_availabilities**
| Column | Description |
|--------|-------------|
| id | Availability identifier |
| teacher details | Course/language eligibility |
| availability | Time slot availability |

### SQL / ORM Queries
- Add student: `UPDATE demo_classes SET booking_id = :bookingId WHERE id = :classId`
- Remove student: `UPDATE demo_classes SET booking_id = NULL WHERE id = :classId`
- Add teacher: Check if confirmation exists → INSERT or UPDATE `teacher_confirmation_id` in demo_classes
- Remove teacher: `UPDATE demo_classes SET teacher_confirmation_id = NULL WHERE id = :classId`
- Eligible teachers: `SELECT * FROM teacher_demo_availabilities WHERE combination IN (:combinations) AND available = true`

### Transactions
- `add/teacher` operation (find availability → create/check confirmation → update `demo_classes`) should be wrapped in a transaction to prevent partial updates

## Performance Analysis
### Good Practices
- Eligibility filtering prevents ops from assigning incompatible teachers or students (wrong course/language)
- Nullable `booking_id` and `teacher_confirmation_id` in `demo_classes` supports partial class states cleanly
- Confirmation auto-creation on `add/teacher` reduces ops friction

### Performance Concerns
- Eligibility lookup (`GET /eligible-bookings`, `GET /eligible-teachers`) likely involves JOIN across multiple tables — needs indexing
- No optimistic locking documented — two ops users could attempt to assign different teachers simultaneously

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No transaction wrapping documented for `add/teacher` multi-step operation |
| Medium | Concurrent operations race condition risk — no locking strategy documented |
| Low | No audit trail for ops-driven participant changes during live classes |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Wrap `add/teacher` in a database transaction
- Add an audit log entry for each add/remove operation (who made the change, when, class ID)
- Index `demo_classes.booking_id` and `demo_classes.teacher_confirmation_id` for fast lookups

### Month 1 (Architectural)
- Add optimistic locking or a class-level lock during active operations to prevent concurrent modification
- Build a notification to the assigned teacher/student when they are added to an active class via this flow

## Test Scenarios
### Functional Tests
- `GET /eligible-bookings` returns only students eligible for the teacher's course/language
- `POST /add/student` correctly sets `booking_id` in `demo_classes`
- `POST /remove/student` correctly nullifies `booking_id`
- `POST /add/teacher` creates a new confirmation when none exists
- `POST /remove/teacher` correctly nullifies `teacher_confirmation_id`

### Performance & Security Tests
- Eligibility endpoints return results in <500ms for realistic data volumes
- Only authorized operations team members can call these endpoints

### Edge Cases
- Attempting to add a student when `booking_id` is already set — should return error or overwrite?
- Class ends while an add/remove operation is in progress — should be blocked or completed?
- Teacher availability expires between eligibility check and add operation — stale availability handling

## Async Jobs & ETL
N/A — Synchronous operational APIs. No async jobs.
