---
title: Unified Demo & Paid Experience - Student
category: product-prd
subcategory: student-lifecycle
source_id: bf077f6b-5581-44ab-a090-b1192979ae70
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Unified Demo & Paid Experience - Student

## Overview

The Unified Demo & Paid Experience initiative revamps the BrightCHAMPS student-facing dashboard to create a single, cohesive product experience for both demo (trial) students and fully enrolled paid students. Historically, the demo and paid experiences were siloed, leading to inconsistency in interface and engagement patterns. This project merges both into one dashboard architecture, where the content and features shown adapt based on the student's enrollment status.

The revamped dashboard is built around three primary modules: a Global Feed (a video showcase of student projects globally), a personal My Feed (a personalized stream of class updates, reminders, and tasks), and a Course Explorer (a structured navigation tool for lessons, homework, and quizzes). These modules serve dual purposes — engaging demo students enough to convert, and keeping paid students invested in their learning journey.

The primary business objective is to improve the Lead to Completion % in the USA from the current range of 36–39% to a target of 60%. The Cost Per Deal is the core business tracking metric for this initiative. A survey of approximately 6,000 parents revealed that the top parent expectations are reminders, engaging and interactive content, clear communication, and flexible scheduling — all of which this experience is designed to address.

## Problem Statement

BrightCHAMPS's pre-demo attendance and in-demo engagement are lower than target. Parents surveyed (n ~6,000) cited three primary unmet needs: timely reminders, interactive content, and clear communication. The current dashboard does not serve demo students with the same richness as paid students, and the experience lacks the engagement hooks needed to drive demo completion and subsequent enrollment. The unified experience aims to close this gap by building a single dashboard that delivers engagement, motivation, and clarity to students at every stage of the lifecycle.

## User Stories

- As a student, I want to scroll through a Global Feed of project videos from students worldwide, so that I can be inspired by my peers' creative work and feel motivated to continue learning.
- As a student, I want to see an Upcoming Class Reminder Card prominently at the top of my personal feed, so that I can join my next class on time without hunting for the session link.
- As a student, I want to view my pending homework and quizzes directly in my feed, so that I can track tasks and submit them before my next class without navigating away.
- As a student, I want to receive a Class Completion Card after finishing a module, so that I can read my teacher's feedback and celebrate the achievement with my family.
- As a student, I want to navigate my full course journey via the Course Explorer tab, so that I can clearly see my progress across lessons, homework, and quizzes at any time.

## Feature Scope

### In Scope

