---
endpoint: POST /v1/unified-data/sale-payments
service: eklavya
source_id: e9b4f90c-e1e1-4341-89c3-762c64463ad0
original_source_name: sale-payments
controller: controllers/unified-data.js:10
service_file: services/unified-data.js:153
router_file: routers/unified-data.js:41-47
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/unified-data/sale-payments

## Summary

Dynamic database query API for the `sale_payments` table. Identical architecture to the `/v1/unified-data/students` endpoint but targets the `SalePayment` model. Supports arbitrary Sequelize-compatible filtering, nested includes (e.g., `PackageSaleInitiator → Student → Parent`), attribute selection, ordering, and pagination over financial payment data.

**Category:** Internal API
**Owner/Team:** Finance Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/unified-data/sale-payments`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Request Body

**Validation source:** `validators/unified-data.js:10-12`

| Field | Required | Description |
|-------|----------|-------------|
| `relations.SalePayment` | Yes | Must exist; contains full query specification |

```json
{
  "relations": {
    "SalePayment": {
      "where": { ... },
      "include": [ ... ],
      "attributes": [ ... ],
      "order": [ ... ],
      "limit": 10,
      "offset": 0,
      "subQuery": false
    }
  }
}
```

### Key `sale_payments` Table Columns

`id`, `package_sale_initiator_id`, `amount`, `status`, `payment_date`, `payment_initiation_id`, `currency`, `payment_method`, `transaction_id`, `receipt_no`, `created_at`, `updated_at`

### Request Examples

**Basic status filter:**
```json
{ "relations": { "SalePayment": { "where": { "status": "completed" } } } }
```

**Amount range with PackageSaleInitiator:**
```json
{
  "relations": {
    "SalePayment": {
      "where": { "amount": { "gte": 1000 }, "status": { "in": ["completed","pending"] } },
      "include": ["PackageSaleInitiator"],
      "limit": 50
    }
  }
}
```

**Complex query with student data:**
```json
{
  "relations": {
    "SalePayment": {
      "where": { "payment_date": { "between": ["2024-01-01","2024-03-31"] }, "status": "completed" },
      "include": [
        { "entity": "PackageSaleInitiator",
          "include": [{ "entity": "Student", "attributes": ["id","name","grade"], "include": ["Parent"] }] }
      ],
      "attributes": ["id","package_sale_initiator_id","amount","status","payment_date"],
      "order": [["payment_date","DESC"]],
      "limit": 100
    }
  }
}
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    { "id": 789, "package_sale_initiator_id": 456, "amount": 1500.00,
      "status": "completed", "payment_date": "2024-02-15T10:30:00.000Z",
      "currency": "USD", "payment_method": "credit_card",
      "PackageSaleInitiator": {
        "id": 456, "student_id": 123, "category": "coding", "status": "active",
        "Student": { "id": 123, "name": "John Doe", "Parent": { "id": 321, "name": "Jane Doe" } }
      }
    }
  ],
  "message": "Data fetched successfully."
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request — invalid relations structure |
| 401 | Unauthorized |
| 500 | Internal server error |

---

## Logic Flow

Identical to `/v1/unified-data/students` — same controller, same service, different primary model:

1. Controller passes body as `query` to `UnifiedDataService.getUnifiedData()`
2. Service calls `_buildInclude(query, this.db)` to parse operators and relations
3. Extracts `SalePayment` as primary model; executes `this.db.SalePayment.findAll({ where, include, ... })`
4. Returns raw results

---

## Microservice Dependencies

**None.** Database-only. No payment gateway calls, no external service dependencies.

---

## Database & SQL Analysis

### Example Generated SQL

```sql
-- Basic
SELECT * FROM sale_payments WHERE status = 'completed' AND amount >= 1000 LIMIT 10 OFFSET 0;

-- With relations
SELECT sp.*, psi.id, psi.student_id, s.name
FROM sale_payments sp
INNER JOIN package_sale_initiators psi ON sp.package_sale_initiator_id = psi.id
INNER JOIN students s ON psi.student_id = s.id
WHERE sp.payment_date BETWEEN '2024-01-01' AND '2024-03-31'
  AND sp.status = 'completed'
ORDER BY sp.payment_date DESC
LIMIT 100 OFFSET 0;
```

### Common Related Tables

| Table | Relationship |
|-------|-------------|
| `package_sale_initiators` | FK: `package_sale_initiator_id` |
| `students` | Via `PackageSaleInitiator` |
| `parents` | Via `Student` |
| `packages` | Via `PackageSaleInitiator` |
| `sale_payment_audit_trial` | Audit trail |

### Recommended Indexes

```sql
CREATE INDEX idx_sale_payments_status ON sale_payments(status);
CREATE INDEX idx_sale_payments_payment_date ON sale_payments(payment_date);
CREATE INDEX idx_sale_payments_amount ON sale_payments(amount);
CREATE INDEX idx_sale_payments_psi_id ON sale_payments(package_sale_initiator_id);
CREATE INDEX idx_sale_payments_status_date ON sale_payments(status, payment_date);
CREATE INDEX idx_sale_payments_psi_status ON sale_payments(package_sale_initiator_id, status);
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Unrestricted access to sensitive financial data — no role-based access control or field masking | `services/unified-data.js:153-176` | Financial data exposure |
| 2 | Default limit 10 can be overridden to any value; no enforced maximum | `services/unified-data.js:139` | Unbounded payment data dumps |
| 3 | No audit logging of payment data access | Service layer | No compliance audit trail |

### Medium Priority

| # | Issue |
|---|-------|
| 4 | Date range queries may cause full table scans without proper compound indexes |
| 5 | Only validates `relations.SalePayment` exists — no structural validation |

---

## Test Scenarios

### Functional
- Basic payment status filter
- Amount range queries
- Date range filtering
- Complex payment-to-student relationship queries
- PackageSaleInitiator joins
- Payment method filtering

### Security
- Unauthorized access attempts
- Large `limit` values
- Sensitive payment field exposure audit
- Payment data enumeration attempts

### Performance
- Large payment dataset queries
- Complex multi-table joins
- Date range query performance
- Concurrent payment data access

### Financial Data Correctness
- Payment status accuracy
- Amount calculation precision
- Currency field handling
- Transaction ID uniqueness checks
