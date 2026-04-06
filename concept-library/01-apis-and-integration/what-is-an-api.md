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

<!--
  LEVEL SELECTOR
  The dashboard renders one level at a time. Switch with the level toggle.
  Each level is self-contained and readable without the others.
  Foundation → Working → Strategic is the recommended reading order.
  Ex-engineers and senior PMs may start at Working or Strategic directly.
-->


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

An API (Application Programming Interface) is a defined contract that lets one piece of software request specific information or actions from another — without needing to know how the other system is built internally.

The most useful analogy: a restaurant menu. The kitchen (the server) has decided exactly what it's willing to make and put it in a fixed list (the menu). You order using a standard format (pointing at the menu, speaking to the waiter). You get exactly what was described. You never need to walk into the kitchen, know the recipes, or care whether the chef changes. The contract — what you can order, what you'll receive — is stable.

In software: the kitchen is the backend system with the data or functionality. The menu is the list of things it's willing to share. You are the client — the app or service making the request. The waiter is the API.

The three API styles you'll encounter as a PM:

**REST** (most common) — uses web URLs and standard request types to get or send data. When your app loads your Twitter feed, it's making a REST call to Twitter's servers asking for your recent posts. When you hit "like", it's making a REST call sending the like action. Nearly every consumer app you've used runs on REST.

**GraphQL** — lets the client ask for exactly the fields it needs, nothing more. If REST is ordering from a full set menu, GraphQL is telling the chef exactly what you want on your plate. Built by Facebook in 2012 to solve mobile data problems.

**gRPC** — a faster, more compact format used for communication between services inside a company's own infrastructure. Less relevant for PM decisions; covered in lesson 03.06.

## When you'll encounter this as a PM

**Writing a PRD for a new feature.** Your feature needs data or functionality that doesn't exist in your product today — a map, a payment processor, a video call. Your engineer will ask "what data do we need from them and what do we send back?" You need to understand what an API contract is to have that conversation meaningfully, not just say "figure it out."

**Sprint planning.** An engineer says "the frontend can't start until the API is built." If you don't understand why the API is the dependency — why the client literally cannot function without knowing what shape the data will arrive in — you'll be tempted to start both in parallel and create rework. The API contract has to exist before anything that consumes it can be built reliably.

**Evaluating a third-party vendor.** Integrating Stripe, Twilio, Zoom, or Salesforce means your engineers will integrate with their API. Before signing the contract, you need to ask: Does their API have good documentation? What's their rate limit — how many requests per second can you make before they throttle you? Do they have webhooks so you get notified when events happen, rather than having to ask repeatedly? These are PM questions. The answers affect your build timeline, your reliability, and your long-term dependency on this vendor.

**An incident happens.** Your on-call engineer says "we're getting 401s from the payment gateway." A 401 is the HTTP status code for "unauthorized — your credentials are invalid or expired." Knowing this tells you: something with authentication broke, not the payment logic. The fix is credential-related, not a code bug. Vocabulary cuts incident triage time in half.

**A stakeholder asks why the feature isn't done.** The feature required integrating with a new vendor API. The vendor's documentation was incomplete and the endpoint behaved differently than documented. This is a real and common cause of delay. If you understand what an API integration involves, you can explain the delay credibly instead of shrugging.

---


# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs, PMs 2+ years in
# Assumes: Foundation. You know what an API is. Now let's build the working model.
# Prereq: read Foundation first, or skip here if you already know the basics.
# ═══════════════════════════════════

## How it actually works

An API call is an HTTP request — the same protocol your browser uses to load a webpage, now used for machine-to-machine communication.

1. **The client forms a request.** It specifies the HTTP method — GET (retrieve data), POST (create or send data), PUT (update), DELETE (remove). It targets a URL called an endpoint: `GET /api/v1/users/42/courses`. It includes parameters (filters, IDs), a request body if sending data (in JSON format), and credentials (an API key or JWT token in the headers).

2. **The request travels to the server.** Over the internet, routed like any other web traffic.

