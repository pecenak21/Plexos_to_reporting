<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-02 — Ensure the Data File object exists, deterministically named

**As** the build, **I want** the same Data File object found and reused on every run, **so that** repeated builds do not accumulate duplicates.

**Type:** Story · **Size:** S · **Traces to:** §7.3 · **Depends on:** WRT-01 · **Q7 answered:** adopt the file-derived convention.

**Spec**

```python
def ensure_data_file_object(sdk, name: str) -> Object
```

`sdk.get_object_by_name(...)` first; `sdk.add_object(...)` only if absent.

**Naming must be deterministic** — the build has to find and update the same object next run rather than creating a duplicate. Proposed: the source file's basename without extension, so `hr_RenewableProfile.csv` → Data File object `hr_RenewableProfile`. Deterministic, unique per source file, and it matches how the file is already identified on the Data sheet.

**Q7 is closed: adopt the file-derived convention.** Every Data File object the build creates is named after its source file's basename. APS's existing objects use human-phrased names — "APS hourly LMP", "APS Load 2025Q3" — and those stay exactly as they are: **objects already in the model are never renamed by a build**, because a rename appears in the diff as a removal plus an addition (DIFF-02) and would look like a structural change that did not happen.

The two naming styles will therefore coexist in the model, and that is fine and worth saying out loud: file-derived names are the build's, human-phrased ones are APS's, and the difference is a useful signal of which is which.

**Acceptance criteria**

1. **Given** a source file with no matching Data File object, **then** one is created with the derived name.
2. **Given** the same source file on a second build, **then** the existing object is reused and no second object is created.
3. **Given** an existing object with a human-phrased name already linked to this property **by APS's own link**, **then** it is **not** reused and **not** renamed — the build creates its own Data File object for its own link (WRT-03), and a ledger entry names both. Reuse applies only to a Data File object a previous build created in the build's own scenario.
4. **Given** two source files whose basenames collide, **then** the build fails naming both — silently sharing one Data File object between two sources would be wrong.
