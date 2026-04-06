---
title: WhatsApp TrialBuddy - Partial Lead
category: product-prd
subcategory: student-lifecycle
source_id: 92af2043-615d-4755-a0fe-1b1f78bb636f
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# WhatsApp TrialBuddy - Partial Lead

## Overview

The WhatsApp TrialBuddy Partial Lead feature addresses a critical gap in BrightCHAMPS's lead funnel: of every 49 WhatsApp marketing conversations initiated, only 1 converts to a full lead. The remaining 48 conversations drop off before all mandatory fields are collected — and because no "partial lead" state exists in the current system, these contacts are completely lost. The parent's verified phone number, course interest, and campaign attribution data (UTM parameters) all vanish with the abandoned conversation.

This feature introduces a Partial Lead state in the CRM that is created automatically 15 minutes after a WhatsApp conversation begins if the user has not yet converted to a full lead. The system stores all available metadata from the conversation (conversation ID, phone, course ID, UTMs), assigns a scout (sales agent) for manual follow-up, and continues to track the contact's journey. If the user later returns and completes all mandatory fields, the Partial Lead is automatically promoted to a full Lead by the Full-Lead Upgrader service.

The feature also handles cross-course scenarios (same phone number messages a different BrightCHAMPS course number), return-user sessions (user returns after 48+ hours), and UTM attribution preservation — ensuring that campaign data is never lost regardless of whether the user completes the demo booking in the first session.

## Problem Statement

BrightCHAMPS runs WhatsApp marketing campaigns that initiate TrialBuddy conversations with prospective parents. The current conversion rate is approximately 1 full lead per 49 conversations (roughly 2%). The 48 abandoned conversations leave no trace in the CRM — no partial profile, no phone number for follow-up, no attribution data for campaign analysis. This represents a massive loss of qualified intent signals and marketing investment. Without a partial lead capture mechanism, scouts cannot follow up, marketing cannot measure campaign efficiency, and the business cannot recover any value from the 98% drop-off rate.

## User Stories

- As a BrightCHAMPS scout, I want to be assigned partial leads with verified phone numbers and specific course tags within 15 minutes of conversation start, so that I can follow up proactively and convert them into full leads.
- As a marketing manager, I want UTM parameters (source, campaign, term) saved to the CRM from the first WhatsApp message, so that campaign attribution data is never lost even when users drop off before completing the flow.
- As a system, I want to automatically upgrade a partial lead to a full lead when all mandatory fields are collected, so that the CRM remains accurate and scouts are notified without manual data entry.
- As a returning user who left a conversation 48+ hours ago, I want my new message to re-attach to my existing open partial lead inquiry, so that the scout has my context and I don't have to start over from scratch.
- As a user who is inquiring about multiple BrightCHAMPS courses, I want each course inquiry tracked separately, so that the right scout for each course can follow up with me independently.

## Feature Scope

### In Scope

- Automatic metadata capture at conversation start: `conversation_id`, `phone_id`, `wa_id`, `course_id`, and UTM parameters
- T+15 minute scheduler to check for full lead conversion and create a `PartialLead` CRM record if not converted
- Scout assignment based on course routing at the point of partial lead creation
- Course-specific partial lead creation (same phone number messaging a different BrightCHAMPS course number = new partial lead for that course)
- Return-user handling: if a user returns after 48 hours and the backend re-opens the chat via template, attach to existing OPEN partial lead or create a fresh one
- Full-Lead Upgrader: listens for all mandatory fields and promotes the partial lead to a full Lead, copies UTM parameters, creates analytics events
- UTM mapping fetched and stored based on the first received message
- Analytics event tracking: `partial_lead_created`, `partial_lead_promoted`, `partial_lead_closed`

### Out of Scope

- Full lead qualification and demo booking (handled by the main TrialBuddy flow)
- Inbound WhatsApp flows outside the Meta billing session context
- Opt-out / STOP handling (handled by the broader WhatsApp platform layer)
- Non-WhatsApp channels (web chat, Zalo, etc.)
- Detailed UI screens (this is a backend + CRM workflow; no parent-facing UI changes)

## Functional Requirements

1. **Conversation Metadata Capture**
   - At the moment the first inbound user message opens a Meta billing session, the system must store: `conversation_id`, `phone_id`, `wa_id`, `course_id`, and all UTM parameters (`utm_source`, `utm_campaign`, `utm_term`).
   - UTM parameters must be fetched and mapped based on the first received message from the user.
   - Acceptance criteria: All six fields stored within 5 seconds of the first inbound message; verified in database for every new conversation.

2. **T+15 Minute Partial Lead Scheduler**
   - A scheduler must run exactly 15 minutes after conversation start.
   - If a full lead already exists for the phone number: do nothing.
   - If no full lead exists: create a `PartialLead` record in the CRM with the captured metadata, tag the course, and assign a scout.
   - Acceptance criteria: Scheduler fires within ±30 seconds of T+15 for all new conversations; partial lead record created correctly in CRM; scout assignment verified for each course.

