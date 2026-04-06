---
title: Paathshala API Specification
category: technical-architecture
subcategory: api-specifications
source_id: b38cbb41
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Paathshala API Specification

## Overview
Paathshala is the core Class Service within the Coretech microservices architecture. It manages demo and paid class lifecycle, feedback submission, curriculum modules, group enrollment, and real-time teacher-student Auxo mapping. It integrates with Eklavya (Student), Tryouts (Booking), and Doordarshan (Meetings) via REST and event-driven architecture.

## API Contract

### GET /demo/feedback?classId=<id>
- **Auth:** Teacher JWT
- **Response:**
```json
{
  "classId": int,
  "courseId": int,
  "courseName": "string",
  "courseType": "FinChamp|CodeChamp|...",
  "teacherId": int,
  "teacherName": "string",
  "studentId": int,
  "studentName": "string",
  "classTime": "ISO8601",
  "grades": [1-12],
  "classStatuses": [],
  "issueDetailOptions": [
    "No Proper Engagement", "Student left", "Language Issue", "Network issue", "Rescheduled by parent"
  ]
}
```

### POST /demo/feedback
- **Auth:** Teacher JWT
- **Request Body:**
```json
{
  "classStatus": "int",
  "review": "string",
  "issueDetail": null,
  "notes": null,
  "reschedule": {
    "parentWillReschedule": true,
    "parentRescheduleTime": false,
    "rescheduleTime": "ISO8601"
  },
  "courseFeedback": {
    "courseId": int,
    "data": {}
  }
}
```

### POST /paathshala/api/v1/class/paid/feedback/v2
- **Auth:** Teacher JWT
- **Purpose:** Submit paid class feedback; triggers `update-paid-class-status` SQS message
- **Status Codes:** 200 OK, 400 Bad Request

### GET /class/demo/class-by-time
- **Auth:** Internal
- **Query Params:** `startTime` (required), `endTime` (required)
- **Purpose:** Fetch demo classes scheduled in a time window
- **Response includes:** meeting joiner details, durations, class errors from `class_errors`, joining metrics from `demo_class_metrics`

### Class Operations (Admin — Add/Remove)
Operations for live demo class management:
- **`student_addition`** — Insert `booking_id` into `demo_classes`
- **`student_removal`** — Nullify `booking_id` in `demo_classes`
- **`teacher_addition`** — Update `teacher_confirmation_id` in `demo_classes`
- **`teacher_removal`** — Nullify `teacher_confirmation_id` in `demo_classes`

### GET /paathshala/api/v1/curriculum/modules
- **Auth:** `x-api-key`
- **Query Params:** `Course` (optional)
- **Response:** Array of module objects with id, name, version, category, grade range, course, duration

### GET /paathshala/api/v1/curriculum/modules/{moduleId}
- **Auth:** `x-api-key`
- **Response:** Module with nested `CurriculumTopics` → `CurriculumProjects` (lessonPlanLink, projectLink, assignmentLink, sessionBooklet, conceptsCovered)

### POST /paathshala/api/v1/curriculum/modules
- **Auth:** `x-api-key`
- **Request Body (all required):** `name, curriculumVersionId, curriculumCategoryId, startGrade, endGrade, active, type, courseId, durationId`
- **Status Codes:** 200 Created, 400 Missing params

### PATCH /paathshala/api/v1/curriculum/modules/{moduleId}
- **Auth:** `x-api-key`
- **Request Body:** At least one module field
- **Status Codes:** 200 OK, 400 No params provided

### POST /paathshala/api/v1/groups/enroll-student
- **Auth:** `x-api-key`
- **Request Body:** `{ "student_id": int, "group_name": "string" }`
- **Purpose:** Enroll student in a group; creates `paid_classes` records and curriculum mappings

### POST /paathshala/api/v1/groups/remove-student
- **Auth:** `x-api-key`
- **Request Body:** `{ "student_id": int, "group_name": "string" }`
- **Purpose:** Remove student from group; refund diamonds

## Logic Flow

### Controller Layer
- Feedback → `FeedbackController` → SNS publish on "Successful" demo
- Curriculum CRUD → `CurriculumController`
- Group enrollment → `GroupController`
- Auxo mapping → `MappingController` → FIFO queue if unmapped

