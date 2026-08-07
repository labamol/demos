# Feature Specification: Work-Experience Evaluator

**Feature Branch**: `004-work-experience-evaluator`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Let a candidate describe their role — job title, employer type, description, activities, duration and share of time on investment work — and return which activities likely qualify toward CFA Institute membership, which do not, what evidence is missing, a confidence level, an improved description they can reuse in their application, and whether the case should be escalated to a human reviewer."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate finds out whether their role likely qualifies (Priority: P1)

A candidate enters their job title, employer type, a description of their role, their main
activities, how long they have been in the role, and roughly what share of their time is spent on
investment-related work. They receive a clear breakdown of which activities are likely to count
toward the qualifying-experience requirement and which are not.

**Why this priority**: "Will my job count?" is the single biggest source of uncertainty in the
candidate-to-member transition and the core of this capability.

**Independent Test**: Submit a role mixing analytical and administrative duties and confirm the
response separates likely-qualifying from likely-non-qualifying activities with a reason for each.

**Acceptance Scenarios**:

1. **Given** a role including valuation and investment recommendations, **When** it is evaluated,
   **Then** those activities appear as likely qualifying with a reason.
2. **Given** a role including data entry and reconciliation, **When** it is evaluated, **Then** those
   activities appear as likely non-qualifying with a reason.
3. **Given** a role with a mix of both, **When** it is evaluated, **Then** both lists are populated
   and no activity appears in both.
4. **Given** any evaluation, **When** the result is shown, **Then** it carries a guidance-only
   disclaimer stating this is not an official eligibility determination.

---

### User Story 2 - Candidate learns how much qualifying time they have accrued (Priority: P1)

Beyond a yes/no, the candidate sees an estimate of qualifying months and hours based on their
duration and the share of time on investment work, measured against the requirement.

**Why this priority**: Automatic work-experience estimation is explicitly called out as a primary
transition opportunity and feeds the readiness score.

**Independent Test**: Submit a role of known duration and time-share and confirm the estimated
qualifying months equal duration multiplied by the investment-time share, and the progress against
the requirement is reported.

**Acceptance Scenarios**:

1. **Given** 36 months at 50% investment-related time, **When** evaluated, **Then** approximately 18
   qualifying months are estimated.
2. **Given** an estimate, **When** it is displayed, **Then** it is shown against the total months
   required for membership with the remaining shortfall.
3. **Given** total accrued experience exceeds the requirement, **When** evaluated, **Then** progress
   is reported as complete and not more than complete.
4. **Given** an evaluation, **When** the calculation is inspected, **Then** the arithmetic is
   deterministic and reproducible from the inputs.

---

### User Story 3 - Candidate is told what evidence is missing (Priority: P2)

The candidate sees what their submission lacks — for example concrete investment-decision examples,
a supervisor attestation, a percentage-of-time statement — so they can strengthen the case before
applying.

**Why this priority**: Turns a borderline verdict into a set of concrete next steps and reduces
rejected applications.

**Independent Test**: Submit a vague description and confirm specific missing-evidence items are
returned; submit a detailed one and confirm fewer items are returned.

**Acceptance Scenarios**:

1. **Given** a description with no concrete examples, **When** evaluated, **Then** missing evidence
   includes a request for specific investment-decision examples.
2. **Given** a submission with no time-share stated, **When** evaluated, **Then** missing evidence
   includes a percentage-of-time statement.
3. **Given** a complete, well-evidenced submission, **When** evaluated, **Then** the missing-evidence
   list is empty or minimal and confidence is high.

---

### User Story 4 - Candidate receives an improved description and a confidence level (Priority: P2)

The candidate gets a rewritten, application-ready description of their role that foregrounds the
qualifying activities, plus a confidence level for the assessment and a clear signal when the case
is too ambiguous to judge automatically.

**Why this priority**: Directly reduces effort at application time and sets expectations about
automated judgement.

**Independent Test**: Confirm every evaluation returns a confidence level and an improved description,
and that a deliberately ambiguous role is flagged for human review.

**Acceptance Scenarios**:

1. **Given** any evaluation, **When** the result is returned, **Then** it includes a confidence level
   and a rewritten description that preserves the candidate's facts.
2. **Given** an ambiguous or borderline role, **When** it is evaluated, **Then** the result recommends
   escalation to a human reviewer and explains why.
