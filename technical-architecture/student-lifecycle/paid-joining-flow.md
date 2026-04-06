---
title: Paid Joining Flow
category: product-prd
subcategory: student-lifecycle
source_id: 64476378-80b0-4cf3-a01d-dfd6320ed230
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Paid Joining Flow

## Overview

The Paid Joining Flow is a teacher-facing feature that redesigns the classroom joining sequence on the Teacher Dashboard to improve teacher preparedness and create a closed-loop administrative task system. Rather than routing teachers directly into a Zoom room, the flow intercepts the join action and redirects the teacher to the student's profile page, where prioritized pre-class to-do items are surfaced. A 10-second cooldown timer on the "Join Now" button enforces a minimum review window before the teacher can enter the classroom.

The joining section is envisioned to evolve from a passive information display into an active to-do list system that captures whether teachers addressed administrative goals during class — such as driving renewals, asking for referrals, reminding students of overdue assessments, or handling refund situations. This creates accountability and a data trail for each teaching session.

The business goal is to improve the quality and preparedness of teaching sessions, recapture lost earnings by prompting teachers to surface renewal and installment conversations, and provide a centralized management interface for teachers to track their students' learning progress, attendance, and administrative status.

## Problem Statement

Teachers were entering Zoom classrooms without reviewing critical student-specific context — pending refunds, missed attendance, low credit balances, overdue homework, or upcoming renewal windows. This meant that high-value administrative conversations (renewals, installment prompts, referral asks) were either forgotten or handled reactively by ops teams. The teacher dashboard's joining section acted purely as an information surface with no task orientation. Without a structured pre-class review and a system to record whether tasks were completed, the organization had limited insight into whether these conversations were happening, and revenue recovery opportunities were being missed.

## User Stories

- As a teacher, I want to see a centralized dashboard of my upcoming and past classes, so that I can efficiently manage my daily schedule and pending evaluations without switching between multiple screens.
- As a teacher, I want to be redirected to the student's profile page before joining a class, so that I can review essential notes and be fully prepared for the session.
- As a teacher, I want the system to surface the top 3 prioritized action items for my student before I join, so that I know exactly what administrative or learning tasks to address during the class.
- As a teacher, I want the virtual classroom to open in a new browser tab, so that I can keep the student's profile page and lesson booklet open for reference while teaching.
- As a teacher, I want the "Join Now" button to become active only after a brief forced review period, so that I have time to absorb the student's context before entering the class.

## Feature Scope

### In Scope

- Teacher Dashboard Homepage with upcoming and past class views
- "Join from student profile" button on the dashboard home page, passing class ID during redirection
- Student Profile / Progress Page as the mandatory pre-class stop in the joining flow
- 10-second cooldown timer on the "Join Now" button on the student profile page
- Pre-class to-do section showing a maximum of 3 prioritized action items per student
- Priority ordering for to-do items (Refund Retained > First Class > Attendance issues > Happy Moments > PTM > Installment/Renewals > Average Class Count > Homework/Assessments)
- Zoom room opening in a new tab upon "Join Now" click
- Join button active window: T-10 minutes to T+10 minutes of scheduled class time
- Dynamic templating variables for to-do messaging: `{{studentName}}`, `{{refundReason}}`, `{{remainingCredits}}`, `{{lost_earnings}}`, `{{dueDate}}`
- Drag-and-drop learning path reordering (incomplete modules only; completed modules locked)
- Learning path auto-advancement (next module activates when all lessons in current module are complete)
- My Students Page for viewing enrolled students
- Evaluation card creation for multiple student submissions per lesson (quiz, assignment, assessment)

### Out of Scope

- The closed-loop task completion capture system (future phase; joining section currently shows tasks but does not yet record whether they were addressed)
- Student-facing dashboard or Zoom joining flow
- Refund flow implementation (required as a dependency for "Refund Retained" to-do items; must be built separately)
- Parent Teacher Meeting (PTM) flow implementation (required as a dependency for PTM to-do items)
- New penalty system for "Class Missed" text updates (dependency; not in this scope)

## Functional Requirements

1. **Join Button Active Window**
   - The "Join Now" button on the student profile page and the "Join from student profile" button on the dashboard homepage must only be active and clickable from T-10 minutes to T+10 minutes of the scheduled class time.
   - Acceptance Criteria: Outside of the T-10 to T+10 window, the button is disabled or hidden. Within the window, the button is clickable (subject to the cooldown timer on the profile page).

2. **"Join from student profile" Redirect with Class ID**
   - Clicking "Join from student profile" on the dashboard homepage must redirect the teacher to the student's profile/progress page.
   - The frontend must pass the class ID as a parameter in the redirection link.
   - Acceptance Criteria: The student profile page correctly populates the upcoming class information section using the passed class ID. If the class ID is not passed, the joining section is not shown.

