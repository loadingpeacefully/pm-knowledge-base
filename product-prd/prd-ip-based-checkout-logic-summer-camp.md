---
title: PRD IP-Based Checkout Logic for Summer Camp 2025
category: product-prd
subcategory: student-lifecycle
source_id: 5e651e7f-2722-4228-bf97-1d672769b33b
notebook: NB5
source_type: pdf
created_at: 2026-04-05
source_notebook: NB5
---

# PRD IP-Based Checkout Logic for Summer Camp 2025

## Overview

The IP-Based Checkout Logic for Summer Camp is a pricing integrity and UX simplification feature for the Summer Camp purchasing flow. It ensures that the currency, pricing, and payment gateway presented to a user during checkout are determined exclusively by their IP-detected geographic location — not by their phone number prefix, browser language, or device locale. This prevents region-based pricing manipulation and ensures a streamlined, localized checkout experience for every customer.

The feature modifies the course page, checkout screen, and payment screen to consume GeoIP-derived region data. The currency selector becomes read-only and pre-filled; the payment gateway selector auto-populates based on the region's allowed gateways and is hidden when only one gateway applies. When GeoIP detection fails, the system defaults to USD/Stripe and re-enables dropdowns for manual selection.

The business goal is threefold: preserve pricing integrity across regions, eliminate the possibility of users gaming region-based price differences by manipulating input fields, and deliver a frictionless, appropriately localized checkout experience that improves conversion.

## Problem Statement

Without IP-based enforcement, users could potentially access alternate regional pricing by changing their phone number prefix or browser locale — or the system could inadvertently serve incorrect pricing due to relying on client-side signals that are easy to manipulate. This creates revenue leakage in the form of underpriced international sales, inconsistent payment gateway routing (which can cause payment failures), and a confusing UX where users see currency options that don't match their actual payment methods. The Summer Camp checkout flow needed a reliable, server-authoritative mechanism to determine pricing and gateway routing that cannot be overridden by client-side data.

## User Stories

- As a customer visiting the Summer Camp page from the United States, I want the checkout to automatically show USD pricing and the appropriate US-compatible payment gateway, so that I don't have to manually select my currency or encounter payment methods that don't work in my region.
- As a customer in India, I want to see INR pricing and Razorpay as the payment method automatically, so that my checkout experience feels native and payment processing works reliably.
- As a customer who uses a foreign phone number, I want to enter my phone number freely without it changing my displayed currency or payment options, so that I can use my preferred contact number without disrupting checkout.
- As a customer whose location cannot be detected, I want to default to USD pricing with the ability to manually select my currency and payment method, so that I can still complete my transaction even when automatic detection fails.
- As a business owner, I want all pricing and gateway decisions to be made from the server side based on IP, so that users cannot manipulate checkout pricing by changing client-side inputs.

## Feature Scope

### In Scope

- GeoIP-based detection of the user's country on course page load
- Pre-filling and disabling the currency dropdown based on detected country code
- Automatic population of the payment method dropdown based on the region's allowed gateways
- Hiding the payment method dropdown when only one gateway applies for the region (e.g., Razorpay for India)
- Showing the payment method dropdown when multiple gateways apply (e.g., Stripe + PayPal for the US)
- Ensuring phone number input and country prefix do not influence pricing or gateway selection
- Fallback to USD currency and Stripe gateway when GeoIP resolution fails
- Re-enabling currency and payment method dropdowns in the fallback/failed-detection state
- Supported currency and symbol mappings: USD ($), INR (₹), AED (د.إ), SAR (ر.س), QAR (ر.ق), GBP (£)
- Frontend storage of detected region in `window._detectedRegion`
- Console logging for fallback scenarios: `console.log("Region fallback: GeoIP failed, using USD default")`

### Out of Scope

- Non-Summer Camp checkout flows (this feature is scoped to Summer Camp 2025)
- Changes to pricing configuration tables or pricing strategy (managed separately)
- Fraud detection or IP/payment card mismatch flagging (mentioned as roadmap item, not in scope)
- User-facing override of auto-detected country (not in scope; only re-enabled on GeoIP failure)
- Server-side anti-spoofing for VPN/proxy detection

## Functional Requirements

1. **GeoIP Region Detection on Page Load**
   - On loading the course/checkout page, the system must silently call a GeoIP service to detect the user's country.
   - The detected country and country code (e.g., "US", "IN", "AE") must be stored in `window._detectedRegion` for use by downstream checkout logic.
   - Acceptance Criteria: GeoIP lookup completes before the checkout UI renders the pricing and payment options. Detected country is logged and accessible in `window._detectedRegion`.

