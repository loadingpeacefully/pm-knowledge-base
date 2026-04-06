---
endpoint: POST /v1/student-credit-transfer/request
service: eklavya
source_id: 40621b34-d8bd-471a-be12-1f76a3ae0bbb
original_source_name: request
controller: controllers/student-credit-transfer.js:25
service_file: facades/student-credit-transfer.js:89 / services/student-credit-transfer.js:54
router_file: routers/student-credit-transfer.js:21
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/student-credit-transfer/request

## Summary

Creates a student credit transfer request to move classes, gems, or diamonds between students. Supports three credit types with distinct validation rules. Class transfers are the most complex — they require course/class type mapping and rate-per-class (RPC) pricing calculations. No authentication required. Contains a known race condition in duplicate request checking and missing database transaction boundaries.

**Category:** Student Management API — Credit Transfer System
**Owner/Team:** Student Credit Management Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/student-credit-transfer/request`
**Authentication:** None

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fromStudentId` | integer (≥1) | Yes | Source student ID |
| `toStudentId` | integer (≥1) | Yes | Destination student ID |
| `creditType` | string | Yes | `"class"`, `"diamond"`, `"gem"` |
| `fromQuantity` | integer (≥1) | Yes | Credits to transfer from source |
| `toQuantity` | integer (≥1) | Yes | Credits to add to destination |
| `createdBy` | string | Yes | Email/identifier of requester |
| `fromCourseId` | integer | If class | Source course ID |
| `toCourseId` | integer | If class | Destination course ID |
| `fromClassType` | string | If class | Source class type |
| `toClassType` | string | If class | Destination class type |
| `toHubId` | integer | If offline/onlineGroup | Hub ID for group/offline transfers |
| `reason` | string | No | Optional reason |
| `skipClassTypeRestrictionCheck` | boolean | No | Override offline/group → online restriction |

**Class types:** `online`, `onlineGroup` (requires `toHubId`), `offline` (requires `toHubId`)

### Request Examples

```json
// Class transfer
{ "fromStudentId": 123, "toStudentId": 456, "fromCourseId": 5, "toCourseId": 8,
  "creditType": "class", "fromQuantity": 10, "toQuantity": 8,
  "fromClassType": "online", "toClassType": "onlineGroup", "toHubId": 5,
  "createdBy": "admin@brightchamps.com" }

// Diamond transfer
{ "fromStudentId": 789, "toStudentId": 101, "creditType": "diamond",
  "fromQuantity": 50, "toQuantity": 50, "createdBy": "parent@example.com" }

// Gem transfer
{ "fromStudentId": 111, "toStudentId": 222, "creditType": "gem",
  "fromQuantity": 100, "toQuantity": 100, "createdBy": "support@brightchamps.com" }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "id": 789, "fromStudentId": 123, "toStudentId": 456,
    "fromCourseId": 5, "toCourseId": 8,
    "creditType": "class", "fromQuantity": 10, "toQuantity": 8,
    "fromStudentClassBalanceId": 234, "toStudentClassBalanceId": null,
    "fromClassType": "online", "toClassType": "onlineGroup",
    "toRpc": 125.50, "toHubId": 5, "status": "requested",
    "createdAt": "2024-11-26T15:30:00.000Z"
  },
  "message": "student credit transfer request submitted successfully."
}
```

**Insufficient balance (400):**
```json
{ "success": false, "data": null, "message": "Insufficient balance", "error": "ValidationError" }
```

