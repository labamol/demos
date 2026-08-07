"""MCP server exposing local directory storage (candidate profiles + documents).

Run standalone over stdio:
    python -m backend.app.mcp.file_server

Registered in mcp.config.json under the `candidate-files` server. The FastAPI app
talks to it through `backend.app.mcp.client.MCPFileClient`, which spawns this server
using the command defined in that config file.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from backend.app.core.config import get_settings
from backend.app.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()
DATA_ROOT: Path = settings.data_path

mcp = FastMCP("candidate-files")


def _safe(relative_path: str) -> Path:
    """Resolve a path inside DATA_ROOT, rejecting traversal outside the storage root."""
    target = (DATA_ROOT / relative_path).resolve()
    if not str(target).startswith(str(DATA_ROOT.resolve())):
        raise ValueError(f"path escapes storage root: {relative_path}")
    return target


@mcp.tool()
def list_profiles() -> str:
    """List the selectable synthetic candidate profile files in local storage."""
    folder = DATA_ROOT / "applications"
    files = sorted(p for p in folder.glob("*.json")) if folder.exists() else []
    payload = []
    for path in files:
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            data = {}
        payload.append(
            {
                "name": path.name,
                "path": str(path.relative_to(DATA_ROOT)),
                "size_bytes": path.stat().st_size,
                "kind": "application",
                "candidate_name": data.get("full_name"),
                "persona": data.get("persona"),
                "lifecycle_stage": data.get("lifecycle_stage"),
            }
        )
    return json.dumps(payload)


@mcp.tool()
def read_profile(file_name: str) -> str:
    """Read one candidate profile JSON file from local directory storage."""
    path = _safe(f"applications/{file_name}") if "/" not in file_name else _safe(file_name)
    if not path.exists():
        raise FileNotFoundError(f"profile not found: {file_name}")
    return path.read_text()


@mcp.tool()
def list_documents(candidate_id: str) -> str:
    """List supporting documents (transcripts, references, employment letters) for a candidate."""
    folder = DATA_ROOT / "documents" / candidate_id
    if not folder.exists():
        return json.dumps([])
    return json.dumps(
        [
            {"name": p.name, "path": str(p.relative_to(DATA_ROOT)), "size_bytes": p.stat().st_size}
            for p in sorted(folder.iterdir())
            if p.is_file()
        ]
    )


@mcp.tool()
def read_document(relative_path: str) -> str:
    """Read the text content of a supporting document from local directory storage."""
    path = _safe(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"document not found: {relative_path}")
    return path.read_text(errors="replace")


if __name__ == "__main__":
    logger.info("Starting MCP file server over %s", DATA_ROOT)
    mcp.run()
