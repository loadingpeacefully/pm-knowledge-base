---
title: schola-new-scripts Server
category: technical-architecture
subcategory: infrastructure
source_id: 4e1f3957-8483-4ede-9160-6f6b4e287242
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# schola-new-scripts Server

## Overview
This document catalogs the scripts and automation jobs running on the `schola-new-scripts` server. Currently, the primary documented script is `trial_placement.py`, a Python script that handles trial placement workflows and sends results via Slack. The server is structured as a job tracking system with fields for job name, path, schedule, status, next action, and purpose.

## API Contract
N/A — This server hosts background scripts, not HTTP APIs.

## Logic Flow
### Controller Layer
Jobs are catalogued in a tracking table format. The single documented script runs on-demand or on a schedule (schedule data not populated in the source document).

### Service/Facade Layer
**Documented Script: `trial_placement.py`**

- **Purpose**: Handles the Trial Placement Flow — processes PNG and PDF files stored on the server, adds student/placement details to those files, and sends the compiled output to Slack with the appropriate "SM" tag
- **Status**: ACTIVE — script exists and is executable
- **Next Action**: **NEEDS TO MIGRATE** to either the `tryouts` or `prabandhan` repository (per recommendation from Aditya)
- **Documentation**: Atlassian wiki link available (access required)

### High-Level Design (HLD)
```
Trigger (schedule TBD)
        │
        ▼
trial_placement.py
        │
        ├── Read PNG/PDF files from server filesystem
        ├── Add student/placement details to files
        └── Send to Slack with "SM" tag
```

## External Integrations
- **Slack** — Delivery channel for processed trial placement files (with SM tagging)
- **Atlassian Wiki** — Documentation reference for this script (access-gated)

## Internal Service Dependencies
- **tryouts** or **prabandhan** — Target repository for migration of this script
- File system on schola-new-scripts server — source of PNG/PDF template files

## Database Operations
### Tables Accessed
Not documented — script appears to be file-based with Slack delivery rather than DB-driven.

### SQL / ORM Queries
N/A

### Transactions
N/A

## Performance Analysis
### Good Practices
- Script is actively tracked for migration — ownership and path are clear
- SM tagging in Slack ensures proper routing to relevant team members

### Performance Concerns
- Script runs on a legacy scripts server rather than within a microservice — no observability, no retry logic, no error alerting documented
- File-based processing without database tracking means no audit trail for placement operations

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Script needs migration from legacy server to `tryouts` or `prabandhan` repo — blocking proper observability |
| Medium | Schedule field not populated — unclear when/how frequently this script executes |
| Medium | No error handling or failure notification mechanism documented |
| Low | File-based processing with no audit trail in database |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Document the actual schedule/trigger for `trial_placement.py`
- Request access to Atlassian wiki and link it to this document

### Month 1 (Architectural)
- Migrate `trial_placement.py` to the `tryouts` or `prabandhan` microservice repository
- Replace file-based Slack delivery with a proper API-driven notification through Hermes (communications service)
- Add database logging for each trial placement run

## Test Scenarios
### Functional Tests
- `trial_placement.py` correctly processes PNG and PDF files
- Slack message arrives with correct SM tag and attached files
- Script fails gracefully when input files are missing

### Performance & Security Tests
- Verify script does not expose sensitive student data in Slack message body
- Check that PNG/PDF files are cleaned up from server after processing

### Edge Cases
- What happens if Slack API is unavailable during script execution?
- Behavior when the PNG/PDF template files on the server are corrupted or missing

## Async Jobs & ETL
- `trial_placement.py` is the sole documented job on this server — functions as a standalone async script delivering placement outputs to Slack
