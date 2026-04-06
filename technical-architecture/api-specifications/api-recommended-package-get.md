---
endpoint: GET /v2/recommended-package
service: eklavya
source_id: 41c3e825-9ca4-4f0c-aa15-2103ac95e0de
original_source_name: recommended-package
controller: controllers/v2/package-sale.js:230
service_file: facades/v2/package-sale.js:3158
router_file: routers/v2/package-sale.js:72
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v2/recommended-package

## Summary

Recommends the next package installment for a student — either for continuing an existing course (via `studentClassBalanceId`) or enrolling in a new course (via `studentId` + `courseId`). Returns `totalClasses`, `sellingPrice`, and `currency` for the next recommended installment. Pricing is calculated from the student's purchase history or fetched from NectedService (external pricing API). Calls 6 services sequentially, no caching, no authentication.

**Category:** Package Management API — Recommendation Engine
**Owner/Team:** Package Sales & Student Recommendation Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v2/recommended-package`
**Authentication:** None

### Query Parameters

**Option 1 — Existing course continuation:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentClassBalanceId` | integer (≥1) | Yes | Student class balance ID for existing course |

**Option 2 — New course enrollment:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | integer (≥1) | Yes | Student ID |
| `courseId` | integer | No | Specific course ID |

### Request Examples

```
GET /v2/recommended-package?studentClassBalanceId=12345
GET /v2/recommended-package?studentId=678&courseId=5
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": { "nextInstallment": { "totalClasses": 20, "sellingPrice": 299.99, "currency": "USD" } },
  "message": "recommended package classes fetched successfully"
}
```

**No recommendation (200):**
```json
{ "success": true, "data": {}, "message": "recommended package classes fetched successfully" }
```

**Already at max classes (400):**
```json
{ "success": false, "data": null, "message": "Already booked max classes", "error": "ValidationError" }
```

**Student didn't buy package in this course (400):**
```json
{ "success": false, "data": null, "message": "Student didn't bought package in this course", "error": "ValidationError" }
```

**Invalid class balance ID (400):**
```json
{ "success": false, "data": { "errors": [{ "msg": "Enter valid class balance id", "path": "studentClassBalanceId" }] }, "message": "Validation Error" }
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `totalClasses` | integer | Recommended class count for next installment |
| `sellingPrice` | number/null | Recommended price (null if not calculated) |
| `currency` | string/null | Currency code (USD, INR, etc.) |

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Recommendation returned (may be empty `{}`) |
| 400 | Validation error or business rule violation |
| 500 | Database or service error |

---

## Logic Flow

### Controller (`controllers/v2/package-sale.js:230-247`)

1. Extract `studentClassBalanceId`, `studentId`, `courseId` from query
2. Call `RecommendationFacade.recommendedPackageToStudent(params)`
3. Return wrapped response

### Facade (`facades/v2/package-sale.js:3158-3298`)

**Path A — `studentClassBalanceId` provided (existing course):**
1. `ClassBalanceService.getStudentClassBalance({ id })` with Student + Parent joins
2. Validate class balance exists and is active
3. Check course eligibility — exclude SCHOLA courses, courses 3 and 11
4. Look up `ONOP_COURSE_PACKAGES` mapping to get `packageId`
5. Check `PackageGradeMappings.findOne({ grade, packageId })` for `total_classes` limit
6. Validate `total_booked_class < packageGradeMapping.total_classes` (else: "Already booked max classes")
7. `PackageSaleInitiatorService.checkPackageAlreadyRegisterByFilter({ packageId, studentId })`
   - If existing sale found: use existing sale payment amounts
   - If not found: analyze `PackageSaleService.getSoldPackagesOfCourse(...)` purchase history
8. Determine class quantity from history (or min 10 if last purchase ≤ 5 classes)
9. `NectedService.getWebsitePriceV2({ package_id, currency, grade })` → RPC pricing
10. Calculate `sellingPrice = rpc × totalClasses`

**Path B — `studentId` (+ optional `courseId`) provided (new course):**
1. Validate `ONOP_COURSE_PACKAGES[courseId]` mapping exists — return `{}` if not
2. `StudentService.getStudentByFilter({ id: studentId })` with Parent join
3. `PlatformService.getCountry(parentCountryId)` → currency info
4. `PlatformService.getCurrenciesByName(null, currencyId)` → currency name
5. Default `totalClasses = 10`
6. `NectedService.getWebsitePriceV2(...)` → RPC pricing; fallback: USD $120 for 10 classes
7. Return `{ totalClasses: 10, sellingPrice, currency }`

**Grade normalization:** Grade 0 → Grade 15 for package compatibility.

---

## Microservice Dependencies

| Service | Call | Trigger | Parallelism |
|---------|------|---------|-------------|
| ClassBalanceService | `getStudentClassBalance(...)` | Path A | Sequential |
| PackageSaleInitiatorService | `checkPackageAlreadyRegisterByFilter(...)` | Path A | Sequential |
| PackageSaleService | `getSoldPackagesOfCourse(...)` | Path A (no existing sale) | Sequential |
| StudentService | `getStudentByFilter(...)` | Path B | Sequential |
| PlatformService | `getCountry(countryId)` | Path B | Sequential |
| PlatformService | `getCurrenciesByName(...)` | Path B | Sequential |
| NectedService | `getWebsitePriceV2(...)` | Both paths | Sequential |

**All calls are sequential — no `Promise.all` used. Total: up to 6 sequential service calls.**

**Fallback:** If NectedService returns no pricing, defaults to `{ totalClasses: 10, sellingPrice: 120, currency: "USD" }`.

---

## Database & SQL Analysis

### Key Queries

```sql
-- Class balance with student + parent
SELECT scb.*, s.*, p.*
FROM student_class_balances scb
INNER JOIN students s ON scb.student_id = s.id
INNER JOIN parents p ON s.parent_id = p.id
WHERE scb.id = ? AND scb.active = 1;

