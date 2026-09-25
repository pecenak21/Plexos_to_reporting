# Task 5 — Technical Design: Plexos Input Pipeline

*(SOW Task 2 as originally numbered; the tasks were reordered and this is now Task 5. Filenames still say Task2 and have been left alone to avoid breaking links.)*

**Status:** build specification, for implementation. **Current as of 2026-09-21** — every open question that needed APS has been answered and folded in; see §15.

Companion documents: `claude/Task2_D3_Problem_Definition.md` holds the reasoning, the evidence behind each confirmed fact, and the decision history — this document is the *what to build*, the problem definition is the *why it's built this way*. `claude/Task5_Build_Backlog.txt` carries the same decisions forward as 67 stories with acceptance criteria.

**Scope:** the input side — APS source data through to a Plexos-ready model, plus the run-diff and validation tooling around it. Output extraction and reporting are separate work and are not covered here.

**Confidence markers used throughout:**
`[CONFIRMED]` — verified against APS's real files, a real populated Plexos model, or Energy Exemplar's actual shipped code.
`[PROPOSED]` — a design decision made here, internally consistent but not yet validated against APS practice.
`[CONFIRM]` — still needs an answer before the affected code is finalized. **Every remaining one is ours to close by testing against the model or the SDK; none is waiting on APS.**
`[ANSWERED]` — was a `[CONFIRM]`, and APS answered it on 2026-09-20 / 21. The answer is stated at the point of use and summarized in §15.
