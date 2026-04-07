---
lesson: Indexing
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 02.01 — SQL vs NoSQL: indexes exist in both SQL and document databases; understanding table structure is required
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/rm-effectiveness-student-performance.md
  - technical-architecture/infrastructure/zoom-demo-class-report-1.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-07
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The dashboard that broke at 9 AM

**The Incident**

Monday morning. Fifty live demo classes started simultaneously. The operations team opened the "Current Running Classes" dashboard to monitor who had joined, when teachers arrived, and whether any class had errors.

The dashboard took **eight seconds to load**. By the time it finished, two classes had started without the ops team knowing a teacher had connected late.

---

### What Went Wrong

**The Root Cause**

The engineers found the cause the same afternoon:

| Component | Details |
|-----------|---------|
| **Data sources** | Two database tables: class metrics (join times) + class errors (technical issues) |
| **Query method** | Both filtered by class ID ("give me data for class 7823") |
| **Critical gap** | Neither table had an index on the class ID column |

**The Performance Impact**

Without an index, the database had no choice:

1. Read **every row** in both tables (hundreds of thousands of historical entries from months of classes)
2. Check each row individually to see if it matched class 7823
3. Repeat for 50 simultaneous queries = 100+ full table scans
4. Result: Dashboard loaded in 8 seconds instead of under 1 second

> **Term:** Index — A database lookup structure that allows direct retrieval of rows matching a condition, instead of scanning every row sequentially.

---

### The Solution

**What changed:** Two lines of SQL  
**Time to deploy:** 15 minutes  
**The instruction:** "Build a lookup structure for the class ID column so you can jump directly to matching rows"

**Impact:** Next Monday morning, the dashboard loaded in under 1 second.

---

### The Missed Opportunity

The two lines of optimization code had been in the roadmap for **three months**.

Nobody had prioritized them.

## F2. What it is — the book index

Imagine a 600-page textbook on education research. You need to find every mention of "student engagement." Without an index: start at page 1, read every page, mark the relevant ones. With an index at the back of the book: look up "student engagement" in alphabetical order, find page numbers 43, 127, 245, 389, go directly there.

A database **index** works the same way. When a table has millions of rows and a query asks "find all rows where class_id = 7823," the database has two choices:

| Approach | Method | Performance |
|----------|--------|-------------|
| **Full table scan** | Read every row, check if it matches | Slow on large tables |
| **Index lookup** | Use pre-built lookup structure to jump directly to matching rows | Fast, especially at scale |

The index is that pre-built structure. The database builds it and maintains it automatically — but only for columns you tell it to index.

### Key terms

> **Index:** A pre-built lookup structure for a column. Like the index at the back of a book, but updated automatically as data changes.

> **Full table scan:** When the database reads every row to answer a query, because no index exists for the column being searched. Fast on small tables. Very slow on large ones.

> **Cardinality:** How many distinct values a column has. A column with high cardinality (unique IDs, email addresses) benefits greatly from an index. A column with low cardinality (a status column with 3 possible values) benefits less — the database may still scan most of the table even with an index.

> **Query plan:** The database's step-by-step strategy for answering a query. When engineers say "EXPLAIN this query," they're asking the database to show its plan — which tells them whether it's using an index or doing a full table scan.

## F3. When you'll encounter this as a PM

### API slowness after data growth
A feature works perfectly in testing and the first weeks after launch. Three months later, it's timing out. The table now has 2 million rows instead of 10,000. Queries that were instant at 10,000 rows now take seconds because they're reading 2 million rows.

**Root cause:** Missing index on the searched column

**Why it's tricky:** Slowness appears gradually, not all at once — which is why it's often missed until users complain.

---

### Operations dashboard lag
Internal dashboards — class monitoring, CRM pipelines, support queues — often have no index-related performance requirements set during development.

| Scale | Status |
|-------|--------|
| 200 records | Works fine |
| 200,000 records | Breaks |

**First engineering question:** Which queries are slow and whether they're missing indexes?

---

### New filter features without indexed columns
Every filter a user can apply in your product maps to a WHERE clause in a database query.

