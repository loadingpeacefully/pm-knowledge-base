---
title: Group 360
category: product-prd
subcategory: student-lifecycle
source_id: 0c81dde1-8229-4bd7-8aee-d38239192b90
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Group 360

## Overview

BrightChamps runs group-format classes — including Regular Classes, Webinars, Workshops, Annual Events, and Cohorts — but the admin dashboard lacks a dedicated section for creating and managing these group structures. Admins currently have no unified interface to define group compositions, assign teachers, map curricula, set schedules, and track the status of active and upcoming group classes. The Group 360 feature addresses this gap by introducing a dedicated admin section specifically for group class management within the BrightChamps Admin Dashboard.

Group 360 gives admins the ability to create groups from scratch with full configuration: subject, level, modality (online/offline), schedule type (one-time or recurring), capacity parameters, curriculum mapping, and physical location for offline classes. Once created, groups can be actively managed: students and teachers can be added, removed, or moved; schedules can be edited; and teaching assistants can be updated. A structured listing view and detailed group details page provide admins with clear visibility into all active, upcoming, and inactive groups.

The feature also requires corresponding changes to the existing "Student 360" dashboard to accommodate group class data, ensuring that individual student views correctly reflect group class participation. Group 360 is the foundation for a broader "Hubs Experience" within the BrightChamps platform, enabling structured, scalable group-based learning management.

## Problem Statement

Admins managing BrightChamps group classes have no dedicated tooling within the admin dashboard to create, configure, and maintain groups. Without this, roster management, schedule coordination, and teacher assignment for group classes rely on workarounds or manual processes outside the platform. This creates operational inefficiency, data inconsistency between systems, and a poor admin experience. The product needs a first-class group management interface that allows admins to own the entire group lifecycle — from creation through active management — directly within the dashboard.

## User Stories

- As an admin, I want to create a new group by selecting its purpose (Regular Class, Webinar, Workshop, etc.) and filling in relevant configuration fields, so that I can organize students and teachers into structured, well-defined learning cohorts.
- As an admin, I want to add, move, or remove students and teachers within a group at any time, so that I can keep group rosters accurate and reflect any enrollment changes or teacher reassignments.
- As an admin, I want to view all active, upcoming, and inactive groups in a filterable list, so that I can quickly monitor the status of all group classes and find specific groups without manual searching.
- As an admin, I want to edit a group's weekly schedule, so that I can adjust class timing when schedules need to change, with appropriate rules for when changes take effect.
- As an admin, I want to see a group's full details — student list, learning progress, teacher info, and schedule — in a single view, so that I have everything I need to manage the group without navigating between multiple pages.

## Feature Scope

### In Scope

- New "Group 360" section added to the BrightChamps Admin Dashboard
- Group Create Page / Form: purpose selection, mandatory fields, dynamic form fields based on purpose
- Group Listing Page: view active, upcoming, and inactive groups with filtering
- Group Details Page: four tabs — Student List, Learning Progress, Teacher Change, Schedule
- Group creation with the following purpose types: Regular Classes, Webinars, Workshop, Annual Event/Activity, Cohort Creation
- Mandatory group fields: Subject, Level, Online/Offline, One-time/Recurring, Start Date/Time
- Conditional mandatory fields: Location (for offline groups), Number of classes/packages (for recurring groups)
- Capacity management: max and min student strength, auto-calculated current strength
- Student roster management: add, remove, move students with confirmation prompts
- Teacher management: assign, change teacher via search; update teaching assistants
- Schedule management: edit weekly schedule via popup; 24-hour change rule
- Teacher profile quick links: WhatsApp contact, Slack profile
- Modifications to the existing Student 360 dashboard to accommodate group class data

### Out of Scope

- Non-admin user access to Group 360 (teacher-facing or student-facing group views are separate)
- Performance analytics or reporting features (Impact Funnel metrics are defined but not populated)
- Automated group creation from enrollment data (manual creation only at this stage)
- Specific non-functional requirements including performance SLAs, accessibility standards, and localization (not defined in the source document)

## Functional Requirements

1. **Group Creation — Purpose Selection**
   - Admins must be able to click "Add Group" on the Group Listing Page to open a popup creation form.
   - The first step of the form must require the admin to select a group purpose from five options: Regular Classes, Webinars, Workshop, Annual Event/Activity, Cohort Creation.
   - Selecting a purpose must dynamically populate the relevant fields for that purpose type.
   - Acceptance criteria: Popup form opens on "Add Group" click; purpose dropdown is present as the first field; form fields change dynamically based on purpose selection.

2. **Group Creation — Mandatory Fields**
   - The following fields must be mandatory for all group types: Subject, Level, Online/Offline, One-time/Recurring, Start Date/Time.
   - Location must be mandatory when "Offline" is selected.
   - Number of classes/packages must be mandatory when "Recurring" is selected.
   - The "Create Group" (continue) button must be disabled until all mandatory fields are completed.
   - Acceptance criteria: Form cannot be submitted without mandatory fields; conditional mandatory fields appear and are enforced based on group type selection.

