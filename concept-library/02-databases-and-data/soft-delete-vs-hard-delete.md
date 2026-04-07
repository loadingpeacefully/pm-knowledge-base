---
lesson: Soft Delete vs Hard Delete
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 02.07 — Schema Design Basics: soft delete is a schema design choice — adding deleted_at to tables; understanding migrations and constraints required
  - 02.03 — Transactions & ACID: soft delete and audit ledgers depend on atomic writes; understanding transaction scope clarifies where data integrity is guaranteed
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/api-specifications/api-student-details-get.md
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

## F1. The credit that vanished and the account that couldn't be restored

Two stories about what happens when engineers make deletion decisions without PM input — and what it costs to fix them later.

### Story 1: The Missing Credit

**The Problem:**
A parent contacts BrightChamps support: their child was marked as having completed a class last Tuesday, but the class was cancelled by the teacher at the last minute. The student's class balance should show 15 remaining classes. It shows 14. Somewhere in the system, a credit was deducted that shouldn't have been.

**What the data revealed:**
- `credits_consumed: 26` (should be 25)
- `total_class_paid: 26` (should be 25)
- **No history available** — the system stores only current totals

**The cost of investigation:**
- Cross-reference every class completion timestamp against Lambda trigger logs
- **2 hours of engineering time**
- Manual database UPDATE with no audit trail or undo capability

**The missed opportunity:**
The optimization roadmap explicitly flagged this gap:

> **Event-driven credit ledger:** Replace direct UPDATE with INSERT-only ledger table for full credit history

Instead of updating a counter, every credit change would create a new row:

| Operation | Current Approach | Ledger Approach |
|-----------|------------------|-----------------|
| Earn credit | `UPDATE counter +1` | `INSERT row (amount: +1, reason: 'class_completed')` |
| Deduct credit | `UPDATE counter -1` | `INSERT row (amount: -1, reason: 'class_used')` |
| Reverse error | Manual SQL + 2 hours | `INSERT row (amount: +1, reason: 'teacher_error_reversal')` |
| Audit trail | ❌ None | ✅ Full history preserved |
| Undo capability | ❌ Manual intervention | ✅ Automatic |

---

### Story 2: The Unrecoverable Account

**The Problem:**
A school district signs an enterprise contract. Three months later, they request a full data export under GDPR Article 20 (right to data portability) before migrating to a competitor's platform.

**What happened:**
The platform physically deleted several student records when parents closed their accounts — the standard "delete account" button triggered a hard `DELETE` on the student row.

**The cascade of data loss:**

```
Student deleted
    ↓
Payment history: GONE
    ↓
Class history: GONE
    ↓
Credit transfer history: BROKEN
    (foreign keys pointing at non-existent student IDs)
    ↓
Export INCOMPLETE
    ↓
District legal team: NOTICE SENT
```

⚠️ **Compliance Risk:** Hard deletion at schema design time violates data portability requirements and creates legal exposure under GDPR, CCPA, and similar regulations.

---

### What This Reveals

Both stories share a root cause: **deletion strategy is a product decision, not just a technical one.**

The decision about how data gets deleted — whether via hard DELETE, soft deletion (marking inactive), ledger tables, or retention-first design — is made at schema design time, usually **without a product manager in the room**. It determines:

- Whether data can be recovered
- Whether errors can be audited
- Whether accounts can be exported
- Whether compliance obligations can be met
- Whether user trust can be preserved

## F2. What it is — the trash can vs the shredder

When data is "deleted" in a software product, two fundamentally different things can happen—and the difference is invisible to users but critical to the product.

### Side-by-side: Hard delete vs. soft delete

| **Hard delete** (the shredder) | **Soft delete** (the trash can) |
|---|---|
| Row physically removed from database | Row remains in database with deletion flag |
| Example: `DELETE FROM students WHERE id = 456` | Example: `UPDATE students SET deleted_at = NOW() WHERE id = 456` |
| Storage is reclaimed immediately | Storage remains allocated |
| **Cannot be undone** without a backup | Can be restored by clearing the flag |
| Breaks references from other tables (payments, bookings, class records point to non-existent row) | References remain valid and intact |
| Audit trail of deletion may be lost | Complete history preserved in database |

### The filing cabinet analogy

**Hard delete** = Shredding the document. Gone permanently.

**Soft delete** = Moving the document to a locked drawer labeled "deleted." Still exists, still referenceable, but hidden from daily operations.