2. **Currency Dropdown — Pre-filled and Disabled**
   - The `<select name="currency">` element must be automatically populated with the currency corresponding to the detected country code.
   - The dropdown must be disabled/read-only by default, styled visually as grayed out to indicate it is not editable.
   - Acceptance Criteria: Currency field is pre-filled and non-editable for all users with a successfully detected region. Visual styling (gray) clearly communicates the read-only state.

3. **Payment Gateway Dropdown — Auto-Population and Conditional Display**
   - The `<select name="payment_method">` must be automatically populated with all allowed payment gateways for the detected region.
   - If only one gateway is available for the region (e.g., Razorpay for INR/India), the dropdown must be hidden or disabled.
   - If multiple gateways are available (e.g., Stripe + PayPal for USD/US), the dropdown must be shown as an active selector.
   - Acceptance Criteria: Indian users never see the payment method dropdown (only Razorpay applies). US users see a dropdown with at least Stripe and PayPal options. The correct gateway is pre-selected as default where applicable.

4. **Phone Number Isolation from Pricing Logic**
   - Phone number country codes entered by the user during checkout must not trigger any change to the currency selector or payment gateway selection.
   - Phone number data is to be used strictly for contact validation or backend reconciliation.
   - Acceptance Criteria: Entering a +1 (US) phone number on a page loaded with an Indian IP does not change the currency from INR to USD or swap the gateway from Razorpay to Stripe.

5. **Browser and Device Locale Ignored**
   - The system must not use `navigator.language`, device locale, or browser language settings to make pricing or gateway decisions.
   - Acceptance Criteria: A user with an English (US) browser locale accessing from an Indian IP sees INR pricing, not USD.

6. **Pricing Amount DOM Updates**
   - `.price-amount` spans/divs in the page DOM must update automatically to reflect the pricing in the detected region's currency when the page loads.
   - Acceptance Criteria: Prices displayed on the course page and checkout reflect the correct currency amount for the detected region without requiring a page reload.

7. **GeoIP Failure Fallback**
   - If the GeoIP service fails or returns no result, the system must:
     - Default currency to USD
     - Default payment gateway to Stripe
     - Re-enable the currency dropdown for manual selection
     - Re-enable the payment method dropdown for manual selection
     - Log: `console.log("Region fallback: GeoIP failed, using USD default")`
   - Acceptance Criteria: A user whose IP cannot be resolved sees USD pricing with Stripe pre-selected, and can manually change currency and payment method. Console log is present for developer debugging.

## UX/UI Flows

### Standard Flow (GeoIP Success)

1. User navigates to the Summer Camp course page.
2. On page load, GeoIP service detects the user's country silently in the background.
3. Detected region is stored in `window._detectedRegion`.
4. DOM updates automatically:
   - `.price-amount` elements update to show the region-appropriate price.
   - `<select name="currency">` is pre-filled with the detected currency (e.g., INR for India) and disabled/grayed out.
   - `<select name="payment_method">` is populated with the allowed gateways for the region.
5. If only one gateway applies (e.g., India → Razorpay): payment method dropdown is hidden or disabled.
6. If multiple gateways apply (e.g., US → Stripe + PayPal): payment method dropdown is shown and active.
7. User enters their phone number; currency and gateway remain unchanged.
8. User proceeds to checkout and completes payment via the pre-selected gateway.

### Fallback Flow (GeoIP Failure)

1. User navigates to the Summer Camp course page.
2. GeoIP lookup fails (service unavailable, IP unresolvable, etc.).
3. System logs: `console.log("Region fallback: GeoIP failed, using USD default")`.
4. DOM updates to show USD pricing as default.
5. Currency dropdown is set to USD but re-enabled for manual selection.
6. Payment method dropdown shows Stripe as default but is re-enabled for manual selection.
7. User can manually change currency and payment method.
8. User proceeds through checkout with their manually selected options.

### Conflicting Input Flow (Phone Number / Browser Locale)

1. User arrives from an Indian IP (GeoIP detects India → INR → Razorpay).
2. User enters a US phone number (+1 prefix) in the phone field.
3. System detects phone prefix but does not change currency or gateway.
4. Checkout continues with INR pricing and Razorpay as the payment gateway.

## Technical Requirements

- **GeoIP Service Integration:** The frontend must integrate with a third-party or internal GeoIP API to resolve the visitor's IP to a country code on page load. The lookup must be completed before the pricing and gateway UI elements are rendered.
- **`window._detectedRegion` Store:** The detected country code must be stored in `window._detectedRegion` for access by all checkout-related scripts on the page.
- **DOM Manipulation Logic:** JavaScript logic must handle:
  - Updating `.price-amount` spans/divs
  - Setting and disabling `<select name="currency">`
  - Setting and conditionally showing/hiding `<select name="payment_method">`
