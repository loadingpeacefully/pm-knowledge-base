---
lesson: DAU/MAU & Engagement Ratios
module: 06 — metrics-and-analytics
tags: product, business
difficulty: working
prereqs:
  - 06.01 — North Star Metric: DAU/MAU is often a north star candidate; you need the framework to evaluate whether it's the right one for your product
  - 06.03 — Cohort Analysis: engagement ratios are aggregate; cohort analysis shows whether those aggregates are improving for new users
writer: senior-pm
qa_panel: Senior PM, CFO/Finance Lead, Junior PM Reader
kb_sources:
  - performance-reviews/apr24-mar25-performance-review.md
  - technical-architecture/student-lifecycle/student-feed.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, head of product, AI-native PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

In the early days of consumer internet, companies measured success by total registered users. "We have 10 million users" sounded impressive. But a user who signed up once, never came back, and whose account sits dormant counts the same as a user who shows up every day. Total users is a cumulative number — it can only go up, it never tells you if your product is alive or dead.

The industry needed a way to measure not just who had ever used a product, but who was actually using it right now. Two numbers became the standard: how many people used the product today (Daily Active Users, or DAU) and how many used it in the past month (Monthly Active Users, or MAU).

Together, these numbers — and especially their ratio — answer the question no vanity metric could: is this product a habit, or a one-time visit?

## F2 — What it is, and a way to think about it

> **DAU (Daily Active Users):** The number of unique users who perform a meaningful action in your product on a given day.

> **MAU (Monthly Active Users):** The number of unique users who perform a meaningful action in your product in a given month.

> **DAU/MAU ratio (Stickiness):** DAU divided by MAU, expressed as a percentage. It answers: "Of all the people who used this product this month, what fraction came back today?"

### A concrete way to think about it

Imagine a gym with 1,000 monthly members:

| Scenario | Daily visitors | DAU/MAU ratio | What it means |
|----------|---|---|---|
| Habit-forming gym | 300 per day | 30% | Members have built a routine |
| Low-engagement gym | 50 per day | 5% | Members signed up but mostly inactive |

The same logic applies to digital products:

| Product type | DAU/MAU ratio | What it means |
|---|---|---|
| Social media app | 50% | Half of all monthly users are active daily — deeply embedded in routine |
| News app | 10% | Most users check in only a few times per month |

**Important:** Neither number is inherently good or bad—it depends entirely on what the product is supposed to do and how often users naturally need it.

> **Stickiness ratio:** Another name for DAU/MAU ratio, emphasizing that it measures whether the product creates habitual return behavior.

## F3 — When you'll encounter this as a PM

| Context | What happens | Why it matters |
|---------|--------------|----------------|
| **Product health reviews** | DAU/MAU discussed in weekly and quarterly reviews | You'll be expected to know your product's metrics, benchmarks, and trends |
| **Feature prioritization** | Engagement features evaluated by DAU/MAU impact | Determines which features (notifications, feeds, streaks, personalization) get built |
| **Fundraising & investor conversations** | DAU/MAU used as quick health signal | High stickiness signals product-market fit; low stickiness raises retention concerns |
| **Growth decisions** | DAU/MAU trend informs acquisition vs. retention priorities | Spending on acquisition while stickiness declines = "pouring water into a leaking bucket" |

### Company — BrightChamps Student Feed

**What:** Redesigned the dashboard as a "habit-forming destination rather than a utility visited only before or after class"

**Why:** Explicitly structured to improve DAU/MAU ratio

**Takeaway:** Engagement-focused features are evaluated by their ability to move stickiness metrics, not just DAU in isolation
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Defining "active"

The most important decision in calculating DAU/MAU is what counts as an "active" user. The definition dramatically affects the numbers.

| Strength | Definition | Example | Risk |
|---|---|---|---|
| **Weakest** | App open / any session | User opens app for 2 seconds and closes | Inflates DAU; hides real engagement |
| **Moderate** | Any meaningful action | User clicks something or reads something | Still broad; includes low-intent users |
| **Strongest** | Core product action | BrightChamps: attending class or viewing feed; Spotify: playing song; Slack: sending message | Most accurate measure of genuine engagement |

