---
title: Hubs
category: technical-architecture
subcategory: infrastructure
source_id: 64cc014d-6574-4922-9048-9d065ac43dca
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Hubs

## Overview
This document describes the Hubs feature in BrightCHAMPS — a group-based class management system that allows students to be organized into multi-student groups (Regular Classes, Webinars, Workshops, Annual Events, Cohort Creation) at physical or virtual hub locations, with dedicated APIs for admin management and attendance tracking.

## API Contract
**Admin Dashboard APIs:**
- `GET /getGroups` — List groups within a hub
- `POST /createGroups` — Create a new group
- `PUT /editGroup` — Edit group details
- `POST /addStudentGroupMapping` — Add a student to a group
- `POST /addGroupSchedule` — Add schedule slots to a group
- `GET /getCoursePackages` — Get available packages for a course
- `GET /getPackageDetails` — Get package details

**Teacher Dashboard APIs:**
- `GET /getStudentClasses` — Fetch group classes for a student (requires `groupClassBalanceId` filter)
- `GET /getGroupClassCount` — Get total group class count

**Auth:** Standard Bearer token authentication assumed.

## Logic Flow
### Controller Layer
Admin users manage groups via the Dronacharya/Prashashak interface. Teachers mark attendance from the Teacher Dashboard. Students view their group classes via the Student Dashboard.

### Service/Facade Layer
**Group Class Lifecycle:**
1. Admin creates a Group in a Hub with course, package (Hub_package or otm_package), teacher assignment, grade range, and schedule
2. Students are mapped to the group via `addStudentGroupMapping`
3. Classes are scheduled via `addGroupSchedule` (weekday + hour)
4. Teacher marks attendance via dronacharya/prashashak dashboard
5. Marking attendance updates `paid_classes.class_status_id` for each student in the group
6. Group Class Balance (GCB) is updated if at least one student attends
7. For offline classes, GCB update happens specifically at attendance marking time

**Attendance and GCB Logic:**
- GCB updates on any single student attendance — not all students required
- Offline classes: GCB update triggered at attendance marking
- Teacher earnings calculated from GCB and `paid_classes` tables (completed class count)

### High-Level Design (HLD)
```
Hub (physical/virtual location)
        │
        ▼
Group (group_type: Regular | Webinar | Workshop | Annual Event | Cohort)
        │
        ├── Group-Student-Mapping (students enrolled)
        ├── Group-Schedule (weekday + hour slots)
        └── GroupClassBalance (total vs completed classes)
                │
                ▼
        Paid Classes (individual class records per student)
                │
                ▼
        Attendance Marking (Teacher Dashboard)
                │
                ▼
        GCB Updated → Teacher Payout Calculated
```

## External Integrations
N/A — Hubs is an internal platform feature with no direct third-party integrations documented.

## Internal Service Dependencies
- Hubs → Dronacharya (teacher service for attendance and teacher data)
- Hubs → Paathshala (class scheduling and paid class management)
- Hubs → Eklavya (student profile and class balance)
- Hubs → Payments (package management — Hub_package vs otm_package)
- Prashashak BE → Hubs management APIs (admin operations)

## Database Operations
### Tables Accessed

**hubs**
| Column | Type | Description |
|--------|------|-------------|
| id | PK | Hub identifier |
| name | string | Hub name |
| AddressLine | string | Physical address |
| zip_code | string | ZIP/postal code |
| country_id | FK | Country reference |
| state | string | State/region |
| timezone_id | FK | Timezone reference |

**Group**
| Column | Type | Description |
|--------|------|-------------|
| group_type | ENUM | Regular Classes / Webinars / Workshop / Annual Event/Activity / Cohort Creation |
| name | string | Group name |
| course_id | FK | Associated course |
| hub_id | FK | Parent hub |
| package_id | FK | Associated package |
| max_students | int | Enrollment cap |
| teacherId | FK | Primary teacher |
| secondaryTeacherId | FK | Secondary teacher |
| minGrade / maxGrade | int | Student grade range |
| start_at | datetime | Group start date |
| status | ENUM | active / inactive / completed |
| classType | ENUM | online / offline |

**Group-student-mapping**
| Column | Description |
|--------|-------------|
| groupId | FK to Group |
| studentId | FK to student |
| Status | Enrollment status |

**Group-schedule**
| Column | Description |
|--------|-------------|
| group_id | FK to Group |
| weekday | Day of week |
| hour | Hour of class |

**GroupClassBalance**
| Column | Description |
|--------|-------------|
| groupId | FK to Group |
| totalClasses | Total scheduled classes |
| completedClasses | Completed classes count |

**Paid Classes**
| Column | Description |
|--------|-------------|
| Class_status_id | Class status reference |
| groupclassbalanceId | FK to GroupClassBalance |
| student_id | FK to student |
| Start_at | Class start time |
| Duration | Class duration |
| Meeting_id | Associated meeting |
| Reference_id | External reference |

**Packages**
| Column | Description |
|--------|-------------|
| package_type | Hub_package or otm_package |

### SQL / ORM Queries
- Student class fetch: requires `groupClassBalanceId` filter in `getStudentClasses`
- Teacher earnings: JOIN `GroupClassBalance` + `paid_classes` WHERE status = completed
- Attendance update: UPDATE `paid_classes` SET class_status = attended WHERE groupclassbalanceId = :id AND student_id IN (attendees)

### Transactions
- Attendance marking updates both `paid_classes` (per student) and `GroupClassBalance` — should be wrapped in a transaction to maintain consistency

## Performance Analysis
### Good Practices
- GroupClassBalance as a separate aggregate table prevents recalculation on every query
- `max_students` cap prevents over-enrollment at group level
- Secondary teacher support provides operational resilience

### Performance Concerns
- Marking attendance for large groups (high `max_students`) requires updating multiple `paid_classes` rows — potential slow write
- `getStudentClasses` requiring explicit `groupClassBalanceId` filter means clients must know the balance ID — coupling concern

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | No documented transaction wrapping for attendance + GCB update — data inconsistency risk |
| Medium | GCB updates on any single student attendance — edge case when only one student attends briefly |
| Medium | Multiple group membership edge case not yet handled (listed as future scope) |
| Low | OTM and Online Groups features are incomplete (listed as future scope) |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Add explicit database transaction wrapping for attendance marking + GCB update
- Document index strategy for `Group-student-mapping.groupId` and `paid_classes.groupclassbalanceId`

### Month 1 (Architectural)
- Implement curriculum redshifting for unattended/cancelled group classes (future scope item)
- Build group class rescheduling functionality
- Handle multi-group student edge cases
- Complete OTM and Online Group functionality

## Test Scenarios
### Functional Tests
- Group created with correct max_students, grade range, and schedule
- Student mapped to group and class appears in `getStudentClasses`
- Attendance marked by teacher updates `paid_classes` for all present students
- GCB increments when at least one student attends
- Teacher payout calculation reflects completed class count from GCB

### Performance & Security Tests
- Concurrent attendance marking for large groups (50+ students) — verify no race conditions on GCB update
- Admin can only access hub groups within their assigned scope

### Edge Cases
- All students absent from a class — GCB should NOT update
- Student leaves and re-enrolls in the same group — prevent duplicate mapping
- Teacher marks attendance for an already-completed class — should be blocked or flagged

## Async Jobs & ETL
N/A — Hubs is a synchronous operational feature. No async jobs documented for this flow.
