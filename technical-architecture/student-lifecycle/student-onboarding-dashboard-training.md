---
title: Student Onboarding Dashboard Training
category: product-prd
subcategory: student-lifecycle
source_id: da8a3238-40df-4d80-ba6e-9064cef4cab8
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Student Onboarding Dashboard Training

## Overview

The Student Onboarding Dashboard Training feature represents a complete overhaul of the existing student onboarding experience at BrightChamps. The current onboarding journey is a linear, unengaging process primarily used for data collection — it lacks personalization, fails to capture user interest, misses critical cross-selling opportunities, and drops users onto a dashboard without adequate guidance or immediate value recognition.

This initiative transforms onboarding from a form-filling exercise into a conversational, gamified experience led by an interactive character (Prof. Greenline / Ms. Greenline). It incorporates profile personalization, a targeted cross-sell recommendation engine with a free trial incentive, and post-onboarding dashboard training via interactive coach marks. The goal is to make a student's first experience with BrightChamps feel welcoming, personalized, and immediately valuable.

The feature spans two major phases: (1) the onboarding flow itself — a multi-step, conversational journey that collects profile data, preferences, and legal consents while creating a sense of delight; and (2) the dashboard training phase — interactive tooltip coach marks that guide new users through the key dashboard features like joining a class, rescheduling, and tracking progress after they have completed onboarding.

## Problem Statement

The current onboarding experience fails on multiple dimensions. It is a static, form-based journey that collects data without creating engagement. Students aged 8-15 and their parents aged 30-45 expect a personalized, interactive, and modern digital experience — and the current flow delivers none of these. Key problems include: no personalization or adaptive content during the signup journey; no cross-selling touchpoints to drive additional course enrollments during a high-intent moment; new users are dropped onto the dashboard after onboarding with no guidance on how to use it, resulting in confusion and poor feature adoption; and there is no mechanism to capture user interest before they disengage, as there is no progress-saving or "welcome back" flow for users who drop off mid-onboarding. The lead-to-conversion rate sits below benchmark — a 10% conversion rate was discovered as a baseline during a European sales team experiment — indicating the onboarding funnel is a major leakage point.

## User Stories

- As a student, I want to upload a custom profile picture or select an avatar during onboarding, so that I feel a personalized sense of belonging and ownership of my profile from day one.
- As a parent, I want to receive interactive coach marks on the dashboard immediately after completing onboarding, so that I can easily understand how to navigate key features like class summaries and rescheduling without needing to call support.
- As a user, I want the system to auto-save my onboarding progress, so that if I drop off mid-flow, I can return to a "Welcome Back" screen and continue exactly from where I left off without re-entering previously submitted data.
- As a student or parent, I want to see personalized course recommendations during onboarding based on my grade and interests, so that I can discover new subjects and claim a free trial class while I am most engaged with the platform.
- As a parent, I want the school name field to auto-suggest options as I type using Google Places, so that I can complete the academic details accurately and without the friction of manual entry.
- As a parent, I want the onboarding to reference my child's name directly (e.g., "Ensure Aditya's financial success") rather than generic pronouns, so that the experience feels tailored to my specific situation.

## Feature Scope

### In Scope