#### BrightChamps Student Feed — Explicit engagement signals
- Likes per session
- Replies per session  
- Return visits to feed page

Each is a more meaningful "active" signal than a raw login.

---

### The stickiness ratio in practice

> **DAU/MAU interpretation:** 50%+ = excellent for social/daily-use products | 20–30% = healthy for consumer apps | Under 10% = weekly/occasional use (fine for some products, problematic for habit-driven revenue)

| Product | DAU/MAU | Period | Notes |
|---|---|---|---|
| Facebook | ~65% | 2014–2018 peak | Declined post-2020 as engagement definition tightened |
| Twitter / X | ~40% | Pre-2022 acquisition | Applied to "monetizable DAU" segment only |
| Consumer mobile apps | 10–25% | 2023–2024 avg | Median; category varies significantly |
| Daily habit products (Duolingo, Wordle) | 50%+ | 2022–2024 | Streak mechanics drive daily return |

⚠️ **Historical benchmarks are not comparable:** Facebook and Twitter changed "active" definitions post-2020. Use category-appropriate 2023–2025 benchmarks where available; treat 2014–2018 figures as directional only.

---

### WAU and other intervals

> **WAU (Weekly Active Users):** The appropriate metric for products designed for regular weekly engagement, not daily use.

**When to use WAU instead of DAU/MAU:**
- Education products with 3 classes/week
- Fitness apps with weekly training patterns
- Any product with natural weekly cadence

**WAU/MAU (weekly stickiness)** — the fraction of monthly users who return in any given week — better reflects health for education, fitness, and similar weekly-cadence products.

---

### Session depth and quality metrics

> **Session depth:** Measures what users did when they arrived, beyond just showing up.

| Metric | What it captures | Relevance |
|---|---|---|
| **Session length** | Duration of each session | Engagement intensity |
| **Actions per session** | Meaningful actions taken | Behavioral commitment |
| **Feature penetration** | % of DAUs using a specific feature | Feature adoption health |

#### BrightChamps Student Feed session quality
- Feed posts engaged (liked/commented)
- Class cards clicked
- Return visits within 24 hours

*What this reveals:* A student who opens the feed and closes it counts as DAU but contributes nothing to session quality. Growth in DAU without growth in session quality signals passive presence, not real engagement.

---

### The engagement pyramid

Not all DAUs are equal. Segment active users by behavior depth:

| Tier | Behavior | Typical % of DAU |
|---|---|---|
| **Core engaged** | Performs primary value action (class attended, message sent, song played) | 20–40% |
| **Casually engaged** | Browses but doesn't complete core action | 30–50% |
| **Passive** | Opens app, minimal interaction | 20–40% |

*What this reveals:* DAU growth can come from real engagement or just passive presence. Understanding your pyramid tells you which.

---

### Tracking DAU/MAU over time

**Direction matters more than absolute number:**
- Product at 25% DAU/MAU declining 6 months = worse shape
- Product at 15% DAU/MAU consistently improving = better trajectory

**Track separately, not just the ratio:**
- Plot DAU and MAU as individual lines
- Ratio can stay stable while both numbers fall (if they decline proportionally)
- Reveals whether stickiness is stable or masking broader decline

## W2 — The decisions this forces

### Quick Reference: Metrics by Product Type

| Product type | Appropriate interval | Right metric |
|---|---|---|
| Social apps, messaging, news | Daily | DAU/MAU |
| Education, fitness, gaming | Weekly | WAU/MAU |
| E-commerce | Purchase occasions | Orders per active user per quarter |
| B2B SaaS | Weekly or per-task | Active users per seat, feature adoption rate |
| Annual subscription services | Monthly at most | MRR retention, annual renewal rate |

---

### Decision 1: Is DAU/MAU the right north star for your product?

