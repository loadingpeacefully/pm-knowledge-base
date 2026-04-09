---
lesson: System Design Thinking
module: 05 — product-fundamentals
tags: tech, product
difficulty: working
prereqs:
  - 01.01 — What is an API: services communicate through APIs; understanding that contract makes architecture readable
  - 03.01 — Cloud Infrastructure Basics: services run on cloud infrastructure; you need the vocabulary
  - 03.06 — Queues & Message Brokers: async patterns appear in almost every architecture diagram
writer: senior-pm
qa_panel: Senior PM, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
  - technical-architecture/student-lifecycle/unified-demo-paid-experience-student.md
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

In the early days of most software products, everything lived in one place. One big codebase, one database, one deployment. You changed the checkout page and the entire app went down while it was deploying. You wanted to scale the video playback feature because it was getting slammed — too bad, you had to scale everything. A bug in the reporting tool crashed the student dashboard. Everything was tangled.

This worked fine for small teams building small things. But as products grew, the tangle became a crisis. Companies were losing features to bugs in unrelated parts of the codebase. Engineers were afraid to touch anything. A "quick fix" could take three weeks because nobody was sure what else it would break.

Something had to change about how software was structured — not just the code inside it, but the shape of the whole system.

## F2 — What it is, and a way to think about it

> **System Design:** The practice of deciding how different parts of a software product are structured, separated, and connected.

### The City Analogy

Instead of one giant building doing everything, a well-designed city has:

| Element | Purpose |
|---------|---------|
| Separate buildings | Each has a specific function (hospital, school, shop, house) |
| Roads | Connect buildings; enable movement and communication |
| Utility networks | Water, electricity, sewage systems operate independently |
| Independence | Hospital expansion doesn't require school expansion |
| Isolation | Water system failure doesn't affect electricity |

**Software architecture mirrors this structure:**

| City Element | Software Equivalent |
|--------------|-------------------|
| Buildings | Services |
| Roads | APIs |
| Utility pipes & networks | Databases and message queues |
| Independent function | Each service does one job |
| Defined connections | Services communicate through set interfaces |

### System Design Thinking: What You're Reading

As a PM, you're learning to read the architecture map and identify:

- What each component does
- What connects to what
- **Where single points of failure exist** ⚠️
- What breaks if one connection fails

### Your Role

**You will not design this map.** You will be in rooms where it's being drawn, and you need to:
- Read and understand it
- Ask the right questions
- Recognize implications for product decisions

## F3 — When you'll encounter this as a PM

| Situation | What happens | Why it matters |
|-----------|--------------|----------------|
| **Architecture reviews** | Engineers walk through proposed technical design on whiteboard or diagrams | You can't participate meaningfully, ask good questions, or flag product intent contradictions if you can't read the diagram |
| **Planning sessions** | Engineering gives estimates based on system architecture | "Three months" often means "touch five services and three databases"—you can't evaluate if it's reasonable without understanding the system |
| **Incident postmortems** | Postmortem explains what failed and why (always architectural) | Downstream dependency failures, service overload, missing indexes—reading fluently makes you a better partner to engineering |
| **Vendor or platform decisions** | Evaluate "build vs. use third-party service" options | Every new vendor becomes a box on the architecture diagram with its own failure modes and dependencies |

---

**Core principle:** You don't need to draw the map. But you need to read it.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

An architecture diagram shows you the shape of a system. Here's how to read one.

---

### Step 1: Find the services (the boxes)

Each box in an architecture diagram is a service — a distinct piece of software with a specific job.

**BrightChamps example:**
- Paathshala → class service
- Eklavya → student service
- Chowkidar → auth service
- Doordarshan → meetings
- Payments → billing
- (11 services total, each owning its domain)

**Your move:**
When you look at a diagram, first list the services and what each one does. If you can't explain each box in one sentence, you don't understand the system yet.

---

### Step 2: Find the communication paths (the lines)

| **Line Type** | **How It Works** | **Trade-offs** |
|---|---|---|
| **Solid line** | Synchronous: Service A calls B and waits for response | Creates dependencies. If B is slow/down, A breaks. Easy to debug. |
| **Dotted line or queue** | Asynchronous: Service A drops a message, B processes later | More resilient. Harder to debug. Better for non-critical flows. |

