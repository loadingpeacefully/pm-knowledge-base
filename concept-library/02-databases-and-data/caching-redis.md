---
lesson: Caching (Redis)
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 02.01 — SQL vs NoSQL: caches sit in front of databases; understanding SQL/NoSQL clarifies what's being cached
  - 02.03 — Transactions & ACID: transactions commit to the database but NOT to the cache; stale cache after a committed update is the most common correctness bug
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/etl-and-async-jobs/feed-post-creation-etl.md
  - technical-architecture/infrastructure/infra-monitoring.md
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

## F1. The teacher who deleted a post that wouldn't disappear

**The situation:**
A teacher posted a class update with an error. Students saw it. The teacher deleted it immediately. One hour later—students were *still* seeing it.

**What happened:**

| Component | Behavior | Result |
|-----------|----------|--------|
| Database | Post record deleted ✓ | Deletion registered |
| Redis cache | Still held old feed view | Post remained visible |
| Invalidation mechanism | None existed | No way to update cache without waiting |
| Cache TTL expiration | Hours to complete | Post finally disappeared after full rebuild |

> **Time to Live (TTL):** The duration a cached item remains valid before expiring and triggering a refresh from the source.

**The core tradeoff:**

| Dimension | Cache Benefit | Cache Cost |
|-----------|--------------|-----------|
| **Speed** | Feed loads in <100ms | — |
| **Freshness** | — | Serves stale data until TTL expires |
| **Complexity** | Pre-built feed view | No deletion mechanism existed |

The Redis cache made the feed fast. But it didn't know about the deletion. It served what it had stored—accurately and quickly—until told otherwise.

---

**The inverse failure:**

A CRM system managing customer deals has **no caching** on read paths. Every request:
- Loads a deal or customer profile
- Calls the database directly
- Makes synchronous calls to external services

**Result:** Average response time of **1.26 seconds**

Sales team members wait 1+ seconds per customer record—across hundreds of daily interactions.

*Engineering flag:* "CRM APIs averaging 1.2–1.3s response times — no caching or async offload."

---

**The pattern:**

These two failures occupy opposite ends of the same spectrum:

- **Over-caching:** Aggressive caching without invalidation = stale data visible to users
- **Under-caching:** No caching at all = unacceptable latency on every request

Both break user experience. Both require different solutions.

## F2. What it is — the whiteboard outside the library

### The Core Concept

> **Database:** The complete store of all data — every student record, every payment, every post. Requires navigation and retrieval time for answers.

> **Cache:** A fast data store that holds recently computed or frequently accessed data, so the application doesn't have to fetch from the slower primary store on every request.

The **database** is the library. It has everything — every student record, every payment, every post. But to get an answer, you have to walk inside, navigate the stacks, pull the book, and read the relevant page. For a complex query, that takes time.

The **cache** is a whiteboard outside the library door. A librarian has already answered the most common questions and written the answers on the whiteboard. When a visitor arrives with a frequent question — "What are the 20 most recent posts in the global feed?" — the answer is already on the whiteboard. No trip inside required. The visitor gets their answer in seconds.

⚠️ **The Critical Weakness:** The whiteboard doesn't update itself. If the librarian goes inside and discovers a book was removed, the whiteboard still shows the old answer until someone erases it and writes the new one.

### Redis in Production

**Redis** is the most widely used cache in production systems. It stores data in memory — RAM — which makes reads and writes roughly **100× faster** than disk-based databases. Redis is the whiteboard: it lives in memory, answers common questions instantly, and holds answers until they expire or are explicitly updated.

### Essential Caching Terms

| Term | Definition |
|------|-----------|
| **Cache hit** | The application asks the cache for data and the cache has it. Request served from cache. Fast. |
| **Cache miss** | The cache doesn't have the data (expired, never cached, or invalidated). Application fetches from database, stores in cache, serves response. Slower than a hit. |
| **TTL (Time to Live)** | How long a cached value is kept before automatically expiring. TTL of 300 seconds = 5 minutes. Next request after expiry is a cache miss. |
| **Cache invalidation** | Explicitly removing or updating a cached value when underlying data changes. The hardest problem in caching — root cause of deleted-post bugs. |

## F3. When you'll encounter this as a PM

