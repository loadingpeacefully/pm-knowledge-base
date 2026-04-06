---
title: Demo Certificate Sharing
category: product-prd
subcategory: student-lifecycle
source_id: 990f4a66-0d5f-4693-9901-ce390abb91ad
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Demo Certificate Sharing

## Overview

After completing a trial (demo) class, students receive a certificate of participation. Currently, when a student or parent clicks the certificate link from an email or WhatsApp message, the certificate downloads directly to the local device — a transactional, low-engagement experience that misses a significant opportunity. The Demo Certificate Sharing feature reimagines this flow by hosting the certificate on a dedicated, celebratory web page that delights the user and actively encourages them to share the achievement on social media and messaging platforms.

The web page displays the certificate alongside a confetti animation and provides "Download" and "Share" call-to-action buttons. When the parent clicks Share, the system auto-copies a pre-filled celebratory message — complete with the student's name, teacher's name, and a shortened referral link — and opens the device's native share panel (Android or iOS). This transforms the certificate from a private download into a viral referral touchpoint.

The business goal is explicitly referral-driven: every certificate share has the potential to generate new leads, deals, and conversions. The feature tracks these outcomes through an Impact Funnel that measures leads, deals, conversions, and revenue attributable to certificate-share referrals. A companion feature for paid students — a full-screen celebration pop-up on module completion — is in scope but currently paused.

## Problem Statement

The current certificate delivery experience is purely functional: a link in an email or WhatsApp message triggers a direct file download. This provides no visual celebration, no engagement, and no path to referral. Parents who are proud of their child's achievement have no easy, ready-made way to share it on WhatsApp or social media, and BrightChamps misses the opportunity to convert that pride into new customer acquisition. The product needs a shareable, celebratory certificate experience that reduces the friction to sharing and embeds a referral mechanism directly in the shared content.

## User Stories

- As a parent who just received my child's demo certificate, I want to view it on a beautiful web page rather than having it download automatically, so that I can see and appreciate the achievement immediately.
- As a parent, I want to tap a "Share" button that opens my phone's native sharing options with a pre-written message ready to go, so that I can share the achievement on WhatsApp without having to compose a message from scratch.
- As a parent sharing the certificate, I want the shared message to include a referral link for BrightChamps, so that my friends and family can easily book a demo class for their own children.
- As a paid student, I want to see a full-screen confetti celebration pop-up when I complete a module, so that I feel recognized and motivated to continue learning.
- As BrightChamps marketing, I want shared certificate messages to include a shortened referral link and generate a rich visual preview on WhatsApp and Facebook, so that certificate shares drive measurable lead acquisition.

## Feature Scope

### In Scope

- Certificate hosted on a dedicated web page URL (student ID as query parameter), replacing direct file download
- Web and mobile views of the certificate with a confetti animation on page load
- "Download My Certificate" and "Share" CTA buttons on the certificate page
- Share button behavior: auto-copy of a pre-defined celebratory message template with dynamic placeholders (student name, teacher name, shortened referral link)
- Native Android and iOS share panel integration triggered on Share button click
- Shortened URLs for both the certificate link and the referral link in the shared message
- Rich link/PDF/image preview generation when shared on WhatsApp and Facebook
- Paid student module completion pop-up: full-screen celebration with confetti (currently paused)
- Pop-up scheduling logic: suppress pop-up if next class starts within 5 minutes; queue for next dashboard visit

### Out of Scope

- Certificate sharing via channels other than the native share panel (e.g., direct social media API posting)
- Certificate generation itself (this PRD covers the sharing and web page experience, not certificate creation)
- Sharing flows for non-demo, non-paid certificates
- Analytics dashboard for tracking individual share events (covered by Impact Funnel reporting separately)

## Functional Requirements

1. **Certificate Web Page Hosting**
   - Certificates must be hosted on a dedicated URL. The URL must include the student ID as a query parameter (e.g., `/certificate?student_id=xxx`) to identify the specific certificate.
   - The page must replace the current behavior of direct file download when the certificate link is clicked.
   - Acceptance criteria: Clicking a certificate link from email or WhatsApp opens the web page, not a file download; the correct student's certificate is displayed based on the query parameter.

2. **Certificate Page UI**
   - The page must display the certificate in a visual format (web or mobile view).
   - A confetti animation must play when the page loads, creating a celebratory experience.
   - The page must include two CTAs: "Download My Certificate" and "Share."
   - Acceptance criteria: Confetti animation fires on page load; both CTAs are visible and functional; certificate is displayed in full.

