---
title: CURL API for Pancake Sync
category: technical-architecture
subcategory: crm-and-sales
source_id: a9d1c2bf
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# CURL API for Pancake Sync

## Overview
Pancake is an external CRM/contact management system used in certain markets. The Schola Server syncs raw Pancake contact data to the BrightChamps unified system via a webhook API, receives back a `BookingObjectId`, and stores it in Pancake contacts to maintain a two-way mapping.

## API Contract
**Endpoint:** `POST https://api-services-stage.brightchamps.com/tryouts/v1/pancake/webhook-for-pancake`

**Auth:** None documented (no API key or Bearer token in the CURL specification)

**Headers:**
```
Content-Type: application/json
```

**Request Body (raw JSON — must be passed as-is from Pancake without transformation):**
```json
{
  "Name": "string",
  "Student Name": "string",
  "Email": "string",
  "Phone": "string",
  "courses": "string (e.g. FinChamps)",
  "Trial Date Time": "string",
  "Status": "string (e.g. Trial Booked)",
  "PancakeCustomer": "string",
  "Owner": "string",
  "created_at": "datetime",
  "modified_at": "datetime"
}
```

**Critical Rule:** The object from Pancake must be passed **directly to the API without any transformation**.

**Response:** Contains `BookingObjectId` — the booking's object ID in the unified system.

**Status Codes:** 200 OK, 400 Bad Request, 500 Internal Server Error

## Logic Flow

### Controller Layer
- Receive raw Pancake contact webhook payload
- Validate `Content-Type: application/json`
- Route to booking creation service
- Return `BookingObjectId` in response

### Service/Facade Layer
1. Accept raw Pancake payload
2. Map Pancake fields to internal booking/student model (internal mapping, no external transformation)
3. Create or update booking record in unified system
4. Return `BookingObjectId` to Schola Server
5. Schola Server stores `BookingObjectId` back into Pancake CRM contacts table

**Two-Way Sync:**
- Pancake → Unified System: Raw payload via webhook
- Unified System → Pancake: `BookingObjectId` synced back to Pancake contacts table
- This bidirectional mapping ensures future updates in either system can be correlated

### High-Level Design (HLD)
```
Pancake (contact entered/updated)
  → Schola Server detects change
  → POST /tryouts/v1/pancake/webhook-for-pancake (raw payload, no transformation)
      → Unified Tryouts Service
          → Map fields → create/update booking
          → Return BookingObjectId
  → Schola Server stores BookingObjectId in Pancake contacts
  → Two-way sync established
```

## External Integrations
- **Pancake CRM:** Source contact management system
- **Schola Server:** Intermediary that reads Pancake contacts and calls the webhook

## Internal Service Dependencies
- **Tryouts Service:** Owns `/v1/pancake/webhook-for-pancake` endpoint and booking creation logic

## Database Operations

### Tables Accessed
- **Pancake contacts table:** `BookingObjectId` field must be added to support the return sync
- **Unified booking table (Tryouts):** Booking record created/updated from Pancake data

### SQL / ORM Queries
- INSERT or UPDATE booking record in Tryouts `bookings` table from Pancake payload
- SELECT `BookingObjectId` from newly created booking record

### Transactions
- Single booking creation — no multi-table transaction documented

## Performance Analysis

### Good Practices
- No-transform rule ensures data integrity — Pancake source data is preserved exactly
- Two-way sync via `BookingObjectId` provides referential integrity between systems

### Performance Concerns
- No authentication on webhook endpoint — potential for unauthorized payload injection
- If `BookingObjectId` sync back to Pancake fails, the two-way mapping is broken
- No rate limiting or deduplication on incoming Pancake webhooks documented

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No authentication (no API key or token) on webhook endpoint |
| High | No deduplication guard — duplicate Pancake contacts could create duplicate bookings |
| Medium | `BookingObjectId` field in Pancake contacts table must be manually added as schema change |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add `x-api-key` header authentication to the Pancake webhook endpoint
- Add deduplication check using Pancake `PancakeCustomer` ID or phone number

### Month 1 (Architectural)
- Implement event-driven sync using Pancake webhooks with retry logic
- Add `BookingObjectId` sync failure alerting to prevent silent mapping breaks

## Test Scenarios

### Functional Tests
- Valid Pancake payload → booking created → `BookingObjectId` returned → synced back to Pancake
- Duplicate Pancake contact re-sent → existing booking updated, not duplicated
- `Status = 'Trial Booked'` correctly maps to internal booking status

### Performance & Security Tests
- Unauthorized payload injection without API key (once auth is added)
- High-frequency Pancake webhook events — rate limiting behavior

### Edge Cases
- `Trial Date Time` in unsupported format → parsing error handling
- `courses` value not matching any internal course — fallback/error
- Schola Server fails to write `BookingObjectId` back to Pancake — retry mechanism
