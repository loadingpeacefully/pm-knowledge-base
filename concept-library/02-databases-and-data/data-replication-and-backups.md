---
lesson: Data Replication & Backups
module: 02 — Databases & Data Systems
tags: tech
difficulty: working
prereqs:
  - 02.01 — SQL vs NoSQL: backup and replication strategies differ between SQL (AWS RDS managed backups) and NoSQL (MongoDB on EC2 requires manual orchestration); this lesson contrasts the two approaches
  - 02.07 — Schema Design Basics: schema migrations interact with replication — a migration on the primary propagates to replicas and can cause replication lag or failure if not managed correctly
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/infrastructure/infra-monitoring.md
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

## F1. The database that had no spare tire

### Database Architecture at BrightChamps

BrightChamps runs two types of databases:

| Database | Type | Service Model | Managed By |
|----------|------|---------------|-----------|
| Student, payments, class records | Relational (AWS RDS) | Managed service | AWS |
| Flexible document storage | MongoDB | Self-hosted | BrightChamps engineering team |

The architecture document flags the MongoDB setup as a single line: "MongoDB self-hosted on EC2 rather than managed Atlas — operational risk." But the practical implications are significant.

---

### How AWS RDS Multi-AZ Works

> **Multi-AZ:** Multiple Availability Zones — different physical data centers in different geographic locations

AWS RDS with Multi-AZ deployment maintains an exact copy of the database on a separate machine in a separate data center. If the primary machine fails (hardware failure, disk corruption, network issue), AWS automatically promotes the standby copy to primary — typically within 60 to 120 seconds.

**Outcome:** Teachers continue classes. Students continue booking. Payments continue processing.

---

### How Self-Hosted MongoDB Fails

The self-hosted MongoDB on EC2 has no automatic standby. The disk holding the data exists on one machine.

**If that machine fails:**
- Hardware failure
- Disk corruption
- Engineer accidentally terminates the wrong instance

Recovery depends entirely on the backup strategy in place:
- **No automated backups** → data is gone
- **Manual backups every 24 hours** → restore to yesterday's state, losing everything since then

During peak class scheduling periods, a day's worth of data includes thousands of booking records, teacher availability updates, and quiz results.

---

### Recovery Metrics: RTO and RPO

> **RTO (Recovery Time Objective):** Time between when something breaks and when the product is back to normal

> **RPO (Recovery Point Objective):** How much data you can afford to lose

| Metric | Managed RDS | Self-Hosted MongoDB |
|--------|-------------|-------------------|
| **RTO** | 2 minutes | Hours (manual restore, testing, failover) |
| **RPO** | ~Zero (continuous replication) | 24 hours (last backup captured) |

**What this reveals:** Most product managers have never been asked "what is our RPO and RTO?" for a feature they shipped. Yet every feature that stores data implicitly answers this question through backup and replication decisions made when the database was set up. If a feature stores booking data in self-hosted MongoDB and the machine fails, the PM's "24-hour RPO" decision was made before they knew they'd made it.

---

### Case Study: The Corruption That Spread

⚠️ **Risk scenario:** An engineering team runs a schema migration on the primary database during business hours. The migration has a bug — it corrupts 50,000 rows in the `student_class_balances` table.

**The problem:** Replication is running. Both the write and the corruption replicate to the standby immediately.

**Discovery:** 30 minutes later, both primary and replica contain corrupted data. The backup from 2am that morning is the last clean copy.

**Recovery cost:** 12 hours of class completions, payment updates, and credit adjustments must be reconstructed manually or accepted as lost.

---

### Replication vs. Backups: Know the Difference

> **Replication:** Copies of current state (including mistakes)

> **Backups:** Point-in-time snapshots that let you go back before the mistake

Both matter. Together, they define what's possible when things go wrong.

## F2. What it is — the spare tire and the checkpoint system

### Replication vs. Backups at a Glance

| Aspect | Replication | Backups |
|--------|-------------|---------|
| **What** | Live copy kept in sync with primary | Snapshots captured at intervals |
| **Timing** | Immediate (or near-immediate) updates | Periodic (hourly, daily, etc.) |
| **Failure scenario** | Replica takes over if primary fails | Restore from checkpoint before problem occurred |
| **Data corruption** | Replica copies corruption from primary | Can recover to pre-corruption state |
| **Analogy** | Second car following first, matching every turn | Video game save points at regular intervals |

---

### Replication: The Live Copy

> **Replication:** Every write to the primary is immediately (or near-immediately) sent to one or more replica databases. The replica contains everything the primary had.

**Key insight:** If the primary fails, a replica can take over—but it also replicates any data corruption that happened before the failure.

*Analogy:* If the first car crashes, the second one is right there to continue the journey. But if the first car drives off a cliff because the driver made a wrong turn, the second car follows it off the cliff too.

---

### Backups: The Checkpoints

