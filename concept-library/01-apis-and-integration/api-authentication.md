---
lesson: API Authentication
module: 01 — APIs & System Integration
tags: tech
difficulty: foundation
prereqs:
  - 01.01 — What is an API — authentication is how access to an API is controlled; read first
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/auth-flow-revamp-student-dashboard.md
  - technical-architecture/api-specifications/api-student-details-get.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, AI-native PM
status: ready
last_qa: 2026-04-06
---
```markdown
<!--
  LEVEL SELECTOR
  The dashboard renders one level at a time. Switch with the level toggle.
  Foundation → Working → Strategic is the recommended reading order.
  Ex-engineers and senior PMs may start at Working or Strategic directly.
-->

# FOUNDATION

**For:** non-technical PMs, aspiring PMs, designers transitioning to PM, MBA PMs on tech modules

**Assumes:** 01.01 What is an API. You know what an API call is.

---
```

## The world before this existed

A student management team shipped a new API endpoint to serve data to their mobile app — student name, grade, class balance, parent phone number, parent email. It worked perfectly. The app loaded fast, data was accurate, parents were happy.

Three months later, a security researcher sent an email. The endpoint was public. Anyone with the URL could pass in a student ID number and retrieve a parent's full contact details. No login, no password, no credential of any kind. Just: `GET /v1/student/details?studentId=1042`. Student 1042's parent phone number came back in the JSON response. So did 1043's. And 10,000 more.

The team had built the right data endpoint. They had tested that the data was correct. They had shipped on time. What they had not done: specify who was allowed to call it.

API authentication is the answer to that question. Before any data is touched, before any logic runs, the server asks: who are you, and can I verify that? If the answer is satisfactory, the request proceeds. If not, it stops immediately.



## What it is

> **API Authentication:** The mechanism that verifies a request comes from who it claims to be before any data or action is accessed.

### The Hotel Key Card Analogy

The hotel doesn't rely on people saying "I'm in room 412." It issues each guest a physical card encoded with their room assignment. When they approach the door, the lock reads the card — not the person's claim.

- **Valid card** → door opens
- **Invalid or expired card** → rejected before the guest touches the handle

**In software:** Your API key, login token, or access credential is the key card. The server's authentication layer is the lock. Your word alone gets you nothing.

---

### Three Authentication Methods

| Method | Mechanism | Best For | Key Risk |
|--------|-----------|----------|----------|
| **API Keys** | Long unique string sent in request header | Server-to-server calls (your system calling external service) | ⚠️ Don't expire automatically; easily leaked in code, logs, or screenshots |
| **JWTs** | Signed token issued after login; contains identity + expiry | Stateless authentication; no database lookup on validation | ⚠️ Cannot be cancelled before expiry once issued |
| **OAuth2** | Standard protocol granting third-party limited, scoped access | User delegates permissions without sharing password | Third-party app can only access approved scopes, not full account |

**OAuth2 in practice:** The "Sign in with Google" flow shows you exactly what permissions the app is requesting before you approve.

## When you'll encounter this as a PM

| Scenario | What you need to decide | Why it matters |
|----------|------------------------|----------------|
| **Speccing a new endpoint** | Declare auth requirement in spec | Endpoint shipped without auth = potential data exposure |
| **Evaluating third-party vendor API** | Check auth method + token scoping | Read-only token ≠ admin token if compromised |
| **Security incident response** | Distinguish API key vs JWT compromise | Determines remediation speed (immediate vs wait-for-expiry) |
| **Mobile vs web implementation** | Understand token storage location | localStorage = JS-vulnerable; httpOnly cookie = protected |
| **Partner API access** | Choose API key vs OAuth2 | Depends on whether human or machine is in the loop |

---

### Speccing a new endpoint

Every API spec must answer: **who is allowed to call this, and how do they prove it?**

⚠️ **Risk:** An endpoint shipped without a declared auth requirement ships as a potential data exposure. This is a PM spec decision — not something to leave implied.

