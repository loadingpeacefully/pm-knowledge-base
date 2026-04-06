---
title: Sales Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: b7002f2d
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Sales Flow

## Overview
The sales flow covers the complete end-to-end journey from demo booking to deal closure. It spans four phases: Demo Booking & Lead Creation, Demo Completion & Deal Creation, Payment Initiation & Completion, and Onboarding & CRM Deal Closure.

## API Contract
**Key Endpoints Across Phases:**

Phase 1:
- `POST /lead/create-db-crm-lead` (Prabandhan)
- Tryouts `bookings` table → SQS → Eklavya `mapStudenWithBooking` Lambda

Phase 2:
- `POST /hotlead` (Tryouts) — Teacher flags hot lead
- `GET /prabandhan/v1/hotlead/channels/filters` — Channel assignment

Phase 3:
- `POST /v2/initiate-payment` (Eklavya)
- `POST /v1/payment-initiation/create-payment` (Payment-Structure)
- `POST /v1/payment-initiation/payment-link` (Payment-Structure)

Phase 4:
- `POST /deal/update-crm-deal-to-closed-won` (Prabandhan)
- `POST /curriculum/student/module` (Paathshala)

## Logic Flow

### Controller Layer
- Booking confirmation triggers async Lambda chain via SQS
- Class completion triggers SNS → Prabandhan SQS → Lambda
- Payment webhook triggers DB updates and SQS downstream queues
- Onboard flow Lambda calls Paathshala and Prabandhan APIs synchronously

### Service/Facade Layer
**Phase 1 — Demo Booking:**
1. Student submits details on landing page → tracker API stores in MongoDB
2. Booking confirmed → `bookings` table INSERT in Tryouts
3. `bookingObjectId` pushed to SQS → `mapStudenWithBooking` Lambda (Eklavya)
4. Lambda: find/create `parents` and `students` records by phone number
5. Prabandhan: `POST /lead/create-db-crm-lead` → Eklavya fetch → Zoho upsert
6. CRM Lead status: `Not Contacted`
7. Hermes: booking confirmation + reminders (WhatsApp + Email)

**Phase 2 — Demo Completion:**
1. Teacher submits post-class feedback → SNS published → Prabandhan SQS
2. `prabandhan-class-completion-flow` Lambda:
   - Fetch `demoClassId` → Paathshala booking details
   - `createDBCRMDeal` function: find existing lead → convert to deal
3. Zoho upsert: Deal stage = `Demo Completed`
4. Append notes: WhatsApp link + dashboard link via `/deal/add-notes-in-crm-deal`
5. Optional: Teacher marks `hotlead` → `POST /hotlead` → Slack channel routing → SM claims → deal owner updated

**Phase 3 — Payment:**
1. Eklavya `POST /v2/initiate-payment` → Payment-Structure `POST /v1/payment-initiation/create-payment`
2. `POST /v1/payment-initiation/payment-link` → aggregator link generation
3. Payment gateway webhook → `payment_transaction_info` updated
4. Eklavya `/payment-callback`: `sale_payments` = paid, `total_credits` updated, `total_booked_class` updated

**Phase 4 — Onboarding & CRM Closure:**
1. SQS: `invoice-generation` → Puppeteer PDF → S3 → Hermes `payment_invoice`
2. SQS: `onboard-flow` (if first payment):
   - Hermes: `welcome_onbaord` + `class_schedule_after_onboard`
   - Paathshala: `/curriculum/student/module`
   - Prabandhan: `/deal/update-crm-deal-to-closed-won` → Deal stage = `Closed Won`

### High-Level Design (HLD)
```
[Booking] → Tracker → MongoDB → SQS → Eklavya (parents/students) → Prabandhan (Lead: Not Contacted)
       → Hermes (confirmation + reminders)

[Demo Class] → Teacher feedback → SNS → Prabandhan SQS → Lambda
       → Deal created (Demo Completed)
       → Optional: Hotlead → Slack → SM claims → Deal owner assigned

[Payment] → Eklavya → Payment-Structure → Aggregator → Webhook → DB updates

[Onboarding] → SQS (invoice + onboard) → Invoice email + Welcome emails + Paathshala + CRM Closed Won
```

