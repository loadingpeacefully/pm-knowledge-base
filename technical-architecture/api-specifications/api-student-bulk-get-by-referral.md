---
endpoint: POST /v1/student
service: eklavya
source_id: 3f04ceca-5a9f-480d-96c7-cd4d91365c03
original_source_name: student (bulk by referral codes)
controller: controllers/students.js:95
service_file: services/students.js:1419
router_file: routers/students.js:70
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/student

## Summary

Retrieves student records in bulk by accepting an array of referral codes. Uses a single `SELECT ... WHERE referral_code IN (...)` query with eager loading of `StudentProfile` (left join, optional) and `Parent` (inner join, required). No authentication required. Sequelize default scope filters to active students only. Well-optimized endpoint with no critical issues — primary concerns are the absence of an input array size limit and no way to identify which referral codes were not found.

**Note:** This is a separate endpoint from `GET /v1/student` (single/flexible lookup). Both share the same path base but differ in HTTP method and lookup strategy.

**Category:** Student Management API — Bulk Student Lookup
**Owner/Team:** Student Management Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/student`
**Authentication:** None

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `referralCodes` | string[] | Yes | Array of referral codes (non-empty array required) |

### Request Examples

```json
// Single lookup
{ "referralCodes": ["BRIGHT_STU_001"] }

// Bulk lookup
{ "referralCodes": ["BRIGHT_STU_001", "BRIGHT_STU_002", "BRIGHT_STU_003"] }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 123, "name": "John Smith Jr", "parentId": 456,
      "referralCode": "BRIGHT_STU_001", "courseId": 5, "batchId": 12,
      "grade": 3, "source": "organic", "gems": 150, "leadSource": "DEFAULT",
      "hasDemo": true,
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-11-20T14:25:00.000Z",
      "StudentProfile": {
        "id": 789, "studentId": 123,
        "profilePicture": "https://cdn.brightchamps.com/profiles/student_123.jpg",
        "created_at": "2024-01-15T10:35:00.000Z"
      },
      "Parent": {
        "id": 456, "name": "John Smith Sr",
        "email": "parent@example.com", "phone": "+1234567890",
        "countryId": 1, "status": "active"
      }
    }
  ],
  "message": "students fetched successfully."
}
```

**No students found (200):**
```json
{ "success": true, "data": [], "message": "students fetched successfully." }
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "Validation failed", "errors": [{ "field": "referralCodes", "message": "You must provide referralCodes" }] }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (empty array if none found) |
| 400 | Validation error — missing or empty `referralCodes` |
| 500 | Database error |

---

## Logic Flow

### Controller (`controllers/students.js:95-108`)

1. Extract `referralCodes` from request body
2. Call `StudentsService.getBulkStudentsByReferralCodes(referralCodes)`
3. Wrap in `ApiResponse` and return

### Service (`services/students.js:1419-1445`)

1. Build filter: `{ referralCode: { [Op.in]: referralCodes } }`
2. Execute `Student.findAll({ where: filter, include: [StudentProfile (LEFT), Parent (INNER)] })`
3. Sequelize default scope applies `active = true` automatically
4. Return all matching records

---

## Microservice Dependencies

**None.** Zero external HTTP calls. Database-only.

---

## Database & SQL Analysis

### Primary Query

```sql
SELECT students.*, student_profiles.*, parents.*
FROM students
LEFT JOIN student_profiles ON students.id = student_profiles.student_id
INNER JOIN parents ON students.parent_id = parents.id
WHERE students.referral_code IN ('BRIGHT_STU_001', 'BRIGHT_STU_002', 'BRIGHT_STU_003')
  AND students.active = true;
```

### Tables Accessed

| Table | Join | Purpose |
|-------|------|---------|
| `students` | PRIMARY | Referral code lookup with `WHERE referral_code IN (...)` |
| `student_profiles` | LEFT JOIN | Optional profile data (may be null) |
| `parents` | INNER JOIN | Required — student must have parent |

### Index Usage

- `students.referral_code` — unique index (primary lookup, very efficient)
- `students.parent_id` — foreign key index for join
- `students.active` — Sequelize default scope filter

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No maximum array size limit — very large arrays cause query timeouts or memory pressure | Validator (only checks non-empty) | Performance degradation with 100+ codes |
| 2 | No response metadata for missing codes — client cannot tell which referral codes were not found | Service response | Poor DX for partial hits |
| 3 | No referral code format validation — arbitrary strings pass to DB | Validator | Minor injection risk (mitigated by Sequelize ORM) |

### Low Priority

| # | Issue |
|---|-------|
| 4 | No authentication — referral codes can be brute-forced to extract student/parent data |
| 5 | Generic `DatabaseError` without specific context on failure |
| 6 | No audit logging of bulk lookup requests |

---

## Test Scenarios

### Functional
- Single valid referral code → 1 student with profile and parent
- Multiple valid codes → all students returned
- Mix of valid and invalid codes → only found students returned
- All invalid codes → empty array
- Duplicate codes in array → 1 record returned per student
- Student with no `StudentProfile` → `StudentProfile: null`

### Validation
- Missing `referralCodes` field → 400
- Empty array `[]` → 400
- Non-array value → 400
- Null values in array

### Performance
- 50-code batch → response time < 200ms
- 200-code batch → query behavior (no limit currently enforced)

### Security
- SQL injection attempt in referral code string (mitigated by ORM)
- Bulk enumeration of student data via referral code guessing
- Response includes parent PII (email, phone) — no auth required

### Edge Cases
- Referral codes with special characters
- Mixed case (case sensitivity in MySQL)
- Codes referencing soft-deleted (inactive) students → not returned
- Very long referral code strings
