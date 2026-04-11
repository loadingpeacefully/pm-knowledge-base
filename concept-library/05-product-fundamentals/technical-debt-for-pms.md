---
lesson: Technical Debt for PMs
module: 05 — product-fundamentals
tags: product
difficulty: working
prereqs:
  - 03.05 — Infrastructure as Code — debt accumulates across the entire stack, not just features
  - 05.05 — Roadmapping — technical debt competes for space on every roadmap
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/infrastructure/web-app-optimization-champ.md
  - technical-architecture/infrastructure/server-schola-production-new.md
profiles:
  foundation: aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: senior PM, head of product, ex-engineer PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

A startup builds fast. The first version of the product is duct tape and clever workarounds — a login page that loads the entire app even though a new user only needs the login form, a database query that scans every row when it should use an index, a caching layer that was "temporary" but became permanent. The product ships. Users love it. The company grows.

Six months later, the engineering team announces that a feature that should take two weeks will take six. The infrastructure is so tangled that touching any one piece risks breaking three others. The app that was fast at 1,000 users is crawling at 50,000. Engineering can't keep up with the product roadmap — not because they're slow, but because half their time is fighting the code itself.

The company has technical debt.

Technical debt is the accumulated cost of shortcuts, incomplete solutions, and outdated architectural decisions made during earlier product development. Like financial debt, it has an interest rate: the longer you carry it, the more it costs you. And like financial debt, some amount of it is completely rational — sometimes the smart move is to ship fast now and clean up later. The problem is when teams forget to clean up, or don't have a PM who helps them make that tradeoff deliberately.

This is the lesson about what technical debt is, how to recognize it, and what your role as a PM is in managing it — because managing it is your job as much as it's engineering's.

---

## F2 — What it is — definition + analogy

> **Technical Debt:** The difference between ideal code (unlimited time) and actual code (real constraints). It compounds over time because imperfect foundations make all subsequent work harder.

### The House Analogy

Imagine buying a house on a budget. You accept shortcuts:
- Mismatched outlets
- An aging but functional furnace
- Furniture hiding a weird corner layout

Each compromise seems fine alone. But **five years later**, when you want to renovate the kitchen, you discover:
- Electrical wiring won't support a modern stove
- That hidden corner is a structural problem
- The furnace needs replacement before winter

**What this reveals:** A 3-month renovation becomes 9 months. You're living in a construction zone the whole time.

### How Technical Debt Works in Code

Technical debt follows the same pattern:

| Stage | What Happens | Why It Matters |
|---|---|---|
| **Creation** | Workarounds made sense when created | They seemed like safe, temporary shortcuts |
| **Accumulation** | They accumulate over time | New features must understand and work around old workarounds |
| **Friction** | Onboarding slows down | New developers must decode the codebase before contributing |
| **Cascades** | Bugs appear unexpectedly | Systems that should be independent are tangled together |

### What PMs Actually Need to Know

⚠️ **Your job is NOT to fix technical debt.** Your job is to:

1. **Recognize** when debt is slowing your roadmap
2. **Build the business case** for addressing it
3. **Prioritize** debt work vs. feature work

These are product decisions, not engineering decisions.

## F3 — When you'll encounter this as a PM

| Signal | What it means | PM action |
|--------|--------------|-----------|
| **Estimates keep being wrong** | Engineering consistently needs twice as long as estimated. Debt requires extra work *before* the feature can start. | Investigate whether scope estimates are missing pre-work phases |
| **Bugs appear in unexpected places** | Fixing one bug causes bugs elsewhere. Systems are more entangled than they should be. | Probe for hidden coupling; ask engineering which areas are tightly connected |
| **"Small" changes take a long time** | A UI text change requires 2 weeks; a new integration requires rewriting unrelated code. Work is out of proportion to scope. | Challenge the scope disconnect; map which systems need touching |
| **Engineering requests a "cleanup sprint"** | Engineers ask for infrastructure time instead of features. Debt is blocking their ability to ship. | ⚠️ Treat as critical signal requiring a *product decision*, not automatic approval or rejection |
| **Planning a major new feature** | You're about to touch a significant area of the codebase. | Assess technical debt in that area *before* committing. Prevents mid-delivery surprises and improves estimate accuracy. |
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Types of technical debt

Not all technical debt is the same. As a PM, understanding the categories helps you prioritize which debt to address and when:

