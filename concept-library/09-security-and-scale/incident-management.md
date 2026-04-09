---
lesson: Incident Management
module: 09 — security and scale
tags: tech
difficulty: working
prereqs:
  - 03.09 — Monitoring & Alerting: incidents are detected through monitoring alerts; understanding what monitoring measures and what triggers an alert is prerequisite for understanding how incidents are discovered
  - 09.04 — Scalability Patterns: most P0/P1 incidents at scale are caused by scalability failures — database saturation, cascading service failures, missing circuit breakers; scalability patterns are the prevention layer for incidents
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/infrastructure/infra-monitoring.md
  - technical-architecture/infrastructure/server-schola-production-new.md
profiles:
  foundation:
    - Non-technical Business PM
    - Aspiring PM
    - Designer PM
    - MBA PM
  working:
    - Growth PM
    - Consumer Startup PM
    - B2B Enterprise PM
  strategic:
    - Ex-Engineer PM
    - Senior PM
    - Head of Product
status: ready
last_qa: 2026-04-09
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

Before structured incident management, when a production system broke, the response was improvised. The engineer who happened to notice the problem would try to fix it. Other engineers would join the investigation informally, sometimes working on the same part of the system simultaneously and interfering with each other's attempts. Customer support would start receiving tickets without knowing there was an outage in progress. Communication was ad hoc — engineering would post updates in a chat channel if they thought of it. No one was coordinating.

The result was that fixes took longer than necessary (multiple people duplicating work, no clear owner), users were left without information (or received inconsistent information from different support channels), and the organization never learned from the incident (no systematic record of what happened and why).

By the 2000s, the companies with the most complex infrastructure — Google, Amazon, financial institutions with trading systems — developed formalized incident response frameworks. These frameworks defined severity levels, specific roles during an incident (incident commander, communications lead), escalation paths, and post-incident review processes. The goal was to reduce mean time to resolution (MTTR), ensure consistent user communication, and create organizational learning from every incident.

The Site Reliability Engineering (SRE) model popularized by Google became the reference framework. It introduced the concept of the postmortem — a structured, blameless analysis of every significant incident — as the mechanism for turning failures into learning.

## F2 — What it is, and a way to think about it

> **Incident:** Any unplanned service disruption or performance degradation that materially affects users or business operations. Incidents range from a single feature being unavailable to full product outages.

### Severity Levels

Incidents are classified by impact to determine response urgency:

| Level | Impact | Response time | Example |
|---|---|---|---|
| **P0 (Critical)** | Full product outage; all users affected; payment or data integrity failure | Immediate — all hands | Production database goes down; payment processing fails for all customers |
| **P1 (High)** | Major feature unavailable; significant portion of users affected | Within 15 minutes | Class scheduling service down during peak hours; login failure for 20% of users |
| **P2 (Medium)** | Non-critical feature degraded; partial user impact | Within 1–2 hours | Slow report generation; intermittent API errors for a subset of users |
| **P3 (Low)** | Minor issue; minimal user impact | Next business day | Minor UI bug; slow-loading dashboard component |

### Key Metrics and Practices

> **MTTR (Mean Time To Resolution):** The average time from incident detection to full resolution. Lower MTTR is better and is a direct measure of incident response effectiveness.

> **Runbook:** A documented procedure for handling a specific type of incident. Example: "If Zoom class joins are failing, check: (1) Doordarshan service health, (2) Zoom API rate limits, (3) Redis token cache." Runbooks reduce MTTR by giving responders a decision tree rather than requiring them to diagnose from scratch.

> **Postmortem:** The structured review conducted after an incident is resolved. It answers: what happened, why it happened, how it was detected, how it was resolved, and what changes will prevent recurrence. Done right, every incident makes the product more reliable.

### The Incident Response Mindset

Think of an incident response as a hospital ER. When a patient arrives, there's a triage nurse (severity classification), an attending physician (incident commander), a clear protocol (runbook), and a handoff to specialists when needed. The ER doesn't improvise — the structure exists so that decisions can be made quickly under pressure. A product with no incident management structure is a hospital where staff shows up when a patient arrives and figures it out from scratch every time.

