---
lesson: Transactions & ACID
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 02.01 — SQL vs NoSQL: transactions are the primary reason to choose SQL for financial and booking data
  - 01.05 — Idempotency: transactions prevent partial state within one operation; idempotency prevents processing the same operation twice
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/payments/payment-flow.md
  - technical-architecture/payments/credit-system-and-class-balance.md
profiles:
  foundation: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
  working: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
  strategic: Senior PM, Head of Product, AI-native PM
status: ready
last_qa: 2026-04-07
---

# ═══════════════════════════════════
# FOUNDATION
# For: Non-technical Business PM, Aspiring PM, Designer PM, MBA PM
# Assumes: nothing
# ═══════════════════════════════════

## F1. The student who paid but couldn't book

**The scenario:**
A student completed payment for a 30-class package. The gateway confirmed the charge and the payment system began updating the database.

**What should have happened:**
1. Mark the sale as paid
2. Add 30 credits to the student's profile
3. Update the student's class booking capacity

**What actually happened:**
Steps 1–2 completed. Then the database connection dropped before step 3 could finish.

---

**The customer experience:**
- Student logs in ✓ Payment confirmed
- Credit balance shows 30 classes ✓ Correct
- Attempts to schedule ✗ Error: "No available class balance"
- Calls support

**The support burden:**
Support had to audit three separate tables to reconstruct what did and didn't get written—because no single record showed the full payment state. They manually ran a database update to fix it.

---

> **Transaction:** A single unit that wraps multiple database operations together. If any one fails, all roll back to the pre-payment state. The payment gateway retries and all operations run again until they succeed.

**Why transactions solve this:**

| Without transaction | With transaction |
|---|---|
| Three separate updates run sequentially | All three updates run as one atomic unit |
| One fails → system stuck in partial state | One fails → all roll back → system stays clean |
| Support must audit multiple tables | System returns to known state automatically |
| Customer sees conflicting data | Customer experiences either full success or full retry |

---

**The implementation risk:**
The edtech platform's payment system *does* use transactions—the engineering team knew to include them. However, every new payment feature and every new table updated at checkout requires inclusion in the transaction boundary. Miss one addition, and the next database interruption produces another partial-state support ticket.

## F2. What it is — the all-or-nothing rule

> **Transaction:** A group of database operations that the database treats as a single unit. All succeed together — or none of them do.

### The core principle

Imagine splitting a restaurant bill. The waiter's system needs to:
1. Charge your card
2. Mark the table as paid
3. Update the day's revenue total

These three operations are linked. If your card is charged but the system crashes before marking the table as paid, you've been charged and the restaurant doesn't know it. If the revenue update fails, the day's numbers are wrong.

**Correct behavior:** Either all three complete, or the charge is reversed and you try again.

The restaurant system wraps those three operations in a single unit with one guarantee: **partial state never persists**.

---

### The ACID promises

Databases make four guarantees about transactions:

| Promise | What it means |
|---------|---------------|
| **Atomicity** | All operations in a transaction succeed, or all are rolled back. No partial state. If the payment callback updates two of three tables and then fails, the database reverts all two completed updates. |
| **Consistency** | The database moves from one valid state to another valid state. Rules the database enforces — like "total_credits can't go negative" or "a sale must have a valid student_id" — hold before and after every transaction. A transaction that would violate those rules is rejected. |
| **Isolation** | Concurrent transactions don't see each other's intermediate state. If two users are both completing payment at the same moment, each transaction sees the database as if it's the only operation running. One doesn't see the other's half-written updates. |
| **Durability** | Once a transaction commits, the data survives crashes. The database writes committed transactions to disk before confirming success. If the server loses power immediately after committing, the data is still there when it restarts. |

## F3. When you'll encounter this as a PM

### Payment feature touches multiple tables
Any checkout flow that updates more than one thing — a sale record, a credit balance, a booking capacity, a CRM deal — has transaction correctness requirements.

**PM question:** "Are all of these updates wrapped in a single transaction? What happens to users if one of them fails?"

### Post-incident report cites "partial state" or "data inconsistency"

Examples of partial-state failures:
- A student paid but has no credits
- An order is marked fulfilled but inventory wasn't decremented
- A booking was confirmed but the seat count wasn't updated

