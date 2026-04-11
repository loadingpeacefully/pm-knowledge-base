---
lesson: Authentication vs Authorization
module: 09 — security and scale
tags: tech
difficulty: working
prereqs:
  - 01.02 — API Authentication: authentication tokens (JWT, API keys) are the mechanism that auth decisions rely on; this lesson builds on that infrastructure
  - 02.09 — PII & Data Privacy: authorization decisions determine which users can access which PII; access control is how privacy is enforced at the code level
writer: staff-engineer-pm
qa_panel: Staff Engineer, Senior PM, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/auth-flow-revamp-student-dashboard.md
  - technical-architecture/api-specifications/api-student-details-get.md
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

The earliest computer systems had no concept of individual users. You sat down at a terminal, and the system trusted you completely. There were no passwords, no permissions — if you were at the keyboard, you could access everything. This worked when computers were expensive and physically secured in server rooms with locked doors. The physical barrier was the security model.

As computers networked together and then connected to the public internet, the physical security model broke down entirely. The terminal could be anywhere; the system had no way to tell who was at the other end. This created two distinct problems that needed separate solutions.

The first problem: how does the system know who you are? You could claim to be anyone. The system needed a way to verify your identity before doing anything else. This became authentication.

The second problem: once the system knows who you are, what are you allowed to do? Not everyone should be able to access everything. A student shouldn't be able to see other students' grades. A customer service agent shouldn't be able to change billing rates. This became authorization.

These two concepts are often confused — and when they're confused in software design, security vulnerabilities follow. The confusion usually goes in one direction: teams implement authentication (proving who you are) but then assume it implies authorization (what you can do). A logged-in user isn't automatically a trusted user for all operations.

## F2 — What it is, and a way to think about it

> **Authentication (authn):** The process of verifying that you are who you claim to be. It answers: "Who are you?" The system checks your credentials — password, biometric, token, magic link — and confirms your identity.

> **Authorization (authz):** The process of determining what you're allowed to do. It answers: "What can you access?" The system checks your identity against permissions and decides whether you can perform a specific action.

### The Critical Relationship

| Aspect | Authentication | Authorization |
|--------|---|---|
| **Question answered** | Who are you? | What can you do? |
| **Happens when** | At login/credential submission | After authentication succeeds |
| **Based on** | Credentials (password, biometric, token) | Identity + permissions ruleset |
| **Alone, is sufficient?** | ❌ No — creates security hole if authorization missing | ✅ Depends on authn first |

⚠️ **Security Risk:** A system that authenticates users but doesn't enforce authorization allows any authenticated user to access any data.

---

> **Session token** (also **JWT — JSON Web Token**): A credential issued after successful authentication. Instead of sending your password on every request, the system gives you a token that proves "I authenticated this user at time X with identity Y." The token is included in subsequent requests so the server knows who you are without re-authenticating.

> **Permission:** A specific action or data access granted to a user role. Examples: "Can view student reports" or "Can edit billing information."

> **Role:** A named set of permissions grouped together. Examples: "Student" (view own data, submit homework), "Teacher" (view student data, submit feedback), "Admin" (all permissions + manage user roles).

---

### Real-World Analogy: Hotel Access

| Layer | Hotel Equivalent | Digital Equivalent |
|-------|---|---|
| **Authentication** | Check-in: show ID and credit card; hotel confirms reservation and identity; receives room key card | Log in with credentials; system confirms user identity; receives session token |
| **Authorization** | Room key card unlocks *specific* areas: your room, gym, parking — but not the presidential suite | Token grants *specific* permissions: view own data, submit homework — but not edit admin settings |
| **Authentication alone** | Key card proves you're a valid guest but doesn't limit what doors you can open | Token proves you're logged in but doesn't limit what data you can access |

## F3 — When you'll encounter this as a PM

### When designing features that touch user data

Every feature that reads or writes user data has implicit authorization decisions:
- Who is allowed to see a student's class history?
- Who can edit a parent's phone number?
- Who can download a report?

These are **PM decisions about the rules of access**, not engineering decisions. If the PM doesn't specify these rules in the PRD, engineering will make them up — and the choices made under time pressure may not reflect the actual security and trust requirements.

### When BrightChamps's Masquerade Flow comes up

### BrightChamps — Admin Impersonation Tool

**What:** The student dashboard has a "Masquerade Flow" where admin users can view the platform as a specific student.

**Why:** This is an authentication bypass — the admin isn't authenticating as the student, they're using admin authorization to impersonate. It's a legitimate support and debugging tool.

