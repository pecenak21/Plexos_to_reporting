<!-- Epic intro: docs/input_pipeline/epics/G_semantic_validation_chec.md -->
### VAL-02 — Every named object exists in the model

**As** the build, **I want** every object named — by a column header or by `target_object` — checked against the model, **so that** a typo in a header does not become a silently skipped generator.

**Type:** Story · **Size:** S · **Traces to:** §8.2 · **Depends on:** VAL-01, FMT-02

**Spec**

Collect the object list per row (wide → non-time column headers; single-object → `target_object`), and check each against the model's objects **of that class**. An object that exists under a different class is a **different failure and gets a different message** — "`Metro to APS` exists as a `Line`, not a `Generator`" is immediately actionable; "not found" is not.

Matching is exact in case and in interior spacing. No fuzzy matching and no normalisation **at this layer** — the reader has already stripped outer whitespace (FMT-01), and nothing further is trimmed, folded or guessed here. A build that guesses would write data to the wrong object.

Missing objects are an **error**, and every one is listed.

**Acceptance criteria**

1. **Given** a wide file with one misspelled header, **then** an error naming the file, the header and the closest real object names of that class.
2. **Given** a header naming a real object of the wrong class, **then** an error saying which class it actually is.
3. **Given** a header differing only in trailing whitespace, **then** it matches — because FMT-01 stripped it. Assert here so the two stories cannot drift apart.
4. **Given** a wide file with 40 headers of which 3 are wrong, **then** all 3 are named in one message.
