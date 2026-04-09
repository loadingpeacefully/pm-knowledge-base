---
lesson: Classification Models
module: 04 — AI & ML Systems
tags: tech
difficulty: working
prereqs:
  - 04.01 — How LLMs Work: Context for how ML models learn patterns from data — classification models follow the same training principle applied to a decision output
  - 04.06 — AI Evals & Quality Scoring: Precision, recall, and thresholds are classification-specific eval concepts — you need evals to know if your classifier is working
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/student-lifecycle/auxo-prediction.md
  - technical-architecture/student-lifecycle/auxo-mapping.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-08
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The problem with handwritten rules

**The spam crisis of 2003**

Email was becoming unusable. By some estimates, **60–80% of all email traffic was spam**.

Early spam filters used rule-based systems:
- Lists of banned words
- Known sender addresses
- Suspicious phrase patterns

Examples: "Win a prize." "Click here." "Limited time offer."

**The limitations of human-written rules**

| Problem | What happened |
|---------|---------------|
| Users added rules manually | Each person maintained their own lists |
| Administrators maintained blocklists | Centralized but static |
| Spammers adapted faster than rules | Added spaces to words, misspelled on purpose ("fr€€" instead of "free") |
| **Result** | **Humans always one step behind** |

**The breakthrough: machine learning**

Engineers stopped asking:
> "What rules should we write?"

And started asking:
> "Can we show a machine thousands of examples of spam and let it figure out the rules itself?"

**The shift from rules to patterns**

> **Classification:** A machine learning model that learns patterns from examples instead of relying on human-written rules.

**Where classification lives today**

- Gmail moves an email to spam
- Instagram flags a comment for review
- A bank declines a transaction
- A streaming service recommends a show

In each case: **the rule-writer is gone. The pattern-learner is in.**

## F2. What it is — definition and analogy

> **Classification model:** A machine learning system that takes an input and assigns it to one of a fixed set of categories. The simplest version: two categories — yes or no, spam or not spam, will churn or won't churn.

### Before going further: two essential terms

| Term | Definition |
|------|------------|
| **Probability** | A number between 0 and 1 expressing how likely something is. 0 = impossible, 1 = certain, 0.94 = 94% confident. Classification models output probabilities, not hard yes/no decisions. |
| **Fixed categories** | The set of possible outputs is defined at training time, not inferred on the fly. A spam classifier can only output "spam" or "not spam" — it was built for those two categories and cannot invent new ones. |

> **Key concept:** A classification model doesn't just say "yes" or "no" — it produces a *probability*. "This email is 94% likely to be spam." The product team then decides where to draw the line — the *threshold* — that turns that probability into an action.

### The analogy: a doctor ordering a test

A doctor doesn't diagnose a patient by checking rules in a rulebook. Instead, they:
- Weigh the patient's age, symptoms, history, and risk factors together
- Arrive at a probabilistic judgment: "this looks like strep, not a cold"
- Base their assessment on patterns learned from thousands of prior patients

**The critical insight:** The doctor decides *when to act* on that judgment.

| Scenario | Probability | Threshold | Action |
|----------|-------------|-----------|--------|
| Chest pain patient | 40% cardiac event risk | High (act immediately) | Immediate attention |
| Low-risk patient | 40% mild infection risk | Low (wait for data) | Wait for test results |

Same probability — different threshold for action, because the cost of being wrong is different.

**Classification models work the same way:**
1. They estimate the probability that something belongs to a category
2. Your team decides the threshold
3. The threshold is a **product decision**, not a math problem

## F3. When you'll encounter this as a PM

| **Domain** | **Use Case** | **Classification Task** |
|---|---|---|
| **Content & Trust** | Spam filtering, hate speech detection, misinformation flagging, fake review detection | Categorize user-generated content at scale without manual review |
| **Risk & Fraud** | Payment fraud detection, account takeover detection, suspicious login flagging | Score transactions/activities as fraudulent or legitimate based on historical patterns |
| **Intent & Routing** | Customer support chatbots, search engines | Route tickets to correct team (billing/technical/account) or serve appropriate result type (navigational/informational/transactional) |
| **Prediction-Driven Decisions** | Churn prediction, course completion, sales conversion, lead quality | Output probability scores that feed into business processes (retention emails, resource allocation, escalation) |

### Quick Decision Framework

When your team asks "can we use ML for this?", apply this filter:

> **The Core Question:** Does this problem reduce to "put this thing into one of N categories?"
> 
> **If yes** → Classification is the right solution class to explore.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation (or existing PM context)
# ═══════════════════════════════════

## W1. How classification actually works

### Step 1: Features — what the model sees

The model doesn't see the raw input. It sees a set of numbers derived from that input, called *features*.

**For an email spam classifier, features might include:**
- Email length in words
- Number of links
- Presence of specific trigrams ("click here now")
- Whether the sender is in the address book
- Time sent (3am emails are more suspicious)

> **Features:** Numbers derived from raw input that the model actually processes. They encode assumptions about what predicts the outcome.

**Who decides?** The product team — usually working with data scientists — chooses which features to include. This is more PM work than it looks: every feature choice embeds a hypothesis about causation.

---

### Step 2: Training — learning the patterns

The model is trained on a *labeled dataset*: thousands or millions of examples where a human (or prior system) already provided the answer.

**The training process:**
1. Model receives examples: "This email is spam. This email is not spam."
2. Model finds statistical relationships between features and labels
3. Model learns patterns like: "5+ links AND sent at 3am AND unknown sender = very likely spam"

> **Key point:** These patterns emerge from data, not from rules you write.

---

### Step 3: Inference — scoring a new input

| Stage | Action | Output |
|---|---|---|
| **New input arrives** | Extract features from email | 5 links, sent 2:47am, unknown sender |
| **Run through model** | Apply learned patterns | Probability score |
| **Output** | Generate prediction | 0.91 (91% chance of spam) |

---

### Step 4: Threshold — turning a score into a decision

A probability is just a number. Something must turn it into an action: the **threshold**.

> **Threshold rule:**
> - **If probability ≥ threshold** → classify as spam (move to spam folder)
> - **If probability < threshold** → classify as not spam (deliver to inbox)

⚠️ **This is entirely a product decision.** Lower the threshold → catch more spam, but flag more legitimate email. Raise the threshold → let more spam through, but protect legitimate email. This is the precision-recall tradeoff (more in W2).

---

### The three types of classification

| Type | Output | Example |
|---|---|---|
| **Binary** | Yes/no; two classes | Spam/not spam, fraud/not fraud, churn/no churn |
| **Multi-class** | One of N classes | Support ticket routing (billing/technical/account/general), language detection |
| **Multi-label** | Multiple classes simultaneously | Content tagging (a post tagged: sports + humor + viral) |

## W2. The decisions this forces

### Decision 1: Precision vs. recall — which mistake is worse?

This is the most important PM decision in any classification feature. You cannot maximize both simultaneously. You have to choose.

> **Precision:** Of all the items the model *classified as positive*, what fraction were actually positive?
> 
> "How often is the model right when it says yes?"

> **Recall:** Of all the items that *actually were positive*, what fraction did the model catch?
> 
> "How many of the real positives did the model find?"

**The tradeoff, made concrete:**

| Scenario | The model says... | What actually happened | Type of error |
|---|---|---|---|
| High precision, miss some | "This is fraud" (correct) | IS fraud | True positive ✓ |
| High precision, miss some | "This is NOT fraud" | Actually IS fraud | False negative — you missed it |
| High recall, more false alarms | "This is fraud" | NOT fraud | False positive — you blocked a legitimate transaction |

**The PM question: what does each error cost?**

| Product context | Costly error | Right tradeoff |
|---|---|---|
| Medical diagnosis (cancer screening) | Missing a real case (false negative) | Optimize recall — catch everything, accept false alarms |
| Fraud detection (payments) | Blocking a real customer (false positive) | Optimize precision — only block when confident |
| Content moderation (hate speech) | Letting harmful content through (false negative) | Optimize recall — review edge cases manually |
| Spam filtering (consumer email) | Losing a legitimate email (false positive) | Optimize precision — users never see lost emails |
| Teacher quality prediction (lead conversion) | Missing a high-converting teacher (false negative) | Optimize recall — you want to surface all good teachers |

**Before your team builds the classifier:** Write down the answer to "Which error is more expensive for our users and our business?" That answer determines your threshold and your success metrics.

---

### Decision 2: What's your threshold?

Threshold is not a default value — it's a product decision with real consequences.

