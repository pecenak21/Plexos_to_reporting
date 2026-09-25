<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-03 — [SPIKE] Verify the `t_tag` / `t_text` / `t_membership` join assumptions

**As** the build team, **I want** the three unverified joins in the `v_property` sketch proven against the real populated model, **so that** the view everything downstream depends on is not built on an assumption.

**Type:** Spike · **Size:** M · **Time-box:** 2 days · **Traces to:** §9.2, open item #1 · **Depends on:** CDM-02

**Why this is first.** §2.2's linkage chain was traced record-by-record and is solid. The three joins below were inferred from documentation and from another script's SQL, and were **not** traced. Every downstream component reads through `v_property`. Getting this wrong means a diff that silently misses or invents changes.

**Questions to answer, each against `2026 APS_TA V3.1 - Copy.xml`:**

1. **`t_tag` holds more than one kind of tag.** Data File, scenario and expression tags all live in `t_tag`, distinguished by the tagged object's class. Confirm: what `class_id` does a Data File tag's object carry, what does a Scenario tag's carry, and can one `data_id` carry several tags at once? If it can, the view must aggregate rather than flat-join — a flat join would multiply rows and inflate every count downstream.
2. **`t_text` rows are typed by `class_id`** (`data_file_text` vs `time_slice_text` vs `expression_text`). Read the actual `class_id` value for data-file text off the model, and confirm whether a single `data_id` can carry more than one text row.
3. **Do `t_membership.parent_class_id` and `child_class_id` exist?** The traced column list in §2.2 is `membership_id, parent_object_id, collection_id, child_object_id` — the class columns both views join on were not among them. Very likely present (EE's `QueryWriteMemberships` joins exactly these). If absent, resolve class through `t_object` instead and update both view definitions.

**Acceptance criteria**

1. Each of the three questions has an answer backed by a query result pasted into the design doc, not a citation.
2. §9.2 of the technical design is rewritten with the confirmed joins and its three `[CONFIRM]` markers removed or converted to findings.
3. CDM-04 and CDM-05 are updated to match before either is started.
4. A count check is recorded: the number of `t_data` rows equals the number of `v_property` rows. Any inequality is explained (not hand-waved) before the spike closes.
