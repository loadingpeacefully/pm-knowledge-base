---
endpoint: POST /v1/feed/showcase-title-and-desc
service: eklavya
source_id: eb9821a3-9f9c-4b01-9063-3bd8b4d64ef3
original_source_name: showcase-title-and-desc
controller: controllers/feed.js:52
service_file: facades/feed.js:389
router_file: routers/feed.js:41
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# POST /v1/feed/showcase-title-and-desc

## Summary

AI-powered endpoint that generates a short catchy title ("hook", max 40 chars) and a longer caption for student showcase videos. Accepts a multipart audio file upload, transcribes it via OpenAI Whisper (through SenpaiService), then passes the transcript to a custom LLM to generate structured content. If transcription fails or produces no output, falls back to using the project name as input. S3 upload of the transcript text and LLM content generation execute in parallel. Requires JWT or API key authentication.

**Category:** Feed Management API — AI Content Generation
**Owner/Team:** Feed Management & AI Content Generation Team

---

## HTTP Contract

**Method:** POST
**Path:** `/v1/feed/showcase-title-and-desc`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)
**Content-Type:** `multipart/form-data`

### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `projectName` | string | Yes | Name of the project/video being showcased (trimmed, non-empty) |
| `userType` | string | Yes | User type creating the showcase (e.g., `student`) |
| `userId` | integer (≥1) | Yes | ID of the user creating the showcase |
| `audioFile` | file | Yes | Audio file to transcribe (multipart upload) |

### Request Examples

```
POST /v1/feed/showcase-title-and-desc
Content-Type: multipart/form-data
Authorization: Bearer <jwt-token>

projectName: My Python Calculator App
userType: student
userId: 123
audioFile: <audio-file>
```

### Response Format

**Success with transcript (200):**
```json
{
  "success": true,
  "data": {
    "hook": "Build Amazing Apps with Python! 🚀",
    "caption": "Watch me create an awesome calculator app using Python! This project taught me about user interfaces, mathematical operations, and clean code practices. #PythonProgramming #StudentShowcase #CodeLearning",
    "transcriptUrl": "https://s3.amazonaws.com/feed-bucket/transcripts/1699123456789_student_123.txt"
  },
  "message": "Showcase Hook, Caption and Transcript Url fetched successfully"
}
```

**Success with fallback (no transcript) (200):**
```json
{
  "success": true,
  "data": {
    "hook": "Check Out My Latest Project! ✨",
    "caption": "Excited to share my latest coding project - My Python Calculator App! ...",
    "transcriptUrl": "https://s3.amazonaws.com/feed-bucket/transcripts/1699123456789_student_123.txt"
  },
  "message": "Showcase Hook, Caption and Transcript Url fetched successfully"
}
```

**No file uploaded (400):**
```json
{ "success": false, "data": null, "message": "No file uploaded", "error": "BadRequest" }
```

