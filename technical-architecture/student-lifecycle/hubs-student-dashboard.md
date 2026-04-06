---
title: Hubs Student Dashboard
category: product-prd
subcategory: student-lifecycle
source_id: 17df3841-dc20-4400-a4ce-a69ff6a6fb8b
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Hubs Student Dashboard

## Overview

The Hubs Student Dashboard is a centralized, user-friendly interface designed to give students real-time access to their class schedules, credits, post-class feedback, assignments, and multimedia content from their sessions. It is part of the broader Hubs Migration initiative — a platform-level upgrade to consolidate the student experience into a single, coherent surface.

The dashboard surfaces the most relevant information a student needs at any given point in their learning journey: what classes are coming up, how many credits remain, what was covered in a past class, and whether any assignments or quizzes need attention. The design supports three distinct class states — Pre-class, Post-class, and Class-Missed — each rendering a tailored view with contextually appropriate content.

The business goal is to improve student engagement, reduce support queries around scheduling and credits, and ensure students feel informed and supported before, during, and after their classes. The dashboard directly supports retention by surfacing missed-class recovery content and maintaining transparency around learning progress.

## Problem Statement

Prior to this feature, students lacked a single place to view their complete class schedule, understand their credit balance across group and 1-on-1 classes, and access post-class summaries. Students who missed a class had no structured way to catch up on what was covered, and feedback from teachers was siloed or inaccessible after the session. This fragmented experience led to disengagement, confusion around scheduling, and lower completion rates for assignments. The Hubs Student Dashboard consolidates all of this into one cohesive interface, reducing friction and improving the overall learning experience.

## User Stories

- As a student, I want to see my upcoming group classes clearly demarcated on my dashboard, so that I always know my schedule at a glance without having to navigate elsewhere.
- As a student, I want to click "View Group Details" on a class card, so that I can review the group schedule, my assigned teacher, and the names of other students in my class before the session begins.
- As a student, I want to see a clear distinction between my group class credits and my 1-on-1 credits in the side panel, so that I understand exactly how many sessions I have remaining in each track.
- As a student, I want to view my auto-evaluated assignments and quizzes immediately after a class, so that I can see my score and act on feedback before the material fades from memory.
- As a student who missed a class, I want to see a "What you've missed today" section along with classroom glimpses and teacher feedback, so that I can catch up on the concepts covered even if I wasn't present.

## Feature Scope

### In Scope

- Upcoming Classes section showing group class schedule with visual demarcation
- Class Joining Cards displaying group name and "View Group Details" CTA
- Right-hand Credits Panel distinguishing group class credits from 1-on-1 credits
- Class Details Pop-up with three dynamic states: Pre-class, Post-class, and Class-Missed
- Post-class Assignments and Quizzes with auto-evaluation and score display
- Teacher Feedback section accessible via "view details" CTA on class cards
- "What we've learnt today" / "What you've missed today" summary section
- Concepts Covered list in the post-class pop-up
- "Glimpses from the Classroom" media carousel (images and videos uploaded by TA)
- Student-wise Attendance display within the post-class pop-up
- Access to feedback from both "my-courses" and "class-summary" pages

### Out of Scope

- Live class joining functionality (separate flow)
- 1-on-1 class scheduling or rescheduling
- TA upload interface for classroom glimpses (TA-side tooling handled separately)
- Parent-facing dashboard views
- Performance targets, browser/device support specifications, and accessibility guidelines (not defined in source document)

## Functional Requirements

1. **Upcoming Classes Display**
   - The dashboard must display upcoming group classes with clear visual demarcation distinguishing classes by time proximity or status.
   - Acceptance Criteria: At least the next scheduled class must be visible on the default dashboard view without scrolling.

2. **Class Joining Card**
   - Each class card must display the Group Name and a "View Group Details" button.
   - Acceptance Criteria: Clicking the button opens a pop-up or panel with group schedule, teacher information, and enrolled student list.

