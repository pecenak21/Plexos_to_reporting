<!-- Epic intro: docs/input_pipeline/epics/I_preprocessors_and_legacy.md -->
### PRE-06 — Outages to daily availability mask

**As** the pipeline, **I want** `Outages Thursday May 21 2026 – Wednesday December 31 2031.xlsx` expanded to a daily mask, **so that** generator availability feeds `Generator.Units`.

**Type:** Story · **Size:** M · **Traces to:** §4 · **Depends on:** PRE-01

**Spec**

Event expansion, following APS's existing `Maintenance.py`: an event list with start/end dates becomes a dense daily calendar, one 0/1 column per unit.

**Pre-expand; do not emit sparse intervals.** APS's convention is the dense timeseries, and `t_date_from` / `t_date_to` interval overrides are deliberately not used.

**The horizon trap is real here.** The source covers May 2026 – December 2031. The model horizon runs well past that. An outage file that stops in 2031 would, under `Missing Value Method = 0`, hold every unit at its 2031-12-31 availability for the rest of the horizon — a unit out on the last day would stay out for fourteen years. VAL-05 stops the build on this, and **the preprocessor must decide explicitly what happens past the source's end date** — pad with 1 (available), or stop and require a longer source. Confirm with APS; state the choice in the script header and in the build report.

**Acceptance criteria**

1. **Given** the real workbook, **then** a daily Standard-Format CSV with one 0/1 column per unit.
2. **Given** an outage spanning a month boundary, **then** every day in it is 0 and the days either side are 1.
3. **Given** the model horizon extending past the source, **then** the padding decision is applied explicitly and recorded, not left to PLEXOS's fill-forward.
4. **Given** the existing `Maintenance.py` output for the same input, **then** values match over the overlapping range.
