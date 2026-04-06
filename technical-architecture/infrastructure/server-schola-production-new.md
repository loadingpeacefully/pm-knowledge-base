---
title: Server 172.31.9.208 — schola-production-new
category: technical-architecture
subcategory: infrastructure
source_id: c958af00-c7ea-4c41-bf82-7a4e7a6060db
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Server 172.31.9.208 — schola-production-new

## Overview
This document catalogs the scheduled cron jobs, service statuses, and known failures running on the legacy `schola-production-new` server (172.31.9.208), which hosts PHP-based scripts for class management, Zoom operations, SSL renewal, and legacy ETL integrations.

## API Contract
- **Payment Instalment Trigger**: `GET http://localhost:7600/api/alepay/instalment/triggerSchedule` — **FAILING** (connection refused on port 7600)
- **Google Sheet Sync (schola-etl)**: Internal service API — **DOWN** (crashed Nov 22, 2023 due to MongoDB connection error)

## Logic Flow
### Controller Layer
All jobs on this server are cron-triggered PHP scripts or curl-based health checks. No HTTP routing layer — jobs run directly via crontab.

### Service/Facade Layer
Jobs are organized into maintenance, class operations, and integrations:

**Active Scheduled Jobs:**

| Job | Script | Schedule | Status |
|-----|--------|----------|--------|
| Class Reminder | `RemindUpcomingClassesCommand.php` | Every hour at :15 and :45 | Active (Discarded next action) |
| Zoom Link Update | `UpdateZoomCommand.php` | Daily at 23:00 | Active (Discarded) |
| Class Status Update | `UpdateLiveClassStatusCommand.php` | Every hour at :15 and :45 | Active (Discarded) |
| Recurring Class Check | `CheckRecurringClassCommand.php` | Daily at 01:00 | Active (Discarded) |
| Zoom Deactivation | `UpdateZoomCommand.php` (alternate params) | Daily at 03:00 | Active (Discarded) |
| Backup File Cleanup | Removes DB backups older than 1 day | Daily at 00:45 | Active |
| Security/Malware Cleanup | `kill.sh` | Every minute | Active |
| SSL Certificate Renewal | `certbot` | Monthly on 1st at 00:00 | Active |

**Failing Services:**

| Job | Command | Schedule | Status | Root Cause |
|-----|---------|----------|--------|------------|
| Payment Instalment Trigger | `curl http://localhost:7600/api/alepay/instalment/triggerSchedule` | Daily at 20:45 | **FAILING** | Port 7600 connection refused |
| Google Sheet Sync (schola-etl) | Internal ETL service | Multiple times daily | **DOWN** | MongoDB connection error (crashed Nov 22, 2023) |

### High-Level Design (HLD)
This is a legacy server running PHP-era Schola platform jobs. All jobs are marked "DISCARDED" for next action, indicating migration away from this server is planned or in progress.

```
Crontab (system cron)
     │
     ├── PHP Scripts (RemindUpcomingClasses, UpdateZoom, UpdateLiveClassStatus, CheckRecurringClass)
     ├── Certbot (SSL renewal)
     ├── Cleanup scripts (backup purge, kill.sh malware cleanup)
     └── Curl trigger (Payment Instalment — FAILING on port 7600)
```

## External Integrations
- **Zoom** — `UpdateZoomCommand.php` manages zoom link lifecycle and license deactivation
- **MongoDB** — Legacy ETL dependency; connection failed Nov 22, 2023 causing `schola-etl` crash
- **Alepay** — Payment instalment trigger via localhost API on port 7600
- **Certbot / Let's Encrypt** — SSL certificate management
- **Google Sheets** — Target of `schola-etl` sync jobs (currently DOWN)

## Internal Service Dependencies
- `schola-etl` → MongoDB (broken connection)
- Payment Instalment Trigger → localhost:7600 service (service no longer running)

## Database Operations
### Tables Accessed
- DB backup directory (`db/`) managed by cleanup job
- MongoDB used by `schola-etl` (connection broken)

### SQL / ORM Queries
Not documented — PHP scripts manage their own DB interactions.

### Transactions
N/A

## Performance Analysis
### Good Practices
- Certbot auto-renewal ensures SSL certificates don't expire
- Daily backup file cleanup prevents disk space exhaustion
- `kill.sh` running every minute provides continuous malware defense (though frequency should be validated)

### Performance Concerns
- `kill.sh` running every minute introduces constant process overhead
- Class reminder and status update scripts running every 30 minutes — unclear if idempotent

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | `schola-etl` has been DOWN since Nov 22, 2023 — Google Sheet sync broken for months |
| Critical | Payment Instalment Trigger FAILING — Alepay instalment schedule not executing |
| High | All active jobs marked "DISCARDED" — migration path not documented |
| High | Port 7600 service not running — unclear if decommissioned or crashed |
| Medium | MongoDB connection error unresolved — no auto-restart or health check configured |
| Low | PHP-era codebase on legacy server — technical debt for maintenance |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Investigate and restart or formally decommission the port 7600 Alepay service
- Document which microservice will take over each "DISCARDED" job
- Set up a MongoDB connection health check with auto-restart for `schola-etl`

### Month 1 (Architectural)
- Migrate all active PHP cron jobs to the appropriate new microservices (Paathshala, Doordarshan, Payments)
- Decommission the legacy schola-production-new server after all job migrations are complete
- Replace `kill.sh` approach with proper AWS WAF or server hardening

## Test Scenarios
### Functional Tests
- Class Reminder sends notifications at scheduled times
- Zoom Link Update correctly deactivates licenses at 03:00
- SSL renewal runs successfully on monthly schedule

### Performance & Security Tests
- Verify `kill.sh` does not introduce race conditions or false-positive process kills
- Audit backup file cleanup to ensure it targets only old backup files

### Edge Cases
- What happens if certbot renewal fails — is there a fallback or alert?
- What is the impact of `schola-etl` being down for months on downstream reporting?

## Async Jobs & ETL
- `schola-etl` is the primary ETL job on this server — currently DOWN since Nov 22, 2023 due to MongoDB failure
- Payment Instalment Trigger is a cron-triggered curl call — currently FAILING
