---
endpoint: GET /v1/payment/transactions
service: eklavya
source_id: 6824fd7d-ce7c-4dc7-a4c5-e54b68a781e3
original_source_name: transactions
controller: controllers/payment.js:248
service_file: facades/payment.js:651
router_file: routers/payment.js:66
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/payment/transactions

## Summary

Retrieves a student's complete payment transaction history spanning package payments, addon material purchases, refunds, and credit transfers. Uses Base64-encoded student ID for downstream service calls. Fetches data from 7 services (5 in parallel via `Promise.all`), applies user timezone to all dates, resolves payment aggregator from the most recent paid transaction, and transforms all data into a unified chronological transaction list. No authentication required. No pagination — all transactions returned.

**Category:** Payment Management API — Transaction History Retrieval
**Owner/Team:** Payment Management & Transaction History Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/payment/transactions`
**Authentication:** None

### Query Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | integer (≥1) | Yes | Student ID for transaction history |

### Request Examples

```
GET /v1/payment/transactions?studentId=123
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "studentName": "John Doe Jr",
    "parentName": "John Doe Sr",
    "paymentAggregator": "razorpay",
    "transactions": [
      {
        "paymentInitiationId": 12345, "salePaymentId": 678, "courseId": 5,
        "status": "paid", "studentName": "John Doe Jr", "parentName": "John Doe Sr",
        "totalAmount": 299.99, "paymentCurrency": "USD",
        "paymentDate": "15 Jan 2025",
        "invoice": "https://invoice-link.com/inv123", "receiptNo": "RCP001234",
        "paymentDueExceededThreshold": false,
        "payments": [
          { "type": "classes", "count": 20, "displayText": "20 Classes for Python Programming Course" },
          { "type": "kit", "count": 1, "displayText": "Programming Starter Kit" }
        ]
      },
      {
        "paymentInitiationId": null, "status": "refunded",
        "totalAmount": 50.00, "paymentCurrency": "USD", "paymentDate": "10 Jan 2025",
        "payments": [{ "type": "refund", "count": 3, "displayText": "Refund for 3 Classes in Python Programming Course" }]
      },
      {
        "paymentInitiationId": null, "status": "transferred",
        "totalAmount": null, "paymentDate": "05 Jan 2025",
        "payments": [{ "type": "transfer", "count": 5, "displayText": "5 Classes transferred from JavaScript Course to Python Course" }]
      }
    ]
  },
  "message": "Payment Transaction Fetched Successfully."
}
```

**No transactions (200):**
```json
{ "success": true, "data": { "transactions": [] }, "message": "Payment Transaction Fetched Successfully." }
```

**Invalid studentId (400):**
```json
{ "success": false, "data": { "errors": [{ "msg": "studentId should be an integer", "path": "studentId", "location": "query" }] }, "message": "Validation Error" }
```

### Transaction Status Values

| Status | Meaning |
|--------|---------|
| `paid` | Payment collected |
| `due` | Payment due/upcoming |
| `refunded` | Refund processed |
| `transferred` | Credit transfer completed |

### Payment Item Types

| Type | Meaning |
|------|---------|
| `classes` | Course class allocation |
| `kit` | Physical/digital kit |
| `diamonds` | Addon material (diamonds) |
| `refund` | Refund transaction |
| `transfer` | Credit transfer |

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid or missing `studentId` |
| 500 | Internal error |

---

## Logic Flow

### Controller (`controllers/payment.js:248-261`)

1. Extract `studentId` from query
2. Call `PaymentFacade.getPaymentTransactionsByStudentId(studentId)`
3. Return wrapped response

### Facade (`facades/payment.js:651-732`)

**Phase 1 — Parallel data collection (`Promise.all`):**
1. Base64-encode `{ student_id: studentId }` for PackageFacadeV2
2. Run simultaneously:
   - `PackageFacadeV2.getPaymentDetails({ encodedData, fetchAllPayments: true })` — packages + addons
   - `RefundService.getRefunds({ studentId, status: ['partial_refunded', 'refunded'] })`
   - `StudentCreditTransferService.getStudentCreditTransferList({ studentId (OR), status: 'TRANSFERRED' })`
   - `PlatformService.getAlltimezones()`
   - `PlatformService.getAllCourse()`

**Phase 2 — Reference maps:**
3. Build `Map<timezoneId, timezone>` and `Map<courseId, course>`
4. Extract `studentClassBalanceId`s from credit transfers
5. `ClassBalanceService.fetchBulkRawClassBalances(ids)` — for transfer display context

**Phase 3 — Payment aggregator:**
6. Find latest paid transaction; `PaymentStructureService.getPaymentData({ id })` → extract aggregator name
7. Filter excluded aggregators (e.g. `"splitit"`)

**Phase 4 — Transformation (`facades/payment.js:455-649`):**
8. Group package payments by `paymentInitiationId` (paid) or `salePaymentId` (open/due)
9. Enrich with course name, kit items, receipt/invoice links
10. Append refund records
11. Append credit transfer records with direction-aware display text
12. Sort all transactions by date descending (newest first)

---

## Microservice Dependencies

| Service | Call | Parallelism | Failure impact |
|---------|------|-------------|----------------|
| PackageFacadeV2 | `getPaymentDetails(encodedData)` | `Promise.all` | Empty payment list |
| RefundService | `getRefunds({ studentId, status })` | `Promise.all` | No refund records |
| StudentCreditTransferService | `getStudentCreditTransferList(...)` | `Promise.all` | No transfer records |
| PlatformService | `getAlltimezones()` | `Promise.all` | Date formatting fails |
| PlatformService | `getAllCourse()` | `Promise.all` | Course names missing |
| ClassBalanceService | `fetchBulkRawClassBalances(ids)` | Sequential (after parallel) | Transfer context missing |
| PaymentStructureService | `getPaymentData({ id })` | Sequential (conditional) | Aggregator not determined |

**Total: 7 service calls per request (5 parallel, 2 sequential)**

---

## Database & SQL Analysis

### Key Queries (via PackageFacadeV2)

```sql
-- Package payments
SELECT psi.*, sp.*, spd.*, p.display_name, s.name, par.name
FROM package_sale_initiators psi
INNER JOIN sale_payments sp ON psi.id = sp.package_sale_initiator_id
LEFT JOIN sale_payment_distributions spd ON sp.id = spd.sale_payment_id
INNER JOIN packages p ON psi.package_id = p.id
INNER JOIN students s ON psi.student_id = s.id
INNER JOIN parents par ON s.parent_id = par.id
WHERE psi.student_id = ? AND sp.status IN ('paid', 'open', 'upcoming');

