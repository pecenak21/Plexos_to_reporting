<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-07 — Orphan data-file count

**As** a modeller, **I want** to know how many CSVs in the tree nothing points at, **so that** a file someone forgot to wire up surfaces.

**Type:** Story · **Size:** S · **Traces to:** §6.1.1 · **Depends on:** BLD-03, CDM-06

**Spec**

Set difference between files present under the tree and paths referenced by `v_property`. Reported as a count in the build report's counts section, with the full list beneath it. **Informational, never an error** — carrying orphans forward is harmless.

**Acceptance criteria**

1. **Given** APS's real tree, **then** 21 orphans are reported (121 present, 100 referenced).
2. **Given** a build that adds a CSV and wires it up, **then** the orphan count is unchanged.
3. **Given** a build that writes a CSV whose link then fails to be created, **then** the orphan count rises — and this is the signal BLD-05 is meant to catch first.
