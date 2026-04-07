---
lesson: Third-Party Integration Patterns
module: 01 — APIs and Integration
tags: tech
difficulty: working
prereqs:
  - 01.01 — What is an API: third-party integrations are built on top of vendor APIs
  - 01.03 — Webhooks vs Polling: webhook integration is one of the three main third-party patterns
  - 01.09 — Error Codes & Response Design: vendor error responses need to be handled differently from internal errors
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/infrastructure/zoom-demo-class-report-1.md
  - technical-architecture/infrastructure/whatsapp-customer-support.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-07
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The morning 500 classes broke

**Timeline: 9:04 AM Monday**
- 500 demo classes scheduled to start in 56 minutes
- Teachers clicking "start class" → nothing happening
- **Root cause:** Zoom partial outage in Asia-Pacific region; meeting creation API failing

---

### What happened

Every teacher attempt to generate a class link triggered this sequence:

1. Class service calls Zoom API
2. Zoom returns error
3. System has no fallback logic
4. Class fails to launch

---

### The escalation

**PM's question to engineering:** "Can we switch to Google Meet for the next hour?"

**Engineer's answer:** No.

> **Why:** The `vendor_meeting_id` from Zoom's API is the database identifier for the entire class system. Student joining links, teacher joining links, and attendance tracking all reference this Zoom meeting ID. No substitution possible without rewriting the class system.

---

### Impact

| Metric | Result |
|--------|--------|
| Classes cancelled | 2 hours |
| Families impacted | 437 |
| Communication | Apology email sent |

---

### The design flaw

**Six months earlier:** PM approved Zoom integration spec

**Question nobody asked:** "What happens when Zoom goes down?"

⚠️ **Critical gap:** No contingency planning for external vendor outages during specification review

## F2. What it is — the subcontractor problem

> **Third-party integration:** When your product depends on another company's software to deliver part of its functionality.

**Real examples:**
- Checkout → Stripe
- Video calls → Zoom
- SMS reminders → Twilio
- WhatsApp support → Kaleyra

### The subcontractor analogy

A resilient builder doesn't hire one electrician with no backup plan. They:
- Designate a primary contractor
- Keep a backup on speed dial
- Ensure work can be continued by any qualified professional

Third-party integrations work the same way. When you couple your product directly to a single vendor with no fallback, you've inherited their reliability as your own. **When they have an outage, you have an outage.**

### Key terms

> **SDK (Software Development Kit):** A library the vendor provides for your programming language. Instead of writing raw HTTP calls to their API, you install their package and call their functions.
>
> **Trade-off:** Faster to build with, but you're now dependent on the vendor maintaining that library.

> **Fallback:** What your system does when the vendor is unavailable.
>
> **Without a fallback:** Unavailable vendor = broken feature
>
> **With a fallback:** System either routes to an alternative, degrades gracefully, or queues work for vendor recovery

> **Vendor coupling:** How tightly your code depends on a specific vendor's implementation.
>
> **High coupling:** Switching vendors requires rewriting code
>
> **Low coupling:** Vendor change is mostly configuration

## F3. When you'll encounter this as a PM

### Scenario: Evaluating a new tool

The sales pitch from any vendor focuses on what works. The PM's job is to ask what breaks.

**Critical questions to ask:**
- "What's your SLA?"
- "What happens to our users when your service is down?"
- "Have you had an outage in the last 12 months?"

These questions belong in the vendor evaluation, not the post-incident review.

---

### Scenario: A vendor has an outage

**First question:** "Is this us or them?"

If a third-party vendor is down, immediately ask: "What does our product do until they recover?"

⚠️ **Risk:** If the answer is "nothing works," that's a design problem deferred to crisis mode.

---

### Scenario: Vendor changes their API or pricing

Vendors change pricing, deprecate API versions, and modify rate limits.

| **Integration Type** | **Impact of Vendor Change** |
|---|---|
| **Tightly coupled** | Every change = potential engineering sprint |
| **Loosely coupled** | Most changes = configuration updates |

---

### Scenario: Security team reviews a new integration

Every third-party integration is a potential attack surface.

