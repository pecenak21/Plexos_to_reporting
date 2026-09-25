<!-- Epic intro: docs/input_pipeline/epics/H_reporting_the_build_repo.md -->
### RPT-04 — Significance threshold and the completeness rule

**As** a modeller, **I want** small changes counted rather than listed, **so that** the diff report is readable without hiding anything.

**Type:** Story · **Size:** S · **Traces to:** §11 · **Depends on:** RPT-03

**Spec**

**Every change is accounted for.** Below-threshold changes are **counted and summed** rather than dropped; only above-threshold changes are itemised in full.

- The threshold is configurable per level and has a stated default (proposed: 0.5% relative change, or any absolute change on a property with no meaningful scale). Per §2.2 it gets a **Run sheet cell**, not only a CLI flag.
- Every sheet that applies a threshold states the threshold **on the sheet**, and states the count and total magnitude of what fell below it.
- A change that is below threshold but swaps a **data file pointer** is always itemised — a pointer swap has no magnitude and must never be summarised away.

**Acceptance criteria**

1. **Given** 400 changes of which 380 are below threshold, **then** 20 rows are itemised and a line states *"380 further changes below the 0.5% threshold, total magnitude X"*.
2. **Given** a threshold of 0, **then** everything is itemised.
3. **Given** a pointer swap of any magnitude, **then** it is itemised.
4. **Given** any thresholded sheet, **then** the threshold value appears on it.
5. **Given** the Run sheet's threshold cell, **then** changing it changes the report without a code change.
