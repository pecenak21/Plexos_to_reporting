<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-04 — Build driver: the run sequence

**As** the build team, **I want** the nineteen steps expressed as one readable sequence with explicit failure semantics, **so that** the order is in one place rather than distributed through the code.

**Type:** Story · **Size:** L · **Traces to:** §7.1 · **Depends on:** BLD-01…03, WRT-01…08, VAL-01…06

**Spec**

```
 1. Read Run sheet                              WBK-01
 2. Read source model's stored data-file paths   CDM-06
 3. PRE-FLIGHT CHECKS                            BLD-01   — before anything is created
 4. Create output_root\run_name\Inputs\          BLD-02
 5. Read Data sheet                              WBK-02
 6. Copy source .xml AND its whole tree          BLD-03   — never edit the source in place
 7. xml_to_db(new_run.xml, new_run.db)           CDM-01
 8. VALIDATION CHECKPOINT 1 (structural)         FMT-03   — FAILS THE BUILD
 9. Resolve every target against the .db         WRT-01
10. VALIDATION CHECKPOINT 2 (semantic)           VAL-*    — FAILS THE BUILD
11. Create / clear the build scenario            WRT-05   [LATE]
12. Write each Data file into the tree           WRT-03
13. For each row: write the Datafile link        WRT-04, WRT-07, WRT-08
14. sdk.validate()                               VAL-06
15. db_to_xml(new_run.db, new_run.xml)
16. Re-check every data-file path resolves       BLD-05
17. Run diff vs compare_to                       DIFF-01
18. Emit build report (flat) + diff report      RPT-01, RPT-02, RPT-03
19. Archive workbook + source files              BLD-06
```

**Failure semantics, and they are not uniform:**

- Steps 8 and 10 **fail the build**. A build that produces a model nobody can trust is worse than no build.
- Every model condition the build can resolve — a Read Order to choose, a variable to carry, a data file already present, a file to place — is resolved, recorded in the exception ledger (BLD-08), and the run continues.
- All writes (steps 11–13) are wrapped in **one `sdk.transaction()` per run**, so a failure leaves no partial model.
- Step 17 failing does **not** fail the build. The model is already built and valid; a diff that could not run is reported as such.

**Acceptance criteria**

1. **Given** a checkpoint-1 error, **then** the build stops in pre-flight (FMT-03), nothing is created under `output_root`, and the findings are reported to the console and written to a findings file beside the workbook.
2. **Given** a failure inside step 13, **then** the transaction rolls back and the `.db` holds no partial writes.
3. **Given** a `compare_to` that cannot be resolved, **then** steps 1–16 complete, the build report is written, no diff workbook is produced, and the build report's outcome line says why — an empty diff workbook would read as "nothing changed".
4. **Given** a clean run against APS's real model, **then** all nineteen steps complete and the run folder matches BLD-02's layout exactly.
5. Each step logs its start, end and duration — a build that takes twenty minutes needs to say where they went.
