# Build progress

Status values: `Todo` · `Ready` · `In progress` · `Blocked: <why>` · `Done` · `Exists` (already in the codebase, verified against the acceptance criteria) · `Partial` (exists, gaps listed in Notes).

A story is `Done` only when its acceptance criteria are covered by automated tests **and** those tests have run against a real APS artifact (see docs/input_pipeline/00_conventions_and_answers.md, Definition of Done). If the real artifact is not available, the status is `Blocked: needs real artifact`, not `Done`.

Update this file in the same commit that changes a story's status. Fill the `Existing code / notes` column during the orient session (`/orient`).

| ID | Title | Type | Size | Sprint | Depends on | Status | Existing code / notes |
|---|---|---|---|---|---|---|---|
| OPS-01 | Repo, dependencies and environment check | Chore | M | 1 | — | Todo | No `check_environment` exists. `requirements/requirements.txt` only pins `duckdb`/`numpy`/`pandas`, and its numpy/pandas pins (2.5.1/3.0.3) don't match what's actually installed in `py312` (1.26.4/2.2.2). `pytest`, `ruff`, `openpyxl`, `eecloud` are already installed on this machine but unpinned anywhere. **`plexos_sdk` is not installed** (confirmed: `ModuleNotFoundError`, no `class PLEXOSSDK` anywhere in `site-packages`) — blocks CDM-01 onward until resolved. Cloud CLI (`plexos-cloud.exe`) is installed at `C:\Users\cto\AppData\Local\Programs\PLEXOS.Cloud\` and on PATH, but `cloud_cli_path` env var is unset and `src/convert_zip_to_parquet.py`'s fallback search dirs don't include the real install path. See CODEBASE_MAP.md §1, §4. |
| CDM-01 | Generate a queryable `.db` from a model `.xml` | Story | S | 1 | OPS-01 | Todo | No `ensure_db` exists. Reusable subprocess idiom for shelling out to the Cloud CLI (list-args, `check=True`, `capture_output=True`, pass `e.stderr` through verbatim) at `src/convert_zip_to_parquet.py:100-111`. Blocked on `plexos_sdk` not being installed (see OPS-01). |
| CDM-02 | Read a `.db` through DuckDB, read-only | Chore | S | 1 | CDM-01 | Todo | No ATTACH/read-only pattern exists. `src/database.py` is the anti-pattern CLAUDE.md warns against: module-level default `duckdb` connection + global `_db_initialized` flag (`database.py:16-36`) and an unbounded `lru_cache` (`database.py:39-46`) — and it only ever reads solution-Parquet schema (`mem_fki`/`mem_period`/`v_data`), never a model `.db`. Do not start from this file. |
| CDM-03 | Verify the `t_tag` / `t_text` / `t_membership` joins | Spike | M | 1 | CDM-02 | Todo | Nothing in `src/` touches `t_object`/`t_membership`/`t_data` schema — different schema entirely from the solution-output Parquet the reporting engine reads. |
| CDM-04 | `v_membership` view | Story | S | 1 | CDM-03 | Todo | |
| CDM-05 | `v_property` view | Story | M | 1 | CDM-03 | Todo | |
| CDM-06 | Stored data-file paths | Story | S | 2 | CDM-05 | Todo | |
| CDM-07 | Scenarios, Read Order, model attachment | Story | M | 2 | CDM-05 | Todo | |
| CDM-08 | Run horizon | Story | S | 2 | CDM-05 | Todo | |
| DIFF-01 | `compare()` engine and folder→model resolution | Story | M | 2 | CDM-01, CDM-02 | Todo | |
| DIFF-02 | Structural diff | Story | S | 2 | CDM-04, DIFF-01 | Todo | |
| DIFF-03 | Assignment diff | Story | M | 2 | CDM-05, DIFF-01 | Todo | |
| DIFF-04 | Source-file diff | Story | S | 8 | BLD-06 | Todo | |
| DIFF-05 | Data diff via `TimeSeriesComparison` | Story | M | 8 | DIFF-03 | Todo | |
| DIFF-06 | Diff regression harness | Chore | M | 2 | DIFF-02, DIFF-03 | Todo | |
| DIFF-07 | Standalone entry point | Story | S | 8 | DIFF-01, WBK-03 | Todo | |
| FMT-01 | Standard Format reader | Story | M | 3 | OPS-01 | Todo | No Standard Format / granularity-inference code exists anywhere in `src/`. |
| FMT-02 | Shape from `target_object` | Story | S | 3 | FMT-01, WBK-02 | Todo | |
| FMT-03 | Checkpoint 1 | Story | M | 3 | FMT-01, FMT-02 | Todo | |
| FMT-04 | Standard-Format writer | Story | S | 3 | FMT-01 | Todo | `transformers.py:501+` (`export_block_to_csv`) is a hand-rolled `csv.writer` idiom, but for a different shape (report pivot blocks, not `Year[,Month[,Day[,Period]]]` + data columns) — style reference only, not reusable code. |
| FMT-05 | Blank templates | Story | S | 3 | FMT-04 | Todo | |
| WBK-01 | Run sheet reader | Story | S | 3 | OPS-01, WBK-04 | Todo | No Run/Data/Compare sheet reading exists, but `create_reports.py:load_excel_config` (esp. lines 49-54, the `Summary` sheet read via `pd.read_excel(xl, 'Summary', index_col=0)` then `.loc[key,'Value']`) is a directly relevant key/value-sheet idiom to adapt for `RunConfig`, plus the header-normalization pattern (`.str.strip().str.title()`) at lines 19, 32. Schema itself shares no fields. |
| WBK-02 | Data sheet reader | Story | S | 3 | WBK-01, WBK-04 | Todo | Same Excel-reading idiom as WBK-01 applies (`create_reports.py:40-46` for a row-shaped sheet with list-parsing, e.g. `Groups`/`Assets`). |
| WBK-03 | Compare sheet reader | Story | S | 3 | WBK-01, WBK-04 | Todo | Same idiom as WBK-01/02. |
| WBK-04 | Reconcile the workbook schema | Chore | S | 3, first | — | Todo | Pure documentation reconciliation; no code to check against. |
| WBK-05 | Workbook validation and error reporting | Story | M | 4 | FMT-01, WBK-01, WBK-02, WBK-03 | Todo | No direct `openpyxl` usage exists anywhere in `src/` (pandas uses it only implicitly as the `.xlsx` engine) — no cell-level access/error-reporting precedent to reuse. `exceptions_report.py`'s severity/record pattern (see BLD-08 note) is the closest reusable shape for surfacing validation errors. |
| WBK-06 | CLI overrides | Story | S | 4 | WBK-01 | Todo | `src/testing_pleoxs_input.py:34-37` shows the repo's one `argparse` precedent (a single `--input-path` flag on a scratch job-worker script) — thin, but confirms no CLI framework is already chosen. |
| BLD-01 | Pre-flight checks | Story | M | 4 | CDM-06, WBK-05 | Todo | |
| BLD-02 | Create the run folder | Story | S | 4 | BLD-01 | Todo | |
| BLD-03 | Copy model and tree forward | Story | M | 4 | BLD-02, CDM-06 | Todo | `convert_zip_to_parquet.py:66-98`'s "already-converted dir short-circuits, partial one is rebuilt" `shutil`/`Path` logic is loose precedent for directory-tree handling, but the input pipeline's rule (always regenerate, force by default) is the opposite of that function's "skip if present" behavior — do not copy the skip logic. |
| BLD-04 | Build driver | Story | L | 7 | BLD-01, VAL-01, WRT-01 | Todo | |
| BLD-05 | Post-build path re-check | Story | S | 4 | BLD-03, BLD-04, CDM-06 | Todo | |
| BLD-06 | Archive workbook and source files | Story | S | 8 | BLD-02 | Todo | |
| BLD-07 | Orphan data-file count | Story | S | 4 | BLD-03, CDM-06 | Todo | |
| BLD-08 | Exception and assumption ledger | Story | M | 7 | BLD-04 | Todo | No build-time exception ledger exists, but `exceptions_report.py` (full file) is a solid reusable *shape*: severities (`ERROR`/`WARN`/`INFO`), de-duplication-with-occurrence-count, `record()`/`reset()`/`write()` API. Would need its module-level `_entries` global replaced with an instance passed through the build (per CLAUDE.md's no-global-state guidance) rather than copied as-is. |
| WRT-01 | Resolve class / collection / property / object | Story | M | 5 | CDM-05, WBK-02 | Todo | Only a dead, never-run one-line scratch import exists (`src/from plexos_sdk import PLEXOSSDK.py`) — no real `plexos_sdk` usage anywhere, and the package isn't installed in `py312` (see OPS-01). |
| WRT-02 | Ensure the Data File object exists | Story | S | 5 | WRT-01 | Todo | Same `plexos_sdk` gap as WRT-01. |
| WRT-03 | Where a file lands in the tree | Story | M | 5 | BLD-03, WRT-02 | Todo | |
| WRT-04 | Write one Data sheet row | Story | L | 5 | FMT-02, WRT-01, WRT-02, WRT-03 | Todo | |
| WRT-05 | Create and clear the build's scenario | Story | M | 6 | CDM-07, WRT-04 | Todo | |
| WRT-06 | Read Order: max + 1 | Story | M | 6 | CDM-07, WRT-05 | Todo | |
| WRT-07 | The second link | Story | L | 6 | WRT-04, WRT-05, WRT-06 | Todo | |
| WRT-08 | Carry conditional variables across | Story | M | 6 | WRT-07 | Todo | |
| WRT-09 | Idempotency | Story | M | 6 | DIFF-03, WRT-04, WRT-08 | Todo | |
| WRT-10 | `remove_property` removal scope | Spike | S | 5 | WRT-04 | Todo | |
| WRT-11 | Batch write path and performance | Spike | S | 6 | WRT-04 | Todo | |
| VAL-01 | Targets resolve to one match | Story | S | 7 | WRT-01 | Todo | |
| VAL-02 | Named objects exist | Story | S | 7 | FMT-02, VAL-01 | Todo | |
| VAL-03 | Overlapping coverage | Story | S | 7 | VAL-02 | Todo | |
| VAL-04 | Coverage completeness | Story | S | 7 | VAL-02 | Todo | |
| VAL-05 | Horizon coverage | Story | M | 7 | CDM-08, FMT-01 | Todo | |
| VAL-06 | `sdk.validate()` | Story | S | 7 | WRT-04 | Todo | |
| RPT-01 | Build report (flat) | Story | M | 8 | BLD-08, VAL-01, VAL-06 | Todo | No flat build-report writer exists; `exceptions_report.py`'s write-a-log-at-end-of-run pattern is loose precedent for structure, not content. |
| RPT-02 | Diff report workbook: summary sheet | Story | M | 8 | DIFF-01 | Todo | No `openpyxl` workbook-*writing* code exists anywhere in `src/` (the reporting engine only ever writes CSV) — no summary/detail multi-sheet precedent to reuse. |
| RPT-03 | Diff report: detail pages per level | Story | M | 8 | DIFF-02, DIFF-05, RPT-02 | Todo | Same gap as RPT-02. |
| RPT-04 | Threshold and completeness rule | Story | S | 8 | RPT-03 | Todo | |
| RPT-05 | Diff report for a standalone comparison | Story | S | 8 | DIFF-07, RPT-02 | Todo | |
| PRE-01 | Preprocessor conventions and harness | Chore | M | 9 | FMT-03, FMT-04 | Todo | No legacy-source parsing code exists — the reporting engine consumes PLEXOS solution output, never raw APS `.xlsm`/`.xls`/`.xlsx` sources. |
| PRE-02 | Load forecast | Story | M | 9 | PRE-01 | Todo | |
| PRE-03 | Gas price | Story | S | 9 | PRE-01 | Todo | |
| PRE-04 | Power price with nodal aggregation | Story | M | 9 | PRE-01 | Todo | |
| PRE-05 | Coal price | Story | S | 9 | PRE-01 | Todo | |
| PRE-06 | Outages to daily mask | Story | M | 9 | PRE-01 | Todo | |
| PRE-07 | VER profiles | Story | M | 9 | PRE-01 | Todo | |
| OPS-02 | CLI entry points | Chore | S | 9 | BLD-04, DIFF-07 | Todo | No CLI framework chosen anywhere in the repo beyond one thin `argparse` scratch example (see WBK-06 note). |
| OPS-03 | Logging | Chore | S | 9 | BLD-04 | Todo | No logging module used anywhere in `src/` — all diagnostics are `print()` with hand-rolled prefixes (`[+]`/`[-]`/`[!]`). Establish a real logging convention fresh; nothing to reuse. |
| OPS-04 | Handover runbook | Chore | M | 9 | — | Todo | |
