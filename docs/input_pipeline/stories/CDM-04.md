<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-04 — `v_membership` view

**As** the structural diff, **I want** one row per relationship in the model with every side named, **so that** structure can be compared without joining five tables at each call site.

**Type:** Story · **Size:** S · **Traces to:** §9.1 · **Depends on:** CDM-03

**Spec**

Columns: `parent_class, child_class, collection, parent_object, child_object`. Joins `t_membership` to `t_object` twice, `t_collection` once, `t_class` twice. Shape deliberately matches Energy Exemplar's `QueryWriteMemberships` output so it can be compared row-for-row against theirs.

**Acceptance criteria**

1. **Given** the populated APS model, **when** `v_membership` is queried, **then** row count equals `SELECT count(*) FROM t_membership` — no join drops or multiplies rows.
2. **Given** a known generator, **when** filtered to it, **then** its region membership appears with both class names and the collection name spelled as PLEXOS spells them.
3. **Given** the view, **then** no column is `NULL` for any row — every membership has both ends and a collection.
4. **Cross-check:** running EE's `QueryWriteMemberships` against the same model produces the same row set (order-insensitive). Any difference is investigated before this story is Done. *(This absorbs open item #5.)*
