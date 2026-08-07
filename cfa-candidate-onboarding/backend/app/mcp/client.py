"""MCP client used by the agents to reach local directory storage.

The client spawns the server declared in `mcp.config.json` over stdio. If the MCP
runtime cannot be started (e.g. dependencies unavailable in a constrained
environment) it transparently falls back to direct filesystem reads of the same
directory, and the audit log records which transport was used.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from backend.app.core.config import PROJECT_ROOT, get_settings

logger = logging.getLogger(__name__)

STDIO_TIMEOUT_SECONDS = 30.0


class MCPFileClient:
    def __init__(self, server_name: str = "candidate-files") -> None:
        self.settings = get_settings()
        self.server_name = server_name
        self.transport = "mcp-stdio"
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        path: Path = self.settings.mcp_config_file
        if not path.exists():
            raise FileNotFoundError(f"MCP config not found at {path}")
        config = json.loads(path.read_text())
        servers = config.get("mcpServers", {})
        if self.server_name not in servers:
            raise KeyError(f"MCP server '{self.server_name}' missing from {path}")
        return servers[self.server_name]

    @property
    def data_root(self) -> Path:
        return self.settings.data_path

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        arguments = arguments or {}
        try:
            return await asyncio.wait_for(
                self._call_over_stdio(tool_name, arguments), timeout=STDIO_TIMEOUT_SECONDS
            )
        except Exception as exc:
            logger.warning("MCP stdio call failed (%s); using direct filesystem fallback", exc)
            self.transport = "filesystem-fallback"
            return self._call_local(tool_name, arguments)

    async def _call_over_stdio(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        command = self._config["command"]
        if command in {"python", "python3"}:
            # Use the interpreter running the API so the server shares its virtualenv.
            command = sys.executable
        params = StdioServerParameters(
            command=command,
            args=self._config.get("args", []),
            env={**os.environ, **self._config.get("env", {}), "PYTHONPATH": str(PROJECT_ROOT)},
            cwd=str(PROJECT_ROOT),
        )
        async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool(tool_name, arguments)
            text = "".join(block.text for block in response.content if getattr(block, "text", None))
        self.transport = "mcp-stdio"
        return json.loads(text) if _is_json(text) else text

    def _call_local(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        root = self.data_root
        if tool_name == "list_profiles":
            folder = root / "applications"
            payload = []
            for path in sorted(folder.glob("*.json")) if folder.exists() else []:
                try:
                    data = json.loads(path.read_text())
                except json.JSONDecodeError:
                    data = {}
                payload.append(
                    {
                        "name": path.name,
                        "path": str(path.relative_to(root)),
                        "size_bytes": path.stat().st_size,
                        "kind": "application",
                        "candidate_name": data.get("full_name"),
                        "persona": data.get("persona"),
                        "lifecycle_stage": data.get("lifecycle_stage"),
                    }
                )
            return payload
        if tool_name == "read_profile":
            name = arguments["file_name"]
            path = root / name if "/" in name else root / "applications" / name
            return json.loads(path.read_text())
        if tool_name == "list_documents":
            folder = root / "documents" / arguments["candidate_id"]
            if not folder.exists():
                return []
            return [
                {"name": p.name, "path": str(p.relative_to(root)), "size_bytes": p.stat().st_size}
                for p in sorted(folder.iterdir())
                if p.is_file()
            ]
        if tool_name == "read_document":
            return (root / arguments["relative_path"]).read_text(errors="replace")
        raise ValueError(f"unknown MCP tool: {tool_name}")


def _is_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False
