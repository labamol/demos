"""Audit trail + workflow-state persistence.

Every agent node writes a `node_started` / `node_completed` pair plus one event per
LLM, MCP and A2A interaction, so a full execution trace can be replayed from Postgres.
When Postgres is unreachable the recorder degrades to an in-memory buffer so the POC
still runs, and flags `persisted=False` on the API response.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from backend.app.core.db import session_scope
from backend.app.models.api import AuditLogEntry
from backend.app.models.domain import AuditEventType

logger = logging.getLogger(__name__)

_MEMORY_LOG: list[AuditLogEntry] = []
_MEMORY_SEQ = 0


def _memory_append(**kwargs: Any) -> AuditLogEntry:
    global _MEMORY_SEQ
    _MEMORY_SEQ += 1
    entry = AuditLogEntry(id=_MEMORY_SEQ, created_at=datetime.now(timezone.utc), **kwargs)
    _MEMORY_LOG.append(entry)
    return entry


class AuditRecorder:
    """Records audit events for a single workflow run."""

    def __init__(self, run_id: str, candidate_id: str | None = None) -> None:
        self.run_id = run_id
        self.candidate_id = candidate_id
        self.persisted = True
        self._sequence = 0
        self.entries: list[AuditLogEntry] = []

    # -- events ------------------------------------------------------
    def record(
        self,
        event_type: AuditEventType | str,
        *,
        status: str = "ok",
        node_name: str | None = None,
        agent_name: str | None = None,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
        duration_ms: int | None = None,
    ) -> AuditLogEntry:
        event = event_type.value if isinstance(event_type, AuditEventType) else event_type
        payload = _jsonable(payload or {})
        row = {
            "run_id": self.run_id,
            "candidate_id": self.candidate_id,
            "event_type": event,
            "node_name": node_name,
            "agent_name": agent_name,
            "status": status,
            "message": message,
            "payload": payload,
            "duration_ms": duration_ms,
        }
        logger.info(
            "audit run=%s event=%s node=%s agent=%s status=%s %s",
            self.run_id,
            event,
            node_name,
            agent_name,
            status,
            message or "",
        )
        entry: AuditLogEntry | None = None
        try:
            with session_scope() as session:
                result = session.execute(
                    text("""
                        INSERT INTO onboarding.agent_audit_log
                            (run_id, candidate_id, event_type, node_name, agent_name,
                             status, message, payload, duration_ms)
                        VALUES
                            (:run_id, :candidate_id, :event_type, :node_name, :agent_name,
                             :status, :message, CAST(:payload AS JSONB), :duration_ms)
                        RETURNING id, created_at
                        """),
                    {**row, "payload": json.dumps(payload)},
                ).one()
                entry = AuditLogEntry(id=result.id, created_at=result.created_at, **row)
        except Exception as exc:  # pragma: no cover - depends on DB availability
            self.persisted = False
            logger.debug("audit persistence unavailable (%s); buffering in memory", exc)
            entry = _memory_append(**row)
        self.entries.append(entry)
        return entry

    @contextmanager
    def node(self, node_name: str, agent_name: str | None = None) -> Iterator[dict[str, Any]]:
        """Context manager emitting node_started / node_completed (or node_failed)."""
        self.record(AuditEventType.NODE_STARTED, node_name=node_name, agent_name=agent_name)
        started = time.perf_counter()
        meta: dict[str, Any] = {}
        try:
            yield meta
        except Exception as exc:
            self.record(
                AuditEventType.NODE_FAILED,
                node_name=node_name,
                agent_name=agent_name,
                status="error",
                message=str(exc),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
            raise
        self.record(
            AuditEventType.NODE_COMPLETED,
            node_name=node_name,
            agent_name=agent_name,
            payload=meta,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    # -- workflow state ---------------------------------------------
    def checkpoint(self, node_name: str, state: dict[str, Any]) -> None:
        self._sequence += 1
        try:
            with session_scope() as session:
                session.execute(
                    text("""
                        INSERT INTO onboarding.workflow_state
                            (run_id, node_name, sequence, state_json)
                        VALUES (:run_id, :node_name, :sequence, CAST(:state AS JSONB))
                        ON CONFLICT (run_id, sequence) DO NOTHING
                        """),
                    {
                        "run_id": self.run_id,
                        "node_name": node_name,
                        "sequence": self._sequence,
                        "state": json.dumps(_jsonable(state)),
                    },
                )
        except Exception as exc:  # pragma: no cover
            self.persisted = False
            logger.debug("state checkpoint skipped (%s)", exc)


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str))


def memory_log(run_id: str | None = None) -> list[AuditLogEntry]:
    if run_id:
        return [e for e in _MEMORY_LOG if e.run_id == run_id]
    return list(_MEMORY_LOG)
