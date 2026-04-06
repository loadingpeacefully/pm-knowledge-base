---
title: TrialBuddy AI-Powered Chatbot
category: product-prd
subcategory: student-lifecycle
source_id: 7f7e965f-e4d3-43d1-81c7-b1668d44e08f
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# TrialBuddy AI-Powered Chatbot

## Overview

TrialBuddy is an AI-powered chatbot built to automate and streamline the pre-trial and trial-day support experience for parents booking BrightCHAMPS trial classes. The current pre-sales and sales workflows are heavily manual: parents who face issues joining a trial class, lose their session link, or have questions about the class must contact a human representative. This creates a bottleneck where frontline sales and pre-sales staff spend significant time on repetitive, low-complexity queries rather than high-value selling activities.

TrialBuddy (persona: "Niki") acts as a first-responder chatbot across multiple touchpoints — WhatsApp, Zalo, the BrightCHAMPS landing page, the trial dashboard, blog pages, and interim pages. It handles the full range of pre-trial support queries: joining link retrieval, session troubleshooting, class rescheduling, re-trial booking for a new subject, and escalation to a human agent when needed.

The business impact is threefold: reduce human support dependency, increase the trial support query resolution rate, and drive a secondary lift in trial-to-enrollment conversion by eliminating friction in the trial experience. An estimated INR 18,00,000 revenue impact is attributed to this initiative.

## Problem Statement

Parents attending online trial classes often encounter friction at the last mile: they cannot find their Zoom/class link, they face browser or app compatibility issues, or they simply need to reschedule. The only resolution path today is to call or message a human agent. This drives up support volume with low-value queries, reduces the productivity of the sales and pre-sales teams, and creates a poor parent experience that can directly reduce the likelihood of enrollment. TrialBuddy exists to eliminate this dependency by providing instant, always-on, AI-driven resolution for the most common trial-support scenarios.

## User Stories

- As a parent who lost my trial class joining link, I want to ask the chatbot to resend it, so that I can access my child's session without waiting for a human agent to respond.
- As a parent facing technical difficulties with Zoom or my browser, I want to receive guided step-by-step troubleshooting from the bot, so that my child can join the class without missing the session.
- As a parent who missed a scheduled trial, I want to request a reschedule by providing a new preferred date and time to the bot, so that my child can still experience the BrightCHAMPS class at a convenient time.
- As a parent with a complex or unanswered query, I want the bot to automatically connect me to a live human agent after multiple failed attempts, so that I receive personalized help when the bot cannot resolve my issue.
- As a parent interested in trialing a second subject, I want the bot to guide me to the trial booking landing page and help me book a new slot, so that I can explore additional BrightCHAMPS offerings without navigating manually.

## Feature Scope

### In Scope

- AI chatbot (persona: Niki) deployed across WhatsApp, Zalo, BrightCHAMPS Landing Page (widget), Trial Dashboard, Student Dashboard, Blog pages (mobile only), and Interim pages
- Joining Support Flow: resend joining link, guide user to find it via WhatsApp/email/dashboard, and initiate email update with OTP if contact details are incorrect
- Troubleshooting Flow: step-by-step Zoom and browser troubleshooting (e.g., clear cache, use Chrome, update Zoom)
- Reschedule Flow (Prashashak Flow): capture preferred date/time and pass to Prashashak backend API, confirm rescheduling
- Re-Trial Booking Flow: guide parent to the trial booking landing page for a new subject
- Human Escalation Flow: automatically trigger live agent escalation after 3 failed bot interactions
- Dynamic option presentation (up to 6 clickable options per message)
- Auto-updating chat text input that reflects user selections (e.g., selected grade auto-fills as a natural sentence)
- Event tracking for all key bot interactions
- Knowledge base covering company info, courses, schedules, technical issues, and referrals

### Out of Scope

- Post-enrollment support queries
- Payment or billing-related queries
- Onboarding flows for enrolled students
- Desktop-specific experience on blog pages (mobile only for blogs)
- Localization beyond English and Zalo-region Vietnamese

## Functional Requirements

1. **Knowledge Base Integration**
   - The bot must be backed by a configured knowledge base covering BrightCHAMPS company information, courses, class schedules, technical troubleshooting steps, and referral programs.
   - Acceptance criteria: Bot must answer at least the top 20 most common trial-support queries accurately without escalation.

2. **Joining Link Retrieval**
   - When a parent reports they cannot find their joining link, the bot must immediately resend the link and guide them to locate it via WhatsApp, email, or the student dashboard.
   - If the parent's email/phone is incorrect, the bot must trigger an Email Update Flow that includes OTP verification to update contact details.
   - Acceptance criteria: Link resend must complete within one bot turn; OTP flow must complete in under 3 steps.

