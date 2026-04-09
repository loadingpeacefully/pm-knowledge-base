---
lesson: CDN & Edge Caching
module: 03 — Infrastructure & DevOps
tags: tech
difficulty: working
prereqs:
  - 03.01 — Cloud Infrastructure Basics: CDNs are a distributed layer of cloud infrastructure; understanding regions and edge locations requires knowing what "cloud" means as a foundation
  - 02.04 — Caching (Redis): CDN caching and Redis caching are different layers of the same caching strategy; understanding TTL, cache hits, and invalidation at the application layer maps directly to CDN concepts
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/infrastructure/website-kt-and-docs.md
  - technical-architecture/infrastructure/web-app-optimization-champ.md
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

## F1. The story of a parent in Dubai loading your product

A parent in Dubai opens BrightChamps.com on a Tuesday evening. The marketing page has to load: HTML for the page structure, CSS for the design, JavaScript for interactivity, images of kids in classrooms, a hero video, and translations in Arabic.

**Without a CDN:**

| Factor | Impact |
|--------|--------|
| **Distance** | 2,700 km across undersea cables (origin server in India) |
| **Latency per round-trip** | 200–400 milliseconds |
| **Number of requests** | Dozens for a modern web page |
| **Total load time** | 4–6 seconds |
| **User abandonment rate** | 40% abandon after 3 seconds |
| **Mobile impact** | Significantly worse |

Studies consistently show 40% of users abandon pages that take more than 3 seconds to load. On mobile, the numbers are worse.

### The expansion problem

When BrightChamps launches in the UAE, Saudi Arabia, and Southeast Asia, the first complaint in every new market is identical: "The website is slow." Not because the product is bad — because the bytes are traveling too far.

> **Content Delivery Network (CDN):** A distributed network of servers positioned globally to cache and serve content from locations physically closer to end users, reducing latency and improving page load times.

This is the problem CDNs were built to solve.

### How BrightChamps solved it

BrightChamps' production website (brightchamps.com) already routes every user through AWS CloudFront, a CDN, before requests reach the application server.

**Request flow:**
```
User → CDN (CloudFront) → Next.js → Redis Cache → Google Sheets
```

For the parent in Dubai, the HTML and assets they need are served from a CloudFront edge location in the Middle East — not from India.

| Metric | Without CDN | With CDN |
|--------|-------------|----------|
| **Round-trip latency** | 300ms | 20ms |
| **Page load perception** | Slow | Fast |

---

### What this means for you as PM

**The question that surfaces at every international expansion conversation:** "How fast does the product load in [new market]?"

The engineering answer involves CDN coverage and cache optimization. Your role is:
- Knowing what questions to ask
- Understanding what metrics like "cache hit ratio of 85%" actually mean for user experience
- Connecting infrastructure decisions to user retention and conversion

## F2. What it is — the library warehouse network

**The core idea:** A publisher in Mumbai prints books in one warehouse. A reader in London waits 3 weeks by sea. A reader in Chennai gets delivery in 2 days (closer proximity). A CDN solves this by stocking copies in warehouses near London, New York, Singapore, and Dubai—so every reader gets the nearest-warehouse speed.

---

### Key terms

> **CDN (Content Delivery Network):** A network of servers distributed globally, each storing copies of your content. When a user requests your page, the request routes to the nearest CDN server instead of your origin server.

> **Edge location / Point of Presence (PoP):** The nearby server that stores and serves your cached content.

> **Cache:** The copy of your content stored at an edge location.
> - **Cache hit:** Edge location has the content → fast delivery
> - **Cache miss:** Edge location doesn't have it yet → fetches from origin, stores copy, serves user

> **TTL (Time to Live):** How long the cached copy is kept before the edge server checks the origin for a fresher version.

> **Cache invalidation:** Forcing all edge locations to discard cached copies and fetch fresh content from origin. Typical workflow: push new code → invalidate CDN cache → users get new version.

---

### The TTL tradeoff

| Approach | Benefit | Cost |
|----------|---------|------|
| Long TTL (e.g., 24 hours) | Fast delivery, minimal origin load | Content may be stale |
| Short TTL (e.g., 5 minutes) | Always fresh | Higher load on origin server |

---

### What CDNs are (and aren't) for

