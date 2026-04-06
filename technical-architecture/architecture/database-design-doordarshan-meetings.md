---
title: Database Design — Doordarshan (Meetings Service)
category: technical-architecture
subcategory: architecture
source_id: 916b0952-ff0b-483a-b0b6-8ee832f924c1
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Database Design — Doordarshan (Meetings Service)

## Overview
This document covers the database schema for the Doordarshan meetings service, specifically the four core tables that manage Zoom token lifecycle, license allocation, meeting state, and meeting event tracking for BrightCHAMPS class sessions.

## API Contract
N/A — This is a schema reference document, not an API specification.

## Logic Flow
### Controller Layer
N/A — This is a data model reference document.

### Service/Facade Layer
The Doordarshan service uses these tables to manage Zoom integrations: tokens are fetched and refreshed using `zoom_tokens`, available licenses are assigned via `zoom_licences`, meeting records are persisted in `meetings`, and lifecycle events are tracked in `meeting_events`.

### High-Level Design (HLD)
1. A meeting request arrives → system checks `zoom_licences` for an available license with `active=true` and `in_use=false`
2. License is reserved (`in_use=true`, `meeting_count` incremented)
3. Meeting record created in `meetings` with host and participant links
4. During the meeting lifecycle, events (join, leave, end) are appended to `meeting_events`
5. After meeting ends, license is released

## External Integrations
- **Zoom** — Provides the underlying meeting infrastructure; access/refresh tokens stored in `zoom_tokens`

## Internal Service Dependencies
- Doordarshan → Paathshala (meeting IDs referenced in class records)
- Doordarshan → Eklavya/Dronacharya (for student/teacher meeting links)

## Database Operations
### Tables Accessed

**zoom_tokens**
| Column | Description |
|--------|-------------|
| id | Primary key |
| type | Token type identifier |
| access_token | Current Zoom access token |
| refresh_token | Token used for rotation |
| created_at | Record creation timestamp |
| updated_at | Last updated timestamp |

**zoom_licences**
| Column | Description |
|--------|-------------|
| id | Primary key |
| licence_id | Zoom license identifier |
| email | License-associated email |
| active | Boolean: is license active |
| priority | Allocation priority order |
| in_use | Boolean: currently assigned to a meeting |
| meeting_count | Number of meetings hosted |

**meetings**
| Column | Description |
|--------|-------------|
| id | Primary key |
| type | Meeting type |
| vendor | Meeting vendor (e.g., Zoom) |
| vendor_id | External vendor meeting ID |
| licence_id | FK to zoom_licences |
| host_link | URL for host to join |
| participant_link | URL with encrypted password for participants |
| start_at | Scheduled start time |
| end_at | Scheduled end time |
| status | ENUM: waiting, scheduled, live, overflow, ended, terminated |
| alternate_host | Backup host assignment |

**meeting_events**
| Column | Description |
|--------|-------------|
| id | Primary key |
| meeting_id | FK to meetings |
| event_type | Type of lifecycle event |
| event_data | JSON payload of event data |

### SQL / ORM Queries
- License availability check: `SELECT * FROM zoom_licences WHERE active=true AND in_use=false ORDER BY priority ASC LIMIT 1`
- Meeting status transitions: UPDATE meetings SET status = :newStatus WHERE id = :meetingId
- Event logging: INSERT INTO meeting_events (meeting_id, event_type, event_data) VALUES (...)

### Transactions
- License reservation and meeting creation should be wrapped in a transaction to prevent double-allocation of a license

## Performance Analysis
### Good Practices
- `priority` column on `zoom_licences` allows deterministic, ordered license selection
- Separate `meeting_events` table keeps the `meetings` table lean and avoids JSON blob sprawl
- ENUM status field enforces valid state transitions at the DB level

### Performance Concerns
- No explicit index documentation provided — `meetings.status` and `meetings.start_at` should be indexed for frequent query patterns
- `meeting_count` on licenses may cause contention under high concurrent booking loads (needs atomic increment)
- `in_use` boolean flag without a TTL could leave licenses locked if a meeting creation fails mid-transaction

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | `in_use` flag without timeout/TTL risks permanent license lockout on failure |
| Medium | No index strategy documented for `meetings` table despite high query volume |
| Low | Token rotation logic not reflected in schema (no `expires_at` column on zoom_tokens) |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Add `expires_at` column to `zoom_tokens` to support proactive token refresh before expiry
- Add database indexes on `meetings.status`, `meetings.start_at`, and `zoom_licences.in_use`

### Month 1 (Architectural)
- Implement a license watchdog job to release licenses stuck in `in_use=true` for more than N minutes with no active meeting
- Evaluate Redis-based distributed locking for license reservation to handle concurrent booking spikes

## Test Scenarios
### Functional Tests
- License is correctly reserved and released before and after a meeting
- Meeting status transitions follow the valid ENUM sequence (waiting → scheduled → live → ended/terminated)
- Token refresh correctly updates both access_token and updated_at

### Performance & Security Tests
- Concurrent meeting booking load test to verify no license double-allocation
- Verify access_token is not exposed in API responses or logs

### Edge Cases
- What happens if Zoom returns an error after license is reserved but before meeting is created?
- What is the behavior when all licenses are `in_use` simultaneously?

## Async Jobs & ETL
- Token refresh should be handled by a background job that checks `zoom_tokens.updated_at` against token expiry window
