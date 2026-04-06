---
lesson: Idempotency
module: 01 — APIs & System Integration
tags: tech
difficulty: foundation
prereqs:
  - 01.01 — What is an API — an API call is the unit of operation; idempotency is a property of those calls
  - 01.02 — API Authentication — idempotency keys are not auth tokens; the distinction matters
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/payments/payment-flow.md
  - technical-architecture/payments/payment-initiation.md
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
# Assumes: 01.01 What is an API. You know what an API call is.
# ═══════════════════════════════════

## F1. The world before this existed

The support ticket came in on a Tuesday. "You charged me twice."

The product manager opened the payment logs. Two records. Two different transaction IDs. Both marked successful. Both charged to the same card on the same afternoon, three minutes apart.

Here is what had actually happened. A parent had opened the checkout screen on her phone, filled in her card details, and tapped "Pay Now." The spinner appeared. Eight seconds passed. Nothing. The app looked frozen. She tapped "Pay Now" again. The confirmation screen appeared. She assumed the first tap had failed.

It hadn't. The first payment had gone through. The confirmation just never arrived — a brief drop in mobile signal. By the time the second tap went out, the first charge was already recorded. The server saw two separate, valid payment requests. It processed both.

The team spent two days on this incident. They manually reversed one charge, absorbed the gateway fee on both transactions, and explained to the customer why the app had taken money twice. The engineering lead traced the root cause. The payment API had no deduplication logic. If the same request arrived twice — from a retry, a double-tap, or a network glitch — it created a new transaction every time.

This is the problem idempotency solves. Not "payments are complex." Not "retry logic is hard." The specific problem: when an operation is triggered more than once, how do you guarantee it only takes effect once?

## F2. What it is — definition and analogy

**Idempotency** means an operation can be performed multiple times and always produce the same result. The first call changes something. Every additional call returns the same result without changing anything further.

Before any mechanism: the hotel key card. When you tap your key card on the door reader, it unlocks. If you tap again immediately, the door is already open — it doesn't unlock twice, it doesn't log a second entry, it doesn't charge you for two unlocks. Tap once or tap ten times, you get exactly one unlocked room. The operation is idempotent.

A payment request is not naturally idempotent. Send it once: charge the card, create a transaction record, send a confirmation email. Send it again: another charge, another record, another email. The server treats each request as a new, separate instruction.

An **idempotency key** is a unique token that the client attaches to a request before sending it. Think of it as a serial number for that specific operation. The server checks: "Have I seen this serial number before?" First time — process the request. Already seen it — return the original result. No second charge. No second record. Same outcome, however many times the request arrives.

Two clarifications before moving on. First, idempotency keys are not passwords. They do not authenticate who you are — authentication is a separate system (covered in 01.02). They only tell the server "this is the same operation you already handled." Second, GET requests — those that only fetch data — are naturally idempotent. Fetching the same page ten times returns the same data without changing anything. The problem is write operations: creating a payment, adding a record, sending a notification. Those need explicit idempotency handling.

## F3. When you'll encounter this as a PM

**Checkout and payment flows.** Any payment button that operates over a mobile connection or can be tapped more than once needs idempotency logic. If your checkout doesn't have it, you have double-charge risk on every retry. You will discover this through a customer complaint, not a code review.

**Credit and balance operations.** If your product gives users credits, tokens, or class bookings, and those credits come from an API call — that API must be idempotent. If an engineer calls the credit API twice during a bug fix, the user should receive one credit, not two.

**Email and notification triggers.** "Send welcome email" should fire once per signup. If the event that triggers it fires three times during a gateway outage — which happens — the user should receive one email, not three. You specify this in the API contract: "this endpoint must be idempotent."

**Background job retries.** Any scheduled job that fails and retries — provisioning a user account, syncing data to a CRM, generating a report — needs to be safe to run multiple times. "Safe to retry" is the practical PM translation of idempotency. When you spec a background job, add this line: "If this job runs more than once, the result must be identical to running it once."

**Webhook processing.** Payment gateways send webhook notifications when a payment completes. During outages, they often send the same notification multiple times. If your system processes each webhook as a new event, one payment can generate multiple internal records. This is a documented failure pattern in real payment architectures.


# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PM, consumer startup PM, B2B enterprise PM, 2+ years experience
# Assumes: Foundation. You understand what an idempotency key is and why payments need one.
# ═══════════════════════════════════

## W1. How it actually works

