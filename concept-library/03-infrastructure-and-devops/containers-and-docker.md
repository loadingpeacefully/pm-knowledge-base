---
lesson: Containers & Docker
module: 03 — Infrastructure & DevOps
tags: tech
difficulty: foundation
prereqs:
  - 03.01 — Cloud Infrastructure Basics: containers run on EC2 instances managed by EKS; understanding EC2 and Kubernetes as the compute layer clarifies what containers are deployed onto
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
  - technical-architecture/infrastructure/web-app-optimization-champ.md
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

## F1. "It works on my machine"

### The Problem

A developer finishes building a new class scheduling feature. It works perfectly on their laptop. They push it to the staging environment for QA. The QA tester opens it and sees a broken page — a crash with a cryptic error message.

| Who | Finding |
|-----|---------|
| Developer | "It works on my machine" |
| QA Engineer | "It's broken on staging" |

**Root cause (after 3 hours):** Developer's laptop runs Node.js 18.12. Staging server runs Node.js 14.21. The new feature's library requires Node.js 16+. Staging is two major versions behind.

> **Environment inconsistency:** The core problem — every server has its own operating system version, runtime versions (Node.js, Python, Java), installed libraries, and configuration files. Differences between environments cause failures that are difficult to reproduce and slow to debug.

### The Solution: Containers

A container packages code together with everything it needs to run:
- Exact version of the runtime (Node.js, Python, etc.)
- All dependencies
- Configuration files
- The application code

**Result:** "It works on my machine" becomes "it works in the container" — and the container runs identically everywhere.

---

### Company — BrightChamps (Microservices Deployment)

**What:** 11 microservices (Eklavya, Paathshala, Doordarshan, Payments, Hermes, and six others), each running as a container on AWS EKS (Kubernetes).

**Why:** When an engineer deploys an update to the Paathshala class service, they don't SSH into a server and manually update code. Instead:
1. Build a new container image with updated code
2. Push it to a container registry
3. Tell Kubernetes to use the new image
4. Kubernetes replaces old containers one by one — without downtime

**Takeaway:** If new containers crash, Kubernetes automatically rolls back to the previous version.

---

### Company — BrightChamps (Frontend Performance)

**What:** Student dashboard is a Next.js application with a critical performance issue: all 49 routes load the same 2.5MB JavaScript bundle. The login page loads the full dashboard code, including features users won't see until after login.

**Why:** The frontend performance fix involves changing the build and deployment mechanism. The Next.js application is packaged into a Docker image, pushed to a registry, and Kubernetes pulls it onto pods. Understanding containers helps PMs understand why "rebuild the bundle strategy" means "build a new container image and redeploy it" — not just a code change, but a packaging and delivery change.

**Takeaway:** Container knowledge bridges engineering and product thinking on deployment mechanics.

---

## PM Decision Frame — When Does Container Knowledge Matter?

| Scenario | Why It Matters | PM Impact |
|----------|----------------|-----------|
| **Release planning** | Every deployment involves building and pushing a container image. Container build time is part of your release timeline. | Prevents over-committing to timelines (e.g., "20-minute deploy" that actually takes 45 minutes due to uncached image build) |
| **Incident response** | If the team uses container versioning correctly, rollback is a 2–5 minute Kubernetes operation, not a 30-minute rebuild. | Changes speed of rollback vs. hotfix decision-making |
| **Sprint scoping** | "Optimize Docker builds" or "right-size container resources" are engineering tasks with measurable outcomes: faster deploys, less cloud spend, reliable autoscaling. | Justifies engineering investment — not "nice to have DevOps work" |
| **Compliance readiness** | Enterprise contracts may require evidence of container image scanning (CVE checks). | Must verify team's containers pass security audit *before* signing deals that require it |

## F2. What it is — the standardized shipping container for software

**The core metaphor:** Before standardized shipping containers, global trade was chaotic—goods repacked at every port. A container packed in Shenzhen could travel by ship, train, and truck to Chicago without ever being unpacked. **Docker containers are the software equivalent:** they package an application and everything it needs to run into a standardized unit that works identically on any machine.

### Three core terms

> **Docker image:** The blueprint. A read-only snapshot of everything needed to run the application: operating system layer, runtime version, libraries, and application code. Built once, runs anywhere. Think of it as a recipe; the container is the prepared dish.

> **Container:** A running instance of an image. When Kubernetes starts the Eklavya student service, it takes the Eklavya Docker image and runs it as a container. You can run many containers from the same image simultaneously—five copies of Eklavya running at once, each serving traffic.