**Examples:**
- "Show me all orders from last week" → filters on `created_at`
- "Show me all students with missed classes" → filters on `missed_class_count`

⚠️ **If the filtered column has no index:** Every new filter option is a potential performance problem at scale.

---

### Engineer mentions "we need to add an index before we ship"
This is a good sign — the engineer has thought about query performance.

**Your job:** Understand the timing and risk profile.

| Scenario | Risk | Action |
|----------|------|--------|
| Index added before launch | Low | Proceed |
| Index retrofitted to production table with millions of rows | High | Brief performance degradation likely during index creation |

---

### Missing index appears in post-incident reports
A missing index is a one-line fix that should have been in the original schema design.

**What to investigate:**
- Was it a table that grew faster than expected?
- Was it a query pattern that wasn't anticipated?

*What this reveals:* These questions help prevent the same failure in the next service.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that an index is a pre-built lookup structure that prevents full table scans; that missing indexes cause queries to slow as data grows.
# ═══════════════════════════════════

## W1. How database indexes actually work — the mechanics that matter for PMs

### Quick Reference
| Concept | Use Case | Key Tradeoff |
|---------|----------|--------------|
| Single-column index | Filter on one column | Low overhead, limited coverage |
| Composite index | Filter on multiple columns together | Order matters; leftmost column is entry point |
| B-tree (default) | General queries, range queries | O(log n) lookups |
| Hash index | Exact equality only | Fast equality, no range queries |
| Full-text index | Text search in long strings | Specialized, not general-purpose |
| GIN/GiST | JSON, arrays, geometric data | PostgreSQL-specific |
| Partial index | Subset of rows (e.g., critical errors only) | Smaller, faster to maintain |

---

### The full table scan — why it's expensive

Query example: `SELECT * FROM class_errors WHERE classId = 7823`

**Without an index:**
- Database reads all 5 million rows sequentially
- Roughly 1 million rows per second for typical disk reads
- Result: **5 seconds per query**

**At development scale (10,000 rows):** 10ms — invisible.  
**At production scale (months later):** Millions of rows accumulated, query becomes slow.

*What this reveals:* Indexing bugs often surface late because the symptom (slowness) only appears at scale, not during QA.

---

### How a B-tree index works

> **B-tree:** A balanced tree structure where each node contains index values and pointers to the next level, down to actual row locations.

**Lookup mechanism:**
- Database traverses the tree, eliminating half the remaining values at each step
- **Complexity:** O(log n)
- **Example:** Finding 1 value in 1 million rows ≈ 20 steps (vs. 1 million full scans)
- **At 100 million rows:** Roughly 27 steps

**Range query support:**
- Values are sorted, so `WHERE created_at BETWEEN start AND end` works efficiently
- Database finds the start, then reads sequentially to the end

---

### Composite indexes — indexing multiple columns together

> **Composite index:** An index on multiple columns together, enabling efficient filters on all indexed columns simultaneously.

**Example scenario:**  
Student performance cron: `WHERE studentId > :lastProcessed AND created_at > :cutoffDate LIMIT 1000`

| Index Type | Handles Both Conditions? | Efficiency |
|------------|--------------------------|-----------|
| Index on `studentId` only | ❌ Must evaluate `created_at` separately | Partial |
| Index on `created_at` only | ❌ Must evaluate `studentId` separately | Partial |
| Composite on `(created_at, studentId)` | ✅ Jumps directly to matching rows | Full |

**Order matters — leftmost column is the entry point:**
- Index on `(created_at, studentId)` helps:
  - ✅ Queries filtering on `created_at` alone
  - ✅ Queries filtering on both columns
- Index on `(created_at, studentId)` does NOT help:
  - ❌ Queries filtering on `studentId` alone (sorted structure starts with `created_at`)

---

### The write tradeoff — indexes cost on every write

> **Index write cost:** Every INSERT, UPDATE, and DELETE must update every index on that table.

**Calculation example:**
- Table with 5 indexes
- 1 INSERT = 1 row write + 5 index writes = **6 total writes**
- High write volume = measurable degradation in write throughput

