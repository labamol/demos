"""Conversational Q&A about exams, work experience and membership."""

from __future__ import annotations

from backend.app.agents.llm import LLMClient
from backend.app.agents.rules import REQUIRED_QUALIFYING_MONTHS, next_exam_milestone
from backend.app.models.domain import CandidateProfile, ReadinessAssessment

SYSTEM_PROMPT = (
    "You are the CFA Institute lifecycle assistant. Answer questions about exams, qualifying "
    "work experience and membership using only the supplied candidate context. Be concise "
    "(max 4 sentences) and always state that eligibility guidance is not an official "
    "determination."
)


def answer_question(
    question: str, profile: CandidateProfile, readiness: ReadinessAssessment, llm: LLMClient
) -> str:
    milestone = next_exam_milestone(profile)
    fallback = (
        f"{profile.full_name}, you have passed "
        f"{', '.join(lvl.value for lvl in profile.passed_levels) or 'no levels yet'}"
        + (f" and your next milestone is {milestone}. " if milestone else ". ")
        + f"Your membership readiness is {readiness.score}% and roughly "
        f"{profile.total_qualifying_months:.0f} of {REQUIRED_QUALIFYING_MONTHS} qualifying "
        f"months are documented. Highest priority: {readiness.highest_priority_action.lower()}. "
        "This is guidance only, not an official eligibility determination."
    )
    return llm.complete_text(
        agent_name="qa-agent",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            f"QUESTION: {question}\n\nCANDIDATE: {profile.model_dump_json(indent=2)}\n"
            f"READINESS: {readiness.model_dump_json(indent=2)}"
        ),
        fallback=fallback,
    )
