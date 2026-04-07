---
lesson: SQL vs NoSQL
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 01.01 — What is an API: APIs read from and write to databases; understanding what's stored where informs API design
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/database-design-doordarshan-meetings.md
  - technical-architecture/architecture/architecture-overview.md
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

## F1. The fifty-seven double-enrollments

**The incident:** Fifty-seven students enrolled in the same class twice and were billed for both during a promotional campaign that drove 4,000+ signups over a weekend (3x normal daily volume).

**Root cause discovery (3-day investigation):**

| System | Behavior | Outcome |
|--------|----------|---------|
| MongoDB (as configured) | Processed duplicate signup requests before first write completed | No automatic duplicate prevention |
| SQL alternative | Would enforce database-level constraint: "no two rows with same student + class" | Duplicates blocked at data layer |
| Application code | Duplicate-catching logic never written | No application-level safeguard |

**The architectural decision:**

18 months prior, the PM deferred to engineering judgment on database selection. The engineer chose MongoDB based on team familiarity. **The critical question never asked:** "What prevents duplicate enrollments at the database level?"

**The cost:**
- 57 refund emails
- 1 engineering sprint lost to data cleanup  
- 1 database constraint (10-minute implementation) left unwritten

---

**⚠️ What this reveals:** 

When PMs default completely to engineering judgment on architecture decisions, critical constraints fall through the cracks—not because engineers are negligent, but because they're optimizing for what they know. A PM's job includes asking the "what breaks this?" questions, even (especially) when deferring technical implementation.

## F2. What it is — the filing cabinet and the sticky note pile

> **Database:** Where your product stores its data permanently. Every user signup, payment, and booking creates a database entry.

### SQL vs. NoSQL at a glance

| Aspect | SQL (Relational) | NoSQL (Document) |
|--------|------------------|------------------|
| **Structure** | Filing cabinet: organized drawers (tables) with labeled sections (columns) | Sticky note pile: flexible notes with variable fields |
| **Schema** | Required upfront | Flexible; enforced in application code |
| **Finding data** | Fast and direct; relationships built-in | Requires scanning; no built-in relationships |
| **Rules** | Database enforces constraints (e.g., no duplicate enrollments) | Application enforces rules |
| **Best for** | Structured, interconnected data | Flexible, varied data shapes |

#### SQL databases (relational)
Work like a well-organized filing cabinet:
- Every drawer = a table (students, classes, payments)
- Every folder = a row (one student, one class)
- Every folder has the same labeled sections (name, email, enrollment_date)
- New sections require reorganizing the entire cabinet

**Strength:** Find anything instantly. Connect related folders: "show me all payments for students enrolled in Math class." Enforce rules: prevent duplicate enrollments.

#### NoSQL databases (document databases like MongoDB)
Work like a pile of organized sticky notes:
- Each note contains whatever you write (name and email on one; name, phone, and emergency contact on another)
- Notes found by label
- Finding all notes where "payment status = completed" requires reading every note that might have that field
- No built-in prevention of duplicate notes

**Trade-off:** Flexibility in exchange for manual enforcement.

### The practical difference

**SQL enforces structure and relationships**
- You define the shape of data before storing it
- The database protects integrity

**NoSQL allows flexible structure**
- Each document can have different fields
- The shape of data lives in your application code, not the database

### Three essential database terms

> **Schema:** The definition of what columns (SQL) or fields (NoSQL) exist and what type of data they hold.
> - SQL requires a schema upfront
> - NoSQL lets you write data without one — but you're making a choice about where enforcement lives, not avoiding enforcement altogether

> **Transaction:** A group of database operations that either all succeed or all fail together.
> - Example: A payment deducts $100 from one account and adds $100 to another. A transaction ensures both happen — or neither does.
> - SQL databases are built for this
> - NoSQL databases have added transaction support, but it varies by product and configuration

> **Primary key:** A unique identifier for each row (SQL) or document (NoSQL).
> - Every record has one
> - This is how the system finds a specific record without reading everything

