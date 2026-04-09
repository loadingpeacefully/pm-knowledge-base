---
lesson: Payment Infrastructure
module: 07 — business and monetization
tags: business
difficulty: working
prereqs:
  - 07.02 — Pricing Models: pricing model determines which payment patterns (one-time, subscription, BNPL, installment) the infrastructure must support
  - 01.01 — What is an API: payment infrastructure is built on API calls between your system and payment gateways
  - 01.03 — Webhooks vs Polling: payment confirmation is always webhook-based — understanding this is essential to understanding payment flows
writer: cfo-finance
qa_panel: CFO/Finance Lead, Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/payments/payment-flow.md
  - technical-architecture/payments/payment-gateway-stripe.md
profiles:
  foundation: non-technical business PM, aspiring PM, designer PM, MBA PM
  working: growth PM, consumer startup PM, B2B enterprise PM
  strategic: ex-engineer PM, senior PM, head of product, AI-native PM
status: ready
last_qa: 2026-04-09
---

# ═══════════════════════════════════
# LEVEL 1 — FOUNDATION
# ═══════════════════════════════════

## F1 — The world before this existed

In the early years of e-commerce, each company that wanted to accept online payments had to build a direct integration with a bank or card network. This meant negotiating with Visa and Mastercard, getting a merchant account, handling encryption of card data, and maintaining that integration as payment networks changed their APIs. This was expensive, slow, and most companies simply couldn't do it.

The payment gateway industry emerged to solve this: instead of connecting to every bank directly, a company could connect to one gateway (like PayPal, Stripe, or Razorpay), and the gateway handled all the bank, card network, and compliance complexity. You got one API; the gateway dealt with everything downstream.

This created a new PM problem: payment infrastructure was now a vendor decision, an integration decision, and an ongoing operations decision, not just a "we accept credit cards" checkbox. Which gateway? For which geography? What happens when a payment gateway goes down? What happens when a webhook fires twice? What happens when a refund needs to be processed for a transaction that happened through a gateway you've since stopped using?

Every product that collects money has a payment infrastructure layer. Understanding it doesn't mean you write the code. It means you understand what decisions you're making, what can go wrong, and how to ask the right questions when it does.

## F2 — What it is, and a way to think about it

> **Payment gateway:** A third-party service that processes payments between your product and a customer's bank or card issuer. Your system sends a payment request to the gateway; the gateway talks to the bank; the gateway tells your system whether it succeeded.
>
> *Examples: Stripe (USD, AED), Razorpay (INR), PayPal, Tabby (BNPL)*

> **Payment aggregator:** Sometimes used interchangeably with gateway. Technically, an aggregator pools multiple merchants under a single merchant account (simplifying setup); a gateway is the technology layer. In practice, most modern services (Stripe, Razorpay) are both.

> **Webhook:** The mechanism by which the payment gateway notifies your system that a payment succeeded (or failed). Your system doesn't check — the gateway calls your system. This is how all modern payment flows work: your product redirects the user to the gateway, the user pays, and the gateway calls your webhook endpoint to confirm.

