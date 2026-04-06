# Technical Architecture

All Coretech backend documentation — APIs, system flows, infrastructure, and ETL pipelines.
Sources from both NotebookLM notebooks merged here by content type.

## Subfolders

| Folder | Files | What's Inside |
|--------|-------|---------------|
| [architecture/](architecture/) | 3 | System architecture overview, DB design, auth flow |
| [api-specifications/](api-specifications/) | 41 | Named API endpoints + cryptic raw endpoint files |
| [payments/](payments/) | 15 | Payment flow, invoice generation, 7 payment gateways |
| [crm-and-sales/](crm-and-sales/) | 17 | Zoho CRM sync, lead/deal lifecycle, hot lead algorithm, Retell AI calling |
| [teacher-management/](teacher-management/) | 5 | Teacher change, LMS, onboarding, payout |
| [student-lifecycle/](student-lifecycle/) | 33 | Booking → demo → paid → class completion, feed, Auxo mapping |
| [etl-and-async-jobs/](etl-and-async-jobs/) | 4 | ETL pipelines, feed Lambda, marketing ETL |
| [infrastructure/](infrastructure/) | 14 | Web app performance, SSE, Hubs, WhatsApp, Zoom, monitoring |

## Key Security Findings (from api-specifications/)
- `api-feed-presigned-url-create.md` — Auth middleware **disabled** on S3 presigned URL endpoint
- `api-package-payment-details-get.md` — No auth + PII exposure via Base64 lookup
- `api-student-all-details-update.md` — 4-table update with **no DB transaction** (high risk)
- `api-referral-claim-create.md` — Race condition + missing transaction on gem award

## Core Microservices Map
| Service | Role |
|---------|------|
| Paathshala | Class management, curriculum |
| Eklavya | Student management, class balances |
| Prabandhan | CRM gateway (Zoho) |
| Chowkidar | Auth, user management |
| Doordarshan | Notifications, Zoom, meetings |
| Hermes | Messaging (WhatsApp, email, SMS) |
| Tryouts | Demo booking |
| Prashashak | Admin/teacher management |
