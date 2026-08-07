# CFA Candidate-to-Member Onboarding POC Constitution

This constitution governs every feature delivered inside `cfa_sdd/`. It is the highest
authority for the Candidate-to-Member Onboarding proof of concept: plans, tasks and
implementations that conflict with it must be changed or explicitly justified in the
Complexity Tracking section of the owning plan.

## Core Principles

### I. Agentic-First Orchestration (NON-NEGOTIABLE)

Every user-facing capability is delivered as a node in a single LangGraph workflow, never as
ad-hoc controller code. Each node owns one responsibility, reads and writes only the shared
typed workflow state, and is independently runnable against a mock profile. Cross-agent work
is delegated through the Google A2A JSON-RPC protocol and file access flows through MCP;
direct in-process calls are permitted only as an explicitly audited fallback when the
transport fails. Every node records a `node_started` / `node_completed` / `node_failed`
audit event and a state checkpoint.

### II. Deterministic Rules, AI Narration

Any number a candidate can act on — readiness score, qualifying months, percentage complete,
eligibility gaps — is produced by transparent, unit-tested deterministic rules with published
weights and thresholds. The LLM may only interpret, explain, prioritize and phrase those
results. An LLM response is never the source of a score, a gate decision, or an eligibility
determination. Every AI-facing surface carries a guidance-only disclaimer: the POC never
issues an official CFA Institute eligibility decision.

### III. Typed Contracts End to End

Pydantic v2 models are the single definition of every domain object and every API
request/response. No untyped dicts cross a module boundary, and `Any`, `getattr`-style
dynamic attribute access, and unvalidated JSON parsing are prohibited in application code.
The React client consumes TypeScript types that mirror those models; a contract change is a
spec change and must be reflected in the feature's `contracts/` directory before implementation.

### IV. Auditability and Reproducibility

Every workflow run is reproducible from the database alone. A run persists: the run row, an
ordered state checkpoint per node, every agent audit event (agent, node, status, duration,
payload, transport actually used), every LLM call (including calls skipped because no API key
is configured), and all generated artifacts (readiness, evaluation, plan, action items,
recommendations). Audit writes must never break a run: if persistence is unavailable, events
are buffered and the degradation itself is recorded. Audit data is queryable by `run_id` and
by `candidate_id`, and is surfaced in the UI.

### V. Offline-Capable, Synthetic-Only

The system must run end to end with an empty `OPENAI_API_KEY`, using deterministic fallback
narration, and each skipped LLM call must appear in the audit log with `status="skipped"`.
All data shipped in the repository is synthetic; real candidate data, real credentials and
real CFA Institute systems are out of scope. Secrets live only in `.env` (never committed);
`.env.example` documents every variable with empty or placeholder values.

## Technology Constraints

The stack is fixed and may not be substituted without an amendment:

- **Backend**: Python 3.10+, FastAPI, Pydantic v2 + pydantic-settings, SQLAlchemy.
- **Agentic workflow**: LangGraph (single compiled graph), LangChain Core.
- **Agent-to-agent**: Google A2A — agent cards at `/a2a/{agent}/.well-known/agent.json`,
  JSON-RPC 2.0 `message/send`.
- **Tooling/files**: MCP server over stdio for all local-directory file access. MCP logs go to
  stderr only — stdout is reserved for JSON-RPC framing.
- **LLM**: OpenAI via `langchain-openai`, model configured through `.env`, optional at runtime.
- **Storage**: local directory storage for mock profiles and documents; PostgreSQL for runs,
  state, audit and artifacts, created by a checked-in DDL script.
- **Frontend**: React 18 + TypeScript + Vite.
- **Deployment configuration is limited to exactly three mechanisms**: `requirements.txt` for
  all pip installs, a `.env` file for configuration, and a JSON config file for MCP. No
  Docker, Compose, Poetry, Pipenv, Helm, Terraform or additional orchestration files.

## Development Workflow

- Work is spec-driven: `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` →
  `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`. No
  implementation starts before its feature has an approved `spec.md`, `plan.md` and `tasks.md`.
- Feature 001 (Agentic Platform Foundation) is a prerequisite for all others; features 002–007
  are independently shippable slices on top of it.
- Specs stay implementation-free: they describe user value, requirements and measurable
  outcomes. Technology decisions belong in `plan.md`.
- Unresolved ambiguity is marked `[NEEDS CLARIFICATION: ...]` and must be resolved before
  `/speckit-plan` completes.
- Quality gates for every change: `ruff check` and `black --check` on backend code,
  `npm run build` (TypeScript strict) on the frontend, the DDL applies cleanly to an empty
  database, and a full workflow run succeeds for each mock persona both with and without an
  OpenAI key.
- Schema changes ship as additive DDL in the same change as the code that needs them.

## Governance

This constitution supersedes team habits and tool defaults. Amendments require a pull request
that states the motivation, updates this file, bumps the version below, and updates any spec,
plan or skill that the change invalidates. Every pull request review must confirm compliance
with the five core principles; deviations must be recorded in the plan's Complexity Tracking
table with a justification and a simpler alternative that was rejected. Use
`.github/skills/` for runtime agent guidance and `cfa_sdd/README.md` for execution instructions.

**Version**: 1.0.0 | **Ratified**: 2026-08-07 | **Last Amended**: 2026-08-07