**Best for:**
- Static assets (images, CSS, JavaScript bundles, fonts, videos)
- Content that doesn't change per-user
- Content safe to serve from cache

**Not for:**
- User-specific pages
- Authenticated content
- Real-time data

## F3. When you'll encounter this as a PM

### International Launch
**Scenario:** "What's our page load time in [country]?" — the answer depends heavily on CDN PoP coverage in that region. If your CDN has edge locations in Singapore but not in Jakarta, users in Indonesia may be hitting the Singapore node, which is meaningfully slower than a Jakarta node would be.

**PM action:** Before any international launch, ask: "What edge locations does our CDN have in this market, and what's the expected p95 page load time for a user there?" Run a synthetic performance test (tools like WebPageTest let you test from specific cities) before launch, not after.

---

### Stale Content After Deploy
**Scenario:** You deploy a landing page update on Friday afternoon. On Monday, a colleague in Singapore says they're still seeing the old version. This is a CDN cache that wasn't invalidated after the deploy.

**PM action:** Cache invalidation should be part of every deploy checklist. Ask: "Does our deploy process automatically invalidate the CDN cache?" If the answer is "we do it manually," that's technical debt with a real product risk: stale content in production after every deployment.

---

### Website Performance Complaints
**Scenario:** A support ticket says "the website is slow." Before assuming backend issues, ask: "Are we seeing high cache miss rates on the CDN?" A cold cache (after a major cache invalidation or a new PoP region) means users are hitting origin directly — which is slower.

**PM action:** "What's our CDN cache hit ratio?" is a legitimate PM question. 

| Cache Hit Ratio | Health Status |
|---|---|
| Below 70% | ⚠️ Caching configuration problem |
| 70–89% | Acceptable range |
| Above 90% | Healthy for primarily static sites |

---

### Planned Traffic Spike
**Scenario:** A promotional campaign, a press feature, or a product launch drives 10× normal traffic. Without a CDN, that traffic hits origin servers — which may not be provisioned for it. With CDN: most of the surge is served from cache, origin handles only cache misses and dynamic requests.

**PM action:** Before any planned traffic event, ask: "Is the campaign landing page cached at the CDN, and what's the TTL?" A landing page with a 24-hour TTL that was just deployed is protected. A landing page with no CDN caching is exposed to full origin load.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level
# ═══════════════════════════════════

## W1. How CDNs actually work — the mechanics that matter for PMs

> **Quick reference:** Cache hit = instant (5–30ms). Cache miss = slow (100–500ms+). Hit ratio of 70–80% is healthy. Versioned filenames = best invalidation strategy.

### 1. The request lifecycle — cache hit vs miss

> **Cache hit:** Edge location has the file. User gets it directly. Latency: 5–30ms.

> **Cache miss:** Edge location doesn't have the file. Edge fetches from origin, stores locally, serves to user. Latency: 100–500ms+. Next users get cached copy.

**BrightChamps request flow:**
```
User (Dubai)
  → CloudFront edge (Middle East PoP)
       → Cache HIT: serve immediately
       → Cache MISS: fetch from Next.js origin (India)
            → Next.js checks Redis
                 → Redis HIT: serve from cache
                 → Redis MISS: fetch from Google Sheets API
```

Each layer absorbs requests before reaching the next (slower) layer. CloudFront is the outermost and fastest.

---

### 2. What gets cached — static vs dynamic

| Content type | Cache at CDN? | TTL guideline |
|---|---|---|
| **CSS / JS bundles** (hashed filename) | ✅ Yes | 1 year (filename changes on deploy) |
| **Images** (product, marketing) | ✅ Yes | 7–30 days |
| **HTML pages** (marketing/public) | ✅ Yes | 5–60 minutes |
| **HTML pages** (logged-in user) | ❌ No | — bypass cache |
| **API responses** (public data) | ✅ Yes | 1–60 minutes |
| **API responses** (user-specific) | ❌ No | — bypass cache |
| **Videos / large media** | ✅ Yes | 7–30 days |

**Healthy cache hit ratio benchmarks:**

| Content type | Healthy ratio | Low ratio indicates |
|---|---|---|
| Static assets (JS/CSS/images/fonts) | 85–95% | TTL too short, or misconfigured for CDN caching |
| Marketing HTML pages | 70–85% | High deploy frequency or personalization bypassing cache |
| Dynamic API responses | 30–50% | Expected — varies per user; only shared endpoints cacheable |
| **Overall site average** | **70–80%** | Below 60% = CDN misconfiguration |

