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

> **API Versioning:** Publishing your API under a version identifier (most commonly `/v1/` or `/v2/` in the URL path) so that incompatible changes can be deployed as a new version while existing clients continue working until they migrate.

### The Core PM Skill

Understanding the difference between two types of API changes:

| Change Type | Definition | Examples | Client Impact |
|---|---|---|---|
| **Non-breaking** | Safe to add to current version | • Adding new optional field<br>• Adding new endpoint<br>• Adding optional query parameter<br>• Fixing existing bugs | ✅ No clients break |
| **Breaking** | Requires new version | • Removing a field<br>• Renaming a field (`name` → `fullName`)<br>• Changing data type (string → integer)<br>• Making optional field required<br>• Removing an endpoint<br>• Changing error code/format | ❌ Existing clients fail |

### The Real Risk

Teams treat non-breaking changes casually and fail to recognize when a "small cleanup" is actually breaking.

**Example:** Renaming `name` → `fullName` looks like a refactor but is a breaking change in disguise.

## F3. The analogy that makes it click

### Textbook Editions = API Versions

When an author releases a textbook with substantial updates, they publish a new edition with a new ISBN. Both editions coexist—schools can keep using the 1st edition while new students get the 2nd. Nothing reaches back to change the 1st edition after publication.

**The mapping:**
| Textbook World | API World |
|---|---|
| ISBN | Version number |
| Textbook content | API contract |
| New edition (breaking changes) | New API version |
| Simultaneous editions in use | v1 and v2 running together |

### URL Versioning: The Standard Approach

Most teams put the version directly in the URL path, mirroring how an ISBN appears on a book spine.

**Examples:**
- `GET /v1/student` — version 1 of the student lookup API
- `GET /v2/student` — version 2, with breaking changes, running alongside v1

**Why this works:**
- ✅ Both versions testable in a browser
- ✅ URLs shareable in Slack messages
- ✅ Visible in logs and monitoring
- ✅ Immediately clear which version you're using

The version visibility everywhere is why URL versioning remains the default approach for most teams.

## F3. When you'll encounter this as a PM

### Shipping "cleanup" that's actually a breaking change
Engineers often don't notice the boundary. "We're just renaming this field" feels trivial internally. From the outside, it breaks every client using that field.

**Your move:** Ask "Who depends on this response today, and what happens to them when this changes?"

---

### Integrating with a third-party API
⚠️ **Risk:** If you call `/v1/` and the vendor sunset v1 six months ago without telling you, you'll get failures with no warning.

**Your move:** 
- Pin to a specific version in your integration
- Monitor for deprecation notices from the vendor

---

### Security issue requiring breaking-change fixes
⚠️ **Worst case scenario:** The secure fix requires a breaking change. You can't silently apply it — that breaks clients.

**What happens:**
- Run insecure v1 alongside secure v2 during migration window
- How long that window lasts = **product and risk decision, not just engineering**

---

### Offering a public API
> **Developer trust principle:** Every breaking change you ship without versioning destroys developer trust.

**Why it matters:** Teams with the best developer relationships (Stripe, Twilio, Shopify) treat versioning as a **commitment, not an afterthought**.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PM, consumer startup PM, B2B enterprise PM, 2+ years experience
# Assumes: Foundation. You understand what a breaking change is and why versions exist.
# ═══════════════════════════════════

## W1. How it works — mechanics and deprecation lifecycle

### Quick Reference: Versioning Approaches

| Approach | Format | Visibility | Testing | Use When |
|----------|--------|------------|---------|----------|
| **URL Path** | `GET /v2/student` | Visible in logs & browser | Easy, no tooling needed | Starting fresh (default) |
| **Header** | `GET /student` + `API-Version: 2024-01-01` | Hidden from URL | Requires tooling | Dedicated API platform team |
| **Query Parameter** | `GET /student?version=2` | Mixed with functional params | Works but messy | Retrofitting only |

**Default recommendation:** URL path versioning. Pick it at the start and stay consistent.

⚠️ **The critical mistake:** Mixing approaches — some endpoints on path, some on headers — destroys predictability across your API surface.

