---
lesson: Pagination
module: 01 — APIs and Integration
tags: tech
difficulty: working
prereqs:
  - 01.01 — What is an API: pagination is a pattern used in almost every API response that returns a list
  - 01.04 — Rate Limiting & Throttling: page size limits and rate limits are two defenses against the same abuse vector
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-student-bulk-installments-get.md
  - technical-architecture/infrastructure/zoom-demo-class-report-1.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-07
---
I don't see any content between the markdown delimiters in your request. The section appears to be empty:

```
---

---
```

Please provide the actual lesson content you'd like me to reformat, and I'll apply the scannability transformations according to your rules (comparison tables, blockquote callouts, warning alerts, company cards, etc.).
# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The page that worked perfectly in testing

**The Scenario**

The PM had spent two weeks building an admin dashboard displaying:
- Student name
- Account status
- Last active timestamp
- Account balance

**In Testing:** Loaded in <1 second with 12 test accounts

**In Production:** 45-second spin, then timeout error

---

**What Went Wrong**

| Layer | Problem | Impact |
|-------|---------|--------|
| **Database** | API query fetched all 40,000 student records simultaneously | Database strain |
| **Network** | Single response packet contained entire dataset | Network bottleneck |
| **Browser** | Attempted to render 40,000 rows at once | Browser crash |

---

**The Root Cause**

> **Pagination:** A technique that divides large datasets into smaller, manageable chunks (pages) loaded on-demand, rather than fetching and displaying the entire dataset at once.

The dashboard never implemented pagination. The test environment had 12 accounts. Production had 40,000.

---

**The PM's Questions**

**"Why didn't we test this?"**

*What this reveals:* Test data volume often doesn't reflect production scale. A passing test with 12 records masks failures with 40,000.

**"What's pagination?"**

*What this reveals:* The PM didn't know a fundamental scaling technique existed—a gap between product thinking and technical constraints.

## F2. What it is — what the library analogy misses

> **Pagination:** The practice of splitting a large set of results into smaller chunks and sending one chunk at a time.

### The Library Analogy

Imagine a library with 40,000 books. When someone asks "what books do you have?" you don't wheel out every book at once. Instead:

- Hand them the catalog for the first 20 books in the section they want
- Tell them: "come back when you want the next 20"
- The books don't move—only the window of what they're viewing changes

**API pagination works the same way.** Instead of returning all 40,000 records in one response, it returns 20 (or 50, or 100)—a "page"—and includes a marker the client can use to request the next page.

### Key Terms

| Term | Definition |
|------|-----------|
| **Page size** | How many records come back per request. "We use a page size of 50" means each API call returns 50 records. |
| **Offset pagination** | The classic approach. "Skip the first 100 records, give me the next 20." Works like numbered pages in a book—you can jump to page 5 directly. |
| **Cursor pagination** | A more robust approach. Instead of saying "skip 100," the API returns a bookmark (cursor), and you say "give me the 20 records after this bookmark." You can't jump to a specific page, but results are stable even when new data is added. |

## F3. When you'll encounter this as a PM

| Scenario | What happens | Your role |
|----------|--------------|-----------|
| **Building any list screen** | Students, orders, transactions, search results, user management—any collection of records needs pagination. Engineers will either add it inconsistently or skip it (shipping the timeout problem). | Specify pagination in the PRD before engineering starts |
| **During a performance incident** | "API is timing out" or "page is slow to load" — classic incident pattern. Root cause: usually a query with no page size limit that worked fine with 100 records but can't handle 50,000. | Recognize pagination as a root cause; prevent via upfront requirements |
| **Stakeholder asks "export all records"** | ⚠️ **The pagination trap.** Export-all is a *separate* engineering problem from display pagination. A 100,000-row export needs a background job, not a bigger page size. | Clarify that pagination ≠ bulk export; route export requests to the data team |
| **Engineer says "we should add pagination"** | You have a design decision to make. | Ask: cursor or offset? What page size? What does the API return when there are no more records? |
| **Mobile app is slow or draining battery** | Over-fetching data on mobile (returning 500 records when the screen shows 10) causes slow load times and battery drain. | Right-size page limits based on mobile constraints; smaller page sizes = better mobile performance |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that pagination splits results into chunks delivered one page at a time.
# ═══════════════════════════════════

## W1. How pagination actually works — the full mechanics

### Quick Reference

