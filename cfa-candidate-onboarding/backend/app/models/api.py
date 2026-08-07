"""Pydantic request/response models for the REST API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.app.models.domain import ActionItem, WorkExperience, WorkflowResult


class MockFileSummary(BaseModel):
    """A selectable file from local directory storage, discovered through MCP."""

    name: str
    path: str
    size_bytes: int
    kind: str = "application"
    candidate_name: str | None = None
    persona: str | None = None
    lifecycle_stage: str | None = None


class RunWorkflowRequest(BaseModel):
    file_name: str = Field(description="Mock profile file selected in the React UI")
    question: str | None = Field(
        default=None,
        description="Optional candidate question about exams, experience or membership",
    )
    extra_experience: WorkExperience | None = None
    completed_action_ids: list[str] = Field(default_factory=list)


class RunWorkflowResponse(BaseModel):
    result: WorkflowResult
    answer: str | None = None
    audit: list[AuditLogEntry] = Field(default_factory=list)


class AuditLogEntry(BaseModel):
    id: int
    run_id: str
    candidate_id: str | None = None
    event_type: str
    node_name: str | None = None
    agent_name: str | None = None
    status: str
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int | None = None
    created_at: datetime


class WorkflowRunSummary(BaseModel):
    run_id: str
    candidate_id: str
    source_file: str
    status: str
    readiness_score: int | None = None
    llm_used: bool = False
    started_at: datetime
    completed_at: datetime | None = None


class ActionToggleRequest(BaseModel):
    run_id: str
    items: list[ActionItem]


RunWorkflowResponse.model_rebuild()
