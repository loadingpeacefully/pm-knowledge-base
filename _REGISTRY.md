# PM Knowledge Base — Central Registry

> Auto-generated 2026-04-05. Sources from two NotebookLM notebooks, enriched with AI.
> Legend: ⚠️ = NEEDS_MANUAL_REVIEW

---

## technical-architecture/architecture/ (3 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [architecture-overview.md](technical-architecture/architecture/architecture-overview.md) | f341d399 | Microservices map (Paathshala, Eklavya, Chowkidar, Doordarshan, Prabandhan, Hermes), AWS EKS/Lambda/S3/SQS, React/Next.js/PHP tech stack |
| [database-design-doordarshan-meetings.md](technical-architecture/architecture/database-design-doordarshan-meetings.md) | 916b0952 | Doordarshan DB schema, zoom_tokens, zoom_licences, meetings (ENUM status), meeting_events |
| [auth-flow-revamp-student-dashboard.md](technical-architecture/architecture/auth-flow-revamp-student-dashboard.md) | 3edfa993 | 4 auth flows (Standard/Magic Link/Masquerade/Auto-Login), SecureStorage, TokenManager, CSRF, rate limiting, JWT |

---

## technical-architecture/infrastructure/ (17 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [infra-monitoring.md](technical-architecture/infrastructure/infra-monitoring.md) | 742c2a1d | New Relic, Kibana, Lens, OTEL, Slack alerts, CRM API latency, Redis TTL bug |
| [server-schola-production-new.md](technical-architecture/infrastructure/server-schola-production-new.md) | c958af00 | Legacy PHP cron jobs, schola-etl DOWN since Nov 2023, Payment Instalment FAILING port 7600, certbot SSL |
| [schola-new-scripts-server.md](technical-architecture/infrastructure/schola-new-scripts-server.md) | 4e1f3957 | trial_placement.py (needs migration), Slack delivery, PNG/PDF processing |
| [web-app-optimization-champ.md](technical-architecture/infrastructure/web-app-optimization-champ.md) | c8114e41 | 88MB build, 2.5MB _app chunk, 49 routes same bundle, 27 Redux slices, 4-tier bundle strategy |
| [web-app-optimization-dronacharya.md](technical-architecture/infrastructure/web-app-optimization-dronacharya.md) | ee4fd99a | 16MB build, 2.2MB main bundle, 56 vulnerabilities (axios CSRF/DoS), Module Federation |
| [web-app-optimization-prashashak.md](technical-architecture/infrastructure/web-app-optimization-prashashak.md) | 436e5156 | 17MB build, Health Score 65/100, Security 45/100 (54 vulns), CRA, MUI, hardcoded URLs |
| [website-kt-and-docs.md](technical-architecture/infrastructure/website-kt-and-docs.md) | f96ea849 | Next.js 15.2.4, 4-level caching (Google Sheets→Redis→API→CDN), AWS Lambda sync, 20+ locales |
| [sse-vs-websockets.md](technical-architecture/infrastructure/sse-vs-websockets.md) | ca0536a8 | Bidirectional vs unidirectional, 6-connection HTTP/1.1 limit, use case decision matrix |
| [server-sent-events.md](technical-architecture/infrastructure/server-sent-events.md) | 63d6ac15 | SSE mechanics, EventSource, auto-reconnect, Redis Pub/Sub for scaling |
| [hubs-group-class-architecture.md](technical-architecture/infrastructure/hubs-group-class-architecture.md) | 64cc014d | Group types (Regular/Webinar/Workshop/Cohort), Hub/Group/GroupClassBalance, teacher payout calc |
| [whatsapp-customer-support.md](technical-architecture/infrastructure/whatsapp-customer-support.md) | 092759d0 | Kaleyra integration, 3 APIs (Get Conversations/Get By Number/Send Message), whatsapp_data table |
| [zoom-demo-class-report-1.md](technical-architecture/infrastructure/zoom-demo-class-report-1.md) | d493c8a7 | /class/demo/class-by-time API, demo_class_metrics, joinStatus, N+1 API call issue |
| [zoom-demo-class-report-2.md](technical-architecture/infrastructure/zoom-demo-class-report-2.md) | 36905878 | Demo class ops API, add/remove student/teacher, eligible-bookings, demo_classes mutations |
| [notifications.md](technical-architecture/infrastructure/notifications.md) | 4f213d09 | Long Polling vs SSE vs WebSockets, delivery mechanism selection, scalability tradeoffs |

---

## technical-architecture/etl-and-async-jobs/ (4 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [marketing-etl.md](technical-architecture/etl-and-async-jobs/marketing-etl.md) | e02ff9e3 | SQL-based ETL, Google Ads + Facebook Ads sources, AWS Glue, FINAL_OUTPUT, Metabase alert |
| [etl-pipeline-inventory.md](technical-architecture/etl-and-async-jobs/etl-pipeline-inventory.md) | 991c8087 | 12 pipelines (Demo/Teacher/Marketing/Student/Payment/etc.), AWS Glue, owners, schedules |
| [my-feed-loading-waterfall.md](technical-architecture/etl-and-async-jobs/my-feed-loading-waterfall.md) | a5c8beed | 4-phase load sequence, Module Federation microfrontend, lazy loading, analytics scripts |
| [feed-post-creation-etl.md](technical-architecture/etl-and-async-jobs/feed-post-creation-etl.md) | e2dc7ead | Feed scopes (Global/Student), Post Creation Lambda (SQS), Redis pre-computed views, ranking |

