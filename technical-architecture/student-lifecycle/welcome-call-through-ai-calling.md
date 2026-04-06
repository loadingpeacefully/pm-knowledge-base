---
title: Welcome Call Through AI Calling
category: product-prd
subcategory: student-lifecycle
source_id: ca2a2043-1374-4f6c-bfaf-0c9f684e2f1d
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Welcome Call Through AI Calling

## Overview

The Welcome Call Through AI Calling feature automates the outbound welcome call that was previously handled manually by BrightCHAMPS pre-sales representatives. Immediately after a parent books a demo class on the BrightCHAMPS website, an AI voice agent (persona: "Niki") is triggered to call the parent, confirm the demo booking details, pitch same-day or next-day slots where relevant, qualify the lead, handle basic FAQs, and manage reschedule requests — all in real time via a natural conversational voice flow.

The AI calling system uses Retell AI as the underlying voice technology and integrates tightly with the Prashashak internal CRM and the reschedule API. Call outcomes, full transcripts, and CRM field updates are synced automatically post-call. If the AI cannot resolve a query, detect a negative sentiment, or a lead remains unresponsive after a maximum of 5 retry attempts, the system escalates to a human pre-sales representative.

The initial rollout targets the USA market. Core business goals are to improve the demo Joining % from 25% to 30% and the demo Completion % from 80% to 85%, while reducing the manual bandwidth burden on the pre-sales team and improving lead engagement velocity.

## Problem Statement

Human pre-sales representatives are unable to make instant welcome calls to every parent who books a demo, due to limited bandwidth and team capacity. This leads to delayed first contact and a degraded first impression. Additionally, there is no mechanism to reliably retry calls when a parent does not answer — meaning leads that could be qualified and confirmed are lost due to unreachable timing. The AI calling feature solves both problems: it places the welcome call instantly upon form submission and automatically retries at configured intervals until a connection is made or the maximum attempt threshold is reached.

## User Stories

- As a parent booking a demo, I want to receive an immediate, friendly welcome call confirming my demo details, so that I feel assured about the credibility and professionalism of BrightCHAMPS before the session.
- As a busy parent, I want to be able to reschedule my demo instantly during the AI call itself by selecting a new slot, so that I can adapt to changes in my schedule without navigating a separate portal.
- As a parent, I want the AI to only call me between 9 AM and 8 PM my local time, so that my family is not disturbed during off-hours or early mornings.
- As a pre-sales representative, I want the AI to automatically update the CRM with the lead's urgency, fitment score, and qualification responses, so that I have full context when conducting any necessary follow-ups.
- As a marketing manager, I want UTM attribution data (source, campaign, term) captured and saved to CRM at the moment of the call trigger, so that campaign performance can be accurately attributed even for partially-completed lead flows.

## Feature Scope

### In Scope

- AI-driven outbound welcome call triggered immediately after demo form submission (within calling hours)
- Conversational script covering: greeting, demo confirmation, same-day / next-day slot pitch, lead qualification questions, FAQ handling, and warm close
- Real-time reschedule capability during the call via Prashashak Reschedule API
- Automated retry scheduler: retries at T+15 min, T+1h, T+6h, and T+24h, strictly within 9 AM–8 PM local time
- CRM (Zoho / Prashashak) update with call transcript, call outcome, qualification data, and UTM parameters
- Exclusion rules to prevent duplicate calls for already-rescheduled, already-called, or AI-calling-generated leads
- Human escalation flow for complex queries, negative sentiment, or AI confidence failures
- Initial rollout for USA market; timezone enforcement is mandatory

### Out of Scope

- Inbound call handling
- Post-enrollment welcome calls (this targets pre-demo booking calls only)
- Non-USA markets in the initial rollout (future phases planned)
- Full language localization beyond English (initial scope)
- Live dashboard for ops to monitor AI call performance (implied future tooling)

## Functional Requirements

1. **Instant AI Call Trigger**
   - The system must trigger the AI call immediately upon demo form submission if within calling hours (9 AM–8 PM local).
   - If submitted outside calling hours, the call must be scheduled for 9 AM the following business day.
   - Acceptance criteria: Call initiated within 60 seconds of form submission during business hours; deferred calls fire at 9 AM local time next day.

2. **Calling Hours Enforcement**
   - No call (initial or retry) must be placed outside 9 AM–8 PM local time of the lead's timezone.
   - Acceptance criteria: Timezone detection verified for US time zones; all calls blocked outside the defined window.

3. **Retry Call Scheduler**
   - If a call goes unanswered, the system must retry at: T+15 min, T+1h, T+6h, T+24h.
   - Each retry must respect the 9 AM–8 PM local time constraint.
   - Maximum of 5 total call attempts before the lead is flagged for manual follow-up.
   - Acceptance criteria: Retry schedule verified with timezone-aware job scheduler; max 5 attempts enforced.

