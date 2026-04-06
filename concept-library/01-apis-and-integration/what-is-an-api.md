---
lesson: What is an API
module: 01 — APIs & System Integration
tags: tech
difficulty: foundation
prereqs: []
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-student-get.md
  - technical-architecture/architecture/architecture-overview.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, AI-native PM
status: ready
last_qa: 2026-04-06
---
```markdown
<!--
  LEVEL SELECTOR
  The dashboard renders one level at a time. Switch with the level toggle.
  Each level is self-contained and readable without the others.
  Foundation → Working → Strategic is the recommended reading order.
  Ex-engineers and senior PMs may start at Working or Strategic directly.
-->
```
# ═══════════════════════════════════
# FOUNDATION
# For: non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules
# Assumes: nothing. Start here if you've never had to think about how two software systems talk to each other.
# ═══════════════════════════════════

## The world before this existed

In 2006, a mid-sized bank wanted to show customers their account balance inside a new mobile app their team was building. The balance data lived in the bank's core banking system — a 20-year-old monolith that no one wanted to touch. The mobile team had two options. First: manually export balance data to a CSV every night and import it into the app's database, so data was always 12–24 hours stale. Second: hire a team of engineers to build a custom connection between the old system and the new app — a project that took 8 months, cost $2 million, and broke every time either system updated.

There was no clean way for one piece of software to ask another for specific information and get a reliable, structured answer back.

This problem wasn't unique to banks. A travel site couldn't check a hotel's live availability without screen-scraping the hotel's website — fragile code that broke every time the hotel redesigned their page. A payments company couldn't plug into an e-commerce checkout without bespoke engineering work on both sides. Every software integration was a one-off, expensive, brittle project. The internet had millions of software systems and almost no standard way for them to talk to each other.

APIs changed that. Today, the same bank can give any app a clean, documented way to ask for a customer's balance. The travel site checks 500 hotel inventories in 200 milliseconds. Stripe connects to any checkout in an afternoon, not 8 months.

## What it is

> **API (Application Programming Interface):** A defined contract that lets one piece of software request specific information or actions from another — without needing to know how the other system is built internally.

### The Restaurant Menu Analogy

| Element | Restaurant | Software |
|---------|-----------|----------|
| **The server** | Kitchen | Backend system with data or functionality |
| **The menu** | Fixed list of offerings | List of things the system will share |
| **The customer** | You | Client (app or service making requests) |
| **The intermediary** | Waiter | The API itself |
| **The contract** | What you can order, what you'll receive | Stable, defined interface |

**Key insight:** You never need to know the internal recipes, walk into the kitchen, or worry if the chef changes. The contract remains stable.

### The Three API Styles

| Style | What It Does | Best For | Example |
|-------|-------------|----------|---------|
| **REST** | Uses web URLs and standard request types to get or send data | Consumer apps; most common approach | Twitter feed loads via REST call; "like" button sends REST action |
| **GraphQL** | Client asks for exactly the fields it needs, nothing more | Mobile and data-efficient requests | Built by Facebook (2012) to solve mobile data problems |
| **gRPC** | Faster, more compact format for internal service communication | Infrastructure between company services | Less relevant for PM decisions (see lesson 03.06) |

## When you'll encounter this as a PM

### Writing a PRD for a new feature
Your feature needs data or functionality that doesn't exist in your product today — a map, a payment processor, a video call.

**Engineer question:** "What data do we need from them and what do we send back?"

*What this reveals:* They're asking you to define the API contract — the shape and flow of data between systems.

**Your role:** Understand what an API contract is so you can have this conversation meaningfully, not just say "figure it out."

---

### Sprint planning
An engineer says: "The frontend can't start until the API is built."

| Without understanding API contracts | With understanding API contracts |
|---|---|
| Tempted to start both in parallel | Know that the API contract must exist first |
| Creates rework when data shape changes | Prevent rework through parallel dependencies |
| Miss the actual blocker | Understand why the client literally cannot function without knowing what shape the data will arrive in |

**Your role:** Recognize that the API contract is a hard dependency — the client cannot be built reliably without knowing the contract first.

