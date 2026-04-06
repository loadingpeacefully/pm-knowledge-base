---
title: Lead Generation from AI Calling
category: technical-architecture
subcategory: crm-and-sales
source_id: e0a99a9a
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Lead Generation from AI Calling

## Overview
AI calling is used to generate leads by targeting two segments: lapsed leads (no booking in 25+ days) and partial leads (dropped off within 12 minutes of booking initiation). Retell AI handles the outbound calls; webhook data is parsed via LLM (Senpai API) to extract booking intent, course preference, and demo time; leads are then created in the standard booking pipeline.

## API Contract
**Webhook Endpoint (Retell → system):**
`POST /retell-ai-call-webhook` (Tryouts service)
- Receives call completion payload from Retell AI

**External Retell API:**
`POST https://api.retell.ai/v2/create-phone-call` — Initiates outbound call

**Internal LLM API (Senpai):**
`POST https://api-services.brightchamps.com/senpai/api/v1/feedback`
- Prompts: `validateDemoSchedule` (booking intent), `datetimeExtractPrompt` (parse date/time)

**SQS Queues:**
- `prod-tryouts-create-booking` — Processes Retell webhook → booking creation
- `prod-ai-call-process.fifo` — Post-call data processing

## Logic Flow

### Controller Layer
- `/retell-ai-call-webhook` receives Retell payload → pushes to `prod-tryouts-create-booking` SQS
- `createBookingConsumer` processes SQS messages

### Service/Facade Layer
**Call Duration Threshold:**
- Lapsed leads: ≥ 30 seconds call duration
- Partial leads: ≥ 60 seconds call duration

**`createBookingConsumer` Processing:**
1. INSERT `tryouts.booking_requests` with `pending` status
   - `identifier_type` = `studentId` (lapsed) or `phone` (partial)
   - `identifier_value` = corresponding value
2. Check call duration threshold → if below: mark `failed`, exit
3. **Intent Validation (Senpai LLM):**
   - Send transcript to `validateDemoSchedule` prompt → check if user wants to book demo
   - If no booking intent → mark `failed`, exit
4. **Date/Time Extraction:**
   - `datetimeExtractPrompt` → extract preferred demo date and time
   - Check `demo_availability` table for available slot
   - If slot unavailable: add 12-hour buffer and recheck
5. **Course Identification:**
   - Match Retell `custom_analysis_data.demo_subject` against dictionary:
     - coding → courseId 1, robotics → courseId 3, math → courseId 15
6. **Lead Quality Score (LQS):** Store Retell custom variables in LQS tracking table
7. **Booking Creation:** Build partial booking + demo booking JSON → create via standard booking pipeline
8. UPDATE `booking_requests` status: `completed` (success) or `failed`

**Post-Call Data Processing:**
- Push Retell `call_id` to delayed SQS → fetch `GET /v2/get-call/{callId}`
- Check disconnection reason (user/agent hangup) + blocklist flag
- INSERT final record into `hermes.ai_call_data`

**Data Captured from Retell `custom_analysis_data`:**
- `demo_subject` → courseId mapping
- `demo_date_time` → preferred booking slot
- `booking_intent` (boolean/string)
- `child_nature`
- `previous_experience`
- `buying_schedule`
- Lead Quality Score variables

### High-Level Design (HLD)
```
Retell AI completes call
  → POST /retell-ai-call-webhook
      → SQS: prod-tryouts-create-booking
          → createBookingConsumer
              → INSERT booking_requests (pending)
              → Check duration threshold (≥30s lapsed, ≥60s partial)
              → Senpai: validateDemoSchedule (booking intent check)
              → Senpai: datetimeExtractPrompt (extract date/time)
              → demo_availability check + 12hr buffer if needed
              → Course dictionary mapping
              → LQS tracking
              → Create booking (standard pipeline)
              → UPDATE booking_requests (completed|failed)
  → Delayed SQS: prod-ai-call-process.fifo
      → GET /v2/get-call/{callId}
      → Check disconnection + blocklist
      → INSERT hermes.ai_call_data
```

## External Integrations
- **Retell AI:** `POST /v2/create-phone-call` (initiate), Webhook (receive call data)
- **Senpai API:** LLM for intent validation and datetime extraction
- **Twilio:** Telephony provider used by Retell for actual call delivery
- **ElevenLabs TTS:** Text-to-speech for Retell voice agent

## Internal Service Dependencies
- **Tryouts:** `/retell-ai-call-webhook`, `createBookingConsumer`, `booking_requests`, `demo_availability`
- **Hermes:** `ai_call_data` table (post-call record storage)
- **Eklavya:** Standard booking creation pipeline (downstream)

## Database Operations

### Tables Accessed
- `tryouts.booking_requests` — INSERT with pending status; UPDATE to completed/failed
- `tryouts.demo_availability` — Check available demo slots
- `hermes.ai_call_data` — Final call record INSERT
- LQS tracking table — Lead Quality Score variables

### SQL / ORM Queries
- INSERT `booking_requests` (`identifier_type`, `identifier_value`, `status='pending'`, `source_id`)
- SELECT `demo_availability` WHERE `datetime BETWEEN ? AND ?` (slot availability check)
- UPDATE `booking_requests` SET `status = 'completed'|'failed'`
- INSERT `hermes.ai_call_data` (call_id, duration, disconnection_reason, blocklist_flag, transcript)

### Transactions
- No multi-table transactions — sequential inserts and updates

## Performance Analysis

### Good Practices
- LLM-based intent validation prevents junk bookings from misheard/irrelevant calls
- Duration threshold gates prevent processing very short (likely failed) calls
- 12-hour buffer on demo availability ensures teacher preparation time
- `booking_requests` table provides full audit trail of all AI call attempts

### Performance Concerns
- Sequential LLM calls (Senpai API) for intent + datetime extraction add 2-5s per call
- `demo_availability` check could be expensive at scale (many slots queried)
- `hermes.ai_call_data` INSERT via delayed SQS — post-call analytics delayed

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Sequential Senpai API calls (intent + datetime) — could be parallelized or combined |
| Medium | Course dictionary (coding=1, robotics=3, math=15) hardcoded — requires code change to add courses |
| Low | `hermes.ai_call_data` table is cross-service (Hermes owned) — coupling concern |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Combine `validateDemoSchedule` and `datetimeExtractPrompt` into a single Senpai API call
- Externalize course dictionary to a configurable database table

### Month 1 (Architectural)
- Pre-index `demo_availability` by date range for fast slot lookup
- Add LQS analytics dashboard for AI call conversion tracking

## Test Scenarios

### Functional Tests
- 45-second lapsed call with booking intent → booking created, `completed` status
- 25-second call → duration threshold not met → `failed` status, no booking
- No booking intent detected by Senpai → `failed` status
- Preferred demo slot unavailable → 12-hour buffer applied → next available slot booked
- Course "coding" → courseId=1 mapping correct

### Performance & Security Tests
- Senpai API timeout during intent validation → graceful failure, mark `failed`
- 100 concurrent Retell webhooks → SQS processing throughput

### Edge Cases
- Transcript mentions multiple courses → first match used
- Demo slot unavailable even after 12-hour buffer → escalation or next-day booking
- User speaks in non-English language → LLM extraction accuracy
- Blocklist flag set for phone number → `ai_call_data` record but no booking
