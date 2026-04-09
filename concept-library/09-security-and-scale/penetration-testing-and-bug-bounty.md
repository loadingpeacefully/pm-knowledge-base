---
lesson: Penetration Testing & Bug Bounty
module: 09 — security and scale
tags: tech
difficulty: working
prereqs:
  - 09.03 — OWASP Top 10 for PMs: penetration testing looks for OWASP-category vulnerabilities; understanding the categories gives PMs the vocabulary to read pen test findings and evaluate their severity
  - 09.01 — Authentication vs Authorization: authorization failures (Broken Access Control) are the most common finding in penetration tests; the BrightChamps disabled-auth endpoints documented in this lesson and 09.01 are canonical pen test findings
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-feed-presigned-url-create.md
  - technical-architecture/api-specifications/api-package-payment-details-get.md
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

Before structured security testing, software was tested for functional correctness — does the feature do what it's supposed to do? — but not for adversarial exploitation — what can a malicious user make it do that it shouldn't? Security was assumed to follow from correct functionality. If the login form accepted the right username and password, it was considered secure.

This assumption was wrong, and the consequences were severe. The first well-documented computer worm, the Morris Worm of 1988, exploited a Unix sendmail debug mode that worked exactly as designed — but was exploitable to propagate malicious code. The vulnerability wasn't a bug in the conventional sense; it was a security assumption that was never tested adversarially.

By the 1990s, financial institutions, government contractors, and defense systems routinely hired outside security specialists to test their systems before deployment — probing for weaknesses the development team hadn't considered. These engagements were called penetration tests (or pen tests): simulated attacks performed with authorization to find vulnerabilities before real attackers did.

The innovation of bug bounty programs, pioneered by Netscape in 1995 and institutionalized by companies like Google and Microsoft in the 2000s, extended this to a global scale: instead of hiring a small team for a fixed engagement, companies offered rewards to any security researcher who found and responsibly disclosed vulnerabilities. The crowd of researchers is large, diverse, and motivated — finding vulnerabilities that even thorough in-house testing missed.

Today, for any company handling user data or payment information, security testing is not optional. Enterprise customers request pen test reports as part of procurement. Compliance frameworks (SOC 2, ISO 27001, PCI DSS) require periodic penetration testing. And bug bounty programs are increasingly treated as table stakes for developer trust.

## F2 — What it is, and a way to think about it

> **Penetration test (pen test):** A simulated cyberattack performed by authorized security professionals against a software system, network, or application to find exploitable vulnerabilities before real attackers do.

> **Bug bounty program:** A structured, ongoing program that invites external security researchers to find and responsibly disclose vulnerabilities in exchange for monetary rewards.

### Key differences: Pen test vs. Bug bounty

| Aspect | Pen test | Bug bounty |
|---|---|---|
| **Duration** | Fixed time period | Ongoing |
| **Team** | Fixed, authorized team | External researchers (continuous) |
| **Scope** | Pre-defined | Typically broader |
| **Incentive** | Contract-based | Reward-based |

### Vulnerability definitions

> **Vulnerability:** A weakness that can be exploited.

> **Finding:** A specific vulnerability identified during a test.

> **Severity:** Classification of findings by potential impact, scored on the CVSS scale.

### Severity classification

| Severity | CVSS score | Example |
|---|---|---|
| **Critical** | 9.0–10.0 | Authentication bypass that allows any user to access any account |
| **High** | 7.0–8.9 | Authenticated endpoint returning another user's PII |
| **Medium** | 4.0–6.9 | Information disclosure in error messages |
| **Low** | 0.1–3.9 | Self-XSS affecting only the attacker's own session |

> **CVSS (Common Vulnerability Scoring System):** The industry-standard framework for rating vulnerability severity. Scores consider attack complexity, privileges required, user interaction required, and potential impact on confidentiality, integrity, and availability.

⚠️ **Responsible disclosure obligation:** Report vulnerabilities to the affected company before publishing publicly, giving them time to fix the issue. Bug bounty programs formalize this with a disclosure timeline (typically 90 days) and payment in exchange for non-publication before deployment.

### Mental model: The fire drill analogy

Think of a pen test like a **fire drill for a building:**

- **The fire marshal** (pen tester) walks the building with explicit authority to identify every fire hazard: blocked exits, missing sprinklers, improper chemical storage
- **The report** identifies specific hazards
- **The building manager** (PM) triages: 
  - Fix the blocked exit immediately *(critical)*
  - Schedule the sprinkler inspection *(high)*
  - Note the storage labeling issue for next quarter *(low)*

