---
title: Demo Availability
category: technical-architecture
subcategory: student-lifecycle
source_id: 9438d2db
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Demo Availability

## Overview
The Demo Availability system serves available booking slots to landing and reschedule pages, dynamically resolving the user's timezone from IP or explicit parameters. It enforces day-level and slot-level booking caps and caches responses in Redis until every 5th minute to minimize landing page load times (200–300ms average).

## API Contract

### GET /demo-availability (also /v1/demoAvailability)
- **Auth:** None required
- **Query Parameters:**
  | Parameter | Required | Notes |
  |-----------|----------|-------|
  | courseName | Yes (or courseId) | |
  | days | Yes | Number of days to show slots for |
  | ip | No | User's IP for timezone detection |
  | tzId | No | Explicit Timezone ID (requires shortCode if set) |
  | shortCode | Conditional | Required if tzId is provided |
  | courseId | No | Alternative to courseName |
  | type | No | Determines slot gap (30/60 min) and same/next day logic |
  | utcDifference | No | UTC offset for timezone priority matching |

- **Response Schema:**
```json
{
  "slots": {
    "YYYY-MM-DD": [
      { "startTime": "08:00:00", "utcStartTime": "string", "available": true }
    ]
  },
  "shortCode": "string",
  "course": {},
  "courseDurationMapping": {},
  "timezones": [],
  "dialingCodes": []
}
```
- **Status Codes:** 200 OK, 400 Bad Request (missing courseName/days)
- **Caching:** Results cached in Redis until every 5th minute (e.g., 9:00, 9:05, 9:10) per unique query parameter set

## Logic Flow

### Controller Layer
`GET /demo-availability` → DemoAvailabilityController → DemoAvailabilityFacade

### Service/Facade Layer
**Timezone Resolution:**
1. If `tzId` + `shortCode` provided: use `tzId` as selected timezone; fetch available timezones using `shortCode`
2. If `ip` provided: detect country via IP; fetch associated timezones; prioritize timezone where UTC offset matches `utcDifference`

**Slot Generation:**
1. Calculate date window from `days` parameter + **+2 day buffer** (for UTC-to-local timezone differences)
2. Fetch current booking counts per slot by joining `MasterCombinations` with `DemoBookingPredictions`
3. Apply capping logic:
   - **Day Limit Check:** If `totalBookings >= dayLimit` → mark all slots on that day as `available = false`
   - **Slot Limit Check:** If `bookings >= limit` for a specific slot → mark that slot as `available = false`; else `available = true`
4. Convert UTC slots to local time, group by local date
5. Remove expired slots (current local time > slot start time)
6. Apply `type` filter:
   - `type=1`: 30-min slots, from next available slot
   - `type=2` or omitted: if local time > 10 AM, show from next day
   - `type=3`: 60-min slots, from next day

**Slot Boundaries:**
- Available between 8 AM and 10 PM in user's local time
- Every timezone slot starts at 00 minutes in IST
- Start time: convert 8 AM local → UTC; if UTC minutes = 00, add 30 minutes
- End time: convert 10 PM local → UTC

### High-Level Design (HLD)
- Tryouts service owns demo availability
- Platform service (intra-cluster, cached) provides timezone, course, and dialing code data
- Redis caching per query parameter set reduces repeated DB queries
- Default `day_limit` = 750 when creating new availability records

## External Integrations
- **Redis:** Caches availability response until next 5th minute boundary
- **Platform Service:** `/v1/mappings/timezones`, `/v1/mappings/courses` for timezone and course duration mappings (intra-cluster, cached)

## Internal Service Dependencies
- `demo_availability` table for day limits
- `demo_availability_slot_limits` for per-slot limits
- `master_combinations` + `demo_booking_predictions` for current booking counts

## Database Operations

### Tables Accessed

**`demo_availability`:**
| Column | Notes |
|--------|-------|
| id | PK |
| cdm_id | Course Duration Mapping ID |
| tz_id | Timezone ID |
| start_time | UTC — start slot boundary |
| end_time | UTC — end slot boundary |
| day_limit | Max bookings per UTC day (default 750) |

**`demo_availability_slot_limits`:**
| Column | Notes |
|--------|-------|
| daId | FK → demo_availability |
| startSlot | UTC |
| endSlot | UTC |
| enabled | 1/0 — show/hide slot |
| limit | Max bookings per slot (undefined = no per-slot cap) |

**`master_combinations`** and **`demo_booking_predictions`:**
- Joined to count booked leads per slot per country group

### SQL / ORM Queries
- SELECT from `demo_availability` WHERE `cdm_id` AND `tz_id` for slot boundaries
- JOIN `master_combinations` + `demo_booking_predictions` to aggregate bookings per slot
- SUM lead counts per UTC day for day limit check

### Transactions
N/A — Read-only at query time.

## Performance Analysis

### Good Practices
- Redis cache at 5-minute granularity reduces DB load for high-traffic landing pages
- +2 day buffer ensures timezone edge cases don't cause missing slots at day boundaries
- Platform service data is cached intra-cluster, minimizing network overhead

### Performance Concerns
- Cache TTL of 5 minutes means a slot can be overbooked by 1–2 bookings during the cache window (accepted trade-off)
- Without per-slot limit (`limit = undefined`), day-limit is the only cap — risk of single-slot overload

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | Setting `limit = undefined` to disable per-slot cap is a non-standard pattern — could be replaced with an explicit `enabled = false` flag |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add composite index on `demo_availability(cdm_id, tz_id)` for faster lookup
- Document the exact Redis key pattern for cache invalidation

### Month 1 (Architectural)
- Reduce cache TTL to 2–3 minutes for high-demand timeslots to reduce overbooking risk
- Add cache invalidation hook when a booking is created, rather than relying solely on TTL

## Test Scenarios

### Functional Tests
- Request with `ip` → verify correct timezone is resolved
- Request with `tzId` + `shortCode` → verify timezone prioritized over IP
- Day limit reached → verify all slots on that day return `available = false`
- Slot limit reached → verify specific slot returns `available = false`, others remain true
- Expired slots → verify slots before current local time are removed from response

### Performance & Security Tests
- Verify Redis cache is returned for identical query parameters within the 5-minute window
- Load test with 500 concurrent requests during peak hours

### Edge Cases
- `type` parameter omitted (should default to next-day if past 10 AM)
- Timezone with UTC+14 or UTC-12 (extreme offsets test buffer logic)
- `days = 0` edge case (should return empty or error)

## Async Jobs & Automation
- **Add Or Update Demo Availability Script:** Configures base `demo_availability` records for all timezone × course duration combinations; sets default `day_limit = 750` and calculates 8 AM–10 PM local-to-UTC boundaries
