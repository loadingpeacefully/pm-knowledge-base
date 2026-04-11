---
lesson: Statistical Significance
module: 06 — metrics and analytics
tags: product
difficulty: working
prereqs:
  - 05.07 — Experimentation & A/B Testing: stats is how you know if your experiment result is real
  - 06.05 — Event Tracking & Instrumentation: events are the raw material statistical tests run on
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

In the early days of product management, decisions about whether a new feature worked were made by looking at the before-and-after numbers. Before: 40% completion rate. After: 55% completion rate. Feature worked. Ship it.

The problem: what if the improvement happened because of something else — a seasonal spike, a marketing campaign that launched the same week, users who happened to sign up that month being more engaged than usual? Without a way to distinguish "the feature caused this" from "this would have happened anyway," teams were fooling themselves constantly.

The consequences were real. Products added features that didn't actually improve outcomes. Features that did work got cut because the improvement wasn't noticed or was attributed to something else. Development cycles were wasted building things based on false signals, and resources were allocated to problems that weren't actually being solved.

Statistical significance is the tool that lets you separate a real effect from a coincidence. It doesn't guarantee you're right, but it sets a defensible bar: how confident do we need to be before we change course?

## F2 — What it is, and a way to think about it

> **Statistical significance:** A measure of how unlikely it is that the difference you observed between two groups happened by chance. A result is "statistically significant" when the probability that the observed difference occurred by random luck falls below a predetermined threshold (usually 5% or 1%).

> **p-value:** The probability of seeing the result you got — or a bigger one — if the feature actually had zero effect. A p-value of 0.05 means: "If the feature had no effect at all, we'd see a difference this big (or bigger) just from random noise about 5% of the time." Low p-value → the observed result is hard to explain as random luck.

> **Confidence interval:** The range of plausible values for the true effect size. "We're 95% confident the feature improved completion rates by between 3% and 11%" is more useful than just knowing the p-value.

> **Statistical significance threshold (α):** The pre-set probability below which we declare a result "real." Most teams use 5% (p < 0.05) or 1% (p < 0.01). Choosing 5% means you're willing to be wrong about 1 in 20 times you declare a result significant.

### A concrete way to think about it

**The coin flip analogy:**

Imagine you're flipping a coin and you suspect it's rigged. You flip it 10 times and get 7 heads. Is the coin rigged?

Maybe — but 7 heads in 10 flips isn't that unusual even with a fair coin. It could just be luck. If you flipped it 1,000 times and got 700 heads, you'd be much more confident the coin is rigged, because that result is extremely unlikely by chance alone.

**The core insight:**

Statistical significance asks: *"How surprised should I be by this result if there's actually nothing going on?"* The less surprised you should be, the less confident you should be that your result is real.

**Applied to products:**

| Scenario | Sample Size | Lift | Confidence |
|----------|-------------|------|------------|
| Small sample | 50 users | +8% conversion | Low — Could easily be luck. Don't ship. |
| Large sample | 50,000 users | +8% conversion | High — Very unlikely by chance. Stronger evidence. |

## F3 — When you'll encounter this as a PM

| Context | What happens | Why it matters |
|---|---|---|
| **A/B test results** | Data team sends experiment report showing "p = 0.04, 95% CI: +3%–11%" | You need to know if this is meaningful before recommending a ship decision |
| **Feature launch post-mortems** | Metric improved — but was it the feature or a coincidence? | Without significance, you can't attribute the improvement to your change |
| **Experiment duration debates** | Stakeholder wants to call the winner early ("it's obviously working") | Peeking too early produces false positives — significance requires full sample size |
| **"Not significant" results** | Experiment shows no significant effect | This does NOT mean the feature has no effect — it may mean you had too few users to detect one |
| **Multiple metrics dashboard** | 10 metrics tracked; 2 show improvements | With 10 metrics and 5% threshold, you'd expect 1 false positive by chance alone |

### BrightChamps — Student Feed Launch

**What:** The Student Feed PRD explicitly calls for A/B testing — feature flag enabled (variant) vs. disabled (control).

**Why:** Without statistical testing, any improvement in engagement after the feed launches could be due to seasonality, new user mix, or a concurrent campaign.

**Takeaway:** Statistical significance is what separates "the feed worked" from "engagement went up that month."
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The experiment structure

