---
lesson: Scalability Patterns
module: 09 — security and scale
tags: tech
difficulty: working
prereqs:
  - 03.03 — Kubernetes: BrightChamps runs microservices on EKS (Elastic Kubernetes Service); horizontal scaling in practice requires understanding how Kubernetes scales pods
  - 03.06 — Queues & Message Brokers: async processing via SQS is one of the primary scalability patterns; understanding queues is prerequisite for understanding why sync-to-async decomposition matters
  - 02.04 — Caching (Redis): caching is how database read bottlenecks are broken; Redis is central to the BrightChamps scaling architecture
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
  - technical-architecture/infrastructure/infra-monitoring.md
profiles:
  foundation:
    - Non-technical Business PM
    - Aspiring PM
    - Designer PM
    - MBA PM
  working:
    - Growth PM
    - Consumer Startup PM
    - B2B Enterprise PM
  strategic:
    - Ex-Engineer PM
    - Senior PM
    - Head of Product
status: ready
last_qa: 2026-04-09
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

In the early web era, most products ran on a single server. One machine handled everything: received requests, ran the application code, queried the database, and returned responses. This was simple to build and manage. It also meant that when traffic grew — when you went from 100 users to 10,000 — the only option was to buy a bigger, faster, more expensive machine.

This approach, called **vertical scaling** (making the one machine larger), hit hard limits. A bigger machine costs disproportionately more. Beyond a certain point, no single machine can handle the load. And when that one machine failed, the entire product went down — no fallback.

The alternative that emerged — **horizontal scaling** (adding more machines instead of bigger machines) — required a fundamental shift in how software was designed. A system that could run on one server had to be redesigned to run on many servers simultaneously, with any individual server able to handle any incoming request without breaking. This is not a small change. It requires rethinking how session data is stored, how database writes are coordinated, and how work is distributed across servers.

The companies that mastered horizontal scaling — Google, Amazon, Netflix — became the architectural reference points for the modern web. Their engineering teams published the patterns: stateless services, database read replicas, asynchronous queues, content delivery networks, circuit breakers. These patterns became the standard toolkit for building products that scale.

## F2 — What it is, and a way to think about it

> **Scalability:** A system's ability to handle increasing load (more users, more requests, more data) without degrading in performance. A scalable system can serve 10x the users without requiring 10x the engineering work or 10x the infrastructure cost.

### The Stateless Requirement

Before comparing approaches, one concept matters most:

> **Stateless server:** Does not retain any information between requests. Every request arrives with everything needed to process it (session token, parameters, user ID). Any server can handle any request from any user.

> **Stateful server:** Stores user session data locally. Subsequent requests from the same user must return to the same server. This blocks horizontal scaling.

**Why this matters:** Horizontal scaling only works when any server can handle any request. If your servers remember which user they're talking to, you're locked to specific servers — which defeats the purpose of adding more.

### Scaling Approaches

| Approach | Method | Pros | Cons |
|----------|--------|------|------|
| **Vertical Scaling** (up) | Add resources to a single server: CPU, RAM, disk | Simple to implement | Hardware limits; exponential cost growth |
| **Horizontal Scaling** (out) | Add more servers running the same application in parallel | Unlimited capacity; cost-effective; cloud-native | Requires stateless design; complexity |

### The Supermarket Analogy

**One lane:** Limited by cashier speed (vertical scaling limits)

**Multiple lanes:** Each lane identical and independent; any customer can be served at any lane from start to finish

*What this reveals:* Scalable systems work the same way—any server must be able to handle any user request, completely independent of prior context.

### Scalability Patterns

Standard engineering techniques for achieving scalability:

- Stateless service design
- Load balancing
- Database caching
- Async queues
- Content delivery networks (CDNs)
- Circuit breakers

## F3 — When you'll encounter this as a PM

### Latency spikes or timeouts under load

**The problem:** Synchronous operations block user requests, causing response time failures at scale.

### BrightChamps — Synchronous CRM writes blocking requests

**What:** The `/v1/deal-create-db-crm-deal` endpoint averaged 1.26 seconds response time; tracker API requests hit 30-second timeouts.

**Why:** The service writes synchronously to Zoho CRM instead of queuing the work asynchronously.

**Takeaway:** As PM, ask: *Can this operation be deferred rather than blocking the user's request?*

---

### Planning for a growth event

