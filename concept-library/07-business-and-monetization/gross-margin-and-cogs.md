---
lesson: Gross Margin & COGS
module: 07 — business and monetization
tags: business
difficulty: working
prereqs:
  - 07.01 — Unit Economics: gross margin is one of the three pillars of unit economics alongside CAC and LTV
  - 07.02 — Pricing Models: pricing model choice determines both revenue structure and which costs belong in COGS
writer: cfo-finance
qa_panel: CFO/Finance Lead, GTM Lead, Junior PM Reader
kb_sources:
  - performance-reviews/apr24-mar25-performance-review.md
  - technical-architecture/payments/package-and-payments.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, head of product, AI-native PM
status: ready
last_qa: 2026-04-09
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

A product team shipped a live video feature — persistent video streams so users could have longer real-time sessions. Engagement doubled. DAU went up. The product team celebrated.

Three months later, the CFO asked why infrastructure costs had doubled. The feature had required 2× the server and streaming capacity. Every extra minute of session time cost the company money in compute and bandwidth. Revenue was flat because longer sessions didn't translate into purchases — users were happily using the feature without paying more for it. The PM had made the right product decision for engagement but had never asked "what does this cost per user?" The product that was "winning" on engagement metrics was destroying the company's economics.

The PM decision that would have changed the outcome: before shipping the live video feature, ask "what is the variable cost per active minute of this feature, and does our pricing cover it?" If a user watches 30 extra minutes per month and that costs $0.50 in compute, the feature only makes sense if it improves conversion by enough to cover that $0.50 COGS addition per user.

This happens constantly — not because PMs are careless, but because the connection between product decisions and financial outcomes isn't visible without understanding a specific part of the income statement.

Gross margin is that connection. Every product decision — what features to build, how to price a package, whether to use AI to automate content creation or hire humans, whether to build payment infrastructure or use a third-party gateway — moves the gross margin line. PMs who don't understand gross margin are making consequential financial decisions without knowing it.

The shift happens when a PM starts asking about costs alongside outcomes. "Engagement doubled" becomes "engagement doubled and here's what it cost us to deliver that engagement." That's the difference between a PM who ships features and a PM who builds sustainable products.

## F2 — What it is, and a way to think about it

> **Revenue:** The total amount customers pay your company for your product or service. For BrightChamps: the price of class packages sold.

> **COGS (Cost of Goods Sold):** The direct costs of delivering your product to a specific customer. These are costs that exist because you made a sale — they wouldn't exist without that sale. For BrightChamps: teacher pay per class, content delivery infrastructure, payment processing fees.

> **Gross profit:** Revenue minus COGS. What's left after you've paid for delivering what you sold.

> **Gross margin:** Gross profit as a percentage of revenue. `(Revenue - COGS) / Revenue × 100`. A 60% gross margin means for every $100 in revenue, $40 went to directly deliver the product and $60 is available for everything else (salaries, marketing, R&D, profit).

### A way to think about it

**The restaurant analogy:**
- Revenue = what customers pay for meals
- COGS = cost of ingredients in each dish
- Gross profit = what's left after ingredients
- Gross margin = that remainder as a percentage of revenue

The restaurant still pays chefs' salaries, rent, marketing, and management — but those are separate from COGS. Gross margin tells you how efficiently the restaurant converts each sale into money available to run the rest of the business.

**In product terms:**
- **Adding variable costs per user** (more server compute, more teacher time, more content creation) → increases COGS
- **Reducing variable costs per user** (AI content automation, infrastructure optimization, self-service features replacing support calls) → improves gross margin

### What goes into COGS for different product types