### Service/Facade Layer
- Demo feedback triggers SNS → Prabandhan SQS → CRM deal creation
- Paid feedback triggers SQS → Lambda → Eklavya balance update
- Group enrollment creates `paid_classes` records atomically
- Auxo mapping: check existing mapping → if none, push to FIFO queue for Tryouts to process

### High-Level Design (HLD)
- Paathshala is deployed on EKS
- MySQL on AWS RDS for all class/curriculum data
- Auxo mapping uses FIFO queue + Redis for real-time teacher-student assignment
- Curriculum management uses Sequelize ORM

## External Integrations
- **AWS SNS/SQS:** Demo feedback fan-out, paid class status update queue
- **AWS RDS (MySQL):** Primary database
- **Platform Service:** Course metadata resolution for curriculum endpoints
- **Zoom (via Doordarshan):** Meeting events → `demo_class_metrics` updates

## Internal Service Dependencies
- Eklavya: `PATCH /eklavya/v2/student-class-balance` on paid class completion
- Tryouts: FIFO queue for Auxo mapping; `/v1/booking/details` for class context
- Dronacharya: Teacher earnings data for upcomingClassDetails Lambda
- Doordarshan: Meeting link provisioning for new classes

## Database Operations

### Tables Accessed
- `demo_classes`: `booking_id`, `teacher_confirmation_id`
- `paid_classes`: `paid_class_status_id`
- `paid_class_metrics`: `metric_key`, `value` (e.g., class-completion-reason)
- `demo_class_metrics`: Join metrics per class
- `class_errors`: Error events per class
- `curriculum_modules`, `curriculum_topics`, `curriculum_projects`: Curriculum hierarchy
- `demo_curriculum`: Fallback curriculum for demo classes

### SQL / ORM Queries
- SELECT `demo_classes` WHERE `id` for booking+teacher mapping
- UPDATE `paid_classes.paid_class_status_id`
- UPSERT `paid_class_metrics`
- INSERT batch `paid_classes` on group enrollment
- SELECT curriculum with nested topic+project joins

### Transactions
- Group enrollment: batch `paid_classes` INSERT is atomic
- Group removal: student-group mapping delete + diamond refund is atomic

## Performance Analysis

### Good Practices
- API key authentication for admin-facing curriculum management
- Auxo mapping uses FIFO queue to prevent race conditions
- Batch INSERT for group enrollment avoids N+1 write pattern

### Performance Concerns
- Nested curriculum query (module → topics → projects) can return large payloads for complex courses
- FIFO queue processing adds 1–2 second latency to teacher-student mapping

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Auxo mapping FIFO queue turnaround of 1–2 seconds is acknowledged as a target for reduction |
| Low | `class_errors` and `demo_class_metrics` tables referenced in GET endpoint but not fully documented |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add pagination to curriculum module list endpoint
- Add index on `demo_classes(booking_id)` for faster Auxo lookup

### Month 1 (Architectural)
- Pre-compute and cache curriculum module trees in Redis on publish/update
- Reduce Auxo mapping FIFO queue turnaround via pre-warmed Redis sorted sets

## Test Scenarios

### Functional Tests
- Submit demo feedback "Successful" → SNS event published → CRM deal created
- Submit paid feedback → SQS triggered → Lambda updates `paid_classes` and Eklavya balance
- Enroll student in group → verify `paid_classes` records created with correct class count
- Remove student from group → verify group mapping removed and diamonds refunded
- Create curriculum module → verify all required fields enforced

### Performance & Security Tests
- Verify `x-api-key` required on curriculum and group endpoints
- Load test `/class/demo/class-by-time` with large time window

### Edge Cases
- Group enrollment with invalid `group_name` → graceful 404
- Paid class feedback submitted twice for same class (idempotency)
- Curriculum module created with `active = false` (should not appear in student curriculum)

## Async Jobs & Automation
- **`update-paid-class-status` SQS Consumer (Lambda):** Triggered by paid feedback API; updates `paid_classes` and calls Eklavya
- **`prabandhan-class-completion-flow` Lambda:** Triggered by SNS "Successful" demo feedback; CRM deal creation
- **`upcomingClassDetails` Lambda (Cron):** Pre-populates `paid_class_metrics` for classes in next 24 hours
- **Paid Schedule Window Expiry Cron:** Cancels `status_id = 18` classes within 2-hour window during teacher leave