*What this reveals:* Multiple database updates were written without a transaction wrapper — or a transaction was open during an operation that was assumed to be atomic but wasn't.

### New feature adds a database update to an existing payment or booking flow

Every addition to a checkout flow raises a structural question: **Does this update belong inside the transaction or outside it?**

| Update type | Belongs inside transaction | Belongs in async queue |
|---|---|---|
| Updates consistent with payment outcome | ✓ Payment confirmation, inventory decrement, balance update | |
| Updates that can lag | | ✓ Welcome email, analytics event, CRM sync |

### Data team reports inconsistent counts between tables

> **Partial-state drift:** Credits granted ≠ payments confirmed, classes booked ≠ booking records created

*What this reveals:* Missing transaction boundaries or transaction failures that weren't fully retried. The payment system exists in three tables: `sale_payments`, `student_profile`, and `student_class_balance`. Without transaction coordination, any of the three can drift from the others.

### Engineering team mentions "isolation levels" or "locking"

> **Isolation level:** Database configuration for how concurrent transactions interact

**The tradeoff you need to know:**
- **Stricter isolation** → prevents data anomalies but reduces throughput
- **Relaxed isolation** → increases throughput but may allow reads of stale or inconsistent data

**For financial systems:** This tradeoff has a correct answer.

---

## PM decision framework

| Situation | Your role | Push back or defer? | What to require |
|---|---|---|---|
| New checkout feature adds a DB table update | Ask: "Is this inside the transaction?" | Push back if async — it must be inside if it's state that must be consistent with payment | Confirm in design review before sprint starts |
| Post-incident: "partial state" or "data inconsistency" | Identify which update was outside the transaction | Push back on fix that adds retry logic instead of a transaction boundary | Require transaction wrapper + test for the failure scenario |
| Engineer says "we'll handle it in the application" for concurrency | Ask: "What happens when two requests arrive at the same millisecond?" | Push back — application-level checks fail under concurrency without DB locking | Require a DB-level lock or an idempotency key, not just an in-memory check |
| New microservice writes financial data | Ask: "What isolation level, and how do we handle concurrent writes?" | Defer to eng on exact level — but require the question be answered before launch | READ COMMITTED at minimum; SERIALIZABLE for any balance check/deduct |
| Launch readiness for any payment feature | Review transaction scope and failure behavior | Defer to eng on implementation — your job is to ensure these questions are answered | All DB writes atomic, failure mode clean, concurrent payments load-tested |
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that a transaction groups database operations into an all-or-nothing unit; knows the four ACID properties.
# ═══════════════════════════════════

## W1. How transactions actually work — the mechanics that matter for PMs

### Quick Reference
- **Transaction = all-or-nothing:** Multiple database changes either all succeed or all revert
- **Isolation level = concurrency tradeoff:** Stricter isolation prevents race conditions but reduces throughput
- **Lock = how isolation works:** Shared locks allow concurrent reads; exclusive locks allow one writer only
- **Deadlock = circular wait:** Two transactions block each other; database kills one and rolls it back
- **Keep transactions short:** Only database operations inside; async work (emails, webhooks) happens after commit

---

### 1. What a transaction looks like in code

```sql
BEGIN;
  UPDATE sale_payments SET status = 'paid' WHERE id = :saleId;
  UPDATE student_profile SET total_credits = total_credits + 30 WHERE student_id = :studentId;
  UPDATE student_class_balance SET total_booked_class = total_booked_class + 30 WHERE student_id = :studentId;
COMMIT;
```

**On success:** All three UPDATEs execute, database commits the changes.

**On failure:** Application calls `ROLLBACK` instead. All three updates revert. The database returns to its pre-transaction state.

> **Transaction:** A sequence of database operations that either all succeed together (COMMIT) or all fail and revert together (ROLLBACK). Atomic — indivisible.

**In ORMs** (Sequelize, TypeORM, ActiveRecord): Transaction blocks auto-rollback on error. The principle remains the same regardless of syntax.

---

### 2. Isolation levels — the knob that controls concurrent transaction behavior

Isolation is the most nuanced ACID property. It answers: *What inconsistencies can occur when transactions run concurrently?*

