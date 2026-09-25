<!-- Epic intro: docs/input_pipeline/epics/J_packaging_operations_and.md -->
### OPS-03 — Logging

**As** whoever is debugging a build a month later, **I want** a log in the run folder, **so that** the build report's summary can be opened up.

**Type:** Chore · **Size:** S · **Traces to:** §7.1 · **Depends on:** BLD-04

**Spec**

A plain text log written into the run folder alongside the report. One line per build step with start, end and duration; every SDK call that writes, with its arguments; every finding, at the point it was raised. Console output stays short — progress and findings only; the detail lives in the file.

The log is **not** a substitute for the exception ledger (BLD-08). The ledger is curated and goes in the report for a modeller; the log is exhaustive and goes in the folder for whoever is debugging.

**Acceptance criteria**

1. **Given** any build, **then** a log is written into the run folder, including for a failed build.
2. **Given** a failed build, **then** the last log line identifies the step that failed.
3. **Given** the log, **then** no absolute path outside the run folder is written that would leak a user's home directory into an archived artifact.
