---
name: "cfa-postgres-audit"
description: "Persist runs, state checkpoints, agent audit events and artifacts in PostgreSQL, and evolve the DDL. Use when touching persistence, the audit trail or db/ddl.sql."
---

## When to use

Use for any change to persistence, the audit trail, or the database definition script.

## Schema shape

Core tables: `candidate`, `exam_record`, `work_experience`, `candidate_reference`, `workflow_run`, `workflow_state`, `agent_audit_log`, `readiness_assessment`, `work_experience_evaluation`, `action_plan`, `action_item`, `recommendation`, plus a latest-run view.

- `workflow_state`: one row per node per run, `UNIQUE (run_id, sequence)`, state stored as JSONB.
- `agent_audit_log`: run id, candidate id, event type, node, agent, status, message, JSONB payload, duration, timestamp. Indexed by run id and candidate id.
- Artifacts reference their `run_id` with `ON DELETE CASCADE`.

## Rules

1. The DDL is idempotent: every statement uses `IF NOT EXISTS` (or equivalent) and re-running it against an existing database is a no-op.
2. Schema changes are additive within the POC — add columns/tables rather than rewriting; ship the DDL change in the same commit as the code that needs it.
3. A run row is created before the profile is known: create it with a null candidate, then attach the candidate id after `load_profile`. Never insert an empty-string candidate id.
4. **Audit writes must never break a run.** Persistence failures are caught, the events are buffered in memory and returned to the caller, and the degradation itself is recorded.
5. Use SQLAlchemy sessions through a single scoped context manager; no session leaks, no autocommit-per-statement in hot paths.
6. Timestamps are `TIMESTAMPTZ DEFAULT now()`.
7. Never log or persist secrets. Payload JSONB is for structured operational data only.

## Verifying

```sql
SELECT node_name, sequence FROM workflow_state WHERE run_id = :run ORDER BY sequence;
SELECT event_type, node_name, agent_name, status, duration_ms
FROM agent_audit_log WHERE run_id = :run ORDER BY id;
```

## Checklist

- [ ] DDL applies to an empty database and re-applies cleanly.
- [ ] One checkpoint per executed node, gapless sequence.
- [ ] Matched start/complete (or fail) event per node.
- [ ] Transport and LLM-skip events present.
- [ ] Run completes with the database stopped.