---

### Key terms

> **Hard delete**
> Physical removal via `DELETE FROM table WHERE id = X`. Row is gone permanently. Cannot be restored without a database backup.

> **Soft delete**
> Logical removal via a `deleted_at` timestamp (or `is_deleted` boolean). Row stays in the database. All queries that show "live" data filter with `WHERE deleted_at IS NULL`.

> **Audit log**
> A separate table recording every change to data: who changed it, when, what the previous value was, what it is now. Exists independently of whether the main table uses soft or hard delete.

> **Data retention**
> Policy governing how long data is kept before permanent deletion. GDPR mandates personal data not be kept longer than necessary. Many companies use soft delete as a staging step: data is soft-deleted immediately (invisible to users), then hard-deleted after a retention period (e.g., 90 days) if no recovery is requested.

## F3. When you'll encounter this as a PM

### Undo requests from users
"The teacher accidentally marked the class complete." "The admin deleted the wrong booking." "The student cancelled their subscription but now wants to reactivate with their history intact."

**The critical difference:** If data was hard-deleted, there is no undo. If it was soft-deleted, the restore is one SQL update.

⚠️ **Risk:** PMs who design "delete" flows without specifying the deletion strategy are implicitly choosing hard delete — the developer default when no requirement is stated.

---

### Regulatory compliance requests

| Right | Requirement | Soft Delete Solution |
|-------|-------------|----------------------|
| **Right to erasure** (GDPR) | Delete personal data on request | Soft-delete for the user (logically deleted) |
| **Right to data portability** (GDPR) | Export all data before deletion | Export on request before permanent removal |
| **Right of access** (GDPR) | Show what data you hold | Retain records during access period |

**How compliant products resolve the tension:** Data is soft-deleted for the user, then exported on request, then anonymized after the retention window instead of hard-deleted. Financial records must be kept for 7 years regardless of GDPR erasure requests.

---

### Finance and support reconciliation

**Scenario:** "Show me all payments for this student, including payments linked to cancelled bookings."

**Hard delete problem:** Bookings are deleted when cancelled → payment records reference bookings that no longer exist → reconciliation query returns incomplete data.

⚠️ **Rule:** Every product with financial transactions should soft-delete or archive related records — not hard-delete them.

---

### Enterprise procurement questionnaires

**Question asked during RFP:** "Can you show who deleted this record and why?"

| Strategy | Answer |
|----------|--------|
| Hard delete, no audit log | "No" |
| Soft delete only | "We can show when it was deleted" |
| Soft delete + audit log table | "We can show who deleted it, when, and what the value was before deletion" |

⚠️ **Timing:** This is a schema decision made long before the RFP arrives.

---

### Ghost data from incomplete soft-delete implementation

**The cost of soft delete:** Every query that fetches live data must add `WHERE deleted_at IS NULL`.

**When discipline breaks down:**
- Miss this filter in one query
- Deleted records appear in dashboards, exports, or API responses
- "Why is this deactivated student showing up in the teacher's class list?" 
- Answer: the class assignment query forgot the soft-delete filter

⚠️ **Ongoing technical burden:** Every developer touching that table must remember the filter. This is not a one-time schema cost—it's a maintenance requirement for the life of the table.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands soft delete as a deleted_at flag, hard delete as physical removal, and the basic compliance/undo implications.
# ═══════════════════════════════════

## W1. How soft and hard delete actually work — the mechanics that matter for PMs

**Quick Reference**
| Pattern | Mechanism | Key PM Implication |
|---------|-----------|-------------------|
| **Soft delete** | Add `deleted_at` timestamp; filter in queries | Data recoverable; requires discipline across all queries |
| **Hard delete** | `DELETE` statement removes row permanently | Irreversible; breaks referential integrity; loses analytics history |
| **Append-only ledger** | Every change is a new INSERT; never UPDATE/DELETE | Full audit trail by design; immutable history |
| **Anonymization** | Soft delete + scrub PII + delayed hard delete | GDPR-compliant; preserves financial records |

---

### 1. The soft delete pattern in practice

> **Soft delete:** Marking a row as deleted (via timestamp) while keeping it in the database. Live data queries filter out marked rows.

