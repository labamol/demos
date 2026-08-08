---
name: "fastapi-service"
description: "Add or change FastAPI routes, pydantic-settings configuration and startup wiring. Use when touching the HTTP API or configuration."
---

## When to use

Use when adding or changing an HTTP route, application settings, CORS, or startup wiring.

> **Adapt:** define your project's concrete route surface in its domain skill. A run-oriented agentic POC usually needs: health, list inputs, start run, get run, list runs, query audit, mutate an artifact, list agents — plus the agent-protocol routes.

## Rules

- Every route declares an explicit `response_model`; no bare dict returns.
- The API layer is thin: validate, call the workflow or repository, map errors to HTTP status. No business rules in route handlers.
- Errors: 400 validation, 404 unknown resource, 502 when a downstream transport failed *and* its fallback also failed, 500 only for genuine bugs. Structured error bodies with actionable messages; never leak a stack trace.
- Long-running endpoints are async and must not block the event loop; wrap blocking IO appropriately.
- CORS comes from settings, not hard-coded.

## Configuration

- All configuration comes from `.env` via pydantic-settings. Never read `os.environ` directly in application code.
- Every setting has a documented entry in `.env.example` with an empty or safe placeholder value.
- Settings expose derived helpers (resolved data path, resolved config path, whether the LLM is usable) rather than making callers recompute them.
- At startup, log whether the database, LLM and tool server are reachable/configured — to stderr, never stdout, if any child process speaks a stdio protocol.

## Checklist

- [ ] Route has a response model and an error path.
- [ ] New settings documented in `.env.example`.
- [ ] `ruff check` and `black --check` pass.
