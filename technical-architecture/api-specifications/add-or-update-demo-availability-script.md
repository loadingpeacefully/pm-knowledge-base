---
title: Add Or Update Demo Availability Script
category: technical-architecture
subcategory: api-specifications
source_id: 74435045-7c39-4180-aa15-a2445eacec5f
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Add Or Update Demo Availability Script

## Overview
This is a one-time (or re-runnable) script that populates or refreshes the `demo_availability` table in the Tryouts database. It ensures that for every timezone and every course, demo slots from 8 AM to 10 PM (local time) are available, with each slot aligned to the nearest `00` minute boundary in IST. The script reads from Platform API endpoints for timezones and course-duration mappings, then upserts records into `demo_availability` with a default day limit of 750.

## API Contract

| Property | Value |
|----------|-------|
| Method | Internal Script (not an HTTP endpoint) |
| Path | N/A — Script invokes: `GET /v1/mappings/timezones`, `GET /v1/mappings/:name` (name=course_duration_mappings), `createOrUpdateDemoAvailability()` |
| Auth | Internal (Platform API key) |
| Content-Type | application/json |

**Platform APIs consumed:**
```
GET /v1/mappings/timezones           → all timezone records
GET /v1/mappings/course_duration_mappings → all course-duration mapping records
```

**Internal upsert function:**
```
createOrUpdateDemoAvailability(tzId, cdmId, startTime, endTime, dayLimit)
```

**Sample slot verification endpoint (for testing):**
```
GET /v1/demoAvailability?courseId=1&ip=36.255.84.94&days=3&type=3&utcDifference=330  (India)
GET /v1/demoAvailability?courseId=8&days=3&type=3&shortCode=MO                        (Macau)
GET /v1/demoAvailability?courseId=8&days=3&type=3&shortCode=US&tzId=20               (US)
```

## Logic Flow

### Controller Layer
- N/A — This is a standalone script, not an HTTP-routed endpoint.

### Service/Facade Layer
1. Fetch all timezones via `GET /v1/mappings/timezones`.
2. Fetch all course-duration mappings via `GET /v1/mappings/course_duration_mappings`.
3. Extract all `cdmId` values (course-duration mapping IDs).
4. Nested loop:
   ```javascript
   for (let timezone of timezones) {
     for (let cdmId of cdmIds) {
       createOrUpdateDemoAvailability()
     }
   }
   ```
5. For each (timezone, cdmId) pair:
   - Convert 8 AM local time to UTC. If UTC minutes ≠ 00, add 30 minutes to align.
   - Convert 10 PM local time to UTC for end time.
   - If `demo_availability` record does not exist for this (cdmId, tzId) pair: INSERT with default `day_limit = 750`.
   - If record exists: UPDATE `start_time`, `end_time`, and `day_limit`.
6. Per-slot limit handling: if a per-slot limit is not defined, set `limit = undefined` (not `0`) to skip per-slot capping in the availability check.

### High-Level Design (HLD)
- Slot alignment rule: every timezone's first slot must start at `00` minutes in IST. This means that if local 8 AM converts to a non-round UTC minute, the start time is bumped to the next 30-minute UTC boundary.
- Default day limit: 750 bookings per day across all slots.
- Per-slot limits are managed separately in `demo_availability_slot_limits` table (not managed by this script directly).
- Total script runtime: ~4 minutes for first run, ~3 min 49 sec on subsequent runs (~3360 total queries).

## External Integrations
- **Platform Service API** — `GET /v1/mappings/timezones` and `GET /v1/mappings/course_duration_mappings` to seed the script's input data.

## Internal Service Dependencies
- **Tryouts DB** — `demo_availability` table is the target.
- **Platform Service** — Source of timezone and course-duration data.

## Database Operations

### Tables Accessed
**Tryouts:**
- `demo_availability` — SELECT, INSERT, UPDATE

### SQL / ORM Queries
```sql
-- Check if record exists
SELECT `id`, `cdm_id`, `tz_id`, `start_time`, `end_time`, `day_limit`,
       `created_at`, `updated_at`
FROM `demo_availability` AS `DemoAvailability`
WHERE `DemoAvailability`.`cdm_id` = 8 AND `DemoAvailability`.`tz_id` = 210
LIMIT 1;

-- Insert if not exists
INSERT INTO `demo_availability`
  (`id`, `cdm_id`, `tz_id`, `start_time`, `end_time`, `day_limit`, `created_at`, `updated_at`)
VALUES
  (DEFAULT, 8, 210, '06:30:00', '20:00:00', 750, ?, ?);

-- Update if exists
UPDATE `demo_availability`
SET `start_time` = '06:30:00', `end_time` = '20:00:00', `day_limit` = 750, `updated_at` = ?
WHERE `cdm_id` = 8 AND `tz_id` = 210;
```

**Total queries:** ~3360 (one SELECT + one INSERT or UPDATE per timezone-cdm combination).

### Transactions
- N/A — Script runs individual upserts per (timezone, cdmId) pair without explicit transactions.

## Performance Analysis

### Good Practices
- Script is idempotent — safe to re-run; existing records are updated, not duplicated.
- First run vs. subsequent runs are both completed in under 5 minutes for ~3360 queries.
- Per-slot limit of `undefined` (vs `0`) correctly bypasses per-slot checks without disabling the feature entirely.

### Performance Concerns
- ~3360 sequential queries without batching — no bulk insert/update optimization.
- Each (timezone, cdmId) pair makes a SELECT before INSERT/UPDATE — could be replaced with an `INSERT ... ON DUPLICATE KEY UPDATE` or `UPSERT` to halve the query count.

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No bulk upsert — ~3360 individual queries could be ~1680 with INSERT ON DUPLICATE KEY UPDATE. |
| Low | Script runtime (~4 min) is acceptable for a maintenance script but would be slow if run frequently; no scheduling mechanism documented. |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Replace SELECT + INSERT/UPDATE pairs with `INSERT INTO ... ON DUPLICATE KEY UPDATE` to reduce total query count by ~50%.

### Month 1 (Architectural)
- Build a scheduled admin API endpoint to trigger demo availability refresh without direct DB access.
- Add validation: warn if calculated `start_time` is later than `end_time` for any timezone (edge case for UTC+12+ zones).

## Test Scenarios

### Functional Tests
- Run script for India (IST) → verify slot at 8 AM IST = UTC 02:30, available: true.
- Run script for Macau (UTC+8) → verify slots start at 08:30 local.
- Run script for US (UTC-5, tzId=20) → verify correct UTC conversion for US Eastern timezone.
- Re-run script → verify existing records are updated, not duplicated.

### Performance & Security Tests
- Script requires Platform API access — verify API key is not embedded in script source.
- Time the full run with current timezone × cdm count to establish baseline (~3360 queries, ~4 min).

### Edge Cases
- Timezone where 8 AM local = UTC time with non-zero minutes → verify 30-minute alignment rule applied.
- Course-duration mapping with zero or null duration → verify script handles gracefully.
- `day_limit` override: verify passing `undefined` as per-slot limit does not write `0` to DB.

## Async Jobs & Automation
- N/A — This is a manual/maintenance script. No EventBridge, Lambda, or SQS automation documented.
- Intended to be run by ops/engineers when timezone or course-duration data changes.