**How it works:**
- Add `deleted_at TIMESTAMP NULL` column — null = active; timestamp = deleted at that time
- Optional: `deleted_by INTEGER` — tracks who triggered the deletion
- Every live-data query includes `WHERE deleted_at IS NULL`
- Enforcement happens via: individual queries, ORM default scopes, or database views

**Real-world signal:** The student details API returns `active: true`. This is soft delete at the API layer:
- `active: false` students still exist in the database
- Payment history is retained
- Credit transfer records remain intact
- API simply filters them from normal responses

---

### 2. Hard delete — when data is actually gone

> **Hard delete:** Permanently removing a row via `DELETE` statement. The row is gone; recovery requires database backups.

**Three immediate consequences:**

⚠️ **Referential integrity breaks**
If foreign keys exist, rows in other tables now point to non-existent data. The database enforces one of three outcomes:
- `RESTRICT` — blocks the delete entirely (must delete dependent rows first)
- `CASCADE` — automatically deletes all dependent rows
- `SET NULL` — leaves dependent rows but clears their foreign key reference

Each has product impact: CASCADE erases payment records when a student is deleted; RESTRICT prevents deletion; SET NULL orphans records.

⚠️ **Backups become your only recovery path**
- Engineer must access production database
- Restore from most recent backup
- Extract and reinsert specific rows
- Takes hours and may restore stale data
- Requires high-privilege access

⚠️ **Analytics queries lose historical cohorts**
Example: "What was Q3 2024 conversion rate?" If churned students are hard-deleted, they disappear from the Q3 cohort. The conversion rate inflates because the denominator is missing deleted users.

---

### 3. The credit ledger — soft delete's more powerful cousin

> **Append-only ledger:** A table where rows are never updated or deleted—every change is a new INSERT. History is immutable by design.

**Current BrightChamps approach:** Two counters (`total_credits`, `credits_consumed`) updated via `UPDATE` statements.

**Proposed ledger table:**
```
credit_ledger:
- id: auto-increment
- student_id: FK to students
- amount: INTEGER (positive = earned; negative = consumed)
- event_type: ENUM('payment', 'class_completed', 'transfer_in', 'transfer_out', 'error_reversal', 'admin_adjustment')
- reference_id: links to payment_id or class_id
- created_at: TIMESTAMP
- created_by: system or admin user ID
```

**How it changes operations:**
- **Check balance:** `SELECT SUM(amount) FROM credit_ledger WHERE student_id = X`
- **Fix a wrong deduction:** `INSERT` a new `error_reversal` row with `+1` amount — the incorrect deduction remains visible history, the correction is transparent
- **No UPDATE, no DELETE** — full audit trail by design
- **Immutable history** — can't rewrite what happened

*What this reveals:* This is the principle behind financial ledgers, event sourcing, and blockchain. Append-only records are inherently auditable because the past can't be changed.

---

### 4. Query implications — the hidden cost of soft delete

Soft delete shifts complexity from deletion to retrieval. Every table with `deleted_at` requires developers to remember the filter everywhere.

| Query context | With soft delete | Without (hard delete) |
|---|---|---|
| Show live students | `WHERE deleted_at IS NULL` — must be added to every query | No filter needed |
| Show deleted students (admin audit) | `WHERE deleted_at IS NOT NULL` | Not possible; requires backup restore |
| Count all-time signups | `SELECT COUNT(*) FROM students` — includes deleted users | `SELECT COUNT(*)` — undercount; missing churned users |
| Analytics cohorts | Full historical cohort available | Cohort incomplete; churned users missing |
| Storage footprint | Grows indefinitely; deleted rows remain | Storage reclaimed on delete |

**The missed filter problem is the most common soft delete bug:**
- New endpoint built
- Developer forgets `WHERE deleted_at IS NULL`
- Deleted records start appearing in reports or API responses
- At scale, this breaks trust in data

**Two solutions:**
1. **ORM default scope** — filter automatically appended to all queries on the table; explicit override needed to see deleted records
2. **Archive table** — move deleted rows to a separate table, keeping main table clean

---

### 5. Cascade behavior — what happens to related records

When a student row is deleted, what happens to dependent rows?

| Related table | Hard delete + CASCADE | Hard delete + RESTRICT | Soft delete |
|---|---|---|---|
| `bookings` (student_id FK) | Booking rows automatically deleted | Delete blocked; must delete bookings first | Bookings stay intact; soft-deleted student is hidden from UI |
| `sale_payments` (student_id FK) | Payment rows deleted — **audit trail destroyed** | Delete blocked; can't delete students with payments | Payments remain; reference valid student row |
| `credit_ledger` (student_id FK) | **All credit history erased** | Delete blocked | **Full credit history preserved** |
| `student_credit_transfers` (student_id FK) | Transfer history deleted — **reconciliation broken** | Delete blocked | Transfer history intact |

