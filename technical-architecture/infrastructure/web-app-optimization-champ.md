---
title: Web App Optimization Metrics — champ.brightchamps.com
category: technical-architecture
subcategory: infrastructure
source_id: c8114e41-61ef-46f0-bad0-54e018e9b748
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Web App Optimization Metrics — champ.brightchamps.com

## Overview
This document is a technical audit of the student dashboard at `champ.brightchamps.com`, identifying critical bundle size issues, architectural bottlenecks, and a prioritized optimization roadmap to reduce the initial JavaScript load from 2.5MB to under 1.5MB and total build from 88MB to ~70MB.

## API Contract
N/A — This is a frontend performance audit document.

## Logic Flow
### Controller Layer
N/A — Frontend optimization audit.

### Service/Facade Layer
The student dashboard is a Next.js application with 49 routes, 27 Redux slices, and 7 nested context providers — all currently loaded uniformly regardless of the route being accessed.

### High-Level Design (HLD)
**Current State (Problems):**
- All 49 routes load the exact same 2.5MB bundle (login page = full dashboard bundle)
- 27 Redux slices initialized at app startup for every page
- 7 context providers initialized upfront across all pages
- Lottie animation files totaling ~4MB loaded synchronously
- All 5 language files (524KB total) loaded statically

**Target State:**
- Total build: 88MB → ~70MB
- Initial JS load: 2.5MB → under 1.5MB
- `_app` chunk: 2.5MB → 1.2MB (48% reduction)
- Route-based 4-tier bundle strategy (see Optimization Roadmap)

## External Integrations
- **Google Fonts** — Font delivery
- **Lottie** — Animation library (top files: `confetti_animation` 1.3MB, `lucky_draw_open_animation` 896KB)
- **ReactQuery DevTools** — Currently loading in production builds (should be dev-only)
- **Elastic APM** — Application performance monitoring (flagged for lazy loading)
- **Lighthouse CI** — Recommended for ongoing performance monitoring
- **webpack-bundle-analyzer** — Recommended for bundle visualization

## Internal Service Dependencies
- Next.js student dashboard → Chowkidar (auth), Eklavya (student data), Paathshala (class data)
- All API calls managed through React Query client

## Database Operations
### Tables Accessed
N/A — Frontend audit.

### SQL / ORM Queries
N/A

### Transactions
N/A

## Performance Analysis
### Good Practices
- React Query already in use for API data fetching and caching
- Next.js framework provides built-in SSR/SSG capabilities
- Code splitting infrastructure (chunking) is in place, though not optimally configured

### Performance Concerns
- **All 49 routes load the same 2.5MB bundle** — critical architectural flaw
- `_app` chunk at 2.5MB is the largest chunk in the entire build
- `moment.js` included — should be replaced with `date-fns`
- Duplicate `react-query` dependency present
- ReactQuery DevTools loading in production
- 5 language files (524KB) loaded statically upfront
- Lottie animations totaling ~4MB loaded without compression or lazy loading
- All 27 Redux slices initialized on every page load

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | All 49 routes share same 2.5MB bundle — login page loads full dashboard code |
| Critical | Lottie `confetti_animation` at 1.3MB loaded globally |
| High | `moment.js` present — 200KB savings available by switching to `date-fns` |
| High | Duplicate `react-query` dependency |
| High | ReactQuery DevTools loading in production build |
| High | All 27 Redux slices initialized regardless of page context |
| Medium | 5 language files (524KB) loaded statically — 400KB savings available |
| Medium | 7 context providers initialized on every page |
| Low | Duplicate CSS detected — PurgeCSS not configured |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Compress top 5 Lottie files or replace with CSS animations / WebP / GIFs (saves >2MB)
- Move language files to dynamic conditional loading (saves >400KB)
- Remove duplicate `react-query` dependency and replace `moment.js` with `date-fns` (saves ~200KB)
- Remove ReactQuery DevTools from production build
- Enable `optimizeCss`, `swcMinify` in `next.config.js`
- Add `webpack-bundle-analyzer`

### Month 1 (Architectural)
**Route-Based 4-Tier Bundle Strategy:**
- **Tier 1 — Minimal Bundle (~300KB)**: Auth pages (login, logout, password reset)
- **Tier 2 — Basic Bundle (~800KB)**: Lightweight pages (onboarding, account settings)
- **Tier 3 — Dashboard Bundle (~1.5MB)**: Full dashboard features
- **Tier 4 — Specialized Bundles (~1.2MB)**: Context-specific bundles (Learning, Social, Skills, Demo)

**Redux Store Splitting:**
- Multiple store configurations (minimal store for auth pages, full store for dashboard)
- Or implement lazy slice loading

**Context Optimization:**
- Conditional context loading so lightweight pages skip heavy contexts (Learning, Class contexts)

**Advanced Configurations:**
- `splitChunks` webpack config to separate vendor libraries
- PurgeCSS to remove unused styles
- Lazy loading for Elastic APM
- Virtual scrolling for large lists
- Lighthouse CI integration in CI/CD with strict budget alerts

## Test Scenarios
### Functional Tests
- Login page loads without importing dashboard-specific modules
- Language switching works correctly after dynamic loading migration
- Redux store initializes only the slices needed for the current route

### Performance & Security Tests
- Lighthouse CI checks pass with bundle size budgets enforced
- First Contentful Paint < target threshold after optimization
- Time to Interactive < target threshold after optimization

### Edge Cases
- Route with lazy-loaded context fails to load context — does the page degrade gracefully?
- Language file fails to load dynamically — does the UI fall back to English?

## Async Jobs & ETL
N/A — Frontend performance audit. No async jobs in scope.
