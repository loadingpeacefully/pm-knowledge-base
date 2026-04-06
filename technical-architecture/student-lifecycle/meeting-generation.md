---
title: Meeting Generation
category: technical-architecture
subcategory: student-lifecycle
source_id: f40149a1
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Meeting Generation

## Overview
The Meeting Generation system, owned by the Doordarshan microservice, manages Zoom license allocation and meeting link generation for all class types (demo and paid). It uses a multi-step license optimization algorithm to reuse expiring licenses before falling back to vendor API calls, and tracks real-time participant join/leave events to calculate class duration.

## API Contract

### GET /meetings/:id
- **Auth:** Internal
- **Purpose:** Fetch details of a specific meeting
- **Response:** Meeting object from `meetings` table

### POST /meetings
- **Auth:** Internal
- **Purpose:** Generate new meeting links
- **Request Body:**
```json
{
  "type": "demo",
  "count": 10,
  "time": "2023-02-10T00:00:00.000Z",
  "duration": 30
}
```
- **Response:** Generated meeting objects with `host_link` and `participant_link`

## Logic Flow

### Controller Layer
`POST /meetings` → MeetingController → `GenerateMeetings(TYPE, START_TIME, DURATION, COUNT)`

### Service/Facade Layer

**`GenerateMeetings(TYPE, START_TIME, DURATION, COUNT)` Algorithm:**

1. **Step 1: Check Unused Licenses (UL)**
   - Query for licenses where `in_use = 0`
   - If `COUNT <= UL` → allocate these licenses and proceed to link generation
   - If `COUNT > UL` → fill available UL, calculate `RM = COUNT - UL`

2. **Step 2: Check Free-able Licenses (FL)**
   - Find licenses where `END_TIME = START_TIME` (licenses whose current meeting ends exactly when new meeting starts — can be reused)
   - Allocate FL licenses up to `RM`
   - If `RM > LEN(FL)` → proceed to vendor fallback

3. **Step 3: Vendor Fallback**
   - Raise license shortfall alarm
   - Call `VendorFallback(START_TIME, DURATION, COUNT = remaining RM)`
   - Create new Zoom meetings via vendor API

4. **Step 4: Link Creation / Pool Dequeueing — `Generate()` function**
   - Check if a pool of pre-generated links exists
   - If pool available → dequeue a link and apply settings via Zoom API
   - If pool empty → make fresh Zoom API call to create a new link

5. **Step 5: Occupy Licenses — `OccupyLicenses()`**
   - UPDATE `zoom_licences`:
     - Set `occupied_time = START_TIME`
     - Set `release_time = START_TIME + DURATION`
     - Set `in_use = 1`

**Zoom Event Processing:**
- `meeting.participant_joined` webhook → set `joinStatus = 1`; log `join_time`
- `meeting.participant_left` webhook → set `joinStatus = 0`; record `end_time`; calculate: `duration = duration + (end_time - lastJoin)`

### High-Level Design (HLD)
- Doordarshan microservice owns all meeting and license management
- License optimization: unused → free-able → new vendor call
- Pre-generated link pool reduces Zoom API call latency
- Real-time participant tracking via Zoom webhooks
- Background cron scripts on server 172.31.9.208 for routine Zoom maintenance

## External Integrations
- **Zoom API:** Meeting creation, license management, `UpdateZoomCommand.php` for link refresh
- **Zoom Webhooks:** `meeting.participant_joined` and `meeting.participant_left` events for real-time tracking

## Internal Service Dependencies
- Paathshala (Class Service): Calls `POST /meetings` to generate links for new demo/paid classes
- Teacher Service (Dronacharya): May use meeting links for confirmed demo slots
- `meetings` table join with `zoom_licences` for license-to-meeting mapping

## Database Operations

### Tables Accessed

**`zoom_tokens`:**
| Column |
|--------|
| id, access_token, refresh_token, created_at, updated_at |

**`zoom_licences`:**
| Column | Notes |
|--------|-------|
| id | PK |
| email | Zoom license email |
| active | boolean |
| priority | Allocation priority |
| in_use | 0/1 |
| meeting_count | Total meetings on this license |

**`meetings`:**
| Column | Notes |
|--------|-------|
| id | PK |
| type | demo, paid, etc. |
| vendor | zoom |
| vendor_id | Zoom meeting ID |
| licence_id | FK → zoom_licences |
| host_link | Teacher URL |
| participant_link | Student URL |
| start_at, end_at | datetime |
| alternate_host | |
| status | ENUM: waiting, scheduled, live, overflow, ended, terminated |

**`meeting_events`:**
| Column |
|--------|
| id, meeting_id, event_type, event_data |

### SQL / ORM Queries
- SELECT `zoom_licences` WHERE `in_use = 0` for unused license check
- SELECT `zoom_licences` WHERE `release_time = :start_time` for free-able license check
- UPDATE `zoom_licences` SET `occupied_time`, `release_time`, `in_use = 1` on allocation
- INSERT into `meetings` for each generated meeting
- INSERT into `meeting_events` on participant join/leave
- UPDATE `meeting_events` duration on participant leave

### Transactions
- License allocation + meeting creation wrapped in a transaction to prevent double-allocation

## Performance Analysis

### Good Practices
- Free-able license reuse minimizes new Zoom API calls (cost and latency)
- Pre-generated link pool further reduces Zoom API round trips
- Separate `meeting_events` audit table provides full join/leave history without bloating `meetings` table

### Performance Concerns
- PHP cron scripts on server 172.31.9.208 introduce a non-standard technology dependency
- Vendor fallback path adds unpredictable latency from Zoom API

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | PHP cron scripts (`UpdateZoomCommand.php`) run on a specific server (172.31.9.208) — not containerized, creates infrastructure dependency |
| Medium | License shortfall alarm mechanism not detailed — unclear if ops are notified in real time |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Migrate PHP cron scripts to Lambda or containerized Node.js tasks
- Add real-time alerting when `VendorFallback` is triggered (license shortfall)

### Month 1 (Architectural)
- Pre-warm the link pool for known upcoming class slots (e.g., generate links 30 minutes before class time)
- Implement license capacity planning based on predicted class load from Auxo forecasts

## Test Scenarios

### Functional Tests
- `POST /meetings` with COUNT ≤ UL → links generated using only unused licenses
- `POST /meetings` with COUNT > UL but COUNT ≤ UL + FL → free-able licenses used
- `POST /meetings` with COUNT > UL + FL → VendorFallback triggered
- Zoom participant join → `join_time` recorded
- Zoom participant leave → `duration` calculated correctly

### Performance & Security Tests
- Verify license allocation transaction prevents double-allocation under concurrent requests
- Benchmark `GenerateMeetings` with COUNT = 100 at peak hour

### Edge Cases
- No unused or free-able licenses at a peak slot → VendorFallback handles full count
- Participant joins and leaves multiple times → cumulative duration calculated correctly
- Pre-generated link pool empty → fresh Zoom API call fallback works

## Async Jobs & Automation
- **`UpdateZoomCommand.php` (PHP Cron, daily at 23:00 on server 172.31.9.208):** Refreshes/updates Zoom meeting links
- **Zoom Deactivation Cron (PHP, daily at 03:00):** Deactivates Zoom licenses or capabilities appropriately
- **Zoom Webhook Processor:** Handles `meeting.participant_joined` and `meeting.participant_left` events for real-time duration tracking
