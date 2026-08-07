"""Capability 4 - personalized 90-day action-plan generator.

Exposed as a Google A2A remote agent (`action-plan-generator`).
"""

from __future__ import annotations

from backend.app.agents.llm import LLMClient
from backend.app.agents.rules import next_exam_milestone
from backend.app.models.domain import (
    ActionItem,
    ActionPlan,
    CandidateProfile,
    ReadinessAssessment,
    ReferenceStatus,
    WorkExperienceEvaluation,
)

SYSTEM_PROMPT = (
    "You are a CFA Institute candidate-to-member transition coach. You produce concrete, "
    "achievable 90-day plans split across three months. Each action must be a short "
    "imperative sentence."
)


def _deterministic_items(
    profile: CandidateProfile,
    readiness: ReadinessAssessment,
    evaluation: WorkExperienceEvaluation,
) -> list[ActionItem]:
    items: list[ActionItem] = []

    def add(month: int, title: str, detail: str = "", category: str = "membership") -> None:
        items.append(
            ActionItem(
                id=f"m{month}-{len(items) + 1}",
                month=month,  # type: ignore[arg-type]
                title=title,
                detail=detail,
                category=category,
            )
        )

    milestone = next_exam_milestone(profile)
    if milestone:
        add(
            1,
            f"Build your {milestone} study schedule",
            "Block weekly study time and register.",
            "exam",
        )
    add(
        1,
        "Update your work-experience history",
        evaluation.suggested_description or "",
        "experience",
    )
    add(
        1,
        "Capture examples of investment decision support",
        "; ".join(evaluation.missing_evidence[:2]),
        "experience",
    )

    pending_refs = [
        r
        for r in profile.references
        if r.status in {ReferenceStatus.NOT_STARTED, ReferenceStatus.IDENTIFIED}
    ]
    if len(profile.references) < 2:
        add(
            1,
            "Identify two possible references",
            "At least one should be a supervisor.",
            "references",
        )
    add(2, "Complete the recommended financial-modelling module", "", "learning")
    add(2, "Attend one local society event", profile.local_society or "", "society")
    add(2, "Review the membership application requirements", "", "membership")
    add(3, "Finalize your work-experience descriptions", "", "experience")
    if pending_refs or len(profile.references) < 2:
        add(3, "Request your references", "", "references")
    if not profile.membership_application_started:
        add(3, "Begin the membership application", readiness.highest_priority_action, "membership")
    elif not profile.dues_paid:
        add(3, "Pay your annual membership dues", "", "membership")
    return items


def generate_action_plan(
    profile: CandidateProfile,
    readiness: ReadinessAssessment,
    evaluation: WorkExperienceEvaluation,
    llm: LLMClient,
    completed_ids: list[str] | None = None,
) -> ActionPlan:
    items = _deterministic_items(profile, readiness, evaluation)
    summary_fallback = (
        f"Your next 90 days focus on {readiness.highest_priority_action.lower()} while keeping "
        "your membership readiness moving from "
        f"{readiness.score}% toward 100%."
    )
    enriched = llm.complete_json(
        agent_name="action-plan-generator",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            "Given the candidate profile, readiness assessment and work-experience evaluation "
            'below, return JSON {"summary": str, "items": [{"month": 1|2|3, '
            '"title": str, "detail": str, "category": str}]} with 6-10 items.\n\n'
            f"PROFILE: {profile.model_dump_json(indent=2)}\n"
            f"READINESS: {readiness.model_dump_json(indent=2)}\n"
            f"EXPERIENCE: {evaluation.model_dump_json(indent=2)}"
        ),
        fallback={"summary": summary_fallback, "items": []},
    )

    llm_items = enriched.get("items") or []
    if llm_items:
        items = []
        for index, raw in enumerate(llm_items, start=1):
            try:
                month = int(raw.get("month", 1))
            except (TypeError, ValueError):
                month = 1
            month = min(max(month, 1), 3)
            items.append(
                ActionItem(
                    id=f"m{month}-{index}",
                    month=month,  # type: ignore[arg-type]
                    title=str(raw.get("title", "")).strip() or "Membership action",
                    detail=str(raw.get("detail", "")),
                    category=str(raw.get("category", "membership")),
                )
            )

    completed = set(completed_ids or [])
    for item in items:
        item.completed = item.id in completed
    return ActionPlan(summary=str(enriched.get("summary") or summary_fallback), items=items)
