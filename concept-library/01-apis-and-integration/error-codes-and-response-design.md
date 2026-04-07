---
lesson: Error Codes & Response Design
module: 01 — APIs and Integration
tags: tech
difficulty: working
prereqs:
  - 01.01 — What is an API: every API response carries a status code; understanding what they mean is foundational
  - 01.02 — API Authentication: 401 vs 403 are the two auth-related error codes with different meanings
  - 01.04 — Rate Limiting & Throttling: 429 is the standard error code for rate limit violations
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-student-get.md
  - technical-architecture/crm-and-sales/sales-flow.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-07
---
I'm ready to reformat PM curriculum content for maximum scannability, but I don't see any actual lesson content in your message to transform.

Please provide:
1. The lesson section text (the content between the `---` markers)
2. The section heading (if not already included)
3. Any level markers (# FOUNDATION, # WORKING KNOWLEDGE, # STRATEGIC DEPTH)

Once you share the actual prose content, I'll restructure it using:
- Comparison tables for decisions
- Blockquote callouts for definitions
- ⚠️ warnings for risk content
- Company example cards
- Engineer question analysis
- Quick reference boxes

Paste the lesson content and I'll format it immediately.
# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The error that said "successfully"

**The Incident**

A support agent filed a ticket: "The sales dashboard is showing a student as non-existent, but the parent says the child enrolled last week and paid in full."

**What the API Returned**

```json
{ "success": false, "data": null, "message": "student fetched successfully." }
```

| Field | Value | Signal |
|-------|-------|--------|
| `success` | `false` | Request failed |
| `data` | `null` | No student record |
| `message` | `"student fetched successfully."` | Success claim |
| HTTP status | 200 | "OK" |

⚠️ **The Problem: Contradictory Signals**

Three teams interpreted this response three different ways:

- **Dashboard developer** → saw HTTP 200, assumed success, didn't check `success` field
- **Support agent** → saw blank profile, had no idea if: student didn't exist, server crashed, or wrong service was queried
- **API designer** → returned contradictory metadata (failed flag + success message)

> **Result:** Zero useful error information reached the person trying to solve the problem.

This is what bad error response design looks like in production.

## F2. What it is — traffic lights for your API

Every HTTP response carries a **status code** — a three-digit number that tells the caller what happened.

> **Status Code:** A three-digit number returned with every HTTP response that indicates the outcome of the request (success, client error, or server error).

### The Traffic Light Analogy

| Light | Meaning | API Equivalent |
|-------|---------|---|
| 🔴 Red | Stop — the road is broken, this isn't your fault | Server error (5xx) |
| 🟡 Yellow | Caution — something in how you approached this isn't right | Client error (4xx) |
| 🟢 Green | Go — everything worked | Success (2xx) |

If every traffic light showed green no matter what was happening, drivers wouldn't know when to wait, when to turn back, and when to call for help. That's exactly what the student API was doing — returning 200 (green) even when nothing was found.

### Status Code Groups

**2xx — Success**
- The request worked
- `200 OK` — worked, here's the data
- `201 Created` — worked, something new was created

**4xx — Client Error**
- Something was wrong with the *request*
- Caller needs to fix something before retrying — the same request sent again will fail again
- `400 Bad Request` — invalid input
- `401 Unauthorized` — no valid token
- `403 Forbidden` — authenticated but not allowed
- `404 Not Found` — resource doesn't exist

**5xx — Server Error**
- Something broke on the *server side*
- The request was valid — the server just failed to handle it
- Caller can retry
- `500 Internal Server Error` — catch-all
- `503 Service Unavailable` — temporarily overloaded or down

### The Critical Distinction

⚠️ **4xx = fix your request; 5xx = the server is broken, try again later.**

## F3. When you'll encounter this as a PM

### Quick Reference: The Three Critical Questions
Before any API ships, require answers to:
1. What status code for a not-found record?
2. Does the error body include a request ID?
3. What status code when the server fails?

---

### During incident triage
"The checkout is broken" can mean:

| Signal | Cause | Response |
|--------|-------|----------|
| 4xx status code | Bad data from frontend | Frontend bug |
| 5xx status code | Payment service down | Infrastructure incident |

The status code tells you where to look.

---

### When writing UX error messages

| Status Code | User Action | Right Message |
|-------------|------------|----------------|
| 5xx | Can retry the same action | "Something went wrong, please try again" |
| 4xx | Must change input/data | "Please check your input and try again" |

If the frontend treats all errors the same way, users get unhelpful messages.

---

### When reviewing a PRD or API spec

⚠️ **Red flag:** An API spec that says "returns 200 on success or failure"

Ask before approval:
- What HTTP status code when the requested record doesn't exist?
- What HTTP status code when validation fails?
- What HTTP status code when the server crashes?

---

### When setting up monitoring and alerts

| Code Pattern | Interpretation | Action |
|--------------|-----------------|--------|
| Spike in 5xx rates | Something is broken | Page on-call |
| Spike in 4xx rates | Client bug deployed OR API being probed | Investigate client + logs |

You can't set up meaningful alerts without knowing which codes mean what.

---

### When a partner integrates with your API

The first thing any developer will check: your error codes.

⚠️ **Integration risks:**
- Return 200 for not-found → partner writes broken retry logic
- Error response missing code/message → debugging falls back to your support team
- Inconsistent status codes → wasted integration cycles

---
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Knows 2xx/4xx/5xx distinction and why it matters for retry logic and UX.
# ═══════════════════════════════════

## W1. How HTTP status codes and error responses actually work

### Quick Reference

| Concept | Key takeaway |
|---------|--------------|
| **Status code purpose** | Communicates retry intent and outcome semantics |
| **Response structure** | Status code + headers + body work together |
| **Most critical skill** | Matching retry logic to status code class |

---

### 1. Every response has a status code, a header set, and a body

A response has three distinct parts that work together:

- **Status code:** The three-digit number (200, 404, 500)
- **Headers:** Metadata about the response (content type, rate limit remaining, request ID)
- **Body:** The actual data (JSON, HTML, empty)

> **Key principle:** The status code travels separately from the body. A well-designed API uses the status code to communicate outcome semantics and the body to communicate details.

---

### 2. The status code communicates retry intent

This is the most practically important thing a PM needs to know:

| Code class | What it means | Retry? | UX message direction |
|---|---|---|---|
| 2xx | Worked | No | Show success state |
| 4xx | Caller's fault | No — fix the request first | "Check your input" |
| 5xx | Server's fault | Yes — try again | "Something went wrong, try again" |
| 429 | Too many requests | Yes — after waiting | "Please wait a moment, then try again" |

> **Critical pattern:** A frontend that retries on 4xx is wasting requests. A frontend that doesn't retry on 5xx is giving up too early. Retry logic depends entirely on which class of error occurred.

---

### 3. The codes PMs encounter most often

| Code | Name | When it happens | PM implication |
|---|---|---|---|
| 200 | OK | Request succeeded, data returned | Standard success |
| 201 | Created | New resource created (POST) | Confirm creation in UI |
| 204 | No Content | Succeeded but nothing to return (DELETE) | Don't try to render data |
| 400 | Bad Request | Invalid input format or missing required field | Show field-level validation error |
| 401 | Unauthorized | No token, or token is invalid/expired | Redirect to login |
| 403 | Forbidden | Token valid, but user lacks permission | Show "you don't have access" — not login |
| 404 | Not Found | Resource doesn't exist | Show empty state or "not found" |
| 409 | Conflict | Tried to create something that already exists | Show "already exists" message |
| 422 | Unprocessable Entity | Data format is valid but semantically wrong | Show domain-specific error |
| 429 | Too Many Requests | Rate limit exceeded | Show wait message, back off |
| 500 | Internal Server Error | Unhandled server crash | "Something went wrong" + retry |
| 503 | Service Unavailable | Server overloaded or down | "Temporarily unavailable" + retry |

---

### 4. The error response body needs three things

A status code tells the caller *that* something went wrong. The body tells them *why* and *how to fix it*:

```json
{
  "error": {
    "code": "STUDENT_NOT_FOUND",
    "message": "No student found with the provided ID.",
    "requestId": "req_abc123",
    "docUrl": "https://docs.example.com/errors/STUDENT_NOT_FOUND"
  }
}
```

**What each field does:**

| Field | Purpose | Example |
|-------|---------|---------|
| **`code`** | Machine-readable string for client behavior mapping | `STUDENT_NOT_FOUND` |
| **`message`** | Human-readable description for developers (not end users) | "No student found with the provided ID." |
| **`requestId`** | Unique identifier to trace error across services | `req_abc123` |
| **`docUrl`** | Direct link to error-specific documentation (for public/partner APIs) | Link to error docs |

> **Support impact:** Without `requestId`, support engineers searching logs have to guess. With it, they can find the full request trace in seconds. Without `docUrl`, every integration question becomes a support ticket.

---

### 5. The anti-pattern: 200 for everything

⚠️ **Common failure pattern in production:**

An edtech platform returns this when a student isn't found:

```json
{ "success": false, "data": null, "message": "student fetched successfully." }
```

**HTTP status code: 200**

**What breaks:**
- Monitoring systems won't count this as an error (it's a 200)
- Frontend code checking only the status code treats this as success
- The message "fetched successfully" is factually wrong

