---
title: Upcoming Class Details Lambda Function
category: technical-architecture
subcategory: api-specifications
source_id: 69b26230
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Upcoming Class Details Lambda Function

## Overview
The `upcomingClassDetails` Lambda function is a scheduled background job that pre-computes contextual teacher pointers for all paid classes scheduled in the next 24 hours. It aggregates data from Paathshala, Tryouts, and Dronacharya to generate up to 3 actionable instructions per class, storing them in `paid_class_metrics` for the Class Details for Teacher API to serve at runtime.

## API Contract

N/A — This is a Lambda function invoked by a cron job. It does not expose an HTTP endpoint. It consumes internal APIs:
- `GET /v1/booking/details` (Tryouts) — booking context per class
- `GET /dronacharya/api/v1/teacher/earnings` (Dronacharya) — teacher earnings data

## Logic Flow

### Controller Layer
EventBridge Cron → Lambda invocation → `PaidClassService.upcomingClassDetails()`

### Service/Facade Layer

**Processing Flow for Each Upcoming Class:**
1. Fetch all paid classes scheduled in next 24 hours from Paathshala DB
2. For each class:
   a. Fetch booking details from Tryouts `GET /v1/booking/details`
   b. Fetch teacher earnings from Dronacharya
   c. Evaluate 6 pointer conditions (in priority order):
      1. Is this the student's **first class at BrightChamps** or first with this teacher?
      2. Has the student recently **paused, cancelled, or missed** classes?
      3. Has the student **earned a certificate** after their previous class?
      4. Are there **pending package installments or renewals**?
      5. Is the student's **average class count for last month** below threshold?
      6. Has the student **missed or failed** their last assignment/quiz/assessment?
   d. Select top 3 most relevant pointers
   e. UPSERT into `paid_class_metrics(metric_key='teacher_pointer', value=<pointer_text>)`

### High-Level Design (HLD)
- Lambda is the pre-computation layer for the Class Details for Teacher API
- MySQL database used (AWS RDS)
- Maximum 3 pointers per class to avoid teacher information overload
- All 6 conditions evaluated; selection of top 3 not fully specified in source

## External Integrations
N/A — All data sources are internal microservices.

## Internal Service Dependencies
- Paathshala (Class Service): Core class schedule and DB tables
- Tryouts (Demo Booking): `/v1/booking/details` for student booking context
- Dronacharya (Teacher Service): Teacher earnings data

## Database Operations

### Tables Accessed

**Paathshala DB Tables:**
| Table | Notes |
|-------|-------|
| `PaidClass` | Upcoming class schedule |
| `PaidClassMetric` | Output: stores computed pointers |
| `StudentClassBalance` | Class balance and history |
| `Booking` | Student booking details |
| `DemoClasses` | Demo class history |
| `DemoClassFeedbacks` | Demo feedback history |
| `TeacherChangeRequests` | Any teacher change history |
| `PaidClassFeedback` | Assignment/quiz/assessment completion |
| `Certificates` | Certificate earned after last class |

### SQL / ORM Queries
- SELECT `PaidClass` WHERE `start_time BETWEEN NOW() AND NOW() + INTERVAL 24 HOUR`
- JOIN `StudentClassBalance` for balance and completion history
- JOIN `Certificates` to check if most recent class earned a certificate
- JOIN `PaidClassFeedback` to check last assignment/quiz status
- UPSERT `PaidClassMetric` per class with up to 3 pointer records

### Transactions
N/A — Individual UPSERT per metric; no multi-table transaction.

## Performance Analysis

### Good Practices
- Background pre-computation ensures the teacher-facing API is fast at class time
- Max 3 pointers limits output payload size
- MySQL on AWS RDS provides reliable performance for batch reads

### Performance Concerns
- Sequential per-class processing (cross-service calls for bookings and earnings) scales poorly for high class volumes
- If Lambda fails mid-run, partial pointer data in DB may cause inconsistent API responses

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Sequential cross-service calls per class within Lambda — should use batch APIs |
| Low | Selection logic for "top 3 from 6" conditions not fully specified in source |
| Low | No incremental run strategy — single 24-hour batch could miss classes for newly scheduled sessions |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Replace per-class Tryouts API call with a batch endpoint (e.g., POST with array of class IDs)
- Add Lambda execution monitoring and alerting on failures

### Month 1 (Architectural)
- Switch from single 24-hour batch to incremental runs (every 2 hours, processing next 2 hours of classes)
- Cache computed pointers in Redis keyed by `classId` with TTL = class start time + 1 hour

## Test Scenarios

### Functional Tests
- Lambda runs → all classes in next 24 hours have `paid_class_metrics` entries
- Class with all 6 conditions true → only 3 metrics stored
- First class for student → "first class" pointer generated
- Student missed last homework → assignment pointer included
- Student has pending installment → renewal reminder pointer included

### Performance & Security Tests
- Lambda execution time benchmark for 500 upcoming classes
- Verify Lambda IAM role does not have overly broad DB access

### Edge Cases
- No classes in next 24 hours → Lambda completes with no DB writes
- Cross-service API call fails for one class → Lambda should continue with remaining classes (error per class, not fail-all)
- Class cancelled after Lambda runs → stale metrics remain until next Lambda run

## Async Jobs & Automation
- **EventBridge Cron → `upcomingClassDetails` Lambda:** Scheduled trigger (exact cron schedule not documented in source); runs to process all classes in the next 24-hour window
