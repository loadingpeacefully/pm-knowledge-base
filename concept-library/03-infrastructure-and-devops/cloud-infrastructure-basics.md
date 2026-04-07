---
lesson: Cloud Infrastructure Basics
module: 03 — Infrastructure & DevOps
tags: tech
difficulty: foundation
prereqs:
  - 02.10 — Data Replication & Backups: cloud regions and AZs are the physical foundation for Multi-AZ replication; understanding AZ structure clarifies why replication across zones provides fault tolerance
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
  - technical-architecture/infrastructure/infra-monitoring.md
  - technical-architecture/infrastructure/server-schola-production-new.md
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

## F1. The server that silently failed for months

### The failure: `schola-etl` and the payment trigger

BrightChamps infrastructure includes a legacy server — internal name `schola-production-new`, IP address 172.31.9.208. It's a single EC2 instance: one virtual computer rented from AWS, running in one location.

**November 22, 2023:** Two critical services crashed on this server:

| Service | Function | Failure | Detection |
|---------|----------|---------|-----------|
| `schola-etl` | Sync class data to Google Sheets (operations team) | MongoDB connection error | Discovered months later |
| Payment Instalment Trigger | Schedule Alepay instalment payments (daily, 8:45pm) | Service no longer running on port 7600 | Unknown period of failure |

⚠️ **The silent failure risk:** This is a single EC2 instance with no auto-restart, no health monitoring, and no failover. When a service crashes, it stays crashed until an engineer manually logs in, investigates, and restarts it.

### Legacy vs. modern infrastructure

| Aspect | `schola-production-new` (EC2) | Current platform (Kubernetes/EKS) |
|--------|------|---------|
| **Failure detection** | Manual (engineer notices) | Automatic (system alerts) |
| **Recovery** | Manual restart/fix | Automatic pod restart (~30 seconds) |
| **Redundancy** | None (single instance) | Multiple replicas |
| **Downtime consequence** | Hours or days | Minutes or seconds |

> **The fundamental difference:** Traditional server management requires humans to notice and fix failures. Modern cloud infrastructure is designed to recover without human intervention.

### What the PM should do when infrastructure fails

1. **Identify business impact** — Which users are affected? What features are broken? What is the operational or revenue consequence?
2. **Set priority** — P0 (page engineers now), P1 (this sprint), or P2 (backlog with timeline)?
3. **Spec the fix** — What does "fixed" actually look like? Restarting the service is a temporary patch. The fix is: restart + add a health check + add alerting so the next crash is discovered in minutes, not months.
4. **Confirm it won't recur** — Every silent failure has two problems: the failure itself, *and* the absence of monitoring that let it go undetected. Both must be addressed.

### The geography problem: Single region, global users

BrightChamps serves students across multiple countries — India, Southeast Asia, the Middle East, the Americas. Consider the latency cost:

- **Vietnam student → Singapore server:** ~100–150ms round trip ✓ acceptable
- **Brazil student → Singapore server:** ~200–300ms round trip ⚠️ noticeable latency hit

**The CDN partial solution:**

AWS CloudFront caches static assets (JavaScript, images, CSS) at edge locations worldwide. The Brazilian student loads the website from São Paulo, not Singapore.

**The API constraint:**

API calls (booking a class, joining a session, submitting a quiz) still route to primary application servers in Singapore. These cannot be cached.

> **Key insight:** Understanding cloud infrastructure means knowing which parts of the product are constrained by server location (APIs, database queries, real-time features) and which aren't (static assets, client-side rendering).

## F2. What it is — renting computing power instead of owning it

### The shift from ownership to rental

**Before cloud computing:** Every company owned its own servers in physical data centers. Provisioning meant weeks of waiting. Scaling for seasonal spikes required guessing demand correctly. Idle capacity still cost money.

**Cloud computing model:** Computing power, storage, databases, and networking are rented from a provider and accessed over the internet. You pay only for what you use. Scale up or down in minutes.

> **Cloud Computing:** The delivery of computing services (compute, storage, databases, networking) over the internet on a pay-as-you-go basis, with infrastructure managed by a third-party provider.

### The ownership vs. rental analogy

| Aspect | Owning a Car | Ride-Sharing |
|--------|--------------|--------------|
| **Maintenance** | You handle it | Provider handles it |
| **Asset idle time** | You pay regardless | You pay only when using |
| **Upfront cost** | High | None |
| **Scaling** | Slow (buy new car) | Instant (request another ride) |

Cloud computing applies the ride-sharing model to computing infrastructure.

---

## Five core cloud services

### Compute
The "brain" — runs your application code.

- **AWS EC2:** Virtual machine you configure and manage
- **AWS Lambda:** Code runs on demand; no server to manage
- **AWS EKS:** Kubernetes orchestrates containers across many machines

*Example:* BrightChamps uses all three — Lambda for background jobs, EKS for current microservices, EC2 for the legacy PHP server.

### Storage
Where files live.

- **AWS S3 (Simple Storage Service):** Infinitely scalable file storage, pay per gigabyte

*Example:* Class recordings, profile pictures, student certificates, teacher photos — all in S3.

