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

In 2014, a payments startup integrated with a payment processor to handle checkout. To know whether a payment had succeeded or failed, they built the obvious thing: every five seconds, their server called the processor's status endpoint asking "did this payment complete?"

It worked fine in testing. In production, with 200 active checkouts happening simultaneously, their server was making 2,400 requests per minute just asking "is it done yet?" on payments that typically took under 3 seconds to process. They hit their rate limit within the hour. The processor throttled them. Real payments stopped confirming. Support tickets flooded in.

Meanwhile, a competitor had registered a webhook URL with the same processor. When each payment completed, the processor called that URL with the result — one request, at the exact moment the payment was ready. No polling loop, no rate limit burned, no artificial delay. Zero requests until an event actually happened.

The question "how do we know when something external changes?" has two answers: keep asking, or wait to be told.

## What it is

Polling and webhooks are two patterns for getting data from an external system when something changes.

Think of it like waiting for a package. Polling is checking your doorstep every ten minutes — you're doing all the work, most checks find nothing, and you might still miss a narrow pickup window. Webhooks are the delivery company texting you the moment they drop it off. You do nothing until the moment it matters.

**Polling** — your system calls the external API on a fixed schedule ("every 30 seconds, check if this order shipped"). Easy to build. Self-healing — if your server is down, polling resumes automatically when it comes back. Wasteful — most requests return "nothing changed."

**Webhooks** — the external system calls your server when an event fires ("when this order ships, POST to your URL"). No wasted requests. Near-real-time delivery. More complex to operate — if your server is down when an event fires, you have to rely on the vendor to retry.

Both solve the same problem: knowing when something external changes. The tradeoff is who bears the work and where the reliability burden sits.

## When you'll encounter this as a PM

**Writing an integration spec.** Every time you integrate with a third-party service, the first question is: do they offer webhooks, or do your engineers have to poll? This question belongs in your spec, not in the sprint review. The answer affects your rate limit budget, your data freshness, and how much engineering complexity you're taking on.

**Defining a real-time requirement.** "Confirmation immediately" requires webhooks — polling adds 0 to N seconds of lag where N is your polling interval. "Within a minute is fine" can be polling. You own this tolerance decision. If you spec a feature with instant confirmation but don't spec webhooks, your engineers will build polling and call it done.

**Incident triage.** Two failure patterns map cleanly: missing events usually means a webhook failure (your endpoint was down and the vendor stopped retrying). Delayed events usually means the polling interval is too long. Different root cause, different fix. Knowing which you have cuts triage time in half.

**Evaluating a vendor.** When you're assessing a third-party integration, check whether they offer webhooks — and if so, what their retry policy is. A vendor who makes one webhook attempt and gives up puts the entire reliability burden on your server's uptime. Stripe retries for 72 hours. Some vendors don't retry at all. This is a vendor selection criterion, not an engineering detail.

**Planning for scale.** An integration that polls every second uses 3,600 API requests per hour. At 10,000 active sessions, that's 36 million requests per hour from polling alone — before any real work happens. Webhooks use one request per actual event. The scale math almost always favors webhooks above a few hundred users.

---


# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs, PMs 2+ years in
# Assumes: Foundation. You know what polling and webhooks are. Now let's build the working model.
# ═══════════════════════════════════

## How it actually works

**Polling — the full sequence:**

1. Your server initiates an HTTP GET to the external API: `GET /api/payments/txn_abc123/status`
2. The API authenticates the request and queries its database for the current state.
3. The API returns the current status: `{"status": "pending"}` with a 200.
4. Your server evaluates: if not "complete," wait the polling interval (say, 5 seconds) and repeat.
5. Eventually, the API returns `{"status": "succeeded"}` — your server processes the outcome.
6. Each iteration is a full round-trip — authentication, database query, HTTP response — even when nothing has changed. For 100 active polls at 5-second intervals, that's 1,200 requests per minute consuming server resources and rate limit budget continuously.

