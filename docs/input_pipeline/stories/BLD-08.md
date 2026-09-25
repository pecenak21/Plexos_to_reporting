<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-08 — Exception and assumption ledger

**As** a modeller reviewing a run that completed without interruption, **I want** every decision the build made for itself, **so that** "it ran clean" is something I can check rather than trust.

**Type:** Story · **Size:** M · **Traces to:** deliverable §"The build report" · **Depends on:** BLD-04 · **[LATE]**

**Spec**

A structured ledger collected through the run and handed to **the build report** (RPT-01, section 3) — not to the diff workbook, which by §2.1 is precisely where this content would be invisible.

Each entry: category, what the build met, what it did, why, and where (object / property / file / sheet row).

**Categories, each one a real case:**

| Category | Example entry |
|---|---|
| Read Order chosen | *Set scenario `Automated Inputs` Read Order to 2001; highest existing on model `TA_Base2_ST` was 2000.* |
| Variable carried across | *Copied `Battery Derate` from the existing link onto the new link for `Max Power` on 14 batteries. Whether it should apply to the new data is a modelling question — see Q10.* |
| Data file placement | *Placed `hr_Load_2026Q1_LRF.csv` at `TimeSeries\Region\` — new Data File object, no existing path to preserve.* |
| Existing data file reused | *Overwrote `TimeSeries\Generator\hr_RenewableProfile.csv` in place; link unchanged.* |
| Diff skipped | *No `compare_to` and source model not from a run folder. First-run case.* |
| Override applied | *`run_name` taken from `--run-name` (`CWP 12212026`); sheet said `CWP 12202026`.* |
| Warning carried | *Checkpoint-1 warning: `An_CoalPrice.csv` has one data column and blank `target_object` — read as single-object.* |

**This is the "the run must go on" half of the standing rule made auditable.** The build does not stop when it meets a condition it can resolve on its own; the ledger is what stops that from being the same as hiding it. A run that completed without interruption can still be reviewed for the decisions behind it.

**Acceptance criteria**

1. **Given** a build that resolves a Read Order, carries a variable and places a new file, **then** all three appear as ledger entries with object and property named.
2. **Given** a build with nothing to resolve, **then** the ledger is empty and the report says so explicitly rather than omitting the section.
3. **Given** any ledger entry, **then** it names a location specific enough to navigate to — an object name, a file path or a sheet cell.
4. **Given** a build that failed, **then** the ledger up to the failure point is still written.
