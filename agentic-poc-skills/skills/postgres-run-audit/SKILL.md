---
name: "postgres-run-audit"
description: "Persist workflow runs, state checkpoints, agent audit events and artifacts in PostgreSQL, and evolve the DDL. Use when touching persistence or the audit trail."
---

## When to use

Use for any change to persistence, the audit trail, or the database definition script.

## Schema shape

Domain tables, plus this reusable audit core:

- `workflow_run` — run id (UUID PK), subject id (nullable at creation), status, started/finished timestamps, input parameters.
- `workflow_state` — one row per node per run: `run_id`, `node_name`, `sequence`, `state_json` JSONB, `UNIQUE (run_id, sequence)`.
- `agent_audit_log` — `run_id`, subject id, `event_type`, `node_name`, `agent_name`, `status`, `message`, `payload` JSONB, `duration_ms`, `created_at`. Indexed by run id and subject id.
- Artifact tables referencing `run_id` with `ON DELETE CASCADE`.
- A `v_latest_run` view for the UI's default query.

## Rules

1. The DDL is idempotent: `IF NOT EXISTS` everywhere; re-running against an existing database is a no-op.
2. Schema changes are additive — add columns/tables rather than rewriting; ship the DDL change in the same commit as the code that needs it.
3. **A run row is created before the subject is known.** Create it with a null subject id, then attach after the loading node resolves it. Never insert an empty-string id to satisfy a NOT NULL — that constraint should not be NOT NULL.
4. **Audit writes must never break a run.** Catch persistence failures, buffer the events in memory, return them to the caller, and record the degradation itself. An observability system that takes down the thing it observes is worse than none.
5. Use sessions through a single scoped context manager; no session leaks.
6. Timestamps are `TIMESTAMPTZ DEFAULT now()`.
7. Never log or persist secrets. Payload JSONB is for structured operational data only.

## Verifying a run

```sql
SELECT node_name, sequence FROM workflow_state WHERE run_id = :run ORDER BY sequence;
SELECT event_type, node_name, agent_name, status, duration_ms
FROM agent_audit_log WHERE run_id = :run ORDER BY id;
```

Gapless sequence, one checkpoint per executed node, a matched start/complete (or fail) pair per node.

## Checklist

- [ ] DDL applies to an empty database and re-applies cleanly.
- [ ] Transport and LLM-skip events present.
- [ ] Run completes with the database stopped.
