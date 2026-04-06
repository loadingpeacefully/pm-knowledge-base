---
title: Sell Collection
category: technical-architecture
subcategory: payments
source_id: 434b9e5d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Sell Collection

## Overview
The sell collection flow is an event-driven system that processes paid sale payments to calculate and allocate sales incentives to Sales Managers. It classifies each transaction into collection types (fresh, renewal, installment variants) and attributes them to a collector using Nected for geography and team hierarchy data.

## API Contract
N/A — Event-driven Lambda function triggered by AWS SQS.

**SQS Queue:** `{stage}-eklavya-sell-collection-info`
**Lambda Function:** `${sls:stage}-sellCollectionInfo`
**Trigger:** Sale payment status changes to `paid`

**SQS Message Payload:**
```json
{
  "salePaymentId": "string",
  "studentClassBalanceId": "string"
}
```

## Logic Flow

### Controller Layer
- SQS message received with `salePaymentId` and `studentClassBalanceId`
- Lambda `sellCollectionInfo` is invoked
- Processes payment → creates sell collection record

### Service/Facade Layer
1. **Fetch Sale Payment:** Retrieve payment details including amount, currency, `package_sale_initiator_id`
2. **Currency Conversion:** Convert payment `amount` to INR (`amountINR`) via platform currency conversion service
3. **Pricing Classification:** Evaluate `collectionFlagId` (0 = below rock bottom, 1 = above rock bottom, 2 = above 1.4x rock bottom)
4. **Collection Type Classification (`collectionType` ENUM):**
   - `fresh`: First payment ever for this student + course combination
   - `fresh-equivalent`: Second payment under same package_sale_initiator, within 28 days
   - `fresh-installment`: Second payment under same package_sale_initiator, after 28 days
   - `renewal`: First payment on an upgraded (new) package_sale_initiator
   - `renewal-equivalent`: Second payment on upgraded PSI, within 28 days
   - `renewal-installment`: Subsequent payment on upgraded PSI, after 28 days
5. **UTM Tracking:** Fetch `utmSource` from initial booking via `source_id` in package_sale_initiator
6. **Collector Attribution:** Fetch from Nected: `collectorGeography`, `collectorPNLId`, `collectorTLId`, `collectorRDId`
7. **Eligible At Calculation:** `eligibleAt` = MAX(paidAt, date of 2nd credit used, date total_completed_classes reached 2)
8. **Persist:** INSERT into sell_collection record

### High-Level Design (HLD)
```
sale_payment.status = 'paid' (Eklavya /payment-callback)
  → SQS PUBLISH: {stage}-eklavya-sell-collection-info
      → Lambda: sellCollectionInfo
          → Fetch sale_payment + package_sale_initiator
          → Currency conversion → amountINR
          → Determine collectionFlagId (vs. rock bottom price)
          → Classify collectionType (fresh/renewal/installment variants)
          → Fetch utmSource from booking
          → Nected: fetch collector (geography, PNL, TL, RD)
          → Calculate eligibleAt = MAX(paidAt, 2nd credit date, 2-class completion date)
          → INSERT sell_collection record
```

## External Integrations
- **Nected:** Provides collector attribution data (`collectorGeography`, `collectorPNLId`, `collectorTLId`, `collectorRDId`) and rock-bottom pricing thresholds
- **AWS SQS:** `{stage}-eklavya-sell-collection-info` queue
- **Platform Currency Conversion Service:** INR conversion for non-INR currencies

## Internal Service Dependencies
- **Eklavya:** `sale_payments`, `package_sale_initiators`, `student_class_balance`
- **Tryouts / Booking Service:** Initial booking data for UTM source extraction
- **Platform Service:** Currency conversion ratios

## Database Operations

### Tables Accessed
- `sale_payments` — Source payment record
- `package_sale_initiators` — Package context for collection type classification
- `student_class_balance` / `student_class_balances` — Used for `eligibleAt` calculation (2nd credit date, completion count)

### SQL / ORM Queries
- SELECT `sale_payments` WHERE `id = salePaymentId`
- SELECT `package_sale_initiators` WHERE `id = packageSaleInitiatorId`
- SELECT COUNT paid `sale_payments` WHERE `package_sale_initiator_id = ? AND status = 'paid'` (for fresh vs. installment)
- SELECT `student_class_balance` WHERE `id = studentClassBalanceId` (for eligibleAt date)

### Transactions
- Single INSERT into sell_collection — no multi-table transaction needed

**Sell Collection Record Schema:**
```
id
salePaymentId
studentClassBalanceId
amountINR
eligibleAt
paidAt
collectionFlagId  (0|1|2)
utmSource
collectionType    (ENUM: fresh|fresh-installment|renewal-installment|renewal|fresh-equivalent|renewal-equivalent)
collectorGeography
collectorPNLId
collectorTLId
collectorRDId
```

## Performance Analysis

### Good Practices
- Fully asynchronous SQS-driven — no impact on payment confirmation latency
- Clear ENUM-based classification enables reliable incentive calculation queries
- 28-day window for fresh/renewal-equivalent distinction is configurable via logic

### Performance Concerns
- Multiple SELECT queries to classify collection type (payment history, class balance) — could be batched
- Nected API call adds external latency; no caching documented
- `eligibleAt` calculation requires three separate date lookups

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Nected API called on every sell collection event — no caching layer |
| Medium | Rock-bottom price comparison logic tightly coupled to Nected — single point of failure |
| Low | No DLQ documented for SQS failures |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add DLQ with retry for `{stage}-eklavya-sell-collection-info`
- Cache Nected collector data per Sales Manager (TTL: 1 hour)

### Month 1 (Architectural)
- Pre-compute `collectionType` at payment time and pass via SQS message to reduce Lambda queries
- Batch `eligibleAt` lookups using a single multi-criteria query

## Test Scenarios

### Functional Tests
- First payment for student + course → `collectionType = fresh`
- Second payment within 28 days on same PSI → `fresh-equivalent`
- Second payment after 28 days → `fresh-installment`
- Upgraded package, first payment → `renewal`
- `amountINR` correct for USD, AED, GBP payments

### Performance & Security Tests
- Nected API timeout — verify graceful failure handling
- Concurrent SQS messages for same salePaymentId (deduplication)

### Edge Cases
- `eligibleAt` when student never uses 2 credits → falls back to `paidAt`
- UTM source not found in booking → null handling
- Currency conversion rate unavailable for payment date
