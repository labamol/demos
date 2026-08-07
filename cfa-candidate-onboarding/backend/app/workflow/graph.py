"""LangGraph agentic workflow for the candidate-to-member transition.

Graph:
    load_profile -> readiness -> work_experience -> [gap_analysis]
                 -> action_plan -> recommendations -> dashboard -> (answer_question?) -> persist

`load_profile` reads local directory storage through MCP; `work_experience`,
`action_plan` and `recommendations` are delegated to remote agents over Google A2A.
Every node emits audit events and a workflow-state checkpoint.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.app.a2a.client import A2AClient
from backend.app.agents import rules
from backend.app.agents.llm import LLMClient
from backend.app.agents.qa import answer_question
from backend.app.mcp.client import MCPFileClient
from backend.app.models.domain import (
    ActionPlan,
    AuditEventType,
    CandidateProfile,
    DashboardView,
    LifecycleStage,
    ReadinessAssessment,
    RecommendationBundle,
    WorkExperience,
    WorkExperienceEvaluation,
    WorkflowResult,
)
from backend.app.services import repository
from backend.app.services.audit import AuditRecorder

logger = logging.getLogger(__name__)

READINESS_SYSTEM_PROMPT = (
    "You explain CFA Institute membership readiness. The numeric score is computed by "
    "deterministic rules and must not be changed - only explain it in at most three sentences."
)


def _keep_last(_: Any, new: Any) -> Any:
    return new


class GraphState(TypedDict, total=False):
    run_id: str
    file_name: str
    question: str | None
    extra_experience: dict[str, Any] | None
    completed_action_ids: list[str]
    profile: Annotated[dict[str, Any], _keep_last]
    documents: list[dict[str, Any]]
    readiness: dict[str, Any]
    work_experience: dict[str, Any]
    action_plan: dict[str, Any]
    recommendations: dict[str, Any]
    dashboard: dict[str, Any]
    answer: str | None
    transition_ready: bool
    llm_used: bool


class OnboardingWorkflow:
    """Builds and runs the LangGraph state machine for one candidate run."""

    def __init__(self, audit: AuditRecorder) -> None:
        self.audit = audit
        self.mcp = MCPFileClient()
        self.a2a = A2AClient(audit)
        self.llm = LLMClient(audit)
        self.graph = self._build()

    # ---------------- nodes ----------------
    async def load_profile(self, state: GraphState) -> GraphState:
        run_id = state["run_id"]
        with self.audit.node("load_profile", agent_name="profile-loader") as meta:
            raw = await self.mcp.call_tool("read_profile", {"file_name": state["file_name"]})
            profile = CandidateProfile.model_validate(raw)
            if state.get("extra_experience"):
                profile.work_experience.append(
                    WorkExperience.model_validate(state["extra_experience"])
                )
            documents = await self.mcp.call_tool(
                "list_documents", {"candidate_id": profile.candidate_id}
            )
            self.audit.candidate_id = profile.candidate_id
            self.audit.record(
                AuditEventType.MCP_CALL,
                node_name="load_profile",
                agent_name="candidate-files",
                message=f"transport={self.mcp.transport}",
                payload={"file": state["file_name"], "documents": len(documents)},
            )
            profile.documents = [d["name"] for d in documents]
            repository.upsert_candidate(profile, state["file_name"])
            repository.attach_candidate(run_id, profile.candidate_id)
            meta.update({"candidate_id": profile.candidate_id, "documents": len(documents)})
            update: GraphState = {
                "profile": profile.model_dump(mode="json"),
                "documents": documents,
            }
        self.audit.checkpoint("load_profile", update)
        return update

    def assess_readiness(self, state: GraphState) -> GraphState:
        with self.audit.node("assess_readiness", agent_name="readiness-agent") as meta:
            profile = CandidateProfile.model_validate(state["profile"])
            breakdown = rules.compute_breakdown(profile)
            score = rules.readiness_score(breakdown)
            priority = rules.highest_priority_action(profile)
            narrative_fallback = (
                f"Membership readiness: {score}%. Your highest-priority action is "
                f"{priority.lower()}."
            )
            narrative = self.llm.complete_text(
                agent_name="readiness-agent",
                system_prompt=READINESS_SYSTEM_PROMPT,
                user_prompt=(
                    f"Score: {score}. Rule breakdown: {breakdown}. "
                    f"Highest priority action: {priority}. "
                    f"Candidate: {profile.model_dump_json(indent=2)}"
                ),
                fallback=narrative_fallback,
            )
            readiness = ReadinessAssessment(
                score=score,
                requirements=rules.build_requirements(profile),
                highest_priority_action=priority,
                blocking_gaps=rules.blocking_gaps(profile),
                rule_breakdown=breakdown,
                narrative=narrative,
            )
            meta.update({"score": score, "gaps": len(readiness.blocking_gaps)})
            update: GraphState = {
                "readiness": readiness.model_dump(mode="json"),
                "transition_ready": rules.transition_ready(profile),
            }
        self.audit.checkpoint("assess_readiness", update)
        return update

    async def evaluate_experience(self, state: GraphState) -> GraphState:
        with self.audit.node("evaluate_experience", agent_name="work-experience-evaluator") as meta:
            response = await self.a2a.send(
                "work-experience-evaluator",
                {
                    "run_id": state["run_id"],
                    "candidate_id": state["profile"]["candidate_id"],
                    "profile": state["profile"],
                },
            )
            evaluation = WorkExperienceEvaluation.model_validate(response["result"])
            meta.update(
                {"completion_pct": evaluation.completion_pct, "confidence": evaluation.confidence}
            )
            update: GraphState = {
                "work_experience": evaluation.model_dump(mode="json"),
                "llm_used": state.get("llm_used", False) or bool(response.get("llm_used")),
            }
        self.audit.checkpoint("evaluate_experience", update)
        return update

    async def build_action_plan(self, state: GraphState) -> GraphState:
        with self.audit.node("build_action_plan", agent_name="action-plan-generator") as meta:
            response = await self.a2a.send(
                "action-plan-generator",
                {
                    "run_id": state["run_id"],
                    "candidate_id": state["profile"]["candidate_id"],
                    "profile": state["profile"],
                    "readiness": state["readiness"],
                    "work_experience": state["work_experience"],
                    "completed_action_ids": state.get("completed_action_ids", []),
                },
            )
            plan = ActionPlan.model_validate(response["result"])
            meta.update({"items": len(plan.items)})
            update: GraphState = {
                "action_plan": plan.model_dump(mode="json"),
                "llm_used": state.get("llm_used", False) or bool(response.get("llm_used")),
            }
        self.audit.checkpoint("build_action_plan", update)
        return update

    async def recommend(self, state: GraphState) -> GraphState:
        with self.audit.node("recommend", agent_name="recommendation-agent") as meta:
            response = await self.a2a.send(
                "recommendation-agent",
                {
                    "run_id": state["run_id"],
                    "candidate_id": state["profile"]["candidate_id"],
                    "profile": state["profile"],
                },
            )
            bundle = RecommendationBundle.model_validate(response["result"])
            meta.update({"learning": len(bundle.learning), "events": len(bundle.events)})
            update: GraphState = {
                "recommendations": bundle.model_dump(mode="json"),
                "llm_used": state.get("llm_used", False) or bool(response.get("llm_used")),
            }
        self.audit.checkpoint("recommend", update)
        return update

    def build_dashboard(self, state: GraphState) -> GraphState:
        with self.audit.node("build_dashboard", agent_name="dashboard-agent") as meta:
            profile = CandidateProfile.model_validate(state["profile"])
            readiness = ReadinessAssessment.model_validate(state["readiness"])
            evaluation = WorkExperienceEvaluation.model_validate(state["work_experience"])
            plan = ActionPlan.model_validate(state["action_plan"])
            transition_ready = bool(state.get("transition_ready"))
            stage = LifecycleStage.MEMBER if transition_ready else profile.lifecycle_stage
            passed = ", ".join(lvl.value for lvl in profile.passed_levels) or "no levels yet"
            milestone = rules.next_exam_milestone(profile)

            if stage == LifecycleStage.MEMBER:
                headline = (
                    f"Welcome, {profile.full_name}. Your membership is active - "
                    "your dashboard now shows renewal, professional learning and society benefits."
                )
                member_benefits = [
                    "Membership renewal and annual dues",
                    "Professional Learning (PL) tracking",
                    "Local society benefits and events",
                    "Member directory and digital charter/badge",
                ]
            else:
                headline = (
                    f"You have passed {passed}. "
                    + (f"Your next major milestone is {milestone}. " if milestone else "")
                    + f"You appear to have completed approximately {evaluation.completion_pct}% "
                    "of the work-experience requirement. "
                    f"{len(plan.by_month(1))} membership preparation activities are recommended."
                )
                member_benefits = []

            dashboard = DashboardView(
                lifecycle_stage=stage,
                headline=headline,
                exam_progression=profile.exams,
                next_exam_milestone=milestone,
                membership_readiness_pct=readiness.score,
                work_experience_pct=evaluation.completion_pct,
                outstanding_actions=readiness.blocking_gaps,
                next_best_actions=[item.title for item in plan.items if not item.completed][:3],
                member_benefits=member_benefits,
            )
            meta.update({"stage": stage.value, "readiness": readiness.score})
            update: GraphState = {"dashboard": dashboard.model_dump(mode="json")}
        self.audit.checkpoint("build_dashboard", update)
        return update

    def answer(self, state: GraphState) -> GraphState:
        question = state.get("question")
        if not question:
            return {"answer": None}
        with self.audit.node("answer_question", agent_name="qa-agent") as meta:
            text = answer_question(
                question,
                CandidateProfile.model_validate(state["profile"]),
                ReadinessAssessment.model_validate(state["readiness"]),
                self.llm,
            )
            meta.update({"question_chars": len(question)})
            update: GraphState = {"answer": text}
        self.audit.checkpoint("answer_question", update)
        return update

    # ---------------- graph ----------------
    def _build(self):
        graph = StateGraph(GraphState)
        graph.add_node("load_profile", self.load_profile)
        graph.add_node("assess_readiness", self.assess_readiness)
        graph.add_node("evaluate_experience", self.evaluate_experience)
        graph.add_node("build_action_plan", self.build_action_plan)
        graph.add_node("recommend", self.recommend)
        graph.add_node("build_dashboard", self.build_dashboard)
        graph.add_node("answer_question", self.answer)

        graph.add_edge(START, "load_profile")
        graph.add_edge("load_profile", "assess_readiness")
        graph.add_edge("assess_readiness", "evaluate_experience")
        graph.add_edge("evaluate_experience", "build_action_plan")
        graph.add_edge("build_action_plan", "recommend")
        graph.add_edge("recommend", "build_dashboard")
        graph.add_conditional_edges(
            "build_dashboard",
            lambda state: "answer_question" if state.get("question") else END,
            {"answer_question": "answer_question", END: END},
        )
        graph.add_edge("answer_question", END)
        return graph.compile()

    async def run(
        self,
        file_name: str,
        question: str | None = None,
        extra_experience: dict[str, Any] | None = None,
        completed_action_ids: list[str] | None = None,
    ) -> tuple[WorkflowResult, str | None]:
        started_at = datetime.now(timezone.utc)
        run_id = self.audit.run_id
        self.audit.record(
            AuditEventType.WORKFLOW_STARTED,
            message=f"file={file_name}",
            payload={"file": file_name, "question": question},
        )
        repository.start_run(run_id, source_file=file_name, question=question)
        try:
            state = await self.graph.ainvoke(
                {
                    "run_id": run_id,
                    "file_name": file_name,
                    "question": question,
                    "extra_experience": extra_experience,
                    "completed_action_ids": completed_action_ids or [],
                }
            )
        except Exception as exc:
            self.audit.record(AuditEventType.WORKFLOW_FAILED, status="error", message=str(exc))
            repository.fail_run(run_id, str(exc))
            raise

        result = WorkflowResult(
            run_id=run_id,
            candidate_id=state["profile"]["candidate_id"],
            source_file=file_name,
            profile=CandidateProfile.model_validate(state["profile"]),
            dashboard=DashboardView.model_validate(state["dashboard"]),
            readiness=ReadinessAssessment.model_validate(state["readiness"]),
            work_experience=WorkExperienceEvaluation.model_validate(state["work_experience"]),
            action_plan=ActionPlan.model_validate(state["action_plan"]),
            recommendations=RecommendationBundle.model_validate(state["recommendations"]),
            transition_ready=bool(state.get("transition_ready")),
            llm_used=bool(state.get("llm_used")) or self.llm.used,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
        )
        answer_text = state.get("answer")
        repository.complete_run(result, answer_text)
        self.audit.record(
            AuditEventType.WORKFLOW_COMPLETED,
            message=f"readiness={result.readiness.score}%",
            payload={
                "readiness": result.readiness.score,
                "transition_ready": result.transition_ready,
            },
        )
        return result, answer_text


def new_run_id() -> str:
    return str(uuid.uuid4())
