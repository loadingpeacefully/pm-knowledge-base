---
lesson: North Star Metric
module: 06 — Metrics & Analytics
tags: metrics, strategy, analytics
difficulty: intermediate
prereqs:
  - none — assumes basic familiarity with DAU, MAU, conversion rate
writer: senior-pm
qa_panel: Senior PM, CFO/Finance Lead, Junior PM Reader
kb_sources:
  - performance-reviews/apr24-mar25-performance-review.md
  - product-prd/nano-skills.md
profiles:
  foundation: non-technical business PM, aspiring PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: senior PM, head of product, AI-native PM
status: ready
last_qa: 2026-04-06
---
```markdown
<!--
  LEVEL SELECTOR
  
  The dashboard renders one level at a time. Switch with the level toggle.
  
  READING PATHS:
  • **Recommended:** Foundation → Working Knowledge → Strategic Depth
  • **For senior PMs & heads of product:** Start at Working Knowledge or Strategic Depth
  
  Each level is self-contained and readable without the others.
-->
```
# ═══════════════════════════════════
# FOUNDATION
# For: non-technical PMs, aspiring PMs, MBA PMs new to metrics
# Assumes: You know what DAU and conversion rate are. No analytics background required.
# ═══════════════════════════════════

## F1. The world before this existed

The quarterly business review was 45 minutes in. The engineering lead was presenting session growth. The growth PM was presenting DAU. The monetization PM was presenting conversion rate. The CFO wanted to know about revenue per user.

All four metrics were moving. Some were up. Some were flat. One was slightly down. Each team had a story for why their number was the one that mattered. Nobody could agree on whether the product was getting better or worse.

The CEO stopped the meeting. "Which one of these tells me if we're winning?"

Nobody answered.

That meeting is a real pattern at product companies. Teams proliferate dashboards. Metrics multiply. And the more metrics you have, the less signal any single one carries — because every team will find the number that makes their work look good. What you end up with isn't a picture of the business. It's a collection of competing defenses.

The North Star Metric exists to solve exactly this. One metric. Agreed upon across the whole company. The single number that best captures whether the product is delivering value to customers. When it moves up, the business is probably healthier. When it stops growing, you have a problem worth mobilising the entire team around — no matter how good every other number looks.

The shift this creates is significant. Teams stop optimizing for their local metric and start asking how their work contributes to the one that matters. Roadmap debates shift from "my feature moves my number" to "which of these options moves *the* number."

## F2. What it is

> **North Star Metric (NSM):** A single metric that captures the core value your product delivers to customers. It is a leading indicator of your business's long-term health — it moves before revenue does, and predicts whether revenue will be healthy six to twelve months from now.

### The everyday analogy

**NSM is a compass heading, not a speedometer.**

| Speedometer | Compass Heading |
|---|---|
| Tells you how fast you're going *right now* | Tells you which direction you're pointed |
| Examples: revenue, conversions, monthly signups | Reveals whether customer value is accumulating |
| Shows current rate of output | Catches what the speedometer misses |
| You can move fast in the wrong direction | Prevents erosion while metrics look great |

### How it differs from a goal

| Goals | North Star Metric |
|---|---|
| Change quarterly | Stable across years |
| What you're trying to hit this quarter | Structural — reflects what value actually means |
| Tactical focus | Long-term business health signal |

**Real examples:**
- **Spotify:** Time spent listening (10+ years unchanged)
- **Airbnb:** Nights booked (consistent since early growth)

### What makes a metric qualify

| Criterion | What it means |
|---|---|
| **Reflects value delivered** | When it goes up, real customers got real value |
| **Leading indicator of revenue** | Revenue follows when this moves — but isn't the metric itself |
| **Team can influence it** | Engineers, PMs, designers can affect it with product decisions |
| **Hard to game** | A team shouldn't be able to inflate it without actually creating value |
| **One number** | Not a formula. Not a ratio of two things. One thing. |

## F3. When you'll encounter this as a PM

