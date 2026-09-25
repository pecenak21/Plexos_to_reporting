<!-- Epic intro: docs/input_pipeline/epics/G_semantic_validation_chec.md -->
### VAL-04 — Coverage completeness against the class's object count

**As** a modeller, **I want** to know when objects of a targeted class are fed by no source at all, **so that** a generator missing from every file surfaces instead of silently defaulting.

**Type:** Story · **Size:** S · **Traces to:** §8.2 · **Depends on:** VAL-02 · **Q9 answered:** carry on and warn, naming every uncovered object.

**Spec**

For each property targeted by any row, compare the union of objects covered across all rows against the model's full object count for that class. Report what is not covered.

**Q9 is closed: carry on and warn.** Partial coverage is legitimate — a source that only feeds new resources covers a fraction of the class by design — so stopping every such build would be wrong.

But an uncovered object keeps whatever value it had, which may be years stale, and nothing else in the pipeline would ever mention it. So the warning has to do real work: **every uncovered object is named in the build report's assumptions section, not merely counted.** A count tells a modeller something is missing without telling them what, which is the worst of both — it prompts a search instead of answering one.

This is a §2.1 case. An object nobody fed is invisible to all four diff levels: its property record is unchanged, so there is nothing to report as changed. Only the build report can say it.

Severity is a single configurable value in one place, so raising it to "error" later is a setting rather than a code change.

Whatever the answer, the count and the list go in the build report either way.

**Acceptance criteria**

1. **Given** the model's full generator set and a source covering part of it, **then** the finding names every uncovered generator and the count. (The model held 215 generators when queried during design — confirm the current count rather than hard-coding it.)
2. **Given** full coverage, **then** no finding.
3. **Given** the severity set to "error", **then** the build stops — the switch lives in one place, not scattered through the checks.
4. **Given** the finding, **then** the build report's assumptions section lists every uncovered object **by name**, not just the count — a count says something is missing without saying what.
5. **Given** the severity later raised to "error", **then** it is a single configuration change with no edit to the check itself.
