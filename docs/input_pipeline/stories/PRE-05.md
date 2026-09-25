<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-05 — Coal price

**As** the pipeline, **I want** `CoalDispFuelPricing_2026_Rev1_260817Calcs.csv` converted, **so that** annual coal price feeds `Fuel.Price`.

**Type:** Story · **Size:** S · **Traces to:** §4 · **Depends on:** PRE-01

**Spec**

Annual. This is the single-object case from the example workbook — `target_object = CH13_Coal` — so the output has one data column and its header is ignored by the build. It will raise checkpoint 1's rule-6 warning by design if `target_object` is ever left blank, which is exactly the case that warning exists for.

**Acceptance criteria**

1. **Given** the real CSV, **then** an annual Standard-Format CSV with `Year` and one value column.
2. **Given** the Data sheet row with `target_object = CH13_Coal`, **then** the pair validates cleanly through checkpoints 1 and 2.
3. **Given** the same row with `target_object` blank, **then** the rule-6 warning fires and names both readings.
