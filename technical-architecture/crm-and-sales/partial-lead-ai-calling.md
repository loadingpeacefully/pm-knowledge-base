---
title: Partial Lead AI Calling
category: technical-architecture
subcategory: crm-and-sales
source_id: 914e7a0d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Partial Lead AI Calling

## Overview
A partial lead is a user who initiates the booking flow but drops off without completing it within 12 minutes. For US/UK users, the system automatically schedules up to 5 AI call attempts at defined intervals (0, 5, 25, 30, 120 minutes post the 12-minute delay) via Retell AI through Hermes. DND compliance ensures calls occur between 9 AM and 9 PM local time.

## API Contract
**Endpoints:**
- `POST /tracker` — Triggered when users provide partial booking details; pushes to SQS if US/UK
- `POST /retell-ai-call-webhook` — Receives Retell call completion data
- `POST /webhook/partial-call` — Receives post-call AI data for partial lead processing

**SQS Queues:**
- `partial-lead-calling-prod.fifo` — 12-minute delayed message for partial lead trigger
- `prod-ai-call-process.fifo` — Post-call processing queue

**Hermes APIs:**
- `POST /api/v1/send-message` — Schedule call attempt
- Hermes Cancel API — Cancel remaining scheduled calls when booking is completed

## Logic Flow

### Controller Layer
- `/tracker` receives partial lead data → if US/UK, pushes `objectId` to `partial-lead-calling-prod.fifo` with 12-minute SQS delay
- `partialLeadAiCalling` consumer processes the queue

### Service/Facade Layer
**Initiation:**
1. User visits booking page, provides partial data → `/tracker` API called
2. If user is from US or UK:
   - Push `objectId` to `partial-lead-calling-prod.fifo` with 12-minute delay
3. After 12 minutes: `partialLeadAiCalling` consumer activates
4. **Validation checks:**
   - No future booking already exists for this parent
   - No existing scheduled partial lead call for this parent
   - Partial lead data has: phone, country, timezone

**Call Scheduling (if valid):**
- Schedule 5 call attempts via Hermes `send-message` API
- Call intervals (post initial 12-minute delay): 0, 5, 25, 30, 120 minutes
- DND compliance: if scheduled time falls outside 9 AM – 9 PM local time → move to 9 AM next day
- Log each scheduled call in `tryouts.communication_logs` using `booking_request_id`

**Post-Call Processing:**
1. Call completes → Retell webhook → `/webhook/partial-call`
2. Push to `prod-ai-call-process.fifo`
3. **If call picked up:**
   - `createBookingConsumer` called (same as lapsed lead flow)
   - Duration threshold: ≥ 60 seconds
   - Senpai LLM: validate intent + extract datetime
   - If booking created: `cancelPartialLeadCalls` → Hermes Cancel API (stop remaining calls)
4. **If call not picked:**
   - Mark attempt as failed
   - Allow next scheduled attempt to proceed

### High-Level Design (HLD)
```
User → /tracker (partial booking data)
  → IF US/UK: SQS push (12-min delay) → partialLeadAiCalling
      → Validation checks (no existing booking/calls)
      → Hermes: schedule 5 call attempts (0, 5, 25, 30, 120 min intervals)
          → DND check → adjust to 9AM if outside window
          → LOG: communication_logs

Call scheduled → Hermes → SQS: prod-hermes-schedule-ai-call
  → scheduleAICall consumer → Retell /v2/create-phone-call

Call completes → Retell → /webhook/partial-call
  → SQS: prod-ai-call-process.fifo
      → IF picked + ≥60s:
          → createBookingConsumer (Senpai LLM → booking)
          → cancelPartialLeadCalls → Hermes Cancel API
      → IF not picked: next attempt scheduled
```

## External Integrations
- **Retell AI:** `POST /v2/create-phone-call`, call completion webhook
- **Senpai API:** Intent validation and datetime extraction (same as lapsed lead flow)
- **Hermes:** Call scheduling (`send-message`), cancellation (Cancel API)

## Internal Service Dependencies
- **Tryouts:** `/tracker`, `booking_requests`, `communication_logs`, `demo_availability`
- **Eklavya:** `parents` lookup by phone (to check for existing bookings)
- **Hermes:** Message scheduling and cancellation

## Database Operations

### Tables Accessed
- `tryouts.booking_requests` — INSERT pending, UPDATE completed/failed
- `tryouts.communication_logs` — Log scheduled calls using `booking_request_id`
- `tryouts.demo_availability` — Available demo slots for time extraction

### SQL / ORM Queries
- SELECT `parents` WHERE `phone = ?` — check for existing parent/booking
- SELECT `communication_logs` WHERE `parent_id = ? AND type = 'partial-lead-call'` — check existing scheduled calls
- INSERT `booking_requests` (`identifier_type='phone'`, `identifier_value=phone`, `status='pending'`)
- INSERT `communication_logs` per scheduled call attempt
- UPDATE `booking_requests` SET `status = 'completed'|'failed'`

### Transactions
- Validation check + scheduling must be atomic to prevent race conditions (two concurrent `/tracker` calls for same phone)

## Performance Analysis

### Good Practices
- 5-attempt schedule with escalating intervals balances conversion effort with user experience
- DND compliance prevents calls during unacceptable hours — reduces opt-out rate
- `cancelPartialLeadCalls` on successful booking prevents over-calling converted leads
- `communication_logs` provides full audit of all call attempts per lead

### Performance Concerns
- SQS delay (12 minutes) means consumer must handle delayed messages correctly with FIFO ordering
- Hermes scheduling for 5 calls creates 5 individual scheduled messages per partial lead — scale concern at high volume
- Validation check + schedule not atomic — duplicate call sequences possible

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Validation check + Hermes scheduling not atomic — duplicate call scheduling possible |
| Medium | US/UK only implementation — no configurable country list |
| Low | Call intervals (0, 5, 25, 30, 120 min) hardcoded — not configurable |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add distributed lock on partial lead call scheduling (key: parent phone, TTL: 12 minutes)
- Move US/UK country list to configuration table for easy expansion

### Month 1 (Architectural)
- Externalize call intervals to a configurable campaign settings table
- Add partial lead conversion analytics (calls-to-booking conversion rate per attempt number)

## Test Scenarios

### Functional Tests
- US user drops off at 8 minutes → after 12 minutes, 5 calls scheduled at correct intervals
- UK user → same flow
- India user → no partial lead calling triggered
- Call answered at 75 seconds with booking intent → booking created → remaining calls cancelled
- Call answered at 45 seconds → below 60s threshold → no booking, next call attempt proceeds

### Performance & Security Tests
- 200 concurrent partial lead triggers — SQS throughput and correct deduplication
- DND compliance: 10 PM local time → call moved to 9 AM next day

### Edge Cases
- User completes booking manually during the 12-minute SQS delay window → validation prevents duplicate calls
- All 5 call attempts unanswered → `booking_requests` status `failed` after final attempt
- User's timezone invalid → default timezone used for DND calculation