> **Container registry:** The storage system for images. AWS has ECR (Elastic Container Registry). Engineers push new image versions (`paathshala:v2.4.1`, `paathshala:v2.4.2`) to ECR. Kubernetes pulls from ECR when deploying, enabling precise rollbacks.

### Containers vs. Virtual Machines

| **Aspect** | **Virtual Machine** | **Container** |
|---|---|---|
| **OS layer** | Full operating system kernel, isolated | Shares host machine's OS kernel |
| **What it contains** | Virtualized hardware, full OS, application | Only application + dependencies |
| **Startup time** | Minutes | Seconds |
| **Scaling impact** | Autoscaler struggles with delays | Autoscaler keeps pace with demand |

*What this reveals:* For a service like Paathshala that scales from 5 to 50 pods during class scheduling surges, the difference between 5-minute VM startup and 5-second container startup determines whether the autoscaler meets demand or users see "no available slots" errors.

## F3. When you'll encounter this as a PM

### Deploy timing unexpectedly changes

**Scenario:** A developer estimates "the deploy will take 10 minutes," but it actually takes 45 minutes—or only 2 minutes.

**Why it happens:**
- Docker image isn't cached → must rebuild from scratch (slower)
- Image was pre-built during CI → faster deployment

**What this means for you:** The container build step is part of the deployment pipeline. Understanding it helps you set accurate deployment expectations and ask the right questions when timelines slip.

---

### Emergency hotfix to production

**Scenario:** "We need to fix this payment bug right now."

**The actual process:**
1. Write the fix
2. Build a new Docker image with the fix
3. Push to registry
4. Deploy the new image to production

⚠️ **Key distinction:** "The fix is written" and "the fix is deployed" are separated by a 2–10 minute build and push step—not just a git commit.

**What this means for you:** When coordinating an emergency deployment, account for image build time in your timeline.

---

### Staging environment doesn't match production

**Scenario:** "We tested this in staging and it worked. Why is it broken in production?"

**Root cause:** Staging and production are running different container images—different versions, different environment variables, different configurations.

> **Container promise:** The container model eliminates environment drift by running the same image everywhere. This only works if staging and production use the identical image with only runtime-injected, environment-specific values (database URLs, API keys).

**What to verify:** When running acceptance testing in staging, confirm with your engineer: *"Are staging and production running the same image version?"*

---

### Engineer requests "Docker image optimization"

**Scenario:** The Next.js student dashboard's 2.5MB JavaScript bundle adds to its container image size.

**Impact chain:**
| Effect | Consequence |
|--------|-------------|
| Larger image | Takes longer to push to registry |
| Larger image | Takes longer to pull to each pod |
| Larger image | Takes longer to start |

**Compound benefit:** When the bundle shrinks from 2.5MB to under 1.5MB:
- Application gets faster for users ✓
- Container image gets smaller ✓
- Every future deployment gets faster ✓

**What this reveals:** Image optimization work speeds up both the user experience and the deployment pipeline.

---

### New microservice is "containerized"

**What it means:** The service has been packaged as a Docker image and can run on Kubernetes.

**Capabilities unlocked:**
- ✓ Deploy with standard tooling (same as all other services)
- ✓ Scale horizontally
- ✓ Roll back if it fails
- ✓ Monitor with existing tools

**Without containerization:** The service requires custom deployment procedures—like arranging custom freight instead of using standard shipping containers.
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation. Understands containers as self-contained packaging, Docker images vs running containers, container registries, and the difference from VMs.
# ═══════════════════════════════════

## W1. How containers actually work — the mechanics that matter for PMs

### Quick Reference
| Concept | PM relevance | Key metric |
|---------|--------------|-----------|
| Layer caching | CI build speed | 30–60 sec (optimized) vs 5–10 min (poor) |
| Multi-stage builds | Image size, deploy speed | ~100MB (optimized) vs ~500MB (naive) |
| Resource limits | Stability, cost | Prevents one service from crashing the host |
| Startup time | Autoscaling response | 1–5 sec (Kubernetes) vs 2–5 min (VMs) |
| Environment variables | Build-once-deploy-anywhere | Same image, different configs (staging/prod) |
| Image versioning | Rollback speed | 2–5 min (containers) vs 15–30 min (traditional) |

---

### 1. The Docker image build process — what happens when code becomes a container

> **Dockerfile:** A recipe that specifies a base image (e.g., `node:18-alpine`), copies files, installs dependencies, and exposes ports. Each instruction creates a layered image.