| Product type | Typical COGS components | What DOESN'T go in COGS |
|---|---|---|
| **Pure SaaS** (software only) | Cloud hosting per user, payment processing fees | Engineering salaries, marketing, office costs |
| **EdTech** (live instruction) | Teacher/tutor pay, content delivery costs, payment processing | Admin staff, sales, curriculum R&D |
| **E-commerce** | Product cost, fulfillment, payment processing | Warehouse fixed costs, marketing, corporate overhead |
| **Marketplace** | Infrastructure per transaction, payment processing, fraud prevention | Platform R&D, customer support staff, sales |

## F3 — When you'll encounter this as a PM

| Context | What happens | What gross margin tells you |
|---|---|---|
| **New feature proposal** | Team wants to build a live tutoring feature | Does the cost to deliver this feature (teacher time, infrastructure) justify the price customers will pay? |
| **Build vs. buy decision** | Should we build payment infrastructure or use Stripe? | Stripe takes 2.9% + $0.30 per transaction — that's a COGS impact on every payment |
| **Pricing review** | Leadership wants to know if a price increase is justified | What is the current gross margin per package, and what would a price change do to it? |
| **AI/automation investment** | Team proposes AI content generation to reduce human authoring | Will the AI cost less per unit than the human cost it replaces? |
| **New product launch** | Launching a premium add-on tier | Does this product have better or worse gross margin than the core product? Does it improve the blended margin? |
| **Investor pitch or board review** | Finance presents P&L | Gross margin benchmarks matter to investors — SaaS is expected at 70%+, marketplaces at 30–50% |

### Company — BrightChamps

**What:** Payment system with explicit cost splits per transaction

**Why:** Break down revenue into teaching/learning delivery costs vs. platform infrastructure costs to calculate accurate gross margin per package

**Takeaway:** A 10-class package selling for $120 with $60 in course_fee allocation = 50% gross margin. The `sale_payment_distributions` table separates:
- `course_fee` — teaching/learning delivery
- `platform_fee` — platform infrastructure & payment processing

This accounting foundation enables margin-based decision-making across feature launches, pricing changes, and investment decisions.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The P&L waterfall

The income statement (Profit & Loss) flows from top to bottom:

```
Revenue (what customers paid)
  − COGS (direct delivery costs)
  ─────────────────────────────
  = Gross Profit
  − Operating Expenses (salaries, marketing, R&D, G&A)
  ─────────────────────────────
  = Operating Income (EBIT)
  − Interest, taxes
  ─────────────────────────────
  = Net Income
```

> **Gross margin:** Revenue minus COGS, measured at the Gross Profit line. Everything below it (salaries, marketing, R&D, office costs) is operating expense, not COGS.

**Why this distinction matters:**
1. Gross margin is the standard comparison metric across companies and industries
2. Operating expenses vary dramatically by company stage, making gross margin more comparable
3. Gross margin reveals whether the core business model works at the unit level — whether revenue exceeds delivery cost

---

### Variable vs. fixed costs: why the distinction matters for scaling

COGS typically contains variable costs — costs that scale with each unit sold. Understanding the variable/fixed split reveals how economics change with scale.

| Cost type | Behavior at scale | Impact on gross margin as company grows |
|---|---|---|
| **Pure variable** | Grows 1:1 with revenue | Gross margin stays constant; every additional sale costs the same percentage |
| **Step-fixed** | Grows in chunks (hire a new team when volume exceeds capacity) | Gross margin dips when hiring, then improves until next threshold |
| **Infrastructure (SaaS)** | Grows slower than revenue at scale | Gross margin improves with scale — serving the 1,000th user is cheaper per-user than the 100th |

**EdTech with live instruction example (BrightChamps):**

Teacher costs are the largest COGS component and are **semi-variable** — each teacher has a fixed hourly/per-class rate, but you need more teachers as student volume grows. 

Gross margin improves through:
- Increasing students per teacher (group classes vs. 1:1)
- Reducing teacher idle time (better scheduling)
- Replacing teacher-delivered content with automated systems

---

### Contribution margin: the product-level view

> **Contribution margin:** Revenue from a specific product or feature minus the directly attributable variable costs. The product-level equivalent of gross margin.

