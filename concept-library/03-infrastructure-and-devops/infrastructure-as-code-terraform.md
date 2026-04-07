---
lesson: Infrastructure as Code
module: 03 — Infrastructure & DevOps
tags: tech
difficulty: foundation
prereqs:
  - 03.01 — Cloud Infrastructure Basics: IaC codifies cloud resources (EC2, RDS, EKS, VPCs); understanding what those resources are is required before understanding what Terraform declares
writer: staff-engineer-pm
qa_panel: Staff Engineer, Junior PM Reader
kb_sources:
  - technical-architecture/architecture/architecture-overview.md
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

## F1. The server no one can explain

### The Situation at BrightChamps

**Server:** `schola-production-new` (IP: 172.31.9.208)  
**Purpose:** Hosts PHP scripts for class reminders, Zoom link updates, payment processing  
**Status:** Two critical failures, unresolved for months

| Component | Failure | Details |
|-----------|---------|---------|
| `schola-etl` service | Completely down | MongoDB connection error since November 22, 2023 — never fixed |
| Payment instalment trigger | Failing | "Connection refused" on port 7600 — service no longer running; unknown when/why it stopped |

⚠️ **Critical risk:** No engineer knows how this server was originally configured. It was set up manually by engineers who are no longer at the company via direct SSH commands, undocumented cron jobs, and ad-hoc package installations.

### The Manual Configuration Problem

When infrastructure is built by hand:

- **Knowledge is trapped** — lives only in the heads of engineers who built it, plus the running server itself
- **Debugging requires reverse-engineering** — engineers must look at what's running, guess at original intent, and hope they don't break something else while investigating
- **Recovery is fragile** — if the server crashes completely (hardware failure, accidental deletion, region outage), recreation takes days of guesswork
- **Rebuilt servers drift** — different from the original, which means new bugs

> **Manual configuration problem:** Infrastructure built by hand carries hidden fragility because the decisions that created it were never documented in code.

### The Contrast: Infrastructure as Code

**BrightChamps' EKS Kubernetes cluster** runs all 11 microservices on AWS-managed infrastructure with a different approach:

| When Node Fails | Manual Server | Infrastructure as Code |
|---|---|---|
| **How does recovery work?** | Manual rebuild, guesswork, days | Automatic replacement |
| **Is new node identical?** | Probably slightly different — bugs result | Exactly identical — defined in code |
| **Where is the design stored?** | Engineer's memory, undocumented SSH history | Version control files |
| **Time to restore?** | Days | Minutes |

> **Infrastructure as Code:** The desired state of infrastructure is written in files stored in version control, enabling rapid, identical recreation.

### The Essential Difference

The difference between `schola-production-new` and the EKS cluster is **not** size or complexity. It is whether infrastructure was:
- **Built by hand** (fragile, knowledge-dependent, slow to recover)
- **Defined in code** (resilient, reproducible, fast to recover)

## F2. What it is — the blueprint that survives the fire

If a house burns down and all you have is your memory of what it looked like, you'll build something close but different. If you have the architect's blueprints, you can rebuild it exactly — same dimensions, same electrical plan, same plumbing. The blueprints survive the fire.

> **Infrastructure as Code (IaC):** Configuration files that describe what infrastructure should exist, stored in version control and made reproducible rather than relying on manual cloud console clicks or server commands.

Instead of clicking through the AWS console or SSH-ing into servers and running commands, engineers write configuration files stored in git — version-controlled, reviewable, shareable, and most importantly, reproducible.

### Terraform: The IaC Standard

> **Terraform:** The most widely used IaC tool that reads `.tf` configuration files and manages cloud resources to match declared state.

**The core workflow:**

| Step | Action | Output |
|------|--------|--------|
| **Declare** | Write `.tf` files describing desired infrastructure | Configuration files in version control |
| **Plan** | Run `terraform plan` — compare declaration vs. current state | Exact preview of all create/change/destroy actions |
| **Apply** | Run `terraform apply` — make the changes | Cloud environment matches code |

**Example declaration:**
```
I want an RDS MySQL database, size db.t3.medium, in VPC vpc-abc123, 
accessible only from the application servers.
```

### What Terraform Manages