---

### Evaluating a third-party vendor
Integrating Stripe, Twilio, Zoom, or Salesforce means your engineers will integrate with their API.

**Questions to ask before signing:**
- Does their API have good documentation?
- What's their rate limit — how many requests per second before throttling?
- Do they have webhooks so you get notified when events happen (vs. asking repeatedly)?

**Your role:** These are PM questions. The answers directly affect your build timeline, reliability, and long-term vendor dependency.

---

### An incident happens
Your on-call engineer says: "We're getting 401s from the payment gateway."

> **401:** HTTP status code meaning "unauthorized — your credentials are invalid or expired"

**What this tells you:** Something with authentication broke, not the payment logic itself. The fix is credential-related, not a code bug.

**Your role:** Vocabulary cuts incident triage time in half.

---

### A stakeholder asks why the feature isn't done
The feature required integrating with a new vendor API. The vendor's documentation was incomplete and the endpoint behaved differently than documented.

**This is real and common.** It's a legitimate cause of delay that's independent of your team's execution.

**Your role:** Explain the delay credibly instead of shrugging. Understanding API integration challenges gives you the language to set expectations.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs, PMs 2+ years in
# Assumes: Foundation. You know what an API is. Now let's build the working model.
# Prereq: read Foundation first, or skip here if you already know the basics.
# ═══════════════════════════════════

## How it actually works

> **API Call:** An HTTP request — the same protocol your browser uses to load a webpage, now used for machine-to-machine communication.

### The 7-Step Flow

| Step | What Happens | Key Detail |
|------|--------------|-----------|
| 1. Client forms request | Specifies HTTP method (GET, POST, PUT, DELETE), endpoint URL, parameters, request body (JSON), credentials (API key or JWT token) | Example: `GET /api/v1/users/42/courses` |
| 2. Request travels | Routed over the internet like any other web traffic | Standard HTTP routing |
| 3. Auth middleware runs | Verifies caller identity and endpoint permission before any business logic | Returns 401 (unauthenticated) or 403 (unauthorized) if failed |
| 4. Input validation | Checks required fields are present and correct type | Returns 400 (bad request) with error message if failed |
| 5. Business logic executes | Queries database, calls services, applies rules, assembles response | Core work happens here |
| 6. Response returns | JSON object paired with HTTP status code | 200 = success, 201 = created, 204 = success (no content), 4xx = client error, 5xx = server error |
| 7. Client acts | Renders data, triggers next action, or handles error | User experiences result as "instant" |

**⏱️ Duration:** 50–500 milliseconds for most production APIs.

---

### REST: Stateless Resource-Based

> **REST:** Representational State Transfer — uses HTTP method to encode the action and URL to identify the resource.

**How it works:**
- Same resource, different methods: `GET /orders/123` (retrieve), `PUT /orders/123` (update), `DELETE /orders/123` (remove)
- Stateless: each request contains all needed information; no session memory on server
- Enables horizontal scaling (add more servers) and caching (GET responses stored at network layer)

---

### GraphQL: Query-Specific Data Fetching

> **GraphQL:** Single endpoint where clients send queries describing exactly what data they need.

**Example query:**
```graphql
query {
  user(id: "42") {
    name
    email
    courses {
      title
      completedAt
    }
  }
}
```

Server returns **exactly those fields — nothing more.**

| Advantage | Cost |
|-----------|------|
| Solves over-fetching (no unused fields) | Significantly more complex to implement server-side |
| Solves under-fetching (no need to chain multiple calls) | HTTP caching doesn't work out of the box |
| Clean query syntax | Poorly written resolvers create N+1 database query problems |

**When to use:** GraphQL earns its complexity when you have 3+ client types (web, mobile, third-party) with genuinely different data needs.

## The decisions this forces

