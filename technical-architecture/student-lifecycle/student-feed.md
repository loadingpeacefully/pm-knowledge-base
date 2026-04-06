---
title: Student Feed
category: product-prd
subcategory: student-lifecycle
source_id: 8d664dc5-3a02-4adf-92c8-3c393863e78e
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Student Feed

## Overview

The Student Feed is a dedicated page on the student dashboard that serves as a centralized hub aggregating all key updates about a student's academic journey. It addresses the critical gap in the current platform where there is no unified, interactive space for students, parents, and teachers to track and engage with educational milestones, homework deadlines, class schedules, and achievements.

Currently, students and parents struggle to keep up with the pace of their learning journey because updates are scattered across multiple surfaces — class notifications, assessment reminders, and achievement badges all arrive through disparate channels with no single source of truth. The Student Feed solves this by consolidating all of this information into a single, real-time, chronologically sorted stream that drives consistent daily engagement with the platform.

The business goal of the feature is to enhance student engagement and provide real-time, personalized educational insights in a user-friendly manner, ultimately driving customer success and retention. It is designed to make the student dashboard a habit-forming destination rather than a utility visited only before or after class.

## Problem Statement

There is a lack of a centralized, interactive platform that effectively tracks and showcases students' educational progress and achievements. Students and parents find it challenging to keep up with educational milestones, homework, and class schedules, which leads to decreased student engagement and inefficient learning tracking. Without a feed-style interface, students are not reminded of upcoming responsibilities, achievements go unacknowledged, and the emotional reward loop of learning is never completed — resulting in poor retention and lower course completion rates.

## User Stories

- As a student, I want to receive timely information on new assessments and automated homework reminders, so that I can keep track of my academic responsibilities and deadlines without relying on external communication.
- As a student or parent, I want to receive notifications for completed and missed classes, so that I can better manage my schedule and address any gaps in attendance promptly.
- As a teacher, I want to view the feed of my respective students, so that I can reply to comments and answer questions asked by students in a contextually relevant way.
- As a student, I want to showcase achievements like new certificates and badges in my feed, so that I feel encouraged by positive reinforcement and the learning journey feels rewarding.
- As a student, I want the upcoming class to always be pinned at the top of my feed, so that I can quickly find and join my next session without scrolling through past activity.

## Feature Scope

### In Scope

- A dedicated Student Feed page on the student dashboard
- Profile pictures for students, teachers, and the BrightChamps company logo
- Dynamic time/date stamps that format based on elapsed time (e.g., "Just Now", "x hours ago", "x days ago")
- Comments component supporting Likes and Replies (single level only)
- Class Cards showing upcoming, live, and completed class states with contextual CTAs
- Assessment Cards surfacing new assessments and quizzes
- Certificate Cards celebrating milestone completions
- Badge Cards for gamified achievement recognition
- Infinite scroll pagination (max 10 posts or last 2 weeks of activity)
- Upcoming Class pinned at top of feed
- Feed sorted in descending order of post date/time (latest on top)
- Comments sorted in ascending order of creation date
- Auto-generated feed content based on student milestones and tasks
- A/B testing framework for measuring adoption impact

### Out of Scope

- Manual post creation by students or parents (feed is auto-generated only)
- Direct messaging between students and teachers (replies are limited to comment threads)
- Nested replies (users cannot reply to a reply — one layer only)
- Push notifications or email digests for feed updates (separate notification system)
- Feed filtering or categorization by content type (in this version)

## Functional Requirements

1. **Feed Aggregation**: The feed must auto-generate posts based on milestones, achievements, and tasks from the student's learning journey. No manual posting is required from the student or parent.
   - Acceptance Criteria: New class events, assessments, certificates, and badges must appear in the feed within a defined latency window after the triggering event occurs.

2. **Upcoming Class Pinning**: The Upcoming Class card must always be pinned to the top of the feed regardless of post date.
   - Acceptance Criteria: Even if a more recent feed item exists (e.g., a just-awarded badge), the upcoming class card must remain in the top position.

