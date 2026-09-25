<!-- Epic intro: docs/input_pipeline/epics/C_standard_format_and_file.md -->
### FMT-05 — Blank standard templates

**As** APS, **I want** blank CSVs to fill in for data not currently fed into the model at all, **so that** new data needs no code.

**Type:** Story · **Size:** S · **Traces to:** §5 · **Depends on:** FMT-04 · **Q12 answered:** which shapes are needed is not known yet — *"let's have a slew of them."* Build all eight.

**Spec**

Eight shapes maximum — granularity × shape:

```
template_wide_annual.csv       Year, <Object 1>, <Object 2>, ...
template_wide_monthly.csv      Year, Month, <Object 1>, ...
template_wide_daily.csv        Year, Month, Day, <Object 1>, ...
template_wide_hourly.csv       Year, Month, Day, Period, <Object 1>, ...
template_single_annual.csv     Year, Value
template_single_monthly.csv    Year, Month, Value
template_single_daily.csv      Year, Month, Day, Value
template_single_hourly.csv     Year, Month, Day, Period, Value
```

**Build all eight.** Q12: which are actually needed is not known yet — *"let's have a slew of them."* Generate them from one definition rather than hand-maintaining eight files, so a format change touches one place and an unused template costs nothing.

A filled-in template is indistinguishable from preprocessor output downstream: same `source_path` column, same handling, no flag anywhere.

**Acceptance criteria**

1. **Given** all eight templates, **then** each is generated and `read_standard_format` accepts it (as an empty file with a valid header). Q12: build the full set now; an unused template costs nothing and a missing one costs a round trip.
2. **Given** a template filled with plausible values, **then** checkpoint 1 passes it.
3. **Given** the hourly templates, **then** the `Period` column's expected range is documented in the file's companion note — 1–24 vs 0–23 is exactly the kind of thing that is obvious to whoever wrote it and to nobody else.
