---
title: BrightChamps iMessage Customer Flow
category: product-prd
subcategory: student-lifecycle
source_id: 0efe6d73-e36c-4c86-be72-adb7199071c9
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# BrightChamps iMessage Customer Flow

## Overview

BrightChamps serves a large base of US customers who use iOS devices, and trial class attendance is a critical conversion event. Parents who book a demo class but forget to attend — or who cannot locate their joining link at the moment of the session — represent a significant drop in conversion rates. The BrightChamps iMessage Customer Flow addresses this by establishing an automated, conversational reminder sequence via Apple's iMessage platform, delivered through an automated account named "Niki" and supported by an AI conversational bot called "TrialBuddy."

The system is purpose-built for iOS users in the US English market and operates within Apple's strict iMessage quotas. It delivers a carefully timed sequence of reminder messages before, during, and immediately after each trial class slot. It handles multiple concurrent bookings with a consolidated digest format to avoid message fatigue, and it supports opt-out keywords to stay compliant with messaging best practices.

The core technical constraint of the system is Apple's hard cap of 50 new contacts per iMessage line per day. The product design accounts for this by managing a pool of iMessage lines and routing new contacts across available lines, with SMS and WhatsApp as fallback channels for non-iOS or quota-exceeded scenarios.

## Problem Statement

Parents who book trial classes for their children are at high risk of drop-off if they don't receive timely, relevant reminders via a channel they actively use. Email and WhatsApp are increasingly noisy channels, and iOS users on Apple devices tend to have higher engagement with iMessage. However, simply blasting messages risks getting the BrightChamps sending numbers blocked by Apple for spam-like behavior. The product needs a system that is both reliable and compliant — delivering reminders with the right timing and message variation to maximize attendance without triggering Apple's spam filters or exhausting the available line capacity.

## User Stories

- As a parent who just booked a trial class, I want to receive a friendly confirmation message immediately with class details, so that I have confidence my booking was received and I know what to expect.
- As a parent with multiple trial bookings, I want to receive a single consolidated daily digest of all upcoming classes, so that I am not overwhelmed by individual reminders for each booking.
- As a parent, I want to receive the Zoom joining link directly in the chat 10 minutes before class starts, so that I don't have to hunt for it in email when I'm trying to get my child ready.
- As a parent, I want to be able to text "STOP" or "MUTE" to the bot and have my preferences respected, so that I can control whether and how I receive messages from BrightChamps.
- As BrightChamps, I want the system to randomly rotate message templates and route contacts across available iMessage lines, so that our sending numbers are not blocked by Apple for repetitive or high-volume messaging.

## Feature Scope

### In Scope

- Automated iMessage reminder flow for US iOS customers booking trial (demo) classes
- Single/first booking message sequence: immediate confirmation, 24h reminder, 1h reminder, 10min reminder, 5min post-start nudge
- Multiple active bookings flow: immediate receipt acknowledgment, consolidated Daily Digest 24h before first slot, individual 30-minute reminders per class
- Reschedule flow: immediate rescheduled slot confirmation and regeneration of reminder sequence
- Consent and opt-out handling: keyword-based opt-out ("STOP", "PAUSE", "MUTE", "SNOOZE", "QUIET", "NO REMINDERS")
- Message template randomization to reduce spam detection risk
- Staggered multi-part message delivery with configurable delays
- Daily quota management: hard cap of 50 new contacts per iMessage line per day
- Multi-line routing: when one line hits 50, route to next available line
- Fallback to SMS or WhatsApp for non-iOS users or when quota is exceeded
- Attendance detection via Zoom response data to conditionally trigger the "didn't join" nudge
- Logging of sent template ID, booking ID, timestamp, and message delivery status

### Out of Scope

- Outbound iMessage flows for existing enrolled students (not trial/demo)
- Android or non-iOS device support for the iMessage channel specifically
- Non-English language variants (this flow is USA - English only)
- Manual agent escalation within iMessage (handled separately)
- Direct booking creation via iMessage chat

## Functional Requirements

1. **iMessage Applicability Check**
   - The system must check whether a customer's phone number is iMessage-capable before routing them to the iMessage channel.
   - This check must use the Linqblue API (or equivalent LQS data) and must confirm the user is an active iOS user within the past 90 days.
   - Acceptance criteria: Only confirmed iOS users receive messages via iMessage; others are routed to SMS/WhatsApp fallback.

2. **Quota Management and Line Routing**
   - The system must maintain a daily counter (`new_contacts_today`) per iMessage line, resetting at 00:00 ET.
   - The hard cap per line is 50 new contacts per day. When reached, new contacts must be routed to the next available line.
   - Total daily capacity is `L x 50`, where L is the number of available iMessage lines.
   - Acceptance criteria: Counter increments correctly; routing switches lines at exactly 50; existing threads on a full line continue unaffected.

3. **Message Template Randomization**
   - For each message event, the system must randomly select from a pool of approved message templates.
   - The same template must not be sent repeatedly to the same contact in the same session.
   - Acceptance criteria: Template selection is random and uniform across the pool; no consecutive identical templates for one contact.