3. **Scout Assignment by Course**
   - When a partial lead is created, a scout must be assigned based on the specific course associated with the WhatsApp number the user messaged.
   - Acceptance criteria: Scout assignment is course-specific; incorrect course routing tested and verified.

4. **Cross-Course Partial Lead Creation**
   - If the same phone number messages a different BrightCHAMPS course number (e.g., user who inquired about coding now messages the math number), the system must create a new, separate `PartialLead` record linked to the new course.
   - The existing partial lead for the original course must not be overwritten.
   - Acceptance criteria: Two distinct partial lead records visible in CRM when a single phone number contacts two different course numbers.

5. **Return User — Session Re-Attachment**
   - If a backend template message re-opens a chat after 48 hours (session expiry), the system must check `PartialLead.status` for that phone number.
   - If status is OPEN: attach the new conversation to the existing partial lead.
   - If status is CLOSED or the lead has been promoted to FULL: create a fresh partial lead.
   - Acceptance criteria: Both OPEN and CLOSED/FULL return-user scenarios tested and verified.

6. **Full-Lead Upgrader**
   - A listener must monitor all PartialLead records and detect when all mandatory CRM fields have been collected (whether by the bot, an agent, or the returning user).
   - Upon detecting full data completeness: promote the record to a full Lead, copy all UTM parameters, and create the `partial_lead_promoted` analytics event with `lead_id` and `time_to_promote_s`.
   - Acceptance criteria: Promotion triggered within 60 seconds of all mandatory fields being filled; UTM parameters present on the promoted Lead record; analytics event fired.

7. **Analytics Event Tracking**
   - The following events must be tracked and logged:
     - `partial_lead_created`: captures `course_id`, `utms`, `phone_mask`, `scout_id`
     - `partial_lead_promoted`: captures `lead_id`, `time_to_promote_s`
     - `partial_lead_closed`: captures `reason`, `closure_time_s`
   - Acceptance criteria: All three events visible in the analytics dashboard; event payloads contain all required fields.

## UX/UI Flows

This feature is a backend automation workflow. There is no graphical parent-facing UI. The flow is described from the system's perspective.

### Flow 1: New Conversation — Partial Lead Creation
1. A parent sends their first inbound WhatsApp message, opening a Meta billing session for a specific BrightCHAMPS course number.
2. System immediately captures and stores: `conversation_id`, `phone_id`, `wa_id`, `course_id`, and UTM parameters from the first message.
3. The TrialBuddy bot (or agent) attempts to collect full lead mandatory fields during the conversation.
4. T+15 minute scheduler fires:
   - Check: Does a full lead exist for this phone number? If YES: no action taken.
   - If NO: Create a `PartialLead` record in the CRM with all captured metadata; tag the course; assign a scout based on course routing.
5. `partial_lead_created` analytics event fired with `course_id`, `utms`, `phone_mask`, and `scout_id`.

### Flow 2: Full-Lead Promotion
1. Scout follows up or the parent returns and continues the TrialBuddy conversation.
2. All mandatory CRM fields are collected (bot, agent, or returning user).
3. Full-Lead Upgrader detects completeness and promotes the `PartialLead` to a full `Lead` record.
4. UTM parameters are copied from the partial lead to the new Lead record.
5. `partial_lead_promoted` analytics event fired with `lead_id` and `time_to_promote_s`.

### Flow 3: Cross-Course Inquiry
1. Parent who previously messaged the coding course WhatsApp number sends a first message to the math course WhatsApp number.
2. System detects the new `course_id` for the same `wa_id`.
3. System creates a new `PartialLead` record linked to the math course, assigns a math scout.
4. The original coding partial lead record is not modified.

### Flow 4: Return User — Session Re-Attachment (After 48 Hours)
1. Backend sends a template message to the parent to re-open the WhatsApp chat after session expiry.
2. Parent responds to the template and re-enters the conversation.
3. System checks `PartialLead.status` for this phone number:
   - If OPEN: attach the new conversation to the existing partial lead; scout retains context.
   - If CLOSED or FULL: create a fresh `PartialLead` record.

### Flow 5: Partial Lead Closure
1. Scout follows up on the partial lead and determines the lead cannot be converted (e.g., not interested, wrong number, no response after all retries).
2. Scout or system marks the partial lead as CLOSED with a reason.
3. `partial_lead_closed` analytics event fired with `reason` and `closure_time_s`.

## Technical Requirements