DAU/MAU is a relevant metric only if daily or near-daily engagement is part of your product's value model. For products where usage is inherently episodic — tax preparation software (annual), flight booking (a few times per year), contract management (monthly) — high DAU/MAU is impossible and irrelevant. Optimizing for it would mean making the product artificially stickier in ways that don't map to real user value.

> **DAU/MAU relevance test:** How often should a healthy user be using this product? If "daily," DAU/MAU is right. If "a few times a week," WAU/MAU is better. Tracking the wrong interval creates false signals.

---

### Decision 2: How to increase DAU/MAU — engagement vs notification abuse

The two most reliable ways to increase DAU/MAU are:

**Path A (Sustainable):** Make the product genuinely more valuable so users want to return daily.

**Path B (Short-term extraction):** Trigger users to return through notifications and re-engagement campaigns regardless of whether there's new value.

#### The Path B collapse mechanism

1. Push notifications increase open rate → DAU ticks up
2. Users who don't find value disengage → notification opt-out rate rises (industry data: aggressive push campaigns can push opt-out **above 50% within 30 days**)
3. Once notifications are disabled, the product loses its re-engagement channel entirely
4. 30-day retention for notification-acquired DAU is typically **20–40% lower** than organically returning users

#### The product-dependence caveat

Some notification-heavy products work because the notifications *are* the value (WhatsApp messages, calendar reminders, real-time sports scores). The test isn't whether notifications trigger the return — it's whether the user finds value after arriving.

- ✓ **High-quality DAU:** Student gets "your class starts in 10 minutes" reminder and attends class
- ✗ **Low-quality DAU:** Student gets "check out this leaderboard!" notification and closes the app in 3 seconds

#### Example: Path A in practice

**BrightChamps — Student Feed**

**What:** Auto-generated content (class cards, achievement cards, homework reminders)

**Why:** Gives students a genuine reason to return daily — not a notification trick, but a personalization feature that creates new content to check.

**Takeaway:** Sustainable DAU growth requires new reasons to return, not louder interruptions.

⚠️ **Notification audit rule:** If your DAU/MAU improvement strategy is primarily "more notifications," track two counter metrics: notification opt-out rate (should stay under 20% for any new campaign) and 30-day retention for notification-acquired users vs. organic returnees.

---

### Decision 3: Separating DAU and MAU trends

A stable DAU/MAU ratio doesn't mean the product is healthy. Both numbers could be declining proportionally — fewer total monthly users with the same fraction coming back daily. Always track DAU and MAU as absolute numbers in addition to the ratio.

#### Diagnostic patterns

| Pattern | What it signals | Implication |
|---|---|---|
| MAU growing, DAU flat | Acquiring users but not converting them to daily habits | Activation/engagement problem |
| DAU growing, MAU flat | Existing users becoming more active; few new users | Growth/acquisition problem |
| Both growing, ratio stable | Healthy scaling | Monitor that ratio doesn't compress as audience grows |
| Both declining, ratio stable | Product is contracting evenly | Retention or market problem |
| DAU/MAU declining with both numbers | Product losing its most engaged users fastest | Serious health signal ⚠️ |

> **Dashboard essential:** Add a 4-week trend line to your DAU/MAU dashboard so direction is always visible. A single-period snapshot is nearly useless for decision-making.

---

### Decision 4: Segment DAU/MAU by user type

Aggregate DAU/MAU hides the engagement patterns of your most important user segments. A product might have 30% overall DAU/MAU, but:
- Paid users: 55%
- Free users: 15%

This meaningful segmentation drives different product decisions.

#### Example: BrightChamps cohort split

**What:** Demo students (pre-conversion) vs. paid students (enrolled) have fundamentally different engagement needs.

**Why:** Tracking DAU/MAU separately reveals whether the Student Feed is driving habit formation where it matters most.

**Takeaway:** Aggregate metrics can hide that your most valuable users are churning while your least valuable ones are highly active.

