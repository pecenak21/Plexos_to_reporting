# Where the documents disagree

Found while preparing these docs for the build. Part A is settled by the precedence rule (design doc wins; the backlog was written before the design was last updated). Part B follows the reconciliation the backlog itself calls for in WBK-04. Part C needs a human decision before the affected story starts.

## A. Settled: the design doc is newer than the backlog

| Topic | Stale text | Use this |
|---|---|---|
| Where checkpoint 1 runs | FMT-03 says §7.1 places it at step 8 "for historical reasons" | Design §7.1 already runs it at step 5, in pre-flight, before any folder is created. Do that. Step 8 does not exist as a separate validation. |
| Archived sources folder name | BLD-02, BLD-06, DIFF-04, WBK-04 say `Upstream Inputs Referenced\` | `Copy of Source Data\`. Design §10.1 and §12 and the deliverable all use it. |
| Read Order example value | WBK-04 quotes the deliverable (v4) as saying "normally 9999" | The rule is max on the target model plus one (2001 against today's model). Deliverable v5 already says this. Never a constant. |
| Report structure | Appendix A says §11 "needs rewriting" and calls it one combined artifact | Two artifacts: flat `build_report.txt` and workbook `diff_report.xlsx`. Design §11 is already rewritten. |
| Workbook filename | Appendix A / WBK-04 say `Input Creation Driver.xlsx` appears in §12 | It does not exist. The archived workbook is `Sources_Workbook.xlsx`. |
| Validation still "proposed" | Design §8 opening paragraph says the rules need APS review | Answered: Q16 accepted the rule set and its placement. Ignore the paragraph. |
| Cross-reference | Design §8.2 says overlap is "§6.3" | It is §6.4. Bands are §6.3. |
| Diff folder contract | Design §10.1 describes each side as a run folder holding three named things | DIFF-01 and §6.6 win: neither side has to be a run folder. The rule is "find the one `.xml` in this folder". |
| Where new files are placed | WRT-03 has a paragraph placing files under `<tree>\<class>\` | Superseded by Q6 further down the same story: `target_folder` column, default `APS_Inputs`. Ignore the class-folder paragraph. |
| SQL in design §9.2 | The `df` and `scn` joins both join `tg.object_id` blindly | Known wrong. Do not copy it. CDM-03 finds the correct joins first. |
| Document names | Docs refer to `Task2_Technical_Design.md`, `claude/Task5_Build_Backlog.txt`, `Task2_D3_Problem_Definition.md` | They are `design/Task5_Technical_Design.txt` and `design/PLEXOS_Pipeline_Build_Backlog.txt` (split into `docs/input_pipeline/stories/`). The problem-definition document was not supplied. |

## B. Workbook schema: proposed resolution (this is WBK-04, and it comes first in its epic)

Checked against the example workbook itself, which is more current than WBK-04's table says. The example already has `target_model`, `scenario_name`, `diff_threshold` on the Run sheet and `target_folder` on the Data sheet.

| Field | Design doc | Example workbook / deliverable | Resolution |
|---|---|---|---|
| Sheet name | "Sources" (§6, §6.2, §7.1) | "Data" | **Data.** Update the design. |
| Run sheet keys | Nine: `run_name`, `output_root`, `source_model`, `source_timeseries`, `compare_to`, `source_root`, `target_model`, `scenario_name`, `diff_threshold` | Seven. Missing `compare_to` and `source_root` | The design's nine are the field list. **Add `compare_to` and `source_root` to the example workbook.** The example's Data rows already use bare filenames in `source_path`, which only make sense with `source_root`. |
| Compare sheet keys | `old_run`, `new_run`, `old_model`, `new_model`, `report_output` | `model_1_path`, `model_2_path`, `output_report_path` | **Workbook names**, since APS has seen them. Keep `old_model` / `new_model` as optional extras for the multi-`.xml` case, for example `model_1_file` / `model_2_file` (suggested names). Update the design. |
| Deliverable's Run table | | Lists only five keys | Add the missing rows so the APS-facing document matches. |

Rename everywhere in one commit, with no compatibility shims: APS has never used the old names.

## C. Decided by the project owner (2026-09-21)

Claude Code: these are settled. Fold the first two into the design doc (`design/Task5_Technical_Design.txt` §7.2.1 and §6.1) the first time you touch the story that needs them, then re-run `python tools/split_docs.py`.

1. **Output file naming (affects WRT-02, WRT-03). Decided.** The build names every data file it writes `<resolution>_<source stem>.csv`, with the resolution prefix taken from the granularity inferred from the file's header: `yr_`, `mn_`, `dy_`, `hr_`. **Always `yr_`, never `An_`.** `An_` exists only in APS's legacy files, and the build never writes it. The file names in the example workbook (`hr_RenewableProfile.csv` and so on) are samples of APS's existing files, not a naming contract. Two small defaults filled in by the planner, which the project owner can override: (a) if a source file's stem already starts with `yr_`, `mn_`, `dy_`, `hr_` or the legacy `An_`, strip it before adding the derived prefix, so a name is never doubled (`hr_hr_...`), and raise a warning if the stripped prefix disagrees with the inferred granularity; (b) the Data File object name is the written file's name without its extension (`hr_RenewableProfile.csv` -> `hr_RenewableProfile`), per Q7.
2. **`--force` and `--dry-run` are command-line-only. Decided, signed off.** Exactly as designed (backlog §2.2). Everything else is a Run sheet cell.
3. **Real artifacts. Decided.**
   - The sample model is `docs/sample model/2026 APS_TA V3.1 - Copy.xml`, with its data-file tree in `docs/sample model/TimeSeries/`.
   - Sample APS source files (the raw formats the preprocessors read) are in `docs/sample APS source files/`.
   - **The model is only ever copied, never opened, converted or written in place.** `ensure_db` writes a `.db` beside the `.xml`, so running it on the original would modify the sample folder. Tests copy the `.xml` into a temp directory (pytest `tmp_path`) first. The tree is several hundred MB (single CSVs up to about 95 MB), so copy the whole tree only for stories that need it (BLD-03 onward) and let everything else use the `.xml` alone or small files. Tests that need the sample skip with a clear message if it is absent. Never commit anything under `docs/sample model` or `docs/sample APS source files`.