| Concept | Definition |
|---------|-----------|
| **Offset pagination** | Request specifies how many rows to skip (`offset`) and how many to return (`limit`) |
| **Cursor pagination** | Request specifies a unique reference point (cursor) and direction; database finds position by record identity |
| **Page metadata** | Response includes `total`, `hasNextPage`, `nextCursor`, and other navigation signals |

---

### 1. The server receives a list request with parameters

A paginated API call looks like this:

```
GET /api/students?limit=20&offset=0
```

| Parameter | Meaning |
|-----------|---------|
| `limit=20` | Return 20 records per page |
| `offset=0` | Start from position 0 (the beginning) |

Subsequent requests increment offset: `offset=20`, then `offset=40`, etc.

> **Offset pagination:** The most common pagination type; client requests a starting position and page size.

---

### 2. The database executes a bounded query

**Without pagination:**
```sql
SELECT * FROM students
```
Fetches the entire table — slow and expensive.

**With pagination:**
```sql
SELECT * FROM students ORDER BY created_at DESC LIMIT 20 OFFSET 0
```

The database scans the table, skips the first `offset` rows, and returns the next `limit` rows. On properly indexed tables with small offsets, this executes quickly.

---

### 3. The API response includes navigation metadata

A well-designed paginated response includes more than just data:

```json
{
  "data": [ ... ],
  "pagination": {
    "total": 40000,
    "page": 1,
    "limit": 20,
    "hasNextPage": true
  }
}
```

**Why PMs need to understand this:** The metadata you request determines the UX you can build — page numbers require `total` and `page`; infinite scroll requires `hasNextPage` or a cursor.

---

### 4. Offset pagination breaks at large offsets

**Problem 1: Performance degradation**

`OFFSET 39980` does not skip directly to row 39,980. The database:
1. Scans through the first 39,980 rows
2. Discards them
3. Returns the next 20

At large offsets, this is nearly as slow as fetching everything.

**Problem 2: Record drift**

If a new record is inserted between a user's page 1 and page 2 requests:
- Every existing record shifts down by one position
- The user may see a **duplicate** (same record on both pages)
- The user may **miss a record entirely**

---

### 5. Cursor pagination fixes both problems

Instead of tracking position by row number, cursor pagination uses a unique value from the last record returned — typically an ID or timestamp:

```
GET /api/students?limit=20&after=student_id_1234
```

**Database query:**
```sql
SELECT * FROM students WHERE id > 1234 ORDER BY id ASC LIMIT 20
```

| Advantage | How it works |
|-----------|------------|
| **Instant position lookup** | `id` is indexed; database finds cursor instantly — no scanning |
| **No record drift** | Position tracked by record identity, not row number; new inserts don't cause duplicates or skips |
| **Consistent results** | Works correctly even if data changes between requests |

**Tradeoff:** You cannot jump to page 50 directly. Navigation is forward-only (or backward if the API supports it).

> **Cursor pagination:** Tracks position by record identity rather than row number; eliminates drift and scales to large datasets.

---

### 6. Page size is a product decision, not just a technical one

Page size affects three dimensions simultaneously:

| Dimension | Large pages | Small pages |
|-----------|-------------|------------|
| **Response time** | More data per request = slower requests | Faster per-request, but more round trips |
| **Mobile impact** | Over-fetches = drains battery and data plan | Respects user's data and battery constraints |
| **UI design** | Numbered pages need total count | Infinite scroll works better with cursor pagination |

Choose page size by understanding your users' context — not just what's fastest on the server.

---

### 7. "No more pages" must be communicated clearly

The API must provide a defined signal for "you've reached the end."

**Common patterns:**

```json
// Pattern 1: Boolean flag
{ "data": [ ... ], "hasNextPage": false }

// Pattern 2: Null cursor
{ "data": [ ... ], "nextCursor": null }

// Pattern 3: Empty array
{ "data": [] }
```

**Why this matters:** Without a clear end-of-data signal, the client doesn't know when to stop requesting pages. Users see loading spinners that never resolve.

## W2. The decisions pagination forces

### Quick Reference
| Decision | Consumer/Feed UIs | Admin/Internal Tools |
|---|---|---|
| **Offset vs. Cursor** | Cursor (stable, no drift) | Offset OK if data is bounded |
| **Page size** | 20–50 | 50–100+ |
| **Total count** | Skip it | Include if UI shows it |

---

### Decision 1: Offset or cursor?

