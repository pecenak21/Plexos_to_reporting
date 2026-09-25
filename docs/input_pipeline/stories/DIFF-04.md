<!-- Epic intro: docs/input_pipeline/epics/B_comparison_engine.md -->
### DIFF-04 — Source-file diff: did the raw inputs change?

**As** a modeller, **I want** to know which source files differ from the ones the baseline run used, **so that** an unexpected model change can be traced to an input before the model is investigated.

**Type:** Story · **Size:** S · **Traces to:** §10.4 (level 1), §11 · **Depends on:** BLD-06

**Spec**

Compares the `Upstream Inputs Referenced/` folders of the two runs. For each file present in either: `added` / `removed` / `changed` / `unchanged`, by SHA-256 over content. No parsing — this level knows nothing about the files' meaning, only whether the bytes differ.

There is **no Energy Exemplar tooling for this level**; it is entirely ours.

Degrades rather than fails: if either side has no archived source folder (a run predating the archive practice, or a plain working folder), report "not available for this side" and continue. The other three levels are unaffected.

**Acceptance criteria**

1. **Given** two runs with identical source folders, **then** every file reports `unchanged`.
2. **Given** one file with one byte changed, **then** it reports `changed` and nothing else does.
3. **Given** an old side with no `Upstream Inputs Referenced/`, **then** the level reports unavailable, names why, and the comparison still returns the other three levels.