## F3 — When you'll encounter this as a PM

### During an active incident

| Your responsibility | What this means |
|---|---|
| **User communication** | Inform affected users what's happening, what's being done, and when to expect resolution |
| **Leadership updates** | Keep leadership informed of status and impact |
| **Engineering protection** | Shield the team from interruptions while they resolve the issue |

The PM typically owns the communication role during incident response.

---

### When reviewing monitoring setup

PMs ask: *"What happens between a customer noticing a problem and us being notified?"*

This question surfaces monitoring gaps. If the answer is "the customer tells support," you've found a critical weakness.

**Example:** BrightChamps's monitoring model:
1. New Relic and Kibana detect anomalies
2. Slack notification triggered
3. Jira ticket created
4. Developer assigned
5. Root cause analysis begins

*What this reveals:* Whether your detection systems catch problems before customers do.

---

### When discovering silent failures

⚠️ **Silent failures are a PM-spotted risk**

**Example:** BrightChamps's `schola-etl` (Google Sheet sync service) was **DOWN since November 22, 2023** — recorded as Critical severity — yet the organization didn't treat it as an ongoing incident.

A service remaining down for months without triggering incident response indicates:
- Failure of incident detection
- Failure of incident classification
- Possible product metric misalignment

PMs often notice these first when business metrics diverge from expected behavior.

---

### When a postmortem produces action items

Postmortem outcomes often require product and engineering changes:
- Add monitoring for previously untracked metrics
- Implement circuit breakers
- Redesign error handling paths

**PM's role:** Ensure these action items get prioritized and completed.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The incident lifecycle

#### Phase 1: Detection

An incident is detected through one of three channels:

| Channel | Mechanism | Speed | Reliability |
|---------|-----------|-------|-------------|
| **Automated alerting** | Monitoring systems (New Relic, Kibana, Datadog) detect metric thresholds exceeded | ⚡ Fastest | Highest |
| **Support escalation** | Customer support escalates recurring tickets | 🐢 Slow (mins-hours) | Medium |
| **Proactive observation** | Engineer notices anomaly in dashboard/logs | 📊 Inconsistent | Depends on active monitoring |

**BrightChamps approach:**
- Uses New Relic and Kibana with Slack integration for alert delivery
- Added OpenTelemetry (OTEL) to payment-structure service specifically to improve distributed tracing visibility — a direct response to observability gaps

#### Phase 2: Triage and classification

> **Severity Classification:** The first decision after detection that determines response scope—who gets paged, who joins the incident channel, SLAs, and executive notification requirements.

⚠️ **Classification errors are costly:**
- **Under-classifying P0 as P2** → delays response, extends user impact
- **Over-classifying P3 as P0** → wastes responder capacity on low-impact issues

#### Phase 3: Incident declaration and role assignment

**For P0/P1 incidents, assign explicit roles:**

| Role | Responsibility | Key Focus |
|------|-----------------|-----------|
| **Incident Commander** | Coordinate responders, prevent duplicate effort, ensure communication, make escalation decisions | Decision authority (NOT fixing the problem) |
| **On-call Engineer** | Investigate root cause, implement fix | Technical problem-solving |
| **Communications Lead** | User-facing status updates, internal stakeholder updates (often the PM) | Transparency and trust |
| **Executive Sponsor** | Available for escalation decisions (P0 incidents) | High-level decision authority |

#### Phase 4: Investigation and mitigation

> **Mitigation First Principle:** Stop or limit user impact *before* understanding root cause. Root cause analysis can wait; user experience cannot.

**Mitigation examples:**
- Roll back a deployment
- Disable a feature
- Redirect traffic
- Scale up a resource

**BrightChamps example — 30-second tracker API timeout:**
The monitoring KB documents: "Implement circuit breakers on all inter-service calls to prevent 30s hangs." A circuit breaker returns an error immediately for hung downstream services — users get an error instead of a 30-second hang. This is mitigation (acceptable user experience) while the underlying bug is investigated.

