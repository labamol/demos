---
name: "cfa-langgraph-workflow"
description: "Author or modify the LangGraph agentic workflow for the CFA onboarding POC: graph wiring, node contracts, shared state, checkpoints and conditional edges. Use when adding, reordering or debugging a workflow node."
---

## When to use

Use whenever a task adds, changes, reorders or debugs a node in the CFA onboarding LangGraph workflow, or changes the shared workflow state.

## Canonical graph

```
load_profile -> assess_readiness -> evaluate_experience -> build_action_plan
             -> recommend -> build_dashboard -> (answer if a question was asked) -> END
```

Exactly one compiled graph exists for the application. Do not create a second graph, and do not bypass the graph with ad-hoc service calls from the API layer.

## Node contract (non-negotiable)

Every node MUST:

1. Take the shared typed state and return only the keys it owns. Never mutate keys owned by another node.
2. Run inside the audit context manager so that `node_started` and `node_completed` (or `node_failed` with the exception type and message) are emitted with a duration.
3. Write a state checkpoint after it completes, with a monotonically increasing sequence number scoped to the run.
4. Be runnable in isolation against a mock profile with no other node having run, given its required state keys.
5. Delegate file reads through the MCP client and specialist work through the A2A client — never import a specialist agent's implementation directly from a node.

## Shared state

- The state is a `TypedDict`/Pydantic-backed structure whose values are Pydantic models, not loose dicts.
- Add a new key only when no existing key expresses the data; document its owner node in the same change.
- Never place secrets, raw file handles, open connections or unserializable objects in state — checkpoints must serialize to JSON.

## Conditional edges

- Conditional routing (for example the optional `answer` node) reads a boolean or enum already present in state; routing functions must be pure and side-effect free.
- Every conditional branch must terminate at `END`; no cycles in the POC graph.

## Failure handling

- A node that fails records `node_failed` and re-raises; the run is marked failed and earlier checkpoints stay queryable.
- Transport failures (MCP or A2A) are not node failures: fall back, record the substituted transport, and continue.

## Checklist before finishing

- [ ] Node emits start/complete/fail events with duration.
- [ ] Node writes exactly one checkpoint.
- [ ] Node owns a disjoint set of state keys.
- [ ] Graph still compiles and every path reaches `END`.
- [ ] A full run succeeds for every mock persona both with and without `OPENAI_API_KEY`.