**Key insight:** The drill doesn't make the building fireproof—it identifies the specific hazards that would cause harm in a real fire.

## F3 — When you'll encounter this as a PM

### Enterprise customers ask for a pen test report
Enterprise procurement commonly requires a recent penetration test report (within 12 months) as part of vendor security due diligence. If the company has never done a pen test, this becomes a blocking factor for enterprise deals.

**Your responsibility:**
- Know whether a recent pen test exists
- Understand what the findings were
- Confirm critical/high findings have been remediated

### Reviewing security findings from a pen test or bug bounty
After a pen test or bug bounty submission, you receive a list of findings with severity ratings. This is a **product prioritization decision with security implications**.

**Triage decisions you'll make:**
| Decision | Timeline |
|----------|----------|
| What gets fixed | Before next release |
| What gets fixed | In next sprint |
| What gets deferred | Next quarter |
| What gets accepted | Tolerable risk |

### Deciding whether to launch a bug bounty program
As the product grows and handles more sensitive data, a bug bounty program becomes a proactive security investment.

**Strategic decisions:**
- **Scope:** Which endpoints? Which features?
- **Reward structure:** Budget for Critical vs High vs Medium findings?
- **Operations:** Can your team receive and respond to reports?

### A security researcher contacts the company directly
⚠️ **Without a bug bounty program**, security researchers who find vulnerabilities contact the company informally. If there's no published security contact, researchers may post the vulnerability publicly — giving your company **no remediation window**.

**Required hygiene:**
- Publish a security contact (security@company.com)
- Create a security.txt file
- Establish a responsible disclosure policy
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### How a penetration test works

**Scoping:** The pen test engagement begins with scope definition — what systems, what methods, what objectives.

| Scope Type | Definition | Use Case |
|---|---|---|
| **Black box** | Tester has no prior knowledge of the system | Simulates external attacker with no inside information |
| **Gray box** | Tester has limited information (user credentials, API docs) | Most common for web application tests |
| **White box** | Tester has full access (source code, architecture, admin credentials) | Most thorough; code-level security review |

**Reconnaissance:** Testers map the attack surface — enumerate endpoints, identify third-party components, discover authentication flows.

**Exploitation:** Testers attempt to exploit vulnerabilities. For web applications, this typically includes testing for OWASP Top 10 vulnerabilities: injection, broken access control, authentication failures, security misconfiguration.

**Reporting:** The pen test produces a report categorizing findings by severity, describing the attack vector, demonstrating proof of concept, and recommending remediation.

---

### What pen testers would find in BrightChamps

The BrightChamps KB documents two API vulnerabilities that would be Critical findings in any external penetration test:

#### Finding 1: `POST /v1/feed/presigned-url` — Authentication disabled

⚠️ **CRITICAL FINDING**

The KB records `auth: None (auth middleware commented out)` for this endpoint.

**Attack sequence:**
1. Discover the endpoint during reconnaissance
2. Note the lack of authentication requirement
3. Send a request with an arbitrary `userId` and receive a valid S3 presigned upload URL for that user
4. Document the attack: any unauthenticated caller can generate upload URLs attributed to any user ID, enabling content injection into any user's feed

**Why Critical:** Unauthenticated access to a functionality that modifies user content (CVSS Critical).

---

#### Finding 2: `POST /v1/package-payment` — No authentication, returns PII

⚠️ **CRITICAL FINDING**

The KB records this endpoint as having no authentication and returning payment details, student records, and parent PII (email, phone).

**Attack sequence:**
1. Discover the endpoint
2. Send requests with sequential `payment_initiation_id` values (starting from 1)
3. Each successful response returns one family's complete payment and personal data
4. Enumerate through IDs to retrieve an arbitrary number of customer records

**Why Critical:** Unauthenticated access returning full PII for any user. The auto-incrementing `payment_initiation_id` makes this trivially automatable—retrieve all records with a simple loop from ID 1 to ID 100,000.

---

### How bug bounty programs work

**Scope definition:** The bug bounty program specifies exactly what is and is not in scope.

Common scope decisions:
- Specific domains (app.company.com) vs all company domains
- Specific vulnerability types (authentication, authorization, injection) vs all vulnerabilities
- Out-of-scope rules (no DDoS, no physical access, no social engineering)

