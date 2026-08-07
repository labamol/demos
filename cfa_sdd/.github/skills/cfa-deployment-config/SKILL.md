---
name: "cfa-deployment-config"
description: "Guard the POC's deployment configuration constraint: requirements.txt, .env and mcp.config.json only. Use when adding dependencies or any config/build file."
---

## When to use

Use whenever a change adds a dependency, a configuration file, or a build/deploy artifact.

## The constraint

Deployment configuration is limited to exactly three mechanisms:

1. `requirements.txt` — all Python dependencies, fully pinned (`==`).
2. `.env` — all runtime configuration, documented in a committed `.env.example`. `.env` itself is never committed.
3. `mcp.config.json` — the MCP server definition.

The frontend uses `package.json` for its own dependencies; that is not deployment configuration and is unaffected.

## Prohibited

Dockerfile, docker-compose, Poetry/PDM/Pipenv/uv lock-based project definitions for the backend runtime, Helm, Terraform, Procfile, systemd units, CI-only deployment manifests, or any additional configuration file format. If a task seems to require one, escalate rather than adding it.

`pyproject.toml` is permitted **only** for tool configuration (ruff, black) — never for dependency declaration or packaging of the backend runtime.

## Adding a dependency

1. Confirm it is genuinely needed and not already satisfied.
2. Prefer a version published at least 7 days ago; never use a floating range.
3. Pin it exactly in `requirements.txt`.
4. Note why it was added in the PR description.

## Secrets

- Secrets exist only in `.env`. Never commit `.env`, never hard-code a key, never log a secret value.
- `.env.example` lists every variable with an empty or placeholder value, including `OPENAI_API_KEY=`.

## Checklist

- [ ] No new config-file format introduced.
- [ ] New dependency pinned in `requirements.txt`.
- [ ] New setting documented in `.env.example`.
- [ ] `.env` still ignored by git.