---

### Three Versioning Approaches

#### URL Path Versioning
```
GET /v1/student
GET /v2/student
```
Visible in logs, testable in a browser, easy to route at the infrastructure layer. Most teams start and stay here.

#### Header Versioning
```
GET /student
API-Version: 2024-01-01
```
Stripe uses this approach — each API key is pinned to a specific version date. Elegant architecture, but invisible in URLs, harder to test without tooling, easier to forget in client code. Suitable for teams with a dedicated API platform function that can enforce consistency.

#### Query Parameter Versioning
```
GET /student?version=2
```
Least common. Works, but messy. Versions get mixed with functional query parameters. **Avoid** unless you're retrofitting an API that didn't originally plan for versioning.

---

### The Deprecation Lifecycle

> **Deprecation Lifecycle:** The process of running two API versions simultaneously through a defined window, then removing the old version cleanly — not abandoning it mid-flight.

Versioning is not just about launching v2. It's about running v1 and v2 simultaneously through a defined deprecation window and then removing v1 cleanly.

**The five-step process:**

1. **Design v2** with the breaking change. Ship it alongside v1 — both endpoints live.
2. **Announce deprecation** of v1 with a specific sunset date. Document what changed and what clients need to do. Publish a migration guide.
3. **Add deprecation warnings** to v1 responses — a `Deprecation` header with the sunset date, so clients who read headers see the warning even if they missed the announcement.
4. **Support the migration** — don't just announce and disappear. Build migration tooling if the change is complex. Run office hours for external developers if you have them.
5. **Sunset v1** on the announced date. Remove the code. Not "start sending 410 Gone" — actually remove it so the codebase doesn't carry dead weight forever.

**Timeline guidance:**
- **External/public APIs:** Minimum 6 months
- **Internal APIs:** Minimum 3 months (you control all clients)

⚠️ **Short timelines** create emergencies. **Long timelines** mean you're maintaining two codebases indefinitely.

---

### KB Grounding: A Real Versioning Decision

**The student lookup API uses `/v1/` path versioning** — `GET /v1/student` and `GET /v1/student/details`. That's the versioning strategy working as designed.

#### The Security Issue

The `/v1/student/details` endpoint has a documented **High-priority security issue:**

| Issue | Current State | Root Cause |
|-------|---------------|-----------|
| Sensitive data exposed | Parent email & phone returned by default | Only opt-in masking available (`isFe=true`) |
| Proper fix | Make masked data default, explicit opt-in for sensitive fields | Breaking change — requires v2 |
| Status quo cost | Known security gap remains in production | Team deferred breaking change |

The `isFe=true` pattern is a reasonable short-term workaround. But the version cost is accumulating. Until they ship `/v2/student/details` with safe defaults, they're running a v1 endpoint with a known security gap.

#### The Semantic Issue

A second issue on the same endpoint: the API returns `success: false` with an HTTP 200 status for records not found.

| Issue | Current State | Impact |
|-------|---------------|--------|
| Wrong HTTP status | Returns 200 for "not found" instead of 404 | Semantically incorrect |
| Migration cost | Clients checking `success` field would silently break | Breaking change — requires v2 |
| Priority | Documented as Low-priority | Sits in v1 until tradeoff is accepted |

**What this reveals:** One small inconsistency, documented as Low-priority, sitting in v1 until someone decides the migration cost is worth paying.

---

**This is what API versioning decisions look like in production.** Not abstract. Real debt, real cost, real tradeoff.

## W2. Tradeoffs — with recommendations

### Quick Reference
| Decision | Default | Rationale |
|----------|---------|-----------|
| URL vs Header versioning | URL versioning | Visible, testable, proxy-friendly |
| Old version support window | 6mo external / 3mo internal | Balance safety with maintainability |
| Versioning scope | Whole API | Single version number, one sunset date |
| Breaking changes | Additive-only policy | Never break within a version |

---

### URL versioning vs header versioning

