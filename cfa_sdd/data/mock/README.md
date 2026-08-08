# Mock data — synthetic profiles and documents

These fixtures are **part of the specification**, not sample data. Every feature spec's acceptance
scenarios and `SC-` success criteria are written against these four personas, so the implementation
must load these exact files and reproduce the expected values below.

All data is synthetic. No real candidate, member, employer or referee is represented.

## Layout

```
data/
├── profile.schema.json                 # the documented profile shape (JSON Schema 2020-12)
└── mock/
    ├── applications/                   # one JSON profile per persona, selectable in the UI
    │   ├── rohan_patel_early_candidate.json
    │   ├── arjun_mehta_candidate.json
    │   ├── aisha_khan_applicant.json
    │   └── neha_sharma_member.json
    └── documents/<candidate_id>/       # supporting documents, listed and read over MCP
```

Both directories are read **exclusively** through the MCP file server (see the
`cfa-mcp-file-access` skill). Direct filesystem reads are permitted only on the audited fallback
path inside the MCP client.

Point the implementation at this directory with `DATA_DIR` in `.env`, and declare the MCP server in
`mcp.config.json`.

## The four personas

| File | Id | Persona | Stage | Passed | Qualifying months | References | Expected readiness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rohan_patel_early_candidate.json` | `CAND-101990` | Early candidate, non-qualifying experience | candidate | I | 3.2 | none | **15%** |
| `arjun_mehta_candidate.json` | `CAND-100234` | Advanced candidate | candidate | I, II | 24.0 | 1 identified | **42%** |
| `aisha_khan_applicant.json` | `CAND-100871` | Newly eligible, application not started | candidate | I, II, III | 56.5 | 1 identified, 1 not started | **70%** |
| `neha_sharma_member.json` | `MEM-204512` | Existing member | member | I, II, III | 96.0 | 2 verified | **100%** |

Each persona exists to exercise a distinct branch, so do not "improve" them:

- **Rohan** — the empty-ish case: one level passed, mostly non-qualifying operations work, no
  references. Exercises low scores, empty states, and the evaluator's non-qualifying classification.
- **Arjun** — the mid-journey case: partially complete on every axis at once, with 30 months at 80%
  investment time. The most useful persona for action-plan prioritization.
- **Aisha** — the interesting case: fully eligible on exams *and* experience but has not started the
  application, so the plan must be dominated by application and reference actions rather than study.
- **Neha** — the terminal case: everything satisfied. Exercises the member experience in feature 007
  and proves the UI does not offer a candidate a plan they have already completed.

## Reproducing the expected readiness

The scores above are not magic numbers — they follow from the published weights in the
`cfa-poc-domain` skill and must be reproducible by hand:

```
score = round(100 * Σ (category_completion × weight)),   each completion capped at 1.0

exams 0.40 · work_experience 0.30 · references 0.15 · application 0.10 · conduct 0.05
exams_completion = passed_levels / 3
work_completion  = min(qualifying_months / 48, 1.0)
refs_completion  = min(submitted_or_verified_refs / 2, 1.0)
```

Worked example — Arjun: `(2/3)(0.40) + (24/48)(0.30) + 0 + 0 + 0 = 0.4167 → 42`.

Note that a reference with status `identified` contributes **nothing**. Pending is never treated as
met — that is why Aisha sits at 70% rather than 85%.

`qualifying_months = months × investment_time_pct / 100`, summed across roles. It is deliberately
authored rather than derived from `start_date`/`end_date` so the fixtures do not drift as time
passes and the expected scores above stay stable.

## Adding or changing a fixture

1. Validate against `../profile.schema.json` — it is the input contract for the whole workflow.
2. Recompute the expected readiness and update the table above.
3. Update any `SC-` criterion in `specs/` that cites the value you changed.
4. State which branch the new persona exercises that the existing four do not. If you cannot, you do
   not need a fifth persona.