**BrightChamps example:**
When a student books a demo, Tryouts calls Paathshala (class service) *synchronously*. If Paathshala is down, demo booking breaks.

---

### Step 3: Find the data stores (the cylinders)

Most diagrams show databases or storage as cylinders.

**Key question:** What data lives where? Which services own which data?

**BrightChamps example:**

| **Database** | **Type** | **Implications** |
|---|---|---|
| MySQL (AWS RDS) | Relational | Specific query patterns, backup strategy, failure modes |
| MongoDB (self-hosted EC2) | Document/flexible | Different query patterns, backup strategy, failure modes |

Two systems = two different operational playbooks.

---

### Step 4: Find the external dependencies (the boxes at the edges)

These are third-party services your system talks to:
- Zoom (video calls)
- Zoho (CRM)
- Stripe (payments)
- AWS services (SQS, CloudFront)

⚠️ **Risk:** Each external dependency is a failure point your engineers don't control.

---

### Step 5: Find the traffic entry points

**Where do requests from users enter the system?**

Usually through an API gateway or load balancer — the front door. This layer controls:
- Load distribution
- Authentication
- Rate limiting
- Routing

**BrightChamps example:**
- Prashahak BE = central admin backend (talks to all core services)
- Each frontend (student, teacher, admin) routes through this layer

---

### Step 6: Ask "what happens when X fails?"

Trace a key user journey through the diagram.

**Example: "Student wants to join a class"**

```
Student app → Prashahak BE → Paathshala (class) → Doordarshan (meetings) → Zoom
```

**What this reveals:**
- 4 hops = 4 failure points
- Any one failing breaks the experience
- This chain drives conversations about reliability, fallbacks, and redundancy

## W2 — The decisions this forces

> **Quick reference — 5 architectural decisions PMs get asked about**
> - **Monolith vs microservices:** monolith first until ~20+ engineers or divergent scaling needs
> - **Sync vs async:** sync for user-facing flows; async (queues) for background jobs
> - **Managed vs self-hosted:** default managed; self-host only with clear cost/compliance reason
> - **Data ownership:** each service owns its own data; shared DB access = coupling problem
> - **Build vs buy:** buy infrastructure, build differentiators

---

### Decision 1: Microservices vs monolith

| Aspect | Monolith | Microservices |
|---|---|---|
| **Deployment** | One deploy for everything | Each service deploys independently |
| **Debugging** | Single log stream, easy to trace | Distributed traces across services |
| **Scaling** | All-or-nothing | Scale individual services by load |
| **Team size** | Works well under ~20 engineers | Worth it when teams need autonomy at scale |
| **Failure blast** | One bug can affect everything | Failures stay contained to one service |

**Recommendation:** For teams under ~20 engineers or products under 18 months old, push back on microservices pressure. The reasoning: microservices require operational infrastructure (service discovery, distributed tracing, container orchestration) that teams of that size usually don't have. The overhead costs more time than the autonomy saves. 

### Company — Shopify
**What:** Scaled past $50B GMV on a monolithic architecture  
**Why:** At smaller scale, coordination costs of microservices exceed the benefits of service independence  
**Takeaway:** Decomposition only pays for itself once you have distinct features with wildly different scaling needs — video processing vs. checkout vs. notifications

**PM outcome:** Microservices architectures make cross-service features take 2–3x longer because you're coordinating multiple teams. Budget for that when scoping.

---

### Decision 2: Synchronous vs asynchronous communication

> **Synchronous:** Call and wait. Simple, debuggable, immediate feedback. Creates tight coupling: if the receiving service is slow or down, the caller waits or fails too.

> **Asynchronous:** Drop a message in a queue (AWS SQS, Kafka, RabbitMQ), move on. The receiver processes when ready. More resilient, but harder to trace and you can't give the user an immediate response based on the result.

| Use case | Recommendation |
|---|---|
| User-facing flows needing real-time response (joining a class, completing a payment) | Synchronous |
| Background jobs (sending emails, generating reports, processing video) | Async queues |

⚠️ **Queue failure risk:** When a background job fails silently in a queue, users don't get an error message — they just never receive the email or the report. That's a product experience problem, not just an engineering one.

**PM outcome:** Ask how queue failures surface to users before you commit to async patterns for critical flows.

