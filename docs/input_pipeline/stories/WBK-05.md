<!-- Epic intro: docs/input_pipeline/epics/D_sources_workbook.md -->
### WBK-05 — Workbook validation and error reporting

**As** whoever fills in the workbook, **I want** every problem with it reported at once, with cell references, **so that** fixing it is one pass rather than one error per run attempt.

**Type:** Story · **Size:** M · **Traces to:** §7.1.1 · **Depends on:** WBK-01, WBK-02, WBK-03, FMT-01

**Spec**

A `WorkbookFindings` collector that gathers everything and raises once at the end of reading, never at the first problem. Each finding carries sheet, cell (`Data!C14`), the offending value, and what was expected.

**Three layers, and each check belongs to exactly one.** Workbook structure and self-consistency here; anything needing the source *file* is FMT-03; anything needing the *model* is VAL-*. A check that appears in two layers gets two error messages for one problem, which is how a user ends up fixing the same thing twice.

Checks at this layer:

- Required keys and columns present.
- Paths are syntactically valid Windows paths; `run_name` has no reserved characters and is not a reserved device name.
- `source_path` values are unique across rows (the same file mapped twice is almost certainly a copy-paste error; if it is deliberate it is expressed as two different target rows, which is fine — so this is a **warning** naming both rows).
- No row where every field is blank except `notes`.

**Not here:** `target_object` populated on a row whose file has several data columns. That needs the CSV read, so it belongs to FMT-02/FMT-03 and is owned there.

**Acceptance criteria**

1. **Given** a workbook with five separate problems, **then** all five appear in one message, each with a cell reference.
2. **Given** `run_name = CWP 12/20/2026`, **then** an error naming the invalid character.
3. **Given** the same `source_path` on two rows targeting the same property, **then** a warning naming both rows.
4. **Given** a clean workbook, **then** nothing is raised and nothing is printed.
5. **Given** the full check list, **then** no check here reads a source CSV or the model — assert by running this layer with `source_root` pointing at an empty folder and no model available.
