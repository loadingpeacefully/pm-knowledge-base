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

# ═══════════════════════════════════
# FOUNDATION
# ═══════════════════════════════════

**For:** Non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules

**Assumes:** 01.01 What is an API. You know what an API call is.
```

## The world before this existed

In 2014, a payments startup integrated with a payment processor to handle checkout. To know whether a payment had succeeded or failed, they built the obvious thing: every five seconds, their server called the processor's status endpoint asking "did this payment complete?"

It worked fine in testing. In production, with 200 active checkouts happening simultaneously, their server was making 2,400 requests per minute just asking "is it done yet?" on payments that typically took under 3 seconds to process. They hit their rate limit within the hour. The processor throttled them. Real payments stopped confirming. Support tickets flooded in.

Meanwhile, a competitor had registered a webhook URL with the same processor. When each payment completed, the processor called that URL with the result — one request, at the exact moment the payment was ready. No polling loop, no rate limit burned, no artificial delay. Zero requests until an event actually happened.

The question "how do we know when something external changes?" has two answers: keep asking, or wait to be told.



## What it is

Polling and webhooks are two patterns for getting data from an external system when something changes.

**The analogy:** Polling is checking your doorstep every ten minutes — you're doing all the work, most checks find nothing, and you might still miss a narrow pickup window. Webhooks are the delivery company texting you the moment they drop it off. You do nothing until the moment it matters.

### Polling vs. Webhooks

| **Polling** | **Webhooks** |
|---|---|
| Your system calls the external API on a fixed schedule | External system calls your server when an event fires |
| **Example:** "Every 30 seconds, check if this order shipped" | **Example:** "When this order ships, POST to your URL" |
| Easy to build | More complex to operate |
| Self-healing — resumes automatically if your server restarts | Relies on vendor retries if your server is down during an event |
| Wasteful — most requests return "nothing changed" | No wasted requests |
| | Near-real-time delivery |

> **Polling:** Your system calls the external API on a fixed schedule to check for changes.

> **Webhooks:** The external system calls your server when an event fires, eliminating the need for constant polling.

### The core tradeoff

Both solve the same problem: knowing when something external changes. The difference is **who bears the work and where the reliability burden sits.**

- Polling shifts work to your system (constant checks)
- Webhooks shift work to the vendor (retry logic and event delivery)

## When you'll encounter this as a PM

| Scenario | Your decision | Why it matters |
|----------|---------------|----------------|
| **Writing an integration spec** | Push/pull question into spec before sprint planning | Affects rate limits, data freshness, and engineering complexity—not a sprint-time discovery |
| **Defining a real-time requirement** | Specify your latency tolerance explicitly | "Immediately" = webhooks required; "within a minute" = polling acceptable. You own this trade-off |
| **Incident triage** | Map failure pattern to root cause | Missing events → webhook failure. Delayed events → polling interval too long. Cuts triage time 50% |
| **Evaluating a vendor** | Assess webhook availability + retry policy | 1 retry = your server uptime is the weak link. 72-hour retry = vendor carries reliability load. Selection criterion, not detail |
| **Planning for scale** | Calculate requests at target user count | 1 req/sec per user = 3.6M reqs/hour at 10K users. Webhooks = 1 req per actual event. Math favors webhooks above ~200 users |

---

### Writing an integration spec
The first decision is structural: do they offer webhooks, or do your engineers poll? This belongs in your spec, not discovered in sprint review. The answer cascades into your rate limit budget, your data freshness SLA, and how much engineering complexity you're absorbing.

### Defining a real-time requirement
> **Real-time tolerance:** Your acceptable latency between event occurrence and your system's awareness of it.

**Instant confirmation** requires webhooks — polling introduces 0 to N seconds of lag (where N = polling interval). **"Within a minute is fine"** can tolerate polling. You own this tolerance decision. If you spec a feature requiring instant confirmation but don't specify webhooks, engineers will build polling and mark it done.

### Incident triage
Two failure patterns separate cleanly:
- **Missing events** → webhook failure (your endpoint was down, vendor stopped retrying)
- **Delayed events** → polling interval too long

Different root cause, different fix. Knowing which you have cuts triage time in half.

### Evaluating a vendor
⚠️ **Webhook retry policy is a reliability decision, not an engineering detail.**

Check whether they offer webhooks *and* what their retry policy is. A vendor making one webhook attempt and stopping puts the entire reliability burden on your server's uptime. Compare:

- **Stripe:** 72-hour retry window
- **Some vendors:** No retry at all

This is a vendor selection criterion.

### Planning for scale
**Polling math at scale:**
- 1 request/second per user
- At 10,000 active users = 36 million requests/hour
- Before any real work happens

**Webhooks:**
- 1 request per actual event
- Flat cost regardless of user count

The scale economics almost always favor webhooks above a few hundred concurrent users.

## How it actually works

| **Method** | **How it works** | **Latency** | **Server cost** | **Best for** |
|---|---|---|---|---|
| **Polling** | Repeatedly request status at fixed intervals | High (delay = interval) | High (continuous requests even when no change) | Non-urgent updates, simple integration |
| **Long polling** | Server holds request open until new data arrives (up to timeout) | Low (near-real-time) | Medium (fewer requests, but connection threads consume resources) | Near-real-time without persistent connections |
| **Webhooks** | Vendor pushes event to your endpoint when state changes | Very low (push on occurrence) | Low (request only on event) | Real-time, event-driven workflows |
| **Server-Sent Events (SSE)** | Persistent connection from browser to your server; server pushes updates | Very low (push as it happens) | Medium (persistent connections) | Browser-to-backend real-time (live feeds, dashboards) |

---

### Polling — the full sequence

> **Polling:** Your server repeatedly requests the same status endpoint at fixed intervals, checking whether the state has changed.

1. Your server initiates an HTTP GET to the external API: `GET /api/payments/txn_abc123/status`
2. The API authenticates the request and queries its database for the current state.
3. The API returns the current status: `{"status": "pending"}` with a 200.
4. Your server evaluates: if not "complete," wait the polling interval (say, 5 seconds) and repeat.
5. Eventually, the API returns `{"status": "succeeded"}` — your server processes the outcome.

⚠️ **Cost trap:** Each iteration is a full round-trip — authentication, database query, HTTP response — even when nothing has changed. For 100 active polls at 5-second intervals, that's **1,200 requests per minute** consuming server resources and rate limit budget continuously.

---

### Long polling — the hybrid

> **Long polling:** The server holds the request open instead of returning immediately, waiting until new data is available (up to a configured timeout) before responding.

Your server sends the request; the external API waits until there's new data (up to a configured timeout, typically 30 seconds) before responding. You get near-real-time delivery without the overhead of a persistent connection.

⚠️ **Implementation burden:** Complex to build and struggles under high concurrency because each open connection consumes a server thread.

---

### Webhooks — the full sequence

> **Webhook:** The vendor registers your endpoint URL and pushes event payloads to it when state changes occur, rather than your server polling for updates.

1. Setup (one-time): you register your endpoint URL with the vendor. `POST /api/webhook/register` with `{"url": "https://yourapp.com/webhooks/payments", "events": ["payment.succeeded", "payment.failed"]}`.
2. Nothing happens until an event fires on the vendor's side.
3. When the event occurs, the vendor's system POSTs a payload to your registered URL: `{"event": "payment.succeeded", "data": {"payment_id": "txn_abc123", "amount": 4999, "currency": "usd"}}`.
4. Your server must respond with `200 OK` within the vendor's timeout window (typically 5–30 seconds). Response body doesn't matter — just the status code.
5. If no `200`: the vendor retries according to their policy — often exponential backoff over hours or days. Stripe retries over 72 hours. GitHub retries for a few hours. Some vendors retry once and stop.

#### Critical: Idempotency

⚠️ **Idempotency is required:** because vendors retry, the same event may arrive twice. Your handler must be idempotent — processing the same event ID twice produces the same outcome as once.

**Implementation pattern:**
- Store processed event IDs in a database
- Check the event ID before processing
- Return `200` if already handled

#### Critical: Signature verification

⚠️ **Signature verification is required:** the vendor signs the payload with a shared secret. Your handler must verify the signature before processing. An unverified webhook is an open endpoint that any attacker can POST fake events to.

---

### Server-Sent Events (SSE) — the persistent push

> **Server-Sent Events (SSE):** A persistent HTTP connection from browser to your server, where the server pushes updates down the stream as events occur. Unidirectional (server → client only).

Simpler than WebSockets, built into modern browsers with automatic reconnection.

**Common use cases:**
- Live notification feeds
- Class status updates
- Real-time dashboards

⚠️ **HTTP/1.1 connection limit:** Browsers limit to 6 concurrent SSE connections per domain. **Resolution:** enable HTTP/2 on your server to bypass this constraint.

## The decisions this forces

### Polling vs webhooks

> **Webhooks:** Server-to-server push notifications triggered by events. Vendor initiates the connection.

> **Polling:** Client repeatedly asks "any updates?" on a fixed interval. You initiate the connection.

**Default to webhooks if available.**

Polling is the right choice when:
- Vendor offers no webhooks
- Feature tolerates 30+ seconds of lag
- You need a simple one-time status check with no ongoing stream

Webhooks are the right choice for everything else where freshness matters.

**⚠️ PM action:** If a vendor pitches their integration without mentioning webhooks, ask explicitly. Discovering mid-sprint that polling is the only option changes the estimate, rate limit budget, and reliability architecture.

---

### Polling interval vs data freshness vs rate limit budget

| Factor | Trade-off | Impact |
|--------|-----------|--------|
| **Shorter interval** | More frequent checks | Fresher data |
| **Shorter interval** | More API calls | Faster rate limit exhaustion |
| **Longer interval** | Fewer API calls | Higher acceptable lag |

**Rate limit math example:**
- 1-second polling interval
- 5,000-request/hour limit
- **Result:** Budget exhausted in 83 minutes (before any business logic runs)

**Before speccing the interval, calculate:**
1. Maximum acceptable lag for this feature?
2. Rate limit math at your expected user volume?

⚠️ **Incomplete spec alert:** "Poll every second" without rate limit math is not ready for sprint.

---

### Webhook reliability design

Your webhook endpoint **will** go down. Decisions the PM owns:

| Decision | Impact | Example |
|----------|--------|---------|
| **Server uptime SLA** | Determines acceptable event loss | 99% uptime = 1% of events missed during outages |
| **Vendor retry window** | Recovery window if you're offline | 72-hour retry = 10-min recovery is fine. Single retry = you need a compensating mechanism. |
| **Event type criticality** | Which failures are acceptable vs catastrophic | Payment confirmations: catastrophic. Feed notifications: acceptable. |

Different event types warrant different reliability designs.

---

### Idempotency: not optional for webhooks

⚠️ **Webhooks retry on failure. Network conditions cause double delivery even without explicit failures.**

**Risk:** If your handler isn't idempotent, processing the same event twice creates:
- Two records
- Two charges
- Two emails
- Data integrity bugs triggered by normal webhook behavior

**Engineering solution:** Deduplicate on vendor-provided event ID before acting.

**PM impact:** "Add webhook support" is not a one-story ticket if the feature involves financial transactions or user-facing state changes. Factor idempotency complexity into sprint estimates.

---

### SSE vs WebSockets for your own real-time features

When building real-time push from your backend to users (not third-party webhooks):

| Choice | One-way or bidirectional? | Use cases | Complexity | Latency |
|--------|---------------------------|-----------|-----------|---------|
| **SSE** | One-way server → client | Notifications, feeds, status updates | Significantly simpler. Standard HTTP, automatic reconnection, firewall-friendly. | Higher |
| **WebSockets** | Bidirectional | Chat, collaborative editing, live classrooms | Custom reconnection logic required. May fail behind corporate firewalls. | Lower. Supports binary data. |

**Default to SSE** unless the feature explicitly requires the client to push data in real time.

## Questions to ask your engineer

| Question | What this reveals | Red flag |
|----------|-------------------|----------|
| **"Does this vendor offer webhooks — and what's their retry policy and maximum retry window?"** | Whether near-real-time is possible and what the reliability guarantee is. A 72-hour retry window means downtime under that period is recoverable. A single retry means your server availability directly determines whether events are lost. | Vendor retries once; events are lost if your server is down. |
| **"If our webhook endpoint is down for 20 minutes, what happens to events that fired during that window — do we lose them, or does the vendor queue them?"** | The explicit failure mode and whether events can be recovered or are permanently lost. | Vendor sends once and discards; no recovery path exists. |
| **"For our polling approach — what interval are we using, how many active sessions hit this at peak, and how much of our rate limit does that consume per hour?"** | Forces rate limit math *before* sprint start, not during production troubleshooting. This calculation must be documented in the integration spec. | Team hasn't done rate limit math; discovers the constraint in production under load. |
| **"Are we validating the webhook signature before processing the payload?"** | Whether your endpoint is vulnerable to forged events. Without validation, any POST from any source is processed. | ⚠️ **Security risk:** Endpoint processes unverified payloads. Attacker can send fake payment confirmations or trigger false events. Expected answer: "Yes, we verify the `Stripe-Signature` or equivalent header." |
| **"Is our webhook handler idempotent — what happens if we receive the same event ID twice?"** | Whether the team has designed for retry-induced duplicates. Retries are a feature, not a bug — but they cause duplication unless handled. | Team hasn't thought about duplicate events; processing the same event twice causes data corruption. |
| **"For SSE connections — are we on HTTP/2? What happens to a user with 7 browser tabs open?"** | HTTP/1.1 browsers support max 6 concurrent SSE connections per domain. The 7th tab receives no updates. HTTP/2 removes this limit entirely. | HTTP/1.1 + multi-tab users = some tabs silently stop receiving updates with no error message. |
| **"What's our mechanism for replaying missed webhook events if our server has an extended outage beyond the vendor's retry window?"** | Whether recovery *beyond* the happy path has been designed. For payment flows, missing events need a reconciliation path — a periodic job that compares local records against vendor records and fills gaps. | ⚠️ **Data loss risk:** Extended outage beyond vendor's retry window = irrecoverable missing events. No reconciliation mechanism exists. |

## Real product examples — named, specific, with numbers

### Stripe — Payment lifecycle events at scale

**What:** Stripe sends webhooks for every payment event (`payment_intent.succeeded`, `payment_intent.payment_failed`, `invoice.paid`, `customer.subscription.deleted`). Non-`2xx` responses trigger retries over 72 hours with exponential backoff. All payloads signed with `Stripe-Signature` header (HMAC-SHA256).

**Why:** At payment scale, reliability is non-negotiable. The signature verification is mandatory—not optional. Dashboard shows full delivery log including retry history and response codes for every event.

**Takeaway:** High-volume merchants are coached to acknowledge immediately (return `200` before processing) and process asynchronously via queue. This prevents timeouts from creating false failures. The design reflects a decade of learning about webhook reliability at payment scale.

---

### GitHub — CI/CD triggering at billions of events per month

**What:** GitHub triggers webhooks on repository events: `push`, `pull_request`, `release`, `check_suite`. Every CI/CD tool (GitHub Actions, CircleCI, Jenkins) depends on the `push` webhook to trigger builds. Payloads signed with `X-Hub-Signature-256` header.

**Why:** Without webhooks, CI systems would need to poll GitHub every few seconds across millions of repositories. The bandwidth and compute cost would be prohibitive. GitHub's webhook delivery is near-real-time, typically under 1 second from event to delivery.

**Takeaway:** GitHub Actions processes over 1 billion workflow runs per month—the scale is only possible because the trigger model is event-driven, not polling-based. This is the anti-pattern that justifies the entire architecture.

---

### Zoom — Recording completion webhooks vs. polling trade-offs

**What:** Zoom fires a `recording.completed` webhook when a cloud recording finishes processing. Delay varies: typically 5–20 minutes for a 1-hour call, occasionally longer during high-demand periods.

**Why:** Teams polling `GET /meetings/{meetingId}/recordings` on 30-second intervals faced two problems:
- Consumed rate limit quota during entire processing window (getting "recording not ready" responses)
- Had to manage retry logic when polling server restarted

Teams using the webhook path had zero requests until ready, then one event with the recording URL.

**Takeaway:** For edtech platforms running 100+ simultaneous classes, the rate limit difference between polling and webhooks at this volume is the difference between free tier and paying for elevated quota. The economics force the architecture choice.

---

### Slack — From persistent connections to event-driven webhooks

**What:** Slack's legacy Real Time Messaging (RTM) API used persistent WebSocket connections. The Events API (webhooks) replaced it in 2016. RTM API is fully deprecated as of 2023 for new apps.

**Why:** Scale problem—millions of installed Slack apps maintaining persistent WebSocket connections consumed enormous server resources at Slack's data centers. Webhooks fire only when events occur, reducing infrastructure load while improving reliability for apps.

**Takeaway:** Even the platform that owns the server benefits from switching to event-driven webhooks when call volume is low relative to event frequency. This is the strongest proof that event-driven is the default pattern at scale.

## What breaks and why

### The idempotency gap discovered in production

> **Idempotency:** Processing the same event multiple times produces the same result as processing it once.

**The failure:** A handler works correctly in testing (rare retries) but creates duplicates in production (frequent double delivery from network issues).

| Testing scenario | Production reality |
|---|---|
| Event received once → action taken | Event received twice → duplicate records, charges, or emails |
| Retries are rare | Network conditions cause routine double delivery |

**The PM prevention rule:** Idempotency is a **required spec item** — not a nice-to-have — for any webhook handler touching:
- Financial state
- User account state  
- Outbound communications (email, SMS, notifications)

⚠️ **Enforce before launch.** Do not defer idempotency to post-launch iterations.

---

### Polling math done at design time vs discovered at scale

**The failure:** Low-volume design doesn't account for 10x user growth, leading to rate limit ceiling crashes and forced re-architecture under production pressure.

**The mandatory calculation:**

```
(active sessions at peak) × (polls per second) × 3600 = requests per hour
```

**Then compare against vendor rate limit.**

| Result | Design decision |
|---|---|
| ≤50% of rate limit at projected scale | Polling is acceptable |
| >50% of rate limit at projected scale | **Webhooks must be the design** |
| Vendor has no webhooks | Rate limit math determines maximum sustainable growth |

---

### Webhook event ordering is not guaranteed

> **Event ordering fallacy:** Webhooks fire in the order events occur, but *delivery order is not guaranteed*.

**The failure mode:**
- `payment.created` event fails initially and retries
- `payment.updated` event delivers immediately  
- `payment.updated` arrives first
- Handler assumes chronological order and corrupts state

**The correct design approach:**

- ✅ Make handlers **state-idempotent** — processing out-of-order events converges to correct state
- ✅ Use the event's own **timestamp or sequence number** for state reconstruction
- ❌ Never rely on arrival order for state decisions

*What this reveals:* Most teams discover this requirement only after seeing corrupted records in production.

---

### SSE connection limits are invisible until they matter

> **SSE connection limit (HTTP/1.1):** Browsers allow only 6 concurrent connections per domain.

**The silent failure:**
- User opens 7 browser tabs
- 7th tab never establishes an SSE connection
- No error message
- No UI feedback
- Users report missing notifications with no clear cause

**The infrastructure requirement:**

| Protocol | Concurrent connections | Action required |
|---|---|---|
| HTTP/1.1 | 6 per domain | ⚠️ Unacceptable for SSE at scale |
| HTTP/2 | No connection limit | ✅ Enable in infrastructure spec |

⚠️ **Enforce HTTP/2 enablement before launch.** Do not discover this when power users report missing notifications.

## How this connects to the bigger system

| Related Lesson | Connection | Why it matters |
|---|---|---|
| **Rate Limiting (01.04)** | Determines whether webhook vs polling is a business decision | Understanding rate limit consumption requires knowing how limits compound across concurrent users. Read both lessons together for third-party API integrations. |
| **API Authentication (01.02)** | Provides security layer specific to webhook's inbound model | Polling: outbound (your server authenticates). Webhooks: inbound (external system calls you). Webhook signature verification is required for inbound call legitimacy. |
| **Queues & Message Brokers (03.06)** | Enables high-reliability webhook processing at scale | Acknowledge webhook immediately (`200`), enqueue for async processing. Production pattern avoids timeouts, enables retry without re-delivery. Cannot design reliable webhook infrastructure without understanding queues. |
| **AI Agent Patterns (04.09)** | Inverts the webhook model into event-driven systems | AI agents responding to events (new ticket, payment failed, onboarding completed) are webhook consumers by another name. Event-driven AI workflows require the same reliability reasoning as webhook handlers. |

## What senior PMs debate

### Polling vs. Webhooks Migration Timeline

| Aspect | Polling First | Webhooks at Design Time |
|--------|---------------|------------------------|
| **Build speed** | Faster | Slower upfront |
| **Debugging** | Easier | More complex |
| **Infrastructure needs** | Minimal | Requires setup |
| **Migration pressure** | Under production load | Planned, controlled |
| **Migration cost** | High, error-prone | Lower, predictable |

**The real debate:** The standard pattern—launch with polling, migrate under load—is almost always wrong. If you're choosing polling for a use case that will predictably scale past the rate limit ceiling within 12 months, you're choosing a known future migration. **Own that choice explicitly, not as a default.**

---

### Webhook Security Coverage

⚠️ **Security adoption is spotty across the industry**, even at well-funded startups.

> **Standard best practices:** Signature verification, replay attack prevention (using event timestamps to reject old events), and rate limiting on webhook endpoints.

**The PM decision framework:**

- **For financial or identity events:** Implement all controls
- **For low-stakes notifications:** Signature verification alone may be sufficient
- **What's not acceptable:** No verification

*What this reveals:* The signature verification is the load-bearing control—it's the minimum. Attackers who can POST fake events need both your endpoint URL *and* your shared secret to cause damage. Defense-in-depth matters for high-risk flows; for others, don't over-engineer.

---

### AI Agents Create a Fourth Category: Model-Initiated Webhooks

> **Model-initiated webhooks:** An AI system registers dynamic webhook endpoints per task, receives events during task execution, and deregisters them on completion.

**New problems this creates:**
- Dangling endpoints after task completion
- Credential leaks in dynamic URL schemes
- Event ordering across concurrent agent tasks

**Emerging standard:** AI agent platforms (LangGraph, OpenAI's function calling infrastructure) abstract webhook management internally.

**The PM question:** Do you need to understand the underlying mechanics, or treat this as a black box?

*What this reveals:* Treat it as a black box until you hit a reliability incident. Then you'll need to understand exactly this level of detail.

## Prerequisites

→ 01.01 What is an API — polling is repeated API calls; webhooks are inbound API calls; read first



## Next: read alongside (companions)

- **01.02 API Authentication** — how webhook signatures verify the caller is genuine
- **01.04 Rate Limiting & Throttling** — polling's rate limit consumption makes this lesson concrete

## Read after (deepens this lesson)

- **03.06 Queues & Message Brokers** — the reliability layer for production webhook processing
- **04.09 AI Agent Patterns** — event-driven AI; agents as webhook consumers