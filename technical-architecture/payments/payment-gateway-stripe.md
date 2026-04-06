---
title: Payment Gateway – Stripe
category: technical-architecture
subcategory: payments
source_id: 81c7be93
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – Stripe

## Overview
Stripe integration generates a hosted checkout payment link (prefixed `plink_`) and processes payment confirmations via webhook using PaymentIntent (`pi_` prefix). Supported currencies include USD and AED.

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment`
- `POST /v1/payment-initiation/payment-link`

**Webhook Endpoint (Stripe → system):**
- `/payment-structure/v1/payment-transaction-info/gateway/stripe/create`

**Stripe Response:**
```json
{
  "transactionId": "plink_...",
  "paymentLink": "https://buy.stripe.com/..."
}
```

**Stripe Webhook Payload (PaymentIntent succeeded):**
```json
{
  "txnId": "pi_...",
  "capture_status": "string",
  "amount": "number",
  "currency": "USD|AED",
  "payment_initiation_id": "string"
}
```

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → `generatePaymentLink` → Stripe SDK
- Webhook at `/gateway/stripe/create` → `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. `createV2` → INSERT `payment_initiations`
2. `generatePaymentLink` → `getPaymentLink` with `planId`, `amount`, `currency`, `aggregatorId`
3. Stripe SDK returns `transactionId` (plink_ prefix) + `paymentLink` (buy.stripe.com URL)

**Webhook Processing:**
1. Receive Stripe webhook: `txnId` with `pi_` prefix (PaymentIntent), `capture_status`, `amount`
2. `receivePayment` creates object with `payment_initiation_id`, `amount`, `capture_status`
3. UPDATE `payment_transaction_info`
4. Call Eklavya service → update sale payment status
5. Trigger `generateInvoice` Lambda

### High-Level Design (HLD)
```
POST /v1/payment-initiation/payment-link
  → Stripe SDK → plink_ transactionId + buy.stripe.com paymentLink
  → User visits Stripe hosted checkout → completes payment
  → Stripe fires webhook → /gateway/stripe/create
      → receivePayment()
          → UPDATE payment_transaction_info (txnId=pi_...)
          → Eklavya: update sale_payment status
          → generateInvoice Lambda trigger
```

## External Integrations
- **Stripe SDK:** Hosted checkout link generation
- **Stripe Webhook:** PaymentIntent succeeded events
- **Supported Currencies:** USD, AED

## Internal Service Dependencies
- **Payment-Structure:** Stripe integration logic
- **Eklavya:** Post-payment updates
- **generateInvoice Lambda:** Invoice generation

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook receipt with `pi_` txnId

### SQL / ORM Queries
- INSERT `payment_initiations` (initiator_id, amount, currency='USD'|'AED', expiry, metadata)
- UPDATE `payment_transaction_info` SET `txn_id = 'pi_...', capture_status = ?, amount = ?`

### Transactions
- Post-webhook updates atomically handled by Eklavya

## Performance Analysis

### Good Practices
- Stripe's hosted checkout is PCI-DSS compliant by default
- `buy.stripe.com` URLs are durable and mobile-friendly
- PaymentIntent model provides clear payment state machine

### Performance Concerns
- No webhook signature verification documented (Stripe provides `stripe-signature` header for HMAC verification)
- No recurring payment / subscription handling documented

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No Stripe webhook signature (`stripe-signature`) verification documented — spoofing risk |
| Medium | Recurring payment support not documented — installment/subscription plans unclear |
| Low | `plink_` vs `pi_` ID types: two different Stripe objects (Payment Link vs PaymentIntent) — ensure correct mapping |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Implement `stripe-signature` header verification on webhook endpoint
- Add Stripe event type filtering (only process `payment_intent.succeeded`)

### Month 1 (Architectural)
- Evaluate Stripe Subscriptions API for recurring installment plans
- Add Stripe Radar rules for fraud detection on AED transactions

## Test Scenarios

### Functional Tests
- Stripe link generated → user pays in USD → webhook (pi_) received → DB updated
- AED payment flow → correct currency in webhook payload
- `capture_status` correctly mapped to `payment_transaction_info`

### Performance & Security Tests
- Stripe webhook signature verification (HMAC-SHA256)
- Replay webhook with same `pi_` ID — idempotency check

### Edge Cases
- Payment link expires without payment (Stripe link TTL)
- AED payment with subunit (fils) handling
- Webhook arrives out of order (created before succeeded)
