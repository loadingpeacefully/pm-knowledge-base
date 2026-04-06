---
title: Summer Camp
category: technical-architecture
subcategory: student-lifecycle
source_id: 0d841d4e
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Summer Camp (KT)

## Overview
The Summer Camp system manages student enrollment, payment processing, and scheduling for BrightChamps summer camp programs. Summer camps are modeled as "add-on materials" in the Eklavya service. DIY camps are auto-enrolled via code; teacher-led masterclasses require manual OPs scheduling through the Prashashak admin dashboard.

## API Contract

### POST /enroll-student-summer-camp (Eklavya Service)
- **Auth:** Internal / landing page triggered
- **Purpose:** Primary enrollment endpoint; books trial class and creates add-on sale records
- **Request Body:**
```json
{
  "studentId": int,
  "studentName": "string",
  "parentName": "string",
  "phone": "string",
  "email": "string",
  "grade": int,
  "tzId": int,
  "countryId": int,
  "currency": "string",
  "aggregator": "string",
  "addonMaterialIds": [int],
  "country": "string",
  "planType": "string",
  "utmCampaign": "string",
  "utmContent": "string",
  "utmMedium": "string",
  "utmSource": "string",
  "utmTerm": "string",
  "campDateTime": "ISO8601",
  "timezone": "string",
  "objectId": "string",
  "landingPage": "string"
}
```

### POST /paathshala/api/v1/groups/enroll-student
- **Auth:** `x-api-key` (admin/ops)
- **Request Body:** `{ "student_id": int, "group_name": "string" }`
- **Purpose:** Enroll student in a teacher-led summer camp group; creates `paid_classes` records and curriculum mappings

### POST /paathshala/api/v1/groups/remove-student
- **Auth:** `x-api-key` (admin/ops)
- **Request Body:** `{ "student_id": int, "group_name": "string" }`
- **Purpose:** Remove student from group and refund diamonds to `student_credit`

### /v1/booking/tracker and /v1/booking/create
- Called sequentially during enrollment flow to register the trial booking

## Logic Flow

### Controller Layer
`POST /enroll-student-summer-camp` → Eklavya EnrollmentController → multi-step orchestration

### Service/Facade Layer
**Enrollment Flow:**
1. Create or update parent record in `eklavya.parents`
2. Create or update student record linked to parent via `parent_id` + `grade`
3. Call booking APIs sequentially: `/v1/booking/tracker` → `/v1/booking/create` (partial trial booking)
4. Create `addon_material_sale_initiators` record
5. Create `addon_material_sale_payments` record
6. Call `initiateCombinedPayment()` → generate payment page link → return to client → redirect to payment

**Post-Payment Callback:**
1. Call `recordPaymentForAddonMaterialSalePayment()`
2. Award student a diamond
3. Check `ConfigManager.get("SUMMER_CAMP_ACTIVITY_MAPPING")` for DIY mapping:
   - If exists → auto-enroll in DIY activity via `nanoSkillSCommonervice.enrollStudentToActivity()`
4. If summer camp add-on material present → call `sendSummerCampOnboardingEmail()` (CC: prachi.goel@brightchamps.com, suneet.jagdev@brightchamps.com)
5. Attempt Google Sheets insert via App Script API (currently broken)

**OPs Scheduling (Teacher-Led Masterclasses):**
1. OPs create group via Prashashak: type = `summercamp`, 10-class schedule, assign teacher
2. Select grade group and curriculum; set class cost = 30 diamonds
3. Use `POST /paathshala/api/v1/groups/enroll-student` with student ID + group name
4. System creates `paid_classes` records and links curriculum to student

### High-Level Design (HLD)
- Summer camps are modeled as `addon_materials` (IDs 43–65)
- DIY camps: automated enrollment via code
- Teacher-led camps: manual OPs workflow in Prashashak
- Payment flow same as standard add-on purchase
- Diamond currency used for class cost (30 diamonds per class)

## External Integrations
- **Google Sheets (App Script API):** Intended for summer camp data logging — **currently not functional**
- **Email Provider (via Hermes):** Onboarding email to parent + internal CC
- **Payment Aggregators:** Standard payment gateway for add-on purchase

## Internal Service Dependencies
- Eklavya: `parents`, `students`, `addon_materials`, `addon_material_sale_initiators`, `addon_material_sale_payments`, `student_credit`
- Tryouts: Booking tracker and creation APIs
- Paathshala: Group enrollment, `paid_classes` creation, curriculum mapping
- NanoSkillS Common Service: DIY activity enrollment

## Database Operations

### Tables Accessed

**`eklavya.parents`:** Parent details

**`eklavya.students`:** Student details (linked to parent)

**`eklavya.addon_materials`:** Summer camp definitions (IDs 43–65)

**`addon_material_sale_initiators`:** Records purchase initiation

**`addon_material_sale_payments`:** Payment status tracking for add-on purchase

**`paid_classes`:** Updated with 10-class schedule when enrolled in teacher-led group

**`student_credit`:** Diamond credits; refunded when student removed from group

### SQL / ORM Queries
- UPSERT on `eklavya.parents` and `eklavya.students`
- INSERT `addon_material_sale_initiators` and `addon_material_sale_payments`
- INSERT `paid_classes` batch (10 rows) when enrolling in teacher-led group
- UPDATE `student_credit` on diamond award and refund

### Transactions
- Group enrollment creates `paid_classes` records atomically
- Group removal refunds diamonds and removes mapping atomically

## Performance Analysis

### Good Practices
- Config-driven DIY activity mapping (`ConfigManager`) allows runtime control without code deploys
- Group enrollment/removal atomicity ensures no half-enrolled states

### Performance Concerns
- Google Sheets App Script API integration is broken — failures are silently swallowed

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Google Sheets insert via App Script API is documented as "currently not working" — data logging for summer camp is broken |
| Medium | Hard-coded internal email CCs (`prachi.goel`, `suneet.jagdev`) in onboarding email function |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Fix or remove the broken Google Sheets App Script integration
- Replace hard-coded email CCs with a config-driven list

### Month 1 (Architectural)
- Automate the teacher-led masterclass scheduling via an API instead of requiring manual OPs intervention
- Build an OPs dashboard widget for bulk summer camp enrollment

## Test Scenarios

### Functional Tests
- Enroll student in summer camp → verify parent/student created, trial booking created, payment link returned
- Successful payment → verify diamond awarded, onboarding email sent, DIY activity enrolled if mapped
- OPs enroll student in teacher-led group → verify 10 `paid_classes` records created
- OPs remove student from group → verify diamonds refunded to `student_credit`

### Performance & Security Tests
- Verify `/enroll-student-summer-camp` does not expose student financial data
- Test concurrent enrollments for the same parent/student to prevent duplicate records

### Edge Cases
- `SUMMER_CAMP_ACTIVITY_MAPPING` config not found → skip DIY enrollment gracefully
- Student removed from group mid-camp (partial completion, partial refund?)
- `addonMaterialIds` contains IDs outside range 43–65 (validation?)

## Async Jobs & Automation
- **`initiateCombinedPayment()` → payment callback:** Post-payment processing including diamond award, DIY enrollment, and onboarding email
- **`sendSummerCampOnboardingEmail()`:** Triggered post-payment; sends onboarding email to parent with internal CCs
