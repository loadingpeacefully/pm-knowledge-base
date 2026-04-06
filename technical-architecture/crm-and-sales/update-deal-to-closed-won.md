---
title: Update Deal to Close Won Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: 492b64b4
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Update Deal to Close Won Flow

## Overview
The Update Deal to Closed Won flow is triggered as part of the first-payment onboard flow. It updates the Zoho CRM deal stage to "Closed Won" and populates key financial and class metrics by calling the Prabandhan API with booking and payment details.

## API Contract
**Endpoint:** `POST /deal/update-crm-deal-to-closed-won` (Prabandhan)

**Request Body:**
```json
{
  "bookingUUID": "string (required)",
  "amount": "number (required)",
  "packageName": "string (required)",
  "totalCourseFee": "number (required)",
  "totalClassesPaid": "number (required)",
  "totalClassesBooked": "number (required)",
  "closingDate": "string (required, format: yyyy-mm-dd)",
  "totalClassesRemaining": "number (optional, defaults to totalClassesPaid)",
  "totalClassesCompleted": "number (optional, defaults to 0)"
}
```

**Response:** Updated deal record or error

**Status Codes:**
- 200 OK — deal successfully updated
- 400 Validation Error — deal not found for `bookingUUID`
- 424 Dependency Error — Zoho CRM update failed

## Logic Flow

### Controller Layer
- Receives `POST /deal/update-crm-deal-to-closed-won` from onboard-flow Lambda
- Validates request body (required fields)
- Returns success or structured error

### Service/Facade Layer
1. **Fetch Deal:** Query `db_crm_deals` by `bookingUUID`
   - IF NOT FOUND → throw Validation Error
2. **Extract Deal Data:** Get `id` (Zoho deal ID) and `dealName` from fetched record
3. **Build Zoho Payload:**
```json
{
  "id": "zoho_deal_id",
  "Deal_Name": "dealName",
  "Stage": "Closed Won",
  "Amount": "amount",
  "Course_Name": "packageName",
  "Total_Course_Fee": "totalCourseFee",
  "Closing_Date": "closingDate (yyyy-mm-dd)",
  "Total_Classes_Booked": "totalClassesBooked",
  "Total_Classes_Completed": "totalClassesCompleted (default 0)",
  "Total_Classes_Paid": "totalClassesPaid",
  "Total_Classes_Remaining": "totalClassesRemaining (default totalClassesPaid)"
}
```
4. **Zoho Update:** Send payload to Zoho CRM service
   - IF Zoho fails → throw Dependency Error
5. **Return:** Success response with updated deal data

**Trigger Context (Onboard Flow):**
- Called by `onboard-flow` Lambda ONLY when `COUNT(sale_payments WHERE status='paid') = 1`
- Called after: Hermes welcome emails + Paathshala curriculum provisioning
- Is the final step in the first-payment onboard sequence

### High-Level Design (HLD)
```
onboard-flow Lambda (first payment gate: COUNT paid sale_payments = 1)
  → Hermes: welcome_onbaord email
  → Hermes: class_schedule_after_onboard email
  → Paathshala: /curriculum/student/module
  → POST /deal/update-crm-deal-to-closed-won
      → db_crm_deals.findOne({ bookingUUID })
          → IF NOT FOUND: Validation Error
      → Build Zoho payload (Stage = "Closed Won", financial + class metrics)
      → Zoho CRM update
          → IF FAILS: Dependency Error
      → Return updated deal
```

## External Integrations
- **Zoho CRM:** Deal stage update via Prabandhan Zoho service (PUT/PATCH on deal record)

## Internal Service Dependencies
- **Prabandhan:** `db_crm_deals` (NoSQL), Zoho CRM service
- **Onboard-Flow Lambda:** Caller (Eklavya SQS consumer)

## Database Operations

### Tables Accessed
- **Prabandhan NoSQL:** `db_crm_deals` — lookup by `bookingUUID`
- **Zoho CRM (via API):** `Deals` module — stage + metric fields update

### SQL / ORM Queries
- `db_crm_deals.findOne({ booking_uuid: bookingUUID })` — fetch deal with Zoho deal ID
- Zoho API: UPDATE deal with mapped payload

### Transactions
- No SQL transactions — single NoSQL read + Zoho API write

## Performance Analysis

### Good Practices
- `bookingUUID`-based lookup ensures correct deal mapping across multiple students
- Default values for optional fields (`totalClassesRemaining`, `totalClassesCompleted`) prevent incomplete Zoho records
- Clear error type separation (Validation vs. Dependency) enables precise error handling by caller

### Performance Concerns
- Sequential execution in onboard flow (emails → Paathshala → this call) — if Zoho is slow, first-payment onboarding is delayed
- No retry on Dependency Error — Zoho CRM may show incorrect deal stage if the call fails

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No retry on Dependency Error (Zoho failure) — deal stage can remain "Demo Completed" permanently |
| Medium | Called synchronously in onboard flow — Zoho unavailability blocks onboarding completion |
| Low | `Closing_Date` format `yyyy-mm-dd` must be validated before Zoho call |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add 3-retry with 2-second backoff on Zoho CRM update failure
- Add structured logging for failed Closed Won updates with deal ID + bookingUUID for manual recovery

### Month 1 (Architectural)
- Make this call async (SQS-backed) within the onboard flow to decouple from synchronous sequence
- Add reconciliation check: daily job to find deals where payment is paid but stage is not Closed Won

## Test Scenarios

### Functional Tests
- First payment → `POST /deal/update-crm-deal-to-closed-won` called → Zoho deal stage = "Closed Won"
- Second payment (non-first) → flow NOT triggered (gate check in onboard Lambda)
- `bookingUUID` not found in `db_crm_deals` → Validation Error returned
- Zoho CRM unreachable → Dependency Error returned

### Performance & Security Tests
- Concurrent first-payment onboard events for different students → all deals correctly updated
- Zoho API returns 429 rate limit → error handling

### Edge Cases
- `totalClassesRemaining` not provided → defaults to `totalClassesPaid` (correct for first payment)
- `totalClassesCompleted` not provided → defaults to 0 (correct — no classes completed yet on first payment)
- `closingDate` in wrong format → Zoho API error propagated as Dependency Error
- Deal exists in `db_crm_deals` but Zoho deal was manually deleted → Dependency Error from Zoho update attempt