| Threshold | Effect | Use when |
|---|---|---|
| **Low (e.g., 0.3)** | Flag more items. Higher recall, lower precision. More false alarms. | The cost of missing a real case is catastrophic (fraud, safety, health) |
| **Medium (e.g., 0.5)** | Balanced. Usually the ML default. Rarely the right product choice. | Only correct if false positives and false negatives cost exactly the same |
| **High (e.g., 0.8)** | Flag fewer items. Higher precision, lower recall. Miss more real cases. | False positives are very costly (blocking paying customers, content moderation overreach) |

#### Company — BrightChamps

**What:** Teacher selection uses conversion rate as a score. When supply exceeds demand, only teachers ranked above a threshold are confirmed.

**Why:** The threshold is calibrated to minimize the cost of assigning a lower-converting teacher to a high-value student slot — a precision-over-recall choice.

**Takeaway:** The false positive (confirming a teacher who won't convert) is more costly than the false negative (not confirming a teacher who would have converted fine).

---

**How to actually set a threshold — a cost-matrix approach:**

Before your first production deploy, fill in this table with your team. The numbers don't have to be exact — order of magnitude is enough.

| Error type | What happens to the user | Business cost (estimate) |
|---|---|---|
| **False positive** | e.g., "Legitimate transaction blocked. User calls support." | e.g., $15 support cost + risk of churn |
| **False negative** | e.g., "Fraudulent transaction approved. Bank absorbs loss." | e.g., $120 average fraud loss |

In this example, a false negative costs 8× more than a false positive → set a lower threshold (optimize for recall). If the costs were reversed — false positive costs $200 in enterprise customer churn, false negative costs $15 in minor fraud — you'd set a high threshold.

**Who sets the threshold:**
- PM proposes the cost matrix and the target operating point
- Data science translates it to a threshold value
- Engineering implements the gate
- PM re-evaluates the cost matrix quarterly or after any significant false positive/negative incident

⚠️ **Critical:** Set the threshold against your actual cost function. Don't accept the 0.5 default unless you've verified it matches your business.

---

### Decision 3: Single model vs. cascaded classifiers

Most real products don't use a single classifier — they use a chain.

| Stage | Speed & Cost | Accuracy | Typical use |
|---|---|---|---|
| **Stage 1** | Fast, cheap | High recall, low precision. Catches 98% of problems but generates 40% false alarms. | Initial screening |
| **Stage 2** | Slower, more expensive | Higher precision. Reviews only what Stage 1 flagged. | Secondary review |
| **Stage 3** | Slowest, most expensive | Human judgment | Items Stage 2 still isn't confident about |

This pattern appears everywhere: Gmail's spam pipeline, Facebook's content moderation, fraud detection at Stripe.

**The PM decision:** Where to draw the escalation boundaries — what threshold sends something to Stage 2, and what threshold escalates to humans.

---

### Decision 4: What do you do with the probability score — not just the binary output?

Many products use the probability as an input to a business rule, not just a binary gate. This approach (called *score banding*) is used in fraud detection, content moderation, and lead scoring.

| Score range | Action |
|---|---|
| 0.9–1.0 | Automatic block or automatic approval — no review needed |
| 0.6–0.9 | Escalate for human review — high priority queue |
| 0.4–0.6 | Soft flag — add friction (CAPTCHA, extra verification) but don't block |
| 0–0.4 | Pass through — no action |

Score banding converts a continuous probability into a tiered set of responses — matching the urgency of the response to the confidence of the model.

#### Company — BrightChamps PQS Event Classification

**What:** The PQS system classifies each moment in a class transcript into one of 17 pedagogical event types (HOMEWORK_CHECK, EXPLANATION, GUIDED_PRACTICE, etc.). This is a multi-class classifier running on transcript segments.

**Why:** The PM decision was defining the 17 categories — what granularity is useful for measuring class quality?

**Takeaway:** Finer categories give more diagnostic signal. Coarser categories are more reliable. The 17-category choice was a product decision about the tradeoff between signal richness and classification accuracy.

---

### Decision 5: How do you handle class imbalance?

Most real-world classification problems are imbalanced — the positive class is rare.

| Product | Positive class rate | Why this matters |
|---|---|---|
| Payment fraud | 0.1–1% of transactions | A model that says "never fraud" is 99% accurate but useless |
| Churn prediction | 5–20% of users | Easy to be "accurate" while missing most churning users |
| Content moderation | <1% of posts are violating | 99.9% accuracy means nothing if you miss 90% of bad content |

⚠️ **The danger:** A naive model trained on imbalanced data learns to predict the majority class almost always — and appears highly accurate while being worthless for the actual task.

**PM implication:** Never evaluate a classifier with just "accuracy." Demand precision, recall, and F1 score. Accuracy is meaningless when the classes are imbalanced.

## W3. Questions to ask your engineer

**"What's our precision and recall — not just accuracy?"**

*What this reveals:* Whether the team is measuring the right thing. "99% accurate" on a 1% positive-class problem means the model might be predicting "not fraud" for everything. Precision and recall expose this.

---

**"What threshold are we using — and did someone set it, or is it the default?"**

*What this reveals:* Whether the threshold was deliberately chosen for your cost function or defaulted to 0.5. This is the most commonly overlooked PM decision in ML feature work.

---

**"What does a false positive look like for a real user, and what does a false negative look like?"**

*What this reveals:* Whether engineering has thought through the UX consequences of each error type. A false positive in fraud detection blocks a paying customer. A false negative in content moderation lets a bad actor through. Both need to be named and prioritized explicitly.

---

**"What features is the model using — and is any of them a proxy for something we shouldn't be using?"**

⚠️ **Risk:** Proxy features can create legal and ethical liability. Geography as a feature for loan approval can be a proxy for race. User engagement as a feature for content ranking can be a proxy for outrage.

*What this reveals:* Whether the model is making decisions based on inappropriate signals. Surfacing features is a legal and ethical risk management question.

---

**"How does the model perform on the groups that matter most — broken down by user segment, not just overall?"**

*What this reveals:* Whether the model has disparate performance across subgroups. A content moderation model with 95% overall recall might have 60% recall on non-English content. The "overall" metric hides the failure mode that matters.

---

**"How do we know when the model's performance has degraded in production?"**

*What this reveals:* Whether there's a monitoring plan for distribution shift — when real-world inputs start diverging from the training data. Models don't stay calibrated forever.

---

**"What happens when the model is wrong — what's the user experience of the error?"**

*What this reveals:* Whether there's a fallback or appeals process. A user who gets incorrectly flagged for fraud needs a path to resolution. A user whose legitimate content is removed needs an appeals mechanism.

## W4. Real product examples

### BrightChamps — Auxo Mapping
**Conversion rate ranking as real-time teacher assignment**

**What:** When multiple teachers are available for a demo class slot, the system ranks them by historical conversion rate and assigns the highest-ranked teacher to each student in under 1–2 seconds using Redis sorted sets.

**Why:** Conversion rate acts as a continuous classifier (probability the teacher converts this student to paid enrollment), optimizing match quality and revenue per slot.

**Key PM implications:**

| Dimension | Impact |
|-----------|--------|
| **Classification type** | Continuous (probability score) → binary action (assigned/not assigned) |
| **Threshold setting** | Implicit: supply-constrained = use all teachers; supply-surplus = only confirm top-ranked teachers |
| **Bias risk** | New teachers with no history are disadvantaged; product team must explicitly decide handling |

**Takeaway:** Continuous scores don't require binary thresholds — downstream supply constraints can calibrate the threshold automatically.

---

### BrightChamps — Auxo Prediction
**Joining rate forecast → resource allocation with safety buffer**

**What:** A 4-week weighted average predicts student joining rates. The system applies a 30% safety buffer (`predicted_leads × 1.3`), then uses a classification gate: excess teachers are ranked by conversion rate and only top performers confirmed.

**Why:** Regression prediction (count output) becomes a classification system through the buffer and ranking threshold — operationalizing a precision-recall tradeoff.

> **Safety buffer as PM choice:** The 30% buffer prioritizes recall (ensuring teacher availability) over precision (minimizing waste). Coverage failure (no teacher when student joins) was deemed costlier than waste (confirming unused teachers).

**Takeaway:** Buffers and thresholds encode your cost function; document which error type you're optimizing against.

---

### Gmail — Spam classification
**Precision-optimized with soft signals for edge cases**

**What:** Gmail's spam filter uses a high confidence threshold for automatic filtering. Lower-confidence emails get soft signals (banner: "This may be spam") instead of hard blocks.

**Why:** Cost asymmetry: losing a legitimate email is catastrophic; receiving spam is annoying but recoverable. Design prioritizes precision (minimize false positives).

| Configuration | Rationale |
|---------------|-----------|
| **High threshold for auto-move** | Reduces false positives (legitimate emails marked spam) |
| **Banner for low-confidence cases** | Alerts user without blocking; user retains control |
| **Result** | High precision, lower recall |

**Takeaway:** UX design (auto-move vs. banner vs. allow) makes your threshold visible and operationalizes your cost function.

---

### Stripe Radar — Fraud detection
**Score banding: threshold as customer configuration**

**What:** Every transaction gets a fraud probability score (0–100). Rather than a single threshold, Stripe uses score bands with different actions:

| Score Band | Action |
|------------|--------|
| **>90** | Automatic block |
| **75–90** | Requires 3D Secure authentication |
| **50–75** | Triggers merchant-configured review rules |
| **<50** | Passes through |

**Why:** Different merchants have different fraud tolerances and cost functions. A digital goods company (high chargeback risk) sets lower thresholds than a B2B SaaS company (low fraud base rate, high cost of blocking legitimate enterprise customers).

> **Configuration as product feature:** Thresholds are not platform defaults — customers adjust bands to their own business model and risk appetite.

**Takeaway:** Exposing threshold configuration to users is a product design decision that scales across heterogeneous use cases with different cost functions.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. What breaks and why

### Distribution shift — the model degrades silently

A spam classifier trained on 2022 email patterns encounters 2024 spam tactics it has never seen. The patterns have shifted, but the model hasn't updated. Precision drops. Users start seeing spam in their inbox.

**The problem:** The product team sees an uptick in spam complaints but can't explain it — model accuracy metrics look fine because they're measured against the old training distribution, not the new real-world one.

**PM prevention role:**
- Monitor production classification rates — not just model metrics
- If the rate of items being classified as "positive" changes significantly without a real-world cause, the model is degrading
- Set alerts on **production score distributions**, not just eval scores

---

### Proxy variables and discriminatory features

A loan approval classifier trained on historical loan data learns that certain zip codes predict default. The zip code is a proxy for race. The model is technically accurate on historical data. It is also discriminating illegally.

**The problem:** Data scientists didn't intend this outcome — it emerged from patterns in historical data that itself reflected historical discrimination.

⚠️ **Legal and ethical risk:** This failure mode affects user access to products, credit, insurance, employment, or housing.

**PM prevention role:**
- Before shipping any classifier affecting protected decisions, perform disparate impact analysis
- Run the model on data segmented by protected characteristics
- Flag features that predict well overall but perform differently (or with different error profiles) for protected groups

---

### Label leakage — the model learns from the future

A churn prediction model trained on data where the "churned" label was assigned 30 days after disengagement learns to predict churn from the absence of engagement in the last 30 days — including data leading up to the training cutoff.

**The problem:** In production, this "future" data isn't available. The model detects users who have already churned, not users about to churn. It fails immediately in production despite strong validation results.

**PM prevention role:**
- When validation results seem unusually good, ask: **"Is there any information in the training features that would not be available at prediction time in production?"**
- If the answer is yes, you have label leakage

---

### The "accurate but useless" failure

Your content moderation classifier achieves 97% accuracy. You ship it. Users start reporting that flagged content takes 48 hours to review.

| Metric | Value | Impact |
|--------|-------|--------|
| Model accuracy | 97% | ✓ Strong |
| False positive rate | 3% | ✗ Critical |
| Daily volume | 10M posts | — |
| Daily false positives | 300,000 items | ✗ Overwhelming |
| Review team capacity | 5,000/day | ✗ 60× understaffed |

**The problem:** The model works perfectly but breaks your operations entirely.

**PM prevention role:**
- Before shipping, calculate operational load: `FPR × volume = review queue size`
- Size your review team accordingly — or rethink your threshold

## S2. How this connects to the bigger system

> **Classification** is the decision layer on top of every other ML system in Module 04.

| System | Role of Classification | Connection |
|--------|------------------------|-----------|
| **Embeddings (04.04)** | Feature source | A k-nearest-neighbor classifier uses embeddings as features. Quality of embedding directly determines classification accuracy. Improving the embedding model improves the classifier without retraining it. |
| **RAG (04.03)** | Routing layer | Decides whether to retrieve ("does this query need grounded context?") and what to retrieve ("which document category is relevant?"). |
| **AI Evals (04.06)** | Evaluation framework | Precision, recall, F1, and threshold calibration are classification-specific concepts. These eval frameworks also apply to LLM output quality scoring—both ask "did the model make the right discrete decision?" |
| **Recommendation systems (04.08)** | Scoring mechanism | The line between ranking (recommendation) and classification (will this user click?) is blurry. Most recommendation systems use a classifier to score items, then rank by score. |

### Classification as Infrastructure

Once a team has a working classifier—even a simple one—it tends to multiply:

- First spam filter → spawns promotional email filter
- First fraud classifier → spawns bot detection classifier  
- First intent router → spawns sentiment classifier

**The scaling challenge:** Managing a portfolio of classifiers (each with its own threshold, training data, and monitoring) becomes a portfolio management problem once classification matures in a product.

## S3. What senior PMs debate

### Debate 1: Simple interpretable models vs. high-accuracy black boxes

| Dimension | Interpretable Model | High-Accuracy Black Box |
|-----------|-------------------|------------------------|
| **Example** | Logistic regression: debt-to-income (0.7×) + employment history (-0.3×) | Deep neural network |
| **Accuracy** | Baseline | +15% improvement |
| **Explainability** | Complete: you know exactly why each decision was made | None: "the model said so" |
| **Regulatory compliance** | ✓ EU AI Act, US Fair Lending Act require explainability for consumer decisions | ✗ Not compliant for regulated industries |

**The PM tension:**
- Product counsel: "We need interpretable models for any consumer-facing decision"
- Data science: "We'll lose 15 percentage points of fraud detection accuracy"

*What this reveals:* Neither side is wrong. This is a **legal risk tolerance decision** that escalates to leadership, not a data question. Senior PMs who haven't forced this conversation with legal and compliance teams have deferred a decision that will resurface during regulatory review.

---

### Debate 2: Model-in-the-loop vs. model-as-the-loop

> **Model-in-the-loop:** Humans review and approve model recommendations before execution
>
> **Model-as-the-loop:** Model makes final decisions autonomously; humans only audit after

**Economic pressure always favors automation** — cheaper, faster, scalable. But:

| Risk | Cost | Probability |
|------|------|-------------|
| Operational savings from removing human review | Known, immediate | High (90%+) |
| Reputational cost of systematic error at scale | Unknown but severe | Lower, but consequences are disproportionate |

**The unresolved question:** Where is the line?

- **Teams that faced a classification failure in production:** Draw the line *conservatively after* — they add human review stages that were removed to cut costs
- **Teams that avoided failure:** Draw the line *conservatively before* — they internalized that 98% accuracy still means 2% errors at their operating scale

*What this reveals:* Most teams learn this lesson through incident, not foresight. The difference between incident and foresight is whether you've explicitly modeled failure modes before they happen at scale.

---

### Debate 3: PM responsibility for historical bias in classifiers

⚠️ **This is no longer optional.** EU AI Act (2026) requires bias testing for high-risk AI systems (employment, credit, education, critical infrastructure). US disparate impact liability (ECOA, Fair Housing Act, Title VII) applies to ML-driven decisions regardless of intent.

**The question is not *whether* PM owns this — it's *how far* the responsibility extends.**

#### Position A: Disparate impact testing as launch gate

**What:** PM tests the classifier against protected characteristics before ship. Model is blocked if recall or precision differs by more than a defined tolerance across demographic groups.

**Why:** Compliance floor in regulated industries.

**Practical challenge:** You may not have (or may not be allowed to collect) demographic labels in training data, which makes testing difficult.

---

#### Position B: The objective function is the deeper problem

**What:** A credit risk classifier optimized for "will this person default" isn't biased in implementation — it's biased in what it optimizes. Historical default rates reflect historical access to capital, which reflects historical redlining.

**Why:** Testing for disparate impact treats symptoms, not cause.

**The PM question:** Should the objective function change from "who is likely to default" to "who is likely to repay given equal access to credit"?

**Why this matters:** This reframing requires a product and legal conversation most PM teams haven't had — but is the direction regulators are pushing.

---

⚠️ **The governance gap**

Most AI product teams have:
- ✓ Clear owner for model accuracy (data science)
- ✓ Clear owner for model deployment (engineering)
- ✗ **Clear owner for "is this model fair across populations"**

Until there is an explicit owner with authority to block a ship decision, fairness defaults to nobody. Senior PMs who haven't forced this conversation have left a governance gap that will eventually be filled by a regulator or an incident.