3. **The server's auth middleware runs first.** Before any business logic: is this caller who they say they are? Do they have permission to call this endpoint? If not — 401 (unauthenticated) or 403 (unauthorized) returns immediately. Nothing else happens.

4. **Input validation runs.** Are all required fields present? Are they the right types? A missing required field returns 400 (bad request) with a specific error message.

5. **Business logic executes.** The server queries its database, calls internal or external services, applies business rules, assembles a response.

6. **The response returns.** A JSON object (or XML, or binary — but almost always JSON now) paired with an HTTP status code. 200 = success. 201 = created. 204 = success, no content. 4xx = client error. 5xx = server error. The client reads the status code first, then parses the response body.

7. **The client acts on the response.** Renders data, triggers the next action, handles the error.

This entire round trip — from client request to server response — takes 50–500 milliseconds for most production APIs. Your users experience it as "instant."

**REST in depth.** REST (Representational State Transfer) uses the HTTP method to encode the action and the URL to identify the resource. The same resource can be accessed with different methods: `GET /orders/123` retrieves order 123. `PUT /orders/123` updates it. `DELETE /orders/123` removes it. REST is stateless — each request contains all the information needed, with no session memory on the server. This makes REST easy to scale horizontally (add more servers) and easy to cache (GET responses that don't change frequently can be stored at the network layer).

**GraphQL in depth.** A GraphQL API exposes a single endpoint. Instead of many resource-specific URLs, the client sends a query describing exactly what it needs:

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

The server returns exactly those fields — nothing more. This solves two problems endemic to REST: over-fetching (you get fields you don't use) and under-fetching (one endpoint doesn't have everything you need, so you chain multiple calls). GraphQL's cost: it's significantly more complex to implement server-side, HTTP caching doesn't work out of the box, and poorly written resolvers create N+1 database query problems. It earns its complexity when you have 3+ client types (web, mobile, third-party) with genuinely different data needs.

## The decisions this forces

**REST vs GraphQL.** This is the single most common API architecture debate you'll sit in as a PM. REST is the right default for almost every product. It's simpler to build, easier to cache, more widely understood, and has better tooling. GraphQL becomes worth the complexity when: (1) you have multiple client types with diverging data needs, (2) over-fetching is causing real mobile performance problems (measured, not hypothesized), and (3) your team has GraphQL expertise. If someone proposes GraphQL on a greenfield project without these conditions, push back. The operational complexity — schema management, query complexity limits, caching strategy — is real and ongoing.

**Public API vs internal API.** Public APIs (exposed to developers outside your company) require versioning strategy, rate limiting, backward compatibility guarantees, and documentation as a product. Once you publish an API and developers build on it, you cannot change its shape without breaking their integrations. Internal APIs can move faster — but the habit of "it's internal, we can change it anytime" creates technical debt quickly as internal APIs get consumed by more systems. Push your team to document and version all APIs, not just public-facing ones. "Internal-only" APIs become external-facing faster than anyone expects.

**Synchronous vs asynchronous.** A synchronous API waits — the client sends a request and holds the connection open until the server responds. Works for fast operations (< 2 seconds). For slow operations — generating a PDF, processing a video, running a report — a synchronous API makes users wait and creates timeout failures. The right pattern is asynchronous: the API immediately returns "request received" with a job ID, then the client polls or receives a webhook when the job completes. PM implication: if your feature involves a slow backend operation, spec the async pattern explicitly. Engineers will sometimes default to synchronous even when it creates a bad UX, because it's simpler to implement.

**API versioning from day one.** Every API will change. The question is whether changes break existing callers. Versioning strategy (embed the version in the URL: `/v1/`, `/v2/`) is much easier to establish at the start than to retrofit. When you deprecate an API version, callers need advance notice — 6–12 months minimum for external consumers, 2–4 weeks for internal consumers. PM role: own the deprecation communication plan. Engineering often defaults to "we'll just change it and see who complains."

**Rate limiting.** Every public API needs rate limits — caps on how many requests a caller can make per second/minute/hour. Without limits: a single misbehaving client can saturate your servers. Rate limits also protect your cost structure when your API calls a paid third-party service underneath. As a PM, you need to spec rate limits as a feature, not leave them as an afterthought. The right limits depend on your use cases — a real-time search feature needs much higher limits than a daily report.

## Questions to ask your engineer

1. **"This endpoint has no rate limiting — what happens if a client hammers it with 10,000 requests per minute?"** The answer reveals whether you have denial-of-service risk and whether the team has thought about cost protection for downstream services. Expected answer: "We have rate limiting at the API gateway." Concerning answer: "We'll deal with it if it happens."

2. **"We're supporting both API keys and JWTs on this endpoint — which clients use which, and why do we need both?"** Supporting two auth methods on one endpoint doubles the attack surface and the test matrix. There should be a specific reason. If the answer is "we inherited one and added the other," that's technical debt to log.

3. **"If this endpoint's response shape changes — we add or remove a field — who breaks and how long do we have to migrate them?"** This surfaces your versioning posture. If the answer is "we'd need to coordinate with 12 teams across 3 orgs," you need a versioning strategy before making any changes.

4. **"If our downstream service is slow — say, taking 8 seconds instead of 200ms — what happens to callers of this API?"** Tests whether you have timeouts and fallback behavior. Without a timeout, the slow downstream response holds the API connection open, consuming server threads, eventually cascading into a full outage. Expected: "We have a 3-second timeout and return a graceful error." Concerning: "It would just be slow."

5. **"What's our p99 latency on this endpoint over the last 30 days — and what causes the long tail?"** P99 is the response time for the slowest 1% of requests. If average is 120ms but p99 is 8 seconds, 1 in 100 users is having a terrible experience. The causes are usually specific (a database query that degrades on certain inputs, a network hop to a distant service) and fixable once identified.

6. **"If this endpoint has no auth and a caller can pass any user ID — can they retrieve another user's data?"** Tests for insecure direct object reference (IDOR) — one of the most common API security vulnerabilities. The answer should be "no, we validate that the authenticated user owns the requested resource." If the engineer pauses before answering, escalate.

7. **"What does our API gateway do for us — and what would we have to build ourselves if it disappeared?"** Surfaces hidden dependencies. API gateways typically handle auth, rate limiting, request logging, SSL termination, and routing. If your team has never mapped this, incidents from gateway problems will be confusing and slow to diagnose.

8. **"For the GraphQL endpoint — do we have query complexity limits? What stops a client from sending a query that joins 15 nested objects and brings down the database?"** GraphQL-specific. Without complexity limits, a single malformed or malicious query can execute thousands of database joins. Expected answer: "Yes, we have a max complexity score and it's enforced." Concerning: silence.

## Real product examples — named, specific, with numbers

**Stripe's Payments API: the API as the product.** Stripe was founded in 2010 on the insight that accepting payments online was unreasonably hard — a 6-week integration with each payment processor. Stripe made the API the entire value proposition. Their API design choices are deliberate business decisions: idempotency keys on all payment endpoints (so a retry never double-charges), machine-readable error codes (so your code can handle specific failures programmatically, not just log "payment failed"), and backward compatibility guaranteed indefinitely on v1 endpoints. The result: Stripe processes hundreds of billions of dollars annually, and a developer can integrate payments in an afternoon. API design quality is a direct revenue driver.

**Twitter/X's rate limiting and the 2023 API pricing controversy.** In 2023, Twitter abruptly changed its free API tier from 1,500,000 tweets/month to 1,500 tweets/month — a 1,000x reduction — and introduced paid tiers at $100/month for basic access. Within days, hundreds of third-party apps built on the Twitter API shut down. Academic researchers lost access to data they'd been using for years. The episode illustrated two things: (1) rate limits and pricing are product strategy decisions with enormous ecosystem consequences, and (2) API-dependent businesses have existential concentration risk. Every PM building on a third-party API should answer: "What happens to our product if this API doubles in price or disappears?"

**GitHub's API and the developer ecosystem flywheel.** GitHub exposes nearly every platform capability through a public API — repositories, pull requests, issues, actions, notifications. This was a deliberate product strategy: by making the platform fully API-accessible, GitHub enabled thousands of tools to build on top of it (CI/CD tools, code review assistants, project management integrations). The API became a distribution mechanism. Every tool that integrates with GitHub's API creates lock-in not just for that tool's users, but for GitHub itself. As a PM: your API strategy is your ecosystem strategy.

**Slack's webhook model and the $26B acquisition.** Slack's Incoming Webhooks — a simple API mechanism that lets any service post a message to a Slack channel — became one of the highest-leverage distribution moves in B2B SaaS history. It required almost no engineering investment, but it connected Slack to every other tool in a company's stack: when a payment succeeds, Slack notifies. When a build fails, Slack notifies. When a support ticket is opened, Slack notifies. By 2021, Slack had 2,400 third-party integrations. The API ecosystem — not the messaging UI itself — was core to the $27.7B Salesforce acquisition price.

**Zoom's API fragility as a PM case study.** Zoom's API is well-documented and widely used — edtech platforms, telemedicine companies, and thousands of B2B products depend on it to create meetings, retrieve recordings, and manage participant data. But in 2020–2022, multiple high-profile outages at Zoom cascaded directly into the products built on top of their API. If your product calls Zoom's API to create a class link, and Zoom's API is down, your class doesn't happen — and your users blame you, not Zoom. The lesson: every third-party API dependency is a reliability dependency. PM responsibility: spec fallback behavior before launch. "What do we show the user if Zoom's API returns a 503?" is a product decision, not an engineering one.

---


# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineers turned PM, senior PMs, heads of product, AI-native PMs
# Assumes: Working Knowledge. Skip to here if you've built on APIs before.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## What breaks and why

**The "internal-only" trap.** The most reliably expensive API mistake is building an internal API with the assumption that it will always be internal. Internal APIs accumulate consumers: first one service calls it, then three, then twelve. The original team changes. The API's behavior becomes load-bearing for systems its authors never anticipated. When someone eventually needs to change the API — and they always do — the migration cost is enormous because no one tracked who was consuming it, under what assumptions. The fix is contractual discipline from the start: document all APIs regardless of audience, version them, and treat internal callers as you would external developers. The effort is small. The alternative is months of migration work.

**Rate limit design as an afterthought.** Rate limits are almost always added reactively — after the first incident where a runaway client saturates the service. The correct pattern is to design rate limits as part of the API spec, test them explicitly, and document them clearly. But there's a subtler failure mode: rate limits designed for current traffic that become inadequate as the product scales. A limit of 100 requests/second per client might be generous today and a bottleneck in 18 months. PM role: own the rate limit review as part of growth planning. If you're projecting 10x user growth, what does that do to API call volumes?

**The consistency vs. availability tradeoff manifests at the API layer.** When two services need to stay in sync — a payment is recorded, then a delivery is triggered, then a notification is sent — and any step can fail, you have a distributed systems consistency problem that surfaces directly in your API design. The naive pattern (synchronous chain of API calls) fails silently when the middle step fails: payment succeeds, delivery trigger fails, notification never fires, and the user's order is in a broken state. The correct patterns (idempotent operations, event sourcing, compensating transactions) are architectural decisions that PMs need to understand well enough to ask about in sprint review — not implement, but identify when they're absent.

**Documentation lag kills developer experience.** Every production API has documentation. The documentation is almost never accurate. It reflects the API at some point in the past, before the three edge cases that got fixed, before the new required field that went undocumented, before the rate limit that got tightened. The impact: developers waste hours on failures that better documentation would prevent. For internal APIs, this is a productivity tax on your own engineers. For external APIs, it's a direct conversion rate problem — developers who can't get a quick successful call will move on. PM responsibility: make API documentation a first-class deliverable, not an afterthought, and define a clear owner for keeping it current.

## How this connects to the bigger system

APIs don't exist in isolation — they're the connective tissue of everything else in the curriculum. Understanding APIs is the prerequisite for understanding most of what follows.

**Authentication (01.02)** is how an API knows who is calling it. Every API security decision — API keys, JWTs, OAuth2 scopes — is an API design decision. The authentication lesson builds directly on the mental model established here.

**Webhooks vs Polling (01.03)** is a lesson about two fundamentally different API calling patterns. Polling is the client repeatedly calling an API asking "is it done yet?" Webhooks flip it — the API calls you when something happens. You cannot understand the tradeoff without understanding what an API call costs (latency, rate limit budget, server load).

**Rate Limiting (01.04)** is a surface of API management. The lesson goes deep on strategies and PM decisions; Foundation here establishes why those decisions matter.

**Databases (Module 02)** are almost always what APIs are retrieving from or writing to. API design choices — what fields are included, whether queries are paginated, how filtering works — directly affect database query patterns, index usage, and query performance.

**Monitoring and Alerting (03.09)** — what you monitor in production is largely API metrics: latency percentiles, error rates by status code, request volumes, rate limit hits. The SLA and SLO concepts only make sense against a specific observable: API response time.

**AI Agent Patterns (04.09)** — modern AI agents are API orchestrators. They receive a task, call a sequence of APIs to gather information or take actions, and synthesize a response. Understanding APIs is foundational for understanding how to design, spec, and evaluate agentic AI products.

## What senior PMs debate

**The platform API strategy question.** When should your product expose a public API? The Stripe, GitHub, and Slack examples show API-as-distribution as a deliberate strategy. But most product organizations have the opposite problem: they build for internal use, accumulate technical debt in the API layer, and then face enormous cleanup work when they want to open it up. The unresolved question: at what product maturity should a team invest in API-as-platform? The arguments cluster around "as soon as you have product-market fit" vs. "only when a specific partner demands it." Neither is wrong — they reflect different risk tolerances for the cleanup cost vs. the opportunity cost of waiting.

**GraphQL has been winning for a decade and is still controversial.** GraphQL was released publicly by Facebook in 2015. It's been "the future of APIs" for a decade. But REST is still dominant in new projects. The practical debate now isn't GraphQL vs REST — it's GraphQL vs. well-designed REST with thoughtful resource modeling. Teams that adopted GraphQL at scale (GitHub switched their public API to GraphQL v4 in 2016) report real benefits on client flexibility and reduced over-fetching. Teams that tried to adopt it in less disciplined organizations report schema drift, resolver performance problems, and documentation debt worse than REST ever was. The PM perspective: GraphQL is a team capability investment, not just a technical choice.

**AI is changing what "API" means.** The traditional API assumes a deterministic contract — call this endpoint with these inputs, get this output. AI inference APIs break that assumption: the same input can produce different outputs (temperature > 0), latency is variable and high (500ms to 30 seconds), and "correctness" isn't binary — you need evals, not just unit tests. This creates new PM decisions: what guarantees do you make to users when your product calls an AI API? How do you handle AI API latency in a UI designed for deterministic responses? When Anthropic, OpenAI, or Google change their models, how do you detect regression in your product? These questions don't have settled answers. PMs building AI products are navigating genuinely uncharted API design territory.

**The cost structure of modern APIs is a business model problem.** Calling an LLM API costs real money per call — $0.01 to $0.15 per 1,000 tokens is a reasonable range today. At 100,000 users making 10 requests per day, that's a meaningful COGS line that didn't exist in traditional software. This changes the PM's relationship with API calls: every feature that adds an LLM API call needs a unit economics analysis. "We'll just add AI everywhere" is a business model choice, not just a product choice. The companies that get this right (carefully selecting which interactions warrant LLM API calls vs. cheaper deterministic logic) will have durable competitive advantage over those that don't.

---

## Prerequisites

→ None — this is Module 01's entry point

## Next: read alongside (companions)
→ 01.02 API Authentication — how access to an API is controlled; read immediately after this
→ 01.03 Webhooks vs Polling — two patterns for getting data from external systems

## Read after (deepens this lesson)
→ 01.04 Rate Limiting & Throttling — goes deep on the limits introduced here
→ 01.05 Idempotency — the payment retry problem, introduced in W4 (Stripe example), explained fully
→ 03.06 Queues & Message Brokers — the asynchronous pattern referenced in W2
→ 04.09 AI Agent Patterns — how agents orchestrate APIs; requires this lesson as foundation