**For any product with financial data:** Soft delete the student row + RESTRICT or SET NULL on payment-related foreign keys. This prevents accidental data loss. Hard deletion of a student with payments must require explicit admin override with a logged reason.

---

### 6. Anonymization — the GDPR-compliant middle path

⚠️ **Regulatory conflict:**
- GDPR: Personal data must be deleted on request
- Financial regulations: Transaction records must be kept for 7 years
- **These conflict if transactions contain personal identifiers**

**Resolution: Anonymize instead of hard-delete**

**When a student requests erasure:**

1. **Immediate soft delete** — user can't log in; data hidden from UI
2. **Scrub PII** — `UPDATE students SET name='[deleted]', email=NULL, phone=NULL WHERE id = X`
   - Row exists but contains no identifiable data
3. **Preserve financial links** — `student_id` foreign keys remain intact
   - Payments reference anonymized row
   - Financial integrity preserved
4. **Delayed hard delete** — after retention window (90 days or 7 years for financial records), hard delete if no legal hold

⚠️ **Schema design requirement:** The student row must allow nullable PII columns (`name VARCHAR NULL`, not `NOT NULL`). This decision must be made at design time.

## W2. The decisions soft vs hard delete forces

### Quick Reference
- **Soft delete default:** Financial history, user content, audit requirements, recoverable data
- **Hard delete default:** Session tokens, temp caches, log entries, transient data
- **Enforcement:** Use ORM default scopes to prevent missed filters

---

### Decision 1: Default to soft delete or hard delete for user-facing "delete" actions?

> **PM default:** Default to soft delete for any entity that has financial history, user-generated content, audit requirements, or that could reasonably need to be recovered. Hard delete is appropriate for transient data (session tokens, temporary caches, log entries past retention) or data with no downstream references.

| Dimension | Soft Delete | Hard Delete |
|---|---|---|
| **Recovery** | One SQL update — instant | Database restore — hours |
| **Audit trail** | Deletion timestamp + who deleted preserved | No record of deletion |
| **Query complexity** | Every query needs `WHERE deleted_at IS NULL` | No filter needed |
| **Storage cost** | Grows until explicit cleanup | Reclaimed immediately |
| **Compliance** | Easier — data exists for export requests | Harder — data gone permanently |
| **When to use** | Users, payments, bookings, content, credit records | Sessions, temp files, log entries, rate limit counters |

---

### Decision 2: Soft delete + retention period, or archive table?

> **PM default:** Use a retention period (soft delete → anonymize → hard delete after N days) for user-facing entities with PII. Use a separate archive table for high-volume operational data where storage cost matters and the main table's performance must be preserved.

| Dimension | Soft Delete + Retention Cleanup | Archive Table (Move Rows) |
|---|---|---|
| **Main table size** | Grows with deleted rows — may affect query performance at scale | Stays lean — only active rows |
| **Archive access** | All in one table, filter by `deleted_at` | Separate table, explicit archive query |
| **Restore capability** | Update `deleted_at` to NULL | Re-insert from archive table |
| **Implementation complexity** | Requires cleanup job on schedule | Requires move-on-delete logic |
| **When to use** | User records, financial records (moderate volume) | High-volume event tables, large operational tables |

---

### Decision 3: Where to enforce the soft-delete filter — query vs ORM vs database?

> **PM default:** Push for ORM-level default scopes for tables with soft delete. Application-level filtering (every developer adds the WHERE clause) is error-prone and guarantees a missed filter within 12 months. Database views (a "live_students" view that filters deleted rows) are the strongest enforcement but add deployment complexity.

| Dimension | Per-Query Filter | ORM Default Scope | Database View |
|---|---|---|---|
| **Missed filter risk** | High — requires discipline across all developers | Low — automatic, explicit override required | Lowest — database enforces |
| **Performance** | Same as ORM scope | Equivalent | Slight overhead — additional abstraction |
| **Seeing deleted records** | Standard query | Requires explicit `.withDeleted()` or equivalent | Query the underlying table directly |
| **Recommendation** | ⚠️ Never — too risky at scale | ✅ Recommended for most stacks | ✅ Best for high-compliance environments |

