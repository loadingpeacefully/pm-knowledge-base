---
title: Class Details for Teacher API
category: technical-architecture
subcategory: api-specifications
source_id: 9ec46799
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Class Details for Teacher API

## Overview
The Class Details for Teacher API aggregates student class balance, upcoming curriculum data, and personalized teacher instructions for the teacher dashboard. It is powered by a background Lambda function (`upcomingClassDetails`) that pre-computes up to 3 contextual pointers per class 24 hours in advance, storing them in `paid_class_metrics` for low-latency retrieval at class time.

## API Contract

The specific HTTP method and exact endpoint path are not documented in the source. The API serves the student progress/profile page on the teacher dashboard.

**Data Returned (from aggregate sources):**
1. **Student Class Balance** — Credits, total booked, completed classes
2. **Curriculum Data** — Upcoming project details, homework, quizzes, assignments, assessments
3. **Teacher Instructions/Pointers** (max 3 per class):
   - Is this the student's first class at BrightChamps or first class with this specific teacher?
   - Has the student paused, cancelled, or missed previous classes?
   - Has the student recently earned a certificate?
   - Are there pending package renewals or upcoming installments?
   - Is the student's average class count for the last month below threshold?
   - Has the student missed or failed their last assignment/quiz/assessment?

**Internal API Calls Made:**
- `GET /v1/student-class-balance` (Eklavya service) — for class balance data
- Paathshala DB queries — for upcoming project and assessment details
- `paid_class_metric` table read — for pre-computed teacher pointers

## Logic Flow

### Controller Layer
Teacher dashboard → Class Details API → aggregate response from Eklavya + Paathshala DB

### Service/Facade Layer
**Real-time API Response:**
1. Fetch student class balance from Eklavya `/v1/student-class-balance`
2. Query Paathshala DB for upcoming project and assessment details
3. Read `paid_class_metric` table for pre-computed teacher pointers (max 3)
4. Assemble and return combined response

**Background Pre-computation (`upcomingClassDetails` Lambda):**
1. Cron triggers Lambda for classes in next 24 hours
2. Lambda calls `PaidClassService.upcomingClassDetails()`
3. For each upcoming class:
   - Fetch class details from Paathshala DB
   - Fetch booking details from Tryouts `/v1/booking/details`
   - Fetch teacher earnings from Dronacharya
   - Evaluate 6 pointer conditions (see above)
   - Select top 3 most relevant pointers
   - Store in `paid_class_metrics(metric_key = 'teacher_pointer', value = ...)`

### High-Level Design (HLD)
- Lambda pre-computation ensures API response is fast at class time (no heavy computation inline)
- Maximum 3 pointers per class prevents information overload for teachers
- Cross-service data aggregation: Eklavya + Paathshala + Tryouts + Dronacharya

## External Integrations
N/A — All data sources are internal microservices.

## Internal Service Dependencies
- Eklavya (Student Service): `/v1/student-class-balance` for balance data
- Tryouts (Demo Booking): `/v1/booking/details` for booking context in Lambda
- Dronacharya (Teacher Service): Teacher earnings data in Lambda
- Paathshala (Class Service): `paid_class_metrics` table, curriculum/project data

## Database Operations

### Tables Accessed

**`paathshala.paid_class_metrics`:**
| Column | Notes |
|--------|-------|
| metric_key | e.g., 'teacher_pointer' |
| value | Pointer text/data |

**`paathshala.paid_classes`:** Class schedule and status data

**Tables queried by `upcomingClassDetails` Lambda:**
- `PaidClass`
- `PaidClassMetric`
- `StudentClassBalance`
- `Booking`
- `DemoClasses`
- `DemoClassFeedbacks`
- `TeacherChangeRequests`
- `PaidClassFeedback`
- `Certificates`

### SQL / ORM Queries
- SELECT classes WHERE `start_time BETWEEN NOW() AND NOW() + 24 hours`
- Multi-table SELECT to evaluate 6 pointer conditions per class
- UPSERT `paid_class_metrics` per class with up to 3 pointer records
- JOIN `Certificates` to check recent certificate earned
- JOIN `PaidClassFeedback` to check last assignment/quiz status

### Transactions
N/A — Lambda writes are individual UPSERTs per class, not wrapped in transactions.

## Performance Analysis

### Good Practices
- Background pre-computation via Lambda eliminates real-time DB overhead at class time
- Strict 3-pointer cap prevents payload bloat
- Cross-service calls are made in Lambda (background) not inline with user request

### Performance Concerns
- Lambda must process all 24-hour upcoming classes within its execution window — could be slow for high class volumes
- If Lambda fails or is delayed, API returns stale/empty pointers

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No fallback documented if `paid_class_metrics` is empty when teacher loads class details |
| Low | Specific HTTP method and endpoint path not documented in source |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add fallback logic in the API to compute pointers inline if `paid_class_metrics` is empty
- Add Lambda execution alerting when processing time exceeds 80% of the 24-hour window

### Month 1 (Architectural)
- Implement incremental Lambda runs (every 2 hours for classes in next 2 hours) instead of one 24-hour batch
- Cache computed pointers in Redis with class-time TTL for faster API reads

## Test Scenarios

### Functional Tests
- Lambda runs and populates `paid_class_metrics` for all classes in next 24 hours
- Teacher loads class details → correct 3 pointers displayed
- Student with no prior classes → "first class" pointer generated
- Student with missed last assignment → assignment pointer included

### Performance & Security Tests
- Verify only the assigned teacher can view class details for their class
- Benchmark Lambda execution time for 500 upcoming classes

### Edge Cases
- All 6 pointer conditions true → only top 3 selected (selection criteria unclear in source)
- Lambda fails mid-run → partial metrics in DB → API must handle incomplete data
- Class cancelled after Lambda runs → stale metrics remain in `paid_class_metrics`

## Async Jobs & Automation
- **`upcomingClassDetails` Lambda (Cron-triggered):** Pre-computes teacher pointers for all classes in the next 24 hours; writes to `paid_class_metrics`
