---
title: Teacher Prioritizing Logic V0
category: product-prd
subcategory: student-lifecycle
source_id: 4aa898ed-b25e-43b6-a0fe-e51162de5b33
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# Teacher Prioritizing Logic V0

## Overview

Teacher Prioritizing Logic V0 introduces a data-driven scoring and ranking system to determine which teachers are allocated to demo (trial) classes at BrightChamps. The system is built on the hypothesis that the quality of the demo teacher is the single largest lever for improving demo conversion rates. By systematically identifying and prioritizing high-converting teachers, the business expects to dramatically improve its "Conversions per Deal" metric — from an initial baseline of 10-12% up to a target of 60%.

The feature operates as a backend allocation engine that evaluates teachers based on their historical conversion performance across multiple time windows, buckets them into four performance tiers (Star, Good, Okay, Poor), and enforces allocation rules that ensure top-tier teachers receive the majority of demo class assignments. The system runs independently across three regional segments: US/CA, ROW (Rest of World), and Vietnam.

In addition to the automated allocation logic, the feature introduces a pre-demo visibility tool for the internal Academy team — a Metabase query interface that allows Academy members to manually look up available Star and Good teachers for specific time slots, enabling human oversight and last-mile staffing operations before demos begin.

## Problem Statement

BrightChamps relies on demo (trial) classes as the primary conversion mechanism for new customers. Currently, demo teachers are allocated without a structured performance-based prioritization system, resulting in a significant portion of demos being conducted by average or underperforming teachers. This leads to a low demo conversion rate (10-12% baseline), meaning the vast majority of potential customers do not convert after their first experience with the platform. The business is leaving substantial revenue on the table by not systematically routing high-intent leads to the teachers most likely to convert them. Teacher Prioritizing Logic V0 directly addresses this by building the infrastructure to rank, bucket, and preferentially allocate demo teachers based on their proven conversion track records.

## User Stories

- As an Academy team member, I want to query a list of available teachers by Date, Slot, Region, and Course, so that I can easily source top-performing teachers for upcoming demos without manually reviewing individual teacher records.
- As an allocation system, I want to group teachers into Star, Good, Okay, and Poor performance tiers based on their historical conversion metrics, so that I can prioritize allocating demos to the top 50% of teachers and maximize conversion outcomes.
- As a system administrator, I want the scoring and ranking logic to be configurable via the Nected integration, so that the weights and thresholds can be adjusted in response to new data without requiring a code deployment.
- As a risk manager, I want teachers with fewer than 7 total demos to be capped at 2 demos per day, so that we limit the business risk of over-relying on unproven teachers who have not yet established a reliable conversion track record.
- As an operations manager, I want the allocation logic to only consider Star and Good teachers until 6 hours before a demo slot, so that low-performing teachers are only used as a fallback in genuine shortage situations, not as a default.

## Feature Scope

### In Scope

- Backend scoring logic to calculate teacher performance metrics: benchmark_cvr, rcvr, and ocvr
- Performance tier bucketing: Star (0-20th percentile), Good (20-40th percentile), Okay (40-70th percentile), Poor (bottom 30th percentile and specific edge cases)
- Regional independence: logic runs separately for US/CA, ROW, and Vietnam
- Allocation rules enforcement: Star and Good teachers preferred until 6 hours before demo; blacklisted teachers never considered; new teachers (fewer than 7 demos) capped at 2 demos per day
- Pre-demo visibility query via Metabase: Academy team can filter by Date, Slot, Region, and Course to find available Star and Good teachers
- Edge case handling: teachers with fewer than 4 demos have rcvr ignored; teachers with exactly 7 demos and 0 conversions are placed in Poor tier and flagged for blacklisting
- Nected integration for configurable scoring parameters (with hardcode fallback for V0)
- Manual blacklisting capability for Poor-tier teachers

### Out of Scope

- Front-end product screens for teachers or students (this is a backend allocation engine)
- Score reduction after each same-day allocation (documented as a future rule, explicitly scoped out of V0)
- Automated blacklisting (manual blacklisting only in V0)
- Real-time teacher scoring dashboards for internal teams (Metabase query is the visibility mechanism in V0)
- Student-facing teacher selection based on this scoring logic (a downstream dependency)

## Functional Requirements

1. **Regional Independence**: The scoring and bucketing logic must execute independently for each of the three regions: US/CA, ROW, and Vietnam.
   - Acceptance Criteria: A teacher's tier assignment in the US/CA region must not be influenced by their performance data in ROW or Vietnam. The three regional calculation pipelines must be isolated.

2. **Benchmark CVR Calculation**: The system must calculate `benchmark_cvr` as the average conversion rate for a given course, derived from all teachers' data over the last 6 months.
   - Acceptance Criteria: `benchmark_cvr` must be recalculated on a defined schedule (e.g., weekly or monthly) and stored for use in relative teacher scoring. The calculation must only include demos that meet the "eligible demo" criteria.