**Layers are the key efficiency mechanism:**

Each Dockerfile instruction creates a layer that is cached. On code-only changes, Docker reuses all previous layers (OS, Node.js, dependencies) and only rebuilds changed layers.

| Scenario | Build time | What happened |
|----------|-----------|---------------|
| Well-structured Dockerfile | 30–60 seconds | Dependencies cached; only app code rebuilt |
| Poorly structured Dockerfile | 5–10 minutes | Everything rebuilt from scratch on every change |

**⚠️ PM implication:** "Why is the CI build slow?" often traces to Dockerfile layer ordering. Dependencies should be copied and installed *before* application code so dependency installation (the slow step) is cached and only reruns when `package.json` changes — not on every code change.

---

### 2. Multi-stage builds — building lean images

> **Multi-stage build:** A Dockerfile pattern where Stage 1 (build) installs dependencies and compiles the app, and Stage 2 (production) copies only the compiled output—discarding build tools.

**Example: Next.js student dashboard**

Starting point:
- JavaScript bundle: 2.5MB → optimization goal: under 1.5MB
- Naive Docker build: ~500MB (includes webpack, TypeScript compiler, test libraries)
- Optimized multi-stage build: ~100MB (only compiled output)

**Impact comparison:**

| Metric | Naive build | Multi-stage build | Benefit |
|--------|-------------|-------------------|---------|
| Image size | ~500MB | ~100MB | 5× smaller |
| Pull time | Slow | Fast | Faster deploys |
| Startup time | Slower | Faster | Faster autoscaling |
| Storage cost (ECR) | Higher | Lower | Direct cost savings |

**PM implication:** "Our Docker images are too large" is a solvable engineering problem with measurable output: image size reduction in MB, deploy time savings in seconds, and storage cost reduction.

---

### 3. Container resource limits — preventing one service from starving others

> **Resource limits:** CPU and memory maximums assigned to each container to prevent one service from consuming all host resources and crashing others.

**When resource limits prevent failure:**

A service with a memory leak consumes more memory over time. Without limits, it crashes the entire host machine. With limits, Kubernetes restarts the container before host failure.

**Resource allocation parameters:**

| Parameter | Controls | Typical range | If too low | If too high |
|-----------|----------|---------------|-----------|------------|
| **CPU request** | Guaranteed CPU allocation | 100m–500m (0.1–0.5 cores) | Service slow under load | Wasted CPU allocation |
| **CPU limit** | Maximum CPU usage | 500m–2000m (0.5–2 cores) | Service throttled even with idle host CPU | One service starves others |
| **Memory request** | Guaranteed memory reserved | 128Mi–512Mi | Too many pods scheduled on one node | Wasted memory reservation |
| **Memory limit** | Maximum memory before restart | 256Mi–1024Mi | Container killed on memory spikes (OOMKilled) | Memory leak unchecked; crashes node |

**⚠️ Warning:** Misconfigured resource limits surface problems through predictable restarts rather than allowing degraded-but-running services to mask deeper issues.

---

### 4. Container startup time — why it matters for scaling and deployment

> **Cold start:** Time for a container to boot from image to ready-to-serve requests.

**Startup time by deployment technology:**

| Technology | Startup time | Scaling capability |
|-----------|--------------|-------------------|
| Virtual machine (EC2) | 2–5 minutes | Cannot scale to demand spikes in time |
| Docker container (cold) | 5–30 seconds | Scales within surge window |
| Docker container (Kubernetes, pre-pulled) | 1–5 seconds | Near-instant scaling |
| AWS Lambda (cold start) | 100–1000ms | Fastest; limited to 15-min execution |

**Real scenario: BrightChamps class scheduling surge**

Peak demand occurs at class scheduling window openings — thousands of parents booking simultaneously.

- Kubernetes detects CPU spike
- Horizontal pod autoscaler scales Paathshala (class service) pods: 5 → 25
- Each new pod starts in 2–5 seconds (pre-pulled image)
- With VMs: 3–5 minute scale-up = surge passes before capacity ready

**PM takeaway:** Container startup time is a direct input to autoscaling responsiveness and cost efficiency.

---

### 5. Environment variables and configuration — what changes between environments

> **Environment variables:** Runtime-injected configuration (database URLs, API keys, log levels, feature flags) that varies between staging and production without rebuilding the image.

**The build-once-deploy-anywhere pattern:**