**AI service failure (500):**
```json
{ "success": false, "data": null, "message": "Error in generateTranscriptFromAudio", "error": "InternalError" }
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `hook` | string | AI-generated catchy title (max 40 characters) |
| `caption` | string | AI-generated engaging caption describing the project and learning journey |
| `transcriptUrl` | string | S3 URL where the audio transcript text is stored |

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Hook, caption, and transcript URL generated |
| 400 | Missing file upload or validation error |
| 401 | Invalid or missing authentication |
| 500 | AI service or S3 failure |

---

## Logic Flow

### Controller (`controllers/feed.js:52-74`)

1. Validate `req.files.audioFile` present — return 400 if missing
2. Extract `projectName`, `userType`, `userId` from body
3. Pass `audioFile[0].buffer` to `FeedFacade.getShowCaseTitleAndDesc()`
4. Return structured response

### Facade (`facades/feed.js:389-409`)

**Phase 1 — Audio transcription:**
1. Convert audio buffer to `PassThrough` stream
2. Generate unique filename: `audio_{timestamp}_{random}.mp3`
3. Call `SenpaiService.generateTranscriptFromAudio({ bufferStream, fileName })`
4. Receive plain-text transcript from OpenAI Whisper

**Phase 2 — Parallel execution:**
5. Generate S3 key: `transcripts/{timestamp}_{userType}_{userId}.txt`
6. Run simultaneously via `Promise.all`:
   - Upload transcript buffer to S3 as `text/plain; charset=utf-8`
   - Call `generateTitleAndDescFromTranscript(projectName, transcript)`

**Phase 3 — AI content generation (`facades/feed.js:369-387`):**
7. Input selection: `transcript?.length > 0` → `"Transcript: {transcript}"` else `"Project Name: {projectName}"`
8. Call `SenpaiService.generateResponse(SYSTEM_PROMPT_FOR_HOOK_AND_CAPTION, userInput)`
9. Parse JSON response for `{ hook, caption }`

**Phase 4 — Response assembly:**
10. Return `{ hook, caption, transcriptUrl: s3UploadResult.Location }`

---

## Microservice Dependencies

| Service | Call | Trigger | Parallelism |
|---------|------|---------|-------------|
| SenpaiService | `generateTranscriptFromAudio({ bufferStream, fileName })` | Always | Sequential (must complete before AI generation) |
| SenpaiService | `generateResponse(systemPrompt, userInput)` | Always | Parallel with S3 upload |
| AWS S3 | `uploadFile({ bucketName, fileKey, buffer, contentType })` | Always | Parallel with AI generation |

**AI processing latency:** Transcription ~2–5 seconds + content generation ~1–3 seconds (total ~3–8 seconds typical)

**Fallback:** If Whisper transcription returns empty, content generation uses `projectName` as input — request still succeeds.

### S3 Storage Pattern

```
transcripts/{timestamp}_{userType}_{userId}.txt
```

Example: `transcripts/1699123456789_student_123.txt`

---

## Database & SQL Analysis

**No direct database queries.** This endpoint is purely service-oriented.

**Indirect DB access via auth middleware:**
- JWT validation (token decode, no DB query)
- API key validation (may query `api_keys` table)

**Persistent storage:** S3 transcript file only. Generated hook/caption are not stored in the database.

---

## Technical Issues

### Medium Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No request rate limiting — any authenticated user can trigger unlimited AI API calls, incurring cost | Router/middleware | OpenAI cost abuse; service degradation |
| 2 | Entire audio file loaded into server memory as buffer — large files cause memory pressure | Controller: `audioFile[0].buffer` | Memory exhaustion for large uploads |
| 3 | No request deduplication — same audio processed multiple times unnecessarily | Facade | Wasted AI processing cost and latency |

### Low Priority

| # | Issue |
|---|-------|
| 4 | No audio file format or size validation — any file type accepted |
| 5 | AI service errors have limited context for debugging |
| 6 | No usage tracking per user — cannot implement per-user AI budget controls |
| 7 | Hardcoded S3 file naming convention in facade — not configurable |
| 8 | Generated content (hook/caption) not persisted — cannot be retrieved later |

---

## Test Scenarios

### Functional
- Valid audio file with clear speech → hook + caption + transcript URL returned
- Audio with unclear/noisy speech → fallback content generated from project name
- Silent/empty audio → fallback to project name
- Various audio formats (MP3, WAV, M4A)

### AI Behavior
- Hook ≤ 40 characters
- Caption contains project name and educational context
- Fallback hook/caption when transcript is empty
- Different `projectName` values → different hook/caption styles

### Authentication
- Valid JWT → 200
- Valid API key → 200
- No auth → 401
- Expired token → 401

### Validation
- Missing `audioFile` → 400
- Missing `projectName` → 400 with field error
- Missing/invalid `userId` → 400
- Empty `projectName` → 400

### Error Handling
- SenpaiService (Whisper) unavailable → 500
- S3 upload fails → behavior (does it still return hook/caption without URL?)
- AI content generation returns malformed JSON → 500

### Performance
- Response time for 30-second audio vs 5-minute audio
- Concurrent requests from same user
- S3 + AI generation parallelism verified (should not be sequential)

### Edge Cases
- Audio in non-English language
- Project name with special characters / emojis
- Very long project name (>255 chars)
- Audio file 0 bytes
