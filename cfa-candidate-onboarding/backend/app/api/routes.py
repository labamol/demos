"""REST API consumed by the React UI."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from backend.app.a2a.cards import AGENT_CARDS
from backend.app.core.db import database_available
from backend.app.mcp.client import MCPFileClient
from backend.app.models.api import (
    ActionToggleRequest,
    AuditLogEntry,
    MockFileSummary,
    RunWorkflowRequest,
    RunWorkflowResponse,
    WorkflowRunSummary,
)
from backend.app.models.domain import WorkflowResult
from backend.app.services import repository
from backend.app.services.audit import AuditRecorder
from backend.app.workflow.graph import OnboardingWorkflow, new_run_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["onboarding"])


@router.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "database": database_available()}


@router.get("/files", response_model=list[MockFileSummary])
async def list_files() -> list[MockFileSummary]:
    """Selectable mock candidate profiles from local directory storage (via MCP)."""
    client = MCPFileClient()
    payload = await client.call_tool("list_profiles")
    return [MockFileSummary.model_validate(item) for item in payload]


@router.post("/workflow/run", response_model=RunWorkflowResponse)
async def run_workflow(request: RunWorkflowRequest) -> RunWorkflowResponse:
    run_id = new_run_id()
    audit = AuditRecorder(run_id=run_id)
    workflow = OnboardingWorkflow(audit)
    try:
        result, answer = await workflow.run(
            file_name=request.file_name,
            question=request.question,
            extra_experience=(
                request.extra_experience.model_dump(mode="json")
                if request.extra_experience
                else None
            ),
            completed_action_ids=request.completed_action_ids,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("workflow run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return RunWorkflowResponse(result=result, answer=answer, audit=audit.entries)


@router.get("/runs", response_model=list[WorkflowRunSummary])
def list_runs(limit: int = 50) -> list[WorkflowRunSummary]:
    return repository.list_runs(limit)


@router.get("/runs/{run_id}", response_model=WorkflowResult)
def get_run(run_id: str) -> WorkflowResult:
    result = repository.get_result(run_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"run {run_id} not found")
    return result


@router.get("/audit", response_model=list[AuditLogEntry])
def get_audit(run_id: str | None = None, limit: int = 500) -> list[AuditLogEntry]:
    return repository.get_audit(run_id, limit)


@router.post("/action-plan/toggle")
def toggle_actions(request: ActionToggleRequest) -> dict[str, int]:
    completed = [item.id for item in request.items if item.completed]
    repository.update_action_items(request.run_id, completed)
    return {"completed": len(completed)}


@router.get("/agents")
def agents() -> list[dict]:
    """Published Google A2A agent cards."""
    return list(AGENT_CARDS.values())