## External Integrations
- **Zoho CRM:** Lead creation, deal creation, deal closure via Prabandhan
- **Hermes:** Booking confirmations, reminders, welcome emails, invoice
- **AWS SNS/SQS:** Class completion event routing
- **Slack:** Hot lead notification and SM claim mechanism
- **Paathshala:** Demo class feedback, curriculum provisioning
- **Payment Aggregators:** Stripe, Razorpay, PayPal, Tabby, etc.

## Internal Service Dependencies
- **Tryouts:** Booking management, hot lead API
- **Eklavya:** Student/parent creation, payment callback, class balance
- **Prabandhan:** CRM microservice (lead/deal management)
- **Paathshala:** Class data, curriculum provisioning
- **Dronacharya:** Teacher data
- **Payment-Structure:** Payment initiation and link generation
- **Hermes:** Email/WhatsApp communications

## Database Operations

### Tables Accessed
- **MongoDB (Tracker):** Raw booking requests
- **Tryouts:** `bookings` table
- **Eklavya:** `parents`, `students`, `sale_payments`, `student_profile`, `student_class_balance`, `payment_initiations`
- **Paathshala:** `demo_classes`, `paid_classes`, `progress_reports`
- **Prabandhan (NoSQL):** `db_crm_deals`
- **Prabandhan (SQL):** `crm_users`, `master_group_filters`, `group_user_mappings`

### SQL / ORM Queries
- INSERT `bookings` (Tryouts)
- findOrCreate `parents` by phone (Eklavya)
- INSERT/UPDATE `students` (Eklavya)
- INSERT `db_crm_deals` on deal creation (Prabandhan NoSQL)
- UPDATE `sale_payments` SET `status = 'paid'` (Eklavya)

### Transactions
- `mapStudenWithBooking` Lambda wraps parent/student create in SQL transaction
- `/payment-callback` wraps sale_payments + student_profile + student_class_balance updates atomically

## Performance Analysis

### Good Practices
- Event-driven architecture (SQS/SNS) decouples each phase, preventing cascading failures
- Atomic transactions on critical DB operations (student creation, payment callback)
- Hot lead routing provides real-time sales opportunity capture

### Performance Concerns
- Long chain of async events — end-to-end tracing is complex (booking → lambda → CRM → payment → onboard)
- Class completion → deal creation path has multiple sequential microservice calls
- No documented end-to-end distributed tracing

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No distributed tracing across the multi-service sales flow |
| Medium | Class completion → Prabandhan lambda has no documented retry on Zoho upsert failure |
| Low | Hermes WhatsApp reminder scheduling not tied to deal state — could send after payment |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add correlation IDs across SQS messages for end-to-end tracing
- Add DLQs to all intermediate SQS queues in the sales flow

### Month 1 (Architectural)
- Implement distributed tracing (AWS X-Ray or equivalent) across Tryouts → Eklavya → Prabandhan → Payment-Structure
- Unify booking event stream into a single event bus (EventBridge) instead of point-to-point SQS

## Test Scenarios

### Functional Tests
- Full happy path: booking → demo → hotlead claimed → payment → onboarding
- Non-hotlead path: SM auto-assigned via group filter → payment → CRM closed won
- First payment gate: welcome emails sent only once

### Performance & Security Tests
- 100 concurrent demo completions → CRM update throughput
- Hot lead race condition: two SMs claim simultaneously — only first succeeds

### Edge Cases
- Demo class marked failed (not successful) — no deal created
- Student payment for non-demo booking (`isDemo = false`) — deal created immediately
- Onboard flow fails after invoice is generated — partial state recovery