3. **Share Button — Auto-Copy and Native Share Panel**
   - Clicking the "Share" button must automatically copy the pre-defined "Certificate Sharing Message" to the user's clipboard.
   - The Share button must also trigger the device's native Android or iOS share panel.
   - The pre-defined message template must include dynamic placeholders: student's name, teacher's name, and a shortened referral link.
   - Acceptance criteria: Native share panel opens on button click; clipboard contains the pre-filled message with correct dynamic values; shortened links are present.

4. **Shortened URLs**
   - Both the certificate URL and the referral link included in the shared message must be shortened URLs.
   - Long URLs must not appear in the shared message.
   - Acceptance criteria: Shared message contains only shortened URLs; both URLs resolve correctly when clicked.

5. **Rich Preview on WhatsApp and Facebook**
   - When the certificate URL is shared on WhatsApp or Facebook, the platform must render a rich preview (link preview, PDF preview, or image preview).
   - The certificate web page must include appropriate Open Graph or equivalent metadata tags to enable rich previews.
   - Acceptance criteria: Shared link on WhatsApp/Facebook displays a visible image or PDF preview of the certificate; no blank link previews.

6. **Paid Student Module Completion Pop-Up (Paused)**
   - Upon module completion, the system must trigger a full-screen celebration pop-up for paid students.
   - The pop-up must include a confetti animation.
   - The system must check if the user's next class starts within 5 minutes of the pop-up trigger time. If `system_time >= upcoming_class_joining_time - 5 mins`, the pop-up must be suppressed and queued for the user's next dashboard visit.
   - Acceptance criteria: Pop-up displays on module completion; pop-up is correctly suppressed when next class is imminent; suppressed pop-up appears on next dashboard visit.

## UX/UI Flows

### Flow 1: Parent Views and Shares Certificate (from Email/WhatsApp)

1. Parent receives a message (email or WhatsApp) containing a certificate link after their child completes a demo class.
2. Parent clicks the link.
3. Instead of a file download, the browser or in-app webview opens a dedicated certificate web page.
4. A confetti animation plays on page load.
5. The certificate is displayed in a web/mobile-optimized layout.
6. Two CTAs are visible: "Download My Certificate" and "Share."
7. Parent clicks "Share."
8. The system automatically copies the pre-filled celebratory message (with student name, teacher name, and shortened referral link) to the clipboard.
9. The device's native Android or iOS share panel opens.
10. Parent selects their preferred app (e.g., WhatsApp, Facebook, Instagram).
11. The selected app opens with the pre-filled message and a rich visual preview of the certificate.
12. Parent sends the message to their contacts.

### Flow 2: Parent Downloads Certificate

1. Parent is on the certificate web page (reached via steps 1–5 of Flow 1).
2. Parent clicks "Download My Certificate."
3. The certificate PDF or image is downloaded to the device.

### Flow 3: Paid Student Module Completion Pop-Up

1. Paid student completes a module.
2. System checks if the student's next class starts within 5 minutes.
3. **If no class imminent:** Full-screen celebration pop-up displays with confetti animation and "Share" CTA.
4. **If class is imminent (within 5 minutes):** Pop-up is suppressed; no interruption to the class-joining flow. Pop-up is queued for the next dashboard visit.
5. On the student's next dashboard login or visit, the queued pop-up is displayed.

## Technical Requirements

- **Certificate Web Page:** A web page must be created that accepts a student ID query parameter and renders the corresponding certificate. The page must serve both web and mobile-optimized layouts.
- **Confetti Animation:** The confetti effect is to be implemented using an Animation JSON file sourced from LottieFiles (a Lottie animation library).
- **Native Share Panel Integration:** The Share button must invoke native iOS share intent and Android share intent/APIs to open the OS-level share panel, not a custom in-app share overlay.
- **URL Shortening Service:** A URL shortening solution is required to shorten both the certificate URL and the referral link before they are inserted into the shared message template. Long URLs are explicitly unacceptable for the shared message format.
- **Open Graph / Rich Preview Metadata:** The certificate web page must include Open Graph meta tags (og:image, og:title, og:description, og:url) so that WhatsApp, Facebook, and other platforms can generate a rich preview when the link is shared.
- **Dynamic Message Template:** The Certificate Sharing Message must be a server-side or client-side template that dynamically populates: `{{student_name}}`, `{{teacher_name}}`, `{{certificate_short_url}}`, and `{{referral_short_url}}`.
- **Pop-Up Queue Mechanism:** For the paid student module completion pop-up, the backend must store a flag indicating a queued pop-up for the student. On next dashboard load, the frontend checks this flag and displays the queued pop-up before clearing the flag.
- **Attendance/Class Time Check:** The pop-up suppression logic requires the system to query the student's upcoming class schedule and compare the class joining time against the current system time before deciding whether to show or queue the pop-up.

