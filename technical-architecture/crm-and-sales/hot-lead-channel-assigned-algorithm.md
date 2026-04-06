---
title: Hot-Lead Channel Assigned Algorithm
category: technical-architecture
subcategory: crm-and-sales
source_id: 47fbdd66
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Hot-Lead Channel Assigned Algorithm

## Overview
The hot-lead channel assignment algorithm distributes hot leads across Slack channels using a vector distance minimization approach. It computes the channel that minimizes the distance between the current lead count distribution (normalized) and the target weightage vector, ensuring balanced distribution across channels over time.

## API Contract
**`GET /prabandhan/v1/hotlead/channels/filters`**
- Fetches the assigned hot lead channel mapping
- **Query Parameters:** `countryId`, `languageId`, `utmSource`, `courseId`, `fallback`
- **Response:** Channel assignment data including weightage and assignment counts

N/A for the algorithm itself — it runs internally within the hot lead routing Lambda.

## Logic Flow

### Controller Layer
- `GET /prabandhan/v1/hotlead/channels/filters` returns channel filter mappings
- Used by hot lead routing Lambda to determine candidate channels

### Service/Facade Layer
**Filter Resolution:**
1. Query `master_group_filters` with student attributes:
   - `channel` (priority: 11), `courseId` (priority: 4), `countryId` (priority: 3), `languageId` (priority: 2), `utmSource` (priority: 1)
   - `null` = wildcard
2. Find the matching sales group
3. Retrieve all Slack channels associated with that group (from `group_hotlead_channnel_mappings`)
4. Each channel has an associated `weightage` value

**Vector Distance Algorithm:**
1. Get `weightages` array: e.g., `[0.6, 0.3, 0.1]` for channels A, B, C
2. Get `counts` array: hot leads assigned in past 2 days per channel, e.g., `[12, 8, 2]`
3. For each channel `i`:
   a. Create temp counts array with `counts[i] + 1` (simulating assigning this lead to channel i)
   b. Normalize the temp counts vector (divide each by total)
   c. Compute absolute distance between normalized counts and weightages vector
4. Select channel with **minimum distance**
5. Increment `counts[selected_channel]` by 1 in database

**Result:** Lead is routed to the Slack channel that brings the distribution closest to the target weightage.

### High-Level Design (HLD)
```
Hot lead triggered (POST /hotlead with classId)
  → Get student attributes (course, language, country, utmSource)
  → master_group_filters lookup (priority-weighted matching)
  → Find sales group
  → group_hotlead_channnel_mappings: get channels + weightages
  → Get counts (past 2 days per channel)
  → FOR EACH channel:
      → Simulate assignment (counts[i] + 1)
      → Normalize vector
      → Compute |normalized_counts - weightages| absolute distance
  → SELECT channel with min distance
  → Increment channel count in DB
  → POST to Slack channel: hot lead notification
```

## External Integrations
- **Slack API:** Sends hot lead notification to selected channel

## Internal Service Dependencies
- **Prabandhan:** `master_group_filters`, `groups`, `group_hotlead_channnel_mappings`, `hotlead_channels`, `crm_users`

## Database Operations

### Tables Accessed
- `master_group_filters` — Filter rules per attribute (channel, course, country, language, utm)
- `groups` — Group definitions
- `group_hotlead_channnel_mappings` — Maps groups to Slack channels with weightages
- `hotlead_channels` — Channel details and weightage values
- `group_hotlead_channel_fallbacks` — Fallback channel configurations for JUMP logic

### SQL / ORM Queries
- SELECT `master_group_filters` WHERE (matching student attributes) ORDER BY priority DESC
- SELECT `group_hotlead_channnel_mappings` WHERE `group_id = ?`
- SELECT `hotlead_channels` WHERE `id IN (channelIds)` — get weightages
- SELECT `COUNT(*)` FROM hot lead assignments WHERE `channel_id = ? AND assigned_at > NOW() - 2 days`
- UPDATE `hotlead_channels` SET `recent_count = recent_count + 1` WHERE `id = selectedChannelId`

### Transactions
- Channel count increment must be atomic with channel selection to prevent concurrent routing errors

## Performance Analysis

### Good Practices
- Vector distance algorithm ensures statistically balanced distribution without centralized state machine
- 2-day rolling window prevents stale historical data from distorting current distribution
- Null wildcard in filters allows flexible group matching without combinatorial explosion

### Performance Concerns
- Algorithm iterates over all channels per hot lead — O(n*channels) per routing decision
- Count query per channel (past 2 days) could be expensive under high channel count
- `recent_count` increment without atomic lock → race condition if two hot leads arrive simultaneously

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | `recent_count` increment lacks atomic lock — concurrent hot leads can be assigned to same channel |
| Medium | O(n*channels) distance computation — performance degrades with many channels per group |
| Low | 2-day window is hardcoded — not configurable per group |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Use `SELECT FOR UPDATE` or Redis atomic increment for `recent_count` to prevent race conditions
- Pre-aggregate recent counts in a materialized view updated every 15 minutes

### Month 1 (Architectural)
- Move routing algorithm to a dedicated service with Redis-backed channel state for low-latency decisions
- Make the time window (currently 2 days) configurable per group via admin settings

## Test Scenarios

### Functional Tests
- Channel A weightage=0.6, B=0.3, C=0.1 → over 100 hot leads, distribution approaches 60/30/10
- Fallback channel assigned when main channel has no available SMs after JUMP timeout
- `countryId`-based filter: UAE leads → UAE-specialized channel, India leads → India channel

### Performance & Security Tests
- 20 concurrent hot leads arriving simultaneously → correct distribution, no double-assignment
- `master_group_filters` lookup with many null wildcards — query performance

### Edge Cases
- All channels have `weightage=0` → equal distribution fallback
- No matching group filter for student's attributes → fallback channel
- 2-day count is 0 for all channels (new group) → random/first-channel selection