3. **Group Capacity**
   - Admins must be able to define maximum and minimum student strength for a group.
   - The system must auto-calculate the current student strength based on the number of students currently mapped to the group.
   - Acceptance criteria: Max/min fields are present on the creation form; current strength reflects the actual number of enrolled students in real time.

4. **Group Listing Page**
   - The listing page must display three status-based views: Active Groups, Upcoming Groups, and Inactive Groups.
   - Admins must be able to filter the list by criteria including Subject, Level, and Status.
   - Each group in the list must include a clickable Group ID or "Group Details" link that navigates to the Group Details page.
   - Acceptance criteria: All three status views are accessible; filters function correctly; navigation from list to details works.

5. **Group Details Page**
   - The Group Details page must display basic group information and include four tabs: Student List, Learning Progress, Teacher Change, and Schedule.
   - Acceptance criteria: All four tabs are accessible from the details page; each tab loads the correct data for the selected group.

6. **Student Roster Management**
   - Admins must be able to add new students to a group by searching and selecting from a student search interface.
   - Admins must be able to remove students from a group via a "Remove" action, which must trigger a confirmation message ("Are you sure you want to remove [Student] from group?") before executing.
   - Acceptance criteria: Student search is functional; add action enrolls the student in the group; confirmation dialog appears before removal; removal is reflected in current strength.

7. **Teacher Management**
   - Admins must be able to change the assigned teacher for a group via a pencil icon edit action on the teacher details.
   - A "Teacher Change" popup must allow the admin to search for a new teacher and click "Allot" to assign them.
   - Teacher profiles must include quick-access links to the teacher's WhatsApp (via contact number) and Slack profile.
   - Acceptance criteria: Teacher change popup functions correctly; Allot action assigns the new teacher; WhatsApp and Slack links open in the correct applications.

8. **Schedule Management**
   - Admins must be able to edit the weekly schedule for a group by clicking a pencil icon next to the Weekly Schedule.
   - A popup must allow selection of days and time slots.
   - If a schedule change is made less than 24 hours before an upcoming class, the new schedule must only take effect after that immediate upcoming class is completed.
   - Acceptance criteria: Schedule edit popup is functional; schedule changes save correctly; the 24-hour rule is enforced — changes within 24 hours of the next class do not affect that class.

## UX/UI Flows

### Flow 1: Create a New Group

1. Admin navigates to the "Group 360" section of the Admin Dashboard.
2. Admin clicks the "Add Group" button on the Group Listing Page.
3. A popup form opens.
4. Admin selects a group purpose from the dropdown: Regular Classes, Webinars, Workshop, Annual Event/Activity, or Cohort Creation.
5. Based on the selection, relevant form fields populate dynamically.
6. Admin fills in all mandatory fields: Subject, Level, Online/Offline, One-time/Recurring, Start Date/Time, and any conditional mandatory fields (Location if Offline; number of classes if Recurring).
7. Admin sets max and min student strength.
8. The "Create Group" button becomes active once all mandatory fields are complete.
9. Admin clicks "Create Group" to confirm.
10. The new group appears in the Group Listing Page.

### Flow 2: View and Navigate Groups

1. Admin navigates to the "Group 360" section.
2. The Group Listing Page displays three tabs/views: Active Groups, Upcoming Groups, Inactive Groups.
3. Admin can apply filters (Subject, Level, Status) to narrow the list.
4. Admin clicks on a blue hyperlinked Group ID or "Group Details" text.
5. Admin is redirected to the Group Details page for that group.
6. The Group Details page displays basic group info and four tabs: Student List, Learning Progress, Teacher Change, Schedule.

### Flow 3: Edit Group Schedule

1. Admin is on the Group Listing Page or Group Details page.
2. Admin clicks the pencil icon next to the Weekly Schedule field.
3. A schedule edit popup opens with day and time slot selectors.
4. Admin selects the new days and/or time slots.
5. Admin saves changes.
6. System checks: is the change being made less than 24 hours before the next scheduled class?
   - If yes: the change is saved but will take effect only after the immediate upcoming class is complete.
   - If no: the change takes effect immediately for all upcoming classes.

### Flow 4: Change Assigned Teacher

1. Admin navigates to the Group Details page for a specific group.
2. Admin clicks the Teacher Change tab, or clicks the pencil icon next to the teacher's details.
3. A "Teacher Change" popup opens with a teacher search interface.
4. Admin searches for and selects the new teacher.
5. Admin clicks "Allot" on the desired teacher.
6. The system processes the teacher assignment.
7. Admin saves changes.
8. The group's teacher details are updated.

### Flow 5: Manage Student Roster

1. Admin is on the Group Details page, Student List tab.
2. Admin clicks "+x more" or the pencil icon in the student column to open the student management popup.
3. To add a student: Admin uses the search field to find a student, then clicks Add/Assign.
4. To remove a student: Admin clicks "Remove" next to the student's name. A confirmation dialog appears: "Are you sure you want to remove [Student] from group?" Admin confirms.
5. Changes are reflected in the student list and current strength count.

