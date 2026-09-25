## 1. System overview

One build cycle, start to finish:

```
APS legacy sources ──> preprocessor scripts ──┐
                                              ├──> Standard-Format CSVs ──┐
APS new data ────────> standard templates ────┘                           │
                                                                          ├──> build script ──> new run model
                   Sources workbook (Run + Sources sheets) ───────────────┘                      (.xml + .db + Timeseries/)
                                                                                                        │
                                            prior run archive ─────────────────────────> diff ──────────┤
                                                                                                        │
                                                                                       diff + validation report
```

Everything upstream of the build script converges on a single idea: by the time the build script sees a file, it is in **Standard Format**, and the build script cannot tell whether that file came from a preprocessor or from a template APS filled in by hand. There is one code path, not two.

### 1.1 Components

| # | Component | Form | Owner after handover |
|---|---|---|---|
| C1 | Preprocessor scripts | One Python script per legacy source | APS (extend per new source) |
| C2 | Standard templates | Blank CSV files | APS (fill in per new dataset) |
| C3 | Sources workbook | Excel file — Run, Sources and Compare sheets | APS (edit per run) |
| C4 | Build script | Python, calls `plexos_sdk` | Utilicast → APS |
| C5 | Validation | Python, two checkpoints inside C4 | Utilicast → APS |
| C6 | CDM views | SQL views over the run `.db` | Utilicast → APS |
| C7 | Diff tool | Python + DuckDB, standalone and build-triggered | Utilicast → APS |
| C8 | Report generator | Python, consumes C5 + C7 | Utilicast → APS |