## F3. When you'll encounter this as a PM

### Situations where database choice matters

**When a new service or feature is being designed**
- Engineering team selects a database type
- Choice shapes the feature's reliability and future flexibility
- **Your move:** Ask "Why this database for this data?" and "What does this choice prevent us from doing later?"

**When the system has a data consistency bug**
- Symptoms: double-charges, duplicate records, missing data
- Root cause often traces to: missing database constraint or incorrect transaction handling
- **Your move:** In post-incident review, ask "Did the database enforce uniqueness, or did we rely on application code?" If application code, assess whether the database choice made enforcement harder

**When a feature requires flexible or variable fields**
- Examples: "Let each school customize student profiles" or "each listing type has different attributes"
- SQL weakness: hundreds of columns with mostly empty cells
- NoSQL strength: handles variable schema naturally
- **Your move:** Recognize this as a legitimate reason to choose or introduce a document database

**When the team proposes adding a new database type**
- "We want to add MongoDB alongside our SQL database" = proposing two systems to operate, monitor, back up, and maintain
- **Your move:** Ask "Is there something we genuinely can't do in the existing database — or is this about developer preference?"

**When an enterprise customer or investor asks about data architecture**
- Weak signal: "Some things are in MongoDB, some in MySQL, we're not sure where the PII is"
- Strong signal: "Our payments are in PostgreSQL with row-level security"
- **Your move:** Database architecture is a trust signal for security-conscious buyers

---

### The two questions that decide the database choice

| Question | Points to SQL | Points to NoSQL |
|----------|---------------|-----------------|
| **Does this data have relationships?** | Yes — records need to link to each other (students→enrollments→classes, orders→customers→payments) and you query across those links | No — records are self-contained and always read as a unit |
| **Does every record have the same shape?** | Yes — every profile has the same columns; structure is a feature | No — some records have 3 custom fields, others have 15; fields vary per customer or context |

**When the answers conflict:** SQL is the safer default — it handles variable data imperfectly but predictably.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands that SQL = structured/relational and NoSQL = flexible/document; that schema and transactions are the key differentiators.
# ═══════════════════════════════════

## W1. How SQL and NoSQL actually differ — the mechanics that matter for PMs

> **Quick Reference:** SQL enforces schema upfront; NoSQL accepts flexible documents. SQL guarantees ACID transactions; NoSQL trades some consistency for scale. SQL excels at relationships; NoSQL at horizontal scaling. Most production systems use both.

### 1. The schema question — who enforces structure?

| Aspect | SQL | NoSQL (Document) |
|--------|-----|------------------|
| **Schema definition** | Defined before data insertion | No enforced schema |
| **Flexibility** | Fixed columns per table | Different documents, different fields |
| **Adding fields** | `ALTER TABLE` migration required | Insert new field in any document anytime |
| **At scale** | Adding column to 50M rows locks table for minutes | No table-wide operations |
| **Data consistency** | Guaranteed uniform shape | Risk of inconsistency across documents |
| **Cost** | Schema discipline enforced; migrations are expensive | Operational risk: inconsistent data shapes undetected |

**Key tension:** SQL's rigidity prevents bad data shapes but makes schema changes costly. NoSQL's flexibility enables quick iteration but requires discipline.

### 2. The relationship question — how data connects to other data

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| **Connection mechanism** | Foreign keys reference other tables | Embed data or application-level lookups |
| **Query pattern** | `JOIN` operations in SQL | Fetch collection → fetch related data separately |
| **What works well** | Complex multi-table queries | Self-contained documents |
| **What fails** | Embedding all related data (denormalization) | N+1 problem at scale (1,000 lookups for 1,000 documents) |

**Example—SQL:** "All students in Math with past-due payments" = single JOIN query.  
**Example—NoSQL:** Same query requires fetching students, then making 1,000+ separate lookups.

### 3. The transaction question — what happens when two writes must both succeed

