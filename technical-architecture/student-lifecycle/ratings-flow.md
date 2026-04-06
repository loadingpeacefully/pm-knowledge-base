---
title: Ratings Flow
category: product-prd
subcategory: student-lifecycle
source_id: 27bdaf64-6bfc-4f87-aaa5-e04ce34efbd9
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Ratings Flow

## Overview

The Ratings Flow is a modular feedback and growth feature embedded in the BrightChamps Unified Student Dashboard. It provides a systematic mechanism for collecting student satisfaction data and converting highly satisfied students into active referral sources or external review contributors. The feature surfaces a dismissible rating stripe on the dashboard, collects a 1–5 star rating, and then branches into distinct experiences based on the rating given.

For 5-star ratings, the flow triggers a celebration animation and transitions the user into a referral sharing experience — offering a 20% discount to friends via pre-filled share messages across WhatsApp, Telegram, Gmail, and Facebook. For ratings of 1–4 stars, the flow surfaces tailored multi-select feedback forms or an open text field, enabling the team to capture actionable dissatisfaction signals and address them proactively.

The business goal is to improve CSAT tracking, generate new leads through a structured referral channel, and provide a lever for boosting external Trust Pilot ratings when needed. The backend toggle between "Referral Flow" and "Trust Pilot Flow" allows the product team to dynamically redirect 5-star users toward whichever growth channel needs more attention at a given time.

## Problem Statement

BrightChamps lacked a systematic, in-product mechanism to gather student satisfaction feedback. Without this, the team had no reliable signal for identifying at-risk students (those giving 1–3 stars) before they churned, and no structured channel for converting delighted students (5-star) into referral sources or external review contributors. Referrals were happening organically and inconsistently, missing the opportunity to amplify word-of-mouth with discounts and trackable UTM parameters. Separately, Trust Pilot ratings were difficult to influence without a direct, frictionless path from happy students to the review platform. The Ratings Flow solves all three gaps in a single, backend-configurable experience.

## User Stories

- As a student on the dashboard, I want to see a clear and non-intrusive rating stripe, so that I can easily share feedback about my BrightChamps experience when I feel ready.
- As a highly satisfied student who gives 5 stars, I want to easily share a referral link with my friends via WhatsApp or other platforms, so that they can get a 20% discount on their courses and I can help people I know benefit from the platform.
- As a dissatisfied student who gives 1–4 stars, I want to select specific reasons for my rating from a relevant list of options, so that BrightChamps can understand and address my exact concerns — such as changing my teacher or improving support.
- As a student who gives a 1-star rating, I want to be able to freely type my concerns in my own words, so that I can express nuanced dissatisfaction beyond what preset options cover.
- As a product manager, I want to toggle the 5-star destination between Referral Flow and Trust Pilot Flow via a backend configuration, so that I can dynamically redirect satisfied users toward whichever external growth channel needs attention at a given time without deploying new code.

## Feature Scope

### In Scope

- Dismissible rating stripe displayed on the BrightChamps Unified Dashboard
- 5-star dynamic rating component
- Conditional feedback forms with specific options for ratings of 2, 3, and 4 stars
- Open text field for 1-star ratings
- 5-star flow: celebration animation, referral sharing modal with pre-filled message
- Referral sharing options: Copy Link, WhatsApp, Telegram, Gmail, Facebook
- Dynamic variables in referral sharing text: `{teacher's name}`, `{subject}`, `{link}`
- UTM tracking parameter: `utm_medium='student-dashboard-rating'` appended to referral lead links
- Backend-configurable toggle to route 5-star users to either Referral Flow or Trust Pilot Flow
- Visibility logic: show stripe once per month until rated; hide for 15 days after a rating is submitted
- KPI tracking for views, ratings received, 5-star count, shares, and downstream acquisition funnel metrics

### Out of Scope

