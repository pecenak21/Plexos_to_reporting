<!-- Epic intro: docs/input_pipeline/epics/H_reporting_the_build_repo.md -->
### RPT-02 — Diff report workbook: summary sheet

**As** a modeller, **I want** the first page of the diff to tell me whether anything needs attention, **so that** I can stop there when nothing does.

**Type:** Story · **Size:** M · **Traces to:** §11; Q11 · **Depends on:** DIFF-01 · **Q11 answered:** workbook, summary page then detail pages.

**Spec**

Excel workbook, written to `Inputs\diff_report.xlsx` for a build and to `<output_report_path>` for a standalone comparison (RPT-05).

**Sheet 1 — Summary:**

- **Header:** the two sides being compared, which is the baseline, and when the comparison ran. For a build, the run name and its baseline run; for a standalone comparison, the two folder paths.
- **Headline counts**, one row per level: source files changed; objects added / removed; memberships added / removed; property records added / removed / changed; data files whose values changed.
- **A pointer to the build report**, by filename, so a modeller who starts here finds the assumptions section rather than concluding from a clean diff that nothing happened. Under §2.1 this cross-reference is load-bearing, not a courtesy.

**Sheets 2+ — the detail pages** (RPT-03).

Formatting is deliberately plain: a standard spreadsheet output, not a designed document. Headers frozen, columns sized, landscape fit-to-width, no decorative colour.

**Acceptance criteria**

1. **Given** a completed comparison, **then** the workbook is written with a Summary sheet and one detail sheet per level, each present even when empty.
2. **Given** an empty detail sheet, **then** it says why (*"No structural changes"*, *"Diff skipped — no baseline"*), never just blank.
3. **Given** a first run with no baseline, **then** no diff workbook is produced and the build report's outcome line says so — an empty workbook would read as "nothing changed".
4. **Given** the Summary sheet, **then** the build report is named on it.
5. **Given** the workbook open in Excel, **then** every sheet prints to a readable width.