| Type | What it is | Measurable business impact | Example |
|---|---|---|---|
| **Performance debt** | Code that works but runs slowly or inefficiently | +1s LCP typically drops mobile conversion 5–7%; every 100ms of latency costs Amazon ~1% of revenue (their 2006 public number) | All 49 routes loading a 2.5MB bundle when the login page needs ~300KB |
| **Architectural debt** | Systems built for one scale that don't support the current or needed scale | Feature delivery 30–50% slower in affected areas; estimate variance >50% vs. greenfield code | 27 Redux slices initialized on every page regardless of context |
| **Dependency debt** | Outdated or duplicated libraries and packages | CVE exposure window (days to patch after public disclosure); bundle bloat 200–500KB per duplicate library | Duplicate react-query dependency; moment.js (67KB) when date-fns (12KB tree-shaken) is leaner |
| **Test debt** | Missing or inadequate automated tests | Change failure rate doubles without automated tests; hotfix frequency 2–4× baseline; ~30 min of manual QA per deploy | No automated tests on checkout flow |
| **Documentation debt** | Undocumented systems that only a few engineers understand | Onboarding time 2–3× longer (typically 4–6 weeks instead of 2); bus-factor risk quantified by % of critical systems owned by single engineer | Undocumented data model for legacy course migration |

> **Redux:** The global state management library that holds application data in memory

> **Lottie:** A library that renders complex vector animations; files are often large

### BrightChamps — Student dashboard performance audit

**What:** A deliberate audit of the `champ.brightchamps.com` student dashboard uncovered significant performance debt as the product scaled.

**Why:** Silent debt compounds undetected until it becomes a crisis. Users experience it as "the app is slow," but no single event triggers visibility.

**Takeaway:** PMs who surface audits proactively prevent debt from compounding into crisis. This debt was silent—discovered through deliberate measurement, not failure.

#### Critical severity findings

- **All 49 routes load the same 2.5MB JavaScript bundle**
  - Login page (new user entry point) loads full dashboard code
  - Only needs ~300KB for authentication
  - *Analogy:* Building a 50-room mansion and making every visitor walk through every room to reach the front door

- **1.3MB Lottie animation file (`confetti_animation`) loads globally on pages that never play it**

#### High severity findings

- `moment.js` (date formatting library) used instead of `date-fns`
  - Same functionality, 5× larger
  - Opportunity: save 200KB
- ReactQuery DevTools (development-only tool) loading in production builds
- 27 Redux slices initialized on every page
  - Most pages need only 2–3 slices

#### Quantified debt

| Metric | Current | Target | Gap |
|---|---|---|---|
| Total initial load | 2.5MB | <1.5MB | 1MB unnecessary code per pageview |

### How debt accumulates

Debt rarely accumulates through recklessness. It accumulates through rational decisions under pressure:

| Driver | What happens | Why it matters |
|---|---|---|
| **Speed tradeoffs** | "We'll ship faster by loading the full bundle everywhere—we'll split it later" | Later never comes; always a new feature to build |
| **Changing requirements** | Caching layer built for 1K users doesn't scale to 100K | Nobody did anything wrong—requirements changed |
| **Growing complexity** | System that worked for 3 engineers becomes a minefield at 30 engineers | Nobody has a full mental model of the whole thing |
| **Legacy decisions** | Architectural choices that made sense then (load everything globally for simplicity) | Becomes debt when product scales |

### Measuring and communicating debt

As a PM, your job is to translate debt from engineering language into business outcomes. Stakeholders don't understand code quality metrics—they understand time, money, and user impact.

| Engineer says | You translate to | Business impact |
|---|---|---|
| "We need to refactor the Redux store" | "Every new dashboard feature takes 30% longer because of unnecessary global state management" | 30% longer = $X in engineering cost per feature |
| "The bundle size is causing LCP failures" | "First meaningful content appears 2 seconds later for users on average mobile connections" | 2 seconds = Y% conversion drop *(Google/SOASTA 2017 mobile research: 53% of mobile users abandon sites that take longer than 3 seconds to load; more recent Google Web Vitals studies 2020–2023 show 10% bounce-rate increase per 1s of load time added)* |
| "We have 0% test coverage on checkout" | "Every checkout change requires 2 days of manual QA and still ships bugs" | 2 days per change × 4 changes/month = 8 days QA overhead + bug risk |

> **LCP (Largest Contentful Paint):** A Google Core Web Vital that measures when the main content becomes visible

