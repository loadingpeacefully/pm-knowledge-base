---
title: "Gamified Platform 03 – Curriculum Versioning System"
category: product-prd
subcategory: content-authoring-engine
source_id: eeee6cc8-5727-4692-9f40-d45d7087c3b5
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: unknown
created_at: 2026-04-06
source_notebook: NB5
---

# Gamified Platform 03: How the Adhyayan CMS Handles Versioning

## Overview

The Adhyayan CMS manages versioning for multiple course verticals through a hierarchical data structure that creates distinct versioning layers for Learning Paths, Modules, and individual scheduled Activities.

## 1. Learning Path & Module Versioning

The CMS versions entire curriculum structures, not just individual files.

### Version IDs
- Every Learning Path (e.g., `finance_L3_AI_demo_4`) is assigned a specific Version ID (e.g., Version 1, Version 2)

### Vertical-Specific Logic
- **Coding:** Only allows modules above version v4
- **Financial Literacy & Robotics:** Currently use a single version structure

### Cross-Version Mapping
- To ensure continuity during upgrades, modules are mapped across versions
- "Intro to Python" in v4 is mapped to its equivalent in v5 to maintain student progress tracking

## 2. The "Activity" Entity Integration

Versioning is tied directly to the scheduling engine via the `Activity` entity.

### Curriculum Version Attribute
- Every scheduled class (Activity) contains a `Curriculum Version` attribute
- Ensures that even if the global curriculum updates, a past class remains linked to the exact version taught at that time

### Data Hierarchy
```
Vertical → Curriculum Version → Class Type → Module → Topic
```

## 3. Automated Student Upgrades (Smart Migration)

When a new curriculum version is published, the system automatically handles version transitions.

### The "Zero-Lesson" Rule
- If a student has completed **0 lessons** in a module (Not Started) → **automatically upgraded** to the latest version
- If a student has completed **≥1 lesson** in a module → remains on original version for that module

### Benefits
- Prevents content discontinuity for active learners
- Ensures new enrollees always get the latest curriculum
- No manual teacher or ops intervention required

## 4. Teacher Visibility & Constraints

The system restricts teacher interactions with versions to prevent data corruption.

### Default to Latest
- When adding new modules via "Add More Modules" flow → system shows only the latest version (e.g., v5)
- No accidental assignment of outdated content

### No Manual Rollback
- Teachers can modify the **sequence** of modules
- Teachers cannot downgrade the **version** of an assigned module
- Protects curriculum integrity

## Why This Matters for Interviews

**Q: "How does your system handle multiple curriculum versions without breaking the student experience?"**

Answer: "We built a versioning system where version upgrades happen at the module level, not the course level. We use a 'Zero-Lesson Rule' — if a student hasn't started a module, they're automatically migrated to the latest version. If they're mid-module, they stay on the original version for continuity. This means thousands of students could be on different curriculum versions simultaneously, all correctly mapped to what they actually studied."

## Relevance Tags
- `adhyayan` `curriculum-versioning` `cms` `smart-migration` `brightchamps` `technical-architecture`
