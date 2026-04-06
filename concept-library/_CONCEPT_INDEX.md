# PM Concept Library — Instruction Manifest
# Architecture: v2 (3-level depth system). All new lessons must follow v2 spec.
# See CLAUDE.md for full v2 architecture: Foundation / Working Knowledge / Strategic Depth
#
# This file is the single source of truth for the entire curriculum pipeline.
# Claude Code reads this file when asked to "write the next lesson."
# Every lesson row declares everything needed — no inference, no clarification needed.
#
# Column definitions:
#   status     : — (not started) | draft | ready
#   writer     : staff-engineer-pm | senior-pm | cfo-finance | gtm-lead
#   qa-panel   : comma-separated list of QA personas
#   kb-sources : top 2 KB files to read first (from _REGISTRY.md)
#   angle      : the specific lens or key tension this lesson must resolve
#
# HOW TO USE:
#   "Write the next lesson" → find first row where status = —, load its full row, execute /new-lesson.
#   "Write lesson 03.04"   → find that specific ID, load its row, execute /new-lesson.
#   "Rewrite [lesson]"     → detect v1 format, execute /rewrite-lesson.
#   Never ask for clarification if the manifest row is complete.

---

## Module 01 — APIs & System Integration
Writer default: staff-engineer-pm
QA default: Staff Engineer + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 01.01 | What is an API | 01-apis-and-integration/what-is-an-api.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-get.md, architecture/architecture-overview.md | REST vs GraphQL vs gRPC — when each applies, PM decision lens |
| 01.02 | API Authentication | 01-apis-and-integration/api-authentication.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/auth-flow-revamp-student-dashboard.md, api-specifications/api-student-details-get.md | JWT vs API key vs OAuth2 — the security vs convenience tradeoff a PM must weigh |
| 01.03 | Webhooks vs Polling | 01-apis-and-integration/webhooks-vs-polling.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | infrastructure/notifications.md, infrastructure/sse-vs-websockets.md | Push vs pull — reliability, cost, and failure mode differences |
| 01.04 | Rate Limiting & Throttling | 01-apis-and-integration/rate-limiting-and-throttling.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-get.md, crm-and-sales/sales-flow.md | Why limits exist, how PMs spec them, what breaks when they're wrong |
| 01.05 | Idempotency | 01-apis-and-integration/idempotency.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | payments/payment-flow.md, payments/payment-initiation.md | Payment retries — why duplicate charges happen and how idempotency keys prevent them |
| 01.06 | API Versioning | 01-apis-and-integration/api-versioning.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-get.md, api-specifications/api-student-details-get.md | Breaking vs non-breaking changes — deprecation strategy PMs must understand |
| 01.07 | Pagination | 01-apis-and-integration/pagination.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-bulk-installments-get.md, infrastructure/zoom-demo-class-report-1.md | Cursor vs offset — why it matters for large datasets and mobile performance |
| 01.08 | API Gateway | 01-apis-and-integration/api-gateway.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, infrastructure/infra-monitoring.md | What it does, when to add one, PM implications for auth and rate limiting |
| 01.09 | Error Codes & Response Design | 01-apis-and-integration/error-codes-and-response-design.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-get.md, crm-and-sales/sales-flow.md | 4xx vs 5xx — what each means for product decisions, UX, and incident triage |
| 01.10 | Third-Party Integration Patterns | 01-apis-and-integration/third-party-integration-patterns.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | infrastructure/zoom-demo-class-report-1.md, infrastructure/whatsapp-customer-support.md | SDK vs API, fallback design, what happens when a vendor goes down |

---

