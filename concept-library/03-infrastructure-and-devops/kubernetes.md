---
lesson: Kubernetes
module: 03 — Infrastructure & DevOps
tags: tech
difficulty: foundation
prereqs:
  - 03.02 — Containers & Docker: Kubernetes orchestrates containers; understanding what a container is (image, registry, resource limits) is required before understanding what Kubernetes does with them
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
  - technical-architecture/infrastructure/infra-monitoring.md
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

## F1. The system that keeps the lights on

### The Problem: Manual Infrastructure at Scale

**7:00pm Sunday. BrightChamps booking surge.**

| Without Automation | With Automation |
|---|---|
| Engineer notices spike (5 min delay) | System detects CPU spike (15 sec) |
| Manually logs into AWS | Auto-triggers scaling policy |
| Adds servers manually | Scales from 5 → 25 pods |
| Waits for startup (varies) | New pods live in <10 sec each |
| **Result:** Errors, lost bookings | **Result:** Zero errors, all bookings succeed |
| **Window:** 10–15 min process vs. 20 min booking window | **Window:** Complete before peak demand |

### The Problem: Risky Deployments

**2:00pm Tuesday. Service update rollout.**

| Old Deployment | With Kubernetes Rolling Update |
|---|---|
| Take service down | New pods start with new code |
| Deploy update | Old pods removed one-at-time |
| Restart service | Health checks verify each new pod |
| **Downtime:** 2–5 minutes | **Downtime:** Zero |
| **User impact:** Active sessions interrupted | **User impact:** Seamless, unnoticed |
| **Deploy time:** Varies with outage risk | **Deploy time:** 4 minutes, predictable |

### What Kubernetes Actually Does

> **Kubernetes:** A system that watches every running service, continuously compares actual state to desired state, and automatically reconciles the difference.

**Its core jobs:**
- **Scaling:** Adds pods when load increases; removes them when it drops
- **Health management:** Restarts crashed pods automatically
- **Rolling updates:** Replaces old code with new code without downtime
- **Load balancing:** Routes traffic across healthy pods

**In this case:** Running on AWS EKS (Elastic Kubernetes Service), managing the Paathshala class scheduling service and Eklavya student service.

## F2. What it is — the hotel manager for your services

### The Hotel Analogy

Running 11 microservices in production is like running a hotel:

| Hotel Element | Microservices Parallel |
|---|---|
| Rooms | Servers |
| Guests | User requests |
| Staff | Containers |
| Continuous turnover | Always-on operations |

The hotel can't close to rearrange. New guests arrive while existing ones sleep. Staff get sick and need replacing. Busy seasons require opening more floors.

**Kubernetes is the hotel manager.** It handles all of that coordination automatically.

### How It Works in Practice

You tell Kubernetes: *"I want the Paathshala service running on 5 pods, always."*

Kubernetes ensures:
- ✓ 5 pods are always running
- ✓ If one crashes, it starts a replacement before anyone notices
- ✓ If demand spikes, it opens more rooms
- ✓ If you deploy a new version, it replaces rooms one at a time while guests keep checking in

### Core Kubernetes Terms

> **Pod:** The smallest running unit. A pod is one running container (or occasionally a tightly coupled group of containers). When you think "one instance of the Paathshala service is running," that's one pod.

> **Node:** A server (EC2 instance) that runs pods. BrightChamps' EKS cluster has multiple nodes. Kubernetes decides which pods go on which nodes based on available resources.

> **Deployment:** The declaration of what you want. "Run 5 copies of Paathshala, using image `paathshala:v2.4.1`, with these resource limits." Kubernetes continuously works to make reality match the deployment specification.

> **Cluster:** The complete Kubernetes environment: all nodes, all pods, all deployments, all services. BrightChamps has one EKS cluster running all 11 microservices.

### What Kubernetes Is NOT

Kubernetes does **not**:
- Build your code
- Decide what your service does
- Handle the database
- Manage anything except running containers

Kubernetes **only** manages:
- Where containers run
- How many are running
- What happens when something goes wrong

## F3. When you'll encounter this as a PM

### Scoping a deploy

**Scenario:** Engineers mention "rolling update" or "recreate deploy"

> **Rolling Update:** Replaces pods one at a time; no downtime
> **Recreate Deploy:** Kills all pods and starts fresh; expect downtime

**PM Action:**
- For recreate deploys: schedule during off-peak hours + add maintenance notice
- **Ask:** "Is there a way to make this migration backward-compatible so we can use a rolling update instead?"
  - *What this reveals:* Whether downtime is avoidable or architectural