**Gross margin vs. contribution margin:**

| Metric | What it measures | When to use it |
|---|---|---|
| **Gross margin** | Company-level: revenue minus all COGS across all products | Investor/board discussions; benchmarking against competitors; overall business health |
| **Contribution margin** | Product-level: revenue from Product X minus variable costs directly attributable to Product X | Deciding which products to grow; evaluating a new feature's ROI; understanding cross-subsidization |

**Rule of thumb:** Use gross margin when talking to investors or benchmarking; use contribution margin when making product prioritization decisions.

**What contribution margin reveals for PMs:** A company with 60% gross margin might have products with wildly different contribution margins:
- Add-on products: 80% contribution margin
- Live tutoring: 40% contribution margin  
- Premium support: 20% contribution margin

This tells you:
- Which products are subsidizing which
- Which products to prioritize for growth
- Which products' economics need to improve before they can scale

---

### BrightChamps's COGS components

| COGS category | What it includes | Variable or fixed? |
|---|---|---|
| **Teacher cost** | Per-class teacher pay (live instruction delivery) | Variable per class |
| **Content delivery** | Streaming infrastructure for class materials, platform hosting | Semi-variable (scales with active students) |
| **Payment processing** | Aggregator fees (Razorpay, Stripe, PayPal — each takes ~2–3% + fixed fee per transaction) | Variable per transaction |
| **Content creation** | Curriculum, worksheets, quiz creation (historically human-authored; shifting to AI automation) | Semi-variable (can be pre-created and reused) |
| **Customer onboarding** | Demo class delivery, trial class costs | Variable per new student |

**The content cost inflection:**

BrightChamps's performance review documents a **67% projected reduction in worksheet creation cost through AI automation**. 

*What this reveals:* Content creation costs belong in COGS for EdTech because they're a direct cost of delivering the learning product. At scale across 2,000+ worksheets, a 67% cost reduction translates directly into gross margin improvement.

---

### Gross margin benchmarks by business model

| Business model | Typical gross margin range | Why |
|---|---|---|
| Pure SaaS (no services) | 70–85% | Software has near-zero marginal cost per additional user |
| EdTech (live instruction) | 30–55% | Teacher cost is significant direct cost per class |
| EdTech (asynchronous/recorded) | 60–80% | Content created once, delivered many times |
| E-commerce | 30–50% | Physical COGS (product + fulfillment) is significant |
| Marketplace | 50–70% | Infrastructure cost per transaction is low; take rate is mostly gross profit |
| Consumer mobile apps | 60–80% | App store fees (30%) and minimal marginal infrastructure cost |

## W2 — The decisions this forces

### Decision 1: What goes into COGS vs. OpEx?

This is both a financial accounting decision and a product clarity decision.

> **Rule:** Costs that exist because you made a specific sale go into COGS. Costs that exist whether or not you made a sale are OpEx.

**Borderline cases PMs encounter:**

| Cost | Classification | Reasoning |
|---|---|---|
| Customer support for a specific product feature | Usually COGS (if required to deliver value) or OpEx (if general support) | Depends on whether support is part of the product promise |
| Infrastructure serving all products | OpEx (allocate by usage if needed) | Not specific to one sale |
| Teacher time for a specific class | COGS | Directly enables delivery of that class |
| Teacher training and certification | OpEx | Enables future delivery, not a specific sale |
| Payment gateway fees | COGS | Incurred per transaction |
| Payment infrastructure engineering | OpEx | R&D/engineering investment |
| Content creation (curriculum) | COGS (direct attribution) or OpEx (R&D) | Depends on whether content is sold directly or supports sales |

---

### Decision 2: How to assess the gross margin impact of a new feature

Before building any feature with a variable cost per user, estimate the gross margin impact:

