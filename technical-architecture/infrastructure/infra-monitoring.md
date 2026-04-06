---
title: Infrastructure Monitoring
category: technical-architecture
subcategory: infrastructure
source_id: 742c2a1d-bf74-4d01-b4cf-68e1e78efc88
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Infrastructure Monitoring

## Overview
This document is a daily operational tracker for BrightCHAMPS engineering teams, covering observability tooling, assigned monitoring responsibilities per microservice, known performance bottlenecks, active API issues, and resolved bugs. It functions as a living runbook rather than a static architecture document.

## API Contract
N/A — This is an operational monitoring tracker, not an API specification.

## Logic Flow
### Controller Layer
Monitoring is tool-driven and reactive: teams use New Relic, Kibana, and Lens to detect anomalies, then assign Jira tickets for resolution. Slack integrations serve as alerting channels for key service events.

### Service/Facade Layer
Monitoring assignments per service:
- **Eklavya** (Student service) — monitored via New Relic/Kibana
- **Platform** — monitored via New Relic/Kibana
- **Chowkidar** (Auth service) — monitored
- **Paathshala** (Class service) — monitored
- **Payment-structure** — OTEL (OpenTelemetry) added; Slack messages configured alongside logs
- **Prabandhan** (CRM service) — logs and Slack messages added via Jira tickets
- **Dronacharya** (Teacher service) — monitored

### High-Level Design (HLD)
```
Service Anomaly Detected
        │
        ▼
New Relic / Kibana Alert
        │
        ├── Slack notification triggered
        ├── Developer assigned via Jira
        └── Root cause analysis performed
                │
                ▼
        Fix deployed → Monitoring verified
```

## External Integrations
- **New Relic** — APM and performance monitoring
- **Kibana** — Log aggregation and search
- **Lens** — Kubernetes cluster monitoring
- **OpenTelemetry (OTEL)** — Distributed tracing instrumentation (added to payment-structure)
- **Slack** — Alert delivery and team notification channel
- **Jira** — Ticket tracking for fixes and observability improvements

## Internal Service Dependencies
- Prabandhan → `/v1/deal/create-db-crm-deal` (avg 1.26s — monitored for latency)
- Prabandhan → `update-crm-deal-to-closed-won` (avg 1.19s — monitored for latency)
- Doordarshan → future live meetings API (intermittent failures tracked)
- Paathshala → paid class joining link → Doordarshan API (guarded: blocked if >2 hours before start)
- Prashashak FE → reschedule API (duplicate calls fixed)

## Database Operations
### Tables Accessed
- No specific tables documented in this monitoring tracker
- Redis cache accessed by multiple services (Redis error logged for missing TTL parameters)

### SQL / ORM Queries
N/A — Monitoring tracker does not document query-level details.

### Transactions
N/A

## Performance Analysis
### Good Practices
- OTEL instrumentation added to payment-structure for distributed tracing
- Logs and Slack alerts co-deployed for payment and CRM services
- Calendar API and bulk class communications flagged proactively before production impact
- 2-hour guard on joining link creation prevents premature Doordarshan API calls

### Performance Concerns
- `/v1/deal/create-db-crm-deal` averages **1.26 seconds** — likely missing index or synchronous third-party call
- `update-crm-deal-to-closed-won` averages **1.19 seconds** — similar concern
- Tracker API and demo class join request stuck for **30 seconds** — possible timeout misconfiguration or blocking call
- Calendar API flagged for excessive response time
- Bulk class communications flagged for excessive processing time

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | CRM APIs averaging 1.2–1.3s response times — no caching or async offload |
| High | Tracker API with 30s timeouts — missing circuit breaker or timeout guard |
| Medium | Redis TTL not enforced uniformly — caused a caught but unexpected cache error |
| Medium | Prashashak FE calling reschedule API multiple times — redundant communication triggers |
| Low | Demo student phone number edit triggers unique constraint failure — missing upsert guard |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Add database indexes to CRM deal creation queries to bring response times below 500ms
- Fix Redis cache calls to always include TTL/duration parameter
- Add deduplication guard on Prashashak FE reschedule API calls

### Month 1 (Architectural)
- Implement circuit breakers on all inter-service calls to prevent 30s hangs
- Add async/queue-based processing for CRM deal updates to decouple from request cycle
- Introduce SLO dashboards in New Relic for each microservice (p95 latency, error rate)

## Test Scenarios
### Functional Tests
- Verify Slack alert fires when payment-structure logs an error
- Verify Doordarshan API is not called when joining link requested >2 hours before class start
- Verify duplicate reschedule API calls from Prashashak FE are deduplicated

### Performance & Security Tests
- Load test `/v1/deal/create-db-crm-deal` to establish baseline and verify <500ms target
- Stress test Redis cache under high concurrency to identify TTL edge cases

### Edge Cases
- What happens when New Relic agent is unavailable — is OTEL tracing still captured?
- Behavior when Slack webhook endpoint is down — are alerts lost silently?

## Async Jobs & ETL
- Slack message delivery is effectively an async alert mechanism integrated into service log pipelines
- OTEL traces feed into distributed tracing backend asynchronously