| Isolation Level | What it prevents | Throughput impact | When to use |
|---|---|---|---|
| READ UNCOMMITTED | Nothing — can read in-progress (dirty) data from other transactions | Highest | **Never in production** |
| **READ COMMITTED** (PostgreSQL default) | Dirty reads: only sees committed data | High — ~5–10% overhead vs uncommitted | Most read/write operations |
| REPEATABLE READ | Dirty reads + non-repeatable reads: same row read twice returns same value | Medium — ~15–25% overhead vs READ COMMITTED | Read-then-act within same transaction on same rows |
| SERIALIZABLE | All anomalies including phantom rows: new rows inserted concurrently don't appear | Lowest — 2–10× throughput reduction under contention | Balance check → validate → deduct; any check-then-act on shared counters |

**The PM question that matters:**

Your checkout flow:
1. Reads the student's current credit balance
2. Validates it's sufficient
3. Deducts the cost

At READ COMMITTED, two concurrent payments can both read the same balance, both validate, and both succeed — when only one should.

At SERIALIZABLE, the second payment sees the first payment's deduction before reading. One fails validation. ✓

> **Race condition:** Two concurrent transactions read the same data, both make decisions based on that old data, and both execute writes. Result: inconsistent database state.

---

### 3. Locking — how isolation is enforced

Databases enforce isolation by locking rows. When a transaction reads or writes a row, it acquires a lock. Other transactions that want to write to that row must wait.

#### Two lock types

| Lock Type | Who can hold | Who blocks | Use case |
|---|---|---|---|
| **Shared lock (read lock)** | Multiple transactions simultaneously | Concurrent writes only | `SELECT` statements; allows parallel reads |
| **Exclusive lock (write lock)** | One transaction only | All reads and writes | `UPDATE`, `DELETE`; no other access until released |

**Lock duration = transaction duration.** An UPDATE inside a transaction that takes 30 seconds holds an exclusive lock on the updated rows for 30 seconds.

**Consequence under high concurrency:** Other transactions queue up waiting. Long queues → timeouts → errors.

---

### 4. Deadlocks — when two transactions wait for each other

> **Deadlock:** Transaction A waits for a lock held by Transaction B. Transaction B waits for a lock held by Transaction A. Neither can proceed. Database detects and kills one (the "victim"), rolling it back.

#### Classic deadlock in a payment system

**Transaction A (Payment 1):**
1. Lock student_profile → UPDATE
2. Wait for lock on student_class_balance

**Transaction B (Payment 2):**
1. Lock student_class_balance → UPDATE
2. Wait for lock on student_profile

A holds student_profile and waits. B holds student_class_balance and waits. Circular dependency. Deadlock.

#### Prevention: Lock ordering

**Always acquire locks in the same order across all transactions.** If every transaction that touches both tables locks student_profile first, then student_class_balance, the circular wait condition is impossible.

```
Transaction A: student_profile → student_class_balance ✓
Transaction B: student_profile → student_class_balance ✓
(Never: B locks student_class_balance first)
```

---

### 5. When NOT to use a transaction — async operations don't belong inside

⚠️ **Keep transactions as short as possible.** Every operation inside a transaction holds locks for its entire duration.

| Operation | Duration | Inside transaction? |
|---|---|---|
| Database UPDATE | 1–10 ms | ✓ Yes |
| Network call (payment gateway) | 100–500 ms | ✗ No |
| Email send | 500–2000 ms | ✗ No |
| Webhook delivery | 100–1000 ms | ✗ No |
| Queue publish (SQS) | 10–50 ms | ✗ No (usually) |

**Why?** Network operations are slow and fail for reasons unrelated to database state. Holding locks during a network call starves other transactions.

#### Correct payment flow pattern

1. **Inside transaction:** Update sale_payments, student_profile, student_class_balance → COMMIT
2. **After transaction:** Publish invoice generation to SQS, publish student onboarding to queue (both async)
3. **If invoice fails:** Retries from queue without affecting the committed payment

The payment is durable. The invoice generation is eventually consistent.

---

### 6. Optimistic vs pessimistic locking

Two strategies for handling concurrent access to the same row.

| Strategy | Lock timing | Throughput | Correctness | Best for |
|---|---|---|---|---|
| **Pessimistic** | Lock before reading (SELECT ... FOR UPDATE) | Low under contention | Guaranteed | High-contention counters (inventory) |
| **Optimistic** | Read without lock; check version on UPDATE | High under low contention | Correct if retries work | Infrequent updates (credit balance) |