### Team recommends "add a cache" to fix a slow page
**Trigger:** Page or API endpoint is slow due to database queries or external API calls.

**Your question:**
- What data are we caching?
- What's the TTL?
- What happens to users when the cache is stale?

---

### Users report seeing outdated data
**Examples:**
- Student sees a post that was deleted
- Price shows the old rate after a promotion ended
- Class shows as available after it was cancelled

*What this reveals:* Stale cache bugs — the underlying data changed but the cache wasn't invalidated.

**Your question:**
- What's the invalidation strategy for this cached data?

---

### Engineering flags a missing TTL
**Trigger:** Infra-monitoring runbook documents: "Redis TTL not enforced uniformly — caused a caught but unexpected cache error."

⚠️ **Risk:** A cached value without a TTL lives forever — until the Redis instance runs out of memory or the key is explicitly deleted. "Forever cache" is almost always wrong.

**Your question:**
- Why isn't there a TTL on this?
- What's the expected freshness window?

---

### New feature needs data that was previously static
**Scenario:** Feature adds real-time pricing, live inventory, or live seat counts — data that was previously safe to cache for a long time.

*What this reveals:* Adding a new cached dependency — or tightening the TTL of an existing one — changes the freshness/performance tradeoff.

**Your question:**
- Does this feature require the cache to reflect updates faster than the current TTL?

---

### Post-incident report cites "cache stampede"
**What happens:** Many cached keys expire simultaneously and every request hits the database at once. Under high traffic, this can bring the database down.

⚠️ **Risk:** Database overload from simultaneous cache misses.

**Your question:**
- Do we have TTL jitter configured to spread expirations?
- Is there a fallback if the cache is cold?
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that a cache stores frequently accessed data in a fast store to avoid expensive database queries; knows cache hit, cache miss, TTL, and cache invalidation.
# ═══════════════════════════════════

## W1. How caching actually works — the mechanics that matter for PMs

### Quick reference
- **Cache-aside pattern:** Application checks cache, falls back to database on miss
- **TTL:** Automatic expiration timer; prevents stale data accumulation
- **Invalidation:** Choose between lazy (TTL), event-driven (write-through), or pre-computation
- **Memory limits:** Configure eviction policy to match your use case
- **Cold start risk:** Pre-warm cache before high traffic arrives

---

### 1. The cache-aside pattern — the most common caching model

```
Request arrives
        │
        ▼
Check cache (Redis) for key
        │
    ┌───┴───┐
  Hit       Miss
    │           │
    ▼           ▼
Serve from    Fetch from DB
cache         or external API
                  │
                  ▼
            Store result in cache (with TTL)
                  │
                  ▼
            Serve response
```

> **Cache-aside pattern:** The application explicitly checks the cache before every expensive operation, populates on miss, and invalidates on update. The database remains the source of truth; the cache is a read-optimized copy.

**Why this pattern resilient:**
- If Redis is down, the application falls back to the database
- Response is slower, but the system continues working

---

### 2. TTL — the expiry clock on every cached value

> **TTL (Time-To-Live):** An automatic expiration timer on every cached value. When the TTL expires, Redis removes the key and the next request becomes a cache miss.

**TTL choices and their consequences:**

| TTL | Behavior | When to use |
|---|---|---|
| 10–60 seconds | Very fresh data; frequent DB reads | Seat counts, live inventory, balance gates where stale = wrong |
| 5–15 minutes | Acceptable staleness; significant DB reduction | User profiles, class schedules, feed rankings |
| 1–24 hours | Long-lived data; changes rarely | Product catalogs, curriculum content, reference data |
| No TTL | Key lives forever (until eviction or explicit delete) | Almost never correct — creates "ghost data" bugs |

⚠️ **Operational hazard:** Missing TTL causes keys to grow stale indefinitely. The cache fills with old data, and eviction eventually removes it without warning. Infra-monitoring flagged this as Medium-severity: "Redis TTL not enforced uniformly — caused a caught but unexpected cache error."

---

### 3. Cache invalidation patterns — the hard part

Three approaches with different tradeoffs:

#### TTL-only (lazy expiration)
Data becomes stale during the TTL window. No invalidation logic required.

**Correct for:** Feed rankings, recommendation scores, non-financial counts  
**Wrong for:** Balances, seat availability, prices