---

## technical-architecture/payments/ (15 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [payment-flow.md](technical-architecture/payments/payment-flow.md) | ae49116a | End-to-end payment flow, aggregator routing, SQS invoice+onboard queues |
| [payment-initiation.md](technical-architecture/payments/payment-initiation.md) | 19f2063b | createV2 function, /v1/payment-initiation/create-payment, payment_initiations table |
| [payment-invoice-generation.md](technical-architecture/payments/payment-invoice-generation.md) | 56cd5977 | Puppeteer PDF, AWS S3, invoice_templates, generateInvoice Lambda |
| [onboard-and-invoice-generation.md](technical-architecture/payments/onboard-and-invoice-generation.md) | 110af03f | First-payment gate, welcome emails, Paathshala curriculum, SQS onboard-flow |
| [package-and-payments.md](technical-architecture/payments/package-and-payments.md) | 714bdd1d | Package types, NectedService pricing, multi-currency, sale_payments table |
| [credit-system-and-class-balance.md](technical-architecture/payments/credit-system-and-class-balance.md) | 8f67bf1c | total_credits vs total_booked_class, credit deduction after class, credit transfer API |
| [revamped-payment-page.md](technical-architecture/payments/revamped-payment-page.md) | 9eae1c63 | Multi-student checkout, Nano Courses cross-sell, upgrade section, amount breakup modal |
| [sell-collection.md](technical-architecture/payments/sell-collection.md) | 434b9e5d | Sales incentive calculation, collection types (fresh/renewal/installment), Nected attribution |
| [payment-gateway-paypal.md](technical-architecture/payments/payment-gateway-paypal.md) | 4a2a8a0f | PayPal invoice-based flow, createDraftInvoice, sendInvoice, USD |
| [payment-gateway-razorpay.md](technical-architecture/payments/payment-gateway-razorpay.md) | 6701bd95 | Razorpay SDK, INR, rzp.io link, webhook dashboard config |
| [payment-gateway-splitit.md](technical-architecture/payments/payment-gateway-splitit.md) | a47cba0d | Installment plans, noOfInstallment, webhook URL in payload, USD |
| [payment-gateway-stripe.md](technical-architecture/payments/payment-gateway-stripe.md) | 81c7be93 | plink_ payment links, pi_ PaymentIntent, USD/AED, buy.stripe.com |
| [payment-gateway-tabby.md](technical-architecture/payments/payment-gateway-tabby.md) | 47bc1149 | BNPL, AED/SAR, api.tabby.ai/v2/checkout, installments |
| [payment-gateway-tazapay.md](technical-architecture/payments/payment-gateway-tazapay.md) | 8e880a9d | GBP/OMR, api.tazapay.com, cross-border payments |
| [payment-gateway-xendit.md](technical-architecture/payments/payment-gateway-xendit.md) | 015cc91c | IDR, payment_intent.succeeded, nested webhook, aggregatorId=6 |

---

## technical-architecture/crm-and-sales/ (17 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [curl-api-pancake-sync.md](technical-architecture/crm-and-sales/curl-api-pancake-sync.md) | a9d1c2bf | Pancake CRM webhook, Schola Server, BookingObjectId two-way sync |
| [renewal-crm.md](technical-architecture/crm-and-sales/renewal-crm.md) | fc197de7 | Renewal triggers (low credits/subscription end), FIFO SQS, Zoho Renewals layout |
| [sales-flow.md](technical-architecture/crm-and-sales/sales-flow.md) | b7002f2d | End-to-end sales: booking → demo → payment → Closed Won, all microservices |
| [sales-tasks.md](technical-architecture/crm-and-sales/sales-tasks.md) | 3bdd664f | Automated CRM tasks: First Connect, PQS Review, Join Trial Class |
| [deal-add-notes-flow.md](technical-architecture/crm-and-sales/deal-add-notes-flow.md) | a1cc86cc | /deal/add-notes-in-crm-deal, OAuth token cache 1hr TTL, auto-notes |
| [deal-creation-flow.md](technical-architecture/crm-and-sales/deal-creation-flow.md) | 7c69a66a | createDBCRMDeal, SNS→SQS trigger, lead-to-deal conversion, Zoho upsert |
| [get-deal-owner.md](technical-architecture/crm-and-sales/get-deal-owner.md) | ef79f78b | POST /deals/owner bulk API, master_group_filters weighted routing |
| [hot-lead-channel-assigned-algorithm.md](technical-architecture/crm-and-sales/hot-lead-channel-assigned-algorithm.md) | 47fbdd66 | Vector distance minimization, channel weightages, 2-day rolling count |
| [hot-lead-flow.md](technical-architecture/crm-and-sales/hot-lead-flow.md) | 534cbc50 | POST /hotlead, Slack claim mechanism, JUMP fallback (3x) |
| [lead-creation-flow.md](technical-architecture/crm-and-sales/lead-creation-flow.md) | bc8aa2be | /lead/create-db-crm-lead, booking_uuid duplicate check, Zoho lead upsert |
| [lead-generation-from-ai-calling.md](technical-architecture/crm-and-sales/lead-generation-from-ai-calling.md) | e0a99a9a | Retell AI, Senpai LLM, booking_requests, LQS |
| [partial-lead-ai-calling.md](technical-architecture/crm-and-sales/partial-lead-ai-calling.md) | 914e7a0d | Partial lead (12min dropout), 5 call attempts, DND compliance |
| [retell-integration-lapsed-lead-calling.md](technical-architecture/crm-and-sales/retell-integration-lapsed-lead-calling.md) | c8136452 | Lapsed leads (>25 days), GPT-4.1 mini + ElevenLabs TTS + Twilio |
| [student-class-information-to-zoho.md](technical-architecture/crm-and-sales/student-class-information-to-zoho.md) | 0a5562cd | Daily cron, /student-balance, Zoho Deals upsert |
| [zoho-crm.md](technical-architecture/crm-and-sales/zoho-crm.md) | 1132d811 | Prabandhan CRM gateway, OAuth token management, Leads/Deals/Notes/Tasks |
| [update-deal-to-closed-won.md](technical-architecture/crm-and-sales/update-deal-to-closed-won.md) | 492b64b4 | /deal/update-crm-deal-to-closed-won, first-payment gate, Zoho Stage=Closed Won |
| [user-creation-flow.md](technical-architecture/crm-and-sales/user-creation-flow.md) | 1d0e2298 | /v1/student/parents/create-or-update, findOrCreate by phone, atomic transaction |

