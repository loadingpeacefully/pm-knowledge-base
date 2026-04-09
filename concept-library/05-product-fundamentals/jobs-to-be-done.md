---
lesson: Jobs to Be Done
module: 05 — Product Fundamentals
tags: product
difficulty: working
prereqs: []
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - product-prd/nano-skills.md
  - technical-architecture/student-lifecycle/unified-demo-paid-experience-student.md
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

## F1 — The world before this existed

For most of the history of product development, companies understood their customers through demographics and psychographics: age, income, interests, behavior clusters. The logic was: know who your customer is, and you'll know what to build for them.

This produced a lot of well-researched products that flopped. The 40-year-old suburban parent demographic will tell you, sincerely, that they want healthy food. Then they stop at McDonald's. The college student who says they need a better study tool downloads Spotify. The enterprise buyer who asks for more features cancels the contract because the product they already have is "too complex."

People don't do what they say. They do what makes progress on the problems they actually have in the moment they have them.

Clayton Christensen, the Harvard Business School professor who popularized Jobs to Be Done (JTBD), put it simply: "People don't buy products. They hire them to do a job." The milkshake study is the canonical illustration. McDonald's wanted to understand who their milkshake customers were. They built detailed buyer personas — age, income, preference profiles. The data was useless. Then a researcher asked a different question: what job were customers hiring the milkshake to do?

The answer was surprising: most milkshakes were purchased in the morning by solo commuters. The job wasn't "I want something sweet." The job was: "I have a 45-minute commute, I need something to keep my hands occupied and stave off hunger until lunch." The milkshake was competing not with other desserts — but with bananas, granola bars, and bagels. And it was winning because it was thick (lasted the commute), filled in one hand, and made the drive feel less monotonous.

Once you understand the job, you design differently. You don't make the milkshake cheaper. You make it thicker, easier to hold, and available faster for morning commuters.

This is the shift that JTBD enables: from "who is our customer?" to "what job is our customer trying to get done?" That question unlocks design decisions, pricing strategies, and competitive analysis that demographics never could.

---

## F2 — What it is — definition + analogy

> **Jobs to Be Done (JTBD):** A framework for understanding why customers buy products and services — specifically, what progress they're trying to make in their lives when they "hire" a product to help them.

**Key distinction:**
A job is **not** a feature request or a task. It's a unit of progress a person is trying to make in a given situation.

### The Contractor Analogy

When you hire a contractor to renovate your kitchen, you're not hiring them for a list of tasks:
- Tile floor
- Paint walls
- Install cabinets

**You're hiring them because:** You want your kitchen to feel like the kind of home you want to live in — and you don't have the skill or time to do it yourself.

**What this reveals:** If a competing contractor offers 20% faster work with the same quality, you might switch. But if they offer a feature you didn't ask for ("we'll also repaint your living room"), you might not care — because repainting the living room isn't the job. Your job is the kitchen feeling right.

**The product principle:** Products are contractors. Customers hire them for jobs. The question JTBD asks is: **what is the actual job?** Not the list of tasks — the underlying progress the customer is trying to make.

### Three Dimensions of Every Job

| Dimension | Definition | Example |
|-----------|-----------|---------|
| **Functional** | The practical outcome | "I need to prepare for my child's class so they don't miss the session." |
| **Emotional** | How the customer wants to feel | "I want to feel like a good parent who's on top of my child's education." |
| **Social** | How the customer wants to be perceived | "I want my child's teacher to see that we take learning seriously." |

**Competitive implication:** A product that only addresses the functional dimension competes on features. A product that addresses all three creates loyalty.

## F3 — When you'll encounter this as a PM

### Feature adoption stalls

**The scenario:** The feature works. Users say they want it. But they don't use it.

**JTBD diagnosis:** You built a feature for a job that either doesn't exist in the user's life, or that another "contractor" is already handling well enough. The feature was solving the wrong job.

---

### A competitor steals your customers

**The scenario:** A completely different product category is beating you for customers.

**Why it happens:** They're serving the same underlying job better — even if the products look nothing alike.