⚠️ **Security decisions that are PM-level:**
- Vendor credential rotation schedules (API keys, OAuth tokens)
- Data access scoping to minimum required permissions
- Audit logging and access controls

---

### Scenario: Planning a vendor migration

Switching payment providers, email providers, or other vendors is a **product project** — not just engineering.

**Required components:**
- Migration plan
- Parallel-run period
- Rollback path

The ease of migration depends almost entirely on how the original integration was designed.

---

## Pre-approval checklist — before any new integration ships

Four questions that belong in vendor evaluation, not post-incident review:

| **Assessment** | **Question** | **Why it matters** |
|---|---|---|
| **Coupling** | Is vendor-specific code contained to one place, or spread throughout the codebase? What does switching cost if this vendor changes pricing or has a sustained outage? | Tight coupling = expensive migrations and risky dependencies |
| **SLA interpretation** | What does the vendor's uptime guarantee actually cover? Is compensation credits or cash? What is the user experience if they breach it during your peak traffic window? | SLA terms vary widely; some don't cover your critical moments |
| **Fallback design** | For every failure mode — outage, rate limit, deprecated API — what does the user experience? Is that outcome acceptable to the business? | Unplanned degradation = product risk |
| **Cost model** | What is the vendor's pricing at 10× current usage? Are there per-request or egress fees that change unit economics at scale? | Hidden costs emerge at scale and impact margins |

⚠️ **Acceptance criteria requirement:** If the engineer cannot answer all four before the integration ships, these are acceptance criteria items — not future tech debt.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that third-party integrations create vendor dependencies and that fallback design is a product decision.
# ═══════════════════════════════════

## W1. How third-party integrations actually work — the patterns and the tradeoffs

### Quick Reference
| Pattern | Speed | Control | Best for |
|---------|-------|---------|----------|
| Direct API | Slow | Maximum | Custom needs, rate-sensitive operations |
| SDK | Fast | Medium | Quick shipping, standard use cases |
| Webhook | N/A | Medium | Event-driven reactions, async processing |

---

### 1. The three integration patterns

Every third-party integration falls into one of three patterns — or a combination:

> **Direct API integration:** Your code calls the vendor's REST (or GraphQL) API directly over HTTP. You handle authentication, error handling, retry logic, and rate limiting yourself. Maximum flexibility, maximum responsibility.

> **SDK integration:** The vendor provides a library for your language (`npm install stripe`, `pip install twilio`). Your code calls SDK functions, and the SDK handles the HTTP calls, serialization, and some error handling internally. Faster to build, but the SDK abstracts error details and you're coupled to the vendor's library version.

> **Webhook integration:** The vendor calls your server when events happen — a payment is completed, a user replies to a WhatsApp message, a class participant joins or leaves. Your server receives the event and processes it. You don't poll; you react. Requires your server to be reachable and the vendor to reliably deliver events.

**Most production integrations combine patterns.** Stripe uses direct API calls to initiate payments and webhooks to confirm payment completion. Zoom uses direct API calls to create meetings and webhooks to track attendance.

---

### 2. What the SDK hides — and what that costs you

An SDK makes integration faster. It also removes visibility.

**The hidden cost:**
When you call `stripe.charges.create()`, the SDK is making an HTTP request to `https://api.stripe.com/v1/charges`. If the request fails, the SDK raises an exception with Stripe's error code. But the SDK might retry the request silently before raising the exception — which means your code may have made 3 API calls before you see the first error. At Stripe's rate limit of 100 requests per second, invisible retries can exhaust your quota.

**Version coupling:**
The SDK also couples you to a version. `stripe@10.x.x` and `stripe@11.x.x` may have breaking interface changes. Falling behind on SDK versions means missing security patches. Upgrading means QA cycles for every integration that uses the SDK.

**The rule:** Use the SDK for speed of initial integration, but understand what it's doing underneath — especially for error handling, retry behavior, and rate limit management.

---

### 3. Webhook reliability is not guaranteed

⚠️ **Vendors send webhooks on a best-effort basis.** Retry behavior varies significantly:

