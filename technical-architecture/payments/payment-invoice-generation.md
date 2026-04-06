---
title: Payment Invoice Generation
category: technical-architecture
subcategory: payments
source_id: 56cd5977
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Payment Invoice Generation

## Overview
After a successful payment, an SQS-triggered Lambda function generates a PDF invoice using Puppeteer, stores it in AWS S3, logs the unique invoice identifier in the `sale_payments` table, and emails the invoice to the customer via Hermes.

## API Contract
N/A — This is an event-driven Lambda function triggered via SQS, not a REST endpoint.

**SQS Queue Names:**
- Production: `prod-invoiceGeneration`
- Development: `dev-invoiceGeneration`

**Lambda Function:** `generateInvoice` (serverless)

## Logic Flow

### Controller Layer
- SQS message received containing `salePaymentId`
- Lambda function `generateInvoice` is invoked
- Any processing failure is logged to `pipeline_failure_tracker`

### Service/Facade Layer
1. **Template Resolution:** Query `invoice_template_specifications` to determine the correct template for the user
2. **Template Fetch:** Retrieve base HTML layout from `invoice_templates` table
3. **PDF Generation:** Render invoice HTML using Puppeteer Node.js module → produce PDF binary
4. **S3 Upload:** Upload PDF to S3 bucket at path `/<unique 10-char string>/original.pdf`
5. **Database Record:** Store the unique 10-character string in `sale_payments.invoice_name` (or equivalent field)
6. **Email Dispatch:** Call Hermes service with `payment_invoice` template, passing S3 reference

### High-Level Design (HLD)
```
POST /payment-callback (Eklavya)
  → DB Updates (sale_payments, student_profile, student_class_balance)
  → Publish to SQS: prod-invoiceGeneration
      → generateInvoice Lambda
          → SELECT invoice_template_specifications (user-specific template rules)
          → SELECT invoice_templates (HTML layout)
          → Puppeteer: render HTML → PDF binary
          → S3 PUT: /{10-char-id}/original.pdf
          → UPDATE sale_payments SET invoice_name = {10-char-id}
          → Hermes: send email (payment_invoice template)
  → Publish to SQS: onboard-flow (parallel)
```

## External Integrations
- **AWS SQS:** `prod-invoiceGeneration` / `dev-invoiceGeneration` queue
- **AWS S3:** Buckets: `brightchamps-invoices` (prod) / `stage-brightchamps-invoices` (staging)
  - Path format: `/<unique 10-char string>/original.pdf`
- **Puppeteer:** Node.js headless browser for HTML-to-PDF rendering
- **Hermes:** Communication service, template: `payment_invoice`

## Internal Service Dependencies
- **Eklavya:** Publishes to SQS after `/payment-callback` DB updates complete
- **Payment-Structure:** Triggers invoice generation Lambda simultaneously with Eklavya callback

## Database Operations

### Tables Accessed
- `invoice_template_specifications` — Defines which template applies to a given user/payment
- `invoice_templates` — Stores HTML layout content for each invoice template
- `sale_payments` — Updated with unique 10-character S3 invoice identifier
- `pipeline_failure_tracker` — Receives error records on Lambda processing failure

### SQL / ORM Queries
- SELECT from `invoice_template_specifications` WHERE (user/payment criteria)
- SELECT from `invoice_templates` WHERE `id = ?`
- UPDATE `sale_payments` SET `invoice_name = '<10-char-string>'` WHERE `id = salePaymentId`
- INSERT into `pipeline_failure_tracker` on exception

### Transactions
- The S3 upload and `sale_payments` update are not explicitly wrapped in a transaction — partial failure risk exists

## Performance Analysis

### Good Practices
- Fully asynchronous via SQS — payment confirmation is not delayed by PDF generation
- Serverless Lambda auto-scales with payment volume
- Template system allows per-user invoice customization without code changes

### Performance Concerns
- Puppeteer is CPU and memory intensive — Lambda memory sizing critical for performance
- Cold start latency on Lambda with Puppeteer can be 3–8 seconds
- No documented retry for failed S3 upload after successful PDF generation (data consistency risk)
- `pipeline_failure_tracker` requires manual intervention for retries

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No atomic transaction between S3 upload and `sale_payments` update — if S3 succeeds but DB update fails, invoice is orphaned |
| Medium | Puppeteer cold starts on Lambda affect invoice delivery SLA |
| Low | `pipeline_failure_tracker` has no automated retry or escalation mechanism |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add DLQ (Dead Letter Queue) to `invoiceGeneration` SQS with automatic retry (3 attempts)
- Set up CloudWatch alarm on `pipeline_failure_tracker` INSERT events

### Month 1 (Architectural)
- Use Lambda Layers or containerized Lambda to pre-install Puppeteer, eliminating cold start overhead
- Add idempotency check: if `sale_payments.invoice_name` is already set, skip re-generation

## Test Scenarios

### Functional Tests
- SQS message triggers Lambda → PDF generated → S3 uploaded → sale_payments updated → email sent
- Correct template selected based on `invoice_template_specifications` rules
- Email received with valid S3-linked PDF attachment

### Performance & Security Tests
- Lambda timeout under high concurrency (>100 simultaneous invoice generation events)
- S3 bucket permissions: verify PDFs are not publicly accessible
- Puppeteer memory consumption per invoice render

### Edge Cases
- `invoice_template_specifications` has no matching rule for user → fallback template or error
- S3 upload fails after PDF is generated → retry logic
- SQS message delivered twice (duplicate) → verify idempotency guard