**Example:** Zoom didn't kill just other video tools. It killed some business travel because the job *"I need face-to-face connection with a partner across the country"* can be done by video.

---

### You're scoping a new feature

**Use JTBD to:** Ask "what job is this feature being hired to do?" before writing a PRD. This clarifies what the minimum viable version actually needs to include.

| Job Definition | Minimum Viable Feature | Why this matters |
|---|---|---|
| "Help me not miss my child's class" | Timely notification | Rich dashboard adds no value to the job |
| "Help me feel confident my child is learning" | Visible progress tracking | Notification alone won't do the job |

---

### You're setting your price

**The principle:** Customers pay based on the value of the job being done, not the cost of the feature set.

| Job Scope | Price Capacity |
|---|---|
| Functional job only | Lower ceiling |
| Functional + emotional + social job | Higher ceiling |

**JTBD reveals:** Where your pricing ceiling actually is.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level, or equivalent PM experience
# ═══════════════════════════════════

## W1 — How it actually works

### The anatomy of a job statement

A well-formed JTBD statement follows this structure:

> **When [situation], I want to [motivation/goal], so I can [expected outcome].**

| Component | Definition | Example |
|-----------|-----------|---------|
| **Situation** | The trigger context — a moment, not a demographic | "When I'm about to drop my child off at a trial class" |
| **Motivation** | The job itself — functional + emotional dimension | "I want to quickly check that my child's session is happening and that they have the link" |
| **Outcome** | The progress being made | "So I can feel confident they won't miss the class and my morning isn't disrupted" |

**Key insight:** The same person has different jobs in different situations. A parent at 7am before a trial class has a different job than a parent at 8pm reviewing progress. Building for the right situation matters as much as building for the right job.

---

### The four forces driving behavior change

When a customer switches solutions or adopts a new product, four forces are at work:

| Force | Direction | Definition | Example |
|-------|-----------|-----------|---------|
| **Push** | Toward change | Frustrations with how things are now | "I keep forgetting when my child's class is" |
| **Pull** | Toward change | Attractiveness of what you're offering | "The reminder card tells me exactly when to join and gives me the link in one tap" |
| **Anxiety** | Against change | Uncertainty about the switch | "What if the new dashboard is confusing?" |
| **Habit** | Against change | Comfort with existing behavior | "I just check my email for the link — it works fine" |

**The winning formula:**

> Push (current frustration) + Pull (new solution) > Anxiety (switching worry) + Habit (status quo comfort)

#### Case: BrightChamps' Unified Demo & Paid Dashboard

