## 15. Open items

**Every item that needed APS was answered on 2026-09-20 / 21.** The answers are recorded below against the item they close and carried into the build backlog (`claude/Task5_Build_Backlog.md`), which is where the resulting stories live. What remains is ours to verify.

**Still open — verify against the model or the SDK, no APS input needed:**

| # | Item | Blocks |
|---|---|---|
| 1 | `t_tag`, `t_text` and `t_membership` class-column joins verified against the real populated model (§9.2) | Phase 1 |
| 1b | Confirm data-file paths are always relative to the model file and never absolute — one absolute path in a source model would survive a copy while pointing back at the original (§6.1.1) | Phase 5 |
| 2 | `remove_property`'s removal scope where several records share a band but differ by scenario or date window (§7.4) | Phase 5 |
| 3 | Whether any batch write path accepts `data_file_text`/`data_file_tag`, or the per-object loop is the only option (§7.2) | Phase 5 — performance only |
| 5 | Cross-check `v_membership` against Energy Exemplar's `QueryWriteMemberships` output on the same model (§10.4) | Phase 1 — validation of our view |

Item 1c is added by the scenario work and was not in the original list: **the `Read Order` attribute's schema path** (`t_attribute` / `t_attribute_data`, and the Model↔Scenario membership) is inferred rather than traced, and the write path's scenario priority rests on it entirely. Verify it alongside item 1, in phase 1.

**Closed — answered by APS:**

| # | Item | Answer |
|---|---|---|
| 4 | Read the Cloud CLI's own reference docs to rule out a Change Database subcommand (§13) | **Closed by decision.** If it is not in the SDK, treat it as not existing. §10 builds the structural diff; no further investigation. |
| 6 | Is the PLEXOS Cloud CLI installed and licensed (§13) | **Yes**, on every machine that will run this, with a licence for every user. |
| 7 | Workbook-driven or automation-triggered (§6.1) | **The workbook runs everything.** A person fills it in and runs everything from it; it is the source of truth and houses the options. CLI arguments are a convenience on top of the sheet, never an alternative to it. |
| 8 | `run_name` naming convention (§6.1) | **Accept any valid folder name.** No pattern, no enforcement, and no warning. |
| 8b | Is `2026 APS_TA V3.1` the standing starting point (§6.1) | It is the current working model, versioned by hand under a new name; the naming is unsettled and does not matter. **Any model can be the starting point — assume nothing about this one.** Every figure quoted from it in this document is a test fixture, not a specification. |
| 8c | Will APS adopt per-run archiving, and does the layout suit (§12) | **Yes to both.** |
| 8d | Do the tree's non-class folders follow a rule the build can apply (§7.2.1) | **Superseded.** The build no longer infers a folder: an optional `target_folder` column on the Sources sheet places the file, defaulting to `APS_Inputs` under the tree root. See §7.2.1. |
| 9 | Data File object naming (§7.3) | **Adopt the file-derived convention.** Objects already in the model keep their names and are never renamed by a build. |
| 10 | Is class + collection always sufficient to disambiguate a property (§6.5) | **Yes.** The four name columns are a complete key. |
| 11 | Validation placement and rule set (§8) | **Accepted as specified** — both checkpoints and their placement. |
| 12 | Coverage completeness — warning or error (§8.2) | **Warning.** The run carries on, and every uncovered object is named in the build report. |
| 13 | Report format (§11) | **Two artifacts, not one.** The build report is flat plain text; the diff report is a workbook with a summary page then detail pages. §11 needs rewriting to match. |
| 14 | Which template shapes are actually needed (§5) | **Not known yet** — build all eight. |
| 15 | Does an existing driver workbook need replacing (§6) | **No.** There is no existing infrastructure: today the model is edited through the PLEXOS interface and the data files are made by hand. |
| 16 | Do modelers read values inline in Desktop's property grid (§3.3) | **No.** §3.3's stated cost of writing everything through Datafiles is not a cost. |

**This document is current as of 2026-09-21.** The decisions taken after its first draft — the scenario mechanism, the Read Order rule and the second link (§7.5); the two-report split (§11); the `target_folder` placement rule (§7.2.1); and the `target_model`, `scenario_name`, `diff_threshold` and `target_folder` columns (§6.1, §6.2) — are folded in. The build backlog (`claude/Task5_Build_Backlog.txt`) carries the same decisions as stories with acceptance criteria; where the two ever disagree, this document is the design and the backlog is the projection of it.
