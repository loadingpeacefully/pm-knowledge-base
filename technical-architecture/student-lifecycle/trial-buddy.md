---
title: Trial Buddy
category: technical-architecture
subcategory: student-lifecycle
source_id: 9f0b701d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Trial Buddy

## Overview
Trial Buddy is a conversational AI assistant (named Niki) that helps parents book and reschedule demo classes through Web Chat, WhatsApp, and iMessage. It uses AWS Bedrock (Claude model) for natural language understanding and tool orchestration, with Redis for concurrency/state management and MySQL for durable conversation storage.

## API Contract

### /demo-stream (Primary Endpoint)
- **Auth:** None documented (invoked via communication vendor webhooks)
- **Purpose:** Primary conversational AI endpoint powering Niki
- **Trigger:** SQS message from communication vendors (Kaleyra, Hermes, Snachar) when a user sends a message

### GET /eklavya/v1/student/fetch-from-phone
- **Auth:** Internal
- **Query Params:** `phone={phoneNumber}`
- **Purpose:** Retrieve existing student and parent details by phone number

## Logic Flow

### Controller Layer
SQS message from vendor → `gen_stream_messages_demo()` function

### Service/Facade Layer
**`gen_stream_messages_demo()` Processing Algorithm:**

1. **Initialization:** Connect to Redis and MySQL; load configuration; parse SQS event payload (`to`, `from`, `body`, `source`, `last_message`, `event_id`, `chat_id`)

2. **Process Locking:** Generate UUID as process ID → store in Redis key `Trial-buddy-{to}-pId` (TTL: 48 hours) to prevent duplicate processing of concurrent messages

3. **Message Batching:**
   - Append incoming message to Redis list `Trial-buddy-{to}-messages`
   - Fetch and concatenate all queued messages into single string for unified processing
   - Wait 3 seconds between outgoing WhatsApp messages to prevent rate limiting

4. **User Identification:**
   - Call Eklavya API `GET /eklavya/v1/student/fetch-from-phone` with phone number
   - If no student found (new user): fetch platform country details, match dial code, build `extra_data` payload with `student_ids`, `parent_id`, `from_number`, `phone`, `country_id`

5. **Conversation State:**
   - Query `conversation` table for active session: `user_id` + `source` match + created within last 48 hours (2880 minutes)
   - If no active session → generate new UUID for conversation

6. **Context Windowing:**
   - Query `message` table: retrieve **last 15 active messages** for `conversation_id`
   - Prevents LLM token overflow

7. **AI Orchestration:**
   - Append new concatenated message to `chat_history` array
   - Insert placeholder record in `message` table
   - Send `chat_history` to AWS Bedrock (Claude model)
   - Bedrock executes tool calls as needed (booking, rescheduling)

8. **Finalization:**
   - UPDATE `message` table with AI response
   - Return response object: `{ textArray, messageId, conversationId }`

### High-Level Design (HLD)
- Asynchronous event-driven: SQS messages from communication vendors → processing function
- Redis: ephemeral state, concurrency lock, message queue per user
- MySQL: durable conversation and message history
- AWS Bedrock (Claude): LLM engine for NLU and tool use
- Conversation window: 48 hours; context window: last 15 messages
- 3-second delay between WhatsApp messages to avoid rate limits

## External Integrations
- **AWS Bedrock (Claude model):** LLM for natural language understanding, response generation, and tool calls
- **Communication Vendors (Kaleyra, Hermes, Snachar):** Trigger SQS messages when users send messages; receive outgoing responses
- **WhatsApp / iMessage / Web Chat:** Delivery channels for Niki's responses

## Internal Service Dependencies
- Eklavya (Student Service): `GET /eklavya/v1/student/fetch-from-phone` for user identification
- Booking APIs (Tryouts): Tool calls for booking and rescheduling demo classes
- Redis: `Trial-buddy-{to}-pId` (process lock), `Trial-buddy-{to}-messages` (message queue)
- MySQL: `conversation` and `message` tables

## Database Operations

### Tables Accessed

**`conversation`:**
| Column | Notes |
|--------|-------|
| id | UUID |
| user_id | Parent/user identifier |
| source | Platform (WhatsApp, iMessage, Web Chat) |
| created_at | Used to check 48-hour activity window |

**`message`:**
| Column | Notes |
|--------|-------|
| id | PK |
| conversation_id | FK → conversation |
| input | User's message text |
| prev_message_id | For conversation threading |
| response | AI response text |
| active | boolean |

### SQL / ORM Queries
- SELECT `conversation` WHERE `user_id` AND `source` AND `created_at > NOW() - 2880 min`
- SELECT last 15 `message` records WHERE `conversation_id` AND `active = true` ORDER BY created_at DESC LIMIT 15
- INSERT placeholder `message` record before Bedrock call
- UPDATE `message.response` after Bedrock returns

### Transactions
N/A — Message insert and update are sequential but not wrapped in explicit transactions.

## Performance Analysis

### Good Practices
- Process locking via Redis UUID prevents duplicate processing of rapid concurrent messages
- Message batching concatenates rapid-fire messages into a single Bedrock call, reducing LLM invocations
- Context window limited to 15 messages prevents token overflow and keeps latency low

### Performance Concerns
- 3-second delay between outgoing WhatsApp messages adds latency for multi-message responses
- Redis TTL of 48 hours for process lock key could cause stale lock if process crashes mid-execution

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Process lock TTL = 48 hours — if a processing crash occurs, the lock may block new messages for up to 48 hours |
| Low | Context window of 15 messages may lose important context in long-running conversations |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Reduce process lock TTL from 48 hours to a short per-message TTL (e.g., 30 seconds) and use a separate active-conversation TTL
- Add a dead-letter queue for failed SQS message processing

### Month 1 (Architectural)
- Implement conversation summarization for sessions exceeding 15 messages to maintain context without exceeding token limits
- Add multi-vendor routing logic to support additional communication channels

## Test Scenarios

### Functional Tests
- New user sends first message → `conversation` record created, user identified via phone lookup
- Existing user sends message within 48 hours → existing conversation used
- User sends 3 rapid messages → all batched and processed as one Bedrock call
- Booking tool call → verify booking created in Tryouts service
- Reschedule tool call → verify booking updated with new time

### Performance & Security Tests
- Verify process lock prevents duplicate processing for concurrent SQS deliveries
- Benchmark Bedrock response time with 15-message chat history context

### Edge Cases
- Phone number not found in Eklavya → new user flow proceeds correctly
- Conversation older than 48 hours → new session started
- Bedrock returns tool call error → graceful fallback response to user
- WhatsApp rate limit hit (3-second delay insufficient at high volume)

## Async Jobs & Automation
- **SQS Consumer (`gen_stream_messages_demo`):** Primary async trigger from communication vendors; processes each incoming user message
- **3-second WhatsApp delay:** Built-in rate limiting between consecutive outgoing messages to the same user