#### Event-driven invalidation (write-through)
When the database is updated, explicitly delete or update the corresponding cache key.

**Advantage:** Cache is always fresh after a write  
**Tradeoff:** Creates a window where the key is deleted and cache is cold until the next read

**Correct for:** Prices, availability, account balances

#### Pre-computation
Compute the result once and cache the computed view instead of caching raw data and computing on read.

**Example — feed system:** The View Generation Lambda computes feed rankings and stores the rendered list in Redis. Feed reads never touch the database; they serve from the pre-computed view.

**Tradeoff:** The pre-computation job must run on every update that changes the view. If disabled, the view goes stale indefinitely.

---

### 4. Redis data structures — what PMs should know

Redis isn't just a key-value string store. Different data types serve different use cases:

| Redis type | What it stores | PM use case |
|---|---|---|
| String | Any value: JSON blob, serialized object | User session, cached API response, feature flag value |
| Hash | Field-value pairs (like a row) | User profile, product attributes |
| List | Ordered sequence | Activity feed, recent events, queue |
| Sorted set | Members with scores, ordered by score | Leaderboards, feed rankings |
| Pub/Sub | Message channel | Real-time notifications, cache invalidation events |

**Example — feed ranking:**  
The platform feed uses a sorted set: each post is a member, the ranking score is its value. Redis returns the top N members by score in O(log N) time — much faster than sorting millions of rows in a database query on every feed load.

---

### 5. Memory limits and eviction — what happens when Redis is full

Redis runs in memory. Memory is finite. When Redis reaches its memory limit, it must evict keys to make room. The eviction policy determines which keys are removed:

| Policy | Behavior | When to use |
|---|---|---|
| `allkeys-lru` | Evict least recently used keys across all keys | General-purpose caching — safe default |
| `volatile-lru` | Evict LRU only from keys with TTL set | When some keys must never be evicted (session store + cache mixed) |
| `volatile-ttl` | Evict keys with shortest TTL first | When freshness matters more than recency |
| `noeviction` | Reject new writes when memory is full | Correct for session stores that must not lose data; wrong for pure caches |

⚠️ **Feed system risk:** If Redis fills up and `noeviction` is configured, new feed views can't be stored — the system fails to update cache at all.

---

### 6. Cache warming — the cold start problem

When a cache is empty (new deployment, Redis restart, cache flush), every request is a cache miss. All requests fall through to the database simultaneously. Under high traffic, this can overwhelm the database before the cache warms up.

**The solution — cache warming:**  
Pre-populate the cache with the most frequently accessed keys before traffic arrives.

**For the feed system:**  
Pre-compute the top feed views during deployment, before the new instance starts serving traffic.

---

### 7. What not to cache

Caching adds complexity. Not every slow operation should be cached.

| Don't cache | Why |
|---|---|
| Write operations | Writes must persist to the database; caching a write means the data may not survive a Redis restart |
| Financial balance gates | If the cache is stale, a user may schedule a class they don't have credits for |
| Small, fast queries | If the DB query is already <10ms, the cache adds operational complexity without meaningful performance gain |
| Data that changes on every write for every user | Cache hit rate would be near 0%; the miss path is slower than no cache |

## W2. The decisions caching forces

### Quick Reference
| Decision | Default Rule |
|----------|--------------|
| **TTL duration** | Short (10–60s) for access gates; Medium (5–15m) for profiles/rankings; Long (1–24h) for static data only |
| **Invalidation strategy** | TTL-only for rankings; Event-based for deleted/moderated content; Never cache access decisions |
| **What to cache** | Raw data for simple lookups; Computed views for expensive operations |

---

### Decision 1: TTL duration — how much staleness is acceptable?

> **PM default:** Decide TTL by asking: "What's the worst thing that happens if a user sees data that's N seconds old?" If the answer is "they make a wrong decision" (overbooking, double-spending) — short TTL or event invalidation. If the answer is "they see slightly old rankings" — medium TTL is fine. **Data that gates access goes to the database directly; never serve access gates from cache.**