**Strategy by workload type:**

| Workload Type | Read Pattern | Write Pattern | Index Strategy |
|---------------|--------------|---------------|-----------------|
| Reporting/dashboards | Frequent, heavy reads | Rare writes | More indexes OK |
| Search results | Thousands of reads/sec | Rare writes | Heavily indexed |
| Event logs | Rarely queried | Millions of appends/day | Minimal indexes |
| Activity streams | Rarely queried | High write volume | Minimal indexes |
| Payment transactions | Rarely queried | High write volume | Minimal indexes |

---

### The query planner — how the database decides which index to use

> **Query planner (optimizer):** The database component that estimates the cost of different query approaches and chooses the cheapest.

**Three planner behaviors that matter for PMs:**

1. **Low cardinality → full table scan may be cheaper**
   - If an index covers only 40% of the table (e.g., status column with "active"/"inactive")
   - Random row lookups cost more than sequential scan
   - Planner may skip the index entirely

2. **Outdated statistics → wrong plan chosen**
   - Planner's estimate of table size becomes inaccurate
   - Engineers fix this with `ANALYZE` (PostgreSQL) or `ANALYZE TABLE` (MySQL)
   - Impact: Queries that worked fast can suddenly slow down

3. **Multi-column filters need composite indexes**
   - Planner can only use one index per table per query condition in most cases
   - Complex `WHERE` clauses with multiple columns require composite indexes to run efficiently

---

### Index types beyond B-tree

| Index Type | Best For | Pros | Cons |
|------------|----------|------|------|
| **B-tree** (default) | General-purpose, range queries | Fast equality and range lookups | — |
| **Hash** | Exact equality (`WHERE id = X`) | Faster than B-tree for pure equality | No range queries |
| **Full-text** | Text search (`WHERE description CONTAINS 'error'`) | Handles searching long strings | Not for general queries |
| **GIN/GiST** (PostgreSQL) | JSON, arrays, geometric data | Flexible attribute queries | PostgreSQL-specific |
| **Partial** | Subset of rows (`WHERE severity = 'critical'`) | Small, fast to build and maintain | Only covers filtered rows |

**Partial index example:**  
`CREATE INDEX ON class_errors (classId) WHERE severity = 'critical'`
- Indexes only critical errors (most queries filter on critical anyway)
- Smaller and faster to maintain than indexing all rows

---

### Adding indexes to production tables — the operational risk

⚠️ **Production risk:** Adding an index to a multi-million-row table requires reading the entire table and building the index structure. This can take **minutes to hours**.

**Lock risk varies by database:**

| Database | Behavior | Safe for Production? |
|----------|----------|----------------------|
| PostgreSQL 9.1+ | `CREATE INDEX CONCURRENTLY` builds index without write locks (slower but safe) | ✅ Yes (with CONCURRENTLY) |
| MySQL | `ALTER TABLE ... ALGORITHM=INPLACE` for some operations | ⚠️ Check version/config |
| Older PostgreSQL | Locks table for writes during build | ❌ Production outage |

**Impact:** Any feature writing to that table experiences downtime during the index build.

**Best practice:** Catch missing indexes during original schema design rather than adding them in production.

## W2. The decisions indexing forces

### Decision 1: Which columns to index?

| | Index this column | Don't index this column |
|---|---|---|
| **Best for** | Columns used in WHERE clauses, JOIN conditions, ORDER BY clauses for large tables | Columns rarely queried; columns with very low cardinality (2–3 distinct values) |
| **Cardinality** | High — unique IDs, emails, timestamps | Low — boolean flags, status enums with few values |
| **Query frequency** | High — used in critical path API responses | Low — used only in rare admin queries |
| **Table size** | Large — millions of rows | Small — tables with a few thousand rows never benefit meaningfully |

> **PM default:** Every foreign key column should have an index. Every column used in a WHERE clause on a high-traffic query on a table that grows should have an index. These are the two rules that catch 80% of missing index problems.

---

### Decision 2: How many indexes — read performance vs write performance?

