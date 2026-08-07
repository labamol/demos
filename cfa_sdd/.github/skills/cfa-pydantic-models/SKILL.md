---
name: "cfa-pydantic-models"
description: "Define and evolve Pydantic v2 domain and API models and their TypeScript counterparts. Use when adding or changing any data contract."
---

## When to use

Use when adding or changing any domain object, API request/response, agent payload or persisted artifact shape.

## Rules

- Pydantic v2 models are the single source of truth for every contract. Domain models live separately from API request/response models; do not expose internal-only fields through the API layer by reusing a domain model unchanged when the shapes differ.
- Prohibited in application code: `Any`, `dict[str, object]` crossing a module boundary, `getattr`/`setattr` dynamic access, and parsing JSON without validating into a model.
- Use enums for every closed set (lifecycle stage, exam level, exam status, requirement status, reference status, audit event type). Never compare against bare string literals.
- Prefer computed properties for derived values (passed levels, total qualifying months, completion percentage) so the derivation lives with the data and cannot drift between callers.
- Use `Field` with descriptions and constraints (ge/le, min_length) for anything user-supplied; validation errors must be actionable.
- Defaults: use `default_factory` for mutable defaults. Timestamps are timezone-aware UTC.
- Money/percentages: percentages are 0–100 integers or 0–1 floats — pick one per field and state it in the field description; never mix within a model.

## Evolving a contract

1. Update the Pydantic model.
2. Update the feature's `contracts/` artifact in `specs/<feature>/`.
3. Update the mirrored TypeScript type in the frontend.
4. Update the DDL if the shape is persisted.
5. Update any mock data files that must still validate.

All five happen in the same change. A contract change without a spec update violates the constitution.

## Checklist

- [ ] Model validates every mock data file.
- [ ] Enums used for all closed sets.
- [ ] Frontend type mirrors the model.
- [ ] No `Any` introduced.