### Database
Where structured data lives.

- **AWS RDS:** Hosts MySQL and other relational databases with tables for students, payments, bookings

Cloud databases handle backups, scaling, and redundancy so engineering doesn't have to.

### Networking
How traffic flows.

- **AWS CloudFront:** CDN (Content Delivery Network) caches content at locations worldwide

*Example:* A student in the US loads BrightChamps — CloudFront serves static files from a US server, not Singapore. Reduces latency; reduces load on origin servers.

### Messaging
How services communicate asynchronously.

- **AWS SQS (Simple Queue Service):** One service puts a message in a queue; another reads and processes it

*Example:* Class completion events, payment webhook processing, notification delivery — work that doesn't need to happen instantly and should survive if a service temporarily crashes.

---

## Geographic deployment: Regions and Availability Zones

> **Region:** A geographic cluster of AWS data centers. AWS has regions in Virginia, Ireland, Singapore, São Paulo, and more.

**Why it matters:** Choosing a region determines where your servers physically are, which affects:
- Latency for users in that geography
- Which data residency laws apply

*Example:* BrightChamps likely runs primary infrastructure in an Asia-Pacific region (Singapore or Mumbai) given its user base.

> **Availability Zone (AZ):** Within a region, a physically separate AWS data center. Singapore region has three AZs.

**Resilience strategy:** If one AZ experiences power failure or network outage, the other two continue operating. Multi-AZ deployment spreads infrastructure across two or more AZs so a single data center failure doesn't take down your service.

## F3. When you'll encounter this as a PM

### During production incidents

"The Lambda is timing out." "The EKS pods are crash-looping." "We have a CPU spike on the RDS instance." "CloudFront is returning 503s."

These are the sentences you'll hear during production incidents. A PM who understands cloud infrastructure basics can:
- Follow the conversation in real time
- Ask informed questions ("Is the RDS issue on the primary or a replica?")
- Help communicate status to stakeholders without waiting for engineering to translate

### When scoping deployment for a new market or region

**The question:** "We're launching in Brazil. What's the infrastructure plan?"

**Why this matters:** AWS has a São Paulo region. Running primary infrastructure there for Brazilian users reduces latency significantly.

**The PM's role:** Understand the cascading decisions:
- Database replication across regions
- Data residency compliance requirements
- Full stack in Brazil vs. cache-only via CloudFront

You need to know enough to ask the right questions before engineering decides.

### When evaluating cost vs. performance tradeoffs

| Decision | Cost | Performance | When it matters |
|----------|------|-------------|-----------------|
| Lambda vs. EC2 for low-frequency jobs | Lambda cheaper | Same outcome | Budget-constrained workloads |
| CloudFront | +$X per month | -40% page load time | User experience + revenue |
| Kubernetes on EKS vs. simple EC2 | Higher to run | Auto-scales during peaks | Traffic variability |

Cloud infrastructure decisions are product decisions with direct cost and user experience implications. A PM who understands these tradeoffs can engage meaningfully with engineering proposals instead of just approving them.

### When prioritizing tech debt

**The scenario:** The `schola-production-new` server is a legacy EC2 instance with failing services and no redundancy. The architecture team has flagged it as operational risk.

**Translation to product decision:**
- Which features depend on this server?
- What are users experiencing when those services fail?
- Migration cost vs. ongoing risk?

This is a PM-owned prioritization decision dressed in infrastructure language.

### When enterprise customers ask about uptime and reliability

> **SLA (Service Level Agreement):** A commitment to uptime percentage (e.g., 99.9%) backed by infrastructure capability.

**The risk:** A product running on a single EC2 instance cannot credibly commit to 99.9% uptime — any hardware failure is a manual recovery process.

**The safe commitment:** A product running on EKS with Multi-AZ RDS can commit to 99.9% because the infrastructure supports it.

Know your infrastructure before you commit to your customers.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands cloud computing as rented infrastructure, the five core services (compute/storage/database/networking/messaging), and what regions and AZs are.
# ═══════════════════════════════════

## W1. How cloud infrastructure actually works — the mechanics that matter for PMs

### Quick Reference
| Layer | What matters for PMs | Key tradeoff |
|---|---|---|
| **Compute** | EC2 vs Lambda vs EKS | Manual control ↔ Auto-scaling + reliability |
| **Geography** | Regions & AZs | User latency ↔ Data residency compliance |
| **Storage** | S3 vs RDS vs MongoDB vs Redis | Cost ↔ Query flexibility ↔ Operational risk |
| **Managed vs Self-Hosted** | Service ownership | Vendor lock-in ↔ Operational overhead |
| **CDN** | CloudFront edge locations | Static asset speed (easy) ↔ API latency (hard) |
| **Serverless** | Lambda pricing & cold starts | Per-invocation savings ↔ Startup delay |

---

**1. Compute tiers — EC2, Lambda, and Kubernetes compared**

BrightChamps uses all three compute models. Each has a different operational profile:

| Compute model | How it works | Best for | BrightChamps use | PM implication |
|---|---|---|---|---|
| **EC2** (virtual machine) | A persistent server you configure, patch, and scale manually | Long-running services, legacy workloads requiring specific OS configuration | Legacy PHP cron server (`schola-production-new`) | Requires operational maintenance; no auto-recovery; engineer must manage capacity |
| **AWS Lambda** (serverless) | Functions that run on-demand, triggered by events; AWS manages the infrastructure | Short-duration background jobs, event processing, webhooks | Payment callbacks, ETL triggers, class completion handlers | No servers to manage; auto-scales to zero; pay per invocation; cold start latency (100–1000ms) |
| **AWS EKS** (Kubernetes) | Containerized services orchestrated across a cluster of EC2 instances; pods auto-restart on failure | Persistent microservices requiring horizontal scaling and auto-recovery | All current microservices (Eklavya, Paathshala, Doordarshan, etc.) | Auto-healing (crashed pods restart in ~30s); auto-scaling; higher operational complexity than Lambda; requires Kubernetes expertise |

**Migration path:** EC2 (manual, fragile) → Lambda (event-driven) and EKS (orchestrated, resilient). The legacy PHP server is the last significant EC2 footprint.

---

**2. Regions and AZs — the geography of reliability**

> **Region:** A geographic cluster of AWS data centers. Choosing a region determines: latency for users in that geography, which data residency laws apply, and the cost of data transfer.

> **Availability Zone (AZ):** A physically separate data center within a region, connected by low-latency fiber. Multi-AZ deployment spreads infrastructure across two or more AZs — a single data center failure doesn't affect service.

**How it works:** AWS Asia Pacific (Singapore) has three AZs: `ap-southeast-1a`, `ap-southeast-1b`, `ap-southeast-1c`. An EKS cluster configured across all three AZs means if one data center loses power, two-thirds of the cluster is unaffected. The cluster scheduler moves pods from the failed AZ to healthy ones automatically.

**Latency by region (approximate round-trip from user to AWS server):**

| User location | AWS Singapore | AWS Mumbai | AWS São Paulo |
|---|---|---|---|
| India | ~50ms | ~10ms | ~250ms |
| Vietnam / Southeast Asia | ~30ms | ~60ms | ~280ms |
| Middle East | ~120ms | ~60ms | ~200ms |
| Brazil | ~250ms | ~230ms | ~15ms |
| UK / Europe | ~170ms | ~120ms | ~200ms |

**PM note:** For live video classes, application latency (API calls, chat, interactive features) should be under 100ms. CloudFront mitigates static asset latency; the primary region choice matters for API and database latency. BrightChamps serving Brazil from Singapore creates perceptible lag on interactive features.

---

**3. Storage tiers — S3, RDS, and the right tool for each data type**

| Storage type | What it holds | Access pattern | Cost model | PM implication |
|---|---|---|---|---|
| **AWS S3** | Files: class recordings, certificates, profile photos, exports | Object storage — fetch by key; not queryable | ~$0.023/GB/month + transfer costs | Cheap for large files; no schema; can't query "all recordings for teacher X" without a database index |
| **AWS RDS (MySQL)** | Structured data: students, payments, bookings, class records | Relational — SQL queries; supports joins and transactions | ~$50–500/month per instance depending on size | The primary source of truth for operational data |
| **MongoDB on EC2** | Flexible document data: variable schemas, nested structures | Document queries — fast for key lookups, slower for analytics | EC2 cost (~$30–100/month) + operational overhead | Self-hosted = operational risk; no managed backups; migration to Atlas removes tech debt |
| **Redis (in-memory)** | Cache, session state, rate limiting counters | Key-value — nanosecond reads; not persistent | ~$15–100/month for ElastiCache | Ephemeral — data lost on restart; never the primary store for critical data |

---

**4. The managed vs self-hosted spectrum — what "operational overhead" means**

Every infrastructure component exists on a spectrum from fully managed (cloud provider handles everything) to fully self-hosted (your team handles everything):

| Service type | Fully managed | Self-hosted | Annual operational cost difference |
|---|---|---|---|
| **Database** | AWS RDS — backups, patching, failover automated | MongoDB on EC2 — team owns backup jobs, version upgrades, failover scripts | ~200 engineer-hours/year per self-hosted instance |
| **Container orchestration** | AWS EKS Fargate — AWS manages the cluster nodes | EKS with self-managed nodes — team patches and scales EC2 nodes | ~100 engineer-hours/year for cluster maintenance |
| **Search** | AWS OpenSearch Service | Elasticsearch on EC2 — team manages indexing, scaling, upgrades | ~150 engineer-hours/year |
| **Caching** | AWS ElastiCache | Redis on EC2 — team manages Redis version, replication, failover | ~50 engineer-hours/year |

**BrightChamps current state:**
- ✅ RDS for MySQL (managed — correct choice)
- ⚠️ MongoDB on EC2 (self-hosted — high-priority debt item)
- ✅ EKS for Kubernetes (managed — correct choice)

**Why MongoDB on EC2 is highest priority:** Databases carry the most operational risk and consume the most engineer hours to manage safely.

---

**5. CDN and edge caching — why CloudFront matters for a global product**