**Step 1: Estimate variable cost per user per period**
- Ask your infrastructure team: "What additional compute, storage, or bandwidth does this require per active user per month?"
- For content features: Cost per user = creation cost ÷ number of users
- For AI features: Get inference cost per session/request from your ML infrastructure team at current token prices
- **Target format:** "$X in additional compute per active user per month"

**Step 2: Calculate cost at projected scale**
- Example: "At 10,000 MAU, this feature adds $X × 10,000 per month to COGS"

**Step 3: Identify the revenue connection**
- "This feature reduces churn by 5% — what is that worth in LTV?"

> **LTV formula:** (Monthly revenue per user) × (1 ÷ monthly churn rate)
> 
> **Example:** $20/month ARPU ÷ 10% churn = $200 LTV
> 
> After 5% churn reduction: $20/month ÷ 5% churn = $400 LTV
> 
> **Delta:** $200 LTV gain per user

**Step 4: Calculate margin impact**
- Does the feature pay for itself through reduced churn, increased conversions, or price increase justification?
- If feature costs $2/user/month and reduces churn by 5% (worth $200 LTV improvement), how many users need improved retention to justify the ongoing COGS addition?

**The critical PM question:**
> "Can we monetize this feature's value at a price that exceeds its COGS, or are we subsidizing user experience at a margin loss?"

---

### Decision 3: Build vs. buy from a gross margin lens

Every build vs. buy decision is a COGS decision:

| Option | COGS impact | When to choose |
|---|---|---|
| **Build internally** | COGS = infrastructure cost only (once built); high upfront OpEx (engineering time) | When volume is high enough that third-party fees exceed amortized build cost |
| **Buy / use third-party** | COGS = per-transaction or per-user fee | When volume is low, or when third-party specialization reduces COGS |

**Example: BrightChamps payment gateway**

**Third-party option (Razorpay):**
- Fee: ~2% per transaction
- Average transaction: ₹5,000 (10-class package)
- Monthly volume: 2,000 transactions
- **Monthly COGS:** 2% × ₹5,000 × 2,000 = **₹200,000**

**Build internally:**
- Upfront build cost: 4 engineer-months × ₹150,000/month = **₹600,000**
- Ongoing COGS (infrastructure only): ~₹2 per transaction = **₹4,000/month**
- Monthly COGS saving: ₹200,000 − ₹4,000 = **₹196,000**
- **Payback period: ~3 months** ✓ Compelling

**Same scenario at early stage (200 transactions/month):**
- Same upfront cost: ₹600,000
- Monthly saving: ₹19,600
- **Payback period: 31 months** ✗ Doesn't make sense

> **Rule of thumb:** Build your own infrastructure component when the annual COGS saving exceeds 2× the build cost. Below that threshold, buy.

---

### Decision 4: The cost vs. quality tradeoff in content delivery

For EdTech, content quality directly affects product value but also affects COGS.

**Human authoring vs. AI automation:**

| Approach | COGS per worksheet | Quality characteristics | Scalability |
|---|---|---|---|
| Human curriculum author | High (hourly rate, review cycles) | Nuanced, pedagogically optimized, error-checked | Limited by author capacity |
| AI-generated (with human review) | ~67% lower | Good for standard problem types; requires validation for complex content | Scales to 2,000+ worksheets |
| AI-generated (no review) | Lowest | High error risk; pedagogical gaps possible | Unlimited but quality uncertain |

**The PM decision:** Which quality level is required for which use case, and what is the gross margin implication of each choice?

*Example:* BrightChamps chose AI + human review as the tier reducing COGS by 67% while maintaining acceptable quality.

---

### Decision 5: Gross margin by product line — what to prioritize

Not all products have the same gross margin. Understanding margin structure reveals which products can fund others:

| Product line | Gross margin profile | Strategic implication |
|---|---|---|
| Core class packages (live 1:1 tutoring) | Lower margin | Volume business; needs scale for profitability |
| Group classes | Higher margin than 1:1 | Teacher cost shared across students; strategically valuable to grow |
| Add-on materials (Nano Courses, Workbooks) | Potentially highest | Content created once, sold many times; high-margin revenue layer |
| Demo/trial classes | Low or negative margin | Marketing cost, not product revenue |

