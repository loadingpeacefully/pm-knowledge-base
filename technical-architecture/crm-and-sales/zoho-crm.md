---
title: Zoho – Customer Relationship Management (CRM)
category: technical-architecture
subcategory: crm-and-sales
source_id: 1132d811
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Zoho – Customer Relationship Management (CRM)

## Overview
Prabandhan is the internal CRM microservice that bridges all BrightChamps systems to Zoho CRM. It manages OAuth token lifecycle (1-hour TTL, NoSQL-cached), provides upsert/CRUD operations across Leads, Deals, Notes, and Tasks modules, and handles bidirectional sync including Zoho webhook callbacks for user creation/update events.

## API Contract
**Zoho API Base URL:** `https://www.zohoapis.in/crm/v2/`

**Authentication:**
```
Authorization: Zoho-oauthtoken {access_token}
```
- Token generation uses: `ZOHO_REFRESH_TOKEN`, `ZOHO_CLIENT_ID`, `ZOHO_GRANT_TYPE`, `ZOHO_CLIENT_SECRET`
- Token cached in NoSQL database, 1-hour TTL

**Key Zoho API Operations:**

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Upsert Lead | POST | `/crm/v2/leads/upsert` |
| Convert Lead to Deal | POST | `/crm/v2/Leads/{leadId}/actions/convert` |
| Upsert Deal | POST | `/crm/v2/deals/upsert` |
| Add Notes to Deal | POST | `/crm/v2/deals/{dealId}/Notes` |
| Create Task | POST | `/crm/v2/Tasks` (via `zoho.crm.createRecord`) |
| Update Task | PUT | `/crm/v2/Tasks/{taskId}` |
| Search Records | GET | `/crm/v2/{module}/search` |

**Duplicate Check:** `duplicate_check_fields: ['booking_uuid']` for leads

## Logic Flow

### Controller Layer
- Prabandhan service acts as the sole CRM gateway — no other microservice calls Zoho directly
- All Zoho operations routed through Prabandhan's Zoho integration layer

### Service/Facade Layer
**OAuth Token Management:**
1. Any Zoho API call triggers token check
2. `fetchToken()`:
   a. Read from NoSQL cache
   b. IF expired or missing → `POST Zoho OAuth endpoint` with refresh token + client credentials
   c. Store new token in NoSQL with expiry timestamp
   d. Return token
3. Inject token into `Authorization: Zoho-oauthtoken {token}` header

**Module Operations:**

**Leads:**
- Created on booking confirmation (`/lead/create-db-crm-lead`)
- Initial `Lead_Status = "Not Contacted"`
- Stored in Zoho + Prabandhan `crm_lead` (NoSQL)
- Once converted to deal → removed from Zoho Leads, retained in NoSQL

**Deals:**
- Created by converting lead via `/Leads/{leadId}/actions/convert`
- Default stage: `Demo Completed`
- Stored in Zoho + Prabandhan `db_crm_deals` (NoSQL)
- Stage progression: `Demo Completed` → `Closed Won` (on first payment)
- Renewal stages: `Renewal Pending` → `Closed Won – Sales` / `Closed Lost`

**Notes:**
- Added via `POST /crm/v2/deals/{dealId}/Notes`
- Auto-added on deal creation: WhatsApp link + Dashboard link
- Manually triggered via `/deal/add-notes-in-crm-deal`
- Key-value pairs transformed to `{ Note_Title, Note_Content }` format

**Tasks:**
- Created via `zoho.crm.createRecord("Tasks", payload)`
- Types: First Connect, PQS Review (TL), Join Trial Class, First Task Creation
- Automated closure based on activity tracking subform or status updates
- Expiry: varies by type (4 hours / 2 days)

**Bidirectional Sync:**
- Zoho webhook → Prabandhan: SM user creation/update events sync into local `crm_users` table