3. **Recent CVR Calculation (rcvr)**: The system must calculate `rcvr` as each teacher's individual conversion rate over their last 3 months of demo data.
   - Acceptance Criteria: If a teacher has 4 or fewer total demos, `rcvr` must be ignored entirely and not factored into their score. Teachers must have at least 5 demos to have a valid rcvr.

4. **Overall CVR Calculation (ocvr)**: The system must calculate `ocvr` as each teacher's conversion rate over the last 24 months of demo data.
   - Acceptance Criteria: `ocvr` must provide a longer-term view of teacher performance to balance against the shorter-term recency bias of `rcvr`.

5. **Eligible Demo Definition**: Demos included in conversion calculations must meet at least one of the following criteria:
   - The student joined the demo session but did not complete it (partial attendance)
   - The demo has a mapped deal with a status of CLOSED WON or CLOSED LOST
   - The demo was completed 7 or more days earlier
   - Acceptance Criteria: Demos that are too recent (under 7 days old) and have no deal status must be excluded from calculations to prevent premature scoring.

6. **Performance Tier Bucketing**: Teachers must be ranked and assigned to one of four tiers based on their composite score:
   - **Star** (0th-20th percentile — top performers): Expected to receive 50% of all demo allocations
   - **Good** (20th-40th percentile): Expected to receive 25% of all demo allocations
   - **Okay** (40th-70th percentile): Expected to receive 25% of all demo allocations
   - **Poor** (bottom 30th percentile + specific edge cases): Flagged for manual blacklisting; not allocated demos
   - Acceptance Criteria: The sum of expected allocation percentages across Star, Good, and Okay must equal 100%. Tier boundaries must be recalculated whenever the teacher pool is rescored.

7. **Allocation Priority Window**: Until 6 hours before a scheduled demo, only Star and Good tier teachers must be considered for allocation predictions and assignment.
   - Acceptance Criteria: The system must enforce a hard cutoff at the T-6 hours mark. After this point, Okay teachers may be considered if Star and Good teachers are unavailable. Poor and blacklisted teachers must never be included regardless of timing.

8. **New Teacher Risk Cap**: Any teacher with fewer than 7 total utilized demos must be capped at a maximum of 2 demo allocations per day.
   - Acceptance Criteria: The system must check a teacher's total demo count before each allocation decision. If the count is below 7 and the teacher has already been allocated 2 demos that day, they must be excluded from further same-day allocation.

9. **Blacklist Enforcement**: Blacklisted teachers must never be included in any allocation consideration, regardless of tier, timing, or availability.
   - Acceptance Criteria: The blacklist check must be the first filter applied in every allocation decision. No blacklisted teacher can pass to subsequent allocation logic.

10. **Pre-Demo Metabase Query**: A Metabase query must allow Academy team members to input Date, Slot, Region, and Course and receive a filtered list of Star and Good teachers who are not on leave and have no conflicting scheduled classes during the requested slot.
    - Acceptance Criteria: The query output must include: Teacher ID, Teacher Name, TL Name, and Availability (TRUE/FALSE). Only Star and Good tier teachers must appear in results. Teachers on leave or with a conflicting class must show Availability = FALSE.

11. **Nected Configuration Integration**: The scoring weights and tier thresholds should be fetched from Nected to allow dynamic reconfiguration without a code deployment.
    - Acceptance Criteria for V0: If Nected integration cannot be completed in time, hardcoded values within the system are acceptable as a fallback. The V0 launch must not be blocked on Nected integration.

## UX/UI Flows

This feature has no student-facing or teacher-facing front-end screens. The primary user-facing interface is the Metabase query tool for the Academy team.

### Academy Pre-Demo Sourcing Flow (Metabase)
1. The Academy team member opens the Metabase query interface.
2. They input the required filter fields: `[Date]`, `[Slot]`, `[Region]`, `[Course]`.
3. They run the query.
4. The system filters the teacher pool to return only Star and Good tier teachers who are not on leave and have no conflicting class scheduled during the requested slot.
5. Results are returned showing: Teacher ID, Teacher Name, TL Name, Availability (TRUE/FALSE).
6. The Academy team member identifies available top-performing teachers and coordinates demo assignments accordingly.

### Automated Allocation Flow (Backend)
1. A demo slot is identified in the scheduling system.
2. The allocation engine checks the current time against the demo start time.
3. If more than 6 hours remain: only Star and Good teachers are eligible.
4. If fewer than 6 hours remain: Star, Good, and Okay teachers are eligible.
5. The engine filters out blacklisted teachers and teachers who are on leave.
6. For remaining eligible teachers, the engine applies the new-teacher risk cap (max 2 demos/day for teachers with fewer than 7 total demos).
7. From the remaining pool, the engine selects a teacher following the tier allocation split (50% Star, 25% Good, 25% Okay).
8. The selected teacher is assigned to the demo slot.

## Technical Requirements

