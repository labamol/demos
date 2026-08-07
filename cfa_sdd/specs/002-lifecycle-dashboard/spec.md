# Feature Specification: Lifecycle-Aware Dashboard

**Feature Branch**: `002-lifecycle-dashboard`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "A single dashboard that adapts to where the person is in the CFA journey — showing exam progression, membership readiness, work-experience progress, outstanding actions, recommended learning, upcoming events and AI-generated next-best actions for candidates, and simulated member benefits once the person becomes a member."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate sees their whole journey on one screen (Priority: P1)

An active candidate selects their profile and immediately sees, without navigating anywhere:
which exam levels they have passed and what is next, how ready they are for membership, how much
qualifying work experience they have accumulated, and what they still have to do.

**Why this priority**: The lifecycle-aware dashboard is the entry point of the POC; every other
capability is reached from it.

**Independent Test**: Select the advanced-candidate profile and confirm the dashboard shows exam
progression, a readiness figure, work-experience progress and a list of outstanding items, all
consistent with the underlying profile data.

**Acceptance Scenarios**:

1. **Given** a candidate who has passed Levels I and II, **When** the dashboard renders, **Then** it
   shows both levels as passed, Level III as the next step, and the registration/scheduling status
   for that level.
2. **Given** a candidate with partial qualifying experience, **When** the dashboard renders, **Then**
   it shows accumulated qualifying months against the required total and the remaining shortfall.
3. **Given** a candidate with unmet membership requirements, **When** the dashboard renders, **Then**
   each outstanding requirement is listed with its current status.
4. **Given** any candidate, **When** the dashboard renders, **Then** it shows the readiness figure
   produced by the readiness capability and links to its detailed explanation.

---

### User Story 2 - Candidate is told what to do next (Priority: P1)

Rather than reading a list of gaps, the candidate sees a short, ordered set of next-best actions
phrased for their specific situation, with the single highest-impact action called out first.

**Why this priority**: Turning status into direction is the core value proposition of the
transition experience described in the POC scope.

**Independent Test**: Run two profiles at different stages and confirm the next-best actions differ
appropriately and that the first action addresses the largest readiness gap.

**Acceptance Scenarios**:

1. **Given** a candidate whose largest gap is work experience, **When** next-best actions are
   generated, **Then** the top action concerns documenting or accruing qualifying experience.
2. **Given** a candidate who has met every requirement except submitting the application, **When**
   next-best actions are generated, **Then** the top action is to submit the membership application.
3. **Given** no language-model credential is configured, **When** next-best actions are generated,
   **Then** deterministic, profile-specific actions are still shown.

---

### User Story 3 - Member sees a member experience instead (Priority: P2)

A person who has already become a charterholder/member sees a member-oriented dashboard —
simulated membership benefits, professional-learning progress, society activity and dues status —
not a candidate progress tracker.

**Why this priority**: Demonstrates the lifecycle awareness that distinguishes this dashboard from
a static candidate view, and completes the candidate-to-member story.

**Independent Test**: Select the existing-member profile and confirm the candidate-only sections are
replaced by member benefits and member-oriented content.

**Acceptance Scenarios**:

1. **Given** a profile in the member stage, **When** the dashboard renders, **Then** simulated member
   benefits are shown and exam-registration prompts are absent.
2. **Given** a profile in the member stage, **When** readiness is displayed, **Then** it shows as
   fully complete with no outstanding membership requirements.
3. **Given** a candidate profile, **When** the dashboard renders, **Then** member-only sections are
   not shown.

---

### User Story 4 - Candidate sees relevant learning and events (Priority: P3)

The dashboard surfaces a small number of recommended learning resources and upcoming society events
matched to the person's stage and gaps.

**Why this priority**: Valuable engagement content, but the dashboard is useful without it.

**Independent Test**: Confirm each profile's dashboard shows learning and event suggestions that
differ by lifecycle stage.

**Acceptance Scenarios**:

1. **Given** a Level III candidate, **When** the dashboard renders, **Then** recommended learning is
   oriented to Level III preparation.
2. **Given** a member, **When** the dashboard renders, **Then** recommended learning is oriented to
   continuing professional learning.

---

### Edge Cases

- A brand-new candidate with no passed exams and no work experience: the dashboard must show a
  meaningful starting state rather than empty panels.
- A candidate whose recorded experience predates their first exam: progress must still be reported
  without negative or impossible values.
- A candidate with more than the required qualifying months: progress is capped at 100% and shown as
  complete.
- A profile with no upcoming events available: the events area shows an explanatory empty state.
- Underlying data is missing an expected section: the affected panel degrades to an empty state and
  the rest of the dashboard still renders.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a single dashboard view assembled from one workflow run, with no
  additional user action required after selecting a profile.
- **FR-002**: Dashboard MUST show exam progression: each level with its status, and the next exam
  step for candidates.
- **FR-003**: Dashboard MUST show the membership readiness figure and a one-line interpretation.
- **FR-004**: Dashboard MUST show work-experience progress as accumulated qualifying months against
  the required total, including the remaining shortfall.
- **FR-005**: Dashboard MUST list outstanding membership requirements with their statuses.
- **FR-006**: Dashboard MUST show an ordered set of next-best actions, with the highest-impact action
  first.
- **FR-007**: Dashboard MUST show recommended learning resources and upcoming events appropriate to
  the person's lifecycle stage.
- **FR-008**: Dashboard MUST switch to member-oriented content, including simulated member benefits,
  when the profile's lifecycle stage is member.
- **FR-009**: Dashboard content MUST be derived from the same run as every other view shown to the
  user, so that no two panels disagree.
- **FR-010**: Dashboard MUST remain fully functional when no language-model credential is configured.
- **FR-011**: Users MUST be able to navigate from the dashboard to the detailed readiness,
  work-experience, action-plan, recommendation and audit views for the same run.
- **FR-012**: System MUST display a guidance-only disclaimer wherever eligibility-related figures are
  shown.

### Key Entities

- **Dashboard View**: The assembled per-run view model — lifecycle stage, exam progression, readiness
  summary, experience progress, outstanding items, learning, events, next-best actions and member
  benefits.
- **Progress Indicator**: A named measure with a current value, a target value and a completion
  percentage.
- **Next-Best Action**: A short, ordered, candidate-specific recommendation with a rationale.
- **Member Benefit**: A simulated benefit shown only for member-stage profiles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can identify their exam status, readiness figure, experience shortfall and top
  next action within 10 seconds of the dashboard rendering, without scrolling past the first screen.
- **SC-002**: For all four synthetic profiles, every dashboard figure matches the underlying profile
  data with no contradiction between panels.
- **SC-003**: Switching from a candidate profile to the member profile changes at least the exam,
  readiness and benefits sections, with zero candidate-only prompts remaining.
- **SC-004**: The dashboard renders completely for every synthetic profile both with and without a
  language-model credential.
- **SC-005**: Every dashboard panel can be traced to the run identifier that produced it.

## Assumptions

- The dashboard is read-only; all state changes happen through the action-plan capability.
- Exam registration, scheduling and results are read from the synthetic profile; there is no live
  exam system integration.
- Events and learning resources are synthetic content shipped with the workspace.
- Depends on feature 001 for the run and on features 003, 005 and 007 for the readiness figure,
  actions and recommendations it displays; before those exist it may show placeholder-free empty
  states.
