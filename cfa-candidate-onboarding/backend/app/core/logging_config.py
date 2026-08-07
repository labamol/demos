"""Structured logging configuration shared by the API, agents and MCP server."""

import logging
import sys

from backend.app.core.config import get_settings

_CONFIGURED = False


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    settings = get_settings()
    # stderr, never stdout: the MCP server speaks JSON-RPC over stdout.
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level.upper())
    _CONFIGURED = True
