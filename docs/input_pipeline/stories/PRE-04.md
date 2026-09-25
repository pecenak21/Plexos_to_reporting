<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-04 — Power price, with nodal aggregation

**As** the pipeline, **I want** `PowerPrice 043026FCM.xls` aggregated from nodal to regional and converted, **so that** hourly price feeds `Region.Price`.

**Type:** Story · **Size:** M · **Traces to:** §4 · **Depends on:** PRE-01

**Spec**

Two steps in one script: aggregate nodal prices to the regional level, then emit hourly wide Standard Format with one column per region.

**The aggregation rule is a modelling decision, not a coding one** — simple mean, load-weighted mean, or something else. It must be stated at the top of the script as a named constant with a comment saying who decided it, and it belongs in the build report's provenance rather than buried in code. **Confirm with APS before writing it.**

**Acceptance criteria**

1. **Given** the real workbook, **then** an hourly Standard-Format CSV with one column per region.
2. **Given** the aggregation, **then** the rule used is named in the script header and reproducible by hand on one sample hour.
3. **Given** a node that maps to no region, **then** the script fails naming it rather than dropping it silently.