| Dimension | Short TTL (10–60s) | Medium TTL (5–15 min) | Long TTL (1–24h) |
|-----------|-------------------|----------------------|------------------|
| Data freshness | Near-real-time | Acceptable lag | Static/reference data only |
| DB load reduction | Low | Significant | Maximum |
| Stale data risk | Minimal | Moderate | High — must have event-based invalidation |
| DB queries per minute (at 100 req/s) | 100–600 misses/min | 7–20 misses/min | Near 0 misses/hour |
| **Best for** | **Counters gating access: seats, credits, balances** | **Profile data, rankings, content** | **Product catalog, curriculum, reference data** |

---

### Decision 2: Cache-aside vs write-through invalidation

> **PM default:** For rankings and counts — TTL-only is fine (slight staleness acceptable). For deleted or moderated content, event-based invalidation is required — **stale deleted content is a trust issue, not just a UX issue**. For any data driving financial or access decisions, don't use the cache at all — read from the database directly.

| Dimension | Cache-aside with TTL | Write-through (invalidate on write) |
|-----------|----------------------|-------------------------------------|
| When cache is updated | When TTL expires | When data is written to DB |
| Implementation complexity | Low — no write-path changes | Medium — write path must also update/delete cache key |
| Staleness window | Full TTL duration (e.g., 5 minutes) | Near-zero — cache reflects DB within milliseconds of write |
| Failure mode | Stale reads until TTL expires | Missed invalidation = permanent stale key (until TTL or explicit fix) |
| **Best for** | **Data that updates infrequently or stale data is acceptable** | **Data that drives user-visible decisions or moderation state** |

---

### Decision 3: What goes in the cache — raw data vs computed views

> **PM default:** The feed pre-computed view is the right pattern for a social feed because the ranking algorithm is expensive to run on every scroll. The cost: you must keep the View Generation Lambda running and handle post deletion explicitly. **A disabled View Generation Lambda means rankings stop updating — PM must track this as a correctness issue, not just a performance issue.**

| Dimension | Cache raw data (DB row) | Cache computed view (pre-rendered result) |
|-----------|-------------------------|-------------------------------------------|
| Best for | Simple lookups: user profile, session token | Complex results: feed ranking, recommendation list, dashboard summary |
| Read complexity | App must assemble the full response from cached parts | App serves cache directly — no assembly required |
| Invalidation scope | Invalidate one key when one record changes | Invalidate the view when any contributing record changes |
| Cache size | Small per key | Large per key — stores computed result |
| **Default** | **Single-entity lookups read frequently** | **Expensive computations worth pre-computing** |

## W3. Questions to ask your engineer

### Quick Reference
| Question | Red Flag | Green Flag |
|----------|----------|-----------|
| TTL on cached data? | Arbitrary or disconnected from business need | Deliberately set based on acceptable staleness window |
| Cache invalidation strategy? | "TTL will eventually expire it" | Explicit invalidation tied to data writes |
| Redis down — what happens? | "We're not sure" | Fallback to database with measured latency impact |
| Cache hit rate? | Unknown or <50% | Monitored; >90% for high-traffic, 60–70%+ for varied data |
| Financial/gating data cached? | Yes, using stale cache for access decisions | Never; read directly from DB for gates, cache for display only |
| Memory & eviction policy? | Undersized; eviction not monitored | Sized for data volume; eviction rate alerting active |
| Keys without TTL? | Yes, accumulating indefinitely | Every key has TTL; persistent data refreshed on access |

---

**1. What's the TTL on this cached data, and why?**

*What this reveals:* Whether TTL was set deliberately based on the data's acceptable staleness window, or arbitrarily.

- **TTL too long:** Risks serving stale data that drives incorrect user decisions  
- **TTL too short:** Reduces cache hit rate to near-zero; adds complexity without performance benefit  
- **Ideal answer:** Connects TTL to business requirement — "User profile TTL is 10 minutes because profile data changes rarely, and a 10-minute delay after a name change is acceptable."

---

**2. What's the cache invalidation strategy when this data changes?**

*What this reveals:* Whether the team has thought through what happens when underlying data is updated.

| Scenario | Insufficient | Sufficient |
|----------|--------------|-----------|
| Deleted content, changed prices, updated availability | "TTL will eventually expire it" | "When a post is deleted, we call Redis DEL on the feed view keys that contained that post" |

⚠️ **Risk:** If the answer is "TTL will eventually expire it," ask whether product has deliberately accepted the staleness window.

---

**3. What happens to the user experience if Redis is down?**

*What this reveals:* Whether there's a fallback strategy in place.

