---
lesson: API Versioning
module: 01 — APIs & System Integration
tags: tech
difficulty: foundation
prereqs:
  - 01.01 — What is an API — a version is a way to manage the API contract over time
  - 01.02 — API Authentication — auth schemes can themselves change between versions
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-student-get.md
  - technical-architecture/api-specifications/api-student-details-get.md
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
# Assumes: 01.01 What is an API. You know what an API call is and what a "contract" means.
# ═══════════════════════════════════

## F1. The world before this existed

The mobile app had been in production for six months. 80,000 students had profiles. Everything worked.

Then the engineering team cleaned up their API. The backend response had been returning a field called `name` — which they'd always found ambiguous. First name? Full name? Display name? During a refactor, they standardised everything. The field became `fullName`. It was a one-line change. It made the codebase cleaner. It made sense to everyone on the team.

They shipped it on a Thursday afternoon.

By Friday morning, the support queue had 200 tickets. Every student profile in the mobile app was blank. No name, no display, just empty fields everywhere the name should be.

Here is what had happened. The mobile app's code was written six months earlier. It asked the API for `name`. The API no longer sent `name` — it sent `fullName`. The app didn't know what `fullName` was, so it showed nothing. The app hadn't changed. The API had. And no one had versioned the change.

The engineering team had to roll back the rename, ship a hotfix, and lose two days they'd planned to spend on new features. The product manager wrote up an incident report. The root cause was three words: *no versioning strategy.*

Renaming a field is a breaking change. So is removing a field. So is changing what a field contains. The problem isn't that APIs change — they have to, as products evolve. The problem is changing them in ways that break the clients who depend on them, without giving those clients time to adapt.

API versioning is the system that lets you evolve your API without breaking clients that depend on the current version.

## F2. What it is — definition and core split

**API versioning** means publishing your API under a version identifier — most commonly `/v1/` or `/v2/` in the URL path — so that when you need to make an incompatible change, you can create a new version (`/v2/`) while clients on the old version (`/v1/`) keep working until they're ready to migrate.

The core skill for a PM is understanding the difference between two types of changes:

**Non-breaking changes** — safe to add to the current version, no clients break:
- Adding a new optional field to a response
- Adding a new endpoint
- Adding an optional query parameter
- Fixing a bug in the existing behaviour (usually)

**Breaking changes** — require a new version, because existing clients will fail:
- Removing a field
- Renaming a field (`name` → `fullName`)
- Changing a field's data type (string to integer)
- Making an optional field required
- Removing an endpoint
- Changing an error code or error format

The mistake teams make is treating the first category casually and not recognising when a "small cleanup" is actually the second category. The rename above was a breaking change wearing the clothes of a refactor.

## F3. The analogy that makes it click

Think about textbook editions. When an author makes substantial updates — new chapters, reorganised content, different exercises — they release a 2nd edition with a new ISBN. Schools can keep teaching from the 1st edition while new students get the 2nd. Both editions co-exist in the world simultaneously.

The version number is the ISBN. The API contract is the content. When the content changes in a way that would break how students were using the 1st edition, you issue a new edition. You don't reach back into the 1st edition and change it once it's been published.

Most teams put the version directly in the URL, the same way an ISBN appears on the book:

- `GET /v1/student` — version 1 of the student lookup API
- `GET /v2/student` — version 2, with breaking changes, running alongside v1

You can test both versions in a browser. You can paste either URL in a Slack message. You can see it in your logs. The version is visible everywhere, which is why URL versioning is the default approach for most teams.

## F3. When you'll encounter this as a PM

**When your team ships a "cleanup" that's actually a breaking change.** Engineers often don't notice the boundary. "We're just renaming this field" feels trivial internally. From the outside, it breaks every client using that field. Your job is to ask: "Who depends on this response today, and what happens to them when this changes?"

**When you're integrating with a third-party API.** Check which version you're calling. If you call `/v1/` and the vendor sunset v1 six months ago without telling you, you'll get failures with no warning. Pin to a specific version in your integration and monitor for deprecation notices.

**When a security issue requires a fix that breaks backwards compatibility.** This is the worst case. The secure fix requires a breaking change. You can't silently apply it — that breaks clients. You have to version it and run an insecure v1 alongside a secure v2 during the migration window. How long that window lasts is a product and risk decision, not just an engineering one.

**When your product offers a public API.** If developers build on your API, every breaking change you ship without versioning destroys developer trust. The teams that have the best developer relationships (Stripe, Twilio, Shopify) treat versioning as a commitment, not an afterthought.


# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PM, consumer startup PM, B2B enterprise PM, 2+ years experience
# Assumes: Foundation. You understand what a breaking change is and why versions exist.
# ═══════════════════════════════════

## W1. How it works — mechanics and deprecation lifecycle

