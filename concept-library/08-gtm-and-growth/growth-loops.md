---
lesson: Growth Loops
module: 08 — gtm and growth
tags: product
difficulty: working
prereqs:
  - 08.02 — Product-Led Growth: PLG is the GTM motion built on growth loops; understanding PLG mechanics is required before analyzing the loops that drive it
  - 06.04 — DAU/MAU & Engagement Ratios: engagement loops are measured by DAU/MAU; understanding the metric is required before designing for it
  - 05.07 — Experimentation & A/B Testing: growth loops are validated through experiments; understanding experimentation is required to know if a loop is working
writer: gtm-lead
qa_panel: GTM Lead, CFO/Finance Lead, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/student-feed.md
  - technical-architecture/student-lifecycle/student-showcase-generating-project-videos-for-feed.md
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

Product growth used to be explained by funnels. You put users in the top (acquisition), some of them moved through the stages (activation, engagement, retention), and the ones who stayed became your user base. The funnel was linear: inputs → outputs. If you wanted more outputs, you added more inputs. More marketing spend → more users → more revenue.

This model works as a diagnostic tool but fails as a growth strategy. A funnel never fills itself. It requires continuous external input — ad spend, content, outbound sales — to generate each new batch of users. The moment you stop feeding the top, the funnel empties. Every user acquired by a funnel is a separate acquisition cost.

Growth loops are different. In a growth loop, existing users generate new users — or generate more value that attracts more users. The output of one cycle becomes the input of the next. When a loop is running, growth is compounding, not linear. Each user creates a fraction of the next user — and the system grows on its own.

This is the structural difference between companies that grow faster as they get bigger (Facebook, TikTok, LinkedIn — their content loops produce more content with more users, attracting more users) and companies that grow at a flat rate regardless of size (most consumer apps that rely entirely on paid acquisition).

The PM's job in growth is to identify which loops exist in the product, measure whether they're closing, and systematically remove the friction that keeps them from compounding.

## F2 — What it is, and a way to think about it

> **Growth loop:** A self-reinforcing cycle where product activity generates inputs that drive more product activity. Each cycle of the loop produces outputs that feed the next cycle. When the loop closes efficiently, growth compounds without requiring proportional input.

> **Loop closure rate:** The fraction of loop outputs that successfully become loop inputs in the next cycle. A loop with 80% closure rate is strong; a loop with 10% closure rate barely functions. Loop closure rate is the key metric for evaluating a loop's efficiency.

> **Acquisition loop:** A loop where existing users attract new users — through sharing, referral, viral content, or organic search driven by user-generated content.

> **Engagement loop:** A loop where using the product creates reasons to use the product more — through content accumulation, habit formation, social interaction, or increasing value with use.

> **Retention loop:** A loop where user investment in the product (data, customization, social connections) makes it harder to leave — compounding the retention of existing users over time.

> **Referral loop:** A specific type of acquisition loop where existing users explicitly recommend the product to new users, either incentivized or organic.

### A way to think about it

**The snowball model**

Think about a snowball rolling down a hill. At first, it's small — each rotation adds a thin layer of snow. But as the snowball grows, each rotation covers a larger surface area and collects more snow. The loop (rotation) stays the same; the output of each cycle grows because the inputs are larger.

**How it works in product**

A product growth loop follows the same pattern:

1. A student creates a showcase video
2. Parents share it to their network
3. Parents in the network sign up for demos
4. Some convert to paying students
5. Those students create more showcase videos

Each cycle of the loop produces new students, who produce new showcases, who produce new leads.

**The critical design principle**

The loop doesn't require the company to do anything between cycles. The students, parents, and new leads are doing the work. The company's job is to design the loop so that the cycle closes reliably.

## F3 — When you'll encounter this as a PM

| Context | What happens | Key question for loops |
|---|---|---|
| **Growth is plateauing** | DAU/MAU is flat despite stable acquisition spend | Are there loops in the product that should be compounding but aren't closing? |
| **Designing a new social feature** | Team builds a sharing or social mechanic | Will this feature close a loop (outputs become inputs) or just add activity with no compounding effect? |
| **Evaluating a viral mechanic** | "Should we add a 'share' button?" | Does sharing bring in new users who generate more content, or is it just activity? |
| **Diagnosing why growth is expensive** | CAC is rising; growth requires more spend each quarter | Is the product entirely funnel-dependent, with no loops? |
| **Building content or UGC features** | Product team adds user-generated content | Does the content attract new users organically? |
| **Internationalization** | Product expands to a new market | Does the loop that works in Market A transfer to Market B, or does it depend on local network effects? |