**Reward structure:** Rewards are tiered by severity.

| Severity | Typical 2024 Reward Range |
|---|---|
| Critical | $5,000–$100,000+ |
| High | $1,000–$10,000 |
| Medium | $250–$1,000 |
| Low | $50–$250 or swag |

Reward amounts depend on company size, sensitivity of data, and platform (HackerOne, Bugcrowd, self-hosted).

**Disclosure timeline:** > **Responsible Disclosure:** Standard practice allows the company 90 days to remediate before the researcher publishes details. Google Project Zero popularized this 90-day standard. If the fix isn't deployed within 90 days, the researcher can publish—creating public pressure.

**Triage and response:** The PM and security team review incoming reports, confirm the vulnerability, assess severity, assign to engineering for remediation, and communicate back to the researcher. Response time matters: slow triage frustrates researchers, and good researchers take their findings to faster-responding programs.

---

### The PM's role in security findings triage

When security findings arrive (from a pen test or bug bounty), the PM must make prioritization decisions that balance security risk against other sprint priorities:

| Severity | Remediation Timeline | Examples |
|---|---|---|
| **Critical** | Before next public deployment | Unauthenticated access to user PII, authentication bypass, SQL injection in production endpoint |
| **High** | Within 1–2 sprints | Authenticated user accessing another user's data (authorization failure), sensitive data in error messages |
| **Medium** | Within next quarter | Information disclosure in response headers, missing rate limiting on non-critical endpoints, security misconfiguration in non-production |
| **Low** | When convenient | Self-XSS, minor information disclosure with no practical exploit |

**The PM decision framework for security findings:**

1. **Verify the finding** — Confirm it's reproducible and the severity rating is accurate
2. **Assess business impact** — What user data is exposed? What operations are affected? What's the realistic attack scenario?
3. **Assign remediation** — Critical to current sprint/immediate fix; High to next sprint; Medium to quarterly backlog
4. **Communicate back** — If it's a bug bounty finding, acknowledge the researcher promptly

## W2 — The decisions this forces

### Decision 1: When and how often to do penetration tests

⚠️ **Cost & Coverage Reality:** Penetration tests are expensive ($10,000–$100,000 per engagement) and time-bounded—findings reflect only the state of the system at that moment.

| **Scenario** | **Frequency/Trigger** |
|---|---|
| **Minimum baseline** | At least annually for payment data, health data, or large PII volumes |
| | Before any major architecture change (auth, API surface, third-party integration) |
| | Before enterprise deals requiring pen test reports |
| **Event-triggered** | Before first enterprise customer onboarding |
| | Before launching in new regulated markets (HIPAA, PCI DSS) |
| | After significant security incidents (verify remediation completeness) |

> **Key limitation:** Pen tests are point-in-time. Features shipped after the test date are NOT covered.

**Complement with continuous coverage:**
- SAST tools (e.g., SonarQube) in CI/CD for code analysis
- DAST tools (e.g., OWASP ZAP) for runtime scanning
- Automated security scanning as complement to periodic manual tests

---

### Decision 2: Whether to launch a bug bounty program

Bug bounty programs scale security testing but demand operational readiness that most companies underestimate.

**Before launch, confirm readiness:**

- ✓ Defined security response process (ownership, SLA for triage, escalation path)
- ✓ Engineering capacity to remediate reported vulnerabilities  
- ✓ Budget allocated for bounties (even $500/Critical bounty adds up)
- ✓ Legal review of program terms (safe harbor, disclosure timelines)

**⚠️ The operational trap:** If the backlog of unremediated findings grows, researchers stop reporting. Budget and response capacity are not optional.

#### Company — BrightChamps
**What:** KB documents two Critical-severity production vulnerabilities (disabled auth on two endpoints).

**Why:** Launching a bug bounty program today would expose these endpoints to active researchers within hours.

**Takeaway:** Fix all known Critical and High findings *before* launching a public program. Private beta (invite-only researchers) stress-tests your triage process first.

---

### Decision 3: How to handle the gap between pen test findings and shipping priorities

Pen tests always produce findings. Medium and low findings are inevitable even in well-secured products. The challenge is integrating them into development without derailing priorities.

| **Approach** | **Outcome** |
|---|---|
| **Wrong:** Separate "security project" running independently | Security debt grows with each pen test while product development continues unaware |
| **Right:** Integrate findings into sprint backlog as first-class items | Security requirements embedded in normal prioritization |