**The problem:** Traffic spikes without advance notice leave engineering unable to scale.

**Your triggering scenarios:**
- Marketing campaign launch
- New market expansion
- High-traffic partner integration

| What Engineering Needs | Why |
|---|---|
| Expected traffic volume | Capacity planning |
| Timing of the spike | Infrastructure provisioning |
| Duration | Resource commitment scope |

→ **Engineering needs advance notice on all three.**

---

### When engineers say "hard to scale"

**This is not an excuse—it's a design constraint.**

> **Stateful features:** Real-time leaderboards, live activity feeds, user-to-user chat require coordination across servers. They introduce shared state that breaks horizontal scaling.

**Your decision framework:** Understand the constraint. Decide if the feature's value justifies the scaling cost, or if the design needs to change.

---

### Infrastructure decisions with scaling tradeoffs

### BrightChamps — Self-hosted MongoDB vs. managed Atlas

**What:** BrightChamps runs MongoDB on self-hosted EC2 instances instead of AWS Atlas (flagged as Medium technical debt).

**Why:** Self-hosted introduces operational overhead and doesn't scale as smoothly as managed services.

**Takeaway:** You're trading migration cost now against scaling friction and operational risk later. Know which tradeoff you're approving.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The core scalability patterns

#### Pattern 1: Stateless services + horizontal scaling

> **Stateless service:** A service where each request is self-contained and any instance can handle it without relying on local memory or previous interactions.

For a service to scale horizontally, it must be stateless. In practice:

- User session data is stored in a shared, external store (Redis, database) — not in the server's local memory
- No user-specific in-memory state persists between requests
- Any server can restart without losing anything user-visible

**BrightChamps** — Microservice architecture
- **What:** Deploys services (Eklavya, Paathshala, Chowkidar, etc.) as containers on AWS EKS (Kubernetes)
- **Why:** When a service needs more capacity, Kubernetes spins up additional pods
- **Takeaway:** This only works because each pod is stateless — any pod can handle any request

---

#### Pattern 2: Load balancing

> **Load balancer:** Infrastructure that distributes incoming requests across multiple server instances.

| Algorithm | How it works | Use case |
|---|---|---|
| **Round robin** | Requests distributed evenly across all instances in rotation | Simple, uniform request loads |
| **Least connections** | New requests sent to the instance with fewest active connections | Variable request complexity |
| **IP hash** | Requests from the same IP always routed to the same instance | Session pinning (usually a sign of stateful design to be fixed) |

**BrightChamps** — Load balancing layer
- **What:** AWS EKS includes internal load balancing across pods; CloudFront acts as edge load balancer
- **Why:** Distributes traffic across service instances and caches static assets globally
- **Takeaway:** Multi-layer load balancing reduces latency and prevents any single instance from bottlenecking

---

#### Pattern 3: Database scaling — the most common bottleneck

Databases hold shared mutable state and are the hardest component to scale horizontally.

| Approach | How it works | When to use |
|---|---|---|
| **Read replicas** | Primary database handles writes; read replicas are synchronized copies that handle reads | Most applications have far more reads than writes |
| **Caching** | Redis or Memcached stores frequently read results in memory | High-traffic read patterns (e.g., product pages) |
| **Database sharding** | Database is split horizontally — different users' data lives in different shards | Data volume exceeds what a single database can handle |

**BrightChamps** — Database optimization
- **What:** Uses Redis for caching across multiple services
- **Why:** Reduces repeated database queries for frequently accessed data
- **Takeaway:** Caching is critical, but database design itself can be a bigger bottleneck

⚠️ **Performance concern identified:**
- `POST /v1/deal/create-db-crm-deal`: 1.26s response time
- `POST /v1/deal/update-crm-deal-to-closed-won`: 1.19s response time
- **Root cause:** Missing indexes or synchronous third-party calls
- **Recommended fix:** Add database indexes (reducing query time from 1.26s to <100ms) + offload CRM syncs to async queue

---

#### Pattern 4: Async processing with queues

> **Async processing:** Moving time-consuming operations out of the request path so the user receives an immediate response while work continues in the background.

**How it works:**
1. User submits request
2. Server queues the work and immediately returns a "success" response
3. Background worker processes the queued work asynchronously
4. User polls for result or receives a notification when complete

