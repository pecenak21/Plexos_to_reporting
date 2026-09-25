<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-01 — Pre-flight checks

**As** whoever starts a build, **I want** a misconfigured run to fail in a second with an empty disk, **so that** I am not cleaning up a half-written run folder.

**Type:** Story · **Size:** M · **Traces to:** §7.1.1 · **Depends on:** WBK-05, CDM-06

**Spec**

Everything checkable before a single file is created, checked there. All findings collected and reported **together**, never one per run attempt.

| # | Check | On failure |
|---|---|---|
| 1 | `output_root` exists and is writable | Error |
| 2 | `output_root\run_name` does **not** exist | Error, unless `--force` |
| 3 | `run_name` is a valid Windows folder name — no reserved characters, not a reserved device name, and within path-length limits **once the deepest data-file path is appended** | Error |
| 4 | `source_model` exists and is readable | Error |
| 5 | **Every data-file path the source model references resolves under `source_timeseries`** | Error, listing every missing file with its stored path |
| 6 | `source_timeseries`, when blank, is inferred as the folder beside `source_model` whose name matches `tree_root_name(db)` | Error naming the folder that was expected |
| 7 | No stored data-file path is absolute (CDM-06) | **See note below** |
| 8 | Free space at `output_root` exceeds the size of the tree about to be copied | Error |
| 9 | `compare_to`, if named, exists and contains a model | Error |
| 10 | `compare_to` blank **and** `source_model` did not come from a run folder | **Note, not error** — the diff will be skipped; this is the expected first-run case |
| 11 | `source_root` exists, and every `source_path` on the Data sheet resolves under it | Error, listing every missing file at once |
| 12 | `target_model` exists in the source model | Error listing the model names that do exist |

**Check 3 is less generous than it looks.** APS's real paths already run to `TimeSeries\Generator\An_NameplateCapacity_2026_Q1_Enhanced_Transmission_STP.csv`. Adding `output_root\run_name\Inputs\` in front of that eats the headroom fast, and Windows fails a 260-character path with an error nobody traces back to the run name.

**Check 7 needs a decision before it is coded.** An absolute stored path is a *model* condition — something already in APS's model — not malformed input someone typed, so the standing rule points at "resolve and log", not "stop". But an absolute path survives a copy while still pointing back at the original model's folder, so the new run would silently read the old run's data. Proposed: **fail the build only if the absolute path resolves outside the run folder**, log it otherwise, and find out first whether any exist at all (CDM-06 flags them; run it against the real model before this story is sized). Do not ship a rule that stops every build on APS's real model over a legacy path nobody has looked at yet.

**Check 5 is the one that matters most.** A model whose tree is missing still opens in PLEXOS Desktop and simply reads nothing. The failure is silent, which is exactly why it is checked up front rather than discovered in Desktop three days later.

**Acceptance criteria**

1. **Given** a run folder that already exists, **then** the build fails before creating anything, and `--force` is named in the message as the way past it.
2. **Given** a source model whose tree is missing 12 files, **then** all 12 are listed with their stored paths, in one message.
3. **Given** a `run_name` that pushes the deepest path past the limit, **then** an error naming that deepest path and its length.
4. **Given** blank `source_timeseries` and a folder named `TimeSeries` beside the model, **then** it is inferred and the build proceeds.
5. **Given** blank `source_timeseries` and no such folder, **then** an error naming `TimeSeries` as the expected folder name.
6. **Given** blank `compare_to` and a source model in a plain working folder, **then** a note is recorded, the diff is skipped, and **the build proceeds** — this is not a failure.
7. **Given** four separate pre-flight failures, **then** all four are reported in one message and `output_root` is untouched.