---

## technical-architecture/teacher-management/ (5 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [teacher-change.md](technical-architecture/teacher-management/teacher-change.md) | ffda40cf | Teacher reassignment lifecycle, REQUESTED/ACTIVE/EXPIRED statuses, teacher_change_requests |
| [teacher-demo-availability-confirmations.md](technical-architecture/teacher-management/teacher-demo-availability-confirmations.md) | c634566d | Auxo availability engine, color-coded slots, confirmation cron (9AM/6PM IST) |
| [teacher-lms.md](technical-architecture/teacher-management/teacher-lms.md) | 069b15bc | Leave management, SNS/SQS for class cancellation on leave, teacher_applied_leave |
| [teacher-onboarding.md](technical-architecture/teacher-management/teacher-onboarding.md) | 0aa7b462 | Teacher application schema, financial details (bank/PAN/KTP), 15+ sub-tables |
| [teacher-payout.md](technical-architecture/teacher-management/teacher-payout.md) | ec36908c | Payout policies, business regions, currency conversion, teacher_earnings/penalties |

---

## technical-architecture/student-lifecycle/ (33 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [demo-communications.md](technical-architecture/student-lifecycle/demo-communications.md) | aad8bfe5 | SNS/SQS booking reminders, A/B weighted templates, Hermes dispatch |
| [demo-availability.md](technical-architecture/student-lifecycle/demo-availability.md) | 9438d2db | /demo-availability API, IP/timezone resolution, per-slot/per-day capping, 5-minute cache |
| [demo-curriculum.md](technical-architecture/student-lifecycle/demo-curriculum.md) | c7e7022f | getDemoCurriculumWithFallBack, combinatorial fallback logic, demo_curriculum table |
| [demo-slot-capping.md](technical-architecture/student-lifecycle/demo-slot-capping.md) | e8bf67aa | Slot type enum (1–5), day/slot limit checks, UTC-to-local conversion |
| [booking-flow.md](technical-architecture/student-lifecycle/booking-flow.md) | af660f56 | Demo booking creation, MongoDB tracker, BOOKING_SQS, mapStudenWithBooking Lambda |
| [post-class-completion-flow.md](technical-architecture/student-lifecycle/post-class-completion-flow.md) | 4c649e6f | prabandhan-class-completion-flow Lambda, SNS→SQS on class success, Zoho CRM |
| [summer-camp.md](technical-architecture/student-lifecycle/summer-camp.md) | 0d841d4e | /enroll-student-summer-camp, addon materials, DIY/teacher-led flow, Google Sheet sync |
| [student-trial-join-task.md](technical-architecture/student-lifecycle/student-trial-join-task.md) | 95b31b58 | Zoom join event → SQS → Zoho task, 5-attempt reassignment algorithm |
| [first-connect-pqs-review.md](technical-architecture/student-lifecycle/first-connect-pqs-review.md) | 2237955b | First Connect + PQS Review task automation, shift window scheduling |
| [trial-buddy.md](technical-architecture/student-lifecycle/trial-buddy.md) | 9f0b701d | /demo-stream AI chatbot (Niki), AWS Bedrock/Claude, Redis message batching |
| [auxo-mapping.md](technical-architecture/student-lifecycle/auxo-mapping.md) | f2ec7acd | Real-time teacher-student mapping, Redis sorted sets by conversion rate, FIFO queue |
| [auxo-prediction.md](technical-architecture/student-lifecycle/auxo-prediction.md) | 4ee039ff | Joining rate prediction, 4-week weighted average, demo_booking_predictions, 30-min cron |
| [meeting-generation.md](technical-architecture/student-lifecycle/meeting-generation.md) | f40149a1 | GenerateMeetings Lambda, Zoom license pool, pre-generated link dequeue, vendor fallback |
| [brightbuddy-additional-flows-login-class-joining-issues.md](technical-architecture/student-lifecycle/brightbuddy-additional-flows-login-class-joining-issues.md) | cf58233e | P1 chatbot flows, login failures, class-join errors, escalation to support |
| [brightchamps-imessage-customer-flow.md](technical-architecture/student-lifecycle/brightchamps-imessage-customer-flow.md) | 0efe6d73 | Apple Business Chat, demo booking via iMessage, reminders, US English market |
| [dashboard-multi-language-support.md](technical-architecture/student-lifecycle/dashboard-multi-language-support.md) | 9527ddd9 | i18n, locale detection, Vietnamese, string bundles, course locale filtering |
| [demo-certificate-sharing.md](technical-architecture/student-lifecycle/demo-certificate-sharing.md) | 990f4a66 | Demo certificate generation, PDF, WhatsApp/email share, S3 storage |
| [group-360.md](technical-architecture/student-lifecycle/group-360.md) | 0c81dde1 | Group dashboard, teacher view, attendance aggregation, at-risk alerts |
| [hubs-student-dashboard.md](technical-architecture/student-lifecycle/hubs-student-dashboard.md) | 17df3841 | Hub class dashboard, upcoming classes, class summaries, Nano Skills tray |
| [login-flow-revamp.md](technical-architecture/student-lifecycle/login-flow-revamp.md) | e5f5ce8c | Multi-profile login, OTP, profile selection, session management |
| [prd-ip-based-checkout-logic-summer-camp.md](product-prd/prd-ip-based-checkout-logic-summer-camp.md) | 5e651e7f | IP geolocation, currency detection, Razorpay/Stripe routing, Summer Camp 2025 |
| [paid-joining-flow.md](technical-architecture/student-lifecycle/paid-joining-flow.md) | 64476378 | Post-demo offer, checkout, enrollment creation, teacher assignment, onboarding |
| [ratings-flow.md](technical-architecture/student-lifecycle/ratings-flow.md) | 27bdaf64 | Class ratings, teacher ratings, aggregate scoring, low-rating alerts |
| [student-feed.md](technical-architecture/student-lifecycle/student-feed.md) | 8d664dc5 | Personalized feed, milestone cards, Nano Skills nudges, event-driven feed posts |
| [student-onboarding-dashboard-training.md](technical-architecture/student-lifecycle/student-onboarding-dashboard-training.md) | da8a3238 | Multi-step onboarding, personal info, address, class scheduling, guided tooltips |
| [student-showcase-generating-project-videos-for-feed.md](technical-architecture/student-lifecycle/student-showcase-generating-project-videos-for-feed.md) | 81e2e49a | Project video generation, Puppeteer, CDN, feed card publishing |
| [teacher-prioritizing-logic-v0.md](technical-architecture/student-lifecycle/teacher-prioritizing-logic-v0.md) | 4aa898ed | Rule-based teacher scoring, availability filter, composite ranking |
| [teacher-profile-and-reviews.md](technical-architecture/student-lifecycle/teacher-profile-and-reviews.md) | 784cea51 | Teacher bio, rolling rating aggregate, review storage, quality alerts |
| [trialbuddy-ai-powered-chatbot.md](technical-architecture/student-lifecycle/trialbuddy-ai-powered-chatbot.md) | 7f7e965f | LLM chatbot, intent classification, demo booking, lead capture, fallback to human |
| [unified-demo-paid-experience-student.md](technical-architecture/student-lifecycle/unified-demo-paid-experience-student.md) | bf077f6b | Unified dashboard, demo vs paid mode flag, feature gates, seamless upgrade |
| [welcome-call-through-ai-calling.md](technical-architecture/student-lifecycle/welcome-call-through-ai-calling.md) | ca2a2043 | AI voice call, Twilio, Synthflow, post-enrollment welcome, retry logic |
| [whatsapp-trialbuddy-partial-lead.md](technical-architecture/student-lifecycle/whatsapp-trialbuddy-partial-lead.md) | 92af2043 | WhatsApp chatbot, partial lead re-engagement, demo booking |
| [pqs-architecture-project-document.md](technical-architecture/student-lifecycle/pqs-architecture-project-document.md) | d9b85014 | Post-class quiz lifecycle, quiz bank, activation, scoring, parent report |