| Scenario | Your Move | The NSM Role |
|----------|-----------|--------------|
| **Setting team OKRs** | For each proposed KR, ask: "Show me the causal link from this KR to the NSM" | Anchor for KRs — they should move it, not proxy for it |
| **Defending your roadmap** | When features compete for sprint capacity, ask: "Which is more directly connected to [NSM]?" | Tiebreaker that ends prioritization debates |
| **Presenting to leadership** | Lead with the NSM and its trend instead of a 20-metric dashboard | The one number that contextualizes everything else |
| **Post-launch reviews** | Ask: "Did this move the NSM?" rather than "Did engagement go up?" | Catches local feature wins that harm the broader system |
| **Hiring and onboarding PMs** | Every new PM should answer within two weeks: "What is our NSM and how does my squad contribute to it?" | Test of whether the NSM is real strategy or just a slide deck |
| **Business looks healthy but something feels wrong** | Run NSM trend against revenue growth — divergence (revenue up, value metric flat) is a leading signal | Early warning system before problems become earnings issues |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: growth PMs, consumer startup PMs, B2B enterprise PMs
# Assumes: Foundation. You understand what the NSM is and why it matters.
# ═══════════════════════════════════

## W1. How to select and validate your NSM

> **Quick reference — North Star Metric**
> **What:** The single metric that best captures whether your product is delivering value to customers
> **When:** Setting company strategy, OKR planning, roadmap prioritisation, post-launch review
> **Default:** Start with "value delivered per active user per period" — not a growth metric, not a revenue metric

### The 5-question filter

Work through these in order. The right NSM clears all five.