---

### Decision 3: Managed services vs self-hosted

> **Managed service:** Cloud provider handles backups, patching, scaling, and failover (AWS RDS, MongoDB Atlas). You pay more per unit but get zero operational overhead.

> **Self-hosted:** You run it yourself on a VM (EC2). Full control, full operational burden — backups, patching, capacity planning, incidents.

### Company — BrightChamps
**What:** Runs MongoDB self-hosted on EC2  
**Why:** Chose upfront cost control over operational simplicity  
**Takeaway:** Flagged as medium-severity technical debt; cost isn't in licensing, it's in engineer time spent on backups, upgrades, and incident response instead of product features

**Recommendation:** Default to managed services unless you have a specific regulatory reason (data residency, compliance) or the scale makes unit economics dramatically better. The "cost savings" of self-hosting usually disappear once you factor in on-call load.

⚠️ **Hidden velocity cost:** Self-hosted infrastructure creates invisible carrying costs on engineering velocity.

**PM outcome:** If your team is slow to ship features, ask how much on-call time is going to infrastructure that could be managed.

---

### Decision 4: Data ownership

> **Data ownership principle:** Each service should own its own data. Payments owns the billing table. Student service owns the student records. Services don't read each other's databases directly — they call each other's APIs.

⚠️ **Coupling risk:** When two services share a database directly, you have hidden coupling. Change the schema in one service and both break. You can't deploy independently. You can't change one without coordinating the other.

**Recommendation:** In architecture reviews, ask "which service owns this data?" If the answer is "both services read it directly," that's a design smell worth raising — not to block the work, but to understand the coordination cost before you commit to the timeline.

**PM outcome:** Shared data across services is the #1 reason "simple" changes take weeks. When estimates surprise you, ask whether the feature requires touching data that multiple services depend on.

---

### Decision 5: Build vs buy

Video processing, email delivery, payments, authentication — these are almost never worth building from scratch. They're solved problems with excellent off-the-shelf solutions (Stripe, SendGrid, Auth0, Cloudinary). The question is whether the capability is genuinely where your product is differentiated.

### Company — BrightChamps
**What:** Uses Zoom for video conferencing (buy) but built its own class scheduling, student lifecycle tracking, and teacher-student matching logic (build)  
**Why:** Differentiation is in how classes are structured, how teachers are paired, how progress is tracked — not in video infrastructure  
**Takeaway:** Default to buy for infrastructure; build only for genuine competitive advantages

| Decision type | Recommendation |
|---|---|
| Infrastructure and platform capabilities | Default to buy |
| Competitive differentiators | Build |
| Revisit boundary | Every 12–18 months |

⚠️ **Maintenance burden:** Every "build" decision adds a service you'll maintain for years. Every "buy" decision adds a vendor dependency you can't fully control. Both have costs.

**PM outcome:** The wrong decision in either direction is usually visible after 18 months. Plan a quarterly review of build-vs-buy choices as your scale and vendor markets change.

## W3 — Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| "Walk me through what happens when [key user action]." | Whether failure modes have been mapped across service boundaries |
| "What's our single biggest point of failure right now?" | Honest operational risk, not polished architecture |
| "If [Service X] went down at 8pm on a weekday, what would users experience?" | Whether the team has thought through failure modes for critical services |
| "Which parts of this system would we need to change to support [product direction]?" | Architectural surface area vs. feature complexity |
| "Is this an existing pattern in our codebase or are we doing this for the first time?" | Hidden operational costs of new patterns |
| "Which external dependencies does this flow touch, and what happens if they go down?" | Undisclosed third-party risk |
| "How will we know if this is working in production?" | Observability gaps in the feature plan |
| "Is there a part of this system you'd rebuild if you were starting fresh?" | Accumulated technical debt affecting prioritization |

---

### 1. "Walk me through what happens when [key user action]."

Pick your most critical user journey — a student joining a class, a user completing a payment — and ask an engineer to trace it through the system, service by service. Count the hops. Ask what happens at each boundary if the next service is slow or unavailable.

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Engineer names specific services, identifies where failures could cascade, mentions existing fallback |
| **Push back if** | Answer is "it just works" — failure modes haven't been thought through |

*What this reveals:* Whether the team understands how their system degrades under stress.

---