> **Why this happens:** Some older frameworks made it easier to always return 200 and encode outcome in the body. This is technical debt that creates silent failures at scale.

**Side-by-side comparison:**

| Aspect | Bad (200) | Good (404) |
|--------|-----------|-----------|
| **Status code** | 200 | 404 |
| **Response** | `{ "success": false, "data": null, "message": "student fetched successfully." }` | `{ "error": { "code": "STUDENT_NOT_FOUND", "message": "No student found with studentId 12345.", "requestId": "req_abc123" } }` |
| **Monitoring catches error?** | ❌ No | ✅ Yes |
| **Frontend shows correct state?** | ❌ No | ✅ Yes |
| **Retry logic works?** | ❌ No | ✅ Yes |
| **Support can trace it?** | ❌ No | ✅ Yes |

---

### 6. 401 vs 403 — the auth distinction that matters for UX

These are frequently confused but require different UX responses:

> **401 Unauthorized:** The server doesn't know who you are. No token, expired token, invalid signature. **Fix:** Authenticate.

> **403 Forbidden:** The server knows exactly who you are — and you're not allowed to do this. **Fix:** Get permission, not re-authentication.

**UX implications:**

| Error | User situation | UX action | Message |
|-------|---|---|---|
| 401 | Not authenticated or token expired | Redirect to login | "Please sign in to continue" |
| 403 | Authenticated but no permission | Show error state, stay on page | "You don't have access to this resource" |

