---
name: "cfa-poc-domain"
description: "CFA candidate-to-member domain reference: journey stages, membership requirements, readiness weights, personas and the guidance-only boundary. Use when a task needs domain grounding."
---

## When to use

Use when a task needs grounding in the CFA candidate-to-member domain: naming, requirement semantics, scoring constants or the synthetic personas.

## Journey

**Candidate**: create a CFA account -> register for an exam -> candidate dashboard -> schedule the exam -> study with curriculum and practice resources -> receive results -> register for the next level.

**Member**: complete the CFA Program -> obtain qualifying work experience -> apply for membership -> submit references -> society review -> CFA Institute approval -> pay dues -> become a member/charterholder.

**Transition opportunities** (the POC's focus): eligibility progress tracker, automatic work-experience estimation, reference tracking, membership readiness score, application checklist, expected approval timeline.

## Membership requirement categories

`exams`, `work_experience`, `references`, `application`, `professional_conduct`, `dues`. Each has a status of met, pending or not met — pending (for example a reference awaiting response, or a society review in progress) is never treated as met.

## Scoring constants

Readiness weights (must sum to 1, defined in one place):

| Category | Weight |
| --- | --- |
| exams | 0.40 |
| work_experience | 0.30 |
| references | 0.15 |
| application | 0.10 |
| professional_conduct | 0.05 |

Other constants: required qualifying months = 48; required references = 2; hours-per-qualifying-month convention = 160.

Score = round(sum(category_completion x weight) x 100), with each category completion capped at 1.0.

## Work-experience classification

Likely qualifying: financial analysis, valuation, investment recommendation, portfolio management, research, risk analysis, trading strategy, client investment advice, economic analysis.

Likely non-qualifying: administrative reporting, data entry, reconciliation, scheduling, generic IT support, clerical processing.

Estimated qualifying months = employment months x investment-time share. Overlapping periods are not double-counted. Ambiguous cases are escalated to a human reviewer rather than given a confident verdict.

## Synthetic personas

Supplied as fixtures in `data/mock/applications/`, validated by `data/profile.schema.json`. These are
specification, not sample data: never edit a fixture to make an implementation pass.

| Persona | Id | Stage | Situation | Readiness |
| --- | --- | --- | --- | --- |
| Rohan Patel | `CAND-101990` | early candidate | One level passed; mostly non-qualifying operations work; no references | 15 |
| Arjun Mehta | `CAND-100234` | advanced candidate | Passed Levels I and II, preparing for Level III, 30 months at 80% investment time | 42 |
| Aisha Khan | `CAND-100871` | applicant | Passed all levels, sufficient experience, has not started the application | 70 |
| Neha Sharma | `MEM-204512` | member | Existing charterholder; everything satisfied | 100 |

The scores are exact, not bands — each is reproducible by hand from the weights above, and
`data/mock/README.md` works the derivation through.

## The guidance-only boundary

The POC never issues an official CFA Institute eligibility, approval or timeline determination. Every eligibility-related surface carries a guidance-only disclaimer, and a human reviewer is always the final authority. All data is synthetic.
