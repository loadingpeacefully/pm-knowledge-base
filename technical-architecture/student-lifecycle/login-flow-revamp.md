---
title: Login Flow Revamp
category: product-prd
subcategory: student-lifecycle
source_id: e5f5ce8c-cdc2-44e4-ab24-90fb573c63d6
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Login Flow Revamp

## Overview

The Login Flow Revamp is a set of targeted improvements to the Schola/BrightChamps login experience designed to reduce friction at the entry point of the platform. The primary problems being addressed are: a default Indian dial code that creates a poor experience for international students, a rigid 4-digit MPIN restriction that excludes users familiar with 6-digit formats, and a difficult login experience for newly converted paid students during onboarding.

The revamp introduces three key changes: IP-based auto-detection of the student's country dial code, flexible MPIN input supporting both 4-digit and 6-digit formats, and pre-logged-in links sent to newly converted students post-payment so they can bypass the login screen entirely. A secondary UI change deprioritizes the "Book a free trial class" button to a secondary CTA, reflecting the shift in focus toward paid students.

This initiative sits within the Customer Success track and is driven by the goal of improving onboarding completion rates, providing a more inclusive and localized experience for international users, and reducing the drop-off that occurs when new paying students cannot easily access the platform after subscribing.

## Problem Statement

The current login page defaults to the Indian country dial code regardless of where the user is accessing the platform from. International students must manually change this field on every login, creating unnecessary friction and signaling a lack of localization. The system also enforces a 4-digit MPIN, which is incompatible with user habits in markets where 6-digit PINs are the norm. Perhaps most critically, newly converted paid students — who represent high-value users at a critical moment in the funnel — face login difficulties that reduce their likelihood of completing onboarding. Collectively, these issues reduce platform access rates, hurt first-session completion, and negatively impact retention for international and newly subscribed users.

## User Stories

- As an international student, I want my country's dial code to automatically prefill based on my IP address, so that I receive a localized experience and do not have to manually change it from the default Indian code every time I log in.
- As a student familiar with a 6-digit MPIN, I want to be able to set and enter a 6-digit MPIN, so that I can log in using a format that feels natural to me without being restricted to 4 digits.
- As a newly converted paid student, I want to receive a pre-logged-in link after completing payment, so that I can access my dashboard immediately without struggling through the standard login flow during onboarding.
- As a returning international student, I want the login page to remember my region preference so that the dial code is consistently accurate across sessions.
- As a product team member, I want the "Book a free trial class" button to be visually deprioritized, so that the login page better serves paid students as the primary audience rather than prompting conversions from the login screen.

## Feature Scope

### In Scope

- Auto-detection of country dial code on the login page based on the user's IP address
- MPIN input flow modification to support both 4-digit and 6-digit MPINs with user choice
- Generation of unique pre-logged-in links for newly converted paid students, triggered post-payment
- Delivery of pre-logged-in links to the user (via SMS, email, or WhatsApp — method TBD)
- UI change: "Book a free trial class" button moved to secondary CTA placement
- Schola platform login page and post-payment onboarding flows

### Out of Scope

- Full authentication system overhaul (OTP, social login, biometric — not part of this revamp)
- Parent/guardian login flows (not mentioned in source)
- MPIN reset or recovery flows (implied dependency but not in scope for this revamp)
- Browser/device-specific performance optimization beyond standard web standards
- Accessibility and localization standards beyond dial code auto-detection

## Functional Requirements

1. **Auto Detection of Dial Code**
   - The login page must detect the user's IP address on page load and automatically prefill the country dial code selector with the appropriate code.
   - This must replace the current behavior of defaulting to the Indian dial code (+91) for all users.
   - Acceptance Criteria: A user accessing the login page from a non-Indian IP sees their country's dial code prefilled without any manual action. Indian users continue to see +91. The dial code remains editable if the auto-detected code is incorrect.

2. **MPIN Input Flow — 4-digit and 6-digit Support**
   - The MPIN input field must support both 4-digit and 6-digit MPINs.
   - Users must be able to select or indicate their preferred MPIN length.
   - The system must validate and authenticate against both MPIN lengths.
   - Acceptance Criteria: A user with a 6-digit MPIN can enter it and successfully authenticate. A user with a 4-digit MPIN is unaffected. No user is forced to change their existing MPIN format.

3. **Pre-Logged-In Links for Newly Converted Students**
   - Upon a successful payment/subscription conversion event, the system must generate a unique, time-limited pre-logged-in link for that user.
   - The link must be sent to the user via the appropriate communication channel post-payment.
   - Clicking the link must bypass the standard login screen and land the user directly on their dashboard or onboarding flow.
   - Acceptance Criteria: A newly converted student who clicks their pre-logged-in link within the validity window is authenticated and routed to their dashboard without entering credentials. An expired link shows a graceful error with a standard login fallback.

4. **"Book a Free Trial Class" CTA Demotion**
   - The "Book a free trial class" button must be repositioned or restyled as a secondary CTA on the login page.
   - Acceptance Criteria: The button is visually less prominent than the primary login action. It remains accessible but does not compete with the login flow for visual attention.

## UX/UI Flows

### Legacy Flow (Current State)

1. User arrives at the Schola login page.
2. Dial code defaults to India (+91).
3. International user manually changes the dial code to their country.
4. User enters their phone number.
5. User enters their 4-digit MPIN.
6. User clicks the Login button.
7. User is authenticated and routed to the dashboard.

