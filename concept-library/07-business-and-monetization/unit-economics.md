---
lesson: Unit Economics
module: 07 — Business & Monetization
tags: business, metrics, strategy
difficulty: intermediate
prereqs:
  - 06.01 — North Star Metric — LTV and LTV:CAC ratio are common NSM candidates for B2B products
writer: cfo-finance
qa_panel: CFO/Finance Lead, GTM Lead, Junior PM Reader
kb_sources:
  - technical-architecture/payments/package-and-payments.md
  - performance-reviews/apr24-mar25-performance-review.md
profiles:
  foundation: non-technical business PM, aspiring PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: senior PM, head of product, CFO-background PM
status: ready
last_qa: 2026-04-07
---
```markdown
<!--
  LEVEL SELECTOR
  
  The dashboard renders one level at a time. Switch with the level toggle.
  Each level is self-contained and readable without the others.
  
  RECOMMENDED READING ORDER:
  Foundation → Working Knowledge → Strategic Depth
  
  NOTE: PMs with finance backgrounds may start at Working Knowledge or Strategic Depth directly.
-->
```
# ═══════════════════════════════════
# FOUNDATION
# For: non-technical PMs, aspiring PMs, MBA PMs
# Assumes: nothing — basic numeracy assumed, no finance background required
# ═══════════════════════════════════

## F1. The world before this existed

The growth review was going well. The PM had the slide ready: 300 new customers in month one, up from 40 the month before. Seven-and-a-half times growth in four weeks.

The CFO looked at it for a moment. "What did that cost?"

The PM didn't know.

"We ran some paid ads. Sent an email campaign. The sales team did demos."

"How much did the ads cost?"

"Maybe ₹4 lakh?"

"And the sales team — how many hours?"

"Maybe... a hundred hours across the team?"

"And those 300 customers — do they all pay monthly? What do they pay? How long do they stay?"

The PM had four of the seven numbers. The CFO had the other three in her head already. She pulled up her calculator.

"You spent roughly ₹12 lakh to acquire these 300 customers. Each one pays ₹1,200 per month and stays for an average of 8 months before churning. That's ₹9,600 per customer in total revenue. Your gross margin on delivery is about 40%. So you net ₹3,840 per customer."

She set the calculator down. "You spent ₹4,000 to make ₹3,840."

The room was quiet.

"Your feature isn't a growth machine. It's a slow way to lose money at scale."

This is why unit economics exists. Not to kill growth ideas — but to tell you whether what looks like growth is actually building something valuable, or just spending faster.

## F2. What it is

> **Unit economics:** The revenue and cost directly associated with a single customer — and whether that customer, over their lifetime with your product, generates more value than they cost to acquire and serve.

### The everyday analogy

Think of it as the profit calculation for a single pizza, before you open a restaurant.

Before expanding to 20 locations, a smart restaurateur calculates: does one pizza make money? What are the ingredients? Labour? Rent per slice sold? If one pizza earns ₹50 after all direct costs, and your location costs ₹50,000 per month, you need to know how many pizzas you sell before the math works. Open 20 locations before checking this, and you scale losses.

Unit economics is the same calculation for a customer. Before acquiring your next 1,000, does one customer make money?

### The three numbers every PM must know

> **CAC (Customer Acquisition Cost):** The total cost of sales and marketing divided by the number of new customers acquired in that period.
> 
> *CAC = Total acquisition spend ÷ New customers acquired*

> **LTV (Lifetime Value):** The total gross profit a customer generates over their full time with your product.
> 
> *LTV = Average Revenue Per User × Gross Margin % × Average Customer Lifetime*

> **Payback Period:** How many months until you've recovered what you spent to acquire a customer.
> 
> *Payback Period = CAC ÷ (Monthly ARPU × Gross Margin %)*

#### The relationship between them

