<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-06 — Model introspection: stored data-file paths

**As** the build's pre-flight, **I want** the list of every data-file path a model expects to resolve, plus the folder name those paths begin with, **so that** the tree can be checked and copied before anything is created.

**Type:** Story · **Size:** S · **Traces to:** §6.1.1, §7.1.1 · **Depends on:** CDM-05

**Spec**

```python
def stored_data_file_paths(db) -> list[str]          # relative, as stored, e.g. "TimeSeries\\Generator\\An_FOM.csv"
def tree_root_name(db) -> str                        # the common first segment, e.g. "TimeSeries"
```

- Paths are read from `v_property.data_file_path`, distinct, preserving the stored form including backslashes and casing.
- `tree_root_name` takes the **common first path segment** across all stored paths. It does **not** hardcode `TimeSeries` — the build reads the model's own convention so it survives a model that uses a different one.
- If the first segments are not all equal, raise `MixedTreeRootError` listing every distinct first segment found. The copy-forward logic (BLD-03) has no correct behaviour in that case and must not guess.
- **Absolute paths:** any stored path that is absolute (drive letter or UNC) is returned but flagged. An absolute path survives a copy while still pointing back at the original model's folder — a silent failure that would make a "new" run read the old run's data. *(Closes open item #1b.)*

**Acceptance criteria**

1. **Given** the populated APS model, **then** exactly 100 distinct paths are returned and `tree_root_name` returns `TimeSeries`.
2. **Given** a model whose paths mix `TimeSeries\...` and `Data\...`, **then** `MixedTreeRootError` names both.
3. **Given** a model containing an absolute path, **then** it is returned flagged, and BLD-01 fails the build on it with that path named.
4. Stored paths come back byte-identical to what is in `t_text` — no normalisation, no separator swapping.
