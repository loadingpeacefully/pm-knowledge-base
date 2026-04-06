---
endpoint: POST /v1/student/parents/create-or-update
service: eklavya
source_id: 850a77b7-fc81-410b-8ea7-b61695aed297
original_source_name: create-or-update
controller: controllers/students.js:1030
service_file: services/students.js:3257
router_file: routers/students.js:326
auth: API Key (apiKeyMiddleware)
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/student/parents/create-or-update

## Summary

Creates or updates a parent record (identified by phone or `parentId`) and optionally creates or updates an associated student record (when `grade` is provided). Integrates with three external services: PlatformService for timezone/country resolution, ChowkidarService for user identity management (creates/updates identity records), and LanguagePredictionService for language inference from UTM data and browser locale. Generates a referral code for new students. API key authentication required.

**Category:** User Management API — Parent/Student Registration & Profile Updates
**Owner/Team:** Student Management & Registration Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/student/parents/create-or-update`
**Authentication:** API Key (`X-API-Key`)

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | No | Parent's email address (sanitized) |
| `phone` | string | Conditional | Parent's phone — required if `parentId` not provided |
| `name` | string | No | Parent's full name |
| `tzId` | integer | Conditional | Timezone ID — required when `phone` provided (or resolve via `timeZone`) |
| `timeZone` | string | No | Timezone name (e.g. `"Europe/London"`) — resolved to `tzId` via PlatformService |
| `countryId` | integer | Conditional | Country ID — required when `phone` provided |
| `parentId` | integer | Conditional | Existing parent ID — required if `phone` not provided |
| `grade` | integer | No | Student grade (1–12) — if provided, triggers student creation/update |
| `childName` | string | No | Student's name |
| `utmSource` | string | No | UTM source for lead tracking (mapped to `leadSource`, default: `"default"`) |
| `dialCode` | string | No | Country dial code (e.g. `"+1"`) |
| `courseId` | integer | No | Course ID for language preference mapping |
| `languagePreference` | integer | No | Preferred language ID |
| `utmMedium` | string | No | UTM medium for marketing attribution |
| `language` | string | No | Language code for language prediction |
| `landingPage` | string | No | Landing page URL for tracking |
| `browserLocale` | string | No | Browser locale for language inference |

**Validation rules:**
- Either `parentId` or `phone` must be provided
- When `phone` provided: `countryId` required, and either `tzId` or `timeZone` required
- Invalid email is silently removed (not rejected) — sanitizer deletes the field

### Request Examples

```json
// Create new parent + student
{
  "email": "jane.smith@example.com", "phone": "+1987654321", "name": "Jane Smith",
  "tzId": 123, "countryId": 1, "grade": 6, "childName": "Emma Smith",
  "utmSource": "google", "dialCode": "+1", "courseId": 5, "languagePreference": 1
}

// Update existing parent
{ "parentId": 456, "email": "john.updated@example.com", "name": "John Updated", "grade": 9, "childName": "John Jr Updated" }

