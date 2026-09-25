<!-- Epic intro: docs/input_pipeline/epics/G_semantic_validation_chec.md -->
### VAL-01 — Targets resolve to exactly one match

**As** the build, **I want** each row's class, collection and property to resolve unambiguously, **so that** an ambiguous name never silently picks one.

**Type:** Story · **Size:** S · **Traces to:** §8.2 · **Depends on:** WRT-01 · **Q8 answered: yes** — exactly one match is always achievable from class + collection + property.

**Spec**

For every Data sheet row: `target_class`, `target_collection` and `target_property` each resolve to exactly one match against the live model. Zero matches and more than one match are both **errors**. More than one should now be unreachable — Q8 confirmed that class + collection always disambiguates — but the check stays, because picking the first would produce a model that is wrong in a way no diff would flag as suspicious, and an assumption worth relying on is worth asserting.

All rows are checked and all failures reported together.

**Acceptance criteria**

1. **Given** a row with a class that does not exist, **then** an error naming the row, the value, and the closest real class names.
2. **Given** a property name that resolves on two collections and a `target_collection` naming neither, **then** an error listing both candidates with their parent classes.
3. **Given** five rows with resolution failures, **then** all five appear in one report.
4. **Given** every row in the example workbook against APS's real model, **then** no findings.