```
Same Docker image (one build):
  ↓
Kubernetes staging → ConfigMap/Secret for staging database
Kubernetes production → ConfigMap/Secret for production database
```

Kubernetes manages environment variables via:
- **ConfigMaps:** Non-sensitive configuration
- **Secrets:** API keys, database passwords

**⚠️ PM implication:** A "quick fix" is only truly quick if it changes only configuration (no build). If code changed, a full build-push-deploy cycle is required. Distinguish between:
- Configuration change: Already-built image, just redeploy (minutes)
- Code change: Build new image, push, deploy (5–15 minutes)

---

### 6. Container registries and image versioning — the rollback mechanism

> **Container registry (ECR):** Centralized storage for all container images with full version history and the ability to retrieve any previous version.

**Image versioning standards:**

- **Semantic versioning:** `v2.4.1`
- **Git commit hash:** `sha-a1b2c3d`

Both enable precise identification of what's running.

**Rollback speed comparison:**

| Approach | Steps | Time | Dependency |
|----------|-------|------|------------|
| Traditional deploy rollback | Checkout old code → reinstall dependencies → rebuild → redeploy | 15–30 minutes | All tools available; no failure during build |
| Container rollback | Pull previous image from ECR → replace pods | 2–5 minutes | Previous image exists in registry |

**⚠️ Critical for post-deploy incidents:** Every post-incident conversation should start with: "What image version is currently running, and is the previous version available in ECR?" If yes, rollback is minutes. If no, recovery takes much longer.

