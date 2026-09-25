<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-03 — Gas price

**As** the pipeline, **I want** `GasPrice 043026SJM.xls` converted, **so that** monthly gas price feeds `Fuel.Price`.

**Type:** Story · **Size:** S · **Traces to:** §4 · **Depends on:** PRE-01

**Spec**

Monthly, wide, one column per gas fuel object. Note the hub-per-column case: the source carries one column per hub and each is a different PLEXOS `Fuel` object, so this is a wide file and `target_object` stays blank (FMT-02).

**Acceptance criteria**

1. **Given** the real workbook, **then** a monthly Standard-Format CSV with one column per fuel.
2. **Given** the output, **then** every header matches a `Fuel` object name exactly, including `MKTGas` — which carries the `Fuel Adder for MKTGas` variable (WRT-08, Q10).
3. **Given** the `.xls` (not `.xlsx`) format, **then** it is read without a manual conversion step.
