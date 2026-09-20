"""
exceptions_report.py
Collects data-quality exceptions raised while building the reports and writes them
to Exceptions_Report.log alongside the generated reports.

The pipeline is deliberately forgiving at runtime -- an unmapped generator keeps its
Plexos name, a missing unit rule falls back to a factor of 1.0, a blueprint row that
matches nothing just contributes no rows. Each of those is silent in the output, so
the report exists to make them visible without failing the run.
"""
import os
from collections import defaultdict
from datetime import datetime

import duckdb
import pandas as pd

ERROR = "ERROR"
WARN = "WARN"
INFO = "INFO"

_SEVERITY_ORDER = {ERROR: 0, WARN: 1, INFO: 2}

_entries = []


def reset():
    _entries.clear()


def record(severity, category, message, details=None):
    """Record one exception. `details` is an optional list of per-item strings.

    The same fault is often hit from several call sites (one unit rule is looked up
    once per block), so repeats collapse into a single entry with a count.
    """
    for entry in _entries:
        if entry['severity'] == severity and entry['category'] == category and entry['message'] == message:
            entry['occurrences'] += 1
            return
    _entries.append({
        "severity": severity,
        "category": category,
        "message": message,
        "details": sorted(set(details)) if details else [],
        "occurrences": 1,
    })


def _distinct_objects():
    """Every object name in the solution, with the class(es) it belongs to."""
    query = """
        SELECT ChildClassName AS class_name, ChildObjectName AS object_name FROM mem_fki
        WHERE ChildObjectName IS NOT NULL AND TRIM(ChildObjectName) <> ''
        UNION
        SELECT ParentClassName AS class_name, ParentObjectName AS object_name FROM mem_fki
        WHERE ParentObjectName IS NOT NULL AND TRIM(ParentObjectName) <> ''
    """
    df = duckdb.query(query).df()
    by_name = defaultdict(set)
    by_class = defaultdict(set)
    for class_name, object_name in zip(df['class_name'], df['object_name']):
        name = str(object_name).strip()
        cls = str(class_name).strip()
        by_name[name].add(cls)
        by_class[cls].add(name)
    return by_name, by_class


def validate_name_map(asset_mapping, coverage_threshold=0.5):
    """Both directions of the Plexos <-> RTSim name map.

    Unmapped names are only reported for the classes the map actually covers. The map
    is generator/battery oriented, so auditing every class would bury the real gaps --
    and a class can't be judged 'covered' by a single hit either, since names collide
    across classes ('External' is both a Generator and a Fuel). A class is audited only
    once `coverage_threshold` of its objects are mapped.
    """
    by_name, by_class = _distinct_objects()

    mapped_plexos = {}
    for plexos_name, rtsim_name in asset_mapping.items():
        if pd.isna(plexos_name) or str(plexos_name).strip() == '':
            continue
        mapped_plexos[str(plexos_name).strip()] = str(rtsim_name).strip() if pd.notna(rtsim_name) else ''

    # Map entries that match no object in the solution at all
    orphans = sorted(name for name in mapped_plexos if name not in by_name)
    if orphans:
        record(
            WARN, "NAME_MAP",
            f"{len(orphans)} name-map entr(ies) match no object in the Plexos solution "
            f"(mapping is unused -- check for typos or retired units)",
            [f"{name}  ->  {mapped_plexos[name]}" for name in orphans],
        )

    covered_classes = []
    for cls, names in by_class.items():
        if not names:
            continue
        if len(names & set(mapped_plexos)) / len(names) >= coverage_threshold:
            covered_classes.append(cls)

    if not covered_classes:
        record(ERROR, "NAME_MAP", "No Plexos class is meaningfully covered by the name map -- the "
                                  "mapping sheet and this solution appear unrelated.")
        return

    unmapped = []
    for cls in sorted(covered_classes):
        for name in sorted(by_class.get(cls, set())):
            if name not in mapped_plexos:
                unmapped.append(f"{name}  [{cls}]")
    if unmapped:
        record(
            WARN, "NAME_MAP",
            f"{len(unmapped)} Plexos object(s) in mapped class(es) {sorted(covered_classes)} "
            f"have no name-map entry -- they keep their Plexos name in the reports",
            unmapped,
        )

    # Several Plexos names collapsing onto one RTSim name are summed together silently
    collisions = defaultdict(list)
    for plexos_name, rtsim_name in mapped_plexos.items():
        if rtsim_name and plexos_name in by_name:
            collisions[rtsim_name].append(plexos_name)
    merged = {k: sorted(v) for k, v in collisions.items() if len(v) > 1}
    if merged:
        record(
            INFO, "NAME_MAP",
            f"{len(merged)} RTSim name(s) receive more than one Plexos object -- their values "
            f"are summed together",
            [f"{rtsim} <- {', '.join(plexos)}" for rtsim, plexos in sorted(merged.items())],
        )