| Vendor | Retry Behavior | Risk |
|--------|---|---|
| Zoom | Retries failed webhooks; stops if you return non-200 | Event loss if endpoint returns error |
| Kaleyra | Retry behavior not documented | Event loss if endpoint is down |
| Stripe | Retries for up to 3 days with exponential backoff | Longest safety window |

**Webhook-based integrations require:**
- **Idempotency:** Your handler must safely process the same event twice without double-charging or double-creating records
- **Dead letter queue or logging:** Track events your server couldn't process
- **Reconciliation mechanism:** Periodically check the vendor's API to confirm your data matches their records

---

### 4. Vendor coupling — the spectrum from tight to loose

| Coupling Type | Definition | Trade-off |
|---|---|---|
| **Tight** | Code references vendor-specific IDs, APIs, data structures throughout codebase. Zoom integration stores `vendor_meeting_id` as primary class reference. | Faster to ship; switching providers means rewriting core systems |
| **Loose** | Code defines own interface (`MeetingProvider`, `MessagingProvider`); vendor is one implementation. | 2-3× longer to build initially; switching providers means writing new implementation only |

**When to choose loose coupling:**
- The vendor is commoditized (email, SMS, video calling)
- The category has significant price competition
- The vendor has a history of pricing changes or service disruptions
- Your product will serve multiple markets with different vendor preferences

---

### 5. Fallback design: the question that needs an answer before launch

⚠️ **Every third-party integration must have a documented answer to:** "What happens to users when this vendor is unavailable?"

| Fallback type | What it means | When to use |
|---|---|---|
| **Hard fail** | Feature breaks, user sees error | Only acceptable for non-critical features |
| **Queue and retry** | Work is saved and retried when vendor recovers | Good for async actions (emails, notifications) |
| **Graceful degradation** | Core flow continues, vendor-dependent feature is skipped | When vendor feature is enhancement, not core |
| **Alternate provider** | Request is routed to a backup vendor | For critical features where downtime is unacceptable |

**Real consequences:**
- The class video system had no fallback — hard fail in production, 437 cancelled classes
- The WhatsApp support system had no queue — if Kaleyra's webhook delivery fails, the message event is lost with no recovery mechanism

---

### 6. The abstraction layer — when it's worth the cost

> **Abstraction layer:** An interface in your code that separates your business logic from the vendor implementation

**Pattern:**
```
Business logic → [MeetingProvider interface] → ZoomMeetingProvider
                                              → GoogleMeetProvider (future)
```

Building this layer takes extra time upfront. 

**It pays off when:**
- The vendor is commoditized (email, SMS, video calling — any competent provider delivers the same service)
- The category has significant price competition (switching can save real money)
- The vendor has a history of pricing changes or service disruptions
- Your product will serve multiple markets where different vendors are preferred

**It doesn't pay off when:**
- The vendor's capability is genuinely unique (you won't switch away from Stripe's fraud detection for a generic payment abstraction)
- The integration is genuinely temporary

---

### 7. Vendor SLA and what it actually guarantees

> **SLA (Service Level Agreement):** Guarantees uptime (99.9% = 8.7 hours/year of allowed downtime) and specifies compensation if breached (usually credits, not cash, not SLA for your customers)

**What an SLA does NOT guarantee:**
- That the outage won't happen during your peak traffic window
- That their compensation will cover your business loss
- That their status page will accurately reflect the outage in real time

**Use SLAs for:** Vendor selection and risk assessment — not as a substitute for fallback design.

## W2. The decisions third-party integrations force

### Decision 1: SDK or direct API integration?

| | SDK | Direct API |
|---|---|---|
| Best for | Fast initial integration, standardized operations | Custom error handling, non-standard flows, high-volume with rate limit control |
| Speed to ship | Fast — vendor handles boilerplate | Slower — you write HTTP client code |
| Error visibility | Low — SDK abstracts retries and failures | High — you see every request and response |
| Version lock risk | High — SDK upgrades may break integration | Low — you control how you call the API |
| **Default** | **Use SDK to ship fast; audit retry and error behavior before going to production** | Use for integrations where you need full control of the HTTP layer |

> **SDK or direct API?** Use the SDK for speed, but require your engineer to audit whether silent retries affect your rate limit budget before launch.