## W3. Questions to ask your engineer

| Question | What this reveals | Right answer | Red flag |
|----------|------------------|--------------|----------|
| **When a user "deletes" their account, is the row hard-deleted or soft-deleted?** | Whether deleted user data can be recovered, exported under GDPR, or referenced by existing financial records | Soft delete — set `deleted_at` on the student row. PII anonymized on request. Financial records preserved. | Hard delete without audit trail or recovery mechanism |
| **Does every query on this table filter out soft-deleted rows? How is that enforced?** | Whether ghost data bugs are a risk | "Yes, our ORM applies a default scope" | "We add `WHERE deleted_at IS NULL` in each query" — will be missed |
| **If we delete a student row, what happens to their payment records and booking history?** | Whether foreign key cascade behavior is defined and intentional | "Payments are RESTRICT — we can't delete a student with payments without an explicit admin override" | "I'm not sure" — signals financial data integrity at risk |
| **Is there an audit log for who deleted this record and why?** | Whether compliance and support requirements can be met | "Yes — all deletes log the requesting user, timestamp, and reason to an audit log table" | No audit trail for deletion events |
| **How do we handle the right-to-erasure request under GDPR?** | Whether the product has a compliant deletion pipeline | Soft delete immediately → anonymize PII columns → hard delete or retain anonymized row after retention window | "We delete the row" without anonymization or audit trail |
| **Can deleted records be restored, and how long does that take?** | Whether customer support can recover from user error | "Soft delete — restore takes seconds, any support agent with admin access can do it" | Recovery requires database restore from backup |
| **For the credit/balance system, is it a running total or a ledger?** | Whether credit errors can be investigated and reversed without manual database surgery | "Ledger — every credit event is an immutable INSERT. Corrections add a new row. Full history always available." | Running counter system — credit disputes slow to resolve |

---

⚠️ **Compliance & Financial Risk:** Questions 1, 4, and 5 are non-negotiable for any product handling payments or personal data. "I'm not sure" answers warrant immediate escalation to your data/security lead.

⚠️ **Data Integrity Risk:** If soft-deletes aren't enforced at the ORM level (Question 2), ghost data bugs become a matter of when, not if.

## W4. Real product examples

### BrightChamps — the credit counter that can't be audited

**The system:**
- Uses `total_credits`, `credits_consumed`, `total_booked_class`, `total_class_paid` as running counters across two tables
- Event flow: teacher feedback → SNS → Lambda → `PATCH /eklavya/v2/student-class-balance` → `UPDATE total_class_paid = total_class_paid + 1`

**The gap:**

| Problem | Impact | Current Resolution |
|---------|--------|-------------------|
| No record of which class completion triggered which increment | Credit disputes unsolvable via query | Manual cross-reference of timestamp logs across systems |
| `student_credit_transfers` table requires manual audit | Support can't self-serve | 2+ engineer hours per incident |
| Wrong deductions, failed payments still credited, transfers to wrong student | Customer trust erosion | Production DB access + manual verification |

**What the ledger solves:**

> **Append-only ledger model:** Every credit change is an INSERT (never an UPDATE). Current balance is derived by summing the ledger.

Dispute resolution becomes queryable:
```
SELECT * FROM credit_ledger WHERE student_id = X ORDER BY created_at DESC
```

Find erroneous row → insert correction row. No manual database surgery required.

**Cost comparison:**

| Approach | Per-incident cost | Monthly cost (10 disputes) | Root cause |
|----------|-------------------|---------------------------|-----------|
| Current (counter model) | 2+ engineer-hours | 20+ engineer-hours | Counters destroy audit trail |
| Proposed (ledger model) | ~5 minutes querying | Eliminated | Ledger is self-auditing |
| One-time build cost | — | 1 sprint | Create table, update Lambda, expose API |

**PM takeaway:** Running counters are simpler to implement than ledgers. But for any balance affecting user perception of fairness — credits, currency, subscription limits — the counter model creates a support and trust debt that compounds. ⚠️ Build the ledger *before* the first 10 disputes, not after the 50th.

---

### BrightChamps — student `active` flag as de-facto soft delete

**What the API shows:**
- `GET /v1/student/details` returns `active: true/false` on student object
- `isFe: true` parameter masks sensitive parent data (`email` → `****@example.com`)
- Soft delete by convention: `active: false` students remain in database with records intact

