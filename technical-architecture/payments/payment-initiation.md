---
title: Payment Initiation
category: technical-architecture
subcategory: payments
source_id: 19f2063b
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Initiation

## Overview
Payment Initiation is the first step of the payment process. It creates a tracked entry in the `payment_initiations` table and then generates an aggregator-specific payment link via the `createV2` and `generatePaymentLink` functions in the Payment-Structure service.

## API Contract
**Endpoint 1:** `POST /v1/payment-initiation/create-payment`
- **Auth:** Internal service call (no explicit external auth documented; called by Eklavya `/v2/initiate-payment` or Prashashak-FE)
- **Request Body:**
```json
{
  "paymentInitiatorName": "string",
  "referrerId": "string",
  "aggregatorName": "string",
  "amount": "number",
  "currency": "string (USD|INR|AED|OMR|GBP|SAR|IDR)",
  "expiry": "ISO8601 datetime",
  "metaData": "object (additional aggregator-specific params)"
}
```
- **Response:** Returns the newly created `payment_initiation` record
- **Status Codes:** 200 OK, 400 Bad Request (aggregator validation fails), 500 Internal Server Error

**Endpoint 2:** `POST /v1/payment-initiation/payment-link`
- **Request:** `{ "paymentInitiationId": "string" }`
- **Response:** `{ "transactionId": "string", "paymentLink": "string" }`

## Logic Flow

### Controller Layer
- Receives `POST /v1/payment-initiation/create-payment` request
- Delegates to `createV2` function
- Returns the created `payment_initiation` object to caller
- Receives `POST /v1/payment-initiation/payment-link`
- Delegates to `generatePaymentLink` function
- Returns `{ transactionId, paymentLink }`

### Service/Facade Layer
**`createV2` function:**
1. Extract `aggregatorName` from request
2. Identify the aggregator (PayPal, Razorpay, Stripe, Tazapay, Xendit, Tabby, Splitit, Manual)
3. INSERT record into `payment_initiations` table with mapped fields
4. Validate aggregator-specific requirements against provided data; throw error if invalid
5. Return newly created `payment_initiation` record

**`generatePaymentLink` function:**
1. Fetch `payment_initiation` by `paymentInitiationId`
2. Call `getPaymentLink` method, passing: `planId`, `amount`, `currency`, `aggregatorId`, `aggregatorName`, `expiry`, `metaData`
3. Invoke aggregator's SDK/API to generate link
4. Return `transactionId` and `paymentLink`

### High-Level Design (HLD)
```
Caller (Eklavya or Prashashak-FE)
  → POST /v1/payment-initiation/create-payment
      → createV2()
          → SELECT aggregator by name
          → INSERT payment_initiations
          → Validate aggregator requirements
      → Return payment_initiation record
  → POST /v1/payment-initiation/payment-link
      → generatePaymentLink()
          → GET payment_initiations by id
          → getPaymentLink() → aggregator SDK
          → Return transactionId + paymentLink
```

## External Integrations
- **PayPal:** `POST https://api-m.sandbox.paypal.com/v2/invoicing/invoices` (via `createInvoice` → `createDraftInvoice` → `sendInvoice`)
- **Razorpay SDK:** Payment link creation with INR support
- **Stripe SDK:** Returns `plink_` prefixed transaction IDs, hosted checkout URL (`https://buy.stripe.com/...`)
- **Tabby API:** `POST https://api.tabby.ai/api/v2/checkout`
- **Tazapay API:** `POST https://api.tazapay.com/v1/checkout`
- **Xendit:** Payment link generation (IDR)
- **Splitit:** Installment checkout link generation

## Internal Service Dependencies
- **Eklavya:** Calls `POST /v2/initiate-payment` which triggers this service
- **Prashashak-FE:** Triggers via "Generate Payment Link" UI action

## Database Operations

### Tables Accessed
- `payment_initiations` — Primary write table

### SQL / ORM Queries
- INSERT into `payment_initiations`:
  - `payment_initiator_id` (from `paymentInitiatorName`)
  - `referrer_id`
  - `aggregator_id`
  - `amount`
  - `currency`
  - `expiry`
  - `additional_request_body` (stores `metaData`)

### Transactions
- Single INSERT; no multi-table transaction required at this stage

## Performance Analysis

### Good Practices
- Clean separation: initiation record creation is decoupled from link generation
- Aggregator validation happens before any external API call, failing fast on bad input

### Performance Concerns
- Synchronous aggregator API call during `generatePaymentLink` — latency depends on third-party response time
- No retry logic documented for failed aggregator calls

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No documented retry/backoff on aggregator link generation failure |
| Low | `metaData` stored as blob in `additional_request_body` — makes querying aggregator-specific data difficult |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add timeout configuration per aggregator with circuit breaker pattern
- Log aggregator response times for SLA monitoring

### Month 1 (Architectural)
- Add async payment link generation with polling endpoint to avoid synchronous wait on slow aggregators
- Normalize `additional_request_body` (metaData) into typed fields per aggregator

## Test Scenarios

### Functional Tests
- Create payment initiation with each supported aggregator
- `generatePaymentLink` returns valid URL for each aggregator
- Aggregator validation failure returns 400 with descriptive error

### Performance & Security Tests
- Simulate aggregator API timeout — verify graceful error response
- Verify `paymentInitiationId` cannot be replayed to generate multiple links

### Edge Cases
- `aggregatorName` not in supported list — error handling
- `expiry` in the past — validation check
- `currency` unsupported by selected aggregator — validation check