## Module 02 — Databases & Data Systems
Writer default: staff-engineer-pm
QA default: Staff Engineer + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 02.01 | SQL vs NoSQL | 02-databases-and-data/sql-vs-nosql.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/database-design-doordarshan-meetings.md, architecture/architecture-overview.md | When to use which — tradeoffs a PM cares about, not a DBA |
| 02.02 | Indexing | 02-databases-and-data/indexing.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/rm-effectiveness-student-performance.md, infrastructure/zoom-demo-class-report-1.md | Why queries are slow, what indexes fix, how PMs spot the symptom |
| 02.03 | Transactions & ACID | 02-databases-and-data/transactions-and-acid.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | payments/payment-flow.md, payments/credit-system-and-class-balance.md | When data consistency matters — payment and booking scenarios |
| 02.04 | Caching (Redis) | 02-databases-and-data/caching-redis.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | etl-and-async-jobs/feed-post-creation-etl.md, infrastructure/infra-monitoring.md | What gets cached, TTL, cache invalidation — the PM's mental model |
| 02.05 | Data Warehouses vs Databases | 02-databases-and-data/data-warehouses-vs-databases.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | etl-and-async-jobs/etl-pipeline-inventory.md, etl-and-async-jobs/marketing-etl.md | OLTP vs OLAP — why metrics queries need a different system than product queries |
| 02.06 | ETL Pipelines | 02-databases-and-data/etl-pipelines.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | etl-and-async-jobs/etl-pipeline-inventory.md, etl-and-async-jobs/marketing-etl.md | How data moves between systems — PM implications for reporting lag and data quality |
| 02.07 | Schema Design Basics | 02-databases-and-data/schema-design-basics.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/database-design-doordarshan-meetings.md, payments/package-and-payments.md | Normalization, migrations — why schema decisions made in sprint 1 haunt you in year 2 |
| 02.08 | Soft Delete vs Hard Delete | 02-databases-and-data/soft-delete-vs-hard-delete.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-details-get.md, payments/credit-system-and-class-balance.md | Compliance, audit trails, undo — the product decision hiding inside a technical choice |
| 02.09 | PII & Data Privacy | 02-databases-and-data/pii-and-data-privacy.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | api-specifications/api-student-details-get.md, api-specifications/api-parent-student-create-or-update.md | Masking, encryption, GDPR basics — what a PM must spec, not just know |
| 02.10 | Data Replication & Backups | 02-databases-and-data/data-replication-and-backups.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | infrastructure/infra-monitoring.md, architecture/architecture-overview.md | RPO, RTO — what PMs need to spec for SLAs and incident recovery |

---

## Module 03 — Infrastructure & DevOps
Writer default: staff-engineer-pm
QA default: Staff Engineer + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 03.01 | Cloud Infrastructure Basics | 03-infrastructure-and-devops/cloud-infrastructure-basics.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, infrastructure/infra-monitoring.md | Servers, regions, AZs — what a PM needs for SLA conversations and incident context |
| 03.02 | Containers & Docker | 03-infrastructure-and-devops/containers-and-docker.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, infrastructure/web-app-optimization-champ.md | What a container is, why devs use it — the PM's mental model without Docker syntax |
| 03.03 | Kubernetes | 03-infrastructure-and-devops/kubernetes.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, infrastructure/infra-monitoring.md | Orchestration, pods, scaling — when K8s decisions affect PM delivery timelines |
| 03.04 | CI/CD Pipelines | 03-infrastructure-and-devops/cicd-pipelines.md | ready | staff-engineer-pm | Staff Engineer, Junior PM Reader | infrastructure/infra-monitoring.md, architecture/architecture-overview.md | How code gets from laptop to production — why deploy frequency is a product metric |
| 03.05 | Infrastructure as Code | 03-infrastructure-and-devops/infrastructure-as-code-terraform.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, infrastructure/server-schola-production-new.md | Terraform — what it is, why it matters for environment consistency and incident recovery |
| 03.06 | Queues & Message Brokers | 03-infrastructure-and-devops/queues-and-message-brokers.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | etl-and-async-jobs/feed-post-creation-etl.md, payments/payment-flow.md | SQS, Kafka — async jobs, fan-out patterns, why the payment confirmation isn't instant |
| 03.07 | CDN & Edge Caching | 03-infrastructure-and-devops/cdn-and-edge-caching.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | infrastructure/website-kt-and-docs.md, infrastructure/web-app-optimization-champ.md | Latency, static assets, global distribution — PM implications for international launches |
| 03.08 | Load Balancing | 03-infrastructure-and-devops/load-balancing.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, infrastructure/infra-monitoring.md | Horizontal scaling, traffic routing — what PMs need to understand for scale conversations |
| 03.09 | Monitoring & Alerting | 03-infrastructure-and-devops/monitoring-and-alerting.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | infrastructure/infra-monitoring.md, infrastructure/server-schola-production-new.md | SLAs, SLOs, SLIs — what PMs own vs what engineering owns |
| 03.10 | Feature Flags | 03-infrastructure-and-devops/feature-flags.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/login-flow-revamp.md, infrastructure/infra-monitoring.md | Staged rollouts, kill switches — the PM's most powerful deployment tool |

---

