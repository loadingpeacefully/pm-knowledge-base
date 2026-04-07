---
lesson: API Gateway
module: 01 — APIs and Integration
tags: tech
difficulty: working
prereqs:
  - 01.01 — What is an API: an API gateway sits in front of other APIs and intercepts all traffic
  - 01.02 — API Authentication: auth validation moves from every service into the gateway
  - 01.04 — Rate Limiting & Throttling: rate limiting is a gateway responsibility, not a per-service one
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
last_qa: 2026-04-07
---
I don't see any content between the `---` markers to reformat. The section appears to be empty.

Please provide the actual lesson content you'd like me to restructure for maximum scannability, and I'll apply the formatting transforms (comparison tables, callouts, company cards, etc.) according to your specifications.
# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The same problem solved five different times

The PM wanted to add rate limiting to the student API. Simple enough. The engineer came back with a question: "Which service?"

| Service | Owner | Codebase |
|---------|-------|----------|
| Student profiles | Student team | Separate |
| Payments | Payments team | Separate |
| Class scheduling | Scheduling team | Separate |
| Teacher data | Teachers team | Separate |
| Authentication | Auth team | Separate |

Rate limiting would need to be added to each service individually—different engineers, different code, different timelines.

**Impact:** The PM's two-day feature estimate became a three-week cross-team project.

---

### The vulnerability cascades

A month later, the security team flagged a problem: one of the seven services was validating authentication tokens using an outdated library with a known vulnerability.

⚠️ **Security Risk:** The fix required a code change in that one service. But the harder question emerged: how long had that vulnerability existed, and which other services might have the same problem?

---

### The PM's realization

**The PM asked:** "Why doesn't every service use the same auth validation? Why isn't there one place where we check tokens before any request gets through?"

**The answer:** There wasn't one. 

*What this reveals:* This is the core problem an API gateway solves—centralizing cross-cutting concerns (authentication, rate limiting, logging) so they're implemented once and enforced everywhere.

## F2. What it is — the hotel lobby

> **API Gateway:** A server that sits in front of all backend services and handles cross-cutting concerns (authentication, rate limiting, routing) before requests reach business logic.

### The Hotel Analogy

Every guest needs to check in, show ID, and get a room key before accessing anything. The hotel doesn't make each floor handle its own check-in—there's one front desk. Every guest goes through it. The floors don't worry about whether someone is actually allowed to be there.

**An API gateway is the front desk for all API traffic.**

Every request from every client—mobile app, web browser, third-party partner—goes through the gateway first. Backend services don't handle any of this themselves.

### Three Core Responsibilities

| Function | What it does | Benefit |
|----------|------------|---------|
| **Authentication** | Validates tokens centrally. "Is this request from someone allowed to be here?" | Backend services trust that authenticated requests made it past the gateway |
| **Rate limiting** | Tracks request counts and blocks/slows excessive traffic. "Is this person sending too many requests?" | Prevents service overload before requests arrive |
| **Routing** | Maps request paths to destinations. "/api/students" → student service, "/api/payments" → payments service | Services don't need to know about each other's existence |

## F3. When you'll encounter this as a PM

### Authentication in new services
**Scenario:** Security team asks you to add auth to a new service.

| Your infrastructure | What you'll hear |
|---|---|
| **No API gateway** | "Auth needs to be implemented in the service" |
| **API gateway present** | "Auth is already handled — the new service inherits it automatically" |

### Rate limiting in sprint planning
**Scenario:** Rate limiting comes up during capacity discussions.

The real question: Is rate limiting a gateway responsibility or per-service?

- **No gateway** → Rate limiting every endpoint = multiple engineering tickets across multiple teams
- **Gateway in place** → Configured once, enforced everywhere

### Third-party API access
**Scenario:** A partner needs access to some endpoints but not others.

| Setup | Configuration effort |
|---|---|
| **Without gateway** | Manage access rules in each service |
| **With gateway** | Configure once at the gateway layer |

### New microservice proposals
**Scenario:** Engineering team proposes adding a microservice.

**Critical question to ask:** "How does it get auth and rate limiting?"

⚠️ **Red flag:** If the answer is "we'll add it to the service," the team either has no gateway or is bypassing it. Either deserves clarification.

