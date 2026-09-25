## 12. Run archive layout

**This is a proposed practice, not an existing one.** `[PROPOSED]` APS has no per-run archive today — an earlier draft of this document read a mock-up folder on the connected drive as evidence of one, which was wrong. The run folder, the `Inputs`/`Outputs` split and the run naming are all part of what this engagement is asking APS to adopt.

That reframes the archive from plumbing into a dependency worth stating plainly: **§10's whole comparison capability rests on it.** A diff needs a prior run in a known shape. No archive, no baseline, no diff — so adopting this practice is not an implementation detail, it is the precondition for the capability APS asked for. The first build has nothing to compare against and says so; value begins at the second run.

Proposed layout:

```
<run_name>/                            e.g. CWP 12202026
    Inputs/
        <model>.xml                    the model Plexos runs
        <model>.db                     the same model, queryable — the CDM
        <tree>/                        the data files — named as the model's own
                                       paths expect, never run-stamped (§6.1.1)
            APS_Inputs/                everything this build wrote (§7.2.1)
        Sources_Workbook.xlsx          the Run + Sources sheets used, for provenance
        Copy of Source Data/           the source files this run consumed
        build_report.txt               what the build decided (§11.1)
        diff_report.xlsx               what changed since the baseline (§11.2)
    Outputs/
        ...                            outside the scope of this milestone
```

The `.xml`, the `.db` and the data tree all fall out of the build anyway (§7.1) — retaining them costs nothing beyond not deleting them. The workbook copy is what makes an archived run self-describing: open it and you can see which model it was built from and which sources fed it. Its Run and Sources sheets are the record; its Compare sheet is scratch space and says nothing about that run (§6.6).

**The data folder's name is not free.** It must match what the model's stored paths expect (§6.1.1) — a run-stamped name like `Timeseries _ CWP 09022026` would resolve nothing. The run stamp belongs on the run folder above it.

`[ANSWERED]` — APS have reviewed the layout and will adopt per-run archiving: **yes to the practice, yes to the layout as drawn.** That secures the precondition §10's whole comparison capability rests on.

The `.db` costs nothing extra to retain — the build already produces it as a working copy on the way to writing the `.xml` (§7.1 steps 8 and 16). Keeping it is a matter of not deleting it.

**Naming, settled (2026-09-20).** The workbook is archived as `Sources_Workbook.xlsx`. An earlier draft asked whether it should instead take over an existing `Input Creation Driver.xlsx` filename — APS have confirmed there is no existing driver workbook and no existing infrastructure of any kind: today the model is edited through the PLEXOS interface and the data files are made by hand. There is nothing to coexist with and no filename to inherit.
