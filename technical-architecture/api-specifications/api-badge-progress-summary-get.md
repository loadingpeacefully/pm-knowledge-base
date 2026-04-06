---
endpoint: GET /v1/badges/progress-summary
service: eklavya
source_id: 7f7e27d9-2546-44ee-a24e-b0c169a67484
original_source_name: progress-summary
controller: controllers/badges.js:9
service_file: facades/badges.js:40
router_file: routers/badges.js:17-22
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/badges/progress-summary

## Summary

Fetches comprehensive badge progress summary for a student, including progress percentage, tier priority, metric values, and rankings for all active badges. Supports an optional `referenceMonth` to query historical badge data. Non-participated badges get a default rank of `total_participants + 1`. Uses Redis caching for badge definitions.

**Category:** Internal API — Gamification
**Owner/Team:** Student Engagement / Gamification Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/badges/progress-summary`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Query Parameters

**Validation source:** `validators/badges.js:3-14`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | integer (min: 1) | Yes | Student ID; auto-converted to integer |
| `referenceMonth` | string (ISO8601 date, YYYY-MM-DD) | No | Month to query; defaults to current month start |

### Request Examples

```
GET /v1/badges/progress-summary?studentId=123
GET /v1/badges/progress-summary?studentId=123&referenceMonth=2024-01-01
GET /v1/badges/progress-summary?studentId=456&referenceMonth=2024-10-01
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    { "badgeId": 2, "badgeName": "Attendance Champion",
      "badgeIcon": "https://example.com/badge-icon.gif",
      "description": "Perfect attendance badge for consistent learning",
      "isLocked": false,
      "progressDetails": { "icon": "attendance-icon.png", "theme": "#FF6B35",
                           "progress": 75, "tierPriority": 3, "metricValue": 15 },
      "rankDetails": { "icon": "", "rank": 42 } },
    { "badgeId": 3, "badgeName": "Homework Hero",
      "badgeIcon": "https://example.com/homework-badge.png",
      "description": "Excellence in homework completion",
      "isLocked": true,
      "progressDetails": { "icon": "homework-icon.png", "theme": "#4ECDC4",
                           "progress": 30, "tierPriority": 1, "metricValue": 6 },
      "rankDetails": { "icon": "", "rank": null } }
  ],
  "message": "Badge progress summary fetched successfully."
}
```

**No badges (200):**
```json
{ "success": false, "data": [], "message": "Badge progress summary fetched successfully." }
```

**Validation error (400):**
```json
{ "success": false, "data": null, "message": "studentId is required", "error": "ValidationError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request — invalid parameters |
| 401 | Unauthorized |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/badges.js:9-22`)

1. Extract `studentId` from validated query params
2. Call `BadgeFacade.getBadgeProgressSummary({ studentId })`
3. Format via `ApiResponse` wrapper

### Facade (`facades/badges.js:40-79`)

1. **Initialize reference month:** `moment.utc().startOf("month").format("YYYY-MM-DD")` (or provided value)
2. **Fetch eligible months:** `fetchEligibleMonthsForBadges({ studentId })` — determines if student is eligible based on enrollment
3. **Get badge definitions:** `badgeService.fetchBadges()` — fetches from Redis cache (`REDIS_KEYS.BADGE_DETAILS`) or DB
4. **Fetch progress + rankings:** `badgeService.fetchStudentBadgeProgressAndRank()` → returns `{ studentProgress, studentBadgeRankMap }`
5. **Handle non-participated badges:** for badges with no participation, compute rank = `total_participants + 1`
6. **Format summary:** `badgeService.formatBadgeSummary()` — combines progress + badge definitions into response array

**Exclusion:** "Bright Star" badge is excluded from this summary (handled separately).

---

## Microservice Dependencies

**None.** Database + Redis only. No external HTTP calls.

**Internal dependencies:**
- `BadgeService` — badge definitions, progress, ranking
- `StudentsService` — student eligibility and enrollment dates (DB)
- Redis — badge definition cache (`REDIS_KEYS.BADGE_DETAILS`)

---

## Database & SQL Analysis

### Key Queries

**Badge definitions:**
```js
Badge.findAll({
  where: { isActive: true },
  include: { model: BadgeTier, required: true, order: ["priority"] }
})
```

**Student badge progress:**
```js
StudentBadgeProgress.findAll({
  where: { studentId, referenceMonth, badgeId: badgeIds, status: { [Op.ne]: 'INACTIVE' } }
})
```

**Student eligibility:**
```js
Student.findAll({
  where: { id: studentId },
  include: [
    { model: Parent, required: true },
    { model: StudentClassBalance, required: true,
      where: { classType: { [Op.notIn]: ['onlineMasterClass','offlineMasterClass','diy'] } } }
  ]
})
```

**Non-participant count:**
```js
StudentBadgeProgress.count({ where: { referenceMonth, badgeId: nonParticipatedBadgeIds } })
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `badges` | Badge definitions and metadata |
| `badge_tiers` | Tier criteria and priority |
| `student_badge_progress` | Per-student per-month progress |
| `students` | Eligibility check |
| `student_class_balances` | Enrollment eligibility |
| `parents` | Part of eligibility join |

### Redis Operations

| Key | Purpose | Source |
|-----|---------|--------|
| `REDIS_KEYS.BADGE_DETAILS` | Cached badge definitions | Written by badge admin operations |
| Badge ranking data | Ranking cache | Written by badge progress calculation jobs |

### Recommended Indexes

```sql
CREATE INDEX idx_student_badge_progress_student_ref ON student_badge_progress(student_id, reference_month);
CREATE INDEX idx_student_badge_progress_badge_ref ON student_badge_progress(badge_id, reference_month);
CREATE INDEX idx_student_badge_progress_status ON student_badge_progress(status);
CREATE INDEX idx_student_class_balance_student_type ON student_class_balances(student_id, class_type);
CREATE INDEX idx_badges_active ON badges(is_active);
CREATE INDEX idx_badge_tiers_badge_priority ON badge_tiers(badge_id, priority);
```

---

## Technical Issues

### High Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Student eligibility join is complex — multiple table join on every request | `facades/badges.js:83-108` | Slow for students with long class histories |
| 2 | Badge ranking calculations scale poorly with large student populations | `facades/badges.js:49-69` | Performance degrades as user base grows |
| 3 | Heavy Redis dependency for badge definitions — no graceful DB fallback path documented | `services/badges.js:32-47` | Service degradation on Redis failure |

### Medium Priority

| # | Issue | Location |
|---|-------|----------|
| 4 | Complex date logic for eligible months — potential for timezone bugs | `facades/badges.js:147-204` |
| 5 | No validation on badge progress data integrity | Throughout facade |

---

## Test Scenarios

### Functional
- Active student with multiple badges in progress
- Student with no badges → empty array
- Historical reference month query
- Non-existent student
- Badge ranking for first vs. last participant
- Badge eligibility boundary (first month of enrollment)

### Performance
- Response time with many badges
- Concurrent badge progress requests
- Cache hit vs miss performance comparison
- Ranking calculation with 10k+ participants

### Security
- Auth enforcement
- Student ID validation (non-integer, negative)
- Reference month format validation

### Edge Cases
- Student with no class enrollments
- Badge progress during month transitions
- Future reference month
- Badges with no participants at all (rank = 1 for first participant)
- Bright Star badge excluded from results
