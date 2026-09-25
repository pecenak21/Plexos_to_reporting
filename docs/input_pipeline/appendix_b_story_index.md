## Appendix B — Story index

| ID | Title | Type | Size | Sprint |
|---|---|---|---|---|
| OPS-01 | Repo, dependencies and environment check | Chore | M | 1 |
| CDM-01 | Generate a queryable `.db` from a model `.xml` | Story | S | 1 |
| CDM-02 | Read a `.db` through DuckDB, read-only | Chore | S | 1 |
| CDM-03 | Verify the `t_tag` / `t_text` / `t_membership` joins | Spike | M | 1 |
| CDM-04 | `v_membership` view | Story | S | 1 |
| CDM-05 | `v_property` view | Story | M | 1 |
| CDM-06 | Stored data-file paths | Story | S | 2 |
| CDM-07 | Scenarios, Read Order, model attachment | Story | M | 2 |
| CDM-08 | Run horizon | Story | S | 2 |
| DIFF-01 | `compare()` engine and folder→model resolution | Story | M | 2 |
| DIFF-02 | Structural diff | Story | S | 2 |
| DIFF-03 | Assignment diff | Story | M | 2 |
| DIFF-04 | Source-file diff | Story | S | 8 |
| DIFF-05 | Data diff via `TimeSeriesComparison` | Story | M | 8 |
| DIFF-06 | Diff regression harness | Chore | M | 2 |
| DIFF-07 | Standalone entry point | Story | S | 8 |
| FMT-01 | Standard Format reader | Story | M | 3 |
| FMT-02 | Shape from `target_object` | Story | S | 3 |
| FMT-03 | Checkpoint 1 | Story | M | 3 |
| FMT-04 | Standard-Format writer | Story | S | 3 |
| FMT-05 | Blank templates | Story | S | 3 |
| WBK-01 | Run sheet reader | Story | S | 3 |
| WBK-02 | Data sheet reader | Story | S | 3 |
| WBK-03 | Compare sheet reader | Story | S | 3 |
| WBK-04 | Reconcile the workbook schema | Chore | S | **3, first** |
| WBK-05 | Workbook validation and error reporting | Story | M | 4 |
| WBK-06 | CLI overrides | Story | S | 4 |
| BLD-01 | Pre-flight checks | Story | M | 4 |
| BLD-02 | Create the run folder | Story | S | 4 |
| BLD-03 | Copy model and tree forward | Story | M | 4 |
| BLD-04 | Build driver | Story | L | 7 |
| BLD-05 | Post-build path re-check | Story | S | 4 |
| BLD-06 | Archive workbook and source files | Story | S | 8 |
| BLD-07 | Orphan data-file count | Story | S | 4 |
| BLD-08 | Exception and assumption ledger | Story | M | 7 |
| WRT-01 | Resolve class / collection / property / object | Story | M | 5 |
| WRT-02 | Ensure the Data File object exists | Story | S | 5 |
| WRT-03 | Where a file lands in the tree | Story | M | 5 |
| WRT-04 | Write one Data sheet row | Story | L | 5 |
| WRT-05 | Create and clear the build's scenario | Story | M | 6 |
| WRT-06 | Read Order: max + 1 | Story | M | 6 |
| WRT-07 | The second link | Story | L | 6 |
| WRT-08 | Carry conditional variables across | Story | M | 6 |
| WRT-09 | Idempotency | Story | M | 6 |
| WRT-10 | `remove_property` removal scope | Spike | S | 5 |
| WRT-11 | Batch write path and performance | Spike | S | 6 |
| VAL-01 | Targets resolve to one match | Story | S | 7 |
| VAL-02 | Named objects exist | Story | S | 7 |
| VAL-03 | Overlapping coverage | Story | S | 7 |
| VAL-04 | Coverage completeness | Story | S | 7 |
| VAL-05 | Horizon coverage | Story | M | 7 |
| VAL-06 | `sdk.validate()` | Story | S | 7 |
| RPT-01 | Build report (flat) | Story | M | 8 |
| RPT-02 | Diff report workbook: summary sheet | Story | M | 8 |
| RPT-03 | Diff report: detail pages per level | Story | M | 8 |
| RPT-04 | Threshold and completeness rule | Story | S | 8 |
| RPT-05 | Diff report for a standalone comparison | Story | S | 8 |
| PRE-01 | Preprocessor conventions and harness | Chore | M | 9 |
| PRE-02 | Load forecast | Story | M | 9 |
| PRE-03 | Gas price | Story | S | 9 |
| PRE-04 | Power price with nodal aggregation | Story | M | 9 |
| PRE-05 | Coal price | Story | S | 9 |
| PRE-06 | Outages to daily mask | Story | M | 9 |
| PRE-07 | VER profiles | Story | M | 9 |
| OPS-02 | CLI entry points | Chore | S | 9 |
| OPS-03 | Logging | Chore | S | 9 |
| OPS-04 | Handover runbook | Chore | M | 9 |

**67 items: 56 stories, 8 chores, 3 spikes.**

Rough order-of-magnitude, at the sizes above (S = 1 day, M = 2.5, L = 6): **≈ 127 developer-days of build work**, before review, APS meetings, or anything the remaining open questions change. That is a planning number, not a commitment.

With APS's answers in, the three items most likely to move it are now **CDM-03** (if the `v_property` joins are not what we think, everything downstream shifts), **CDM-07** (the Read Order schema path is asserted, not traced — and WRT-05 and WRT-06 both stand on it), and **WRT-07** (the second link is the least-proven mechanism in the whole design, and only PLEXOS Desktop can prove it works). Q10's answer removed the fourth: the variables apply, no opt-out column needed.