### High-Level Design (HLD)
```
Any Prabandhan Service Call
  → fetchToken()
      → NoSQL: check cached token (1-hr TTL)
      → IF expired: POST Zoho OAuth → new token → cache
  → Zoho API call with token

Leads:
  Booking → /lead/create-db-crm-lead → Zoho upsert (leads)
  Demo completed → /Leads/{id}/actions/convert → Zoho deal created

Deals:
  Class completion → SNS → Lambda → createDBCRMDeal → Zoho upsert (deals)
  Payment → /deal/update-crm-deal-to-closed-won → Zoho deal stage = Closed Won

Notes:
  Deal created → auto-append (WhatsApp + Dashboard links)
  Manual → /deal/add-notes-in-crm-deal → Zoho notes

Tasks:
  Lead created → create "First Connect" task
  Audit score ≤6 → create "PQS Review" task (TL)
  Student joins Zoom → create "Join Trial Class" task

Zoho → Prabandhan webhook:
  SM user created/updated → sync to crm_users (SQL)
```

## External Integrations
- **Zoho CRM:** Primary CRM platform (Leads, Deals, Notes, Tasks, Users modules)
- **Zoho OAuth 2.0:** Token generation endpoint

## Internal Service Dependencies
- **Eklavya:** Student, parent, booking, payment data (source of truth for CRM data)
- **Paathshala:** Class and progress data for renewal CRM
- **Dronacharya:** Teacher data for deal creation
- **Platform:** Course, country, timezone mappings

## Database Operations

### Tables Accessed
- **Prabandhan NoSQL:** `crm_lead`, `db_crm_deals` — local mirrors of Zoho records
- **Prabandhan NoSQL:** Token cache
- **Prabandhan SQL:** `crm_users` — SM user mappings from Zoho webhook sync

### SQL / ORM Queries
- NoSQL read/write for token cache (key: `zoho_access_token`)
- `crm_lead.findOne({ bookingObjectId })` — duplicate check
- `db_crm_deals.findOne({ studentId, courseId })` — deal lookup
- SELECT `crm_users` WHERE `owner_id = ?`

### Transactions
- No SQL transactions — Zoho API operations are external and non-transactional
- Local NoSQL writes are independent of Zoho API success/failure in some flows

## Performance Analysis

### Good Practices
- Centralized Zoho gateway in Prabandhan — single point of control and monitoring
- Token caching eliminates repeated OAuth roundtrips
- Upsert operations prevent duplicate record creation across all modules
- Local NoSQL mirror (`crm_lead`, `db_crm_deals`) enables fast internal lookups without Zoho API calls

### Performance Concerns
- 1-hour token expiry causes latency spike on first call after expiry (token refresh adds ~500ms)
- No rate limiting handling documented — Zoho has API credit limits
- All microservice CRM updates are synchronous → Zoho unavailability blocks downstream flows
- Sequential Zoho operations (create → notes → tasks) increase end-to-end latency

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Zoho unavailability blocks synchronous flows (deal creation, note addition) |
| High | No Zoho API rate limit handling documented — potential 429 errors in peak scenarios |
| Medium | Token refresh adds latency on hourly expiry — proactive refresh not implemented |
| Low | Local NoSQL and Zoho records can diverge if Zoho write succeeds but local write fails |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Implement proactive token refresh 5 minutes before 1-hour expiry
- Add Zoho API error handler with 3-retry exponential backoff on 429/503 responses

### Month 1 (Architectural)
- Make all Zoho write operations async (queue-backed) to decouple from synchronous user-facing flows
- Add reconciliation job to detect and fix divergence between local NoSQL and Zoho records

## Test Scenarios

### Functional Tests
- Token expired → new token generated and cached → Zoho API call succeeds
- Lead upsert: `booking_uuid` duplicate → updates existing lead, not creates new
- Deal created → notes automatically appended with WhatsApp and dashboard links
- Task created for new lead → appears in Zoho CRM Tasks module

### Performance & Security Tests
- 1,000 Zoho API calls in rapid succession → rate limit behavior
- Token cache race condition (two concurrent expired-token requests) → only one regeneration

### Edge Cases
- Refresh token expired (long-term) → OAuth failure → alert mechanism
- Zoho API returns 404 for deal ID (deal deleted externally) → local NoSQL still has record → sync divergence
- Network timeout on Zoho API → retry behavior
