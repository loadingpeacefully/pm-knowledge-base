---
title: "Teacher Availability – Unified Dashboard Experience"
category: product-prd
subcategory: teacher-dashboard
source_id: 4942fe93-6c7b-478f-976a-bc104eca720c
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Teacher Availability – Unified Dashboard Experience

## Problem Statement

Teachers currently mark one-time and repeat availability (LTA – Long-Term Availability) on two **separate pages**, resulting in:
- Inconsistency and confusion in the scheduling experience
- Different steps and mental models for LTA vs. one-time marking
- Scheduling conflicts and teacher/student cancellations
- Calendar view lacking lesson/module context (teachers can't plan ahead without drilling into each class)

## Solution Overview

A **unified class scheduling experience** serving as a one-stop solution for teachers to mark both repeat and one-time availability from a single calendar view. Both demo and paid class bookings can occur within any marked availability slot.

## Key Design Principles

1. **Single Calendar View** — no separate pages for LTA vs. one-time
2. **Repeat and One-Time from Same Interface** — dropdown triggers the correct editing mode
3. **Lesson Context in Calendar** — show module name/topic within each booked class slot
4. **Timezone Accuracy** — all times stored in UTC; displayed in teacher's local timezone with DST support
5. **Slot State Clarity** — 3 clear visual states: Open, Booked (Demo), Booked (Paid)

## Availability Types

### Repeat Availability (LTA)
- Teacher selects day(s) of week + time range
- These slots recur weekly until modified
- Paid classes are ONLY scheduled in Repeat Availability slots
- Demo classes can be scheduled in both Repeat and One-Time slots

### One-Time Availability
- Teacher selects specific date(s) + time range for the current or next week only
- Maximum selection: [Current Week] + 1 week ahead
- All existing Repeat slots shown in "read mode" to prevent accidental overlap

## UI/UX Design

### Calendar Page Layout
- **A:** Class Schedule page header
- **B:** Hello {{Teacher Name}} greeting
- **C:** Week Navigation (default: current week)
- **D:** Mark Availability Dropdown (Repeat / One-Time)
- **Sidebar:** 2 states — Collapsed (default) and Expanded

### Time Slot Interactions
- 30-minute intervals (2 clicks to select 60 minutes)
- 3 slot states during editing:
  1. **Default:** "Click here to book slot" (empty)
  2. **Hover:** Checkbox appears for selection
  3. **Selected:** Visual fill color to confirm selection
- Teachers can deselect by clicking a marked slot
- Calendar is vertically scrollable to access all time slots

### Save Actions
- **Repeat Availability:** "Save Changes" button → toast message: "Repeat class scheduled successfully"
- **One-Time Availability:** "Save" button → toast message: "One-Time class scheduled successfully"
- After saving, calendar updates immediately to reflect marked slots

## Time Zone Handling

### Architecture
- All availability stored in **UTC** to ensure consistent cross-timezone operations
- Display layer converts UTC to teacher's local timezone using IANA timezone database
- Student-facing scheduling converts teacher availability to student's local timezone

### DST (Daylight Savings Time) Logic
- Spring Forward: Add 1 hour to stored UTC time for display
- Fall Back: Subtract 1 hour from stored UTC time for display
- System uses Moment.js `moment.tz()` for automatic DST adjustment by timezone

### Example
- Teacher in Sydney marks 9:00 AM AEST
- Stored as: 23:00 UTC (previous day)
- Student in Mumbai sees: 4:30 AM IST
- Student in San Francisco sees: 4:00 PM PST

## Edge Cases

### Overlapping Availability
- System prevents double-booking the same slot
- If Repeat and One-Time attempt to overlap: Repeat slot takes precedence; system warns teacher

### Demo During Paid Class Time
- If a demo is scheduled at 4:00 PM and a student tries to book a paid class at 1:30 PM in the same Repeat slot: the slot shows as available for the student (different times don't conflict)

### Class Already Scheduled
- Slots with booked demo or paid classes show as non-editable
- Visual color coding: Repeat (blue), Demo booked (orange), Paid booked (green)

### Recurring Availability Exceptions
- If a paid class is scheduled during a to-be-cancelled repeat slot: the paid class moves to the next matched repeat slot for that student

## Minimum Availability Requirement
- Current standard: 20–25 hours per week
- For Offline/Innovation Hubs: requirement suspended (pending traffic clarity)

## Communication Templates
- Demo booking confirmation: email_format_58.html
- Paid class conversion notification: email_format_20.html

## Relevance Tags
- `teacher-availability` `calendar` `scheduling` `lta` `timezone` `unified-dashboard` `brightchamps` `product-prd`