3. **Feed Sorting**: Remaining posts below the pinned upcoming class must be sorted in descending order of post date/time (most recent first).
   - Acceptance Criteria: If two posts share the same timestamp, secondary sort by post type priority.

4. **Infinite Scroll Pagination**: The feed must load a maximum of 10 posts or all posts within the last 2 weeks, whichever is smaller, using infinite scroll behavior.
   - Acceptance Criteria: On initial load, render up to 10 posts. As the user scrolls to the bottom, load the next batch. Do not show a "Load More" button.

5. **Comment Sorting**: Comments on any feed post must be sorted in ascending order of their creation date (oldest first, newest last).
   - Acceptance Criteria: When a new comment is added, it appends to the bottom of the comment thread.

6. **Reply Constraints**: Users must only be allowed one layer of replies. A user cannot reply to an existing reply.
   - Acceptance Criteria: The "Reply" action must be hidden or disabled on all replies. Only top-level comments support replies.

7. **Like Interaction**: Users can like any comment. Clicking "Like" must transition the button from a default to a selected/reacted state and increment the like counter.
   - Acceptance Criteria: The like state must persist on page refresh. The counter must increment by exactly 1 per user per comment.

8. **Class Card States**: A class card must dynamically change its displayed state over time:
   - Upcoming (>2 hours to class): Shows date/time, lesson name, reschedule CTA, view notes CTA.
   - Upcoming (<2 hours to class): Transitions to a more prominent join-ready state.
   - Live: Indicates the class is currently in session.
   - Completed (attended): Shows "Class Feedback Pending" until teacher feedback is submitted; then expands to show revision video, class notes, and teacher feedback.
   - Completed (missed, student duration = 0 mins): Shows a specific "Class Missed" alert state.

9. **Profile Picture Fallback**: If a teacher has not uploaded a profile image, the system must display a default image using the first character of their first name.
   - Acceptance Criteria: The fallback renders consistently across all card types and comment avatars.

10. **Dynamic Time Stamps**: Feed posts and comments must display dynamically formatted timestamps:
    - Feed posts: "Just Now" (<10 mins), transitioning to "x hours ago", then "x days ago", then specific "DD Mon YYYY" format.
    - Comments: Abbreviated format — "Now", "x h", "x d", "x w", "x y".

## UX/UI Flows

### Main Feed Load Flow
1. User navigates to the Student Dashboard and clicks on the Feed tab.
2. The system loads the feed with the Upcoming Class card pinned at the top.
3. Below the pinned card, the remaining posts are loaded in reverse chronological order (latest first).
4. The user scrolls down; infinite scroll triggers additional post loading up to the 10-post or 2-week limit.
5. Each post displays a profile picture (student, teacher, or BrightChamps logo), a dynamic timestamp, and relevant content.

### Class Card Lifecycle Flow
1. A class is scheduled in the system and a Class Card appears in the feed with "Upcoming" state, showing date/time, lesson name, reschedule CTA, and view notes CTA.
2. As the class start time approaches (<2 hours), the card state transitions to a prominent countdown state.
3. When the class starts, the card state changes to "Live".
4. After the class ends:
   - If student attended: Card enters "Class Feedback Pending" state. Once the teacher submits feedback, the card expands to show the revision video, class notes, and teacher feedback.
   - If student did not attend (duration = 0 mins): Card enters "Class Missed" alert state with a prompt to reschedule.

### Comment Interaction Flow
1. A user views a feed post that has a comments section.
2. The user clicks "Like" on a comment — the like button transitions to a selected state and the counter increments.
3. The user clicks "Reply" on a top-level comment — a reply input field appears.
4. The user types their reply and submits — the reply appears below the parent comment in ascending chronological order.
5. If the user attempts to click "Reply" on an existing reply, the action is blocked (button not shown).

### Achievement Highlight Flow
1. A student earns a new certificate or badge in the system.
2. An auto-generated Certificate Card or Badge Card appears in the feed with the relevant achievement details.
3. The student or parent can view the achievement, share the certificate, and optionally like or comment.

## Technical Requirements

