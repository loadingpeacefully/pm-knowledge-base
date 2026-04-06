---
title: Teacher Onboarding
category: technical-architecture
subcategory: teacher-management
source_id: 0aa7b462
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Teacher Onboarding

## Overview
The Teacher Onboarding system manages the full lifecycle of teacher applications, from initial submission through shortlisting and final onboarding into the platform. It provides a rich database schema spanning application profile, financial details, eligibility, and skill mappings, with an admin dashboard (Prashashak) for managing the onboarding pipeline.

## API Contract
N/A — The source documentation covers database schema and frontend admin routes. Specific backend API endpoints, request/response schemas, and service layer logic are not documented in the available sources.

## Logic Flow

### Controller Layer
Admin dashboard routes (Prashashak):
- `/teacher-onboarding/active-applications` → `TeacherOnboarding.tsx` (300KB dynamic bundle)
- `/teacher-onboarding/shorlisted-teachers` → `TeacherOnboardingListing.tsx`
- `/teacher-onboarding/details` → `TeacherOnboardingDetails.tsx`

### Service/Facade Layer
N/A — Not documented in source.

### High-Level Design (HLD)
- Application pipeline: submission → review → shortlisting → onboarding
- Financial and banking details stored per country-specific requirements (India: PAN/Aadhaar; Indonesia: KTP/NPWP; international: IBAN/Swift)
- Once onboarded, teacher data migrates to core teacher tables (`teachers`, `teacher_profile`, `teacher_eligibility`, etc.)

## External Integrations
N/A — Not documented in source.

## Internal Service Dependencies
- Dronacharya (Teacher Service): Core teacher tables (`teachers`, `teacher_profile`, `teacher_eligibility`) receive data post-onboarding
- Prashashak (Admin Dashboard): Frontend for managing onboarding pipeline

## Database Operations

### Tables Accessed

**Application-Phase Tables:**

**`teacher_applications`:**
| Column |
|--------|
| id, name, phone, email, dob, status, gender, country_id, source, reviewed_by, brightchamps_email, email_password, hr, hr_status, hiring_manager, demo_manager |

**`teacher_application_profile`:**
| Column |
|--------|
| id, application_id, qualification, university, previous_company, experience, hours_committed, signature_image, photo, resume, degree_certificate, address_permanent, address_current, intro |

**`teacher_application_financial_details`:**
| Column |
|--------|
| id, application_id, bank_account_number, account_holder_name, bank_name, bank_address, bank_country_id, ifsc_code, swift_code, pan_number, ktp_number, npwp_tax_id, tax_id, aadhaar_number, taxation_image, identity_proof_image, tax_id_international_image, salary_disbursment, salary_disbursment_image, ktp_id_image, tax_id_image, aadhaar_card, pan_card, taxation, identity_proof_number, transit_number, iban, iban_paypal_id, paypal_email, local_id |

**`teacher_application_courses`:** `id, application_id, course_id`

**`teacher_application_countries`:** `id, application_id, country_id`

**`teacher_application_grades`:** `id, application_id, grade (1-12)`

**`teacher_application_skills`:** `id, application_id, skill_id`

**`teacher_application_languages`:** `id, application_id, language_id`

**Post-Onboarding Core Tables:**

**`teachers`** and **`teacher_profile`:** Core teacher identity and active profile

**`teacher_eligibility`:** `teacher_id, country_id, grade, course, duration`

**`teacher_languages`** and **`teacher_skills`:** Languages and hard/soft skill categorizations

**`teacher_roles`:** User system roles (teacher, team_lead)

**`teacher_mapped_vertical`:** `teacher_id, vertical_id`

**`teacher_specializations`** and **`teacher_certifications`:** Additional qualifications

**`teacher_metrics`:** Performance metrics on the platform

### SQL / ORM Queries
N/A — Not documented in source.

### Transactions
N/A — Not documented in source.

## Performance Analysis

### Good Practices
- Financial details are stored in a dedicated table with country-specific fields, allowing clean extensibility per region
- Skills separated into hard and soft categories via `teacher_skills`

### Performance Concerns
- `TeacherOnboarding.tsx` admin bundle is documented as 300KB — heavy initial load for the admin dashboard page

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | No API endpoints documented — all interaction appears to be via admin dashboard UI with no documented backend contract |
| Low | Large frontend bundle (300KB) for active applications page may degrade admin UX on slow connections |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Document and formalize the backend API contract for the onboarding pipeline
- Lazy-load the `TeacherOnboarding.tsx` admin bundle to reduce initial page load

### Month 1 (Architectural)
- Add an automated state machine for application status transitions (submitted → reviewed → shortlisted → onboarded)
- Implement webhook notifications to HR when application status changes

## Test Scenarios

### Functional Tests
- Submit new teacher application with all required fields
- Verify financial details are stored correctly for different country types (India, Indonesia, International)
- View shortlisted teachers in admin dashboard
- Transition application to onboarded state and verify core teacher tables are populated

### Performance & Security Tests
- Verify sensitive financial data (bank account, PAN, Aadhaar) is not exposed in API responses to unauthorized roles
- Test 300KB bundle load time on throttled connections

### Edge Cases
- Application submitted with missing financial details for required country (e.g., no PAN for India)
- Duplicate email/phone in application submission

## Async Jobs & Automation
N/A — Not documented in source.