### Incident response and latency issues
**Scenario:** An incident involves slow API responses.

The gateway is often where first symptoms appear:
- High latency
- Elevated error rates
- Request queue buildup

**Why this matters:** Understanding what sits between the client and the service helps you read incident reports faster and ask better questions during post-mortems.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Knows the gateway sits in front of services and handles auth, rate limiting, routing.
# ═══════════════════════════════════

## W1. How an API gateway actually works — the full mechanics

### Quick Reference
| Step | Action | Result |
|------|--------|--------|
| 1 | Single entry point | All requests route through gateway |
| 2 | Authentication | Token validated, user identity extracted |
| 3 | Rate limiting | Requests throttled by user/key/IP/endpoint |
| 4 | Routing | Request sent to correct backend service |
| 5 | Transformation | Headers modified, correlation ID added |
| 6 | Logging | Unified access log created |
| 7 | Delivery | Clean, verified request reaches service |

---

### **1. Every client request hits the gateway first**

Without a gateway, requests go directly to individual services. With a gateway, all requests go to a single entry point:

```
Client → API Gateway → Student Service
Client → API Gateway → Payments Service
Client → API Gateway → Class Service
```

> **API Gateway:** A single entry point that routes all client requests to appropriate backend services

**Why this matters:** The gateway's address is the only address clients need to know. Internal services can change, split, merge, or be replaced — clients remain unaffected as long as the gateway routes correctly.

---

### **2. The gateway authenticates the request**

The gateway receives the request and validates the authorization header:
- Validates JWT token signature
- Checks expiry
- Extracts user identity (ID, roles, permissions)
- Returns `401 Unauthorized` immediately if invalid

> **Trust model shift:** Backend services don't validate tokens. They trust the gateway. The gateway attaches verified user identity to forwarded requests as a header.

The backend service never sees invalid requests.

---

### **3. The gateway applies rate limiting**

After authentication, the gateway checks rate limits using the requester's identity from step 2.

**If limit exceeded:** Returns `429 Too Many Requests` immediately. Backend service never sees the request.

**Rate limiting levels available:**
- Per API key
- Per user
- Per IP address
- Per endpoint
- Per client application

⚠️ All rate limiting runs at the gateway — not in services. Enforcement happens before requests reach backend.

---

### **4. The gateway routes the request**

The gateway matches request path and method to routing rules:

```
GET  /api/v1/students/*     →  student-service:3001
POST /api/v1/payments/*     →  payments-service:3002
GET  /api/v1/classes/*      →  class-service:3003
```

> **API versioning:** Gateway routes `/api/v1/` to old service and `/api/v2/` to new service. Clients specify version; gateway delivers to correct backend.

---

### **5. The gateway transforms the request**

Before forwarding, the gateway modifies the request:

| Transformation | Purpose |
|---|---|
| Strips raw auth token | Service doesn't need it |
| Adds correlation ID | Unique identifier for tracing across services |
| Normalizes headers | Ensures service receives expected format |
| Strips internal headers | Removes debug headers service shouldn't see |

---

### **6. The gateway logs the request**

Every request is logged in one unified location:

```
Timestamp | Client Identity | Endpoint | Response Time | Status Code
```

Without a gateway, logs scatter across each service. With a gateway, one access log captures all traffic.

---

### **7. The backend service receives a clean, verified request**

The service receives a request that has already been:
- ✓ Authenticated
- ✓ Rate-limited
- ✓ Routed to the correct destination
- ✓ Transformed with necessary metadata
- ✓ Logged

The service focuses entirely on business logic. It doesn't need:
- Its own auth library
- Its own rate limiter
- Its own request logger

## W2. The decisions an API gateway forces

### Decision 1: When should we add a gateway?

| | No gateway | Add a gateway |
|---|---|---|
| **Best for** | Single service or true monolith — one codebase handles everything | 3+ services, multiple clients (web + mobile + partners), auth/rate limiting needs |
| **Engineering cost** | Low — no gateway to manage | Medium — gateway is its own deployment with its own config |
| **Cross-cutting work** | Each service implements auth, rate limiting, logging independently | One implementation, every service inherits it automatically |
| **New service onboarding** | Engineer adds auth, rate limiting, logging to new service | New service is registered in gateway config — gets everything immediately |