4. **Single Booking Reminder Sequence**
   - Immediately after booking: Send Part 1 of the intro message, wait 10 seconds, send Part 2 asking if the parent received the email link.
   - Follow up with a consent message explaining opt-out keywords.
   - 24 hours before class: Send a reminder asking if the parent needs the joining link.
   - 1 hour before class: Send a nudge to check laptop and Zoom readiness.
   - 10 minutes before class: Send Part 1 alerting class is starting, wait 10 seconds, send Part 2 with the direct joining link.
   - 5 minutes after class start (if absent): Send Part 1 alerting that the teacher is waiting. If no attendance detected after 2 minutes, send Part 2 offering help.
   - Acceptance criteria: All messages fire at the correct relative times; Part 1 / Part 2 sequencing maintains the configured delay.

5. **Multiple Bookings Flow**
   - On an additional booking, send an instant receipt confirmation in the same existing thread.
   - 24 hours before the earliest upcoming slot, send a consolidated Daily Digest listing all upcoming classes with a dynamic `{{schedule_list}}`.
   - 30 minutes before each individual class, send a distinct reminder for that specific session.
   - Acceptance criteria: No duplicate threads created; digest accurately lists all upcoming slots; per-class 30min reminders fire independently.

6. **Reschedule Flow**
   - When a booking is rescheduled, the system must immediately cancel all pending reminders for the old slot.
   - An immediate rescheduled confirmation message must be sent.
   - The full reminder sequence must be regenerated for the new slot.
   - Acceptance criteria: Old reminders are cancelled before new ones are queued; no reminders fire for the old slot after reschedule.

7. **Opt-Out Handling**
   - The system must recognize the following keywords from the user: "STOP", "PAUSE", "MUTE", "SNOOZE", "QUIET", "NO REMINDERS".
   - On receiving "STOP", the system must tag the contact as `opt_out` and suppress all future outreach on the channel.
   - Other pause keywords may trigger a temporary reduction in message frequency.
   - Acceptance criteria: Opt-out tag persists; no messages are sent to `opt_out` contacts.

8. **Data Logging**
   - The system must log: customer identifier, template ID sent, booking ID, sent timestamp, and message status (failed/delivered/blocked/read).
   - Acceptance criteria: All outbound messages have a corresponding log record; status is updated as delivery receipts are received.

## UX/UI Flows

### Flow 1: Single Booking — Full Reminder Sequence

1. Parent completes a trial class booking.
2. System checks if the parent's number is iMessage-capable (via Linqblue API).
3. If yes and quota not exceeded: system assigns the parent to an available iMessage line and increments `new_contacts_today`.
4. **Immediate (T+0):** System sends Part 1 of the intro message (randomly selected template). After 10 seconds, sends Part 2 asking if the parent received the email link. A consent/opt-out message follows.
5. **T-24h before class:** System sends a reminder asking if the parent needs the joining link dropped in the chat.
6. **T-1h before class:** System sends a readiness nudge (check laptop, check Zoom).
7. **T-10min before class:** Part 1 — alert that class is about to start. After 10 seconds, Part 2 — direct joining link is sent.
8. **T+5min after class start (if parent has not joined):** Part 1 — alert that the teacher is waiting. If no attendance detected after 2 minutes, Part 2 — offer help.

### Flow 2: Multiple Active Bookings

1. Parent already has an existing iMessage thread with the Niki account.
2. Parent books a second (or additional) class.
3. System sends an instant receipt confirmation message in the same existing thread.
4. **T-24h before the earliest upcoming slot:** System sends a consolidated Daily Digest with a `{{schedule_list}}` covering all upcoming classes.
5. **T-30min before each individual class:** System sends a distinct reminder specific to that class, with the joining link.
6. If two sibling slots are at the exact same time, a single merged message is sent referencing both students by name.

### Flow 3: Reschedule Flow

1. Booking is rescheduled (by parent or by BrightChamps ops).
2. System immediately cancels all pending reminder jobs for the original slot.
3. System sends an immediate reschedule confirmation message in the existing thread with the new date and time.
4. Full new reminder sequence (T-24h, T-1h, T-10min, T+5min) is queued for the new slot.

### Flow 4: Opt-Out Flow

1. Parent sends a keyword such as "STOP" in the iMessage thread.
2. System detects the keyword and tags the contact as `opt_out`.
3. System acknowledges the opt-out with a confirmation message.
4. All pending and future message jobs for this contact on this channel are suppressed.

## Technical Requirements

