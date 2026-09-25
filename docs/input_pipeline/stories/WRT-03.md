<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-03 — Decide where a Data sheet file lands in the tree

**As** the build, **I want** each source file placed where its link expects it, **so that** refreshing a source shows as a data change rather than a rewiring.

**Type:** Story · **Size:** M · **Traces to:** §7.2.1 · **Depends on:** BLD-03, WRT-02 · **Q6 answered:** a `target_folder` column on the Data sheet, defaulting to `APS_Inputs`.

**Spec**

**The build only ever writes files it owns.** This is the correction the second-link decision (WRT-07) forces on the original §7.2.1 rule, and it is the single most important line in this story: a CSV that APS's own link reads is **never** overwritten. Overwriting it would change what that link returns while leaving the link itself intact — which is worse than repointing it, because DIFF-03 would see nothing and only the data-level diff would catch it. It would also break the promise the example workbook makes to APS in writing: *"Existing scenarios and base data are left as they are."*

So there are three cases, not two:

| Case | Action |
|---|---|
| **Our Data File object from a previous build** (created by the build, tagged with the build's scenario) | Overwrite the CSV **at its existing stored path**, path unchanged. This is what makes "copy forward, change what differs" work: refreshing a source rewrites one file in place and changes nothing structural, so the run-to-run diff shows a data change rather than a spurious rewiring. |
| **New source, no Data File object yet** | Create one and place the CSV at `<tree>\<target_folder>\<filename>` — `target_folder` defaults to **`APS_Inputs`** (naming below). |
| **A Data File object exists but the build did not create it** — APS's own file, read by APS's own link | **Do not touch it.** Write our own file alongside, with our own Data File object, and link it in our scenario. Record a ledger entry naming the existing file and the one we wrote. |

Ownership is determined by whether the Data File object is linked from a record carrying the build's scenario — not by filename, which can collide.

**Filename.** The deliverable states the convention as `<tree>\<class>\<resolution>_<source stem>.csv`, where resolution is the smallest time column (`yr_`, `mn_`, `dy_`, `hr_`). Note APS's real tree uses `An_` for annual where the deliverable says `yr_`, and both appear in the example workbook — **WBK-04 settles which prefix vocabulary is canonical** before this story is started.

**Placement.** `<tree>\<target_class>\` matches APS's observed convention: the tree is organised by category with `Generator\`, `Fuels\`, `Emission\`, `Lines\`, and files sit under the category of the class they feed.

**Never move an existing Data File's path as a side effect of a build.** If a file genuinely needs relocating that is a deliberate act, and it will show in the structural diff as exactly what it is.

**Placement — Q6 closed.** An optional `target_folder` column on the Data sheet, relative to the tree root, **defaulting to `APS_Inputs`**. Blank means `<tree>\APS_Inputs\`; filled in means exactly what it says.

This replaced an earlier rule that placed each file under a folder named for its PLEXOS class. The default folder is better on three counts, and the reasoning is worth keeping close to the code:

1. **Nothing is inferred.** The class-name rule had no answer for the tree's workflow folders — `Aurora\`, `LT Builds\`, `Load Following\`, `Load Forecasts\`, `Market\`, `Archive\` — which are groupings by purpose, not by class. There was no rule the build could apply to know when one of those was the right home, so it would have guessed wrong quietly.
2. **It puts everything the build wrote in one place.** That makes WRT-03's central rule — *the build only ever writes files it owns* — visible in a folder listing rather than only in a diff. A file appearing under `APS_Inputs\` that nobody expected, or one of APS's own files changing outside it, are both immediately obvious.
3. **It stays overridable per file**, in a cell, by the one person who knows where a file belongs (§2.2).

Every placement still goes in the build report's assumptions section, defaulted or specified. A file in an unexpected folder still resolves and still produces a working model — exactly the class of thing §2.1 says must be stated in words rather than left to a diff.

**Creating the folder.** `APS_Inputs\` will not exist in a model's tree the first time a build runs against it. The build creates it, and records that it did.

**Acceptance criteria**

1. **Given** a Data File this build's scenario created on a previous run, **then** its CSV is overwritten at its existing stored path and `t_text` is unchanged.
2. **Given** APS's own `TimeSeries\Generator\hr_RenewableProfile.csv` and a Data sheet row targeting the same property, **then** that file's bytes are **unchanged**, a separate file is written for our link, and a ledger entry names both. Assert the original file's hash before and after.
3. **Given** a new Data File and a blank `target_folder`, **then** it lands at `TimeSeries\APS_Inputs\<filename>` and the stored path matches — whatever its class.
3b. **Given** a tree with no `APS_Inputs\` folder, **then** the build creates it and records that it did.
3c. **Given** `target_folder = Load Forecasts`, **then** the file lands at `TimeSeries\Load Forecasts\<filename>` and the folder is created if absent.
3d. **Given** a `target_folder` that escapes the tree — absolute, or containing `..` — **then** the build fails naming the cell.
4. **Given** a property that already has a link when the build writes to it, **then** a **warning** is raised naming the existing file and the existing link — the deliverable promises this and under the second-link design it is the normal case, so it must be a report line rather than a silence.
5. **Given** a placement, **then** a ledger entry names the file and the folder chosen.
6. **Given** any existing Data File, **then** no build ever changes its stored path — assert it.
