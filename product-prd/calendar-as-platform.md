---
title: "Calendar as a Platform"
category: product-prd
subcategory: platform-infrastructure
source_id: 95947549-b91f-4797-8328-d477c8c6e8db
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Calendar as a Platform

## Overview

This document defines the strategic vision for treating the BrightCHAMPS scheduling calendar not as a feature, but as a **platform** — a central infrastructure layer that coordinates availability, booking, class delivery, and payments across all user types (students, teachers, and ops).

## Problem Statement

### Fragmentation Before Unification
- Multiple verticals (Coding, Robotics, FinLit, Schola) had independent scheduling systems
- Teachers managed availability in disconnected spreadsheets/forms
- Students couldn't see a unified class calendar across all enrolled courses
- Demo scheduling required 20 ops staff for manual reconciliation

## The "Calendar as Platform" Concept

### Core Idea
Treat the calendar as a **shared infrastructure service** that all product features consume — not a standalone view. Similar to how Google Calendar is a platform that other apps integrate with.

### Key Entities
1. **Time Slots** — atomic units of calendar availability (30-minute increments)
2. **Availability Rules** — repeat (LTA) vs. one-time teacher availability
3. **Booking Engine** — allocates students to available teacher slots
4. **Class Events** — the outcome of the booking engine (confirmed class with teacher + student + curriculum context)
5. **Conflict Resolution** — logic for handling overlapping bookings, cancellations, reschedules

### User-Specific Views
- **Student:** Upcoming classes calendar with lesson context (module, topic)
- **Teacher:** Weekly availability grid with booked classes, empty slots, and demo allocations
- **Ops/Admin:** Centralized monitoring of all ongoing and scheduled classes; alert system for no-shows and escalations

## Architecture Decisions

### Single Source of Truth
- All availability, booking, and class data lives in a unified MySQL database (with Redis caching for real-time reads)
- Deprecated: individual spreadsheets, per-vertical calendar tools

### Separation of Concerns
- **Availability marking** (teacher action) is decoupled from **booking** (platform action) and **class delivery** (Zoom/100ms action)
- Each layer can be modified independently without breaking others

### Time Zone Handling
- All times stored in UTC
- Display converted to user's local time zone
- Daylight savings accounted for using IANA timezone database (Moment.js on frontend)

## Key Flows

### Teacher Availability Flow
1. Teacher opens Calendar page
2. Selects "Mark Availability" — chooses Repeat or One-Time
3. For Repeat: selects day(s) of week + time range; saves → creates recurring LTA rule
4. For One-Time: navigates to specific week; selects specific date + time → creates one-time availability
5. Marked slots become eligible for demo and paid class booking

### Demo Booking Flow
1. Parent selects preferred demo time
2. Platform queries available teacher slots (matching subject, grade, region)
3. Booking Engine applies Teacher Prioritization Logic (RCVR/OCVR scores)
4. Demo confirmed; teacher and parent notified
5. First 10 demos use Demo Day Score for allocation; after 10 → DQS takes over

## Impact
- Ops staff reduced from ~20 → 3–4 for demo scheduling
- 100% user migration completed across all verticals
- Foundation for all subsequent scheduling features (group classes, summer camp, self-paced)

## Relevance Tags
- `calendar-platform` `scheduling` `infrastructure` `teacher-availability` `unified-migration` `brightchamps`
