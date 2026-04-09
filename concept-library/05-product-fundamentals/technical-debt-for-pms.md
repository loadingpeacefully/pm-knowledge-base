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

A 3-month renovation becomes 9 months. You're living in a construction zone the whole time.

### How Technical Debt Works in Code

Technical debt follows the same pattern:

| What Happens | Why It Matters |
|---|---|
| Workarounds made sense when created | They seemed like safe, temporary shortcuts |
| They accumulate over time | New features must understand and work around old workarounds |
| Onboarding slows down | New developers must decode the codebase before contributing |
| Bugs appear unexpectedly | Systems that should be independent are tangled together |

### What PMs Actually Need to Know

⚠️ **Your job is NOT to fix technical debt.** Your job is to:

1. **Recognize when debt is slowing your roadmap**
2. **Build the business case for addressing it**
3. **Prioritize debt work vs. feature work**

These are product decisions, not engineering decisions.

## F3 — When you'll encounter this as a PM

| Signal | What it means | PM action |
|--------|--------------|-----------|
| **Estimates keep being wrong** | Engineering consistently needs twice as long as estimated. Debt requires extra work *before* the feature can start. | Investigate whether scope estimates are missing pre-work phases |
| **Bugs appear in unexpected places** | Fixing one bug causes bugs elsewhere. Systems are more entangled than they should be. | Probe for hidden coupling; ask engineering which areas are tightly connected |
| **"Small" changes take a long time** | A UI text change requires 2 weeks; a new integration requires rewriting unrelated code. Work is out of proportion to scope. | Challenge the scope disconnect; map which systems need touching |
| **Engineering requests a "cleanup sprint"** | Engineers ask for infrastructure time instead of features. Debt is blocking their ability to ship. | Treat as critical signal requiring a *product decision*, not automatic approval or rejection |
| **Planning a major new feature** | You're about to touch a significant area of the codebase. | Assess technical debt in that area *before* committing. Prevents mid-delivery surprises and improves estimate accuracy. |
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Types of technical debt

Not all technical debt is the same. As a PM, understanding the categories helps you prioritize which debt to address and when:

| Type | What it is | Business impact | Example |
|---|---|---|---|
| **Performance debt** | Code that works but runs slowly or inefficiently | Direct user experience harm; conversion and retention damage | All 49 routes loading a 2.5MB bundle when the login page needs ~300KB |
| **Architectural debt** | Systems built for one scale that don't support the current or needed scale | Makes new features slow and risky to build | 27 Redux slices initialized on every page regardless of context |
| **Dependency debt** | Outdated or duplicated libraries and packages | Security vulnerabilities; compatibility issues with new features | Duplicate react-query dependency; moment.js when date-fns is leaner |
| **Test debt** | Missing or inadequate automated tests | Every change requires manual verification; bugs ship undetected | No automated tests on checkout flow |
| **Documentation debt** | Undocumented systems that only a few engineers understand | Onboarding cost; bus-factor risk (critical knowledge in one person's head) | Undocumented data model for legacy course migration |

### BrightChamps — Student dashboard performance audit

**What:** A deliberate audit of the `champ.brightchamps.com` student dashboard uncovered significant performance debt as the product scaled.

**Why:** Silent debt compounds undetected until it becomes a crisis. Users experience it as "the app is slow," but no single event triggers visibility.

**Critical severity findings:**
- All 49 routes load the same 2.5MB JavaScript bundle
  - Login page (new user entry point) loads full dashboard code
  - Only needs ~300KB for authentication
  - *Analogy:* Building a 50-room mansion and making every visitor walk through every room to reach the front door
- 1.3MB Lottie animation file (`confetti_animation`) loads globally on pages that never play it

**High severity findings:**
- `moment.js` (date formatting library) used instead of `date-fns`
  - Same functionality, 5× larger
  - Opportunity: save 200KB
- ReactQuery DevTools (development-only tool) loading in production builds
- 27 Redux slices initialized on every page
  - Most pages need only 2–3 slices

**Quantified debt:**
| Metric | Current | Target | Gap |
|---|---|---|---|
| Total initial load | 2.5MB | <1.5MB | 1MB unnecessary code per pageview |

**Takeaway:** PMs who surface audits proactively prevent debt from compounding into crisis. This debt was silent—discovered through deliberate measurement, not failure.

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
| "The bundle size is causing LCP failures" | "First meaningful content appears 2 seconds later for users on average mobile connections" | 2 seconds = Y% conversion drop *(Google research: 53% of mobile users abandon after 3 seconds)* |
| "We have 0% test coverage on checkout" | "Every checkout change requires 2 days of manual QA and still ships bugs" | 2 days per change × 4 changes/month = 8 days QA overhead + bug risk |

> **Best practice:** Always communicate debt in business terms: shipping speed, user experience, or business outcomes—not "the code is messy."

### The optimization roadmap structure

The BrightChamps audit organized debt fixes into a two-horizon roadmap:

**Horizon 1 — Quick wins** *(high impact, low risk)*
- Compress/replace top 5 Lottie animation files → saves >2MB
- Move language files to dynamic loading → saves >400KB
- Remove duplicate dependency and replace moment.js → saves ~200KB
- Remove ReactQuery DevTools from production → immediate improvement
- **Timeline:** 3–5 engineering days
- **Result:** Majority of performance gain achieved quickly

**Horizon 2 — Architectural fixes** *(high impact, higher risk)*
- Route-based 4-tier bundle strategy:
  - Tier 1: ~300KB (auth only)
  - Tier 2: ~800KB (lightweight)
  - Tier 3: ~1.5MB (full dashboard)
  - Tier 4: ~1.2MB (specialized)
- Redux store splitting → multiple store configurations per context
- Context optimization → lightweight pages skip heavy contexts
- **Timeline:** 3–4 engineering weeks
- **Result:** Eliminates root cause, prevents recurrence

> **Sequencing principle:** Quick wins first (build confidence, show progress, deliver immediate user benefit), then architectural work (addresses root cause, prevents future debt).

## W2 — The decisions this forces

### Decision 1: How much capacity should go to debt vs. features?

> **Technical Debt Interest Rate:** Spending 0% on debt causes velocity to decline ~10–15% per quarter. Spending 20% maintains velocity. Spending 30%+ improves it.

There's no universal right answer, but the typical range is **15–25% of engineering capacity** reserved for technical work, including debt, performance, security, and infrastructure.

**Reference point:** Spotify's 20% "tech health ring" is a well-known benchmark.

| Debt Investment | Velocity Outcome |
|---|---|
| 0% | Declines 10–15% per quarter |
| 20% | Maintained |
| 30%+ | Improves |

**✓ Recommendation:** Negotiate a fixed percentage (15–20%) for technical health upfront in roadmap planning — not as a discretionary budget that gets cut when features slip. Treating technical investment as protected capacity is the only way to prevent debt from compounding indefinitely.

---

### Decision 2: How do you prioritize which debt to address?

Not all debt is equal. Use this triage framework:

| Priority | Criteria | Example |
|---|---|---|
| **Do now** | Blocks roadmap, causes user-facing performance degradation, or creates security risk | 2.5MB bundle on login page |
| **Plan next quarter** | Slows velocity significantly but has workarounds | 27 Redux slices initialized globally |
| **Track & monitor** | Exists but isn't actively causing pain | Undocumented legacy modules |
| **Tolerate** | In systems that won't be touched again | Old admin tools with no planned features |

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

1. **Debt is scopable independently**  
   Add it to the roadmap as its own item with its own estimate. This makes the work visible and allows proper prioritization.

2. **Debt is tightly coupled to the feature**  
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
>
> **Unclear scope example:** "Improve the code quality"

## W4 — Real product examples

### BrightChamps — Frontend performance debt quantified and staged

**What:** 49-route student dashboard loaded a single 2.5MB JavaScript bundle globally.

**Why:** The architectural choice made sense at initial scale but became a user-facing problem as the product grew.

**The PM insight:** Quantifying debt changes how it's prioritized.

| Problem statement | Business impact |
|---|---|
| "Our login page loads 2.5MB of JavaScript" | Engineering issue |
| "Our login page loads 2.5MB of JavaScript, causing slow loads for returning users and decreasing return conversion" | Product priority |

**Optimization roadmap:**

1. **Quick wins (1 week)** — Lowest risk, highest visibility
   - Lottie animation compression
   - DevTools removal
   - Language file dynamic loading

2. **Architectural fix (Month 1)** — Root cause
   - Bundle splitting by route tier

**Takeaway:** Quick wins first maintains momentum and demonstrates value while larger work progresses.

---

### Spotify — Tech health as a protected budget

**What:** Spotify allocates a fixed percentage of engineering capacity to "tech health" work (codebase maintenance and improvement) separate from feature delivery.

**Why:** This allocation is protected—not cut during sprint overruns or negotiated away by stakeholder pressure.

**The business case:**

- Teams *without* explicit technical investment lose 10–15% delivery velocity per quarter
- A 20% ongoing investment maintains constant velocity
- Reactive debt management (100% feature capacity) leads to crisis firefighting

**Takeaway:** ⚠️ Without deliberate PM advocacy for protected technical capacity, delivery pressure will always win. By the time debt becomes a crisis, remediation costs compound.

---

### Stripe — API versioning as debt management

**What:** Stripe maintains every historical API version to avoid breaking changes that would damage developer trust.

**Why:** This creates permanent maintenance surface area—a deliberate, self-imposed debt.

**The PM insight:** 

> **Deliberate debt vs. accidental debt:** Stripe chose to carry version maintenance debt rather than force breaking changes on customers. Some debt is a product strategy decision, not a technical failure.

**Takeaway:** Understand what you're getting in exchange for carrying debt. Dedicate first-class engineering capacity (team + budget) to manage it.

---

### Airbnb — The true cost of undocumented systems

**What:** Critical infrastructure was documented only in engineers' heads. When those engineers left, the company faced months of reverse-engineering or complete rebuilds.

**Why:** Documentation debt remains invisible until knowledge gaps appear.

⚠️ **The cost:** Months of rework vs. the cost of documenting during initial shipment.

**The PM role:**

- Treat documentation as a deliverable, not an afterthought
- "Done" = working code + documented architecture
- Without this standard, documentation debt accumulates with every feature shipped

**Takeaway:** Accepting incomplete delivery (no docs) creates exponential future costs.
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

Surface debt systematically *before* the crisis forces the issue.

---

### "We'll deal with it later" is a self-perpetuating trap

| Each week deferred | Compounding cost |
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

⚠️ **The cleanup debt:** Emergency response creates new debt that needs to be addressed in the aftermath — not just one fix cycle, but a dedicated cleanup sprint.

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

⚠️ **The hidden cost:** Not just replacement hiring — it's the knowledge that leaves with each departing engineer. PMs who treat debt as purely a technical concern miss this signal until it becomes an attrition crisis.

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
- Manual configuration = invisible debt (fragile until knowledge holder leaves)
- Code-based configuration = legible, changeable, version-tracked debt
- IaC transforms opaque systems into maintainable ones

---

### Feature Flags (03.10) — Incremental Risk Reduction

> **Feature Flags (for refactoring):** infrastructure enabling parallel old/new implementation runs with staged traffic routing

**Safe refactoring pattern:**
1. Run old and new implementations in parallel
2. Route small traffic percentage to refactored version
3. Measure performance and stability
4. Expand percentage incrementally

⚠️ **Without feature flags, teams face false choice:** ship refactor to everyone (risky) *or* don't refactor (debt compounds)

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