**Right-approach prioritization:**

- **Critical findings** → P0 (stop the sprint)
- **High findings** → Sprint-level priority (displace lower-priority features)
- **Medium findings** → Backlog items (quarterly resolution target)

> **PM accountability question:** After a pen test, can you answer: How many Critical/High findings are fully remediated? What's the remediation timeline for the rest?

This is not engineering ownership—this is product ownership of security requirements.

## W3 — Questions to ask your engineering team

### Quick Reference
| Question | Reveals | Red Flag |
|----------|---------|----------|
| Pen test history | Security posture maturity | Never tested or >2 years old |
| Vulnerability disclosure process | Responsible disclosure baseline | No security.txt or contact |
| Known open vulnerabilities | Security debt and prioritization | Unresolved Critical findings |
| Automated security testing | Continuous vs. periodic coverage | No SAST/DAST in CI/CD |
| Bug bounty readiness | Team self-awareness | Unknown vulnerabilities or timeline |
| Specific endpoint remediation | Accountability and rigor | No owner or completion date |

---

### Question 1: Penetration testing history

**Ask:** When was our last penetration test, what firm conducted it, and what were the Critical and High findings — and which have been remediated?

*What this reveals:* The state of the company's security posture and compliance readiness.

| Signal | Interpretation |
|--------|-----------------|
| Never done a pen test | 🚩 Red flag for enterprise sales and compliance |
| Last test 3+ years ago | Current architecture hasn't been validated |
| Test date + severity summary + remediation status | ✅ Healthy tracking |
| Unresolved Critical findings | 🚩 P0 conversation required |

---

### Question 2: Vulnerability disclosure process

**Ask:** Do we have a process for receiving and responding to security vulnerability reports — is there a security.txt or security contact published?

*What this reveals:* Whether the company has a responsible disclosure baseline.

> **Minimum baseline:** A security contact (security@company.com) and a security.txt file at `/.well-known/security.txt`

⚠️ **Without a published process:** Researchers who find vulnerabilities have no official channel — they may publish findings instead, escalating risk.

⚠️ **Undocumented process:** The first security research contact becomes a fire drill.

---

### Question 3: Known open vulnerabilities

**Ask:** Are there any currently known security vulnerabilities — identified in pen tests, bug reports, or internal review — that haven't been remediated?

*What this reveals:* Outstanding security debt and organizational honesty about risk.

| Response | Assessment |
|----------|------------|
| "None" | Unlikely; suggests gaps in testing |
| "I don't know" | 🚩 Awareness gap |
| List with severity, owners, and timelines | ✅ Healthy state |
| Known Critical finding still open | 🚩 P0 that should preempt feature work |

---

### Question 4: Automated security testing

**Ask:** What does our automated security testing look like — do we have SAST or DAST scanning in CI/CD?

*What this reveals:* Whether security testing is continuous or periodic only.

> **SAST (Static Application Security Testing):** Scans source code for known vulnerability patterns
> **DAST (Dynamic Application Security Testing):** Tests the running application by sending adversarial requests

| Testing Model | Coverage Gap | Ideal State |
|---------------|--------------|------------|
| Periodic pen tests only | New vulnerabilities shipped between tests | Automated scanning on every commit |
| Annual human pen tests | Once per year | ✅ Combine with annual human testing |

---

### Question 5: Bug bounty readiness

**Ask:** If we launched a bug bounty program today, what findings do you think we'd receive first, and how quickly could we remediate them?

*What this reveals:* The engineering team's self-awareness about current security posture and remediation capacity.

**Healthy answer includes:**
- Known vulnerabilities that would be discovered
- Realistic remediation timeline
- Awareness of current gaps

⚠️ **"I don't know":** Suggests security posture hasn't been actively assessed.

*Use this question especially before deciding to launch a bug bounty program.*

---

### Question 6: Specific remediation: BrightChamps authentication endpoints

**Ask:** For the two BrightChamps endpoints with disabled authentication — what is the remediation timeline, and what acceptance criteria would verify the fix is complete?

*What this reveals:* Whether known Critical vulnerabilities have clear owners, timelines, and verification criteria.

**Vulnerabilities:**
- `POST /v1/feed/presigned-url` — authentication middleware disabled
- `POST /v1/package-payment` — authentication middleware missing

