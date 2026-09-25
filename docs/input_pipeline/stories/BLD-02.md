<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-02 — Create the run folder

**As** the archive, **I want** a run folder created to a fixed shape, refused if it already exists, **so that** a run is never written over.

**Type:** Story · **Size:** S · **Traces to:** §12, §6.1 · **Depends on:** BLD-01 · **Q3 / Q14 answered:** accept any folder name, no pattern enforcement; APS will adopt per-run archiving and the layout as proposed.

**Spec**

```
<output_root>\<run_name>\                  e.g. CWP 12202026
    Inputs\
        <model>.xml
        <model>.db
        <tree>\                            named as the model's own paths expect
        Sources_Workbook.xlsx          the workbook that produced this run
        Upstream Inputs Referenced\     WBK-04: the deliverable calls this
                                       "Copy of Source Data" — pick one
        build_report.txt               plain text — what the build decided (RPT-01)
        diff_report.xlsx               workbook — what changed (RPT-02, RPT-03)
    Outputs\                               created empty; outside this milestone
```

- Refuses an existing `output_root\run_name`. `--force` is the only override and is CLI-only.
- **Q3 is closed: accept any valid folder name.** No pattern check, no naming convention, and **no warning** — a warning on a name APS deliberately chose is noise, and noise in a report is how the signal in it stops being read. The only constraints on `run_name` are the Windows ones in BLD-01 check 3.

**This layout is new, and APS has agreed to it.** They have no per-run archive today — an earlier draft read a mock-up folder on a connected drive as evidence of one, which was wrong — so the run folder, the `Inputs`/`Outputs` split and the run naming are all things this engagement asked them to adopt. **Q14: yes to both, the practice and the layout.**

That matters more than a formatting agreement, because §10's whole comparison capability rests on it: no archive, no baseline, no diff. The first build still has nothing to compare against and says so; value begins at the second run.

**Acceptance criteria**

1. **Given** a clean `output_root`, **then** the full skeleton is created with `Outputs\` present and empty.
2. **Given** an existing run folder and no `--force`, **then** nothing is created and the build fails.
3. **Given** `--force`, **then** the build proceeds and the build report's run header records that an existing folder was overwritten — §2.1: no diff level would ever show it.
3b. **Given** a `run_name` of `Q4 rerun (Ben's copy)`, **then** it is accepted without comment. Q3: any valid folder name, no pattern, no warning.
4. **Given** a build that fails at any later step, **then** the partially-created run folder is left in place with the failure recorded in it — not silently deleted, since the partial state is evidence.