| | Offset pagination | Cursor pagination |
|---|---|---|
| Best for | Admin dashboards, small datasets, numbered-page UIs | Feeds, infinite scroll, mobile apps, large datasets |
| Jump to page | Yes — `OFFSET = (page - 1) × limit` | No — forward-only (or bidirectional with extra complexity) |
| New data during browsing | Causes drift (duplicates or skipped records) | Stable — new records don't affect existing cursors |
| DB performance at large offsets | Degrades — scans all prior rows | Constant — uses index to find cursor position |

> **PM default:** If the list is a feed, a timeline, or anything with real-time updates — **cursor**. If it's a bounded admin table where the data is stable and total count matters (e.g., "showing records 41–60 of 200") — offset is acceptable.

---

### Decision 2: What page size?

| | Small page (10–25) | Medium page (50–100) | Large page (200+) |
|---|---|---|---|
| Best for | Mobile first views, preview lists | Admin dashboards, search results | Data-heavy internal tools, bulk processing |
| Round trips | More — higher latency on slow networks | Balanced | Fewer — but larger responses |
| Risk | User waits for next page too often | — | Memory pressure, mobile data cost, slow initial load |

> **PM default:** 20 is a safe default for most consumer-facing lists. Ask the engineer what the current default is — if there's no default at all, that's the bug.

---

### Decision 3: Should the API expose total count?

**The trade-off:**
- **Pro:** Useful for pagination UI ("page 3 of 2,000")
- **Con:** Requires `COUNT(*)` query every load — on large tables, this can be as slow as fetching the data itself

**When it matters:**
- **Feeds & infinite scroll:** Total count is irrelevant — skip it
- **Admin tools:** "Page 3 of 2,000" provides useful context — cost may be justified

> **PM default:** Don't ask for total count unless the UX explicitly shows it. Confirm with the engineer whether the count query is optimized (or cached) before shipping a paginated list that shows totals.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **Are we using offset or cursor pagination — and why was that chosen?** | Whether the choice was intentional or the default. Offset on a large, fast-moving dataset (like an activity feed) is a reliability problem waiting to emerge as the dataset grows. |
| **What happens if a new record is created while a user is paginating through the list?** | Whether offset pagination is causing drift. If the answer is "they might see a duplicate or miss a record," this is a known limitation. For feeds and financial data, that's unacceptable. For a static admin list, it may be tolerable. |
| **What's the current maximum page size — is there a limit enforced server-side?** | Whether the endpoint can be abused. An API with no page size cap can be called with `limit=100000`, which is a denial-of-service vector and a performance bomb. The bulk installments API in our system had no batch size limit — 10 IDs generates ~50 database queries; 1,000 IDs generates ~5,000 queries. |
| **At what record count does our current pagination approach start degrading?** | The break point for offset pagination. `OFFSET 10000` on a table with no index means 10,000 row scans per request. If the table has 500,000 rows and no one has stress-tested offset=490000, there's a latency cliff waiting in production. |
| **What does the API return to signal end of list — and does the client handle it?** | Whether infinite scroll or "load more" has a stopping condition. If the client doesn't handle `hasNextPage: false` correctly, it will keep making empty requests forever. |
| **What's our page size for mobile vs. web — are they the same?** | Whether mobile performance has been considered. A page size of 100 that works fine on desktop can cause noticeable load time and data usage on 4G. Mobile apps often need smaller pages with faster first-paint. |
| **Is there any list in the system currently fetching all records with no pagination?** | The "admin dashboard bug" waiting in production. Every team has at least one endpoint that was built without pagination because the dataset was small at the time. The zoom demo class monitoring dashboard in our system had this exact pattern — per-class API calls in a loop with no pagination on the outer query. |
| **If someone tries to export all 40,000 records, what happens today?** | Whether export is handled as a background job or as a very large page request. These are fundamentally different engineering problems. If someone can trigger a 40,000-row export through the same endpoint as the display list, you have a performance and security problem. |

## W4. Real product examples

### Stripe — Cursor pagination as API design standard

**What:** Built cursor-based pagination into core API using `starting_after` and `ending_before` parameters on every list endpoint
- Default limit: 10
- Maximum limit: 100

**Why it worked:**
- Stripe's API serves financial products where data integrity is critical
- Offset drift causes duplicate charges → support tickets and trust problems
- Cursor pagination eliminates drift entirely
- Explicit 100-record maximum prevents abuse
- Became the industry reference standard

**PM takeaway:** When specifying a new list API, audit against the Stripe pattern:
- ✓ `limit` parameter
- ✓ `starting_after` (cursor parameter)
- ✓ `has_more` in response

If your API returns a list without a cursor parameter, ask why.

---

