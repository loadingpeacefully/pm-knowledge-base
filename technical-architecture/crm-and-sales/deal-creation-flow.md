---
title: Deal Creation Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: 7c69a66a
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Deal Creation Flow

## Overview
CRM deals are created by converting an existing lead into a deal when a demo class is marked successful. The flow is event-driven via SNS/SQS, executes `createDBCRMDeal`, upserts to Zoho CRM, stores the deal in `db_crm_deals` (NoSQL), and automatically appends WhatsApp and dashboard links as notes.

## API Contract
**Subsequent Deal Operation Endpoints:**
- `POST /v1/deal/update-crm-deal-to-closed-won`
- `POST /deal/add-notes-in-crm-deal`

N/A for primary deal creation — triggered via SNS/SQS event, not REST endpoint.

**`createDBCRMDeal` Required Fields:**
```json
{
  "bookingObjId": "string",
  "demoTeacherName": "string",
  "demoTeacherId": "string"
}
```

**Optional Fields:**
```json
{
  "hotLead": "string (default: HotLead-No)",
  "labels": "array",
  "notes": "object",
  "smEmail": "string (if omitted: defaults to owner ID 87956000301603205)"
}
```

**Zoho Deal Payload:**
```json
{
  "Deal_Name": "parent.name",
  "Stage": "Demo Completed",
  "userid": "string",
  "Demo_Teacher": "string",
  "Demo_Time": "datetime",
  "Type": "booking type",
  "Vertical": "string",
  "country_detected": "string",
  "Time_Zone": "string",
  "Course": "string",
  "booking_uuid": "string"
}
```

## Logic Flow

### Controller Layer
- SNS → Prabandhan SQS → `prabandhan-class-completion-flow` Lambda
- Alternatively: `bc8aa2be` lead creation calls `createDBCRMDeal` for non-demo bookings (`isDemo = false`)

### Service/Facade Layer
**Primary Trigger (Post Demo):**
1. Teacher submits feedback (class marked Successful) → SNS published
2. Prabandhan SQS picks up message → `prabandhan-class-completion-flow` Lambda
3. Fetch `demoClassId` → Paathshala: booking details, teacher details
4. Execute `createDBCRMDeal`:
   a. Fetch booking details from Prabandhan
   b. Search existing lead in Zoho → convert lead to deal
   c. Build Zoho deal payload with `Deal_Name`, `Stage='Demo Completed'`, course, teacher, country, timezone
   d. Set deal owner: if `smEmail` provided → assign to SM; else default owner ID `87956000301603205`
   e. Send to Zoho upsert service targeting `deal` module, pipeline=`sales`
   f. Zoho upsert: IF deal exists → UPDATE; IF not → CREATE
5. INSERT deal record in `db_crm_deals` (Prabandhan NoSQL)
6. Query `crm_users` SQL table for owner ID resolution
7. Auto-append notes: WhatsApp link + Dashboard link via `/deal/add-notes-in-crm-deal`

**Secondary Trigger (Non-Demo Bookings):**
- `isDemo = false` during lead creation → `createDBCRMDeal` called with default teacher values

**Deal Stages Lifecycle:**
- `Demo Completed` → `Closed Won` (first payment) → Renewal stages (if applicable)
- Intermediate: `Parent Contacted`, `Appointment Scheduled`, `Pitching Done`, `On Hold`, `Interested`
- Terminal: `Closed Won`, `Closed Won – Sales`, `Closed Won – Previous Cycle`, `Closed Lost`

### High-Level Design (HLD)
```
Teacher submits feedback (class=Successful)
  → SNS publish
  → Prabandhan SQS
      → prabandhan-class-completion-flow Lambda
          → Paathshala: demo class + booking details
          → createDBCRMDeal()
              → Find/convert existing Zoho lead → Deal
              → Zoho upsert (deal module, pipeline=sales)
              → INSERT db_crm_deals (NoSQL)
              → Query crm_users for owner mapping
              → /deal/add-notes-in-crm-deal (WhatsApp + Dashboard links)
          → Log error to Slack if any step fails
```

## External Integrations
- **Zoho CRM:** Deal upsert via `/crm/v2/deals/upsert` (or convert from lead via `/crm/v2/Leads/{id}/actions/convert`)
- **Slack:** Error alerting on `createDBCRMDeal` failure

## Internal Service Dependencies
- **Paathshala:** `demo_classes` (class validation), booking/teacher details
- **Prabandhan:** `db_crm_deals` (NoSQL deal storage), `crm_users` (SQL owner lookup)
- **Eklavya:** Student/parent context for deal payload
- **Platform:** Master courses for course name/vertical mapping

## Database Operations

### Tables Accessed
- **Prabandhan NoSQL:** `db_crm_deals` — INSERT new deal record
- **Prabandhan SQL:** `crm_users` — resolve employee IDs to owner IDs
- **Paathshala SQL:** `demo_classes` — class validation trigger
- **Zoho CRM:** `Leads` module (source for conversion), `Deals` module (target)

### SQL / ORM Queries
- `db_crm_deals.insertOne({ bookingUUID, dealId (from Zoho), courseId, studentId, ... })`
- SELECT `crm_users` WHERE `owner_id = ?` → get `user_id`
- Zoho lead search + conversion via API

### Transactions
- If any step in `createDBCRMDeal` fails → error logged to Slack, Lambda exits
- No explicit SQL rollback documented for partial deal creation

## Performance Analysis

### Good Practices
- Zoho upsert (IF exists → UPDATE, IF not → CREATE) prevents duplicate deals
- Auto-appended notes (WhatsApp + dashboard links) ensure SM has immediate context
- Error logging to Slack provides real-time failure visibility

### Performance Concerns
- Multiple sequential API calls: Paathshala → Zoho lead search → Zoho deal create → notes append
- No retry on Zoho upsert failure — if Zoho is temporarily unavailable, deal is lost
- `crm_users` SQL lookup per deal — no caching

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No retry mechanism on Zoho upsert failure — deals can be silently lost |
| Medium | Sequential API chain (Paathshala → Zoho → Notes) adds latency per deal |
| Low | Default owner ID `87956000301603205` hardcoded — admin change requires code update |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add 3-retry with exponential backoff on Zoho upsert calls
- Cache `crm_users` mappings (TTL: 1 hour) to reduce SQL lookups

### Month 1 (Architectural)
- Move default owner ID to configuration table for admin management
- Add compensating action in Slack alert to include re-trigger command for failed deal creation

## Test Scenarios

### Functional Tests
- Demo marked successful → deal created in Zoho with stage `Demo Completed`
- Non-demo booking (`isDemo=false`) → deal created immediately on lead creation
- `smEmail` provided → deal assigned to specific SM
- No `smEmail` → deal assigned to default owner ID
- Auto-notes → WhatsApp link + dashboard link appended to Zoho deal

### Performance & Security Tests
- Concurrent class completions — multiple deals created simultaneously
- Zoho rate limits — deal creation under high class completion load

### Edge Cases
- Lead not found in Zoho when converting → error handling and Slack alert
- `prabandhan-class-completion-flow` Lambda timeout — deal creation incomplete
- Same booking ID processed twice (SNS delivery guarantee) — Zoho upsert handles idempotently
