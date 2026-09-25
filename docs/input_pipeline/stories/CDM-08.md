<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-08 — Model introspection: run horizon

**As** horizon validation, **I want** the start and end of the model's simulation horizon, **so that** a source file that stops short of it can be rejected.

**Type:** Story · **Size:** S · **Traces to:** §8.2; VAL-05 · **Depends on:** CDM-05 · **Q5 answered:** per-run; read the horizon from whichever model the Run sheet names.

**Spec**

```python
def model_horizon(db, model_name: str) -> tuple[date, date]
```

- The horizon comes from the Horizon object attached to the named model (`Date From` / `Date To`, or `Date From` + `Step Count` × step type — handle both forms; PLEXOS permits either).
- Return the resolved concrete dates, not the raw attribute values.

**Why this matters more than it looks.** PLEXOS's `Missing Value Method` defaults to `0` = Last Value, which fills a short data file forward to the end of the horizon **silently**. (Source: PLEXOS's own documentation of the property, reviewed during design. The deliverable is deliberately more cautious — *"this may change as it is discovered how Plexos handles this method"* — so treat the default as established and the exact fill behaviour as worth one confirming test.) A source file covering 2026–2040 against a 2026–2045 model produces a model that runs, reports nothing, and holds five years of flat-lined values. This function is what makes VAL-05 possible, and VAL-05 is a build-stopping error for exactly that reason.

**Acceptance criteria**

1. **Given** APS's real model, **then** the horizon's start and end dates are returned and match what PLEXOS Desktop shows for the same model.
2. **Given** a horizon expressed as start + step count, **then** the resolved end date is correct for the step type.
3. **Given** a model with no horizon attached, **then** it raises rather than returning a default range.
