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

# FOUNDATION

**For:** Non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules

**Assumes:** Nothing. Start here if you've never had to think about how two software systems talk to each other.

**Recommended approach:** Read Foundation first, then progress to Working Knowledge and Strategic Depth as your confidence grows.
```

## The world before this existed

In 2006, a mid-sized bank wanted to show customers their account balance inside a new mobile app their team was building. The balance data lived in the bank's core banking system — a 20-year-old monolith that no one wanted to touch. The mobile team had two options. First: manually export balance data to a CSV every night and import it into the app's database, so data was always 12–24 hours stale. Second: hire a team of engineers to build a custom connection between the old system and the new app — a project that took 8 months, cost $2 million, and broke every time either system updated.

There was no clean way for one piece of software to ask another for specific information and get a reliable, structured answer back.

This problem wasn't unique to banks. A travel site couldn't check a hotel's live availability without screen-scraping the hotel's website — fragile code that broke every time the hotel redesigned their page. A payments company couldn't plug into an e-commerce checkout without bespoke engineering work on both sides. Every software integration was a one-off, expensive, brittle project. The internet had millions of software systems and almost no standard way for them to talk to each other.

APIs changed that. Today, the same bank can give any app a clean, documented way to ask for a customer's balance. The travel site checks 500 hotel inventories in 200 milliseconds. Stripe connects to any checkout in an afternoon, not 8 months.



## What it is

> **API (Application Programming Interface):** A defined contract that lets one piece of software request specific information or actions from another — without needing to know how the other system is built internally.

### The Restaurant Menu Analogy

| Element | In a Restaurant | In Software |
|---------|-----------------|-------------|
| **The System** | Kitchen | Backend server |
| **The Contract** | Fixed menu | List of available requests |
| **How You Interact** | Point at menu, speak to waiter | Use standard request format |
| **What You Get** | Exactly what's described | Data or action as specified |
| **What You Don't Need** | Kitchen knowledge, recipes, chef details | Internal system knowledge, implementation details |
| **Stability** | Menu stays consistent | API contract stays consistent |

### Three API Styles

| Style | How It Works | Best For | Example |
|-------|-------------|----------|---------|
| **REST** (most common) | Uses web URLs and standard request types to get or send data | Consumer apps, public-facing services | Loading Twitter feed (GET request); sending a like (POST request) |
| **GraphQL** | Client asks for exactly the fields it needs, nothing more | Mobile apps with bandwidth constraints; precise data needs | Instead of downloading full user profile, request only name + avatar |
| **gRPC** | Faster, more compact format for internal service communication | Company infrastructure, backend-to-backend | Internal microservice communication (covered in lesson 03.06) |

## When you'll encounter this as a PM

| Scenario | What happens | Why it matters |
|----------|--------------|----------------|
| **Writing a PRD for a new feature** | Your feature needs external data or functionality (map, payment processor, video call). Engineer asks: "What data do we need from them and what do we send back?" | You need to understand API contracts to have this conversation meaningfully, not just delegate it. |
| **Sprint planning** | Engineer says "frontend can't start until the API is built." | Without understanding why the API contract must exist first, you'll be tempted to parallelize work and create rework. The contract shape must be known before consuming code can be built reliably. |
| **Evaluating a third-party vendor** | Before integrating Stripe, Twilio, Zoom, or Salesforce, engineers will need their API. | You must ask the PM questions: Is documentation good? What's the rate limit? Do webhooks exist? These answers directly affect build timeline, reliability, and long-term vendor dependency. |
| **An incident happens** | On-call engineer: "We're getting 401s from the payment gateway." | A 401 = "unauthorized — credentials invalid or expired." This tells you the issue is authentication, not payment logic. Vocabulary cuts incident triage time in half. |
| **Stakeholder asks why the feature isn't done** | Feature required integrating a new vendor API. Vendor documentation was incomplete; endpoint behaved differently than documented. | This is a real and common delay cause. Understanding API integration complexity lets you explain credibly instead of shrugging. |

## How it actually works

> **API call:** An HTTP request — the same protocol your browser uses to load a webpage, now used for machine-to-machine communication.

### 7-Step API Flow

| Step | What happens | Key detail |
|------|--------------|-----------|
| 1. Client forms request | Specifies HTTP method (GET, POST, PUT, DELETE), endpoint URL, parameters, request body (JSON), credentials (API key/JWT in headers) | Example: `GET /api/v1/users/42/courses` |
| 2. Request travels to server | Routed over the internet like any other web traffic | 50–500ms round trip for production APIs |
| 3. Auth middleware runs | Validates identity and permissions before any business logic executes | Returns 401 (unauthenticated) or 403 (unauthorized) if rejected |
| 4. Input validation | Confirms all required fields present and correct types | Returns 400 (bad request) with specific error message if invalid |
| 5. Business logic executes | Server queries database, calls services, applies rules, assembles response | Core operation |
| 6. Response returns | JSON object paired with HTTP status code (200 = success, 201 = created, 204 = success/no content, 4xx = client error, 5xx = server error) | Client reads status code first, then parses body |
| 7. Client acts on response | Renders data, triggers next action, or handles error | User experiences as "instant" |

---

### REST in depth

> **REST (Representational State Transfer):** Uses the HTTP method to encode the action and the URL to identify the resource.

**How it works:**
- Same resource, different methods: `GET /orders/123` retrieves, `PUT /orders/123` updates, `DELETE /orders/123` deletes
- Stateless — each request contains all needed information, no server-side session memory
- Enables horizontal scaling (add more servers easily) and network-layer caching

---

### GraphQL in depth

> **GraphQL:** A single-endpoint API where clients send queries describing exactly what data they need.

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

**Solves:**
- Over-fetching — you get only requested fields, not unnecessary ones
- Under-fetching — one query can span multiple resources

**Trade-offs:**

| Advantage | Disadvantage |
|-----------|--------------|
| Precise data retrieval | Significantly more complex to implement server-side |
| Works across multiple client types (web, mobile, third-party) | HTTP caching doesn't work out of the box |
| Reduces network calls | Poorly written resolvers create N+1 database query problems |

**When to use:** GraphQL earns its complexity when you have 3+ client types with genuinely different data needs.

## The decisions this forces

| Decision | Default | When to reconsider | Watch out for |
|----------|---------|-------------------|---------------|
| **REST vs GraphQL** | REST | Multiple client types with diverging data needs + measured over-fetching performance problems + team GraphQL expertise | GraphQL adds ongoing complexity: schema management, query limits, caching strategy |
| **Public vs Internal API** | Treat all as public | Speed of iteration needed | "Internal-only" becomes external-facing faster than expected; internal APIs accumulate debt without versioning |
| **Synchronous vs Asynchronous** | Depends on operation speed | Operations > 2 seconds (PDF generation, video processing, reports) | Engineers default to sync for simplicity even when it creates timeout failures and poor UX |
| **API Versioning** | Version from day one | Never (establish immediately) | Retrofitting versioning later is far harder than building it in |
| **Rate Limiting** | Required for all public APIs | Cost protection when calling paid services | Easy to overlook; depends heavily on use case (real-time search ≠ daily report) |

### REST vs GraphQL

> **REST:** Representational State Transfer. Simpler to build, easier to cache, more widely understood, better tooling.

> **GraphQL:** Query language that lets clients request exactly the data they need. Worth the complexity only when all three conditions exist:
> 1. Multiple client types with diverging data needs
> 2. Over-fetching causing *measured* (not hypothesized) mobile performance problems
> 3. Your team has GraphQL expertise

**If someone proposes GraphQL on a greenfield project without these conditions, push back.** The operational complexity is real and ongoing.

---

### Public API vs Internal API

> **Public API:** Exposed to external developers. Requires versioning strategy, rate limiting, backward compatibility guarantees, documentation as a product.

> **Internal API:** Used only within your company. Can move faster but easily accumulates technical debt.

**Once you publish an API and developers build on it, you cannot change its shape without breaking their integrations.**

**PM action:** Push your team to document and version *all* APIs, not just public-facing ones. "Internal-only" APIs become external-facing faster than anyone expects.

---

### Synchronous vs Asynchronous

| Type | How it works | Best for | Problem |
|------|-------------|----------|---------|
| **Synchronous** | Client holds connection open; server responds immediately | Fast operations (< 2 seconds) | Creates timeout failures and user wait time for slow operations |
| **Asynchronous** | Server returns "request received" + job ID; client polls or receives webhook when complete | Slow operations: PDF generation, video processing, reports | Requires more engineering work |

**PM implication:** If your feature involves a slow backend operation, spec the async pattern explicitly. Engineers often default to synchronous because it's simpler to implement, even when it creates poor UX.

---

### API Versioning from Day One

> **API Versioning:** Embedding version in URL (e.g., `/v1/`, `/v2/`) so that changes don't break existing callers.

**Establish versioning at the start, not retrofit.** Every API will change. The question is whether changes break existing callers.

**Deprecation timelines:**
- External consumers: 6–12 months notice minimum
- Internal consumers: 2–4 weeks notice

**PM role:** Own the deprecation communication plan. Engineering often defaults to "we'll just change it and see who complains."

---

### Rate Limiting

> **Rate Limiting:** Caps on how many requests a caller can make per second/minute/hour.

⚠️ **Without rate limits:** A single misbehaving client can saturate your servers.

⚠️ **Cost risk:** If your API calls a paid third-party service underneath, rate limits protect your cost structure.

**PM action:** Spec rate limits as a feature, not leave them as an afterthought. The right limits depend on your use cases:
- Real-time search feature → higher limits needed
- Daily report → lower limits acceptable

## Questions to ask your engineer

| # | Question | *What this reveals:* | Expected Answer | ⚠️ Concerning Answer |
|---|----------|---------------------|-----------------|----------------------|
| 1 | "This endpoint has no rate limiting — what happens if a client hammers it with 10,000 requests per minute?" | Denial-of-service risk and cost protection for downstream services | "We have rate limiting at the API gateway." | "We'll deal with it if it happens." |
| 2 | "We're supporting both API keys and JWTs on this endpoint — which clients use which, and why do we need both?" | Technical debt and attack surface awareness | A specific reason tied to client requirements | "We inherited one and added the other." |
| 3 | "If this endpoint's response shape changes — we add or remove a field — who breaks and how long do we have to migrate them?" | Your versioning posture and coordination overhead | A clear versioning strategy in place | "We'd need to coordinate with 12 teams across 3 orgs." |
| 4 | "If our downstream service is slow — say, taking 8 seconds instead of 200ms — what happens to callers of this API?" | Timeout and fallback behavior; cascade failure risk | "We have a 3-second timeout and return a graceful error." | "It would just be slow." |
| 5 | "What's our p99 latency on this endpoint over the last 30 days — and what causes the long tail?" | Whether slow outlier requests are monitored and addressable | Specific root causes identified and fixable (e.g., database query degradation, distant service hops) | Vague answers or no monitoring of tail latency |
| 6 | "If this endpoint has no auth and a caller can pass any user ID — can they retrieve another user's data?" | Insecure direct object reference (IDOR) vulnerabilities | "No, we validate that the authenticated user owns the requested resource." | ⚠️ Engineer pauses or says "probably yes" |
| 7 | "What does our API gateway do for us — and what would we have to build ourselves if it disappeared?" | Hidden dependencies and incident diagnosis capability | Clear mapping of gateway responsibilities (auth, rate limiting, logging, SSL, routing) | "We've never really mapped it out." |
| 8 | "For the GraphQL endpoint — do we have query complexity limits? What stops a client from sending a query that joins 15 nested objects and brings down the database?" | Query complexity enforcement and database protection | "Yes, we have a max complexity score and it's enforced." | ⚠️ Silence or "we haven't thought about that" |

---

> **Technical Debt:** Inherited security decisions (like dual auth methods) that persist without active justification, accumulating surface area and testing burden.

> **Insecure Direct Object Reference (IDOR):** A vulnerability where an endpoint fails to validate that the authenticated user has permission to access the resource they're requesting by ID.

> **P99 Latency:** The response time threshold below which 99% of requests complete; the slowest 1% of users experience this latency or worse.

⚠️ **Security escalation trigger:** If an engineer hesitates on questions 6 or 8, treat as a potential vulnerability requiring immediate review. Do not defer.

## Real product examples — named, specific, with numbers

### Stripe — API design as revenue multiplier

**What:** Founded 2010 on a single insight: online payments required 6-week integrations per processor. Stripe made the API the entire value proposition.

**Design choices as business decisions:**
- Idempotency keys on all payment endpoints (retry safety = no double-charges)
- Machine-readable error codes (code handles failures programmatically, not just log strings)
- Backward compatibility guaranteed indefinitely on v1 endpoints

**Why:** Eliminates entire categories of developer friction.

**Takeaway:** Processes hundreds of billions annually. A developer integrates payments in an afternoon. *API design quality is a direct revenue driver.*

---

### Twitter/X — rate limits as existential risk

**What:** 2023 API overhaul: free tier collapsed from 1,500,000 tweets/month → 1,500 tweets/month (1,000x reduction). Paid tiers introduced at $100/month for basic access.

**Immediate consequence:** Hundreds of third-party apps shut down within days. Academic researchers lost years of data access.

| Dimension | Before | After |
|-----------|--------|-------|
| Free tier quota | 1.5M tweets/month | 1.5K tweets/month |
| Price multiplier | Baseline | ~67x increase to maintain usage |
| Ecosystem viability | Thousands of dependent tools | Rapid collapse |

**Why:** Rate limits and pricing are *product strategy decisions with enormous ecosystem consequences*.

**Takeaway:** Every PM building on a third-party API must answer: *"What happens to our product if this API doubles in price or disappears?"* This isn't hypothetical. API-dependent businesses have existential concentration risk.

---

### GitHub — API as ecosystem distribution engine

**What:** GitHub exposes nearly every platform capability through public API: repositories, pull requests, issues, actions, notifications. Deliberate product strategy, not afterthought.

**Outcome:** Thousands of tools built on top. CI/CD tools, code review assistants, project management integrations all depend on GitHub API.

**Why:** The API became a distribution mechanism *and* a lock-in multiplier. Every tool that integrates with GitHub's API creates lock-in not just for that tool's users, but for GitHub itself.

**Takeaway:** *Your API strategy is your ecosystem strategy.* API access compounds your competitive moat.

---

### Slack — webhooks as $27.7B acquisition driver

**What:** Incoming Webhooks — simple API mechanism allowing any service to post a message to a Slack channel.

**By 2021:**
- 2,400 third-party integrations
- Every tool in a company's stack connected to Slack
- Payment succeeds → Slack notifies. Build fails → Slack notifies. Support ticket opened → Slack notifies.

**Investment required:** Almost none. Engineering-light, impact-massive.

**Why:** The API ecosystem — not the messaging UI — became core to product value.

**Takeaway:** Salesforce's $27.7B acquisition price was largely a bet on the integration network, not the chat interface.

---

### Zoom — API reliability cascades into dependent products

**What:** Well-documented API. Widely used by edtech platforms, telemedicine companies, thousands of B2B products to create meetings, retrieve recordings, manage participants.

**Problem 2020–2022:** Multiple high-profile outages. When Zoom's API is down:
- Edtech platform can't create class links → classes don't happen
- Telemedicine app can't spawn meeting rooms → appointments fail
- *Your users blame you, not Zoom*

| Failure Point | Your Control? | User Attribution |
|---------------|---------------|------------------|
| Zoom API outage | ❌ No | ✅ Your product |
| Your fallback behavior | ✅ Yes | ✅ Your product |
| User experience | ✅ Yes | ✅ Your product |

⚠️ **Every third-party API dependency is a reliability dependency.**

**PM responsibility:** Spec fallback behavior *before launch*. "What do we show the user if Zoom's API returns a 503?" is a product decision, not an engineering one.

**Takeaway:** Dependency risk requires explicit fallback design. Don't discover this during an outage.

## What breaks and why

### The "internal-only" trap

> **Internal API:** An API built for use only within your organization, with no external consumers.

The most reliably expensive API mistake is building an internal API with the assumption that it will always be internal. Internal APIs accumulate consumers:
- First one service calls it
- Then three services call it
- Then twelve services call it

**The problem:** The original team changes. The API's behavior becomes load-bearing for systems its authors never anticipated. When someone eventually needs to change the API — and they always do — the migration cost is enormous because no one tracked who was consuming it, under what assumptions.

**The fix:**
- Document all APIs regardless of audience
- Version them from day one
- Treat internal callers as you would external developers

*The effort is small. The alternative is months of migration work.*

---

### Rate limit design as an afterthought

> **Rate limit:** A cap on the number of requests a client can make to an API within a specified time period.

Rate limits are almost always added reactively — after the first incident where a runaway client saturates the service.

| Failure mode | Impact | Prevention |
|---|---|---|
| No rate limits initially | Incident-driven discovery | Design limits as part of API spec |
| Limits designed for current traffic | Becomes bottleneck as product scales | Review limits during growth planning |
| Example: 100 req/sec per client | Adequate today, inadequate in 18 months | Project traffic growth (10x?) and stress-test limits |

**PM responsibility:** Own the rate limit review as part of growth planning. If you're projecting 10x user growth, what does that do to API call volumes?

---

### The consistency vs. availability tradeoff at the API layer

> **Distributed systems consistency problem:** When multiple services need to stay synchronized and any step in a transaction chain can fail.

**The scenario:** A payment is recorded → a delivery is triggered → a notification is sent.

| Approach | How it fails | Outcome |
|---|---|---|
| Synchronous chain of API calls (naive) | Silent failure in middle step | Payment succeeds, delivery trigger fails, notification never fires. Order is in broken state. |
| Idempotent operations, event sourcing, compensating transactions (correct) | Designed to handle partial failures | Order state remains recoverable |

⚠️ **Risk:** This is an architectural decision that surfaces directly in your API design. PMs need to understand these patterns well enough to ask about them in sprint review — not implement, but identify when they're absent.

---

### Documentation lag kills developer experience

Every production API has documentation. The documentation is almost never accurate.

**Common causes of documentation drift:**
- Reflects the API at some point in the past
- Misses the three edge cases that got fixed
- Undocumented new required fields
- Tightened rate limits not reflected

**The impact:**
- Internal APIs: productivity tax on your own engineers
- External APIs: direct conversion rate problem — developers who can't get a quick successful call will move on

**PM responsibility:**
- Make API documentation a first-class deliverable, not an afterthought
- Define a clear owner for keeping it current
- Review documentation accuracy as part of the release checklist

## How this connects to the bigger system

APIs don't exist in isolation — they're the connective tissue of everything else in the curriculum. Understanding APIs is the prerequisite for understanding most of what follows.

| Lesson | Connection | Why it matters |
|--------|-----------|----------------|
| **Authentication (01.02)** | API knows who is calling it | Every API security decision (API keys, JWTs, OAuth2 scopes) is an API design decision |
| **Webhooks vs Polling (01.03)** | Two fundamentally different API calling patterns | Understanding API call costs (latency, rate limit budget, server load) is essential to evaluate the tradeoff |
| **Rate Limiting (01.04)** | Surface of API management | Foundation here establishes why PM decisions about strategy matter |
| **Databases (Module 02)** | Almost always what APIs retrieve from or write to | API design choices (fields included, pagination, filtering) directly affect database query patterns and performance |
| **Monitoring and Alerting (03.09)** | Production observability is largely API metrics | SLA and SLO concepts only make sense against specific observables like API response time |
| **AI Agent Patterns (04.09)** | Modern AI agents are API orchestrators | Agents call sequences of APIs to gather information or take actions — understanding APIs is foundational for designing agentic products |

## What senior PMs debate

### Platform API strategy: When to expose public APIs?

**The tension:** Build for internal use first (accumulate technical debt) vs. invest in public API readiness upfront (opportunity cost).

| **"API-as-platform from day one"** | **"Only when a partner demands it"** |
|---|---|
| Requires investment at product-market fit | Reduces speculative infrastructure spend |
| Enables network effects like Stripe, GitHub, Slack | Avoids cleanup work if demand never materializes |
| Higher upfront cost | Higher future cleanup cost |

> **Key insight:** This debate reflects risk tolerance, not right answers. Different product strategies legitimately choose different paths.

---

### GraphQL: A decade of "the future" — and REST still wins

**What happened:** Facebook released GraphQL in 2015. It's been "the future of APIs" ever since. REST remains dominant in new projects.

**The real debate now:** Not GraphQL vs. REST, but GraphQL vs. well-designed REST with thoughtful resource modeling.

| **Adoption success** | **Adoption struggles** |
|---|---|
| GitHub (switched public API to GraphQL v4, 2016) | Schema drift in less disciplined orgs |
| Client flexibility, reduced over-fetching | Resolver performance problems |
| | Documentation debt worse than REST |

> **PM perspective:** GraphQL is a *team capability investment*, not just a technical choice. The technology only works if your organization can maintain discipline around schema design and resolver performance.

---

### AI is redefining what "API" means

Traditional APIs assume a **deterministic contract**: same inputs → same outputs, predictable latency, binary correctness.

**AI inference APIs break all three assumptions:**

- **Output:** Same input can produce different outputs (temperature > 0)
- **Latency:** Variable and high (500ms–30 seconds vs. <100ms traditional)
- **Correctness:** Probabilistic, requires evals and monitoring — not unit tests

**New PM decisions this creates:**

- What guarantees do you make to users when your product calls an AI API?
- How do you design UI for non-deterministic response times?
- When model providers change their models, how do you detect product regression?

⚠️ **Warning:** These questions don't have settled answers yet. PMs building AI products are navigating genuinely uncharted territory.

---

### AI API costs: A business model problem, not just a tech problem

**The cost structure:** LLM API calls cost real money: $0.01–$0.15 per 1,000 tokens.

**At scale, this matters:**
- 100,000 users × 10 requests/day = meaningful COGS that didn't exist in traditional software
- Every feature adding an LLM call needs unit economics analysis
- "We'll just add AI everywhere" is a *business model choice*, not a product choice

| **Disciplined approach** | **Undisciplined approach** |
|---|---|
| Carefully select interactions warranting LLM calls | Add AI to every feature |
| Use cheaper deterministic logic where appropriate | Treat all API calls equally |
| Durable competitive advantage through unit economics | Unsustainable COGS at scale |

## Prerequisites

→ None — this is Module 01's entry point



## Next: read alongside (companions)

| Topic | Purpose | When to read |
|-------|---------|--------------|
| **01.02 API Authentication** | How access to an API is controlled | Immediately after this lesson |
| **01.03 Webhooks vs Polling** | Two patterns for getting data from external systems | After authentication fundamentals |

## Read after (deepens this lesson)

| Lesson | Why it matters | Connection |
|--------|----------------|-----------|
| **01.04** Rate Limiting & Throttling | Deep dive on the limits introduced here | Foundation for controlling API load |
| **01.05** Idempotency | Payment retry problem (Stripe example from W4) explained fully | Critical for reliability patterns |
| **03.06** Queues & Message Brokers | Asynchronous pattern referenced in W2 | Scales the request handling introduced here |
| **04.09** AI Agent Patterns | How agents orchestrate APIs | Requires this lesson as prerequisite |