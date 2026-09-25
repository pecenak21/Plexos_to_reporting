# Kickoff: running the input-pipeline build with Claude Code

## 1. Before the first session

- Check the branch. This repo currently has `ingestion_main` checked out. Make sure that is the feature branch you want, and commit this kit as one commit ("Add input pipeline design docs and Claude Code kit") so the history starts clean.
- Install the slash commands. Claude Code reads them from `.claude\commands\`, which this session is not allowed to write to, so they were put in `docs\input_pipeline\claude_commands\`. From the repo root, run once in a terminal:

  ```
  xcopy /I /Y docs\input_pipeline\claude_commands .claude\commands
  ```

  (If `.claude\commands` does not exist, `/I` creates it.) After that, `/orient`, `/story` and `/verify-story` are available.
- Start Claude Code from the repo root (`C:\Users\cto\Plexos_to_Reporting`) and give it the Energy Exemplar scripts repo: `/add-dir C:\Users\cto\PLEXOS-Cloud-Automation-Scripts`.
- The sample model and sample APS source files are already in `docs/sample model/` and `docs/sample APS source files/`. Claude Code only ever copies them. Make sure the machine also has the PLEXOS Cloud CLI and `plexos_sdk`.
- Make sure the two sample folders are not committed to git (they are several hundred MB). Add them to `.gitignore` if they are not already ignored.
- `DOC_CONFLICTS.md` part C records your decisions (file naming, CLI-only flags, sample data). Nothing else is owed before sprint 1.

## 2. Session 0: orient (no code)

```
claude
> /orient
```

It maps the reporting engine's conventions and reusable pieces and writes `docs/input_pipeline/CODEBASE_MAP.md`. It will confirm where the new package goes (proposed: `src/plexos_input/`, tests in `tests/`) and raise anything that clashes with the design. Read it before you continue.

## 3. Sprint 1

The backlog's goal for sprint 1: "Here is APS's real model as a SQL database, and here are its properties in one flat table."

```
> /story OPS-01      (adds pytest, SDK and Cloud CLI dependency checks, check_environment)
> /story CDM-01
> /story CDM-02
> /story CDM-03      (spike: needs the real model; its answers change CDM-04 and CDM-05)
> /story CDM-04
> /story CDM-05
```

Use a fresh session (`/clear`) for each story. `CLAUDE.md`, the story file and `PROGRESS.md` carry the state. When a story finishes, run `/verify-story <ID>` in a new session before starting one that depends on it.

Sprint order after that is in `docs/input_pipeline/appendix_b_story_index.md` and `PROGRESS.md`. The backlog's reasoning: CDM views first (everything reads through them), the diff second (it proves "nothing changed" on an unmodified model, the cheapest correctness check for the whole pipeline), and the write path late, because it is the only part that changes a model.

## 4. Things Claude Code cannot do for you

- **WRT-07, the second link.** Only PLEXOS Desktop can prove PLEXOS reads the new value. Claude Code will build it and tell you what to open and check.
- **CDM-03 and CDM-07.** These verify assumed database joins and the Read Order attribute path against the real model. If the answers differ from the design, everything downstream shifts. Read the evidence it pastes into the design doc.
- **Decisions.** It is instructed to stop and ask rather than choose.

## 5. Keeping the docs honest

The design doc is the source of truth. If a story shows it is wrong, Claude Code updates `design/Task5_Technical_Design.txt` first, then the story, then runs `python tools/split_docs.py`. Review those doc changes in the diff: they are decisions.