**BrightChamps** — Async job handling
- **What:** Uses AWS SQS for async processing; Hermes service and class updates offloaded to queues
- **Why:** Frees up web servers to handle new requests instead of blocking on slow operations
- **Takeaway:** Async patterns are essential for user experience at scale

⚠️ **Issue identified:**
- 30-second tracker API timeout indicates a synchronous external call (likely to Zoho or another third-party)
- **Action needed:** Move to async queue to prevent blocking

---

#### Pattern 5: CDN (Content Delivery Network)

> **CDN:** A network of servers that cache static assets at edge locations close to users globally, reducing latency and load on origin servers.

Static assets (JavaScript, CSS, images, video) don't change between requests and don't need to be served from the application server.

| Metric | Local CDN | Cross-continent origin |
|---|---|---|
| Latency | 5–20ms | 150–300ms |
| Load on app servers | Dramatically reduced | Higher |

**BrightChamps** — Asset delivery
- **What:** Uses AWS CloudFront for static asset distribution
- **Why:** Serves files from edge locations close to users
- **Takeaway:** Combined with image compression, lazy loading, and caching headers, CDN optimization removes a major scaling bottleneck

---

#### Pattern 6: Circuit breakers

> **Circuit breaker:** A mechanism that prevents cascading failures by immediately rejecting calls to a failing downstream service instead of waiting for timeouts.

**The problem:**
In microservices, one slow service causes cascading failure:
- Service A calls slow Service B → blocks Service A's threads → blocks all requests to Service A → blocks Service C (which depends on Service A)

**How it works:**
1. Circuit breaker monitors calls to a downstream service
2. If failure rate exceeds threshold (e.g., >50% of calls fail or timeout in last 30 seconds), circuit "opens"
3. Calls to that service are immediately rejected with a fallback response
4. After cool-down period, circuit "half-opens" to test if service has recovered

⚠️ **Missing in current architecture:**
- KB explicitly flags: "Implement circuit breakers on all inter-service calls to prevent 30s hangs"
- **Current consequence:** 30-second tracker API hang is the direct result of missing circuit breakers allowing cascading failures

---

### BrightChamps architecture: scalability in practice

| Component | Scaling approach |
|---|---|
| Application services (Eklavya, Paathshala, etc.) | Horizontal scaling via AWS EKS (Kubernetes pods) |
| Static assets | CDN via AWS CloudFront |
| Async jobs | AWS SQS message queues |
| Background compute | AWS Lambda (serverless, auto-scales) |
| Primary database | AWS RDS (MySQL) — managed, with read replica capability |
| Document store | MongoDB self-hosted on EC2 — **limited horizontal scaling** |
| Caching | Redis (shared across services) |

⚠️ **Technical debt: MongoDB self-hosted on EC2**

| Aspect | Self-hosted MongoDB on EC2 | MongoDB Atlas |
|---|---|---|
| Horizontal scaling | Requires manual intervention (adding EC2 instances, configuring replica sets, managing sharding) | Handles scaling automatically |
| Operational burden | High — ongoing maintenance and monitoring | Managed service |
| Cost at scale | Potentially lower per unit, but labor-intensive | Higher unit cost, lower operational cost |
| Current status | Medium technical debt — will become painful as student/teacher data grows | Recommended path forward |

**What this reveals:** Self-hosted infrastructure decisions made at smaller scale become scaling bottlenecks as the product grows. MongoDB Atlas trades some cost efficiency for operational simplicity — a prudent tradeoff given growth trajectory.

## W2 — The decisions this forces

### Decision 1: Stateless vs stateful feature design

Every feature that introduces server-side state creates a horizontal scaling constraint. The PM's job is to recognize which feature requests are stateful and ask whether they need to be.

| Design Choice | How It Works | Scaling Impact | PM Question |
|---|---|---|---|
| **Server-side sessions** | Login state stored in server memory; all user requests route to same server (sticky sessions) | Doesn't scale horizontally | Can we avoid storing this state on the server? |
| **Token-based auth (JWT)** | Login state in token; token verified by any server | Scales horizontally—any server handles any user | Is stateless auth viable for this feature? |

> **Stateless design:** The system doesn't store user-specific state on any single server. The token or client carries all necessary information for any server to process the request.

**Real-time features**

| Requirement | Scope | Scalability | Alternative |
|---|---|---|---|
| **True real-time** (live feeds, leaderboards, multiplayer) | All servers must coordinate on same events | Hard—requires WebSockets + pub/sub layer | Near-real-time (5–30s polling) |
| **Near-real-time** | Periodic refresh acceptable to users | Stateless and horizontally scalable | — |

