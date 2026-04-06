---
title: Feed
category: technical-architecture
subcategory: etl-and-async-jobs
source_id: e2dc7ead-7257-4ed5-9297-885524c348dd
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Feed

## Overview
This document describes the BrightCHAMPS student dashboard Feed feature — a social-style content feed (similar to Instagram) that displays student and teacher posts, enables interactions (thumbs up, celebrate, share, comment), and uses pre-computed Redis-cached views with a scoring-based ranking algorithm to optimize scroll performance.

## API Contract
**Interactions Sync API:**
- Method: `POST`
- Path: `/interactions/sync` (implied)
- Request Body:
```json
{
  "parentType": "post | comment",
  "parentId": "<id>",
  "interactionType": "thumbs_up | celebrate | share | comment",
  "userId": "<userId>"
}
```
- Response: Updated interaction state and post metrics

**Feed Load API:**
- Query params: `scope=global|student`, `sort=most_recent|most_viewed`
- Response: Pre-computed feed view from Redis cache

**Auth:** Standard Bearer token — scope controls Global Feed vs. Student (private) Feed access.

## Logic Flow
### Controller Layer
Users load the feed with a scope preference (global or private) and sort preference (most recent or most viewed). The system serves a pre-computed view from Redis. When interactions occur, they update aggregate metrics and trigger re-ranking via the View Generation Lambda.

### Service/Facade Layer
**Feed Scopes:**
- **Global Feed** — Posts from all users (students and teachers) visible to all
- **Student Feed (Private)** — Posts visible only to the post owner

**Post Types:**
- User-generated posts (created directly)
- System-generated posts — triggered by milestones: class completions, certificate generation, assignment/quiz reminders
- Posts use pre-defined **templates** which dictate reference types and data update rules

**Feed Architecture (Lambda-based):**

1. **Process Content Lambda**
   - Triggered after media upload to S3
   - Fetches media metadata
   - Creates a media info record in DB
   - Transforms raw S3 file streams into playlists
   - Pushes processed media back to S3
   - Enqueues post data into the creation SQS queue

2. **Post Creation Lambda** (SQS consumer)
   - Processes creation requests in batches of 20 messages or every 30 seconds
   - Builds JSON payloads based on templates
   - Fetches all referenced entities
   - Checks if post already exists (idempotency check)
   - Executes DB write inside a SQL transaction

3. **View Generation Lambda** (currently disabled)
   - Batches interaction events in groups of 100 or every 30 seconds
   - Dynamically updates feed rankings and cached views based on new interactions

**Interaction Handling:**
- Actions: thumbs up, celebrate, share, comment
- Interaction recorded in DB
- Aggregate post metrics updated (Feed Entity Metrics table)
- Event pushed to View Generation queue
- Interactions can be toggled inactive (e.g., "unliking" a post)

**Comment System:**
- Comments can be nested (parent = post or another comment)
- Comments have visibility scopes set by the commenter

### High-Level Design (HLD)
```
Media Upload (S3)
        │
        ▼
Process Content Lambda
        │
        ├── Fetch metadata
        ├── Create MediaInfo record
        ├── Transform stream → playlist
        ├── Push processed media to S3
        └── Enqueue to Post Creation SQS Queue
                │
                ▼
Post Creation Lambda (consumer, batch 20 / 30s)
        │
        ├── Build JSON payload from template
        ├── Fetch references
        ├── Idempotency check (post exists?)
        └── SQL Transaction:
            ├── INSERT posts
            ├── INSERT post references
            └── INSERT feed entity metrics (or ROLLBACK on failure)

User Interaction (thumbs_up, celebrate, share, comment)
        │
        ▼
Interactions Sync API
        │
        ├── Record interaction in user_interactions table
        ├── Update post aggregate metrics
        └── Push event to View Generation Queue
                │
                ▼
View Generation Lambda (disabled — batch 100 / 30s)
        │
        └── Recompute ranking score
            └── Update Redis cached view

User Loads Feed
        │
        ▼
Redis Cache (pre-computed views: most_recent or most_viewed)
        │
        ▼
Feed Content Rendered
```

**Ranking Algorithm:**
- Computes score based on: post metrics + scope + creation time + mathematical multiplier
- If new post's max score > minimum score of existing cached view → view updated with new post
- If view exceeds size limit → lowest-ranked entries removed from bottom

## External Integrations
- **AWS S3** — Media storage (raw uploads and processed playlists)
- **AWS SQS** — Post creation queue (consumed by Post Creation Lambda), View Generation queue
- **AWS Lambda** — Process Content Lambda, Post Creation Lambda, View Generation Lambda
- **Redis** — Pre-computed view cache for feed rendering
- **AWS RDS (MySQL)** — Persistent storage for all feed tables

## Internal Service Dependencies
- Feed Service → S3 (media storage/processing)
- Feed Service → SQS (post creation and view generation queues)
- Feed Service → Redis (view cache reads and writes)
- Feed Service → Eklavya (student entity data for post references)
- Feed Service → Dronacharya (employee/teacher entity data for post references)
- Feed Service → Paathshala (class completion triggers for system-generated posts)

## Database Operations
### Tables Accessed

**Posts**
| Column | Description |
|--------|-------------|
| id | Post identifier |
| user_id | Post owner |
| template_id | FK to Post Templates |
| scope | global or student (private) |
| status | active / inactive |
| created_at | Creation timestamp |