> **PM default:** If your engineers are telling you "we need to add rate limiting to this endpoint — it'll take two weeks," and the reason is that each service needs it separately, that's the signal. The gateway isn't a feature to ship on a roadmap; it's the solution to a recurring cost you're already paying.

**When to act:** Start without one. Add when 3+ services share the same auth model and you're repeating cross-cutting code.

---

### Decision 2: Managed or self-hosted?

| | Managed (AWS API Gateway, Google Apigee) | Self-hosted (Kong, nginx, Traefik) |
|---|---|---|
| **Best for** | Teams on AWS/GCP, serverless backends, low ops bandwidth | Teams needing custom plugins, high-volume traffic with predictable costs |
| **Cost model** | Pay per request (~$3.50 per million requests on AWS) | Fixed infrastructure cost — no per-request charges |
| **Ops burden** | None — vendor manages availability | Your team manages uptime, config, upgrades |
| **Flexibility** | Limited to vendor's plugin/feature set | Fully configurable, extensible |

> **PM default:** For most early-to-mid stage products, managed wins on time-to-value. The ops burden of self-hosted only pays off at scale or when vendor limits become real constraints.

**When to act:** Managed if you're already on AWS/GCP and traffic is <100M requests/month. Self-hosted at high scale or when per-request cost becomes meaningful.

---

### Decision 3: What goes in the gateway vs. what stays in the service?

**The rule: cross-cutting concerns go in the gateway; business logic stays in the service.**

| In the gateway | Stays in the service |
|---|---|
| Auth token validation | User permission checks (can *this* user view *this* record?) |
| Rate limiting (per API key) | Business rule throttling (only 3 free exports per day) |
| Request logging | Application-level audit logging (who changed what) |
| Routing by path/version | Routing by data (route VIP customers to premium infrastructure) |
| Header normalization | Response transformation for specific clients |

⚠️ **Risk:** Teams under deadline pressure start putting business logic in the gateway ("just check if the user has a premium plan here") because it's fast to ship. This creates a gateway that's hard to test, hard to debug, and impossible to hand off.

**Keep the gateway dumb.**

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **Where does auth token validation happen right now — in each service or in one place?** | Whether the team has centralized auth. Distributed validation creates a vulnerability surface across every service, inconsistent behavior when tokens expire, and recurring costs for each auth logic update. |
| **If we add a new microservice tomorrow, how long before it has rate limiting and auth?** | The true cost of not having a gateway. "A few days of setup" per service multiplies across all planned services. A gateway eliminates this repeat work. |
| **Is the gateway a single point of failure — what happens if it goes down?** | ⚠️ Whether the gateway has redundancy. No failover = all traffic stops on restart or crash. This is the most critical operational question before gateway adoption. Right answer: multiple instances behind a load balancer. |
| **Can we give a third party access to specific endpoints without exposing others?** | Whether the gateway supports scoped access controls. A partner needing read access to student records shouldn't reach payment endpoints. This is a gateway routing + auth scoping feature—difficult without one. |
| **Where are API access logs — are they in one place or scattered across services?** | Whether your team can reconstruct a user's request sequence during an incident. Scattered logs across 8 services = 8 dashboards to correlate. A gateway access log is the single source of truth. |
| **Does the gateway transform requests before forwarding them — and do the services know about those transformations?** | Hidden dependencies. If the gateway strips or adds headers that services depend on, a config change can silently break a service. The gateway-service contract must be documented. |
| **What's our plan if the gateway becomes a bottleneck — if every request goes through it, what's the scaling story?** | Whether the team has thought about gateway capacity. A gateway that can't handle peak traffic is worse than none, because it blocks all services simultaneously. Ask about horizontal scaling, circuit breakers, and timeout configurations. |

## W4. Real product examples

### Netflix — Zuul as the original API gateway

**What:** Built and open-sourced Zuul, their API gateway, to handle routing, auth, and resilience for hundreds of microservices. Every request from Netflix clients passes through Zuul before reaching any backend service.