For a system like BrightChamps, Terraform orchestrates:
- EC2 instances
- EKS clusters
- RDS databases
- S3 buckets
- Security groups
- VPCs
- Load balancers
- IAM roles
- Lambda functions
- CloudFront distributions

The entire AWS environment can be described in Terraform files and reproduced from those files alone.

### What Terraform Is NOT

Terraform **does not** configure what runs inside the infrastructure:
- ✗ Provisions EC2 instance but doesn't install software on it
- ✗ Creates EKS cluster but doesn't deploy application containers

Application deployment is handled by CI/CD pipelines (03.04) and Kubernetes configurations.

## F3. When you'll encounter this as a PM

### Scenario 1: Environment is broken, origin unknown
**The problem:** Manually configured infrastructure degrades without documentation. Recovery takes hours or days instead of the 15 minutes a `terraform apply` would take.

**Symptom to watch for:** Incident postmortem concludes "we couldn't reproduce the environment."

**PM action:** 
- Add "migrate this service to Terraform" to the next sprint after the incident
- Recognize both the sprint cost and the insurance value are real

---

### Scenario 2: Engineers request a new environment
**The ask:** "We need a staging environment that mirrors production"

| Without IaC | With IaC |
|---|---|
| 2-week manual configuration project | 2-hour project |
| Staging ≠ Production (structural drift) | `terraform apply` in new account = identical to production |

**PM action:** 
- Ask engineers: "Is our production infrastructure in Terraform?"
- If yes → fast, low-risk timeline
- If no → timeline estimate increases significantly

---

### Scenario 3: Disaster recovery planning
**The question:** "How long would it take to rebuild our infrastructure if the primary AWS region went down?"

| Without IaC | With IaC |
|---|---|
| Days, with incomplete documentation and manual recreation | Hours (run Terraform against new region) |

**PM action:** 
- Include this question in quarterly infra reviews
- Recognize the answer has direct SLA implications for customer commitments

---

### Scenario 4: "Infra work" appears in sprint planning
**What it is:** Writing Terraform configurations for existing manually-built infrastructure ("importing" existing infrastructure)

**Why it matters:**
- Shows no user value today
- Compounds value across: environment creation, incident recovery, engineer onboarding (read config instead of reverse-engineer)

**PM action:**
- Treat Terraform migration as technical debt repayment, not optional work
- Budget 10–15% of infra-related sprint capacity consistently
- Avoid all-at-once or never patterns
# ═══════════════════════════════════
# WORKING KNOWLEDGE
# For: Growth PM, Consumer Startup PM, B2B Enterprise PM, Ex-Engineer PM
# Assumes: Foundation level
# ═══════════════════════════════════

## W1. How Infrastructure as Code actually works — the mechanics that matter for PMs

> **Quick reference:** Terraform declares desired infrastructure state, compares to reality, and applies changes via a reviewable plan. The state file is the source of truth. Modules enable reuse. IaC makes environments cheap to create and cost-transparent.

### 1. The Terraform workflow — declare, plan, apply

Terraform operates on the same desired-state principle as Kubernetes: you declare what you want, and the tool reconciles reality to match. The difference is scope — Kubernetes manages running containers; Terraform manages the infrastructure those containers run on.

A simplified Terraform configuration for a BrightChamps RDS database looks like:

```
resource "aws_db_instance" "paathshala_db" {
  identifier        = "paathshala-production"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  multi_az          = true
}
```

**What this declares:** "There should be a MySQL 8.0 RDS instance called paathshala-production, on a db.t3.medium, with 100GB storage, in Multi-AZ mode."

Terraform reads this configuration, compares it to AWS, and creates or modifies the database to match.

#### The plan phase — visibility before change

**Before any change happens, `terraform plan` prints what it will do:**

```
+ create aws_db_instance.paathshala_db
  + engine = "mysql"
  + instance_class = "db.t3.medium"
  ~ multi_az: false → true   (change)
```

| Symbol | Meaning |
|---|---|
| `+` | Create |
| `~` | Change |
| `-` | Destroy |

**Why this matters:** The plan is reviewable — engineers see exactly what will happen before it happens. This safety mechanism prevents "I thought the command would only add a security rule, but it deleted the load balancer."

### 2. State file — Terraform's memory of what it built

