---
endpoint: GET /eklavya/v1/student/get-course-teacher-details
service: eklavya
source_id: 1deb6d9f-4d62-4124-b296-e6287f2d216d
duplicate_source_id: cbc8911d-9dac-45db-9333-bd821474cc0b
original_source_name: _studentId-040426-181554.pdf
note: Earlier/simpler version of the same endpoint. Full enriched doc at api-student-course-teacher-details-get.md (source 2ad05a2c)
created_at: 2026-04-05
source_notebook: NB1
---

# GET /eklavya/v1/student/get-course-teacher-details (V1 Spec)

## Summary

Fetches all students associated with a given `teacherId`, with optional filtering for ACTIVE/PAST students and student name search. Supports pagination. Data is sourced from the `student_class_balances` table in Eklavya, joined with student, course, teacher, and country records.

**Jira:** BCT-473 — API to fetch data wrt class id on teacher dashboard
**Feature:** Students Page on Teacher Dashboard (My Students + Student Profile Page)
**Document Status:** INPROGRESS
**Document Owner:** @Gurivelli Satish

> **Note:** This is the V1 specification document. The fully enriched version (with churn analytics, INACTIVE state, parallel service calls) is at [`api-student-course-teacher-details-get.md`](api-student-course-teacher-details-get.md).

---

## HTTP Contract

**Method:** GET
**Path:** `/eklavya/v1/student/get-course-teacher-details`
**Authentication:** API Key (`X-API-KEY: eklavyaapikey`)

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| teacherId | integer | No | Filter by teacher |
| studentId | integer | No | Filter by specific student |
| type | string | No | `ACTIVE` or `PAST` |
| studentName | string | No | Partial name match (LIKE search) |
| pageCounter | integer | No | Pagination offset |

### Response (200 OK)

```json
{
  "success": 200,
  "data": [
    {
      "studentClassBalanceId": 6131,
      "totalBookedClass": 150,
      "totalPaidClass": 150,
      "totalCompletedClass": 23,
      "totalPenalties": 0,
      "courseId": 1,
      "courseName": "Coding",
      "studentId": 41568,
      "studentName": "Zehra Siyad",
      "grade": 7,
      "teacherId": 88,
      "teacherName": "Gifty Abhishek Telagathoti",
      "countryId": 2,
      "country": "UAE",
      "profilePicture": "https://brightchamps-student-profile.s3.ap-south-1.amazonaws.com/..."
    }
  ],
  "message": "Course and Teacher Detail fetched successfully.",
  "status": 200,
  "errors": []
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request / validation error |
| 424 | Dependency error |
| 500 | Internal server error |

---

## Business Logic

### HLD

1. **Solution:** Create an API in Eklavya service where student-teacher mapping is stored in the `student_class_balances` table.
2. **Use case:** Called from the Students Page on Teacher Dashboard — teachers view their students and student progress.
3. **Data flow:** Request comes in with optional `teacherId`, `type`, `studentName`, `studentId`. Filters are applied to `student_class_balances` join query. Results paginated via `pageCounter`.

### Filter Logic

**Active students** (type = ACTIVE):
```js
filter.total_booked_class = {
  [Op.gt]: literal("total_completed_class + total_penalties"),
};
```

**Past students** (type = PAST):
```js
filter.total_booked_class = {
  [Op.lte]: literal("total_completed_class + total_penalties"),
};
```

**Name search:**
```js
filter = {
  "$Student.name$": studentName
    ? { [Op.like]: `%${studentName}%` }
    : null,
}
```

---

## Database Analysis

### Tables Involved

| Database | Table | Access |
|----------|-------|--------|
| eklavya | `student_class_balances` | Read (primary — student-teacher mapping) |
| eklavya | `students` | Read (join — name, grade, profile) |
| eklavya | `parents` | Read (join) |
| platform | `master_courses` | Read (join — course name) |
| platform | `countries` | Read (join — country name) |
| dronacharya | `teachers` | Read (join — teacher name) |

### Performance Concerns

- **No pagination limit enforcement**: `pageCounter` passed but no max page size — could return unbounded rows
- **LIKE query on name**: `%name%` pattern scan is non-indexed and slow at scale
- **Cross-database join**: Joining eklavya, platform, and dronacharya in a single query — no guarantee indexes exist on FK columns across services

---

## Technical Issues

| Priority | Issue |
|----------|-------|
| Medium | `studentId` param accepted but filtering logic unclear in this spec — may conflict with `teacherId` filter |
| Medium | No max `pageCounter` or `pageSize` limit |
| Low | No auth beyond API Key — no JWT validation in this V1 spec |

---

## Test Scenarios

1. Fetch all students for a valid `teacherId` — verify count and fields
2. Filter `type=ACTIVE` — verify `totalBookedClass > totalCompletedClass + totalPenalties`
3. Filter `type=PAST` — inverse condition
4. Filter by `studentName` partial match — case sensitivity check
5. Pagination with `pageCounter` — verify offset behavior
6. Missing `teacherId` — should it return all students or 400?
7. Invalid `type` value — verify 400 response
8. Large teacher with 1000+ students — measure response time
