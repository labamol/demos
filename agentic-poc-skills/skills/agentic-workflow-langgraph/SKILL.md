---
name: "agentic-workflow-langgraph"
description: "Author and modify a LangGraph agentic workflow: graph wiring, node contract, shared typed state, checkpoints and conditional edges. Use when adding, reordering or debugging a workflow node."
---

## When to use

Use whenever a task adds, changes, reorders or debugs a node in the LangGraph workflow, or changes the shared workflow state.

> **Adapt:** record your project's canonical node sequence in the project's domain skill or constitution and reference it here. Everything below is domain-independent.

## One graph

Exactly one compiled graph exists for the application. Do not create a second graph, and do not bypass the graph with ad-hoc service calls from the API layer. A capability that is worth showing to a user is worth being a node.

## Node contract (non-negotiable)

Every node MUST:

1. Take the shared typed state and return only the keys it owns. Never mutate keys owned by another node.
2. Run inside the audit context manager so that `node_started` and `node_completed` (or `node_failed` with the exception type and message) are emitted with a duration.
3. Write a state checkpoint after it completes, with a monotonically increasing sequence number scoped to the run.
4. Be runnable in isolation against a fixture input with no other node having run, given its required state keys.
5. Delegate file/tool access through the tool-server client and specialist work through the agent-protocol client — never import a specialist agent's implementation directly from a node.

## Shared state

- The state is a `TypedDict`/Pydantic-backed structure whose values are typed models, not loose dicts.
- Add a new key only when no existing key expresses the data; document its owner node in the same change.
- Never place secrets, raw file handles, open connections or unserializable objects in state — checkpoints must serialize to JSON.

## Conditional edges

- Routing functions read a boolean or enum already present in state and must be pure and side-effect free.
- Every conditional branch must terminate at `END`. Avoid cycles unless the project explicitly specifies a bounded retry loop with a max-iteration guard in state.

## Failure handling

- A node that fails records `node_failed` and re-raises; the run is marked failed and earlier checkpoints stay queryable.
- Transport failures (tool server or agent protocol) are **not** node failures: fall back, record the substituted transport, and continue.

## Checklist

- [ ] Node emits start/complete/fail events with duration.
- [ ] Node writes exactly one checkpoint.
- [ ] Node owns a disjoint set of state keys.
- [ ] Graph compiles and every path reaches `END`.
- [ ] A full run succeeds for every fixture, with and without an LLM API key.
