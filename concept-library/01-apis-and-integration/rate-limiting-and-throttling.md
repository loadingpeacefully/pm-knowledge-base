---
lesson: Rate Limiting & Throttling
module: 01 — APIs & System Integration
tags: tech
difficulty: foundation
prereqs:
  - 01.01 — What is an API — rate limits protect APIs; read first
  - 01.03 — Webhooks vs Polling — polling burns rate limits fastest; read before this
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-student-get.md
  - technical-architecture/crm-and-sales/sales-flow.md
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
  Foundation → Working → Strategic is the recommended reading order.
-->


# ═══════════════════════════════════
# FOUNDATION
# For: non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules
# Assumes: 01.01 What is an API. You know what an API call is.
# ═══════════════════════════════════

## The world before this existed

In the early days of Twitter's API, there were no rate limits. Any developer could call the API as many times as they wanted. A single misbehaving script — an infinite loop, a buggy retry mechanism, a developer stress-testing their app — could make millions of requests per hour. On a day when a celebrity tweeted something viral, the API would saturate. Legitimate apps would get slow responses or errors. Other developers, playing by the rules, suffered because one caller wasn't.

Twitter eventually added rate limits. Their API still gets abused — but now a single bad actor hits their personal ceiling, not Twitter's infrastructure ceiling. Everyone else keeps working.

Every popular API you've used — Stripe, GitHub, Google Maps, OpenAI — has rate limits. The ceiling is almost always lower than engineers assume, and the consequences of hitting it range from delayed data to a service outage.

## What it is

Rate limiting caps how many requests a caller can make to an API within a time window. Throttling is the softer version: instead of rejecting requests that exceed the limit, the API slows responses down to a manageable pace. Both protect shared infrastructure from being consumed by any single caller.

Think of a highway on-ramp metering light. When traffic is heavy, cars entering the highway are paced — one every few seconds. You're not being blocked from the highway. You're being slowed to a rate the highway can absorb without gridlock. The highway still works. Everyone moves.

Three limit mechanisms a PM will encounter:

**Fixed window** — 1,000 requests per hour, resetting at the top of each hour. Simple and predictable. Exploitable: if you can batch all your requests in the last minute of the window, you burn through the limit before the reset, then wait 59 minutes. Systems that have bursting traffic patterns (a cron job that fires at :00) can hit fixed window limits in seconds.

**Sliding window** — 1,000 requests in any rolling 60-minute period. Smoother than fixed window. Harder to game. More common in production APIs that serve high-traffic use cases.

**Token bucket** — requests consume tokens from a bucket that refills at a fixed rate. Burst traffic is allowed as long as there are tokens in the bucket. A batch of 50 requests in 2 seconds is fine if the bucket has 50 tokens. Then the bucket refills at, say, 10 tokens per minute. Stripe and GitHub use token bucket variants because they match the natural call patterns of developers: occasional bursts followed by quiet periods.

## When you'll encounter this as a PM

**Integrating with a third-party API.** Every external API has limits. Before committing to a third-party integration in a PRD, confirm the vendor's rate limit and calculate whether your projected call volume fits within it. The PM owns this check — discovering a rate limit problem after engineering has built the integration is a spec failure.

**Incident triage.** Your on-call engineer reports a wave of `429 Too Many Requests` errors. This means a caller is over their limit. The usual cause: a polling loop, a cron job, or a batch operation that isn't paced. The fix is always the same structure — slow down, queue requests, and add backoff (waiting progressively longer between retries). Retrying immediately on a `429` makes the problem worse.

**Scaling decisions.** An integration that runs fine at 100 concurrent users may hit limits at 10,000. If one user session triggers four API calls, 10,000 users is 40,000 calls — and each of those calls might hit a separate downstream service with its own limit. Rate limits are a scaling ceiling that needs to be calculated before committing to an architecture.

**Pricing negotiations.** Higher rate limits are often what enterprise tiers are actually selling. A SaaS vendor's pricing page that says "Enterprise: custom limits" usually means you're paying for more API quota. Understanding what your rate limit budget is across vendors affects your COGS at scale.

---


# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs, PMs 2+ years in
# Assumes: Foundation. You know the three limit mechanisms. Now let's build the working model.
# ═══════════════════════════════════

## How it actually works

**The request lifecycle with rate limiting:**

1. **The client sends a request.** API key, JWT, or IP address identifies the caller. Rate limits are almost always scoped to caller identity, not to the API as a whole — your misbehaving client doesn't affect another customer's quota.

2. **The API gateway checks the caller's quota.** It retrieves the caller's current usage count from a fast data store (Redis is common — low-latency, in-memory). This check happens before any business logic runs.

