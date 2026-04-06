---
title: Server Sent Events (SSE)
category: technical-architecture
subcategory: infrastructure
source_id: 63d6ac15-f515-4055-be32-1594bc88d51c
notebook: Coretech Post-Trial Sales Automation Blueprint
source_type: pdf
created_at: 2026-04-05
source_notebook: NB1
---

# Server Sent Events (SSE)

## Overview
This document covers Server-Sent Events (SSE) as a technology for real-time server-to-client data push over a persistent HTTP connection, including its technical properties, use cases, scaling strategies, advantages, and limitations. It serves as a foundational reference for BrightCHAMPS teams evaluating SSE for notifications or live update features.

## API Contract
- **Protocol**: Standard HTTP (no special handshake)
- **Client**: Opens `EventSource` connection to server endpoint
- **Direction**: Unidirectional — server to client only
- **Data format**: Text-based (JSON/plain text); no native binary support
- **Reconnection**: Automatic built-in reconnection on network drop

## Logic Flow
### Controller Layer
The server maintains a persistent HTTP connection per client. When new data is available, the server pushes it as a text event. The client's `EventSource` API handles the connection and auto-reconnects on drop.

### Service/Facade Layer
**Core SSE Flow:**
1. Client opens `EventSource(url)` connection
2. Server holds the connection open (long-lived HTTP)
3. When an event occurs server-side, it writes the event to the response stream
4. Client's `EventSource` listener receives the event
5. If connection drops, client automatically attempts reconnection (with last event ID tracking)

**Scaling Strategies:**
- **Load Balancing** — Distribute SSE connections across multiple servers
- **Connection Pooling** — Reuse connections to handle client requests efficiently
- **Caching + Pub/Sub** — Use Redis Pub/Sub to broadcast same update to many SSE servers simultaneously
- **CDN** — Distribute static assets to reduce load on SSE servers

### High-Level Design (HLD)
```
Client EventSource
        │
        ▼
HTTP Long-lived Connection (persistent)
        │
        ▼
Server Event Loop
        │
        ├── Event occurs (notification, feed update, etc.)
        ├── Write event to response stream: "data: {json}\n\n"
        └── Client receives event → triggers handler
```

**Graceful Degradation:**
- If connection drops → EventSource auto-reconnects
- Falls back to standard HTTP long polling if SSE is blocked

## External Integrations
- **CDN** — Reduces load on SSE servers for static content
- **Redis Pub/Sub** — Recommended for multi-server SSE broadcasting scenarios

## Internal Service Dependencies
- Applicable to BrightCHAMPS services needing real-time push:
  - **Hermes** (communications service) — notification delivery
  - **Feed service** — live feed updates
  - **Monitoring dashboards** — real-time metric streaming

## Database Operations
N/A — SSE is a transport-layer technology. Database interactions are determined by the specific service using SSE.

## Performance Analysis
### Good Practices
- **Low resource efficiency** — uses fewer server resources than maintaining many WebSocket connections
- **Simple implementation** — client only needs to open `EventSource`; no custom handshake
- **Automatic reconnection** — built-in client-side retry without custom code
- **Stateless updates** — perfect for cases where bidirectional communication is unnecessary
- **Firewall-friendly** — runs over standard HTTP/HTTPS; not blocked by corporate proxies
- **Broad browser compatibility** — natively supported by modern browsers

### Performance Concerns
- **HTTP/1.1 limitation**: Only **6 concurrent SSE connections per browser + domain** — critical constraint for multi-tab usage
- **No binary data**: Text-only transport; cannot stream audio or video
- **No message acknowledgment**: Fire-and-forget — no delivery guarantee
- **Cross-tab limitations**: Cannot share real-time updates across multiple browser tabs
- **Latency at scale**: For very large numbers of users, can introduce latency affecting real-time notification delivery
- **Corporate firewall/proxy risk**: Certain proxies or firewalls may buffer or block SSE streams
- **Legacy browser fallback required**: Niche browsers may not support `EventSource` natively

### Technical Debt
| Severity | Issue |
|----------|-------|
| N/A | Reference/conceptual document — no specific implementation debt |

## Optimization Roadmap
### Week 1 (Quick Wins)
- Ensure SSE server endpoints set correct `Content-Type: text/event-stream` headers
- Implement `Last-Event-ID` tracking so clients resume from the last received event after reconnection
- Use HTTP/2 to remove the 6-connection-per-domain limit

### Month 1 (Architectural)
- Implement Redis Pub/Sub as the broadcast layer when scaling SSE to multiple server instances
- Add connection count monitoring per SSE endpoint to detect scaling bottlenecks
- Evaluate hybrid approach: SSE for broadcast notifications + WebSockets for interactive UI features

## Test Scenarios
### Functional Tests
- Client receives events in real time after server publishes them
- Client automatically reconnects after simulated network drop
- `Last-Event-ID` correctly resumes event stream after reconnection

### Performance & Security Tests
- Concurrent connection load test — find max sustainable connections per server instance
- HTTP/1.1 tab test — verify 6-connection limit behavior in multi-tab scenarios
- SSE endpoint does not leak sensitive data to unauthorized clients

### Edge Cases
- Corporate proxy buffers SSE stream — client receives delayed batched events instead of streaming
- Server process restarts mid-stream — does client reconnect cleanly?
- Very high event frequency (100+ events/second) — does stream remain stable?

## Async Jobs & ETL
N/A — SSE is a transport protocol layer. The async jobs that produce events (e.g., notification triggers, feed update processors) are defined in the services that consume SSE.
