---
title: Retell Integration and Lapsed Lead Calling
category: technical-architecture
subcategory: crm-and-sales
source_id: c8136452
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Retell Integration and Lapsed Lead Calling

## Overview
Lapsed leads are parents who last booked a demo more than 25 days ago, have no paid classes, and have not been contacted in the past 7 days. Retell AI is configured as a voice agent (GPT-4.1 mini + ElevenLabs TTS + Twilio telephony) to make outbound calls. Call scheduling is batch-processed via CSV → Hermes → SQS → Retell API; post-call webhook data is processed to create bookings.

## API Contract
**Hermes Scheduling API:**
`POST /api/v1/send-message`
- Schedules outbound AI calls via Hermes SQS pipeline
- SQS Queue: `prod-hermes-schedule-ai-call`

**Retell Call Initiation:**
`POST https://api.retell.ai/v2/create-phone-call`

**Retell Post-Call Webhook:**
`POST /retell-ai-call-webhook` (Tryouts service)
- `call_analyzed` event from Retell

**Retell Get Call API:**
`GET https://api.retell.ai/v2/get-call/{callId}`

**SQL Query for Lapsed Lead Identification:**
```sql
SELECT parent_data
FROM analytics
WHERE b.datetime > NOW() - INTERVAL '25 days'
  AND no paid classes enrolled
  AND no vendor communication in past 7 days
  AND country IN (eligible countries)
```

## Logic Flow

### Controller Layer
- Batch script identifies lapsed leads → generates CSV → processes via Hermes
- `scheduleAICall` consumer handles SQS → Retell API call
- `/retell-ai-call-webhook` receives post-call data → `createBookingConsumer`

### Service/Facade Layer
**Lapsed Lead Identification:**
1. SQL query against analytics DB — criteria:
   - Last demo booking > 25 days ago
   - No paid classes enrolled
   - No vendor communication in past 7 days
   - Country in eligible list
2. Batch results exported to CSV

**Call Scheduling:**
1. Create Hermes communication template: `medium='ai-call'`, `vendor='retell'`
2. Script reads CSV, maps user timezones → distributes call times in 10:30 AM – 1:30 PM local window
3. Send payloads to Hermes `/api/v1/send-message` (batched)
4. Hermes pushes to SQS: `prod-hermes-schedule-ai-call`
5. `scheduleAICall` consumer → `POST /v2/create-phone-call` (Retell)

**Retell AI Agent Configuration:**
- Voice engine: `retell_voice_engine`
- LLM: `gpt_4_1_mini_high_priority`
- TTS: `elevenlabs_tts_new`
- Telephony: Twilio
- Dynamic variables: `child_name`, `course_name`, `student_id`

**Post-Call Processing:**
1. Retell fires `call_analyzed` webhook → `/retell-ai-call-webhook`
2. Payload includes: transcript, duration, `custom_analysis_data`, LLM token usage, recording URLs
3. Push to SQS: `prod-tryouts-create-booking`
4. `createBookingConsumer`:
   - Filter: duration ≥ 30 seconds
   - Senpai: `validateDemoSchedule` → confirm booking intent
   - Senpai: `datetimeExtractPrompt` → extract demo time
   - Check `demo_availability` + 12-hour buffer
   - Course mapping via dictionary
   - LQS tracking
   - Create booking if validated
5. Log final call data:
   - Push `call_id` to delayed SQS → `GET /v2/get-call/{callId}`
   - Check disconnection reason + blocklist
   - INSERT `hermes.ai_call_data`

### High-Level Design (HLD)
```
Analytics SQL → Lapsed leads (>25 days, no paid classes, no recent contact)
  → CSV batch → Hermes template (ai-call, retell)
  → Hermes /api/v1/send-message (batched, TZ-aware scheduling 10:30AM-1:30PM)
  → SQS: prod-hermes-schedule-ai-call
      → scheduleAICall consumer
          → POST /v2/create-phone-call (Retell)
              → Retell: GPT-4.1 mini + ElevenLabs TTS + Twilio phone call

Call completes → call_analyzed webhook → /retell-ai-call-webhook
  → SQS: prod-tryouts-create-booking
      → createBookingConsumer
          → Duration check ≥30s
          → Senpai: intent + datetime
          → demo_availability check
          → Course mapping
          → LQS tracking
          → CREATE BOOKING (standard pipeline)
  → Delayed SQS → GET /v2/get-call/{callId}
      → Check disconnection + blocklist
      → INSERT hermes.ai_call_data
```