#### Phase 5: Resolution and verification

An incident is resolved when:
1. Service is restored to normal
2. **Verified by monitoring** — metrics (error rates, latency) returned to baseline

⚠️ **Common failure:** Engineers declare incidents resolved after applying a fix without confirming monitoring verification. This leads to premature closure and incident re-opening.

#### Phase 6: Postmortem

**Conducted within 24–72 hours** of resolution while incident is fresh.

**Standard structure:**

1. **Timeline** — What happened, when, who noticed
2. **Root cause analysis** — The underlying failure, not the symptom (use "5 Whys" technique)
3. **Impact** — User impact, duration, business impact
4. **What went well** — Parts of response that worked (fast detection, existing runbook)
5. **What went poorly** — Response gaps (slow detection, missing runbook, unclear communication)
6. **Action items** — Specific changes with owners and deadlines

**Blameless postmortem principle:**

> **Blameless Postmortem:** Focus on system and process failures, not individual mistakes. If root cause is "engineer deployed breaking change," action item is "improve deployment validation"—not "reprimand engineer."

⚠️ **Why this matters:** Blame-focused postmortems create incentives to hide incidents and discourage honest reporting.

---

### BrightChamps incident examples from the KB

#### Silent failure: schola-etl DOWN since November 22, 2023

**What:** Google Sheet sync service crashed due to MongoDB connection error and has been continuously down.

**Why:** Recorded as Critical severity technical debt rather than an active P1 incident.

**Takeaway:** A service providing data sync being unavailable for months represents a failure of incident management—it should have a resolution timeline and active response.

#### Failing payment trigger: port 7600 connection refused

**What:** Alepay payment instalment trigger on `schola-production-new` failing with port 7600 connection refused.

**Why:** Payment-related failures are P0/P1 (revenue impact), but recorded as Critical technical debt instead of active incident.

**Takeaway:** Without incident management process, revenue-impacting failures sit in backlog rather than receiving prioritized response.

#### Intermittent monitoring gap: Doordarshan API

**What:** Monitoring KB notes "Doordarshan → future live meetings API (intermittent failures tracked)" but failures remain unresolved.

**Why:** Tracking without response creates a monitoring gap—team knows failures occur but hasn't treated as incident requiring resolution.

**Takeaway:** Intermittent failures are early warning signals that typically precede sustained failures.

---

### The BrightChamps monitoring stack in practice

| Tool | Purpose | Coverage |
|---|---|---|
| **New Relic** | APM (Application Performance Monitoring) | Eklavya, Platform, Chowkidar, Paathshala, Dronacharya |
| **Kibana** | Log aggregation and search | Most services |
| **Lens** | Kubernetes cluster monitoring | EKS pods and nodes |
| **OpenTelemetry (OTEL)** | Distributed tracing | Payment-structure (added recently) |
| **Slack** | Alert delivery and team notification | All monitored services |
| **Jira** | Ticket tracking for fixes | All incidents |

**Critical gap identified:**

⚠️ **No SLO dashboards yet.** Roadmap item: "Introduce SLO dashboards in New Relic for each microservice (p95 latency, error rate)" — Month 1.

*What this reveals:* Team has monitoring infrastructure but no clear definition of "good"—making severity classification subjective and inconsistent.

## W2 — The decisions this forces

### Decision 1: What counts as an incident — and what should be escalated immediately

The most common PM failure in incident management is under-classification: treating a P1 as a P2 to avoid the overhead of full incident response, or assuming engineering will escalate when they find something serious.

| Severity | Criteria | Action |
|----------|----------|--------|
| **P0** | • Payment processing failure<br>• Data integrity failure<br>• Security incident (unauthorized access, auth bypass) | Immediate escalation |
| **P1** | • Authentication failure affecting >1% of users<br>• Core feature unavailable for >5% of active users | Immediate escalation |
| **P2+** | Below P1 thresholds | Standard incident process |