3. **Under the limit: request proceeds.** Counter increments. The response includes rate limit headers on every response — not just when you're close to the limit: `X-RateLimit-Limit: 1000`, `X-RateLimit-Remaining: 742`, `X-RateLimit-Reset: 1714000800`. Well-designed clients read these headers on every response to self-regulate before hitting the ceiling.

4. **Over the limit: `429 Too Many Requests` is returned immediately.** No business logic runs. No database query executes. The response includes `Retry-After: 30` (wait 30 seconds) or the equivalent reset header. The client must obey the `Retry-After` and implement exponential backoff — waiting progressively longer between retries: 1s, 2s, 4s, 8s, 16s... Retrying immediately on a `429` burns the little remaining quota and extends the lockout period.

5. **Limits are often layered.** A vendor may have: 100 requests/minute, 5,000 requests/hour, and 50,000 requests/day. A single burst can hit the per-minute limit while being well under the hourly limit. Any one limit returning `429` blocks the request regardless of the others. This layering is why "we're within our daily quota" doesn't prevent `429` errors.

6. **Throttling differs from hard limits.** Some APIs throttle instead of rejecting — the response comes back, just slowly: a 200ms endpoint becomes 2 seconds. No `429`. Your application feels slow rather than errored. From a PM perspective, throttling is harder to detect because it doesn't show up as an error rate — it shows up as a latency spike.

**Token bucket mechanics — why bursts are allowed:**
The bucket starts full (say, 100 tokens). Each request consumes 1 token. The bucket refills at 10 tokens/second. If your app makes 80 requests in 0.1 seconds, 80 tokens are consumed immediately — the burst is permitted. The bucket then has 20 tokens and refills over the next 8 seconds. This matches the natural pattern of production traffic: occasional spikes followed by quiet. Token bucket is more lenient than fixed window for legitimate burst use cases while still preventing sustained overconsumption.

## The decisions this forces

**Queue vs inline processing for high-volume external calls.** If your feature needs to make 500 API calls to an external service per user event, making them inline in the request path will either hit rate limits or introduce multi-second latency for users. The correct architecture: enqueue the work, process it from a worker at the vendor's allowed rate using backoff on `429`. The PM decision: how much delay is acceptable? A CRM sync can queue for 10 minutes. A payment confirmation cannot. "We'll use a queue" without specifying the acceptable latency is an incomplete spec.

**Polling interval vs rate limit budget.** Polling burns rate limits faster than any other pattern. A 5-second polling interval for 1,000 active sessions = 720,000 requests per hour. If the vendor's limit is 1,000,000 requests per day, polling alone at this volume would exhaust the daily limit in 84 minutes. Calculate this before committing to a polling-based design: (polling interval in seconds) × (concurrent pollers) × 3600 = requests per hour. If that number is within 50% of the limit, design for webhooks instead.

**Setting rate limits on your own API.** Every API you expose needs limits. Too low: legitimate use cases break, partners get blocked, your own mobile app hits errors during traffic spikes. Too high: a single runaway client can saturate your database. The right baseline: 2–3× expected peak per tier, tuned from production `429` logs over the first 90 days. Differentiate limits between internal callers (your own services), partners (authenticated external), and anonymous public. Internal callers typically get 10× the limit of external callers — they're trusted and their traffic patterns are known.

**Burst vs sustained throughput — match to call pattern.** Token bucket tolerates burst traffic (50 calls in 2 seconds, then nothing for 5 minutes) — right for event-driven integrations. Fixed window is simpler for steady batch jobs that run at predictable times. Sliding window is most accurate for sustained high-volume traffic. Choose by observing actual call patterns, not by which algorithm is simplest to explain. If you can't describe your app's API call pattern to your engineer, you can't spec the right limit algorithm.

**Enterprise tier uplift as a product decision.** When a partner tells you they need higher rate limits, this is not an engineering capacity question — it's a pricing decision. Higher limits consume more resources on your infrastructure. The unit economics of "what does it cost to serve this partner at 10× the standard limit?" should inform whether enterprise tier pricing covers the infrastructure cost. PMs who treat rate limit uplift as a free favor are giving away margin.

## Questions to ask your engineer

1. **"What limits does this vendor enforce per key, per minute, and per day — and have we done the math at 10× our current user volume?"** Rate limit problems are predictable with arithmetic. If the team can't answer this, the integration spec is incomplete.

2. **"When our client gets a `429`, does it read `Retry-After` and queue — or does it retry immediately?"** Immediate retry on `429` is the single most common cause of rate limit self-perpetuation. One bad client turns a brief limit hit into an extended lockout. Expected: we read `Retry-After` and implement exponential backoff. Concerning: we retry immediately.

3. **"For high-volume external calls, are we processing inline in the request path or using a rate-controlled queue?"** Inline processing means your users experience the rate limit wait as latency. A queue absorbs the limit into processing delay that happens in the background. The right answer depends on whether the operation is synchronous (user is waiting) or asynchronous (background job).

