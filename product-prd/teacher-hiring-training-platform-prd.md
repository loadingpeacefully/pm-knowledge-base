---
title: "Hiring + Training System (Current → Future State)"
category: product-prd
subcategory: teacher-supply-chain
source_id: d2ce96c0-b530-459d-a459-38d3cd5f4c9f
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Hiring + Training System: Current → Future State

## Overview

Comprehensive documentation of BrightCHAMPS' teacher hiring and training pipeline — mapping the current fragmented state (Google Sheets/Forms) to a future unified admin platform. Covers all stages from application intake to teacher deployment.

## 1. Overall Pipeline

Every teacher moves through three stages:

```
HIRING
├── Application Intake
├── Assignment (Zipcar Case)
├── Demo Day Booking
├── Demo Evaluation
└── Hiring Decision

TRAINING
├── Batch Creation
├── DIY Training (LMS)
├── Live Sessions (Day 1 → Day 4)
├── Task Evaluations
├── Mock Demo
└── Final Readiness Decision

DEPLOYMENT
├── Add to Teacher Pool
└── Demo Allocation Engine
```

## 2. Current Problems

### Operational Fragmentation
- Data lives across Google Sheets, Google Forms, WhatsApp groups, and ad-hoc trackers
- No unified system to track a candidate's full journey

### Manual Dependency
- Team manually copies names, emails, scores from Sheet → Sheet
- Manual batch creation, notifications, progress checks

### Zero State Visibility
- No single view: "Where is this candidate right now?"
- Trainers cannot see full history of stages

### Evaluation Layer Scattered
- Assignment score: Google Sheet
- Demo Day score: Separate sheet
- Daily training submissions: Google Forms
- Mock demo score: Another separate sheet
- No syncing between these systems

### Quality Leakage
- Demo allocation uses default DQS instead of Demo Day Score for new teachers → penalizes new teachers with limited demos

## 3. Core Actors

1. Candidate
2. Hiring Reviewer (assignment evaluator)
3. Demo Reviewer
4. Training Manager
5. Trainer (Day 1–4 sessions)
6. Ops Team
7. System / Automation
8. Teacher Allocation Engine

## 4. End-to-End Stages

### A. Hiring Stages

**1. Application Intake**
- Basic profile, experience, education, preferred subject, availability
- Stored in Applicant Table

**2. Assessment (Zipcar Task)**
- Written assignment / product case submitted via form
- Reviewer scores: Structure, Clarity, Product Thinking, Writing Quality
- Output: Pass/Fail + Score

**3. Demo Day Booking**
- Candidate selects slot; joins live demo with reviewer

**4. Demo Evaluation**
- Scored on: Communication, Student Handling, Clarity, Pacing, Energy, Class Structure, Rapport
- Output: Demo Day Score (0–20), Comments, Pass/Fail

**5. Hiring Decision**
- Assignment PASS + Demo PASS → Move to Training
- Any Fail → Reject

### B. Training Stages

**1. Batch Creation** — currently manual

**2. DIY Training**
- LMS access: recorded modules, quizzes, task submissions

**3. Live Training (Day 1 → Day 4)**
- Trainer covers: Soft skills, System overview, Lesson flow, Evaluation rubric

**4. Task Evaluations**
- Submitted via Google Form; reviewed via sheets by trainer

**5. Mock Demo**
- Scored on: Lesson flow, Problem-solving, Communication, Classroom management

**6. Final Readiness**
- Training manager consolidates all data → decides: Ready / Not Ready / Retraining

### C. Deployment

**1. Add to Teacher Pool**
- Create teacher profile, eligibility flags, time slots, onboarding docs

**2. Demo Allocation**
- First 10 demos: use Demo Day Score directly
- After 10 demos: DQS takes over
- Ops can: add demo credits, trigger reactivation, override flags

## 5. Future State: 3-Page Admin Platform

### Page 1: Hiring Pipeline
- View all candidates with current stage, assignment score, demo score
- Move to next stage or reject
- Auto-push to Training when hired
- Automated: demo booking, evaluation submission, status updates

### Page 2: Batch Creation & Training Management
- Create batches (Name, Dates, Trainer, Subject)
- Track attendance, DIY progress, task submissions
- Trainer evaluations + mock demo scheduling
- One timeline per candidate

### Page 3: Training Tracker
- Per candidate: DIY %, task status, trainer scores, mock demo, attendance
- System actions: auto-mark "Training Completed", auto-transfer to Teacher Pool

## 6. Evaluation Layer Mapping

| Stage | Currently In | Data Type |
|-------|-------------|-----------|
| Assignment | Google Form + Sheet | Score, rubric |
| Demo Day | Sheet | Score, clips, notes |
| DIY quizzes | Form | MCQ results |
| Daily tasks | Google Drive + Sheet | File links |
| Trainer evaluations | Sheet | Scores |
| Mock demo | Separate sheet | Score, reviewer |
| Readiness decision | Consolidated sheet | Final Pass/Fail |

## Relevance Tags
- `teacher-hiring` `teacher-training` `dqs` `admin-platform` `supply-chain` `brightchamps` `product-prd`