---

### BrightChamps — Two embedded growth loops in design

**Showcase acquisition loop (in development)**

**What:** Student completes coding project → records showcase video → video published to global feed → parent/peer shares externally → new visitors land on BrightChamps → some convert to leads → some become paying students → those students create showcases.

**Why:** Showcase videos are designed as organic proof of platform value. The explicit business goal in the PRD is "Visitors to Leads."

**Takeaway:** This is an acquisition loop where user outputs (videos) become inputs (social proof that attracts new users).

---

**Student Feed engagement loop**

**What:** Student attends class → feed auto-generates class card with completion status → student/parent opens feed to track progress → regular engagement creates daily habit → habit increases class attendance → consistent attendance generates more feed events.

**Why:** The feed was designed to make the student dashboard "a habit-forming destination rather than a utility visited only before or after class."

**Takeaway:** This is a retention/engagement loop where the product output (progress signals) reinforces the behavior (attendance) that generates more output.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Loop anatomy: inputs, actions, outputs, and closure

Every growth loop has four components:

> **Input:** What starts the cycle. For an acquisition loop, the input is a new user. For an engagement loop, the input is a user session.

> **Action:** What the user does that generates the loop's output. For a content loop, the action is creating content. For a referral loop, the action is sharing or inviting.

> **Output:** The result of the action that feeds the next cycle. For a content loop, the output is content that attracts new users. For a referral loop, the output is an invitation that brings a new user.

> **Closure:** The fraction of loop outputs that successfully restart the cycle. Calculated as: **closure rate = (loop outputs that become new inputs) ÷ (total loop outputs)**.

#### Worked example — BrightChamps showcase acquisition loop:

1. 100 students create showcase videos (loop inputs → actions → outputs)
2. 60 showcases pass moderation and become visible (60% moderation close rate)
3. 60 live showcases generate 600 external visitors (10 visitors per showcase average)
4. 600 visitors produce 30 trial bookings (5% trial conversion)
5. 30 trials convert to 12 paying students (40% trial-to-paid conversion)
6. 12 new paying students eventually create 8 showcases (67% create at least one showcase)

**Loop closure rate = 8 new showcases ÷ 100 original showcases = 8%**

This means: for every 100 showcase-creating students in the current cohort, the acquisition loop returns 8 new students who will eventually create showcases. K-factor equivalent ≈ 0.08. This is a weak but functioning loop — the product investment to improve moderation speed or add external sharing would have compounding returns.

> **Why closure rate is not per-user conversion:** The closure rate measures how well the *loop* restarts, not how well an individual user converts. A 5% trial conversion rate is a funnel metric. Loop closure rate measures whether the total system compounds — whether 100 units going in eventually produce more than 0 units for the next cycle.

---

### The four types of growth loops

#### 1. Content/UGC acquisition loop

User creates content → content is indexed or shared → content attracts new users → new users create more content.

**Examples:**
- TikTok (videos attract new viewers who become creators)
- YouTube (video creators attract subscribers who watch more video)
- BrightChamps Showcase (student videos attract new families who enroll students who create more videos)

**Key metric:** content → new user conversion rate. If content is being created but not attracting new users, the loop isn't closing on the acquisition side.

**PM design decisions:**
- What makes the content worth sharing?
- Is the content publicly accessible without login?
- Does the platform make sharing frictionless?
- Does the content quality improve with the platform's help?

#### 2. Viral/referral acquisition loop

User experiences product value → user invites or refers others → referred users join → they experience value and refer others.

**Referral types:**

| Type | Mechanism | Example |
|---|---|---|
| Product-native virality | Using the product creates a referral moment | Figma shared designs, Notion shared pages, Zoom meeting links |
| Incentivized referral | Explicit reward for referral | Dropbox storage, Uber credits, BrightChamps diamond rewards |
| Word-of-mouth | User recommends without in-product mechanic | Requires genuinely exceptional product |

> **K-factor:** (invitations sent per user) × (conversion rate of invitation to signup). K > 1 means each cohort generates more than one new user — viral growth without paid acquisition.

#### 3. Engagement/habit loop

User action produces in-product reward or value → reward creates motivation to return → return visit produces new user action.