def _rate_text(value):
    """Conversion rates read back as floats; print them without trailing zeros."""
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def validate_unit_table(df_units):
    """Unit sheet sanity: Excel-coerced labels, unusable rates, contradictory duplicates.

    Details name the sheet row so the offending cell can be found directly -- a label
    Excel turned into a number prints as '0', which says nothing about where it lives.
    """
    # Row 1 of the sheet is the header, so DataFrame index 0 is sheet row 2.
    def sheet_row(idx):
        return idx + 2

    # Right-aligning the row numbers keeps the detail lines in sheet order once record()
    # sorts them, and lines the values up under each other in the log.
    width = len(str(sheet_row(len(df_units) - 1))) if len(df_units) else 1

    coerced = []
    for row in df_units.itertuples():
        rule = f'"{row.UnitFrom}" -> "{row.UnitTo}", rate {_rate_text(row.ConversionRate)}'
        for col, value in (('UnitFrom', row.UnitFrom), ('UnitTo', row.UnitTo)):
            text = str(value).strip()
            # '$000' typed into Excel becomes the number 0, which then never matches a
            # real unitValue -- the conversion silently no-ops and values stay 1000x off.
            if text and text.replace('.', '', 1).replace('-', '', 1).isdigit():
                coerced.append(f"row {sheet_row(row.Index):>{width}}, {col:<8} = {text:<6} (rule reads {rule})")
    if coerced:
        record(ERROR, "UNIT_CONVERSION",
               f"{len(coerced)} unit label(s) on the UnitConversion sheet are numbers rather than text. "
               f"A rule with a numeric label can never match a unit, so any value it was meant to scale "
               f"is written out unconverted. Excel stores a label like $000 as the number 0 -- format "
               f"the cell as Text, then retype the label.",
               coerced)

    bad_rate = df_units[df_units['ConversionRate'].isna() | (df_units['ConversionRate'] == 0)]
    if not bad_rate.empty:
        record(ERROR, "UNIT_CONVERSION",
               f"{len(bad_rate)} conversion rule(s) have a blank or zero rate -- applying one "
               f"blanks out the affected section",
               [f'row {sheet_row(r.Index):>{width}}, "{r.UnitFrom}" -> "{r.UnitTo}" = {r.ConversionRate}'
                for r in bad_rate.itertuples()])

    pairs = df_units.assign(
        _from=df_units['UnitFrom'].str.lower().str.strip(),
        _to=df_units['UnitTo'].str.lower().str.strip(),
    )
    dupes = pairs[pairs.duplicated(subset=['_from', '_to'], keep=False)]
    conflicting = []
    for key, grp in dupes.groupby(['_from', '_to']):
        if grp['ConversionRate'].nunique() > 1:
            rows = ", ".join(str(sheet_row(i)) for i in sorted(grp.index))
            rates = sorted(set(grp['ConversionRate']))
            conflicting.append(f'"{key[0]}" -> "{key[1]}": rates {rates} on rows {rows}')
    if conflicting:
        record(WARN, "UNIT_CONVERSION",
               f"{len(conflicting)} unit pair(s) defined more than once with different rates "
               f"(the first match wins)",
               conflicting)


def validate_blueprint(blueprint, asset_groups):
    """Blueprint rows that duplicate each other, or that reference things the solution lacks."""
    seen = defaultdict(int)
    for row in blueprint:
        seen[tuple('' if pd.isna(v) else str(v).strip() for v in row)] += 1
    dupes = [f"{k[0]} | {k[1]} | {k[2]} | {k[3]}  (x{n})" for k, n in seen.items() if n > 1]
    if dupes:
        record(WARN, "BLUEPRINT",
               f"{len(dupes)} blueprint row(s) are duplicated -- each produces an identical repeated "
               f"row in the report",
               sorted(dupes))

    known = duckdb.query("""
        SELECT DISTINCT LOWER(TRIM(ChildClassName)) AS child_cls, LOWER(TRIM(ParentClassName)) AS parent_cls,
               LOWER(TRIM(PropertyName)) AS prop
        FROM mem_fki
    """).df()
    known_classes = set(known['child_cls'].dropna()) | set(known['parent_cls'].dropna())
    known_props = set(known['prop'].dropna())
    child_props = defaultdict(set)
    parent_props = defaultdict(set)
    for child_cls, parent_cls, prop in zip(known['child_cls'], known['parent_cls'], known['prop']):
        child_props[child_cls].add(prop)
        parent_props[parent_cls].add(prop)

    missing_class, missing_prop = [], []
    for header, class_input, _group, prop_input, *_ in blueprint:
        raw_cls = str(class_input).strip().lower()
        prop = str(prop_input).strip().lower()
        # Nested entries are written 'Parent.Child'; their properties belong to the
        # membership under the parent object, not to the parent class itself.
        nested = '.' in raw_cls
        cls = raw_cls.split('.')[0]
        props_for_cls = parent_props.get(cls, set()) if nested else child_props.get(cls, set())

        if cls and cls != 'nan' and cls not in known_classes:
            missing_class.append(f"{header}: class '{class_input}'")
        elif prop and prop != 'nan' and prop not in known_props:
            missing_prop.append(f"{header}: property '{prop_input}'")
        elif props_for_cls and prop and prop != 'nan' and prop not in props_for_cls:
            missing_prop.append(f"{header}: property '{prop_input}' is not reported for class '{class_input}'")

    missing_class = sorted(set(missing_class))
    missing_prop = sorted(set(missing_prop))
    if missing_class:
        record(ERROR, "BLUEPRINT",
               f"{len(missing_class)} blueprint row(s) reference a class this solution does not contain",
               missing_class)
    if missing_prop:
        record(ERROR, "BLUEPRINT",
               f"{len(missing_prop)} blueprint row(s) reference a property this solution does not contain",
               missing_prop)

    categories = duckdb.query("""
        SELECT DISTINCT LOWER(TRIM(ChildObjectCategoryName)) AS cat FROM mem_fki
        WHERE ChildObjectCategoryName IS NOT NULL
    """).df()
    known_cats = set(categories['cat'].dropna())

    empty_groups = []
    for (cls, group), assets in asset_groups.items():
        unknown = [a for a in assets
                   if a and a.strip().lower() not in ('all', 'nan') and a.strip().lower() not in known_cats]
        if unknown:
            empty_groups.append(f"{cls} / {group}: {', '.join(unknown)}")
    if empty_groups:
        record(WARN, "GROUPS",
               f"{len(empty_groups)} asset group(s) list categories that match no Plexos object "
               f"-- those filters silently exclude everything",
               sorted(empty_groups))