> **Reconciliation:** The process of verifying that what your system thinks happened (payments recorded in your database) matches what the gateway actually processed (the gateway's ledger). Discrepancies here cause revenue leakage or fraud.

### A way to think about it: The postal sorting office model

Think of payment infrastructure like a postal sorting office:

| Step | What happens | Owner |
|------|--------------|-------|
| 1 | You hand the package to a courier | You (create payment, choose gateway) |
| 2 | Courier delivers it | Gateway (user completes payment on gateway-hosted page) |
| 3 | Courier calls to confirm delivery | Gateway (webhook fires back to your system) |
| 4 | You update your records | You (database marks transaction as paid) |
| 5 | You trigger next steps | You (shipping, invoices, downstream actions fire) |

**The critical insight:** Payment infrastructure ensures each step happens **exactly once, in the right order**.

**Failure modes:**
- Step 3 fails or fires twice → your records are wrong
- Step 4 fails → customer paid but your system doesn't know
- Step 5 fires before step 4 confirms → you've sent something before money arrived

## F3 — When you'll encounter this as a PM

| Context | What happens | Payment infrastructure question |
|---|---|---|
| **Launching in a new market** | Product expands to a new country or currency | Which gateway supports that currency? What fees? What compliance requirements apply locally? |
| **Payment failure spike** | Conversion rate drops; users report checkout failures | Is the gateway down? Is there a webhook delivery issue? Is a specific payment method failing? |
| **Refund or dispute** | Customer requests refund; chargeback filed | Does the gateway support refunds via API? Who holds refund liability — gateway or platform? |
| **Revenue reconciliation** | Finance asks: "Our books say X but gateway says Y" | Is there a webhook that fired twice? A payment that succeeded at the gateway but failed in your DB? |
| **Adding a new payment method** | Business wants to accept installments or BNPL | New gateway integration required. What's the engineering effort? What does the new UX look like? |
| **PCI compliance audit** | Security review of how card data is handled | Are you using gateway-hosted pages (good) or handling raw card numbers yourself (risky)? |

### Company — BrightChamps

**What:** Payment infrastructure spanning 8 aggregators — PayPal, Razorpay, Stripe, Tabby, Tazapay, Xendit, Splitit, and Manual — each mapped to different geographies and currencies.

**Why:** Parents in different regions need locally-relevant payment methods. A parent paying in Indonesia uses Xendit (IDR); a parent in the UAE may use Stripe (AED) or Tabby (AED, BNPL).

**How it works:** When any payment succeeds, a webhook fires to BrightChamps's backend, which updates the database, triggers invoice generation, and initiates student onboarding.

**Takeaway:** This is the infrastructure layer underneath every sale. A PM who doesn't understand it can't diagnose a conversion drop, can't scope a gateway integration, and can't ask the right questions during a payment incident.
# ═══════════════════════════════════
# LEVEL 2 — WORKING KNOWLEDGE
# ═══════════════════════════════════

## W1 — How it actually works

### The full payment flow: step by step

Every payment at BrightChamps follows the same sequence across all 8 gateways:

#### Step 1 — Payment initiation
The frontend (Prashashak-FE, the sales dashboard) or the checkout system (Eklavya) calls:
```
POST /v1/payment-initiation/create-payment
```
This creates a record in the `payment_initiations` table with the selected aggregator, amount, currency, and expiry time. Nothing has been charged yet — this is just a record that payment is being attempted.

#### Step 2 — Payment link generation
The system then calls:
```
POST /v1/payment-initiation/payment-link
```
Using the `paymentInitiationId` from Step 1, the Payment-Structure microservice calls the selected gateway's SDK or API. Stripe returns a `plink_` prefixed URL (a hosted payment page on `buy.stripe.com`). Razorpay returns its own hosted link. The user is redirected to the gateway-hosted page to enter payment details.

#### Step 3 — User pays on gateway-hosted page
The user completes payment directly on the gateway's page. Your system is not involved. Card data never touches BrightChamps servers — the gateway handles all PCI-DSS compliance here.

#### Step 4 — Gateway fires webhook
When payment succeeds (or fails), the gateway calls your webhook endpoint:
```
/payment-structure/v1/payment-transaction-info/gateway/:name/create
```
For Stripe, the webhook payload contains a PaymentIntent ID (`pi_` prefix, different from the `plink_` payment link ID), the capture status, amount, and currency.

#### Step 5 — Webhook handler updates state
The `receivePayment` function:
1. Updates `payment_transaction_info` table with the gateway transaction ID
2. Calls Eklavya's `/payment-callback` to mark the sale as paid
3. Updates `sale_payments`, `student_profile` (credits), `student_class_balance` (class count) atomically
4. Queues invoice generation and student onboarding via AWS SQS

#### Step 6 — Async post-payment processing
Two SQS queues handle downstream actions:

| Queue | Action | Failure impact |
|---|---|---|
| `invoice-generation` | Lambda triggers Puppeteer to render PDF → stores in S3 → Hermes sends email | Payment already confirmed; no rollback |
| `onboard-flow` | Lambda triggers welcome emails via Hermes → provisions curriculum in Paathshala → marks CRM deal Closed Won in Prabandhan | Payment already confirmed; no rollback |

⚠️ **Critical:** SQS decoupling means if invoice generation is slow or fails, the payment is already confirmed and the student is already onboarded. Downstream failure does not roll back the payment.

---

### Why webhooks, not polling

| Approach | Latency | Load | Reliability | Trade-off |
|---|---|---|---|---|
| **Polling** | High (depends on poll frequency) | High (thousands of requests) | Risk of missed success window | Simple to build |
| **Webhooks** | Low (immediate push) | Low (event-driven) | Depends on endpoint availability | Requires idempotent, responsive handler |

> **Webhook:** A method where the payment gateway pushes the result to your system immediately when it has payment status, rather than your system repeatedly asking for updates.

**Webhook endpoint requirements:**

- **Available:** If it's down when the webhook fires, you may miss the payment confirmation
- **Idempotent:** If the gateway fires the same webhook twice (common in distributed systems), your system must process it exactly once
- **Responsive:** Gateways expect a 200 response quickly (within 5–10 seconds). Slow handlers risk webhook timeouts and retries

---

### The multi-gateway architecture

| Gateway | Currency | Geography | Payment type |
|---|---|---|---|
| **Razorpay** | INR | India | Standard card/UPI |
| **Stripe** | USD, AED | US, UAE | Standard card |
| **PayPal** | Multi | Global | Invoice-based |
| **Tabby** | AED, SAR | UAE, Saudi Arabia | BNPL (buy now pay later) |
| **Tazapay** | GBP, OMR | UK, Oman | Standard card |
| **Xendit** | IDR | Indonesia | Standard card |
| **Splitit** | USD | US | Installment (0% interest) |
| **Manual** | Any | Internal | Ops-created payments |

**PM implication:** Adding a new market requires selecting and integrating a gateway that supports the target currency and local payment methods. Not all gateways are equal — they differ in fees, fraud tooling, local bank support, and compliance requirements.

---

### The reconciliation loop

Every night (or periodically), finance reconciles:

- What BrightChamps's database says was paid (sum of `sale_payments` where `status = 'paid'`)
- What each gateway's ledger says was received
- What landed in the bank account

**Discrepancies surface four types of issues:**

1. **Webhook fired but DB write failed** — Payment succeeded at gateway, not recorded in system
2. **Duplicate webhook** — Same payment recorded twice in DB (if no idempotency guard)
3. **Manual payment not in gateway** — Manual path bypasses webhook entirely; audit trail inconsistency
4. **Refund issued at gateway, not in DB** — Gateway shows lower total; DB shows higher

## W2 — The decisions this forces

### Decision 1: Hosted payment pages vs. direct card capture

| Approach | How it works | PCI-DSS scope | PM implication |
|---|---|---|---|
| **Hosted page (gateway-managed)** | User redirected to gateway's page to enter card details | Minimal — card data never touches your servers | No PCI audit for card handling; less control over UX |
| **Direct capture (your form)** | User enters card details in your UI; you tokenize via JS SDK | Higher — even tokenization requires SAQ-A-EP compliance | Full UX control; higher engineering and compliance overhead |
| **Embedded JS (Stripe Elements, Razorpay Checkout)** | Gateway provides a JS component that renders in your UI | Moderate — card data tokenized in browser by gateway | Best of both: branded UX, reduced card scope |

### Company — BrightChamps

**What:** Uses hosted gateway pages (Stripe's `buy.stripe.com`, Razorpay's hosted link)

**Why:** Minimizes PCI scope for card handling compliance

**Takeaway:** Reduced compliance overhead but limited control over checkout UX at the payment step

---

### Decision 2: How to handle webhook failure

Webhooks are not guaranteed to be delivered exactly once. Common scenarios:

| Scenario | What happens without protection | Fix |
|---|---|---|
| **Webhook fires twice** | Payment recorded twice; double credits for student | Idempotency key: check if `txnId` already processed; skip if yes |
| **Webhook delivery fails (your endpoint down)** | Gateway retries (5–10× over hours); all retries must be safe to process | Same idempotency check handles this |
| **Webhook arrives before `payment_initiation` record committed** | Foreign key failure or null reference in DB | Small delay or retry logic in webhook handler |
| **Webhook never arrives** | Payment succeeded at gateway; DB never updated | Monitoring alert on unresolved `payment_initiations`; reconciliation catches these overnight |

⚠️ **Critical gap at BrightChamps:** No documented idempotency guard on webhook processing exists per the KB. A duplicate webhook from Stripe, Razorpay, or any gateway could create double-credits or double-bookings without alerting anyone.

> **PM action framework:**
> - **Business impact:** A duplicate webhook creates double-credits (student gets 2× classes from 1 payment), double revenue entries (finance reports incorrect revenue), and incorrect student_class_balance. At 1,000 payments/day with even a 0.1% duplicate rate, that's 1 bad record per day compounding.
> - **Remediation:** Implement a database unique constraint on `(gateway_name, txn_id)` in `payment_transaction_info`. This is a 1–2 day fix. Until it ships, add a daily reconciliation check comparing the count of `payment_transaction_info` entries against `sale_payments` entries for the same `payment_initiation_id`.
> - **Launch gate:** Any new payment feature or gateway integration must require idempotency as a launch criterion in the engineering spec — not a post-launch "we should add this later" item.
> - **Test requirement:** Specify in QA plan: "same webhook payload fires twice; confirm the system creates exactly one `payment_transaction_info` record and credits the student exactly once."

---

### Decision 3: Multi-currency and multi-gateway routing logic

When a user from a new geography begins checkout, the system must select the right gateway. This routing logic is a PM decision because it affects:

- **Conversion rate:** Wrong gateway for a market = payment method users don't trust or can't use
- **Cost:** Gateway fees range from 1.5–3.5% depending on currency, card type, and gateway agreement
- **Risk:** Some gateways have higher fraud rates for specific corridors

**Gateway selection criteria:**

1. Does the gateway support the target currency?
2. Does the gateway support the preferred local payment method (UPI in India, BNPL in UAE, GoPay in Indonesia)?
3. What is the gateway fee at the expected transaction volume?
4. What is the gateway's uptime SLA and incident history?

---

### Decision 4: BNPL and installment integration — business model implications

### Company — Tabby & Splitit

**What:** Buy-now-pay-later (BNPL) and installment gateways serving UAE, Saudi Arabia, and USD markets

**Why:** Enable customers to spread payments across multiple installments

**Takeaway:** Understand the revenue timing and fee structure before enabling

> **Business model shift:** BrightChamps receives full payment immediately (the BNPL provider pays BrightChamps upfront). The BNPL provider collects from the customer in installments. BrightChamps's revenue is not deferred — but BrightChamps pays a higher gateway fee (typically 3–6% for BNPL vs. 1.5–2.5% for standard).

**The PM decision:** Is the conversion uplift from BNPL worth the higher fee?

| Scenario | Fee impact | Decision |
|---|---|---|
| BNPL converts 15% more parents (wouldn't otherwise buy) | ₹20,000 package × 2% BNPL fee = ₹400 cost, but +15% revenue | **Enable:** net revenue positive |
| BNPL primarily serves parents who would pay full price anyway | ₹20,000 package × 2% BNPL fee = ₹400 cost, no incremental conversion | **Disable or test:** pure fee cost with no benefit |

---

### Decision 5: Payment incident response — what does the PM do?

When payment conversion drops or a gateway incident is reported, the PM's job is to triage quickly and route correctly. The common mistake: treating every payment failure as an engineering incident, when many are product or operations issues.

**Incident decision tree:**

| Symptom | First check | Likely cause | PM action |
|---|---|---|---|
| Conversion rate drops suddenly (same day) | Check gateway status page | Gateway outage | Escalate to engineering; check if fallback gateway is available; communicate to sales team |
| Conversion rate drops gradually over days | Check payment method mix and failure codes | Wrong payment method for new traffic mix; card decline rate increase | Check if traffic source changed; add local payment method if needed |
| Webhook delay — student provisioned late | Check SQS queue depth and Lambda errors | Post-payment pipeline failure | Engineering escalation; manual recovery for affected students |
| Revenue vs. gateway ledger mismatch | Check `payment_transaction_info` against gateway export | Idempotency failure, manual payment gap | Finance + engineering; run duplicate transaction audit |
| Specific geography conversion low | Check gateway's local payment method support | Card penetration low; gateway not supporting local method | Evaluate local gateway for that geography |
| User reports "payment succeeded but no access" | Check `sale_payments` status and SQS logs | DB write failed after webhook; SQS onboarding failure | Engineering fix + customer support manual recovery |

> **The PM's role in a payment incident is NOT to debug the code.** It is to:
> 1. Triage the symptom to identify whether it's a gateway, product, or data issue
> 2. Communicate estimated impact to business stakeholders
> 3. Define the customer recovery path
> 4. Ensure a postmortem captures the root cause and preventive action

---

### Decision 6: What the Manual payment path means for operations and audit

BrightChamps has a Manual payment option that allows operations teams to mark a sale as paid without going through a gateway. This serves legitimate use cases: cash payments, bank transfers, enterprise invoices. 

⚠️ **Audit and reconciliation risk:** Per the KB, the manual path bypasses the webhook flow entirely, meaning:
- No `payment_transaction_info` record is created via webhook
- No standard audit trail for the payment
- Reconciliation against gateway ledgers will always show a discrepancy for manual payments

**The PM question:** Is the manual path documented with its own audit trail? Is there a separate table or field that distinguishes manual payments from gateway payments for reconciliation purposes? If not, every finance audit creates work to manually explain the discrepancy.

## W3 — Questions to ask your engineer

| Question | Why it matters | Red flags |
|----------|----------------|-----------|
| Do we have idempotency guards on all webhook handlers — can the same webhook fire twice without double-processing? | Webhooks in distributed systems *will* retry. Processing the same payment twice is a financial error. | "We think so but it's not formally tested" / No idempotency key defined / No duplicate detection mechanism |
| What is the average time from payment completion to webhook receipt? | Determines how long your "processing" screen holds. For Stripe, typically <30s; for some gateways in high-latency regions, several minutes. | No baseline measured / UX timeout is shorter than actual gateway latency |
| What happens to a student's access if the SQS onboarding queue fails after payment? | Payment recorded ≠ student provisioned. Need visibility into whether failures are auto-caught or require manual support intervention. | No monitoring / No retry mechanism / Only manual recovery path |
| Do we verify Stripe webhook signatures using the `stripe-signature` header? | Unsigned webhooks can be spoofed by anyone with the right payload format. | Answer is "no" or "we skip this for performance" |
| When a payment fails, does the user see a specific error message from the gateway, or a generic failure? | "Card declined by issuer" → user can try different card. "Payment failed" → user is stuck. Gateway-specific errors affect conversion. | Generic errors only / No error passthrough from gateway |
| How are refunds processed — through the gateway API, or manually through the gateway dashboard? | Manual refunds = no audit trail in your DB = no systematic way to report refund rates or catch fraud. | Ops team manually logs into Stripe dashboard / No API integration for refunds |
| What is our fallback if the primary gateway for a region goes down during peak checkout traffic? | Multi-gateway setup only works if there's automatic routing logic. Manual ops intervention during peak = lost transactions. | Single point of failure / Manual failover only / No fallback gateway configured |
| How does reconciliation work — who runs it, how often, and what's the threshold for escalation? | Daily reconciliation (DB vs. gateway ledger) is a financial control. No reconciliation = discrepancies accumulate silently. | No one running it regularly / Never automated / No escalation process defined |

---

### Idempotency guards on webhooks

> **Idempotency:** The property that processing the same request multiple times produces the same result as processing it once.

Webhook handlers must be idempotent because gateways retry failed deliveries. The answer should include:
- Which field is used as the idempotency key (typically the gateway's transaction ID)
- How duplicate detection is implemented (database unique constraint, Redis cache, in-memory check)

*What this reveals:* Whether the payment system is safe under the distributed system conditions that are guaranteed to occur in production.

---

### Webhook latency baseline

Gateway latency varies widely:
- **Stripe:** typically under 30 seconds
- **High-latency regions:** several minutes possible

This directly impacts UX design: how long should you show a "processing payment" screen before declaring a timeout?

*What this reveals:* The actual latency of the payment confirmation loop and whether the current UX timeout creates correct user expectations.

---

### Post-payment pipeline reliability

A critical gap: payment recorded ≠ student provisioned.

**Questions to answer:**
- Is there monitoring for SQS queue failures?
- Is there a retry mechanism?
- Is there a manual recovery path if onboarding fails?

*What this reveals:* Whether a failed onboarding is automatically caught or requires customer support to discover and fix.

---

### Webhook signature verification

⚠️ **Security requirement:** Stripe sends a cryptographic signature with every webhook via the `stripe-signature` header. Verifying it ensures the webhook came from Stripe and wasn't spoofed.

If verification is not implemented, BrightChamps's webhook endpoint can be called by anyone with the right payload format.

*What this reveals:* The security posture of the payment webhook layer. This is explicitly documented as a high-severity tech debt gap.

---

### Error message handling

| Approach | User experience | Impact |
|----------|-----------------|--------|
| Generic errors | "Payment failed, try again" | No actionable info; user is stuck |
| Gateway-specific errors | "Card declined by issuer — try a different card" | User can self-resolve; higher conversion |

*What this reveals:* Whether the error handling layer passes gateway diagnostics through to the user, or absorbs them.

---

### Refund processing model

| Method | Audit trail | Operational maturity |
|--------|------------|----------------------|
| Gateway API integration | ✓ Recorded in BrightChamps DB | High — systematic reporting & controls |
| Manual dashboard clicks | ✗ No BrightChamps audit trail | Low — out-of-band process |

Manual refunds also create blind spots: no systematic way to report refund rates or detect fraud patterns.

*What this reveals:* Whether refund operations are integrated into the system or a manual out-of-band process — a key indicator of operational maturity.

---

### Regional failover strategy

⚠️ **Operational risk:** A single gateway outage during peak checkout can halt all transactions in a geography.

Multi-gateway infrastructure only protects you if:
- Automatic routing logic switches to a backup gateway, OR
- Manual ops intervention is fast enough to avoid significant transaction loss

*What this reveals:* The operational resilience of the payment layer.

---

### Reconciliation discipline

> **Reconciliation:** The process of comparing your payment records (in your DB) against the gateway's ledger to catch discrepancies.

| Frequency | Approach | Risk |
|-----------|----------|------|
| Daily | Automated | ✓ Discrepancies caught immediately |
| Manual, irregular | Ad hoc | ✗ Discrepancies accumulate silently |
| Never | — | ✗ No financial controls |

*What this reveals:* Whether payments are treated as a financial system requiring ongoing monitoring, or a technical system assumed to "just work."

## W4 — Real product examples

### BrightChamps — 8-gateway payment routing: the geographic complexity behind every sale

**What:** BrightChamps routes each payment to a different gateway based on the customer's geography and currency:
- Parent in India → Razorpay (INR)
- Parent in UAE → Stripe (AED) or Tabby (AED, BNPL)
- Parent in Indonesia → Xendit (IDR)
- Parent in UK → Tazapay (GBP)

**Why:** Each gateway has a different SDK, webhook payload format, error codes, refund API, and test environment. Adding a new gateway requires an integration, webhook handler, sandbox testing, and reconciliation logic—not just a configuration change.

**Takeaway:** Every new market launch is a gateway decision: not just "can we accept payments there?" but "which gateway has the best conversion rate, lowest fees, and most reliable local payment method support?"

---

### BrightChamps — Stripe integration: plink_ vs pi_ and why it matters

> **Payment Link (`plink_`):** The URL generated when BrightChamps creates a payment link; sent to the user.

> **PaymentIntent (`pi_`):** The transaction ID created when the user completes payment; arrives in the webhook.

**What:** BrightChamps's `payment_initiations` table stores the `plink_` ID at creation time. When the webhook arrives, it contains a `pi_` ID—a different Stripe object.

**Why this matters:** The mapping between the two must be maintained correctly, or reconciliation between "payment created" and "payment confirmed" breaks. Stripe's knowledge base explicitly documents this as a risk.

**Takeaway:** Any engineer working on Stripe integration or reconciliation must understand that the ID used to generate the link is not the ID used to confirm payment. This is a common source of bugs in Stripe integrations.

---

### Stripe — hosted checkout as a PCI compliance strategy

**What:** Stripe's `buy.stripe.com` hosted checkout pages mean card data is entered on Stripe's servers, not BrightChamps's. Stripe maintains PCI-DSS Level 1 certification (the highest level).

**Why:** PCI-DSS Level 1 certification costs $50,000–$200,000+ per year for direct card handling. By routing card entry through a gateway-hosted page, BrightChamps reduces its PCI scope to "SAQ-A" (the simplest tier), eliminating most compliance overhead.

⚠️ **Risk:** Any initiative to bring card data entry "in-house" (building your own payment form) fundamentally changes your PCI scope—this is a compliance and cost decision, not just a UX decision.

#### PCI-DSS Scope Levels (SAQ Types)

| SAQ Type | When It Applies | Annual Compliance Cost | Timeline |
|---|---|---|---|
| **SAQ-A** | All card entry via hosted gateway pages; no card data on your servers | $5,000–$20,000 | 1–2 months |
| **SAQ-A-EP** | JavaScript-based card capture (Stripe Elements) on your domain | $15,000–$50,000 | 3–6 months |
| **SAQ-D (full audit)** | Direct card capture via your own form; card data on your servers | $50,000–$200,000+ | 6–12 months |
| **PCI-DSS Level 1** | >6 million transactions/year; typically required by enterprise customers | $100,000–$500,000/year | Ongoing |

**Takeaway:** Every proposal to "build our own checkout form for better UX" must account for PCI scope change in the ROI calculation. Moving from SAQ-A to SAQ-A-EP could add $30,000–$50,000 in annual compliance costs and 3–6 months of pre-launch compliance work. That cost belongs in the business case, not treated as "engineering will handle it."

---

### Tabby — BNPL integration and unit economics impact

> **Buy-Now-Pay-Later (BNPL):** Payment model where customer receives the product immediately and pays in installments.

**What:** Tabby operates in UAE and Saudi Arabia. When a BrightChamps customer uses Tabby:
- Tabby pays BrightChamps the full amount immediately
- Customer pays Tabby in 4 equal installments over 6 weeks, interest-free
- Tabby charges BrightChamps a merchant fee of 4–6% of transaction value

**Unit economics:** A ₹15,000 class package paid via Tabby generates ₹900–₹1,500 less in net revenue than the same package paid via Razorpay (2% fee).

**The real question:** Does BNPL enable conversion lift?
- **If** BNPL is used primarily by customers who would have paid anyway → pure fee cost
- **If** BNPL enables net-new purchases → revenue-generative (even with higher fee)

**Takeaway:** Track BNPL conversion rate separately from standard payment method conversion rate. A 20% conversion lift on BNPL can offset the higher fees and increase revenue per 100 checkout attempts.
# ═══════════════════════════════════
# LEVEL 3 — STRATEGIC DEPTH
# ═══════════════════════════════════

## S1 — What breaks and why

### The webhook reliability trap

Products that work perfectly in testing fail in production when payment volumes increase because testing doesn't simulate the distributed system conditions of real gateways: webhook retries, out-of-order delivery, delayed arrival after network partition, and idempotency failures from duplicate events.

**The failure mode:**
- Payment gateway experiences a blip and retries all webhooks from the past 30 minutes
- System lacks idempotency guards, processes each retry as a new transaction
- Students receive double credits
- Finance sees double revenue entries
- Reconciliation gap takes weeks to untangle

> **Idempotency:** The property that processing the same request multiple times produces the same result as processing it once.

**The PM prevention role:** Before any payment feature launches, require evidence that idempotency is tested — not just "we think it handles duplicates" but a **specific test case where the same webhook fires twice and the system processes it exactly once**. This is a launch criteria item, not an engineering nice-to-have.

---

### The gateway concentration risk

Multi-gateway infrastructure creates the illusion of resilience. But if 80% of transactions run through one gateway (e.g., Razorpay for India) and that gateway experiences an outage, 80% of revenue collection stops. The other gateways don't help.

**Detection signal:** Look at the payment gateway fee line in financial reports. If one gateway accounts for >60% of total gateway fees, that's your concentration.

⚠️ **Risk window:** A 99.9% SLA (Razorpay's stated uptime) means 8.7 hours of potential downtime per year — which may not be evenly distributed across time zones and peak checkout windows.

**The fix isn't just technical:** Genuine payment resilience requires that:
- Sales teams know what to do when a gateway is down (switch to manual, offer alternative payment link, document the gap)
- Engineering team has fallback configured
- Both groups practice the response plan

---

### The reconciliation debt spiral

When reconciliation is manual and infrequent, discrepancies accumulate. A webhook that fired twice in Week 1 isn't caught until Week 4, when the finance team runs the monthly reconciliation. By then, the double-credited student has already attended 8 extra classes that weren't paid for. The refund or credit correction requires manual intervention from 3 teams.

**The compounding effect:**

Every manual path (manual payments, manual refunds, manual corrections) that bypasses the webhook flow adds a category of discrepancy that can't be automatically detected. Over time, the number of exception categories grows, making reconciliation progressively more expensive.

| Manual Path | Added Discrepancy Category | Detection Method | Risk |
|---|---|---|---|
| Manual payments | Offline txn not in gateway ledger | Manual audit | Days of lag |
| Manual refunds | Refund posted without webhook | Daily reconciliation | Double-reversal risk |
| Manual corrections | Credit adjustments outside system | Exception tracking | No audit trail |

**The structural prevention:**
- Automated daily reconciliation between the payment DB and every gateway's ledger
- Each discrepancy type gets a defined resolution path
- New payment paths (BNPL, manual, installments) must include reconciliation design as part of the integration spec

## S2 — How this connects to the bigger system

| Concept | Connection | Key Insight |
|---|---|---|
| **Webhooks vs Polling** (01.03) | Payment confirmation is the canonical webhook use case | Push vs. poll architecture explains why webhook idempotency and availability are critical PM concerns |
| **Idempotency** (01.05) | Payment webhooks must be idempotent | Directly explains failure mode: what happens when a webhook fires twice without deduplication |
| **Gross Margin & COGS** (07.03) | Gateway fees are COGS | Every transaction has a cost; gateway selection and routing affects gross margin directly |
| **Pricing Models** (07.02) | Payment type determines gateway requirements | Subscription → recurring billing support • Installments → BNPL gateways • One-time → standard gateway |
| **Unit Economics** (07.01) | Payment method mix affects LTV calculation | High BNPL usage increases per-transaction COGS; must use actual fee mix, not blended rate |
| **PII & Data Privacy** (02.09) | Payment data is highly regulated | Card numbers, billing addresses, transaction histories require PCI-DSS and GDPR compliance |
| **Error Codes & Response Design** (01.09) | Gateway errors must be user-facing | How you handle and expose errors determines whether payment failures are self-resolvable |

### The payments-finance feedback loop

> **Core dependency:** Payment infrastructure is where product and finance have the most direct shared responsibility.

**Who decides what:**
- **Product:** Gateway integrations, webhook handling, UX flows
- **Finance:** Revenue recognition, reconciliation, reporting accuracy

**What breaks:**
- Adding a gateway without a reconciliation plan
- Recognizing revenue before webhook confirmation
- Either side changing systems unilaterally

**The reliable model:**

Every new payment flow requires *both* documents reviewed together before engineering starts:

1. **Product spec:** UX, API, error handling, user flows
2. **Finance spec:** Transaction recognition timing, reconciliation appearance, exception handling paths

*What this reveals:* Payment systems demand cross-functional design—product decisions have immediate financial consequences.

## S3 — What senior PMs debate

### "Should we reduce gateway count to simplify operations, or expand it to maximize conversion?"

| Dimension | Consolidation | Geographic Specificity |
|-----------|----------------|------------------------|
| **Engineering burden** | Lower: 2–3 gateways across 10 countries | Higher: 8× failure modes, reconciliation, SDK upgrades |
| **Supported methods** | Card + multi-currency (Stripe, Checkout.com) | Local methods (UPI, GoPay, SADAD) |
| **Conversion impact** | Risk in markets with low card penetration | Aligns with local preferences |
| **Reconciliation** | Simpler model | 8× complexity per gateway added |

**The resolution framework:**
For each geography, answer these unit economics questions:
- What is the payment method preference distribution?
- What conversion penalty does a card-only experience impose?
- Is that penalty larger than the operational cost of a local gateway?

**Market example:** Indonesia
- Bank transfers and e-wallets dominate online payments
- Card penetration is low
- Card-only checkout = significant conversion loss

---

### "When is a payment failure a PM problem vs. an engineering problem?"

> **Payment failure root cause:** The reflex is "engineering." The accurate answer is: **payment failures that follow predictable patterns are product problems.**

| Failure Type | Category | Examples | Requires |
|--------------|----------|----------|----------|
| **Infrastructure issues** | Engineering | Webhook delivery failure; SDK version incompatibility; SSL cert expiry | Technical fixes |
| **Behavioral patterns** | Product | High declines in low-card-penetration markets; abandonment after 3D Secure; mobile vs. desktop disparity | UX/product changes |

**Why the distinction matters:**
- **PM problems** require product interventions: add local payment methods, redesign 3D Secure interstitial, build mobile-specific error states
- Treating conversion drop as "engineering will investigate the gateway" delays the actual product fix

---

### "What does embedded finance and real-time payments change about payment infrastructure?"

#### Real-time payments

> **Real-time payment rails:** Instant, low-cost transaction networks (UPI in India, SEPA Instant in EU, FedNow in US)

**Scale impact:** UPI processes 13+ billion transactions per month at near-zero fees

**Business implication:** Per-transaction fee economics that justify traditional gateway selection are collapsing in markets with real-time rails

**Implementation choice:** BrightChamps could eliminate Razorpay fees on Indian transactions via direct NPCI integration or bank partnership — but this bypasses traditional gateways

---

#### Embedded finance

> **Embedded finance:** Financial products (credit, insurance, BNPL) offered at point of purchase rather than routing users to external providers

**Strategic question:** Does BrightChamps remain a **merchant** (route to gateways, no financial liability) or become a **payment facilitator** (hold float, manage credit risk)?

| Role | Revenue Opportunity | Requirements |
|------|-------------------|--------------|
| Merchant | Limited | Gateway integration only |
| Payment Facilitator | Significant | Regulatory approval, capital requirements, credit risk management |

⚠️ **Risk:** Embedded finance revenue is real, but regulatory and capital requirements are substantial. Regulatory liability varies by jurisdiction.