**What:** Combined class finder and one-tap join flow
**Why:** Directly targeted Push 1 (parents couldn't find links, attendance was low) and Pull 2 (frictionless join experience)
**Evidence:** "Parents surveyed (n~6,000)" quantified the push frustration
**Takeaway:** Great products don't just add features — they reduce switching anxiety while increasing perceived pull

---

### Competing solutions (substitutes, not just competitors)

> **Substitutes:** Solutions customers hire for the same job that aren't in your product category — your real competition

Your true competition often isn't another product in your category. Customers hire substitute solutions for the same job.

#### Case: Nano Skills (BrightChamps' self-paced micro-course marketplace)

**What:** A marketplace to spend accumulated diamonds on micro-courses
**Job:** "I want to keep learning something useful independently between live classes"
**Real competitors:** YouTube tutorials, Wikipedia rabbit holes, doing nothing
**Challenge:** Had to be more engaging than "search YouTube for it" — a higher bar than competing with other structured platforms
**Takeaway:** Understanding substitutes reveals both your true competition and why your value proposition actually matters

---

### Job mapping: the steps in a job

> **Job Map:** A breakdown of the sequential steps a customer goes through to get a job done — reveals friction and gaps in current solutions

#### Example: "Stay on top of my child's learning"

| Step | What Happens | BrightChamps Solution |
|------|--------------|----------------------|
| 1. **Define** | Understand what's being taught in this class | Left to parents/teacher |
| 2. **Locate** | Find the class link and time | ✓ Upcoming Class Reminder Card |
| 3. **Prepare** | Get my child ready to join | Left to parents |
| 4. **Execute** | Help them join the class on time | Left to parents |
| 5. **Monitor** | Know whether the class went well | ✓ Post-class feedback card |
| 6. **Evaluate** | Assess whether my child is making progress | ✓ Course Explorer with progress view |
| 7. **Reinforce** | Do something at home to support learning | Left to parents/teacher |

**Key insight:** Products that serve more steps in the job map create more value and more switching cost. BrightChamps addressed 3 out of 7 steps — identifying gaps where parents or teachers still had to do the work.

## W2 — The decisions this forces

### Quick Reference
| Decision | Core Question | Key Tension |
|----------|---------------|-------------|
| Job scope | How broadly to define the job? | Too narrow = features; too broad = strategy |
| Functional vs. emotional | Which job dimension matters most? | Commoditization vs. defensibility |
| Segmentation | Jobs or demographics? | Precision vs. measurability |
| Research necessity | When to run JTBD studies? | Depth vs. speed |

---

### Decision 1: Job scope — how broadly to define the job

**The question:**
> What unit should the JTBD statement describe?

**The pitfalls:**

| Scope | Example | Problem |
|-------|---------|---------|
| **Too narrow** | "When my child misses a class, I want to reschedule, so I can fit it into my week." | Describes a task, not a job — leads to building a rescheduling feature |
| **Too broad** | "I want to raise a successful child." | Life goal, not a job a product can be hired for |
| **Right scope** | "When I'm managing my child's edtech experience, I want to feel confident they're making progress, so I don't have to wonder whether we're getting value for money." | Specific enough to generate design decisions (progress visibility, parent reports); broad enough to encompass meaningful product surface |

> **Recommendation:** Define the job at the level where your product can plausibly be hired. **The test:** Can you write acceptance criteria for a feature that serves this job? If the job is too narrow, you'll build features. If it's too broad, you'll build a company strategy, not a product.

---

### Decision 2: Functional vs. emotional job emphasis

**The question:**
> Should the product primarily solve the functional job, or invest in the emotional and social dimensions?

**The dynamic:**

| Context | Functional Job Focus | Emotional Job Focus | Outcome |
|---------|---------------------|-------------------|---------|
| **Consumer** | "Show me the class schedule" | "I want to feel like an attentive parent" | Emotional job = defensibility; functional-only = commodity race to bottom |
| **Enterprise** | "Get the job done reliably" | "I want to feel I made the right procurement decision" | Emotional needs served by proof points, case studies, SLAs—not UI |

> **Recommendation:** Map all three job dimensions before scoping any feature. Then decide explicitly: **which dimension is most underserved in the current product?** That gap is where the highest-leverage product work usually lives.

---

### Decision 3: Job-level segmentation vs. demographic segmentation

**The question:**
> Should product decisions be driven by job-based segments or demographic segments?

**The comparison:**

| Segmentation Type | Example | Strength | Weakness |
|-------------------|---------|----------|----------|
| **Demographic** | "25–35 year old working parents" | Easy to define and communicate | Low predictive power for feature adoption |
| **Job-based** | "Parents managing live-class schedules who feel anxious about value-for-money" | High predictive power; spans age, income, geography | Harder to measure |

*What this reveals:* A "growth PM at an edtech startup in India" and a "head of product at a SaaS company in Singapore" may have identical JTBD for "understand what my team will build next quarter" — meaning the same roadmapping tool serves both despite different demographics.

> **Recommendation:** Use job-based segments for product design decisions and messaging. Use demographic segments for marketing channel selection and acquisition targeting. They serve different purposes and shouldn't be confused.

---

### Decision 4: When JTBD research is worth running

**The question:**
> Is running a JTBD interview study necessary for every product decision?

**When it's high-value:**
- You don't understand why users churn (the switching job is unclear)
- You're entering a new market (you don't know which job is underserved)
- You're designing a v1 product (you're making untested assumptions about the job)

**When it's low-value:**
- You have strong adoption and clear engagement signals
- You're building an incremental improvement to a well-understood job
- You're running a rapid experiment

