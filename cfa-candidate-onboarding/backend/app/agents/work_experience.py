"""Capability 3 - work-experience evaluator agent skill.

Exposed as a Google A2A remote agent (`work-experience-evaluator`) and also callable
in-process as a LangGraph node fallback.
"""

from __future__ import annotations

from backend.app.agents.llm import LLMClient
from backend.app.agents.rules import HOURS_PER_QUALIFYING_MONTH, REQUIRED_QUALIFYING_MONTHS
from backend.app.models.domain import CandidateProfile, WorkExperienceEvaluation

QUALIFYING_KEYWORDS = {
    "financial analysis": "Financial analysis",
    "valuation": "Company and security valuation",
    "investment recommendation": "Investment recommendations",
    "portfolio": "Portfolio construction and management",
    "risk": "Investment risk management",
    "research": "Investment research",
    "due diligence": "Investment due diligence",
    "asset allocation": "Asset allocation",
    "trading": "Trade execution supporting the investment process",
    "client advisory": "Client investment advisory",
}

NON_QUALIFYING_KEYWORDS = {
    "administrative": "Administrative reporting",
    "reporting": "Routine operational reporting",
    "data entry": "Data entry",
    "scheduling": "Scheduling and coordination",
    "reconciliation": "Back-office reconciliation",
    "onboarding paperwork": "Client onboarding paperwork",
}

SYSTEM_PROMPT = (
    "You are a CFA Institute membership work-experience evaluator. You assess whether a "
    "candidate's role involves evaluating or applying financial, economic or statistical data "
    "as part of the investment decision-making process. You never issue an official eligibility "
    "determination - you provide guidance only."
)


def _classify(profile: CandidateProfile) -> tuple[list[str], list[str]]:
    text = " ".join(
        [
            *(w.role_description.lower() for w in profile.work_experience),
            *(a.lower() for w in profile.work_experience for a in w.activities),
            *(w.job_title.lower() for w in profile.work_experience),
        ]
    )
    qualifying = sorted({label for key, label in QUALIFYING_KEYWORDS.items() if key in text})
    non_qualifying = sorted(
        {label for key, label in NON_QUALIFYING_KEYWORDS.items() if key in text}
    )
    return qualifying, non_qualifying


def evaluate_work_experience(profile: CandidateProfile, llm: LLMClient) -> WorkExperienceEvaluation:
    months = profile.total_qualifying_months
    completion_pct = min(round(months / REQUIRED_QUALIFYING_MONTHS * 100), 100)
    qualifying, non_qualifying = _classify(profile)

    missing_evidence: list[str] = []
    if not profile.work_experience:
        missing_evidence.append("No work-experience records captured yet")
    for exp in profile.work_experience:
        if not exp.activities:
            missing_evidence.append(
                f"Activity detail missing for {exp.job_title} at {exp.employer}"
            )
        if exp.investment_time_pct < 50:
            missing_evidence.append(
                f"{exp.job_title}: only {exp.investment_time_pct}% investment-related time recorded"
            )
    if not any("supervisor" in r.relationship.lower() for r in profile.references):
        missing_evidence.append("A supervisor reference confirming the role is not yet identified")

    confidence = 0.35
    if qualifying:
        confidence += 0.15 * min(len(qualifying), 3)
    if profile.work_experience:
        confidence += 0.1
    if non_qualifying:
        confidence -= 0.1
    confidence = round(max(0.1, min(confidence, 0.95)), 2)

    titles = ", ".join(f"{w.job_title} at {w.employer}" for w in profile.work_experience) or "n/a"
    fallback_description = (
        f"Responsible for {', '.join(a.lower() for a in qualifying[:3]) or 'investment support'} "
        "as an input to portfolio and investment decisions; quantify the assets, mandates and "
        "decisions influenced, and state the percentage of time spent on investment work."
    )
    rationale = (
        f"Approximately {months:.0f} qualifying months ({completion_pct}% of the "
        f"{REQUIRED_QUALIFYING_MONTHS} month requirement) derived from {titles}."
    )

    fallback = {
        "likely_qualifying_activities": qualifying,
        "non_qualifying_activities": non_qualifying,
        "missing_evidence": missing_evidence,
        "suggested_description": fallback_description,
        "rationale": rationale,
    }
    enriched = llm.complete_json(
        agent_name="work-experience-evaluator",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            "Evaluate this candidate's work experience against the CFA Institute qualifying "
            "experience rubric and return JSON with keys likely_qualifying_activities (list), "
            "non_qualifying_activities (list), missing_evidence (list), suggested_description "
            "(string, an improved 2-sentence experience description), rationale (string).\n\n"
            f"{profile.model_dump_json(include={'work_experience', 'references'}, indent=2)}"
        ),
        fallback=fallback,
    )

    return WorkExperienceEvaluation(
        qualifying_months_estimate=months,
        qualifying_hours_estimate=int(months * HOURS_PER_QUALIFYING_MONTH),
        requirement_months=REQUIRED_QUALIFYING_MONTHS,
        completion_pct=completion_pct,
        likely_qualifying_activities=list(enriched.get("likely_qualifying_activities") or []),
        non_qualifying_activities=list(enriched.get("non_qualifying_activities") or []),
        missing_evidence=list(enriched.get("missing_evidence") or []),
        confidence=confidence,
        suggested_description=str(enriched.get("suggested_description") or ""),
        escalation_recommended=confidence < 0.5 or bool(non_qualifying and completion_pct >= 90),
        rationale=str(enriched.get("rationale") or rationale),
    )
