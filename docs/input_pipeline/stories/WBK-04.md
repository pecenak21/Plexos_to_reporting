<!-- Epic intro: docs/input_pipeline/epics/D_sources_workbook.md -->
### WBK-04 — Reconcile the workbook schema across the design doc, the deliverable and the example file

**As** the build team, **I want** one authoritative field list, **so that** three documents do not describe three interfaces.

**Type:** Chore · **Size:** S · **Traces to:** §6.1, §6.6; example workbook · **Depends on:** — · **Q13 answered:** there is no existing driver workbook and no existing infrastructure — nothing to coexist with.

**This runs first in its epic.** WBK-01 … WBK-03 are written against its output, so it cannot be the thing that cleans up after them.

**The actual discrepancies**, which will otherwise be discovered in code review:

| Field | Technical design §6.1/§6.6 | Example workbook | Resolution needed |
|---|---|---|---|
| Run sheet | has `compare_to`, `source_root`; no `target_model` | has `target_model`; no `compare_to`, no `source_root` | `target_model` is required by the scenario work **[LATE]** and must be added to the design. `compare_to` and `source_root` must be added to the workbook, or dropped with a stated reason. |
| Compare sheet | `old_run` / `new_run` / `old_model` / `new_model` / `report_output` | `model_1_path` / `model_2_path` / `output_report_path` | The workbook's names are the ones APS has seen. Adopt them; keep `old_model` / `new_model` as optional additions for the multi-`.xml` case. |
| Sheet name | "Sources" | "Data" | Pick one. The deliverable and the example workbook both say **Data**. |
| Compare sheet | §6.6 describes it as the workbook's third sheet | present as a third sheet | The deliverable's *Sources workbook* section documents only Sheet 1 and Sheet 2, and puts the comparison settings in a separate *Running a comparison* section. Say "three sheets" in the deliverable, or say plainly that the third is not part of the build's input. |
| `scenario_name` | absent | absent | **Add it as a Run sheet row.** Q18: *"Everything should live in the run sheet cell."* |
| `target_folder` | absent | absent | **Add it as an optional Data sheet column.** Blank → `APS_Inputs`. Q6, closed — build it. |
| Diff threshold | absent | absent | **Add it as a Run sheet row** (RPT-04). Per §2.2, a setting that changes the report belongs on the sheet, not only behind a flag. |
| Read Order value | absent | — | The deliverable says the build sets the scenario's Read Order "one above the maximum — **normally 9999**", and also that the highest existing is 2000. Both cannot hold: max+1 gives **2001**. The rule is right; the illustrative number is wrong. Fix the deliverable. |
| Data file naming | §7.2.1 keeps the source filename | rows use `An_`, `hr_`, `mn_`, `dy_` | The deliverable mandates `<resolution>_<source stem>.csv` with `yr_` for annual; APS's real tree and the example workbook use `An_`. Settle one prefix vocabulary and fix whichever document is wrong. |
| Archived source folder | `Upstream Inputs Referenced\` (§12) | — | The deliverable's run-folder figure calls it `Copy of Source Data/`. APS has seen that name in a figure and will look for it on disk. Pick one and change the other. |

**Q13 is closed and it removes work rather than adding it:** there is no existing driver workbook and no existing infrastructure — today it is the PLEXOS interface and files made by hand. So this workbook coexists with nothing and inherits no filename.

**One consequence to carry into the documents:** `Input Creation Driver.xlsx` appears in §12 of the technical design and in the deliverable's run-folder figure. It names a file that does not exist. Take it out of both and use `Sources_Workbook.xlsx` throughout.

**Acceptance criteria**

1. One field list exists, in the technical design, and the deliverable and example workbook are updated to match it.
2. Every renamed field is renamed everywhere in one commit — no compatibility shims for names APS has never used in anger.
3. WBK-01 … WBK-03 are written against the reconciled list, not against any one document.