## Non-Functional Requirements

- **Device Support:** The certificate web page and Share button must work on both iOS and Android mobile devices, as well as desktop web browsers. Native share panel integration is mobile-specific; on desktop, a fallback behavior (e.g., copy-to-clipboard) must be provided.
- **URL Length:** All URLs in the shared message must be shortened. Long, unformatted URLs are unacceptable from a UX and message formatting perspective.
- **Rich Preview Quality:** The certificate preview image used in Open Graph tags must be high resolution and legible when displayed as a thumbnail in WhatsApp and Facebook.
- **Animation Performance:** The Lottie confetti animation must not significantly impact page load time. It should be lazy-loaded after the core certificate content is rendered.
- **Localization:** The document references email and WhatsApp templates for English ("en") and other language variants ("rb"). The sharing message template must support localization to match the language of the recipient.

## Success Metrics

The feature is measured through an Impact Funnel focused on referral-driven business outcomes:

| Metric | Description |
|---|---|
| Total Leads | Number of new leads generated from certificate share referral links |
| Total Deals | Number of leads that progress to a booked demo |
| Total Conversions | Number of deals that result in a paid enrollment |
| Revenue | Total revenue attributable to conversions from certificate share referrals |

Example baseline targets mentioned in the source: 234 leads, 77 deals, 2 conversions, revenue of 24,543 (currency not specified).

Additional proxy metrics:
- Share rate: percentage of parents who click "Share" after viewing the certificate
- Download rate: percentage of parents who download the certificate
- Rich preview render rate: percentage of shared links that display a visual preview on WhatsApp/Facebook

## Edge Cases & Error Handling

- **Class Time Conflict (Pop-Up Suppression):** If a paid student earns a module completion certificate and their next class starts within 5 minutes, the full-screen celebration pop-up is suppressed entirely during that session to avoid disrupting their class entry. The pop-up is queued in the backend and displayed on the student's next dashboard visit.
- **URL Shortening Failure:** If the URL shortening service is unavailable when a parent attempts to share, the system must either fall back to the full-length URL (with a note) or display an error message and allow retry. Sharing must not silently break.
- **Student or Teacher Name Missing:** If the dynamic placeholders cannot be resolved (e.g., teacher name is not available), the message template must have a sensible fallback string to avoid sending a message with visible placeholder tokens.
- **Rich Preview Not Loading:** If the Open Graph metadata is not correctly consumed by the target platform, the share will still succeed as a text link. This is an acceptable degradation but should be monitored.
- **Certificate URL Not Found:** If the student ID query parameter resolves to no certificate (e.g., certificate was not yet generated or ID is invalid), the page must display a clear error state rather than a blank or broken page.

## Dependencies

- **URL Shortening Mechanism:** Explicitly identified as a dependency. A URL shortening service must be selected, integrated, and operational before the share feature can be launched.
- **Business Team Adoption:** The source document indicates a "Business Team Adoption" status, implying the business/sales team needs to be aligned on the referral link structure and tracking before the feature goes live.
- **Certificate Generation Service:** The web page and share flow depend on the upstream certificate generation service having already created and stored the certificate. If certificate generation is delayed or fails, the web page cannot render correctly.
- **LottieFiles / Animation Library:** The confetti animation depends on the Lottie animation framework and the specific animation JSON file. This must be sourced and licensed appropriately.

### Teams Involved

| Team | Role |
|---|---|
| Product | Feature scoping, Impact Funnel definition, referral link strategy |
| Design | Certificate web page design, confetti animation, Share button UX, mobile/web layouts |
| Tech | Web page hosting, URL shortening integration, Open Graph metadata, native share panel integration, pop-up queue mechanism |
| Marketing | Certificate sharing message template, referral link tracking, campaign alignment |
| QA | Testing share flows on Android and iOS, rich preview validation on WhatsApp/Facebook, pop-up suppression logic |