Every A/B test creates two conditions and compares an outcome:

| Component | What it is | Example |
|---|---|---|
| **Control group** | Users who experience the current product (no change) | Students without the Student Feed enabled |
| **Treatment group** | Users who experience the new version | Students with the Student Feed enabled |
| **Metric** | The outcome you're measuring | 7-day return visit rate |
| **Null hypothesis** | The assumption that there is no real difference | "The feed has no effect on return visits" |

> **Null hypothesis:** The statistical assumption that there is no real difference between conditions. A test rejects this hypothesis when the observed difference is unlikely to occur by random chance.

The statistical test asks: "If the null hypothesis were true (the feed does nothing), how likely is it that we'd see the difference we observed?" If that probability is very low (below your threshold), you reject the null hypothesis and conclude the effect is likely real.

### Sample size and statistical power

The two most misunderstood concepts in experiments:

> **Sample size:** How many users you need to detect a meaningful effect reliably. Too few users and you can't distinguish a real 5% improvement from random noise.

> **Statistical power:** The probability that your experiment will detect a real effect if one exists. A test with 80% power means: if the feature truly improves conversions by 5%, you'll successfully detect that 80% of the time (and miss it 20% of the time).

**Factors affecting sample size requirements:**

| Variable | Effect on required sample size |
|---|---|
| Smaller effect you want to detect | Larger sample needed |
| Higher confidence threshold (1% vs 5%) | Larger sample needed |
| Higher statistical power (90% vs 80%) | Larger sample needed |
| Higher baseline conversion rate variability | Larger sample needed |

**Practical implication:** A feature that improves conversion from 30% to 35% (a 17% relative improvement) requires fewer users to detect reliably than a feature that improves from 30% to 31% (a 3% relative improvement).

**Sample size requirements (80% power, 5% significance, two-tailed):**

| Baseline rate | Target rate | Relative improvement | Required users per variant |
|---|---|---|---|
| 30% | 35% | +17% | ~2,000 |
| 30% | 33% | +10% | ~5,000 |
| 30% | 31% | +3% | ~48,000 |
| 5% | 6% | +20% | ~10,000 |

These numbers illustrate why small improvements require much larger samples. For a product with 500 daily users, detecting a 3% improvement on a 30% baseline would take ~96 days (48,000 ÷ 500) — nearly 3 months. 