---

### Service is "crashing and restarting"

**Scenario:** Engineer says "Hermes service is in a crash loop"

> **Crash Loop:** Kubernetes automatically restarts a pod because it keeps failing its health check; crashes can be invisible until they compound

**PM Action:**
- **Ask two questions:**
  1. "How long has the crash loop been happening?"
  2. "Are users experiencing errors right now?"

| If users are affected | If users are not affected |
|---|---|
| **Priority: P1** | **Priority: Urgent, not critical** |
| | |

- **Escalate:** Assign an engineer to root-cause now; set "no new work until resolved" policy on that service

---

### Discussing peak load capacity

**Scenario:** "Can the system handle the back-to-school surge?"

This is partly a Kubernetes question:
- Does the Horizontal Pod Autoscaler have permission to scale to enough pods?
- Are there enough nodes in the cluster to schedule them?

**PM Action:**
- **Two weeks before any planned surge, ask:**
  - "What is the current HPA max replica setting for [service], and what is the cluster's available headroom?"
  - *What this reveals:* Whether you need a load test or have sufficient capacity
- ⚠️ **Don't rely on Kubernetes auto-scaling to discover limits during a live event**

---

### Deploy takes longer than expected

**Scenario:** Rolling update is slower than anticipated

> **Deploy Duration Drivers:**
> - Number of pods in the deployment
> - `maxUnavailable` setting (how many pods replace per batch)
> 
> *Example:* 11-pod deployment replacing 2 pods at a time = 5–6 replacement cycles

**PM Action:**
- **Before release, ask:**
  - "How many pods in this deployment?"
  - "What's the maxUnavailable setting?"
  - *What this reveals:* Deploy window length (e.g., 3 minutes vs. 20 minutes)
- Adjust communication plan based on deploy window duration

---

### Incident postmortem mentions "pod eviction" or "OOMKilled"

**Scenario:** Service degradation tied to Kubernetes resource management

| Term | Cause | Takeaway |
|---|---|---|
| **OOMKilled** | Pod exceeded its memory limit | Memory limit was set too low |
| **Eviction** | Node under pressure (too many pods or another service consuming unexpectedly) | Either too many pods on too few nodes, or resource contention |

⚠️ **Neither is a code bug** — both are Kubernetes-managed resource events

**PM Action:**
- Add to postmortem action items: "Review resource limits for this service"
- Schedule sprint work to fix limits or node allocation
- *What this reveals:* This requires infrastructure work, not just monitoring
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level
# ═══════════════════════════════════

## W1. How Kubernetes actually works — the mechanics that matter for PMs

### Quick Reference
| Concept | What PMs need to know |
|---------|----------------------|
| Desired state | You declare what you want; Kubernetes enforces it continuously |
| Pod scheduling | Pods need CPU/memory reserves; if cluster is full, pods stay Pending |
| Rolling updates | Default strategy; zero downtime if readiness probes work correctly |
| Health checks | Liveness = restart if dead; Readiness = remove from traffic if not ready |
| HPA | Auto-scales pods based on CPU/memory; misconfiguration causes performance issues |
| Observability | Lens shows pod status; New Relic shows app metrics |

---

### 1. The desired state model — Kubernetes as a control loop

Kubernetes operates on a principle called desired state: you declare what you want, and Kubernetes continuously reconciles reality against it.

**How it works:**
- You submit a Deployment manifest: "I want 5 replicas of Paathshala, using image `paathshala:v2.4.1`"
- Kubernetes reads this, checks current state (maybe 3 pods are running), starts 2 more
- If one pod crashes, Kubernetes detects the gap and starts a replacement within seconds
- If you update to 8 replicas, Kubernetes starts 3 more
- If you change the image to `v2.4.2`, Kubernetes replaces pods one by one with the new image

> **Key concept — Desired state:**
> Your service specification is a contract, not a request. Kubernetes will always try to fulfill the declared state. The danger: if the declared state is wrong (wrong resource limits, wrong replica count, wrong image tag), Kubernetes will faithfully enforce the wrong thing.

---

### 2. Pods, nodes, and scheduling — where things actually run

When Kubernetes starts a new pod, it runs a scheduling decision: which node has enough available CPU and memory to run this pod given its resource requests?

> **Resource requests and limits:**
> A pod's **resource request** is a promise to Kubernetes. Kubernetes guarantees that requested CPU and memory are reserved on the node. If no node has enough free capacity, the pod is **Pending** — it cannot start. A cluster where all nodes are full and new pods stay Pending is a **capacity problem**: more nodes are needed.