BrightChamps uses AWS CloudFront to serve static assets. CloudFront has 400+ edge locations worldwide.

**Without CDN:**
- Browser requests JavaScript bundle from origin server in Singapore
- Round trip from Brazil: ~250ms

**With CDN:**
- Browser requests from nearest CloudFront edge in São Paulo
- Round trip: ~15ms

**What CloudFront caches:**
Static files — JavaScript bundles, CSS files, images, fonts, video thumbnails. Anything that doesn't change per user.

**What CloudFront doesn't help with:**
API calls — booking a class, loading a student's profile, submitting payment. These must reach the application server. Geographic proximity to the primary region still matters for API and database latency.

⚠️ **Cache invalidation risk:** When a new deployment pushes updated JavaScript, CloudFront caches must be invalidated — told to discard old files and fetch new ones. A deployment that doesn't invalidate the CDN cache means users in edge locations continue seeing the old version. This is why "clear the CDN cache" is a required step in deployment checklists.

---

**6. Serverless (Lambda) — cost model and the cold start tradeoff**

AWS Lambda charges per invocation and per execution duration — no charge when idle. For low-frequency background jobs (the kind that run once a day or in response to payment webhooks), Lambda is dramatically cheaper than a persistent EC2 instance.

**Cost comparison for a payment webhook handler:**

| Model | Cost | Trade-off |
|---|---|---|
| EC2 (t3.small, 24/7) | ~$15/month regardless of load | Always running, always available |
| Lambda (10,000 invocations/month, 200ms each) | ~$0.02/month | Cold start latency |

**The cold start problem:**

> **Cold start:** Lambda functions that haven't run recently are "cold" — AWS must initialize the execution environment, which takes 100–1,000ms before the function starts executing.

**When cold starts matter:**
- ❌ User-facing synchronous requests (API calls that block until Lambda finishes) — cold starts add perceptible latency
- ✅ Background jobs (scheduled triggers, webhook queues) — cold starts are irrelevant

**BrightChamps use case:** Lambda for background processing — payment callbacks, class completion handlers, ETL triggers. Appropriate uses: event-driven, not on the synchronous user request path.

## W2. The decisions cloud infrastructure forces

**Quick Reference**
| Decision | Default | When to override |
|---|---|---|
| Regions | Single region + CDN | >20% MAU in different region with latency complaints OR data residency requirements |
| Compute | Lambda (background) / EKS (services) | EC2 only for legacy workloads |
| Services | Always managed | Self-hosted only for legacy migrations |

---

### Decision 1: Which region(s) to deploy primary infrastructure in?

> **PM default:** Deploy primary infrastructure in the region closest to your largest user segment. Use CloudFront for global static asset delivery regardless of where primary infrastructure lives. Add a second region only when a specific user segment has latency complaints that CDN cannot solve, or when data residency regulations require it.

| | Single region (Singapore) | Multi-region (Singapore + Mumbai) | Multi-region (Singapore + São Paulo) |
|---|---|---|---|
| API latency for India | ~50ms | ~10ms — significant improvement | No change for India |
| API latency for Brazil | ~250ms — noticeable on interactive features | No change for Brazil | ~15ms — major improvement |
| Infrastructure cost | 1× | ~1.8× | ~1.8× |
| Operational complexity | Low | Medium — cross-region sync, data residency | Medium — separate deployment pipeline |
| **Threshold to add region** | Default | >20% of MAU in India with latency complaints | >20% of MAU in Latin America |

---

### Decision 2: EC2 / Lambda / EKS — which compute model for a new service?

> **PM default:** Lambda for event-driven background jobs (webhooks, scheduled tasks, ETL triggers) under 15 minutes duration. EKS for persistent microservices requiring high availability and horizontal scaling. EC2 only for legacy workloads that cannot be containerized — never for new production services.

| | AWS Lambda | AWS EKS (Kubernetes) | AWS EC2 |
|---|---|---|---|
| Auto-recovery on crash | Yes — function reinvokes automatically | Yes — pods restart in ~30s | No — engineer must intervene |
| Cold start latency | 100–1000ms on first invocation | None — persistent containers | None |
| Scaling | Automatic — scales to millions of concurrent invocations | Configurable auto-scaling based on CPU/memory | Manual — engineer must add instances |
| Operational overhead | Near-zero | Medium — cluster management | High — full server management |
| Cost model | Per-invocation; free when idle | Hourly for cluster + instances | Hourly for instances (charged when idle) |
| **Default** | **Background jobs, event handlers, scheduled tasks** | **Persistent APIs, microservices, user-facing services** | **Legacy only — never new production** |

---

### Decision 3: Managed cloud service vs self-hosted for a new infrastructure component?

> **PM default:** Always use managed cloud services for new production deployments. Self-hosted components create ongoing operational debt that grows with the team and the platform. The cost savings of self-hosted rarely exceed the cost of engineering time to maintain, monitor, and recover from failures.

