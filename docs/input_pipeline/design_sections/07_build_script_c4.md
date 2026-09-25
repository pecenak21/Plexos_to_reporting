## 7. Build script (C4)

### 7.1 Flow

```
 1. Read Run sheet                             → run_name, output_root, source_model,
                                                 source_timeseries, target_model, compare_to,
                                                 source_root, scenario_name, diff_threshold (§6.1)
 2. Read Sources sheet                         → list of source rows (§6.2)
 3. Read source model's stored data-file paths → the tree's folder name + the 100-odd
                                                 paths it expects to resolve (§6.1.1)
 4. PRE-FLIGHT CHECKS                          → §7.1.1 — before anything is created
 5. VALIDATION CHECKPOINT 1 (structural)       → per source file (§8.1). Needs no model, so it
                                                 runs here, on an untouched disk — not after a
                                                 121-file tree has been copied
 6. Create output_root\run_name\Inputs\        → the new run folder
 7. Copy source .xml AND its whole data-file   → the unit, not just the model (§6.1.1)
    tree into the new run folder                 never edit the source in place
 8. xml_to_db(new_run.xml, new_run.db)         → SDK working copy
 9. sdk.validate()                             → baseline pass, to tell pre-existing findings
                                                 from ones this build introduces (§8.2)
10. Resolve every target against the .db       → class / collection / property lang IDs, by name
11. VALIDATION CHECKPOINT 2 (semantic)         → coverage, overlap, existence, horizon (§8.2)
12. Create / clear the build's scenario        → attach to target_model, set Read Order (§7.5)
13. Write each Sources file into the tree      → §7.2.1 — our own files only, into APS_Inputs\
                                                 unless target_folder says otherwise
14. For each row: write the Datafile link      → §7.2 and §7.5 — a second link in our scenario,
                                                 mirroring the existing one, variables carried
15. sdk.validate()                             → compare against step 9's result
16. db_to_xml(new_run.db, new_run.xml)         → the model Plexos opens
17. Re-check every data-file path resolves     → §7.1.1, now against the built model
18. Run diff vs compare_to                     → §10
19. Emit build report + diff report            → §11.1, §11.2
20. Copy the workbook and the source files     → §12, provenance
    into the archive
```

**Failure semantics, which are not uniform:**

- **Steps 5 and 11 fail the build.** A build that produces a model nobody can trust is worse than no build. Step 5 failing leaves the disk untouched; step 11 failing leaves a run folder holding the findings and the build report.
- **Every model condition the build can resolve is resolved, recorded and carried on from** — a Read Order to choose, a variable to carry, a folder to create, a data file already linked. The standing rule: *model conditions get resolved and logged; bad input data stops the build.*
- **Steps 12–14 run inside one `sdk.transaction()`**, so a failure leaves no partial model.
- **Step 18 failing does not fail the build.** The model is already built and valid; a comparison that could not run is stated as such in the build report.

Step 17 is cheap and worth doing every time: it is the same check as pre-flight, run against the finished model, and it catches a Data File written to a path that does not match where the CSV actually landed — the one failure mode that would otherwise produce a model that opens fine and reads nothing.

### 7.1.1 Pre-flight checks

Everything that can be checked before a single file is created, checked there — so a misconfigured run fails in a second with an empty disk, rather than halfway through with a partial run folder someone now has to clean up.