3. **Troubleshooting Flow**
   - Bot must present a sequential troubleshooting guide for common issues: Zoom not opening, camera/microphone not working, browser compatibility.
   - Troubleshooting steps must direct users to Chrome specifically.
   - After 3 failed resolution attempts, bot must auto-trigger Human Escalation Flow.
   - Acceptance criteria: All troubleshooting steps are presented in correct order with no dead ends.

4. **Reschedule Flow**
   - Bot must capture the parent's preferred new date and time slot.
   - Bot must call the Prashashak backend API to process the rescheduling request.
   - Bot must confirm the rescheduling with the parent in the same conversation thread.
   - Acceptance criteria: Rescheduling confirmation returned to parent within the same session; API integration tested end-to-end with Prashashak team.

5. **Re-Trial Booking Flow**
   - Bot must identify when a parent wants to trial a second subject and guide them to the trial booking landing page URL.
   - Acceptance criteria: Correct URL served; flow completes in under 3 bot turns.

6. **Human Escalation Flow**
   - Bot must detect an unresolved query after 3 interactions and offer a "Request Human Help" button.
   - On WhatsApp/Zalo: bot connects to live agent via platform messaging.
   - On Dashboard: bot displays a "Request Human Help" button.
   - Acceptance criteria: Escalation is never blocked; human agent receives full conversation context.

7. **Dynamic Options and Auto-Update**
   - Bot must present up to 6 contextual clickable options per message turn.
   - When a user selects an option (e.g., a grade or time slot), the chat text input must auto-update to reflect that choice as a natural sentence.
   - Acceptance criteria: Auto-update visible to user within 500ms of selection.

8. **Trigger Mechanisms**
   - Blog (mobile): chat widget must trigger on widget tap, 30% page scroll, 10 seconds on page, or exit intent.
   - Landing page (desktop): widget must open when the "Why BrightCHAMPS" heading enters the viewport.
   - Acceptance criteria: All triggers tested on target devices before release.

9. **Session Management**
   - Active session duration: 3 days.
   - Chat box must remain active and non-interruptive while user interacts with options or types.
   - Acceptance criteria: Session persists across page reloads within the 3-day window.

10. **Event Tracking**
    - The following events must be tracked with a `session_id` parameter: `chat_shown`, `widget_tapped`, `user_message_sent`, `bot_message_sent`, `user_selected_option`, `escalation_triggered`, `trial_booked`, `session_start`, `session_end`.
    - Acceptance criteria: All events visible in the analytics dashboard within 24 hours of implementation.

## UX/UI Flows

### Flow 1: Joining Support Flow
1. Parent messages the bot (or taps the widget) with a query about their joining link (e.g., "I can't find my class link").
2. Bot immediately resends the joining link in the conversation.
3. Bot presents options: "Find it on WhatsApp," "Find it in your Email," "Find it on the Dashboard."
4. If parent reports email is wrong: Bot initiates Email Update Flow — asks for correct email, sends OTP, verifies, and updates contact details in the system.
5. Bot confirms link has been resent to the updated contact and closes the flow.

### Flow 2: Troubleshooting Flow
1. Parent reports a technical issue (e.g., "Zoom is not opening," "I can't hear anything").
2. Bot categorizes the issue and presents a step-by-step guide (e.g., clear browser cache, switch to Chrome, update Zoom app).
3. Bot asks: "Did this resolve your issue?" after each major step.
4. If resolved: Bot confirms and closes the flow.
5. If unresolved after 3 attempts: Bot auto-triggers Human Escalation Flow.

### Flow 3: Reschedule Flow (Prashashak Flow)
1. Parent indicates they missed or need to reschedule their trial (e.g., "I missed my class").
2. Bot asks for the parent's preferred new date.
3. Bot asks for the preferred time slot (presents dynamic options).
4. Bot calls Prashashak backend API with the new date/time preference.
5. Bot confirms the new scheduled time to the parent in the same conversation.

### Flow 4: Re-Trial Booking Flow
1. Parent requests a trial for a different subject (e.g., "Can my child try coding?").
2. Bot identifies the intent as a new subject trial request.
3. Bot shares the trial booking landing page URL with instructions to choose subject, fill in details, and select a time slot.
4. Bot confirms the new booking once the parent completes the flow.

### Flow 5: Human Escalation Flow
1. Bot detects that a query remains unresolved after 3 interaction attempts.
2. Bot presents a "Request Human Help" button or message.
3. On WhatsApp/Zalo: parent is connected to a live human agent with full conversation context transferred.
4. On Dashboard: a "Request Human Help" CTA is displayed; human agent is notified with full context.

### Chat Widget Triggers (Blog / Landing Page)
- Blog (mobile): widget auto-opens on 30% scroll, 10 seconds on page, exit intent, or explicit widget tap.
- Landing Page (desktop): widget opens when "Why BrightCHAMPS" heading scrolls into view; expanded chat box is 320px x 520px (or 60% height x 20% width).

## Technical Requirements

