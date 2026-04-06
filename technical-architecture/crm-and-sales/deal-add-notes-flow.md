---
title: Deal Add Notes Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: a1cc86cc
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Deal Add Notes Flow

## Overview
The deal add notes flow allows systems to attach structured notes (key-value pairs) to existing Zoho CRM deals. Notes are automatically appended during deal creation (WhatsApp link, dashboard link) and can be triggered manually via the internal API. OAuth token caching handles Zoho authentication.

## API Contract
**Internal Endpoint:** `POST /deal/add-notes-in-crm-deal`

**Request Body:**
```json
{
  "studentId": "string",
  "notes": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

**External Zoho API Called:**
`POST https://www.zohoapis.in/crm/v2/deals/{dealId}/Notes`

**Zoho Request Payload:**
```json
{
  "data": [
    {
      "Note_Title": "string",
      "Note_Content": "string"
    }
  ]
}
```

**Zoho Auth Header:**
```
Authorization: Zoho-oauthtoken {zoho_access_token}
```

**Status Codes:** 200 OK, 400 Validation Error (deal not found), 424 Dependency Error (Zoho call fails)

## Logic Flow

### Controller Layer
- Receive `POST /deal/add-notes-in-crm-deal` with `studentId` and `notes`
- Validate request structure
- Return success or error

### Service/Facade Layer
1. **Fetch Deal:** Lookup deal by `studentId` in internal database
2. **Validation:** If no deal found → throw Validation Error, halt processing
3. **Token Retrieval:**
   a. Check NoSQL database for cached Zoho access token
   b. If token is missing or expired (1-hour TTL) → generate new token using `ZOHO_REFRESH_TOKEN`, `ZOHO_CLIENT_ID`, `ZOHO_GRANT_TYPE`, `ZOHO_CLIENT_SECRET`
   c. Store new token in NoSQL database
4. **Payload Construction:** Transform `notes` key-value pairs into Zoho `{ Note_Title, Note_Content }` array
5. **Zoho API Call:** `POST /crm/v2/deals/{dealId}/Notes` with `Authorization: Zoho-oauthtoken`
6. **Error Handling:** If Zoho call fails → throw Dependency Error

**Auto-Note Generation (during deal creation):**
- WhatsApp link: `config_json.whatsappPrefix + parent.phone`
- Dashboard link: `config_json.dashboardPrefix + studentId + bookingObjectId + courseName`
- Both auto-appended via `add-notes-in-crm-deal` on deal creation success

### High-Level Design (HLD)
```
POST /deal/add-notes-in-crm-deal
  → Lookup deal by studentId (internal DB)
      → IF NOT FOUND: Validation Error
  → Get Zoho OAuth token
      → Check NoSQL cache (1-hour TTL)
      → IF EXPIRED: generate new token → store in NoSQL
  → Build Zoho payload (Note_Title + Note_Content per key-value pair)
  → POST https://www.zohoapis.in/crm/v2/deals/{dealId}/Notes
      → IF FAILS: Dependency Error
      → IF SUCCESS: return deal data

[Auto-trigger on deal creation]
  → WhatsApp link + Dashboard link → add-notes-in-crm-deal
```

## External Integrations
- **Zoho CRM API:** `POST /crm/v2/deals/{dealId}/Notes`
- **Zoho OAuth:** Token endpoint using refresh token + client credentials
- **Token Cache:** NoSQL database (1-hour TTL)

## Internal Service Dependencies
- **Prabandhan:** Owns `/deal/add-notes-in-crm-deal` and `db_crm_deals` collection
- **Deal Creation Flow:** Automatically calls this endpoint post-deal creation

## Database Operations

### Tables Accessed
- **Prabandhan NoSQL (`db_crm_deals`):** Lookup deal by `studentId`, retrieve `dealId`
- **NoSQL (token cache):** Read/write Zoho access token

### SQL / ORM Queries
- `db_crm_deals.findOne({ studentId })` — fetch deal details
- NoSQL read/write for Zoho token cache

### Transactions
- No SQL transactions — single NoSQL read + Zoho API call

## Performance Analysis

### Good Practices
- OAuth token caching avoids regenerating token on every API call (1-hour cache)
- Validation error on missing deal prevents unnecessary Zoho API calls
- Auto-note generation on deal creation ensures SMs always have WhatsApp + dashboard links

### Performance Concerns
- Token refresh adds latency on first call after 1-hour expiry
- Sequential: DB lookup → token check → Zoho API — no parallelism possible
- No batching — each note addition is a separate Zoho API call

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Token expiry at exactly 1 hour could cause race conditions in high-frequency note addition scenarios |
| Low | Notes are per-call — no batch note creation endpoint documented |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add proactive token refresh 5 minutes before expiry to eliminate cache-miss latency
- Add structured logging on Zoho API failures for debugging

### Month 1 (Architectural)
- Implement batch note creation for multi-note scenarios to reduce Zoho API call count

## Test Scenarios

### Functional Tests
- Valid `studentId` with existing deal → notes added to Zoho CRM
- Invalid `studentId` (no deal found) → Validation Error returned
- Zoho API failure → Dependency Error returned
- Auto-notes on deal creation → WhatsApp and dashboard links correctly appended

### Performance & Security Tests
- Token cache miss (first call after expiry) → new token generated and cached
- Concurrent note addition requests with expired token — only one token regeneration

### Edge Cases
- `notes` object with special characters in values — Zoho payload encoding
- Zoho access token generation fails (invalid refresh token) — error propagation
- Deal exists in internal DB but deleted from Zoho — Dependency Error on Zoho call
