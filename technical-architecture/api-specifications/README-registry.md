# API Specification Registry

All 27 sources from NotebookLM notebook `2c11acfe-fafc-4bb8-8381-c92ca2cb4353` processed and documented.

| # | Filename | Source ID | Endpoint | Auth | Key Topics |
|---|----------|-----------|----------|------|------------|
| 1 | `api-student-bulk-details-get.md` | `846d377a-7ee6-47bb-8a7d-c82093440a18` | `POST /v1/student/details/bulk` | API Key | Bulk student fetch by IDs; conditional JOINs; validator claims max 200 but not enforced |
| 2 | `api-student-details-get.md` | `4012dffc-aaa3-4b8f-b6f4-70132d560a47` | `GET /v1/student/details` | None | Single student + parent; opt-in PII masking via `isFe`; 4 external service calls |
| 3 | `api-student-filter-get.md` | `b890d6a5-68c4-455a-a111-9e59e5b3ae99` | `GET /v1/student/filter` | API Key | Two-stage name/parent search; returns IDs only; no input validation on filter param |
| 4 | `api-unified-data-students-query.md` | `33da7b0c-3388-4c7a-9a2e-ed3acad5fe56` | `POST /v1/unified-data/students` | JWT or API Key | Dynamic Sequelize passthrough; unrestricted DB access; major security risk |
| 5 | `api-student-get.md` | `b76ea6cf-fa89-4315-b2cc-3f63472524ef` | `GET /v1/student` | JWT or API Key | Flexible lookup by studentId/referralCode/objectId; enrichment flags |
| 6 | `api-student-class-balance-get.md` | `f9c7f5a2-e3c1-4ba8-9a03-d11c83d1af9e` | `GET /v1/student-class-balance` | None | Balance with optional teacher/student/language includes; no pagination; SELECT * |
| 7 | `api-unified-data-sale-payments-query.md` | `e9b4f90c-e1e1-4341-89c3-762c64463ad0` | `POST /v1/unified-data/sale-payments` | JWT or API Key | Same architecture as students query for SalePayment model; financial data risk |
| 8 | `api-badge-banner-notification-get.md` | `985eafbd-42e5-4b81-a1d7-9a9386018314` | `GET /v1/badges/badge-banner-notification` | JWT or API Key | Redis-only; no DB; key `eklavya:badges:notifications:parent:{parentId}`; TTL 30 days |
| 9 | `api-student-details-by-balance-ids-get.md` | `a260a6b0-f8a8-4496-939b-5db8c9648e23` | `POST /v1/student/details/balanceIds` | JWT or API Key | Reverse lookup via StudentClassBalance IDs; no input validation |
| 10 | `api-student-bulk-installments-get.md` | `120028ae-3bef-463d-afb0-95890d8ce10c` | `POST /v1/student/bulk-installments` | JWT or API Key | N+1 queries (10 IDs = ~50 queries); auto-package creation side effect during read |
| 11 | `api-badge-progress-summary-get.md` | `7f7e27d9-2546-44ee-a24e-b0c169a67484` | `GET /v1/badges/progress-summary` | JWT or API Key | Badge progress + ranking; Redis caching; non-participated badges get rank = total+1 |
| 12 | `api-student-course-teacher-details-get.md` | `2ad05a2c-5d9e-4794-b7ce-dc0d490c22da` | `GET /v1/student/get-course-teacher-details` | JWT or API Key | ACTIVE/PAST/INACTIVE filter; 4–5 external calls; INACTIVE fully dependent on Paathshala; no default pagination limit |
| 13 | `api-student-get-students-by-parent.md` | `3443f51d-e037-4f54-bb55-399304d908fe` | `GET /v1/student/get-students` | JWT | Parent-scoped; parentId from JWT; optional demoData + magicLink; Chowkidar + Tryouts |
| 14 | `api-system-spec-get.md` | `8b5495cd-76b8-48eb-bcb3-6134611ab40f` | `GET /v1/system-spec` | JWT or API Key | Device/performance analytics; schema-validated dynamic filter; no pagination |
| 15 | `api-user-get.md` | `4dfd6346-d5d7-4309-a825-1aeb3260b1c9` | `GET /v1/user` | JWT | Stateless JWT extraction; zero DB/Redis/external calls; < 10ms |
| 16 | `api-student-credit-transfer-request-create.md` | `40621b34-d8bd-471a-be12-1f76a3ae0bbb` | `POST /v1/student-credit-transfer/request` | None | class/diamond/gem transfer; RPC pricing; no transaction; race condition in duplicate check |
| 17 | `api-feed-presigned-url-create.md` | `29fb93b5-PENDING-FULL-UUID` | `POST /v1/feed/presigned-url` | NONE (auth commented out) | S3 presigned URL; Redis 60s cooldown; auth middleware disabled — CRITICAL |
| 18 | `api-referral-claim-create.md` | `94f3c928-PENDING-FULL-UUID` | `POST /v1/referral/claim` | None | Gem award (1 or 5); Tryouts dependency; race condition; no transaction |
| 19 | `api-package-cancel-sold.md` | `8f06f04b-6e73-48c4-907c-b85ac048957c` | `POST /v1/cancel-sold-package` | None | DB transaction; cancels unpaid installments; expires payment initiations; parent package restore |
| 20 | `api-package-payment-details-get.md` | `d9737249-9bd0-4fea-b787-68f45744040d` | `POST /v1/package-payment` | None | Base64-encoded payment initiation lookup; packages + addon materials + parent PII; no auth |
| 21 | `api-feed-showcase-ai-content-generate.md` | `eb9821a3-9f9c-4b01-9063-3bd8b4d64ef3` | `POST /v1/feed/showcase-title-and-desc` | JWT or API Key | OpenAI Whisper transcription; custom LLM caption; S3 upload; parallel execution; no rate limit |
| 22 | `api-student-bulk-get-by-referral.md` | `3f04ceca-5a9f-480d-96c7-cd4d91365c03` | `POST /v1/student` | None | Bulk lookup by referral codes; `WHERE referral_code IN (...)`; no array size limit; no auth |
| 23 | `api-parent-student-create-or-update.md` | `850a77b7-fc81-410b-8ea7-b61695aed297` | `POST /v1/student/parents/create-or-update` | API Key | Parent findOrCreate by phone; student creation; Chowkidar + Platform + LanguagePrediction |
| 24 | `api-payment-transactions-get.md` | `6824fd7d-ce7c-4dc7-a4c5-e54b68a781e3` | `GET /v1/payment/transactions` | None | 7 service calls; packages + refunds + credit transfers; timezone-aware; no pagination; no auth |
| 25 | `api-recommended-package-get.md` | `41c3e825-9ca4-4f0c-aa15-2103ac95e0de` | `GET /v2/recommended-package` | None | Next installment recommendation; NectedService pricing; 6 sequential service calls; no cache |
| 26 | `api-student-all-details-update.md` | `052a9875-c499-44c6-8172-4ebe0caf9251` | `PUT /v1/student/all-details` | None | 4-table update; no transaction; Chowkidar sync; SQS certificate regen on name change |
| 27 | `api-unknown-1deb6d9f.md` | `1deb6d9f-PENDING-FULL-UUID` | UNKNOWN | — | Empty source content — NEEDS_MANUAL_REVIEW |

