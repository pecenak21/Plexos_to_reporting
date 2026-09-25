<!-- Epic intro: docs/input_pipeline/epics/J_packaging_operations_and.md -->
### OPS-01 — Repo, dependencies and environment check

**As** the build team and later APS, **I want** a repo that says what it needs and checks it, **so that** "it doesn't work on my machine" has an answer.

**Type:** Chore · **Size:** M · **Traces to:** §13 · **Depends on:** — · **Q1 answered:** the Cloud CLI is installed on every machine that will run this, and every user is licensed. The dependency is secured; the check below stays as a guard, not as an open risk.

**Spec**

| Dependency | Purpose | Note |
|---|---|---|
| `plexos_sdk` | All model reads/writes, XML↔DB conversion | `pip install plexos_sdk-*.whl` — plain local package, no cloud container |
| **PLEXOS Cloud CLI** | DB↔XML conversion backend; required by EE scripts | A **local executable**, not a cloud service call. **The one hard external dependency.** |
| `duckdb` | CDM views, diff engine | Same pattern EE's own scripts use |
| `pandas` | Preprocessors, report assembly | |
| `openpyxl` | Sources workbook, Excel report | |
| `eecloud` | Required by EE automation scripts | |

Target platform: **PLEXOS Desktop, running locally against archived `.xml` / `.db` files.** The Cloud-only pieces — DataHub, Cloud Studies and changesets, Pre/Post task-definition chains — do not apply, and `CreateChangeSet` is not part of this design.

Deliver a `check_environment` command that verifies each dependency, prints the Cloud CLI's version, and exits non-zero with a specific message on any failure. Run it as the first thing in CI and name it in the runbook as the first thing to run on a new machine.

**Acceptance criteria**

1. **Given** a machine with everything installed, **then** `check_environment` exits 0 and prints each version.
2. **Given** a machine without the Cloud CLI, **then** it exits non-zero naming the CLI and where it is expected.
3. **Given** a pinned dependency set, **then** a fresh install reproduces it exactly — versions pinned, not ranged.
4. **Given** CI, **then** the check runs before any test.