> **Best practice:** Always communicate debt in business terms: shipping speed, user experience, or business outcomes—not "the code is messy."

### The optimization roadmap structure

The BrightChamps audit organized debt fixes into a two-horizon roadmap:

#### Horizon 1 — Quick wins *(high impact, low risk)*

- Compress/replace top 5 Lottie animation files → saves >2MB
- Move language files to dynamic loading → saves >400KB
- Remove duplicate dependency and replace moment.js → saves ~200KB
- Remove ReactQuery DevTools from production → immediate improvement

**Timeline:** 3–5 engineering days  
**Result:** Majority of performance gain achieved quickly

#### Horizon 2 — Architectural fixes *(high impact, higher risk)*

- **Route-based 4-tier bundle strategy:**
  - Tier 1: ~300KB (auth only)
  - Tier 2: ~800KB (lightweight)
  - Tier 3: ~1.5MB (full dashboard)
  - Tier 4: ~1.2MB (specialized)
- **Redux store splitting** → multiple store configurations per context
- **Context optimization** → lightweight pages skip heavy contexts

**Timeline:** 3–4 engineering weeks  
**Result:** Eliminates root cause, prevents recurrence

> **Sequencing principle:** Quick wins first (build confidence, show progress, deliver immediate user benefit), then architectural work (addresses root cause, prevents future debt).

## W2 — The decisions this forces

### Decision 1: How much capacity should go to debt vs. features?

> **Technical Debt Interest Rate:** The observed pattern across teams with no technical-health budget is a steady decline in delivery velocity — typically 10–15% per quarter in the teams that track it, though the rate depends on codebase age, team size, and feature churn. Teams that protect 20% of capacity for technical work generally maintain velocity; teams that protect 30% or more often see velocity *improve* as accumulated drag gets paid down.

This is an empirical pattern, not a universal law. The direction is reliable (0% → decline, 20% → stable, 30%+ → improve), but the exact numbers depend on how old the codebase is and how much debt is already in it.

**Capacity allocation by company stage:**

| Stage | Protected technical capacity | Rationale |
|---|---|---|
| **Seed / early startup** (0–18 months, <10 eng) | 10–15% | Codebase is young, debt hasn't compounded, feature velocity matters more than infrastructure |
| **Growth stage** (18 months – 3 years, 10–50 eng) | 15–20% | Debt starts biting; this is the most common range and where Spotify's 20% "tech health ring" benchmark sits |
| **Scale-up** (3+ years, 50–200 eng) | 20–30% | Multi-team coordination debt, integration complexity, security hardening all compound |
| **Enterprise** (public company / regulated industry) | 25–35% | Compliance debt (SOC 2, GDPR, HIPAA), multi-tenant isolation, long-lived API versions, and customer SLAs all require continuous investment independent of feature work |

**Reference point:** Spotify's 20% "tech health ring" is the most widely cited benchmark, but Spotify is a mid-scale-up company — enterprise PMs in regulated industries should expect to allocate more, not less.

**✓ Recommendation:** Pick the band for your stage, negotiate it as a fixed percentage upfront in roadmap planning, and protect it from discretionary cuts when features slip. Treating technical investment as protected capacity is the only way to prevent debt from compounding indefinitely. If your stage crosses a threshold (Series A → Series B, pre-SOC-2 → post-SOC-2), revisit the allocation — debt math changes with scale.

---

### Decision 2: How do you prioritize which debt to address?

Not all debt is equal. Use this triage framework:

| Priority | Criteria | Concrete threshold | Example |
|---|---|---|---|
| **Do now** | Blocks roadmap, causes user-facing degradation, or creates security risk | Estimate variance >50% due to debt; Core Web Vital below passing threshold; known CVE (security vulnerability) | 2.5MB bundle on login page |
| **Plan next quarter** | Slows velocity but has workarounds | Feature delivery taking >30% longer than baseline due to area complexity; >2 unrelated bugs traced to same debt area in one quarter | 27 Redux slices initialized globally |
| **Track & monitor** | Exists but isn't impacting delivery | No measurable velocity impact; no user-facing symptoms | Undocumented legacy modules |
| **Tolerate** | In systems with no planned features | Area untouched for 12+ months; no roadmap items in next two quarters | Old admin tools with no planned features |

**The key question:** Is this debt blocking something on the roadmap?
- **Yes** → It's a roadmap item
- **No** → It stays in the backlog

