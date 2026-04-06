---
title: PQS Architecture & Project Document
category: product-prd
subcategory: student-lifecycle
source_id: d9b85014-7ea3-4b5c-bbc1-64bf076bdee6
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# PQS Architecture & Project Document

## Overview

The Platform Quality Score (PQS) is a deterministic, automated intelligence engine built to transform raw class transcripts into structured pedagogical quality data and parent-facing post-class reports. Where educational quality assurance has historically been manual, subjective, and trapped within backend operational silos, PQS replaces that process with a fully automated pipeline that ingests transcripts, evaluates them against a 10-point pedagogical rubric, and produces a structured JSON "Forensic Ledger" that drives rich, interactive frontend reports for parents.

The PQS architecture is organized into three decoupled layers: Ingestion (transcript capture and language detection), The Engine (rubric evaluation and forensic ledger generation), and Output / Narrative Generation (rendering the parent-facing `post_class_feedback.html` report). The frontend report surface includes three key modules: Class Energy (voice ratio of teacher vs. student talk time), The Learning Journey (a minute-by-minute visual timeline of Concept Depth vs. Student Expression), and Actionable Next Steps (context-aware prompts for parents to reinforce learning at home).

As of the document date, PQS processes 70% of all One-to-One (OTO) platform volume and generates accurate quality scores for 91% of all completed paid classes within enabled courses. The system's stated business goal is to use backend QA data as a retention engine — making the quality of every class visible and tangible to parents, thereby increasing their confidence in the platform and their likelihood to continue enrollment.

## Problem Statement

Educational quality assurance at BrightCHAMPS was manual, subjective, and siloed in backend operations. There was no scalable mechanism to evaluate whether each class met pedagogical standards, and no way for parents to understand the quality of the learning experience their child received. This created a retention risk: parents who did not perceive tangible learning progress were more likely to churn. PQS solves this by automating quality scoring at scale and surfacing the results directly to parents as a premium post-class experience, transforming quality assurance from an internal audit function into a parent-facing retention product.

## User Stories

- As a parent, I want to view a visual timeline of my child's Learning Journey after each class, so that I can see the progression of Concept Depth and my child's active participation throughout the session.
- As a parent, I want to receive context-aware Actionable Next Steps (e.g., "Ask Jason to explain the difference between CeFi and DeFi"), so that I can reinforce learning at home between classes.
- As a parent, I want to see the Class Energy voice ratio (e.g., "94% Teacher / 6% Student"), so that I understand how much my child participated versus how much the teacher was speaking.
- As a QA administrator, I want the system to automatically map each class transcript against a 10-point pedagogical rubric, so that quality assurance is deterministic and consistent rather than subject to individual reviewer bias.
- As a system operator, I want classes with less than 75% English content to be flagged and routed out of the primary pipeline, so that the quality scores are based only on evaluable content and the integrity of the scoring data is protected.

## Feature Scope

### In Scope

- Transcript ingestion from Zoom (using native platform language flags) and Google Meet (via audio-transcript analysis pipeline)
- Language detection and enforcement of a >75% English threshold for primary pipeline ingestion
- 10-point pedagogical rubric evaluation engine
- PQS Forensic Ledger: a structured, chronological JSON array mapping pedagogical micro-events to timestamps
- Forensic Ledger fields: event type tags (e.g., `HOMEWORK_CHECK`, `EXPLANATION`), speaker role identification, exact evidence quotes, and mathematical score justification
- Parent-facing `post_class_feedback.html` post-class report UI with three modules:
  - Class Energy (Voice Ratios: Teacher talk time % vs. Student talk time %)
  - The Learning Journey (minute-by-minute visual timeline: Concept Depth vs. Student Expression)
  - Actionable Next Steps (context-aware prompts for parent reinforcement at home)
- Dynamic and responsive parent report UI
- Multi-lingual rollout roadmap for non-English session processing (future phase)

### Out of Scope

- Teacher-facing evaluation reports (current scope is parent-facing only)
- Group class (non-OTO) processing (current focus is One-to-One classes)
- Real-time in-class scoring (evaluation is post-class only)
- Non-English session processing in the current phase (flagged and routed out; multi-lingual pipeline is a future blocker)
- Google Meet audio-analysis pipeline (technical strategy and cost architecture still being finalized at document time)

## Functional Requirements

1. **Transcript Ingestion**
   - The system must ingest raw class transcripts from Zoom and Google Meet after each class.
   - For Zoom: use native platform language flags to identify the instruction language.
   - For Google Meet: route the session through an audio-transcript analysis pipeline to identify the instruction language (native flags not available on Google Meet).
   - Acceptance criteria: 100% of completed Zoom OTO classes successfully ingested; Google Meet ingestion pipeline delivering sessions for processing.