---

### Decision 2: Tight coupling or abstraction layer?

| | Tight coupling | Abstraction layer |
|---|---|---|
| Best for | Truly unique vendor capability; prototypes; temporary integrations | Commoditized services (email, SMS, video, storage); vendor-switching likely |
| Build time | Fast | 2–3× longer upfront |
| Switching cost | High — rewrite required | Low — new implementation of existing interface |
| Maintenance | Simple — one codebase | Two layers to maintain (interface + implementation) |
| **Default** | **Use tight coupling when you're confident the vendor is the right long-term choice** | Use abstraction when the vendor category is competitive or history suggests switching |

> **Tight coupling vs. abstraction:** For payments, messaging, and video — categories where multiple vendors are roughly equivalent — build the abstraction. For integrations where the vendor's unique capability is the reason you chose them, tight coupling is acceptable.

---

### Decision 3: Synchronous or queue-based integration?

| | Synchronous (direct call in request path) | Queue-based (async, via message queue) |
|---|---|---|
| Best for | Actions where the user waits for the result (payment confirmation) | Notifications, emails, background tasks — user doesn't wait |
| Vendor outage impact | User-facing error if vendor is down | Messages queue up; processed when vendor recovers |
| Latency | Adds vendor's response time to your API response time | No impact on request latency |
| Complexity | Simple — call vendor, handle response | Higher — needs queue infrastructure and dead letter handling |
| **Default** | **Use for transactional, user-blocking operations only** | **Use for all notifications, communications, and background actions** |

⚠️ **Reliability risk:** Synchronous calls to third-party vendors in the critical path create user-facing failures whenever the vendor is down. If a user doesn't need to see the result before clicking "next," the call should be async and queue-based.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **If this vendor is unavailable for two hours, what happens to users who hit this feature?** | Whether there's a documented fallback. If the answer is "the feature breaks," ask what the fallback plan is. If the answer is "there isn't one," that's a product decision deferred to the incident response team. Make it explicit: does the business accept that risk, or should fallback be in scope? |
| **Are we using their SDK or calling their API directly — and do we know what the SDK does when it fails?** | Whether the team understands the retry and error behavior of the integration. Invisible SDK retries can exhaust rate limits. SDK exceptions may mask the specific error code the vendor returned. If the engineer hasn't reviewed the SDK's error handling, the integration's failure modes are unknown. |
| **Are we calling the vendor synchronously in the request path, or asynchronously via a queue?** | Whether vendor latency and outages affect user-facing response times. A synchronous call to Kaleyra in the WhatsApp send-message flow means every outbound support reply waits for Kaleyra to respond. If Kaleyra is slow or down, the ops agent's action fails. A queue-based send means the message is buffered and sent when Kaleyra recovers. |
| **What happens if the vendor's webhook delivery fails — is that event permanently lost?** | Whether webhook-based integrations have reliability guarantees. The WhatsApp support system has no documented dead letter queue for failed Kaleyra webhook deliveries — a missed event means a missed customer message with no recovery path. The Zoom attendance system depends on webhook events for duration tracking — missed events mean inaccurate attendance records. |
| **Do we have a vendor-agnostic interface, or is vendor-specific code throughout the codebase?** | The switching cost if the vendor relationship ends or pricing changes. If `zoom.meeting.create()` is called in 14 different places across 5 services, a vendor switch is a 14-location code change. If it's behind a `MeetingProvider` interface, it's one implementation file. |
| **What's our credential rotation plan for this vendor's API key?** | Whether the integration has been designed for security operations. An API key that was set up 18 months ago and never rotated is a security liability. Rotation should be possible without downtime — which requires the key to be stored in a secrets manager, not hardcoded, and the rotation process to be tested. |
| **What does the vendor's rate limit look like, and what's our current headroom?** | Whether the integration will scale. Kaleyra's outbound WhatsApp rate limits apply per phone number. If the support team sends 100 messages per hour and the limit is 80, the integration is already over quota. Discovering this in production — when ops replies start failing silently — is avoidable with a capacity review before launch. |

## W4. Real product examples

---