> **Segmentation baseline:** Always report DAU/MAU at the segment level for: paid vs free, new vs returning, mobile vs desktop.

---

### Decision 5: When to prioritize DAU/MAU vs other engagement metrics

DAU/MAU measures **breadth of engagement** (how many users return). It does *not* measure:
- **Depth:** How much value they get per session
- **Quality:** Whether they're doing the thing that creates value
- **Revenue:** Whether engaged users are monetizable

A product can have excellent DAU/MAU while generating poor revenue — users return daily but never pay. A product can have modest DAU/MAU but extraordinary per-session value — users return less often but each session drives meaningful business outcomes.

#### Real case: Twitter's mDAU

Some users were counted as "active" in ways that couldn't be monetized (bots, embeds, logged-out views). Counting them inflated DAU without actually representing business health. Twitter introduced **mDAU (monetizable DAU)** to solve this.

> **Engagement hierarchy:** Use DAU/MAU as a leading indicator of engagement health, not as a direct business metric. Always pair it with a conversion or revenue metric to distinguish active users who generate value from active users who are just browsing.

## W3 — Questions to ask your engineer

| Question | Why it matters | Good answer | Push back if |
|----------|---|---|---|
| **1. "What's our definition of 'active' for DAU and MAU calculation?"** | The definition determines whether the number is trustworthy. "Any app open" = meaningless. "Core product action performed" = real signal. | A specific, named event or action with documented rationale for why it was chosen | Definition is "any session" or "any login" — these systematically inflate engagement metrics |
| **2. "Are we counting unique users per day/month, or total sessions?"** | DAU measures unique users. A user opening the app 10 times on Monday should count once, not 10 times. Session-based counting inflates the metric. | Unique users, deduplicated by user_id within the period | Calculation is session-based or deduplication isn't confirmed |
| **3. "How are we handling multi-device users? Does a user who logs in on both mobile and desktop count once or twice?"** | Multi-device counting is a subtle but common source of DAU inflation. Some teams count device sessions, not user sessions. | User-level deduplication by user_id, not by device | Device-level tracking is used without user-level reconciliation |
| **4. "What's the latency on our DAU calculation? Are we seeing yesterday's data or real-time?"** | During a product launch or incident, you need near-real-time DAU. Nightly batch jobs mean you're always 24 hours behind, limiting operational decisions. | Specific latency stated (e.g., "30-minute delay from event to dashboard") | No one knows the latency — this indicates a data infrastructure gap that limits your ability to react |
| **5. "Are bots, test accounts, and internal traffic excluded from DAU/MAU?"** | QA automated tests, scrapers, and monitoring scripts inflate DAU. Internal employees may or may not belong depending on product type. | Specific exclusion list: bot IPs, test account IDs, internal employee filters | No filtering is applied — high-traffic products almost always have non-human traffic distorting engagement numbers |
| **6. "How do we handle users who were active in the last 28 days vs. the calendar month for MAU?"** | Calendar month MAU creates artificial seasonality (Jan = 31 days, Feb = 28). Rolling 28-day MAU is more consistent and comparable period-over-period. | Explicit methodology stated (rolling window or calendar month), with consistency confirmed across all time periods | Methodology varies — inconsistent MAU calculation makes period-over-period comparisons meaningless |
| **7. "Can we segment DAU/MAU by feature or product area?"** | If the entire platform's DAU bundles all actions together, a new feature's specific contribution to engagement becomes invisible. Example: BrightChamps's Student Feed DAU must be separable from class attendance and other actions. | Feature-level DAU tracking exists or can be created with specific events | All engagement is aggregated with no feature attribution — you'll be unable to measure whether the feed is actually working |
| **8. "What's our current DAU/MAU and how does it compare to 3 months ago?"** | The trend matters more than the absolute number. Direct questions about 3-month trends force the team to have a prepared view, not just a point-in-time number. | Specific numbers with trend direction | "We don't track that historically" — a basic engagement metric with no historical tracking is a data infrastructure gap |

