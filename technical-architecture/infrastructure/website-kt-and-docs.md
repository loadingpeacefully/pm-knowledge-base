---
title: Website KT and Docs — brightchamps.com
category: technical-architecture
subcategory: infrastructure
source_id: f96ea849-641d-414e-ac3b-481333e9bc03
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Website KT and Docs — brightchamps.com

## Overview
This document is a knowledge transfer guide for the BrightCHAMPS marketing website (brightchamps.com), covering the Next.js 15 tech stack, 4-level caching architecture (Google Sheets → Redis → API → CDN), folder structure, deployment process, and local onboarding steps for new developers.

## API Contract
- **CDN Cache Purge**: `GET https://staging-next.brightchamps.com/api/cache/clear-cdn-cache`
- **Redis Sync**: AWS Lambda function (triggered manually or on schedule) to sync Google Sheets data into Redis
- Auth: N/A for cache management endpoints (internal use)

## Logic Flow
### Controller Layer
Website requests flow: User → CDN (CloudFront) → Next.js API/SSR → Redis Cache → Google Sheets (base data source)

Cache purge flow:
1. Update data in Google Sheets
2. Trigger AWS Lambda to sync Redis with updated sheet data
3. Run Redis cache purge commands to clear outdated cached rows and query results
4. Call API endpoint to purge CDN cache

### Service/Facade Layer
The website is data-driven from Google Sheets via a multi-layer cache:
- **Google Sheets** — Base data source for content (feedbacks, reviews, team-people, FAQ, jobs, packages, courses, etc.)
- **Redis** — Caches Google Sheet data by row or sheet; auto-updates daily at 5:30 AM IST. Redis query results are also independently cached
- **API layer** — Caches API call responses
- **CDN (CloudFront)** — Caches fully rendered pages

### High-Level Design (HLD)
```
Data Update Flow:
Google Sheets (update content)
        │
        ▼
AWS Lambda (sync Redis)
        │
        ▼
Redis Cache Purge (specific sheet rows + query results)
        │
        ▼
CDN Cache Purge (API call to clear-cdn-cache)
        │
        ▼
Users see updated content
```

**Caching Architecture (4 levels):**
```
User → CDN → API → REDIS QUERY → REDIS → Google Sheets
```

**Redis auto-refresh:** Daily at 5:30 AM IST

## External Integrations
- **Google Sheets** — Primary CMS / data source for website content
- **Google APIs (Sheets + Auth)** — SDK for reading sheet data
- **AWS Lambda** — Redis sync trigger
- **AWS CloudFront** — CDN for page caching
- **AWS Secrets Manager + SSM** — Credentials and parameter storage
- **Redis / ioredis** — Caching layer
- **Segment Analytics** — User analytics tracking
- **React Intl** — Internationalization (20+ locales)
- **React Slick** — Carousel components
- **Axios** — HTTP client for API calls
- **Turbopack** — Development server build tool (Next.js 15)

## Internal Service Dependencies
- Website → AWS Lambda (for Redis sync)
- Website → AWS Secrets Manager (for credentials)
- Website → AWS SSM (for parameter store access)

## Database Operations
### Tables Accessed
Not a traditional database — data stored in Google Sheets, cached in Redis. No SQL tables.

### SQL / ORM Queries
N/A — data access is via Google Sheets API and Redis key lookups.

### Transactions
N/A

## Performance Analysis
### Good Practices
- 4-level caching architecture ensures minimal latency for end users
- Daily Redis auto-refresh at 5:30 AM IST keeps cache warm
- Dynamic sitemaps and meta tags for SEO
- Bundle analysis script (`npm run analyze`) available
- Turbopack for faster development builds
- Multi-language support for 20+ locales handled via React Intl

### Performance Concerns
- Google Sheets as a CMS source introduces a dependency on Google API rate limits
- Manual 4-step cache invalidation process is error-prone — no automated invalidation on sheet update
- AWS credential requirements for local setup create onboarding friction for new developers

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | Manual cache invalidation process (4 steps) — risk of stale content if steps are missed |
| Medium | Google Sheets as production CMS — rate-limited, non-transactional, no versioning |
| Low | Local development requires AWS credentials — increases onboarding complexity |
| Low | `/new-website/` directory inside `src/` suggests a parallel rebuild effort — unclear migration status |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Document and automate the 4-step cache invalidation process into a single script or Lambda trigger
- Add a webhook or Apps Script trigger on Google Sheets update to auto-initiate Redis sync

### Month 1 (Architectural)
- Evaluate replacing Google Sheets CMS with a headless CMS (e.g., Contentful, Sanity) for better versioning and API reliability
- Clarify the status and completion timeline of `/new-website/` migration inside `src/`
- Simplify local dev setup by providing mock credentials or a local Redis instance for development

## Test Scenarios
### Functional Tests
- Content updated in Google Sheets reflects on website after completing all 4 cache invalidation steps
- Redis auto-refresh at 5:30 AM IST updates content without manual intervention
- Multi-language pages render correctly for all 20+ supported locales
- Course pages for Math, Coding, Robotics, AI, and Financial Literacy load correctly

### Performance & Security Tests
- CDN cache hit rate is high (>90%) for static/marketing pages
- AWS credentials are not exposed in frontend bundles or API responses

### Edge Cases
- What happens when Google Sheets API rate limit is exceeded during a Redis sync?
- Behavior when AWS Lambda sync job fails mid-execution — is Redis left in a partially updated state?
- CDN cache not purged after content update — how long before auto-expiry?

## Async Jobs & ETL
- **AWS Lambda** — Redis sync job triggered manually or on schedule
- **Daily Redis refresh** — Runs at 5:30 AM IST automatically
- **CDN cache invalidation** — Triggered via API call as the final step in the content update process

## Developer Onboarding
**Prerequisites:**
- Node.js (check: `node --version`, `npm --version`)
- AWS credentials (for SSM integration and secrets management)

**Setup:**
```bash
npm install
npm run dev       # Development server with Turbopack → http://localhost:3000
npm run build     # Production build
npm run start     # Production server
npm run lint      # Code linting
npm run analyze   # Bundle size analysis
```

**Environment:** Check `.env` file and `/config/` directory for environment-specific configurations (dev/stage/prod).

**Folder Structure:**
- `pages/` — Next.js routing (`_app.js`, `_document.js`, `index.js`, `api/`, `courses/`)
- `src/components/` — Reusable React components
- `src/sections/`, `src/layouts/`, `src/hooks/`, `src/services/`, `src/utils/`, `src/constants/`, `src/styles/`, `src/lib/`, `src/new-website/`
- Root: `/services`, `/config`, `/public`, `/utils`
