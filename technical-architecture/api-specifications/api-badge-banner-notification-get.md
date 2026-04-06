---
endpoint: GET /v1/badges/badge-banner-notification
service: eklavya
source_id: 985eafbd-42e5-4b81-a1d7-9a9386018314
original_source_name: badge-banner-notification
controller: controllers/badges.js:130
service_file: services/badges.js:1037
router_file: routers/badges.js:53-58
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/badges/badge-banner-notification

## Summary

Retrieves badge banner notification status for a parent from Redis cache. Pure Redis read — no database queries, no external service calls. Returns whether a notification exists (`isNotified`), when it was set, and which student triggered it. TTL on the Redis key is 30 days (set by the corresponding POST operation).

**Category:** Internal API — Notification Retrieval
**Owner/Team:** Student Engagement / Gamification Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/badges/badge-banner-notification`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Query Parameters

**Validation source:** `validators/badges.js:100-107`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parentId` | integer (min: 1) | Yes | Parent ID to check notification status for; auto-converted to integer |

### Request Examples

```
GET /v1/badges/badge-banner-notification?parentId=123
GET /v1/badges/badge-banner-notification?parentId=789
```

### Response Format

**Notification exists (200):**
```json
{
  "success": true,
  "data": { "isNotified": true, "timestamp": "2024-10-26 14:30:25", "studentId": 456 },
  "message": "Badge notifications fetched successfully."
}
```

**No notification (200):**
```json
{
  "success": false,
  "data": { "isNotified": false, "timestamp": null, "studentId": null },
  "message": "Badge notifications fetched successfully."
}
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "parentId is required", "error": "ValidationError" }
```

**Redis down (500):**
```json
{ "success": false, "data": null, "message": "Redis connection not established", "error": "InternalError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (with or without notification data) |
| 400 | Bad request — invalid or missing `parentId` |
| 401 | Unauthorized |
| 500 | Redis connection or service error |

---

## Logic Flow

### Controller (`controllers/badges.js:130-143`)

1. Extract `parentId` from validated query params
2. Call `BadgeFacade.getBadgeBannerNotification({ parentId })`
3. Format via `ApiResponse` wrapper
4. Return JSON

### Facade (`facades/badges.js:779-791`)

Pass-through with error wrapping: converts service errors to `InternalError` with context, then calls `BadgeService.getBadgeBannerNotification()`

### Service (`services/badges.js:1037-1053`)

1. Check `this.redis?.isReady` — throw `InternalError("Redis connection not established")` if false
2. `await this.redis.get(REDIS_KEYS.STUDENT_BADGE_NOTIFICATIONS(parentId))`
   - Key pattern: `eklavya:badges:notifications:parent:{parentId}`
3. If `null`: return `{ isNotified: false, timestamp: null, studentId: null }`
4. Else: `return JSON.parse(value)` → `{ isNotified: true, timestamp: "YYYY-MM-DD HH:mm:ss", studentId: <int> }`

---

## Microservice Dependencies

**None.** Redis-only. No database queries, no HTTP calls.

**Infrastructure dependency:**
- Redis (required) — TTL on keys: 30 days (2,592,000 seconds), set by the corresponding POST/write operation

---

## Redis Analysis

### Key Structure

```
eklavya:badges:notifications:parent:{parentId}
```

| Property | Value |
|----------|-------|
| Value type | JSON string |
| TTL | 30 days (set on write) |
| Namespace | `eklavya:badges:notifications:` |

### Redis Command

```
GET "eklavya:badges:notifications:parent:123"
```

### Expected Stored JSON Schema

```json
{ "isNotified": true, "timestamp": "2024-10-26 14:30:25", "studentId": 456 }
```

### Performance Characteristics

- Redis GET: O(1)
- Typical response time: < 1ms (local Redis), 1–5ms (remote)
- Memory per key: ~150 bytes
- JSON parse time: < 0.1ms for this payload

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Complete dependency on Redis — no fallback if Redis is down; service returns 500 | `services/badges.js:1039` | Full feature outage on Redis failure |
| 2 | `JSON.parse(value)` without schema validation — corrupted cache data causes crash | `services/badges.js:1045` | Application crash on malformed cache |

### Medium Priority

| # | Issue | Impact |
|---|-------|--------|
| 3 | No retry logic on Redis transient errors | Unnecessary 500s on brief Redis timeouts |
| 4 | `success: false` returned when no notification exists (but operation succeeded) | Confusing semantics for callers |

### Low Priority

| # | Issue |
|---|-------|
| 5 | No application-level caching — every request hits Redis for popular parent IDs |
| 6 | JSON string stored vs Redis Hash — slightly less efficient for this structure |

---

## Test Scenarios

### Functional
- Parent with existing notification → `isNotified: true`
- Parent with no notification → `isNotified: false` with null fields
- Notification immediately after write operation
- Different `parentId` values

### Validation
- Missing `parentId`
- Non-integer `parentId`
- Negative or zero `parentId`
- Very large `parentId`

### Infrastructure (Redis)
- Redis connection failure → 500 with informative message
- Redis timeout
- Redis key expiration mid-flight
- Corrupted JSON in Redis key
- Redis cluster failover

### Security
- JWT auth enforcement
- API key enforcement
- Parent ID enumeration attempts

### Edge Cases
- JSON with missing fields (`isNotified` present but `timestamp` null)
- Unicode characters in cached data
- Near-TTL keys (expiring during request)