#### Pessimistic locking

```sql
BEGIN;
  SELECT balance FROM student_profile WHERE student_id = :id FOR UPDATE;
  -- Row is locked. No other transaction can modify it.
  UPDATE student_profile SET total_credits = balance - 30 WHERE student_id = :id;
COMMIT;
```

**Pros:** No race conditions. The row is locked for the duration.

**Cons:** Reduces throughput when many transactions compete for the same rows. Other transactions wait.

#### Optimistic locking

```sql
BEGIN;
  SELECT balance, version FROM student_profile WHERE student_id = :id;
  -- No lock acquired.
  UPDATE student_profile 
    SET total_credits = balance - 30, version = version + 1 
    WHERE student_id = :id AND version = :oldVersion;
  -- If another transaction changed the version, UPDATE affects 0 rows.
COMMIT;

-- Application checks: affected_rows == 0? Retry.
```

**Pros:** No locks held during the read. High throughput under low contention.

**Cons:** Under high contention (many simultaneous updates to the same row), many retries occur.

#### When to use which

- **Student credit balance updated by payment webhooks (infrequent, batched) + class completions (frequent, distributed):** Optimistic with a `version` column
- **Inventory decremented by many concurrent checkout flows:** Pessimistic (prevent overselling)

---

### 7. Transaction scope in microservices — the distributed transaction problem

> **Database transaction:** Local to a single database. Cannot span multiple databases.

A payment flow spanning multiple services:
- Payment-Structure service writes to `payment_initiations` table
- Eklavya service writes to `student_profile` table
- Paathshala service writes to curriculum provisioning table

Each service has its own database. No single transaction can cover all three.

#### The problem

Each service can guarantee ACID within its own database. But cross-service consistency requires application-level patterns.

#### Solutions (each with tradeoffs)

| Pattern | How it works | Consistency | Complexity |
|---|---|---|---|
| **Saga (Choreography)** | Each service listens to the previous service's event and emits its own | Eventual consistency; compensating rollbacks on failure | Medium |
| **Saga (Orchestration)** | Central orchestrator coordinates the sequence of local transactions | Eventual consistency; explicit compensation steps | High |
| **Event sourcing** | Shared immutable event log; all services read and replay | Eventual consistency; strong audit trail | High |

These patterns sacrifice the clean atomicity of a single database transaction for the operational flexibility of service independence.

## W2. The decisions transactions force

### Quick reference
- **Transaction scope:** Database writes only; async operations go in queues
- **Isolation level:** READ COMMITTED by default; SERIALIZABLE for balance checks
- **Locking:** Pessimistic for high-contention rows (>5–10%); optimistic for low-contention

---

### Decision 1: What belongs inside the transaction vs outside it?

| | Inside the transaction | Outside the transaction (async) |
|---|---|---|
| Best for | Database updates that must be consistent with each other; state that must either all change or not change | Network calls, email sends, webhook deliveries, queue publishes, third-party API calls |
| Failure behavior | Any failure rolls back all updates in the transaction | Failure is retried independently; committed DB state is preserved |
| Latency impact | Must complete within transaction timeout (typically 30–60 seconds) | No constraint on latency |
| Lock duration | Rows locked for entire duration | No locks held after transaction commits |

**→ Default:** Only database writes with direct consistency dependencies should go inside. Everything else — async operations — belongs in queues after the transaction commits.

> **PM default:** If it's a network call or a side effect, it doesn't belong in the transaction. The transaction should contain only the database writes that must be atomically consistent with each other.

---

### Decision 2: Which isolation level?

| | READ COMMITTED | REPEATABLE READ | SERIALIZABLE |
|---|---|---|---|
| Best for | Most read/write operations where stale data for one read is acceptable | Operations that read data, then act on it within the same transaction | Financial balance checks: read balance → validate → deduct |
| Throughput | High — baseline | Medium — ~15–25% lower than READ COMMITTED | Low — 2–10× lower under high concurrency (e.g. 1,000 tps → 200–500 tps for heavily contended rows) |
| Anomaly risk | Non-repeatable reads (same row reads twice → different values) | Phantom rows (new rows inserted between reads match your query) | None |
| Deadlock risk | Low | Medium | High — serializable transactions abort and retry on conflict |

