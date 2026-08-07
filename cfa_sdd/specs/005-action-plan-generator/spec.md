# Feature Specification: Personalized Action-Plan Generator

**Feature Branch**: `005-action-plan-generator`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Generate a structured, candidate-specific 90-day transition plan broken into months 1, 2 and 3, covering exams, work-experience documentation, references and the membership application, where the candidate can mark actions complete and regenerate the plan from what remains."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate receives a 90-day plan tailored to their gaps (Priority: P1)

After seeing their readiness score and missing requirements, the candidate asks for a plan and
receives a concrete set of actions organized into month 1, month 2 and month 3, each addressing one
of their actual gaps.

**Why this priority**: The action plan is the deliverable that converts assessment into execution and
is the fourth named POC capability.

**Independent Test**: Generate a plan for the advanced-candidate profile and confirm it contains
actions in all three months, each traceable to a gap identified by the readiness assessment.

**Acceptance Scenarios**:

1. **Given** an assessed candidate, **When** a plan is generated, **Then** it contains at least one
   action in each of months 1, 2 and 3.
2. **Given** a candidate with an exam gap, **When** a plan is generated, **Then** it includes a study
   and exam-preparation action scheduled before the exam-related milestones.
3. **Given** a candidate missing references, **When** a plan is generated, **Then** it includes
   identifying referees and requesting references, in that order.
4. **Given** any generated plan, **When** the actions are inspected, **Then** every action has a title,
   a description, a target month, a category and a priority.
5. **Given** two profiles at different stages, **When** plans are generated, **Then** the plans differ
   in content, not only in ordering.

---

### User Story 2 - Candidate works the plan and marks actions complete (Priority: P1)

The candidate ticks off actions as they finish them, and the completion state survives navigating
away and coming back.

**Why this priority**: Without persistence the plan is a static document; tracking progress is what
makes it a tool.

**Independent Test**: Mark several actions complete, reload the application, and confirm the same
actions are still marked complete.

**Acceptance Scenarios**:

1. **Given** a generated plan, **When** an action is marked complete, **Then** its state is persisted
   and reflected immediately.
2. **Given** a completed action, **When** it is unmarked, **Then** it returns to outstanding and the
   change is persisted.
3. **Given** completed actions, **When** the plan is reopened later, **Then** the same actions are
   still marked complete.
4. **Given** a plan with some actions complete, **When** progress is displayed, **Then** it shows the
   count and share of completed actions.

---

### User Story 3 - Candidate regenerates the plan from what is left (Priority: P2)

Having completed part of the plan, or having had their situation change, the candidate regenerates
it and receives an updated plan that respects what they have already done rather than starting from
scratch.

**Why this priority**: Keeps the plan alive over the 90 days; the plan is still valuable on first
generation without it.

**Independent Test**: Complete several actions, regenerate, and confirm the completed actions remain
marked complete and the new plan does not re-ask for finished work.

**Acceptance Scenarios**:

1. **Given** a plan with completed actions, **When** the plan is regenerated, **Then** the previously
   completed actions remain marked complete.
2. **Given** a plan with completed actions, **When** the plan is regenerated, **Then** actions that
   duplicate completed work are not reintroduced as outstanding.
3. **Given** a regenerated plan, **When** its history is inspected, **Then** the relationship between
   the new plan and the run and plan it superseded is recorded and auditable.
4. **Given** a plain re-run of the workflow that is not an explicit regeneration, **When** the plan is
   displayed, **Then** the user is not silently shown a plan with their completion state discarded.

---

### User Story 4 - Plan reflects the person's lifecycle stage (Priority: P3)

A member does not receive a candidate transition plan; they receive maintenance-oriented actions such
as professional learning and society engagement.

**Why this priority**: Consistency with the lifecycle-aware experience; low volume of affected users
in the demo.

**Independent Test**: Generate a plan for the member profile and confirm it contains no
membership-application actions.