| Metric | What it tells you |
|---|---|
| **LTV > CAC** | You make money on each customer — eventually |
| **LTV:CAC ratio** | How much you make per rupee/dollar spent acquiring (3:1 = industry floor) |
| **Payback period** | How long you're cash-negative per customer (12–18 months = healthy for growth-stage) |

### Why gross margin is in every formula

Revenue is not profit. When an edtech platform sells a ₹1,200/month subscription, it doesn't keep ₹1,200. It pays for teachers, servers, support, and platform fees. If those direct costs consume 60% of revenue, the gross margin is 40%, and the actual value per month per customer is ₹480 — not ₹1,200.

**LTV that ignores gross margin is optimism, not analysis.**

| Customer Type | Revenue | Gross Margin | Actual LTV | Why it matters |
|---|---|---|---|---|
| Customer A | ₹50,000 | 10% | ₹5,000 | Low-margin business |
| Customer B | ₹20,000 | 60% | ₹12,000 | **2.4× more valuable** |

The second customer is more than twice as valuable — even at less than half the revenue.

## F3. When you'll encounter this as a PM

| Scenario | Unit Economics Question | PM Action |
|----------|------------------------|-----------|
| **New acquisition channel pitch** | At the CAC this channel implies, do we make money on resulting customers? | Determine the CAC ceiling for viability before committing budget |
| **Pricing change decision** | At the new price, does LTV still justify CAC and does payback period stay within cash tolerance? | Model impact on both acquisition speed and per-customer profitability |
| **Growth review with healthy surface metrics** | If CAC grew 80% while MAU grew 40% and LTV is flat, are we acquiring customers faster or losing money faster? | Verify that growth is real rather than expensive |
| **Competitor price cut** | Can the competitor sustain the cut (LTV:CAC still positive) and can we sustain matching it (payback period intact)? | Use unit economics to inform competitive response strategy |
| **Headcount and hiring decisions** | Can the LTV from customers new hires bring justify their acquisition cost? | Reframe headcount debates from politics to financial sustainability |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs
# Assumes: Foundation. You know what CAC, LTV, and payback period mean.
# ═══════════════════════════════════

## W1. How unit economics actually works — the full mechanics

> **Quick reference — Unit Economics**
> **What:** Revenue and cost per customer — does one customer make money?
> **When:** Pricing decisions, channel investment, growth reviews, expansion planning
> **Default:** Payback period < 18 months for growth-stage. LTV:CAC ≥ 3:1 at maturity.

### CAC: the full calculation

Most teams calculate blended CAC wrong. They divide total marketing spend by total new customers. This hides everything important.

> **CAC (Customer Acquisition Cost):** Total investment in sales and marketing divided by number of new customers acquired in a period.

**Blended CAC formula:**
```
CAC = (Total sales cost + Total marketing cost) / New customers in period
```

#### What "total sales cost" must include:
- Sales salaries and commission
- Sales tooling (CRM, demo software)
- Sales management overhead
- Pre-sales support hours

#### What "total marketing cost" must include:
- Paid media spend (all channels)
- Content and creative production
- Marketing team salaries
- Agency and contractor fees
- Attribution tooling

⚠️ **Common mistake:** Teams routinely omit salaries from CAC because they're "fixed costs." This is wrong — salaries are acquisition costs when sales people are spending time acquiring customers. A CAC that excludes headcount is 40–60% understated at most growth-stage companies.

**Channel-level CAC** is what actually drives decisions. Blended CAC tells you the average; channel-level CAC tells you which channels are profitable and which are subsidised by others.

---

### LTV: the mechanism, not the formula

> **LTV (Lifetime Value):** Total gross profit margin generated by a customer during their entire relationship with the company.

**LTV formula:**
```
LTV = ARPU × Gross Margin % × (1 / Monthly Churn Rate)
```

The `1 / churn rate` term = average customer lifetime in months.
- 5% monthly churn = 20 month average lifetime
- 2% monthly churn = 50 month average lifetime

