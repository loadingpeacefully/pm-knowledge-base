---
title: My Feed Loading Waterfall
category: technical-architecture
subcategory: etl-and-async-jobs
source_id: a5c8beed-e2f2-42eb-882f-469d8e8945cf
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# My Feed Loading Waterfall

## Overview
This document maps the complete multi-phase loading sequence for the `my-feed` page on the student dashboard (`champ.brightchamps.com`), analyzing each layer from browser-level HTML parsing through Next.js initialization, layout rendering, and microfrontend (Module Federation) loading. It identifies performance optimizations including lazy loading, skeleton states, and async external scripts.

## API Contract
N/A — This is a frontend loading sequence analysis, not a backend API document.

## Logic Flow
### Controller Layer
The loading sequence flows through 4 distinct phases: Browser Level → Next.js App Level → Layout Level → Page/Microfrontend Level.

### Service/Facade Layer
**Phase 1 — Browser Level (HTML Document Fetch & Parse):**
- DNS resolution → HTML document fetch
- `<Head>` elements processed: viewport, description meta tags
- Font preconnections established: Google Fonts + Gstatic (Nunito, Inter, Poppins, Lilita One, Nunito Sans)
- Async/deferred external scripts triggered: Google Tag Manager, MoEngage SDK, Microsoft Clarity, Facebook Pixel, Google Maps API

**Phase 2 — Next.js App Level (Initialization & Providers):**
- `_app.tsx` initializes with error boundaries and global SCSS styles
- **7-level Context Provider chain** initialized:
  1. Redux store (global state)
  2. I18Next (language detection)
  3. `AuthContextProvider` (authentication state)
  4. `StudentListContextProvider` (student list management)
  5. `LearningProgressContextProvider` (learning progress)
  6. Additional nested contexts
  7. React Query client (API data fetching and caching)

**Phase 3 — Layout Level (Dynamic Selection & Rendering):**
- Route `my-feed` detected → `FeedLayout` dynamically selected
- Layout components lazy-loaded → `LayoutSkeleton` displayed during loading
- `NewDashboard` container rendered:
  - `LeftSideBar`
  - Mobile menus
  - Conditionally lazy-loaded: `Chatbot`, `PaymentErrorPopup`
- `FeedLayout` template constructs inner UI:
  - Sticky Header
  - Banner Lists
  - Section Header with "Upcoming Class Cards" (using `CardSkeleton` while loading)

**Phase 4 — Page Level & Microfrontend Loading:**
- `my-feed` page component mounts
- Access validation checks run
- `FeedApplication` component dynamically imported
- Event tracking established
- Module Federation loads external microfrontend via remote entry URL
- Shared dependencies: React, React-Redux
- External Feed Content rendered (posts, activities, interactions)

### High-Level Design (HLD)
```
Browser Request
        │ DNS → HTML Document
        ▼
Font Preconnections + Async Scripts (GTM, MoEngage, Clarity, FB Pixel, Maps)
        │
        ▼
Next.js _app.tsx
        │ 7-level Context Provider chain + React Query
        ▼
Route Detection → FeedLayout Selected
        │ LayoutSkeleton displayed (lazy loading in progress)
        ▼
NewDashboard Container
        │ LeftSideBar + Conditionally lazy: Chatbot, PaymentErrorPopup
        ▼
FeedLayout Inner UI
        │ Sticky Header + Banner Lists + Upcoming Class Cards (CardSkeleton)
        ▼
my-feed Page Component
        │ Access validation
        ▼
Dynamic Import: FeedApplication
        │ Module Federation → Remote Entry URL
        ▼
External Microfrontend Loaded
        │ Shared: React + React-Redux
        ▼
Feed Content Rendered (posts, activities, interactions)
```

## External Integrations
- **Google Tag Manager** — Analytics/tag management (async loaded)
- **MoEngage SDK** — Push notifications and user engagement (async loaded)
- **Microsoft Clarity** — Session recording and heatmaps (async loaded)
- **Facebook Pixel** — Conversion tracking (async loaded)
- **Google Maps API** — Location features (deferred loaded)
- **Google Fonts** — Nunito, Inter, Poppins, Lilita One, Nunito Sans (preconnected)
- **Module Federation** — External Feed microfrontend loaded via remote entry URL

## Internal Service Dependencies
- `FeedApplication` (microfrontend) → Feed service APIs for posts, interactions, comments
- `AuthContextProvider` → Chowkidar (auth service) for session validation
- `StudentListContextProvider` → Eklavya (student service)
- `LearningProgressContextProvider` → Paathshala (class/learning service)
- `CardSkeleton` / Upcoming Class Cards → Paathshala (class schedule data)

## Database Operations
N/A — Frontend loading waterfall analysis. Database queries are abstracted through service APIs.

## Performance Analysis
### Good Practices
- Dynamic imports used extensively for on-demand component loading
- `LayoutSkeleton` and `CardSkeleton` improve perceived performance
- Module Federation decouples the Feed microfrontend — independent deployability
- Shared dependencies (React, React-Redux) in Module Federation save duplicate bundle downloads
- All heavy analytics scripts (GTM, MoEngage, Clarity, FB Pixel) loaded asynchronously — do not block main thread
- Font preconnections with `display=swap` ensure text visible while custom fonts load

### Performance Concerns
- **7-level Context Provider chain** initialized on every page load — even pages that don't need LearningProgress or StudentList contexts
- All 7 contexts initialized at `_app.tsx` level — not deferred by route
- Multiple analytics SDKs loading simultaneously (GTM, MoEngage, Clarity, FB Pixel, Maps) — combined script weight non-trivial
- Module Federation remote entry fetch is a blocking dependency for Feed content — network latency impacts Feed render

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | 7-level Context Provider chain initialized globally — heavy pages load all contexts including unused ones |
| Medium | Module Federation remote entry URL is a single point of failure for Feed rendering |
| Medium | LearningProgressContextProvider and StudentListContextProvider load on every page regardless of need |
| Low | 5 simultaneous analytics scripts — consider tag management to batch/prioritize |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Move `LearningProgressContextProvider` and `StudentListContextProvider` to route-specific providers (only mount on pages that use them)
- Add error boundary around `FeedApplication` module federation import to prevent full page failure if feed fails to load

### Month 1 (Architectural)
- Implement route-aware context loading (as aligned with the champ.brightchamps.com optimization plan — Tier 1–4 bundle strategy)
- Add a CDN cache for the Module Federation remote entry file to reduce cold-start latency for the microfrontend
- Audit and reduce analytics SDK count — consolidate into fewer SDKs where possible

## Test Scenarios
### Functional Tests
- `LayoutSkeleton` visible during layout lazy-load phase
- `CardSkeleton` visible while Upcoming Class Cards data is fetching
- Feed content renders after Module Federation remote entry loads
- All 7 context providers initialize without errors

### Performance & Security Tests
- Measure time-to-first-meaningful-paint for `my-feed` page
- Module Federation remote entry load time under P95 network conditions
- Verify async analytics scripts don't block `DOMContentLoaded`

### Edge Cases
- Module Federation remote entry URL is unavailable — does page render without feed content gracefully?
- `AuthContextProvider` validation fails — does page redirect without rendering partial content?
- Font preconnection fails — does `display=swap` ensure text fallback is shown?

## Async Jobs & ETL
- **Module Federation**: Feed microfrontend loaded asynchronously via remote entry URL
- **Analytics SDKs**: GTM, MoEngage, Clarity, FB Pixel, Google Maps — all loaded asynchronously post-HTML parse
- **React Query**: Client-side async data fetching provider initialized at app level