## Module 04 — AI & ML Systems
Writer default: staff-engineer-pm
QA default: Staff Engineer + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 04.01 | How LLMs Work | 04-ai-and-ml-systems/how-llms-work.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/pqs-architecture-project-document.md, student-lifecycle/trialbuddy-ai-powered-chatbot.md | Tokens, context window, temperature — PM vocabulary for AI product decisions |
| 04.02 | Prompt Engineering Basics | 04-ai-and-ml-systems/prompt-engineering-basics.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/pqs-architecture-project-document.md, student-lifecycle/trialbuddy-ai-powered-chatbot.md | System prompts, few-shot, chain-of-thought — what a PM needs to spec AI behavior |
| 04.03 | RAG | 04-ai-and-ml-systems/rag-retrieval-augmented-generation.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/trialbuddy-ai-powered-chatbot.md, student-lifecycle/pqs-architecture-project-document.md | Grounding LLMs in real data — when RAG vs fine-tuning, PM decision criteria |
| 04.04 | Embeddings & Vector Databases | 04-ai-and-ml-systems/embeddings-and-vector-databases.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/pqs-architecture-project-document.md, student-lifecycle/auxo-mapping.md | Semantic search, similarity matching — how PMs spec search and recommendation features |
| 04.05 | Fine-tuning vs Prompting | 04-ai-and-ml-systems/fine-tuning-vs-prompting.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/pqs-architecture-project-document.md, student-lifecycle/trialbuddy-ai-powered-chatbot.md | When to train, when to prompt — cost, time, and quality tradeoffs |
| 04.06 | AI Evals & Quality Scoring | 04-ai-and-ml-systems/ai-evals-and-quality-scoring.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/pqs-architecture-project-document.md, student-lifecycle/first-connect-pqs-review.md | How to measure LLM output quality — what a PM owns in an AI system's quality bar |
| 04.07 | Classification Models | 04-ai-and-ml-systems/classification-models.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/auxo-prediction.md, student-lifecycle/auxo-mapping.md | Binary classification, thresholds, precision/recall — PM tradeoffs in ML-driven features |
| 04.08 | Recommendation Systems | 04-ai-and-ml-systems/recommendation-systems.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/auxo-mapping.md, student-lifecycle/student-feed.md | Collaborative filtering, content-based, hybrid — when each fits, PM implications |
| 04.09 | AI Agent Patterns | 04-ai-and-ml-systems/ai-agent-patterns.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/trialbuddy-ai-powered-chatbot.md, student-lifecycle/welcome-call-through-ai-calling.md | Orchestration, tool use, multi-agent — how to scope and spec agentic products |
| 04.10 | AI Cost & Latency Tradeoffs | 04-ai-and-ml-systems/ai-cost-and-latency-tradeoffs.md | — | staff-engineer-pm | Staff Engineer, Junior PM Reader | student-lifecycle/pqs-architecture-project-document.md, student-lifecycle/trialbuddy-ai-powered-chatbot.md | Model size, batching, caching — PM decisions that directly control AI infrastructure cost |

---

## Module 05 — Product Fundamentals
Writer default: senior-pm
QA default: Senior PM + Staff Engineer + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 05.01 | PRD Writing | 05-product-fundamentals/prd-writing.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | product-prd/unified-migration-prd.md, student-lifecycle/unified-demo-paid-experience-student.md | What makes a PRD useful vs decorative — the sections engineers actually read |
| 05.02 | Jobs to Be Done | 05-product-fundamentals/jobs-to-be-done.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | product-prd/nano-skills.md, student-lifecycle/unified-demo-paid-experience-student.md | The framework and when to use it — how it changes what you build |
| 05.03 | Prioritization Frameworks | 05-product-fundamentals/prioritization-frameworks.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, product-prd/unified-migration-prd.md | RICE, MoSCoW — when frameworks help and when they launder bad decisions |
| 05.04 | User Story Writing | 05-product-fundamentals/user-story-writing.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | student-lifecycle/paid-joining-flow.md, student-lifecycle/unified-demo-paid-experience-student.md | Format, acceptance criteria, edge cases — what makes a story actionable |
| 05.05 | Roadmapping | 05-product-fundamentals/roadmapping.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, product-prd/unified-migration-prd.md | Now/next/later, outcome-based vs feature-based — why most roadmaps are fiction |
| 05.06 | Discovery vs Delivery | 05-product-fundamentals/discovery-vs-delivery.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | student-lifecycle/auxo-prediction.md, product-prd/pre-demo-engagement-game-v01.md | Dual-track — when to do what, and why mixing them kills both |
| 05.07 | Experimentation & A/B Testing | 05-product-fundamentals/experimentation-and-ab-testing.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | student-lifecycle/student-feed.md, performance-reviews/apr24-mar25-performance-review.md | Hypothesis, sample size, significance — what PMs must know to not be fooled by results |
| 05.08 | Technical Debt for PMs | 05-product-fundamentals/technical-debt-for-pms.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | infrastructure/web-app-optimization-champ.md, infrastructure/server-schola-production-new.md | How to evaluate, prioritize, and advocate — the PM's role in debt decisions |
| 05.09 | System Design Thinking | 05-product-fundamentals/system-design-thinking.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | architecture/architecture-overview.md, student-lifecycle/unified-demo-paid-experience-student.md | How PMs should read architecture diagrams — what to look for, what to question |
| 05.10 | Release Management | 05-product-fundamentals/release-management.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | infrastructure/infra-monitoring.md, student-lifecycle/login-flow-revamp.md | Phased rollouts, canary, feature flags — the PM's release decision framework |

