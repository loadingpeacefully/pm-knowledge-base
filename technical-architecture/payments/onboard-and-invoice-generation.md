---
title: Onboard and Invoice Generation
category: technical-architecture
subcategory: payments
source_id: 110af03f
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Onboard and Invoice Generation

## Overview
After a successful payment is confirmed via the `/payment-callback` endpoint, the system triggers two parallel SQS queues: `invoice-generation` and `onboard-flow`. The invoice flow generates and emails a PDF invoice; the onboard flow (activated only on the first payment) sends welcome emails, provisions curriculum via Paathshala, and marks the CRM deal as Closed Won.

## API Contract
**Webhook Trigger:** `POST /payment-callback` (Eklavya service)
- Called by payment gateway on successful transaction
- Triggers downstream DB updates and SQS queue invocations

N/A for REST contract — downstream processing is event-driven via SQS Lambdas.

## Logic Flow

### Controller Layer
- `/payment-callback` validates gateway webhook payload
- Initiates DB updates synchronously
- Publishes to two SQS queues asynchronously

### Service/Facade Layer
**Post-Payment DB Updates (synchronous):**
1. UPDATE `sale_payments` SET `status = 'paid'`
2. UPDATE `student_profile` SET `total_credits = total_credits + X`
3. Fetch module from `package_module_mapping` to determine class totals
4. UPDATE `student_class_balance` SET `total_booked_class = total_booked_class + Y`

**Invoice Generation (async via SQS):**
1. Resolve invoice template from `invoice_template_specifications`
2. Fetch layout from `invoice_templates`
3. Render PDF via Puppeteer
4. Upload to S3 at `/<10-char-id>/original.pdf`
5. Update `sale_payments` with invoice identifier
6. Hermes: send `payment_invoice` email template

**Onboard Flow (async via SQS — first payment only):**
1. Check: COUNT `sale_payments` WHERE `status = 'paid'` for this student = 1
2. If first payment:
   - Hermes: send `welcome_onbaord` email
   - Hermes: send `class_schedule_after_onboard` email
   - Paathshala: `POST /curriculum/student/module` (assign curriculum)
   - Prabandhan: `POST /deal/update-crm-deal-to-closed-won`

### High-Level Design (HLD)
```
Gateway Webhook → POST /payment-callback (Eklavya)
  │
  ├─ DB: UPDATE sale_payments (status=paid)
  ├─ DB: UPDATE student_profile (total_credits)
  ├─ DB: SELECT package_module_mapping
  ├─ DB: UPDATE student_class_balance (total_booked_class)
  │
  ├─ SQS → invoice-generation Lambda
  │         → Template lookup → Puppeteer PDF → S3 → sale_payments update → Hermes email
  │
  └─ SQS → onboard-flow Lambda
            → IF first payment:
                → Hermes: welcome_onbaord email
                → Hermes: class_schedule_after_onboard email
                → Paathshala: /curriculum/student/module
                → Prabandhan: /deal/update-crm-deal-to-closed-won
```

## External Integrations
- **AWS SQS:** `invoice-generation` and `onboard-flow` queues
- **AWS S3:** `brightchamps-invoices` (prod) / `stage-brightchamps-invoices` (staging)
- **Puppeteer:** PDF invoice rendering
- **Hermes:** Templates: `payment_invoice`, `welcome_onbaord`, `class_schedule_after_onboard`
- **Paathshala:** `POST /curriculum/student/module`
- **Prabandhan:** `POST /deal/update-crm-deal-to-closed-won`

## Internal Service Dependencies
- **Eklavya:** Owns `/payment-callback`, `student_profile`, `student_class_balance`, `sale_payments`
- **Package-Structure / Payment-Structure:** Provides `package_module_mapping` data
- **generateInvoice Lambda:** Handles Puppeteer rendering and S3 upload

## Database Operations

### Tables Accessed
- `sale_payments` — Status updated to `paid`; invoice identifier stored
- `student_profile` — `total_credits` incremented
- `student_class_balance` — `total_booked_class` incremented
- `package_module_mapping` — Read to determine class totals per module/course
- `invoice_template_specifications` — Invoice template selection rules
- `invoice_templates` — HTML template content
- `pipeline_failure_tracker` — Failure logging for SQS pipeline errors

### SQL / ORM Queries
- UPDATE `sale_payments` SET `status = 'paid'` WHERE `id = ?`
- SELECT from `package_module_mapping` WHERE `package_id = ?` (to get class count)
- UPDATE `student_class_balance` SET `total_booked_class = ?`
- UPDATE `student_profile` SET `total_credits = ?`
- SELECT COUNT(*) FROM `sale_payments` WHERE `student_id = ? AND status = 'paid'` (first-payment check)

### Transactions
- DB updates in `/payment-callback` (sale_payments, student_profile, student_class_balance) are executed atomically

## Performance Analysis

### Good Practices
- Parallel SQS queues enable invoice generation and onboarding to run concurrently
- First-payment gate prevents duplicate onboarding emails on subsequent payments
- Atomic DB updates in payment callback prevent partial state

### Performance Concerns
- Synchronous `/payment-callback` must complete all DB updates before returning 200 — timeout risk under load
- No documented rollback if Paathshala or Prabandhan API calls fail in the onboard flow
- `pipeline_failure_tracker` requires manual retry orchestration

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Onboard flow has no compensating transaction if Paathshala or Prabandhan call fails mid-flow |
| Medium | First-payment detection relies on COUNT query — race condition possible with concurrent webhooks |
| Low | `welcome_onbaord` typo in template name (likely production artifact) |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add DLQ with 3 retries for both `invoice-generation` and `onboard-flow` SQS queues
- Add idempotency token on `/payment-callback` using `transaction_id`

### Month 1 (Architectural)
- Implement saga pattern for onboard flow — record each step's completion to enable partial retry
- Add distributed lock on first-payment check to prevent race conditions

## Test Scenarios

### Functional Tests
- Successful payment → invoice PDF generated → S3 stored → email sent
- First payment → welcome emails sent → Paathshala provisioned → CRM deal closed won
- Second payment → onboard flow NOT triggered (gate check)

### Performance & Security Tests
- Concurrent `/payment-callback` calls for same `sale_payment_id`
- Hermes email delivery confirmation under load

### Edge Cases
- Paathshala API unavailable during onboard flow — retry and fallback
- Invoice template not found — error handling
- SQS message processed twice — idempotency