**Recommendation:** Default to stateless design. When a feature requires state, ask explicitly: *Where does this state live?* If the answer is "on the server," ask whether it can be moved to Redis or a token.

---

### Decision 2: Sync vs async processing

The choice between synchronous and asynchronous processing determines user experience and system scalability simultaneously.

| Processing Type | User Experience | Best For | Risk |
|---|---|---|---|
| **Synchronous** | User waits for result | Fast operations (<500ms), immediate user feedback needed, failure requires instant confirmation (e.g., payments) | Blocks user; slow operations degrade UX |
| **Asynchronous** | User gets immediate acknowledgment; result arrives later | Slow operations, unpredictable timing, third-party system dependencies (CRM, email, video) | User may forget about task; needs notification system |

*What this reveals:* If the user is waiting on the server during a sync call, scaling the server doesn't help—the user still waits.

**Example: BrightChamps CRM sync**

The Zoho CRM sync (1.26s) should be **async**. The user who creates a deal doesn't need to wait 1.26 seconds. They need immediate confirmation the deal was created. The Zoho sync happens in a background queue within seconds.

**Recommendation:** Any operation involving third-party systems (Zoho, Zoom, email providers) should be async unless the user explicitly needs the third-party confirmation before proceeding.

---

### Decision 3: When to invest in scalability vs ship faster

Scalability investment is not free. Adding Redis caching requires cache invalidation logic. Async processing requires queue infrastructure and monitoring. Circuit breakers require fallback behavior design. For early-stage products, premature scalability investment slows feature delivery without proportional benefit.

**The right threshold — invest when:**

- ✅ Current architecture causes measurable user-visible degradation (latency, errors, timeouts)
- ✅ Known growth event will increase traffic significantly within 6–12 months
- ✅ Technical debt will become exponentially more expensive to fix after system grows larger

**Defer when:**

- ❌ Product serves <10,000 daily active users
- ❌ No known scaling bottlenecks
- ❌ No growth events planned

⚠️ **Exception:** Build simple, stateless services from the start. Redesigning for statelessness later is expensive. Don't speculatively add caching, circuit breakers, or async queues—but do design for statelessness day one.

**BrightChamps context:** The CRM API latency (1.26s) is already user-visible. The 30-second timeout is a P1 incident risk. These are **past the threshold**—they need to be fixed now, not deferred.

## W3 — Questions to ask your engineering team

### Quick Reference
| Question | Red Flag | Green Flag |
|----------|----------|-----------|
| Stateless services? | Session data in server memory | Sessions in Redis or JWT tokens |
| P95 latency? | Team doesn't measure it | P95 tracked and <acceptable threshold> |
| Async opportunities? | All operations synchronous | Third-party calls, analytics, background jobs queued |
| Circuit breakers? | No resilience pattern | Per-service circuit breaker configs |
| DB scaling? | Single primary, no caching | Read replicas + Redis caching |
| Auto-scaling? | Manual scaling required | HPA configured with thresholds |
| Self-hosted DB? | Acknowledged but unprioritized | Atlas or managed alternative in roadmap |

---

### 1. Are our application services stateless — or do any store user session data in server memory?

*What this reveals:* Whether horizontal scaling is currently possible.

**The problem:** If services store sessions locally, you have sticky session routing — adding more servers doesn't help because each user is bound to one server.

✅ **Healthy answers:**
- "Session data is in Redis"
- "We use JWT tokens with no server-side state"

---

### 2. What's the p95 (95th percentile) latency for our most critical user-facing APIs, and where are the bottlenecks?

*What this reveals:* Whether scaling problems are already user-visible.

> **P95 latency:** Response time for the slowest 5% of requests — the real user experience tail, not the average.

⚠️ **Warning:** Average latency can look fine while p95 is terrible. BrightChamps's monitoring shows Prabandhan at 1.26s average — p95 is likely much worse.

🚩 **Red flag:** Team doesn't know their p95 latency = no performance observability.

---

### 3. Which operations are currently synchronous that could be moved to async queues?

*What this reveals:* Where the low-hanging scalability improvements are.

**Candidates for async:**
- Third-party integrations (CRM sync, email delivery)
- Non-critical writes (analytics events, activity logs)
- Background processing (image resizing, report generation)

