---
name: "a2a-agents"
description: "Implement and call Google A2A specialist agents: agent cards, JSON-RPC message/send endpoints, client dispatch and audited transport fallback. Use when adding or changing a specialist agent."
---

## When to use

Use when adding, changing or calling a specialist agent over the Google A2A protocol.

> **Adapt:** list your project's specialist agents in the project's domain skill. The protocol rules below are domain-independent.

## Server side

- Publish an agent card at `/a2a/{agent}/.well-known/agent.json` containing at minimum: agent id, name, description, version, and the list of skills with id, name, description and example inputs.
- List all agents at `/a2a/agents`.
- Accept JSON-RPC 2.0 `message/send` at the agent's endpoint. The response MUST be a valid JSON-RPC response object: `result` on success, `error` with a numeric code and message on failure. Never return HTTP 200 with a bare payload.
- Validate the request payload with a typed model before dispatch; on validation failure return a JSON-RPC error and persist no partial artifact.
- Every inbound call is audited: agent name, skill, status, duration.

## Client side

- Call agents over HTTP by default. Record `transport="a2a-http"` on success.
- On connection failure or timeout, fall back to the in-process implementation, record `transport="in-process-fallback"`, and continue the run. A transport failure must never fail the run.
- Timeouts must be explicit; do not rely on library defaults.

## Adding a new agent

1. Define the request and response models.
2. Add the agent card entry.
3. Register the dispatch handler.
4. Add the client helper that the workflow node calls.
5. Add the catalogue test asserting every published agent is dispatchable.

## Why a real protocol rather than function calls

The point of A2A here is that agents are independently addressable and discoverable — an integrator can call one without the workflow, and agents can later move out of process without touching callers. Keep the in-process path strictly as a fallback, never as the default, or that property quietly disappears.

## Checklist

- [ ] Card reachable and machine-readable.
- [ ] Agent listed in `/a2a/agents`.
- [ ] Malformed request returns a JSON-RPC error, not a stack trace.
- [ ] Success records the HTTP transport; a forced failure records the fallback.