## Technical Requirements

- **Student 360 Integration / Modifications:** The existing Student 360 dashboard must be updated to accommodate group class data. This includes modifying data points displayed, updating filters, and limiting certain schedule functionalities that conflict with group-level schedule management. This is a prerequisite dependency.
- **Dynamic Form Engine:** The group creation form must support dynamic field visibility based on the selected purpose type. This requires a form configuration model that maps purpose types to required and optional fields.
- **Auto-Calculated Strength:** Current student strength must be computed from the live roster and updated in real time as students are added or removed. This may require a counter maintained in the group record and updated on roster change events.
- **Teacher Contact Links:** The UI must construct WhatsApp deep links from the teacher's contact number (`https://wa.me/{number}`) and include a direct link to the teacher's Slack profile. These must open in the respective native apps.
- **Schedule Change Rule Engine:** The backend must implement the 24-hour schedule change rule: when a schedule edit is submitted, the system must compare the change submission time against the next scheduled class time. If the gap is less than 24 hours, the new schedule is stored but the effective date is set to after the next class completion.
- **Confirmation Dialogs:** The student removal flow must implement a confirmation dialog before executing the removal to prevent accidental data loss.

## Non-Functional Requirements

The source document does not contain explicit non-functional requirements (performance targets, browser/device support, accessibility standards, or localization requirements). Based on the feature context and general admin dashboard standards, the following are synthesized:

- **Performance:** The Group Listing Page should load within 2–3 seconds for lists of up to several hundred groups. The Group Details page should aggregate and render all four tabs' data within 2–3 seconds.
- **Reliability:** Schedule change enforcement (the 24-hour rule) must be executed reliably with no exceptions for any group type.
- **Data Integrity:** Student removal confirmation dialogs must prevent accidental roster changes. All roster and schedule changes must be logged for audit purposes.
- **Browser Support:** The feature must function on all browsers supported by the existing BrightChamps Admin Dashboard.

## Success Metrics

The source document contains placeholder Impact Funnel tables with the following metric categories, but specific target values have not been defined:

- **Improvement Metric:** Operational efficiency improvement for admins managing group classes
- **Current Adoption %:** Baseline percentage of group classes managed via the new Group 360 section vs. legacy workarounds
- **Expected Adoption %:** Target percentage of group class management actions completed through Group 360
- **Expected Impact:** Reduction in manual errors, scheduling conflicts, or support requests related to group class management

Proxy metrics to track post-launch:
- Number of groups created via the Group 360 interface per week
- Time taken by admins to complete roster changes (add/remove student) before and after
- Reduction in support tickets related to group class management errors

## Edge Cases & Error Handling

- **Schedule Change Within 24 Hours:** If an admin edits a group's weekly schedule less than 24 hours before the next class date, the change must not apply to that immediate upcoming class. The new schedule takes effect only after the next class is completed. The UI should inform the admin of this behavior at the time of the change (e.g., "This change will take effect after your class on [date/time]").
- **Student Removal Confirmation:** When an admin attempts to remove a student from a group, a confirmation dialog must be shown: "Are you sure you want to remove [Student Name] from this group?" The removal must not proceed without explicit confirmation to prevent accidental data loss.
- **Purpose-Specific Field Validation:** If an admin switches the selected group purpose after partially filling in the form, the system must handle field resets gracefully — clearing fields that are no longer relevant while preserving fields that are common across purposes.
- **Capacity Overflow:** If an admin attempts to add a student to a group that has already reached its maximum student strength, the system should display a clear warning or block the addition, depending on the configured behavior.
- **Teacher Unavailability:** If the teacher being allotted to a group has a scheduling conflict, the system should surface a warning during the "Allot" step. Resolution behavior (block or warn) should be defined.

## Dependencies

- **Student 360 Dashboard Modifications:** Group 360 explicitly depends on changes being made to the Student 360 platform. These changes are required to ensure student profiles correctly reflect group class enrollment and to limit schedule functionalities that conflict with group-level management. This is a hard dependency that must be completed alongside or before Group 360.
- **Teacher Availability and Profile Data:** The teacher search and assignment flow depends on accurate, up-to-date teacher profiles including contact numbers, Slack handles, and availability data.
- **Curriculum Mapping Service:** Group creation with curriculum mapping requires the curriculum service to expose group-compatible mapping endpoints.

### Teams Involved

| Team | Role |
|---|---|
| Business | Aditya Gupta — business sponsor and requirements owner |
| Product | Gargi Kekre — product owner |
| Design | Gurbinder Singh Bakshi — UI/UX design for Group 360 screens |
| Tech | Backend (group data model, schedule rule engine, Student 360 modifications), Frontend (dynamic form, listing, details page) |
| QA | End-to-end testing of all group creation, roster management, schedule change, and teacher assignment flows |
