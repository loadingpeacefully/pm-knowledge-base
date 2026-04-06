---
title: BrightBuddy Additional Flows - Login & Class Joining Issues
category: product-prd
subcategory: student-lifecycle
source_id: cf58233e-a881-4571-b203-2b3bedd3e2fb
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# BrightBuddy Additional Flows - Login & Class Joining Issues

## Overview

Students frequently encounter two categories of friction during their learning journey: difficulty logging into the BrightChamps dashboard and problems joining live classes. These issues have historically created a significant support burden, with teachers and operations staff spending considerable time manually resolving what should be self-serviceable problems. The BrightBuddy Additional Flows initiative addresses both of these failure points by embedding automated assistance directly into the student and teacher interfaces.

The solution is split into two distinct product areas. Part 1 focuses on login assistance by enabling teachers to send pre-authenticated "magic links" to students, removing the dependency on credential recovery flows. Part 2 adds an in-dashboard shortcut on the Live Class Card that opens the BrightBuddy chatbot to handle class-joining failures in real time, including fetching direct Zoom links and helping students locate misplaced or rescheduled classes.

The business objective is aggressive: reduce Dashboard Login and Class Joining ticket volume to zero, as part of a broader initiative targeting a 72% overall reduction in support ticket volume. This PRD covers the full scope of both parts, including UX flows, functional requirements, technical integrations, and team dependencies.

## Problem Statement

Teachers are spending teaching bandwidth resolving student login and class-joining issues, routing these cases to the operations team and creating delays in both support resolution and class attendance. Students who cannot log in or join a class have no self-service path and are forced to wait for manual intervention. This degrades the learning experience, inflates support costs, and risks churn — particularly for students who miss live sessions due to technical barriers. The product needs an automated, low-friction resolution path for both login failures and class-joining failures that students can complete without any human involvement.

## User Stories

- As a teacher, I want to send a one-time magic login link to my student via WhatsApp, email, or SMS, so that they can access their dashboard immediately without needing to contact the operations team.
- As a student, I want to add and verify an alternate mobile number or email address on my profile, so that I have a backup login method available if my primary contact fails.
- As a student, I want to click a "Facing issues?" help link directly on my upcoming class card, so that I can get a direct Zoom link from the chatbot if the main join button is not working.
- As a student, I want to report that my expected class is not showing up in my dashboard, so that I can confirm my actual schedule and trigger a reschedule if the class times are incorrect.
- As an operations team member, I want teachers and students to resolve common login and class-joining issues on their own, so that ticket volume is reduced and my team can focus on complex escalations.

## Feature Scope

### In Scope

- Teacher-initiated magic link generation from the student details page
- Magic link delivery via WhatsApp, Email, and SMS channels
- Magic links that pre-authenticate the student directly to the dashboard homepage or the BrightBuddy chatbot
- Single-use expiry enforcement for all magic links
- Student-facing "Edit contact information" section for adding/updating backup mobile number and email
- OTP-based verification flow for all contact info additions and changes
- UI affordance (red dot indicator) showing count of unfilled contact fields
- Shiny glow animation on the contact info section when a student logs in via magic link
- "Facing issues? Click here" CTA on the Live Class Card in the student dashboard
- BrightBuddy chatbot flow to handle "Unable to join my class" issue — providing direct Zoom link
- BrightBuddy chatbot flow to handle "Can't find my class" issue — showing schedule and enabling reschedule
- Attendance tracking for students who join class via the fallback Zoom link provided by BrightBuddy
- Conditional visibility of chatbot menu options based on class start time (within 15 minutes or ongoing)

### Out of Scope

- Teacher-related issues within the BrightBuddy chatbot (covered in the Additional Flow - Teacher Issues sub PRD)
- Password reset or credential management beyond magic link generation
- Direct Zoom link provision for classes more than 15 minutes from starting
- Changes to the core BrightBuddy chatbot infrastructure or Prof Greenline persona

## Functional Requirements

1. **Magic Link Generation (Teacher Side)**
   - Teachers must have access to a "Help your student" trigger on the student details page.
   - Upon clicking, teachers must be able to choose between sending a "Chatbot link" (opens BrightBuddy) or "Homepage link" (opens student dashboard).
   - Teachers must be able to select the delivery channel: WhatsApp, Email, or SMS.
   - The system must generate a pre-authenticated, single-use token-based link and dispatch it via the chosen channel.
   - Acceptance criteria: The link logs in the student without requiring credentials, works exactly once, and fails gracefully on reuse.