**Before committing to an experiment:** Use an online sample size calculator (e.g., Evan Miller's A/B testing calculator) to get exact numbers for your specific baseline metrics.

### Type I and Type II errors

⚠️ **Risk:** Both error types lead to costly decisions — shipping ineffective features or killing ones that work.

| Error type | What it means | When it happens | Consequence |
|---|---|---|---|
| **Type I (false positive)** | You declare a winner, but the effect was actually random | p-value below threshold by chance | Shipping a feature that doesn't actually work |
| **Type II (false negative)** | You fail to detect a real effect | Sample size too small | Killing a feature that actually works |

The 5% significance threshold controls Type I errors: you're saying "I'm willing to be wrong 5% of the time when I call a result significant." There's a tradeoff — stricter thresholds reduce Type I errors but increase Type II errors (more real effects get missed).

### Confidence intervals: the most practical output

> **Confidence interval (CI):** A range of values you're 95% confident contains the true effect size. More useful than a p-value because it shows *how big* the effect likely is, not just whether it's "real."

**Same p-value, two very different decisions — read the CI, not the stars:**

| | Wide CI (unreliable) | Narrow CI (actionable) |
|---|---|---|
| **p-value** | 0.03 "significant" | 0.03 "significant" |
| **95% CI** | +0.1% to +14% completion rate | +5% to +8% completion rate |
| **What it means** | Effect is somewhere between "nearly nothing" and "enormous" | Effect is between 5% and 8% — precise enough to plan around |
| **PM decision** | Don't make major bets — collect more users to narrow the range | Ship with confidence; the range is large enough to matter *and* tight enough to forecast |

**Why this matters:** A p-value alone tells you *whether* the effect is likely real. The CI tells you *how big* it probably is. Two experiments with identical p-values can point to wildly different ship decisions — only the CI width reveals which.

### Minimum Detectable Effect (MDE)

> **Minimum Detectable Effect (MDE):** The smallest improvement worth detecting and acting on. This determines your required sample size and experiment duration.

Before running an experiment, decide: **what's the smallest improvement that's worth knowing about?**

A 0.1% improvement in conversion might be real but irrelevant. A 5% improvement would change the roadmap. Setting the MDE before the experiment determines your required sample size and experiment duration.

⚠️ **Critical rule — avoid p-hacking:** Set the MDE before the experiment starts, not after you see the results. Choosing the MDE that makes your result look significant is manipulation and invalidates your statistical conclusion.

## W2 — The decisions this forces

### Decision 1: How long to run the experiment before calling results

Running an experiment too short produces false positives. Running it too long wastes users and development time on experiments that have clearly concluded.

#### Three common mistakes

| Mistake | What happens | Consequence |
|---|---|---|
| **Peeking and stopping early** | Checking results daily and stopping when it "looks significant" | False positive rate balloons; you'll call winners that aren't real |
| **Running past statistical conclusion** | Continuing after significance is achieved, hoping for bigger effect | Increases false positive rate over time; also delays shipping |
| **Fixed pre-calculated duration** | Running exactly as long as the power calculation says | ✅ Correct approach — discipline required to not peek |

#### The minimum runtime rule

> **Minimum runtime rule:** Run experiments for at least one full business cycle — never less. The cycle length depends on your product's natural usage rhythm.

| Product type | Minimum runtime | Why |
|---|---|---|
| Consumer daily-use (social, messaging, news) | 7 days | Captures full weekly behavior cycle — weekday/weekend users differ systematically |
| Consumer weekly-cadence (education, fitness) | 2–4 weeks | Users only engage 2–5 days per week; short runs miss the rhythm |
| B2B SaaS | 2 weeks minimum | Weekday vs weekend usage diverges even more; enterprise users skip weekends entirely |
| Subscription billing / renewal | Full billing cycle | You can't measure renewal until renewal actually happens |

**Why 7 days minimum:** User behavior varies by day of week. An experiment running Mon–Wed over-indexes on early-week behavior. If the treatment group happens to include more Monday users — and Monday users naturally convert better — you'll see a "treatment effect" that's actually day-of-week confounding. A full week forces each group to contain a representative mix.

**Action:** Calculate required sample size → translate to calendar time using your daily traffic → commit to that duration. If results "obviously win" on day 3 of a 14-day experiment, wait until day 14. The discipline is the point.

---

### Decision 2: Statistical significance vs practical significance

A result can be statistically significant but practically meaningless — and vice versa.

| Scenario | Statistical significance | Practical significance | Decision |
|---|---|---|---|
| +0.2% conversion at 1M users | Likely significant (large sample) | Too small to affect business | **Don't ship** — engineering cost > benefit |
| +12% conversion at 200 users | Probably not significant yet | Enormous if real | **Run longer** — collect more data |
| +5% conversion at 10,000 users | Likely significant | Meaningful improvement | **Ship with confidence** |

#### The key question

> **Practical significance test:** "If this result is real and the confidence interval is accurate, would the business impact justify the engineering and maintenance costs?"

Statistical significance gives you confidence the effect is real. Business judgment determines if the effect is worth acting on.

### Company — BrightChamps

**What:** Quiz completion improved from 40% to 89% — a 49 percentage point jump

**Why:** Demonstrates extreme practical significance

**Takeaway:** Because this was observed (not a controlled experiment), statistical significance testing doesn't apply — you can't separate the feature effect from other changes

---

### Decision 3: What "not significant" actually means

⚠️ **Most common PM misinterpretation:** "The experiment was not significant, so the feature doesn't work."

> **"Not significant" means:** We don't have enough statistical evidence to conclude the effect is real, given the sample size we had.

#### What "not significant" does NOT mean

- The feature had no effect
- The feature made things worse
- You should not ship the feature

#### What "not significant" could actually mean

| Possible explanation | What to do |
|---|---|
| Effect is real but small — you'd need 3× more users to detect it | Run longer / get more traffic / accept the ambiguity |
| Effect is real but your primary metric was wrong | Check secondary metrics; reconsider the success criterion |
| Effect is genuinely near-zero | Look at confidence interval lower bound — if entire CI is close to zero, that's evidence of no meaningful effect |
| Your metric has too much variance to detect the signal | Use a lower-variance metric for the same goal |

#### Before calling an experiment "not significant"

Check the **confidence interval**:
- **CI: +0.1% to +9%** = "We couldn't narrow it down" (not "no effect")
- **CI: -1% to +1%** = Actual evidence the effect is near zero

---

### Decision 4: Multiple comparisons problem

If you test 20 metrics with a 5% significance threshold and everything else is random noise, you'd expect roughly 1 metric to appear "significant" by chance.

> **Multiple comparisons problem:** Running tests across many metrics inflates false positive rates. "We found a significant improvement in this metric" is weak evidence if you're tracking 20 metrics simultaneously.

#### The problem grows when

- Running multiple variants in the same experiment (A/B/C/D tests)
- Tracking many outcome metrics and reporting the best-looking one
- Running many experiments simultaneously on overlapping user populations

#### Solution: Bonferroni correction

If testing 5 metrics, use a **1% significance threshold** (5% ÷ 5) for each. This keeps the family-wide error rate at 5%.

#### Practical PM approach

1. **Pre-register** your primary metric before the experiment starts
2. **Call significance** on the primary metric only
3. **Treat secondary metrics** as hypothesis-generating, not decision-making

---

### Decision 5: When to use statistical significance vs. other decision frameworks

Statistical testing is not always the right tool.

| Situation | Better approach | Why |
|---|---|---|
| Small user base (< 1,000 users) | Qualitative research + directional data | Too few users for reliable statistical tests; interviews more informative |
| One-sided decision (must ship for regulatory, business, or deadline reasons) | Risk assessment + rollout plan | Statistics won't change the decision; focus on risk mitigation |
| Evaluating existing features with no control group | Cohort analysis + time-series analysis | No randomization = can't use significance testing validly |
| Decisions with irreversible consequences | Higher threshold (99%) or multiple replications | ⚠️ Type I errors in irreversible decisions are catastrophically costly |

## W3 — Questions to ask your data team

| Question | Purpose | Red flag |
|----------|---------|----------|
| "What sample size do we need before the experiment result is trustworthy, and how long will it take to get there?" | Forces power calculation conversation upfront | 18+ months to significance = experiment not worth running at current traffic |
| "What MDE (minimum detectable effect) are we designing for?" | Ensures appropriate experiment sizing | No MDE specified = underpowered experiment risk |
| "Are we running one-tailed or two-tailed tests, and why?" | Clarifies test design assumptions | One-tailed tests used to achieve "significance" faster = inflated false positive rate |
| "Are there any novelty effects in this experiment we should control for?" | Validates experiment duration adequacy | Experiment too short to see past early-adopter exploration behavior |
| "Are we correcting for multiple comparisons? How many metrics are we tracking?" | Prevents false positives across metric set | Tracking 20 metrics, reporting the 2 that showed significance = random noise as insight |
| "Is user-level randomization appropriate for this experiment, or do we have network effects?" | Validates experiment design validity | Social features, messaging, or shared content without cluster randomization = invalid results |
| "What's the current p-value and confidence interval, and are we still on schedule to reach significance?" | Monitors instrumentation health mid-experiment | Broken tracking caught on day 28 instead of day 7 |
| "What are our primary and secondary metrics, and which one drives the ship decision?" | Locks in decision rule before results arrive | Metric switching post-results = HiPPO rationalization |

---

### Question 1: Sample size & duration
*What this reveals:* Whether you have enough traffic to detect the effect size you care about. If it would take 18 months to get statistical significance, you need a different approach.

### Question 2: Minimum detectable effect (MDE)
> **MDE:** The smallest improvement magnitude you'd actually care about detecting in an experiment.

*What this reveals:* Whether the experiment is sized appropriately for the effect you'd actually care about. "We designed for 5% improvement" means a 1% improvement won't be detected even if real.

### Question 3: One-tailed vs. two-tailed tests
| Test type | Power | Best for | Risk |
|-----------|-------|----------|------|
| One-tailed | Higher | When you only care about improvement direction | Misses degradation; inflates false positives if used to chase significance |
| Two-tailed | Lower | Catching both improvements AND degradation | Standard for product teams |

*What this reveals:* Test design awareness. Teams using one-tailed tests to get "significance" faster are inflating their false positive rate.

### Question 4: Novelty effects
> **Novelty effect:** User behavior changes in the first few days of encountering a new feature—users explore more, click more, notice more—then regresses to baseline.

*What this reveals:* Whether the experiment duration is long enough to see through novelty. Standard practice: run at least long enough for early adopters' novelty behavior to normalize.

### Question 5: Multiple comparisons correction
⚠️ **Multiple testing risk:** If the data team is tracking 20 metrics and reporting the 2 that "showed significance," you may be looking at random noise presented as insight.

*What this reveals:* Whether the significance reports are adjusted for the number of comparisons. Unadjusted multi-metric reports are misleading.

### Question 6: Randomization unit & network effects
> **Network effects:** When users in the treatment group can interact with users in the control group (social features, messaging, shared content), creating contamination between groups.

⚠️ **Validity risk:** User-level randomization with network effects breaks A/B test interpretation. Requires cluster randomization (e.g., by geography) instead.

*What this reveals:* Whether the experiment design is valid. Social features, referral programs, and any shared-state features require cluster randomization rather than user-level randomization.

### Question 7: Mid-experiment instrumentation check
*What this reveals:* Instrumentation health and trajectory, not decision information. You want to catch broken tracking at day 7, not day 28. Ask at the midpoint of planned duration—to verify traffic routing and event firing, not to peek at results and stop early.

### Question 8: Primary vs. secondary metrics
> **Primary metric:** The pre-registered metric that drives the ship/no-ship decision before results arrive.

*What this reveals:* Whether there's a clear pre-registered decision rule or whether the team will rationalize whatever result shows up. Pre-committing prevents HiPPO-driven metric switching after results are in ("the primary didn't work but look at this secondary metric that did!").

## W4 — Real product examples

### BrightChamps — Multiplayer Quiz: what strong numbers look like without an A/B test

**What:** Launched multiplayer quizzes for classroom group sessions.
- Math teacher adoption: **65%**
- Coding: 36.6%
- FinLit: 24.2%
- Robotics: 28.9%

**Why this matters:** 

> **Observational vs. Causal Claims:** Adoption metrics show *what happened*. Outcome claims require controlled experiments to show *why it happened*.

The 65% adoption rate tells you teachers used the feature — it doesn't tell you whether classes with multiplayer quizzes had better outcomes than classes without. No control group → no statistical significance claim.

**The statistical limitation:** Reporting "65% adoption" as success is appropriate. Claiming "multiplayer quizzes improve student outcomes" would require:
- Same teachers & course type
- Some classes with multiplayer, some without
- Learning outcome comparison
- Controlled analysis

**Takeaway:** Strong adoption numbers and causal outcome claims require different types of evidence. PMs often conflate the two.

---

### BrightChamps — Student Feed: A/B test framework as the right approach

**What:** The Student Feed PRD specifies:
- Feature flag gate to support A/B testing
- Control group (students without feed) vs. treatment group
- Tracked metrics: "Improvement Metric Value," "Current Adoption %," "Expected Impact"
- Targets set post-A/B baseline

**Why this is correct:** BrightChamps can now compare return visit rates, likes per session, and reply rates between groups. Statistical testing determines whether treatment improvements exceed random chance.

**Critical pre-work checklist:**

| Step | Purpose |
|------|---------|
| Set MDE | Define minimum improvement in return visits that justifies maintenance cost |
| Calculate sample size | Ensure statistical power to detect the MDE |
| Commit to duration | Lock experiment timeline before analyzing results |

**Takeaway:** Feature flags aren't just for rollout control — they're the infrastructure for valid causal experiments. The PRD's foresight in requiring A/B testing enables statistical significance analysis.

---

### Booking.com — culture of experimentation at scale

**What:** Booking.com runs thousands of simultaneous experiments with dedicated infrastructure handling:
- Randomization
- Significance testing
- Conflict detection (automated)

**How they scale rigor:**
- Each experiment analyzed independently
- Automated significance thresholds applied
- Primary metrics pre-registered by teams
- Multiple comparisons flagged and corrected automatically

**What PMs learn from this:** At scale, experimentation becomes the default shipping process, not a special procedure. Infrastructure makes statistical rigor automatic.

**Outcome:** Booking.com's conversion optimization credited with significant revenue gains — verifiable because of rigorous experimental design. Single-metric, pre-registered, powered experiments create defensible decisions.

---

### Netflix — going beyond binary significance

**What:** Netflix requires experiments to pass two filters, not just one.

| Filter | Requirement |
|--------|-------------|
| **Statistical significance** | p < threshold, corrected for multiple comparisons |
| **Practical significance** | Effect size ≥ MDE (pre-committed before experiment) |

**Why this matters:** 

⚠️ **Scale bias:** With 200M+ users, tiny effects become statistically significant easily. A 0.02% improvement in click-through rate is significant at scale but has minimal business impact.

The practical significance filter prevents shipping features that "work" statistically but don't move the business.

**Takeaway:** Statistical significance is necessary but not sufficient. Always pair with a practical significance requirement (minimum effect size you care about) to prevent engineering time spent on real-but-meaningless improvements.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### P-hacking and researcher degrees of freedom

> **P-hacking:** The practice of manipulating experiment analysis until the p-value crosses the significance threshold (p < 0.05), often through seemingly innocuous choices rather than deliberate dishonesty.

**Common researcher degrees of freedom:**
- Stopping the experiment early when p just crossed 0.05
- Removing "outlier" users whose behavior pushed the result the wrong way
- Switching from the primary metric to a secondary metric that looked better
- Splitting the data by subgroup until a significant subgroup appears
- Adding or removing covariates until significance is achieved

Each choice inflates the false positive rate dramatically. A team with 5 degrees of freedom effectively runs 5 implicit experiments, achieving a false positive rate far exceeding 5% even when every individual test uses p < 0.05.

**Structural fix:**
| Element | Requirement |
|---------|-------------|
| Hypothesis | Document before data collection |
| Primary metric | Locked in advance |
| Sample size | Calculated and committed |
| Test duration | Set upfront |
| Statistical threshold | Pre-specified |

**Result:** Pre-registration eliminates suspicion of p-hacking. Without it, any result report can be questioned, even unintentionally manipulated ones.

---

### Novelty effects and time-based confounders

> **Novelty effect:** Strong early feature performance driven by user exploration and curiosity that regresses toward baseline as users adjust (typically within 1–4 weeks).

**Example:** A new navigation pattern shows high engagement in week 1, returns to normal by week 4. A 1-week experiment falsely declares it a winner.

**Other time-based confounders:**

| Confounder | Impact | How it breaks results |
|-----------|--------|----------------------|
| **Seasonality** | High-engagement holiday periods | Treatment effects appear inflated |
| **Marketing overlap** | Campaign targeting treatment cohort's demographic | Treatment performance inflated |
| **Learning effects** | Users know the feature is "new" in A/B test | Post-launch behavior differs from test behavior |

**What breaks:** Teams running experiments too briefly ship features based on novelty effects that evaporate post-launch.

**Minimum runtime:** At least one full business cycle (typically 2–4 weeks).

---

### Interference effects destroying randomization validity

> **Randomization assumption:** Treatment and control groups are independent. This breaks when groups interact, influence, or depend on each other.

**When interference occurs:**

| Scenario | Mechanism | Result |
|----------|-----------|--------|
| **Social features** | Treatment user shares with control user | Control group influenced by treatment |
| **Network effects** | Feature value depends on adoption density | Neither group experiences full feature value |
| **Two-sided marketplaces** | Buyer feature affects seller behavior, which affects all buyers | Treatment effects biased (inflated or deflated) |

⚠️ **Failure modes:** Treatment effects appear smaller than reality (control group benefits from spillover) OR larger than reality (treatment group experiences artificially dense adoption).

**The fix:**

> **Cluster randomization:** Randomize at a unit containing the interaction (geographic market, friend group, class cohort) instead of individual user level. Preserves independence at the cost of larger required sample sizes.

## S2 — How this connects to the bigger system

| Concept | Connection | How they interact |
|---|---|---|
| **Experimentation & A/B Testing (05.07)** | Statistical significance is the evaluation layer of experiments | Experiments without significance testing are observations, not experiments |
| **Event Tracking (06.05)** | Events are the raw material significance tests run on | Instrumentation gaps create measurement error that inflates p-values |
| **Feature Flags (03.10)** | Flags are the randomization infrastructure | Clean flag assignment is required for valid significance testing |
| **Counter Metrics (06.09)** | Multiple metric testing requires significance correction | Guardrail metrics tested simultaneously require Bonferroni or similar corrections |
| **North Star Metric (06.01)** | Pre-committing to a primary metric is a requirement for valid significance claims | Teams that switch primary metrics after seeing results are p-hacking |

### The compounding dependency

⚠️ **Statistical significance is only valid when every upstream component is solid:**

1. **Clean event tracking** — no instrumentation drift
2. **Valid random assignment** — no selection bias in who gets which variant
3. **Pre-committed primary metric** — no post-hoc metric selection
4. **Adequate sample size** — power calculation done upfront
5. **Full planned duration** — no early stopping based on peeking

> **Key principle:** Any one of these failing invalidates the significance claim. The result may look statistically valid but be meaningless.

**Why senior PMs ask process questions, not just "what was the p-value?"**

When these dependencies break, p-values become theater—metrics that perform statistical gymnastics without revealing truth. The significance claim collapses upstream, not downstream.

## S3 — What senior PMs debate

### Frequentist vs Bayesian: does p-value testing even make sense for product decisions?

| Question | Frequentist Answer | Bayesian Answer | PM Implication |
|----------|-------------------|-----------------|----------------|
| **What does it answer?** | "If there were no real effect, how likely is this result?" | "Given this result, how likely is it that the feature actually works?" | Bayesian directly answers what PMs need |
| **Incorporates prior knowledge?** | No | Yes (what we know about similar features) | Bayesian learns across experiments |
| **Output format** | p-value | Probability variant is better | Bayesian is more actionable |
| **Interpretation risk** | Widely misunderstood | Still can be misinterpreted | Both require careful communication |

**Current PM practice:** Most A/B testing platforms default to frequentist, but Bayesian adoption is growing—especially for teams running many sequential experiments.

#### Platform shifts

> **VWO & Optimizely adoption:** Both platforms moved toward Bayesian by default because results are more interpretable for product decisions.

**The tradeoff:** Bayesian results depend on the prior you choose, which introduces subjectivity. Understanding this distinction helps you ask better questions of your data team.

---

### What's the right significance threshold — is 5% still reasonable?

> **The 5% standard (p < 0.05):** Established in early 20th-century agricultural science for one-time experiments with clear resource constraints. It was never designed for product teams running hundreds of experiments per year.

#### Arguments for stricter thresholds (1% or lower)

- More simultaneous experiments = more chances for false positives at 5%
- Irreversible decisions (platform changes, database migrations) warrant higher confidence
- One high-profile false positive can destroy experimentation culture with stakeholders

#### Arguments for looser thresholds (10%) or sequential testing

- Underpowered experiments (small user bases) forced to run indefinitely at 5%
- False negative cost (missing real improvements) often exceeds false positive cost
- Sequential testing methods (SPRT, always-valid inference) allow continuous monitoring with controlled error rates

#### What AI is changing

**2024–2025 AI-assisted platforms** can automatically select optimal thresholds based on:
- Experiment context
- Business stakes
- Historical false positive rates

The blanket 5% threshold is becoming obsolete for sophisticated teams.

---

### How should PMs respond to "not significant" results?

#### The politically difficult scenario

A team ships an underpowered experiment (too few users), runs for 5 days (too short), and reports "no significant effect." The PM is told to kill the feature.

#### ✅ The right PM response

1. **Check the confidence interval**, not just the significance claim
2. **Ask:** "What was the MDE we designed for, and how does it compare to our business-relevant minimum effect?"
3. **Ask:** "How long did we run, and what does the power calculation say we needed?"
4. **Interpret correctly:** If underpowered, the result is *uninformative*, not *negative*

#### ⚠️ The wrong PM response

Accepting "not significant" as "doesn't work" without investigating experiment capability. This pattern:
- Kills good features prematurely
- Allows underpowered experiments to veto roadmap items
- Relies on absence of evidence rather than evidence of absence

**What this reveals:** "Not significant" only means "we didn't detect an effect *given our experimental design*"—not "the feature has no effect."