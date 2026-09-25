---
description: Independent check of a finished story against its acceptance criteria and the standing rules. Best run in a fresh session. Usage - /verify-story CDM-05
argument-hint: <STORY-ID>
---

You are reviewing story **$ARGUMENTS**. You did not write it. Do not fix anything unless I ask; report.

1. Read `docs/input_pipeline/stories/$ARGUMENTS.md`, the standing rules in `CLAUDE.md`, and the design sections the story cites.
2. Find the commit(s) for `$ARGUMENTS` (`git log --grep "$ARGUMENTS"`) and read the diff.
3. For every acceptance criterion, name the test that asserts it and say whether the assertion is real. A test that only checks the function runs, or asserts a hardcoded number that would change if APS versioned the model, does not count.
4. Run the tests. Say whether they ran against a real APS artifact or only a fixture.
5. Search the diff for: hardcoded fixture values, writes to a model `.db`, `<>` used where `IS DISTINCT FROM` is needed, surrogate IDs used for matching, a `.db` trusted without regeneration, summarised SDK or CLI errors, checks that stop at the first finding, decisions that never reach the exception ledger.
6. Report as a table: criterion, test, verdict (`covered`, `weak`, `missing`), then a list of standing-rule concerns, then whether the `PROGRESS.md` status is honest.