---

### Evaluating a third-party vendor API

Ask two questions:
1. What auth method do they use?
2. Are their tokens scoped?

> **Token scoping:** The principle that access tokens should only have the minimum permissions needed for their specific purpose.

A read-only API token does far less damage if compromised than an admin-level token. The auth design is part of your vendor evaluation criteria.

---

### A security incident happens

**Common incident:** "An API key was leaked in a GitHub commit"

⚠️ **Your decision tree:**

| Token type | What happened | Your action | Timeline |
|------------|---------------|------------|----------|
| **API key** | Leaked/exposed | Revoke and reissue | Immediate |
| **JWT** | Compromised | Can't revoke; must wait for expiry or force logout | Delayed; longer window |

Understanding this difference tells you severity and the right remediation timeline.

---

### Mobile and web have different auth rules

Where a token is stored matters.

| Storage location | Security profile | Who can access |
|------------------|-----------------|-----------------|
| Browser `localStorage` | ⚠️ **Vulnerable** | JavaScript (including malicious scripts from compromised ads) |
| `httpOnly` cookie | ✓ **Protected** | Server only; invisible to JavaScript |

Your engineers will make this call — you need to understand enough to ask whether it was made intentionally.

---

### A partner wants API access

**PM decision:** API key or OAuth2?

| Method | Best for | Tradeoff |
|--------|----------|----------|
| **API key** | Machine-to-machine integration | Simple and revocable, but less granular |
| **OAuth2** | User-consented access | More complex, but scoped and auditable per-user |

The right answer depends on whether a human user is in the loop or it's a pure machine-to-machine integration. This is a PM product decision with security implications.

## How it actually works

Authentication happens before anything else in the request lifecycle. Understanding the sequence matters because it determines what your engineers build, what fails when it fails, and what your monitoring should track.

### The request lifecycle

| Step | What happens | Key detail |
|------|--------------|-----------|
| 1. Client sends credential | API key in `X-API-Key` header, JWT in `Authorization: Bearer` header, or OAuth2 access token | Credential **always** in header — never in URL (prevents logging in server access logs) |
| 2. Auth middleware intercepts | Runs before route handlers, business logic, database queries | Extracts credential from header |
| 3. API key validation | Server queries key store: is key active? Which tenant owns it? | Involves database lookup per request; most implementations cache recent lookups |
| 4. JWT validation | Server re-computes cryptographic signature, compares to token's embedded signature | No database lookup (JWT's core advantage for high-throughput APIs); also checks `exp` field |
| 5. OAuth2 validation | Server validates access token, reads `scope` field | Scopes are explicit: `read:user`, `write:repos`, `admin:org` |
| 6. Auth fails | `401 Unauthorized` returned immediately | No data accessed, no business logic executed; includes `WWW-Authenticate` header |
| 7. Auth succeeds | Verified user ID, role, or tenant attached to request context | Every subsequent layer reads from this context |
| 8. Token refresh (JWT-specific) | Client uses refresh token to obtain new JWT | Refresh tokens are longer-lived, stored securely, revocable in database |

### Key definitions

> **Authentication:** Identity verification — "you are who you say you are"

> **Authorization:** Access control — "you're allowed to do this"

> **Refresh token:** A longer-lived credential stored more securely, used only to obtain new access tokens without requiring re-login

> **Scope:** An explicit permission granted by an OAuth2 token (e.g., `read:user`, `write:repos`, `admin:org`)

### The HTTP response tells the story

| Response | Meaning | Example |
|----------|---------|---------|
| `401 Unauthorized` | Authentication failed — server doesn't know who you are | Invalid/missing credential; expired JWT |
| `403 Forbidden` | Authentication passed but caller lacks permission | Valid token, but operation outside token's scope |

⚠️ **Common bug:** Confusing `401` and `403` in error handling. A `403` means the caller *is* authenticated — they just can't do this action. Returning `401` for a scope violation is misleading.

### How token expiry and revocation work

