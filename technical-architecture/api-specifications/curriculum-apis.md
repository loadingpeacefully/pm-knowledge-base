---
title: Curriculum APIs
category: technical-architecture
subcategory: api-specifications
source_id: 9b6f85ee
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Curriculum APIs

## Overview
The Curriculum APIs, housed in the Paathshala (Class Service), manage the creation, retrieval, and update of curriculum modules, topics, and projects used in BrightChamps paid classes. A specialized fallback algorithm (`getDemoCurriculumWithFallBack`) handles the assignment of demo lesson links using priority-based wildcard matching.

## API Contract

### GET /paathshala/api/v1/curriculum/modules
- **Auth:** `x-api-key` header required
- **Query Params:** `Course` (optional — course name)
- **Response:**
```json
[{
  "id": int,
  "name": "string",
  "curriculumVersionId": int,
  "curriculumCategoryId": int,
  "startGrade": int,
  "endGrade": int,
  "active": true,
  "courseId": int,
  "durationId": int,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}]
```

### GET /paathshala/api/v1/curriculum/modules/{moduleId}
- **Auth:** `x-api-key` header required
- **Response:** Module details with nested structure:
```json
{
  "id": int,
  "name": "string",
  "CurriculumTopics": [{
    "id": int,
    "name": "string",
    "curriculumModuleId": int,
    "active": boolean,
    "CurriculumProjects": [{
      "id": int,
      "name": "string",
      "curriculumTopicId": int,
      "classNumber": int,
      "active": boolean,
      "platform": "string",
      "title": "string",
      "description": "string",
      "conceptsCovered": "string",
      "imageUrl": "string",
      "lessonPlanLink": "string",
      "projectLink": "string",
      "assignmentLink": "string",
      "sessionBooklet": "string",
      "quizId": int,
      "bannerImageUrl": "string"
    }]
  }]
}
```

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
- **Status Codes:** 200 OK, 400 Bad Request (no params)

## Logic Flow

### Controller Layer
`CurriculumController` handles CRUD operations; `getDemoCurriculumWithFallBack` is an internal service function called at class creation time.

### Service/Facade Layer

**Standard Module Management:**
1. GET modules: fetch all; optionally call Platform service for course details if `Course` query param provided
2. GET module by ID: nested JOIN across `curriculum_modules` → `curriculum_topics` → `curriculum_projects`
3. POST module: validate all required fields → INSERT into `curriculum_modules`
4. PATCH module: validate at least one field → UPDATE `curriculum_modules` WHERE `id`

**`getDemoCurriculumWithFallBack({ grade, countryId, languageId, courseId, scope })`:**
1. `courseId` is mandatory; other fields optional
2. Generate 8 filter combinations: all permutations of null/value for `countryId`, `grade`, `languageId`
3. Single DB query: `SELECT WHERE courseId = ? AND active = 1 AND scope = 'all' AND (combination_1 OR combination_2 OR ... OR combination_8)`
4. Priority resolution (in-memory): iterate fetched rows against filter list in order `["countryId", "grade", "languageId"]`
5. Exact match wins over null (wildcard); return first fully matching row

**Priority Example:**
- Input: `countryId=5, grade=7, languageId=2`
- Highest priority: row with `countryId=5, grade=7, languageId=2`
- Next: `countryId=5, grade=7, languageId=null`
- Next: `countryId=5, grade=null, languageId=2`
- ... down to `countryId=null, grade=null, languageId=null` (universal fallback)

### High-Level Design (HLD)
- Paathshala owns all curriculum data; Sequelize ORM; MySQL on AWS RDS
- Platform service provides course metadata when needed
- Null columns in `demo_curriculum` act as wildcards for broad-match curricula

## External Integrations
- **Platform Service:** Called when `Course` query param provided to resolve course details

## Internal Service Dependencies
- Paathshala DB: All curriculum tables
- Post-payment onboarding flow: `/curriculum/student/module` assigns modules to newly enrolled students

## Database Operations

### Tables Accessed

**`curriculum_modules`:**
`id, name, curriculumVersionId, curriculumCategoryId, startGrade, endGrade, active, courseId, durationId, created_at, updated_at`

**`curriculum_topics`:**
`id, name, curriculumModuleId, active`

**`curriculum_projects`:**
`id, name, curriculumTopicId, classNumber, active, platform, title, description, conceptsCovered, imageUrl, lessonPlanLink, projectLink, assignmentLink, sessionBooklet, quizId, bannerImageUrl`

**`demo_curriculum`:**
`courseId, countryId (nullable), languageId (nullable), grade (nullable), lessonLink, lessonName, active, scope`

### SQL / ORM Queries
- SELECT modules with optional JOIN to Platform for course details
- SELECT module by ID with nested JOIN: modules → topics → projects
- INSERT into `curriculum_modules` on POST
- UPDATE `curriculum_modules` on PATCH
- Single `Op.or` query across 8 combinations for demo curriculum fallback

### Transactions
- Module creation: single INSERT (no multi-table transaction needed)
- Module update: single UPDATE

## Performance Analysis

### Good Practices
- Single `Op.or` query for 8 demo curriculum combinations avoids N+1 queries
- In-memory priority resolution after one DB fetch is efficient
- API key auth prevents unauthorized curriculum modifications

### Performance Concerns
- Nested topics + projects JOIN can produce large payloads for module-with-many-classes
- No pagination on module list endpoint

### Technical Debt
| Severity | Issue |
|----------|-------|
| Low | `scope = 'all'` is hard-coded in `getDemoCurriculumWithFallBack` — other scope values not documented |
| Low | No curriculum versioning strategy documented for migrating students between curriculum versions |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Add pagination to `GET /curriculum/modules` list endpoint
- Add composite index on `demo_curriculum(courseId, active, scope)` for fallback query

### Month 1 (Architectural)
- Cache `getDemoCurriculumWithFallBack` results per `(courseId, countryId, grade, languageId)` in Redis
- Build curriculum version migration tooling for bulk student re-assignment

## Test Scenarios

### Functional Tests
- GET modules with no Course param → all modules returned
- GET modules with valid Course param → Platform service called, course-filtered response
- GET module by ID → nested topics and projects returned correctly
- POST module with all required fields → 200 response
- POST module with missing `courseId` → 400 response
- PATCH module with `active = false` → module deactivated
- Demo curriculum fallback: exact match → most specific row returned
- Demo curriculum fallback: no exact match → wildcard row returned

### Performance & Security Tests
- Verify `x-api-key` required on all write endpoints
- Benchmark nested module detail query for module with 50+ projects

### Edge Cases
- PATCH with no body fields → 400 response
- Demo curriculum with no matching row at all → null/empty response
- `courseId` null in `getDemoCurriculumWithFallBack` → should 400

## Async Jobs & Automation
- **Post-payment onboarding flow:** `/curriculum/student/module` called from onboard-flow SQS consumer to assign curriculum modules to newly paid students
