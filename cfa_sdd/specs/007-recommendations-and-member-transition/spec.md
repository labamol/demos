# Feature Specification: Recommendations & Simulated Member Transition

**Feature Branch**: `007-recommendations-and-member-transition`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Recommend learning, society events and career/volunteer opportunities matched to the person's stage and gaps; track references and application readiness with an expected approval timeline; and transition the experience into a simulated member dashboard once all requirements are complete."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate receives stage-appropriate recommendations (Priority: P1)

The candidate sees a short, ranked set of recommendations across three areas — learning, events and
society activity, and career or volunteer opportunities — each with a reason tied to their situation.

**Why this priority**: Learning, event and career recommendations are a required user experience of
the POC and the main engagement driver beyond compliance-style checklists.

**Independent Test**: Run two profiles at different stages and confirm each receives recommendations
in all three areas, with different content and a stated reason per item.

**Acceptance Scenarios**:

1. **Given** a Level III candidate, **When** recommendations are generated, **Then** learning items are
   oriented to Level III preparation and each states why it was suggested.
2. **Given** a candidate short on qualifying experience, **When** recommendations are generated, **Then**
   at least one career or volunteer item addresses gaining or evidencing qualifying experience.
3. **Given** any profile, **When** recommendations are generated, **Then** each area contains at least
   one item and no item appears twice.
4. **Given** no language-model credential is configured, **When** recommendations are generated, **Then**
   deterministic, stage-appropriate items are still returned.

---

### User Story 2 - Candidate tracks references and application readiness (Priority: P1)

The candidate sees each reference they need, who it is assigned to, its current status, and an overall
application-readiness checklist with an expected approval timeline.

**Why this priority**: Reference tracking, the application checklist and the expected approval timeline
are named transition opportunities in the POC scope.

**Independent Test**: For a profile with partial references, confirm each reference is listed with its
status, the checklist shows which items block submission, and an expected timeline is shown.

**Acceptance Scenarios**:

1. **Given** a candidate needing two references with one received, **When** the tracker is shown,
   **Then** it shows one received and one outstanding, with the outstanding one's status.
2. **Given** an application checklist, **When** it is shown, **Then** each item is marked satisfied,
   pending or outstanding and blocking items are visually distinct.
3. **Given** a candidate whose checklist is complete, **When** the timeline is shown, **Then** it gives an
   expected approval window with the stages it covers.
4. **Given** any timeline, **When** it is displayed, **Then** it is labelled as an estimate and carries a
   guidance-only disclaimer.

---

### User Story 3 - Candidate transitions into a simulated member experience (Priority: P2)

Once every membership requirement is complete, the person can move into a simulated member dashboard
showing member benefits, professional-learning tracking and society engagement instead of candidate
progress.

**Why this priority**: This is the payoff of the candidate-to-member journey and demonstrates the full
arc, but requires the earlier capabilities to be meaningful.

**Independent Test**: Select the fully-complete profile and confirm the experience switches to member
content; select an incomplete profile and confirm the transition is unavailable with the reason shown.

**Acceptance Scenarios**:

1. **Given** a profile with all requirements complete, **When** the experience is rendered, **Then** the
   simulated member dashboard is shown.
2. **Given** a profile with outstanding requirements, **When** the transition is attempted, **Then** it is
   unavailable and the blocking requirements are named.
3. **Given** the member experience, **When** it is shown, **Then** it presents member benefits,
   professional-learning progress and society engagement, and no candidate exam prompts.
4. **Given** the transition occurs, **When** the audit trail is inspected, **Then** the stage change is
   recorded against the run.

---

### Edge Cases

- No events are available for the candidate's region or stage: the events area shows an explanatory
  empty state rather than unrelated items.
- A reference is recorded as declined: it counts as outstanding and prompts identifying a replacement.
- A reference has been pending beyond a reasonable window: it is highlighted as needing follow-up.
- Requirements were complete but new data makes them incomplete: the member experience reverts and the
  reason is shown.
- Recommendations would duplicate an item already in the action plan: the duplicate is suppressed or
  cross-referenced rather than shown twice.
- The expected timeline cannot be estimated because a prerequisite is unmet: the timeline states the
  blocking prerequisite instead of showing a date.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate recommendations in three areas: learning, events and society
  activity, and career or volunteer opportunities.
- **FR-002**: Every recommendation MUST include a title, a short description, an area and a reason tied
  to the candidate's stage or gaps.
- **FR-003**: System MUST rank recommendations and limit each area to a reviewable maximum.
- **FR-004**: System MUST avoid duplicate recommendations within a run and MUST cross-reference rather
  than duplicate items already present in the action plan.
- **FR-005**: System MUST produce member-oriented recommendations for member-stage profiles.
- **FR-006**: System MUST list every required reference with its assignee and status, and MUST identify
  outstanding, declined and overdue references.
- **FR-007**: System MUST present an application-readiness checklist whose items map to the membership
  requirements, marking which items block submission.
- **FR-008**: System MUST present an expected approval timeline covering the stages from submission to
  approval, labelled as an estimate, or state the blocking prerequisite when it cannot be estimated.
- **FR-009**: System MUST enable the transition to the simulated member experience only when all
  membership requirements are complete, and MUST name the blocking requirements otherwise.
- **FR-010**: The simulated member experience MUST present member benefits, professional-learning
  progress and society engagement, and MUST NOT present candidate exam or application prompts.
- **FR-011**: System MUST record the lifecycle stage change against the run when the transition occurs.
- **FR-012**: System MUST include a guidance-only disclaimer with the timeline and any
  eligibility-related statement.
- **FR-013**: System MUST operate with no language-model credential configured, using deterministic
  recommendation content.
- **FR-014**: System MUST make recommendation generation callable as an independently addressable
  specialist agent.
- **FR-015**: System MUST persist recommendations, reference statuses and the transition event against
  the run.

### Key Entities

- **Recommendation**: A ranked suggestion — area, title, description, reason and optional link to a
  related action item.
- **Reference**: A required referee — name, relationship, status, request date and follow-up need.
- **Application Checklist Item**: A membership requirement expressed as a submission gate — status and
  whether it blocks submission.
- **Approval Timeline**: The estimated sequence of stages from submission to approval, with an expected
  window per stage and an estimate label.
- **Member Experience**: The simulated member view — benefits, professional-learning progress and
  society engagement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every synthetic profile receives at least one recommendation in each of the three areas,
  with no duplicates.
- **SC-002**: 100% of recommendations state a reason that references the candidate's stage or a specific
  gap.
- **SC-003**: For every profile, the reference tracker's outstanding count matches the reference shortfall
  reported by the readiness assessment.
- **SC-004**: The member transition is offered for exactly those profiles with all requirements complete,
  and blocked with named reasons for all others.
- **SC-005**: Recommendations and the timeline are produced for all profiles with no language-model
  credential configured.
- **SC-006**: The lifecycle stage change is discoverable in the audit trail for 100% of transitions.

## Assumptions

- Events, learning resources and career opportunities are synthetic content shipped in local storage;
  there is no integration with a real events or learning platform.
- Expected approval windows are documented, configurable estimates, not commitments, and are never
  presented as official CFA Institute timelines.
- Reference submission is simulated; no email or notification is sent to any referee.
- The member experience is a simulation for demonstration; it does not grant any real membership benefit.
- Depends on feature 001 for orchestration, agent addressing, persistence and audit, on feature 003 for
  requirement statuses, and on feature 005 for action-plan cross-referencing.