- `output_root` exists and is writable.
- `output_root\run_name` does **not** exist. (Overridden only by an explicit `--force` CLI flag; see §6.1.)
- `run_name` is a valid folder name on Windows — no reserved characters, not a reserved device name, within path-length limits once the deepest data-file path is appended. APS's real paths already run to `TimeSeries\Generator\An_NameplateCapacity_2026_Q1_Enhanced_Transmission_STP.csv`, so the headroom is smaller than it looks.
- `source_model` exists and is readable.
- **Every data-file path the source model references resolves under `source_timeseries`.** Missing files are listed all at once with their stored paths. This is the check that matters most: a model whose tree is missing produces a build that completes and a model that reads nothing — the failure mode is silent, which is exactly why it is checked up front rather than discovered in Desktop.
- `source_timeseries`, when blank, is inferred as the folder beside `source_model` whose name matches the first segment of the model's stored paths. If no such folder exists, stop and say which name was expected.
- Free space at `output_root` exceeds the size of the tree about to be copied.
- `compare_to`, if named, exists and contains a model (§10.1's disambiguation rule applies). If blank and the source model did not come from a run folder, the build notes that the diff will be skipped and continues — that is the expected first-run case, not an error.
- `source_root` exists, and every `source_path` on the Sources sheet resolves to a file that exists under it. Missing source files are reported **all at once**, not one per run attempt.

### 7.2 Writing one Sources row

```
resolve target class / collection / property lang IDs by name
determine object list:
    wide          → non-time column headers
    single-object → [target_object]
ensure Data File object exists (§7.3)
for each object:
    membership = sdk.get_membership_by_names(
        parent_class_lang_id, collection_lang_id, parent_name, object_name)

    # remove-then-add, not update: update_property cannot set a data file (§2.3)
    sdk.remove_property(membership, property_obj, band_id=<row band, default 1>)
    sdk.add_property(
        membership     = membership,
        property_obj   = property_obj,
        value          = None,
        data_file_text = <path relative to the model — §7.2.1>,
        data_file_tag  = data_file_obj,
        band_id        = <row band, default 1>,
        scenario_tag   = <row scenario, default None>,
    )
```

`remove_property` returns a boolean rather than raising when nothing was there, so the same code path handles both a first write and a re-write.

Writes are wrapped in a single `sdk.transaction()` per run so a failed build leaves no partial model. `[CONFIRM — ours, spike]` for sources touching many objects (some touch hundreds), check whether a batch write path exists that accepts `data_file_text`/`data_file_tag`. `bulk_add_property` and `bulk_update_property` are documented but neither takes data-file parameters and `bulk_update_property` requires a scenario tag, so the per-object loop above may be the only correct option. Measure it against a real wide file before optimising.

### 7.2.1 Where a Sources file lands in the tree

`data_file_text` is a path relative to the model, so the build has to decide where each Standard-Format file goes inside the copied tree.

**The build only ever writes files it owns.** This is the rule the second-link decision (§7.5) forces on an earlier draft of this section, and it is the most important line here: a CSV that one of APS's own links reads is **never** overwritten. Doing so would change what that link returns while leaving the link itself intact — worse than repointing it, because §10.2's assignment comparison would see nothing and only the data-level comparison would catch it.

Three cases:

| Case | Action |
|---|---|
| **Our Data File object from a previous build** — created by the build, tagged with the build's scenario | Overwrite the CSV at its existing stored path, path unchanged. This is what makes "copy forward, change what differs" work: refreshing a source rewrites one file in place and changes nothing structural, so the run-to-run diff shows a data change rather than a spurious rewiring. |
| **New source, no Data File object yet** | Create one and place the CSV at `<tree>\<target_folder>\<filename>`. |
| **A Data File object exists but the build did not create it** — APS's own file, read by APS's own link | Leave it alone entirely. Write our own file alongside, with our own Data File object, linked in our scenario, and record both in the build report. |

Ownership is decided by whether the Data File object is linked from a record carrying the build's scenario — not by filename, which can collide.

**Placement — `target_folder`, defaulting to `APS_Inputs`.** `[ANSWERED]` An earlier draft placed each new file under a folder named for its Plexos class (`TimeSeries\Generator\`, `TimeSeries\Fuels\`). That rule had no answer for the tree's workflow folders — `Aurora\`, `LT Builds\`, `Load Following\`, `Load Forecasts\`, `Market\`, `Archive\` — which group by purpose rather than by class, and no way for the build to know when one of those was the right home. It would have guessed, quietly.

The resolution is an optional `target_folder` column on the Sources sheet (§6.2), relative to the tree root, defaulting to **`APS_Inputs`**. Three reasons that is better rather than merely different:

1. **Nothing is inferred.** The one person who knows where a file belongs says so, in a cell (§6.1.1's rule that the workbook is the interface).
2. **Everything the build wrote sits in one folder.** That makes the ownership rule above visible in a directory listing rather than only in a comparison — an unexpected file under `APS_Inputs\`, or one of APS's own files changing outside it, is immediately obvious.
3. **It stays overridable per file**, so a source that genuinely belongs beside its siblings goes there by being told to.

`APS_Inputs\` will not exist the first time a build runs against a given model. The build creates it and records that it did.

**Filenames.** Files the build writes are named `<resolution>_<source stem>.csv`, where resolution is the smallest time column — `yr_`, `mn_`, `dy_`, `hr_`. Note that APS's existing tree uses **both** `An_` and `yr_` for annual data (`An_FOM.csv` and `yr_EmissionsPrice.csv` sit in the same model), so there is no single existing convention to match; `yr_` is chosen because it is consistent with the other three. Files already in the model keep their names.

**Never move an existing Data File's path as a side effect of a build.** If a file genuinely needs relocating, that is a deliberate act, and it will show up in the structural diff as exactly what it is.

### 7.3 Data File object naming

One Data File object per Standard-Format file. The name must be **deterministic** — the build has to find and update the same object on the next run rather than creating a duplicate.

`[PROPOSED]`: the source file's basename without extension, e.g. `hr_RenewableProfile.csv` → Data File object `hr_RenewableProfile`.

Deterministic, unique per source file, and it matches how the file is already identified on the Sources sheet. `[ANSWERED]` — **adopt the file-derived convention.**

APS's existing 84 Data File objects use human-phrased names ("APS hourly LMP", "APS Load 2025Q3") and **keep them**: an object already in the model is never renamed by a build, because a rename appears in the diff as a removal plus an addition (§10.2) and would look like a structural change that did not happen. The two styles will therefore coexist, and that is useful rather than untidy — a file-derived name is the build's, a human-phrased one is APS's, and the difference says at a glance which is which.

### 7.4 Idempotency

Re-running a build against the same inputs must not duplicate records. Because a Datafile-backed property cannot be updated in place (§2.3), idempotency comes from the remove-then-add sequence in §7.2 rather than from an update call.

What makes that safe is the SDK's own duplicate-detection rule: two property records are the same only if membership, property, `band_id`, value, texts and tags all match, with different scenario tags, Datafile tags, or date ranges each counting as distinct records. `[CONFIRMED]` That rule is also what makes §7.5's second link possible at all: our record and APS's differ by scenario tag, so the SDK treats them as distinct rather than as a duplicate.

Under §7.5, idempotency comes from clearing and rewriting the build's own scenario each run, not from removing APS's records — the build never removes a link it did not create.

One consequence to watch `[CONFIRM — ours, spike]`: `remove_property(membership, property_obj, band_id)` does not take a scenario or date-range argument. If a property carries several records at the same band that differ only by scenario or date window, a plain remove may take out more than intended. Verify the removal scope against a multi-scenario property before the build script is used on anything but band 1 / no scenario.

The same identity rule drives the diff (§10.2) — one definition, used in both places.

---

### 7.5 The scenario, the Read Order, and the second link

This section records decisions taken after the rest of this document was written, and it governs §7.2's write path. `[CONFIRMED with APS]`

**Everything the build writes goes into one scenario it owns**, named `Automated Inputs` by default and set on the Run sheet (§6.1). Each build **clears the scenario's contents and rewrites them**, so a previous build's values are never silently reused.

**The scenario object itself is kept, never deleted.** Deleting it would also remove its attachment to the model, and that attachment is what makes the data take effect — a scenario only applies to models it is attached to. The build attaches it to the model named in `target_model`. One consequence worth telling APS: renaming the scenario on the Run sheet leaves the previous build's data in place under the old name, which is the mechanism for keeping it, and a way to accumulate orphaned scenarios if that is not what was wanted.

**The second link: add ours, leave theirs.** The build adds its own link from the target property to the data file it writes, tagged with its scenario, and **leaves any existing link exactly as it is**. The new link mirrors the existing one in every other respect — band, date range, time slices, and any variables attached to it — so the two records differ only in the data file they read and the scenario that tags them. §7.4's identity rule is what lets both coexist.

**Read Order: one above the maximum on the target model.** Where two scenarios define the same data, Plexos reads them in `Read Order` and the last read wins, so higher is higher priority. Scenarios default to 0; the highest currently set in APS's model is 2000. The build reads the highest Read Order among the scenarios *attached to `target_model`* and sets its own one above it — 2001 against today's model. **No other scenario's Read Order is changed.**

Two rejected alternatives, both of which were proposed and both of which are wrong:

- *A fixed large value.* `999` was suggested and is **below** three existing scenarios at 1000 and one at 2000; it would have lost silently.
- *Resetting other scenarios down to make room.* That edits APS's model to solve our problem, and can create new ties among the scenarios it moves.

Ties are not settled by Read Order: where two scenarios share a value, Plexos falls back to the order they appear in the interface — by category, then alphabetically within category — so the winner would depend on the scenario's *name*. Taking one above the maximum avoids the tie entirely. The value used and the maximum it was derived from are recorded in the build report every run.

**Conditional variables are carried onto the new link.** Where an existing link carries a conditional variable, the build copies it to the new link. This is not optional: **data tagged with a conditional variable overrides read ordering entirely**, so a new link without it would lose regardless of Read Order — the build would complete, report success, and change nothing. It is the most dangerous silent-failure mode in the write path.

Known real cases: `Battery` → `Max Power` carries `Battery Derate`; one `Fuel` → `Price` (`MKTGas`) carries `Fuel Adder for MKTGas`.

APS have confirmed the variables **should** apply to the data the build writes — *"but should be called out explicitly in the build report! It is critical that assumptions like this are called out explicitly. A diff report won't catch these."* That second half is a correctness requirement, not a reporting preference, and it generalises into the rule stated in §11.1: a carried variable changes what Plexos computes while leaving structure, property records and CSV values all identical, so every level of §10 reports nothing. Each carried variable is named individually in the build report, with its object and property.

**Schema note** `[CONFIRM — ours, spike]`: `Read Order` is read as an *attribute* (`t_attribute` / `t_attribute_data`), and "attached to a model" as a membership between the Model object and the Scenario object. Neither path was traced record-by-record the way §2.2's chain was, and this section rests on both. Verify alongside §9.2's joins, in phase 1.
