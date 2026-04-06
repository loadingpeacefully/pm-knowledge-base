---
endpoint: PUT /v1/student/all-details
service: eklavya
source_id: 052a9875-c499-44c6-8172-4ebe0caf9251
original_source_name: all-details
controller: controllers/students.js (updateStudentAllDetails)
service_file: services/students.js (updateStudentAllDetails)
router_file: routers/students.js:134
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# PUT /v1/student/all-details

## Summary

Updates comprehensive student and parent information across 4 database tables simultaneously (`students`, `parents`, `student_profiles`, `student_language_mappings`). Accepts either `studentId` or `objectId` (resolved via TryoutsService). Conditionally syncs user identity changes to ChowkidarService and triggers certificate regeneration via AWS SQS when the student's name changes. No authentication required. Critical issue: no database transaction wraps the multi-table updates — partial failure leaves inconsistent state.

**Category:** Student Management API — Profile Update
**Owner/Team:** Student Management Team

---

## HTTP Contract

**Method:** PUT
**Path:** `/v1/student/all-details`
**Authentication:** None

### Request Body

**Identifier (one of required):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | integer (≥1) | Conditional | Student ID to update |
| `objectId` | string | Conditional | Booking object ID — resolved to studentId via TryoutsService |

**Update fields (all optional):**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Student name |
| `grade` | integer | Student grade level |
| `parentName` | string | Parent name (mapped to `parents.name`) |
| `email` | string | Parent email (valid email format) |
| `phone` | string | Parent phone number |
| `tzId` | integer (≥1) | Timezone ID (requires `countryId`) |
| `countryId` | integer (≥1) | Country ID (requires `tzId`) |
| `languageId` | integer | Language preference ID |
| `preferredLanguageId` | integer | Preferred language (mapped to `parents.languageId`) |
| `alternatePhoneNumber` | string | Alternate phone |
| `alternateDialCode` | string | Alternate dial code |
| `alternateEmail` | string | Alternate email (valid email format) |
| `dob` | string | Date of birth |
| `address` | string | Address |
| `city` | string | City |
| `dialCode` | string | Phone dial code |
| `gender` | string | Gender |
| `updatedBy` | integer | ID of user making the update |
| `source` | string | Source of update (e.g. `"admin_panel"`) |

### Request Examples

```json
// Update by studentId
{ "studentId": 12345, "name": "John Doe Updated", "grade": 8, "email": "john.doe.updated@example.com", "phone": "+1234567890", "updatedBy": 789 }

// Update by objectId
{ "objectId": "booking_abc123", "parentName": "Jane Doe", "countryId": 1, "tzId": 5, "alternateEmail": "jane.alternate@example.com" }

// Comprehensive update
{ "studentId": 12345, "name": "Updated Name", "parentName": "Updated Parent", "grade": 10, "email": "new@example.com", "gender": "male", "dob": "2010-05-15", "countryId": 2, "tzId": 8 }
```

### Response Format

**Success (200):**
```json
{ "success": true, "data": true, "message": "student details updated successfully." }
```

**Validation error (400):**
```json
{ "success": false, "data": { "errors": [{ "type": "field", "msg": "Invalid studentId", "path": "studentId" }] }, "message": "Validation Error" }
```

**Missing identifier (400):**
```json
{ "success": false, "data": { "errors": [{ "type": "alternative", "msg": "Please provide studentId or phone" }] }, "message": "Validation Error" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Updated successfully |
| 400 | Validation error |
| 500 | Database or service error |

---

## Logic Flow

### Controller

1. Extract all params from request body
2. Log country update info (debug)
3. Call `StudentsService.updateStudentAllDetails(payload)`
4. Return `ApiResponse({ data: true })`

### Service

**Phase 1 — Student ID resolution:**
1. If `objectId` provided: `TryoutsService.getOnlyBookingInfoByObjectId({ objectId })` → extract `studentId`
2. If `studentId` provided: use directly

**Phase 2 — Payload segmentation (using strict column allowlists):**
3. `studentPayload` ← `ALLOWED_STUDENT_COLUMNS` (name, grade, hasDemo)
4. `parentPayload` ← `ALLOWED_PARENT_COLUMNS` (phone, email, name, tzId, countryId, etc.)
   - Field mapping: `parentName → name`, `preferredLanguageId → languageId`
5. `profilePayload` ← `ALLOWED_PROFILE_COLUMNS` (gender, dob, address, city, profilePicture)
   - Auto-sets `student_id = studentId`
6. `languagePayload` ← `ALLOWED_STUDENT_LANGUAGE_MAPPING_COLUMNS` (languageId)

**Phase 3 — Fetch existing records:**
7. `SELECT parentId FROM students WHERE id = studentId`
8. `SELECT * FROM parents WHERE id = parentId` (for identity change comparison)

**Phase 4 — Sequential database updates:**
9. `UPDATE students SET ... WHERE id = studentId` (if `studentPayload`)
10. `UPDATE parents SET ... WHERE id = parentId` (if `parentPayload`)
11. `INSERT INTO student_profiles ... ON DUPLICATE KEY UPDATE ...` (if `profilePayload`)
12. `studentLanguage({ studentId, languageId })` upsert (if `languagePayload`)

**Phase 5 — External service sync (conditional):**
13. If email/phone/countryId/dialCode changed: `ChowkidarService.updateUserIdentifiers({ oldUserDetails, newUserDetails })`

**Phase 6 — Certificate regeneration (conditional, if name changed):**
14. `PaathshalaService.getCertificates({ studentId })`
15. For each certificate with valid `template_id`: publish to SQS `UPDATE_CERTIFICATE_TRIGGER` queue with updated `student_name` in `merge_vars`

---

## Microservice Dependencies

| Service | Call | Trigger | Failure impact |
|---------|------|---------|---------------|
| TryoutsService | `getOnlyBookingInfoByObjectId({ objectId })` | `objectId` provided | Blocks update — cannot resolve studentId |
| ChowkidarService | `updateUserIdentifiers(...)` | email/phone/country changed | Blocks update (called synchronously) |
| PaathshalaService | `getCertificates({ studentId })` | `name` field changed | Blocks update (called synchronously) |
| AWS SQS | `publishMessage(certificatePayload, queue)` | Name changed + certs exist | Certificate names not updated |

---

## Database & SQL Analysis

### Key Queries

```sql
-- Lookup
SELECT parent_id FROM students WHERE id = ?;
SELECT * FROM parents WHERE id = ?;

