---
endpoint: POST /v1/package-payment
service: eklavya
source_id: d9737249-9bd0-4fea-b787-68f45744040d
original_source_name: package-payment
controller: controllers/package-sale.js:209
service_file: services/package-sale.js:1006
router_file: routers/package-sale.js:81
auth: None
security_flag: "⚠️ AUTH_DISABLED"
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/package-payment

## Summary

Retrieves comprehensive payment details for a package purchase (and optionally addon materials) using a Base64-encoded payment initiation reference. Decodes the payload to extract `payment_initiation_id`, then aggregates data across package sales, addon material sales, sale payment distributions, student/parent records, and regional data from the Platform service. Returns a fully enriched response including installment breakdown, payment status (OPEN/PAID/EXPIRED), and parent metadata for payment gateway rendering. No authentication required.

**Category:** Payment Management API — Payment Information Retrieval
**Owner/Team:** Package Sales & Payment Management Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/package-payment`
**Authentication:** None

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded JSON containing `payment_initiation_id` (and optionally `expiry`) |

**Decoded data structure:**
```json
{ "payment_initiation_id": 12345, "expiry": "2024-12-31T23:59:59.000Z" }
```

### Request Examples

```json
{ "data": "eyJwYXltZW50X2luaXRpYXRpb25faWQiOjEyMzQ1fQ==" }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "totalPaymentAmount": "299.99",
    "totalPackageAmount": "249.99",
    "totalAddonMaterialAmount": "50.00",
    "packagePaymentDetails": [{
      "original_selling_price": 300.00,
      "discount": 50.01,
      "total_price": 249.99,
      "selling_price": 249.99,
      "student_id": 123,
      "plan_type": "installment",
      "course_id": 5,
      "total_classes": 20,
      "Package": { "type": "course_package", "display_name": "Python Programming Course", "total_classes": 20, "internal_name": "python_basics_v2" },
      "SalePayments": [{
        "id": 456, "amount": 124.99, "currency": "USD", "status": "open",
        "total_classes": 10, "payment_type": "one_time", "discount": 25.01,
        "subscription_interval": null,
        "SalePaymentDistributions": [{ "price": 100.00, "type": "course_fee" }, { "price": 24.99, "type": "platform_fee" }]
      }]
    }],
    "addonMaterialPaymentDetails": [],
    "students": [{ "id": 123, "name": "John Doe Jr", "parentId": 456, "grade": 8, "referralCode": "STU_123_REF" }],
    "parent": { "id": 456, "name": "John Doe Sr", "email": "john.doe@example.com", "phone": "+1234567890", "countryId": 1, "country": { "dial_code": "+1", "short_code": "US", "id": 1 } },
    "metaData": { "countryId": 1, "country": "United States", "countryShortCode": "US", "phone": "+1234567890", "email": "john.doe@example.com", "firstName": "John Doe Sr", "lastName": "", "noOfIntallment": "", "packageName": "python_basics_v2" },
    "paymentInitiationId": 12345,
    "paymentStatus": "open",
    "expiry": "2024-12-31T23:59:59.000Z"
  },
  "message": "payment details fetched successfully."
}
```

**Payment not found (404):**
```json
{ "success": false, "data": null, "message": "payment initiation - 99999 - provided is not attached to any package sale initiator", "error": "ValidationError" }
```

**Missing payment_initiation_id (400):**
```json
{ "success": false, "data": null, "message": "payment_initiation_id is required", "error": "BaseError" }
```

**Invalid Base64 (500):**
```json
{ "success": false, "data": null, "message": "error in getPackagePaymentDetails: Unexpected token", "error": "DatabaseError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Payment details retrieved |
| 400 | Invalid encoded data or missing payment_initiation_id |
| 404 | Payment initiation not attached to any package or addon |
| 500 | Database or processing error |

### Payment Status Logic

| Status | Condition |
|--------|-----------|
| `paid` | All associated sale payments have `status = 'paid'` |
| `expired` | Current time is after expiry date |
| `open` | Active payment within expiry with unpaid installments |

---

## Logic Flow

### Controller (`controllers/package-sale.js:209-224`)

1. Extract `data` (Base64 string) from request body
2. Call `PackageSaleService.getPackagePaymentDetails(encodedData)`
3. Wrap in `ApiResponse` and return

### Service (`services/package-sale.js:1006-1142`)

**Phase 1 — Decode:**
1. `Buffer.from(data, 'base64').toString()` → parse JSON → extract `payment_initiation_id`
2. Validate `payment_initiation_id` present; throw `BaseError` if missing

**Phase 2 — Payment structure:**
3. `PaymentStructureService.getPaymentData({ id: paymentInitiationId })` — retrieves expiry

**Phase 3 — Package data:**
4. `PackageSaleInitiator.findAll` where joined `SalePayment.payment_initiation_id = ?`, excluding `cancelled` payments
   - Eager-loads: `Package`, `SalePayment` → `SalePaymentDistribution`

**Phase 4 — Addon material data:**
5. `AddonMaterialSaleInitiator.findAll` where joined payment initiation ID
   - Eager-loads: `AddonMaterial`, `AddonMaterialSalePayment`

**Phase 5 — Student & parent:**
6. Extract unique student IDs from both collections
7. `Student.findAll({ where: { id: studentIds } })` with Parent include
8. `PlatformService.getAllCountries()` for country enrichment

**Phase 6 — Format response:**
9. Calculate `totalPackageAmount`, `totalAddonMaterialAmount`, `totalPaymentAmount`
10. Determine `paymentStatus` from expiry and payment states
11. Build `metaData` with parent contact info for payment gateway

---

## Microservice Dependencies

| Service | Call | Trigger |
|---------|------|---------|
| PaymentStructureService | `getPaymentData({ id })` | Always |
| PlatformService | `getAllCountries()` | Always |

**Both calls are sequential — should be parallelized.**

---

## Database & SQL Analysis

### Key Queries

```sql
-- Package payment details (multi-join)
SELECT psi.original_selling_price, psi.discount, psi.total_price, psi.selling_price,
       psi.student_id, psi.plan_type, psi.course_id,
       p.type, p.display_name, p.total_classes, p.internal_name,
       sp.id, sp.amount, sp.currency, sp.status, sp.total_classes, sp.payment_type, sp.discount,
       spd.price, spd.type
FROM package_sale_initiators psi
INNER JOIN packages p ON psi.package_id = p.id
INNER JOIN sale_payments sp ON psi.id = sp.package_sale_initiator_id
LEFT JOIN sale_payment_distributions spd ON sp.id = spd.sale_payment_id
WHERE sp.payment_initiation_id = ?
  AND sp.status != 'cancelled';

-- Addon material details
SELECT amsi.*, am.displayName, am.totalItems, am.type,
       amsp.id, amsp.amount, amsp.currency, amsp.status
FROM addon_material_sale_initiators amsi
INNER JOIN addon_materials am ON amsi.addon_material_id = am.id
INNER JOIN addon_material_sale_payments amsp ON amsi.id = amsp.addon_material_sale_initiator_id
WHERE amsp.paymentInitiationId = ?;

-- Student details
SELECT * FROM students WHERE id IN (?, ?);
SELECT * FROM parents WHERE id = ?;
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `package_sale_initiators` | Core package purchase records |
| `sale_payments` | Payment installments |
| `sale_payment_distributions` | Installment breakdown (course fee / platform fee) |
| `packages` | Package metadata |
| `addon_material_sale_initiators` | Addon material purchases |
| `addon_material_sale_payments` | Addon payment installments |
| `addon_materials` | Addon metadata |
| `students` | Student info |
| `parents` | Parent/customer info |

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | 4-5 sequential DB queries per request | Service | 200–400ms latency |
| 2 | PaymentStructureService and PlatformService calls are sequential — should be `Promise.all` | Service | Extra latency per external call |
| 3 | No request body validation middleware — malformed Base64 reaches service and throws parse error | Router | Generic 500 instead of 400 |
| 4 | No authentication — payment details (amounts, student/parent PII) exposed to unauthenticated callers | Router | Data exposure risk |

### Low Priority

| # | Issue |
|---|-------|
| 5 | Payment status strings hardcoded — should use constants |
| 6 | Error messages expose internal IDs and table structure |
| 7 | No caching for `getAllCountries()` — fetched on every request |

---

## Test Scenarios

### Functional
- Valid Base64 with package-only payment → full response
- Valid Base64 with package + addon material → combined totals
- Multiple students in single payment initiation
- Installment plan (multiple SalePayments) vs one-time
- Subscription payment with `subscription_interval`

### Business Logic
- All payments paid → `paymentStatus = 'paid'`
- Expiry in past → `paymentStatus = 'expired'`
- Mix of paid and unpaid → `paymentStatus = 'open'`
- Cancelled payments excluded from response

### Validation
- Missing `data` field → 400/500
- Valid Base64 but missing `payment_initiation_id` in JSON → 400
- Non-existent `payment_initiation_id` → 404
- Corrupted Base64 → 500

### Security
- Unauthenticated access to any payment initiation (currently succeeds)
- Large Base64 payload
- SQL injection via decoded JSON values

### Edge Cases
- Payment with zero amounts
- Addon materials with zero items
- Students with missing parent record
- Payment spanning multiple currencies