**JWTs:** Expire based on the embedded `exp` field. Once issued, the server cannot revoke a valid JWT — it runs until expiration.

**Refresh tokens:** Can be revoked in the database. When you need to "revoke this session," you invalidate the refresh token. The access JWT runs out naturally; the user cannot silently refresh.

*This asymmetry is why refresh tokens are stored more securely than access tokens.*

## The decisions this forces

| Decision | API Keys | JWTs |
|----------|----------|------|
| **Best for** | Server-to-server calls | User-facing, session-based flows |
| **Example** | Backend calling Stripe API | Logged-in user session token |
| **Risk if misused** | Stateless, not user-scoped | Overcomplicated for machine calls |
| **Default approach** | Machine-to-machine | User sessions |

⚠️ **Never support both methods on the same endpoint without documented justification.** This doubles your attack surface and test matrix.

---

### Token Storage: localStorage vs httpOnly Cookies

| Aspect | localStorage | httpOnly Cookies |
|--------|--------------|------------------|
| **Accessibility** | Readable by any JavaScript on the page | Invisible to JavaScript; sent auto-magically with requests |
| **Primary risk** | XSS vulnerability can silently exfiltrate all tokens | CSRF (cross-site request forgery) risk |
| **Mitigation required** | Prevent XSS (harder) | CSRF token (adds complexity) |
| **When to use** | Low-sensitivity content app with short-lived JWTs | Financial/sensitive data applications |

> **XSS (Cross-Site Scripting):** An attacker injects malicious JavaScript that runs in your user's browser and can access localStorage tokens.

> **CSRF (Cross-Site Request Forgery):** A malicious site tricks a user's browser into making requests (with httpOnly cookies attached) to your service without the user's knowledge.

⚠️ **This is a PM call.** Token storage is a product risk tolerance decision that requires understanding your threat model and sensitivity level.

---

### Token Expiry: Short-Lived vs Long-Lived

| Factor | Short-Lived (15–30 min) | Long-Lived (30+ days) |
|--------|------------------------|----------------------|
| **Damage window if stolen** | Limited | Extended |
| **Implementation complexity** | Higher (silent refresh logic needed) | Lower |
| **Appropriate for** | Payments, auth-sensitive flows | Public content feeds, low-sensitivity data |

**The right answer is threat-model specific.**

*What this reveals:* Engineers will default to "easiest to implement." The PM must force the conversation: *"What happens if this token is stolen?"*

---

### OAuth2 Scopes: Minimum Viable Access

> **OAuth2 Scope:** A permission level that limits what a third-party app can do with a user's account on another service.

**Principle:** Request only the scopes your feature actually uses.

| Scope Choice | Impact | Risk |
|--------------|--------|------|
| Requesting only what you need | ✓ Smaller blast radius if compromised | ✓ Better user trust at consent screen |
| Scope creep (e.g., `admin:org` instead of `read:user`) | ✗ Large blast radius if token compromised | ✗ User hesitation → conversion risk |

⚠️ **Scope creep is a product decision.** Each scope adds security surface and consent friction. Review scopes annually as features evolve.

---

### Refresh Token Storage

> **Refresh Token:** A long-lived credential that generates new access tokens indefinitely until revoked. The most sensitive credential in the JWT flow.

| Storage Location | Security Level | Tradeoff |
|------------------|----------------|----------|
| Memory | Lowest (lost on page reload) | Frequent re-authentication required |
| localStorage | Medium (XSS risk) | Simpler implementation, higher risk |
| httpOnly Cookies | Highest (invisible to JS, CSRF mitigated) | More complex implementation |

⚠️ **Ensure this is an explicit PM/engineering choice, not a default.** High-sensitivity applications should use httpOnly cookies. Other applications require balancing security against implementation complexity.

## Questions to ask your engineer

