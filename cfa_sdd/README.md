# CFA Candidate-to-Member Onboarding — Spec-Driven Development Package

A ready-to-execute [GitHub Spec Kit](https://github.com/github/spec-kit) workspace for the
**Candidate-to-Member Onboarding** POC. It contains the project constitution, seven feature
specifications covering the POC capability list, the Spec Kit skills for GitHub Copilot agents, and
stack-specific agent skills for the target technology stack.

This folder is **specification and process only** — it contains no application code. The dev team
runs the Spec Kit commands here to plan, task and implement each feature.

> The sibling folder `../cfa-candidate-onboarding/` is a working reference implementation of the same
> POC. Treat it as a read-only exemplar. Nothing in this package modifies it.
>
> Starting a POC in a *different* domain on the same stack? Use `../agentic-poc-skills/`, the
> domain-neutral extraction of this package's skills and constitution.

## What's in here

```
cfa_sdd/
├── .github/
│   ├── copilot-instructions.md          # Always-on guidance for Copilot agents
│   └── skills/
│       ├── speckit-*/SKILL.md           # Spec Kit workflow skills (constitution, specify, plan, …)
│       └── cfa-*/SKILL.md               # Stack + domain skills for this POC
├── .specify/
│   ├── memory/constitution.md           # Project constitution (v1.0.0) — highest authority
│   ├── templates/                       # spec / plan / tasks / checklist templates
│   ├── scripts/bash/                    # Feature scaffolding + prerequisite scripts
│   └── workflows/                       # Spec Kit workflow definition
├── specs/
│   ├── 001-agentic-platform-foundation/spec.md
│   ├── 002-lifecycle-dashboard/spec.md
│   ├── 003-membership-readiness-assessment/spec.md
│   ├── 004-work-experience-evaluator/spec.md
│   ├── 005-action-plan-generator/spec.md
│   ├── 006-candidate-qa-assistant/spec.md
│   └── 007-recommendations-and-member-transition/spec.md
└── README.md
```

## The constitution

`.specify/memory/constitution.md` (v1.0.0) encodes the same principles the POC was built on:

| Principle | Summary |
| --- | --- |
| I. Agentic-First Orchestration | One LangGraph workflow; MCP for files, A2A for agents; every node audited and checkpointed |
| II. Deterministic Rules, AI Narration | Every actionable number comes from transparent rules; the LLM only explains |
| III. Typed Contracts End to End | Pydantic v2 is the single source of truth; mirrored TypeScript types |
| IV. Auditability and Reproducibility | Every run reconstructable from the database alone |
| V. Offline-Capable, Synthetic-Only | Works with no `OPENAI_API_KEY`; synthetic data; secrets only in `.env` |

It also fixes the technology stack and restricts deployment configuration to exactly
`requirements.txt`, `.env` and `mcp.config.json`.

## The features

| # | Feature | POC capability |
| --- | --- | --- |
| 001 | Agentic Platform Foundation | Orchestration, MCP, A2A, audit, persistence, API shell — **prerequisite for all others** |
| 002 | Lifecycle-Aware Dashboard | POC capability 1 |
| 003 | Membership Readiness Assessment | POC capability 2 |
| 004 | Work-Experience Evaluator | POC capability 3 |
| 005 | Personalized Action-Plan Generator | POC capability 4 |
| 006 | Candidate Q&A Assistant | Required user experience: ask about exams, experience, membership |
| 007 | Recommendations & Simulated Member Transition | Reference tracking, application checklist, approval timeline, member dashboard |

Each `spec.md` is implementation-free and contains prioritized user stories with independent tests,
acceptance scenarios, edge cases, numbered functional requirements, key entities, measurable success
criteria and explicit assumptions.

## Agent skills

Spec Kit workflow skills (installed by `specify init`):

`speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-plan`, `speckit-tasks`,
`speckit-analyze`, `speckit-checklist`, `speckit-implement`, `speckit-converge`,
`speckit-taskstoissues`.

Stack and domain skills added for this POC:

| Skill | Covers |
| --- | --- |
| `cfa-langgraph-workflow` | Graph wiring, node contract, shared state, checkpoints |
| `cfa-a2a-agents` | Agent cards, JSON-RPC `message/send`, audited transport fallback |
| `cfa-mcp-file-access` | MCP stdio server/client, path containment, stdout hygiene |
| `cfa-pydantic-models` | Pydantic v2 contracts and their TypeScript mirrors |
| `cfa-postgres-audit` | Runs, state checkpoints, audit events, idempotent DDL |
| `cfa-openai-llm` | Deterministic fallback, audited/skipped calls, the narration boundary |
| `cfa-fastapi-backend` | Route surface, error mapping, pydantic-settings configuration |
| `cfa-react-ui` | Panels, run lifecycle, loading/error/empty states, strict typing |
| `cfa-deployment-config` | The three-file deployment constraint and dependency pinning |
| `cfa-poc-domain` | Journey stages, requirement categories, scoring constants, personas |

## Prerequisites

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- Git
- GitHub Copilot (agent mode) in VS Code, or any agent that reads `.github/skills/`

Install the Specify CLI (only needed to re-scaffold or upgrade; the package is already initialized):

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.16.0
specify check
```

## How the dev team executes a feature

Open **`cfa_sdd/` as the workspace root** in VS Code (the Spec Kit scripts resolve the repo root from
`.specify/`, and Copilot picks up `.github/` from the workspace root). Then, for one feature at a
time, starting with 001:

```text
# 1. Point the session at the feature (both variables — the helper scripts
#    resolve the directory from SPECIFY_FEATURE_DIRECTORY or .specify/feature.json)
export SPECIFY_FEATURE=001-agentic-platform-foundation
export SPECIFY_FEATURE_DIRECTORY=specs/001-agentic-platform-foundation

# 2. (Optional but recommended) de-risk ambiguity in the spec
/speckit-clarify

# 3. Produce the technical plan and design artifacts
/speckit-plan Use Python 3.11 + FastAPI + Pydantic v2 + SQLAlchemy + PostgreSQL,
              LangGraph for the workflow, Google A2A for specialist agents,
              MCP over stdio for local file access, OpenAI via langchain-openai,
              React 18 + TypeScript + Vite for the UI. Deployment configuration is
              limited to requirements.txt, .env and mcp.config.json.

# 4. Generate the dependency-ordered task list
/speckit-tasks

# 5. Optional quality gates
/speckit-checklist
/speckit-analyze

# 6. Implement
/speckit-implement
```

Then repeat for `002` … `007`. To hand tasks to the team as tracked work instead of implementing
in-session, run `/speckit-taskstoissues` after `/speckit-tasks`.

To start additional features beyond these seven:

```bash
.specify/scripts/bash/create-new-feature.sh --short-name "my-feature" "Description of the feature"
```

To amend the constitution, run `/speckit-constitution` and bump the version at the bottom of the file.

## Recommended execution order

```
001 Agentic Platform Foundation      (blocks everything)
 ├─ 003 Membership Readiness Assessment
 │   ├─ 005 Personalized Action-Plan Generator
 │   ├─ 006 Candidate Q&A Assistant
 │   └─ 007 Recommendations & Member Transition   (also depends on 005)
 ├─ 004 Work-Experience Evaluator
 └─ 002 Lifecycle-Aware Dashboard     (consumes 003, 005, 007 — build last for a full dashboard)
```

## Definition of done for every feature

- `spec.md`, `plan.md` and `tasks.md` exist and `/speckit-analyze` reports no unresolved
  inconsistencies.
- No `[NEEDS CLARIFICATION]` markers remain.
- `ruff check` and `black --check` pass on backend code; `npm run build` passes on the frontend.
- `db/ddl.sql` applies cleanly to an empty database and re-applies without error.
- A full workflow run succeeds for every synthetic persona, both with and without `OPENAI_API_KEY`.
- Every constitutional principle is satisfied, or a deviation is justified in the plan's Complexity
  Tracking table.