**→ Default:** READ COMMITTED for general operations. SERIALIZABLE for any flow that reads a balance, validates it, and deducts from it — where two concurrent operations must not both succeed on the same balance.

> **PM default:** READ COMMITTED for general operations. SERIALIZABLE for any flow that reads a balance, validates it, and deducts from it — where two concurrent operations must not both succeed on the same balance.

---

### Decision 3: Pessimistic or optimistic locking for concurrent row access?

| | Pessimistic locking | Optimistic locking |
|---|---|---|
| Best for | High-contention rows: inventory counters, ticket seats, shared appointment slots | Low-contention rows: user profiles, settings, records updated rarely or by one actor at a time |
| Contention threshold | Use when >5–10% of transactions compete for the same row; retry storm worse than lock wait | Use when <5% of transactions compete for the same row; conflicts rare |
| Lock held during | Entire read + write duration (typically 10–200ms per transaction) | Not held — version check on write only |
| Throughput | Lower under contention — each waiter adds the lock-hold duration (e.g. 50ms × 20 waiters = 1s queue) | Higher under low contention — no waiting, only ~1–2ms retry overhead on rare conflict |
| Failure mode | Waits and timeouts if lock held too long (>500ms typical timeout) | Retry on version conflict — can cause retry storms if contention unexpectedly spikes |

**→ Default:** Use pessimistic locking for counters that many concurrent operations decrement. Use optimistic locking for records with infrequent concurrent writes.

> **PM default:** Credit balances updated by concurrent payment webhooks for the same student are high-contention — pessimistic locking (`SELECT ... FOR UPDATE`) prevents double-addition. Student profiles updated only by their own actions are low-contention — optimistic locking is sufficient.

## W3. Questions to ask your engineer

| Question | What This Reveals | Correct Answer |
|----------|-------------------|-----------------|
| **Are all of the database updates in this checkout/booking flow wrapped in a single transaction?** | Whether partial state is possible. If the payment confirmation triggers updates to `sale_payments`, `student_profile`, and `student_class_balance`, all three should be inside one transaction. If any update is outside, a failure between them produces inconsistent data that requires manual correction. | "Yes, all three are in the same transaction block." |
| **What happens to the user if the transaction fails?** | Whether the failure mode is clean. A clean failure: transaction rolls back → database returns to pre-payment state → gateway retries webhook → transaction runs again. An unclean failure: "user needs to contact support" = partial state is possible. | Transaction rolls back cleanly and retries automatically. |
| **How long does this transaction stay open? What operations are inside it?** | Whether the transaction scope is appropriate. Transactions that include network calls (Zoho CRM, email service) hold locks while waiting for external systems. Slow external systems = extended lock duration = contention. | Network calls happen *after* the transaction commits, not inside it. |
| **Are there any places where two concurrent requests update the same row?** | Whether concurrency control is needed. Two payment webhooks for the same student (duplicate gateway delivery) could both increment `total_credits` without locking/idempotency, resulting in double credits. | Either a pessimistic lock prevents concurrent updates to the same student's credit row, OR an idempotency key prevents duplicate processing. |
| **What isolation level does this transaction use?** | Whether the isolation level matches the operation's consistency requirements. READ COMMITTED allows another transaction to modify the balance between the read and deduct — deduction based on stale value. SERIALIZABLE prevents this. | "READ COMMITTED for most operations, SERIALIZABLE for the balance check/deduct flow." |
| **What's the rollback behavior if a downstream service call fails after the transaction commits?** | Whether there's a compensating action for downstream failures. If credits are added and sale marked paid, but SQS queue publish fails, the invoice won't generate. | SQS publishes *after* the commit, with retry logic and dead-letter queue. Committed database state is source of truth; downstream actions are eventually consistent. |
| **Have we tested concurrent payments for the same student under load?** | Whether concurrency edge cases were validated. Two concurrent payments for the same student can both trigger the same credit top-up transaction. Without appropriate locking, both read the same credit value and both add to it — incorrect final balance. | Concurrent payment scenarios are in the load test plan, not discovered as post-launch bugs. |

## W4. Real product examples

### Live class platform — atomic post-payment updates across three tables

**What:** Payment confirmation flow wraps three database updates in a single transaction:
- Mark sale as paid in `sale_payments`
- Add package credits to `student_profile.total_credits`
- Increment booking capacity in `student_class_balance.total_booked_class`

