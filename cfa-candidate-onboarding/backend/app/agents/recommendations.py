"""Recommended learning, events and career activities (persona 3 / member value)."""

from __future__ import annotations

from backend.app.agents.llm import LLMClient
from backend.app.models.domain import (
    CandidateProfile,
    LifecycleStage,
    Recommendation,
    RecommendationBundle,
)

SYSTEM_PROMPT = (
    "You recommend CFA Institute learning modules, society events and career activities "
    "that match the user's lifecycle stage and experience gaps."
)


def _baseline(profile: CandidateProfile) -> RecommendationBundle:
    society = profile.local_society or "your local society"
    if profile.lifecycle_stage == LifecycleStage.MEMBER:
        return RecommendationBundle(
            learning=[
                Recommendation(
                    title="Professional Learning: Private Markets",
                    kind="learning",
                    reason="Counts toward your annual PL hours.",
                ),
                Recommendation(
                    title="Ethics refresher module",
                    kind="learning",
                    reason="Keeps your conduct declaration current.",
                ),
            ],
            events=[
                Recommendation(
                    title=f"{society} annual forecast dinner",
                    kind="event",
                    reason="High-value local networking.",
                ),
                Recommendation(
                    title="Global Investment Conference",
                    kind="event",
                    reason="Matches your stated interests.",
                ),
            ],
            career=[
                Recommendation(
                    title="Mentor a Level III candidate",
                    kind="volunteer",
                    reason="Volunteer opportunity with your society.",
                ),
                Recommendation(
                    title="Member directory profile refresh",
                    kind="career",
                    reason="Improves networking discoverability.",
                ),
            ],
        )
    return RecommendationBundle(
        learning=[
            Recommendation(
                title="Practical Skills Module: Financial Modeling",
                kind="learning",
                reason="Strengthens the investment analysis evidence in your application.",
            ),
            Recommendation(
                title="Learning Ecosystem: Level III mock exam set",
                kind="learning",
                reason="Targets your next exam milestone.",
            ),
        ],
        events=[
            Recommendation(
                title=f"{society} candidate-to-member briefing",
                kind="event",
                reason="Explains the society review step of your application.",
            ),
        ],
        career=[
            Recommendation(
                title="Work-experience writing clinic",
                kind="career",
                reason="Helps you document qualifying activities.",
            ),
        ],
    )


def generate_recommendations(profile: CandidateProfile, llm: LLMClient) -> RecommendationBundle:
    bundle = _baseline(profile)
    enriched = llm.complete_json(
        agent_name="recommendation-agent",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            'Return JSON {"learning": [{"title", "reason"}], "events": [...], '
            '"career": [...]} with at most 3 entries per group for this user.\n'
            f"{profile.model_dump_json(indent=2)}"
        ),
        fallback={},
    )
    for group, kind in (("learning", "learning"), ("events", "event"), ("career", "career")):
        raw = enriched.get(group)
        if isinstance(raw, list) and raw:
            recs = [
                Recommendation(
                    title=str(item.get("title", "")).strip(),
                    kind=kind,  # type: ignore[arg-type]
                    reason=str(item.get("reason", "")),
                )
                for item in raw
                if isinstance(item, dict) and item.get("title")
            ]
            if recs:
                setattr(bundle, group if group != "events" else "events", recs)
    return bundle
