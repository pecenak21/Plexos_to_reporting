# PLEXOS Input Pipeline — Build Backlog

**Audience:** the build team. Assumes PLEXOS, `plexos_sdk` and the design docs. Not an APS-facing document.

**Sources this backlog is derived from:**

| Source | Role |
|---|---|
| `claude/Task2_Technical_Design.md` | The build spec. Every story cites a section of it. |
| `claude/Task2_D3_Problem_Definition.md` | Why each decision is what it is. Read when a story's rationale is challenged. |
| `APS_Plexos_Input_Pipeline_Task5.docx` (v4) | The APS-facing deliverable. Carries the scenario / Read Order / build report decisions made **after** the technical design was last written — those are marked **[LATE]** below. |
| `APS_Plexos_Input_Workbook_Example.xlsx` | The agreed interface shape for the workbook stories. |

---

## 1. How this backlog was built, and how to keep it honest

The method, so it can be repeated as the design moves:

1. **Epics come from components, not from features.** The design doc already names eight components (C1–C8). Each became an epic; nothing was invented and nothing was dropped. That keeps the backlog and the design in one-to-one correspondence — if a component is missing an epic, the design has a gap.
2. **Stories come from the things that can fail independently.** A story is one thing that can be built, demonstrated and broken on its own. "Write a Sources row" is a story; "the build script" is not.
3. **Acceptance criteria come from the design's `[PROPOSED]` rules.** Every rule the design states — "overlap is an error, not a precedence rule", "never run-stamp the data folder", "the build must not stop on a condition it can resolve" — is written as a Given/When/Then so it can be tested rather than remembered.
4. **`[CONFIRM]` items become either a spike story or a blocking question.** If we can close it ourselves it is a spike with acceptance criteria. If only APS can close it, it is listed in §5 and named on the stories it blocks. Nothing marked `[CONFIRM]` is silently assumed.
5. **Every story cites its design section.** When the design changes, a grep for the section number finds the stories that need to change with it.

**Keeping it honest:** when a design decision changes, update the design doc first and the story second. The design doc is the source of truth; this backlog is a projection of it.

---

## 2. Conventions

**Story ID prefixes** map to epics: `CDM`, `DIFF`, `FMT`, `WBK`, `BLD`, `WRT`, `VAL`, `RPT`, `PRE`, `OPS`.

**Size:** `S` ≤ 1 day · `M` 2–3 days · `L` 4–8 days. Anything larger gets split before it is started.

**Story types:**

- **Story** — produces working code behind an acceptance test.
- **Spike** — produces an answer and a written note, not production code. Time-boxed. Every spike's acceptance criterion is "the answer is recorded in the design doc and the stories it blocks are updated."
- **Chore** — infrastructure with no user-visible behaviour.

**Definition of Ready.** A story is ready when: its acceptance criteria are written; every `[CONFIRM]` it depends on is closed or explicitly deferred with a stated assumption; the real APS file it will be tested against is identified by name; and its dependencies are `Done`.

**Definition of Done.** Code merged; acceptance criteria covered by an automated test; the test runs against a **real APS artifact** (the populated model, a real source file, a real archived run) and not only a fixture; the design doc updated if the build revealed something the design got wrong.

**The standing behavioural rule**, which shapes several acceptance criteria and is easy to get backwards:

> **Model conditions get resolved and logged. Bad input data stops the build.**

A condition the build can resolve on its own — a Read Order to pick, a variable to carry across, a data file already present — is resolved, recorded in the build report, and the run continues. A source file that is malformed, has gaps, names objects that do not exist, or does not cover the model horizon stops the build before anything is written. *The run must go on; a model nobody can trust must not be produced.*

### 2.1 Two further standing rules, from APS's answers (2026-09-20)

**Anything the diff cannot catch must be stated explicitly in the build report.** APS's answer to Q10, in their words: *"It is critical that assumptions like this are called out explicitly. A diff report won't catch these."*

This is the sharpest constraint in the whole set, and it is not a reporting preference — it is a correctness requirement, because it names the gap the comparison tooling structurally cannot close. A conditional variable carried onto a new link changes what PLEXOS computes and leaves **no trace** in any of the four diff levels: the structure is unchanged, the assignment records match, and the CSV values are identical. A modeller reading a clean diff would conclude nothing happened.

