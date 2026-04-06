---
title: Teacher Profile and Reviews
category: product-prd
subcategory: student-lifecycle
source_id: 784cea51-f6e3-4918-99c9-1515be75ef7e
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Teacher Profile and Reviews

## Overview

The Teacher Profile and Reviews feature introduces a comprehensive, media-rich teacher profile system across the BrightChamps platform. Currently, there are no teacher images or profile cards displayed in customer-facing dashboards during teacher selection or changes, and there is no mechanism for students to rate their teachers or leave feedback. This feature addresses both gaps simultaneously by building a structured profile with a photo, video, bio, experience statistics, and a dynamic ratings system — all visible to students, parents, and the public.

The feature is designed to serve multiple stakeholder goals. For students and parents, it creates informed trust in their assigned teacher before and during their learning journey. For teachers, it builds a stake in their long-term relationship with BrightChamps: a rich, review-backed profile with accumulated ratings represents a professional asset that they would forfeit if they left the organization — a deliberate retention mechanism. For the business, the profile system is a foundational prerequisite for multiple upcoming features including teacher selection in LingoCHAMPS demo bookings, BrightBuddy flows, and student onboarding flows.

The feature touches four distinct surfaces: the Teacher Dashboard (where teachers manage their profile), the Student Dashboard (where students view profiles and submit reviews), the Prashashak admin portal (where admins manage foundational profile data), and a public-facing profile URL (for external sharing).

## Problem Statement

BrightChamps operates a large network of teachers, but students and parents have no way to learn about their assigned teacher before or during their learning journey. There are no teacher images displayed during teacher selection or assignment, no structured bio or background information, and no feedback mechanism for students to share their experience. This creates a trust deficit: parents making decisions about their child's education cannot evaluate the teacher they are investing in, and students have no channel to express satisfaction or dissatisfaction in a structured way. Additionally, the absence of a review system leaves a significant amount of social proof value uncaptured — positive student experiences are not being surfaced to prospective customers or used to drive teacher accountability.

## User Stories

- As a teacher, I want to upload and edit my profile image, video introduction, and "About Me" description, so that I can maintain an up-to-date and compelling profile that represents my teaching style to students and parents.
- As a student, I want to write a review and give a star rating to my teacher after class, so that I can share my learning experience and provide feedback that helps improve the quality of teaching on the platform.
- As a student, I want the option to submit my review anonymously, so that my name and profile picture are hidden from the public and I feel comfortable providing honest feedback without social pressure.
- As a teacher, I want to flag or report junk and poor-quality reviews, so that the administration can evaluate them for removal and my public profile accurately reflects genuine student experiences.
- As a teacher, I want to share my profile via a public URL, so that I can showcase my professional portfolio and accumulated reviews to people outside the BrightChamps organization — including prospective employers or students.
- As a system administrator, I want to manage foundational profile data (name, course, country, languages) through the Prashashak admin panel, so that teacher profiles are accurate and consistent without requiring teachers to manually re-enter information already in our systems.

## Feature Scope

### In Scope

- Teacher Dashboard "View and Edit Profile" section for managing profile image, video, and bio
- Profile image upload with constraints (JPEG, PNG, GIF; min 100x100 px; max 5 MB)
- "About Me" text field (50 to 1000 characters)
- Video introduction upload (MP4, WebM, MOV, AVI; 20 MB to 250 MB)
- Prashashak admin auto-population of: teacher name, course, ID, country/flag, and languages
- Dynamic profile completeness indicator ("100% complete" vs. "Please complete your profile")
- Dynamic ratings calculation: average of "write a review" ratings and class card ratings from the last 3 months
- Student "Write a Review" flow with star rating and text
- Anonymous review submission option (name replaced with "Anonymous student"; profile picture blurred)
- Review editing logic: updates existing review if within 30 days; creates a new separate review if beyond 30 days
- Review display with sorting: top 5 reviews with rating > 4 in the last 90 days shown first (reverse chronological); all remaining reviews follow in reverse chronological order
- Teacher "Report this review" flag interaction with backend capture
- Video player pop-up supporting play/pause and timeline scrubbing
- Public shareable profile URL (read-only; interactive functions disabled)
- Multi-course teacher profile adaptation (multiple course tags in the primary card)

### Out of Scope

