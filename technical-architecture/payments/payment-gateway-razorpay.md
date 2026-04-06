---
title: Payment Gateway – Razorpay
category: technical-architecture
subcategory: payments
source_id: 6701bd95
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – Razorpay

## Overview
Razorpay integration generates a payment link via the Razorpay SDK with INR currency support. A callback URL handles user redirection post-payment; webhooks configured in the Razorpay dashboard deliver payment confirmation to the system.

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment`
- `POST /v1/payment-initiation/payment-link`

**Webhook Endpoints (Razorpay → system):**
- Production: `https://api-services.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/razorpay/create`
- Staging: `https://api-services-stage.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/razorpay/create`

**Callback URL (user redirect):** `https://payments-staging.brightchamps.com/success.html`
**Callback Method:** `GET`

**Razorpay SDK Payload:**
```json
{
  "amount": "number",
  "currency": "INR",
  "customer": {
    "name": "string",
    "email": "string",
    "contact": "string"
  },
  "reference_id": "string",
  "notes": "object",
  "callback_url": "https://payments-staging.brightchamps.com/success.html",
  "callback_method": "get"
}
```

**SDK Response:**
```json
{
  "transactionId": "string",
  "paymentLink": "https://rzp.io/i/tVDRSv6rWZ"
}
```

**Webhook Payload from Razorpay:**
```json
{
  "txnId": "string",
  "amount": "number",
  "currency": "INR",
  "paymentMethod": "string"
}
```

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → `generatePaymentLink` → Razorpay SDK call
- Webhook at `/gateway/razorpay/create` → `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. `createV2` → INSERT `payment_initiations`
2. `generatePaymentLink` → `getPaymentLink`
3. Build Razorpay SDK payload with amount, currency=INR, customer details, reference_id, callback_url
4. Call Razorpay SDK create endpoint
5. Return `transactionId` + `paymentLink` (rzp.io short URL)

**Webhook Processing:**
1. Receive Razorpay webhook with `txnId`, `amount`, `currency`, `paymentMethod`
2. UPDATE `payment_transaction_info`
3. Call Eklavya service to update sale payment status
4. Trigger `generateInvoice` Lambda

### High-Level Design (HLD)
```
POST /v1/payment-initiation/payment-link
  → Razorpay SDK create
      → Returns transactionId + paymentLink (rzp.io/i/...)
  → User visits rzp.io link → completes payment
  → Razorpay fires webhook → /gateway/razorpay/create
      → receivePayment()
          → UPDATE payment_transaction_info
          → Eklavya: update sale_payment status
          → generateInvoice Lambda trigger
  → User redirected to callback_url (success.html)
```

## External Integrations
- **Razorpay SDK:** Payment link creation
- **Supported Currency:** INR
- **Webhook:** Must be configured in Razorpay merchant dashboard

## Internal Service Dependencies
- **Payment-Structure:** Razorpay integration logic
- **Eklavya:** Post-payment status updates and credit allocation
- **generateInvoice Lambda:** Invoice generation trigger

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook with `txnId`, amount, currency, paymentMethod

### SQL / ORM Queries
- INSERT `payment_initiations` (initiator_id, amount, currency='INR', expiry, metadata)
- UPDATE `payment_transaction_info` SET `txn_id = ?, amount = ?, currency = 'INR', payment_method = 'Razorpay'`

### Transactions
- Post-webhook updates handled atomically by Eklavya `/payment-callback`

## Performance Analysis

### Good Practices
- rzp.io short URLs are user-friendly and mobile-accessible
- `callback_method: get` enables simple redirect handling without JS

### Performance Concerns
- Webhook must be manually configured in Razorpay dashboard — operational risk if misconfigured
- No documented retry logic on webhook delivery failure

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Webhook configuration is manual — not codified in infrastructure |
| Low | No explicit error handling documented for Razorpay SDK failures |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Document Razorpay webhook configuration in runbook with environment-specific URLs
- Add webhook signature verification using Razorpay's `X-Razorpay-Signature` header

### Month 1 (Architectural)
- Implement infrastructure-as-code (Terraform/Serverless) to manage webhook URLs

## Test Scenarios

### Functional Tests
- Razorpay payment link generated → user pays → webhook received → DB updated
- INR amount correctly passed to Razorpay SDK
- User redirected to `success.html` after payment

### Performance & Security Tests
- Webhook signature validation (prevent spoofed payment confirmations)
- Concurrent payments from same customer

### Edge Cases
- INR amount with paise values (subunit handling)
- Razorpay SDK returns error code — propagate to caller
- Webhook delivery delayed by >5 minutes
