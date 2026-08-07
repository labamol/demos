---
name: "cfa-fastapi-backend"
description: "Add or change FastAPI routes, settings and startup wiring for the POC backend. Use when touching the HTTP API or configuration."
---

## When to use

Use when adding or changing an HTTP route, application settings, CORS, or startup wiring.

## API surface

```
GET  /api/health
GET  /api/files
POST /api/workflow/run
GET  /api/runs
GET  /api/runs/{run_id}
GET  /api/audit
POST /api/action-plan/toggle
GET  /api/agents
GET  /a2a/agents
GET  /a2a/{agent}/.well-known/agent.json
POST /a2a/{agent}            (JSON-RPC 2.0 message/send)
```

## Rules

- Every route declares an explicit Pydantic `response_model`; no bare dict returns.
- The API layer is thin: validate, call the workflow or repository, map errors to HTTP status. No business rules in route handlers.
- Errors: 400 for validation, 404 for unknown run/file/action, 502 when a downstream transport fails after fallback also failed, 500 only for genuine bugs. Error bodies are structured, with an actionable message; never leak a stack trace.
- Long-running workflow endpoints are async and must not block the event loop; wrap blocking IO appropriately.
- CORS is configured from settings, not hard-coded.

## Configuration

- All configuration comes from `.env` via pydantic-settings. Never read `os.environ` directly in application code.
- Every setting has a documented entry in `.env.example` with an empty or safe placeholder value.
- Settings expose derived helpers (resolved data path, resolved MCP config path, whether the LLM is usable) rather than making callers recompute them.
- At startup, log whether the database, LLM and MCP config are reachable/configured — to stderr, never stdout.

## Checklist

- [ ] Route has a response model and an error path.
- [ ] New settings documented in `.env.example`.
- [ ] `ruff check` and `black --check` pass.