---

## technical-architecture/api-specifications/ (41 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [api-specification.md](technical-architecture/api-specifications/api-specification.md) | 9c6ea921 | Full microservices catalog, JWT/API key auth, standard response wrapper |
| [apis-country-business-region.md](technical-architecture/api-specifications/apis-country-business-region.md) | 6c0b6ba7 | PATCH /platform/v1/mappings/country/:id, POST /business-region |
| [paathshala-api-specification.md](technical-architecture/api-specifications/paathshala-api-specification.md) | b38cbb41 | POST /demo/feedback, GET /demo/feedback, class status and issue detail options |
| [class-details-for-teacher.md](technical-architecture/api-specifications/class-details-for-teacher.md) | 9ec46799 | Teacher class card API, paid_class_metric, upcomingClassDetails Lambda |
| [booking-classes-api-post.md](technical-architecture/api-specifications/booking-classes-api-post.md) | 9cfbd23e | POST /classes v3, validator chain, pagination, country group merging |
| [curriculum-apis.md](technical-architecture/api-specifications/curriculum-apis.md) | 9b6f85ee | GET/POST/PATCH curriculum modules and topics, CurriculumProjects, API key auth |
| [list-bookings.md](technical-architecture/api-specifications/list-bookings.md) | 6c3446f4 | /tryouts/v1/booking/classes, cancel/reschedule/unqualify flow |
| [create-user-api.md](technical-architecture/api-specifications/create-user-api.md) | 1f7bf74c | User identity with roles, user_identifiers table, atomic transaction |
| [upcoming-class-details-lambda.md](technical-architecture/api-specifications/upcoming-class-details-lambda.md) | 69b26230 | 24-hour class scan cron, paid_class_metric population, 6 class context pointers |
| [update-paid-class-status.md](technical-architecture/api-specifications/update-paid-class-status.md) | eddd4b55 | EventBridge cron + feedback API dual trigger, class-completion-reason metric |
| [manual-payment.md](technical-architecture/api-specifications/manual-payment.md) | a924ec92 | aggregatorId: 8 / "manual", direct receivePayment call, Manual_success capture |
| [student-report-v1.md](technical-architecture/api-specifications/student-report-v1.md) | 37388efc | Unified Refund System v1.0, Prashashak→Eklavya→Prabandhan→Zoho CRM flow |
| [rm-effectiveness-student-performance.md](technical-architecture/api-specifications/rm-effectiveness-student-performance.md) | 1b80c207 | collectStudentForStudentClassPerformance Lambda, Redis cursor pagination, 24-field performance matrix |
| [add-or-update-demo-availability-script.md](technical-architecture/api-specifications/add-or-update-demo-availability-script.md) | 74435045 | Demo availability upsert script, IST slot alignment, 8AM–10PM window, ~3360 queries/run |
| [api-student-bulk-details-get.md](technical-architecture/api-specifications/api-student-bulk-details-get.md) | 846d377a | Bulk student details retrieval |
| [api-student-details-get.md](technical-architecture/api-specifications/api-student-details-get.md) | 4012dffc | Student details by ID |
| [api-student-filter-get.md](technical-architecture/api-specifications/api-student-filter-get.md) | b890d6a5 | Student filter/search API |
| [api-unified-data-students-query.md](technical-architecture/api-specifications/api-unified-data-students-query.md) | 33da7b0c | Unified data — students query |
| [api-student-get.md](technical-architecture/api-specifications/api-student-get.md) | b76ea6cf | Single student retrieval |
| [api-student-class-balance-get.md](technical-architecture/api-specifications/api-student-class-balance-get.md) | f9c7f5a2 | Student class balance endpoint |
| [api-unified-data-sale-payments-query.md](technical-architecture/api-specifications/api-unified-data-sale-payments-query.md) | e9b4f90c | Unified data — sale payments query |
| [api-badge-banner-notification-get.md](technical-architecture/api-specifications/api-badge-banner-notification-get.md) | 985eafbd | Badge/banner notification state |
| [api-student-details-by-balance-ids-get.md](technical-architecture/api-specifications/api-student-details-by-balance-ids-get.md) | a260a6b0 | Student details by balance IDs |
| [api-student-bulk-installments-get.md](technical-architecture/api-specifications/api-student-bulk-installments-get.md) | 120028ae | Bulk installments lookup |
| [api-badge-progress-summary-get.md](technical-architecture/api-specifications/api-badge-progress-summary-get.md) | 7f7e27d9 | Student badge and progress summary |
| [api-student-course-teacher-details-get.md](technical-architecture/api-specifications/api-student-course-teacher-details-get.md) | 2ad05a2c | Course + teacher details for student |
| [api-student-get-students-by-parent.md](technical-architecture/api-specifications/api-student-get-students-by-parent.md) | 3443f51d | Get all students under a parent |
| [api-system-spec-get.md](technical-architecture/api-specifications/api-system-spec-get.md) | 8b5495cd | System spec / dynamic field validation |
| [api-user-get.md](technical-architecture/api-specifications/api-user-get.md) | 4dfd6346 | User profile retrieval |
| [api-student-credit-transfer-request-create.md](technical-architecture/api-specifications/api-student-credit-transfer-request-create.md) | 40621b34 | Credit transfer request creation |
| [api-feed-presigned-url-create.md](technical-architecture/api-specifications/api-feed-presigned-url-create.md) | 29fb93b5 | ⚠️ S3 presigned URL — auth middleware DISABLED (critical security finding) |
| [api-referral-claim-create.md](technical-architecture/api-specifications/api-referral-claim-create.md) | 94f3c928 | Gem award with race condition + missing transaction |
| [api-package-cancel-sold.md](technical-architecture/api-specifications/api-package-cancel-sold.md) | 8f06f04b | Package cancellation with DB transaction |
| [api-package-payment-details-get.md](technical-architecture/api-specifications/api-package-payment-details-get.md) | d9737249 | Base64-encoded payment lookup, no auth, PII exposure |
| [api-feed-showcase-ai-content-generate.md](technical-architecture/api-specifications/api-feed-showcase-ai-content-generate.md) | eb9821a3 | OpenAI Whisper + LLM caption generation, no rate limiting |
| [api-student-bulk-get-by-referral.md](technical-architecture/api-specifications/api-student-bulk-get-by-referral.md) | 3f04ceca | Bulk lookup by referral codes array |
| [api-parent-student-create-or-update.md](technical-architecture/api-specifications/api-parent-student-create-or-update.md) | 850a77b7 | findOrCreate parent + student with 3 external services |
| [api-payment-transactions-get.md](technical-architecture/api-specifications/api-payment-transactions-get.md) | 6824fd7d | 7-service aggregation for full transaction history |
| [api-recommended-package-get.md](technical-architecture/api-specifications/api-recommended-package-get.md) | 41c3e825 | Pricing recommendation via NectedService, 6 sequential calls |
| [api-student-all-details-update.md](technical-architecture/api-specifications/api-student-all-details-update.md) | 052a9875 | 4-table update, no transaction (high priority issue), SQS cert regen |
| [api-student-course-teacher-details-v1.md](technical-architecture/api-specifications/api-student-course-teacher-details-v1.md) | 1deb6d9f | V1 spec — GET students by teacherId/studentId, ACTIVE/PAST filter; see also 2ad05a2c for enriched V2 |

