---
name: "cfa-mcp-file-access"
description: "Work with the MCP stdio file server and client used for all local-directory profile and document access, including path safety and stdout hygiene. Use when touching file access."
---

## When to use

Use for any change that reads candidate profiles or supporting documents, or that touches the MCP server, client or `mcp.config.json`.

## Hard rules

1. **All** local file access for profiles and documents goes through the MCP tool server. Direct filesystem reads are permitted only as the audited fallback path in the MCP client.
2. **stdout is reserved for JSON-RPC framing.** The MCP server process must never print to stdout. All logging goes to stderr. A single stray `print()` corrupts the protocol.
3. Every path is resolved against the configured data directory and rejected if it escapes it. Resolve symlinks before the containment check.

## Server tools

- `list_profiles()` — profile files with candidate name, id and lifecycle stage.
- `read_profile(file_name)` — one profile document.
- `list_documents(candidate_id)` — supporting documents for a candidate.
- `read_document(relative_path)` — one supporting document.

Return structured data; raise a tool error with an actionable message for missing files.

## Client

- Read server definition from `mcp.config.json` (`mcpServers` map: `command`, `args`, `env`).
- Spawn the server with `sys.executable` when the configured command is `python`/`python3`, so the child shares the API's virtualenv.
- Set `cwd` to the project root and `PYTHONPATH` so the server module imports.
- Use an explicit timeout (30s). On timeout or startup failure, fall back to direct filesystem access, record `transport="filesystem-fallback"`, and continue.
- Record the transport actually used on every call.

## Checklist

- [ ] No stdout writes anywhere in the server process, including dependencies configured at import time.
- [ ] Traversal attempts (`../`, absolute paths, symlinks) are rejected.
- [ ] A real stdio round-trip succeeds and records `mcp-stdio`.
- [ ] Killing the server still lets a run complete via the recorded fallback.