*What each question reveals:* These eight questions expose whether your engineering team has intentional, defensible engagement metrics or inflated vanity numbers. Strong answers indicate mature data infrastructure. Weak answers indicate you're making product decisions on unreliable signals.

## W4 — Real product examples

### BrightChamps — Student Feed as a DAU/MAU improvement initiative

**What:** Auto-generated class cards, achievement badges, homework reminders, and pinned upcoming classes designed to create daily check-in reasons beyond class scheduling.

**Why:** Students visited the dashboard only before/after class (utility behavior), not habitually. The feed aimed to increase daily active user ratios by making the product a habit rather than a scheduling tool.

**Measurement approach:**
| Metric | Purpose |
|--------|---------|
| Return visits to feed page | Direct DAU/MAU proxy |
| Likes per session | Engagement depth |
| Replies per session | Community interaction |
| Variant (feed enabled) vs. control (no feed) | A/B testing infrastructure |

**Takeaway:** Success criteria were defined in engagement terms—if the feed drives daily return visits, it improves the DAU/MAU ratio. Feature-level metrics alone were insufficient.

---

### Facebook — stickiness as a PMF signal

**What:** "7 in 10 days" threshold—users returning 7 of their first 10 days after signup—used as the internal metric for product-market fit.

**Why:** Cohort analysis revealed that users meeting this threshold had dramatically higher long-term retention. This individual-level habit formation aggregates into strong DAU/MAU at scale.

**What this reveals:** Facebook later achieved ~65% DAU/MAU—one of the highest stickiness ratios of any large consumer product—driven by social graph density and the daily habit of social checking.

**Takeaway:** The "7 in 10 days" metric became the benchmark against which other social products measured themselves.

---

### Twitter — mDAU as a response to DAU inflation

**What:** mDAU (Monetizable Daily Active Users) launched in 2019 to count only users who log in and see ads, excluding embedded tweet views, automated accounts, and logged-out views.

**Why:** Raw DAU numbers were inflated and misleading—presence ≠ monetizable engagement.

**The distinction:**
| Metric | What it counts | Why it matters |
|--------|----------------|----------------|
| DAU | Presence (any active view) | Can inflate through bot activity or third-party embeds |
| mDAU | Monetizable engagement (logged-in, ad-served) | Reflects actual revenue-generating users |

⚠️ **Strategic risk:** Optimizing raw DAU can lead to counting users who generate no revenue and have no product relationship. For advertising or subscription models, this distinction is critical.

**Takeaway:** DAU measures presence, not monetizable engagement. Industry lesson: honest metrics require distinguishing between "active" and "monetizable active."

---

### Duolingo — streaks as a DAU/MAU engineering mechanism

**What:** A streak counter that tracks consecutive practice days and resets on missed days, creating a daily obligation through loss-aversion psychology.

**Why:** Missing a day destroys the streak, which users find psychologically costly. Result: Duolingo's DAU/MAU consistently exceeds education app industry averages.

**The engagement tension:**
| User Type | Behavior | Engagement Profile |
|-----------|----------|-------------------|
| Streak-driven returners | Return to protect streak | Habitual presence |
| Learning-driven returners | Return to learn | Genuine engagement |

**Takeaway:** Streaks drive daily returns, but this creates a distinction between users returning for habit vs. users returning for product value. Duolingo tracks both metrics to understand which type of engagement they're optimizing.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The active definition arms race

As DAU/MAU became a standard investor metric, companies expanded their definition of "active" to maximize the number.

| What counts as "active" | Problem |
|---|---|
| Opening the app | Inflates true engagement |
| Receiving a notification | May be passive exposure |
| Embedded widget loads on third-party sites | Inadvertent, not intentional use |

> **The core issue:** Facebook, Twitter, and Snapchat have all been criticized for definitions that include passive or inadvertent exposures as "active" users.