> **Backups:** Snapshots of the database saved at regular intervals in a separate location. They capture a specific moment in time and don't stay in sync with the live database.

**Key insight:** You can restore from a checkpoint before a problem occurred (bad migration, data corruption, accidental deletion).

*Analogy:* Like save points in a video game. Every few levels, the game auto-saves. If you die, you restart from the last save point—but you lose progress since then.

---

### The Four Recovery Terms

> **RPO (Recovery Point Objective):** The maximum acceptable age of data you can recover from.
- If RPO = 1 hour and a failure occurs, you can afford to lose at most 1 hour of data
- Drives backup frequency (1-hour RPO requires hourly backups)

> **RTO (Recovery Time Objective):** The maximum acceptable time to restore service after a failure.
- If RTO = 4 hours, the system must be back online within 4 hours of outage start
- Drives failover and recovery architecture (2-minute RTO requires automated failover; 4-hour RTO allows manual recovery)

> **Replication lag:** The delay between a write on the primary and when it appears on the replica.
- **Synchronous replication:** Zero lag but slower writes (primary waits for replica confirmation)
- **Asynchronous replication:** Fast writes but small lag window (replica slightly behind)

> **Failover:** The process of promoting a replica to become the new primary when the original primary fails.
- **Automatic failover** (managed databases like RDS Multi-AZ): 60–120 seconds, no human intervention
- **Manual failover:** Engineer detects failure, promotes replica, updates connection strings — minutes to hours

## F3. When you'll encounter this as a PM

### When scoping an SLA or uptime commitment

"We commit to 99.9% uptime" sounds like a product decision but is actually a replication and backup architecture decision.

| Uptime Commitment | Allowed Downtime (Annual) | Allowed Downtime (Monthly) | Technical Requirement |
|---|---|---|---|
| 99.9% | 8.7 hours | ~44 minutes | Automated failover |

⚠️ **Risk:** Committing to 99.9% without confirming the technical architecture to support it means committing to something the product can't deliver. If the current architecture requires manual engineer intervention to restore from backup, actual uptime is determined by engineer availability, not technical guarantees.

---

### When asking "what's our disaster recovery plan?"

For any data-storing feature, this question should be asked before launch, not after an incident.

**Required information to document:**
- Where are backups stored?
- How frequently are they taken?
- How long does a restore take?
- Has the restore process been tested recently?

⚠️ **Warning sign:** If the answer is "automated AWS RDS backups for MySQL" but "we're not sure" for MongoDB, the product has asymmetric risk — one database is protected, the other is a single point of failure.

---

### When a database incident occurs

The first question in any data loss incident: **"What was our last clean backup, and how long does a restore take?"**

⚠️ **Critical:** If the answer takes hours to determine, the product doesn't have a documented recovery process.

**PM advantage:** PMs who confirmed RPO and RTO in advance can have the right conversation with the CTO during an incident:

> *"Our backup was 6 hours ago — we're looking at losing 6 hours of data if we restore. What's the plan?"*

PMs who haven't confirmed this arrive without information.

---

### When an enterprise customer asks about your business continuity plan

Enterprise contracts — especially with schools, corporations, and regulated industries — increasingly require documented RPO and RTO guarantees.

**Insufficient answer:**
- "We use AWS and they're reliable"

**Required answer:**
- "Our RTO is X hours, RPO is Y hours, and here's the architecture that supports those guarantees"

*What this reveals:* This information comes from engineering, but the PM must know to ask for it and understand what the answer means for the product's commitments.

---

### When evaluating the MongoDB on EC2 tech debt

The architecture overview flags MongoDB self-hosted on EC2 as an "operational risk."

**Translation to product decision:**
1. What features currently store data in MongoDB?
2. What is their current RPO and RTO?
3. What would happen to users of those features if the MongoDB instance failed today?

> **Strategic framing:** The PM who can articulate "here is the specific user-facing risk and here is the cost of fixing it" is better positioned to prioritize the migration to managed Atlas than the PM who treats it as an abstract infrastructure item.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands RPO, RTO, replication vs backups, and the business risk of the MongoDB on EC2 setup.
# ═══════════════════════════════════

## W1. How replication and backups actually work — the mechanics that matter for PMs

### Quick Reference
- **RTO** = Recovery Time Objective (how fast you restore)
- **RPO** = Recovery Point Objective (how much data loss you accept)
- **Synchronous replication** = zero data loss, slower writes
- **Asynchronous replication** = faster writes, data loss risk
- **Multi-AZ** = minimum for production user data
- **Unmanaged backups** = highest operational risk

---

### 1. Replication architectures — the PM-relevant choices

Replication means continuously copying data from a primary database to one or more secondary databases. There are four core configurations a PM encounters:

| Architecture | How it works | RTO | RPO | PM use case |
|---|---|---|---|---|
| **Single instance** | One database, no copy | Hours (manual restore from backup) | Hours (last backup) | Development, non-critical features — never for production user data |
| **Read replica** | Primary handles writes; replicas handle reads; replicas do not auto-promote if primary fails | Hours (manual failover) | Seconds–minutes (replication lag) | High read traffic — reports, analytics, dashboards. Does NOT protect against primary failure without manual intervention |
| **Multi-AZ (standby replica)** | Primary + standby in different availability zones; standby auto-promotes if primary fails | 60–120 seconds (automatic) | Seconds (synchronous or near-synchronous replication) | Production workloads with uptime requirements; the minimum for any feature where data loss is unacceptable |
| **Multi-region** | Replicas in geographically separate regions | Minutes (cross-region failover) | Seconds–minutes (replication lag across regions) | Global products, data residency requirements, catastrophic region-level failure protection |

### BrightChamps — RDS Architecture Verification

**What:** AWS RDS for MySQL supports all three replication patterns.

**Why:** The architecture overview does not confirm whether Multi-AZ is enabled — a PM owning any payment or class scheduling feature must verify this.

**Takeaway:** Multi-AZ is not a default; it must be explicitly requested and confirmed.

---

### 2. Synchronous vs asynchronous replication — the write latency tradeoff

Every replication setup makes a fundamental choice: does the primary wait for the replica to confirm before acknowledging the write to the application?

> **Synchronous replication:** Primary sends write to replica, waits for acknowledgment, then confirms success to the application. Zero data loss risk — if the primary fails after confirmation, the replica has the data. Cost: every write is slower by the round-trip time to the replica (typically 1–5ms within a data center, 20–100ms cross-region).

> **Asynchronous replication:** Primary confirms success immediately, sends write to replica in the background. Faster writes. Risk: if the primary fails between the write confirmation and the replica receiving it, those writes are lost. Typical lag: milliseconds to seconds within a region.

**AWS RDS Multi-AZ behavior:**
- Uses synchronous replication within the same region
- Near-zero data loss
- Write latency overhead: 1–2ms
- Read replicas use asynchronous replication — faster writes, with up to a few seconds of lag before replicas reflect recent writes

#### Read-after-Write Consistency — A PM Decision Point

If you build a feature where a user writes data and then immediately reads it (bookings confirmation, payment completion → show updated balance):

- **Can that read go to a replica?** If the replica is 2 seconds behind, the user sees stale data.
- **Who decides?** The PM must specify read-after-write consistency requirements, not the engineering team assume them.

---

### 3. Backup types — full, incremental, and point-in-time recovery

| Type | How it works | Storage cost | Restore time | PM implication |
|---|---|---|---|---|
| **Full backup** | Complete snapshot of the entire database | High — entire DB per backup | Slowest — restore entire DB | Run weekly or daily; provides a clean baseline |
| **Incremental backup** | Only changes since last full backup | Low — only deltas | Slower than full if many incrementals must chain | Common for large databases; restore = apply full + all incrementals since |
| **Point-in-time recovery (PITR)** | Continuous binary log capture; restore to any second in the retention window | Medium — continuous log stream | Fast — apply full backup + logs to target time | Enables "restore to 3:47pm yesterday" after a bad migration |

#### AWS RDS Automated Backups

- **Default:** Point-in-time recovery enabled
- **Retention window:** Configurable (1–35 days)
- **Capability:** Restore database to any specific second within retention window
- **Critical use case:** Recovering from bug-induced data corruption at a known timestamp

#### MongoDB on EC2 — Unmanaged Backups

⚠️ **Risk:** No automated backups by default.

Engineering team must build:
- Cron jobs to trigger `mongodump`
- Scripts to upload snapshots to S3
- Monitoring to verify backups completed successfully

**The hidden failure mode:** If the cron job silently fails for a week, the "latest backup" assumption is wrong.

---

### 4. The RTO/RPO math — what commitments are actually achievable

| Setup | Realistic RPO | Realistic RTO | Monthly downtime budget for 99.9% SLA |
|---|---|---|---|
| RDS Single-AZ + daily backups | 24 hours | 2–4 hours (restore from backup) | 44 minutes — **unachievable** with 2–4h RTO |
| RDS Single-AZ + PITR enabled | Near-zero (seconds) | 30–60 minutes (restore from PITR) | **Achievable** if restore is automated |
| RDS Multi-AZ | Near-zero | 60–120 seconds (automatic failover) | **Achievable** |
| RDS Multi-AZ + read replicas | Near-zero | 60–120 seconds | **Achievable** with no read traffic interruption during failover |
| MongoDB EC2 (no managed backups) | Unknown — depends on manual schedule | Hours to days — manual restore | **Not achievable** without architectural change |

#### MongoDB EC2 Risk Quantified

If the MongoDB EC2 instance fails today and the last verified backup is from 3 days ago:

- **RPO** = 3 days
- **RTO** = estimated 4–8 hours (restore MongoDB on new EC2, verify data integrity, update connection strings)
- **SLA impact:** Any feature storing critical user data in this instance cannot make a credible SLA commitment