### Zoom — Tight coupling with no fallback

**What:** Built the class delivery system with Zoom as the video provider. The `vendor_meeting_id` from Zoom's API is stored as the primary identifier for every class. Teacher join links, student join links, attendance tracking, and class monitoring all reference this ID.

**Why it failed:** When Zoom experienced a regional outage, the meeting creation API failed. With no abstraction layer and no fallback provider, every class that needed a new meeting link was blocked. The system had no way to substitute Google Meet or any other provider — the Zoom meeting ID *was* the class, not a reference to a class.

**Takeaway:** For any integration where the vendor delivers a core user-facing action (class delivery, payment processing, authentication), ask before launch: **"If this vendor is down for two hours during peak usage, what does the user experience?"** If the answer is "complete failure," fallback design is not optional.

---

### Kaleyra — No queue, no error handling, no recovery

**What:** Built WhatsApp customer support via Kaleyra webhook integration. Incoming WhatsApp messages trigger Kaleyra webhooks that write to a `whatsapp_data` table. Outbound messages call Kaleyra's API directly in the request path. No queue, no retry, no dead letter mechanism documented.

**Why it failed (and will fail again):** 
- Kaleyra's webhook retry behavior is undocumented
- If the webhook endpoint is down or slow when Kaleyra fires, the message event may be lost permanently
- No queue to catch it, no reconciliation to detect it
- Outbound messages sent synchronously means any Kaleyra latency or outage fails the ops agent's reply action immediately
- Missing queue is unscheduled tech debt

⚠️ **Risk:** Message loss in production with no detection mechanism

**Takeaway:** For every webhook-based integration, require two things before launch:
1. Documented retry/dead letter behavior for webhook delivery failures
2. A queue for outbound vendor calls

Both are weeks of work to add later and hours to include upfront.

---

### Stripe — Abstraction that enables vendor optionality

**What:** Stripe built their own abstraction across payment networks (Visa, Mastercard, American Express, bank transfers) so that a product integrating Stripe gets a single API regardless of payment method. Teams then build their own payment abstraction (`PaymentProvider` interface) to route to Stripe, Braintree, or Adyen by changing configuration rather than code.

**Why it worked:** 
- Mature payment stacks at Shopify, Airbnb, and Uber route different payment methods/geographies to different processors behind a single interface
- When Stripe increased pricing, teams could evaluate alternatives without codebase rewrite
- Adding new markets required a local processor — the new processor was a new implementation of the existing interface

**Takeaway:** The abstraction investment pays off when the vendor category has multiple equivalent providers and real pricing competition. Payment processing, email delivery, SMS, and video conferencing are categories where this investment is almost always justified within 2 years.

---

### Twilio — The vendor that abstracts another vendor

**What:** Twilio's core product is itself an abstraction layer — it sits between your code and dozens of telecom carriers globally. When you send an SMS via Twilio, Twilio routes to the best available carrier for that destination number, handles carrier-specific formatting requirements, and retries on carrier failure.

**Why it matters:**
- Twilio is the fallback infrastructure for its own integrations
- When AT&T has a delivery issue, Twilio routes to Verizon
- When a carrier in Singapore blocks a number, Twilio switches
- The PM integrating Twilio doesn't need to know any of this — the fallback is the product
- This is the payoff of abstraction at the vendor layer: your product inherits Twilio's reliability investment without building it yourself

**Takeaway:** When evaluating communication vendors (SMS, WhatsApp, email), ask: **Does the vendor itself have redundancy across underlying carriers or infrastructure?** A vendor that's a single-carrier wrapper is just as brittle as building the carrier integration directly. A vendor that abstracts multiple underlying providers is buying you resilience you don't have to build.

---

### Gong.io — Multi-tenant credential isolation in enterprise B2B integrations

**What:** Gong integrates with each enterprise customer's Salesforce CRM via OAuth 2.0. Each customer authorizes Gong to access their Salesforce instance; Gong stores per-tenant OAuth tokens in isolated credential stores. Customer A's Salesforce credentials never interact with Customer B's data pipeline. Every API call is scoped to a single tenant's authorized token and logged with tenant ID, timestamp, and action.