**PM implications:**

| Scenario | What it means | Action |
|----------|--------------|--------|
| "We're at cluster capacity" | System cannot schedule new pods without adding nodes | Add nodes (costs money, takes minutes) |
| "Pod pending" errors during high traffic | Autoscaler can't find room | Pre-scale nodes proactively, not reactively |

*What this reveals:* Cluster fullness directly impacts deployment and scaling speed during peak demand.

---

### 3. Rolling updates — how deploys happen without downtime

A Deployment in Kubernetes has a `strategy` field controlling how pods are replaced.

#### Strategy comparison

| Strategy | Downtime | Risk | When to use |
|---|---|---|---|
| **RollingUpdate** | Zero (if configured correctly) | Old and new code run simultaneously during transition | Default for all services — stateless APIs |
| **Recreate** | 30–90 seconds | Predictable downtime window | Schema migrations that break backward compatibility |

#### RollingUpdate parameters

- **`maxUnavailable`**: how many pods can be down at once (e.g., 1 — only one pod is unavailable during the update)
- **`maxSurge`**: how many extra pods can be created above the desired count (e.g., 1 — one extra pod is started before one old pod is removed)

#### Deploy duration math

A 10-pod deployment with `maxUnavailable: 2`:
- Replaces 2 pods per cycle
- Each cycle = slowest pod startup + readiness probe time
- Example: 30-second startup + 15-second probe = 45 seconds per cycle
- Total: 45 seconds × 5 cycles = **~3.75 minutes expected deploy window**

**Recommendation:** Use RollingUpdate for 95% of deploys. Test backward compatibility before every deploy. Use Recreate only when explicitly required by migration.

*What this reveals:* Probe configuration directly impacts deploy speed and risk.

---

### 4. Health checks — how Kubernetes knows a pod is alive and ready

Every pod can have two health checks configured:

#### Liveness probe
**Question:** "Is this pod still alive?"
- If it fails repeatedly, Kubernetes kills and restarts the pod
- Typical probe: HTTP GET on `/health` or `/ping`
- Use case: detect deadlock or unrecoverable state

#### Readiness probe
**Question:** "Is this pod ready to receive traffic?"
- If it fails, Kubernetes removes the pod from the load balancer (no traffic, but pod is not killed)
- Typical probe: same HTTP check, but can also verify database connections, cache warming
- Use case: normal during startup; pods pass readiness before receiving traffic

> ⚠️ **Critical distinction for PMs:**
> A pod can be **alive but not ready**. This is normal during startup. A rolling update waits for new pods to pass their readiness probe before removing old ones. If a readiness probe is misconfigured (timeout too short, wrong endpoint), pods fail the probe immediately — and the rolling update stalls or causes downtime. **"The deploy is stuck" is often a misconfigured readiness probe.**

#### PM checklist before releasing services with slow startup

- Does the readiness probe timeout match actual startup time?
- Is the probe endpoint correct and responding?
- For ML models loading at startup: is the timeout set long enough?
- Example: A 45-second model load with a 10-second probe timeout = every new pod fails readiness checks

*What this reveals:* Probe misconfiguration is the #1 cause of deploy stalls and silent downtime.

---

### 5. Horizontal Pod Autoscaler (HPA) — automatic scaling

The HPA watches a metric (typically CPU utilization or memory) and adjusts the pod count automatically to keep the metric near a target.

**Example:** HPA on Paathshala configured for target 70% CPU — if CPU exceeds 70% for 30 seconds, HPA adds pods; if CPU drops below 50% for 5 minutes, HPA removes pods.

#### HPA misconfiguration risks

| Parameter | What it controls | If set too high | If set too low |
|---|---|---|---|
| **Target CPU %** | Utilization level that triggers scaling | Scale-up triggers too late; traffic errors already occurring | Unnecessary scaling; wasted cost |
| **Min replicas** | Minimum pods regardless of load | Wasted resources | Single pod = single point of failure |
| **Max replicas** | Maximum pods HPA can create | Hit capacity ceiling during peaks | Runaway cost if HPA bugs |
| **Scale-up stabilization** | Seconds before adding pods | Slow response to genuine spikes | Unnecessary thrashing |
| **Scale-down stabilization** | Seconds before removing pods (default: 5 min) | Wasted resources | Pod oscillation (add/remove/add/remove) |

**BrightChamps context:** EKS enables horizontal scaling of individual microservices. The class scheduling surge is the primary scaling event — Paathshala is the highest-risk service for HPA misconfiguration.