| | Managed (RDS, ElastiCache, Atlas) | Self-hosted (EC2 instances) |
|---|---|---|
| Uptime during hardware failure | Automatic failover — minutes | Manual recovery — hours |
| Backup strategy | Included, automated, validated | Must build, monitor, maintain |
| Version upgrades | Managed maintenance windows | Engineering team owns patching |
| Incident response | AWS handles hardware layer | On-call engineer paged for disk failures |
| True annual cost | Subscription cost | Subscription cost + ~200 engineering hours |
| **Default** | **Always for new production workloads** | **Legacy only — migration target, not starting point** |

⚠️ **Operational debt warning:** Self-hosted infrastructure often appears cheaper initially but compounds maintenance costs over 18–24 months as the platform scales.

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **1. What region is our primary infrastructure in, and what's the latency to our top 3 user geographies?** | Whether the current region choice is appropriate for the user base and whether there's a latency problem affecting interactive features. |
| **2. When a service pod crashes in Kubernetes, what actually happens?** | Whether auto-recovery is configured and tested. |
| **3. For the legacy EC2 server — what services are still running on it, and which are failing?** | Whether there are currently broken services affecting users that nobody is monitoring. |
| **4. What monitoring is in place to detect when a service goes down? How quickly do we get alerted?** | Whether the monitoring coverage is complete or whether failures go undetected for days or months. |
| **5. Does CloudFront cache our static assets? When was the CDN invalidation last tested after a deployment?** | Whether users are getting stale versions of the application after deployments. |
| **6. What's the monthly AWS bill by service? Which services are the top 3 cost drivers?** | Whether cloud costs are understood and managed, or whether the bill is a surprise each month. |
| **7. Is the MongoDB on EC2 on a migration path to Atlas? What's the timeline?** | Whether the highest-risk infrastructure item is being actively addressed. |

---

### Question 1: Region & Latency

**What this reveals:** Whether the current region choice is appropriate for the user base and whether there's a latency problem affecting interactive features.

**Good answer looks like:**
- Names the region (e.g., `ap-southeast-1` Singapore)
- Provides measured latency (not estimates) to key markets
- Either confirms acceptability or flags a migration plan

---

### Question 2: Pod Crash Behavior

**What this reveals:** Whether auto-recovery is configured and tested.

**Good answer looks like:**
- "Kubernetes detects the crash within seconds, restarts the pod automatically, traffic is briefly interrupted (~30 seconds), no engineer is paged unless restarts are looping."

**Red flag:**
- Answer describes a manual process → product has lower reliability than EKS should provide

---

### Question 3: Legacy EC2 Services

**What this reveals:** Whether there are currently broken services affecting users that nobody is monitoring.

**Known failures:**
- `schola-etl` (DOWN since Nov 2023)
- Payment instalment trigger (FAILING)

**Good answer looks like:**
- Confirms awareness of these failures and has a timeline for migration or decommission

---

### Question 4: Monitoring & Alerting

**What this reveals:** Whether the monitoring coverage is complete or whether failures go undetected for days or months.

**Good answer looks like:**
- "New Relic and Kibana monitor all EKS services"
- "Alerts go to Slack within 2 minutes of a pod crash-looping"
- "The legacy EC2 server has separate uptime monitoring"

**Red flag:**
⚠️ Answer is "we check Kibana manually" → condition for multi-month undetected failures (e.g., `schola-etl` was down for months with no alert)

---

### Question 5: CDN & Stale Assets

**What this reveals:** Whether users are getting stale versions of the application after deployments.

**Good answer looks like:**
- "Yes, CloudFront caches all static assets"
- "Our deployment pipeline invalidates the CDN cache automatically"
- "We tested this last sprint and the invalidation completed in under 5 minutes"

**Red flag:**
⚠️ "We think so" or no invalidation step in deployment pipeline → user-facing bug risk

---

### Question 6: Cloud Cost Attribution

**What this reveals:** Whether cloud costs are understood and managed, or whether the bill is a surprise each month.

**Good answer looks like:**
- Names the top 3 cost drivers (typically EC2/EKS, RDS, data transfer)
- Confirms tagging by service so costs can be attributed
- Shows month-over-month trends

**Context:** For a product scaling internationally, cloud costs can grow faster than revenue if unmonitored.

---

### Question 7: MongoDB Migration Plan

**What this reveals:** Whether the highest-risk infrastructure item is being actively addressed.

**Good answer looks like:**
- "We're migrating MongoDB to Atlas in Q[X]"
- "The migration plan includes data migration, connection string updates, and a parallel-run validation period"

**Red flag:**
⚠️ Answer is "it's in the backlog" → operational risk is unmanaged

## W4. Real product examples

### BrightChamps — the legacy EC2 server with silent failures

**What it is:** A single EC2 instance (`schola-production-new`, IP `172.31.9.208`) running PHP cron jobs — class reminders, Zoom license management, SSL renewal, and legacy ETL integration. It is not part of the EKS cluster. It has no automatic restart capability. It has no auto-scaling. Services that crash stay crashed until an engineer manually intervenes.

**The failures documented in the KB:**

| Service | Failure | Duration | Impact |
|---|---|---|---|
| `schola-etl` (Google Sheet sync) | DOWN — MongoDB connection error | Since Nov 22, 2023 (months) | Operations team Google Sheets not updated |
| Payment instalment trigger | FAILING — port 7600 connection refused | Unknown period | Alepay instalment schedules not executing |

