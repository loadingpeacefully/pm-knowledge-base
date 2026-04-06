---
endpoint: POST /v1/referral/claim
service: eklavya
source_id: 94f3c928-PENDING-FULL-UUID
original_source_name: claim
controller: controllers/referral.js
service_file: facades/referral.js:124 / services/referral.js:146,179
router_file: routers/referral.js
auth: None
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/referral/claim

## Summary

Awards gems to a student when a referral milestone is reached — either 1 gem for a demo class completed or 5 gems for a demo-to-paid conversion. Fetches referral data from the external Tryouts service, validates the referral hasn't already been claimed, updates the student's gem balance, and records the claim in an audit table. No authentication required. Contains a race condition in gem update (read-then-write without atomicity) and is missing database transaction boundaries across the two write operations.

**Category:** Referral / Reward System API
**Owner/Team:** Referral / Student Incentives Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/referral/claim`
**Authentication:** None

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `referralCode` | string | Yes | Referral code to claim |
| `claimType` | string | Yes | `"demo_completed"` or `"demo_converted"` |
| `studentId` | integer | Yes | Student ID receiving the gem reward |

### Request Examples

```json
// Demo completed — 1 gem
{ "referralCode": "AJ789456", "claimType": "demo_completed", "studentId": 12345 }

// Demo converted — 5 gems
{ "referralCode": "AJ789456", "claimType": "demo_converted", "studentId": 12345 }
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "gemsAwarded": 5,
    "newGemBalance": 25,
    "claimId": 789,
    "claimType": "demo_converted"
  },
  "message": "Referral claimed successfully."
}
```

**Already claimed (400):**
```json
{
  "success": false,
  "data": null,
  "message": "Referral has already been claimed.",
  "error": "ValidationError"
}
```

**Referral not found (400):**
```json
{
  "success": false,
  "data": null,
  "message": "Referral not found.",
  "error": "ValidationError"
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Claim processed, gems awarded |
| 400 | Validation error, already claimed, or referral not found |
| 500 | Database or external service error |

---

## Logic Flow

### Facade (`facades/referral.js:124`)

1. Call `tryoutsService.getReferralByCode(referralCode)` — fetch referral data
2. If referral not found → throw validation error
3. Compute gems to award: `demo_completed` → 1 gem, `demo_converted` → 5 gems
4. Call `ReferralService.checkAndClaimReferral(referralCode, claimType, studentId, gemsToAward)`

### Service — Check Phase (`services/referral.js:146`)

1. Query `gems_claimed` table: check if `referralCode + claimType` already claimed
2. If exists → throw "already claimed" error

### Service — Claim Phase (`services/referral.js:179`)

3. `updateStudentGems(studentId, gemsToAward)`:
   - `SELECT gems FROM students WHERE id = studentId` (read current balance)
   - `UPDATE students SET gems = gems + gemsToAward WHERE id = studentId`
4. `addReferralClaimed(referralCode, claimType, studentId)`:
   - `INSERT INTO gems_claimed (referral_code, claim_type, student_id, gems_awarded, created_at)`

**Gem award amounts:**
- `demo_completed`: 1 gem
- `demo_converted`: 5 gems

---

## Microservice Dependencies

| Service | Call | Trigger |
|---------|------|---------|
| Tryouts | `getReferralByCode(referralCode)` | Always |

**No other external HTTP calls.**

---

## Database & SQL Analysis

### Key Queries

```sql
-- Duplicate claim check
SELECT * FROM gems_claimed
WHERE referral_code = ? AND claim_type = ?;

-- Read current gem balance (part of race condition)
SELECT gems FROM students WHERE id = ?;

-- Update gem balance
UPDATE students SET gems = gems + ? WHERE id = ?;

-- Record claim
INSERT INTO gems_claimed (referral_code, claim_type, student_id, gems_awarded, created_at)
VALUES (?, ?, ?, ?, NOW());
```

### Tables Accessed

| Table | Purpose |
|-------|---------|
| `students` | Gem balance read and update |
| `gems_claimed` | Audit trail — duplicate prevention and claim record |

---

## Technical Issues

### Critical Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Race condition in gem update — `SELECT gems` then `UPDATE gems + ?` is not atomic; concurrent claims can result in lost gem awards | `services/referral.js:179` | Gem balance corruption under concurrent load |
| 2 | No database transaction — `updateStudentGems` and `addReferralClaimed` are separate operations; if `addReferralClaimed` fails after gem update, student receives gems but no audit record exists (or vice versa) | `services/referral.js:179` | Inconsistent state; potential double-spend |

### High Priority

| # | Issue | Impact |
|---|-------|--------|
| 3 | Duplicate check (step 1) and claim insert (step 4) have a TOCTOU race condition — two concurrent requests pass the duplicate check before either inserts | `gems_claimed` table | Double gem award for same referral |
| 4 | No authentication — any caller can claim gems for any studentId | Router level | Unauthorized gem manipulation |
| 5 | Tryouts service failure causes complete endpoint failure — no fallback | Facade | Full feature outage when Tryouts is down |

### Medium Priority

| # | Issue | Impact |
|---|-------|--------|
| 6 | No validation that `studentId` in request matches the referral's intended student in Tryouts data | Facade | Gems awarded to wrong student |
| 7 | `claimType` enum is not validated in input — invalid values pass through to DB | Validator | Unexpected claim types in database |

### Low Priority

| # | Issue |
|---|-------|
| 8 | Gem award amounts (1 and 5) are hardcoded — not configurable |
| 9 | No rate limiting — a single studentId can spam claim attempts |

---

## Test Scenarios

### Functional
- `demo_completed` claim → 1 gem awarded, `gems_claimed` record created
- `demo_converted` claim → 5 gems awarded, `gems_claimed` record created
- Valid referral code with no prior claim → success
- Student gem balance increments correctly

### Business Logic
- Same referralCode + claimType combination claimed twice → second request blocked
- Same referralCode, different claimType (demo_completed then demo_converted) → both succeed independently
- Non-existent referral code → 404/400 from Tryouts response

### Race Condition
- Concurrent identical requests (same referralCode + claimType) — only one should award gems
- Expected failure: both may succeed due to TOCTOU gap

### Validation
- Missing required fields
- Invalid `claimType` value
- Negative or zero `studentId`

### Security
- Claim gems for another student's referral (no auth currently allows this)
- Extremely high gem values via request tampering

### Error Handling
- Tryouts service unavailable → 500 or graceful error
- Database write failure after gem update (transaction gap scenario)
- Gems_claimed insert failure → orphaned gem award
