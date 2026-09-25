<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-06 — Archive the workbook and the source files

**As** anyone opening an archived run a year later, **I want** the run to describe itself, **so that** its provenance is in the folder rather than in someone's memory.

**Type:** Story · **Size:** S · **Traces to:** §12, §6.1.1 · **Depends on:** BLD-02 · **Q13 / Q14 answered:** archiving adopted; no existing driver workbook to reconcile with.

**Spec**

- Copy the workbook itself into `Inputs\Sources_Workbook.xlsx`. Its Run and Data sheets are the record; its Compare sheet is scratch (WBK-03) and the report says so.
- Copy every file named on the Data sheet into `Inputs\Upstream Inputs Referenced\`, preserving relative structure under `source_root`. This is what DIFF-04 compares against on the next run.
- The `.xml`, the `.db` and the tree are already there from the build; retaining them is a matter of **not deleting them**, not extra work.

**Why the workbook rather than command-line arguments carries the run's identity.** Both work, and the build accepts CLI overrides (WBK-06). But the workbook is archived with the run, so putting the run's identity and baseline in it makes the archived workbook a complete record of what produced that model — open any archived run and its provenance is right there. Arguments lose that unless separately logged, which is why WBK-06 logs them.

**Acceptance criteria**

1. **Given** a completed build, **then** the workbook and every source file named on the Data sheet are present under `Inputs\`.
2. **Given** two source files with the same basename in different folders under `source_root`, **then** both are archived without collision.
3. **Given** an archived run, **then** re-reading its archived workbook reproduces the `RunConfig` that built it, except for any CLI overrides — which the report names.