2. **Language Detection and Threshold Enforcement**
   - Classes with less than 75% English content must be flagged and routed out of the primary evaluation pipeline.
   - These outlier sessions (Bahasa, Hindi, Bangla, and others) must be held pending localized prompt deployment in the multi-lingual phase.
   - Acceptance criteria: Language threshold correctly applied; flagged sessions visible in an outlier queue; no mis-scored non-English sessions passed through the primary pipeline.

3. **10-Point Pedagogical Rubric Evaluation**
   - The Engine must evaluate each ingested transcript against a defined 10-point pedagogical rubric.
   - The rubric includes metrics such as: Concept Clarity, Worked Examples, and Guided Practice (among others defined in the rubric document).
   - Acceptance criteria: Rubric evaluation runs automatically post-ingestion; all 10 rubric dimensions scored for each class; rubric definition versioned and auditable.

4. **PQS Forensic Ledger Generation**
   - The Engine must produce a PQS Forensic Ledger: a highly structured, chronological JSON array.
   - Each entry in the JSON must include: timestamp, pedagogical event type tag (e.g., `HOMEWORK_CHECK`, `EXPLANATION`), speaker role, exact evidence quote, and the mathematical basis for the score contribution.
   - The JSON format must be format-agnostic and infinitely extensible (able to support future dimensions without schema breaking changes).
   - Acceptance criteria: JSON Forensic Ledger produced for 91%+ of completed paid classes within enabled courses; all required fields present in every ledger entry.

5. **Class Energy (Voice Ratios) Display**
   - The parent report must display the teacher-to-student voice ratio (e.g., "94% Teacher / 6% Student") derived from the Forensic Ledger.
   - Acceptance criteria: Voice ratio calculated correctly; displayed prominently in the parent report.

6. **The Learning Journey Timeline**
   - The parent report must display a minute-by-minute visual timeline contrasting Concept Depth against Student Expression across the class duration.
   - Acceptance criteria: Timeline renders correctly for classes of varying lengths; data sourced from the Forensic Ledger timestamps and event types.

7. **Actionable Next Steps**
   - The parent report must include context-aware, personalized prompts for the parent (e.g., "Ask [child's name] to explain the difference between CeFi and DeFi").
   - These prompts must be generated based on the specific content and gaps identified in the Forensic Ledger.
   - Acceptance criteria: Actionable Next Steps are specific to the class content (not generic); reviewed for quality before rollout.

8. **Dynamic and Responsive Report UI**
   - The `post_class_feedback.html` parent UI must dynamically adapt without visual breakage across different device types and screen sizes.
   - Acceptance criteria: Report tested and verified on mobile (iOS and Android browsers) and desktop (Chrome, Safari); no layout breakage.

## UX/UI Flows

This feature has two primary flows: the backend processing pipeline and the parent-facing report experience.

### Flow 1: Backend Processing Pipeline (Post-Class)
1. Class ends on Zoom or Google Meet.
2. Ingestion Layer captures the raw class transcript.
3. Language detection runs:
   - Zoom: native platform flags used.
   - Google Meet: session routed through audio-transcript analysis pipeline.
4. If language is < 75% English: session is flagged and routed to the outlier queue (not processed by the primary engine).
5. If language passes the threshold: transcript is passed to The Engine.
6. The Engine maps the transcript against the 10-point pedagogical rubric.
7. The Engine generates the PQS Forensic Ledger (structured chronological JSON array).
8. The Forensic Ledger is stored in the backend data store.

### Flow 2: Narrative Generation — Parent Report
1. The Forensic Ledger is consumed by the Narrative Generation layer.
2. Voice ratio (Class Energy) is calculated from speaker role data in the ledger.
3. Minute-by-minute timeline (Learning Journey) is generated from timestamps and event type tags in the ledger.
4. Actionable Next Steps are generated from content and gap analysis of the ledger entries.
5. The `post_class_feedback.html` parent UI is rendered with all three modules populated.
6. Parent receives or accesses the report (via dashboard or notification).

### Parent Report UX
1. Parent receives a notification (WhatsApp/email) or navigates to the student dashboard post-class.
2. Parent opens the post-class feedback report.
3. Parent views the Class Energy module — sees voice ratio visualization.
4. Parent scrolls to the Learning Journey — views the minute-by-minute timeline.
5. Parent reads the Actionable Next Steps section and saves prompts to reinforce learning at home.

## Technical Requirements