---

## Module 06 — Metrics & Analytics
Writer default: senior-pm
QA default: Senior PM + CFO/Finance Lead + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 06.01 | North Star Metric | 06-metrics-and-analytics/north-star-metric.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, product-prd/nano-skills.md | How to define one, why most teams pick the wrong one, common traps |
| 06.02 | Funnel Analysis | 06-metrics-and-analytics/funnel-analysis.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | student-lifecycle/unified-demo-paid-experience-student.md, crm-and-sales/sales-flow.md | Conversion, drop-off, attribution — how to read a funnel without fooling yourself |
| 06.03 | Cohort Analysis | 06-metrics-and-analytics/cohort-analysis.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, payments/credit-system-and-class-balance.md | Retention curves, LTV segmentation — the most important analysis a PM never does |
| 06.04 | DAU/MAU & Engagement Ratios | 06-metrics-and-analytics/dau-mau-and-engagement-ratios.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, student-lifecycle/student-feed.md | Stickiness — what the ratios mean and when they lie |
| 06.05 | Event Tracking & Instrumentation | 06-metrics-and-analytics/event-tracking-and-instrumentation.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | student-lifecycle/paid-joining-flow.md, student-lifecycle/student-feed.md | How to spec events for engineers — the PM's job before build, not after |
| 06.06 | Statistical Significance | 06-metrics-and-analytics/statistical-significance.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, student-lifecycle/student-feed.md | p-values, confidence intervals — what PMs must know to not be fooled by A/B results |
| 06.07 | Dashboards & BI Tools | 06-metrics-and-analytics/dashboards-and-bi-tools.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | etl-and-async-jobs/marketing-etl.md, etl-and-async-jobs/etl-pipeline-inventory.md | Metabase, Looker, Mixpanel — what to expect, what to own, what to delegate |
| 06.08 | Lagging vs Leading Indicators | 06-metrics-and-analytics/lagging-vs-leading-indicators.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, student-lifecycle/auxo-prediction.md | How to pick early signals — before revenue moves, what moves first |
| 06.09 | Counter Metrics | 06-metrics-and-analytics/counter-metrics.md | — | senior-pm | Senior PM, CFO/Finance Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, student-lifecycle/student-feed.md | Guardrail metrics — preventing optimization traps when one metric improves another breaks |
| 06.10 | Data Quality & Pipelines | 06-metrics-and-analytics/data-quality-and-pipelines.md | — | senior-pm | Senior PM, Staff Engineer, Junior PM Reader | etl-and-async-jobs/etl-pipeline-inventory.md, infrastructure/infra-monitoring.md | Why metrics break, what PMs should audit — the unsexy work that makes everything else valid |

---