**Remediation:**
| Endpoint | Fix | Acceptance Criteria |
|----------|-----|-------------------|
| `/v1/feed/presigned-url` | Re-enable authentication middleware | Authenticated requests succeed; unauthenticated requests return 401 |
| `/v1/package-payment` | Add authentication middleware | Authenticated requests succeed; unauthenticated requests return 401; arbitrary userId cannot be used without auth |

⚠️ **Both require test verification:** Confirm an unauthenticated caller cannot assume an arbitrary userId.

## W4 — Real product examples

### BrightChamps — Unauthenticated critical endpoints, documented but unpatched

**What:** Two endpoints with no authentication controls:
- `POST /v1/feed/presigned-url` (auth middleware commented out)
- `POST /v1/package-payment` (no authentication, returns full payment data and parent PII)

**Why this matters:** Both vulnerabilities are trivially discoverable and exploitable. The payment endpoint is particularly severe: `payment_initiation_id` is auto-incrementing, making automated enumeration of all customer payment records and PII feasible.

**Takeaway:** The organizational pattern is more concerning than the technical flaw. These are documented as *known* vulnerabilities rather than P0 emergencies, suggesting the company hasn't internalized that **known Critical vulnerabilities require immediate remediation**, not backlog treatment.

**Remediation timeline:** Authentication middleware addition — fast, simple fix.

---

### HackerOne — The bug bounty platform standard

**What:** Largest bug bounty platform hosting programs for GitHub, Uber, Twitter, US Department of Defense. Public researcher track records and reputation scores; transparent scope, rewards, and response time commitments.

**Why this matters:** For enterprise B2B companies, HackerOne listing provides instant security credibility with enterprise buyers. The response time leaderboard creates competitive pressure for rapid triage.

**Takeaway:** Bug bounty programs signal that your company actively invites security scrutiny — a trust multiplier with security-conscious buyers.

---

### Google Project Zero — The 90-day disclosure standard

**What:** Full-time elite security research team that discloses vulnerabilities in third-party software with a **non-negotiable 90-day remediation window**. After 90 days, findings publish regardless of fix status.

**Why this matters:** Project Zero's disclosure practice became the industry standard for responsible disclosure. Published findings without fixes carry both technical exposure and reputational cost.

**Takeaway:** Plan for 90-day remediation cycles as the industry expectation for Critical security vulnerabilities. Ensure engineering capacity exists to emergency-patch on this timeline.

---

### Microsoft — Bug bounty at scale ($13.7M in 2022)

| Metric | Value |
|--------|-------|
| Total rewards (FY2022) | $13.7M |
| Researchers across | 46 countries |
| Participant count | 335 researchers |
| Highest single bounty | $200,000 (Windows RCE) |

**Why this investment:** Each Critical vulnerability caught through bounty prevents millions in breach costs, regulatory fines, and customer trust damage.

**Takeaway:** Bug bounty programs are cost-effective security testing at scale — not charity. The ROI calculation: bounty cost << breach cost prevention.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The triage failure: security findings treated as feature requests

⚠️ **Organizational Risk:** Security findings compete for sprint capacity without special status, causing Critical findings to age in the backlog alongside feature requests.

**The Problem:**
- Pen test and bug bounty findings arrive → acknowledged → backlog → age without priority
- Critical findings from 2 years ago remain open while Q3 features already have their own findings
- Root cause: organization hasn't established that Critical security findings are P0 incidents that *stop* feature work

**Who's Accountable:**
This is a PM failure as much as an engineering one. PMs who allow Critical security findings to age in the backlog are **accepting security risk on behalf of the company without explicit authorization from leadership.**

---

### The false security of the pen test report

⚠️ **False Confidence Risk:** A clean pen test report is a snapshot, not a security guarantee.

| What Companies Believe | What's Actually True |
|---|---|
| "Clean pen test 8 months ago = secure now" | Pen test was valid 8 months ago, before 30 new features shipped |
| "We're secure because we passed" | Current codebase may have vulnerabilities introduced since the test |
| "Annual pen tests are sufficient" | New code shipped since last test hasn't been security-tested |

**The Failure Mode:**
Enterprise customer asks: "When did you last do a pen test?"  
PM responds: "8 months ago" with confidence.  
Reality: Last pen test predates a major authentication system rewrite.

**The Antidote:**
Combine **continuous automated security scanning** (for new code as it ships) + **periodic pen tests** (for depth and new patterns).

---

### Researcher attrition from slow response