**Why this happens on EC2 but not EKS:**

> **EKS (Kubernetes):** Has a built-in controller that monitors pod health and restarts crashed pods automatically.

> **EC2:** A virtual machine with no built-in restart mechanism. If the process running inside crashes, the EC2 instance continues running but the process is gone. Without an external health check (watchdog process, load balancer health check, or service supervisor), the crash is invisible.

**PM framing for prioritization:**

"The legacy EC2 server has two currently-failing services — a Google Sheets sync and a payment instalment trigger. Both have been failing for an unknown period. We don't know what business processes are affected because we don't have complete documentation of what depends on these services. I'm proposing we spend one sprint doing a complete audit of the server's dependencies, document the business impact of each failing service, and either restart the services or formally decommission the server."

---

### BrightChamps — the EKS advantage in practice

**What they built:**

The current microservices — Eklavya, Paathshala, Doordarshan, Payments, Hermes, and others — run on AWS EKS. Kubernetes manages the cluster: scheduling pods across multiple nodes and AZs, restarting failed pods, and scaling based on load.

**The monitoring stack:**

- **APM:** New Relic for application performance monitoring
- **Logs:** Kibana for log aggregation
- **Cluster visibility:** Lens for Kubernetes cluster visibility
- **Distributed tracing:** OpenTelemetry (added to payment-structure service)
- **Roadmap:** SLO dashboards in New Relic for each microservice (p95 latency, error rate) — a step toward quantified reliability commitments

**What Kubernetes provides that EC2 doesn't:**

| Capability | Behavior | Business impact |
|---|---|---|
| **Pod restart** | Crashed payment service pod detected and restarted in ~30 seconds | Service recovers automatically; no engineer pager |
| **Rolling deployments** | New code deployed pod by pod; bad deploys trigger automatic rollback | Safer deployments with faster incident recovery |
| **Horizontal pod autoscaling** | During peak class scheduling windows, Kubernetes adds pod replicas; removes them after peak | Cost efficiency + performance during traffic spikes |
| **Multi-AZ scheduling** | Pods spread across multiple AZs; single data center failure doesn't take down entire service | Protection against ~99% of cloud provider failures |

---

### AWS — how regions and AZs affect real product decisions

**The structure:**

AWS operates 33 geographic regions (2024), each with 2–6 AZs.

**Common product-relevant regions:**
- `us-east-1` (Virginia)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)
- `ap-south-1` (Mumbai)
- `sa-east-1` (São Paulo)

**Why region choice is a product decision, not just an engineering one:**

| Scenario | Region choice | Rationale |
|---|---|---|
| **EU education product** | `eu-west-1` or EU-only | GDPR requires EU student data stored in EU; storing in Singapore may not satisfy enterprise customers' data residency requirements |
| **India market entry** | `ap-south-1` (Mumbai) vs `ap-southeast-1` (Singapore) | Mumbai reduces latency by 40ms for Indian users — measurable for real-time class interactions |
| **India regulatory compliance** | `ap-south-1` (Mumbai) only | DPDP Act may require Indian user data stored in Indian data centers; AWS Singapore does not satisfy this |

**The AZ resilience model:**

> **Multi-AZ deployment:** AWS guarantees AZs within a region are isolated from failures in other AZs. Protects against ~99% of cloud provider failures.

> **Single-AZ deployment:** Exposed to data center-level incidents — approximately once every 1–2 years for any specific AZ.

⚠️ **Risk:** Single-AZ deployments are a business continuity vulnerability. Prioritize Multi-AZ architecture for any production service.

---

### Enterprise B2B — data residency as an infrastructure requirement

**What enterprise customers require:**

Large enterprise contracts — particularly with government school systems, banks, and healthcare companies — often specify where data must be stored.

- "All student data must be processed and stored within India."
- "No EU personal data may leave the EU."

These requirements are enforced by law in some jurisdictions (GDPR for EU data, DPDP for Indian data) and by contract in others.

**The infrastructure implication:**

A product that runs all infrastructure in Singapore cannot satisfy a "data must remain in India" requirement.

**Options:**
1. Deploy a full stack in AWS Mumbai for Indian enterprise customers
2. Use AWS Mumbai as the primary region for Indian users
3. Store and process user data in the compliant region with a separate deployment pipeline (most common pragmatic solution)

**What a PM must answer before an enterprise deal closes:**

- Which AWS regions do we currently run production infrastructure in?
- Which services process or store customer data?
- Can we guarantee that Indian customer data stays in AWS Mumbai and never transits through Singapore?
- What would it cost to add a second region for data residency compliance?

⚠️ **Business risk:** These are infrastructure questions with enterprise revenue implications. A PM who can't answer them before the first enterprise call loses deals to competitors who can.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands EC2/Lambda/EKS compute tiers, regions and AZs, managed vs self-hosted, CDN mechanics, and the cost model for cloud services.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Silent failure with no alerting

**The failure:** The `schola-etl` service was down for months before anyone noticed. Services crash silently; no alert fires; users and operations teams adapt their workflows without reporting the missing data; the failure is discovered months later during an audit or a new team member investigating the system.

