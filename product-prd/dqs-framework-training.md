---
title: "DQS (Demo Quality Score) Framework Training"
category: product-prd
subcategory: teacher-quality
source_id: 7931e129-abca-4b40-8260-50b97a01a822
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# DQS Framework Training

## Overview

The Demo Quality Score (DQS) is BrightCHAMPS' proprietary teacher evaluation framework for assessing the quality of demo classes. It is used to rank and allocate teachers for demo class assignments, ensuring high-converting teachers receive more high-intent student leads.

## Problem Context

### Why DQS Was Built
- Default demo allocation was random or chronological — teachers were not differentiated by performance
- New teachers suffered low demo volume (reducing their conversion ramp-up)
- High-performing teachers were not systematically prioritized for high-value leads
- Manual evaluation was inconsistent and not scalable

## DQS Framework Architecture

### Scoring Dimensions
The DQS evaluates teachers on the following criteria during a demo class:

| Dimension | Description | Weight |
|-----------|-------------|--------|
| **Agenda Sharing** | Did the teacher share a clear class agenda at the start? | High |
| **Recap** | Did the teacher summarize key points at the end? | High |
| **Student Engagement** | Did the student participate actively throughout? | High |
| **Communication Clarity** | Was the explanation clear and age-appropriate? | Medium |
| **Pacing** | Was the class too fast, too slow, or well-paced? | Medium |
| **Energy Level** | Was the teacher's energy appropriate and engaging? | Medium |
| **Rapport** | Did the teacher build a positive relationship with the student? | Medium |
| **Problem Solving** | Did the teacher handle unexpected questions or issues gracefully? | Low |

### Score Calculation
- Each dimension scored 0–5 by a human reviewer (or AI-assisted detection system)
- DQS = weighted average across all dimensions (0–20 scale)
- Scores update after each demo; rolling average with recency weighting

### AI-Assisted Evaluation
- System detects specific behavioral cues from class recordings (Agenda Sharing, Recap events)
- Reduces reviewer burden while maintaining consistency
- Human override available for edge cases

## Demo Allocation Logic

### Standard Allocation
- Teachers ranked by DQS score within their subject/region/availability pool
- Higher DQS → more demo allocations
- Prevents gaming: score recalculates after each demo (not a one-time assessment)

### New Teacher Rule
- For the first 10 demos: use **Demo Day Score** (from the hiring evaluation) instead of DQS
- After 10 demos: transition to actual DQS based on real demo performance
- Rationale: new teachers haven't built an actual DQS track record; Demo Day Score is the best available proxy

### Regional Allocation
- Separate allocation pools for different regions (US/ROW/Vietnam)
- RCVR (Region Conversion Rate) and OCVR (Overall Conversion Rate) feed into teacher scoring
- Teachers with high conversion rates in specific regions get prioritized for those regions

## Training Program Structure

### Why Training is Necessary
- DQS dimensions are abstract — teachers need behavioral examples of what "5" vs "2" looks like
- Training builds teacher self-awareness and consistent delivery standards

### Training Modules
1. **Understanding the DQS Framework** — why it exists, how scores are calculated
2. **Behavioral Examples** — video walkthroughs of high/low scoring demo behaviors
3. **Agenda Sharing Workshop** — specific scripts and formats for opening a demo class
4. **Engagement Techniques** — interactive methods for keeping students active
5. **Mock Demo with Scoring** — practice demo with real-time feedback from trainer

## Integration with Hiring Pipeline
- DQS framework is introduced during the training phase (post-hire)
- Demo Day Score (used during hiring) is calibrated against the DQS scale for consistency
- Readiness decision at end of training incorporates predicted DQS based on mock demo performance

## Impact
- More predictable conversion rates due to quality-based allocation
- New teachers ramp up faster with Demo Day Score protection
- Ops team gains structured data for teacher coaching interventions

## Relevance Tags
- `dqs` `demo-quality-score` `teacher-evaluation` `hiring-pipeline` `teacher-training` `brightchamps`