#### Why churn rate dominates LTV:

| Monthly Churn | Multiplier | Impact |
|---|---|---|
| 5% | 20× | LTV = ARPU × Margin × 20 |
| 2% | 50× | LTV = ARPU × Margin × 50 |

**Key insight:** If ARPU and margin are equal, a business with 2% churn has 2.5× the LTV of a business with 5% churn. No pricing, no upsell, no acquisition optimisation can compensate for a high churn rate. The denominator wins.

#### Gross margin in LTV — reflect actual delivery cost

Gross margin must account for:
- **Teacher-based models** (edtech): delivery COGS moves with volume
- **Infrastructure-based models** (SaaS): delivery COGS moves more slowly with server and support costs

Both need to be modelled, not assumed.

---

### Payback period: the cash-flow lens

| Metric | Tells You |
|---|---|
| **LTV:CAC** | Long-run profitability |
| **Payback period** | Cash-flow reality and financing needs |

> **Payback Period:** Number of months required to recover the CAC from the gross margin of a single customer.

**Payback period formula:**
```
Payback = CAC / (Monthly ARPU × Gross Margin %)
```

#### What a 24-month payback means:

- You are cash-negative on every new customer for 2 years
- At ₹5,000 CAC per customer acquiring 100 customers/month = ₹5,00,000/month in cash-negative positions
- All of which need to be financed before payback

**Interest-rate sensitivity:** In low-rate environments, this is manageable. In high-rate environments, this is expensive and risky.

⚠️ **Why this matters:** Payback period became the primary unit economics metric for most growth-stage companies after 2022 because it connects unit economics to cash requirements in a way LTV:CAC does not.

---

### LTV:CAC: the maturity signal

At early stage, payback period is the operating metric. At Series B+ with recurring revenue, LTV:CAC becomes the strategic signal:

| LTV:CAC Ratio | Interpretation | Action |
|---|---|---|
| < 1:1 | Destroying value on every customer — unsustainable at any scale | Fix model or shut down |
| 1:1 – 2:1 | Marginal — CAC barely recovered, no room for overhead or reinvestment | Improve retention or raise prices |
| 3:1 | Industry floor for sustainable growth | Minimum viable unit economics |
| 4:1 – 6:1 | Healthy — room to invest in growth and still profit | Safe to scale |
| > 8:1 | Underinvesting in growth OR unusually capital-efficient model (PLG, viral) | Opportunity to acquire more aggressively |

## W2. The decisions unit economics forces

### Quick reference: Which lever to pull?

| Lever | Best when | Speed | Risk |
|---|---|---|---|
| **Reduce CAC** | New channels exist; current CAC is channel-specific | 1–3 months | May reduce volume if high-CAC channels drive growth |
| **Increase LTV** | Pricing below market; expansion revenue untapped | Immediate (new customers) | May reduce conversion if not positioned right |
| **Reduce churn** | Churn > 3%/month; value delivery gaps exist | 3–6 months | Usually a product problem, not a surface fix |

> **PM default:** Fix churn before optimizing CAC. A leaky bucket gets worse, not better, when you pour more in faster.

---

### Which lever to pull: CAC reduction vs LTV improvement vs churn reduction

When unit economics are weak, three levers exist. They are not interchangeable.

#### Reduce CAC
- **Best for:** CAC is channel-specific and fixable; new channels exist
- **Mechanism:** Shift mix to lower-CAC channels (content, PLG, referral)
- **Speed:** 1–3 months to see channel-level impact
- **Risk:** May reduce volume if high-CAC channels were driving most growth
- **Default:** First lever for early-stage, paid-acquisition-heavy businesses

#### Increase LTV (price/upsell)
- **Best for:** Pricing is below market; upsell/expansion revenue is untapped
- **Mechanism:** Increase price, add tiers, improve expansion revenue
- **Speed:** Immediate on new customers; delayed on existing
- **Risk:** May reduce conversion; may not if pricing was below market
- **Default:** First lever when gross margin is low and price is below market