**Takeaway:** Requires careful authorization design:
- Only admin-role users can trigger it
- Must be audited (who masqueraded as whom, when)
- Must be scoped (admins can view, not act as students)

⚠️ **Risk:** Any PM who specifies a "view as user" feature without thinking through authorization constraints will create a support tool that's also a security liability.

### When you're reviewing a bug related to data exposure

> **Authorization Bug vs. Authentication Bug:** "User A was able to see User B's data" is an *authorization* bug, not an *authentication* bug. The user was authenticated correctly. The authorization check — "is this user allowed to see this specific record?" — failed.

**What this reveals:** PMs who understand this distinction can better diagnose the root cause and communicate the issue to engineering correctly.

### When API endpoints are being designed

### BrightChamps — Unprotected Student Endpoint

**What:** The `GET /v1/student/details` endpoint is marked `auth: None (public endpoint)` but returns sensitive student and parent data.

**Why:** This is an authorization gap — the endpoint is accessible to anyone who knows a studentId, referralCode, or objectId.

**Takeaway:** The `isFe=true` parameter that masks parent email and phone is a partial mitigation, but the underlying issue is that the endpoint has no authentication requirement at all.

⚠️ **Risk:** A PM who reviews API designs without understanding authentication and authorization will miss this kind of exposure.

### When you're specifying an admin panel or internal tool

Admin tools always require explicit authorization thinking:

| Consideration | Question |
|---|---|
| **Role scoping** | Which employee roles can access which operations? |
| **Sensitive operations** | Do sensitive operations require secondary confirmation (a second admin approval)? |
| **Audit trail** | Are all admin actions logged for audit? |

⚠️ **Risk:** A PM who specifies "admins can reset user passwords" without specifying audit logging and role scoping has created an admin tool that's one misconfigured account away from a breach.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### Authentication mechanics

#### Step 1: Credential presentation

The user presents a credential — password, magic link token, OAuth token, biometric. For BrightChamps's standard login flow: the user enters email/password or mobile/MPIN. These credentials are validated client-side (format checks) then sent to the backend (Chowkidar service) for verification.

#### Step 2: Credential verification

The backend checks the credential against its stored representation. Passwords are never stored in plaintext — they're stored as hashed values (bcrypt, Argon2, or similar). The system hashes the submitted password and compares it to the stored hash. If they match, identity is confirmed.

> ⚠️ **Case study — BrightChamps MPIN plaintext storage (critical severity)**
>
> | Aspect | Detail |
> |---|---|
> | **What** | Mobile PINs (MPINs) stored in plaintext in a Google Sheet rather than hashed in the auth service |
> | **Impact scope** | Every mobile user's MPIN readable by anyone with Sheet access — all engineers, plus anyone with leaked Google Workspace credentials |
> | **Severity** | Critical — full credential compromise across the mobile user base |
> | **How it was found** | Internal BrightChamps auth revamp audit (pre-Chowkidar migration) flagged the Sheet as the auth source of truth |
> | **Remediation** | Migrate MPINs to hashed storage (bcrypt/Argon2) in Chowkidar service; deprecate the Sheet; rotate all MPINs post-migration |
>
> **PM lesson:** When you inherit an auth system, audit *where the credential material actually lives*, not just how the login flow works. Plaintext credential stores outside the auth service are the most common critical-severity finding in security audits — and they usually trace to a decision made years earlier when the product was smaller and "it's just a spreadsheet" felt acceptable.

#### Step 3: Token issuance

On successful authentication, the backend issues a JWT (JSON Web Token). A JWT contains:

> **JWT (JSON Web Token):** A signed token containing user identity and metadata, used to prove authentication state without re-sending credentials

| JWT Component | Contents |
|---|---|
| **Header** | Algorithm used to sign it |
| **Payload** | User ID, role, expiry time |
| **Signature** | Cryptographic proof the backend issued it |

The frontend stores this token and includes it in all subsequent API requests via the `Authorization: Bearer <token>` header.

#### Step 4: Token storage security

Where the token is stored matters enormously:

| Storage Method | Security | Vulnerability | Recommendation |
|---|---|---|---|
| `localStorage` | Low | Accessible to JavaScript; vulnerable to XSS attacks | ❌ Avoid |
| `httpOnly cookies` | High | Inaccessible to JavaScript; protected from XSS | ✅ Best practice |
| `SecureStorage` (crypto-js encrypted) | Medium | Better than localStorage but still JS-accessible in theory | ⚠️ Intermediate approach |