**Long polling — the hybrid:** The server holds the request open instead of returning immediately. Your server sends the request; the external API waits until there's new data (up to a configured timeout, typically 30 seconds) before responding. You get near-real-time delivery without the overhead of a persistent connection. Tradeoff: it's complex to implement and struggles under high concurrency because each open connection consumes a server thread.

**Webhooks — the full sequence:**

1. Setup (one-time): you register your endpoint URL with the vendor. `POST /api/webhook/register` with `{"url": "https://yourapp.com/webhooks/payments", "events": ["payment.succeeded", "payment.failed"]}`.
2. Nothing happens until an event fires on the vendor's side.
3. When the event occurs, the vendor's system POSTs a payload to your registered URL: `{"event": "payment.succeeded", "data": {"payment_id": "txn_abc123", "amount": 4999, "currency": "usd"}}`.
4. Your server must respond with `200 OK` within the vendor's timeout window (typically 5–30 seconds). Response body doesn't matter — just the status code.
5. If no `200`: the vendor retries according to their policy — often exponential backoff over hours or days. Stripe retries over 72 hours. GitHub retries for a few hours. Some vendors retry once and stop.
6. **Idempotency is required:** because vendors retry, the same event may arrive twice. Your handler must be idempotent — processing the same event ID twice produces the same outcome as once. The standard pattern: store processed event IDs, check before acting, return `200` if already handled.
7. **Signature verification is required:** the vendor signs the payload with a shared secret. Your handler must verify the signature before processing. An unverified webhook is an open endpoint that any attacker can POST fake events to.

**Server-Sent Events (SSE) — the persistent push:** For product scenarios where you need real-time updates from your own backend to a browser (not third-party), SSE opens a persistent HTTP connection from the browser to your server. The server pushes updates down the stream as events occur. Unidirectional (server → client only), simpler than WebSockets, built into modern browsers with automatic reconnection. Used for: live notification feeds, class status updates, real-time dashboards. The KB source constraint: HTTP/1.1 limits browsers to 6 concurrent SSE connections per domain — resolved by enabling HTTP/2 on the server.

## The decisions this forces

**When to poll vs webhook — default to webhooks if available.** Polling is the right choice when: (1) the vendor offers no webhooks, (2) the feature tolerates 30+ seconds of lag, (3) you need a simple one-time status check with no ongoing stream. Webhooks are the right choice for everything else where freshness matters. The PM call: if a vendor pitches their integration and doesn't mention webhooks, ask explicitly. Discovering mid-sprint that polling is the only option changes the estimate, the rate limit budget, and the reliability architecture.

**Polling interval vs data freshness vs rate limit budget.** These three are in direct tension. Shorter interval = fresher data = more API calls = faster rate limit exhaustion. A 1-second polling interval on a 5,000-request/hour limit exhausts the budget in 83 minutes — before any real business logic runs. The right interval is determined by: what's the maximum acceptable lag for this feature, and what's the rate limit math at your expected user volume? Calculate both before speccing the interval. "Poll every second" without the rate limit math is an incomplete spec.

**Webhook reliability design.** Your webhook endpoint will go down. The question is what happens then. Decisions the PM owns: (1) What's your server's expected uptime? If 99%, you'll miss 1% of events during outages. Is that acceptable? (2) Does the vendor retry — and for how long? If the vendor retries for 72 hours and your server recovers in 10 minutes, you lose nothing. If the vendor retries once, you need a compensating mechanism (reconciliation job, manual replay). (3) For which event types is missing an event acceptable vs catastrophic? Payment confirmations: catastrophic. Feed update notifications: acceptable. Different events warrant different reliability designs.

**Idempotency: not optional for webhooks.** Because webhooks retry on failure, and network conditions can cause double delivery even without explicit failures, your handler will receive the same event more than once. If the handler isn't idempotent — if processing the same event twice creates two records, two charges, or two emails — you have a data integrity bug triggered by normal webhook behavior. The engineering solution: deduplicate on the vendor-provided event ID before acting. This is engineering complexity the PM should factor into the sprint estimate. "Add webhook support" is not a one-story ticket if the feature involves financial transactions or user-facing state changes.

