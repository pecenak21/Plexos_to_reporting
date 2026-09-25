## 8. Validation (C5)

Two checkpoints, deliberately separated by *what they can know*. `[PROPOSED]` — the two-point placement was proposed and not yet confirmed with APS, and the specific rule lists below are written here for the first time rather than carried from an agreed source. Both need APS review before implementation.

### 8.1 Checkpoint 1 — structural, per source file, before any build work

Runs against the file alone, needs no model. Catches problems close to their cause, before build effort is spent.

- Header time columns are a valid prefix of `Year, Month, Day, Period`, in order.
- At least one data column present.
- No duplicate time keys within the file.
- Values parse as numeric; no stray text or blank cells in data columns.
- Time coverage is contiguous — no gaps within the file's own range.
- Warning: single data column with `target_object` blank (§3.2).

### 8.2 Checkpoint 2 — semantic, at build time, against the live model

Needs the resolved `.db`. Runs alongside the diff because both answer the same question: *should I trust this build?*

- `target_class` / `target_collection` / `target_property` resolve to exactly one match each.
- Every object named (column header or `target_object`) exists in the model.
- Non-overlapping coverage across rows sharing a target (§6.3) — **error**.
- Coverage completeness against the class's object count — **warning**. `[ANSWERED]` — APS: carry on and warn. Partial coverage is legitimate (a source that only feeds new resources covers a fraction of a class by design), so stopping every such build would be wrong. But the warning has to do real work: **every uncovered object is named in the build report, not merely counted.** An object nobody fed keeps whatever value it had, possibly years stale, and is invisible to all four comparison levels — its property record is unchanged, so there is nothing to report as changed. Only the build report can say it. Severity is one configurable value in one place, so raising it to an error later is a setting rather than a code change.
- Time coverage spans the model's run horizon.
- `sdk.validate()` — the SDK's own integrity checks, folded in as a free first pass.

`[ANSWERED]` — the rule set above and its two-point placement are accepted as specified. No reconciliation against a Task 1 D1 rule list is outstanding.
