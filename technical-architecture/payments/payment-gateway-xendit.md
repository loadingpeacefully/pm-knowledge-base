---
title: Payment Gateway – Xendit
category: technical-architecture
subcategory: payments
source_id: 015cc91c
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – Xendit

## Overview
Xendit is an Indonesian payment gateway used for IDR transactions. Payment links are generated via the Xendit API and payment confirmations are delivered via webhook (configured in the Xendit dashboard). Webhook payloads include nested charge details with `payment_intent.succeeded` event type.

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment`
- `POST /v1/payment-initiation/payment-link`

**Webhook Endpoints (Xendit → system):**
- Production: `https://api-services.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/xendit/create`
- Staging: `https://api-services-stage.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/xendit/create`

**Xendit Request Payload:**
```json
{
  "planId": "string",
  "amount": "number",
  "currency": "IDR",
  "aggregatorId": 6,
  "aggregatorName": "xendit",
  "expiry": "datetime",
  "metaData": "object"
}
```

**Xendit Response:**
```json
{
  "transactionId": "string",
  "paymentLink": "string"
}
```

**Xendit Webhook Payload (nested structure):**
```json
{
  "event": "payment_intent.succeeded",
  "data": {
    "amount_captured": "number",
    "charges": {
      "items": [...]
    }
  }
}
```

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → `generatePaymentLink` → Xendit API
- Webhook at `/gateway/xendit/create` → `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. `createV2` → INSERT `payment_initiations`
2. Build Xendit payload: `planId`, `amount`, `currency=IDR`, `aggregatorId=6`, `aggregatorName='xendit'`
3. Call Xendit API → receive `transactionId` + `paymentLink`

**Webhook Processing:**
1. Receive Xendit webhook: `event=payment_intent.succeeded`, nested `amount_captured`, charge details
2. UPDATE `payment_transaction_info`
3. Call Eklavya service → update sale_payment status
4. Trigger `generateInvoice` Lambda

### High-Level Design (HLD)
```
POST /v1/payment-initiation/payment-link
  → Xendit API → transactionId + paymentLink
  → User completes Xendit payment
  → Xendit fires webhook (payment_intent.succeeded) → /gateway/xendit/create
      → receivePayment()
          → UPDATE payment_transaction_info
          → Eklavya: update sale_payment
          → generateInvoice Lambda
```

## External Integrations
- **Xendit API:** Payment link generation
- **Xendit Dashboard:** Webhook URL configuration (not embedded in payload)
- **Supported Currency:** IDR (Indonesian Rupiah)
- **aggregatorId:** 6 (hardcoded identifier for Xendit in system)

## Internal Service Dependencies
- **Payment-Structure:** Xendit integration logic
- **Eklavya:** Post-payment updates
- **generateInvoice Lambda:** Invoice generation

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook receipt

### SQL / ORM Queries
- INSERT `payment_initiations` (amount, currency='IDR', expiry, metadata)
- UPDATE `payment_transaction_info` from nested webhook `amount_captured` and charge data

### Transactions
- Post-webhook updates atomically handled by Eklavya

## Performance Analysis

### Good Practices
- `aggregatorId=6` provides unambiguous system identification
- `payment_intent.succeeded` event type clearly signals successful capture

### Performance Concerns
- Nested webhook payload structure requires deeper parsing logic vs. flat payloads
- Webhook configured in Xendit dashboard — manual step, operational risk

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No webhook signature verification documented |
| Medium | Webhook URL must be manually configured in Xendit dashboard — not codified |
| Low | PHP currency support not confirmed in documentation |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Document Xendit dashboard webhook configuration as runbook step
- Add Xendit webhook token verification

### Month 1 (Architectural)
- Investigate Xendit's webhook management API for programmatic configuration

## Test Scenarios

### Functional Tests
- IDR payment link generated → user pays → `payment_intent.succeeded` webhook received → DB updated
- Nested charge details correctly parsed from webhook payload
- `aggregatorId=6` correctly routes to Xendit in aggregator selection

### Performance & Security Tests
- Webhook signature/token verification
- IDR large number handling (millions in IDR for standard course amounts)

### Edge Cases
- Xendit sends `payment_intent.failed` — handle gracefully (no sale_payment update)
- Nested `charges.items` array empty — fallback parsing
- Webhook delivery retried by Xendit after initial timeout — idempotency