- **Zoom Native Platform Flags**: Zoom API integration is used to access native language detection flags. Note: a 2-3% false-positive anomaly in the Zoom flag integration has been identified and is being patched.
- **Google Meet Audio-Transcript Analysis Pipeline**: Because Google Meet does not have native language flags, a separate audio-analysis pipeline is required for language identification. Technical strategy and cost architecture for this pipeline are being finalized.
- **PQS Forensic Ledger (JSON)**: The Forensic Ledger is the core data artifact of the system. It must be structured as a chronological JSON array with: timestamp, event type (`HOMEWORK_CHECK`, `EXPLANATION`, etc.), speaker role, evidence quote, and score justification. The format must be extensible without breaking changes.
- **Pedagogical Rubric Storage**: The 10-point rubric definition must be versioned and stored so that scores can be audited and reproduced. Rubric changes must not silently invalidate historical scores.
- **Language Processing Prompts**: The engine uses prompts (likely LLM-based) to evaluate transcripts. Multi-lingual prompt deployment (for Hindi, Bangla, Bahasa, etc.) is planned for the next phase.
- **Parent Report HTML**: The `post_class_feedback.html` file is the primary frontend output. It must be dynamically populated from the Forensic Ledger data and must render responsively across mobile and desktop.
- **Schola Course Expansion**: Course expansion under the Schola initiative may increase the volume of sessions processed; the pipeline must scale accordingly.
- **Language Authenticity Audits**: Periodic audits of language detection accuracy are planned to catch and reduce false positives/negatives in the language threshold enforcement.

## Non-Functional Requirements

- **Scale / Throughput**: System currently processes 70% of all OTO platform volume. Must scale with course and user base growth.
- **Accuracy**: Generates accurate PQS scores for 91% of completed paid classes within enabled courses. 79% total PQS generation rate (factoring in incomplete, dropped, or cancelled sessions).
- **Language Threshold**: Strict >75% English enforcement for current phase. Non-English sessions routed to outlier queue.
- **Responsiveness**: Parent report UI (`post_class_feedback.html`) must adapt without visual breakage across device types.
- **Extensibility**: JSON Forensic Ledger must be format-agnostic and extensible to support future rubric dimensions and output modules.
- **Zoom Flag Reliability**: Known 2-3% false-positive anomaly in Zoom native flag integration is being patched; monitoring required.
- **Accessibility**: Not explicitly specified in source; parent-facing HTML report should meet WCAG 2.1 AA as a baseline.
- **Browser Support**: Not explicitly specified; standard modern browsers (Chrome, Safari, Firefox, Edge) targeted for parent report rendering.

## Success Metrics

| Metric | Current Value | Notes |
|--------|---------------|-------|
| PQS Score Accuracy (completed paid classes, enabled courses) | 91% | Target: approach 100% |
| Total PQS Generation Rate (all sessions including drops/cancellations) | 79% | Factors in incomplete/dropped sessions |
| OTO Platform Volume Captured | 70% | Current coverage of all One-to-One sessions |
| Un-scored completed classes (language outliers) | ~9% | Requires multi-lingual rollout to resolve |

- **Primary KPI**: PQS generation accuracy rate for completed paid classes — target is to move toward 100% as language outliers are resolved and Google Meet pipeline is finalized.
- **Secondary KPI**: Parent engagement with the post-class feedback report (open rate, time on page, Actionable Next Steps viewed) — these are retention signals.
- **Business Goal**: Use the PQS-powered parent report as a retention engine; reduction in churn attributable to poor perceived learning quality is the long-term measure.

## Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| Class transcript is < 75% English (Bahasa, Hindi, Bangla, etc.) | Flag and route to outlier queue; hold pending multi-lingual prompt deployment; do not produce a score |
| Google Meet session has no native language flags | Route through audio-transcript analysis pipeline for language identification |
| Zoom native flag false positive (~2-3% anomaly) | Flag is being patched; monitoring pipeline must alert on anomalies; affected sessions manually reviewed |
| Incomplete or dropped class session | Session included in the 79% total PQS generation rate denominator; no score generated; session marked as incomplete |
| Forensic Ledger JSON is malformed or incomplete | Error logged; session flagged for re-processing; parent report not rendered with incomplete data |
| Parent report UI receives incomplete Forensic Ledger data | Graceful degradation: render available modules; do not display broken/empty chart sections without a fallback state |
| New rubric dimension added to the 10-point rubric | Forensic Ledger JSON extensibility must absorb new fields without breaking historical data reads |

## Dependencies

| Dependency | Owner | Notes |
|------------|-------|-------|
| Zoom Native Language Flag API | Tech | Required for Zoom transcript ingestion; 2-3% false-positive anomaly being patched |
| Google Meet Audio-Transcript Analysis Pipeline | Tech | Technical strategy and cost architecture being finalized; blocker for full Google Meet coverage |
| 10-Point Pedagogical Rubric Definition | Curriculum / QA | Must be versioned and maintained; changes must be carefully managed to avoid invalidating historical scores |
| Multi-Lingual Prompt Deployment | Tech / Curriculum | Required to process the ~9% of non-English sessions currently routed to the outlier queue |
| Schola Course Expansion | Product / Curriculum | Increasing course volume will increase processing load; pipeline must scale accordingly |
| Language Authenticity Audit Process | QA / Operations | Ongoing audits required to monitor and improve language detection accuracy |
| Parent Notification Service | Tech | Required to deliver post-class feedback report links to parents via WhatsApp/email |
| QA Sign-off | QA | Regression required for rubric accuracy, language threshold enforcement, and parent report rendering |