#### Reduce churn
- **Best for:** Churn is high relative to similar products; value delivery gaps exist
- **Mechanism:** Fix retention drivers — onboarding, engagement, product-market fit
- **Speed:** 3–6 months to see cohort retention lift
- **Risk:** High effort; most retention problems are product problems, not surface problems
- **Default:** First lever when churn > 3%/month; no other lever matters at this rate

---

### Short vs long payback period business models

Different business models have structurally different payback period tolerances.

| | **Short payback** <12 months | **Long payback** 12–36 months |
|---|---|---|
| **Best for** | Consumer SaaS, SMB market, high-churn-risk segments | Enterprise SaaS, annual contracts, sticky products with high switching cost |
| **Financing requirement** | Low — cash recouped quickly | High — must finance gap between acquisition spend and payback |
| **Growth sensitivity** | More sensitive to CAC increases | More sensitive to churn increases (long payback + high churn = catastrophic) |
| **What determines viability** | Volume and channel efficiency | Contract value and retention |
| **Default** | Target for consumer and growth-stage products | Acceptable only with high ACV, strong NDR, and adequate financing |

> **PM default:** If your product serves SMBs or consumers, a payback period above 18 months is a structural problem, not just a metric. Fix it before scaling.

---

### Add-on revenue and its effect on unit economics

> **Add-on revenue:** Optional purchases (upsell, cross-sell, expansion) that increase LTV without increasing CAC, since the customer is already acquired.

**The opportunity:**
- Add-ons increase LTV without acquisition cost
- High attach rate + high margin = meaningful payback period improvement
- Even a 5% gross margin uplift from add-ons can shift payback period significantly

**Your job as PM:**
- Identify which add-ons have high attach rates and high margins
- Make them more discoverable
- Project impact before scaling

⚠️ **Cannibalisation risk:** Add-on revenue that replaces base subscription upgrades doesn't improve LTV. Model cannibalisation before projecting LTV improvement from add-on strategy.

## W3. Questions to ask in growth and finance reviews

> **Quick Reference:** Seven diagnostic questions that reveal whether a team truly understands their unit economics or is operating on incomplete data.

---

### "What is our channel-level CAC, not blended CAC?"

*What this reveals:* Blended CAC is an average that hides which channels are profitable and which are subsidised. A team that can answer by channel has done the work. A team that only knows blended CAC is making growth decisions in the dark.

---

### "Does our CAC calculation include full sales and marketing headcount — salaries, not just spend?"

*What this reveals:* Most early-stage teams omit headcount from CAC. If the answer is "we only count media spend," the real CAC is 30–60% higher than reported. This changes the LTV:CAC ratio immediately.

---

### "What is the gross margin assumption in our LTV calculation?"

*What this reveals:* Teams that use revenue (not gross profit) in LTV are overstating it by 40–90%, depending on COGS structure. Ask specifically: "Does this include delivery cost, support cost, and payment processing fees?"

---

### "What is our payback period on customers acquired last quarter, by cohort?"

*What this reveals:* The right calculation is cohort-level, not blended. If the answer is a blended estimate, new high-CAC customers are being averaged with old low-CAC customers, and payback trend is invisible.

---

### "At our current churn rate, what happens to LTV if we raise price 15%?"

*What this reveals:* Forces modelling of price elasticity in the context of unit economics, not just conversion rate. A PM who can model this live in a review meeting demonstrates genuine financial command of the product.

---

### "Does our LTV model include expansion revenue, or only base subscription?"

*What this reveals:* Products with strong expansion revenue (upsell, cross-sell, usage growth) have higher true LTV than base subscription implies. If the model excludes it, LTV is understated and growth investment may be under-funded.

---

### "At what CAC level does this channel become unprofitable given current LTV?"

