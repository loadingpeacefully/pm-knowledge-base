---
endpoint: GET /v1/student/details
service: eklavya
source_id: 4012dffc-aaa3-4b8f-b6f4-70132d560a47
original_source_name: details
controller: controllers/students.js:28
service_file: services/students.js:918
router_file: routers/students.js:61
auth: None (public endpoint)
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/student/details

## Summary

Retrieves comprehensive student and parent information for a single student. Supports lookup by `studentId`, `referralCode`, or `objectId`. Optionally includes achievement data (badges and certificates), class balance, and package information. Sensitive parent data can be masked for frontend consumers via `isFe=true`.

**Category:** Internal API
**Owner/Team:** Student Management Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/student/details`
**Authentication:** None (public endpoint)

### Query Parameters

**Validation source:** `validators/student.js:247-260`

**One of the following is required:**

| Field | Type | Description |
|-------|------|-------------|
| `studentId` | integer (min: 1) | Student ID |
| `referralCode` | string | Student referral code |
| `objectId` | string | Booking object ID |

**Optional:**

| Field | Type | Description |
|-------|------|-------------|
| `isFe` | boolean | Mask sensitive parent data (email, phone) |
| `leadSource` | string | Filter by lead source |
| `showAchievements` | boolean | Include badge and certificate data |
| `isStudentClassBalance` | boolean | Include class balance info |
| `isPackageInfo` | boolean | Include package information |
| `isStudentProfile` | boolean | Include student profile details |

### Request Examples

```
GET /v1/student/details?studentId=123
GET /v1/student/details?studentId=123&isFe=true
GET /v1/student/details?studentId=123&showAchievements=true
GET /v1/student/details?referralCode=ABC123
GET /v1/student/details?objectId=booking_456
GET /v1/student/details?studentId=123&isFe=false&showAchievements=true&leadSource=website
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "student": {
      "id": 123,
      "name": "John Doe",
      "grade": 5,
      "gems": 100,
      "referralCode": "ABC123",
      "active": true,
      "leadSource": "website",
      "diamondCredits": { "type": "diamond_credit", "totalCredits": 50, "creditsConsumed": 10 },
      "level": "Junior Champ",
      "isPaid": true,
      "language": "English",
      "StudentLanguageMappings": [{ "languageId": 10, "preferrence": 1 }],
      "StudentClassBalances": [{ "id": 789, "student_id": 123, "course_id": 5, "remaining_classes": 15 }],
      "StudentPerformanceMatrices": [{ "teacherRating": 4.5, "totalCompletedPaidClass": 10 }]
    },
    "parent": {
      "id": 456,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "phone": "+1234567890",
      "countryId": 1,
      "countryName": "United States",
      "businessRegion": "North America",
      "dialCode": "+1",
      "timezone": "America/New_York"
    },
    "studentProfile": {
      "student_id": 123,
      "school": "ABC School",
      "joinedDate": "2024-01-15",
      "dob": "2015-05-20",
      "gender": "Male",
      "age": 9,
      "profilePicture": "https://ik.imagekit.io/brightchamps/dashboard/avatar_boy.webp",
      "isOnboarded": true
    }
  },
  "message": "details fetched successfully."
}
```

**With `isFe=true` — masked parent fields:**
```json
{
  "parent": {
    "email": "****@example.com",
    "phone": "+123*******"
  }
}
```

**With `showAchievements=true`:**
```json
{
  "achievementData": {
    "certificates": [{ "id": 1, "name": "Coding Fundamentals", "issueDate": "2024-02-15" }],
    "badges": [{ "badgeId": 1, "name": "Math Master", "progress": 75, "isEarned": false }]
  }
}
```

**Not found (200 with `success: false`):**
```json
{ "success": false, "data": null, "message": "details fetched successfully." }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (or not found with `success: false`) |
| 400 | Bad request — validation failed |
| 404 | Student not found |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:28-44`)

1. Extract `studentId`, `isFe`, `leadSource`, `showAchievements` from query params
2. Call `StudentsService.studentAndParentViaId()` with parameters
3. Format via `ApiResponse` wrapper
4. Return JSON

### Service (`services/students.js:918-1082`)

1. **Build student filter:** `{ id: studentId }`, add `leadSource` if provided
2. **Execute `Student.findOne()`** with eager-loaded relations:
   - `Parent` (required INNER JOIN)
   - `StudentClassBalance` (LEFT JOIN)
   - `StudentLanguageMapping` (LEFT JOIN, specific attributes, ordered by preference DESC)
   - `StudentProfile` (LEFT JOIN)
   - `StudentCredit` (LEFT JOIN, specific attributes)
   - `StudentPerformanceMatrix` (LEFT JOIN, 20+ attributes)
3. **Parallel external calls** via `Promise.allSettled()`:
   - Platform Service: `getCountry(countryId)`, `getTimeZone(tzId)`, `getLanguageById(languageId)`
   - Tryouts Service: `getCountryGroups({ countryId, isStudent: 1 })`
4. **Data processing:**
   - Format parent with country/timezone data
   - Mask email/phone if `isFe=true`
   - Compute student age, penalties, profile picture URL (gender-based default)
   - Process credits and level
5. **Optional achievements** (if `showAchievements=true`):
   - Badges Service: `fetchBadges()`, `fetchStudentBadgeProgress()`
   - Paathshala Service: `getCertificates({ studentId })`
6. Return structured `{ student, parent, studentProfile }` object

---

## Microservice Dependencies

| Service | Call | Purpose | Parallelism |
|---------|------|---------|-------------|
| Platform | `getCountry(countryId)` | Country name, dial code | Parallel (allSettled) |
| Platform | `getTimeZone(tzId)` | Timezone display name | Parallel (allSettled) |
| Platform | `getLanguageById(languageId)` | Language name | Parallel (allSettled) |
| Tryouts | `getCountryGroups({ countryId, isStudent: 1 })` | Business region | Sequential |
| Badges | `fetchBadges()`, `fetchStudentBadgeProgress()` | Achievement badges | Conditional |
| Paathshala | `getCertificates({ studentId })` | Certificates | Conditional |

**Error handling:** All external calls use `Promise.allSettled()` — individual failures do not break the main response.

---

## Database & SQL Analysis

### Primary Query (`services/students.js:923-980`)

```js
Student.findOne({
  where: studentFilter,
  include: [
    { model: Parent },
    { model: StudentClassBalance },
    { model: StudentLanguageMapping, required: false, attributes: ["languageId", "preferrence"] },
    { model: StudentProfile, required: false },
    { model: StudentCredit, required: false, attributes: [...] },
    { model: StudentPerformanceMatrix, required: false, attributes: [...20+ fields] }
  ],
  order: [[StudentLanguageMapping, "preferrence", "DESC"]]
})
```

### Equivalent SQL

```sql
SELECT s.*, p.*, scb.*, slm.languageId, slm.preferrence,
       sp.*, sc.type, sc.totalCredits, sc.creditsConsumed,
       spm.teacherRating, spm.totalCompletedPaidClass -- ...20+ columns