Terraform tracks what it has created in a **state file** (`terraform.tfstate`). The state file maps configuration declarations to real AWS resources: "this `aws_db_instance.paathshala_db` declaration corresponds to RDS instance ID `db-abc123-xyz`."

The state file is the source of truth for what Terraform manages.

#### Remote state — preventing coordination disasters

> **Term — Remote state:** The state file must be stored in a shared location accessible to all engineers and CI/CD pipelines — typically an S3 bucket with DynamoDB locking.

**Why:** If two engineers have local copies of the state file and both run `terraform apply`, they'll create conflicting infrastructure. Remote state (S3 + lock) prevents this. 

⚠️ **Risk:** A team running Terraform with local state files is one miscoordination away from a production incident.

#### Drift — when reality diverges from code

⚠️ **Drift occurs when:** Someone makes a manual change in the AWS console (adds a security rule, increases an instance size) without updating the Terraform files. The state file and the real infrastructure are now out of sync.

**What happens next:** The next `terraform apply` may undo the manual change.

**Common question:** "Why did the security rule disappear?" — Often a Terraform drift incident.

**The fix:** Always make infrastructure changes through Terraform, never through the AWS console directly.

### 3. Modules — reusable infrastructure components

A Terraform module is a reusable component. Instead of writing the same RDS configuration for 11 microservices, engineers write one `rds_database` module and call it 11 times with different parameters.

**What modules enforce:** Consistency — all databases get the same encryption settings, backup retention policy, and security group structure.

**PM impact:** When engineers say "we have a standard module for new microservices," new service infrastructure setup is a day of work instead of a week. The first service is expensive to build. The tenth service is cheap — because modules capture the patterns.

### 4. Environments — IaC enables cheap environment parity

With infrastructure defined in Terraform, creating a new environment means running the same configuration with different variable values: `environment = "staging"` vs `environment = "production"`. Resources get different names (paathshala-staging vs paathshala-production) but identical structure.

| Dimension | Without IaC | With IaC |
|---|---|---|
| **Staging consistency** | Built manually — diverges from production over time | Created from production Terraform config — structurally identical |
| **Environment parity issues** | "Works in staging, broken in production" happens regularly | Environment parity is automatic — same config, same behavior |
| **Time to new environment** | 1–2 weeks of engineering work | 2–4 hours to run `terraform apply` |
| **Disaster recovery speed** | Days to rebuild in new region | Hours to rebuild in new region |
| **New engineer onboarding** | Read documentation (if it exists) | Read the Terraform files |

### 5. Cost visibility — Terraform as a cost ledger

Every resource in a Terraform configuration has a corresponding AWS cost. Tools like `infracost` read Terraform files and output the monthly cost delta before `terraform apply` runs.

**Example output:** "This change will add $142/month."

#### Cost-aware decision making

**PM implication:** Infrastructure changes have predictable, reviewable costs before they're applied.

**Real scenario:** "The engineer asked to upgrade the RDS instance class from db.t3.medium to db.t3.large" is a decision with a concrete cost attached: **+$50/month per environment**.

**Why it matters:** Cost-blind approvals compound. A PM who reviews infracost output before approving infrastructure changes makes better resource allocation decisions.

#### Common infrastructure costs

| Resource type | Approx monthly cost | Notes |
|---|---|---|
| db.t3.medium RDS (Multi-AZ) | ~$90 | Standard for small-medium services |
| db.t3.large RDS (Multi-AZ) | ~$180 | Doubles cost vs medium |
| EKS cluster (control plane) | ~$73 | Fixed per-cluster cost |
| m5.large EC2 / EKS node | ~$69 | Per node, regardless of utilization |
| S3 storage | ~$0.023/GB | Cheap for most use cases |
| CloudFront | ~$0.0085/GB transferred | CDN cost |

## W2. The decisions IaC forces

### Quick Reference
| Decision | Recommendation |
|---|---|
| Import existing infrastructure? | Start with highest blast radius (core production, legacy servers, shared networking) |
| Which IaC tool? | Terraform for most teams |
| Manual or CI/CD? | CI/CD for production; manual only for local experiments |

---

### Decision 1: When is it worth writing Terraform for existing infrastructure?

**The tradeoff:**
- **Upfront cost:** 1–3 days per service (read config, write Terraform, import, verify)
- **Recurring return:** Faster environment creation, faster incident recovery, easier onboarding, compliance evidence

