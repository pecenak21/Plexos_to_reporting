<!-- Epic intro: docs/input_pipeline/epics/G_semantic_validation_chec.md -->
### VAL-06 — Fold in `sdk.validate()`

**As** the build, **I want** the SDK's own integrity pass run as part of validation, **so that** a free check is not skipped.

**Type:** Story · **Size:** S · **Traces to:** §2.3, §8.2, §7.1 step 13 · **Depends on:** WRT-04

**Spec**

Call `sdk.validate()` after the writes and before `db_to_xml`. Its findings are folded into the checkpoint-2 finding set with their own category, so a modeller can tell an SDK finding from one of ours.

Run it **before** the writes too, against the freshly-copied model. If the source model is already failing the SDK's own checks, that needs to be visible as a pre-existing condition rather than appearing as something this build caused.

**Acceptance criteria**

1. **Given** a clean build, **then** `sdk.validate()` runs at both points and reports nothing.
2. **Given** a source model with pre-existing findings, **then** they are reported as pre-existing, before the writes, and do not stop the build.
3. **Given** a build that introduces a finding, **then** it is reported as new — the diff of the two validate results is what makes this distinction, so both results are retained.
4. **Given** any SDK finding, **then** its text appears verbatim in the report rather than being reworded.