| Aspect | URL Versioning | Header Versioning |
|--------|---|---|
| **Visibility** | Explicit in request | Hidden in headers |
| **Testability** | Easy to test manually | Requires header tools |
| **Proxy-friendly** | Yes | Requires header support |
| **Architectural cleanliness** | Lower | Higher |
| **Granularity** | Coarse (whole version) | Fine (date-based pinning) |

**Default recommendation:** URL versioning

**When to choose header versioning:** Only with a dedicated API platform team that can enforce consistency across all services.

⚠️ **Risk:** Header versioning's invisibility causes engineers to forget version headers in new client code, creating silent compatibility breaks.

---

### How long to run old versions

| Timeline | External APIs | Internal APIs |
|----------|---|---|
| **Short (30–60 days)** | ❌ Creates migration emergencies | ✅ Acceptable with full client enumeration |
| **Medium (6 months)** | ✅ **Recommended** | ✅ **Recommended** |
| **Long (12+ months)** | ✅ Safe but costly | ⚠️ Indefinite dual maintenance |

**Default:** 6 months for external APIs, 3 months for internal

⚠️ **Critical:** Never shorten external API timelines. You cannot enumerate all clients.

---

### Version the whole API vs individual endpoints

> **Selective versioning:** Versioning only certain endpoints (e.g., `/v2/payment` alongside `/v1/student`)

**Problem:** Creates an unmaintainable version matrix
- Which client is on v1 for payments but v2 for users?
- What combinations are officially supported?
- Testing and support burden grows exponentially

**Default recommendation:** Version the whole API together

**Benefits:**
- One version number
- One migration event
- One sunset date
- Clarity for clients and engineers

---

### Additive-only policy (strong default)

> **Additive-only policy:** Never remove or rename anything in a published version. Only add new fields, endpoints, and behavior.

| Cost | Benefit |
|------|---------|
| Old versions accumulate cruft | Clients never experience breaking changes |
| Larger payload sizes over time | Developers trust the contract implicitly |
| More backward-compatibility code | No surprise migrations required |

**How Stripe operates:** Maintained decades of API versions without breaking changes within a version. Old versions have inconsistencies, but the guarantee—*this version will never break you*—creates developer trust.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **"What's our current versioning strategy — URL path, header, or query param?"** | Whether there's a consistent approach or ad hoc variation per endpoint, and whether anyone actually owns this decision |
| **"What's your definition of a breaking change? Where is that documented?"** | Whether the team has shared alignment — engineers often disagree on what counts as breaking, and that disagreement causes incidents |
| **"How long do we support old versions? Who decides the sunset date?"** | Whether you have a formal deprecation process or just let old versions accumulate until someone notices |
| **"How do we communicate deprecations to external clients — response headers, email, docs?"** | Whether clients get advance warning through multiple channels or just find out when things break |
| **"If we needed to fix a security issue that requires a breaking change, how long would migration take?"** | Your actual risk surface — a 12-month migration means a 12-month window for a known vulnerability to stay in production |
| **"Are there any endpoints right now that technically need a v2 for a known issue but haven't been versioned yet?"** | Whether technical debt is accumulating behind backwards compatibility — the `isFe=true` security issue is exactly this kind of deferred breaking change |
| **"How do we test that v1 still works when we ship v2?"** | Whether there's regression testing for old versions or whether it's manual and best-effort — the thing that breaks when this doesn't exist is the assumption that v1 is stable |

## W4. Real companies

### Stripe — Date-based versioning with 7+ years of backwards compatibility

**What:** Date-based header versioning (`2023-10-16`). Each API key pinned to the version it was created on.

**Why:** Maintains versions back to 2011 (~7 years backwards compatibility). Changelog explicitly marks breaking vs non-breaking changes. Heavy investment in migration guides and upgrade tooling.

**Takeaway:** Consistently highest developer trust scores among API platforms.

---

### Twilio — Date-based path versioning with account structure

**What:** URL path versioning with date strings embedded: `/2010-04-01/Accounts/{AccountSid}/Messages`

**Why:** Version visible, pinned, and running alongside newer versions. Unusual format but same principle as Stripe.