This is the full request lifecycle for an idempotent payment operation.

1. **Client generates a unique key.** Before sending the request, the client — whether a frontend, mobile app, or backend service — generates a UUID: a randomly generated, universally unique identifier. Example: `idem_7f3a2c91-4b5e-4d89-a1f2-83c91e6b2d44`. This key must be unique per intended transaction, not per API call. The client generates it once, then reuses it on every retry for that same operation.

2. **Client sends the request with the key attached.** The full request goes out with the idempotency key as an HTTP header: `Idempotency-Key: idem_7f3a2c91-4b5e-4d89-a1f2-83c91e6b2d44`, alongside the payload — amount, currency, customer ID, payment aggregator.

3. **Server checks its idempotency key store.** Before processing anything, the server queries its key store — typically Redis or a dedicated database table — for that exact key. This check happens before any external call is made.

4. **First arrival — key is new.** The key is not found. The server proceeds: it calls the payment aggregator (Stripe, Razorpay, Xendit, etc.), records the transaction, updates the customer's balance. The full operation runs.

5. **Server stores the key and the result atomically.** After processing, the server writes: `{key: idem_7f3a2c91..., result: {transactionId: "txn_abc", status: "paid", amount: 299}, expires: +24h}`. The result is cached for the duration of the idempotency window.

6. **Network drops — the response never reaches the client.** The payment processed. The server returned 200. But the mobile signal cut out. The app received nothing.

7. **Client retries with the same key.** The retry logic fires after a timeout. The client sends the same request, same payload, and — critically — the same `Idempotency-Key` header. The key was generated before the first attempt and has not changed.

8. **Server finds the key — returns cached result.** The server queries the key store. The key exists. It does not process the request again. It returns the cached result: `{transactionId: "txn_abc", status: "paid", amount: 299}`.

9. **Client receives the original result and confirms success.** From the client's perspective: payment succeeded. From the server's perspective: nothing changed. One charge. One record. One confirmation email.

The critical implementation requirement: the idempotency key check must be **atomic with the processing step**. If two requests with the same key arrive simultaneously — a real scenario during concurrent retries — the server must guarantee only one gets processed. This requires an atomic database operation: a conditional INSERT that fails if the key already exists, not a read-then-write sequence. A read-then-write has a race window where two simultaneous requests both pass the "key not found" check and both proceed to the aggregator.

## W2. The decisions this forces

**1. Who generates the idempotency key — the client or the server?**
If the client generates it, the client controls deduplication. A frontend bug that generates a new key on each retry defeats the entire mechanism — each retry looks like a new transaction. If the server generates it, the client can't retry safely because it doesn't have the key to reuse on the next call. The right answer: client generates, server validates and stores. The PM's job is to spec this explicitly in the API contract. "The caller must generate a UUID before initiating this operation and must use the same UUID on all retries" is a one-line spec requirement that prevents an entire class of production incidents.

**2. How long should idempotency keys be stored?**
Stripe uses 24 hours. Some systems use 7 days. Too short: a retry that arrives after an extended outage finds an expired key and processes as a new transaction — double charge. Too long: key storage scales proportionally with transaction volume, adding infrastructure cost. For payment operations, 24 hours covers the vast majority of legitimate retry windows. For account provisioning or large data imports where retries might span days, extend to 7 days. This is a business policy, not a technical default. PM must specify it — not leave it for engineering to pick.

**3. What happens when the payment processes but key storage fails?**
This is the partial failure trap. The aggregator charge succeeds. The server attempts to write the idempotency key to Redis. Redis returns a connection error for 200ms. The key is never stored. The retry fires. The key isn't found. The server processes again. Second charge. This scenario bites teams that implement idempotency key storage as an afterthought — separate from the aggregator call, on infrastructure that can fail independently. The fix: make the key write and the aggregator call within the same failure boundary, or use a two-phase approach where the key is pre-stored before the aggregator call with a "pending" status, then updated to "complete" after. Ask your engineer: "If key storage fails, what happens to the operation that just completed?"

**4. Which operations need idempotency guards — just payments, or everything?**
Most teams add idempotency to payment creation and forget everything downstream. One online learning platform's payment architecture documented as High severity technical debt: "No documented webhook idempotency guard — duplicate payments possible," with the proposed fix being "idempotency key check on webhook handler using `transaction_id` deduplication." The webhook handler, the credit allocation step, the account provisioning step, the notification trigger — all are mutating operations that can fire multiple times. The right scope: any API call that creates records, moves money, allocates access, or triggers communications. If your engineer says "we only need it on the payment endpoint," push back.

