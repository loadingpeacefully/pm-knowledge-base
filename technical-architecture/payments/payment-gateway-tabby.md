---
title: Payment Gateway – Tabby
category: technical-architecture
subcategory: payments
source_id: 47bc1149
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – Tabby

## Overview
Tabby provides Buy Now, Pay Later (BNPL) installment payments for Middle Eastern markets. The system creates a Tabby checkout session via `POST https://api.tabby.ai/api/v2/checkout` and processes payment confirmation via a webhook. Supported currencies are AED (UAE) and SAR (Saudi Arabia).

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment`
- `POST /v1/payment-initiation/payment-link`

**External Tabby API:**
- `POST https://api.tabby.ai/api/v2/checkout`

**Tabby Request Payload:**
```json
{
  "amount": "number",
  "currency": "AED|SAR",
  "buyer": {
    "phone": "string",
    "email": "string",
    "name": "string"
  },
  "order": {
    "items": [...],
    "reference_id": "string"
  },
  "language": "string",
  "merchant_code": "BCUAE",
  "merchant_urls": {
    "success": "string",
    "cancel": "string",
    "failure": "string"
  }
}
```

**Tabby Response:**
```json
{
  "transactionId": "string",
  "paymentLink": "string (includes product=installments)"
}
```

**Webhook Endpoints (Tabby → system):**
- Production: `https://api-services.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/tabby/create`
- Staging: `https://api-services-stage.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/tabby/create`

**Tabby Webhook Payload:**
```json
{
  "email": "string",
  "phone": "string",
  "txnId": "string",
  "amount": "number",
  "expiry": "datetime",
  "planId": "string",
  "currency": "AED|SAR",
  "country": "string",
  "paymentMethod": "Tabby"
}
```

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → `generatePaymentLink` → Tabby API call
- Webhook at `/gateway/tabby/create` → `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. `createV2` → INSERT `payment_initiations`
2. Build Tabby payload with amount, currency (AED/SAR), buyer details, order info, merchant_code=BCUAE, merchant_urls
3. `POST https://api.tabby.ai/api/v2/checkout`
4. Return `transactionId` + `paymentLink` (with `product=installments` in URL)

**Webhook Processing:**
1. Receive Tabby webhook with `txnId`, amount, currency, `paymentMethod='Tabby'`
2. UPDATE `payment_transaction_info`
3. Call Eklavya service → update sale_payment status
4. Trigger `generateInvoice` Lambda

### High-Level Design (HLD)
```
POST /v1/payment-initiation/payment-link
  → POST https://api.tabby.ai/api/v2/checkout
      → Returns transactionId + paymentLink (product=installments)
  → User completes Tabby BNPL checkout
  → Tabby webhook → /gateway/tabby/create
      → receivePayment()
          → UPDATE payment_transaction_info
          → Eklavya: update sale_payment
          → generateInvoice Lambda
  → User redirected to merchant_urls.success
```

## External Integrations
- **Tabby API:** `https://api.tabby.ai/api/v2/checkout`
- **Merchant Code:** `BCUAE`
- **Supported Currencies:** AED (UAE), SAR (Saudi Arabia)

## Internal Service Dependencies
- **Payment-Structure:** Tabby integration logic
- **Eklavya:** Post-payment updates
- **generateInvoice Lambda:** Invoice generation

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook receipt

### SQL / ORM Queries
- INSERT `payment_initiations` (initiator_id, amount, currency='AED'|'SAR', expiry, metadata)
- UPDATE `payment_transaction_info` SET `txn_id = ?, email = ?, phone = ?, currency = ?, payment_method = 'Tabby'`

### Transactions
- Post-webhook updates atomically handled by Eklavya

## Performance Analysis

### Good Practices
- `merchant_urls` with success/cancel/failure provides clear user journey for all outcomes
- Middle East focused currencies (AED, SAR) align with target geography

### Performance Concerns
- No webhook signature verification documented
- Order items array in payload — must be correctly populated for BNPL eligibility checks

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No webhook signature verification documented |
| Low | `merchant_code = BCUAE` hardcoded — expansion to KSA may require separate merchant code |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Implement Tabby webhook signature verification
- Add explicit validation for AED/SAR currency and UAE/SA country codes before Tabby is selected

### Month 1 (Architectural)
- Evaluate Tabby Pay-in-X plan options (2, 3, 4 installments) as configurable option

## Test Scenarios

### Functional Tests
- AED payment: Tabby link generated → user selects installment plan → webhook received → DB updated
- SAR payment: correct currency in payload and webhook
- `merchant_urls.cancel` and `merchant_urls.failure` correctly handle user abandonment

### Performance & Security Tests
- Webhook spoofing — reject requests without valid signature
- Concurrent Tabby payments from same buyer

### Edge Cases
- Tabby rejects buyer (credit check failure) — error URL redirect
- Order items array empty or malformed — Tabby rejection
- Currency mismatch between initiation and webhook
