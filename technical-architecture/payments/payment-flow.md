---
title: Payment Flow
category: technical-architecture
subcategory: payments
source_id: ae49116a
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Flow

## Overview
The payment flow is a multi-step end-to-end process that covers payment initiation, payment link generation via multiple aggregators, webhook-based transaction recording, invoice generation, and student onboarding. It integrates across the Payment-Structure, Eklavya, and Prabandhan microservices.

## API Contract
**Payment Initiation:**
- `POST /v1/payment-initiation/create-payment` — Creates a payment initiation entry
- `POST /v1/payment-initiation/payment-link` — Generates the aggregator-specific payment URL
- `POST /payment-callback` (Eklavya) — Webhook endpoint called by gateways upon payment success

**Request Body (create-payment):**
```json
{
  "paymentInitiatorName": "string",
  "referrerId": "string",
  "aggregatorName": "string (paypal|razorpay|splitit|stripe|tazapay|xendit|tabby|manual)",
  "amount": "number",
  "currency": "string",
  "expiry": "datetime",
  "metaData": "object"
}
```

**Response:** Returns newly created `payment_initiation` record including `paymentInitiationId`.

**Status Codes:** 200 OK, 400 Bad Request (validation failure), 500 Internal Server Error

## Logic Flow

### Controller Layer
- Receives payment initiation request and delegates to `createV2` function
- Receives payment link request using `paymentInitiationId` via `generatePaymentLink`
- Formats and returns payment link to caller (Eklavya `/v2/initiate-payment` or Prashashak-FE)

### Service/Facade Layer
**createV2 function:**
1. Identifies payment aggregator from `aggregatorName`
2. Inserts record into `payment_initiations` table
3. Validates aggregator-specific requirements; throws error on failure
4. Returns newly created initiation record

**generatePaymentLink function:**
1. Retrieves `payment_initiation` record by ID
2. Calls selected aggregator's SDK/API via `getPaymentLink` method
3. Returns `transactionId` and `paymentLink` to caller

**receivePayment (webhook handler):**
1. Parses gateway webhook payload
2. Updates `payment_transaction_info` table
3. Calls Eklavya `/payment-callback` to mark sale as paid
4. Triggers `generateInvoice` Lambda

### High-Level Design (HLD)
```
User → Prashashak-FE / Eklavya
         → POST /v1/payment-initiation/create-payment
         → POST /v1/payment-initiation/payment-link
         → [Aggregator SDK: PayPal | Razorpay | Stripe | Tabby | Tazapay | Xendit | Splitit | Manual]
         → User completes payment on gateway-hosted page
         → Gateway fires webhook → /gateway/:name/create
         → receivePayment → Eklavya /payment-callback
         → SQS: invoice-generation + onboard-flow
         → generateInvoice Lambda → S3 → Hermes email
         → onboard-flow Lambda → Hermes welcome emails → Paathshala → Prabandhan Closed Won
```

## External Integrations
- **PayPal:** Invoice-based payment via `POST https://api-m.sandbox.paypal.com/v2/invoicing/invoices`
- **Razorpay:** Payment link via Razorpay SDK (INR)
- **Stripe:** Checkout session via Stripe SDK (USD, AED)
- **Tabby:** BNPL via `POST https://api.tabby.ai/api/v2/checkout` (AED, SAR)
- **Tazapay:** `POST https://api.tazapay.com/v1/checkout` (GBP, OMR)
- **Xendit:** Payment link (IDR)
- **Splitit:** Installment-based checkout (USD)
- **AWS SQS:** `invoice-generation` and `onboard-flow` queues
- **AWS S3:** Invoice PDF storage (`brightchamps-invoices` / `stage-brightchamps-invoices`)
- **Hermes:** Email dispatch service (`payment_invoice`, `welcome_onbaord`, `class_schedule_after_onboard`)
- **Paathshala:** `/curriculum/student/module` for curriculum provisioning
- **Prabandhan:** `/deal/update-crm-deal-to-closed-won`

## Internal Service Dependencies
- **Eklavya:** `/v2/initiate-payment` (payment trigger), `/payment-callback` (post-payment hook)
- **Prashashak-FE:** Initiates payment link generation via UI action
- **Payment-Structure:** Core payment microservice housing all aggregator integrations
- **generateInvoice Lambda:** Puppeteer-based PDF invoice generation

## Database Operations

### Tables Accessed
- `payment_initiations` — Stores initiation records
- `payment_transaction_info` — Updated by webhook with transaction details
- `sale_payments` — Updated to `paid` status; invoice name stored here
- `student_profile` — `total_credits` updated post-payment
- `student_class_balance` — `total_booked_class` updated based on package module
- `package_module_mapping` — Fetched to calculate class totals per module
- `pipeline_failure_tracker` — Logs SQS pipeline failures

### SQL / ORM Queries
- INSERT into `payment_initiations` with `payment_initiator_id`, `referrer_id`, `aggregator_id`, `amount`, `currency`, `expiry`, `additional_request_body`
- UPDATE `sale_payments` SET `status = 'paid'` WHERE `payment_initiation_id = ?`
- UPDATE `student_profile` SET `total_credits = total_credits + X`
- UPDATE `student_class_balance` SET `total_booked_class = total_booked_class + X`

### Transactions
- Post-payment DB updates (sale_payments, student_profile, student_class_balance) are executed atomically within the `/payment-callback` handler

## Performance Analysis

### Good Practices
- Asynchronous post-payment processing via SQS (invoice generation and onboarding decoupled from payment confirmation)
- Lambda-based serverless scaling for invoice generation
- Pipeline failure tracker enables retry/debugging without data loss

### Performance Concerns
- Synchronous webhook handler must complete DB updates before returning 200 to gateway — risk of timeout under high load
- No explicit mention of idempotency keys on webhook processing (duplicate webhook risk)
- `generateInvoice` Puppeteer rendering is CPU-heavy — cold start latency on Lambda possible

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No documented webhook idempotency guard — duplicate payments possible |
| Medium | Manual payment path bypasses webhook entirely — no audit trail standardization |
| Low | Pipeline failure tracker requires manual monitoring/retry logic |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add idempotency key check on webhook handler using `transaction_id` deduplication
- Add dead-letter queue (DLQ) monitoring for `invoice-generation` and `onboard-flow` SQS

### Month 1 (Architectural)
- Implement event sourcing for payment state transitions to ensure auditability
- Move Puppeteer invoice generation to a warm container pool to reduce cold starts
- Add webhook signature verification for all gateways

## Test Scenarios

### Functional Tests
- Happy path: payment initiation → link generation → webhook → credits updated → invoice sent
- Manual payment path: `receivePayment` called directly, status marked paid
- First payment onboarding: verify SQS triggers, welcome emails sent, Paathshala updated, CRM closed won

### Performance & Security Tests
- Concurrent webhook calls from same gateway with same transaction ID (idempotency test)
- Webhook replay attack simulation — verify duplicate prevention
- SQS message throughput under peak payment load

### Edge Cases
- Aggregator returns payment link but user never completes payment (expiry handling)
- Webhook arrives before `payment_initiation` record is committed
- `pipeline_failure_tracker` entry — retry logic and escalation path
- Multi-currency payment with unsupported currency for selected aggregator