- **Meta WhatsApp Business API**: All inbound messages arrive via webhook from the Meta Business API. Each new conversation that opens a Meta billing session is the trigger for the partial lead capture flow. Each BrightCHAMPS course must own a dedicated WhatsApp number for course-specific routing to work.
- **T+15 Min Scheduler**: A background job must fire exactly 15 minutes after conversation start, check CRM for existing full lead, and create the `PartialLead` record if needed. Must be reliable and timezone-aware.
- **Prashashak CRM**: The `PartialLead` record must be created and maintained in the Prashashak CRM. All field updates (scout assignment, status changes, promotions) must sync in real time.
- **UTM Mapping Sheet / Analytics Integration**: UTM parameters must be extracted from the first inbound message and mapped using the defined UTM Analytics & Events schema. The mapping must be available before partial lead creation.
- **Full-Lead Upgrader Listener**: A backend listener or polling job must monitor PartialLead records for mandatory field completeness and trigger the promotion logic.
- **Course-to-WhatsApp-Number Mapping**: A routing table must exist that maps each BrightCHAMPS course to a specific WhatsApp number, enabling correct scout assignment at partial lead creation time.
- **Session Re-Attachment Logic**: The system must persist a `PartialLead.status` field that can be queried when a template message re-opens a chat after 48 hours.
- **Analytics Event Pipeline**: All three events (`partial_lead_created`, `partial_lead_promoted`, `partial_lead_closed`) must be fired with the correct payloads to the analytics pipeline.

## Non-Functional Requirements

- **Timing Precision**: The T+15 minute scheduler is the core trigger for partial lead creation. Any significant delay (>1 minute) in the scheduler could result in false negatives if a user converts between T+14 and T+16 minutes. Reliability is critical.
- **CRM Data Integrity**: UTM parameters must never be lost. They must survive the partial-to-full lead promotion and appear on the final Lead record.
- **Scalability**: The system must handle the full volume of WhatsApp marketing conversations; based on current data, ~49x the full-lead volume.
- **Phone Masking**: The `partial_lead_created` event must use a `phone_mask` rather than the raw phone number for analytics reporting (privacy requirement).
- **API Rate Limits**: Meta WhatsApp Business API rate limits must be respected; the system must not exceed allowed message rates.
- **Browser / Device Support**: Not applicable (backend service).
- **Accessibility**: Not applicable (no parent-facing UI in this feature).
- **Localization**: Not specified explicitly; UTM and metadata handling is language-agnostic.

## Success Metrics

| Event | Fields Tracked |
|-------|---------------|
| `partial_lead_created` | `course_id`, `utms`, `phone_mask`, `scout_id` |
| `partial_lead_promoted` | `lead_id`, `time_to_promote_s` |
| `partial_lead_closed` | `reason`, `closure_time_s` |

- **Primary KPI**: Number of partial leads created per day (captures the volume of previously lost contacts now being tracked).
- **Conversion Rate**: Percentage of partial leads promoted to full leads (`partial_lead_promoted` / `partial_lead_created`).
- **Time to Promote**: Average `time_to_promote_s` — how quickly scouts and bots convert partial leads to full leads.
- **Attribution Recovery**: Percentage of promoted full leads that have complete UTM data, confirming no attribution loss.
- **Baseline Problem Being Solved**: Current conversion rate is 1 full lead per 49 conversations (~2%). Any improvement to this ratio is a direct business win.

## Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| Full lead already exists at T+15 min check | Do nothing; no duplicate partial lead created |
| Same phone number messages a different course number | Create a separate, new partial lead for the new course; do not overwrite existing record |
| User returns after 48 hours and PartialLead.status is OPEN | Attach new conversation to existing partial lead |
| User returns after 48 hours and PartialLead.status is CLOSED or FULL | Create a fresh partial lead record |
| UTM parameters missing from the first message | Log the missing UTMs; create partial lead without UTM fields; flag for investigation |
| T+15 min scheduler fires but CRM is unavailable | Implement retry with exponential backoff; do not silently drop the event |
| Mandatory fields collected but Full-Lead Upgrader has not fired | Implement a secondary fallback check (e.g., T+30 min re-check for any partial leads with complete fields) |
| Scout assignment fails because course routing table has no mapping | Flag the partial lead as unassigned; alert system admin; do not leave the lead without follow-up |

## Dependencies

| Dependency | Owner | Notes |
|------------|-------|-------|
| Meta WhatsApp Business API | Tech | Core dependency; each course must have a dedicated WhatsApp number |
| Prashashak CRM | Backend / CRM Team | Partial lead records and scout assignment managed here |
| UTM Analytics & Events Schema | Analytics / Tech | UTM mapping matrix must be available before partial lead capture goes live |
| T+15 Min Background Scheduler | Backend Engineering | Core trigger mechanism; must be reliable and timezone-aware |
| Full-Lead Upgrader Service | Backend Engineering | Listener/polling job to detect full mandatory field completion |
| Course-to-WhatsApp-Number Routing Table | Product / Tech | Must be maintained and accurate for correct scout assignment |
| Scout / Sales Team | Sales / Operations | Scouts must be briefed on partial lead assignment workflow and follow-up SLA |
| TrialBuddy Conversational Flow | Product / Tech | Partial lead capture is dependent on the main TrialBuddy bot being live on WhatsApp |