**Examples:**
- **Duolingo streak:** Attend lesson → maintain streak → loss-aversion brings user back to protect streak → attend next lesson
- **BrightChamps feed:** Attend class → feed shows completion card → parent engages with feed → parent reinforces attendance → student attends class

**Key metric:** D1, D7, and D30 retention. A strong engagement loop produces high D30 retention. A weak loop drops off sharply after D7 as the initial novelty wears off.

**PM design decisions:**
- What is the smallest action that still produces a meaningful reward?
- How quickly can a user complete one loop cycle?
- Is the reward intrinsic (the action itself is satisfying) or extrinsic (diamonds, badges, streaks)?

#### 4. Retention/data loop

User invests in the product → investment creates switching costs → switching costs keep the user in the product → user continues investing.

**Examples:**
- **Notion:** Notes and pages accumulate → workspace becomes irreplaceable → user continues adding to it
- **Spotify:** Listening history, playlists, and Wrapped → emotional investment → switching means losing history
- **BrightChamps credit system:** Student builds a class history and achievement record → record is emotionally valuable → losing it is a reason to renew

**Key metric:** data depth per user (how much has this user invested in the product?) vs. churn rate. Users with deeper data investment churn at significantly lower rates.

**PM design decisions:**
- What user data/investment accumulates naturally with use?
- Is it exportable to competitors (if yes, the switching cost is lower)?
- Is it displayed in a way that reminds users of their investment (activity heatmaps, year-in-review, milestone counts)?

---

### Loop stacking: how multiple loops compound

Strong products have multiple loops running simultaneously, feeding into each other.

#### BrightChamps loop stack:

| Loop | Input | Action | Output |
|---|---|---|---|
| Engagement loop | Scheduled class | Student attends | Feed card, badge, diamond reward |
| Retention loop | Diamond balance | Student earns more diamonds | Switching cost (lose diamond progress) |
| Content loop | Class completion | Student records showcase | Showcase video on feed/externally |
| Acquisition loop | External showcase | Parent from new family views | Trial booking, demo conversion |

Each loop's output feeds the next: engagement → retention → content → acquisition → back to engagement (new student enrolled). When the stack is running, each enrolled student eventually generates fractions of new students.

---

### Loop closure: finding and fixing the breaks

A loop that doesn't close is just a feature. The most common reason loops fail to close: the friction at one step in the cycle is high enough that the output doesn't feed the next input.

#### Showcase loop closure analysis:

| Step | Output | Friction points |
|---|---|---|
| Student records showcase | Showcase video | Technical (complex UI), motivational (requires effort) |
| Showcase published to feed | Video on global feed | Moderation delay (teacher must approve before global visibility) |
| Parent shares externally | External share | Out of scope in V0 (no external sharing button) |
| External visitor sees showcase | BrightChamps.com traffic | Requires external link; no direct CTA from showcase to trial |
| Visitor books trial | Trial conversion | Standard conversion funnel |

⚠️ **Two biggest loop closure risks:**

1. **Teacher moderation delay** reduces the social momentum of a fresh showcase — students share videos within hours of completion; waiting days for moderation kills the sharing impulse.

2. **No external sharing button in V0** means the loop depends on parents manually copying and sharing links.

## W2 — The decisions this forces

### Decision 1: Identify the loop type that fits the product

Not every product has every loop type. The diagnostic:

| Product characteristic | Most natural loop type |
|---|---|
| **User-generated content** (videos, designs, documents) | Content/UGC acquisition loop |
| **Social connections** (teams, friends, networks) | Viral/referral loop |
| **Habit or recurring action** (daily tasks, learning, fitness) | Engagement loop |
| **Data accumulation** (notes, history, custom configurations) | Retention/data loop |
| **Marketplace** (supply and demand) | Liquidity loop (supply attracts demand, demand attracts supply) |

Most products have 2–3 applicable loop types. The PM's job is to choose which loop to invest in first — usually the one with the highest current closure rate, because it requires the least friction-reduction work to produce compounding returns.

---

### Decision 2: How to measure loop closure rate

> **Loop closure rate:** The percentage of time a user completes a full cycle within a growth loop (from initial action through to activation of the next cycle).

Loop closure rate is hard to measure directly. Use these proxies instead:

| Loop type | Proxy metric | What to look for |
|---|---|---|
| **Acquisition loop** | Organic signup rate | % of new signups citing "referred by friend," "saw shared content," or "found via search." Rising over time = loop closing. |
| **Engagement loop** | D7 and D30 retention | Users who completed "the loop action" (posted showcase, earned badge, hit streak) should retain significantly higher than those who didn't. |
| **Referral loop** | K-factor | Measure new signups each existing user generates within 30 days of joining. K > 0.3 = meaningful. K < 0.1 = barely exists. |
| **Retention loop** | Cohort churn by data depth | Users with more invested (more content, longer history, more customization) should churn lower than shallow-investment new users. |

---

### Decision 3: Building the loop vs. optimizing the funnel

Growth teams face a recurring resource allocation decision:

| Strategy | Impact | Cost | Sustainability |
|---|---|---|---|
| **Funnel optimization** (lower CAC per user acquired) | Immediate, measurable CAC improvement | Requires continuous investment | Gains erode the moment you stop |
| **Loop investment** (compound growth from existing users) | Slower to compound | One-time upfront work | Sustains without ongoing investment |

**The attribution problem:** A showcase video invested in month 1 may drive 10 trials in month 6. Loop investment is harder to attribute but creates compounding value.

**The PM decision rule:**
- **If CAC is rising and acquisition costs more each quarter:** Your product has no working loops. Funnel optimization = renting growth; loop investment = building a compounding asset.
- **Prioritize loops** when the loop closure rate has a clear path to improvement.
- **Prioritize the funnel** when no natural loop exists in the product.

---

### Decision 4: When a loop breaks — diagnosis framework

When a previously working loop stops closing, use this diagnosis framework:

| Symptom | Likely break location | Investigation checklist |
|---|---|---|
| Content volume rising but organic acquisition flat | Content → new user conversion broken | ✓ Is content discoverable externally? ✓ Is there a CTA to try the product? |
| Referral invitations sent but conversion dropping | Invitation → signup conversion broken | ✓ Is landing page still performing? ✓ Has onboarding changed? ✓ Is incentive still relevant? |
| D7 retention dropping but D1 high | Loop action isn't happening early enough | ✓ When do new users first complete the loop action? If day 5+, loop isn't starting before churn. |
| Existing users not generating content | Action step is too high friction | ✓ How many steps between product use and content creation? Each step reduces participation. |

## W3 — Questions to ask your team

### Quick Reference
| Question | Reveals | Action |
|----------|---------|--------|
| Growth loops structure | Loop completeness | Map all 4 components |
| Organic vs. paid ratio | Loop-driven growth | Track 3-month trend |
| Content external reach | Acquisition loop closure | Measure external exposure |
| K-factor & referral path | Loop design maturity | Quantify virality mechanism |
| Retained vs. churned behavior | Engagement loop action | Identify critical first 14 days |
| Dormancy & re-engagement | Loop resilience | Map re-entry mechanics |
| Content creation & sharing rates | Loop health at each step | Track per-user metrics |
| Growth without paid spend | True organic engine | Run 6-month scenario |

---

### 1. Growth loops structure

**"What are the growth loops currently running in our product — and for each one, can we describe the input, action, output, and closure rate?"**

> **Growth Loop:** A self-reinforcing cycle with four required components: input (user entry point), action (behavior completed), output (result), and closure rate (% of cycles that complete and re-trigger).

If the team can't describe a complete loop (all four components), there probably isn't a working loop — just a series of features that look like a loop.

*What this reveals:* Whether growth thinking is structured around compounding loops or around funnel stages with no self-reinforcing mechanism.

---

### 2. Organic vs. paid acquisition ratio

**"What percentage of our new user signups came through non-paid organic channels in the last 3 months — and is that percentage growing or shrinking?"**

| Scenario | What It Means | Risk Level |
|----------|---------------|-----------|
| Organic share growing | At least one acquisition loop is running | ✅ Low |
| Organic share static | Product is funnel-dependent | ⚠️ Medium |
| Organic share shrinking | Growth requires continuous paid spend | 🔴 High |

*What this reveals:* Whether loops are generating compounding acquisition or whether growth requires continuous acquisition spend.

---

### 3. Content acquisition loop closure

**"For our content or UGC features — what fraction of created content is ever seen by someone outside the platform, and does external exposure drive trial signups?"**

This measures the closure rate of the content acquisition loop. If content is created but never seen externally, the loop's acquisition output is zero.

*What this reveals:* Whether the content loop is closing on the acquisition side, or whether it's only an engagement loop (internal benefit only).

---

### 4. Referral loop: K-factor and virality mechanism

**"What is our K-factor — and what is the most common path by which an existing user creates a new user?"**