### Instagram — Cursor pagination to fix feed drift and mobile battery

**What:** Migrated main feed from offset-based to cursor-based pagination (2013)
- Cursor: timestamp of last post seen

**Why it worked:**
- Instagram feed changes every few seconds
- **Offset pagination problem:** New viral post pushes everything down → users see posts appear twice mid-scroll
- **Cursor pagination solution:** Anchors each scroll session to exact post seen last
- Secondary benefit: Fewer redundant DB row scans = measurably lower battery drain on mobile

**PM takeaway:** Real-time or frequently-updated lists (feeds, notifications, activity logs) will fail with offset pagination at scale. Drift problems appear in support queue before engineering catches them.

---

### Edtech platform — Bulk API with no pagination, no batch limit

**What:** Built bulk student installment status API with:
- No maximum batch size enforced
- No pagination
- 4–6 individual DB queries per student ID

**What broke:**
| Input size | Database queries | Result |
|---|---|---|
| 10 student IDs | ~50 queries | Normal |
| 1,000 student IDs | ~5,000 queries | Connection pool saturation → timeouts across unrelated services |

Same pattern in demo class monitoring dashboard: loop of individual API calls per class, no pagination on outer query.

**PM takeaway:** Internal APIs without pagination are a time bomb. For every bulk endpoint, ask: "What's the maximum input size?" If the answer is "whatever the caller sends," the spec is incomplete.

---

### Twitter/X — Cursor pagination for timeline stability

**What:** Moved home timeline to cursor-based pagination anchored by tweet ID (not time offset)
- Cursor: ID of last tweet seen in current session

**Why it worked:**
- Twitter timeline updates continuously
- **Offset pagination problem:** High-engagement tweet appears between scroll sessions → next batch skips or repeats tweets
- **Tweet ID cursor solution:** User always continues from exactly where they left off

**PM takeaway:** For feeds with recency-based sort and continuous new records, use the natural sort key as cursor (tweet ID style) rather than timestamp cursors. IDs are guaranteed unique; timestamps can collide.

---

### Salesforce — Hard row limits and the enterprise integration trap

**What:** Enforced hard SOQL query limit of 2,000 records per API call
- Every REST API list request must paginate
- No way to fetch >2,000 records in one call
- Uses `nextRecordsUrl` cursor for continuation

**Why it matters for enterprise PMs:**
Enterprise B2B products frequently sync with Salesforce (accounts, contacts, opportunities). A team building CRM integration that assumes "give me all accounts" will:
1. Hit the 2,000-record wall
2. Break the sync
3. Retrofit cursor-based iteration in production
4. Discover this in QA with a 50,000-account customer (not the 200-account test tenant)

**PM takeaway:** Before writing any integration spec for enterprise systems (Salesforce, Workday, SAP, HubSpot), read the pagination limits. Enterprise APIs almost always have hard limits. Integration design must iterate through pages — never assume single-call returns everything.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands offset vs. cursor tradeoffs, page size decisions, and drift.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Pattern 1: No pagination on internal APIs until the table grows

**The Problem:**
Internal APIs often ship without pagination because "it's internal, nobody's sending 10,000 IDs." Until someone does.

| Aspect | Reality |
|--------|---------|
| **What happens** | No page size enforcement, no cursor, no total count cap |
| **Timeline** | Works for ~18 months |
| **The breaking point** | Scheduled job hits endpoint with every student ID in database |
| **Cascade effect** | DB connection pool saturates → three other services timeout |

**Why this happens:** Internal tools accumulate technical debt precisely because they lack the external scrutiny that consumer-facing APIs receive.

**PM prevention role:** Any API that accepts an array or returns a list needs a documented maximum page size **before it ships**. This belongs in the API spec, not the post-incident review.

---

### Pattern 2: Client-side pagination masquerading as server-side pagination

**The Problem:**
Fetch all records from the API, store them in memory, paginate the UI with JavaScript. It looks like pagination. It doesn't solve the performance problem.

| What the PM sees | What's actually happening |
|------------------|--------------------------|
| ✅ Feature demo works | API returns 40,000 records on every page load |
| ✅ Pages load in sequence | Only the display is chunked; all data loaded upfront |
| ✅ Pagination appears functional | 5MB+ of JSON transferred per page load |

**PM prevention role:** When pagination is demoed in QA:
1. Open Network tab
2. Load first page
3. Ask: **"What does the API return — the full dataset or one page?"**
4. If first page load is 5MB+ of JSON, it's client-side.

---