All three execute as one atomic unit in the `/payment-callback` webhook handler.

**Why it matters:** The three tables represent different aspects of the same business fact: a student completed a payment and is owed classes. If any one update fails, the other two should not persist.

| Risk | Impact |
|------|--------|
| Student appears paid but has no booking capacity | Creates support case |
| Student has booking capacity without paid sale record | Unbilled entitlement |

The transaction boundary ensures these states never diverge.

⚠️ **What's still at risk:** The platform has no idempotency guard on the webhook handler. If the payment gateway delivers the same webhook twice (common under network retries), both deliveries run the transaction — and the student gets double credits. The transaction protects against partial state within one payment. It doesn't protect against processing the same payment twice. That requires a separate idempotency check (verify whether this `transaction_id` has already been processed) before the transaction begins.

**PM takeaway:** A transaction is necessary but not sufficient for payment correctness.
- Transaction handles: "partial failure" problem
- Idempotency key handles: "duplicate processing" problem
- **Both are required**

---

### Live class platform — weak isolation in the credit deduction flow

**What:** After class completion, teacher feedback triggers a Lambda chain:
```
teacher feedback → SNS → Lambda → PATCH API → 
UPDATE student_class_balances.total_class_paid
UPDATE student_profiles.credits_consumed
```

**The problem:** Lambda chain introduces latency between class completion and credit deduction. During that window, a student's booking capacity shows credits available that have actually been consumed. A student completing their last class could schedule another class in the gap between completion and credit deduction.

> **Eventual Consistency:** Data will reach a correct state eventually, but not immediately. A few seconds of staleness is acceptable for most operations, but problematic for reads that gate access.

**Why this matters:** This is the practical consequence of relaxed isolation in an async system. For most operations, eventual consistency is acceptable. For read-then-act patterns where the read gates access (check available credits before allowing scheduling), the gap matters.

| Approach | Tradeoff |
|----------|----------|
| Eventual consistency | Allows over-scheduling during lag window |
| Strong consistency | Prevents overselling, higher latency per class completion |

**PM takeaway:** Eventual consistency is a deliberate choice, not a default. For any read-then-act pattern where the read gates access, ask: does the data freshness guarantee match the business requirement?

---

### Stripe — the ledger model as the gold standard for financial transactions

**What:** Stripe's internal financial model never updates a balance in place. Every financial event creates new ledger entries. A payment creates two entries: debit the cardholder's account, credit Stripe's account. A refund creates two more. The current balance is derived by summing the ledger, not by reading a single balance column. All ledger entries are written atomically in a single transaction.

**Why it works:**

| Model | Vulnerability |
|-------|---|
| Balance column (direct UPDATE) | Corrupted by concurrent writes, partial failures, retrospective adjustments |
| Append-only ledger | No UPDATE conflicts, fully auditable, always recoverable |

An append-only ledger is:
- **Append-only:** no UPDATE conflicts
- **Auditable:** full history is permanent
- **Recoverable:** any current state can be recomputed from full history

The transaction boundary covers ledger insertion — if either entry fails to write, neither does. The balance is always correct by definition: it's the sum of all ledger entries.

**PM takeaway:** For any financial feature — credits, currency balances, subscription states — consider whether the correct model is:
- **Update a counter:** fast, fragile at scale
- **Append to a ledger:** slower to query, but correct and auditable

Stripe chose the ledger. The KB roadmap has "Event-driven credit ledger: replace direct UPDATE with INSERT-only ledger table" as a Month 1 architectural item — for the same reasons.

---

### Shopify — two-phase inventory reservation to prevent overselling

**What:** When a customer adds an item to cart and begins checkout, Shopify creates a reservation record: hold 1 unit of this SKU for this checkout session for N minutes. This reservation is a separate record from the final inventory decrement. The two-phase design — reserve first, confirm on payment — prevents two simultaneous checkouts from both believing inventory is available and both completing.

**Why it matters:** 

**Naive approach (read → deduct):**
- Checkout 1 reads "1 unit available" → succeeds
- Checkout 2 reads "1 unit available" → succeeds
- Result: overselling

**Shopify's reservation approach:**
- Atomically check availability AND create reservation row
- If reservation already exists for this SKU, return "out of stock"
- Payment confirmation atomically converts reservation to permanent inventory decrement

