"""Thin OpenAI wrapper with deterministic fallback and audit hooks."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from backend.app.core.config import get_settings
from backend.app.models.domain import AuditEventType
from backend.app.services.audit import AuditRecorder

logger = logging.getLogger(__name__)


class LLMClient:
    """Calls OpenAI when a key is configured; otherwise returns the caller's fallback.

    Every call is recorded in the audit log with model, latency and token usage so
    agent behaviour is fully traceable.
    """

    def __init__(self, audit: AuditRecorder) -> None:
        self.settings = get_settings()
        self.audit = audit
        self.used = False

    @property
    def enabled(self) -> bool:
        return self.settings.use_llm

    def complete_json(
        self,
        *,
        agent_name: str,
        system_prompt: str,
        user_prompt: str,
        fallback: dict[str, Any],
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        if not self.enabled:
            self.audit.record(
                AuditEventType.LLM_CALL,
                agent_name=agent_name,
                status="skipped",
                message="OPENAI_API_KEY not configured - deterministic fallback used",
            )
            return fallback

        started = time.perf_counter()
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            self.used = True
            usage = getattr(response, "usage", None)
            self.audit.record(
                AuditEventType.LLM_CALL,
                agent_name=agent_name,
                message=f"model={self.settings.openai_model}",
                payload={
                    "prompt_chars": len(user_prompt),
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "keys": sorted(parsed.keys()),
                },
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
            return {**fallback, **parsed}
        except Exception as exc:
            logger.warning("LLM call failed for %s: %s", agent_name, exc)
            self.audit.record(
                AuditEventType.LLM_CALL,
                agent_name=agent_name,
                status="error",
                message=str(exc),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
            return fallback

    def complete_text(
        self, *, agent_name: str, system_prompt: str, user_prompt: str, fallback: str
    ) -> str:
        result = self.complete_json(
            agent_name=agent_name,
            system_prompt=system_prompt + ' Respond as JSON: {"text": "..."}',
            user_prompt=user_prompt,
            fallback={"text": fallback},
        )
        return str(result.get("text") or fallback)
