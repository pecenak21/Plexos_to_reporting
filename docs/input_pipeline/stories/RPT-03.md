<!-- Epic intro: docs/input_pipeline/epics/H_reporting_the_build_repo.md -->
### RPT-03 — Diff report: detail pages, one per level

**As** a modeller, **I want** each level's differences listed in full, **so that** a headline count can be opened up.

**Type:** Story · **Size:** M · **Traces to:** §11, §10.4 · **Depends on:** RPT-02, DIFF-02 … DIFF-05

**Spec**

Each sheet is a flat table, one row per difference, with the natural key spelled out in columns so it can be filtered and pivoted.

| Sheet | Key columns | Payload columns | Produced by |
|---|---|---|---|
| Source files | file path | status, old hash, new hash | Ours — no EE tooling exists |
| Structure | parent class, parent object, collection, child class, child object | change type | Ours — `v_membership` + the object diff |
| Assignments | + property, band, scenario, date from, date to | old value, new value, old data file, new data file, change type | Ours — `v_property` |
| Data | property, object, time key | old value, new value, difference, % difference | EE `TimeSeriesComparison` |

**The Assignments sheet carries the most weight and is the one a modeller should be pointed at first.** A Datafile pointer swapped to a different CSV — the most common change this pipeline produces — touches no `t_membership` row at all, so the Structure sheet reports nothing for it. Without this level the most routine kind of change in the whole process would be invisible.

The Data sheet carries the per-property statistics from DIFF-05 (MAE, RMSE, correlation, max error, mean bias) in a small block above the detail rows — the example workbook shows the shape.

**Acceptance criteria**

1. **Given** a run that re-pointed one property, **then** the Assignments sheet has one row naming both CSVs and the Structure sheet is empty with its note.
2. **Given** a level with more rows than Excel comfortably holds, **then** the sheet is truncated with an explicit count of what was omitted and a pointer to the full CSV written beside the workbook — never silently cut.
3. **Given** every sheet, **then** the natural key columns are present and sortable.
4. **Given** the Data sheet, **then** per-property statistics appear above the detail rows.
