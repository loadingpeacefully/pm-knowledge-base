---
title: Auth Flow Revamp — Student Dashboard
category: technical-architecture
subcategory: architecture
source_id: 3edfa993-dec8-45a6-8e03-16071c3898a2
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Auth Flow Revamp — Student Dashboard

## Overview
This document describes the architectural redesign of the BrightCHAMPS student dashboard authentication system, addressing fragmented login flows, plain-text token storage, and missing security primitives. It introduces a clean four-flow architecture with a centralized FlowController, secure storage utilities, and a phased security hardening plan.

## API Contract
- **Login API**: Called after credential validation in Standard Login Flow
- **Auth Backend**: Called in Magic Link Flow with extracted URL token
- **Token Refresh Endpoint**: Called by TokenManager for auto-login flow when tokens are near expiry
- Auth: JWT tokens with proper expiration
- Headers: Standard Bearer token headers post-login

## Logic Flow
### Controller Layer
A centralized **FlowController** is responsible for:
- Orchestrating which authentication flow to activate (Standard, Magic Link, Masquerade, Auto-Login)
- Managing redirects after successful or failed authentication
- Handling error recovery and fallback scenarios

### Service/Facade Layer
**Four Authentication Flows:**

1. **Standard Login Flow**
   - User enters credentials (email/password or mobile/MPIN)
   - Credentials validated client-side
   - Login API called
   - Secure tokens stored via SecureStorage utility
   - Parent profiles fetched
   - Appropriate student profile selected
   - Authenticated state set

2. **Magic Link Flow**
   - Token extracted from URL parameters
   - Token format validated
   - Backend authentication call made with token
   - URL parameters cleared post-auth
   - Session initialized

3. **Masquerade Flow**
   - Admin permission validation performed first
   - Target student ID extracted
   - Normal auth checks bypassed for admin users
   - Specific student profile loaded

4. **Auto-Login Flow**
   - Stored token expiry checked and validated
   - Token refreshed via TokenManager if near expiry
   - Cached profile loaded without re-authentication

**Support Layer:**
- **SecureStorage utility** — replaces plain `localStorage` with `crypto-js` encrypted storage
- **TokenManager class** — handles automatic token refresh logic and expiry validation
- **SessionManager** — manages session validation, cleanup, and state storage (`TokenPair`, `sessionExpiry`)

### High-Level Design (HLD)
```
User Request
     │
     ▼
FlowController.detect()
     │
     ├── URL has magic_token? → Magic Link Flow
     ├── Admin masquerade params? → Masquerade Flow
     ├── Valid stored tokens? → Auto-Login Flow
     └── Default → Standard Login Flow
                        │
                        ▼
              LoginForm (Unified)
              ├── Tab: Mobile + MPIN
              └── Tab: Email + Password
                        │
                        ▼
              Login API → TokenManager.store()
                        │
                        ▼
              SessionManager.initialize()
                        │
                        ▼
              Authenticated State Set
```

**Domain Layer:** Authentication = "Who is the user?" | Authorization = "What can they access?"
- Permissions managed in Domain layer, not UI layer

## External Integrations
- **crypto-js** — Client-side encryption library for SecureStorage
- JWT token infrastructure (backend-issued)
- Google Sheets (legacy: currently stores MPINs in plain text — flagged as critical security debt)

## Internal Service Dependencies
- Student Dashboard FE → Chowkidar (User and Auth Service) for login API
- FlowController → SessionManager → TokenManager (layered dependency)
- Masquerade flow → Admin permission validation service (likely Prashahak BE)

## Database Operations
### Tables Accessed
Not explicitly detailed — authentication is managed in Chowkidar service. Client-side state uses encrypted storage.

### SQL / ORM Queries
N/A for frontend auth revamp document.

### Transactions
N/A for frontend auth revamp document.

## Performance Analysis
### Good Practices
- Unified LoginForm reduces code duplication between `MobileLogin` and `EmailLogin` components
- Auto-Login flow with cached profiles reduces re-authentication latency
- FlowController centralizes routing logic, preventing scattered auth checks across components
- SecureStorage prevents token exposure in browser dev tools

### Performance Concerns
- 7-level Context Provider chain initialized on app load (identified separately in Feed waterfall doc) impacts TTFB
- Magic link flow requires round-trip validation on every URL-based entry

### Technical Debt
| Severity | Issue |
|----------|-------|
| Critical | MPINs currently stored in plain text on Google Sheets |
| Critical | Tokens stored in plain `localStorage` without encryption (current state) |
| High | Missing token rotation on current system |
| High | Inconsistent magic link handling across entry points |
| High | Complex branching logic with overlapping entry points in current auth code |
| Medium | Heavy code duplication between MobileLogin and EmailLogin components |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Implement SecureStorage utility with crypto-js to replace plain localStorage immediately
- Merge MobileLogin and EmailLogin into unified LoginForm component
- Add FlowController to centralize authentication routing

### Month 1 (Architectural)
- Phase 7 Security Hardening:
  - Migrate to httpOnly cookies for token storage
  - Implement rate limiting on login attempts
  - Add CSRF protection
  - Implement input validation and sanitization
  - Set up security audit logs
- Migrate MPINs off Google Sheets to a secure hashed store in Chowkidar

## Test Scenarios
### Functional Tests
- Standard login with valid email/password returns authenticated state
- Standard login with valid mobile/MPIN returns authenticated state
- Magic link with valid token authenticates and clears URL params
- Magic link with expired/invalid token returns appropriate error
- Masquerade flow only accessible to admin-permissioned users
- Auto-login refreshes token when near expiry and loads cached profile

### Performance & Security Tests
- Rate limiting prevents more than N login attempts per minute per IP
- Stored tokens are unreadable in plain text via browser dev tools
- CSRF token validation blocks cross-site form submissions
- Input sanitization prevents XSS via login fields

### Edge Cases
- What happens when auto-login token is expired and refresh also fails?
- Concurrent login attempts from two tabs with the same account
- Magic link used a second time after first successful auth
- Masquerade session cleanup when admin logs out

## Async Jobs & ETL
N/A — Authentication is a synchronous flow. Token refresh is handled client-side by TokenManager on demand.
