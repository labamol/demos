---
name: "mcp-file-access"
description: "Work with an MCP stdio tool server and client for local file/data access, including path containment and stdout hygiene. Use when touching tool-server file access."
---

## When to use

Use for any change that reads local data files through MCP, or that touches the MCP server, client or `mcp.config.json`.

> **Adapt:** the tool names below are illustrative; define your project's tool surface in its domain skill.

## Hard rules

1. **All** local file access for the domain data goes through the MCP tool server. Direct filesystem reads are permitted only as the audited fallback path inside the MCP client.
2. **stdout is reserved for JSON-RPC framing.** The server process must never print to stdout — all logging goes to stderr. A single stray `print()`, or a library that logs to stdout at import time, corrupts the protocol. This failure looks like a hang, not an error.
3. Every path is resolved against the configured data directory and rejected if it escapes it. Resolve symlinks *before* the containment check.

## Typical tool surface

- `list_<items>()` — enumerate available records with their key identifying fields.
- `read_<item>(name)` — read one record.
- `list_documents(owner_id)` / `read_document(relative_path)` — supporting files.

Return structured data; raise a tool error with an actionable message for missing files.

## Client

- Read the server definition from `mcp.config.json` (`mcpServers` map: `command`, `args`, `env`).
- Spawn with `sys.executable` when the configured command is `python`/`python3`, so the child shares the parent's virtualenv. Otherwise the server dies with `ModuleNotFoundError` and you silently run on the fallback path.
- Set `cwd` to the project root and `PYTHONPATH` so the server module imports.
- Use an explicit timeout (e.g. 30s). On timeout or startup failure, fall back to direct filesystem access, record `transport="filesystem-fallback"`, and continue.
- Record the transport actually used on every call — otherwise you cannot tell a working integration from a permanently-degraded one.

## Checklist

- [ ] No stdout writes anywhere in the server process, including at import time.
- [ ] Traversal attempts (`../`, absolute paths, symlinks) rejected.
- [ ] A real stdio round-trip succeeds and records the MCP transport.
- [ ] Killing the server still lets a run complete via the recorded fallback.
