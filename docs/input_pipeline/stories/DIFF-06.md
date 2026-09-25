<!-- Epic intro: docs/input_pipeline/epics/B_comparison_engine.md -->
### DIFF-06 — Diff regression harness

**As** the build team, **I want** the diff proven on a model we broke on purpose, **so that** "nothing changed" means nothing changed.

**Type:** Chore · **Size:** M · **Traces to:** §14 phase 2 · **Depends on:** DIFF-02, DIFF-03

**Why this is a story and not a test file.** This harness is the cheapest correctness check available for the entire pipeline, and it exists before the write path does. A diff that can prove zero differences on an unmodified model is what makes every later story's acceptance test meaningful.

**Spec**

A fixture generator that takes APS's real model and produces mutated copies, one mutation each: add an object; remove an object; rename an object; change a scalar value; re-point a data file; add a scenario tag; change a date window; change a band. Each mutation records its own expected diff. The harness asserts the diff reports **exactly** that and nothing else.

**Acceptance criteria**

1. **Given** the unmutated model against itself, **then** zero differences at every level.
2. **Given** each mutation, **then** the diff reports exactly the expected change set — no extra rows, no missing rows.
3. **Given** the `.db` regenerated twice from the same `.xml`, **then** zero differences — the surrogate-key guard.
4. The harness runs in CI on every change to `v_property`, `v_membership`, or the diff SQL.