---

### 5. Backup validation — the step most teams skip

⚠️ **A backup that has never been tested is not a backup. It's a file that might be restorable.**

Backup files can be corrupted, incomplete, or stored in a format that can't be quickly restored. The only way to know a backup is good is to restore it.

#### Three Backup Validation Tests

**Restore test**
- Restore the backup to a test environment
- Verify data looks correct
- Check table counts, spot-check specific records
- Verify indexes are intact

**Timing test**
- How long does the restore actually take?
- A 500GB database might take 4 hours to restore from S3
- If your RTO commitment is 2 hours, the backup strategy is insufficient

**Automated verification**
- After each backup completes, run a checksum or row count comparison
- Confirm the backup file is valid
- Alert if verification fails

#### AWS RDS vs Self-Managed Approach

| Responsibility | AWS RDS | MongoDB EC2 |
|---|---|---|
| **Backup validation** | AWS validates automatically | Engineering team must build and run |
| **Testing burden** | Low | High |

The BrightChamps tech debt item on MongoDB migration implicitly includes backup validation as part of the rationale for moving to Atlas.

---

### 6. Replication and backups in a microservices architecture

> **Critical: In microservices, there is no single database strategy.** Each service owns its own backup and replication requirements. Multi-AZ RDS for one service and unmanaged MongoDB EC2 for another means the product has inconsistent SLAs — even if the team thinks of it as "we use AWS."

⚠️ **Every cross-service feature's recovery posture is only as strong as its weakest database.**

BrightChamps has 11 microservices, each owning its data. Replication and backup strategy must be specified per service:

### Eklavya — Students, Payments
- **Database:** MySQL on RDS
- **Verification needed:** Is Multi-AZ enabled?
- **Backup retention window:** Confirm settings

### Paathshala — Classes
- **Database:** MySQL on RDS
- **Verification needed:** Is Multi-AZ enabled?
- **Backup retention window:** Confirm settings

### Doordarshan — Meetings
- **Database:** MySQL on RDS
- **Verification needed:** Is Multi-AZ enabled?
- **Additional risk:** Is Zoom license state recoverable?

### MongoDB Services
- **Database:** Self-hosted EC2
- **Risk level:** Highest
- **Status:** No confirmed backup strategy
- **Mitigation:** Migration to Atlas reduces operational risk

### Redis Caches
- **Role:** Ephemeral by nature
- **Recovery requirement:** Loss is acceptable (cache rebuilt from DB)
- **Verification needed:** Confirm no critical state exists only in Redis

#### Cross-Service Feature Checklist

A PM owning a cross-service feature must understand which databases their data touches and whether each has adequate backup and replication coverage.

❌ **Not acceptable:** "We use AWS"

✅ **Acceptable:** "We use AWS RDS with Multi-AZ and 7-day PITR for MySQL, and we're migrating MongoDB to Atlas"

## W2. The decisions replication and backups force

### Decision 1: What RPO and RTO does this feature require?

> **RPO (Recovery Point Objective):** Maximum acceptable data loss, measured in time. RPO of 1 hour means losing up to 1 hour of data is acceptable.

> **RTO (Recovery Time Objective):** Maximum acceptable downtime before the system is restored and serving traffic again.

**PM default:** For any feature where data loss causes direct user harm (payments, class credits, booking history), require RPO ≤ 1 hour and RTO ≤ 30 minutes. This mandates Multi-AZ replication and PITR backups. For non-critical features (preferences, analytics events, non-transactional logs), RPO of 24 hours and RTO of 4 hours may be acceptable.

| Feature type | Acceptable RPO | Acceptable RTO | Minimum infrastructure |
|---|---|---|---|
| Payment records, class credits | Near-zero (seconds) | < 5 minutes | Multi-AZ + PITR + read replicas |
| Booking history, student profiles | < 1 hour | < 30 minutes | Multi-AZ + PITR |
| Teacher availability, scheduling | < 1 hour | < 1 hour | Multi-AZ |
| Analytics events, preferences | < 24 hours | < 4 hours | Single-AZ + daily backups |
| Non-persistent cache data | N/A — rebuild from DB | N/A | No backup required |

---

### Decision 2: Read replicas for read traffic, or primary-only?

> **Read replica:** A read-only copy of your database that stays in sync with the primary. Accepts queries but not writes.

**PM default:** Use read replicas for any query pattern with high read-to-write ratios (reporting dashboards, analytics, class history views) where up-to-2-second read lag is acceptable. Never route read-after-write queries (show confirmation immediately after save) to read replicas — always read from primary for those.