| | Few indexes (1–3 per table) | Many indexes (5+ per table) |
|---|---|---|
| **Best for** | Write-heavy tables: event logs, activity streams, transaction logs | Read-heavy tables: search, dashboards, reporting tables |
| **Write impact** | Minimal overhead per INSERT/UPDATE | Measurable throughput reduction at high write volume |
| **Read coverage** | Targeted queries are fast; others may still scan | Most query patterns covered |
| **Maintenance** | Low — fewer structures to maintain and rebuild | Higher — more structures to update on schema changes |

> **PM default:** Index by evidence, not by anticipation. Add an index when a specific query is proven slow — not preemptively on every column you think might be queried someday.

---

### Decision 3: Add the index before launch or after?

| | Index before launch | Index after launch (to production table) |
|---|---|---|
| **Risk** | None — table is empty or small | ⚠️ High if table is large — index build locks table or degrades performance during build |
| **Data available** | No — can't profile real query patterns yet | Yes — can use query logs to find the actual slow queries |
| **Cost to fix** | Trivial — add to schema migration | Non-trivial — requires `CREATE INDEX CONCURRENTLY` or maintenance window |
| **Discovery method** | Engineering review of query patterns | Slow query logs, EXPLAIN output, monitoring alerts |

> **PM default:** Foreign key indexes belong in the initial schema. Other indexes can be added reactively — but only with a plan for how to build them on a production table without causing an outage.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **Which columns are in the WHERE clauses of the most frequently-called queries for this table?** | The index coverage gap. If the most frequent query filters on `classId` and `classId` has no index, every execution of that query is a full table scan. The answer should include the query volume estimate — a query called 10 times per day with no index is a different priority than one called 10,000 times per day. |
| **What does EXPLAIN show for this query?** | Whether the database is using an index or doing a full table scan. `EXPLAIN` output includes "Seq Scan" (full table scan — slow at scale) or "Index Scan" (using an index — fast). If an engineer runs EXPLAIN on a slow query and sees "Seq Scan" on a large table, the diagnosis is clear. PMs don't need to read EXPLAIN output, but knowing it exists means the PM can ask for it as a diagnostic. |
| **Is there an index on every foreign key column in this table?** | Whether the most common join and filter patterns are covered. Foreign keys are almost always used in WHERE clauses and JOIN conditions. A foreign key column with no index is a near-guaranteed performance problem once the table grows beyond a few hundred thousand rows. |
| **How many rows are in this table today, and what's the expected growth rate over 12 months?** | The urgency of adding missing indexes. A table with 50,000 rows and no index on a query column has no visible performance problem today. The same table with 5 million rows and no index has an 8-second query. Knowing the growth trajectory tells the PM whether this is a this-sprint fix or a this-month fix. |
| **Is this query in the user-facing critical path, or a background job?** | How to prioritize the fix. A slow query in the user-facing path (an API response the user is waiting for) is a product quality issue. A slow query in a background job (a cron that runs every 30 minutes) is an operational concern — slower but not user-visible. Both need fixing, but user-facing queries are higher priority. |
| **If we add an index to this table now, how will we do it without locking the table?** | Whether the engineer has a production-safe plan. On PostgreSQL, `CREATE INDEX CONCURRENTLY` adds the index without locking writes. On MySQL, `ALTER TABLE ... ALGORITHM=INPLACE` is safer than the default. If the engineer says "we'll just run ALTER TABLE during off-peak hours," ask how long the operation takes on this table size and what happens to writes during that window. |
| **Are there any queries that sort on a non-indexed column?** | A hidden index gap. ORDER BY on an unindexed column forces the database to sort the full result set in memory before returning it — which can be slower than even a full table scan on large result sets. Indexes on ORDER BY columns are as important as indexes on WHERE columns for query-intensive features like dashboards and sorted lists. |

## W4. Real product examples

### Demo class monitoring — missing indexes cause ops failure under load

**What they did:**
Built a real-time dashboard showing all active demo classes, teacher join status, student attendance, and class errors. The dashboard queries two tables per class:
- `demo_class_metrics` (join times)
- `class_errors` (error records)