**The PM's role in classification:** In many organizations, the PM is notified of incidents by engineering rather than discovering them independently. But PMs are often positioned to notice incidents that engineering doesn't: a spike in support tickets, a drop in business metrics, user feedback in app reviews or social media. PMs who monitor business health metrics (DAU, session completion rates, payment success rates) can detect incidents that have user-visible impact but haven't triggered automated alerts.

> **Golden rule:** When in doubt about severity, classify higher. A P1 that turns out to be P2 costs 30 minutes of unnecessary overhead. A P2 that turns out to be P1 costs hours of delayed response and extended user impact.

---

### Decision 2: What PM communication looks like during an incident

During a P0 or P1 incident, users need information. Engineering is focused on resolution. The PM bridges this gap.

#### External communication (user-facing status page or email)

| Timeline | Message | Example |
|----------|---------|---------|
| **Within 15 min** | Initial acknowledgment | "We are aware of an issue affecting [feature]. Our team is investigating. We will provide updates every 30 minutes." |
| **At committed intervals** | Regular updates (even if no progress) | "We are still investigating. No resolution yet. Next update in 30 minutes." |
| **Upon resolution** | Resolution notification | "The issue affecting [feature] has been resolved as of [time]. [Optional: brief explanation of what happened]." |

**External communication rules:**
- ✅ Commit to specific update intervals and keep them
- ✅ Describe impact in user terms, not technical terms ("class scheduling is unavailable" not "Paathshala service is returning 503s")
- ❌ Don't speculate about root cause or resolution timeline until confident
- ❌ Never blame third-party vendors publicly (even if it's Zoom's fault)

#### Internal communication (leadership and stakeholders)

- **P0 incidents:** Immediate notification to CEO/CTO/relevant VP
- **Ongoing:** Current status, estimated resolution time, business impact estimate
- **Post-incident:** Summary of what happened and preventive actions

---

### Decision 3: How to treat postmortem action items on the roadmap

Postmortem action items are not optional. They're the return on investment for having survived an incident. But they compete with feature work for engineering capacity.

> **PM responsibility:** Postmortem action items should be entered into the sprint backlog with explicit priority. P0 postmortem actions — fixing the root cause of a critical incident — should be treated as P1 priority work. They do not go to the bottom of the backlog.

⚠️ **The failure mode to prevent:** The BrightChamps KB documents several items in the "Technical Debt" tables that appear to be unresolved postmortem action items or known incidents never treated as incidents: the schola-etl crash (November 2023), the port 7600 payment trigger failure, the missing circuit breakers, the Redis TTL error. When postmortem action items sit in technical debt tables for months, the organization is accumulating incident risk.

**The right question:** After every significant incident, the PM should be able to answer:
1. What is the specific change that would have prevented this incident?
2. Is that change scheduled?
3. Who owns it?

## W3 — Questions to ask your engineering team

### Quick Reference
| Question | Red Flag | Green Flag |
|----------|----------|-----------|
| P0/P1 declaration process | "We message the team and see who responds" | Named roles, specific channels, on-call rotation |
| Monitoring coverage | Services handling user data with no alerting | All critical services have automated alerting |
| Runbook currency | Outdated contacts, 6+ months old | Recent review dates, specific incident types covered |
| Postmortem follow-up | "We don't do formal postmortems" | Specific action items with owners and dates |
| MTTR trend | Flat or increasing over 6 months | Declining trend showing improvement |
| Degraded services | Production failures reclassified as tech debt | No unacknowledged failures in production |
| User communication | "We figure it out in the moment" | Designated owner with target communication time |

---

### 1. What's the process for declaring a P0 or P1 incident — who decides, and who gets paged?

*What this reveals:* Whether incident classification is systematic or ad hoc.

**Correct answer includes:**
- Specific roles (on-call engineer, engineering manager backup, PM notification status)
- Specific channels (dedicated Slack incident channel, PagerDuty or equivalent)

⚠️ **Red flag:** "We message the engineering team and see who responds" indicates no formal on-call rotation — incident response will be inconsistent.

---