| Question | What this reveals | Red flag | Expected answer |
|----------|-------------------|----------|-----------------|
| **"Which endpoints currently have no auth middleware — can we audit the full list?"** | Whether auth coverage is intentional or assumed | "We think they all have auth" or "We don't have a central audit capability" | A list, or a tool that generates one |
| **"Where are JWTs currently stored on the client — localStorage or httpOnly cookies — and was that a deliberate security decision?"** | Whether storage choice was deliberate or defaulted to convenience | "localStorage because it was easier" (known risk deferred, not a decision) | Intentional choice tied to token sensitivity and risk assessment |
| **"When a user's JWT expires mid-session, what happens exactly — do we have silent refresh, or do we log them out?"** | Whether the team has thought through the full auth lifecycle and UX implications | No answer or "we haven't decided" | Silent refresh (better UX) or explicit logout flow (team understands tradeoff) |
| **"If an API key is leaked today — committed to a public GitHub repo — what's the rotation process and how many dependent services need updating?"** | The operational reality of API key management and incident response capability | "Manually update config in 12 places" | Key revocation is one-step; dependent services pick up new key from secrets manager automatically |
| **"For our OAuth2 integrations with external services — what scopes did we request, and do we actually use all of them?"** | Whether scope creep exists and if anyone has audited permissions recently | Vague answer or "we're not sure" | Recent audit; unused scopes removed; each scope mapped to a feature |
| **"If auth middleware throws an unexpected error — an exception, a timeout on the key lookup — does the request fail open or fail closed?"** | Whether the team has explicitly tested auth system resilience | "Fail open" (request passes through if auth system errors) | Always "fail closed": auth errors block requests |
| **"On our most sensitive endpoints, do we have per-user rate limiting in addition to authentication?"** | Whether the team thinks about authenticated abuse, not just anonymous abuse | No per-user rate limiting on sensitive endpoints | Per-user rate limits protecting sensitive operations (separate from auth verification) |
| **"When we issue API keys to partners, do we have an automated rotation mechanism or are they permanent until manually revoked?"** | Ops discipline and long-term credential liability | Permanent keys with no rotation policy | Automatic expiry, scheduled rotation, or rotation on personnel change |

## Real product examples — named, specific, with numbers

### Stripe — Two-key architecture as threat model design

**What:** Stripe issues two distinct API key types: publishable keys (frontend-safe, payment-initiation only) and secret keys (server-only, full account access).

**Why:** A leaked publishable key has minimal impact. A leaked secret key is total account compromise. The design makes the threat model explicit and enforces correct deployment by architecture, not documentation.

**Takeaway:** This distinction has prevented countless incidents from credentials committed to public repositories. With hundreds of billions in annual transaction volume, this design choice is directly load-bearing for trust.

---

### GitHub — OAuth2 scope system

**What:** GitHub's developer OAuth requires apps to declare granular scopes (`repo:read`, `user:email`, `admin:org`, etc.). Users see the full scope list before granting access.

**Why:** Apps requesting `admin:org` when only `repo:read` is needed show visibly higher abandonment at the consent screen. Minimal scope = better conversion.

**Takeaway:** The scope system aligns developer incentives with user security. In 2023, GitHub introduced fine-grained personal access tokens, moving from resource-type scopes to repository and action-level permissions.

---

### Zoom — API key to OAuth2 migration

**What:** Zoom deprecated JWT-based API keys (hard cutoff in 2023), forcing teams on the legacy API key path to migrate to OAuth2 within 6 months.

**Why:** Teams with clean OAuth2 integration migrated smoothly. Teams using deprecated JWT keys scrambled under deadline pressure.

**Takeaway:** Dependency on a vendor's auth mechanism is a product risk. When a vendor deprecates an auth method, you migrate on *their* timeline, not yours. Build this into your deployment architecture decisions.

---

### Firebase Authentication — Managed auth as a build-vs-buy decision

