<!-- Epic intro: docs/input_pipeline/epics/D_sources_workbook.md -->
### WBK-06 — CLI overrides for run settings

**As** anyone scripting a build, **I want** to override Run sheet values from the command line, **so that** the workbook is not the only way in.

**Type:** Story · **Size:** S · **Traces to:** §6.1.1 · **Depends on:** WBK-01 · **Q2 answered:** the workbook runs everything. This story is a convenience on top of the sheet, not a second interface — see §2.2.

**Spec**

**Read §2.2 first.** Q2 settled that the workbook runs everything and is the source of truth. This story is a convenience on top of the sheet, not a second way in — **no option may exist only here**, and a new setting gets its Run sheet cell before it gets a flag.

Every Run sheet setting has a matching flag: `--run-name`, `--output-root`, `--source-model`, `--source-timeseries`, `--target-model`, `--compare-to`, `--source-root`, `--scenario-name`. CLI wins over the sheet.

**Two things are CLI-only and must never become cells:**

- `--force`, which permits writing into an existing run folder. A destructive action must not be something someone can leave switched on from last time.
- `--dry-run`, which runs pre-flight and both validation checkpoints and then stops without creating anything.

**The provenance cost of overrides, which must be handled and not just noted.** The archived workbook is meant to be a complete record of what produced a run (§12), and Q2 makes that its primary job. An override makes the archived sheet a lie about its own run. So: **every override is recorded in the build report's run header**, showing the sheet value beside the value actually used. Under §2.1 this is not optional housekeeping — an override is invisible to every diff level, so if the report does not say it, nothing does.

**Acceptance criteria**

1. **Given** `--run-name X` and `run_name = Y` on the sheet, **then** the run folder is `X`.
2. **Given** any override, **then** the build report names the setting, the sheet value and the used value.
3. **Given** `--force` present in the workbook as a cell, **then** it is rejected as an unknown key (WBK-01 case 4).
4. **Given** `--dry-run`, **then** pre-flight and both checkpoints run, findings are reported, and `output_root` is unchanged on disk.
