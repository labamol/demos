---
name: "deployment-config-guard"
description: "Enforce a deliberately minimal deployment-configuration surface and safe dependency additions. Use when adding a dependency or any config/build file."
---

## When to use

Use whenever a change adds a dependency, a configuration file, or a build/deploy artifact.

## The constraint

The project declares a small, closed set of deployment-configuration mechanisms. A typical minimal-POC set is:

1. `requirements.txt` — all Python dependencies, fully pinned (`==`).
2. `.env` — all runtime configuration, documented in a committed `.env.example`. `.env` itself is never committed.
3. One JSON config file for the tool server (e.g. `mcp.config.json`).

> **Adapt:** replace the list above with your project's declared set, and keep this skill as the guard. The value is not the specific three files — it is that an agent refuses to quietly widen the surface.

The frontend's `package.json` covers its own dependencies; that is not deployment configuration.

## Prohibited unless the project's declared set includes them

Dockerfile, docker-compose, Poetry/PDM/Pipenv lock-based runtime project definitions, Helm, Terraform, Procfile, systemd units, or any additional configuration file format. If a task seems to require one, **escalate rather than adding it** — a widened surface is a decision for the project owner, not a workaround for a failing step.

`pyproject.toml` is permitted only for tool configuration (ruff, black) — never for dependency declaration or runtime packaging.

## Adding a dependency

1. Confirm it is genuinely needed and not already satisfied.
2. Prefer a version published at least 7 days ago; never a floating range (`latest`, `*`, unbounded `>=`).
3. Pin it exactly.
4. Say why it was added in the PR description.

## Secrets

- Secrets exist only in `.env`. Never commit `.env`, never hard-code a key, never log a secret value.
- `.env.example` lists every variable with an empty or placeholder value.
- Never relax a security control (dependency age policy, branch protection, registry settings) to make a build pass. Escalate.

## Checklist

- [ ] No new config-file format introduced.
- [ ] New dependency pinned.
- [ ] New setting documented in `.env.example`.
- [ ] `.env` still ignored by git.