| Dimension | Managed Service (Firebase, Auth0, Clerk) | Build In-House |
|-----------|------------------------------------------|-----------------|
| **Time to production** | 1 day | 3–6 weeks |
| **Security complexity** | Vendor-handled (correct by default) | Your responsibility |
| **Auth methods** | Email/password, OAuth social, SMS, JWT | Depends on build scope |
| **Data residency** | Vendor's infrastructure (Google, Auth0 servers) | Your infrastructure |
| **Compliance overhead** | High (vendor vetting required) | Medium (your responsibility) |
| **Vendor lock-in risk** | High | None |

**PM decision framework:** Managed auth services compress time-to-market and handle security complexity correctly — but they're infrastructure dependencies that require compliance vetting *before* adoption.

⚠️ **For regulated industries** (healthcare, finance): data residency and vendor dependency create audit risk. Scope this against compliance requirements before committing.

## What breaks and why

### The "no auth" endpoint pattern that compounds

⚠️ **Most common and most expensive auth failure:** An endpoint shipped without any authentication layer because it was labeled "internal only" or "for testing."

**How it breaks:**
- Internal services call them without credentials (they never needed to set up credentials)
- Infrastructure changes occur: VPC misconfiguration, new microservice boundary, cloud migration
- What was never accessible externally becomes accessible
- Original exposure window can last **months** before detection

**PM prevention:**
- Every new endpoint requires explicit auth documentation in the spec
- "Internal only" is **not** a substitute for an auth decision
- **Gate:** If the team can't articulate what auth method an endpoint uses, it doesn't ship

---

### Token storage as deferred security debt

⚠️ **The pattern:** Tokens stored in plain localStorage to ship faster, with "migrate to httpOnly cookies in Phase 7" deferred indefinitely.

| **Approach** | **Shipping Cost** | **Migration Cost** | **Incident Cost** |
|---|---|---|---|
| **Implement httpOnly cookies at start** | Few days | — | — |
| **localStorage now, migrate later** | Days saved | Weeks + coordination | Weeks + reputational damage |

**What gets complicated:**
- Requires frontend/backend coordination
- Changes every authenticated request flow
- Full auth lifecycle regression testing needed

**PM responsibility:** Make the risk calculation explicit and document it—or push back on deferral.

---

### Refresh token revocation gaps

> **The JWT constraint:** Access tokens cannot be revoked before expiry—this is structural to the design.

**The workaround:** Refresh token revocation
- Revoke the refresh token → no new access tokens can be generated
- Requires a token store checked on every refresh

⚠️ **The gap:** Teams that implement JWT access tokens without a corresponding refresh token revocation mechanism make "log this user out on all devices" impossible.

**Why it matters:**
- Account takeover scenarios
- Abuse prevention at scale
- Compromised credentials response

**PM checkpoint:** Ensure "force logout" is a first-class feature, tested in staging, **before launch**—not a post-incident retrofit.

---

### Scope drift in partner integrations

> **OAuth2 scopes:** Requested at integration time and rarely revisited.

**The problem:**
- A partner integration from two years ago still holds `admin:write` scope
- The feature that required it may have been replaced by a dedicated API endpoint
- Excess scope persists indefinitely
- At scale: broad unused scopes = large attack surface

⚠️ **Risk exposure:** A compromised partner token can do far more than the current integration requires.

**PM responsibility:** Quarterly auth audit
- Review active partner token scopes against current integration functionality
- Reduce scope to minimum required
- Security win with zero user impact

## How this connects to the bigger system

Authentication is the entry gate for everything else in the curriculum. Understanding it compounds rapidly.