### Pattern 3: Infinite scroll without a stopping condition

**The Problem:**
Client calls `GET /feed?after=cursor_X` → receives `hasNextPage: true` with 20 results → passes cursor back → repeats until `hasNextPage: false`. If the server never returns `false` (bug), the client loops forever.

| Scenario | Outcome |
|----------|---------|
| **Happy path** | Server eventually returns `hasNextPage: false` |
| **Bug state** | Server never returns `false` |
| **Client behavior** | Generates infinite empty API requests |
| **When discovered** | User reaches end of finite list (not visible in QA testing) |

⚠️ **Why testing misses this:** There's always data during QA. The bug only emerges when a user reaches the actual end of a finite list.

## S2. How this connects to the bigger system

### Rate Limiting (01.04)

| Mechanism | Scope | Purpose |
|-----------|-------|---------|
| Rate limits | Requests per second | Cap request frequency |
| Page size limits | Data per request | Cap data volume per call |

⚠️ **Critical:** Neither mechanism alone prevents abuse. A caller with a high rate limit but no page size cap can still trigger 5,000 DB queries in one request. **Both must be enforced on list endpoints.**

---

### Idempotency (01.05)

| Pagination Type | Idempotent? | Behavior with New Data |
|-----------------|-------------|----------------------|
| Cursor-based | ✓ Yes | Same cursor always returns same results |
| Offset-based | ✗ No | New inserts shift which records appear at given offset |

> **Idempotency:** A property where repeated identical requests produce the same result without side effects.

**Why this matters:** When APIs are called by retry-capable clients (background jobs, payment processors), cursor pagination's idempotency is a **correctness guarantee, not just a performance optimization.**

---

### Webhooks vs. Polling (01.03)

Pagination is fundamentally a polling mechanism — the client repeatedly requests the next batch.

**Common pattern for event streams:**
- **Webhooks** deliver new events in real time
- **Pagination + cursors** let clients catch up on historical events without missing any

**The cursor benefit:** Prevents both gaps and duplicates across the two delivery paths.

---

### Databases and Query Performance (Module 02)

Pagination performance depends entirely on the underlying indexes.

| Cursor Field | Index Status | Query Complexity | Performance |
|--------------|--------------|------------------|-------------|
| `id` (primary key) | Indexed | O(log n) | Fast |
| `last_active_at` | No index | O(n) | Slow on large tables |

**Before approving a pagination design for large tables, ask:** "Is the cursor field indexed?"

*Note: The PM doesn't write indexes, but should validate this assumption before sign-off.*

## S3. What senior PMs debate

### Infinite scroll versus numbered pages

| Dimension | Infinite Scroll | Numbered Pages |
|-----------|-----------------|-----------------|
| **Metric impact** | ↑ Time-on-surface, content exposure | ↑ Task completion, user control |
| **Spatial awareness** | None ("Where am I?") | High ("I was on page 4") |
| **Re-orientation time** | High when returning | Low when returning |
| **Best for** | Content discovery, feeds | Task-oriented lists, specific records |
| **Typical choice reason** | Default feed pattern | Intentional design |

**The debate:** Infinite scroll optimizes session-level engagement metrics while degrading task completion and user control. Most teams default to infinite scroll for feeds, then apply it to contexts where numbered pages would perform better.

---

### Internal API pagination

> **The conventional view:** Internal APIs are engineering decisions, not PM decisions.

> **The counterargument:** The bulk installment API without a page size cap caused a production incident affecting students in 12 countries—and the PM owned the feature.

**The actual debate:** Not whether PMs should understand SQL, but whether PM-owned APIs should have *documented input limits as a product requirement*.

| Team approach | Outcome |
|---------------|---------|
| Pagination as non-functional requirement ("engineering will handle it") | Consistent timeout incidents |
| Pagination as documented requirement ("what's the maximum batch size?") | Prevents production failures |

**Key question before handoff:** What's the maximum batch size?

---

### AI inference APIs: inverted pagination

> **Traditional pagination:** Client requests data in batches (chunked reads — cursor → page size → termination)
> 
> **Streaming AI responses:** Server sends tokens as generated (chunked writes — cursor → batch size → [DONE] event)

**The inversion:** Instead of asking "what page size should the *client* request," senior PMs building AI products ask "what token batch size should the *server* flush."

| Decision type | Impact | Ownership |
|---------------|--------|-----------|
| Token batch size | Perceived responsiveness | UX |
| Token batch size | Infrastructure cost | Performance |

**The concept is identical. The direction is inverted.**