**Latency impact — what the numbers mean for users:**

| Scenario | Latency | User experience |
|---|---|---|
| Edge PoP in same country (hit) | 5–30ms | **Instant** — imperceptible |
| Edge PoP in adjacent region (hit) | 30–80ms | **Fast** — no delay felt |
| Cache miss → origin (same region) | 50–150ms | **Acceptable** but noticeably slower |
| Cache miss → origin (cross-continent) | 200–500ms | **Noticeable delay** |
| All 20–50 assets uncached, cross-continent | 4–10 sec total | **High abandonment risk** |

**Real impact example:** A 30-asset marketing page (JS, CSS, images, fonts) with each asset taking 200ms longer via origin vs. CDN (cross-continent) = **6 seconds saved per page load**. Improving cache hit ratio from 60% → 85% saves **2.5 seconds** of perceived load time for international users.

**BrightChamps context:**
The student dashboard audit found 4MB of Lottie animation files (including `confetti_animation` at 1.3MB) loaded globally. These are **ideal CDN candidates** — large, static, identical for every user. Serving from edge locations instead of origin saves 1–2 seconds on first page load for international users.

---

### 3. Cache invalidation — why it's hard and what the options are

Cache invalidation is a genuinely hard distributed systems problem. The tension: CDN edges worldwide have cached copies. When origin updates, all edges must discard their copies. CDNs have hundreds of PoPs globally.

| Strategy | How it works | Pros | Cons |
|---|---|---|---|
| **TTL expiry** (passive) | Cached copies auto-expire after X minutes. Edge re-fetches on next request. | Simple; no deploy step | Stale content window of up to TTL duration |
| **Invalidation API** (active) | Call CDN API after deploy to explicitly purge paths. CloudFront: `CreateInvalidation`. Takes 1–5 min to propagate. | Precise control; no stale window after deploy | Must automate in deploy process; easy to forget |
| **Versioned filenames** (immutable) | Embed content hash in filename (`main.a3f2d8.js`). Old filename cached forever (never changes). New deploy = new filename. | Zero stale window; 1-year TTL safe; maximum CDN efficiency | Requires build tooling (Next.js handles this) |

⚠️ **BrightChamps technical debt:** The website-kt docs show a **4-step manual cache invalidation process:**
1. Update data in Google Sheets
2. Trigger AWS Lambda to sync Redis
3. Run Redis cache purge commands
4. Call CDN cache purge API

Marked as **Medium severity:** "Risk of stale content if steps are missed."

⚠️ **PM implication:** Cache invalidation is a **product correctness issue**, not just infrastructure. If marketing updates pricing and CDN cache isn't invalidated, users in Dubai see one price and users in Singapore see another. This is a product incident.

---

### 4. CDN behaviors and routing rules

Modern CDNs (CloudFront, Cloudflare) let you configure **behaviors** — rules controlling how different URL patterns are handled:

```
/*.jpg                  → cache TTL 30 days
/api/*                  → bypass cache (forward to origin)
/dashboard/*            → bypass cache (authenticated)
/static/*               → cache TTL 1 year (versioned filenames)
/*  (default)           → cache TTL 5 minutes
```

A single CDN distribution can handle static assets (long TTL), marketing pages (medium TTL), and API calls (no cache) — each with the right caching behavior.

---

### 5. CDN coverage and latency by region

CDN coverage determines the distance to the nearest PoP — which directly determines latency.

| CDN provider | PoP count | Strong regions | Weak regions |
|---|---|---|---|
| **AWS CloudFront** | 550+ | NA, EU, India, SEA | Africa, Central Asia |
| **Cloudflare** | 300+ | Global (very broad) | Some tier-2 markets |
| **Fastly** | 90+ | NA, EU, APAC | Africa, LatAm |
| **Azure CDN** | 130+ | NA, EU | Africa, SEA |

**BrightChamps uses CloudFront.** Strong coverage in primary markets (India, SEA, Middle East). For expansion to Tier 2 cities or African markets, verify coverage during launch planning.

## W2. The decisions CDNs force

