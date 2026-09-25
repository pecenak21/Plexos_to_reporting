## 13. Environment and dependencies

| Dependency | Purpose | Notes |
|---|---|---|
| `plexos_sdk` | All model reads/writes, XML↔DB conversion | `pip install plexos_sdk-*.whl`. Plain local package, no cloud container. `[CONFIRMED]` |
| PLEXOS Cloud CLI | DB↔XML conversion backend; required by EE scripts | A local executable, not a cloud service call. `[ANSWERED]` — installed on every machine that will run this pipeline, with a licence for every user. The one hard external dependency is secured. |
| `duckdb` | CDM views, diff engine | Same pattern EE's own scripts use |
| `pandas` | Preprocessors, report assembly | |
| `openpyxl` | Sources workbook, Excel report | |
| `eecloud` | Required by EE automation scripts | |

**Target platform:** PLEXOS Desktop, running locally against archived `.xml`/`.db` files. `[CONFIRMED]` The Cloud-only pieces — DataHub, Cloud Studies and changesets, Pre/Post task-definition chains — do not apply, and `CreateChangeSet` is not part of this design.

**Note on Desktop's Change Database feature:** PLEXOS Desktop's `Create Change Database` / `Import Change Database` has no programmatic equivalent, which is why §10 builds the structural diff rather than wrapping it.

- No such method exists in `plexos_sdk` — checked against the complete documented method list. `[CONFIRMED]`
- Nothing matching appears in the Cloud SDK's documented command surface either; the `changeset` methods there are PLEXOS Cloud Studies' commit history, a different concept. `[CONFIRMED]`
- The Cloud **CLI's own** reference documentation has not been read — only the Python SDK wrapper's. **Settled by decision (2026-09-21): if it is not in the SDK, treat it as not existing.** Even a CLI-only subcommand would have covered one of §10's four comparison levels, not removed the other three, so this is not worth further investigation.