**5. How should a duplicate key be handled at the response level?**
Two approaches: return 200 with the original result and an `X-Idempotent-Replayed: true` header, or return 409 Conflict. The 200 approach is correct for operations where idempotency confirms completion. The client asked "did this happen?" and the answer is yes — return the original success response. A 409 implies a conflict, which triggers error-handling code paths in the client and may surface an error message to the user on what was actually a successful operation. Stripe uses 200 with a replay header as the industry reference. Push back if your engineering team defaults to 409 on duplicate keys for payment or provisioning operations.

## W3. Questions to ask your engineer

**"Where exactly is the idempotency key generated — in the frontend, the API client layer, or the backend service?"** (This reveals: whether the key is consistent across retries. If the frontend generates a new key on each page reload, every retry creates a new transaction. This is the most common implementation mistake.)

**"What's our idempotency window, and who decided that number?"** (This reveals: whether the window was set deliberately or defaulted to 24 hours because it's Stripe's default. The right window depends on your longest plausible retry scenario — a payment from a user with spotty connectivity may not retry for 12 hours.)

**"If the aggregator call succeeds but our idempotency key storage write fails — what's the outcome?"** (This reveals: partial failure handling. If the team says "that can't happen" or "we'd have bigger problems," you have latent double-charge risk. The correct answer names a specific failure handling strategy.)

**"Are webhook handlers idempotent? What prevents us from processing the same webhook event twice?"** (This reveals: a documented gap in many payment architectures. Payment gateways retry webhook delivery on failure. If the handler processes the payment on each delivery, one payment event can generate multiple internal transaction records.)

**"Is the idempotency check atomic, or is it read-then-write?"** (This reveals: whether concurrent retries are safe. A read-then-write implementation has a race window where two simultaneous retries both pass the "key not found" check and both reach the aggregator. The correct implementation uses a conditional atomic INSERT.)

**"What's the infrastructure for our key store — is it within the same failure boundary as the payment operation?"** (This reveals: the partial failure scenario. If key storage is a separate Redis cluster that can fail independently from the main database, the idempotency guarantee is weaker than it appears on paper.)

**"What's the list of all write operations in this payment flow — payment creation, credit allocation, access provisioning, notification triggers — and which ones have idempotency guards?"** (This reveals: the actual scope of protection. Most teams can answer for the payment creation step. Almost none can answer comprehensively for the full downstream chain.)

## W4. Real product examples

**Stripe.** Every write operation in Stripe's API accepts an `Idempotency-Key` header. The window is 24 hours. On a duplicate key, Stripe returns the original response from cache and sets the `X-Stripe-Should-Retry` header to `false`. Their documentation explicitly states: "If a request fails due to a network error, retry with the same idempotency key — not a new one." This is the industry reference implementation. When evaluating any payment API your team is building or integrating, the question "does it behave like Stripe on retries" is a useful shorthand for "is idempotency correctly implemented."

**Multi-gateway payment systems.** An online learning platform operating across 7 payment aggregators (Razorpay for India, Stripe for USD markets, Xendit for Indonesia, Tabby for UAE/Saudi Arabia) had the following documented as High-severity technical debt in its architecture review: "No documented webhook idempotency guard — duplicate payments possible." The system received webhook callbacks from each gateway independently. The immediate fix proposed: "Add idempotency key check on webhook handler using `transaction_id` deduplication." The pattern — multi-gateway systems where each gateway fires webhooks independently and the internal handler doesn't check for duplicate `transaction_id` before processing — is one of the most common payment correctness failures in production.

**AWS.** Many AWS API operations are designed idempotent by default. `CreateBucket` with the same bucket name from the same account returns 200 if the bucket already exists, rather than an error. `CreateOrUpdateTags` on an EC2 instance applies the tag once, not repeatedly, on duplicate calls. DynamoDB's conditional writes (`PutItem` with a `ConditionExpression` that checks if the item already exists) are the infrastructure-level primitive most server-side idempotency implementations are built on. AWS's decision to document per-operation idempotency behavior explicitly is a model worth following when designing internal APIs — state clearly, in the API contract, which operations are idempotent and what behavior the caller can rely on during retries.

