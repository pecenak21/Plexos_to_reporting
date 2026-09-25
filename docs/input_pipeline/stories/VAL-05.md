<!-- Epic intro: docs/input_pipeline/epics/G_semantic_validation_chec.md -->
### VAL-05 — Horizon coverage

**As** the build, **I want** a source file that does not span the model's horizon to stop the build, **so that** PLEXOS does not silently fill five years of flat values.

**Type:** Story · **Size:** M · **Traces to:** §8.2; deliverable · **Depends on:** CDM-08, FMT-01 · **Q5 answered:** per-run; check against whichever model the Run sheet names.

**Why this is an error and not a warning.** PLEXOS's `Missing Value Method` defaults to `0` = **Last Value**, which fills forward from the last value present to the end of the horizon, **silently**. (See CDM-08 on where that default comes from and what still needs confirming.) A file covering 2026–2040 against a 2026–2045 model produces a model that runs, reports nothing, and holds five years of flat-lined values that look like a modelling choice. Nothing downstream — not the diff, not `sdk.validate()`, not Desktop — flags it. This check is the only thing standing between that file and a plausible-looking wrong answer.

This is squarely the "bad input data stops the build" half of the standing rule.

**Spec**

For each source file, compare its own time range against `model_horizon(db, target_model)` (CDM-08):

| Case | Severity |
|---|---|
| File ends before the horizon ends | **Error** — the fill-forward case |
| File starts after the horizon starts | **Error** — the leading-gap case |
| File extends beyond the horizon | Note only — extra data is harmless and PLEXOS ignores it |
| Gaps *within* the file's range | Already an error at checkpoint 1 (FMT-03 rule 5) |

The error names the file, its actual range, the horizon, and the size of the shortfall in years.

**Acceptance criteria**

1. **Given** a model horizon of 2026–2045 and a file covering 2026–2040, **then** an error naming the five-year shortfall.
2. **Given** a file covering 2026–2050 against the same horizon, **then** a note, and the build proceeds.
3. **Given** a file covering exactly the horizon, **then** no finding.
4. **Given** an hourly file, **then** coverage is evaluated at the file's own granularity, not coerced to years.
5. **Given** several short files, **then** all are named in one message.
