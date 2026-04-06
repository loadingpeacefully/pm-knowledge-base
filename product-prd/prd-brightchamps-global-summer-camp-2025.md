---
title: "PRD BrightChamps Global Summer Camp 2025"
category: product-prd
subcategory: summer-camp
source_id: adc84d64-3d10-42fd-ae51-f55efcb56ad1
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
prd_scope: global-overview
source_notebook: NB5
---

# PRD BrightChamps Global Summer Camp 2025

## Overview

Product requirements for the BrightChamps Global Summer Camp 2025 — a multi-week intensive program available internationally. Covers end-to-end product scope from discovery and checkout through to in-camp experience and post-camp outcomes.

## Problem Statement

BrightChamps Summer Camp 2024 faced challenges with international checkout, inconsistent scheduling experiences across markets, and low awareness among existing students. The 2025 edition needs a product-led approach to scale enrollments globally.

## Goals & Success Metrics

- Grow Summer Camp 2025 enrollments by 40% vs. 2024
- Achieve 70% international enrollment (non-India)
- Achieve 85% camp completion rate (students who start complete all sessions)
- Generate 500+ showcase projects from camp participants

## User Stories / Jobs-to-Be-Done

- As an international parent, I want to enroll my child in Summer Camp with local payment method and currency
- As a student, I want to know exactly what projects I will build during camp
- As a parent, I want daily updates on what my child is doing at camp
- As a student, I want to share my Summer Camp projects and certificate with friends

## Feature Scope

**In Scope:**
- Global camp landing page with IP-based pricing
- Self-serve enrollment and scheduling
- Camp schedule and daily activity overview
- Parent daily update notifications (WhatsApp/email)
- End-of-camp certificate and showcase project
- Multi-currency checkout (Razorpay + Stripe)

**Out of Scope:**
- Physical camp (fully online)
- In-country local instructor matching (uses existing teacher pool)
- Live streaming of camp to non-enrolled viewers

## Key Design Decisions

- IP-based pricing at checkout (server-side geo-detection)
- Camp is structured in 1-week, 2-week, and 4-week packages
- Each camp day has a defined project output (not open-ended)
- Parent daily updates are automated from teacher class notes (not manual)

## Open Questions / Risks

- How to handle timezone scheduling for international batches efficiently?
- Risk: Teacher availability constraints may limit batch sizes
- Dependency: International payment gateway reliability during peak enrollment period
- Open: What post-camp product pathway is offered to non-existing students who join via Summer Camp?
