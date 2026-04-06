---
title: Marketing ETL Documentation
category: technical-architecture
subcategory: etl-and-async-jobs
source_id: e02ff9e3-f30b-418c-ad1e-541eaeb49e45
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Marketing ETL Documentation

## Overview
This document describes the Marketing ETL pipeline, which aggregates performance marketing spend data from Google Ads and Facebook/Meta into a unified dataset for campaign effectiveness analysis across courses, verticals, channels, and geographies using SQL-based transformations in AWS Glue.

## API Contract
N/A — This is an internal ETL pipeline, not an HTTP API.

## Logic Flow
### Controller Layer
N/A — ETL pipeline executed on schedule via AWS Glue.

### Service/Facade Layer
**4-Step ETL Data Flow:**

1. **Base Data Selection**
   - Ingest raw data from two sources:
     - `tryouts.performance_marketing_google_spends` (Google Ads data)
     - `tryouts.performance_marketing_spends` (Facebook/Meta Ads data)

2. **Dimension Derivation** (Business Logic via CASE statements)
   - **Geographic dimensions:**
     - Derive `country_name` from country codes
     - Special mappings: `'BC'` and `'Hubs Centre'` → `'Vietnam'`; unmatched codes → default `'India'`
     - Derive `business_region`: SEA, Rest of the World, USA_Canada
   - **Product dimensions:**
     - Map numeric `vertical_id` to human-readable `vertical_name` (e.g., 1 → 'Codechamps', 2 → 'Finchamps')
     - Map to broader `course_name` (e.g., 'Coding', 'Financial Literacy', 'Robotics')
   - **Marketing channel standardization:**
     - Transform campaign `flag` into standardized `utm_updated` classification
     - Normalized buckets: Google-Display, App-Android, App-IOS, FB, TikTok, DSA (Direct Sales Agent), Affiliate

3. **Aggregation**
   - Group by all derived dimensions
   - Sum quantitative metrics with null → 0 defaulting for spend values
   - Metrics aggregated: `spend`, `impressions`, `clicks`, `unique_clicks`, `reach`, `inline_link_clicks`, `post_engagements`

4. **Final Output**
   - Generates `FINAL_OUTPUT` dataset/table
   - Columns: `date`, `country_name`, `vertical_name`, `course_name`, `utm_updated`, aggregated metrics
   - Left joins to country mapping tables (`countries`, `country_groupings`) to preserve all records

### High-Level Design (HLD)
```
GOOGLE_DATA (tryouts.performance_marketing_google_spends)
        │
        └──────┐
               ▼
FACEBOOK_DATA (tryouts.performance_marketing_spends)
               │
               ▼
COUNTRY_MAPPING + BUSINESS_REGION (left joins)
               │
               ▼
CASE-based Dimension Derivation
(country_name, business_region, vertical_name, course_name, utm_updated)
               │
               ▼
GROUP BY dimensions → SUM metrics → NULL → 0
               │
               ▼
FINAL_OUTPUT (unified marketing performance table)
```

## External Integrations
- **Google Ads** — Source data (via `tryouts.performance_marketing_google_spends` table)
- **Facebook/Meta Ads** — Source data (via `tryouts.performance_marketing_spends` table)
- **AWS Glue** — ETL execution platform
- **PostgreSQL** — Source and target database

## Internal Service Dependencies
- Marketing ETL → `tryouts` schema (PostgreSQL) for source data
- Marketing ETL → `countries`, `country_groupings` reference tables
- FINAL_OUTPUT → Marketing analytics/BI dashboards (Metabase: `https://analytics.brightchamps.com/question/2622-marketing-alert`)

## Database Operations
### Tables Accessed
- **Source**: `tryouts.performance_marketing_google_spends`
- **Source**: `tryouts.performance_marketing_spends`
- **Reference**: `countries` table (country code to name mapping)
- **Reference**: `country_groupings` table (country to business region mapping)
- **Target**: `FINAL_OUTPUT` (aggregated marketing performance)

### SQL / ORM Queries
```sql
-- Dimension derivation example
CASE
  WHEN country_code = 'BC' THEN 'Vietnam'
  WHEN country_code = 'Hubs Centre' THEN 'Vietnam'
  ELSE COALESCE(c.country_name, 'India')
END AS country_name,

CASE vertical_id
  WHEN 1 THEN 'Codechamps'
  WHEN 2 THEN 'Finchamps'
  ...
END AS vertical_name,

CASE flag
  WHEN 'google_display' THEN 'Google-Display'
  WHEN 'app_android' THEN 'App-Android'
  ...
END AS utm_updated

-- Aggregation
GROUP BY date, country_name, business_region, vertical_name, course_name, utm_updated
-- Metrics
SUM(COALESCE(spend, 0)) AS total_spend,
SUM(COALESCE(impressions, 0)) AS total_impressions,
SUM(COALESCE(clicks, 0)) AS total_clicks
```

### Transactions
N/A — ETL pipeline is a read-transform-write batch job; not transactional in the traditional sense.

## Performance Analysis
### Good Practices
- Left joins on country mapping tables preserve all records even when country data is incomplete
- COALESCE for null handling prevents incorrect metric aggregations
- Separate staging tables (`performance_marketing_google_spends`, `performance_marketing_spends`) per source prevent schema coupling

### Performance Concerns
- No scheduling information documented — unclear if this pipeline runs at appropriate freshness for marketing decision-making
- CASE statements for dimension derivation hardcode business logic in SQL — changes require SQL edits and pipeline redeployment
- No incremental load strategy documented for the main marketing spend tables — could be doing full table scans on large datasets

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Hardcoded country/vertical mappings in SQL CASE statements — brittle and hard to maintain |
| Medium | Scheduling not documented — unclear pipeline freshness guarantees |
| Medium | No documentation on incremental vs. full load strategy |
| Low | `'BC'` and `'Hubs Centre'` → Vietnam mapping is non-obvious — needs a source data fix upstream |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Document the current schedule and freshness SLA for the Marketing ETL
- Move country/vertical/channel mappings from hardcoded SQL CASE statements to a reference/lookup table that can be updated without pipeline changes

### Month 1 (Architectural)
- Implement incremental load pattern (using `updated_at` or date-based partitioning) to avoid full table scans
- Add data quality checks: alert if Google or Facebook source tables have zero rows for a given date (data pipeline upstream failures)
- Connect the Metabase alert (`/question/2622-marketing-alert`) to automated Slack/email notifications

## Test Scenarios
### Functional Tests
- Google data rows correctly joined and country name derived
- Facebook data rows correctly standardized with `utm_updated` classification
- Left joins ensure no records are dropped when country mapping is missing
- COALESCE ensures NULL spend values appear as 0 in FINAL_OUTPUT

### Performance & Security Tests
- ETL completes within SLA window (define target, e.g., <30 minutes for daily run)
- FINAL_OUTPUT row count matches expected sum of Google + Facebook source rows

### Edge Cases
- New country code added to source data with no CASE mapping — should default to 'India', not error
- New vertical ID added without CASE mapping — NULL vertical_name in output (alert needed)
- Facebook API data missing for a day — partial output vs. full failure handling

## Async Jobs & ETL
- **Platform**: AWS Glue
- **Sources**: PostgreSQL (`tryouts` schema)
- **Target**: PostgreSQL (FINAL_OUTPUT table)
- **Schedule**: Daily (per ETL Inventory catalog)
- **Status**: Healthy, Incremental: Yes
- **Alert**: `https://analytics.brightchamps.com/question/2622-marketing-alert`
- **Owner**: Kadambi Kashyap