| Concept | Connection | Why it matters |
|---------|-----------|----------------|
| **What is an API (01.01)** | Establishes the request/response model that authentication sits on top of | The HTTP request lifecycle — auth middleware fires before business logic — only makes sense after you understand what an API call is. Authentication is not a separate concept; it's a mandatory layer in every API that handles non-public data. |
| **Webhooks vs Polling (01.03)** | Introduces outbound authentication | When your server calls an external webhook, the receiving endpoint must verify the request came from you, not a spoofed source. Webhook signature verification — sending a hash of the payload signed with a shared secret — applies the same core principle (prove identity via cryptographic signature) in a different direction. |
| **Rate Limiting (01.04)** | The layer *after* authentication in the security stack | Authentication answers "who are you?" Rate limiting answers "how much can you do?" These are additive, not substitutes: authenticated abuse — a legitimate user overloading an endpoint — requires rate limiting as mitigation. Revocation of their auth doesn't help if they create a new account. |
| **AI Agent Patterns (04.09)** | Creates a new auth problem without settled answers yet | An AI agent acting on behalf of a user needs credentials to call APIs on the user's behalf. Emerging questions: Do you issue long-lived API keys? Short-lived delegated tokens? OAuth2 scopes for agent actions? The pattern evolving toward scoped delegation tokens with explicit user consent per action type — but implementation varies widely. This is an active design space where understanding classic auth patterns is required to evaluate new proposals critically. |

## What senior PMs debate

### Passkeys will make passwords and JWTs obsolete for consumer auth — the timeline is the debate

| Aspect | Details |
|--------|---------|
| **Technology** | WebAuthn standard; native support from Apple, Google, Microsoft (2022–2023) |
| **How it works** | Replaces passwords with cryptographic device-bound credentials |
| **Security gains** | Phishing-resistant by design; no password to steal |
| **User experience** | Biometric unlock |
| **Adoption signals** | Google: 900M+ passkey uses (year 1); PayPal: 10% lower account takeover rate post-rollout |

**Real friction points:**
- Legacy SSO infrastructure in enterprises
- Regulated industries with specific auth compliance requirements
- Users with older devices

**PM decision framework:**
- **B2C consumer products:** Implement passkeys now, maintain password fallback
- **B2B enterprise:** Depends on whether buyers control their SSO stack

---

### The machine-to-machine auth problem is getting worse, not better

> **Machine-to-machine auth:** Service-to-service calls inside a microservices architecture, currently reliant on API keys or service account credentials stored in config files, secrets managers, or environment variables

**Why this is urgent:**
- Microservices proliferation = more credentials
- More credentials = more rotation surface
- Credential leaks = wider blast radius

| Current State | Emerging Solutions | Adoption Reality |
|---------------|-------------------|------------------|
| API keys in config | SPIFFE/SPIRE (cryptographic service identity) | Limited outside large orgs |
| Service account credentials in env vars | Short-lived Workload Identity tokens (cloud providers) | Limited outside large orgs |
| Secrets manager storage | | |

**Action for platform PMs:** Ask your infrastructure teams about the service identity model *now*, not after a service account credential is compromised.

---

### AI API authentication creates a new principal type with unclear governance

⚠️ **Risk:** An AI agent calling an API on behalf of a user is neither the user nor a traditional service account—it has an ambiguous risk profile.

| Risk Factor | What This Means |
|------------|-----------------|
| Unauthorized actions | May take actions user didn't explicitly authorize in this session |
| Unobservable context | May be running in contexts the user can't observe |
| Compounding effects | May execute actions across many systems sequentially |

**Current generation approach:**
- First generation: User-level OAuth2 tokens with broad scopes

**Future generation requirement:**
- Purpose-bound, time-limited, action-scoped delegation tokens
- Standard didn't exist two years ago; still being defined

**PM action items:**
- Design for auditability from the start
- Design for scope limitation from the start
- Prepare for regulatory pressure: "What did your AI agent do with access to my account?"

## Prerequisites

→ 01.01 What is an API — the request/response model and HTTP request lifecycle; read first



## Next: read alongside (companions)

→ **01.03 Webhooks vs Polling** — outbound authentication: how you prove your webhooks are real

## Read after (deepens this lesson)

| Lesson | Why read it |
|--------|-----------|
| **01.04 Rate Limiting & Throttling** | The layer *after* auth: controlling how much an authenticated caller can do |
| **09.01 Security & Threat Modeling** | The full threat model that auth is one component of |