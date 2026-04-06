---
title: Package and Payments
category: technical-architecture
subcategory: payments
source_id: 714bdd1d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Package and Payments

## Overview
This document covers how course packages are defined, priced, sold, and linked to the payment system. It describes package types, dynamic pricing via NectedService, multi-currency support, the sale_payments table structure, and how payment aggregators are assigned per package and country.

## API Contract
**Primary Endpoint:** `POST /v1/package-payment`
- **Auth:** Internal (Base64-encoded payment_initiation_id from frontend)
- **Request Body:**
```json
{
  "payment_initiation_id_encoded": "string (Base64 encoded JSON)"
}
```
- Decoded payload contains `payment_initiation_id`
- **Response:** Aggregated checkout data including package details, add-on materials, student/parent info, regional pricing, and available aggregators

## Logic Flow

### Controller Layer
- Decode Base64 encoded `payment_initiation_id` from frontend
- Validate payment structure and expiry
- Return aggregated checkout payload to Prashashak-FE / payment page

### Service/Facade Layer
1. **Decode & Validate:** Decode Base64 → extract `payment_initiation_id` → validate expiry
2. **Parallel Data Fetch:**
   - Fetch `PackageSaleInitiator` records (course type, installment plan, discounts)
   - Fetch `AddonMaterialSaleInitiator` records (Nano Courses, Workbooks, Diamonds)
3. **Student Aggregation:** Extract all student IDs from packages and add-ons → fetch student/parent records
4. **Pricing via NectedService:** Fetch dynamic package pricing; apply regional currency via PlatformService
5. **Aggregator Assignment:**
   - Find most recent paid payment from package details
   - Extract payment initiation data → identify aggregator
   - Filter excluded aggregators (e.g., Splitit excluded from certain installment types)
   - Assign default aggregator if no match
6. **Debounce Sync:** Real-time price recalculation as user adds/removes items

### High-Level Design (HLD)
```
Prashashak-FE → POST /v1/package-payment (Base64 payload)
  → Decode → Validate expiry
  → PARALLEL:
      → PackageSaleInitiator records (packages, installments, discounts)
      → AddonMaterialSaleInitiator records (nano courses, diamonds, workbooks)
  → Aggregate student IDs → fetch students/parents
  → NectedService: dynamic pricing per package
  → PlatformService: currency/country/timezone resolution
  → Aggregator selection logic → return paymentLink metadata
  → Return full checkout payload to FE
```

## External Integrations
- **NectedService:** Dynamic pricing recommendation engine — fetches package pricing based on student history
- **PlatformService:** Resolves country, currency, and timezone for regional pricing
- **Payment Aggregators:** PayPal, Razorpay, Stripe, Tabby, Tazapay, Xendit, Splitit, Manual

## Internal Service Dependencies
- **Eklavya:** `packages`, `package_sale_initiators`, `addon_material_sale_initiators`, `sale_payments`, `student_profile`, `student_class_balance`
- **Payment-Structure:** Payment initiation and link generation
- **Paathshala:** Class scheduling data for multi-student checkout

## Database Operations

### Tables Accessed
- `packages` — Package metadata and definitions
- `package_sale_initiators` — Tracks sold packages (pricing, course ID, student relationship, installment plan)
- `addon_materials` — Defines add-on products (workbooks, diamonds, nano courses)
- `addon_material_sale_initiators` — Tracks add-on sales
- `package_grade_mappings` — Restricts package availability by student grade
- `sale_payments` — Individual payment installment tracking
- `sale_payment_distributions` — Breaks payments into `course_fee` + `platform_fee` allocations

### SQL / ORM Queries
- SELECT `PackageSaleInitiator` WHERE `payment_initiation_id = ?` (includes course type, installment, discounts)
- SELECT `AddonMaterialSaleInitiator` WHERE `payment_initiation_id = ?`
- SELECT `sale_payments` ORDER BY created_at DESC LIMIT 1 (for aggregator detection)
- SELECT `package_grade_mappings` WHERE `grade_id = ?`

### Transactions
- Package sale creation involves multi-table writes (package_sale_initiators, sale_payments, sale_payment_distributions) — should be transactional

## Performance Analysis

### Good Practices
- Parallel data fetching for packages and add-ons reduces latency
- Debounce logic on frontend prevents excessive API calls during item add/remove
- Dynamic pricing with NectedService allows personalized pricing without code changes

### Performance Concerns
- Aggregator selection logic requires fetching most recent paid payment — sequential DB reads
- Multi-entity aggregation (all student IDs across packages and add-ons) could be N+1 if not using batch queries
- NectedService call adds external latency to checkout page load

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Aggregator assignment is implicit (based on last paid payment) — no explicit admin override documented |
| Medium | Fallback pricing hardcoded ($120 USD for 10 classes) — requires code change to update |
| Low | `package_grade_mappings` check adds a query per student — batch preload recommended |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Cache NectedService pricing response per student (TTL: 15 minutes)
- Batch-load all student records in a single query instead of per-student fetches

### Month 1 (Architectural)
- Implement explicit aggregator configuration table (country + course → aggregator mapping)
- Replace hardcoded fallback pricing with configurable admin panel settings

## Test Scenarios

### Functional Tests
- Single student checkout with one package → correct pricing, aggregator, and payment link
- Multi-student checkout with mixed packages and add-ons → correct student grouping
- Upgrade course section visible with correct strikethrough pricing

### Performance & Security Tests
- Checkout page load time under concurrent sessions
- Base64 payload tampering — verify validation rejects modified payloads
- Expired `payment_initiation_id` → 400 response

### Edge Cases
- Student grade has no matching `package_grade_mappings` entry
- NectedService unavailable → fallback pricing applied
- All aggregators excluded by filter → default aggregator assignment
- Currency conversion ratio unavailable for payment date