*What this reveals:* HPA tuning directly impacts both performance (under-scaling causes errors) and cost (over-scaling wastes money).

---

### 6. Observability — how you see what Kubernetes is doing

#### Lens
- **What:** Kubernetes dashboard tool documented in BrightChamps' infra-monitoring KB
- **Shows:** pod status (Running, Pending, CrashLoopBackOff), resource utilization (CPU/memory per pod), pod logs in real-time, deployment history
- **Role:** Primary operational view for the engineering team

#### New Relic / Kibana
- **What:** Application-level metrics and log aggregation
- **Shows:** Response time, error rate, throughput (e.g., "Prabandhan CRM API averages 1.26s")
- **Role:** Performance concerns tracked in infra-monitoring KB

#### Pod states PMs should know

| State | Meaning | Action |
|-------|---------|--------|
| `Running` | Healthy, receiving traffic | Normal operation |
| `Pending` | Cannot be scheduled | Cluster at capacity OR resource request too high |
| `CrashLoopBackOff` | Crashing repeatedly; restarting with exponential delay | Check app logs; likely code bug or resource exhaustion |
| `OOMKilled` | Exceeded memory limit; Kubernetes killed it | Increase memory limit OR fix memory leak |
| `Terminating` | Being gracefully shut down | Normal during rolling update |
| `ImagePullBackOff` | Cannot pull Docker image | Check: wrong tag, ECR permissions, network issue |

⚠️ **Watch for:** `CrashLoopBackOff` during deploys — indicates the new image has a startup bug.

## W2. The decisions Kubernetes forces

### Quick Reference
| Decision | Default | When to deviate |
|----------|---------|-----------------|
| Update strategy | Rolling updates | Only recreate for non-backward-compatible migrations with maintenance window |
| Minimum replicas | 2 per service | Critical services (Payments, Chowkidar): 3+ with HPA |
| Cost model | ~$7/pod/month | Scales with node utilization and node type |
| Config ownership | Platform sets floor, engineers tune above | Engineers propose > PM approves cost impact |

---

### Decision 1: Rolling update vs recreate — when is downtime acceptable?

**The default:** Rolling updates. Old and new versions run simultaneously, requiring API backward compatibility.

**The hard case:**
Database schema migrations that break old code (removed columns, renamed fields). Solution: stage across multiple deploys instead of one breaking change.

```
Migration sequence:
Add column → Dual-write → Remove old column
(allows old code to function throughout)
```

> **Recommendation:** Default to rolling updates. Use recreate only when forced by non-backward-compatible migration — plan a maintenance window.

**Engineer estimate to require:**  
"Can we make this migration backward compatible?" — must be part of sprint planning for any schema changes.

*What this reveals:* Whether the team is thinking about deploy risk early, not treating migrations as afterthoughts.

---

### Decision 2: How many replicas to run as a baseline?

**The tradeoff:** More replicas = higher availability but higher baseline cost. Fewer replicas = lower cost but higher blast radius per pod crash.

| Replica count | Pod crash impact | Downtime risk | Best for |
|---|---|---|---|
| 1 replica | Service unavailable | ~30 seconds until restart | Dev/staging only |
| 2 replicas | 50% capacity loss | No full outage | Standard production services |
| 3+ replicas | Minimal user impact | Negligible | Critical services (Payments, Chowkidar) |

> **Recommendation:** No production service below 2 replicas. Critical services require 3+ with HPA configured.

**⚠️ Cost-driven undercounting is a reliability blind spot:**  
A PM approving "1 replica to save cost" is accepting predictable 30-second outage windows on every deploy and crash.

---

### Decision 3: What this actually costs — the $/pod math PMs should know

**Cost structure:** You pay for EC2 nodes, not pod count. One m5.xlarge can run 10–30 pods depending on resource requests.

| Node type | vCPU | Memory | $/hr | $/month |
|---|---|---|---|---|
| t3.medium | 2 | 4 GB | $0.042 | $30 |
| m5.large | 2 | 8 GB | $0.096 | $69 |
| m5.xlarge | 4 | 16 GB | $0.192 | $138 |
| c5.2xlarge | 8 | 16 GB | $0.340 | $245 |
| g4dn.xlarge (GPU) | 4 | 16 GB + 1 GPU | $0.526 | $379 |

**Baseline pod cost:** At $138/mo per m5.xlarge and 20 pods per node = **~$7/pod/month**

#### Cost decision models

