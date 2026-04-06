---
title: "PRD All-in-One Summer Camp 2025 Course Detail & Scheduling"
category: product-prd
subcategory: summer-camp
source_id: 5988a16a-faf5-4269-b775-9199d4d84651
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
prd_scope: course-detail
source_notebook: NB5
---

# PRD All-in-One Summer Camp 2025 Course Detail & Scheduling

## Overview

Product requirements for the Summer Camp 2025 course detail page and scheduling flow. Covers course presentation, slot selection, checkout, and enrollment confirmation for the all-in-one Summer Camp package.

## Problem Statement

Summer Camp 2025 is a multi-course package sold to parents for their children's summer holidays. The existing course detail and scheduling pages are not optimized for this package format — they lack bundle visualization, flexible scheduling, and IP-based pricing.

## Goals & Success Metrics

- Achieve Summer Camp 2025 enrollment targets (specific numbers in campaign brief)
- Reduce checkout abandonment by 20% vs. previous year
- Increase self-serve scheduling completion rate to 80%
- Improve page-to-purchase conversion rate

## User Stories / Jobs-to-Be-Done

- As a parent, I want to see all courses included in the Summer Camp package on one page
- As a parent, I want to select preferred class times for my child during the summer
- As a parent, I want to complete checkout without needing to call sales
- As a student, I want to see the summer camp schedule and know what to expect each day

## Feature Scope

**In Scope:**
- Summer Camp course detail page (bundle overview, courses included, schedule format)
- Slot selection interface (date, time, batch selection)
- IP-based pricing and checkout (Razorpay for India, Stripe for international)
- Enrollment confirmation with full schedule summary
- Mobile-optimized checkout flow

**Out of Scope:**
- In-class experience for Summer Camp (covered by separate team)
- Post-camp certificate (covered by certificate service)
- Referral/discount codes (marketing team scope)

## Key Design Decisions

- IP-based checkout config: country detection server-side, with user override option
- Scheduling uses available batch slots (not individual teacher selection)
- Bundle price shown prominently with per-course breakdown for transparency
- Enrollment confirmation sent via WhatsApp and email within 5 minutes

## Open Questions / Risks

- How many batch slots will be available per city/timezone at launch?
- Risk: Slot capacity constraints may cause checkout frustration if shown too late
- Dependency: IP geolocation service must be reliable for international users
- Open: Should Summer Camp certificate be different from standard course certificate?