3. **10-Second Cooldown Timer on "Join Now"**
   - On the student profile page's joining section, the "Join Now" button must be initially disabled with a 10-second countdown timer running immediately upon page load.
   - The button must remain unclickable for the full 10 seconds.
   - Acceptance Criteria: Teacher cannot bypass the cooldown. Timer counts down visibly. After 10 seconds, the "Join Now" button becomes fully enabled.

4. **Zoom Room Opens in New Tab**
   - Clicking the enabled "Join Now" button must open the Zoom classroom link in a new browser tab.
   - The student profile/progress page must remain open in the original tab.
   - Acceptance Criteria: Teacher is in the Zoom room in a new tab. Student profile page is preserved in the original tab for reference during class.

5. **Pre-Class To-Do Section — Maximum 3 Items, Priority Ordered**
   - The pre-class information section on the student profile page must display a maximum of 3 to-do items.
   - Items must be ordered strictly by the following priority:
     1. Refund Retained
     2. First Class
     3. Attendance (Paused, Cancelled, Missed)
     4. Happy Moments
     5. PTM (Parent Teacher Meeting)
     6. Installment and Renewals
     7. Average Class Count
     8. Homework/Assessments
   - Acceptance Criteria: If more than 3 qualifying to-do items exist, only the top 3 by priority are shown. No more than 3 items are displayed at once.

6. **Dynamic To-Do Messaging Variables**
   - To-do item text must support dynamic templating with the following variables: `{{studentName}}`, `{{refundReason}}`, `{{remainingCredits}}`, `{{lost_earnings}}`, `{{dueDate}}`.
   - Acceptance Criteria: Variables render with actual values pulled from the student's record. No `{{variable}}` placeholders appear in the rendered UI.

7. **Learning Path — Drag-and-Drop Reordering**
   - Teachers must be able to reorder incomplete modules in a student's learning path via drag-and-drop.
   - Completed modules must be locked and cannot be reordered.
   - Acceptance Criteria: Dragging an incomplete module reorders it in the path. Attempting to drag a completed module has no effect (drag is disabled for completed modules).

8. **Learning Path — Auto-Advancement**
   - When a teacher sets a new active module and the new module already has completed lessons, the system must automatically start from the first incomplete lesson.
   - If all lessons in the currently active module are completed, the system must automatically activate the next module in sequence.
   - Acceptance Criteria: No teacher action is needed to advance between modules when all lessons are complete. The correct lesson is always the starting point when a new module is activated.

9. **Multiple Evaluation Cards per Lesson**
   - If a student makes multiple submissions for the same lesson (e.g., a quiz, an assignment, and an assessment), the system must create separate evaluation cards for each submission type.
   - Acceptance Criteria: Teacher sees distinct evaluation cards for each submission type within the same lesson. Cards are not merged or deduplicated.

## UX/UI Flows

### Primary Flow: Teacher Joins a Class via Student Profile

1. Teacher opens the Teacher Dashboard Homepage.
2. Teacher sees an upcoming class card with the student's name and class time.
3. "Join from student profile" button becomes active at T-10 minutes.
4. Teacher clicks "Join from student profile."
5. Frontend passes the class ID to the redirect URL.
6. Teacher is redirected to the Student Profile / Progress Page.
7. The joining section on the student profile page loads, populating class info from the class ID.
8. The pre-class to-do section displays up to 3 prioritized tasks (e.g., "Refund Retained — discuss with {{studentName}}", "Renewal due on {{dueDate}}").
9. "Join Now" button is visible but disabled; a 10-second countdown timer begins immediately.
10. Teacher reads through the to-do items and pre-class notes during the 10-second window.
11. Countdown reaches zero; "Join Now" button becomes enabled.
12. Teacher clicks "Join Now."
13. Zoom classroom opens in a new browser tab.
14. Teacher's original tab remains on the student profile page for reference during class.

### Secondary Flow: Teacher Views My Students Page

1. Teacher navigates to "My Students" from the dashboard sidebar.
2. Teacher sees a list of enrolled students with key status indicators.
3. Teacher clicks on a specific student to open their profile page.
4. Teacher reviews learning progress, attendance, and evaluation cards.
5. If a class is upcoming (within the join window), the joining section is visible with the cooldown timer flow as above.

### Learning Path Reordering Flow

1. Teacher navigates to the student's learning path section on the profile page.
2. Teacher sees a list of modules with completed modules locked and incomplete modules draggable.
3. Teacher drags an incomplete module to a new position in the sequence.
4. The learning path updates to reflect the new order.
5. If all lessons in the currently active module are done, the next module activates automatically.
6. If the teacher manually sets a new active module with already-completed lessons, the path starts from the first incomplete lesson in that module.

## Technical Requirements