| Decision | REST | GraphQL |
|----------|------|---------|
| **Best for** | Default for almost all products | Multiple client types with diverging data needs |
| **Build complexity** | Simpler | Higher operational overhead |
| **Caching** | Easier, more widely understood | Strategy-dependent, requires expertise |
| **Tooling ecosystem** | Mature, robust | Growing but specialized |
| **When to choose** | Greenfield projects without specific GraphQL conditions | (1) Multiple client types, (2) Measured over-fetching problems, (3) Team expertise present |
| **Ongoing cost** | Low | Schema management, query limits, caching strategy |
| **PM red flag** | None if default | "We want this on greenfield" without the three conditions above |

---

| Decision | Public API | Internal API |
|----------|-----------|--------------|
| **Versioning required** | ✓ Yes, always | Often skipped (mistake) |
| **Rate limiting required** | ✓ Yes, always | Sometimes skipped |
| **Documentation** | Product-grade | Often minimal |
| **Backward compatibility** | Strict guarantees | Loose, creates debt |
| **Change velocity** | Slow (deprecation cycles) | Fast (but fragile) |
| **Reality check** | Cannot change shape once published | Becomes external-facing faster than expected |
| **PM responsibility** | Own versioning and deprecation plan | Still own versioning—don't let "internal" be an excuse |

---

| Decision | Synchronous | Asynchronous |
|----------|-------------|--------------|
| **Client behavior** | Holds connection open, waits for response | Returns immediately with job ID |
| **Best for** | Fast operations (< 2 seconds) | Slow operations (PDFs, video, reports) |
| **UX risk** | Timeout failures, forced waiting | Client polls or receives webhook when complete |
| **Implementation complexity** | Simple | Higher (job queue, webhooks/polling) |
| **PM role** | Explicitly spec async pattern for slow ops | Engineers default to sync for simplicity—push back |

---

### API Versioning

> **API versioning:** A strategy to manage changes without breaking existing callers. Standard pattern: embed version in URL (`/v1/`, `/v2/`).

**Key timing:**
- Establish from day one (retrofitting is much harder)
- External deprecation cycle: 6–12 months minimum notice
- Internal deprecation cycle: 2–4 weeks notice

**PM ownership:** Own the deprecation communication plan. Engineering defaults to "we'll change it and see who complains."

---

### Rate Limiting

> **Rate limiting:** Caps on requests per second/minute/hour to prevent server saturation and cost overruns.

⚠️ **Without rate limits:** A single misbehaving client can saturate your servers. If your API calls a paid third-party service, uncontrolled usage directly impacts costs.

**PM role:** Spec rate limits as a feature, not an afterthought. Limits vary by use case—real-time search needs much higher limits than daily reports.

## Questions to ask your engineer

| Question | What this reveals | Expected answer | ⚠️ Red flag |
|----------|-------------------|-----------------|-----------|
| **"This endpoint has no rate limiting — what happens if a client hammers it with 10,000 requests per minute?"** | Denial-of-service risk and cost protection for downstream services | "We have rate limiting at the API gateway." | "We'll deal with it if it happens." |
| **"We're supporting both API keys and JWTs on this endpoint — which clients use which, and why do we need both?"** | Whether auth method sprawl creates unnecessary attack surface and test burden | A specific reason tied to client needs or migration timeline | "We inherited one and added the other" (technical debt) |
| **"If this endpoint's response shape changes — we add or remove a field — who breaks and how long do we have to migrate them?"** | Versioning posture and coordination risk across teams | Clear versioning strategy in place before changes | "We'd need to coordinate with 12 teams across 3 orgs" (missing strategy) |
| **"If our downstream service is slow — say, taking 8 seconds instead of 200ms — what happens to callers of this API?"** | Timeout and fallback behavior; cascade failure risk | "We have a 3-second timeout and return a graceful error." | "It would just be slow" (no timeout = thread exhaustion → outage) |
| **"What's our p99 latency on this endpoint over the last 30 days — and what causes the long tail?"** | Long-tail performance and whether slow degradation is understood and addressable | Specific identified causes (e.g., query degradation, distant service hop) | Vague answers or inability to articulate causes |
| **"If this endpoint has no auth and a caller can pass any user ID — can they retrieve another user's data?"** | Insecure Direct Object Reference (IDOR) vulnerability | "No, we validate that the authenticated user owns the requested resource." | ⚠️ Engineer pauses before answering — escalate immediately |
| **"What does our API gateway do for us — and what would we have to build ourselves if it disappeared?"** | Hidden dependencies and incident diagnostic clarity | Clear mapping of gateway responsibilities (auth, rate limiting, logging, SSL, routing) | Team has never inventoried what the gateway provides |
| **"For the GraphQL endpoint — do we have query complexity limits? What stops a client from sending a query that joins 15 nested objects and brings down the database?"** | Protection against database exhaustion via malicious or malformed queries | "Yes, we have a max complexity score and it's enforced." | ⚠️ Silence or "We haven't thought about that" |

