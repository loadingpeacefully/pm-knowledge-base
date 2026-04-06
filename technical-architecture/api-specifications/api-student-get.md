---
endpoint: GET /v1/student
service: eklavya
source_id: b76ea6cf-fa89-4315-b2cc-3f63472524ef
original_source_name: student (GET)
controller: controllers/students.js:65
service_file: services/students.js:1420
router_file: routers/students.js:69
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/student

## Summary

Retrieves comprehensive student information with flexible lookup by `studentId`, `referralCode`, or `objectId`. Supports modular data enrichment via boolean flags for class balance, package info, and student profile. When `objectId` is provided, resolves to a `studentId` via an external Tryouts service call.

**Category:** Core API — Student Information Retrieval
**Owner/Team:** Student Management / Core Platform Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/student`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Query Parameters

**Validation source:** `validators/student.js:247-260`

**One of the following is required:**

| Field | Type | Description |
|-------|------|-------------|
| `studentId` | integer (≥1) | Direct student ID lookup |
| `referralCode` | string | Referral code lookup |
| `objectId` | string | Demo booking object ID — resolved to `studentId` via Tryouts service |

**Optional enrichment flags:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `isStudentClassBalance` | boolean | false | Include `StudentClassBalance` records |
| `isPackageInfo` | boolean | false | Include active `PackageSaleInitiator` records |
| `isStudentProfile` | boolean | true | Include `StudentProfile` data |

### Request Examples

```
GET /v1/student?studentId=12345
GET /v1/student?referralCode=ST123456
GET /v1/student?objectId=demo_789012
GET /v1/student?studentId=12345&isStudentClassBalance=true&isPackageInfo=true&isStudentProfile=true
GET /v1/student?studentId=12345&isStudentProfile=false
```

### Response Format

**Success (200) — full response:**
```json
{
  "success": true,
  "data": {
    "id": 12345,
    "name": "Emma Johnson",
    "grade": 5,
    "gems": 150,
    "active": 1,
    "referralCode": "ST123456",
    "languageId": 1,
    "Parent": {
      "id": 54321,
      "name": "Sarah Johnson",
      "email": "sarah.johnson@email.com",
      "phone": "+12345678901",
      "countryId": 1,
      "tzId": 12
    },
    "StudentProfile": {
      "id": 67890,
      "studentId": 12345,
      "totalCredits": 24,
      "creditsConsumed": 8,
      "profilePicture": "https://example.com/profile.jpg",
      "gender": "Female",
      "joinedDate": "2024-10-16T10:00:00.000Z",
      "misc": "{\"isOnboarded\":true}",
      "subscriptionEndsAt": "2024-12-15T23:59:59.000Z"
    },
    "StudentClassBalances": [
      { "id": 98765, "courseId": 2, "teacherId": 789, "totalBookedClass": 24,
        "totalCompletedClass": 8, "classType": "online", "active": 1 }
    ],
    "PackageSaleInitiators": [
      { "id": 13579, "studentId": 12345, "packageId": 456, "status": "active",
        "classesSold": 24, "sourceType": "demo_conversion" }
    ]
  },
  "message": "student fetched successfully."
}
```

**Not found (200):**
```json
{ "success": false, "data": null, "message": "student fetched successfully." }
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "You must provide studentId", "error": "ValidationError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (or not found with `success: false`) |
| 400 | Bad request — missing required lookup param |
| 401 | Unauthorized |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:65-92`)

1. Extract `objectId`, `studentId`, `referralCode`, enrichment flags from query params
2. Call `StudentsService.getStudentInfo()` with all params
3. Format via `ApiResponse` wrapper
4. Return JSON

### Service (`services/students.js:1420-1470`)

**Lookup priority:**

1. **objectId** → call Tryouts service `getOnlyBookingInfoByObjectId({ objectId })` → extract `studentId`
2. **referralCode** → `filter = { referralCode }`
3. **studentId** → `filter = { id: studentId }`

**Dynamic include strategy:**

- `Parent`: always included (required INNER JOIN)
- `StudentClassBalance`: added if `isStudentClassBalance=true`
- `PackageSaleInitiator`: added with `where: { status: 'active' }` if `isPackageInfo=true`
- `StudentProfile`: added if `isStudentProfile=true` (default: true)

**Query:** `Student.findOne({ where: filter, include: includedModels })`

Returns `null` if student not found.

---

## Microservice Dependencies

| Service | Call | Trigger | Auth |
|---------|------|---------|------|
| Tryouts | `getOnlyBookingInfoByObjectId({ objectId })` | Only when `objectId` provided | `X-API-KEY: TRYOUTS_API_KEY` |

**Error handling:** Tryouts failures propagate as `DependencyError`. If Tryouts is unavailable and `objectId` is the only lookup method, the request will fail.

---

## Database & SQL Analysis

### Query Structure

```js
await this.db.Student.findOne({
  where: filter,  // { id: studentId } OR { referralCode }
  include: includedModels  // Dynamic based on flags
})
```

### Equivalent SQL (all flags enabled)

```sql
SELECT s.*, p.*,
       scb.*,
       psi.*,
       sp.*