FROM students s
INNER JOIN parents p ON s.parent_id = p.id
LEFT JOIN student_class_balances scb ON s.id = scb.student_id
LEFT JOIN student_language_mappings slm ON s.id = slm.student_id
LEFT JOIN student_profiles sp ON s.id = sp.student_id
LEFT JOIN student_credits sc ON s.id = sc.student_id
LEFT JOIN student_performance_matrix spm ON s.id = spm.student_id
WHERE s.id = ? AND (s.leadSource = ? OR ? IS NULL)
ORDER BY slm.preferrence DESC, slm.id DESC;
```

### Recommended Indexes

```sql
CREATE INDEX idx_students_id ON students(id);
CREATE INDEX idx_students_leadSource ON students(leadSource);
CREATE INDEX idx_slm_student_preference ON student_language_mappings(student_id, preferrence DESC);
CREATE INDEX idx_scb_student_id ON student_class_balances(student_id);
CREATE INDEX idx_sp_student_id ON student_profiles(student_id);
CREATE INDEX idx_sc_student_id ON student_credits(student_id);
CREATE INDEX idx_spm_student_id ON student_performance_matrix(student_id);
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Complex single query with 6 eager-loaded tables including 20+ attribute performance matrix | `services/students.js:923-980` | Slow response, high DB load |
| 2 | 3–4 external service calls per request add cascading latency | `services/students.js:986-994` | P99 latency degradation |
| 3 | Full parent data (email, phone) returned unless `isFe=true` — opt-in masking is risky | `services/students.js:1004-1018` | Data privacy exposure |

### Medium Priority

| # | Issue | Location |
|---|-------|----------|
| 4 | 20+ performance metric attributes selected — unnecessary data transfer | `services/students.js:948-973` |
| 5 | Profile picture URL generation logic in service (should be frontend or CDN) | `services/students.js:1037-1045` |

---

## Test Scenarios

### Functional
- Lookup by `studentId`, `referralCode`, `objectId`
- `isFe=true` masked data validation
- `showAchievements=true` badge + certificate response
- `leadSource` filter behavior
- Non-existent student returns `success: false`

### Performance
- Response time with all includes vs minimal
- External service call timing under load
- Concurrent user load testing

### Error Scenarios
- Invalid `studentId` format
- External service (Platform, Tryouts) failure — should not 500
- Database connection failure
- Missing required parent relation

### Security
- Sensitive data masking when `isFe=true`
- Data exposure audit when `isFe=false`
- Parameter injection attempts
