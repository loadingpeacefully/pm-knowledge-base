---
title: Revamped Payment Page – Enabling Cross-Sell and Multi-Student Checkout
category: technical-architecture
subcategory: payments
source_id: 9eae1c63
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Revamped Payment Page – Enabling Cross-Sell and Multi-Student Checkout

## Overview
The revamped payment page supports multi-student enrollment in a single transaction, cross-selling via Nano Courses, upselling via an upgrade section, and an itemized amount breakup modal. The backend API `POST /v1/package-payment` serves the checkout data; the frontend uses debounce-based real-time price sync.

## API Contract
**POST `/v1/package-payment`**
- **Auth:** Internal (Base64-encoded payment_initiation_id)
- **Request Body:**
```json
{
  "payment_initiation_id_encoded": "string (Base64 JSON)"
}
```
- **Response:**
```json
{
  "packages": [...],
  "addonMaterials": [...],
  "students": [...],
  "parents": [...],
  "pricingBreakup": {...},
  "currency": "string",
  "country": "string",
  "timezone": "string",
  "paymentExpiry": "datetime"
}
```
- **Status Codes:** 200 OK, 400 Bad Request (expired or invalid payload), 500 Internal Server Error

## Logic Flow

### Controller Layer
- Decode Base64 `payment_initiation_id`
- Validate payment structure and expiry timestamp
- Orchestrate parallel DB queries for packages and add-ons
- Call PlatformService for regional data enrichment
- Return aggregated checkout payload

### Service/Facade Layer
1. **Decode & Validate:** Base64 decode → extract `payment_initiation_id` → check expiry
2. **Parallel Data Fetch:**
   - `PackageSaleInitiator` records: course type, installment plans, discounts, upgrade options
   - `AddonMaterialSaleInitiator` records: Nano Courses, Workbooks, Diamonds
3. **Student Aggregation:** Extract student IDs from both → batch-fetch student/parent profiles
4. **Regional Enrichment:** PlatformService → country, currency, timezone → localized pricing display
5. **Upgrade Section Logic:** Compare current package against higher tier → compute savings → set strikethrough price
6. **Nano Course Availability:** Fetch available nano courses positioned above payment CTA
7. **Debounce Sync:** Frontend debounces add/remove actions → calls backend to recalculate total
8. **Address Validation:** Billing address captured via bottom-sheet modal; pincode verified via regex or Google Maps API

### High-Level Design (HLD)
```
User opens payment page
  → GET payment page (Prashashak-FE loads payment_initiation_id from URL)
  → POST /v1/package-payment (Base64 payload)
      → Decode → Validate expiry
      → PARALLEL:
          → PackageSaleInitiator (course, installments, discounts)
          → AddonMaterialSaleInitiator (nano, diamonds, workbooks)
      → Batch-fetch students + parents
      → PlatformService: currency/country/TZ
      → Compute upgrade section (current vs. next tier)
      → Return full checkout payload

User adds Nano Course
  → Debounce → POST /v1/package-payment (updated initiation)
      → Recalculate total → Return updated pricing

User proceeds to payment
  → Billing address capture (bottom-sheet modal)
  → POST /v1/payment-initiation/payment-link → aggregator payment URL
  → Redirect to gateway
```

## External Integrations
- **PlatformService:** Country, currency, timezone resolution
- **NectedService:** Dynamic pricing per student purchase history
- **Google Maps API:** Address and pincode validation for physical kit delivery
- **Payment Aggregators:** Final payment link generation (Stripe, Razorpay, PayPal, Tabby, etc.)

## Internal Service Dependencies
- **Eklavya:** `PackageSaleInitiator`, `AddonMaterialSaleInitiator`, student/parent profiles, `package_grade_mappings`
- **Payment-Structure:** `POST /v1/package-payment` backend, payment initiation/link APIs
- **Prashashak-FE:** Frontend hosting the payment page

## Database Operations

### Tables Accessed
- `package_sale_initiators` — Course type, installment plan, discounts
- `addon_material_sale_initiators` — Nano Courses, Workbooks, Diamonds
- `addon_materials` — Add-on product definitions
- `packages` — Package definitions and tier hierarchy
- `students` / `parents` — Profile display on student cards
- `payment_initiations` — Expiry validation

### SQL / ORM Queries
- SELECT `PackageSaleInitiator` WHERE `payment_initiation_id = ?`
- SELECT `AddonMaterialSaleInitiator` WHERE `payment_initiation_id = ?`
- SELECT `students`, `parents` WHERE `id IN (studentIds[])` (batch)
- SELECT `packages` for upgrade tier comparison

### Transactions
- No write transactions at this stage (read-only aggregation)
- Writes occur when user confirms and triggers payment initiation

## Performance Analysis

### Good Practices
- Parallel data fetching for packages and add-ons minimizes checkout load time
- Debounce prevents excessive API calls on rapid item add/remove
- Regional pricing enrichment via PlatformService keeps pricing accurate without hardcoding
- Urgency timer on sticky footer increases payment conversion

### Performance Concerns
- Multiple sequential DB calls for student card rendering (student + parent + package + add-ons per student)
- Google Maps API call adds external latency to address validation
- Full payload re-fetch on each debounced item change — could be optimized to diff-only update

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Full payload reload on item add/remove instead of incremental price update |
| Medium | Mobile number locked on student edit modal creates friction for data correction scenarios |
| Low | Address validation using both regex and Google Maps — inconsistent approach |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Implement incremental price diff endpoint to avoid full payload reload on add/remove
- Cache PlatformService country/currency response per session

### Month 1 (Architectural)
- Pre-compute upgrade tier recommendations server-side at initiation time
- Implement A/B test framework for Nano Course cross-sell positioning

## Test Scenarios

### Functional Tests
- Single student checkout: correct package displayed, correct pricing, correct aggregator
- Multi-student checkout: two students with different courses shown as separate cards
- Nano Course added → assigned to correct student via bottom-sheet selector
- Upgrade section shows correct strikethrough price and savings
- Amount breakup modal shows all line items (course, add-ons, discounts, installments)

### Performance & Security Tests
- 50 concurrent users loading checkout page — response time < 2s
- Expired `payment_initiation_id` → 400, user redirected appropriately
- Tampered Base64 payload → validation rejection

### Edge Cases
- Parent has 3+ children → all student cards rendered correctly
- Nano Course unavailable → section hidden gracefully
- Upgrade section not applicable (student already on top tier) → section hidden
- Billing address in a country without pincode validation regex
