---
name: "<project>-domain"
description: "<Domain> reference: lifecycle stages, entities, scoring constants, personas and the advisory boundary. Use when a task needs domain grounding."
---

<!--
  This is the ONE skill you must write from scratch per project. The nine skills in
  ../skills/ are domain-neutral; this file is where all the domain specificity lives,
  so that the others never need editing.

  Delete every instruction comment before shipping.
-->

## When to use

Use when a task needs grounding in the <domain> domain: naming, entity semantics, scoring
constants or the fixture personas.

## Lifecycle

<!--
  The journey the subject travels through, in stages, in the domain's own vocabulary.
  Name each stage exactly as the code and the UI will name it.
-->

**<Stage A>**: step -> step -> step.

**<Stage B>**: step -> step -> step.

**Transition opportunities** (what the POC actually targets): <the specific gaps between stages
that the product improves>.

## Entities and requirement categories

<!--
  The closed sets. Every one of these becomes an enum. State the status vocabulary explicitly,
  and be explicit about how "pending" is treated — ambiguity here causes scoring bugs.
-->

`<category_1>`, `<category_2>`, ... Each has a status of <met | pending | not met>. Pending is
never treated as met.

## Scoring constants

<!--
  Every number the product shows a user must appear here, in one place, with its weight.
  If a reviewer cannot reproduce a displayed score by hand from this table, the table is wrong.
-->

| Category | Weight |
| --- | --- |
| `<category_1>` | 0.00 |
| `<category_2>` | 0.00 |

Weights must sum to 1. Other constants: `<REQUIRED_X> = n`, `<THRESHOLD_Y> = n`.

Score = round(sum(category_completion x weight) x 100), each completion capped at 1.0.

## Classification rules

<!--
  If the product classifies free text (activities, claims, tickets), publish the keyword or rule
  sets here so they are reviewable, and state the escalation policy for ambiguous cases.
-->

Likely `<positive class>`: <terms>.

Likely `<negative class>`: <terms>.

Ambiguous cases are escalated to a human reviewer rather than given a confident verdict.

## Fixture personas

<!--
  The synthetic subjects used for every demo and test. Include the expected headline metric per
  persona so a regression is obvious at a glance.
-->

| Persona | Stage | Situation | Expected score |
| --- | --- | --- | --- |
| <name> | <stage> | <one line> | ~n |

## The advisory boundary

<!--
  State plainly what determination the system must never make. Every domain with a regulator,
  an approval body or a professional standard needs this paragraph.
-->

The POC never issues an official <eligibility / approval / compliance> determination. Every
such surface carries a guidance-only disclaimer, and a human reviewer is always the final
authority. All data is synthetic.
