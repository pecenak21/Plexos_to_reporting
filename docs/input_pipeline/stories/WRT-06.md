<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-06 — Read Order: one above the maximum on the target model

**As** the build, **I want** its scenario to win against every other scenario on the model, **so that** the data it wrote is the data PLEXOS uses. **[LATE]**

**Type:** Story · **Size:** M · **Traces to:** deliverable §"Writing CSVs as datafiles" · **Depends on:** CDM-07, WRT-05

**Spec**

Where two scenarios define the same data, PLEXOS reads them in `Read Order` and **the last read wins** — a higher Read Order is higher priority. Scenarios default to 0; the highest currently set in APS's model is **2000**.

The build **reads the highest Read Order among the scenarios attached to `target_model` and sets its own to one above it.** No other scenario's Read Order is changed.

**Why max+1 and not a fixed large number.** Two reasons, both learned the hard way:

- A fixed value collides. `999` was proposed and is *below* three existing scenarios at 1000 and one at 2000 — it would have lost silently.
- **Ties are not settled by Read Order.** Where two scenarios share a value at the same Read Order, PLEXOS falls back to the order they appear in the interface — by category, then alphabetically within category — so the winner would depend on the scenario's *name*. Taking one above the maximum avoids the tie entirely.

The earlier idea of resetting other scenarios' Read Order down to make room is **rejected**: it edits APS's model to solve our problem, and it can create new ties among the scenarios it moves.

Where the chosen value is not the expected one, the build records it and why (BLD-08).

**One thing to fix in the deliverable, not in the code.** It says the build sets the value "one above it — normally 9999", and also that the highest Read Order currently in the model is 2000. Max+1 of 2000 is 2001; 9999 would only arise if a scenario at 9998 existed. The rule is right and the illustrative number is wrong — WBK-04 carries it.

**Acceptance criteria**

1. **Given** a target model whose highest attached Read Order is 2000, **then** the build's scenario is set to 2001.
2. **Given** a target model with no scenarios attached, **then** the build's scenario is set to 1.
3. **Given** any run, **then** no other scenario's Read Order is modified — assert by diffing scenario attributes before and after.
4. **Given** a second build against the model the first produced, **then** the Read Order is recomputed and does not creep upward without cause (the build's own scenario is excluded from the maximum).
5. **Given** the value chosen, **then** a ledger entry records it and the maximum it was derived from.
