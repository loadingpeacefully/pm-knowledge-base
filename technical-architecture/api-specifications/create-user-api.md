---
title: Create User API
category: technical-architecture
subcategory: api-specifications
source_id: 1f7bf74c
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Create User API

## Overview
The Create User API, managed by the Chowkidar (Auth) service, handles creation of user accounts with role and identifier assignments. It supports multiple authentication types (email/password, Google OAuth, phone/MPIN) and uses an idempotent upsert-style flow that creates a user if new, or adds a missing identifier/role if the user already exists.

## API Contract

### POST /[chowkidar]/create-user (exact path not documented)
- **Auth:** Internal / admin system
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "type": "parent|teacher|admin",
  "email": "saswata.mid@brightchamps.com",
  "phone": "6666657319",
  "countryId": 1
}
```
- **Response (200 — User Created):**
```json
{
  "success": true,
  "data": [],
  "message": "User created succesfully",
  "status": 200,
  "errors": []
}
```
- **Response (200 — Already Exists):**
```json
{
  "success": true,
  "data": [],
  "message": "User & role already exist for one of the identifiers provided",
  "status": 200,
  "errors": []
}
```

## Logic Flow

### Controller Layer
`POST /create-user` → UserController.createUser()

### Service/Facade Layer
**User Creation Flow (wrapped in DB transaction):**

1. **Payload Transformation:** Map incoming `type` + `email`/`phone` to role, `identifier_type`, and `identifier_value`

2. **Identifier Check:** SELECT from `user_identifiers` WHERE email OR phone matches → determine if user exists

3. **If User Already Exists:**
   a. Fetch `user_id` of matching identifier
   b. For each identifier type/value pair in request:
      - Check if `identifier_type` already exists for that `user_id`
      - If not: generate secret (`identifier_secret`) and add to payload
      - If `identifier_type = 'mpin'`: add `countryId` to payload
   c. Check if requested role already exists for `user_id`
   d. If role doesn't exist: create role
   e. If role exists AND no new identifiers to add: return "User & role already exist" message (no-op)

4. **If User Does Not Exist:**
   a. INSERT new user → capture new `user_id`
   b. CREATE role for new `user_id`

5. **Identifier Insertion:** INSERT eligible identifier payload into `user_identifiers` using existing or new `user_id`

### High-Level Design (HLD)

**Identifier Types:**
| `identifier_type` | `identifier_value` | `identifier_secret` |
|-------------------|--------------------|---------------------|
| `email` | Email address | Hashed password |
| `google` | Email address | null |
| `mpin` | Phone number | 4-digit MPIN |

**User Types:** `parent`, `teacher`, `admin`

**Atomicity:** The entire flow (user INSERT + role INSERT + identifier INSERT) is wrapped in a single database transaction. On any error, all operations are rolled back.

## External Integrations
N/A — Chowkidar is self-contained; no external services called.

## Internal Service Dependencies
- Eklavya (Student Service): Calls `POST /v1/student/parents/create-or-update` which internally calls Chowkidar for identity management
- All other services: Depend on Chowkidar for JWT issuance and role resolution

## Database Operations

### Tables Accessed

**`users`:**
| Column | Notes |
|--------|-------|
| id | PK, Auto Increment |
| (other user fields) | Not detailed in source |

**`user_identifiers`:**
| Column | Notes |
|--------|-------|
| id | PK |
| user_id | FK → users |
| identifier_type | email, google, mpin |
| identifier_value | Email or phone |
| identifier_secret | Hashed password, null, or 4-digit MPIN |
| (countryId for mpin) | |

**`roles`:**
| Column | Notes |
|--------|-------|
| id | PK |
| user_id | FK → users |
| role | parent, teacher, admin |

### SQL / ORM Queries
- SELECT `user_identifiers` WHERE `identifier_value IN (email, phone)` for existence check
- INSERT into `users` for new user
- INSERT into `roles` for new user or new role
- INSERT into `user_identifiers` for new identifier

### Transactions
- Entire user creation flow wrapped in a DB transaction: users INSERT + roles INSERT + user_identifiers INSERT
- On any failure → full rollback to prevent partial user creation

## Performance Analysis

### Good Practices
- Full transaction rollback prevents partial user states (user created but no role/identifier)
- Idempotent design: calling the API twice for the same user is a no-op, not an error
- Separate `identifier_type` allows a single user to have multiple auth methods

### Performance Concerns
- Sequential SELECT → INSERT pattern within a transaction; acceptable at low volume but may cause lock contention at high volume

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | Exact API endpoint path not documented in source |
| Low | `identifier_secret` generation logic not detailed (especially for hashed password) |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Document exact endpoint path and add to API catalog
- Add index on `user_identifiers(identifier_value)` for fast existence checks

### Month 1 (Architectural)
- Implement rate limiting on user creation to prevent bulk account creation abuse
- Add audit log table for user creation events (who created, from which service)

## Test Scenarios

### Functional Tests
- Create new parent user with email and phone → user, role, and both identifiers created
- Create user with same email again → "User & role already exist" message (no-op)
- Create user with same email but different role (e.g., teacher) → role added, existing user not duplicated
- Create user with `mpin` type → `countryId` added to identifier payload

### Performance & Security Tests
- Verify hashed password stored (not plain text) for email identifier type
- Concurrent creation of same user from two requests → transaction ensures only one user created (no duplicate)

### Edge Cases
- User exists but with only email identifier; request includes phone → phone identifier added
- Role already exists AND no new identifiers → exactly "User & role already exist" message returned
- DB transaction failure mid-way → verify complete rollback

## Async Jobs & Automation
N/A — Synchronous API; no async processing.
