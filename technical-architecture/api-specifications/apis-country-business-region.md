---
title: APIs for Country and Business Region
category: technical-architecture
subcategory: api-specifications
source_id: 6c0b6ba7
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# APIs for Country and Business Region

## Overview
The Country and Business Region APIs, managed by the Platform service, allow administrators to create business regions and map countries to regions. These mappings are foundational to multi-region operations across Coretech services, controlling pricing, availability, and routing logic based on student/teacher geography.

## API Contract

### PATCH /platform/v1/mappings/country/:id
- **Auth:** `x-api-key` header required
- **Content-Type:** `application/json`
- **Purpose:** Update the business region mapping for a specific country
- **Path Param:** `:id` — country ID
- **Request Body:**
```json
{ "brId": 1 }
```
- **Response (200 OK):**
```json
{
  "success": 200,
  "data": 1,
  "message": "country updated successfully.",
  "status": 200,
  "errors": []
}
```

### POST /platform/v1/mappings/business-region
- **Auth:** `x-api-key` header required
- **Content-Type:** `application/json`
- **Purpose:** Create a new business region
- **Request Body:**
```json
{ "name": "Mars" }
```
- **Response (200 OK):**
```json
{
  "success": 200,
  "data": { "id": 5, "name": "Mars" },
  "message": "businessRegion created successfully.",
  "status": 200,
  "errors": []
}
```

## Logic Flow

### Controller Layer
`PATCH /platform/v1/mappings/country/:id` → PlatformController.updateCountry()
`POST /platform/v1/mappings/business-region` → PlatformController.createBusinessRegion()

### Service/Facade Layer
- Country update: validate `brId` exists in `business_regions` → UPDATE `countries.br_id`
- Business region creation: INSERT into `business_regions` with `name` → return new `id`

### High-Level Design (HLD)
- Platform service owns all master configuration: countries, business regions, timezones, currencies
- MySQL on AWS RDS
- API key authentication for admin-only access
- Other services (Eklavya, Tryouts, etc.) call Platform service to resolve country/timezone/course metadata during student enrollment, demo slot generation, and booking flows
- Intra-cluster calls to Platform service are cached to minimize network overhead

## External Integrations
N/A — Platform service is a source-of-truth master data service; it does not call external APIs.

## Internal Service Dependencies
- Eklavya (Student Service): Calls Platform to resolve country by IP or dial code during student creation
- Tryouts (Demo Booking): Calls `/v1/mappings/timezones` and `/v1/mappings/courses` for slot generation
- Payout system (Dronacharya): Uses `business_regions` to determine payout amounts via `teacher_prices.payout_business_region_id`

## Database Operations

### Tables Accessed

**`countries`:**
| Column | Notes |
|--------|-------|
| id | PK |
| name | Country name |
| code | e.g., VNM |
| short_code | e.g., VN |
| dial_code | e.g., +84 |
| currency_id | FK |
| flag | Image URL |
| br_id | FK → business_regions (the key field updated by PATCH endpoint) |

**`business_regions`:**
| Column | Notes |
|--------|-------|
| id | PK |
| name | Region name |
| created_at | |
| updated_at | |

### SQL / ORM Queries
- `UPDATE countries SET br_id = :brId WHERE id = :countryId`
- `INSERT INTO business_regions (name) VALUES (:name)`

### Transactions
N/A — Single-table writes; no multi-table transactions needed.

## Performance Analysis

### Good Practices
- API key authentication prevents unauthorized mapping changes
- Simple two-table schema: easy to query and maintain
- Intra-cluster caching by consuming services reduces Platform load for read-heavy operations

### Performance Concerns
- No documented read endpoints for retrieving all countries or business regions — unclear if these are paginated
- Country-to-region updates affect all downstream services that cache country data; no documented cache invalidation strategy

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No documented cache invalidation when `countries.br_id` is updated — downstream services may serve stale region data |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add a `GET /platform/v1/mappings/countries` list endpoint for admin visibility
- Document cache invalidation strategy for country/business region changes

### Month 1 (Architectural)
- Implement event-driven cache invalidation (SNS publish on country/region update) for all consuming services
- Add version/timestamp to country and business region records for optimistic locking

## Test Scenarios

### Functional Tests
- PATCH country with valid `brId` → verify `countries.br_id` updated
- PATCH country with non-existent `brId` → should return 400/404
- POST business region with unique name → verify new `id` returned
- POST business region with duplicate name → verify appropriate error response

### Performance & Security Tests
- Verify `x-api-key` required on both endpoints; request without key → 401
- Test with 100 concurrent country updates

### Edge Cases
- PATCH country to a `brId` that doesn't exist in `business_regions`
- POST business region with empty `name` string

## Async Jobs & Automation
N/A — Synchronous CRUD operations only. No background jobs documented.
