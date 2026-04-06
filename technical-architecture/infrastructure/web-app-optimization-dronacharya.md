---
title: Web App Optimization Metrics — dronacharya.brightchamps.com
category: technical-architecture
subcategory: infrastructure
source_id: ee4fd99a-1b85-404c-b1b9-f0cdf182bfdc
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Web App Optimization Metrics — dronacharya.brightchamps.com

## Overview
This document is a technical audit of the teacher dashboard at `dronacharya.brightchamps.com`, classifying the overall application risk as HIGH. It identifies a 16MB build dominated by source maps, bloated dependencies, massive component files, and 56 security vulnerabilities, and proposes a 6-phase optimization plan targeting a ~75% reduction in build size.

## API Contract
N/A — This is a frontend performance audit document.

## Logic Flow
### Controller Layer
N/A — Frontend optimization audit.

### Service/Facade Layer
The teacher dashboard is a React application (TypeScript) with significant architectural debt: a 16MB build, the main bundle at 2.2MB, 56 npm vulnerabilities, and components exceeding 879 lines.

### High-Level Design (HLD)
**Current State:**
- Total build: ~16MB (target: ~4MB)
- Main bundle: 2.2MB (target: <500KB — 77% reduction needed)
- Source maps in production: >10MB overhead
- No gzip/brotli compression
- `myClass/index.tsx`: 879+ lines
- `Calendar.tsx`: 397 lines
- React hooks: 909+ instances across components
- Security vulnerabilities: 56 total

**Target State:**
- Total build: ~4MB
- Main bundle: <500KB
- Source maps: disabled in production
- Compression: enabled

## External Integrations
- **Firebase 10.8.0** — Heavy dependency, not optimized with tree shaking
- **Material-UI (MUI)** — Bulk imports without tree shaking
- **Multiple React video players** — Not optimized
- **axios 0.27.2** — Outdated; CSRF and DoS vulnerabilities (CVE documented)
- **webpack-bundle-analyzer** — Recommended for bundle tracking

## Internal Service Dependencies
- Teacher dashboard → Dronacharya (teacher service)
- Teacher dashboard → Paathshala (class data)
- Teacher dashboard → Doordarshan (meeting links)

## Database Operations
### Tables Accessed
N/A — Frontend audit.

### SQL / ORM Queries
N/A

### Transactions
N/A

## Performance Analysis
### Good Practices
- TypeScript in use (reducing runtime errors)
- Code splitting infrastructure present (some chunks exist)

### Performance Concerns
- Source maps shipped to production: **>10MB overhead** (single largest quick win)
- No gzip or brotli compression configured
- `myClass/index.tsx` at 879+ lines — poor decomposition
- 909+ React hook usages — risk of excessive re-renders and complex state management
- Firebase 10.8.0 loaded without tree shaking
- MUI bulk imports pulling in unused components
- Multiple video player libraries loaded

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | Source maps enabled in production — 10MB+ overhead |
| Critical | `axios 0.27.2` — CSRF, SSRF, DoS vulnerabilities |
| Critical | `form-data` — arbitrary file write vulnerability |
| High | No gzip/brotli compression configured |
| High | Firebase loaded without tree shaking |
| High | Main bundle at 2.2MB — 4x over target |
| High | 56 total npm vulnerabilities (including critical and high severity) |
| Medium | `myClass/index.tsx` at 879+ lines — decomposition needed |
| Medium | 909+ React hooks — re-render risk |
| Medium | `moment` library present — replace with `dayjs` |
| Low | Unencrypted localStorage usage identified |
| Low | Missing try-catch blocks in service calls |

## Optimization Roadmap
### Week 1 (Quick Wins)
**Phase 1 — Quick Wins:**
- Set `GENERATE_SOURCEMAP=false` — removes ~10MB instantly
- Enable gzip/brotli compression in Webpack config — reduces transfer sizes 70–80%
- Set up `webpack-bundle-analyzer`
- Update `axios` to latest (fix CSRF/SSRF/DoS)
- Update `form-data`, `braces`, `@babel/traverse` dependencies
- Replace unencrypted localStorage usage with secure alternatives
- Add missing try-catch blocks in service calls

### Month 1 (Architectural)
**Phase 2 — Dependency Optimization (Weeks 3–4):**
- Implement tree shaking for MUI (specific component imports)
- Replace `moment` with `dayjs` (lighter alternative)
- Optimize vendor chunks with `webpack-bundle-analyzer` guidance

**Phase 3 — Advanced Code Splitting (Weeks 5–6):**
- `React.lazy()` for route-level and component-level code splitting
- Break `myClass/index.tsx` (879 lines) into micro-components

**Phase 4 — Heavy Page Optimization (Weeks 7–8):**
- Calendar page: lazy loading + virtual scrolling (350KB → <150KB)
- Classes Dashboard: split into smaller micro-components
- Optimize Firebase with tree-shaking and lazy initialization

**Phase 5 — Asset Optimization (Weeks 9–10):**
- Convert PNG images to WebP/AVIF
- Font optimization: `font-display: swap` + subsetting (saves 100–200KB)

**Phase 6 — Advanced Webpack (Weeks 11–12):**
- Module Federation for micro-frontend split
- `TerserPlugin` to drop `console.log` and debuggers in production

## Test Scenarios
### Functional Tests
- Source maps removed from production build
- Calendar page renders correctly with virtual scrolling
- Firebase functionality preserved after tree-shaking optimization

### Performance & Security Tests
- Lighthouse score improvement after Phase 1 (baseline vs. post-optimization)
- `npm audit` shows 0 critical and 0 high vulnerabilities after dependency updates
- axios update does not break existing API call patterns

### Edge Cases
- Tree-shaken MUI build still covers all used components
- Virtual scrolling on Calendar page handles large class lists without visual glitches

## Async Jobs & ETL
N/A — Frontend performance audit. No async jobs in scope.
