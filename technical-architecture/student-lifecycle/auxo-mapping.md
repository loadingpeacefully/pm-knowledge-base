---
title: Auxo Mapping
category: technical-architecture
subcategory: student-lifecycle
source_id: f2ec7acd
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Auxo Mapping

## Overview
The Auxo Mapping system performs real-time teacher-student matching when participants join a demo class. It uses Redis sorted sets (keyed by class start time and combination) to queue and rank waiting teachers by conversion rate, and FIFO queue processing via the Tryouts service to assign the highest-performing available teacher to each joining student.

## API Contract

N/A — Auxo Mapping operates via inter-service message queue communication rather than HTTP endpoints. Paathshala checks mapping state and routes requests to Tryouts via a FIFO queue when unmapped.

## Logic Flow

### Controller Layer
Zoom join event → Paathshala checks teacher-student mapping → if unmapped, push to FIFO queue → Tryouts service processes mapping

### Service/Facade Layer

**Teacher Join Flow:**
1. Receive payload: `{ "teacherConfirmationId": 1 }`
2. Fetch teacher's booking time, combination IDs, and conversion rate
3. Check for waiting students (joined but not yet mapped to a teacher)
4. If waiting student's combination ID matches teacher's combination → map immediately
5. If no waiting students → push teacher's combination IDs to Redis sorted sets:
   - Key pattern: `teachers-${classStartTime}-${combination}`
   - Score = teacher's conversion rate (higher = higher priority in sorted set)
   - Store sorted sets in Redis Hashmap

**Student Join Flow:**
1. Receive payload: `{ "bookingId": 1 }`
2. Fetch student's booking time and combination ID
3. Search Redis key: `teachers-${classStartTime}-${studentCombination.id}` for waiting teachers
4. If teachers found:
   - Pop highest-conversion-rate teacher: `redisClient.zRange(key, 0, 0, { REV: true })`
   - Map teacher to student
5. If no teacher found → place student in empty room
   - Future improvement: check backup combinations table before assigning empty room

**Architecture Assumption:**
- Optimized for teachers joining before students (most common case)
- Reverse case (student waits for teacher) is also handled via the Redis sorted set lookup path

### High-Level Design (HLD)
- Paathshala (Class Service) detects join events and delegates mapping to Tryouts via FIFO queue
- Redis sorted sets store waiting teachers per (classStartTime, combination) with conversion rate as score
- Current turnaround time: 1–2 seconds
- Scalability plan: build backup combinations table for fallback when no teacher matches primary combination

## External Integrations
- **Redis:** Sorted sets and Hashmap for real-time teacher queue management

## Internal Service Dependencies
- Paathshala: Detects join events; checks existing teacher-student mapping; routes unmapped joins to FIFO queue
- Tryouts: Processes FIFO queue; executes teacher-student mapping
- `demo_booking_predictions` + `combination_joining_rates`: Provide conversion rate and combination data

## Database Operations

### Tables Accessed

**`combination_joining_rates`:**
| Column | Notes |
|--------|-------|
| joining_rate | Historical joining rate per combination |

**`demo_booking_predictions`:**
| Column | Notes |
|--------|-------|
| total_leads | Gross booking count |
| filtered_leads | Net valid leads |
| predicted_leads | Teachers to confirm |
| teacher_predicted_leads | Teachers to request availability from |
| teacher_availity_marked | Count who marked availability |
| teacher_confirmed | Count confirmed |

**Redis Keys:**
- `teachers-${classStartTime}-${combination}` (sorted set, score = conversion rate)
- Hashmap for Redis sorted set storage

### SQL / ORM Queries
- SELECT teacher's `bookingTime`, `combinationIds`, `conversionRate` using `teacherConfirmationId`
- SELECT student's `bookingTime`, `combinationId` using `bookingId`
- `redisClient.zRange(key, 0, 0, { REV: true })` — pop highest conversion rate teacher

### Transactions
N/A — Redis operations are atomic; DB mapping updates are single writes.

## Performance Analysis

### Good Practices
- Redis sorted sets with conversion rate scoring ensure highest-performing teachers are matched first
- FIFO queue in Paathshala prevents race conditions in concurrent join processing
- Teacher-joins-first assumption matches real-world class start behavior

### Performance Concerns
- Current turnaround: 1–2 seconds — may feel slow for students joining very active slots
- No fallback for mismatched combinations → student goes to empty room without trying adjacent combinations

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No backup combination fallback implemented — students with no exact combination match go to empty rooms instead of trying adjacent combinations |
| Medium | 1–2 second turnaround documented as a target for reduction |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Implement backup combinations table and check adjacent combinations before assigning empty room
- Reduce Redis key expiry to be tied to class end time to prevent stale keys

### Month 1 (Architectural)
- Pre-warm Redis sorted sets 5 minutes before class start using confirmed teacher list
- Build observability dashboard for real-time match success rate and empty-room frequency

## Test Scenarios

### Functional Tests
- Teacher joins before student → teacher stored in Redis sorted set
- Student joins → highest conversion rate teacher popped from Redis → mapped
- Two teachers with different conversion rates → higher-rate teacher selected first
- Student joins with no matching teacher in Redis → placed in empty room
- Teacher joins when waiting student already in room → immediate mapping without Redis lookup

### Performance & Security Tests
- Simulate 100 concurrent class starts at the same time slot and verify mapping correctness
- Verify Redis sorted set is cleaned up after class ends

### Edge Cases
- Student combination ID has no matching Redis key (no teachers for that combination)
- Teacher's combination IDs span multiple slots → multi-key insertion in Redis
- Redis eviction removes a teacher entry before student joins

## Async Jobs & Automation
- **FIFO Queue (Paathshala → Tryouts):** Routes unmapped join events for teacher-student matching
- **Prediction Cron (Every 15 min):** Updates `demo_booking_predictions` with predicted leads per combination
- **Joining Rate Cron (Every 30 min):** Collects actual joining rates into `combination_joining_rates`
