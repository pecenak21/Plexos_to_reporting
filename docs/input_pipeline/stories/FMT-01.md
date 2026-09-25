<!-- Epic intro: docs/input_pipeline/epics/C_standard_format_and_file.md -->
### FMT-01 — Standard Format reader with inferred granularity

**As** the build, **I want** any Standard-Format CSV read into a uniform structure with its granularity worked out from its own header, **so that** no format or granularity field is needed anywhere in the interface.

**Type:** Story · **Size:** M · **Traces to:** §3.1 · **Depends on:** OPS-01

**Spec**

```python
def read_standard_format(path: Path) -> StandardFile
# StandardFile: granularity, time_columns, data_columns, frame, path
```

Time columns are always a **prefix of** `Year, Month, Day, Period`, in that order:

| Granularity | Time columns |
|---|---|
| Annual | `Year` |
| Monthly | `Year, Month` |
| Daily | `Year, Month, Day` |
| Hourly | `Year, Month, Day, Period` |

- `Year` is mandatory. Granularity is inferred from how many of the prefix are present — **never declared**.
- A header containing `Year, Day` (a gap in the prefix) or `Month, Year` (out of order) is invalid, not a different granularity.
- Everything after the time columns is a data column. **Leading and trailing whitespace is stripped from every header; interior spacing is preserved exactly** — headers are matched against PLEXOS object names, which contain interior spaces (`Metro to APS`) but never leading or trailing ones. This is the one normalisation in the reader, and it is here rather than in VAL-02 so there is a single place it happens.
- Confirmed against every `An_` / `yr_` / `mn_` / `hr_`-prefixed CSV in APS's `Generator/`, `Fuels/`, `Emission/` and `Archive/` folders.

**Acceptance criteria**

1. **Given** each of the four valid header shapes, **then** the matching granularity is returned.
2. **Given** `Year, Day, Value`, **then** it raises naming the invalid prefix and showing the valid ones.
3. **Given** `Month, Year, Value`, **then** it raises on ordering, not on granularity.
4. **Given** a file with no `Year`, **then** it raises.
5. **Given** a header with a trailing blank column (Excel's habit), **then** the blank is dropped, not treated as an unnamed object.
6. **Given** `hr_RenewableProfile.csv` from APS's real tree, **then** granularity is hourly and every data column header is returned with interior spacing intact and outer whitespace stripped.
