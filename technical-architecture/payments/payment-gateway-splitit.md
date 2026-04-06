---
title: Payment Gateway – Splitit
category: technical-architecture
subcategory: payments
source_id: a47cba0d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Gateway – Splitit

## Overview
Splitit enables installment-based payment plans. The system generates a checkout link by passing installment plan parameters to Splitit; webhook and callback URLs must be included in the creation payload. Primary documented currency is USD for US customers.

## API Contract
**Internal Endpoints:**
- `POST /v1/payment-initiation/create-payment`
- `POST /v1/payment-initiation/payment-link`

**Webhook Endpoints (Splitit → system):**
- Production: `http://api.brightchamps.com/splitit/receivePaymentSplitit`
- Staging: `https://testnodeapi.brightchamps.com/splitit/receivePaymentSplitit`

**Splitit Payload (sent to Splitit gateway):**
```json
{
  "planId": "string",
  "amount": "number",
  "currency": "USD",
  "noOfInstallment": "number",
  "webhookUrl": "string",
  "callbackUrl": "string"
}
```

**Splitit Response:**
```json
{
  "transactionId": "string",
  "paymentLink": "string"
}
```

## Logic Flow

### Controller Layer
- `POST /v1/payment-initiation/payment-link` → `generatePaymentLink` → Splitit API call
- Webhook at `/splitit/receivePaymentSplitit` → `receivePayment`

### Service/Facade Layer
**Payment Link Generation:**
1. `createV2` → INSERT `payment_initiations`
2. `generatePaymentLink` → `getPaymentLink`
3. Build Splitit payload: `planId`, `amount`, `currency`, `noOfInstallment`, `webhookUrl` (required), `callbackUrl`
4. Note: Splitit **requires webhook URL in the creation payload** (unlike gateways that use dashboard configuration)
5. Call Splitit API → receive `transactionId` + `paymentLink`

**Webhook Processing:**
1. Receive Splitit webhook payload
2. UPDATE `payment_transaction_info`
3. Call Eklavya service to update sale payment status
4. Trigger `generateInvoice` Lambda

**Aggregator Exclusion:**
- Splitit is explicitly excluded from certain installment structures (filtered out during aggregator selection for specific package types)

### High-Level Design (HLD)
```
POST /v1/payment-initiation/payment-link
  → Build Splitit payload (with webhookUrl embedded)
  → Splitit API → transactionId + paymentLink
  → User visits Splitit checkout → selects installment plan → completes
  → Splitit fires webhook → /splitit/receivePaymentSplitit
      → receivePayment()
          → UPDATE payment_transaction_info
          → Eklavya: update sale_payment status
          → generateInvoice Lambda trigger
```

## External Integrations
- **Splitit API:** Installment checkout link generation
- **Supported Currency:** USD (US)
- **Webhook:** Embedded in creation payload (not dashboard-configured)

## Internal Service Dependencies
- **Payment-Structure:** Splitit integration logic
- **Eklavya:** Post-payment status updates
- **generateInvoice Lambda:** Invoice generation

## Database Operations

### Tables Accessed
- `payment_initiations` — INSERT on initiation
- `payment_transaction_info` — UPDATE on webhook receipt

### SQL / ORM Queries
- INSERT `payment_initiations` (initiator_id, amount, currency='USD', expiry, metadata including noOfInstallment)
- UPDATE `payment_transaction_info` on webhook receipt

### Transactions
- Post-webhook updates handled atomically by Eklavya `/payment-callback`

## Performance Analysis

### Good Practices
- Webhook URL embedded in payload ensures correct routing regardless of dashboard configuration
- Explicit aggregator exclusion logic prevents Splitit from being assigned to incompatible package types

### Performance Concerns
- Splitit requires explicit installment count in payload — must be determined before link generation
- No documented timeout handling on Splitit API

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Aggregator exclusion rules for Splitit are hardcoded in service logic |
| Low | Only USD/US documented — no clear guidance on expanding to other markets |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Document Splitit exclusion rules in a configuration table for admin management

### Month 1 (Architectural)
- Externalize `noOfInstallment` calculation to a configurable installment plan service

## Test Scenarios

### Functional Tests
- Splitit link generated with 3, 6, 12 installment options → correct plan displayed
- User completes first installment → webhook received → DB updated
- Splitit excluded from single-payment package types

### Performance & Security Tests
- Webhook payload validation — reject unsigned/malformed payloads
- Simultaneous installment payments from same user

### Edge Cases
- User abandons payment after link generation — expiry handling
- Splitit rejects `noOfInstallment` value — error propagation
- USD amount edge cases (Splitit minimum amount thresholds)