| | Primary-only | Read replicas |
|---|---|---|
| Read latency under load | Degrades as read traffic increases | Stable — read load distributed across replicas |
| Write latency | No additional overhead | Minimal (replication is async for read replicas) |
| Read consistency | Always fresh | Up to seconds stale — not suitable for read-after-write |
| Cost | Lower — single instance | Higher — additional replica instances |
| **Best for** | **Low to medium traffic; read-after-write required** | **High read traffic; analytics and reporting; read lag acceptable** |

---

### Decision 3: Managed database service vs self-hosted?

> **Managed database service:** Cloud provider (AWS RDS, Google Cloud SQL, MongoDB Atlas) handles backups, failover, patching, and infrastructure maintenance.

**PM default:** Use managed database services for all production databases. Self-hosted databases require the engineering team to own backup orchestration, failover automation, version patching, and capacity management. The engineering time cost of self-hosted operations consistently exceeds the cost savings.

| | Managed (RDS, Atlas) | Self-hosted (EC2 + MongoDB) |
|---|---|---|
| Backup automation | Included and managed by cloud provider | Must build, monitor, and maintain yourself |
| Failover | Automated (Multi-AZ: 60–120 seconds) | Manual — requires on-call engineer at any hour |
| Version patching | Managed maintenance windows | Engineering team owns patching schedule |
| Engineering overhead | Near-zero for operational maintenance | Estimated 20–40 engineering hours/month per instance |
| Cost | Higher instance costs | Lower instance costs + hidden operational time cost |
| **Default** | **All production databases** | **Legacy only — never for new production workloads** |

⚠️ **Operational risk:** Self-hosted databases without automated failover create 24/7 on-call burden and single points of failure. A database outage at 3 AM requires an engineer to manually restore service.

## W3. Questions to ask your engineer

| Question | What This Reveals |
|----------|-------------------|
| **Is our primary database running with Multi-AZ replication enabled?** | Whether production has automated failover or if every hardware failure becomes a manual recovery incident |
| **What is our current RPO and RTO for each database in the system?** | Whether recovery objectives are documented, tested, and backed by infrastructure |
| **When was the last time a backup restore was actually tested?** | Whether backups are trusted or merely assumed to work |
| **What is the backup retention window, and what happens to backups containing user PII after the retention period?** | Whether retention aligns with recovery needs AND privacy obligations |
| **For the MongoDB instances on EC2 — what is the backup schedule, and where are backups stored?** | Whether the highest-risk database in the architecture has any recovery capability |
| **If the primary database fails at 3am on a Sunday, what actually happens?** | Whether recovery requires human intervention and how quickly |
| **Do read replicas exist? Are any queries currently routed to them?** | Whether the product has read scaling capacity and if time-sensitive queries might read stale data |

---

### Question 1: Multi-AZ replication

**Expected answer:** "Yes — Multi-AZ is enabled for all production instances handling user data."

**Red flags:** Any "no" means the uptime SLA has no technical backing.

*What this reveals:* Whether every hardware failure becomes a manual recovery incident.

---

### Question 2: RPO and RTO by database

**Expected answer:** Names each database type (RDS MySQL, MongoDB EC2), states RPO and RTO explicitly, explains what infrastructure achieves those numbers.

**Red flags:** "I'm not sure" means the product has no recovery guarantee.

*What this reveals:* Whether recovery objectives are documented, tested, and backed by infrastructure.

---

### Question 3: Last backup restore test

**Expected answer:** "We ran a restore test last quarter. The restore took X hours, and the data integrity checks passed."

**Red flags:** "Never" or "a long time ago" means the backup strategy is unverified — the backup file might exist but the restore process might be broken.

*What this reveals:* Whether backups are trusted or merely assumed to work.

---

### Question 4: Backup retention and PII handling

**Expected answer:** Specifies the retention window, acknowledges the PII implication, states that backup retention is disclosed in the privacy policy.

**Context:** 7-day retention is standard on RDS. But backups contain PII — if a user requests erasure under GDPR, the live database is anonymized, but backups from before the erasure still contain their data.

⚠️ **Privacy risk:** Backup retention must align with both recovery needs AND privacy obligations. If you cannot delete backups on demand, you cannot fully comply with erasure requests.

*What this reveals:* Whether backup retention aligns with recovery needs and privacy obligations.

---

### Question 5: MongoDB on EC2 — backup schedule and storage

**Expected answer:** Includes a specific schedule (e.g., "daily `mongodump` to S3 bucket, with backup completion monitoring"), a retention period, and confirmation that the backup was successfully taken in the last 24 hours.

**Red flags:** "We're working on it" means there's currently no reliable backup.

*What this reveals:* Whether the highest-risk database in the architecture has any recovery capability.

---

### Question 6: 3am Sunday failure scenario

**Expected answer varies by architecture:**

| Scenario | Answer | Risk Level |
|----------|--------|------------|
| RDS Multi-AZ | "AWS automatically fails over to standby — we get a Slack alert, no intervention required" | Low |
| Manual process | "An on-call engineer gets paged, assesses failure, begins restore" | Medium |
| Self-hosted MongoDB, no on-call | "We discover it Monday morning" | High |