**Import priority by scenario:**

| Scenario | Priority | Why |
|---|---|---|
| Core production services (databases, load balancers, EKS cluster) | HIGH | Highest blast radius if lost |
| Legacy servers with undocumented config (schola-production-new) | HIGH | Highest risk + lowest reproducibility |
| Shared networking (VPC, subnets, security groups) | HIGH | All services depend on this |
| Supporting services (monitoring, alerting) | MEDIUM | — |
| Rarely-changed one-off resources | LOW | — |

> **Recommendation:** Start with what has the highest blast radius. Legacy servers with failing services are the top priority.

---

### Decision 2: Terraform vs AWS CloudFormation vs CDK vs Pulumi

| Tool | Language | Cloud Support | Best for |
|---|---|---|---|
| **Terraform** | HCL (declarative config) | Multi-cloud (AWS, GCP, Azure) | Most teams; largest ecosystem; most tooling |
| **AWS CloudFormation** | YAML/JSON | AWS only | Teams already deep in AWS tooling |
| **AWS CDK** | TypeScript, Python, Java | AWS only | Engineers who prefer writing code over config |
| **Pulumi** | TypeScript, Python, Go | Multi-cloud | Teams who want real programming language features |

> **Recommendation:** Terraform for most teams. CDK/Pulumi if the team strongly opposes HCL and prefers Python/TypeScript. CloudFormation only for AWS-only shops minimizing external dependencies.

---

### Decision 3: Should Terraform run manually or in CI/CD?

**Manual apply (from laptop):**
- ✓ Lower barrier to entry
- ✗ Requires engineer to have AWS credentials
- ✗ Requires correct Terraform version locally
- ✗ Risk of applying wrong workspace
- ✗ No peer review; scales poorly as team grows

**CI/CD apply (GitHub Actions, Atlantis, etc.):**
- ✓ Every change goes through pull request
- ✓ Plan reviewed by second engineer
- ✓ Apply runs automatically on merge
- ✓ Infrastructure changes get same rigor as code changes
- ✓ Audit trail and consistency

> **Recommendation:** Terraform should run in CI/CD for all production changes. Manual apply from laptops is acceptable for local experiments only. "We run Terraform from laptops" is an operational risk that scales badly as the team grows.

## W3. Questions to ask your engineer

### Quick Reference
| Question | What It Reveals | Red Flag |
|----------|-----------------|----------|
| IaC tool in use? | Reproducibility baseline | No IaC for critical services |
| State file location? | Safety of parallel changes | Local state storage |
| Regional failover timeline? | DR feasibility | "We don't know" or >24 hours |
| Drift detection? | Source of truth status | No automated drift checks |
| Env separation? | Staging/prod parity | Shared config without variables |
| Legacy infrastructure? | Migration risk | Unplanned manual systems |
| New service provisioning time? | Module maturity | >1 week per service |

---

**1. Is our production infrastructure defined in Terraform, CloudFormation, or another IaC tool?**

*What this reveals:* The reproducibility baseline. If the answer is "partially" or "no," ask which services are most critical and whether they're covered.

⚠️ **Risk:** A team with no IaC for their database layer is one region failure away from a days-long recovery.

---

**2. Where is the Terraform state file stored — locally or in a remote backend like S3?**

*What this reveals:* Whether parallel infrastructure changes are safe. Local state means one engineer's apply can conflict with another's.

> **Correct answer:** "Remote state in S3 with DynamoDB locking. Only CI/CD can apply to production."

---

**3. If our primary AWS region went down right now, how long would it take to rebuild in a new region?**

*What this reveals:* The practical disaster recovery timeline and SLA commitments to customers.

| With IaC | Without IaC |
|----------|-----------|
| "A few hours — run apply in us-west-2 and update DNS" | "We don't know — we'd have to recreate everything manually" |

---

**4. Are we tracking infrastructure drift — whether anyone is making manual changes to AWS outside of Terraform?**

*What this reveals:* Whether the Terraform files are the real source of truth or aspirational documentation.

> **Correct answer:** "We run `terraform plan` in CI on a schedule. Any drift triggers an alert."

---

**5. Do we have separate Terraform configurations for staging and production, or a shared one with environment variables?**

*What this reveals:* Whether staging actually mirrors production.

