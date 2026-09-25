<!-- Epic intro: docs/input_pipeline/epics/J_packaging_operations_and.md -->
### OPS-02 — CLI entry points

**As** anyone running this, **I want** two commands with obvious names, **so that** the pipeline is reachable without reading code.

**Type:** Chore · **Size:** S · **Traces to:** §10, §6.1.1 · **Depends on:** BLD-04, DIFF-07

**Spec**

```
plexos-build   <workbook.xlsx> [--run-name …] [--output-root …] [--force] [--dry-run]
plexos-compare [<old> <new>] [--workbook …] [--report …]
check-environment
```

`plexos-compare` with no arguments and no filled-in Compare sheet lists the run folders it can find and asks which two. The listing already exists for the build's pre-flight, so this is nearly free.

**Acceptance criteria**

1. **Given** each command with `--help`, **then** every option is documented with its default.
2. **Given** a failed build, **then** the exit code is non-zero and distinguishes validation failure from an internal error.
3. **Given** `plexos-compare` with no arguments, **then** the run folders are listed and two can be picked.