3. **Given** no language-model credential is configured, **When** a role is evaluated, **Then** the
   activity classification, estimates and confidence are still produced deterministically and the
   improved description falls back to a deterministic rewrite.

---

### Edge Cases

- Empty or whitespace-only role description: the request is rejected with an actionable validation
  message and no artifact is persisted.
- Investment-time share outside 0–100: the request is rejected.
- Zero-month or future-dated employment duration: no qualifying time is estimated and the anomaly is
  reported.
- Non-investment employer type (for example a regulator or academia) with genuinely qualifying
  activities: the activities are still assessed on their substance, and the case is flagged for human
  review.
- Overlapping employment periods across multiple roles: overlapping time is not double-counted.
- A description written in a language other than English or full of unexplained jargon: confidence is
  reduced and escalation is recommended.
- Free-text input containing instructions aimed at the assistant must not change the deterministic
  classification or the disclaimer.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept job title, employer type, role description, a list of activities,
  employment duration and the percentage of time spent on investment-related work.
- **FR-002**: System MUST validate every input, rejecting empty descriptions, non-positive durations
  and out-of-range percentages with actionable messages.
- **FR-003**: System MUST return activities classified as likely qualifying or likely non-qualifying,
  each with a reason, and MUST NOT place an activity in both lists.
- **FR-004**: System MUST estimate qualifying months and hours deterministically from duration and
  investment-time share, and MUST report progress against the required total without exceeding
  complete.
- **FR-005**: System MUST NOT double-count overlapping employment periods.
- **FR-006**: System MUST return a list of missing evidence items specific to the submission.
- **FR-007**: System MUST return a confidence level for the assessment.
- **FR-008**: System MUST return an improved, application-ready description that preserves the
  candidate's stated facts and adds no invented achievements.
- **FR-009**: System MUST recommend escalation to a human reviewer when confidence is low or the case
  is ambiguous, stating the reason.
- **FR-010**: System MUST include a guidance-only disclaimer in every response, stating that this is
  not an official CFA Institute eligibility determination.
- **FR-011**: System MUST produce classifications, estimates and confidence deterministically,
  independent of any language-model output.
- **FR-012**: System MUST operate with no language-model credential configured, falling back to a
  deterministic improved description.
- **FR-013**: System MUST persist each evaluation against its run, including inputs and outputs.
- **FR-014**: Users MUST be able to evaluate an ad-hoc role in addition to the roles recorded in the
  selected profile, and see both results.
- **FR-015**: System MUST make the evaluator callable as an independently addressable specialist agent.

### Key Entities

- **Work Experience Submission**: The candidate-provided role — title, employer type, description,
  activities, duration and investment-time share.
- **Activity Assessment**: One activity with its qualifying verdict and reason.
- **Experience Evaluation**: The full result — qualifying and non-qualifying activities, estimated
  qualifying months and hours, progress against the requirement, missing evidence, confidence,
  improved description, escalation recommendation and disclaimer.
- **Qualifying Criteria**: The documented keyword and rule set, required total months and hours-per-month
  convention used by the estimation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a submission with known duration and time-share, the estimated qualifying months are
  reproducible by hand from the published rules, every time.
- **SC-002**: Across a curated set of clearly qualifying and clearly non-qualifying activity
  descriptions, classification is correct for at least 90% of items.
- **SC-003**: 100% of evaluations return a confidence level, a disclaimer and either an empty or an
  itemized missing-evidence list.
- **SC-004**: Every ambiguous case in the curated set is flagged for human review rather than given a
  confident verdict.
- **SC-005**: Evaluation completes for all synthetic profiles and for ad-hoc submissions with no
  language-model credential configured.
- **SC-006**: The qualifying months reported here match the work-experience figure used by the
  readiness assessment for the same run.

## Assumptions

- The qualifying-experience requirement is a documented, configurable total number of months, with a
  documented hours-per-month convention for reporting hours.
- Qualifying and non-qualifying activity keyword sets are configuration, reviewable and adjustable
  without code changes to the rules engine.
- The POC never issues an official eligibility determination; a human reviewer is always the final
  authority.
- Supporting documents referenced by a profile may be read as additional evidence where available.
- Depends on feature 001 for orchestration, agent addressing, persistence and audit.