> **K-factor:** The average number of new users acquired by each active user. K > 1 indicates exponential growth; K < 1 indicates linear decay.

| Finding | Interpretation | Next Step |
|---------|-----------------|-----------|
| K-factor unknown | Referral loop hasn't been measured | Start measurement immediately |
| Virality is product-native | Built-in sharing mechanic exists | Invest in optimization |
| Virality is incidental | Occasional word-of-mouth only | Redesign for intentional sharing |

*What this reveals:* Whether the referral loop is designed or accidental, and whether investment in it is likely to compound.

---

### 5. Engagement loop: retained vs. churned user behavior

**"When we look at our highest-retained users vs. our churned users at the 90-day mark — what did the retained users do in their first 14 days that churned users didn't?"**

This question finds the engagement loop action. If retained users universally completed some action in the first two weeks that churned users skipped, that action is the loop's closing step — and the product should push new users toward it urgently.

*What this reveals:* The specific action that closes the engagement/retention loop, enabling targeted onboarding investment.

---

### 6. Loop re-entry and dormancy mechanics

**"What is the longest a user can go without engaging with a loop action — and does the product do anything to bring them back into the loop before they fully churn?"**

| Re-entry Mechanism | Example | Impact |
|-------------------|---------|--------|
| Dormancy email | Reminder that user missed new content | Loop continuation |
| In-app push | Notification of relevant activity | Loop continuation |
| Streak/milestone notification | "Your 30-day streak expires in 2 days" | Loop continuation |
| None | User just churns | Loop breaks permanently |

If the answer is "they just churn," there's no re-engagement mechanism in the loop.

*What this reveals:* Whether the engagement loop has a re-entry mechanism for users who miss a cycle, or whether one missed cycle breaks the loop permanently.

---

### 7. Content creation and sharing rates

**"What is the average number of showcase videos / user-generated content pieces created per active user per month — and what fraction are shared outside the product?"**

This measures both the content creation rate (action step) and the external sharing rate (closure step for the acquisition loop).

| Metric | Healthy Benchmark | Red Flag |
|--------|-------------------|----------|
| Content per active user/month | Rising or stable | Declining |
| % shared externally | >20% | <5% |

