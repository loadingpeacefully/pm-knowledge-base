---
title: Dashboard Multi-Language Support
category: product-prd
subcategory: student-lifecycle
source_id: 9527ddd9-e399-41f6-97ce-7b845eb51797
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Dashboard Multi-Language Support

## Overview

BrightChamps (Schola platform) operates in multiple international markets, including Vietnam, Thailand, and Indonesia. A significant portion of its students and parents are non-English speakers, and the current English-only dashboard interface creates a direct barrier to engagement, comprehension, and retention for these users. The Dashboard Multi-Language Support feature addresses this by integrating a language selector into the platform that translates all user interface elements — buttons, labels, navigation items, and content — into the user's preferred language.

The feature is first surfaced during onboarding, where users are prompted to set their language preference immediately, ensuring a localized experience from the very first interaction. Users can also change their language at any time via a drop-down selector in the left side navigation menu. Once set, the preference is stored in the backend so that the user's chosen language is applied consistently regardless of the device they use to log in.

The supported languages at launch are Vietnamese, Thai, Bahasa Indonesia, and English, chosen to align with the demographics of BrightChamps' core non-English-speaking markets. The business goal is to improve platform accessibility and inclusivity, driving higher engagement and retention among non-English speaking students and educators globally.

## Problem Statement

Language barriers are limiting the platform's reach and user engagement in non-English-speaking markets. Students, parents, and educators who do not read English fluently are unable to navigate the dashboard confidently, reducing their ability to access educational content, track progress, and interact with teachers and course materials. Without localization, BrightChamps cannot serve these markets effectively, and the platform risks losing users to competitors with native-language offerings. The product needs a robust, extensible multi-language system that can be expanded to new locales as the company grows.

## User Stories

- As a non-English speaking student, I want to select my native language during onboarding, so that I can navigate the dashboard and access educational content without language barriers.
- As an educator in a non-English speaking region, I want to view the platform navigation and interface in my preferred language, so that I can create and manage content and interact with students more efficiently.
- As a parent with limited English proficiency, I want to receive notifications and course updates in my preferred language, so that I can stay informed about my child's learning progress.
- As a platform user, I want my language preference to be saved to my profile and persist across devices, so that I always see the dashboard in my chosen language regardless of where I log in.
- As a user, I want to be able to change my display language at any time from the navigation menu, so that I can switch between languages without needing to contact support or reinstall the app.

## Feature Scope

### In Scope

- Language preference prompt during onboarding (first-time user setup)
- Language drop-down selector in the left side navigation menu
- Translation of all UI elements: buttons, labels, navigation items, and interface copy
- Support for four languages at launch: Vietnamese, Thai, Bahasa (Indonesian), and English
- Backend storage of language preference linked to the user profile
- Cross-device consistency: preference applies whenever the user logs in on any device
- Localized content delivery based on the stored preference

### Out of Scope

- Translation of user-generated content (e.g., student assignments, teacher notes)
- Machine translation of course curriculum content (separate localization effort)
- Real-time translation of live class sessions
- Languages beyond the four initial launch languages (extensibility is planned for the roadmap)
- Right-to-left (RTL) language support (e.g., Arabic, Hebrew)

## Functional Requirements

1. **Onboarding Language Selection**
   - During onboarding, the system must present the user with a language selection prompt before they reach the main dashboard.
   - The available options must include: Vietnamese, Thai, Bahasa, and English.
   - The selected language must be stored and applied immediately to the rest of the onboarding flow.
   - Acceptance criteria: First-time users see the language prompt; selection is saved; subsequent pages render in the chosen language.

2. **Navigation Menu Language Selector**
   - A drop-down language selector must be accessible from the left side navigation menu at all times when the user is logged in.
   - The selector must display the currently active language and allow the user to switch to any of the four supported languages.
   - Switching language must re-render the UI in the selected language without requiring a full page reload (or with minimal disruption).
   - Acceptance criteria: Language selector is present in the nav menu; switching language updates all UI strings; selection persists after the change.

3. **UI Translation Coverage**
   - The language selector must translate all user interface elements, including buttons, labels, navigation items, and system-generated messages.
   - Acceptance criteria: No untranslated English strings are visible to a user with a non-English language preference set; all interactive and informational UI elements render in the selected language.

4. **Backend Storage of Language Preference**
   - The user's language preference must be stored in the backend as part of the user profile.
   - On every login and dashboard load, the system must retrieve the stored preference and apply it.
   - Acceptance criteria: Language preference persists across sessions; logging in on a different device applies the same language preference; updating the preference is reflected immediately.

5. **Cross-Device Consistency**
   - The language preference stored in the backend must be device-agnostic and must apply on any device the user logs into.
   - Acceptance criteria: A user who sets Vietnamese on mobile sees Vietnamese on desktop on next login without needing to set it again.

## UX/UI Flows

### Flow 1: Onboarding Language Selection

1. A new user begins the onboarding process after creating an account.
2. Before reaching the main dashboard, the system displays a language selection screen or prompt.
3. The user is shown the four available languages: Vietnamese, Thai, Bahasa, English.
4. The user selects their preferred language.
5. The system saves the selection to the user's profile in the backend.
6. The remainder of the onboarding flow renders in the selected language.
7. The user reaches the main dashboard, which is fully displayed in their chosen language.