**BrightChamps implementation:** Uses `SecureStorage` as an intermediate step—safer than plain localStorage but below the security standard of httpOnly cookies.

#### Step 5: The JWT revocation problem

JWTs are *stateless* by design — the server can verify a token without looking anything up. That's the performance win. It's also the revocation problem: once issued, a JWT is valid until it expires. Changing the user's password, marking their account compromised, or hitting "log out all devices" does not invalidate tokens already in circulation.

| Revocation strategy | How it works | Tradeoff |
|---|---|---|
| **Short expiry + refresh tokens** | Access token expires in 5–15 min; client uses a long-lived refresh token to get a new one. Server can revoke the refresh token to cut off future access. | Compromised access token remains valid until its (short) expiry. Standard pattern for most apps. |
| **Token blacklist** | Maintain a set of revoked token IDs; check every request against it. | Adds a lookup to every request — loses the stateless performance win. Used when instant revocation is required. |
| **Session versioning** | Every JWT carries the user's session version number. Bumping the version on logout invalidates all prior tokens. | Small DB lookup per request; simpler than a blacklist; most common compromise design. |
| **Key rotation** | Emergency-only: rotate the signing key. Every token issued under the old key is instantly invalid. | Nuclear option — logs out every user. Reserved for key compromise, not individual account incidents. |

**✓ PM decision:** Short expiry + refresh token is the default. Only move to session versioning or blacklist if your threat model includes "must invalidate a session within 60 seconds" — for example, regulated industries, high-value account takeover recovery, or B2B products where IT admins need instant employee offboarding.

#### BrightChamps's four authentication flows

| Flow | Trigger | Mechanism | Primary use case |
|---|---|---|---|
| **Standard Login** | User enters credentials | Email/password or mobile/MPIN validation | Regular user login |
| **Magic Link** | Token in URL parameters | Backend validates URL token, clears params post-auth | Passwordless login, email invitations |
| **Masquerade** | Admin with target student ID | Admin permission validated, normal auth bypassed | Support debugging, "view as user" |
| **Auto-Login** | Valid stored token exists | Token expiry checked, refreshed if near expiry | Return visits, background refresh |

#### Federated identity — when a third party handles auth for you

Most products shouldn't build their own password flow. A **federated identity** approach delegates authentication to an existing identity provider (IdP) that the user already has an account with. The user signs in to the IdP, and the IdP vouches for them to your app.

| Protocol | When to use | What it gives you | Tradeoff |
|---|---|---|---|
| **OAuth 2.0** | Consumer apps ("Sign in with Google / Apple / Facebook") | Delegated authorization — user grants your app specific permissions (read email, access calendar) without giving you their password | You depend on the IdP's uptime and policy changes; users who lose their IdP account lose yours |
| **OpenID Connect (OIDC)** | Consumer auth on top of OAuth 2.0; most "Sign in with X" buttons use this | Identity layer: who the user is, not just what they can access | Adds ID token verification complexity; still vendor-dependent |
| **SAML 2.0** | Enterprise B2B — required by most SOC 2 / ISO 27001 customers | IT admins can provision and deprovision employees centrally; single sign-on across a company's entire tool stack | XML-based, verbose, older — no consumer support; only relevant if you're selling to companies |
| **Magic links / WebAuthn** | Passwordless flows when you don't want a third-party dependency | No password to steal; WebAuthn enables FIDO2 hardware-key login | Email deliverability becomes your auth SLA; WebAuthn UX is still unfamiliar for most users |

**✓ PM decision tree:**
- **B2C product, hobby-to-growth scale** → Start with OAuth 2.0 / OIDC via Google + Apple (Apple is required on iOS if you offer any third-party sign-in).
- **B2C product, regulated or medical** → Passwordless magic link + WebAuthn. Avoid sharing user identity with a third party.
- **B2B product** → SAML 2.0 is table stakes for enterprise deals. You will be asked for it in security reviews before you cross $100K ACV.
- **Multi-tenant SaaS** → SAML per tenant, with each enterprise customer's IdP handling their own user lifecycle. Never let customer A's IdP authenticate a user into customer B's workspace.

**⚠️ The multi-tenant isolation trap:** When you add SAML, you must scope the resulting session to a specific tenant. A common mistake: trust the email domain from the IdP assertion, not the tenant binding. If `user@acme.com` can authenticate via Acme's IdP AND via a leaked personal Acme account on a different IdP, you've created a cross-tenant auth bypass.

---

### Authorization mechanics

> **Role-Based Access Control (RBAC):** A model where users are assigned roles; roles have permissions; authorization checks verify whether the user's role includes the required permission for the requested action

