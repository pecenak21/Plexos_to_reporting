<!-- Epic intro: docs/input_pipeline/epics/B_comparison_engine.md -->
### DIFF-02 — Structural diff: memberships added and removed

**As** a modeller, **I want** to see which objects and relationships appeared or disappeared, **so that** structural change is separated from value change.

**Type:** Story · **Size:** S · **Traces to:** §10.2, §10.4 · **Depends on:** CDM-04, DIFF-01

**Spec**

Two comparisons, not one:

1. **Memberships.** FULL OUTER JOIN `old.v_membership` to `new.v_membership` on the full natural key — `(parent_class, parent_object, collection, child_class, child_object)` — returning rows where either side is `NULL`, classified `added` / `removed`.
2. **Objects.** A separate FULL OUTER JOIN on `(class name, object name)` from `t_object` + `t_class`. §10.2 defines Object as its own record type with its own natural key, and it cannot be derived from the membership diff: **a Data File object is wired in through `t_tag`, not `t_membership`** (§2.2's traced chain), so it has no membership row at all. Since WRT-02 creates one Data File object per new source, deriving objects from memberships would make the pipeline's single most common structural addition invisible at this level.

**Accepted limitation, confirmed as expected:** a renamed object appears as one removal plus one addition, not a rename. Natural-key matching by name cannot detect renames and this schema has no stable identifier to fall back on. Do not build heuristics for it.

**Acceptance criteria**

1. **Given** a model compared against itself, **then** zero structural differences.
2. **Given** a copy with one generator added, **then** exactly its object add and its membership adds are reported.
2b. **Given** a copy with one Data File object added and no membership, **then** the object add is reported — the case the membership join cannot see.
3. **Given** a copy with one generator renamed, **then** one removal and one addition are reported, and the report labels this as the known rename behaviour rather than leaving the reader to infer it.
4. **Given** two independently-generated `.db` of the same model, **then** zero differences — proving surrogate IDs are not participating in matching.