- Teacher quality scoring or rolling average recomputation based on ratings (separate internal flow)
- Post-class automatic rating prompts (this feature is dashboard-initiated, not class-completion-triggered)
- Full analytics tool integration (current state uses Google Sheets; analytics tool migration is a future roadmap item)
- Automated resolution workflows for negative feedback (operational; out of product scope for this release)

## Functional Requirements

1. **Rating Stripe Visibility and Frequency**
   - The rating stripe must appear on the Unified Dashboard once per calendar month until the user provides a rating.
   - After a user submits a rating, the stripe must be hidden for 15 days.
   - Acceptance Criteria: A user who has not rated in the current month sees the stripe. A user who submitted a rating today does not see the stripe for the next 15 days. After 15 days, the monthly display logic resumes.

2. **Dismissible Stripe**
   - The rating stripe must be dismissible by the user without requiring them to submit a rating.
   - Dismissal must not be counted as a rating submission (the 15-day suppression should not apply on dismissal).
   - Acceptance Criteria: User can close/dismiss the stripe. The stripe reappears on the next session or appropriate recurrence cycle.

3. **Backend Flow Toggle — Referral vs. Trust Pilot**
   - The system must support a backend configuration switch that determines whether a 5-star rating routes the user to the Referral Flow or the Trust Pilot Flow.
   - The switch must be changeable without a frontend deploy.
   - Acceptance Criteria: When set to "Referral Flow", 5-star users see the referral sharing modal. When set to "Trust Pilot Flow", 5-star users are directed toward the Trust Pilot review platform. The toggle can be changed for a configured number of days.

4. **5-Star Rating — Celebration and Referral Sharing**
   - Selecting 5 stars must immediately trigger a celebration animation.
   - The UI must transition to a "Thank you for rating us" modal that invites the user to refer family or friends.
   - The modal must include: Copy Link button, WhatsApp icon/share, Telegram icon/share, Gmail icon/share, Facebook icon/share.
   - The pre-filled message must include dynamic values for `{teacher's name}`, `{subject}`, and `{link}`.
   - The referral lead link must include the UTM parameter `utm_medium='student-dashboard-rating'`.
   - Acceptance Criteria: All five sharing methods are present and functional. Dynamic variables render with actual data. UTM parameter is appended to all shared links.

5. **4-Star Rating — Conditional Feedback Form**
   - Selecting 4 stars must surface a multiple-select feedback form with the following options:
     - More engagement
     - Better customer support
     - Increase curriculum relevance
     - Change my teacher
     - Nothing specific
   - Acceptance Criteria: All five options are present as multi-select checkboxes. User can select one or more. Submission records the selected options.

6. **3-Star Rating — Conditional Feedback Form**
   - Selecting 3 stars must surface a multiple-select feedback form with the following options:
     - Improve class experience
     - Better customer support
     - Revamp curriculum
     - Change teacher
     - Others
   - Acceptance Criteria: All five options are present as multi-select checkboxes. User can select one or more. Submission records the selected options.

7. **2-Star Rating — Conditional Feedback Form**
   - Selecting 2 stars must surface a multiple-select feedback form with the following options:
     - Didn't enjoy my classes
     - Need a teacher change
     - The subject seems difficult to understand
     - No support in query resolutions
     - Others
   - Acceptance Criteria: All four options (plus "Others") are present as multi-select checkboxes. User can select one or more. Submission records the selected options.

8. **1-Star Rating — Open Text Feedback**
   - Selecting 1 star must surface an open text box field for the user to freely type their concerns.
   - Acceptance Criteria: Text field is present, accepts free-form input, and the submission stores the text alongside the 1-star rating.

9. **UTM Tracking on Referral Links**
   - All referral links generated by the 5-star flow must include `utm_medium='student-dashboard-rating'` as a URL parameter.
   - Acceptance Criteria: Copying the link or sharing via any platform (WhatsApp, Telegram, Gmail, Facebook) produces a URL containing the correct UTM parameter.

## UX/UI Flows

### Flow 1: User Sees Rating Stripe and Dismisses