**Takeaway:** Demonstrates flexibility in *where* you encode versions, not just *how*.

---

### Shopify — Quarterly releases with defined sunset windows

**What:** Date-based URL versioning (`api.myshopify.com/admin/api/2024-01/{resource}`). New versions released quarterly with 12-month support window.

**Why:** App developers in the ecosystem have clear migration timelines and can plan accordingly.

**Takeaway:** Predictable cadence builds trust even with shorter support windows.

---

### Student API (KB) — Path versioning with unresolved technical debt

**What:** Path versioning at `/v1/` for both endpoints. Simple, clean implementation.

**Why:** Two documented issues require breaking changes to fix properly:
- `isFe=true` security hack
- `success: false` on 200 for not-found responses

**Takeaway:** Neither issue has been versioned yet. Classic versioning debt: the right fix exists, the cost is migration, and the team is deferring it.

*What this reveals:* Versioning isn't just a technical choice—it's a commitment to fixing mistakes. Deferring breaks compounds risk over time.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineer PM, senior PM, AI-native PM, technical leads moving into product
# Assumes: Working Knowledge. You understand the deprecation lifecycle and can identify breaking changes.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### The forever-v1 trap

**What happens:**
- Team ships v2 and announces v1 deprecation with a sunset date
- At the midpoint, some clients haven't migrated
- Sunset date slips
- Two years later: v1 still running, five sunset extensions, every endpoint maintained twice

**Root cause:**
The PM didn't audit migration status at the three-month mark. Announcements sent once don't drive behavior change for inattentive clients.

**Prevention checklist:**
- Treat API migration like a product launch with customer success motion
- Maintain a named list of every v1 client
- Contact each client individually at the midpoint
- Build migration tooling and clear guides
- **Hold the sunset date** — slipping once teaches clients that dates are suggestions

---

### The silent breaking change

**What happens:**
An engineer "fixes" inconsistent behavior they consider a bug. `GET /v1/student` returned `success: false` with HTTP 200 for not-found records. The engineer changes it to return HTTP 404 (semantically correct). Ships without a version bump.

Clients checking `success: false` to detect not-found behavior now get 404 and crash. Their error handlers never expected 404 from this endpoint.

**Why it's dangerous:**
> **Breaking change masquerading as bug fix:** These are the most dangerous category. There is no malice—just the assumption that clients "shouldn't have relied on" the old behavior. They did.

**Mitigation:**
Code review for all API changes must explicitly ask:

> **Required question:** "Does this change the behavior any existing client could depend on?"

If the answer is "I don't know," default to a version bump unless you can affirmatively prove no client depends on the old behavior.

---

### The mass migration failure

**What happens:**
- Team ships v2 with real improvements (security, response format, latency)
- Announces 30-day migration window
- Internal services migrate in a week
- Three days before sunset: first external developer files support ticket (missed the announcement)
- One week after sunset: B2B enterprise partner's integration breaks during a board demo

**Why it fails:**
30 days is engineered-team thinking. External developers have day jobs, release cycles, and approval processes.

⚠️ **Risk:** Escalation costs far exceed the cost of running both versions longer.

**Migration timeline rule:**
> **Set deadlines by slowest client, not fastest:** If your slowest client needs 6 months, that's your minimum. You can incentivize faster clients to migrate early, but the sunset date anchors to the laggards.

---

### API-versioning theater

**What happens:**
The version number exists in the URL but versioning is not enforced. Breaking changes ship without incrementing the version:
- Behavioral changes
- Response format changes  
- Field renames

All treated as "just fixes," not new versions.

Clients stable on v1 experience intermittent failures. The changelog shows nothing. Support tickets arrive with no explanation.

⚠️ **Trust destruction:** Versioning theater maintains the appearance of a stable contract while violating it in practice.

**Only mitigation:**
- Document a strict definition of breaking change
- Route every API change with behavioral impact through version review before shipping
- Enforce the process

## S2. How this connects to the rest of your work

### 01.01 — What is an API

> **API Contract:** The agreement between provider and client about what data/functionality is available and how to access it

