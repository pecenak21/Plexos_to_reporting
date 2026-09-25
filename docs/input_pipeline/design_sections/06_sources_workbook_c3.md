## 6. Sources workbook (C3)

Three sheets:

| Sheet | Shape | Purpose |
|---|---|---|
| **Run** | Key/value, ~6 rows | What this run is and what it builds from (§6.1) |
| **Sources** | One row per file | Where each Standard-Format file goes in Plexos (§6.2) |
| **Compare** | Key/value, ~4 rows | An on-demand comparison of any two runs (§6.6) |

The first two drive the build. The third drives the standalone comparison and is not read by the build at all.

### 6.1 Run sheet — the run's identity and destination

A per-run value cannot live on the Sources sheet. The run's name would have to be repeated on every row, which lets two rows disagree about what run they belong to and makes the build's first job reconciling its own configuration. So run-level settings get their own small key/value sheet — roughly five rows, not a second table to maintain. `[PROPOSED]`

| Setting | Required | Example | Purpose |
|---|---|---|---|
| `run_name` | Yes | `CWP 12202026` | The folder created for this run; also the run's identifier in the build report and archive |
| `output_root` | Yes | `...\Plexos models Folder` | Where run folders are created |
| `source_model` | Yes | `...\TimeSeries\2026 APS_TA V3.1.xml` | **Full path to the `.xml` copied as this build's starting point.** Any location — a prior run, a base template, a working folder |
| `source_timeseries` | No | *(blank → inferred)* | The data-file tree that travels with that model (§6.1.1). Blank means "the folder beside `source_model` that its own stored paths name" |
| `compare_to` | No | *(blank → source model's run)* | The run the automatic diff compares against. Blank means the run `source_model` came from; if it did not come from a run folder, the build skips the diff and says so |
| `source_root` | Yes | `...\Standard Format` | What `source_path` on the Sources sheet is relative to, so those cells stay short and portable |
| `target_model` | Yes | `TA_Base2_ST` | The Plexos model this run builds. Sets the horizon validated against (§8.2) and the model the build's scenario attaches to (§7.5). Per-run — there is no standing answer |
| `scenario_name` | No | *(blank → `Automated Inputs`)* | The scenario everything this run writes goes into (§7.5). Cleared and rewritten each build; rename it to keep a previous build's data |
| `diff_threshold` | No | *(blank → 0.5%)* | Changes smaller than this are counted in the diff report rather than itemized (§11.2) |

**Why `source_model` is a path to a model, not the name of a run.** An earlier draft had one `baseline_run` field doing both jobs — the model to copy and the run to diff against — on the reasoning that they are the same folder in practice. They are not, for a reason that is structural rather than incidental: **APS has no run folders today** (§12). Per-run archiving is part of what this engagement is proposing, so on the first build there is by definition no run folder for the starting model to live in. APS's real working model (`2026 APS_TA V3.1 - Copy.xml`, 100 Data File paths, all resolving) sits in an ordinary working folder. Requiring the starting point to be a run folder under `output_root` would make the first build impossible and the real working model unaddressable. `[CONFIRMED]`

The same split covers the ongoing case: once runs are being archived, `compare_to` blank means "the run this model came from," which is the normal steady state. On the first build it is blank and there is nothing to compare against — the build says so and continues rather than failing.

**Rules the build enforces:**

- **`output_root\run_name` must not already exist.** The build fails rather than writing into or over an existing run folder. Overwriting is a `--force` CLI flag, never a spreadsheet cell — a destructive action should not be something someone can leave switched on from last time.
- **`source_model` is explicit, never inferred.** Defaulting to "the most recent folder" would make a build's output depend on directory state rather than on the workbook, and make the same workbook produce different results on different days.
- **Every data-file path the source model references must resolve before anything is copied** (§6.1.1). The failure this guards against is silent — a model missing its tree still opens in Desktop and simply reads nothing — so it is checked up front rather than discovered later.

### 6.1.1 The model and its data-file tree are one unit

**This is the part an earlier draft got wrong, and it is worth being precise about.** Data File paths inside a Plexos model are stored **relative to the model file's own folder**. Verified against APS's populated model, which stores 100 distinct paths of this shape: `[CONFIRMED]`

```
TimeSeries\Generator\An_FOM.csv
TimeSeries\Fuels\mn_FuelPrices.csv
TimeSeries\Emission\yr_EmissionsPrice.csv
```

Beside that `.xml` sits a `TimeSeries\` folder with ten category subfolders — `Archive`, `Aurora`, `Emission`, `Fuels`, `Generator`, `LT Builds`, `Lines`, `Load Following`, `Load Forecasts`, `Market` — holding 121 CSVs, of which the model references 100. Spot-checked paths all resolve.

Three consequences the build must respect:

1. **Copy the whole tree, not just the `.xml`.** A typical run touches a handful of properties; the model carries ~100 data-file links. Copying only the `.xml` and writing the workbook's few CSVs would leave the other ~95 links pointing at files that do not exist in the new run folder. The build copies the entire source data-file tree first, preserving its subfolder structure, then overwrites or adds only what the Sources sheet names. **Copy forward, change what differs.**
2. **The destination folder name is not free.** The stored paths begin with a literal folder name, so the copy has to land in a folder called exactly that or every path breaks. The build does not hardcode `TimeSeries` — it reads the model's own stored paths, takes their common first segment, and uses that as the destination folder name. Self-checking, and it survives a model that uses a different convention. `[PROPOSED]`
3. **Never run-stamp that folder.** The draft run-folder structure (§12) named the data folder `Timeseries _ CWP 09022026` — a stamped name no relative path in a populated model could resolve against. Caught before anything was built on it, but worth keeping as a standing rule for the proposed structure: the data folder keeps the name the model's paths expect, and the run stamp goes on the run folder above it, which is where it is useful anyway.

**Orphans.** 121 files present, 100 referenced — 21 CSVs in the tree that no Data File object points at. Harmless to carry forward, but the build report should count them, since an orphan is usually either a file someone forgot to wire up or a leftover from a link that moved.

**Why the workbook rather than command-line arguments.** `[ANSWERED]` — and the answer is stronger than this section originally assumed. APS: *"The workbook runs everything. This is still a very manual process without much automation. A human will set up the workbook and runs everything from it. It needs to be the source of truth and house necessary options."*

So the workbook is not merely the more convenient of two equal options; it is **the interface**. Three consequences the build must hold to:

- **A new option gets a Run sheet cell first.** A CLI flag is a convenience on top of a cell, never an alternative to one, and no behaviour may be reachable only from the command line.
- **The archived workbook is the complete record of a run** (§12) — which is what makes the archive worth keeping, and why every CLI override has to be reported (below).
- **Overrides are reported.** An override makes the archived sheet a lie about its own run, and no comparison level would ever show it, so the build report names the setting, the sheet value and the value actually used.

**One deliberate exception**, flagged for APS rather than assumed: `--force`, which permits writing into an existing run folder, stays command-line-only. A destructive option living in a cell is one somebody leaves switched on from last time and does not notice — the cell would be perfectly truthful and the build would still overwrite a run. `--dry-run` is command-line-only for the mirror-image reason: it is something you do once, not a setting you keep.

**Note on an earlier decision.** §6.2's "no run-selection sheet" still stands — that was about not building a sheet for choosing *which sources participate* in a given run, and this does not reintroduce it. Every row on the Sources sheet is always active; the Run sheet says only where the run goes and what it builds from.

### 6.2 Sources sheet columns

| Column | Required | Meaning |
|---|---|---|
| `source_path` | Yes | Path to the Standard-Format file (preprocessor output or filled template — treated identically) |
| `target_class` | Yes | Plexos class name, e.g. `Generator` |
| `target_collection` | Yes | Plexos collection name, e.g. `Generators` |
| `target_property` | Yes | Plexos property name, e.g. `Max Capacity` |
| `target_object` | Conditional | Populated for single-object files; blank for wide files (§3.2) |
| `target_folder` | No | Where the CSV is placed inside the data-file tree. Blank → `APS_Inputs` (§7.2.1) |
| `notes` | No | Free text, ignored by the build |

Deliberately absent: no format/granularity column (§3.1), no run-selection sheet, no source registry, no object/property catalog — object and property existence is validated against the live model itself.

### 6.3 Bands — deferred, not designed out

`band_id` is **not** a column on the v1 sheet. The internal write function accepts it as an optional parameter from day one (defaulting to band 1), exactly as `sdk.add_property()` does. Adding a sheet column later is a pure additive change — a column plus a few lines wiring it through the same call — not a rebuild. `[PROPOSED, agreed]`

`scenario_tag` is no longer in this category: §7.5 makes every write carry the build's own scenario, so the parameter is always supplied. What stays off the sheet is a *per-row* scenario; the run-level one is a Run sheet cell.

This is the general rule for any optional SDK parameter not needed in v1: **full signature internally, minimal surface on the sheet.**

### 6.4 Multiple rows per target

Several rows may share the same `target_class`/`target_collection`/`target_property`, each pointing at a different file covering a different set of objects. This needs no special mechanism — Plexos properties are written per object-membership, not atomically per class. APS already does this: `hr_RenewableProfile.csv` (existing renewables) and `hr_NewResRenProfile.csv` (planned resources) both feed hourly `Rating`. `[CONFIRMED]`

**Overlap is a build-time error, not a precedence rule.** If two rows share a target and their object sets intersect, the build fails and names the overlapping objects. No row-order winner, no "last one wins" — nothing anyone has to remember. `[PROPOSED, agreed]`

### 6.5 Property disambiguation

`[ANSWERED]` — **yes, always sufficient.** The SDK's property lookup resolves a property name *within a collection*, and the collection is resolved by name too; where the same property name exists on multiple collections, `parent_class_lang_id` disambiguates, and `target_class` supplies it. The four name columns on the Sources sheet are a complete key. No fifth column is needed.

Keep the "resolved to more than one match" error path anyway (§8.2). It should now be unreachable — and an unreachable error that fires is the cheapest possible signal that an assumption stopped holding.

---

### 6.6 Compare sheet — an on-demand comparison of any two runs

The build always compares its own output against its baseline and needs no configuration to do it (§6.1's `compare_to`). Separately, a modeller will occasionally want to ask "what changed between these two runs?" about runs that have nothing to do with today's build. That is what this sheet is for. `[PROPOSED]`

| Setting | Required | Example | Purpose |
|---|---|---|---|
| `old_run` | Yes | `CWP 09202026` | The baseline side |
| `new_run` | Yes | `CWP 12202026` | The side being compared |
| `old_model` / `new_model` | Conditional | *(blank)* | Only when that folder holds more than one `.xml` (§10.1) |
| `report_output` | No | *(blank → `<output_root>\Comparisons\`)* | Where the report is written |

**Each side is a path, and that is deliberately permissive.** A bare name resolves against `output_root`; a full path is taken as-is. More importantly, neither side has to be a *run* folder — the resolution rule is "find the model in this folder" (§10.1), which is satisfied equally by an archived run and by the working folder a live model sits in. So "how does the model I have open differ from the last archived run?" needs no extra machinery: point `old_run` at the archived run and `new_run` at the working folder. Given that APS's real working model does not live in a run folder, this is likely to be the more common use, not the exotic one.

**Why the report cannot go where the build's does.** A build writes its report into the run it just created, which it owns. A standalone comparison owns neither side — writing into either would be editing an archived record after the fact. So it writes somewhere else, defaulting to a `Comparisons\` folder beside the runs, named for both sides and the date.

**One wrinkle worth naming.** The workbook is archived with each build as provenance (§12), so an archived copy will carry whatever was last typed on the Compare sheet — which has nothing to do with that build. Harmless, but it means the Compare sheet is scratch space rather than part of the run record. `[PROPOSED]` The build report states this on every run, so nobody reads an archived Compare sheet as a statement about that run. Not raised with APS as a question, because the alternative — a second workbook to keep track of — is worse than a sentence in a report. Revisit only if the sentence turns out not to be enough.
