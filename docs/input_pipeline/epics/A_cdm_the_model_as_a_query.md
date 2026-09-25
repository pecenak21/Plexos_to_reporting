## EPIC A — CDM: the model as a queryable database

**Component C6.** Phase 1. The decision this epic rests on: there is no separate canonical database. PLEXOS's own model, converted to SQLite, *is* the canonical data model — normalized, queryable, and incapable of drifting out of step with the model because it is the model. What this epic builds is not an ETL pipeline; it is the `.db` generation step plus a small set of pre-joined views that make the normalized tables readable.
