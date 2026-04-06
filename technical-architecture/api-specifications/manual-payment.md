---
title: Manual Payment Flow
category: technical-architecture
subcategory: api-specifications
source_id: a924ec92-db12-4c7a-adfa-b65ea78b8ed1
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Manual Payment Flow

## Overview
Manual payments are processed by the operations team or Sales Managers (SMs) for cases where no payment gateway webhook is involved. Instead of going through a standard aggregator webhook route, the system directly calls the `receivePayment` function (the same function that webhook routes call), then marks the sale payment as paid and generates the invoice.

## API Contract

| Property | Value |
|----------|-------|
| Method | Internal / Ops-facing (no public endpoint documented) |
| Path | N/A — calls internal `receivePayment` function directly |
| Auth | Internal ops authorization |
| Content-Type | application/json |

**Payload:**
```json
{
  "planId": "string",
  "amount": 488,
  "currency": "USD",
  "aggregatorId": 8,
  "aggregatorName": "manual",
  "expiry": "2023-08-15 18:04:46",
  "countryId": 19,
  "country": "United States of America",
  "countryShortCode": "US",
  "phone": "5406232966",
  "email": "amnajahan0905@gmail.com",
  "firstName": "Amna",
  "lastName": "",
  "packageName": "Champion",
  "txnId": "1234",
  "paymentMethod": "Schola Bank",
  "businessAccountName": "Brightchamps Singapore"
}
```

**Updated Payment Transaction Info (after receivePayment):**
```json
{
  "payment_initiation_id": "101594",
  "payment_method": "Schola Bank",
  "amount": 488,
  "currency": "USD",
  "capture_status": "Manual_success",
  "status": "success",
  "response": { ... }
}
```

## Logic Flow

### Controller Layer
- No standard HTTP endpoint — triggered manually through ops tooling or SM dashboard.

### Service/Facade Layer
1. Ops team or SM provides the payment payload with `aggregatorName: "manual"`.
2. System calls `receivePayment(payload)` directly — bypassing any payment gateway webhook.
3. `receivePayment` updates `payment_transaction_info` with:
   - `capture_status: "Manual_success"`
   - `status: "success"`
4. Sale payment status is updated from `open` → `paid`.
5. Invoice is generated immediately.

### High-Level Design (HLD)
- Manual payments use `aggregatorId: 8` / `aggregatorName: "manual"` to identify themselves in the payment system.
- No webhook URL is configured for manual payments — the function call replaces the webhook route.
- `txnId` is manually provided (e.g., a bank reference number or internal ops reference).
- Invoice generation is synchronous with payment status update (unlike automated flows which may use SQS).

## External Integrations
- N/A — Manual payments intentionally bypass all external payment gateways.
- No webhook registration.

## Internal Service Dependencies
- **Payments Service** — `receivePayment` function processes the manual payment.
- **Invoice Generation** — Called directly after manual payment success.
- **Sale Payments** — Status updated from `open` to `paid`.

## Database Operations

### Tables Accessed
- `payment_transaction_info` — Updated: `capture_status`, `status`, `response`
- `sale_payments` — Updated: status from `open` to `paid`
- Invoice-related tables — New invoice record created

### SQL / ORM Queries
- `UPDATE payment_transaction_info SET capture_status = 'Manual_success', status = 'success', response = ? WHERE payment_initiation_id = ?`
- `UPDATE sale_payments SET status = 'paid' WHERE payment_initiation_id = ?`

### Transactions
- Manual payment and invoice generation should be atomic — if invoice generation fails, the payment status update should be rolled back (not explicitly documented in source).

## Performance Analysis

### Good Practices
- Reuses the same `receivePayment` function as automated webhook routes — consistent payment processing logic.
- Provides ops team with same invoice generation capability as automated flows.

### Performance Concerns
- No concurrency control — multiple ops users could submit manual payments for the same `planId` simultaneously.
- No idempotency key documented; duplicate `txnId` values could cause duplicate payment records.

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No idempotency check on `txnId` for manual payments — risk of double payment recording. |
| Medium | Manual `txnId` values like "1234" suggest weak validation in ops tooling. |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add unique constraint check on `txnId` within `payment_transaction_info` for manual payments.
- Add confirmation dialog in ops UI before submitting manual payment.

### Month 1 (Architectural)
- Build a dedicated manual payment audit log table to track all ops-submitted payments with submitter ID and timestamp.
- Implement optimistic locking on `payment_initiation_id` to prevent concurrent manual submissions for the same plan.

## Test Scenarios

### Functional Tests
- Submit manual payment with valid payload → verify `payment_transaction_info` updated with `Manual_success`.
- Verify sale payment status changes from `open` to `paid`.
- Verify invoice is generated after successful manual payment.

### Performance & Security Tests
- Verify only authorized ops/SM roles can trigger manual payments.
- Test duplicate submission of same `planId` — verify idempotency behavior.

### Edge Cases
- `aggregatorName` not set to "manual" — verify it falls through to webhook path.
- Missing required fields (e.g., no `txnId`) — verify validation behavior.
- Invoice generation failure after payment status update — verify rollback or retry mechanism.

## Async Jobs & Automation
- N/A — Manual payments are synchronous and do not use async queues or lambdas.
- Invoice generation is triggered synchronously within the `receivePayment` call path.
