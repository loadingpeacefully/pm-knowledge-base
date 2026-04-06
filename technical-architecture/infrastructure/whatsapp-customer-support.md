---
title: WhatsApp Customer Support
category: technical-architecture
subcategory: infrastructure
source_id: 092759d0-46be-4c66-b620-aec1f019a24e
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# WhatsApp Customer Support

## Overview
This document describes the BrightCHAMPS WhatsApp customer support system, which enables operations teams to receive and respond to user-initiated WhatsApp conversations triggered by demo class reminders. The system integrates with Kaleyra for WhatsApp messaging and exposes three internal APIs for conversation management.

## API Contract
**1. Get Conversations**
- Method: `GET`
- Path: `/conversations`
- Description: Fetches latest user-replied messages for the support dashboard
- Data source: `whatsapp_data` table
- Response: List of conversations ordered by most recent reply

**2. Get Conversations By Number**
- Method: `GET`
- Path: `/conversations/{{number}}`
- Description: Fetches chronological message history (incoming + outgoing) for a specific phone number
- Response: Full conversation thread for the selected number

**3. Send Message**
- Method: `POST`
- Path: `/send-message` (implied)
- Request Body:
```json
{
  "to": "<client_phone_number>",
  "from": "<kaleyra_number>",
  "body": "<custom_message_text>"
}
```
- Description: Sends a free-form reply to a specific WhatsApp conversation

**Auth:** Internal service — assumed standard auth.

## Logic Flow
### Controller Layer
1. User books a demo class → automated WhatsApp reminder is sent (via Hermes/Kaleyra)
2. User replies to the WhatsApp reminder → creates a user-initiated conversation
3. Kaleyra webhook fires → conversation data stored in `whatsapp_data` table
4. Operations team opens support dashboard → calls `GET /conversations` to see latest replies
5. Ops clicks on a conversation → calls `GET /conversations/{{number}}` for full history
6. Ops types and sends a custom reply → calls `POST /send-message`

### Service/Facade Layer
**Message Classification:**
- Some incoming messages are auto-tagged with prefixes like `"No lead found / Non-English"` indicating system-level classification logic exists
- Operations team can respond with **free-form messages** (no pre-approved template required) because the conversation is user-initiated

**Kaleyra Integration:**
- Kaleyra webhooks pipe incoming WhatsApp messages into the data system
- Data currently consumed by a legacy system — migration to new microservices is pending
- Which new microservice will handle Kaleyra webhooks is TBD

### High-Level Design (HLD)
```
Demo Class Booking
        │
        ▼
WhatsApp Reminder (Kaleyra → user)
        │
        ▼
User Replies to Reminder
        │
        ▼
Kaleyra Webhook → Data Ingestion Layer → whatsapp_data table
        │
        ▼
Operations Dashboard (GET /conversations)
        │
        ├── Select conversation (GET /conversations/{{number}})
        └── Send reply (POST /send-message → Kaleyra → WhatsApp → User)
```

## External Integrations
- **Kaleyra** — WhatsApp messaging provider; sends outbound reminders and receives inbound messages via webhooks
- **WhatsApp** — End-user messaging channel

## Internal Service Dependencies
- WhatsApp Customer Support → Kaleyra (webhook ingestion)
- WhatsApp Customer Support → `whatsapp_data` table (conversation storage)
- WhatsApp Customer Support → Demo booking flow (trigger for initial reminder)
- Future: Kaleyra webhooks will migrate to a new microservice (TBD — Hermes or dedicated service)

## Database Operations
### Tables Accessed

**whatsapp_data**
| Column | Description |
|--------|-------------|
| (phone) number | Conversation identifier |
| message content | Incoming/outgoing message body |
| direction | Incoming or outgoing |
| timestamp | Message timestamp |
| system tags | Auto-classification tags (e.g., "No lead found / Non-English") |

### SQL / ORM Queries
- Get latest conversations: `SELECT * FROM whatsapp_data WHERE direction='incoming' ORDER BY timestamp DESC`
- Get conversation by number: `SELECT * FROM whatsapp_data WHERE number = :number ORDER BY timestamp ASC`

### Transactions
N/A — Reads are non-transactional; writes are single-row inserts on webhook receipt.

## Performance Analysis
### Good Practices
- User-initiated conversation flow removes the need for pre-approved WhatsApp templates — faster ops response
- Chronological conversation view gives context to ops team before replying
- Auto-tagging of non-English or no-lead messages reduces ops triage time

### Performance Concerns
- Kaleyra webhooks feeding into a legacy system — migration risk and potential data inconsistency during transition
- No documented pagination on `GET /conversations` — could be slow with high message volumes
- No rate limiting or queue documented for outbound message sending — risk of Kaleyra API rate limit hits

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | Kaleyra webhooks still flowing into legacy system — migration to new microservice TBD and unscheduled |
| High | Database tables must be redesigned flexibly for future service migration — current schema may be legacy-coupled |
| Medium | No pagination documented on conversation list endpoint — performance risk at scale |
| Medium | No documented error handling for failed Kaleyra webhook deliveries |
| Low | Which microservice owns WhatsApp support is unresolved (Hermes vs. dedicated service) |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Add pagination to `GET /conversations` to prevent full table scans
- Document current `whatsapp_data` table schema for migration planning
- Decide which microservice will own Kaleyra webhook ingestion

### Month 1 (Architectural)
- Migrate Kaleyra webhook ingestion from legacy system to chosen microservice
- Redesign `whatsapp_data` table with service-agnostic schema for future portability
- Add a message delivery queue (SQS) for outbound WhatsApp sends to handle Kaleyra rate limits gracefully

## Test Scenarios
### Functional Tests
- Demo class reminder triggers WhatsApp message to user via Kaleyra
- User reply appears in operations dashboard within 30 seconds
- Ops team can view full conversation history for any phone number
- Ops team reply is delivered to user via Kaleyra successfully

### Performance & Security Tests
- `GET /conversations` returns paginated results in <500ms with 10k message records
- Outbound `POST /send-message` is rate-limited to prevent Kaleyra quota exhaustion
- Verify `whatsapp_data` is not accessible by unauthorized internal services

### Edge Cases
- User sends non-English WhatsApp message — auto-tag correctly applied
- Multiple users with same phone number (unlikely but possible) — de-duplication handling
- Kaleyra webhook delivery failure — retry mechanism or dead letter queue?

## Async Jobs & ETL
- Kaleyra inbound webhook → async write to `whatsapp_data` table
- Future: Kaleyra webhook processing will be moved to a microservice (likely queue-based via SQS)
