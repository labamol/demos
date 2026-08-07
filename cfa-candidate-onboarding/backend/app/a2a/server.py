"""Google A2A JSON-RPC endpoints exposing the POC's remote agents.

Each agent publishes an agent card at
    GET /a2a/{agent}/.well-known/agent.json
and accepts A2A `message/send` JSON-RPC requests at
    POST /a2a/{agent}
The LangGraph workflow calls these agents through `backend.app.a2a.client.A2AClient`,
which keeps agent-to-agent traffic on the protocol rather than direct function calls.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from backend.app.a2a.cards import AGENT_CARDS
from backend.app.agents.action_plan import generate_action_plan
from backend.app.agents.llm import LLMClient
from backend.app.agents.recommendations import generate_recommendations
from backend.app.agents.work_experience import evaluate_work_experience
from backend.app.models.domain import (
    CandidateProfile,
    ReadinessAssessment,
    WorkExperienceEvaluation,
)
from backend.app.services.audit import AuditRecorder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/a2a", tags=["a2a"])


def _handle(agent: str, payload: dict[str, Any]) -> dict[str, Any]:
    run_id = payload.get("run_id") or str(uuid.uuid4())
    audit = AuditRecorder(run_id=run_id, candidate_id=payload.get("candidate_id"))
    llm = LLMClient(audit)
    profile = CandidateProfile.model_validate(payload["profile"])

    if agent == "work-experience-evaluator":
        result = evaluate_work_experience(profile, llm)
    elif agent == "action-plan-generator":
        result = generate_action_plan(
            profile,
            ReadinessAssessment.model_validate(payload["readiness"]),
            WorkExperienceEvaluation.model_validate(payload["work_experience"]),
            llm,
            payload.get("completed_action_ids", []),
        )
    elif agent == "recommendation-agent":
        result = generate_recommendations(profile, llm)
    else:  # pragma: no cover - guarded by caller
        raise HTTPException(status_code=404, detail=f"unknown agent {agent}")

    return {"result": result.model_dump(mode="json"), "llm_used": llm.used}


@router.get("/{agent}/.well-known/agent.json")
def agent_card(agent: str) -> dict[str, Any]:
    if agent not in AGENT_CARDS:
        raise HTTPException(status_code=404, detail=f"unknown agent {agent}")
    return AGENT_CARDS[agent]


@router.get("/agents")
def list_agents() -> list[dict[str, Any]]:
    return list(AGENT_CARDS.values())


@router.post("/{agent}")
async def message_send(agent: str, request: Request) -> dict[str, Any]:
    """Minimal A2A `message/send` handler (JSON-RPC 2.0)."""
    if agent not in AGENT_CARDS:
        raise HTTPException(status_code=404, detail=f"unknown agent {agent}")
    body = await request.json()
    rpc_id = body.get("id", 1)
    if body.get("method") != "message/send":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"method not found: {body.get('method')}"},
        }

    message = body.get("params", {}).get("message", {})
    parts = message.get("parts", [])
    data: dict[str, Any] = {}
    for part in parts:
        if part.get("kind") == "data":
            data.update(part.get("data") or {})
        elif part.get("kind") == "text" and part.get("text"):
            try:
                data.update(json.loads(part["text"]))
            except json.JSONDecodeError:
                data["text"] = part["text"]

    try:
        output = _handle(agent, data)
    except Exception as exc:
        logger.exception("A2A agent %s failed", agent)
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32000, "message": str(exc)}}

    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "kind": "message",
            "role": "agent",
            "messageId": str(uuid.uuid4()),
            "parts": [{"kind": "data", "data": output}],
        },
    }