⚠️ **Risk:** Every synchronous third-party call is a latency and reliability risk.

---

### 4. Do we have circuit breakers on inter-service calls — and what happens when a downstream service is slow or unavailable?

*What this reveals:* Resilience against cascading failure.

✅ **Correct answer:** Specific circuit breaker configurations per service.

🚩 **Red flags:**
- "I don't know"
- "We haven't implemented circuit breakers yet"

⚠️ **Risk:** A slow service can cascade to total system failure. The 30-second timeout in the BrightChamps monitoring KB is the symptom of missing circuit breakers.

---

### 5. What's our horizontal scaling strategy for the database — do we use read replicas or caching for high-read-volume queries?

*What this reveals:* Whether the database is the current or imminent scaling bottleneck.

**The constraint:** Databases can't scale horizontally as easily as stateless services.

| Scenario | Result |
|----------|--------|
| All queries → single primary without caching/replicas | Database CPU/connection limits hit first |
| Redis caching + read replicas | High-frequency reads distributed, primary protected |

✅ **Healthy setup:**
- Redis caching for high-frequency reads
- Read replicas for the MySQL RDS instance

---

### 6. How does the system behave during traffic spikes — is scaling automatic (auto-scaling), or does it require manual intervention?

*What this reveals:* Whether scaling is reactive (manual) or proactive (automatic).

| Approach | Response Time | Outcome |
|----------|---------------|---------|
| Manual scaling | Human logs in → adds capacity | Spike causes degradation before capacity arrives |
| Auto-scaling (HPA) | CPU/memory threshold breached → pods scale up instantly | Capacity scales with demand |

✅ **AWS EKS example:** Horizontal Pod Autoscaler (HPA) scales pods automatically when thresholds breached.

**Ask for specifics:**
- Which services have auto-scaling configured?
- What triggers it?
- What's the maximum scale-out capacity?

---

### 7. What's our database migration strategy for the MongoDB self-hosted on EC2 — is this in the scaling roadmap?

*What this reveals:* Whether operational scaling debt is acknowledged and planned.

| Approach | Scaling Burden | Operational Overhead |
|----------|----------------|----------------------|
| Self-hosted MongoDB on EC2 | Manual | High — adding nodes, replica sets, sharding |
| MongoDB Atlas | Automatic | Low — managed service handles it |

🚩 **Signal:** "We've discussed it but haven't prioritized it" → ask when current setup hits bottleneck.

## W4 — Real product examples

### BrightChamps — Scalability patterns in production

**What:** Full microservices architecture on AWS EKS with SQS, Lambda, CloudFront, RDS, and Redis. EKS enables horizontal scaling of individual services independently.

**Why:** During peak class scheduling (weekday evenings across India, Vietnam, Thailand), services like Paathshala (class service) and Doordarshan (meetings service) scale without affecting others.

**Takeaway:** These aren't theoretical concerns—they're real bottlenecks in production systems.

**Active gaps documented in runbooks:**
- **CRM sync operations:** 1.2–1.3s (should be async)
- **Inter-service calls:** Lack circuit breakers (causing 30-second hangs)
- **Database:** MongoDB self-hosted on EC2 rather than Atlas (limited auto-scaling)

---

### Netflix — Stateless microservices at 200+ million users

**What:** 700+ independent, stateless, horizontally scalable microservices serving 200 million subscribers.

**Why:** The 2011 Netflix streaming outage (AWS us-east-1 failure took down entire service) drove the shift to multi-region, stateless design.

**How reliability is verified:** Chaos Monkey deliberately kills random production instances to verify automatic recovery—only possible in stateless, auto-scaling systems.

**Result:** 99.97%+ availability by 2020.

**Takeaway for PMs:** Stateless design is not an engineering preference—it's the prerequisite for reliability at scale.

---

### Twitter 2009-2012 — The "fail whale" years

**The anti-pattern:**

Original Rails monolith stored timeline data synchronously. When a user tweeted, the system immediately computed and wrote that tweet to every follower's timeline.

| Scale | Result |
|-------|--------|
| 100,000 users | Worked fine |
| 100 million users + celebrities with millions of followers | Single tweet = millions of synchronous DB writes = 503 errors ("fail whale") |

**The solution — Async timeline service:**
- Tweet delivery queued and processed by background workers
- Timelines for inactive users computed on-demand rather than pre-written

