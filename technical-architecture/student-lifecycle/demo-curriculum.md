---
title: Demo Curriculum
category: technical-architecture
subcategory: student-lifecycle
source_id: c7e7022f
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Demo Curriculum

## Overview
The Demo Curriculum system manages the assignment of the correct lesson link to a student for their trial class, using a priority-based fallback algorithm. It generates all possible demographic filter combinations and resolves the best-matching curriculum from the `demo_curriculum` table, supporting wildcard (null) fields for broad-match curricula.

## API Contract

### GET /paathshala/api/v1/curriculum/modules
- **Auth:** `x-api-key` header required
- **Query Params:** `Course` (optional — course name; triggers internal Platform service call)
- **Response:**
```json
[{
  "id": int,
  "name": "string",
  "curriculumVersionId": int,
  "curriculumCategoryId": int,
  "startGrade": int,
  "endGrade": int,
  "active": boolean,
  "courseId": int,
  "durationId": int,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}]
```

### GET /paathshala/api/v1/curriculum/modules/{moduleId}
- **Auth:** `x-api-key` header required
- **Response:** Module details with nested `CurriculumTopics` and `CurriculumProjects` arrays

### POST /api/v1/curriculum/modules
- **Auth:** `x-api-key` header required
- **Request Body (all required):**
```json
{
  "name": "string",
  "curriculumVersionId": int,
  "curriculumCategoryId": int,
  "startGrade": int,
  "endGrade": int,
  "active": boolean,
  "type": "string",
  "courseId": int,
  "durationId": int
}
```
- **Status Codes:** 200 Created, 400 Bad Request (missing required params)

### PATCH /api/v1/curriculum/modules/{moduleId}
- **Auth:** `x-api-key` header required
- **Request Body:** At least one field from POST schema
- **Status Codes:** 200 OK, 400 Bad Request (no params provided)

## Logic Flow

### Controller Layer
Curriculum endpoints routed through `CurriculumController` in Paathshala service.
Demo curriculum resolution via internal function `getDemoCurriculumWithFallBack()`.

### Service/Facade Layer
**`getDemoCurriculumWithFallBack({ grade, countryId, languageId, courseId, scope })`:**
1. `courseId` is mandatory; other fields are optional
2. Generate 8 possible filter combinations using presence/absence (null) of `countryId`, `grade`, `languageId`
3. Execute a single DB query with `Op.or` across all 8 combinations, filtered by `courseId`, `active: 1`, `scope: 'all'`
4. Iterate fetched rows against filter list in strict priority order: `["countryId", "grade", "languageId"]`
5. Return first row that matches the highest-priority available combination (exact match wins over wildcard null)

**Priority logic:** exact `countryId` > null `countryId`; exact `grade` > null `grade`; exact `languageId` > null `languageId`

### High-Level Design (HLD)
- Paathshala (Class Service) owns all curriculum operations
- Platform service called for course metadata resolution when `Course` query param provided
- Sequelize ORM against MySQL/AWS RDS
- Null values in `demo_curriculum` act as wildcards (match any input)

## External Integrations
- **Platform Service:** Called internally to fetch course details when `Course` query parameter provided

## Internal Service Dependencies
- Paathshala DB: `demo_curriculum`, `curriculum_modules`, `curriculum_topics`, `curriculum_projects` tables
- Platform service (intra-cluster): Course and duration resolution

## Database Operations

### Tables Accessed

**`demo_curriculum`:**
| Column | Notes |
|--------|-------|
| courseId | Mandatory for lookup |
| countryId | nullable — null = any |
| languageId | nullable — null = any |
| grade | nullable — null = any |
| lessonLink | URL of the lesson |
| lessonName | Display name |
| active | boolean |
| scope | e.g., 'all' |

**`curriculum_modules` (via GET /modules endpoint):**
Columns: `id, name, curriculumVersionId, curriculumCategoryId, startGrade, endGrade, active, courseId, durationId, created_at, updated_at`

**`CurriculumTopics`** (nested in module detail response):
`id, name, curriculumModuleId, active`

**`CurriculumProjects`** (nested in topic):
`id, name, curriculumTopicId, classNumber, active, platform, title, description, conceptsCovered, imageUrl, lessonPlanLink, projectLink, assignmentLink, sessionBooklet, quizId, bannerImageUrl`

### SQL / ORM Queries
- Single `SELECT` with `Op.or` across 8 filter combinations for demo curriculum fallback
- `WHERE courseId = ? AND active = 1 AND scope = 'all'` base filter
- Sequelize ORM; MySQL on AWS RDS

### Transactions
- Module creation via POST is a single INSERT
- Module update via PATCH is a single UPDATE

## Performance Analysis

### Good Practices
- Single query with `Op.or` for 8 combinations avoids N+1 queries
- Priority resolution is done in-memory after the DB fetch
- API key authentication prevents unauthorized curriculum management

### Performance Concerns
- Large `CurriculumProjects` arrays in the module detail response could be slow for modules with many class sessions
- No pagination documented for `GET /modules` list endpoint

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | `getDemoCurriculumWithFallBack` uses `scope: 'all'` hard-coded — unclear if other scope values are supported |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add index on `demo_curriculum(courseId, active, scope)` for faster fallback lookups
- Add pagination to `GET /paathshala/api/v1/curriculum/modules` list endpoint

### Month 1 (Architectural)
- Cache demo curriculum results per `(courseId, countryId, grade, languageId)` combination in Redis with TTL
- Build admin UI for managing `demo_curriculum` records without direct DB access

## Test Scenarios

### Functional Tests
- Exact match (countryId + grade + languageId all match): returns most specific curriculum
- Partial match (only courseId matches): returns wildcard row
- No match at all: verify graceful null/empty response
- Create module with all required fields: verify 200 response
- Create module with missing field: verify 400 response

### Performance & Security Tests
- Verify `x-api-key` required on POST/PATCH endpoints
- Benchmark fallback query time for `demo_curriculum` table with 10,000+ rows

### Edge Cases
- Multiple rows with same priority level (tie-breaking behavior)
- `scope` value other than 'all' in `demo_curriculum` table
- `courseId` is null in request (should 400 or return empty)

## Async Jobs & Automation
N/A — Demo curriculum resolution is synchronous at class creation time.