> **Two-Phase Pattern:** Reservation (atomic check + hold) → Confirmation (atomic conversion to final state)

**PM takeaway:** For any resource that can be exhausted — inventory, appointment slots, class seats — use reservation → confirmation, not read → deduct. The reservation is the transaction boundary. The confirmation converts it. This prevents overselling without serializing all operations through a single lock on the resource counter.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands ACID properties, isolation levels, locking, and the distributed transaction problem.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### The long transaction that becomes a production outage

**What happens:**
A single long-running transaction holds exclusive locks on rows for its entire duration. In a payment system, a Puppeteer invoice generation step (CPU-heavy, 3–8 seconds) holds locks on `sale_payments` and `student_profile` rows for that entire duration.

| Traffic Level | Observable Impact |
|---|---|
| Low payment volume | Invisible — locks resolve quickly |
| 100 concurrent webhooks | 800 seconds of cumulative lock wait time → transaction timeout cascade → all webhooks after the first return 500 → payment gateway retry storm |

**Why this happens:**
"Invoice generation is inside the transaction" is a design decision with production consequences. It only surfaces when concurrency makes lock contention real.

**PM prevention role:**
- Transaction scope is a **product requirement**, not an implementation detail
- The correct design (transaction commits first, invoice generation runs asynchronously via SQS) is a **PM-level architecture discussion before the feature ships**
- This conversation belongs in sprint planning, not in post-incident root cause analysis

---

### Phantom reads in financial operations

**What happens:**
READ COMMITTED allows phantom reads: a transaction reads "student has 0 credits remaining," another transaction concurrently adds credits, the first transaction reads again and sees the new credits.

> **Phantom read:** A transaction reads the same row twice and gets different results due to concurrent modifications from another transaction.

**In a read-then-deduct flow:**
Two concurrent operations both read a sufficient balance and both succeed — **double-consuming credits that only exist once**.

| Isolation Level | Behavior | Risk |
|---|---|---|
| READ COMMITTED (default) | Allows phantom reads | ⚠️ Race condition in balance gates |
| SERIALIZABLE | Prevents phantom reads | Correct for financial operations |

**Why this happens:**
This is not a bug in the code; it's a consequence of isolation level choice. It appears at scale when concurrent operations become frequent, not when sequential processing hides the race condition.

**PM prevention role:**
- "What isolation level does this transaction use?" is a **sprint review question**, not an advanced DBA concern
- Financial operations that read-then-act require explicit isolation level specification
- This conversation belongs in sprint planning, before the feature is deployed to a transaction volume that makes the race condition observable

---

### The "let the application handle it" trap

**What happens:**
Teams using MongoDB or Redis for speed build application-level consistency logic:

```
read balance → check in memory → write back if sufficient
```

This logic is **correct when requests are sequential**. It **breaks under concurrency**.

| Scenario | Result |
|---|---|
| Sequential requests | Works as intended |
| Two concurrent requests | Both pass the in-memory check → both write back an updated balance → second write **overwrites** the first instead of accumulating |

**Why this happens:**
The application is doing exactly what it was told. The concurrency model is wrong.

⚠️ **Fixing this later requires architectural changes:**
- Moving to SQL, OR
- Implementing distributed locking (Redis SETNX or similar)
- Both changes made under production pressure

**PM prevention role:**
When a new service handles financial counters, ask these questions in the technical design review:

1. **Database choice:** What system is handling this?
2. **Locking strategy:** "How does this handle concurrent writes to the same balance?"
3. **If the answer is "the application handles it":** Ask what happens when two requests arrive simultaneously

---

## S2. How this connects to the bigger system

### SQL vs NoSQL (02.01)

| Aspect | SQL | NoSQL (MongoDB 4.0+) |
|--------|-----|----------------------|
| Transaction model | Native ACID | Added multi-document support |
| Performance overhead | Baseline | Higher |
| Failure behavior | Consistent | Subtle differences |
| Use case fit | Financial data ✓ | Flexibility-first systems |

> **Why it matters:** For payment and booking systems, SQL's transaction model is the standard choice—correctness trumps flexibility.

---

### Idempotency (01.05)

These solve **adjacent problems:**

| Problem | Solution | Scope |
|---------|----------|-------|
| Partial state within one execution | Transaction | Single execution |
| Duplicate state from retries | Idempotency key | Multiple executions |

