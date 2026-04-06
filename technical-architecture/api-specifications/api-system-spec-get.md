---
endpoint: GET /v1/system-spec
service: eklavya
source_id: 8b5495cd-76b8-48eb-bcb3-6134611ab40f
original_source_name: system-spec
controller: controllers/system-spec.js:8
service_file: services/system-spec.js:57
router_file: routers/system-spec.js:24-30
auth: JWT or API Key
last_documented: 2025-01-26
source_notebook: NB1
---

# GET /v1/system-spec

## Summary

Retrieves device and performance analytics records for a student. Uses a dynamic schema-validated filter strategy: any combination of valid `SystemSpec` model fields can be passed as query parameters; the service automatically validates them against the ORM schema and rejects non-existent or blacklisted fields. Requires at least one valid filter to prevent unscoped full-table queries.

**Category:** Internal API — System Analytics & Device Monitoring
**Owner/Team:** Technical Operations / System Analytics Team

---

## HTTP Contract

**Method:** GET
**Path:** `/v1/system-spec`
**Authentication:** JWT (`Authorization: Bearer`) OR API Key (`X-API-Key`)

### Query Parameters

**Validation source:** `validators/system-spec.js:48-75`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | integer | Yes | Student ID to filter system specs |
| `roomId` | integer | No | Classroom/room identifier |
| `classType` | string | No | Class type (`paid`, `demo`, `trial`) |
| `userAgent` | string | No | Browser user agent string |
| `deviceMemory` | integer | No | Device memory in GB |
| `deviceConcurrency` | integer | No | CPU core count |
| `networkSpeed` | decimal | No | Network speed in Mbps |
| `screenWidth` | integer | No | Screen width in pixels |
| `screenHeight` | integer | No | Screen height in pixels |
| `event` | string | No | System event type (`class_join`, `app_start`) |
| `gpuDetailsDevice` | string | No | GPU device information |
| `gpuDetailsFps` | string | No | GPU FPS capability |
| `gpuDetailsGpu` | string | No | GPU model |
| `deviceType` | string | No | `desktop`, `mobile`, `tablet` |
| `os` | string | No | Operating system |

### Request Examples

```
GET /v1/system-spec?studentId=12345
GET /v1/system-spec?studentId=12345&classType=paid
GET /v1/system-spec?studentId=12345&deviceType=desktop&os=Windows
GET /v1/system-spec?studentId=12345&deviceMemory=8&networkSpeed=50.5&screenWidth=1920&screenHeight=1080
GET /v1/system-spec?studentId=12345&event=class_join&gpuDetailsDevice=NVIDIA&gpuDetailsFps=60
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "data": [
    { "id": 98765, "studentId": 12345, "roomId": 789, "classType": "paid",
      "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "deviceMemory": 16.00, "deviceConcurrency": 8, "networkSpeed": 75.50,
      "screenWidth": 1920, "screenHeight": 1080, "event": "class_join",
      "gpuDetailsDevice": "NVIDIA GeForce RTX 3060", "gpuDetailsFps": "144",
      "gpuDetailsGpu": "RTX 3060 Ti", "deviceType": "desktop", "os": "Windows 11",
      "architecture": "x64", "osVersion": "22H2", "model": "Dell XPS 15",
      "city": "New York", "region": "New York", "source": "classroom_app",
      "ipAddress": "192.168.1.100", "created_at": "2024-11-20T10:30:00.000Z" }
  ],
  "message": "system specs fetched successfully."
}
```

**No results (200):**
```json
{ "success": true, "data": [], "message": "system specs fetched successfully." }
```

**Missing `studentId` (400):**
```json
{ "success": false, "data": null, "message": "studentId cannot be empty.", "error": "ValidationError" }
```