- Students editing or deleting their own reviews (only teachers can flag reviews; admins handle removal)
- Teacher profile search/discovery for students (profile access is contextual within the student-teacher relationship, not a browsable directory)
- Real-time review notifications for teachers (separate notification system)
- Automated review moderation (flagged reviews are evaluated manually by admins in v1)
- Peer teacher profile views
- Integration with third-party review aggregators

## Functional Requirements

1. **Profile Image Upload**: Teachers must be able to upload a profile image with the following constraints:
   - Formats: JPEG, PNG, GIF
   - Minimum resolution: 100x100 px
   - Maximum file size: 5 MB
   - Acceptance Criteria: Images outside the format/size constraints must be rejected with a clear error message. Valid images must be previewed before submission. The upload modal must display format and size guidance.

2. **"About Me" Text Field**: Teachers must be able to add and edit a bio description.
   - Constraints: Minimum 50 characters, maximum 1000 characters.
   - Acceptance Criteria: The character count must be displayed live. Submissions below 50 or above 1000 characters must be rejected. A toast notification must display "Profile updated successfully" upon successful save.

3. **Video Introduction Upload**: Teachers must be able to upload a video introduction.
   - Formats: MP4, WebM, MOV, AVI
   - Size: 20 MB to 250 MB
   - Acceptance Criteria: Videos outside the allowed range must be rejected with a specific error message. Uploaded videos must be playable via the in-platform video player pop-up.

4. **Auto-Population from Prashashak**: The system must automatically pull and display foundational profile data from the Prashashak admin panel: teacher name, course(s), teacher ID, country/flag, and languages.
   - Acceptance Criteria: These fields must not be editable by the teacher directly. Any updates must flow from Prashashak. The profile must reflect changes from Prashashak within a defined sync window.

5. **Profile Completeness Indicator**: The system must display a dynamic completeness message based on whether all profile sections have been filled.
   - Acceptance Criteria: If all sections are complete, display "Your profile is 100% complete." If any section is missing, display "Please complete your profile" with a prompt to the incomplete section.

6. **Dynamic Ratings Calculation**: The teacher's displayed profile rating must be calculated as the average of two sources:
   - Ratings received via the "write a review" feature
   - Average of class card ratings received on the student dashboard in the last 3 months
   - Acceptance Criteria: The rating must update automatically as new ratings are submitted. The 3-month window for class card ratings must be a rolling window, not a fixed calendar period.

7. **Write a Review — Student Flow**: Students must be able to submit a star rating and text review for their teacher.
   - Access points: Clicking the teacher's name/image, or clicking a "Write a review" button on Upcoming/Completed classes pages.
   - Acceptance Criteria: The review form must include a star rating selector and a free-text field. The "Submit Review" button must only be enabled after a star rating is selected. A toast "Thanks! Your review is submitted" must appear on successful submission.

8. **Anonymous Review Submission**: Students must have the option to submit a review anonymously by checking "Give this review anonymously."
   - Acceptance Criteria: If the anonymous option is checked, the reviewer's name must display as "Anonymous student" and their profile picture must be replaced with a blurred image. The anonymity must be enforced at the database level, not just the display layer.

9. **Review Editing Logic**: The system must enforce the following update behavior:
   - If a student submits a new review within 30 days of their most recent review for the same teacher: the existing review is updated (not a new record).
   - If a student submits a review more than 30 days after their most recent review for the same teacher: a new, distinct review record is created.
   - Acceptance Criteria: The 30-day check must be performed server-side at submission time.

10. **Review Sorting**: Reviews on the teacher's profile must be sorted as follows:
    - First: The top 5 reviews with a rating > 4 submitted within the last 90 days, in reverse chronological order (most recent first).
    - Then: All remaining reviews in reverse chronological order.
    - Acceptance Criteria: If fewer than 5 reviews meet the "top 5" criteria, all qualifying reviews appear first and the remaining slots are not padded with lower-rated reviews.

11. **Teacher Review Flagging**: Teachers must be able to flag a review as junk or poor quality by hovering over a review and clicking a flag icon ("Report this review").
    - Acceptance Criteria: On click, the flag icon must turn permanent blue and a toast must display "We will evaluate this review!" The flag event must be captured in the backend for admin review. The flagged review must remain visible until an admin decides to remove it.

12. **Video Player Pop-Up**: Clicking a teacher's uploaded video on their profile must open a pop-up video player.
    - Acceptance Criteria: The player must support play/pause via click on the video surface and timeline scrubbing via drag interaction. Closing the pop-up must return the user to the profile without page navigation.

