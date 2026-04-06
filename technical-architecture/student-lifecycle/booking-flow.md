---
title: Booking Flow
category: technical-architecture
subcategory: student-lifecycle
source_id: af660f56
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Booking Flow

## Overview
The Booking Flow manages the end-to-end lifecycle of a student's trial class booking, from initial partial data capture through final payment processing and onboarding. It spans the Tryouts (demo booking), Eklavya (student), Paathshala (class), and Payments services, using SQS for asynchronous student/parent mapping and MongoDB for partial tracking.

## API Contract

### POST /eklavya/v1/student/details
- **Auth:** None (public)
- **Purpose:** Fetch student and parent details mapped to a booking; triggers Lambda to create them from partial MongoDB data if absent
- **Request Body:** `{ "objectId": "6423e172d3dbd1f47d4156a9" }`
- **Response:**
```json
{
  "booking": { "id": int, "datetime": "ISO8601", "duration": int, "bookingType": "string", "joinStatus": "string" },
  "student": { "id": int, "grade": int, "parentId": int, "name": "string" },
  "parent": { "phone": "string", "email": "string" },
  "courseDetail": {},
  "timeZoneDetail": {}
}
```

### POST /classes
- **Auth:** None required
- **Purpose:** Retrieve filtered booking class information with advanced querying
- **Request Body:**
  | Field | Required | Type |
  |-------|----------|------|
  | startTime | Conditional | ISO8601 string |
  | filter | Conditional | object |
  | studentId | Conditional | integer |
  | endTime | No | ISO8601 string |
  | courseIds | No | comma-separated string |
  | limit | No | integer |
  | offset | No | integer |
  | bookingType | No | string |
  | feedback | No | boolean (default: true) |
- **Response (200 OK):**
```json
{
  "success": true, "status": 200, "message": "classes successfully fetched",
  "data": {
    "classes": [{
      "id": 12345, "datetime": "2024-01-15T10:30:00.000Z", "duration": 60,
      "bookingType": "firstBooking", "joinStatus": "created", "status": "active",
      "student": { "id": 567, "name": "John Doe", "grade": 5 }
    }],
    "totalCount": 150
  }
}
```

### GET /tryouts/v1/booking/classes
- **Query Params:** `startTime` (required), `endTime` (required)
- **Purpose:** List all bookings in a time range

### PUT/PATCH /tryouts/v1/booking/:updateType
- `:updateType` values: `Cancel`, `Reschedule`, `Unqualify`

### POST /v1/payment-initiation/create-payment
- **Purpose:** Creates a `payment_initiations` entry to begin the payment flow
- **Response:** `paymentInitiationId`

### POST /v1/payment-initiation/payment-link
- **Purpose:** Generates payment gateway link using `paymentInitiationId`
- **Supported Aggregators:** Stripe, Razorpay, PayPal, Xendit, Tabby, Tazapay, Splitit, Manual

## Logic Flow

### Controller Layer
- Booking creation → `BookingController.createBooking()`
- Booking state changes → `BookingController.updateBooking(:updateType)`
- AI booking fallback → `createBookingConsumer` (SQS consumer)

### Service/Facade Layer
**Booking Creation Flow:**
1. User marks availability → partial data stored in MongoDB via tracker API
2. User clicks "create booking" → finalized booking record created in `tryouts.bookings`
3. `objectId` pushed to `BOOKING_SQS` queue and CRM
4. Lambda `mapStudenWithBooking` (Eklavya service) consumes SQS message:
   - Checks if parent phone exists → update parent if yes, create if no
   - Checks student grade and ID → update or create student
5. AI Calling Fallback (if user drops off):
   - Partial details captured → pushed to `booking_requests` table
   - `createBookingConsumer` processes the request

**Payment Flow:**
1. `POST /v1/payment-initiation/create-payment` → create `payment_initiations` record
2. `POST /v1/payment-initiation/payment-link` → call payment aggregator → return URL to client
3. Client redirected to payment page
4. On successful payment: aggregator fires webhook to `/payment-callback` in Eklavya
5. Webhook updates `sale_payments` to `paid`; updates `student_profile.total_credits`; updates `student_class_balance.total_booked_class`
6. Post-payment SQS triggers:
   - `invoice-generation` queue: PDF generation via Puppeteer → upload to S3 → send via Hermes email
   - `onboard-flow` queue: welcome emails, curriculum module assignment, CRM deal → "Closed Won"

### High-Level Design (HLD)
**Booking State Machine:**
| State | status | joinStatus | bookingType |
|-------|--------|------------|-------------|
| Active/Created | active | null or created | firstBooking |
| Rescheduled | active | created | rescheduled |
| Cancelled | inactive | cancelled | — |
| Unqualified | inactive | unqualified | — |
| AI Request Pending | — | — | status: pending |
| AI Request Done | — | — | status: completed/failed |