> **Bug Bounty Program Health:** Researcher participation depends on expected payout + likelihood of prompt payment.

**Researcher Decision Logic:**
Quality researchers choose programs based on:
1. Expected payout
2. Likelihood of getting paid quickly

**The Consequence of Slow Triage:**
Programs with 30+ day triage times, severity rating disputes, or delayed payments attract lower-quality researchers over time.

**Why This Matters:**
The best researchers on HackerOne have thousands of options. A slow program gets the researchers who couldn't get into faster programs.

| Target Response Time | Severity Level |
|---|---|
| 24–48 hours | Critical findings |
| Published SLA | Each severity level |

**PM Ownership:**
Researcher response time is a **product quality metric** for your bug bounty program.

## S2 — How this connects to the bigger system

| Concept | Connection |
|---|---|
| **OWASP Top 10** (09.03) | Pen tests are structured around the OWASP Top 10 categories. Knowing this framework lets you read pen test findings as a prioritized list of category failures rather than an undifferentiated list of bugs. The BrightChamps vulnerabilities (Broken Access Control, Auth Failures) would be the first findings in any pen test. |
| **Authentication vs Authorization** (09.01) | Authorization failures (Broken Access Control) are the most common pen test finding. Understanding the difference between authentication (*who are you*) and authorization (*what can you do*) is prerequisite for understanding and triaging access control findings. |
| **Incident Management** (09.05) | ⚠️ A Critical pen test or bug bounty finding is an incident — not a sprint item. The incident management process (declare severity, assign owner, communicate to stakeholders, resolve with defined timeline) applies to Critical security findings. |
| **GDPR & Data Privacy** (09.02) | ⚠️ A pen test finding that confirms unauthorized access to user PII is a potential GDPR breach — triggering the 72-hour notification requirement. Dismissing PII-related pen test findings as "theoretical" may result in unintentionally failing to notify regulators of a discovered breach. |
| **Feature Flags** (03.10) | Feature flags can be used as temporary mitigations for pen test findings that require longer fixes: disable the vulnerable feature behind a flag while the permanent fix is developed. This reduces exposure time without requiring an emergency code deployment. |

## S3 — What senior PMs debate

### Internal red team vs external pen test: coverage vs cost

| Factor | Internal Red Team | External Pen Test |
|--------|-------------------|-------------------|
| **Strengths** | Deep codebase knowledge; finds logic flaws; continuous review | Fresh adversarial perspective; unbiased; outsider viewpoint |
| **Weaknesses** | Shares team assumptions; may miss obvious vulnerabilities | Lacks codebase context; misses subtle logic issues |
| **Cost model** | Ongoing salary + tools | Annual engagement fee |
| **Frequency** | Continuous | Typically annual |

**Senior team resolution:** Internal security engineers for continuous review + annual external pen tests for validation

**For PMs without internal security engineers:**
- ⚠️ Annual external pen test is the minimum requirement
- Consider hiring a dedicated security engineer if: handling regulated data OR pursuing enterprise deals

---

### Bug bounty program scope: broad vs narrow

| Scope Level | Coverage | Triage Burden | Risk |
|-------------|----------|---------------|------|
| **Broad** | All domains, all vulnerability types | High; unexpected findings | Better security posture |
| **Narrow** | Specific endpoints, specific types | Low; predictable | ⚠️ Researchers find Critical vulns outside scope → no reward → immediate public disclosure likely |

**Observed pattern:** Programs starting narrow expand over time as security team triage capacity grows

**For PMs:** Start with narrow scope matching engineering's remediation capacity. Expand as organization's security response capacity grows.

---

### Responsible disclosure vs immediate public disclosure: the ethical debate

> **90-day responsible disclosure standard:** Company receives private notice; has 90 days to fix Critical vulnerabilities before public disclosure

**The tension:**
- **Private disclosure** = protects company, leaves users exposed longer
- **Public disclosure** = protects users, may trigger incident before fix exists
- **Researcher dilemma:** smaller companies without security engineers often fail to remediate within 90 days

**Emerging argument from ethicists & researchers:**
Critical user-data vulnerabilities warrant **30-day windows** (not 90) to create stronger remediation incentives for large companies with resources

⚠️ **For PMs:** 
- The 90-day window is a **social contract, not a legal right**
- Companies failing to remediate Critical findings within 90 days breach expected norms
- **Reputational consequence of public disclosure is the enforcement mechanism** — plan accordingly