---

## product-prd/ (55+ files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [final-prd-brightchamps-learner-app.md](product-prd/final-prd-brightchamps-learner-app.md) | 929cd1cc | Learner app overview, unified dashboard, NPS, churn reduction |
| [flexible-learning-path.md](product-prd/flexible-learning-path.md) | fd410cb1 | Student-paced learning, lesson unlock, non-linear progress |
| [gamification-badges.md](product-prd/gamification-badges.md) | 29f5812e | Badge system, attendance streaks, Nano Skills badges, feed cards, DAU |
| [harvard-courses-in-nano-skills.md](product-prd/harvard-courses-in-nano-skills.md) | cc2d52aa | Premium Nano Skills tier, Harvard branding, diamond pricing |
| [multilingual-support-vietnamese-phase-1.md](product-prd/multilingual-support-vietnamese-phase-1.md) | bb498177 | Vietnamese localization, locale detection, course surfacing |
| [nano-skills-unlocking-conversions-engagement.md](product-prd/nano-skills-unlocking-conversions-engagement.md) | 8a894ff0 | Diamond top-up, language-sensitive tray, post-enrollment activation |
| [prd-all-in-one-summer-camp-2025-course-detail-scheduling.md](product-prd/prd-all-in-one-summer-camp-2025-course-detail-scheduling.md) | 5988a16a | Summer Camp course detail page, slot selection, IP checkout |
| [prd-brightchamps-global-summer-camp-2025.md](product-prd/prd-brightchamps-global-summer-camp-2025.md) | adc84d64 | Global summer camp, international checkout, 40% enrollment growth |
| [pre-demo-engagement-game-v01.md](product-prd/pre-demo-engagement-game-v01.md) | 87f14ecf | Pre-demo mini-game, attendance uplift, no-login token access |
| [productized-add-credits-flow-v0.md](product-prd/productized-add-credits-flow-v0.md) | 1a7fd72d | Self-serve credit top-up, low-credit alert, bundle selection |
| [nano-skills-s2-unlocking-conversions-engagement-v2.md](product-prd/nano-skills-s2-unlocking-conversions-engagement-v2.md) | 5db3460b | Sprint 2: banners, trays, category tabs, discount offer, dynamic ordering |
| [student-progress-report.md](product-prd/student-progress-report.md) | dcacfc9d | 10-lesson trigger, PDF report, knowledge curve, URI renewal |
| [ai-worksheet-generator.md](product-prd/ai-worksheet-generator.md) | cf808d7c | geeta-AI, LLM question generation, Google Sheets integration |
| [introducing-post-class-quiz-galaxy.md](product-prd/introducing-post-class-quiz-galaxy.md) | a592a4d1 | Quiz Galaxy, orb states, Commander Nova, flashcard review |
| [mvp-post-class-experience.md](product-prd/mvp-post-class-experience.md) | 14477142 | XP system, invite-a-friend challenge, progress dashboard, FinLit |
| [post-class-experience-prd.md](product-prd/post-class-experience-prd.md) | 85fe3e8a | Post-class quiz + home activity, Phase 1 and Phase 2 feature scope |
| [prd-ai-powered-modular-math-lesson-generator.md](product-prd/prd-ai-powered-modular-math-lesson-generator.md) | e8c7ec29 | K-10 lesson generator, modular bots, Common Core alignment |
| [phase-2-quiz-experience.md](product-prd/phase-2-quiz-experience.md) | b955cec3 | Phase 2 quiz animations, orb icon design, SVG state transitions |
| [paid-student-dashboard-v1.md](product-prd/paid-student-dashboard-v1.md) | dacd6f61 | Unified paid dashboard, multi-profile login, reschedule, cancel |
| [personalized-virtual-tutor-chatbot.md](product-prd/personalized-virtual-tutor-chatbot.md) | 63075efa | AI tutor, long-term memory, RAG pipeline, adaptive learning |
| [post-class-activity.md](product-prd/post-class-activity.md) | f7201c5c | Dynamic class cards, lesson status, quiz/assignment activation |
| [wheelseye-price-visibility-experiment.md](product-prd/wheelseye-price-visibility-experiment.md) | a708d204 | Wheelseye, live quote stream, dual 30-min timers, trust experiment |
| [user-onboarding.md](product-prd/user-onboarding.md) | 17dcf65b | First-login onboarding, personal info, address, class scheduling |
| [v1-generation-prompt-math-worksheet.md](product-prd/v1-generation-prompt-math-worksheet.md) | 4afd2754 | LLM prompt templates, difficulty distribution, context distribution |
| [worksheet-question-validation-flow.md](product-prd/worksheet-question-validation-flow.md) | 9fa493f7 | Tag validation, blank-key correspondence, answer type checking |
| [math-worksheet-flow.md](product-prd/math-worksheet-flow.md) | d9a2ddce | End-to-end worksheet pipeline, intake → generation → review → production |
| [current-prompts-2025.md](product-prd/current-prompts-2025.md) | ca6f2149 | AI prompts inventory July 2025 |
| [calendar-as-platform.md](product-prd/calendar-as-platform.md) | 95947549 | Calendar as a Platform concept |
| [curriculum-design-process.md](product-prd/curriculum-design-process.md) | 1fdab4a9 | Curriculum design process |
| [dqs-framework-training.md](product-prd/dqs-framework-training.md) | 7931e129 | DQS framework training |
| [demo-joining-page.md](product-prd/demo-joining-page.md) | c5354271 | Demo joining page spec |
| [lesson-structure-guidelines.md](product-prd/lesson-structure-guidelines.md) | 4480f90d | Lesson structure with guidelines |
| [maths-overview.md](product-prd/maths-overview.md) | d14cf137 | Maths curriculum overview |
| [money-lessons.md](product-prd/money-lessons.md) | 6e967217 | Money/FinLit lesson content |
| [nano-skills.md](product-prd/nano-skills.md) | 53e1d399 | Nano Skills product spec PDF |
| [product-training-deck.md](product-prd/product-training-deck.md) | 24b95bff | Product training deck |
| [adhyayan-cms-templates-spec.md](product-prd/adhyayan-cms-templates-spec.md) | 59cb8139 | Adhyayan CMS templates spec |
| [teacher-hiring-training-platform-prd.md](product-prd/teacher-hiring-training-platform-prd.md) | d2ce96c0 | Hiring/training system (untitled doc) |
| [teacher-availability-prd.md](product-prd/teacher-availability-prd.md) | 4942fe93 | Teacher availability PRD |
| [gamified-platform-01.md](product-prd/gamified-platform-01.md) | cfabaff6 | Gamified Platform Part 1 |
| [gamified-platform-02.md](product-prd/gamified-platform-02.md) | f621f36a | Gamified Platform Part 2 |
| [gamified-platform-03.md](product-prd/gamified-platform-03.md) | eeee6cc8 | Gamified Platform Part 3 |
| [architectural-innovation-to-pm.md](product-prd/architectural-innovation-to-pm.md) | 32069997 | Architectural Innovation to PM Excellence |
| [building-scalable-ecosystems-deck.md](product-prd/building-scalable-ecosystems-deck.md) | 7b8e09bb | Building Scalable Ecosystems — Suneet Jagdev product journey |
| [brightchamps-complete-portfolio.md](product-prd/brightchamps-complete-portfolio.md) | 38ab7e8c | Complete BrightCHAMPS product portfolio |
| [content-factory-01-stage-viewer.md](product-prd/content-factory-01-stage-viewer.md) | bf74b82e | Content Factory stage viewer |
| [content-factory-02-bug-resolution.md](product-prd/content-factory-02-bug-resolution.md) | 81d54c1f | Content Factory bug resolution |
| [content-factory-03-technical.md](product-prd/content-factory-03-technical.md) | 26b47625 | Content Factory technical ETL |
| [content-factory-summary.md](product-prd/content-factory-summary.md) | f891ed02 | Content Factory summary |
| [geeta-ai-content-factory.md](product-prd/geeta-ai-content-factory.md) | 6685498d | Geeta-AI Content Factory |
| [json-template-tech-questions.md](product-prd/json-template-tech-questions.md) | 4253649a | JSON Template Tech Questions |
| [master-projects.md](product-prd/master-projects.md) | c94dfe06 | Master Projects list |
| [gamified-learning-remaining-context.md](product-prd/gamified-learning-remaining-context.md) | 8f647ade | Remaining context — gamified learning |
| [suneet-full-portfolio-overview.md](product-prd/suneet-full-portfolio-overview.md) | 75e6e9d2 | Suneet Jagdev full portfolio overview |
| [json-gamified-template-engine.md](product-prd/json-gamified-template-engine.md) | f4ff9895 | JSON-driven gamified template engine architecture |
| [unified-migration-prd.md](product-prd/unified-migration-prd.md) | e61fae52 | Unified migration PRD |
| [wheelseye-arth-master-projects.md](product-prd/wheelseye-arth-master-projects.md) | 5017acd2 | Wheelseye and Arth Design master project records |
| [work-done-q1-q4-2024.md](product-prd/work-done-q1-q4-2024.md) | f0127992 | Work done Q1-Q4 2024 |
| [work-done-2-kra-kpi-scores.md](product-prd/work-done-2-kra-kpi-scores.md) | 8d8e47d8 | Work done 2 — KRA/KPI scores |
| [work-done-3-updated-master.md](product-prd/work-done-3-updated-master.md) | 82f7b065 | Work done 3 — updated master |
| [geeta-ai-hybrid-content-ops.md](product-prd/geeta-ai-hybrid-content-ops.md) | 25ce869f | Geeta-AI Hybrid Content Operations Platform |
| [language-of-intelligent-machines.md](product-prd/language-of-intelligent-machines.md) | 52ed7ed4 | The Language of Intelligent Machines |