Both filtered by `classId`.

**Why it broke:**

| Condition | Testing | Production |
|-----------|---------|-----------|
| Table size | 5 classes, small tables | 50 simultaneous classes, hundreds of thousands of historical rows |
| Query performance | Milliseconds | 8+ seconds (vs. 2-second target) |
| Index status | Missing on `classId` | Full table scans on 100+ per-class queries |

Neither `demo_class_metrics.classId` nor `class_errors.classId` had a database index. The indexes were documented in the Week 1 optimization roadmap but deprioritized.

**What happened:**
Both indexes were added in a fifteen-minute deployment. The next Monday morning with 50 simultaneous classes, the dashboard loaded in under one second. Queries that had been scanning hundreds of thousands of rows now completed in single-digit milliseconds.

**PM takeaway:**
⚠️ Performance testing at **10× expected production load**, not development load, is the only way to discover missing index problems before launch. A table that's fast with 10,000 rows may be unusable with 1 million rows. Require engineers to run load tests and EXPLAIN analysis on any dashboard or API that queries tables with unbounded growth.

---

### Student performance pipeline — compound index on the cursor query

**What they did:**
A cron-triggered Lambda runs every 30 minutes to collect performance data for up to 1,000 students active in the last 30 days. The query uses cursor-based pagination:

```
WHERE studentId > :lastProcessed 
  AND created_at > :cutoffDate 
ORDER BY studentId 
LIMIT 1000
```

This runs 48 times per day across a `paid_classes` table that grows by tens of thousands of rows monthly.

**Why indexing matters here:**

| Index Type | Coverage | Result |
|------------|----------|--------|
| Single-column index on `studentId` | Covers cursor condition only | Still requires sequential scan for date filter |
| Composite index on `(created_at, studentId)` | Covers both conditions simultaneously | Database jumps directly to matching rows |

At 48 cron runs per day with 1,000 students each, the difference between a covering composite index and a single-column index compounds into minutes of daily compute time.

**PM takeaway:**
⚠️ Cursor-based pagination — the performance-correct alternative to offset pagination — only maintains its performance advantage when the cursor column is indexed. An unindexed cursor column turns cursor pagination into the same full table scan problem as offset pagination. **Always confirm that the pagination cursor column has an index.**

---

### Slack — composite index on (team_id, channel_id, timestamp) for message search

**What they did:**
Slack's message database is queried with near-identical patterns millions of times per day: "get all messages in channel X for team Y, sorted by timestamp." Built a composite index on `(team_id, channel_id, timestamp)` to cover the exact query pattern.

**Index design:**
- **team_id** first (highest cardinality discriminator) — eliminates 99%+ of rows immediately
- **channel_id** next — eliminates most of the rest
- **timestamp** last — handles range filter and sort without additional sort step

**Why it worked:**
The composite index covers the exact query pattern without requiring the database to scan across multiple single-column indexes. Message queries that would take seconds on an unindexed table complete in single-digit milliseconds at trillion-row scale.

**PM takeaway:**
For any high-frequency query that filters on multiple columns, the composite index column order should match the query's filter priority — **highest-cardinality discriminator first**. This is an engineering design decision made once in the schema that determines query performance for the lifetime of the product.

---

### Shopify — covering indexes to eliminate table lookups entirely

**What they did:**
Shopify processes millions of orders per day with dashboards surfacing order counts, statuses, and summaries by merchant. Uses a covering index on merchant dashboards:

> **Covering index:** An index that includes not just the indexed columns but also the columns the query needs to return — allowing the database to answer the query entirely from the index without touching the main table.

Example: Index on `(merchant_id, status, created_at)` **includes** `order_total` — so "get all orders for merchant X with status Y, sum of totals" never reads the main orders table.

**Why it worked:**

| Lookup Type | Process | I/O Cost |
|-------------|---------|----------|
| Standard index | Find rows in index → fetch columns from main table | Higher |
| Covering index | Answer query entirely from index structure | 40–60% reduction |