- **WhatsApp API Integration**: Bot must send and receive messages via the WhatsApp Business API.
- **Zalo API Integration**: Bot must be deployed on the Zalo messaging platform for Vietnam region.
- **Prashashak Backend API**: The Reschedule Flow requires real-time integration with the Prashashak backend to fetch available time slots and confirm rescheduling. API contract must be agreed upon with the Prashashak team.
- **Knowledge Base System**: A structured knowledge base must be configured and maintained covering: company info, available courses, class schedules, technical troubleshooting guides, and referral program details.
- **Dynamic Options Engine**: Backend must support real-time generation and delivery of up to 6 contextual quick-reply options per bot turn.
- **Auto-Update Input**: Backend must push updated text to the chat input field when the user selects a dynamic option (e.g., selecting "3rd grade" populates "My child is in 3rd grade" in the input box).
- **Session Persistence**: Sessions must persist for 3 days, stored server-side and associated with a unique `session_id`.
- **Event Tracking Pipeline**: All tracked events must be sent with a `session_id` parameter to the analytics pipeline.
- **Widget Embedding**: Chat widget must be embeddable via a JavaScript snippet on landing pages, blog pages, and the trial/student dashboard.
- **Bot Response Latency**: Responses must appear without perceptible delay; target < 2 seconds per bot turn.
- **Slot Availability Query**: < 500ms (cached) for fetching available rescheduling slots from Prashashak.
- **Escalation Handoff**: Escalation to a human agent must be offered within 30 seconds of low-confidence/unresolved detection.

## Non-Functional Requirements

- **Tone and Persona**: Bot persona is "Niki" — friendly, supportive, confident, lightly casual. Responses must be concise and empathetic ("Spartan sentences" — no filler, no robotic language).
- **Session Duration**: Active session window is 3 days.
- **Device Support**: Full functionality on mobile and desktop for WhatsApp, Zalo, landing pages, and dashboards. Blog widget is mobile-only.
- **Browser Guidance**: Troubleshooting flows are designed around Chrome; users on other browsers should be guided to switch.
- **Widget Dimensions (Desktop)**: Expanded chat box: 320px x 520px or 60% height x 20% width.
- **Accessibility**: WCAG 2.1 AA standard practices should be applied for all widget interactions (not explicitly specified in source).
- **Localization**: English as primary language; Zalo deployment implies Vietnamese-language support for the Vietnam market.

## Success Metrics

| Metric | Goal |
|--------|------|
| Trial Support Query Resolution Rate | Increase (target % in progress) |
| Human Support Dependency | Decrease (target % in progress) |
| Trial-to-Enrollment Conversion | Secondary lift expected |
| Estimated Revenue Impact | INR 18,00,000 |

- **Primary KPI**: Percentage of trial-support queries resolved autonomously by the bot without human escalation.
- **Secondary KPI**: Reduction in volume of manual support tickets raised to the pre-sales/sales team.
- **Tertiary KPI**: Lift in trial-to-enrollment conversion rate attributed to reduced trial friction.

## Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| Bot cannot resolve a query after 3 attempts | Auto-trigger Human Escalation Flow; connect parent to live agent with full conversation context |
| Parent's email/phone on file is incorrect | Initiate Email Update Flow with OTP verification before resending the link |
| Prashashak API is unavailable during Reschedule Flow | Surface a fallback message asking the parent to try again; do not silently fail |
| Parent exits the chat mid-flow | Session persists for 3 days; parent can return and resume |
| User selects an option that matches no configured flow | Bot presents a clarifying question and surfaces the "Request Human Help" option |
| Widget fails to load on blog/landing page | Widget must fail gracefully without breaking the host page layout |
| Parent provides an unrecognized date format for reschedule | Bot asks for clarification with a sample format (e.g., "Please say a date like 'Monday 3pm'") |

## Dependencies

| Dependency | Owner | Notes |
|------------|-------|-------|
| Prashashak Backend API | Backend / Prashashak Team | Required for Reschedule Flow; API contract to be defined |
| WhatsApp Business API | Tech (@Ankit Jat) | Required for WhatsApp deployment |
| Zalo API | Tech | Required for Vietnam market deployment |
| Knowledge Base Configuration | Product / Business (@Shivam Sharma, @Paul) | Must be populated and reviewed before launch |
| Dynamic Options Engine (Back-End) | Tech (@Ankit Jat) | Required for contextual quick-reply options and auto-update |
| Analytics / Event Tracking Pipeline | Tech | Required for all 9 tracked events with session_id |
| Widget Embedding (Landing Page, Blog, Dashboard) | Tech + Design | Requires cross-team coordination for embed placement and trigger logic |
| Human Agent Escalation Queue | Customer Support / Sales / Pre-Sales | Agents must be trained and available to receive escalated conversations |
| QA Sign-off | QA Team | Full regression across all 5 flows and all platforms required before release |