> **Correct answer:** "Shared configuration with environment-specific variable files. Running apply for staging uses the same modules as production, just with different names and smaller instance sizes."

---

**6. What infrastructure does `schola-production-new` run that isn't yet in Terraform, and what's the plan for migrating it?**

*What this reveals:* The specific legacy risk on the team's radar.

⚠️ **Real example:** The `schola-production-new` server has two critical failures that have persisted for months because no one can safely modify a manually-configured system. If the team doesn't have a migration plan, that's a backlog item worth adding.

---

**7. When we need to provision infrastructure for a new microservice, how long does that take today?**

*What this reveals:* Whether module abstractions exist.

| Timeline | Interpretation |
|----------|-----------------|
| ~1 day (mostly code review) | Standard modules exist |
| 2+ weeks | Modules are missing; each service provisioned from scratch |

## W4. Real product examples

### BrightChamps — the cost of unmanaged infrastructure

**The `schola-production-new` failure mode:**

| Service | Status | Root Cause | Duration |
|---------|--------|-----------|----------|
| `schola-etl` | DOWN | MongoDB connection error | Since Nov 22, 2023 (4+ months) |
| Payment instalment trigger | FAILING | Port 7600 connection refused | Ongoing |

These aren't complex bugs—they're configuration failures on a manually-built server where the original setup is undocumented.

**What IaC would have changed:**

If the server had been provisioned with Terraform and configured with Ansible or Packer:
- Configuration would be version-controlled
- Engineers could read the configuration file to understand exact setup
- Problems could be diagnosed by comparing configuration to current state
- Instead: service down 4+ months while engineers work around it

**PM implication:** 

The two failures have been open for months not because they're hard to fix, but because no one can safely change a system they didn't build and can't fully understand. The sprint cost to migrate this server to Terraform (2–3 days) is offset by months of engineer time spent working around failures and ongoing business risk of a broken payment trigger.

---

### BrightChamps — EKS as the IaC success model

**What AWS manages on BrightChamps' behalf:**

The architecture-overview KB documents BrightChamps' use of:
- AWS EKS (managed Kubernetes)
- RDS (managed MySQL)
- S3, SQS, Lambda, CloudFront

For managed AWS services, configuration is defined through API calls—exactly what Terraform automates. Each service can be declared in Terraform files and reproduced in minutes.

**The contrast:**

| Aspect | EKS | schola-production-new |
|--------|-----|----------------------|
| **Reproducibility** | Can be reproduced | Cannot be reproduced |
| **Setup method** | Declarative configuration | Manual |
| **Key difference** | Built with IaC | Built without IaC |

The difference is not which service is more important—it's which was built with declarative configuration.

---

### Airbnb — Terraform at scale

**How Airbnb uses IaC:**

Airbnb's infrastructure team maintains Terraform configurations for thousands of AWS resources across multiple regions:
1. Every infrastructure change goes through code review (same process as application code)
2. Terraform runs in CI/CD with automated `plan` output in pull requests
3. Engineers review the plan before approving the merge

**PM implication:** 

At scale, "infrastructure is code" means infrastructure changes are subject to the same quality controls as application code—review, test, staged rollout. A PM can ask "what's the plan for this infrastructure change?" and get a reviewable document (`terraform plan` output) rather than a verbal description.

---

### Enterprise B2B — IaC as a compliance requirement

⚠️ **Security & Compliance:** Manual AWS console changes leave no audit trail visible to auditors. This creates compliance risk for enterprise deals.

**What SOC 2 and ISO 27001 require:**

Enterprise compliance frameworks require evidence that infrastructure changes are:
- Reviewed
- Approved
- Logged
- Reversible

Terraform in CI/CD creates a complete audit trail: every infrastructure change is a git commit, linked to a pull request, with reviewer approval and a plan showing exactly what changed.

**Three compliance-relevant questions to ask before an enterprise audit:**

> **Change control:**
> "Can we produce a history of every infrastructure change made in the last 12 months, with who approved it?"
> 
> *With Terraform in CI/CD: yes, via git history.*

> **Environment consistency:**
> "Is our staging environment structurally identical to production?"
> 
> *With shared Terraform modules: yes, provably.*

