## 3. Standard Format

The contract every file entering the build script satisfies.

### 3.1 Shape

```
<time columns>, <data column(s)>
```

Time columns are always a **prefix of** `Year, Month, Day, Period`, in that order:

| Granularity | Time columns |
|---|---|
| Annual | `Year` |
| Monthly | `Year, Month` |
| Daily | `Year, Month, Day` |
| Hourly | `Year, Month, Day, Period` |

`Year` is mandatory. Granularity is **inferred from the header**, never declared — there is no format column anywhere in the interface. `[CONFIRMED]` against every `An_`/`yr_`/`mn_`/`hr_`-prefixed CSV in APS's `Generator/`, `Fuels/`, `Emission/` and `Archive/` folders.

### 3.2 Two file shapes

| Shape | Data columns | Object identity comes from |
|---|---|---|
| **Wide / shared** | Many; each header is an exact Plexos object name | The column headers |
| **Single-object** | One | The Sources row's `target_object` |

**Disambiguation rule** `[PROPOSED]`: shape is determined by whether `target_object` is populated on the Sources row, **not** by counting columns.

- `target_object` blank → wide. Every non-time column header is treated as an exact Plexos object name.
- `target_object` populated → single-object. The single data column's header is ignored entirely.

This is deliberate. Inferring shape structurally ("one data column means single-object") breaks on the real edge case of a wide file that happens to cover exactly one object — a legitimate and likely situation as APS adds resources one at a time. Keying off `target_object` is deterministic in every case and needs no special handling.

**Validation:** if `target_object` is blank and the file has exactly one data column, the build emits a warning naming both possible readings, since this is the one case where a user error (forgetting `target_object`) is silently plausible.

### 3.3 Why everything goes through a Datafile

Even near-constant values (e.g. `yr_EmissionsPrice.csv`, one row, one year) are written as Datafile CSVs rather than scalars in the model. Three reasons: `[CONFIRMED as APS's existing convention]`

1. **Diffing stays clean.** Value changes live in CSVs and diff with ordinary tooling; the model-structure diff stays about genuine structure. Mixing scalar values into the model would bury real structural changes in routine value churn.
2. **Matches existing practice.** Every real APS file reviewed already works this way.
3. **One code path.** No "is this static enough to skip the file?" decision for anyone to get wrong.

Known cost: in Plexos Desktop, a Datafile-linked property displays as `Data File: xyz.csv` rather than showing the number inline. `[ANSWERED]` — APS modelers do not rely on reading values inline in the property grid, so this costs nothing in practice. Writing everything through Datafiles is settled with no caveat.