**Why it worked:**
- Enterprise customers (especially financial services and healthcare) run security reviews before approving CRM integrations
- Standard checklist: credential isolation, data residency, audit trail
- Gong's per-tenant isolation design passes reviews without custom engineering per deal
- Teams that built multi-tenant integrations with shared API key per vendor fail enterprise security reviews and require architectural rework

⚠️ **Risk:** Shared API key per vendor fails enterprise security reviews. Retrofit to per-tenant isolation is 4–6 week project under deal-closing pressure.

| Approach | Enterprise Security Review | Timeline to Fix |
|---|---|---|
| Shared API key per vendor | ❌ Fails | 4–6 weeks (under pressure) |
| Per-tenant credential isolation | ✅ Passes | Included upfront (hours) |

**Takeaway:** For enterprise B2B, multi-tenant credential isolation is a **qualification requirement, not a feature**. Add "per-tenant credential isolation" to your integration acceptance criteria before you have enterprise customers, not after.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands the three integration patterns, fallback design, and the coupling-vs-abstraction tradeoff.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Pattern 1: Tight vendor coupling disguised as "we'll refactor later"

**The scenario:**
The Zoom `vendor_meeting_id` wasn't designed with the assumption that Zoom would be permanent. An engineer intended to add an abstraction layer "when we have time," deferring the fallback design to "after we ship."

**What happened:**
- Two years later: 40,000 classes processed per month
- Refactor estimate: 12 engineering weeks
- Root cause: 11 services reference `vendor_meeting_id` directly; every integration test assumes Zoom's format
- The cost: 12 weeks engineering + 4 weeks regression testing

**Why it compounds:**
An abstraction that would have taken 3 extra days in the original sprint now costs 16 weeks total. Deferred coupling debt spreads across services faster than other tech debt.

**PM prevention checklist:**
- [ ] For any commoditized vendor integration, make the abstraction layer a **launch requirement**, not a post-ship refactor
- [ ] Add to acceptance criteria: *"The vendor should be replaceable by a config change, not a code change"*
- [ ] This single criterion prevents months of future rework

---

### Pattern 2: Webhook integrations without idempotency handlers

**The scenario:**
The demo class attendance system receives Zoom `participant_joined` webhooks. Zoom occasionally delivers the same webhook event twice (documented behavior, not a bug).

**What went wrong:**
| Scale | Impact |
|-------|--------|
| 50 classes/day | Manageable with manual cleanup |
| 5,000 classes/day | Duplicates corrupt analytics, trigger incorrect billing, generate false CRM signals |

**Timeline:**
- Day 1: Bug existed (invisible at small scale)
- Day 730: Data team discovered attendance dataset was unreliable

**PM prevention checklist:**
- [ ] Require idempotency as an acceptance criterion for **every webhook handler**
- [ ] QA test: *"If we deliver the same webhook event twice, does our system process it twice or once?"*
  - If twice → correctness bug exists
  - If once → idempotency implemented
- [ ] Add this test to the QA checklist, not the post-incident review

---

### Pattern 3: Vendor credentials that never rotate

⚠️ **Security risk**

**The scenario:**
An API key stored in a config file, committed to git 18 months ago, never rotated.

**Exposure surface:**
- Every engineer who touched that service
- Every CI/CD system that ran that config
- Every security scanner that audited the repository

**Why delay matters:**
Most production API key compromises involve keys leaked months *before* they were exploited. Attackers wait until they know exactly how to use them. **Rotation forces a new key into production, invalidating any compromised copy.**

**PM prevention checklist:**
- [ ] Include vendor credential rotation in integration acceptance criteria
- [ ] Revisit rotation requirements in quarterly security reviews
- [ ] Operational question: *"Can we rotate this key without downtime?"*
  - If answer requires a deployment → key isn't stored correctly
  - If answer is a 10-minute process → integration was designed well

## S2. How this connects to the bigger system

| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| **Webhooks vs. Polling** | Vendor delivers events; you process them. Retry behavior, delivery guarantees, and deduplication vary by vendor. | Reliability is almost never tested before production. Understanding webhook delivery semantics before vendor signup is a product requirement, not an engineering detail. |
| **API Authentication** | Vendor API keys are external auth credentials with same security requirements as internal tokens. | Keys need scoped permissions, rotation schedules, secrets manager storage (not env files/git), and monitoring for unusual usage patterns indicating compromise. |
| **Rate Limiting** | Vendor rate limits apply to *your calls to their API*, not user calls to yours. Shared quota across entire system. | A background job calling Kaleyra for bulk WhatsApp shares the same limit as synchronous sends from ops dashboard. Background jobs can exhaust quota, breaking user-facing integration with no obvious cause-and-effect. |
| **API Versioning** | Vendor deprecations create forced migrations with fixed deadlines you didn't set. | Integrations tightly coupled to specific vendor API versions require refactoring production code under external time pressure. Abstraction layers absorb version changes in one file. |

## S3. What senior PMs debate

### Build vs. buy at the infrastructure layer

**The core question:** At what scale does a commodity third-party service become worth building in-house?

| Factor | Build In-House | Buy Third-Party |
|--------|-----------------|-----------------|
| **Cost visibility** | Distributed, invisible on P&L | Explicit line item |
| **When it makes sense** | Strategically differentiating; vendor lock-in risk; material P&L impact at your scale | Fast time-to-market; commodity capability; operational overhead unacceptable |
| **Hidden cost** | Engineering maintenance burden consistently undercounted | Often overcounted by teams |
| **Outcome** | Premature builds → high-maintenance internal systems | Optionality without operational cost |

**The honest calculus most senior PMs reach:**

Build in-house **only when**:
- The vendor's capability is **strategically differentiating** to your product
- Vendor lock-in creates **genuine business risk**
- Vendor pricing at your scale is a **material P&L issue**

For everything else: the abstraction layer buys optionality.

**Real-world examples:**
- Twilio (SMS), Zoom (video), Stripe (payments) — most teams should buy, not build

---

### Tight coupling: a choice, not a shortcut

> **Tight coupling:** Direct, unabstracted dependency on a third-party service (e.g., calling `zoom.createMeeting()` directly throughout your codebase).

**The conventional framing:** Tight coupling is a shortcut made under deadline pressure.

**The honest framing:** Tight coupling is often a deliberate choice by engineers to avoid abstraction overhead.

| Dimension | Tight Coupling | Abstracted Layer |
|-----------|----------------|------------------|
| **Simplicity for new engineers** | High — just call the vendor API | Lower — must understand interface contract + routing logic |
| **Testing complexity** | Lower initially | Higher |
| **Documentation burden** | Lower | Higher |
| **Onboarding friction** | Lower | Higher |
| **Resilience at scale** | Fails hard when vendor changes | Survives vendor changes |

**The real tradeoff:** Who bears the complexity cost?
- **Abstraction:** Engineers who build today
- **Tight coupling:** Engineers and users who inherit failures at scale

⚠️ **Senior PM responsibility:** Make this tradeoff explicit. Don't leave it to the engineer under deadline pressure to decide.

---

### LLM API vendors: the new infrastructure debate

**Current state (2024-2025):** Every product team integrating LLM APIs faces the same questions payment teams worked through a decade ago.

**Arguments for abstraction layer:**

| Reason | Risk |
|--------|------|
| LLM pricing is volatile | GPT-4 pricing changed multiple times |
| Model quality evolves rapidly | Best model in 6 months may not be today's choice |
| Vendor concentration risk | Single provider controls your AI capability |

**Arguments against abstraction layer:**

| Reason | Impact |
|--------|--------|
| LLM capabilities are NOT commoditized | Output quality varies significantly by provider/model for specific tasks |
| Differs from SMS delivery | Carrier irrelevance ≠ model irrelevance |

**Current industry consensus (with caveats):**

✓ **DO abstract at the prompt/task level**
- Define *what the AI should do*, not *which model does it*

✗ **DON'T abstract at the infrastructure level**
- Use the provider's SDK directly
- Accept the coupling

⚠️ **This may not be correct in 2 years** as model commoditization accelerates. Teams building AI products in production today are making a bet on the status quo.