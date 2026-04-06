---
title: HotLead Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: 534cbc50
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# HotLead Flow

## Overview
A hot lead is a demo student identified by the teacher as having high purchase intent. The teacher flags the lead via the `POST /hotlead` API; the system routes the lead to a Slack channel via a weighted algorithm; the first SM to claim it wins the lead. Unclaimed leads "jump" to fallback channels (up to 3 times).

## API Contract
**`POST /hotlead`** (Tryouts service)
- **Request Body:** `{ "classId": "string" }`
- **Trigger:** Teacher clicks "Hot Lead" button on teacher dashboard

**`POST /webhook`** (Slack callback)
- **Content-Type:** `application/x-www-form-urlencoded`
- **Payload:** `{ "classId": "string", "slackUserId": "string" }`
- Called when SM clicks "Claim to get link" in Slack

**`GET https://slack.com/api/users.info`**
- Resolves Slack user ID to SM email address

**`GET /prabandhan/v1/hotlead/channels/filters`**
- Query: `countryId`, `languageId`, `utmSource`, `courseId`, `fallback`
- Returns channel assignment mapping

## Logic Flow

### Controller Layer
- `POST /hotlead`: receive `classId`, fetch student/teacher details, route to Slack
- `POST /webhook`: receive Slack claim callback, resolve SM email, assign deal

### Service/Facade Layer
**Hot Lead Flagging:**
1. Teacher submits `POST /hotlead` with `classId`
2. Fetch student details from Tryouts, Eklavya (student attributes: course, language, grade, country, registration page)
3. Fetch teacher details from Dronacharya
4. Route to Slack channel via vector distance algorithm (see `hot-lead-channel-assigned-algorithm.md`)
5. Post Slack notification to selected channel with "Claim to get link" button

**Claim Mechanism:**
1. SM clicks "Claim" button → Slack sends `POST /webhook` with `classId` + `slackUserId`
2. System resolves SM email via `GET https://slack.com/api/users.info` with `slackUserId`
3. If lead already claimed → send DM to second SM: "Already claimed"
4. If first claim:
   a. Update deal owner in CRM to claiming SM
   b. Send private DM to SM with Zoom meeting link + class details
   c. Update public Slack message: "Claimed by @[SM name]"

**Jump Logic (Fallback):**
- If lead not claimed within 2 minutes:
  - Re-trigger notification to same channel OR route to `group_hotlead_channel_fallbacks` table
  - Maximum 3 jumps allowed
  - After max jumps: lead handled by default process

**Post-Demo SNS/SQS Deal Creation (parallel to hotlead):**
- Teacher's feedback submission (marking class "Successful") → SNS → Prabandhan SQS
- `prabandhan-class-completion-flow` Lambda allocates SM + creates Zoho deal

### High-Level Design (HLD)
```
Teacher clicks "Hot Lead" button
  → POST /hotlead (classId)
      → Fetch student/teacher from Tryouts + Eklavya + Dronacharya
      → Channel routing (vector distance algorithm)
      → POST to Slack channel (with Claim button)

Claim button clicked (SM)
  → POST /webhook {classId, slackUserId}
      → GET slack.com/api/users.info → SM email
      → IF already claimed → DM "Already claimed"
      → IF first claim:
          → Update CRM deal owner → claiming SM
          → DM SM: Zoom link + class details
          → Update public Slack msg: "Claimed by @SM"

No claim within 2 minutes → JUMP
  → Re-trigger to same or fallback channel (max 3 jumps)

Class marked Successful → SNS → Prabandhan Lambda
  → Allocate SM via group filters
  → Create Zoho deal (Deal stage: Demo Completed)
  → Append notes (WhatsApp + Dashboard links)
```

## External Integrations
- **Slack API:**
  - `POST` to channel webhook (hot lead notification with interactive button)
  - `GET https://slack.com/api/users.info` (resolve Slack user ID to email)
  - DM to claiming SM
- **Zoom:** Meeting link included in SM's DM (fetched from class details)

## Internal Service Dependencies
- **Tryouts:** `POST /hotlead` handler, booking/class data
- **Eklavya:** Student profile attributes (course, language, grade, country)
- **Dronacharya:** Teacher details
- **Prabandhan:** Channel routing, `db_crm_deals`, `hotlead_channels`, `group_hotlead_channnel_mappings`, `group_hotlead_channel_fallbacks`, `crm_users`

## Database Operations

### Tables Accessed
- `hotlead_channels` — Slack channel info and weightages
- `group_hotlead_channnel_mappings` — Group-to-channel assignments
- `group_hotlead_channel_fallbacks` — Fallback channels for JUMP
- `crm_users` — SM email → owner ID mapping
- `db_crm_deals` — Deal storage after claim

### SQL / ORM Queries
- SELECT `hotlead_channels` WHERE `id IN (?)` (channel details + weights)
- UPDATE `hotlead_channels` SET `recent_count = recent_count + 1`
- SELECT `group_hotlead_channel_fallbacks` WHERE `primary_channel_id = ?`
- UPDATE `db_crm_deals` SET `owner_id = ?` WHERE `booking_uuid = ?`

### Transactions
- Claim operation: check if already claimed + set claimer must be atomic (to prevent race between concurrent claimers)

## Performance Analysis

### Good Practices
- First-to-claim model maximizes SM motivation and speed of response
- Slack DM with Zoom link provides immediate actionable information to claiming SM
- Jump logic ensures hot leads are never permanently unattended

### Performance Concerns
- Race condition on simultaneous claims: two SMs click at exactly the same time — atomicity of claim check is critical
- Slack API calls introduce external latency (channel post + DM)
- Jump timer (2 minutes) requires a scheduled job or delayed SQS message

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Claim atomicity — concurrent claims could result in two SMs receiving Zoom link |
| Medium | Jump timer requires reliable delayed execution — SQS delay or scheduled Lambda |
| Low | Maximum 3 jumps is hardcoded — not configurable per group |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Implement Redis-based distributed lock on hot lead claim (key: `classId`, TTL: 30 seconds)
- Add configurable `max_jumps` per group in database

### Month 1 (Architectural)
- Move jump timer to SQS message delay (configurable per channel) instead of scheduled Lambda
- Add hot lead claim analytics dashboard (claim rate, time-to-claim, jump rate per channel)

## Test Scenarios

### Functional Tests
- Teacher flags hot lead → Slack notification in correct channel for student's country/course
- SM claims → DM received with Zoom link → public message updated to "Claimed by @SM"
- Two SMs click simultaneously → only one receives Zoom link, second gets "Already claimed"
- No claim in 2 min → JUMP → re-notified in same or fallback channel
- After 3 jumps → lead falls to default allocation

### Performance & Security Tests
- 10 concurrent hot leads across the same Slack channel — routing correctness and performance
- Slack API rate limits under hot lead burst

### Edge Cases
- No eligible SM in any channel after 3 jumps → escalation path
- Slack `users.info` returns no email for `slackUserId` — error handling
- Teacher flags same class as hot lead twice — deduplication
