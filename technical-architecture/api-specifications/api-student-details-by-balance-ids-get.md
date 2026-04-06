---
endpoint: POST /v1/student/details/balanceIds
service: eklavya
source_id: a260a6b0-f8a8-4496-939b-5db8c9648e23
original_source_name: balanceIds
controller: controllers/students.js:128
service_file: services/students.js:1670
router_file: routers/students.js:83
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/student/details/balanceIds

## Summary

Reverse lookup: given an array of `StudentClassBalance` IDs, fetches the corresponding student records with full profile, parent, language mappings, and the matching class balance records. Useful for resolving student information from balance context (e.g., scheduling or class management systems that only hold balance IDs).

**Category:** Internal API
**Owner/Team:** Student Management Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/student/details/balanceIds`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Request Body

**No explicit validation middleware.** Accepts raw request body.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentBalanceIds` | array[integer] | Yes | Array of `student_class_balances.id` values |

```json
{ "studentBalanceIds": [123, 456, 789] }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "name": "John Doe",
      "grade": 8,
      "parent_id": 789,
      "referral_code": "ST456DEF",
      "StudentProfile": {
        "student_id": 456, "gender": "Male", "dob": "2015-06-20",
        "school_name": "Central High School", "total_credits": 150, "credits_consumed": 45
      },
      "StudentLanguageMappings": [
        { "languageId": 1, "preferrence": 5 }, { "languageId": 3, "preferrence": 3 }
      ],
      "Parent": { "countryId": 1, "name": "Jane Doe", "tzId": "America/New_York",
                  "email": "jane.doe@example.com", "phone": "+1234567890" },
      "StudentClassBalances": [
        { "id": 123, "student_id": 456, "course_id": 2, "teacher_id": 89,
          "class_type": "online", "total_paid_class": 20, "total_completed_class": 12 }
      ]
    }
  ],
  "message": "students fetched successfully."
}
```

**Empty (200):**
```json
{ "success": false, "data": [], "message": "students fetched successfully." }
```

**Error (500):**
```json
{ "success": false, "data": null, "message": "error in getStudentsViaBalanceIds", "error": "DatabaseError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized |
| 500 | Database error |

---

## Logic Flow

### Controller (`controllers/students.js:128-139`)

1. Extract `studentBalanceIds` array from request body
2. Call `StudentsService.getStudentsViaBalanceIds(studentBalanceIds)`
3. Format via `ApiResponse` wrapper
4. Return JSON

### Service (`services/students.js:1670-1703`)

**Single query with multiple joins:**

1. `Student.findAll()` with includes:
   - `StudentProfile` (LEFT JOIN)
   - `StudentLanguageMapping` (LEFT JOIN, attributes: `["languageId", "preferrence"]`)
   - `Parent` (INNER JOIN, attributes: `["countryId","name","tzId","email","phone"]`)
   - `StudentClassBalance` (INNER JOIN, `where: { id: studentBalanceIds }`)
2. Order by `StudentLanguageMapping.preferrence DESC`, then `StudentLanguageMapping.id DESC`
3. Return complete Sequelize objects — no transformation

**Key:** The filter is on `StudentClassBalance.id IN (...)`, not `Student.id`. This is the reverse-lookup mechanism.

---

## Microservice Dependencies

**None.** Database-only. No external service calls.

---

## Database & SQL Analysis

### Sequelize Query (`services/students.js:1672-1697`)

```js
Student.findAll({
  include: [
    { model: StudentProfile },                                         // LEFT JOIN
    { required: false, model: StudentLanguageMapping,
      attributes: ["languageId", "preferrence"] },                    // LEFT JOIN
    { required: true, model: Parent,
      attributes: ["countryId","name","tzId","email","phone"] },      // INNER JOIN
    { required: true, model: StudentClassBalance,
      where: { id: studentBalanceIds } }                              // INNER JOIN + WHERE id IN (...)
  ],
  order: [
    [StudentLanguageMapping, "preferrence", "DESC"],
    [StudentLanguageMapping, "id", "DESC"]
  ]
})
```

### Equivalent SQL

```sql
SELECT s.*, sp.*,
       slm.languageId, slm.preferrence,
       p.countryId, p.name, p.tzId, p.email, p.phone,
       scb.*
FROM students s
LEFT JOIN student_profiles sp ON s.id = sp.student_id
LEFT JOIN student_language_mappings slm ON s.id = slm.student_id
INNER JOIN parents p ON s.parent_id = p.id
INNER JOIN student_class_balances scb ON s.id = scb.student_id
WHERE scb.id IN (123, 456, 789)
ORDER BY slm.preferrence DESC, slm.id DESC;
```

### Tables Accessed

| Table | Join | Purpose |
|-------|------|---------|
| `students` | PRIMARY | Base entity |
| `student_profiles` | LEFT JOIN | Profile details |
| `student_language_mappings` | LEFT JOIN | Language preferences |
| `parents` | INNER JOIN | Parent info (limited attrs) |
| `student_class_balances` | INNER JOIN | Filter anchor (reverse lookup) |

### Recommended Indexes

```sql
CREATE INDEX idx_student_class_balances_id ON student_class_balances(id);
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_student_profiles_student_id ON student_profiles(student_id);
CREATE INDEX idx_student_language_mappings_student_pref ON student_language_mappings(student_id, preferrence DESC);
CREATE INDEX idx_student_class_balances_student_id ON student_class_balances(student_id);
CREATE INDEX idx_scb_id_student_active ON student_class_balances(id, student_id, active);
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No input validation — no format check on `studentBalanceIds`, no array size limit | `routers/students.js:83` | Injection risk, unbounded queries |
| 2 | No limit clause — unlimited result set if many IDs provided | `services/students.js:1672` | Memory/performance degradation |

### Medium Priority

| # | Issue | Impact |
|---|-------|--------|
| 3 | ORDER BY on optional LEFT JOIN table (language mappings) — expensive when mappings are sparse | Query performance |
| 4 | No handling for non-existent balance IDs — returns empty without validation error | Confusing caller experience |

### Low Priority

| # | Issue |
|---|-------|
| 5 | Full `SELECT *` on `students` and `student_profiles` — unnecessary data transfer |

---

## Test Scenarios

### Functional
- Single balance ID
- Multiple balance IDs (2–10)
- Non-existent balance IDs → empty result
- Mixed valid/invalid IDs

### Performance
- Response time at 1, 10, 50 IDs
- Memory usage with large result sets
- Concurrent requests

### Security
- Authentication enforcement (JWT and API key)
- Invalid request body format
- SQL injection via array elements
- Large payload / oversized array

### Edge Cases
- Balance IDs for inactive students
- Balance IDs with no associated parent record (INNER JOIN fails → excluded)
- Students with no language preferences
- Duplicate IDs in request array