**Scenario A: Scaling from 5 → 25 Paathshala pods during surge**
- 20 pods fit on 1 node = 1 extra m5.xlarge
- 2-hour surge: $0.19/hr × 2 = **~$0.38**
- HPA-driven scaling is cheap for short bursts

**Scenario B: Running 3 replicas instead of 1 for critical service**
- Cost: ~$21/mo per service
- 5 critical services: ~$105/mo for meaningful availability improvement
- Verdict: **Worth it**

**Scenario C: GPU node for AI inference**
- Cost: $379/mo for 1 GPU node
- Your inference: $0.25 per 1000 requests
- Anthropic API: ~$8 per 1000 tokens
- Verdict: GPU nodes win at high volume; managed APIs win at low volume

> **PM approval pattern:** When an engineer requests increased memory limits, acknowledge the cost. Example: "Eklavya: 512Mi → 1024Mi" doubles memory cost (~$3–4/mo per pod). Note in infra cost tracker. Cost-blind approvals compound across 11 services.

---

### Decision 4: Who owns Kubernetes configuration — engineers or platform team?

> **Configuration dimensions:** Resource limits, replica counts, HPA settings, probe timeouts — all have cost and reliability implications.

**The ownership problem:**
- Too-low resource limits → OOMKills during traffic spikes
- Too-high limits → paying for unused capacity

| Ownership model | Speed | Consistency | Risk |
|---|---|---|---|
| Engineers own per-service config | Fast iteration | Inconsistent settings | Forgotten tuning, cost drift |
| Platform team owns all config | Slow per-service changes | Consistent defaults | Bureaucracy, suboptimal per-service tuning |

> **Recommendation:** Platform team sets minimum standards (minimum replicas, required probes, memory ceiling per service tier). Individual engineers own tuning above the floor.

**PM's role in cost governance:**
1. Engineer proposes change: "Increase Eklavya memory: 512Mi → 1024Mi"
2. PM acknowledges: "That's ~$3–4/mo per pod added. Approved, tracking in infra cost."
3. Track cumulatively across services
4. Revisit in quarterly cost review

*What this reveals:* Whether the organization is treating infrastructure cost as a real constraint or treating it as "engineering's problem."

## W3. Questions to ask your engineer

| Question | What this reveals |
|----------|-------------------|
| **1. What deployment strategy are we using for this release — rolling update or recreate?** | Whether the deploy will cause downtime, and whether the engineer has checked that changes are backward-compatible with the running version. A "recreate" answer should prompt: *"What's our maintenance window plan?"* |
| **2. Do all our production services have both liveness and readiness probes configured?** | Whether Kubernetes can correctly detect unhealthy pods and protect traffic during deploys. Missing readiness probes means deploys may route traffic to pods that aren't ready. |
| **3. What does the HPA configuration look like for Paathshala — what's the scale trigger and what's the max replica count?** | Whether the class booking service can handle peak surge. A max replica count that's too low means HPA hits its ceiling during peak and pods get overwhelmed. A scale trigger too conservative (e.g., 90% CPU) means scaling starts too late. |
| **4. Are there any services currently running as single replicas in production?** | Single points of failure. One crash = outage. This is a risk PMs should track. |
| **5. What's happening to the pods flagged with high response times in New Relic — are they being throttled or are they genuinely slow?** | Whether the 1.26s CRM API latency is a CPU throttling problem (resource limit too low) or an application-level issue (missing index, synchronous third-party call). CPU throttling requires a Kubernetes resource limit fix; the other requires application work. |
| **6. How long does a production deploy typically take end to end, from merge to pods running?** | The practical deploy velocity. Look for a specific answer: *"8 minutes total — 5 minutes for CI + 3 minutes for rolling update across 8 pods."* |
| **7. What's our cluster's current headroom — how much capacity is available before we'd need to add nodes?** | Whether a planned traffic surge requires pre-scaling. Node provisioning takes 3–5 minutes on EKS. If the cluster is at 85% capacity and an event will drive a 40% traffic spike, new nodes must be added before the event, not during. |

### Expected answers to highlight

> **Liveness & Readiness Probes (Question 2):** Liveness checks the `/health` endpoint with a 30-second timeout; readiness checks the same endpoint but also waits for the DB connection pool to initialize.

## W4. Real product examples

### BrightChamps — EKS as the operational backbone

**The deployment architecture:**
All 11 BrightChamps microservices run on AWS EKS (Kubernetes managed by AWS):
- Eklavya, Paathshala, Doordarshan, Dronacharya, Prabandhan
- Payments, Hermes, Chowkidar, Tryouts, Shotgun, Prashahak BE