*What this reveals:* Forces the team to name a CAC ceiling — the maximum acquisition cost at which the business still makes money. This is the single most useful number in a channel investment decision, and most teams don't have it pre-calculated.

## W4. Real product examples

### Duolingo — Freemium CAC and the $0 acquisition model

**What:** Built a product where 95%+ of users are acquired at effectively zero CAC through organic, word-of-mouth, and app store discovery. Monetisation comes from a small percentage converting to Duolingo Plus (subscription) or Duolingo Max (premium AI features).

**Why:** When CAC ≈ $0 for most users, LTV:CAC ratios are structurally excellent even at modest ARPU. The constraint isn't acquisition — it's conversion and LTV per converted user.

**Takeaway:** PLG products flip the unit economics equation. The constraint is LTV (how to convert and retain free users into paid), not CAC. When evaluating PLG, model conversion rate and LTV of converted users — not acquisition efficiency.

---

### Salesforce — High CAC justified by enterprise LTV and net dollar retention

**What:** Runs one of the highest-CAC acquisition models in SaaS — enterprise sales cycles of 6–12 months, large sales teams, extensive pre-sales engineering. CAC per enterprise customer: $50,000–$200,000.

**Why:** Enterprise contracts start at $100,000+ ARR and expand through additional seats and modules over time. Net Dollar Retention consistently above 120% — existing customers grow revenue by 20% per year without new CAC, compounding LTV dramatically above the initial contract value.

**Takeaway:** LTV:CAC is not just about the initial contract. For enterprise products, payback period may be 18–36 months, but LTV keeps expanding after payback. Model expansion revenue explicitly — the initial sale is often a small fraction of total LTV.

---

### An edtech platform — Installment payments restructuring payback period

**What:** Sold annual course packages on an installment structure — students paid monthly rather than annually upfront. Improved conversion on paper; in practice, restructured CAC payback from immediate to 8–12 months.

**Why:** The shift required financing the payback gap — platform was cash-negative per customer for 8+ months. When modelled explicitly: add-on revenue (digital goods, supplementary courses) contributed 5% gross margin uplift partially offsetting the extended payback period. COGS reduction from AI-driven content automation (~67% lower creation cost) made unit economics viable at scale.

**Takeaway:** Payment structure is a unit economics decision, not just a conversion decision. Monthly billing improves conversion but extends payback period and creates a cash gap. Model both effects before defaulting to installments.

---

### HubSpot — Freemium-to-enterprise LTV stacking across tiers

**What:** Offered a generous free CRM tier acquired at near-zero CAC, then converted a subset into paid tiers (Starter → Professional → Enterprise) as customer businesses scaled. Average customer LTV grew with company size — SMBs who became enterprise customers had LTVs 10–20× their original contract.

**Why:** HubSpot's LTV model compounds because:
- Free tier creates a large base at zero CAC
- Conversion to paid happens when customers are already sold on the product, reducing sales cost at upgrade
- NRR from tier upgrades adds expansion revenue on top of base subscriptions

The unit economics of the initial free-to-Starter conversion are modest; the LTV of a Starter-to-Enterprise journey justifies the full acquisition investment.

**Takeaway:** In freemium models, don't calculate LTV on the first paid conversion. Model the full journey — what percentage of Starter customers eventually become Professional or Enterprise, and what is the LTV at each destination?
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: senior PMs, heads of product, CFO-background PMs
# Assumes: Working Knowledge. You can calculate and interpret CAC, LTV, payback period.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Blended CAC masking channel degradation

**The problem:** One blended CAC number hides channel-specific efficiency loss.

| Metric | Year 1 | Year 2 | Change |
|--------|--------|--------|--------|
| Content + referral CAC | ₹800 | ₹800 | — |
| Paid CAC | ₹3,500 | ₹3,500 | — |
| Content + referral mix | 80% | 40% | -40pp |
| Paid mix | 20% | 60% | +40pp |
| **Blended CAC** | **₹1,300** | **₹2,300** | **+77%** |

