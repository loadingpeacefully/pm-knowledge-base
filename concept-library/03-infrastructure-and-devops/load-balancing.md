---
lesson: Load Balancing
module: 03 — Infrastructure & DevOps
tags: tech
difficulty: working
prereqs:
  - 03.01 — Cloud Infrastructure Basics: load balancers sit in front of cloud compute (EC2, EKS pods); understanding what servers and regions are makes LB concepts concrete
  - 03.03 — Kubernetes: BrightChamps uses EKS with ALB Ingress; Kubernetes horizontal scaling and load balancing are tightly coupled — rolling deploys and health checks connect directly
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
  - technical-architecture/infrastructure/infra-monitoring.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. What happens when the one server handling everything goes down

### The scenario

**9:00 PM IST, Sunday evening.** Across India, parents open the BrightChamps app to book coding classes for the week. Thousands of booking requests hit the Paathshala class service simultaneously.

**With a single server:**
- Server gets overwhelmed, slows to a crawl, booking requests time out
- Parents see spinning wheels, refresh (generating more load)
- If the server crashes: *every booking attempt fails*
- Teachers and students see empty schedules

This isn't hypothetical. Before load balancing became standard, every traffic spike—promotional campaign, press mention, product launch—was a production incident waiting to happen.

### The core fix: load balancing

> **Load Balancer:** A system that distributes incoming requests across multiple servers, preventing any single server from becoming a bottleneck.

**Instead of:** 1 server handling 10,000 requests → **System crashes or slows dramatically**

**With load balancing:** 5 servers each handling 2,000 requests → **One crashes? Remaining four absorb the load**

The load balancer acts as a traffic cop:
- Receives every incoming request
- Routes it to a healthy server
- Monitors which servers are working
- Stops sending traffic to crashed servers
- Result: slowness at worst, *not* outage

### How BrightChamps implements this

**Architecture:**
- 11 named microservices on AWS EKS (Kubernetes)
- Each microservice runs multiple pods (server instances)
- AWS Application Load Balancer (ALB) in front of each service
- ALB distributes requests across healthy pods

**Load testing requirement:** Engineers verify the load balancer and pods can handle expected peak traffic *before* a real surge arrives—particularly during peak class scheduling windows.

### PM decision frame — why you need to know this

Load balancing affects four regular PM decisions:

| **PM Decision** | **Load Balancing Knowledge** |
|---|---|
| **Launch readiness** | Can you sign off the system handles 5× traffic before a campaign? Only if you know load testing was done and capacity ceiling is confirmed. |
| **Incident triage** | Users report slowness—is it a slow backend (missing database index) or capacity problem (not enough pods)? Different diagnosis, different fix, different timeline. |
| **Deploy safety** | "We roll pods one at a time" means nothing if connection draining isn't configured. Users get connection resets mid-request during every deploy. |
| **Feature scope** | A feature storing user state *on the server* instead of a database makes horizontal scaling harder. Catching this in scoping avoids a future refactor. |

**Key takeaway:** You don't configure load balancers. You do know when to ask about them.

## F2. What it is — the toll booth with multiple lanes

On a highway with one toll booth, cars queue for kilometers during rush hour. The fix is simple: open more lanes. A traffic controller watches which lanes are free and directs cars to the least-congested one. Drivers don't choose — they go where they're directed.

A **load balancer** is that traffic controller for network requests. It sits between users (or other services) and your backend servers. Incoming requests don't go directly to a server — they go to the load balancer first, which distributes them.

### Four defining terms

