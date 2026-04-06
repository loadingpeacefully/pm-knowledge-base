---
title: List Bookings
category: technical-architecture
subcategory: api-specifications
source_id: 6c3446f4
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# List Bookings

## Overview
The List Bookings API exposes two endpoints for retrieving and managing demo class bookings: a simple time-range GET endpoint for operational use, and the advanced `POST /classes` for enriched filtered queries. Both endpoints also support booking state transitions (cancel, reschedule, unqualify) that trigger downstream communication actions.

## API Contract

### GET /tryouts/v1/booking/classes
- **Auth:** Internal/Admin
- **Query Params:** `startTime` (required), `endTime` (required)
- **Purpose:** Fetch all active bookings between the time range
- **Response Fields Per Booking:**
```
id, parentName, childName, grade, phone, language, slot, status, joinStatus, bookingType,
linkParams.id, countryName, countryId, dialCode, courseId, tzId, utmSource, utmCampaign,
email, duration, courseName
```

### PUT/PATCH /tryouts/v1/booking/:updateType
- `:updateType` values: `Cancel`, `Reschedule`, `Unqualify`

**Cancel Payload:**
- Updates: `joinStatus = 'cancelled'`, `status = 'inactive'`
- Triggers: `POST /communications/demo-cancel` with `objectId`
- Then: `DELETE /communications` to remove remaining scheduled messages

**Reschedule Payload:**
- Fetches available slots from `/prashashak/v1/reschedule`
- Updates: `datetime`, `joinStatus = 'created'`, `bookingType = 'rescheduled'`, `status = 'active'`
- Then: `DELETE /communications` to remove old scheduled messages
- New communication schedule created after reschedule

**Unqualify Payload:**
- Updates: `joinStatus = 'unqualified'`, `status = 'inactive'`
- Then: `DELETE /communications` to remove scheduled messages

## Logic Flow

### Controller Layer
`GET /tryouts/v1/booking/classes` → BookingController.getClasses()
`PUT /tryouts/v1/booking/:updateType` → BookingController.updateBooking()

### Service/Facade Layer
**GET /tryouts/v1/booking/classes Implementation:**
1. Query `bookings` table WHERE `status = 'active'` AND `student_id IS NOT NULL` AND time range
2. Loop through bookings; enrich each:
   - GET student details via `/eklavya/v1/student/details?studentId=`
   - GET timezone details via `/platform/v1/mappings/timezones/:id/details`
   - Map courses from `/platform/v1/mappings/courses`
3. Return enriched array

**Cancel Flow:**
1. UPDATE `bookings`: `joinStatus = 'cancelled'`, `status = 'inactive'`
2. POST `/communications/demo-cancel` with `objectId`
3. DELETE `/communications` with `objectId`

**Reschedule Flow:**
1. Fetch slots from `/prashashak/v1/reschedule` (reasons and available times)
2. UPDATE `bookings`: new `datetime`, `joinStatus = 'created'`, `bookingType = 'rescheduled'`, `status = 'active'`
3. DELETE `/communications` with `objectId`
4. New communications scheduled by SNS/SQS booking update event

**Unqualify Flow:**
1. UPDATE `bookings`: `joinStatus = 'unqualified'`, `status = 'inactive'`
2. DELETE `/communications` with `objectId`

### High-Level Design (HLD)
- Tryouts service owns booking state management
- All state transitions also trigger communication cleanup
- GET endpoint enriches data via sequential API calls to Eklavya and Platform (potential N+1 pattern)

## External Integrations
N/A — All data sources are internal microservices.

## Internal Service Dependencies
- Eklavya (Student Service): `/v1/student/details` for per-booking student enrichment
- Platform Service: `/v1/mappings/timezones/:id/details` and `/v1/mappings/courses`
- Tryouts Communications: `/communications/demo-cancel` (POST) and `/communications` (DELETE)
- Prashashak: `/v1/reschedule` for available reschedule slots and reasons

## Database Operations

### Tables Accessed

**`tryouts.bookings`:**
| Column |
|--------|
| id, datetime, duration, courseId, studentId, status, joinStatus, bookingType, objectId, tzId, phone, grade |

### SQL / ORM Queries
- SELECT `bookings` WHERE `status = 'active'` AND `student_id IS NOT NULL` AND `datetime BETWEEN :startTime AND :endTime`
- UPDATE `bookings` SET `joinStatus`, `status`, `bookingType`, `datetime` per updateType

### Transactions
N/A — State transitions are sequential updates; no multi-table transactions documented.

## Performance Analysis

### Good Practices
- Filtering by `status = 'active'` and non-null `student_id` reduces result set early
- Communication cleanup (DELETE) always follows state transitions, preventing stale scheduled messages

### Performance Concerns
- GET endpoint loops through bookings making sequential Eklavya + Platform API calls — classic N+1 pattern at scale
- No pagination documented for GET endpoint

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | N+1 API call pattern in GET handler: sequential per-booking student and timezone lookups instead of batch API calls |
| Medium | No pagination on GET endpoint — requesting a large time window could return thousands of records |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add `limit` and `offset` pagination to `GET /tryouts/v1/booking/classes`
- Batch student IDs and call `POST /v1/student/details/bulk` instead of per-booking lookups

### Month 1 (Architectural)
- Replace sequential enrichment loop with `Promise.all` parallel calls
- Cache timezone and course mappings in-memory or Redis to eliminate repeated Platform service calls

## Test Scenarios

### Functional Tests
- GET with valid time range → returns enriched booking list
- GET with no `startTime` → 400 error
- Cancel booking → `status = inactive`, cancellation comms triggered, scheduled comms deleted
- Reschedule booking → new slot applied, `bookingType = rescheduled`, old comms deleted
- Unqualify booking → `status = inactive`, comms deleted

### Performance & Security Tests
- GET with 7-day range containing 1000 bookings → verify sequential API call does not time out
- Verify admin auth required to access state transition endpoints

### Edge Cases
- Cancel already-cancelled booking (idempotency check)
- Reschedule when no available slots found from Prashashak
- Unqualify a booking that was already rescheduled

## Async Jobs & Automation
- **SNS/SQS (booking_comms queue):** After reschedule, `isDateTimeModified = true` triggers new communication scheduling via SNS fan-out
- **DELETE /communications:** Called synchronously during cancel, reschedule, and unqualify flows