---

### 7. The security consideration: 404 vs 403 for unauthorized access

⚠️ **Security design decision:** If a user requests a resource they're not allowed to see, should you return 403 (reveals the resource exists) or 404 (hides existence)?

| Scenario | Better choice | Why |
|----------|---|---|
| Admin resources, internal tools | 403 Forbidden | Cleaner UX for legitimate users; unauthorized access is expected to fail |
| Sensitive records (private messages, medical data, payment details) | 404 Not Found | Prevents unauthorized user from knowing the record exists at all |

> **Tradeoff:** Security vs. UX clarity. For most admin resources, 403 is cleaner. For sensitive data, 404 adds a security layer.

## W2. The decisions error design forces

### Quick Reference
| Decision | Default | Risk if wrong |
|---|---|---|
| Status code for "not found" | 404 | 200 responses hide errors from monitoring |
| Error response detail | `{code, message, requestId}` minimum | Stack traces leak security vulnerabilities |
| Retry logic | Only 5xx and 429 | 4xx retries waste resources and never succeed |

---

### Decision 1: What status code for "record not found"?

| Dimension | 404 Not Found ✓ | 200 with success:false ✗ |
|---|---|---|
| Best for | All new API design | Legacy APIs where changing codes would break existing clients |
| Monitoring | Error counted in status-code dashboards | Invisible — dashboards see only 200 |
| Frontend handling | Dedicated 404 handler, correct empty-state | Client must inspect body on every response |
| Retry logic | Client knows 4xx = don't retry | Client may retry a response that will never change |
| **Default** | **Use this. Always.** | Only when backward compatibility makes 404 impossible — document the exception explicitly |

> **PM default:** If your engineer proposes returning 200 for not-found because "it's simpler," push back. It makes error monitoring, retry logic, and frontend error handling all harder. The short-term simplicity creates long-term operational cost.

---

### Decision 2: How much detail in the error body?

| Dimension | Minimal<br/>(code + message only) | Verbose<br/>(code + message + field + doc_url + requestId) |
|---|---|---|
| Best for | Public APIs where you control the client | Developer-facing APIs, partner integrations |
| Security | Safer — less information for attackers | Must scrub stack traces and internal details |
| Debuggability | Slower to diagnose | Fast to diagnose |
| **Default** | **Never include stack traces. Always include requestId. Add field-level details for validation errors.** | Full verbosity for developer-facing APIs with a `docUrl` per error code |

