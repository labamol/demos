"""Postgres persistence for candidates, runs and capability outputs."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from backend.app.core.db import session_scope
from backend.app.models.api import AuditLogEntry, WorkflowRunSummary
from backend.app.models.domain import CandidateProfile, WorkflowResult
from backend.app.services.audit import memory_log

logger = logging.getLogger(__name__)

_MEMORY_RUNS: dict[str, WorkflowRunSummary] = {}
_MEMORY_RESULTS: dict[str, WorkflowResult] = {}


def _dumps(value: Any) -> str:
    return json.dumps(json.loads(json.dumps(value, default=str)))


def start_run(run_id: str, source_file: str, question: str | None) -> None:
    """Open the run row. The candidate is unknown until `load_profile` has run."""
    _MEMORY_RUNS[run_id] = WorkflowRunSummary(
        run_id=run_id,
        candidate_id="",
        source_file=source_file,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    try:
        with session_scope() as session:
            session.execute(
                text("""
                    INSERT INTO onboarding.workflow_run
                        (run_id, source_file, status, question)
                    VALUES (CAST(:run_id AS UUID), :source_file, 'running', :question)
                    ON CONFLICT (run_id) DO NOTHING
                    """),
                {"run_id": run_id, "source_file": source_file, "question": question},
            )
    except Exception as exc:  # pragma: no cover
        logger.debug("start_run not persisted (%s)", exc)


def attach_candidate(run_id: str, candidate_id: str) -> None:
    """Link a run to its candidate as soon as the profile has been loaded."""
    summary = _MEMORY_RUNS.get(run_id)
    if summary:
        summary.candidate_id = candidate_id
    try:
        with session_scope() as session:
            session.execute(
                text(
                    "UPDATE onboarding.workflow_run SET candidate_id = :cid "
                    "WHERE run_id = CAST(:run_id AS UUID)"
                ),
                {"cid": candidate_id, "run_id": run_id},
            )
    except Exception as exc:  # pragma: no cover
        logger.debug("attach_candidate not persisted (%s)", exc)


def upsert_candidate(profile: CandidateProfile, source_file: str) -> None:
    try:
        with session_scope() as session:
            session.execute(
                text("""
                    INSERT INTO onboarding.candidate
                        (candidate_id, full_name, email, persona, stage, country, local_society,
                         professional_conduct_declared, membership_application_started, dues_paid,
                         source_file, profile_json)
                    VALUES
                        (:candidate_id, :full_name, :email, :persona,
                         CAST(:stage AS onboarding.lifecycle_stage), :country, :local_society,
                         :conduct, :app_started, :dues, :source_file, CAST(:profile AS JSONB))
                    ON CONFLICT (candidate_id) DO UPDATE SET
                        full_name = EXCLUDED.full_name,
                        email = EXCLUDED.email,
                        persona = EXCLUDED.persona,
                        stage = EXCLUDED.stage,
                        country = EXCLUDED.country,
                        local_society = EXCLUDED.local_society,
                        professional_conduct_declared = EXCLUDED.professional_conduct_declared,
                        membership_application_started = EXCLUDED.membership_application_started,
                        dues_paid = EXCLUDED.dues_paid,
                        source_file = EXCLUDED.source_file,
                        profile_json = EXCLUDED.profile_json,
                        updated_at = now()
                    """),
                {
                    "candidate_id": profile.candidate_id,
                    "full_name": profile.full_name,
                    "email": profile.email,
                    "persona": profile.persona,
                    "stage": profile.lifecycle_stage.value,
                    "country": profile.country,
                    "local_society": profile.local_society,
                    "conduct": profile.professional_conduct_declared,
                    "app_started": profile.membership_application_started,
                    "dues": profile.dues_paid,
                    "source_file": source_file,
                    "profile": _dumps(profile.model_dump()),
                },
            )
            for exam in profile.exams:
                session.execute(
                    text("""
                        INSERT INTO onboarding.exam_record
                            (candidate_id, level, status, result_date, scheduled_date)
                        VALUES (:cid, :level, :status, :result_date, :scheduled_date)
                        ON CONFLICT (candidate_id, level) DO UPDATE SET
                            status = EXCLUDED.status,
                            result_date = EXCLUDED.result_date,
                            scheduled_date = EXCLUDED.scheduled_date
                        """),
                    {
                        "cid": profile.candidate_id,
                        "level": exam.level.value,
                        "status": exam.status.value,
                        "result_date": exam.result_date,
                        "scheduled_date": exam.scheduled_date,
                    },
                )
    except Exception as exc:  # pragma: no cover
        logger.debug("candidate not persisted (%s)", exc)


def complete_run(result: WorkflowResult, answer: str | None) -> None:
    _MEMORY_RESULTS[result.run_id] = result
    summary = _MEMORY_RUNS.get(result.run_id)
    if summary:
        summary.status = "completed"
        summary.readiness_score = result.readiness.score
        summary.llm_used = result.llm_used
        summary.completed_at = result.completed_at
    try:
        with session_scope() as session:
            params = {"run_id": result.run_id, "cid": result.candidate_id}
            session.execute(
                text("""
                    UPDATE onboarding.workflow_run
                       SET status = 'completed',
                           candidate_id = :cid,
                           readiness_score = :score,
                           llm_used = :llm_used,
                           answer = :answer,
                           result_json = CAST(:result AS JSONB),
                           completed_at = now()
                     WHERE run_id = CAST(:run_id AS UUID)
                    """),
                {
                    **params,
                    "score": result.readiness.score,
                    "llm_used": result.llm_used,
                    "answer": answer,
                    "result": _dumps(result.model_dump()),
                },
            )
            session.execute(
                text("""
                    INSERT INTO onboarding.readiness_assessment
                        (run_id, candidate_id, score, highest_priority_action,
                         rule_breakdown, requirements, narrative)
                    VALUES (CAST(:run_id AS UUID), :cid, :score, :action,
                            CAST(:breakdown AS JSONB), CAST(:reqs AS JSONB), :narrative)
                    """),
                {
                    **params,
                    "score": result.readiness.score,
                    "action": result.readiness.highest_priority_action,
                    "breakdown": _dumps(result.readiness.rule_breakdown),
                    "reqs": _dumps([r.model_dump() for r in result.readiness.requirements]),
                    "narrative": result.readiness.narrative,
                },
            )
            we = result.work_experience
            session.execute(
                text("""
                    INSERT INTO onboarding.work_experience_evaluation
                        (run_id, candidate_id, qualifying_months, completion_pct, confidence,
                         escalation_recommended, evaluation_json)
                    VALUES (CAST(:run_id AS UUID), :cid, :months, :pct, :conf, :esc,
                            CAST(:payload AS JSONB))
                    """),
                {
                    **params,
                    "months": we.qualifying_months_estimate,
                    "pct": we.completion_pct,
                    "conf": we.confidence,
                    "esc": we.escalation_recommended,
                    "payload": _dumps(we.model_dump()),
                },
            )
            plan_id = session.execute(
                text("""
                    INSERT INTO onboarding.action_plan (run_id, candidate_id, horizon_days, summary)
                    VALUES (CAST(:run_id AS UUID), :cid, :horizon, :summary)
                    RETURNING id
                    """),
                {
                    **params,
                    "horizon": result.action_plan.horizon_days,
                    "summary": result.action_plan.summary,
                },
            ).scalar_one()
            for item in result.action_plan.items:
                session.execute(
                    text("""
                        INSERT INTO onboarding.action_item
                            (plan_id, external_id, month, title, detail, category, completed)
                        VALUES (:plan_id, :ext, :month, :title, :detail, :category, :completed)
                        ON CONFLICT (plan_id, external_id) DO UPDATE
                            SET completed = EXCLUDED.completed
                        """),
                    {
                        "plan_id": plan_id,
                        "ext": item.id,
                        "month": item.month,
                        "title": item.title,
                        "detail": item.detail,
                        "category": item.category,
                        "completed": item.completed,
                    },
                )
            bundle = result.recommendations
            for group in (bundle.learning, bundle.events, bundle.career):
                for rec in group:
                    session.execute(
                        text("""
                            INSERT INTO onboarding.recommendation
                                (run_id, candidate_id, kind, title, reason, url)
                            VALUES (CAST(:run_id AS UUID), :cid, :kind, :title, :reason, :url)
                            """),
                        {
                            **params,
                            "kind": rec.kind,
                            "title": rec.title,
                            "reason": rec.reason,
                            "url": rec.url,
                        },
                    )
    except Exception as exc:  # pragma: no cover
        logger.debug("run results not persisted (%s)", exc)


def fail_run(run_id: str, error: str) -> None:
    summary = _MEMORY_RUNS.get(run_id)
    if summary:
        summary.status = "failed"
    try:
        with session_scope() as session:
            session.execute(
                text("""
                    UPDATE onboarding.workflow_run
                       SET status = 'failed', error = :error, completed_at = now()
                     WHERE run_id = CAST(:run_id AS UUID)
                    """),
                {"run_id": run_id, "error": error},
            )
    except Exception as exc:  # pragma: no cover
        logger.debug("fail_run not persisted (%s)", exc)


def list_runs(limit: int = 50) -> list[WorkflowRunSummary]:
    try:
        with session_scope() as session:
            rows = session.execute(
                text("""
                    SELECT run_id::text, candidate_id, source_file, status::text,
                           readiness_score, llm_used, started_at, completed_at
                      FROM onboarding.workflow_run
                     ORDER BY started_at DESC
                     LIMIT :limit
                    """),
                {"limit": limit},
            ).all()
        return [
            WorkflowRunSummary(
                run_id=r[0],
                candidate_id=r[1] or "",
                source_file=r[2] or "",
                status=r[3],
                readiness_score=r[4],
                llm_used=r[5],
                started_at=r[6],
                completed_at=r[7],
            )
            for r in rows
        ]
    except Exception as exc:  # pragma: no cover
        logger.debug("falling back to in-memory runs (%s)", exc)
        return sorted(_MEMORY_RUNS.values(), key=lambda r: r.started_at, reverse=True)[:limit]


def get_result(run_id: str) -> WorkflowResult | None:
    try:
        with session_scope() as session:
            row = session.execute(
                text(
                    "SELECT result_json FROM onboarding.workflow_run "
                    "WHERE run_id = CAST(:run_id AS UUID)"
                ),
                {"run_id": run_id},
            ).scalar_one_or_none()
        if row:
            return WorkflowResult.model_validate(row)
    except Exception as exc:  # pragma: no cover
        logger.debug("falling back to in-memory result (%s)", exc)
    return _MEMORY_RESULTS.get(run_id)


def get_audit(run_id: str | None = None, limit: int = 500) -> list[AuditLogEntry]:
    try:
        clause = "WHERE run_id = CAST(:run_id AS UUID)" if run_id else ""
        with session_scope() as session:
            rows = session.execute(
                text(f"""
                    SELECT id, run_id::text, candidate_id, event_type, node_name, agent_name,
                           status, message, payload, duration_ms, created_at
                      FROM onboarding.agent_audit_log
                      {clause}
                     ORDER BY id DESC
                     LIMIT :limit
                    """),
                {"run_id": run_id, "limit": limit} if run_id else {"limit": limit},
            ).all()
        return [
            AuditLogEntry(
                id=r[0],
                run_id=r[1],
                candidate_id=r[2],
                event_type=r[3],
                node_name=r[4],
                agent_name=r[5],
                status=r[6],
                message=r[7],
                payload=r[8] or {},
                duration_ms=r[9],
                created_at=r[10],
            )
            for r in rows
        ]
    except Exception as exc:  # pragma: no cover
        logger.debug("falling back to in-memory audit log (%s)", exc)
        return list(reversed(memory_log(run_id)))[:limit]


def update_action_items(run_id: str, completed_ids: list[str]) -> None:
    result = _MEMORY_RESULTS.get(run_id)
    if result:
        for item in result.action_plan.items:
            item.completed = item.id in completed_ids
    try:
        with session_scope() as session:
            session.execute(
                text("""
                    UPDATE onboarding.action_item ai
                       SET completed = ai.external_id = ANY(:ids)
                      FROM onboarding.action_plan ap
                     WHERE ai.plan_id = ap.id
                       AND ap.run_id = CAST(:run_id AS UUID)
                    """),
                {"ids": completed_ids, "run_id": run_id},
            )
    except Exception as exc:  # pragma: no cover
        logger.debug("action items not persisted (%s)", exc)
