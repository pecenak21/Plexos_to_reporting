<!-- Epic intro: docs/input_pipeline/epics/F_plexos_write_path.md -->
### WRT-07 — The second link: add ours, leave theirs

**As** APS, **I want** existing links left exactly as they are, **so that** the build adds data without removing anything they rely on. **[LATE]**

**Type:** Story · **Size:** L · **Traces to:** deliverable §"Writing CSVs as datafiles" · **Depends on:** WRT-04, WRT-05, WRT-06

**Spec**

The build adds its **own link** from the target attribute to the data file it writes, tagged with its scenario, and **leaves any existing link in place**. The new link **mirrors the existing one in every other respect** — bands, date ranges, time slices and any variables attached to it — so the two records differ only in the data file they read and the scenario that tags them.

The two records coexist because the SDK's duplicate-detection rule treats records differing by scenario tag, Datafile tag or date range as **distinct**: two property records are the same only if membership, property, `band_id`, value, texts and tags all match. Different scenario tag → different record. That is what makes the second link possible at all.

Read Order (WRT-06) is what decides which of the two PLEXOS actually uses.

**What "mirrors" means concretely**, and each of these must be read off the existing record rather than defaulted:

| Attribute of the existing link | Mirrored on the new link |
|---|---|
| `band_id` | Yes |
| `date_from` / `date_to` | Yes |
| Time slice tags | Yes |
| Variable tags | Yes — WRT-08 |
| Data file | **No** — ours |
| Scenario tag | **No** — ours |

**Acceptance criteria**

1. **Given** a property with one existing link and no scenario, **then** after the build both records exist in `v_property`, distinguished by scenario and data file.
2. **Given** an existing link with `date_from` set, **then** the new link carries the same `date_from`.
3. **Given** an existing multi-band property, **then** a new link is created at the row's band (band 1 in v1, since the Data sheet carries no band column — §6.3) and mirrors the existing record at that band. Multi-band source files are out of scope until the sheet gains a band column; a property whose existing records span several bands raises a ledger entry naming the bands left untouched.
4. **Given** a property with **no** existing link, **then** one new link is created with defaults and a ledger entry notes there was nothing to mirror.
5. **Given** a built model opened in PLEXOS, **then** the value PLEXOS reports for that property is the one from our CSV. **This is the one stated exception to the Definition of Done's "covered by an automated test"** — nothing outside Desktop can prove what Desktop reads. Check it by hand, record the screenshot in the story, and treat the automated tests as necessary but not sufficient until it is done.