- **Feed Content Generation**: The feed content is entirely auto-generated. The backend must listen to events from the student's learning journey (class completions, assessment submissions, badge/certificate awards) and create corresponding feed post records.
- **Time Formatting Logic**: The system requires server-side or client-side dynamic date/time formatting logic with specific thresholds:
  - Feed posts: <10 mins → "Just Now"; <1 hour → "x mins ago"; <24 hours → "x hours ago"; <7 days → "x days ago"; else → "DD Mon YYYY"
  - Comments: "Now" → "x h" → "x d" → "x w" → "x y"
- **Like State Persistence**: Like states per user per comment must be stored in the database and returned on feed load.
- **Infinite Scroll API**: The feed API must support cursor-based pagination to enable seamless infinite scroll behavior.
- **Comment Threading**: Comment data model must support a single level of parent-child relationship (top-level comment → replies). Replies to replies must be rejected at the API layer.
- **Teacher Feed Access**: Teachers must have read access to the feeds of their assigned students and write access to post replies.
- **A/B Testing Infrastructure**: The rollout must be gated behind a feature flag to support A/B testing. Adoption and engagement metrics must be tracked per variant.

## Non-Functional Requirements

- **Performance**: The feed must use infinite scroll to ensure the initial page load is not blocked by loading all historical posts. Initial load target should render the first 10 posts within an acceptable response time (exact target TBD with Tech team).
- **Accessibility**: Profile picture fallback characters must meet minimum contrast ratios. Timestamp labels and card CTAs must be screen-reader accessible.
- **Localization**: Dynamic timestamp labels ("Just Now", "x hours ago") should be designed for localization into supported languages. Date formats (DD Mon YYYY) should respect locale conventions.
- **Browser/Device Support**: The feed page must be fully functional on modern desktop and mobile browsers. Exact device support matrix to be confirmed with the Tech team.

## Success Metrics

- **Primary Goal**: Improvement in student engagement and overall customer success scores.
- **Adoption Measurement**: The rollout will be gated behind A/B testing. Feature adoption will be measured comparing the variant (feed enabled) against the control (no feed).
- **Metric Framework**: The document outlines a framework tracking "Improvement Metric Value", "Current Adoption %" and "Expected Impact" — specific numerical targets are to be populated post-A/B test baseline.
- **Engagement Signals**: Likes per session, replies per session, and return visits to the feed page are implied engagement signals.

## Edge Cases & Error Handling

- **Missing Teacher Profile Picture**: If a teacher has not uploaded a profile image, the system falls back to a default avatar displaying the first character of their first name. This fallback must be visually consistent with the uploaded image display.
- **Class Missed State**: If a student's class duration is logged as 0 minutes, the system must trigger the "Class Missed" card state instead of the standard completed state. This must not be confused with a class that hasn't happened yet.
- **Nested Reply Attempt**: If a user attempts to reply to an existing reply, the system must prevent this interaction. The "Reply" CTA should not be rendered on reply-level comments.
- **Empty Feed**: If a student has no feed activity in the last 2 weeks and no upcoming class, the feed must display an empty state with an appropriate message (e.g., an encouraging prompt to attend their next class or complete an assessment).
- **Feed Post Generation Failure**: If an event fires but the corresponding feed post fails to generate, the system must log the failure for debugging without surfacing an error to the student.

## Dependencies

- **Content Generation System**: The entire feature depends on auto-generated data sourced from the student's learning journey. Any gaps in event tracking (class attendance, assessment completion, badge awards) will result in an incomplete feed.
- **Teacher Assignment System**: For teacher profile pictures and teacher-authored replies to render correctly, teachers must be properly assigned to students in the backend.
- **A/B Testing Infrastructure**: Full adoption decisions and subsequent feature iterations depend on the results of the planned A/B test. The feature flag and analytics instrumentation must be in place before launch.
- **Tech Team Sign-off**: The document notes "Discussed with Tech" under FAQs, indicating that key implementation decisions (pagination strategy, feed generation latency) require Tech team alignment before finalization.
- **Design System**: Dynamic card components (Class Card, Assessment Card, Certificate Card, Badge Card) must align with the existing BrightChamps design system to ensure visual consistency.