### Decision 1: What TTL strategy for HTML pages?

HTML pages are the hardest CDN caching decision. JS and CSS can use versioned filenames (infinite TTL). Images change rarely. But HTML is the entry point — it references the JS and CSS. If you cache HTML for 1 day, users won't get new features for 24 hours after deploy.

| TTL choice | Pros | Cons | When to use |
|---|---|---|---|
| No cache (TTL 0) | Always fresh | Full origin load for every page view | High-churn content (dashboards, feeds) |
| Short TTL (5–15 min) | Mostly fresh | Stale window exists | Marketing pages with frequent updates |
| Medium TTL (1–6 hours) | Good cache efficiency | Deploy requires manual invalidation | Campaign landing pages |
| Long TTL (24h+) | Maximum CDN efficiency | Must invalidate on every deploy | Stable pages (terms, about) |

> **Recommendation:** Marketing pages should use 5–15 minute TTL (balancing freshness and efficiency) paired with active invalidation on deploy. Static assets (JS/CSS/images) should use versioned filenames with 1-year TTL — the filename changes on each deploy, so caches never need invalidating.

---

### Decision 2: Which pages bypass CDN entirely?

⚠️ **Security risk:** If User A's account page is cached and served to User B, that's a data leakage incident. Authenticated pages require explicit CDN bypass configuration.

| Page type | Cache? | How to implement bypass |
|---|---|---|
| Logged-in dashboard | No | Set `Cache-Control: no-store` header at origin |
| Checkout / payment flow | No | `Cache-Control: no-store` + CloudFront behavior for `/checkout/*` |
| Profile / account settings | No | Bypass rule on `/account/*` |
| A/B test variant | Conditional | Cache default; bypass for variant cookie |

**PM implication:** When adding new authenticated pages to the product, confirm with engineering that CDN bypass rules are configured. A new authenticated page that accidentally gets cached at the CDN is a privacy incident waiting to happen.

---

### Decision 3: What does CDN actually cost — and when does it save money?

CDN pricing is pay-per-byte-transferred and pay-per-request. The numbers are small per unit but add up at scale.

| CDN provider | Data transfer cost | Request cost | Free tier | Best fit |
|---|---|---|---|---|
| **AWS CloudFront** | $0.0085–$0.085/GB (region-tiered; India egress ~$0.085) | $0.0075 per 10k HTTPS requests | 1TB/mo + 10M requests/mo (12 months) | AWS-native stack |
| **Cloudflare** | Flat-fee tiers — Pro $20/mo, Biz $200/mo (bandwidth unlimited on paid plans) | Included in tier | Generous free tier (unmetered bandwidth) | Cost-predictable, early-stage products |
| **Fastly** | $0.08–$0.12/GB | $0.0075 per 10k requests | None | High-performance edge compute |
| **Akamai** | Negotiated enterprise contract | Enterprise pricing | None | Large-scale enterprise |

#### The ROI math for a typical SaaS product

**Scenario:** Mid-scale SaaS serving 100GB/day of static assets (JS, CSS, images, fonts) from AWS origin

| Approach | Monthly cost | Notes |
|---|---|---|
| Without CDN | ~$255 | 100GB × 30 days × $0.085 AWS egress + origin server load (CPU/memory) |
| With CloudFront (85% hit rate) | ~$293 | Origin: $38/mo (15GB/day). CloudFront: ~$255/mo |

**Wait — CDN isn't always cheaper.** The ROI comes from two places:
1. **Reduced origin load** means fewer/smaller origin servers needed
2. **Regional pricing advantages** — CloudFront egress is cheaper than direct EC2/ALB in many regions

For products with global users and heavy static assets, CDN typically reduces total infrastructure cost by **20–40%** while improving performance.

**PM implication:** "What does our CDN cost?" is reasonable to ask. For BrightChamps on CloudFront, the 4-level cache architecture means origin traffic is already minimal — CDN is doing its job (likely under $200/month for website delivery). The more interesting number: **cost of NOT having CDN** in international markets (user drop-off due to slow load, support tickets, failed conversions).

---

### Decision 4: CDN vendor — CloudFront vs Cloudflare vs Fastly

