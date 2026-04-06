---
endpoint: GET /v1/student/filter
service: eklavya
source_id: b890d6a5-68c4-455a-a111-9e59e5b3ae99
original_source_name: filter
controller: controllers/students.js:337
service_file: services/students.js:2054
router_file: routers/students.js:133
auth: API Key required
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/student/filter

## Summary

Searches students by name or parent information (name, email, phone). Uses a two-stage search: first by student name, then by parent info if the first stage returns fewer than 1000 results. Returns only student IDs.

**Category:** Internal API
**Owner/Team:** Student Management Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/student/filter`
**Authentication:** API Key required (`X-API-Key` header)

### Query Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filter` | string | Yes | Search term (student name or parent name/email/phone) |

**Note:** No explicit validator — relies on API key middleware only. The `filter` parameter has no length or format validation.

### Request Examples

```
GET /v1/student/filter?filter=John
GET /v1/student/filter?filter=Jane
GET /v1/student/filter?filter=jane@example.com
GET /v1/student/filter?filter=+1234567890
GET /v1/student/filter?filter=Joh
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [{ "id": 123 }, { "id": 456 }, { "id": 789 }],
  "message": "students fetched successfully."
}
```

**Empty result (200):**
```json
{ "success": false, "data": [], "message": "students fetched successfully." }
```

**Unauthorized (401):**
```json
{ "success": false, "data": null, "message": "API key required", "error": "Unauthorized" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized — missing or invalid API key |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:337-350`)

1. Extract `filter` from query string
2. Call `StudentsService.getStudentsFromFilters(filter)`
3. Format via `ApiResponse` wrapper
4. Return JSON with student ID array

### Service (`services/students.js:2054-2100`)

**Two-stage search algorithm:**

**Stage 1 — Student name search:**
1. `Student.findAll({ where: { name: { [Op.like]: `${filter}%` } }, attributes: ["id"], limit: 1000, raw: true })`
2. Returns up to 1000 matching student IDs

**Stage 2 — Parent information search (conditional):**
3. Executes only if Stage 1 returns fewer than 1000 results
4. Searches via parent join with `Op.or`: `name LIKE 'filter%'`, `email LIKE 'filter%'`, `phone = filter` (exact)
5. Uses in-memory mapping object to deduplicate merged results

**Key algorithm properties:**
- Prefix matching (`LIKE 'filter%'`) for names and emails
- Exact match (`=`) for phone numbers
- Hard limit of 1000 per stage
- In-memory deduplication across both stages
- `raw: true` on both queries for performance (no Sequelize object instantiation)

---

## Microservice Dependencies

**None.** `getStudentsFromFilters` is database-only. No calls to any external service.

---

## Database & SQL Analysis

### Stage 1 Query

```js
Student.findAll({
  where: { name: { [Op.like]: `${filter}%` } },
  attributes: ["id"],
  limit: 1000,
  raw: true
})
```

```sql
SELECT id FROM students
WHERE name LIKE 'John%'
LIMIT 1000;
```

### Stage 2 Query

```js
Student.findAll({
  include: [{
    required: true,
    model: Parent,
    attributes: [],
    where: {
      [Op.or]: [
        { name: { [Op.like]: `${filter}%` } },
        { email: { [Op.like]: `${filter}%` } },
        { phone: filter }
      ]
    }
  }],
  attributes: ["id"],
  limit: 1000,
  raw: true
})
```

```sql
SELECT s.id
FROM students s
INNER JOIN parents p ON s.parent_id = p.id
WHERE (p.name LIKE 'Jane%'
   OR p.email LIKE 'jane%'
   OR p.phone = '+1234567890')
LIMIT 1000;
```

### Tables Accessed

| Table | Join Type | Condition |
|-------|-----------|-----------|
| `students` | PRIMARY | Stage 1 and Stage 2 |
| `parents` | INNER JOIN | Stage 2 only |

### Recommended Indexes

```sql
CREATE INDEX idx_students_name_prefix ON students(name(10));
CREATE INDEX idx_parents_name_prefix ON parents(name(10));
CREATE INDEX idx_parents_email_prefix ON parents(email(20));
CREATE INDEX idx_parents_phone ON parents(phone);
CREATE INDEX idx_students_parent_id ON students(parent_id);
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Two separate queries when a single UNION query would suffice | `services/students.js:2057-2090` | Unnecessary DB round-trip |
| 2 | No input validation on `filter` — no length, format, or character constraints | `controllers/students.js:339` | Expensive queries, injection risk |
| 3 | Basic `LIKE` pattern matching without full-text indexes | `services/students.js:2059-2082` | Poor search performance on large datasets |

### Medium Priority

| # | Issue | Location |
|---|-------|----------|
| 4 | Hard-coded 1000 limit with no pagination | `services/students.js:2056` |
| 5 | In-memory deduplication scales with result size | `services/students.js:2068-2071` |

---

## Optimization Recommendations

**Immediate (Week 1):**
- Add input validation: min 2 chars, max 50 chars, alphanumeric + common email/phone characters
- Combine into single UNION query: `SELECT DISTINCT s.id FROM students s LEFT JOIN parents p ... WHERE s.name LIKE ? OR p.name LIKE ? OR p.email LIKE ? OR p.phone = ? LIMIT 1000`

**Long-term:**
- Add full-text search indexes: `ALTER TABLE students ADD FULLTEXT(name)` and `ALTER TABLE parents ADD FULLTEXT(name, email)`
- Add pagination parameters (`limit`, `offset`)
- Cache common search queries (5-minute TTL)

---

## Test Scenarios

### Functional
- Search by student name (exact and prefix)
- Search by parent name, email, phone
- Empty `filter` parameter
- Case sensitivity behavior
- Special character handling

### Performance
- Large result sets approaching 1000 limit
- Query time with varying filter lengths
- Concurrent searches under load

### Security
- API key enforcement
- SQL injection via `filter` value
- Large input string handling (DoS prevention)

### Edge Cases
- 1-2 character filters (very broad match)
- Numeric-only filters
- Phone number format variations
- Filters that exactly hit the 1000 limit in Stage 1 (Stage 2 skipped)