- **Failure:** No fallback → feature is down  
- **Success:** Fallback to database → response slower but functional  
- **Ideal answer:** "We fall back to the database. Response time increases from ~50ms to ~300ms, but the feature continues working."  
- **Red flag:** "We're not sure" means the failure mode hasn't been tested

---

**4. What's the cache hit rate in production?**

*What this reveals:* Whether the cache is actually providing value.

- **Low hit rate (20%):** Cache adds latency on miss path without meaningfully reducing DB load  
- **Target hit rates:** 
  - High-traffic feed: >90%  
  - User profile cache with many unique users: 60–70%  
- **Unknown hit rate:** No one is monitoring whether the cache is working

---

**5. Is any financial or access-gating data being served from the cache?**

*What this reveals:* Whether there's a correctness risk.

⚠️ **Risk scenario:** Student's credit balance served from stale cache → balance used to approve/deny class booking → student takes class without sufficient credits.

| Use Case | Cache Acceptable? | Rationale |
|----------|-------------------|-----------|
| Display only (e.g., showing balance on dashboard) | ✅ Yes | Stale display is acceptable |
| Access gate (e.g., checking if student can book) | ❌ No | Must read from DB to prevent fraud/error |

**Ideal answer:** "We read balances directly from the database for any check that gates access. Cache is used only for display."

---

**6. What's the memory configuration and eviction policy?**

*What this reveals:* Whether the team has sized Redis for the expected data volume and chosen eviction policies wisely.

⚠️ **Risk:** If Redis is undersized, keys will be evicted under load — including important session tokens or fresh data.

**Ideal answer:** "We've set a memory limit of X GB, using allkeys-lru eviction. We monitor the eviction rate in New Relic and alert if it spikes."

---

**7. Do any cache keys lack a TTL?**

*What this reveals:* Whether "eternal" keys will accumulate forever.

⚠️ **Risk:** Keys without TTL live until Redis runs out of memory and evicts them — without warning. This was flagged in the infra-monitoring runbook: "Redis TTL not enforced uniformly — caused a caught but unexpected cache error."

**Ideal answer:** Every key has a TTL. If a key must persist longer than TTL, it should be **refreshed on access**, not stored without expiry.

## W4. Real product examples

### Live class platform — pre-computed feed views in Redis

**What they did:** The feed system pre-computes ranked post lists for the global feed and stores them in Redis as sorted sets. When a user loads the feed, the system reads directly from the Redis cache — no database query, no ranking computation at request time. The View Generation Lambda (a background job) is responsible for updating the cached view when interactions occur (thumbs up, celebrate, share, comment).

| Metric | With Cache | Without Cache |
|--------|-----------|---------------|
| Feed scroll load time | <100ms | 500ms–2 seconds |
| Operation | Read pre-computed Redis view | Join posts, count interactions, compute ranking score |

**What broke:** 

⚠️ The View Generation Lambda is currently **disabled**. Rankings are not being updated dynamically.

⚠️ **No documented cache invalidation strategy** for deleted or inactive posts. When a post is deleted from the database, the Redis view still contains it until the TTL expires or the cache is manually cleared — deleted posts remain visible to students during the cache TTL window (Critical/High severity tech debt).

**PM takeaway:** Pre-computed cache views are the right architecture for complex feed ranking. But the view must be kept current: the View Generation Lambda must be running, and there must be an explicit invalidation path for content that is deleted or deactivated. A cache without an invalidation strategy is a deferred correctness bug.

---

### Live class platform — CRM APIs with no caching

**What they did:** The CRM deal management APIs (`/v1/deal/create-db-crm-deal`, `update-crm-deal-to-closed-won`) make synchronous database queries and external service calls on every request. No caching layer exists on the read path. Customer profile data — deal history, student details, contact information — is fetched from the database on every load.

**Current performance:**
- Average response time: **1.26–1.19 seconds per API call**
- Severity flag: High ("CRM APIs averaging 1.2–1.3s response times — no caching or async offload")

**What caching fixes:**

Customer profile data is read dozens of times per day by sales reps but updated only once per deal lifecycle (status changes, new notes). A 5-minute TTL cache on the customer read path would:
- Serve ~95% of requests from Redis at **<20ms**
- Only write operations (deal status update, new note added) hit the database
- Result: 1.26s average → **<50ms for cached reads**, with occasional 1.26s misses on cache expiry (invisible to users)