- **Zoom Integration:** The final step of the joining flow routes the teacher to a Zoom room. The system must generate or retrieve the correct Zoom room link for the class and open it in a new tab via the "Join Now" button.
- **Class ID Passing:** When "Join from student profile" is clicked on the dashboard homepage, the frontend must include the `classId` as a URL parameter in the redirection to the student profile page. The student profile page must read this parameter to populate the joining section with the correct class data.
- **Dynamic Templating:** The backend must supply the following variables to the to-do messaging templates: `{{studentName}}`, `{{refundReason}}`, `{{remainingCredits}}`, `{{lost_earnings}}`, `{{dueDate}}`. These must be resolved server-side before the UI renders.
- **To-Do Priority Logic:** The system must evaluate all qualifying to-do conditions for a student and return the top 3 by priority order for display. This evaluation must occur server-side.
- **Join Button State Management:** The "Join Now" button state (active/inactive) must be controlled by comparing the current time against the class's scheduled time (T-10 to T+10 window). This state check must be reliable across time zones.
- **Drag-and-Drop State:** Drag-and-drop reordering of learning path modules must persist changes to the student's learning path record. Completed module lock must be enforced both visually and in the underlying data model.

## Non-Functional Requirements

- **Performance:** The dashboard must load and display responsively to avoid delays that could cause teachers to miss their pre-class review window. The student profile page must load within acceptable time for the 10-second timer to be meaningful.
- **Scalability:** The system must handle teachers with high volumes of students and classes without degrading the dashboard's responsiveness.
- **Responsiveness:** The Teacher Dashboard homepage and student profile page must be optimized for different screen sizes and devices, as teachers may access the dashboard from various devices.
- Specific browser support matrix, accessibility standards (WCAG level), and localization requirements are not specified in the source document.

## Success Metrics

Specific KPIs and OKRs are not explicitly defined in the source document. Success is tied to:

- Teacher preparedness rate (percentage of teachers who complete the 10-second cooldown review before joining, as a proxy for engagement with to-do items)
- Renewal conversion rate attributed to teacher-driven renewal prompts during class (expected lift from surfacing Installment/Renewals to-dos)
- Reduction in lost earnings per teacher (tracked via `{{lost_earnings}}` variable surfacing; target TBD)
- Referral capture rate from teacher-prompted referral conversations during class
- Future metric: closed-loop task completion rate (once the system evolves to capture whether teachers addressed each to-do item)

## Edge Cases & Error Handling

- **Missing Class ID on Redirect:** If the frontend fails to pass the class ID when redirecting to the student profile page, the joining section must not be displayed. The document notes this is a critical bug — if the class ID is missing at scale, joining functionality is broken organization-wide. This must be treated as a P0 bug.
- **Multiple Submissions for Same Lesson:** When a student submits a quiz, assignment, and assessment for the same lesson, the system creates separate evaluation cards for each. Teachers see all three cards distinctly without any merging logic.
- **Learning Path Module Fully Completed:** If all lessons in the currently active module are completed when a new module is set as active, the system automatically advances to the next module. No manual intervention by the teacher is required.
- **New Active Module with Pre-Completed Lessons:** If a teacher changes the active learning module and the new module already contains completed lessons, the system automatically starts the path from the first incomplete lesson in that module. Completed lessons are not re-shown as the starting point.
- **Join Button Outside Active Window:** If a teacher attempts to access the student profile joining section outside the T-10 to T+10 window (e.g., by navigating directly), the "Join Now" button must be disabled or absent. The page should show the upcoming class time clearly so the teacher knows when the window opens.
- **Refund Retained To-Do Without Refund Flow Built:** Refund Retained to-do items are blocked pending the implementation of the refund flow. Until the refund flow is live, this to-do type should either not appear or render in a disabled state.
- **PTM To-Do Without PTM Flow Built:** Parent Teacher Meeting to-do items are blocked pending PTM flow implementation. Same handling applies as Refund Retained.
- **Class Missed Text Requiring New Penalty System:** Current "Class Missed" text content is a placeholder; the final text depends on the new penalty system going live. A content toggle or feature flag should manage this transition.

## Dependencies

- **Zoom:** The entire class joining action depends on Zoom room generation and routing. If Zoom integration fails, teachers cannot join their classrooms.
- **Refund Flow:** "Refund Retained" to-do items cannot be surfaced until the refund flow is implemented and operational.
- **Parent Teacher Meeting (PTM) Flow:** PTM to-do items cannot be surfaced until the PTM flow is built.
- **New Penalty System:** Updated "Class Missed" messaging in to-do items depends on the new penalty system going live.
- **Student Profile Service:** Dynamic templating variables (`{{studentName}}`, `{{refundReason}}`, `{{remainingCredits}}`, `{{lost_earnings}}`, `{{dueDate}}`) must be supplied by the student profile and account services.
- **Class Scheduling Service:** Join button active window (T-10 to T+10) depends on accurate scheduled class time data from the class scheduling service.
- **Frontend Engineering:** Class ID passing logic on redirect, 10-second timer implementation, drag-and-drop module reordering, and Zoom tab-opening behavior.
- **Backend Engineering:** To-do priority evaluation logic, dynamic template variable resolution, join window state management.