At Shopify's transaction volume, the difference is measurable in infrastructure cost and response time.

**PM takeaway:**
For dashboard and reporting features that run the same query pattern thousands of times per day, covering indexes are worth discussing with your engineering team. They're a **targeted optimization for known, stable query patterns** — not a general solution.

**Ask your team:** "Is this query in the critical path, and can we cover it with an index that includes the output columns?"
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands B-tree indexes, composite indexes, and the read/write tradeoff.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### "It worked in testing" — the scale gap failure

**The pattern:**
- Query works in staging (50,000 rows) → times out in production (5 million rows)
- Developer never ran `EXPLAIN` analysis
- Missing indexes are invisible at small scale

**Why it happens:**

Database query planners choose between index scan and full table scan based on table size estimates.

| Scale | Operation | Time | Notice? |
|-------|-----------|------|---------|
| 50,000 rows | Full table scan | 50ms | No — below threshold |
| 5 million rows | Full table scan | 5 seconds | Yes — triggers alerts |

**PM prevention role:**

Require load tests and `EXPLAIN` analysis on any new query touching a table expected to grow unboundedly (messages, events, transactions, class records, errors).

| Cost | Scenario |
|------|----------|
| $0 | Running EXPLAIN during development |
| High | Discovering missing index in production incident |

---

### Index explosion on write-heavy tables

**The pattern:**
- Table starts as data store → becomes heavily-indexed reporting source
- Each index addition individually justified ("we need created_at for date filter")
- Cumulative effect: 8 indexes on table processing 10,000 writes/minute
- Write throughput degrades 30–40%

> **Why:** Each INSERT maintains 8 index structures simultaneously instead of just the primary storage.

**The actual problem:**

This is an architectural issue disguised as an indexing issue. The query shouldn't be on the write table at all.

**Correct solutions (in priority order):**
1. Read replica for reporting queries
2. Data warehouse
3. ~~More indexes on write table~~ ❌

**PM prevention role:**

Index additions to high-write tables require explicit write throughput analysis. Ask: Does this query belong on the write table, or should it be served from a read replica or data warehouse?

| Decision Speed | Consequence |
|---|---|
| Fast | Adding an index |
| Slower but critical | Architectural question of which database layer owns the query |

---

### Stale statistics causing the wrong query plan

**The pattern:**
- Database planner relies on table statistics (row counts, value distributions, cardinality)
- Table grows very quickly → statistics become severely outdated
- Planner believes table has 100,000 rows when it has 10 million
- Planner chooses full table scan over available index (underestimates scan cost)

**The symptom:** 
Index exists but database isn't using it. Performance doesn't improve after adding the index.

> **How statistics update:**
> - PostgreSQL: automatic via `autovacuum`
> - Other systems: manual via `ANALYZE`

**PM prevention role:**

When an index doesn't improve query performance, diagnose statistics first:

```
ANALYZE tablename
```

This one-minute step rules out the statistics problem before investigating other explanations.

## S2. How this connects to the bigger system

### SQL vs NoSQL (02.01)

| Aspect | SQL | NoSQL (MongoDB, Firestore) |
|--------|-----|---------------------------|
| Index purpose | Accelerate column queries against known schemas | Accelerate queries on document fields, including nested JSON paths |
| Schema visibility | Visible in database layer | Hidden; schema flexibility can obscure indexing problems |
| Performance failure | Un-indexed columns cause query slowdown | Un-indexed document fields cause same slowdown, harder to diagnose |

**Key insight:** The SQL vs NoSQL choice doesn't eliminate the indexing requirement—it changes the index design problem. Choosing MongoDB for schema flexibility, then querying un-indexed document fields, produces the same performance failure as un-indexed SQL columns, just harder to diagnose.

---

### Pagination (01.07)

> **Cursor-based pagination:** The performance-correct approach for large datasets, using an indexed cursor column with binary search (e.g., `WHERE id > :lastId`) to find the starting point, then returning N rows sequentially.

**Common miss:** Teams switch from offset to cursor pagination to fix performance, but forget to index the cursor column. Without the index, cursor pagination degrades to a full table scan—the same performance problem they were trying to solve.

