---
title: Booking Classes API - POST
category: technical-architecture
subcategory: api-specifications
source_id: 9cfbd23e
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Booking Classes API - POST

## Overview
The `POST /classes` endpoint retrieves filtered booking class information with advanced querying, pagination, and multi-service data enrichment. It supports filtering by time range, student, course, country, and booking type, and enriches results with referral data, communication metrics, and AI booking predictions.

## API Contract

### POST /classes
- **Auth:** None required
- **Content-Type:** `application/json`

**Request Body:**
| Field | Required | Type | Notes |
|-------|----------|------|-------|
| startTime | Conditional | ISO8601 string | At least one of startTime, filter, or studentId required |
| filter | Conditional | object | Custom filter object |
| studentId | Conditional | integer | |
| endTime | No | ISO8601 string | |
| courseIds | No | string | Comma-separated |
| languageIds | No | string | Comma-separated |
| countryIds | No | string | Comma-separated |
| countryGroupIds | No | string | Comma-separated |
| bookingUuIds | No | array | |
| bookingType | No | string | |
| hubId | No | string | |
| utmSource | No | string | |
| feedback | No | boolean | Default: true |
| limit | No | integer | Pagination |
| offset | No | integer | Pagination |

**Response (200 OK):**
```json
{
  "success": true,
  "status": 200,
  "message": "classes successfully fetched",
  "data": {
    "totalCount": 150,
    "classes": [{
      "id": 12345,
      "datetime": "2024-01-15T10:30:00.000Z",
      "duration": 60,
      "courseId": int,
      "studentId": int,
      "bookingType": "firstBooking",
      "joinStatus": "created",
      "status": "active",
      "tzId": int,
      "phone": "string",
      "grade": int,
      "objectId": "string",
      "student": { "id": int, "name": "string", "grade": int, "languageMappings": [] },
      "referralDetails": {},
      "communicationStatus": { "whatsapp": int, "email": int, "sms": int },
      "prediction": { "teacher_predicted_leads": int }
    }]
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "status": 400,
  "message": "invalid filter",
  "errors": [{ "type": "field", "msg": "Wrong dateTime format", "path": "startTime", "location": "body" }]
}
```

## Logic Flow

### Controller Layer
Request → `bookingValidator.allClassesValidatorV2` → `useValidation` middleware → `bookingController.allClassesByTimeV3` → `bookingFacade.allClassesByTimeV2`

### Service/Facade Layer
**8-Step Business Logic Flow:**
1. **Validation:** Ensure required filters present; validate ISO8601 format; prevent SQL injection/XSS
2. **Country Group Processing:** Merge `countryGroupIds` with individual `countryIds`
3. **Student Filtering:** Apply language and country filters to student records
4. **Data Retrieval:** Fetch paginated bookings from Database Service
5. **Referral Processing:** Enrich each booking with referral information
6. **Communication Status:** Aggregate WhatsApp, email, SMS communication counts from Communication Logs Service
7. **Prediction Enhancement:** Add AI booking prediction data (`teacher_predicted_leads`) from Booking Prediction Service
8. **Data Formatting:** Structure final response with all associations

### High-Level Design (HLD)
- Lives in Tryouts (Demo Booking) service
- Multi-service enrichment via parallel `Promise.all` calls where possible
- Cursor-based pagination recommended for large datasets
- Circuit breaker pattern advised for external service calls

## External Integrations
N/A — All enrichment data comes from internal services.

## Internal Service Dependencies
- Student Service (Eklavya): Student details and language mappings
- Group Mapping Service: Country group ID expansion
- Communication Logs Service: Per-booking communication counts
- Booking Prediction Service: `teacher_predicted_leads` from Auxo predictions
- Database Service: Core booking records

## Database Operations

### Tables Accessed
- `tryouts.bookings`: Core booking records (id, datetime, duration, courseId, studentId, status, joinStatus, bookingType, tzId, phone, grade, objectId)

### SQL / ORM Queries
- SELECT bookings WHERE time range AND status AND other filters
- Pagination via LIMIT/OFFSET
- JOIN with student language mappings
- Aggregate communication counts per booking from communication logs

### Transactions
N/A — Read-only endpoint.

## Performance Analysis

### Good Practices
- Validator middleware catches bad input before hitting DB
- `Promise.all` for independent enrichment calls reduces wall-clock time
- Input validation prevents SQL injection and XSS

### Performance Concerns
- Multi-service enrichment (5+ services) increases response latency for large result sets
- No auth requirement means this endpoint could be crawled for bulk student data

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No authentication required — this endpoint exposes student data (phone, grade, booking details) without any auth |
| Medium | Cursor-based pagination and circuit breakers are documented as "recommended" but not confirmed as implemented |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add rate limiting and/or optional auth to prevent bulk data scraping
- Add composite index on `tryouts.bookings(startTime, status)` for time-range queries

### Month 1 (Architectural)
- Implement cursor-based pagination for large dataset queries
- Add circuit breaker for enrichment service calls with graceful degradation (return booking without enrichment on failure)

## Test Scenarios

### Functional Tests
- Request with only `startTime` → returns bookings in range
- Request with `studentId` → returns bookings for that student
- Request with `countryGroupIds` → correctly expands to individual countries
- Invalid `startTime` format → 400 with field-specific error message
- Missing all three required fields → 400 error

### Performance & Security Tests
- Load test with large time range (30 days) and verify pagination works correctly
- Verify no authentication bypass for this endpoint (rate limit check)

### Edge Cases
- `feedback = false` → verify feedback data excluded from response
- `bookingUuIds` with 1000 IDs → verify bulk lookup performance
- `limit = 0` → should return error or empty array

## Async Jobs & Automation
N/A — Synchronous read endpoint; no async processing.