- **Metric Calculation Backend**: The backend must track and calculate rolling conversion rate metrics for each teacher across three windows: 3-month (rcvr), 6-month (benchmark_cvr), and 24-month (ocvr). These must be recalculated on a defined schedule and stored for retrieval by the allocation engine.
- **Deal State Integration**: The system must read deal states (CLOSED WON, CLOSED LOST) from the CRM or deal management system to determine eligible demos for conversion calculations.
- **Nected Integration**: Scoring configuration (weights, thresholds, tier boundary percentiles) should be fetched from Nected. A hardcoded fallback is acceptable for V0 if the integration is not ready.
- **Metabase Integration**: The Academy visibility query must be implemented as a Metabase query with the required input parameters (Date, Slot, Region, Course) and output columns (Teacher ID, Teacher Name, TL Name, Availability).
- **Blacklist Storage**: The blacklist must be stored in a database table that the allocation engine reads at the start of every allocation decision. The blacklist must be manually maintainable by authorized operations staff.
- **Leave and Availability Data**: The allocation system must have access to teacher leave records and scheduled class data to properly filter out unavailable teachers in both the Metabase query and the automated allocation flow.
- **Demo Allocation Counter**: The system must track daily demo allocation counts per teacher to enforce the 2-demo-per-day cap for new teachers (fewer than 7 total demos).

## Non-Functional Requirements

- **Configurability**: The primary non-functional requirement is that scoring logic must be configurable via Nected without requiring a code deployment. This enables the business to respond to performance data and adjust thresholds quickly.
- **Regional Isolation**: The calculation and bucketing pipelines for US/CA, ROW, and Vietnam must be isolated to prevent cross-regional data contamination.
- **V0 Fallback Tolerance**: Given that this is a V0 implementation, hardcoded configuration values are acceptable if the Nected integration cannot be completed within the release window. The feature must not be blocked on external integrations.
- **Auditability**: All allocation decisions must be logged with sufficient metadata (teacher selected, tier at time of selection, demo ID, region, timestamp) to enable post-hoc analysis and debugging.

## Success Metrics

- **Primary KPI**: "Conversions per Deal" — the primary metric the entire feature is designed to improve.
- **Target**: Demo conversion rate must increase from the current baseline of 10-12% to a target of 60% post-launch.
- **Measurement**: Conversion rate must be tracked per teacher tier to validate that Star and Good teachers outperform Okay teachers, confirming the bucketing logic is sound.
- **Secondary Metrics**: Percentage of demos covered by Star and Good teachers (allocation quality); reduction in demos conducted by Poor-tier teachers; Academy team time saved on manual teacher sourcing.

## Edge Cases & Error Handling

- **Insufficient Recent Demo Data**: If a teacher has 4 or fewer total demos, the system must completely ignore their `rcvr` (recent 3-month conversion rate) when computing their score. Only `ocvr` and relative `benchmark_cvr` comparisons must inform their tier placement.
- **New Teacher with Zero Conversions at 7 Demos**: If a new teacher reaches exactly 7 utilized demos with 0 conversions, they must be immediately bucketed into the Poor tier and flagged for manual blacklisting review. This prevents a new teacher from continuing to receive demos despite a clear zero-conversion track record.
- **All Top-Tier Teachers Unavailable**: If no Star or Good teachers are available for a slot and the 6-hour window has not yet passed, the allocation system must surface this as a shortage condition to the Academy team via the Metabase query (Availability = FALSE for all results), enabling human intervention to resolve the staffing gap.
- **Future Rule — Same-Day Score Reduction**: A rule to reduce a teacher's score by 10% after each successful allocation within the same day is documented in the source as a future enhancement. This rule is explicitly scoped out of V0 and must not be implemented until V1.
- **Nected Unavailability**: If the Nected service is unavailable at the time the allocation engine needs scoring configuration, the system must fall back to the hardcoded configuration values. An alert must be raised to the operations team.

## Dependencies

- **Team Dependencies**: The feature requires coordination across Business (Micky Sukhwani), Product (Paul), Tech (Aditya Bhargav, Dhawal Agrawal), and QA (Vidurbh Raj Srivastava).
- **Metabase Setup**: The pre-demo visibility report depends on Metabase being set up and configured with access to the relevant teacher performance and availability data. This is a prerequisite for the Academy team tooling.
- **Nected Service**: Dynamic scoring configuration depends on the Nected service being integrated. While a hardcode fallback exists for V0, the Nected integration must be completed in a subsequent sprint to achieve the full configurability goal.
- **CRM / Deal Management System**: Calculating eligible demos requires access to deal states (CLOSED WON, CLOSED LOST) from the CRM. The data pipeline between the CRM and the scoring backend must be established before the conversion rate calculations can be trusted.
- **Leave Management System**: Filtering out unavailable teachers in the Metabase query and allocation engine requires access to teacher leave records. Integration with the leave management system is a prerequisite.
- **Teacher Profile Data**: The allocation engine must have access to current teacher availability, teaching schedule, and total demo count. These data sources must be reliable and up-to-date for the system to function correctly.