## Real product examples — named, specific, with numbers

### Stripe — API design as business strategy

**What:** Founded in 2010 to solve the core problem that online payment acceptance required a separate 6-week integration with each processor. Stripe made the API itself the entire value proposition.

**Why:** Three deliberate API design choices became revenue drivers:
- **Idempotency keys** on all payment endpoints prevent double-charging on retries
- **Machine-readable error codes** let code handle specific failures programmatically instead of just logging generic failures
- **Indefinite backward compatibility** on v1 endpoints eliminate costly migrations

**Takeaway:** Stripe processes hundreds of billions annually and developers can integrate payments in an afternoon. API design quality is a direct revenue driver.

---

### Twitter/X — The cost of API concentration risk

**What:** In 2023, Twitter cut the free API tier from 1,500,000 tweets/month to 1,500 tweets/month (a 1,000x reduction) and introduced paid tiers at $100/month for basic access.

**Why:** The decision was a revenue play that backfired strategically.

**Takeaway:** Hundreds of third-party apps shut down within days. Academic researchers lost years of data access. This revealed two critical truths:
1. Rate limits and pricing are ecosystem-level product decisions
2. API-dependent businesses face existential concentration risk

⚠️ **PM question for any product relying on third-party APIs:** What happens to our product if this API doubles in price or disappears?

---

### GitHub — APIs as ecosystem distribution

**What:** GitHub exposes nearly every platform capability through public APIs — repositories, pull requests, issues, actions, notifications.

**Why:** This wasn't accidental. It was deliberate product strategy to enable thousands of external tools to build integrations.

**Takeaway:** The API became a distribution mechanism. Every CI/CD tool, code review assistant, and project management integration that hooks into GitHub creates lock-in not just for that tool's users, but for GitHub itself.

*What this reveals:* Your API strategy is your ecosystem strategy.

---

### Slack — Webhooks and the $27.7B exit

**What:** Slack's Incoming Webhooks — a simple API mechanism allowing any service to post messages to a Slack channel — required minimal engineering investment but delivered maximum strategic impact.

**Why:** Webhooks connected Slack to every other tool in the enterprise stack:
- Payment succeeds → Slack notifies
- Build fails → Slack notifies
- Support ticket opens → Slack notifies

**Takeaway:** By 2021, 2,400 third-party integrations existed. The API ecosystem — not the messaging UI — was core to the $27.7B Salesforce acquisition valuation.

*What this reveals:* Low-effort API surfaces can become your highest-leverage distribution mechanism.

---

### Zoom — Third-party API dependency as reliability risk

**What:** Zoom's well-documented API is widely used by edtech platforms, telemedicine companies, and thousands of B2B products to create meetings, retrieve recordings, and manage participant data. Multiple high-profile outages in 2020–2022 cascaded directly into dependent products.

**Why:** API reliability is not just an engineering concern. It's a product concern.

**Takeaway:** If your product calls Zoom's API to create a class link and Zoom is down, your class doesn't happen — and your users blame you, not Zoom.

⚠️ **PM responsibility:** Spec fallback behavior before launch. "What do we show users if Zoom's API returns a 503?" is a product decision, not an engineering one.

*What this reveals:* Every third-party API dependency is a reliability dependency you own in the eyes of your users.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineers turned PM, senior PMs, heads of product, AI-native PMs
# Assumes: Working Knowledge. Skip to here if you've built on APIs before.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## What breaks and why

### Internal-only APIs become load-bearing systems

