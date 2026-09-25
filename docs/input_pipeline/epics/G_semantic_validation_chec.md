## EPIC G — Semantic validation (checkpoint 2)

**Component C5.** Phase 6. Two checkpoints, deliberately separated by *what they can know*. Checkpoint 1 (FMT-03) runs against a file alone and needs no model. Checkpoint 2 needs the resolved `.db` and runs alongside the diff, because both answer the same question: **should I trust this build?**

The rule set below was written for the first time in the technical design rather than carried from an agreed source, and the two-point placement was proposed rather than confirmed. **Q16 closed both: the rule set and the placement are accepted as specified.** One question remains inside the epic — Q9, whether incomplete coverage should warn or stop (VAL-04) — and a default is in place.

Checkpoint 2 **fails the build** on any error (§7.1 step 10), with one boundary worth stating rather than leaving to an acceptance criterion: **findings that already existed in the source model are reported as pre-existing and do not stop the build.** They are a model condition the build met, not input the build was given — the standing rule's own distinction. Only findings this build introduced are errors. VAL-06 is where that line is drawn, and drawing it needs the before-and-after `sdk.validate()` results, which is why both are retained.