> **Disaster recovery:**
> "Do you have documented, tested procedures to rebuild your infrastructure?"
> 
> *With Terraform: the procedure is `terraform apply` and the documentation is the code itself.*

**PM implication:** 

Enterprise deals often stall at the security review stage, not the product evaluation stage. A company that cannot answer these three questions with evidence—not assurances—loses enterprise contracts to competitors who can. IaC is infrastructure investment that pays off in sales cycles.

**Pre-enterprise-readiness checklist addition:**
- ✓ IaC coverage for all production infrastructure
- ✓ SOC 2 certification
- ✓ Penetration testing results
# ═══════════════════════════════════
# STRATEGIC DEPTH
# For: Senior PM, Head of Product, AI-native PM
# Assumes: Working Knowledge
# ═══════════════════════════════════

## S1. The failure patterns that actually happen

### Failure pattern 1: State file corruption — the infrastructure amnesia

**The incident:**
A team stores their Terraform state in S3 but without versioning enabled. An engineer runs `terraform apply` with an incorrect configuration — it creates some resources, fails partway through, and leaves the state file in a partially-updated state. Now the state file doesn't accurately represent what exists in AWS. The next `terraform plan` shows incorrect changes. Engineers start making manual AWS console fixes to compensate. The state file diverges further from reality. Eventually no one trusts Terraform and teams start bypassing it.

**What this reveals:** State file management failures typically cascade from misconfiguration at setup time, not from operator error during use.

**PM prevention role:**
- State file management is an infrastructure reliability task that belongs in **onboarding and architecture review** — not discovered during an incident
- The correct setup (S3 versioning, DynamoDB locking, restricted write access) takes hours to configure and prevents weeks of untangling
- **Before the first `terraform apply` runs**, ask: "How is the state file managed?"

---

### Failure pattern 2: Terraform plan says "destroy production database"

**The incident:**
An engineer refactors a Terraform module to rename a resource. Terraform sees a resource with the old name being removed and a resource with the new name being created — destroy the old, create the new. If the resource is an RDS database, "destroy" means the data is gone. This is a real class of incident: Terraform refactoring that accidentally schedules a deletion.

**What this reveals:** IaC tooling executes exactly what you specify, not what you intended — and refactoring looks like deletion to the system.

**PM prevention role:**
- Any Terraform plan that includes a `-` (destroy) line on a data-bearing resource must be reviewed by a senior engineer before apply
- **Write the policy before the incident:** "Destroy on RDS or S3 requires explicit engineering manager approval" in the PR review process
- This one-line policy prevents this entire class of incident

---

### Failure pattern 3: IaC coverage gaps — the "known safe" zones that aren't

**The incident:**
A team Terraform-manages their EKS cluster and RDS databases. The networking layer (VPCs, subnets, security groups, route tables) was set up two years ago and "we're afraid to touch it." Security groups accumulate manual changes over time. An audit finds security group rules that no one can explain. The networking layer is the highest-blast-radius infrastructure — a misconfigured security group can expose the production database to the public internet.

**What this reveals:** Manual infrastructure persists in "trusted" older layers and becomes an untrackable attack surface.

⚠️ **Risk:** Networking layer is highest blast-radius infrastructure. A single misconfigured security group can expose the production database to the public internet.

**PM prevention role:**
- Track IaC coverage explicitly in quarterly infrastructure reviews
- **Ask:** "What percentage of our AWS resources are Terraform-managed?"
- **Target:** Answer should trend toward 100% for production infrastructure
- **Priority:** Any coverage gaps in high-blast-radius resources (networking, IAM, databases) must have explicit migration timelines

## S2. How this connects to the bigger system

| System | Connection | How IaC fits |
|--------|-----------|-------------|
| **Cloud Infrastructure Basics (03.01)** | IaC codifies cloud resources | Every EC2 instance, EKS cluster, RDS database, and Lambda function has a corresponding Terraform resource type. `aws_eks_cluster` creates what 03.01 describes as EKS. |
| **CI/CD Pipelines (03.04)** | Enforcement mechanism for changes | `terraform plan` runs on PR; `terraform apply` runs on merge to main. Infrastructure changes get automated testing and review like application code. |
| **Kubernetes (03.03)** | EKS cluster itself is a Terraform resource | Node group configuration, IAM roles, VPC settings, and add-ons are declared in Terraform. Cluster version upgrades go through code review → plan → apply with rollback path. |
| **Monitoring & Alerting (03.09)** | Observability codified alongside infrastructure | CloudWatch alarms, integrations, and index patterns become Terraform-managed. Service provisioning and monitoring configuration happen together in one `terraform apply`. |