**How RBAC evaluates requests:**

```
User (student, userId=123) 
  → Role: "student" 
    → Permissions: [view_own_data, submit_homework]

Request: GET /v1/student/details?studentId=456
Authorization check: Does "student" role have "view_other_students_data"? 
Response: NO → 403 Forbidden
```

#### Where authorization is enforced

Authorization happens at two layers — only one is secure:

| Layer | What it does | Security value |
|---|---|---|
| **UI layer** | Hide buttons/pages the user can't access | ⚠️ Cosmetic only — not security |
| **Server (API) layer** | Reject requests from unauthorized users | ✅ Enforces actual security |

**Critical principle:** A user can bypass UI controls with a direct API call. All authorization must be enforced at the server layer. UI authorization is only UX convenience.

⚠️ **BrightChamps public endpoint problem:** `GET /v1/student/details` is marked `auth: None` — no authentication required. This means anyone with a valid `studentId`, `referralCode`, or `objectId` can retrieve student and parent data including:
- Name, grade, school
- Performance data
- `isPaid`, `level`, `teacherRating`, `totalCompletedPaidClass`

The `isFe=true` parameter masks email and phone, but sensitive student data remains exposed. **PM red flag:** This is an authorization gap. Sensitive student data should require at minimum that the requester is authenticated as that student's parent, or an internal service, or an authenticated admin.

**How this kind of gap usually happens — and what should catch it:**

| Root cause | What to ask in PM review |
|---|---|
| Endpoint was built for a legitimate unauthenticated use case (referral landing page, public shareable scorecard) and never re-scoped when the payload grew | "What's the minimum data this endpoint actually needs? Can we return a stripped-down DTO for the unauthenticated case and require auth for the full record?" |
| `auth: None` was a development shortcut that never got removed | "Who reviews new endpoint auth decisions before ship? Is there an automated scanner for `auth: None` in the OpenAPI spec?" |
| Team assumed obscurity (hard-to-guess IDs) was security | "Are our IDs enumerable? (Incremental integer IDs = yes.) Does removing obscurity break the endpoint entirely?" |
| Payload grew over time — each feature added a new field to the existing response without revisiting auth scope | "Every time we add a field to a DTO, does the auth scope still match the new data sensitivity?" |

**PM process fix:** Every new endpoint with `auth: None` should go through an explicit security review, not the default PR process. Every PR that *adds a field* to a DTO returned by an unauthenticated endpoint should re-trigger that review. The gap is almost always created by incremental growth, not by a single bad decision.

#### Attribute-Based Access Control (ABAC)

> **ABAC (Attribute-Based Access Control):** An extension of RBAC that adds context to authorization decisions, enabling rules like "role X can do action Y if the data belongs to their own userId or their enrolled students"

ABAC handles cases like "students can see their own data but not others'" more cleanly than RBAC alone.

#### Token scope and least privilege

> **Least Privilege:** Grant only the minimum permissions needed for the specific context

A well-designed auth system issues tokens with minimum necessary permissions — a token issued for a student's dashboard session shouldn't include admin permissions. If the student session token is stolen (XSS, exposed in logs), the attacker only gets student-level access, not admin access.

---

### Session lifecycle

Sessions move through distinct phases. Each phase forces a concrete PM decision with a default and a tradeoff:

| Phase | What happens | PM decision | Default (consumer) | Default (regulated / B2B) |
|---|---|---|---|---|
| **Creation** | Successful auth → token issued | Session duration | 30 days (sticky login) | 8 hours (work day) or 15 min (finance/health) |
| **Use** | Token sent with each request; server validates | Refresh-on-use vs. fixed expiry | Refresh-on-use (keep active users logged in) | Fixed expiry (force re-auth on schedule) |
| **Refresh** | TokenManager detects near-expiry, requests new token silently | Is refresh silent or does it prompt? | Silent — user never sees it | Silent if <8h inactive, prompt after |
| **Expiry** | Token past expiry; backend rejects | What UX does the user see? | Soft redirect to login, preserve form state | Hard redirect with "session expired for your security" message |
| **Revocation** | Admin or user explicitly kills a token | Who can revoke what, and how fast? | User can log out current session; no "log out everywhere" | User can log out all devices; admin can force-revoke within 60s |

**✓ Recommendation:** Pick the consumer defaults unless you're in a regulated industry or selling to companies that require session controls in their security questionnaire. Don't mix — 30-day refresh-on-use sessions with admin-revocable tokens is a common middle ground that confuses users and still fails SOC 2 because the *access token* (not the refresh token) has no revocation path.

