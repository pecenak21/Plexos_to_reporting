## 2. Confirmed Plexos write mechanics

This section is the foundation everything else rests on. §2.1 and §2.2 were traced record-by-record against a real populated APS model (`2026 APS_TA V3.1 - Copy.xml`, 952 objects, 84 of them Data File objects). §2.3–§2.5 rest on a different and weaker evidence class — Energy Exemplar's SDK documentation and the source of their shipped scripts — which is enough to build on but was not verified against the model itself.

### 2.1 A property does not hold a value directly

Time-varying data reaches Plexos through a **Data File**: a CSV on disk, plus a Data File object inside the model that points at it, plus a link from the target property to that Data File object. Writing data is therefore always two operations — write the CSV, and wire it into the model.

### 2.2 The linkage chain

| Table | Columns that matter | Role |
|---|---|---|
| `t_membership` | `membership_id, parent_object_id, collection_id, child_object_id` | Which object/relationship a data instance belongs to |
| `t_property` | `property_id, collection_id, name, unit_id, is_multi_band` | Which property (e.g. `Rating`, `Price`) |
| `t_data` | `data_id, membership_id, property_id, value` | The core record: this membership's this property has an instance |
| `t_tag` | `data_id, object_id` | Links the record to the Data File object (`t_tag.object_id`) |
| `t_text` | `data_id, value` | The file path string, e.g. `TimeSeries\Load Following\hr_APS_LMP_Profile - region.csv` |
| `t_date_from` / `t_date_to` | `data_id, date` | Optional validity window on the record |

Traced example: Data File `object_id=614` ("APS hourly LMP") is referenced via `t_tag` rows resolving to `t_data` records for `Offer Price` and `Bid Price` on two BESS generators — one shared hourly CSV feeding a multi-band price property across multiple objects.

### 2.3 The SDK does this in one call

The build script does **not** write these tables by hand. `plexos_sdk` exposes exactly this primitive: `[CONFIRMED against PLEXOS_SDK_Methods.md]`

```python
data: Data = sdk.add_property(
    membership=membership,
    property_obj=property_obj,
    value=None,                          # scalar, or None for pure Datafile-backed
    data_file_text="TimeSeries/hr_RenewableProfile.csv",   # -> t_text
    data_file_tag=data_file_obj,                           # -> t_tag  (the Data File object)
    date_from=None, date_to=None,                          # -> t_date_from / t_date_to
    band_id=1,
    scenario_tag=None,
)
```

**Important constraint on the update path.** `add_property` is the *only* documented method that accepts `data_file_text` / `data_file_tag`. The documented signature of `update_property` is:

```
update_property(membership, property_obj, value: float!, band_id=1, period_type_id?) -> Data
```

— `value` is required, and there is no way to set or change a data file through it. There is also no `create_if_missing` parameter, and `bulk_update_property` requires a `scenario_tag`. **A Datafile-backed property therefore cannot be updated in place**; it must be removed and re-added. This is exactly what Energy Exemplar's own `ReplaceModelInputFiles` does under `--replace-existing true`, which is good corroboration that it is the intended pattern rather than a workaround. §7.2 and §7.4 are written accordingly.

Other methods the build script uses: `sdk.remove_property(...)`, `sdk.add_object(...)` / `sdk.get_object_by_name(...)` for Data File objects, `sdk.get_membership_by_names(...)`, `sdk.transaction(...)`, and `sdk.validate()` for a free integrity pass. All present in the documented method list. `[CONFIRMED]`

### 2.4 Name-based resolution, no lang-IDs in the interface

Class, collection, and property are resolved **by name** against the live model, using the same lookup pattern Energy Exemplar's own `ReplaceModelInputFiles` uses (`t_class` / `t_collection` / `t_property` name queries returning `lang_id`). The Sources workbook therefore carries plain names — `Generator` / `Generators` / `Max Capacity` — and never numeric IDs. `[CONFIRMED]`

### 2.5 The `.db` is not a given

PLEXOS Desktop saves `.xml`. The `.db` is produced on demand by `plexos-sdk xml-to-db` and exists only because something asked for it — no `.db` exists in any of APS's archived run folders today. Every EE script that reads `reference.db` fails loudly if it's absent rather than creating it. **Any component that needs a `.db` must create it.** `[CONFIRMED]`