*What this reveals:* Whether recovery requires human intervention and how quickly someone is available.

---

### Question 7: Read replicas and query routing

**Expected answer:** Identifies which query patterns go to replicas (reports, analytics, history views) and confirms that transactional queries (payment confirmation, booking creation) always read from the primary.

*What this reveals:* Whether the product has read scaling capacity and if time-sensitive queries might read stale data from replicas.

## W4. Real product examples

---

### BrightChamps — the MongoDB operational risk

**The architecture:**
- MongoDB runs on self-hosted EC2 instances
- Flagged as "operational risk" vs. managed MongoDB Atlas
- No backup schedule documented
- No RPO or RTO specified for MongoDB-backed services

**The risk exposure:**

| Risk | Impact |
|------|--------|
| Services using MongoDB not fully documented | Cannot enumerate which services depend on which database |
| EC2 instance failure | No automatic failover; manual provisioning, install, and restore required |
| Missing backup schedule | Data on failed instance may be permanently unrecoverable |

**Quantified impact:**

If MongoDB stores class scheduling, quiz results, or teacher availability:
- **Service impact:** Features unavailable during peak class hours until manual recovery
- **Recovery timeline:** 2–6 hours (provision EC2 + restore MongoDB + validate + update connection strings)
- **Data at risk:** Everything written since last successful backup

**The fix:**

MongoDB Atlas (managed) provides:
- Automated backups with PITR
- Multi-AZ replication
- Automatic failover
- **Migration cost:** 2–4 weeks engineering (data migration + connection string updates)

⚠️ **Risk:** Cost of not fixing = one EC2 failure during business hours could render core features unavailable for 4+ hours

**PM framing:**
This is not abstract infrastructure. Ask engineering:
1. Which features currently store data in MongoDB?
2. What is the user impact if those features become unavailable for 4 hours?
3. Is that impact acceptable given the 3-week migration cost?

---

### AWS RDS Multi-AZ — what protected recovery looks like

**What AWS provides automatically:**

| Capability | Detail |
|-----------|--------|
| Replication | Synchronous to standby in different AZ |
| Failure detection | Automatic; no human intervention required |
| DNS update | Application connection string unchanged; AWS points to new primary |
| Failover time | 60–120 seconds including DNS propagation |
| PITR | Enabled by default; restore to any second in past 7 days (up to 35 days configurable) |

**What this means for a PM:**

A data center hardware failure causes:
- **Write operations:** 60-second interruption during failover
- **Read operations:** Unaffected (read replicas continue)
- **User experience:** Brief write errors, then full service restored automatically

**Without Multi-AZ (Single-AZ):** Same hardware failure = 30–60 minute outage while AWS provisions replacement

**Cost comparison (AWS RDS MySQL, approximate):**

| Configuration | Cost/month | Use case |
|---------------|-----------|----------|
| Single-AZ (db.t3.medium) | ~$50 | Non-critical features |
| Multi-AZ (db.t3.medium) | ~$100 | Failover protection (2× cost) |
| Read replica (db.t3.medium) | ~$50 per replica | Read scaling without failover |

⚠️ For any feature handling payments or bookings: the $50/month additional cost for Multi-AZ is the cheapest SLA insurance available.

---

### Stripe — RPO of zero for financial data

**What they built:**
- Payment data in PostgreSQL with synchronous replication across multiple AZs
- Ledger model: append-only, immutable records
- Failover promotes a replica that contains every transaction the primary had

**Their recovery objectives:**

| Metric | Value | Constraint |
|--------|-------|-----------|
| RPO | Approaches zero | Synchronous replication; no write acknowledged until on multiple replicas |
| RTO | < 30 seconds | Primary region failure |
| Multi-region failover | Hot standbys | Geographically separate regions |

> **RPO of zero principle:** For financial data, RPO of zero is not aspirational—it's a regulatory requirement.

**Regulatory context:**
- UK FCA, US FinCEN, EU PSD2 all require complete transaction records
- RPO of even 1 minute = potentially losing payment events
- Data loss must be reported as incident to regulators
- Stripe's append-only ledger architecture makes this impossible by construction

**PM implication:**
Any product handling real money—even if not bank-regulated—should treat RPO for payment records as near-zero. The replication architecture must support this requirement, not the other way around.

---

### Enterprise B2B — backup guarantees as contract terms

**What enterprise customers require:**

Large enterprise contracts (EdTech, HR software, B2B SaaS) increasingly include specific business continuity clauses:

> **Common contractual language:**
> - "Vendor shall maintain an RPO of no more than 4 hours for all customer data."
> - "In the event of data loss, vendor shall restore service within 2 hours (RTO)."
> - "Backup restore tests conducted quarterly with written confirmation."
> - "Backups stored in geographically separate location from primary data."