So the test for every build-time decision is not "is it logged somewhere" but: **would the diff show this? If no, the build report must say it in words.** That applies to variables carried across (WRT-08), Read Orders chosen (WRT-06), files placed by inference (WRT-03), objects left uncovered (VAL-04), pre-existing model conditions tolerated (VAL-06, BLD-01) and every CLI override (WBK-06). BLD-08's ledger is the mechanism; this is the rule that decides what goes in it.

**Assume nothing about APS's current model.** Q4: *"The code can take any model as starting point. Don't assume anything from this model."*

Every figure this backlog quotes off `2026 APS_TA V3.1` — 952 objects, 84 Data File objects, 100 referenced paths, 121 files, 21 orphans, 215 generators, 8 regions, the `TimeSeries` tree name, Read Order 2000, the ten subfolder names — is a **test fixture, not a specification**. Each is legitimate in an acceptance criterion as *the expected result for that model*, and illegitimate anywhere in the code as a constant, a default, or a structural assumption. The two places this already bites: `tree_root_name` reads the model's own paths rather than hardcoding `TimeSeries` (CDM-06), and `max_read_order` reads the target model's own scenarios rather than assuming a range (CDM-07). Hold the same line everywhere else.

A useful discipline when writing a test: if the assertion would have to change when APS versions the model, it is asserting the fixture. Assert the *rule* instead, and let the number be whatever the model says.

### 2.2 The workbook is the interface

Q2: *"The workbook runs everything… It needs to be the source of truth and house necessary options."* This is a manual process run by a person, not an automated pipeline.

Consequences for the build:

- **A new option gets a Run sheet cell first.** A CLI flag is not an alternative to a cell; it is a convenience on top of one. WBK-06 is demoted accordingly.
- **No behaviour is reachable only from the command line**, with one deliberate exception below.
- **The archived workbook is the complete record of a run** — which is what makes §12's archive worth keeping, and why WBK-06 has to report every override that made the archived sheet inaccurate.

**The one exception, and it needs your sign-off:** `--force`, which lets a build write into a run folder that already exists. It stays command-line-only because a destructive option living in a cell is one someone leaves switched on from last time and does not notice. That is precisely the failure "source of truth" does not protect against — the cell would be truthful and still wrong. `--dry-run` is command-line-only for the same reason in reverse: it is a thing you do once, not a setting. Say if you would rather both were cells.

---

## 3. Epic map

| Epic | Component | What it delivers | Phase | Stories |
|---|---|---|---|---|
| **A. CDM — the model as a queryable database** | C6 | `.db` generation, DuckDB access, `v_membership` / `v_property` views, model introspection helpers | 1 | CDM-01 … CDM-08 |
| **B. Comparison engine** | C7 | `compare(old, new)`, four diff levels, standalone and build-triggered entry points | 2 | DIFF-01 … DIFF-07 |
| **C. Standard Format and file validation** | C2, C5 | Format reader, granularity inference, shape rule, checkpoint 1, blank templates | 3 | FMT-01 … FMT-05 |
| **D. Sources workbook** | C3 | Run / Data / Compare sheet readers, schema validation, CLI overrides | 4 | WBK-01 … WBK-06 |
| **E. Build orchestration** | C4 | Pre-flight, run folder, copy-forward, the build sequence, the exception ledger, archiving | 5 | BLD-01 … BLD-08 |
| **F. PLEXOS write path** | C4 | Name resolution, Data File objects, the scenario, Read Order, second link, variables, idempotency | 5 | WRT-01 … WRT-11 |
| **G. Semantic validation** | C5 | Checkpoint 2 — resolution, existence, overlap, coverage, horizon | 6 | VAL-01 … VAL-06 |
| **H. Reporting** | C8 | Two artifacts, per Q11: a **flat build report** (what the build decided) and a **diff workbook** (what changed) | 7 | RPT-01 … RPT-05 |
| **I. Preprocessors and templates** | C1 | One script per legacy source, to the established conventions | 8 | PRE-01 … PRE-07 |
| **J. Packaging and handover** | — | Repo, dependencies, CLI, logging, runbook | throughout | OPS-01 … OPS-04 |