**Post Templates**
| Column | Description |
|--------|-------------|
| id | Template identifier |
| reference_types | What entities this template references |
| update_rules | How post data is updated |

**Post Media Info**
| Column | Description |
|--------|-------------|
| id | Media record |
| post_id | FK to Posts |
| media_url | S3 URL |
| playlist_url | Processed playlist URL |

**Post Reference Mappings**
| Column | Description |
|--------|-------------|
| post_id | FK to Posts |
| reference_type | Entity type |
| reference_id | Entity ID |

**Feed Entity Metrics**
| Column | Description |
|--------|-------------|
| post_id | FK to Posts |
| thumbs_up_count | Aggregate interaction count |
| celebrate_count | Aggregate interaction count |
| share_count | Aggregate interaction count |
| comment_count | Aggregate interaction count |
| score | Computed ranking score |

**User Interactions**
| Column | Description |
|--------|-------------|
| id | Interaction identifier |
| user_id | Interacting user |
| parent_type | post or comment |
| parent_id | Target post/comment ID |
| interaction_type | thumbs_up / celebrate / share / comment |
| active | Boolean (false if "unliked") |

**Comments**
| Column | Description |
|--------|-------------|
| id | Comment identifier |
| parent_type | post or comment (nested) |
| parent_id | Parent post/comment ID |
| content | Comment text |
| visibility_scope | Commenter-defined visibility |
| user_id | Comment author |

### SQL / ORM Queries
```sql
-- Post creation (transactional)
BEGIN;
  INSERT INTO posts (user_id, template_id, scope, status, created_at) VALUES (...);
  INSERT INTO post_reference_mappings (post_id, reference_type, reference_id) VALUES (...);
  INSERT INTO feed_entity_metrics (post_id, thumbs_up_count, score) VALUES (0, 0, computed_score);
COMMIT; -- or ROLLBACK on failure

-- Interaction update
UPDATE feed_entity_metrics
SET thumbs_up_count = thumbs_up_count + 1,
    score = recomputed_score
WHERE post_id = :postId;
```

### Transactions
- Post creation (INSERT posts + references + metrics) is wrapped in a SQL transaction
- On success: COMMIT
- On failure: ROLLBACK
- Ensures no partial post records exist in the database

## Performance Analysis
### Good Practices
- Pre-computed Redis cached views prevent real-time DB queries on feed scroll
- SQS batch processing (20 messages / 30 seconds) smooths traffic spikes for post creation
- SQL transactions on post creation prevent partial/corrupt records
- Idempotency check before post creation prevents duplicate posts on re-trigger
- Scope separation (global vs. private) prevents unauthorized content access

### Performance Concerns
- View Generation Lambda is currently **disabled** — ranking scores may be stale
- Redis view eviction: if cached view is stale and Lambda is disabled, users may see outdated rankings
- SQS batch size of 20 with 30-second timeout introduces up to 30-second latency for new post appearance
- No documented cache invalidation strategy for Redis feed views if a post is deleted or made inactive

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | View Generation Lambda is disabled — ranking is not being updated dynamically |
| High | No cache invalidation strategy documented for deleted/inactive posts in Redis views |
| Medium | 30-second SQS batch timeout introduces latency for new post visibility |
| Medium | System-generated posts depend on milestone events from multiple services — coupling risk |
| Low | Comment nesting depth not limited — could create deeply nested structures |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Re-enable View Generation Lambda with appropriate batch sizing for current traffic volume
- Document and implement a cache invalidation mechanism for deleted/inactive posts in Redis
- Add a maximum nesting depth limit for comments (e.g., max 3 levels)

### Month 1 (Architectural)
- Reduce SQS post creation batch timeout from 30 seconds to 5–10 seconds for faster post visibility
- Add a dead letter queue (DLQ) for failed post creation messages
- Implement a real-time score update path (in addition to batch) for high-velocity posts

## Test Scenarios
### Functional Tests
- System-generated post created automatically on class completion
- User-generated post with media appears in feed after processing pipeline completes
- Global feed shows posts from all users; student feed shows only owner's posts
- Thumbs up interaction updates aggregate count in feed_entity_metrics
- Unliking a post sets interaction.active = false and decrements count
- Nested comment successfully created with correct parent_type and parent_id

### Performance & Security Tests
- Feed scroll loads pre-computed Redis view in <100ms
- Post Creation Lambda processes 20 messages within batch window
- Private student posts are not visible to other students' feed requests

### Edge Cases
- Post creation Lambda receives duplicate SQS message — idempotency check prevents duplicate post
- S3 media processing fails — post creation queued but no media_url available
- View Generation Lambda triggered for a post that was deleted — graceful skip required
- Redis cache evicted while user is mid-scroll — fallback DB query needed

## Async Jobs & ETL
- **Process Content Lambda** — S3-triggered, media transformation pipeline, enqueues to SQS
- **Post Creation Lambda** — SQS consumer, batches of 20 messages or 30-second window
- **View Generation Lambda** — SQS consumer, batches of 100 events or 30-second window (currently disabled)
- **SQS Queues**: Post creation queue, View generation queue
- **Redis**: Pre-computed feed views refreshed by View Generation Lambda
