---
title: Teacher Demo Availability and Confirmations
category: technical-architecture
subcategory: teacher-management
source_id: c634566d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Teacher Demo Availability and Confirmations

## Overview
The Auxo system is a predictive engine and real-time mapping service that manages demo class slots, forecasts teacher demand using historical joining rates, enables teachers to mark their availability, and automatically confirms teachers for upcoming demo classes. It uses color-coded dashboards, conversion-rate-based ranking, and automated cron pipelines to ensure optimal teacher coverage.

## API Contract

### GET /teacher/demo/avaialbility (Teacher Service)
- **Purpose:** Fetch teachers who have already marked themselves as available
- **Response:**
```json
[{ "startTime": "string", "comb_id": int, "confirmed": false }]
```

### GET /tryouts/v1/teacherDemoConfirmations/startTime/:startTime
- **Auth:** Internal
- **Query Params:** `endTime`
- **Purpose:** Fetch all teacher demo confirmations in a time window

### GET /v1/demo/operations/eligible-teachers
- **Query Params:** `demoClassId`
- **Purpose:** Fetch available teachers eligible for a specific demo class

### POST /v1/demo/operations/add/teacher
- **Auth:** Admin JWT
- **Request Body:**
```json
{
  "adminId": 12345,
  "operation": "teacher_addition",
  "demoClassId": 5,
  "payload": { "teacherAvailabilityId": 24 }
}
```
- **Purpose:** Manually confirms a teacher for a demo class; updates `teacher_confirmation_id`

### POST /v1/demo/operations/remove/teacher
- **Auth:** Admin JWT
- **Purpose:** Removes a teacher from a class by setting their confirmation ID to null

## Logic Flow

### Controller Layer
Endpoints route through operations controller in the Tryouts service.

### Service/Facade Layer
**Teacher Availability Interface:**
1. Teacher submits configuration: supported countries, languages, and grades
2. System creates all possible permutations and maps them against `demo_booking_predictions`
3. Dashboard renders color-coded cards:
   - Grey: Full (availability > 80% or 0 total leads)
   - White: Available (availability 40–80%)
   - Orange: Deficit (availability < 40%)
   - Blue: Teacher already marked availability
   - Green: Teacher has confirmed demo
   - Red: Teacher has a conflicting paid class
   - Black: Teacher is on leave
4. If available teachers exceed required, rank by conversion rate and select top performers

**Confirmation Selection Logic:**
- Confirm 30% of permutations plus a 10% buffer
- Emit confirmation event to Teacher Service to update `teacher_avaialbility.confirmed = true`

### High-Level Design (HLD)
- Tryouts service owns the Auxo prediction and confirmation domain
- Teacher Service (Dronacharya) and Meeting Service (Doordarshan) integrate for schedule sync and Zoom link creation
- Redis caches `/v1/demoAvailability` responses until every 5th minute
- FIFO processing of availability marking → ranking → confirmation

## External Integrations
- **Redis:** Caches availability limits per query parameter set until the next 5-minute boundary
- **Platform Microservice:** `/v1/mappings/timezones` and `/v1/mappings/courses` for country/timezone/course data
- **Teacher Service (Dronacharya):** Syncs teacher schedules and receives confirmation events
- **Meeting Service (Doordarshan):** Spins up Zoom meeting links for confirmed demo classes

## Internal Service Dependencies
- `Tryouts` service owns prediction, availability, and confirmation tables
- `Dronacharya` (Teacher Service) is called to update `teacher_avaialbility.confirmed`
- `demo_booking_predictions` table joins with `master_combinations` for per-slot counts

## Database Operations

### Tables Accessed

**`demo_availability`:**
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| cdm_id | int | Course Duration Mapping ID |
| tz_id | int | Timezone ID |
| start_time | datetime | UTC |
| end_time | datetime | UTC |
| day_limit | int | Max bookings per day |

**`demo_availability_slot_limits`:**
| Column | Type | Notes |
|--------|------|-------|
| daId | int | FK → demo_availability |
| startSlot | datetime | UTC |
| endSlot | datetime | UTC |
| enabled | tinyint | 1/0 |
| limit | int | Max bookings per slot |

**`combination_joining_rates`:**
| Column | Type |
|--------|------|
| joining_rate | float |

**`demo_booking_predictions`:**
| Column | Type | Notes |
|--------|------|-------|
| total_leads | int | From tryouts.bookings |
| filtered_leads | int | Excluding cancelled/unqualified |
| predicted_leads | int | Teachers to confirm |
| teacher_predicted_leads | int | Teachers to request availability from |
| teacher_availity_marked | int | Count who marked availability |
| teacher_confirmed | int | Count confirmed |

**`teacher_avaialbility` / `teacher_demo_availabilities`:**
| Column | Type |
|--------|------|
| startTime | datetime |
| teacherid | int |
| combId | int |
| confirmed | boolean |

**`teacher_demo_confirmations`:** Tracks finalized teacher-to-slot assignments

**`demo_classes`:** Maps `booking_id` → `teacher_confirmation_id`

### SQL / ORM Queries
- JOIN `master_combinations` + `demo_booking_predictions` to get per-slot booked lead counts
- SELECT with ranking by conversion rate when selecting teachers for confirmation
- UPSERT on `demo_booking_predictions` per (combination_id, datetime)

### Transactions
- Teacher confirmation updates `teacher_confirmation_id` atomically

## Performance Analysis

### Good Practices
- Redis caching of availability endpoint reduces DB load during high-traffic landing page access
- Weighted average prediction with 4-week history smooths out anomalies
- 30% buffer in `teacher_predicted_leads` prevents slot coverage gaps

### Performance Concerns
- 30-minute cron for joining rate collection may lag in reflecting real-time demand spikes
- Permutation generation for teacher availability could scale poorly with many country/language/grade combinations

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | Typo in table/column names: `teacher_avaialbility` (misspelled in source) |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Standardize column name spelling (`teacher_availability` vs `teacher_avaialbility`) in code and schema
- Add Redis TTL invalidation hooks when availability is manually updated via operations API

### Month 1 (Architectural)
- Expand weighted average prediction model to account for holiday calendars and seasonal demand shifts
- Build a real-time deficit alert to notify ops when `teacher_availity_marked < predicted_leads` by a threshold

## Test Scenarios

### Functional Tests
- Teacher marks availability and appears in correct color bucket on dashboard
- Cron at 17th minute correctly selects and trims to top-ranked available teachers
- Confirmation cron at 30-min intervals confirms correct number for 1h/3h/6h windows
- Manual add/remove teacher via operations API updates `demo_classes` correctly

### Performance & Security Tests
- Simulate 1000 concurrent availability marks and verify Redis lock prevents duplicates
- Verify admin-only access to operations endpoints

### Edge Cases
- All available teachers exceed required count (ranking + trimming logic)
- Zero `total_leads` for a slot (should show Grey)
- Confirmation cron triggered when no teachers have marked availability

## Async Jobs & Automation
- **Every 30 minutes:** Fetch actual joining rates of previous 30-min and 60-min classes → store in `combination_joining_rates`
- **Every 15 minutes:** Run joining rate predictions per combination ID for next 3 days → update `demo_booking_predictions`
- **At the 17th minute:** Process and mark teacher availability; rank and trim if excess
- **Every half hour:** Confirm teachers for upcoming 1h, 3h, and 6h slots (30% of permutations + 10% buffer); emit confirmation event to Teacher Service