## External Integrations
- **MongoDB:** Partial booking tracker data storage
- **Zoho CRM:** Booking objectId pushed on creation
- **Payment Aggregators:** Stripe, Razorpay, PayPal, Xendit, Tabby, Tazapay, Splitit, Manual
- **Puppeteer (Lambda):** Invoice PDF generation
- **AWS S3:** Invoice storage
- **Hermes:** Invoice email dispatch, welcome email on onboarding
- **AWS SQS:** BOOKING_SQS, invoice-generation, onboard-flow queues

## Internal Service Dependencies
- Tryouts (Demo Booking): `tryouts.bookings`, `tryouts.booking_requests`
- Eklavya (Student): `eklavya.students`, `eklavya.parents`, `eklavya.student_class_balances`, `eklavya.student_profiles`, `eklavya.sale_payments`
- Paathshala (Class): `paathshala.demo_classes` maps bookings to teachers
- Chowkidar (Auth): Identity management for newly created users
- Platform Service: Timezone and course resolution

## Database Operations

### Tables Accessed

**`tryouts.bookings` (primary booking table):**
- `id, objectId, datetime, duration, courseId, studentId, status, joinStatus, bookingType, tzId, phone, grade`

**`tryouts.booking_requests` (AI fallback):**
| Column | Type |
|--------|------|
| id | INT |
| identifier_type | STRING |
| identifier_value | INT |
| source | STRING |
| data | JSON |
| booking_id | INT |
| status | STRING (pending, completed, failed) |

**`eklavya.students`, `eklavya.parents`, `eklavya.student_class_balances`**

**`paathshala.demo_classes`:** Maps `booking_id` → `teacher_confirmation_id`

**`eklavya.sale_payments`:** Payment transaction records

**`eklavya.student_profiles`:** Tracks `total_credits`

### SQL / ORM Queries
- INSERT into `tryouts.bookings` on booking creation
- SELECT by `objectId` in MongoDB and SQL for partial data mapping
- UPDATE `eklavya.student_profiles.total_credits` on payment success
- UPDATE `eklavya.student_class_balances.total_booked_class` on payment success
- UPDATE `eklavya.sale_payments.status = 'paid'` on webhook

### Transactions
- Payment webhook processing uses a DB transaction: `sale_payments` update + `student_profiles` update + `student_class_balance` update are atomic

## Performance Analysis

### Good Practices
- Partial tracking via MongoDB reduces write pressure on relational DB during high-traffic booking form abandonment
- Asynchronous SQS consumer for student/parent mapping decouples booking creation from user lookup latency
- Post-payment flows (invoice, onboarding) are non-blocking via SQS

### Performance Concerns
- Lambda `mapStudenWithBooking` performs sequential checks (parent → student) — could benefit from parallel resolution
- Payment webhook must be idempotent to handle duplicate delivery from aggregators

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | AI booking fallback via `booking_requests` table — no documented cleanup/expiry for stale `pending` records |
| Low | MongoDB for partial tracking creates a dual-store pattern that adds operational complexity |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add TTL index on MongoDB tracker documents to auto-expire after 24 hours
- Add idempotency key check in payment webhook handler

### Month 1 (Architectural)
- Consolidate partial booking tracking to a single store (SQL or MongoDB, not both)
- Implement payment webhook retry + DLQ with alerting for failed fulfillment

## Test Scenarios

### Functional Tests
- Complete booking creation flow end-to-end: tracker → booking → student mapping
- Cancel booking: verify `status = inactive`, `joinStatus = cancelled`, cancellation comms triggered
- Reschedule booking: verify `bookingType = rescheduled`, `joinStatus = created`
- Unqualify booking: verify `status = inactive`, `joinStatus = unqualified`
- Payment success webhook: verify `sale_payments`, `student_profiles`, `student_class_balances` all updated

### Performance & Security Tests
- Payment webhook idempotency: send same webhook twice, verify no double credit
- Verify payment aggregator callback URL is authenticated (webhook secret)

### Edge Cases
- User drops off mid-booking form (AI fallback triggered)
- Payment webhook received before `mapStudenWithBooking` Lambda completes (student not yet in DB)
- Booking rescheduled after cancellation comms already sent

## Async Jobs & Automation
- **BOOKING_SQS Consumer (`mapStudenWithBooking` Lambda):** Maps booking to student/parent records in Eklavya
- **`createBookingConsumer`:** Processes AI-assisted booking requests from `booking_requests` table
- **`invoice-generation` SQS Queue:** Triggers Puppeteer Lambda → S3 upload → Hermes email on payment success
- **`onboard-flow` SQS Queue:** Sends welcome emails, assigns curriculum, updates CRM to "Closed Won" on payment success