⚠️ **Critical:** These are contractual obligations with financial penalties for breach—not best practices.

**The verification gap:**

Many enterprise contracts are signed based on "we use AWS" without verifying:
- Multi-AZ actually enabled
- Backup retention properly configured
- Restore procedures actually tested

*First test happens during actual incident at 2am when primary database fails.*

**PM takeaway:**

Before committing to specific RPO/RTO numbers in any enterprise contract, confirm with engineering:

1. What is the actual recovery architecture for each database type?
2. Have restore procedures been tested?
3. What are the realistic recovery timelines?

⚠️ **Liability risk:** The number in the contract must match what engineering can deliver—not what sales wants in the deck.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands Multi-AZ, PITR, RPO/RTO math, read replica tradeoffs, and the managed vs self-hosted cost model.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### "We have backups" — assumption that was false

**What happened:** An engineering team runs monthly backups to S3 and assumes they're protected. Eighteen months later, a production incident requires a restore — but the backup file is corrupted. Investigation reveals: S3 uploads failed silently for four months, the monitoring alert was misconfigured, and the most recent valid backup is 22 weeks old. Production data from five months is gone.

⚠️ **The actual failure:** "We have backups" is not a backup strategy.

**A backup strategy requires:**
- Backup frequency
- Backup validation (automated checksum or restore test)
- Monitoring with alerting on failure
- Retention policy
- Recovery procedure documentation

**PM prevention role:** Ask "when was our last restore test?" *before* an incident. The PM who asks this discovers a corrupted backup in a test environment, not during real failure.

---

### Read replica routing that caused stale billing data

**What happened:** A team adds a read replica to reduce primary database load and routes all reads to it. A user pays; the payment Lambda writes to primary; the confirmation screen reads from the replica (3 seconds behind). User sees old balance. Support ticket: "I was charged but my credits didn't update."

⚠️ **The actual failure:** Read-after-write consistency violation — not a payment code bug.

**Root cause:** Read replicas introduce a new requirement that is *not* an engineering default — it's a **product decision**.

| Query Type | Source | Tolerance | Example |
|---|---|---|---|
| Read-after-write | Primary | Requires fresh data | "Show me my balance after I paid" |
| Historical reads | Replica | Tolerates lag | "Show me my historical class report" |

**PM prevention role:** Specify in the feature spec which queries read from primary and which read from replica. This is a product requirement, not an infrastructure choice.

---

### MongoDB migration that revealed missing data

**What happened:** During migration from EC2 to Atlas, validation discovers 14,000 quiz result records from a 6-week period are absent. Investigation: a cron job meant to backup and prune old data had a bug — it pruned live data instead. Nobody noticed because MongoDB isn't the primary reporting store; missing records weren't in any dashboard. Data loss went undetected for 8 months.

⚠️ **The actual failure:** Silent data loss — hardest failure to catch because it has no alert.

**PM prevention role:** Data stored outside the primary monitoring perimeter needs explicit integrity monitoring:

- Row count alerts
- Expected-vs-actual comparisons
- Periodic spot audits

**Key insight:** Most teams discover silent data loss during migrations, not before. Make the audit proactive, not reactive.

## S2. How this connects to the bigger system

### ETL Pipelines (02.06)

**The tension:** ETL pipelines reading from replicas must account for replication lag.

| Scenario | Data Freshness | Acceptable? |
|----------|---|---|
| Weekly report from read replica | 5 minutes behind | ✅ Yes |
| Real-time dashboard from read replica | 5 minutes behind | ❌ No |

**What PMs must specify:** Does this pipeline read from primary or replica, and what is the acceptable data freshness for this pipeline's output?

---

### Schema Design Basics (02.07)

**The risk:** Long-running migrations block both primary and standby simultaneously.

| Migration Type | Primary Impact | Standby Impact | Failover Risk |
|---|---|---|---|
| Quick migration (2 min) | Minimal | Minimal | Low |
| Long-running ALTER TABLE (30 min) | Blocks writes | Blocks replication | ⚠️ High — failover unavailable during migration |

