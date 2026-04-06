---
title: BrightCHAMPS Platform Architecture Overview
category: technical-architecture
subcategory: architecture
source_id: f341d399-d959-4f91-b000-a3a678108492
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# BrightCHAMPS Platform Architecture Overview

## Overview
This document outlines the unified microservices architecture of the BrightCHAMPS educational platform, describing all backend services, frontend applications, tech stack, cloud infrastructure, and high-level system flows connecting students, teachers, and administrators.

## API Contract
N/A — This is a system architecture overview document, not an API specification.

## Logic Flow
### Controller Layer
Requests from the three main user groups (students, teachers, administrators) flow through their respective frontend applications into a central backend layer. The Prashahak BE (Admin Backend) acts as a gateway that interacts with all core microservices.

### Service/Facade Layer
Each domain is handled by a named microservice:
- **Paathshala** — Class service
- **Doordarshan** — Meetings service
- **Dronacharya** — Teacher service
- **Prabandhan** — CRM service
- **Eklavya** — Student service
- **Tryouts** — Demo Booking and Predictions service
- **Chowkidar** — User and Authentication Service
- **Shotgun** — Quiz service
- **Payments** — Sales and payments service
- **Hermes** — Communications service
- **Prashahak BE** — Admin Dashboard backend, interacts with all core services

### High-Level Design (HLD)
The platform supports the following end-to-end logical flows:
1. **Lead / Demo Booking Flow** — Prospect enters the system, books a demo session
2. **Authentication Flow** — Login, token management, session handling
3. **Class and Meetings / Conference Flows** — Scheduling, joining, post-class actions
4. **CRM and Payments Flows** — Deal creation, invoicing, payment processing
5. **Student, Teacher, and Admin Flows** — Profile management, dashboard interactions
6. **Quiz Flows** — Assessment creation, delivery, scoring

## External Integrations
- **Zoom** — Video conferencing for classes and meetings
- **Zoho** — CRM data management
- **AWS CloudFront** — Content delivery network
- **AWS SQS** — Message queuing for async jobs
- **AWS S3** — Object storage
- **AWS Elemental MediaConvert** — Video content processing for classes
- **AWS RDS** — Hosted MySQL database
- **AWS EKS** — Kubernetes service for containerized microservice deployment
- **AWS Lambda** — Serverless functions for background processing

## Internal Service Dependencies
- Prashahak BE → all core services (Eklavya, Paathshala, Dronacharya, Prabandhan, Chowkidar, Doordarshan, Payments, Hermes)
- Tryouts → Paathshala (for class scheduling during demo flow)
- Payments → Eklavya (for student package association)
- Doordarshan → Zoom (for meeting creation)

## Database Operations
### Tables Accessed
- MySQL DB hosted on AWS RDS (primary relational store)
- MongoDB self-hosted on EC2 instances (document store for flexible/unstructured data)

### SQL / ORM Queries
Not detailed in this document — see DB Design document for schema specifics.

### Transactions
Not detailed in this architectural overview.

## Performance Analysis
### Good Practices
- Kubernetes (EKS) enables horizontal scaling of individual microservices
- CloudFront CDN reduces latency for static asset delivery
- SQS decouples synchronous request handling from async processing jobs
- Serverless Lambda functions allow on-demand compute for background tasks

### Performance Concerns
- Multiple self-hosted MongoDB instances on EC2 introduce operational overhead and potential inconsistency in scaling
- Cross-service communication patterns not documented — potential N+1 or chatty service calls

### Technical Debt
| Severity | Issue |
|----------|-------|
| Medium | MongoDB self-hosted on EC2 rather than managed Atlas — operational risk |
| Low | PHP still present in tech stack alongside React/Next.js — mixed language burden |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Document cross-service API contracts between all microservices
- Ensure CloudFront cache headers are optimized for static assets

### Month 1 (Architectural)
- Evaluate migrating self-hosted MongoDB to AWS Atlas for managed scaling
- Introduce an API gateway layer to centralize auth, rate limiting, and routing across microservices

## Test Scenarios
### Functional Tests
- Verify each microservice handles its domain independently (Paathshala for classes, Eklavya for students, etc.)
- Validate that Prashahak BE correctly orchestrates cross-service requests

### Performance & Security Tests
- Load test EKS pods under peak class scheduling windows
- Verify SQS queue depth doesn't accumulate unbounded during traffic spikes

### Edge Cases
- What happens if Doordarshan (meetings service) is unavailable during a demo booking?
- Fallback behavior when MediaConvert fails for video processing

## Async Jobs & ETL
- AWS SQS queues used for decoupled async processing (e.g., communications, class updates)
- AWS Lambda functions for serverless background tasks
- AWS Elemental MediaConvert for video class content transcoding
