## EPIC B — Comparison engine

**Component C7.** Phase 2. "What changed?" is four questions, and no single tool answers all of them. Energy Exemplar's tooling covers one level — the numbers inside the CSVs — and the other three are ours.

Desktop's `Create Change Database` looks like the right tool and has no equivalent in `plexos_sdk` (checked against the complete documented method list) or in the Cloud SDK's documented command surface. **Q17 closes the question by decision: if it is not in the SDK, treat it as not existing.** Even a CLI-only subcommand would have covered one of the four levels, not removed the other three, so this epic is built either way.

The engine is one function with no opinion about how it was reached. Both entry points are thin wrappers.
