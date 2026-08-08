# CFA Candidate-to-Member Onboarding — Spec-Driven Development Package

A ready-to-execute [GitHub Spec Kit](https://github.com/github/spec-kit) workspace for the
**Candidate-to-Member Onboarding** POC. It contains the project constitution, seven feature
specifications covering the POC capability list, the Spec Kit skills for GitHub Copilot agents, and
stack-specific agent skills for the target technology stack.

This folder is **self-contained**: everything needed to go from specification to a working POC is
here. It contains no application code — the dev team runs the Spec Kit commands to plan, task and
implement each feature — but it does ship the synthetic fixtures and the input contract those
specifications are written against.

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
├── data/
│   ├── profile.schema.json              # Input contract for a candidate/member profile
│   └── mock/
│       ├── README.md                    # The four personas + how their scores are derived
│       ├── applications/*.json          # Synthetic profiles, selectable from the UI
│       └── documents/<candidate_id>/    # Supporting documents, read over MCP
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

## The fixtures are part of the specification

`data/` is not sample data to be replaced — the acceptance scenarios and `SC-` success criteria in
`specs/` are written against these four personas, and the implementation must reproduce their
expected readiness scores exactly:

| Persona | Stage | Expected readiness |
| --- | --- | --- |
| Rohan Patel — early candidate, non-qualifying experience | candidate | 15% |
| Arjun Mehta — advanced candidate | candidate | 42% |
| Aisha Khan — eligible but application not started | candidate | 70% |
| Neha Sharma — existing member | member | 100% |

Each score is reproducible by hand from the weights published in the `cfa-poc-domain` skill; the
derivation is worked through in `data/mock/README.md`. Every profile must validate against
`data/profile.schema.json`, which is the input contract for the entire workflow.

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

To run the Spec Kit commands:

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- Git
- GitHub Copilot (agent mode) in VS Code, or any agent that reads `.github/skills/`

The Specify CLI is only needed to re-scaffold or upgrade the workspace — the package is already
initialized:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.16.0
specify check
```

### Environment for the implementation

The stack the constitution fixes needs the following available before `/speckit-implement` on
feature 001 can produce a runnable system:

| Component | Version | Notes |
| --- | --- | --- |
| Python | 3.11+ | One virtualenv at the project root. The MCP server must be spawned with `sys.executable` so the child process shares it. |
| PostgreSQL | 14+ | Running locally and reachable over TCP. |
| Node.js | 18+ | With npm, for the React client. |
| OpenAI API key | — | **Optional.** The system must run end to end without one (Principle V). |

Create the database before the first run — the DDL script written in feature 001 assumes the
database and role already exist:

```bash
sudo -u postgres psql -c "CREATE USER onboarding WITH PASSWORD 'onboarding';"
sudo -u postgres psql -c "CREATE DATABASE onboarding OWNER onboarding;"
```

The resulting connection string, the path to `data/mock`, and the optional API key all belong in
`.env` (documented in a committed `.env.example`) — never in code. See the `cfa-deployment-config`
skill for the configuration constraint this must respect.

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
