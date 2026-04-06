---
title: Coretech API Specification
category: technical-architecture
subcategory: api-specifications
source_id: 9c6ea921
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Coretech API Specification

## Overview
This document covers the general API architecture, authentication conventions, request/response design standards, and the comprehensive catalog of endpoints across all Coretech microservices. The system is a unified microservices architecture serving BrightChamps' educational platform.

## API Contract

### Base URLs
| Environment | URL |
|-------------|-----|
| Production | `https://api-services.brightchamps.com/` |
| Staging | `https://api-services-stage.brightchamps.com/` |

### Authentication Methods
| Method | Header | Notes |
|--------|--------|-------|
| JWT Bearer Token | `Authorization: Bearer <jwt_token>` | Handled by `authMiddleware` or `authOrApiKeyMiddleware` |
| API Key | `x-api-key: <API-KEY>` | For system-to-system calls |
| Cookies | `Cookie: i18next=en-GB` + session cookie | Some frontend-facing endpoints |
| None | — | Specific public endpoints (booking fetchers, public student details) |

### Standard Response Wrapper
All success and error responses use the `ApiResponse` format:
```json
{
  "success": true,
  "data": {},
  "message": "string",
  "status": 200,
  "errors": []
}
```

### Error Response Format
```json
{
  "success": false,
  "errors": [{ "type": "field", "msg": "string", "path": "string", "location": "body" }],
  "status": 400
}
```

### Standard HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Validation error or business rule violation |
| 401 | Missing, expired, or invalid JWT/API key |
| 404 | Resource not found |
| 424 | Dependency error (external/internal service failure) |
| 500 | Database, transaction, or server error |

### Pagination & Filtering
List endpoints use: `limit`, `offset`, `pageCounter`
Dynamic filters support: `between`, `in`, `like`, and nested table `includes` via JSON filter objects

### Content-Type
- Default: `application/json`
- File uploads: `multipart/form-data`

## Logic Flow

### Controller Layer
Each microservice has its own router and controller layer. All routes pass through authentication middleware before reaching controllers.

### Service/Facade Layer
Controllers call service/facade methods. Services orchestrate DB operations, inter-service calls, and external integrations.

### High-Level Design (HLD)

**Microservices:**
| Service Name | Code Name | Responsibility |
|-------------|-----------|----------------|
| Class Service | Paathshala | Class scheduling, curriculum, group management |
| Meetings Service | Doordarshan | Zoom license and meeting link management |
| Teacher Service | Dronacharya | Teacher profiles, payout, LTA |
| CRM Service | Prabandhan | Zoho CRM integration, sales automation |
| Student Service | Eklavya | Student profiles, balances, payments |
| Demo Booking Service | Tryouts | Demo booking, availability, communications |
| Auth Service | Chowkidar | User identity, JWT, role management |
| Communications Service | Hermes | Email, WhatsApp, SMS dispatch |
| Payments Service | Payments | Payment initiation, webhooks, aggregators |

## External Integrations
- **Zoho CRM:** Lead, deal, and task management
- **AWS (S3, SQS, SNS, Lambda, Bedrock):** Object storage, async messaging, serverless compute, AI
- **Zoom:** Meeting creation and real-time event tracking
- **Payment Aggregators:** Stripe, Razorpay, PayPal, Xendit, Tabby, Tazapay, Splitit, Manual
- **Hermes:** Email and WhatsApp dispatch
- **Redis:** Caching across multiple services
- **MySQL (AWS RDS):** Primary relational database for all services

## Internal Service Dependencies

### Student Management (Eklavya)
- `GET /v1/student` — Multi-mode student/parent lookup by `studentId`, `referralCode`, or `objectId`
- `POST /v1/student` — Bulk student lookup by `referralCodes` array
- `PUT /v1/student/all-details` — Update student and parent details (name change triggers SQS for certificate regeneration)
- `GET /v1/student/details` — Rich student data with optional achievements
- `POST /v1/student/details/balanceIds` — Bulk fetch by `studentBalanceIds`
- `POST /v1/student/details/bulk` — Bulk fetch by `studentIds` with country/language filters
- `GET /v1/student/filter` — Search students by name, email, or phone
- `GET /v1/student/get-students` — Parent Dashboard: all students for authenticated parent; `demoData=true` for booking stats; `isMagicLink=true` for auth link
- `POST /v1/student/parents/create-or-update` — Create/update parent+student; UTM tracking; language preference prediction; Chowkidar identity management

### Class & Balance Management (Eklavya)
- `GET /v1/student-class-balance` — Class balance details by `studentId`, `courseId`, or balance `id`
- `POST /v1/student/bulk-student-class-balances` — Bulk balance retrieval by `studentIds`
- `GET /v1/student/get-course-teacher-details` — Student-course-teacher relationships with churn analytics; type: `ACTIVE`, `PAST`, `INACTIVE`

