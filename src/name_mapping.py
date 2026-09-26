"""
name_mapping.py
Every workbook sheet whose name starts with "maptable" is a name-mapping table:
column 1 is the text printed in the report, column 2 the text it replaces. Other
columns are reference only.

The mapping is applied in two places:
  - to object names while the data is built (NameMap.name / NameMap.arrange), so
    several PLEXOS objects mapped onto one name are summed, and names inside
    generated labels ("Total Effluents (lb) -- <name>") are mapped too;
  - to every text cell of the finished report (NameMap.cell), so any printed
    string -- a section title, a column header, a generated row label -- can be
    renamed from the workbook without code.
"""
from collections import defaultdict, namedtuple

import pandas as pd

MAPTABLE_PREFIX = "maptable"
# Pre-maptable sheet names; a workbook still using them would silently lose its mapping
LEGACY_SHEETS = ("Generator_name_map", "Contract_name_map")

# row is the sheet row number as Excel shows it, for pointing the user at the cell
Entry = namedtuple("Entry", "sheet row target source")


def _text(value):
    return "" if pd.isna(value) else str(value)


class NameMap:
    def __init__(self, entries, legacy_sheets=()):
        self.entries = list(entries)
        self.legacy_sheets = list(legacy_sheets)
        self.sheets = list(dict.fromkeys(e.sheet for e in self.entries))

        # Source -> target. Sheets are read in workbook order and rows top to bottom,
        # so when a source is listed twice the last listing wins.
        self.lookup = {}
        for e in self.entries:
            if e.source:
                self.lookup[e.source] = e.target

        # Each sheet's targets in sheet order: the row order of any section using it
        self.targets = {s: list(dict.fromkeys(e.target for e in self.entries if e.sheet == s)) for s in self.sheets}
        self._position = {s: {t: i for i, t in enumerate(ts)} for s, ts in self.targets.items()}

        # Targets with nothing mapped onto them. They are not printed (a zero row would land in
        # every section sharing the sheet's labels); the exceptions report lists them.
        active = set(self.lookup.values())
        self.empty = {s: [t for t in ts if t not in active] for s, ts in self.targets.items()}

        # Sources that actually renamed something during the run, for the unused-entry check
        self.used_sources = set()

    def name(self, value):
        """Mapped name for one object name or report string; anything unmapped passes through."""
        if not isinstance(value, str):
            return value
        key = value.strip()
        if key in self.lookup:
            self.used_sources.add(key)
            return self.lookup[key]
        return value

    # The report pass uses the same exact-match rule as object names
    cell = name

    def ordered(self, names):
        """
        `names` mapped, de-duplicated and put in maptable order. Names in no maptable
        keep their order, after the mapped ones.
        """
        mapped = list(dict.fromkeys(self.name(n) for n in names))
        present = set(mapped)
        used = [s for s in self.sheets if present & set(self.targets[s])]

        def sort_key(item):
            position, label = item
            for rank, sheet in enumerate(used):
                if label in self._position[sheet]:
                    return (rank, self._position[sheet][label])
            return (len(used), position)

        return [label for _, label in sorted(enumerate(mapped), key=sort_key)]

    def arrange(self, df):
        """
        Apply the mapping to a DataFrame indexed by name: rename the index, sum rows
        that now share a name and order rows by maptable.
        """
        if df.empty:
            return df
        index_name = df.index.name
        out = df.copy()
        out.index = [self.name(i) for i in out.index]
        out = out.groupby(level=0, sort=False).sum()
        out = out.reindex(self.ordered(out.index))
        out.index.name = index_name
        return out

    def duplicates(self):
        """Sources listed more than once: {source: [Entry, ...]} in listing order (the last one is used)."""
        by_source = defaultdict(list)
        for e in self.entries:
            if e.source:
                by_source[e.source].append(e)
        return {s: es for s, es in by_source.items() if len(es) > 1}


def load_maptables(xl):
    """Read every maptable sheet of an open pd.ExcelFile, in workbook order."""
    entries = []
    for sheet in xl.sheet_names:
        if not sheet.strip().lower().startswith(MAPTABLE_PREFIX):
            continue
        df = pd.read_excel(xl, sheet, header=0, dtype=object)
        if df.shape[1] < 2:
            continue
        for i, (target, source) in enumerate(zip(df.iloc[:, 0], df.iloc[:, 1])):
            target = _text(target)
            if not target.strip():
                continue
            # Row 1 is the header, so DataFrame row 0 is sheet row 2. The target keeps its
            # padding (RTSim labels are fixed-width); the source is matched trimmed.
            entries.append(Entry(sheet, i + 2, target, _text(source).strip()))
    legacy = [s for s in xl.sheet_names if s in LEGACY_SHEETS]
    return NameMap(entries, legacy)