**Invalid filter field (400):**
```json
{ "success": false, "data": null, "message": "Invalid Filter", "error": "BadRequestError" }
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request — validation failed or invalid filter fields |
| 401 | Unauthorized |
| 500 | Internal server error |

---

## Logic Flow

### Controller (`controllers/system-spec.js:8-21`)

1. Pass entire `req.query` object to `SystemSpecService.getSystemSpec(filter)`
2. Format via `ApiResponse` wrapper

### Service (`services/system-spec.js:57-73`)

1. **Schema validation:** call `getValidDbFilter("SystemSpec", filter)`:
   - Compare each query param key against `SystemSpec` model attributes
   - Remove non-existent fields
   - Remove fields in `model.rejectListAttr` (security blacklist)
2. **Empty filter guard:** if no valid filters remain → throw `BadRequestError("Invalid Filter")`
3. **Execute:** `SystemSpec.findAll({ where: validFilter, ...options })`
4. Return array

**Field mapping (API camelCase → DB snake_case):**

| API Param | DB Column |
|-----------|-----------|
| `studentId` | `student_id` |
| `roomId` | `room_id` |
| `classType` | `class_type` |
| `userAgent` | `user_agent` |
| `deviceMemory` | `device_memory` |
| `gpuDetailsDevice` | `gpu_details_device` |
| `ipAddress` | `ip_address` |

---

## Microservice Dependencies

**None.** Database-only. No external service calls.

---

## Database & SQL Analysis

### Dynamic Query

```js
await this.db.SystemSpec.findAll({ where: validFilter })
```

### Example SQL

```sql
-- Single filter
SELECT * FROM system_specs WHERE student_id = 12345;

-- Multiple filters
SELECT * FROM system_specs
WHERE student_id = 12345 AND class_type = 'paid' AND device_type = 'desktop' AND os = 'Windows 11';

-- Performance filter
SELECT * FROM system_specs
WHERE student_id = 12345 AND screen_width = 1920 AND device_concurrency >= 4 AND gpu_details_device LIKE '%NVIDIA%';
```

### Tables Accessed

`system_specs` (single table — no joins)

### Recommended Indexes

```sql
CREATE INDEX idx_system_specs_student_id ON system_specs(student_id);
CREATE INDEX idx_system_specs_student_class_event ON system_specs(student_id, class_type, event);
CREATE INDEX idx_system_specs_device_type_os ON system_specs(student_id, device_type, os);
CREATE INDEX idx_system_specs_performance ON system_specs(student_id, device_memory, network_speed);
CREATE INDEX idx_system_specs_room_created ON system_specs(student_id, room_id, created_at);
CREATE INDEX idx_system_specs_common_filters ON system_specs(student_id, class_type, device_type, event, created_at);
```

---

## Technical Issues

### Low Priority

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | No pagination — could return large result sets for students with many spec records | Service layer | Memory/response time |
| 2 | No default `ORDER BY` clause — results are in arbitrary DB order | `services/system-spec.js:63-66` | Inconsistent ordering |
| 3 | No date range filtering — cannot scope to recent sessions | Validator | Limited analytics use |
| 4 | Generic "Invalid Filter" error doesn't specify which fields failed | `getValidDbFilter` | Poor developer experience |

---

## Test Scenarios

### Functional
- `studentId` only (broadest filter)
- `studentId` + `classType`
- `studentId` + multiple filters (device, OS, GPU, event)
- Performance specs (memory, network speed, screen resolution)
- No matching records for valid filter → empty array

### Validation
- Missing `studentId` → 400
- Invalid field name (e.g., `badField=123`) → 400 "Invalid Filter"
- Non-integer `studentId`
- Valid field names with invalid data types

### Security
- Auth enforcement (JWT and API key)
- Field injection via unknown query params (blocked by schema validation)
- SQL injection via field values (blocked by Sequelize ORM)

### Performance
- Response time with single vs multiple filters
- Large result sets (students with many spec records)
- Concurrent requests

### Edge Cases
- Student with zero system spec records → empty array
- Specs with null optional fields
- Very long user agent strings
- Special characters in city/region names
- Decimal precision in memory and network speed
