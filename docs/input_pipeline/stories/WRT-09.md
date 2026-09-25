<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-09 — Idempotency: build twice, get the same model

**As** the build team, **I want** a repeated build against unchanged inputs to produce an identical model, **so that** "nothing changed" is provable.

**Type:** Story · **Size:** M · **Traces to:** §7.4 · **Depends on:** WRT-04 … WRT-08, DIFF-03

**Spec**

Re-running a build against the same inputs must not duplicate records. Because a Datafile-backed property cannot be updated in place (§2.3), idempotency comes from the clear-and-rewrite of the build's own scenario (WRT-05) plus the remove-then-add sequence, not from an update call.

What makes that safe is the SDK's own duplicate-detection rule: two property records are identical only if membership, property, `band_id`, value, texts and tags all match, with different scenario tags, Datafile tags or date ranges each counting as distinct.

**The unresolved part, and it is not cosmetic.** `remove_property` targets membership + property + band and takes **no scenario argument**. Under the second link, APS's record and ours share membership, property and band and differ only by scenario — so a plain remove may take **both**. WRT-10 is the spike that answers this and it must land before this story is implemented. If removal is not scenario-scoped, the clear step in WRT-05 iterates the scenario's own records instead, and this story's mechanism changes accordingly. Do not write code against the assumption that it is scoped.

The same identity rule drives the diff (DIFF-03) — one definition, used for writing and for diffing.

**Acceptance criteria**

1. **Given** two builds from the same workbook against the same source model, **then** `compare()` between the two run folders reports zero differences at every level.
2. **Given** a second build, **then** the record count in `v_property` is unchanged — no accumulation.
3. **Given** a second build, **then** no second Data File object is created for any source (WRT-02 case 2).
4. **Given** a build, then a change to one CSV, then another build, **then** the diff reports exactly that one data change and no structural change.
