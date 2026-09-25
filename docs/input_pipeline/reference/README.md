# Reference material

The design docs cite these, and they were not in the document set. Claude Code will invent `plexos_sdk` method signatures if it does not have them.

## Probably already on this machine

`C:\Users\cto\PLEXOS-Cloud-Automation-Scripts` exists (folders: `Automation`, `Compute`, `Documentation`, `Pre`, `Post`, `Workflows`, `tests`, `pipelines`) and `src/testing_pleoxs_input.py` imports `eecloud` from it. It is very likely the Energy Exemplar scripts repo the design refers to. Give Claude Code read access to it when you start:

```
> /add-dir C:\Users\cto\PLEXOS-Cloud-Automation-Scripts
```

Then have it locate these and record the paths in the table below.

| Item | Why it is needed | Needed by | Path on this machine |
|---|---|---|---|
| `PLEXOS_SDK_Methods.md` (complete documented method list for `plexos_sdk`) | Every write. The design's SDK claims were checked against it. | OPS-01, CDM-01, WRT-01 to WRT-11 | |
| `ReplaceModelInputFiles` script | The name-resolution and remove-then-add pattern the write path copies | WRT-01, WRT-04 | |
| `QueryWriteMemberships` script | Cross-check for `v_membership` | CDM-04 | |
| `TimeSeriesComparison` script | The data-level diff wraps `TimeSeriesComparator` | DIFF-05 | |
| APS's `Load_PLEXOS.py` and `Maintenance.py` | Preprocessor conventions and the two transformation patterns | PRE-01 to PRE-07 | In `docs/sample model/TimeSeries/` (see below) |
| `Task2_D3_Problem_Definition.md` | Reasoning behind each decision, for when a rule is challenged | Any | |

If `PLEXOS_SDK_Methods.md` is not in that repo's `Documentation` folder, add it here before sprint 1.

## Sample data in this repo (read-only: copy, never modify)

| What | Where (relative to repo root) | Notes |
|---|---|---|
| The populated model | `docs/sample model/2026 APS_TA V3.1 - Copy.xml` (about 12 MB) | The design's fixture model. Copy to a temp directory before use. |
| Its data-file tree | `docs/sample model/TimeSeries/` (10 category folders, several hundred MB) | Includes real Standard Format files for FMT and VAL tests, for example `Emission/yr_EmissionsPrice.csv` (tiny) and `Generator/An_FOM.csv`. |
| Preprocessor references | `docs/sample model/TimeSeries/Generator/Updated Maintenance/Maintenance.py` and `docs/sample model/TimeSeries/Load Forecasts/2026 Q1/Load_PLEXOS.py` | The APS scripts the design's preprocessor conventions are drawn from (PRE-01 to PRE-07). |
| Raw APS source files | `docs/sample APS source files/` | Coal pricing `.xlsm`, gas price `.xls`, load forecast `.xlsx`, outages `.xlsx`, power price `.xls`, plus a `Gas - Power Prices/` subfolder. Inputs for the preprocessors. |

Do not commit these. Tests that need them should skip cleanly if they are absent. The Cloud CLI executable is found through the `cloud_cli_path` environment variable, as the existing scratch script does.