## Module 07 — Business & Monetization
Writer default: cfo-finance
QA default: CFO/Finance Lead + GTM Lead + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 07.01 | Unit Economics | 07-business-and-monetization/unit-economics.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | payments/package-and-payments.md, performance-reviews/apr24-mar25-performance-review.md | CAC, LTV, payback period — the mechanism behind each, not just the definition |
| 07.02 | Pricing Models | 07-business-and-monetization/pricing-models.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | payments/package-and-payments.md, payments/revamped-payment-page.md | Subscription, usage-based, freemium, marketplace — when each model fits |
| 07.03 | Gross Margin & COGS | 07-business-and-monetization/gross-margin-and-cogs.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, payments/package-and-payments.md | What a PM needs to know about P&L — which product decisions move the margin line |
| 07.04 | Monetization Design | 07-business-and-monetization/monetization-design.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | payments/revamped-payment-page.md, product-prd/nano-skills.md | Where to put the paywall, upgrade triggers — the product decisions that determine revenue |
| 07.05 | Payment Infrastructure | 07-business-and-monetization/payment-infrastructure.md | — | cfo-finance | CFO/Finance Lead, Staff Engineer, Junior PM Reader | payments/payment-flow.md, payments/payment-gateway-stripe.md | Gateways, webhooks, reconciliation — what a PM must understand to ship payments correctly |
| 07.06 | Marketplace Economics | 07-business-and-monetization/marketplace-economics.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | research-competitive/lingoace-tech-pedagogical-architecture.md, payments/sell-collection.md | Take rate, liquidity, supply/demand balance — the PM's role in marketplace health |
| 07.07 | Churn & Retention Economics | 07-business-and-monetization/churn-and-retention-economics.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | payments/credit-system-and-class-balance.md, performance-reviews/apr24-mar25-performance-review.md | Revenue churn vs user churn — why they diverge and what each signals |
| 07.08 | Subscription Mechanics | 07-business-and-monetization/subscription-mechanics.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | payments/payment-flow.md, crm-and-sales/renewal-crm.md | Billing cycles, trials, dunning, pausing — the edge cases that destroy LTV if unspecced |
| 07.09 | Virtual Currency & Rewards | 07-business-and-monetization/virtual-currency-and-rewards.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | product-prd/building-scalable-ecosystems-deck.md, student-lifecycle/student-feed.md | Engagement economy design — when virtual currency helps and when it inflates |
| 07.10 | Financial Modeling Basics | 07-business-and-monetization/financial-modeling-basics.md | — | cfo-finance | CFO/Finance Lead, GTM Lead, Junior PM Reader | performance-reviews/apr24-mar25-performance-review.md, payments/package-and-payments.md | Building a simple revenue model — what PMs need vs what finance needs |

---

## Module 08 — GTM & Growth
Writer default: gtm-lead
QA default: GTM Lead + CFO/Finance Lead + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 08.01 | Go-To-Market Strategy | 08-gtm-and-growth/go-to-market-strategy.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | research-competitive/lingoace-tech-pedagogical-architecture.md, performance-reviews/apr24-mar25-performance-review.md | ICP, channels, sequencing — the GTM decisions that happen before launch, not after |
| 08.02 | Product-Led Growth | 08-gtm-and-growth/product-led-growth.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | student-lifecycle/student-feed.md, product-prd/nano-skills.md | PLG loops — what qualifies as PLG and what doesn't, and how to know the difference |
| 08.03 | Growth Loops | 08-gtm-and-growth/growth-loops.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | student-lifecycle/student-feed.md, student-lifecycle/student-showcase-generating-project-videos-for-feed.md | Acquisition, engagement, retention, referral loops — how to identify and close a loop |
| 08.04 | User Onboarding Design | 08-gtm-and-growth/user-onboarding-design.md | — | gtm-lead | GTM Lead, Senior PM, Junior PM Reader | student-lifecycle/unified-demo-paid-experience-student.md, student-lifecycle/student-onboarding-dashboard-training.md | Activation events, time-to-value — the PM decisions that determine week-1 retention |
| 08.05 | Referral & Virality Mechanics | 08-gtm-and-growth/referral-and-virality-mechanics.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | student-lifecycle/student-showcase-generating-project-videos-for-feed.md, student-lifecycle/demo-certificate-sharing.md | k-factor, incentive design — when referral programs work and when they're wasted spend |
| 08.06 | SEO Basics for PMs | 08-gtm-and-growth/seo-basics-for-pms.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | infrastructure/website-kt-and-docs.md, research-competitive/lingoace-company-overview-leadiq.md | Organic growth, content strategy, indexability — what PMs must spec for SEO to work |
| 08.07 | Paid Acquisition Fundamentals | 08-gtm-and-growth/paid-acquisition-fundamentals.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | etl-and-async-jobs/marketing-etl.md, crm-and-sales/sales-flow.md | CAC by channel, ROAS, attribution — PM decisions that affect marketing efficiency |
| 08.08 | CRM & Sales Pipeline | 08-gtm-and-growth/crm-and-sales-pipeline.md | — | gtm-lead | GTM Lead, CFO/Finance Lead, Junior PM Reader | crm-and-sales/sales-flow.md, crm-and-sales/renewal-crm.md | Stages, handoffs, instrumentation — what PMs need to build to make sales effective |
| 08.09 | Internationalization & Localization | 08-gtm-and-growth/internationalization-and-localization.md | — | gtm-lead | GTM Lead, Staff Engineer, Junior PM Reader | student-lifecycle/dashboard-multi-language-support.md, infrastructure/website-kt-and-docs.md | What it means to build for global — the PM decisions that unlock or block new markets |
| 08.10 | Competitive Benchmarking | 08-gtm-and-growth/competitive-benchmarking.md | — | gtm-lead | GTM Lead, Senior PM, Junior PM Reader | research-competitive/lingoace-tech-pedagogical-architecture.md, research-competitive/lingoace-study-generated.md | Frameworks, what to track, what to ignore — turning competitor research into decisions |