⚠️ **Security risk:** Stack traces in production error responses expose internal code paths and library versions. Remove them before deployment.

> **PM default:** The minimum viable error response is `{ code, message, requestId }`. Stack traces in production error responses are a security vulnerability. Request IDs are non-negotiable if you have more than one service.

---

### Decision 3: Which errors are retryable?

> **Retryable:** An error where the same request sent later might succeed without any changes.

| Retryable | Not retryable |
|---|---|
| 500 Internal Server Error | 400 Bad Request |
| 503 Service Unavailable | 401 Unauthorized |
| 429 Too Many Requests (after backoff) | 403 Forbidden |
| Network timeout | 404 Not Found |
| | 409 Conflict |

> **PM default:** Build retry logic only for 5xx and 429. For 4xx, surface the error to the user — retrying won't change the outcome. This distinction should be in the frontend spec, not left to developer judgment.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **What HTTP status code do we return when a requested record doesn't exist?** | Whether the team uses 404 or the 200-with-success-false anti-pattern. If it's 200, ask whether the monitoring dashboards are watching status codes — they'll miss every not-found error. |
| **Do our error responses include a request ID?** | Whether the team can trace errors across services. In the sales flow with 6+ services in the chain (booking → CRM → payment → onboarding), a request ID is the thread that connects the failure point to the root cause. Without it, debugging a failed onboarding requires correlating timestamps across 6 different service logs. |
| **What's the difference between our 401 and 403 responses — do we have both?** | Whether auth errors are properly differentiated. If the API returns 403 for expired tokens instead of 401, the frontend may show "you don't have permission" when the real fix is "log in again." |
| **Which of our 5xx errors are transient (safe to retry) versus permanent (need investigation)?** | Whether retry logic is designed or assumed. A database connection timeout (transient 500) should be retried. A 500 caused by a schema mismatch won't be fixed by retrying. If the team hasn't categorized these, the client will either retry forever or give up too early. |
| **Do we include field-level detail in our 400 validation errors?** | Whether validation errors are actionable. `{ "message": "Bad Request" }` tells the caller nothing. `{ "code": "VALIDATION_ERROR", "field": "studentId", "message": "studentId must be a positive integer" }` tells the frontend exactly what to show and where to show it. |
| **Are 5xx rates monitored and alerting — and what's the threshold for a page?** | Whether the team has operational visibility. A 5xx rate that spikes from 0.1% to 5% in two minutes means something broke. If nobody is watching that signal, the first alert will come from a customer support ticket. |
| **What error code does the payment service return if the payment gateway is unavailable?** | Whether third-party failures are mapped to meaningful status codes. A payment gateway timeout should produce a specific error code (e.g., `GATEWAY_UNAVAILABLE`) that the frontend handles with "please try again in a few minutes" — not a generic 500 that shows "something went wrong." |

## W4. Real product examples

### Stripe — Machine-readable error codes as API design standard

**What:** Every Stripe error response includes an HTTP status code, a machine-readable `code` string (e.g., `card_declined`, `invalid_expiry_year`), a human-readable `message`, a `doc_url` linking to documentation for that specific error, and a `request_id` for support tracing.

**Why:** Developers integrating Stripe can write switch statements on `code` values — each error code maps to a specific UX action:
- `card_declined` → "your card was declined"
- `insufficient_funds` → "your card has insufficient funds"

The request ID lets Stripe's support team pull the exact transaction log from a single string. Result: a developer integration experience reliable enough to become the industry reference.

**Takeaway:** When specifying error codes for a public-facing or partner-facing API, write out the error code dictionary before engineering starts. Each code needs:
- String name
- Human description
- HTTP status
- Retryability flag
- Documentation link

This is a product spec, not an engineering implementation detail.

---

### GitHub API — 404 as a security tool

**What:** GitHub returns `404 Not Found` for private repositories that a user isn't authorized to see — even though the repository exists. An authenticated user without access gets the same response as one asking for a repository that doesn't exist.

**Why:** Returning `403 Forbidden` would reveal that the repository exists but is private — actionable information for attackers enumerating private repository names. The 404 response hides existence entirely. GitHub documents this behavior explicitly in their API docs.