2. **Magic Link Expiry and Security**
   - All magic links must be time-bound and expire after a single use.
   - The backend must validate each link against its usage state before allowing authentication.
   - Acceptance criteria: A link used once must return an error if accessed again; an unused link must authenticate successfully.

3. **Backup Contact Information**
   - Students must be able to view, add, and update a secondary email address and an alternate mobile number from the "Edit contact information" section.
   - Fields showing no data must display "NA" with an "+ Add" button; existing fields must show a "Change" button.
   - All additions and changes must trigger OTP verification before being saved.
   - Acceptance criteria: Updated contact info persists to the student profile; OTP must be validated before save is committed.

4. **Contact Info UI Affordance**
   - The contact info section must display a red dot indicator showing the count of unfilled contact fields.
   - When a student accesses the dashboard via a magic link, the contact info section must animate with a "shiny glow" to prompt the student to fill in backup details.
   - Acceptance criteria: Red dot count is accurate; glow animation fires on magic link login and not on regular login.

5. **Live Class Card — "Facing Issues?" CTA**
   - The Live Class Card in the student dashboard must include a "Facing issues? Click here" link for any class in an active or upcoming state.
   - Clicking this link must open the BrightChat modal (Prof Greenline chatbot).
   - Acceptance criteria: CTA is visible on the class card; modal opens with appropriate issue options.

6. **Chatbot Flow — Unable to Join**
   - If the student selects "I'm unable to join my class," the chatbot must provide the direct Zoom link for the class.
   - This option must only be available if the class starts within 15 minutes or is currently ongoing.
   - Attendance must be tracked correctly when the student joins via this fallback Zoom link.
   - Acceptance criteria: Zoom link is accurate and functional; attendance is recorded in the backend system.

7. **Chatbot Flow — Can't Find Class**
   - If the student selects "I can't find my class," the chatbot must display the student's upcoming class schedule.
   - The student must be presented with options: "Okay, Got it" (dismiss) or "Report Wrong Class Times" (trigger reschedule flow).
   - Acceptance criteria: Schedule shown is current and accurate; reschedule flow is triggered on report.

## UX/UI Flows

### Flow 1: Teacher Sends Magic Link

1. Teacher navigates to the student details page in the teacher portal.
2. Teacher clicks the "Help your student" button.
3. A modal appears offering two link types: "Chatbot link" (opens BrightBuddy) or "Homepage link" (opens student dashboard).
4. Teacher selects the desired link type.
5. Teacher selects the delivery channel: WhatsApp, Email, or SMS.
6. The system generates a single-use pre-authenticated link and dispatches a pre-formatted message to the student via the chosen channel.
7. Student receives the message, clicks the link, and is automatically logged into their dashboard or BrightBuddy without entering credentials.

### Flow 2: Student Updates Backup Contact Information

1. Student navigates to the "Edit contact information" section on the student dashboard.
2. The section displays current contact details. Unfilled fields show "NA" and a red dot indicator shows the count of missing fields.
3. Student clicks "Change" (for existing data) or "+ Add" (for empty fields).
4. Student enters the new mobile number or email address.
5. System sends an OTP to the new contact point.
6. An OTP verification modal appears; the student enters the received OTP.
7. Student clicks "Submit" to confirm.
8. System validates the OTP and saves the updated contact information.
9. Red dot count decreases or disappears when all fields are filled.

### Flow 3: Student Encounters a Class-Joining Issue

1. Student views the "Your Upcoming Classes" section on the dashboard.
2. Student locates the relevant class card. If the class is live, a "Live" icon is displayed on the card.
3. Student clicks "Facing issues? Click here" on the class card.
4. The BrightChat modal opens, presenting the Prof Greenline chatbot interface.
5. The chatbot presents issue options relevant to the class state.

**Sub-flow 3a — Unable to Join (class within 15 mins or ongoing):**

6a. Student selects "I'm unable to join my class."
7a. Chatbot retrieves and displays the direct Zoom link for the class.
8a. Student clicks the link to join.
9a. Attendance is recorded by the backend system.

**Sub-flow 3b — Can't Find Class:**

