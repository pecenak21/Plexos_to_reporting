## 11. Reports (C8)

`[ANSWERED]` **Two artifacts, not one.** An earlier draft of this section proposed a single combined report answering both "what changed since last time" and "what might be wrong". APS: *"the build report can be flat. The diff report should be a workbook. There should be a summary page, then detailed pages."*

| Artifact | Answers | Form | Produced |
|---|---|---|---|
| **Build report** | What did the build decide, and what should I check? | Flat — one plain-text `.txt` file, `Inputs\build_report.txt` | Every build, including a failed one |
| **Diff report** | What changed since last time? | Workbook — a summary page then a detail page per level | Every build with a baseline, and every standalone comparison |

**The split is not formatting.** The build report is the home of everything a comparison structurally cannot show, and that content has nowhere sensible to sit inside a diff workbook precisely because it is what the diff does not contain. Keeping them apart stops the one thing the comparison cannot tell you from being filed behind five sheets of things it can.

### 11.1 Build report — flat text

`.txt`, not Markdown: a `.md` is a file an APS modeler has no reason to recognise, and its syntax gets in the way of the content rather than formatting it. A `.txt` opens in Notepad on any machine, pastes into an email intact, and prints. Upper-case section headings, body text wrapped at 100 columns, indented bullets, no tables.

Sections: **run header** (run name, source model, `target_model`, scenario name and the Read Order it was given with the maximum it was derived from, baseline run or "none — first run", duration, every CLI override with sheet value beside used value) · **outcome** (completed, or stopped at which step and why) · **exceptions and assumptions** · **validation findings**, errors first · **counts** · **standing notes**.

**The rule that decides what goes in the exceptions section:** *would the comparison show this?* If no, it belongs here, in words, with the object and property named. The canonical case is a conditional variable carried onto a new link (§7.5): it changes what Plexos computes while leaving structure, property records and CSV values all identical, so every level of §10 reports nothing. Also covered: the Read Order chosen, a data file placed by default, an object no source covered, a pre-existing model condition tolerated, and every CLI override.

A failed build still writes this file, holding the header, the findings and the ledger up to the point it stopped. That is the report a modeler most needs — the one explaining why nothing was produced.

### 11.2 Diff report — workbook

`Inputs\diff_report.xlsx` for a build; the Compare sheet's output path for a standalone comparison (§6.6).

**Summary sheet:** the two sides and which is the baseline; headline counts per level (source files changed; objects and memberships added / removed; property records added / removed / changed; data files whose values changed); and **a pointer to the build report by filename**, so a modeler who starts here finds the assumptions section rather than concluding from a clean diff that nothing happened.

**Detail sheets**, one per level, each a flat table with the natural key spelled out in columns so it can be filtered and pivoted:

| Level | Content | Produced by |
|---|---|---|
| Source files | Which raw inputs changed since the baseline run | Ours — no EE tooling exists for this |
| Model structure | Objects and memberships added / removed | Ours — `v_membership` diff (§9.1) |
| Assignments | Property values, Datafile pointer swaps, band/scenario/date changes | Ours — `v_property` diff (§9.2) |
| Final data | Per property, object-by-object old → new, above threshold, with MAE / RMSE / correlation / max error / mean bias | `TimeSeriesComparison` (EE) |

**Completeness rule:** every change is accounted for. Below-threshold changes are counted and summed rather than silently dropped; only above-threshold changes are itemized in full. The threshold is a Run sheet cell (`diff_threshold`), stated on every sheet that applies it, and a change that swaps a **data file pointer** is always itemized regardless — a pointer swap has no magnitude and must never be summarised away.

A first build has no baseline and produces **no diff workbook at all**; the build report's outcome line says so. An empty workbook would read as "nothing changed".
