<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-05 — `v_property` view

**As** the assignment diff, validation and anyone asking "what is this set to", **I want** one row per property value assignment with its data file, scenario, band and date window resolved, **so that** the model is browsable and diffable as a flat table.

**Type:** Story · **Size:** M · **Traces to:** §9.2 · **Depends on:** CDM-03

**Spec**

Columns: `parent_class, parent_object, collection, child_class, child_object, property, band_id, value, data_file_path, data_file_object, scenario, date_from, date_to`.

Built from `t_data` joined to `t_membership`, `t_property`, `t_collection`, `t_object` (×2), `t_class` (×2), with LEFT joins to `t_text`, `t_tag` → Data File object, `t_tag` → Scenario object, `t_date_from`, `t_date_to`.

**The corrections CDM-03 must deliver before this is written:**

- The `t_tag` joins filter on the tagged object's class — Data File for `data_file_object`, Scenario for `scenario`. The sketch in §9.2 joins `tg.object_id` twice blindly, which is wrong.
- The `t_text` join filters on the data-file text class.
- If one `data_id` can carry multiple tags of the same kind, resolve as an aggregate.

**This view is the substrate for the diff**, so its identity columns must exactly match DIFF-03's natural key. Any column added here that is not in that key will silently fail to participate in matching.

**Acceptance criteria**

1. **Given** the populated APS model, **when** `v_property` is queried, **then** its row count equals `t_data`'s row count. A larger count means a join is multiplying rows and the view is wrong.
2. **Given** Data File object `object_id=614` ("APS hourly LMP"), **when** filtered on `data_file_object`, **then** `Offer Price` and `Bid Price` records appear for the two BESS generators, with the shared CSV path in `data_file_path` — this is the one linkage traced end-to-end in §2.2 and is the reference case.
3. **Given** a property with no data file, **then** `data_file_path` and `data_file_object` are `NULL` and `value` is populated.
4. **Given** a property carrying a scenario tag, **then** `scenario` holds the scenario's name and `data_file_object` is not contaminated with it.
5. **Given** the model's 100 distinct stored data-file paths, **when** `SELECT DISTINCT data_file_path WHERE data_file_path IS NOT NULL` is run, **then** 100 rows come back. (Without the `IS NOT NULL`, `DISTINCT` returns `NULL` as a row and the answer is 101 — the guard is the point of the criterion.)