**Twilio.** Twilio's messaging API accepts an `Idempotency-Key` header on outbound SMS and WhatsApp sends. Their documentation notes that without an idempotency key, a retry following a network timeout will send the message a second time. With the key, the second send returns the original message SID and status — no duplicate delivery. For products that send transactional messages (payment confirmations, one-time passcodes, booking confirmations), the PM's job is to specify that the message-sending API call is idempotent — not assume the underlying service handles it.


# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineer PM, senior PM, head of product, AI-native PM
# Assumes: Working Knowledge. You understand the full idempotency key lifecycle and the partial failure problem.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. What breaks and why

**The partial failure trap at scale.** Single-service idempotency fails under distributed load not through incorrect logic, but through infrastructure split: the aggregator call succeeds, key storage fails for 200ms during a Redis availability blip, the retry fires, the key isn't found, a second charge processes. This is not a rare race condition — it is predictable under peak payment load, which is exactly when retry storms occur. The PM prevention role: require that key storage and operation processing share a failure boundary. Pre-storing the key with a "pending" status before the aggregator call, then updating it to "complete," ensures a crash between the two steps either blocks the retry (key found, status pending — return pending result) or allows reprocessing (key not stored — process fresh). Teams that treat Redis key storage as best-effort have not actually implemented idempotency. They have implemented optimistic deduplication, which is a different and weaker guarantee.

**The expired key retry window.** A customer initiates a payment. Their device goes offline for 28 hours — extended outage, device powered off, travel without connectivity. The retry fires when they reconnect. The 24-hour key window has expired. The server processes a second payment. From the system's perspective, everything behaved correctly: the key was valid for 24 hours, that's the stated contract. From the customer's perspective, they attempted one purchase and were charged twice. This failure is guaranteed to occur eventually if the idempotency window is shorter than your longest plausible retry interval. The window is a business policy, not a technical constant, and it must be set deliberately — not inherited from Stripe's default because your gateway uses Stripe.

**Idempotency applied at the wrong boundary.** The "charge payment" endpoint is idempotent. The "provision access" endpoint downstream is not. The "send onboarding email" trigger is not. One payment event creates one charge, three access grants, and three welcome emails. A real architecture review flagged exactly this: webhook handlers for a multi-gateway payment system had no idempotency check, meaning a single successful payment that triggered multiple webhook deliveries (common during gateway retries) created multiple internal transaction records, multiple credit allocations, and multiple email sends. The PM who signed off on "payment is idempotent" without auditing the full downstream mutation chain signed off on a system that is not actually idempotent end to end.

**The atomic check race condition under concurrent retries.** A client sends a payment request. Network timeout at 30 seconds. The client fires two parallel retries. Both arrive at the server within 50ms. The server reads the key store — neither has been stored yet. Both pass the "key not found" check. Both proceed to the aggregator. Two charges. This is the canonical read-then-write race condition, and it occurs at exactly the moments when retry pressure is highest: network instability, gateway degradation, high-concurrency checkout windows. The fix is an atomic conditional INSERT — a database-level write that succeeds only if the key does not exist, failing and returning the existing record otherwise. A PM reviewing a payment system implementation should ask "how does the key check handle simultaneous retries" and expect a specific, technical answer — not "we use Redis so it's fast."

## S2. How this connects to the bigger system

**01.03 Webhooks vs Polling.** Webhooks and idempotency are structurally coupled. The decision to use webhooks (01.03) creates an automatic idempotency requirement on the webhook handler. Payment gateways retry webhook delivery when the handler doesn't return 200 quickly enough — Stripe retries up to 36 times over 3 days. A PM who understands webhooks but not idempotency will spec a system that treats each webhook delivery as a new event. The result: one payment creates multiple internal records, multiple credits, multiple emails. The architecture review KB documents this exact pattern as a High-severity gap. The lesson: you cannot reason about webhook architecture without simultaneously reasoning about handler idempotency.

**01.02 API Authentication.** An idempotency key is not an authentication token. They are distinct mechanisms that operate on orthogonal axes: authentication answers "who is making this request," idempotency answers "have I processed this exact operation before." They are confused in API design when teams use the auth token or session ID as the idempotency key. This collapses all operations from the same authenticated user into one — a second payment from the same session returns the first payment's result, regardless of amount or intent. The PM reviewing an API contract should verify that idempotency keys are scoped to individual operations, not to sessions or users.

