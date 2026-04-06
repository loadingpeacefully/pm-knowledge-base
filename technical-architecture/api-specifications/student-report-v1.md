---
title: Student Report (Refund Flow) v1.0
category: technical-architecture
subcategory: api-specifications
source_id: 37388efc-5b4e-49f6-b226-46b7c6dd306c
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Student Report (Refund Flow) v1.0

## Overview
SR V1.0 documents the Unified Refund System for BrightChamps' paid student management. From the Prashashak home page, ops users can initiate a refund for a paid student's course enrollment. The flow involves three services: Prashashak (UI/trigger), Eklavya (data aggregation), and Prabandhan (Zoho CRM refund request creation).

## API Contract

| Property | Value |
|----------|-------|
| Method | Internal (Prashashak → Eklavya → Prabandhan) |
| Path | Prashashak triggers → Eklavya internal endpoint → Prabandhan/Zoho CRM |
| Auth | Internal service auth |
| Content-Type | application/json |

**Data Flow:**
1. User clicks "Refund" in Prashashak for a paid student.
2. Eklavya is called to generate all data needed for the refund request.
3. Eklavya sends its data payload to Prabandhan.
4. Prabandhan calls Zoho CRM API to create a refund request record.

**Note:** The source document is marked as an in-progress design document (LLD sections are stubs). Full request/response schemas and HTTP status codes are listed as "to be filled."

## Logic Flow

### Controller Layer
- Prashashak (ops dashboard) renders a refund trigger button per student/course.
- On click, Prashashak calls Eklavya's refund data endpoint.

### Service/Facade Layer
1. **Prashashak** initiates the refund action from the UI.
2. **Eklavya** gathers all required refund data (student balance, payment history, package details) and forwards to Prabandhan.
3. **Prabandhan** constructs the Zoho CRM refund request payload and calls Zoho CRM API via `zoho.crm.createRecord`.

### High-Level Design (HLD)
- Three-service orchestration: Prashashak → Eklavya → Prabandhan → Zoho CRM.
- Goal: Minimize manual user intervention in the refund process.
- Feature: Refunds <> Unified System (as labeled in Jira/design docs).
- Architecture diagram exists in source (image) but content is not transcribable.

## External Integrations
- **Zoho CRM** — Refund request created via Zoho CRM API (`zoho.crm.createRecord`).

## Internal Service Dependencies
- **Eklavya** — Generates refund data from student and payment records.
- **Prabandhan** — Acts as bridge between internal services and Zoho CRM.
- **Prashashak** — Ops-facing UI for initiating refund.

## Database Operations

### Tables Accessed
- Eklavya payment and balance tables (specific tables not documented in source).
- Zoho CRM records created externally.

### SQL / ORM Queries
- N/A (not documented in source v1.0 — marked as stub in LLD section).

### Transactions
- N/A (not documented in source v1.0).

## Performance Analysis

### Good Practices
- Three-tier separation of concerns (UI → data service → CRM integration) keeps each service focused on its responsibility.

### Performance Concerns
- Source document is incomplete (LLD sections are stubs) — performance benchmarks are listed as "to be filled."

### Technical Debt
| Severity | Issue |
|----------|-------|
| High | Document is marked in-progress — LLD (file structure, code examples, API request/response, HTTP status codes, table ERDs) are all stubs. |
| Medium | No documented rollback or failure handling if Zoho CRM API call fails after Eklavya data aggregation. |

## Optimization Roadmap

### Week 1 (Quick Wins)
- Complete the LLD section with actual API request/response schemas.
- Document HTTP status codes for each service call in the chain.

### Month 1 (Architectural)
- Add idempotency to Zoho CRM refund creation to prevent duplicate refund requests.
- Build a refund status tracking table in Prabandhan DB to track state across the three-service chain.

## Test Scenarios

### Functional Tests
- Initiate refund from Prashashak for a paid student → verify Zoho CRM record is created.
- Verify Eklavya correctly aggregates all required refund data.

### Performance & Security Tests
- N/A (not documented in source v1.0).

### Edge Cases
- Zoho CRM API failure after Eklavya data aggregation — current behavior not documented.
- Student with no active paid balance attempting refund — validation not documented.

## Async Jobs & Automation
- N/A — Refund flow appears to be synchronous per design. No Lambda or SQS documented in this version.