⚠️ **Security implication:** For any resource that should be non-discoverable by unauthorized users (private content, draft records, other users' data), `404` hides existence. `403` leaks it.

**Takeaway:** This is a product decision with security implications, not just a technical choice. It belongs in the PRD.

---

### The edtech platform — 200-for-everything causing silent failures

**What:** The student-get API returns HTTP 200 with `{ "success": false, "data": null, "message": "student fetched successfully." }` when a student record isn't found.

**Why it failed:**
- Monitoring was configured to alert on 5xx error rates (standard practice)
- Not-found responses were invisible because they carried a 200 status code
- A data migration left 847 student records orphaned
- System showed 200 responses for every lookup — no alarms, no alerts
- Sales team discovered the problem when customers called about missing class schedules
- Records had been orphaned for **11 days** before detection

⚠️ **Critical risk:** Status codes drive alerting. `200-with-success-false` is invisible to most monitoring systems.

**Takeaway:** Before launching any feature that writes new records, confirm:
1. What the read API returns for not-found
2. That not-found is tracked as an error in your monitoring

---

### Twilio — Numeric error codes for programmable handling

**What:** Twilio's API returns HTTP status codes for request-level outcomes, plus assigns a numeric error code to every failure scenario (e.g., 21211 = "Invalid 'To' Phone Number", 21614 = "Unsubscribed recipient"). Each numeric code has dedicated documentation.

**Why:** Developers can handle specific failure scenarios programmatically:

| Error Code | Scenario | Automated Action |
|---|---|---|
| 21614 | Unsubscribed recipient | Remove from send list |
| 21211 | Invalid number | Flag record for cleanup |

Without distinct codes, all failed messages look identical and require manual investigation.

**Takeaway:** Generic error messages are a hidden cost — they turn automatable failure handling into manual support tickets. When designing an API called by business logic (not just humans), ask: "Which failure modes should the caller handle differently?" Each one needs its own error code.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Knows status code classes, retryability, error body design, and 200-for-everything as anti-pattern.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Pattern 1: 200-for-everything creates monitoring blindspots

**The problem:**
- API returns `success:false` on HTTP 200
- Monitoring systems watch HTTP status codes (the default)
- Error rates appear clean; alerts never trigger
- Actual failures hidden in body-level fields
- Discovery happens in post-mortems

**Why it compounds:**
- At scale, dozens of endpoints adopt the same pattern
- Retrofitting requires changes across every service
- Both API responses AND monitoring configs need updates

> **The blindspot:** "We were watching the wrong signal"

**PM prevention role:**
- Treat error response design as a monitoring requirement, not just API design
- Before shipping: confirm which status codes trigger alerts
- If using `success:false` on 200, require separate monitoring on the body field
- Document it explicitly — it will be forgotten otherwise

---

### Pattern 2: Stack traces in 500 responses are a security vulnerability

**The vulnerability:**
Exposing full stack traces in production error responses leaks:
- Database schema
- Internal service names
- File paths and line numbers
- Any secrets in stack frames

**How it happens (repeatedly):**
| Step | Reality |
|------|---------|
| Development | Stack traces enabled for debugging |
| Production deploy | Configuration switch disabled ✓ |
| Hotfix investigation | Re-enabled for troubleshooting |
| Aftermath | Stays on. Attacker now has everything. |

⚠️ This has happened at companies that knew better.

**PM prevention role:**
- Error response format must differ by environment
- Production format should be the default
- Verbose format requires explicit opt-in
- Add to security review checklist: "Verify stack traces are not in production error responses"

---

### Pattern 3: Inconsistent error codes across services

**The scenario:**
Sales flow spans six services. Payment fails partway through booking→demo→payment→onboarding chain.

| Dimension | Service A | Service B | Service C |
|-----------|-----------|-----------|-----------|
| Validation errors | 400 | 422 | — |
| Error structure | `{ "error": {...} }` | `{ "code": ..., "message": ... }` | — |
| Request ID | Included | — | — |

**The cost:**
- Incident responder translates between six different formats
- Every minute of translation = customer downtime
- Becomes "archaeology" rather than triage

**PM prevention role:**
- Define error response schema at platform level before the third service launches
- After three services exist, retrofitting requires coordination across every client
- Own the requirement: error format is part of the platform API contract

## S2. How this connects to the bigger system

### API Authentication (01.02)

> **401 vs. 403:** 401 = user needs to authenticate (log in again); 403 = user is authenticated but lacks permission

The distinction between these two codes is the most consequential error decision in auth-heavy products because it cascades through:
- Auth flow design
- Session expiry handling  
- Permission escalation UX

⚠️ **Critical UX risk:** Returning 403 when you should return 401 makes users see "access denied" instead of "log in again" — a mismatch that generates support tickets and frustrated users.

---

### Rate Limiting (01.04)

> **429 (Too Many Requests):** Standard rate limit response code that must include `Retry-After` header

| Element | Purpose | Impact of omission |
|---------|---------|-------------------|
| 429 status code | Signal rate limit hit | Caller knows request failed due to limits |
| `Retry-After` header | Specify seconds until retry succeeds | Clients must guess; forces custom backoff logic |

**Reference implementations:** Stripe and AWS both include `Retry-After`. An API returning 429 without it places the burden of retry delay estimation on every caller.

---

### API Gateway (01.08)

**Multi-layer error problem:** In a multi-service system, the same status code originates from different places:

| Source | Example scenario | Remediation differs |
|--------|------------------|----------------------|
| Gateway | Invalid token at entry point | Token refresh needed |
| Service facade | Service-level token rejection | Service-specific validation rules |
| Downstream dependency | Backend service timeout | Retry or circuit break |

⚠️ **Architecture requirement:** Error responses must include a `source` field identifying which layer generated the error. Without it, callers cannot route remediation correctly.

---

### Webhooks vs. Polling (01.03)

> **Webhook semantics:** Your server returns a status code to the *sender*, and the sender uses it to decide retry behavior

| Your response | Sender behavior | Consequence |
|---------------|-----------------|-------------|
| 200 OK | Stops retrying — event processed | Event is marked complete |
| 5xx | Retries the webhook | Transient failures get handled |
| 4xx | Stops retrying permanently | **Event is lost forever** |

⚠️ **Critical bug pattern:** Returning 400 for unparseable webhook messages means those events are never retried. Always return 200 to acknowledge receipt, then handle parsing failures asynchronously. Returning 4xx codes causes permanent event loss.

## S3. What senior PMs debate

### REST status code purity vs. pragmatic body-level error encoding

| Approach | Argument | Trade-off |
|----------|----------|-----------|
| **REST orthodoxy** | HTTP status codes carry semantic meaning and should be used precisely | Limited 4xx codes (handful) vs. 50+ distinct business failure modes |
| **Body-level encoding** | Move semantic richness to response body; keep HTTP layer simple | Requires parsing body on every response; breaks standard HTTP monitoring tools |
| **Envelope pattern** | `{ success: bool, data: ..., error: ... }` structure | Used by Google's older RPC-over-HTTP; abandoned by gRPC in favor of separate status field |

**Industry standard:**
- **Stripe's compromise:** Use HTTP status codes for their intended classes (success, client error, server error), then use error codes in the body for the specific business reason within that class
- *What this reveals:* Pragmatism beats purity at scale. Stripe's approach is the right answer because it satisfies both semantic clarity and tool compatibility.

---

### Error message verbosity in production: DX vs. security

| Consideration | Developer Experience | Security Posture |
|---|---|---|
| **Benefit of detailed messages** | Reduces integration time; shrinks support ticket volume | — |
| **Risk of detailed messages** | — | User enumeration (400 vs 404); field validation leaks; internal service exposure |
| **What teams choose** | Vague messages frustrate developers | Vague messages frustrate attackers |

**The mature resolution:**
- Machine-readable error codes (fully documented publicly)
- Human-readable messages describing the business problem *without* implementation details
- ✅ **Good:** "Email address is already registered"
- ⚠️ **Avoid:** "Duplicate entry in `users.email` index"

---

### AI agents as API callers: a new error-handling paradigm

> **Shift:** Error handling is no longer just human-facing. Agents must parse errors, decide retry strategy, escalate to humans, and communicate failure state.

| Response | Human capability | Agent capability |
|----------|---|---|
| 429 with `Retry-After: 30` | Read message, click retry | ✅ Actionable—waits 30s, continues |
| 500 with empty body | Try again manually | ❌ Dead end |
| 400 with `{ "code": "STUDENT_NOT_FOUND" }` | Understand business problem | ✅ Tries alternate lookup strategy |

⚠️ **Critical:** Vague 500s were tolerable when humans could manually retry. With AI agents in multi-step workflows, they become blockers with no fallback.

**Key insight:**
- *What this reveals:* Error response design is now an **AI product decision**, not just an API design decision. As agents become primary API consumers, error response quality directly determines agent reliability in production workflows.