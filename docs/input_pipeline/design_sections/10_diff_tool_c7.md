## 10. Diff tool (C7)

Two entry points, one comparison engine.

The engine itself is a plain function with no opinion about how it was reached:

```python
compare(old_path, new_path) -> ComparisonResult
```

Both entry points are thin wrappers over it:

- **Build-triggered.** The build already knows both sides — it just produced one, and `compare_to` names the other — so it calls `compare()` directly as step 18 of §7.1 and writes the report into the run it just created. Nothing is invoked by hand; the report is simply part of what a build produces.
- **Standalone.** Reads the Compare sheet (§6.6) for its two paths and its output location, then calls the same function. Same workbook, same muscle memory as configuring a build, and pasting a Windows path with spaces into a cell beats quoting it on a command line.

Keeping the engine free of I/O concerns is what lets the same code serve both without either wrapper special-casing the other — the same reasoning that led to importing `TimeSeriesComparator` as a class rather than shelling out to its script (§10.4).

**Optional conveniences, not the primary path.** The standalone wrapper should also accept two paths as command-line arguments for scripted use, and — invoked with neither arguments nor a filled-in Compare sheet — list the run folders it can find and ask which two. Both are cheap: the argument form is a few lines, and the listing already exists for the build's pre-flight. Neither is how APS is expected to reach it day to day.

### 10.1 Input contract

The tool works from **two folder paths** — from the Compare sheet (§6.6) when run standalone, or from the build's own two sides when triggered by a build. Not two `.db` paths. Each folder is expected to hold:

```
<run folder>/
    Copy of Source Data/            source data as referenced by this run
    <model>.xml                     the run's Plexos model
    Timeseries/                     the Datafile CSVs
```

Resolution rules:

- **Exactly one `.xml`** → use it.
- **More than one `.xml`** → use `old_model` / `new_model` from the Compare sheet, or prompt if those are blank. No convention-based guess (newest, largest, name match) — a silently wrong pick produces a confidently wrong diff.
- **The tool always generates the `.db` itself**, on both sides, every run: `plexos-sdk xml-to-db <chosen>.xml <chosen>.db`, written into that same run folder.

That last rule is deliberate. Rather than detecting and trusting a pre-existing `.db` — which may be stale, may not correspond to the current `.xml`, or (per §2.5) usually will not exist at all in an archived folder — conversion is a mandatory first step of every diff. There is only ever the one `.db`, freshly generated from the one `.xml` the user confirmed, so "which `.db` is current" never arises.

### 10.2 Matching strategy

Comparing two SQLite databases is **not** a raw table diff. `object_id`, `membership_id`, `data_id` and `property_id` are auto-increment surrogate keys assigned independently per database — the same real generator will carry different IDs in two separately-built `.db` files even when nothing about it changed. An ID-keyed or row-by-row diff reports near-universal false differences.

Records are matched on **natural key**:

| Record type | Natural key |
|---|---|
| Object | (class name, object name) |
| Membership | (parent class, parent object, collection, child class, child object) |
| Property record | (membership natural key, property name, `band_id`, scenario name, `date_from`, `date_to`) |

Compared payload once matched: `value`, `data_file_path`, `data_file_object`.

This reuses the identity definition `plexos_sdk` already applies for property duplicate detection (§7.4) — same rule, used for writing and for diffing.

### 10.3 Implementation

```sql
ATTACH 'old_run.db' AS old (TYPE SQLITE, READ_ONLY);
ATTACH 'new_run.db' AS new (TYPE SQLITE, READ_ONLY);

SELECT
    COALESCE(o.parent_class, n.parent_class)   AS parent_class,
    COALESCE(o.child_object, n.child_object)   AS object,
    COALESCE(o.property,     n.property)       AS property,
    COALESCE(o.band_id,      n.band_id)        AS band_id,
    o.value          AS old_value,      n.value          AS new_value,
    o.data_file_path AS old_data_file,  n.data_file_path AS new_data_file,
    CASE WHEN o.property IS NULL THEN 'added'
         WHEN n.property IS NULL THEN 'removed'
         ELSE 'changed' END                    AS change_type
FROM old.v_property o
FULL OUTER JOIN new.v_property n
  USING (parent_class, parent_object, collection, child_class, child_object,
         property, band_id, scenario, date_from, date_to)
WHERE o.property IS NULL
   OR n.property IS NULL
   OR o.value          IS DISTINCT FROM n.value
   OR o.data_file_path IS DISTINCT FROM n.data_file_path;
```

The same pattern applies to `v_membership` for pure structural adds/removes.

**Accepted limitation:** a renamed object appears as one removal plus one addition, not a rename. Natural-key matching by name cannot detect renames, and this schema has no stable identifier to fall back on. Confirmed as expected behavior. `[CONFIRMED as acceptable]`

### 10.4 The three pieces, and what each can see

| Piece | Built how | Sees | Cannot see |
|---|---|---|---|
| `v_membership` diff | Ours (§9.1) | Memberships added / removed | Any value, or which file a property points at |
| `v_property` diff | Ours (§9.2) | Property values, Datafile pointer swaps, band/scenario/date changes | Values *inside* the CSVs |
| `TimeSeriesComparison` | Energy Exemplar's | Values inside the Datafile CSVs, with MAE/RMSE/correlation/max error/mean bias, gap and anomaly flags | Anything about model structure |

Plus a fourth, separate piece with no EE tooling behind it: comparing the **raw source files** between two runs (level 1 in §4). Not covered by any of the three above.

**On `QueryWriteMemberships`:** the pipeline does not invoke it. Its query is reimplemented as the `v_membership` view (§9.1) — same output shape, same DuckDB-over-SQLite approach, minus the cloud environment-variable lookup for the database path. The pipeline already needs DuckDB views for the CDM and the `v_property` diff, so adding one more view is cheaper than shelling out to a script and parsing its CSV. EE's script remains useful as a **cross-check**: running it against the same model should produce the same rows as `v_membership`, which is a cheap way to validate the view in phase 1. `[PROPOSED]`

The `v_property` diff carries the most weight and is not optional. A Datafile pointer swapped to a different CSV — the most common change this pipeline produces — touches no `t_membership` row at all, so a membership-level comparison reports nothing.

**On `TimeSeriesComparison`:** its "local" variant still requires `--cli-path` and `--environment` as mandatory CLI arguments even when every input file is local. Not a blocker, since the Cloud CLI is a prerequisite for this pipeline regardless (§13); alternatively import `TimeSeriesComparator` directly and pass `datahub_manager=None`, which skips the DataHub upload side effect entirely. `[CONFIRMED]`
