<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-07 — Model introspection: scenarios, Read Order, and model attachment

**As** the write path, **I want** to know which scenarios are attached to a given PLEXOS model and what Read Order each carries, **so that** the build's own scenario can be given a Read Order that wins. **[LATE]**

**Type:** Story · **Size:** M · **Traces to:** deliverable §"Writing CSVs as datafiles"; §6.3 · **Depends on:** CDM-05 · **Q5 answered:** `target_model` is per-run and nothing is standard, so resolve it from the Run sheet every time and cache no default.

**Spec**

```python
def scenarios_on_model(db, model_name: str) -> list[Scenario]   # name, read_order, category
def max_read_order(db, model_name: str) -> int
```

- A Scenario's `Read Order` is an **attribute**, read via `t_attribute` / `t_attribute_data`, not a property. Default is 0 when unset. **`[CONFIRM]` — this schema path is inferred, not traced.** `t_attribute` / `t_attribute_data` are not in §2.2's record-by-record traced table list, and this story is the sole foundation of WRT-05 and WRT-06. Verify it against the populated model the same way CDM-03 verifies the view joins, and do it before WRT-05 starts, not alongside it.
- "Attached to a model" is a membership between the Model object and the Scenario object — only scenarios attached to the target model participate in that model's read ordering, which is why the maximum is taken per-model and not model-wide.
- Known real values, read directly off `2026 APS_TA V3.1 - Copy.xml` during design (not from either document — re-verify with a query before coding against them): three scenarios at Read Order 1000 and one at 2000. Any implementation that assumes small integers or a dense range is wrong.

**Acceptance criteria**

1. **Given** the populated APS model and a named model object, **then** the scenarios attached to it are returned with their Read Orders, including scenarios with no Read Order set, reported as 0.
2. **Given** that model, **then** `max_read_order` returns 2000.
3. **Given** a model with no scenarios attached, **then** `max_read_order` returns 0 and does not raise.
4. **Given** a model name that does not exist, **then** it raises naming the model and listing the model names that do exist — a typo in `target_model` must not be reported as "no scenarios".
