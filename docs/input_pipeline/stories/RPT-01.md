<!-- Epic intro: docs/input_pipeline/epics/H_reporting_the_build_repo.md -->
### RPT-01 — Build report (flat)

**As** an APS modeller, **I want** a short plain-text file saying what the build decided, **so that** the assumptions behind a clean run are in front of me — in a file my machine opens without being asked what to open it with.

**Type:** Story · **Size:** M · **Traces to:** §11 (superseded by Q11); deliverable §"The build report" · **Depends on:** BLD-08, VAL-01 … VAL-06 · **Q11 answered:** flat.

**Spec**

One file, `Inputs\build_report.txt`, written on **every** build — successful, failed, or stopped at a checkpoint.

**Plain text, not Markdown.** A `.md` file is something an APS modeller has no reason to recognise: it opens in the wrong application or in none, and its syntax gets in the way of the content rather than formatting it. A `.txt` opens in Notepad on every machine at APS, pastes into an email intact, and prints. That is the whole requirement.

Formatting conventions, so it reads as a document rather than a log dump:

- Section headings in `UPPER CASE` on their own line, with a rule of dashes beneath.
- Wrap body text at 100 columns. Nothing relies on a window being wide.
- Entries as indented `-` bullets, continuation lines aligned under the text.
- Key/value pairs in the header aligned on a fixed column so they scan vertically.
- No pipe tables, no backticks, no asterisks, no `#`. If something needs a table, it is a detail page in the diff workbook, not a paragraph in this file.

Sections, in this order:

1. **Run header.** Run name; source model path; `target_model`; scenario name and the Read Order it was given, with the maximum it was derived from; baseline run (or *"none — first run"*); start time and duration; every CLI override with the sheet value beside the value actually used (WBK-06).
2. **Outcome.** One line: completed, or stopped at which step and why.
3. **Exceptions and assumptions.** The ledger from BLD-08, one bullet each: what the build met, what it did, why, and where. **This is the point of the file.**
4. **Validation findings.** Every checkpoint-1 and checkpoint-2 finding, errors first, each with its location.
5. **Counts.** Rows written, objects touched, Data File objects created, orphan CSVs, files archived.
6. **Standing notes.** Two, printed every time rather than left as tribal knowledge: renamed objects appear in the diff as one removal plus one addition, and the archived workbook's Compare sheet is scratch space that says nothing about this run (WBK-03).

**The §2.1 test applies to every line of section 3:** *would the diff show this?* If no, it belongs here, spelled out in words, with the object and property named. Variables carried across (WRT-08) are the canonical case — they change what PLEXOS computes and leave no trace in any of the four diff levels.

**Acceptance criteria**

1. **Given** a completed build, **then** `build_report.txt` exists in the run folder with all six sections present.
2. **Given** a build that stopped at checkpoint 1, **then** the file still exists, the outcome line names the step, and sections 3 and 4 hold everything gathered up to that point.
3. **Given** a build that carried a conditional variable, **then** section 3 names the object, the property, the variable, and says in words that the diff will not show it.
4. **Given** a build with an empty ledger, **then** section 3 reads *"No exceptions or assumptions recorded"* rather than being omitted. An absent section and an empty one must not look the same.
5. **Given** a first run with no baseline, **then** the header says so, and no count reads `0` where the right answer is *"not measured"*.
6. **Given** the file opened in Notepad at a default window size, **then** every line fits without horizontal scrolling and no formatting character appears that is not doing visible work.
7. **Given** the file, **then** it contains no Markdown syntax at all — assert it, because the temptation to reach for a pipe table when a section gets long is exactly how this drifts back.
