# Feature Specification: Agentic Platform Foundation

**Feature Branch**: `001-agentic-platform-foundation`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Agentic platform foundation for the CFA Candidate-to-Member Onboarding POC: a single orchestrated agent workflow that loads a selected synthetic candidate profile from local directory storage, delegates specialist work to independent agents, persists an auditable record of every run, and exposes the result to a web client."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select a synthetic profile and run the journey (Priority: P1)

A demo user opens the web application, sees the list of synthetic candidate profiles available
in the workspace, picks one, and starts a run. The system loads that profile, executes the
orchestrated agent workflow end to end, and returns a single consolidated result the UI can
render.

**Why this priority**: Nothing else in the POC is demonstrable without profile selection and a
completed run. This is the minimum viable slice.

**Independent Test**: Start the app with only this feature implemented, select each of the four
synthetic profiles, and confirm a run completes and returns a result identifying the candidate,
their lifecycle stage and the ordered list of workflow steps executed.

**Acceptance Scenarios**:

1. **Given** the workspace contains synthetic profile files, **When** the user opens the app,
   **Then** every profile is listed with candidate name, identifier and lifecycle stage.
2. **Given** a profile is selected, **When** the user starts a run, **Then** a run identifier is
   returned and the result contains the loaded candidate data.
3. **Given** a profile file is malformed or missing, **When** the user starts a run, **Then** the
   run fails with a clear message naming the file and the run failure is recorded.

---

### User Story 2 - Reproduce and inspect any run from the audit trail (Priority: P1)

An analyst reviewing the demo needs to see exactly what the system did: which steps ran, which
agent handled each step, how long each took, which transport was used, whether the language
model was called or skipped, and what the state looked like after each step.

**Why this priority**: Auditability of agent execution and workflow state is an explicit
requirement of the POC and a constitutional principle; it must exist from the first slice, not
be retrofitted.

**Independent Test**: Execute a run, then query the audit trail by run identifier and confirm a
complete ordered event sequence plus one state checkpoint per step, and that the same is visible
in the UI.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** the audit trail is queried by run identifier, **Then** it
   contains a start and completion event for every workflow step, in execution order, each with a
   duration.
2. **Given** a completed run, **When** the stored state checkpoints are listed, **Then** there is
   one checkpoint per executed step with a monotonically increasing sequence number.
3. **Given** a step delegated work to a specialist agent, **When** its events are inspected,
   **Then** the record names the agent and the transport actually used, including whether a
   fallback transport was substituted.
4. **Given** the record store is unavailable, **When** a run executes, **Then** the run still
   completes, events are buffered and returned to the caller, and the degradation is recorded.

---

### User Story 3 - Run the whole demo without external AI access (Priority: P2)

A presenter must be able to run the demo on a laptop with no language-model credentials
configured and still get a complete, sensible result.

**Why this priority**: The POC is demonstrated in environments without outbound AI access;
deterministic behaviour also makes the demo repeatable.

**Independent Test**: Clear the language-model credential, run every profile, and confirm all
runs complete with deterministic narration and that skipped model calls appear in the audit trail.

**Acceptance Scenarios**:

1. **Given** no language-model credential is configured, **When** a run executes, **Then** the run
   completes successfully using deterministic fallback narration.
2. **Given** no credential is configured, **When** the audit trail is inspected, **Then** each
   attempted model call appears with status `skipped`.
3. **Given** a credential is configured, **When** a run executes, **Then** model calls are recorded
   with the model name, duration and token usage.

---

### User Story 4 - Specialist agents are independently addressable (Priority: P3)

An integrator wants to discover the specialist agents the platform exposes and call one directly,
without going through the full workflow.

**Why this priority**: Demonstrates genuine agent-to-agent interoperability rather than internal
function calls, but the demo works without it.

**Independent Test**: Retrieve the list of published agents and their capability descriptions, then
invoke one directly with a payload and receive a structured response.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** the agent catalogue is requested, **Then** each
   specialist agent is listed with a machine-readable capability description.
2. **Given** an agent identifier, **When** a well-formed request is sent to it, **Then** a structured
   result is returned and the call is audited.
3. **Given** a malformed request, **When** it is sent to an agent, **Then** a protocol-conformant
   error is returned and no partial artifact is persisted.

---

### Edge Cases

- Two runs are started for the same profile concurrently: each must receive a distinct run
  identifier and independent audit trail with no interleaved state checkpoints.
- The file-access service fails to start: the run must fall back to reading local storage directly,
  complete, and record that the fallback was used.