**Why:** Netflix runs thousands of microservices. Without a centralized gateway, each service would need its own auth, rate limiting, and circuit breaker logic — replicated thousands of times. Zuul gave them a single place to implement cross-cutting concerns, change routing without touching services, and add resilience patterns (circuit breakers, retries, fallbacks) globally.

**Takeaway:** Zuul became the model for what API gateways should do. If your engineers propose a gateway architecture, the Netflix pattern is the reference implementation: one entry point, dumb routing, services that trust the gateway's auth context.

---

### AWS API Gateway — Managed gateway for serverless stacks

**What:** AWS offers a fully managed API gateway that handles routing, auth (via Cognito or Lambda authorizers), rate limiting, SSL termination, and logging. It charges ~$3.50 per million API calls.

**Why:** The cost model is a product decision. At low volume, managed is cheap and requires zero ops. At 500M requests/month, you're paying $1,750/month for the gateway alone — before compute costs. A high-volume B2C product that doesn't model gateway costs at scale will hit a budget surprise. The per-request pricing also creates a misaligned incentive: teams avoid building features that make more API calls because each call costs money.

**Takeaway:** When budgeting for a managed gateway, model the cost at 10× current volume. If the number becomes significant relative to your infrastructure bill, evaluate self-hosted alternatives before you need to migrate under pressure.

---

### The edtech platform — Admin backend as de facto gateway

**What:** Built a central admin backend (Prashahak BE) that handles all admin dashboard traffic and orchestrates calls to the underlying microservices (student, class, teacher, CRM, payments). It acts as a gateway for admin traffic, even if it wasn't designed as one.

**Why:** The architecture documents explicitly flagged "Introduce an API gateway layer to centralize auth, rate limiting, and routing across microservices" as an outstanding architectural recommendation. Without a formal gateway, each microservice handles its own auth token validation:

| Problem | Impact |
|---------|--------|
| Auth vulnerability in one service | Fix required individual patch instead of single gateway-level update |
| CRM service averaging 1.26-second response times | No circuit breaker — slowness propagated to callers instead of being isolated |

**Takeaway:** If your platform has a service that "talks to everything" — an admin backend, a BFF (Backend for Frontend), or a monolith facade — it's already doing gateway work informally. That's the right place to formalize the gateway pattern before the team adds the fifth service and the auth problem compounds again.

---

### Kong — Plugin-based self-hosted gateway

**What:** Kong is an open-source API gateway where every capability (auth, rate limiting, logging, transformations) is a plugin that can be enabled per route or globally. Teams configure Kong through an admin API rather than code changes.

**Why:** Enterprise products often need different auth mechanisms for different clients — JWT for mobile apps, API keys for partners, OAuth for enterprise SSO. Kong's plugin model handles this per-route without code changes to backend services. A new enterprise customer requiring SAML auth is a Kong config change, not a sprint.

**Takeaway:** When evaluating gateway tools for a B2B product, ask whether the gateway supports multiple auth mechanisms per route. A gateway that only does JWT will create engineering debt the moment your first enterprise customer requires something different.

---

### B2B SaaS multi-tenant platform — Gateway as tenant router

**What:** A B2B SaaS serving enterprise customers routed all API traffic through a gateway that read a tenant ID from each request header, validated the tenant's subscription tier, applied tier-specific rate limits, and forwarded the request to either shared or dedicated infrastructure based on the customer's contract.

| Tier | Rate Limit |
|------|-----------|
| Starter | 100 req/min |
| Enterprise | 10,000 req/min |

**Why:** Enterprise customers had contractual SLAs that required data isolation and guaranteed throughput. Without gateway-level tenant routing, every backend service would need its own tenant awareness logic. The gateway centralized the contract enforcement: a customer downgrade or upgrade changed one gateway configuration, not 8 services. When a new enterprise customer required their data to stay in a specific AWS region, the gateway was the only change needed — routing their tenant ID to a region-specific backend cluster.

**Takeaway:** In B2B SaaS, the gateway is where customer contract terms become technical policy: which tier gets which rate limit, which customer gets dedicated infrastructure, which endpoints are restricted to enterprise plans. This is a product decision, not an engineering configuration. Specify it in the contract spec before engineering designs the gateway rules.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands gateway routing, auth centralization, and the managed vs. self-hosted tradeoff.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Pattern 1: The gateway becomes a deployment bottleneck

