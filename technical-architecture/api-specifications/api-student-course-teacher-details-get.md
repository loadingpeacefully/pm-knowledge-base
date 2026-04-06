---
endpoint: GET /v1/student/get-course-teacher-details
service: eklavya
source_id: 2ad05a2c-5d9e-4794-b7ce-dc0d490c22da
original_source_name: get-course-teacher-details
controller: controllers/students.js:275
service_file: facades/student.js:120
router_file: routers/students.js:106-111
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/student/get-course-teacher-details

## Summary

Retrieves comprehensive student-course-teacher relationship data with advanced ACTIVE/PAST/INACTIVE status filtering, performance metrics, and churn analytics. Orchestrates 4–5 external service calls in parallel. The `INACTIVE` type query is fully dependent on the Paathshala churn analytics service — it returns early (empty) if that service is unavailable.

**Category:** Internal API — Student Management & Analytics
**Owner/Team:** Student Operations / Teacher Management Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/student/get-course-teacher-details`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Query Parameters

**Validation source:** `validators/student.js:20-44`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | integer | No | Filter by specific student |
| `teacherId` | integer | No | Filter by specific teacher |
| `type` | enum | No | Status filter: `ACTIVE`, `PAST`, `INACTIVE` |
| `studentName` | string | No | Partial name match |
| `pageCounter` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Records per page (no default enforced — critical issue) |
| `courseId` | integer | No | Filter by course |
| `studentClassBalanceId` | integer | No | Filter by specific balance |
| `leadSource` | string | No | Lead source filter (used but not in validator) |

**Type semantics:**
- `ACTIVE`: `total_paid_class > total_completed_class` AND not flagged as churned
- `PAST`: `total_paid_class <= total_completed_class` OR confirmed churned (`CHURN_CLASS`)
- `INACTIVE`: only students with `CHURN_RED_FLAG` status (potential churn)

### Request Examples

```
GET /v1/student/get-course-teacher-details
GET /v1/student/get-course-teacher-details?teacherId=123&type=ACTIVE
GET /v1/student/get-course-teacher-details?courseId=2&pageCounter=1&limit=20
GET /v1/student/get-course-teacher-details?studentName=John&type=ACTIVE
GET /v1/student/get-course-teacher-details?type=INACTIVE&teacherId=456
GET /v1/student/get-course-teacher-details?studentClassBalanceId=789
```

### Response Format

**Success — Active student (200):**
```json
{
  "success": true,
  "data": [{
    "studentClassBalanceId": 12345, "classType": "online",
    "totalBookedClass": 24, "totalPaidClass": 24, "totalCompletedClass": 8, "totalPenalties": 0,
    "courseId": 2, "courseName": "Coding for Kids",
    "studentId": 67890, "studentName": "Emma Johnson",
    "parentId": 54321, "parentName": "Sarah Johnson",
    "phone": "+12345678901", "referralCode": "ST123456", "grade": 5,
    "teacherId": 789, "teacherName": "John Smith",
    "countryId": 1, "email": "sarah.johnson@email.com", "country": "United States",
    "gender": "Female", "showcasePercentage": 85.5, "performanceGrade": "A",
    "profilePicture": "https://ik.imagekit.io/brightchamps/dashboard/avatar_girl.webp",
    "churnData": null, "isNewlyEnrolled": false, "studentLanguage": "en", "showPracticeZone": true
  }],
  "message": "Course and Teacher Detail fetched successfully."
}
```

**Inactive student — churn data populated:**
```json
{
  "churnData": {
    "studentClassBalanceDetailId": 23456, "status": "CHURN_RED_FLAG",
    "lastClassDate": "2024-11-01T10:00:00.000Z",
    "daysLeftToChurn": 15, "addedDate": "2024-10-25T09:00:00.000Z"
  }
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (empty array if no results) |
| 400 | Bad request — validation failed |
| 401 | Unauthorized |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:275-308`)

1. Extract all query params with defaults (`pageCounter = 1`)
2. Call `StudentFacade.getCourseAndTeacherDetails()`
3. Format via `ApiResponse` wrapper

### Facade (`facades/student.js:120-397`)

1. **Pagination:** compute `LIMIT` and `OFFSET`
2. **Type-specific filter + churn data:**
   - `ACTIVE`: `total_paid_class > total_completed_class` + 2 Paathshala calls (`CHURN_RED_FLAG`, `CHURN_CLASS`) → exclude churned students
   - `PAST`: `total_paid_class <= total_completed_class` + 1 Paathshala call (`CHURN_CLASS`) → include churned
   - `INACTIVE`: 1 Paathshala call (`CHURN_RED_FLAG`) → returns early if no churn data
3. **Database query:** `ClassBalanceService.getStudentClassBalance()` with includes:
   - `Student` → `Parent` + `StudentProfile`
   - Pagination: `LIMIT/OFFSET`
4. **Parallel external calls** (`Promise.allSettled`):
   - `platformService.getAllCourse()` — course names
   - `platformService.getAllCountries()` — country names
   - `teacherService.getTeachersById(teacherIds)` — teacher details
   - `studentPerformanceMetricsService.fetchStudentPerformances()` — current month metrics
5. **Data transformation:** build lookup maps, map performance metrics, compute `showcasePercentage`, `performanceGrade`, `isNewlyEnrolled`, `showPracticeZone`, gender-based profile pictures

---

## Microservice Dependencies

| Service | Call(s) | Trigger | Parallelism |
|---------|---------|---------|-------------|
| Paathshala | `getChurnData({ status: "CHURN_RED_FLAG" })` | ACTIVE (2×), INACTIVE (1×) | Sequential for ACTIVE (bug) |
| Paathshala | `getChurnData({ status: "CHURN_CLASS" })` | ACTIVE, PAST | — |
| Platform | `getAllCourse()` | Always | `Promise.allSettled` |
| Platform | `getAllCountries()` | Always | `Promise.allSettled` |
| Teacher Service | `getTeachersById(teacherIds)` | Always | `Promise.allSettled` |
| StudentPerformanceMetrics | `fetchStudentPerformances()` | Always | `Promise.allSettled` |

**Total external calls:** 4–5 per request (2 Paathshala for ACTIVE type)

**Critical:** `INACTIVE` type returns an empty array early if Paathshala returns no data or fails.

---

## Database & SQL Analysis

### Primary Query

```js
await this.classBalanceService.getStudentClassBalance(filter, {
  includeFilter: [
    { model: Student, required: true, attributes: ["grade","name","referralCode"],
      include: [
        { model: Parent, required: true, attributes: ["countryId","email","id","name","phone"] },
        { model: StudentProfile, required: true, attributes: ["profilePicture","gender"] }
      ] }
  ],
  limit: LIMIT,
  offset: OFFSET
})
```

### Equivalent SQL

```sql
SELECT scb.*, s.grade, s.name, s.referral_code,
       p.country_id, p.email, p.id, p.name, p.phone,
       sp.profile_picture, sp.gender
FROM student_class_balances scb
JOIN students s ON scb.student_id = s.id
JOIN parents p ON s.parent_id = p.id
JOIN student_profiles sp ON s.id = sp.student_id
WHERE scb.active = 1
  -- AND type-specific conditions
ORDER BY scb.id
LIMIT ? OFFSET ?;
```

### Type-Specific Filters

```sql
-- ACTIVE
WHERE scb.total_paid_class > scb.total_completed_class
  AND scb.id NOT IN (SELECT scb_detail_id FROM churn_data WHERE status IN ('CHURN_RED_FLAG','CHURN_CLASS'));

-- PAST
WHERE scb.total_paid_class <= scb.total_completed_class
   OR scb.id IN (SELECT scb_detail_id FROM churn_data WHERE status = 'CHURN_CLASS');

-- INACTIVE
WHERE scb.id IN (SELECT scb_detail_id FROM churn_data WHERE status = 'CHURN_RED_FLAG');
```

### Performance Metrics Query

```sql
SELECT spm.student_class_balance_id, spm_detail.metric_key, spm_detail.metric_value
FROM student_performance_metrics_summaries spm
JOIN student_performance_metrics spm_detail ON spm.id = spm_detail.summary_id
WHERE spm.created_at BETWEEN ? AND ?
  AND spm.student_class_balance_id IN (...)
  AND spm.teacher_id IN (...)
  AND spm_detail.metric_key IN ('SHOWCASE_PERCENTAGE','PERFORMANCE_GRADE');
```

### Recommended Indexes

```sql
CREATE INDEX idx_student_class_balance_active_paid_completed ON student_class_balances(active, total_paid_class, total_completed_class);
CREATE INDEX idx_student_class_balance_teacher_course ON student_class_balances(teacher_id, course_id);
CREATE INDEX idx_students_name ON students(name);
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_performance_metrics_scb_teacher_date ON student_performance_metrics_summaries(student_class_balance_id, teacher_id, created_at);
CREATE INDEX idx_performance_metrics_key ON student_performance_metrics(metric_key);
CREATE INDEX idx_parents_lead_source ON parents(lead_source);
```

---

## Technical Issues

### Critical Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | `INACTIVE` type has hard dependency on Paathshala — early return with empty data if service is down | `facades/student.js:219-220` | Total feature failure for INACTIVE view |
| 2 | No default pagination limit — without explicit `limit`, returns all records | Facade | Memory exhaustion, slow response |
| 3 | ACTIVE type makes 2 sequential Paathshala calls (should be parallel) | `facades/student.js:169-172` | 2× unnecessary latency |

### High Priority

| # | Issue | Impact |
|---|-------|--------|
| 4 | Platform reference data (`getAllCourse`, `getAllCountries`) fetched on every request — no caching | Unnecessary API calls on every request |
| 5 | Complex conditional query logic per type makes optimization hard | Inconsistent performance across types |
| 6 | Mixed error handling — some services use `Promise.allSettled` (graceful), others propagate directly | Unpredictable failures |

### Medium Priority

| # | Issue |
|---|-------|
| 7 | Performance metrics fetched for all results even when not needed |
| 8 | In-memory result transformation for potentially large datasets |
| 9 | Hardcoded avatar URLs, 30-day churn window, threshold constants |

---

## Test Scenarios

### Functional
- No filters — all students
- `teacherId` filter
- `type=ACTIVE` — active students
- `type=PAST` — completed/churned
- `type=INACTIVE` — churn risk
- `studentName` partial match
- Pagination (`pageCounter`, `limit`)
- Combined filters

### Business Logic
- Active student classification (paid > completed AND not churned)
- Churned student in PAST vs INACTIVE
- Days-to-churn calculation accuracy
- Profile picture gender logic
- `isNewlyEnrolled` and `showPracticeZone` derivation

### Error / Resilience
- Paathshala service down → INACTIVE returns empty (known behavior to document)
- Platform service timeout → courses/countries missing from response
- Teacher service failure → teacher names missing

### Performance
- Response time without filters (large dataset)
- ACTIVE vs INACTIVE type comparison
- Pagination: first vs last page
- Concurrent requests with different `type` filters
- External service timeout impact

### Edge Cases
- Student with zero completed classes
- Student with more completed than paid (data anomaly)
- Teacher with no current students
- Performance metrics missing for some students in result
