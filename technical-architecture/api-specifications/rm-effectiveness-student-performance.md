---
title: RM Effectiveness - Collecting Student Performance
category: technical-architecture
subcategory: api-specifications
source_id: 1b80c207-de09-4c92-b24c-41426dc6b4b0
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# RM Effectiveness - Collecting Student Performance

## Overview
This system collects and aggregates student performance data from paid classes, quizzes, homework, and class metrics to populate the `student_performance_matrix` in Eklavya. A cron-triggered Lambda in Paathshala runs every 30 minutes to identify students with activity in the last 30 days and fan-out to two SQS queues: one to update performance data in Paathshala, and one to sync that data to Zoho CRM for RM (Relationship Manager) effectiveness tracking.

## API Contract

| Property | Value |
|----------|-------|
| Method | Internal (SQS-triggered Lambda + downstream API calls) |
| Path | `/v1/student-performance-matrix/bulk-create` (Eklavya) |
| Auth | Internal service auth (API key) |
| Content-Type | application/json |

**Eklavya Bulk Create API:**
```
POST /v1/student-performance-matrix/bulk-create
```
Bulk inserts or updates student performance records.

**Dronacharya Teacher Ratings API:**
```
GET /api/v1/teacher/ratings
```
Fetches all ratings given by a student for teachers.

**SQS Queues:**
- `UPDATE_STUDENT_CLASS_PERFORMANCE_QUEUE` — triggers `updateStudentClassPerformance` Lambda.
- `UPDATE_STUDENT_PERFORMANCE_ON_ZOHO_QUEUE` — triggers Zoho sync.

## Logic Flow

### Controller Layer
- No HTTP controller — all triggered via EventBridge Cron → Lambda.

### Service/Facade Layer
**`collectStudentForStudentClassPerformance` Lambda:**
1. Runs every 30 minutes (`cron(17,47 * * * ? *)`).
2. Fetches up to 1000 distinct students who had paid class activity in the last `DAYS_FOR_COLLECTING_STUDENT_CLASS_PERFORMANCE` days (default: 30 days).
3. Uses Redis key `studentClassPerformance:fetch:{endDate}:{includeDays}:{utcDate}` to track the last processed `studentId` for cursor-based pagination.
4. For each student, publishes to both SQS queues.
5. Updates Redis cursor to last processed `studentId` with 24-hour TTL.

**`updateStudentClassPerformance` Lambda (Paathshala):**
- Fetches student data from:
  - `paid_classes` (statuses 13, or 14/16/17 where `is_exempt` = 0 in penalties)
  - `paid_class_metrics` (using metric keys listed below)
  - `paid_class_assignments`
- Processes metrics using specialized processor functions per metric key.
- Calls Dronacharya `GET /api/v1/teacher/ratings` for teacher rating data.
- Sends formatted data to Eklavya `POST /v1/student-performance-matrix/bulk-create`.

**Metric Processor Functions:**
```
"teacher-video-duration"  → processTeacherVideoDuration
"teacher-duration"        → processTeacherDuration
"student-duration"        → processStudentDuration
"perfect-class"           → processPerfectClass
"teacher-joined-zm"       → processTeacherJoining
"common-duration"         → processCommonDuration
```

### High-Level Design (HLD)
- Cursor-based Redis pagination prevents reprocessing already-fetched students within a 24-hour window.
- Fan-out pattern: each student is published to two SQS queues simultaneously (performance update + Zoho sync).
- Quiz/homework: pending means `obtained_score = 0`.
- Only paid classes with `status_id = 13` OR (`14, 16, 17` AND `is_exempt = 0`) are counted.

## External Integrations
- **Zoho CRM** — Student performance data synced via `UPDATE_STUDENT_PERFORMANCE_ON_ZOHO_QUEUE` for RM dashboards.
- **AWS SQS** — `UPDATE_STUDENT_CLASS_PERFORMANCE_QUEUE`, `UPDATE_STUDENT_PERFORMANCE_ON_ZOHO_QUEUE`.
- **AWS Lambda** — `collectStudentForStudentClassPerformance`, `updateStudentClassPerformance`.

## Internal Service Dependencies
- **Paathshala** — Source of paid class, metric, and assignment data.
- **Dronacharya** — `GET /api/v1/teacher/ratings` for teacher-student rating data.
- **Eklavya** — `POST /v1/student-performance-matrix/bulk-create` for storing final performance matrix.