- A specialist agent is unreachable over its network transport: the platform must fall back to
  local execution and record the substituted transport.
- A profile references a supporting document that does not exist: the run completes and the missing
  document is reported as missing evidence rather than raising an error.
- A step raises an unexpected error: the run is marked failed, a failure event is recorded with the
  step name, and prior checkpoints remain queryable.
- Attempted access to a file outside the configured storage directory must be rejected.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST discover and list every synthetic candidate profile in the configured
  local storage directory, exposing candidate name, identifier, lifecycle stage and file name.
- **FR-002**: System MUST read profile and supporting-document files exclusively through the
  file-access tool service, and MUST reject any path that resolves outside the configured directory.
- **FR-003**: System MUST execute a single orchestrated workflow whose steps run in a defined order:
  load profile → assess readiness → evaluate work experience → build action plan → generate
  recommendations → assemble dashboard → optionally answer a user question.
- **FR-004**: System MUST assign every run a unique identifier returned to the caller.
- **FR-005**: System MUST persist a run record, one ordered state checkpoint per executed step, and
  a start/completion (or failure) event per step, each with a duration.
- **FR-006**: System MUST record, for each delegated call, the target agent and the transport
  actually used, distinguishing the primary transport from any fallback.
- **FR-007**: System MUST record every language-model interaction, including interactions skipped
  because no credential is configured, with an explicit status.
- **FR-008**: System MUST complete runs successfully when no language-model credential is configured,
  substituting deterministic narration.
- **FR-009**: System MUST continue a run when the record store is unavailable, buffering audit events
  and recording the degradation.
- **FR-010**: System MUST publish a discoverable catalogue of specialist agents with machine-readable
  capability descriptions, and MUST accept direct, protocol-conformant requests to each.
- **FR-011**: System MUST expose an interface for the web client to list profiles, start a run,
  retrieve a run by identifier, list recent runs, and query the audit trail.
- **FR-012**: System MUST validate every inbound and outbound payload against a declared schema and
  reject non-conforming payloads with an actionable error.
- **FR-013**: System MUST provide a database definition script that creates all persistence
  structures from empty, and MUST be runnable against a freshly created empty database.
- **FR-014**: System MUST report, at startup, whether the record store, language model and file-access
  service are reachable and configured.
- **FR-015**: Users MUST be able to view the audit trail for the most recent run from the web client.

### Key Entities

- **Candidate Profile**: A synthetic person progressing through the CFA journey — identity, lifecycle
  stage, exam history, work experience entries, references, membership requirements and supporting
  document links.
- **Workflow Run**: One execution of the orchestrated workflow for one profile — identifier, selected
  profile, status, start and end time, and optional user question.
- **State Checkpoint**: The workflow state captured after a step, with the run identifier, step name
  and sequence number.
- **Audit Event**: One recorded occurrence during a run — event type, step, agent, status, message,
  structured payload, duration and timestamp.
- **Agent Capability Description**: A published, machine-readable description of a specialist agent —
  identifier, name, description and the skills it offers.
- **Run Artifact**: A structured output produced by a step (readiness result, experience evaluation,
  action plan, recommendation set, dashboard) linked to its run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A demo user can go from opening the application to a completed run for any synthetic
  profile in under 30 seconds without reading documentation.
- **SC-002**: 100% of executed workflow steps produce both a state checkpoint and a matched
  start/completion or failure event.
- **SC-003**: Every artifact shown in the UI can be traced back to a run identifier and its
  originating step using only stored records.
- **SC-004**: All synthetic profiles complete a run successfully both with and without a
  language-model credential configured.
- **SC-005**: The database definition script applies cleanly to an empty database, and re-applying it
  produces no errors.
- **SC-006**: A reviewer can determine, from stored records alone, whether each delegated call used
  its primary transport or a fallback, for 100% of delegated calls.

## Assumptions

- Only synthetic data is used; there is no integration with real CFA Institute systems, and no
  authentication or authorization is required for the POC.
- A single user drives the demo at a time; multi-tenant isolation and horizontal scaling are out of
  scope.
- The database, file storage and application all run on the same machine.
- Profile files are hand-authored JSON documents conforming to `data/profile.schema.json`, and the
  four profiles in `data/mock/applications/` are supplied with this package rather than authored
  during implementation.
- Deployment configuration is limited to a dependency manifest, an environment file and a JSON
  configuration file for the file-access service, per the constitution.
- Features 002–007 depend on this feature and are built on top of it.
