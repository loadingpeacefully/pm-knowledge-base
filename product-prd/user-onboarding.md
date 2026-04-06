---
title: "User Onboarding"
category: product-prd
subcategory: learner-experience
source_id: 17dcf65b-f496-46a0-8cfd-99454137dc19
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# User Onboarding

## Overview

Onboarding flow for first-time users on the unified paid student dashboard. Allows users to input personal information, address details, and select their preferred course start date before accessing the main dashboard.

## Problem Statement

The unified paid student dashboard lacked the ability to collect personal information from first-time users. Upon initial login, users were immediately prompted to schedule classes — bypassing profile setup. This abrupt progression disrupted the onboarding experience and left incomplete student profiles.

## Goals & Success Metrics

- Achieve 90% onboarding completion rate within 48 hours of first login
- Reduce incomplete profile records by 80%
- Improve first-class show-up rate by ensuring students have scheduled classes through onboarding
- Reduce ops effort to manually collect student details post-enrollment

## User Stories / Jobs-to-Be-Done

- As a new student (parent), I want to enter my child's details easily on first login so the platform knows who I am
- As a parent, I want to choose when my child's classes start so I can plan around our schedule
- As a student, I want to be guided step-by-step rather than faced with an empty dashboard
- As a teacher, I want accurate student profile information before the first class

## Feature Scope

**In Scope:**
- Step 1 — Personal Information: name, email, phone number
- Step 2 — Address Details: residential address, school name (compulsory for all users)
- Step 3 — Class Scheduling: preferred course start date, time slot selection
- State persistence: onboarding progress saved so users can resume if they drop off
- Post-completion: first class scheduled automatically, welcome message dispatched

**Out of Scope:**
- Social login during onboarding (handled at authentication layer)
- Profile photo upload (V2)
- Multi-course onboarding (one course at a time in V1)

## Key Design Decisions

- Onboarding is mandatory — users cannot access the main dashboard until all 3 steps are complete
- Address details are compulsory for all users (not optional)
- Class scheduling in Step 3 uses available teacher slots (not open date picker)
- Resume capability: if user exits mid-onboarding, they return to the correct step on next login
- Welcome message (WhatsApp + email) dispatched within 5 minutes of onboarding completion

## Open Questions / Risks

- Should known fields from CRM/lead record be auto-filled to reduce friction?
- Risk: Mandatory address collection may cause drop-off for privacy-conscious parents
- Dependency: Teacher availability service must expose reliable slots for Step 3 scheduling
- Open: What happens if no teacher slots are available during onboarding Step 3?