-- Student update
UPDATE students SET name = ?, grade = ?, has_demo = ?, updated_by = ?, source = ?, updated_at = NOW() WHERE id = ?;

-- Parent update (with field mapping)
UPDATE parents
SET phone = ?, email = ?, name = ?,  -- parentName→name
    mother_name = ?, tz_id = ?, country_id = ?,
    alternate_email = ?, alternate_phone_number = ?,
    language_id = ?,  -- preferredLanguageId→languageId
    dial_code = ?, updated_at = NOW()
WHERE id = ?;

-- Profile upsert
INSERT INTO student_profiles (student_id, gender, dob, address, city, school_name, ...)
VALUES (?, ?, ?, ?, ?, ?, ...)
ON DUPLICATE KEY UPDATE gender = VALUES(gender), dob = VALUES(dob), ...;
```

### Tables Accessed

| Table | Operation | Purpose |
|-------|-----------|---------|
| `students` | SELECT + UPDATE | Student name, grade |
| `parents` | SELECT + UPDATE | Contact info, timezone, language |
| `student_profiles` | UPSERT | Gender, DOB, address, city |
| `student_language_mappings` | UPSERT (via `studentLanguage`) | Language preference priority |

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No database transaction — 4 table updates are independent; if parent update fails after student update, data is inconsistent | Service layer | Partial update corruption |
| 2 | ChowkidarService and PaathshalaService called synchronously in critical path — failure blocks entire update | Service layer | Endpoint fails when auth or cert services are down |

### Medium Priority

| # | Issue | Impact |
|---|-------|--------|
| 3 | Sequential database updates — student, parent, profile, language mapping each make separate round trips | Performance: ~4 DB round trips per update |
| 4 | Certificate fetch + SQS publish blocks response — should be fully async | Update latency scales with number of certificates |
| 5 | No optimistic locking — concurrent updates overwrite silently | Data loss under concurrent access |

### Low Priority

| # | Issue |
|---|-------|
| 6 | No authentication — any caller can update any student's data |
| 7 | Invalid email is rejected by validator (unlike `create-or-update` which silently removes it) — inconsistent behavior |
| 8 | Limited audit logging — `updatedBy` field tracked but field-level change history not stored |

---

## Test Scenarios

### Functional
- Update by `studentId` — only student fields
- Update by `studentId` — only parent fields
- Update by `objectId` — requires TryoutsService resolution
- Update student name → verify SQS certificate message published
- Update email → verify ChowkidarService called with old and new details
- Profile upsert — new profile vs existing profile

### Business Logic
- `parentName` → saved as `parents.name`
- `preferredLanguageId` → saved as `parents.languageId`
- `countryId` provided without `tzId` → 400 validation
- Empty payload (no fields to update) → behavior (all allowlist filters return empty)

### Transaction / Data Integrity
- DB failure on parent update after student update → student updated but parent not (no rollback)
- Concurrent updates to same studentId → last write wins (no optimistic locking)

### External Service
- TryoutsService down → `objectId`-based update fails
- ChowkidarService down → identity sync blocked, update fails
- PaathshalaService down → certificate update blocked, update fails
- SQS unavailable → certificates not regenerated

### Security
- No auth — any caller can update any student profile
- `studentId` enumeration to modify other students' data
- SQL injection in text fields (mitigated by Sequelize ORM)

### Edge Cases
- Student with no parent record
- `name` update for student with 50+ certificates
- Unicode characters in name (certificate merge vars)
- Updating both `languageId` and `preferredLanguageId`
- `countryId` change triggers Chowkidar update