---

### Decision 3: How do you make the case for debt work to non-technical stakeholders?

The most common PM frustration: engineering wants to address debt, stakeholders want features, and you're in the middle.

**The debt case requires business language:**

- **Speed:** "These 3 debt items are adding ~40% to the time it takes to ship any dashboard feature. Addressing them this quarter gets that capacity back for the rest of the year."

- **Risk:** "The 0% test coverage on the checkout flow means we ship bugs into payments ~2x per quarter. Each incident requires emergency engineering time and customer support escalation."

- **Cost:** "The 2.5MB bundle is increasing bounce rate by an estimated X% on mobile. At our current traffic, that's Y sessions lost per month."

**✓ Recommendation:** Always pair a debt request with a business outcome.

| Instead of | Use |
|---|---|
| "Refactoring the Redux store" | "Reducing feature delivery time by 30% for all dashboard work this year" |

---

### Decision 4: When is it better to rewrite vs. refactor?

| Approach | Definition | Risk Profile | Timeline |
|---|---|---|---|
| **Rewrite** | Start from scratch with new design | Higher risk, potentially higher reward | Longer |
| **Refactor** | Incrementally improve existing code | Lower risk, avoids "big bang" failure | Ongoing |

**Common tension:** PM instinct favors rewrites (clean slate). Engineering favors refactoring (rewrites have a history of exceeding time and budget).

**✓ Recommendation:** Default to incremental refactoring unless the current system is so architecturally broken that building on it is actively more dangerous than starting over.

**Example:** BrightChamps bundle strategy — don't rewrite the entire frontend, but implement a route-based 4-tier bundle strategy incrementally, starting with the highest-impact routes.

---

### Decision 5: How do you handle debt discovered mid-feature delivery?

**The problem:** Engineering discovers unexpected debt while building a feature. Scope expands. Estimate doubles.

**Two paths forward:**

**1. Debt is scopable independently**  
Add it to the roadmap as its own item with its own estimate. This makes the work visible and allows proper prioritization.

**2. Debt is tightly coupled to the feature**  
You literally can't ship the feature without fixing it first. Accept the expanded scope and reset stakeholder expectations with specific reasoning:

> "We discovered X during implementation. X adds Y days. Here's why we can't ship the feature without addressing it."

**✓ Recommendation:** Always separate debt from feature scope when possible. Make the work visible rather than hiding it inside a feature estimate.

## W3 — Questions to ask your engineer

**Quick Reference:** These six questions help you distinguish between manageable debt and blocking issues before sprint commitment. Each reveals a different dimension of technical debt risk.

---

### "What's the debt situation in the area we're about to build in?"

*What this reveals:* Whether there are hidden costs in the upcoming feature. Engineers who've worked in a codebase for a while often have immediate intuition about which parts are clean and which are "here there be dragons." Asking before sprint commitment prevents surprises.

---

### "If we did nothing about this debt, what would happen in 6 months?"

*What this reveals:* The interest rate on this specific debt. Some debt compounds fast (performance issues get worse with more traffic), some is stable (old admin tools that nobody touches). The answer calibrates urgency.

---

### "What's the minimum debt we'd need to address before starting this feature?"

*What this reveals:* Whether there's a way to scope the feature without a full debt cleanup. Often engineering can work around debt for a single feature — the cost is time, and the question is whether that's acceptable.

---

### ⚠️ "Is this debt creating security or compliance risks?"

*What this reveals:* Whether there are non-negotiable urgency signals. Security and compliance debt is categorically different from performance debt — it has a deadline imposed by external actors (regulators, security incidents), not by roadmap prioritization.

---

### "What's the right shape for addressing this — quick win, refactor, or rewrite?"

*What this reveals:* The cost structure of the fix.

| Shape | Cost | Timeline | Impact |
|-------|------|----------|--------|
| Quick win | Low | Days | High |
| Refactor | Medium | Weeks | Medium |
| Rewrite | High | Months | High risk |

Understanding the shape before committing helps you make roadmap tradeoffs.

---

### "How would we know when this debt is addressed — what does done look like?"

*What this reveals:* Whether the debt work has a clear end state or is open-ended.

> **Clear scope example:** "Reduce initial JavaScript bundle from 2.5MB to under 1.5MB, verified by Lighthouse CI in the build pipeline"

> **Unclear scope example:** "Improve the code quality"

## W4 — Real product examples

