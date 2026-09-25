---
description: Session 0 - map the existing codebase against the design and backlog. Writes docs only, no code changes.
---

Do not write or change any code in this session. The only files you may create or edit are `docs/input_pipeline/CODEBASE_MAP.md`, `docs/input_pipeline/PROGRESS.md` and the Commands section of `CLAUDE.md`.

We are building the PLEXOS input pipeline described in `design/` and `docs/input_pipeline/`, inside this repo. The existing code is the PLEXOS Reporting Automation Engine (solution files to reports); the input pipeline is a new, separate capability that sits beside it, so "what exists" is mostly about conventions and reusable pieces, not finished stories. Before any story is built, I need to know what already exists.

1. Read `CLAUDE.md`, `docs/input_pipeline/00_conventions_and_answers.md`, `docs/input_pipeline/design_sections/01_system_overview.md`, `docs/input_pipeline/DOC_CONFLICTS.md` and `docs/input_pipeline/appendix_b_story_index.md`. Do not read the full design or full backlog.
2. Explore the repo (use the Explore agent for breadth). Establish: language and version, package layout, dependency management, how tests run, entry points, logging and config conventions, coding style, anything Windows-specific, and how `plexos_sdk`, the Cloud CLI, DuckDB, pandas and openpyxl are already used, if at all.
3. Write `docs/input_pipeline/CODEBASE_MAP.md` with:
   - Layout and conventions, in about a page.
   - For each component C1 to C8 in design §1.1: what exists, where, and how close it is to the design.
   - Existing code that conflicts with a non-negotiable rule in `CLAUDE.md` (for example raw SQL writes to a model database, a hardcoded `TimeSeries` or model name, overwriting existing CSVs). Quote file and line.
   - Anything reusable that the backlog would otherwise rebuild.
4. In `docs/input_pipeline/PROGRESS.md`, fill the `Existing code / notes` column for every story that touches existing code, and set its status to `Exists`, `Partial` or leave `Todo`. Use `Exists` only if you have checked the acceptance criteria against the code, not just the file name.
5. Propose the test, lint and environment-check commands to put in the Commands section of `CLAUDE.md`, and fill them in only if the repo makes them unambiguous.
6. Finish with: the three biggest risks you see in fitting the backlog to this codebase, which backlog stories need adapting rather than building from scratch (OPS-01 is the obvious one), and any question you need answered before sprint 1.

Do not start on any story.
