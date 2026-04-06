---
lesson: Webhooks vs Polling
module: 01 — APIs & System Integration
tags: tech
difficulty: foundation
prereqs:
  - 01.01 — What is an API — polling and webhooks are both patterns for calling APIs; read first
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/infrastructure/notifications.md
  - technical-architecture/infrastructure/sse-vs-websockets.md
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
  Foundation → Working → Strategic is the recommended reading order.
-->
```
# ═══════════════════════════════════
# FOUNDATION
# For: non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules
# Assumes: 01.01 What is an API. You know what an API call is.
# ═══════════════════════════════════

## The world before this existed

In 2014, a payments startup integrated with a payment processor to handle checkout. To know whether a payment had succeeded or failed, they built the obvious thing: every five seconds, their server called the processor's status endpoint asking "did this payment complete?"

It worked fine in testing. In production, with 200 active checkouts happening simultaneously, their server was making 2,400 requests per minute just asking "is it done yet?" on payments that typically took under 3 seconds to process. They hit their rate limit within the hour. The processor throttled them. Real payments stopped confirming. Support tickets flooded in.

Meanwhile, a competitor had registered a webhook URL with the same processor. When each payment completed, the processor called that URL with the result — one request, at the exact moment the payment was ready. No polling loop, no rate limit burned, no artificial delay. Zero requests until an event actually happened.

The question "how do we know when something external changes?" has two answers: keep asking, or wait to be told.

## What it is

Polling and webhooks are two patterns for getting data from an external system when something changes.

**Think of it like waiting for a package:**
- **Polling** = checking your doorstep every ten minutes (you do all the work, most checks find nothing, you might miss the pickup window)
- **Webhooks** = the delivery company texting you the moment they drop it off (you do nothing until it matters)

---

| Aspect | Polling | Webhooks |
|--------|---------|----------|
| **How it works** | Your system calls the external API on a fixed schedule | External system calls your server when an event fires |
| **Example** | "Every 30 seconds, check if this order shipped" | "When this order ships, POST to your URL" |
| **Implementation complexity** | Easy to build | More complex to operate |
| **Request efficiency** | Wasteful — most requests return "nothing changed" | No wasted requests |
| **Data freshness** | Delayed by polling interval | Near-real-time delivery |
| **Reliability if you're down** | Self-healing — polling resumes automatically when your server comes back | Dependent — must rely on vendor retry logic if server is down during event |

---

> **The core tradeoff:** Who bears the work and where the reliability burden sits.

## When you'll encounter this as a PM

| **Scenario** | **Key Question** | **Why It Matters** |
|---|---|---|
| **Writing an integration spec** | Webhooks or polling? | Affects rate limits, data freshness, engineering complexity — decide in spec, not sprint review |
| **Defining a real-time requirement** | What's your latency tolerance? | "Immediate" → webhooks required; "within a minute" → polling acceptable. You own this decision |
| **Incident triage** | Missing or delayed events? | Missing = webhook failure; Delayed = polling interval too long. Different root cause, different fix |
| **Evaluating a vendor** | What's their retry policy? | Stripe: 72 hours. Some vendors: zero retries. This determines whether reliability burden falls on your server |
| **Planning for scale** | How many requests will this cost? | 1 request/sec polling = 3.6M requests/hour at 10K users. Webhooks = 1 request per actual event |

---

### Decision Framework: Webhooks vs. Polling

> **Webhooks:** Vendor pushes data to your endpoint when events occur. You receive exactly one request per event. Reliability depends on vendor's retry policy and your endpoint uptime.

> **Polling:** Your servers repeatedly ask "anything new?" on an interval. You control timing but consume API quota constantly, even with no events.

---

### Common Failure Patterns

**Missing events** = Webhook delivery failed (your endpoint was down, vendor stopped retrying)
- Fix: Improve endpoint uptime, verify vendor retry window

**Delayed events** = Polling interval too long
- Fix: Increase polling frequency (costs more quota)

---

### Scale Math Example

- **Polling approach:** 1 request/second × 3,600 seconds = 3,600 requests/hour
- **At 10,000 active users:** 3,600 × 10,000 = **36 million requests/hour** (before any real work)
- **Webhooks approach:** 1 request per actual event only

⚠️ **The scale inflection point:** Above a few hundred concurrent users, webhooks almost always win on cost and reliability. Verify your vendor's retry policy before committing.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs, PMs 2+ years in
# Assumes: Foundation. You know what polling and webhooks are. Now let's build the working model.
# ═══════════════════════════════════

## How it actually works

### Quick comparison: Polling vs. Long Polling vs. Webhooks vs. SSE

| **Method** | **Initiation** | **Overhead** | **Latency** | **Complexity** | **Best for** |
|---|---|---|---|---|---|
| **Polling** | Client pulls repeatedly | High (1,200 req/min per 100 active polls at 5s interval) | High (5–30s delay) | Low | Batch jobs, non-urgent checks |
| **Long Polling** | Client pulls, server holds | Medium | Low (near real-time) | Medium | Real-time updates without persistent connections |
| **Webhooks** | Server pushes event-driven | Low | Very low (immediate) | Medium–High (idempotency + signatures required) | Third-party integrations, event-driven workflows |
| **SSE** | Server pushes persistent stream | Low | Very low (immediate) | Low | Browser-to-server real-time (dashboards, feeds) |

---

### Polling — the full sequence

1. Your server initiates an HTTP GET to the external API: `GET /api/payments/txn_abc123/status`
2. The API authenticates the request and queries its database for the current state.
3. The API returns the current status: `{"status": "pending"}` with a 200.
4. Your server evaluates: if not "complete," wait the polling interval (say, 5 seconds) and repeat.
5. Eventually, the API returns `{"status": "succeeded"}` — your server processes the outcome.

> ⚠️ **Resource drain:** Each iteration is a full round-trip — authentication, database query, HTTP response — even when nothing has changed. For 100 active polls at 5-second intervals, that's **1,200 requests per minute** consuming server resources and rate limit budget continuously.

---

### Long polling — the hybrid

The server holds the request open instead of returning immediately. Your server sends the request; the external API waits until there's new data (up to a configured timeout, typically 30 seconds) before responding. You get near-real-time delivery without the overhead of a persistent connection.

> ⚠️ **Concurrency tradeoff:** Complex to implement and struggles under high concurrency because each open connection consumes a server thread.

---

### Webhooks — the full sequence

1. **Setup (one-time):** Register your endpoint URL with the vendor. `POST /api/webhook/register` with `{"url": "https://yourapp.com/webhooks/payments", "events": ["payment.succeeded", "payment.failed"]}`.
2. Nothing happens until an event fires on the vendor's side.
3. **Event delivery:** The vendor's system POSTs a payload to your registered URL: `{"event": "payment.succeeded", "data": {"payment_id": "txn_abc123", "amount": 4999, "currency": "usd"}}`.
4. **Acknowledge receipt:** Your server must respond with `200 OK` within the vendor's timeout window (typically 5–30 seconds). Response body doesn't matter — just the status code.
5. **Vendor retry policy:** If no `200`: the vendor retries according to their policy — often exponential backoff over hours or days. Stripe retries over 72 hours. GitHub retries for a few hours. Some vendors retry once and stop.

> ⚠️ **Idempotency is required:** Because vendors retry, the same event may arrive twice. Your handler must be idempotent — processing the same event ID twice produces the same outcome as once. **Standard pattern:** Store processed event IDs, check before acting, return `200` if already handled.

> ⚠️ **Signature verification is required:** The vendor signs the payload with a shared secret. Your handler must verify the signature before processing. An unverified webhook is an open endpoint that any attacker can POST fake events to.

---

### Server-Sent Events (SSE) — the persistent push

For product scenarios where you need real-time updates from your own backend to a browser (not third-party), SSE opens a persistent HTTP connection from the browser to your server. The server pushes updates down the stream as events occur.

**Characteristics:**
- Unidirectional (server → client only)
- Simpler than WebSockets
- Built into modern browsers with automatic reconnection
- **Used for:** Live notification feeds, class status updates, real-time dashboards

> ⚠️ **HTTP/1.1 connection limit:** Browsers limit to 6 concurrent SSE connections per domain. **Resolution:** Enable HTTP/2 on the server to remove this constraint.

## The decisions this forces

### When to poll vs webhook — default to webhooks if available

| Scenario | Right choice | Why |
|----------|--------------|-----|
| Vendor offers no webhooks | Polling | Only option available |
| Feature tolerates 30+ seconds of lag | Polling | Acceptable delay for use case |
| Simple one-time status check, no ongoing stream | Polling | No need for continuous updates |
| Freshness matters; vendor supports webhooks | Webhooks | Real-time or near-real-time needed |

**PM action:** If a vendor pitches their integration without mentioning webhooks, ask explicitly. Discovering mid-sprint that polling is the only option changes the estimate, the rate limit budget, and the reliability architecture.

---

### Polling interval vs data freshness vs rate limit budget

These three are in direct tension:

```
Shorter interval → fresher data → more API calls → faster rate limit exhaustion
```

⚠️ **Rate limit math example:**
- Polling interval: 1 second
- Rate limit: 5,000 requests/hour
- Result: Budget exhausted in **83 minutes** — before any real business logic runs

**Before speccing the interval, calculate:**
1. Maximum acceptable lag for this feature?
2. Rate limit math at your expected user volume?

> **Incomplete spec:** "Poll every second" without the rate limit math

---

### Webhook reliability design

Your webhook endpoint will go down. The PM owns these decisions:

| Decision | Impact | Example |
|----------|--------|---------|
| **Server uptime SLA** | Percentage of events missed during outages | 99% uptime = 1% of events lost |
| **Vendor retry policy** | Whether lost events are recoverable | 72-hour retry: loss is temporary. Single retry: need compensating mechanism |
| **Event type criticality** | Reliability architecture varies by event | Payment confirmations = catastrophic if missed. Feed updates = acceptable if missed |

**Different events warrant different reliability designs.** Map each event type to its acceptable failure mode before building.

---

### Idempotency: not optional for webhooks

⚠️ **Why this matters:** Webhooks retry on failure, and network conditions cause double delivery even without explicit failures. Your handler will receive the same event more than once.

**Risk if handler is not idempotent:**
- Processing same event twice = two records
- Processing same event twice = two charges
- Processing same event twice = two emails
- Result: Data integrity bug triggered by normal webhook behavior

**Engineering solution:** Deduplicate on the vendor-provided event ID before acting.

> **PM implication:** "Add webhook support" is not a one-story ticket if the feature involves financial transactions or user-facing state changes. Factor idempotency complexity into sprint estimate.

---

### SSE vs WebSockets for your own real-time features

When building real-time push from your backend to users (not third-party webhooks):

| Technology | One-way? | Complexity | Use case | Tradeoffs |
|------------|----------|-----------|----------|-----------|
| **SSE** | Yes | Simpler | Notifications, feeds, status updates | Uses standard HTTP, automatic reconnection, firewall-friendly |
| **WebSockets** | No (bidirectional) | Complex | Chat, collaborative editing, live classrooms | Lower latency, binary data, custom reconnection logic, may fail behind corporate firewalls |

**Default to SSE** unless the feature explicitly requires the client to push data in real time.

## Questions to ask your engineer

| Question | What this reveals | Red flag | Expected answer |
|----------|-------------------|----------|-----------------|
| **"Does this vendor offer webhooks — and what's their retry policy and maximum retry window?"** | Whether near-real-time is possible and what reliability guarantee exists. A 72-hour retry window means downtime under that window is recoverable. A single retry means your server availability directly determines whether events are lost. | Vendor retries once only | Vendor retries for 24–72 hours |
| **"If our webhook endpoint is down for 20 minutes, what happens to events that fired during that window — do we lose them, or does the vendor queue them?"** | The explicit failure mode and whether you have a reconciliation path. | Vendor sends once; events are lost with no recovery plan | Vendor retries; events are recoverable or you have a manual replay mechanism |
| **"For our polling approach — what interval are we using, how many active sessions hit this at peak, and how much of our rate limit does that consume per hour?"** | Whether rate limit math has been done before sprint start. This calculation must live in the integration spec, not be discovered in production. | Rate limit impact unknown or uncalculated | Math documented and margin buffer included |
| **"Are we validating the webhook signature before processing the payload?"** | Whether your endpoint accepts POST from any source. | No signature validation; attackers can send fake payment confirmations or trigger false events | Yes, we verify the `Stripe-Signature` or equivalent header before processing |
| **"Is our webhook handler idempotent — what happens if we receive the same event ID twice?"** | Whether the team has designed for retry-induced duplicates. | Team hasn't considered duplicate handling | We check event ID against a processed-events store before processing |
| **"For SSE connections — are we on HTTP/2? What happens to a user with 7 browser tabs open?"** | Whether you've hit HTTP/1.1's 6-connection-per-domain limit. HTTP/2 removes this; HTTP/1.1 leaves the 7th tab without updates. | Running HTTP/1.1 with no awareness of the limitation | On HTTP/2, or HTTP/1.1 with documented user-impact acceptance |
| **"What's our mechanism for replaying missed webhook events if our server has an extended outage beyond the vendor's retry window?"** | Whether recovery beyond the happy path exists. For payment flows, missing events need a reconciliation path — a periodic job comparing local records against vendor records and filling gaps. | No replay mechanism; extended outages create irrecoverable data loss | Periodic reconciliation job documented; gap-filling process in place |

⚠️ **Webhook signature validation is a critical security control.** Processing unvalidated webhooks allows attackers to inject fake events (payment confirmations, state changes, etc.). Always verify the vendor-provided signature header before processing payload data.

## Real product examples — named, specific, with numbers

### Stripe — Payment lifecycle at scale

**What:** Sends webhooks for every payment event (`payment_intent.succeeded`, `payment_intent.payment_failed`, `invoice.paid`, `customer.subscription.deleted`). Non-`2xx` responses trigger retries over 72 hours with exponential backoff. Payloads signed with `Stripe-Signature` header (HMAC-SHA256).

**Why:** A decade of learning webhook reliability at payment scale. Dashboard shows full delivery log including retry history and response codes.

**Takeaway:** For high-volume merchants, acknowledge immediately (return `200` before processing) and process asynchronously via queue to prevent timeouts from creating false failures.

⚠️ **Security requirement:** Signature verification is mandatory. Do not process unsigned webhooks.

---

### GitHub — CI/CD trigger efficiency

**What:** Triggers webhooks on repository events: `push`, `pull_request`, `release`, `check_suite`. Payloads signed with `X-Hub-Signature-256` header. Delivery near-real-time (typically <1 second).

**Why:** Every CI/CD tool (GitHub Actions, CircleCI, Jenkins) depends on `push` webhook to trigger builds. Polling alternative: GitHub would need to poll millions of repositories every few seconds—bandwidth and compute cost prohibitive.

**Scale:** Processes 1 billion+ workflow runs per month—only possible with event-driven, not polling-based triggers.

**Takeaway:** Event-driven architecture eliminates the polling tax at platform scale.

---

### Zoom — Recording availability notifications

**What:** `recording.completed` webhook fires when cloud recording finishes processing. Processing delay: 5–20 minutes typical (1-hour call), longer during high-demand periods.

**Why:** Teams polling `GET /meetings/{meetingId}/recordings` every 30 seconds encountered:
- Rate limit quota consumed during entire processing window
- "Recording not ready" responses wasting quota
- Retry logic failures when polling server restarted

Webhook teams: zero requests until ready, then one event with URL.

**Scale impact:** For edtech platforms with 100+ simultaneous classes, rate limit difference between polling and webhooks is the difference between free tier and paid quota.

**Takeaway:** Webhooks preserve quota and eliminate retry complexity.

---

### Slack — From persistent connections to event-driven

**What:** Deprecated Real Time Messaging (RTM) API (persistent WebSocket connections) in favor of Events API (webhooks) in 2016. RTM API fully deprecated as of 2023 for new apps.

**Why:** Millions of installed Slack apps maintaining persistent WebSocket connections consumed enormous server resources. Webhooks—firing only on events—reduced infrastructure load while improving reliability.

**Architectural insight:** Even the platform that owns the server benefits from switching from persistent connections to event-driven webhooks when call volume is low relative to event frequency.

**Takeaway:** Event-driven model scales better than persistent connection model, even for the platform operator.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineers turned PM, senior PMs, heads of product, AI-native PMs
# Assumes: Working Knowledge. Skip here if you've built webhook consumers before.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## What breaks and why

### The idiopotency gap discovered in production

> **Idempotency:** A handler processes the same event multiple times and produces the same outcome as processing it once.

**The problem:** Handlers work correctly in testing (rare retries) but create duplicates in production (frequent retries from network failures).

| Testing scenario | Production reality |
|---|---|
| Event received once → action taken once | Event received twice → duplicate record, charge, or email |
| Retries are rare | Network conditions cause routine double delivery |

**What engineers typically test:**
- Event received, action taken ✓

**What engineers rarely test:**
- Event received twice, action taken once ✗

**PM prevention:** Idempotency is a **required spec item** for any webhook handler touching:
- Financial state
- User account state  
- Outbound communications

Not a nice-to-have. Not "we'll add it if we see duplicates." **Required before launch.**

---

### Polling math done at design time vs discovered at scale

**The failure mode:** Low-volume design doesn't calculate rate limit consumption at projected scale. 10x user growth = 10x polling requests hitting the rate limit ceiling. Migration from polling to webhooks becomes a full re-architecture under production pressure.

**Mandatory calculation for integration spec:**

```
(active sessions at peak) × (polls per second) × 3600 = requests per hour
```

**Decision rule:**
- Compare against vendor rate limit
- If consumption > 50% of limit at projected scale → **webhooks required**
- If vendor has no webhooks → rate limit math determines maximum growth capacity

---

### Webhook event ordering is not guaranteed

> **Event ordering fallacy:** Webhooks arrive in the order events occurred.

**Reality:** Delivery order is NOT guaranteed. A `payment.updated` event can arrive before `payment.created` if the first delivery failed and retried.

**Correct handler design:**
- Must be **state-idempotent** (out-of-order events converge to correct state)
- Use event's own timestamp or sequence number, not arrival order
- Reconstruct state based on event metadata, not delivery sequence

⚠️ **Risk:** Handlers assuming chronological ordering will corrupt state. Most teams don't discover this until they see corrupted records in production.

---

### SSE connection limits are invisible until they matter

> **HTTP/1.1 browser limit:** 6 concurrent connections per domain

**The silent failure:** A user with 7 browser tabs gets no real-time updates on the 7th tab.
- The 7th connection never establishes
- No error message
- No notification
- No UI feedback
- Users discover this from missing notifications, not monitoring

**Scale discovery:** Teams running SSE at HTTP/1.1 often learn about this from user complaints about missing real-time updates.

**PM specification requirement:** Ensure **HTTP/2 enablement** is in the SSE infrastructure spec.
- HTTP/2 removes the per-domain connection limit
- Requires intentional server configuration
- Cannot be retrofitted post-launch without degrading power users

⚠️ **Risk:** Delaying HTTP/2 until after launch means fixing a widespread issue under production pressure.

## How this connects to the bigger system

| Related Lesson | Connection | Key Takeaway |
|---|---|---|
| **Rate Limiting (01.04)** | Webhooks vs polling is a business decision driven by rate limit consumption across concurrent users | Read together for any third-party API integration |
| **API Authentication (01.02)** | Webhooks are inbound calls requiring signature verification; polling is outbound requiring standard auth | Webhook endpoints need verification to prevent unauthenticated access |
| **Queues & Message Brokers (03.06)** | Async event processing via queues enables reliable webhook handling at scale without re-delivery | Cannot design production webhook infrastructure without queue architecture |
| **AI Agent Patterns (04.09)** | AI agents are event-driven systems where webhooks trigger automated actions | Event-driven AI workflows require the same reliability reasoning as webhook handlers |

### Rate Limiting (01.04)
**Why together:** Polling's rate limit consumption compounds across concurrent users. Understanding this mental model is essential for deciding between webhooks and polling as a business trade-off, not just a technical preference.

### API Authentication (01.02)
⚠️ **Security distinction:**
- **Polling:** Outbound requests — your server initiates authenticated calls
- **Webhooks:** Inbound calls — external system calls your server, you must verify legitimacy via signature verification

Without webhook signature verification, your endpoint is an unauthenticated HTTP endpoint.

### Queues & Message Brokers (03.06)
**Production pattern:**
1. Acknowledge webhook immediately (return `200`)
2. Enqueue event for async processing
3. Enables retry without re-delivery from vendor
4. Avoids timeouts at scale

Reliable webhook infrastructure at scale requires queue architecture.

### AI Agent Patterns (04.09)
**Inversion model:** AI agents consuming events are webhooks by another name.

Examples:
- New support ticket created → agent responds
- Payment failed → agent escalates
- User onboarding step completed → agent sends next step

Event-driven AI workflows require the same reliability reasoning as webhook handlers.

## What senior PMs debate

### Polling vs. webhooks migration timeline

| Aspect | Polling First | Webhooks at Design |
|--------|---------------|-------------------|
| **Build speed** | Faster | Slower |
| **Debug complexity** | Easier | More complex |
| **Infrastructure needs** | Minimal on your side | Requires setup |
| **Migration timing** | Under production load | Planned, pre-scale |
| **Cost of migration** | High (pressure + coordination) | Low (planned) |
| **Risk profile** | Known future rework | Risk front-loaded |

> **Key principle:** The choice between polling and webhooks should be explicit, not a default. If you're choosing polling for a use case that will predictably scale past the rate limit ceiling within 12 months, you're choosing a known future migration—own that choice.

**The real debate:** "Faster to build now" vs. "cheaper to migrate before load."

---

### Webhook security controls

⚠️ **Security is under-specced across the industry.** Signature verification, replay attack prevention (event timestamp validation), and rate limiting on webhook endpoints are documented best practices—but adoption is spotty even at well-funded startups.

| Control | Purpose | Required? |
|---------|---------|-----------|
| **Signature verification** | Confirm the sender is legitimate | Yes (always) |
| **Replay attack prevention** | Reject old/duplicate events via timestamp | Depends on stakes |
| **Rate limiting** | Protect your endpoint from overload | Depends on stakes |

> **Attack surface reality:** An attacker needs both your endpoint URL *and* your shared secret to cause damage. Signature verification is the load-bearing control; the rest is defense-in-depth.

**PM call:**
- **Financial or identity events:** Implement all controls
- **Low-stakes notifications:** Signature verification alone may be sufficient
- **Never acceptable:** No verification

---

### AI agents and model-initiated webhooks

A new model is emerging beyond the classic two:

1. **Your system polls** external APIs
2. **External systems push** webhooks to you
3. **AI agents register dynamic webhooks** per task, receive events during execution, then deregister on completion (NEW)

⚠️ **This creates new problems:** The classic webhook model wasn't designed for:
- Dangling endpoints from failed deregistration
- Credential leaks in dynamic URL schemes
- Event ordering across concurrent agent tasks
- Webhook lifecycle management at scale

**Current industry response:** AI agent platforms (LangGraph, OpenAI function calling) abstract webhook management internally.

> **PM decision:** Treat webhook mechanics as a black box until you hit a reliability incident. Then you'll need to understand exactly this level of detail.

## Prerequisites

→ 01.01 What is an API — polling is repeated API calls; webhooks are inbound API calls; read first

## Next: read alongside (companions)

- **01.02 API Authentication** — how webhook signatures verify the caller is genuine
- **01.04 Rate Limiting & Throttling** — polling's rate limit consumption makes this lesson concrete

## Read after (deepens this lesson)

- **03.06 Queues & Message Brokers** — the reliability layer for production webhook processing
- **04.09 AI Agent Patterns** — event-driven AI; agents as webhook consumers