**Real scenario — Payment callback processing:**
- ✓ Transaction rolls back failed callback cleanly
- ✓ Idempotency check prevents double-processing on retry
- ⚠️ Transaction alone is insufficient

> **Current risk:** HIGH severity debt—no idempotency guard on webhook processing means the transaction cannot guarantee payment correctness alone.

---

### Indexing (02.02)

**Missing index consequences:**

```
Query without index on student_id
├─ Should lock: 1 row
└─ Actually locks: Full table scan result (~thousands of rows)
    └─ Creates contention between payments for different students
```

> **Lock scope expansion:** Row-level locking acquires locks on rows returned by the query. Without an index, the database locks all rows in the scan path—not just the target row.

**Impact under concurrency:** Multiple payments competing for locks on the same large table scan multiplies contention.

---

### Caching (02.04)

**Two cache use cases with opposite correctness requirements:**

| Context | Data freshness | Risk if stale | Design choice |
|---------|-----------------|----------------|---------------|
| Credit balance display | Slightly old OK | Low—UX delay | Cache reads |
| Credit balance gate (can student schedule?) | Must be current | **HIGH**—false denial | Read from database |

> **Cache limitation:** Caches are not participants in database transactions. When a transaction commits to `student_profile.total_credits`, the cache holds the pre-update value until expiration or explicit invalidation.

**Rule:** Cache for reads. Always read from the database for gates.

## S3. What senior PMs debate

### Saga pattern vs. two-phase commit: which compromise is worse?

| Approach | How it works | Strengths | Weaknesses |
|----------|-------------|----------|-----------|
| **Two-phase commit (2PC)** | Coordinator orchestrates a single ACID transaction across multiple databases | Correct; centralizes complexity | Slow (coordinator round trip); fragile (coordinator failure locks all participants); operationally complex |
| **Saga pattern** | Sequence of local ACID transactions with compensating transactions to undo failed steps | Eventually consistent; observable; operationally simpler | Requires every team to implement compensating transactions; hard to test under real failure scenarios |

> **Saga:** A sequence of local ACID transactions across services, where each step can be undone by a compensating transaction if a later step fails.

**Example flow:**
1. Reserve credits
2. Confirm payment
3. Provision curriculum
   - *If step 3 fails:* reverse payment, release credits

**The actual debate:** Neither is obviously better. 2PC centralizes complexity in the coordinator; sagas distribute it to every team. Both are tradeoffs against a problem (cross-service consistency) that local SQL transactions don't have.

---

### Event sourcing: audit trail insurance or engineering overhead?

| Model | Storage | Read cost | Audit trail | Consistency |
|-------|---------|-----------|-------------|-------------|
| **Direct UPDATE** | Current state only (balance column) | Fast; single row lookup | None; history is lost | Vulnerable to UPDATE conflicts |
| **Event sourcing** | INSERT-only ledger (every credit add/deduction) | Expensive without careful indexing; requires aggregation across millions of events | Complete; every change has a reason | Correct by construction |

> **Event sourcing:** Store every event (credit additions/deductions) instead of current state. Derive current state by replaying events or summing the ledger.

**The tradeoff depends on scale:**
- **Hundreds of payments/day (startup):** Direct UPDATEs are correct and simple
- **Millions of payments/day (platform):** Ledger model's correctness properties justify read-layer complexity

> **Key discovery:** Teams implementing event sourcing learn that the read layer requires as much engineering investment as the write layer.

---

### AI is reshaping the read layer, not the write layer

⚠️ **Common PM misunderstanding:** AI features don't change the transactional write model.

**What's actually happening:**

| Layer | Handles | Technology | Change needed? |
|-------|---------|-----------|-----------------|
| **Write layer** | Payment confirmations, credit updates, booking records | SQL, ACID, strongly consistent | No |
| **Read layer (new)** | Semantic queries, vector similarity searches, real-time inference | Indexed data optimized for query pattern | Yes |

**LLM-powered features create new read requirements:**
- Semantic queries ("which students showed declining engagement over 90 days?")
- Vector similarity searches over content embeddings
- Real-time inference over streaming events

**What this means for PMs:** You don't re-examine the payment transaction model when building AI features. You ensure the data written by those transactions is surfaced through a read layer optimized for your AI feature's query pattern — not served directly from the transactional database.