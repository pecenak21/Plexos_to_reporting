## 9. CDM views (C6)

The `.db` **is** the canonical data model — normalized, queryable, always exactly in sync because it *is* the model in relational form. But raw `t_*` tables are still normalized: answering "what is this generator's Rating set to" means joining five tables by hand. The CDM deliverable is therefore a small set of pre-joined views, not an ETL pipeline.

### 9.1 `v_membership` — structure

Matches the shape Energy Exemplar's own `QueryWriteMemberships` exports, so it is directly comparable to their output:

```sql
CREATE VIEW v_membership AS
SELECT pc.name AS parent_class, cc.name AS child_class, col.name AS collection,
       po.name AS parent_object, co.name AS child_object
FROM t_membership m
JOIN t_object     po  ON po.object_id     = m.parent_object_id
JOIN t_object     co  ON co.object_id     = m.child_object_id
JOIN t_collection col ON col.collection_id = m.collection_id
JOIN t_class      pc  ON pc.class_id      = m.parent_class_id
JOIN t_class      cc  ON cc.class_id      = m.child_class_id;
```

### 9.2 `v_property` — resolved values and Datafile links

The view that makes the model genuinely browsable, and the substrate for the diff:

```sql
CREATE VIEW v_property AS
SELECT pc.name AS parent_class, po.name AS parent_object, col.name AS collection,
       cc.name AS child_class,  co.name AS child_object,
       p.name  AS property,     d.band_id,
       d.value        AS value,
       txt.value      AS data_file_path,     -- t_text
       df.name        AS data_file_object,   -- t_tag -> Data File object
       scn.name       AS scenario,
       dfrom.date     AS date_from,
       dto.date       AS date_to
FROM t_data d
JOIN t_membership m   ON m.membership_id  = d.membership_id
JOIN t_property   p   ON p.property_id    = d.property_id
JOIN t_collection col ON col.collection_id = m.collection_id
JOIN t_object     po  ON po.object_id     = m.parent_object_id
JOIN t_object     co  ON co.object_id     = m.child_object_id
JOIN t_class      pc  ON pc.class_id      = m.parent_class_id
JOIN t_class      cc  ON cc.class_id      = m.child_class_id
LEFT JOIN t_text      txt   ON txt.data_id   = d.data_id
LEFT JOIN t_tag       tg    ON tg.data_id    = d.data_id
LEFT JOIN t_object    df    ON df.object_id  = tg.object_id
LEFT JOIN t_object    scn   ON scn.object_id = tg.object_id
LEFT JOIN t_date_from dfrom ON dfrom.data_id = d.data_id
LEFT JOIN t_date_to   dto   ON dto.data_id   = d.data_id;
```

`[CONFIRM — ours, spike]` three joins above are sketched and need verification against the real populated model before this view is finalized:

1. **`t_tag` holds more than one kind of tag.** Datafile, scenario and expression tags all live there, distinguished by the tagged object's class. The `df` and `scn` joins must filter on class (Data File vs Scenario) rather than both blindly joining `tg.object_id` as written. A single property can also carry multiple tags, so this may need to resolve as an aggregate rather than a flat join.
2. **`t_text` rows are typed by `class_id`** (`data_file_text` vs `time_slice_text` vs `expression_text`, per the SDK's duplicate-detection rules). The `txt` join needs the Datafile-text class filter; the exact `class_id` value needs reading off the real model.

3. **`t_membership.parent_class_id` / `child_class_id` are assumed to exist.** The traced column list in §2.2 is `membership_id, parent_object_id, collection_id, child_object_id` — the class columns both views join on were not among them. They are very likely present (Energy Exemplar's own `QueryWriteMemberships` joins exactly these), but confirm rather than assume; if absent, resolve class through `t_object` instead.

All three were identified from documented behavior or another script's SQL; none was traced record-by-record in the populated model, unlike §2.2's chain. Verify all three together in phase 1 before building on them.

### 9.3 Access

DuckDB over the SQLite file — `duckdb.connect()`, `ATTACH '<run>.db' (TYPE SQLITE, READ_ONLY)`. No server, no separate database, and the same tool the diff already needs. This is exactly the pattern Energy Exemplar's own `QueryWriteMemberships` uses. `[CONFIRMED]`