### 2. Which of our services are currently monitored with automated alerting — and which are not?

*What this reveals:* Observability gaps in your system.

**Critical services requiring automated alerting:**
- User data handling
- Payments & transactions
- Authentication & access
- Class scheduling & features

⚠️ **Risk:** The BrightChamps monitoring KB covers Eklavya, Chowkidar, and Paathshala but leaves `schola-etl` uncovered—which crashed undetected. Services without alerting can fail silently for days.

---

### 3. Do we have runbooks for our most common incident types — and when were they last updated?

*What this reveals:* Whether incident response is prepared and current.

**Correct answer includes:**
- Specific runbooks (zoom class join failures, payment processing failures)
- Recent review dates (within last 3 months)
- Current contact information and endpoint details

⚠️ **Critical risk:** A runbook that says "contact [engineer who left 3 months ago]" creates false confidence and is worse than having no runbook. Runbooks outdated 6+ months are likely wrong.

---

### 4. What are the open items from the last 3 postmortems — what's been resolved and what's pending?

*What this reveals:* Whether the organization learns from incidents.

| Signal | Interpretation |
|--------|-----------------|
| "We don't do formal postmortems" | No organizational learning from incidents |
| "The postmortem happened but I'm not sure about action items" | Process exists but isn't tracked |
| Specific action items with owners and completion dates | Postmortem process is functioning |

---

### 5. What is the current MTTR for P1 incidents, and how has it trended over the last 6 months?

*What this reveals:* Incident response effectiveness and improvement trajectory.

**Healthy trend:** MTTR declining as team builds runbooks, adds monitoring, and addresses patterns.

⚠️ **Warning signs:**
- MTTR increasing or flat over 6 months
- Team doesn't measure MTTR (can't improve what isn't measured)

---

### 6. Are there any services currently in a degraded state that don't have an active resolution timeline?

*What this reveals:* Unacknowledged production incidents disguised as technical debt.

⚠️ **Critical risk:** The BrightChamps KB documents `schola-etl` as DOWN for months. Production failures reclassified as "technical debt" without an active owner and timeline are masquerading P1s.

**Watch especially for:**
- Payment-related failures
- Authentication-related failures
- Data-integrity failures

---

### 7. What's the process for communicating to users during a P0 or P1 — who writes the status updates, and what's the target time from detection to first user communication?

*What this reveals:* Whether user communication has a designated owner.

| Scenario | Implication |
|----------|------------|
| "We figure it out in the moment" | No process; communication is delayed and inconsistent |
| "Support sends something eventually" | User communication is deprioritized |
| Designated PM/comms owner with target time | Clear ownership and accountability |

**Recommendation:** The PM should own this process.

## W4 — Real product examples

### BrightChamps — Two silent production failures

**What:**
- `schola-etl` DOWN since November 22, 2023 — Google Sheet sync broken for months (known root cause: MongoDB connection error, no active resolution)
- Alepay payment instalment trigger FAILING (unknown date) — port 7600 service not running, scheduled payment triggers not executing

**Why this matters:**
Incident management culture doesn't exist — P0/P1 failures accumulate as line items in technical debt tables instead of being treated as active production incidents with owners and resolution timelines.

**Takeaway:**
Silent failures compound. Without incident ownership and clear resolution timelines, critical production issues become normalized as "technical debt."

---

### AWS us-east-1 outage — Cascade and communication failure (2017)

**What:**
- February 2017: S3 outage in us-east-1 took down ~4 hours of internet-wide services (Slack, Quora, Medium, thousands more)
- Root cause: typo during maintenance removed more S3 capacity than intended, triggering cascading failures
- Status page blindness: AWS's internal health dashboard was hosted on S3 in us-east-1 — it went down during the outage

**Why this matters:**
Infrastructure dependencies on the same systems being monitored create status-page blindness. User communication during incidents requires out-of-band channels.

**Takeaway:**
Monitor your monitors. Don't host your incident communication channel on the infrastructure you're trying to report on.

---

### GitLab database deletion — Near-catastrophic data loss (2017)