---

## Notes

- Sources 17 and 18 (`29fb93b5`, `94f3c928`) have partial UUIDs — full UUIDs were not retrievable from the notebook query. Content was extracted from the previous session's context.
- Source 27 (`1deb6d9f`) returned empty content from NotebookLM. Manual review required.
- Sources 4, 7 (`unified-data` endpoints) are high-risk: they expose raw Sequelize query passthrough with no field restrictions.
- Source 17 (`feed/presigned-url`) has auth middleware commented out — immediate security fix required.

## Critical Issues Across All APIs (Summary)

| Priority | Issue | Affected Endpoints |
|----------|-------|-------------------|
| Critical | Auth middleware commented out | `POST /v1/feed/presigned-url` |
| Critical | No database transactions on multi-step writes | Credit transfer, referral claim, student all-details update |
| Critical | Race conditions in duplicate/gem checks | Credit transfer, referral claim |
| Critical | Unrestricted DB access (Sequelize passthrough) | Unified-data students, unified-data sale-payments |
| High | No authentication on sensitive write/read endpoints | 10+ endpoints expose student/payment/parent PII |
| High | N+1 queries | Bulk installments |
| High | No pagination on large result sets | Student course-teacher details, payment transactions, system-spec |
| Medium | Sequential external service calls (should be `Promise.all`) | Get students by parent, payment transactions, recommended package |