## S3. What senior PMs debate

### HCL vs real programming languages — the IaC language wars

| Dimension | HCL (Terraform) | Real Languages (CDK/Pulumi) |
|-----------|-----------------|------------------------------|
| **Expressiveness** | Purpose-built, declarative only | Full programming language features |
| **Loops & logic** | Limited workarounds | Native `for`, conditionals, functions |
| **Type safety** | No type checking | Full type checking & IDE support |
| **Learning curve** | Lower ceiling, higher floor | Steeper learning curve, higher ceiling |
| **Code review** | Predictable, easy to audit | Risk of opaque dynamic logic |
| **Test frameworks** | Limited | Full testing infrastructure |

> **The staffing tradeoff:** Terraform favors *breadth* (any engineer can read and modify it); CDK/Pulumi favor *depth* (strong programmers write superior infrastructure).

**For senior PMs:** This choice should align with your team's composition. Teams with junior or generalist engineers benefit from HCL's guardrails. Teams with strong developers benefit from CDK/Pulumi's expressiveness.

---

### GitOps for infrastructure — is "git as the source of truth" the right model at scale?

**What GitOps requires:**
- Git is the single source of truth for all infrastructure state
- Automated systems (Atlantis, ArgoCD) continuously reconcile running environment to git state
- All changes require a PR; manual console changes are automatically reverted

**The tension:** GitOps removes emergency manual fixes.

| Scenario | GitOps approach | Traditional approach |
|----------|-----------------|----------------------|
| Production incident, fastest fix is a security group change | Open a PR (slower) | Modify console immediately (faster) |
| Audit requirement | Full recorded history in git | Manual changes hard to trace |
| Team velocity | Structured but slower | Faster but riskier |

⚠️ **Risk tradeoff:** Teams implementing strict GitOps must maintain emergency break-glass procedures with complete audit trails to handle critical incidents without bypassing the system.

**For PMs — choose based on:**
- **Heavily regulated enterprises** → GitOps (auditability & reproducibility win)
- **Fast-moving startups** → May find GitOps slows incident recovery unacceptably

---

### AI-generated Terraform — present reality, not future novelty

**Current state:** Engineers use Claude, GPT-4, and GitHub Copilot to write Terraform today. This is established practice, not a future trend.

> **The output quality:** First drafts are typically 80% correct. The remaining 20% is where the risks concentrate.

**The critical failure mode:**

⚠️ **Security blind spot:** AI-generated Terraform looks correct to engineers unfamiliar with specific resource types. High-risk categories:
- **IAM policies** — overly permissive (wildcards instead of specific permissions) or unintended cross-account access
- **Security groups** — rules like `0.0.0.0/0` ingress on port 22 (open SSH to the internet) appear as minor details in 200-line configs
- **Secrets management** — credentials or sensitive data inadvertently exposed

**Documented incidents:**
- Teams without security specialist review shipped infrastructure with IAM permissions allowing any EC2 instance to read any S3 bucket
- Functional testing doesn't catch these — the infrastructure "works" but is dangerously over-permissioned

---

### Code review policy for AI-assisted infrastructure

> **Mandatory security gates for AI-generated IaC:**
> 1. **All AI-generated Terraform** must be reviewed by an engineer who can explain every line — not approve because it "looks reasonable"
> 2. **IAM policies and security group rules** generated by AI require explicit security review, separate from standard PR approval
> 3. **Networking, permissions, or secrets management configs** must pass `tfsec` (static security analysis) before merge

---

### PM implications: the economics shift

**Before AI-assisted infrastructure:**
- New service provisioning: ~8 hours
- Cost argument: "We don't have time to write Terraform"
- IaC adoption was optional for resource-constrained teams

**With AI-assisted infrastructure:**
- New service provisioning: ~2 hours
- Cost barrier to IaC adoption is significantly lower
- The staffing argument for "we can't afford IaC" weakens

**What this reveals:** The business case for IaC adoption is stronger than 18 months ago — but the security review requirement remains non-negotiable.