- Revamped unified student dashboard with a Left Side-Bar and Right Side-Bar
- Left Side-Bar navigation: Explore, Learn, Arena, Nano Skills, and Rewards tabs
- Right Side-Bar: Profile, Schedule, Updates, and Critical Information panels
- Module 01 — Global Feed: infinite-scroll video showcase of popular student projects globally with watch, celebrate, and share interactions
- Module 02 — My Feed (Student's Personal Feed): personalized stream with class update cards including:
  - Upcoming Class Reminder Card
  - Homework / Quizzes Pending Card
  - Class Completion Card (with teacher feedback)
  - Certificate Achievement Card
  - Missed Class Card
- Module 03 — Course Explorer: three-tab navigation (Lessons, Homework, Quizzes) with closed and expanded module card views
- Timezone and Language dropdown support (localization baseline)
- Mobile-responsive design (Figma mobile designs linked)

### Out of Scope

- Arena tab (explicitly deferred to a future scope)
- Project Tags in the Global Feed (explicitly deferred)
- Course Explorer detail pages (handled under the Gurukul: Middle Layer initiative separately)
- Post-enrollment payment flows
- Teacher-facing dashboard

## Functional Requirements

1. **Global Feed Video Autoplay**
   - Videos must autoplay in a muted state while the user scrolls.
   - If a user clicks to activate sound, sound must remain on for all subsequent videos in the session.
   - If two videos are simultaneously on screen: the first video must mute when less than 50% of it is visible, and the second video must automatically unmute.
   - Acceptance criteria: Autoplay and sound logic verified on mobile and desktop across Chrome, Safari, and Firefox.

2. **Global Feed Ordering and Featuring**
   - Videos must be ordered by publish date by default.
   - The top 10 videos with the most reactions in the past 24 hours must be prioritized and may receive a "featured" tag.
   - Acceptance criteria: Featured videos appear in the top 10 positions; ordering verified via admin/test data.

3. **Upcoming Class Reminder Card**
   - Must display: class number, lesson title, lesson image/GIF, student name, teacher name, class time, and a prominently colored "Join The Class" button.
   - Teacher name display rule: use first name unless it is fewer than 3 characters, in which case use the full name.
   - Acceptance criteria: All required fields rendered; edge case for short teacher names tested.

4. **Homework / Quizzes Pending Card**
   - Must display all pending assignments and quizzes with a "Submit Assignment" CTA.
   - If only one assignment is pending: user is taken directly to that assignment on click.
   - If multiple assignments are pending: user is routed to the Homework tab in the Course Explorer.
   - Acceptance criteria: Single and multi-assignment routing tested and verified.

5. **Class Completion Card**
   - Displayed after a student completes a module.
   - Must include teacher feedback.
   - Acceptance criteria: Card appears in My Feed within one class session post-completion; teacher feedback content is visible.

6. **Missed Class Card**
   - If a student misses a scheduled class, a "Your teacher missed you!" card must appear in My Feed.
   - Must include a CTA to "Schedule a makeup class."
   - Acceptance criteria: Card appears in My Feed within 1 hour of the missed class window.

7. **Course Explorer — Lessons Tab**
   - Module cards must support two states: Closed Version (basic info and progress indicator) and Expanded Version (full list of lessons with status and clickable GIFs/tags).
   - The active (current) module must be expanded by default at the top of the list.
   - Completed/previous module cards must cascade below the active module in a collapsed state.
   - Acceptance criteria: Active module auto-expanded on page load; all module states render correctly.

8. **Course Explorer — Homework and Quizzes Tabs**
   - Must display all pending and submitted homework and quiz items with status indicators.
   - Acceptance criteria: Items sorted by due date; status (pending/submitted/graded) displayed correctly.

9. **Curriculum Metadata Display**
   - The Course Explorer must consume and display the following metadata from the curriculum backend: 1-liner module description, module image, lesson GIF, and lesson tags.
   - Acceptance criteria: All metadata fields rendered; missing metadata handled gracefully with fallback states.

10. **Dashboard Layout and Navigation**
    - Left Side-Bar must always be visible and allow navigation between Explore, Learn, Arena, Nano Skills, and Rewards tabs.
    - Right Side-Bar must display Profile, Schedule, Updates, and Critical Information panels.
    - Arena tab must be visible in the nav but disabled/coming-soon state for current scope.
    - Acceptance criteria: Navigation tested across mobile and desktop; Arena tab labeled appropriately.

## UX/UI Flows

### Flow 1: Global Feed Infinite Scroll
1. Student lands on the Explore tab, which defaults to the Global Feed.
2. Videos load and autoplay muted as the student scrolls down.
3. Student taps a video to activate sound; all subsequent videos play with sound.
4. If two videos appear on screen simultaneously, the first mutes (< 50% visible) and the next auto-unmutes.
5. Feed loads more videos as student reaches the bottom (infinite scroll).

### Flow 2: Upcoming Class — Join Flow
1. Student lands on My Feed (Learn tab or home view).
2. Upcoming Class Reminder Card appears at the top with class number, lesson title, lesson image, teacher name, and class time.
3. Student taps "Join The Class" button.
4. Student is taken directly to the class session.

### Flow 3: Homework Submission Flow
1. Student sees a Homework / Quizzes Pending Card in My Feed.
2. Student taps "Submit Assignment."
3. If one assignment is pending: student is taken directly to that assignment page.
4. If multiple assignments are pending: student is routed to the Homework tab in the Course Explorer.
5. Student completes and submits the assignment.

### Flow 4: Course Explorer Navigation
1. Student taps the Learn tab and navigates to Course Explorer.
2. Lessons tab is displayed by default; the active module is expanded at the top.
3. Student scrolls down to see all previous (completed) module cards in collapsed/closed state.
4. Student taps a closed module to expand it and view lesson list with statuses and GIFs.
5. Student taps a lesson GIF or tag to navigate to the lesson detail page (handled by Gurukul Middle Layer).
6. Student switches between Lessons, Homework, and Quizzes tabs to review overall progress.

### Flow 5: Missed Class Card
1. Student misses a scheduled class.
2. Within 1 hour, a "Your teacher missed you!" card appears in the student's My Feed.
3. Student taps "Schedule a makeup class" CTA.
4. Student is routed to the rescheduling flow.

## Technical Requirements

- **Gurukul: Middle Layer Integration**: The Global Feed video content must be sourced from the Gurukul Middle Layer initiative. The Course Explorer detail/lesson pages are also handled under this initiative. Both must be delivered before the full Course Explorer experience can go live.
- **Curriculum Backend Metadata**: The curriculum backend must supply: 1-liner module description, module image, lesson GIF, and lesson tags for all modules. API contract to be defined with the curriculum team.
- **Video Autoplay Logic**: Frontend must implement a visibility-threshold-based autoplay/mute system (< 50% visibility = mute trigger for first video; auto-unmute for the next).
- **Event and Event Schema**: The document references a link to Events & Event Schema; all user interactions on the dashboard (video plays, card clicks, tab navigations, class joins) must be tracked via the event schema.
- **Timezone and Language Support**: The dashboard must support a Timezone dropdown (e.g., "Asia/Kolkata") and a Language dropdown (e.g., "English") stored in user profile settings.
- **Mobile-Responsive Design**: All modules must be responsive; Figma mobile designs must be implemented alongside desktop.
- **FAQs and Tech Alignment**: Tech has been consulted (per "FAQs - Discussed with Tech" reference in document); final API contracts and event schemas must be formalized.

## Non-Functional Requirements

- **Performance**: Dashboard load must be under 2 seconds. Mode detection (demo vs. paid) is a single DB lookup indexed on student_id. Feature gates evaluated client-side post-mode flag receipt.
- **Localization**: Timezone (e.g., Asia/Kolkata) and Language (e.g., English) dropdowns are present, indicating baseline multi-region/multi-language support.
- **Mobile Support**: Full mobile responsiveness required; Figma mobile designs are linked and must be implemented.
- **Browser Support**: Not explicitly specified; standard modern browser support (Chrome, Safari, Firefox, Edge) should be targeted.
- **Accessibility**: Not explicitly specified in source; WCAG 2.1 AA should be applied as a baseline.
- **Video Fallbacks**: If a video fails to load, the feed must skip gracefully and load the next item without a blank screen.
- **Metadata Fallbacks**: If curriculum metadata (image, GIF, tags) is missing for a module, the UI must display a fallback/placeholder state without breaking the layout.

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Lead to Completion % (USA) | 36% – 39% | 60% |
| Cost Per Deal | Current (tracking) | Reduce |

- The primary KPI is the Lead to Completion percentage for the USA market.
- Secondary engagement metrics: Global Feed watch time, Class Reminder Card click-through rate ("Join The Class" taps), Homework submission rate from the Pending Card CTA.

## Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| Parent submits homework with multiple assignments pending | Route to Homework tab in Course Explorer rather than a single assignment page |
| Teacher's first name is fewer than 3 characters | Display full name in the Upcoming Class Reminder Card |
| Student misses a scheduled class | Display "Your teacher missed you!" Missed Class Card in My Feed within 1 hour; provide makeup scheduling CTA |
| Global Feed video fails to load | Skip gracefully; load next video in feed; no blank/broken card visible |
| Curriculum metadata (GIF, image, tags) is missing for a module | Display fallback/placeholder content; do not break Course Explorer layout |
| Arena tab clicked by student (out of scope) | Show a "Coming Soon" state; do not route to a broken page |
| Student has no upcoming classes | Upcoming Class Reminder Card is hidden; My Feed shows other active cards |

## Dependencies

| Dependency | Owner | Notes |
|------------|-------|-------|
| Gurukul: Middle Layer Initiative | Tech | Required for Global Feed video content and Course Explorer detail pages |
| Curriculum Backend Metadata | Curriculum Team | Must provide module descriptions, images, lesson GIFs, and tags before Course Explorer launch |
| Event Schema | Tech | Required for tracking all dashboard interactions |
| Figma Design Finalization | Design | Mobile and desktop Figma files must be finalized before frontend implementation |
| QA Sign-off | QA (Vidurbh Raj Srivastava) | Full regression across demo and paid modes on mobile and desktop |
| Product / Business Alignment | Shivam Sharma, Paul | Business track is "Cost Per Deal"; metric targets must be signed off |