### Flow 2: Changing Language from the Navigation Menu

1. The user is logged in and viewing the dashboard in their current language.
2. The user opens the left side navigation menu.
3. The user locates and clicks the language drop-down selector.
4. The drop-down displays the four available language options with the current language highlighted.
5. The user selects a new language.
6. The system updates the UI in real time to render all elements in the newly selected language.
7. The system saves the updated preference to the backend.
8. On the user's next login, the dashboard loads in the updated language preference.

## Technical Requirements

- **Backend Language Preference Storage:** The user profile data model must include a `language_preference` field (e.g., locale code: `vi`, `th`, `id`, `en`). A `PATCH /user/preferences` endpoint (or equivalent) must support updating this field.
- **Locale-Aware API Responses:** Backend APIs should accept a `lang` query parameter so that server-rendered content (course listings, notifications, feed content) can be returned in the appropriate locale.
- **Frontend i18n Layer:** The frontend must implement an internationalization (i18n) framework (e.g., i18next, react-intl, or equivalent) with a locale context provider. String bundles for each supported language must be maintained and served — ideally from a CDN for performance.
- **String Bundle Management:** A translation management system or CMS must store locale-specific string bundles. New language additions must not require code changes — only new string bundle files.
- **Content Management System (CMS):** Course metadata, feed copy, and notification templates must have multi-locale content entries in the CMS to support locale-filtered delivery.
- **Fallback to English:** If a string is not available in the user's selected language, the system must fall back to the English string rather than displaying a blank or broken UI.
- **Locale Detection on First Login:** For users who have not set a preference, the system should detect locale from the device/browser language setting as a default starting point before the onboarding prompt.

## Non-Functional Requirements

- **Performance:** String bundles must be CDN-served to minimize load time. Initial dashboard load with locale detection must complete within an acceptable threshold (target: under 1.5 seconds). String bundle fetching must not block the initial render.
- **Extensibility:** The architecture must support adding new languages by adding new string bundle files without requiring application code changes. This is critical for scaling to new markets.
- **Consistency:** All UI areas — navigation, buttons, notifications, course listings, error messages — must render consistently in the selected language. Partial translations (some elements in English, some in the selected language) are not acceptable.
- **Localization Quality:** Translations must be reviewed by native speakers or professional translators, not generated by machine translation alone, to ensure accuracy and cultural appropriateness.
- **Accessibility:** Language switching must be accessible via keyboard navigation. The language selector must have appropriate ARIA labels for screen reader support.
- **Device and Browser Support:** The feature must work on all browsers and devices supported by the existing platform (web, mobile web, and mobile app where applicable).

## Success Metrics

The source document includes an "Impact Funnel" section with the following metric categories, though specific target values had not been defined at the time of writing:

- **Improvement Metric:** Target improvement in user engagement or comprehension scores for non-English speaking users.
- **Funnel Metric:** Conversion rate improvement (onboarding completion, course enrollment) for users who use a non-English language setting.
- **Expected Adoption %:** Percentage of non-English-speaking users who select a non-English language after the feature is launched.
- **Expected Impact:** Measured improvement in retention or course completion rates in target markets (Vietnam, Thailand, Indonesia).

Proxy metrics to track:
- Number of active users with a non-English language preference set
- Bounce rate change on the dashboard for non-English speaking users post-launch
- Support ticket volume related to language/navigation confusion

## Edge Cases & Error Handling

- **Missing Translation (Untranslated String):** If a UI string has not yet been translated for the selected language, the system must fall back to the English version of that string rather than displaying a key name or blank. A background job should flag untranslated strings for the content team.
- **New User Without Preference:** A new user who skips the onboarding language selection (or comes from a context where it is not surfaced) should have the platform default to English, with an easy path to change via the navigation menu.
- **Browser Language Fallback:** For users with no stored preference, the system should attempt to match the device/browser language to one of the four supported languages. If no match is found, English is used.
- **Course Not Available in Selected Language:** If a course or piece of content is not available in the user's selected language, it should be displayed in English with a clear label indicating the original language, rather than being hidden or showing a blank state.
- **Language Preference Sync Failure:** If the backend fails to save an updated language preference, the user should see a toast or error message, and the local session should retain the change even if it cannot be persisted immediately.

## Dependencies

- **CMS with Multi-Locale Support:** Course metadata, notifications, and feed content must be stored with locale variants in the CMS. This is a prerequisite for content-level localization.
- **Translation Management System:** A tool or workflow for managing translations across string bundles is needed to scale the translation effort and onboard new languages.
- **User Profile Service:** The language preference field must be added to the user profile data model and exposed via the profile API.

### Teams Involved

| Team | Role |
|---|---|
| Product | Owner: Darshan Patil; feature scoping and prioritization |
| Design | UI/UX design for language selector, onboarding prompt, and locale-aware layouts |
| Tech | i18n framework implementation, backend API updates, CMS integration, CDN setup |
| Customer Success | Input on most impactful languages by market; user feedback post-launch |
| QA | Testing all four locales across all UI surfaces; regression testing on language switch |