Versioning is your change management layer on top of the contract. Every breaking change is a contract renegotiation—versioning makes that renegotiation orderly rather than chaotic.

### 01.02 — API Authentication

| Aspect | Migration Impact |
|--------|------------------|
| **Scope granularity** | OAuth scopes for v2 may be more granular than v1 |
| **Key formats** | May change between versions |
| **Surface area** | Clients migrate both data contract AND authentication contract simultaneously |

**Plan for it:** Include authentication changes in your migration guide. This doubles the migration surface.

### 01.03 — Webhooks vs Polling

> **Webhook Payload Contract:** The specific fields and structure of data sent to integrations on event triggers

Webhook versioning is often forgotten because:
- Webhook consumers are **passive** (don't request data; data arrives at them)
- Field renames without versioning break integrations **silently**
- Webhook consumers are the **hardest clients to find and notify** during migration

### 01.04 — Rate Limiting

**Version-specific rate limits as migration incentive:**

- **v1 limits:** Baseline rate ceiling
- **v2 limits:** Higher throughput available
- **Outcome:** Converts "migration is work with no benefit" → "migration gets us better throughput"

Small leverage point, but sometimes the nudge that unsticks a slow-moving client.

## S3. The debates worth having

### Should you ever force-migrate clients?

| **The case for forcing** | **The case against** |
|---|---|
| Infinite backwards compatibility is technically impossible | Breaking a client without consent violates API contract trust |
| Infrastructure ages out; security vulnerabilities accrue | Developer ecosystems take years to build and can be destroyed in one incident |
| Cost of maintaining old versions eventually exceeds cost of breaking unmigrated clients | |
| Stripe maintains 7 years of versions, but most teams cannot | |

**Position: Force migration is justified — with conditions**

✅ **Required:**
- Generous timeline: 12+ months for external APIs
- Multi-channel communication
- Direct outreach to every known client
- Migration tooling that makes the upgrade path explicit

⚠️ **What's not acceptable:**
- Surprise breaking changes with inadequate notice
- Sunset dates extended repeatedly until clients stop believing them
- Forcing migration when clients aren't ready

---

### URL versioning vs header versioning

| **Header versioning** | **URL versioning** |
|---|---|
| **Pros:** Cleaner URL namespace; granular version pinning (dates instead of integers); incremental upgrades without full migration events; architecturally mature | **Pros:** Visible and testable; cacheable; proxy-friendly; shows up in logs without additional tooling; zero learning curve |
| **Cons:** Invisibility requires heavy tooling investment to compensate | **Cons:** Namespace pollution; full migration events required |
| **Example:** Stripe's profitable developer ecosystem built on this | **Example:** Most teams' default choice |

**Position: URL versioning wins for most teams**

Header versioning's elegance requires:
- Developer portals with version dashboards
- API gateways that enforce version headers
- Monitoring that tracks version adoption

> **When to choose:** If you have an API platform team, build toward header versioning. If you don't, URL versioning done well is better than header versioning done poorly.

---

### Should PMs own API versioning decisions or engineering?

**The current problem:**

Neither owns it clearly. Engineers make decisions because "it's a technical question." PMs aren't in the room. Breaking changes ship without migration windows. Post-mortems reveal: "PM should have been involved earlier."

**The wrong solution:**

Handing versioning to PMs without engineering context produces:
- Sunset timelines set by business urgency, not client migration reality
- Timelines that are too aggressive
- Underresourced execution
- Deadlines extended repeatedly anyway

**The correct split:**

| **PMs own** | **Engineering owns** |
|---|---|
| External relationship surface | Technical surface |
| Sunset timeline (you know client migration needs) | What counts as breaking |
| Communication strategy (you own dev relations) | How to maintain parallel versions without forking |
| Business cost of running parallel versions | When tech debt of old versions exceeds migration cost |

> **The key principle:** Versioning is a product management problem that requires engineering execution. Neither decides alone.

⚠️ **Where the breakdown happens:** When PMs assume "versioning is a technical decision" and disengage.