**The cascading trap:**
- Metric inflates → Investors rely on it → Actual engagement health is hidden
- Teams that inherit an inflated DAU definition are stuck — making the definition stricter will cause an apparent drop in DAU, which looks like a decline even if actual engagement didn't change

---

### DAU/MAU divergence from revenue

A product can sustain excellent DAU/MAU while generating poor revenue per user.

**Three common scenarios:**

1. **Limited monetization scope** — Monetization applies to only a subset of daily users
2. **Low-CPM ads** — The ads shown to daily users are low-value
3. **Wrong behavior context** — Daily behavior doesn't create the conditions for monetization

**Real-world comparison:**

| Platform | DAU/MAU | Revenue-per-active-user |
|---|---|---|
| YouTube | High | High |
| Wikipedia | High | Low |

⚠️ **BrightChamps risk:** If the Student Feed drives daily feed visits but doesn't improve class attendance rates or subscription renewal, the engagement is vanity rather than value.

**What teams miss:** Hitting DAU/MAU targets and celebrating without checking revenue-per-active-user may mean the engagement built doesn't translate to business outcomes.

---

### The notification inflation trap at scale

Push notifications follow a predictable but hidden failure curve:

| Scale | Effect | Outcome |
|---|---|---|
| Small scale | Reliably increase DAU | Positive growth |
| Large scale, early | Marginal returns begin | Growth slows |
| Large scale, ongoing | Habituation or annoyance | DAU declines |
| After 6–12 months | User fatigue compounds | Churn accelerates |

⚠️ **The lag problem:** Declining DAU/MAU often appears 6–12 months after notification frequency increases, making the causal connection hard to see.

**Misdiagnosis trap:** Teams that attribute declining DAU/MAU to other factors while ignoring notification frequency often miss the actual root cause.

---

### The new user vs retained user DAU composition problem

> **The composition problem:** DAU is a composite of new users (in their first week) and retained users (longer tenure), but they behave differently.

**How DAU can mislead:**

| User cohort | Session frequency | Impact on DAU |
|---|---|---|
| New users (first week) | High (exploring) | Inflates DAU/MAU during high acquisition |
| Retained users | Low (established patterns) | Lowers DAU/MAU when acquisition slows |

**The false signal:** When acquisition slows, high-exploration new users are replaced in the DAU calculation by fewer, lower-frequency retained users. DAU/MAU appears to drop even if the product hasn't gotten worse.

**The fix:** Separate "new user DAU" from "retained user DAU" in your analysis — this is the only way to distinguish acquisition-driven DAU from retention-driven DAU.

## S2 — How this connects to the bigger system

| Concept | What it does | Key question |
|---------|-------------|--------------|
| **North Star Metric (06.01)** | Identifies whether DAU/MAU predicts real business value | "Does high DAU/MAU actually move revenue or retention in our business?" |
| **Cohort Analysis (06.03)** | Reveals trends hidden in aggregate metrics | Are new-user cohorts improving, or is overall DAU/MAU masking decline? |
| **Funnel Analysis (06.02)** | Shows user entry and conversion separately from engagement | Is the problem growth (poor funnel) or retention (poor DAU/MAU)? |
| **Feature Flags (03.10)** | Isolates a feature's true impact via A/B testing | Did the feed drive DAU gains, or were other changes responsible? |
| **Counter Metrics (06.09)** | Prevents optimizing the metric while harming the business | Is DAU growth real habit formation or just metric gaming? |

---

### North Star Metric (06.01)

> **North Star:** A single metric that represents the core value your product delivers

DAU/MAU works well for **habit-forming consumer products** but fails for products where daily engagement isn't the actual value model. Teams often learn this painfully by optimizing DAU/MAU only to find it doesn't move revenue or retention.

**The litmus test:** If high DAU/MAU clearly predicts business health, it's a good north star. If the connection is unclear, it's misleading.

---

### Cohort Analysis (06.03)

**The problem it solves:** Aggregate DAU/MAU can appear stable while new-user cohorts deteriorate.

