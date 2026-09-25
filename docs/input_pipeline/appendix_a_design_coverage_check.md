## Appendix A — Design coverage check

Every section of the technical design, and where it is built. The `[LATE]` rows at the bottom are decisions that live only in the APS-facing deliverable — the technical design has not caught up with them yet, and **updating it is itself a piece of work someone should own.**

| § | Subject | Stories |
|---|---|---|
| 1.1 | Components C1–C8 | Epic map; OPS-04 (ownership) |
| 2.1–2.2 | Data File linkage chain | CDM-05, WRT-04 |
| 2.3 | SDK `add_property`; `update_property` constraint | WRT-04, WRT-09 |
| 2.4 | Name-based resolution | WRT-01 |
| 2.5 | The `.db` is not a given | CDM-01 |
| 3.1 | Standard Format shape and granularity | FMT-01 |
| 3.2 | Two file shapes | FMT-02 |
| 3.3 | Why everything goes through a Datafile | WRT-04. **Q15 answered: no** — modelers do not read values inline in Desktop's property grid, so §3.3's stated cost is not a cost. |
| 4 | Preprocessor conventions and patterns | PRE-01 … PRE-07 |
| 5 | Standard templates | FMT-05 |
| 6.1 | Run sheet | WBK-01, BLD-01 |
| 6.1.1 | Model and tree travel together | BLD-03, CDM-06, BLD-07 |
| 6.2 | Sources / Data sheet columns | WBK-02 |
| 6.3 | Bands and scenarios deferred | WBK-02 (internal signature) |
| 6.4 | Multiple rows per target; overlap is an error | VAL-03, PRE-07 |
| 6.5 | Property disambiguation | WRT-01, VAL-01. **Q8 answered: yes** — four name columns are a complete key. |
| 6.6 | Compare sheet | WBK-03, DIFF-07, RPT-05 |
| 7.1 | Build flow | BLD-04 |
| 7.1.1 | Pre-flight checks | BLD-01 |
| 7.2 | Writing one row | WRT-04; WRT-11 |
| 7.2.1 | Where a file lands in the tree | WRT-03; Q6 |
| 7.3 | Data File object naming | WRT-02; Q7 |
| 7.4 | Idempotency | WRT-09, WRT-10 |
| 8.1 | Checkpoint 1 | FMT-03 |
| 8.2 | Checkpoint 2 | VAL-01 … VAL-06 |
| 9.1 | `v_membership` | CDM-04 |
| 9.2 | `v_property` | CDM-03, CDM-05 |
| 9.3 | DuckDB access | CDM-02 |
| 10, 10.1 | Diff engine and input contract | DIFF-01 |
| 10.2, 10.3 | Matching and implementation | DIFF-02, DIFF-03 |
| 10.4 | The three pieces plus source files | DIFF-04, DIFF-05 |
| 11 | Report | RPT-01 … RPT-05 — **superseded by Q11**: §11's "one combined artifact" is now two, a flat build report and a diff workbook. §11 needs rewriting. |
| 12 | Run archive layout | BLD-02, BLD-06. **Q14 answered: yes to both.** §12 also names `Input Creation Driver.xlsx`, which Q13 confirms does not exist — remove it. |
| 13 | Environment and dependencies | OPS-01. **Q1 answered: installed and licensed everywhere.** §13's Change Database `[CONFIRM]` is closed by Q17 — remove the marker. |
| 14 | Build sequence | Sprint plan |
| 15 #1, #1b, #2, #3, #5 | Open items we close ourselves | CDM-03, CDM-04, CDM-06, WRT-10, WRT-11 |
| 15 #4 | Cloud CLI change-database subcommand | **Q17 closed by decision** — not in the SDK, so treated as not existing. No story. |
| 15 #6–#10, #12–#16 | Open items needing APS | Q1 … Q15 — **thirteen of fifteen answered 2026-09-20**; Q6 and Q9 restated in §5.2 |
| 15 #11 | Validation rule set never agreed with APS | **Q16 answered: yes**, the rule set and its placement are accepted |
| **[LATE]** | Scenario, Read Order, second link, variables | WRT-05 … WRT-08, CDM-07, WBK-04 |
| **[LATE]** | Build report exception ledger | BLD-08, RPT-02 |
| **[LATE]** | Horizon / Missing Value Method | CDM-08, VAL-05 |
| **[LATE]** | Data file naming (`<resolution>_<stem>.csv`) | WRT-03; WBK-04 (the `An_` vs `yr_` conflict) |
| **[LATE]** | Archived source folder name (`Copy of Source Data`) | WBK-04, BLD-06, DIFF-04 |
| **[LATE]** | Scenario name is changeable | WBK-01, WBK-04, WRT-05; **Q18** |
| **[LATE]** | Warning when a property already has a link | WRT-03 AC4 |
