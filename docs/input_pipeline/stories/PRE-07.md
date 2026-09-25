<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-07 — VER profiles

**As** the pipeline, **I want** the renewable profile sources converted, **so that** hourly `Generator.Rating` is fed for both existing and planned resources.

**Type:** Story · **Size:** M · **Traces to:** §4, §6.4 · **Depends on:** PRE-01

**Spec**

Two output files, matching the model's existing split: `hr_RenewableProfile.csv` (existing renewables) and `hr_NewResRenProfile.csv` (planned resources). Both feed hourly `Rating`, on **disjoint** generator sets.

This is the reference case for VAL-03: two Data sheet rows, same target, different objects, no overlap — allowed and already how APS works. If the two files ever come to share a generator, VAL-03 stops the build and names it, which is the intended behaviour.

**Acceptance criteria**

1. **Given** the real sources, **then** two hourly Standard-Format CSVs are produced.
2. **Given** both outputs, **then** their column sets are disjoint and VAL-03 reports nothing.
3. **Given** a generator deliberately added to both, **then** VAL-03 names it and the build stops.
4. **Given** the outputs, **then** every header matches a `Generator` object name exactly.