6b. Student selects "I can't find my class."
7b. Chatbot displays the student's current upcoming class schedule.
8b. Student selects "Okay, Got it" to dismiss, or "Report Wrong Class Times" to escalate.
9b. If the student reports wrong times, the reschedule flow is triggered.

## Technical Requirements

- **Magic Link Token Service:** Backend must support generating time-bound, single-use authentication tokens. Tokens must be stored with usage state (used/unused) and validated server-side on each access attempt.
- **Messaging Integrations:** The system requires active integrations with WhatsApp Business API, email sending service, and SMS gateway to dispatch magic link messages.
- **Zoom API Integration:** The BrightBuddy chatbot must be able to fetch the direct Zoom join link for a specific class session in real time, based on the student's schedule and class ID.
- **OTP Service:** An OTP generation and delivery service is required for the contact information verification flow. OTPs must be time-bound and validated server-side before any profile update is committed.
- **Attendance Tracking:** The attendance system must record class joins that originate from the BrightBuddy-provided Zoom link, not just joins from the native dashboard "Join" button. This may require a trackable redirect link rather than a raw Zoom URL.
- **Student Schedule API:** The chatbot must have read access to the student's class schedule to display upcoming classes in the "Can't find class" flow and to determine class start times for conditional option visibility.

## Non-Functional Requirements

- **Security:** All magic links must be single-use and expire after first access. OTP codes must be time-bound. No permanent login bypass mechanisms should be exposed.
- **UI Discoverability:** The red dot indicator on the contact info section must accurately reflect the number of missing contact fields and update in real time as fields are completed. The shiny glow animation must fire only for magic link-based logins.
- **Conditional Logic:** The "Unable to join my class" and "Teacher not in class" chatbot options must be hidden when a class is more than 15 minutes from starting to prevent students from getting non-functional Zoom links.
- **Reliability:** The fallback Zoom link provided by BrightBuddy must work even when the primary dashboard "Join" button fails, implying the Zoom link fetch must use a separate, resilient code path.

## Success Metrics

- **Primary KPI:** Dashboard Login and Class Joining related issue cases reduced to 0 per period.
- **Secondary KPI:** Overall support ticket volume reduced by 72%.
- **Proxy Metric:** Increase in self-service resolution rate (students/teachers resolving issues without ops team involvement).
- **Engagement Metric:** Rate of students completing backup contact info after magic link login (measuring the effectiveness of the glow animation affordance).

## Edge Cases & Error Handling

- **Class more than 15 minutes away:** The "Unable to join my class" and "Teacher not in class" chatbot options are hidden from the menu. Only the "Can't find my class" option is available. This prevents students from requesting a Zoom link before it has been created in the system.
- **Ongoing class (Live state):** The class card displays a "Live" icon, and all issue options — "Unable to join," "Teacher not in class," and "Can't find my class" — are visible and accessible.
- **Missing contact info:** If a secondary email or alternate mobile number has not been added, the UI displays "NA" in the relevant field and shows an "+ Add" button instead of "Change." The red dot count reflects the number of missing fields.
- **Magic link reuse attempt:** If a student attempts to use a magic link that has already been consumed, the system must return a clear error message and optionally prompt the teacher to generate a new link.
- **OTP failure:** If OTP delivery fails or the user enters an incorrect OTP, the system must display an error and allow the student to request a new OTP without losing their entered contact data.

## Dependencies

- **Additional Flow - Teacher Issues sub PRD:** The "Teacher not in class" option visible in the Live Class Card chatbot flow is handled by a separate sub PRD. This feature is a dependency for the complete chatbot menu.
- **Zoom Integration Service:** Reliable fetching of Zoom links depends on the Zoom API integration being maintained by the tech team.
- **Messaging Gateways:** WhatsApp, Email, and SMS delivery depends on existing messaging infrastructure and third-party provider uptime.
- **BrightBuddy Chatbot Platform:** The Prof Greenline chatbot (BrightBuddy) must support adding new flow nodes for the class-joining issue paths.

### Teams Involved

| Team | Role |
|---|---|
| Operations Excellence | Business sponsor; Micky Sukhwani, Lucky |
| Product | Aakrit Balwant Patel, Sachin Kumar |
| Design | Gurbinder Singh |
| Tech | Backend (token service, OTP, Zoom API), Frontend (dashboard UI, chatbot modal) |
| QA | End-to-end testing of all flows |