| Factor | AWS CloudFront | Cloudflare | Fastly |
|---|---|---|---|
| Ecosystem fit | Best if already on AWS | Standalone, easy DNS setup | Developer-focused, edge compute strong |
| PoP coverage | 550+ globally | 300+ with very broad Tier-2 | 90+ in major markets |
| Edge compute | Lambda@Edge, CloudFront Functions | Workers (powerful, popular) | Compute@Edge |
| Pricing model | Per-GB transfer + per-request | Flat fee tiers (generous free tier) | Pay-as-you-go |
| DDoS / WAF | Shield Standard/Advanced | Best-in-class included | Available as add-on |
| Best for | AWS-native infrastructure | Simplicity, security, Tier-2 global | High-performance edge compute |

### BrightChamps — CloudFront ✓

**What:** BrightChamps uses CloudFront, not Cloudflare or Fastly.

**Why:** Correct choice given AWS-native infrastructure (Lambda, SQS, S3, RDS all on AWS).

**Takeaway:** Vendor consistency reduces operational overhead and simplifies IAM/security policies.

## W3. Questions to ask your engineer

### Quick Reference
| Question Focus | What It Reveals | Red Flag Answer |
|---|---|---|
| Cache hit ratio | CDN effectiveness | <70% on static content |
| Invalidation process | Deploy reliability | Manual multi-step process |
| Page load (p95) | International UX | >4 seconds |
| CDN bypasses | Security separation | Unapproved authenticated pages cached |
| Origin capacity | CDN dependency risk | Origin sized for cache-miss rate only |
| Large asset caching | Efficiency of big files | Origin-served on every request |
| Bundle cache busting | Static asset strategy | CDN invalidation per deploy |

---

**1. What's our current CDN cache hit ratio, and what does a healthy ratio look like for our traffic pattern?**

*What this reveals:* Whether the CDN is doing its job.

⚠️ **Red flag:** A ratio below 70% on a primarily static marketing site means many requests are hitting origin unnecessarily — either TTLs are too short, too much content is being bypassed, or cache invalidations are happening too frequently.

---

**2. Is cache invalidation automated as part of our deploy process, or is it a manual step?**

*What this reveals:* Reliability of content freshness after deploys.

### BrightChamps — Manual invalidation as technical debt
**What:** 4-step manual invalidation process documented in their systems  
**Why:** Never automated during initial setup  
**Takeaway:** Follow-up question: "When was the last time a step was missed, and what happened?"

---

**3. What's the end-to-end page load time (p95) for users in [target launch country], and how much of that is CDN-served?**

*What this reveals:* International user experience before a market launch.

A synthetic test from WebPageTest or Pingdom using a node in the target country gives the real number. If p95 is above 4 seconds, ask which assets aren't CDN-cached.

---

**4. Which of our pages bypass the CDN, and why? Is that list maintained somewhere?**

*What this reveals:* Whether authenticated vs public content is correctly separated in CDN routing rules.

⚠️ **Security risk:** A new authenticated page deployed without a bypass rule could get cached and served to multiple users cross-user.

---

**5. What happens to our origin servers if the CDN is down or misconfigured and all traffic hits origin directly?**

*What this reveals:* Origin provisioning and CDN dependency patterns.

| Approach | Risk | Mitigation |
|---|---|---|
| Origin sized for cache-miss rate only (~10%) | CDN outage overloads origin | Requires manual traffic diversion |
| Origin provisioned for full traffic | Higher infrastructure costs | No surge risk; CDN acts purely as acceleration |

---

**6. Are our Lottie animation files and large static assets (images, videos) being served from CDN? What's the TTL on them?**

*What this reveals:* Whether the biggest assets are being efficiently cached.

### BrightChamps — Inefficient large asset serving
**What:** 4MB of Lottie files in student dashboard loaded globally  
**Why:** Served from origin on every request  
**Takeaway:** International users pay full round-trip latency for 4MB of data every session

---

**7. How do we handle cache busting for JavaScript and CSS bundles after a deploy?**

*What this reveals:* Whether static asset caching is set up correctly.

| Approach | Assessment | Notes |
|---|---|---|
| Content-hashed filenames with 1-year TTL | ✓ Optimal | Next.js does this by default |
| CDN invalidation after every deploy | Functional but fragile | Slower and operationally risky |

## W4. Real product examples

### BrightChamps — the 4-level caching architecture