**Phase order is not negotiable in one respect:** phase 1 before everything, because every downstream component reads through those views, and phase 2 next, because a diff that can prove "nothing changed" on an unmodified model is the cheapest correctness check available for the whole pipeline. (§14)

---

## 4. Suggested sprint sequencing

Two-week sprints, one build team. Adjust to actual capacity; the ordering is what matters.

| Sprint | Goal — stated as a demo, not a list | Stories |
|---|---|---|
| **1** | *"Here is APS's real model as a SQL database, and here are its properties in one flat table."* | OPS-01, CDM-01, CDM-02, CDM-03 (spike), CDM-04, CDM-05 |
| **2** | *"Here is a diff of a run against itself — zero differences — and against a copy we broke on purpose."* | CDM-06, CDM-07, CDM-08, DIFF-01, DIFF-02, DIFF-03, DIFF-06 |
| **3** | *"Here is a real APS source file being read, validated, and rejected for the right reasons."* | **WBK-04 first**, then FMT-01, FMT-02, FMT-03, FMT-04, FMT-05, WBK-01, WBK-02, WBK-03 |
| **4** | *"Here is a run folder created from a real model, with the whole data-file tree copied forward and every path still resolving."* | BLD-01, BLD-02, BLD-03, BLD-05, BLD-07, WBK-05, WBK-06 |
| **5** | *"Here is one property re-pointed at a file we wrote, in our own scenario, and PLEXOS reads our value."* | WRT-01, WRT-02, WRT-03, WRT-04, WRT-10 (spike) |
| **6** | *"Here is the scenario winning against APS's existing scenarios, with the variable carried across, twice in a row, identically."* | WRT-05, WRT-06, WRT-07, WRT-08, WRT-09, WRT-11 (spike) |
| **7** | *"Here is a build that refuses to run on bad data and tells you everything wrong at once."* | VAL-01 … VAL-06, BLD-04, BLD-08 |
| **8** | *"Here is the build report for a real run."* | RPT-01 … RPT-05, DIFF-04, DIFF-05, DIFF-07, BLD-06 |
| **9+** | *"Here is every legacy source feeding the pipeline unattended."* | PRE-01 … PRE-07, OPS-02, OPS-03, OPS-04 |

The write path (sprints 5–6) is deliberately late. It is the only part of the pipeline that changes a model, and it is much cheaper to get wrong once the diff exists to show exactly what it did.

---

## 5. Blocking questions — answered 2026-09-20

Carried from §15 of the technical design and put to APS. **All eighteen are now closed** — fifteen on 2026-09-20 and the last three on 2026-09-21. The answers are recorded here and carried into the stories they affect. Nothing in the backlog is waiting on APS.

### 5.1 Answered — these are now design facts