**Acceptance Scenarios**:

1. **Given** a member profile, **When** a plan is generated, **Then** it contains no exam-registration
   or membership-application actions.
2. **Given** a member profile, **When** a plan is generated, **Then** it contains professional-learning
   and engagement actions.

---

### Edge Cases

- A fully ready candidate with no gaps: the plan is short and focuses on submitting and following
  through on the application rather than being empty.
- A very early candidate with many gaps: the plan is capped at a reviewable number of actions per
  month, prioritized by impact, rather than listing everything.
- All actions are marked complete: progress shows 100% and regeneration produces a maintenance plan
  or an explicit "nothing outstanding" state.
- An action identifier is toggled that does not belong to the current plan: the request is rejected
  without altering the plan.
- The same action is toggled twice in rapid succession: the final state is deterministic and matches
  the last request.
- Regeneration is requested while a previous generation is still running: the result is a single
  coherent plan, not two interleaved ones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a plan covering 90 days, partitioned into month 1, month 2 and
  month 3.
- **FR-002**: Every action MUST have a stable identifier, title, description, target month, category
  and priority.
- **FR-003**: Every action MUST be traceable to a gap or requirement identified by the readiness
  assessment, or to a maintenance objective for members.
- **FR-004**: System MUST order actions so that prerequisites precede dependent actions.
- **FR-005**: System MUST limit the number of actions per month to a reviewable maximum, prioritizing
  by impact when there are more gaps than slots.
- **FR-006**: Users MUST be able to mark any action complete or outstanding, and the state MUST persist
  across sessions.
- **FR-007**: System MUST report plan progress as the number and share of completed actions.
- **FR-008**: Users MUST be able to regenerate the plan, and regeneration MUST preserve previously
  completed actions and MUST NOT reintroduce completed work as outstanding.
- **FR-009**: System MUST record the lineage between a regenerated plan and the plan it supersedes, so
  a reviewer can follow the sequence.
- **FR-010**: System MUST NOT silently discard completion state when the workflow is re-run for other
  reasons; either the state carries forward or the user is told the plan is new.
- **FR-011**: System MUST generate lifecycle-appropriate plans, excluding candidate-only actions for
  members.
- **FR-012**: System MUST produce a usable plan with no language-model credential configured, using
  deterministic action templates personalized with the candidate's data.
- **FR-013**: System MUST persist the plan and its actions against the run that produced them.
- **FR-014**: System MUST make plan generation callable as an independently addressable specialist
  agent.
- **FR-015**: System MUST reject toggle requests for unknown actions with an actionable error.

### Key Entities

- **Action Plan**: The 90-day plan for one run — owning run, candidate, generation time, summary,
  superseded plan reference and its actions.
- **Action Item**: A single action — identifier, title, description, target month, category, priority,
  completion state, and the requirement or gap it addresses.
- **Plan Progress**: The derived completion count and share for a plan.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every synthetic candidate profile, the generated plan contains at least one action
  in each of the three months and every action maps to a real gap.
- **SC-002**: 100% of unmet requirements from the readiness assessment are addressed by at least one
  planned action.
- **SC-003**: Completion state survives a full application reload for 100% of toggled actions.
- **SC-004**: After regeneration, previously completed actions remain complete 100% of the time and no
  completed work reappears as outstanding.
- **SC-005**: A reviewer can trace any displayed plan back to its run and to the plan it superseded.
- **SC-006**: Plans generate successfully for all profiles with no language-model credential configured.

## Assumptions

- The 90-day window starts on the day the plan is generated; calendar scheduling and reminders are out
  of scope.
- Actions are advisory; the POC does not perform any action on the candidate's behalf, and no action
  submits anything to CFA Institute.
- A reviewable maximum of actions per month is a documented, configurable constant.
- Depends on feature 001 for orchestration, agent addressing, persistence and audit, and on feature 003
  for the gaps that drive the plan.