| Question | What it tests | Pass = | Fail = |
|----------|---------------|--------|--------|
| **1. Does it capture value delivered — not activity?** | Whether the metric measures outcome, not just presence | Sessions/clicks reflect *actual value* (e.g., Duolingo DAU = lesson completed) | Sessions/clicks measure "users showed up" with no value signal |
| **2. Is it causally connected to revenue — not the same as revenue?** | Whether the metric drives revenue, rather than being revenue | "Lessons completed per subscriber per week" (causes renewal) | "Revenue" or "ARR" (measures extraction, not delivery) |
| **3. Can your team move it in a 6–12 week sprint?** | Whether teams can see sprint-to-metric impact | "Weekly lessons completed" (lagging, but achievable) | "5-year customer LTV" (too broad, too lagging) |
| **4. Is it resistant to gaming?** | Whether moving the metric requires actual value creation | Can't inflate without real engagement (durable) | Push notifications inflate DAU; shortening idle timeout inflates sessions (hollow activity) |
| **5. Does every team recognise their work in it?** | Whether all functions see a path from their work to this number | Engineering, Design, CS all own a piece of the outcome | Only Growth can move it (it's a growth metric, not a north star) |

---

### The three bad NSM candidates most teams reach for

**❌ Revenue or ARR**
- Measures what you *extracted* from customers, not what you *delivered* to them
- Healthy signal in bull markets; lagging disaster indicator when things turn
- **Why it fails the filter:** Flunks #1 (activity not value), #2 (IS revenue, not causal to it)

**❌ Registered users or total signups**
- Growth metrics, not value metrics
- A dormant user base is not a healthy product
- **Why it fails the filter:** Flunks #1 (activity not value), #5 (growth team only)

**❌ NPS or satisfaction score**
- A survey response is not a behaviour
- Users say they love products they don't use
- Too indirect, too slow, too gameable (ask at peak delight = inflated scores)
- **Why it fails the filter:** Flunks #4 (easily gamed), #3 (too lagging to move in a sprint)

## W2. The decisions your NSM forces

### Single NSM vs metric portfolio

Every company eventually debates this. Teams with 3+ product lines argue that a single NSM ignores whole segments of the business.

| | **Single NSM** | **Metric portfolio (2–4 metrics)** |
|---|---|---|
| Best for | Single-product companies, early-stage, hypergrowth phase | Multi-product, multi-segment, or platform businesses |
| Alignment | Maximal — one answer to "are we winning?" | Harder — teams can always point to their metric |
| Gaming risk | Higher — single point of failure | Lower — harder to game multiple metrics simultaneously |
| Strategic clarity | High — every team knows the target | Medium — portfolio metrics can conflict |
| **Default** | **Use single NSM unless you have 3+ distinct user jobs** | Only when product lines have genuinely different value definitions |

> **PM default:** Start with one. Most teams that "need" a portfolio are avoiding the hard conversation about what actually matters. Add a second metric only when the first structurally cannot represent a major user segment. A practical trigger: when a second product line reaches 25% of users or revenue, revisit whether the original NSM still captures the whole business.

### Output metric vs input metric as NSM

| | **Output metric** | **Input metric** |
|---|---|---|
| Example | "Nights booked" (Airbnb) | "Listings with 5+ reviews" |
| What it measures | Value delivered | What drives value delivery |
| Responds to | Product quality, demand | Supply investment, operational work |
| Strategic horizon | Months to years | Weeks to months |
| **Default** | **Use output metric as NSM** | Use input metrics as leading sub-metrics below NSM |

> **Output metric:** Measures the actual value your product delivers to users. This is what should drive your strategy.

> **Input metric:** Measures what causes value delivery to happen. These belong in squad-level KRs, not at the NSM level.

> **PM default:** Output metrics as the NSM. Input metrics as the squad-level KRs that feed it. Don't confuse "we can move this faster" (input) with "this is what matters" (output).

### When to change your NSM

Resist the temptation. Companies that change their NSM frequently signal one of two problems:
- **Strategic error** — the original NSM was wrong from the start
- **Accountability avoidance** — the new one is more flattering than the last

**Legitimate reasons to change:**
- The product fundamentally shifted its value proposition
- You discovered the original metric was gameable and structurally misleading

## W3. Questions to ask your team and leadership

### "What's our north star metric right now?"

*What this reveals:* If different people give different answers — or anyone says "it depends on the team" — you don't have a real NSM. You have aspirational alignment theatre. This question exposes that faster than any audit.

---

### "When did it last move significantly, and why?"

*What this reveals:* Teams that can answer this have a real relationship with the metric. Teams that can't are tracking it on a dashboard nobody reads. If the last significant move was 6 months ago and nobody remembers why, the metric has no operational presence.

---

### "What did we ship last quarter that was designed to move it?"

*What this reveals:* If no one can name a feature, the NSM is a strategy document artefact, not an operating metric. The answer should be immediate — "we shipped X in Q2, it moved the NSM by N%."

---

### "Can someone on the engineering team draw the causal path from their current sprint to the NSM?"

*What this reveals:* Tests whether the NSM has actually been decomposed into input metrics at the squad level. If engineers can't see the connection, they're not building toward it — they're building toward their PM's ticket descriptions.

---

### "What would it mean for the NSM to go up 20% without the business actually being healthier?"

*What this reveals:* Forces the team to think about gaming vectors. If there's an obvious answer (send more push notifications, make re-login mandatory), the metric is fragile. A good NSM should require genuine value creation to move.

---

### "Does our NSM capture value for all our core user segments?"

*What this reveals:* For multi-sided platforms (marketplaces, B2B2C), an NSM that only captures one side of the market creates a blindspot. "Rides completed" captured Uber's rider value but didn't capture driver supply health until supply crises became acute.

---

### "At what NSM level would you feel confident raising prices or expanding?"

*What this reveals:* Forces the CFO/leadership team to connect the NSM to business threshold decisions. If they can't answer, the NSM hasn't been operationalised at the business level. If they can, you have a built-in trigger for strategic milestones.

## W4. Real product examples

### Spotify — Time spent listening per user per month

**What:** Made "time spent listening" the internal operating metric, not "monthly active users," despite MAU being the headline for investors.

**Why it worked:** 
- Listening time captures *value delivered* — a 40-hour/month user gets more value than one who opens the app twice
- MAU masks retention quality; listening time exposes it
- Reveals engagement depth that DAU wouldn't show

**Takeaway:** When your revenue model is subscription, the NSM that matters is value depth per paying user — not reach. Reach is a growth metric. Depth is the north star.

---

### Airbnb — Nights booked

**What:** Anchored the entire company — supply growth, demand, product, trust & safety — on a single output metric: nights booked.

**Why it worked:**
- "Nights booked" requires *both* supply (hosts listing) and demand (guests booking) to be healthy
- A single metric with two inputs forced cross-functional alignment that separate supply and demand metrics couldn't create
- Every team could see their direct contribution

**Takeaway:** The best NSMs for two-sided platforms are the transaction that requires both sides to succeed. If your metric can go up when only one side is healthy, it will be gamed.

---

### Duolingo — Daily Active Users (completed at least one lesson)

**What:** Used DAU as their NSM — but with a strict definition: a DAU counted only if the user completed at least one lesson, not just opened the app.

**Why it worked:**
- The definition change is everything — loose DAU (app open) enables engagement inflation through push notifications
- With "completed a lesson" DAU, you can only move the metric by making the lesson worth doing
- Forced the product team to improve completion rates, not just open rates

**Takeaway:** The definition of your metric is as important as the metric itself. Two teams tracking "DAU" can have completely different NSMs depending on how they define an "active" session.

---

### Slack — Messages sent per active team per week (B2B SaaS)

**What:** Identified that teams sending 2,000+ messages collectively had a retention rate above 93%, versus ~50% for teams below that threshold. Used "messages sent per team" as their activation and engagement NSM.

**Why it worked:**
- In a team collaboration tool, individual user activity is noise — what matters is whether the team is using it as a communication layer
- 2,000 messages is a proxy for "this team now communicates through Slack"
- Seat count could grow while teams remained dormant; messages exposed that gap

**Takeaway:** For B2B products, the unit of value is often the team or account, not the individual user. A metric that tracks individual activity in a product built for groups will give you a false picture. Define value at the right unit of analysis.

---

### HubSpot — Companies with 5+ contacts added in the last 30 days (B2B enterprise CRM)

**What:** Defined their operating NSM not as "seats activated" or "logins per week" but as "companies with active contact entry" — the signal that a customer was actually running their CRM.

**Why it worked:**
- A CRM where no one enters contacts is a failed implementation, regardless of login rates
- Companies hitting the 5-contact threshold had dramatically higher 12-month retention and expansion revenue
- The metric captured whether the core job (managing contacts) was actually being done

**Takeaway:** For B2B products, seat activation is almost always the wrong NSM. Define your NSM as evidence that the customer's job is being done — not as evidence that users have shown up.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: senior PMs, heads of product, AI-native PMs
# Assumes: Working Knowledge. You can select and validate an NSM.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### The vanity metric coronation

> **Vanity Metric:** A metric that looks healthy but measures flattery rather than value—typically never decreases and grows through spending alone.

**The problem:** Total registered users is the most common example. It never goes down and is easy to grow through acquisition spend, requiring no relationship between growth and retention.

**The mechanism of failure:**
- Leadership reports it as a health signal for years
- Underlying value metrics (active retention, engagement depth) quietly erode
- By the time the revenue line responds, the product has been in decline for 12–18 months

**Red flag:** If your NSM can't go down, it's not measuring health.

---

### The metric that gets managed, not moved

**The problem:** Within 6 months of committing to an NSM, teams discover operational levers that move the metric without requiring real product work.

| Operational Lever | What happens | Why it's hollow |
|---|---|---|
| Push notifications | DAU increases | No engagement improvement |
| Mandatory re-onboarding | Activation rates inflate | Artificially classifying existing users |
| Shortened session timeouts | Session counts increase | Fragmentation, not quality |

**Prevention strategy:**
1. Define the NSM's gaming vectors *before* committing to it
2. Track counter-metrics from day one:
   - Session length after re-engagement
   - Retention at day-30 for "activated" users

---

### NSM drift

**The problem:** A single-product company becomes multi-product, but the original NSM remains unchanged.

**What happens:**
- New product lines adopt their own local metrics
- The "company NSM" loses authority unofficially
- Teams reference local metrics in roadmap reviews instead
- Original NSM becomes a legacy slide

**The mechanism:** Strategic discontinuity without explicit NSM renegotiation.

**Prevention:** When a new product line reaches **20%+ of revenue or users**, formally revisit whether the NSM still represents the whole company's value proposition.

---

### The north star that points at the exit

⚠️ **Risk:** A company can optimize an NSM so hard that it creates structural damage elsewhere.

**Example scenario:**
- **NSM:** Daily streaks completed
- **Result:** Product ships features that make streaks hard to break (notifications, guilt mechanics, friction on quitting)
- **The outcome:** NSM grows while NPS and long-term retention decline

**The real problem:** Users stay because the product makes *leaving costly*, not because it delivers value.

**The mechanism:** The NSM captures a behavior that correlates with value under normal conditions but can be sustained through coercion.

**The fix:** Track counter-metrics alongside the NSM:
- Voluntary return rate
- Uninstalls following a session

## S2. How this connects to the rest of your work

| Lesson | Connection | Why it matters |
|--------|-----------|---|
| **06.04 DAU/MAU & Engagement Ratios** | Most common NSM candidates | Stickiness ratios reveal whether DAU growth is shallow or deep—not just how many users, but how engaged they are |
| **06.09 Counter Metrics** | Operationalises gaming prevention | Every NSM needs ≥1 counter-metric to detect when the NSM moves without creating real value |
| **06.02 Funnel Analysis** | NSM sits at funnel endpoint | Decomposes which funnel stages constrain NSM growth |
| **06.03 Cohort Analysis** | Validates NSM growth authenticity | Exposes cohort degradation hidden in aggregate metrics (new user inflation masking churn in older cohorts) |
| **05.03 Prioritisation Frameworks** | NSM anchors roadmap prioritisation | Makes "impact" comparable across features—RICE, ICE, and opportunity scoring only work when all teams score against the same metric |
| **06.08 Lagging vs Leading Indicators** | NSM sits in indicator hierarchy | NSM is typically lagging/coincident; this lesson covers selecting leading indicators that predict NSM movement |

## S3. What senior PMs debate

**The North Star Metric framework was designed for a different era — and applying it to 2025 multi-product companies actively distorts strategy.**

### The original context

The NSM framework emerged from hypergrowth single-product companies:

| Company | Year | Single value proposition | Why NSM worked |
|---------|------|-------------------------|-----------------|
| Facebook | 2008 | Social graph | One product, one growth lever |
| Spotify | 2010 | Music streaming | One product, one growth lever |
| Airbnb | 2012 | Home rentals | One product, one growth lever |

"Friends added in 10 days" was legitimate because Facebook *was* literally just a social graph with one job.

### Why it breaks at scale

Apply the same framework to a 2025 product company with:
- Core subscription product
- AI assistant
- Marketplace
- B2B tier

**Result:** Strategic tunnel vision. Every product line gets evaluated against a value definition designed for a different product. The AI assistant's value is captured differently than the marketplace's. Optimising both against a single metric produces a metric that fits neither perfectly.

> **The serious critique:** Not that NSMs are wrong — it's that the *single* NSM model has aged out for most companies past Series B.

### The replacement model: Metric trees

**Structure:**
- **Trunk metric** = company's primary value proposition (owned by executives)
- **3–4 branch metrics per product area** = causally validated to roll up to trunk (owned by teams)

**Decision flow:**
- Prioritisation happens at the **branch level** (Is this sprint work moving our branch metric?)
- Strategy happens at the **trunk level** (Are our branches still causally connected to the trunk?)

**Failure mode prevented:** A single NSM technically applies company-wide but only captures one product line's health. Revenue grows while three branches go unwatered, and the dashboard won't surface it until they've been dry for a year.

### The counter-position worth taking seriously

| Metric trees risk | Single NSM benefit |
|-------------------|-------------------|
| Every team has its own number | Shared reality across teams |
| Cross-team debates regress into "our branch metric is up" | Forces teams to argue in same language |
| Language diverges into 12 branch metrics | Single shared number prevents metric fragmentation |
| Multiple realities, even if causally validated | Creates alignment discipline |

*What this reveals:* The tension isn't between "right" and "wrong" — it's between measurement precision and organizational alignment.

### What this means for PMs

**Under 50 engineers, single product:**
- Fight for a single NSM
- Alignment value outweighs measurement precision lost

**Multi-product company:**
- Don't spend six months finding the perfect single metric
- Build a metric tree, causal-validate the branches
- Use trunk as **strategy metric** — not operating metric
- Know which one you're building for

### A third complication: AI products break NSM causality

The standard NSM framework assumes: *product decisions → NSM movement*

**For AI-native products, two things break this:**

1. **Non-deterministic value delivery** — same user action produces different outputs on different days, so "sessions completed" doesn't capture output quality
2. **Model updates bypass PM decisions** — version changes alter what the product delivers without any PM work, making the causal link intermittent

**The practical response:** AI products need a quality layer below the NSM

```
NSM (business metric)
     ↓ depends on ↓
Quality layer (task-completion rate, output accuracy, thumbs-up ratio)
     ↓ detects when ↓
Model update has silently shifted the value NSM measures
```

⚠️ **Risk:** Running NSM-only on AI products masks silent value degradation from model updates

### The meta-skill

The real skill isn't picking the right metric. It's knowing when to change the framework, not just the number.

## Related lessons

### Prerequisites
- No hard prerequisites. Familiarity with DAU, MAU, and conversion rate assumed.

### Next: read alongside (companions)
- 06.02 Funnel Analysis — decompose the inputs that drive your NSM
- 06.04 DAU/MAU & Engagement Ratios — the most common NSM candidates, and when they mislead
- 06.09 Counter Metrics — how to prevent NSM gaming with guardrail metrics

### Read after (deepens this lesson)
- 06.03 Cohort Analysis — whether NSM aggregate growth is masking cohort-level decline
- 06.08 Lagging vs Leading Indicators — how to select leading sub-metrics that predict NSM movement
- 05.03 Prioritisation Frameworks — how NSM anchors impact scoring across competing features