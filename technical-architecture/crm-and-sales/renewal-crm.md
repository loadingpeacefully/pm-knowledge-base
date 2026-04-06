---
title: Renewal CRM
category: technical-architecture
subcategory: crm-and-sales
source_id: fc197de7
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Renewal CRM

## Overview
The Renewal CRM flow manages student subscription renewals by creating and updating CRM leads/deals in Zoho CRM (via Prabandhan). It replaces a manual Google Sheets process with structured SQS-driven lead creation, covering three trigger scenarios: low class credits, expiring subscriptions, and fresh new payments.

## API Contract
**SQS Queue:** `prod-prabandhan-process-renewal-crm.fifo`
**Consumer Function:** `processRenewalCrmLead`

**Internal APIs used within the flow:**
- `GET /eklavya/v1/student/overview-data` — Student and payment data
- `GET /paathshala/api/v1/class/paid/overview-data` — Upcoming classes and progress reports
- `GET /dronacharya/api/v1/teacher/lead/details` — Current teacher and team lead CRM data
- `POST /deal/update-crm-deal-to-closed-won` — Prabandhan: close deal on renewal payment

N/A for REST contract — trigger is event-driven via SQS.

## Logic Flow

### Controller Layer
- SQS `prod-prabandhan-process-renewal-crm.fifo` receives message
- `processRenewalCrmLead` consumer function executes

### Service/Facade Layer
**Trigger 1 — Low Credits (Renewal Lead):**
- `updateClassBalanceV2` detects student's class balance drops to ≤ 6 credits
- Pushes student data to SQS queue

**Trigger 2 — Subscription Ending:**
- Daily cron job `triggerSubscriptionEndEvents` runs at 07:50 UTC
- Checks for online/online-group class balances where subscription ends in 30 days AND student has paid classes remaining
- Pushes qualifying students to SQS queue

**Trigger 3 — New Fresh Payment:**
- New payment recorded → invoice generation SQS → subsequently pushes to renewal processing queue
- Creates a "Closed Won" entry (not a pending renewal)

**Consumer Processing (`processRenewalCrmLead`):**
1. Fetch student overview: `/eklavya/v1/student/overview-data`
2. Fetch class data: `/paathshala/api/v1/class/paid/overview-data` (upcoming classes, progress reports, `studentClassBalanceId`)
3. Fetch teacher data: `/dronacharya/api/v1/teacher/lead/details` (teacher + TL CRM data)
4. Currency conversion: convert `sale_payment.amount` and `packageSaleInitiator.total_price` to INR via Platform service
5. Calculate renewal cycle: `count(paid sale_payments) - 1` for closed won; `count(paid sale_payments)` for pending
6. Create/update Zoho CRM lead under "Renewals" layout
7. Unique key: `Student * Course * Class Type * Cycle Count`

**Lead Stages:**
- `Renewal Pending` → `Parent Contacted` → `Appointment Scheduled` → `Pitching Done` → `On Hold` → `Interested` → `Closed Won` / `Closed Lost`

**Activity Syncing:**
- Calls via integrated dialers (Call Hippo, Air Call, Maqsam, Knowlarity) auto-create entries in CRM Activity Tracking subform

### High-Level Design (HLD)
```
TRIGGER 1: updateClassBalanceV2 (credits ≤ 6)
TRIGGER 2: Daily cron 07:50 UTC (subscription ending in 30 days)
TRIGGER 3: New payment recorded
  → SQS: prod-prabandhan-process-renewal-crm.fifo
      → processRenewalCrmLead consumer
          → GET /eklavya: student + payment data
          → GET /paathshala: class data
          → GET /dronacharya: teacher data
          → Platform: currency conversion to INR
          → Calculate cycle count
          → Zoho CRM upsert (Renewals layout)
              → Lead Stage: Renewal Pending | Closed Won
          → Hermes: notifications (if applicable)
```

## External Integrations
- **Zoho CRM:** "Renewals" layout, lead/deal upsert
- **Platform Service:** Currency conversion ratio per date
- **Hermes:** `payment_invoice`, `welcome_onbaord`, `class_schedule_after_onboard` templates
- **Integrated Dialers:** Call Hippo, Air Call, Maqsam, Knowlarity (activity auto-sync)

## Internal Service Dependencies
- **Eklavya:** `student_class_balances`, `sale_payments`, `package_sale_initiators`, `students`, `parents`, `student_profiles`
- **Paathshala:** `paid_classes`, `progress_reports`
- **Dronacharya:** `teachers`, `teacher_profile`
- **Platform:** `timezones`, `countries`, `courses`, `languages`
- **Prabandhan:** `/deal/update-crm-deal-to-closed-won`

## Database Operations

### Tables Accessed
- **Eklavya (read):** `students`, `parents`, `student_class_balances`, `student_profile`, `package_sale_initiators`, `sale_payments`
- **Paathshala (read):** `paid_classes`, `progress_reports`
- **Dronacharya (read):** `teachers`, `teacher_profile`
- **Platform (read):** `timezones`, `countries`, `courses`, `languages`

### SQL / ORM Queries
- SELECT `student_class_balances` WHERE `total_credits <= 6` (low credit trigger)
- SELECT `student_class_balances` WHERE `subscription_end <= NOW() + 30 days AND paid_classes > 0` (subscription trigger)
- COUNT `sale_payments` WHERE `student_id = ? AND status = 'paid'` (cycle count calculation)
- SELECT currency conversion rate from Platform service

### Transactions
- Zoho CRM upsert is the primary write; no multi-table SQL transactions

## Performance Analysis

### Good Practices
- FIFO SQS queue ensures ordered processing of renewal events per student
- Daily cron with UTC timing ensures consistent global execution
- Cycle count uniqueness (`Student * Course * Class Type * Cycle Count`) prevents duplicate renewal leads

### Performance Concerns
- Three sequential microservice API calls (Eklavya, Paathshala, Dronacharya) before CRM update — high latency per message
- Currency conversion requires external Platform service call per lead
- Large student cohorts at end-of-month could cause SQS queue backlog

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Three sequential API calls per renewal lead — no parallel fetching |
| Medium | Cron job at 07:50 UTC processes all expiring subscriptions in bulk — potential thundering herd |
| Low | Activity sync for Maqsam/Knowlarity may not be uniformly implemented across all dialer integrations |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Parallelize Eklavya, Paathshala, and Dronacharya API calls within `processRenewalCrmLead`
- Add SQS dead-letter queue for failed renewal lead processing

### Month 1 (Architectural)
- Spread cron trigger across time windows instead of single UTC burst
- Cache currency conversion rates (TTL: 1 day) to avoid repeated Platform service calls

## Test Scenarios

### Functional Tests
- Low credits trigger: student at 6 credits → renewal lead created in Zoho
- Subscription trigger: subscription ending in 30 days → lead created
- Fresh payment trigger: new payment → Closed Won lead created
- Cycle count: 3rd paid payment → cycle count = 2 (for pending) or 2 for closed won

### Performance & Security Tests
- 1,000 simultaneous low-credit triggers — SQS throughput and processing latency
- Zoho CRM API rate limit handling under bulk renewal processing

### Edge Cases
- Student with multiple courses: separate renewal leads per course
- Subscription ending trigger fires same day as low-credits trigger — deduplification
- Teacher not assigned to student — Dronacharya returns null, default values used