**Productivity impact:**

| Scenario | Requests/Day | Wait Time | Weekly Loss |
|----------|-------------|-----------|-------------|
| **No cache** | 400 requests × 1.26s | 504 sec/day (8.4 min) | **42 minutes/week** |
| **95% cache hit** | 400 requests × (0.95 × 0.05s + 0.05 × 1.26s) | ~22 sec/day | ~3 min/week |

*At 50 sales reps loading customer records 8 times per day.*

**PM takeaway:** Missing a cache where one is warranted is a product quality issue quantifiable in productivity minutes, not just a performance footnote. The test: "Is this data read far more often than it's written, and does the read time noticeably degrade the user experience?" If yes — it's a PM requirement to specify a cache, not an engineering nice-to-have.

---

### Redis cache error from missing TTL

**What happened:** The infra-monitoring runbook documents: "Redis TTL not enforced uniformly — caused a caught but unexpected cache error." A service attempted to cache a value without including the TTL parameter in the Redis call. Redis returned an error because the call was malformed. The error was caught — it didn't surface to users — but it was unexpected, meaning no monitoring alert existed for it.

**Optimization roadmap (Week 1):**
- Fix Redis cache calls to always include TTL/duration parameter
- Add monitoring alert when a Redis call is made without TTL

**Why it matters:**

⚠️ A missing TTL is a **latent correctness risk**. Without TTL, the key either:
- Lives forever (growing stale)
- Requires explicit deletion (rarely implemented consistently)

A cache key that becomes stale is indistinguishable from a fresh key to the application — until a user makes a decision based on stale data and files a support ticket.

**PM takeaway:** "Fix TTL enforcement" sounds like a backend detail but it's a product reliability requirement. This is a code review gate: every Redis SET call must include an expiry.

---

### Salesforce — per-tenant cache isolation in enterprise B2B SaaS

**What they did:** Salesforce caches customer record data, list views, and report results per tenant. Every cache key is namespaced by organization ID: `org:{orgId}:contact:{contactId}`. Cache invalidation when Tenant A updates a contact only flushes Tenant A's cache keys — Tenant B's cached data is untouched.

**Why it matters for B2B SaaS:**

⚠️ Enterprise customers have **strict data isolation requirements**. A cache miss that accidentally serves one tenant's data to another is a security incident, not a bug.

The per-tenant namespace pattern enables:
- Tenant-level TTL tuning (high-volume enterprise accounts get shorter TTLs; low-volume accounts tolerate longer ones)
- Tenant-level cache flush during data migrations
- Data segregation guarantees for SOC 2 audit compliance

**Performance at scale:**

| Metric | Impact |
|--------|--------|
| Database read load reduction | ~80–90% for list views & contact lookups |
| Cache hit rate for active users | >85% |
| Effective database traffic | Only 15% of what it would be without caching |
| Scale | 150,000+ enterprise customers |

**PM takeaway:** In enterprise B2B SaaS, caching is not just a performance decision — it's a compliance and data isolation decision. Any multi-tenant system caching data must namespace keys by tenant ID and implement per-tenant invalidation. "We cache customer records" without tenant namespace isolation is a SOC 2 finding waiting to happen.

---

### Shopify — product catalog caching at scale

**What they did:** Shopify caches product catalog data — names, prices, inventory status, images — in Redis with a TTL of several minutes. Product pages across millions of storefronts are served from cached data. When a merchant updates a price or marks an item out of stock, Shopify uses event-driven cache invalidation: the specific product's cache keys are explicitly deleted, and the next read rebuilds the cache with fresh data.

**Caching strategy:**

| Approach | Trigger | Result |
|----------|---------|--------|
| **TTL expiry** | Minutes pass | Eventual consistency |
| **Event-driven invalidation** | Write operation (price/inventory change) | Immediate update in seconds |
| **Hybrid** | Both together | Fast reads + fresh data on writes |

**Why it works:** Product catalog data is read thousands of times for every one write. The hybrid approach — TTL for eventual expiry + explicit invalidation on writes — ensures prices and inventory update in seconds after a merchant change, not after the TTL expires.

**Performance at scale:**

