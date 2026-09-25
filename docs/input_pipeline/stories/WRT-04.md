<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-04 — Write one Data sheet row

**As** the build, **I want** one function that writes one row's worth of links, **so that** the remove-then-add sequence exists in exactly one place.

**Type:** Story · **Size:** L · **Traces to:** §7.2, §2.3 · **Depends on:** WRT-01, WRT-02, WRT-03, FMT-02

**Spec**

```
resolve target class / collection / property                      WRT-01
determine object list:
    wide          → non-time column headers                       FMT-02
    single-object → [target_object]
ensure Data File object exists                                    WRT-02
place the CSV in the tree                                         WRT-03
for each object:
    membership = sdk.get_membership_by_names(
        parent_class_lang_id, collection_lang_id, parent_name, object_name)

    sdk.add_property(
        membership     = membership,
        property_obj   = property_obj,
        value          = None,
        data_file_text = <path relative to the model>,
        data_file_tag  = data_file_obj,
        band_id        = <row band, default 1>,
        scenario_tag   = <the build's scenario>,                   WRT-05
    )
```

**The constraint that shapes this whole story.** `add_property` is the *only* documented method that accepts `data_file_text` / `data_file_tag`. `update_property`'s documented signature is `update_property(membership, property_obj, value: float!, band_id=1, period_type_id?)` — `value` is required and there is no way to set or change a data file through it. There is no `create_if_missing`, and `bulk_update_property` requires a scenario tag. **A Datafile-backed property cannot be updated in place.** Where a record must be replaced, it is `remove_property` then `add_property`. This is exactly what EE's own `ReplaceModelInputFiles` does under `--replace-existing true`, which is good corroboration that it is the intended pattern rather than a workaround.

`remove_property` returns a boolean rather than raising when nothing was there, so one code path handles both a first write and a re-write.

**Note the interaction with WRT-07.** Under the second-link approach the build does **not** remove APS's existing link — it adds its own alongside, tagged with its own scenario. `remove_property` is used only to clear the build's *own* previous records from its *own* scenario (WRT-05), never to remove a link the build did not create.

**Acceptance criteria**

1. **Given** a wide file with three object columns, **then** three property records are created, one per membership.
2. **Given** a single-object row, **then** exactly one record is created against the named object.
3. **Given** an object named in a column that does not exist in the model, **then** the build fails before any write — this is VAL-02's job and WRT-04 must not paper over it.
4. **Given** a completed row, **then** `v_property` shows each object's property with the right `data_file_path`, `data_file_object` and `scenario`.
5. **Given** a failure part-way through a row's objects, **then** the transaction rolls back and no record from that row survives.
6. **Given** APS's real model and the ten example rows, **then** all ten write and `sdk.validate()` passes.