> **Recommendation:** Do one JTBD study per major product initiative, not one per feature. 
>
> **Sample size guidance:** Practitioners like Bob Moesta and Chris Spiek observe that 6–10 well-conducted switch interviews tend to surface dominant jobs in a relatively homogeneous customer segment before returns diminish sharply. 
>
> **Important caveat:** This is not a universal law. Markets with high diversity (multiple distinct job segments, B2B with multiple decision-makers, global products with cultural variation) may require significantly more. Use 6 interviews as a starting point for a narrow, well-defined segment — not as a stopping rule.

## W3 — Questions to ask your engineer

### "What job does this feature serve — and what's the competing solution for that job today?"

*What this reveals:* Forces the team to articulate what customers currently do instead of using your feature. The substitute is your real competition. If engineering can't name the substitute, the feature doesn't have a clear job.

---

### "Which step in the user's job map does this feature address?"

*What this reveals:* Whether the feature is isolated (fills one step in the job) or connected (supports the full job sequence). Features that connect steps — like a reminder card that both shows the class time and gives the join link — are more valuable because they reduce effort across multiple job steps.

---

### "What's the anxiety or habit that will stop users from adopting this?"

*What this reveals:* Push forces alone don't drive adoption. If users feel the current solution is "good enough" or are anxious about change, the feature will see low adoption despite solving a real functional need. Naming the resistance forces design consideration of onboarding, trust signals, and migration paths.

---

### "If the feature perfectly solves the functional job, which emotional or social job dimensions are still unserved?"

*What this reveals:* Engineers default to solving functional requirements because those are what PRDs specify. This question opens a conversation about whether the design — beyond the specification — addresses the emotional and social dimensions that drive retention.

---

### "Are we serving the job the user hired us for today, or a different job we think they should have?"

*What this reveals:* Feature ideas often come from what PMs or engineers think users want, rather than what users are actually trying to get done. This question is a gut-check on whether the roadmap is user-pull or product-push.

## W4 — Real product examples

### BrightChamps Nano Skills — discovering a job that wasn't being served

**What:** A catalog of self-paced micro-courses (10–60 minutes) unlocked with diamonds earned through class attendance, quizzes, and referrals.

**Why:** Students had accumulated diamonds with nowhere meaningful to spend them. The real job wasn't "spend my diamonds"—it was "I want to keep learning interesting things between live classes, on my own terms, without waiting for a scheduled session." YouTube, Wikipedia, and doing nothing were the only available contractors.

**How JTBD shaped the solution:**

| Element | Job Served |
|---------|-----------|
| Nano Skills catalog | Contractor for self-paced learning |
| Diamond spending | Gives idle currency a job |
| Diamond earning loop | Creates pull to stay engaged (attend classes, complete quizzes) |
| Smart Modal upsell | Converts scarcity into revenue (want to enroll → buy diamonds) |

**Takeaway:** The job existed before the product. Nano Skills found it, then designed a mechanic that served multiple jobs simultaneously—learning, currency utility, and monetization.

**Year 1 outcomes:**
- 3,000+ cumulative enrollments
- 5% gross margin uplift from diamond top-up purchases

---

### BrightChamps Unified Demo & Paid Dashboard — designing for the parent's job, not the student's

**What:** A parent-facing dashboard combining class schedules, progress tracking, teacher feedback, achievement certificates, and peer project feeds.

**Why:** PM research surfaced a different job than the obvious one. Parents weren't primarily hiring for "show me the schedule." They were hiring to: *"When I'm managing my child's edtech experience, I want to feel confident they're making progress and not missing classes, so I don't have to wonder whether this is worth the money."*

This is an **emotional and social job**, not a functional one.

**Job dimensions and product responses:**

| Dimension | Job | Product Response |
|-----------|-----|------------------|
| **Functional** | Know class schedule | Upcoming Class Reminder Card with join link; Course Explorer with progress tracking |
| **Emotional** | Feel confident in child's progress | Post-class feedback with teacher comments; Class Completion Card with achievement framing |
| **Social** | Validate the investment socially | Certificate Achievement Cards (shareable); global feed showing peer projects |