3. **Credits Panel**
   - A right-hand side panel must be present showing the student's remaining credits.
   - Credits must be split into two distinct categories: Group Class Credits and 1-on-1 Class Credits.
   - Acceptance Criteria: Both credit types are visible simultaneously. Values update in real time as classes are consumed.

4. **Dynamic Class Details Pop-up — Pre-class State**
   - Must show: Group schedule, assigned teacher profile, and list of enrolled students.
   - Acceptance Criteria: Pop-up renders correctly before a class is live; no post-class content is shown.

5. **Dynamic Class Details Pop-up — Post-class State**
   - Must show: Teacher Feedback, "What we've learnt today" summary, Concepts Covered, Glimpses of the Class (carousel), and Student-wise Attendance.
   - Acceptance Criteria: All five sections are present after a class concludes. Carousel hides if no media has been uploaded by the TA.

6. **Dynamic Class Details Pop-up — Class-Missed State**
   - Must show: "Oops you missed the class today!" header, targeted teacher feedback ("Try to be more regular"), "What you've missed today" section, Concepts Covered, Glimpses, and Student-wise Attendance.
   - Acceptance Criteria: Missed-class state is triggered automatically when a student is marked absent. Messaging and content are distinct from the post-class state.

7. **Assignments and Quizzes**
   - Post-class assessments must be surfaced to students after a session ends.
   - Scores must be auto-evaluated and displayed dynamically without manual intervention.
   - Acceptance Criteria: Score is visible in the right-side pop-up immediately after submission. Feedback is accessible via "view details" CTA.

8. **Feedback Access Points**
   - "View details" CTA must be available on both the "my-courses" page and the "class-summary" page.
   - Clicking either CTA must open the right-side pop-up with the relevant class's feedback and summary.
   - Acceptance Criteria: Both access points lead to the same pop-up component with accurate data for the selected class.

9. **Glimpses from the Classroom Carousel**
   - The carousel must support multiple images and videos uploaded by the TA.
   - If no media is uploaded, the "Glimpses from the Classroom" section title and carousel must be hidden entirely (no empty state shown).
   - Acceptance Criteria: Carousel renders correctly with at least one media item; section is invisible when media count is zero.

## UX/UI Flows

### Flow 1: Pre-Class — Viewing Group Details

1. Student lands on the dashboard.
2. Student sees the Upcoming Classes section with one or more class cards.
3. Student clicks "View Group Details" on the relevant class card.
4. A pop-up opens rendering the Pre-class state:
   - Group schedule for the current session/week
   - Assigned teacher's name and profile
   - List of other students enrolled in the group
5. Student reviews the information and closes the pop-up or proceeds to join the class.

### Flow 2: Post-Class — Accessing Feedback and Summary

1. Class concludes; dashboard updates the class card to reflect a completed status.
2. Student navigates to "my-courses" or "class-summary" page.
3. Student clicks "view details" on the completed class card.
4. A right-side pop-up opens rendering the Post-class state:
   - Teacher's written feedback for the student
   - "What we've learnt today" narrative summary
   - List of Concepts Covered during the session
   - "Glimpses from the Classroom" media carousel (if TA has uploaded media)
   - Student-wise Attendance record
5. Student reviews feedback and scrolls through class content.
6. If Assignments or Quizzes are available, student sees their auto-evaluated score in the same view.

### Flow 3: Missed Class — Catch-Up Flow

1. Student missed a scheduled class; class card reflects a missed status.
2. Student clicks "view details" on the missed class card.
3. Pop-up opens with the Class-Missed state:
   - "Oops you missed the class today!" header messaging
   - Teacher feedback: "Try to be more regular" (or equivalent)
   - "What you've missed today" summary section
   - Concepts Covered list
   - "Glimpses from the Classroom" carousel (if TA uploaded media)
   - Student-wise Attendance (student marked absent)
4. Student reviews the missed content for self-directed catch-up.

### Flow 4: Credits Monitoring

1. Student views the right-hand Credits Panel on the dashboard.
2. Panel displays two distinct credit counts: Group Class Credits and 1-on-1 Class Credits.
3. As classes are consumed, credit counts decrement in real time.
4. Student uses this information to plan future sessions or contact support if credits seem incorrect.

