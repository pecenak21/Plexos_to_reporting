<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-05 — Create and clear the build's scenario

**As** the build, **I want** every value it writes to live in one scenario it owns, **so that** stale values are never reused and APS's own data is never touched. **[LATE]**

**Type:** Story · **Size:** M · **Traces to:** deliverable §"Writing CSVs as datafiles" · **Depends on:** CDM-07, WRT-04 · **Q5 answered:** per-run; attach to whichever model the Run sheet names. **Q18 answered:** the scenario name is a Run sheet cell.

**Spec**

- All values written by a build go into a single scenario, named **`Automated Inputs`** by default, changeable in the workbook.
- **Each build clears the scenario's contents and rewrites them**, so stale values from a previous build are never reused.
- **The scenario object itself is kept, never deleted.** Deleting it would also remove its attachment to the model, and the attachment is what makes the data take effect. Consequence worth stating to APS: renaming the scenario in the workbook leaves a previous build's data in place under the old name — which is the mechanism for keeping a build's data if that is wanted, and a way to accumulate orphaned scenarios if it is not.
- The scenario is attached to the model named in `target_model`. **A scenario only applies to models it is attached to**, so this step is what makes the data take effect at all.

**Acceptance criteria**

1. **Given** no existing `Automated Inputs` scenario, **then** one is created and attached to `target_model`.
2. **Given** an existing one with records from a previous build, **then** its records are cleared and the new ones written — and the old records are gone, verified through `v_property`.
3. **Given** an existing one, **then** the scenario **object** still has the same identity afterwards and its model attachment survives.
4. **Given** a scenario name changed in the workbook, **then** the previous scenario and its data are left untouched and a ledger entry says so.
5. **Given** a completed build, **then** every record the build wrote carries this scenario in `v_property.scenario`, and no record outside it was modified.