**The KPI that reveals the job:**

> **Lead to Completion % (LTC):** Percentage of parents who booked a trial class and then enrolled as paid students.

- USA baseline: 36–39%
- Target: 60%

The 24–point gap isn't closed by better functional design (parents can already find the link in email). It's closed by serving the emotional job—helping parents *feel* their investment is worth it. That feeling drives enrollment.

---

### Intercom — messaging platform that changed its job definition

**What:** A messaging platform that evolved from support ticketing to a full engagement suite (messaging, bots, help center, CRM).

**Why:** Early positioning ("respond to support tickets faster") described a functional job that competitors could undercut on price. The actual, broader job customers were hiring for: *"When I'm trying to grow my SaaS product, I want to engage my users at the right moment with the right message, so they activate, convert, and stay."*

**What this reveals:** This job spans support, marketing, onboarding, and sales—commanding higher pricing and a larger addressable market than a single-function tool.

**The structural insight:**

| Approach | Outcome |
|----------|---------|
| Narrow job definition | Build features that solve one thing well |
| Correct job definition | Build platforms that serve the full job sequence |

**Takeaway:** Intercom moved upmarket by redefining what job they were hired for. They expanded from a support tool to an engagement platform because they understood the full job sequence.

---

### Amazon — the job that drives Prime

**What:** A $139/year membership providing fast shipping and low-friction checkout.

**Why:** Prime is often described as a loyalty program. The JTBD lens reveals the actual job: *"When I think of something I need, I want to be able to get it without friction—without thinking about shipping costs, without waiting, without driving to a store."*

**The job Prime solves:**

| Barrier | How Prime Removes It |
|---------|---------------------|
| Anxiety about shipping fees | Unlimited included shipping |
| Habit inertia (I usually go to Target) | Lower mental transaction cost than alternatives |
| Waiting time | Fast delivery as default |

**What this reveals:** Customers aren't paying $139 for unlimited shipping. They're paying for the feeling that Amazon is always the default answer. The fee works because the job—"frictionless procurement of physical goods"—is worth that much, and Amazon is the best contractor for it.

**Scale:** 200+ million Prime members pay because the job and the contractor are well-matched.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM, Ex-Engineer PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1 — What breaks and why

### Job mis-specification narrows the competitive moat

When a product defines its job too narrowly, it invites substitution from unexpected directions.

**The Problem:**
A "live tutoring platform" defined its job as "provide 1:1 tutoring sessions." But the underlying customer job was broader: "help my child keep learning."

**Substitutes that emerged:**
- Micro-course marketplace (Nano Skills) — lower cost, flexible
- Self-paced app (Duolingo) — self-directed learning
- Both served *part* of the same job at lower friction

| Competitor | Form Factor | Why it wins | What the tutoring platform missed |
|---|---|---|---|
| Live tutoring | 1:1 synchronous | Personalized instruction | Defined job by *form* not *progress* |
| Nano Skills | Micro-courses | Affordable, specific topics | Customer need = flexible learning |
| Duolingo | Self-paced app | Habit-building, gamified | Customer need = daily practice |

> **Key insight:** Customers switch to substitutes without warning when the platform defined the job by its delivery method rather than the progress customers seek.

---

### Emotional job underinvestment creates churnable products

Products that serve only the functional job compete in a **commodity market** — priced on features and cost alone.

**The trap:**
When a competitor launches at 20% lower price, a functionally-defined product has no defense.

**The solution:**
Invest deeply in emotional and social dimensions before the price war starts.

**Comparison:**

| Product Experience | Price Sensitivity | Why |
|---|---|---|
| "Class completed" notification | High — switches on price | Functional only; no emotional lock-in |
| Detailed post-class analysis with child's name + specific homework | Low — price is secondary | Emotional job: "I'm a caring, engaged parent" |

**PM prevention checklist:**
- Audit emotional and social job dimensions annually
- ⚠️ **Red flag:** Cannot name three things your product does for the emotional job = underinvestment

---