### 2. "What's our single biggest point of failure right now?"

Engineers always know the answer. They usually don't say it unless asked. This gets you the honest view of operational risk — not the polished architecture diagram, but the thing the on-call engineer actually fears.

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Specific service, database, or third-party dependency named with clear impact statement |
| **Push back if** | Answer is "we don't have any single points of failure" — every system has them at some scale |

*What this reveals:* Where the real operational fragility lives.

---

### 3. "If [Service X] went down at 8pm on a weekday, what would users experience?"

Tests whether the team has thought through failure modes for critical services.

| Scenario | Meaning |
|----------|---------|
| "Nothing, we have a fallback" | System designed for resilience |
| "The entire dashboard would stop loading" | Critical dependency with no protection |

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Specific user impact description + existing or planned fallback |
| **Push back if** | Answer is unclear — gap in incident preparation that will surface at the worst time |

⚠️ **Unclear answers here are operational risk.** This is what your incident response plan actually depends on.

*What this reveals:* Whether failure scenarios have been gamed out.

---

### 4. "Which parts of this system would we need to change to support [product direction]?"

Ask this before committing to a roadmap item. It maps the architectural surface area — whether the estimate is big because the feature is complex or because the system wasn't designed for it.

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Named services, database changes, and cross-team dependencies listed explicitly |
| **Act if** | Answer is "we'd need to refactor the core data model" — that's a 3–6 month conversation disguised as a feature estimate |

*What this reveals:* Whether you're building a feature or rewriting the foundation.

---

### 5. "Is this an existing pattern in our codebase or are we doing this for the first time?"

New patterns carry hidden costs: new infrastructure to operate, new failure modes to debug, potential security surface that hasn't been reviewed. Existing patterns have working runbooks and engineers who've debugged them before.

| Pattern Type | Cost Profile |
|--------------|--------------|
| **Existing** | Known failure modes, documented runbooks, team expertise |
| **New** | Infrastructure ops, incident debugging, security review, runbook creation |

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | "We've done this before for X, just replicate it" vs. "this is our first time with this approach" |
| **Escalate if** | It's new and estimate doesn't include operational setup + incident runbook creation |

*What this reveals:* Whether you're adding technical debt to your roadmap.

---

### 6. "Which external dependencies does this flow touch, and what happens if they go down?"

This is how you discover undisclosed third-party risk. Engineers often focus on the code path and don't volunteer that it calls a third-party API with no SLA guarantee.

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Named external services, SLA/reliability record, fallback or graceful degradation strategy |
| **Red flag** | External API in critical user path with no fallback and no monitoring alert |

⚠️ **Third-party APIs in critical paths without fallbacks are production risk.** You need to know about these before launch.

*What this reveals:* Which external vendors control your reliability.

---

### 7. "How will we know if this is working in production?"

The most underused question in product planning. Probes for observability — metrics, logs, and alerts for the new code path. A feature that works in staging and breaks silently in production because no one added monitoring is a PM problem as much as an engineering one.

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Specific dashboard, alert, or metric named that will confirm feature health |
| **Push back if** | Answer is "we'll check it manually" — that's not observability, that's hope |

*What this reveals:* Whether you'll know when the feature breaks in production.

---

### 8. "Is there a part of this system you'd rebuild if you were starting fresh?"

This is how you surface accumulated technical debt that isn't on the roadmap but is creating drag. Engineers will tell you if you ask — and knowing which parts of the system are fragile helps you make better prioritization calls when something breaks at 2am.

| Indicator | Assessment |
|-----------|------------|
| **Good answer** | Honest identification of one or two brittle areas with reasons they've accumulated |
| **Use for** | Quarterly planning conversations about architecture investment vs. feature work |

*What this reveals:* Which parts of the system are slowing you down.

## W4 — Real product examples

### BrightChamps — 11 microservices, one central orchestrator

**What:** 11 named microservices (Paathshala for classes, Doordarshan for meetings, Dronacharya for teachers, Prabandhan for CRM, Eklavya for students, Tryouts for demo bookings, Chowkidar for auth, Shotgun for quizzes, Payments, Hermes for communications, Prashahak BE for admin) with Prashahak BE acting as central orchestrator calling all others.

**Why:** Each service owns a domain, giving teams autonomy while centralizing orchestration in one place.