**PM implication:** Maintaining ECR image retention policy (don't auto-delete old versions too aggressively) is a cheap insurance policy for rapid rollbacks.

## W2. The decisions containers force

### Quick Reference
- **Containerize on EKS:** User-facing APIs, persistent services, >15min execution, in-memory state
- **Use Lambda:** Event-driven jobs, <15min execution, webhooks, ETL triggers
- **Never use EC2:** No new services on legacy infrastructure
- **Image optimization:** Schedule separately; only include in feature sprint if blocking delivery
- **Configuration:** Always inject at runtime; never bake into images

---

### Decision 1: When should a new service be containerized vs deployed as a Lambda function?

> **PM default:** Containerize (deploy on EKS) any persistent service that handles user-facing API requests, requires more than 15 minutes of execution time, or needs to maintain in-memory state between requests. Use Lambda for event-driven, short-duration background jobs. Never add new services to the legacy EC2 server.

| Capability | Containerized (EKS) | Lambda (serverless) | EC2 (legacy) |
|---|---|---|---|
| **Startup time** | 2–30 seconds | 100–1000ms (cold start) | 2–5 minutes |
| **Maximum execution** | No limit | 15 minutes | No limit |
| **Horizontal scaling** | Kubernetes autoscaler | Automatic (to millions) | Manual |
| **Rollback speed** | 2–5 minutes | 2–5 minutes (new Lambda version) | 15–30 minutes |
| **Best for** | User-facing APIs, persistent microservices | Background jobs, webhooks, ETL triggers | ⚠️ Never for new services |

---

### Decision 2: Should we optimize the Docker image as part of this feature sprint?

> **PM default:** Image optimization (multi-stage builds, layer caching, smaller base images) is maintenance work that pays forward on every future deployment. It should be scheduled as a standalone tech debt sprint rather than added to a feature sprint — mixing optimization with feature work makes both harder to validate. Include it in the sprint planning when deployment times exceed 5 minutes.

| Factor | Optimize in current sprint | Separate optimization sprint |
|---|---|---|
| **Build time impact** | Immediate improvement | Delayed improvement |
| **Feature sprint velocity** | Reduced — optimization scope competes with features | Full velocity on feature work |
| **Validation clarity** | Mixed — hard to separate optimization from feature changes | Clean — clear before/after metrics |
| **When to choose** | Only if image size is directly blocking feature | ✓ Preferred approach |

---

### Decision 3: How should environment-specific configuration be managed — baked into the image or injected at runtime?

> **PM default:** All environment-specific configuration (database URLs, API keys, feature flags, log levels) must be injected at runtime via environment variables — never baked into the Docker image. Baking configuration into images means building separate images for staging and production, doubling build time and eliminating the guarantee that what's tested in staging is what runs in production.

| Approach | Runtime injection (ConfigMaps/Secrets) | Baked into image |
|---|---|---|
| **Same image staging → production** | ✓ Yes — guaranteed | ✗ No — different images per environment |
| **Secret management** | Kubernetes Secrets; secure pattern | ⚠️ Risk of secrets in git |
| **Config changes without rebuild** | ✓ Yes — update ConfigMap, restart | ✗ No — must rebuild and redeploy |
| **Security & consistency** | ✓ Correct pattern | ⚠️ Anti-pattern |

## W3. Questions to ask your engineer

**1. What is our current Docker image size for each service, and how long does a build take?**

*What this reveals:* Whether image optimization is needed and whether build times are affecting deployment velocity.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Largest images** | Named (e.g., "Next.js frontend: 420MB") | Unknown or oversized (>500MB) |
| **Build time** | <10 minutes | >10 minutes |
| **Multi-stage builds** | Confirmed in use | Not mentioned or missing |

---

**2. When we roll back a deploy, how long does it actually take?**

*What this reveals:* Whether the rollback process is fast enough to be used aggressively during incidents.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Rollback speed** | 2–4 minutes (tested) | 20+ minutes or untested |
| **Previous images** | Retained 30 days in ECR | Not retained or unclear policy |

---

**3. Are staging and production running the same Docker image version?**

*What this reveals:* Whether QA results from staging are valid for production.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Image versions** | Identical across environments | Different versions |
| **Configuration differences** | Only environment variables (URLs, keys) | Different code or binaries |

---

**4. Does our CI/CD pipeline automatically build and push a new Docker image on every merge to main?**

*What this reveals:* Whether the deployment process is automated or requires manual steps.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Merge → build** | Automatic trigger on main | Manual build step required |
| **Testing** | Automated in pipeline | Manual testing step |
| **Push to registry** | Automatic to ECR | Manual push |
| **Production deploy** | Manual approval gate (safe) | Automatic or missing gate |

---

**5. What happens if a container's memory usage keeps growing — does it get automatically restarted?**

*What this reveals:* Whether memory limits are configured and whether memory leaks cause visible incidents or silent performance degradation.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Memory limits** | Set per container | Unlimited or not configured |
| **OOM behavior** | Kubernetes kills/restarts (OOMKilled) | Container lingers or crashes silently |
| **Alerting** | Alerts on OOMKilled events | No alerts on memory issues |

---

**6. How are API keys and database passwords managed — are they in environment variables, and are those secrets committed to the git repository?**

*What this reveals:* Whether secrets management follows security best practices.

⚠️ **CRITICAL SECURITY ISSUE:** Secrets committed to git are a critical vulnerability — anyone with repository access has production credentials.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Secrets storage** | Kubernetes Secrets or external vault | Environment variables in code |
| **Git repository** | No sensitive data | Secrets committed to history |
| **Injection method** | Injected at container startup | Hardcoded or passed at build time |

---

**7. What is our image retention policy in ECR — how many previous versions are available for rollback?**

*What this reveals:* Whether the rollback window matches the team's incident response timeline.

| Signal | Healthy | At Risk |
|--------|---------|---------|
| **Retention window** | 30 days minimum | Aggressive deletion (e.g., last 5 only) |
| **Critical services** | Last 10 tagged releases kept regardless of age | Single retention policy for all services |
| **Rollback options** | Multiple versions available for investigation | Limited window restricts incident response |

## W4. Real product examples

### BrightChamps — 11 microservices, 11 containers

**The deployment architecture:**

Each of BrightChamps' 11 microservices (Eklavya, Paathshala, Doordarshan, Dronacharya, Prabandhan, Payments, Hermes, Chowkidar, Tryouts, Shotgun, Prashahak BE) runs as one or more Docker containers on AWS EKS. The monitoring stack — New Relic, Kibana, Lens — provides visibility into each container's health, resource usage, and logs.

**Why containerization matters for this architecture:**

| Without Containers | With Containers |
|---|---|
| SSH to each server running Paathshala | Build one image, push once to ECR |
| git pull, npm install on each instance | Kubernetes applies to all pods automatically |
| Dozens of SSH sessions per deployment | Single deployment command |
| No guarantee of consistent updates | Guaranteed consistency across all instances |

**The monitoring dividend:**

Because containers report their resource usage (CPU, memory) to Kubernetes, Lens (the Kubernetes monitoring tool) provides a real-time view of every container across the cluster. The infra-monitoring KB documents Lens as a monitoring tool — it's the Kubernetes dashboard that shows pod health, resource utilization, and logs. This visibility is only possible because each service is containerized; it's unavailable for the legacy EC2 server running PHP scripts.

**What this means for the PM:**

When an engineer says "we need to spend a sprint containerizing the reporting service," they're buying:

- Independent deployability (ship reports fixes without touching Payments)
- Automatic rollback if the deploy breaks
- Real-time resource monitoring in Lens
- Ability to scale the service independently during peak load

The sprint cost is real; so is the operational leverage.

---

### BrightChamps — the Next.js frontend as a container

**What it means to containerize a Next.js app:**

The student dashboard at `champ.brightchamps.com` is a Next.js application with 49 routes, 27 Redux slices, and a 2.5MB JavaScript bundle. To deploy it:

1. The Next.js app is compiled (webpack builds all routes and assets)
2. Packaged into a Docker image with a lightweight Node.js server
3. The image is pushed to ECR
4. Kubernetes runs the image on pods behind a load balancer

**The bundle size and image size connection:**

The web app optimization KB targets reducing the JavaScript bundle from 2.5MB to under 1.5MB. This makes the app faster for users (less JavaScript to download). It also makes the Docker image smaller — compiled Next.js output is part of the image.

Optimization activities include:
- Route-based 4-tier bundle strategy
- Removing Lottie animations
- Lazy loading

Each reduces both the user-facing load time and the deployment artifact size.

**The Tier 1 bundle implication:**

Currently, the login page loads 2.5MB of JavaScript — the full dashboard bundle. After the 4-tier optimization, the login page loads ~300KB (Tier 1 minimal bundle). The login page would be deployed as a different build target, potentially a different container configuration. 

The PM approving this optimization work is approving a change to both the runtime behavior (faster login) and the deployment architecture (different container structure for different route tiers).

---

### Docker Hub / ECR — the container registry as a version history

> **Container Registry:** A central repository that stores and versions all Docker images, enabling consistent deployment across environments and fast rollback capabilities.

**What a container registry provides:**

- **Immutable history:** Every pushed image is retained with its tag. `eklavya:v3.1.2` is the same bits today as when it was built.
- **Fast rollback:** If `eklavya:v3.2.0` introduces a bug, Kubernetes can roll back to `eklavya:v3.1.2` in under 5 minutes — faster than rebuilding from code.
- **Audit trail:** ECR logs every push and pull. "Which version was running in production at 3:47pm on Tuesday?" is answerable from the ECR deployment history.
- **Multi-environment promotion:** The image tested in staging (`eklavya:v3.2.0`) is promoted to production unchanged — not rebuilt, not recompiled. The exact same bits that passed staging tests run in production.

**PM implication:**

Container registries are part of the release management system. When a PM asks "are we sure production is running what we tested?", the answer comes from comparing the image tag deployed to production against the image tag that passed staging QA. If they're the same SHA, they're the same code.

---

### Enterprise B2B — container image scanning as a compliance requirement

**What enterprise customers require:**

Enterprise SaaS contracts — particularly with financial institutions, healthcare companies, and government clients — frequently require evidence of container image scanning. Every Docker image contains third-party libraries. Libraries have vulnerabilities (CVEs — Common Vulnerabilities and Exposures). An unpatched vulnerability in a base image that ships to production is a security risk that enterprises will flag during security audits.

> **CVE (Common Vulnerabilities and Exposures):** A standardized identifier for known security vulnerabilities in software libraries and dependencies.

**Container image scanning:**

Tools like Amazon ECR's built-in scanner, Snyk, or Trivy scan every image for known CVEs in its layers. Each scan produces a report: critical vulnerabilities, high, medium, low. Enterprise contracts may specify:

- "No critical CVEs in production images"
- "All critical and high CVEs must be remediated within 30 days of discovery"

**What this means for the PM:**

Upgrading base images (e.g., updating from `node:18.12-alpine` to `node:20-alpine`) is not just a technical upgrade — it's a security maintenance activity that affects compliance status. A PM whose enterprise customer has a CVE clause in their contract needs to track:

- How frequently are base images updated?
- Are all critical CVEs in current production images remediated?
- Does the CI pipeline block deploys with unresolved critical vulnerabilities?

---

⚠️ **Three compliance-relevant questions to ask your team before signing enterprise contracts:**

| Question | Why it matters |
|---|---|
| **CVE scanning:** Does our CI pipeline scan images for vulnerabilities before deploying to production? Do critical CVEs block the deploy? | Prevents shipping known vulnerabilities to customers |
| **Secrets hygiene:** Are there any API keys, database passwords, or tokens baked into Docker images or committed to the git repository? All secrets should be in Kubernetes Secrets, injected at runtime. | Prevents credential exposure in container images and version control |
| **Audit trail:** Can we produce a report showing which image version was running in production on a specific date, and who pushed it? ECR provides this — but only if the team uses tagged, versioned images (not `latest` tags, which don't track provenance). | Satisfies enterprise security audit requirements and enables incident investigation |
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge. Understands Docker image layers, multi-stage builds, resource limits, container registries, and the configuration injection pattern.
# This level debates, doesn't explain.
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Environment variable mismatch — staging passes, production fails

**The scenario:**
A feature flag controlling a new payment flow is enabled in staging via an environment variable: `NEW_PAYMENT_FLOW=true`. Staging QA passes. The image is promoted to production. In production, the environment variable isn't set — it defaults to `false`. The new payment flow never appears. No error is thrown.

**What happens:**
- Feature appears non-functional in production
- Engineers spend 2 hours debugging
- Root cause: environment variable mismatch between environments

**PM prevention checklist:**
- [ ] Environment variable specification is part of feature acceptance criteria
- [ ] Document required configuration values for each environment
- [ ] Specify default values and their behavior
- [ ] Assign ownership for pre-deploy environment configuration
- [ ] Deploy checklist verifies production environment variables before feature-flag rollouts

---

### OOMKilled container degrading silently

**The scenario:**
The Paathshala class service has a memory leak — a cache that grows unboundedly. Kubernetes kills and restarts the pod when it hits the limit. Each restart takes 5 seconds.

| Stage | Frequency | User Impact | Detection |
|-------|-----------|-------------|-----------|
| Week 1 | One restart/week | Invisible | None |
| Week 4–8 | One restart/day | Minor | Support tickets appear |
| Week 12+ | One restart/hour | Recurring 5-sec disruptions | Developer notices high restart counts in Lens |

**Why this matters:**
Recurring 5-second disruptions during live classes are a direct user experience problem, not an abstract infrastructure concern.

**PM prevention checklist:**
- [ ] OOMKilled events monitored with active alerting (not just dashboards)
- [ ] Memory limit set for every new service
- [ ] OOMKill alerts configured before production deployment
- [ ] Restart rate tracked as a reliability metric
- [ ] Baseline and threshold defined for alert triggers

---

### Stale CDN combined with container rollback

**The scenario:**
A deploy introduces a frontend bug — buttons in the wrong positions. The backend image is rolled back instantly. But the JavaScript served to users comes from CloudFront's cache — the new (buggy) version is cached at CDN edge locations for 24 hours.

| System | Rollback Status | Resolution Time |
|--------|-----------------|-----------------|
| Kubernetes (backend) | ✓ Rolled back instantly | Immediate |
| CloudFront (frontend assets) | ✗ Still serving cached buggy version | 5–10 min for cache invalidation |
| User experience | ❌ Broken UI persists | 24 hours without manual action |

**Why this matters:**
These are two different systems. A rollback that addresses only one leaves the other in an inconsistent state.

**PM prevention checklist:**
- [ ] Incident runbook for frontend services includes "invalidate CDN cache" as a distinct step
- [ ] "Roll back container image" and "invalidate CDN cache" are listed as separate actions
- [ ] Deployment runbook specifies which systems need coordination
- [ ] On-call rotation trained on both Kubernetes and CDN workflows

## S2. How this connects to the bigger system

### Kubernetes (03.03)

**What:** Containers are the fundamental unit that Kubernetes orchestrates.

**Key concepts:**
- Pod = running container (or small group of co-running containers)
- Deployment = specification of which container image to run and replica count
- Kubernetes operations: deployment, scaling, recovery all depend on container understanding

**Why it matters:** Understanding containers is the prerequisite for understanding how Kubernetes makes deployment, scaling, and recovery decisions.

---

### CI/CD Pipelines (03.04)

**What:** The CI/CD pipeline automates the container build and deployment workflow.

| Stage | Action | Container Relevance |
|-------|--------|---------------------|
| Merge to main | Triggered | — |
| Code build | Compile/prepare code | — |
| Run tests | Validation | — |
| Build Docker image | Create container | **Performance critical** |
| Push to ECR | Store image | — |
| Deploy to staging | Run container | — |

**Performance lever:** Docker build optimization (layer caching, base image size) directly impacts pipeline speed.

---

### Monitoring & Alerting (03.09)

**What:** Container health produces specific signals that must be monitored and alerted on.

**Critical container signals:**
- **CPU throttling** — container hit its CPU limit
- **OOMKill events** — container hit memory limit
- **Restart counts** — container crash-looping
- **Image pull errors** — ECR unreachable

**Tools & visibility:** New Relic (APM), Kibana (logs), Lens (Kubernetes) provide visibility into these signals — **only if alerting is configured for signals that matter.**

---

### CDN & Edge Caching (03.07)

**What:** Frontend container deployments and CDN cache invalidation must be coordinated as a single operation.

| System | Responsibility | Timing |
|--------|-----------------|--------|
| Kubernetes | Deploy new container image | When pod restarts |
| CloudFront (CDN) | Invalidate old static asset caches | Must happen in sync |

**Why it matters:** Container holds both server-side rendering logic and static assets. New image deployment requires simultaneous CDN cache invalidation to achieve consistent deployment state.

---

### Feature Flags (03.10)

**What:** Feature flags can be implemented two ways, each with different container lifecycle implications.

| Approach | Implementation | Effect Timing | Container Impact |
|----------|-----------------|----------------|-----------------|
| Environment variables | Config passed to pod | Requires pod restart | Slower (Kubernetes restarts pod) |
| Service-side toggle | Application fetches flag state | Immediate | Instant (no restart needed) |

**Decision factor:** For kill switches requiring instant activation during incidents, service-side flags are necessary.

## S3. What senior PMs debate

### Monolith vs microservices: when does containerization make a monolith worse?

**The case: BrightChamps' 11 microservices**

| Benefit | Cost |
|---------|------|
| Independent deployment | 11 Docker images to build |
| Independent scaling | 11 deployment pipelines to maintain |
| Fault isolation | 11 sets of resource limits to tune |
| | 11 services to monitor |

> **Operational overhead:** The real cost of microservices isn't eliminated by containers—it's made manageable, but not negligible.

**The competing model: modular monolith**

A single well-organized deployable unit (one container) can deliver:
- Faster deploys
- Simpler debugging
- Lower operational overhead

...compared to 11 containers with 11 deployment pipelines.

**The senior PM question:**

For each proposed new service: *"Does this actually need to be a separate container, or does it add more deployment complexity than the isolation benefit justifies?"*

*What this reveals:* Are you measuring the true cost of operational complexity, not just architectural purity?

---

### WebAssembly and the post-Docker future: is container isolation enough?

⚠️ **Security limitation:** Docker containers share the host operating system kernel. A container with a kernel-level vulnerability can potentially affect the host or other containers.

**When kernel-level isolation fails:**

Security-sensitive workloads move beyond containers:
- **VMs** — slower but fully isolated
- **gVisor** — user-space kernel that intercepts container syscalls
- **WebAssembly** — untrusted code in sandboxed environment outside OS entirely

> **WebAssembly (WASM):** A deployment target for edge functions and untrusted code execution with microsecond startup times (vs container seconds), full portability across any WASM runtime, and strict sandboxing by design.

**Platform examples:**
- Fastly
- Cloudflare
- Fermyon

**The senior PM question:**

For which categories of feature does WASM's isolation and startup advantage make it the right deployment model over containers?
- User-submitted content execution
- Edge personalization
- Partner integrations

*What this reveals:* Are you choosing deployment models based on threat model and performance requirements, not just "container for everything"?

---

### AI model serving — containers are being pushed to their limits

**The infrastructure mismatch:**

| Requirement | Container Design | Reality |
|-------------|------------------|---------|
| GPU memory for 70B model | Not designed for GPU scheduling | 140GB required (single A100 or multiple GPUs) |
| Startup time | Seconds (key advantage) | Model loading takes minutes |
| Request batching | Standard orchestration (Kubernetes) | Requires specialized schedulers (vLLM, TensorRT-LLM) |

⚠️ **Kubernetes limitation:** GPU-aware extensions exist, but Kubernetes wasn't originally designed for GPU scheduling at scale.

**The emerging architecture:**

Infrastructure split by workload type:

| Service Type | Infrastructure |
|--------------|-----------------|
| Student interaction summarizer (LLM-based) | Specialized GPU inference platform |
| Class recommendation engine (lighter ML) | Standard containerized service |

**The senior PM question:**

Should AI inference infrastructure be managed separately from standard container-based microservices?

**Build-vs-buy decision framework:**

- **Use managed inference API** (OpenAI, Anthropic, AWS Bedrock) — until volume justifies operational complexity
- **Self-host GPU serving** — when inference volume and cost structure demand it

*What this reveals:* Do you understand which parts of your AI stack can stay containerized and which need specialized infrastructure?