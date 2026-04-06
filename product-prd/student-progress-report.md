---
title: "Student Progress Report"
category: product-prd
subcategory: learner-experience
source_id: dcacfc9d-8235-49aa-b50d-e407a057ef6a
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Student Progress Report

## Overview

Automated progress report generated for students every 10 unique lessons completed. Delivered to parents via WhatsApp and email as a PDF. Designed to provide transparent, tangible evidence of learning progress to parents and support renewal conversations.

## Problem Statement

50% of parents surveyed want a progress report against the original curriculum. Currently there is no way for parents to track their child's learning progress. URI (renewal) team frequently requests progress summaries before conversion calls. Without a structured report, renewal conversations rely on anecdotal teacher feedback.

## Goals & Success Metrics

- Increase URI conversion rate by 10% for students with progress reports
- Increase NPS by 10 points among parents who receive progress reports
- Achieve 80% delivery success rate for generated reports
- Generate at least 1 report per student within first 60 days of enrollment

## User Stories / Jobs-to-Be-Done

- As a parent, I want a formal report showing what my child has learned in the last 10 classes
- As a parent, I want to see my child's quiz scores and teacher ratings in one place
- As a teacher, I want the progress report to include my feedback so parents understand my perspective
- As a student, I want to see which projects I completed and what skills I gained
- As the URI team, I want the progress report to be available before every renewal call

## Feature Scope

**In Scope:**
- Auto-generation trigger: every 10 unique lessons marked "Covered all concepts" by teacher
- Report sections: Header, Student Details, Academy Performance (knowledge curve, academic score, instructor rating), Course Progress (pie chart), Topics Covered (10 lessons), Assignments/Projects Completed, Academic Excellence Team Review (strengths, weaknesses, teacher feedback), Footer
- Performance scoring: Academic score (assignments + quizzes + assessments), Instructor rating (normalized from teacher feedback), Knowledge curve (benchmarked vs. peers)
- Delivery: WhatsApp + email at 10 AM student local time on next day after 10th lesson
- PDF format with BrightCHAMPS logo and STEM Accredited logo
- PTM integration: CTA in PTM joining cues links to latest progress report

**Out of Scope:**
- Separate progress reports per subject for multi-course students (V1: per course only)
- In-app progress report view (V1: PDF delivery only)
- Financial Literacy project URLs (no project URL sharing in FinLit)

## Key Design Decisions

- Report scheduling is decoupled from PTM frequency — triggered by lesson completion, not class count
- Knowledge curve shows student position relative to peers: Bottom 5% artificially moved to 2-5 bracket; Below Average (2-5) not shown to student
- Strengths/weaknesses: max 4 each; if no weaknesses, bottom 2 strengths converted to weakness unless score ≥ 80%
- Teacher feedback field: minimum 300 characters, mandatory for progress report generation

## Open Questions / Risks

- What if teacher feedback is not submitted for 1 or more of the 10 lessons — does report wait or generate without it?
- Risk: Multiple teachers in a 10-lesson window — report shows only latest teacher
- Dependency: Teacher must submit feedback with "Covered all concepts" lesson status for trigger
- Open: Legal sign-off on using teacher signatures in reports
