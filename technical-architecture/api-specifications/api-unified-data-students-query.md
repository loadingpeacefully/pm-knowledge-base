---
endpoint: POST /v1/unified-data/students
service: eklavya
source_id: 33da7b0c-3388-4c7a-9a2e-ed3acad5fe56
original_source_name: students
controller: controllers/unified-data.js:10
service_file: services/unified-data.js:153
router_file: routers/unified-data.js:25-31
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/unified-data/students

## Summary

A dynamic database query API for the `students` table. Callers send a Sequelize-compatible query structure in the request body and the service translates it directly into a `findAll` call. Supports arbitrary WHERE conditions, nested includes, attribute selection, ordering, and pagination. Functions as a flexible pass-through query layer over the Student ORM model.

**Category:** Internal API
**Owner/Team:** Data Integration Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/unified-data/students`
**Authentication:** JWT token (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Request Body

**Validation source:** `validators/unified-data.js:2-4`

| Field | Required | Description |
|-------|----------|-------------|
| `relations.Student` | Yes | Must exist; contains the full query specification |

```json
{
  "relations": {
    "Student": {
      "where": { ... },
      "include": [ ... ],
      "attributes": [ ... ],
      "order": [ ... ],
      "limit": 10,
      "offset": 0,
      "subQuery": false
    }
  }
}
```

### Supported Operators in `where`

| JSON key | Sequelize Op | Example |
|----------|-------------|---------|
| `in` | `Op.in` | `"id": { "in": [1,2,3] }` |
| `like` | `Op.like` | `"name": { "like": "%John%" }` |
| `gt` / `gte` | `Op.gt/gte` | `"grade": { "gte": 5 }` |
| `lt` / `lte` | `Op.lt/lte` | — |
| `between` | `Op.between` | `"created_at": { "between": ["2024-01-01","2024-12-31"] }` |
| `notNull` | `Op.not: null` | `"email": { "notNull": true }` |

Advanced features: `Sequelize.literal()`, `Sequelize.col()`, `Sequelize.fn()`, `Sequelize.cast()`, `Sequelize.where()`

### Request Examples

**Basic ID lookup:**
```json
{
  "relations": {
    "Student": { "where": { "id": { "in": [123, 456, 789] } } }
  }
}
```

**With parent + profile:**
```json
{
  "relations": {
    "Student": {
      "where": { "grade": 5 },
      "include": ["Parent", "StudentProfile"],
      "limit": 20,
      "offset": 0
    }
  }
}
```

**Complex nested query:**
```json
{
  "relations": {
    "Student": {
      "where": { "active": true, "grade": { "gte": 5 } },
      "include": [
        { "entity": "Parent", "where": { "country_id": 1 }, "attributes": ["id","name","email"] },
        { "entity": "StudentClassBalance", "where": { "remaining_classes": { "gt": 0 } }, "include": ["Course"] }
      ],
      "attributes": ["id","name","grade","gems"],
      "order": [["created_at","DESC"]],
      "limit": 50
    }
  }
}
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    { "id": 123, "name": "John Doe", "grade": 5, "gems": 100,
      "Parent": { "id": 456, "name": "Jane Doe", "email": "jane@example.com" },
      "StudentProfile": { "student_id": 123, "school": "ABC School" } }
  ],
  "message": "Data fetched successfully."
}
```

**Empty (200):**
```json
{ "success": false, "data": [], "message": "Data fetched successfully." }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request — invalid relations structure |
| 401 | Unauthorized — auth missing or invalid |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/unified-data.js:10-23`)

1. Extract entire request body as `query` object
2. Call `unifiedDataService.getUnifiedData({ query })`
3. Format via `ApiResponse` wrapper
4. Return JSON

### Service (`services/unified-data.js:153-176`)

1. Call `_buildInclude(query, this.db)` to parse relations into Sequelize config (handles operator mapping, nested includes, literals, etc.)
2. Extract primary model name from `relations` object key (`"Student"`)
3. Extract model config (`where`, `include`, `attributes`, `order`, `limit`, `offset`, `subQuery`)
4. Execute `this.db[modelName].findAll({ where, include, attributes, order, limit, offset, subQuery })`
   - Default `limit: 10`, default `offset: 0`
5. Return raw results

### Query Builder (`services/unified-data.js:18-151`)

Complex operator parser that:
- Maps JSON operator keys to `Sequelize.Op.*` symbols
- Supports nested relations with their own where/attributes
- Handles `Sequelize.literal`, `col`, `fn`, `cast`, `where`

---

## Microservice Dependencies

**None.** This is a database-only endpoint. No external service calls.

---

## Database & SQL Analysis

### Tables Accessed

Dynamically determined by the `relations.Student.include` array. Potentially any table accessible via Sequelize models.

### Example Generated SQL

```sql
-- Simple query
SELECT * FROM students WHERE id IN (123, 456, 789);

-- With includes and filters
SELECT s.*, p.id, p.name, p.email
FROM students s
INNER JOIN parents p ON s.parent_id = p.id
WHERE s.grade = 5 AND p.country_id = 1
ORDER BY s.created_at DESC
LIMIT 20 OFFSET 0;
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Unrestricted database access — callers can query any model/field/join without whitelist | `services/unified-data.js:153-176` | Data exposure, potential DoS |
| 2 | Default limit is 10 but callers can override to any value; no maximum enforced | `services/unified-data.js:139` | Unbounded result sets |
| 3 | Complex operator parsing logic (~130 lines) is difficult to audit and maintain | `services/unified-data.js:55-129` | Parsing bugs, injection surface |

### Medium Priority

| # | Issue | Location |
|---|-------|----------|
| 4 | Generic error wrapping hides specific DB errors | `services/unified-data.js:171-175` |
| 5 | Only validates `relations.Student` exists; no structural validation on nested query objects | `validators/unified-data.js:2-4` |

---

## Test Scenarios

### Functional
- Basic query by student IDs
- Student with single relation (Parent)
- Student with multiple relations and nested includes
- Operator tests: `in`, `like`, `gt`, `gte`, `between`, `notNull`
- Attribute selection
- Ordering and pagination (`limit`, `offset`)

### Security
- Unauthorized access (missing token and API key)
- Attempt to query non-student models via relations key
- Large `limit` value injection
- Malformed operator structures (should not 500)

### Performance
- Large result sets (high `limit`)
- Complex multi-level includes
- Concurrent query load

### Error Scenarios
- Invalid relation structures
- Non-existent model references in `include`
- Database connection failures
- Malformed Sequelize operator keys
