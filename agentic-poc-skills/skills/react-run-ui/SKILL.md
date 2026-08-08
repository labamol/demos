---
name: "react-run-ui"
description: "Build a React + TypeScript + Vite client for a run-oriented agentic backend: panels, run lifecycle, error states and API typing. Use when touching the frontend."
---

## When to use

Use for any change to the React client of a run-oriented agentic application.

> **Adapt:** the panel/tab set is project-specific; the lifecycle rules below are not.

## Structure

**A single run drives every panel.** One component per panel; the app shell owns run state and passes typed props down. An audit panel that exposes the run's event trail is worth building even for a POC — it is the cheapest possible demo of trustworthiness.

## Rules

- TypeScript strict. Types mirroring the backend models live in one module and are the only shapes crossing the API boundary; no `any`, no inline structural types for API payloads.
- **Never render two panels from different runs.** If a new run starts, all panels update together. Mixed-run rendering produces contradictions the user will notice before you do.
- Every asynchronous action has three visible states: loading, error, empty. An empty result renders an explanatory empty state, not a blank panel.
- Surface API error messages; never swallow a failure into an empty panel.
- The API base URL comes from `import.meta.env.VITE_API_BASE` with a sane default; declare it in `src/vite-env.d.ts` or the strict build fails on `ImportMeta.env`.
- Repeated disclaimers/legal text render through a shared component so the wording cannot drift between panels.
- Mutations (toggles, edits) update optimistically but reconcile with the server response and revert on failure.

## Checklist

- [ ] `npm run build` passes (type-check included).
- [ ] Loading, error and empty states exist for every new async surface.
- [ ] New API shape added to the shared types module.
- [ ] No panel can display data from a stale run.
