---
description: Build one backlog story, test-first. Usage - /story CDM-05
argument-hint: <STORY-ID>
---

Implement backlog story **$ARGUMENTS**.

## 1. Read, and only this

- `docs/input_pipeline/stories/$ARGUMENTS.md`, and the epic intro it links to.
- `docs/input_pipeline/00_conventions_and_answers.md` (standing rules, Definition of Ready and Done) if you have not read it this session.
- The design sections the story's `Traces to` line cites, from `docs/input_pipeline/design_sections/`.
- The stories it depends on, only to see their interfaces.
- The `$ARGUMENTS` row in `docs/input_pipeline/PROGRESS.md`, and `docs/input_pipeline/CODEBASE_MAP.md` for what already exists.
- Any entry in `docs/input_pipeline/DOC_CONFLICTS.md` that touches this story. Section C entries are decisions I owe you: if one applies, stop and ask.

## 2. Definition of Ready

Check: acceptance criteria are written; every `[CONFIRM]` it depends on is closed; every dependency is `Done` or `Exists` in `docs/input_pipeline/PROGRESS.md`; the real APS artifact it will be tested against is identified and reachable. If any fails, stop and tell me which and what you need. Do not work around it.

## 3. Plan, then wait

Post a short plan: files you will add or change (reusing existing code where `docs/input_pipeline/CODEBASE_MAP.md` says it exists), the tests you will write, and anything in the story you think is wrong or ambiguous. Wait for my go-ahead.

## 4. Build

- Turn each acceptance criterion into a test first, named for the criterion (`test_cdm05_ac2_...`). Run them and watch them fail for the right reason.
- Implement until they pass. Follow the code conventions already in the repo.
- Where the story quotes a figure from the APS fixture model (an object count, a path count), it belongs in the test as the expected result for that fixture only. It must never appear in production code.
- If the story is a Spike: no production code. Answer each question with a query result or a run, paste the evidence into the design doc, remove or convert its `[CONFIRM]` markers, and update the stories it unblocks.

## 5. Self-check against the standing rules

Before you report, answer each in one line: Does anything I wrote hardcode a fixture value? Could the diff show every decision this code makes, and if not, does it reach the exception ledger? Does anything write to a model `.db` other than through `plexos_sdk`? Does anything touch a file or link the build does not own? Do errors from the SDK or CLI pass through verbatim? Do checks collect all findings rather than stop at the first?

## 6. Close out

- Run the full test suite, not only the new tests.
- Run the tests against the real artifact. If you cannot, set the story to `Blocked: needs real artifact` in `docs/input_pipeline/PROGRESS.md` and say exactly what you need. Do not mark it Done.
- If reality disagreed with the design, update the design doc first, then the story, then run `python tools/split_docs.py`.
- Update `docs/input_pipeline/PROGRESS.md`. Commit as `$ARGUMENTS: <summary>`. Do not push.

## 7. Report

Three parts, short: what is done and where; what is not verified and why; anything that belongs in the build report's exception ledger or that I should look at in PLEXOS Desktop.