4. **"If we hit the vendor's rate limit during a traffic spike — which flows fail, and do they fail silently or with an alert?"** Silent failures are the dangerous category. A payment confirmation that fails silently because of a `429` looks like a successful transaction to the user but nothing to the backend. Expected: `429`s are monitored, alerted when they exceed a threshold, and critical flows have explicit error handling.

5. **"For our own APIs — what limits are spec'd per tier, and do internal callers get the same ceiling as third-party partners?"** Internal services calling your own APIs should have separate, higher limits — they're trusted, their patterns are known, and throttling your own mobile app because it's hitting your own API limits is a self-inflicted incident. If internal and external share the same bucket, fix it.

6. **"Do we alert when `429` responses exceed 1% of calls on any external integration?"** A 1% `429` rate means 1 in 100 requests is failing. Over 10,000 requests/hour, that's 100 silent failures per hour. The alert threshold depends on the integration's sensitivity — payment flows warrant 0.1%, notification flows can tolerate 1%. Having no alert is the wrong answer.

7. **"What's our token bucket capacity at peak — can we absorb the traffic spike from our largest marketing campaign without throttling?"** Capacity planning for rate limits is the same as capacity planning for infrastructure. If a campaign sends a surge of users to your signup flow simultaneously, and each signup triggers 5 API calls to external services, 10,000 signups = 50,000 API calls in a narrow window. Does the bucket hold that?

## Real product examples — named, specific, with numbers

**Stripe: rate limits as an explicit product feature.** Stripe enforces 100 requests/second in live mode per account, with token bucket burst headroom for short spikes. Rate limit headers appear on every response — not just `429`s — so well-behaved clients can self-regulate before hitting the limit. Stripe's documentation explicitly instructs developers to use idempotency keys with queued retries, never tight polling loops. The design reflects Stripe's risk: a payment that retries rapidly on `429` without idempotency could double-charge. Rate limit discipline is part of Stripe's correctness guarantee, not just their scalability story.

**Twitter/X: rate limit pricing as business model.** In early 2023, Twitter reduced its free API tier from 1,500,000 tweets/month to 1,500 tweets/month — a 1,000× reduction — and introduced paid tiers starting at $100/month for 10,000 tweets/month. Within weeks, hundreds of third-party apps and academic research projects lost their ability to function. The episode illustrates two things: (1) rate limits and rate limit pricing are business model decisions with ecosystem-level consequences, and (2) every product built on a third-party API with meaningful rate limits has concentration risk. The PM question for every such dependency: "What happens to our product if this vendor 100× their rate limit pricing tomorrow?"

**GitHub REST API: 5,000 requests/hour.** GitHub enforces 5,000 requests/hour per authenticated user, 60/hour unauthenticated. CI/CD pipelines that poll GitHub's API for build status — rather than using webhooks — exhaust this in minutes at high velocity. GitHub's GraphQL API is the architectural answer: a single well-formed query replaces 10–20 REST calls. For PMs: when a vendor offers a GraphQL API alongside a REST API, the rate limit math often forces GraphQL adoption at scale, even if the team would prefer the simplicity of REST.

**OpenAI: tokens per minute as the new rate limit unit.** OpenAI enforces rate limits in two dimensions simultaneously: requests per minute (RPM) and tokens per minute (TPM). A single large request can hit the TPM limit while being well under the RPM limit. At GPT-4 prices (roughly $0.03 per 1,000 prompt tokens, $0.06 per 1,000 completion tokens as of early 2024), hitting TPM limits on a production feature means both a service disruption and a cost spike. AI API rate limits introduce a cost dimension that traditional REST API rate limits don't have — the PM implication is that rate limit headroom and unit economics are the same conversation.

---


# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineers turned PM, senior PMs, heads of product, AI-native PMs
# Assumes: Working Knowledge. Skip here if you've managed API rate limit incidents before.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## What breaks and why

**The rate limit that works in staging and fails in production.** Staging environments typically have one or two test users. Production has thousands of concurrent users, each generating API calls simultaneously. A rate limit that gives 100 requests/minute per user is invisible in staging — one user never hits it. In production, 100 concurrent users all starting a session simultaneously = 100 simultaneous rate limit counters, each racing toward their individual ceiling. Per-user limits don't aggregate into a global problem. Global limits do. The failure mode: a feature that calls a shared external service with a global account-level limit (not per-user) will hit that limit when concurrent users multiply call volume. The PM prevention role: distinguish between per-key, per-user, and per-account limits when reviewing vendor documentation. Ask explicitly.