**SSE vs WebSockets for your own real-time features.** When building real-time push from your backend to users (not third-party webhooks), the choice is: SSE for one-way server push (notifications, feeds, status updates), WebSockets for bidirectional real-time (chat, collaborative editing, live classrooms). SSE is significantly simpler to implement and operate — uses standard HTTP, automatic reconnection, firewall-friendly. WebSockets are lower-latency, support binary data, and allow the client to send messages, but require custom reconnection logic and may fail behind corporate firewalls. Default to SSE unless the feature explicitly requires the client to push data in real time.

## Questions to ask your engineer

1. **"Does this vendor offer webhooks — and what's their retry policy and maximum retry window?"** Reveals whether near-real-time is possible and what the reliability guarantee is. If the vendor retries for 72 hours, downtime under that window is recoverable. If they retry once, your server availability directly determines whether events are lost.

2. **"If our webhook endpoint is down for 20 minutes, what happens to events that fired during that window — do we lose them, or does the vendor queue them?"** Tests the explicit failure mode. Expected: vendor retries, events recover. Concerning: vendor sends once, events are lost. If events can be lost, what's the reconciliation path?

3. **"For our polling approach — what interval are we using, how many active sessions hit this at peak, and how much of our rate limit does that consume per hour?"** Forces the rate limit math before sprint start. This calculation should be in the integration spec, not discovered in production.

4. **"Are we validating the webhook signature before processing the payload?"** If not, your webhook endpoint will process any POST from any source. An attacker can send fake payment confirmations or trigger false events. This is a critical security gap. Expected answer: yes, we verify the `Stripe-Signature` or equivalent header.

5. **"Is our webhook handler idempotent — what happens if we receive the same event ID twice?"** Tests whether the team has designed for retry-induced duplicates. Expected: we check the event ID against a processed-events store. Concerning: we haven't thought about this.

6. **"For SSE connections — are we on HTTP/2? What happens to a user with 7 browser tabs open?"** HTTP/1.1 browsers support a maximum of 6 concurrent SSE connections per domain. The 7th tab gets no updates. HTTP/2 removes this limit. If the answer is "we're on HTTP/1.1 and haven't thought about this," that's a real user-impacting limitation.

7. **"What's our mechanism for replaying missed webhook events if our server has an extended outage beyond the vendor's retry window?"** Tests whether recovery beyond the happy path has been designed. For payment flows, missing events need a reconciliation path — a periodic job that compares local records against vendor records and fills gaps. Without this, extended outages create irrecoverable data loss.

## Real product examples — named, specific, with numbers

**Stripe's webhook architecture: the industry reference.** Stripe sends webhooks for every payment lifecycle event — `payment_intent.succeeded`, `payment_intent.payment_failed`, `invoice.paid`, `customer.subscription.deleted`. Non-`2xx` responses trigger retries over 72 hours with exponential backoff. Payloads are signed with a `Stripe-Signature` header containing an HMAC-SHA256 signature — verification is mandatory for security. Stripe's dashboard shows the full delivery log for every webhook event including retry history and response codes. For high-volume merchants, Stripe recommends acknowledging immediately (return `200` before processing) and processing asynchronously via a queue — preventing timeouts from creating false failures. The design reflects a decade of learning about webhook reliability at payment scale.

**GitHub's CI/CD webhook model.** GitHub triggers webhooks on repository events: `push`, `pull_request`, `release`, `check_suite`. Every CI/CD tool (GitHub Actions, CircleCI, Jenkins) depends on the `push` webhook to trigger builds. Without webhooks, CI systems would need to poll GitHub every few seconds across millions of repositories — the bandwidth and compute cost would be prohibitive. GitHub's webhook delivery is near-real-time, typically under 1 second from event to delivery. GitHub signs payloads with a `X-Hub-Signature-256` header. GitHub Actions processes over 1 billion workflow runs per month — the scale is only possible because the trigger model is event-driven, not polling-based.

