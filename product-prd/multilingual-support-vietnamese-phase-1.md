---
title: "Multilingual Support Vietnamese Phase 1"
category: product-prd
subcategory: localization
source_id: bb498177-532e-482e-9e3c-04bd328e8cba
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Multilingual Support Vietnamese Phase 1

## Overview

Phase 1 of multilingual support adds Vietnamese language localization to the student dashboard and Nano Skills catalog. Vietnamese students represent a high-diamond-balance, high-intent segment that is currently underserved by English-only content.

## Problem Statement

Vietnamese students hold ~70% of total diamond balances across the platform but are shown English-language Nano Skills by default. The lack of Vietnamese UI and course surfacing leads to low discovery and conversion for this segment.

## Goals & Success Metrics

- Increase Nano Skills enrollment for Vietnamese-locale students by 30%
- Increase diamond consumption among Vietnamese students (target: contribute ≥ 20% of monthly Nano Skills diamond consumption)
- Reduce support tickets related to language confusion from Vietnamese users

## User Stories / Jobs-to-Be-Done

- As a Vietnamese student, I want to see the dashboard and courses in my language
- As a Vietnamese parent, I want course descriptions and communications in Vietnamese
- As a student in Vietnam, I want to find Vietnamese-language courses first on the Nano Skills page
- As a Vietnamese student, I want quiz and homework instructions in Vietnamese

## Feature Scope

**In Scope:**
- Dashboard UI strings in Vietnamese (student dashboard, Nano Skills page)
- Vietnamese language tray on Nano Skills homepage for Vietnamese-locale users
- Vietnamese-translated course cards and descriptions
- Email and WhatsApp notifications in Vietnamese for Vietnamese-locale users
- Language preference setting in user profile

**Out of Scope:**
- Teacher-facing UI in Vietnamese
- Real-time translation of teacher speech during classes
- Vietnamese localization for FinLit content (Phase 2)

## Key Design Decisions

- Locale detection uses system language, with manual override in profile settings
- Vietnamese tray shows top 5 enrolled English courses that have Vietnamese translation
- Courses without Vietnamese translation fall back to English with a language tag
- No machine translation — all translations are human-reviewed

## Open Questions / Risks

- Who maintains Vietnamese translations as new UI strings are added?
- Risk: Inconsistent tone/quality if translations are done by multiple vendors
- Dependency: CMS must support multi-locale content entries per course
