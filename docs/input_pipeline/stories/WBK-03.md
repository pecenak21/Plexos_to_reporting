<!-- Epic intro: docs/input_pipeline/epics/D_sources_workbook.md -->
### WBK-03 — Compare sheet reader

**As** the standalone comparison, **I want** its two paths and its output location from the workbook, **so that** pasting a Windows path with spaces into a cell beats quoting it on a command line.

**Type:** Story · **Size:** S · **Traces to:** §6.6 · **Depends on:** WBK-04, WBK-01

**Spec**

| Setting | Required | Meaning |
|---|---|---|
| `model_1_path` | Yes | The baseline — the "before" side |
| `model_2_path` | Yes | The side being compared against it |
| `output_report_path` | No | Blank → `<output_root>\Comparisons\` |

Each side may be a run folder or any folder holding a model. A bare name resolves against `output_root`; a full path is taken as-is. Disambiguation when a folder holds several `.xml` is DIFF-01's job.

**One wrinkle that must be stated, not just known.** The workbook is archived with each build as provenance (§12), so an archived copy carries whatever was last typed on this sheet — which has nothing to do with that build. Harmless, but it means the Compare sheet is **scratch space, not part of the run record**. RPT-02 states this in every build report so nobody reads an archived Compare sheet as a statement about that run.

**Acceptance criteria**

1. **Given** the example workbook's Compare sheet, **then** both paths and the output path are returned.
2. **Given** a bare folder name in `model_1_path`, **then** it resolves under `output_root`.
3. **Given** a blank `output_report_path`, **then** it defaults to `<output_root>\Comparisons\`.
4. **Given** a build run, **then** the Compare sheet is not read at all — assert this, so the two paths cannot accidentally become coupled.