---

### Caching (02.04)

> **Query caching hierarchy:** The correct sequence is (1) add indexes first (cheap), (2) add read replicas if write/read contention exists (medium cost), (3) add caching only for truly read-heavy, cacheable query patterns (highest operational complexity).

⚠️ **Anti-pattern:** Using caching to hide a missing index problem is technically correct but wasteful—every cache miss hits the slow query, defeating the purpose of caching.

**When caching belongs:** Queries that are too expensive even with correct indexes—either because the table is enormous and the query touches a high percentage of rows, or because the query is called so frequently that even fast index lookups add up.

---

### Data Warehouses vs Databases (02.05)

| Query type | Operational queries | Analytics queries |
|------------|-------------------|-------------------|
| Examples | Point reads, range scans | Cohort analysis, aggregations, cross-table joins for reporting |
| Storage structure | B-tree indexes | Columnar storage |
| Optimization goal | Fast targeted access | Fast full-dataset scans |
| Correct home | Operational database | Analytics database (Redshift, BigQuery, Snowflake) |

**PM's architectural question:** Is a slow analytics query actually a problem with the operational database, or a problem with trying to serve analytics from the wrong tool? Trying to solve analytics performance by adding more indexes to a B-tree-indexed operational database is solving the wrong problem.

## S3. What senior PMs debate

### Automated index recommendations — does the PM still need to care about indexing?

| Aspect | Automated Recommendations | PM-Level Awareness |
|--------|---------------------------|-------------------|
| **When it triggers** | After slow query observed in production | Before launch, during schema review |
| **User impact** | Users experience slowness first | Issues prevented on empty table |
| **Fix complexity** | After millions of rows exist | Trivial when table is empty |
| **Role** | Catches misses | Prevents them |

**Examples:**
- PostgreSQL, CockroachDB, AWS Aurora Performance Insights, Azure SQL — all surface missing index recommendations
- CockroachDB's statement statistics surface index recommendations automatically

*What this reveals:* Automation is reactive; PM expertise is proactive. The question isn't whether tools alert engineers, but whether the PM asks the right questions before production impact.

---

### Partial indexes — the underused optimization senior PMs should know exists

> **Partial Index:** An index covering only rows matching a WHERE condition, reducing size and maintenance cost for tables where most rows are historical or completed.

**Example:**
```sql
CREATE INDEX ON class_errors (classId) WHERE resolved = false
```

**Impact when 99% of rows are resolved:**
- Index size: 1% of full index
- Build time: Proportionally faster
- Query performance: Faster scans on active subset
- Maintenance: Minimal

**Trigger question for PMs:** "What percentage of this table does the typical query touch?"

**Ideal use cases:**
- Class errors (resolved vs. active)
- Expired sessions (active vs. expired)
- Resolved incidents (completed vs. open)

*What this reveals:* Most teams skip partial indexes as "optimization-level detail," but for heavily historical tables, this is an architectural decision that should happen before the table reaches 100 million rows.

---

### Vector indexes — a fundamentally different index problem that PMs building AI products need to understand

> **Vector Index:** An index answering "find the N rows most similar to X" through nearest-neighbor search in high-dimensional space, fundamentally different from traditional B-tree indexing.

| Algorithm | Trade-off | Best For |
|-----------|-----------|----------|
| **HNSW** (Hierarchical Navigable Small World) | Higher build time & memory → near-constant query time | High-volume, low-latency queries |
| **IVF** (Inverted File Index) | Smaller memory footprint → slightly reduced accuracy | Memory-constrained environments |

**Critical for PMs building:**
- Semantic search
- Recommendation systems
- RAG (retrieval-augmented generation) features

**Key question:** Not "is this column indexed?" but **"which vector index algorithm fits this query volume and accuracy requirement?"**

*What this reveals:* Vector indexing is a new dimension of the indexing decision that didn't exist three years ago. It's now on the critical path for any AI-enabled product feature and requires different algorithmic thinking than traditional indexes.