**The architecture:** brightchamps.com routes every request through a 4-level caching stack:

| Layer | Technology | What's cached | Cache duration |
|---|---|---|---|
| **CDN** | AWS CloudFront | Fully rendered pages, static assets | Minutes to days (TTL-based) |
| **API cache** | Next.js API layer | API call responses | Request-level |
| **Redis query cache** | Redis | Google Sheets query results | Until purged or daily reset |
| **Redis data cache** | Redis | Raw Google Sheet rows | Auto-refresh daily at 5:30 AM IST |

⚠️ **The data update problem:** When the marketing team updates pricing or content in Google Sheets, users don't see the update automatically. The change must propagate through all four layers: Google Sheets → Lambda syncs Redis → Redis purge → CDN purge. This requires a human to execute 4 steps in sequence. Miss any step, and different users in different regions see different content.

**PM implication:** This is a correctness risk, not just a performance concern. The optimization roadmap calls for automating this into a single-trigger pipeline. Before building any feature that touches website content, confirm whether the invalidation pipeline is automated — or whether content updates still require a 4-step manual process.

---

### BrightChamps — static asset performance on the student dashboard

**The opportunity:** The student dashboard performance audit documents that the `confetti_animation` Lottie file is 1.3MB and the `lucky_draw_open_animation` is 896KB. These files are loaded synchronously on every page load. For a student in Malaysia on a mobile connection:

- **Origin distance:** ~2,500km to AWS India
- **From origin (5 Mbps bandwidth):** 1.3MB takes ~2 seconds to load
- **From Singapore CloudFront PoP (~400km):** ~0.3 seconds

**The impact:** 1.7 seconds per session, per user, every time the page loads — just for one animation file. At scale (BrightChamps has millions of users), this is meaningful. The optimization roadmap recommends compressing Lottie files or replacing with WebP/GIFs — but CDN caching with aggressive TTLs is the immediate, zero-refactor win.

---

### Netflix — CDN as the business model

**Scale:** Netflix delivers ~15% of global internet traffic. Their entire video delivery depends on a CDN architecture called Open Connect — proprietary edge servers they physically install inside ISP data centers worldwide, pre-loaded with popular content.

**The PM insight:** Netflix recognized that CDN is not infrastructure — it's the product. Streaming at 4K to 200 million households simultaneously is impossible without edge-cached video content physically located kilometers from the viewer, not continents away.

| Netflix CDN fact | Detail |
|---|---|
| Open Connect servers | 17,000+ embedded in ISPs globally |
| Content pre-loaded | Most-watched titles pre-staged at each ISP node |
| Cache hit target | >95% of video traffic served from edge |
| Origin traffic | <5% of total — only for uncached content |

**For non-video products:** Netflix-level CDN engineering is overkill for most SaaS. But the principle applies: the closer your content is to your user, the better the experience. For BrightChamps' international expansion, the question is not "should we use a CDN?" (they already do) but "are we getting 90%+ cache hit ratios in every target market, and do we have PoP coverage in Tier-2 cities we're expanding to?"

---

### Cloudflare — CDN as security and performance combined

**What Cloudflare changed:** Traditional CDNs (Akamai, CloudFront) were primarily delivery acceleration. Cloudflare positioned CDN as a unified security + performance layer: DDoS protection, WAF (Web Application Firewall), bot management, SSL termination, and edge caching — all in one DNS proxy.

**The PM implication for B2B:** Enterprise customers often require DDoS protection and WAF as security controls. A company using Cloudflare can tell enterprise buyers: "All traffic is scrubbed at Cloudflare's edge before reaching our infrastructure." This is a procurement and compliance talking point, not just a technical detail.

| Cloudflare capability | CDN benefit | Security benefit |
|---|---|---|
| Edge caching | Reduce origin load, improve latency | — |
| DDoS protection | Absorb attack traffic at edge | Protect origin from volumetric attacks |
| WAF | — | Block malicious requests before origin |
| Bot management | Reduce fake traffic on origin | Prevent credential stuffing, scraping |
| Workers (edge compute) | Run logic at edge without origin | Rate limiting, auth checks at edge |
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Failure pattern 1: Stale cache after deploy — the Friday afternoon incident