**The problem:**

⚠️ **Informal soft delete — no audit trail**
- No `deleted_at` timestamp
- No `deleted_by` audit field
- No retention policy defined
- Unanswerable questions: "How long do we keep inactive records?" "Who deactivated this student and when?"

**The upgrade path:**

| Current State | After Migration |
|---------------|-----------------|
| `active BOOLEAN` only | `active BOOLEAN` + `deactivated_at TIMESTAMP NULL` + `deactivated_by INTEGER NULL` |
| Zero auditability | Full audit trail + compliance-ready |
| Cost: N/A | Cost: Nullable column migration (no table lock) |

**Value unlock:** First enterprise customer audit will require this. Build before customer acquisition.

---

### Stripe — immutable payment records and the append-only ledger

> **Append-only ledger:** A refund is not an UPDATE of the original charge. It's a new `Refund` object referencing the original `Charge`. Same for `Dispute`, `Payout`, etc. Balance = sum of all objects.

**Why it matters:**

⚠️ **Financial regulation requirement** — Banking authorities (US, UK, EU) mandate immutable financial records.

| Requirement | Counter Model | Ledger Model |
|-------------|---------------|--------------|
| Payment can be modified | ✗ Violates compliance | ✓ Impossible by design |
| Audit trail automatic | ✗ Manual | ✓ Built-in |
| Dispute resolution | ✗ Requires DB surgery | ✓ Query new Dispute object |
| Regulator-acceptable | ✗ Retrofit required | ✓ Compliant at architecture |

**PM implication:** For products handling real money, the ledger model is not optional. When asked "Can we just update the payment record on dispute?" — the answer is: *"Payment events are immutable. We create new events (refund, dispute, adjustment) that reference the original. Current balance derives from full event history."*

---

### Enterprise B2B — soft delete as procurement requirement

**What enterprise contracts require:**

⚠️ **Non-negotiable data clauses:**
- "Customer data must be recoverable for 90 days after deletion"
- "All deletions must be logged with initiating user and timestamp"
- "Data export must include soft-deleted records from past 30 days"

These are **contract obligations**, not feature requests. Architectures with hard delete fail these requirements.

**Required schema additions:**

| Component | Purpose | Examples |
|-----------|---------|----------|
| `deleted_at TIMESTAMP NULL` | Soft delete marker | On all customer-facing entities |
| `deleted_by INTEGER NULL` | Audit trail | FK to admin/system user |
| Audit log table | Compliance evidence | All delete events + reason codes |
| Retention policy | Legal compliance | Soft delete → anonymize PII → hard delete per contract |
| Restore API/UI | Customer service enablement | Support restores without DB access |

**SOC 2 Type II connection:**

⚠️ **Auditor findings trigger migrations** — SOC 2 auditors check that production data changes are logged with evidence of who modified what.

| Timing | Cost | Impact |
|--------|------|--------|
| Build at schema design | ~1 sprint | Zero friction |
| Retrofit during SOC 2 prep | Multi-week project | Touches every sensitive table |
| After SOC 2 finding issued | Emergency project + audit delay | Compliance risk |

**Build soft delete at initial schema design.** Retrofit after SOC 2 prep begins is a bottleneck.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands soft delete mechanics, ledger vs counter patterns, cascade behavior, GDPR anonymization pipeline, and compliance requirements.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### The ghost data incident

**What happened:**
A growth PM adds a new "all students" report to the admin dashboard. The engineer building the endpoint joins three tables — students, packages, bookings — but misses the `WHERE deleted_at IS NULL` filter on students. 

**The impact:**
- Report shows: 12,000 students
- Actual live count: 9,400 students
- Missing: 2,600 churned, deleted, or test accounts
- The CEO presents Q3 growth numbers to the board using this dashboard
- Discrepancy surfaces when it doesn't match the billing system count

**PM prevention role:**

Every new data endpoint or report that touches soft-deleted tables needs explicit confirmation in the PR review checklist:

> **Soft-delete check:** "Did we verify the `deleted_at` filter is applied?"

This must be a line item before merge—not a discovery made after the board meeting.

---

### The GDPR erasure that wiped financial history

**What happened:**
A startup receives a right-to-erasure request. The engineer implements a hard delete cascade: `DELETE FROM users WHERE id = X CASCADE`. Booking records, payment records, subscription events — all gone.