13. **Public Profile URL**: Each teacher must have a unique, shareable public URL for their profile.
    - Acceptance Criteria: When accessed via the public URL, the profile must be read-only. Interactive functions — "Write a review," "Edit profile," and any student-only CTAs — must be hidden or disabled. The public profile must display all the same content as the in-platform profile.

14. **Multi-Course Teacher Adaptation**: If a teacher teaches more than one course, the profile UI must accommodate multiple course listings.
    - Acceptance Criteria: All courses must be listed in the primary profile card. In the reviews section, the specific course relevant to each reviewer must be displayed as a tag next to the student's name.

## UX/UI Flows

### Edit Profile Flow (Teacher)
1. The teacher logs into their Teacher Dashboard.
2. They click "View and Edit Profile" in the top-right area of the dashboard.
3. They see a profile overview with a completeness status message.
4. They click "Edit Profile," triggering an edit pop-up modal.
5. In the modal, they can: upload or change their profile image (with format/size guidance), upload or change their video introduction, and update their "About Me" text.
6. They make changes and click "Submit."
7. A toast notification displays "Profile updated successfully."
8. The pop-up closes and the profile reflects the updated information.

### Submit Review Flow (Student)
1. A student is on their Student Dashboard viewing an Upcoming or Completed class.
2. The student clicks the teacher's name/image or the "Write a review" button on the class card.
3. The student is taken to (or shown a modal for) the teacher's profile page.
4. The student clicks "Write a Review."
5. A review form appears with a star rating selector and a free-text field.
6. Optionally, the student checks "Give this review anonymously."
7. The student selects a star rating and types their review text.
8. The student clicks "Submit Review."
9. A toast notification displays "Thanks! Your review is submitted."
10. The review appears in the reviews section of the teacher's profile (with anonymized display if anonymous was selected).

### Report Review Flow (Teacher)
1. The teacher is viewing their profile and reviews section.
2. They hover over a specific review they want to flag.
3. A flag icon ("Report this review") appears on hover.
4. The teacher clicks the flag icon.
5. The icon immediately turns permanent blue (no further confirmation dialog).
6. A toast displays "We will evaluate this review!"
7. The flag event is captured in the backend for admin review.
8. The review remains visible on the profile until an admin makes a removal decision.

### Public Profile View (External User)
1. A teacher copies their public profile URL and shares it externally (e.g., via WhatsApp, LinkedIn).
2. An external user (not logged in or without a teacher-student relationship) opens the URL.
3. The profile loads in a read-only state displaying: profile image, video, bio, stats, ratings, and reviews.
4. Interactive elements ("Write a review," "Edit Profile," class-specific CTAs) are hidden.
5. The external user can watch the video introduction via the pop-up video player.

## Technical Requirements

- **Prashashak Integration**: The system must integrate with the Prashashak admin panel to auto-pull and display the teacher's name, course, ID, country/flag, and languages. A sync mechanism must be defined to keep profile data current when Prashashak data changes.
- **Rating Calculation Engine**: The backend must calculate and store a composite rating for each teacher as the average of two data sources: (1) ratings from the "write a review" feature, and (2) the average of class card ratings from the last 3 months (rolling window). This must recalculate in near-real time when new ratings are submitted.
- **Review Database Model**: The reviews table must store: reviewer ID, teacher ID, star rating, review text, anonymity flag, submission timestamp, course tag, and flagged status. The 30-day update-vs-create logic must be implemented server-side at the time of review submission.
- **Anonymous Review Enforcement**: When a review is submitted with the anonymous flag, the reviewer's identity must be masked at the data layer, not just the display layer. Admin tools must not expose the reviewer's identity to teachers.
- **Flag Capture**: When a teacher clicks "Report this review," the flag event must be stored in the backend with the review ID, teacher ID, and timestamp. An admin notification or queue entry must be created for admin follow-up.
- **Video Player**: The in-platform video player must support play/pause via click and timeline scrubbing. The pop-up must be implemented as an overlay modal that does not navigate away from the current page.
- **Public URL Access Control**: The public profile URL must be accessible without authentication. Interactive features must be disabled on public URL access, enforced at the API layer (not just the frontend).
- **File Storage**: Profile images and videos must be stored in a file storage system with appropriate access controls. Video files up to 250 MB must be supported.