// Create with timezone name resolution
{ "phone": "+447700900123", "timeZone": "Europe/London", "countryId": 2, "name": "Sarah Johnson", "grade": 7, "childName": "Alex Johnson", "courseId": 8 }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "parent": { "id": 789, "email": "jane.smith@example.com", "phone": "+1987654321", "name": "Jane Smith", "countryId": 1, "tzId": 123, "dialCode": "+1", "createdAt": "2025-01-26T10:30:00.000Z", "updatedAt": "2025-01-26T10:30:00.000Z" },
    "student": { "id": 456, "name": "Emma Smith", "grade": 6, "parentId": 789, "leadSource": "google", "hasDemo": true, "referralCode": "STU_456_REF", "createdAt": "2025-01-26T10:30:00.000Z", "updatedAt": "2025-01-26T10:30:00.000Z" }
  },
  "message": "Parent created or updated successfully."
}
```

**No student (grade not provided) — `student: null`**

**Validation error (400):**
```json
{ "success": false, "data": { "errors": [{ "type": "field", "msg": "Either parentId or phone is required" }] }, "message": "Validation Error" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Parent (and optionally student) created/updated |
| 400 | Validation error or missing required fields |
| 401 | Invalid or missing API key |
| 404 | Parent not found when using `parentId` |
| 500 | Database or service error |

---

## Logic Flow

### Controller (`controllers/students.js:1030-1097`)

1. Extract 16 body params
2. Log `countryId` if provided (debugging)
3. Call `StudentsService.createOrUpdateParentAndStudent(params)`
4. Return wrapped response

### Service (`services/students.js:3257-3320`)

**Phase 1 — Parent management (`services/students.js:751-850`):**

If `parentId` provided (update path):
- Find parent by ID; throw if not found
- Build update payload (name, email conditionally)
- Check `paid_number` flag to block certain updates for paying customers
- Update parent record; call `ChowkidarService.updateUserIdentifiers` if email changed

If `phone` provided (create path):
- Get dial code from PlatformService if not provided
- `Parent.findOrCreate({ where: { phone } })` — phone as unique identifier
- Default name to `"Parent"` if not provided
- `ChowkidarService.createUserV2(email, phone, countryId, dialCode)`
- If existing by phone: `ChowkidarService.updateUserIdentifiers` if email provided

**Phase 2 — Lead source resolution:**
- Map `utmSource` → internal `leadSource` using `LEAD_SOURCES` constant
- Set `hasDemo = true` for all students created via this endpoint

**Phase 3 — Student management (only when `grade` provided):**
- `Student.findOrCreate({ where: { grade, parentId } })`
- Generate referral code via `EncryptionService.generateReferralCode(studentId)` for new students

**Phase 4 — Language preference (`services/students.js:1216-1282`):**
- If `courseId` in `SCHOLA_COURSES`: use adhoc mapping by courseId/countryId
- Otherwise: `LanguagePredictionService.fetchLang(partialBooking)` — infers from UTM + browser locale
- Find max preference value for student
- Create/update `StudentLanguageMapping` with incremented priority
- If `languagePreference` differs from inferred language: add separate mapping entry

---

## Microservice Dependencies

| Service | Call | Trigger | Failure impact |
|---------|------|---------|---------------|
| PlatformService | `getTimeZone(null, { name })` | `phone` provided + `timeZone` field set | Blocks parent creation |
| PlatformService | `getCountry(countryId)` | Dial code resolution | Blocks creation if dial code needed |
| ChowkidarService | `createUserV2(email, phone, countryId, dialCode)` | New parent creation | Blocks creation (critical path) |
| ChowkidarService | `updateUserIdentifiers(...)` | Email change on existing parent | Partial failure risk |
| LanguagePredictionService | `fetchLang(partialBooking)` | Student created, non-Schola course | Defaults to English (graceful) |

---

## Database & SQL Analysis

### Key Queries

```sql
-- Find parent by ID (update path)
SELECT * FROM parents WHERE id = ?;

-- Find or create parent by phone
SELECT * FROM parents WHERE phone = ? LIMIT 1;
INSERT INTO parents (email, phone, name, countryId, tzId, dialCode, createdAt, updatedAt) VALUES (...);

-- Update parent
UPDATE parents SET email = ?, name = ?, countryId = ?, tzId = ?, updatedAt = NOW() WHERE id = ?;

-- Find or create student by grade + parentId
SELECT * FROM students WHERE grade = ? AND parentId = ? LIMIT 1;
INSERT INTO students (grade, name, parentId, leadSource, hasDemo, createdAt, updatedAt) VALUES (...);

-- Update referral code for new student
UPDATE students SET referralCode = ? WHERE id = ?;

-- Language preference management
SELECT * FROM student_language_mappings WHERE studentId = ? ORDER BY preferrence DESC LIMIT 1;
INSERT INTO student_language_mappings (studentId, languageId, preferrence, ...) VALUES (...);
UPDATE student_language_mappings SET preferrence = ? WHERE studentId = ? AND languageId = ?;
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `parents` | Create or update parent record |
| `students` | Create or update student record |
| `student_language_mappings` | Language preference storage with priority ordering |

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Timezone resolution API call happens in validator middleware — service call during validation phase adds latency before request reaches service layer | `validators/student.js:747-774` | 100–300ms latency on every `phone+timeZone` request |
| 2 | ChowkidarService called synchronously in critical path — failure blocks parent creation entirely | Parent creation logic | Full endpoint failure when Chowkidar is down |
| 3 | Multiple sequential external service calls (Platform → Chowkidar → Language) — no parallelism | Service layer | 300–700ms cumulative latency |

### Low Priority

| # | Issue |
|---|-------|
| 4 | Invalid email is silently deleted (not rejected) — client receives 200 but email not saved, no indication |
| 5 | Parent name defaults to `"Parent"` — low quality default for analytics |
| 6 | Language preference logic is complex with multiple code paths — high maintenance burden |
| 7 | `student.findOrCreate({ where: { grade, parentId } })` — student uniqueness by grade + parent is fragile (if grade changes, new student record created) |

---

## Test Scenarios

### Functional
- Create new parent + student with all fields
- Create parent only (no `grade` provided) → `student: null`
- Update existing parent by `parentId`
- Timezone name resolution (`timeZone` field → `tzId` via PlatformService)
- New student → referral code generated
- UTM source mapping to `leadSource` constant

### Business Logic
- Schola course → adhoc language mapping (no LanguagePrediction call)
- Non-Schola course → language predicted from UTM + browserLocale
- `languagePreference` different from inferred language → two preference entries created
- Parent with paid history → certain fields blocked from update

### Validation
- Neither `parentId` nor `phone` → 400
- `phone` without `countryId` → 400
- `phone` without `tzId` or `timeZone` → 400
- Invalid timezone name → 400 (PlatformService resolution fails)
- Invalid email → silently removed, request continues
- `grade` outside 1–12 → behavior

### External Service
- ChowkidarService down → endpoint fails (known risk)
- PlatformService timezone API fails → blocks phone-based creation
- LanguagePrediction fails → default language assigned (graceful)

### Security
- API key required — 401 without key
- No data validation that `parentId` belongs to calling service's scope
- Phone number as unique identifier — collision risk across test/prod

### Edge Cases
- Same phone used twice concurrently → `findOrCreate` race condition
- Grade change for existing student → new student record created (may duplicate)
- Empty `childName` with `grade` → student created with null name
