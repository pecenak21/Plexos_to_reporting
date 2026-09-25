## 14. Build sequence

Ordered so each phase produces something testable against real APS data.

| Phase | Deliverable | Depends on |
|---|---|---|
| 1 | CDM views (§9) against APS's populated model, with `t_tag` / `t_text` **and §7.5's `Read Order` attribute path** verified | — |
| 2 | Diff tool (§10), validated by diffing a run against itself (expect zero differences) then against a hand-modified copy | 1 |
| 3 | Standard Format reader + validation checkpoint 1 (§3, §8.1) | — |
| 4 | Sources workbook v1 (§6) populated with APS's real preprocessed-file inventory | 3 |
| 5 | Build script write path (§7), including the scenario, Read Order and second link (§7.5), against a scratch model copy | 1, 3, 4 |
| 6 | Validation checkpoint 2 (§8.2) | 5 |
| 7 | Build report and diff report (§11.1, §11.2) | 2, 6 |
| 8 | Preprocessors for remaining legacy sources (§4) | 3 |

Phase 1 first because everything downstream depends on those joins being right — and §7.5 now rests on an equally unverified schema path, so it joins phase 1 rather than being discovered in phase 5. Phase 2 next because a diff that can prove "nothing changed" on an unmodified model is the cheapest possible correctness check for the whole pipeline, and it exists before the write path does, which is what makes every later phase's testing meaningful.

The build backlog (`claude/Task5_Build_Backlog.txt`) expands these eight phases into a nine-sprint sequence with 67 stories.
