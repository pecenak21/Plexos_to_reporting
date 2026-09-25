<!-- Epic intro: docs/input_pipeline/epics/C_standard_format_and_file.md -->
### FMT-02 — File shape determined by `target_object`, not by column count

**As** the build, **I want** shape decided by whether the Sources row names an object, **so that** a legitimate one-object wide file is never misread.

**Type:** Story · **Size:** S · **Traces to:** §3.2 · **Depends on:** FMT-01, WBK-02

**Spec**

| Shape | Data columns | Object identity comes from |
|---|---|---|
| **Wide / shared** | Many; each header is an exact PLEXOS object name | The column headers |
| **Single-object** | One | The Sources row's `target_object` |

The rule: **`target_object` blank → wide; `target_object` populated → single-object.** In the single-object case the data column's header is ignored entirely.

**Why not infer from structure.** "One data column means single-object" breaks on the real edge case of a wide file that happens to cover exactly one object — a legitimate and likely situation as APS adds resources one at a time. Keying off `target_object` is deterministic in every case and needs no special handling.

**Acceptance criteria**

1. **Given** blank `target_object` and headers `Ocotillo CT01, Ocotillo CT02`, **then** two objects are resolved from the headers.
2. **Given** `target_object = CH13_Coal` and a column headed `Price`, **then** one object is resolved and the header is ignored.
3. **Given** blank `target_object` and one data column headed with a real object name, **then** it resolves as wide, to that one object.
4. **Given** `target_object` populated and **two** data columns, **then** the build fails — a single-object row cannot consume a multi-column file, and quietly taking the first column would be a silent wrong answer.
