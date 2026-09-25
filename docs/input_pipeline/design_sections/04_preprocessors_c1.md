## 4. Preprocessors (C1)

One script per legacy source. No shared framework, no plugin registry, no declarative mapping layer — this matches how APS already works and was an explicit design decision. `[CONFIRMED against APS's existing scripts]`

**Conventions**, drawn from APS's own `Load_PLEXOS.py` and `Maintenance.py`:

- Plain `pandas`, under ~100 lines, single purpose.
- Config constants at the top of the file (paths, sheet names, horizon bounds), no CLI argument parsing.
- Reads one source artifact, writes one or more Standard-Format CSVs.
- Idempotent — running twice on the same input produces byte-identical output.

**Two established transformation patterns:**

| Pattern | Source shape | Output | Real example |
|---|---|---|---|
| Melt-on-columns | Wide grid, one column per year/period | Long `Year, Month, Day, Period, value` rows | `Load_PLEXOS.py` (DSM, Embedded_DG, Incremental_DG, DistBATT) |
| Event expansion | Event list with start/end dates | Dense daily mask, one 0/1 column per unit | `Maintenance.py` (outages → daily calendar 2026-01-01 to 2044-12-31) |

Note that `Maintenance.py` does **not** use `t_date_from`/`t_date_to` interval overrides — APS's actual convention is to pre-expand events into a dense timeseries. New outage-type preprocessors should follow that pattern rather than emitting sparse intervals.
