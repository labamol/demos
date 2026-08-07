# Feature Specification: Membership Readiness Assessment

**Feature Branch**: `003-membership-readiness-assessment`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Produce a membership readiness score from transparent deterministic rules, explain it in plain language, list every missing requirement, and identify the single highest-priority action the candidate should take next."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate gets a readiness score they can trust (Priority: P1)

A candidate wants one number that tells them how close they are to CFA Institute membership, and
wants to see exactly how that number was calculated.

**Why this priority**: The readiness score is the anchor metric of the candidate-to-member
transition experience; the rest of the assessment hangs off it.

**Independent Test**: Run each synthetic profile and confirm each returns a whole-number score
between 0 and 100 together with a per-category breakdown whose weighted sum reproduces the score.

**Acceptance Scenarios**:

1. **Given** any candidate profile, **When** readiness is assessed, **Then** a whole-number score
   between 0 and 100 is returned.
2. **Given** a readiness score, **When** the breakdown is inspected, **Then** each contributing
   category is listed with its own completion level, its weight and its contribution, and the
   weighted contributions sum to the reported score.
3. **Given** the same profile assessed twice with no data change, **When** the scores are compared,
   **Then** they are identical.
4. **Given** a profile that satisfies every requirement, **When** readiness is assessed, **Then** the
   score is 100.
5. **Given** a profile at the very start of the journey, **When** readiness is assessed, **Then** the
   score is low but non-negative and the breakdown explains why.

---

### User Story 2 - Candidate understands what the score means (Priority: P1)

The candidate reads a short plain-language interpretation of their score — what it implies about
their position, what is driving it down, and what changes would move it most.

**Why this priority**: A bare number without interpretation does not change behaviour; the narrative
is the AI value-add over a static tracker.

**Independent Test**: Confirm each profile receives a narrative that references its own actual gaps,
and that a deterministic narrative is produced when no language model is available.

**Acceptance Scenarios**:

1. **Given** an assessed profile, **When** the interpretation is read, **Then** it references the
   candidate's actual largest gap by name.
2. **Given** no language-model credential is configured, **When** the interpretation is produced,
   **Then** a deterministic, profile-specific narrative is returned and the skipped model call is
   recorded.
3. **Given** an interpretation is displayed, **When** the user reads it, **Then** a guidance-only
   disclaimer is shown alongside it.
4. **Given** a language model is configured but fails, **When** the interpretation is produced,
   **Then** the deterministic narrative is substituted and the failure is recorded, without failing
   the run.

---

### User Story 3 - Candidate sees exactly what is missing (Priority: P1)

The candidate sees an itemized list of unmet membership requirements — exams, qualifying experience,
references, application submission, professional-conduct statement, dues — each with its status and
what would satisfy it.

**Why this priority**: The missing-requirements list is what makes the score actionable and feeds the
application checklist and the action plan.

**Independent Test**: For each profile, confirm the set of unmet requirements matches the profile
data and that satisfied requirements are marked complete rather than omitted.

**Acceptance Scenarios**:

1. **Given** a candidate missing references, **When** requirements are listed, **Then** references
   appear as unmet with the number still needed.
2. **Given** a candidate who has passed all three levels, **When** requirements are listed, **Then**
   the exam requirement is marked complete.
3. **Given** any candidate, **When** requirements are listed, **Then** every requirement category
   appears exactly once with an unambiguous status.

---

### User Story 4 - Candidate is told the single most important next step (Priority: P2)

Among all gaps, the candidate is shown the one action that would improve readiness the most, with a
reason.

**Why this priority**: Prioritization prevents the checklist from being overwhelming, but the
assessment is still useful without it.

**Independent Test**: Construct two profiles whose largest gaps differ and confirm the highest-priority
action differs accordingly.

**Acceptance Scenarios**:

1. **Given** a candidate whose largest weighted gap is exams, **When** the priority action is
   determined, **Then** it concerns completing the remaining exam level.
2. **Given** a candidate with only an unsubmitted application remaining, **When** the priority action
   is determined, **Then** it is to submit the application.
3. **Given** a fully ready candidate, **When** the priority action is determined, **Then** it reflects
   maintaining membership rather than an unmet gap.

---

### Edge Cases

- Recorded experience exceeds the required total: the experience category is capped at complete and
  does not inflate the score above 100.
- A candidate has more references than required: the reference category is complete, not over-weighted.
- A requirement has an unknown or in-review status: it is treated as not yet satisfied and labelled
  as pending rather than failed.
- Profile data is internally inconsistent (for example, membership applied for but no exams passed):
  the score is still computed and the inconsistency is surfaced in the missing-requirements list.
- Weights are reconfigured: the score changes, but the breakdown must still reproduce the reported
  score exactly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST compute a readiness score as a whole number from 0 to 100 using
  deterministic, documented rules with published category weights.
- **FR-002**: Category weights MUST sum to 1 and MUST be defined in one place, visible to reviewers.
- **FR-003**: System MUST return a per-category breakdown with each category's completion level,
  weight and contribution, such that the contributions reproduce the reported score.
- **FR-004**: System MUST cap every category's completion level at fully complete so that surplus
  achievement never inflates the score.
- **FR-005**: System MUST produce identical output for identical input; the score MUST NOT depend on
  any language-model output.
- **FR-006**: System MUST produce a plain-language interpretation of the score that references the
  candidate's actual gaps.
- **FR-007**: System MUST produce the interpretation deterministically when no language model is
  available or when a model call fails, and MUST record the skip or failure.
- **FR-008**: System MUST list every membership requirement with an explicit status of met, pending
  or not met, and MUST state what would satisfy each unmet requirement.
- **FR-009**: System MUST identify exactly one highest-priority action with a rationale tied to the
  breakdown.
- **FR-010**: System MUST display a guidance-only disclaimer with the score and the interpretation.
- **FR-011**: System MUST persist the score, breakdown, requirement statuses, interpretation and
  priority action against the run that produced them.
- **FR-012**: Users MUST be able to view the full breakdown, not just the headline score.

### Key Entities

- **Readiness Assessment**: The result for one run — overall score, category breakdown, requirement
  statuses, interpretation, highest-priority action and disclaimer.
- **Readiness Category**: One weighted contributor to the score — name, weight, completion level and
  contribution.
- **Membership Requirement**: A named prerequisite for membership — status, what satisfies it and any
  remaining quantity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every synthetic profile, the sum of weighted category contributions equals the
  reported score exactly.
- **SC-002**: Repeated assessment of an unchanged profile returns an identical score 100% of the time.
- **SC-003**: The four synthetic personas produce clearly separated scores spanning early-stage to
  fully-ready, so a reviewer can distinguish stages at a glance.
- **SC-004**: A reviewer can reconstruct the score by hand from the published weights and the profile
  data, with no hidden adjustments.
- **SC-005**: Assessment completes successfully for all profiles with no language-model credential
  configured.
- **SC-006**: Every unmet requirement shown in the assessment appears as at least one item in the
  generated action plan.

## Assumptions

- Membership requirements follow the CFA Institute journey described in the POC scope: completing the
  CFA Program, qualifying work experience, references, submitting the application, society review,
  institute approval and dues.
- The required qualifying-experience total and reference count are configurable constants documented
  alongside the weights.
- Society review and institute approval outcomes are simulated; the POC never issues an official
  determination.
- Depends on feature 001 for orchestration, persistence and audit.
