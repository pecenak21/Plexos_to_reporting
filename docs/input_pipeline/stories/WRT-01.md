<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-01 — Resolve class, collection, property and object by name

**As** the build, **I want** plain names resolved against the live model, **so that** the workbook never carries a numeric ID.

**Type:** Story · **Size:** M · **Traces to:** §2.4, §6.5 · **Depends on:** CDM-05, WBK-02 · **Q8 answered: yes** — class + collection always disambiguates.

**Spec**

```python
def resolve_target(db, target_class, target_collection, target_property) -> ResolvedTarget
def resolve_object(db, class_name, object_name) -> Object
```

Uses the same lookup pattern EE's `ReplaceModelInputFiles` uses: `t_class` / `t_collection` / `t_property` name queries returning `lang_id`.

**Q8 is closed: yes, always sufficient.** The SDK resolves a property name within a collection, and the collection by name; where a property name exists on several collections, `parent_class_lang_id` disambiguates, and `target_class` + `target_collection` supplies it. The four name columns are a complete key — no fifth column, no change to WBK-02. Keep the "more than one match" error path anyway (VAL-01): it should now be unreachable, and an unreachable error that fires is the cheapest possible signal that an assumption broke.

**Acceptance criteria**

1. **Given** `Generator` / `Generators` / `Max Capacity`, **then** exactly one property resolves.
2. **Given** a property name that exists on two collections and a `target_collection` naming one, **then** the right one resolves.
3. **Given** a name that resolves to more than one match, **then** it raises listing every match with its parent class — never picks the first.
4. **Given** a misspelled class, **then** it raises listing the closest real class names. A build that stops on a typo should say which typo.
5. **Given** every row in the example workbook against APS's real model, **then** all ten resolve.