-- Refunds
SELECT * FROM refunds WHERE student_id = ? AND status IN ('partial_refunded', 'refunded')
ORDER BY refunded_date DESC;

-- Credit transfers (student as sender or receiver)
SELECT * FROM student_credit_transfers
WHERE (from_student_id = ? OR to_student_id = ?) AND status = 'transferred'
ORDER BY updated_at DESC;

-- Class balances for transfer context
SELECT * FROM student_class_balances WHERE class_balance_id IN (?, ?, ?);

-- Addon material payments
SELECT amsi.*, amsp.*, am.display_name
FROM addon_material_sale_initiators amsi
INNER JOIN addon_material_sale_payments amsp ON amsi.id = amsp.addon_material_sale_initiator_id
INNER JOIN addon_materials am ON amsi.addon_material_id = am.id
WHERE amsi.student_id = ? AND amsp.status = 'paid';
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `package_sale_initiators` | Package purchase records |
| `sale_payments` | Installment status |
| `sale_payment_distributions` | Fee breakdown (course fee / platform fee / kit) |
| `packages` | Package names |
| `addon_material_sale_initiators` | Addon purchases |
| `addon_material_sale_payments` | Addon payment status |
| `addon_materials` | Addon names |
| `refunds` | Refund records |
| `student_credit_transfers` | Transfer records |
| `student_class_balances` | Class balance context for transfers |
| `students` | Student name |
| `parents` | Parent name |

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No pagination — all transactions returned for a student | Facade | Large response + high memory for active students with many transactions |
| 2 | PlatformService timezone/course data fetched on every request — no caching | `Promise.all` block | 100–300ms unnecessary latency on every call |
| 3 | No authentication — any caller can access any student's payment history including amounts and parent PII | Router | Data exposure |

### Low Priority

| # | Issue |
|---|-------|
| 4 | 7 service calls per request — high failure surface area |
| 5 | `PaymentDueExceededThreshold` constant hardcoded — not configurable |
| 6 | Date formatting (`"DD MMM YYYY"`) hardcoded — not locale-aware |
| 7 | Complex in-memory data transformation for large datasets |

---

## Test Scenarios

### Functional
- Student with package payments only
- Student with package + addon material (diamond) payments
- Student with refunds
- Student with credit transfers (as sender and as receiver)
- Mixed transaction types in chronological order
- Student with no transactions → `{ transactions: [] }`

### Business Logic
- Payment due threshold: `paymentDueExceededThreshold = true` when due date is within threshold days
- Payment grouping by `paymentInitiationId` for paid; by `salePaymentId` for open
- Transfer display text direction: "transferred FROM X course" vs "received FROM X course"
- Timezone applied: all dates in student's timezone format `"DD MMM YYYY"`
- `paymentAggregator` from most recent paid transaction (excludes "splitit")

### Validation
- Missing `studentId` → 400
- Non-integer `studentId` → 400
- Negative/zero `studentId` → 400

### Security
- Unauthenticated access to any student's payment data (currently allowed)
- `studentId` enumeration to extract financial/PII data

### Performance
- Student with 100+ transactions — response time and size
- Parallel service call verification (5 should fire simultaneously)
- PlatformService cache miss vs hit impact

### Edge Cases
- Transactions in multiple currencies
- Credit transfers with missing class balance context
- Refunds with no matching package (orphaned refund)
- Payment aggregator changed between transactions (most recent used)
- Timezone DST transitions affecting date display
