<!-- Epic intro: docs/input_pipeline/epics/C_standard_format_and_file.md -->
### FMT-03 — Validation checkpoint 1: per-file, structural, before any build work

**As** whoever prepared a file, **I want** to be told everything wrong with it at once and before the build starts doing work, **so that** problems surface next to their cause.

**Type:** Story · **Size:** M · **Traces to:** §8.1, §7.1 step 8 · **Depends on:** FMT-01, FMT-02

**Spec**

Runs against the file alone and needs no model — so **most of it runs in pre-flight, before the run folder exists** (BLD-01 check 11 already resolves every `source_path`, and this checkpoint's rules can run in the same pass). §7.1 places it at step 8 for historical reasons; running it at step 3 is strictly better, because at step 8 the build has already created a run folder and copied a ~121-file tree, which is exactly the half-written state BLD-01 exists to prevent.

**Decide this once and write it into both stories.** Proposed: run the whole rule set in pre-flight; keep step 8 as a no-op assertion that it ran. If anything in the rule set turns out to need the copied tree, that part stays at step 8 and the split is stated explicitly rather than left implicit.

Rules — each returns a structured finding with file, row/column and the offending value:

| # | Rule | Severity |
|---|---|---|
| 1 | Header time columns are a valid prefix of `Year, Month, Day, Period`, in order | Error |
| 2 | At least one data column present | Error |
| 3 | No duplicate time keys within the file | Error |
| 4 | Values parse as numeric; no stray text, no blank cells in data columns | Error |
| 5 | Time coverage is contiguous — no gaps within the file's own range | Error |
| 6 | Single data column with `target_object` blank | **Warning** |

Rule 6 is a warning rather than an error because it is the one case where a user error (forgetting `target_object`) is silently plausible — the message names both possible readings so the preparer can confirm which was meant.

**All findings for all files are collected and reported together.** The build does not stop at the first bad file. One run, one complete list.

This checkpoint is **build-stopping on any error** (§7.1: "steps 8 and 10 both fail the build"). This is the "bad input data stops the build" half of the standing rule — the half that does *not* get resolved and logged.

**Acceptance criteria**

1. **Given** a file with a blank cell mid-column, **then** an error naming the row, the column header and the time key.
2. **Given** an hourly file missing 2030-03-14 hour 3, **then** a contiguity error naming that gap.
3. **Given** a file with 2026 listed twice, **then** a duplicate-key error naming the duplicate.
4. **Given** three bad files, **then** all three appear in one report and the build stops once, not three times.
5. **Given** a file with `#N/A` in a data column, **then** a numeric-parse error — not a silent `NaN`.
6. **Given** a one-column file with blank `target_object`, **then** a warning stating both readings, and the build continues.
