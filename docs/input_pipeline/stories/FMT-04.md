<!-- Epic intro: docs/input_pipeline/epics/C_standard_format_and_file.md -->
### FMT-04 — Standard-Format writer

**As** the preprocessors and the build, **I want** one function that writes Standard Format, **so that** every file entering the pipeline is written the same way.

**Type:** Story · **Size:** S · **Traces to:** §3.1, §4 · **Depends on:** FMT-01

**Spec**

```python
def write_standard_format(frame, path: Path, granularity: Granularity) -> Path
```

- Writes time columns first, in prefix order, then data columns in the order given.
- No index column, no BOM, `\r\n` line endings (these land on a Windows file share and get opened in Excel), consistent numeric formatting.
- **Deterministic:** the same frame written twice produces byte-identical files. This is what makes preprocessor idempotency (PRE-01) and the source-file diff (DIFF-04) meaningful — a file that re-serialises differently every run would show as changed on every run and train everyone to ignore that level.

**Acceptance criteria**

1. **Given** the same frame written twice, **then** the two files are byte-identical.
2. **Given** a file written by this function, **then** `read_standard_format` reads it back with the same granularity and values.
3. **Given** a float that is exactly an integer, **then** its written form is stable across runs.
4. **Given** an object name containing a comma, **then** it is quoted and reads back intact.