- **Payment Gateway Configuration:** A country-to-gateway mapping must be maintained (configurable, not hardcoded) covering at minimum: India → Razorpay; US → Stripe + PayPal; UAE → Tabby + Tazapay; UK → Stripe; Saudi Arabia → Tazapay; Qatar → Tazapay.
- **Currency and Symbol Mapping:** The system must support: USD ($), INR (₹), AED (د.إ), SAR (ر.س), QAR (ر.ق), GBP (£).
- **Fallback Logic:** If GeoIP returns no result or errors, fallback to USD + Stripe with re-enabled user-editable dropdowns.
- **No Client-Side Override Sources:** The logic must explicitly ignore `navigator.language`, device locale, and phone number prefix when making currency/gateway decisions.

## Non-Functional Requirements

- **Pricing Integrity:** All pricing and gateway decisions must be authoritative from the server/GeoIP layer; client-side inputs must not override region-derived configuration.
- **Visual Accessibility:** Disabled dropdown elements (currency, payment method in single-gateway regions) must be visually distinct — styled as grayed out — to clearly communicate their read-only state to users.
- **Localization:** The feature must correctly map and display symbols and amounts for the following currencies: USD ($), INR (₹), AED (د.إ), SAR (ر.س), QAR (ر.ق), GBP (£). RTL language considerations may apply for Arabic currency symbols.
- **Browser Logic Exclusions:** The system must explicitly exclude `navigator.language` and device locale from all checkout decision-making logic.
- Specific page load performance targets are not defined in the source document. Reasonable default: GeoIP lookup should not add more than 300ms to the checkout page load time; session-level caching of the IP resolution is recommended.

## Success Metrics

Specific KPIs and OKRs are not defined in the source document. The primary qualitative success marker is the enforcement of pricing integrity and elimination of region-based misuse. Inferred measurable metrics:

- Zero cases of users successfully accessing alternate-region pricing via phone number or browser locale manipulation post-launch
- Checkout conversion rate for international users (expected lift from localized UX)
- Payment failure rate reduction (expected improvement from correct gateway routing per region)
- GeoIP fallback rate (percentage of sessions falling through to USD default; should remain low — below 5%)
- Customer support tickets related to wrong currency displayed at checkout (expected to drop to near zero)

## Edge Cases & Error Handling

- **GeoIP Service Unavailable:** Fail open with USD/Stripe defaults. Re-enable dropdowns for manual selection. Log the fallback event for monitoring.
- **IP Address from VPN or Proxy:** The system will apply whichever country the GeoIP service resolves the IP to (which may be incorrect for VPN users). Since user override is not in scope outside of GeoIP failure, these users may see incorrect pricing. This is an accepted limitation for now; fraud detection/override flagging is noted as a future roadmap item.
- **Unrecognized Country Code:** If GeoIP returns a country code not present in the gateway/currency mapping, the system must fall back to USD/Stripe defaults rather than showing an error or breaking the checkout page.
- **Conflicting Phone Number Prefix:** If a user enters a phone number with a country prefix different from their IP-detected region, the system must ignore the phone prefix and maintain the IP-detected currency and gateway. This behavior must be explicit in the frontend logic to prevent any accidental override.
- **Multiple Browser Tabs:** If a user opens the checkout in multiple tabs simultaneously, each tab's GeoIP detection should be independent and consistent (derived from the same IP, so results should match).
- **Currency Dropdown Inadvertent Edit (Accessibility Edge Case):** Since the disabled dropdown is visually grayed out, screen reader users should be informed it is read-only. ARIA attributes (`aria-disabled="true"`, `readonly`) should be applied.

## Dependencies

- **GeoIP Service:** External dependency on a third-party GeoIP resolution service (e.g., MaxMind GeoIP, ipapi, or similar). Feature cannot function without this service. Uptime and latency of this service directly impact checkout page load time.
- **Payment Gateway Configurations:** Correct routing depends on active, configured accounts with Stripe, Razorpay, PayPal, Tabby, and Tazapay for the respective regions. Gateway configuration changes must be reflected in the country-to-gateway mapping table.
- **Summer Camp Pricing Data:** Country-to-pricing mappings must be established and loaded correctly before the feature goes live.
- **Frontend Engineering:** DOM manipulation logic, `window._detectedRegion` implementation, and conditional UI rendering.
- **Backend Engineering:** GeoIP API integration, fallback logic, and country-to-gateway mapping configuration.
- **QA/Testing:** Multi-region test scenarios, fallback state testing, and phone-number-isolation validation.
