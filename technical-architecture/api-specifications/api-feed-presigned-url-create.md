---
endpoint: POST /v1/feed/presigned-url
service: eklavya
source_id: 29fb93b5-PENDING-FULL-UUID
original_source_name: presigned-url
controller: controllers/feed.js
service_file: facades/feed.js:528
router_file: routers/feed.js
auth: NONE (auth middleware commented out — CRITICAL SECURITY ISSUE)
security_flag: "⚠️ AUTH_DISABLED"
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/feed/presigned-url

## Summary

Generates an AWS S3 presigned URL for client-side media upload to the feed system. Enforces a 60-second Redis-based rate limit (cooldown) per user to prevent duplicate upload requests. Embeds file metadata (userId, userType, uniqueKey) directly into S3 object metadata at presign time. The auth middleware is currently **commented out**, making this endpoint publicly accessible — any caller can generate upload URLs for any userId/userType combination.

**Category:** Feed / Media Upload API
**Owner/Team:** Feed / Content Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/feed/presigned-url`
**Authentication:** None (auth middleware disabled — see Technical Issues)

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `userId` | integer | Yes | User requesting the upload |
| `userType` | string | Yes | Type of user (e.g., `student`, `teacher`) |
| `uniqueKey` | string | Yes | Client-generated unique key for deduplication |
| `fileExtension` | string | Yes | File extension (e.g., `mp4`, `jpg`) |
| `contentType` | string | Yes | MIME type (e.g., `video/mp4`, `image/jpeg`) |

### Request Examples

```json
{
  "userId": 12345,
  "userType": "student",
  "uniqueKey": "abc123def456",
  "fileExtension": "mp4",
  "contentType": "video/mp4"
}
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": {
    "presignedUrl": "https://s3.amazonaws.com/bucket/temp/abc123def456_student_12345.mp4?X-Amz-...",
    "s3Key": "temp/abc123def456_student_12345.mp4",
    "expiresIn": 3600
  },
  "message": "Presigned URL generated successfully."
}
```

**Rate limited — cooldown active (400):**
```json
{
  "success": false,
  "data": null,
  "message": "Please wait before requesting another upload URL.",
  "error": "ValidationError"
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Presigned URL generated |
| 400 | Rate limited or validation error |
| 500 | S3 or Redis error |

---

## Logic Flow

### Facade (`facades/feed.js:528`)

1. **Rate limit check:** Look up Redis key `feed_dup_{userId}#{userType}`
   - If key exists → reject with cooldown error
   - If key absent → proceed
2. **Set cooldown:** Write Redis key `feed_dup_{userId}#{userType}` with 60-second TTL
3. **Build S3 key:** `temp/${uniqueKey}_${userType}_${userId}.${fileExtension}`
4. **Set validation key:** Write Redis key `feed_val_{userId}#{userType}#{uniqueKey}` (used by downstream feed creation to validate the upload is legitimate)
5. **Generate presigned URL:** Call `core/utils/aws/s3.js:59` — `getSignedPutUrl(s3Key, contentType, metadata)`
   - URL expiry: 1 hour
   - S3 object metadata: `{ userId, userType, uniqueKey }`
6. Return presigned URL and S3 key

---

## Microservice Dependencies

| Service | Call | Trigger |
|---------|------|---------|
| AWS S3 | `getSignedPutUrl` | Always |
| Redis | GET `feed_dup_*` | Always (rate limit check) |
| Redis | SET `feed_dup_*` (TTL 60s) | Always (set cooldown) |
| Redis | SET `feed_val_*` | Always (validation token) |

**No external HTTP service calls.**

---

## Database & SQL Analysis

**None.** This endpoint performs zero database operations. All state is Redis-only.

### Redis Key Schema

| Key Pattern | Purpose | TTL |
|-------------|---------|-----|
| `feed_dup_{userId}#{userType}` | Upload cooldown — prevents re-request within 60s | 60 seconds |
| `feed_val_{userId}#{userType}#{uniqueKey}` | Validation token — proves upload is authorized | Until feed is created or expired |

### S3 Key Pattern

```
temp/{uniqueKey}_{userType}_{userId}.{fileExtension}
```

Example: `temp/abc123def456_student_12345.mp4`

---

## Technical Issues

### Critical Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | Auth middleware is **commented out** — endpoint is fully public with no authentication | Router/middleware layer | Any unauthenticated caller can generate S3 upload URLs for arbitrary userId/userType values; S3 storage abuse |
| 2 | No server-side validation that `userId` matches any real user in the database | Facade | Presigned URLs can be generated for non-existent users |

### High Priority

| # | Issue | Impact |
|---|-------|--------|
| 3 | `uniqueKey` is client-supplied with no format/length validation | Arbitrary S3 key injection possible |
| 4 | No file size limit enforced at presign time — S3 presigned PUT allows any size upload | Potential S3 storage abuse |
| 5 | Redis validation key has no documented TTL — may persist indefinitely if feed creation never occurs | Redis memory leak |

### Medium Priority

| # | Issue | Impact |
|---|-------|--------|
| 6 | 60-second cooldown is hardcoded — not configurable per user type or environment | Inflexible for different use cases |
| 7 | S3 `temp/` prefix implies a lifecycle policy should delete unclaimed uploads, but this is not confirmed | Orphaned files in S3 |

---

## Test Scenarios

### Functional
- Valid request → presigned URL returned with correct S3 key pattern
- Upload file using returned presigned URL → file appears in S3 at expected key
- Second request within 60 seconds → rate limit error
- Second request after 60 seconds → new presigned URL issued

### Rate Limiting
- Concurrent duplicate requests — only first should succeed
- Redis TTL expiry — request should succeed after 60s
- Different userId/userType combinations — separate cooldown buckets

### Security
- Request without auth (currently succeeds — should be blocked after fix)
- Invalid/negative userId values
- Oversized uniqueKey string
- Content-type mismatch (specify image MIME but upload video)

### Error Handling
- Redis unavailable → behavior (should fail open or closed?)
- AWS S3 presign failure → 500
- Missing required fields → validation error

### Edge Cases
- File extension with leading dot (`.mp4` vs `mp4`)
- Very long uniqueKey
- Special characters in uniqueKey
- userType values outside known enum