**Existing request (400):**
```json
{ "success": false, "data": null, "message": "Request already exists for the student - Reject the old Request and try again", "error": "ValidationError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success — request created |
| 400 | Validation error or business rule violation |
| 500 | Database or processing error |

---

## Logic Flow

### Controller (`controllers/student-credit-transfer.js:25-39`)

1. Extract all body params
2. Call `StudentCreditTransferFacade.postStudentCreditTransfer(data)`
3. Return via `ApiResponse` wrapper

### Facade — Phase 1: Input Validation (`facades/student-credit-transfer.js:89-295`)

1. **Class type restriction:** block offline/onlineGroup → online transfers (overridable via `skipClassTypeRestrictionCheck`)
2. **Credit-type validation:**
   - **Class:** fetch source class balance, verify `total_paid_class - total_completed_class >= fromQuantity`, calculate RPC = `paidAmount ÷ totalClasses`
   - **Diamond:** fetch `student_credits` where `type = 'diamond_credit'`, verify `totalCredits - creditsConsumed >= fromQuantity`
   - **Gem:** fetch `students.gems`, verify balance

### Facade — Phase 2: Transfer Request Creation

3. Build payload with `toRpc`, `toHubId`, credit type metadata
4. Call `StudentCreditTransferService.postCreditTransferRequest(payload)`

### Service (`services/student-credit-transfer.js:54-79`)

1. Check for existing REQUESTED or APPROVED transfer for `fromStudentId` → throw if found
2. `StudentCreditTransfer.create(payload)` with `status: "requested"`
3. Return created record

**RPC Formula:** `toRpc = (fromRpc × fromQuantity) ÷ toQuantity`

---

## Microservice Dependencies

**None** for request creation. All validation is database-only.

**Internal service chain:**
- `StudentService` — student, class balance, gem data
- `StudentCreditTransferService` — duplicate check + record creation
- `PackageSaleService` — payment history for RPC calculation (class type)
- `StudentCreditService` — diamond balance

---

## Database & SQL Analysis

### Key Queries

```sql
-- Class balance validation
SELECT * FROM student_class_balances WHERE student_id = ? AND course_id = ? AND class_type = ?;

-- Payment history for RPC
SELECT SUM(amount), COUNT(*) FROM sale_payments sp
JOIN package_sale_initiators psi ON sp.package_sale_initiator_id = psi.id
WHERE student_id = ? AND course_id = ? AND status = 'paid';

-- Diamond balance
SELECT * FROM student_credits WHERE student_id = ? AND type = 'diamond_credit';

-- Gem balance
SELECT gems FROM students WHERE id = ?;

-- Duplicate check
SELECT * FROM student_credit_transfers WHERE from_student_id = ? AND status IN ('requested','approved');

-- Create
INSERT INTO student_credit_transfers (..., status) VALUES (..., 'requested');
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `student_credit_transfers` | Primary — create + duplicate check |
| `students` | Gem balance |
| `student_class_balances` | Class credit validation |
| `student_credits` | Diamond balance |
| `package_sale_initiators` | RPC calculation |
| `sale_payments` | Payment amounts for RPC |

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No database transaction — gem update and claim record are separate operations; partial failure leaves inconsistent state | Facade performs sequential service calls | Data corruption risk |
| 2 | Race condition in duplicate check — time gap between `SELECT` check and `INSERT` allows concurrent duplicate requests | `postCreditTransferRequest` | Multiple concurrent active requests per student |

### Medium Priority

| # | Issue | Impact |
|---|-------|--------|
| 3 | 5–8 sequential DB queries per validation (class type) | High latency: 300–500ms for class transfers |
| 4 | "Insufficient balance" error gives no details (available vs requested) | Poor UX for troubleshooting |
| 5 | No maximum quantity limit in validator | Unrealistic transfer amounts possible |

### Low Priority

| # | Issue |
|---|-------|
| 6 | Class type restriction is hardcoded (not configurable) |
| 7 | No request expiration — stale "requested" status blocks future transfers indefinitely |
| 8 | No audit logging of validation steps |

---

## Test Scenarios

### Functional
- Class transfer between different students
- Class transfer same student, different courses (self-transfer)
- Diamond transfer
- Gem transfer
- `toClassType = "onlineGroup"` with `toHubId`
- Override class type restriction via `skipClassTypeRestrictionCheck`
- Transfer with optional `reason`

### Business Logic
- Insufficient class balance → 400
- Insufficient diamond credits
- Insufficient gems
- Duplicate active request → 400 "Request already exists"
- RPC calculation accuracy
- Self-transfer detection

### Race Condition
- Concurrent requests for same `fromStudentId` → only one should succeed

### Validation
- Missing required fields
- Invalid `creditType`
- Negative/zero quantities
- Missing `fromCourseId` when `creditType = "class"`
- Missing `toHubId` when `toClassType = "onlineGroup"`

### Security
- SQL injection via text fields
- Oversized payloads
- Cross-student unauthorized transfers (no auth currently)