| Factor | Impact |
|--------|--------|
| Traffic volume | Millions of storefronts, billions of page views/day |
| Product page load time | ~100ms (feasible only with caching) |
| Database footprint | Would be thousands of times larger without Redis caching |

**PM takeaway:** For any catalog-style data (products, curriculum, class schedules, reference data), the pattern is: long TTL for infrequent reads, event-driven invalidation when data changes. The PM's job is to specify the acceptable staleness window for each data type — not to implement the caching, but to give engineering the product requirement that drives the TTL decision.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands cache-aside pattern, TTL, invalidation strategies, Redis data structures, and the pre-computed view pattern.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Cache Stampede — Death by Cold Start

> **Cache Stampede:** Thousands of requests simultaneously miss the cache when many keys expire at the same time, overwhelming the database before the cache can repopulate.

**What happens:** When cache keys share the same TTL (often from a deployment that flushes the cache), they all expire simultaneously. Every request in that window becomes a cache miss, sending thousands of database queries at once.

**Trigger:**
- Deployment that flushes the cache
- Batch of keys set with identical TTL values

**PM prevention role:**

| Action | Details |
|--------|---------|
| **Standard mitigation** | TTL jitter — add random variation (±10–30%) to TTL values so keys expire at different times |
| **Implementation effort** | One-line code change |
| **Launch review question** | "Do we have TTL jitter configured? What's the warm-up plan if the cache is cold after deployment?" |

---

### Stale Cache as Trust Destruction

> **Stale Cache Risk:** When moderated or deleted content remains visible due to unexpired cache, users lose trust in the platform's integrity.

**The real impact:** A student seeing a deleted answer, inappropriate material, or a pricing mistake believes the platform failed its core responsibility. The technical explanation ("cache TTL hadn't expired yet") doesn't matter — this is a trust event, not a UX bug.

**Severity varies by data type:**

| Data Type | Impact | Mitigation |
|-----------|--------|-----------|
| **Financial data** | Critical — wrong prices destroy trust | No caching OR event invalidation required |
| **Moderated/deleted content** | High — trust destruction | Event invalidation required |
| **Rankings/counts** | Acceptable — user can refresh | TTL is sufficient |

**PM prevention role:** Classify cached data by staleness impact at feature design time, not after an incident. Ask: "What's the worst thing that happens if this cached value is wrong?"

---

### The "Application Handles It" Assumption About Redis Failures

⚠️ **Risk:** Teams assume Redis is always available and don't implement fallback behavior.

> **Redis Unavailability:** Cluster failures, network partitions, and memory exhaustion cause Redis to be offline for minutes at a time — but the database remains available.

**Failure mode:** If the application treats Redis unavailability as fatal (throws 500 errors instead of falling back to the database), the feature goes down whenever Redis fails — even though the database is working.

**PM prevention role:** Make graceful degradation a launch requirement question, not a post-incident investigation.

| Acceptable Fallback | Unacceptable |
|-------------------|--------------|
| Fall back to DB with increased latency | 500 error |
| Serve cached response with staleness warning | Application crash |
| Return degraded feature (subset of data) | Feature unavailable |

**Launch checklist question:** "What's the graceful degradation behavior when Redis is unavailable?"

## S2. How this connects to the bigger system

### Transactions & ACID (02.03)

| Scenario | Cache Behavior | Database Behavior | Risk Level | Rule |
|----------|---|---|---|---|
| Display (balance shown to user) | Holds pre-transaction value until expiry/invalidation | Updated immediately on commit | Low | Cache acceptable |
| Access gates (can student schedule?) | Says "no credits" | Says "30 credits" | ⚠️ **High** | Use database for gates |

**The issue:** Redis is not a participant in database transactions. When a transaction commits, the cache retains stale data until it expires or is explicitly invalidated.

**When it matters most:** Correctness-critical decisions (access control, authorization) require the source of truth (the database), not the performance layer (the cache).

---

### Indexing (02.02)

Both caching and indexing solve speed problems—but at different layers:

| Approach | Mechanism | Speed Gain | Best Used When |
|----------|-----------|-----------|---|
| **Indexing** | B-tree lookup in database | Full table scan (~seconds) → lookup (~milliseconds) | Query is logically necessary |
| **Caching** | Redis read (skip DB entirely) | Database query → cache hit (~microseconds) | Indexed query is still too slow |

