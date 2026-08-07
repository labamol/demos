"""Pydantic domain models for the candidate-to-member journey."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LifecycleStage(str, Enum):
    CANDIDATE = "candidate"
    MEMBERSHIP_APPLICANT = "membership_applicant"
    MEMBER = "member"


class ExamLevel(str, Enum):
    LEVEL_I = "Level I"
    LEVEL_II = "Level II"
    LEVEL_III = "Level III"


class ExamStatus(str, Enum):
    PASSED = "passed"
    SCHEDULED = "scheduled"
    REGISTERED = "registered"
    NOT_STARTED = "not_started"
    FAILED = "failed"


class RequirementStatus(str, Enum):
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"
    PARTIALLY_COMPLETE = "partially_complete"
    NOT_STARTED = "not_started"
    PENDING = "pending"


class ReferenceStatus(str, Enum):
    NOT_STARTED = "not_started"
    IDENTIFIED = "identified"
    REQUESTED = "requested"
    SUBMITTED = "submitted"
    VERIFIED = "verified"


class AuditEventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    LLM_CALL = "llm_call"
    MCP_CALL = "mcp_call"
    A2A_CALL = "a2a_call"


class ExamRecord(BaseModel):
    level: ExamLevel
    status: ExamStatus
    result_date: date | None = None
    scheduled_date: date | None = None


class WorkExperience(BaseModel):
    """Input for Capability 3 - work-experience evaluator."""

    job_title: str
    employer: str
    employer_type: str = Field(description="e.g. asset manager, bank, corporate, consultancy")
    role_description: str
    activities: list[str] = Field(default_factory=list)
    start_date: date
    end_date: date | None = None
    months: int = Field(ge=0, description="Employment duration in months")
    investment_time_pct: int = Field(ge=0, le=100)

    @property
    def qualifying_months(self) -> float:
        return round(self.months * self.investment_time_pct / 100, 1)


class Reference(BaseModel):
    name: str
    relationship: str
    status: ReferenceStatus = ReferenceStatus.NOT_STARTED
    is_member: bool = False


class MembershipRequirement(BaseModel):
    name: str
    status: RequirementStatus
    explanation: str
    weight: float = Field(default=0.25, ge=0, le=1)
    completion_pct: int = Field(default=0, ge=0, le=100)


class CandidateProfile(BaseModel):
    """Synthetic candidate profile loaded from local directory storage via MCP."""

    model_config = ConfigDict(populate_by_name=True)

    candidate_id: str
    full_name: str
    email: str
    persona: str = Field(description="Free-text persona label, e.g. 'Advanced candidate'")
    lifecycle_stage: LifecycleStage = LifecycleStage.CANDIDATE
    country: str = "India"
    local_society: str | None = None
    exams: list[ExamRecord] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    professional_conduct_declared: bool = False
    membership_application_started: bool = False
    dues_paid: bool = False
    documents: list[str] = Field(default_factory=list)

    @property
    def passed_levels(self) -> list[ExamLevel]:
        return [e.level for e in self.exams if e.status == ExamStatus.PASSED]

    @property
    def total_qualifying_months(self) -> float:
        return round(sum(w.qualifying_months for w in self.work_experience), 1)


class WorkExperienceEvaluation(BaseModel):
    """Capability 3 output. Guidance only - never an official eligibility determination."""

    qualifying_months_estimate: float
    qualifying_hours_estimate: int
    requirement_months: int = 48
    completion_pct: int = Field(ge=0, le=100)
    likely_qualifying_activities: list[str] = Field(default_factory=list)
    non_qualifying_activities: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    suggested_description: str = ""
    escalation_recommended: bool = False
    rationale: str = ""
    disclaimer: str = (
        "This assessment is guidance only and is not an official CFA Institute "
        "eligibility determination."
    )


class ReadinessAssessment(BaseModel):
    """Capability 2 output. Score comes from transparent rules; narrative comes from the LLM."""

    score: int = Field(ge=0, le=100)
    requirements: list[MembershipRequirement] = Field(default_factory=list)
    highest_priority_action: str
    blocking_gaps: list[str] = Field(default_factory=list)
    rule_breakdown: dict[str, float] = Field(default_factory=dict)
    narrative: str = ""


class ActionItem(BaseModel):
    id: str
    month: Literal[1, 2, 3]
    title: str
    detail: str = ""
    category: str = "membership"
    completed: bool = False


class ActionPlan(BaseModel):
    """Capability 4 output - personalized 90 day plan."""

    horizon_days: int = 90
    summary: str = ""
    items: list[ActionItem] = Field(default_factory=list)

    def by_month(self, month: int) -> list[ActionItem]:
        return [i for i in self.items if i.month == month]


class Recommendation(BaseModel):
    title: str
    kind: Literal["learning", "event", "career", "volunteer", "society"]
    reason: str
    url: str | None = None


class RecommendationBundle(BaseModel):
    learning: list[Recommendation] = Field(default_factory=list)
    events: list[Recommendation] = Field(default_factory=list)
    career: list[Recommendation] = Field(default_factory=list)


class DashboardView(BaseModel):
    """Capability 1 - lifecycle-aware dashboard payload."""

    lifecycle_stage: LifecycleStage
    headline: str
    exam_progression: list[ExamRecord] = Field(default_factory=list)
    next_exam_milestone: str | None = None
    membership_readiness_pct: int = 0
    work_experience_pct: int = 0
    outstanding_actions: list[str] = Field(default_factory=list)
    next_best_actions: list[str] = Field(default_factory=list)
    member_benefits: list[str] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    run_id: str
    candidate_id: str
    source_file: str
    profile: CandidateProfile
    dashboard: DashboardView
    readiness: ReadinessAssessment
    work_experience: WorkExperienceEvaluation
    action_plan: ActionPlan
    recommendations: RecommendationBundle
    transition_ready: bool = False
    llm_used: bool = False
    started_at: datetime
    completed_at: datetime