**Takeaway for PMs:** Synchronous fan-out to millions of users is a known anti-pattern. Any feature that writes to all followers, all subscribers, or all members of large groups requires async design.

---

### Stripe — API reliability as a product feature

**What:** Millions of API requests daily from tens of thousands of merchants.

**Published reliability target:** 99.999% uptime for payment APIs.

**Technical enablers:**
- Horizontal scaling
- Multi-region deployment
- Circuit breakers on all downstream dependencies (card networks, bank APIs)
- Extensive caching of non-real-time data
- Public status page and real-time reliability dashboard

**Takeaway for PMs:** In payments and developer-facing products, API reliability is a product feature, not just infrastructure. SLOs and reliability targets belong in the product spec.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The database is almost always the first bottleneck

> **Database Bottleneck:** The shared mutable state that cannot scale horizontally, becoming a critical constraint as application servers scale out.

**Why it happens:**
- Application servers scale horizontally easily (they're stateless)
- Databases are shared mutable state (don't scale horizontally)
- Adding more application servers increases database load faster than capacity grows

**The failure cascade:**
1. Engineers scale out application servers to handle traffic growth
2. Database CPU hits 100%
3. All queries start queuing
4. p99 latency spikes from 50ms to 5 seconds
5. Product degrades catastrophically

⚠️ **Critical timing:** This happens suddenly. The system handles increasing load fine until the database saturates, then collapses without warning.

**Prevention strategy:** Add read replicas and caching *before* the database becomes the bottleneck — not after.

⚠️ **PM accountability:** Approving growth investments without asking "how does this affect database load?" is approving a time bomb.

---

### Distributed systems introduce failure modes that don't exist in monoliths

> **Partial Failure:** In microservices, some services are up, others degraded, and user experience exists somewhere between "fully working" and "fully broken."

| Failure Mode | Mechanism | Impact |
|---|---|---|
| **False positive circuit breaker** | Circuit breaker trips incorrectly | Denies service to valid users |
| **Retry storm** | All services retry simultaneously when dependency recovers | Overwhelms the recovering service |
| **Cascading failure** | Slow service spreads degradation through dependency graph | Spreads faster than teams can diagnose |

**Real example:** BrightChamps monitoring KB documents a 30-second timeout as an open issue. Without circuit breakers, that timeout will eventually cascade.

**PM's role:** Resilience is a feature. Graceful degradation behavior belongs in the product specification.

**Questions to ask engineering:**
- What does the user see when a downstream service is unavailable?
  - *What this reveals:* Whether your team has thought through user-facing degradation vs. internal failure modes
- How do we prevent cascading failures from single slow services?
  - *What this reveals:* Whether your architecture has circuit breakers and timeout strategies in place

---

### Scalability debt is expensive to pay in the middle of growth

> **Scalability Debt Timing:** Redesigning for scalability during fast growth splits engineering attention and resources, making both feature delivery and infrastructure work suffer.

| Timing | Conditions | Outcome |
|---|---|---|
| **Wrong time** | Growth is fast, attention is split, team is undersized for both workstreams | Neither features nor infrastructure get proper attention |
| **Right time** | *Just before* the growth that will expose limits (requires accurate forecasting) | Team has capacity to do infrastructure work thoroughly while maintaining feature velocity |

⚠️ **PM risk:** Not communicating growth expectations to engineering creates the scenario where the product visibly degrades exactly when it's most important to impress new users.

## S2 — How this connects to the bigger system

### Kubernetes (03.03)
**Connection:** EKS is the orchestration layer that makes horizontal pod scaling automatic in the BrightChamps architecture. Pod scheduling, resource limits, and HPA configuration are all prerequisites to understanding how "add more servers" actually works in practice.

**Key Takeaway:** Kubernetes automates the mechanics of horizontal scaling

---

### Queues & Message Brokers (03.06)
**Connection:** Async processing via SQS is one of the two most impactful scalability patterns (alongside stateless design). The queue concept is prerequisite for understanding why synchronous third-party calls are a scalability antipattern.

**Key Takeaway:** Async messaging is essential to prevent cascading bottlenecks

---

### Caching (Redis) (02.04)
**Connection:** Redis solves the database bottleneck for read-heavy workloads. Read replicas handle read scaling at the database level; Redis caching handles it at the application level with lower latency. Both are required in a complete scalability strategy.

**Key Takeaway:** Caching layers protect databases from read saturation

---

### Load Balancing (03.08)
**Connection:** Load balancing is the mechanism that makes horizontal scaling work for incoming traffic. EKS has internal load balancing; CloudFront is the edge load balancer. L4 (TCP) vs. L7 (HTTP) load balancing affects session affinity and routing decisions.

**Key Takeaway:** Load balancers distribute traffic across scaled infrastructure

---

### Monitoring & Alerting (03.09)
**Connection:** The BrightChamps monitoring KB (New Relic, Kibana, OTEL) is the detection layer for scalability problems. You can't scale what you can't observe. p95 latency dashboards and auto-scaling triggers require monitoring infrastructure as a prerequisite.

**Key Takeaway:** Observability is the prerequisite for detecting scalability failures

---

### Incident Management (09.05)
**Connection:** Scalability failures are the most common cause of incidents in high-growth products. The incident management process defines how teams respond when a service saturates. Circuit breakers and auto-scaling reduce the blast radius; incident runbooks define what to do when they don't.

**Key Takeaway:** Incident response procedures limit damage from scalability failures

## S3 — What senior PMs debate

### Monolith vs microservices: the pendulum has swung back

| Aspect | Monolith | Microservices | Modular Monolith |
|--------|----------|---------------|------------------|
| **Deployment** | Single deployable | Independent per service | Single deployable, modular internals |
| **Scaling** | Vertical or full replication | Per-service scaling | Full replication only |
| **Operational complexity** | Low | High (discovery, tracing, latency, failures) | Low |
| **Team ownership** | Shared codebase | Independent service teams | Shared codebase, clear boundaries |
| **When to use** | <15 engineers, low traffic variance | Proven scaling needs, large teams | Most companies, until proven otherwise |

> **Modular Monolith:** A single deployable application with clean internal module boundaries, decomposed into independent services only when specific scaling or team ownership requirements justify it.

**The real debate:** Architecture decisions should depend on *your* team size, traffic patterns, and deployment frequency—not on what Netflix does. A team of 15 engineers managing 20 microservices has created more operational overhead than it can sustain.

---

### The SLO vs best-effort reliability debate

| Approach | SLO (Explicit targets) | Best-effort reliability | Informal SLOs |
|----------|----------------------|------------------------|----------------|
| **Definition** | "99.9% of API requests complete in <200ms" | "We try to keep things fast" | p95 latency targets in dashboards |
| **Investment required** | Ongoing, deliberate | Only after incidents | Minimal overhead |
| **Benefits** | Shared language, prioritization clarity | Low bureaucracy | Observability without overhead |
| **Risks** | Metric optimization over UX, bureaucratic drag | Reactive firefighting | — |
| **Best for** | Products where reliability is a differentiator (e.g., Stripe) | Internal/exploratory tools | Most B2B and internal products |

> **Service Level Objective (SLO):** An explicit reliability target defining acceptable performance for a service (e.g., uptime, latency, error rate).

**What senior PMs should know:** SLOs create clarity but can incentivize engineering to optimize metrics rather than actual user experience. Informal SLOs tracked in monitoring dashboards often provide the observability benefits for most products without the overhead.

---

### When does AI change the scalability calculus?

⚠️ **LLM inference breaks traditional scaling assumptions**

**Cost and latency reality:**
- **Per-request cost:** $0.02–0.06 (10–100x a standard API call)
- **Hardware:** GPU infrastructure, harder to scale than CPU
- **Latency:** 2–20 seconds (10–100x a standard database query)

Products adding AI features (copilots, summarization, generation) face a fundamentally different scalability problem than stateless microservices.

**Emerging patterns to reduce cost and latency:**

| Pattern | How it works | Tradeoff |
|---------|------------|----------|
| **Aggressive caching** | Identical or near-identical queries return cached results | Reduced freshness; bounded savings |
| **Model routing** | Route simple requests to cheaper/faster models (distilled models, Haiku vs Opus) | Quality variance across request types |
| **Async processing** | User submits request; result delivered asynchronously (not in response path) | Removes latency from UX but adds complexity |

**For senior PMs in 2025:** If you're building AI-native features, you need a scalability model for LLM calls that is fundamentally different from the stateless microservices patterns that work for standard APIs. This shapes pricing, latency budgets, and feature design.