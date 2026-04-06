---
title: Payment Gateway – Tazapay
category: technical-architecture
subcategory: payments
source_id: 8e880a9d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – Tazapay

## Overview
Tazapay is a cross-border payment gateway used for GBP and OMR transactions. It requires explicit callback, complete, and error URL parameters in the checkout payload. Webhooks are configured within the payload rather than the merchant dashboard.

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment`
- `POST /v1/payment-initiation/payment-link`

**External Tazapay API:**
- Production: `POST https://api.tazapay.com/v1/checkout`
- Staging: `POST https://api-sandbox.tazapay.com/v1/checkout`

**Tazapay Payload:**
```json
{
  "planId": "string",
  "amount": "number",
  "currency": "GBP|OMR",
  "aggregatorId": "number",
  "aggregatorName": "tazapay",
  "expiry": "datetime",
  "callback_url": "string (webhook URL for background status updates)",
  "complete_url": "string (redirect on success)",
  "error_url": "https://payments-staging.brightchamps.com/cancel.html"
}
```

**Tazapay Response:**
```json
{
  "transactionId": "string",
  "paymentLink": "string"
}
```

**Webhook Endpoints (Tazapay → system):**
- Production: `http://api.brightchamps.com/tazapay/receivePaymentTazapay`
- Staging: `https://testnodeapi.brightchamps.com/tazapay/receivePaymentTazapay`

**Tazapay Webhook Payload:**
```json
{
  "txnId": "string",
  "amount": "number",
  "currency": "GBP|OMR",
  "countryId": "string",
  "paymentMethod": "string"
}
```

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → `generatePaymentLink` → Tazapay API
- Webhook at `/tazapay/receivePaymentTazapay` → `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. `createV2` → INSERT `payment_initiations`
2. Build Tazapay payload: amount, currency (GBP/OMR), `callback_url`, `complete_url`, `error_url`
3. Note: All three URL types **required** in the payload
4. `POST https://api.tazapay.com/v1/checkout` → returns `transactionId` + `paymentLink`

**Webhook Processing:**
1. Receive Tazapay webhook: `txnId`, `amount`, `currency`, `countryId`
2. UPDATE `payment_transaction_info`
3. Call Eklavya service → update sale_payment status
4. Trigger `generateInvoice` Lambda

**Error Handling:**
- `error_url` (`cancel.html`) handles user payment failure via redirect
- No programmatic error propagation beyond redirect

### High-Level Design (HLD)
```
POST /v1/payment-initiation/payment-link
  → POST https://api.tazapay.com/v1/checkout (with callback/complete/error URLs)
      → Returns transactionId + paymentLink
  → User completes Tazapay payment
  → Tazapay fires webhook to callback_url → /tazapay/receivePaymentTazapay
      → receivePayment()
          → UPDATE payment_transaction_info
          → Eklavya: update sale_payment
          → generateInvoice Lambda
  → User redirected to complete_url (success) or error_url (failure)
```

## External Integrations
- **Tazapay API:** Production (`api.tazapay.com`) / Sandbox (`api-sandbox.tazapay.com`)
- **Supported Currencies:** GBP (UK), OMR (Oman)

## Internal Service Dependencies
- **Payment-Structure:** Tazapay integration logic
- **Eklavya:** Post-payment updates
- **generateInvoice Lambda:** Invoice generation

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook receipt

### SQL / ORM Queries
- INSERT `payment_initiations` (amount, currency='GBP'|'OMR', expiry, metadata)
- UPDATE `payment_transaction_info` SET `txn_id = ?, amount = ?, currency = ?, country_id = ?`

### Transactions
- Atomically handled by Eklavya post-webhook

## Performance Analysis

### Good Practices
- Three-URL pattern (callback/complete/error) provides clear handling for all payment outcomes
- Sandbox environment available for testing without live transactions

### Performance Concerns
- No webhook signature verification documented
- Webhook URL is embedded in payload — requires correct environment URL at generation time

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No webhook signature verification documented |
| Low | `error_url` is hardcoded to staging URL in examples — production override must be verified |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Verify production `error_url` is not pointing to staging endpoint
- Add Tazapay webhook HMAC verification

### Month 1 (Architectural)
- Externalize `complete_url` and `error_url` to environment configuration for easy switching

## Test Scenarios

### Functional Tests
- GBP payment: link generated → user pays → webhook received → DB updated
- OMR payment: correct currency in webhook payload
- Payment failure: user redirected to `error_url` (cancel.html)

### Performance & Security Tests
- Webhook spoofing prevention
- GBP/OMR currency precision handling

### Edge Cases
- Tazapay API unreachable: graceful error with descriptive message
- `countryId` missing from webhook payload
- `complete_url` redirect failure (user stays on Tazapay page)
