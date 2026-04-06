---
title: Web App Optimization Metrics — prashashak.brightchamps.com
category: technical-architecture
subcategory: infrastructure
source_id: 436e5156-6f49-4f3d-92b1-df347c7a2e74
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Web App Optimization Metrics — prashashak.brightchamps.com

## Overview
This document is a technical audit of the BrightCHAMPS Admin Frontend (Prashashak) at `prashashak.brightchamps.com`, built with React 18.2.0 and TypeScript (Create React App). The application has an Overall Health Score of 65/100 with a 17MB build (3x over target), 54 npm vulnerabilities, and significant performance, security, and maintainability debt.

## API Contract
N/A — This is a frontend performance audit document.

## Logic Flow
### Controller Layer
N/A — Frontend optimization audit.

### Service/Facade Layer
The admin frontend is a CRA (Create React App) application with 50+ code-split chunks, a 1.7MB main bundle, 7MB of source maps in production, and 26 service files with duplicate logic.

### High-Level Design (HLD)
**Overall Health Score: 65/100**
- Security: 45/100 (Poor — 54 vulnerabilities)
- Performance: 50/100 (Poor — massive bundles)
- Maintainability: 70/100 (Fair — technical debt)
- Code Quality: 75/100 (Good — 85% TypeScript usage, some `any` types)

**Current Build Metrics:**
- Total build size: **17MB** (target: <5MB)
  - JavaScript: 15MB
  - CSS: 696KB
  - Media: 365KB
- Main bundle: **1.7MB** (target: <500KB)
- Source maps in production: **7MB overhead**
- No gzip compression detected

## External Integrations
- **Material-UI (MUI)** — Heavy component library, not tree-shaken
- **axios 0.27.2** — CSRF, SSRF, DoS vulnerabilities
- **@babel/traverse** — Arbitrary code execution vulnerability
- **form-data** — Arbitrary file write vulnerability
- **html2canvas** — Unused heavy dependency (flagged for removal)
- **jspdf** — Unused heavy dependency (flagged for removal)
- **moment-timezone** — Should be replaced with `date-fns` (92% size decrease available)
- **webpack-bundle-analyzer** — Recommended for bundle tracking

## Internal Service Dependencies
- Prashashak FE → Prashashak BE (admin API layer)
- Prashashak BE → all core microservices (Eklavya, Paathshala, Dronacharya, Prabandhan, Chowkidar, Payments)
- 26 service files with duplicate logic across the admin frontend

## Database Operations
### Tables Accessed
N/A — Frontend audit.

### SQL / ORM Queries
N/A

### Transactions
N/A

## Performance Analysis
### Good Practices
- 85% TypeScript usage rate — strong type coverage
- Code splitting with 50+ chunks (though not optimally configured)
- Feature-based directory organization implied by 26 service files

### Performance Concerns
- 17MB total build — more than 3x the 5MB target
- 1.7MB main bundle — more than 3x the 500KB target
- Source maps in production: 7MB overhead
- No gzip compression
- Synchronous component imports blocking render
- Heavy MUI components not lazy-loaded
- Unoptimized API calls without request caching
- `html2canvas` and `jspdf` present but unused

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | `axios 0.27.2` — CSRF, SSRF, DoS risks |
| Critical | `@babel/traverse` — arbitrary code execution vulnerability |
| Critical | `form-data` — arbitrary file write vulnerability |
| Critical | Source maps enabled in production (7MB overhead) |
| High | No gzip compression |
| High | 54 total vulnerabilities (2 critical, 23 high) |
| High | Main bundle at 1.7MB — 3.4x over target |
| High | Hardcoded URLs in codebase (should use environment variables) |
| High | Typo in base constants: `PRASHSHAK_BE` (not `PRASHASHAK_BE`) |
| Medium | Duplicate logic across 26 service files |
| Medium | Missing API validation across service layer |
| Medium | Large commented-out code blocks |
| Medium | Error handling rated 40% — missing error boundaries, inconsistent try/catch |
| Low | `any` types and missing TypeScript interfaces |
| Low | `html2canvas` and `jspdf` unused but bundled |

## Optimization Roadmap
### Week 1 (Quick Wins)
**Phase 1 (Weeks 1–2) — Target: 40% reduction (-6.8MB):**
- Remove source maps in production (`GENERATE_SOURCEMAP=false`)
- Enable gzip compression
- Remove unused heavy dependencies: `html2canvas`, `jspdf`
- Update `axios` to fix CSRF/SSRF/DoS
- Update `@babel/traverse` and `form-data` for security fixes
- Replace hardcoded URLs with environment variables
- Fix `PRASHSHAK_BE` typo in base constants
- Add missing error boundaries and try-catch blocks

### Month 1 (Architectural)
**Phase 2 (Weeks 3–4) — Target: 15% reduction (-2.5MB):**
- Replace `moment-timezone` with `date-fns` (92% size decrease)
- Tree-shake MUI imports (specific component imports instead of bulk)
- Bundle analysis with `webpack-bundle-analyzer`
- Dynamic imports for heavy libraries

**Phase 3 (Weeks 5–6) — Target: 20% reduction (-3.4MB):**
- Feature-based code splitting with `React.lazy()`
- Component-level lazy loading for Payment and Teacher modules
- Lazy load DataGrid and other heavy UI components

**Phase 4 (Weeks 7–8) — Target: 10% reduction (-1.7MB):**
- Student List: virtualized tables
- Teacher List: paginated loading
- Dashboard: lazy widget loading
- Micro-frontend pattern for major features

**Phase 5 (Weeks 9–10) — Target: 8% reduction (-1.4MB):**
- Font optimization (remove unused variants, subsetting)
- Tree-shake MUI icon set
- SVG sprites
- Image optimization: WebP + lazy loading

**Phase 6 (Weeks 11–12) — Target: 7% reduction (-1.2MB):**
- Custom Webpack configurations
- Advanced tree shaking
- Runtime chunk optimization

**Long-term:**
- Transition to micro-frontend architecture
- Comprehensive performance and error monitoring
- CI/CD code quality gates with strict bundle budgets
- Regular security audits

## Test Scenarios
### Functional Tests
- All 26 service files function correctly after deduplication
- Admin dashboard renders on all major route combinations
- Hardcoded URL removal does not break API connectivity in any environment

### Performance & Security Tests
- `npm audit` shows 0 critical vulnerabilities after dependency updates
- Lighthouse performance score improvement from 50/100 baseline
- Bundle size < 5MB total after Phase 1–2 optimizations

### Edge Cases
- What happens when a lazy-loaded module fails in production?
- Environment variable misconfiguration — does the app fail gracefully or silently?

## Async Jobs & ETL
N/A — Frontend performance audit. No async jobs in scope.