## Database Operations

### Tables Accessed
**Paathshala:**
- `paid_classes` — filtered by status_id (13, 14, 16, 17) and `is_exempt`
- `paid_class_metrics` — metric keys: `perfect-class`, `teacher-video-duration`, `teacher-duration`, `student-duration`, `teacher-joined-zm`, `common-duration`
- `paid_class_assignments` — homework/quiz data

**Eklavya:**
- `student_performance_matrix` — bulk created/updated

### SQL / ORM Queries
**Cursor-based student fetch:**
```javascript
getDistinctStudentsForCreditUsedClasses({
  startDate, endDate,
  studentId: { [Op.gt]: fetchedStudentId },
  limit: LIMIT_FOR_FETCHING_STUDENT_CLASS_PERFORMANCE  // 1000
})
```

**Performance data table fields tracked:**
```
Id, studentId, teacherId, studentClassBalanceId,
total_completed_paid_class, total_missed_paid_classes,
total_classes_rated, average_class_rating,
total_hw_given, total_hw_completed,
total_quiz_given, total_quiz_completed, average_quiz_score,
total_perfect_class, teacher_joined_on_time,
teacher_camera_on, teacherAverageCameraOnDuration,
teacher_average_class_duration, student_average_class_duration,
first_class_date, last_class_date,
teacher_rating, teacher_last_rated_at
```

### Transactions
- N/A — Eklavya bulk create handles upsert atomicity internally.

## Performance Analysis

### Good Practices
- Redis cursor pagination prevents full table scans on repeated cron runs.
- Batch size capped at 1000 students per cron run to prevent Lambda timeout.
- Metric processing uses a dispatch object (`getMatrixProcessFunc`) avoiding conditional chains.
- `cron(17,47 * * * ? *)` offsets from the top of the hour to avoid contention with other crons.

### Performance Concerns
- SQS fan-out to two queues per student means 2000 SQS publishes per 1000 students per cron run.
- Lambda `timeout: 900` (15 minutes) — high ceiling may mask slow DB queries.
- `maximumRetryAttempts: 1` — limited retry on failure may miss student updates.

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Redis cursor key uses `getUTCDate()` which resets daily — students processed near midnight may be duplicated or skipped at the date boundary. |
| Medium | `maximumRetryAttempts: 1` means a transient Lambda failure silently drops student performance updates. |
| Low | `includeDays` defaults in source suggest a possible tight coupling between Lambda config and data recency expectations. |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Increase `maximumRetryAttempts` to 3 and configure a DLQ for failed student updates.
- Add CloudWatch metrics for queue depth of both SQS queues.

### Month 1 (Architectural)
- Replace cursor-based Redis pagination with a dedicated processing queue (SQS FIFO) to avoid Redis key expiry edge cases.
- Parallelize Dronacharya and Paathshala data fetches with `Promise.all` if not already done.

## Test Scenarios

### Functional Tests
- Run cron with 10 students active in last 30 days → verify all 10 get published to both SQS queues.
- Verify Redis cursor advances correctly after each cron run.
- Verify `updateStudentClassPerformance` Lambda processes all metric keys correctly.
- Verify Eklavya bulk create endpoint receives well-formed performance matrix payload.

### Performance & Security Tests
- Test cron with 1000 students — verify Lambda completes within 900-second timeout.
- Verify only internal service auth can call Eklavya bulk create.

### Edge Cases
- Student with zero completed paid classes — verify zero-count metrics are correctly stored (not null).
- Quiz/homework with `obtained_score = 0` → should be marked as pending.
- Cron runs near UTC midnight — verify Redis cursor key transition does not skip students.
- Dronacharya ratings API returns empty → verify graceful handling (no rating fields set, not error).

## Async Jobs & Automation
- **EventBridge Cron:** `cron(17,47 * * * ? *)` — every 30 minutes at :17 and :47.
- **`collectStudentForStudentClassPerformance` Lambda (Paathshala):** Cursor-based student collection and SQS fan-out. Timeout: 900s, maxEventAge: 1200s, maxRetry: 1.
- **`UPDATE_STUDENT_CLASS_PERFORMANCE_QUEUE` (SQS):** Feeds `updateStudentClassPerformance` Lambda.
- **`UPDATE_STUDENT_PERFORMANCE_ON_ZOHO_QUEUE` (SQS):** Feeds Zoho CRM sync process.
