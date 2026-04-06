---
title: "Consigner Price Visibility Experiment"
category: product-prd
subcategory: marketplace
source_id: a708d204-28f1-41af-9b9d-482e5771a416
notebook: Suneet Jagdev Performance Reviews 2023-2025
source_type: pdf
created_at: 2026-04-06
source_notebook: NB5
---

# Consigner Price Visibility Experiment

## Overview

An experiment on the Wheelseye Truck Booking App (Android) to give consignors real-time visibility into truck operator quotes during the demand search phase. Replaces a 60-minute black-box wait with a live quote stream, creating trust and reducing wait perception.

## Problem Statement

Consignors booking via Wheelseye currently wait up to 60 minutes to receive a best price from the OpSearch algorithm. During this time, they have no visibility into the demand status or incoming quotes. This creates frustration, reduces trust, and leads to demand cancellations.

## Goals & Success Metrics

- Reduce demand cancellation rate during search phase
- Increase user trust score (qualitative survey)
- Increase demand confirmation rate (operator selected and confirmed by consignor)
- Reduce average time from demand creation to confirmation

## User Stories / Jobs-to-Be-Done

- As a consignor, I want to see quotes as they come in so I don't feel like I'm waiting in the dark
- As a consignor, I want to choose the best price from received quotes before the window closes
- As a consignor, I want to understand what stage my demand is at (searching, quotes received, confirming)
- As a consignor, I want to be alerted when my first quote arrives and when time is running out

## Feature Scope

**In Scope:**
- New Demand Search Page with live status updates and animated truck graphic
- Two 30-minute timers: Quote Collection (T1) and Quote Confirmation (T2)
- Up to 5 quotes displayed (max 3 visible without expansion, "View # more" button for rest)
- Status/sub-status sequence: Searching → First price found → Expanding search → Confirm your booking
- Sticky status banners: Searching, Best price found, Choose best price now, Vehicle details fetching
- Quotes expire after T2; best price from OpSearch algorithm shown as fallback
- WhatsApp notifications: First Price Found (T1), Countdown (T2 -15 min)
- Edge case: No quotes in 30 min → "Sorry, this is unusual" state; quotes post-30min handled separately

**Out of Scope:**
- Changes to OpSearch algorithm
- Special Request demands (existing flow maintained, ~20% daily average)
- New operator quotes included in visual display (only Retention Operators shown)

## Key Design Decisions

- OpSearch assignment time reduced from 5 min to 2 min (to start quote collection faster)
- Latest quote shown on top (descending recency order)
- Fixed status timers: 20 seconds each for statuses before first quote arrives
- Experiment runs on shortlisted consignors only (selected from Bidding Experiment Shortlisted Consigners sheet)
- WhatsApp comms sent only if consignor hasn't confirmed after 1 hour

## Open Questions / Risks

- How do consignors perceive waiting for "best price" vs. choosing from limited quotes (risk of regret)?
- Risk: Showing 5 quotes may create analysis paralysis
- Dependency: OpSearch must expose quote stream in real-time to the frontend
- Open: Template 01 (First Price Found WhatsApp) is currently ON HOLD — need business decision