| # | Question | Answer | What changed |
|---|---|---|---|
| Q1 | Is the Cloud CLI installed and licensed? | **Yes, on every machine that will run this, with a licence for every user.** | The one hard external dependency is closed. OPS-01 and DIFF-05 unblocked; nothing in the backlog is gated on it any more. |
| Q2 | Workbook-driven or automation-triggered? | **The workbook runs everything.** This is a manual process. A person fills in the workbook and runs everything from it. *"It needs to be the source of truth and house necessary options."* | Settles §6.1.1's open question in favour of the workbook. WBK-06 is demoted from a peer interface to a convenience, and **any new option gets a Run sheet cell first** — see §2.1. |
| Q3 | Enforce `CWP MMDDYYYY` for `run_name`? | **No — accept any folder name.** | BLD-02 drops the pattern check and the warning. |
| Q4 | Is `2026 APS_TA V3.1` the standing starting point? | **It is the current working model, versioned by hand with a new name; the naming is unsettled and does not matter.** *"The code can take any model as starting point. Don't assume anything from this model."* | Becomes a standing constraint — see §2.2. Every number this backlog quotes from that model is a fixture, not a contract. |
| Q5 | Is `target_model` standing or per-run? | **Per run. Nothing is standard.** *"The code needs to be flexible to work with any model."* | CDM-07, CDM-08, VAL-05 and WRT-05 unblocked, and all four must resolve the model at runtime from the Run sheet rather than caching a default. |
| Q7 | Data File object naming? | **Adopt the file-derived convention.** | WRT-02 closed: `hr_RenewableProfile.csv` → Data File object `hr_RenewableProfile`. Existing objects are still never renamed. |
| Q8 | Is class + collection enough to disambiguate a property? | **Yes.** | WRT-01 and VAL-01 closed. The four name columns are a complete key; no fifth column needed. |
| Q10 | Should the derate / adder variables apply to build-written data? | **Yes, they should apply — "but should be called out explicitly in the build report! It is critical that assumptions like this are called out explicitly. A diff report won't catch these."** | WRT-08 confirmed as written. The second half is more important than the first and is promoted to a standing principle — see §2.1. |
| Q11 | Report format? | **Two different artifacts.** The **build report** can be flat. The **diff report** should be a workbook: a summary page, then detailed pages. | Epic H restructured. RPT-01 is now the flat build report; RPT-02 and RPT-03 are the diff workbook's summary and detail sheets. |
| Q12 | Which template shapes are needed? | **Not known yet — "let's have a slew of them."** | FMT-05 builds all eight shapes rather than waiting. |
| Q13 | Does an existing driver workbook need replacing? | **No — there is no existing infrastructure.** Today it is the PLEXOS interface and files made by hand. | WBK-04 unblocked and simplified: nothing to coexist with. Also means `Input Creation Driver.xlsx`, which appears in §12 of the design and in the deliverable's folder figure, **names a file that does not exist** and should come out of both. |
| Q14 | Adopt per-run archiving, and does the layout suit? | **Yes, and yes.** | BLD-02 and BLD-06 unblocked. The comparison capability's precondition is secured. |
| Q15 | Do modelers read values inline in Desktop's property grid? | **No.** | §3.3's known cost is not a cost. Writing everything through Datafiles is settled with no caveat. |
| Q16 | Is the validation rule set right? | **Yes.** | FMT-03 and VAL-01 … VAL-06 unblocked as specified. |
| Q18 | Where does the scenario name live? | **"Everything should live in the run sheet cell."** | `scenario_name` becomes a Run sheet row. WBK-04 adds it; WRT-05's rename behaviour becomes testable. |

### 5.2 The last three, answered 2026-09-21

| # | Question | Answer | What changed |
|---|---|---|---|
| Q6 | Which folder does a new data file go in? | **Add a `target_folder` column, defaulting to `APS_Inputs`.** | WRT-03 closed, and the rule is simpler than the one it replaces — see below. WBK-02 gains the column. |
| Q9 | Should incomplete object coverage warn or stop? | **Carry on and warn.** | VAL-04 closed: warning severity, and every uncovered object named in the build report. |
| Q17 | Does the Cloud CLI have a Change Database subcommand? | **Closed by decision rather than investigation:** *"If it's not in the SDK, let's assume it doesn't exist."* | The spike that was going to check it is dropped. Epic B is built as specified, with no caveat left hanging in its premise. |

**Q6's answer improves the placement rule rather than just settling it.** The rule it replaces put each new file under a folder named for its PLEXOS class — `TimeSeries\APS_Inputs\` now replaces `TimeSeries\Generator\`, `TimeSeries\Fuels\` and the rest. Three reasons that is better, not merely different:

1. **Nothing has to be inferred.** The class-name rule had no answer for the tree's workflow folders (`Aurora\`, `LT Builds\`, `Load Following\`, `Market\`), and no rule the build could apply to know when one of those was the right home. Now there is nothing to work out.
2. **It separates what the build wrote from what APS wrote, on disk, at a glance.** That is WRT-03's central rule — *the build only ever writes files it owns* — made visible in a folder listing rather than only in a diff. Someone can open `APS_Inputs\` and see exactly what this pipeline produced.
3. **It is still overridable per file.** A file that genuinely belongs beside its siblings goes there by being told to, in the cell, rather than by the build guessing.

---

### 5.3 Nothing is blocked

Every question put to APS is closed. The unknowns that remain are ours, and each already has a spike: **CDM-03** (the `v_property` joins), **CDM-04**'s cross-check against Energy Exemplar's own output, **CDM-06**'s absolute-path check, **CDM-07**'s `t_attribute` schema path, **WRT-10** (`remove_property` removal scope) and **WRT-11** (batch write performance). None blocks a start; CDM-03 and CDM-07 are the two that would cost real rework if left until after the code they underpin.
