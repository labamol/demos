---
name: "cfa-react-ui"
description: "Build or change the React 18 + TypeScript + Vite client: panels, run lifecycle, error states and API typing. Use when touching the frontend."
---

## When to use

Use for any change to the React client.

## Structure

A single run drives every panel. Tabs: `dashboard`, `readiness`, `experience`, `plan`, `recommendations`, `audit`. One component per panel; the app shell owns run state and passes typed props down.

## Rules

- TypeScript strict. Types mirroring backend Pydantic models live in one module and are the only shapes crossing the API boundary; no `any`, no inline structural types for API payloads.
- Never render two panels from different runs. If a new run starts, all panels update together.
- Every asynchronous action has three visible states: loading, error, empty. An empty result renders an explanatory empty state, not a blank panel.
- Errors from the API are surfaced with their message; never swallow a failure into an empty panel.
- The API base URL comes from `import.meta.env.VITE_API_BASE` with a sane default; `src/vite-env.d.ts` must declare it.
- Disclaimers on eligibility-related figures are rendered by a shared component so the wording cannot drift.
- Action-plan toggles update optimistically but reconcile with the server response and revert on failure.

## Checklist

- [ ] `npm run build` passes (type-check included).
- [ ] Loading, error and empty states exist for every new async surface.
- [ ] New API shape added to the shared types module.
- [ ] No panel can display data from a stale run.