-- Package grade availability
SELECT pgm.*, pgm.total_classes FROM package_grade_mappings pgm
WHERE pgm.grade = ? AND pgm.package_id = ?;

-- Student's sold packages (purchase history)
SELECT psi.*, sp.*, p.*
FROM package_sale_initiators psi
LEFT JOIN sale_payments sp ON psi.id = sp.package_sale_initiator_id
INNER JOIN packages p ON psi.package_id = p.id
WHERE psi.student_id = ? AND psi.course_id = ? AND psi.status != 'inactive'
ORDER BY psi.updated_at DESC;

-- Check existing package registration
SELECT psi.*, sp.* FROM package_sale_initiators psi
LEFT JOIN sale_payments sp ON psi.id = sp.package_sale_initiator_id
WHERE psi.package_id = ? AND psi.student_id = ? AND psi.category = ?;
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `student_class_balances` | Learning progress and booked class count |
| `package_grade_mappings` | Max class limits per package/grade |
| `package_sale_initiators` | Purchase history and existing registrations |
| `sale_payments` | Payment amounts for pricing analysis |
| `packages` | Package metadata |
| `students` | Student grade for package compatibility |
| `parents` | Parent country for currency localization |

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | All 6 service calls are sequential — should use `Promise.all` where independent | Facade | 300–800ms cumulative latency |
| 2 | No result caching — same recommendation recalculated on every request | Facade | Unnecessary DB/service load |
| 3 | No authentication — pricing data for any student accessible publicly | Router | Data exposure |
| 4 | NectedService is critical dependency with no circuit breaker — failure propagates | Pricing calculation | Feature outage when NectedService down |

### Low Priority

| # | Issue |
|---|-------|
| 5 | Course exclusions hardcoded (`SCHOLA_COURSES`, courses 3 and 11) — not configurable |
| 6 | `ONOP_COURSE_PACKAGES` mapping hardcoded — requires deploy to update |
| 7 | Fallback pricing ($120 / 10 classes in USD) hardcoded |
| 8 | Large facade method with multiple nested conditionals — high complexity |

---

## Test Scenarios

### Functional
- `studentClassBalanceId` for existing course with purchase history → recommendation uses historical pricing
- `studentClassBalanceId` for student without existing sale → fresh package recommendation
- `studentId` + `courseId` for new enrollment → defaults to 10 classes
- `studentId` without `courseId` → behavior (no mapping → empty `{}`)

### Business Logic
- Course in SCHOLA_COURSES exclusion list → return `{}`
- Course IDs 3 or 11 → return `{}`
- Student at max booked classes → 400 "Already booked max classes"
- Last purchase was ≤ 5 classes → recommendation bumped to 10 classes
- Grade 0 student → grade 15 used for package lookup

### External Service
- NectedService unavailable → fallback to $120 / 10 classes (USD)
- PlatformService unavailable → country/currency fails (no graceful fallback currently)

### Validation
- `studentClassBalanceId` = 0 → 400
- Non-existent `studentClassBalanceId` → 400 "Enter valid Student Class Balance Id!"
- Non-existent `studentId` → service error

### Security
- Any caller can get pricing recommendations for any student (no auth)
- Pricing data disclosure via enumeration

### Edge Cases
- Student in country with unsupported currency
- Package grade mapping missing for student grade
- Student with zero purchase history for course
- Extremely large `total_booked_class` count
