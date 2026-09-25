<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-02 — Load forecast

**As** the pipeline, **I want** `LOAD MultiYear_26LRF_Rev1.xlsx` converted to Standard Format, **so that** hourly regional load feeds `Region.Load`.

**Type:** Story · **Size:** M · **Traces to:** §4 · **Depends on:** PRE-01

**Spec**

Melt-on-columns, following APS's existing `Load_PLEXOS.py`. Output: hourly, wide, one column per region. The model held eight `Region` objects when queried during design — `APS`, `Four Corners`, `Market`, `Metro`, `New Mexico`, `Northern`, `Palo Verde`, `Pinal` — but the script resolves the set from the model rather than hard-coding it. (Note `Market` is both a region name and a tree subfolder name; they are unrelated.) Handles the DSM / Embedded_DG / Incremental_DG / DistBATT components the existing script already handles.

**Acceptance criteria**

1. **Given** the real workbook, **then** an hourly Standard-Format CSV is produced with one column per region.
2. **Given** the output, **then** every column header exactly matches a `Region` object name in the model (VAL-02 would otherwise fail the build).
3. **Given** the output, **then** it spans the full model horizon — VAL-05 is the check that would otherwise stop the build, and the preprocessor is where the shortfall should be noticed first.
4. **Given** the existing `Load_PLEXOS.py` output for the same input, **then** values match.