**Zoom's recording-ready webhook.** Zoom fires a `recording.completed` webhook when a cloud recording finishes processing. The delay between call end and recording availability varies: typically 5–20 minutes for a 1-hour call, occasionally longer for high-demand periods. Teams that polled `GET /meetings/{meetingId}/recordings` on a 30-second interval hit two problems: (1) they consumed rate limit quota during the entire processing window, getting "recording not ready" responses, and (2) they had to manage retry logic when their polling server restarted. Teams on the webhook path had none of these issues — zero requests until the recording was ready, then one event with the recording URL. For edtech platforms running 100+ simultaneous classes, the rate limit difference between polling and webhooks at this volume is the difference between staying within free tier and paying for elevated quota.

**Slack's event API and the polling-to-webhooks migration.** Slack's legacy Real Time Messaging (RTM) API used persistent WebSocket connections. The Events API (webhooks) replaced it in 2016. The migration was driven by scale: millions of installed Slack apps maintaining persistent WebSocket connections consumed enormous server resources at Slack's data centers. Webhooks — firing only when events occur — reduced Slack's infrastructure load while improving reliability for apps. As of 2023, Slack has deprecated the RTM API entirely for new apps. The architectural lesson: even the platform that owns the server can benefit from switching from persistent connections to event-driven webhooks when the call volume is low relative to the event frequency.

---


# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineers turned PM, senior PMs, heads of product, AI-native PMs
# Assumes: Working Knowledge. Skip here if you've built webhook consumers before.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## What breaks and why

**The idempotency gap discovered in production.** The most expensive webhook failure pattern isn't a missing signature check — it's a handler that processes duplicate events correctly in testing (where retries are rare) and creates duplicate records, charges, or emails in production (where network conditions routinely cause double delivery). Engineers test "event received, action taken." They rarely test "event received twice, action taken once." The PM prevention role: idempotency is a required spec item for any webhook handler touching financial state, user account state, or outbound communications. Not a nice-to-have. Not "we'll add it if we see duplicates." Required before launch.

**Polling math done at design time vs discovered at scale.** The failure mode is predictable: a team designs a polling integration at low volume, doesn't calculate rate limit consumption at projected scale, and discovers the problem when 10x user growth drives 10x polling requests into a rate limit ceiling. At that point, migrating from polling to webhooks is a full re-architecture under production pressure. The calculation is simple and should be mandatory in the integration spec: (active sessions at peak) × (polls per second) × 3600 = requests per hour. Compare against rate limit. If it's over 50% of the limit at projected scale, webhooks must be the design. If the vendor doesn't offer webhooks, the rate limit math determines how the integration can grow.

**Webhook event ordering is not guaranteed.** Vendors fire webhooks in the order events occur, but delivery order is not guaranteed. A `payment.updated` event can arrive before the `payment.created` event if the first delivery failed and retried while the second delivered immediately. Handlers that assume chronological ordering will corrupt state. The correct design: handlers must be state-idempotent (processing out-of-order events converges to correct state) and should use the event's own timestamp or sequence number, not arrival order, for state reconstruction. Most teams don't think about this until they see corrupted records.

**SSE connection limits are invisible until they matter.** HTTP/1.1 browsers allow 6 concurrent connections per domain. For an SSE implementation on HTTP/1.1, a user with 7 browser tabs open gets no real-time updates on the 7th tab — silently. There's no error, no notification, no UI feedback. The 6th connection just never establishes. Teams running SSE at scale on HTTP/1.1 often discover this from user complaints about missing notifications, not from monitoring. HTTP/2 removes the limit, but requires intentional server configuration. The PM role: ensure HTTP/2 enablement is in the SSE infrastructure spec, not discovered post-launch when power users start reporting missing notifications.

