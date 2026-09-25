<!-- Epic intro: docs/input_pipeline/epics/A_cdm_the_model_as_a_query.md -->
### CDM-02 — Read a `.db` through DuckDB, read-only

**As** the diff tool and the CDM consumers, **I want** one connection helper, **so that** nothing in the codebase opens a model database a second, different way.

**Type:** Chore · **Size:** S · **Traces to:** §9.3 · **Depends on:** CDM-01

**Spec**

```python
@contextmanager
def open_model(db_path: Path, alias: str = "m") -> duckdb.DuckDBPyConnection
```

- `duckdb.connect()` in memory, then `ATTACH '<db_path>' AS <alias> (TYPE SQLITE, READ_ONLY)`.
- **Read-only is not optional.** Nothing in the read path may write to a model database; writes go through `plexos_sdk` and nowhere else. This is the same pattern Energy Exemplar's own `QueryWriteMemberships` uses.
- A second overload attaches two databases under `old` / `new` for the diff (DIFF-03).
- Views (CDM-04, CDM-05) are created in the in-memory DuckDB session against the attached alias, **not** persisted into the SQLite file — so the archived `.db` stays exactly what the CLI produced.

**Acceptance criteria**

1. **Given** a valid `.db`, **when** opened, **then** `SELECT count(*) FROM m.t_object` returns the object count.
2. **Given** an open connection, **when** any `INSERT`/`UPDATE`/`DELETE` is attempted against the attached alias, **then** DuckDB raises rather than writing.
3. **Given** two databases attached as `old` and `new`, **when** a query names `old.t_object` and `new.t_object` in one statement, **then** it executes.
4. **Given** the context manager exits by exception, **then** the connection is closed and the SQLite file is not left locked.