## External Integrations
- **Retell AI:** `POST /v2/create-phone-call`, `GET /v2/get-call/{callId}`, `call_analyzed` webhook
- **Twilio:** Phone call delivery via Retell
- **ElevenLabs TTS:** Voice synthesis for Retell AI agent
- **GPT-4.1 mini:** Conversation logic for Retell
- **Senpai API:** Intent validation + datetime extraction
- **Hermes:** Call scheduling and template management

## Internal Service Dependencies
- **Tryouts:** `/retell-ai-call-webhook`, `createBookingConsumer`, `booking_requests`, `demo_availability`
- **Hermes:** `ai_call_data` table, scheduling API
- **Eklavya:** Standard booking creation (downstream from `createBookingConsumer`)
- **Analytics DB:** Lapsed lead identification via SQL query

## Database Operations

### Tables Accessed
- **Analytics DB:** Lapsed lead query (read-only)
- `tryouts.booking_requests` — INSERT pending; UPDATE completed/failed
- `tryouts.demo_availability` — Slot availability check
- `hermes.ai_call_data` — Final call record INSERT
- LQS tracking table — Lead quality scores

### SQL / ORM Queries
- Analytics: SELECT parents WHERE last_booking > 25 days AND no paid classes AND no recent communication
- INSERT `booking_requests` (`identifier_type='studentId'`, `status='pending'`)
- UPDATE `booking_requests` SET `status = 'completed'|'failed'`
- INSERT `hermes.ai_call_data` (call_id, duration, transcript, disconnection_reason)

### Transactions
- No multi-table transactions — sequential processing pipeline

## Performance Analysis

### Good Practices
- Batch scheduling with timezone-aware distribution prevents call flooding in any single timezone
- 10:30 AM – 1:30 PM local window maximizes answer rates
- 30-second duration threshold filters out voicemail/rejected calls efficiently
- Retell's `custom_analysis_data` provides structured data extraction without manual parsing

### Performance Concerns
- CSV batch processing is manual — lacks real-time trigger capability
- Sequential Senpai API calls (intent + datetime) add 2-5s per processed call
- `hermes.ai_call_data` INSERT via delayed SQS means analytics are not real-time

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Manual CSV batch process — no automated scheduled trigger for lapsed lead identification |
| Medium | Analytics SQL query runs on analytics DB — cross-database dependency |
| Medium | Course dictionary hardcoded (coding=1, math=15, robotics=3) |
| Low | Call window (10:30AM–1:30PM) hardcoded — not configurable per market |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Automate lapsed lead SQL → Hermes pipeline as a scheduled Lambda (daily)
- Externalize call window and course dictionary to configuration table

### Month 1 (Architectural)
- Replace CSV batch with streaming pipeline from analytics DB → Hermes directly
- Combine Senpai intent + datetime prompts into a single API call to halve latency

## Test Scenarios

### Functional Tests
- Lapsed lead identified correctly (25+ days, no paid, no recent contact)
- Call scheduled in 10:30 AM – 1:30 PM local window per timezone
- Call answered at 35 seconds with booking intent → booking created
- Call answered at 20 seconds → below threshold → no booking, status failed
- Preferred demo time unavailable → 12-hour buffer → next available slot

### Performance & Security Tests
- 1,000 lapsed leads batch processed — Hermes and Retell throughput
- Retell webhook replay (same call_id) — idempotency check

### Edge Cases
- User's country not in eligible list but still in analytics results → guard check
- Retell `custom_analysis_data` missing `demo_subject` → fallback course assignment or failure
- All demo slots full for 48 hours → failure handling
