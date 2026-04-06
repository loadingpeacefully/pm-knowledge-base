---
title: Student Class Information to ZOHO
category: technical-architecture
subcategory: crm-and-sales
source_id: 0a5562cd
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Student Class Information to ZOHO

## Overview
A daily cron job pushes student class progress metrics (total booked, paid, and completed classes) to the Deals module in Zoho CRM. It targets students who completed or missed a class the previous day and whose remaining paid classes are ≤ 6, ensuring renewal sales managers have current data for outreach.

## API Contract
**Internal Endpoint:** `POST /student-balance` (Prabandhan)
- Receives batched student class balance data from Eklavya
- Processes and pushes to Zoho CRM

**Trigger:** Daily cron job (Eklavya)

**Zoho CRM Update (via Prabandhan upsert service):**
- Module: `Deals`
- Operation: `upsertToZoho`
- Payload per deal:
```json
{
  "id": "zoho_deal_id",
  "Deal_Name": "string",
  "Total_Classes_Booked": "number",
  "Total_Classes_Completed": "number",
  "Total_Classes_Paid": "number"
}
```

**Trigger Condition (SQL):**
```sql
SELECT student_class_balance
WHERE updated_at BETWEEN yesterday_start AND yesterday_end
  AND (total_paid_class - total_completed_class) <= 6
```

## Logic Flow

### Controller Layer
- Daily cron triggers Eklavya to query `student_class_balance`
- Batched data sent to `POST /student-balance` (Prabandhan)
- Prabandhan maps data and pushes to Zoho CRM

### Service/Facade Layer
1. **Cron Execution (Eklavya):**
   - `findAll` on `StudentClassBalance` WHERE `updated_at = yesterday` AND `(total_paid_class - total_completed_class) <= 6`
   - Batch results → `POST /student-balance` (Prabandhan)

2. **Prabandhan Processing:**
   a. Fetch `master_courses` from Platform service → build `courseName → courseId` hashmap
   b. Build `dealHashmap` keyed by `studentId_courseId` → store class balance metrics
   c. For each student:
      - Lookup primary deal in `db_crm_deals` by `studentId + courseId`
      - Also lookup support deals (for multi-deal scenarios)
   d. **Legacy Fallback:** If support deal not in local DB → query Tryouts `getBookingDetailsByFilter` → store as legacy support deal via `placeLegacySupportDealInDb`
   e. Build Zoho upsert payload array (primary + support deals)
   f. `zohoCRMService.upsertToZoho` → Deals module → batch UPDATE

3. **Zoho Payload Fields:**
   - `id` (Zoho deal ID)
   - `Deal_Name`
   - `Total_Classes_Booked`
   - `Total_Classes_Completed`
   - `Total_Classes_Paid`

### High-Level Design (HLD)
```
Daily Cron (Eklavya)
  → SELECT student_class_balance
      WHERE updated_at = yesterday
      AND (total_paid_class - total_completed_class) <= 6
  → Batch → POST /student-balance (Prabandhan)
      → Platform: master_courses (courseId mapping)
      → Build dealHashmap (studentId_courseId → metrics)
      → For each student:
          → db_crm_deals: find primary + support deals
          → IF support deal missing: Tryouts fallback + placeLegacySupportDealInDb
          → Build Zoho payload array
      → zohoCRMService.upsertToZoho (Deals module, batch)
```

## External Integrations
- **Zoho CRM:** Deals module batch upsert
- **Platform Service:** `master_courses` for courseId mapping

## Internal Service Dependencies
- **Eklavya:** `student_class_balance` daily query + cron job
- **Prabandhan:** `db_crm_deals` (NoSQL), `POST /student-balance`, Zoho upsert service
- **Tryouts:** `getBookingDetailsByFilter` (legacy support deal fallback)

## Database Operations

### Tables Accessed
- **Eklavya SQL:** `student_class_balance` — daily filtered query
- **Prabandhan NoSQL:** `db_crm_deals` — deal lookup by studentId+courseId
- **Platform SQL:** `master_courses` — courseId mapping

### SQL / ORM Queries
- SELECT `student_class_balance` WHERE `updated_at > ? AND updated_at < ? AND (total_paid_class - total_completed_class) <= 6`
- `db_crm_deals.find({ studentId, courseId })` — primary and support deals
- `db_crm_deals.insertOne(legacySupportDeal)` — legacy support deal persistence
- Zoho: batch `upsertToZoho` for all deals in payload array

### Transactions
- No SQL transactions — sequential reads and Zoho batch write

## Performance Analysis

### Good Practices
- Batched Zoho upsert reduces API call count vs. per-student calls
- `(total_paid_class - total_completed_class) <= 6` filter ensures only renewal-relevant students are pushed
- `dealHashmap` by `studentId_courseId` provides O(1) deal lookup within the batch

### Performance Concerns
- Daily cron processes all qualifying students in one batch — potential large batch size at scale
- Platform service call per batch (not per student) — reasonable
- Legacy support deal fallback adds Tryouts API call per missing deal — N+1 concern for students without local deal records
- Zoho API rate limits under large batch upserts

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Legacy support deal fallback (Tryouts API call) is N+1 for students missing local deal records |
| Medium | Cron runs once daily — data can be up to 24 hours stale in Zoho CRM |
| Low | `(total_paid_class - total_completed_class) <= 6` threshold hardcoded |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Pre-populate legacy support deal records during booking creation to eliminate fallback Tryouts calls
- Make the `<= 6` class threshold configurable via admin settings

### Month 1 (Architectural)
- Replace daily cron with event-driven update: trigger Zoho sync whenever `student_class_balance` is updated
- Implement Zoho API rate limit handling with exponential backoff in `upsertToZoho`

## Test Scenarios

### Functional Tests
- Student with 4 remaining classes → included in daily batch → Zoho deal updated
- Student with 10 remaining classes → excluded from batch
- `Total_Classes_Booked`, `Total_Classes_Completed`, `Total_Classes_Paid` all correctly populated in Zoho
- Legacy support deal not in local DB → Tryouts fallback → persisted → Zoho updated

### Performance & Security Tests
- 5,000 qualifying students in one daily batch — Zoho upsert throughput and rate limit handling
- Cron failure (Eklavya down) → job missed → catch-up mechanism

### Edge Cases
- Student has multiple courses — separate Zoho deal records updated per courseId
- Zoho deal deleted externally — upsert creates new deal (if upsert behavior is insert on missing ID)
- `total_paid_class` = 0 (newly enrolled) → edge case on difference calculation