### Payments & Packages (Eklavya)
- `POST /v1/payment-initiation/create-payment` — Create payment initiation record
- `POST /v1/payment-initiation/payment-link` — Generate payment URL via aggregator
- `GET /v1/payment/transactions` — Comprehensive financial history; groups by `paymentInitiationId`
- `POST /v1/package-payment` — Payment metadata via Base64 `payment_initiation_id` decode
- `GET /v2/recommended-package` — Recommendation engine for next installment; uses NectedService for localized pricing
- `POST /v1/cancel-sold-package` — Cancel package; deactivate, cancel installments, expire external links
- `POST /v1/student/bulk-installments` — Installment status by `studentClassBalanceIds`; auto-upgrade logic

### Feed, Gamification & Content (Eklavya)
- `POST /v1/feed/presigned-url` — S3 presigned URL for video upload; 60-second Redis rate limit
- `POST /v1/feed/showcase-title-and-desc` — Audio upload → Whisper transcription → LLM caption/hook generation
- `GET /v1/badges/progress-summary` — Gamification tiers, peer ranking, default ranks for unearned badges
- `GET /v1/badges/badge-banner-notification` — Redis-only fast badge notification check

### Referrals & Credit Transfers (Eklavya)
- `GET /v1/referral/details` — Referral history; teacher view queries 15-day student referrals
- `POST /v1/referral/claim` — Claim gems for referrals (1 gem: demo, 5 gems: conversion)
- `POST /v1/student-credit-transfer/request` — Transfer class credits, gems, diamonds; validates balances and RPC

### Unified Data (Eklavya — Internal)
- `POST /v1/unified-data/students` — Raw Sequelize JSON filter → dynamic SQL query
- `POST /v1/unified-data/sale-payments` — Raw Sequelize JSON filter → dynamic SQL query

### Auth & System (Chowkidar)
- `GET /v1/user` — Stateless JWT decode; returns role and permissions without DB call
- `GET /v1/system-spec` — Technical capability analysis (CPU, RAM, GPU FPS, network speed)

### Bookings & Demos (Tryouts)
- `POST /classes` — Advanced filtered booking class retrieval
- `GET /demo-availability` — Slot availability with timezone resolution and capping

## Database Operations

### Tables Accessed
Distributed across service-specific MySQL databases (AWS RDS):
- `eklavya.*` — student, parent, balance, payment, referral, feed tables
- `paathshala.*` — class, curriculum, group tables
- `tryouts.*` — booking, availability, prediction tables
- `dronacharya.*` — teacher, payout, LTA tables

### SQL / ORM Queries
- Sequelize ORM used across Node.js services
- Dynamic Sequelize JSON filter objects on unified data endpoints
- Composite DB indexes recommended for high-cardinality list queries

### Transactions
- Package cancellation, payment webhook, and user creation flows use explicit DB transactions

## Performance Analysis

### Good Practices
- Stateless JWT decode at `/v1/user` avoids DB round-trip for auth checks
- Redis caching used across availability, badge, rate-limit, and feed endpoints
- `Promise.all` parallel processing in facade layers for independent service calls

### Performance Concerns
- Dynamic SQL via unified data endpoints (`POST /v1/unified-data/*`) poses performance risk for deeply nested `include` structures
- Some list endpoints lack pagination documentation

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | `POST /v1/unified-data/students` and `/sale-payments` allow raw Sequelize filters — severe data exposure risk if not strictly protected by internal auth roles |
| Medium | Multiple endpoints documented as "no authentication required" — needs audit for PII exposure |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Audit all "no auth" endpoints for PII exposure risk
- Add rate limiting to unified data endpoints

### Month 1 (Architectural)
- Replace unified data raw-filter endpoints with typed query endpoints per use case
- Implement circuit breaker pattern for inter-service calls to handle downstream failures gracefully

## Test Scenarios

### Functional Tests
- JWT auth flow: valid token → 200, expired token → 401, missing token → 401
- API key auth: valid key → 200, invalid key → 401
- Pagination: verify `limit` and `offset` work correctly on list endpoints
- Standard error format: validate 400/404/500 responses match `ApiResponse` schema

### Performance & Security Tests
- Verify unified data endpoints reject non-internal callers
- Load test key student endpoints at 1000 concurrent requests

### Edge Cases
- `isMagicLink=true` on `/v1/student/get-students` (Chowkidar called for auth link generation)
- Student name change trigger SQS certificate regeneration
- Package cancellation rolls back transaction on partial failure

## Async Jobs & Automation
- **SQS Queues:** BOOKING_SQS, invoice-generation, onboard-flow, booking_comms, update-paid-class-status, prabandhan-crm-notifications
- **SNS Topics:** Booking creation/modification events, demo class feedback events, leave approval events
- **Lambda Functions:** mapStudenWithBooking, prabandhan-class-completion-flow, update-paid-class-status, upcomingClassDetails, publish-paid-class-status-update, collectStudentForStudentClassPerformance