**The insight:** Growing higher-margin products (group classes, add-ons) faster than lower-margin products (1:1, demos) improves blended gross margin—even if total revenue grows at the same rate.

## W3 — Questions to ask your team

### Quick Reference: 8 Essential Margin Questions
| Question | Reveals | Priority |
|----------|---------|----------|
| Gross margin at 1× vs 2× volume | Scale economics | High |
| Largest single COGS component | Leverage points | High |
| Payment processing fee impact | Pricing optimization | Medium |
| AI-assisted creation COGS | Automation ROI | Medium |
| Demo delivery cost vs conversion | Funnel viability | High |
| Course/platform fee split accuracy | Cost accounting quality | High |
| Refund policy margin impact | Hidden losses | Medium |
| Break-even revenue run rate | Minimum viable scale | High |

---

### 1. "What is the gross margin on this product at current volume, and how does it change at 2× volume?"

Scale economics vary dramatically by cost structure. A product with high fixed costs in COGS improves gross margin dramatically with scale. A product with purely variable COGS stays at the same margin regardless of volume.

*What this reveals:* Whether the product's economics improve with growth or stay flat. Products that don't improve at scale require price increases or cost reductions to ever be profitable.

---

### 2. "What is the largest single COGS component for this product?"

For BrightChamps, teacher cost dominates. For a pure SaaS product, it might be cloud hosting. Knowing the largest cost component tells you where margin improvement is possible.

*What this reveals:* Where leverage exists. Reducing the largest cost component has a disproportionate impact on gross margin compared to optimizing smaller line items.

---

### 3. "How does our payment processing fee impact gross margin across different price points?"

| Transaction Value | Fee Structure | Fee % of Revenue |
|-------------------|---------------|------------------|
| $10 | $0.30 + 2.9% | 5.9% |
| $100 | $0.30 + 2.9% | 3.2% |

High-volume, low-value transactions are particularly vulnerable to payment processing COGS.

*What this reveals:* Whether the pricing and package structure is optimized to minimize payment processing as a percentage of revenue.

---

### 4. "If we switch from human content creation to AI-assisted creation, what is the COGS impact per content piece at scale?"

The BrightChamps worksheet automation case is the template: quantify the cost per unit before and after, multiply by volume, and calculate the margin improvement.

*What this reveals:* Whether the team has done the unit economics of automation investments, not just the productivity story.

---

### 5. "What is the cost of delivering a demo class, and how does it compare to the average conversion value from a demo?"

Demos are a COGS item — teacher time, platform costs, sales effort. 

> **Example:** If a demo costs ₹500 to deliver and converts at 10% to a ₹5,000 package, the demo's effective cost per acquisition is ₹5,000. Is that below the LTV?

*What this reveals:* Whether the demo funnel is economically viable or whether the company is subsidizing acquisition at a loss.

---

### 6. "How does the course_fee / platform_fee split in our payment system reflect actual cost allocation?"

BrightChamps's sale_payment_distributions table explicitly tracks this split. 

⚠️ **Risk:** If the platform_fee allocation doesn't cover actual infrastructure costs, the product is showing artificially high "course margin" while hiding infrastructure losses.

*What this reveals:* Whether internal cost accounting is accurate enough to make good product margin decisions.

---

### 7. "What is the gross margin impact of our refund policy?"

Refunds reverse revenue but some COGS are already incurred (teacher has already been paid for the class). The cost of refunds includes both the revenue reversal and any unrecoverable COGS.

*What this reveals:* Whether the refund rate is a gross margin problem, not just a customer satisfaction metric.

---

### 8. "At what revenue run rate does this product become gross-margin positive?"

