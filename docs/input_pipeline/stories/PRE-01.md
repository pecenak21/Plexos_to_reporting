<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-01 — Preprocessor conventions and test harness

**As** whoever writes the next preprocessor, **I want** the conventions written down and a harness that checks them, **so that** ten scripts stay consistent without a framework.

**Type:** Chore · **Size:** M · **Traces to:** §4 · **Depends on:** FMT-03, FMT-04

**Spec**

Conventions, drawn from APS's own scripts:

- Plain `pandas`, under ~100 lines, single purpose.
- Config constants at the top of the file — paths, sheet names, horizon bounds. **No CLI argument parsing.**
- Reads one source artifact, writes one or more Standard-Format CSVs through `write_standard_format` (FMT-04).
- **Idempotent** — running twice on the same input produces byte-identical output. This is what makes DIFF-04 meaningful; a script that re-serialises differently each run would show as changed on every run and train everyone to ignore that level.

Two established transformation patterns, both already in use:

| Pattern | Source shape | Output | Real example |
|---|---|---|---|
| **Melt-on-columns** | Wide grid, one column per year/period | Long `Year, Month, Day, Period, value` rows | `Load_PLEXOS.py` (DSM, Embedded_DG, Incremental_DG, DistBATT) |
| **Event expansion** | Event list with start/end dates | Dense daily mask, one 0/1 column per unit | `Maintenance.py` (outages → daily calendar 2026-01-01 to 2044-12-31) |

**A convention worth stating because it is easy to get wrong:** `Maintenance.py` does **not** use `t_date_from` / `t_date_to` interval overrides. APS's actual convention is to pre-expand events into a dense timeseries. New outage-type preprocessors follow that pattern rather than emitting sparse intervals.

The harness: given a preprocessor and its real source file, run it twice, assert byte-identical output, and run checkpoint 1 over every file it produced.

**Acceptance criteria**

1. **Given** any preprocessor, **when** run twice, **then** byte-identical output.
2. **Given** any preprocessor's output, **then** checkpoint 1 passes it with no errors.
3. **Given** a new preprocessor added to the repo, **then** it is picked up by the harness without registration.
4. The conventions are a document in the repo, not only in this backlog.
