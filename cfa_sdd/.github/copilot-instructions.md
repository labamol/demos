# Copilot Instructions — CFA Candidate-to-Member Onboarding POC (`cfa_sdd/`)

You are working in a **spec-driven** project. Read this file before any task in this folder.

## Ground rules

1. **The constitution wins.** `.specify/memory/constitution.md` is the highest authority. If a request
   conflicts with it, say so and propose either a compliant alternative or a constitution amendment.
2. **No implementation without a spec.** Work flows through the Spec Kit skills in order:
   `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` →
   `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`. Do not write feature code before the
   owning feature has an approved `spec.md`, `plan.md` and `tasks.md` in `specs/`.
3. **`data/` is specification, not sample data.** The four synthetic profiles and their expected
   readiness scores are what the acceptance criteria are written against. Every profile must validate
   against `data/profile.schema.json`. Do not edit, replace or "improve" a fixture to make an
   implementation pass — fix the implementation.
4. **Feature 001 first.** `001-agentic-platform-foundation` is a prerequisite for features 002–007.

## Feature map

| Feature | Capability |
| --- | --- |
| `001-agentic-platform-foundation` | LangGraph orchestration, MCP file access, A2A agents, Postgres audit, API shell |
| `002-lifecycle-dashboard` | Lifecycle-aware dashboard |
| `003-membership-readiness-assessment` | Readiness score, breakdown, missing requirements |
| `004-work-experience-evaluator` | Qualifying-experience evaluation |
| `005-action-plan-generator` | Personalized 90-day plan |
| `006-candidate-qa-assistant` | Grounded Q&A on exams, experience, membership |
| `007-recommendations-and-member-transition` | Recommendations, reference tracking, member transition |

## Stack skills — invoke these, don't improvise

Before writing code in an area, load the matching skill from `.github/skills/`:

| Area | Skill |
| --- | --- |
| Workflow nodes, graph wiring, state | `cfa-langgraph-workflow` |
| Specialist agents, agent cards, JSON-RPC | `cfa-a2a-agents` |
| Profile/document file access | `cfa-mcp-file-access` |
| Data contracts | `cfa-pydantic-models` |
| Persistence, audit trail, DDL | `cfa-postgres-audit` |
| Any LLM call | `cfa-openai-llm` |
| HTTP routes, settings | `cfa-fastapi-backend` |
| React client | `cfa-react-ui` |
| Dependencies and config files | `cfa-deployment-config` |
| Domain semantics, constants, personas | `cfa-poc-domain` |

## Reflexes

- Any candidate-facing number comes from deterministic rules. The LLM narrates; it never decides.
- Every workflow node emits start/complete/fail audit events and one state checkpoint.
- Every eligibility-related surface carries the guidance-only disclaimer.
- Everything must work with `OPENAI_API_KEY` empty; skipped LLM calls are audited.
- Deployment config is limited to `requirements.txt`, `.env` and `mcp.config.json` — nothing else.
- MCP server processes never write to stdout.
- Synthetic data only; secrets only in `.env`, which is never committed.

## Quality gates before you report done

- `ruff check` and `black --check` pass on backend code.
- `npm run build` passes (TypeScript strict).
- `db/ddl.sql` applies cleanly to an empty database and re-applies without error.
- A full workflow run succeeds for every synthetic persona, both with and without an OpenAI key.