**What happened:** Paid channel CAC stayed constant, but dependency shifted from efficient to expensive channels. The blended metric masked channel saturation.

**Prevention:**
- Track channel-level CAC weekly (operating metric)
- Use blended CAC only for board reporting

---

### LTV calculated on revenue, not margin

> **Gross Margin-Adjusted LTV:** Revenue LTV × gross margin % = true economic LTV available for reinvestment and profit

**The problem:** Non-finance PMs default to revenue LTV because it's in their dashboards.

| Component | Value | Impact |
|-----------|-------|--------|
| Annual revenue per customer (ARPU) | ₹1,250 |  |
| Months modeled | 12 |  |
| **Revenue LTV** | **₹15,000** | What the team presented |
| Gross margin | 35% | From CFO |
| **Margin-adjusted LTV** | **₹5,250** | What decisions should use |
| **Overstatement ratio** | **2.85×** | Risk exposure |

**Downstream distortion:**
- CAC ceiling set too high
- Growth investment justified incorrectly
- Payback tolerance too permissive

**Prevention:** Require margin-adjusted LTV as the only LTV presented to leadership. Make finance the single source of COGS allocation.

---

### Ignoring the cash cost of payback period

⚠️ **Cash trap:** A positive unit economics ratio can coexist with negative cash runway.

**The problem:** Teams confuse "profitable per customer" with "company has cash."

| Variable | Value |
|----------|-------|
| Monthly acquisition | 200 customers |
| CAC per customer | ₹5,000 |
| Monthly cash outlay | ₹10,00,000 |
| **12-month payback exposure** | **₹2.4 crore** |
| Company bank balance | ₹1.8 crore |
| **Cash gap** | **₹60 lakh shortfall** |
| LTV:CAC ratio | 3.2:1 (looks healthy) |

**What's hidden:** The 24-month payback means ₹2.4 crore sits in "in-flight" revenue that hasn't landed yet, while the company needs cash today.

**Prevention:** Model outstanding payback exposure as a separate cash requirement:

> **(Monthly new customers) × CAC × (average months to payback) = cash requirement**

Add this line item to cash runway calculations, not just unit economics dashboards.

---

### Cohort-blind LTV averaging

**The problem:** Average LTV conceals a bimodal distribution—most customers churn early, a small segment stays and generates value.

| Metric | Value | Reality |
|--------|-------|---------|
| Average LTV | ₹12,000 | Describes 0% of actual customers |
| Median LTV | ₹2,800 | Describes typical customer |
| Top-decile LTV | ₹45,000 | Describes high-value segment |
| Churn by month 6 | 70% | |
| Revenue from remaining 30% | 90% | |

**The trap:** Acquisition strategy optimized for average LTV only works for top 30% of customers. Expensive to acquire and retain the 70% who churn at month 2.

**What this reveals:** The "average" customer doesn't exist. Decisions based on it hurt profitability on the actual customer mix.

**Prevention:**
- Segment LTV by: cohort, channel, customer profile
- Know the LTV of the customer you're actually acquiring
- Don't use all-customer averages for forward-looking decisions

## S2. How this connects to the rest of your work

| Lesson | Connection | Why it matters |
|--------|-----------|----------------|
| **07.07 Churn & Retention Economics** | Churn rate is the denominator in the LTV formula | A 1% monthly churn reduction has larger LTV impact than almost any other lever |
| **06.03 Cohort Analysis** | Accurate LTV requires cohort-level retention data | Aggregate retention averages hide cohort degradation that produces inflated LTV projections. Never model LTV from blended data |
| **07.02 Pricing Models** | Pricing decisions are LTV decisions | A price increase lifts LTV immediately on new customers; pricing model (subscription vs usage-based vs freemium) determines LTV structure, not just level |
| **08.01 Go-To-Market Strategy** | CAC by channel is the financial constraint on GTM investment | A GTM strategy without channel-level CAC vs product LTV modeling is a spending plan, not a strategy |
| **06.01 North Star Metric** | LTV:CAC ratio is a strong NSM candidate for B2B subscription products | Captures both sides of value equation: what customers are worth and what they cost to acquire |
| **08.07 Paid Acquisition Fundamentals** | Relationship between ROAS and CAC | Evaluate paid channel efficiency in context of payback period, not just immediate conversion |