def validate_contract_map(contract_rows):
    """Section 23 contract table: fuels it misses, entries that match nothing, unusable factors."""
    if not contract_rows:
        return
    fuels = set(duckdb.query(
        "SELECT DISTINCT TRIM(ChildObjectName) AS n FROM mem_fki WHERE LOWER(ChildClassName) = 'fuel'"
    ).df()['n'])
    listed = {plexos for plexos, _, _ in contract_rows}

    not_listed = sorted(fuels - listed)
    if not_listed:
        record(WARN, "CONTRACT_MAP",
               f"{len(not_listed)} Plexos fuel(s) are not listed in Contract_name_map -- left out of section 23",
               not_listed)

    stale = sorted(listed - fuels)
    if stale:
        record(WARN, "CONTRACT_MAP",
               f"{len(stale)} Contract_name_map entr(ies) match no Plexos fuel -- their section 23 rows are all zero",
               stale)

    unmapped = sorted(plexos for plexos, label, _ in contract_rows if not label.strip() and plexos in fuels)
    if unmapped:
        record(INFO, "CONTRACT_MAP",
               f"{len(unmapped)} Plexos fuel(s) are listed without an RTSim contract -- omitted from section 23",
               unmapped)

    bad_factor = sorted(f"{plexos} -> {label.strip()} (factor {factor})"
                        for plexos, label, factor in contract_rows
                        if label.strip() and (pd.isna(factor) or factor == 0))
    if bad_factor:
        record(ERROR, "CONTRACT_MAP",
               f"{len(bad_factor)} mapped contract(s) have a blank or zero ConversionFactor -- those rows report nothing",
               bad_factor)


def record_unit_miss(property_name, db_unit, target_unit):
    record(WARN, "UNIT_CONVERSION",
           f"No conversion rule for '{db_unit}' -> '{target_unit}' (property '{property_name}'); "
           f"values were left unconverted")


def record_nan_scale(property_name, db_unit, target_unit):
    record(ERROR, "UNIT_CONVERSION",
           f"Conversion rule '{db_unit}' -> '{target_unit}' (property '{property_name}') resolved to NaN; "
           f"every value in that block becomes blank")


def record_no_data(header, property_name, class_name):
    record(WARN, "NO_DATA",
           f"Section '{header}': no data returned for property '{property_name}' (class '{class_name}') "
           f"-- the section is missing these rows")


def write(output_dir, report_name="Exceptions_Report.log"):
    """Write the collected exceptions and echo a summary to the console."""
    path = os.path.join(output_dir, report_name)
    counts = defaultdict(int)
    for entry in _entries:
        counts[entry['severity']] += 1

    ordered = sorted(_entries, key=lambda e: (e['category'], _SEVERITY_ORDER.get(e['severity'], 9)))

    with open(path, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write(" Report Generation Exceptions\n")
        f.write(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("==================================================\n\n")

        if not ordered:
            f.write("No exceptions recorded.\n")
        else:
            f.write(f"Summary: {counts[ERROR]} error(s), {counts[WARN]} warning(s), {counts[INFO]} note(s)\n\n")
            current_category = None
            for entry in ordered:
                if entry['category'] != current_category:
                    current_category = entry['category']
                    f.write(f"\n----- {current_category} -----\n")
                repeat = f"  (hit {entry['occurrences']}x)" if entry['occurrences'] > 1 else ""
                f.write(f"\n[{entry['severity']}] {entry['message']}{repeat}\n")
                for detail in entry['details']:
                    f.write(f"       {detail}\n")
        f.write("\n")

    print(f"[+] Exceptions report written to: {path}")
    if ordered:
        print(f"    {counts[ERROR]} error(s), {counts[WARN]} warning(s), {counts[INFO]} note(s)")
        for entry in ordered:
            if entry['severity'] == ERROR:
                print(f"    [ERROR] {entry['message']}")
    else:
        print("    No exceptions recorded.")

    return path