> **Silent failure:** A service stops producing output but no one detects it because there is no active monitoring mechanism—only passive dashboards no one checks regularly.

**PM prevention role:**

| Requirement | What it prevents |
|---|---|
| Health check with alerting (not just dashboards) | Months-long outages going undetected |
| Business-critical services checked at expected frequency | Degraded data pipelines flying under the radar |
| Alert if daily ETL is missing today's output | Reporting gaps |
| Alert if payment trigger fails to fire by expected time | Payment processing delays |

⚠️ **Critical:** Add "monitoring and alerting specification" to acceptance criteria for every background service. This is not assumed; it must be explicit.

---

### Deployment that broke the CDN cache

**The failure:** A team deploys a new frontend with a significant UI change. All tests pass, the service is healthy. Three hours later, support receives tickets: "The app looks broken for me" from users in Southeast Asia, Australia, and Japan. The engineers in India see the new UI correctly. Root cause: the CDN cache invalidation step was skipped in the deployment runbook. Edge locations in Asia still have the old JavaScript bundle cached—in some cases for up to 24 hours.

> **CDN cache invalidation:** The automated process of clearing cached assets across all edge locations so users receive the latest version, not stale files from regional servers.

**PM prevention role:**

- CDN cache invalidation is a **deployment step**, not optional cleanup
- Every frontend asset deployment must include **automated CDN invalidation**
- Geographic variance in user experience means your browser test is insufficient
- Add to release checklist: "Verify CDN invalidation completed for all edge regions"

⚠️ **Geographic blind spot:** If your team only tests from one region, you will miss cache issues affecting other geographies until customers report them.

---

### Cloud cost spike nobody saw coming

**The failure:** An engineering team adds S3 lifecycle rules to archive old class recordings. The configuration accidentally applies to *all* S3 buckets, including the actively-accessed profile photo bucket. AWS charges $0.03/GB for Glacier retrievals vs $0.0004/GB for Standard access. As millions of profile photo loads hit the archive retrieval fee, the monthly S3 bill spikes from $800 to $14,000 in 30 days. Nobody notices until the invoice arrives.

| Cost dimension | What went wrong |
|---|---|
| Storage access pattern | Changed without impact modeling |
| Blast radius | Configuration applied too broadly |
| Detection timing | Only discovered at invoice time (30 days late) |

> **Cloud cost governance:** The practice of reviewing infrastructure changes for their financial impact before deployment and monitoring cloud spend regularly.

**PM prevention role:**

- Ask "what does this do to our AWS bill?" for every infrastructure change
- Require cost impact estimates for changes that modify:
  - Storage access patterns
  - Compute capacity
  - Data transfer routing
- Conduct monthly AWS bill reviews broken down by service as a standard ritual
- Treat cost surprises as a product ownership gap, not an engineering problem

⚠️ **Finance gap:** Cloud cost governance is a PM responsibility. Missing it means you approve financial decisions without understanding their impact.

## S2. How this connects to the bigger system

| System | Connection | Why it matters |
|--------|-----------|-----------------|
| **Data Replication & Backups (02.10)** | AZ architecture is the physical foundation for Multi-AZ replication | AWS guarantees failover protection because AZs are physically independent with separate power, cooling, and network infrastructure |
| | | Region-level failures require multi-region replication—Multi-AZ only protects against AZ-level failures |
| **CI/CD Pipelines (03.04)** | Deployments on EKS use rolling update strategies | Kubernetes deploys new pods one at a time while old pods serve traffic, enabling zero-downtime deployments impossible on single EC2 instances |
| | | Deployment pipeline directly interacts with cloud infrastructure: regions, clusters, CDN caches, Lambda functions |
| **Containers & Docker (03.02)** | EKS runs Docker containers | Kubernetes watches container health across a cluster of EC2 nodes and restarts failed containers automatically |
| **Queues & Message Brokers (03.06)** | AWS SQS is the messaging layer in BrightChamps | Decouples services: when a class completes, teacher feedback triggers SQS messages that credit deduction Lambda consumes asynchronously |
| | | SQS persists messages even if consumer crashes, handles retries automatically, scales without capacity planning |
| **Monitoring & Alerting (03.09)** | Monitoring stack (New Relic, Kibana, Lens) is itself cloud infrastructure | Must be deployed, configured, and maintained |
| | | Infrastructure monitoring (server running?) ≠ application monitoring (application processing requests?) |
| | | EC2 server can be "running" while a service on it is crashed; must monitor application health, not just infrastructure |

## S3. What senior PMs debate

### Multi-cloud vs AWS-committed: vendor lock-in as a product strategy decision

**The situation:** BrightChamps is deeply integrated with AWS-specific services: EKS, SQS, Lambda, RDS, CloudFront, S3. Migration to another cloud provider would require rewriting the messaging layer, replacing managed database services, re-architecting serverless functions, and rebuilding CDN configuration.

> **Vendor lock-in:** Dependence on a specific provider's services, making switching costly and difficult.

**The debate:**

