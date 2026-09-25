<!-- Epic intro: docs/input_pipeline/epics/J_packaging_operations_and.md -->
### OPS-04 — Handover runbook

**As** APS after handover, **I want** a runbook, **so that** the pipeline outlives the engagement.

**Type:** Chore · **Size:** M · **Traces to:** §1.1 (ownership column) · **Depends on:** everything

**Spec**

Written for the APS modeller who will own this, not for the build team. Covers: installing and checking the environment; filling in the workbook; running a build; reading the build report; running a standalone comparison; adding a new source (which is a new row, and sometimes a new preprocessor); what each failure message means and what to do about it; and what the build will *not* do.

Per §1.1, ownership after handover splits: APS owns the preprocessors, the templates and the workbook; everything else transfers from Utilicast to APS. The runbook is what makes the transfer real.

**Acceptance criteria**

1. **Given** the runbook, **then** someone who has not seen the code can run a build end to end on a test model.
2. **Given** each failure message the build can emit, **then** the runbook names it and says what to do.
3. **Given** the runbook, **then** adding a new source is documented as a worked example from real APS data, not in the abstract.
