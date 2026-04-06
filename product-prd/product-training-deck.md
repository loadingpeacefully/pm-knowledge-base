---
title: "Product Training Deck"
category: product-prd
subcategory: onboarding-training
source_id: 24b95bff-48f6-4443-be8c-716b2e119ba7
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Product Training Deck

## Overview

BrightCHAMPS internal product training deck — a comprehensive onboarding resource for new team members (product, engineering, sales, ops) to understand the platform's core product architecture, key workflows, and strategic context.

## Purpose

### Who This Deck Is For
- New product managers joining the team
- Engineering leads onboarding to a specific product area
- Sales and ops staff who need to understand what the platform does
- Teachers during the onboarding training program

### What This Deck Covers
- Platform overview and current product portfolio
- User journeys for each persona (Student, Teacher, Admin)
- Key product metrics and success criteria
- How the different platform components connect

## Platform Overview

### The BrightCHAMPS Platform Architecture

```
STUDENT EXPERIENCE
├── Student Dashboard (unified, post-migration)
│   ├── Live Class (Zoom integration)
│   ├── Adhyayan: Gamified Learning Modules
│   ├── Quiz Galaxy (post-class assessments)
│   ├── Nano Skills Marketplace
│   └── Numon: Practice Zone (math worksheets)

TEACHER EXPERIENCE
├── Teacher Dashboard
│   ├── Teacher Availability Calendar (Repeat + One-Time LTA)
│   ├── Demo & Paid Class Calendar
│   ├── Class Joining + Booklet Access
│   ├── Salary Dashboard (credits + payslips)
│   └── Issue Reporting (live escalation to ops)

ADMIN / OPS EXPERIENCE
├── Admin Dashboard
│   ├── Demo Ops (centralized monitoring + alerts)
│   ├── Teacher Management (DQS, allocation, performance)
│   ├── Student Management (enrollments, diamond balances)
│   └── Content Management (Adhyayan CMS)
```

## Key User Journeys

### Student: From Demo to Paid
1. Parent books demo via website
2. Student joins Demo Joining Page (system check + pre-demo game)
3. Teacher delivers 30-min demo class
4. Parent receives follow-up from sales
5. Parent pays → student account upgraded to Paid
6. Student accesses Adhyayan platform for live classes
7. Post-class: Quiz Galaxy unlocked
8. Diamonds earned → Nano Skills marketplace accessible

### Teacher: From Application to First Demo
1. Teacher applies via web form
2. Assignment (Zipcar case) → hiring evaluation
3. Demo Day → DQS recorded
4. Training batch (Day 1–4 live sessions + DIY LMS modules)
5. Mock demo → readiness assessment
6. Added to teacher pool
7. First 10 demos: allocated based on Demo Day Score
8. After 10 demos: DQS governs allocation

### Admin/Ops: Daily Demo Operations
1. Morning: check pending demo schedule + no-show alerts
2. Real-time monitoring: teacher join status, student join status
3. Escalation alerts: trigger replacement teacher if needed
4. Post-demo: mark outcomes (demo given, no-show, rescheduled)
5. End of day: conversion data update

## Key Product Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Demo conversion rate | ≥15% | % of demos that convert to paid subscriptions |
| Quiz completion rate | ≥85% | % of unlocked quizzes completed by students |
| Module rating | ≥4.5/5 | Student rating for each gamified learning module |
| Teacher DQS | ≥14/20 | Average demo quality score across teacher pool |
| Ops efficiency | ≤3 staff for demo ops | Headcount required for centralized demo monitoring |

## Common Onboarding Questions

**Q: Why did we build our own CMS instead of using a third-party tool?**
A: The gamified template engine requires a custom JSON schema that no off-the-shelf CMS supports. The Adhyayan CMS was built to allow non-technical content teams to author JSON configurations with real-time preview.

**Q: How does the Diamond economy work?**
A: Diamonds are earned by students through platform engagement (class attendance, quiz completion, referrals). They can be spent on Nano Skills courses or purchased directly. This creates a closed-loop engagement/monetization system.

**Q: What is the DQS and why does it matter?**
A: DQS (Demo Quality Score) is how we ensure quality teacher allocation. It measures teacher performance across 8 dimensions during a demo class. Higher DQS → more demo allocations → better outcomes for both teacher earnings and company revenue.

## Relevance Tags
- `training-deck` `product-overview` `onboarding` `platform-architecture` `brightchamps` `user-journeys`