**Takeaway:** The design created an implicit central point of failure. Next step: introduce a dedicated API gateway layer to centralize auth, rate limiting, and routing—removing the double duty from Prashahak BE.

### BrightChamps — demo vs paid mode detection at the dashboard

**What:** The unified student dashboard determines feature visibility through a single database lookup indexed on `student_id`, with feature gates evaluated client-side after the flag is received.

**Why:** One fast DB read + client-side logic avoids a server round-trip for every gated feature check—a deliberate performance optimization.

**Takeaway:** Centralizing mode detection in one lookup made it both fast and debuggable. The tradeoff: one bug in mode detection breaks the experience for all demo students.

### Netflix — architecture shapes team topology

**What:** Migration from DVD-delivery monolith to streaming platform required moving to hundreds of microservices, each owned by a small team.

**Why:** Independent service deployments enabled ~100 deploys per day instead of one per week. Teams aligned to services, not cross-service features.

**Takeaway:** Architecture shapes shipping velocity. This wasn't purely technical—it was organizational.

### Shopify — the great monolith defense

**What:** In 2019, Shopify publicly defended their Rails monolith, keeping it well-modularized into "pods"—logical separations that gave team independence without distributed systems overhead.

**Why:** Microservices only help if you have operational maturity to run them. Shopify scaled past $50B GMV on their monolith.

**Takeaway:** Microservices are not inherently superior. They trade one set of problems for another.

### Airbnb — the cost of service decomposition

**What:** Hundreds of microservices led to hard-to-trace request chains, inconsistent data, and onboarding friction. Airbnb consolidated into a "service mesh" with shared observability tooling.

**Why:** Features cutting across multiple services shipped disproportionately slower.

**Takeaway:** Understanding where your system's seams are helps PMs identify where real delivery friction originates.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The distributed systems fallacy: "the network is reliable"

In a microservices system, every service-to-service call is a network call. Networks fail, timeout, and return partial results.

| Hop Count | Per-Hop Reliability | End-to-End Reliability |
|-----------|-------------------|----------------------|
| 6 hops | 99.9% | 99.4% |
| 10 hops | 99.9% | 99.0% |

At scale, multiply by request volume and you're handling failures constantly.

⚠️ **Risk:** PMs who set reliability targets without understanding the hop count are setting targets that physics won't allow.

---

### Chatty service patterns and latency compounding

When one user action triggers many small cross-service calls in series, latency compounds. Each hop adds **20–50ms of network overhead**.

**Example:** A dashboard load requiring 8 synchronous downstream calls will always be slow, regardless of how fast each individual service is.

| Problem | Root Cause | PM Action |
|---------|-----------|-----------|
| Performance complaint | Service design, not code optimization | Recognize architectural problem and escalate |
| Synchronous call chains | No batching, caching, or denormalization | Request architectural redesign |

---

### Tight coupling disguised as clean architecture

Services that technically appear separate on a diagram but share a database or call each other in tight synchronous chains are only superficially decoupled.

**What this reveals:** When Schema A changes, both Service 1 and Service 2 break — but they look independent on the diagram.

⚠️ **Release Risk:** A "simple" schema change turns into a multi-team coordinated deploy. If your team struggles to deploy independently without coordinating with three other teams, the architecture has coupling that the diagram isn't showing.

---

### Data consistency across service boundaries

When two services need to stay in sync — student record in Eklavya, billing record in Payments — the system has to handle the case where one update succeeds and the other fails.

> **Split-brain state:** Data that looks correct locally but is wrong globally.

Without careful design (eventual consistency, sagas, two-phase commits), you get situations where the student is marked paid in one system and not paid in another.

⚠️ **Detection Challenge:** This is the hardest class of bugs to diagnose because inconsistency isn't local to any single service.

---

### External dependency failure cascades

Every third-party service in your architecture is a silent assumption.

**Example — Zoom EdTech outages (2020–2021):** Any EdTech platform that hadn't built a fallback (reconnect flow, reschedule prompt, local recording) suddenly had tens of thousands of students in broken classes.

| What Diagrams Show | What Diagrams Hide |
|--------------------|-------------------|
| Clean external dependency boxes | You don't control their SLA |
| | You don't control their API changes |
| | You don't control their incident response timeline |