---

## performance-reviews/ (2 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [apr24-mar25-performance-review.md](performance-reviews/apr24-mar25-performance-review.md) | 603cde13 | KRA/KPI review Apr 2024 – Mar 2025, self-assessment |
| [mar23-apr24-performance-review.md](performance-reviews/mar23-apr24-performance-review.md) | 7c86b73f | KRA/KPI review Mar 2023 – Apr 2024 |

---

## research-competitive/ (17 files)

| File | Source ID | Key Topics |
|------|-----------|------------|
| [lingoace-avoid-reddit.md](research-competitive/lingoace-avoid-reddit.md) | 500214fd | User complaints: Singapore Math curriculum issues |
| [lingoace-very-unimpressed-reddit.md](research-competitive/lingoace-very-unimpressed-reddit.md) | 1dcaa2a3 | Teacher quality, scheduling frustrations |
| [55min-math-block-reddit.md](research-competitive/55min-math-block-reddit.md) | a9eb11ba | Math block structure pedagogy |
| [adaptive-learning-google-blog.md](research-competitive/adaptive-learning-google-blog.md) | 60fdd871 | Google's adaptive learning tech perspective |
| [lingoace-1v4-classroom-handbook.md](research-competitive/lingoace-1v4-classroom-handbook.md) | 81b541ec | LingoAce 1v4 class format, teacher guidelines |
| [lingoace-company-overview-leadiq.md](research-competitive/lingoace-company-overview-leadiq.md) | 990a15b9 | Company overview, contacts, competitors |
| [lingoace-connect-app-store.md](research-competitive/lingoace-connect-app-store.md) | bff72d3d | App Store listing, ratings, features |
| [lingoace-expands-math-music-pr.md](research-competitive/lingoace-expands-math-music-pr.md) | adc2dcd6 | Math and music expansion announcement |
| [lingoace-full-upgrade-chinese-pr.md](research-competitive/lingoace-full-upgrade-chinese-pr.md) | f51f2dec | Chinese program precision learning upgrade |
| [lingoace-acemath-upgrade-pr.md](research-competitive/lingoace-acemath-upgrade-pr.md) | 830b5829 | AceMath major upgrade for global students |
| [lingoace-peak-xv-podcast.md](research-competitive/lingoace-peak-xv-podcast.md) | 8a49c6e7 | Peak XV growth strategy, investor perspective |
| [lingoace-trustpilot-page1.md](research-competitive/lingoace-trustpilot-page1.md) | 527605f0 | Trustpilot user reviews — page 1 |
| [lingoace-trustpilot-page5.md](research-competitive/lingoace-trustpilot-page5.md) | 65af9bc9 | Trustpilot user reviews — page 5 |
| [esl-teacher-365-lingoace.md](research-competitive/esl-teacher-365-lingoace.md) | 66a84952 | ESL teacher perspective on LingoAce |
| [ui-ux-children-gaming-platforms.md](research-competitive/ui-ux-children-gaming-platforms.md) | 67e231d2 | Academic paper: UI/UX for children's educational gaming |
| [lingoace-study-generated.md](research-competitive/lingoace-study-generated.md) | 93a0d501 | AI-generated LingoAce study |
| [lingoace-tech-pedagogical-architecture.md](research-competitive/lingoace-tech-pedagogical-architecture.md) | 17d63b8c | LingoAce tech and pedagogical architecture analysis |

