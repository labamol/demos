"""Google A2A agent cards for the remote agents in this POC."""

from __future__ import annotations

from typing import Any

from backend.app.core.config import get_settings

A2A_VERSION = "0.2.0"


def _card(name: str, description: str, skills: list[dict[str, Any]]) -> dict[str, Any]:
    base = get_settings().a2a_base_url.rstrip("/")
    return {
        "name": name,
        "description": description,
        "url": f"{base}/a2a/{name}",
        "version": "1.0.0",
        "protocolVersion": A2A_VERSION,
        "provider": {"organization": "CFA Candidate-to-Member POC"},
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": skills,
    }


AGENT_CARDS: dict[str, dict[str, Any]] = {
    "work-experience-evaluator": _card(
        "work-experience-evaluator",
        "Evaluates candidate work experience against the CFA qualifying-experience rubric "
        "and returns likely qualifying activities, missing evidence and a confidence score.",
        [
            {
                "id": "evaluate_experience",
                "name": "Evaluate work experience",
                "description": (
                    "Assess a candidate's employment history for qualifying experience."
                ),
                "tags": ["membership", "eligibility", "guidance"],
                "examples": ["Do my 30 months as an equity research associate qualify?"],
            }
        ],
    ),
    "action-plan-generator": _card(
        "action-plan-generator",
        "Generates a personalized 90-day candidate-to-member transition plan.",
        [
            {
                "id": "generate_plan",
                "name": "Generate transition plan",
                "description": (
                    "Produce a three-month plan from readiness and experience inputs."
                ),
                "tags": ["planning", "membership"],
                "examples": ["What should I do over the next 90 days?"],
            }
        ],
    ),
    "recommendation-agent": _card(
        "recommendation-agent",
        "Recommends learning modules, society events and career activities for the user's stage.",
        [
            {
                "id": "recommend",
                "name": "Recommend activities",
                "description": "Return learning, event and career recommendations.",
                "tags": ["learning", "events", "career"],
                "examples": ["What should I learn next?"],
            }
        ],
    ),
}
