<!-- Epic intro: docs/input_pipeline/epics/B_comparison_engine.md -->
### DIFF-07 — Standalone entry point

**As** a modeller, **I want** to compare any two models without running a build, **so that** "how does the model I have open differ from the last archived run?" is one action.

**Type:** Story · **Size:** S · **Traces to:** §6.6, §10 · **Depends on:** DIFF-01, WBK-03

**Spec**

Precedence, highest first:

1. Two paths given as command-line arguments.
2. The Compare sheet's `model_1_path` / `model_2_path` (WBK-03).
3. Neither — list the run folders found under `output_root` and ask which two.

`model_1` is **always** the baseline, the "before" side. Reversing the two reverses the report: additions become removals. State this on the sheet and in the report header so nobody reads a reversed report as a real change.

**Where the report goes.** Not into either side. A build writes its report into the run it just created, which it owns; a standalone comparison owns neither side, and writing into one would be editing an archived record after the fact. Default is `<output_root>\Comparisons\`, named for both sides and the date.

**Acceptance criteria**

1. **Given** two paths as arguments, **then** those win over whatever the sheet says.
2. **Given** a filled-in Compare sheet and no arguments, **then** the sheet's paths are used.
3. **Given** neither, **then** the run folders are listed and the user picks two.
4. **Given** a run and its baseline compared in both orders, **then** the two reports are mirror images — every `added` in one is `removed` in the other.
5. **Given** any standalone comparison, **then** nothing is written inside either compared folder.
