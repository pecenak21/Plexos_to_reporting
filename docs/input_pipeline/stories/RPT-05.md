<!-- Epic intro: docs/input_pipeline/epics/H_reporting_the_build_repo.md -->
### RPT-05 — Diff report for a standalone comparison

**As** a modeller comparing two arbitrary models, **I want** the same workbook shape, **so that** there is one thing to learn.

**Type:** Story · **Size:** S · **Traces to:** §6.6, §10 · **Depends on:** RPT-02, DIFF-07

**Spec**

The same workbook as RPT-02 and RPT-03. There is **no build report** for a standalone comparison — nothing was built, so there are no decisions to record — and the workbook's header says so, rather than leaving a modeller looking for a file that does not exist.

The header names both sides, states that **`model_1` is always the baseline**, and states that reversing the two reverses the report.

Written to `output_report_path`, defaulting to `<output_root>\Comparisons\`, named for both sides and the date. **Never into either compared folder** — a standalone comparison owns neither side, and writing into one would be editing an archived record after the fact.

**Acceptance criteria**

1. **Given** a standalone comparison, **then** the workbook holds the four detail sheets and its header states that no build report accompanies it.
2. **Given** the default output path, **then** the file lands in `Comparisons\` named for both sides and the date.
3. **Given** a comparison run in both directions, **then** the two reports are mirror images.
4. **Given** any standalone comparison, **then** nothing is written inside either compared folder — assert it.