**What happened:**
A team deploys a pricing change on Friday afternoon and triggers CDN invalidation for `/pricing`. The invalidation propagates to most PoPs within 5 minutes, but one edge location in Southeast Asia takes 15 minutes. Users in Thailand see old pricing. A screenshot circulates on social media.

**The dangerous version:**
Deploy triggers CloudFront invalidation for `/pricing.html` but not for cached API response at `/api/pricing`. HTML is fresh, API response is stale. Page shows new marketing copy with old prices. Testing doesn't catch this because staging doesn't have a CDN.

**PM prevention checklist:**
- [ ] Cache invalidation paths are tested as part of every deploy that changes user-facing content
- [ ] Standing question: "Does our staging environment replicate CDN behavior?"
- [ ] If staging bypasses CDN entirely, flag that cache-related bugs will only appear in production

---

### Failure pattern 2: Cache poisoning — wrong content served to wrong users

**What happened:**
Team adds A/B test logic that serves different homepage variants based on query parameter (`?variant=B`). CDN caches the response for `/?variant=B` as the default homepage. Next 10,000 users—who didn't send the query parameter—get the B variant because it's cached.

**The dangerous version:**
Page with user-specific content (e.g., "Welcome back, [Name]" header fetched client-side) also includes server-rendered portion. If server-rendered portion is cached, User A's server-rendered content gets served to User B.

**PM prevention checklist:**
- [ ] Any personalization feature (A/B tests, geotargeting, logged-in state) has cache bypass or cache key augmentation strategy defined *before* implementation
- [ ] Standing question: "How does this feature interact with our CDN cache rules?"

⚠️ **Risk:** Adding personalization to a cached page without engineering cache strategy correctly is a primary vector for cache poisoning incidents.

---

### Failure pattern 3: CDN as single point of failure

**What happened:**
Team routes 100% of traffic through CloudFront. CloudFront experiences outage (rare but documented—notable incidents in 2021 and 2022). No traffic reaches origin because all DNS points to CloudFront. Product is down globally despite healthy origin servers.

**The fix:**
Configure DNS failover with secondary route that bypasses CDN and goes directly to origin if CDN health checks fail. Requires origin provisioned for full traffic capacity, not just cache miss traffic—a cost and capacity decision.

**PM prevention checklist:**
- [ ] Standing question in availability/SLA conversations: "What's our CDN failover strategy?"
- [ ] If answer is "no bypass and origin can't handle full traffic without CDN," document as known single point of failure

⚠️ **Risk:** CDN outage with no failover = global product outage even when origin is healthy.

## S2. How this connects to the bigger system

### CI/CD Pipelines (03.04)

Cache invalidation is a **deploy step**, not a manual runbook task.

| Aspect | Detail |
|--------|--------|
| **Where it lives** | Post-deploy job in CI/CD pipeline (GitHub Actions, CircleCI, etc.) |
| **What happens without it** | Stale cache guaranteed after every deployment |
| **Best practice** | CDN invalidation in deployment definition |

### Monitoring & Alerting (03.09)

CDN metrics are **first-class observability signals**. A monitoring setup tracking only application metrics is blind to a major request path layer.

| Signal | What it reveals |
|--------|-----------------|
| **Cache hit ratio** | Are we actually serving from cache? |
| **Origin error rate** | Is origin healthy when CDN misses? |
| **Edge request volume by region** | Where are users actually coming from? |
| **p95 latency by PoP** | Which regions are slow? |

### Feature Flags (03.10)

Feature flags and CDN caching create **architectural tension** because flag checks typically run per-request with user context, preventing final-form caching.

| Approach | How it works | Tradeoff |
|----------|-------------|----------|
| **Render baseline at CDN** | Cache page without flagged feature; control via server | Complex logic at origin |
| **Client-side flag evaluation** | Cache same page shell for everyone; check flag via JavaScript after load | Slight delay in feature reveal |
| **Edge computing** | CloudFront Functions / Cloudflare Workers inject flag logic at CDN | Vendor lock-in, complexity |

**Cleanest approach:** Client-side flag evaluation so the cached page shell is identical for all users.

### Security (09 module)

⚠️ **CDN as security perimeter:** CDN is the first infrastructure component touching incoming requests. It's the natural layer for:

- **Rate limiting** — block IPs making excessive requests
- **DDoS mitigation** — absorb volumetric attacks before reaching origin
- **WAF rules** — block SQL injection, XSS patterns at edge
- **Bot filtering** — filter non-human traffic

For enterprise and compliance-sensitive products, **CDN vendor selection is partly a security decision**, not just a performance one.

## S3. What senior PMs debate

### Edge computing — when does logic move from origin to edge?

**The shift:**
Traditional CDNs cache static content. Edge computing moves executable logic to the CDN layer: CloudFront Functions, Lambda@Edge, Cloudflare Workers. Instead of "cache this HTML file," it's "run this JavaScript function at every PoP globally."

| Use case | Benefit |
|----------|---------|
| A/B test assignment at edge | No origin round-trip |
| Authentication header injection | Security at scale |
| Geolocation-based redirects | Instant location response |
| Real-time personalization | Origin latency eliminated |
| Request rewriting & transformation | Universal policy enforcement |

**The operational complexity:**

⚠️ **Edge functions introduce new risks:**
- Run at 200+ PoPs globally — debugging becomes distributed debugging
- Tight execution limits (CPU time, memory)
- Errors propagate globally in minutes
- Create new infrastructure layer between application code and users
- Most engineering teams lack strong observability here

**The PM decision framework:**

> **Right question:** "Does this feature genuinely require sub-50ms globally, or are we adding edge complexity for a marginal gain?"

Edge computing justifies itself for:
- Latency-sensitive features (sub-10ms response times required)
- Global-scale operations (rewriting every request based on geography)

For most product features, the latency benefit does not justify operational complexity.

---

### Can you cache AI-generated content at CDN?

**The problem:**
AI-generated content (personalized recommendations, generated summaries, tailored descriptions) is typically dynamic — unique per user per session. Traditional CDN caching doesn't apply because the cache key is the URL path. Two users with the same URL might need different AI responses.

**The solution: Semantic caching**

> **Semantic caching:** Cache by the *meaning* of the input, not the URL path

**How it works:**

1. User submits a query ("what coding courses do you have for 8-year-olds?")
2. System converts query to vector embedding (numerical representation of meaning)
3. Check vector database: is there cached response within semantic distance threshold X?
4. **Hit:** return cached response. Cost: $0.00, latency: <50ms
5. **Miss:** call LLM, store result with embedding for future hits

**The cost impact:**

| Scenario | Daily cost | With 40% semantic hit rate |
|----------|-----------|---------------------------|
| 100K daily queries at $0.05/call | $5,000 | $3,000 (40% savings) |
| 100K daily queries at $0.10/call | $10,000 | $6,000 (40% savings) |

For narrow-domain products (tutoring, customer support, specialized assistants), 30–60% of queries are semantically similar to previously cached queries.

**Applying to BrightChamps:**

| Type | Example | Cacheable? |
|------|---------|-----------|
| Contextual output | "explain loops" + "how do loops work?" | ✓ Yes — same useful output |
| Genuinely personalized | Student's learning path recommendation | ✗ No — requires per-user state |

**Implementation:**
Libraries like GPTCache, LangChain's caching layer, and Redis vector search module handle this. It's application-layer caching with semantic keys — the principle mirrors traditional CDN caching (don't compute what you already have), but the cache key changes from URL to meaning.

---

### CDN as the new API gateway — the architectural shift

**Traditional architecture:**
```
User → CDN (cache) → Load balancer → Application servers → Database
```
CDN is passive — either serves from cache or passes through.

**Emerging architecture:**
```
User → Edge (Cloudflare Workers / CloudFront Functions) → [maybe] origin
```

**What moves to edge:**
- Authentication
- Routing
- A/B testing
- Rate limiting
- Request transformation
- Lightweight personalization

**What stays at origin:**
- Complex business logic
- Database reads/writes
- Real compute work

**Why this matters for product velocity:**

| Deployment | Speed | Geographic targeting |
|------------|-------|----------------------|
| Origin deploy | 5–15 minutes | Single region first |
| Edge deploy | Seconds | True global targeting from launch |

The "dumb CDN" is becoming the "smart edge." For PMs at scale, deciding what runs at edge vs. origin is now a meaningful architectural decision with product velocity implications — not just infrastructure theater. Features implemented at the edge require no application deploys, roll out globally in seconds, and enable true geographic A/B testing.