⚠️ **Hidden Risk:** Architecture diagrams mask the actual failure modes of external dependencies.

## S2 — How this connects to the bigger system

> **API Gateway:** The traffic control layer that sits in front of all services, centralizing cross-cutting concerns (auth, rate limiting, routing, SSL termination) that would otherwise be duplicated across every service.

**Why this matters:** System design thinking explains *why* the gateway exists. Understanding the architecture tells you the cost of not having one.

**BrightChamps case:** No dedicated API gateway layer yet; Prashahak BE doing double duty. *What this reveals:* Routing and auth logic may be scattered, creating maintenance overhead and scaling friction.

---

> **Queue:** An async processing layer—every async pattern in an architecture diagram depends on one.

**When to use:** Only once you understand which user journeys require immediate response and which can tolerate eventual processing. This is a system design decision first, a technical choice second.

---

> **Feature Flag:** An architectural decision as much as a deployment tool—not just a switch, but a system for evaluating eligibility at the right layer.

**BrightChamps case:** Feature gates evaluated client-side after receiving the mode flag. *What this reveals:* Performance and failure modes depend on where evaluation happens and what it queries. PM reasoning requires knowing the system design.

---

> **Container Orchestration (Kubernetes):** The infrastructure layer that makes microservices operationally feasible.

**Why this matters:** 

| Understanding | Enables |
|---|---|
| Service architecture alone | Architectural thinking |
| Service architecture + orchestration layer | Informed decisions on scaling limits, resource contention, cost of new services |

---

> **Distributed Tracing:** A monitoring system that shows the path of a single request across multiple services.

**Observability scaling rule:** 
- 1 monolith → 1 set of monitors
- 10 microservices → 10 service monitors + cross-service tracing

Architecture complexity multiplies observability requirements. System design thinking reveals where the gaps are.

---

> **Architectural Debt:** Structural decisions that constrain every feature built on top—the most expensive kind of technical debt.

**BrightChamps case:** Self-hosted MongoDB on EC2. Every team working with document data carries the operational burden of that infrastructure choice until migration. *What this reveals:* Early architectural decisions compound cost across the organization and limit future velocity.

## S3 — What senior PMs debate

### **"When should a PM push back on microservices proposals?"**

| Microservices Pitch | Counterargument | PM Leverage |
|---|---|---|
| Team autonomy + independent scalability | Most teams lack operational maturity for distributed systems | Push back on premature decomposition |

> **The Hightower Principle:** Teams should "earn" microservices by demonstrating they can run their monolith well first.

**The question to ask:** "What's the evidence our team can handle the operational burden of a new service before we add one?"

---

### **The platform vs product tension in architecture decisions**

The core tension:

- **Product goals (now):** Ship features this quarter
- **Platform goals (future):** Flexibility for unknown use cases

> **The reframed question:** Not "is this the right architecture?" but "is this the right *time* for this architectural investment?"

**Factors that determine timing:**
- How fast is the system growing?
- How much is the current design already slowing delivery?
- Does the team have skills to operate what they're proposing?

---

### **What AI is doing to system design**

⚠️ **LLM inference breaks traditional API assumptions**

| Traditional Services | LLM Inference |
|---|---|
| Predictable latency | 0.5–30 seconds (same model, same input) |
| Predictable costs | Cost varies dramatically by token length |
| Clear failure modes (500 errors) | Partial responses, hallucinations, timeouts |

**New architectural primitives required:**
- Streaming responses
- Async processing
- Confidence thresholds
- Graceful degradation

> **For senior PMs on AI products:** You need a system design mental model written after 2022, not inherited from 2015.

---

### **The underrated importance of data architecture**

Most system design conversations focus on services and APIs. **Data architecture** — where data lives, how it moves, who owns it — is the more consequential decision.

| Refactoring Scope | Effort |
|---|---|
| Refactor a service | Weeks |
| Migrate a data model (11 services depend on it) | Quarters |

**Real example:** BrightChamps architecture identifies cross-service communication patterns as undocumented, revealing potential N+1 or chatty service calls. This is a data architecture problem: services are chatty because they don't have access to structured data, forcing repeated cross-service queries.

> **The data architecture insight:** You can't fix chatty services without first understanding what data each service actually needs and whether it's structured to minimize cross-service queries.