> **ACID Guarantee:** **A**tomicity (all operations succeed or all roll back), **C**onsistency (data always stays valid), **I**solation (concurrent writes don't corrupt each other), **D**urability (committed data survives crashes).

**SQL model:**
- Multiple operations in one transaction block
- All succeed or all roll back
- Partial state never persists
- Example: Enroll student + decrement available seats = atomic (both succeed or both fail)

**NoSQL model:**
- Single-document operations are atomic
- Multi-document transactions available in MongoDB 4.0+ but require explicit blocks
- Higher performance overhead
- ⚠️ **Risk:** When enrollment correctness is critical, SQL's automatic protection is simpler than reasoning through manual transaction logic

### 4. The query question — what you can ask the database

| Query Type | SQL | NoSQL |
|------------|-----|-------|
| **Complex filters** | ✓ Standard | ✓ Possible but verbose |
| **Aggregations** | ✓ Built-in | ✓ Aggregation pipeline (MongoDB) |
| **Joins** | ✓ Optimized | ✗ Expensive or requires export |
| **Ad-hoc queries** | ✓ Flexible | ✗ Best with known access patterns |
| **Analytics on full dataset** | ✓ Feasible | → Export to data warehouse |

**What this reveals:** SQL supports exploratory analysis; NoSQL requires upfront knowledge of how data will be accessed.

### 5. The scale question — where each hits its limits

| Scaling Approach | SQL | NoSQL |
|------------------|-----|-------|
| **Vertical** | ✓ Easiest (bigger server) | ✓ Works |
| **Horizontal** | ✗ Difficult (sharding, read replicas) | ✓ First-class feature (built-in sharding) |
| **Modern managed services** | ✓ CockroachDB, PlanetScale preserve SQL semantics | ✓ Native horizontal scaling |
| **Best use case** | Moderate scale with complex queries | Billions of events/day, high-volume writes |

**Example:** Activity logs and IoT sensor data scale more naturally on document databases.

### 6. The operational question — who runs it and at what cost?

| Deployment | Operational Burden | Notes |
|------------|-------------------|-------|
| SQL (managed: AWS RDS, Cloud SQL) | Low | Automatic backups, failover, less expertise needed |
| NoSQL (self-hosted: MongoDB on EC2) | High | Flagged as technical debt in live class platforms |

⚠️ **Operational Risk:** Running two database types = two backup strategies, two failure modes, two teams of expertise required. Cost is real, not theoretical.

### 7. The real answer: most production systems use both

**Use SQL for:**
- Payments
- Enrollments
- User accounts
- Bookings

**Use NoSQL for:**
- Activity logs
- User-generated content
- Flexible metadata
- Event streams

**Decision rule:** Running two database types is justified when use cases *genuinely require it*. It's a mistake when done to avoid schema discipline.

## W2. The decisions SQL vs NoSQL forces

### Quick Reference
- **SQL default:** Financial, identity, enrollment, booking data
- **One database default:** Prove a second is necessary before adding it
- **Embed default (NoSQL):** Single owner + always accessed together

---

### Decision 1: What database type for a new service?

| | SQL (PostgreSQL, MySQL) | Document NoSQL (MongoDB, Firestore) |
|---|---|---|
| Best for | Structured, relational data; financial operations; user accounts; anything with JOINs or uniqueness constraints | Flexible/variable schema; high-volume event logs; user-generated content; hierarchical or self-contained data |
| Consistency guarantee | Strong — ACID transactions out of the box | Eventually consistent by default; ACID available but requires explicit configuration |
| Schema flexibility | Low — migrations required for structural changes | High — documents in the same collection can have different fields |
| Query complexity | High — JOINs, aggregations, subqueries standard | Medium — simple by-key or by-field queries; cross-collection queries expensive |

> **PM default:** When in doubt, start with SQL. The discipline of a defined schema catches data model problems before they become production bugs. Add NoSQL only when you have a specific use case SQL handles poorly — not because it's faster to get started.

**When to use SQL:** Financial operations, user accounts, enrollment, booking systems, or any service requiring JOINs or uniqueness constraints.

**When to use NoSQL:** Variable schemas are genuinely needed AND relational queries aren't required.

---

### Decision 2: One database or two (polyglot persistence)?

| | Single database | Mixed databases (polyglot persistence) |
|---|---|---|
| Best for | Teams early in scale; when consistency and simplicity matter more than flexibility | Systems with genuinely different data needs (financial records + high-volume event logs) at scale |
| Operational complexity | One system to monitor, back up, tune | Two systems, two failure modes, two expertise requirements |
| Data consistency | Simpler — cross-table transactions available | Harder — cross-system consistency requires application-level coordination |
| Onboarding friction | Lower — one paradigm | Higher — new engineers learn two systems |

> **PM default:** "We want to add MongoDB" should require a clear answer to: "What can't we do in our current SQL database?" Developer preference or familiarity is not sufficient justification for doubling operational complexity.

**The test:** Start with one database and prove the second is necessary before adding it.

**Red flag:** Requests for a second database based on developer preference or familiarity alone.

---

### Decision 3: Embed related data or keep it separate (for NoSQL)?

| | Embedded data (inside the document) | Referenced data (separate collection) |
|---|---|---|
| Best for | Data that's always read together and owned by one record | Data shared across many records; frequently updated independently |
| Read performance | Fast — one document fetch returns everything | Slower — requires lookup across collections |
| Write performance | Slower — updating embedded data rewrites the whole document | Faster — update the shared record once |
| Consistency risk | Low — one document, one atomic write | Higher — two writes, two failure points |

> **PM default:** Ask: "Is this data owned by one record or shared across many?" Embedding is simpler; referencing is required for shared data.

**Quick decision framework:**
- **Embed if:** Single owner + always accessed together
- **Reference if:** Shared across records OR updated independently

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **1. Is this data relational — does it need to reference other tables or collections?** | Whether JOINs are required. If students link to enrollments which link to classes, a document database will create application-level join complexity that SQL handles natively. If each record is self-contained, document storage fits well. |
| **2. Does this feature need to prevent duplicates or enforce uniqueness at the database level?** | Whether the team is relying on application code or database constraints for data integrity. Database-enforced uniqueness (a UNIQUE constraint in SQL) is reliable even under concurrent load. Application-level duplicate checks can fail during traffic spikes — exactly the scenario behind 57 double-enrollments. |
| **3. Are there operations where two writes must both succeed — or both fail?** | Whether ACID transactions are required. Payment + enrollment record creation, balance deduction + ledger entry, license reservation + meeting record — these pairs produce corrupted state on partial failure. SQL handles this cleanly. If the team chose NoSQL for data requiring this, ask how they're managing transaction safety. |
| **4. How variable is the schema? Will different records in this collection have different fields?** | Whether NoSQL's flexibility is genuinely needed. If every record has the same fields and the schema is stable, SQL's rigidity is a feature, not a constraint. If data is inherently variable — event payloads, user-generated content, configuration metadata — document storage reduces schema migration pain significantly. |
| **5. What's the primary query pattern — fetch by ID, or complex filters across the full dataset?** | Whether query requirements fit the database's strengths. NoSQL excels at "fetch this document by ID or indexed field." It struggles with "find all records where this field is greater than X, grouped by Y." If the analytics team is going to query this data directly, SQL or a data warehouse is needed. |
| **6. Are we adding a new database type, or can this data live in the existing database?** | The real cost of the decision. A second database type doubles operational burden — monitoring, backups, on-call expertise, security patching. If the new data can be modeled in the existing SQL database (even imperfectly), the operational simplicity may outweigh the flexibility gains. |
| **7. Who is running this database — managed service or self-hosted?** | ⚠️ The operational risk profile. Managed databases (AWS RDS, MongoDB Atlas) handle backups, failover, and patching automatically. Self-hosted databases on EC2 require the engineering team to own all of that. Self-hosted MongoDB is documented technical debt in multiple production architectures — a risk that managed services eliminate. |

## W4. Real product examples

### Live class platform — SQL + NoSQL tradeoffs

**What:** MySQL on AWS RDS for structured transactional data (class bookings, enrollments, payments, meeting records, license allocation) + MongoDB self-hosted on EC2 for flexible/unstructured data (event logs, dynamic metadata).

**Why it worked:**
- SQL database handles correctness-critical data with ENUM status fields, foreign keys, and transaction-wrapped license reservation — prevents double-booking
- NoSQL flexibility for event logs without rigid schema constraints

**Where it created risk:**
- MongoDB on self-hosted EC2 = higher operational overhead than managed service
- Inconsistent scaling, no automatic failover
- Running a second operational system with no managed backing

**Takeaway:** Polyglot persistence is real — SQL for transactions, documents for flexible data. But self-hosting a second database is a *named operational cost*, not an afterthought. MongoDB Atlas or Firestore reduce this significantly.

---

### Airbnb — schema flexibility at listing scale

**What:** Stores 7+ million listings with radically different types (apartments, yachts, treehouses, castles). Each type has different attributes (yachts: dock location, captain availability; treehouses: weight limits, ladder access).

**Why it worked:**
- Listing attributes (flexible, variable, read-heavy) → flexible document store
- Bookings, payments, user accounts (structured, correctness-critical) → SQL
- Eliminated constant schema migrations when adding new listing types

| Pain Point | SQL Approach | Document Approach |
|---|---|---|
| New property type added | Add columns, migrate schema | Update document template |
| NULL values in schema | 80%+ of rows NULL | Omit field if not applicable |
| Operational burden | High at 7M+ listings | Minimal |

**Takeaway:** When product catalog has genuinely variable attributes per record type, document storage removes schema migration work. Signal: if SQL columns are NULL for 80%+ of rows, consider a document model.

---

### Facebook/Instagram — SQL at billion-user scale

**What:** Meta chose MySQL as primary database, scaled horizontally to 10,000+ MySQL hosts using Vitess (open-source sharding layer). Instagram's PostgreSQL similarly runs at scale on SQL.

**Why it matters:** Common assumption: "at scale, you need NoSQL." ❌

Meta disproves this. With proper sharding and proxy layers, SQL semantics (transactions, complex queries, foreign key constraints) work at internet scale.

**Takeaway:** "We'll need NoSQL at 100× scale" is often false. SQL scales with infrastructure investment. Real question: Does your team have expertise to scale SQL horizontally? Does NoSQL solve a problem you have *today* — not one you might have later?

---

### Notion — document database as the product

**What:** Entire product built on document model. Every piece of content — pages, databases, bullet points, tables, images — is a "block" with type, content, and properties. 20+ million users, block table is one of highest-traffic document collections.

**Why schema flexibility is load-bearing:** Users define their own content structure. Rigid SQL schema would break the product.

**What breaks:** When Notion added relational database features (linked records), they had to build SQL-like semantics on top of documents — re-inventing foreign keys and lookups from scratch. Significant engineering effort.

**Takeaway:** Documents are right for user-defined structure. But relational queries don't disappear — they get pushed to application code. If you eventually need relationships between records, you're either migrating to SQL or building relational logic on documents. Both are expensive.

---

### Enterprise B2B SaaS — compliance-first architecture

**What:** Enterprise SaaS (healthcare, financial services, HR) runs all customer data on PostgreSQL — not for performance, but for compliance.

| Requirement | SQL (PostgreSQL) | Document Database |
|---|---|---|
| **GDPR "right to be forgotten"** | Targeted DELETE by customer_id in transaction — all related records removed atomically | Full-collection scan; no atomicity guarantee ⚠️ |
| **Multi-tenant isolation** | Row-level security policies at database layer — enforced for all queries | Application logic prevents cross-tenant access (but has bugs) ⚠️ |
| **Audit compliance** | ACID-guaranteed audit logs | Application-level logging (incomplete) ⚠️ |

> **Row-level security:** Database-level rule enforcing Customer A's data is never accessible to Customer B — cannot be bypassed by application code.

⚠️ **Security implication:** When prospect security team asks "how is our data isolated?", answer "row-level security at PostgreSQL layer with ACID audit logs" passes SOC 2 review. "Application logic prevents cross-tenant access" does not — because application logic has bugs.

**Takeaway:** For enterprise B2B SaaS, database choice is often a *sales qualification question before an engineering question*. If serving regulated industries, SQL's audit trail, ACID guarantees, and row-level security are the answer to "can we trust you with our data?" — not features added after contract signing.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands SQL vs NoSQL mechanics, when to use each, and polyglot persistence tradeoffs.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### "NoSQL for everything" — the flexibility trap

**The pattern:**
Teams in the 2010s adopted MongoDB for faster startup (no schema migrations, no upfront design). At year two, the cost reappeared:
- Application code became the implicit schema
- Every service made undocumented assumptions about fields, types, required attributes
- Database enforced nothing
- Errors surfaced silently in production (missing field = null, not error)
- Data corruption went undetected for months

**The hidden cost:**
Teams rebuilt schema discipline in application logic instead of database constraints—paying the design cost they'd avoided upfront, plus added complexity spread across code they didn't control.

**PM prevention role:**
- Require explicit written schema documentation for document databases, even though the database won't enforce it
- Treat the written schema as a contract the team maintains
- Unwritten schemas degrade silently over 18 months

---

### "SQL for everything, forever" — the NULL column cemetery

**The pattern:**
Teams kept adding columns to SQL tables instead of introducing a second data model:

| What happened | Cost |
|---|---|
| Student table: 12 → 147 columns | Schema migrations require maintenance windows |
| 80% of rows NULL in 60+ columns | Every query hits bloated table |
| Inertia delayed modeling decision | Compound technical debt |

**The right call (two years ago):** Separate document store for flexible attributes; keep SQL table lean.

**PM prevention role:**
- Require schema migrations to appear in sprint estimates as real engineering work
- Watch for consistent underestimation—signals the SQL schema has grown too wide
- Review question for each new field: *Does this belong in the existing table, or does it need different storage strategy?*

---

### Migration debt compounds under operational pressure

**The pattern:**
Painful migrations aren't planned—they're forced:
- Poorly-designed SQL schema needs structural changes in production
- Self-hosted MongoDB needs to move to managed service
- Both require touching live data while systems operate

**Real example:**
A live class platform's self-hosted MongoDB on EC2 was flagged as technical debt over a year ago. Every week of delay = another week of application code written against the unmanaged deployment, growing the surface area the migration must eventually touch.

**PM prevention role:**
- Database choice is a **sprint-1 decision** that constrains architecture for years
- It deserves the same scrutiny as any other foundational decision
- "Let's revisit later" is a debt accumulation strategy, not a deferral strategy

## S2. How this connects to the bigger system

| System | Role | Key Decision Point |
|--------|------|-------------------|
| **Transactions & ACID (02.03)** | Determines if multi-record consistency is possible | SQL for payments, enrollments, inventory; NoSQL when ACID is optional |
| **Indexing (02.02)** | Required by both; failure mode identical at scale | SQL indexes columns; NoSQL indexes document fields—both prevent query timeouts |
| **Caching (02.04)** | Bridges the gap between query costs | Redis layers between expensive SQL queries and dynamic data |
| **Data Warehouses (02.05)** | Separates analytical from operational traffic | OLAP queries must run separately from OLTP production systems |

---

### Transactions & ACID (02.03)

The SQL vs NoSQL choice is largely a **transaction decision in disguise**.

- **When ACID matters:** payments, enrollments, inventory — multi-record consistency required
- **SQL is the path of least resistance** when you need it
- **The lesson:** Understanding when ACID matters, and what happens when it's absent, is what makes this choice legible at the architectural level

> **ACID:** Atomicity, Consistency, Isolation, Durability — guarantees that multi-record updates either all succeed or all fail, with no intermediate states visible to other processes

---

### Indexing (02.02)

Both SQL and NoSQL require indexing strategies — **the form differs, the failure mode is identical**.

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| **Index accelerates** | Column queries | Document fields or nested paths |
| **Small scale** | Missing indexes invisible | Missing indexes invisible |
| **Production scale** | Query timeouts, cascading degradation | Query timeouts, cascading degradation |

**The lesson:** The SQL vs NoSQL choice doesn't eliminate the indexing requirement — it changes its shape.

---

### Caching (02.04)

Redis often fills the gap between SQL query cost and document database query limitations.

**Architecture pattern:**
- Expensive SQL queries → cached in Redis
- Real-time counters → stored in Redis  
- Event logs → stored in document stores
- Dynamic data too fresh to pre-compute → Redis as buffer layer

**The lesson:** Understanding where caching fits relative to database choice is how architectural decisions are actually made—not as isolated choices, but as a system.

---

### Data Warehouses vs Databases (02.05)

Both SQL and NoSQL are **OLTP systems** — built for writes and point reads.

> **OLTP:** Online Transactional Processing — optimized for frequent writes and fast single-record lookups

> **OLAP:** Online Analytical Processing — optimized for aggregations and scans across historical datasets

**When analytics needs differ from operational needs:**

| Workload | Right Tool | Why |
|----------|-----------|-----|
| Cohort analysis, funnel queries, aggregations across millions of rows | Data warehouse | Designed for scan-heavy analytical queries |
| Production writes and point reads | SQL or NoSQL database | Designed for transactional throughput |

⚠️ **Risk:** Letting the analytics team query the production database directly is one of the most common causes of production database performance degradation — write traffic and analytics traffic compete for the same resources.

## S3. What senior PMs debate

### NewSQL: does it make the SQL vs NoSQL choice obsolete?

| Aspect | NewSQL Thesis | Counterargument |
|--------|---------------|-----------------|
| **What it solves** | SQL semantics + horizontal scaling (previously required NoSQL for write-heavy workloads) | Operational and cost complexity outweighs benefits below internet-company scale |
| **Examples** | Google Spanner (multi-region, strong consistency); CockroachDB (open-source equivalent); PlanetScale (MySQL-compatible, auto-sharding) | Vanilla MySQL or Postgres sufficient for most teams |
| **Key question** | Is scale concern current or hypothetical? Is horizontal scaling needed now or in 3 years? | — |

**What this reveals:** The decision hinge is *when* you need scale, not whether you theoretically could.

---

### PostgreSQL with JSON columns: is MongoDB still needed?

| Aspect | JSONB Case | MongoDB Case |
|--------|-----------|--------------|
| **Strength** | Polyglot single system; competitive performance; no operational overhead if already running Postgres | Mature document model, replication, aggregation pipeline; idiomatic for document-heavy workloads |
| **Weakness** | Works against the data model if 90% of data is document-oriented | Requires additional operational infrastructure |
| **Decision factor** | Use for 10% document data in a primarily relational system | Use if 90% of data is document-style |

**What this reveals:** The ratio of document-to-relational data determines whether JSONB pragmatism becomes architectural compromise.

---

### AI is creating a third database category — and the mental model needs updating

> **Vector Database:** A specialized database that stores high-dimensional numerical representations (embeddings) of content and queries by similarity rather than equality or range.

**Examples:** Pinecone, Weaviate, Qdrant, pgvector

**How it differs:**
- SQL/NoSQL: Query by equality, range, or document structure
- Vector DB: Query by similarity — "give me the 10 records semantically closest to this input"

**Why this matters for PMs:**

The 2025 database choice is no longer binary:
- ❌ **Risk:** Build semantic search on SQL LIKE queries or NoSQL document scans → lower quality results + order-of-magnitude higher query costs
- ✅ **Better approach:** SQL + NoSQL + vector database, each handling what it's designed for

**Use cases requiring vector databases:**
- Semantic search
- Recommendation systems
- Document similarity
- Chatbot context retrieval

**What this reveals:** Teams that distinguish this category in 2025 avoid costly architectural mismatches between query pattern and data structure.