- Full onboarding flow redesign with Ms. Greenline conversational character
- Welcome screen and user identification (Parent vs. Student)
- Student profile setup: name, profile picture upload or default avatar selection, date of birth, gender
- Location and academic details: country, city, timezone auto-detection, school name via Google Places API, academic grade
- Student interests selection
- Parent details capture: names, occupations, phone numbers, emails
- Shipping/billing address capture
- Class scheduling interface with preferred days and time slots
- Teacher assignment logic (Recommended, Trial Class, Referral, or Sibling's Teachers categories)
- Tentative scheduling flow and dashboard tracker card when no teacher is immediately available
- Cross-sell recommendation flow: personalized course modal with free trial class incentive (next 7 days)
- Code of Conduct and Terms & Conditions acceptance
- Digital Student ID card generation
- Post-onboarding dashboard coach marks (interactive tooltips)
- Progress auto-save and "Welcome Back" resume flow for drop-offs
- Fuzzy logic for sibling/duplicate student detection
- Internal employee "masquerade" detection to skip onboarding for admin sessions
- Free/gift class card upon onboarding completion
- Real-time name personalization injected into conversational prompts

### Out of Scope

- SMS/WhatsApp phone verification (planned for v2)
- Email verification via gateway link (planned for v2)
- Automated image moderation (manual operational audits in v1; automated system planned for v2)
- Advanced teacher profile browsing during scheduling (dependent on Teacher Profile feature completion)

## Functional Requirements

1. **Dashboard Coach Marks (MUST HAVE)**: Interactive guides must trigger immediately after the user completes onboarding. They must walk the user through at minimum: joining a class, rescheduling a class, and tracking progress.
   - Acceptance Criteria: Coach marks must appear in sequence on the first dashboard load post-onboarding. They must be dismissible but must not be permanently skippable without completing the guided sequence at least once.

2. **Profile Picture Upload (MUST HAVE)**: Users must be able to upload a local image or select a default gender-based avatar.
   - Acceptance Criteria: Supported formats — JPEG, PNG. Minimum resolution: 100x100 px. Maximum file size: 5 MB. Images must go to an automated moderation queue (or manual audit in v1) before displaying on the profile. A preview-and-adjust step must be shown before submission.

3. **Cross-Sell Flow Integration (MUST HAVE)**: A recommendation modal must appear after the essential onboarding steps are completed, presenting personalized courses based on location, current enrolled course, and grade.
   - Acceptance Criteria: The recommendation engine must evaluate 15 distinct logic cases (factoring age, location, and enrolled vertical). If no valid recommendations exist for the student's profile, the entire cross-sell screen must be silently skipped. The user must be able to book a free demo slot within the next 7 days from this modal.

4. **Free/Gift Class Card (MUST HAVE)**: A free class must be granted upon onboarding completion to provide immediate perceived value.
   - Acceptance Criteria: The gift class card must appear on the dashboard immediately after onboarding and before the coach marks begin.

5. **Real-Time Name Personalization**: The conversational prompts must dynamically inject the enrolled student's name. For example, "Ensure Aditya's financial success" instead of "Ensure your child's financial success".
   - Acceptance Criteria: Once the student's name is captured in the onboarding flow, all subsequent conversational prompts must reference it by first name.

6. **Progress Auto-Save and Resume**: The system must save the user's onboarding progress after each completed step. If the user exits mid-flow and returns, they must be greeted with a "Welcome Back" screen and land at the last completed step.
   - Acceptance Criteria: Progress must persist across browser sessions (not just in-session). Returning users must not be asked to re-enter any previously submitted data.

7. **Fuzzy Logic Sibling Handling**: If a parent re-enrolls a child under a slightly different name or grade that fuzzy logic identifies as matching an existing student in the system, the system must trigger a confirmation flow.
   - Acceptance Criteria: On confirmation, credits from the old account must transfer to the new account, and the old duplicate record must be marked inactive. The flow must be labeled a "My Bad" recovery flow to keep the tone friendly.

8. **Internal User Bypass**: If an internal employee uses the admin masquerade option to log in as a student, the onboarding flow must be silently skipped.
   - Acceptance Criteria: The system must execute a "True User Check" on every onboarding session start. If the session is identified as internal/masquerade, redirect directly to the dashboard without triggering any onboarding steps or saving any onboarding data.

9. **Teacher Unavailability Handling**: If the scheduling step cannot find an available teacher for the user's preferred time slots, the system must not block the user.
   - Acceptance Criteria: Classes must be tentatively scheduled, and a dynamic progress tracker card must be added to the dashboard showing real-time progress on finding a teacher, including an ETA.

10. **School Name Autocomplete**: The school name input must integrate with Google Places API to provide real-time auto-suggestions as the user types.
    - Acceptance Criteria: Suggestions must appear after 2+ characters are typed. Selection must populate the field with the full school name. The field must also accept free-text entry for schools not in the database.

## UX/UI Flows

### Main Onboarding Flow (Step-by-Step)
1. **Welcome Screen**: User lands on a welcome screen introducing Ms. Greenline. The character sets a conversational, friendly tone.
2. **User Identification**: User is asked whether they are a Parent or a Student. This selection influences the tone and content of subsequent screens.
3. **Student Name Entry**: User enters the student's first and last name. Name fields must support multi-language characters.
4. **Profile Picture**: User is prompted to upload a photo or choose a default gender-based avatar. After selection, a preview-and-adjust step is shown. Image is submitted for moderation.
5. **Date of Birth**: User enters the student's date of birth.
6. **Gender Selection**: User selects the student's gender.
7. **Country and City**: User selects country, which populates the city dropdown and auto-sets the timezone.
8. **School Name**: User types the school name; Google Places API provides live autocomplete suggestions.
9. **Academic Grade**: User selects the student's current grade level.
10. **Student Interests**: User selects from a list of interest categories (e.g., coding, math, robotics).
11. **Parent Details**: User enters parent's name, occupation, phone number, and email.
12. **Shipping/Billing Address**: User enters the shipping/billing address.
13. **Class Scheduling**: User selects preferred days and time slots via a pop-up UI. The system recommends teachers (Recommended, Trial Class, Referral, or Sibling's Teachers). User selects a teacher. If no teacher is available, tentative scheduling occurs with a dashboard tracker card.
14. **Cross-Sell Modal**: After scheduling, a modal opens showing recommended courses based on the 15-case logic tree. User can select a course and book a free trial class within the next 7 days.
15. **Code of Conduct**: User reviews and accepts the Code of Conduct.
16. **Terms & Conditions**: User reviews and accepts Terms & Conditions.
17. **Student ID Generation**: The system generates a digital Student ID card as a celebration milestone.
18. **Dashboard + Coach Marks**: User lands on the dashboard. Interactive coach marks begin guiding them through key features.

### Profile Picture Upload Flow
1. User is prompted to upload an image.
2. User either uploads from their device (JPEG/PNG, max 5MB) or selects a default avatar.
3. User is guided on format and size requirements.
4. User previews and adjusts the image (crop/position).
5. User clicks submit; image enters the moderation queue.
6. The profile displays the image once approved (or immediately in v1 with manual audit).

### Cross-Sell Flow
1. Upon finishing essential onboarding steps, a modal opens showing recommended courses.
2. Courses are dynamically populated based on the 15-case logic tree (age, location, existing courses).
3. If no valid recommendations exist, the modal is silently skipped.
4. User clicks a course to view details and the free trial incentive.
5. User selects a course and is shown available demo slots in the next 7 days.
6. User selects a slot. A confirmation is sent and the class is added to the calendar.

### Drop-Off and Resume Flow
1. User exits the onboarding flow at any step after the name entry.
2. On their next login, instead of restarting, the system shows a "Welcome Back" screen.
3. The user is taken directly to the last completed step with all prior data preserved.

## Technical Requirements

- **Google Places API**: Integration with Google Places API (Place Autocomplete — Maps JavaScript API) is required for the School Name field's auto-suggestion functionality.
- **Zoom Integration**: The student's "Nick Name" from their profile must be passed into the Zoom joining link so it displays correctly during live classes. This must be set up during the onboarding profile step.
- **Cross-Sell Recommendation Engine**: A backend recommendation matrix must implement 15 distinct logic cases using Grade, Location, and Enrolled Vertical as inputs to determine which courses to show. This must be configurable and maintainable by the product team.
- **Image Moderation**: An automated moderation pipeline (or manual operational audit in v1) must process profile image uploads before they are publicly displayed. The system must flag inappropriate images.
- **Fuzzy Logic Engine**: A backend fuzzy matching service must compare new student name entries against existing students under the same parent account. Match threshold and confirmation flow logic must be defined and tested.
- **Progress Persistence**: Onboarding state (current step and all previously entered data) must be persisted server-side so it survives browser/session restarts.
- **Teacher Assignment Backend**: The teacher recommendation logic must categorize available teachers into four tiers (Recommended, Trial Class, Referral, Sibling's Teachers) and present them in that priority order during scheduling.
- **Masquerade Detection**: A "True User Check" must be implemented at the onboarding session start to detect admin masquerade sessions and bypass the flow.

## Non-Functional Requirements

- **Performance**: Profile picture file sizes are capped at 5 MB to optimize storage and load times. Students must have a minimum 10 Mbps internet connection for live classes (surfaced during onboarding setup guidance).
- **Device/Browser Support**: Students are required to join classes using a Mac or PC with the Zoom application. Onboarding must be fully functional on modern desktop browsers. Mobile onboarding support should be designed responsively.
- **Localization**: Name input fields must support multi-language character sets to accommodate the global student base. Timezone must be auto-populated based on the selected country. Date formats must respect locale conventions.
- **Accessibility**: Conversational prompts and form inputs must be keyboard navigable. Avatar selection and profile picture upload flows must have appropriate ARIA labels.

## Success Metrics

- **Revenue (Primary KPI)**: Fresh Revenue target of up to 6 Lacs per month generated through the cross-sell flow.
- **Refund Reduction**: Refund Amount Saved target of up to 3 Lacs per month through improved early experience and value delivery.
- **Conversion Rate**: Improving the lead-to-conversion rate, benchmarked against a 10% rate identified during the European sales team experiment.
- **Feature Adoption**: High adoption percentages across Business Teams, Students, and Parents to validate user satisfaction and efficient dashboard usage post-onboarding.
- **Course Enrollments**: Number of additional course enrollments generated through the cross-sell modal during onboarding.

## Edge Cases & Error Handling

- **Internal Employee Masquerade**: If an internal user (Sales/Support) uses the admin masquerade option to log in as a student, the "True User Check" must silently skip the onboarding flow entirely to prevent junk data from being captured in the onboarding dataset.
- **Teacher Unavailability**: If the system cannot find a suitable teacher for the user's chosen time slots, the user must not be blocked. Tentative scheduling must proceed, and a dynamic tracker card must be added to the dashboard showing real-time progress on teacher assignment with an ETA.
- **Duplicate Sibling Detection**: If a parent re-enrolls the same child under a slightly different name or grade, fuzzy logic must detect the similarity and trigger the "My Bad" recovery flow — combining accounts and transferring credits instead of creating a duplicate profile.
- **No Cross-Sell Matches**: If the backend logic evaluates the student's profile and finds no valid course recommendations across all 15 cases, the cross-sell screen must be entirely skipped without any error message or empty state shown to the user.
- **Profile Image Rejected by Moderation**: If a submitted profile picture is flagged as inappropriate, the system must notify the user and prompt them to reupload. The old image (or default avatar) must remain displayed until a valid image is approved.
- **School Not Found in Google Places**: If the user's school does not appear in Google Places autocomplete results, the field must accept free-text entry to prevent blocking the flow.

## Dependencies

- **Team Coordination**: The feature requires involvement from Product Management, Design, Tech, QA, and Customer Success teams. All teams must be aligned before sprint planning begins.
- **Teacher Profile Data Quality**: The new scheduling flow is strictly dependent on having updated, high-quality teacher profiles. Teachers must complete a required Google Form; this data must be populated into the database before the scheduling step can function. Failure to populate teacher data is cited as a blocker that could delay the release.
- **Future v2 Dependencies**:
  - SMS/WhatsApp API integration for phone number verification
  - Email gateway API for email verification links
  - Automated image moderation system (replacing the v1 manual audit)
- **Cross-Sell Logic Sign-Off**: The 15-case recommendation matrix must be reviewed and signed off by the Business and Product teams before implementation begins to ensure commercial viability.
- **Zoom API**: Zoom integration for passing student nicknames into joining links must be configured and tested as part of the onboarding setup phase.