**01.04 Rate Limiting & Throttling.** Rate limiting and idempotency address different failure modes from the same root cause: too many requests to a system. Rate limiting prevents a volume problem. Idempotency prevents a correctness problem. A system with rate limiting but without idempotency will stop retry storms from overwhelming infrastructure — but provides no protection when retries occur within the rate limit window. The PM who specs only rate limiting on a payment API has solved availability but not correctness. Both must be designed together: rate limiting sets the ceiling on request volume; idempotency ensures that requests below that ceiling, including retries, produce correct outcomes.

**01.09 Error Codes & Response Design.** The response format for a duplicate idempotency key is an API design decision with measurable product consequences. Returning 409 on a duplicate key causes the client's error-handling code to fire — surfaces "payment failed" to the user on a transaction that actually succeeded. Returning 200 with the original result continues the success flow — correct UX, correct analytics event, correct receipt trigger. The difference between 200 and 409 on a duplicate key is the difference between a good checkout experience and a confusing one during a network retry. This is a spec decision, and it belongs in the PM's API design review, not engineering's default.

## S3. What senior PMs debate

**Who owns the idempotency spec?** The prevailing position is that idempotency is an engineering concern — PMs don't spec it, engineers implement it. The evidence against this: every double-charge postmortem ends with a PM asking "why didn't we spec this?" The idempotency window, the key generation responsibility, the partial failure policy, the response format on duplicates — these are business decisions wearing technical clothing. What's the acceptable window for safe retries? SLA question. Who is responsible for generating the key, and what happens when they don't? API contract question. What does the user experience when a duplicate key arrives? Product question. The counterargument — that requiring PMs to reason about idempotency implementation detail overloads the PM role — is a reasonable concern about depth, not direction. The correct scope: PMs must specify the observable behavior ("retrying this operation within 48 hours must produce the same result as the first call"), not the implementation. Leaving that behavior unspecified and hoping engineers default to correctness is how production double-charges happen.

**AI agents and the idempotency contract.** In 2024–2025, AI agents — LLM-powered systems executing sequences of API calls — became a meaningful source of payment and provisioning traffic in products with automated workflows. The problem: AI agents don't maintain idempotency keys across reasoning steps the way a stateful client does. When an agent retries a failed tool call, it reconstructs the request from scratch — often generating a new idempotency key in the process, because the key wasn't part of the agent's persistent context. The standard assumption — "the same client reuses the same key on retry" — breaks when the "client" is an LLM that reconstitutes context from a conversation history rather than from a deterministic state machine. The blast radius scales with automation: an AI agent running an automated procurement or subscription workflow can execute dozens of payment operations before a human reviews. Teams building AI-powered checkout, automated renewal, or agent-driven account management cannot assume standard client-side idempotency behavior. The right solution — treating the agent's session as the idempotency unit rather than the individual request, and pre-allocating idempotency keys at session initialization — requires backend changes most payment APIs were not designed to support. This is an open problem in production at scale.

**Distributed idempotency across microservices.** In a monolith, one Redis instance and one check covers the full operation. In a microservices architecture, one user-facing operation spans five services — payment, access provisioning, notification, CRM update, analytics. Each service owns its own idempotency guard. Each is implemented differently, with different key scopes, different windows, different failure modes. The result is not end-to-end idempotency — it is a chain of independently idempotent services with unguarded gaps at the handoffs. The architectural debate: should idempotency be a platform concern (a shared idempotency service all operations route through, enforcing consistent keys and windows) or an application concern (each service team implements it according to shared guidelines)? The platform approach creates a single point of failure and a political fight over ownership. The per-service approach creates inconsistent guarantees that fail at the exact moments when the guarantees matter most. Most companies end up with the per-service approach by default, discover the gaps in postmortems, and retrofit platform-level solutions. The PM who understands this tradeoff can advocate for a platform-level investment before the distributed inconsistency shows up as a customer-facing incident. That advocacy is more valuable before the microservices proliferate than after.

## Prerequisites

→ What is an API (01.01) — understand API calls as the unit of operation before studying their properties
→ API Authentication (01.02) — idempotency keys and auth tokens are different mechanisms; know both before the distinction matters in a design review

## Related lessons

→ Webhooks vs Polling (01.03) — webhooks create idempotency requirements; these two concepts compound directly
→ Rate Limiting & Throttling (01.04) — rate limiting and idempotency solve adjacent problems; design them together
→ Error Codes & Response Design (01.09) — the response to a duplicate key (200 vs 409) is a product decision
→ API Versioning (01.06) — adding idempotency to an existing API is a breaking change; version it carefully
