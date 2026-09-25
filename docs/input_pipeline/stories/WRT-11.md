<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-11 — [SPIKE] Batch write path and write performance

**As** the build team, **I want** to know whether a batch write exists that accepts data-file parameters, **so that** wide files touching hundreds of objects do not make a build unusably slow.

**Type:** Spike · **Size:** S · **Time-box:** 1 day · **Traces to:** §7.2, open item #3 · **Depends on:** WRT-04

**The question.** `bulk_add_property` and `bulk_update_property` are documented, but **neither takes data-file parameters** and `bulk_update_property` requires a scenario tag. The per-object loop in WRT-04 may be the only correct option. Some APS sources touch hundreds of objects — 215 generators is a real number.

**Measure before optimising.** Time a real wide file — `hr_RenewableProfile.csv` against its full object set — through the per-object loop. If the whole build is under a few minutes, this closes as "no action" and the loop stands.

**Acceptance criteria**

1. A measured wall-clock number for the largest real source, recorded in the design doc.
2. A stated answer on whether any batch path accepts `data_file_text` / `data_file_tag`.
3. If the loop is too slow **and** no batch path exists, a follow-up story is written — not an ad-hoc optimisation inside WRT-04.
4. §7.2's `[CONFIRM]` marker is closed either way.
