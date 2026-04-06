---
endpoint: POST /v1/student/bulk-installments
service: eklavya
source_id: 120028ae-3bef-463d-afb0-95890d8ce10c
original_source_name: bulk-installments
controller: controllers/students.js:775
service_file: facades/student.js:2099
router_file: routers/students.js:268-273
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/student/bulk-installments

## Summary

Fetches installment payment status for multiple student class balances in a single bulk call. For each balance, evaluates whether a payment installment is pending, completed, or not applicable, based on complex business rules (class type, paid vs. completed count, 14-day payment window, Schola course exclusions). Contains a notable side effect: may auto-create upgrade packages during a read operation.

**Category:** Internal API — Payment Management
**Owner/Team:** Payments / Finance Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/student/bulk-installments`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Request Body

**Validation source:** `validators/student.js:535-547`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentClassBalanceIds` | array[number] | Yes | Array of `student_class_balances.id` values; minimum 0 elements |

```json
{ "studentClassBalanceIds": [123, 456, 789] }
```

### Response Format

**Success — mixed statuses (200):**
```json
{
  "success": true,
  "data": [
    { "studentClassBalanceId": 123, "packageSaleInitiatorId": 456, "category": "online_regular",
      "salePaymentId": 789, "currency": "USD", "datetime": "2024-11-15T10:00:00.000Z",
      "balance": 8, "paymentAmount": 299.99, "referrerId": 101, "referrerType": "teacher",
      "remindersSent": 2, "status": "pending" },
    { "studentClassBalanceId": 456, "status": "no_installment" },
    { "studentClassBalanceId": 789, "status": "completed", "paidVia": "teacher" }
  ],
  "message": "Installments info fetched successfully"
}
```

**Empty array input (200):**
```json
{ "success": false, "data": [], "message": "Installments info fetched successfully" }
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "studentClassBalanceIds are required", "error": "ValidationError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request — validation failed |
| 401 | Unauthorized |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/students.js:775-788`)

1. Extract `studentClassBalanceIds` from request body
2. Call `StudentFacade.getBulkInstallmentStatus(studentClassBalanceIds)`
3. Format via `ApiResponse` wrapper

### Facade — Bulk Orchestration (`facades/student.js:2099-2127`)

1. Bulk-fetch all class balance records using `WHERE id IN (...)`
2. Iterate through each record:
   - Call `getInstallmentStatus({ studentClassBalanceId, referrerId: teacherId, referrerType: "teacher" })`
   - Catch individual errors; skip failed items (silent — not surfaced to caller)
3. Return array of successful results

### Facade — Individual Status (`facades/student.js:1960-2097`)

For each balance:

1. **Class type filter:**
   - Teacher referrers: online classes only
   - Other referrers: online + online-group + offline

2. **Eligibility checks:**
   - Balance must exist with valid class type
   - Exclude Schola courses and `course_id = 11`
   - Student must have remaining paid classes

3. **Auto-package creation (side effect!):**
   - If `totalBookedClass == totalPaidClass` AND not `course_id = 3`: call `packageCommon.createStudentUpgradePackage()`

4. **Payment status analysis:**
   - Fetch `PackageSaleInitiator` + `SalePayment` records
   - Check for open (unpaid) sale payments
   - Analyze 14-day payment history window

5. **Status determination:**
   - `NO_INSTALLMENT`: No eligible packages, Schola course, recent payment within 14 days, or >3 classes remaining
   - `COMPLETED`: Recent payment within 14 days AND >3 classes remaining
   - `PENDING`: Open sale payment exists and classes running low

6. **Reminder count:** query `payment_reminder_comm_logs` for open payment

---

## Microservice Dependencies

**None.** Database-only. No external HTTP calls.

**Internal service chain:**
- `ClassBalanceService` — class balance data
- `PackageSaleInitiationService` — package + payment data
- `PaymentService` — reminder logs
- `PackageCommon` — auto-package creation (side effect)

---

## Database & SQL Analysis

### Query Pattern (N+1 Problem)

| Step | Query | Frequency |
|------|-------|-----------|
| 1. Bulk class balance fetch | `SELECT * FROM student_class_balances WHERE id IN (...)` | 1x |
| 2. Individual class balance (per item) | `SELECT * FROM student_class_balances WHERE id = ? AND class_type IN (...)` | N× |
| 3. Package sale initiator (per item) | `SELECT psi.*, sp.* FROM package_sale_initiators psi JOIN sale_payments sp...` | N× |
| 4. Reminder logs (per item) | `SELECT * FROM payment_reminder_comm_logs WHERE sale_payment_id = ?` | N× |
| **Total** | | **1 + (N × 4–6) queries** |

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `student_class_balances` | Primary filtering |
| `package_sale_initiators` | Package status |
| `sale_payments` | Payment amounts and status |
| `payment_reminder_comm_logs` | Reminder count |
| `students` | Student data |
| `student_language_mappings` | Schola course logic |

### Recommended Indexes

```sql
CREATE INDEX idx_student_class_balances_id_type ON student_class_balances(id, class_type);
CREATE INDEX idx_psi_course_student_status ON package_sale_initiators(course_id, student_id, status);
CREATE INDEX idx_psi_category_autopay ON package_sale_initiators(category, is_auto_pay_opt);
CREATE INDEX idx_sale_payments_psi_status ON sale_payments(package_sale_initiator_id, status);
CREATE INDEX idx_sale_payments_datetime_status ON sale_payments(datetime, status);
CREATE INDEX idx_payment_reminder_logs_sale_referrer ON payment_reminder_comm_logs(sale_payment_id, referrer_type, referrer_id);
```

---

## Technical Issues

### Critical Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | N+1 query pattern — 10 balance IDs = ~50 DB queries | `facades/student.js:2109-2120` | Linear performance degradation |
| 2 | No batch size limit — array can be arbitrarily large | Validator | Timeout / memory exhaustion |
| 3 | Auto-package creation side effect inside a read operation | `facades/student.js:1999-2003` | Unexpected data mutations on GET-equivalent calls |

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 4 | Individual failures silently skipped — caller gets partial results with no error details | `facades/student.js:2117-2119` | Invisible partial failures |
| 5 | Sequential processing — no `Promise.all` across items | `facades/student.js:2109` | Linear latency scaling |
| 6 | Date comparison logic in application code (14-day window) | `facades/student.js:2025-2030` | Timezone edge cases |

### Medium Priority

| # | Issue |
|---|-------|
| 7 | Inconsistent response structure — some items have many fields, `no_installment` items have only status |
| 8 | Hardcoded business rule constants (3 classes, 14 days, excluded course IDs) scattered throughout |

---

## Test Scenarios

### Functional
- Single balance ID
- Multiple IDs with mixed statuses (pending / completed / no_installment)
- Empty array → empty data
- Non-existent balance IDs → excluded from result
- Schola courses → `no_installment`
- Student with open sale payment → `pending`
- Student with recent payment (within 14 days) → `completed`

### Business Logic
- Auto-package creation trigger: `totalBookedClass == totalPaidClass` AND not `course_id = 3`
- Class type filter: teacher vs other referrer
- 14-day window boundary conditions

### Performance
- 1, 10, 25, 50 IDs — response time and query count
- Concurrent batch requests
- DB connection pool utilization

### Error Handling
- DB connection failure mid-loop
- Individual student processing error — verify others still returned
- Large payload / oversized array

### Security
- Auth enforcement
- SQL injection via array elements
- Large payload DoS