For new products with high fixed content creation costs and low initial volume, gross margin may start negative (cost per user exceeds revenue per user). Knowing the break-even volume focuses the team on what needs to happen for the product to work economically.

*What this reveals:* The minimum viable scale for this product's economics. If the break-even volume requires market conditions that don't exist, the product's economics are broken regardless of execution.

## W4 — Real product examples

### BrightChamps — the content automation COGS case

**What:** In JFM '25, BrightChamps built an AI-powered worksheet authoring system using internal bots and a Google App Script pipeline to auto-generate question variations from structured inputs.

**Why:** Projected 67% reduction in worksheet creation cost. At scale across 2,000+ worksheets, this directly reduces the content creation component of COGS.

**Takeaway:** The human-authored baseline (curriculum author rate × hours per worksheet) was replaced by AI generation + lighter human validation, preserving quality while cutting variable cost.

#### Financial impact

| Metric | Baseline | Post-automation | Delta |
|--------|----------|-----------------|-------|
| Cost per worksheet | ₹1,000 | ₹330 | 67% reduction |
| Total cost (2,000 worksheets) | ₹2,000,000 | ₹660,000 | ₹1,340,000 |
| Impact | COGS line item | COGS line item | Direct gross profit gain |

#### What PMs can replicate

1. Identify the largest content creation cost component
2. Estimate cost per unit
3. Evaluate AI automation feasibility
4. Calculate the COGS delta
5. Compare against quality risk and implementation cost

---

### BrightChamps — payment distributions as COGS tracking

**What:** Every BrightChamps payment is recorded in `sale_payment_distributions`, split into `course_fee` and `platform_fee` allocations.

**Why:** This split enables calculation of contribution margin per package type.

**Takeaway:** When proposing new pricing tiers or packages, finance will immediately ask: "What are the course_fee and platform_fee allocations?" PMs who answer this question speak the language of finance.

#### Example margin calculation

| Component | Amount | % of Price |
|-----------|--------|-----------|
| 10-class package | $120 | 100% |
| Course fee (teacher/delivery) | $60 | 50% |
| Platform fee (infrastructure) | $10 | 8.3% |
| Payment processing | $2 | 1.7% |
| **Effective gross margin** | **$48** | **40%** |

---

### Duolingo — the gross margin of asynchronous EdTech vs. live tutoring

**What:** Duolingo operates two models: asynchronous content (created once, served to millions) and live tutoring (human tutors for premium sessions).

**Why:** The COGS profiles are radically different and determine strategic margin potential.

#### Margin comparison

| Model | Gross Margin | Cost Structure | Scalability |
|-------|--------------|-----------------|-------------|
| Asynchronous EdTech | ~70% | Content creation (one-time) + infrastructure (marginal) | Infinite |
| Live tutoring | 40–50% | Tutor pay (per-session direct cost) | Constrained |

**Takeaway:** For BrightChamps, the path to higher gross margin runs through asynchronous content delivery (Nano Courses, recorded practice modules) rather than more live 1:1 instruction. Each shift toward asynchronous delivery reduces the teacher-cost component of COGS and improves blended gross margin.

---

### AWS / Stripe — payment processing fees as a permanent COGS line

**What:** Every BrightChamps payment processed through an external gateway incurs a fee: Razorpay (India) ~2%, Stripe (US/international) 2.9% + $0.30 per transaction.

**Why:** These are permanent COGS items—they exist on every transaction, forever, unless BrightChamps builds its own payment infrastructure.

**Takeaway:** Payment processing fees are a structural cost that compounds at scale.

#### Gross margin math: example

| Period | Transaction Volume | Razorpay fee (₹5,000 package) | Annual COGS impact |
|--------|-------------------|-------------------------------|-------------------|
| Monthly | 1,000 sales | ₹100 per sale | ₹1,200,000/year |
| At 2,000 monthly | 2,000 sales | ₹100 per sale | ₹2,400,000/year |

#### Build vs. buy decision framework