### BrightChamps — Frontend performance debt quantified and staged

**What:** 49-route student dashboard loaded a single 2.5MB JavaScript bundle globally.

**How it got there:** Early in the product's life the frontend had 3 routes and building route-based code splitting was over-engineering. The team shipped a single bundle and added routes incrementally over 18 months. No one decision created the 2.5MB bundle — it was 40+ feature shipments, each adding 40–80KB, compounding. By the time the bundle was audited, no single route owner felt responsible; the debt belonged to "the architecture" rather than a specific team.

**Why:** The architectural choice made sense at 3 routes (YAGNI — don't build what you don't need). It became a user-facing problem at 49 routes because login-page users were paying to download code for the other 48 routes they'd never visit.

**The PM insight:** Quantifying debt changes how it's prioritized. And — more importantly — debt that was born from correct early decisions still needs to be paid down once the scale changes. "We didn't make a mistake" isn't a defense; "we haven't updated for the new scale" is the actual diagnosis.

| Problem statement | Classification | Result |
|---|---|---|
| "Our login page loads 2.5MB of JavaScript" | Engineering issue | Deprioritized |
| "Our login page loads 2.5MB of JavaScript, causing slow loads for returning users and decreasing return conversion" | Product priority | Funded |

**Optimization roadmap:**

| Phase | Scope | Timeline | Rationale |
|---|---|---|---|
| Quick wins | Lottie animation compression, DevTools removal, language file dynamic loading | 1 week | Lowest risk, highest visibility |
| Architectural fix | Bundle splitting by route tier | Month 1 | Root cause resolution |

**Takeaway:** Quick wins first maintains momentum and demonstrates value while larger work progresses.

---

### Spotify — Tech health as a protected budget

**What:** Spotify allocates a fixed percentage of engineering capacity to "tech health" work (codebase maintenance and improvement) separate from feature delivery.

**Why:** This allocation is protected—not cut during sprint overruns or negotiated away by stakeholder pressure.

**The business case:**

| Scenario | Velocity impact | Outcome |
|---|---|---|
| No explicit technical investment | −10–15% per quarter | Compounding slowdown |
| 20% ongoing technical capacity | Maintained | Stable delivery |
| Reactive debt management (100% feature focus) | Crisis mode | Firefighting cycles |

⚠️ **Critical risk:** Without deliberate PM advocacy for protected technical capacity, delivery pressure will always win. By the time debt becomes a crisis, remediation costs compound exponentially.

**Takeaway:** Budget protection is the only reliable defense against debt accumulation.

---

### Stripe — API versioning as debt management

**What:** Stripe maintains every historical API version to avoid breaking changes that would damage developer trust.

**Why:** This creates permanent maintenance surface area—a deliberate, self-imposed debt.

> **Deliberate debt vs. accidental debt:** Some debt is a product strategy decision, not a technical failure. Stripe chose to carry version maintenance debt rather than force breaking changes on customers.

**Takeaway:** Understand what you're getting in exchange for carrying debt. Dedicate first-class engineering capacity (team + budget) to manage it.

---

### Airbnb — The true cost of undocumented systems

**What:** Critical infrastructure was documented only in engineers' heads. When those engineers left, the company faced months of reverse-engineering or complete rebuilds.

**Why:** Documentation debt remains invisible until knowledge gaps appear.

⚠️ **Hidden cost:** Months of rework vs. the cost of documenting during initial shipment—a stark asymmetry that compounds with every engineer departure.

**PM standard for "done":**

- ✅ Working code
- ✅ Documented architecture
- ❌ Incomplete delivery (missing docs) creates exponential future costs

**Takeaway:** Treat documentation as a first-class deliverable, not an afterthought.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

> **Technical Debt:** Accumulated shortcuts, compromises, and deferred work in code that compounds over time, making future changes slower and more expensive.

### Debt is invisible until it's a crisis — and crises have catastrophic timing

Performance debt doesn't announce itself. The app gets 10% slower per month — slow enough that no single day feels different, fast enough that users notice over time. By the time leadership identifies "the app is slow" as a real problem, the debt has compounded to the point where addressing it takes months of engineering capacity.

**The PM's blindspot:**  
The PM who waits for the crisis to surface debt has lost the ability to address it cheaply.

**The discipline:**
- Quarterly audits
- Engineering retrospectives
- Performance monitoring

*Surface debt systematically before the crisis forces the issue.*

