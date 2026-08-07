# Feature Specification: Candidate Q&A Assistant

**Feature Branch**: `006-candidate-qa-assistant`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Let the person ask free-text questions about exams, work experience and membership, and answer them grounded in their own profile and the assessment produced for their current run, never inventing eligibility determinations."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate asks a question about their own situation (Priority: P1)

While viewing their dashboard, the candidate types a question such as "how much more experience do I
need?" and receives an answer that uses their own numbers rather than generic guidance.

**Why this priority**: Asking questions about exams, work experience and membership is one of the
required user experiences of the POC.

**Independent Test**: Ask each of an exam, an experience and a membership question for one profile and
confirm each answer cites that profile's actual figures.

**Acceptance Scenarios**:

1. **Given** a candidate with partial experience, **When** they ask how much more experience they need,
   **Then** the answer states their accumulated qualifying months and the remaining shortfall.
2. **Given** a candidate who has passed two levels, **When** they ask what exam comes next, **Then** the
   answer names the correct next level and its status.
3. **Given** a candidate with unmet requirements, **When** they ask what is stopping them from applying,
   **Then** the answer lists their actual unmet requirements.
4. **Given** any answer, **When** it is displayed, **Then** it carries a guidance-only disclaimer.

---

### User Story 2 - Answers stay grounded and never overreach (Priority: P1)

The assistant must not invent policy, promise approval, or contradict the deterministic assessment
shown elsewhere in the application.

**Why this priority**: An assistant that fabricates eligibility guidance is worse than no assistant,
and grounding is a constitutional requirement.

**Independent Test**: Ask questions whose answers are not derivable from the profile or the assessment
and confirm the assistant declines and points to an authoritative next step.

**Acceptance Scenarios**:

1. **Given** a question the available data cannot answer, **When** it is asked, **Then** the assistant
   says so and suggests where to get an authoritative answer, rather than guessing.
2. **Given** a question asking whether the candidate will be approved, **When** it is asked, **Then**
   the answer explains that the POC cannot make an official determination.
3. **Given** an answer that references a figure, **When** it is compared with the readiness assessment
   for the same run, **Then** the two agree.
4. **Given** a question containing instructions aimed at the assistant, **When** it is asked, **Then**
   the assistant ignores the injected instructions and answers within its defined scope.

---

### User Story 3 - Questions are answered without external AI access (Priority: P2)

The demo can be given with no language-model credential and questions still receive useful, grounded
answers.

**Why this priority**: Required for offline demonstration, though the answers are richer with a model.

**Independent Test**: Clear the credential, ask the standard question set, and confirm profile-specific
deterministic answers are returned and skipped model calls are recorded.

**Acceptance Scenarios**:

1. **Given** no credential is configured, **When** a question is asked, **Then** a deterministic,
   profile-specific answer is returned.
2. **Given** no credential is configured, **When** the audit trail is inspected, **Then** the skipped
   model call is recorded.
3. **Given** a model call fails, **When** a question is asked, **Then** the deterministic answer is
   substituted and the failure is recorded without failing the run.

---

### Edge Cases

- Empty or whitespace-only question: no answer area is shown and no error is raised.
- Very long question: it is truncated or rejected with a clear message rather than failing silently.
- Question in scope but about a topic outside exams, experience and membership: the assistant states
  the topic is out of scope for the POC.
- Question asked before a run has completed: the user is told to run the workflow first.
- Question that requests personal data about another candidate: the request is refused.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to submit a free-text question alongside a profile selection and
  receive an answer as part of the same run.
- **FR-002**: System MUST ground every answer in the selected profile and the artifacts produced by the
  current run.
- **FR-003**: System MUST cover exams, work experience and membership topics, and MUST state clearly
  when a question is outside that scope.
- **FR-004**: System MUST NOT assert any official eligibility or approval determination, and MUST
  include a guidance-only disclaimer with every answer.
- **FR-005**: System MUST NOT contradict figures produced by the deterministic assessment for the same
  run.
- **FR-006**: System MUST decline, rather than guess, when the available data cannot answer the question.
- **FR-007**: System MUST ignore instructions embedded in user-supplied question text that attempt to
  change its scope, disclaimer or grounding.
- **FR-008**: System MUST treat an empty question as "no question asked" and produce no answer artifact.
- **FR-009**: System MUST answer deterministically when no language model is available or a model call
  fails, and MUST record the skip or failure.
- **FR-010**: System MUST persist each question and answer against its run and record the associated
  model interaction.

### Key Entities

- **Question**: The user's free-text input for a run.
- **Answer**: The grounded response — text, the topics it addresses, the run artifacts it drew on, and
  the disclaimer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a standard set of exam, experience and membership questions across all profiles,
  100% of answers cite figures that match the run's assessment.
- **SC-002**: 100% of answers include a guidance-only disclaimer.
- **SC-003**: For a curated set of unanswerable or out-of-scope questions, the assistant declines in
  100% of cases rather than fabricating an answer.
- **SC-004**: Questions are answered successfully for all profiles with no language-model credential
  configured.
- **SC-005**: Submitting an empty question produces no answer area and no error, every time.

## Assumptions

- Single-turn question answering; conversational memory across turns is out of scope for the POC.
- Questions are asked in English.
- There is no retrieval over external CFA Institute content; grounding is limited to the profile, the
  supporting documents in local storage, and the current run's artifacts.
- Depends on feature 001 for orchestration and audit and on feature 003 for the figures it cites.