**What:**
- January 2017: DBA accidentally deleted 300GB of production data during incident response
- All five backup processes had failed or were incomplete — backups had never been tested for restores
- Result: ~6 hours of user data lost, 18-hour downtime

**Why this matters:**
GitLab published a full, transparent postmortem detailing every backup failure. This blameless transparency became industry practice.

> **Blameless postmortem principle:** Disclosing what went wrong openly — internally and externally — builds user trust. Hiding incident details destroys it in a way transparency doesn't.

**Takeaway:**
Test your backups. Transparency in failure rebuilds trust faster than silence.

---

### Stripe — SLO model as product feature

**What:**
- Stripe publishes uptime and latency targets as public service SLOs
- Status page updates in near-real-time with affected components, latency measurements, and resolution progress
- Enterprise customers build incident response workflows that trigger on Stripe's status page updates

**Why this matters:**
For developer-facing products, a public status page with genuine transparency (not just green lights) is a competitive differentiator. Customers can react to Stripe incidents without waiting for support confirmation.

> **Product decision:** "Would our customers benefit from a public status page?" is not just an infrastructure question — it's a product strategy question.

**Takeaway:**
Transparency in real-time status is a feature, not just an operational courtesy.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### Communication failure outlasts technical failure

> **The core issue:** Technical incidents are temporary. Reputation damage from poor communication is permanent.

A product can experience a 30-minute outage two ways:

| Scenario | Communication | User Trust Outcome |
|----------|---|---|
| **Managed incident** | Immediate acknowledgment, regular updates, accurate timeline | Trust remains intact |
| **Silent incident** | No communication or vague updates delivered late | Disproportionate trust damage |

Users experiencing an outage are already frustrated. Silence confirms their worst assumption: *the company doesn't care or doesn't know.*

**Why this matters for PMs:** The communication failure is often worse than the technical failure in terms of user impact. Owning incident communication means understanding this distinction deeply.

---

### Postmortem action items must ship

> **The follow-through failure:** Postmortems produce action items that enter the backlog and compete with feature work.

**The pattern that repeats:**
1. Incident occurs → postmortem conducted
2. Action items generated: add circuit breaker, add monitoring, redesign error handling
3. Items deprioritized under sprint pressure
4. Same failure mode causes next incident
5. Cycle repeats

⚠️ **The BrightChamps KB pattern:** Critical and High severity items documented in technical debt tables without active owners or timelines represent organizational failure to learn.

**What separates learning organizations:** Treating postmortem action items as non-negotiable sprint commitments—not optional backlog work.

---

### On-call culture determines team capacity and incident quality

| Factor | Poor On-Call Culture | Sustainable On-Call Culture |
|--------|---|---|
| **Team rotation** | Same engineers on-call continuously, no depth for rotation | Engineers rotate with adequate rest periods |
| **Incident handling** | Exhausted responders make mistakes | Alert, capable responders |
| **Automation investment** | Chronically deprioritized (no time to build) | Active runbook and automation development |
| **Team retention** | High attrition; best engineers leave | Engineers stay; sustainable workload |

⚠️ **For PMs managing incident-responsible teams:** On-call sustainability is a product health concern. An engineering team burning out on on-call produces worse software.

**Strategic investment:** Runbooks, monitoring improvements, and incident automation are investments in team capacity—not just operational overhead.

## S2 — How this connects to the bigger system

| Concept | Connection | Role |
|---|---|---|
| Monitoring & Alerting (03.09) | Automated detection layer; without it, incidents discovered through user reports (adding minutes to hours of undetected impact) | **Detection** |
| Scalability Patterns (09.04) | Most P0/P1 incidents at scale stem from database saturation, cascading failures, missing circuit breakers | **Prevention** |
| Feature Flags (03.10) | Enable instant mitigation for feature-caused incidents without code deployment | **Mitigation** |
| OWASP Top 10 (09.03) | Security incidents require specialized response: legal notification, regulatory reporting, evidence preservation | **Compliance** |
| GDPR & Data Privacy (09.02) | Breach notification to regulators **within 72 hours** of becoming aware of unauthorized personal data access | **Compliance** |