**Visibility stack:**
| Tool | Purpose |
|------|---------|
| Lens | Kubernetes visibility |
| New Relic | APM (Application Performance Monitoring) |
| Kibana | Log aggregation |

**The class booking surge scenario:**
Paathshala handles class scheduling with predictable demand spikes — many parents booking simultaneously at known times.

| Without Kubernetes | With EKS + HPA |
|-------------------|----------------|
| Traffic spike doubles request volume → manual intervention required | CPU threshold exceeded → HPA automatically schedules additional pods |
| SSH to servers, start new instances, hope it's fast enough | Horizontal scaling happens automatically |

**The monitoring KB finding — PM implications:**

⚠️ Two CRM APIs showing 1.26s and 1.19s response times could indicate:
- **CPU throttling:** Resource limits too low; pods being CPU-capped
- **Application slowness:** Missing DB index, synchronous external call

> **Key PM question before troubleshooting:** When New Relic shows a service is slow, ask "are pods being throttled or evicted?" *before* assuming code is broken. An SRE investigating this checks Lens for CPU throttling events first.

---

### BrightChamps — Lens as the operational view

**What Lens shows the engineering team:**

| Element | Details |
|---------|---------|
| Pod state | Running, Pending, CrashLoopBackOff |
| Resource usage | Per-pod CPU and memory usage |
| Deployment tracking | History and current state |
| Live diagnostics | Real-time logs |

**PM relevance during incidents:**

When a war room is active, Lens is ground truth for deployment health. Engineers confirm:
- "Paathshala pod 7 is in CrashLoopBackOff"
- "Memory usage on Hermes pod is at 94% of limit"

> **PM insight:** Understanding Lens screenshots lets you participate in triage without asking "what does that mean?" every 30 seconds. This accelerates incident response.

---

### Stripe — Kubernetes for zero-downtime deploy velocity

**Stripe's deployment model:**

| Constraint | Implication |
|-----------|------------|
| Millions of merchants depend on uninterrupted payment processing | Deploy downtime = business-critical failure |
| Rolling updates with backward compatibility | Multiple deploys per day possible |
| Every API change must be compatible with previous version running simultaneously | Enforced as pre-deploy check |

**PM implication:**

> **Deploy velocity trade-off:** Stripe achieves multiple deploys per day with zero downtime *only* because rolling updates are default and backward compatibility is a hard requirement, not a suggestion.

A PM team allowing breaking API changes in single deploys trades away Stripe-level deploy velocity for short-term development speed.

---

### Enterprise B2B — Kubernetes as a compliance and security surface

⚠️ **Common enterprise security questionnaire requirements:**

**Least-privilege access:**
- Can a compromised pod access other pods' secrets?
- Are RBAC (Role-Based Access Control) policies enforced?

**Workload isolation:**
- Are namespaces used to isolate tenant workloads?

**Container hardening:**
- Are containers prevented from running as root?
- Is pod security policy enforced?

**Audit & compliance:**
- Are Kubernetes API audit logs (who changed what deployment when) retained?
- Are logs exportable for compliance review?

**PM implications:**

⚠️ **Critical milestone:** Never sign an enterprise contract before confirming Kubernetes RBAC and namespace isolation are in place. This is a compliance risk.

> **Roadmap planning:** Adding a security review milestone before first enterprise customer onboarding includes:
> - Kubernetes configuration audit
> - Namespace design implementation
> - RBAC policy creation
> - Audit log retention setup

**Takeaway:** This engineering effort requires sprint time — it does not happen automatically.
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Failure pattern 1: The readiness probe that breaks every deploy

**Symptom:** Deploys never complete; rolling updates stall.

**Root cause:** Readiness probe timeout (10s) shorter than actual startup time (35s).

**What happened:**
- Service requires significant startup: database connection pool initialization, feature flag config load, in-memory cache warm-up
- Pod fails readiness probe before becoming ready
- Kubernetes marks pod `NotReady`, keeps it out of load balancer
- Rolling update stalls — old pods can't be removed
- Never caught in staging (warm DB connection already cached)

**PM prevention role:**

When a service requiring significant startup initialization is proposed, ask:
- "What is the expected pod startup time?"
- "Does it exceed 30 seconds?"

If yes: **readiness probe configuration must be part of the deploy ticket**, not a post-outage discovery.

---

### Failure pattern 2: No resource requests — the noisy neighbor

**Symptom:** Elevated latency (80ms → 1.2s response times); looks like a Paathshala bug or database problem.