1. User opens the BrightChamps Unified Dashboard.
2. Rating stripe appears at the top or in a designated banner area.
3. User clicks the dismiss/close button.
4. Stripe disappears for the current session.
5. Stripe reappears on next recurrence per the monthly display logic (not suppressed by the 15-day rule since no rating was submitted).

### Flow 2: 5-Star Rating — Referral Flow (Backend Toggle = Referral)

1. User sees the rating stripe and clicks it or the star selector.
2. User taps the 5th star.
3. Celebration animation plays.
4. UI transitions to a "Thank you for rating us!" modal.
5. Modal invites the user to refer a friend and shows a pre-filled message with `{teacher's name}`, `{subject}`, and `{link}`.
6. User selects a sharing method: Copy Link, WhatsApp, Telegram, Gmail, or Facebook.
7. If Copy Link: link is copied to clipboard; confirmation message shown.
8. If social share: native share sheet or redirect to the platform with the pre-filled message.
9. All shared links include `utm_medium='student-dashboard-rating'`.
10. Rating recorded; stripe hidden for 15 days.

### Flow 3: 5-Star Rating — Trust Pilot Flow (Backend Toggle = Trust Pilot)

1–4. Same as Flow 2 steps 1–4.
5. Modal directs the user toward leaving a Trust Pilot review (link or redirect to Trust Pilot).
6. Rating recorded; stripe hidden for 15 days.

### Flow 4: 4-Star Rating — Structured Feedback

1. User taps the 4th star.
2. Modal updates to an acknowledgment message and displays multiple-select checkboxes: "More engagement", "Better customer support", "Increase curriculum relevance", "Change my teacher", "Nothing specific".
3. User selects one or more options.
4. User clicks "Submit."
5. Feedback recorded alongside the 4-star rating.
6. Stripe hidden for 15 days.

### Flow 5: 3-Star Rating — Structured Feedback

1. User taps the 3rd star.
2. Modal updates with an apology/prompt and displays: "Improve class experience", "Better customer support", "Revamp curriculum", "Change teacher", "Others".
3. User selects options and submits.
4. Feedback recorded; stripe hidden for 15 days.

### Flow 6: 2-Star Rating — Structured Feedback

1. User taps the 2nd star.
2. Modal displays: "Didn't enjoy my classes", "Need a teacher change", "The subject seems difficult to understand", "No support in query resolutions", "Others".
3. User selects options and submits.
4. Feedback recorded; stripe hidden for 15 days.

### Flow 7: 1-Star Rating — Open Text Feedback

1. User taps the 1st star.
2. Modal updates to a message expressing concern over a poor experience.
3. User sees an open text box and types their specific concerns.
4. User clicks "Submit."
5. Feedback text recorded alongside the 1-star rating.
6. Stripe hidden for 15 days.

## Technical Requirements

- **Backend Configuration Toggle:** A backend-configurable flag must determine whether 5-star users are routed to the Referral Flow or the Trust Pilot Flow. This must be changeable without a frontend deployment. The toggle must also support configuration for a set number of days (e.g., run Trust Pilot Flow for 7 days, then revert to Referral Flow).
- **Dynamic Variable Injection:** The referral sharing message must dynamically inject `{teacher's name}` and `{subject}` from the student's enrollment record. These values must be resolved server-side before the message is rendered in the modal.
- **UTM Parameter Appending:** All referral lead links generated by this flow must have `utm_medium='student-dashboard-rating'` appended. This must apply to all five sharing channels (Copy Link, WhatsApp, Telegram, Gmail, Facebook).
- **Rating Visibility State Management:** The backend must store when a user last submitted a rating and use this to determine stripe visibility (hide for 15 days post-rating; show monthly otherwise). This state must persist across sessions and devices.
- **Data Storage — Current State:** Rating responses and feedback selections are currently tracked manually via a Google Sheet. All rating submissions and feedback responses must be written to the data store for this manual tracking.
- **Analytics Migration (Future):** A long-term requirement exists to migrate from Google Sheets tracking to an integrated analytics tool (previously used Google Analytics). This is a future roadmap item, not in the current release scope.

