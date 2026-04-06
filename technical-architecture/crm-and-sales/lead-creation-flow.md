---
title: Lead Creation Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: bc8aa2be
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Lead Creation Flow

## Overview
Lead creation is triggered by a new booking's `bookingObjectId` being sent to Prabandhan's `/lead/create-db-crm-lead` endpoint. The service fetches booking/student/parent/course data from Eklavya, maps it to Zoho CRM lead fields, performs a duplicate check on `booking_uuid`, and upserts the lead to Zoho CRM and local NoSQL.

## API Contract
**Endpoint:** `POST /lead/create-db-crm-lead` (Prabandhan)

**Request Body:**
```json
{
  "bookingObjectId": "string"
}
```

**Response:** Created/updated lead record confirmation

**Status Codes:** 200 OK, 400 Dependency Error (booking not found in Eklavya), 400 Validation Error (bad input), 424 Dependency Error (Zoho upsert fails)

## Logic Flow

### Controller Layer
- Receive `POST /lead/create-db-crm-lead` with `bookingObjectId`
- Delegate to lead creation service
- Return lead record or error

### Service/Facade Layer
1. **Fetch Details:** Use `bookingObjectId` to fetch booking, student, parent, course, timezone from Eklavya
   - Validation: if not found → throw Dependency Error
2. **Referral Check:**
   - If `utmSource` = "Sibling" or "Referral" AND `referralType` = "deal" or "uri":
     - `referrerId` is a deal ID → fetch deal owner ID
     - Assign as lead owner
   - Else: assign default owner ID `87956000000111013`
3. **Duplicate Check:** Search local NoSQL for existing lead with `bookingObjectId`
   - If exists: UPDATE existing CRM lead
   - If not: proceed with new creation
4. **Data Mapping** to Zoho Lead fields:
   - `First_Name` / `Child_Name` → `student.name`
   - `Last_Name` → `parent.name`
   - `Mobile` → `parent.phone`
   - `Email` → `parent.email`
   - `Lead_Status` → `"Not Contacted"` (hardcoded)
   - `Time_Zone` → `timeZoneDetail.display_name`
   - `userid` → `student.id`
   - `Demo_Time` → `booking.datetime` (if `isDemo=false` and no datetime: `new Date().toISOString()`)
   - `Course` → `courseDetail.name`
   - `Vertical` → `courseDetail.MasterVertical.name`
   - `Lead_Source` → `timeZoneDetail.Country.name`
   - `booking_uuid` → `booking.objectId` (used as `duplicate_check_fields`)
5. **Zoho Upsert:** Send to Zoho upsert service → `leads` module
   - Duplicate check field: `booking_uuid`
   - If duplicate exists in Zoho → UPDATE; else → CREATE
6. **Persist Locally:** Store new Zoho lead ID in `crm_lead` (NoSQL)
7. **Deal Creation (conditional):** If `isDemo = false` → call `createDBCRMDeal` with default teacher values

### High-Level Design (HLD)
```
Booking confirmed → bookingObjectId
  → POST /lead/create-db-crm-lead (Prabandhan)
      → Eklavya: fetch booking + student + parent + course + timezone
          → IF NOT FOUND: Dependency Error
      → Referral check (utmSource/referralType)
          → Assign owner ID (referral deal owner OR default)
      → Local NoSQL: duplicate check by bookingObjectId
          → IF EXISTS: update Zoho lead
          → IF NOT: continue creation
      → Map to Zoho lead payload (Lead_Status = "Not Contacted")
      → Zoho upsert (leads module, duplicate_check: booking_uuid)
      → Store lead in crm_lead (NoSQL)
      → IF isDemo=false: createDBCRMDeal()
```

## External Integrations
- **Zoho CRM:** Lead upsert via `https://www.zohoapis.in/crm/v2/leads/upsert`

## Internal Service Dependencies
- **Eklavya:** Booking details, student/parent profiles, timezone data
- **Platform Service:** Timezone ID resolution from string name
- **Prabandhan:** `crm_lead` (NoSQL), Zoho upsert service

## Database Operations

### Tables Accessed
- **Eklavya SQL:** `bookings`, `students`, `parents`, `courses`, `timezones`
- **Prabandhan NoSQL:** `crm_lead` — stores created lead with Zoho lead ID
- **Zoho CRM:** `Leads` module (via API)

### SQL / ORM Queries
- GET Eklavya booking data by `objectId`
- `crm_lead.findOne({ bookingObjectId })` — duplicate check
- `crm_lead.insertOne({ bookingObjectId, zohoLeadId, ... })` — persist new lead
- Zoho API: `POST /crm/v2/leads/upsert` with `duplicate_check_fields: ['booking_uuid']`

### Transactions
- No SQL transactions — Eklavya read + NoSQL write + Zoho API are sequential independent operations

## Performance Analysis

### Good Practices
- `booking_uuid` as duplicate check field in both local NoSQL and Zoho prevents duplicate leads at two levels
- Default owner assignment prevents unowned leads from slipping through
- Referral type detection ensures proper attribution tracking

### Performance Concerns
- Sequential dependency: Eklavya fetch → Zoho upsert → NoSQL persist — any failure breaks the chain
- No retry on Zoho upsert failure — lead could be lost
- Each lead creation requires an Eklavya API call even for re-triggered bookings

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No retry on Zoho upsert failure — lead silently lost if Zoho is temporarily unavailable |
| Medium | Default owner ID `87956000000111013` hardcoded in service logic |
| Low | `Lead_Status = "Not Contacted"` hardcoded — no configurable initial status |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add 3-retry with exponential backoff on Zoho upsert
- Move default owner ID to environment configuration

### Month 1 (Architectural)
- Add event-driven retry (SQS DLQ + retry Lambda) for failed lead creations
- Cache Eklavya booking data per `bookingObjectId` during creation (prevent duplicate Eklavya calls on retry)

## Test Scenarios

### Functional Tests
- Valid booking → lead created in Zoho with `Lead_Status = "Not Contacted"`
- Referral booking (`utmSource=Sibling`) → deal owner assigned as lead owner
- Same `bookingObjectId` submitted twice → Zoho `booking_uuid` duplicate check prevents new lead
- `isDemo=false` booking → `createDBCRMDeal` called with default teacher values

### Performance & Security Tests
- 500 concurrent lead creation requests — Eklavya and Zoho throughput
- Zoho API rate limit (API credits exhausted) — graceful error handling

### Edge Cases
- Eklavya returns student but no parent → validation handling
- Timezone string not found in Platform service → lead creation with null timezone
- `referrerId` is a deal ID that no longer exists → fallback to default owner
