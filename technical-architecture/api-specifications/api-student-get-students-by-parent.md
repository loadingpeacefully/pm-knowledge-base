---
endpoint: GET /v1/student/get-students
service: eklavya
source_id: 3443f51d-e037-4f54-bb55-399304d908fe
original_source_name: get-students
controller: controllers/students.js:47
service_file: services/students.js:1337
router_file: routers/students.js:62-68
auth: JWT required (authMiddleware with true parameter)
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/student/get-students

## Summary

Retrieves all students associated with the authenticated parent's account. The parent ID is extracted from the JWT token — no `parentId` query param needed. Optionally enriches results with demo booking counts (via Tryouts service) and parent magic link URLs (via Chowkidar service). Calculates `showParentHub` and `showInsights` flags from class balance data.

**Category:** Parent Dashboard API — Student Management & Profile Access
**Owner/Team:** Parent Dashboard / Student Management Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/student/get-students`
**Authentication:** JWT required (`Authorization: Bearer`)

### Query Parameters

**Validation source:** `validators/student.js:691-694`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `demoData` | boolean | No | When `true`: fetch demo booking counts, compute `showParentHub`, `showInsights` |
| `isMagicLink` | boolean | No | When `true`: generate magic link for parent login (requires Chowkidar service) |

### Request Examples

```
GET /v1/student/get-students
GET /v1/student/get-students?demoData=true
GET /v1/student/get-students?isMagicLink=true
GET /v1/student/get-students?demoData=true&isMagicLink=true
```

### Response Format

**Basic (200):**
```json
{
  "success": true,
  "data": [
    { "id": 12345, "name": "Alice Johnson", "referral_code": "AJ789456",
      "isActive": true, "parentId": 567, "gender": "female",
      "profilePicture": "https://cdn.brightchamps.com/profiles/alice.jpg",
      "isNewDashboard": true,
      "StudentClassBalances": [
        { "total_booked_class": 20, "total_completed_class": 8,
          "total_penalties": 1, "total_paid_class": 20, "classType": "online" }
      ] }
  ],
  "message": "students fetched successfully."
}
```

**Enhanced (`demoData=true`):**
```json
{
  "data": [{
    "id": 12345, "name": "Alice Johnson",
    "showParentHub": true, "showInsights": true,
    "demoClassCount": { "totalBooked": 3, "totalPending": 1 },
    "magicLink": null
  }]
}
```

**With `isMagicLink=true`:**
```json
{ "magicLink": "https://auth.brightchamps.com/magic/abc123xyz456" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (empty array if no students) |
| 400 | Bad request — invalid boolean params |
| 401 | Unauthorized — missing or invalid JWT |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:47-64`)

1. Extract `parentId` from `req.user.id` (JWT payload — no query param)
2. Extract `demoData`, `isMagicLink` from query params
3. Call `StudentsService.getStudentsViaParentId(parentId, { demoData, isMagicLink })`
4. Format via `ApiResponse` wrapper

### Service (`services/students.js:1337-1419`)

**Base query (always):**
```js
Student.findAll({
  where: { parentId },
  include: [
    { model: StudentProfile, attributes: [] },
    { model: StudentClassBalance, required: false,
      attributes: ["total_booked_class","total_completed_class","total_penalties","total_paid_class","classType"] },
    // Conditional: Parent (for magic link)
  ],
  attributes: { include: [
    [col("StudentProfile.gender"), "gender"],
    [col("StudentProfile.profile_picture"), "profilePicture"],
    [col("StudentProfile.is_new_dashboard"), "isNewDashboard"]
  ]}
})
```

**Enhanced processing (when `demoData=true`):**
1. Magic link: `chowkidarService.getMagicLink({ phone, countryId })` (if `isMagicLink=true`)
2. Demo bookings: `tryoutsService.fetchBookingFromStudentId(studentIds.join(","))` — comma-separated IDs
3. Business logic per student:
   - `showParentHub`: `true` if any class balance has `total_paid_class > 0`
   - `showInsights`: `true` if paid classes exist AND class type is `online` or `online-group`
   - `demoClassCount.totalPending`: active demo bookings with `joinStatus in [created,joined]` AND `datetime > now - 1 hour`
   - `demoClassCount.totalBooked`: all active demo bookings

---

## Microservice Dependencies

| Service | Call | Trigger | Auth |
|---------|------|---------|------|
| Chowkidar | `getMagicLink({ phone, countryId })` | `isMagicLink=true` AND `demoData=true` | Service key |
| Tryouts | `fetchBookingFromStudentId(csvStudentIds)` | `demoData=true` | Service key |

**Current issue:** Both calls are sequential (not parallelized). Should use `Promise.all`.

---

## Database & SQL Analysis

### Basic SQL

```sql
SELECT students.*, student_profiles.gender, student_profiles.profile_picture, student_profiles.is_new_dashboard
FROM students
LEFT JOIN student_profiles ON students.id = student_profiles.student_id
LEFT JOIN student_class_balances ON students.id = student_class_balances.student_id
WHERE students.parent_id = 567;
```

### Enhanced SQL (with magic link — adds Parent join)

```sql
SELECT students.*, sp.gender, sp.profile_picture, sp.is_new_dashboard,
       p.phone, p.country_id
FROM students
LEFT JOIN student_profiles sp ON students.id = sp.student_id
LEFT JOIN student_class_balances scb ON students.id = scb.student_id
LEFT JOIN parents p ON students.parent_id = p.id
WHERE students.parent_id = 567;
```

### Tables Accessed

| Table | Join | Condition |
|-------|------|-----------|
| `students` | PRIMARY | `WHERE parent_id = ?` |
| `student_profiles` | LEFT JOIN | always |
| `student_class_balances` | LEFT JOIN | always |
| `parents` | LEFT JOIN | only when `isMagicLink=true` |

### Recommended Indexes

```sql
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_student_profiles_student_id ON student_profiles(student_id);
CREATE INDEX idx_student_class_balances_student_id ON student_class_balances(student_id);
CREATE INDEX idx_students_parent_active ON students(parent_id, is_active);
```

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Sequential external API calls (magic link + booking) — should be `Promise.all` | `services/students.js:1373-1380` | 100–500ms extra latency |
| 2 | Booking processing uses O(n×m) nested loop — should use Map-based O(1) lookup | `services/students.js:1383-1398` | Scales poorly with many students/bookings |
| 3 | Student IDs passed to Tryouts as comma-separated string — URL length limits | `students.map((e) => e.id).join(",")` | Breaks for parents with many students |

### Low Priority

| # | Issue |
|---|-------|
| 4 | No pagination — all students returned for a parent |
| 5 | External service failures (Tryouts/Chowkidar) can break entire response — no graceful fallback |
| 6 | Magic link uses `students[0].Parent.phone` — fails if first student has different parent |

---

## Test Scenarios

### Functional
- Parent with single student (basic vs enhanced mode)
- Parent with multiple students, mixed class statuses
- `demoData=true` — verify `showParentHub`, `showInsights`, `demoClassCount` values
- `isMagicLink=true` — verify magic link URL in response
- Empty parent (no students) → `data: []`

### Business Logic
- `showParentHub=true` when any student has `total_paid_class > 0`
- `showInsights=true` when paid classes AND `classType` is `online` or `online-group`
- Pending demo count: only future bookings with 1-hour buffer
- Students with no class balances → `showParentHub=false`

### Security
- JWT required — 401 without token
- Cannot access other parents' students (parentId from JWT)
- Invalid boolean values for flags

### Error Handling
- Chowkidar service down → magic link fails (should fall back gracefully)
- Tryouts service timeout → demo data unavailable (should return basic data)
- Database failure

### Edge Cases
- Parent with 20+ students
- Students with no profiles
- Demo bookings with timezone edge cases (1-hour buffer)