> **The "internal-only" trap:** Building an internal API assuming it will always stay internal, then discovering it has accumulated unknown consumers across the organization.

**What happens:**
- First one service calls it → then three → then twelve
- Original team changes; new stakeholders depend on it unknowingly
- API's behavior becomes load-bearing for systems its authors never anticipated
- When change is finally needed, migration cost is enormous because no one tracked consumers or their assumptions

**The fix:**
Apply contractual discipline from day one, regardless of intended audience:
- Document all APIs (internal and external)
- Version them
- Treat internal callers as you would external developers

**Why it matters:** The upfront effort is small. The alternative is months of migration work.

---

### Rate limit design as reactive firefighting

> **Rate limiting:** Rules that cap how many API requests a client can make in a given timeframe, preventing any single consumer from overwhelming the service.

**Common failure mode:** Rate limits added only after the first incident where a runaway client saturates the service.

**The correct pattern:**
- Design rate limits as part of the API spec (not afterward)
- Test them explicitly
- Document them clearly

**The scaling trap:** Rate limits designed for current traffic become inadequate as you scale.

| Scenario | Today | 18 months (10x growth) |
|----------|-------|------------------------|
| Current limit | 100 requests/sec per client (generous) | Bottleneck |
| Impact | ✓ Adequate headroom | ✗ Blocks legitimate traffic |

**PM responsibility:** Own rate limit review as part of growth planning. If you're projecting 10x user growth, model what that does to API call volumes.

---

### Consistency vs. availability at the API layer

> **Distributed systems consistency problem:** When multiple services must stay in sync (payment recorded → delivery triggered → notification sent) and any step can fail, your API design must handle cascade failures.

**The naive pattern (breaks silently):**
```
Payment succeeds → Delivery trigger fails → Notification never fires
↓
User's order is in broken state, but no immediate error signal
```

**Correct patterns** (architectural decisions PMs must recognize):
- **Idempotent operations** — Same request called twice has same effect as once
- **Event sourcing** — Record intent as immutable events, rebuild state from them
- **Compensating transactions** — If step N fails, automatically undo steps 1 through N-1

**PM responsibility:** Understand these well enough to ask about them in sprint review. You're not implementing them—you're identifying when they're absent and escalating.

---

### Documentation lag as a conversion killer

> **Documentation lag:** Production API docs that drift from reality, reflecting the API at some historical point before fixes, new fields, or tightened limits.

**What developers encounter:**
- Edge cases fixed but docs never updated
- New required fields undocumented
- Rate limits tightened but old limits still published
- Wasted hours debugging failures better docs would prevent

**Impact varies by API type:**

| API Type | User | Cost of Poor Docs |
|----------|------|-------------------|
| Internal | Your own engineers | Productivity tax on your team |
| External | Outside developers | Direct conversion rate problem |

**The conversion killer:** Developers who can't get a quick successful call will move on to competitors.