**The impact:**
- Accounting system cannot reconcile revenue for that month
- Payment rows reference non-existent users
- Finance team discovers discrepancy during monthly close
- Investigation: 2 days engineering time + partial restore from backup
- Realization: financial records were legally required to be kept for 7 years

⚠️ **Legal/compliance risk:** GDPR erasure and financial record retention have conflicting requirements. Hard delete cascades violate accounting obligations.

**PM prevention role:**

> **GDPR erasure ≠ delete everything.** It means: render the person unidentifiable while preserving legally required records.

The product requirement for "delete account" must explicitly specify:
- Which data is **anonymized**
- Which data is **retained** (and for how long)
- Which **tables the erasure request touches**

*This is a PM spec problem, not an engineering problem.*

---

### The ledger that lost a year of credits

**What happened:**
The team migrates from the counter model to the ledger model mid-way through the product's life. The migration script: for each student, insert one ledger row representing their current balance (`amount = total_credits - credits_consumed`).

**The gap:**
- Historical detail is lost (which classes earned which credits, which payments added how many credits)
- New ledger starts from a snapshot, not from history
- One year later: a student dispute goes back 14 months
- Ledger shows starting balance + all events *after migration only*
- Cannot show what happened before

**PM prevention role:**

When migrating counter → ledger, this decision has compliance and support implications:

| Approach | Cost | Upside | Downside |
|---|---|---|---|
| **Backfill historical events** | Expensive; requires sourcing data from logs + payment records | Full audit trail; supports long-tail disputes | High implementation lift |
| **Start from snapshot** | Cheap; one-time migration script | Fast rollout | Loses pre-migration history; limits dispute window |

*This must be made explicitly, documented, and communicated to customer support.*

## S2. How this connects to the bigger system

| System | Connection | Key Requirement |
|--------|-----------|-----------------|
| **Schema Design Basics (02.07)** | Soft delete adds `deleted_at` and `deleted_by` columns via nullable migrations | Cascade behavior (RESTRICT / CASCADE / SET NULL) must be set at schema design time |
| **Transactions & ACID (02.03)** | Soft delete + audit log entry must atomically succeed or fail together | Transaction scope must include ALL side-effects: both `UPDATE deleted_at` AND `INSERT INTO audit_logs` |
| **ETL Pipelines (02.06)** | Pipelines reading soft-deleted tables must explicitly filter `deleted_at` | Churned students are critical for churn analysis — hard deletion destroys this signal |
| **Caching (Redis) (02.04)** | Redis cache must be invalidated on soft delete, not wait for TTL expiry | ⚠️ Security-sensitive deletions (abuse, parental request) cannot tolerate stale cache hits |
| **PII & Data Privacy (02.09)** | Soft delete alone is insufficient for GDPR compliance | Requires: soft delete → anonymization job → hard delete of PII-free row |

### Deep Dives

#### Schema Design Basics (02.07)
**What:** Soft delete is a schema design decision — adding `deleted_at` and `deleted_by` columns to tables that need it.

**Implementation:** Nullable column migrations (safe) and potentially backfilling values for existing rows. Cascade behavior (RESTRICT vs CASCADE vs SET NULL on foreign keys) is set at schema design time and determines what's possible when a delete occurs.

---

#### Transactions & ACID (02.03)
**What:** A soft delete that must atomically trigger an audit log entry requires a transaction.

**The Problem:** If the soft delete succeeds but the audit insert fails (or vice versa), the audit trail is incomplete.

**Requirement:** Transaction scope must explicitly include all side-effects of a deletion, not just the primary row update. Both the `UPDATE deleted_at = NOW()` and the `INSERT INTO audit_logs` must succeed or both fail.

---

#### ETL Pipelines (02.06)
**What:** ETL pipelines that read from soft-deleted tables must handle the `deleted_at` filter.

**Decision Required:** Extract only live students (`WHERE deleted_at IS NULL`), or extract all students including churned ones?

**Why It Matters:** Churned students are some of the most valuable data for churn analysis — hard-deleting them destroys this signal. The ETL pipeline spec must explicitly address deleted row handling.

---

#### Caching (Redis) (02.04)
**What:** A Redis cache storing a student profile must be invalidated when the student is soft-deleted.