**The retry storm.** A service hits `429`. Its retry logic fires immediately, consuming what little remaining quota exists. The quota resets. The service fires again, immediately. The quota is consumed in seconds. The retry logic fires again. This cycle — rate limit → immediate retry → deeper rate limit → immediate retry — can persist for hours, making a momentary rate limit spike into an extended outage. The fix is exponential backoff with jitter (randomized wait times prevent synchronized retries from multiple instances creating another storm). The PM implication: any feature that calls an external API with volume needs an explicit spec for what the retry behavior looks like. "Retry on failure" without backoff is a ticking storm.

**Limits that become ceilings for product growth.** A rate limit that was generous at Series A becomes a growth constraint at Series B. The product team wants to add a new feature that triples API call volume. The vendor's limit doesn't triple — or it triples only on a tier that costs 5× more. The limit that was an invisible background assumption becomes the constraint that shapes the roadmap. Rate limit headroom should be in growth planning the same way database capacity and server compute are. If the team doesn't know what percentage of their vendor rate limit budget is being used at current volume, they can't plan for 3× growth without a potential surprise.

**LLM API rate limits are structurally different.** Traditional API rate limits are set by the service provider based on infrastructure cost. LLM API limits are set by a combination of infrastructure cost and safety constraints — and they change with model updates. A rate limit change from OpenAI or Anthropic can happen between versions of the same model. Products that built tight coupling to specific model versions and assumed stable limits have faced disruptions when model updates changed the latency or token throughput profile. The correct design: build rate limit headroom as a buffer, not an assumption, and treat LLM API limits as variable rather than fixed.

## How this connects to the bigger system

**Webhooks vs Polling (01.03)** establishes why rate limits are the forcing function for architecture decisions. Polling's rate limit consumption is the quantitative argument for webhooks at scale. You cannot make the argument rigorously without the rate limiting lesson's math.

**Queues & Message Brokers (03.06)** are the architectural solution when rate limits make inline processing impossible. A queue absorbs traffic spikes and feeds requests to external APIs at the permitted rate. Understanding rate limiting is what makes queue design meaningful rather than abstract — you're designing the queue throughput to match the rate limit ceiling.

**Databases (02.xx)** surface the rate limit concept internally: database connection pools are rate limits for database access, enforced by connection count rather than requests per second. The same reasoning — queue vs inline, burst capacity, retry behavior — applies to both external API rate limits and internal database connection limits.

**AI Agent Patterns (04.09)** creates compounding rate limit problems. An AI agent that calls multiple tools in sequence may hit rate limits across three external APIs simultaneously — each with different limit algorithms, different retry policies, and different costs per request. Designing AI agents that are rate-limit-aware requires understanding all three limit mechanisms and how to orchestrate calls to stay within limits across multiple services concurrently.

## What senior PMs debate

**Per-user limits vs global limits — who bears the cost of one bad actor?** Per-user limits (each API key gets its own bucket) mean a misbehaving client affects only themselves. Global account limits (all API keys share one bucket) mean one misbehaving client can degrade service for everyone. Most B2B APIs use per-key limits. Most enterprise SaaS products that expose APIs to their own customers use a combination — per-user limits plus a global ceiling. The unresolved tension: per-user limits require more complex tracking infrastructure (one counter per user vs one global counter), but global limits create unfair outcomes. The answer is almost always "per-user with a global ceiling" — the debate is where to set each and who gets premium limits.

**Rate limits as revenue protection vs rate limits as infrastructure protection.** The traditional framing is: rate limits protect servers from overload. The modern framing (especially for AI APIs) is: rate limits protect unit economics. An LLM API call costs real money per token — OpenAI, Anthropic, and Google all price by token volume. A product that makes unlimited LLM calls per user request has no floor on COGS per user. Rate limits for AI features are often product-level monetization decisions disguised as technical constraints. The PM implication: when an AI product announces rate limits on their "generous free tier," read it as a unit economics decision, not an infrastructure decision. The limit is where the margin is.

**Rate limit transparency is a competitive moat.** Stripe's rate limit headers on every response — not just on `429`s — allow developers to self-regulate and build better products. Opaque rate limits that only show up as `429` failures create frustration, bad integrations, and support burden. The debate: does being transparent about your rate limit headroom help competitors understand your capacity? The evidence from the market: transparency (Stripe, GitHub, Twilio) correlates with better developer experience and higher adoption. Opacity (older enterprise APIs) correlates with integration frustration and workarounds. For API products, rate limit transparency is table stakes for developer trust.

---

## Prerequisites

→ 01.01 What is an API — rate limits protect APIs; understand the API model first
→ 01.03 Webhooks vs Polling — polling burns rate limits fastest; the relationship is direct

## Next: read alongside (companions)
→ 01.05 Idempotency — safe retries on `429` require idempotency keys to prevent duplicate actions

## Read after (deepens this lesson)
→ 03.06 Queues & Message Brokers — the architecture for processing within rate limit constraints
→ 04.09 AI Agent Patterns — compounding rate limits across multi-tool agent calls
