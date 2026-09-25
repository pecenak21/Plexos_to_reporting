<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-08 — Carry conditional variables onto the new link

**As** the build, **I want** any variable on the existing link copied to the new one, **so that** current behaviour is preserved rather than silently lost. **[LATE]**

**Type:** Story · **Size:** M · **Traces to:** deliverable §"Writing CSVs as datafiles" · **Depends on:** WRT-07 · **Q10 answered:** the variables **should** apply to the new data — and must be called out explicitly in the build report. See §2.1.

**Spec**

Where an existing link carries a **conditional variable**, that variable is copied onto the new link.

**Why this is not optional.** Data tagged with a conditional variable **overrides read ordering entirely**. A new link without the variable would lose to the old one regardless of Read Order — the build would complete, report success, and change nothing. This is the single most dangerous silent-failure mode in the write path.

**Known real cases in the current model:**

| Object / property | Variable |
|---|---|
| `Battery` → `Max Power` | `Battery Derate` |
| One `Fuel` → `Price` (`MKTGas`) | `Fuel Adder for MKTGas` |

Each is named individually in the build report.

**Q10 is closed, and both halves of the answer matter.**

*"It should apply to the new data files, but should be called out explicitly in the build report! It is critical that assumptions like this are called out explicitly. A diff report won't catch these."*

So: **copy the variable** — this story stands as written, no per-row opt-out, no extra column. And the reporting half is not a nice-to-have attached to it; it is the reason the story is safe to implement at all. A carried variable changes what PLEXOS computes and leaves **no trace in any of the four diff levels**: structure unchanged, assignment records matching, CSV values identical. A modeller reading a clean diff would conclude nothing happened.

That is why §2.1 exists, and this is its canonical case. The build report must name the object, the property and the variable, and say in words that the diff will not show it.

**Acceptance criteria**

1. **Given** an existing link carrying `Battery Derate`, **then** the new link carries it too, and a ledger entry names the object, the property and the variable.
2. **Given** an existing link with no variable, **then** the new link has none and nothing is logged.
3. **Given** a built model, **then** the number of links carrying each variable is unchanged plus exactly the number of new links the build created.
4. **Given** any variable carried, **then** the build report lists it under exceptions and assumptions with Q10's open status stated — the modeller must be able to see that this was a decision, not a certainty.
