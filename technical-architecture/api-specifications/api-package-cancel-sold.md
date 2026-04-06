---
endpoint: POST /v1/cancel-sold-package
service: eklavya
source_id: 8f06f04b-6e73-48c4-907c-b85ac048957c
original_source_name: cancel-sold-package
controller: controllers/package-sale.js:173
service_file: services/package-sale.js:861
router_file: routers/package-sale.js:63
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/cancel-sold-package

## Summary

Cancels a sold package by transitioning its status to `inactive`, cancelling all unpaid sale payments, expiring associated payment initiations (via the Payment microservice), and optionally restoring a parent package when the cancellation is an upgrade/downgrade rollback. All mutations execute within a single database transaction. The endpoint correctly blocks cancellation if any installment has already been paid. No authentication required.

**Category:** Package Management API — Package Cancellation System
**Owner/Team:** Package Sales & Payment Management Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/cancel-sold-package`
**Authentication:** None

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packageSaleId` | integer | Yes | ID of the package sale initiator to cancel |
| `studentId` | integer | Yes | Student associated with the package sale |

### Request Examples

```json
{ "packageSaleId": 123, "studentId": 456 }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "packageSaleId": 123,
    "status": "inactive",
    "cancelledPayments": 3,
    "refundedAmount": 1500.00,
    "currency": "USD",
    "cancellationTimestamp": "2024-11-26T15:30:00.000Z"
  },
  "message": "Sold Package cancelled successfully successfully."
}
```

**Already paid (400):**
```json
{ "success": false, "data": null, "message": "Sale payment already paid for package id: 123", "error": "ValidationError" }
```

**Not found (404):**
```json
{ "success": false, "data": null, "message": "Package sale not found", "error": "ValidationError" }
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "Validation failed", "errors": [{ "field": "packageSaleId", "message": "packageSaleId should be an integer" }] }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Package cancelled successfully |
| 400 | Validation error or paid payments block cancellation |
| 404 | Package sale initiator not found |
| 500 | Database or transaction error |

---

## Logic Flow

### Controller (`controllers/package-sale.js:173-186`)

1. Extract `packageSaleId` from request body
2. Call `PackageSaleService.cancelSoldPackage(packageSaleId)`
3. Wrap in `ApiResponse` and return

### Service (`services/package-sale.js:861-972`)

**Phase 1 — Validation:**
1. `checkPackageSalePresence(packageSaleId)` — fetch full record with relationships; throw if not found
2. Query `sale_payments` for `status = 'paid'` — throw `ValidationError` if any exist

**Phase 2 — Transaction-scoped mutations (all within `sequelize.transaction`):**
3. `UPDATE package_sale_initiators SET status = 'inactive'`; set `auto_pay_status = 'cancelled'` if `is_auto_pay_opt = 1`
4. `UPDATE sale_payments SET status = 'cancelled'` where `status IN ('open', 'upcoming')`
5. Collect `payment_initiation_id` values from cancelled payments

**Phase 3 — Payment gateway cleanup (within transaction):**
6. Non-auto-pay: call `PaymentService.expirePaymentInitiation(ids)` per initiation
7. Auto-pay: call `PaymentService.expireSubscriptionPaymentInitiation({ ids, packageSaleData })`
8. Payment service failures are logged but do not roll back the transaction

**Phase 4 — Package hierarchy restoration:**
9. If `parent_sale_initiator_id` exists (upgrade/downgrade scenario): reactivate parent package, restore forwarded payments to `open`

**Phase 5 — Rock bottom cleanup:**
10. Call `inactiveRockBottomViolation` — removes pricing rule violation records for this package

---

## Microservice Dependencies

| Service | Call | Trigger | Failure handling |
|---------|------|---------|-----------------|
| Payment microservice | `expirePaymentInitiation(ids)` | Non-auto-pay packages | Logged, does not block cancellation |
| Payment microservice | `expireSubscriptionPaymentInitiation({ ids, packageSaleData })` | Auto-pay packages | Logged, does not block cancellation |

**No other external HTTP calls.**

---

## Database & SQL Analysis

### Key Queries

```sql
-- Validation: check for paid payments
SELECT COUNT(*) FROM sale_payments
WHERE package_sale_initiator_id = ? AND status = 'paid';

-- Cancel package
UPDATE package_sale_initiators
SET status = 'inactive',
    auto_pay_status = CASE WHEN is_auto_pay_opt = 1 THEN 'cancelled' ELSE auto_pay_status END,
    updated_at = NOW()
WHERE id = ?;

-- Cancel unpaid payments
UPDATE sale_payments
SET status = 'cancelled', updated_at = NOW()
WHERE package_sale_initiator_id = ? AND status IN ('open', 'upcoming');

-- Restore parent package (upgrade/downgrade rollback)
UPDATE package_sale_initiators SET status = 'active', updated_at = NOW() WHERE id = ?;
UPDATE sale_payments SET status = 'open', updated_at = NOW()
WHERE package_sale_initiator_id = ? AND status = 'forwarded';
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `package_sale_initiators` | Primary — status transitions, auto-pay, parent chain |
| `sale_payments` | Cancel unpaid installments; restore forwarded payments |
| `packages` | Package type for business logic (n1p1 vs regular) |
| `payment_initiations` | External gateway references for expiry |
| `rock_bottom_violations` | Pricing rule cleanup |

### Transaction Analysis

This endpoint has strong transaction design:
- Explicit `sequelize.transaction()` boundary around all DB mutations
- Automatic rollback on any DB failure
- ACID-compliant status transitions across multiple tables

**Known issue:** Payment service calls execute inside the transaction boundary — a slow payment service extends transaction hold time and increases deadlock risk.

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Payment service calls inside DB transaction — slow payment gateway extends lock hold time | `cancelSoldPackage` | Increased deadlock risk; long-running transactions |
| 2 | Payment service failures silently logged — orphaned payment initiations if gateway not cleaned up | Error handling in service | Dangling payment links in gateway |
| 3 | No cancellation reason captured — cannot track why packages are cancelled | Request body | Missing business analytics |

### Low Priority

| # | Issue |
|---|-------|
| 4 | Status strings hardcoded (`'inactive'`, `'cancelled'`, `'open'`) — should use imported constants |
| 5 | Complex nested conditionals for auto-pay and package type handling increase maintenance burden |
| 6 | Limited audit logging — no structured log of which payments were cancelled or amounts involved |
| 7 | No authentication — any caller can cancel any package for any student |

---

## Test Scenarios

### Functional
- Valid package cancellation with 3 unpaid installments
- Auto-pay package cancellation — subscription payment initiation expired
- Package with `parent_sale_initiator_id` — verify parent package reactivated
- N1P1 package type cancellation
- Demo package cancellation

### Business Logic
- Package with one paid payment → blocked with 400
- Package not found → 404
- `packageSaleId` is zero or negative → 400 validation
- Package already in `inactive` status → behavior

### Transaction / Database
- Concurrent cancellation of same packageSaleId — only one should succeed
- Database failure mid-transaction → rollback verified
- Payment service timeout during cancellation → transaction outcome

### Security
- Cross-student package access (no auth currently)
- SQL injection in `packageSaleId`
- Oversized payload

### Edge Cases
- Package with zero unpaid payments (only upcoming)
- Package with forwarded payments (upgrade scenario)
- Payment initiations already expired in gateway
- Rock bottom violation cleanup failure