| Factor | Buy (Gateway) | Build (In-house) |
|--------|--------------|-----------------|
| **Monthly cost** | ₹100,000 | ₹0 (fixed engineering) |
| **Build investment** | ₹0 | ₹1,200,000 (12 eng-months @ ₹100k) |
| **Break-even timeline** | — | 12 months |
| **Ongoing burden** | None | Reliability, compliance, maintenance |

⚠️ **Risk consideration:** Building payment infrastructure owns the reliability risk, compliance burden (PCI-DSS), and perpetual maintenance cost. Gateway fees exist for good reason—outsource risk alongside outsource cost.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The gross margin erosion trap

Gross margin rarely collapses suddenly — it erodes gradually. Each product decision adds a small variable cost. Each feature adds a bit more infrastructure. Each new market adds country-specific compliance and support costs. Individually, each decision looks fine. Collectively, they degrade gross margin by 5–10 percentage points over 18 months without any single decision looking like the culprit.

**How to detect gradual erosion:**
- Track gross margin as a **percentage** quarterly, not just absolute gross profit dollars
- Watch for the warning sign: Revenue growing 30% while gross profit grows 20% = declining gross margin = decreasing efficiency

**The PM role:** PMs propose the features that add variable costs. Understanding gross margin lets you ask: *"What is the cost-per-user impact of this feature?"* **before** the cost is locked in.

### Contribution margin confusion

> **Contribution Margin:** What a specific product contributes after its direct variable costs (product-level metric)

> **Gross Margin:** The company-level metric for overall profit efficiency

Senior product leaders sometimes conflate these, leading products to appear "profitable at the product level" while harming company-level profitability.

**The typical confusion:**

| Signal | Reality |
|--------|---------|
| New product launches with 70% contribution margin | "Great economics!" |
| But doesn't cover infrastructure, support, sales share | Fully-loaded margin = 10% or negative |
| Looks profitable in isolation | Unprofitable when shared costs allocated |

**The fix:** PMs building new products must track both:
- **Contribution margin** (the product-level number)
- **Fully-loaded margin** (contribution margin − allocated shared costs)

Leadership will ask about the fully-loaded number. Being surprised destroys credibility.

### The COGS misclassification problem

What counts as COGS varies by company accounting policy. This means gross margin comparisons across companies can be misleading.

**Common classification differences:**

| Function | Company A | Company B |
|----------|-----------|-----------|
| Customer success (onboarding, support) | COGS | OpEx |
| Content creation | COGS | R&D |
| Technical infrastructure | COGS | COGS |

**Why this matters for PMs:** When leadership says *"Our gross margin is 45% vs. competitor's 65%,"* ask: **Are you comparing the same thing?**

A competitor that classifies customer success as OpEx will show higher gross margin than one that correctly classifies it as COGS — even with identical underlying economics. The accounting choice creates the appearance of a gap that may not exist operationally.

## S2 — How this connects to the bigger system

| Concept | Connection | Interaction |
|---|---|---|
| **Unit Economics (07.01)** | Gross margin embedded in LTV calculation | LTV = ARPU × margin × lifetime; improving gross margin improves LTV without changing price or retention |
| **Pricing Models (07.02)** | Pricing model determines COGS structure | Subscription: COGS spread over time · Transactional: COGS concentrated at delivery · Usage-based: COGS scales with consumption |
| **Payment Infrastructure (07.05)** | Gateway choice directly affects COGS | Gateway fees are permanent COGS line; build vs. buy is a gross margin decision |
| **Churn & Retention Economics (07.07)** | High churn destroys gross margin economics | Gross profit from one cohort must recover acquisition + service COGS before churn |
| **ETL Pipelines (02.06)** | Data infrastructure contributes to COGS | Infrastructure costs for product-delivery pipelines belong in COGS |
| **Feature Flags (03.10)** | Gradual rollouts enable COGS testing | Test uncertain COGS impact at 10% rollout before full-scale commitment |

