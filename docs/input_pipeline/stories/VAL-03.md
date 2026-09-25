<!-- Epic intro: docs/input_pipeline/epics/G_semantic_validation_chec.md -->
### VAL-03 — Overlapping coverage across rows sharing a target

**As** the build, **I want** two rows that target the same property and the same object to stop the build, **so that** nobody has to remember a precedence rule.

**Type:** Story · **Size:** S · **Traces to:** §6.4, §8.2 · **Depends on:** VAL-02

**Spec**

Several rows may share the same `target_class` / `target_collection` / `target_property`, each covering a **different** set of objects. This needs no special mechanism — PLEXOS properties are written per object-membership, not atomically per class. APS already does this: `hr_RenewableProfile.csv` (existing renewables) and `hr_NewResRenProfile.csv` (planned resources) both feed hourly `Rating`.

**But if two rows sharing a target cover any of the same objects, the build fails and names the overlapping objects.** No row-order winner, no "last one wins" — nothing anyone has to remember. This is a deliberate refusal to add a precedence rule.

**Acceptance criteria**

1. **Given** the two VER rows from the example workbook with disjoint object sets, **then** no finding.
2. **Given** the same two rows with one generator appearing in both files, **then** an error naming that generator, both rows and both files.
3. **Given** two rows sharing a target and overlapping on 12 objects, **then** all 12 are named, not just the first.
4. **Given** the v1 interface, where every row is band 1 (§6.3), **then** overlap is evaluated on (target, object) alone. The overlap key is written as (target, object, band) from the start so that adding a band column later is a column change rather than a rule change — but there is no band escape hatch in v1 and the tests must not imply one.
