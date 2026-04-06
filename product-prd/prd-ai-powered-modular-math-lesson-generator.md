---
title: "PRD AI-Powered Modular Math Lesson Generator for K-10"
category: product-prd
subcategory: content-tools
source_id: e8c7ec29-c3e7-49db-9f24-14cf192390e9
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# PRD AI-Powered Modular Math Lesson Generator for K-10

## Overview

An AI-powered system for educators to create structured, Common Core-aligned K-10 math lessons through a modular bot pipeline. Auto-generates projects, modules, learning objectives, and lesson plans; supports design and JSON development workflows with task state tracking.

## Problem Statement

Manual lesson creation for Grades K-10 requires 20 SMEs over 26 weeks at 1,800,000 INR for 1,200 lessons. Without automation, content quality is inconsistent across SMEs and timelines are at risk. The AI system reduces this to 4 reviewers at 600,000 INR — a 67% cost reduction.

## Goals & Success Metrics

- Generate all 1,200 lessons (Grades 1-10, 120/grade) within 26-week window
- Reduce lesson creation cost from 1,500 INR to 500 INR per lesson
- Achieve < 5% rejection rate in human review phase
- All lessons aligned to Common Core standards with zero omissions

## User Stories / Jobs-to-Be-Done

- As a curriculum developer, I want lesson structure auto-generated from curriculum data so I only need to review, not create
- As a teacher, I want to regenerate a specific section of a lesson if the AI content isn't clear enough
- As a designer, I want to be assigned visual tasks directly from the system (not by email/Slack)
- As a JSON developer, I want AI-generated content alongside my template to reduce manual effort
- As an admin, I want to track which lessons are in Draft, In Review, In Design, or Complete

## Feature Scope

**In Scope:**
- Auto-generation of Projects and Modules from curriculum database
- Detailed Learning Objective generation (brief + bullet points, editable)
- Lesson Plan generation: Title Slide, Concept Explanation, Guided Practice, Independent Practice, Review/Conclusion
- Task states: Draft → In Review → Ready for JSON → In Design → Complete
- JSON development interface with GPT-generated content alongside templates
- Designer assignment CTA with Figma link attachment
- PDF export of full lesson plan for offline review (Phase 2)
- Final review and publishing workflow

**Out of Scope:**
- Student-facing lesson delivery (lesson is content, not player)
- Non-math subjects in Phase 1
- Real-time student on-demand lesson generation (Phase 2)

## Key Design Decisions

- Lesson plan has 5 sections, each comprising multiple tasks — tasks are independently editable and regeneratable without affecting other tasks
- Design tasks are assigned from the system, not via external communication
- JSON development uses side-by-side view (template + GPT content) for developer efficiency
- Phase 2: bot-specific task assignments (Concept Bot, Practice Bot) and Figma-to-JSON automation

## Open Questions / Risks

- Who is the primary user (curriculum developer vs. teacher) — different access levels needed?
- Risk: LLM-generated content may require more revision than estimated (review velocity may drop below 15 lessons/week/SME)
- Dependency: Curriculum data must be cleanly structured in the database before auto-generation works
- Open: What happens to existing manually-created lessons? Migration or parallel system?