## Non-Functional Requirements

- **Performance**: File size constraints (max 5 MB for images, max 250 MB for videos) are in place to manage storage costs and load times. Video files must use a streaming-compatible format/encoding to enable playback without requiring full download.
- **Storage Optimization**: The strict upload size limits imply a need for server-side validation before the file is fully uploaded (or immediately after). Chunked/resumable uploads should be considered for video files.
- **Localization**: "Country and flag" and "Languages" fields on the profile indicate basic localization support. These are managed by Prashashak and must display in a localized format based on the user's region.
- **Accessibility**: Profile images must have alt text. The video player must support keyboard controls for play/pause. Review star ratings must be accessible via keyboard.
- **Security**: The anonymity flag on reviews must be treated as a security property, not just a display preference. No API endpoint that teachers can access must return the reviewer's identity for anonymous reviews.

## Success Metrics

- **No Standalone KPI**: There is no separate impact metric calculated for this specific feature because it serves as a prerequisite for multiple other line items and initiatives. Its success is measured through its downstream impact on dependent features.
- **Downstream Impact Features**: Teacher Profile and Reviews is a stated prerequisite for:
  - Teacher selection in LingoCHAMPS demo bookings
  - BrightBuddy assignment flows
  - Student onboarding teacher display flows
- **Implied Quality Metrics**: Average teacher profile completeness rate; number of reviews submitted per month; average teacher rating across the platform; teacher retention rate (measuring the "profile as retention mechanism" hypothesis).

## Edge Cases & Error Handling

- **Incomplete Profile**: If any profile section is missing (no image, no video, or no bio), the dashboard message must dynamically change from "Your profile is 100% complete" to "Please complete your profile." The incomplete sections must be highlighted or linked for easy navigation to the edit flow.
- **Anonymous Review Display**: If a student opts to submit anonymously, the system must display "Anonymous student" as the reviewer name and replace their profile picture with a blurred/generic image. This must be consistent across all surfaces where the review appears.
- **Student Review at 30-Day Boundary**: If a student submits a new review exactly on or after 30 days from their most recent review for the same teacher, the system must create a new review record. If before the 30-day mark, it must update the existing review. The system must handle the exact 30-day timestamp edge case consistently (inclusive or exclusive — defined by engineering).
- **Multi-Course Teacher Reviews**: When a teacher teaches multiple courses, the review form must capture the specific course relevant to the student submitting the review. The course tag must be displayed next to the student's name in the reviews section to provide context.
- **Video Upload at Size Boundary**: If a teacher uploads a video that is exactly at the 20 MB minimum or 250 MB maximum boundary, the system must accept it without error. Files below 20 MB or above 250 MB must be rejected with a clear explanation.
- **Flagged Review Pending Admin Review**: Once a teacher flags a review, the review must remain visible to all users until an admin takes action. The teacher must not be able to un-flag a review; only admins can resolve flagged items.
- **Public URL Access Without Authentication**: If an unauthenticated user accesses a teacher's public URL, the profile must load successfully without requiring login. Any attempt to interact with restricted actions must be silently suppressed without redirecting to a login page.

## Dependencies

- **Prashashak Admin Panel**: This feature relies heavily on Prashashak to populate foundational profile data (name, course, ID, country/flag, languages). The profile cannot be fully displayed without this integration being in place and data being current.
- **Downstream Feature Dependencies**: The Teacher Profile and Reviews feature is a strict prerequisite for multiple planned features. These features must not be scoped into a sprint before Teacher Profile is complete:
  - Teacher selection flow in LingoCHAMPS demo bookings
  - BrightBuddy assignment flows
  - Student onboarding teacher display flows
- **Class Card Rating System**: The dynamic rating calculation depends on class card ratings being tracked on the student dashboard. The class card rating capture mechanism must be in place and feeding the ratings database before the composite profile rating can be computed.
- **Team Involvement**: Successful deployment requires involvement from Business, Product, Design, Tech, and QA teams. Given the prerequisite nature of this feature for multiple downstream flows, it should be treated as high-priority infrastructure.
- **Admin Review Workflow**: The "Report this review" flagging system requires an admin workflow in the backend (or Prashashak) where flagged reviews can be evaluated and actioned. This must be built in parallel with or before the teacher-facing flagging UI is released.