- **Linqblue API / LQS Integration:** Required to evaluate iMessage applicability for each customer's phone number and to confirm iOS device usage within the past 90 days. Must be queried at booking time before channel assignment.
- **Messaging Queue and Scheduler:** A robust job scheduler is required to queue messages at precise relative times (T-24h, T-1h, T-10min, T+5min) and support cancellation and regeneration of job queues on reschedule.
- **Multi-Line Management:** Backend must track the available iMessage line pool, the daily `new_contacts_today` counter per line, and route contacts to the next available line when the cap is reached.
- **Template Engine:** A template management system must store approved message templates with dynamic variable placeholders (`{{parent_first_name}}`, `{{course_name}}`, `{{schedule_list}}`, etc.) and support random selection from a pool per event type.
- **Zoom Attendance Data:** Integration with Zoom response data (or equivalent) to determine whether the parent joined the class. This is required to conditionally trigger the T+5min "didn't join" message only for absent parents.
- **TrialBuddy AI Bot:** An AI conversational bot must handle dynamic in-thread replies from parents (questions, reschedule requests, etc.) during and between reminder sequences.
- **Opt-Out State Storage:** A mapped database must store opt-out/pause states per contact and per channel, consulted before any outbound message is dispatched.
- **Logging Infrastructure:** A database table or log store must capture all outbound messages with: contact ID, template ID, booking ID, timestamp, and delivery status (failed/delivered/blocked/read).

## Non-Functional Requirements

- **Throughput:** The system must support daily messaging capacity of `L x 50` new contacts, where L is the number of active iMessage lines. All existing threads must continue regardless of new-contact quota limits.
- **Delivery Timing:** Scheduled messages must fire within an acceptable tolerance of their target time (e.g., within ±1 minute for the T-10min reminder).
- **Device Targeting:** The iMessage channel is exclusively for confirmed iOS users. All non-iOS users, and all iOS users who cannot be assigned a line, must receive an equivalent flow via SMS or WhatsApp fallback.
- **Localization:** This flow is for USA - English only. Message templates are in English; date/time formats follow US conventions. Timezone handling must default to ET for quota resets.
- **Spam Avoidance:** Message templates must be randomized per event type to avoid repetitive patterns. Prior contact history must be checked — if Part 1 of the intro was sent to this number previously, only Part 2 is sent on a new booking.
- **Data Retention:** Message logs (template ID, booking ID, status) must be retained for analysis and debugging.

## Success Metrics

- **Attendance Rate:** Improvement in trial class attendance rate for US iOS customers receiving the iMessage flow versus a control group on SMS/WhatsApp only.
- **Quota Adherence:** Zero incidents of iMessage line blocking due to exceeding Apple's 50-new-contacts/day limit.
- **Delivery Rate:** Percentage of messages with "delivered" or "read" status versus "failed" or "blocked" status.
- **Opt-Out Rate:** Percentage of contacts opting out; high opt-out rate may signal template quality or frequency issues.
- **Attendance Detection Accuracy:** Accuracy of the Zoom-based attendance check; false positives (sending "didn't join" to parents who did join) should be minimized.

## Edge Cases & Error Handling

- **Reschedule:** Cancel all pending reminders for the old slot immediately upon reschedule confirmation. Generate new reminder sequence for the new slot. Send immediate reschedule confirmation to the parent.
- **Opt-Out:** On receiving "STOP" or equivalent keyword, tag the contact as `opt_out` and suppress all future messages on the iMessage channel. Deliver an acknowledgment message.
- **Quota Limit Reached:** When the 50-new-contact daily cap is hit on a line, route new contacts to the next available line. If all lines are full, fall back to SMS or WhatsApp. Existing threads on the full line continue normally.
- **Simultaneous Sibling Bookings:** If two children in the same family have classes at exactly the same time, send a single merged reminder message that includes both children's names, rather than two separate messages.
- **Repeated Part 1 Message:** If the customer has previously received Part 1 of the intro message on the same number (from a prior booking), skip Part 1 and send only Part 2 on the new booking to avoid redundancy.
- **Zoom Data Unavailable:** If Zoom attendance data cannot be retrieved at T+5min, the system should have a fallback — either send the nudge anyway (conservative) or skip it (risk of missing absent parents). The configured fallback behavior should be documented and testable.
- **Message Delivery Failure:** If a message fails to deliver, the system must log the failure status and may retry once before escalating to a fallback channel.

## Dependencies

- **Linqblue API / LQS:** Core dependency for iMessage applicability checks. If this API is unavailable, the system cannot assign contacts to the iMessage channel and must default all traffic to SMS/WhatsApp.
- **Zoom API / Attendance Data:** Required for the conditional T+5min absent-parent nudge. Inaccurate or delayed Zoom data will affect the quality of attendance detection.
- **Apple iMessage Line Pool:** The daily capacity of the system is directly proportional to the number of iMessage lines provisioned. Adding capacity requires acquiring and provisioning additional Apple iMessage lines.
- **TrialBuddy AI Bot:** The conversational AI that handles dynamic in-thread responses from parents. Must be maintained and updated separately.

### Teams Involved

| Team | Role |
|---|---|
| Engineering / Backend | Line routing logic, Linqblue integration, Zoom integration, scheduling system |
| AI Team | TrialBuddy bot management and dynamic response handling |
| Marketing / CRM | Template creation and approval, opt-out compliance |
| QA | End-to-end flow testing including edge cases (reschedule, opt-out, quota overflow) |