**Three versioning approaches**

URL path versioning is the default. The version number lives in the URL path:

```
GET /v1/student
GET /v2/student
```

Visible in logs, testable in a browser, easy to route at the infrastructure layer. Most teams start and stay here.

Header versioning puts the version in a request header instead:

```
GET /student
API-Version: 2024-01-01
```

Stripe uses this approach — each API key is pinned to a specific version date. Elegant architecture, but invisible in URLs, harder to test without tooling, easier to forget in client code. Suitable for teams with a dedicated API platform function that can enforce consistency.

Query parameter versioning:

```
GET /student?version=2
```

Least common. Works, but messy. Versions get mixed with functional query parameters. Avoid unless you're retrofitting an API that didn't originally plan for versioning.

Default recommendation: URL path versioning. Pick it at the start and stay consistent. The wrong choice is mixing approaches — some endpoints on path, some on headers.

**The deprecation lifecycle**

Versioning is not just about launching v2. It's about running v1 and v2 simultaneously through a defined deprecation window and then removing v1 cleanly.

The lifecycle:

1. **Design v2** with the breaking change. Ship it alongside v1 — both endpoints live.
2. **Announce deprecation** of v1 with a specific sunset date. Document what changed and what clients need to do. Publish a migration guide.
3. **Add deprecation warnings** to v1 responses — a `Deprecation` header with the sunset date, so clients who read headers see the warning even if they missed the announcement.
4. **Support the migration** — don't just announce and disappear. Build migration tooling if the change is complex. Run office hours for external developers if you have them.
5. **Sunset v1** on the announced date. Remove the code. Not "start sending 410 Gone" — actually remove it so the codebase doesn't carry dead weight forever.

Minimum sunset timeline: 6 months for external/public APIs. 3 months for internal APIs where you control all the clients. Shorter timelines create emergencies. Longer timelines mean you're maintaining two codebases indefinitely.

**KB grounding: a real versioning decision**

The student lookup API in production uses `/v1/` path versioning — `GET /v1/student` and `GET /v1/student/details`. That's the versioning strategy working as designed.

The `/v1/student/details` endpoint has a documented High-priority security issue: sensitive parent data (email address, phone number) is returned in the default response. The only protection is an opt-in masking flag — `isFe=true` in the query — which frontends are supposed to use to strip the sensitive fields.

The proper fix is to make masked data the default, with an explicit opt-in to receive it for authorised internal use. But removing fields from the default response is a breaking change. Any client that currently depends on receiving those fields without the flag will break.

The `isFe=true` pattern is the team deferring that breaking change. It's a reasonable short-term workaround. But the version cost is accumulating. Until they ship `/v2/student/details` with safe defaults, they're running a v1 endpoint with a known security gap — and the reason it hasn't been fixed is that fixing it properly requires going through the versioning process.

There's a second issue on the same endpoint: the API returns `success: false` with an HTTP 200 status for records not found. Semantically wrong — a 404 should be used — but fixing it to return 404 is also a breaking change. Any client that checks the `success` field instead of the HTTP status would silently break. One small inconsistency, documented as Low-priority, sitting in v1 until someone decides the migration cost is worth paying.

This is what API versioning decisions look like in production. Not abstract. Real debt, real cost, real tradeoff.

## W2. Tradeoffs — with recommendations

**URL versioning vs header versioning**