---

### "We'll deal with it later" is a self-perpetuating trap

| Deferral Area | What Compounds |
|---|---|
| New features | Become harder to ship |
| Bug fixes | Become more frequent |
| Team morale | Engineers get frustrated |
| Refactoring | Requires higher skill to do safely |

Teams that consistently defer debt accumulate organizational inertia against addressing it — because by the time it's critical, fixing it means stopping feature work, which creates stakeholder pressure to keep shipping instead.

**The paradox:**
- You need velocity to justify addressing debt
- But debt is the reason you have low velocity

**Breaking out requires:**
- Explicit PM advocacy
- Stakeholder education

---

### Debt tradeoffs made in crisis mode are usually wrong

When a performance incident forces an emergency, engineering makes fast decisions under pressure:

- ❌ The wrong fix gets applied
- ❌ Architectural shortcuts are taken to restore service quickly
- ❌ New layer of technical compromise gets left behind

⚠️ **Emergency cleanup debt:** Crisis response creates new debt that needs dedicated attention — not just one fix cycle, but a dedicated cleanup sprint addressing root causes, not symptoms.

**Your role in crisis debt management:**
- Resist declaring victory when service is restored
- Plan the cleanup sprint that addresses the *root cause*, not the symptom

---

### Engineering burnout is a debt signal

Engineers who spend most of their time fighting the codebase rather than building new things burn out faster.

**When attrition spikes and exit interviews reference:**
- Frustration with the codebase
- Constant context-switching between features and firefighting
- Inability to take pride in their work

…technical debt is destroying organizational capacity.

⚠️ **Hidden attrition cost:** Not just replacement hiring — it's the knowledge that leaves with each departing engineer. PMs who treat debt as purely a technical concern miss this signal until it becomes an attrition crisis.

---

### AI-era debt: a new category PMs should track separately

LLM-powered features create categories of debt that didn't exist before 2023, and PMs who treat AI code like normal backend code underestimate how fast it compounds.

| AI debt type | What it is | How it bites |
|---|---|---|
| **Prompt debt** | Prompts hardcoded in application code with no version control, no A/B test harness, no output quality tests. Every change is a blind deploy. | Regression risk on every prompt edit; no way to attribute quality changes to prompt vs. model changes; rollback means finding the old string in git history |
| **Context window debt** | Retrieval logic stitched together ad-hoc (concatenate top-k chunks, truncate to fit). No retrieval evaluation. Quality depends on hidden embedding model drift. | Silent quality degradation as the knowledge base grows; debugging requires tracing retrieval + generation + re-ranking separately |
| **Model version debt** | Pinning to `gpt-4` or `claude-3-opus` without a migration plan. When the provider deprecates, you have 30–90 days to re-test everything downstream. | Forced upgrade cycles at vendor's pace, not yours; output schema drift between versions; cost-per-token changes break unit economics |
| **Inference cost debt** | Shipping features that hit the model on every user interaction with no caching, no batching, no fallback tier. | COGS line grows linearly with usage; successful feature = budget crisis; no circuit breakers when usage spikes |
| **Eval debt** | No automated quality eval pipeline for model outputs. "It looks good in testing" is the only QA. | Regressions ship silently; no ground truth to improve against; subjective quality arguments between PM / eng / users with no data |

**What's different about AI debt:** Normal technical debt compounds over months. Prompt and model-version debt can compound in *weeks* — a single model provider deprecation notice can invalidate quarters of PM work. The PM response is to demand a standing eval harness before shipping the first AI feature, not after the second incident.

**The shift in the last 2 years:** Pre-2023, PMs managed AI debt by talking to ML engineers about model retraining cycles. Post-2023, LLM features are built by backend engineers with no ML background, using vendor APIs. This means AI debt now sits inside product teams, not ML platform teams — and PMs are on the hook for managing it directly.

## S2 — How this connects to the bigger system

> **Technical Debt (in roadmap context):** debt that is actively blocking roadmap items, making it prioritizable rather than infinitely deferrable

Technical debt relevance is determined by roadmap impact, not codebase severity alone. The BrightChamps bundle size debt became actionable the moment it blocked perceived performance on new features.

| Debt Type | Impact | Priority |
|-----------|--------|----------|
| Blocking next 3 roadmap items | Emergency | Immediate |
| Blocking 1 current item | High | Current sprint |
| Not blocking anything | Background noise | Defer or eliminate |

