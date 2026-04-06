---
title: "Productized Add Credits Flow V0"
category: product-prd
subcategory: payments
source_id: 1a7fd72d-bc5e-4972-8b63-421cd18a3c0e
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Productized Add Credits Flow V0

## Overview

V0 of a self-serve, product-led flow for parents to add class credits directly from the student dashboard without involving sales. Removes the dependency on a sales rep for credit top-ups and installment purchases.

## Problem Statement

Currently, adding class credits requires contacting the sales team (Prashashak). This creates friction for parents who want to continue courses, delays credit top-up, and increases ops load. A self-serve flow enables parents to purchase credits on their own timeline.

## Goals & Success Metrics

- Achieve 20% of credit additions via self-serve (vs. sales-assisted)
- Reduce average time from credit request to credit added from 24h to < 1h
- Increase renewal conversion rate among parents who initiate top-up flow
- Reduce ops team load for credit addition requests by 30%

## User Stories / Jobs-to-Be-Done

- As a parent, I want to see how many class credits my child has left and buy more without calling anyone
- As a parent, I want to choose a credit bundle that fits my budget
- As a parent, I want to complete payment securely using my preferred method
- As a parent, I want to receive immediate confirmation when credits are added

## Feature Scope

**In Scope:**
- Credits remaining display on parent/student dashboard
- Low credits alert (when < 5 credits remaining)
- Credit bundle selection page (3-4 bundle options)
- Checkout with Razorpay (India) / Stripe (international)
- Confirmation message (WhatsApp + email) on successful payment
- Credits reflected in dashboard in real-time post-payment

**Out of Scope:**
- Custom credit amount (pre-defined bundles only in V0)
- Installment payment plans (V1)
- Gifting credits to another student

## Key Design Decisions

- Low-credit alert shown proactively at < 5 credits (not only when student tries to book)
- Bundle options designed to match existing pricing tiers (no new pricing needed)
- Payment uses existing parent hub payment flow with no new gateway integration
- Credits added to student account within 5 minutes of payment confirmation

## Open Questions / Risks

- Should the sales team be notified when a parent initiates self-serve credit purchase?
- Risk: Parents may reduce engagement with sales team, affecting upsell opportunities
- Dependency: Razorpay/Stripe payment success webhook reliability
- Open: How to handle payment disputes for self-serve credit purchases?