**Why it matters:** Zero-downtime migrations (02.07's 5-step pattern) are doubly critical on replicated databases. A poorly timed migration can make failover unavailable precisely when it's most needed.

---

### Caching (Redis) (02.04)

> **Redis durability trap:** Redis is not durable. Data in Redis can be lost on restart or eviction.

| Data Type | Store In Redis? | Risk |
|---|---|---|
| Session tokens (ephemeral, recoverable from DB) | ✅ Yes | Safe — DB has source of truth |
| Class balance calculations | ❌ No | Creates "zero backup, zero recovery" |
| Feature flag states | ❌ No | Loss means silent failures |

**The boundary you must define:** Explicitly decide what data lives in Redis (ephemeral, recoverable) vs. what must be persisted in the primary database.

---

### PII & Data Privacy (02.09)

⚠️ **GDPR erasure & backups:** Backups contain PII at the time of backup. A GDPR erasure request deletes PII from the live database but **does not modify existing backups**.

| Timeline | Backup State | User PII Status |
|---|---|---|
| Erasure request at T=0 | Existing backups still contain PII | Deleted from live DB |
| T=0 to T=retention window | Backups retained per policy | Still in backups |
| T > retention window | Backups deleted | Erasure complete |

**What you must do:** Disclose the backup retention period in your privacy policy *before* the first erasure request. This is defensible — but only if documented in advance.

---

### Soft Delete vs Hard Delete (02.08)

**How replication affects deletion recovery:**

| Deletion Type | Primary at 3:47pm | Replica at 3:47pm | PITR to 3:46pm |
|---|---|---|---|
| Soft delete | User marked inactive | Reflects deletion within seconds | User reappears (soft delete undone) |
| Hard delete | User removed | Reflects deletion within seconds | User reappears (hard delete undone) |

**Critical for compliance:** PITR to a pre-deletion point effectively undoes *any* delete (soft or hard). If your compliance workflow requires deletion to be permanent and auditable, this interaction must be understood and controlled.

## S3. What senior PMs debate

### RPO of zero: is it actually achievable or always an approximation?

> **RPO (Recovery Point Objective):** the maximum acceptable amount of data loss, measured as time elapsed since the last durable write.

**The synchronous replication claim:**
Synchronous replication achieves RPO of zero because the replica confirms before the primary acknowledges—no acknowledged write is lost.

**The reality:**
Between primary acknowledgment and replica disk persistence, multiple buffers exist:
- Filesystem buffer
- Network queue  
- Disk write operation

In catastrophic failure (primary *and* replica failing simultaneously during a write), the in-flight write is lost.

**Honest framing:**
Synchronous replication provides RPO measured in **milliseconds**, not truly zero.

| Category | RPO Standard | Business Impact | Infrastructure Cost |
|---|---|---|---|
| EdTech, consumer apps, B2B SaaS | Milliseconds RPO | Operationally equivalent to zero | Standard replication |
| Financial/banking systems | Hardware-level durability guarantee | Regulatory requirement | Battery-backed RAID, NVMe persistent memory |

**The senior PM debate:** For which product categories does the difference between "milliseconds" and "truly zero" actually matter? The answer shifts infrastructure costs by an order of magnitude.

---

### Chaos engineering — the only way to know if your disaster recovery actually works

> **Chaos engineering:** intentionally injecting failures into production or production-mirror systems to verify automatic recovery operates as designed.

**The problem with traditional testing:**
- Tabletop exercises ✗ (everyone rested, runbook open, ideal conditions)
- Annual restore tests ✗ (scheduled, prepared, outdated runbooks not exposed)
- Neither tells you if recovery works at 3am with a new on-call engineer and two simultaneous service failures

**The emerging practice:**
Scheduled chaos drills in production environments:
- Intentionally fail a replica
- Terminate a database instance
- Cut a service mid-load
- Verify automatic failover meets committed RTO

**Risk avoidance:** Companies discovering their failover takes 8 minutes (not 2) during a drill avoid discovering it during a real incident.

**For product teams — the ROI calculation:**

| Investment | Cost | Benefit |
|---|---|---|
| Chaos engineering framework | Engineering time for setup | Unverified SLA confidence |
| Potential user-visible errors during drills | Real but bounded errors | Dramatically reduced severity when failures occur |

**The senior PM question:** Which features have SLA commitments that are currently unverified? Prioritizing chaos testing against those features is a risk-based engineering investment, not optional infrastructure work.

---

### Replication and AI training data pipelines — a new consistency challenge

**The problem:**
Modern products that continuously train or fine-tune ML models on production data face a consistency requirement that traditional RPO/RTO frameworks don't address.

**Example scenario:**
- Model trained on replica data with 5-second lag
- Failover event causes replica to lag 30 minutes
- Training batch includes 30 minutes of "stale" data
- Result: model doesn't reflect current production state

| Use Case | Stale Data Impact | Acceptability |
|---|---|---|
| General features | Statistical noise | ✓ Acceptable |
| Financial calculations | Incorrect balances | ✗ Unacceptable |
| Medication dosing | Wrong treatment decisions | ✗ Unacceptable |
| High-stakes student assessments | Inaccurate scoring | ✗ Unacceptable |

**The unresolved question:**
Where should ML training pipelines read from?

| Option | Pros | Cons |
|---|---|---|
| **Primary database** | Accurate, reflects live state | Adds direct load to production |
| **Dedicated training replicas** | Isolated, no prod load impact | Requires additional replication tier |
| **Event streams** | Accurate, decoupled from DB | Requires event architecture investment |

⚠️ **This is not yet a settled practice.** The senior PM building AI-native features on replicated databases must ensure the engineering team has made an explicit, documented decision about training data sourcing — and that consistency implications are clearly understood.