## How this connects to the bigger system

**Rate Limiting (01.04)** is the mathematical ceiling that makes webhook vs polling a business decision, not just a technical preference. Understanding polling's rate limit consumption requires the rate limiting lesson's mental model for how limits compound across concurrent users. The two lessons should be read together for any integration involving third-party APIs.

**API Authentication (01.02)** provides the security layer that webhooks require beyond what polling needs. Polling is outbound — your server initiates authenticated requests. Webhooks are inbound — an external system calls your server, and you must verify the call is legitimate. Webhook signature verification is the auth mechanism for inbound calls; without it, your webhook endpoint is an unauthenticated HTTP endpoint.

**Queues & Message Brokers (03.06)** is the architectural layer that makes high-reliability webhook processing possible. Acknowledging the webhook immediately (return `200`) and enqueuing the event for async processing is the production-grade pattern for avoiding timeouts and enabling retry without re-delivery from the vendor. You cannot design reliable webhook infrastructure at scale without understanding queues.

**AI Agent Patterns (04.09)** inverts the webhook model: AI agents that need to take actions in response to events are event-driven systems where webhooks are the trigger mechanism. An AI agent that responds to "new support ticket created" events, "payment failed" events, or "user onboarding step completed" events is a webhook consumer by another name. Designing event-driven AI workflows requires the same reliability reasoning as designing reliable webhook handlers.

## What senior PMs debate

**The polling-to-webhooks migration timeline is almost always wrong.** The standard product pattern: launch with polling ("we'll migrate to webhooks when we need to scale"), then face a migration under load rather than planning it at design time. The argument for "polling first" is real: it's faster to build, easier to debug, and requires no infrastructure on your end beyond the polling loop. The argument against: migration under production pressure is expensive, error-prone, and requires feature flag coordination during cutover. The PM's decision should be explicit, not a default. If you're choosing polling for a use case that will predictably scale past the rate limit ceiling within 12 months, you're choosing a known future migration. Own that choice.

**Webhook security is under-specced across the industry.** Signature verification, replay attack prevention (using the event timestamp to reject old events), and rate limiting on your own webhook endpoints are all documented best practices, but adoption is spotty even at well-funded startups. The counter-argument to "just implement all security controls": the real attack surface for most webhook endpoints is low — an attacker who can POST fake events to your payment webhook needs to know both your endpoint URL and your shared secret to cause damage. The signature verification is the load-bearing control; the rest is defense-in-depth. The PM call: for financial or identity events, implement all controls. For low-stakes notifications, signature verification alone may be sufficient. What's not acceptable is no verification.

**AI agents are creating a fourth category: model-initiated webhooks.** The classic model is: (1) your system polls external APIs, or (2) external systems push webhooks to you. AI agents introduce a third model: an AI system registers dynamic webhook endpoints per task, receives events during task execution, and deregisters them on completion. This creates webhook lifecycle management problems — dangling endpoints, credential leaks in dynamic URL schemes, event ordering across concurrent agent tasks — that the classic webhook model wasn't designed for. The emerging standard is AI agent platforms (LangGraph, OpenAI's function calling infrastructure) abstracting webhook management internally. Whether PMs building agent features need to understand the underlying mechanics or can treat this as a black box is an open question. My position: treat it as a black box until you hit a reliability incident, then you'll need to understand exactly this level.

---

## Prerequisites

→ 01.01 What is an API — polling is repeated API calls; webhooks are inbound API calls; read first

## Next: read alongside (companions)
→ 01.02 API Authentication — how webhook signatures verify the caller is genuine
→ 01.04 Rate Limiting & Throttling — polling's rate limit consumption makes this lesson concrete

## Read after (deepens this lesson)
→ 03.06 Queues & Message Brokers — the reliability layer for production webhook processing
→ 04.09 AI Agent Patterns — event-driven AI; agents as webhook consumers
