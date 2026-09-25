<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-01 — Generate a queryable `.db` from a model `.xml`

**As** any component that needs to read a model, **I want** a single function that hands me a `.db` for a given `.xml`, **so that** no component has to care whether one already existed.

**Type:** Story · **Size:** S · **Traces to:** §2.5, §10.1 · **Depends on:** OPS-01

**Spec**

```python
def ensure_db(xml_path: Path, db_path: Path | None = None, *, force: bool = True) -> Path
```

- Default `db_path` is `xml_path.with_suffix(".db")`, written **beside the `.xml`**, never in a temp directory — the run archive keeps it (§12).
- Shells out to `plexos-sdk xml-to-db <xml> <db>` (the SDK's documented conversion, which is backed by the Cloud CLI).
- `force=True` — the default, and what the diff tool uses — regenerates unconditionally, overwriting any existing `.db`. This is deliberate: an existing `.db` may be stale, may not correspond to the current `.xml`, and per §2.5 usually will not exist at all. "Which `.db` is current" must never be a question anyone has to answer.
- `force=False` is for the build script's own working copy only, where it just produced the `.db` itself.
- Non-zero exit from the CLI raises `PlexosConversionError` carrying the CLI's stderr verbatim. Do not summarise the CLI's error; the modeller needs its text.

**Acceptance criteria**

1. **Given** an `.xml` with no `.db` beside it, **when** `ensure_db` is called, **then** a `.db` is created beside it and its path returned.
2. **Given** an `.xml` with a stale `.db` beside it (a `.db` generated from a different model), **when** `ensure_db` is called with the default `force=True`, **then** the `.db` is overwritten and its content reflects the current `.xml`.
3. **Given** the Cloud CLI is not on PATH, **when** `ensure_db` is called, **then** it raises with a message naming the missing executable and pointing at the dependency note — not a bare `FileNotFoundError`.
4. **Given** a malformed `.xml`, **when** `ensure_db` is called, **then** the CLI's own stderr appears unaltered in the raised exception.

**Tests**

- Round-trip against `2026 APS_TA V3.1 - Copy.xml` (952 objects, 84 Data File objects): the generated `.db` contains 952 rows in `t_object`.
- `xml → db → xml` produces a model that re-converts to a byte-identical `.db`. (Not byte-identical XML — the CLI is not guaranteed to preserve formatting.)
