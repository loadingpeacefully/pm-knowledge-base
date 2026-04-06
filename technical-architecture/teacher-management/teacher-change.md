---
title: Teacher Change
category: technical-architecture
subcategory: teacher-management
source_id: ffda40cf
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Teacher Change

## Overview
The Teacher Change system manages the complete lifecycle of requests to reassign a student to a different teacher, supporting both temporary (time-bounded) and permanent teacher replacements. It relies on a multi-step teacher-filtering algorithm that queries availability, profile attributes, and student capacity before confirming a replacement.

## API Contract

### GET /teacher-change/form-data
- **Auth:** JWT Bearer token
- **Response:**
```json
{
  "requestTypes": [{ "name": "string", "value": "temporary|permanent" }],
  "reasonsSources": [{
    "name": "string",
    "reasons": [{ "id": int, "name": "string", "subreasons": [{ "id": int, "name": "string" }] }]
  }]
}
```

### POST /teacher-change/requests?type=["temporary"|"permanent"]
- **Auth:** JWT Bearer token
- **Request Body:**
```json
{
  "reasonId": int,
  "referenceType": "lms|ops",
  "initiator": int,
  "studentId": int,
  "studentBalanceId": int,
  "oldTeacherId": int,
  "source": "student_dashboard|admin_dashboard",
  "startTime": "ISO8601 (required if type=temporary)",
  "endTime": "ISO8601 (required if type=temporary)",
  "comments": "string"
}
```

### GET /teacher-change/requests?type=&studentId=&status=&reference_type=
- **Auth:** JWT Bearer token
- **Query Params:** `type`, `studentId`, `status`, `reference_type`
- **Response:** Array of teacher change request objects

### POST /teacher-change/teachers-list
- **Auth:** JWT Bearer token
- **Response:**
```json
[{
  "requestId": int,
  "availability": [{ "day": "string", "time": "string" }],
  "countryId": int,
  "gender": "string",
  "languageId": int,
  "leadId": int,
  "scoringMetricKey": "string",
  "minStudentCount": int,
  "maxStudentCount": int,
  "teacherId": int
}]
```

### POST /teacher-change/requests/expire/:id
- **Auth:** JWT Bearer token
- **Purpose:** Manually expires a specific teacher change request

## Logic Flow

### Controller Layer
Routes map to: `GET /form-data`, `POST /requests`, `GET /requests`, `POST /teachers-list`, `POST /requests/expire/:id`

### Service/Facade Layer
**`GetTeachers()` Method:**
1. If `teacherId` is provided in the request, bypass filtering and return that teacher directly
2. Fetch student's `course_id` from the database
3. Query the Calendar API to find all LTA-eligible teachers matching the course and availability
4. Apply sequential filters:
   - `teachers` table: match by `lead_id` and `country_id`
   - `teacher_profile` table: match by `gender`
   - `teacher_languages` table: match by `language_id`
5. Calculate current student count for all filtered teachers

**`GetDataForAboveTeachers()` Method:**
1. Gather existing data from `teacher` and `teacher_profile` tables
2. Fetch missing data: languages, LTA availability, student count, skills
3. Construct final response payload

### High-Level Design (HLD)
- Paathshala (Class Service) owns the teacher change domain
- Calendar API is queried for LTA availability
- Teacher filtering is sequential: country → gender → language
- Status lifecycle: REQUESTED → ACTIVE → REVERTED / EXPIRED / COMPLETED
- Change Status Update Cron manages automated status transitions (currently marked TODO)

## External Integrations
- **Calendar API:** Queried to fetch real-time teacher availability for Long Term Assignments (LTA)
- **Upcoming Class Details Lambda (upcomingClassDetails):** Queries `teacher_change_requests` to gather metrics for classes in the next 24 hours

## Internal Service Dependencies
- `PaidClassService.upcomingClassDetails()` — reads `teacher_change_requests` table for class context
- Dronacharya (Teacher Service) — provides teacher profile, language, and LTA data

## Database Operations

### Tables Accessed
**`teacher_change_reasons`** (Paathshala DB):
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK, Auto Increment |
| source | varchar | |
| reason | varchar | |
| sub_reason | varchar | nullable |
| active | tinyint | default 1 |
| created_at | timestamp | |
| updated_at | timestamp | |

**`teacher_change_requests`** (Paathshala DB):
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| type | ENUM | 'temporary', 'permanent' |
| student_id | int | |
| student_balance_id | int | |
| old_teacher_id | int | |
| new_teacher_id | int | |
| reason_id | int | FK → teacher_change_reasons |
| reference_type | ENUM | 'lms', 'ops' |
| reference_id | int | |
| start_at | datetime | |
| end_at | datetime | |
| status | ENUM | 'REQUESTED', 'ACTIVE', 'REVERTED', 'EXPIRED', 'COMPLETED' |
| source | varchar | |
| comments | text | |
| created_at | timestamp | |
| created_by | int | |
| updated_at | timestamp | |
| updated_by | int | |

### SQL / ORM Queries
- `SELECT` on `teachers` WHERE `lead_id` AND `country_id` match filters
- `SELECT` on `teacher_profile` WHERE `gender` matches
- `SELECT` on `teacher_languages` WHERE `language_id` matches
- Student count aggregation across filtered teacher IDs

### Transactions
- Request creation is a single write to `teacher_change_requests`

## Performance Analysis

### Good Practices
- Teacher filtering is applied sequentially to reduce result set early
- Direct `teacherId` shortcut bypasses all filtering logic for targeted assignments

### Performance Concerns
- Multiple sequential DB queries (teachers → teacher_profile → teacher_languages) without explicit JOIN optimization
- Calendar API external call adds latency to the teacher list fetch

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Change Status Update Cron is documented as `// TODO` — automated lifecycle status transitions are not implemented |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Merge teacher filtering queries into a single JOIN query instead of sequential queries
- Add composite index on `teacher_change_requests(student_id, status)`

### Month 1 (Architectural)
- Implement the Change Status Update Cron for automated lifecycle management
- Cache Calendar API LTA results in Redis with short TTL to reduce external latency

## Test Scenarios

### Functional Tests
- Create temporary change request with valid start/end times
- Create permanent change request without time bounds
- Fetch teachers list with and without pre-selected teacherId
- Expire request via manual API call
- Verify status transitions: REQUESTED → ACTIVE → COMPLETED

### Performance & Security Tests
- Verify JWT auth enforced on all endpoints
- Test with high teacher list cardinality to benchmark filter query time

### Edge Cases
- `teacherId` provided in teachers-list request (should bypass filtering)
- Temporary change request missing `startTime` or `endTime` (should 400)
- Expire already-expired request (idempotency check)

## Async Jobs & Automation
- **Change Status Update Cron:** Intended to auto-manage status transitions (REQUESTED → ACTIVE → EXPIRED/COMPLETED). Currently unimplemented (marked `// TODO`)
- **upcomingClassDetails Lambda (Cron-triggered):** Reads `teacher_change_requests` as part of building the 24-hour class context window for teachers