*What this reveals:* Whether the content creation and sharing steps are healthy, or whether the loop is breaking at creation (students don't make showcases) or sharing (showcases are made but not seen externally).

---

### 8. Paid acquisition removal scenario

**"If our paid acquisition stopped tomorrow, what would our growth look like in 6 months?"**

This thought experiment isolates how much of current growth is loop-driven vs. funnel-dependent. 

| 6-Month Outcome | Interpretation | Risk |
|-----------------|-----------------|------|
| Growth continues upward | Strong organic loops running | ✅ Low dependency |
| Growth flattens | Mixed loop + paid dependency | ⚠️ Medium dependency |
| Growth collapses | Entirely funnel-dependent | 🔴 High risk |

*What this reveals:* The true health of the product's organic growth engine and the risk profile of a marketing budget cut.

## W4 — Real product examples

### BrightChamps — student showcase as acquisition loop design

**What:** The Student Showcase feature is designed as a direct acquisition loop: student creates a coding project video → publishes to a feed → parents/teachers share externally → new families discover BrightChamps → some book trials → some enroll → those students create showcases.

**The explicit business goal:** The PRD states that the Showcase's primary business impact metric is "Visitors to Leads" — showcase videos function as organic proof of BrightChamps's value to families who have never heard of the product. This is a content acquisition loop where the students are doing the marketing.

**Loop closure risks:**

| Risk | Impact | Why it matters |
|------|--------|----------------|
| **Moderation delay** | Teacher approval latency between completion and visibility | Reduces sharing impulse — parents and students want to share immediately after class, not 2 days later |
| **No external sharing CTA in V0** | V0 scopes out direct social media sharing; requires manual link copying | High friction blocks loop closure — depends on parents manually copying links |
| **Discovery gated by authentication** | Showcases only visible to authenticated users; external visitors must create account | Reduces acquisition output — external visitors can't see showcases without signup |

**The PM's loop closure spec:** For the acquisition loop to close, at minimum one change is needed from V0: **a shareable link to showcases that external visitors can view without an account.** This single change converts the showcase from an engagement feature to an acquisition feature.

---

### TikTok — the content loop at scale

**What:** TikTok's growth is driven by a content/UGC acquisition loop: creator makes video → video surfaces in For You Page → viewer watches → algorithm optimizes video distribution → more viewers → some become creators → more videos.

**Loop mechanics:**

| Stage | Component | Driver |
|-------|-----------|--------|
| **Input** | Creator creates video | High-frequency; powered by view counts and comments |
| **Action** | Algorithm distributes to predicted-interested viewers | Algorithmic matching |
| **Output** | New users discover TikTok via shared videos or external links | Network effect |
| **Closure** | New users sign up; some become creators | Self-reinforcing cycle |

**The algorithmic accelerant:** TikTok's algorithm is the loop's efficiency multiplier. A video that reaches high closure rate (many viewers → creators) gets amplified by the algorithm. A video with low closure rate gets suppressed. The loop self-optimizes toward content that produces more creators.

**The PM lesson:** The TikTok loop closes because:
1. **Viewing without an account is possible** — no signup required to see a video
2. **The creative barrier is extremely low** — 15-second vertical video, no editing required
3. **The feedback loop provides instant motivation** — views, likes drive creator behavior

All three reduce loop closure friction.

---

### Dropbox — incentivized referral loop

**What:** Dropbox's referral program (2008–2010) offered both referrer and referee 500MB of free storage for each successful referral. This created a direct referral loop: user has Dropbox → invites friend for more storage → friend signs up → friend invites their network.

**The numbers:**
- **3,900% user growth** from 100,000 to 4 million users in 15 months
- **35% of new signups** came from the referral program at peak

**Why it worked:**

| Success factor | Why it mattered |
|---|---|
| **Storage scarcity was real** | 500MB was genuinely valuable in 2008; incentive was proportional to product's core value |
| **Invitation mechanism was in-product** | Dropbox prompted referrals during onboarding, when user enthusiasm was highest |
| **Symmetric incentive** | Both parties benefited; asymmetric programs (referrer only) have lower conversion because referral feels self-interested |

**The PM lesson:** Incentivized referral loops require the incentive to be:
- **(a) Genuinely valuable** — not a token discount
- **(b) Aligned with core value** — more storage for a storage product  
- **(c) Symmetric or near-symmetric** — both parties win

**⚠️ Incentive decay risk:** When incentive value declines (storage became cheap), the loop's closure rate dropped proportionally.

---

### LinkedIn — professional network retention loop

**What:** LinkedIn's retention loop is a data/network loop: user adds connections and career history → LinkedIn becomes increasingly valuable as a professional record → switching to a different network means starting over → user continues investing in LinkedIn profile → more connections → more valuable record.

**The accumulation mechanics:**

> **Switching cost accumulation:** Profile data, connections, and engagement history are LinkedIn-specific and not easily ported. After 5 years on LinkedIn, a user has hundreds of connections, dozens of recommendations, and a complete career record. Switching means losing all of this — or rebuilding it on a platform with fewer connections.

**What compounds the loop:**

| Mechanism | Effect |
|-----------|--------|
| Profile data (work history, endorsements, recommendations) | LinkedIn-specific; not portable |
| Connection network | LinkedIn accounts only; not portable contacts |
| Engagement history (posts, comments, reactions) | Accumulates and visible on profile |
| "People You May Know" system | Continuously surfaces new connections; adds network value each cycle |

**Why this is a loop and not just lock-in:** LinkedIn's retention isn't passive. The connection recommendations system continuously surfaces new connections — adding more value to the network with each cycle. Each connection added makes the network more valuable, which encourages more investment, which makes the network more valuable.

---

### Slack — enterprise B2B expansion loop

**What:** Slack's growth in enterprise accounts is powered by an expansion loop, not an acquisition loop. A single team adopts Slack → workflow improves → adjacent teams notice → adoption spreads via internal champion → company expands seats → finance team sees consolidated bill → IT standardizes → new teams get onboarded by existing Slack users.

**Why this is a B2B loop and not a funnel:**

| Traditional Enterprise Funnel | Slack's B2B Loop |
|---|---|
| Prospect → demo → evaluation → contract → onboarding → renewal | Team adoption → internal spread → formalization → expansion → standardization |
| Linear; requires central decision | Non-linear; spreads before legal/procurement involvement |
| Single buyer decision point | Multiple internal adoption events; each is input to next cycle |

**Loop mechanics:**

| Stage | Component |
|-------|-----------|
| **Input** | 1 team adopts Slack (often without central IT approval) |
| **Action** | Team uses Slack → workflow visibly improves → channels, integrations, shared history accumulate |
| **Output** | Cross-functional meetings route to Slack → adjacent teams start ad-hoc usage |
| **Closure** | Adjacent team usage formalizes → expansion seat request → new team starts cycle |

**The numbers:**
- **70% of paid seats** came from organic expansion within existing accounts (2019)
- The bottom-up adoption loop was the primary growth driver

**The enterprise PM lesson:**

> **B2B loop design principle:** Consumer loops close through external sharing (content, referral). Enterprise loops close through internal adoption spread. Design for the internal champion's ability to demonstrate value to adjacent teams — not for the user's ability to invite external friends.

**Key design insight for B2B:** The "user" who closes the loop isn't always the same as the "buyer" — the champion who spreads Slack and the IT manager who approves the enterprise contract are different people.

**Different B2B loop metrics:**
- Instead of K-factor, measure **expansion rate** (revenue from existing accounts growing)
- Measure **internal NPS** (likelihood of internal team recommending to another team)
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The loop design theater failure

Teams build features that look like loops but don't actually close. The most common example: a social sharing button that generates shares, but the shares don't convert to new users because the shared page requires login to view. The sharing action happens; the loop doesn't close.

| Signal | Cause | Prevention |
|--------|-------|-----------|
| Activity at action step (shares, invitations) with no measurable acquisition/engagement output | Loops designed for sharing behavior without designing for external recipient experience | Define loop closure metric before V0 ships |

**Example prevention metric:** "% of showcases that generate at least one external click-through to BrightChamps.com"

> **Loop closure:** When the output of one user's action becomes an input that drives acquisition or engagement for a new or existing user

⚠️ **Risk:** If closure metric is zero at launch, the loop is broken from day one. Ship with this metric defined.

---

### The loop interference failure

Multiple loops in the same product can interfere with each other. The most common interference pattern: the engagement loop's retention mechanism conflicts with the acquisition loop's virality requirement.

**Interference mechanism:**

| Loop | Mechanic | Impact on Sharing |
|------|---------|-------------------|
| **Acquisition** | Content shared externally brings in new users | Requires diverse, broadly appealing content |
| **Retention** | Content personalization increases engagement | Reduces content diversity users see |
| **Result** | User's network sees different content than user sees → reduced shareability of individual pieces | **Acquisition loop degraded** |

| Detection Signal | PM's Analytical Job |
|---|---|
| Acquisition loop closure rate declining despite rising content creation | Map loops explicitly; identify shared components; model impact on each loop before shipping changes to shared components (algorithm, ranking, visibility) |

---

### The false K-factor inflation

Products with incentivized referral programs can inflate K-factor metrics while degrading the quality of referred users. Attractive referral incentives (discount, credits, free storage) drive users to invite people with no genuine interest in the product — just to earn the reward.

| What Happens | Short Term | Long Term |
|---|---|---|
| K-factor increases, CAC appears lower | ✓ More signups | ✗ High churn in referred cohort |
| | | ✗ Incentive cost eats into margins |
| | | ✗ LTV negligible |

> **K-factor inflation:** Rising referral metrics paired with declining activation/retention of referred cohorts—indicating low-quality acquisitions

| Detection Pattern | Structural Risk |
|---|---|
| Rising K-factor + declining activation rate + declining 30-day retention for referred cohorts | Incentivized referral loop economics appear good short-term, fail long-term |

**PM prevention design:** Measure referred-cohort retention separately from overall retention. Design the referral incentive to require activation, not just signup — both parties receive the incentive only when the referred user reaches the activation event, not at account creation.

## S2 — How this connects to the bigger system

| Concept | Connection | Interaction |
|---|---|---|
| **Product-Led Growth (08.02)** | PLG is the GTM motion powered by growth loops | PLG acquisition, expansion, and referral are formalized loop mechanics; PLG without loops is just self-serve pricing |
| **User Onboarding Design (08.04)** | Onboarding delivers users to their first loop cycle | Goal: ensure every new user completes their first loop action |
| **Referral & Virality Mechanics (08.05)** | Virality mechanics implement referral loops | K-factor, viral coefficient, and incentive design engineer the loop's closure rate |
| **DAU/MAU & Engagement Ratios (06.04)** | DAU/MAU measures engagement loop strength | Strong loops produce daily return behavior; DAU/MAU is the proxy for whether the loop is running |
| **Cohort Analysis (06.03)** | Cohort retention reveals loop compounding | D7, D30, D90 curves show whether loops close after first cycle or only for first session |
| **Experimentation & A/B Testing (05.07)** | Loop improvements validated through experiments | ⚠️ Reducing friction at one step can break the loop at another — always A/B test changes |
| **North Star Metric (06.01)** | NSM should be the loop's output | If NSM = class completion rate, the primary loop should produce class completions |

### Loops and the revenue model

Growth loops affect P&L differently than funnels:

#### CAC over time
A working acquisition loop reduces CAC as it compounds. The first 1,000 users are acquired at full market CAC; as the loop generates organic acquisition, blended CAC decreases. **This is the financial case for loop investment.**

#### LTV of loop-generated users
Users acquired through organic loops (referral, content) typically have higher LTV than paid-channel users — because organic acquisition selects for users who already have social proof of the product's value.

#### The compound growth premium
At equivalent spend, a company with K=0.5 grows at **2× the rate** of a company with K=0 — because every user generates half a new user organically in addition to paid acquisition. **Over 18 months, this gap is enormous.**

## S3 — What senior PMs debate

### "Are growth loops actually new, or is this just 'viral mechanics' with a new name?"

**The skeptic's case:**
- Viral mechanics discussed since early social networks
- K-factor concept predates "growth loop" terminology by 15 years
- Renaming funnels as loops + adding "compounding" doesn't change underlying mechanics

**The legitimate distinction:**

| Aspect | Viral Mechanics | Growth Loops Framework |
|--------|-----------------|------------------------|
| **Primary focus** | Sharing and K-factor | Systematic mapping of inputs, actions, outputs, closure rates |
| **Loop types covered** | Sharing only | Engagement, retention, data loops—even with K < 1 |
| **Compounding view** | Limited | Multiple mechanisms simultaneously |
| **Completeness** | Narrower | More comprehensive |

**The practical resolution for PMs:**

Whether you call it viral mechanics or growth loops, ask: *"Is there any part of my product that generates more activity automatically, without continuous external input?"*

- If yes → measure it and invest in it
- The terminology matters less than the analysis

---

### "When should a company prioritize growth loops over growth channels?"

> **Growth channels:** Paid acquisition, content marketing, outbound sales — driven by continuous external input

> **Growth loops:** Product mechanics that generate activity automatically and compound over time

**The timing problem:** Most early-stage companies use channels because they need users faster than loops can compound. A 100-user product has a weaker loop than a 100,000-user product, even with identical mechanics.

**Strategic decision framework by scale:**

| User Count | Primary Strategy | Secondary Strategy | Why |
|-----------|-----------------|-------------------|-----|
| **< 10,000** | Focus on channels | Monitor loop mechanics | Loop can't compound at this scale |
| **10,000–100,000** | Channels + one strong loop | Begin optimization | Loop won't yet be primary driver |
| **> 100,000** | Strong acquisition loop | Channels as supplement | Each 1% loop improvement = hundreds of new users, no added spend |

**What changed in the last 2 years:**

AI personalization has dramatically accelerated engagement loop efficiency. Products that personalize content, recommendations, and notifications based on real-time behavior close loops at higher rates than static UX products.

*What this reveals:* The competitive gap between AI-personalized and non-personalized products has widened significantly.

---

### "How do you build a growth loop for a product that has no natural virality?"

B2B enterprise software, highly specialized tools, and regulated industry products often lack natural sharing or UGC mechanics—where referral and content loops don't obviously apply.

**Applicable loops for non-viral products:**

| Loop Type | How It Works | Example |
|-----------|-------------|---------|
| **Data/retention** | Accumulate user data and investment; switching cost increases over time | PM tool capturing all roadmap history becomes irreplaceable |
| **Professional word-of-mouth** | Referral through offline channels (conferences, LinkedIn, peer recommendations) | Enterprise software worth recommending; easy to share via case studies and ROI calculations |
| **Integration ecosystem** | Deep integration into buyer's workflow creates data and workflow dependency | Enterprise tools hard to abandon due to ecosystem lock-in |

**The BrightChamps application in B2B:**

**What:** If BrightChamps sold to schools instead of individual parents, the showcase loop would operate differently—but would still close.

**Why:** Schools share student achievement data with parents and communities. A showcase from a BrightChamps-enabled class becomes marketing for the school program, which markets BrightChamps to other administrators.

**Takeaway:** The loop closes through institutional word-of-mouth rather than direct parent sharing. The mechanics shift; the compounding principle remains.