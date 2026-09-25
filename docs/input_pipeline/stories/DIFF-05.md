<!-- Epic intro: docs/input_pipeline/epics/B_comparison_engine.md -->
### DIFF-05 — Data diff: the numbers inside the CSVs

**As** a modeller, **I want** per-value differences with error statistics between the two runs' data files, **so that** "the load changed" comes with a magnitude.

**Type:** Story · **Size:** M · **Traces to:** §10.4 · **Depends on:** DIFF-03, Q1

**Spec**

Wraps Energy Exemplar's `TimeSeriesComparison`. **Import `TimeSeriesComparator` as a class and pass `datahub_manager=None`** rather than shelling out to their script — that skips the DataHub upload side effect entirely and avoids their CLI's mandatory `--cli-path` / `--environment` arguments, which their "local" variant still requires even when every input is local.

Pairing: for each property whose `data_file_path` is the same on both sides, compare the file at that path under each run's tree. For a property whose pointer *changed*, DIFF-03 already reported the swap; the data comparison then runs old file vs new file so the swap comes with a magnitude rather than just a rewiring note.

Returns per pair: MAE, RMSE, correlation, max error, mean bias, plus their gap and anomaly flags.

**Acceptance criteria**

1. **Given** two runs with an identical CSV, **then** MAE and max error are 0 and correlation is 1.
2. **Given** a CSV where one year's values are scaled 1.05×, **then** mean bias is positive and max error matches the largest absolute difference.
3. **Given** the comparator invoked with `datahub_manager=None`, **then** no network call is attempted — assert this, do not assume it.
4. **Given** a CSV present on one side only, **then** it is reported as such rather than raising.
