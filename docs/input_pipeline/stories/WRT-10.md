<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-10 — [SPIKE] `remove_property` removal scope

**As** the build team, **I want** to know exactly what `remove_property` removes, **so that** clearing our scenario cannot take out records we do not own.

**Type:** Spike · **Size:** S · **Time-box:** 1 day · **Traces to:** §7.4, open item #2 · **Depends on:** WRT-04

**The question.** `remove_property(membership, property_obj, band_id)` takes no scenario or date-range argument. If a property carries several records at the same band that differ only by scenario or date window, **a plain remove may take out more than intended** — including APS's existing link, which WRT-07 is specifically designed to leave alone.

**What to test**, against a scratch copy of the populated model:

1. A property with two records at band 1 differing only by scenario tag → what does `remove_property(membership, prop, band_id=1)` leave behind?
2. A property with two records at band 1 differing only by date window → same question.
3. Is there any scenario-scoped removal available — a parameter, a different method, or removal via the scenario object?

**Acceptance criteria**

1. Each case has an answer backed by a before/after `v_property` query recorded in the design doc.
2. If removal is not scenario-scoped, WRT-05's clear step is rewritten to remove by iterating the scenario's own records, and WRT-07 gains an acceptance criterion asserting the existing link survives.
3. §7.4's `[CONFIRM]` marker is closed.
