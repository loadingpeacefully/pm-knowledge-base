---
endpoint: POST /v1/student/details/bulk
service: eklavya
source_id: 846d377a-7ee6-47bb-8a7d-c82093440a18
original_source_name: bulk
controller: controllers/students.js:109
service_file: services/students.js:1610
router_file: routers/students.js:76-82
auth: API Key (strict)
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/student/details/bulk

## Summary

Fetches comprehensive student details in bulk by providing student IDs, with optional filtering by country and language. Returns full student objects including parent, profile, language mappings, and optionally class balances.

**Category:** Internal API
**Owner/Team:** Student Management Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/student/details/bulk`
**Authentication:** API Key required (`X-API-Key` header)

### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `X-API-Key` | Yes | Strict API key validation via `apiKeyMiddleware` |
| `Content-Type` | Yes | `application/json` |

### Request Body

**Validation source:** `validators/student.js:9-18`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentIds` | array[integer] | Yes | Student IDs to fetch; minimum 1 element |
| `countryIds` | array[integer] | No | Filter students by parent country IDs |
| `languageIds` | array[integer] | No | Filter students by language preference IDs |
| `studentClassBalance` | boolean | No | Include student class balance records |

```json
{
  "studentIds": [123, 456, 789],
  "countryIds": [1, 2],
  "languageIds": [1, 3],
  "studentClassBalance": true
}
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "John Doe",
      "grade": 8,
      "parent_id": 456,
      "lead_source": "organic",
      "has_demo": true,
      "referral_code": "ST123ABC",
      "gems": 250,
      "active": 1,
      "StudentProfile": { "student_id": 123, "gender": "Male", "dob": "2015-06-20" },
      "Parent": { "id": 456, "name": "Jane Doe", "email": "jane.doe@example.com", "country_id": 1 },
      "StudentLanguageMappings": [{ "languageId": 1, "preferrence": 5 }],
      "StudentClassBalances": [{ "id": 789, "total_paid_class": 20, "total_completed_class": 12 }]
    }
  ],
  "message": "students fetched successfully."
}
```

**Empty result (200):**
```json
{ "success": false, "data": [], "message": "students fetched successfully." }
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "studentIds should be array with max size 200", "error": "ValidationError" }
```

**Auth error (401):**
```json
{ "success": false, "data": null, "message": "Access Denied <> API KEY required.", "error": "AuthorizationError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success — students found and returned |
| 400 | Bad request — validation failed |
| 401 | Unauthorized — missing or invalid API key |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:109-127`)

1. Extract `studentIds`, `countryIds`, `languageIds`, `studentClassBalance` from request body
2. Call `StudentsService.getStudentsViaStudentIds()` with all parameters
3. Format response via `ApiResponse` wrapper
4. Return JSON

### Service (`services/students.js:1610-1669`)

**Dynamic Query Building:**

1. **Initialize query components** — empty order array, parent include with optional country filter
2. **Build include array dynamically:**
   - `StudentProfile`: always included (LEFT JOIN)
   - `Parent`: always included as required (INNER JOIN); apply `WHERE country_id IN (...)` if `countryIds` provided
   - `StudentLanguageMapping`: included only if `languageInclude` is true; applied as INNER JOIN if `languageIds` provided
   - `StudentClassBalance`: included only if `studentClassBalance === true`
3. **Language ordering:** if language mappings included, ORDER BY `preferrence DESC`, then `id DESC`
4. **Execute:** `Student.findAll({ where: { id: studentIds }, include: [...], order: [...] })`
5. **Return:** raw Sequelize objects with all related data; no post-processing

---

## Microservice Dependencies

**None.** `getStudentsViaStudentIds` is a database-only method. No calls to Platform, Paathshala, Tryouts, or any external service.

---

## Database & SQL Analysis

### Sequelize Query (`services/students.js:1659-1663`)

```js
Student.findAll({
  where: { id: studentIds },
  include: [
    { model: StudentProfile },
    { required: true, model: Parent, where: countryIds ? { countryId: countryIds } : undefined },
    { required: languageIds ? true : false, model: StudentLanguageMapping,
      attributes: ["languageId", "preferrence"],
      where: languageIds ? { languageId: languageIds } : undefined },
    { model: StudentClassBalance, required: false }
  ],
  order: languageInclude ? [[StudentLanguageMapping, "preferrence", "DESC"], [StudentLanguageMapping, "id", "DESC"]] : []
})
```

### Tables Accessed (conditional)

| Table | Join Type | Condition |
|-------|-----------|-----------|
| `students` | PRIMARY | always |
| `student_profiles` | LEFT JOIN | always |
| `parents` | INNER JOIN | always; conditional WHERE on `country_id` |
| `student_language_mappings` | LEFT/INNER JOIN | conditional on `languageIds` |
| `student_class_balances` | LEFT JOIN | conditional on `studentClassBalance` flag |

### Equivalent SQL (full filters)

```sql
SELECT s.*, sp.*, p.*, slm.languageId, slm.preferrence, scb.*
FROM students s
LEFT JOIN student_profiles sp ON s.id = sp.student_id
INNER JOIN parents p ON s.parent_id = p.id AND p.country_id IN (1, 2)
INNER JOIN student_language_mappings slm ON s.id = slm.student_id AND slm.language_id IN (1, 3)
LEFT JOIN student_class_balances scb ON s.id = scb.student_id
WHERE s.id IN (123, 456, 789)
ORDER BY slm.preferrence DESC, slm.id DESC;
```

### Recommended Indexes

```sql
CREATE INDEX idx_students_id_active ON students(id, active);
CREATE INDEX idx_parents_country_id ON parents(country_id);
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_student_language_mappings_student_lang ON student_language_mappings(student_id, language_id);
CREATE INDEX idx_student_language_mappings_pref ON student_language_mappings(student_id, preferrence DESC);
CREATE INDEX idx_student_class_balances_student_id ON student_class_balances(student_id);
CREATE INDEX idx_student_profiles_student_id ON student_profiles(student_id);
```

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Validator error message says "max size 200" but no actual limit is enforced | `validators/student.js:11-12` | Large arrays can trigger expensive queries |
| 2 | Multiple conditional joins create unpredictable query execution plans | `services/students.js:1652-1662` | Inconsistent response times |
| 3 | ORDER BY on optional joined table when language mappings are sparse | `services/students.js:1639-1642` | Query performance degradation |

### Low Priority

| # | Issue | Impact |
|---|-------|--------|
| 4 | No request payload size validation | Potential memory issues with very large arrays |
| 5 | Country filter changes WHERE clause; language filter changes join type — inconsistent behavior | Confusing query semantics |

---

## Test Scenarios

### Functional
- Basic request with `studentIds` only
- With `countryIds` filter
- With `languageIds` filter
- With both country and language filters
- With `studentClassBalance: true`
- With `studentClassBalance: false`
- Non-existent student IDs (empty result)
- Single vs large batch (100+ IDs)

### Validation
- Missing `studentIds`
- Empty `studentIds` array
- Non-integer values in `studentIds`
- Invalid `countryIds`/`languageIds` format
- Arrays exceeding 200 elements

### Performance
- Response time at 1, 10, 50, 100, 200 IDs
- Different filter combinations execution plan comparison
- Concurrent bulk requests

### Security
- Missing API key → 401
- Invalid API key → 401
- Large payload injection
- SQL injection via array parameters
