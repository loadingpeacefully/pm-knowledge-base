---
title: Auxo Prediction
category: technical-architecture
subcategory: student-lifecycle
source_id: 4ee039ff
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Auxo Prediction

## Overview
The Auxo Prediction system forecasts the number of teachers required for upcoming demo class slots using a weighted 4-week historical joining rate average. It runs within the Tryouts (Demo Booking/Predictions) service and drives the teacher availability marking and confirmation pipeline, applying a 30% safety buffer to all predictions.

## API Contract

N/A — Auxo Prediction operates entirely via scheduled cron jobs and internal service data. No external HTTP API endpoints are documented for this subsystem.

## Logic Flow

### Controller Layer
Cron-triggered Lambda functions driving prediction pipeline.

### Service/Facade Layer

**Prediction Algorithm:**
1. For each datetime-combination ID group, fetch joining rates from the past 4 identical weekday-time slots (e.g., last 4 Tuesdays at 07:30:00Z)
2. Calculate weighted average:
   - W1 (most recent week) = 32.5
   - W2 = 30
   - W3 = 22.5
   - W4 (oldest week) = 15
   - `predicted_joining_rate = (rate_w1 × 32.5 + rate_w2 × 30 + rate_w3 × 22.5 + rate_w4 × 15) / 100`
3. Apply 30% buffer:
   ```
   teacher_predicted_leads = predicted_leads + (predicted_leads × 0.3)
   ```
4. Update `demo_booking_predictions` with predictions for next 3 days

**Availability Marking (17th minute):**
1. Run availability marking for all teachers
2. Compare `teacher_availity_marked` vs. `teacher_predicted_leads`
3. If more teachers available than required → rank by historical conversion rate → select top teachers only

**Confirmation (Every 30 minutes):**
1. Confirm teachers for slots occurring in next 1h, 3h, and 6h
2. Confirm `30% of permutations + 10% buffer`
3. Emit confirmation event to Teacher Service (Dronacharya) → update `teacher_avaialbility.confirmed = true`

**Joining Rate Collection (Every 30 minutes):**
1. Fetch actual joining rates of most recently completed classes per combination ID
   - e.g., at 12:00 PM: retrieve 11:30 AM 30-min class and 11:00 AM 60-min class data
2. Store in `combination_joining_rates`

### High-Level Design (HLD)
- Tryouts service owns the entire prediction pipeline
- Weighted average uses 4-week same-weekday-same-time historical data
- Safety buffer of 30% prevents coverage gaps due to late-joining teachers
- Teacher selection uses conversion rate ranking when supply > demand
- Cron jobs run at precise intervals tied to class start times

## External Integrations
- **Teacher Service (Dronacharya):** Receives confirmation events; updates `teacher_avaialbility.confirmed`

## Internal Service Dependencies
- `tryouts.bookings`: Source for `total_leads` and `filtered_leads`
- `combination_joining_rates`: Historical joining rate input for prediction
- `demo_booking_predictions`: Output table for predictions and tracking
- Teacher conversion rate data (from teacher profile or metrics tables)

## Database Operations

### Tables Accessed

**`combination_joining_rates`:**
| Column | Notes |
|--------|-------|
| joining_rate | Actual joining rate per combination per class slot |
| (combination_id, datetime implied) | Grouping keys |

**`demo_booking_predictions`:**
| Column | Notes |
|--------|-------|
| total_leads | Gross bookings from `tryouts.bookings` |
| filtered_leads | Valid leads (excluding cancelled/unqualified) |
| predicted_leads | Exact number of teachers to confirm |
| teacher_predicted_leads | Teachers to request availability from (includes 30% buffer) |
| teacher_availity_marked | Count of teachers who marked availability |
| teacher_confirmed | Count of confirmed teachers |

### SQL / ORM Queries
- SELECT `combination_joining_rates` for past 4 identical weekday-time slots per combination ID
- Weighted average calculation performed in application layer
- UPSERT `demo_booking_predictions` with new predicted values per (combination_id, datetime)
- INSERT into `combination_joining_rates` every 30 minutes with actual class joining rates

### Transactions
- UPSERT on `demo_booking_predictions` is an atomic insert-or-update per combination+datetime key

## Performance Analysis

### Good Practices
- 4-week weighted average smooths out single-week anomalies (holidays, outages)
- Weights favor recency (W1=32.5) while maintaining historical context (W4=15)
- 30% buffer ensures teacher supply slightly exceeds demand
- Conversion-rate ranking maximizes confirmation quality when supply > demand

### Performance Concerns
- Prediction cron runs every 15 minutes — generates writes across all combination IDs for 3 days (~potentially thousands of rows)
- Joining rate collection at 30-minute intervals could miss sub-30-minute class variations

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | Weight constants (32.5, 30, 22.5, 15) are hard-coded — should be configurable to allow A/B testing of prediction models |
| Low | No documented alerting when `teacher_confirmed < predicted_leads` threshold is breached |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add alert/notification when `teacher_confirmed` significantly lags `predicted_leads` within 2 hours of class start
- Make weight constants configurable via `ConfigManager` for model tuning

### Month 1 (Architectural)
- Introduce holiday/event calendar awareness into the prediction model
- Evaluate expanding from 4-week to 8-week history with additional weight decay for older data

## Test Scenarios

### Functional Tests
- Prediction cron generates correct weighted average for a known joining rate history
- 30% buffer correctly applied: `predicted_leads = 10` → `teacher_predicted_leads = 13`
- Joining rate collection at 12:00 PM captures both 11:30 AM (30-min) and 11:00 AM (60-min) classes
- Confirmation cron sends correct number of teacher confirmations for 1h/3h/6h slots

### Performance & Security Tests
- Verify prediction cron handles 500+ combination IDs within its 15-minute run window
- Benchmark UPSERT performance on `demo_booking_predictions` at scale

### Edge Cases
- Only 2 weeks of joining rate history available (should use available weeks only)
- All 4 historical rates are 0 (no bookings in past month → `predicted_leads = 0`)
- `teacher_availity_marked = 0` when prediction says 10 needed → ops visibility required

## Async Jobs & Automation
- **Every 30 minutes:** Collect actual joining rates of completed classes → INSERT into `combination_joining_rates`
- **Every 15 minutes:** Calculate weighted average predictions per combination ID for next 3 days → UPSERT `demo_booking_predictions`
- **At the 17th minute:** Run availability marking; rank and trim teachers if supply > demand based on conversion rate
- **Every 30 minutes:** Confirm teachers for upcoming 1h, 3h, 6h slots; emit confirmation event to Dronacharya