### The PM-finance relationship

> **Gross margin:** the percentage of revenue remaining after direct costs of goods sold; one of finance's most critical metrics and one PMs often misunderstand.

PMs who master gross margin can:

- **Participate credibly in budget discussions** — explain why infrastructure investment pays back through COGS reduction
- **Argue for strategic investments** — show OpEx today that reduces COGS at scale
- **Spot hidden COGS implications** — identify when feature proposals carry unestimated costs
- **Bridge product and financial metrics** — translate "engagement improved" into margin impact

## S3 — What senior PMs debate

### "What gross margin should we target, and when does it become a constraint?"

| Business model | Target gross margin | Why |
|---|---|---|
| Pure SaaS | 70–85% | Near-zero marginal cost per additional user; software scales |
| EdTech (live instruction) | 40–60% | Teacher cost is irreducible; improvement comes from group classes and asynchronous content |
| EdTech (asynchronous) | 65–80% | Content created once; marginal delivery cost is infrastructure |
| Consumer marketplace | 50–70% | Take rate minus payment processing and fraud; minimal fulfillment |

**The core debate at growth-stage companies:**

| Approach | Strategy | Tradeoff |
|---|---|---|
| **Optimize margin now** | Avoid low-margin features and products | Slower growth, higher unit economics early |
| **Invest in volume now** | Build scale to negotiate costs down later | Lower margins initially; bet on cost improvement at scale |

*What this reveals:* Most successful consumer businesses prioritize volume in early stages, accepting lower gross margins, and optimize costs as they achieve scale.

> **Gross margin as constraint:** When the company needs to be profitable (running out of runway), gross margin that's too low can't be fixed by volume — you need either a price increase or a cost reduction.

⚠️ **Risk:** Companies that pursue volume growth without periodically checking gross margin trajectory sometimes discover at Series C or IPO that the core business model doesn't work at any scale.

---

### "Should content and R&D investments be in COGS or OpEx?"

For EdTech companies, this classification affects how gross margin is presented to investors.

| Classification | Gross margin shown | Implication | Risk |
|---|---|---|---|
| **All content creation in COGS** | Lowest | Most conservative; reflects true delivery cost | Appears less profitable than peers |
| **Recurring content in COGS, new curriculum in OpEx** | Mid-range | Most common for mature EdTechs; separates maintenance from innovation | Requires consistent methodology |
| **All content creation in OpEx** | Highest | Most aggressive; shows strongest margin | ⚠️ Can mislead investors about true delivery cost per student |

**PM implication:** How your company classifies content creation costs affects what gross margin "means" and how it benchmarks against competitors. Understanding the classification helps PMs provide accurate estimates when proposing content investments.

---

### "What do AI models change about the gross margin structure of knowledge work products?"

> **AI inference cost:** Using foundation models as a product component introduces a new COGS item that traditional software products didn't have. Each AI-powered interaction (tutor response, generated worksheet, personalized recommendation) has a compute cost.

**The strategic question:** Does AI improve or worsen gross margin?

| AI deployment model | Margin impact | Mechanism |
|---|---|---|
| **Replacing human labor** (e.g., BrightChamps worksheet automation) | ✅ Improves | Compute cost of AI generation < human authoring cost |
| **Adding as enhancement layer** (AI tutor alongside live teacher) | ⚠️ May worsen | AI adds to COGS without replacing existing COGS; margin only improves if AI increases price or reduces churn enough to improve LTV |
| **As product differentiation** | Depends on pricing | If AI features justify price premium > AI compute cost, margin improves; if bundled without price increase, margin worsens |

**For BrightChamps—by feature:**
- **AI content automation (worksheet generation):** ✅ Improves gross margin
- **AI tutoring features (BrightBuddy):** ⚠️ May worsen margin unless priced separately or engagement improvement reduces churn enough to offset compute cost