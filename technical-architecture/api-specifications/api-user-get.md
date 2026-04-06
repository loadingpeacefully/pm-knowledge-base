---
endpoint: GET /v1/user
service: eklavya
source_id: 4dfd6346-d5d7-4309-a825-1aeb3260b1c9
original_source_name: user
controller: controllers/user.js:10
service_file: No service layer (direct token extraction)
router_file: routers/user.js:11
auth: JWT required
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/user

## Summary

Stateless endpoint that returns the authenticated user's details directly from the JWT token payload — no database lookup, no external service calls, no Redis. The `authMiddleware` validates the token and populates `req.user`; the controller returns it as-is. Serves parent, teacher, and operations user types.

**Category:** Authentication API — User Session Management
**Owner/Team:** Authentication / User Management Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/user`
**Authentication:** JWT required (`Authorization: Bearer`)

### Query Parameters

None. All user data is sourced from the JWT token payload.

### Request Examples

```
GET /v1/user
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response Format

**Parent user (200):**
```json
{
  "success": true,
  "data": {
    "id": 567, "email": "parent@example.com", "phone": "+1234567890",
    "name": "John Smith", "countryId": 1, "tzId": 12, "dialCode": "+1",
    "status": "active", "created_at": "2024-01-15T10:30:00.000Z",
    "iat": 1700482500, "exp": 1700568900
  },
  "message": "User details fetched"
}
```

**Teacher user (200):**
```json
{
  "data": {
    "id": 123, "email": "teacher@brightchamps.com", "role": "teacher",
    "departmentId": 5, "permissions": ["view_students","schedule_classes"],
    "iat": 1700482500, "exp": 1700568900
  }
}
```

**Operations user (200):**
```json
{
  "data": {
    "id": 789, "username": "ops_user", "role": "operations",
    "permissions": ["manage_students","view_reports","modify_schedules"]
  }
}
```

**No user data in token (200):**
```json
{ "success": false, "data": null, "message": "User details fetched" }
```

**Unauthorized (401):**
```json
{ "success": false, "data": null, "message": "Unauthorized", "error": "AuthenticationError" }
```

**Expired token (401):**
```json
{ "success": false, "data": null, "message": "Token expired", "error": "TokenExpiredError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Unauthorized — missing, invalid, or expired JWT |
| 500 | Server error |

---

## Logic Flow

### Middleware (`authMiddleware`)

1. Extract `Authorization: Bearer <token>` header
2. Verify JWT signature using secret key
3. Check expiration timestamp
4. Decode payload → populate `req.user`

### Controller (`controllers/user.js:10-22`)

1. Read `req.user` (already populated by middleware)
2. Create `ApiResponse({ success: !!user, data: user, message: "User details fetched" })`
3. Return JSON — no additional processing

---

## Microservice Dependencies

**None.** No database queries, no Redis, no external HTTP calls.

**Data source:** JWT token payload only. User data reflects state at token issuance time.

---

## Database & SQL Analysis

**None.** This endpoint performs zero database operations.

### JWT Payload Structure

```json
{
  "id": 567,
  "email": "parent@example.com",
  "phone": "+1234567890",
  "name": "John Smith",
  "role": "parent",
  "countryId": 1, "tzId": 12, "status": "active",
  "permissions": ["view_dashboard", "manage_children"],
  "iat": 1700482500,
  "exp": 1700568900
}
```

### Performance Characteristics

- **Response time:** < 10ms (pure in-memory JWT decode)
- **Database connections:** 0
- **External calls:** 0
- **Horizontally scalable:** Yes — fully stateless

---

## Technical Issues

### Low Priority

| # | Issue | Impact |
|---|-------|--------|
| 1 | JWT payload reflects state at token issuance — user data can be stale (email changed, account deactivated, etc.) | Stale data returned; deactivated users still get data until token expires |
| 2 | No real-time user status validation — blocked users retain access until token expiry | Security gap for urgent account suspensions |
| 3 | Response includes JWT metadata (`iat`, `exp`) — minor data exposure | Client learns token lifecycle details |

---

## Test Scenarios

### Functional
- Valid JWT with parent data
- Valid JWT with teacher data (different fields)
- Valid JWT with operations user data
- JWT with minimal payload (missing optional fields)

### Authentication
- Valid signature → 200
- Invalid signature → 401
- Tampered payload → 401
- Expired token (`exp` in past) → 401
- Future `iat` → behavior validation
- Missing `Authorization` header → 401
- Non-Bearer format → 401

### Performance
- Response time < 10ms target
- 100+ concurrent requests with same token
- Large JWT payload (8KB+) processing

### Security
- JWT signature enforcement
- Token expiry enforcement
- Header injection attempts
- Token replay attack prevention
- Sensitive data in response audit (`iat`, `exp` exposure)

### Edge Cases
- Empty JWT payload
- JWT with null user data
- Very large `permissions` array in payload
- Simultaneous requests with same token