## Technical Requirements

- **Auto-Evaluation Engine:** Assignments and quizzes submitted post-class must be processed by an auto-evaluation system. Scores must be written back to the student's profile and surfaced in the class details pop-up dynamically.
- **TA Media Upload Pipeline:** The Glimpses carousel depends on TAs uploading images and videos after each class. The system must store these media assets and serve them via the carousel component. The dashboard must conditionally render or hide the carousel section based on whether media assets exist for a given class.
- **Class State Management:** The system must track and expose three distinct states per class (Pre-class, Post-class, Class-Missed) based on schedule data and attendance records. The class details pop-up component must consume this state to render the appropriate view.
- **Credits Data API:** The credits panel requires a real-time or near-real-time API endpoint that returns a student's remaining group and 1-on-1 credits separately.
- **Stakeholder Systems:** Integration with scheduling, attendance, and feedback systems is implied. Specific API contracts or third-party services are not detailed in the source document.

## Non-Functional Requirements

- Performance targets, browser and device support matrix, accessibility standards, and localization/language support requirements are not explicitly specified in the source document.
- As reasonable defaults for a student-facing web product:
  - Dashboard should load within 3 seconds on a standard broadband connection.
  - Must be functional on modern evergreen browsers (Chrome, Safari, Firefox, Edge).
  - Mobile responsiveness is expected given the student demographic.
  - Accessibility should conform to at minimum WCAG 2.1 AA standards.

## Success Metrics

The source document contains a metrics table with columns for "Improvement Metric", "Adoption %", and "Impact Funnel" but no values are filled in. The following metrics are inferred from the feature's stated goals:

- Increase in post-class assignment submission rate (target TBD)
- Reduction in student support tickets related to scheduling and credits confusion
- Increase in "view details" CTA click-through rate on completed class cards
- Percentage of students accessing missed-class catch-up content within 24 hours of absence
- Dashboard engagement rate (daily active students viewing the dashboard vs. total enrolled students)

## Edge Cases & Error Handling

- **Missed Class State:** When a student is marked absent for a scheduled class, the dashboard must automatically render the "Class-Missed" state for that card, including missed-class-specific messaging and teacher feedback. This state is distinct from the Post-class state and must not show "What we've learnt today" language.
- **No TA Media Uploaded:** If the TA has not uploaded any images or videos for a class, the "Glimpses from the Classroom" section — including its title — must be hidden completely. No empty state, placeholder, or loading spinner should be shown.
- **Pending Auto-Evaluation:** If an assignment or quiz has been submitted but evaluation has not yet completed, the UI must handle this gracefully (e.g., show a "Score pending" state rather than displaying null or broken data).
- **No Feedback from Teacher:** If a teacher has not submitted feedback for a completed class, the feedback section should either hide or display a neutral placeholder ("Feedback not yet available") rather than an empty field.
- **Credits API Failure:** If the credits data cannot be fetched, the credits panel should show a fallback state with a retry option rather than displaying zero or stale data.

## Dependencies

- **Business Stakeholder:** Aditya Gupta — business sign-off and prioritization
- **Product Owner:** Gargi Kekre — requirements ownership and acceptance
- **Design:** Gurbinder Singh — UI/UX design and mockup delivery
- **Engineering:** Abhinav Gupta — technical implementation lead
- **Teaching Assistants (Operational):** The Glimpses from the Classroom feature is operationally dependent on TAs uploading media content after each class. Without TA adoption of the upload workflow, this section will remain hidden for all classes.
- **Attendance System:** The three-state class pop-up (Pre/Post/Missed) depends on accurate and timely attendance data being recorded and exposed via API.
- **Auto-Evaluation Service:** Assignment and quiz scores displayed in the dashboard depend on a functioning auto-evaluation pipeline completing before the student views their results.
- **Hubs Migration Program:** This feature is part of the broader Hubs Migration initiative; timelines and scope are coupled to that program's overall delivery schedule.