URL versioning is visible, testable, and proxy-friendly. Header versioning is architecturally cleaner and supports more granular pinning (Stripe's date-based approach lets clients get non-breaking improvements without migrating).

Default to URL versioning unless you have an API platform team that can enforce header-based consistency across all services. Header versioning's invisibility becomes a liability when engineers forget to add the version header in new client code.

**How long to run old versions**

Shorter windows (30–60 days) move faster but create emergencies for clients who need time to migrate. Longer windows (12+ months) are safe for clients but mean you're running and testing two codebases indefinitely.

Default: 6 months for external APIs, 3 months for internal. Shorten internal timelines only when you can enumerate and directly contact every client. Never shorten external timelines — you can't know all your clients.

**Version the whole API vs version individual endpoints**

Some teams version selectively: `/v2/payment` but still `/v1/student`. This feels economical but creates a version matrix that nobody can track. Which client is on v1 for payments but v2 for users? What combinations are supported?

Default to versioning the whole API together. One version number, one migration event, one sunset date. The overhead of whole-API versioning pays off in clarity.

**Additive-only policy (strong default)**

The lowest-cost versioning discipline: commit to never removing or renaming anything in a published version. Only add. If you need to remove something, do it in a new version. This means v1 accumulates some cruft over time — but clients on v1 never break unexpectedly.

This is how Stripe operates. They've maintained decades of API versions without breaking changes within a version. The cost is that old versions have some inconsistencies. The benefit is that developers trust the contract.

## W3. Questions to ask your engineer

**"What's our current versioning strategy — URL path, header, or query param?"** *(this reveals: whether there's a consistent approach or ad hoc variation per endpoint, and whether anyone actually owns this decision)*

**"What's your definition of a breaking change? Where is that documented?"** *(this reveals: whether the team has shared alignment — engineers often disagree on what counts as breaking, and that disagreement causes incidents)*

**"How long do we support old versions? Who decides the sunset date?"** *(this reveals: whether you have a formal deprecation process or just let old versions accumulate until someone notices)*

**"How do we communicate deprecations to external clients — response headers, email, docs?"** *(this reveals: whether clients get advance warning through multiple channels or just find out when things break)*

**"If we needed to fix a security issue that requires a breaking change, how long would migration take?"** *(this reveals: your actual risk surface — a 12-month migration means a 12-month window for a known vulnerability to stay in production)*

**"Are there any endpoints right now that technically need a v2 for a known issue but haven't been versioned yet?"** *(this reveals: whether technical debt is accumulating behind backwards compatibility — the `isFe=true` security issue is exactly this kind of deferred breaking change)*

**"How do we test that v1 still works when we ship v2?"** *(this reveals: whether there's regression testing for old versions or whether it's manual and best-effort — the thing that breaks when this doesn't exist is the assumption that v1 is stable)*

## W4. Real companies

**Stripe** uses date-based header versioning (`2023-10-16`). Each API key is pinned to the version it was created on. Stripe maintains versions going back to 2011 — roughly 7 years of backwards compatibility. Their changelog explicitly marks breaking vs non-breaking changes for every version. They invest heavily in migration guides and version-upgrade tooling. Result: Stripe's developer trust scores consistently among the highest of any API platform.

**Twilio** uses URL path versioning with date-based version strings embedded in the path — the base URL for their SMS API looks like `/2010-04-01/Accounts/{AccountSid}/Messages`. Unusual format but the same principle: the version is visible, pinned, and running alongside newer versions.

**Shopify** uses date-based URL versioning for their Admin API — `api.myshopify.com/admin/api/2024-01/{resource}`. They release new versions quarterly and maintain a 12-month support window before sunset. App developers in the Shopify ecosystem know exactly when they need to migrate and can plan accordingly.

**The student API (KB):** Path versioning at `/v1/` for both endpoints — a clean implementation of the simplest approach. The debt: two documented issues (`isFe=true` security hack, `success: false` on 200 for not-found) that both require a breaking change to fix properly. Neither has been versioned yet. Classic example of versioning debt: the right fix exists, the cost is migration, and the team is deferring it.


# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineer PM, senior PM, AI-native PM, technical leads moving into product
# Assumes: Working Knowledge. You understand the deprecation lifecycle and can identify breaking changes.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

**The forever-v1 trap**

The team ships v2. They announce v1 deprecation with a sunset date of six months out. Six months pass. One major client hasn't migrated. The sunset date slips to three more months. Those three months pass. Two more clients. Another extension.

Two years later, v1 is still running. It has had five sunset date extensions. The team maintains two implementations of every endpoint. Every new feature must be shipped to both versions. Engineers budget time for this. It compounds.

The root cause is never purely technical. It's that the PM didn't audit client migration status at the three-month mark. Migration happened for clients who were watching. Clients who weren't watching didn't migrate. The announcement was sent once. Nobody followed up.

Prevention: treat API migration like a product launch with a customer success motion. Know every client on v1 by name. Contact them individually at the midpoint. Make migration the path of least resistance with tooling and clear guides. And hold the sunset date — slipping it once teaches clients that sunset dates are suggestions.

**The silent breaking change**

An engineer makes a change they consider minor. The `GET /v1/student` endpoint was returning `success: false` with HTTP 200 for not-found records — inconsistent, but that was how v1 worked. Someone "fixes" it during a bug sweep to return HTTP 404. Makes sense semantically. Ships without a version bump.

Every client that checked `success: false` to detect not-found behaviour now gets a 404 and potentially crashes, because their error handler didn't expect 404 from this endpoint. They depended on the documented inconsistency. That inconsistency was part of the contract.

Breaking changes that masquerade as bug fixes are the most dangerous category. There is no malice. Just the assumption that "this was wrong before, clients shouldn't have relied on it." Clients did rely on it. They always do.

Mitigation: code review for API changes should explicitly ask "does this change the behaviour any existing client could depend on?" The answer is "I don't know" often enough that the default should be version-bump unless you can prove no client depends on the old behaviour.

**The mass migration failure**

The team ships v2 with genuine improvements — better security, cleaner response format, lower latency. They announce a 30-day migration window because the engineering team is confident v2 is ready and they want to move fast.

Internal services migrate in a week. The team celebrates. Three days before sunset, the first external developer integration files a support ticket: they hadn't seen the announcement. A week after sunset, a B2B enterprise partner escalates to the CEO: their integration broke during a board demo.

The 30-day window was designed for an engineering team context. External developers have day jobs, release cycles, and approval processes. 30 days is not enough. The escalation cost more than three additional months of running both versions would have.

Rule of thumb: the migration timeline should be set by the slowest client you have, not the fastest. If your slowest client needs 6 months, that's your minimum. You can set incentives to speed up faster clients, but the sunset date anchors to the laggards.

**API-versioning theater**

The version number exists in the URL. Breaking changes still happen in v1. The team just quietly ships behavioural changes, response format changes, or field renames without incrementing the version — because "it's not really breaking, it's just a fix."

Clients who were stable on v1 start experiencing intermittent failures they can't explain. They check the changelog: nothing there. They file a support ticket. The API is technically on the same version it always was.

This is the most trust-destroying failure. Versioning theater maintains the appearance of a stable contract while violating it in practice. The only mitigation is a documented, enforced definition of breaking change — and a process that routes any API change with behavioural impact through a version review before it ships.

## S2. How this connects to the rest of your work

**01.01 — What is an API**: The API contract is what clients depend on. Versioning is how you manage that contract over time — it's the change management layer on top of the contract. Every breaking change is a contract renegotiation, and versioning is how you make that renegotiation orderly rather than chaotic.

**01.02 — API Authentication**: Authentication schemes can change between versions. OAuth scopes for v2 may be more granular than v1. API key formats may change. A client on v1 that needs to migrate to v2 is migrating both the data contract and the authentication contract simultaneously. This doubles the migration surface. Plan for it in your migration guide.

**01.03 — Webhooks vs Polling**: Webhook payloads are API contracts. A webhook that fires on payment completion sends a payload with specific fields — and if you rename a field in that payload without versioning it, every integration listening to that webhook breaks silently. Webhook versioning is often forgotten because webhook consumers are passive. They don't request data; data arrives at them. They're the hardest clients to find and notify during a migration.

**01.04 — Rate Limiting**: Version-specific rate limits are a migration incentive. You can offer higher rate limits on v2 than v1 — a tangible performance benefit for migrating. This converts "migration is work with no benefit to me" into "migration gets us better throughput." Small but sometimes the nudge that unsticks a slow-moving client.

## S3. The debates worth having

**Should you ever force-migrate clients?**

The case for forcing: infinite backwards compatibility is technically impossible. Infrastructure ages out. Security vulnerabilities accrue. Eventually, the cost of maintaining old versions exceeds the cost of breaking clients who haven't migrated. Stripe and Stripe-level resources can maintain 7 years of versions. Most teams cannot.

The case against: breaking a client without consent violates the contract trust that makes APIs valuable. Developer ecosystems take years to build and can be destroyed in one incident.

Position: force migration is justified — but the timeline must be generous (12+ months for external APIs), communicated through multiple channels, with direct outreach to every known client, and migration tooling that makes the upgrade path explicit. What's not acceptable is surprise: shipping a breaking change with inadequate notice, or setting a sunset date you extend so many times that clients stop believing it's real. When you finally enforce it, they're not ready.

**URL versioning vs header versioning**

The case for header versioning: cleaner URL namespace, more granular version pinning (dates instead of integers), better support for incremental upgrades without full migration events. This is the architecturally mature approach — Stripe built a profitable developer ecosystem on it.

The case for URL versioning: visible, testable, cacheable, proxy-friendly, shows up in logs and monitoring without additional tooling. Zero learning curve for any developer.

Position: URL versioning wins for most teams. Header versioning's elegance requires tooling investment to compensate for invisibility — you need developer portals with version dashboards, API gateways that enforce version headers, monitoring that tracks version adoption. If you have an API platform team, build toward header versioning. If you don't, URL versioning done well is better than header versioning done poorly.

**Should PMs own API versioning decisions or engineering?**

In most teams, neither owns it clearly. Engineers make version decisions because "it's a technical question." PMs are not in the room. Then a breaking change ships without a migration window. A client breaks. The post-mortem eventually includes "PM should have been involved earlier."

But if you hand versioning decisions to PMs without engineering context, you get sunset timelines set by business urgency rather than client migration reality — too aggressive, underresourced, and ultimately extended anyway.

The correct split: PMs own the external relationship surface — the sunset timeline (because you know how long clients need), the communication strategy (because you own developer relations), and the business cost of running parallel versions. Engineering owns the technical surface — what counts as breaking, how to maintain two versions without forking the codebase, when the tech debt of old versions exceeds the migration cost. Neither decides alone. The breakdown happens when PMs assume "versioning is a technical decision" and disengage. It isn't. Versioning is a product management problem that requires engineering execution.
