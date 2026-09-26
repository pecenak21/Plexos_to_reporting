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


def validate_name_maps(name_map, coverage_threshold=0.5):
    """The maptable sheets on their own and against the solution's object names.

    Maptables are class-blind: a listed name renames every object and every report cell
    spelled that way. Unmapped names are only audited for the classes the maptables
    actually cover. The maps are generator/battery oriented, so auditing every class
    would bury the real gaps -- and a class can't be judged 'covered' by a single hit
    either, since names collide across classes ('External' is both a Generator and a
    Fuel). A class is audited only once `coverage_threshold` of its objects are mapped.
    """
    for sheet in name_map.legacy_sheets:
        record(ERROR, "NAME_MAP",
               f"Sheet '{sheet}' is no longer read. Mapping sheets must be named 'maptable...' "
               f"(e.g. maptable_Generators); rename it or its names print as PLEXOS has them")
    if not name_map.sheets:
        record(WARN, "NAME_MAP", "No 'maptable' sheets found -- every name prints as PLEXOS has it")
        return

    lookup = name_map.lookup
    by_name, by_class = _distinct_objects()

    # The same name listed twice: the later listing silently wins
    duplicates = []
    for source, listings in sorted(name_map.duplicates().items()):
        used = listings[-1]
        others = "; ".join(f"{e.sheet} row {e.row} -> '{e.target}'" for e in listings[:-1])
        duplicates.append(f"'{source}': used {used.sheet} row {used.row} -> '{used.target}'  (ignored: {others})")
    if duplicates:
        record(WARN, "NAME_MAP",
               f"{len(duplicates)} name(s) are listed more than once in the maptables -- the last "
               f"listing (sheets in workbook order, rows top to bottom) is the one used",
               duplicates)

    collisions = [f"'{name}' [{', '.join(sorted(by_name[name]))}] -> '{target}'"
                  for name, target in sorted(lookup.items()) if len(by_name.get(name, ())) > 1]
    if collisions:
        record(WARN, "NAME_MAP",
               f"{len(collisions)} mapped name(s) belong to more than one Plexos class -- maptables "
               f"ignore class, so every object with that name is renamed the same way",
               collisions)

    # A -> B and B -> C: the report pass renames the already-mapped B a second time
    chains = [f"'{source}' -> '{target}' -> '{lookup[target.strip()]}'"
              for source, target in sorted(lookup.items())
              if target.strip() in lookup and lookup[target.strip()] != target]
    if chains:
        record(WARN, "NAME_MAP",
               f"{len(chains)} mapped name(s) are themselves mapped again -- the report shows the last name in the chain",
               chains)

    empties = [f"{sheet}: '{target}'" for sheet in name_map.sheets for target in name_map.empty[sheet]]
    if empties:
        record(INFO, "NAME_MAP",
               f"{len(empties)} maptable name(s) have no mapping defined (column 2 blank) -- they are not "
               f"printed in the reports",
               empties)

    covered_classes = [cls for cls, names in by_class.items()
                       if names and len(names & set(lookup)) / len(names) >= coverage_threshold]
    unmapped = [f"{name}  [{cls}]" for cls in sorted(covered_classes)
                for name in sorted(by_class.get(cls, set())) if name not in lookup]
    if unmapped:
        record(WARN, "NAME_MAP",
               f"{len(unmapped)} Plexos object(s) in mapped class(es) {sorted(covered_classes)} "
               f"have no maptable entry -- they keep their Plexos name in the reports",
               unmapped)

    # Several Plexos names collapsing onto one report name are summed together silently
    collisions = defaultdict(list)
    for source, target in lookup.items():
        if source in by_name:
            collisions[target].append(source)
    merged = {k: sorted(v) for k, v in collisions.items() if len(v) > 1}
    if merged:
        record(INFO, "NAME_MAP",
               f"{len(merged)} report name(s) receive more than one Plexos object -- their values "
               f"are summed together",
               [f"{target} <- {', '.join(sources)}" for target, sources in sorted(merged.items())])


def validate_name_map_usage(name_map):
    """After the reports are built: maptable entries that renamed nothing."""
    by_name, _ = _distinct_objects()
    unused = [f"{e.sheet} row {e.row}: '{e.source}' -> '{e.target}'"
              for e in name_map.entries
              if e.source and e.source not in name_map.used_sources and e.source not in by_name]
    if unused:
        record(WARN, "NAME_MAP",
               f"{len(unused)} maptable entr(ies) match nothing in the solution or the reports -- check "
               f"for typos, retired units, or a report label that has changed",
               unused)


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


def validate_contract_map(contract_factors, name_map):
    """Section 23: fuels without a factor, factors that match nothing, unusable factors, unlabelled fuels."""
    if not contract_factors:
        return
    fuels = set(duckdb.query(
        "SELECT DISTINCT TRIM(ChildObjectName) AS n FROM mem_fki WHERE LOWER(ChildClassName) = 'fuel'"
    ).df()['n'])
    listed = {plexos for plexos, _ in contract_factors}

    not_listed = sorted(fuels - listed)
    if not_listed:
        record(WARN, "CONTRACT_MAP",
               f"{len(not_listed)} Plexos fuel(s) are not listed in Contract_factors -- left out of section 23",
               not_listed)

    stale = sorted(listed - fuels)
    if stale:
        record(WARN, "CONTRACT_MAP",
               f"{len(stale)} Contract_factors entr(ies) match no Plexos fuel -- their section 23 rows are all zero",
               stale)

    unlabelled = sorted(plexos for plexos in listed if plexos in fuels and plexos not in name_map.lookup)
    if unlabelled:
        record(INFO, "CONTRACT_MAP",
               f"{len(unlabelled)} fuel(s) in Contract_factors have no maptable entry -- they appear in "
               f"section 23 under their Plexos name",
               unlabelled)

    bad_factor = sorted(f"{plexos} (factor {factor})" for plexos, factor in contract_factors
                        if pd.isna(factor) or factor == 0)
    if bad_factor:
        record(ERROR, "CONTRACT_MAP",
               f"{len(bad_factor)} fuel(s) have a blank or zero ConversionFactor -- those rows report nothing",
               bad_factor)


def record_unit_miss(property_name, db_unit, target_unit):
    record(WARN, "UNIT_CONVERSION",
           f"No conversion rule for '{db_unit}' -> '{target_unit}' (property '{property_name}'); "
           f"values were left unconverted")


def record_nan_scale(property_name, db_unit, target_unit):
    record(ERROR, "UNIT_CONVERSION",
           f"Conversion rule '{db_unit}' -> '{target_unit}' (property '{property_name}') resolved to NaN; "
           f"every value in that block becomes blank")


def record_period_fallback(property_name, class_name, preferred, used):
    record(WARN, "PERIOD_TYPE",
           f"Property '{property_name}' (class '{class_name}') is not reported at {preferred.title()} "
           f"resolution; its values were built from {used.title()} data instead")


def record_mixed_units(property_name, class_name, units):
    record(WARN, "UNIT_CONVERSION",
           f"Property '{property_name}' (class '{class_name}') is reported in more than one unit "
           f"({', '.join(units)}); '{units[0]}' was used to pick the conversion rule")


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