---

## Module 09 — Security, Compliance & Scale
Writer default: staff-engineer-pm
QA default: Staff Engineer + Senior PM + Junior PM Reader

| ID | Lesson | File | Status | Writer | QA Panel | KB Sources | Angle |
|---|---|---|---|---|---|---|---|
| 09.01 | Authentication vs Authorization | 09-security-and-scale/authentication-vs-authorization.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | architecture/auth-flow-revamp-student-dashboard.md, api-specifications/api-student-details-get.md | Who you are vs what you can do — why the distinction matters for every feature spec |
| 09.02 | GDPR & Data Privacy for PMs | 09-security-and-scale/gdpr-and-data-privacy.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | api-specifications/api-student-details-get.md, api-specifications/api-parent-student-create-or-update.md | What compliance means in product decisions — the PM's checklist before shipping user data features |
| 09.03 | OWASP Top 10 for PMs | 09-security-and-scale/owasp-top-10-for-pms.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | api-specifications/api-feed-presigned-url-create.md, api-specifications/api-package-payment-details-get.md | Vulnerabilities PMs should know exist — how to ask the right security questions in a sprint |
| 09.04 | Scalability Patterns | 09-security-and-scale/scalability-patterns.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | architecture/architecture-overview.md, infrastructure/infra-monitoring.md | Horizontal vs vertical, stateless design — PM decisions that create or prevent scale problems |
| 09.05 | Incident Management | 09-security-and-scale/incident-management.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | infrastructure/infra-monitoring.md, infrastructure/server-schola-production-new.md | P0/P1/P2, runbooks, postmortems — what PMs own during and after an incident |
| 09.06 | Multi-Tenancy | 09-security-and-scale/multi-tenancy.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | architecture/architecture-overview.md, infrastructure/hubs-group-class-architecture.md | Shared vs isolated infra — what it means for enterprise product decisions and data isolation |
| 09.07 | Penetration Testing & Bug Bounty | 09-security-and-scale/penetration-testing-and-bug-bounty.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | api-specifications/api-feed-presigned-url-create.md, api-specifications/api-package-payment-details-get.md | What PMs should know — how to prioritize security findings and communicate risk |
| 09.08 | Accessibility (a11y) | 09-security-and-scale/accessibility.md | — | staff-engineer-pm | Staff Engineer, Senior PM, Junior PM Reader | infrastructure/web-app-optimization-champ.md, student-lifecycle/student-onboarding-dashboard-training.md | WCAG basics — why a11y is a product decision, not a design one |

---

## Pipeline instructions for Claude Code

When asked to "write the next lesson" or "write lesson [ID]":

1. Read this file
2. Find the target lesson row (next — = first row where status is —, or specific ID requested)
3. Load the following in order:
   - `.claude/skills/kb-reader.md`
   - `.claude/skills/writer-personas.md` → activate the persona declared in `writer` column
   - `.claude/skills/lesson-writer.md`
4. Read the 2 KB files listed in `kb-sources` column
5. Write the lesson using the activated writer persona and the angle declared
6. Run `.claude/skills/lesson-qa.md` → assemble panel from `qa-panel` column (not from tags alone)
7. Apply fixes per QA verdict
8. Save to the file path in `file` column
9. Update this file: change status from — to draft or ready
10. Update tasks.md

Never ask for clarification if all columns are filled. Execute directly.