## Non-Functional Requirements

- Performance targets, browser and device support matrix, formal accessibility standards, and localization requirements are not specified in the source document.
- Recommended defaults for a student-facing dashboard feature:
  - Rating submission response should be near-instantaneous (under 500ms) to not break the momentum of the celebration/feedback flow.
  - Must be functional on mobile browsers, as many students access the dashboard via phone.
  - The sharing modal must work correctly with native mobile share APIs (for WhatsApp, Telegram, etc.) where applicable.
  - Multi-language support for the pre-filled referral message may be needed for international students ({{subject}} and {{teacher's name}} are dynamic; the surrounding copy may need localization in later phases).

## Success Metrics

The document defines an impact funnel with the following explicit KPIs:

**Engagement KPIs:**
- Number of views on the rating stripe
- Number of ratings received

**Satisfaction KPIs:**
- Number of users who rated 5 stars (and percentage of all raters)

**Referral/Viral KPIs:**
- Number of users who copied or shared the referral link (and percentage of 5-star raters)

**Acquisition Funnel KPIs (downstream):**
- Number of landing page views from referral links
- Landing Page Conversion Rate (LPCR)
- Number of leads generated
- Number of leads who joined (paid)
- Number of demo classes completed from referred leads
- Number of conversions (paid enrollments from referred leads)
- Total revenue attributed to the referral flow

## Edge Cases & Error Handling

- **User Dismisses Without Rating:** Dismissal must not trigger the 15-day suppression. The stripe should reappear per the normal monthly cadence.
- **User Rates and Returns Within 15 Days:** The stripe must remain hidden for the full 15 days post-rating. A user who navigates back multiple times should not see the stripe until the suppression window expires.
- **Backend Toggle Not Set:** If the backend configuration for Referral vs. Trust Pilot flow is not set or returns an error, the system should default to the Referral Flow to avoid routing errors.
- **Dynamic Variables Unavailable:** If `{teacher's name}` or `{subject}` cannot be resolved (e.g., student has no active teacher assigned or no active enrollment), the pre-filled message must still render gracefully — either omitting the variable or substituting with a neutral placeholder — rather than showing a raw `{variable}` token.
- **UTM Parameter Failure:** If UTM appending fails for any sharing channel, the link should still be shareable (fail open); the UTM omission should be logged for monitoring purposes.
- **Submission Failure (Network Error):** If the rating or feedback submission fails due to a network error, the user should see a friendly error state with a retry option, rather than silently losing the feedback data.
- **Multiple Share Attempts:** If a user shares via multiple channels (e.g., copies the link and also shares via WhatsApp), both actions should be tracked separately in the KPI instrumentation.
- **Trust Pilot Redirect Broken:** If the Trust Pilot link is unavailable, the user should see a fallback message or be redirected to the Referral Flow as a backup.

## Dependencies

- **Backend Engineering:** Backend configuration toggle for Referral vs. Trust Pilot flow routing; dynamic variable resolution for teacher name and subject; rating visibility state management (15-day suppression, monthly display logic); data storage for ratings and feedback.
- **Frontend Engineering:** Star rating component, celebration animation, conditional modal rendering (5-star vs. 2/3/4/1-star states), sharing integrations (WhatsApp, Telegram, Gmail, Facebook, Copy Link), UTM parameter injection.
- **Data/Analytics Team:** Current tracking is via Google Sheets; long-term dependency on analytics tool integration for automated KPI measurement. Until the migration is complete, manual tracking from the Google Sheet is the measurement method.
- **Marketing/Growth Team:** Referral discount offering (20% off course purchases) must be configured and fulfillable. UTM tracking must be aligned with the team's attribution model.
- **Trust Pilot:** External platform dependency; the Trust Pilot link must be active and accessible for the Trust Pilot flow variant to work.
- **Student Profile / Enrollment Service:** Dynamic variables `{teacher's name}` and `{subject}` depend on real-time data from the student's active enrollment record.
