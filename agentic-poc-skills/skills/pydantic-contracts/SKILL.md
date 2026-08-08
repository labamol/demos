---
name: "pydantic-contracts"
description: "Define and evolve Pydantic v2 domain and API models and their TypeScript counterparts. Use when adding or changing any data contract."
---

## When to use

Use when adding or changing any domain object, API request/response, agent payload or persisted artifact shape.

## Rules

- Pydantic v2 models are the single source of truth for every contract. Keep domain models separate from API request/response models; do not expose internal-only fields by reusing a domain model unchanged when the shapes differ.
- Prohibited in application code: `Any`, untyped dicts crossing a module boundary, `getattr`/`setattr` dynamic access, and parsing JSON without validating into a model. If you reach for one of these, you do not yet understand the type — go read it.
- Use enums for every closed set (statuses, stages, levels, event types). Never compare against bare string literals.
- Prefer computed properties for derived values so the derivation lives with the data and cannot drift between callers.
- Use `Field` with descriptions and constraints (`ge`/`le`, `min_length`) for anything user-supplied; validation errors must be actionable.
- `default_factory` for mutable defaults. Timestamps are timezone-aware UTC.
- Percentages: pick 0–100 integers *or* 0–1 floats per field, state it in the field description, and never mix within a model. This is the single most common source of silent factor-of-100 bugs.

## Evolving a contract — all in one change

1. Update the Pydantic model.
2. Update the feature's `contracts/` artifact under `specs/<feature>/`.
3. Update the mirrored TypeScript type in the frontend.
4. Update the DDL if the shape is persisted.
5. Update any fixture/mock data that must still validate.

A contract change without a spec update is a process violation, not a shortcut.

## Checklist

- [ ] Model validates every fixture file.
- [ ] Enums used for all closed sets.
- [ ] Frontend type mirrors the model.
- [ ] No `Any` introduced.