---

## assets/ (images — logged only, not converted)

| Source ID | Original Title | Context |
|-----------|---------------|---------|
| 168067b6, 2ac3c2f5, 3aa248ed, 70306360, 22dd7644, 22db8934, 73a09c19 | CMS1–CMS7.png | CMS interface screenshots |
| caba6ab8, 8b799c04, 4eb9019d, 263a16c6, 9fdf8734, 8255aa4c, 64409ee8 | NS01–NS07.png | Nano Skills UI screenshots |
| 24388b48, ad09fdda, 039deb74, 1fa05e1c | Screenshot 2025-06-02 | UI screenshots June 2025 |
| bea444c6, d0da0b3b, 4ff3c87d | Screenshot 2025-07-02 | UI screenshots July 2025 |
| a35d7a3a, bd76ec13 | Screenshot 2025-10-12 | UI screenshots Oct 2025 |
| 66d38091, 1c9b9d2f, 38ab97d7, 14646c02 | Screenshot 2026-01-30 | UI screenshots Jan 2026 |
| 4a56ac6b, a978b699, 285192be, c5385f6a, 134254f1, 331ce01c | image (2–4).png | Miscellaneous images |
| f056e3d8 | Whiteboard.chat for Teachers (YouTube) | Teaching tools reference video |