4. **Dynamic Conversational Script**
   - The AI must cover: introduction (as "Niki" from BrightCHAMPS), demo confirmation (date, time, child's name, subject), slot pitch (same-day before 12 PM or next-day after 12 PM), qualification questions (urgency, timeline, goals), FAQ handling (pricing, structure), and a warm closing.
   - Acceptance criteria: Script reviewed and approved by Business/Product stakeholders; all branches tested in UAT.

5. **Slot Pitch Logic**
   - Leads booked before 12 PM local time: AI must pitch earlier same-day slots.
   - Leads booked after 12 PM local time: AI must pitch next-day slots.
   - Acceptance criteria: Pitch timing logic verified in QA with mocked booking timestamps across both scenarios.

6. **Real-Time Reschedule via API**
   - If the parent requests a reschedule during the call, the AI must fetch available slots from the Prashashak Reschedule API, offer options, confirm the parent's choice, and update the CRM instantly.
   - Acceptance criteria: Reschedule confirmed during the live call; CRM updated within 10 seconds of confirmation; lead flagged as rescheduled and excluded from retry queue.

7. **CRM Data Sync**
   - All of the following must be synced to Zoho / Prashashak CRM post-call: call transcript, call outcome (completed / no-answer / escalated / rescheduled), qualification data (urgency, fitment, preferences), and UTM parameters from the original form submission.
   - Acceptance criteria: CRM record updated within 60 seconds of call end; all required fields populated.

8. **Exclusion Rules**
   - The system must NOT initiate a call if any of the following are true: the lead has already been rescheduled, the lead was generated by an AI calling campaign (to prevent loops), or the CRM already has a positive call log indicating a human rep already made contact.
   - Acceptance criteria: Exclusion logic tested against all three scenarios; no duplicate calls placed.

9. **Human Escalation Flow**
   - If the parent asks a question the AI cannot answer, expresses frustration, or sentiment is detected as negative, the AI must automatically trigger a handoff to a human pre-sales representative.
   - Acceptance criteria: Escalation tested with simulated negative-sentiment prompts; human agent notified within 30 seconds; conversation context passed in full.

10. **Partial Lead Handling**
    - If the AI cannot collect all mandatory CRM fields during the call (e.g., call dropped before qualification), the lead must be flagged as "Partial" and routed to a human for follow-up.
    - Acceptance criteria: Partial lead flag visible in CRM; assigned to a human queue within the same business day.

## UX/UI Flows

This feature is a voice-based automation. There is no graphical UI for the end user (parent). The flows are conversational sequences delivered over a phone call.

### Flow 1: Welcome Call Trigger
1. Parent submits the BrightCHAMPS demo booking form.
2. System checks current local time for the lead's timezone.
3. If within 9 AM–8 PM: AI call is placed immediately (within 60 seconds).
4. If outside 9 AM–8 PM: Call is scheduled for 9 AM the following morning.

### Flow 2: Greeting and Slot Pitch
1. Call connects. AI introduces itself: "Hi, this is Niki from BrightCHAMPS!"
2. AI confirms the booked demo: date, time, child's name, subject.
3. AI pitches an earlier/same-day slot (if booking was before 12 PM) or next-day slot (if after 12 PM).
4. If parent accepts: AI calls the Reschedule API, allots the new slot, and confirms.
5. If parent declines: AI proceeds to the qualification and FAQ section.

### Flow 3: Lead Qualification and FAQs
1. AI explains the purpose of the demo class.
2. AI asks soft qualification questions: "What inspired you to look into this for [child's name]?", "What's your timeline?", "What are your goals?"
3. AI captures responses and syncs to CRM.
4. AI asks if the parent has any questions.
5. If parent asks about pricing or structure: AI handles with a scripted response.
6. If parent asks something complex or is frustrated: AI triggers Human Escalation Flow.
7. AI closes the call warmly.

### Flow 4: Reschedule Flow
1. Parent requests a new demo time during the call.
2. AI fetches available slots from the Prashashak Reschedule API.
3. AI offers 2–3 slot options verbally.
4. Parent selects a slot.
5. AI confirms the new slot, updates CRM, and flags the lead as "Rescheduled" (excluded from retry queue).

### Flow 5: Retry Flow (Unanswered Call)
1. Call goes unanswered.
2. System schedules next retry within calling hours: T+15 min, then T+1h, T+6h, T+24h.
3. After 5 total failed attempts: Lead is flagged for manual follow-up by the pre-sales team.

### Flow 6: Human Escalation Flow
1. AI detects negative sentiment, complex query, or drops below confidence threshold.
2. AI says: "Let me connect you with one of our team members right now."
3. Human pre-sales rep is notified with full call transcript context.
4. CRM is updated with escalation status.

## Technical Requirements

- **Retell AI**: Primary AI calling vendor. The entire voice agent experience is built and deployed through Retell AI. Reliability and uptime of Retell AI is a direct dependency.
- **Zoho / Prashashak CRM Integration**: CRM must receive real-time updates for all call outcomes, transcripts, qualification data, and UTM parameters. Real-time sync is required (not batch).
- **Prashashak Reschedule API**: Must be integrated to fetch available teacher slots and process rescheduling during the live call. Response time must be fast enough to not break the conversational flow (target: < 3 seconds).
- **UTM Attribution Mapping**: UTM parameters (`utm_source`, `utm_campaign`, `utm_term`) from the form submission must be passed to the call trigger and mapped to the CRM record.
- **Timezone Detection**: The system must accurately detect and enforce the lead's local timezone (9 AM–8 PM window). Incorrect timezone detection would result in calls placed outside permitted hours.
- **Retry Job Scheduler**: A background job scheduler must manage the retry queue with timezone-aware timing logic.
- **CRM Pre-Check**: Before any call is triggered, the system must query the CRM to check for existing positive call logs or rescheduled status — to enforce exclusion rules.
- **Call Transcript Storage**: Full call audio recordings and transcripts must be stored in the CRM for quality review and training purposes.

## Non-Functional Requirements

- **Voice Quality**: The AI voice (via Retell AI) must have a clear voice and accent appropriate for the USA market. Poor voice quality will directly degrade parent trust.
- **Call Timing**: Call placed within 60 seconds of form submission during business hours.
- **CRM Sync Latency**: Real-time CRM sync required; updates within 60 seconds of call completion.
- **Retry Logic Precision**: Retry scheduler must correctly honor timezone-aware 9 AM–8 PM boundaries; off-hour calls are a compliance/UX risk.
- **Localization**: Initial scope is USA (English). Future rollout to other regions requires localized scripts and timezone support.
- **Accessibility**: Not applicable for voice calls; however, transcript storage enables post-hoc accessibility review.
- **Maximum Call Attempts**: Hard cap of 5 total attempts per lead; system must not exceed this under any circumstances.

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Demo Joining % | 25% | 30% |
| Demo Completion % | 80% | 85% |
| AI to Human Escalation Rate | Tracked | Minimize |

- **Primary KPIs**: Demo Joining % and Demo Completion % for the USA market.
- **AI to Human Escalation Rate**: Tracked to identify edge cases or script gaps where AI cannot resolve queries independently.
- **CRM Data Quality**: Percentage of leads where all mandatory CRM fields are populated post-call.

## Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| Call goes unanswered | Retry at T+15m, T+1h, T+6h, T+24h within calling hours; flag for manual follow-up after 5 attempts |
| Form submitted outside calling hours (9 PM, late night) | Schedule call for 9 AM local time next business day |
| Parent requests reschedule during the call | Fetch slots via Prashashak API, confirm new slot in real time, update CRM, exclude from retry queue |
| AI cannot answer a complex query | Trigger human escalation flow; pass full transcript context to the pre-sales rep |
| Parent expresses negative sentiment or frustration | Auto-escalate to human agent; flag CRM record accordingly |
| CRM already has a positive call log | Abort AI call trigger; do not duplicate outreach |
| Lead was generated by an AI calling campaign | Exclude from AI call trigger to prevent loops |
| Lead has already been rescheduled | Exclude from retry queue; no further AI calls |
| Prashashak Reschedule API is slow or unavailable | Apologize, note the request, and flag for human follow-up; do not leave the parent on hold indefinitely |
| Call drops mid-conversation before mandatory fields captured | Flag as Partial Lead; route to human follow-up queue |

## Dependencies

| Dependency | Owner | Notes |
|------------|-------|-------|
| Retell AI (AI Calling Vendor) | Tech (@Ankit Jat) | Core dependency; all voice AI delivered through this vendor |
| Prashashak Reschedule API | Backend / Prashashak Team | Required for real-time slot fetching and rescheduling during live calls |
| Zoho / Prashashak CRM Integration | Tech | Real-time sync required for all call outcomes, transcripts, and UTM data |
| UTM Attribution Mapping | Analytics / Tech | UTM parameters must flow from form submission to call trigger to CRM |
| Timezone Detection Service | Tech | Required to enforce 9 AM–8 PM calling hour rule per lead's local time |
| Retry Job Scheduler | Tech | Background job with timezone-aware scheduling logic |
| Human Pre-Sales Team | Pre-Sales | Must be available and trained to receive AI escalations and handle partial leads |
| Business Sign-off | Vishal Gupta | Business stakeholder approval required on script and metric targets |
| Product | Shivam Sharma, Paul | Product owners responsible for scope and acceptance |
| QA Sign-off | Divya G | Full regression across all flows, retry logic, exclusion rules, and escalation paths |