| Consideration | Multi-cloud approach | AWS-committed approach |
|---|---|---|
| **What it means** | Maintain portability across AWS, GCP, Azure using cloud-agnostic abstractions | Optimize for AWS-specific services and features |
| **Engineering cost** | High upfront + ongoing complexity (standard Kubernetes, open-source databases, multi-provider IaC) | Lower upfront, simpler operations |
| **Payoff** | Provider negotiating leverage; protection against provider outages; regulatory flexibility | Faster feature shipping; lower operational burden |
| **Risk profile** | Complexity risk | Concentration risk |

**The counterargument:** AWS reliability is high enough that provider-level outages affecting the entire product are rare (~1 per 3–5 years for most regions). The engineering cost of multi-cloud portability, spread over those years, almost always exceeds the cost of an outage event itself.

**The threshold question:** At what company size and at what enterprise customer concentration does vendor lock-in become a material business risk?

---

### FinOps as a product discipline: who owns the cloud bill?

Cloud infrastructure costs are variable — they scale with usage, can spike unexpectedly, and are directly affected by product decisions (data caching, log retention, compute tier selection).

> **FinOps (Financial Operations for cloud):** Treating cloud cost as a first-class product metric by setting cost budgets per service, attributing costs to product features, and building cost efficiency into engineering decisions from the start.

**The cost visibility problem:** In many companies, engineering owns infrastructure decisions and finance owns the budget, with no one explicitly owning the intersection.

**Example metric:** A product generating $1M in annual recurring revenue and spending $300K on AWS operates at a 30% infrastructure-to-revenue ratio. Whether that ratio stays at 30%, drops to 10%, or grows to 50% as the product scales is a direct function of infrastructure decisions made during feature development.

**The senior PM debate:** Should cloud cost per feature be tracked on the same dashboard as conversion rate and retention?

- **Companies that do:** Build explicit tracking — every new feature includes an infrastructure cost estimate, and the PM is accountable for the feature's margin contribution. These companies tend to have stronger gross margin profiles at scale because infrastructure decisions are made with full economic visibility, not just technical preference.
- **Companies that don't:** Make infrastructure decisions based on technical preference alone, often discovering margin impact only when scaling.

---

### AI inference infrastructure — managed APIs vs self-hosted GPUs

Adding AI features introduces an entirely new infrastructure cost model. Standard cloud services charge for compute time, storage, and data transfer — predictable and linear with usage. AI inference charges per token (input + output) at rates that scale with model size and context length.

**The cost and capability tradeoffs:**

| Approach | Cost model | Latency | Privacy | Control | PM implication |
|---|---|---|---|---|---|
| **Managed API** (OpenAI, Anthropic, Google Gemini) | Per token — $0.003–$0.06/1K tokens depending on model and tier | Low for small models; 200–800ms for large | PII sent to third-party API | None — provider owns model and infrastructure | Zero operational overhead; per-request cost grows linearly with usage; PII leaves your infrastructure |
| **AWS Bedrock / Google Vertex AI** | Per token or per inference request — similar to direct APIs | Similar to managed APIs | Data stays in your cloud account | Model selection but not fine-tuning | Compliant data residency; still per-token cost; limited to available models |
| **Self-hosted GPU** (EC2 GPU instances, Lambda GPU) | Hourly compute — $1–$35/hour per GPU instance depending on size | Fastest — no network hop to third party | Full control — data never leaves | Full — can fine-tune, modify, optimize | High operational complexity; economic only at >100K daily inferences; requires ML engineering to manage |

**The cost math that surprises PMs:**

A student takes 30 classes per month. Each class completion triggers an AI-generated feedback report (500 input tokens + 300 output tokens = 800 tokens). At $0.01/1K tokens (GPT-4o pricing):
- Cost per report: $0.008
- Cost per student per month: $0.24
- At 100,000 active students: **$24,000/month in inference costs** — added to the AWS bill without any new infrastructure

⚠️ **Critical PM question before adding AI to any feature:** "What is the token budget per user interaction, and what does that cost per 1K users?" If the answer isn't known before launch, the AI feature's margin contribution is unknown until the invoice arrives.

---

### Serverless and the architectural boundary: where should Lambda end and Kubernetes begin?

BrightChamps uses Lambda for background jobs and EKS for persistent services. This boundary is clear today, but becomes contested as the platform grows.

**Why the boundary matters:** Lambda's 15-minute execution limit, cold start latency, and per-invocation cost model make it unsuitable for:
- Video transcoding jobs that take 20 minutes
- Batch analytics queries that take 3 minutes but run 10,000 times per day
- Services with predictable high traffic where a warm pool of containers is more cost-efficient than per-invocation Lambda

**The emerging debate:** AWS Lambda SnapStart, container-based Lambda, and Lambda extensions are progressively blurring the line between serverless and containers.

**The question a senior PM should ask before building a new feature:**

Not: "Is this Lambda or Kubernetes?"

Instead: "What are the execution characteristics of this workload, and which compute model's cost and reliability profile fits best?"

This requires specifying before engineering chooses the compute model:
- Execution duration
- Concurrency patterns
- Cold start tolerance
- Traffic predictability