**The Risk:** If the cache key is `student:{id}` and the TTL is 15 minutes, a soft-deleted student's profile may continue to be served from cache for up to 15 minutes after deletion.

⚠️ **For security-sensitive deletions** (account deactivation due to abuse, parental request), this is unacceptable. Event-driven cache invalidation on soft delete is a requirement, not an optimization.

---

#### PII & Data Privacy (02.09)
**What:** Soft delete is the mechanism; anonymization is the outcome required for GDPR.

**The Full Compliance Cycle:**
1. Soft delete makes the account invisible to the user
2. Scheduled anonymization job scrubs PII fields after retention window
3. Final hard delete removes the now-PII-free row

> **Critical:** Neither soft delete alone nor anonymization alone satisfies the full compliance requirement. They must be designed together.

## S3. What senior PMs debate

### Soft delete is a leaky abstraction — should we use event sourcing instead?

**The problem with soft delete:**

| Aspect | Soft Delete | Event Sourcing |
|--------|-------------|-----------------|
| **Storage model** | UPDATE row, filter on queries | Immutable sequence of events |
| **State representation** | Mutable boolean/timestamp flag | Derived from event replay |
| **History** | Lost after deletion | Complete and permanent |
| **Query correctness** | Every query needs "not deleted" filter | Queries against derived state |
| **Audit trail** | Implicit; must be reconstructed | Explicit; built into design |

> **Soft delete:** A pattern where rows are marked as deleted (via a boolean or timestamp) rather than physically removed, requiring filters on every query that assumes the row still exists.

> **Event sourcing:** A design pattern where the database stores the immutable sequence of state changes (events) rather than current state, with current state derived by replaying events.

**The trade-off:**

Event sourcing eliminates soft delete redundancy — deactivation and reactivation are just events in the sequence. The full history is immutable by construction.

The cost is operational complexity:
- Querying current state requires either event replay (slow) or maintaining a separate **projection** (read model) kept in sync with the event log
- Most products aren't built event-first because this complexity is high

**Where the ROI flips:** Event sourcing becomes worth the cost in subsystems handling:
- Money movements
- Compliance-sensitive actions
- Reversible state changes
- The lightweight cousin: the **ledger pattern**

**The senior PM debate:** At what scale or regulatory requirement does the ROI of event sourcing exceed the cost of eventual consistency, projection maintenance, and operational complexity?

---

### Right-to-erasure vs right-to-portability: which obligation wins when data is someone else's too?

**The regulatory collision:**

| Regulation | Obligation | Scope |
|------------|-----------|-------|
| **GDPR Article 17** | Right to erasure | Personal data of the requesting subject |
| **GDPR Article 20** | Right to data portability | Personal data in a structured, portable format |

Both are straightforward when data belongs to one person. They break when data involves multiple people.

**The scenario:**
A student's class booking record contains:
- Student name, enrollment date
- Teacher name, class details
- Shared attendance data

If the student requests erasure, what happens?
- Can you anonymize the teacher's name in *their own* booking history?
- If the class had multiple students, does one student's erasure remove data from another student's record?

**Current regulatory guidance:**
Erasure applies to the personal data *of the requesting subject*, not to records that merely reference them alongside others.

**In practice:**
- Student row → anonymized
- Booking record → student's PII nulled out
- Teacher's view of their teaching history → unaffected

⚠️ **Edge cases proliferate.** The product requirement for "what does 'delete account' actually delete?" must be answered by the PM at design time, not discovered by engineers during implementation.

---

### AI and deletion: does training data inherit the right to erasure?

> **Machine unlearning:** The theoretical process of removing the influence of specific training examples from an already-trained model — currently an active research area, not practically solvable at scale.

**The compliance question:**
When a user requests erasure, must their data be removed from the AI model's training set?

**The practical answer (current industry standard):**
- Training data is anonymized (PII removed) *before* model training
- The model never "contains" personal data in a recoverable sense
- User erasure request is satisfied by anonymizing the source data

⚠️ **Not universally accepted.** The EU AI Act and several national interpretations are still evolving. Regulators may reject the "anonymized training data" argument as insufficient.

**For senior PMs building AI-native products:**

The data retention policy and the AI training data pipeline **must be designed together**, not independently.

If user interaction data feeds model training:
- Resolve right-to-erasure implications *before* the first enterprise customer signs a DPA (Data Processing Agreement)
- "We'll figure it out when someone asks" is not a product strategy — it's a liability

---