#### BrightChamps's TokenManager

The auto-login flow includes a **TokenManager** class that:
- Checks stored token expiry
- Refreshes the token before it expires
- Creates a seamless experience for returning users without requiring re-authentication

**What this reveals:** This is a PM-specified UX decision (users shouldn't be unexpectedly logged out) implemented through an architectural choice (token refresh mechanism). Session design is not purely technical — it's a UX choice with security implications.

## W2 — The decisions this forces

### Decision 1: Where to enforce authorization — UI vs. server vs. both

Every PM who designs a role-based UI must decide: where do we enforce access control?

| Approach | Security | UX | Use Case |
|----------|----------|----|----|
| **UI-only** | ❌ None (cosmetic) | ✅ Clear | Never use |
| **Server-only** | ✅ Real | ❌ Confusing errors | Functional but poor experience |
| **Both layers** | ✅ Real | ✅ Clear | ✅ **Correct pattern** |

**Why UI-only fails:** A non-admin user can directly call the admin API endpoint and retrieve data, bypassing the hidden navigation entirely.

**Why both layers works:** The UI hides or disables controls for unauthorized actions (preventing user confusion), while the server enforces identical rules on every API call (preventing bypass attacks).

> **BrightChamps model:** Permissions are managed in the Domain layer, not the UI layer — meaning authorization is evaluated in business logic, not just the frontend.

**The PM specification requirement:** When specifying a feature with access control, your PRD must include:
1. Which roles can access which UI elements (for UX design)
2. What the server-side authorization rules are (for API design)

*Missing either creates either a security gap or a confusing user experience.*

---

### Decision 2: Session duration and refresh strategy

How long should a session stay valid? This is a real PM tradeoff:

| Duration | Advantages | Disadvantages | Best For |
|----------|-----------|---------------|----------|
| **Short (15 min — 2 hrs)** | Token theft has limited window | Frequent re-auth friction | Financial apps, admin panels, sensitive transactions |
| **Long (7 — 30 days)** | Seamless experience, no interruption | Long-term attacker access if stolen | Consumer apps, moderate sensitivity |
| **Sliding (refresh on activity)** | Active users never logged out; inactive accounts time out naturally | Requires token refresh infrastructure | **Most consumer applications** |

> **Sliding sessions:** Token expiry is reset on each active use; sessions only expire when truly inactive.

**The BrightChamps design:** Auto-Login flow with TokenManager refresh implements a sliding-session model — the system silently refreshes tokens for active users so they're never unexpectedly logged out.

*This is the right call for an edtech platform where parents and students access regularly and re-authentication friction reduces engagement.*

---

### Decision 3: How to handle the masquerade pattern

"View as user" or masquerade functionality (allowing admins to impersonate users for debugging) is a common support tool request. It requires careful PM thinking:

#### Authorization requirements:

- Only **specific admin roles** should trigger masquerade (not all admins; ideally a dedicated "support" role with explicit permission)
- Masquerade should be **read-only** — admins view what the user sees but cannot take actions on their behalf (purchase, delete, message)
- **Every masquerade session must be logged:** admin identity, target user identity, start time, end time, actions taken

⚠️ **Security & Privacy:** Without audit logs, masquerade is a covert surveillance tool. With logs, it becomes a transparency mechanism — users can see who accessed their account and when, and the company can audit admin behavior.

#### What to specify in your PRD:

- Which admin roles can masquerade
- Whether masquerade sessions are read-only
- The audit log schema required
- Whether the target user is notified that an admin session occurred

## W3 — Questions to ask your engineering team

### Quick Reference
| Question | Core Risk | Priority |
|----------|-----------|----------|
| Authentication enforcement | Unauthorized data access | Critical |
| Authorization layer | Bypassed access controls | Critical |
| Token storage | XSS vulnerability | High |
| Session expiry | Prolonged token misuse | High |
| Access revocation speed | Delayed permission changes | High |
| Masquerade logging | Audit trail gaps | Medium |
| Multi-role handling | Edge case access errors | Medium |

---

### 1. Where is authentication enforced for our sensitive API endpoints — and are any endpoints public that shouldn't be?

**What this reveals:** The system's exposure surface for unauthenticated data access.

⚠️ **Live risk:** BrightChamps `GET /v1/student/details` endpoint has `auth: None` but returns student and parent data.

**Follow-up:** If engineering answers "most endpoints require a valid JWT, but some internal endpoints are public," request a complete list of public endpoints and audit them for data exposure.

> **Key principle:** Public endpoints serving user data are a common security gap.

---

### 2. Where in the stack is authorization enforced — UI layer only, or server layer?

**What this reveals:** Whether authorization controls can be easily bypassed.

⚠️ **Critical issue:** If the answer is "we check roles in the frontend," authorization is cosmetic only.

> **Non-negotiable:** Authorization enforcement must exist at the API/service layer. UI-only checks are one API call away from being bypassed.

---

### 3. How are tokens stored on the client, and what's the plan for httpOnly cookies?

**What this reveals:** Vulnerability to cross-site scripting (XSS) attacks.

| Storage Method | XSS Vulnerable | Notes |
|---|---|---|
| `localStorage` | ✅ Yes | Any XSS attack can steal tokens |
| `sessionStorage` | ✅ Yes | Session-scoped but still accessible to XSS |
| `SecureStorage` (encrypted) | ⚠️ Partial | Interim improvement; not XSS-proof |
| `httpOnly` cookies | ❌ No | Inaccessible to JavaScript; XSS-resistant |

**Migration example:** BrightChamps moved from plain `localStorage` → `SecureStorage` (encrypted) as interim step, with planned migration to `httpOnly` cookies for full XSS protection.

⚠️ **High severity:** If the answer is "localStorage, we haven't looked at this," add to security backlog immediately.

---

### 4. What is the session expiry model — fixed expiry, sliding expiry, or never-expiring?

**What this reveals:** How long a stolen token remains usable.

| Expiry Model | Security | UX Impact | Best For |
|---|---|---|---|
| Never-expiring | ❌ Critical risk | Best | (Avoid entirely) |
| Fixed 30-day | ⚠️ Risky | Good | Legacy systems |
| Sliding window (short idle + absolute max) | ✅ Balanced | Good | Most applications |

**Recommended:** 30-minute idle expiry + 30-day absolute maximum with refresh token flow.

> **Core tradeoff:** Never-expiring tokens grant permanent access if stolen. Short absolute maximums require token refresh but limit attacker window.

---

### 5. When an admin changes a user's role or revokes access, how quickly does it take effect?

**What this reveals:** The gap between permission change and token invalidation.

⚠️ **JWT limitation:** JWTs are cryptographically self-contained — the server validates them without checking a database. A revoked user's existing token still works until it expires.

**Required for immediate revocation:** A token revocation mechanism (blocklist or short token expiry).

**Follow-up:** If the answer is "it takes effect when their current session expires," ask how long that might be. For terminated employees or compromised accounts, delays are unacceptable.

---

### 6. Are masquerade sessions logged, and what does the audit log contain?

**What this reveals:** Accountability for privileged access.

⚠️ **Compliance & trust issue:** Masquerade without audit logs is a liability.

**Required audit log fields:**
- Admin identity
- Target user identity
- Timestamp
- Actions taken during masquerade session

**Red flag:** If engineering hasn't thought about logging, specify this requirement before masquerade functionality ships.

---

### 7. How does our authorization model handle edge cases — like a teacher who's also a parent, or a student with access to both free and paid content?

**What this reveals:** Whether the authorization model handles real-world complexity.

| Authorization Model | Handles Multi-Role | Handles Attributes | Complexity |
|---|---|---|---|
| Role-based (RBAC) | ❌ Fragile | ❌ Limited | Low |
| Attribute-based (ABAC) | ✅ Strong | ✅ Full | High |
| Custom hybrid | ✅ Possible | ✅ Possible | Variable |

**Common failure:** Teacher enrolls their child as a student — simplistic role model (student = one role, teacher = different role) breaks because the user now has two roles simultaneously.

> **Design principle:** Real users often have multiple roles or attributes affecting access. Authorization logic must account for overlapping permissions and context-dependent rules.

## W4 — Real product examples

### BrightChamps — Auth debt as security risk

**What:** Authentication system accumulated critical vulnerabilities: MPINs stored in plain text in Google Sheets and session tokens in unencrypted `localStorage`.

**Why:** Original system built for speed, not security. Technical debt accumulated without periodic review.

**The vulnerabilities:**
- MPINs in plain text → anyone with sheet access has every PIN
- Session tokens in `localStorage` → any XSS vulnerability exposes all tokens on the page

⚠️ **Security risk:** Neither vulnerability requires sophisticated attacks—both are beginner-level mistakes that expose the system to basic threats.

**The fix:**
- SecureStorage with crypto-js encryption replaces plain `localStorage`
- MPINs migrate to hashed storage in Chowkidar

**Takeaway:** Authentication security is not a one-time implementation. Tokens, credential storage, and session management require periodic review as threat models evolve and new authentication paths (magic links, auto-login) introduce different security properties.

---

### GitHub — OAuth scopes as authorization precision

**What:** OAuth system enforces scoped authorization—third-party apps request exact permissions (`repo:read`, `user:email`, `gist:write`), users approve/deny, scopes enforced on every API call.

**Why:** Implements least-privilege authorization—apps get exactly what they asked for, nothing more.

**How it works:**

| Request | Permission | Outcome |
|---------|-----------|---------|
| `repo:read` | Read repositories | ✓ Read allowed |
| `repo:write` | Modify repositories | Requires elevated approval |
| App with `repo:read` tries to push code | Write operation | 403 error |

**Takeaway:** When building integrations, specify exact permissions needed, explain why each is necessary, and request no more than required.

---

### Slack — Role-based access in enterprise settings

**What:** Enterprise product with detailed role hierarchy determining authorization levels across workspace and organization contexts.

**Role structure:**

| Role | Capabilities |
|------|--------------|
| Workspace member | Read public channels, post messages |
| Channel manager | Manage specific channels |
| Workspace admin | Manage members and channels |
| Organization admin | Set security policies across all workspaces |

**Why this matters:** Authorization design is not just engineering—it's a product design decision that determines how enterprise IT departments govern usage.

**GTM relevance:** Enterprise customers evaluate Slack partly on authorization capabilities. "Can we control who can invite external guests?" is an authorization question that's often an evaluation criterion for deals.

**Takeaway:** RBAC features are product features, not implementation details. They directly impact enterprise sales conversations.

---

### Google Docs — Authorization as UX

**What:** Four-level authorization model surfaces complex underlying system as intuitive mental model: can view, can comment, can edit, full ownership.

**Why this works:**

> **The mental model users understand:** Four clear permission levels map directly to collaboration needs—no technical complexity required.

> **The reality underneath:** Individual permissions, link sharing, organization-level policies create a more complex system than the UX suggests.

**Design principle:** The authorization rules you specify in the PRD become the permissions UX users experience.

**What this reveals:** 
- Well-designed authorization → users understand and trust it
- Opaque/confusing authorization → users feel frustrated or insecure about data access

**Takeaway:** Authorization is a user-facing design problem, not just a security problem. How users perceive access control shapes trust in your product.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### Authorization checks applied at the wrong layer

⚠️ **IDOR vulnerability — most common API security bug**

| Layer | Check | Result |
|-------|-------|--------|
| **Authentication** | "Is this a valid logged-in user?" | ✓ Validates JWT |
| **Authorization** | "Is this user allowed to access this resource?" | ✗ Often missing |

**The gap:** API endpoint validates the JWT but never checks whether the authenticated user has permission to access the specific resource. Any logged-in user can access another user's data by changing the `userId` or `studentId` parameter.

> **Insecure Direct Object Reference (IDOR):** When applications fail to properly verify that the authenticated user has authorization to access a specific resource, allowing attackers to enumerate and access other users' data by manipulating identifiers.

**Real severity scale:**
- **More secure:** IDOR present (auth layer incomplete)
- **Critical:** No authentication at all — BrightChamps `GET /v1/student/details` allows unauthenticated access to any studentId

---

### Session fixation and token leakage in logs

⚠️ **Tokens in logs = tokens in perpetuity**

JWT tokens commonly leak into systems where they persist indefinitely:

- **Server access logs** — when tokens live in URL query parameters instead of headers
- **Error tracking systems** — Sentry capturing full requests with auth headers
- **Third-party analytics** — token exposure across external services

**Why this matters:** Once a token enters a log file, it exists as long as the log is retained. Any unauthorized access to that log compromises every token within it.

**Architectural fixes required:**

| Component | Fix |
|-----------|-----|
| Token placement | Headers only (never URL parameters) |
| Logging systems | Strip auth headers automatically |
| Error tracking | Exclude sensitive headers from captures |

**PM responsibility:** You won't implement these fixes, but you must recognize the risk when deciding token handling patterns and log retention policies.

---

### The bootstrap authorization problem

⚠️ **Legacy bootstrap accounts = common entry point for breaches**

**The chicken-and-egg problem:** Before authorization exists, authorization can't grant admin access. Products solve this with a hardcoded "superadmin" setup process during initial launch.

**Where security breaks:**

| Stage | Security Level | Risk |
|-------|----------------|------|
| **Initial setup** | Intentionally weakened | Temporary & necessary |
| **Post-launch** | Often unchanged | ⚠️ Persists indefinitely |

**Common weaknesses in legacy bootstrap accounts:**
- Hardcoded credentials that were "temporary"
- No MFA requirement (unlike normal accounts)
- Setup process never formally decommissioned
- Often forgotten in security audits

**Production reality:** Bootstrap accounts created during initial setup but never properly secured are a frequent entry point for production security incidents.

## S2 — How this connects to the bigger system

| Concept | Connection |
|---|---|
| **API Authentication** (01.02) | Authentication tokens (JWT, API keys, session cookies) are the mechanism that carries identity between requests. Auth is the **"who are you"** infrastructure; auth tokens are how that answer travels across the network. |
| **PII & Data Privacy** (02.09) | Authorization controls are the enforcement mechanism for privacy. GDPR's requirement that users can access only their own data, and that data access is audited, is implemented through authorization rules. A privacy policy that says "users can only see their own data" requires **server-side authorization enforcement** to be real. |
| **OWASP Top 10** (09.03) | ⚠️ **Broken Access Control is OWASP's #1 most critical web vulnerability.** IDOR (accessing other users' data via manipulated IDs), privilege escalation (regular user accessing admin functions), and missing authorization checks are all instances of broken access control — directly caused by the same design gaps discussed in this lesson. |
| **Incident Management** (09.05) | A data exposure incident caused by an **authorization failure** (user accessed another user's data) requires a different incident response than an **authentication failure** (credentials were stolen). The PM needs to understand which type of failure occurred to communicate correctly with users and meet data breach notification requirements. |
| **Multi-Tenancy** (09.06) | Multi-tenant systems have an additional authorization layer: **tenant isolation**. Not only must user A not access user B's data, but organization A must not access organization B's data. Tenant-level authorization is the most critical security boundary in SaaS products. |

## S3 — What senior PMs debate

### Zero trust vs. perimeter security models

> **Zero Trust:** A security model where no request is trusted by default, regardless of origin. Every service-to-service call requires authentication and authorization against minimum necessary permissions.

Traditional security assumed traffic inside the company network was trusted. Zero Trust inverts this assumption.

| Aspect | Traditional Perimeter | Zero Trust |
|--------|----------------------|-----------|
| Trust assumption | Inside network = authorized | No default trust anywhere |
| Service-to-service calls | Network access sufficient | Requires authentication |
| Service accounts | Global access | Scoped permissions only |
| Request logging | Selective | Every request logged |
| Complexity | Lower | Higher |
| Latency impact | Lower | Higher due to auth checks |

**The PM debate:** Does the security benefit justify the architectural complexity and latency overhead? When is Zero Trust worth the cost?

---

### JWTs vs. opaque tokens for session management

| Factor | JWTs | Opaque Tokens |
|--------|------|---------------|
| **How they work** | Self-contained, cryptographically signed | Random strings stored in database |
| **Validation** | Server verifies signature (no DB lookup) | Server looks up in database |
| **Speed** | Fast and stateless | Requires database query per request |
| **Revocation** | Can't revoke before expiry | Can revoke instantly |
| **Session logout** | Requires short expiry or blocklist | Delete DB entry = instant revocation |

**Real example — BrightChamps:** An admin needs to immediately revoke a compromised student's session.
- **JWT approach:** Either accept users getting logged out frequently (short expiry) OR maintain a token blocklist (adds DB lookup, loses stateless benefit)
- **Opaque token approach:** Delete the database entry, revocation is instant

**The PM debate:** How much session revocation capability does your product require? This is a security-UX tradeoff that PMs must decide, not just engineers.

---

### Auth as a product feature vs. auth as infrastructure

> **Auth as product feature:** Authentication and authorization are evaluated by customers, have roadmaps, and drive purchasing decisions (common in enterprise).
> 
> **Auth as infrastructure:** Authentication is invisible to users and expected to work seamlessly (common in consumer products).

**Enterprise software auth features:**
- SSO integration (Okta, Azure AD)
- MFA options (TOTP, push authentication)
- Role customization interfaces
- Audit log export for compliance

**Consumer product auth:**
- Works invisibly
- Users expect frictionless login
- Not a competitive differentiator

**The PM debate:** At what growth stage does your customer segment require enterprise auth features? When does investing in auth capabilities (SOC 2 compliance, SSO, custom roles) unlock enterprise deals that justify the investment?

*This is a market and positioning decision driven by PM research into what enterprise buyers require—not by engineering's assessment of what's technically interesting to build.*