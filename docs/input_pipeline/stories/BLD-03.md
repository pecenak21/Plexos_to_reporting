<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-03 — Copy the model and its whole data-file tree forward

**As** the build, **I want** the entire source tree copied before anything is written, **so that** the ~95 links this run does not touch still resolve.

**Type:** Story · **Size:** M · **Traces to:** §6.1.1 · **Depends on:** BLD-02, CDM-06 · **Q4 answered:** any model can be the starting point — *"don't assume anything from this model."* See §2.1.

**This is the part an earlier draft got wrong, and it is worth being precise about.** Data File paths inside a PLEXOS model are stored **relative to the model file's own folder**. APS's populated model stores 100 distinct paths of this shape:

```
TimeSeries\Generator\An_FOM.csv
TimeSeries\Fuels\mn_FuelPrices.csv
TimeSeries\Emission\yr_EmissionsPrice.csv
```

A typical run touches a handful of properties. Copying only the `.xml` and writing the workbook's few CSVs would leave the other ~95 links pointing at files that do not exist in the new run folder — and the model would still open, and still read nothing.

**Spec**

1. Copy `source_model` into `Inputs\`, keeping its filename or applying the run's naming convention (Q4 / Q3).
2. Copy the **entire** `source_timeseries` tree into `Inputs\`, preserving subfolder structure, **into a folder named exactly `tree_root_name(db)`**.
3. Never modify anything under `source_model`'s original folder. The source is read-only for the whole build.

**Three rules, each of which has already bitten once:**

- **Copy forward, change what differs.** The whole tree first; then overwrite or add only what the Data sheet names.
- **The destination folder name is not free.** Stored paths begin with a literal folder name, so the copy must land in a folder called exactly that. The build does not hardcode `TimeSeries` — it reads the model's own paths and takes their common first segment. Self-checking, and it survives a model using a different convention.
- **Never run-stamp that folder.** A draft layout named it `Timeseries _ CWP 09022026` — a stamped name no relative path could resolve against. The run stamp goes on the run folder *above* it, which is where it is useful anyway.

**Orphans.** APS's tree holds 121 CSVs of which the model references 100. The 21 orphans are harmless to carry forward, but BLD-07 counts them — an orphan is usually either a file someone forgot to wire up or a leftover from a link that moved.

**Acceptance criteria**

1. **Given** APS's real model and tree, **when** copied, **then** all 121 files land under `Inputs\TimeSeries\` with subfolders preserved.
2. **Given** the copied model, **then** all 100 stored paths resolve against the new location.
3. **Given** a model whose `tree_root_name` is `Data`, **then** the destination folder is named `Data`, not `TimeSeries`.
4. **Given** a completed copy, **then** the source folder's files have unchanged mtimes — nothing was written there.
5. **Given** a copy interrupted mid-way, **then** the run fails and the partial folder is left with the failure recorded, not silently reused on a retry.