**Root cause:** Service deployed with no resource requests or limits.

**What happened:**
- Background job normally uses 20% CPU
- On bad day: enters processing loop, consumes 100% of node's CPU
- Other pods on same node have guaranteed CPU requests, but can't use them
- Unthrottled service consumes above its fair share
- All pod performance degrades

| Configuration | Impact |
|---|---|
| Resource requests set | CPU guaranteed per pod |
| Resource limits set | Runaway service throttled |
| Neither set | Noisy neighbor problem |

**PM prevention role:**

Resource limits and requests must be a **deploy checklist item, not optional**.

Code review approval process is incomplete without: "Are resource limits set?"

---

### Failure pattern 3: HPA fighting itself — replica oscillation

**Symptom:** Deploy looks fine but latency is erratic and unpredictable.

**Root cause:** HPA scale-down stabilization window (60s) shorter than burst cycle period (30s spike → 90s drop → repeat).

**What happened:**
- Load is moderate but bursty
- HPA scales up (adds pods) → waits 60s → scales down
- Next burst arrives before new pods fully shut down
- Scales back up again
- Constant add/remove cycles prevent stable capacity
- Pod startup overhead accumulates

**Solution:** Increase stabilization window to **5–10 minutes for services with predictable periodic load patterns**.

**PM prevention role:**

Understand your traffic shape. Ask:

- "What does our load profile look like over 24 hours?"
- "Are there predictable burst windows?" (e.g., class scheduling times, batch report generation)
- "Should HPA be tuned for those specific patterns?"

These are **product questions with direct Kubernetes configuration implications**.

## S2. How this connects to the bigger system

### Containers & Docker (03.02)
**Connection:** Kubernetes orchestrates containers — every Kubernetes concept operates on container images.

| Concept | How it works |
|---------|-------------|
| Pods | Run a specific image version |
| Deployments | Reference an image tag |
| Rollbacks | Swap image tags |
| Resource enforcement | CPU/memory requests and limits configured at deployment level, enforced by container runtime |

**Why this matters:** Understanding containers is the prerequisite for understanding why Kubernetes works the way it does.

---

### CI/CD Pipelines (03.04)
**Connection:** The CI/CD pipeline submits new deployments to Kubernetes — they're two halves of zero-downtime delivery.

**The flow:**
1. Merge to main
2. Build Docker image
3. Push to ECR
4. Run `kubectl apply` (or Helm upgrade) with new image tag
5. Kubernetes executes rolling update

| Layer | Failure mode |
|-------|--------------|
| CI/CD broken | Kubernetes never gets the new image |
| Kubernetes misconfigured | The deploy the pipeline submits never completes |

---

### Monitoring & Alerting (03.09)
**Connection:** Kubernetes generates events that monitoring systems must consume to provide operational visibility.

**Events to monitor:**
- Pod crashes (CrashLoopBackOff)
- OOMKill events
- Node pressure warnings
- Pending pods

**Tools & perspectives:**
- New Relic — application errors
- Kibana — log aggregation
- Lens — Kubernetes-native view (see BrightChamps infra-monitoring KB)

⚠️ **Blind spot:** A monitoring system that alerts on application errors but not on Kubernetes events misses the operational layer. Example: "Paathshala is slow" in New Relic without seeing "Paathshala pod is being CPU throttled" in Lens.

---

### CDN & Edge Caching (03.07)
**Connection:** Kubernetes and CDN are independent systems that must be coordinated during deploys.

| System | Manages |
|--------|---------|
| Kubernetes | Server-side rendering and API response layer |
| CDN | Edge caching layer |

⚠️ **Deploy risk:** A Kubernetes rolling update replacing the server-side image does not automatically invalidate CDN caches of the old API responses. For APIs that change response structure, CDN cache invalidation must accompany the Kubernetes deploy.

---

### Feature Flags (03.10)
**Connection:** Feature flags and Kubernetes rolling updates are complementary deploy risk management strategies.

| Strategy | Manages | How |
|----------|---------|-----|
| Rolling update | Infrastructure risk | Replace pods incrementally |
| Feature flag | Product/rollout risk | Enable features for subset of users independently of pod version |

**Best practice — use both:**
1. Deploy new code via rolling update (infrastructure risk managed)
2. Enable feature flag for 5% of users (product risk managed)

Neither strategy alone is as powerful as both together.

## S3. What senior PMs debate

### Kubernetes complexity vs the alternatives — when is EKS overkill?