## S3. What senior PMs debate

> **LTV:CAC Benchmark:** The 3:1 ratio (lifetime value to customer acquisition cost) emerged from 2012–2015 SaaS research when market conditions were uniform and financing was cheap. It is now more likely to mislead than guide.

### The case against the 3:1 benchmark

**Origin & obsolescence**

The benchmark comes from David Skok's SaaS metrics research (2012–2015), when:
- CAC structures were relatively uniform (outbound sales + paid acquisition dominated)
- Interest rates near 0% made 24-month payback periods cheap to finance
- The ratio worked because 3:1 implied sufficient margin to cover overhead, reinvest, and profit

**Three structural shifts that broke it:**

| Factor | 2015 Context | 2025 Reality | Impact |
|--------|--------------|--------------|--------|
| **Acquisition model** | Sales-led (high, uniform CAC) | PLG (often $0 CAC for 90%+ of users) | Products like Figma, Linear, Notion hit 20:1, 50:1, or infinite ratios—benchmark becomes meaningless |
| **Interest rates** | ~0% (2015–2021) | 7–8% (2023–2025) | Same payback period now costs real capital; two identical 3:1 ratios with different payback periods have different financing requirements |
| **Gross margin drivers** | Fixed by pricing | Dynamic via AI/automation | AI-driven COGS reduction (e.g., 35% → 60% margin) improves unit economics without touching acquisition or pricing—benchmark misses this entirely |

⚠️ **The risk of abandoning guardrails:** Benchmarks exist because they encode learning from hundreds of comparable businesses. Discarding 3:1 in favor of "our model is different" frequently lets teams rationalize weak unit economics.

### The case for keeping guardrails (the counter-position)

A business still needs enough margin above CAC to survive overhead, downturns, and reinvestment cycles. The 3:1 rule communicates something real—abandoning it entirely invites rationalization.

### What actually matters: The payback-period-first framework

Replace LTV:CAC ≥ 3:1 with:

| Metric | Rule | Role |
|--------|------|------|
| **Payback period** | < 18 months (growth stage)<br/>< 12 months (Series B+) | Operating constraint—the immediate lever you control |
| **LTV:CAC ratio** | 3:1+ as long-run target | Strategic signal—signals sustainable unit economics over time |

**Why this matters:**
- A 3:1 LTV:CAC with 30-month payback is worse for a cash-constrained startup than a 2:1 LTV:CAC with 8-month payback
- The old benchmark hides this trade-off; the payback framework exposes it
- Payback period determines *when* capital comes back; LTV:CAC determines *how much* margin you have once it does

## Related lessons

### Prerequisites
- 06.01 North Star Metric — LTV:CAC is a common NSM candidate for B2B products; understand NSM selection before using unit economics as a north star

### Next: read alongside (companions)
- 07.02 Pricing Models — pricing decisions directly change LTV; the two lessons are inseparable
- 07.07 Churn & Retention Economics — churn rate is in the LTV denominator; fixing churn is the highest-leverage unit economics lever
- 08.01 Go-To-Market Strategy — CAC by channel is the financial constraint on GTM investment

### Read after (deepens this lesson)
- 06.03 Cohort Analysis — accurate LTV requires cohort-level retention; aggregate LTV averages mislead
- 08.07 Paid Acquisition Fundamentals — ROAS vs CAC; channel-level unit economics in practice
- 07.08 Subscription Mechanics — billing structure, dunning, and payment recovery all affect gross margin and LTV calculation