> **Load balancer**
> The component that receives all incoming traffic and distributes it across backend servers. Users interact with one address (the load balancer's IP or domain); they never see individual servers.

> **Backend / upstream**
> The servers (or pods) doing the actual work. The load balancer maintains a list of these and sends traffic to them.

> **Health check**
> The load balancer regularly pings each backend (e.g., `GET /health` every 10 seconds). If a backend fails to respond three times, the load balancer marks it unhealthy and stops sending traffic to it. When it recovers, the load balancer automatically adds it back.

> **Algorithm**
> The rule for which backend gets the next request.

**Common load balancing algorithms:**

| Algorithm | How it works | Best for |
|-----------|-------------|----------|
| **Round-robin** | Request 1 → server A, request 2 → server B, request 3 → server C, request 4 → server A… | Requests of similar duration |
| **Least connections** | Send the next request to whichever server currently has the fewest active connections | Requests with highly variable duration |

### What load balancing enables

- **Availability** — if one server crashes, traffic routes to the rest. The failure is hidden from users.
- **Scalability** — add more servers behind the load balancer to handle more traffic. No changes required by users or other services — the load balancer address stays the same.
- **Zero-downtime deploys** — deploy new code to one server at a time; the load balancer keeps routing live traffic to the other servers while each one updates.

## F3. When you'll encounter this as a PM

### Planning capacity for a high-traffic event

**Scenario:** Promotional campaign, flash sale, or press feature driving sudden traffic spike

**Engineering question:** "Are we load-balanced and scaled for X× normal traffic?"

*What this reveals:* Whether your infrastructure can handle predictable peak demand

**PM action:**
- Add load testing to launch checklist for any planned traffic event
- Test validates that load balancer and backend pool handle expected peak
- BrightChamps architecture documentation requires load testing "EKS pods under peak class scheduling windows" — this is a product responsibility as much as engineering

---

### Discussing a service that's slow under load

**Scenario:** BrightChamps infra monitoring flags `/v1/deal/create-db-crm-deal` averaging 1.26 seconds (Prabandhan CRM service)

| Condition | Behavior |
|-----------|----------|
| Low traffic | 1.26s latency may be acceptable |
| 10× load, fewer concurrent requests per pod | Queue grows behind load balancer; p99 latency climbs to 5–10 seconds |

**Engineering question:** "What's our p95 latency for this API at 5× normal load?"

*What this reveals:* Whether the system degrades gracefully under traffic stress

**PM action:**
- Don't assume slow API = load balancing problem
- Root cause could be: missing database index, synchronous third-party call, or N+1 query
- Load balancing determines *how gracefully* a slow API degrades under traffic
- Ask whether the system will hold under expected peak

---

### When an engineer mentions "connection draining" or "graceful shutdown"

> **Connection draining:** A grace period during rolling deploy where the load balancer stops sending new requests to a server being updated but waits for in-progress requests to finish before removal

**Scenario:** Rolling deploy updating one server at a time

**Standard behavior:**
- Stop sending new requests to the server being updated
- Wait grace period for in-progress requests to complete
- Then remove server from pool

**PM action:**
- If users report intermittent errors during deploys, connection draining duration may be too short
- Standard: 30-second drain
- Long-running requests (batch jobs, file uploads): may need 2–5 minutes
- Validate drain duration matches API request patterns

---

### When a service has a timeout problem

**Scenario:** BrightChamps monitoring flags Tracker API and demo class join request stuck for 30 seconds — "possible timeout misconfiguration or blocking call"

> **Circuit breaker:** A load-balancing-adjacent pattern that stops sending requests to a failing/slow downstream service entirely, returning a fast failure instead of waiting for timeout

**Architecture recommendation:** Implement circuit breakers on all inter-service calls

| Response type | User experience | PM concern |
|---------------|-----------------|-----------|
| 30-second timeout fires without feedback | User sees spinner for 30 seconds | Product incident, not just infrastructure issue |
| With circuit breaker + error message | Fast, meaningful failure | Graceful degradation |

**PM action:**
- Define user experience when timeout fires
- Do users see a spinner, or a meaningful error message?
- Treat as product incident, not just infrastructure issue
- Circuit breakers and timeouts are tools for defining how gracefully your product fails
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level
# ═══════════════════════════════════

## W1. How load balancing actually works — the mechanics that matter for PMs

> **Quick Reference:** Load balancers distribute traffic across backend servers using algorithms (round-robin, least connections, etc.), monitor health via probes, route at Layer 4 (transport) or Layer 7 (application), and manage graceful shutdowns during deploys. BrightChamps uses Layer 7 (ALB) for microservices routing.

### 1. Load balancing algorithms

> **Load balancing algorithm:** A rule determining which backend server receives each incoming request.

| Algorithm | How it works | Best for | Avoid when |
|---|---|---|---|
| **Round-robin** | Requests distributed sequentially, one per backend | Uniform request sizes, identical backends | Long-running requests mixed with short ones |
| **Least connections** | Next request goes to backend with fewest active connections | Variable request duration | Identical backends with similar load |
| **IP hash** | Client's IP determines which backend handles all their requests (session stickiness) | Stateful apps requiring stickiness | Scaling (adding/removing backends breaks affinity) |
| **Weighted round-robin** | Backends receive different traffic weights (e.g., 1×, 3×) | Mixed backend capacities | All backends are identical |
| **Random with two choices** | Pick two backends randomly, send to one with fewer connections | Large-scale deployments (cheaper to compute) | Small clusters where precision matters |

---

### 2. Health checks — how the load balancer knows a backend is down

**Active health checks:**
- Load balancer probes each backend on a schedule (typical: `GET /health` every 10 seconds)
- Backend marked unhealthy after failing to respond or returning non-2xx status 3 consecutive times
- Backend re-added to rotation once it recovers and passes checks again

**Passive health checks:**
- Load balancer monitors live traffic
- Backend temporarily removed after returning 5xx errors on N consecutive requests

⚠️ **BrightChamps timing issue:** The Tracker API timing out for 30 seconds means health checks may still pass (server responds, just slowly) while real users experience unacceptable latency. Health checks validating only availability miss performance degradation.

**Better health check design:** Include response time validation — mark backend unhealthy if `/health` takes >2 seconds, not just if it fails to respond.

---

### 3. Layer 4 vs Layer 7 load balancing

> **Layer 4 (Transport Layer):** Routes based on TCP/UDP only — sees source/destination IP and port, cannot see HTTP content. Fast but has limited routing intelligence.

> **Layer 7 (Application Layer):** Routes based on HTTP headers, URL path, cookies, body content. Can make intelligent routing decisions based on request content.

| Aspect | Layer 4 (NLB) | Layer 7 (ALB) |
|---|---|---|
| **Routing basis** | IP, port only | HTTP headers, URL path, cookies, body |
| **Processing overhead** | Minimal | Higher |
| **Use case** | Non-HTTP protocols, extreme throughput | Microservices, content-based routing |
| **AWS service** | Network Load Balancer (NLB) | Application Load Balancer (ALB) |

**BrightChamps architecture uses ALB (Layer 7):**

Enables path-based microservices routing from a single load balancer:
- `brightchamps.com/api/classes/*` → Paathshala pods
- `brightchamps.com/api/students/*` → Eklavya pods
- `brightchamps.com/api/auth/*` → Chowkidar pods
- `brightchamps.com/api/payments/*` → Payments pods

*What this reveals:* ALB is how one load balancer fronts an entire microservices platform. Without path-based routing, you'd need one load balancer per service — expensive and operationally complex.

---

### 4. Connection draining and graceful shutdown

> **Connection draining:** A configured grace period allowing in-flight requests to complete before a backend is removed from rotation.

**Drain sequence:**
1. Load balancer stops sending **new** requests to the draining backend
2. Existing connections allowed to complete (or timeout at drain duration limit)
3. After drain period expires, backend is removed

**Typical drain duration:** 30 seconds for web APIs | 2–5 minutes for long-running workloads (file uploads, video processing, batch jobs)

**BrightChamps deploy implication:** Kubernetes rolling updates on EKS follow the pattern: drain → terminate → replace → health check → add back to rotation.

*What this reveals:* Drain duration directly determines the window of user impact per pod during a deploy. Too short = connection resets mid-request. Too long = deploys take longer (each pod waits out its drain window).

---

### 5. Horizontal scaling vs vertical scaling

> **Vertical scaling (scale up):** Increase server resources (CPU, RAM). Simple but hits size limits and creates single point of failure.

> **Horizontal scaling (scale out):** Add more servers behind load balancer. Improves availability through redundancy but requires stateless application design.

| Factor | Vertical scaling | Horizontal scaling |
|---|---|---|
| **Implementation** | Resize/upgrade single server | Add servers + configure LB |
| **Availability impact** | One server still fails | Multiple servers; LB routes around failures |
| **Cost scaling** | Exponential (larger servers cost disproportionately more) | Linear (add identical servers) |
| **Application requirement** | Works with stateful apps | Requires stateless design or shared state (DB/cache) |
| **Maximum scale** | Hard ceiling (largest available instance type) | Effectively unlimited |

**BrightChamps uses horizontal scaling:**
- EKS Kubernetes manages pod counts per microservice
- Horizontal Pod Autoscaler (HPA) watches CPU/memory metrics
- New pods automatically added under load
- ALB automatically distributes traffic to newly registered healthy pods

---

### 6. The BrightChamps microservices ALB architecture

The architecture includes 11 core microservices in EKS. ALB Ingress Controller acts as Layer 7 load balancer, routing by path to the correct service.

| Service | Route | Function | Scaling concern |
|---|---|---|---|
| **Paathshala** | `/api/classes/*` | Class scheduling | Peak: 9 PM IST Sunday booking rush |
| **Eklavya** | `/api/students/*` | Student data | Scales with user base growth |
| **Chowkidar** | `/api/auth/*` | Authentication | Login bursts on app open |
| **Prabandhan** | `/api/crm/*` | CRM/deals | 1.26s avg — under investigation |
| **Doordarshan** | `/api/meetings/*` | Video meetings | Peak: class start times |
| **Payments** | `/api/payments/*` | Transactions | Low volume, high criticality |

Each row represents a pod pool. ALB distributes requests within each pool.

⚠️ **Critical distinction:** When Prabandhan CRM averages 1.26s response time, adding more pods behind the load balancer increases resilience under load but **does not fix the underlying slow query**. The load balancer makes a slow service more resilient; it does not make a slow service fast.

## W2. The decisions load balancing forces

### Decision 1: Stateless vs stateful — can you add more servers freely?

Horizontal scaling only works if any backend can handle any request. If a user's session data lives on Server A only, routing their next request to Server B means they're logged out.

| Approach | How it works | Pros | Cons | When to use |
|---|---|---|---|---|
| **Stateless + JWT** | No server-side session. Auth token contains all user context — any pod can validate it. | Any pod handles any request; scale freely | Requires JWT implementation; token revocation is harder | All new applications — this is the modern standard |
| **Sticky sessions** | LB routes same user to same pod always (via cookie or IP hash) | Works for legacy stateful apps; no code change needed | Pod failure loses session; scaling changes break affinity; 33% of users hit degraded pod if one pod is slow | Legacy apps as a transitional measure only |
| **External session store** | Session data in Redis or database; all pods read/write the same store | Any pod handles any request; scale freely | Requires Redis infrastructure; session store becomes a dependency | Migrating stateful apps that can't yet adopt JWTs |

> **Recommendation:** New applications: stateless with JWT. Legacy stateful: sticky sessions temporarily, migrate to stateless. Sticky sessions are a workaround, not a permanent architecture.

---

### Decision 2: How long should connection draining be?

| API type | Typical request duration | Recommended drain |
|---|---|---|
| Standard web API (CRUD) | <500ms | 30 seconds |
| Search / complex query | 1–5 seconds | 60 seconds |
| File upload / processing | 10–60 seconds | 120 seconds |
| Video transcoding / AI inference | Minutes | 5+ minutes or graceful job hand-off |

**Real scenario:** The BrightChamps Tracker API with 30-second timeouts — if drain is set to 30 seconds and a request is in progress when drain starts, it could be terminated right as it completes. 

> **Critical rule:** Drain should be slightly longer than the longest expected request duration for that service.

---

### Decision 3: Internal vs external load balancer — what should be publicly addressable?

In a microservices architecture, load balancers exist at multiple tiers:

| Tier | Type | Handles | Example |
|---|---|---|---|
| External (internet-facing) | Public ALB | User traffic → frontend or API gateway | brightchamps.com → Next.js pods |
| Internal (service-to-service) | Private ALB / K8s Service | Microservice A → Microservice B | Paathshala → Doordarshan |

> **Security boundary:** Internal load balancers are not publicly accessible — they exist only within the VPC. Doordarshan (meetings service) should not be directly accessible from the internet; only Paathshala should call it. The load balancer enforces this by having no public IP.

> **Recommendation:** Only the API gateway (or edge layer) should have an internet-facing load balancer. All inter-service communication should use internal load balancers or Kubernetes service discovery, keeping internal services off the public internet entirely.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **1. What load balancer type are we using, and does it support path-based routing for our microservices?** | Whether the team has a single entry point (ALB with path routing) or a proliferation of load balancers per service. The latter is operational complexity that compounds at scale. |
| **2. What's our connection drain duration, and has it been tuned for our slowest APIs?** | Whether deploys cause user-visible errors. Drain duration must exceed the longest API timeout to avoid terminating in-progress requests during deploys. |
| **3. What are our health check parameters — interval, threshold, and what does the `/health` endpoint actually validate?** | How quickly the load balancer detects and routes around unhealthy pods. A health check that only validates "server is listening" misses performance degradation. |
| **4. What's the p95 latency for each of our critical services at 3× and 10× current traffic? Have we load tested these?** | Scaling headroom before user experience degrades. The answer should name specific services and their tested throughput limits. |
| **5. Are our applications stateless — can any pod handle any request, or do users need to hit the same pod?** | Whether horizontal scaling is actually possible. The answer should explain the authentication mechanism (JWT vs server-side sessions) and whether Redis is used for shared state. |
| **6. What happens to a user's request if the pod handling it is removed during a rolling deploy?** | The deploy experience for users. The correct answer: "Connection draining routes their request to completion before the pod is terminated." |
| **7. Do we have circuit breakers on inter-service calls — what happens when a critical service is down during peak traffic?** | The failure isolation between microservices. Without circuit breakers, a slow downstream service causes upstream services to accumulate blocked connections, cascading failures. |

---

### Company — BrightChamps (EKS deployment)

**What:** ALB Ingress Controller handles path-based routing for all 11 services with connection drain duration tuned to 30+ seconds (matching Tracker API timeout).

**Why:** Single entry point reduces operational complexity. Drain duration ≥ slowest API timeout prevents request termination during deploys.

**Takeaway:** Architecture correctly routes and drains at scale.

---

### Company — Prabandhan (health check gap)

**What:** Health check with 2-second response time threshold would have caught degraded 1.26s API performance.

**Why:** Reactive health checks (only "server listening") miss performance degradation that degrades user experience.

**Takeaway:** Health checks must validate application responsiveness, not just reachability.

---

### Company — BrightChamps (circuit breaker recommendation)

**What:** Architecture docs recommend circuit breakers for all inter-service calls after Doordarshan downtime cascaded failures during class scheduling.

**Why:** Without circuit breakers, slow downstream services cause upstream services to accumulate blocked connections, multiplying failure impact.

**Takeaway:** Circuit breakers isolate failures and must specify fallback behavior (cached response, fast failure, or degraded mode).

## W4. Real product examples

### BrightChamps — 11 microservices behind one ALB

**The architecture:** The BrightChamps platform runs 11 microservices on EKS, all fronted by an ALB Ingress Controller. Each service maintains multiple pod replicas. The ALB routes by URL path to the correct service pool.

| Service | Traffic source | Current performance | Scaling flag |
|---|---|---|---|
| Paathshala (classes) | Student app, teacher app, admin | Normal | Sunday 9 PM IST surge |
| Prabandhan (CRM) | Admin backend, sales flow | **1.26s avg** — under investigation | Request queue grows under load |
| Doordarshan (meetings) | Class join flow | Intermittent failures tracked | Class start-time spikes |
| Chowkidar (auth) | All apps on login | Normal | App-open burst patterns |
| Payments | Checkout flow | Normal | Low volume, high criticality |

**The performance gap:** Prabandhan's 1.26s average response time is a documented issue. Under 3× traffic, if each pod can handle ~50 concurrent requests before queuing, adding load increases queue depth faster than additional pods can be provisioned. 

> **Key insight:** The load balancer distributes load correctly — but the fix is a database index on the CRM deal creation query, not more pods. More pods distribute the slow work; faster code eliminates it.

---

### BrightChamps — the circuit breaker gap

**The failure pattern:** The monitoring tracker documents a Tracker API and demo class join request stuck for 30 seconds. The recommended fix: implement circuit breakers on all inter-service calls. Without a circuit breaker, when Doordarshan is slow or down, Paathshala accumulates open connections waiting for responses. Each waiting thread blocks a pod connection slot. At scale, all Paathshala pods fill their connection pools with waiting Doordarshan requests and become unable to handle new class scheduling requests — a cascade.

**The circuit breaker pattern:**

```
Paathshala → Doordarshan request
  → Success: circuit closed (normal operation)
  → 5 consecutive failures: circuit opens
       → Fast fail: return cached/fallback response
       → After 30s: half-open state, send test request
            → Success: circuit closes
            → Failure: circuit stays open
```

**PM implication:** 

> **Circuit breaker definition:** A mechanism that stops requests to a failing service, returns cached/fallback responses instead, and periodically tests recovery without overloading the failed service.

Circuit breakers define your failure modes. For class scheduling (Paathshala → Doordarshan), the fallback matters:
- ✅ "Video meeting link generation failed — we'll send it by email within 5 minutes" 
- ❌ "Class join timed out after 30 seconds"

*What this reveals:* The PM defines the fallback behavior; engineering implements the circuit breaker.

---

### AWS ALB — path-based routing in production

**The scale:** AWS ALB handles tens of millions of requests per second across all AWS customers. A single ALB in a BrightChamps-scale deployment easily handles thousands of requests per second with sub-millisecond routing overhead.

| ALB capability | What it enables |
|---|---|
| Path-based routing | One ALB for all 11 microservices (by URL path) |
| Host-based routing | `api.brightchamps.com` vs `admin.brightchamps.com` → different backends |
| Weighted target groups | 90/10 traffic split for gradual rollouts (canary deploys) |
| Connection draining | Configurable per target group (30s default, adjustable) |
| Health check customization | Per-path, per-threshold, response time validation |
| Access logs to S3 | Full request log for every request — SLO analysis input |

**Canary deployments via weighted target groups:**

Deploy new code to 10% of pods → route 10% of traffic to them via ALB weight → monitor error rates and latency. If healthy after 30 minutes, shift to 50%, then 100%. Roll back at any point by adjusting weights. 

> **User-facing benefit:** No user notices — the load balancer handles the gradual shift transparently.

---

### Shopify — load balancing for 1,167 orders per second

**The peak:** Black Friday 2023, Shopify processed 4.2 million transactions per hour — 1,167 orders per second at peak. Each order hits multiple microservices: inventory, payment, fulfillment, notifications. Each service runs behind its own load balancer.

| Load balancing decision | How Shopify handles it |
|---|---|
| **Horizontal scaling** | Each service scales independently; checkout doesn't scale with inventory |
| **Traffic spike readiness** | Annual load tests simulate Black Friday traffic 3–4 months before the event |
| **Circuit breakers** | If inventory service degrades, checkout returns "cart confirmed, inventory reserved" instead of timing out |
| **Connection draining** | Rolling deploys during Black Friday are suspended; deploy freeze 72 hours before peak |
| **p99 target** | Checkout p99 latency <200ms during peak; breached = incident |

**The PM insight that transfers:** 

Shopify's deploy freeze is a **product decision, not an engineering one**. The PM team defined the risk threshold — "no deploys 72 hours before Black Friday" — and engineering enforced it via process. 

*What this reveals:* Load balancing strategy applied at the product level means protecting the system by reducing the operational surface area during peak load, not just by adding more servers.

---

### Stripe — global load balancing at payment scale

**The constraint:** Payment processing is latency-sensitive (users wait synchronously) and correctness-critical (no double charges, no lost transactions). Stripe runs active-active multi-region deployments — servers in multiple AWS regions simultaneously handling production traffic, with load balancers routing each payment to the geographically nearest healthy region.

| Stripe LB approach | Detail |
|---|---|
| Multi-region active-active | Traffic routed to nearest healthy region |
| Anycast routing | Single IP resolves to nearest PoP globally |
| Regional failover | Automatic rerouting if a region degrades |
| Circuit breakers on every downstream | Payment fails fast rather than hanging |
| p99 latency target | <300ms for payment confirmation globally |

**PM insight — the business impact:**

For payment and checkout flows, load balancing strategy is directly tied to conversion rates. 

⚠️ **Conversion risk:** Every 100ms of additional latency at checkout reduces conversion by ~1% (industry benchmark).

Stripe's multi-region LB is an engineering decision with direct revenue impact — the kind of infrastructure investment that has a clear product ROI case.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Failure pattern 1: The thundering herd after a cache flush

**What happens:**
After cache invalidation (CDN or Redis), all requests miss cache simultaneously and hit the load balancer at once. Every backend pod does expensive origin work in parallel.

| Stage | Impact |
|-------|--------|
| Cache invalidation | All entries expire at same time |
| Request wave | 1,000 simultaneous requests hit backends |
| Database load | 1,000 queries execute simultaneously (e.g., 500ms each) |
| Backend timeout | Pods wait for DB responses, health checks fail |
| Cascade | LB removes pods; remaining pods get more traffic; they also time out |

> **The misconception:** This looks like a load balancer failure. The LB is actually doing its job correctly — the failure is *synchronized cache expiry*.

**Prevention fixes:**
- **Jitter TTLs** — add random offset to prevent mass simultaneous expiry
- **Request coalescing** — if 100 requests miss the same key, only one fetches from origin; the other 99 wait for the result

**PM prevention role:**
Before any planned cache flush (after major deploys), ask:
- "Do we have jitter on TTLs?"
- "Do we have request coalescing for expensive cache misses?"

⚠️ This is not routine infrastructure hygiene — it's a traffic spike mitigant that can prevent the cache flush itself from causing a partial outage.

---

### Failure pattern 2: Sticky sessions masking a partially broken backend

**What happens:**
A stateful application uses IP-hash sticky sessions across three backends. One backend develops a slow memory leak (response time: 200ms → 3 seconds over 6 hours). The health check passes, but 33% of users are routed to the degraded backend.

| What you see | What's actually happening |
|--------------|--------------------------|
| "Latency slightly elevated" (aggregate metric) | One-third of users experience 10× worse performance |
| Average latency across all backends | Slow backend masked by fast backends in the average |
| Health check passing | Backend responds, but performance is degraded |

> **Subpopulation effect:** Sticky sessions route a consistent subset of users to one backend. Aggregate metrics hide this routing bias.

**Prevention fix:**
- Per-backend latency monitoring (not just aggregate)
- Alert on backend-level performance anomalies

**PM prevention role:**
When diagnosing performance complaints affecting only a subset of users, ask:
- "Do we use sticky sessions?"
- "Is there any mechanism by which a subset of users could be routed differently?"

---

### Failure pattern 3: The database connection pool exhaustion during scale-out

**What happens:**
Horizontal scaling adds more pods. Each pod maintains a database connection pool (e.g., 10 connections/pod).

| Scenario | Pod count | Total connections | Database limit | Result |
|----------|-----------|-------------------|-----------------|--------|
| Baseline | 5 pods | 50 connections | 151 (RDS MySQL default) | ✓ Safe |
| Scale-out | 50 pods | 500 connections | 151 | ✗ Exceeded |

New pods cannot establish connections → fail health checks → load balancer removes them → scale-out event causes a cascade.

⚠️ This catches every team that scales horizontally for the first time without thinking about connection pool limits.

**Prevention fix:**
- **PgBouncer** or **RDS Proxy** — connection pooler that multiplexes thousands of application connections over fewer actual database connections

**PM prevention role:**
When the team discusses scaling out a service, ask:
- "What happens to database connection count as we scale from X pods to 10X pods?"
- If the answer is "it grows proportionally," ask: "What's the database connection limit, and is a connection pooler in place?"

⚠️ Add this to the launch checklist for any service expected to scale horizontally.

## S2. How this connects to the bigger system

| System | Connection | PM Implication |
|--------|-----------|-----------------|
| **Kubernetes (03.03)** | LB configuration lives as code in Ingress resources; ALB Ingress Controller auto-manages rules. Rolling updates, health checks, and pod autoscaling integrate directly with LB. | Treating LB in isolation misses how infrastructure actually operates—must understand K8s integration. |
| **CDN (03.07)** | Two-tier traffic distribution: CDN edge (tier 1) → cache hit serves directly; cache miss → LB at origin (tier 2) → backend pods. Cache hit rate drives LB load. | Improving cache hit ratio from 70% → 90% reduces LB traffic by 66% on static-heavy sites. Small cache optimization = massive load reduction. |
| **Monitoring & Alerting (03.09)** | LB is the primary SLO data source: request rate (rps), p50/p95/p99 latency, 5xx errors, backend health, connection count, drain events. | "Introduce SLO dashboards" recommendation is fundamentally a LB metrics project—signals originate at the LB. |
| **CI/CD (03.04)** | Every rolling deploy: drain pod → terminate → deploy → pass health checks → add to LB rotation → repeat. Drain duration coordination is critical. | Deploy pipeline must treat LB interaction as first-class concern; misconfiguration causes user-visible errors during rollouts. |

## S3. What senior PMs debate

### Service mesh vs traditional load balancing — when does Envoy/Istio justify its complexity?

> **Service Mesh:** Infrastructure layer that moves load balancing, circuit breaking, retries, mTLS, and observability from application code into sidecar proxies running next to every pod. Every service-to-service request flows through the sidecar without requiring code changes.

**The case for:**
- Consistent traffic management across all services without each team implementing their own logic
- Single configuration point for retries, timeouts, and traffic splitting across entire platform
- Automatic observability — every inter-service call traced without instrumentation code

**The case against:**
- High operational complexity (Istio notoriously difficult to operate)
- ~3ms latency added per hop
- Requires expertise in both application and mesh debugging
- At BrightChamps' 11-service scale, operational overhead may exceed benefits

| Decision Factor | Service Mesh | API Gateway + Per-Service Logic |
|---|---|---|
| **Best for** | 50+ microservices; need platform-wide consistency | <30 services; teams can own circuit breaker logic |
| **Latency cost** | ~3ms per hop | Minimal |
| **Observability** | Automatic across entire mesh | Manual per-service instrumentation |
| **Operational burden** | High (dedicated platform team) | Lower |
| **Configuration point** | Centralized | Distributed |

**PM lens:** Service mesh justifies its complexity only when the organization has standardized on microservices at scale (50+ services) and consistency benefit is demonstrable. At 11 services, a well-configured API gateway with per-service circuit breakers (in code) delivers most value at a fraction of complexity.

---

### Global load balancing — multi-region active-active vs active-passive

**Context:** BrightChamps currently operates in single AWS region (India). International expansion (SEA, Middle East) raises routing question: serve all users from India (high latency) or route to nearest region (requires multi-region data sync)?

| Approach | Active-Passive | Active-Active |
|---|---|---|
| **How it works** | One primary region + standby; DNS failover on outage | Both regions serve live traffic; GeoDNS routes to nearest |
| **User latency (normal)** | High for non-primary regions (unchanged) | Low for all regions (location-optimized) |
| **Data sync** | Single source of truth | Eventual consistency OR expensive sync replication |
| **Complexity** | Lower | 5–10× higher |
| **Cost** | Lower | 5–10× higher |

**PM decision framework:**
- **Too early:** During product-market fit validation in new markets
- **Right time:** Before hundreds of thousands of international users, when latency demonstrably hurts retention in specific markets
- **Transition sequence:** CDN coverage → read-replica databases in target regions → active-active multi-region

---

### AI inference load balancing — a fundamentally different problem

⚠️ **Problem scope shift:** Web request load balancing assumes independent, short-lived (ms–sec), uniform-cost requests. AI inference violates all three assumptions.

| Characteristic | Web Requests | AI Inference |
|---|---|---|
| **Duration** | Milliseconds to seconds | 5–60 seconds (LLM responses) |
| **Cost variance** | Relatively uniform | 100:1 ratio (10 vs 1,000 tokens) |
| **Scarce resource** | CPU, RAM | GPU memory (context window) |
| **Request pattern** | Independent | May depend on session context |

**Emerging patterns for AI workloads:**

- **Least-token routing** — Route to GPU with most available context capacity (not fewest connections)
- **Request batching at LB layer** — Batch multiple small requests to maximize GPU utilization instead of routing each request individually
- **Priority queuing** — Premium users' inference requests skip queue; load balancer must respect business model, not treat all requests equally

**BrightChamps application:**

When a student asks the AI tutor a question, that inference needs different load balancing than a class booking API call:

| Workload | Duration | Load Balancing Strategy | Business Logic |
|---|---|---|---|
| **Class booking API** | 50ms | Round-robin across pods | Standard |
| **AI tutoring inference** | ~10 seconds | Least-token routing + batching | Priority: paying vs trial students |

**Product team responsibility:** Define priority logic and routing requirements.  
**Engineering responsibility:** Implement load balancer architecture that enforces those rules.