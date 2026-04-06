---
title: Get Deal Owner
category: technical-architecture
subcategory: crm-and-sales
source_id: ef79f78b
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Get Deal Owner

## Overview
The Get Deal Owner flow identifies the Sales Manager who owns a CRM deal and returns their email. It supports bulk lookups by `bookingUUID` or `studentId + courseId` and is used primarily by Tryouts service during student/teacher/referral booking flows to assign SM emails to bookings.

## API Contract
**Endpoint:** `POST /deals/owner`
- **Auth:** Internal service-to-service (no public auth documented)
- **Request Body:**
```json
{
  "deals": [
    {
      "bookingUUID": "string"
    },
    {
      "studentId": "string",
      "courseId": "string"
    }
  ]
}
```
(Each item can use either `bookingUUID` OR the `studentId`+`courseId` combination)

**Response:**
```json
[
  {
    "studentId": "string",
    "courseName": "string",
    "bookingUUID": "string",
    "employeeEmail": "string"
  }
]
```

**Internal Dependency Endpoint:**
`POST /admin/employees` (Prashashak) — fetches employee details by list of `user_id` values

## Logic Flow

### Controller Layer
- Receive bulk `POST /deals/owner` request
- Delegate to `DBCRMDeal` service → `getDealOwner` function
- Return array of `{ studentId, courseName, bookingUUID, employeeEmail }` mappings

### Service/Facade Layer
1. **`getDealOwner` called by `DBCRMDeal` service**
2. **Fetch Course Data:** Call Platform service to retrieve course mappings (MongoDB stores course names, not IDs → need name-to-ID conversion)
3. **Fetch Deals:** Query `db_crm_deals` by `bookingUUID` or `studentId`+`courseId` combinations
4. **Aggregate Owner IDs:** Collect all `deal_owner_id` values from fetched deals
5. **Resolve User IDs:** Query `crm_users` SQL table → map `owner_id` to `user_id`
6. **Fetch Employee Emails:** Send array of `user_id` to `POST /admin/employees` (Prashashak)
7. **Build Response:** Map employee emails back to respective `owner_id` → build response array with `studentId`, `courseName`, `bookingUUID`, `employeeEmail`

**Standard Deal Allocation (Non-Hotlead):**
For standard (non-hotlead) round-robin assignments when demo is marked successful:
1. Lambda fetches student attributes
2. Match against `master_group_filters` table with weighted priority:
   - `channel` (11), `courseId` (4), `countryId` — geography (3), `languageId` (2), `utmSource` (1)
   - `null` values act as wildcards
3. Find SM in matched group with `deals_alloted < max_deals`
4. Assign deal to that SM

### High-Level Design (HLD)
```
POST /deals/owner (bulk)
  → getDealOwner()
      → Platform service: course name → ID mapping
      → db_crm_deals query (by bookingUUID or studentId+courseId)
      → crm_users SQL: owner_id → user_id
      → POST /admin/employees (Prashashak): user_id → email
      → Build and return response array

[Standard Allocation — post demo success]
  → Lambda
      → master_group_filters lookup (channel, course, country, language, utmSource)
      → group_user_mappings: find SM with deals_alloted < max_deals
      → Assign + increment deals_alloted
```

## External Integrations
- N/A — all internal service calls

## Internal Service Dependencies
- **Prabandhan:** `db_crm_deals` (NoSQL), `crm_users` (SQL), `master_group_filters`, `group_user_mappings`, `groups`
- **Prashashak:** `POST /admin/employees` — employee email lookup
- **Platform:** Course name-to-ID mapping from `master_courses`

## Database Operations

### Tables Accessed
- **Prabandhan NoSQL:** `db_crm_deals` — deal lookup by bookingUUID or studentId/courseId
- **Prabandhan SQL:**
  - `crm_users` — maps owner_id to user_id
  - `master_group_filters` — routing rules by channel, course, country, language, utm
  - `group_user_mappings` — SM capacity (deals_alloted, max_deals)
  - `groups` — group definitions
  - `group_filter_mappings` — filter-to-group associations
- **Prashashak SQL:** `employees` — email addresses
- **Platform SQL:** `master_courses` — course name/ID mapping

### SQL / ORM Queries
- `db_crm_deals.find({ bookingUUID: { $in: [...] } })`
- SELECT `crm_users` WHERE `owner_id IN (?)`
- SELECT `master_group_filters` WHERE (channel, courseId, countryId, languageId, utmSource) — weighted priority match
- SELECT `group_user_mappings` WHERE `group_id = ? AND deals_alloted < max_deals` LIMIT 1
- UPDATE `group_user_mappings` SET `deals_alloted = deals_alloted + 1`

### Transactions
- `deals_alloted` increment should be atomic to prevent double-assignment under concurrent requests

## Performance Analysis

### Good Practices
- Bulk endpoint design avoids N+1 calls for multi-booking scenarios
- Weighted filter priority (channel > course > country > language > utm) provides deterministic routing
- `null` wildcard in filter fields provides flexible matching without combinatorial explosion

### Performance Concerns
- Sequential chain: Platform → `db_crm_deals` → `crm_users` → Prashashak — no parallel execution
- `master_group_filters` matching logic may require full table scan if not properly indexed
- `deals_alloted` increment without distributed lock could cause double-assignment under concurrent lambda execution

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | `deals_alloted` increment lacks distributed lock — race condition in concurrent deal allocation |
| Medium | Sequential API calls (Platform → CRM → Prashashak) — parallelizable |
| Low | MongoDB stores course names not IDs — requires extra Platform API call per bulk request |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add database-level atomic increment on `group_user_mappings.deals_alloted` (using SELECT FOR UPDATE)
- Cache Platform course mappings (TTL: 1 hour) to eliminate repeated calls

### Month 1 (Architectural)
- Parallelize Platform and `db_crm_deals` fetches at start of `getDealOwner`
- Store course IDs in `db_crm_deals` to eliminate Platform dependency

## Test Scenarios

### Functional Tests
- Single `bookingUUID` → correct SM email returned
- Bulk request (10 deals) → all emails returned correctly
- `studentId + courseId` lookup → correct deal and SM found
- Round-robin: SM at `max_deals` → skipped, next available SM assigned

### Performance & Security Tests
- Concurrent deal allocation: two Lambdas assign same deal simultaneously → only one SM assigned
- Bulk request with 100 bookingUUIDs — response time benchmark

### Edge Cases
- No deal found for `bookingUUID` → null/empty entry in response array
- All SMs in group at `max_deals` → fallback behavior
- Course name not in Platform `master_courses` → mapping failure
