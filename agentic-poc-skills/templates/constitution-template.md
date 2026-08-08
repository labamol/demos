# <PROJECT NAME> Constitution

<!--
  A reusable constitution for an auditable agentic POC, extracted from the CFA
  Candidate-to-Member onboarding POC (see ../../cfa_sdd/.specify/memory/constitution.md
  for a filled-in example).

  Principles I–V are domain-neutral: adopt them close to verbatim. The Technology
  Constraints section is the part you must rewrite for your stack.

  Delete every instruction comment before shipping. Copy the result to
  .specify/memory/constitution.md in your Spec Kit workspace.
-->

This constitution governs every feature delivered in this project. It is the highest authority:
plans, tasks and implementations that conflict with it must be changed or explicitly justified in
the Complexity Tracking section of the owning plan.

## Core Principles

### I. Agentic-First Orchestration (NON-NEGOTIABLE)

Every user-facing capability is delivered as a node in a single orchestrated workflow, never as
ad-hoc controller code. Each node owns one responsibility, reads and writes only the shared typed
workflow state, and is independently runnable against a fixture. Cross-agent work is delegated
through the agent protocol and tool/file access through the tool-server protocol; direct in-process
calls are permitted only as an explicitly audited fallback when the transport fails. Every node
records start/completion/failure events and a state checkpoint.

### II. Deterministic Rules, AI Narration

Any number a user can act on — scores, estimates, percentages, gaps — is produced by transparent,
unit-tested deterministic rules with published weights and thresholds. The LLM may only interpret,
explain, prioritize and phrase those results. An LLM response is never the source of a score, a gate
decision, or an authoritative determination. Every AI-facing surface in an advisory domain carries a
guidance-only disclaimer.

### III. Typed Contracts End to End

Typed models are the single definition of every domain object and every API request/response. No
untyped dicts cross a module boundary, and dynamic attribute access and unvalidated parsing are
prohibited in application code. The client consumes types mirroring those models; a contract change
is a spec change and must be reflected in the feature's `contracts/` directory before implementation.

### IV. Auditability and Reproducibility

Every workflow run is reproducible from the datastore alone. A run persists: the run row, an ordered
state checkpoint per node, every agent audit event (agent, node, status, duration, payload, transport
actually used), every LLM call (including calls skipped because no credential is configured), and all
generated artifacts. Audit writes must never break a run: if persistence is unavailable, events are
buffered and the degradation itself is recorded. Audit data is queryable by run and by subject, and is
surfaced in the UI.

### V. Offline-Capable, Synthetic-Only

The system must run end to end with no LLM credential configured, using deterministic fallback
narration, and each skipped call must appear in the audit log with an explicit skipped status. All data
shipped in the repository is synthetic; real user data, real credentials and real production systems are
out of scope. Secrets live only in the environment file (never committed); an example file documents
every variable with empty or placeholder values.

## Technology Constraints

<!--
  REWRITE THIS SECTION. This is the only part that is genuinely project-specific.
  Be specific enough that an agent cannot silently substitute a component.
-->

The stack is fixed and may not be substituted without an amendment:

- **Backend**: <language, framework, validation library, ORM>.
- **Agentic workflow**: <orchestration library — a single compiled graph>.
- **Agent-to-agent**: <protocol, discovery endpoint convention>.
- **Tooling/files**: <tool-server protocol and transport, plus any stdio hygiene rule>.
- **LLM**: <provider and client, model configured through the environment file, optional at runtime>.
- **Storage**: <file storage for fixtures; database for runs, state, audit and artifacts, created by a
  checked-in DDL script>.
- **Frontend**: <framework, language, bundler>.
- **Deployment configuration is limited to exactly these mechanisms**: <list them>. No other
  configuration, packaging or orchestration files.

## Development Workflow

- Work is spec-driven: `/speckit-constitution` -> `/speckit-specify` -> `/speckit-clarify` ->
  `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` -> `/speckit-implement`. No implementation
  starts before its feature has an approved `spec.md`, `plan.md` and `tasks.md`.
- The platform-foundation feature is a prerequisite for all others; capability features are
  independently shippable slices on top of it.
- Specs stay implementation-free: they describe user value, requirements and measurable outcomes.
  Technology decisions belong in `plan.md`.
- Unresolved ambiguity is marked `[NEEDS CLARIFICATION: ...]` and must be resolved before
  `/speckit-plan` completes.
- Quality gates for every change: <lint>, <format check>, <frontend build/type-check>, the DDL applies
  cleanly to an empty database, and a full workflow run succeeds for each fixture both with and without
  an LLM credential.
- Schema changes ship as additive DDL in the same change as the code that needs them.

## Governance

This constitution supersedes team habits and tool defaults. Amendments require a pull request that
states the motivation, updates this file, bumps the version below, and updates any spec, plan or skill
the change invalidates. Every pull request review must confirm compliance with the five core principles;
deviations must be recorded in the plan's Complexity Tracking table with a justification and a simpler
alternative that was rejected.

**Version**: 1.0.0 | **Ratified**: <YYYY-MM-DD> | **Last Amended**: <YYYY-MM-DD>
