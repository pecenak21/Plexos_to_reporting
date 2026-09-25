<!-- Epic intro: docs/input_pipeline/epics/D_sources_workbook.md -->
### WBK-01 — Run sheet reader

**As** the build, **I want** the run's identity and starting point from one small key/value sheet, **so that** per-run settings cannot disagree with each other.

**Type:** Story · **Size:** S · **Traces to:** §6.1 · **Depends on:** OPS-01, **WBK-04** · **Q2 / Q18 answered:** the workbook runs everything and is the source of truth; every option gets a Run sheet cell, `scenario_name` included.

**Spec**

```python
@dataclass
class RunConfig:
    run_name: str            # required
    output_root: Path        # required
    source_model: Path       # required — full path to the .xml copied as the starting point
    source_timeseries: Path | None   # blank → inferred (§6.1.1)
    target_model: str        # required — the PLEXOS model being built  [LATE]
    compare_to: Path | None  # blank → the run source_model came from; none → diff skipped
    source_root: Path        # required — what source_path on the Data sheet is relative to
    scenario_name: str       # default "Automated Inputs" — the scenario the build writes into  [LATE]
    diff_threshold: float    # default 0.005 — below this, changes are counted not listed (RPT-04)
```

**Why a separate sheet.** A per-run value cannot live on the Data sheet — the run's name would have to be repeated on every row, which lets two rows disagree about what run they belong to and makes the build's first job reconciling its own configuration.

**Why `source_model` is a path and not the name of a run.** An earlier draft had one `baseline_run` field doing both jobs. They are not the same, for a structural reason: **APS has no run folders today.** Per-run archiving is part of what this engagement proposes, so on the first build there is by definition no run folder for the starting model to live in — APS's real working model sits in an ordinary working folder. Requiring a run folder would make the first build impossible.

- `scenario_name` is the field that makes the deliverable's *"default, can be changed"* true. It is not on the example workbook's Run sheet yet — **WBK-04 adds it**. Q18 settles where it goes: *"Everything should live in the run sheet cell."*
- `diff_threshold: float` joins it for the same reason (RPT-04). The general rule from §2.2: if it changes what the build does or what the report says, it is a cell.
- Key matching is case-insensitive and whitespace-trimmed; unknown keys are an error naming the key and listing the valid ones (a typo must not read as "not set").
- `source_timeseries` blank is *not* an error — it is inferred by BLD-01.
- `compare_to` blank is *not* an error — it means "the run `source_model` came from", and if it did not come from a run folder the build skips the diff and says so. That is the expected first-run case.

**Acceptance criteria**

1. **Given** the example workbook's Run sheet, **then** a `RunConfig` is returned with every field populated as typed.
2. **Given** a missing required key, **then** an error naming it.
3. **Given** `Run_Name` with different casing, **then** it is accepted.
4. **Given** an unknown key `souce_model`, **then** an error naming it and listing the valid keys.
5. **Given** blank `source_timeseries` and blank `compare_to`, **then** both are `None` and no error is raised.
6. **Given** blank `scenario_name` and blank `diff_threshold`, **then** the documented defaults apply and the build report's run header states that they were defaulted rather than typed.