FROM students s
JOIN parents p ON s.parent_id = p.id
LEFT JOIN student_class_balances scb ON s.id = scb.student_id
LEFT JOIN package_sale_initiators psi ON s.id = psi.student_id AND psi.status = 'active'
LEFT JOIN student_profiles sp ON s.id = sp.student_id
WHERE s.id = ? OR s.referral_code = ?;
```

### Tables Accessed (conditional)

| Table | Join | Condition |
|-------|------|-----------|
| `students` | PRIMARY | always |
| `parents` | INNER JOIN | always |
| `student_class_balances` | LEFT JOIN | `isStudentClassBalance=true` |
| `package_sale_initiators` | LEFT JOIN | `isPackageInfo=true`, filtered to `status='active'` |
| `student_profiles` | LEFT JOIN | `isStudentProfile=true` (default) |

### Recommended Indexes

```sql
CREATE INDEX idx_students_id ON students(id);
CREATE INDEX idx_students_referral_code ON students(referral_code);
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_student_class_balance_student_id ON student_class_balances(student_id);
CREATE INDEX idx_package_sale_initiators_student_status ON package_sale_initiators(student_id, status);
CREATE INDEX idx_student_profiles_student_id ON student_profiles(student_id);
```

---

## Technical Issues

### Low Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | `objectId → studentId` resolution is not cached; repeated calls for same objectId hit Tryouts every time | `services/students.js:1431-1432` | Unnecessary external API calls |
| 2 | Returns `success: false` with `data: null` for not-found rather than 404 | `controllers/students.js:84` | Inconsistent API pattern |
| 3 | No validation preventing illogical flag combinations (all false) | Validator | Unnecessary DB joins |

### Medium Priority

| # | Issue |
|---|-------|
| 4 | Different error types from different layers (`DatabaseError` vs `DependencyError`) |
| 5 | No correlation ID / request tracing across Tryouts service call |

---

## Test Scenarios

### Functional
- Lookup by `studentId` (valid, invalid, non-existent)
- Lookup by `referralCode`
- Lookup by `objectId` (valid booking, invalid booking)
- All flag combinations (8 permutations of true/false)
- `isStudentClassBalance=true` with/without class balances
- `isPackageInfo=true` with/without active packages

### Validation
- Missing all three lookup parameters
- Invalid `studentId` format (non-integer, negative)
- Invalid boolean flag values

### Performance
- Response time: basic vs all flags enabled
- Concurrent requests for same student
- Students with many class balances / active packages

### Error Handling
- Tryouts service unavailable during `objectId` lookup
- Database connection failure
- Invalid JWT / expired token

### Edge Cases
- Student with no parent (fails required join)
- Student with multiple active packages
- `objectId` pointing to deleted booking
- Very long referral codes
