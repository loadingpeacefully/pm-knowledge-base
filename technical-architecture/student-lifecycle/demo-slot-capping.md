---
title: Demo Slot Capping
category: technical-architecture
subcategory: student-lifecycle
source_id: e8bf67aa
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Demo Slot Capping

## Overview
The Demo Slot Capping system enforces booking limits on demo class slots at both daily and per-slot granularities. It is the capacity management layer powering the `/demo-availability` endpoint, preventing overbooking through a two-tier capping algorithm applied after timezone resolution and current booking count aggregation.

## API Contract

### GET /v1/demoAvailability (also /demo-availability)
- **Auth:** None required
- **Query Parameters:**
  | Parameter | Required | Notes |
  |-----------|----------|-------|
  | courseName | Yes (or courseId) | |
  | days | Yes | |
  | ip | No | For timezone detection |
  | tzId | No | Explicit timezone (requires shortCode) |
  | shortCode | Conditional | Required if tzId set |
  | type | No | Slot gap and day offset control |
  | utcDifference | No | UTC offset for timezone matching |
- **Caching:** Per query parameter set, cached until next 5th minute
- **Performance Target:** 200–300ms average response time

## Logic Flow

### Controller Layer
`GET /v1/demoAvailability` → DemoAvailabilityController → Capping logic in service layer

### Service/Facade Layer
**Capping Algorithm (5 Steps):**

1. **Timezone Detection**
   - If `tzId` + `shortCode`: fetch timezones by short code, prioritize `tzId`
   - If `ip`: detect country by IP, fetch timezones, match UTC offset to `utcDifference`

2. **Date Window Calculation**
   - Calculate dates needed based on `days` parameter
   - Add **+2 day buffer** for UTC-to-local conversion edge cases

3. **Fetch Booking Counts**
   - JOIN `MasterCombinations` with `DemoBookingPredictions`
   - Aggregate current booked lead counts per slot for the specific country group

4. **Apply Capping Limits**
   - **Day Limit Check:** `SUM(bookings on UTC day) >= dayLimit` → set `available = false` for all slots on that day
   - **Slot Limit Check:** If day limit not breached, compare slot bookings vs. slot `limit`:
     - `bookings >= limit` → `available = false`
     - `bookings < limit` → `available = true`
   - If `limit = undefined` (not set): skip per-slot check, only day limit applies

5. **Local Time Conversion & Cleanup**
   - Convert UTC slots to user's local time
   - Group by local date
   - Remove expired slots (current local time > slot start time)
   - Apply `type` filter (next available slot vs. next day, 30 vs. 60 min gaps)

### High-Level Design (HLD)
- Tryouts service owns the capping domain
- Two-tier capping: daily capacity + per-slot capacity
- Default `day_limit = 750` created by the Add Or Update Demo Availability Script
- `limit = undefined` (not 0) disables per-slot cap for a timezone — by design to distinguish "uncapped" from "zero-limit"

## External Integrations
- **Redis:** Response cached until next 5th minute boundary per unique parameter set
- **Platform Service:** Provides timezone and course duration mappings (intra-cluster, cached)

## Internal Service Dependencies
- `demo_availability` and `demo_availability_slot_limits` tables for cap configuration
- `master_combinations` + `demo_booking_predictions` for real-time booking counts

## Database Operations

### Tables Accessed

**`demo_availability`:**
| Column | Notes |
|--------|-------|
| id | PK |
| cdm_id | Course Duration Mapping ID |
| tz_id | Timezone ID |
| start_time | UTC slot start boundary |
| end_time | UTC slot end boundary |
| day_limit | Max bookings per day (default 750) |

**`demo_availability_slot_limits`:**
| Column | Notes |
|--------|-------|
| daId | FK → demo_availability |
| startSlot | UTC |
| endSlot | UTC |
| enabled | 1/0 — whether slot is displayed |
| limit | Per-slot cap (undefined = no per-slot cap) |

### SQL / ORM Queries
- SELECT `demo_availability` WHERE `cdm_id` AND `tz_id`
- JOIN `MasterCombinations` + `DemoBookingPredictions` to aggregate bookings per slot per country group
- SUM bookings per UTC day for day limit check
- Compare individual slot booking count vs. `demo_availability_slot_limits.limit`

### Transactions
N/A — Read-only at query time.

## Performance Analysis

### Good Practices
- Two-tier capping (day + slot) prevents both bulk flooding and individual slot abuse
- Redis cache reduces repeated DB joins during high-traffic periods
- `enabled` flag on slot limits allows operations to disable specific slots without deleting records

### Performance Concerns
- During the 5-minute Redis cache window, a slot can be overbooked by up to 1–2 bookings (accepted trade-off for performance)
- Large country groups with many combinations may increase `DemoBookingPredictions` JOIN complexity

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | `limit = undefined` as a "no cap" signal is non-standard — recommend an explicit `is_capped` boolean column instead |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add composite index on `demo_availability_slot_limits(daId, startSlot)` for fast slot-level lookups
- Shorten Redis TTL to 2 minutes for peak-demand timeslots to reduce overbooking window

### Month 1 (Architectural)
- Implement booking-write-time cache invalidation in Redis to immediately reflect new bookings
- Add real-time cap breach alerting via SNS when a slot reaches 90% capacity

## Test Scenarios

### Functional Tests
- Day limit reached → all slots on that UTC day return `available = false`
- Day limit not reached, slot limit reached → only that slot returns `available = false`
- `limit = undefined` for a slot → slot-level check is skipped, only day limit applies
- `enabled = 0` on a slot → slot not displayed at all
- Expired slots are excluded from response

### Performance & Security Tests
- Cache hit verification: identical request within 5-minute window returns cached response
- Load test: 1000 simultaneous booking slot requests during peak hour

### Edge Cases
- `dayLimit = 0` (should all slots be unavailable?)
- Booking created exactly at the cache boundary (race condition)
- All slots disabled (`enabled = 0`) for a timezone

## Async Jobs & Automation
- **Add Or Update Demo Availability Script:** Manages baseline `demo_availability` configuration — creates records for all timezone × course combinations with `day_limit = 750` and 8 AM–10 PM UTC boundaries. Runs approximately 3360 queries per execution.