---

## Skipped Sources
| Source ID | Title | Reason |
|-----------|-------|--------|
| ecd70aa6, 229ab86c, b67d7bca, afa11a4a, 78873331, b664db76 | Suneet Jagdev resume PDFs (NB1) | Excluded per plan |
| 2d860f47, ab436972 | Harness resume generated texts (NB1) | Excluded per plan |
| 491f3dee, bda4051b | Create User API (duplicate) | Deduplicated |
| a645ed11 | Credit System (duplicate) | Deduplicated |
| e6188b7e | Onboard and Invoice (duplicate) | Deduplicated |
| 7ba28431 | Package and Payments (duplicate) | Deduplicated |
| e80d952a | Payment Invoice Generation (duplicate) | Deduplicated |
| 4e41f78d | RM Effectiveness (duplicate) | Deduplicated |
| 506ab5cd | SR V1.0 (duplicate) | Deduplicated |
| 75360aa1 | Sell Collection (duplicate) | Deduplicated |
| cbc8911d | _studentId (duplicate) | Deduplicated |
| 27a29c55 | Hubs Student Dashboard (duplicate) | Deduplicated |
| 9dd0bc87 | PRD Post Class Experience (duplicate) | Deduplicated |
| b678351a, f777cecd | Suneet Jagdev resumes (NB5) | Excluded per plan |
