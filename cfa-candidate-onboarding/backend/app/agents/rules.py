"""Transparent, deterministic rules for membership readiness (Capability 2).

The score is intentionally rule-based rather than LLM generated; the LLM only adds
the explanatory narrative on top of these numbers.
"""

from __future__ import annotations

from backend.app.models.domain import (
    CandidateProfile,
    ExamLevel,
    MembershipRequirement,
    ReferenceStatus,
    RequirementStatus,
)

REQUIRED_QUALIFYING_MONTHS = 48
REQUIRED_REFERENCES = 2
HOURS_PER_QUALIFYING_MONTH = 160

WEIGHTS: dict[str, float] = {
    "exams": 0.40,
    "work_experience": 0.30,
    "references": 0.15,
    "application": 0.10,
    "professional_conduct": 0.05,
}

EXAM_ORDER = [ExamLevel.LEVEL_I, ExamLevel.LEVEL_II, ExamLevel.LEVEL_III]


def exam_completion(profile: CandidateProfile) -> float:
    passed = set(profile.passed_levels)
    return len([lvl for lvl in EXAM_ORDER if lvl in passed]) / len(EXAM_ORDER)


def work_experience_completion(profile: CandidateProfile) -> float:
    return min(profile.total_qualifying_months / REQUIRED_QUALIFYING_MONTHS, 1.0)


def reference_completion(profile: CandidateProfile) -> float:
    accepted = {ReferenceStatus.SUBMITTED, ReferenceStatus.VERIFIED}
    submitted = len([r for r in profile.references if r.status in accepted])
    return min(submitted / REQUIRED_REFERENCES, 1.0)


def next_exam_milestone(profile: CandidateProfile) -> str | None:
    passed = set(profile.passed_levels)
    for level in EXAM_ORDER:
        if level not in passed:
            return level.value
    return None


def compute_breakdown(profile: CandidateProfile) -> dict[str, float]:
    return {
        "exams": round(exam_completion(profile), 4),
        "work_experience": round(work_experience_completion(profile), 4),
        "references": round(reference_completion(profile), 4),
        "application": 1.0 if profile.membership_application_started else 0.0,
        "professional_conduct": 1.0 if profile.professional_conduct_declared else 0.0,
    }


def readiness_score(breakdown: dict[str, float]) -> int:
    return round(sum(breakdown[key] * weight for key, weight in WEIGHTS.items()) * 100)


def build_requirements(profile: CandidateProfile) -> list[MembershipRequirement]:
    breakdown = compute_breakdown(profile)
    passed = [lvl.value for lvl in profile.passed_levels]
    hours = int(profile.total_qualifying_months * HOURS_PER_QUALIFYING_MONTH)
    accepted = {ReferenceStatus.SUBMITTED, ReferenceStatus.VERIFIED}
    submitted_refs = len([r for r in profile.references if r.status in accepted])

    def status_for(value: float, started: bool) -> RequirementStatus:
        if value >= 1.0:
            return RequirementStatus.COMPLETE
        if value <= 0.0:
            return RequirementStatus.NOT_STARTED if not started else RequirementStatus.PENDING
        return RequirementStatus.PARTIALLY_COMPLETE

    exam_status = (
        RequirementStatus.COMPLETE if breakdown["exams"] >= 1.0 else RequirementStatus.IN_PROGRESS
    )
    return [
        MembershipRequirement(
            name="Exam completion",
            status=exam_status,
            explanation=(
                f"{', '.join(passed) or 'No levels'} completed"
                + (
                    f"; next milestone is {next_exam_milestone(profile)}"
                    if next_exam_milestone(profile)
                    else "; all three levels passed"
                )
            ),
            weight=WEIGHTS["exams"],
            completion_pct=round(breakdown["exams"] * 100),
        ),
        MembershipRequirement(
            name="Work experience",
            status=status_for(breakdown["work_experience"], bool(profile.work_experience)),
            explanation=(
                f"Estimated {hours:,} qualifying hours "
                f"({profile.total_qualifying_months:.0f} of {REQUIRED_QUALIFYING_MONTHS} months)"
            ),
            weight=WEIGHTS["work_experience"],
            completion_pct=round(breakdown["work_experience"] * 100),
        ),
        MembershipRequirement(
            name="References",
            status=status_for(breakdown["references"], bool(profile.references)),
            explanation=(
                f"{submitted_refs} of {REQUIRED_REFERENCES} required references submitted"
            ),
            weight=WEIGHTS["references"],
            completion_pct=round(breakdown["references"] * 100),
        ),
        MembershipRequirement(
            name="Membership application",
            status=(
                RequirementStatus.IN_PROGRESS
                if profile.membership_application_started
                else RequirementStatus.NOT_STARTED
            ),
            explanation="Available once exam and experience prerequisites are met",
            weight=WEIGHTS["application"],
            completion_pct=round(breakdown["application"] * 100),
        ),
        MembershipRequirement(
            name="Professional conduct declaration",
            status=(
                RequirementStatus.COMPLETE
                if profile.professional_conduct_declared
                else RequirementStatus.PENDING
            ),
            explanation="Required during the membership application",
            weight=WEIGHTS["professional_conduct"],
            completion_pct=round(breakdown["professional_conduct"] * 100),
        ),
    ]


def highest_priority_action(profile: CandidateProfile) -> str:
    breakdown = compute_breakdown(profile)
    if breakdown["exams"] < 1.0:
        return f"Prepare for and pass {next_exam_milestone(profile)}"
    if breakdown["work_experience"] < 1.0:
        remaining = REQUIRED_QUALIFYING_MONTHS - profile.total_qualifying_months
        return (
            "Document your current work experience to close the estimated "
            f"{remaining:.0f} month gap"
        )
    if breakdown["references"] < 1.0:
        return "Request your professional references"
    if breakdown["application"] < 1.0:
        return "Start your membership application"
    if breakdown["professional_conduct"] < 1.0:
        return "Complete the professional conduct declaration"
    if not profile.dues_paid:
        return "Pay your annual membership dues"
    return "You are ready for membership - review your member dashboard"


def blocking_gaps(profile: CandidateProfile) -> list[str]:
    breakdown = compute_breakdown(profile)
    labels = {
        "exams": "Remaining CFA exam levels",
        "work_experience": "Qualifying work experience evidence",
        "references": "Professional references",
        "application": "Membership application not started",
        "professional_conduct": "Professional conduct declaration pending",
    }
    return [labels[key] for key, value in breakdown.items() if value < 1.0]


def transition_ready(profile: CandidateProfile) -> bool:
    breakdown = compute_breakdown(profile)
    return all(value >= 1.0 for value in breakdown.values()) and profile.dues_paid
