---
title: Notifications — Real-time Delivery Mechanisms
category: technical-architecture
subcategory: infrastructure
source_id: 4f213d09-426c-459a-bf97-3f2d1a6fc5fd
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Notifications — Real-time Delivery Mechanisms

## Overview
This document covers the three real-time notification delivery mechanisms available for BrightCHAMPS services: Long Polling, Server-Sent Events (SSE), and WebSockets. It provides a technical comparison of each approach — implementation complexity, scalability, latency, and suitability — to guide which mechanism to use for different notification scenarios (class reminders, live updates, interactive features).

## API Contract
N/A — This is a reference document for transport-layer technology selection, not a specific notification API specification.

## Logic Flow
### Controller Layer
N/A — Technology comparison reference.

### Service/Facade Layer
**Three Notification Delivery Mechanisms:**

**1. Long Polling**
- Client sends HTTP request to server
- Server holds the request open until new data is available or timeout occurs
- Client immediately sends a new request after receiving a response (polling loop)
- Simulates real-time communication using standard HTTP

**2. Server-Sent Events (SSE)**
- Client opens `EventSource` connection to server
- Server maintains a unidirectional stream (server → client only)
- Built-in auto-reconnection on connection drop
- Uses HTTP/2 multiplexing to avoid the 6-connection-per-domain limit

**3. WebSockets**
- Client and server establish a persistent bidirectional connection via upgrade handshake
- Either party can send messages at any time (full-duplex)
- Supports binary data, custom subprotocols, and message acknowledgment

### High-Level Design (HLD)
**Technology Selection Matrix:**

| Scenario | Recommended Mechanism |
|----------|----------------------|
| Class reminders, feed updates, stock tickers | SSE |
| Chat, collaborative whiteboards, gaming | WebSockets |
| Legacy system compatibility, simple polling | Long Polling |
| Online classroom interactive features | WebSockets |
| One-way server notifications (broadcast to all) | SSE |

## External Integrations
N/A — Transport layer reference. Implementation integrations vary by service.

## Internal Service Dependencies
- **Hermes** (communications service) — primary service that would implement notification delivery
- **Feed service** — would use SSE or WebSockets for real-time feed updates
- **Paathshala** (class service) — real-time class status updates

## Database Operations
N/A — Transport layer reference document.

## Performance Analysis
### Good Practices
**Long Polling:**
- Simple implementation using standard HTTP request-response
- Works with most web servers and browsers without additional infrastructure
- Graceful degradation to regular polling if real-time features fail

**SSE:**
- Simple `EventSource` client implementation
- Highly resource-efficient — low server overhead per connection
- Automatic reconnection without custom retry code
- Firewall-friendly (standard HTTP/HTTPS)
- Perfect for broadcast updates (same data to all connected clients)

**WebSockets:**
- Lowest latency for interactive real-time scenarios
- Persistent efficient connections once established
- Supports binary data (audio/video streaming)
- Message acknowledgment for guaranteed delivery
- Can be shared across browser tabs
- Custom subprotocol support

### Performance Concerns
**Long Polling:**
- Scalability challenges — many open connections strain server resources
- Higher latency than SSE/WebSockets (wait for timeout or new data)
- Complex error handling and retry strategies required

**SSE:**
- HTTP/1.1 limit: **6 concurrent connections per browser + domain** (resolved with HTTP/2)
- No cross-tab connection sharing
- No binary data support
- No message acknowledgment — fire-and-forget

**WebSockets:**
- Higher server resource consumption — complex to scale to millions of connections
- May fail in corporate networks/firewalls
- Requires custom error handling and reconnection strategies
- Initial connection handshake overhead

### Technical Debt
| Severity | Issue |
|----------|-------|
| N/A | Reference document — no specific implementation tech debt tracked here |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Audit current notification delivery mechanism in Hermes service
- Determine if any current polling-based notifications can be migrated to SSE for lower overhead

### Month 1 (Architectural)
- Implement SSE for feed updates and class status notifications (one-way broadcast scenarios)
- Implement WebSockets for any interactive real-time classroom or chat features
- Ensure HTTP/2 is enabled on all SSE server endpoints to remove 6-connection limit

## Test Scenarios
### Functional Tests
- Long polling: client receives notification within one polling cycle
- SSE: client auto-reconnects after simulated network drop
- WebSockets: bidirectional message exchange works within 100ms

### Performance & Security Tests
- Long polling: measure server memory under 1000 concurrent open connections
- SSE: verify HTTP/2 multiplexing removes 6-connection browser limit
- WebSockets: 10k concurrent connections load test

### Edge Cases
- Long polling timeout handling — client behavior when server holds connection for >30s
- SSE behind a corporate proxy that buffers the stream
- WebSocket behind a load balancer that terminates connections after idle timeout

## Async Jobs & ETL
N/A — Transport layer reference. Specific notification triggers (e.g., class reminder cron, payment confirmation event) are defined in the originating services.