### New Flow 1: Auto-Detection and Flexible MPIN Login

1. User arrives at the Schola login page.
2. System detects user's IP address and automatically prefills the correct country dial code.
3. User sees their country dial code already selected (no manual intervention needed).
4. User enters their phone number.
5. User is presented with the MPIN input field, which accepts 4 or 6 digits.
6. User enters their MPIN (either 4 or 6 digits depending on what they set).
7. User clicks the Login button.
8. User is authenticated and routed to the dashboard.
9. "Book a free trial class" is visible as a secondary CTA but does not interrupt the login flow.

### New Flow 2: Pre-Logged-In Link for Newly Converted Students

1. User completes a payment and converts to a paid subscription.
2. System triggers generation of a unique pre-logged-in link associated with the user's account.
3. Link is delivered to the user via post-payment communication (SMS/email/WhatsApp).
4. User clicks the link from their message.
5. System validates the link (checks uniqueness, expiry, and account association).
6. If valid: user is bypassed past the login screen and lands directly on their dashboard or onboarding start.
7. If expired or invalid: user sees a friendly error message with a prompt to log in via the standard flow.

## Technical Requirements

- **IP Geolocation Integration:** The login page must integrate with an IP geolocation service (e.g., MaxMind GeoIP, ipapi, or similar) to detect the user's country on page load. The detected country must be mapped to the correct ITU dial code and used to prefill the dial code selector.
- **MPIN Validation Backend Update:** The authentication backend must be updated to accept and validate both 4-digit and 6-digit MPINs. The MPIN length must be stored alongside the hashed MPIN in the user's authentication record.
- **Pre-Logged-In Link Generation Service:** A new service or extension to the existing auth flow must be built to:
  - Generate unique, cryptographically random tokens tied to a user account.
  - Set an expiry time on the token (duration TBD; recommended 24–72 hours post-generation).
  - Validate tokens on redemption and issue an authenticated session.
  - Invalidate tokens after single use to prevent replay attacks.
- **Post-Payment Trigger:** The pre-logged-in link generation must be triggered by the payment/subscription conversion event, integrating with the payment processing system or CRM post-purchase webhook.
- Specific API contracts, third-party services beyond IP geolocation, and data storage schemas are not detailed in the source document.

## Non-Functional Requirements

- **Localization:** The auto-detection feature is specifically designed to provide a more localized experience for students worldwide. The dial code prefill must cover all countries where BrightChamps/Schola operates.
- **Security:** Pre-logged-in links must be single-use and time-limited to prevent unauthorized access if a link is forwarded or intercepted. Token generation must use cryptographically secure random methods.
- Performance targets, explicit browser and device support matrix, and formal accessibility standards are not specified in the source document.
- Reasonable defaults: Login page should be responsive and functional on mobile devices, given the student demographic and likelihood of accessing via phone.

## Success Metrics

The source document references an "Impact Funnel" framework with fields for "Improvement Metric Value", "Current/Expected Adoption %", and "Current/Expected Impact" but leaves these blank. Inferred success metrics based on the stated goals:

- Onboarding completion rate for newly converted paid students (primary metric; target: measurable lift from pre-logged-in link adoption)
- Login page drop-off rate for international users (expected decrease post dial code auto-detection)
- Support ticket volume related to login difficulties during onboarding (expected decrease)
- MPIN-related login failure rate (expected decrease with 6-digit MPIN support)
- Pre-logged-in link click-through rate within 24 hours of payment conversion

## Edge Cases & Error Handling

- **IP Address Undetectable or Masked:** If the user's IP cannot be resolved (e.g., VPN, Tor, or geolocation service failure), the system must fall back to a default dial code (e.g., India +91 for now) or display a neutral "Select your country" prompt rather than failing silently or breaking the page.
- **Incorrect Auto-Detected Dial Code:** The auto-filled dial code must remain manually editable. Users can correct it if the geolocation is inaccurate.
- **Pre-Logged-In Link Expired:** If the user clicks a pre-logged-in link after it has expired, they must see a clear message (e.g., "This link has expired. Please log in below.") and be redirected to the standard login page.
- **Pre-Logged-In Link Already Used:** If the link has already been redeemed (single-use enforcement), the system should respond with the same expired-link message rather than exposing whether the link was used by someone else.
- **Wrong MPIN Length Entered:** If a user with a 4-digit MPIN accidentally enters only 3 or 5 digits, the system must show a validation error before attempting authentication. Similarly for 6-digit MPIN users.
- **Payment Webhook Failure:** If the post-payment trigger for pre-logged-in link generation fails, the system must log the failure and retry. If retries are exhausted, the user should still be able to log in via the standard flow; support can manually resend the link if needed.

## Dependencies

- **Customer Success Team:** Feature owner and primary driver; responsible for business requirements and success measurement.
- **Product Team:** Requirements definition and acceptance criteria.
- **Design Team:** UI/UX changes to the login page (CTA demotion, MPIN input redesign, dial code selector update).
- **Engineering/Tech Team:** Backend and frontend implementation across auth service, MPIN validation, IP geolocation integration, and link generation service.
- **QA Team:** Test coverage for all three flows (auto-detection, flexible MPIN, pre-logged-in links) including edge cases.
- **Payment System / CRM:** Pre-logged-in link generation depends on a reliable post-payment conversion event or webhook from the payment processing layer.
- **IP Geolocation Service:** External or internal service dependency for dial code auto-detection. Must be evaluated for latency impact on login page load time.