---

### Deep connections

**Monitoring & Alerting (03.09)**  
The BrightChamps stack (New Relic, Kibana, Slack alerts) is the triggering mechanism for incident response. Without automated alerting, incidents are discovered through user reports — adding minutes to hours of undetected impact before response begins.

**Scalability Patterns (09.04)**  
Circuit breakers, auto-scaling, and async processing reduce both frequency and severity of incidents. These patterns are the incident prevention layer — most P0/P1 incidents at scale are scalability failures (database saturation, cascading service failures, missing circuit breakers).

**Feature Flags (03.10)**  
"Kill switch" feature flags are the fastest incident mitigation for newly shipped features. Feature flags enable instant rollback to previous behavior without a code deployment when a new release causes a P1.

**OWASP Top 10 (09.03)**  
Security incidents are a specialized subset with specific response requirements. Unauthorized data access (OWASP #1) requires legal notification, potential regulatory reporting, and evidence preservation — steps not required in non-security incidents.

⚠️ **GDPR & Data Privacy (09.02)**  
**Article 33 requires breach notification to regulators within 72 hours** of becoming aware of a personal data breach. Any incident involving unauthorized access to user data is a potential GDPR breach, triggering a parallel regulatory response process alongside technical incident response. PMs on products with EU users must know this timeline.

## S3 — What senior PMs debate

### The transparency paradox: how much to tell users

| Perspective | Argument | Risk |
|---|---|---|
| **Transparency** | Detailed postmortems (e.g., GitLab's 2017 database deletion incident) build trust with technical users. Demonstrates organizational maturity, honesty, and genuine learning. | None inherent to transparency |
| **Opacity** | Detailed postmortems educate potential attackers about system vulnerabilities. Exposes engineering decisions to legal liability. | Trust erosion; perception of incompetence |

**Practical resolution:**
Publish enough to demonstrate root cause understanding and remediation, *without* specific architectural details that create security risk.

✅ Example: "We experienced a database replication failure due to misconfiguration in our backup verification process. We have implemented automated backup testing and updated our deployment procedures."

> **The real skill:** Judgment per incident. The line between useful transparency and operational security disclosure is contextual, not absolute.

---

### The incident severity classification debate: science or art?

**The stakes:**
- Under-classify → P0 gets P2 response times
- Over-classify → Team burns out on false P0s and stops taking them seriously

| Approach | Advantage | Limitation |
|---|---|---|
| **Automated classification** (rules: if error rate > 5% for > 2 min AND affects payment endpoints = P0) | Consistent; removes human bias under pressure | Brittle. A 5% error rate on low-traffic API ≠ 5% on checkout API |
| **Human judgment** | Calibrated to context; understands business nuance | Inconsistent; degrades under pressure |

**Most mature organizations:** Automated classification as initial signal + human confirmation for P0/P1.

> **PM's role in this debate:** Define severity criteria in terms of *user impact*, not just technical metrics.

---

### Incident management and AI systems: the new edge cases

⚠️ **The problem:** AI systems (LLM inference, recommendation models, classification pipelines) fail *without generating traditional incident signals*.

| Failure Mode | Detection Gap | Impact |
|---|---|---|
| Degraded model quality (hallucinating, recommending irrelevant content, misclassifying at elevated rates) | Standard monitoring (error rates, latency) won't detect it | Users see broken features; metrics look healthy |
| Model drift | Traditional monitoring blind spot | Silent quality degradation over time |
| Training data anomalies | Not visible in production logs | Systematic failures emerge slowly |

**What's needed:**
- **ML observability** discipline: model drift detection, output quality scoring, data distribution monitoring
- **Quality metrics** (not just availability metrics) as trigger conditions for incidents
- **Postmortem processes** that account for failure modes like training data drift (absent in traditional software)

> **For PMs shipping AI-native features in 2025:** Your incident management framework must treat *quality* as infrastructure, not afterthought.