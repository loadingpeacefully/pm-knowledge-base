---
title: Student Showcase — Generating Project Videos for Feed
category: product-prd
subcategory: student-lifecycle
source_id: 81e2e49a-5959-4b0f-999a-81768e17c94b
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Student Showcase — Generating Project Videos for Feed

## Overview

The Student Showcase feature introduces a native video recording and publishing capability directly within the student's classroom environment. It enables students to record their coding projects — including their screen and a camera overlay — narrate the key features of what they have built, and publish the result to a feed for peers, parents, and teachers to view. This creates a "can show, can tell" learning environment where students demonstrate mastery through self-expression rather than just test scores.

The feature is designed to close a significant experiential gap in the current platform: students complete coding projects in class but have no way to preserve, present, or share their work with an audience. Showcase transforms project completion from a private milestone into a social, rewarding moment. The published video appears both in the student's personal feed and in a moderated global feed visible to peers, giving students an audience and a reason to put their best work forward.

The Showcase workflow is embedded natively in the student classroom interface — available on both the web and desktop app versions of the Student Classroom. The recording, editing, captioning, and publishing steps are all completed within the platform without requiring any external tools, reducing friction and keeping the student in their learning environment throughout the entire process. The feature is currently in DRAFT status as of the source document.

## Problem Statement

