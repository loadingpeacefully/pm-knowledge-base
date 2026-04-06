---
endpoint: GET /v1/student-class-balance
service: eklavya
source_id: f9c7f5a2-e3c1-4ba8-9a03-d11c83d1af9e
original_source_name: student-class-balance
controller: controllers/class-balance.js:32
service_file: services/class-balance.js:77
router_file: routers/class-balance.js:27-32
auth: None (public endpoint)
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/student-class-balance

## Summary

Retrieves student class balance details with optional enrichment for student/parent data, teacher mappings, and language preferences. Supports lookup by student ID (with optional course filter) or by direct balance record ID. Class type filtering supports multiple values.

**Category:** Internal API
**Owner/Team:** Academic Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/student-class-balance`
**Authentication:** None (public endpoint)

### Query Parameters

**Validation source:** `validators/class-balance.js:4-25`

**One of the following is required:**

| Option | Field | Type | Description |
|--------|-------|------|-------------|
| Option 1 | `studentId` | integer | Student ID to fetch balance for |
| Option 2 | `id` | integer | Direct balance record ID |

**Optional:**

| Field | Type | Description |
|-------|------|-------------|
| `courseId` | integer | Filter by specific course (used with `studentId`) |
| `isStudentDetails` | boolean | Include student and parent details |
| `classType` | string or array | Filter by class type(s) — comma-separated string or array |
| `mappedTeachers` | boolean | Include teacher mapping information |
| `studentLanguageMappings` | boolean | Include student language preferences |

**Valid `classType` values:** `online` (default), `offline`, `online-group`, `online-master-class`, `offline-master-class`, `diy`

### Request Examples

```
GET /v1/student-class-balance?studentId=123
GET /v1/student-class-balance?studentId=123&courseId=5
GET /v1/student-class-balance?studentId=123&isStudentDetails=true
GET /v1/student-class-balance?id=789
GET /v1/student-class-balance?studentId=123&classType=online,offline
GET /v1/student-class-balance?studentId=123&courseId=5&isStudentDetails=true&mappedTeachers=true&studentLanguageMappings=true
```

### Response Format

**Basic (200):**
```json
{
  "success": true,
  "data": [
    { "id": 789, "student_id": 123, "course_id": 5, "remaining_classes": 15,
      "teacher_id": 101, "class_type": "online", "active": true }
  ],
  "message": "details fetched successfully."
}
```

**With `isStudentDetails=true`:**
```json
{
  "data": [{
    "id": 789,
    "Student": {
      "id": 123, "name": "John Doe", "grade": 5,
      "Parent": { "id": 456, "name": "Jane Doe", "email": "jane@example.com" },
      "StudentLanguageMappings": [{ "id": 1, "student_id": 123, "language_id": 10 }]
    }
  }]
}
```

**With `mappedTeachers=true`:**
```json
{
  "data": [{
    "id": 789,
    "StudentTeacherMappings": [{ "id": 1, "teacherId": 101, "isPrimary": true }]
  }]
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request — invalid parameters |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/class-balance.js:32-57`)

1. Extract `studentId`, `courseId`, `id`, `classType`, `mappedTeachers`, `studentLanguageMappings` from query params
2. Convert `classType` comma-separated string to array if needed
3. Call `ClassBalanceService.getClassBalanceDetails()` with all params
4. Format via `ApiResponse` wrapper
5. Return JSON

### Service (`services/class-balance.js:77-118`)

1. **Build filter object:**
   - Default: `{ student_id: studentId, class_type: classType }`
   - Add `course_id` if provided
   - If `id` provided: override with `{ id, classType: CLASS_TYPES.all }` (no class type filter)
2. **Build include array dynamically:**
   - If `isStudentDetails=true`: include `Student` → `Parent`
   - If `studentLanguageMappings=true`: also add `StudentLanguageMapping` nested inside `Student`
   - If `mappedTeachers=true`: include `StudentTeacherMapping` with `active` filter
3. **Execute:** `StudentClassBalance.findAll({ where: filter, include: includeFilter })`
4. Return raw results

---

## Microservice Dependencies

**None.** Database-only endpoint with no external service calls.

---

## Database & SQL Analysis

### Primary Query (`services/class-balance.js:60-66`)

```js
const data = await this.db.StudentClassBalance.findAll({
  where: filter,
  include: extra?.includeFilter,
  limit: extra?.limit,
  offset: extra?.offset,
  attributes: extra?.attributes
})
```

### Equivalent SQL — Basic

```sql
SELECT * FROM student_class_balances
WHERE student_id = ?
AND class_type = 'online'
AND (course_id = ? OR ? IS NULL);
```

### Equivalent SQL — With Student Details

```sql
SELECT scb.*, s.id, s.name, s.grade, p.id, p.name, p.email, p.phone
FROM student_class_balances scb
INNER JOIN students s ON scb.student_id = s.id
INNER JOIN parents p ON s.parent_id = p.id
WHERE scb.student_id = ? AND scb.class_type = ?;
```

### Tables Accessed (conditional)

| Table | Join | Condition |
|-------|------|-----------|
| `student_class_balances` | PRIMARY | always |
| `students` | INNER JOIN | `isStudentDetails=true` |
| `parents` | INNER JOIN | `isStudentDetails=true` |
| `student_language_mappings` | LEFT JOIN | `studentLanguageMappings=true` |
| `student_teacher_mappings` | LEFT JOIN | `mappedTeachers=true` |

### Recommended Indexes

```sql
CREATE INDEX idx_scb_student_course_type ON student_class_balances(student_id, course_id, class_type);
CREATE INDEX idx_scb_id ON student_class_balances(id);
CREATE INDEX idx_stm_active ON student_teacher_mappings(student_id, active, isPrimary);
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No pagination — returns all matching records for a student | `validators/class-balance.js:4-25` | Memory/performance issues on large datasets |
| 2 | `SELECT *` pattern — no explicit attribute selection | `services/class-balance.js:60-66` | Unnecessary data transfer |

### Medium Priority

| # | Issue | Location |
|---|-------|----------|
| 3 | Class type conversion logic in controller (should be in validator) | `controllers/class-balance.js:36-38` |
| 4 | Dynamic include building makes query performance unpredictable with multiple flags | `services/class-balance.js:92-116` |

---

## Test Scenarios

### Functional
- Balance by `studentId` only
- Balance by `id` directly
- `courseId` filter combined with `studentId`
- Single `classType` filter
- Multiple `classType` values (comma-separated)
- `isStudentDetails=true`
- `mappedTeachers=true`
- `studentLanguageMappings=true`
- All optional flags combined

### Edge Cases
- Non-existent `studentId`
- Invalid `courseId`
- Invalid `classType` string
- Missing both `studentId` and `id`
- Student with no teacher mappings

### Error Scenarios
- Database connection failure
- Invalid parameter types (string for integer fields)
- Malformed `classType` array