**The situation:**
BrightChamps runs 11 microservices on EKS—appropriate at that scale. But Kubernetes carries real operational costs:

| Responsibility | Effort | Frequency |
|---|---|---|
| Cluster maintenance | Ongoing | Continuous |
| HPA tuning | Medium | Per-service |
| Health probe configuration | Medium | Per-service |
| Node group management | Ongoing | Continuous |
| Version upgrades | High | Every 12–18 months |
| Debugging scheduling failures | High | As needed |

**The comparison:**

| Platform | Operational Control | Operational Simplicity | Hiring Friction |
|---|---|---|---|
| **Kubernetes (EKS)** | High (canary, blue/green, sidecar injection) | Low | High (scarce expertise) |
| **AWS ECS** | Medium | Medium | Medium |
| **Serverless (Lambda)** | Low | Very High | Low |
| **PaaS (Railway/Render)** | Low | Very High | Low |

**The PM debate:**
"We're on Kubernetes" is a three-axis decision:

1. **Hiring** — Kubernetes engineers cost more and are harder to find
2. **Operations** — Someone owns cluster maintenance as a permanent responsibility
3. **Capability** — What deployment patterns become possible (canary deploys, blue/green, sidecar injection)

> **Key insight:** Choosing Kubernetes is as much a product organization decision as a technical one.

---

### GitOps vs imperative deploys — does declarative state management change the PM workflow?

**Traditional model (imperative):**
```
Code merges → CI/CD pipeline → kubectl apply [new image tag] → Deploy complete
```

**GitOps model (declarative):**
```
Git repository [desired state] ← ArgoCD continuously reconciles → Kubernetes cluster [actual state]
```

**What changes for PMs:**

| Capability | Imperative | GitOps |
|---|---|---|
| **Source of truth** | "Ask an engineer" or check monitoring tool | Git repository (queryable, auditable) |
| **Current state visibility** | Requires manual cluster inspection | Read git repo anytime |
| **Rollback mechanism** | Kubernetes command (requires access) | Git revert (available to anyone with repo access) |
| **Drift detection** | Manual; discovered through incident | Automatic; continuously reconciled |
| **Audit trail** | Weak (manual changes not captured) | Strong (all changes in git history) |

**The debate:**

| Factor | GitOps Overhead | GitOps Benefit |
|---|---|---|
| **Tooling complexity** | ArgoCD requires operational maintenance | Reduces human-error risk |
| **Compliance/audit** | Extra layer to maintain | Deployment state fully auditable |
| **Team stage** | Premature for early-stage teams | Worth investment for mature teams |

> **Trade-off:** GitOps is worth the investment for teams that need compliance and deployment audit trails, or that have had incidents caused by manual cluster changes. Early-stage teams moving fast may find it premature.

---

### AI inference on Kubernetes — GPU nodes, model serving, and the new operational tier

**GPU vs CPU resource economics:**

| Attribute | CPU Pods | GPU Pods |
|---|---|---|
| **Cost** | Low | $2–10/hour per node |
| **Provisioning time** | <30s | 3–8 minutes |
| **Scaling model** | Easily replicated | Can't replicate; don't share |
| **Over-provisioning risk** | Low cost of waste | High cost of waste |
| **Kubernetes allocation** | Native `cpu` resource | Explicit `nvidia.com/gpu` request |

**Why HPA breaks for GPU:**
CPU-based HPA scales horizontally without friction. GPU services require:
- Fixed pod count (GPUs don't share)
- Slow node provisioning (blocks scaling)
- Expensive waste (over-provisioning is costly)

**The PM decision framework:**
When your roadmap includes "add AI recommendations to the student dashboard," someone must own the inference infrastructure model:

### Option 1: Managed API (Anthropic/OpenAI)
**What:** Per-token pricing, vendor handles all infrastructure  
**Why:** Zero operational complexity, predictable costs at scale  
**Trade-off:** Per-token margins; vendor lock-in  

### Option 2: Dedicated Kubernetes GPU nodes
**What:** Run GPU pods on reserved EKS nodes  
**Why:** Lower per-inference cost at extreme scale; full control  
**Trade-off:** High operational complexity; GPU idle costs  

### Option 3: Spot GPU instances
**What:** Lower-cost GPU nodes, interruption risk  
**Why:** Cost optimization; viable for fault-tolerant workloads  
**Trade-off:** Service interruptions possible; requires retry logic  

⚠️ **This is no longer a purely engineering decision.** The cost model at scale is a product and business decision that affects margins, unit economics, and go-to-market strategy.