**The sequence matters:**
1. Add indexes first
2. Add caching only if indexed queries remain slow

⚠️ **Cache stampede risk:** Caching a slow query without indexing means every cache miss still hits a slow query—and under a stampede, thousands of slow queries execute simultaneously.

---

### Pagination (01.07)

> **Offset-based pagination:** `LIMIT 20 OFFSET 40` generates a unique query per page. Each page combination = different cache key = low hit rates.

> **Cursor-based pagination:** Uses a stable cursor to fetch the same page. Same cursor = same cache key = high hit rates.

**For cached feeds:** Cursor-based pagination is necessary to make caching effective. The same page of results returns from the same Redis key on every request.

---

### Third-Party Integration Patterns (01.10)

External APIs (Zoom, Salesforce, WhatsApp) are high-value caching candidates:

- **Slow:** 100–500ms per call
- **Rate-limited:** Quota restrictions apply
- **Infrequently changing:** Read frequency >> write frequency

**Caching examples:**
- Zoom room links for the duration of a class session
- Salesforce customer details for 15 minutes

**Invalidation strategy:**

| Data Type | TTL | Reasoning |
|-----------|-----|-----------|
| Availability, pricing | Short TTL | Changes frequently |
| User identity, room configuration | Long TTL | Stable, rarely changes |

## S3. What senior PMs debate

### Cache-aside vs write-through vs write-back: which pattern is actually correct?

| Pattern | How it works | Consistency guarantee | Trade-off |
|---------|--------------|----------------------|-----------|
| **Cache-aside** | Defer to database as source of truth | Eventual consistency | Staleness window accepted |
| **Write-through** | Update cache on every write | Near-real-time consistency | Added latency + complexity on writes |
| **Write-back** | Write to cache first, flush async | Highest write performance | Data loss risk if cache fails before flush |

> **The real debate:** This isn't purely technical—it's about what the product guarantees to users. Cache-aside accepts eventual consistency as the product contract. Write-through promises consistency at throughput cost.

**Right answer depends on the feature:**
- **Social feed** → eventual consistency works
- **Inventory counter** → immediate consistency required

⚠️ **PM-level risk:** Most teams default to cache-aside (simplest), then discover specific features requiring write-through. Adding write-through to a cache-aside system requires retrofitting write paths.

**What this reveals:** Senior PMs should push for an explicit staleness contract at feature design time, not after the first stale-data support ticket.

---

### Redis as a session store and as a cache in the same cluster — operational risk or pragmatic efficiency?

> **The tension:** Session data (auth tokens, login state) must never be evicted. Cache data (feeds, catalogs) should be evicted under memory pressure. These are opposite requirements.

**What happens if you mix them:**
- Same eviction policy (LRU) works for cache but breaks sessions
- Users logged out mid-session during traffic spikes = P0 incident

**The pragmatic answer:**
- Use separate Redis clusters *or* separate keyspaces with different eviction policies

**The timing decision (PM call):**

| Scale stage | Acceptable? | Why |
|-------------|------------|-----|
| Startup | Maybe | Operational overhead of second cluster is high |
| Platform | No | Session eviction incident is P0; risk outweighs savings |

**What this reveals:** Most teams make this separation decision after their first session eviction incident rather than before. Senior PMs should force the decision upfront.

---

### Vector caches and semantic similarity: AI is changing what "caching" means

> **New problem:** Traditional caches miss when query text changes slightly, even if semantically identical. "What classes does my child have this week?" and "show me my kid's upcoming sessions" are the same question—different strings.

**Vector caching solves this:**
- Stores query embeddings, not exact query text
- Returns cached results for semantically similar queries
- Uses cosine similarity to find matches
- Approximate caching: result computed for *similar* query, not exact query

**Performance gains for read-heavy AI features:**
- Semantic search
- Recommendation explanations
- FAQ answering
- **Typical impact:** 40–60% reduction in LLM API calls without meaningful quality loss

**PM questions for AI features (2025):**

1. What's the acceptable staleness window for the AI response?
2. What's the acceptable semantic distance before we call the model again?

**What this reveals:** Vector caching applies the same staleness-vs-latency trade-offs as traditional caching, but operates on embeddings instead of exact strings.