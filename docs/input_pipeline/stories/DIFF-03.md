<!-- Epic intro: docs/input_pipeline/epics/B_comparison_engine.md -->
### DIFF-03 — Assignment diff: property values and data-file pointers

**As** a modeller, **I want** to see every property whose value, data file or window changed, **so that** the most common change this pipeline makes is visible at all.

**Type:** Story · **Size:** M · **Traces to:** §10.2, §10.3 · **Depends on:** CDM-05, DIFF-01

**Why this level carries the most weight.** When a property is re-pointed at an updated CSV — by far the most common change this pipeline produces — the model's *structure* is untouched. A membership-level comparison reports nothing at all. Without this level the routine case is invisible. This story is not optional and should not be deferred behind DIFF-02.

**Spec**

FULL OUTER JOIN `old.v_property` to `new.v_property` USING the natural key:

```
(parent_class, parent_object, collection, child_class, child_object,
 property, band_id, scenario, date_from, date_to)
```

Compared payload once matched: `value`, `data_file_path`, `data_file_object`.

Emit rows where either side is `NULL` (`added` / `removed`) or any payload column `IS DISTINCT FROM` its counterpart (`changed`). `IS DISTINCT FROM`, not `<>` — `NULL <> NULL` is `NULL` and would drop exactly the rows where a data file appeared or disappeared.

This reuses the identity definition `plexos_sdk` itself applies for duplicate detection (§7.4): one rule, used for writing and for diffing.

**Acceptance criteria**

1. **Given** a model compared against itself, **then** zero assignment differences.
2. **Given** a copy in which one property is re-pointed from `hr_A.csv` to `hr_B.csv`, **then** exactly one `changed` row appears, naming both paths, and DIFF-02 reports nothing for it.
3. **Given** a copy in which a scalar value changed, **then** one `changed` row with old and new values.
4. **Given** a copy in which a property gained a scenario tag, **then** one removal and one addition (the scenario is part of the key) — and this is documented as expected, not a bug.
5. **Given** a property that had a data file and now has `NULL`, **then** it is reported — the `IS DISTINCT FROM` case.
6. **Given** APS's real model against a regenerated copy of itself, **then** zero rows. This is the regression test that proves surrogate keys are excluded.
