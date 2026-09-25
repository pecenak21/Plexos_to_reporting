<!-- Epic intro: docs/input_pipeline/epics/E_build_orchestration.md -->
### BLD-05 — Post-build path re-check

**As** the build, **I want** every data-file path re-verified against the finished model, **so that** a file written somewhere other than where its link points is caught here and not in Desktop.

**Type:** Story · **Size:** S · **Traces to:** §7.1 step 15 · **Depends on:** BLD-03, CDM-06 · **Wired into the build sequence by:** BLD-04 (sprint 7)

**Spec**

Re-run check 5 of pre-flight, this time against `new_run.xml` and the run's own tree.

**Build it in sprint 4 against the copied model** — at that point the copy exists (BLD-03) even though nothing has been written into it, which is enough to exercise and test the check. Wiring it into the build sequence as step 16 happens with BLD-04 in sprint 7. Cheap, and it catches **the one failure mode that would otherwise produce a model that opens fine and reads nothing**: a Data File whose `t_text` path does not match where the CSV actually landed.

Any failure here is a **build error**, not a warning. The model is wrong.

**Acceptance criteria**

1. **Given** a clean build, **then** every stored path resolves and the count matches the pre-flight count plus any newly added files.
2. **Given** a deliberately corrupted link (path edited to a file that does not exist), **then** the build fails naming that path and the property that points at it.
3. **Given** a newly-created Data File, **then** its stored path resolves — the new-file case is the one most likely to be wrong.