Students at BrightChamps complete coding projects during their classes, but there is no mechanism for them to record, present, or share those projects with an audience. This creates a missed opportunity on multiple fronts: students lose the motivational benefit of an audience, parents cannot see what their children are building, and the platform misses a powerful word-of-mouth and lead generation opportunity (showcase videos shared externally serve as organic proof of the platform's value). The absence of a "show your work" capability also means students cannot practice the critical 21st-century skill of presenting and articulating their technical work — a skill as important as building the project itself.

## User Stories

- As a student, I want to initiate a screen and camera recording from within my current lesson, so that I can showcase my completed project to my teacher and peers without leaving the classroom environment.
- As a student, I want to toggle my camera and microphone on/off and reposition my camera overlay on the screen, so that I have full control over how I appear in the video and can focus attention on the right parts of my project.
- As a student, I want to record my project screen while narrating the project's features and highlights, so that I can explain what I built and why, practicing both technical and communication skills.
- As a student, I want to preview my recording after finishing, trim the start and end segments, and re-record if I am not satisfied, so that the final showcase video highlights my best work and I feel confident publishing it.
- As a student, I want to add a caption or short description to my showcase before publishing, so that viewers understand the context and purpose of my project without needing to watch the entire video.
- As a teacher, I want to act as a moderator and decide whether a showcase video is appropriate to publish on the global feed, so that the shared feed maintains quality and safety standards for all students.

## Feature Scope

### In Scope

- Recording initiation modal integrated into the student classroom sidebar
- Recording source selection: full screen, specific window, or cropped area
- Camera overlay with two display modes: circular webcam bubble or green screen
- Camera and microphone toggle controls (on/off)
- Camera bubble repositioning to any corner of the screen
- Start/stop recording with an on-screen countdown (3-2-1) and recording timer
- Pause/Resume, Mute/Unmute, Retake, and Finish controls during recording
- Post-recording video preview and editing: timeline handles for trimming start/end
- Re-record option from the preview step
- Caption/description input (up to 100 characters) before publishing
- "Launch Showcase" action to publish the video
- Upload progress indicator
- "Your showcase is live!" confirmation state
- Student's personal feed showing their published showcases
- Global feed with video thumbnail cards viewable by peers
- Video player modal for viewing showcases on the global feed
- Teacher moderation flow to approve/reject showcase videos before global feed publication
- Browser permission requests for camera and microphone access

### Out of Scope

- Showcases from mobile devices (limited to Student Classroom Web and Desktop App)
- Advanced video editing beyond start/end trimming (no cuts, transitions, or text overlays)
- Video hosting via third-party platforms (e.g., YouTube, Vimeo) — videos are stored securely on BrightChamps infrastructure
- Direct sharing of showcase videos to external social media platforms (in this version)
- Comments or reactions on showcase feed items (separate comments system)
- Analytics on video views or engagement per showcase (not in V0)

## Functional Requirements

1. **Initiate Recording Modal (MUST HAVE)**: A "Showcase" panel in the classroom sidebar must surface a "Start Now" button. Clicking it opens a recording configuration modal or side drawer labeled "Showcase Options".
   - Acceptance Criteria: The Showcase panel must be accessible at any point during a class session. The modal must open without disrupting the active classroom session.

2. **Select Recording Source (MUST HAVE)**: The user must be able to choose from three recording area options: full screen, a specific application window, or a user-defined cropped area.
   - Acceptance Criteria: All three source types must be selectable. The selected source must be visually indicated in the configuration UI before recording starts.

3. **Camera Overlay Integration (MUST HAVE)**: The user must be able to enable or disable their camera overlay. When enabled, they must choose between a circular webcam bubble (100x100 px) or a green screen display. The camera bubble must be repositionable to any corner of the screen.
   - Acceptance Criteria: Camera toggle must work independently of the microphone toggle. The default microphone state is OFF. Camera overlay positioning must persist across the recording session (not reset on pause/resume).

4. **Start/Stop Recording with Timer (MUST HAVE)**: A "Start Recording" button must trigger a 3-2-1 countdown on screen before recording begins. An on-screen timer must run during recording. A single-click "Finish" button must stop the recording.
   - Acceptance Criteria: The 3-2-1 countdown must be clearly visible. The recording timer must count upward from 00:00:00. A maximum recording duration of 3 minutes (00:03:00) must be enforced.

5. **In-Recording Controls (MUST HAVE)**: During recording, the user must have access to: Pause/Resume, Mute/Unmute, Retake (discard current and restart), and Finish.
   - Acceptance Criteria: Pause must suspend the recording timer. Resume must continue it. Retake must discard the current recording entirely and return the user to the configuration step.

6. **30-Second Warning**: When the recording timer reaches 00:00:30 (30 seconds remaining), a toast notification must display: "The recording will stop in 30 seconds."
   - Acceptance Criteria: The toast must be non-blocking (does not interrupt recording). The recording must automatically stop at 00:00:00.

7. **Preview and Edit Clip (MUST HAVE)**: After stopping the recording, a video player must open showing the full clip. Timeline handles must allow the user to trim the start and end of the video.
   - Acceptance Criteria: The trimmed segment must be clearly visualized in the timeline. "Restart Recording" must discard the clip and return to configuration. "Next" must save the trimmed segment and advance to the caption step.

8. **Add Caption (MUST HAVE)**: A text input field must allow the student to add a short description of up to 100 characters before publishing.
   - Acceptance Criteria: Character count must be displayed live. Exceeding 100 characters must be prevented (hard cap). The caption field must be optional — the user can proceed without entering text.

9. **Launch (Publish) Showcase (MUST HAVE)**: Clicking "Launch Showcase" must upload the trimmed video and caption to the server. An upload progress indicator must be shown. A "Your showcase is live!" confirmation state must appear upon successful upload.
   - Acceptance Criteria: The publish action must not be available until at least the recording step is complete. Upload progress must update in real time. On upload failure, an error state must be shown with a retry option.

10. **Playback and Display on Feed (MUST HAVE)**: The published video must appear as a thumbnail card on the student's personal feed ("My Feed") and on the global feed. Clicking the thumbnail must open a video player modal supporting play/pause and timeline scrubbing.
    - Acceptance Criteria: The video player modal must open without navigating away from the feed page. Play/pause must be controlled via click on the video. Timeline scrubbing must be supported.

11. **Teacher Moderation Flow (MUST HAVE)**: Teachers must have a review interface to decide whether each submitted showcase is appropriate for publication on the global feed.
    - Acceptance Criteria: Teachers must be able to approve or reject a showcase. Rejected showcases must not appear on the global feed. Students must receive a notification when their showcase is approved or rejected.

12. **Browser Permission Handling**: If camera or microphone permissions have not been granted by the browser, the system must request them when the user clicks "Start Recording".
    - Acceptance Criteria: If the user denies permissions, recording must not start. An informational message must explain that camera/microphone access is required for Showcase.

## UX/UI Flows

### Step 01 — Initiate
1. The student is in their classroom session and sees a "Showcase" panel in the sidebar.
2. The student clicks "Start Now" on the panel.
3. A modal or side drawer labeled "Showcase Options" opens.

### Step 02 — Configure
1. The user selects their recording area from three options: full screen, a specific window, or a cropped frame.
2. The user toggles their camera on or off (default: off), selects their camera display mode (circular bubble or green screen), and drags the camera bubble to their preferred corner.
3. The user toggles their microphone on or off (default: off).
4. The user clicks "Start Recording."
5. A 3-2-1 countdown appears on screen.

### Step 03 — Record
1. Recording begins. An on-screen recording indicator is visible along with the running timer.
2. Controls available: Pause/Resume, Mute/Unmute, Retake, Finish.
3. The student interacts with their project and narrates their work.
4. At 00:00:30 remaining, a toast notification appears: "The recording will stop in 30 seconds."
5. The student clicks "Finish" (or recording auto-stops at 00:00:00).

### Step 04 — Preview and Edit
1. A video player opens displaying the full recorded clip.
2. The student reviews the clip. Timeline handles are available to trim the start and/or end.
3. Option A: "Restart Recording" — discards the clip and returns to Step 02 (Configure).
4. Option B: "Next" — saves the trimmed segment and advances to the caption step.

### Step 05 — Add Caption
1. A text input field is displayed with a 100-character limit shown as a live counter.
2. The student types a brief description of their project (optional).
3. The student clicks "Launch Showcase."
4. The system uploads the video (progress bar shown).
5. Upon successful upload: "Your showcase is live!" confirmation is displayed.

### Step 06 — Viewing on Feed
1. The published video appears as a thumbnail card in the student's "My Feed" section.
2. In the Global Feed, peers see the video thumbnail card.
3. A peer or parent clicks the thumbnail to open the video player modal.
4. The modal supports play/pause and timeline scrubbing.

### Teacher Moderation Flow
1. Teacher receives a notification that a student has submitted a showcase for review.
2. Teacher opens the review interface and watches the video.
3. Teacher clicks "Approve" or "Reject."
4. If approved: the video is published to the global feed and the student is notified.
5. If rejected: the video is not published and the student is notified with feedback.

## Technical Requirements

- **Browser Permissions**: The platform must use the browser's MediaDevices API to request camera and microphone permissions before recording begins. Permission denial must be handled gracefully with a user-facing message.
- **Screen Capture API**: The recording feature requires the browser's Screen Capture API (getDisplayMedia) to capture the selected recording area (full screen, window, or cropped region).
- **Video Storage**: Recorded videos must be uploaded and securely stored on the BrightChamps server. Access to videos on the global feed must be restricted to authenticated users.
- **Video Player**: The feed thumbnail player and the full-screen modal player must support at minimum: play/pause via click on the video surface, and timeline scrubbing via drag interaction.
- **Upload Progress**: The upload state must be communicated to the frontend in real time (either via WebSocket, polling, or upload progress events from the HTTP multipart upload API).
- **Moderation Queue**: The backend must maintain a moderation queue where teacher-submitted approval/rejection decisions are stored and reflected in the feed visibility logic.
- **Maximum Recording Duration**: The system must enforce a maximum recording duration of 3 minutes (00:03:00) at the recording layer, not just as a UI-level timer.
- **Platform Support**: The feature must function on both the Student Classroom Web (browser-based) and the Student Classroom Desktop App.

## Non-Functional Requirements

- **Platform Support**: Student Classroom Web and Student Classroom Desktop App only. Mobile is not in scope for this version.
- **Accessibility**: Recording controls (start, stop, pause, mute) must be keyboard accessible. The video player modal must support keyboard navigation for play/pause and timeline control.
- **Performance**: Video upload must support resumable uploads to handle unstable connections. The upload progress indicator must update in near-real time.
- **Security**: Recorded videos must be stored with access controls ensuring only authenticated users with appropriate roles (the student, their teacher, and enrolled peers) can view feed content.
- **Browser Compatibility**: Screen recording via getDisplayMedia is only available in Chromium-based browsers and Firefox. Safari limitations must be documented and surfaced to users attempting to use unsupported browsers.

## Success Metrics

- **Primary Business Impact Metric**: "Visitors to Leads" — the Showcase feature is tracked under this business impact funnel, with the hypothesis that published showcase videos drive external visibility and convert new visitors to leads.
- **Note on Draft Status**: Because the document is in DRAFT status, specific KPI values, adoption targets, and impact funnel metrics are currently left as blank template fields. These must be defined before the feature goes to implementation.
- **Implied Engagement Metrics**: Number of showcases created per week, number of showcases published to the global feed, number of video views per showcase, and teacher moderation turnaround time.

## Edge Cases & Error Handling

- **Recording Duration Limit**: The recording timer starts at 00:03:00 and counts down. At 00:00:30, a toast warning is displayed. At 00:00:00, recording automatically stops and the user is taken to the preview step. This is expected behavior, not an error state.
- **Camera/Microphone Permissions Denied**: If the user denies browser permissions for camera or microphone, recording must not start. The system must display an informational message explaining that these permissions are required and provide guidance on how to enable them in the browser settings.
- **Default Microphone State**: The microphone toggle is set to OFF by default to prevent unintended audio capture. Students must explicitly opt in to audio recording.
- **Upload Failure**: If the video upload fails after the student clicks "Launch Showcase," an error state must be shown with a clear retry option. The student's trimmed video and caption must be preserved so they do not need to re-record.
- **Teacher Rejects Showcase**: If a teacher rejects a showcase, the video must not appear on the global feed. The student must receive a notification. The video may remain visible in the student's own personal feed at the product team's discretion.
- **No Camera Detected**: If the student's device has no camera available, the camera overlay option must be disabled gracefully. Screen-only recording must still be available.

## Dependencies

- **Cross-Functional Team**: The feature requires coordination across Business (Micky Sukhwani), Product (Aakrit Balwant Patel, Paul), Design (Adnan), Tech (Dhawal Agrawal, Aditya Bhargav), and QA (Vidurbh Raj Srivastava).
- **Student Feed Feature**: The Showcase publishing flow depends on the Student Feed infrastructure being in place to surface the "My Feed" and "Global Feed" sections where showcase videos appear.
- **Teacher Notification System**: The teacher moderation flow depends on a notification system capable of alerting teachers when a new showcase is submitted for review.
- **Browser Compatibility Assessment**: Before development begins, the Tech team must confirm compatibility of Screen Capture API (getDisplayMedia) across the target browser set and document any limitations for the Desktop App wrapper.
- **Video Storage Infrastructure**: The backend team must provision and configure secure video storage with appropriate access control policies before the upload flow can be implemented.
