<!-- Epic intro: docs/input_pipeline/epics/D_sources_workbook.md -->
### WBK-02 — Data sheet reader

**As** the build, **I want** one row per source file saying where its values belong in PLEXOS, **so that** mapping needs no code.

**Type:** Story · **Size:** S · **Traces to:** §6.2 · **Depends on:** WBK-04, WBK-01 · **Q8 answered:** class + collection is always enough to disambiguate a property. The four name columns are a complete key.

**Spec**

| Column | Required | Meaning |
|---|---|---|
| `source_path` | Yes | Path to the Standard-Format file, **relative to `source_root`**. Preprocessor output and filled-in template are treated identically. |
| `target_class` | Yes | PLEXOS class name, e.g. `Generator` |
| `target_collection` | Yes | PLEXOS collection name, e.g. `Generators` |
| `target_property` | Yes | PLEXOS property name, e.g. `Max Capacity` |
| `target_object` | Conditional | Populated for single-object files, blank for wide (§3.2 / FMT-02) |
| `target_folder` | No | Where the CSV goes inside the data-file tree. Blank → `APS_Inputs` (WRT-03, Q6) |
| `notes` | No | Free text, ignored by the build |

Class, collection and property are **plain names**, resolved against the live model at build time using the same lookup pattern EE's own `ReplaceModelInputFiles` uses. Numeric IDs never appear in the interface.

**Deliberately absent, and each absence is a decision:** no format or granularity column (§3.1 — self-describing); no run-selection sheet (every row is always active); no source registry; no object or property catalog (existence is validated against the live model itself).

**Not on the sheet but present in the internal signature:** `band_id` and `scenario_tag`, defaulting to band 1 and the build's own scenario. The general rule — **full signature internally, minimal surface on the sheet** — makes adding a column later an additive change rather than a rebuild.

**Acceptance criteria**

1. **Given** the example workbook's ten rows, **then** ten `SourceRow` objects are returned with fields as typed.
1b. **Given** a blank `target_folder`, **then** it resolves to `APS_Inputs` rather than to `None` — the default is applied at read time so nothing downstream has to know it.
2. **Given** a row missing `target_property`, **then** an error naming the sheet row number.
3. **Given** a blank row in the middle of the table, **then** it is skipped, not read as a row of empty strings.
4. **Given** a row whose `notes` contains a comma and a line break, **then** it is read intact and ignored by the build.
5. **Given** trailing whitespace on `target_class`, **then** it is trimmed — an invisible space must not produce "class not found".
