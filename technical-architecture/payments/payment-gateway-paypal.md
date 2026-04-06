---
title: Payment Gateway – PayPal
category: technical-architecture
subcategory: payments
source_id: 4a2a8a0f
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – PayPal

## Overview
PayPal integration uses the invoice-based flow: the system creates a draft PayPal invoice, sends it to the buyer, and receives payment confirmation via a PayPal-hosted webhook. Supported currency is USD.

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment` — Creates payment initiation record
- `POST /v1/payment-initiation/payment-link` — Triggers PayPal invoice creation

**External PayPal API:**
- `POST https://api-m.sandbox.paypal.com/v2/invoicing/invoices` — Creates draft invoice
- Response includes `invoiceId` → passed to `sendInvoice` function → returns `paymentLink`

**Webhook Endpoints (PayPal → system):**
- Production: `https://api-services.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/paypal/create`
- Staging: `https://api-services-stage.brightchamps.com/payment-structure/v1/payment-transaction-info/gateway/paypal/create`

**Callback Endpoint (user redirect):** Eklavya `/payment-callback`

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → calls `generatePaymentLink`
- Webhook received at `/gateway/paypal/create` → calls `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. Call `createV2` → INSERT `payment_initiations`
2. Call `generatePaymentLink` → `getPaymentLink` with `planId`, `amount`, `currency`, `aggregatorId`, `aggregatorName`, `expiry`, `metaData`
3. PayPal flow: `createInvoice` → `createDraftInvoice` → `POST PayPal /v2/invoicing/invoices`
4. Extract `invoiceId` from PayPal response
5. Call `sendInvoice` → retrieves `transactionId` and `paymentLink`
6. Return `paymentLink` to user

**Webhook Processing:**
1. Receive PayPal webhook payload: `invoice_number`, `currency_code`, `amount`, buyer details
2. Call `receivePayment` function
3. UPDATE `payment_transaction_info` (transaction ID, email, phone, amount, `paymentMethod = 'Paypal'`)
4. Call Eklavya `/payment-callback`
5. Trigger `generateInvoice` Lambda

**Manual Payment (no webhook):**
- Operations team calls `receivePayment` directly
- No webhook URL configured

### High-Level Design (HLD)
```
Prashashak-FE
  → POST /v1/payment-initiation/create-payment
  → POST /v1/payment-initiation/payment-link
      → createInvoice()
          → createDraftInvoice()
              → POST https://api-m.sandbox.paypal.com/v2/invoicing/invoices
          → sendInvoice() → transactionId + paymentLink
  → Return paymentLink to user

User completes PayPal payment
  → PayPal webhook → /gateway/paypal/create
      → receivePayment()
          → UPDATE payment_transaction_info
          → POST Eklavya /payment-callback
          → Trigger generateInvoice Lambda
```

## External Integrations
- **PayPal API:** `https://api-m.sandbox.paypal.com/v2/invoicing/invoices`
- **PayPal Webhook:** Configured in PayPal dashboard to point to production/staging webhook URLs
- **Supported Currency:** USD

## Internal Service Dependencies
- **Payment-Structure:** Hosts PayPal integration logic
- **Eklavya:** `/payment-callback` for post-payment DB updates
- **generateInvoice Lambda:** Invoice PDF generation

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook receipt
- `sale_payments` — Status updated to `paid` via Eklavya callback
- `student_profile` — `total_credits` updated
- `student_class_balance` — `total_booked_class` updated
- `pipeline_failure_tracker` — SQS failure logging

### SQL / ORM Queries
- INSERT `payment_initiations` (initiator_id, amount, currency=USD, expiry, metadata)
- UPDATE `payment_transaction_info` SET `txn_id = ?, email = ?, phone = ?, amount = ?, payment_method = 'Paypal'`

### Transactions
- Post-webhook DB updates are handled atomically within the Eklavya `/payment-callback` handler

## Performance Analysis

### Good Practices
- Invoice-based flow provides clear transaction trail in PayPal dashboard
- `pipeline_failure_tracker` captures async processing failures for debugging

### Performance Concerns
- Two sequential PayPal API calls (`createDraftInvoice` + `sendInvoice`) before returning payment link — increases link generation latency
- No documented retry on PayPal API failure during invoice creation

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Two-step PayPal invoice creation (`draft` then `send`) could be consolidated |
| Medium | No webhook signature verification documented |
| Low | Manual payment bypass (no webhook) creates inconsistent audit trail |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add webhook event signature verification using PayPal's WEBHOOK-ID header
- Add timeout + retry (3 attempts) on PayPal invoice creation API calls

### Month 1 (Architectural)
- Evaluate PayPal Checkout Sessions API as alternative to invoice-based flow for lower latency

## Test Scenarios

### Functional Tests
- PayPal link generated → user pays → webhook received → sale_payments marked paid
- Manual payment: `receivePayment` called directly → correct DB updates
- `invoice_number` correctly mapped to `payment_initiation_id`

### Performance & Security Tests
- Webhook replay: same PayPal invoice_number received twice — idempotency check
- PayPal API down: error propagates gracefully with descriptive message

### Edge Cases
- PayPal `createDraftInvoice` succeeds but `sendInvoice` fails — orphaned draft invoice
- Webhook arrives before payment initiation record is committed
- USD conversion edge cases (very small amounts, PayPal minimum invoice amount)
