"""Google A2A client used by the LangGraph workflow to reach remote agents.

Calls the A2A HTTP endpoint when reachable; if the transport fails the call is
executed in-process so the POC still completes, and the fallback is audited.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

import httpx

from backend.app.core.config import get_settings
from backend.app.models.domain import AuditEventType
from backend.app.services.audit import AuditRecorder

logger = logging.getLogger(__name__)


class A2AClient:
    def __init__(self, audit: AuditRecorder, timeout: float = 120.0) -> None:
        self.settings = get_settings()
        self.audit = audit
        self.timeout = timeout

    async def send(self, agent: str, data: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.a2a_base_url.rstrip('/')}/a2a/{agent}"
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "messageId": str(uuid.uuid4()),
                    "parts": [{"kind": "data", "data": data}],
                }
            },
        }
        started = time.perf_counter()
        transport = "a2a-http"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=request)
                response.raise_for_status()
                body = response.json()
            if "error" in body:
                raise RuntimeError(body["error"].get("message", "A2A error"))
            payload = body["result"]["parts"][0]["data"]
        except Exception as exc:
            logger.warning("A2A call to %s failed (%s); executing agent in-process", agent, exc)
            transport = "in-process-fallback"
            from backend.app.a2a.server import _handle

            payload = _handle(agent, data)

        self.audit.record(
            AuditEventType.A2A_CALL,
            agent_name=agent,
            message=f"transport={transport}",
            payload={"transport": transport, "url": url},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        return payload
