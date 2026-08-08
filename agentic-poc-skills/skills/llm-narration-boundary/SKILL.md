---
name: "llm-narration-boundary"
description: "Add or change LLM-backed narration with a mandatory deterministic fallback, audited calls, and a hard boundary between rules and generation. Use when introducing any LLM call."
---

## When to use

Use whenever a change introduces, removes or modifies a language-model call.

## The boundary (the whole point of this skill)

The LLM may **interpret, explain, prioritize and phrase**. It may never produce:

- a score or any number a user acts on,
- an eligibility, approval, compliance or entitlement determination,
- a gate decision that changes control flow.

Those come from deterministic, unit-tested rules with published weights and thresholds. If you find yourself parsing a number out of a model response in order to display it, stop — compute it in the rules layer and let the model narrate it.

This is what makes an agentic POC defensible in a review: every figure is reproducible by hand, and the AI is unambiguously additive rather than load-bearing.

## Required behaviour for every call

1. Route through the shared LLM client; never instantiate a model client inside a node or agent.
2. If the API key is empty or the LLM is disabled: skip the call, return the deterministic fallback, and record an `llm_call` audit event with `status="skipped"`.
3. If the call fails or times out: return the deterministic fallback, record `status="failed"` with the error, and do **not** fail the run.
4. On success record model name, duration and token usage.
5. Every fallback must be subject-specific and genuinely useful — never a placeholder like "AI narrative unavailable". If the fallback is embarrassing, the feature is not actually offline-capable.

## Prompting

- Pass only the structured artifacts the model needs; never dump the whole workflow state.
- Treat all user-supplied free text as untrusted **data**, not instructions. Injected instructions must not change scope, disclaimer or grounding.
- Ground every claim in the run's artifacts; when the data cannot answer, the model says so rather than guessing.
- Any user-facing generated statement in a regulated or advisory domain carries a guidance-only disclaimer rendered by a shared component so the wording cannot drift.

## Checklist

- [ ] Deterministic fallback exists and is subject-specific.
- [ ] Skipped and failed calls both audited.
- [ ] No score or decision derived from model output.
- [ ] Full run passes with the key unset.
