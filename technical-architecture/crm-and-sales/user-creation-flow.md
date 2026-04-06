---
title: User Creation Flow
category: technical-architecture
subcategory: crm-and-sales
source_id: 1d0e2298
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# User Creation Flow

## Overview
The user creation flow creates or updates parent and student records in Eklavya. It uses phone number as the unique parent identifier, supports atomic SQL transactions for parent+student creation, integrates with ChowkidarService for identity management, and syncs user data back from Zoho CRM webhooks for SM records.

## API Contract
**Primary Endpoint:** `POST /v1/student/parents/create-or-update`
- **Auth:** API key via `apiKeyMiddleware`
- **Request Body:**
```json
{
  "phone": "string (unique parent identifier)",
  "countryId": "string (required if creating new parent with phone)",
  "tzId": "string",
  "timeZone": "string",
  "name": "string (parent name, defaults to 'Parent' if not provided)",
  "email": "string (sanitized and validated)",
  "grade": "string (required to create student record)",
  "studentName": "string",
  "utmSource": "string",
  "courseId": "string",
  "landingPage": "string"
}
```

**Response:** Created/updated parent + student records

**Generic User API:**
`POST /v1/user/create` — Assigns roles and authentication identifiers (email, MPIN, Google OAuth)
- Checks if user+role already exists → returns "User & role already exist for one of the identifiers provided"

## Logic Flow

### Controller Layer
- Validate API key via `apiKeyMiddleware`
- Validate required fields (phone → requires countryId + timezone)
- Delegate to parent/student creation service

### Service/Facade Layer
**Parent Processing:**
1. Search for existing parent using `parentId` (if provided) OR `phone` number
2. IF EXISTS → UPDATE parent record
3. IF NOT EXISTS → CREATE parent record
   - Require `countryId` and `tzId`/`timeZone`
   - Default name: "Parent" if not provided
4. **PlatformService:** Resolve `countryId` → regional dialing code; convert `timeZone` string → `tzId`
5. **ChowkidarService:** `createUserV2` or update — sync identity across BrightChamps ecosystem (email/phone)

**Student Processing:**
1. IF `grade` and `parent_id` provided → create student record
2. Set `hasDemo = true` (auto-grant demo access)
3. Generate unique referral code (auto-assigned)
4. **LanguagePredictionService:** Infer language from UTM source, browser locale, or `courseId`
5. Store `student_language_mappings` (with preference score, deduplication check)

**Full Transaction Wrap:**
- `parents` + `students` + `student_language_mappings` creation wrapped in SQL transaction
- IF any step fails → complete rollback

**Zoho CRM → User Sync (reverse direction):**
- Zoho webhook fires when SM user is created/updated in Zoho CRM
- Prabandhan processes webhook → syncs SM record into `crm_users` SQL table
- Enables internal lookup of Zoho owner IDs by employee email

### High-Level Design (HLD)
```
POST /v1/student/parents/create-or-update
  → apiKeyMiddleware validation
  → Find/Create parent by phone (findOrCreate)
      → IF new: require countryId + timezone
      → PlatformService: countryId → dialing code, timeZone → tzId
      → ChowkidarService: createUserV2 (sync identity)
  → IF grade provided: Create student
      → hasDemo = true
      → Generate referral code
      → LanguagePredictionService (UTM + locale + courseId)
      → student_language_mappings INSERT (with deduplication)
  → SQL TRANSACTION: parents + students + student_language_mappings
      → IF ANY FAIL: ROLLBACK all

[Reverse direction: Zoho → Prabandhan]
Zoho SM user event → webhook → Prabandhan
  → Sync to crm_users table
```

## External Integrations
- **ChowkidarService (Identity Management):** Syncs user identities across BrightChamps services — called on create/update with phone or email

## Internal Service Dependencies
- **Eklavya:** Owns `parents`, `students`, `student_profile`, `student_language_mappings`, `user_identifiers`, `roles`
- **PlatformService:** Country dialing codes, timezone ID resolution
- **ChowkidarService:** User identity synchronization
- **LanguagePredictionService:** Language inference from booking data, locale, course

## Database Operations

### Tables Accessed
- `parents` — INSERT or UPDATE
- `students` — INSERT if grade provided
- `student_profiles` — Extended student profile (gender, school, DOB)
- `student_language_mappings` — Language preference with preference score
- `user_identifiers` — Maps emails/phones to roles (generic user system)
- `roles` — Role assignments (parent, teacher, admin)

### SQL / ORM Queries
- SELECT `parents` WHERE `phone = ?` OR `id = parentId` (findOrCreate)
- INSERT `parents` (phone, countryId, tzId, name)
- INSERT `students` (parentId, grade, name, hasDemo=true, referralCode)
- INSERT `student_language_mappings` WHERE NOT EXISTS (deduplication)
- SELECT `user_identifiers` WHERE `email = ? OR phone = ?` AND `role = ?` (duplicate role check)

### Transactions
- **Critical:** `parents` + `students` + `student_language_mappings` wrapped in SQL transaction
- `user_identifiers` / `roles` updates via ChowkidarService (separate transaction)

## Performance Analysis

### Good Practices
- `findOrCreate` pattern on phone prevents duplicate parent accounts
- Atomic transaction rollback prevents partial records (parent without student or vice versa)
- Language prediction at creation time reduces downstream language-detection latency
- Student referral code auto-generation enables marketing attribution from day 1

### Performance Concerns
- Three external service calls (PlatformService, ChowkidarService, LanguagePredictionService) add creation latency
- SQL transaction holds locks on `parents` and `students` tables during the entire creation process

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Three sequential external service calls in creation path — adds 1-3s latency |
| Low | `hasDemo = true` hardcoded for all new students — not configurable |
| Low | Referral code generation logic not documented — collision risk if not using UUID |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Parallelize PlatformService and LanguagePredictionService calls (both are independent)
- Add rate limiting on `POST /v1/student/parents/create-or-update` to prevent abuse

### Month 1 (Architectural)
- Move ChowkidarService sync to async (post-creation SQS message) to reduce critical path latency
- Implement phone number normalization (E.164 format) before uniqueness check

## Test Scenarios

### Functional Tests
- New parent with phone → parent created, student created (if grade provided), referral code generated
- Existing parent by phone → parent updated, student created (if not existing)
- No name provided → parent name defaults to "Parent"
- No grade provided → parent created, no student record
- Duplicate role check → "User & role already exist" response

### Performance & Security Tests
- Concurrent creation with same phone number → only one parent created (findOrCreate atomicity)
- API key validation — reject requests without valid key

### Edge Cases
- `countryId` not provided for new parent creation → Validation Error
- `email` with invalid format → sanitization rejection
- `timeZone` string not found in Platform → fallback or error
- ChowkidarService unavailable → transaction rollback
- Same language preference submitted twice for same student → deduplication prevents duplicate mapping