### Job-to-be-done statements without situation lead to wrong segmentation

> **The mistake:** "Parents want to track their child's progress" — applies equally to all parents, but their *situations* are different

**The reality:**

| Situation | Actual Job | Segmentation Error |
|---|---|---|
| Child is thriving | "Confirm things are going well so I don't have to worry" | Generic progress tracking ≠ reassurance |
| Child is struggling | "Understand specifically what's wrong and what I should do about it" | Generic progress tracking ≠ diagnostic insight |

⚠️ **Product consequence:** Building one product for both situations leads to a product that serves neither well.

## S2 — How this connects to the bigger system

### JTBD and user story writing (05.04)

> **Same idea at different scales:** User stories are job statements narrowed to feature scope.

**Format comparison:**
| Element | JTBD | User Story |
|---------|------|-----------|
| **Scope** | Customer need (broad) | Feature request (narrow) |
| **Example job** | Help parent monitor child's attendance | See upcoming class schedule |
| **"So that" clause** | The job itself | The underlying job purpose |

**Why this matters:** PMs who understand JTBD write better user stories because they grasp what the "so that" clause accomplishes, not just what the "I want" requests.

---

### JTBD and North Star Metrics (06.01)

> **Alignment is critical:** Your North Star metric should capture the primary job being done for the customer.

**When they diverge:**

| Misalignment | Result |
|--------------|--------|
| Job: "Help me feel confident my child is making progress" | North Star: "Sessions completed" |
| Outcome | Sessions ↑ / Parent confidence → flat / Churn on schedule |

**What this reveals:** Optimizing the metric while failing the underlying job is the fastest path to churn.

---

### JTBD and prioritization frameworks (05.03)

> **Complementary, not redundant:** RICE scoring and MoSCoW prioritization work best when you know which job each feature serves.

**The filtering sequence:**

1. **JTBD first:** "Are we solving real jobs customers are trying to get done?"
2. **Quantitative second:** RICE/MoSCoW answer "Which jobs should we prioritize?"

**Key insight:** A feature with high Reach and Impact scores that serves a job no customer actually needs is still the wrong feature.

## S3 — What senior PMs debate

| **Position A** | **Position B** |
|---|---|
| **JTBD is the correct unit of analysis for product strategy** | **JTBD is imprecise for execution** |
| Jobs are stable across technological substitution. "I want to communicate with someone far away" persists across messengers → letters → telegraph → phone → text → WhatsApp. | Jobs-based thinking doesn't translate to shipping. You cannot ship a job; you ship features. JTBD analysis must convert to a prioritized backlog, but the framework doesn't tell you whether to build feature A before feature B. |
| Building strategy on job understanding = building on stable ground. Companies defining strategy around technology, features, or category get disrupted; companies defining it around jobs see disruptions coming. | Practitioners disagree on fundamentals: what counts as a job? What's the right abstraction level? The "hire/fire" metaphor fails in some contexts (e.g., what job does a social feed do?). JTBD is a useful lens, not an operating system. |

---

### The genuine tension

Position A and Position B describe **different phases of the PM's job:**

- **Strategy & discovery** benefit enormously from JTBD—it prevents building solutions before understanding problems
- **Execution** requires different tools

**The skill:** knowing which tool to use at each phase.

- The PM using JTBD for everything will struggle with prioritization and delivery
- The PM ignoring JTBD will prioritize features without understanding which jobs they serve

---

### JTBD in AI-native products: the job is changing, not just the contractor

Traditional JTBD assumes the **job is stable** and **contractors (solutions) change**. AI products invert this:

> **The job itself evolves.** "I want to write clearly" was historically a job humans completed through practice, editing, feedback, and reading. AI writing tools don't just serve this job better—they fundamentally change:
> - Expected output quality
> - Speed of completion
> - What "getting the job done" means socially

**Why this matters:** When AI editors become ubiquitous, the social job ("I want to be seen as a skilled writer") transforms because unassisted writing signals new meaning.

**For AI product PMs:** Model not just the *current* JTBD, but how the job itself will evolve as the technology becomes commonplace.