**PM responsibility:**
- Treat API documentation as a first-class deliverable, not an afterthought
- Define a clear owner for keeping docs current
- Review docs as part of launch readiness (don't wait for complaints)

## How this connects to the bigger system

APIs are the connective tissue of everything else in the curriculum. Understanding APIs is the prerequisite for understanding most of what follows.

| Topic | Connection | Why it matters |
|-------|-----------|----------------|
| **Authentication (01.02)** | How an API knows who is calling it | Every API security decision (API keys, JWTs, OAuth2 scopes) is an API design decision. This lesson builds directly on the mental model established here. |
| **Webhooks vs Polling (01.03)** | Two fundamentally different API calling patterns | Polling = client repeatedly asking "is it done yet?" Webhooks = API calls you when something happens. Understanding the tradeoff requires knowing what an API call costs (latency, rate limit budget, server load). |
| **Rate Limiting (01.04)** | A core surface of API management | Foundation establishes *why* rate limiting decisions matter; the full lesson goes deep on strategies and PM decisions. |
| **Databases (Module 02)** | Almost always what APIs retrieve from or write to | API design choices (which fields are included, whether queries are paginated, how filtering works) directly affect database query patterns, index usage, and query performance. |
| **Monitoring and Alerting (03.09)** | Production observability is largely API metrics | What you monitor: latency percentiles, error rates by status code, request volumes, rate limit hits. SLA and SLO concepts only make sense against a specific observable: API response time. |
| **AI Agent Patterns (04.09)** | Modern AI agents are API orchestrators | They receive a task, call a sequence of APIs to gather information or take actions, and synthesize a response. Understanding APIs is foundational for designing, speccing, and evaluating agentic AI products. |

## What senior PMs debate

### Platform API strategy: When to expose public APIs?

**The core tension:**
- **"As soon as you have product-market fit"** → Maximize opportunity, early partner lock-in
- **"Only when a specific partner demands it"** → Minimize cleanup costs, defer investment

**What this reveals:** Most teams face the opposite problem: they build for internal use, accumulate technical debt in the API layer, then face enormous cleanup work when opening up. The real question is your risk tolerance for cleanup cost vs. opportunity cost of waiting.

**Real stakes:** Stripe, GitHub, and Slack deliberately positioned API-as-distribution. But most organizations don't have this choice early — they must decide retroactively.

---

### GraphQL's decade-long "is it the future?" debate

| Dimension | GraphQL | Well-designed REST |
|-----------|---------|-------------------|
| **Status** | "The future" since 2015 | Still dominant in new projects |
| **Client flexibility** | High (query what you need) | Lower (fixed payloads) |
| **Over-fetching** | Eliminated | Still a risk |
| **At scale, risks** | Schema drift, resolver performance, documentation debt | Over-engineered, verbose contracts |

**GitHub's adoption (2016):** Switched public API to GraphQL v4 for client flexibility and reduced over-fetching.

**What this reveals:** GraphQL is a **team capability investment**, not just a technical choice. Success depends on organizational discipline. Undisciplined GraphQL adoption often produces worse outcomes than REST.

---

### AI is rewriting the API contract itself

⚠️ **Non-deterministic APIs challenge traditional PM assumptions**

| Traditional API | AI Inference API |
|-----------------|------------------|
| Same input → same output | Same input → different outputs (temperature > 0) |
| Predictable latency | Variable latency (500ms–30s) |
| Correctness = pass/fail tests | Correctness = eval metrics |

**New PM decisions:**
- What guarantees do you make to users when your product calls an AI API?
- How do you handle AI latency in UIs designed for instant responses?
- How do you detect regression when Anthropic/OpenAI/Google changes their models?

**What this reveals:** PMs building AI products are in genuinely uncharted territory. There are no settled answers yet.

---

### AI API costs = new business model constraints

⚠️ **Every LLM API call is a direct COGS line item**

**The math that changes everything:**
- $0.01–$0.15 per 1,000 tokens (current range)
- 100,000 users × 10 requests/day = **real money**

**This inverts the PM's decision framework:**

| Decision | Before AI APIs | With AI APIs |
|----------|---|---|
| "Add this feature?" | Product question | Product + unit economics question |
| "Use AI here?" | Optional enhancement | Explicit business model choice |

**Competitive advantage:** Teams that carefully select which interactions warrant LLM calls (vs. cheaper deterministic logic) will outcompete those that default to "add AI everywhere."

**What this reveals:** Cost structure is not just an operations problem—it's a strategic constraint on product design.

## Prerequisites

→ None — this is Module 01's entry point

## Next: read alongside (companions)

| Lesson | Why read it | Timing |
|--------|-------------|--------|
| **01.02 API Authentication** | How access to an API is controlled | Read immediately after this |
| **01.03 Webhooks vs Polling** | Two patterns for getting data from external systems | Read next |

## Read after (deepens this lesson)

| Lesson | Purpose |
|--------|---------|
| **01.04 Rate Limiting & Throttling** | Deep dive on the limits introduced here |
| **01.05 Idempotency** | Full explanation of the payment retry problem (Stripe example from W4) |
| **03.06 Queues & Message Brokers** | Complete coverage of the asynchronous pattern referenced in W2 |
| **04.09 AI Agent Patterns** | How agents orchestrate APIs; requires this lesson as foundation |