**How it works:** Break DAU/MAU by signup period to see whether the product actually improves for users entering *now* versus users from earlier periods.

**Applied example:** Evaluate the BrightChamps Student Feed by comparing DAU/MAU for cohorts onboarded *after* launch versus *before* launch—not just overall DAU/MAU movement.

---

### Funnel Analysis (06.02)

> **Funnel vs. DAU/MAU:** Funnel shows how users *enter*; DAU/MAU shows whether they *stay*

These metrics diagnose different problems:

- **Great funnel + poor DAU/MAU** = engagement problem
- **Poor funnel + great DAU/MAU** = growth problem

---

### Feature Flags (03.10)

⚠️ **Risk:** Without a control group, you cannot attribute DAU changes to your new feature. Other concurrent changes will create false credit.

**Standard practice:** Release features affecting DAU/MAU with feature flags and measure against a control group.

**BrightChamps example:** The Student Feed uses A/B testing and feature flags to isolate the feed's contribution to DAU before full rollout.

---

### Counter Metrics (06.09)

> **Counter Metric:** A secondary metric that reveals whether your north star improvement is real or gaming

Any DAU/MAU initiative needs counter metrics matched to the driver:

| DAU Driver | Counter Metric | What it reveals |
|-----------|---|---|
| Notifications | Opt-out rate | Are users actually engaged or just being pushed? |
| Streaks | Streak break recovery rate | Do users return after breaking, or churn? |
| Feed views | Views without engagement | Is presence real or passive scrolling? |
| Feature usage | Class cancellation rate | Does it improve real behavior (attendance) or just metrics? |

## S3 — What senior PMs debate

### **"Is DAU/MAU a product metric or a business metric?"**

| Perspective | View | Risk |
|---|---|---|
| **Traditional** | DAU/MAU = success metric | Can mask unprofitable growth |
| **Senior PM consensus** | DAU/MAU = diagnostic signal only | Requires explicit translation to revenue/LTV |

> **The core tension:** A company with 70% DAU/MAU can lose money. A company with 15% DAU/MAU can be highly profitable.

**The emerging framework:**
- DAU/MAU is a *leading indicator* of product health
- Requires explicit linking to: revenue, retention, or LTV
- Treat as early warning system, not success definition
- Decision-relevant only when connected to business outcomes

---

### **The habit vs utility debate for non-daily products**

**The tension:**

| Product Type | Engagement Goal | Trade-off |
|---|---|---|
| **Habit-based** | Daily return + notifications + gamification | Risk: degrades utility experience |
| **Utility-based** | Fast, clean, tool-like experience | Risk: appears "less engaged" by DAU metrics |

**Where this matters most:**
- B2B products
- Tools and SaaS
- Transactional services

**The unresolved debate:**
- *Utility advocates:* Adding social/notifications to utility products destroys the reason users chose them
- *Habit advocates:* Even utilities benefit from habitual familiarity; returning users upgrade more, refer more, engage with new features more

> **Current state:** No consensus. Answer depends entirely on whether there's a *genuine reason for daily use that creates real value*.

---

### **What AI is doing to engagement ratios**

**AI is restructuring engagement in two opposite directions:**

| Direction | Mechanism | Effect on DAU/MAU |
|---|---|---|
| **Deepening engagement** | AI-generated personalized content (feeds, recommendations, summaries) creates genuine new value per visit | ↑ Increases DAU/MAU |
| **Reducing engagement** | AI assistants answer questions on behalf of the product (user gets answer in 5 seconds via AI interface) | ↓ Decreases DAU/MAU |

**The measurement problem:**

⚠️ **DAU/MAU assumes:** engagement depth = value delivered

⚠️ **AI decouples this:** A user who gets their answer in 5 seconds appears "less engaged" than a user who navigates the full product for 10 minutes — despite receiving the same or better value.

**What this reveals:** Engagement ratios were designed for products where time-on-product correlates with satisfaction. AI interfaces break that assumption. Metrics haven't caught up to this reality yet.