---

### Monitoring and Alerting (03.09) — Early Detection

> **Performance Debt Detection:** visible metrics in CI/CD pipeline that flag debt before it becomes expensive

**What PMs can own:**
- Lighthouse CI integration
- Bundle size budgets in CI/CD
- LCP (Largest Contentful Paint) tracking

⚠️ **Without monitoring infrastructure, debt remains invisible until expensive to fix.**

---

### Infrastructure as Code (03.05) — Debt Prevention

> **Infrastructure as Code (IaC):** infrastructure defined in code rather than manual configuration, making state visible and version-controlled

**Why this matters for debt:**

| Configuration Method | Visibility | Debt Characteristics |
|---|---|---|
| Manual configuration | Hidden | Invisible debt; fragile until knowledge holder leaves |
| Code-based (IaC) | Transparent | Legible, changeable, version-tracked debt |
| **Outcome** | — | **IaC transforms opaque systems into maintainable ones** |

---

### Feature Flags (03.10) — Incremental Risk Reduction

> **Feature Flags (for refactoring):** infrastructure enabling parallel old/new implementation runs with staged traffic routing

**Safe refactoring pattern:**

1. Run old and new implementations in parallel
2. Route small traffic percentage to refactored version
3. Measure performance and stability
4. Expand percentage incrementally

⚠️ **Without feature flags, teams face a false choice:** ship refactor to everyone (risky) *or* don't refactor (debt compounds)

---

### Release Management (05.10) — Staged Debt Work

Debt-related engineering sprints require different release discipline than feature work.

**Bundle size refactor example requires:**
- Staged rollout (not all traffic at once)
- Performance monitoring during rollout
- Rollback capability if regressions appear

⚠️ **Careful refactoring can become a production incident without proper release management applied to debt work.**

## S3 — What senior PMs debate

### Should PMs own the technical health metric or is that engineering's domain?

| Perspective | Position | Implication |
|---|---|---|
| **Engineering-owned** | Technical health metrics (bundle size, test coverage, MTBF, deployment frequency) are engineering KPIs that PMs respect but don't manage | PM creates space for health work; engineering sets targets |
| **PM-owned** | PMs who don't track technical health don't understand true team capacity | Checkout at 0% test coverage = product risk, not just engineering risk; informed roadmap decisions require this visibility |

**The practical synthesis:**

PMs don't need to own the metrics, but must understand them well enough to make informed tradeoffs. A PM unaware of:
- Application bundle size
- Team deployment frequency  
- Test coverage on critical paths

…is making roadmap decisions without key constraints.

---

### Is the 20% technical health allocation universally right?

> **Technical health allocation:** The percentage of engineering capacity dedicated to debt paydown, refactoring, and codebase maintenance (as opposed to feature work).

**The Spotify 20% model is a starting point, not a prescription:**

| Scenario | Context | Appropriate allocation |
|---|---|---|
| **Startup** | 3 people, clean recent code, minimal debt | <20% |
| **Growth stage** | Scaling codebase, increasing team friction | ~20% |
| **Legacy enterprise** | 10+ years old, 15 engineers navigating accumulated decisions | 30–40%+ |

**Better metric: velocity trends**

Track velocity quarter over quarter:
- ✅ Stable or increasing velocity = technical investment is calibrated
- ⚠️ Declining velocity = underinvesting in health

The correct allocation is the one that **maintains or improves delivery velocity over time**—and that number varies by company age, codebase maturity, and team growth rate.

---

### How is AI changing the economics of technical debt?

AI coding tools (GitHub Copilot, Cursor) are rewriting the cost structure of debt work in both directions:

**Accelerating debt paydown:**
- Identifying and fixing debt categories faster
- Replacing deprecated dependencies
- Adding test coverage
- Suggesting refactoring patterns
- *Example:* Tasks that took a senior engineer a week now take a day

**Introducing new debt forms:**
- Generated code that passes tests but breaks architectural consistency
- Duplicated logic a human engineer would have recognized as existing
- Patterns that work but aren't maintainable by developers unfamiliar with the generation method

⚠️ **PM responsibility shift, not elimination:**

AI doesn't remove technical debt as a management concern—it **changes where debt originates**. Critical disciplines remain:
- Auditing generated code for architectural consistency
- Maintaining strong engineering standards for code "done"-ness
- Keeping technical quality metrics visible

The nature of the work shifts but the management responsibility doesn't.