**The problem:**
Once every service depends on the gateway for auth and routing, the gateway config lands on the critical path for every service deployment. A team deploying 10 times per day now requires gateway config reviews for each deploy. The gateway team becomes a coordination tax.

**The failure mode:**
Teams route around the gateway ("just add auth directly to this service — the gateway change would take a week") and you end up with a hybrid where some services trust the gateway and some don't. The auth contract breaks in unpredictable ways.

**PM prevention role:**
- Gateway configuration changes should be deployable independently of service deployments
- If they're coupled — if changing a route requires a service redeploy, or vice versa — the team has an architectural problem
- Own the requirement that gateway config has its own deployment path

---

### Pattern 2: Business logic creeps into the gateway

**The problem:**
The first violation is innocent: "let's just check for premium plans here, it's faster than adding it to the service." The second violation justifies itself with the first. Within 18 months, the gateway has discount logic, feature flag checks, A/B test routing by user segment, and a customer-specific header injection. None of it is tested. None of it is observable.

**The failure mode:**
When the gateway breaks, half the product breaks in ways nobody can explain.

**PM prevention role:**
- Codify the gateway's responsibility as a team standard and review it in architecture reviews
- Any PR that adds conditional logic based on user data — not request metadata — belongs in the service
- Ensure the gateway's config is readable by someone who doesn't know the business domain

---

### Pattern 3: No circuit breakers means one slow service takes down the gateway

**The problem:**
The infra monitoring docs flagged a tracker API with 30-second response times and a CRM service averaging 1.2 seconds per request. Without circuit breakers at the gateway, every request that hits those routes waits. Gateway connection pool fills with waiting threads. Other routes start timing out too. A slow payments service causes a slow student profile load — because they share a gateway that ran out of connections.

**The failure mode:**
⚠️ A single slow service can cascade to degrade or fail the entire product

**PM prevention role:**
- Before approving gateway adoption, require a circuit breaker configuration per route
- Specify: default timeouts, maximum queue depths, fallback responses
- These aren't engineering details — they determine whether your product degrades gracefully or fails catastrophically when a single service is slow

## S2. How this connects to the bigger system

### API Authentication (01.02)

The gateway is where authentication architecture becomes real.

| Concept | Role | Enforcement Point |
|---------|------|-------------------|
| JWT, API keys, OAuth | Token mechanisms | Gateway validates tokens, checks scopes, rejects invalid requests |
| Auth without gateway | N implementations | N services = N potential drift points |

**Key insight:** The gateway is the single enforcement point before requests reach business logic.

---

### Rate Limiting (01.04)

Rate limiting taught as a concept becomes a gateway configuration question in practice.

| Layer | Purpose | Implementation |
|-------|---------|-----------------|
| **Gateway-level limits** | Protect infrastructure | Token bucket, sliding window algorithms |
| **Service-level limits** | Enforce business rules | Throttling logic inside the service |

**Key insight:** These are not the same. A PM specifying rate limits must distinguish where the limit applies.

---

### API Versioning (01.06)

> **Version Routing:** Gateway receives `/v1/students` and `/v2/students`, routes each to the appropriate backend, allowing old and new versions to coexist.

**Without a gateway:** Versioning requires the service itself to maintain and route between versions — coupling the versioning contract to the service's deployment lifecycle.

**With a gateway:** Versioning responsibility sits outside the service.

---

### CI/CD Pipelines (03.04)

⚠️ **Gateway configuration is a deployable artifact.** It has its own pipeline, version history, and rollback story.

| Risk | Scenario | Prevention |
|------|----------|-----------|
| Production incident | Misconfigured gateway routes production traffic to staging | Treat configs like application code |
| Uncontrolled change | Gateway changes without review | Code review required |
| Silent failures | Post-deploy issues missed | Monitoring post-deploy |

**Deployment discipline required:** Gateway configs need review, staging tests, feature flags, and post-deploy monitoring — just like application code.

## S3. What senior PMs debate

### Gateway proliferation is the real failure mode, not gateway absence

Most engineers agree that a gateway is the right pattern for microservice auth and routing. The problem emerges at scale:

| What happens | Why it matters |
|---|---|
| Every team builds one | Admin backend, BFF, internal tools, mobile all add separate API layers |
| None is authoritative | Conflicting rate limits, duplicate auth logic |
| No single source of truth | No unified access log, no coordinated governance |

> **Gateway proliferation:** When multiple independent gateways exist across an organization, each locally optimized but globally uncoordinated.

**The real debate:** Who owns the gateway, and what prevents teams from routing around it? Without a clear owner and a clear cost for bypass, the gateway proliferates into irrelevance.

---

### Service mesh vs. API gateway — and why conflating them is a PM problem

These solve different problems at different layers:

| Dimension | API Gateway | Service Mesh |
|---|---|---|
| **Traffic direction** | North-south (external clients → system) | East-west (service ↔ service) |
| **Authentication target** | External caller | Internal service |
| **Threat model** | Public internet attacks | Malicious or compromised internal service |
| **Rate limiting** | Per-external-user | Per-internal-caller |
| **Observability** | Inbound request visibility | Inter-service call tracing |

> **API Gateway:** Handles traffic from external clients entering the system; authenticates the caller at the boundary.

> **Service Mesh:** Handles traffic between services within the system; secures internal service-to-service communication.

**The PM question for architecture reviews:** "Is this solving the external request problem, the internal service communication problem, or both — and if both, have we confirmed one tool can do it well?"

---

### AI agents break the assumptions baked into every existing gateway configuration

Traditional gateways are configured for human-scale traffic: one click → one API call → rate limit of 10–60 requests/minute. 

An AI agent completing a task makes hundreds of API calls in seconds:
- Fetching context from multiple sources
- Reading related records
- Writing state changes
- Polling for async results
- Retrying on partial failures

The agent isn't misbehaving. The gateway is measuring the wrong thing.

#### Three specific failure modes already happening in production

**1. Rate limits designed for humans block agent workflows**

| Scenario | What happens | Why it's wrong |
|---|---|---|
| 60 req/min limit + human user | Works fine; user makes ~5 calls/min | Rate limit is appropriate |
| Same limit + AI agent summarizing 12 weeks of class records | Agent needs 200 calls in <1 minute | Gateway returns `429`, agent fails or retries (hits limit again) |
| Team raises global limit to fix it | Fixes agent, enables abuse | Opens vector for malicious traffic |

**The correct fix:** Differentiate agent identity from human identity at the gateway. Apply separate rate limits per traffic type.

---

**2. Session-based auth doesn't fit agent execution patterns**

Human sessions: 15 minutes to 1 hour token expiry ✓ Works for human UX.

Agent tasks: Start session → pause for processing → resume 2 hours later.

| Token state | Human user | AI agent |
|---|---|---|
| Token expires mid-workflow | User sees login prompt, re-authenticates | No UX to re-authenticate; task fails silently |
| Duration needed | Minutes to hours | Hours to days |
| Solution | Session refresh on user action | Service accounts, long-lived API keys, or automated token refresh |

> **Session-based auth:** Authentication tied to a human user's active interaction; assumes frequent UX opportunities to refresh credentials.

**Gateway requirement:** Agent auth configuration needs service accounts, long-lived API keys, or token refresh logic separate from human session flow.

---

**3. No observability for agent vs. human traffic**

⚠️ **Risk:** When an AI feature causes API traffic spike, teams can't tell if it's user adoption, agent inefficiency, or an agent loop bug. Silent failure and cascading overload are possible.

Gateway logs show:
- ✓ Requests and status codes
- ✗ Whether call came from human or agent
- ✗ Agent task context or purpose
- ✗ Agent retry loops or failures

**Gateway requirement:** Tag and differentiate traffic by source at the auth and logging layer. Make agent identity a first-class concept.

---

#### The timing debate

**Teams that define agent-specific gateway policies BEFORE shipping their first AI feature:**
- Iterate faster on agent UX and efficiency
- Catch rate-limit and auth failures in staging
- Ship with confidence in observability

**Teams that discover the problem AFTER production incidents:**
- Retrofit policies under pressure
- Usually resort to globally raising rate limits and hoping nothing breaks
- Risk cascading failures and abuse vectors

The debate isn't whether to handle this. It's when.