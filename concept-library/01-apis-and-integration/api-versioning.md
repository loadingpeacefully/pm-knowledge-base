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

# FOUNDATION

**For:** non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules

**Assumes:** 01.01 What is an API. You know what an API call is and what a "contract" means.

---
```

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

> **API versioning:** Publishing your API under a version identifier — most commonly `/v1/` or `/v2/` in the URL path — so that when you need to make an incompatible change, you can create a new version (`/v2/`) while clients on the old version (`/v1/`) keep working until they're ready to migrate.

### The core PM skill: identifying change type

| **Non-breaking changes** | **Breaking changes** |
|---|---|
| Safe to add to current version | Require a new version |
| Existing clients continue working | Existing clients will fail |
| Adding a new optional field to a response | Removing a field |
| Adding a new endpoint | Renaming a field (`name` → `fullName`) |
| Adding an optional query parameter | Changing a field's data type (string to integer) |
| Fixing a bug in existing behaviour (usually) | Making an optional field required |
| | Removing an endpoint |
| | Changing an error code or error format |

⚠️ **Common mistake:** Teams treat non-breaking changes casually and miss when a "small cleanup" is actually breaking. The rename example above—`name` → `fullName`—looks like a refactor but is a breaking change that requires a new API version.

## F3. The analogy that makes it click

**Textbook editions as API versions**

When an author makes substantial updates — new chapters, reorganised content, different exercises — they release a 2nd edition with a new ISBN. Schools can keep teaching from the 1st edition while new students get the 2nd. Both editions co-exist simultaneously.

| Element | Textbook Edition | API Versioning |
|---------|------------------|-----------------|
| **Version identifier** | ISBN | Version number |
| **What changes** | Chapters, content, exercises | API contract |
| **Backward compatibility** | Old edition still available | v1 and v2 run side-by-side |
| **When you create new version** | Breaking changes for users | Breaking changes to contract |
| **Can you modify after release?** | No — edition is fixed | No — version is immutable |

**URL versioning: the standard approach**

Most teams embed the version directly in the URL, like an ISBN on a book spine:

```
GET /v1/student     → version 1 of the student lookup API
GET /v2/student     → version 2, with breaking changes, running alongside v1
```

**Why URL versioning wins**

- ✓ Test both versions in a browser
- ✓ Share either URL in Slack or documentation
- ✓ Version appears in logs and monitoring
- ✓ Visible everywhere by default

## F3. When you'll encounter this as a PM

### Scenario 1: Internal "cleanup" that's actually breaking
Engineers often don't notice the boundary between non-breaking and breaking changes.

**The problem:** "We're just renaming this field" feels trivial internally. From the outside, it breaks every client using that field.

**Your question to ask:**
> "Who depends on this response today, and what happens to them when this changes?"

---

### Scenario 2: Third-party API integration
**The risk:** If you call `/v1/` and the vendor sunset v1 six months ago without telling you, you'll get failures with no warning.

**Your mitigation:**
- Pin to a specific version in your integration
- Monitor for deprecation notices
- Don't assume vendor support continues

---

### Scenario 3: Security fix requiring breaking change
⚠️ **Worst case scenario**

| Constraint | Your decision |
|---|---|
| Can't silently apply secure fix | Would break existing clients |
| Must version the change | Run insecure v1 + secure v2 in parallel |
| Migration window length | Product and risk decision, not engineering-only |

---

### Scenario 4: Public API with external developers
**Why this matters:** Developers build business logic on your API. Every breaking change without versioning destroys developer trust.

**Companies that get this right** (Stripe, Twilio, Shopify) treat versioning as a commitment, not an afterthought. This becomes competitive advantage.

---

# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PM, consumer startup PM, B2B enterprise PM, 2+ years experience
# Assumes: Foundation. You understand what a breaking change is and why versions exist.
# ═══════════════════════════════════

## W1. How it works — mechanics and deprecation lifecycle

### Quick Reference

| Approach | Syntax | Pros | Cons | Best for |
|----------|--------|------|------|----------|
| **URL Path** | `GET /v2/student` | Visible in logs, testable in browser, easy to route | — | Default choice |
| **Header** | `GET /student` + `API-Version: 2024-01-01` | Clean URLs, elegant | Invisible in logs, harder to test, easy to forget | Teams with dedicated API platform function |
| **Query Parameter** | `GET /student?version=2` | Works | Mixes with functional params, messy | Only for retrofitting legacy APIs |

**Default recommendation:** URL path versioning. Pick it at the start and stay consistent. The wrong choice is mixing approaches — some endpoints on path, some on headers.

---

### Three versioning approaches

**URL path versioning**

```
GET /v1/student
GET /v2/student
```

Visible in logs, testable in a browser, easy to route at the infrastructure layer. Most teams start and stay here.

---

**Header versioning**

```
GET /student
API-Version: 2024-01-01
```

Stripe uses this approach — each API key is pinned to a specific version date. Elegant architecture, but invisible in URLs, harder to test without tooling, easier to forget in client code. Suitable for teams with a dedicated API platform function that can enforce consistency.

---

**Query parameter versioning**

```
GET /student?version=2
```

Least common. Works, but messy. Versions get mixed with functional query parameters. Avoid unless you're retrofitting an API that didn't originally plan for versioning.

---

## The deprecation lifecycle

Versioning is not just about launching v2. It's about running v1 and v2 simultaneously through a defined deprecation window and then removing v1 cleanly.

**The five-step lifecycle:**

1. **Design v2** with the breaking change. Ship it alongside v1 — both endpoints live.
2. **Announce deprecation** of v1 with a specific sunset date. Document what changed and what clients need to do. Publish a migration guide.
3. **Add deprecation warnings** to v1 responses — a `Deprecation` header with the sunset date, so clients who read headers see the warning even if they missed the announcement.
4. **Support the migration** — don't just announce and disappear. Build migration tooling if the change is complex. Run office hours for external developers if you have them.
5. **Sunset v1** on the announced date. Remove the code. Not "start sending 410 Gone" — actually remove it so the codebase doesn't carry dead weight forever.

**Timeline minimums:**
- External/public APIs: **6 months minimum**
- Internal APIs (where you control all clients): **3 months minimum**

Shorter timelines create emergencies. Longer timelines mean you're maintaining two codebases indefinitely.

---

## KB grounding: a real versioning decision

The student lookup API in production uses `/v1/` path versioning — `GET /v1/student` and `GET /v1/student/details`. That's the versioning strategy working as designed.

### Issue #1: Security gap in default response

⚠️ **Security Issue — High Priority**

The `/v1/student/details` endpoint returns sensitive parent data (email address, phone number) in the default response. The only protection is an opt-in masking flag — `isFe=true` in the query — which frontends are supposed to use to strip the sensitive fields.

**The proper fix:** Make masked data the default, with an explicit opt-in to receive it for authorised internal use. But removing fields from the default response is a breaking change. Any client that currently depends on receiving those fields without the flag will break.

**Current state:** The `isFe=true` pattern is the team deferring that breaking change. It's a reasonable short-term workaround. But the version cost is accumulating. Until they ship `/v2/student/details` with safe defaults, they're running a v1 endpoint with a known security gap — and the reason it hasn't been fixed is that fixing it properly requires going through the versioning process.

---

### Issue #2: Semantic HTTP status misuse

The API returns `success: false` with an HTTP 200 status for records not found. Semantically wrong — a 404 should be used — but fixing it to return 404 is also a breaking change. Any client that checks the `success` field instead of the HTTP status would silently break.

**Priority:** Low-priority, sitting in v1 until someone decides the migration cost is worth paying.

---

**What this reveals:**

API versioning decisions in production are not abstract. They are real debt, real cost, real tradeoff. A single broken choice compounds across the entire API lifetime.

## W2. Tradeoffs — with recommendations

### Quick Reference
| Decision | External APIs | Internal APIs |
|----------|---------------|---------------|
| **Versioning approach** | URL versioning (default) | URL versioning (default) |
| **Support window** | 6+ months | 3 months |
| **Scope** | Whole API per version | Whole API per version |
| **Change policy** | Additive-only | Additive-only |

---

### URL versioning vs header versioning

| Dimension | URL Versioning | Header Versioning |
|-----------|---|---|
| **Visibility** | Visible in every request | Hidden in headers |
| **Testability** | Easy to test multiple versions | Requires header manipulation |
| **Proxy-friendly** | ✓ Proxies understand the route | Can bypass version headers |
| **Granularity** | One version per URL | Supports date-based pinning (Stripe) |
| **Enforcement** | Natural for all requests | Requires team discipline |

**Recommendation:** Default to URL versioning unless you have a dedicated API platform team enforcing header consistency across all services.

⚠️ **Risk:** Header versioning's invisibility becomes a liability—engineers frequently forget to add version headers in new client code, causing silent version mismatches.

---

### How long to run old versions

| Window | Pros | Cons | Best for |
|--------|------|------|----------|
| **30–60 days** | Fast migration cadence | Creates client emergencies; insufficient migration time | Internal APIs with enumerated, reachable clients only |
| **6 months** | Balanced; time for planning | Moderate codebase maintenance burden | Standard for external APIs |
| **12+ months** | Safe for all clients | Running two+ codebases indefinitely; testing overhead | Only if client diversity requires it |

**Recommendation:** 
- External APIs: **6 months minimum**
- Internal APIs: **3 months** (only if you can contact every client)
- Never shorten external timelines—you cannot know all your clients

⚠️ **Risk:** Shortening external timelines creates unmanageable migration chaos for unknown downstream users.

---

### Version the whole API vs version individual endpoints

| Approach | Example | Cost | Risk |
|----------|---------|------|------|
| **Whole-API versioning** | `/v2/payment`, `/v2/student`, `/v2/users` | Higher per-version overhead | Single migration event; clear tracking |
| **Selective versioning** | `/v2/payment` + `/v1/student` + `/v2/users` | Appears economical initially | Version matrix becomes unmaintainable |

**The selective approach creates unsustainable complexity:**
- Which client is on v1 for payments but v2 for users?
- What version combinations are officially supported?
- Which versions can be sunset together?

**Recommendation:** Default to versioning the whole API together. One version number, one migration event, one sunset date. The clarity overhead pays off immediately.

---

### Additive-only policy (strong default)

> **Additive-only versioning:** Never remove, rename, or restructure fields within a published version. Only add new fields or endpoints.

**How it works:** When you need to remove something, publish a new version; leave the old field untouched in the previous version.

| Dimension | Benefit |
|-----------|---------|
| **Stability** | v1 clients never break unexpectedly |
| **Trust** | Developers rely on the version contract |
| **Simplicity** | Lowest-cost versioning discipline |

**Trade-off:** Old versions accumulate unused or superseded fields over time (technical cruft).

**Real-world example (Stripe):** Maintains decades of API versions without breaking changes within a version. Cost: some inconsistencies in older endpoints. Benefit: legendary developer trust and minimal client churn during migrations.

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

### Stripe — Date-based header versioning

**What:** API keys pinned to creation date; versions maintained back to 2011 (7+ years backwards compatibility); explicit breaking vs non-breaking changelog per version.

**Why:** Heavy investment in migration guides and upgrade tooling reduces friction for developers.

**Takeaway:** Consistently highest developer trust scores among API platforms — versioning as competitive advantage.

---

### Twilio — URL path versioning (date-based)

**What:** Date strings embedded directly in path: `/2010-04-01/Accounts/{AccountSid}/Messages`

**Why:** Version visibility and pinning alongside newer versions, unusual format but same underlying principle.

**Takeaway:** Demonstrates multiple valid implementations of the same core strategy.

---

### Shopify — Date-based URL versioning with lifecycle discipline

**What:** Quarterly releases; 12-month support window before sunset (`api.myshopify.com/admin/api/2024-01/{resource}`).

**Why:** Clear migration timeline lets app developers plan predictably.

**Takeaway:** Predictability + structured sunset = ecosystem trust, even with active deprecation.

---

### Student API (KB) — Versioning debt in action

**What:** Simple path versioning (`/v1/`); two documented breaking issues unresolved:
- `isFe=true` security hack
- `success: false` on 200 for not-found

**Why:** Both require breaking changes to fix; migration cost deferred.

**Takeaway:** Classic versioning debt: right fix exists, cost is real, team is deferring it. Shows the real-world trade-off between technical correctness and adoption friction.

---

# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: ex-engineer PM, senior PM, AI-native PM, technical leads moving into product
# Assumes: Working Knowledge. You understand the deprecation lifecycle and can identify breaking changes.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### The forever-v1 trap

**What happens:**
The team ships v2 and announces v1 deprecation with a sunset date of six months. Six months pass. One major client hasn't migrated. The sunset date slips to three more months. Those three months pass. Two more clients. Another extension.

Two years later, v1 is still running with five sunset date extensions. Every endpoint exists twice. Every new feature ships to both versions. Engineers budget time for this. It compounds.

**Root cause:**
The PM didn't audit client migration status at the three-month mark. Migration happened for clients who were watching. Clients who weren't watching didn't migrate. The announcement was sent once. Nobody followed up.

**Prevention:**

- Treat API migration like a product launch with a customer success motion
- Know every client on v1 by name
- Contact them individually at the midpoint
- Make migration the path of least resistance with tooling and clear guides
- **Hold the sunset date** — slipping it once teaches clients that sunset dates are suggestions

---

### The silent breaking change

**What happens:**
An engineer makes a change they consider minor. The `GET /v1/student` endpoint was returning `success: false` with HTTP 200 for not-found records — inconsistent, but that's how v1 worked. Someone "fixes" it to return HTTP 404 instead. Ships without a version bump.

Every client that checked `success: false` to detect not-found behavior now gets a 404 and potentially crashes, because their error handler didn't expect 404 from this endpoint.

**Why it's dangerous:**

Breaking changes that masquerade as bug fixes are the most dangerous category. There is no malice — just the assumption that "this was wrong before, clients shouldn't have relied on it." Clients did rely on it. They always do.

> **Silent breaking change:** A behavior modification shipped without version increment, disguised as a bug fix, that changes how existing clients experience the API.

**Mitigation:**

Code review for API changes must explicitly ask:

| Question | Action |
|----------|--------|
| Does this change the behavior any existing client could depend on? | Treat as breaking change |
| Can you prove no client depends on the old behavior? | Only then skip version bump |
| Uncertain about client dependencies? | Default to version bump |

---

### The mass migration failure

**What happens:**
The team ships v2 with genuine improvements — better security, cleaner response format, lower latency. They announce a 30-day migration window because engineering is confident v2 is ready and wants to move fast.

Internal services migrate in a week. Three days before sunset, the first external developer files a support ticket: they hadn't seen the announcement. A week after sunset, a B2B enterprise partner escalates to the CEO: their integration broke during a board demo.

**The problem:**

The 30-day window was designed for an engineering team context. External developers have:
- Day jobs
- Release cycles
- Approval processes
- Support queues

30 days is not enough. The escalation cost more than three additional months of running both versions would have.

**Rule of thumb:**

> Set migration timeline by the slowest client you have, not the fastest. If your slowest client needs 6 months, that's your minimum. You can incentivize faster clients to migrate early, but the sunset date anchors to the laggards.

---

### API-versioning theater

**What happens:**
The version number exists in the URL. Breaking changes still happen in v1. The team quietly ships behavioral changes, response format changes, or field renames without incrementing the version — because "it's not really breaking, it's just a fix."

Clients who were stable on v1 start experiencing intermittent failures they can't explain. They check the changelog: nothing there. They file a support ticket. The API is technically on the same version it always was.

⚠️ **Trust destruction risk:** Versioning theater maintains the appearance of a stable contract while violating it in practice. This is the most corrosive failure pattern.

**Mitigation:**

- Document an enforced definition of breaking change
- Route any API change with behavioral impact through a version review before shipping
- Version review gates the change to production

## S2. How this connects to the rest of your work

### 01.01 — What is an API

> **API Contract:** The agreement between you and clients about what data, fields, and behavior the API provides

Versioning is your change management layer on top of the contract. Every breaking change is a contract renegotiation—versioning makes that renegotiation **orderly rather than chaotic**.

---

### 01.02 — API Authentication

| Aspect | Impact on Versioning |
|--------|----------------------|
| Authentication schemes | Can change between versions |
| OAuth scopes | v2 may have more granular permissions than v1 |
| API key formats | May change across versions |
| Client migration surface | **Doubles**—clients migrate data contract + auth contract simultaneously |

**Plan this in your migration guide.** Clients migrating v1→v2 are solving two problems at once.

---

### 01.03 — Webhooks vs Polling

> **Webhook Contract:** The specific fields and structure in the payload fired when an event occurs (e.g., payment completion)

**The risk:** Renaming a field in a webhook payload without versioning breaks every integration listening to it—**silently**.

**Why webhooks are harder:**
- Webhook consumers are *passive* (data arrives to them; they don't request it)
- You can't easily find or notify all webhook consumers during migration
- Silent failures are common

---

### 01.04 — Rate Limiting

**Strategy:** Use version-specific rate limits as a migration incentive.

| Scenario | Client Motivation |
|----------|-------------------|
| Same rate limits on v1 and v2 | "Migration is work with no benefit to me" |
| Higher rate limits on v2 | "Migration gets us better throughput" ✓ |

A tangible performance benefit often provides the nudge needed to unstick slow-moving clients.

## S3. The debates worth having

### Should you ever force-migrate clients?

| **Case For** | **Case Against** |
|---|---|
| Infinite backwards compatibility is technically impossible. Infrastructure ages out. Security vulnerabilities accrue. Eventually, the cost of maintaining old versions exceeds the cost of breaking clients who haven't migrated. Stripe and Stripe-level resources can maintain 7 years of versions. Most teams cannot. | Breaking a client without consent violates the contract trust that makes APIs valuable. Developer ecosystems take years to build and can be destroyed in one incident. |

**Position:** Force migration is justified — but only with:
- ⚠️ **Timeline:** 12+ months minimum for external APIs
- **Communication:** Multiple channels + direct outreach to every known client
- **Tooling:** Migration assistance that makes the upgrade path explicit

⚠️ **What's not acceptable:** Surprise breaking changes with inadequate notice, or setting a sunset date you extend repeatedly until clients stop believing it's real. When you finally enforce it, they're unprepared.

---

### URL versioning vs header versioning

| **Header Versioning** | **URL Versioning** |
|---|---|
| Cleaner URL namespace. More granular version pinning (dates instead of integers). Better support for incremental upgrades without full migration events. Architecturally mature — Stripe built a profitable developer ecosystem on it. | Visible, testable, cacheable, proxy-friendly. Shows up in logs and monitoring without additional tooling. Zero learning curve for any developer. |

**Position:** URL versioning wins for most teams.

Header versioning's elegance requires significant tooling investment to compensate for invisibility:
- Developer portals with version dashboards
- API gateways that enforce version headers
- Monitoring that tracks version adoption

**Decision rule:** If you have an API platform team, build toward header versioning. If you don't, URL versioning done well beats header versioning done poorly.

---

### Should PMs own API versioning decisions or engineering?

**Current reality:** Neither owns it clearly.
- Engineers make version decisions because "it's a technical question"
- PMs are not in the room
- Breaking changes ship without a migration window
- Post-mortems conclude: "PM should have been involved earlier"

**The trap:** If you hand versioning decisions to PMs without engineering context, you get:
- Sunset timelines set by business urgency rather than client migration reality
- Timelines that are too aggressive and underresourced
- Extensions that become the norm

**Correct split:**

| **PM Owns** | **Engineering Owns** |
|---|---|
| External relationship surface: sunset timeline, communication strategy, business cost of running parallel versions | Technical surface: what counts as breaking, how to maintain two versions without forking the codebase, when tech debt of old versions exceeds migration cost |

**Critical principle:** Neither decides alone. The breakdown happens when PMs assume "versioning is a technical decision" and disengage.

> **Key insight:** Versioning is a product management problem that requires engineering execution — not a purely technical decision.